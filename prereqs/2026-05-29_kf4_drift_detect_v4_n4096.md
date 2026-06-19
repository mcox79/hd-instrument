# Pre-registration: kf4_drift_detect_v4_n4096

**Date:** 2026-05-29
**Anchor:** kf4_drift_detect_v4_n4096
**Queue:** overnight_queue
**Script:** experiments/exp_kf4_drift_detect_v4_n4096.py
**Parent:** kf4_drift_detect_v3_n4096 (HARD_FAIL gap=0)

## Hypothesis

KF-4 drift detection (posterior-entropy rescue) has detectable signal at N=4096 when
N_DRIFT_STEPS=200 (20x more drift than v3). v3 used 100 steps and found gap=0.

## Protocol

3 seeds x 2 M_fracs ([2.0, 8.0] x N) x N=4096. N_DRIFT_STEPS=200.
Accuracy drop measurement after drift perturbation.

## Pre-registered bands

HARD_PASS: mean_acc_drop >= 0.05 at any M_frac, >= 2/3 seeds.
HARD_FAIL: mean_acc_drop < 0.005 across ALL M_fracs ALL seeds.
MIDDLE_BAND: mean_acc_drop in [0.005, 0.05).

## Formula self-tests

1. N=4096 (PROT-018 binding). N=4096 log2=12 EVEN -> Kerdock SAFE.
2. noise_fraction = N_DRIFT_STEPS / M. At M_frac=2.0: 200/8192 = 0.024.
3. Expected acc_drop ~ noise_fraction ~ 0.024. HP=0.05 is 2x this.

## Timeout estimate

Smoke ~5s at N=1024. Full: ceil(1.5 * 5 * 8 * 3 * 2) = 360s. Safety x4: 1440s.
Floor _n4096 = 14400s. timeout_s = 14400
