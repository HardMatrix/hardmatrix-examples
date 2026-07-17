// relay.c — Transparent ioctl proxy for Renode Linux
// Reads remote_submit from UART, calls ioctl on /dev/tensor0, sends response back.
// Runs as init (PID 1) via init.sh wrapper.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <stdint.h>
#include <termios.h>

#include "../../include/api.h"
#include "../../include/remote_api.h"

#if __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "The tensor remote protocol currently requires a little-endian target"
#endif

_Static_assert(sizeof(struct remote_submit) == 32, "remote_submit wire size changed");
_Static_assert(sizeof(struct remote_response) == 16, "remote_response wire size changed");

#define UART_PATH "/dev/ttyS1"
#define TENSOR_PATH "/dev/tensor0"
#define MAX_DATA_BYTES (TENSOR_MAX_ELEMENTS * 4)

static int read_all(int fd, void *buf, size_t len)
{
    char *p = (char *)buf;
    while (len > 0) {
        ssize_t n = read(fd, p, len);
        if (n < 0) {
            if (errno == EINTR) continue;
            perror("relay: read");
            return -1;
        }
        if (n == 0) {
            fprintf(stderr, "relay: EOF on read\n");
            return -1;
        }
        p += n;
        len -= (size_t)n;
    }
    return 0;
}

static int write_all(int fd, const void *buf, size_t len)
{
    const char *p = (const char *)buf;
    while (len > 0) {
        ssize_t n = write(fd, p, len);
        if (n < 0) {
            if (errno == EINTR) continue;
            perror("relay: write");
            return -1;
        }
        p += n;
        len -= (size_t)n;
    }
    return 0;
}

static int write_response(int fd, uint32_t status, uint32_t len)
{
    struct remote_response resp;
    memset(&resp, 0, sizeof(resp));
    resp.magic = REMOTE_MAGIC;
    resp.version = REMOTE_PROTOCOL_VERSION;
    resp.status = status;
    resp.len = len;
    return write_all(fd, &resp, sizeof(resp));
}

int main(void)
{
    int uart_fd, tensor_fd;
    struct remote_submit req;
    struct remote_response resp;
    struct tensor_submit ts;
    uint8_t a_buf[MAX_DATA_BYTES];
    uint8_t b_buf[MAX_DATA_BYTES];
    uint8_t out_buf[MAX_DATA_BYTES];
    size_t data_bytes;
    int rc;

    fprintf(stderr, "relay: starting\n");

    // Open UART data channel
    uart_fd = open(UART_PATH, O_RDWR);
    if (uart_fd < 0) {
        perror("relay: open UART");
        return 1;
    }

    // Set raw mode — disable all tty processing for binary transparency
    {
        struct termios tio;
        tcgetattr(uart_fd, &tio);
        cfmakeraw(&tio);
        tio.c_cc[VMIN] = 1;
        tio.c_cc[VTIME] = 0;
        tcsetattr(uart_fd, TCSANOW, &tio);
    }

    // Open tensor device
    tensor_fd = open(TENSOR_PATH, O_RDWR);
    if (tensor_fd < 0) {
        perror("relay: open tensor");
        return 1;
    }

    // Signal host that we're ready
    write_all(uart_fd, "READY\n", 6);
    fprintf(stderr, "relay: READY sent, entering main loop\n");

    for (;;) {
        // 1. Read request header
        if (read_all(uart_fd, &req, sizeof(req)) < 0)
            break;

        if (req.magic != REMOTE_MAGIC) {
            fprintf(stderr, "relay: bad magic 0x%08x\n", req.magic);
            write_response(uart_fd, 1, 0);
            break;
        }

        if (req.version != REMOTE_PROTOCOL_VERSION) {
            fprintf(stderr, "relay: unsupported protocol version %u\n", req.version);
            write_response(uart_fd, 1, 0);
            break;
        }

        if (req.len == 0 || req.len > TENSOR_MAX_ELEMENTS || req.elem_bytes != 4) {
            fprintf(stderr, "relay: invalid len=%u elem_bytes=%u\n",
                    req.len, req.elem_bytes);
            write_response(uart_fd, 1, 0);
            break;
        }

        data_bytes = (size_t)req.len * req.elem_bytes;

        // 2. Read input data
        if (read_all(uart_fd, a_buf, data_bytes) < 0) break;
        if (read_all(uart_fd, b_buf, data_bytes) < 0) break;

        fprintf(stderr, "relay: op=%u len=%u\n", req.op, req.len);

        // 3. Build local tensor_submit and call ioctl
        memset(&ts, 0, sizeof(ts));
        ts.version = TENSOR_API_VERSION;
        ts.op = req.op;
        ts.len = req.len;
        ts.elem_bytes = req.elem_bytes;
        ts.a_ptr = (uint64_t)(uintptr_t)a_buf;
        ts.b_ptr = (uint64_t)(uintptr_t)b_buf;
        ts.out_ptr = (uint64_t)(uintptr_t)out_buf;
        ts.timeout_ms = 5000;

        rc = ioctl(tensor_fd, TENSOR_IOC_SUBMIT, &ts);

        // 4. Send response
        memset(&resp, 0, sizeof(resp));
        resp.magic = REMOTE_MAGIC;
        resp.version = REMOTE_PROTOCOL_VERSION;
        resp.status = (rc == 0) ? 0 : 1;
        resp.len = req.len;

        if (write_all(uart_fd, &resp, sizeof(resp)) < 0) break;

        if (rc == 0) {
            if (write_all(uart_fd, out_buf, data_bytes) < 0) break;
        }

        fprintf(stderr, "relay: done rc=%d status=0x%x\n", rc, ts.status);
    }

    close(tensor_fd);
    close(uart_fd);
    fprintf(stderr, "relay: exiting\n");
    return 0;
}
