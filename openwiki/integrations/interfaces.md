---
type: Integration Reference
title: Integration Points and Interfaces
description: External toolchain dependencies and internal ABI, protocol, bus, and emulator contracts that connect the HardMatrix examples.
tags: [integrations, abi, fusesoc, renode, axi]
---

# Integration points and interfaces

## FuseSoC, Verilator, and cocotb

Both examples package RTL through FuseSoC and simulate with Verilator/cocotb.

- The FCS core depends on `hardmatrix:examples:axis_if:2.0.0` and receives core roots on the command line.
- The Vector Adder Machine core depends on `fusesoc:utils:generators` and `stratum:interfaces:axi4_lite:0.2.0`; `fusesoc_setup.sh` initializes local libraries.
- Chisel generation is a FuseSoC generator backed by Mill.

Shared FCS test support lives in `shared/python/utils/tb_utils`: an AXI-stream driver, handshake monitor, and valid-pattern generators. The shared `axis_if.sv` also carries protocol assertions. These integrations directly support the [FCS domain contract](../domain/axis-ethernet-fcs.md).

## PyTorch extension boundary

`setup.py` builds `mydev._C` from `cpp/ops/*.cpp` with PyTorch's `CppExtension`. Import side effects register allocator, guard, kernels, CPU fallback, and the Python device module. The package targets Python 3.13+ and PyTorch 2.9.x in `pyproject.toml`/lock data.

This is a synchronous, one-device integration. Adding device indices, streams, asynchronous copies, or non-host-visible memory requires coordinated changes beyond the two hardware kernels described in [PyTorch custom device](../domain/pytorch-custom-device.md).

## Ioctl ABI

`include/api.h` is shared by userspace extension code, the Linux driver, and the Renode relay. Version 2 defines `tensor_submit`, including operation, length, element size, three user pointers, timeout, flags, and returned hardware status.

Key constraints are `TENSOR_MAX_ELEMENTS == 4`, `elem_bytes == 4`, reserved flags zero, and opcodes 1/2. Any structure or version change requires rebuilding every consumer and guest artifact. The local backend submits with a 1000 ms timeout; the relay supplies a 5000 ms ioctl timeout.

## Remote wire protocol

`include/remote_api.h` defines a little-endian packed protocol:

```text
Host → relay: 32-byte remote_submit + A bytes + B bytes
Relay → host: 16-byte remote_response + result bytes
```

Both peers validate magic/version/length, and the C++ backend enforces header sizes with static assertions. The relay first sends `READY\n`. A single persistent connection is serialized; transport/protocol exceptions close it and allow a later reconnect.

The protocol has no authentication, authorization, encryption, or message resynchronization. Bind/use it only on trusted development networks. Extending it must update `remote_api.h`, `cpp/ops/backend.cpp`, `renode/relay/relay.c`, and remote tests together.

## AXI4-Lite and register generation

The Vector Adder Machine combines:

- Chisel compute/control sources;
- a SystemRDL register specification;
- generated SystemVerilog register block/wrapper/package;
- generated Scala bundles;
- generated Python register model;
- an AXI4-Lite SystemVerilog interface.

The instruction write is semantically atomic because writing the opcode field triggers execution through `swmod`. Software should not decompose one intended instruction into independently triggering updates. The register map occupies `0x180` bytes and currently uses a nine-bit AXI address path; expanding it requires auditing the Renode adapter's address shadows/casts.

## Renode, Verilator, and guest Linux

`renode/platform.repl` defines a 64-bit RISC-V machine and maps the accelerator at `0x40000000..0x400001ff`. `renode/buildroot/tensor_soc.dts` must mirror CPU, RAM, interrupt, UART, and accelerator configuration; compatible string `acme,tensor-1.0` binds the Linux driver.

`renode/verilator/sim_renode.cpp` adapts Renode IntegrationLibrary's AXI representation to the Verilated top. `.resc` scripts load OpenSBI, Linux, DTB, and the shared library, then expose UART1 over TCP 9001. Guest init mounts pseudo-filesystems, loads the module, configures `/dev/ttyS1`, and replaces itself with the relay.

The [development workflow](../workflows/development.md) explains when to rebuild only the Verilated library versus the complete Buildroot artifact chain; the [testing runbook](../operations/testing-runbook.md) provides isolation tests.

## Synchronization checklist

Before merging a cross-layer change, use the [source map](../source-map.md) and verify:

1. Shared ABI versions and packed sizes agree.
2. Opcodes and lane counts agree from PyTorch through RTL.
3. RDL offsets/fields match generated artifacts and driver literals.
4. Platform and DTS addresses/resource sizes match.
5. Guest images and Verilated libraries were rebuilt when their sources changed.
6. Relevant direct RTL, local mock, and remote tests all pass.