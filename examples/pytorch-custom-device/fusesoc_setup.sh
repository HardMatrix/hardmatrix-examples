#!/usr/bin/env bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FUSESOC_CONFIG=$SCRIPT_PATH/fusesoc.conf
FUSESOC_LIBRARY_ROOT=$SCRIPT_PATH/.fusesoc_libraries

if command -v fusesoc >/dev/null 2>&1; then
    FUSESOC_BIN=$(command -v fusesoc)
elif [ -x "$SCRIPT_PATH/.venv/bin/fusesoc" ]; then
    FUSESOC_BIN=$SCRIPT_PATH/.venv/bin/fusesoc
else
    echo "FuseSoC not found. Run 'uv sync' or activate an environment with fusesoc."
    return 1 2>/dev/null || exit 1
fi

fusesoc_with_config() {
    "$FUSESOC_BIN" --config "$FUSESOC_CONFIG" "$@"
}

fusesoc_has_library() {
    fusesoc_with_config library list | awk -F ':' -v name="$1" '
        NR > 1 {
            gsub(/^[ \t]+|[ \t]+$/, "", $1)
            if ($1 == name) found = 1
        }
        END { exit found ? 0 : 1 }
    '
}

mkdir -p "$FUSESOC_LIBRARY_ROOT"
touch "$FUSESOC_CONFIG"

if ! fusesoc_has_library fusesoc-gen; then
    fusesoc_with_config library add \
        --location "$FUSESOC_LIBRARY_ROOT/fusesoc-generators" \
        fusesoc-gen \
        https://github.com/fusesoc/fusesoc-generators || return 1 2>/dev/null || exit 1
fi

if ! fusesoc_has_library pytorch-custom-device; then
    fusesoc_with_config library add \
        pytorch-custom-device \
        "$SCRIPT_PATH/hw" || return 1 2>/dev/null || exit 1
fi

if [ ! -d "$FUSESOC_LIBRARY_ROOT/fusesoc-generators" ]; then
    fusesoc_with_config library update fusesoc-gen || return 1 2>/dev/null || exit 1
fi

echo "FuseSoC config: $FUSESOC_CONFIG"
echo "FuseSoC libraries: $FUSESOC_LIBRARY_ROOT"
