# Pre-reg: large_k_path_scaling_v1_n4096

**Date:** 2026-05-30
**Anchor:** large_k_path_scaling_v1_n4096
**Script:** experiments/exp_large_k_path_scaling_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** user msg 2026-05-30 next-1-2-week priorities ("K_paths scaling toward production-realistic values")

## Hypothesis

Bayesian propagation (D) enumerates K candidate paths and scores each
(K * depth log-likelihoods). Continuous-output (B) and spectral (E)
don't enumerate explicitly per-candidate but DO score each candidate
in the K-pool here, since the experimental harness compares mechanisms
on the SAME candidate pool. The expected scaling is:
- B and E: linear in K (per-candidate scoring of a fixed-cost forward op)
- D: linear in K (per-hop loglikelihood) -- but K-enumeration
  combinatorics if D builds candidate trees implicitly.

Accuracy hypothesis: at fixed depth=4 and M=512, do any of the paths
maintain >= 0.65 accuracy at K=1000?

Latency hypothesis: sub-quadratic latency scaling (lat(K=1000)/lat(K=100) < 100).

## Pre-registered bands

| Outcome      | Condition                                                                |
|--------------|--------------------------------------------------------------------------|
| HARD_PASS    | at least one path maintains accuracy >=0.65 at K=1000 in >=3/5 seeds AND has latency_ratio(K=1000)/latency_ratio(K=100) < 100 (sub-quadratic) |
| HARD_FAIL    | all 3 paths drop below 0.30 accuracy at K >= 250 (no production-scale viability) in >=3/5 seeds |
| MIDDLE_BAND  | otherwise                                                                |

## Calibration

P(HP) estimate: 0.40-0.55. B's forward op is O(N) per candidate
regardless of K (just argmax against codebook). D's loglik is also
linear per candidate. E's spectral signature requires a topk per hop
per candidate. All 3 are linear in K asymptotically. Accuracy at K=1000
depends on whether 999 decoys can pull argmax away from the coherent
path -- substrate's KF1 sharpness suggests B stays high; D and E less
certain.

## Self-test

- N == 4096 (PROT-018); M == 512 (sub-capacity); depth == 4.
- K_PATHS_FULL contains both 100 (denominator) and 1000 (numerator) for
  latency ratio.
- Verdict gate HP synthetic: B with stable acc=0.7 at K=1000 and linear
  latency passes; D with quadratic latency fails sub-quadratic.
- Verdict gate HF synthetic: all 3 dropping below 0.30 at K>=250 fails.
- Forward pass at smoke (N=1024, M=64, K=10, n_queries=2) returns
  bounded acc values and positive latencies.

## Timeout estimate

smoke_wall_s = 0.79s (K=10 and K=100 at N=1024, 1 seed). Each K=100
took ~270 ms on E mechanism; at K=1000 that's ~2.7s/query for E. FULL:
6 K-values x 5 seeds x 3 paths x 5 queries. E at K=1000 alone: 5
queries * 5 seeds = 25 queries * 2.7s = 67s for E at K=1000. Total
across all K: ~5x at K<=100 (negligible) + 67s at K=1000 + 50s at K=500
+ 25s at K=250 = ~150s for E. B and D much faster. At N=4096, multiply
all by ~4-16x from the N-ratio. Estimate 30-60 minutes.
scaling_exp = 1.5. `ceil(1.5 * 0.79 * 4^1.5 * 5 * 6) = 711s` ratio-based
but doesn't capture the K-axis; direct estimate is 1800-3600s.
**timeout_s = 21600** (6h budget; this is a scaling sweep with K=1000
where E mechanism's per-query cost grows substantially).

NOTE: 21600s > 14400s threshold -> per-experiment-timeout-required
policy: this is a long run, FLAGGED for For You visibility but approved
because the K-scaling sweep IS the load-bearing question.

## Production config

N=4096, M=512, depth=4, K_paths=[10, 50, 100, 250, 500, 1000],
seeds=[7,17,23,31,41], n_queries=5, beta=4.0, top_k_sig=16.

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
