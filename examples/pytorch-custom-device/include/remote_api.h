#pragma once

// Remote ioctl proxy protocol — used between host C++ backend and Renode relay.
// Wire format: all fields little-endian, packed.

#include <stdint.h>

#define REMOTE_MAGIC 0x54454E53  // "TENS" in little-endian
#define REMOTE_PROTOCOL_VERSION 2

// Host → Relay: header (32 bytes) + a_data + b_data
struct remote_submit {
    uint32_t magic;       // REMOTE_MAGIC
    uint32_t version;     // REMOTE_PROTOCOL_VERSION
    uint32_t op;          // tensor_op enum value
    uint32_t len;         // element count
    uint32_t elem_bytes;  // 4
    uint32_t reserved[3]; // pad to 32 bytes
} __attribute__((packed));

// Relay → Host: header (16 bytes) + out_data
struct remote_response {
    uint32_t magic;       // REMOTE_MAGIC
    uint32_t version;     // REMOTE_PROTOCOL_VERSION
    uint32_t status;      // 0 = OK, nonzero = error
    uint32_t len;         // element count in result
} __attribute__((packed));
