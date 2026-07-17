#pragma once
#include <c10/core/Allocator.h>
#include <c10/core/Device.h>
#include <c10/util/Exception.h>
#include <cstdlib>
#include <cstring>  // for std::memcpy

struct TensorAllocator final : public c10::Allocator {
  // NOTE: must NOT be const; matches c10::Allocator::allocate(size_t)
  c10::DataPtr allocate(size_t nbytes) override {
    void* p = (nbytes ? std::malloc(nbytes) : nullptr);
    TORCH_CHECK(nbytes == 0 || p != nullptr,
                "tensor: malloc failed for ", nbytes, " bytes");
    return {
      p,
      p,
      &TensorAllocator::raw_delete,
      c10::Device(c10::DeviceType::PrivateUse1, 0)
    };
  }

  static void raw_delete(void* p) {
    if (p) std::free(p);
  }

  c10::DeleterFnPtr raw_deleter() const override {
    return &TensorAllocator::raw_delete;
  }

  // Optional but useful; matches the virtual in Allocator.h
  void copy_data(void* dest, const void* src, std::size_t count) const override {
    if (count == 0) return;
    std::memcpy(dest, src, count);
  }
};

