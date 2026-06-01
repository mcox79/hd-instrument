# Pre-registration: set_algebra_composability_v1

**Date:** 2026-06-01
**Anchor:** set_algebra_composability_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_set_algebra_composability_v1.py
**Cap_map row:** set-algebra primitives -- union/Jaccard/symdiff rider sub-properties

## Scientific question
Q17: Rider on Q1 (tr_w1w2_set_intersect_v1 HARD_PASS r=0.9999990). Given K_est from trace,
do derived union/Jaccard/symdiff match theory with MAE<0.5 AND Pearson r>0.999?

## Pre-registered bands
- HARD-PASS: all 3 quantities (union, Jaccard, symdiff) have MAE < 0.5 AND r > 0.999.
- MIDDLE: any MAE in [0.5, 2.0] or r in [0.99, 0.999].
- HARD-FAIL: any MAE > 2.0 or r < 0.99.

## Design
- N=2048, M1=M2=50 (same as Q1 for comparability)
- K grid: {0, 5, 10, 20, 30, 40, 50}, 3 trials per (seed, K)
- 5 seeds
- Formula: K_est = tr(W1 W2) - M1*M2/N

## Formula self-tests
1. K=0: K_est = 1.22 - 2500/2048 = 0.0. Union=100, Jaccard=0, Symdiff=100.
2. K=50: K_est = 51.20 - 2500/2048 = 50.0. Union=50, Jaccard=1.0, Symdiff=0.
3. K=10: K_est ~ 10.0. Union=90, Jaccard=10/90=0.111, Symdiff=80.

## Timeout estimate
smoke_wall_s=0.2s. FULL: ceil(1.5 * 0.2 * 1.0 * 2.5) = ceil(0.75) = 1. timeout=300 (floor).

## N-suffix note
No _nN suffix. Production N=2048 per PROT-018 rule 3.

## Smoke result
run_mode=smoke, verdict=HARD_PASS union_r=0.999997 union_mae=0.0334, elapsed=0.2s.
Metrics non-null. Very strong signal at smoke scale. PASS gate.
