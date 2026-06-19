# Prereg: caching_eviction_cost_amortized_v1

## Scientific question
Amortized eviction cost: batch rank-K unwrite is O(1) per eviction vs O(N) sequential.

## Pre-registered thresholds
- HARD-PASS: All of A (amort_ratio <= 2.0), B (speedup >= 1.10), C (acc_post >= 0.85).
- HARD-FAIL: HF-A (amort_ratio > 5.0) OR HF-C (acc_post < 0.60).
- MIDDLE: 2/3 cells.

## Calibration note
First batch eviction timing test. Bands +-50% per calibration-probe policy.

## Smoke result
HARD_PASS 3/3: amort_ratio=0.269 (HP<=2.0), speedup=10.680 (HP>=1.10), acc=1.000 (HP>=0.85).
Batch rank-K update 10x faster than sequential. Amortized cost sub-linear (ratio < 1 = improving with K).
Walk-back NOT needed (well above HP on all cells).

## Timeout estimate
Smoke wall: 0.4s. FULL: N=1024, seeds=5 (vs smoke seeds=2).
timeout = ceil(1.5 * 0.4 * 2^1.5 * 2.5) = ceil(1.5*0.4*2.83*2.5) = ceil(4.24) = 5s.
timeout=120s (overhead dominated).

## N-suffix note
No _nN suffix; production N=1024 per rule 3.
