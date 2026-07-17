#!/bin/bash
# run_tests.sh — Run all test phases for the PyTorch custom-device example
#
# Usage:
#   ./scripts/run_tests.sh [phase]
#
# Phases:
#   hw      - CocoTB hardware tests (Verilator)
#   mock    - PyTorch tests with mock kernel driver
#   remote  - PyTorch tests with Renode (autostarts Renode for localhost target)
#   all     - Run all phases (default)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PHASE="${1:-all}"
PASS=0
FAIL=0

run_phase() {
    local name="$1"
    shift
    echo ""
    echo "=========================================="
    echo "  Phase: $name"
    echo "=========================================="
    if "$@"; then
        echo "  -> PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "  -> FAIL: $name"
        FAIL=$((FAIL + 1))
    fi
}

# Phase 1: Hardware tests (CocoTB + Verilator)
run_hw() {
    ./fusesoc_setup.sh
    run_phase "Hardware (CocoTB)" \
        .venv/bin/fusesoc --config fusesoc.conf run --target test \
        hardmatrix:accelerators:vector_adder_machine:0.1.0
}

# Phase 2: Mock driver PyTorch tests
run_mock() {
    # Check if driver is loaded
    if [ ! -c /dev/tensor0 ]; then
        echo "WARNING: /dev/tensor0 not found. Loading mock driver..."
        sudo rmmod tensor 2>/dev/null || true
        sudo insmod cpp/driver/tensor.ko mock=1 debug=0 mock_autocreate=1 device_mode=0666
        sleep 1
    fi

    run_phase "PyTorch (mock driver)" uv run pytest tests/test_pytorch_mock.py -v
}

# Phase 3: Remote backend PyTorch tests
run_remote() {
    run_phase "PyTorch (remote -> Renode)" \
        env TENSOR_BACKEND=remote uv run pytest tests/test_pytorch_remote.py -v
}

case "$PHASE" in
    hw)     run_hw ;;
    mock)   run_mock ;;
    remote) run_remote ;;
    all)
        run_hw
        run_mock
        run_remote
        ;;
    *)
        echo "Unknown phase: $PHASE"
        echo "Usage: $0 [hw|mock|remote|all]"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "  Results: $PASS passed, $FAIL failed"
echo "=========================================="

[ "$FAIL" -eq 0 ] || exit 1
