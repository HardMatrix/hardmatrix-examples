# Renode scenarios

Run all commands from the `pytorch-custom-device` example root after `uv sync`.

## Automated test

```sh
make test-remote
```

## Manual scenarios

Build the Verilator integration library and create the log directory first:

```sh
make verilator-lib
mkdir -p out
```

Headless Linux boot:

```sh
renode --disable-xwt -e "include @renode/resc/boot_headless.resc"
```

Interactive Linux boot:

```sh
renode --disable-xwt -e "include @renode/resc/boot_interactive.resc"
```

Register-level hardware check without Linux:

```sh
renode --disable-xwt --console -e "include @renode/resc/vam_regtest.resc"
```
