# Pre-registration: streaming_brand_gram_refresh_v1

**Date:** 2026-06-02
**Script:** experiments/exp_streaming_brand_gram_refresh_v1.py
**Queue:** remote_cpu_queue
**N:** 2048 (no _nN suffix)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (min_acc=1.0, t=0.00s; algebraic identity in float64)

## Hypothesis

Incremental Brand Gram refresh G_incr matches batch G_batch with accuracy >= 0.98 for all K writes (K in 1..50). The identity is algebraic in float64, so float numerical accuracy is the only failure mode.

## Metrics

- `accuracy`: 1 - ||G_batch - G_incr||_F / ||G_batch||_F per K write
- `min_acc`: minimum accuracy across K values

## Thresholds (pre-registered)

**HARD_PASS:** min_acc >= 0.98 for ALL K in sweep
**HARD_FAIL:** min_acc < 0.95 for any K
**MIDDLE_BAND:** min_acc in [0.95, 0.98)

## Timeout

120s (algebraic identity; sub-second per seed)
