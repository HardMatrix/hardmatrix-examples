#include "backend.h"
#include "../../include/api.h"
#include "../../include/remote_api.h"

#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netdb.h>
#include <unistd.h>
#include <cerrno>
#include <cstring>
#include <cstdlib>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>

#if __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "The tensor remote protocol currently requires a little-endian host"
#endif

static_assert(sizeof(remote_submit) == 32, "remote_submit wire size changed");
static_assert(sizeof(remote_response) == 16, "remote_response wire size changed");

// --- Ioctl Backend: local /dev/tensor0 ---

class IoctlBackend : public HardwareBackend {
    int fd_ = -1;
    std::mutex mutex_;

    void ensure_open() {
        if (fd_ >= 0) return;
        fd_ = ::open("/dev/tensor0", O_RDWR);
        if (fd_ < 0)
            throw std::runtime_error(
                "Failed to open /dev/tensor0: " + std::string(::strerror(errno)));
    }

public:
    bool is_available() noexcept override {
        std::lock_guard<std::mutex> lock(mutex_);
        try {
            ensure_open();
            return true;
        } catch (...) {
            return false;
        }
    }

    int submit(uint32_t op, uint32_t len, uint32_t elem_bytes,
               const void* a_data, const void* b_data,
               void* out_data) override {
        std::lock_guard<std::mutex> lock(mutex_);
        ensure_open();

        tensor_submit s{};
        s.version    = TENSOR_API_VERSION;
        s.op         = op;
        s.len        = len;
        s.elem_bytes = elem_bytes;
        s.a_ptr      = (uint64_t)(uintptr_t)a_data;
        s.b_ptr      = (uint64_t)(uintptr_t)b_data;
        s.out_ptr    = (uint64_t)(uintptr_t)out_data;
        s.timeout_ms = 1000;

        return ::ioctl(fd_, TENSOR_IOC_SUBMIT, &s);
    }

    ~IoctlBackend() override {
        if (fd_ >= 0) ::close(fd_);
    }
};

// --- Remote Backend: TCP to Renode relay ---

class RemoteBackend : public HardwareBackend {
    int sock_ = -1;
    std::mutex mutex_;

    struct HostPort {
        std::string host;
        std::string port;
    };

    static HostPort parse_remote_addr(const std::string& addr) {
        std::string host;
        std::string port_str;

        if (addr.empty()) {
            throw std::runtime_error("TENSOR_REMOTE_ADDR is empty");
        }

        if (addr.front() == '[') {
            const auto close = addr.find(']');
            if (close == std::string::npos || close + 1 >= addr.size() || addr[close + 1] != ':') {
                throw std::runtime_error("TENSOR_REMOTE_ADDR must be [host]:port for IPv6 addresses");
            }
            host = addr.substr(1, close - 1);
            port_str = addr.substr(close + 2);
        } else {
            const auto colon = addr.rfind(':');
            if (colon == std::string::npos) {
                throw std::runtime_error("TENSOR_REMOTE_ADDR must be host:port");
            }
            host = addr.substr(0, colon);
            port_str = addr.substr(colon + 1);
            if (host.find(':') != std::string::npos) {
                throw std::runtime_error("TENSOR_REMOTE_ADDR must use [host]:port for IPv6 addresses");
            }
        }

        if (host.empty() || port_str.empty()) {
            throw std::runtime_error("TENSOR_REMOTE_ADDR requires both host and port");
        }

        char* end = nullptr;
        errno = 0;
        long port = std::strtol(port_str.c_str(), &end, 10);
        if (errno != 0 || end == port_str.c_str() || *end != '\0' || port < 1 || port > 65535) {
            throw std::runtime_error("TENSOR_REMOTE_ADDR has invalid port: " + port_str);
        }

        return HostPort{host, std::to_string(port)};
    }

    static int parse_socket_timeout_ms() {
        const char* timeout = std::getenv("TENSOR_REMOTE_SOCKET_TIMEOUT_MS");
        if (!timeout || *timeout == '\0') return 10000;

        char* end = nullptr;
        errno = 0;
        long value = std::strtol(timeout, &end, 10);
        if (errno != 0 || end == timeout || *end != '\0' || value < 1 || value > 600000) {
            throw std::runtime_error(
                "TENSOR_REMOTE_SOCKET_TIMEOUT_MS must be an integer in [1, 600000]");
        }
        return static_cast<int>(value);
    }

    static void configure_socket_timeouts(int fd, int timeout_ms) {
        struct timeval tv{};
        tv.tv_sec = timeout_ms / 1000;
        tv.tv_usec = (timeout_ms % 1000) * 1000;
        if (::setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0 ||
            ::setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv)) < 0) {
            throw std::runtime_error(
                "Failed to configure remote socket timeout: " + std::string(::strerror(errno)));
        }
    }

    static void send_all(int fd, const void* buf, size_t len) {
        const char* p = (const char*)buf;
        while (len > 0) {
            ssize_t n = ::send(fd, p, len, MSG_NOSIGNAL);
            if (n < 0) {
                if (errno == EINTR) continue;
                if (errno == EAGAIN || errno == EWOULDBLOCK)
                    throw std::runtime_error("remote send timed out");
                throw std::runtime_error(
                    "remote send failed: " + std::string(::strerror(errno)));
            }
            if (n == 0) throw std::runtime_error("remote send failed: connection closed");
            p += n;
            len -= (size_t)n;
        }
    }

    void close_socket() noexcept {
        if (sock_ >= 0) {
            ::close(sock_);
            sock_ = -1;
        }
    }

    static void recv_all(int fd, void* buf, size_t len) {
        char* p = (char*)buf;
        while (len > 0) {
            ssize_t n = ::recv(fd, p, len, 0);
            if (n < 0) {
                if (errno == EINTR) continue;
                if (errno == EAGAIN || errno == EWOULDBLOCK)
                    throw std::runtime_error("remote recv timed out");
                throw std::runtime_error(
                    "remote recv failed: " + std::string(::strerror(errno)));
            }
            if (n == 0) throw std::runtime_error("remote recv failed: connection closed");
            p += n;
            len -= (size_t)n;
        }
    }

    void ensure_connected() {
        if (sock_ >= 0) return;

        const char* addr = std::getenv("TENSOR_REMOTE_ADDR");
        if (!addr) addr = "localhost:9001";

        const std::string addr_str(addr);
        const HostPort hp = parse_remote_addr(addr_str);

        struct addrinfo hints{};
        hints.ai_family = AF_UNSPEC;
        hints.ai_socktype = SOCK_STREAM;

        struct addrinfo* result = nullptr;
        const int gai_rc = ::getaddrinfo(hp.host.c_str(), hp.port.c_str(), &hints, &result);
        if (gai_rc != 0) {
            throw std::runtime_error(
                "resolve() for " + addr_str + " failed: " + std::string(::gai_strerror(gai_rc)));
        }

        int last_errno = 0;
        for (struct addrinfo* ai = result; ai != nullptr; ai = ai->ai_next) {
            const int fd = ::socket(ai->ai_family, ai->ai_socktype, ai->ai_protocol);
            if (fd < 0) {
                last_errno = errno;
                continue;
            }
            if (::connect(fd, ai->ai_addr, ai->ai_addrlen) == 0) {
                sock_ = fd;
                break;
            }
            last_errno = errno;
            ::close(fd);
        }
        ::freeaddrinfo(result);

        if (sock_ < 0) {
            throw std::runtime_error(
                "connect() to " + addr_str + " failed: " + std::string(::strerror(last_errno)));
        }

        try {
            const int timeout_ms = parse_socket_timeout_ms();
            configure_socket_timeouts(sock_, timeout_ms);
        } catch (...) {
            close_socket();
            throw;
        }

        // Wait for READY\n from relay
        char buf[6];
        recv_all(sock_, buf, sizeof(buf));
        if (std::memcmp(buf, "READY\n", sizeof(buf)) != 0) {
            close_socket();
            throw std::runtime_error("remote handshake failed: expected READY\\n");
        }
    }

public:
    bool is_available() noexcept override {
        std::lock_guard<std::mutex> lock(mutex_);
        try {
            ensure_connected();
            return true;
        } catch (...) {
            close_socket();
            return false;
        }
    }

    int submit(uint32_t op, uint32_t len, uint32_t elem_bytes,
               const void* a_data, const void* b_data,
               void* out_data) override {
        std::lock_guard<std::mutex> lock(mutex_);
        try {
            ensure_connected();

            size_t data_bytes = (size_t)len * elem_bytes;

            remote_submit req{};
            req.magic = REMOTE_MAGIC;
            req.version = REMOTE_PROTOCOL_VERSION;
            req.op = op;
            req.len = len;
            req.elem_bytes = elem_bytes;

            send_all(sock_, &req, sizeof(req));
            send_all(sock_, a_data, data_bytes);
            send_all(sock_, b_data, data_bytes);

            remote_response resp{};
            recv_all(sock_, &resp, sizeof(resp));

            if (resp.magic != REMOTE_MAGIC)
                throw std::runtime_error("Invalid response magic");
            if (resp.version != REMOTE_PROTOCOL_VERSION)
                throw std::runtime_error("Unsupported response protocol version");
            if (resp.len != len)
                throw std::runtime_error("Invalid response length");
            if (resp.status != 0) return -1;

            recv_all(sock_, out_data, data_bytes);
            return 0;
        } catch (...) {
            close_socket();
            throw;
        }
    }

    ~RemoteBackend() override {
        close_socket();
    }
};

// --- Backend selector ---

HardwareBackend& get_backend() {
    static std::unique_ptr<HardwareBackend> instance = [] {
        const char* env = std::getenv("TENSOR_BACKEND");
        if (env && std::string(env) == "remote") {
            return std::unique_ptr<HardwareBackend>(new RemoteBackend());
        }
        return std::unique_ptr<HardwareBackend>(new IoctlBackend());
    }();
    return *instance;
}
