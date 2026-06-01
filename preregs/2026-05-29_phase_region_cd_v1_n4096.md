# Pre-registration: phase_region_cd_v1_n4096

**Date:** 2026-05-29
**Anchor:** phase_region_cd_v1_n4096
**Script:** experiments/exp_phase_region_cd_v1_n4096.py
**Queue:** overnight_queue
**Timeout:** 14400s

## Hypothesis

At beta=64 (above beta_c~10-16):
- Region C (M_frac=4, below M_c): retention approaches 1.0 (ferromagnetic stabilization).
- Region D (M_frac=12, above M_c): retention remains low despite high beta (M_c boundary holds).

## Configuration

- N: 4096, beta=64.0, seeds=[7,17,23,31,41]
- Region C: M_frac=4.0 (below M_c), Region D: M_frac=12.0 (above M_c)
- Smoke: N=1024, 1 seed -> ret_C=1.0, ret_D=0.30

## Pre-registered bands (calibration probe; first beta=64 measurement)

Per calibration-probe policy: bands set +/-50% around theoretical prediction.

Region C (ferromagnet): HARD_PASS_C: mean_retention >= 0.70 at >= 3/5 seeds.
HARD_FAIL_C: mean_retention < 0.35.

Region D (overcapacity): HARD_PASS_D: mean_retention < 0.30 at >= 3/5 seeds.
HARD_FAIL_D: mean_retention >= 0.60.

Joint HARD_PASS: both regions meet individual criteria (phase boundary confirmed).

Smoke: MIDDLE_BAND at N=1024 (1 seed only; C met at 1/1, D met at 0/1 borderline=0.30).
Full run with 5 seeds expected to confirm.

## Timeout

ceil(1.5 * 0.21s_smoke * (4096/1024)^1.5 * 5) = 13s. Floor=14400. timeout_s=14400.
