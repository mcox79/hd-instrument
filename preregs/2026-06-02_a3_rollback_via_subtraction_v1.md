# Pre-registration: a3_rollback_via_subtraction_v1

DATE: 2026-06-02
QUEUE: remote_cpu_queue
ANCHOR: a3_rollback_via_subtraction_v1

## Scientific question
Can exact rollback of the weight matrix W be achieved via rank-1 subtraction,
restoring W to within machine precision of the pre-write state?

## Hard-pass (pre-registered)
HP1: relative_err = ||W_rb - W_orig||_F / ||W_orig||_F < 1e-10
HP2: acc after rollback >= 0.95
HP3: rollback wall time < 0.1s

## Hard-fail (pre-registered)
HF1: relative_err > 1e-6
HF2: acc after rollback < 0.80

## Middle band
2/3 HP conditions met

## Smoke result
HARD_PASS: all 3 HP conditions met (N=512 smoke, 2 seeds).
rel_err=0.0 (numerical precision), acc_after=1.000, rollback_t=0.013s.

## Production config
N=1024, M_BASE=100, K_WRITES=20, SEEDS=[7,17,23,31,41]

## Timeout estimate
~3s (algebraic; trivially fast)
