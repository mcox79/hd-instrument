# Pre-registration: streaming_prediction_5_consolidation_v1

**Date:** 2026-06-02
**Script:** experiments/exp_streaming_prediction_5_consolidation_v1.py
**Queue:** remote_cpu_queue
**N:** 1024 (no _nN suffix)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (hot_ret=1.0, cold_ret=0.04-0.25, diff=0.74-0.96 at T=20; wall<1s)

## Hypothesis

Wave 4 Streaming Prediction 5: continuous-time replay-free consolidation via differential
weight boosting for hot patterns + exponential decay for cold patterns produces measurable
differential retention: hot patterns remain accessible, cold patterns fade.

## Metrics

- `hot_retention`: mean cosine similarity of hot pattern retrievals
- `cold_retention`: mean cosine similarity of cold pattern retrievals (should decrease)
- `differential`: hot_retention - cold_retention

## Thresholds (pre-registered)

**HARD_PASS:** hot_retention >= 0.85 AND cold_retention <= 0.60 AND differential >= 0.25 (best T)
**HARD_FAIL:** hot_retention < 0.50
**MIDDLE_BAND:** differential in [0.15, 0.25) with hot >= 0.50

## Walk-back assessment

Smoke diff=0.74-0.96 >> 0.25 HP threshold. No walk-back needed.

## Timeout estimate

smoke_wall_s<1, FULL same N, FULL_seeds=5 vs smoke=2, more T_rounds
timeout = ceil(1.5 * 1.0 * 1.0 * 2.5) = 4 -> 300s (conservative)

## Calibration note

First SP5 replay-free consolidation measurement. Novel mechanism.
