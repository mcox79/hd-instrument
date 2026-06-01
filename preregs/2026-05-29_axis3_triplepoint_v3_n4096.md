# Pre-Registration: axis3_triplepoint_v3_n4096

Date: 2026-05-29
Anchor: axis3_triplepoint_v3_n4096
Queue: remote_cpu_queue
Script: experiments/exp_axis3_triplepoint_v3_n4096.py
Timeout: 14400s

## Question
Do 6 diverse (M_frac, beta) operating points show sign divergence in perturbation response?
v3 extends v2's 3-point grid to 6 points including high-beta extreme.

## Config
N=4096, OPERATING_POINTS=[(4.0,8.0),(8.0,4.0),(4.0,16.0),(12.0,8.0),(8.0,16.0),(4.0,32.0)], SEEDS=[7,17,23]

## Pre-Registered Thresholds
HARD_PASS: >= 1 operating point with sign divergence AND max|delta_ret| >= 0.15
HARD_FAIL: max|delta_ret| < 0.05 at all operating points (insensitive substrate)
MIDDLE_BAND: max|delta_ret| >= 0.05 but no sign divergence or < 0.15

## Calibration Note
Prior: v2 confirmed sign divergence at 3 operating points. v3 widens the grid.
Smoke HARD_PASS: n_sign_div=1/2, max_delta=0.2600 > HP_DELTA_MIN=0.15.
WALK-BACK GATE: d=0.2600/0.15=1.73 > 1.0 (no doubling needed).
