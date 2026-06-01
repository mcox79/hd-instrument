# Pre-registration: t2_codebook_boundary_v1_n4096

Date: 2026-05-28
Queue: overnight_queue
Script: experiments/exp_t2_codebook_boundary_v1_n4096.py
N: 4096
Seeds: [7, 17, 23, 31, 41]
M_frac: 2.0
C_fracs: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]

## Hypothesis
Retention increases monotonically with codebook fraction c (more structured patterns = better retrieval). Slope of retention vs c is positive and significant.

## Thresholds (pre-registered)

HARD_PASS: slope >= 0.10 AND total_var >= 0.05, across >= 3/5 seeds
HARD_FAIL: slope < 0.02 OR total_var < 0.01 for majority of seeds
MIDDLE_BAND: all other outcomes

## Calibration basis
Smoke result: slope=0.138, total_var=0.165 at N=4096, M_frac=2.0, 1 seed.
First measurement (calibration probe). HP_SLOPE_MIN=0.10 set +-50% below smoke slope=0.138 (0.138 * 0.72 ~ 0.10 conservative floor). HARD_FAIL at 0.02 (7x below smoke).

## Timeout
14400s (PROT-019 tier: _n4096 >= 14400s)
