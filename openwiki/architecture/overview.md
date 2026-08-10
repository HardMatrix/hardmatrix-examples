---
type: Architecture Overview
title: Repository Architecture
description: Structural and runtime architecture of the HardMatrix examples, including shared verification support, parameterized pipeline experiments, and the software-to-RTL PyTorch path.
tags: [architecture, rtl, pipeline, pytorch, renode]
---

# Repository architecture

## Architectural shape

This is an examples repository rather than a single deployable system. `examples/` contains independently runnable demonstrations, while `shared/` holds reusable RTL and cocotb support. Build orchestration is split between root-level uv/FuseSoC configuration and example-local FuseSoC cores, Makefiles, and scripts.

```text
examples/
  axis-eth-fcs/           Byte-stream RTL block and cocotb verification
  area-timing-sweep/      Parameterized ARX and RS pipelines plus observations
  pytorch-custom-device/  Python → C++ → driver/protocol → RTL example
shared/
  rtl/axis-if/            AXI4-Stream interface and assertions
  python/utils/tb_utils/  cocotb driver, monitor, and traffic generators
```

The [AXI Ethernet FCS](../domain/axis-ethernet-fcs.md) example depends directly on both shared areas. The [area-timing sweep](../domain/area-timing-sweep.md) uses the root verification environment but has no shared RTL dependency. The [PyTorch custom device](../domain/pytorch-custom-device.md) mostly carries its own AXI4-Lite interface and verification stack because it demonstrates a larger vertical integration.

## Independent pipeline experiment

`area-timing-sweep` holds two fixed-work, feed-forward datapaths: 64 ARX rounds and a 64-coefficient GF(2^10) Horner evaluation. In each module, elaboration-time integer boundaries partition operations across `PIPELINE_STAGES`, and every partition ends in a register. Both accept one input per cycle without backpressure; only `valid_o` identifies meaningful output. The RS pipeline adds a coefficient-load prerequisite and suppresses inputs until coefficients have been captured.

The checked-in CSV/SVG results compare all depths from 1 through 64 at a 1 GHz synthesis target. They are derived observations rather than a build product of the public core: this repository contains no synthesis target or plot-generation source. The [development workflow](../workflows/development.md) therefore treats cocotb as the ordinary correctness path and the result tables as historical experiment evidence.

## AXI Ethernet FCS path

`axis_eth_fcs_insert.sv` is a two-state streaming component. During payload bypass it forwards accepted bytes combinationally while updating a reflected CRC-32. It suppresses the payload's incoming `tlast`; after the final payload handshake it blocks upstream traffic and emits the complemented CRC as four least-significant-byte-first beats, asserting downstream `tlast` only on the fourth.

FuseSoC resolves the example core's dependency on the shared `axis_if` core. A SystemVerilog wrapper presents flat signals to cocotb; Python drivers and monitors generate packet traffic and compare output against `zlib.crc32`. See the [testing runbook](../operations/testing-runbook.md) for the exact simulation and lint paths.

## PyTorch custom-device path

The custom-device example is intentionally layered to demonstrate how a framework operation reaches modeled hardware:

```text
PyTorch tensor operation
  → mydev Python import and PrivateUse1 registration
  → C++ allocator, device guard, and dispatcher kernels
  → local ioctl backend OR remote TCP backend
  → /dev/tensor0 Linux driver
  → AXI4-Lite register transaction
  → Chisel VectorAdderMachine + generated PeakRDL register block
```

Only `aten::add.Tensor` and `aten::sub.Tensor` have accelerator kernels. Device allocation uses host `malloc`, generic operators can access those buffers directly, and unregistered operations fall back to CPU. This makes the example easy to exercise but is not a model of isolated accelerator memory or asynchronous streams.

### Local path

The default C++ backend opens `/dev/tensor0` and issues `TENSOR_IOC_SUBMIT`. The Linux driver supports a software register-space mock and a real platform-MMIO mode. In real mode it writes source vectors, clears status, writes one packed instruction, polls completion, and reads the destination vector.

### Remote Renode path

With `TENSOR_BACKEND=remote`, the C++ backend connects to `TENSOR_REMOTE_ADDR` (default `localhost:9001`), waits for `READY\n`, and sends a packed little-endian request. Renode exposes the guest's second UART over TCP. The guest relay converts requests into the same ioctl ABI; the guest driver accesses a `CoSimulatedPeripheral` backed by a Verilated accelerator library.

This remote path depends on the [integration contracts](../integrations/interfaces.md) staying synchronized across host C++, relay, guest driver, platform description, device tree, generated register map, and RTL.

## Hardware control model

The canonical register-map specification is `examples/pytorch-custom-device/hw/chisel/vector_adder_machine/rdl/vector_adder_machine.rdl`:

- instruction register at `0x00`;
- status at `0x04` (`done`, `error`, write-one `clear`);
- eight four-element vectors beginning at `0x100`;
- four 32-bit elements per vector and a 16-byte vector stride.

Writing the instruction opcode field triggers execution. The Chisel unit snapshots both input vectors, computes one element per cycle, and publishes all four result elements together. The top level always accepts the output and latches done/error status. The driver currently uses vectors 0 and 1 as inputs and vector 2 as output.

## Design intent and history

The original FCS and PyTorch examples and their self-hosted regression were introduced together by `20a809c`, indicating that the repository's main product is executable reference material rather than a reusable production library. Commit `23d937c` then removed the workflow without replacing it. The area/timing experiment is a later working-tree addition, while `02fac4b` fixes fresh Renode relay packaging by creating the Buildroot overlay directory before installation. The architecture remains testable locally, but automation is no longer tracked; the [development workflow](../workflows/development.md) and [testing runbook](../operations/testing-runbook.md) therefore describe local commands as authoritative.

## Change boundaries

- Changes confined to the FCS algorithm should stay inside its RTL and test, but interface changes also affect shared AXI support and the core dependency.
- Changes to PyTorch operator semantics cross C++ kernels, `include/api.h`, driver behavior, Chisel opcodes, and tests.
- Register-map changes start from RDL and require generated artifacts, driver literals, the Renode adapter, and register-level tests to be audited.
- Platform address or compatible-string changes must update both `renode/platform.repl` and `renode/buildroot/tensor_soc.dts`.

Use the [source map](../source-map.md) to locate each owning file before editing.