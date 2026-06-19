# Pre-registration: kappa3_hutchinson_v2

**Date:** 2026-06-02
**Anchor:** kappa3_hutchinson_v2
**Queue:** remote_cpu_queue

## Fix from v1
v1 TIMEOUT at 1800s: Python for-loop over n_probes=5000 with 3 N=4096 matrix-vector ops each.
v2 vectorized: 3 batched matrix-matrix multiplications (W @ W @ W @ V where V is N x n_probes).
Smoke result: 6.3s for 2 seeds 2 M values (vs >1800s in v1). HARD_PASS smoke.

## Hypothesis
kappa_3 free-cumulant Hutchinson estimator discriminates Hopfield W from GOE W with >= 4-sigma separation at N=4096, across M values [50, 100, 200, 500].

## Pre-registered thresholds
- HARD-PASS: min_sigma_sep >= 4.0 across all M values AND theory_ratio in [0.05, 20.0].
- MIDDLE: 2.0 <= min_sigma_sep < 4.0, or theory_ratio outside [0.05, 20.0].
- HARD-FAIL: min_sigma_sep < 2.0.

## Smoke result
N=4096, 2 seeds, n_probes=500, M=[100, 500]:
- min_sigma_sep=32.8, mean=101.5 (>>4.0)
- theory_ratio=1.23 (within 20x)
- HARD_PASS smoke. Vectorized estimator confirmed ~100x faster than v1.

## Timeout estimate
Smoke wall: 6.3s / (2 seeds * 2 M values) = ~1.6s per cell.
Full: n_probes=5000 (10x more probes), 5 seeds, 4 M values.
Wall = 1.5 * 6.3 * (5000/500) * (5/2) * (4/2) = 1.5 * 6.3 * 10 * 2.5 * 2 = 472s.
Round up to 600s.

## N-suffix
No _nN suffix; production N=4096 per rule 3.
