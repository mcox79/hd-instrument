# Pre-registration: wave14_ortho_jarzynski_crooks_v2

Date: 2026-05-27
Author: orchestrator

## Trigger

wave14_ortho_jarzynski_crooks_v1 MIDDLE_BAND: hp_frac=0.00; mean_agreement=16.517;
jarz_var=27.462. Root cause: high Jarzynski variance at beta=1.0 (strong coupling).

## Fix

- N=512 (was 256): larger N reduces per-step work fluctuations
- beta=0.3 (was 1.0): softer coupling moves system toward quasi-static limit
- M_SWEEP extended to [50, 200, 500, 1000]: probe well above capacity
- 5 seeds (was 1 in smoke)

## Pre-registered bands

HARD_PASS: hp_frac >= 0.60 AND jarz_var_mean < 5.0 at beta=0.3
  -> Jarzynski viable at soft coupling; cheaper capacity estimator unlocked

HARD_FAIL: all agreement > 200% AND jarz_var_mean > 50 even at beta=0.3
  -> Fundamental non-equilibrium gap; unusable for substrate writes

MIDDLE_BAND: intermediate
  -> May need beta < 0.3 or much larger N

INSTRUMENTATION_FAIL: NaN metrics

## Cap_map rows addressed

- Orthogonal probe: Jarzynski equality (currently no cap_map row; informational)
- Open question: can substrate write free-energy be estimated forward-only?
