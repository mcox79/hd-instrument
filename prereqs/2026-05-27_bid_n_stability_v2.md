# Pre-registration: bid_n_stability_v2

**Filed:** 2026-05-27  
**Script:** experiments/exp_bid_n_stability_v2.py  
**Queue:** remote_cpu_queue  
**Timeout:** 5400s

## Scientific question

Does BID (binary intrinsic dimensionality via TwoNN) remain outside all known
static Hopfield class bands at production-scale N in {4096, 8192}?

v247 (bid_substrate_probe_v1) HARD_PASSed HP3 at N=512-2048 (BID=46.95+-5.90,
sigma_margin=7.54). bid_order_parameter_v4_full TIMED OUT at N=8192 (default 1500s).
This probe fills the gap with proper --timeout 5400.

## Parent verdict

- bid_substrate_probe_v1 (v247): HARD_PASS at N=512-2048, bid=46.95+-5.90
- bid_order_parameter_v4_full: TIMEOUT at 1500s (partial: N=4096 3-seed completed OK)

## Pre-registered thresholds

HARD_PASS: BID_mean at N=4096 AND N=8192 BOTH outside all 3 Hopfield class bands
  (BAND_MAX_INSIDE=0.55; BID >> 2.0 per v247), AND HP3 N-drift < 5% as N doubles.
  Confirms non-static-Hopfield classification holds at production scale.

HARD_FAIL: BID_mean at any N in {4096, 8192} falls inside any Hopfield class band
  (0.15 <= BID <= 0.55 natural units).

MIDDLE_BAND: BID outside bands but HP3 N-drift >= 5% (unstable N-scaling).

## Formula self-tests (from script)

1. BID at N=512: ~48.69 (consistent with v247 range)
2. n_drift formula: |BID(N_hi) - BID(N_lo)| / BID(N_lo)
3. Verdict logic: any_inside_band gate, HP3 gate, sigma_margin gate

## Justification

v247 priority 1 (cheapest CPU drill, ~30min). Resolves open interpretive question:
is the BID outside-Hopfield-bands observation an N-dependent finite-N artifact, or
does the substrate genuinely sit outside all known static-phase classes at production
scale? This directly supports the non-equilibrium stat-mech row 🟢 45-60%.

## Production config

N_VALUES_FULL=[4096, 8192], M_FRAC=0.125, SEEDS_FULL=[7,17,23], timeout=5400s
