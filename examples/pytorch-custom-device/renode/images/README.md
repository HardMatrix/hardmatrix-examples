# Renode guest artifacts

The checked-in `fw_jump.bin`, `Image`, and `tensor_soc.dtb` files are used by:

```sh
make test-remote
```

Run the command from the `pytorch-custom-device` example root.

The artifacts are generated reproducibly from Buildroot revision
`49d1ea93f7d3ad8f7113cea39be4c39b4d6faca6`, Linux 6.18.7, and OpenSBI 1.6.
Verify them from this directory with:

```sh
sha256sum -c SHA256SUMS
```

To replace these artifacts after guest software or platform changes, follow
[`../buildroot/README.md`](../buildroot/README.md).
