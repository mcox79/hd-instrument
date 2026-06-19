# Pre-registration: wave14_parisi_pq_sweep_v3

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Bet E v3 — finite-size scaling (6-test battery item #2)
Author: experiment_dev session, pipeline tick 73

## Why

Bet E v1 PARISI_DISCRIMINATES + v2 RSB_CONFIRMED already validated. The 6-test
battery item #2 (system-size scaling) was deferred from v2 as expensive. v3
addresses it: vary N and measure how Binder cumulant + overlap distribution
extrapolate to thermodynamic limit.

Per RSB phase theory: Binder cumulant should converge to a NONZERO limit as
N -> infinity (vs zero for RS phase). Multi-peak P(q) should sharpen, not
wash out, with N.

## Mechanism

For each codebook in {random_bsc, hadamard, kerdock}:
  for N in {512, 1024, 2048, 4096}:
    pool = make_pool(codebook, N, M=2N, seed)
    binder[N] = binder_cumulant(P(q) from pool)
    n_peaks[N] = histogram peak count in P(q)
  Fit binder[N] vs 1/N. Extrapolate to N -> infinity (1/N -> 0).

## Verdict labels

- PARISI_V3_RSB_THERMODYNAMIC (extrapolated binder > 0.6 — RSB confirmed
  to thermodynamic limit)
- PARISI_V3_RSB_FINITE_ONLY (binder declines with N — was finite-size,
  v2 RSB_CONFIRMED was N-specific artifact)
- PARISI_V3_INCONCLUSIVE

## Runtime: ~15 min CPU (4 N values × 3 codebooks × 3 seeds)
