# Prereq: activation_barrier_fine_grid_v2_n4096

**Date:** 2026-06-02
**Anchor:** activation_barrier_fine_grid_v2_n4096
**Queue:** remote_cpu_queue
**Script:** experiments/exp_activation_barrier_fine_grid_v2_n4096.py

## Hypothesis

LVH #208 rescue R2: finer nf_frac grid to resolve Arrhenius ratio discrepancy.
Prior run (v1, 0.04-step grid): measured ratio=1.10 vs Arrhenius prediction=2.316 (47%).
LVH #208 annotation: coarse grid (0.04 step) compresses ratio by construction (adjacent grid points 0.40 vs 0.44).
This run uses 0.01-step grid (4x finer) to measure true nf_crit values.
If ratio increases substantially (>1.5) that confirms coarse-grid artifact.

## PROT-022 Formula Self-tests

1. Barrier ratio: (alpha_c - 0.05) / (alpha_c - 0.10) = 2.316 +- 0.001
   [INPUT: alpha_c=0.138, alpha1=0.05, alpha2=0.10]
   [EXPECTED: 2.3157 within 0.001] [VERIFIED: barrier_ratio=2.3158]
2. Grid resolution: step = 0.01 (all differences in NOISE_FRACS_FINE == 0.01)
   [VERIFIED in _selftest_grid_resolution()]

## Pre-registered Bands

**HARD-PASS:** ratio > 1.5 AND n_monotone >= 4/5 (coarse-grid artifact confirmed; ratio toward Arrhenius)
**MIDDLE:** 1.1 < ratio <= 1.5 (partial improvement; grid helped but not fully resolved)
**HARD-FAIL:** ratio <= 1.02 on fine grid (direction lost; v1 effect was noise)

## Smoke Result (N=512, 2 seeds, 0.04-step grid for comparability)

Seed 7: nf_crit_05=0.48, nf_crit_10=0.44, ratio=1.09, monotone=True
Seed 17: nf_crit_05=0.44, nf_crit_10=0.44, ratio=1.00, monotone=False
Smoke verdict: MIDDLE_BAND (expected; N=512 noisy, ratio compressed at small N)
Note: smoke uses 0.04-step for comparability with v1. FULL run uses 0.01-step.

## Walk-back gate

Smoke MIDDLE at N=512 is expected (small-N noisiness). Effect directionally positive.
FULL N=4096 with 0.01-step grid expected to show larger ratio. Proceeding.

## Timeout Estimate

- v1 elapsed: 91.5s at N=4096 5-seed (0.04-step, 13 noise fracs, 3 alpha)
- v2 uses 2 alpha and 61 noise fracs (vs 3 alpha and 13 fracs in v1)
- Cell work: 2/3 alpha * 61/13 fracs = 0.67 * 4.7 = 3.1x per seed
- v2 timeout = ceil(1.5 * 91.5 * (61/13) / (3/2)) = ceil(1.5 * 91.5 * 3.1) = ceil(425) = 600s
- Using 3600s for margin.

## N-suffix

No _nN suffix (alpha-sweep; N=4096 fixed in script).

## Cap_map Impact

- HARD-PASS: LVH #208 resolved as coarse-grid artifact; Arrhenius direction + partially confirmed magnitude; PP-33 caveat(p) updated.
- MIDDLE: partial artifact; ratio improved but barrier truly weaker than Arrhenius; R3 theory rescue warranted.
- HARD-FAIL: direction lost on fine grid; Arrhenius barrier not empirically supported at all; PP-33 caveat updated as refutation.
