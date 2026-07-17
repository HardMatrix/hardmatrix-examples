#!/bin/bash
# build.sh — Build minimal RISC-V Linux image for tensor-soc Renode simulation
#
# Usage:
#   ./build.sh              # Full build (first time, ~30-60 min)
#   ./build.sh rebuild      # Rebuild rootfs + kernel after overlay changes
#   ./build.sh module       # Cross-compile tensor.ko against Buildroot kernel
#   ./build.sh install      # Copy images to renode/images/ for Renode
#   BUILDROOT_DIR=/path/to/buildroot ./build.sh
#
# Prerequisites:
#   - Buildroot cloned at $BUILDROOT_DIR (default: ~/buildroot)
#   - RISC-V relay binary built (renode/relay/relay)
#
# Output:
#   $BUILDROOT_DIR/output/images/fw_jump.bin    — OpenSBI firmware (raw binary)
#   $BUILDROOT_DIR/output/images/fw_jump.elf    — OpenSBI firmware (ELF)
#   $BUILDROOT_DIR/output/images/Image          — Linux kernel (with initramfs)
#   $BUILDROOT_DIR/output/images/tensor_soc.dtb — Device tree blob

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILDROOT_DIR="${BUILDROOT_DIR:-$HOME/buildroot}"
BOARD_DIR="$BUILDROOT_DIR/board/tensor_soc"
BUILDROOT_REV="${BUILDROOT_REV:-49d1ea93f7d3ad8f7113cea39be4c39b4d6faca6}"

if [ ! -d "$BUILDROOT_DIR" ]; then
    echo "ERROR: Buildroot not found at $BUILDROOT_DIR"
    echo "Set BUILDROOT_DIR or clone default: git clone https://github.com/buildroot/buildroot ~/buildroot"
    exit 1
fi

CURRENT_BUILDROOT_REV="$(git -C "$BUILDROOT_DIR" rev-parse HEAD 2>/dev/null || true)"
if [ "$CURRENT_BUILDROOT_REV" != "$BUILDROOT_REV" ]; then
    echo "ERROR: Buildroot revision mismatch"
    echo "Expected: $BUILDROOT_REV"
    echo "Found:    ${CURRENT_BUILDROOT_REV:-not a Git checkout}"
    echo "Check out the expected revision or set BUILDROOT_REV explicitly."
    exit 1
fi

setup_board() {
    echo "=== Setting up board files ==="

    # Create board directory in Buildroot
    mkdir -p "$BOARD_DIR/overlay/sbin"
    mkdir -p "$BOARD_DIR/overlay/lib/modules"

    # Copy DTS and kernel fragment
    cp "$SCRIPT_DIR/tensor_soc.dts" "$BOARD_DIR/"
    cp "$SCRIPT_DIR/kernel.fragment" "$BOARD_DIR/"

    # Copy overlay
    cp "$SCRIPT_DIR/overlay/init" "$BOARD_DIR/overlay/"
    chmod +x "$BOARD_DIR/overlay/init"

    if [ -f "$SCRIPT_DIR/overlay/sbin/relay" ]; then
        cp "$SCRIPT_DIR/overlay/sbin/relay" "$BOARD_DIR/overlay/sbin/"
        chmod +x "$BOARD_DIR/overlay/sbin/relay"
    else
        echo "WARNING: relay binary not found — build it first (make -C renode/relay)"
    fi

    # Copy tensor.ko if available
    if [ -f "$SCRIPT_DIR/overlay/lib/modules/tensor.ko" ]; then
        cp "$SCRIPT_DIR/overlay/lib/modules/tensor.ko" "$BOARD_DIR/overlay/lib/modules/"
    fi

    # Create defconfig
    cat > "$BUILDROOT_DIR/configs/tensor_soc_defconfig" << 'DEFCONFIG'
# Architecture: RISC-V 64-bit
BR2_riscv=y

# Reproducible build metadata
BR2_REPRODUCIBLE=y

# Kernel headers
BR2_PACKAGE_HOST_LINUX_HEADERS_CUSTOM_6_18=y

# System — no init daemon, our overlay provides /init
BR2_INIT_NONE=y
BR2_SYSTEM_BIN_SH_BUSYBOX=y

# Kernel
BR2_LINUX_KERNEL=y
BR2_LINUX_KERNEL_CUSTOM_VERSION=y
BR2_LINUX_KERNEL_CUSTOM_VERSION_VALUE="6.18.7"
BR2_LINUX_KERNEL_USE_ARCH_DEFAULT_CONFIG=y
BR2_LINUX_KERNEL_CONFIG_FRAGMENT_FILES="board/tensor_soc/kernel.fragment"
BR2_LINUX_KERNEL_DTS_SUPPORT=y
BR2_LINUX_KERNEL_CUSTOM_DTS_PATH="board/tensor_soc/tensor_soc.dts"

# Rootfs — initramfs embedded in kernel image (auto-selects CPIO)
BR2_TARGET_ROOTFS_INITRAMFS=y
# BR2_TARGET_ROOTFS_EXT2 is not set

# Overlay
BR2_ROOTFS_OVERLAY="board/tensor_soc/overlay"

# OpenSBI firmware — FDT address must be past the kernel Image (~35MB)
BR2_TARGET_OPENSBI=y
BR2_TARGET_OPENSBI_CUSTOM_VERSION=y
BR2_TARGET_OPENSBI_CUSTOM_VERSION_VALUE="1.6"
BR2_TARGET_OPENSBI_PLAT="generic"
BR2_TARGET_OPENSBI_ADDITIONAL_VARIABLES="FW_JUMP_FDT_ADDR=0x88000000"

# No extra packages
# BR2_PACKAGE_HOST_QEMU is not set
DEFCONFIG

    echo "Board files and defconfig created."
}

build_full() {
    setup_board

    echo "=== Running Buildroot (this may take 30-60 minutes on first build) ==="
    cd "$BUILDROOT_DIR"
    make tensor_soc_defconfig
    make -j"$(nproc)"

    echo ""
    echo "=== Build complete ==="
    echo "Images:"
    ls -lh "$BUILDROOT_DIR/output/images/"
}

build_rebuild() {
    setup_board

    echo "=== Rebuilding rootfs + kernel ==="
    cd "$BUILDROOT_DIR"
    make tensor_soc_defconfig
    # Force rootfs rebuild
    rm -f output/images/rootfs.cpio*
    make -j"$(nproc)"

    echo "=== Rebuild complete ==="
}

build_module() {
    echo "=== Cross-compiling tensor.ko ==="

    KDIR="$BUILDROOT_DIR/output/build/linux-6.18.7"
    if [ ! -d "$KDIR" ]; then
        echo "ERROR: Kernel build directory not found at $KDIR"
        echo "Run './build.sh' first to build the kernel."
        exit 1
    fi

    # Auto-detect toolchain prefix (glibc vs uclibc vs musl)
    CROSS=""
    for prefix in riscv64-buildroot-linux-gnu- riscv64-buildroot-linux-uclibc- riscv64-buildroot-linux-musl-; do
        if [ -f "$BUILDROOT_DIR/output/host/bin/${prefix}gcc" ]; then
            CROSS="$BUILDROOT_DIR/output/host/bin/${prefix}"
            break
        fi
    done
    if [ -z "$CROSS" ]; then
        echo "ERROR: Buildroot toolchain not found"
        echo "Run './build.sh' first to build the toolchain."
        exit 1
    fi
    echo "Using toolchain: ${CROSS}gcc"

    MODULE_BUILD_DIR="$REPO_DIR/build/driver-riscv"
    mkdir -p "$MODULE_BUILD_DIR/src"
    install -m 0644 "$REPO_DIR/cpp/driver/Makefile" "$MODULE_BUILD_DIR/Makefile"
    install -m 0644 "$REPO_DIR/cpp/driver/src/hal.c" "$MODULE_BUILD_DIR/src/hal.c"

    make -C "$KDIR" \
        M="$MODULE_BUILD_DIR" \
        ARCH=riscv \
        CROSS_COMPILE="$CROSS" \
        clean

    make -C "$KDIR" \
        M="$MODULE_BUILD_DIR" \
        ARCH=riscv \
        CROSS_COMPILE="$CROSS" \
        modules

    "${CROSS}strip" --strip-debug "$MODULE_BUILD_DIR/tensor.ko"

    install -D -m 0644 "$MODULE_BUILD_DIR/tensor.ko" \
        "$SCRIPT_DIR/overlay/lib/modules/tensor.ko"
    echo "tensor.ko built and copied to overlay."

    echo ""
    echo "Now run './build.sh rebuild' to embed the module in the kernel image."
}

install_images() {
    echo "=== Installing images to renode/images/ ==="

    IMAGES_DIR="$REPO_DIR/renode/images"
    mkdir -p "$IMAGES_DIR"

    BR_IMAGES="$BUILDROOT_DIR/output/images"
    if [ ! -d "$BR_IMAGES" ]; then
        echo "ERROR: No Buildroot images found. Run './build.sh' first."
        exit 1
    fi

    if [ -f "$BR_IMAGES/fw_jump.bin" ]; then
        cp "$BR_IMAGES/fw_jump.bin" "$IMAGES_DIR/"
    elif [ -f "$BR_IMAGES/fw_jump.elf" ]; then
        echo "WARNING: fw_jump.bin not found, attempting to generate from fw_jump.elf"
        OBJCOPY_BIN=""
        for candidate in \
            "$BUILDROOT_DIR/output/host/bin/riscv64-buildroot-linux-gnu-objcopy" \
            "$BUILDROOT_DIR/output/host/bin/riscv64-buildroot-linux-uclibc-objcopy" \
            "$BUILDROOT_DIR/output/host/bin/riscv64-buildroot-linux-musl-objcopy" \
            riscv64-linux-gnu-objcopy \
            llvm-objcopy \
            objcopy; do
            if [ -x "$candidate" ]; then
                OBJCOPY_BIN="$candidate"
                break
            fi
            if command -v "$candidate" >/dev/null 2>&1; then
                OBJCOPY_BIN="$(command -v "$candidate")"
                break
            fi
        done
        if [ -z "$OBJCOPY_BIN" ]; then
            echo "ERROR: Could not find objcopy to generate fw_jump.bin from fw_jump.elf"
            exit 1
        fi
        "$OBJCOPY_BIN" -O binary "$BR_IMAGES/fw_jump.elf" "$IMAGES_DIR/fw_jump.bin"
    else
        echo "ERROR: Neither fw_jump.bin nor fw_jump.elf found in $BR_IMAGES"
        exit 1
    fi
    cp "$BR_IMAGES/Image" "$IMAGES_DIR/"
    cp "$BR_IMAGES/tensor_soc.dtb" "$IMAGES_DIR/" 2>/dev/null || \
        echo "WARNING: tensor_soc.dtb not found (check BR2_LINUX_KERNEL_CUSTOM_DTS_PATH)"

    (
        cd "$IMAGES_DIR"
        sha256sum Image fw_jump.bin tensor_soc.dtb > SHA256SUMS
    )

    echo "Installed to $IMAGES_DIR/:"
    ls -lh "$IMAGES_DIR/"
}

case "${1:-full}" in
    full)    build_full ;;
    rebuild) build_rebuild ;;
    module)  build_module ;;
    install) install_images ;;
    *)
        echo "Usage: $0 [full|rebuild|module|install]"
        exit 1
        ;;
esac
