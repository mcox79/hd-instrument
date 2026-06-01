# Pre-registration: c2_order_param_id_v1_n4096

**Date:** 2026-05-28
**Anchor:** c2_order_param_id_v1_n4096
**Script:** experiments/exp_c2_order_param_id_v1_n4096.py
**Queue:** overnight_queue
**Timeout:** 14400s

## Hypothesis

Basin count increases sharply at beta_c (confirming first-order multi-basin SKAH-M character).

## Configuration

- N: 4096, M_frac=4.0, beta_sweep=[4,8,16,32,64], seeds=[7,17,23], N_INIT=200 random inits
- Smoke: N=1024, beta=[4,8,16], 1 seed

## Pre-registered bands

HARD_PASS: n_basins at beta=16 >= 2x n_basins at beta=8 at >= 2/3 seeds.
HARD_FAIL: n_basins flat (<= 1.1x ratio) across beta sweep.
MIDDLE_BAND: ratio 1.1-2.0x.

Smoke verdict: HARD_FAIL (ratio=1.0, flat at N=1024). Full N=4096 may show different behavior.

## Timeout

ceil(1.5 * 1.0s_smoke * (4096/1024)^2 * 3 * (5/3)) = ceil(120s). Floor=14400. timeout_s=14400.
