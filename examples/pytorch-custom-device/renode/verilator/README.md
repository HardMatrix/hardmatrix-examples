# Renode Verilator adapter

Run all commands from the `pytorch-custom-device` example root.

## Prerequisites

- Verilator
- Renode IntegrationLibrary, normally installed at
  `/opt/renode/plugins/IntegrationLibrary`

## Build

Use the default IntegrationLibrary location:

```sh
make verilator-lib
```

Override the location when Renode is installed elsewhere:

```sh
RENODE_INTEGRATION=/path/to/IntegrationLibrary make verilator-lib
```

Run the end-to-end test after rebuilding:

```sh
make test-remote
```
