# Pre-registration: gap4_two_tier_generational_W_v1

**Date:** 2026-06-26
**Anchor:** gap4_two_tier_generational_W_v1
**Queue:** local_cpu_queue (CPU-only numpy; ~3 CPU-hr per drill estimate; route remote_cpu if smoke per-arm wall exceeds 30 min)
**N:** 4096, **Seeds:** [11, 13, 19], **Cycles:** 4000

## Scientific question

The substrate's W matrix is single-tier today. Four disparate fields (JVM generational GC, RocksDB LSM leveled compaction, immune-system germinal-center maturation, brain hippocampus-cortex consolidation) independently arrived at the same architecture: two-tier storage with periodic promotion of important entries from a young/fast layer to an old/slow layer. Does adding a second W_old matrix with periodic importance-weighted promotion from W_young extend the substrate's continual-write horizon past the single-tier cliff (a8 alpha=0.30 boundary at N=1024) when stressed at ~7x Hopfield capacity?

## Pre-registered bands

**HARD-PASS_TWO_TIER_EXTENDS_CONTINUAL (all 4 conditions):**
- best two-tier arm final_forget <= 0.05 at cycle 4000
- baseline single-W cliffs at some cycle (curve_max_forget > 0.10)
- best two-tier arm cv across seeds <= 0.07
- best two-tier arm strictly better than baseline at final cycle

**HARD-PASS_PARTIAL:** drift_reduction (baseline_final_forget - best_two_tier_final_forget) >= 0.30 absolute but not all HP conditions met.

**MIDDLE_BAND:** drift_reduction in (0.05, 0.30) -- mechanism real but smaller than predicted; tune K_promote / tau / gamma hyperparameters in Phase 2.

**HARD-FAIL_TWO_TIER_DOESNT_HELP:** drift_reduction within +/- 0.05 of baseline -- two-tier provides no measurable benefit at this regime.

**HARD-FAIL_PROMOTION_CORRUPTS_W_OLD (implicit):** if best two-tier arm shows DEGRADATION vs baseline (drift_reduction < -0.05), promotion strategy is mis-specified.

## Calibration rationale

Drift from research drill `notes/research_gap4_continual_5x_drill_2026-06-26.md` Prediction 1 (P_deflated=0.50; four-field convergence). Anchor numerics: a8 baseline establishes substrate single-tier no-forgetting boundary at alpha=0.30 (1.5x Hopfield capacity alpha_c=0.138); NREM-replay v1 smoke MIDDLE_BAND drift_red=0.0667 (anchors "replay alone is insufficient"). At N=4096, 4000 cycles = alpha=0.977 (~7.1x Hopfield capacity) -- well past single-tier cliff; baseline SHOULD cliff in this regime. TWO_TIER has discriminating headroom: HARD_PASS_FORGET_CEILING=0.05 is tight (95% retention); HARD_PASS_BASELINE_CLIFF=0.10 ensures baseline genuinely fails so the comparison is honest. CV ceiling 0.07 inherits from NREM-replay v1 (same-class continual-cycle cell). The random-promote ablation isolates "is importance scoring necessary?" -- if it matches the importance-driven arm, importance scoring is not load-bearing.

## N-suffix section

Anchor name does NOT contain _n<N> suffix (PROT-018 rule: omit suffix when N=N_default-for-cell; the cell's production N=4096 is canonical for the continual-cycles class). Both smoke and FULL use identical N=4096 per META_M7 capacity-sensitive-dims rule. Only N_CYCLES, RECALL_PROBE_M, CHECKPOINT_INTERVAL, and SEEDS change between smoke and full.

## Timeout estimate

NREM-replay v1 smoke wall: 24.4s for N=1024, 500 cycles, 4 arms, 1 seed = ~6.1s per arm-per-500-cyc-N1024.
Scaling to N=4096, 4000 cycles, 5 arms, 3 seeds:
- per-cycle work dominates by N^2 (the W @ state matmul); cycle count linear.
- per-arm wall (N=4096, 4000 cycles) ~ 6.1 * (4096/1024)^2 * (4000/500) = 6.1 * 16 * 8 = 781s ~ 13 min.
- TWO_TIER arms also do periodic score-all-atoms-so-far for promotion: 4 promotion steps at K=1000 with cap cycles each = O(N^2 * cap) operations dominated by recall loops; estimate +20% per two-tier arm.
- per-seed total = 13 min baseline + 4 * 13 * 1.2 = ~75 min. Three seeds = ~225 min = 3.75 hr.
- Add 50% safety margin: timeout_s = 4 hr * 1.5 = 6 hr = 21600s.

LOCAL CPU QUEUE timeout cap: 14400s (4 hr). If smoke shows per-arm wall >2h, ROUTE TO REMOTE_CPU via Orchestrator (Fix #17 + Fix #24). DECISION: dispatch local with timeout=14400s if smoke estimates per-seed <80min; else route remote_cpu.

Per-arm sub-checkpoint (NESS-hang prevention USER 2026-06-26): _write_arm_partial after each arm completes, cap losing >1 arm of compute.

Sub-cycle progress: print every CHECKPOINT_INTERVAL (250 cycles) cycle => visible liveness ~once per 50s under nominal load.

timeout_s = 14400 (4 hr cap; if smoke shows extrapolation > 80% of cap, route to remote_cpu instead).
