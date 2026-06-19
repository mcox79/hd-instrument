# Pre-registration: wave14_moe_cosine_router_v1

**Date:** 2026-05-27
**Script:** experiments/exp_wave14_moe_cosine_router_v1.py
**Queue:** remote_cpu_queue
**ETA:** ~2500s (~40 min CPU)

## Hypothesis

LSH gating entropy is the sole source of K-scaling degradation in MoE SHIFT (M2_DOMINANT verdict from wave14_moe_shift_K_perarm_v1). Replacing LSH with cosine-dot gating using fixed BSC anchors (substrate-native operation) should reduce routing entropy and preserve retention at high K.

Source: notes/exp_dev_handoff_moe_learned_router_probe_2026-05-27.md
Baseline: data/exp_wave14_moe_shift_K_perarm_v1/metrics.json (M2_DOMINANT)

## Design

- K sweep: {4, 8, 16, 32}
- N = 4096 (substrate default)
- M_per_expert = 800 (same as K_perarm baseline)
- 3 seeds
- Router: cosine-dot top-1 with fixed BSC anchor per expert

## Pre-registered bands (from handoff)

- **HARD-PASS:** routing_entropy@K=16 < 2.0b AND retention@K=16 >= retention@K=4 - 0.005
- **HARD-FAIL:** routing_entropy@K=16 > 3.0b OR retention@K=16 < retention@K=4 - 0.015
- **MIDDLE:** entropy in [2.0, 3.0b] or retention delta in [0.005, 0.015]

## Autonomy given to exp_dev

- Router type: token-choice (argmax), Expert-Choice if batch available
- Anchor init: random BSC (this run); Hebbian-anchor as fallback if HARD-FAIL
