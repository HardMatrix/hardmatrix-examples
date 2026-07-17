# Hardware

Run hardware commands from the `pytorch-custom-device` example root.

## Prerequisites

- Complete `uv sync` in the example root
- Install Verilator and a JDK

## Test

```sh
make test-hw
```

## Development files

```text
axi4_lite/                     Shared AXI4-Lite interface
chisel/vector_adder_machine/   Chisel design, generated CSR RTL, and tests
```
