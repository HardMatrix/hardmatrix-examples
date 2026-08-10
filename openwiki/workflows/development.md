---
type: Development Guide
title: Development Workflows
description: Practical setup, build, change, and artifact-rebuild workflows for the HardMatrix RTL and PyTorch custom-device examples.
tags: [development, build, fusesoc, renode]
---

# Development workflows

## Environment split

The repository uses two uv environments:

- The root environment supports the [AXI Ethernet FCS](../domain/axis-ethernet-fcs.md) and [area-timing sweep](../domain/area-timing-sweep.md) examples plus shared cocotb utilities.
- `examples/pytorch-custom-device/.venv` supports PyTorch, extension building, accelerator tests, and remote tests.

Run commands from the directory stated in the relevant README; paths in Makefiles and scripts assume that working directory.

## AXI Ethernet FCS workflow

From the repository root:

```sh
uv sync
uv run fusesoc \
  --config=fusesoc.conf \
  --cores-root=examples/axis-eth-fcs \
  --cores-root=shared/rtl/axis-if \
  run --target test hardmatrix:examples:axis_eth_fcs_insert:0.1.0
```

For lint, replace `--target test` with `--target lint`. The core manifest is `examples/axis-eth-fcs/axis_eth_fcs.core`; the root `fusesoc.conf` is intentionally minimal, so omitting either core root prevents dependency resolution.

Typical change path:

1. Edit `rtl/axis_eth_fcs_insert.sv` for flow/state behavior or `rtl/eth_crc32_byte.sv` for CRC logic.
2. Update `test/test_axis_eth_fcs_insert.py` to encode the intended packet contract.
3. If the interface changes, update the wrapper and audit `shared/rtl/axis-if` plus `shared/python/utils/tb_utils`.
4. Run test and lint targets as specified in the [testing runbook](../operations/testing-runbook.md).

## Area-timing sweep workflow

From the repository root after `uv sync`, run the independent targets:

```sh
uv run fusesoc --config=fusesoc.conf \
  --cores-root=examples/area-timing-sweep \
  run --target test_arx hardmatrix:examples:area_timing_sweep:0.1.0
uv run fusesoc --config=fusesoc.conf \
  --cores-root=examples/area-timing-sweep \
  run --target test_rs hardmatrix:examples:area_timing_sweep:0.1.0
```

`area_timing_sweep.core` passes `PIPELINE_STAGES` as a Verilog parameter; override it with FuseSoC parameter syntax when changing or sampling partition behavior. For ARX changes, keep `arx_round` and Python `arx_model` synchronized. For RS changes, keep `gf_multiply`, coefficient packing/order, and `polynomial_value` synchronized. Run both targets when changing common pipeline assumptions; one target is otherwise the narrowest check.

The CSV and SVG files under `results/` came from an external Hydra/OpenROAD ASAP7 sweep. No synthesis target, orchestration, or plotting code is checked in, so ordinary RTL changes should not hand-edit these derived artifacts. Escalate to the external sweep only when publishing new area/timing claims; see [Area-timing sweep](../domain/area-timing-sweep.md).

## PyTorch fast-cycle workflow

From `examples/pytorch-custom-device`:

```sh
uv sync
make test-hw
```

`make all`/`make build` creates the environment and builds the host kernel driver, but does not install the C++ PyTorch extension as an explicit target. Tests assume the environment/extension setup described by the example's packaging and README; the removed CI workflow explicitly used:

```sh
uv pip install -e . --no-build-isolation
```

### Hardware-only changes

`make test-hw` runs `fusesoc_setup.sh`, then the `hardmatrix:accelerators:vector_adder_machine:0.1.0` FuseSoC `test` target. FuseSoC invokes Mill to generate Chisel SystemVerilog and runs cocotb with Verilator.

For register-map changes, start at `hw/chisel/vector_adder_machine/rdl/vector_adder_machine.rdl`, not the generated files. The repository checks generated SV, Scala bundles, and a Python RDL model into `src/` and `test/`, but does not document one command that regenerates all of them. Until that gap is resolved, audit the generated set listed in the [source map](../source-map.md) and validate both ordinary and register/socket tests.

### Mock-driver changes

Build and load the module, then run PyTorch tests:

```sh
make -C cpp/driver
sudo insmod cpp/driver/tensor.ko \
  mock=1 debug=0 mock_autocreate=1 device_mode=0666
make test-mock
sudo rmmod tensor
```

Use `0666` only on a disposable development machine. Driver, ioctl, or operator changes should be checked against the [PyTorch domain invariants](../domain/pytorch-custom-device.md).

### Remote/Renode changes

The standard checked-in-artifact path is:

```sh
make test-remote
```

That target first runs `make verilator-lib`, then starts the remote pytest path with `TENSOR_BACKEND=remote` and `TENSOR_REMOTE_ADDR=localhost:9001`. Localhost tests can autostart Renode.

After changing guest driver, relay, kernel configuration, device tree, or platform files:

```sh
BUILDROOT_DIR=/path/to/buildroot make renode-build
make test-remote
```

`renode-build` rebuilds the Verilated library, relay, RISC-V driver module, and image. Its `relay` prerequisite creates `renode/buildroot/overlay/sbin` before installing the relay, so a fresh or cleaned overlay does not need that directory prepared manually. Buildroot setup is documented in `renode/buildroot/README.md`; source scripts pin Buildroot commit `49d1ea93f7d3ad8f7113cea39be4c39b4d6faca6`, Linux 6.18.7, and OpenSBI 1.6.

For manual scenarios, build the library, create `out/`, and run one of the `.resc` scripts documented in `renode/resc/README.md`. `vam_regtest.resc` isolates the register-level RTL path without Linux.

## Choosing a test orchestrator

Prefer Make targets for documented behavior. `scripts/run_tests.sh [hw|mock|remote|all]` provides phase reporting and can load a missing mock driver, but it is not equivalent to the Makefile: its remote phase does not explicitly depend on `verilator-lib`. Running it after RTL changes can therefore use stale artifacts.

## Cleanup

From the PyTorch example:

```sh
make clean
```

This removes `.venv`, `build`, `out`, Python caches, and cleans the host driver. It does not regenerate or validate checked-in guest images. Use the [integration page](../integrations/interfaces.md) to determine which external artifact chain a source change affects.
