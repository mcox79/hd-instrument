# Prereq: csp_memory_warm_start_v1

## Scientific question
Memory-of-solutions warm-start speedup at rho=0.9. Research predicts ~10x; HP at 2x.

## Pre-registered bands
HARD-PASS: speedup >= 2.0 in >= 4/5 seeds.
MIDDLE: speedup >= 1.5 in >= 3/5 seeds.
HARD-FAIL: speedup < 1.2 in >= 3/5 seeds.
Calibration probe; +-50%. HP at 2.0; HF at 1.2.

## N-suffix
No _nN suffix; production N=2048; rationale: CSP warm-start test.

## Timeout estimate
smoke_wall_s=0.7. ceil(1.5 * 0.7 * (5/2)) = 2.6s -> timeout_s=300.

## Date
2026-06-01
