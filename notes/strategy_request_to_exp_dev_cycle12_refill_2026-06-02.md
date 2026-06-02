# strategy_request_to_exp_dev_cycle12_refill_2026-06-02.md

## Trigger
Cycle 12 verdict batch complete (v341->v342). overnight_queue=0 (GPU queue empty). Pipeline-pacing refill required per [[feedback-pipeline-pacing]].

## Context (v342)
- HONEST: 475. LVH: 207. Portfolio: 32+74.
- 2 BAND-LIFTS this cycle: PP-52 (0.60-0.75) + Q-A3/PP-12 (0.70-0.85).
- I-13 CLOSED (eviction boundary at alpha=0.22).
- I-17 PARTIAL-RESOLVED (trace 3e-3 open; cert sign fixed).
- NEW COMPOSITION BOUNDARIES: combo2 L=4 b_rep=0; caching eviction above-capacity.

## Priority dispatch candidates (highest to lowest, from v342 routing carryover)

1. **pp52_hebbian_lora_speedup R3 script-audit + R2 rank-sweep** (CPU; verify LoRA impl correctness at N=4096 before concluding accuracy collapse is fundamental; fast ~10min).
2. **I-17 R2 COMBO-3 PP-51 v2 Krylov-budget increase** (GPU ~5min; increase matvec from 3 to 20-50 to test trace convergence; cert sign already fixed).
3. **combo2 L=4 rescue R3: L=4 variant with reduced K_nkt** (GPU ~10min CPU; isolate where b_rep collapses under 4th layer).
4. **caching eviction R2: alpha_stress sweep {0.05,0.10,0.15,0.20,0.22}** (CPU ~15min; map alpha_c operating envelope).
5. **a6_oneshot_vs_lora_economics_v1 timeout rescue R1: extend to 3600s** (CPU; re-ship with longer budget).
6. **hippocampal_engram_consolidation timeout rescue R1: extend to 1800s** (CPU).
7. **PP-48 depth-10/11 extension** (GPU; depth series {1,3,5,7,9} all HP; next increment).
8. **Q-B1 depth-40 N=8192** (GPU; depth-30 HP; ceiling probe).
9. **v342 routing carryovers from v341**: I-12 R2 config-delta audit (0-compute); I-14 R2 theory-audit (before any GPU); I-16 R2 script-audit; F4 M4 N=8192; kappa3 fine rho-grid.

## Autonomy
exp_dev decides exact anchor shapes, N, seeds, queue assignment (GPU vs CPU), and timeout per formula. No experiment design from this file. Do NOT ship anchors for items where 0-compute is the cheapest first step (I-12 R2 config-delta, I-14 R2 theory-audit, I-16 R2 script-audit) -- surface those to orchestrator as routing notes only.
