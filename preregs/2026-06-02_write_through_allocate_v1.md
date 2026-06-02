# Pre-registration: write_through_allocate_v1

**Date:** 2026-06-02
**Anchor:** write_through_allocate_v1
**Queue:** remote_cpu_queue

## Hypothesis
Dual += (two matrices updated simultaneously) implements zero-overhead write-through.
Mean |sim_fast - sim_slow| < 0.01 (numerically identical retrieval).

## Pre-registered thresholds
- HARD-PASS: mean_delta_sim < 0.01.
- MIDDLE: 0.01 <= delta < 0.05.
- HARD-FAIL: delta >= 0.05.

Note: this is a verification experiment. Both matrices receive identical updates so
delta should be machine-precision ~1e-15.

## Smoke result
N=1024, M=100, 2 seeds: mean_delta_sim=0.00 (machine precision). HARD_PASS. Smoke wall: 1.5s.

## Timeout estimate
Smoke wall: 1.5s / 2 seeds. Full: 5 seeds, M=200. wall = 1.5 * 0.75 * 5 * 2 = 11.25s. timeout=60s.
