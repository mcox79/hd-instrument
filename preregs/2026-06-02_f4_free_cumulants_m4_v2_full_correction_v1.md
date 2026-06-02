# Pre-registration: f4_free_cumulants_m4_v2_full_correction_v1

**Date:** 2026-06-02
**Script:** experiments/exp_f4_free_cumulants_m4_v2_full_correction_v1.py
**Queue:** remote_cpu_queue
**N:** 4096 (FULL; smoke at N=1024)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** MIDDLE_BAND at N=1024 (mean_err=0.057; alpha=0.10 still ~6.6% off)
**Timeout:** 600s (N=4096 eigvalsh; 4 alpha values x 5 seeds)

## Hypothesis

I-9 rescue: F4 M4 rel_err=0.066 at N=1024 is finite-N fluctuation.
At N=4096 (4x N), finite-N corrections reduce 4x.
Multi-alpha sweep (0.05, 0.10, 0.15, 0.20) characterizes alpha-dependence.

## Metrics

- `rel_err_M4`: |M4_emp - M4_th| / M4_th per alpha
- Secondary: `rel_err_M3`, `kappa2_rel`

## Thresholds

HARD-PASS: rel_err_M4 <= 0.05 for 3/4 alpha values AND mean <= 0.08.
HARD-FAIL: rel_err_M4 > 0.30 for any alpha.
MIDDLE: mean in (0.05, 0.30).
