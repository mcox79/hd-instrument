# Prereg: wave14f_hippo_eigenspace_v1

**Date:** 2026-05-26
**Parent:** wave14f_hippo_init_w_v1 P1=HARD_FAIL, P3=HARD_PASS (spectral_corr=0.993)
**Question:** Does a TIME-VARYING HiPPO spectral-tracking update improve chain-recall depth?

## Hypothesis
P3=HARD_PASS means post-training W naturally has HiPPO-like eigenstructure.
Rescue #3: continuously bias W toward HiPPO eigenspace during training via spectral rotation update.
This may improve convergence on temporal depth tasks.

## Design
- N=1024; 3 seeds; 15 epochs; d_max=100
- Arm A: Hebbian + HiPPO spectral rotation (lr=0.01)
- Arm B: vanilla Hebbian
- CPU (remote_cpu_queue); ~30-60 min

## Pre-registered bands
- **HARD_PASS**: depth_at_half ratio (A/B) >= 1.5 AND baseline depth_at_half >= 5
- **HARD_FAIL**: ratio < 1.0 (tracking hurts)
- **MIDDLE_BAND**: ratio in [1.0, 1.5)
- **INSTRUMENTATION_FAIL**: baseline depth_at_half < 2

## Calibration
First empirical test of spectral-tracking update. Bands per calibration-probe policy (±50%).
