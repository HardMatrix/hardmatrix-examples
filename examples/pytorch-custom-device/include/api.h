#pragma once
#include <linux/ioctl.h>
#include <linux/types.h>

#define TENSOR_IOC_MAGIC 'M'
#define TENSOR_API_VERSION 2
#define TENSOR_MAX_ELEMENTS 4

enum tensor_op {
    TENSOR_OP_VADD_I32 = 1,  // out[i] = a[i] + b[i]
    TENSOR_OP_VSUB_I32 = 2,  // out[i] = a[i] - b[i]
};

struct tensor_submit {
    __u32 version;      // API version (must be TENSOR_API_VERSION)
    __u32 op;           // enum tensor_op
    __u32 len;          // element count (1–TENSOR_MAX_ELEMENTS)
    __u32 elem_bytes;   // must be 4
    __u64 a_ptr;        // user-space pointer to input A
    __u64 b_ptr;        // user-space pointer to input B
    __u64 out_ptr;      // user-space pointer to output
    __u32 timeout_ms;   // 0 => default
    __u32 flags;        // reserved; must be zero
    __u32 status;       // driver returns HW status here
    __u32 reserved;
};

#define TENSOR_IOC_SUBMIT _IOWR(TENSOR_IOC_MAGIC, 1, struct tensor_submit)
#define TENSOR_IOC_RESET  _IO  (TENSOR_IOC_MAGIC, 2)
