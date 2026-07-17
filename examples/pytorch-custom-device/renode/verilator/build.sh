#!/bin/bash
# Build VectorAdderMachine as a Verilated native shared library for Renode
#
# Prerequisites:
#   - Verilator installed
#   - Renode with IntegrationLibrary (renode_bus.h, axilite.h)
#   - Chisel-generated SystemVerilog in hw/chisel/vector_adder_machine/src/
#
# Usage:
#   cd <repo-root>
#   ./renode/verilator/build.sh
#
# Output: renode/verilator/libVverilated_vam.so (native shared library loaded by Renode)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$SCRIPT_DIR/obj_dir"
OUTPUT="$SCRIPT_DIR/libVverilated_vam.so"

# Paths to RTL sources
VAM_SRC="$REPO_ROOT/hw/chisel/vector_adder_machine/src"
VAM_GEN="$REPO_ROOT/hw/chisel/vector_adder_machine/generated"
AXI_SRC="$REPO_ROOT/hw/axi4_lite/src"

# Renode verilator-integration path
RENODE_INTEGRATION="${RENODE_INTEGRATION:-/opt/renode/plugins/IntegrationLibrary}"

if [ ! -d "$RENODE_INTEGRATION" ]; then
    echo "ERROR: Renode IntegrationLibrary not found at $RENODE_INTEGRATION"
    echo "Set RENODE_INTEGRATION env var to the correct path"
    echo "Typically: /opt/renode/plugins/IntegrationLibrary"
    exit 1
fi

echo "=== Building Verilated VAM for Renode ==="
echo "RTL sources: $VAM_SRC"
echo "Renode integration: $RENODE_INTEGRATION"

# Generate Chisel SV if not already present
if [ ! -f "$VAM_GEN/VectorAdderMachine.sv" ] || [ ! -f "$VAM_GEN/VectorAdderUnit.sv" ]; then
    echo "Generating Chisel SV..."
    (cd "$REPO_ROOT/hw/chisel/vector_adder_machine" && mill -i vector_adder_machine.run --target-dir=generated)
fi

# Verilate — build as shared library for native Renode integration
verilator \
    --cc \
    --exe \
    --timing \
    -Wno-MULTIDRIVEN -Wno-WIDTHTRUNC -Wno-WIDTHEXPAND \
    -CFLAGS "-fPIC -DINVERT_RESET -I$RENODE_INTEGRATION -I$RENODE_INTEGRATION/libs/socket-cpp" \
    -LDFLAGS "-shared" \
    --top-module VectorAdderMachine \
    -Mdir "$BUILD_DIR" \
    "$VAM_GEN/VectorAdderMachine.sv" \
    "$VAM_GEN/VectorAdderUnit.sv" \
    "$VAM_SRC/vector_adder_machine_regmap.sv" \
    "$VAM_SRC/vector_adder_machine_regmap_pkg.sv" \
    "$VAM_SRC/vector_adder_machine_regmap_wrapper.sv" \
    "$AXI_SRC/axi4lite_intf.sv" \
    "$SCRIPT_DIR/sim_renode.cpp" \
    "$RENODE_INTEGRATION/src/renode_bus.cpp" \
    "$RENODE_INTEGRATION/src/buses/bus.cpp" \
    "$RENODE_INTEGRATION/src/buses/axilite.cpp" \
    "$RENODE_INTEGRATION/src/communication/socket_channel.cpp" \
    "$RENODE_INTEGRATION/libs/socket-cpp/Socket/Socket.cpp" \
    "$RENODE_INTEGRATION/libs/socket-cpp/Socket/TCPClient.cpp"

# Build
make -C "$BUILD_DIR" -f VVectorAdderMachine.mk -j"$(nproc)"

# Copy output
cp "$BUILD_DIR/VVectorAdderMachine" "$OUTPUT"

echo "=== Done: $OUTPUT ==="
echo "Use in Renode .repl: simulationFilePath: @$OUTPUT"
