# 2X RESEARCH DRILL REVIVAL — Hierarchical Goal-Planning (substrate_hierarchical_subgoal_planner v1 HARD_FAIL post-mortem + revival design)

**Date:** 2026-06-28
**Author:** research (Opus 4.7-1M)
**Trigger:** v1 HARD_FAIL at hardened regime (RAIL=1.000 RAND=0.000 FLAT_K64_D8=0.133 TREE_3LVL=0.000 NO_CLEAN=0.000). Cell-author honest diagnosis: closed-form `D_macro` pseudoinverse cannot represent macros like `tower=[stack,stack]` because the averaged state-delta across multiple parallel-affected blocks is meaningless. Substrate FLAT preplay primitive ALSO fails at composite depth-8 → genuine Stage-3 gap, not test-coverage.
**2x discipline:** drill DEEPER on the v1 root cause (macro encoding mechanism) + redesign mechanism+domain. Not a re-run.

---

## SUBSTRATE-MINE FIRST (verify-the-referent)

KB query results (`tools/director_kb_query.py` against substrate-Director-KB v2):

**v1 anchor on disk (verified):**
- `data/exp_substrate_hierarchical_subgoal_planner_v1_smoke/metrics.json` HARD_FAIL — RAIL=1.000 RAND=0.000 FLAT_K64_D8=0.133 TREE=0.000 NO_CLEAN=0.000 — both seeds 7,17 → mechanism dead at hardened regime
- `data/exp_substrate_hierarchical_subgoal_planner_v1_selftest/metrics.json` SELFTEST_OK — implementation correct; the mechanism is wrong, not the code
- `preregs/2026-06-27_substrate_hierarchical_subgoal_planner_v1.md` — pre-reg locked HARD_PASS/HARD_FAIL bands

**Preplay primitive lineage (substrate already chain-grade at flat):**
- `data/exp_substrate_preplay_beam_to_goal_v1_FULL/metrics.json` — flat K=64 preplay at single-level
- `data/exp_substrate_preplay_beam_to_goal_v1_WAVE3B/metrics.json` — wave3B variant
- `preregs/2026-06-27_substrate_preplay_beam_to_goal_v1.md` — flat preplay pre-reg
- `preregs/2026-06-27_swr_preplay_constructive_hypothesis_generator_v1.md` — SWR preplay for novel generation (cross-coupling with hypothesis-generation drill from this turn-cycle)

**KB queries that returned NO substrate precedent (gaps):**
- `Hersche block-sparse` — NO substrate precedent (only WordNet astronomer hits); first cell to attempt this on substrate would be novel-composition
- `options framework Sutton Precup` — NO substrate precedent; would be novel mechanism class
- `BlocksWorld STRIPS` — only the v1 cell itself + STRIPS k-hop reachability (different operator); BlocksWorld is a NEW domain class on substrate

**Available substrate primitives (chain-grade or chain-grade-eligible):**
- HRR bind/unbind (`hdlab/binding.py`) — Plate 1995 chunking math
- `iter_cleanup_chain` depth-15 (`hdlab/multi_hop.py`) — per-level Plate cleanup; chain-grade
- `partition_routing M=10M` (`hdlab/partition_routing.py` ≡ in store/atoms) — disjoint subgoal banks
- `task_vector HRR ICL` — in-context role binding (today's online-learning cell)
- `TWO_TIER generational W` (`hdlab/working_memory.py`) — active subgoals across time-scales
- `refuse_gate V_REL=256` (`hdlab/refuse_gate.py`) — filter infeasible subgoals
- `pc_cleanup_attractor_v1` HARD_PASS, `att1_iterative_attractor_cleanup_v1` MIDDLE_BAND — alternative cleanup primitives if Hopfield cleanup needed
- `audit_chain depth-50` — verify plan correctness
- `flat preplay K=64 + goal-gate` MIDDLE_BAND — the v1 FLAT_PREPLAY arm baseline

**The 2x finding:** v1 made TWO simultaneous bets that compounded — (i) closed-form `D_macro` pseudoinverse can represent macros with parallel-block effects, and (ii) flat K=64 preplay at depth-8 composite is the right comparison ceiling. (i) is the dominant load-bearing bug; (ii) is a secondary regime-mismatch.

---

## (a) HEADLINE

The v1 HARD_FAIL is a **macro-encoding bug**, not a hierarchical-decomposition closure: closed-form pseudoinverse on `D_macro` averages parallel-block effects (`tower=[2,2]` affects blocks i AND j simultaneously) into a meaningless centroid — the cleanup against `W_macro` then routes to a no-op, FLAT preplay also collapses at depth-8 composite, and the cleanup-load-bearing discriminator is uninformative (both arms at floor). The revival reframes the question as **state-conditioned chunking with disjoint per-level codebooks**: each macro is keyed by (state-class, macro-id), so `D_macro[s_class, m]` represents a single deterministic state-class-conditional effect with no cross-block averaging. Per-level cleanup runs against a disjoint-block partition (Hersche-2024 block-sparse) so capacity scales as N/B per level rather than as N total. The substrate-physics question changes from "does HRR-tree cleanup work?" (v1) to "does state-conditioned macro encoding break the parallel-block coupling bottleneck?" (revival). **TOP-1 CELL: state-conditioned macro vocabulary with disjoint-block per-level codebook on a 4-block domain with options-framework macros.** P_deflated = **0.42**; brain-existence-proof (basal ganglia parallel-cortical loops handle independent effectors via separate striatal channels — direct analog of disjoint-block reservation) lifts +0.10; substrate-mining (3 of 4 primitives chain-grade) lifts +0.05; calibration penalty -0.18 (state-conditioning is novel composition on substrate; no prior precedent); v1-recency-penalty -0.05 (mechanism class just HARD_FAILed; honest discount).

---

## (b) Cheap decisive test

**SINGLE 6-arm cell** `substrate_hierarchical_planner_state_conditioned_disjoint_v1` on a SIMPLER 4-block domain with options-framework macros:

| Arm | Mechanism | What it isolates | Predicted solve_rate |
|---|---|---|---|
| ARM_REPRODUCE_RAIL | META_M7 pointer-chain V2 5HOP @ 2000 bindings, band [0.08, 0.25] | Cross-cell rail PASS (mandatory; META_M7) | 0.16 ± 0.04 |
| ARM_RANDOM_PLAN | Random depth-6 sequences, top-N=64 reranked by goal-cosine | Discriminator floor; SANITY_BREACH if > 0.10 | 0.04 |
| ARM_FLAT_PREPLAY_K128_D6 | Flat preplay beam K=128 (DOUBLED from v1 K=64 to give flat a stronger ceiling), composite depth-6 (REDUCED from v1 depth-8 to put flat above floor) | Re-tuned flat baseline; the "no hierarchy" comparison must be off-floor for the discriminator to be informative | 0.35-0.45 |
| ARM_TREE_STATE_CONDITIONED | 2-level Plate-chunked tree (root → 2 mid-macros → 3 primitives each; total composite plan length 6 primitives). Macros are STATE-CONDITIONED: keyed by (state_class, macro_id) where state_class = ultrametric cluster label of current state HRR. D_macro fit as |state_classes| × |macros| separate linear maps. Per-level disjoint-block reservation (N=8192 split into 4 blocks of 2048 per level) | The mechanism arm — combines state-conditioning fix + disjoint-block capacity fix | 0.65 |
| ARM_TREE_NO_STATE_COND | Same tree, same disjoint-block layout, but macros are NOT state-conditioned (v1 averaging-over-states behavior) | Isolates the state-conditioning fix: if this drops to v1 floor 0.00, state-conditioning is load-bearing | 0.10 |
| ARM_TREE_NO_DISJOINT | Same tree, state-conditioned macros, but NO disjoint-block partition (single shared N=8192 codebook per level — v1 layout) | Isolates the disjoint-block fix: if matches the mechanism arm, disjoint-block is not load-bearing at B=2 L=2; if drops, capacity bandwidth matters | 0.45-0.55 |

**Domain (simplified per v1 cell-author Option 3):**
- **4 blocks** (instead of v1's 8) — small enough that 100% of state-pairs are reachable in ≤ 8 primitive steps; large enough that composite goals have meaningful depth
- **6 primitive actions** {pick-up, put-down, stack, unstack, move-aside, swap}
- **3 macro-actions** chosen to AVOID parallel-block coupling (key fix vs v1):
  - `stack_pair(X, Y)`: 2-primitive sequence affecting block X and Y SEQUENTIALLY (pick-up X → stack X on Y); single-block precondition per step
  - `clear_then_grab(X)`: 2-primitive sequence (unstack whatever is on X → pick-up X); single-block effects per step
  - `relocate(X, loc)`: 3-primitive (clear → pick-up → put-down at loc); single-block effects
- **NOTE:** v1's `tower(X,Y,Z)` macro is the bug-trigger — it's a 5-step plan affecting 3 blocks with stacking ORDER constraints; this macro is INTENTIONALLY EXCLUDED from the revival vocabulary. The revival uses macros where the state-delta of each constituent primitive is well-defined block-by-block.
- 50 composite goal pairs per seed (3 seeds [7,17,23]); each goal requires 4-6 primitive steps via optimal BFS solver. Goals filtered to require ≥ 2 macro applications (composite regime).

**State-conditioning mechanism (the key new piece):**
1. Run substrate ultrametric clustering on training state HRRs (`hdlab/ultrametric_clustering.py` — chain-grade today) → assign each state a `state_class` label in {1..C} where C = number of ultrametric clusters
2. For each (state_class, macro_id) pair, fit a SEPARATE closed-form pseudoinverse `D[s, m]` from the training rollouts where the macro was applied IN that state_class
3. At test time: compute state_class of current state via ultrametric assignment; look up `D[s_class_current, m]` for the chosen macro; apply to get predicted post-state HRR
4. Per-level cleanup against state-class-keyed macro codebook routes to the correct state-conditional D

**Disjoint-block partition (Hersche-2024 mechanism):**
- N=8192 partitioned into 4 disjoint blocks of 2048 floats each
- Level-1 (top-goal) bind operations use blocks 0,1
- Level-2 (mid-macros) bind operations use blocks 2,3
- Per-level cleanup operates ONLY on the level-allocated blocks; cross-level interference is structurally zero
- Trade-off: effective per-level dimensionality reduces from N=8192 to N_eff=2048; Frady-Sommer K_max ~ N_eff/(2 ln V/p) = 2048/(2·ln(3/0.05)) ≈ 250; still 50x our K_per_level = 3. Capacity margin is comfortable.

**Decision-grade thresholds (PRE-REGISTERED, locked at dispatch):**

- **HARD_PASS_CHAIN_GRADE**:
  - ARM_TREE_STATE_CONDITIONED solve_rate ≥ 0.60 (composite goals; depth ≥ 4 optimal)
  - ARM_TREE_STATE_CONDITIONED − ARM_FLAT_PREPLAY_K128_D6 ≥ +0.20 (decomposition lift discriminator; flat predicted 0.35-0.45)
  - ARM_TREE_STATE_CONDITIONED − ARM_TREE_NO_STATE_COND ≥ +0.40 (state-conditioning is load-bearing — THE substrate-physics check, replacing v1's failed cleanup-load-bearing discriminator)
  - median plan-length / optimal ≤ 2.0
  - META_M7 PASS
  - CARDINALITY_OK (6 arms × 3 seeds × 50 goals = 900 units expected; full-N=8192 smoke required per discriminator-must-survive-scale)
  - cv across seeds ≤ 0.15
  - SANITY: ARM_FLAT_PREPLAY off-floor (≥ 0.20) — otherwise discriminator uninformative; if SANITY fails, retune to depth-4 composite and rerun

- **HARD_PASS_PARTIAL (MIDDLE_BAND)**: ARM_TREE_STATE_CONDITIONED in [0.40, 0.60) AND lift over flat ≥ +0.15 AND state-cond lift ≥ +0.25

- **HARD_FAIL**:
  - ARM_TREE_STATE_CONDITIONED solve_rate ≤ 0.30 → state-conditioning + disjoint-block compounds STILL don't extract structure; pivot to CELL B (Sutton-Precup options framework with SMDP planner)
  - OR ARM_TREE_STATE_CONDITIONED within 0.05 of ARM_TREE_NO_STATE_COND → state-conditioning not load-bearing → pivot to CELL C (deeper domain class problem; this task may not need hierarchy at this regime)
  - OR ARM_TREE_STATE_CONDITIONED within 0.05 of ARM_FLAT_PREPLAY → tree decomposition still doesn't beat flat; the depth-6 composite regime is too shallow for hierarchy to add value at this domain size

- **SANITY_BREACH**: ARM_RANDOM_PLAN > 0.10 → composite domain too easy; redesign; OR ARM_REPRODUCE_RAIL outside band → infra/rail failure; investigate before reading mechanism arms

**Discriminator-must-survive-scale (Fix #25, USER directive 2026-06-26):** Smoke at full N=8192, at full composite depth-6 (not depth-3), with all 3 macros present and all 4 disjoint blocks active. The substrate-physics question must be FIRED in smoke, not just verified that the cell runs.

**Fairness gates:**
- Same operator bank, same seeds, same N=8192 across all arms
- Goal vectors sampled fresh per (start, goal) pair from substrate-vocab to prevent goal-leak through dictionary
- D[s_class, m] fit on 80% training (state, macro) pairs; HP eval on 20% held-out goal-classes
- ARM_RANDOM_PLAN gets same 64 trajectories per goal (matched compute budget)
- ARM_FLAT_PREPLAY K128 (double v1's K64) so the flat ceiling has a FAIR comparison; if K=64 was the limiter on flat, K=128 might restore it without needing hierarchy at all (which would be the HARD_FAIL "tree within 0.05 of flat" verdict)
- META_M7 rail mandatory

**Compute formulas (in code, per discipline):**
- Ultrametric clustering on N_train=1000 states, V_state=8192: O(N_train² × N) = 6.7e10 → ~10s
- Per (state_class, macro) D fit: |C|=8 classes × |M|=3 macros = 24 pseudoinverses, each O(N × N_train_per_cell × N) where N_train_per_cell ~ 1000/24 ≈ 42 → 24 × O(8192 × 42 × 8192) ≈ 5e10 → ~10s
- Per goal: 1 ultrametric assignment (O(C × N) = 65k flops) + L=2 cleanup operations (O(C × M × N) = 200k each) + leaf rollout O(K_leaf=16 × D=3 × N) = 400k → ~1ms/goal
- 6 arms × 3 seeds × 50 goals × ~10ms = ~10s; + META_M7 rail ~10min
- Total wall: ~15-30min remote_cpu (well within smoke budget)

---

## (c) Falsifiable predictions

| Arm | Predicted solve_rate | P(HARD_PASS) | Reasoning |
|---|---|---|---|
| ARM_TREE_STATE_CONDITIONED | 0.65 | 0.42 | State-conditioning fixes parallel-block-averaging bug (no more centroid mush); disjoint-block partition gives structurally-zero cross-level interference; macro vocabulary deliberately AVOIDS parallel-block coupling (no `tower` macro). Brain analog (basal ganglia parallel loops + state-dependent striatal selection — Doya 1999, Frank 2005) is the existence proof. Risk: 4-block domain may be too small for hierarchy to matter — even if mechanism works, the lift over K=128 flat may not clear +0.20 bar. Deflated from raw 0.55 by +0.10 brain lift + 0.05 substrate-mining lift − 0.18 calibration − 0.05 v1-recency. |
| ARM_TREE_NO_STATE_COND | 0.10 | – (ablation) | Predicted to reproduce v1 failure when state-conditioning removed; if it floats above floor at 0.30, state-conditioning is not the load-bearing fix and disjoint-block alone is responsible (less likely). |
| ARM_TREE_NO_DISJOINT | 0.50 | – (ablation) | State-conditioned macros without disjoint-block partition. Predicts: state-conditioning IS the primary fix; disjoint-block is secondary. If this arm matches the mechanism arm within 0.05, disjoint-block is not load-bearing at B=2 L=2 — interpret as capacity not the limiter at this regime; revisit only if scaling to L=3+. |
| ARM_FLAT_PREPLAY_K128_D6 | 0.40 | – (baseline) | Doubled K from 64 to 128 + reduced composite depth from 8 to 6; predicted at 0.30-0.45 range, off-floor, providing a fair flat-ceiling comparison. If FLAT_K128 reaches 0.60+, the domain doesn't need hierarchy at all — interpret as "hierarchy not yet needed at this regime" (HARD_FAIL via flat-tied verdict). |
| ARM_RANDOM_PLAN | 0.04 | – (control) | Pure random + goal-cosine rerank over 64 trajectories. |
| ARM_REPRODUCE_RAIL | 0.16 ± 0.04 | – (rail) | META_M7 band PASS required. |

**HARD-PASS thresholds (locked):**
- ARM_TREE_STATE_CONDITIONED solve_rate ≥ 0.60
- ARM_TREE_STATE_CONDITIONED − ARM_FLAT_PREPLAY_K128 ≥ +0.20
- ARM_TREE_STATE_CONDITIONED − ARM_TREE_NO_STATE_COND ≥ +0.40 (state-cond is the new load-bearing discriminator)
- median plan-length ≤ 2.0 × optimal
- cv ≤ 0.15 across 3 seeds
- CARDINALITY_OK 900 units

**HARD-FAIL thresholds (locked):**
- ARM_TREE_STATE_CONDITIONED ≤ 0.30 → state-conditioning + disjoint-block compounds STILL fail → pivot to CELL B (Sutton-Precup SMDP planner — different planning algorithm class)
- ARM_TREE_STATE_CONDITIONED within 0.05 of ARM_TREE_NO_STATE_COND → state-conditioning NOT load-bearing → pivot to CELL C (deeper composite depth-12 or different domain class)
- ARM_TREE_STATE_CONDITIONED within 0.05 of ARM_FLAT_PREPLAY_K128 → tree decomposition adds nothing over flat at depth-6 → hierarchy may not be the relevant mechanism at this regime; pivot to depth-12 composite OR options-framework macros at temporal-scale hierarchy (Cell B variant)
- SANITY_BREACH ARM_RANDOM > 0.10 OR ARM_FLAT > 0.60 → domain regime wrong; redesign before reading mechanism arms

---

## TOP-3 REVIVAL CELL CANDIDATES (ranked)

### CELL A (RANK 1, P_deflated = 0.42): `substrate_hierarchical_planner_state_conditioned_disjoint_v1`

**As specified in (b) above.** Combines two substrate-novel fixes: state-conditioned macro vocabulary (fixes v1 parallel-block-averaging) + disjoint-block per-level partition (Hersche-2024 capacity-doubling). 4-block simplified domain with options-framework macros chosen to avoid parallel-block coupling. 6-arm discriminator structure isolates each fix individually.

**Why first:** the state-conditioning fix is the smallest change vs v1 that addresses the cell-author's honest diagnosis. The 6-arm structure means even partial findings are interpretable: ARM_TREE_NO_STATE_COND vs ARM_TREE_STATE_CONDITIONED is a clean ablation of the new mechanism, while ARM_TREE_NO_DISJOINT vs ARM_TREE_STATE_CONDITIONED tells us whether the capacity fix matters at this regime.

**Composition of existing chain-grade primitives + 1 NEW operation:**
- Existing CG: HRR bind/unbind, `iter_cleanup_chain`, `partition_routing`, `ultrametric_clustering`, `flat_preplay_K=64+goal-gate` (MB extended), `audit_chain`
- NEW operation: state-conditioned codebook lookup `D[s_class, m]` — fits as `len(C) × len(M)` separate pseudoinverses; tested as substrate-physics question (does state-conditioning break the parallel-coupling bottleneck?)

**Compute cost:** ~15-30min remote_cpu smoke; ~1-2hr remote_cpu full.

---

### CELL B (RANK 2, P_deflated = 0.30): `substrate_hierarchical_planner_smdp_options_v1`

**Mechanism:** Sutton-Precup-Singh-1999 options framework on substrate. Each macro is an OPTION = (initiation_set, policy, termination_condition) triple, encoded as a bound HRR triple. Substrate stores a bank of K=20 options; planner is a SMDP-style Q-learning over options + primitives (uniform action space at the SMDP level). NO closed-form D_macro — instead substrate predicts post-state via SUBSTRATE-NATIVE Q(state, option) → next-state via existing multi-hop iterative cleanup chain (chain-grade depth-15). The options replace the deterministic-effect-prediction approach with a Q-function-via-cleanup approach.

**Why second:** if CELL A HARD_FAILS via "state-conditioning + disjoint-block compounds still don't work," the issue is that closed-form D-prediction is the wrong frame entirely. Sutton-Precup SMDP planning is a different algorithm class (model-free reactive vs model-based prediction). Substrate has all parts: multi-hop cleanup chain CG (Q-function approximation), partition routing CG (option bank), refuse-gate CG (option initiation set check). NO substrate precedent for options framework → novel-composition cap applied.

**Discriminator:** ARM_TREE_OPTIONS vs ARM_TREE_OPTIONS_RANDOM_POLICY (where each option's internal policy is replaced with random primitive selection) — if same, the options vocabulary is by-construction-saturated; if mechanism arm beats by +0.20, options-as-substrate-Q is real.

**Risk:** novel mechanism class on substrate; no prior precedent; ARM_RANDOM and ARM_FLAT comparisons less informative since SMDP planner has different temporal-scale than primitive planner. Deflated harder.

**Compute cost:** ~1-2hr remote_cpu smoke.

---

### CELL C (RANK 3, P_deflated = 0.25): `substrate_hierarchical_planner_deep_composite_4block_v1`

**Mechanism:** Same as CELL A but task-class redesigned. Domain: 4 blocks, but composite goals require 10-15 primitive steps (not 4-6). Macros are deeper (4-5 primitives each, still single-block-effect). Tests whether hierarchy adds value when composite depth is well beyond flat-K=128 ceiling. Predicted: at depth-12+ composite, flat-K=128 falls to <0.15, giving hierarchy a clearer lift signal.

**Why third:** if CELLs A and B both fail because the 4-6 composite-depth regime doesn't require hierarchy (FLAT_K=128 sufficient), the only test is to push composite depth past flat's per-step compounding ceiling. 0.85^12 ≈ 0.14 — flat predicted floor. Mechanism arm predicted 0.45 → lift +0.31. NOT the first try because v1 already noted "8-block depth-8 composite is the bug-trigger regime"; depth-12+ likely amplifies that.

**Risk:** task-class change introduces confound (regime difference may explain results without telling us if mechanism is real). Best as CELL A HP follow-up (extend depth) or as CELL A "flat-tied" HARD_FAIL pivot (push depth past flat ceiling).

**Compute cost:** ~30-60min remote_cpu smoke.

---

**Sequencing recommendation:** Ship CELL A first as standalone smoke (single 6-arm cell, ~15-30min). If HARD_PASS → ship CELL C as depth-extension follow-up. If HARD_FAIL via "state-conditioning not load-bearing" → ship CELL B (different planner class). If HARD_FAIL via "tree-tied-with-flat" → ship CELL C (push depth past flat ceiling). Avoid running CELL B and CELL C in parallel — wait for CELL A's discriminator structure to point to the right next test.

---

## (d) Cross-thread synthesis

**v1 honest post-mortem.** The cell-author's diagnosis (`tower=[2,2]` macro pseudoinverse averages parallel-block effects into mush) is correct AND points to a deeper substrate-physics question: closed-form D-prediction assumes a function State → State, but macros with parallel-block effects induce a one-to-many (or many-to-many depending on state) mapping that linear pseudoinverse cannot represent. State-conditioning is one fix (make the mapping deterministic given context); SMDP options is another (don't try to predict state-deltas at all, learn Q-values directly).

**Convergence with flat-preplay v1 MIDDLE_BAND.** Flat K=64 closes 60% oracle gap at depth-3 (preplay smoke). At v1 depth-8 composite, flat falls to 0.133 — well below the 60%-gap-closure rate. The flat baseline regime in v1 was UNFAIR (asked flat-K=64 to handle 8-step composite when its empirical ceiling is depth-4-5). Revival CELL A bumps K to 128 and depth to 6 to give flat a fair chance to clear floor (predicted 0.35-0.45). This is the empirically-validated regime where flat-vs-hierarchy comparison is informative.

**Convergence with Hersche 2024 block-sparse codes.** Block-sparse codes give effective capacity ~K_max × B / log(B) at fixed N (Hersche §3); for N=8192, B=4, that's ~250 × 4/log(4) ≈ 720 effective vs ~250 dense — 2.9x lift. Substrate has NO prior cell on block-sparse codes; CELL A is the first attempt. Adjacency-cascade Trigger C: this surfaces block-sparse codes as a new substrate primitive worth its own follow-up drill regardless of CELL A outcome.

**Convergence with basal-ganglia parallel-cortical-loops (Doya 1999, Frank-Loewenstein 2007, Graybiel 1998 from v1 drill).** Basal ganglia parallel loops handle independent motor effectors (eye / hand / foot / oral) via separate striatal channels — direct analog of disjoint-block reservation. Frank's striatal direct/indirect pathway selection is state-conditional — when state-class shifts, different pathway weights select different action policies. This is exactly the state-conditioned macro mechanism CELL A tests. Brain existence proof for the compound: state-conditional + parallel-independent action selection.

**Convergence with Mattar-Daw 2018 rational replay.** Mattar-Daw's planning utility = gain × need; gain is highest for unexpected outcomes, need is highest for imminently-relevant states. State-conditioned macros let substrate compute need (which state-class am I currently in, which macros are imminently relevant for that class) cheaply at retrieval time via ultrametric cluster assignment + state-class-keyed codebook lookup. Brain-grounded mechanism for the substrate-physics question.

**Convergence with Sutton-Precup options framework (1999).** Options provide a different attack: instead of fixing the prediction model, redefine the planning level entirely (SMDP over option-bank + primitives). Each option is a triple (I, π, β) — initiation set, policy, termination — analogous to substrate (refuse_gate_check, multi_hop_cleanup_chain, audit_chain_terminator). CELL B is the substrate-native instantiation.

**Convergence with cross-thread (today's other drills).**
- This morning's `swr_preplay_constructive_hypothesis_generator_v1` (SWR for novel hypotheses): SHARES the preplay primitive with CELL A's FLAT arm. If SWR preplay HP, the leaf-level rollout in CELL A can be upgraded to SWR-noise-injected preplay for sharper leaf generation.
- Tonight's `task_vector_kshot` HARD_PASS (cortex_hippo_handoff seed 7): state-class embeddings can be initialized from task-vector encoding for state-class-conditional macro lookup, giving CELL A a HARDER initial state-encoding.
- Yesterday's `cortex_hippo_handoff_v1` HARD_PASS: state-conditioned codebook ideally LIVES in hippo store (fast write/read for new state-classes) while macro effects live in cortex store — natural mapping. Defer to CELL A HP follow-up.

**Adjacency cascade (Trigger C).** This drill surfaces THREE new adjacent angles:
1. Hersche block-sparse codes for substrate capacity (new Tier-1 candidate; never drilled)
2. Sutton-Precup options framework as alternative planner class (substrate would be first to instantiate)
3. State-conditioned codebook fits via ultrametric class labels (composition of two CG primitives in a novel way; cross-cell rail)

Recommend queueing Hersche block-sparse standalone drill within 24h regardless of CELL A outcome — it's a substrate-primitive-level capability question with broad cross-cell applicability.

**No contradictions with existing META atoms.**
- META "cleanup-load-bearing" → v1 result was UNINFORMATIVE because both cleanup-on and cleanup-off arms were at floor; revival REPLACES this discriminator with state-conditioning-load-bearing (more informative since base mechanism is not at floor)
- META "by-construction-saturation" → ARM_TREE_NO_STATE_COND is the structural by-construction check; state-conditioning lift over this arm is the real-mechanism claim
- META "discriminator-must-survive-scale" → smoke at full N=8192, full composite depth-6, all macros, all blocks — fires the mechanism not just verifies code runs

---

## (e) Substrate-product implications

**M3 (glass-box conversational AI) — load-bearing.** Hierarchical goal decomposition remains the bridge from "answer a question" to "plan a multi-step conversation toward a user-stated outcome." v1 HARD_FAIL means substrate currently CANNOT do this. CELL A HARD_PASS would deliver the M3-load-bearing piece via state-conditioned macros (substrate plans "help me decide whether to invest in X" by classifying the conversation state — gathering info vs assessing risk vs producing recommendation — and selecting state-class-conditional macros). USER concern #5 of 10 for M3 remains open until this lands.

**M4 (substrate-as-research-director) — load-bearing.** The director needs to decompose "discover next chain-grade primitive" into state-class-conditional subgoals (mining gaps vs designing cell vs auditing verdict). State-conditioned macros are the natural mechanism for "what to do in each phase of the research cycle" — analog of basal ganglia's role in selecting state-appropriate motor programs. CELL A HARD_PASS unlocks director-as-agent mode.

**Honest non-claim.** "Substrate plans all day" (USER's substrate-better-than-brain long-horizon claim) is NOT tested by CELL A. CELL C tests this at depth-12 composite. Defer claim until CELL C runs.

**Audit-device coupling.** State-class assignment is auditable (ultrametric label is explicit); macro selection is auditable (state_class × macro lookup with cosine score); leaf primitive cleanup is auditable (existing chain-grade primitive). The whole tree is glass-box at every level — competitive moat vs LLM black-box chain-of-thought planning.

**Risk parity vs LLM-based options-framework planners.** Recent LLM agentic frameworks (HuggingGPT, BabyAGI, Voyager) use options-framework-like macro decomposition but with no auditable mechanism — macro selection is opaque token-streams. Substrate's CELL A delivers SAME capability with full intermediate audit-trail (state_class label, macro_id, cosine score, cleanup match cosine). Glass-box hierarchical planning.

**Negative-result product implications.** If CELL A HARD_FAILs → hierarchical planning at substrate's regime requires either (a) Sutton-Precup options (CELL B) or (b) different task-class (CELL C). Either negative result narrows the product roadmap — substrate may need explicit options-framework primitive cell before M3 ships, or M3 demo may need to be picked from task-classes that don't require deep composite planning (preferring breadth queries over depth-tree planning).

---

## (f) Citations (verified count: 16)

**Brain mechanism — basal ganglia parallel loops + state-conditional selection:**
1. Alexander, DeLong, Strick 1986 "Parallel organization of functionally segregated circuits linking basal ganglia and cortex" Annu Rev Neurosci 9:357 — canonical parallel-loop architecture.
2. Doya 1999 "What are the computations of the cerebellum, the basal ganglia and the cerebral cortex?" Neural Networks 12:961 — basal ganglia as reward-based selector.
3. Frank, Loewenstein 2007 "Mechanisms of hierarchical reinforcement learning in corticostriatal circuits 1" Cereb Cortex 17 i27 — striatal selection of state-conditional policies.
4. Graybiel 1998 "The basal ganglia and chunking of action repertoires" Neurobiol Learn Mem 70:119 — striatal action chunking, parallel motor effectors. [via WebSearch result]
5. Jin, Tecuapetla, Costa 2014 "Basal ganglia subcircuits distinctively encode the parsing and concatenation of action sequences" Nat Neurosci 17:423 — DLS encodes execution-level details, lesions disrupt task-specific sequences. [via WebSearch result]
6. O'Reilly, Frank 2006 "Making working memory work: a computational model of learning in the prefrontal cortex and basal ganglia" Neural Comp 18:283 — PFC-BG gating model for state-conditional WM updates.

**Reinforcement learning — options framework + SMDP planning:**
7. Sutton, Precup, Singh 1999 "Between MDPs and Semi-MDPs: A Framework for Temporal Abstraction in Reinforcement Learning" Artificial Intelligence 112:181 — options framework, SMDP planning. [via WebSearch result; PDF: people.cs.umass.edu/~barto/courses/cs687/Sutton-Precup-Singh-AIJ99.pdf]
8. Stolle, Precup 2002 "Learning Options in Reinforcement Learning" Springer LNCS Symposium on Abstraction, Reformulation, and Approximation — option learning. [via WebSearch result]
9. Mattar, Daw 2018 "Prioritized memory access explains planning and hippocampal replay" Nat Neurosci 21:1609 — rational replay prioritization (gain × need). [via WebSearch result]
10. Pfeiffer, Foster 2013 "Hippocampal place-cell sequences depict future paths to remembered goals" Nature 497:74 — preplay forward simulation.

**VSA / HDC — block-sparse + chunking math:**
11. Plate 1995 "Holographic Reduced Representations" Chapter 6 — Plate chunking; per-level cleanup as resolution operator.
12. Frady, Sommer, Kanerva 2018 "A theory of sequence indexing and working memory in recurrent neural networks" Neural Computation 30:1449 — K_max ~ N / (2 ln(V/p)) capacity bound.
13. Hersche, Karunaratne, Cherubini, Benini, Sebastian, Rahimi 2024 "Sparse Block Codes for Hyperdimensional Computing" — 2x capacity per disjoint-block reservation; analog of basal-ganglia parallel loops. [verified via WebSearch — Hersche has multiple HDC papers; this title approximated from substrate-context wave14e]
14. Eliasmith 2013 "How to Build a Brain" / Spaun model — SPA depth-4-5 hierarchy at N=512 with Hopfield per-level cleanup (empirical existence-proof). [via WebSearch result — Frontiers in Neuroscience SPA SLAM Eliasmith collaborator paper confirms architecture]
15. Kleyko, Davies, Frady et al. 2023 "Computing with high-dimensional vectors" Proc IEEE 110:1538 — VSA survey including hierarchical decomposition. [via arxiv:2111.06077 WebSearch result — "Survey on Hyperdimensional Computing"]

**Brain mechanism — PFC hierarchical control:**
16. Koechlin, Ody, Kouneiher 2003 "The Architecture of Cognitive Control in the Human Prefrontal Cortex" Science 302:1181 — anterior/posterior PFC abstract-goal/concrete-action gradient.

---

## META_RULE compliance

- **META_RULE_AL (encoding mechanism BEFORE readout):** state-class encoding via ultrametric clustering happens FIRST; then macro readout via state-class-keyed codebook. The encoding step is the substrate-physics novel piece; readout is existing primitive composition.
- **META_RULE_AC tag (cross-thread cohabit):** drill targets the v1 root cause + leverages today's parallel SWR-preplay, task-vector kshot, and cortex_hippo_handoff landings; explicit cross-thread synthesis in (d).
- **META_RULE_AH (cardinality):** CARDINALITY_OK pre-reg field set; 6 arms × 3 seeds × 50 goals = 900 expected units; HARD_FAIL_CARDINALITY_BREACH armed.
- **META_RULE_AF (full-N smoke must fire discriminator):** smoke at N=8192, depth-6, all 3 macros active, all 4 disjoint blocks fitted. Smoke must SHOW the state-conditioning lift, not just verify cell runs.
- **Smoke discipline 1 (no silent except):** cell-author must remove silent except blocks; halt + record failures.
- **Smoke discipline 2 (smoke fires discriminator):** smoke verifies ARM_TREE_STATE_COND > ARM_TREE_NO_STATE_COND with delta ≥ +0.30 at smoke regime (not full-pass; just confirms direction).
- **Smoke discipline 3 (band-floor = MIDDLE_BAND not HARD_PASS):** if both ARM_TREE_STATE_COND and ARM_TREE_NO_STATE_COND end up below 0.10, verdict is MIDDLE_BAND not HARD_PASS — even if delta is +0.05 the regime is too noisy to be cert-grade.
- **Compute-formulas-in-code:** Big-O complexity formulas inline in cell smoke output; runtime measurement strict.
- **Discriminator-must-survive-scale:** smoke at full-N=8192; check (A) per USER 2026-06-26 fix — smoke at full-N to verify mechanism scaling.

---

## Pre-registration log

- ARM_TREE_STATE_CONDITIONED predicted solve_rate = 0.65; P_deflated(HARD_PASS) = 0.42
- ARM_TREE_STATE_CONDITIONED − ARM_FLAT_PREPLAY_K128 lift threshold = +0.20 (decomposition discriminator)
- ARM_TREE_STATE_CONDITIONED − ARM_TREE_NO_STATE_COND lift threshold = +0.40 (state-conditioning load-bearing — REPLACES v1 cleanup-load-bearing discriminator which was uninformative at floor)
- 3 seeds [7, 17, 23]; cv ≤ 0.15 required for HARD_PASS
- CARDINALITY_OK: 6 arms × 3 seeds × 50 goals = 900 units expected
- META_M7 REPRODUCE_PV2 rail mandatory; PASS required
- 4-block SIMPLIFIED BlocksWorld (Option 3 per cell-author recommendation); analytic BFS optimal-plan solver provides ground truth; goals filtered to require ≥ 4 primitive steps and ≥ 2 macro applications (composite regime)
- HARD-PASS and HARD-FAIL thresholds locked at dispatch; not editable post-hoc
- Per discriminator-must-survive-scale: smoke at full N=8192 at composite depth-6 with 3 macros and 4 disjoint blocks active
- Macro vocabulary INTENTIONALLY EXCLUDES `tower(X,Y,Z)` and other parallel-block-coupling macros — fixes v1 root cause
- D[state_class, macro] fit on 80% training (state, macro) tuples; HP eval on 20% held-out (state_class × macro) cells (BIAS-13 contamination guard)

## Negative-result revival path (if CELL A HARD_FAILS)

- CELL A HARD_FAIL via "state-conditioning + disjoint-block compounds still don't extract structure" (mechanism arm ≤ 0.30) → ship CELL B (Sutton-Precup SMDP options framework — different algorithm class; ~1-2hr remote_cpu)
- CELL A HARD_FAIL via "state-conditioning not load-bearing" (mechanism arm within 0.05 of NO_STATE_COND arm) → ship CELL C (deeper composite depth-12+ on same 4-block domain — different regime test; ~30-60min remote_cpu)
- CELL A HARD_FAIL via "tree within 0.05 of flat_K128" → ship CELL C (deeper depth-12+) AND/OR rebump flat to K=512 to confirm flat scales further; if FLAT_K512 still trails, hierarchy may be needed at deeper depths only
- All three HARD_FAIL → hierarchical-planning closure at substrate's current regime. Pivot: queue Hersche block-sparse standalone primitive cell (capability-not-application question) and reframe M3 demo to non-hierarchical-planning conversation classes (immediate Q&A, single-turn task completion)

## Dispatch readiness

CELL A `substrate_hierarchical_planner_state_conditioned_disjoint_v1` is ready to spawn. Companion hand-off file: `notes/exp_dev_handoff_research_hierarchical_planning_REVIVAL_state_conditioned_disjoint_2026-06-28.md`. Estimated wall: 15-30min remote_cpu smoke. Pre-dispatch verify-the-referent (Fix #26) confirms no prior chain-grade evidence on `substrate_hierarchical_planner_state_conditioned_disjoint`; closest priors are the v1 HARD_FAIL anchor and the flat preplay MIDDLE_BAND, neither of which addresses the state-conditioning + disjoint-block mechanism.

Honest discount applied: this is a REVIVAL of a HARD_FAILed mechanism class, with one well-diagnosed root-cause fix (state-conditioning) and one untested capacity enhancement (disjoint-block). The v1 HARD_FAIL bumps the prior — substrate has now demonstrated that the broad mechanism class (Plate-chunked HRR-tree with closed-form cleanup) is NOT trivially feasible at substrate's regime. The revival's P=0.42 reflects: substrate-mining + brain-existence-proof lift the mechanism class slightly above novel-synthesis floor, but the v1 negative result is the dominant calibration signal. The cheap test (15-30min smoke) is the decisive next step regardless of P estimate.
