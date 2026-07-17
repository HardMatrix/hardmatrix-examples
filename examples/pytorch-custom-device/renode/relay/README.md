# Guest relay

Run all commands from the `pytorch-custom-device` example root.

## Prerequisites

- Complete the first Buildroot build documented in
  [`../buildroot/README.md`](../buildroot/README.md) so its RISC-V toolchain is
  available.

## Build

```sh
BUILDROOT_DIR=/path/to/buildroot make -C renode/relay
```

## Install into the guest image

```sh
BUILDROOT_DIR=/path/to/buildroot make relay image
```

Run `make test-remote` after rebuilding the image.
