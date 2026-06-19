# Pre-registration: hippocampal_nonrecip_replay_v1

**Date:** 2026-06-01
**Anchor:** hippocampal_nonrecip_replay_v1
**Script:** experiments/exp_hippocampal_nonrecip_replay_v1.py
**Queue:** remote_cpu_queue
**N:** 1024

## Hypothesis

Non-reciprocal Hebbian weight matrix W = sum_{t=0}^{M-2} outer(xi_{t+1}, xi_t) / N
encodes temporal order. Replaying from pattern t goes forward in the sequence
more than backward. forward_bias = (n_forward - n_backward) / total steps.
Expected bias > 0.50 based on directed graph theory.

## Pre-registered thresholds (calibration probe, first empirical anchor)

±50% of theoretical prediction 0.50:
- **HARD-PASS:** mean forward_bias > 0.25 (50% of theoretical)
- **HARD-FAIL:** mean forward_bias < -0.10 (net backward or random)
- **MIDDLE-BAND:** mean forward_bias in [-0.10, 0.25]

## Smoke result (2026-06-01)

Smoke HARD_PASS: mean_bias=0.600 >> HP=0.25. Wall ~6.8s at 2 seeds.

## Cap-map rows

- Hippocampal phenomena: non-reciprocal replay directionality
- Temporal sequence storage in substrate
