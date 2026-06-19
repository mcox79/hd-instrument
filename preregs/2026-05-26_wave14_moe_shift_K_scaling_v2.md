# Prereg: wave14_moe_shift_K_scaling_v2

**Date:** 2026-05-26
**Parent:** wave14_moe_shift_K_scaling_v1 MIDDLE_BAND (ratio=0.98, p=-0.02)
**Question:** Does K-scaling plateau at K=64, or is there continued sub-linear decline?

## Hypothesis
Extending K sweep from {2,4,8,16,32} to include K=64 maps the full K-scaling curve.
Sub-linear plateau at K=32->64 would confirm that parameter count (not structural separation) drives the near-flat scaling.

## Design
- K sweep: {2, 4, 8, 16, 32, 64}
- N=4096, M_per_expert=1600 (same as v1)
- 5 seeds
- Arms: A (SHIFT), B (PARTITION), C (SINGLE)
- GPU (overnight_queue)

## Pre-registered bands
- **HARD_PASS**: retention_A(K=64)/retention_A(K=2) >= 4.0 OR monotone with structural_lift >= 0.10
- **HARD_FAIL**: flat across K, structural_lift < 0.05
- **MIDDLE_BAND**: sub-linear scaling (ratio < 4.0 but monotone)

## Calibration
No prior empirical anchor at K=64. v1 at K=32 ratio=0.98. Bands from v1 prereg (unchanged).
