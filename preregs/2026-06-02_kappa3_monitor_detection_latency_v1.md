# Pre-registration: kappa3_monitor_detection_latency_v1

**Date:** 2026-06-02
**Script:** experiments/exp_kappa3_monitor_detection_latency_v1.py
**Queue:** remote_cpu_queue
**N:** 2048 (no _nN suffix)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (mean_detection_W=1.8, all injection types detected in 1-4 writes)

## Hypothesis

The kappa_3 = Tr(W^3)/N Hutchinson monitor detects distribution shifts within W <= 50 writes with FP_rate < 0.10. Tests 5 injection types: gaussian_sign, structured, anti_correlated, all_ones, uniform_random.

## Metrics

- `detection_W`: writes until kappa_3 deviates > 3-sigma from baseline per injection type
- `mean_detection_W`: mean over injection types
- `FP_rate`: false positive rate during pre-injection phase
- `all_detected`: boolean (all injection types detected within W_max=50)

## Thresholds (pre-registered)

**HARD_PASS:** mean_detection_W <= 50 AND FP_rate < 0.10 AND all_detected=True
**HARD_FAIL:** mean_detection_W > 100 OR FP_rate >= 0.50
**MIDDLE_BAND:** mean_detection_W in (50, 100], FP_rate < 0.50

## Timeout

600s (from: ~2s per seed per injection type * 5 types * 5 seeds * 1.5 = 75s estimated; generous cap)
