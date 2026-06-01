# Pre-registration: moe_capacity_aware_router_v1_n4096

Date: 2026-05-28
Queue: remote_cpu_queue
Script: experiments/exp_moe_capacity_aware_router_v1_n4096.py
N: 4096
Seeds: [7, 17, 23, 31, 41]
K_sweep: [4, 8, 16, 32]
M_budget_per_expert: 800

## Hypothesis
Capacity-aware routing (route to least-loaded expert) achieves retention that scales with K under fixed total capacity. Routing must be capacity-aware not identity-aware (meta-learning lock from v266 HARD_FAIL).

## Thresholds (pre-registered)

HARD_PASS: ret[K=32] >= 0.85 AND ret[K=32] >= ret[K=4] * 0.90, across >= 3/5 seeds
HARD_FAIL: ret[K=32] < 0.50 for majority seeds (routing fails at high K)
MIDDLE_BAND: K-scaling shows positive trend but below HARD_PASS floor

## Calibration basis
Smoke result: K=16 ret=0.911 at 1 seed. Capacity-aware fill_frac routing should maintain high retention even at K=32 by keeping experts balanced. HP ret >= 0.85 = smoke_result - 7% margin.

## Timeout
3600s (remote CPU; 4 K_sweep x 5 seeds = 20 cells; ~1h budget)
