# Prereg: hippocampal_place_field_v1

## Scientific question
Hippocampal place-field encoding: does the substrate store and retrieve spatially-structured
place-field patterns with spatial gradient preservation?

## Pre-registered thresholds
- HARD-PASS: All of A (cosine >= 0.80), B (rho_spatial >= 0.60), C (acc_K >= 0.75).
- HARD-FAIL: 0-1 cells pass.
- MIDDLE: 2/3 cells.

## Calibration note
First place-field encoding test. Bands +-50% per calibration-probe policy.
Theory: PLACE_FRAC=0.30 active neurons, Gaussian sigma=2, K=50 << alpha_c*N=141.

## Smoke result
HARD_PASS 3/3: cosine=0.879 (HP>=0.80), rho_spatial=0.856 (HP>=0.60), acc=0.879 (HP>=0.75).
Excellent smoke result. No walk-back needed. Spatial gradient preserved (rho=0.856).

## Timeout estimate
Smoke wall: 0.1s. FULL: N=1024, K=50, seeds=5 (vs smoke seeds=2).
timeout = ceil(1.5 * 0.1 * 2^1.0 * 2.5) = ceil(0.75) = 1s.
timeout=120s (overhead dominated).

## N-suffix note
No _nN suffix; production N=1024 per rule 3.
