`default_nettype none

module rs_chien_horner_pipeline #(
    parameter int unsigned SYMBOL_WIDTH            = 10,
    parameter int unsigned N_COEFFICIENTS          = 64,
    parameter int unsigned PIPELINE_STAGES         = 1,
    parameter logic [SYMBOL_WIDTH:0]
        PRIMITIVE_POLYNOMIAL = 11'h409
) (
    input  logic                                       clk,
    input  logic                                       rst_n,

    input  logic [N_COEFFICIENTS*SYMBOL_WIDTH-1:0]     coefficients_i,
    input  logic                                       load_coefficients_i,

    input  logic [SYMBOL_WIDTH-1:0]                    x_i,
    input  logic                                       valid_i,

    output logic [SYMBOL_WIDTH-1:0]                    value_o,
    output logic                                       root_o,
    output logic                                       valid_o
);

    logic [SYMBOL_WIDTH-1:0] coefficient_reg [0:N_COEFFICIENTS-1];
    logic                    coefficients_loaded;

    logic [SYMBOL_WIDTH-1:0] pipeline_accumulator [0:PIPELINE_STAGES];
    logic [SYMBOL_WIDTH-1:0] pipeline_x           [0:PIPELINE_STAGES];
    logic                    pipeline_valid       [0:PIPELINE_STAGES];

    logic [SYMBOL_WIDTH-1:0] value_out;
    logic                    root_out;
    logic                    valid_out;

    function automatic logic [SYMBOL_WIDTH-1:0] gf_multiply(
        input logic [SYMBOL_WIDTH-1:0] multiplicand_i,
        input logic [SYMBOL_WIDTH-1:0] multiplier_i
    );
        logic [SYMBOL_WIDTH-1:0] product;
        logic [SYMBOL_WIDTH-1:0] shifted_multiplicand;

        product                = '0;
        shifted_multiplicand   = multiplicand_i;

        for (int unsigned bit_index = 0;
             bit_index < SYMBOL_WIDTH;
             bit_index++) begin
            if (multiplier_i[bit_index]) begin
                product ^= shifted_multiplicand;
            end

            if (shifted_multiplicand[SYMBOL_WIDTH-1]) begin
                shifted_multiplicand =
                    {shifted_multiplicand[SYMBOL_WIDTH-2:0], 1'b0}
                    ^ PRIMITIVE_POLYNOMIAL[SYMBOL_WIDTH-1:0];
            end else begin
                shifted_multiplicand =
                    {shifted_multiplicand[SYMBOL_WIDTH-2:0], 1'b0};
            end
        end

        gf_multiply = product;
    endfunction

    if (SYMBOL_WIDTH < 2) begin : gen_invalid_symbol_width
        initial $fatal(1, "SYMBOL_WIDTH must be at least 2");
    end

    if ((N_COEFFICIENTS == 0) || (PIPELINE_STAGES == 0)) begin : gen_invalid_size
        initial $fatal(
            1,
            "N_COEFFICIENTS and PIPELINE_STAGES must be greater than zero"
        );
    end

    if (!PRIMITIVE_POLYNOMIAL[SYMBOL_WIDTH]
        || !PRIMITIVE_POLYNOMIAL[0]) begin : gen_invalid_polynomial
        initial $fatal(
            1,
            "PRIMITIVE_POLYNOMIAL must include the highest and constant terms"
        );
    end

    always_ff @(posedge clk or negedge rst_n) begin : coefficient_reg_proc
        if (!rst_n) begin
            coefficients_loaded <= 1'b0;
        end else if (load_coefficients_i) begin
            for (int unsigned coefficient_index = 0;
                 coefficient_index < N_COEFFICIENTS;
                 coefficient_index++) begin
                coefficient_reg[coefficient_index] <=
                    coefficients_i[coefficient_index*SYMBOL_WIDTH +: SYMBOL_WIDTH];
            end
            coefficients_loaded <= 1'b1;
        end
    end

    always_ff @(posedge clk or negedge rst_n) begin : input_reg_proc
        if (!rst_n) begin
            pipeline_valid[0] <= 1'b0;
        end else begin
            pipeline_accumulator[0] <= '0;
            pipeline_x[0]           <= x_i;
            pipeline_valid[0]       <= valid_i && coefficients_loaded;
        end
    end

    for (genvar stage_index = 0;
         stage_index < PIPELINE_STAGES;
         stage_index++) begin : gen_pipeline_stage

        localparam int unsigned FIRST_COEFFICIENT =
            (stage_index * N_COEFFICIENTS) / PIPELINE_STAGES;
        localparam int unsigned LAST_COEFFICIENT =
            ((stage_index + 1) * N_COEFFICIENTS) / PIPELINE_STAGES;
        localparam int unsigned STAGE_COEFFICIENTS =
            LAST_COEFFICIENT - FIRST_COEFFICIENT;

        logic [SYMBOL_WIDTH-1:0] horner_value [0:STAGE_COEFFICIENTS];

        assign horner_value[0] = pipeline_accumulator[stage_index];

        for (genvar term_index = 0;
             term_index < STAGE_COEFFICIENTS;
             term_index++) begin : gen_horner_term

            localparam int unsigned COEFFICIENT_INDEX =
                N_COEFFICIENTS - 1
                - FIRST_COEFFICIENT
                - term_index;

            assign horner_value[term_index+1] =
                gf_multiply(horner_value[term_index], pipeline_x[stage_index])
                ^ coefficient_reg[COEFFICIENT_INDEX];
        end

        always_ff @(posedge clk or negedge rst_n) begin : pipeline_reg_proc
            if (!rst_n) begin
                pipeline_valid[stage_index+1] <= 1'b0;
            end else begin
                pipeline_accumulator[stage_index+1] <=
                    horner_value[STAGE_COEFFICIENTS];
                pipeline_x[stage_index+1] <= pipeline_x[stage_index];
                pipeline_valid[stage_index+1] <= pipeline_valid[stage_index];
            end
        end

    end

    assign value_out = pipeline_accumulator[PIPELINE_STAGES];
    assign valid_out = pipeline_valid[PIPELINE_STAGES];
    assign root_out  = valid_out && (value_out == '0);

    assign value_o = value_out;
    assign root_o  = root_out;
    assign valid_o = valid_out;

endmodule

`default_nettype wire
