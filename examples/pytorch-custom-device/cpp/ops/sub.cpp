#include <ATen/ATen.h>
#include <torch/library.h>
#include <c10/util/Exception.h>

#include "backend.h"
#include "../../include/api.h"

using namespace at;

static Tensor tensor_sub_impl(const Tensor& a, const Tensor& b, const Scalar& alpha)
{
  TORCH_CHECK(a.device().type() == c10::DeviceType::PrivateUse1, "sub: a not on PrivateUse1");
  TORCH_CHECK(b.device().type() == c10::DeviceType::PrivateUse1, "sub: b not on PrivateUse1");
  TORCH_CHECK(a.scalar_type() == kInt && b.scalar_type() == kInt, "sub: int32 only");
  TORCH_CHECK(a.is_contiguous() && b.is_contiguous(), "sub: contiguous only");
  TORCH_CHECK(a.sizes() == b.sizes(), "sub: operands must have the same shape; broadcasting is not supported");
  TORCH_CHECK(alpha.equal(1), "sub: alpha != 1 not supported");
  TORCH_CHECK(a.numel() <= TENSOR_MAX_ELEMENTS, "sub: max ", TENSOR_MAX_ELEMENTS, " elements");

  auto out = at::empty_like(a);
  if (a.numel() == 0) {
    return out;
  }

  int rc = get_backend().submit(
      TENSOR_OP_VSUB_I32,
      (uint32_t)a.numel(),
      sizeof(int32_t),
      a.data_ptr<int32_t>(),
      b.data_ptr<int32_t>(),
      out.data_ptr<int32_t>());
  TORCH_CHECK(rc == 0, "sub: backend submit failed, rc=", rc);

  return out;
}

static Tensor tensor_sub_wrapper(const Tensor& self, const Tensor& other, const Scalar& alpha)
{
  return tensor_sub_impl(self, other, alpha);
}

TORCH_LIBRARY_IMPL(aten, PrivateUse1, m) {
  m.impl("sub.Tensor", &tensor_sub_wrapper);
}
