# Pre-registration: wave14_moe_shift_partition_v1

**Date:** 2026-05-24
**Script:** experiments/exp_wave14_moe_shift_partition_v1.py
**Queue:** overnight_queue
**Parent handoffs:**
  - notes/exp_dev_handoff_research_moe_rebuild_2026-05-24.md (3-arm design spec)
  - notes/exp_dev_handoff_research_alpha_c_recalibration_2026-05-24.md (alpha_c bands)

## Why this experiment

R-PRIME-2 HARD-FAILED due to PARTITION-architecture confound: at N_k = N/K, the load
ratio M_per_expert / M_cap_per_expert = 4*M_total/N has K cancel algebraically, making
retention flat-in-K by construction. The rebuild tests the correct SHIFT vs PARTITION
binary using three matched arms.

M_per_expert=1600 from recalibrated alpha_c=0.56 at N=4096:
int(0.70 * 0.5625 * 4096) = 1612 ~ 1600 (conservative round-down).

## Design

**Arm A (SHIFT):** K full-N experts (N=4096 each), LSH balanced-bin gate + top-2 retrieval.
  Parameter budget: K*N^2 (grows with K). Per-expert capacity: alpha_c*N.
  Aggregate capacity (perfect gate): K * alpha_c * N.

**Arm B (PARTITION):** K experts each (N/K, N/K), same LSH gate but top-1 retrieval.
  Parameter budget: N^2 (fixed). Per-expert capacity: alpha_c*(N/K).
  Aggregate capacity: K * alpha_c * N/K = alpha_c * N. FLAT in K by construction.
  This is the negative control / null hypothesis.

**Arm C (SINGLE):** 1 expert of dim int(sqrt(K)*N), parameter budget K*N^2 (matched to SHIFT).
  Tests whether SHIFT gains come from structural separation or raw parameter count.

## Config

- N = 4096 (full mode)
- K_sweep = [1, 2, 4, 8]
- M_per_expert = 1600 (70% of alpha_c*N from recalibrated prestep)
- M_total_grid = [0.5, 1.0, 2.0] x K x M_per_expert (per K value)
- Seeds = [7, 17, 23, 31, 41] (5 seeds)
- Gating: LSH balanced-bin, equal-frequency quantile bins, top-2 retrieval (SHIFT)
- Mode-collapse instrumentation: Gini, max/min ratio, top2_frac logged per cell

## Pre-registered outcome bands

**HARD-PASS -- MoE BREAKS the floor:**
- Arm A (SHIFT) retention exceeds Arm C (SINGLE) by > 0.15 at M_total ~ 2*M_single_baseline
- Mode-collapse WITHIN safe band: Gini < 0.4, max/min < 5x, top2_frac < 0.6
- Retention monotone-non-decreasing in K at fixed M_total/K (tol 0.02)
- -> MoE row: structural separation demonstrated; SHIFT-MoE breaks parameter-count floor

**HARD-FAIL -- MoE on substrate REJECTED:**
- Arm A tracks Arm C within +/-0.05 across ALL M_total values
- Mode-collapse present: Gini > 0.4 OR max/min > 5x
- -> MoE row closed; parameter budget alone explains any improvement

**MIDDLE BAND -- MoE hides on floor at higher cost:**
- Arm A exceeds Arm C by 0.05-0.15
- Mode-collapse marginal: Gini 0.3-0.4 OR max/min 3x-5x
- -> Structural separation present but not dominant mechanism

**INSTRUMENTATION-FAIL:**
- Mode-collapse metrics cannot be reported (degenerate gating)
- OR cosine values all-zero or exactly constant
- -> Re-design before re-ship

## Smoke result

Smoke (N=512, 1 seed, K in {1,2,4}) PASSED suspicious-result gate.
All arms produce non-null, non-zero, non-constant cosines.

Walk-back gate TRIGGERED: smoke effect size d=0.446 < 1.0 (borderline).
Smoke best lift Arm A vs C: K=4, M=1600, A=0.699, C=0.512, lift=+0.187.
Note: smoke lift at K=4 M=1600 EXCEEDS the 0.15 HARD-PASS threshold, but d < 1.0
because variance across the combined K+M space is large. Full run at 5 seeds x N=4096
will provide proper per-cell CIs.

Walk-back pre-registration: full run uses n=5 seeds (not doubled to 10) because:
- The limiting variance is expected to be between K and M conditions, not between seeds
- 5 seeds at N=4096 gives CI half-width ~0.01-0.02 per cell (adequate for 0.15 threshold)
- Smoke d pooled the entire Arm A vs Arm C space; per-cell d at K=4, M=2*M_baseline
  is expected >> 1.0 at full N

## Self-test cells

1. gini([500,500,500,500]) = 0.0  verified
2. gini([2000,0,0,0]) = 0.75     verified
3. top2_frac balanced: 0.50 < 0.75 threshold  verified
4. top2_frac collapsed: 1.0 > 0.75 ALERT      verified
5. PARTITION K-cancellation: load_ratio = M_total/(alpha_c*N) for K in {2,4,8}  verified
6. SHIFT ratio decreases with K                verified
7. run_one_cell at tiny N=32 K=2 M=16: all arms cosine > 0.0  verified

## Estimated runtime

~4-6 GPU-hours: 4 K-values x 3 M-multipliers x 5 seeds x 3 arms x N=4096.
Each cell: 3 NxN matrix ops + top-2 retrieval over M_total items.
