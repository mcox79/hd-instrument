# Pre-registration: moe_fixed_total_capacity_K_sweep_v1_n4096

**Date:** 2026-05-28
**Anchor:** moe_fixed_total_capacity_K_sweep_v1_n4096
**Script:** experiments/exp_moe_fixed_total_capacity_K_sweep_v1_n4096.py
**Queue:** remote_cpu_queue
**Routing note:** strategy_request_to_exp_dev_v260_moe_fixed_total_capacity_K_sweep_2026-05-28.md

## Hypothesis

Under fixed total capacity (M_total=3200), retention does NOT degrade as K increases from 4 to 16.
If true, MoE K-scaling collapse was an entropy routing artifact, NOT a substrate capacity limit.
K=16 design point LIFTS TO ACTIVE.

## Configuration

- N = 4096 (PROT-018 binding via _n4096 suffix)
- M_total = 3200 (fixed; = 800 * 4 = K=4 baseline capacity)
- K_sweep = [4, 8, 16, 32]
- M_per_expert at each K: {4:800, 8:400, 16:200, 32:100}
- Seeds = [7, 17, 23] (3-seed)
- Router: gradient-trained (same as moe_gradient_router_v1)

## Pre-registered thresholds (HF1/HF2/HF3)

**HARD_PASS_NO_CEILING:** ret_delta(K16 vs K4) >= -0.05 AND ret_K16 >= 0.70.
  Interpretation: MoE K-scaling was entropy artifact; K=16 unblocked.

**HARD_FAIL_CEILING:** ret_delta < -0.15 AND ret_K16 < 0.50.
  Interpretation: TRUE K-scaling ceiling; retention degrades with K under fixed total capacity.

**MIDDLE_BAND:** ret_delta in (-0.15, -0.05); partial degradation.

## Cap_map impact

- HARD_PASS: MoE SHIFT K=16 path LIFTS TO ACTIVE; key design point unblocked.
- HARD_FAIL: K-scaling ceiling confirmed as fixed-capacity bound; annotate row.

## Timeout estimate

- moe_gradient_router_v1 FULL elapsed estimated ~3000s (per Hebbian v1 analog).
- K={4,8,16,32} x 3 seeds x gradient training.
- timeout_s = ceil(1.5 * 3000) = 4500s. Under 2h: no extra flag.

## Formula self-tests

1. M_per_expert = M_total // K: {4:800, 8:400, 16:200, 32:100}. Verified.
2. entropy(uniform K=4) = 2.0b, entropy(uniform K=16) = 4.0b. Verified.
3. HARD_PASS gate: ret_K16=0.93, ret_K4=0.95 -> delta=-0.02 >= -0.05. Verified.
4. HARD_FAIL gate: ret_K16=0.30, ret_K4=0.95 -> delta=-0.65 < -0.15. Verified.

## OOM check

Peak (W_sequential + keys + vals at M_total): ~170MB. Under 6GB. PASS.

## Smoke gate

Passed: N=512 1-seed K={4,16}. ret=1.0 at both K. entropy varies 2.0-4.0b.
HARD_PASS_NO_CEILING at smoke. elapsed=0.1s.
