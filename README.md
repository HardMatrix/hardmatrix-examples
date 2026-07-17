# hardmatrix-examples

Public examples and companion code for HardMatrix development workflows.

Run commands in this README from the repository root.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- Verilator and standard C/C++ build tools for RTL tests

## Install

Install the repository-level verification environment:

```sh
uv sync
```

## AXI Ethernet FCS tests

Run the cocotb test:

```sh
uv run fusesoc \
  --config=fusesoc.conf \
  --cores-root=examples/axis-eth-fcs \
  --cores-root=shared/rtl/axis-if \
  run --target test hardmatrix:examples:axis_eth_fcs_insert:0.1.0
```

Run Verilator lint with the same environment and core roots:

```sh
uv run fusesoc \
  --config=fusesoc.conf \
  --cores-root=examples/axis-eth-fcs \
  --cores-root=shared/rtl/axis-if \
  run --target lint hardmatrix:examples:axis_eth_fcs_insert:0.1.0
```

See [`examples/axis-eth-fcs/README.md`](examples/axis-eth-fcs/README.md) for
the files used by this example.

## PyTorch custom-device tests

The PyTorch example uses its own environment:

```sh
cd examples/pytorch-custom-device
uv sync
make test-hw
```

See
[`examples/pytorch-custom-device/README.md`](examples/pytorch-custom-device/README.md)
for host-driver and Renode test instructions.

## Development layout

```text
examples/
  axis-eth-fcs/           Standalone AXI4-Stream Ethernet FCS RTL example
  pytorch-custom-device/  Full-stack PyTorch custom-device example
shared/
  rtl/                    RTL interfaces shared by examples
  python/                 Python verification helpers shared by examples
```
