# Pre-registration: wave14_moe_cosine_router_v2_k_stress

**Date:** 2026-05-27
**Script:** experiments/exp_wave14_moe_cosine_router_v2_k_stress.py
**Queue:** overnight_queue (GPU; M_total = 128 * 800 = 102400 at K=128; ~2-3h)
**Trigger:** exp_wave14_moe_cosine_router_v1 returns COSINE_ROUTER_HARD_PASS

## Hypothesis

If cosine-dot routing rescues K-scaling at K=16, does it extend all the way to K=128?
Tests 3 router variants: token-choice, expert-choice, Hebbian-anchor token-choice.

## Design

K sweep: {32, 64, 128}, N=4096, M_per_expert=800, 3 seeds.
Expert-Choice variant added (each expert pulls top-C queries).

## Pre-registered bands

- **HARD-PASS (ceiling to K=128):** retention@K=128 >= retention@K=32 * 0.95 AND entropy < 3.0b
- **HARD-FAIL (ceiling below K=64):** retention@K=64 < retention@K=32 - 0.015 OR entropy > 4.0b
- **MIDDLE:** K=64 OK but K=128 degrades > 5%
