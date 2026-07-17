# Renode development

Run all commands from the `pytorch-custom-device` example root.

## Prerequisites

- Renode
- Verilator
- Renode IntegrationLibrary, normally installed with Renode
- Complete `uv sync` in the example root

## Run the end-to-end test

The checked-in guest artifacts are sufficient for the standard test:

```sh
make test-remote
```

## Rebuild generated artifacts

Rebuild the Verilator library only:

```sh
make verilator-lib
```

After changing guest software or platform files, use an initialized Buildroot
checkout:

```sh
BUILDROOT_DIR=/path/to/buildroot make renode-build
make test-remote
```

First-time guest-image setup is documented in
[`buildroot/README.md`](buildroot/README.md). Manual Renode commands are in
[`resc/README.md`](resc/README.md).
