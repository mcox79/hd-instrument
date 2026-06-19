# Pre-registration: q_c2_mp_hc_v2_corrected_n4096

**Date:** 2026-06-02
**Script:** experiments/exp_q_c2_mp_hc_v2_corrected_n4096.py
**Queue:** overnight_queue
**N:** 4096 (PROT-018 binding)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (Z=0.59 at alpha=0.05, Z=0.35 at alpha=0.10; null_mean=1.5295, null_std=0.0711)

## Hypothesis

The Hopfield lambda_max is consistent with the Marchenko-Pastur bulk when measured against an empirical Wishart null (same N, M, +-1 entries). Z-score in [-3, 3] across all alpha values indicates no spectral anomaly. Redesign from v1 which used asymptotic MP formula causing Z=-18 to -41 systematic bias at finite N.

## Metrics

- `Z_clean`: (lmax_Hopfield - null_mean) / null_std per (alpha, seed)
- `null_mean`, `null_std`: empirical from 50 Wishart null samples per cell

## Thresholds (pre-registered)

**HARD_PASS:** ALL Z_clean in [-3.0, 3.0] across all (alpha, seed)
**HARD_FAIL:** ANY |Z_clean| > 5.0
**MIDDLE_BAND:** some cells outside [-3, 3] but none outside [-5, 5]

## Timeout

2700s (from: 1.5 * 4.5s * (1024/1024)^1 * 5/2 * (50/8 null samples scale) ~= 2700s estimated)
