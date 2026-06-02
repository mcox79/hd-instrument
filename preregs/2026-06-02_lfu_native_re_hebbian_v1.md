# Pre-registration: lfu_native_re_hebbian_v1

**Date:** 2026-06-02
**Anchor:** lfu_native_re_hebbian_v1
**Queue:** remote_cpu_queue

## Hypothesis
Re-Hebbian writes on READ implement native LFU: patterns re-written k times accumulate
weight proportional to (1+k), discriminating by raw dot product xi^T W xi.

## Pre-registered thresholds
- HARD-PASS: discrimination_ratio (raw dot product) >= 3.0 at k_reads=10.
- MIDDLE: 1.5 <= disc_ratio < 3.0.
- HARD-FAIL: disc_ratio < 1.5 at k=10.

Calibration probe: no prior empirical anchor. Theory predicts 11x at k=10; HP=3.0 is 73% below theory.

## Smoke result
N=1024, M=50, 2 seeds, k_reads=[1,5,10,20]:
- disc_ratio at k=10: 8.84 (theory 11x; HARD_PASS HP>=3.0)
- Monotone in k: True (k=1: 1.94, k=5: 5.31, k=10: 8.84, k=20: 14.29)
- Smoke wall: 3.3s

## Timeout estimate
Smoke wall: 3.3s / 2 seeds = 1.65s/seed.
Full: 5 seeds, same config. wall = 1.5 * 1.65 * 5 = 12.4s. timeout=60s.
