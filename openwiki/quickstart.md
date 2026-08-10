---
type: Quickstart
title: hardmatrix-examples Quickstart
description: Entry point for the HardMatrix public examples repository, covering setup, three hardware examples, verification paths, and exact change navigation for engineers.
tags: [hardmatrix, examples, hardware, verification]
---

# hardmatrix-examples quickstart

## What this repository is

`hardmatrix-examples` is a public companion repository for demonstrating HardMatrix hardware-development workflows. It contains three independent examples:

- A byte-wide AXI4-Stream block that appends an Ethernet CRC-32 frame check sequence.
- An area/timing experiment that distributes fixed 64-operation ARX and Reed-Solomon Chien/Horner workloads over configurable pipeline depths.
- A full-stack PyTorch `PrivateUse1` custom device that sends small integer add/subtract operations through either a Linux ioctl driver or a TCP-to-Renode path to a four-lane RTL accelerator.

The examples share verification and interface infrastructure where useful, but they are not one runtime application. The [architecture overview](architecture/overview.md) explains their boundaries and the PyTorch example's layered data path.

## Start here

Install [uv](https://docs.astral.sh/uv/), Verilator, and standard C/C++ build tools, then create the root verification environment:

```sh
uv sync
```

The root `pyproject.toml` installs pytest, cocotb, cocotb-bus, and FuseSoC and exposes `shared/python/utils`. The PyTorch example has a separate environment and additional JDK, Ninja, Linux-header, Renode, and optionally Buildroot requirements.

### AXI Ethernet FCS

```sh
uv run fusesoc \
  --config=fusesoc.conf \
  --cores-root=examples/axis-eth-fcs \
  --cores-root=shared/rtl/axis-if \
  run --target test hardmatrix:examples:axis_eth_fcs_insert:0.1.0
```

Read [AXI Ethernet FCS](domain/axis-ethernet-fcs.md) before changing CRC ordering, `tlast`, backpressure, or stream width.

### Area-timing sweep

```sh
uv run fusesoc \
  --config=fusesoc.conf \
  --cores-root=examples/area-timing-sweep \
  run --target test_arx hardmatrix:examples:area_timing_sweep:0.1.0
uv run fusesoc \
  --config=fusesoc.conf \
  --cores-root=examples/area-timing-sweep \
  run --target test_rs hardmatrix:examples:area_timing_sweep:0.1.0
```

Read [Area-timing sweep](domain/area-timing-sweep.md) before changing pipeline partitioning, validity latency, GF arithmetic, coefficient loading, or interpreting the checked-in synthesis results.

### PyTorch custom device

```sh
cd examples/pytorch-custom-device
uv sync
make test-hw
```

Read [PyTorch custom device](domain/pytorch-custom-device.md) before changing operator constraints, ABI structures, opcodes, register addresses, device count, or generated hardware files.

## Wiki map

- [Architecture overview](architecture/overview.md) — component boundaries and runtime data flows.
- [AXI Ethernet FCS](domain/axis-ethernet-fcs.md) — stream/CRC behavior and design invariants.
- [Area-timing sweep](domain/area-timing-sweep.md) — parameterized pipelines, correctness boundaries, and synthesis observations.
- [PyTorch custom device](domain/pytorch-custom-device.md) — software, driver, protocol, and accelerator model.
- [Development workflows](workflows/development.md) — setup, build, regeneration, and change-oriented paths.
- [Testing and operations runbook](operations/testing-runbook.md) — test matrix, privileged steps, troubleshooting, and cleanup.
- [Integration points](integrations/interfaces.md) — external tools and cross-layer contracts.
- [Source map](source-map.md) — practical file ownership and navigation.

## Change routing

| Change area or intent | Wiki page | Exact source entry points | Important symbols/types | Focused tests | Minimal validation |
|---|---|---|---|---|---|
| FCS bytes, flow, or AXI handshake | [AXI Ethernet FCS](domain/axis-ethernet-fcs.md) | `examples/axis-eth-fcs/rtl/axis_eth_fcs_insert.sv`, `rtl/eth_crc32_byte.sv` | `axis_eth_fcs_insert`, `eth_crc32_byte` | `test/test_axis_eth_fcs_insert.py` | Root FuseSoC `--target test` for `hardmatrix:examples:axis_eth_fcs_insert:0.1.0` |
| Pipeline depth or ARX behavior | [Area-timing sweep](domain/area-timing-sweep.md) | `examples/area-timing-sweep/rtl/arx_pipeline.sv`, `area_timing_sweep.core` | `arx_pipeline`, `arx_round`, `PIPELINE_STAGES` | `test/test_arx_pipeline.py` | Root FuseSoC `--target test_arx` for `hardmatrix:examples:area_timing_sweep:0.1.0` |
| RS GF arithmetic or coefficient lifecycle | [Area-timing sweep](domain/area-timing-sweep.md) | `examples/area-timing-sweep/rtl/rs_chien_horner_pipeline.sv` | `rs_chien_horner_pipeline`, `gf_multiply`, `coefficients_loaded` | `test/test_rs_chien_horner_pipeline.py` | Root FuseSoC `--target test_rs` for `hardmatrix:examples:area_timing_sweep:0.1.0` |
| PyTorch operator or backend | [PyTorch custom device](domain/pytorch-custom-device.md) | `cpp/ops/add.cpp`, `sub.cpp`, `backend.*`, `include/api.h` | dispatcher kernels, `Backend`, `tensor_submit` | `tests/test_pytorch_mock.py`, `tests/test_pytorch_remote.py` | `make test-mock` or `make test-remote` for the changed backend |
| Accelerator/register map | [Integration points](integrations/interfaces.md) | `hw/chisel/vector_adder_machine/rdl/vector_adder_machine.rdl`, `src/VectorAdderMachine.scala` | RDL registers, `VectorAdderMachine` | `test/test_vector_adder_machine.py` | `make test-hw` |
| Renode guest image or relay packaging | [Development workflows](workflows/development.md) | `Makefile`, `renode/relay/relay.c`, `renode/buildroot/build.sh` | `relay`, `renode-build` | `tests/test_pytorch_remote.py` | Conditional: `BUILDROOT_DIR=/path/to/buildroot make renode-build`, then `make test-remote` |

Commands abbreviated in this table are written in full on the linked page.

## Repository conventions

- Run root README commands from the repository root; run PyTorch commands from `examples/pytorch-custom-device`.
- Treat `*.core` files and Make targets as executable build/test definitions. The root `fusesoc.conf` intentionally declares no libraries; commands supply core roots.
- Do not treat generated files, guest images, Verilated libraries, or area/timing CSV/SVG outputs as authoritative source. The [source map](source-map.md) identifies source/derived boundaries.
- The mock-driver procedure loads a kernel module and may use mode `0666`. Follow the [testing runbook](operations/testing-runbook.md); persistent systems should keep default `0660` and use a group or udev rule.

## Repository evolution

Commit `20a809c` introduced the FCS and PyTorch examples, shared utilities, and a self-hosted regression workflow in one large import. Commit `23d937c` removed that workflow, and current HEAD `02fac4b` makes a clean `make renode-build` reliable by creating the relay overlay directory before installation. The area/timing example and its root README entry are current working-tree additions rather than committed history. There is no tracked CI runner, so local test commands remain the source of truth.

## Backlog

- **PeakRDL regeneration** — `examples/pytorch-custom-device/hw/chisel/vector_adder_machine/rdl/vector_adder_machine.rdl`: generated SV, Scala, and Python artifacts exist, but no canonical all-artifact regeneration command is documented.
- **Optional socket test** — `examples/pytorch-custom-device/hw/chisel/vector_adder_machine/vector_adder_machine.core`: `test_socket` is not included by `make test-hw`.
- **FCS edge-case verification** — `examples/axis-eth-fcs/test/test_axis_eth_fcs_insert.py`: reset during a frame/FCS, source-valid gaps, and explicit eight-bit width enforcement remain uncovered.
- **Area/timing test matrix** — `examples/area-timing-sweep/test/`: exact latency, reset, parameter-guard failures, valid gaps, multiple stage counts, input-before-coefficient-load, and coefficient reload in flight remain uncovered.
- **Area/timing result reproduction** — `examples/area-timing-sweep/results/README.md`: provenance and outputs are recorded, but the Hydra/OpenROAD orchestration and plotting source needed to reproduce them are absent.
