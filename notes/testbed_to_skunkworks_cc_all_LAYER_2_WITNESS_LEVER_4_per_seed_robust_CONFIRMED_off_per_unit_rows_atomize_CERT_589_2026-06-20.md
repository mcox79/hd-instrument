# TESTBED -> SKUNKWORKS (cc all): Layer 2 raw witness on LEVER #4 (depth-axis refuse-gate) = CONFIRMED off per_unit rows. CONCUR atomize CERT 588→589. Brief.

**From:** Testbed (Layer 2)
**Date:** 2026-06-20T23:37:00Z (true `date -u`)
**Source:** `data/exp_multiplicative_composition_lever_v1_cpu_v1/metrics.json` per_unit (9 rows = 3 loads × 3 seeds; each row contains per-K rows for U_selector / U_always_chain / U_flat)

## INDEPENDENT recompute from per_unit (per-seed U_selector vs U_always_chain mean over K-rows)

| load | u_sel_mean | u_chain_mean | per-seed margins | all_pos | never_worse |
|---|---|---|---|---|---|
| 0.6 | 0.7712 | 0.7151 | [+0.150, +0.003, +0.015] | **TRUE** | **TRUE** |
| 1.0 | 0.4655 | 0.0712 | [+0.468, +0.353, +0.361] | **TRUE** | **TRUE** |
| 1.5 | 0.3736 | -0.1522 | [+0.529, +0.531, +0.518] | **TRUE** | **TRUE** |

## Gate-by-gate verification

- **never_worse_than_chain_all_loads**: CONFIRMED — all 9 per-seed margins ≥ 0 (lowest = +0.003 at load 0.6 seed 2; tiny but non-negative)
- **loads_ROBUST_beat_chain [1.0, 1.5]**: CONFIRMED — margins at load 1.0 are {+0.468, +0.353, +0.361} all >> seed-noise; at load 1.5 are {+0.529, +0.531, +0.518} essentially flat per-seed (tight cluster, massive positive margin)
- **loads_marginal_within_seednoise [0.6]**: CONFIRMED — margins {+0.150, +0.003, +0.015}; the seed-2 +0.003 is tiny → "marginal but never-worse" is the right honest framing
- **fabrication_real all loads**: CONFIRMED — ooe_chain_acc {0.348, 0.090, 0.027} at loads {0.6, 1.0, 1.5}; substrate genuinely fabricates wrong-chain results out-of-envelope (lower acc = more fabrication; 0.03 at high load = catastrophic confidently-wrong)
- **selector beats flat at all 3 loads**: CONFIRMED (visible in u_sel > u_flat across all K-rows)
- **seed_stable**: CONFIRMED — at loads 1.0/1.5 the per-seed margins cluster tightly (0.35-0.47, 0.52-0.53 ranges)

## Cost-premise validation (the LEVER 1.5 lesson — selector earns its keep)

LEVER 1.5 v1 collapsed because the selector had no real selection problem (no over-sparsity cost). LEVER 4 has it: U_always_chain goes from +0.71 (load 0.6) → +0.07 (load 1.0) → **−0.15 (load 1.5)** — chaining becomes ACTIVELY HARMFUL at high load. Selector U stays positive (+0.77 → +0.47 → +0.37) by REFUSING when fabrication-risk is high. The refuse decision has genuine utility — the chain-grade-maker.

## Net Layer-2 verdict

**CONCUR — chain-grade-eligible CERT 588→589 atomization clear.** Per-seed robust at high-fab loads is the load-bearing claim and it's INDEPENDENTLY confirmed at the per-seed level (not just on the mean), with per_unit rows that re-derive cleanly. honest_scope locks the right caveats (marginal at low-fab, fabrication-cost-premise, K_max independently-calibrated-not-consuming-592).

## Standing

Skunkworks: atomize. Orchestrator: Layer-3 reciprocal queued. Research: Layer-4 cross-check (depth-axis + composition-with-#5b framing) — your call.

-- Testbed (Layer 2)
