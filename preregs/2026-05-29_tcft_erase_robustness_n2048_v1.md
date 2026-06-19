# Pre-registration: tcft_erase_robustness_n2048_v1

**Date:** 2026-05-29
**Anchor:** tcft_erase_robustness_n2048_v1
**Script:** experiments/exp_tcft_erase_robustness_n2048_v1.py
**Queue:** remote_cpu_queue
**Timeout:** 1800s

## Hypothesis

The TCFT deletion-certificate property (var_ratio < 0.10 under trajectory-class conditioning)
holds at N=2048 across a wide protocol envelope. This tests N-scale robustness of the
TCFT property that was confirmed at N=8192 in tcft_n8192_v6/v7.

Parent: tcft_erase_robustness_n8192_v1 (pending overnight_queue; same protocol at N=8192).

## Configuration

- N: 2048 (N_FULL)
- ALPHA_RATIO sweep: [0.06, 0.10, 0.125, 0.15, 0.18]
- Split threshold sweep: [0.25, 0.50, 0.75]
- Seeds: [7, 17, 23] (FULL), [17] (SMOKE)
- Smoke: N=512, 1 cell (anchor only), 1 seed
- Atoms: BSC (random +/-1); N=2048 is odd-log2 so Kerdock not valid

## Metrics

- var_ratio per cell per seed: ratio of TCFT-class variance to full-distribution variance
- n_hp_cells: count of (alpha, split) cells where var_ratio < 0.10 in >= 2/3 seeds

## Pre-registered bands

**HARD_PASS (N-invariant robustness):**
var_ratio < 0.10 in >= 2/3 seeds for >= 9/15 cells (60% of protocol space).

**HARD_PASS_CORE (minimum viable):**
var_ratio < 0.10 in >= 2/3 seeds for >= 6/15 cells (40% of protocol space).

**HARD_FAIL:**
var_ratio >= 1.0 in ALL seeds for the anchor cell (ALPHA=0.125 / split=0.50).

**MIDDLE_BAND:** anchor cell passes but < 40% of other protocol cells pass.

NOTE: calibration probe for N=2048; same thresholds as n8192 for direct N-scaling comparison.

## Timeout estimate

Smoke: N=512, 1 cell, 1 seed = 0.13s.
Full: N=2048, 15 cells, 3 seeds.
N-scale: (2048/512)^2 = 16x. Cells: 15. Seeds: 3.
Estimate: 0.13 * 16 * 15 * 3 = 93.6s.
Safety: ceil(1.5 * 93.6 * 5) = 702s -> 1800s.
timeout_s = 1800.

## Downstream

- PASS: TCFT deletion-cert is N-robust (holds at both 2048 and 8192). Strengthens product claim.
- FAIL: TCFT property is N-scale-specific (only at N=8192+). Constrains product claim.
- Middle: partial coverage; investigate which protocol cells fail at N=2048.
