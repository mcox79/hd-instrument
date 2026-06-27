# 3X RESEARCH DRILL — Goal-Directed Planning (substrate's missing dlPFC goal-slot)

**Date:** 2026-06-27
**Author:** research (Opus 4.7-1M)
**Trigger:** USER 2026-06-27 ~18:00 PDT — drill high-priority items 3x; weigh testability with elements we have; build experiments to prove out.
**Problem statement:** Substrate has PFC controller that routes per-step from CURRENT STATE, not TOWARD a GOAL. Brain has dlPFC goal-slot (Miller-Cohen 2001) that modulates routing throughout a plan. Without it, substrate is a reactive Q&A engine, not a planning agent.

## SUBSTRATE-MINE FIRST (honest verify-the-referent on prior evidence)

Before drilling forward, what does the substrate ACTUALLY have today (per metrics.json reads, not framing):
- `strips_planning_khop_cpu_v1`: **HARD_PASS** — 2-hop forward-chaining reachability=1.000. Substrate CAN plan when given STRIPS-style precondition operators. This is goal-aware (the chain ends at a goal-test).
- `pfc_controller_per_step_operator_select_v1_smoke`: **HARD_FAIL** at depth=3, lift=+0.03 over single-operator (oracle says +0.43 headroom). The controller IS goal-blind at the gate — it picks operators by `cosine(current_state, op_key)`, never seeing the goal vector.
- `stc_tag_and_capture_v1_smoke`: **HARD_FAIL** (baseline saturated at 0.953 — discriminator regime bug, not mechanism failure)
- `parietal_cortex_spatial_reasoning_v1`: SELFTEST_OK only — no full-data verdict yet
- The prompt's claimed "+0.378 lift at depth=6" is not on disk for v1; either it's the depth-extended REVIVAL cell not yet landed, or it's a forward projection from yesterday's `research_drill_2x_pfc_controller_revival_2026-06-27.md` Angle-B1 hypothesis. **Honest framing: PFC controller has weak directional signal at depth=3 only; deeper-depth lift is hypothesized, not measured.**

What primitives are USABLE TODAY for goal-directed work: `predictive_coding.py` (residual_magnitude as plan-score), `multi_hop.py` (iter_cleanup_chain at depth-15 chain-grade), `iterative_attractor.py` (Modern Hopfield fixed-point), `binding.py` (HRR bind/unbind for state+goal composition), `sequence_memory.py`, plus STRIPS forward-chaining already HARD_PASS.

The substrate is goal-CAPABLE (STRIPS does goal-test), but PFC routing is goal-BLIND. The gap is mechanism-level: **how do we get the goal vector into the per-step routing gate.**

## ANGLE A — PURE MATH: representing + using a goal in HD

**A1. Goal-conditioned gate (multiplicative modulation).** Replace `op = argmax(cos(state, op_keys))` with `op = argmax(cos(state * goal, op_keys))` where `*` is HRR bind. The gate now scores operators against the (state, goal) pair, not state alone. Substrate-native; one extra bind per step. Mante-2013 dPFC analog: context (goal) gates which input dimensions reach the readout. **P=0.50** (deflated; brain-grounded; minimal substrate change; risk = bound state may live in wrong subspace for argmax-against-op-keys).

**A2. Backward induction from goal.** Pre-compute `goal_chain[k] = unbind(goal, op_k)` for each operator. At each step, route by `op = argmax_k cos(state, goal_chain[k])` — picks the operator whose INVERSE applied to the goal best matches current state. Equivalent to A* heuristic-distance-to-goal in HD. **P=0.45** (novel-synthesis cap; HRR involutive unbind is chain-grade; the heuristic is admissible iff op_keys are orthonormal — which they are by-construction in our operator bank).

**A3. Distance-to-goal as plan-score.** Run K parallel candidate plans (per A1 or vanilla) of depth D. Score each leaf by `cos(leaf_state, goal)`. Return the plan with highest score. This is beam search with goal-cosine as utility. The GAP-B note's `substrate_planning_cortex_composed_beam_v1` is exactly this with K=128, D=15. **P=0.50** (already drilled; cost-validated; awaiting compose with goal-conditioned gate from A1).

## ANGLE B — BRAIN: dlPFC goal-slot + ACC error + striatum + preplay

**B1. dlPFC goal-slot as bound role.** Brain (Miller-Cohen 2001; Mante-Sussillo-Newsome 2013) holds goal as a sustained activation pattern in dlPFC that biases readout throughout task. Substrate analog: bind goal-vector into a dedicated `GOAL_ROLE` and keep it in WM bank-0 for the entire plan; every routing decision reads `bank-0 unbind GOAL_ROLE` to recover goal-context. WM is chain-grade K=4096 — capacity is fine. **P=0.55** (high P; brain-existence-proof; substrate has the WM banks already).

**B2. ACC-style error-monitoring + replan.** Brain ACC fires when expected reward / goal-distance diverges from prediction (Holroyd-Coles 2002). Substrate analog: at each step, compute `residual = predicted_next_state - actual_next_state` via `predictive_coding.residual_magnitude`; if `residual > threshold`, REPLAN (restart beam from current state). This is exactly the brain's "online correction" loop. **P=0.50** (predictive_coding.py is in hdlab; residual-mag is well-defined; threshold is the only free parameter).

**B3. Hippocampal preplay / forward sweep.** Pfeiffer-Foster 2013 — rodent hippocampus mentally simulates routes to remembered goal BEFORE moving. Substrate analog: before executing any action, run K=64 parallel forward rollouts of depth-D using `iter_cleanup_chain` with `state_bind_goal` as input; pick the rollout whose final state has highest `cos(leaf, goal)`. This is brain-faithful planning-before-acting. **P=0.55** (multi-hop chain-grade at depth-15 already proves the rollout primitive works; substrate-better-than-brain claim = brain runs 2-3 rollouts, we run 64+).

## ANGLE C — CROSS-DOMAIN: A* / MCTS / hierarchical RL / model-based RL

**C1. HD A* (heuristic search).** Maintain frontier of (state, cumulative_cost) HD bindings. Heuristic h(state) = `1 - cos(state, goal)`. Expand frontier by smallest `f = g + h`. Stop when frontier-min state has `cos(state, goal) > 0.95`. Substrate-mappable: frontier is a multi-bank WM; expansion = one substrate step per node. **P=0.40** (deflated; A* assumes admissible heuristic — cos-distance isn't provably admissible on HD; classical A* on grids works, on substrate not validated).

**C2. HD MCTS (sampling-based search).** UCB selection over candidate actions, rollout to depth D, backprop value, repeat. The GAP-B note already drilled this with `cortex_composed_beam` variant. Substrate-better-than-brain by parallel-N (we have K=4096 WM banks; brain has 2-3 dlPFC slots). **P=0.50** (already-drilled; matches Candidate 2 in GAP-B; depth-D rollout chain-graded primitive).

**C3. Hierarchical RL (options / macro-actions).** Compose 5-step substrate subroutines into 1 macro-action; planning at macro-level has 6^3=216 trajectories vs primitive-level 6^15=4.7e11. Substrate analog: identify chains via existing `multi_hop.iter_cleanup_chain` that recur; bind them as compound operators and add to operator bank; route at macro-level via PFC controller. **P=0.40** (deflated; option-discovery is non-trivial; requires either expert priors or self-supervised chain-mining).

## TOP-2 CELL PROPOSALS (testable NOW with substrate elements we have)

### CELL 1: `pfc_goal_conditioned_gate_v1` (Angle A1 + B1 combined; CHEAPEST decisive test)

**Hypothesis:** PFC controller v1 HARD_FAIL'd at depth=3 (lift +0.03 vs oracle +0.43) because the gate `argmax cos(state, op_key)` is goal-blind. Replacing with `argmax cos(bind(state, goal), op_key)` — and holding goal in a dedicated WM-bank for the whole plan — closes >50% of the oracle gap by depth=6.

**Arms (4 mandatory + 1 diagnostic):**
1. ARM_PFC_COSINE_ARGMAX_V1 — baseline (regression check; should match prior HARD_FAIL)
2. ARM_PFC_STATE_GOAL_BIND_GATE — A1 mechanism (goal modulates per-step gate via bind)
3. ARM_PFC_GOAL_WM_SLOT — B1 mechanism (goal in persistent WM bank; gate reads bank each step)
4. ARM_PFC_COMBINED_A1_B1 — full mechanism (bind + persistent WM slot)
5. ARM_DIAG_ORACLE — unchanged oracle bound (must be >=0.85)

**Discriminator (META_RULE_K — fires at smoke):**
- HARD_PASS: ARM_COMBINED lift over SINGLE_OPERATOR >= +0.20 AND > V1 by >= +0.15 AND cv < 0.10 AND oracle gap closed >50% AND CARDINALITY_OK (5 arms × 2 depths × 5 seeds = 50 units expected)
- MIDDLE_BAND: lift in [+0.08, +0.20)
- HARD_FAIL: ARM_COMBINED <= V1 + 0.03 (mechanism class dead)

**Discriminator-must-survive-scale:** Smoke at full N=8192 at depth=3 AND depth=6 (per Fix #22 + per yesterday's revival B1 insight). Per-arm metrics required (Fix #28) — no verdict_msg-only claims.

**Fairness gates:** Same operator bank, same seeds, same N across arms. SAME_W single goal-vector per seed (different goals across seeds for variance). Goal is sampled fresh per (state, plan) pair from substrate-vocab to prevent goal-leak through op-keys.

**Compute:** Forward-only, no autograd. ~30-60min remote_cpu. CPU-eligible. No GPU needed.

**Why this first:** Cheapest test of the load-bearing claim "goal-blind gate is the bug." If COMBINED HARD_PASS — we have a substrate-grade goal-directed gate primitive. If HARD_FAIL — pivot to Cell 2 (preplay) or rethink.

### CELL 2: `substrate_preplay_beam_to_goal_v1` (Angle B3 + A3 combined; brain-faithful + substrate-better-than-brain)

**Hypothesis:** Substrate can run K=64 parallel forward rollouts to a goal-state before acting (hippocampal preplay analog); pick rollout with max `cos(leaf, goal)`. At synthetic 4-block planning domain (STRIPS-style), substrate solves >=0.70 of goal pairs in <=2x optimal plan-length, beating greedy-1step by >=0.25, and parallel-K=64 beats parallel-K=4 by >=0.10 (the substrate-better-than-brain discriminator).

**Arms (4 mandatory + 1 control):**
1. ARM_GREEDY_1STEP — pick action whose successor has highest `cos(s', goal)`; no lookahead (the "Q&A engine" baseline USER worries substrate currently IS)
2. ARM_PREPLAY_K4_D6 — brain-scale parallel rollouts (Cowan-4 analog)
3. ARM_PREPLAY_K64_D6 — substrate-scale (K=64 parallel; substrate's K=4096 WM banks comfortably support)
4. ARM_PREPLAY_K64_D15 — full-depth (chain-graded primitive depth) + goal-conditioned gate from Cell 1
5. ARM_RANDOM_PLAN (control) — random action sequences; should HARD_FAIL_BASELINE

**Discriminator (META_RULE_K):**
- HARD_PASS_CHAIN_GRADE: ARM_PREPLAY_K64_D15 solve_rate >= 0.70 AND >= GREEDY + 0.25 AND K=64 >= K=4 by >= +0.10 (parallel-scaling discriminator) AND median plan-length <= 2x optimal AND CARDINALITY_OK (5 arms × 3 seeds × 100 goals = 1500 units)
- HARD_PASS_PARTIAL: solve_rate in [0.50, 0.70) AND beats greedy by >=0.15
- MIDDLE_BAND: solve_rate in [0.30, 0.50) AND beats greedy by >=0.05
- HARD_FAIL: solve_rate <= 0.30 OR K=64 within 0.05 of K=4 (parallel doesn't help — rollouts mode-collapsed)
- SANITY_BREACH: RANDOM_PLAN solve_rate > 0.15 — domain too easy

**Discriminator-must-survive-scale:** Smoke runs K=4 at full N=8192 D=6 to verify mechanism fires; full dispatch runs K=64 D=15 across 3 seeds × 100 goals.

**Fairness gates:** Same 4-block BlocksWorld synthetic (6 actions: pick-up, put-down, stack, unstack, move-aside, swap); ground-truth optimal via analytic BFS solver; goals sampled to require >=3 steps (filter trivial goals); META_M7 cross-cell rail required (band [0.08, 0.25]).

**Compute:** Forward-only. W_world fit (closed-form pseudoinverse over (state, action) → next_state): ~100s setup; per-rollout step ~16us; 5 arms × 3 seeds × 100 goals × K_max=64 × D=15 = ~30-60min remote_cpu. CPU-eligible.

**Substrate elements used (verified in hdlab/):**
- `multi_hop.iter_cleanup_chain` (chain-grade depth-15 rollout primitive)
- `iterative_attractor` (Modern Hopfield cleanup at each rollout step)
- `binding.bind/unbind` (state-goal composition; HRR involutive)
- `predictive_coding.residual_magnitude` (per-rollout uncertainty signal for tie-breaking)
- `working_memory` multi-bank (parallel-K slot capacity; chain-grade K=4096)

## DISPATCH RECOMMENDATION

**Order:** Cell 1 FIRST (cheaper, faster, fixes the goal-blind gate directly — the smallest possible Δ from today's HARD_FAIL). If Cell 1 HARD_PASS, Cell 2 reuses the goal-conditioned gate as ARM_PREPLAY_K64_D15's per-step routing. If Cell 1 HARD_FAIL — the gate is not the bottleneck; Cell 2 alone tests whether multi-rollout-beam-with-goal-scoring can rescue planning even with a goal-blind gate (the leaf-scoring step uses goal).

**Decision matrix:**
- BOTH HARD_PASS → substrate goal-directed planning capability vindicated; cap_map opens "PFC goal-slot + preplay-beam" row; pivot to richer domains (6-block, hierarchical)
- Cell 1 PASS, Cell 2 FAIL → gate works but rollout-beam mode-collapses; pivot to Modern Hopfield as value head (GAP-B Candidate 2)
- Cell 1 FAIL, Cell 2 PASS → leaf-scoring is enough; the gate doesn't need goal-awareness; pivot to scaling Cell 2
- BOTH FAIL → substrate's goal-directed compose is bottlenecked elsewhere (likely W_world fidelity at depth>=10); pivot to GAP-B Candidate 4 (hippocampal-replay-trained world model)

**Routing:** Spawn `hdi_exp_dev` to pre-reg both cells per envelope-fail-bands + author smoke. Per fix #26, run `predispatch_check.py` for prior evidence of either anchor. Per Fix #28, all framing claims from per-arm metrics.json reads, not verdict_msg.

**Honest priors (lit-scan calibration penalty applied):** Cell 1 P=0.50 (deflated from 0.65; brain-grounded; minimal mechanism delta; substrate already passes simpler oracle-aware tests). Cell 2 P=0.50 (matches GAP-B Candidate 1 prior; multi-hop chain-grade at depth-15 + STRIPS HARD_PASS provides converging evidence the rollout primitive works). Neither is high-P; together they discriminate the failure mode and either way produce decision-grade evidence about WHERE the goal-blindness lives.
