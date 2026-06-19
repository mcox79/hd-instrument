# Prereg: phase_boundary_characterization_v1_n4096

Date: 2026-05-30
Anchor: phase_boundary_characterization_v1_n4096
Script: experiments/exp_phase_boundary_characterization_v1_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018)

## Question

Fine-grained probes around two phase boundaries:
- beta-axis around beta_c~10 at fixed M_frac=2; 7 betas: [9.0, 9.5, 9.8, 10.0,
  10.2, 10.5, 11.0]
- M-axis bracketing M_c estimate at fixed beta=4; 7 M values: [8192, 12288,
  16384, 20480, 24576, 28672, 32768]

Do we see phase-transition signatures (recall slope >= 5x near boundary vs
background)?

## Pre-registered bands

- **HARD_PASS**: max-center-slope / endpoint-slope >= 5.0 in EITHER beta OR
  M sweep.
- **HARD_FAIL**: slope ratio <= 1.5 in BOTH sweeps.
- **MIDDLE_BAND**: otherwise.

## Sweep

- 14 cells (7 beta + 7 M) * 5 seeds = 70 cell-seeds. retention + KF-1 at each.

## Timeout estimate

User specified 21600s. scaling_exp=1.5.
