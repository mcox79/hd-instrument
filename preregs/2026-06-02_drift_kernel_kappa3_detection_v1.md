# Pre-registration: drift_kernel_kappa3_detection_v1

**Date:** 2026-06-02
**Script:** experiments/exp_drift_kernel_kappa3_detection_v1.py
**Queue:** remote_cpu_queue
**N:** 2048 (no _nN suffix)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (mean_W=1.5 for all eps values)

## Hypothesis

The kappa_3 monitor detects gradual drift (each write pattern = sign(cos(theta)*xi_ref + sin(theta)*xi_perp) with theta += eps/write) within W <= 100 writes at eps=1e-3. Faster drift (larger eps) detected sooner.

## Metrics

- `detection_W`: writes until kappa_3 flags 3-sigma deviation per eps value
- `detection_W_target`: detection_W at eps=1e-3 (primary metric)

## Thresholds (pre-registered)

**HARD_PASS:** detection_W(eps=1e-3) <= 100
**HARD_FAIL:** detection_W(eps=1e-3) > 200
**MIDDLE_BAND:** detection_W(eps=1e-3) in (100, 200]

eps sweep: [1e-4, 1e-3, 1e-2, 1e-1] for full run; monotone relationship expected (higher eps = faster detection).

## Timeout

600s (from: ~1s per seed per eps * 4 eps * 5 seeds * 1.5 = 30s estimated; generous cap)
