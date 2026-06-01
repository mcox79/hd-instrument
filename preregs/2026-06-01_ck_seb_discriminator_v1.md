# Prereg: ck_seb_discriminator_v1

**Filed:** 2026-06-01
**Anchor:** ck_seb_discriminator_v1
**Queue:** overnight_queue
**Script:** experiments/exp_ck_seb_discriminator_v1.py

## Hypothesis

The substrate is in the CK (Cugliandolo-Kurchan) class: parametric chi vs C plot
shows a KINK at q_EA, and long-time C(t,t_w) shows a detectable plateau below 1.

## Pre-registered bands

- HARD-PASS: chi-C slope changes by >= 0.30 at some C* in [0.3, 0.8] in >= 4/5 seeds
             AND q_EA < 0.80 * C(t_w, t_w) in >= 4/5 seeds (above alpha_c=0.138).
- MIDDLE: kink visible but slope_change in [0.10, 0.30] OR q_EA in [0.80, 0.95].
- HARD-FAIL: straight line (slope_change < 0.10) AND q_EA absent (plateau >= 0.95) in >= 4/5 seeds.

P_deflated(CK_class) = 0.40-0.47.
Calibration probe: no prior CK discriminator anchor. Bands +-50% per policy.

## Design

N=2048 (GPU overnight_queue). alpha in {0.05, 0.15} (below/above alpha_c).
t_w in {10, 100, 1000}. 500 steps per window. Beta=10. 5 seeds (smoke: 2).

## OOM pre-check

W at N=2048: 2048^2 * 4 = 16 MB. Well within 8 GB GPU.

## Timeout estimate

smoke_wall_s ~ 60s. Full: 5 seeds * 2 alpha * 1500 sweeps ~ 150s.
timeout_s = ceil(1.5 * 150) = 225 -> 300 (floor).

## N-suffix note

No _nN suffix. Production N = 2048; CK discriminator (N^2 matrix fits 8GB GPU).
