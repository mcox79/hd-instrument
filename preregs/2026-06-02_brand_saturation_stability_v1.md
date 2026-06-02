# Pre-registration: brand_saturation_stability_v1

**Date:** 2026-06-02
**Script:** experiments/exp_brand_saturation_stability_v1.py
**Queue:** remote_cpu_queue
**N:** 2048 (no _nN suffix)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (acc=1.0 at alpha=0.10, 0.20; wall=24s/seed at alpha=0.20)

## Hypothesis

Brand-incremental SVD confirmed HP'd at alpha < 0.10 (v333). Extension to alpha >= 0.10
(saturation region): accuracy remains >= 0.97 because Brand is algebraically exact up to
floating-point precision, which is independent of load factor.

## Metrics

- `accuracy`: 1 - ||W_batch - W_brand||_F / ||W_batch||_F per alpha

## Thresholds (pre-registered)

**HARD_PASS:** accuracy >= 0.97 for ALL alpha in {0.10, 0.20, 0.40, 0.80}
**HARD_FAIL:** accuracy < 0.95 for any alpha
**MIDDLE_BAND:** all acc >= 0.95 but some < 0.97

## Timeout estimate

smoke_wall_s=24 (alpha=0.20), FULL 4 alpha values vs smoke 2, FULL_seeds=5 vs smoke=2
timeout = ceil(1.5 * 24 * (4/2) * 2.5) = ceil(180) -> 900s

## Calibration note

First direct Brand saturation measurement at alpha >= 0.10. Bands set per calibration probe
policy (+-50% of acc drop). Since v333 showed acc=1.0 at alpha<0.10 (algebraic), drop budget
is generous.
