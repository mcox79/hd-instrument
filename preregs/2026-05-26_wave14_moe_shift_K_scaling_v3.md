# Prereg: wave14_moe_shift_K_scaling_v3

**Date:** 2026-05-26
**Parent:** wave14_moe_shift_K_scaling_v2 (in-flight; K in {2,4,8,16,32,64})
**Trigger:** ship when v2 HARD_PASS or monotone K-scaling past K=64
**Question:** Does SHIFT structural separation scale to K=128 and K=256?

## Hypothesis
If v2 confirms monotone K-scaling to K=64, the extreme-K regime (K=128, K=256) may
show continued growth, saturation, or collapse onset. This maps the upper K envelope.

## Design
- K sweep: {64, 128, 256}  (K=64 overlap for continuity with v2)
- N = 2048 (N=4096 OOMs at K>=128; 4096^2 * 4 bytes * 128 = 8.59 GB)
- M_per_expert = 800 (proportional to N=2048)
- 5 seeds, GPU overnight_queue
- Arms: A (SHIFT), B (PARTITION), C (SINGLE) -- identical to v2

## Pre-registered bands
- **HARD_PASS**: retention_A(K=128) / retention_A(K=64) >= 1.10 AND structural_lift_A-C at K=128 >= 0.10
- **HARD_FAIL**: retention_A(K=256) <= retention_A(K=64) - 0.05 (degradation) OR Gini > 0.5 at K>=128
- **MIDDLE_BAND**: monotone but ratio(128/64) < 1.10 (plateau/slow growth)
- **INSTRUMENTATION_FAIL**: OOM at K>=128 OR non-finite retention

## Calibration
No empirical anchor at K=128 or K=256. V2 gave K=64 continuation of K=32 plateau (ratio=0.98 in v1).
Bands set at +-50% of v1 threshold per calibration-probe policy; HARD_PASS uses 10% gain threshold.

## Middle-band outcome plan
If K-scaling plateaus at K=64 (MIDDLE_BAND): characterize scaling exponent p at extreme K.
Route to: per-arm divergence probe (exp_wave14_moe_shift_K_perarm_v1) to identify mechanism.
