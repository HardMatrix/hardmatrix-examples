# AXI Ethernet FCS Inserter

This example appends a four-byte Ethernet FCS to each byte-wide AXI4-Stream packet.

Run all commands from the `hardmatrix-examples` repository root.

## Install

```sh
uv sync
```

## Test

```sh
uv run fusesoc \
  --config=fusesoc.conf \
  --cores-root=examples/axis-eth-fcs \
  --cores-root=shared/rtl/axis-if \
  run --target test hardmatrix:examples:axis_eth_fcs_insert:0.1.0
```

## Lint

```sh
uv run fusesoc \
  --config=fusesoc.conf \
  --cores-root=examples/axis-eth-fcs \
  --cores-root=shared/rtl/axis-if \
  run --target lint hardmatrix:examples:axis_eth_fcs_insert:0.1.0
```

## Development files

- `rtl/`: SystemVerilog implementation
- `test/`: cocotb test and SystemVerilog testbench
- `axis_eth_fcs.core`: FuseSoC test and lint targets
