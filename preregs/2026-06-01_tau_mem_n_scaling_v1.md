# Prereg: tau_mem_n_scaling_v1

**Filed:** 2026-06-01
**Anchor:** tau_mem_n_scaling_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_tau_mem_n_scaling_v1.py

## Hypothesis

tau_mem = (1/gamma) * log(1 + N*gamma/(2*lambda)) with gamma=0.01, lambda=0.001
holds empirically across N in {8192, 16384, 32768}.

## Pre-registered bands

- HARD-PASS: R^2 > 0.95 on log-log fit AND C_mean in [0.50, 1.50] (+-50% of theory).
- MIDDLE: 0.85 <= R^2 <= 0.95 OR C in [0.33, 3.0].
- HARD-FAIL: R^2 < 0.85 OR C outside [0.33, 3.0].

Calibration probe: no prior empirical anchor. Bands +-50% per policy.

## Theoretical predictions

N=8192: tau_theory ~ 376. N=16384: tau_theory ~ 443. N=32768: tau_theory ~ 510.

## Timeout estimate

Scalar ODE simulation: <<1s. timeout_s = 600 (safety factor for file I/O).

## N-suffix note

No _nN suffix. N-scaling sweep across {8192, 16384, 32768}.
