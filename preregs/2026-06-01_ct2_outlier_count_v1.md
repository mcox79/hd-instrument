# Prereq: ct2_outlier_count_v1

## Scientific question
Free-Poisson empirical confirmation: (1) nonzero rank of W = M (algebraic identity), (2) lambda_max converges to (1+sqrt(alpha))^2 as N grows.

## Pre-registered bands
HARD-PASS: rank_test ALL pass AND mean edge_error < 0.03 at N=4096 in >= 4/5 seeds.
MIDDLE: rank_test passes AND edge_ratio within 0.05-0.10.
HARD-FAIL: rank_test fails OR edge_ratio < 0.90 in >= 3/5 seeds.
Calibration probe; bands +-50% per policy.

## N-suffix
No _nN suffix; production N = 4096 + N-scaling sweep; rationale: spectral convergence test at multiple scales.

## Timeout estimate
smoke_wall_s=28. FULL: ceil(1.5 * 28 * (5/2)) = 105s -> timeout_s=300.

## Date
2026-06-01
