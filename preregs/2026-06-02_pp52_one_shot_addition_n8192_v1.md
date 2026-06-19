# Prereg: pp52_one_shot_addition_n8192_v1

**Date:** 2026-06-02
**Anchor:** pp52_one_shot_addition_n8192_v1
**Queue:** overnight_queue

## Scientific question
At N=8192, M=650 initial patterns: can substrate one-shot-add new patterns with immediate retrievability AND existing patterns retain >= 95% accuracy?

## Pre-registered thresholds
- HP1: new pattern cosine >= 0.90 immediately after one write in >= 4/5 seeds.
- HP2: existing patterns retain >= 95% accuracy after K_NEW=10 additions in >= 4/5 seeds.
- HP3: write wall-time < 1.0 second for any single pattern addition in all seeds.
- HARD-PASS: all 3 HP in >= 4/5 seeds.
- HARD-FAIL: new pattern cosine < 0.70 OR accuracy drops > 10pp.
- MIDDLE: cosine in [0.70, 0.90) OR accuracy drop 5-10pp.

## Prior anchor
pp52_one_shot_addition_n4096_v1 HARD_PASS (cycle 12); N=8192 is production-N extension.

## Timeout estimate
smoke_wall_s ~ 15s at N=1024 2-seed. FULL N=8192/smoke N=1024 = 8x, seeds 5/2 = 2.5x. scaling_exp=2.0 (W matrix N*N):
timeout_s = ceil(1.5 * 15 * 8^2.0 * 2.5) = ceil(3600) = **3600s**.

## GPU memory
W = 8192*8192*4 = 268 MB. Safe on 8 GB GPU.

## PROT-018
anchor _n8192; production N = 8192. Verified.
