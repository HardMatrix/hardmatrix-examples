# Cross-compile relay for RISC-V Linux (static, minimal)
BUILDROOT_DIR ?= $(HOME)/buildroot

# Prefer Buildroot toolchain if present; otherwise use a system cross-compiler prefix.
ifneq ($(wildcard $(BUILDROOT_DIR)/output/host/bin/riscv64-buildroot-linux-gnu-gcc),)
CROSS_COMPILE ?= $(BUILDROOT_DIR)/output/host/bin/riscv64-buildroot-linux-gnu-
else ifneq ($(wildcard $(BUILDROOT_DIR)/output/host/bin/riscv64-buildroot-linux-uclibc-gcc),)
CROSS_COMPILE ?= $(BUILDROOT_DIR)/output/host/bin/riscv64-buildroot-linux-uclibc-
else ifneq ($(wildcard $(BUILDROOT_DIR)/output/host/bin/riscv64-buildroot-linux-musl-gcc),)
CROSS_COMPILE ?= $(BUILDROOT_DIR)/output/host/bin/riscv64-buildroot-linux-musl-
else
CROSS_COMPILE ?= riscv64-linux-gnu-
endif

# GNU make provides a built-in default CC=cc; override that default for this target.
ifeq ($(origin CC), default)
CC := $(CROSS_COMPILE)gcc
endif
STRIP ?= $(CROSS_COMPILE)strip

CFLAGS = -march=rv64imafdc -mabi=lp64d -static -Os -Wall -Wextra
INCLUDES = -I../../include
API_HEADERS = ../../include/api.h ../../include/remote_api.h

.PHONY: all clean

all: relay

relay: relay.c $(API_HEADERS) Makefile
	$(CC) $(CFLAGS) $(INCLUDES) -o $@ $<
	$(STRIP) --strip-all $@

clean:
	rm -f relay
