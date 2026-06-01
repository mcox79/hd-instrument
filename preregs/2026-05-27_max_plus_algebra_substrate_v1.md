# Pre-registration: max_plus_algebra_substrate_v1

Date: 2026-05-27
Experimenter: exp_dev (sub-agent)
Probe type: Orthogonal framework (tropical/max-plus algebra)

## Hypothesis

Max-plus (tropical) algebra can serve as an alternative memory retrieval operation
for BSC substrate. The tropical inner product max_j(W_ij + v_j) replaces the
bilinear Hebbian inner product. This matters because:
1. Deletion in max-plus = set column to -inf (algebraically exact GDPR erase)
2. Capacity is determined by LP geometry (different from spectral theory)
3. This is an unexplored algebraic lens on substrate memory

## Pre-registered thresholds (calibration probe -- no prior empirical anchor)

HARD-PASS: K=1 exact accuracy >= 0.90 (max-plus CAN retrieve single pattern)
  AND K=4 exact accuracy >= 0.50 (above chance 1/256)
HARD-FAIL: K=1 exact accuracy < 0.20 (below any useful signal)
MIDDLE-BAND: 0.20 <= K=1 < 0.90

Calibration-probe policy applied: HARD-PASS at theoretical prediction (0.90 for K=1),
HARD-FAIL at 3x below (0.20). Bands explicitly wider than default.
"No prior empirical anchor on max-plus substrate; bands set per calibration-probe policy."

## Timeout estimate

N=1024 5 K-values 5 seeds 100 trials each: ~40s.
timeout_s = ceil(1.5 * 40 * 1.0) = ceil(60) -> 300s.

## Smoke result

N=256 2 K-values 1 seed: K=1 exact=1.000 (HARD_PASS at smoke).
K=4 exact=0.250. Smoke HARD_PASS (K=1 >= 0.90). Proceeding to FULL.

## N-suffix

No _nN suffix; production N = 1024 (standard calibration probe N, stated in script).
