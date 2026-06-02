# Pre-registration: spectral_capacity_monitor_v1

**Date:** 2026-06-02
**Anchor:** spectral_capacity_monitor_v1
**Queue:** remote_cpu_queue

## Hypothesis
lambda_max monotonically increases with M (load-bearing), and reaches >= 97% of the
MP theoretical upper edge at high load (M/N ~ 0.12-0.138). Monitor is informative.

## Pre-registered thresholds
- HARD-PASS: monotonicity_rate >= 0.80 AND mean_ratio_high >= 0.97.
- MIDDLE: monotonicity_rate >= 0.60 AND mean_ratio_high >= 0.94.
- HARD-FAIL: monotonicity_rate < 0.60 OR mean_ratio_high < 0.90.

Calibration probe; no direct empirical anchor for ratio metric.

## Smoke result
N=4096, M_low=[100, 200], M_high=[492, 565], 2 seeds:
- monotonicity_rate=1.000 (HP>=0.80)
- mean_ratio_high=0.9747 (HP>=0.97 -- marginally above)
- HARD_PASS smoke. Smoke wall: 3.5s.

## Timeout estimate
Smoke wall: 3.5s / (2 seeds * 4 M values) = ~0.44s per cell.
Full: 5 seeds * 6 M values = 30 cells * 0.44s = 13.2s.
wall = 1.5 * 13.2 * 2 (power iter overhead) = 39.6s. timeout=300s.
