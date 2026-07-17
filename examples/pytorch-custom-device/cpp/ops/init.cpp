// Backend initialization: DeviceGuard + PrivateUse1 name registration.
// The static objects in allocator.cpp perform allocator registration at load time.
#include <torch/extension.h>
#include <c10/core/impl/DeviceGuardImplInterface.h>
#include "backend.h"

namespace {

void check_device(c10::Device device) {
  TORCH_CHECK(device.type() == c10::DeviceType::PrivateUse1,
              "expected a PrivateUse1 device, got ", device);
  TORCH_CHECK(device.index() == -1 || device.index() == 0,
              "PrivateUse1 exposes only device index 0, got ", device.index());
}

struct PrivateUse1Guard final : public c10::impl::DeviceGuardImplInterface {
  c10::DeviceType type() const override {
    return c10::DeviceType::PrivateUse1;
  }
  c10::Device exchangeDevice(c10::Device device) const override {
    check_device(device);
    return c10::Device(c10::DeviceType::PrivateUse1, 0);
  }
  c10::Device getDevice() const override {
    return c10::Device(c10::DeviceType::PrivateUse1, 0);
  }
  void setDevice(c10::Device device) const override { check_device(device); }
  void uncheckedSetDevice(c10::Device) const noexcept override {}
  c10::Stream getStream(c10::Device) const noexcept override {
    return c10::Stream(c10::Stream::DEFAULT,
                       c10::Device(c10::DeviceType::PrivateUse1, 0));
  }
  c10::Stream getDefaultStream(c10::Device) const override {
    return c10::Stream(c10::Stream::DEFAULT,
                       c10::Device(c10::DeviceType::PrivateUse1, 0));
  }
  c10::Stream exchangeStream(c10::Stream) const noexcept override {
    return c10::Stream(c10::Stream::DEFAULT,
                       c10::Device(c10::DeviceType::PrivateUse1, 0));
  }
  c10::DeviceIndex deviceCount() const noexcept override { return 1; }
};

C10_REGISTER_GUARD_IMPL(PrivateUse1, PrivateUse1Guard);

} // anonymous namespace

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
  c10::register_privateuse1_backend("privateuseone");
  m.def("backend_is_available", []() { return get_backend().is_available(); });
}
