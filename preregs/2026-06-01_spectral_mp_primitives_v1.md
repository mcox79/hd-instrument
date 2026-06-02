# Prereq: spectral_mp_primitives_v1

## Scientific question
3 spectral capabilities: health-check Z-score, deletion-privacy SNR, capacity monitor r.

## Pre-registered bands
HC HARD-PASS: |Z_clean| < 4 AND |Z_corr| > 4 in >= 4/5 seeds.
DP HARD-PASS: SNR ratio in [0.33, 3.0] in >= 4/5 seeds.
CM HARD-PASS: r(M, lambda_max) > 0.98 in >= 4/5 seeds.
MIDDLE: any 2 of 3 pass in >= 2/5 seeds.
HARD-FAIL: all 3 fail in >= 3/5 seeds.
Calibration probe; +-50%.

## N-suffix
No _nN suffix; production N=4096; rationale: spectral test needs clean TW scale.

## Timeout estimate
smoke_wall_s=1.5 (N=1024). FULL N=4096: ceil(1.5 * 1.5 * (4096/1024)^2 * (5/2)) = ceil(225) -> timeout_s=300.

## Date
2026-06-01
