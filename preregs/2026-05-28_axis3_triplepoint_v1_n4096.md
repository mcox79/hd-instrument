# Pre-registration: axis3_triplepoint_v1_n4096

**Date:** 2026-05-28
**Anchor:** axis3_triplepoint_v1_n4096
**Script:** experiments/exp_axis3_triplepoint_v1_n4096.py
**Queue:** overnight_queue

## Hypothesis

At the candidate triple-point operating point (M/N=6, beta=8, N=4096), perturbations in different directions produce qualitatively different retention responses: at least 2 directions show opposite-sign delta_ret, with max |delta_ret| >= 0.15.

## Context

Three independent signals (BID v245, SKAH-M v228, Pred-4 v211) point to a triple-point. Axis-3 tests whether the operating point is at a saddle by measuring direction-dependent perturbation response.

## Pre-registered Thresholds

- **HARD_PASS:** max |delta_ret| >= 0.15 AND at least 2 directions with opposite signs
- **HARD_FAIL:** all |delta_ret| < 0.02 (flat response, deep in basin)
- **MIDDLE_BAND:** max |delta_ret| in [0.02, 0.15)

## Calibration

Calibration probe: no prior direct anchor for perturbation-direction comparative study.
Bands widened to +-50% per calibration-probe policy.
HP threshold 0.15 = predicted response at saddle (50% of expected 0.3 delta_ret at full epsilon=0.40).
HF threshold 0.02 = near-zero response (substrate far from saddle).

## Walk-back gate applied

Smoke max|delta_ret|=0.13 is within 20% of HP threshold 0.15. Per role contract walk-back:
seeds doubled from 3 to 5 (SEEDS_FULL=[7,17,23,31,41]).
Also: smoke sign_divergence=False (no opposite-sign dirs). MIDDLE_BAND/borderline outcome.
HP requires BOTH max|delta_ret|>=0.15 AND sign_divergence. 5-seed run gives more power.

## Timeout Estimate

150 perturbation cells x 5 seeds (walk-back doubled). Per cell: ~1s at N=4096 (0.31s smoke / 12 cells -> 0.026s/cell; N-scale (4096/1024)^2 = 16x -> 0.41s/cell).
Total: ceil(1.5 * 0.026 * 16 * 150 * 5) = ceil(468) = 470s. Safety 5x: 2350s. PROT-019 floor: 3600s.
**timeout_s = 3600**

## N-suffix

_n4096 suffix; production N = 4096 (PROT-018 binding).

## OOM Check

W float32 at N=4096: 64MB. Peak W + codebook: ~130MB. Under 6GB. PASS.
