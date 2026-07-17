"""PrivateUse1 tests using the local tensor kernel driver's mock backend.

Prerequisite:
    sudo insmod cpp/driver/tensor.ko mock=1 debug=0 mock_autocreate=1 device_mode=0666
"""

from concurrent.futures import ThreadPoolExecutor

import pytest
import torch

import mydev  # noqa: F401 - importing registers the backend


DEVICE = "privateuseone"


@pytest.fixture(autouse=True)
def check_device_available():
    assert torch.privateuseone.is_available(), "load tensor.ko in mock mode first"


class TestTensorInfrastructure:
    def test_empty(self):
        tensor = torch.empty(4, device=DEVICE, dtype=torch.float32)
        assert tensor.device.type == DEVICE
        assert tensor.dtype == torch.float32

    def test_creation_and_fill(self):
        assert torch.ones(4, device=DEVICE).cpu().tolist() == [1.0] * 4
        assert torch.zeros(4, device=DEVICE).cpu().tolist() == [0.0] * 4

        tensor = torch.empty(4, device=DEVICE, dtype=torch.float32)
        tensor.fill_(3.5)
        assert tensor.cpu().tolist() == [3.5] * 4

    def test_copy_paths(self):
        cpu_tensor = torch.tensor([1.0, 2.0, 3.0, 4.0])
        device_tensor = cpu_tensor.to(DEVICE)
        device_copy = device_tensor.to(DEVICE)

        assert device_tensor.cpu().tolist() == cpu_tensor.tolist()
        assert device_copy.cpu().tolist() == cpu_tensor.tolist()

    def test_scalar_and_print(self):
        tensor = torch.ones(1, device=DEVICE)
        assert tensor.item() == 1.0
        assert "privateuseone" in str(tensor)


class TestHardwareIntegerOps:
    def test_add(self):
        a = torch.tensor([1, 2, 3, 4], dtype=torch.int32, device=DEVICE)
        b = torch.tensor([10, 20, 30, 40], dtype=torch.int32, device=DEVICE)
        result = a + b

        assert result.cpu().tolist() == [11, 22, 33, 44]
        assert result.dtype == torch.int32
        assert result.device.type == DEVICE

    def test_sub(self):
        a = torch.tensor([10, 20, 30, 40], dtype=torch.int32, device=DEVICE)
        b = torch.tensor([1, 2, 3, 4], dtype=torch.int32, device=DEVICE)
        result = a - b

        assert result.cpu().tolist() == [9, 18, 27, 36]
        assert result.dtype == torch.int32

    def test_empty(self):
        a = torch.empty(0, dtype=torch.int32, device=DEVICE)
        b = torch.empty(0, dtype=torch.int32, device=DEVICE)
        result = a + b

        assert result.shape == (0,)
        assert result.dtype == torch.int32

    def test_concurrent_submissions(self):
        def add_value(value: int) -> list[int]:
            a = torch.tensor([value] * 4, dtype=torch.int32, device=DEVICE)
            b = torch.ones(4, dtype=torch.int32, device=DEVICE)
            return (a + b).cpu().tolist()

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(add_value, range(4)))

        assert results == [[value + 1] * 4 for value in range(4)]


class TestHardwareOpErrors:
    def test_float32_rejected(self):
        a = torch.ones(4, device=DEVICE)
        with pytest.raises(RuntimeError, match="int32 only"):
            _ = a + a

    def test_alpha_unsupported(self):
        a = torch.ones(4, dtype=torch.int32, device=DEVICE)
        with pytest.raises(RuntimeError, match="alpha != 1"):
            torch.add(a, a, alpha=2)

    def test_too_many_elements(self):
        a = torch.ones(5, dtype=torch.int32, device=DEVICE)
        with pytest.raises(RuntimeError, match="max 4 elements"):
            _ = a + a

    def test_different_shapes_rejected(self):
        a = torch.ones((2, 2), dtype=torch.int32, device=DEVICE)
        b = torch.ones(4, dtype=torch.int32, device=DEVICE)
        with pytest.raises(RuntimeError, match="same shape"):
            _ = a + b

    def test_broadcasting_rejected(self):
        a = torch.ones((2, 1), dtype=torch.int32, device=DEVICE)
        b = torch.ones((1, 2), dtype=torch.int32, device=DEVICE)
        with pytest.raises(RuntimeError, match="broadcasting is not supported"):
            _ = a + b
