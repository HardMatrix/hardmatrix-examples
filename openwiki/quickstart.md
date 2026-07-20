---
type: Quickstart
title: hardmatrix-examples Quickstart
description: Entry point for the HardMatrix public examples repository, covering setup, the two hardware examples, verification paths, and where engineers should make changes.
tags: [hardmatrix, examples, hardware, verification]
---

# hardmatrix-examples quickstart

## What this repository is

`hardmatrix-examples` is a public companion repository for demonstrating HardMatrix hardware-development workflows. It currently contains two independent examples:

- A byte-wide AXI4-Stream block that appends an Ethernet CRC-32 frame check sequence.
- A full-stack PyTorch `PrivateUse1` custom device that sends small integer add/subtract operations through either a Linux ioctl driver or a TCP-to-Renode path to a four-lane RTL accelerator.

The examples share verification and interface infrastructure, but they are not one runtime application. The [architecture overview](architecture/overview.md) explains their boundaries and the PyTorch example's layered data path.

## Start here

### Prerequisites

At repository level, install [uv](https://docs.astral.sh/uv/), Verilator, and standard C/C++ build tools. Then create the root verification environment:

```sh
uv sync
```

The root `pyproject.toml` installs pytest, cocotb, cocotb-bus, and FuseSoC and exposes `shared/python/utils` as a package. The PyTorch example has a separate environment and additional JDK, Ninja, Linux-header, Renode, and optionally Buildroot requirements.

### Choose a path

**AXI Ethernet FCS**

```sh
uv run fusesoc \
  --config=fusesoc.conf \
  --cores-root=examples/axis-eth-fcs \
  --cores-root=shared/rtl/axis-if \
  run --target test hardmatrix:examples:axis_eth_fcs_insert:0.1.0
```

Read [AXI Ethernet FCS](domain/axis-ethernet-fcs.md) before changing CRC ordering, `tlast`, backpressure, or stream width.

**PyTorch custom device**

```sh
cd examples/pytorch-custom-device
uv sync
make test-hw
```

Read [PyTorch custom device](domain/pytorch-custom-device.md) before changing operator constraints, ABI structures, opcodes, register addresses, device count, or generated hardware files.

## Wiki map

- [Architecture overview](architecture/overview.md) — component boundaries and runtime data flows.
- [AXI Ethernet FCS](domain/axis-ethernet-fcs.md) — stream/CRC behavior and design invariants.
- [PyTorch custom device](domain/pytorch-custom-device.md) — software, driver, protocol, and accelerator model.
- [Development workflows](workflows/development.md) — setup, build, regeneration, and change-oriented paths.
- [Testing and operations runbook](operations/testing-runbook.md) — test matrix, privileged steps, troubleshooting, and cleanup.
- [Integration points](integrations/interfaces.md) — external tools and cross-layer contracts.
- [Source map](source-map.md) — practical file ownership and navigation.

## Repository conventions

- Run root README commands from the repository root; run PyTorch example commands from `examples/pytorch-custom-device`.
- Treat `*.core` files and Make targets as the executable build/test definitions. The root `fusesoc.conf` intentionally does not declare libraries; commands supply core roots explicitly.
- Do not treat generated files, guest images, or Verilated libraries as authoritative source. The [source map](source-map.md) identifies source/generated boundaries.
- The PyTorch mock-driver instructions load a kernel module and may use mode `0666`. Follow the safety guidance in the [testing runbook](operations/testing-runbook.md); persistent systems should keep the driver's default `0660` and use a group or udev rule.

## Repository evolution

The initial commit contained only repository scaffolding. Commit `20a809c` introduced both examples, shared utilities, their docs, and a self-hosted regression workflow in one large examples import. The current HEAD, `23d937c`, removed that workflow. Consequently, `.github/workflows/run-regression.yml` is present only as an untracked working-tree file at documentation time; there is no tracked CI runner, and local test commands are the current source of truth.

## Backlog

- **PeakRDL regeneration** — `examples/pytorch-custom-device/hw/chisel/vector_adder_machine/rdl/vector_adder_machine.rdl`: the repository checks in generated SV, Scala, and Python artifacts but does not document one canonical command that regenerates all of them.
- **Optional socket test** — `examples/pytorch-custom-device/hw/chisel/vector_adder_machine/vector_adder_machine.core`: the `test_socket` target exists but is not included by `make test-hw`.
- **FCS edge-case verification** — `examples/axis-eth-fcs/test/test_axis_eth_fcs_insert.py`: reset during a frame/FCS, source-valid gaps, and explicit eight-bit width enforcement remain uncovered.
