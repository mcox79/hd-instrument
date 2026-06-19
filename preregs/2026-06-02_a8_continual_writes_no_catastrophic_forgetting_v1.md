# Prereg: a8_continual_writes_no_catastrophic_forgetting_v1

**Date:** 2026-06-02
**Anchor:** a8_continual_writes_no_catastrophic_forgetting_v1
**Queue:** remote_cpu_queue

## Scientific question
1000+ Hebbian writes without catastrophic forgetting before alpha_c capacity limit.

## Pre-registered thresholds
- HP1: retrieval accuracy >= 0.60 at alpha = 0.05.
- HP2: retrieval accuracy >= 0.60 at alpha = 0.10.
- HP3: cliff slope from alpha=0.10 to 0.15 >= -0.50 per alpha-unit (no sudden cliff).
- HARD-PASS: all 3 HP in >= 4/5 seeds.
- HARD-FAIL: accuracy < 0.30 at alpha = 0.05.
- MIDDLE: HP1+HP2 but cliff detected.

## Timeout estimate
smoke_wall_s = 0 (trivially fast at N=256). FULL N=1024 M_MAX=250 5 seeds:
Estimated 30s per seed (O(N^2*M_MAX) ~ 262M ops). timeout_s = ceil(1.5 * 30 * 1 * 2.5) = **120s**.
