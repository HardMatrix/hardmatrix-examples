from . import _C


def is_available() -> bool:
    return bool(_C.backend_is_available())


def device_count() -> int:
    return int(is_available())


def current_device() -> int:
    return 0


def set_device(device: int) -> None:
    index = int(device)
    if index != 0:
        raise ValueError(f"privateuseone has one device; invalid index {index}")


def synchronize(device: int | None = None) -> None:
    if device is not None:
        set_device(device)
