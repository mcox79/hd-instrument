# Pre-registration: tcft_direct_empirical_sweep_v1_n16384

**Date**: 2026-06-01
**Anchor**: tcft_direct_empirical_sweep_v1_n16384
**Queue**: remote_cpu_queue
**Script**: experiments/exp_tcft_direct_empirical_sweep_v1_n16384.py

## Scientific Question

Does `tcft_variance_ratio` show meaningful monotonic degradation (>10% relative change) as M/N grows from 0.25 to 2.0 at N=16384? This resolves the P2 BLOCKED state caused by a 6-order-of-magnitude mismatch with an external document's cited values (0.20-0.66 vs substrate measurements of 3.2e-8).

## Design

- N = 16384 (fixed)
- M sweep: M/N in {0.25, 0.50, 1.00, 1.50, 2.00} = M in {4096, 8192, 16384, 24576, 32768}
- 5 seeds: [7, 17, 23, 31, 41]
- device: CPU (remote_cpu_queue)
- Metric: `tcft_variance_ratio` = variance(TCFT-conditioned trajectory class) / variance(unconditioned)

## Implementation Note

Uses vectorized batched gram matrix approach instead of the O(M x N^2) sequential outer-product loop.
Formula: w_mu = -(ALPHA/N) * sum_{i<mu} (v_i . v_mu)^2 + mu * ALPHA
Numerical identity with sequential verified at max diff 4.4e-16.
Gram computed in chunks of 4096 rows to limit peak memory.

## Pre-registered Thresholds (HARD -- filed before running)

### HARD-PASS (positive closure)
All mean `tcft_variance_ratio` values < 0.001 across the M/N range.
Interpretation: substrate's TCFT-equivalent is negligible; P2 closes as non-issue.
External doc's claimed 0.20-0.66 values are not replicated.

### HARD-PASS (monotonic closure)
Spearman r(M/N, mean_vr) > 0.3 (increasing trend, load degrades performance)
AND max_vr / min_vr > 2.0.
OR Spearman r < -0.3 (decreasing trend) AND max/min > 2.0.
Interpretation: substrate shows directional behavior; P2 can be classified definitively.

### HARD-FAIL
All mean `tcft_variance_ratio` values within 10% of each other (spread/mid < 0.10)
AND all values > 0.01 (moderate scale, not near-zero)
AND |Spearman r| < 0.3 (no directional trend).
Interpretation: experimental noise is indistinguishable from a monotonic pattern.
P2 closure requires redesign.

### MIDDLE-BAND
All other outcomes: some cells clean, others ambiguous. Partial closure only.
Outcome plan: identify which M/N regime is ambiguous; consider targeted 3-seed follow-up.

## Strategic Value

Either outcome is informative:
- HARD-PASS (positive): substrate TCFT-equivalent substantially better than external doc claim -- positive finding for compliance positioning.
- HARD-PASS (monotonic): external concern validated empirically with actual substrate numbers.
- HARD-FAIL: redesign needed; file upstream push to Strategy.

## Timeout Estimate

Measured single-seed timings at N=16384:
- M=4096 (M/N=0.25): 1.9s
- M=8192 (M/N=0.50): 11.3s
- M=16384 (M/N=1.00): 47.6s
- M=24576 (M/N=1.50): 113.2s
- M=32768 (M/N=2.00): 195.3s

Total per-seed: 369s. 5 seeds: 1846s.
Formula: ceil(1.5 * 1846) = ceil(2769) -> 3000s (rounded to 300s steps).
However, PROT-019 enforces a floor of 21600s for _n16384 anchors (N >= 8192).
**timeout_s = 21600** (PROT-019 floor; actual expected completion ~1846s, floor is safety margin).
Under 14400s cap -- NO, 21600s exceeds 14400s (4h) but is the mandatory PROT-019 floor.
Note: actual runtime estimated at ~1846s (0.5h); 21600s is a 12x safety margin
enforced by PROT-019 to prevent partial-seed kills seen in tcft_n8192_v5.

Scaling exponent: 2.0 (gram matrix O(M^2 * N), batched BLAS).
Smoke: N=512, FULL: N=16384 -- smoke ran at much smaller scale.
Used measured remote-machine timings (from pre-ship local tests) not smoke-based formula.

## OOM Check

Peak memory per cell (chunked approach):
- Gram chunk: chunk_size * M * 8 = 4096 * 32768 * 8 = 1.07 GB (at M=32768)
- Patterns: M * N * 8 = 32768 * 16384 * 8 = 4.29 GB (at M=32768)
- Total: 5.37 GB < 6 GB ceiling OK.
No N^2 weight matrix allocated.

## N-suffix Binding (PROT-018)

`_n16384` suffix -> production N = 16384.
Script: `N_FULL = 16384` with assertion at module scope.
Smoke runs at N_SMOKE=512 (smaller, as expected). FULL queued config uses N=16384.

## Calibration Probe Policy

Prior empirical anchor at N=8192: mean_var_ratio = 3.2e-8 (from v245+v247).
This is the first direct measurement at N=16384 WITH M sweep.
Bands are NOT widened to +-50% because the positive-closure threshold (all < 0.001)
is conservative (6 orders of magnitude above the N=8192 measurement).
The HARD-PASS conditions are designed for closure regardless of direction.

## Smoke Results (pre-registration)

Smoke at N=512, M=[128, 512], seed=17:
- M=128 (M/N=0.25): tcft_variance_ratio = 0.0305, valid=True
- M=512 (M/N=1.00): tcft_variance_ratio = 1.35e-6, valid=True

Smoke verdict: TCFT_SWEEP_HARD_PASS_MONOTONIC (decreasing trend at small N).
Smoke effect size: ratio = 22,642 >> 2.0. Strong signal at smoke scale.
Walk-back gate: smoke d >> 1.0, well clear of borderline. FULL N not doubled.

Self-test: PASS (7/7 cells, formula identity, OOM check, verdict formulas all verified).
Multi-scale smoke: N=512 and N=2048 both pass with valid metrics.
