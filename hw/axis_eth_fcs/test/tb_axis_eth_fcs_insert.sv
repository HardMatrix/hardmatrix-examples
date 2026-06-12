module tb_axis_eth_fcs_insert
#()
(
    input  logic       clk,
    input  logic       rst_n,

    input  logic [7:0] s_axis_tdata,
    input  logic       s_axis_tvalid,
    input  logic       s_axis_tlast,
    output logic       s_axis_tready,

    output logic [7:0] m_axis_tdata,
    output logic       m_axis_tvalid,
    output logic       m_axis_tlast,
    input  logic       m_axis_tready
);

    axis_if#(.NB_TDATA(8)) s_axis (
        .clk  (clk),
        .rst_n(rst_n)
    );

    assign s_axis.tdata  = s_axis_tdata;
    assign s_axis.tvalid = s_axis_tvalid;
    assign s_axis.tlast  = s_axis_tlast;
    assign s_axis_tready = s_axis.tready;

    axis_if#(.NB_TDATA(8)) m_axis (
        .clk  (clk),
        .rst_n(rst_n)
    );

    assign m_axis_tdata  = m_axis.tdata;
    assign m_axis_tvalid = m_axis.tvalid;
    assign m_axis_tlast  = m_axis.tlast;
    assign m_axis.tready = m_axis_tready;

    axis_eth_fcs_insert
    u_axis_eth_fcs_insert (
        .clk   (clk),
        .rst_n (rst_n),
        .s_axis(s_axis),
        .m_axis(m_axis)
    );

endmodule
