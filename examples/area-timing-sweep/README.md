# Area-timing sweep

This example contains two parameterized SystemVerilog datapaths. The
`PIPELINE_STAGES` parameter distributes a fixed amount of combinational work
across register stages.

## Modules

### `arx_pipeline`

Applies `N_ROUNDS` add-rotate-XOR rounds to the input words `a_i` and `b_i`.
The result is returned through `a_o` and `b_o` when `valid_o` is asserted.

### `rs_chien_horner_pipeline`

Loads a Reed-Solomon locator polynomial through `coefficients_i`, then evaluates
it at each `x_i` using Horner's method over a binary Galois field. `value_o`
contains the polynomial value and `root_o` indicates whether it is zero. Load
the coefficients before sending input points and do not reload them while data
is still in the pipeline.

Both modules accept one input per cycle and do not provide backpressure. They
use an active-low asynchronous reset. Datapath outputs are meaningful only when
`valid_o` is asserted.

## Run the functional tests

From the repository root:

```sh
source .venv/bin/activate

fusesoc --config=fusesoc.conf \
  --cores-root=examples/area-timing-sweep \
  run --target test_arx \
  hardmatrix:examples:area_timing_sweep:0.1.0

fusesoc --config=fusesoc.conf \
  --cores-root=examples/area-timing-sweep \
  run --target test_rs \
  hardmatrix:examples:area_timing_sweep:0.1.0
```

## Run the synthesis sweeps

The repository includes a self-contained Hydra runner and FuseSoC/OpenROAD
launcher. Docker supplies OpenROAD Flow Scripts and the ASAP7 platform; no
private HardMatrix repository is required.

Resolve and inspect one configuration without running synthesis:

```sh
uv run hydra-sweep \
  --config tools/hydra-sweeps/area-timing/arx.yaml \
  --cfg job --resolve
```

Run all pipeline depths from 1 through 64 for each datapath:

```sh
uv run hydra-sweep \
  --config tools/hydra-sweeps/area-timing/arx.yaml -m \
  'parameters.PIPELINE_STAGES=range(1,65)'

uv run hydra-sweep \
  --config tools/hydra-sweeps/area-timing/rs.yaml -m \
  'parameters.PIPELINE_STAGES=range(1,65)'
```

Each point receives an isolated FuseSoC work root. The runner requires clean
OpenROAD synthesis checks, then aggregates area, cell count, power, setup
timing, and the worst setup path into JSON and CSV files below `build/`.
