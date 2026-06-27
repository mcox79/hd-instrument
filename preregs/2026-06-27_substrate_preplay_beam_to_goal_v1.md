# Prereg: substrate_preplay_beam_to_goal_v1

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) Wave 3B TOP-2
**Drill source:** notes/research_drill_3x_goal_directed_planning_2026-06-27.md (CELL 2; Angle B3 + A3)
**Stage:** Stage 3 (goal-directed planning; higher functions)
**P_deflated:** 0.50

## HYPOTHESIS

Substrate can run K=64 parallel forward rollouts to a goal-state before acting (hippocampal preplay analog; Pfeiffer-Foster 2013). For each rollout, pick action sequence whose final state maximizes cos(leaf_state, goal). At synthetic 4-block BlocksWorld (STRIPS-style), substrate solves >= 0.70 of goal pairs in <= 2x optimal plan-length, beating greedy-1step by >= 0.25, AND parallel-K=64 beats parallel-K=4 by >= 0.10 (the substrate-better-than-brain discriminator; Cowan-4 vs substrate-K=64).

## ARMS (5)

1. **ARM_GREEDY_1STEP** -- pick action whose successor has highest cos(s', goal); no lookahead (the "Q&A engine" baseline).
2. **ARM_PREPLAY_K4** -- 4 parallel rollouts depth D=6; pick best by cos(leaf, goal); Cowan-4 brain-scale analog.
3. **ARM_PREPLAY_K64** -- 64 parallel rollouts depth D=6; substrate-scale.
4. **ARM_PREPLAY_K64_WITH_GOAL_GATE** -- K=64 with bind(state, goal) gating per-step action selection (Cell 1 mechanism layered in).
5. **ARM_RANDOM_CONTROL** -- random action sequences; should HARD_FAIL_BASELINE (<= 0.15 solve rate).

## PRE-REG BANDS (LOCKED; PROSPECTIVE)

- **HARD_PASS**: ARM_PREPLAY_K64 solve_rate >= 0.70 AND (ARM_PREPLAY_K64 - ARM_GREEDY_1STEP) >= 0.25 AND (ARM_PREPLAY_K64 - ARM_PREPLAY_K4) >= 0.10 (substrate-better-than-brain proof) AND ARM_PREPLAY_K64_WITH_GOAL_GATE closes >= 50% of gap to ARM_DIAG_ORACLE (here treated as 1.0 since analytic-solver gives ground truth) AND median plan-length <= 2x optimal AND ARM_RANDOM_CONTROL <= 0.15.
- **MIDDLE_BAND**: solve_rate in [0.50, 0.70) AND beats greedy by >= 0.15 OR K=64 within [0.05, 0.10] of K=4.
- **HARD_FAIL**: solve_rate <= 0.30 OR ARM_PREPLAY_K64 - ARM_PREPLAY_K4 < 0.05 (parallel doesn't help -- rollouts mode-collapsed) OR ARM_RANDOM_CONTROL > 0.30 (domain too easy = discriminator broken).

## FAIRNESS GATES

- Same 4-block BlocksWorld synthetic; 6 actions (pick-up, put-down, stack, unstack, move-aside, swap).
- Ground-truth optimal via analytic BFS solver in-cell.
- Goals sampled to require >= 3 steps (filter trivial goals).
- W_world fit identically across arms (closed-form pseudoinverse over (state, action) -> next_state).
- Same N_DIM; same seeds; per-(arm, seed) cv reported.

## CARDINALITY (META_RULE_H)

- EXPECTED_N_UNITS_FULL = 5 arms * 3 seeds * 100 goals = 1500
- EXPECTED_N_UNITS_SMOKE = 5 arms * 2 seeds * 20 goals = 200
- Discriminator-must-survive-scale: smoke runs K=4 vs K=64 at full D=6 to verify parallel-scaling discriminator fires.

## HARDENING

L1 STARTED + L2 per-arm progress + L3 outer try/except + L4 import-crash sentinel.

## COMPUTE

CPU on remote_cpu; ~30-60 min full; <10 min smoke. Forward-only numpy. W_world fit ~5s setup; per-rollout step ~us-scale.

## SUBSTRATE PREREQS (verified in hdlab/)

- multi_hop.iter_cleanup_chain (chain-grade depth-15 rollout primitive)
- iterative_attractor (Modern Hopfield cleanup at each rollout step)
- binding.bind/unbind (state-goal composition; HRR involutive)
- predictive_coding.residual_magnitude (per-rollout uncertainty for tie-breaking; optional)
- working_memory multi-bank (parallel-K slot capacity; chain-grade K=4096)

Cell uses self-contained instances of these primitives (no hdlab imports for portability per author convention).
