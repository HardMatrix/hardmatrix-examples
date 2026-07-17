`default_nettype wire
interface axis_if
#(
    parameter integer unsigned  NB_TDATA   = 32
)
(
    input logic clk,
    input logic rst_n
);

    initial begin
        if (NB_TDATA == 0) begin : g_check_n_bits_tdata_nonzero
            $fatal(1, "The number of bits in the tdata vector cannot be zero.");
        end
    end

    // Protocol signals
    logic                                       tvalid          ; // Master -> Slave
    logic                                       tready          ; // Master <- Slave
    logic   [NB_TDATA-1:0]                      tdata           ; // Master -> Slave
    logic                                       tlast           ; // Master -> Slave

    // Asserted if handshake will occur
    logic                                       transaction     ;

    assign transaction = tvalid && tready;

    modport master
    (
        output  tvalid          ,
        input   tready          ,
        output  tdata           ,
        output  tlast
    );

    modport slave
    (
        input  tvalid           ,
        output tready           ,
        input  tdata            ,
        input  tlast
    );

    // ASSERTIONS
    `ifdef SYNTHESIS
    `else
        property VALID_RST;
            @(posedge clk) rst_n == 1'b0 |=> tvalid == 1'b0;
        endproperty
        assert property (VALID_RST) else
            $error("VALID_RST: tvalid must be LOW while reset is asserted");

        property AXI4STREAM_ERRM_TVALID_RESET;
            //Vivado < 2021.2 does not support $fell
            @(posedge clk) (rst_n & !$past(rst_n)) |-> tvalid == 1'b0;
        endproperty
        assert property (AXI4STREAM_ERRM_TVALID_RESET) else
            $error(string'({"AXI4STREAM_ERRM_TVALID_RESET: tvalid was not low for ",
                    "the first cycle after reset went low"}));

        property AXI4STREAM_ERRM_TVALID_STABLE;
            @(posedge clk) disable iff (!rst_n) (tvalid && !tready) |=> tvalid;
        endproperty
        assert property (AXI4STREAM_ERRM_TVALID_STABLE) else
            $error(string'({"AXI4STREAM_ERRM_TVALID_STABLE: tvalid was deasserted ",
                    "even though the data was not consumed"}));

        property AXI4STREAM_ERRM_TDATA_STABLE;
            @(posedge clk) disable iff (!rst_n) (tvalid && !tready) |=> $stable(tdata);
        endproperty
        assert property (AXI4STREAM_ERRM_TDATA_STABLE) else
            $error(string'({"AXI4STREAM_ERRM_TDATA_STABLE: tdata was not stable when ",
                    "tvalid was asserted and tready was low"}));

        property AXI4STREAM_ERRM_TLAST_STABLE;
            @(posedge clk) disable iff (!rst_n) (tvalid && !tready) |=> $stable(tlast);
        endproperty
        assert property (AXI4STREAM_ERRM_TLAST_STABLE) else
            $error(string'({"AXI4STREAM_ERRM_TLAST_STABLE: tlast was not ",
                    "stable when tvalid was asserted and tready was low"}));

        property AXI4STREAM_ERRM_TDATA_X;
            @(posedge clk) (rst_n && tvalid) |-> !$isunknown(tdata);
        endproperty
        assert property (AXI4STREAM_ERRM_TDATA_X) else
            $error(string'({"AXI4STREAM_ERRM_TDATA_X: part (or all) of tdata ",
                    "was 1'bX while tvalid was high"}));

        property AXI4STREAM_ERRM_TLAST_X;
            @(posedge clk) (rst_n && tvalid) |-> !$isunknown(tlast);
        endproperty
        assert property (AXI4STREAM_ERRM_TLAST_X) else
            $error("AXI4STREAM_ERRM_TLAST_X: tlast was 1'bX while tvalid was high");
    `endif //SYNTHESIS

endinterface
