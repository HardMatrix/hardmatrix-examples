# AXI Ethernet FCS Inserter

This example appends a four-byte Ethernet FCS to each byte-wide AXI4-Stream packet.
The cocotb test uses Python's `zlib.crc32` as the reference model and compares RTL
output with a `cocotb_bus` scoreboard.

```sh
fusesoc --cores-root=hw run --target test hardmatrix:examples:axis_eth_fcs_insert:0.1.0
```
