# Pre-registration: kappa3_mixing_correction_completion_v1

**Date:** 2026-06-02
**Script:** experiments/exp_kappa3_mixing_correction_completion_v1.py
**Queue:** remote_cpu_queue
**N:** 1024 (no _nN suffix)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (rel_err_corrected=0.012-0.023 at rho=0,0.1; wall<0.15s/seed)

## Hypothesis

kappa_3(W) = M/N for IID patterns (free-Poisson identity). Under correlated patterns (rho>0),
mixing correction delta_kappa3 = beta_3 * rho^2 restores predicted kappa_3 to within 3%.
Research predicts: beta_3 = alpha (leading-order correction from replica calculation).

## Metrics

- `rel_err_corrected`: |kappa3_emp - kappa3_corrected| / kappa3_corrected per rho value
- `rel_err_iid`: |kappa3_emp - alpha| / alpha (uncorrected, for comparison)

## Thresholds (pre-registered)

**HARD_PASS:** rel_err_corrected <= 0.03 for ALL rho in {0, 0.10, 0.20, 0.30}
**HARD_FAIL:** rel_err_corrected > 0.30 for any rho (formula wrong)
**MIDDLE_BAND:** some rho within 3%, some between 3% and 30%

## Walk-back assessment

Smoke shows rel_err=0.012-0.023 at rho=0,0.10 -- both < 0.03 HP threshold.
Robust margin at smoke scale.

## Timeout estimate

smoke_wall_s=0.13 (2 rho, 2 seeds), FULL 4 rho x 5 seeds:
timeout = ceil(1.5 * 0.13 * (4/2) * (5/2)) = ceil(0.98) -> 600s
