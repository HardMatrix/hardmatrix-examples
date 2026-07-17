module vector_adder_machine_regmap_wrapper(
    input wire clk,
    input wire rst,
    output logic s_axil_awready,
    input logic s_axil_awvalid,
    input logic [8:0] s_axil_awaddr,
    input logic [2:0] s_axil_awprot,
    output logic s_axil_wready,
    input logic s_axil_wvalid,
    input logic [31:0] s_axil_wdata,
    input logic [3:0] s_axil_wstrb,
    input logic s_axil_bready,
    output logic s_axil_bvalid,
    output logic [1:0] s_axil_bresp,
    output logic s_axil_arready,
    input logic s_axil_arvalid,
    input logic [8:0] s_axil_araddr,
    input logic [2:0] s_axil_arprot,
    input logic s_axil_rready,
    output logic s_axil_rvalid,
    output logic [31:0] s_axil_rdata,
    output logic [1:0] s_axil_rresp,
    input logic hwif_in_status_done_next,
    input logic hwif_in_status_done_we,
    input logic hwif_in_status_error_next,
    input logic hwif_in_status_error_we,
    input logic hwif_in_status_clear_next,
    input logic hwif_in_status_clear_we,
    input logic [31:0] hwif_in_vectors_0_elems_0_data_next,
    input logic hwif_in_vectors_0_elems_0_data_we,
    input logic [31:0] hwif_in_vectors_0_elems_1_data_next,
    input logic hwif_in_vectors_0_elems_1_data_we,
    input logic [31:0] hwif_in_vectors_0_elems_2_data_next,
    input logic hwif_in_vectors_0_elems_2_data_we,
    input logic [31:0] hwif_in_vectors_0_elems_3_data_next,
    input logic hwif_in_vectors_0_elems_3_data_we,
    input logic [31:0] hwif_in_vectors_1_elems_0_data_next,
    input logic hwif_in_vectors_1_elems_0_data_we,
    input logic [31:0] hwif_in_vectors_1_elems_1_data_next,
    input logic hwif_in_vectors_1_elems_1_data_we,
    input logic [31:0] hwif_in_vectors_1_elems_2_data_next,
    input logic hwif_in_vectors_1_elems_2_data_we,
    input logic [31:0] hwif_in_vectors_1_elems_3_data_next,
    input logic hwif_in_vectors_1_elems_3_data_we,
    input logic [31:0] hwif_in_vectors_2_elems_0_data_next,
    input logic hwif_in_vectors_2_elems_0_data_we,
    input logic [31:0] hwif_in_vectors_2_elems_1_data_next,
    input logic hwif_in_vectors_2_elems_1_data_we,
    input logic [31:0] hwif_in_vectors_2_elems_2_data_next,
    input logic hwif_in_vectors_2_elems_2_data_we,
    input logic [31:0] hwif_in_vectors_2_elems_3_data_next,
    input logic hwif_in_vectors_2_elems_3_data_we,
    input logic [31:0] hwif_in_vectors_3_elems_0_data_next,
    input logic hwif_in_vectors_3_elems_0_data_we,
    input logic [31:0] hwif_in_vectors_3_elems_1_data_next,
    input logic hwif_in_vectors_3_elems_1_data_we,
    input logic [31:0] hwif_in_vectors_3_elems_2_data_next,
    input logic hwif_in_vectors_3_elems_2_data_we,
    input logic [31:0] hwif_in_vectors_3_elems_3_data_next,
    input logic hwif_in_vectors_3_elems_3_data_we,
    input logic [31:0] hwif_in_vectors_4_elems_0_data_next,
    input logic hwif_in_vectors_4_elems_0_data_we,
    input logic [31:0] hwif_in_vectors_4_elems_1_data_next,
    input logic hwif_in_vectors_4_elems_1_data_we,
    input logic [31:0] hwif_in_vectors_4_elems_2_data_next,
    input logic hwif_in_vectors_4_elems_2_data_we,
    input logic [31:0] hwif_in_vectors_4_elems_3_data_next,
    input logic hwif_in_vectors_4_elems_3_data_we,
    input logic [31:0] hwif_in_vectors_5_elems_0_data_next,
    input logic hwif_in_vectors_5_elems_0_data_we,
    input logic [31:0] hwif_in_vectors_5_elems_1_data_next,
    input logic hwif_in_vectors_5_elems_1_data_we,
    input logic [31:0] hwif_in_vectors_5_elems_2_data_next,
    input logic hwif_in_vectors_5_elems_2_data_we,
    input logic [31:0] hwif_in_vectors_5_elems_3_data_next,
    input logic hwif_in_vectors_5_elems_3_data_we,
    input logic [31:0] hwif_in_vectors_6_elems_0_data_next,
    input logic hwif_in_vectors_6_elems_0_data_we,
    input logic [31:0] hwif_in_vectors_6_elems_1_data_next,
    input logic hwif_in_vectors_6_elems_1_data_we,
    input logic [31:0] hwif_in_vectors_6_elems_2_data_next,
    input logic hwif_in_vectors_6_elems_2_data_we,
    input logic [31:0] hwif_in_vectors_6_elems_3_data_next,
    input logic hwif_in_vectors_6_elems_3_data_we,
    input logic [31:0] hwif_in_vectors_7_elems_0_data_next,
    input logic hwif_in_vectors_7_elems_0_data_we,
    input logic [31:0] hwif_in_vectors_7_elems_1_data_next,
    input logic hwif_in_vectors_7_elems_1_data_we,
    input logic [31:0] hwif_in_vectors_7_elems_2_data_next,
    input logic hwif_in_vectors_7_elems_2_data_we,
    input logic [31:0] hwif_in_vectors_7_elems_3_data_next,
    input logic hwif_in_vectors_7_elems_3_data_we,
    output logic hwif_out_status_done_value,
    output logic hwif_out_status_error_value,
    output logic hwif_out_status_clear_value,
    output logic [7:0] hwif_out_instruction_op_value,
    output logic hwif_out_instruction_op_swmod,
    output logic [2:0] hwif_out_instruction_rega_value,
    output logic [2:0] hwif_out_instruction_regb_value,
    output logic [2:0] hwif_out_instruction_dest_value,
    output logic [31:0] hwif_out_vectors_0_elems_0_data_value,
    output logic [31:0] hwif_out_vectors_0_elems_1_data_value,
    output logic [31:0] hwif_out_vectors_0_elems_2_data_value,
    output logic [31:0] hwif_out_vectors_0_elems_3_data_value,
    output logic [31:0] hwif_out_vectors_1_elems_0_data_value,
    output logic [31:0] hwif_out_vectors_1_elems_1_data_value,
    output logic [31:0] hwif_out_vectors_1_elems_2_data_value,
    output logic [31:0] hwif_out_vectors_1_elems_3_data_value,
    output logic [31:0] hwif_out_vectors_2_elems_0_data_value,
    output logic [31:0] hwif_out_vectors_2_elems_1_data_value,
    output logic [31:0] hwif_out_vectors_2_elems_2_data_value,
    output logic [31:0] hwif_out_vectors_2_elems_3_data_value,
    output logic [31:0] hwif_out_vectors_3_elems_0_data_value,
    output logic [31:0] hwif_out_vectors_3_elems_1_data_value,
    output logic [31:0] hwif_out_vectors_3_elems_2_data_value,
    output logic [31:0] hwif_out_vectors_3_elems_3_data_value,
    output logic [31:0] hwif_out_vectors_4_elems_0_data_value,
    output logic [31:0] hwif_out_vectors_4_elems_1_data_value,
    output logic [31:0] hwif_out_vectors_4_elems_2_data_value,
    output logic [31:0] hwif_out_vectors_4_elems_3_data_value,
    output logic [31:0] hwif_out_vectors_5_elems_0_data_value,
    output logic [31:0] hwif_out_vectors_5_elems_1_data_value,
    output logic [31:0] hwif_out_vectors_5_elems_2_data_value,
    output logic [31:0] hwif_out_vectors_5_elems_3_data_value,
    output logic [31:0] hwif_out_vectors_6_elems_0_data_value,
    output logic [31:0] hwif_out_vectors_6_elems_1_data_value,
    output logic [31:0] hwif_out_vectors_6_elems_2_data_value,
    output logic [31:0] hwif_out_vectors_6_elems_3_data_value,
    output logic [31:0] hwif_out_vectors_7_elems_0_data_value,
    output logic [31:0] hwif_out_vectors_7_elems_1_data_value,
    output logic [31:0] hwif_out_vectors_7_elems_2_data_value,
    output logic [31:0] hwif_out_vectors_7_elems_3_data_value
);
    import vector_adder_machine_regmap_pkg::*;
    vector_adder_machine_regmap_pkg::vector_adder_machine_regmap__in_t hwif_in;
    vector_adder_machine_regmap_pkg::vector_adder_machine_regmap__out_t hwif_out;
    axi4lite_intf s_axil(.*);

    assign hwif_in.status.done.next = hwif_in_status_done_next;
    assign hwif_in.status.done.we = hwif_in_status_done_we;
    assign hwif_in.status.error.next = hwif_in_status_error_next;
    assign hwif_in.status.error.we = hwif_in_status_error_we;
    assign hwif_in.status.clear.next = hwif_in_status_clear_next;
    assign hwif_in.status.clear.we = hwif_in_status_clear_we;
    assign hwif_in.vectors[0].elems[0].data.next = hwif_in_vectors_0_elems_0_data_next;
    assign hwif_in.vectors[0].elems[0].data.we = hwif_in_vectors_0_elems_0_data_we;
    assign hwif_in.vectors[0].elems[1].data.next = hwif_in_vectors_0_elems_1_data_next;
    assign hwif_in.vectors[0].elems[1].data.we = hwif_in_vectors_0_elems_1_data_we;
    assign hwif_in.vectors[0].elems[2].data.next = hwif_in_vectors_0_elems_2_data_next;
    assign hwif_in.vectors[0].elems[2].data.we = hwif_in_vectors_0_elems_2_data_we;
    assign hwif_in.vectors[0].elems[3].data.next = hwif_in_vectors_0_elems_3_data_next;
    assign hwif_in.vectors[0].elems[3].data.we = hwif_in_vectors_0_elems_3_data_we;
    assign hwif_in.vectors[1].elems[0].data.next = hwif_in_vectors_1_elems_0_data_next;
    assign hwif_in.vectors[1].elems[0].data.we = hwif_in_vectors_1_elems_0_data_we;
    assign hwif_in.vectors[1].elems[1].data.next = hwif_in_vectors_1_elems_1_data_next;
    assign hwif_in.vectors[1].elems[1].data.we = hwif_in_vectors_1_elems_1_data_we;
    assign hwif_in.vectors[1].elems[2].data.next = hwif_in_vectors_1_elems_2_data_next;
    assign hwif_in.vectors[1].elems[2].data.we = hwif_in_vectors_1_elems_2_data_we;
    assign hwif_in.vectors[1].elems[3].data.next = hwif_in_vectors_1_elems_3_data_next;
    assign hwif_in.vectors[1].elems[3].data.we = hwif_in_vectors_1_elems_3_data_we;
    assign hwif_in.vectors[2].elems[0].data.next = hwif_in_vectors_2_elems_0_data_next;
    assign hwif_in.vectors[2].elems[0].data.we = hwif_in_vectors_2_elems_0_data_we;
    assign hwif_in.vectors[2].elems[1].data.next = hwif_in_vectors_2_elems_1_data_next;
    assign hwif_in.vectors[2].elems[1].data.we = hwif_in_vectors_2_elems_1_data_we;
    assign hwif_in.vectors[2].elems[2].data.next = hwif_in_vectors_2_elems_2_data_next;
    assign hwif_in.vectors[2].elems[2].data.we = hwif_in_vectors_2_elems_2_data_we;
    assign hwif_in.vectors[2].elems[3].data.next = hwif_in_vectors_2_elems_3_data_next;
    assign hwif_in.vectors[2].elems[3].data.we = hwif_in_vectors_2_elems_3_data_we;
    assign hwif_in.vectors[3].elems[0].data.next = hwif_in_vectors_3_elems_0_data_next;
    assign hwif_in.vectors[3].elems[0].data.we = hwif_in_vectors_3_elems_0_data_we;
    assign hwif_in.vectors[3].elems[1].data.next = hwif_in_vectors_3_elems_1_data_next;
    assign hwif_in.vectors[3].elems[1].data.we = hwif_in_vectors_3_elems_1_data_we;
    assign hwif_in.vectors[3].elems[2].data.next = hwif_in_vectors_3_elems_2_data_next;
    assign hwif_in.vectors[3].elems[2].data.we = hwif_in_vectors_3_elems_2_data_we;
    assign hwif_in.vectors[3].elems[3].data.next = hwif_in_vectors_3_elems_3_data_next;
    assign hwif_in.vectors[3].elems[3].data.we = hwif_in_vectors_3_elems_3_data_we;
    assign hwif_in.vectors[4].elems[0].data.next = hwif_in_vectors_4_elems_0_data_next;
    assign hwif_in.vectors[4].elems[0].data.we = hwif_in_vectors_4_elems_0_data_we;
    assign hwif_in.vectors[4].elems[1].data.next = hwif_in_vectors_4_elems_1_data_next;
    assign hwif_in.vectors[4].elems[1].data.we = hwif_in_vectors_4_elems_1_data_we;
    assign hwif_in.vectors[4].elems[2].data.next = hwif_in_vectors_4_elems_2_data_next;
    assign hwif_in.vectors[4].elems[2].data.we = hwif_in_vectors_4_elems_2_data_we;
    assign hwif_in.vectors[4].elems[3].data.next = hwif_in_vectors_4_elems_3_data_next;
    assign hwif_in.vectors[4].elems[3].data.we = hwif_in_vectors_4_elems_3_data_we;
    assign hwif_in.vectors[5].elems[0].data.next = hwif_in_vectors_5_elems_0_data_next;
    assign hwif_in.vectors[5].elems[0].data.we = hwif_in_vectors_5_elems_0_data_we;
    assign hwif_in.vectors[5].elems[1].data.next = hwif_in_vectors_5_elems_1_data_next;
    assign hwif_in.vectors[5].elems[1].data.we = hwif_in_vectors_5_elems_1_data_we;
    assign hwif_in.vectors[5].elems[2].data.next = hwif_in_vectors_5_elems_2_data_next;
    assign hwif_in.vectors[5].elems[2].data.we = hwif_in_vectors_5_elems_2_data_we;
    assign hwif_in.vectors[5].elems[3].data.next = hwif_in_vectors_5_elems_3_data_next;
    assign hwif_in.vectors[5].elems[3].data.we = hwif_in_vectors_5_elems_3_data_we;
    assign hwif_in.vectors[6].elems[0].data.next = hwif_in_vectors_6_elems_0_data_next;
    assign hwif_in.vectors[6].elems[0].data.we = hwif_in_vectors_6_elems_0_data_we;
    assign hwif_in.vectors[6].elems[1].data.next = hwif_in_vectors_6_elems_1_data_next;
    assign hwif_in.vectors[6].elems[1].data.we = hwif_in_vectors_6_elems_1_data_we;
    assign hwif_in.vectors[6].elems[2].data.next = hwif_in_vectors_6_elems_2_data_next;
    assign hwif_in.vectors[6].elems[2].data.we = hwif_in_vectors_6_elems_2_data_we;
    assign hwif_in.vectors[6].elems[3].data.next = hwif_in_vectors_6_elems_3_data_next;
    assign hwif_in.vectors[6].elems[3].data.we = hwif_in_vectors_6_elems_3_data_we;
    assign hwif_in.vectors[7].elems[0].data.next = hwif_in_vectors_7_elems_0_data_next;
    assign hwif_in.vectors[7].elems[0].data.we = hwif_in_vectors_7_elems_0_data_we;
    assign hwif_in.vectors[7].elems[1].data.next = hwif_in_vectors_7_elems_1_data_next;
    assign hwif_in.vectors[7].elems[1].data.we = hwif_in_vectors_7_elems_1_data_we;
    assign hwif_in.vectors[7].elems[2].data.next = hwif_in_vectors_7_elems_2_data_next;
    assign hwif_in.vectors[7].elems[2].data.we = hwif_in_vectors_7_elems_2_data_we;
    assign hwif_in.vectors[7].elems[3].data.next = hwif_in_vectors_7_elems_3_data_next;
    assign hwif_in.vectors[7].elems[3].data.we = hwif_in_vectors_7_elems_3_data_we;

    vector_adder_machine_regmap u_regblock (.clk(clk), .rst(rst), .hwif_in(hwif_in), .hwif_out(hwif_out), .s_axil(s_axil));

    assign s_axil.AWVALID = s_axil_awvalid;
    assign s_axil.AWADDR = s_axil_awaddr;
    assign s_axil.AWPROT = s_axil_awprot;
    assign s_axil.WVALID = s_axil_wvalid;
    assign s_axil.WDATA = s_axil_wdata;
    assign s_axil.WSTRB = s_axil_wstrb;
    assign s_axil.BREADY = s_axil_bready;
    assign s_axil.ARVALID = s_axil_arvalid;
    assign s_axil.ARADDR = s_axil_araddr;
    assign s_axil.ARPROT = s_axil_arprot;
    assign s_axil.RREADY = s_axil_rready;
    assign s_axil_awready = s_axil.AWREADY;
    assign s_axil_wready = s_axil.WREADY;
    assign s_axil_bvalid = s_axil.BVALID;
    assign s_axil_bresp = s_axil.BRESP;
    assign s_axil_arready = s_axil.ARREADY;
    assign s_axil_rvalid = s_axil.RVALID;
    assign s_axil_rdata = s_axil.RDATA;
    assign s_axil_rresp = s_axil.RRESP;

    // done/error are hw=w fields — not in hwif_out struct, tie off (unused by Chisel)
    assign hwif_out_status_done_value = 1'b0;
    assign hwif_out_status_error_value = 1'b0;
    assign hwif_out_status_clear_value = hwif_out.status.clear.value;
    assign hwif_out_instruction_op_value = hwif_out.instruction.op.value;
    assign hwif_out_instruction_op_swmod = hwif_out.instruction.op.swmod;
    assign hwif_out_instruction_rega_value = hwif_out.instruction.rega.value;
    assign hwif_out_instruction_regb_value = hwif_out.instruction.regb.value;
    assign hwif_out_instruction_dest_value = hwif_out.instruction.dest.value;
    assign hwif_out_vectors_0_elems_0_data_value = hwif_out.vectors[0].elems[0].data.value;
    assign hwif_out_vectors_0_elems_1_data_value = hwif_out.vectors[0].elems[1].data.value;
    assign hwif_out_vectors_0_elems_2_data_value = hwif_out.vectors[0].elems[2].data.value;
    assign hwif_out_vectors_0_elems_3_data_value = hwif_out.vectors[0].elems[3].data.value;
    assign hwif_out_vectors_1_elems_0_data_value = hwif_out.vectors[1].elems[0].data.value;
    assign hwif_out_vectors_1_elems_1_data_value = hwif_out.vectors[1].elems[1].data.value;
    assign hwif_out_vectors_1_elems_2_data_value = hwif_out.vectors[1].elems[2].data.value;
    assign hwif_out_vectors_1_elems_3_data_value = hwif_out.vectors[1].elems[3].data.value;
    assign hwif_out_vectors_2_elems_0_data_value = hwif_out.vectors[2].elems[0].data.value;
    assign hwif_out_vectors_2_elems_1_data_value = hwif_out.vectors[2].elems[1].data.value;
    assign hwif_out_vectors_2_elems_2_data_value = hwif_out.vectors[2].elems[2].data.value;
    assign hwif_out_vectors_2_elems_3_data_value = hwif_out.vectors[2].elems[3].data.value;
    assign hwif_out_vectors_3_elems_0_data_value = hwif_out.vectors[3].elems[0].data.value;
    assign hwif_out_vectors_3_elems_1_data_value = hwif_out.vectors[3].elems[1].data.value;
    assign hwif_out_vectors_3_elems_2_data_value = hwif_out.vectors[3].elems[2].data.value;
    assign hwif_out_vectors_3_elems_3_data_value = hwif_out.vectors[3].elems[3].data.value;
    assign hwif_out_vectors_4_elems_0_data_value = hwif_out.vectors[4].elems[0].data.value;
    assign hwif_out_vectors_4_elems_1_data_value = hwif_out.vectors[4].elems[1].data.value;
    assign hwif_out_vectors_4_elems_2_data_value = hwif_out.vectors[4].elems[2].data.value;
    assign hwif_out_vectors_4_elems_3_data_value = hwif_out.vectors[4].elems[3].data.value;
    assign hwif_out_vectors_5_elems_0_data_value = hwif_out.vectors[5].elems[0].data.value;
    assign hwif_out_vectors_5_elems_1_data_value = hwif_out.vectors[5].elems[1].data.value;
    assign hwif_out_vectors_5_elems_2_data_value = hwif_out.vectors[5].elems[2].data.value;
    assign hwif_out_vectors_5_elems_3_data_value = hwif_out.vectors[5].elems[3].data.value;
    assign hwif_out_vectors_6_elems_0_data_value = hwif_out.vectors[6].elems[0].data.value;
    assign hwif_out_vectors_6_elems_1_data_value = hwif_out.vectors[6].elems[1].data.value;
    assign hwif_out_vectors_6_elems_2_data_value = hwif_out.vectors[6].elems[2].data.value;
    assign hwif_out_vectors_6_elems_3_data_value = hwif_out.vectors[6].elems[3].data.value;
    assign hwif_out_vectors_7_elems_0_data_value = hwif_out.vectors[7].elems[0].data.value;
    assign hwif_out_vectors_7_elems_1_data_value = hwif_out.vectors[7].elems[1].data.value;
    assign hwif_out_vectors_7_elems_2_data_value = hwif_out.vectors[7].elems[2].data.value;
    assign hwif_out_vectors_7_elems_3_data_value = hwif_out.vectors[7].elems[3].data.value;
endmodule
