# exp_dev hand-off -- research: GAP B goal-directed planning / forward simulation

filed-by: research (Opus 4.7 1M)
date: 2026-06-26
trigger: USER in-thread deep drill on goal-directed planning. "Given a goal, can substrate generate a SEQUENCE of actions to achieve it?" + USER addendum: cortex layer being spun up TODAY -- flag cortex-composed planning explicitly + drill it as top candidate.
pause state: respect data/orchestrator_paused.flag

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are POINTERS to substrate-feasible mechanisms; exp_dev autonomously designs the experiment per anchor + verify-the-referent.

---

## Trigger (cite source)

`notes/research_gap_B_goal_directed_planning_2026-06-26.md`

Headline: Substrate-grade planning is a recomposition of already-chain-grade primitives (multi-hop depth-15 + multi-bank WM K=1024 + g1b autoregressive + kv_learned_projection). Three brain mechanisms map directly to substrate: (1) parallel-beam rollout = USER's K=8192 beam-width-vs-brain-3 claim; (2) predictive-coding hierarchy = Rao 2024 active predictive coding; (3) BG winner-take-all = argmax over rollout value scores. The cortex-composed variant (cortex W as policy + world-model + MH value head) is the substrate-better-than-brain proofpoint but DEPENDS on cortex layer cells landing chain-grade first.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (Rank 1): substrate_planning_cortex_composed_beam_v1_META_M7

- **Anchor pointer:** Candidate 1 in research note Section 3 + cheap decisive test in Section (b). 4 arms: REPRODUCE rail / GREEDY_1STEP baseline / RANDOM_BASELINE control / PB_PC_N128_D15 candidate.
- **Substrate-product reading:** "Substrate plans an action sequence to achieve a goal via parallel-beam rollout with learned world-model + value head; the substrate-better-than-brain claim is the parallel-N discriminator (N=128 lift over N=8 by >=0.10)."
- **Tier hint:** chain-grade-eligible if HP (solve_rate >= 0.70 AND lift over greedy >= 0.25 AND parallel-scaling lift >= 0.10 AND median plan-length / optimal <= 2.0 AND META_M7 PASS).
- **Why now:** cheapest decisive test substrate has access to RIGHT NOW; Cell X (beam-search-with-WM-candidates v1) lands today/tomorrow and provides the per-hop infrastructure; W_world + V_W fits are <100s compute; BlocksWorld evaluator ~200 lines. Either outcome (HP or HF) is decisive.
- **P_deflated:** 0.50 (novel-synthesis cap)
- **Substrate-feasibility:** HIGH (4 of 5 primitives chain-grade; W_world is kv_learned_projection class at 0.827 precedent)
- **Mechanism class:** parallel-beam rollout with closed-form pseudoinverse W_world + V_W (no backprop)
- **Domain:** BlocksWorld synthetic, 4 blocks, 6 actions {pick-up, put-down, stack, unstack, move-aside, swap}, 100 random goal pairs/seed, analytic optimal-plan solver provides ground truth
- **Sequencing:** GATED on Cell X verdict landing; if Cell X HP -> ship; if Cell X HARD_FAIL -> ship with conservative envelope (N=32, D=5)

### ANCHOR 2 (Rank 2): substrate_planning_cortex_composed_with_MH_value_head_v1

- **Anchor pointer:** Candidate 2 in research note Section 3 + Section 2 Class 6 (cortex-composed). Extends ANCHOR 1 with Modern Hopfield value head: goal codewords as MH attractors; V_W(state) = -energy(MH iteration from state, attractor = goal).
- **Substrate-product reading:** "Substrate planning composes WITH the cortex layer -- MH value head is denoising-robust where cosine value head is not; tests substrate-better-than-brain claim that cortex composition LIFTS planning over flat substrate."
- **Tier hint:** chain-grade-eligible if HP AND MH value head beats cosine value head by >=0.05.
- **Why now:** GATED on (a) ANCHOR 1 HP AND (b) Modern Hopfield revival cell verdict landing chain-grade-PASS (today/tomorrow). If MH revival MIDDLE_BANDs or HARD_FAILs, ANCHOR 2 is DEPRECATED.
- **P_deflated:** 0.45
- **Substrate-feasibility:** HIGH IF cortex cells land HP
- **Mechanism class:** PB-PC + MH value head + cortex slow-W action prior (if Gap 3 BCM cell also HPs)
- **Composition prior cascade:** if all THREE cortex cells (TWO_TIER + BCM + MH revival) land chain-grade-PASS today, ANCHOR 2 P_deflated lifts to 0.50; if 2 of 3 PASS, stays 0.45; if 1 of 3 PASS, drops to 0.35; if 0 of 3 PASS, DEPRECATED.

### ANCHOR 3 (Rank 3): substrate_planning_active_predictive_coding_hierarchy_v1

- **Anchor pointer:** Candidate 3 in research note Section 3 + Class 3. Three-level hierarchy of W_world matrices at temporal scales (1-step / 5-step / 25-step macro-action); predictive_coding.py provides per-layer prediction-error machinery; residual_magnitude() biases planner toward macro-actions where world-model is confident.
- **Substrate-product reading:** "Substrate plans at deep horizons (>=50 primitive steps) via hierarchical option composition -- the 'plan all day' substrate-better-than-brain claim gets empirical evidence."
- **Tier hint:** chain-grade-eligible only if HP at depth-50 effective primitive horizon AND beats flat-D15 by >=0.10.
- **Why now:** GATED on ANCHOR 1 HP_PARTIAL or HP (need flat baseline before hierarchy adds value). If ANCHOR 1 HARD_FAILs, ANCHOR 3 DEFERRED until world-model bottleneck resolved (ANCHOR 4 path).
- **P_deflated:** 0.35
- **Substrate-feasibility:** MEDIUM (hierarchy training requires synthesizing macro-action data; non-trivial)
- **Mechanism class:** Rao 2024 active predictive coding hierarchical world model
- **Open question:** macro-action training data synthesis -- exp_dev autonomously decides whether to synthesize via random subsequence sampling or via Q-learning-style value-iteration on the flat W_world

---

## Optional rescue anchors (cite if ANCHOR 1 HARD_FAILS)

### ANCHOR 4 (HARD_FAIL pivot from ANCHOR 1): substrate_planning_NREM_replay_world_model_v1

- **Anchor pointer:** Candidate 4 in research note Section 2 Class 4. W_world fit WITH NREM replay decorator (proven-bound +0.57 drift_reduction 2026-06-22).
- **Why now:** ONLY if ANCHOR 1 HARD_FAILS specifically because W_world is the bottleneck (not the rollout mechanism; discriminator: ARM_PB_PC train solve_rate >> test). Tests whether replay sharpening of world model lifts planning to HP.
- **P_deflated:** 0.40

### ANCHOR 5 (HARD_FAIL pivot from ANCHOR 1): substrate_planning_belief_state_SLAM_v1

- **Anchor pointer:** Candidate 5 in research note Section 2 Class 5. Multi-bank WM at K=50 represents belief distribution over current state; minimize residual_magnitude across rollouts.
- **Why now:** ONLY if ANCHOR 1 AND ANCHOR 4 both fail. Tests whether the substrate's planning capability requires belief-state tracking (POMDP analog).
- **P_deflated:** 0.30

---

## Context pointers (file paths, not summaries)

- `notes/research_gap_B_goal_directed_planning_2026-06-26.md` -- THIS drill (mechanism, candidates, predictions)
- `notes/exp_dev_to_research_USER_beam_search_and_expansion_sweep_DISPATCHED_2026-06-25.md` -- Cell X dispatch (predecessor providing per-hop infrastructure)
- `notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md` -- Gap 1 separate-pathway routing (informs W_world fit class)
- `notes/research_n5_revival_slow_learning_cortex_context_2026-06-26.md` -- learning-time vs query-time placement (informs W_world learning-time fit)
- `notes/research_modern_hopfield_revival_slow_built_basins_2026-06-26.md` -- MH revival cell (precondition for ANCHOR 2)
- `notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md` -- TWO_TIER cortex layer dispatch (precondition for ANCHOR 2)
- `data/substrate_index/atoms.jsonl` -- search for `kv_learned_projection` (chain-grade 0.827; 2026-06-20)
- `data/substrate_index/atoms.jsonl` -- search for `g1b autoregressive` chain-grade
- `data/substrate_index/atoms.jsonl` -- search for `NREM_replay drift_reduction` (proven-bound +0.57)
- `hdlab/predictive_coding.py` -- predict/residual/residual_magnitude/threshold_gate/proportional_gate/gated_write (ALL ANCHORS reuse)
- `hdlab/multi_hop.py` -- iter_cleanup_chain / partition_routed_chain (per-rollout-step primitive)
- `hdlab/working_memory.py` -- assert_chain_grade_envelope (parallel-N bank assertion at K=1024)
- `hdlab/generation.py` -- g1b autoregressive (alternative per-step rollout primitive)
- `hdlab/iterative_attractor.py` -- Modern-Hopfield-style fixed-point iteration (ANCHOR 2 value head)
- META_M7 REPRODUCE_PV2 band [0.08, 0.25] -- pointer-chain v2 reference rail

---

## BlocksWorld evaluator spec (exp_dev autonomously implements)

- 4 blocks {A, B, C, D} on a table; each block has at most one block on top
- 6 primitive actions: pick-up(X) / put-down(X) / stack(X, Y) / unstack(X) / move-aside(X) / swap(X, Y)
- State encoding: bind each (block, location) pair via HRR; bundle all pairs into state codeword
- Goal encoding: same as state encoding for the target configuration
- 100 random (start, goal) pairs per seed
- Analytic optimal-plan solver: BFS over state space (max 2^4 = 16 states; trivially solvable) -- provides optimal-plan-length ground truth
- Per-rollout-step cost: O(N * V_C) = ~1.6e6 FLOPS
- Solve = rolled-state final cosine to goal >= 0.80 AND plan-length <= 3 * optimal AND no-invalid-action in trajectory

---

## Contract

- ANCHOR 1 first; ~3-5h local_cpu single 4-arm cell
- META_M7 rail MANDATORY (REPRODUCE_POINTER_CHAIN_V2_5HOP arm, band [0.08, 0.25])
- Parallel-scaling discriminator (N=128 vs N=8 lift >=0.10) REQUIRED for chain-grade HARD_PASS; without it cell tiers down to MIDDLE_BAND even at solve_rate >=0.70
- Train/test discipline: W_world fit on 80% training goals; HP evaluation on 20% held-out; train >> test by >0.20 flags overfit
- Cell-author smoke first (verify W_world fit converges <30s; train solve_rate >= 0.65 on smoke domain; BlocksWorld solver returns correct optimal plan-length for hand-verified examples)
- Fix #17 strict runtime measurement
- Fix #28 verify per-arm metrics before cross-cell convergence claims (no over-claiming from verdict_msg framings)
- Pre-reg per-arm thresholds before dispatch per [[feedback-experiment-bias-master-checklist]]
- BIAS-13/14/15 contamination/regime/mismatch guards: confirm BlocksWorld state encoding is NOT a copy of any existing substrate atom (clean synthetic per [[feedback-clean-encoder-tests-no-contamination]])
- Verify-the-referent gate: tools/predispatch_check.py before dispatch

---

## Autonomy declaration

exp_dev designs the cell autonomously per anchor pointer. Specifically:
- Decide whether to ship as single 4-arm cell or split into 2 cells (greedy + random can ship as one bundle; PB_PC may ship separately if compute >5h)
- Decide N_DIM (8192 from substrate-mining baseline; deviate only with stated reason)
- Decide whether to dispatch local_cpu or remote_cpu (numpy-bound; local is fine for the cell size)
- Decide ridge regularization for W_world / V_W fit (recommended; lambda from training-set cross-validation)
- Decide whether to include extra ARM_PB_PC_K32_D5 (conservative envelope) as an additional smoke gate if compute budget allows
- Decide whether to add ARM_PB_PC_HRR_BIND_STATE vs ARM_PB_PC_BUNDLE_STATE arm to test bind-vs-bundle for state encoding (recommend: pick ONE encoding from substrate-mining; do not test both in this cell -- queue as a follow-up if cell HARD_PASSES)
- Decide whether the W_world is a SINGLE matrix (state x action -> next_state) OR a tensor (one matrix per action) -- recommend tensor for clean discriminator; document choice in cell preamble
- Decide whether action policy is uniform-random sampling at each step (cheapest baseline) OR learned softmax over substrate-W (if Gap 3 BCM cell HPs first, use cortex-W as policy and document the GATE)

Research deliverable is the mechanism + candidate ranking + HP/HF thresholds. exp_dev owns experiment-design freedom per [[feedback-no-experiment-design-in-prompts]].

---

## Cortex layer composition GATE (USER addendum-specific)

The cortex-composed variant (ANCHOR 2 / Candidate 6) is the substrate-better-than-brain proofpoint. It requires THREE cortex layer cells landing chain-grade PASS today:
1. TWO_TIER generational W (gap4 cell IN FLIGHT) -- provides architectural pattern
2. BCM slow-learning cortex W (gap3 cell IN FLIGHT) -- provides action policy
3. Modern Hopfield revival (cell IN FLIGHT) -- provides nonlinear value head

GATE: at exp_dev's pre-dispatch check, query verdict status of all three. If any one HARD_FAILS, drop the corresponding component:
- TWO_TIER fail -> stick with single-W substrate (no separation of cortex from per-hop W)
- BCM fail -> use uniform-random action sampling (no cortex action policy)
- MH revival fail -> use cosine value head only (no MH-energy value)

Even with all three components dropped, ANCHOR 1 still ships (with W_world from kv_learned_projection class + V_W cosine + uniform-random action sampling). ANCHOR 1 P_deflated 0.50 stands independently of cortex layer outcomes.

---

End of hand-off.
