module eth_crc32_byte
#()
(
    input  logic [32-1:0] crc_i,
    input  logic [8-1:0]  data_i,
    input  logic          valid_i,
    output logic [32-1:0] crc_o,
    output logic          crc_ready_o
);

    localparam logic [32-1:0] CRC_POLY = 32'hEDB8_8320;

    always_comb begin : crc32_update_byte_proc
        crc_o = crc_i;
        for (int unsigned i = 0; i < 8; i++) begin
            if (crc_o[0] ^ data_i[i]) begin
                crc_o = (crc_o >> 1) ^ CRC_POLY;
            end else begin
                crc_o = crc_o >> 1;
            end
        end
    end : crc32_update_byte_proc

    assign crc_ready_o = valid_i;

endmodule
