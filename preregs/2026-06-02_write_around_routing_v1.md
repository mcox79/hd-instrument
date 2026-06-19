# Pre-registration: write_around_routing_v1

**Date:** 2026-06-02
**Anchor:** write_around_routing_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_write_around_routing_v1.py

## Scientific question (Caching-Policy Expressibility, Tier 1)
Can the substrate implement write-around routing via cosine probe primitive:
route to cache ONLY if similarity >= threshold_high, bypass if <= threshold_low,
defer (grace zone) otherwise?

## Pre-registered thresholds (set BEFORE run)
- HARD-PASS: acc >= 0.95 AND fpr <= 0.05 (routing accurate; low false-positive bypass)
- MIDDLE: acc in [0.80, 0.95) OR fpr in (0.05, 0.20]
- HARD-FAIL: acc < 0.80 OR fpr > 0.20

## Calibration note
Cosine probe is a known substrate primitive (refusal-cert uses same mechanism).
Threshold-based routing should achieve near-perfect acc at low M (< 50% capacity).

## Smoke result
HARD_PASS: acc=1.000, fpr=0.000 (smoke N=1024, THRESHOLD_HIGH=0.7, THRESHOLD_LOW=0.3, 2 seeds)
