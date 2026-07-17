.PHONY: all build venv driver clean test test-hw test-mock test-remote \
       verilator-lib relay driver-riscv image renode-build

FUSESOC ?= .venv/bin/fusesoc
FUSESOC_CONFIG ?= fusesoc.conf

# --- Host development (fast cycle) ---

all: build

venv:
	uv sync

driver:
	$(MAKE) -C cpp/driver

build: venv driver

# --- Testing ---

test-hw:
	./fusesoc_setup.sh
	$(FUSESOC) --config $(FUSESOC_CONFIG) run --target test hardmatrix:accelerators:vector_adder_machine:0.1.0

test-mock:
	.venv/bin/pytest tests/test_pytorch_mock.py -v

test-remote: verilator-lib
	TENSOR_BACKEND=remote TENSOR_REMOTE_ADDR=localhost:9001 \
		.venv/bin/pytest tests/test_pytorch_remote.py -v

test: test-hw test-mock

# --- Renode / RISC-V (slow, requires an initialized Buildroot checkout) ---

verilator-lib:
	./renode/verilator/build.sh

relay:
	$(MAKE) -C renode/relay
	install -m 0755 renode/relay/relay renode/buildroot/overlay/sbin/relay

driver-riscv:
	./renode/buildroot/build.sh module

image:
	./renode/buildroot/build.sh rebuild
	./renode/buildroot/build.sh install

renode-build: verilator-lib relay driver-riscv image

# --- Clean ---

clean:
	rm -rf .venv build out
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
	$(MAKE) -C cpp/driver clean
