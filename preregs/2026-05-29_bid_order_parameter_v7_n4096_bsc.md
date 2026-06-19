# Pre-Registration: bid_order_parameter_v7_n4096_bsc

Date: 2026-05-29
Anchor: bid_order_parameter_v7_n4096_bsc
Queue: remote_cpu_queue
Script: experiments/exp_bid_order_parameter_v7_n4096_bsc.py
Timeout: 14400s

## Question
Does BID (intrinsic dimensionality) show a collapse at high M_frac (>=8)?
v6 covered M_frac=[0.05..8.0] and found BID outside Hopfield bands. v7 extends to 16.0.

## Config
N=4096, SEEDS=[7,17,23], M_FRACS=[0.05,0.10,0.25,0.50,1.0,2.0,4.0,8.0,12.0,16.0]

## Pre-Registered Thresholds
HARD_PASS: spearman_rho(M_frac, BID) > 0.5 AND BID at M_frac=2 outside Hopfield [lo,hi]
HARD_FAIL: BID flat (range < 0.1 * mean_BID) across all M_fracs (instrumentation failure)
MIDDLE_BAND: BID responds to M_frac but rho < 0.5 or not outside Hopfield band

## Calibration Note
Prior: v6 confirmed BID-M_frac correlation at N=4096. v7 adds high-M collapse check.
Bands +/-50% of v6 empirical values per calibration policy.
