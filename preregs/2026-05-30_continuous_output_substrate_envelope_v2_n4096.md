# Prereg: continuous_output_substrate_envelope_v2_n4096

Date: 2026-05-30
Anchor: continuous_output_substrate_envelope_v2_n4096
Script: experiments/exp_continuous_output_substrate_envelope_v2_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018 binding)

## Question

v1 (commit 75c565d) ran a SINGLE M=512 cell and HP-passed; cap_map v283
flagged a sub-capacity caveat. v2 sweeps M across the broader envelope
to confirm the 4 continuous-output metrics survive as M approaches
the estimated M_c (16K-20K from m_c_probe v1 MIDDLE_BAND).

## Pre-registered bands (per-M-cell composite)

Per (M, seed) cell HP thresholds (same as v1):
- `interp_cosine        >= 0.7`
- `hallu_signal_AUC     >= 0.85`
- `argmax_consistency   >= 0.95`
- `kf2_max_iso          <= 0.10`

Cross-cell verdict:

- **HARD_PASS**: all 4 metrics pass HP in >= 3/5 seeds at >= 3/4 M cells
- **HARD_FAIL**: majority-of-seeds HF (interp<=0.3 OR argmax<=0.5) in >= 3 M cells
- **MIDDLE_BAND**: otherwise

## Sweep

- N=4096, beta=8.0
- M cells: [512, 2048, 8192, 16384] (4 cells)
- Seeds: 5 ([7,17,23,31,41])
- Interp pairs: 64; hallu probes: 200; KF-2 edits: 16

## Timeout estimate

User-authorized 21600s (6h). scaling_exp=1.5 from v1 single-cell baseline
(~30s) * 4 M-cells * 5 seeds = ~600s; ample headroom.

## N-suffix

`_n4096` binds production N = 4096. Smoke runs at N=1024.
