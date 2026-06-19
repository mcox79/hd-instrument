# Pre-registration: drift_diffusion_bp_v3

**Date**: 2026-05-27
**Anchor**: drift_diffusion_bp_v3
**Script**: experiments/exp_drift_diffusion_bp_v3.py
**Queue**: remote_cpu_queue
**Parent**: drift_diffusion_bp_v2 (MIDDLE_BAND; smoke only 1 seed N=256)

## Hypothesis

Selective damping gain > 0.05 OR erase_corr > 0.60 in >= 3/5 seeds at N=1024.
Smoke showed damp_gain=0.213 (HP), erase_corr=0.552 (below HP threshold).

## Pre-registered bands

- HARD-PASS: damp_gain > 0.05 in >= 3/5 seeds OR erase_corr > 0.60 in >= 3/5 seeds
- HARD-FAIL: both protocols <= 0 gain in >= 4/5 seeds
- MIDDLE-BAND: one protocol helps in 1-2/5 seeds

Calibration probe: first multi-seed at N=1024. Bands widened +-50%.

## Walk-back gate

Smoke: damp_gain=0.213 (clearly > 0.05 HP), erase_corr=0.552 (< 0.60 HP by 8%).
Effect size d = (0.552 - 0.60) / noise ~ -0.8 (borderline for erase_corr).
Walk-back: maintain planned N=1024, 5 seeds as is (damp_gain clearly passes; erase_corr borderline).

## Timeout estimate

v1 elapsed ~71s for 5 seeds at N=256. N=1024 scales linearly.
timeout_s = ceil(1.5 * 71 * (1024/256)^1.0 * (5/5)) = ceil(426) = 900s.
