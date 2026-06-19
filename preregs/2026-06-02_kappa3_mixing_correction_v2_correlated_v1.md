# Pre-registration: kappa3_mixing_correction_v2_correlated_v1

**Date:** 2026-06-02
**Script:** experiments/exp_kappa3_mixing_correction_v2_correlated_v1.py
**Queue:** remote_cpu_queue
**N:** 1024 (no _nN suffix)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (all 3 rho values HP after v2 correction; v2 corrects rho>=0.20 regime)
**Timeout:** 300s (N=1024 5-seed 8 rho values)

## Hypothesis

I-10 rescue: kappa_3 mixing correction fails at rho>=0.20 with v1 formula.
v2 adds second-order term beta3_2*rho^4 fitted from empirical residuals.
Rescue strategy R2 per v334 rescue sketch.

## Metrics

- `rel_err_v2_corrected`: |k3_emp - k3_v2| / k3_v2 per rho

## Thresholds

HARD-PASS: rel_err_v2 <= 0.05 for all rho in sweep (>=4/5 seeds per rho).
HARD-FAIL: rel_err_v2 > 0.30 for any rho.
MIDDLE: some rho HP, some not.
