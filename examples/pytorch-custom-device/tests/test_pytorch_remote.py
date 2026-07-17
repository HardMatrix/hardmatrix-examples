"""End-to-end PrivateUse1 tests through Renode and the RTL accelerator."""

from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import time

import pytest
import torch


os.environ.setdefault("TENSOR_BACKEND", "remote")
os.environ.setdefault("TENSOR_REMOTE_ADDR", "localhost:9001")

import mydev  # noqa: E402,F401 - environment selects the backend at import time


DEVICE = "privateuseone"
REPO_ROOT = Path(__file__).resolve().parents[1]
UART_LOG = REPO_ROOT / "out" / "tensor_soc_uart0.log"
RENODE_PROCESS_LOG = REPO_ROOT / "out" / "renode-process.log"


def _tail_file(path: Path, lines: int = 40) -> str:
    if not path.exists():
        return f"{path} does not exist"
    return "\n".join(path.read_text(errors="ignore").splitlines()[-lines:])


def _log_cursor(path: Path) -> tuple[int | None, int]:
    if not path.exists():
        return (None, 0)
    stat = path.stat()
    return (stat.st_ino, stat.st_size)


def _parse_host(address: str) -> str:
    if address.startswith("["):
        end = address.find("]")
        return address[1:end] if end != -1 else address
    index = address.rfind(":")
    return address if index == -1 else address[:index]


def _is_local_remote_target() -> bool:
    address = os.environ.get("TENSOR_REMOTE_ADDR", "localhost:9001")
    return _parse_host(address) in ("localhost", "127.0.0.1", "::1")


def _wait_for_relay_ready(
    timeout_s: int,
    proc: subprocess.Popen,
    renode_log: Path,
    uart_inode: int | None,
    uart_offset: int,
) -> None:
    deadline = time.monotonic() + timeout_s
    marker = b"relay: READY sent, entering main loop"
    carry = b""

    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(
                f"Renode exited before relay readiness (rc={proc.returncode})\n"
                f"UART tail:\n{_tail_file(UART_LOG)}\n"
                f"Renode tail:\n{_tail_file(renode_log)}"
            )

        if UART_LOG.exists():
            stat = UART_LOG.stat()
            if uart_inode is None or stat.st_ino != uart_inode or stat.st_size < uart_offset:
                uart_inode = stat.st_ino
                uart_offset = 0
                carry = b""

            with UART_LOG.open("rb") as stream:
                stream.seek(uart_offset)
                chunk = stream.read()
                uart_offset = stream.tell()

            combined = carry + chunk
            if marker in combined:
                return
            carry = combined[-(len(marker) - 1) :]

        time.sleep(1)

    raise RuntimeError(
        f"Timed out waiting for relay readiness\n"
        f"UART tail:\n{_tail_file(UART_LOG)}\n"
        f"Renode tail:\n{_tail_file(renode_log)}"
    )


def _stop_renode(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    if proc.stdin is not None:
        proc.stdin.write("quit\n")
        proc.stdin.flush()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


@pytest.fixture(scope="session", autouse=True)
def ensure_remote_environment():
    proc = None
    log_file = None
    try:
        autostart = os.environ.get("TENSOR_REMOTE_AUTOSTART", "1").lower() not in (
            "0",
            "false",
            "no",
        )
        if autostart and _is_local_remote_target():
            xdg_home = REPO_ROOT / ".renode-xdg"
            (REPO_ROOT / "out").mkdir(parents=True, exist_ok=True)
            (xdg_home / "renode").mkdir(parents=True, exist_ok=True)
            (xdg_home / "renode" / "config").touch()

            log_file = RENODE_PROCESS_LOG.open("w")
            environment = os.environ.copy()
            environment["XDG_CONFIG_HOME"] = str(xdg_home)
            uart_inode, uart_offset = _log_cursor(UART_LOG)
            proc = subprocess.Popen(
                [
                    "renode",
                    "--disable-xwt",
                    "--console",
                    "-e",
                    "include @renode/resc/boot_headless.resc",
                ],
                cwd=REPO_ROOT,
                env=environment,
                stdin=subprocess.PIPE,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True,
            )
            _wait_for_relay_ready(
                int(os.environ.get("TENSOR_REMOTE_READY_TIMEOUT_S", "600")),
                proc,
                RENODE_PROCESS_LOG,
                uart_inode,
                uart_offset,
            )

        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if torch.privateuseone.is_available():
                break
            time.sleep(0.5)
        else:
            raise RuntimeError(f"remote backend unavailable\n{_tail_file(UART_LOG)}")

        yield
    finally:
        _stop_renode(proc)
        if log_file is not None:
            log_file.close()


class TestRemoteIntegerOps:
    def test_add(self):
        a = torch.tensor([1, 2, 3, 4], dtype=torch.int32, device=DEVICE)
        b = torch.tensor([10, 20, 30, 40], dtype=torch.int32, device=DEVICE)
        result = a + b

        assert result.cpu().tolist() == [11, 22, 33, 44]
        assert result.device.type == DEVICE

    def test_sub(self):
        a = torch.tensor([10, 20, 30, 40], dtype=torch.int32, device=DEVICE)
        b = torch.tensor([1, 2, 3, 4], dtype=torch.int32, device=DEVICE)

        assert (a - b).cpu().tolist() == [9, 18, 27, 36]

    def test_empty(self):
        a = torch.empty(0, dtype=torch.int32, device=DEVICE)
        assert (a + a).shape == (0,)

    def test_concurrent_submissions(self):
        def add_value(value: int) -> list[int]:
            a = torch.tensor([value] * 4, dtype=torch.int32, device=DEVICE)
            b = torch.ones(4, dtype=torch.int32, device=DEVICE)
            return (a + b).cpu().tolist()

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(add_value, range(4)))

        assert results == [[value + 1] * 4 for value in range(4)]


class TestRemoteErrors:
    def test_float32_rejected(self):
        a = torch.ones(4, device=DEVICE)
        with pytest.raises(RuntimeError, match="int32 only"):
            _ = a + a

    def test_too_many_elements(self):
        a = torch.ones(5, dtype=torch.int32, device=DEVICE)
        with pytest.raises(RuntimeError, match="max 4 elements"):
            _ = a + a

    def test_different_shapes_rejected(self):
        a = torch.ones((2, 2), dtype=torch.int32, device=DEVICE)
        b = torch.ones(4, dtype=torch.int32, device=DEVICE)
        with pytest.raises(RuntimeError, match="same shape"):
            _ = a + b


class TestRemoteTensorInfrastructure:
    def test_copy_roundtrip(self):
        cpu_tensor = torch.tensor([1.0, 2.0, 3.0, 4.0])
        assert cpu_tensor.to(DEVICE).cpu().tolist() == cpu_tensor.tolist()

    def test_scalar(self):
        assert torch.ones(1, device=DEVICE).item() == 1.0
