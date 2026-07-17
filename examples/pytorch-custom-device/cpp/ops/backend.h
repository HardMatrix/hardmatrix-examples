#pragma once
#include <cstdint>
#include <cstddef>

class HardwareBackend {
public:
    virtual ~HardwareBackend() = default;
    virtual bool is_available() noexcept = 0;
    // Submit a tensor operation. Returns 0 on success, nonzero on error.
    virtual int submit(uint32_t op, uint32_t len, uint32_t elem_bytes,
                       const void* a_data, const void* b_data,
                       void* out_data) = 0;
};

// Returns a singleton backend selected by TENSOR_BACKEND env var:
//   "ioctl"  (default) — local /dev/tensor0
//   "remote" — TCP to TENSOR_REMOTE_ADDR (default localhost:9001)
HardwareBackend& get_backend();
