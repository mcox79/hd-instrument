# Pre-registration: bid_m_normalized_v2_n4096

Date: 2026-05-28
Queue: remote_cpu_queue
Script: experiments/exp_bid_m_normalized_v2_n4096.py
N: 4096
Seeds: [7, 17, 23]
M_fracs: [0.025, 0.05, 0.125, 0.5, 2.0, 5.0, 10.0, 15.0]

## Hypothesis
BID (TwoNN intrinsic dimension) remains outside static-Hopfield bands (BAND_MAX_INSIDE=0.55) across all M_fracs. BID shows monotone increase with M_frac in the over-capacity regime (M_frac > 1.0).

## Thresholds (pre-registered)

HARD_PASS: BID > 0.55 for ALL M_fracs across >= 2/3 seeds; monotone increasing trend in BID vs M_frac for M_frac >= 0.5
HARD_FAIL: BID <= 0.55 for any M_frac at majority seeds
MIDDLE_BAND: BID outside bands but trend unclear

## Calibration basis
BID v1 result: BID in 20-200 range (TwoNN absolute); BAND_MAX_INSIDE=0.55 means any positive TwoNN value is outside Hopfield bands. Smoke: BID=48.01, 24.47, 37.23 for 3 M_fracs all >> 0.55.
Wider M-range sweep to characterize trajectory from near-zero M (M_frac=0.025) through heavy overload (M_frac=15.0).

## Timeout
3600s (remote CPU; TwoNN estimation on 4096-dim, 8 M_fracs, 3 seeds; ~1h budget)
