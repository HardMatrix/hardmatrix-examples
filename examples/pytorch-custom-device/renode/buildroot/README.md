# Buildroot guest image

Run all commands from the `pytorch-custom-device` example root.

## Prerequisites

- A Buildroot checkout and its documented host build dependencies
- Renode, Verilator, and the Renode IntegrationLibrary when running the final
  end-to-end test

Set `BUILDROOT_DIR` to the checkout path in every command below.

The guest artifacts use this pinned Buildroot revision:

```sh
git clone https://github.com/buildroot/buildroot.git /path/to/buildroot
git -C /path/to/buildroot checkout 49d1ea93f7d3ad8f7113cea39be4c39b4d6faca6
```

## First build

The first Buildroot pass creates the cross-toolchain and kernel build tree.
Rebuild afterward to add the relay and kernel module to the guest image:

```sh
BUILDROOT_DIR=/path/to/buildroot ./renode/buildroot/build.sh full
BUILDROOT_DIR=/path/to/buildroot make relay driver-riscv image
```

## Rebuild after guest changes

```sh
BUILDROOT_DIR=/path/to/buildroot make relay driver-riscv image
```

## Test the rebuilt image

```sh
make test-remote
```
