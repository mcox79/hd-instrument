# exp_dev -> Strategy: BID v6 blocked (metric incompatibility)

**Filed:** 2026-05-29
**Blocking reason:** INSTRUMENTATION_SUSPECT - BAND_MAX_INSIDE from v1 is not applicable
  to raw BSC pattern BID (measures different quantities)

## What was attempted

bid_order_parameter_v6_n4096: rescue of bid_order_parameter_v5_n8192_bsc MIDDLE_BAND
by using N=4096 BSC atoms with Spearman rank correlation instead of strict monotone.

## What was found

Smoke at N=512 (BSC): bid_norm=0.21 at M_frac=0.05. HARD_FAIL: bid_norm < BAND_MAX_INSIDE=0.55.
4x smoke at N=2048: bid_norm=0.12 -- even lower.

## Root cause

BAND_MAX_INSIDE=0.55 was established in bid_m_normalized_v1 for Hopfield ATTRACTOR BID
(BID of attractor vectors after Hopfield dynamics), NOT raw pattern BID. The v5 and v6
approach measures TwoNN BID of RAW BSC patterns (before any dynamics).

For random BSC patterns of size M at dimension N:
  BID = TwoNN estimate ~ min(M-1, d_intrinsic)
  For N=512, M=25: BID ~ 17 (limited by sample size)
  normalized_bid = 17/512 = 0.033

For Hopfield attractors (v1):
  Attractors are clustered near stored patterns -> lower intrinsic dim -> BID < N
  The 0.55 threshold was calibrated for this clustered structure.

Raw BSC patterns have NO clustering structure; their TwoNN BID is limited by
sample size M and scales differently from attractor BID.

## Why Kerdock doesn't work

Kerdock codewords are equidistant (pairwise distances all = sqrt(2N)). This makes
r1=r2 for all points, log(r2/r1)=0, and TwoNN BID is undefined (returns NaN).

## Recommendations to Strategy

Option 1: Use Hopfield attractor-based BID at N=4096 (same as v1 but extend M_frac
grid and use Spearman monotone criterion). This preserves comparability with BAND_MAX_INSIDE.

Option 2: Calibrate a new BAND_MAX_INSIDE for raw-pattern BID at N=4096. Run
bid_m_normalized_v1 at N=4096 to see what normalized attractor BID looks like at
low M_frac, then use that as the new threshold.

Option 3: Ship bid_m_normalized_v2 at N=4096 with finer M_frac grid (8 points) and
Spearman rho. Import run_one_seed_Mfrac from v1 and just extend the sweep.

The simplest path is Option 3: it's a direct extension of v1 with Spearman rho.

Routing: notes/exp_dev_to_strategy_bid_v6_blocked_2026-05-29.md
