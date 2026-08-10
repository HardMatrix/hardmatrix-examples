`default_nettype none

module arx_pipeline #(
    parameter int unsigned WORD_WIDTH      = 32,
    parameter int unsigned N_ROUNDS        = 64,
    parameter int unsigned PIPELINE_STAGES = 1,
    parameter int unsigned ROTATE_A        = 5,
    parameter int unsigned ROTATE_B        = 11
) (
    input  logic                  clk,
    input  logic                  rst_n,
    input  logic [WORD_WIDTH-1:0] a_i,
    input  logic [WORD_WIDTH-1:0] b_i,
    input  logic                  valid_i,
    output logic [WORD_WIDTH-1:0] a_o,
    output logic [WORD_WIDTH-1:0] b_o,
    output logic                  valid_o
);

    localparam int unsigned STATE_WIDTH = 2 * WORD_WIDTH;

    logic [STATE_WIDTH-1:0] pipeline_state [0:PIPELINE_STAGES];
    logic                   pipeline_valid [0:PIPELINE_STAGES];

    logic [WORD_WIDTH-1:0] a_out;
    logic [WORD_WIDTH-1:0] b_out;
    logic                  valid_out;

    function automatic logic [WORD_WIDTH-1:0] rotate_left(
        input logic [WORD_WIDTH-1:0] value,
        input int unsigned           amount
    );
        rotate_left = (value << amount) | (value >> (WORD_WIDTH - amount));
    endfunction

    function automatic logic [STATE_WIDTH-1:0] arx_round(
        input logic [STATE_WIDTH-1:0] state
    );
        logic [WORD_WIDTH-1:0] a;
        logic [WORD_WIDTH-1:0] b;
        logic [WORD_WIDTH-1:0] next_a;
        logic [WORD_WIDTH-1:0] next_b;

        a = state[STATE_WIDTH-1-:WORD_WIDTH];
        b = state[WORD_WIDTH-1:0];

        next_a = rotate_left(a, ROTATE_A) + b;
        next_b = rotate_left(b, ROTATE_B) ^ next_a;

        arx_round = {next_a, next_b};
    endfunction

    if (WORD_WIDTH < 2) begin : gen_invalid_word_width
        initial $fatal(1, "WORD_WIDTH must be at least 2");
    end

    if ((ROTATE_A == 0) || (ROTATE_A >= WORD_WIDTH)) begin : gen_invalid_rotate_a
        initial $fatal(1, "ROTATE_A must be in the range 1..WORD_WIDTH-1");
    end

    if ((ROTATE_B == 0) || (ROTATE_B >= WORD_WIDTH)) begin : gen_invalid_rotate_b
        initial $fatal(1, "ROTATE_B must be in the range 1..WORD_WIDTH-1");
    end

    if ((N_ROUNDS == 0) || (PIPELINE_STAGES == 0)) begin : gen_invalid_stage_count
        initial $fatal(1, "N_ROUNDS and PIPELINE_STAGES must be greater than zero");
    end

    always_ff @(posedge clk or negedge rst_n) begin : input_reg_proc
        if (!rst_n) begin
            pipeline_valid[0] <= 1'b0;
        end else begin
            pipeline_state[0] <= {a_i, b_i};
            pipeline_valid[0] <= valid_i;
        end
    end

    for (genvar stage_index = 0;
         stage_index < PIPELINE_STAGES;
         stage_index++) begin : gen_pipeline_stage

        localparam int unsigned FIRST_ROUND =
            (stage_index * N_ROUNDS) / PIPELINE_STAGES;
        localparam int unsigned LAST_ROUND =
            ((stage_index + 1) * N_ROUNDS) / PIPELINE_STAGES;
        localparam int unsigned STAGE_ROUNDS = LAST_ROUND - FIRST_ROUND;

        logic [STATE_WIDTH-1:0] round_state [0:STAGE_ROUNDS];

        assign round_state[0] = pipeline_state[stage_index];

        for (genvar round_index = 0;
             round_index < STAGE_ROUNDS;
             round_index++) begin : gen_round
            assign round_state[round_index+1] = arx_round(round_state[round_index]);
        end

        always_ff @(posedge clk or negedge rst_n) begin : pipeline_reg_proc
            if (!rst_n) begin
                pipeline_valid[stage_index+1] <= 1'b0;
            end else begin
                pipeline_state[stage_index+1] <= round_state[STAGE_ROUNDS];
                pipeline_valid[stage_index+1] <= pipeline_valid[stage_index];
            end
        end

    end

    assign a_out     = pipeline_state[PIPELINE_STAGES][STATE_WIDTH-1-:WORD_WIDTH];
    assign b_out     = pipeline_state[PIPELINE_STAGES][WORD_WIDTH-1:0];
    assign valid_out = pipeline_valid[PIPELINE_STAGES];

    assign a_o     = a_out;
    assign b_o     = b_out;
    assign valid_o = valid_out;

endmodule

`default_nettype wire
