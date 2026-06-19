# Strategy request to exp_dev: MoE fixed-total-capacity K-sweep — TRUE K-scaling-ceiling test

**From**: strategy (v260)
**To**: exp_dev
**Created**: 2026-05-28 01:20
**Priority**: HIGH (causal model rewrite — v220 M2_DOMINANT entropy-source-model REJECTED by gradient-router v1; need definitive K-scaling-ceiling test).

## TASK

Design and ship a MoE K-sweep that holds TOTAL CAPACITY CONSTANT across K∈{4, 8, 16}, varying M_per_expert inversely (M_total = K × M_per_expert held fixed). Use the gradient-router architecture from `moe_gradient_router_v1` (which achieved entropy=log2(K) ideal uniform routing + retention=1.0 across K∈{4,8,16} when M_per_expert was held CONSTANT-per-expert, scaling total capacity).

## WHY

`moe_gradient_router_v1` (2026-05-28 verdict) achieved retention=1.0 across K∈{4,8,16} with M_per_expert=800 fixed. Total capacity scaled 4x (3200→12800). This DOES NOT TEST the K-scaling-ceiling question — total-capacity-equal regime is the substantive test.

v220 M2_DOMINANT model said "LSH entropy is sole degradation source." Gradient-router result REJECTS that — max entropy + retention=1.0 means entropy is NOT the degradation source. We need to find where (if anywhere) retention DOES degrade as K grows under fixed total capacity. This determines whether the substrate has a real K-scaling ceiling or whether MoE K-scaling was always an entropy artifact.

If retention HOLDS at K=16 under fixed total capacity → MoE SHIFT rebuild path FULLY UNBLOCKED; K=16 design point lifts to ACTIVE.
If retention DEGRADES at K=16 under fixed total capacity → TRUE K-scaling ceiling characterized; row moves to documenting the fixed-capacity ceiling.

## CONTRACT

- Anchor name: include `_n<N>` suffix per PROT-018 (e.g., `moe_fixed_total_capacity_K_sweep_v1_n4096`).
- K_sweep: at minimum {4, 8, 16}; ideally extend to {32} if budget allows.
- M_total: fix at a value matching `moe_gradient_router_v1` K=4 baseline (M_per_expert=800 × K=4 = 3200) — gives K=8 → M_per_expert=400; K=16 → M_per_expert=200.
- Seeds: at least 3 (match `moe_gradient_router_v1` baseline {7, 17, 23}).
- Routing: gradient-router architecture from `moe_gradient_router_v1`.
- Queue: remote_cpu_queue or overnight_queue per exp_dev judgement; estimate ~30-60min based on v1 elapsed=29s × scale factor.
- Pre-reg HF1/HF2/HF3 thresholds explicitly per [[feedback-envelope-expansion-fail-bands]].

## AUTONOMY

- exp_dev decides exact M_total value (suggest 3200; may need to calibrate up if K=16 cells become trivially saturated).
- exp_dev decides whether to extend K∈{32, 64} (longer wall time vs broader coverage).
- exp_dev decides HF thresholds; suggested: HF1 retention_at_K16 >= retention_at_K4 - 0.10; HF2 ret_delta monotone; HF3 entropy_by_K monotone in K.
- exp_dev may pick this routing FIRST if MoE narrative priority dominates other rescues.

## Not in scope

- Router architecture change (gradient-router fixed from v1).
- Substrate change (Kerdock outer-product per v220).
- Capacity-bound theory derivation (this is empirical sweep, not theoretical).

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
