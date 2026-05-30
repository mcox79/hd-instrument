# Prereg: n_scaling_modern_hopfield_v1_n16384

Date: 2026-05-30
Anchor: n_scaling_modern_hopfield_v1_n16384
Script: experiments/exp_n_scaling_modern_hopfield_v1_n16384.py
N-suffix: _n16384 -> production N = 16384 (PROT-018 binding)

## Question

At N=16384, what is `max_M_at_95_recall` and does it match the linear-capacity
prediction (`N/4`), exponential modern-Hopfield prediction (`>> 2N`), or sit
between?

## Pre-registered bands

- **HARD_PASS**: `max_M_at_95_recall > 2*N = 32768`
  (exponential bend detected; substrate beats outer-product ceiling)
- **HARD_FAIL**: `max_M_at_95_recall in [0.8 * N/4, 1.2 * N/4] = [3277, 4915]`
  (linear extends; no bend)
- **MIDDLE_BAND**: otherwise (slope change but not exponential)

Calibration-probe policy: no prior empirical anchor at N=16384; bands at ±20%
of linear baseline for HF and +100% for HP.

## Sweep

- M values: [N/8, N/4, N/2, N, 2N, 4N, 8N, 16N] = [2048, 4096, 8192, 16384,
  32768, 65536, 131072, 262144]
- Seeds: 3 (memory cost constraint at N=16384, 16N)

## Timeout estimate

User-explicit 86400s authorization for battery-class N=16384 sweep.
scaling_exp=2.0 (matrix-matmul dominant).

## N-suffix

`_n16384` binds production N = 16384. Smoke runs at N=1024. queue_add.py
exit-6 validator checks the `N = 16384` literal in the script.
