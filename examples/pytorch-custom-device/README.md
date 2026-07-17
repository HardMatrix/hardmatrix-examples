# PyTorch custom-device example

This example connects PyTorch's `PrivateUse1` backend to a four-element RTL
integer accelerator. Run the commands below from this directory.

## Prerequisites

- [uv](https://docs.astral.sh/uv/), a C/C++ compiler, and Ninja
- Verilator and a JDK for RTL tests
- Linux kernel headers matching the host kernel for driver tests
- Renode and its IntegrationLibrary for end-to-end tests
- A Buildroot checkout only when rebuilding the guest image

## Setup

```sh
uv sync
```

The lock file uses the CPU-only PyTorch 2.9.x package line.

## RTL tests

```sh
make test-hw
```

## Host mock-driver tests

```sh
make -C cpp/driver
sudo insmod cpp/driver/tensor.ko \
  mock=1 debug=0 mock_autocreate=1 device_mode=0666
make test-mock
sudo rmmod tensor
```

Use mode `0666` only on a disposable development machine. For persistent use,
keep the default `0660` mode and configure an appropriate group or udev rule.

## Renode end-to-end tests

Run against the included guest artifacts:

```sh
make test-remote
```

After changing the guest driver, relay, kernel configuration, or device tree,
rebuild with an existing Buildroot checkout and rerun the test:

```sh
BUILDROOT_DIR=/path/to/buildroot make renode-build
make test-remote
```

For a first-time Buildroot setup, follow
[`renode/buildroot/README.md`](renode/buildroot/README.md).

## Development layout

```text
mydev/                 Python device-module registration
cpp/ops/               PrivateUse1 allocator, operators, and backends
cpp/driver/            Linux platform/misc driver
include/               Shared ioctl and remote protocol ABIs
hw/                    Chisel, generated register map, and cocotb tests
renode/                RISC-V platform, relay, images, and RTL adapter
tests/                 Host mock and end-to-end PyTorch tests
```

Hardware-backed addition and subtraction accept contiguous `torch.int32`
tensors with matching shapes and at most four elements. Broadcasting is not
supported by the hardware path.

## Cleanup

```sh
make clean
```
