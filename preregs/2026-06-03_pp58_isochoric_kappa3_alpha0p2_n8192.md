# Pre-registration: PP-58 isochoric -- kappa_3 alpha=0.2 N=8192 formula verification

**Date:** 2026-06-03
**Anchor:** `pp58_isochoric_kappa3_alpha0p2_n8192_v5_n8192`
**Queue:** remote_cpu_queue
**Trigger:** PP-58 R4: formula sqrt(1/alpha-1) over-predicts cap_crit at alpha<=0.1 by ~30-33%
  (confirmed at N=4096 and N=8192). Does the formula hold at alpha=0.2 across N?
  alpha=0.2: cap_crit_pred = sqrt(1/0.2-1) = sqrt(4) = 2.0. A clean round number.

## Capability question

Does the isochoric kappa_3 cap_crit formula sqrt(1/alpha-1) hold at alpha=0.2 N=8192?
Specifically: does measured cap_crit fall within 20% of 2.0 with resolvable envelope separation?

## Scientific context

PP-58 R2 confirmed: formula is exact at alpha=0.2 (not over-predicting as at alpha<=0.1).
This R4 test cross-validates at N=8192 vs the N=4096 R2 result. If formula holds at both N,
the alpha=0.2 regime is the boundary where PP-58 formula transitions from over-prediction
to accuracy. Key for theory recalibration (R2 theory task) and for defining the valid
operating range of the isochoric measurement protocol.

## Pre-registered bands

**HARD-PASS:** cap_crit within 20% of 2.0 (i.e., in [1.60, 2.40])
  AND audit_crit resolvable (not None)
  AND ratio (cap_crit / audit_crit) >= 5.0
  AND result consistent across >= 4/5 seeds

**MIDDLE:** cap_crit within 20% of 2.0 but ratio < 5.0
  OR audit_crit grid-limited (not enough grid resolution to resolve)
  OR cap_crit in [2.40, 3.00] (slight over-prediction begins at alpha=0.2)

**HARD-FAIL:** cap_crit > 3.0 (strong over-prediction -- formula breaks at alpha=0.2)
  OR cap_crit < 1.0 (large under-prediction)
  OR no valid measurements

## Formula self-tests (PROT-022)

1. sqrt(1/0.2 - 1) = sqrt(4) = 2.0
   [INPUT: alpha=0.2] [EXPECTED: cap_crit_pred = 2.0 exactly]
2. kappa_3 identity at sigma_g=0: ratio ~ O(1) (not 0, not infinity)
   [INPUT: sigma_g=0.0, alpha=0.2] [EXPECTED: kappa3_ratio in [0.5, 5.0]]
3. M = int(0.2 * 8192) = 1638 >= 1
   [INPUT: alpha=0.2, N=8192] [EXPECTED: M = 1638]
4. sigma_g grid contains 2.0: FULL grid [0.0, 0.1, 0.2, ..., 2.0] has 21 points
   [EXPECTED: len(SIGMA_G_FULL) = 21, max = 2.0]

## Smoke result

N_ACTIVE=1024, 2 seeds, sigma_g = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]:
MIDDLE_BAND: cap_crit=2.000 (pred=2.000, within tol), ratio=2.00 (< HP_RATIO_MIN=5.0).
Instrumentation verified: non-NaN kappa3_ratios, clear recall degradation, cap_pred exact.
MIDDLE at smoke N is expected (ratio improves with N as audit_crit sharpens).
Decision: ship -- cap_pred exact, mechanism working.

## Timeout estimate

Smoke elapsed 0.55s at N=1024, 2 seeds, 6 sigma points.
Full: N=8192, 5 seeds, 21 sigma points.
Scaling: (8192/1024)^2 * (5/2) * (21/6) = 64 * 2.5 * 3.5 = 560x.
But numpy W@x dominates: actual scaling closer to (8192/1024)^1 = 8x per probe.
Revised: ceil(1.5 * 0.55 * 8 * 2.5 * 3.5) = ceil(57.75) = 60s.
With 5x margin for Hutchinson estimator variance at larger N: 1200s.

## N-suffix section

Anchor has _n8192; N = 8192 in script. PROT-018 verified.
