export PLATFORM ?= asap7

# Edalize resolves the FuseSoC dependency graph and writes these manifests in
# the build root. The build root is mounted read-only at /work in the ORFS image.
export VERILOG_FILES = $(addprefix /work/,$(shell cat /work/files.txt))
export VERILOG_INCLUDE_DIRS = $(addprefix /work/,$(shell cat /work/incdirs.txt))
export SDC_FILE = /work/constraint.sdc

export SYNTH_HDL_FRONTEND = slang

# Permit inferred memories up to 2^20 bits to map normally.
export SYNTH_MEMORY_MAX_BITS ?= 1048576
export SYNTH_MOCK_LARGE_MEMORIES ?= 0
