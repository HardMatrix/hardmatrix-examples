# Area-timing sweep results

This directory records a 128-point post-synthesis sweep at a 1 GHz target. Both
fixed-workload datapaths were synthesized at every integer pipeline depth from
1 through 64, including all non-power-of-two configurations.

- ARX: 64 add-rotate-XOR rounds.
- RS Chien/Horner: 64 coefficients over GF(2^10).
- Pipeline stages: every integer in `1..64` for each datapath.
- Target: 1 GHz (1.000 ns period).
- Orchestration: Hydra multirun driving FuseSoC and the OpenROAD target.
- Platform: ASAP7, flat synthesis, Slang frontend, speed-oriented ABC mapping
  (`ABC_AREA=0`).
- Constraints: 100 ps clock uncertainty, zero input/output delay, and reset
  declared as a false path.
- Tool image: `openroad/orfs:latest` at
  `sha256:c1b25c7d0d74a5c3118843451a2803836ac776140bf29e87fb05a1f84d73aa02`.
- Tool versions: Yosys 0.67+post; OpenROAD 26Q3-528-g20d2d5c16e.
- Date: 2026-08-10.

All 128 runs completed successfully and every synthesis check reported zero
problems. Timing and power are post-synthesis estimates, not placed-and-routed
signoff results.

## Results

- [Combined 128-point table](sweep_1ghz.csv)
- [ARX 64-point table](arx_sweep.csv)
- [RS Chien/Horner 64-point table](rs_chien_sweep.csv)

Each of the 128 rows retains 59 fields: architectural configuration, operation
distribution, latency, throughput, tool controls, cell count, total/sequential/
combinational area, setup WNS/TNS and worst path, hold slack, minimum period,
Fmax, post-synthesis power breakdown, target classification, and selection
flags. The flags identify power-of-two depths, area-period and area-power Pareto
fronts, minimum area meeting 1 GHz, minimum period, and minimum vectorless power.

## Scatter plots

Area versus estimated minimum period:

- [Combined timing scatter plot](combined_area_timing.svg)
- [ARX timing scatter plot](arx_area_timing.svg)
- [RS Chien/Horner timing scatter plot](rs_chien_area_timing.svg)

The vertical axes are logarithmic. A continuous blue-to-green-to-yellow
gradient encodes pipeline depth from 1 through 64 stages. Text labels identify
stages 1, 2, 4, 8, 16, 32, and 64. Orange outlines and dotted connecting lines
identify the relevant Pareto front. Timing plots identify the minimum-area
point meeting 1 GHz with a red arrow and short annotation.

The SVG files were rendered with the canonical HardMatrix Matplotlib style.
Only the self-contained results and plots are checked in; no plot-generation
code or private repository dependency is part of this example.

## Selected points

| Datapath | Point | Stages | Area (µm²) | Seq. area (µm²) | Min. period (ns) | Fmax (MHz) | Setup WNS (ns) | Vectorless power (W) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ARX | No pipeline cuts | 1 | 2260.76 | 38.08 | 30.35738 | 32.94 | -29.35738 | 1.8100 |
| ARX | First/minimum-area point meeting 1 GHz | 32 | 2871.36 | 628.37 | 0.77147 | 1296.22 | +0.22853 | 0.1690 |
| ARX | One operation per stage; best period/power | 64 | 4035.22 | 1237.70 | 0.47968 | 2084.73 | +0.52032 | 0.0766 |
| RS Chien/Horner | No pipeline cuts | 1 | 2858.69 | 193.59 | 9.20330 | 108.66 | -8.20330 | 1.4300 |
| RS Chien/Horner | First point meeting 1 GHz | 13 | 2682.73 | 268.13 | 0.90812 | 1101.18 | +0.09188 | 1.0200 |
| RS Chien/Horner | Minimum-area point meeting 1 GHz | 15 | 2468.74 | 280.55 | 0.92094 | 1085.84 | +0.07906 | 0.8770 |
| RS Chien/Horner | One operation per stage; best period/power | 64 | 3040.06 | 584.89 | 0.32936 | 3036.19 | +0.67064 | 0.0480 |

## Interpretation

With 64 real operations in each workload, every measured configuration performs
useful combinational work in every stage. There are no registered pass-through
stages in this sweep; the 64-stage endpoint represents exactly one operation per
stage for both datapaths.

ARX first meets 1 GHz at 32 stages, which is also its minimum-area passing point.
RS first meets the target at 13 stages, while the 15-stage mapping is 214.0 µm²
smaller and still passes. This is a concrete example of why the all-integer sweep
is more informative than sampling only powers of two: synthesis mapping is not a
smooth function of pipeline depth.

The vectorless power estimates fall toward the deeply pipelined points in this
post-synthesis model. They were produced without VCD/SAIF activity, and the clock
group is zero because no clock tree exists yet. The power columns are
useful for relative exploration within this sweep, but they do not demonstrate
real implementation power or include the physical clock cost of the added
registers.
