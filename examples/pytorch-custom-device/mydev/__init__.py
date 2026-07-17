import torch
from . import _C  # noqa: F401
from . import _device

# Importing the extension runs its allocator, dispatcher, and device-guard
# registrations. Expose the matching Python device module once per process.
if not hasattr(torch, "privateuseone"):
    torch._register_device_module("privateuseone", _device)
