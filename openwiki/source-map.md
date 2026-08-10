---
type: Source Map
title: Repository Source Map
description: Engineer-oriented map of authoritative sources, generated artifacts, tests, build entrypoints, and ownership boundaries in hardmatrix-examples.
tags: [source-map, navigation, maintenance]
---

# Repository source map

Use this page to find the owning source before editing. Runtime relationships are in the [architecture overview](architecture/overview.md), and commands/checks are in the [development workflow](workflows/development.md) and [testing runbook](operations/testing-runbook.md).

## Repository level

| Path | Role |
|---|---|
| `README.md` | Supported entry commands and top-level layout |
| `pyproject.toml`, `uv.lock` | Root cocotb/FuseSoC verification environment |
| `fusesoc.conf` | Minimal project config; core roots are supplied per command |
| `shared/rtl/axis-if/` | Shared AXI4-Stream interface, modports, and assertions |
| `shared/python/utils/tb_utils/` | Reusable cocotb AXI stream driver/monitor and traffic helpers |
| `examples/area-timing-sweep/` | Independent fixed-work pipeline-depth experiment, cocotb bring-up, and checked-in synthesis observations |
| `openwiki/INSTRUCTIONS.md` | User-authored OpenWiki scope; control metadata, not generated docs |

Build outputs, `.venv`, caches, and `shared/python/*.egg-info` are not source.

## AXI Ethernet FCS

| Path | Ownership |
|---|---|
| `examples/axis-eth-fcs/rtl/axis_eth_fcs_insert.sv` | Packet FSM, handshake, CRC capture, FCS emission |
| `examples/axis-eth-fcs/rtl/eth_crc32_byte.sv` | Reflected byte-at-a-time CRC update |
| `examples/axis-eth-fcs/axis_eth_fcs.core` | FuseSoC dependency plus default/lint/test targets |
| `examples/axis-eth-fcs/test/tb_axis_eth_fcs_insert.sv` | Cocotb-facing wrapper |
| `examples/axis-eth-fcs/test/test_axis_eth_fcs_insert.py` | Reference model and behavioral tests |
| `examples/axis-eth-fcs/README.md` | Local usage summary |

Read [AXI Ethernet FCS](domain/axis-ethernet-fcs.md) for semantic hazards before changing these files.

## Area-timing sweep

| Path | Ownership |
|---|---|
| `examples/area-timing-sweep/rtl/arx_pipeline.sv` | ARX round function, parameter guards, work distribution, pipeline validity |
| `examples/area-timing-sweep/rtl/rs_chien_horner_pipeline.sv` | Coefficient load state, GF multiplication, Horner-term distribution, root indication |
| `examples/area-timing-sweep/area_timing_sweep.core` | FuseSoC `test_arx` and `test_rs` targets and public `PIPELINE_STAGES` parameter |
| `examples/area-timing-sweep/test/test_arx_pipeline.py` | 64-round Python model and ordered streaming bring-up |
| `examples/area-timing-sweep/test/test_rs_chien_horner_pipeline.py` | GF model, coefficient-load sequence, polynomial/root bring-up |
| `examples/area-timing-sweep/results/` | Checked-in CSV/SVG post-synthesis observations; derived and not reproducible from this repository alone |

Read [Area-timing sweep](domain/area-timing-sweep.md) before changing operation partitioning, validity latency, coefficient ordering, or interpreting synthesis data.

## PyTorch front end and extension

| Path | Ownership |
|---|---|
| `examples/pytorch-custom-device/mydev/__init__.py` | Extension import and device-module registration |
| `mydev/_device.py` | Python device availability/count/synchronization surface |
| `setup.py`, `pyproject.toml` | C++ extension packaging and Python/PyTorch constraints |
| `cpp/ops/init.cpp` | PrivateUse1 naming, device guard, extension API |
| `cpp/ops/allocator.*` | Host-memory PrivateUse1 allocator |
| `cpp/ops/ops.cpp` | Generic tensor/storage/copy operations and fallback registration |
| `cpp/ops/add.cpp`, `sub.cpp` | Hardware-backed operator validation and submission |
| `cpp/ops/backend.*` | Process-lifetime local/remote backend implementations |

## Driver and shared protocols

| Path | Ownership |
|---|---|
| `include/api.h` | Canonical ioctl ABI, tensor opcodes, max element count |
| `include/remote_api.h` | Canonical packed TCP protocol |
| `cpp/driver/src/hal.c` | Linux platform/misc driver, mock arithmetic, real MMIO transaction |
| `cpp/driver/Makefile` | Host kernel-module build |
| `renode/relay/relay.c` | Guest UART/TCP protocol-to-ioctl bridge |

These files form the core contracts described in [integration points](integrations/interfaces.md); change them as a synchronized set.

## Accelerator source and generated files

**Authoritative design sources**

- `hw/chisel/vector_adder_machine/rdl/vector_adder_machine.rdl` — register map.
- `src/VectorAdderMachine.scala` — top-level register-to-compute wiring.
- `src/VectorAdderUnit.scala` — lane computation/state machine.
- `src/VectorAdderMachineRegmapBlackBox.scala` — generated block bridge.
- `src/VectorRedAdderUnit.scala` — currently unused implementation.
- `build.mill` — Chisel build/generation definition.
- `vector_adder_machine.core` — FuseSoC generator and test targets.
- `hw/axi4_lite/src/axi4lite_intf.sv` — local AXI4-Lite interface.

Paths above are relative to `examples/pytorch-custom-device/hw/chisel/vector_adder_machine` except the AXI interface.

**Checked-in generated artifacts**

- `src/vector_adder_machine_regmap.sv`
- `src/vector_adder_machine_regmap_pkg.sv`
- `src/vector_adder_machine_regmap_wrapper.sv`
- `src/vector_adder_machine_regmap_bundles.scala`
- `test/vector_adder_machine_rdl.py`
- `generated/` when present after generation

Do not make isolated fixes only in generated files. Regenerate from RDL/Scala and inspect the diff. A unified PeakRDL regeneration command is currently undocumented.

**Tests**

- `test/test_vector_adder_machine.py` — normal cocotb accelerator tests.
- `test/test_vector_adder_machine_socket.py` — optional socket/register integration target.

## Renode and guest system

| Path | Ownership |
|---|---|
| `renode/platform.repl` | Emulated RISC-V platform and accelerator mapping |
| `renode/resc/*.resc` | Boot and direct register scenarios |
| `renode/buildroot/tensor_soc.dts` | Guest hardware description; must match `.repl` |
| `renode/buildroot/kernel.fragment` | Guest kernel features |
| `renode/buildroot/overlay/init` | Guest startup/module/relay handoff |
| `renode/buildroot/build.sh` | Pinned Buildroot, kernel, OpenSBI, module/image process |
| `renode/verilator/sim_renode.cpp` | Renode IntegrationLibrary adapter |
| `renode/verilator/build.sh` | Verilated shared-library build |
| `renode/images/` | Checked-in firmware/kernel/DTB artifacts; derived, potentially stale |

## Orchestration and tests

| Path | Role |
|---|---|
| `examples/pytorch-custom-device/Makefile` | Preferred host, hardware, mock, remote, rebuild, cleanup targets |
| `scripts/run_tests.sh` | Phase runner; remote phase does not rebuild Verilator library |
| `tests/test_pytorch_mock.py` | Local PrivateUse1 + mock-driver tests |
| `tests/test_pytorch_remote.py` | Remote/Renode E2E tests and optional autostart |

## History-sensitive areas

The original FCS and PyTorch implementation was imported almost entirely in commit `20a809c`; there is little incremental blame history to explain individual design choices. Commit `23d937c` removed the self-hosted regression workflow. Commit `02fac4b` made relay packaging robust on a fresh Buildroot overlay by creating `overlay/sbin` before copying the binary. The area/timing example and root README changes are currently uncommitted working-tree additions, so they have no Git rationale beyond their source and README evidence.

For change impact, start with the relevant domain page—[FCS](domain/axis-ethernet-fcs.md), [area-timing sweep](domain/area-timing-sweep.md), or [PyTorch custom device](domain/pytorch-custom-device.md)—then follow its links to integrations and tests.