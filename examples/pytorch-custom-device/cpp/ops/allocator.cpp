#include "allocator.h"
#include <c10/core/Allocator.h>

static TensorAllocator g_tensor_allocator;

// Register our allocator for PrivateUse1 at load time.
struct TensorAllocatorRegistrar {
  TensorAllocatorRegistrar() {
    c10::SetAllocator(c10::DeviceType::PrivateUse1, &g_tensor_allocator);
  }
};
static TensorAllocatorRegistrar _alloc_registrar;

