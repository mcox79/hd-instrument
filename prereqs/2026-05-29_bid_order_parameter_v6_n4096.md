# Pre-registration: bid_order_parameter_v6_n4096

**Date:** 2026-05-29
**Anchor:** bid_order_parameter_v6_n4096
**Queue:** overnight_queue
**Script:** experiments/exp_bid_order_parameter_v6_n4096.py
**Parent:** bid_order_parameter_v5_n8192_bsc (MIDDLE_BAND: n_outside=3/3 but non-monotone)

## Hypothesis

BID decreases monotonically with M_frac at N=4096 BSC atoms. v5 showed the signal IS
present (n_outside=3/3) but the strict monotone check failed due to per-cell variance.
v6 uses Spearman rank correlation (robust to variance) at lower N=4096.

## Protocol

3 seeds x 8 M_fracs x N=4096 BSC atoms. Spearman rho on BID vs M_frac.
TwoNN intrinsic dimensionality estimator. No Kerdock (BSC atoms used).

## Pre-registered bands

HARD_PASS: Spearman rho < -0.5 (robust negative correlation)
  AND n_outside_low >= 2/3 seeds at M_frac <= 0.25.
  Interpretation: BID robustly decreases and stays outside Hopfield bands at low load.

HARD_FAIL: n_outside_low = 0/3 at M_frac <= 0.25.

MIDDLE_BAND: n_outside > 0 but rho >= -0.5 (not robustly monotone).

## Formula self-tests

1. N=4096 (PROT-018 binding). BSC atoms.
2. BAND_MAX_INSIDE = 0.55. normalized_bid = bid / N.
3. M at M_frac=0.05, N=4096: M=204.
4. Spearman rho < 0 means BID decreases as M_frac increases.
5. TwoNN BID: 1 / mean(log(r2/r1)) where r1, r2 are nearest-neighbor distances.

## Timeout estimate

24 cells (8 M_fracs x 3 seeds). ~2.7s/cell x 24 = 64s. Safety ceil(1.5 * 64 * 5) = 480s.
Floor _n4096 = 14400s.
timeout_s = 14400

## N-suffix binding (PROT-018)

_n4096 suffix -> N_FULL = 4096 in script. VERIFIED.
