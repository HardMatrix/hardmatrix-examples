module axis_eth_fcs_insert
#()
(
    input logic clk,
    input logic rst_n,

    axis_if s_axis,
    axis_if m_axis
);

    localparam logic [32-1:0] CRC_INIT = 32'hFFFF_FFFF;
    localparam int unsigned N_FCS_BYTES = 4;

    typedef enum logic [0:0] {
        ST_BYPASS_DATA,
        ST_SEND_FCS
    } axis_eth_fcs_insert_state_t;

    axis_eth_fcs_insert_state_t current_state, next_state;

    logic [32-1:0] crc;
    logic [32-1:0] next_crc;
    logic [32-1:0] fcs;
    logic [$clog2(N_FCS_BYTES)-1:0] fcs_count;
    logic last_fcs_byte;
    logic crc_valid;
    logic crc_ready;

    eth_crc32_byte
    u_eth_crc32_byte (
        .crc_i       (crc),
        .data_i      (s_axis.tdata),
        .valid_i     (crc_valid),
        .crc_o       (next_crc),
        .crc_ready_o (crc_ready)
    );

    assign crc_valid = s_axis.transaction;

    always_ff @(posedge clk) begin : axis_eth_fcs_insert_state_upd_proc
        if (!rst_n) begin
            current_state <= ST_BYPASS_DATA;
        end else begin
            current_state <= next_state;
        end
    end : axis_eth_fcs_insert_state_upd_proc

    always_comb begin : axis_eth_fcs_insert_state_transition_proc
        case (current_state)
            ST_BYPASS_DATA: begin
                if (s_axis.transaction && s_axis.tlast) begin
                    next_state = ST_SEND_FCS;
                end else begin
                    next_state = ST_BYPASS_DATA;
                end
            end
            ST_SEND_FCS: begin
                if (m_axis.transaction && last_fcs_byte) begin
                    next_state = ST_BYPASS_DATA;
                end else begin
                    next_state = ST_SEND_FCS;
                end
            end
            default: begin
                next_state = current_state;
            end
        endcase
    end : axis_eth_fcs_insert_state_transition_proc

    always_ff @(posedge clk) begin : crc_upd_proc
        if (!rst_n) begin
            crc <= CRC_INIT;
            fcs <= '0;
        end else if (crc_ready) begin
            if (s_axis.tlast) begin
                crc <= CRC_INIT;
                fcs <= ~next_crc;
            end else begin
                crc <= next_crc;
            end
        end
    end : crc_upd_proc

    always_ff @(posedge clk) begin : fcs_count_upd_proc
        if (!rst_n) begin
            fcs_count <= '0;
        end else if (current_state == ST_BYPASS_DATA) begin
            fcs_count <= '0;
        end else if (m_axis.transaction) begin
            if (last_fcs_byte) begin
                fcs_count <= '0;
            end else begin
                fcs_count <= fcs_count + 1'b1;
            end
        end
    end : fcs_count_upd_proc

    assign last_fcs_byte = fcs_count == ($size(fcs_count))'(N_FCS_BYTES-1);

    always_comb begin : axis_output_proc
        s_axis.tready = '0;
        m_axis.tvalid = '0;
        m_axis.tdata  = '0;
        m_axis.tlast  = '0;

        case (current_state)
            ST_BYPASS_DATA: begin
                s_axis.tready = m_axis.tready;
                m_axis.tvalid = s_axis.tvalid;
                m_axis.tdata  = s_axis.tdata;
                m_axis.tlast  = 1'b0;
            end
            ST_SEND_FCS: begin
                s_axis.tready = 1'b0;
                m_axis.tvalid = 1'b1;
                m_axis.tdata  = fcs[fcs_count*8+:8];
                m_axis.tlast  = last_fcs_byte;
            end
            default: begin
                s_axis.tready = '0;
                m_axis.tvalid = '0;
                m_axis.tdata  = '0;
                m_axis.tlast  = '0;
            end
        endcase
    end : axis_output_proc

endmodule
