# exp_dev hand-off — research: hierarchical goal-directed planning primitive (Stage 3)

filed-by: research (Opus 4.7 1M)
date: 2026-06-27
trigger: USER load-bearing concern #5 for M3 (M4-load-bearing). Substrate has single-hop preplay (K=64 + goal-conditioned gate, MIDDLE_BAND today; closes 60% oracle gap). Hierarchical subgoal decomposition (make-breakfast → boil-water + crack-egg + plate) is untested.
pause state: respect data/orchestrator_paused.flag

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are POINTERS to substrate-feasible mechanisms; exp_dev autonomously designs the cell per anchor + verify-the-referent.

---

## Trigger (cite source)

`notes/research_drill_2x_hierarchical_goal_planning_primitive_stage3_2026-06-27.md`

**Headline:** Hierarchical goal decomposition is a 3-level Plate-chunked HRR tree where per-level cleanup against a learned dictionary breaks noise compounding. Substrate has chain-grade pieces 3/4 (HRR bind/unbind, multi_hop.iter_cleanup_chain, partition routing M=10M); missing piece is the per-level chunk-dictionary fit (closed-form pseudoinverse on macro-action codebook). For 3-level B=4 trees at N=8192, K_total=64 is 50x under Frady-Sommer cliff — comfortable regime. **Substrate-better-than-brain: parallel cleanup across all K^L candidate trees vs brain's ~3 sequential alternatives.**

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (Rank 1): `substrate_hierarchical_subgoal_planner_v1`

- **Anchor pointer:** Section (b) of research note + CELL 1 in TOP-3 ranking. 5 arms: REPRODUCE_RAIL + RANDOM_PLAN + FLAT_PREPLAY_K64_D8 + HRR_TREE_DECOMPOSE_3LVL (mechanism) + HRR_TREE_NO_CLEANUP_ABLATE (Plate discriminator).
- **Substrate-product reading:** "Substrate decomposes composite goals (8-step optimal plan) into 3-level HRR-tree subgoal hierarchy; per-level cleanup against learned chunk-dictionary recovers macro-actions; leaves route through existing flat-K=16 preplay beam. Glass-box hierarchical plan is fully auditable at each level — the substrate analog of anterior-PFC abstract-goal binding (Koechlin 2003) composing with posterior-PFC concrete-action leaves (Badre 2008)."
- **Tier hint:** chain-grade-eligible if HP (solve_rate ≥ 0.65 AND lift over flat ≥ +0.25 AND cleanup-load-bearing lift ≥ +0.20 AND median plan-length ≤ 2x optimal AND META_M7 PASS AND CARDINALITY_OK).
- **Why now:** cheapest test of the Plate-chunking hypothesis at substrate scale; all primitives already chain-grade; per-level dictionary fit is <30s compute; 8-block BlocksWorld evaluator ~250 lines on top of yesterday's 4-block evaluator. Composes WITH yesterday's `pfc_goal_conditioned_gate_v1` (Cell 1 from 3x drill) — the goal-conditioned gate IS the per-step routing inside ARM_HRR_TREE leaf rollouts.
- **P_deflated:** 0.45 (deflated from 0.65; novel-composition cap; brain-existence-proof + substrate-mining lifts; calibration penalty -0.20; novel-composition cap -0.05)
- **Substrate-feasibility:** HIGH. Existing chain-grade primitives:
  - `hdlab/binding.py` — HRR bind/unbind (involutive, chain-grade)
  - `hdlab/multi_hop.py` — iter_cleanup_chain (depth-15 chain-grade; THE per-level cleanup primitive)
  - `hdlab/working_memory.py` — multi-bank K=4096 (parallel rollout slot capacity)
  - `hdlab/partition_routing.py` — M=10M chain-grade (per-level codebook hosting)
  - `hdlab/iterative_attractor.py` — Modern Hopfield cleanup variant
- **Mechanism class:** Plate 1995 Ch.6 hierarchical chunking with per-level cleanup; closed-form pseudoinverse for chunk-dictionary fit (no autograd; no Hebbian-window dependency)
- **Domain:** 8-block extended BlocksWorld; 6 primitive actions {pick-up, put-down, stack, unstack, move-aside, swap}; 5 mid-level macros {tower, separate, gather, order, clear-surface}; 100 composite goal pairs per seed; analytic BFS optimal-plan solver (8-block state space ~10^6 states, tractable); goals filtered to require ≥ 6 primitive steps (composite regime)
- **Sequencing:** NOT GATED on yesterday's cells; this drill targets a different mechanism layer (tree vs gate). Composes with yesterday's `pfc_goal_conditioned_gate_v1` if that ships first, but does NOT depend on its verdict.

### ANCHOR 2 (Rank 2): `substrate_hierarchical_planner_block_sparse_hersche_v1`

- **Anchor pointer:** CELL 2 in research note TOP-3. Same HRR tree as ANCHOR 1, but per-level codebook uses Hersche-2024 block-sparse codes (arXiv:2303.13957); each level reserves disjoint blocks of N=8192 vector, eliminating cross-level interference. Adds 1 arm: ARM_HRR_TREE_BLOCK_SPARSE_3LVL.
- **Substrate-product reading:** "Block-sparse per-level codebook gives ~2x cleanup capacity (effective K_max lifts from ~530 to ~1060); enables deeper trees (4-level B=4 with K_total=256) and higher per-level fidelity."
- **Tier hint:** chain-grade-eligible if HP AND block-sparse arm beats dense-codebook arm by ≥ +0.05.
- **Why now:** GATED on ANCHOR 1 outcome. If ANCHOR 1 HARD_FAILS specifically via "cleanup not load-bearing" failure mode (interpreting as: dictionary fit margin insufficient), ANCHOR 2 ships immediately. If ANCHOR 1 HP, ANCHOR 2 ships as DEPTH EXTENSION (4-level trees for 64-step composite plans).
- **P_deflated:** 0.35 (deflated harder; block partitioning is novel composition on substrate; per-level disjoint block assignment scheme is unverified at substrate scale)
- **Substrate-feasibility:** MEDIUM (Hersche math is published; substrate implementation of disjoint block assignment is new code; partition routing primitive provides the block mechanism)
- **Mechanism class:** Block-sparse HDC + Plate hierarchical chunking
- **Sequencing:** GATED on ANCHOR 1 verdict

### ANCHOR 3 (Rank 3): `substrate_hierarchical_planner_replay_consolidated_dictionary_v1`

- **Anchor pointer:** CELL 3 in research note TOP-3. ANCHOR 1 + NREM replay decorator on dictionary fit (proven-bound +0.57 drift_reduction 2026-06-22). Replay re-presents (state_pre, macro_action, state_post) tuples at compressed time-scale; sharpens W_macro discriminating capacity. Adds 1 arm: ARM_HRR_TREE_NREM_REPLAY.
- **Substrate-product reading:** "NREM-replay-sharpened chunk-dictionary tests whether dictionary fidelity is the limiter for hierarchical planning; brain CLS analog (hippocampal replay consolidates schemas into cortical chunks)."
- **Tier hint:** chain-grade-eligible if HP AND replay-augmented arm beats vanilla-dictionary arm by ≥ +0.10.
- **Why now:** GATED on ANCHOR 1 MIDDLE_BAND outcome (i.e. mechanism is right but fidelity is bottleneck). If ANCHOR 1 HP or HARD_FAIL, ANCHOR 3 deferred.
- **P_deflated:** 0.30 (two simultaneous mechanism changes — hierarchy + replay; deflated harder)
- **Substrate-feasibility:** HIGH IF ANCHOR 1 ships first; NREM replay is chain-grade primitive
- **Mechanism class:** Plate hierarchical chunking + CLS-style replay consolidation
- **Sequencing:** GATED on ANCHOR 1 MIDDLE_BAND

---

## Context pointers (file paths, not summaries)

- `notes/research_drill_2x_hierarchical_goal_planning_primitive_stage3_2026-06-27.md` — THIS drill (math, candidates, predictions)
- `notes/research_drill_3x_goal_directed_planning_2026-06-27.md` — yesterday's per-step gate drill (Cell 1 `pfc_goal_conditioned_gate_v1` composes WITH ANCHOR 1 leaves)
- `notes/research_gap_B_goal_directed_planning_2026-06-26.md` — flat-K=128 preplay drill (FLAT baseline that ARM_FLAT_PREPLAY in this cell extends to depth-8)
- `notes/wave14e_hierarchical_composition_research.md` — substrate-physics scoping doc; Plate Ch.6 + Frady-Sommer + Hersche + SPA Spaun precedent; depth-vs-capacity tradeoff math (THE load-bearing math doc for this cell)
- `notes/research_drill_substrate_first_hierarchical_5x_2026-06-08.md` — production-architecture hierarchical pipeline drill (different abstraction layer: query-routing not goal-decomposition)
- `notes/research_drill_2x_hierarchical_3_tier_W_revival_2026-06-27.md` — 3-tier W revival drill (different abstraction: timescale-hierarchy of W matrices, not goal-tree decomposition; orthogonal)
- `hdlab/binding.py` — HRR bind/unbind (involutive, chain-grade)
- `hdlab/multi_hop.py` — iter_cleanup_chain (THE per-level cleanup primitive)
- `hdlab/working_memory.py` — multi-bank K=4096 chain-grade WM
- `hdlab/iterative_attractor.py` — Modern Hopfield cleanup (alternative per-level cleanup primitive)
- `hdlab/partition_routing.py` — M=10M chain-grade (per-level codebook hosting)
- `hdlab/predictive_coding.py` — residual_magnitude (per-leaf-rollout uncertainty signal; optional tie-breaker at leaf level)
- `data/substrate_index/atoms.jsonl` — search `multi_hop` (chain-grade depth-15), `partition_routing_10M` (chain-grade), `task_vector_HRR` (chain-grade), `NREM_replay drift_reduction` (proven-bound +0.57)
- META_M7 REPRODUCE_PV2 rail band [0.08, 0.25] — mandatory

---

## Extended BlocksWorld evaluator spec (exp_dev autonomously implements)

- 8 blocks {A..H} on a table (extends yesterday's 4-block); each block has at most one block on top
- 6 primitive actions: pick-up(X) / put-down(X) / stack(X, Y) / unstack(X) / move-aside(X) / swap(X, Y)
- 5 mid-level macro-actions defined as primitive subsequences:
  - tower(X, Y, Z): stack(X, Y) → stack(Y, Z)
  - separate(X, Y): unstack(X) → put-down(X) [if X on Y]
  - gather(X, Y, Z, W): move blocks to common region (multi-primitive)
  - order(X, Y, Z): rearrange into target ordering
  - clear-surface(X): unstack all blocks above X
- State encoding: HRR bind each (block, location) pair; bundle all pairs into state codeword
- Goal encoding: HRR bind of target (block, location) pairs into goal codeword
- 100 random (start, goal) pairs per seed; 3 seeds [7, 17, 23]
- Analytic optimal-plan solver: BFS over 8-block state space (~10^6 states, tractable); provides optimal-plan-length ground truth
- Goal filter: optimal plan-length ≥ 6 primitive steps (composite regime; sub-tier easy goals filtered)
- Solve = final-state cosine to goal ≥ 0.80 AND plan-length ≤ 3 × optimal AND no-invalid-action in trajectory

---

## Contract

- ANCHOR 1 first; ~30-60min remote_cpu single 5-arm cell
- META_M7 rail MANDATORY (REPRODUCE_POINTER_CHAIN_V2_5HOP arm, band [0.08, 0.25])
- Cleanup-load-bearing discriminator (ARM_HRR_TREE − ARM_HRR_TREE_NO_CLEANUP ≥ +0.20) REQUIRED for chain-grade HARD_PASS — this is the Plate-1995 substrate-physics check; without it cell tiers down to MIDDLE_BAND even at absolute solve_rate ≥ 0.65
- Decomposition lift discriminator (ARM_HRR_TREE − ARM_FLAT_PREPLAY ≥ +0.25) REQUIRED for chain-grade
- Train/test discipline: W_macro and W_goal fit on 80% training goal-classes; HP eval on 20% held-out goal-classes (per BIAS-13/14/15 contamination guard)
- Cell-author smoke first per discriminator-must-survive-scale: smoke at full N=8192 depth-6 composite with 3 of 5 macros active (not N=512 depth-3 with 1 macro) — verify per-level cleanup actually fires
- CARDINALITY_OK mandatory pre-reg field: EXPECTED_N_UNITS = 5 arms × 3 seeds × 100 goals = 1500
- No silent `except:` blocks (per three-smoke-disciplines feedback)
- Smoke must FIRE the discriminator, not just verify cell runs
- Band-floor result is MIDDLE_BAND not HARD_PASS
- Fix #17 strict runtime measurement
- Fix #28 verify per-arm metrics.json before any cross-arm convergence framing (NO verdict_msg-only claims)
- Pre-reg per-arm thresholds locked at dispatch (not editable post-hoc)
- BIAS-13/14/15 contamination/regime/mismatch guards: 8-block BlocksWorld is fresh synthetic; goal-encoding uses substrate-vocab not training-set classes; macro-actions defined as code, not learned from substrate state distribution
- Verify-the-referent gate: `tools/predispatch_check.py substrate_hierarchical_subgoal_planner_v1` before dispatch (per fix #26)
- Honest classification: cell-author classifies; Skunkworks tier UP if appropriate (per fix #28-recurring; default UNDER-claim)

---

## Autonomy declaration

exp_dev autonomously decides:
- Cell file layout under `cells/` (suggest `cells/substrate_hierarchical_subgoal_planner_v1.py`)
- Smoke configuration (suggest depth-6 composite + 3 of 5 macros + 1 seed + 20 goals as smoke for ~5min wall)
- W_macro / W_goal pseudoinverse fit code (existing hdlab patterns for closed-form fits)
- Whether to use `iter_cleanup_chain` (canonical) or `iterative_attractor` (Modern Hopfield variant) for per-level cleanup; default = iter_cleanup_chain (chain-grade at depth-15)
- HRR_TREE_NO_CLEANUP arm implementation: replace per-level cleanup with raw bundle (zero-op) OR with identity-cleanup (verify-the-referent); default = raw bundle
- Seed selection beyond [7, 17, 23] if cv > 0.10 at smoke
- Queue target: remote_cpu (Fix #17 routing — pure-numpy forward-only, no GPU benefit per Fix #24)
- Whether to spawn parallel ANCHOR 2 or ANCHOR 3 cells; default = serial after ANCHOR 1 verdict

exp_dev does NOT decide:
- HARD_PASS thresholds (locked at research note Section c)
- Mechanism class (must use Plate-chunking HRR tree with per-level cleanup; not Rao temporal-hierarchy)
- Domain (8-block extended BlocksWorld; composite goals ≥ 6 primitive steps)
- Discriminator definition (cleanup-load-bearing AND decomposition-lift are both required for chain-grade)

---

## Completion criteria

ANCHOR 1 dispatched → wait for verdict landing (recent_landings.jsonl polled) → Skunkworks classifies → research re-engaged for ANCHOR 2/3 sequencing decision based on actual outcome.
