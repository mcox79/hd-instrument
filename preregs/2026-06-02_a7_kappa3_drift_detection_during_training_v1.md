# Prereg: a7_kappa3_drift_detection_during_training_v1

Date: 2026-06-02
Queue: remote_cpu_queue
Timeout: 900s (re-ship; original 300s timed out)

## Scientific question

Can kappa_3 = Tr(W^3)/N, computed inline during training, detect a distributional drift
(IID BSC -> biased patterns, p_bias=0.70) within W <= 50 writes after drift onset?

## Configuration

N=1024, SEEDS=[7,17,23,31,41], M_WARM=50, DETECT_WINDOW=200, N_HUTCHINSON=300

## Pre-registered bands

HARD-PASS (HP):
  HP1: kappa_3 > baseline + 3-sigma within W <= 50 writes after drift onset (all seeds)
  HP2: latency <= 50 writes (same gate framed as latency)
  HP3: false-positive rate < 5% (IID-only run stays below 3-sigma threshold)

HARD-FAIL (HF):
  No detection in 200 writes OR FPR > 20%

MIDDLE-BAND:
  Detection in 51-100 writes OR FPR 5-20%

## Timeout estimate

Smoke wall was ~120s at N=512/SEEDS=2; FULL N=1024, SEEDS=5, N_HUTCHINSON=300.
Estimate: 120s * (1024/512)^2 * (5/2) = 120 * 4 * 2.5 = 1200s. Setting 900s (conservative).
If still times out, increase to 1800s.

## PROT-018

No _nN suffix in anchor name (production N=1024 per rule 3).

## Notes

Re-ship from failed (timed out at 300s). Added "summary" field to metrics dict.
Timeout raised to 900s.
