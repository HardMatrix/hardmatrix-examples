// ops.cpp — All required PrivateUse1 infrastructure operators.
// Since our allocator is malloc-based (host memory), we can delegate most ops
// directly to the native CPU implementations via at::from_blob or at::native::*.
// Based on PyTorch's OpenReg reference:
//   pytorch/test/cpp_extensions/open_registration_extension

#include <ATen/ATen.h>
#include <ATen/EmptyTensor.h>
#include <ATen/native/CPUFallback.h>
#include <ATen/ops/_local_scalar_dense_native.h>
#include <ATen/ops/_reshape_alias_native.h>
#include <ATen/ops/as_strided_cpu_dispatch.h>
#include <ATen/ops/copy_native.h>
#include <ATen/ops/resize_native.h>
#include <ATen/ops/set_cpu_dispatch.h>
#include <ATen/ops/set_native.h>
#include <ATen/ops/view_native.h>
#include <torch/library.h>

using namespace at;

// ---------- empty.memory_format ----------
static Tensor wrapper_empty_memory_format(
    IntArrayRef size,
    std::optional<ScalarType> dtype_opt,
    std::optional<Layout> layout_opt,
    std::optional<Device> device_opt,
    std::optional<bool> pin_memory_opt,
    std::optional<MemoryFormat> memory_format_opt)
{
  auto device = c10::device_or_default(device_opt);
  auto dtype = c10::dtype_or_default(dtype_opt);
  TORCH_CHECK(device.is_privateuseone());
  auto allocator = c10::GetAllocator(c10::DeviceType::PrivateUse1);
  constexpr c10::DispatchKeySet pu1_dks(c10::DispatchKey::PrivateUse1);
  return at::detail::empty_generic(size, allocator, pu1_dks, dtype, memory_format_opt);
}

// ---------- empty_strided ----------
static Tensor wrapper_empty_strided(
    IntArrayRef size,
    IntArrayRef stride,
    std::optional<ScalarType> dtype_opt,
    std::optional<Layout> layout_opt,
    std::optional<Device> device_opt,
    std::optional<bool> pin_memory_opt)
{
  auto device = c10::device_or_default(device_opt);
  auto dtype = c10::dtype_or_default(dtype_opt);
  TORCH_CHECK(device.is_privateuseone());
  auto allocator = c10::GetAllocator(c10::DeviceType::PrivateUse1);
  constexpr c10::DispatchKeySet pu1_dks(c10::DispatchKey::PrivateUse1);
  return at::detail::empty_strided_generic(size, stride, allocator, pu1_dks, dtype);
}

// ---------- as_strided ----------
static Tensor wrapper_as_strided(
    const Tensor& self,
    c10::SymIntArrayRef size,
    c10::SymIntArrayRef stride,
    std::optional<c10::SymInt> storage_offset)
{
  // Memory is malloc-backed, so CPU as_strided works directly
  return at::cpu::as_strided_symint(self, size, stride, storage_offset);
}

// ---------- view ----------
static Tensor wrapper_view(const Tensor& self, c10::SymIntArrayRef size) {
  return at::native::view(self, C10_AS_INTARRAYREF_SLOW(size));
}

// ---------- _reshape_alias ----------
static Tensor wrapper_reshape_alias(
    const Tensor& self,
    c10::SymIntArrayRef size,
    c10::SymIntArrayRef stride)
{
  return at::native::_reshape_alias(
      self, C10_AS_INTARRAYREF_SLOW(size), C10_AS_INTARRAYREF_SLOW(stride));
}

// ---------- resize_ ----------
static const Tensor& wrapper_resize_(
    const Tensor& self,
    c10::SymIntArrayRef size,
    std::optional<MemoryFormat> memory_format)
{
  return at::native::resize_(self, C10_AS_INTARRAYREF_SLOW(size), memory_format);
}

// ---------- _copy_from ----------
// Uses at::from_blob to reinterpret malloc memory as CPU tensors, then native copy.
static Tensor wrapper_copy_from(
    const Tensor& self,
    const Tensor& dst,
    bool non_blocking)
{
  TORCH_CHECK(self.defined(), "_copy_from: source not defined");
  TORCH_CHECK(dst.defined(), "_copy_from: destination not defined");

  if (self.device() == dst.device()) {
    // Device→Device: reinterpret both as CPU
    auto dst_cpu = at::from_blob(dst.data_ptr(), dst.sizes(), dst.strides(),
                                 dst.options().device(kCPU));
    auto self_cpu = at::from_blob(self.data_ptr(), self.sizes(), self.strides(),
                                  self.options().device(kCPU));
    at::native::copy_(const_cast<Tensor&>(dst_cpu), self_cpu, non_blocking);
  } else if (self.is_cpu()) {
    // CPU→Device: reinterpret dst as CPU, copy from self
    auto dst_cpu = at::from_blob(dst.data_ptr(), dst.sizes(), dst.strides(),
                                 dst.options().device(kCPU));
    at::native::copy_(const_cast<Tensor&>(dst_cpu), self, non_blocking);
  } else {
    // Device→CPU: reinterpret self as CPU, copy into dst
    auto self_cpu = at::from_blob(self.data_ptr(), self.sizes(), self.strides(),
                                  self.options().device(kCPU));
    at::native::copy_(const_cast<Tensor&>(dst), self_cpu, non_blocking);
  }
  return dst;
}

// ---------- _copy_from_and_resize ----------
static Tensor wrapper_copy_from_and_resize(
    const Tensor& self,
    const Tensor& dst)
{
  at::native::resize_(dst, self.sizes(), std::nullopt);
  return at::native::copy_(const_cast<Tensor&>(dst), self, false);
}

// ---------- _local_scalar_dense ----------
static Scalar wrapper_local_scalar_dense(const Tensor& self) {
  // Malloc memory is directly CPU-accessible
  return at::native::_local_scalar_dense_cpu(self);
}

// ---------- set_.source_Tensor ----------
static Tensor& wrapper_set_source_Tensor(Tensor& self, const Tensor& source) {
  return at::native::set_tensor_(self, source);
}

// ---------- set_.source_Storage ----------
static Tensor& wrapper_set_source_Storage(Tensor& self, Storage source) {
  return at::native::set_(self, source);
}

// ---------- set_.source_Storage_storage_offset ----------
static Tensor& wrapper_set_source_Storage_offset(
    Tensor& result,
    Storage storage,
    int64_t storage_offset,
    IntArrayRef size,
    IntArrayRef stride)
{
  return at::cpu::set_(result, storage, storage_offset, size, stride);
}

// ---------- _has_compatible_shallow_copy_type ----------
static bool wrapper_has_compatible_shallow_copy_type(
    const Tensor& self, const Tensor& other)
{
  return self.device() == other.device() && self.layout() == other.layout();
}

// ---------- fill_.Scalar ----------
static Tensor& wrapper_fill_scalar(Tensor& self, const Scalar& value) {
  auto self_cpu = at::from_blob(self.data_ptr(), self.sizes(), self.strides(),
                                self.options().device(kCPU));
  self_cpu.fill_(value);
  return self;
}

// ---------- zero_ ----------
static Tensor& wrapper_zero(Tensor& self) {
  auto self_cpu = at::from_blob(self.data_ptr(), self.sizes(), self.strides(),
                                self.options().device(kCPU));
  self_cpu.zero_();
  return self;
}

// ---------- copy_ ----------
static Tensor& wrapper_copy(Tensor& self, const Tensor& src, bool non_blocking) {
  if (src.device().type() == c10::DeviceType::PrivateUse1) {
    auto src_cpu = at::from_blob(src.data_ptr(), src.sizes(), src.strides(),
                                 src.options().device(kCPU));
    auto self_cpu = at::from_blob(self.data_ptr(), self.sizes(), self.strides(),
                                  self.options().device(kCPU));
    at::native::copy_(self_cpu, src_cpu, non_blocking);
  } else {
    auto self_cpu = at::from_blob(self.data_ptr(), self.sizes(), self.strides(),
                                  self.options().device(kCPU));
    at::native::copy_(self_cpu, src, non_blocking);
  }
  return self;
}

// ===== Registration =====

TORCH_LIBRARY_IMPL(aten, PrivateUse1, m) {
  // Required infrastructure (12 ops from OpenReg spec)
  m.impl("empty.memory_format", wrapper_empty_memory_format);
  m.impl("empty_strided", wrapper_empty_strided);
  m.impl("as_strided", wrapper_as_strided);
  m.impl("view", wrapper_view);
  m.impl("_reshape_alias", wrapper_reshape_alias);
  m.impl("resize_", wrapper_resize_);
  m.impl("_copy_from", wrapper_copy_from);
  m.impl("_copy_from_and_resize", wrapper_copy_from_and_resize);
  m.impl("_local_scalar_dense", wrapper_local_scalar_dense);
  m.impl("_has_compatible_shallow_copy_type", wrapper_has_compatible_shallow_copy_type);
  m.impl("set_.source_Tensor", wrapper_set_source_Tensor);
  m.impl("set_.source_Storage", wrapper_set_source_Storage);
  m.impl("set_.source_Storage_storage_offset", wrapper_set_source_Storage_offset);

  // Common ops (avoid fallback overhead)
  m.impl("fill_.Scalar", wrapper_fill_scalar);
  m.impl("zero_", wrapper_zero);
  m.impl("copy_", wrapper_copy);
}

// ===== CPU Fallback =====
// Use PyTorch's built-in cpu_fallback for all unregistered ops.
static void pu1_cpu_fallback(const c10::OperatorHandle& op, torch::jit::Stack* stack) {
  at::native::cpu_fallback(op, stack);
}

TORCH_LIBRARY_IMPL(_, PrivateUse1, m) {
  m.fallback(torch::CppFunction::makeFromBoxedFunction<&pu1_cpu_fallback>());
}
