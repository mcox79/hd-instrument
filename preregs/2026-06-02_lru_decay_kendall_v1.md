# Pre-registration: lru_decay_kendall_v1

**Date:** 2026-06-02
**Anchor:** lru_decay_kendall_v1
**Queue:** remote_cpu_queue

## Hypothesis
Exponential decay (gamma=0.95) before each Hebbian WRITE implements native LRU.
Kendall-tau between write-order and retrieval-similarity rank >= 0.90 at largest M tested.

## Pre-registered thresholds
- HARD-PASS: Kendall-tau >= 0.90 at largest M value.
- MIDDLE: 0.60 <= tau < 0.90.
- HARD-FAIL: tau < 0.60.

Calibration probe: no prior empirical anchor. Theory predicts strong monotone recency ordering.

## Smoke result
N=1024, gamma=0.95, M_sweep=[10, 20, 40], 2 seeds:
- tau at M=40: 0.882 (MIDDLE -- within 20% of HP=0.90)
- Walk-back gate triggered: FULL uses 5 seeds (up from 2) to increase power.

## Walk-back gate
Smoke tau at M=40: 0.882. HP=0.90. Within 20% of HP (0.90 * 0.80 = 0.72 < 0.882 < 0.90).
Walk-back: double FULL seeds (5 seeds, same M). If mean tau across seeds >= 0.90, HARD_PASS.

## Timeout estimate
Smoke wall: 1.2s / 2 seeds = 0.6s/seed.
Full: 5 seeds, M_sweep=[10,20,40,80]. wall = 1.5 * 0.6 * 5 * (4/3) = 6s. timeout=60s.
