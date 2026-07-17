#include <ATen/ATen.h>
#include <torch/library.h>
#include <c10/util/Exception.h>

#include "backend.h"
#include "../../include/api.h"

using namespace at;

static Tensor tensor_add_impl(const Tensor& a, const Tensor& b, const Scalar& alpha)
{
  TORCH_CHECK(a.device().type() == c10::DeviceType::PrivateUse1, "add: a not on PrivateUse1");
  TORCH_CHECK(b.device().type() == c10::DeviceType::PrivateUse1, "add: b not on PrivateUse1");
  TORCH_CHECK(a.scalar_type() == kInt && b.scalar_type() == kInt, "add: int32 only");
  TORCH_CHECK(a.is_contiguous() && b.is_contiguous(), "add: contiguous only");
  TORCH_CHECK(a.sizes() == b.sizes(), "add: operands must have the same shape; broadcasting is not supported");
  TORCH_CHECK(alpha.equal(1), "add: alpha != 1 not supported");
  TORCH_CHECK(a.numel() <= TENSOR_MAX_ELEMENTS, "add: max ", TENSOR_MAX_ELEMENTS, " elements");

  auto out = at::empty_like(a);
  if (a.numel() == 0) {
    return out;
  }

  int rc = get_backend().submit(
      TENSOR_OP_VADD_I32,
      (uint32_t)a.numel(),
      sizeof(int32_t),
      a.data_ptr<int32_t>(),
      b.data_ptr<int32_t>(),
      out.data_ptr<int32_t>());
  TORCH_CHECK(rc == 0, "add: backend submit failed, rc=", rc);

  return out;
}

static Tensor tensor_add_wrapper(const Tensor& self, const Tensor& other, const Scalar& alpha)
{
  return tensor_add_impl(self, other, alpha);
}

TORCH_LIBRARY_IMPL(aten, PrivateUse1, m) {
  m.impl("add.Tensor", &tensor_add_wrapper);
}
