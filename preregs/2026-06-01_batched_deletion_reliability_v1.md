# Pre-registration: batched_deletion_reliability_v1

**Date:** 2026-06-01
**Anchor:** batched_deletion_reliability_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_batched_deletion_reliability_v1.py
**Cap_map row:** PP-9 deletion-cert -- batched-delete sub-property

## Scientific question
Q22: Does batched deletion reliability follow R(k) ~ r_1^k for independent sets?
And is the correlated case (c~0.3-0.5) characterized?

## Pre-registered bands
- HARD-PASS: empirical R(k) matches r_1^k within 2pp for k in {1,5,10,20} (independent case).
  Correlated case characterized regardless of direction.
- MIDDLE: independent case within 5pp but not 2pp for some k.
- HARD-FAIL: independent case deviates > 10pp at k <= 10.

## Design
- N=4096, M=200, k in {1, 5, 10, 20, 50}
- Two delete-set types: independent (random) and correlated (cosine ~0.40)
- Reliability: fraction deleted patterns with post-delete overlap < 0.5 * pre-delete overlap
- 5 seeds

## Formula self-tests
1. r_1 from k=1 measurement. Expected 0.88-0.96 from theory.
2. k=10 independent: R_pred = r_1^10. If r_1=0.92: R_pred=0.43.
3. Correlated ghost attractor at centroid may persist post-delete.

## Timeout estimate
smoke_wall_s=56.3s, FULL: ceil(1.5 * 56.3 * 1.0 * 2.5) = ceil(211) = 300. timeout=900.

## N-suffix note
No _nN suffix. Production N=4096 per PROT-018 rule 3.

## Smoke result
run_mode=smoke, verdict=HARD_PASS r1=1.0 max_dev=0.0, elapsed=56.3s.
r1=1.0 and max_dev=0.0 at smoke (2 seeds) may be due to low M load (alpha=0.049).
FULL run with 5 seeds will provide production-level characterization.
High r1=1.0 at smoke is consistent with good deletion reliability at low alpha.
