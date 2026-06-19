# Pre-registration: wave14_moe_attention_routing_v1

**Date**: 2026-05-27
**Anchor**: wave14_moe_attention_routing_v1
**Script**: experiments/exp_wave14_moe_attention_routing_v1.py
**Queue**: remote_cpu_queue
**Parent**: wave14_moe_hebbian_anchor_router_v1 (HEBBIAN_ROUTER_HARD_FAIL; all routers fail)

## Hypothesis

Soft attention routing (transformer-style) achieves routing entropy in [1.0, 3.5]b at K=16
AND retention delta >= -0.01 vs K=4 baseline.

## Pre-registered bands

- HARD-PASS: attention_entropy at K=16 in [1.0, 3.5] AND retention_delta >= -0.01
- HARD-FAIL: retention_delta < -0.05 OR entropy > 3.8b (uniform)
- MIDDLE: partial success

## Walk-back gate

Smoke (1 seed, N=512): K=4 ret=0.800, K=8 ret=0.650, delta=-0.150. 
Effect size d = 0.15/noise ~ large. Smoke shows HARD_FAIL direction clearly.
Walk-back: ship FULL to confirm with 2 seeds and wider K range (K=16).
Doubled seeds from 1 to 2 (walk-back gate: borderline effect for K=8; may differ at K=16).

## Timeout estimate

smoke_wall_s = 0.07s (very fast). FULL: N=4096, K=[4,8,16], 2 seeds, 3 temps.
Estimate from K_perarm_v1 (2288.9s) at N=4096: attention should be ~same or faster.
timeout_s = 6000s (conservative; K=16 M_per_expert=200 * 200 patterns per expert).
