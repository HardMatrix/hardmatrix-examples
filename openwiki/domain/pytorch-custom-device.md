---
type: System Domain Concept
title: PyTorch Custom Device
description: Domain model and cross-layer invariants for the PrivateUse1-to-Linux-driver-to-RTL vector accelerator example, including local and Renode backends.
tags: [pytorch, privateuse1, linux-driver, chisel, renode]
---

# PyTorch custom device

## Product goal

`examples/pytorch-custom-device` demonstrates a complete framework-to-hardware path rather than a production accelerator backend. It connects PyTorch's `PrivateUse1` dispatch key to a synchronous four-element integer vector machine and provides two deployment modes: local `/dev/tensor0` ioctl access and a remote TCP path into a Renode RISC-V guest. Its place in the repository is summarized by the [architecture overview](../architecture/overview.md).

## PyTorch device model

Importing `mydev` loads the compiled `_C` extension and registers `mydev/_device.py` as the `privateuseone` device module. C++ initialization installs:

- one device, index 0;
- a `PrivateUse1` device guard;
- only the default stream;
- a custom allocator backed by host `malloc`/`free`;
- dispatcher implementations and boxed CPU fallback.

Execution is synchronous; `synchronize()` is effectively a no-op. Host-addressable allocation lets `cpp/ops/ops.cpp` implement copies, views, fill, scalar extraction, and storage operations by treating device memory as CPU memory. Unregistered operations can execute through CPU fallback. This convenience can hide missing accelerator kernels and would be invalid if allocation moved to non-host-accessible memory.

Only `aten::add.Tensor` and `aten::sub.Tensor` submit to the backend. Both require contiguous `torch.int32` operands on `PrivateUse1`, identical shapes, `alpha == 1`, and at most four elements. Broadcasting is not supported. Empty tensors return without submission.

## Backend selection

`cpp/ops/backend.cpp` creates one process-lifetime backend on first access:

- `TENSOR_BACKEND=remote` selects TCP.
- Any other or missing value selects local ioctl.

Because the selected object is a function-static singleton, changing the environment after first use does not switch modes in that process. Both backends serialize use with a mutex and retain their descriptor/socket.

### Local ioctl

The default path opens `/dev/tensor0`, fills `tensor_submit`, and calls `TENSOR_IOC_SUBMIT` with a 1000 ms timeout. The shared ABI in `include/api.h` is version 2, limits requests to four 32-bit elements, and assigns opcodes 1 and 2 to add/subtract.

`cpp/driver/src/hal.c` supports:

- **mock mode** — software-backed registers and arithmetic, optionally with a synthetic platform device;
- **real mode** — mapped platform MMIO and polling of the hardware status register.

The driver copies user inputs before locking, serializes the full register transaction, writes source vectors 0/1, clears status, writes the instruction once, and reads vector 2. Real mode busy-polls until completion, signal, or timeout; there is no interrupt path.

### Remote TCP and Renode

The remote backend connects to `TENSOR_REMOTE_ADDR` (default `localhost:9001`), applies `TENSOR_REMOTE_SOCKET_TIMEOUT_MS` (default 10 seconds), and requires `READY\n`. `include/remote_api.h` defines packed 32-byte request and 16-byte response headers; all peers must be little-endian.

The guest relay validates the request, invokes the same ioctl ABI, and returns the result. Renode routes UART1 to TCP and maps the Vector Adder Machine at `0x40000000`. The guest device tree binds that region to the driver with compatible string `acme,tensor-1.0`; Renode's co-simulated peripheral delegates AXI4-Lite accesses to a Verilated library. The full external boundary is documented in [integration points](../integrations/interfaces.md).

## Accelerator and register map

The RDL source defines:

- instruction `0x00`: opcode `[7:0]`, source A `[10:8]`, source B `[13:11]`, destination `[16:14]`;
- status `0x04`: done bit 0, error bit 1, clear bit 2;
- eight vectors from `0x100`, each four 32-bit words.

Writing the opcode field's `swmod` triggers work. `VectorAdderUnit.scala` snapshots the instruction and operands, computes one lane per cycle, and reports an error for an unsupported opcode. Add/sub arithmetic preserves 32-bit wraparound bit patterns. `VectorAdderMachine.scala` writes all four result lanes on output acceptance and latches status.

`VectorRedAdderUnit.scala` is present but is not connected by the top level.

## Cross-layer invariants

Changes must preserve these relationships:

| Contract | Coupled sources |
|---|---|
| Opcodes | `include/api.h`, driver, `VectorAdderUnit.scala`, RTL/PyTorch tests |
| Element count/width | API constants, relay buffers, driver loops, RDL vectors, Chisel constants |
| Register layout/instruction bits | RDL, generated SV/Scala/Python, driver literals, Renode register test |
| Local ioctl ABI | extension, host/guest driver, relay |
| Remote wire ABI | `remote_api.h`, C++ backend, relay |
| MMIO/platform identity | `platform.repl`, `tensor_soc.dts`, driver compatible/resource size |
| One synchronous device | Python module, guard, allocator, tests |

The [development workflow](../workflows/development.md) maps these contracts to rebuild commands, and the [source map](../source-map.md) distinguishes canonical sources from checked-in generated artifacts.

## Risks and limitations

- Remote traffic has no authentication or encryption; use it only in a trusted development environment.
- Remote failures collapse guest ioctl detail to a generic nonzero status.
- Checked-in guest images, DTB, relay, kernel module, and Verilated library can drift from source.
- Generated register-map files can drift from RDL; a complete canonical regeneration command is not documented.
- `renode/verilator/build.sh` generates Chisel RTL only if it is absent, so source edits can leave stale generated RTL.
- Expanding beyond four lanes is an ABI, protocol, register-map, driver, RTL, and test migration—not a single constant change.