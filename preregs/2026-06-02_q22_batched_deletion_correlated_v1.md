# Pre-registration: q22_batched_deletion_correlated_v1

**Date:** 2026-06-02
**Anchor:** q22_batched_deletion_correlated_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_q22_batched_deletion_correlated_v1.py

## Scientific question (Q22 extension)
At moderate semantic correlation (c ~ 0.3-0.5) between stored patterns, does batched
deletion leave a "ghost attractor" (residual_cos >= 0.15 for deleted patterns) that
is absent in the uncorrelated case?

## Pre-registered thresholds
- HARD-PASS: max_residual_cos >= 0.15 at c >= 0.25 (ghost attractor confirmed at moderate correlation)
- MIDDLE: max_residual_cos in [0.05, 0.15) at c >= 0.25
- HARD-FAIL: max_residual_cos < 0.05 at all c (no ghost attractor; deletion is clean at all correlations)

## Calibration note
Smoke showed max_residual=0.143, within 5% of HARD-PASS=0.15 -> walk-back gate applied;
seeds doubled 5->10 for FULL run. N=4096 FULL, K_BATCH=[5,10,20], C_VALUES=[0.0,0.3,0.5].

## Walk-back applied
Smoke effect within 20% of HP threshold: seeds 5->10 (doubled per walk-back gate).

## Smoke result
MIDDLE_BAND (near HP): max_residual_cos=0.143 at c=0.3 (smoke N=1024, K=10, 2 seeds)
