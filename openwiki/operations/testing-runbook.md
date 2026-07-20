---
type: Operations Runbook
title: Testing and Operations Runbook
description: Verification matrix, prerequisites, privileged procedures, failure triage, and current automation status for hardmatrix-examples.
tags: [testing, operations, cocotb, kernel-module]
---

# Testing and operations runbook

## Current automation status

There is no tracked GitHub Actions regression at HEAD. Commit `20a809c` added a self-hosted workflow for FCS, accelerator RTL, mock-driver, and remote Renode phases; commit `23d937c` removed it. A `.github/` directory may appear as untracked local content, but it is not part of the current source baseline. Treat the commands below and the [development workflow](../workflows/development.md) as authoritative.

## Test matrix

| Scope | Command/location | What it proves | Main dependencies |
|---|---|---|---|
| FCS simulation | Root: FuseSoC `--target test` | Packet CRC/FCS, `tlast`, random backpressure | uv, FuseSoC, Verilator, cocotb |
| FCS lint | Root: FuseSoC `--target lint` | Verilator structural/style checks | uv, FuseSoC, Verilator |
| Vector accelerator RTL | PyTorch example: `make test-hw` | AXI4-Lite/register behavior and vector operations | uv, JDK/Mill, FuseSoC, Verilator, cocotb |
| Optional RDL socket | FuseSoC `--target test_socket` | Socket-based generated-register integration | Same as RTL test; not in `make test-hw` |
| PyTorch mock | `make test-mock` after module load | PrivateUse1 registration, operators, local ioctl, mock driver | C++ toolchain, PyTorch env, matching kernel headers, root |
| PyTorch remote | `make test-remote` | Host protocol → Renode guest → ioctl → Verilated hardware | Renode, IntegrationLibrary, checked-in guest artifacts |
| Direct Renode register smoke | `vam_regtest.resc` | Platform/AXI/Verilated register behavior without Linux | Renode, Verilated library |

The [FCS concept](../domain/axis-ethernet-fcs.md) describes its expected bytes; the [PyTorch custom device](../domain/pytorch-custom-device.md) defines the cross-layer semantics those tests protect.

## Safe mock-driver procedure

From `examples/pytorch-custom-device`:

```sh
make -C cpp/driver
sudo rmmod tensor 2>/dev/null || true
sudo insmod cpp/driver/tensor.ko \
  mock=1 debug=0 mock_autocreate=1 device_mode=0666
make test-mock
sudo rmmod tensor
```

Operational rules:

- Use a kernel whose matching headers are installed.
- Use `device_mode=0666` only on a disposable development host. The module's default is `0660`; persistent systems should use group ownership or a udev rule.
- Always unload the module after tests, including after failures.
- The module creates `/dev/tensor0`; if it is absent, inspect module load errors and platform-device creation before debugging PyTorch.
- The local backend is cached for the process lifetime. Restart pytest/Python after changing `TENSOR_BACKEND` or replacing the loaded driver.

## Remote test procedure

```sh
make test-remote
```

This rebuilds the Verilated library before pytest. For local targets, `tests/test_pytorch_remote.py` can autostart Renode; `TENSOR_REMOTE_AUTOSTART` controls that behavior and `TENSOR_REMOTE_READY_TIMEOUT_S` controls guest readiness waiting. The backend address defaults to `localhost:9001`; `TENSOR_REMOTE_SOCKET_TIMEOUT_MS` defaults to 10000 and accepts 1–600000 ms.

After guest/platform source changes, first run:

```sh
BUILDROOT_DIR=/path/to/buildroot make renode-build
```

Useful logs from the historical CI and current test flow live under `examples/pytorch-custom-device/out/`, including UART, Renode process, and monitor logs.

## Failure triage

### FuseSoC cannot resolve a core

- For FCS, ensure both `--cores-root=examples/axis-eth-fcs` and `--cores-root=shared/rtl/axis-if` are present.
- For the vector machine, run `./fusesoc_setup.sh` from the PyTorch example before invoking its local `.venv/bin/fusesoc`.

### CRC mismatch or premature packet end

- Verify the reflected polynomial, final complement, and little-endian FCS byte order.
- Ensure state changes occur only on `tvalid && tready`.
- Confirm payload `tlast` is suppressed and final FCS `tlast` is asserted.

### `mydev` is unavailable

- Confirm `uv sync` and editable extension installation completed.
- For local mode, verify `/dev/tensor0` is readable/writable.
- For remote mode, set `TENSOR_BACKEND=remote` before importing/first using the backend and verify TCP reachability.

### Remote handshake/connect failure

- Verify the address syntax (`host:port`, or `[IPv6]:port`) and port 9001 mapping.
- Check that guest init loaded `tensor.ko`, configured UART1, and executed the relay.
- Inspect `out/tensor_soc_uart0.log` and Renode logs.
- A malformed request or transport failure can terminate the single relay connection; restart the scenario.

### Hardware timeout/status failure

- Cross-check API opcodes and register instruction encoding.
- Ensure status was cleared before instruction submission.
- Use `renode/resc/vam_regtest.resc` to separate RTL/platform failures from Linux/relay/PyTorch failures.
- Remember that the remote response currently loses detailed guest errno and hardware status.

## Coverage cautions

FCS tests do not cover reset during packet/FCS emission or source-valid gaps. `make test-hw` omits `test_socket`. CPU fallback means PyTorch tests may pass operations that have no accelerator kernel. For changes to ABI, register map, platform identity, or generated artifacts, consult [integration points](../integrations/interfaces.md) and test every affected layer rather than relying on one happy-path suite.