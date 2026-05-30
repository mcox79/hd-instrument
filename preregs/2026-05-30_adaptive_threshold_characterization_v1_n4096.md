# Prereg: adaptive_threshold_characterization_v1_n4096

Date: 2026-05-30
Anchor: adaptive_threshold_characterization_v1_n4096
Script: experiments/exp_adaptive_threshold_characterization_v1_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018)

## Question

Per (beta in [4, 10, 32] x M_frac in [1, 4, 16]) cell: what is the empirical
optimal KF-1 hallucination threshold (max Youden's J statistic over the 7
candidate threshold values)? How does it compare to the closed-form framework
prediction `predicted_threshold(beta, M_frac) = sigmoid(beta*(M_frac/4 - 1))`?

## Pre-registered bands

- **HARD_PASS**: empirical-vs-prediction within +/-20% in >= 7 of 9 cells
  (`mean_rel_err <= 0.20` in >= 7/9 cells).
- **HARD_FAIL**: empirical-vs-prediction off by >= 50% in >= 6 of 9 cells.
- **MIDDLE_BAND**: otherwise.

## Formula self-tests (verified in `_instrumentation_selftest`)

- `predicted_threshold(4, 1)` ~ 0.047
- `predicted_threshold(10, 4)` = 0.5 (sigmoid(0))
- `predicted_threshold(32, 16)` = 0.99 (clipped)

## Sweep

- N=4096; 9-cell grid * 3 seeds * 7 threshold values.

## Timeout estimate

User specified 21600s. scaling_exp=1.5.
