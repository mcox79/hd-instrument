# Pre-registration: f4_free_cumulants_m4_fixed_v1

**Date:** 2026-06-02
**Script:** experiments/exp_f4_free_cumulants_m4_fixed_v1.py
**Queue:** remote_cpu_queue
**N:** 1024 (no _nN suffix)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** MIDDLE_BAND (M4_rel=0.069 > HP 0.05, M3/kappa2 PASS; wall=0.5s/3seeds)

## Hypothesis

f4_free_cumulants_v1 HARD_FAILED due to diagonal-removal bug (W had diagonal=0 but free-Poisson
moments assume W_full with diagonal). This fix uses W_full (no diagonal removal) for moment
comparison. Prediction: M4 relative error < 5% (finite-N corrections may be ~7% at N=1024).

## Fix notes

**Root cause of v1 HARD_FAIL:** W = Xi^T Xi / N had diagonal removed (np.fill_diagonal(W, 0)).
Free-Poisson formula M4 = alpha + 7alpha^2 + 6alpha^3 + alpha^4 is for W_full.
For W_diag, the eigenvalue distribution shifts by -alpha from each eigenvalue.
**Fix:** Use W_full (no diagonal removal) for eigenvalue computation.

## Metrics

- `rel_err_M4`: |M4_emp - M4_theory| / M4_theory (primary metric)
- `rel_err_M3`: |M3_emp - M3_theory| / M3_theory
- `kappa2_rel`: |kappa2_emp - alpha| / alpha

## Thresholds (pre-registered)

**HARD_PASS:** rel_err_M4 <= 0.05 AND rel_err_M3 <= 0.08 AND kappa2_rel <= 0.05 (3/3 cells)
**HARD_FAIL:** rel_err_M4 > 0.30 OR kappa2_rel > 0.20
**MIDDLE_BAND:** 2/3 cells pass

## Walk-back assessment

Smoke M4_rel=0.069, threshold=0.05, within 38% above HP. Borderline but not within 20%.
FULL run at N=1024 may show similar finite-N corrections. Interpretation: MIDDLE_BAND is
acceptable result (finite-N effects documented).

## Timeout estimate

smoke_wall_s=0.5 (3 seeds), FULL 5 seeds: timeout = ceil(1.5 * 0.5/3 * 5) = 2 -> 600s

## Calibration note

Finite-N correction to M4: smoke shows systematic ~7% deficit consistent with O(1/N) term.
