# Hydra sweeps

This directory contains public, self-contained Hydra configurations for running
parameter sweeps through FuseSoC. The `hydra-sweep` command is installed from
this repository and does not depend on `hardmatrix-utils`.

The area/timing examples exercise the two parameterized RTL blocks under
`examples/area-timing-sweep`:

```bash
uv run hydra-sweep --config tools/hydra-sweeps/area-timing/arx.yaml -m \
  'parameters.PIPELINE_STAGES=range(1,65)'

uv run hydra-sweep --config tools/hydra-sweeps/area-timing/rs.yaml -m \
  'parameters.PIPELINE_STAGES=range(1,65)'
```

Hydra job metadata and synthesis results are written below `build/`. Each
configuration also maintains aggregate JSON and CSV files in its configured
`output.root`. The simple public runner collects metrics only; publication plots
and Pareto post-processing are intentionally outside its scope.
