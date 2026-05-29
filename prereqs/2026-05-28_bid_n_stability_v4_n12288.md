# Pre-registration: bid_n_stability_v4_n12288

**Date:** 2026-05-28
**Anchor:** bid_n_stability_v4_n12288
**Queue:** overnight_queue
**Script:** experiments/exp_bid_n_stability_v4_n12288.py
**Parent:** bid_n_stability_v3_n16384 (TIMEOUT; zero metrics)

## Hypothesis

BID scaling-law continues at N=12288 (intermediate N between v2 N=8192 and v3 N=16384).
v3 timed out at N=16384 (M^2 cost blowup). v4 uses N=12288 to avoid the blowup.
Expected BID(N=12288) = BID(8192) * 1.28 ~ [179, 211] based on v2 mean BID ~ 140-165.

## Protocol

N in {8192, 12288}, 3 seeds each. TwoNN BID estimator. No Kerdock (no power-of-2 requirement
for BSC/random atoms used by this script). Multi-scale smoke at N_SMOKE and N_SMOKE*4.

## Pre-registered bands

HARD_PASS: BID(N=12288) in [110, 250] AND outside all Hopfield-class bands
  (normalized BID > BAND_MAX_INSIDE=0.55 OR BID >= 50 absolute).

HARD_FAIL: BID(N=12288) inside Hopfield class band.

MIDDLE_BAND: BID outside bands but outside [110, 250] corridor.

## Formula self-tests

1. BID geometric interpolation: BID(12288) = BID(8192) * (12288/8192)^log2(1.54) = BID(8192) * 1.28.
2. interp_bid(100, 8192, 12288) = 128. Expected increase: positive.
3. N=12288 is NOT power-of-2; Kerdock not used. SAFE.

## Timeout estimate

N=8192 (3 seeds): 3 * 700s = 2100s. N=12288 (3 seeds): 3 * 1575s = 4725s.
Total: 6825s. Safety 1.5x: 10238s -> 10800s. Exceeds 7200s (flagged for visibility).
timeout_s = 21600 (PROT-019 _n12288 threshold not specified; using _n8192 floor as conservative)

## N-suffix binding (PROT-018)

_n12288 suffix; production N includes N=12288 as primary new cell. VERIFIED.
N=12288 is NOT a power of 2. Kerdock codebook construction NOT called. SAFE.
