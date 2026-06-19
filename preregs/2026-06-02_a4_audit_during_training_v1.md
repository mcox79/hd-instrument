# Pre-registration: a4_audit_during_training_v1

DATE: 2026-06-02
QUEUE: remote_cpu_queue
ANCHOR: a4_audit_during_training_v1

## Scientific question
Can kappa_3 (Tr(W^3)/N, Hutchinson estimator) detect an adversarial pattern injection
within <= 50 writes, at 3-sigma above baseline, with FPR < 5%?

## Hard-pass (pre-registered)
HP1: anomaly detected (kappa_3 exceedance >= 3-sigma threshold)
HP2: detection latency <= 50 writes
HP3: FPR < 5% (false positive rate on baseline-only windows)

## Hard-fail (pre-registered)
HF1: FPR > 20%
HF2: detection latency > 100 writes

## Middle band
2/3 HP conditions met

## Smoke result
HARD_PASS: all 3 HP conditions met (N=512 smoke, 2 seeds).
detected=2/2, latency=1 write, fpr=0.000.

## P_deflated: 0.55 (calibration probe; novel capability; no direct prior benchmark)

## Production config
N=1024, M_CLEAN_BEFORE=50, M_CLEAN_AFTER=50, N_HUTCHINSON=300, N_BASELINE_RUNS=20, SEEDS=[7,17,23,31,41]

## Timeout estimate
~27s (1.5 * 1.8s * 4x * 2.5x_seeds)
