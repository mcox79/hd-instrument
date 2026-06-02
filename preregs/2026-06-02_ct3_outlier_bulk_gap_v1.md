# Pre-registration: ct3_outlier_bulk_gap_v1

**Date:** 2026-06-02
**Anchor:** ct3_outlier_bulk_gap_v1
**Queue:** remote_cpu_queue

## Hypothesis
Empirical lambda_max matches MP theory (1+sqrt(alpha))^2 within 5% at N=4096 for
alpha in [0.05, 0.10, 0.138].

## Pre-registered thresholds
- HARD-PASS: max relative_error < 0.05 across all alpha.
- MIDDLE: 0.05 <= max_err < 0.20.
- HARD-FAIL: max_err >= 0.20.

Follow-on to CT-2 HARD_PASS; narrower bands since CT-2 established the framework.

## Smoke result
N=4096, alpha=[0.05, 0.138], 2 seeds, 40-step power iteration:
- max_rel_error=0.0155, mean=0.0137 (HARD_PASS HP<0.05)
- Smoke wall: 1.8s

## Timeout estimate
Smoke wall: 1.8s / (2 seeds * 2 alpha) = ~0.45s per cell.
Full: 5 seeds * 3 alpha = 15 cells * 0.45s = 6.75s.
wall = 1.5 * 6.75 = 10.1s. timeout=120s.
