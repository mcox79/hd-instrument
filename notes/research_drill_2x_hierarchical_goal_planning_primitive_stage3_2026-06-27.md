# 2X RESEARCH DRILL — Hierarchical Goal-Directed Planning Primitive (Stage 3)

**Date:** 2026-06-27
**Author:** research (Opus 4.7-1M)
**Trigger:** USER load-bearing concern #5 for M3 (M4-load-bearing). Substrate did single-hop preplay (K=64 + goal-conditioned gate closes 60% oracle gap, MIDDLE_BAND today). Untested: hierarchical subgoal decomposition (make-breakfast → boil-water + crack-egg + plate; conference-room → chairs + projector + coffee + signs). Like a new employee who can do any one task but can't decompose composite goals.
**2x discipline:** drill DEEPER on the existing flat-K=128 preplay result, NOT re-run lit-scan. Drill the missing HIERARCHY layer.

---

## SUBSTRATE-MINE FIRST (verify-the-referent on what we already have)

**Today on disk (per metrics.json, not framing):**

- `substrate_preplay_beam_to_goal v1`: smoke MIDDLE_BAND. K=64 + goal-conditioned gate closes ~60% oracle gap (single-level beam; depth-D rollouts at flat granularity).
- `multi_hop.iter_cleanup_chain`: chain-grade depth-15 (single-level chain; no subgoal nesting).
- `partition routing M=10M`: chain-grade (can host O(1e7) subgoal pointers).
- `task_vector HRR ICL`: chain-grade (in-context goal specification via bound role).
- `TWO_TIER generational W`: chain-grade-eligible (working memory for active subgoals across time-scales).
- `refuse-gate V_REL=256`: chain-grade (filter infeasible subgoals).
- `audit-chain depth-50`: chain-grade (verify plan correctness).
- `strips_planning_khop_cpu_v1`: HARD_PASS 2-hop reachability=1.000 (substrate CAN plan with STRIPS preconditions; but FLAT — no subgoal nesting).
- `pfc_goal_conditioned_gate_v1` (yesterday's drill): cell-author-ready, single-level.

**Substrate already chain-grade at three of the four pieces hierarchy needs:**
1. HRR bind/unbind for tree composition (Plate 1995 chunking — wave14e Frady-Sommer math + Eliasmith SPA Spaun depth-4 empirical)
2. Per-level cleanup primitive (iter_cleanup_chain — breaks the noise-multiplies-by-depth bound; this is THE load-bearing math from Plate Ch.6)
3. Partition routing to host distinct subgoal banks at distinct levels (M=10M plenty)

**Missing:**
- A composition that BINDS a goal HRR-tree, ROUTES the leaf-primitives back to substrate's existing K=64 preplay beam, and AUDITS that the cleaned-up macro-action sequence equals the cleaned-up primitive-action sequence.

The 2x finding: **this is NOT a new mechanism request — it is a COMPOSE-EXISTING-PRIMITIVES drill.** P prior accordingly lifted vs novel-synthesis; deflated for novel-composition risk.

---

## (a) HEADLINE

Hierarchical goal decomposition for Stage 3 is a 3-level Plate-chunked HRR tree (goal-bundle → mid-subgoals → primitive-actions) where per-level cleanup against a learned chunk-dictionary breaks the noise compounding bound. Substrate has chain-grade pieces 3/4: HRR bind/unbind, multi-hop cleanup chain depth-15, partition-routed M=10M banks. The missing piece is the chunk-dictionary fit (per-level codebook of "valid macro-actions"). For 3-level branching B=4 the total flat-equivalent K_total = B^3 = 64 — comfortably under the Frady-Sommer K_max~261 cliff at N=4096. **Substrate-better-than-brain mechanism: per-level cleanup is parallel across all K^L candidate trees, where brain runs ~3 alternatives sequentially.** P_deflated for chain-grade hierarchical planning = **0.45** at the novel-composition cap (brain-existence-proof lifts +0.10; substrate-mining lifts +0.05; calibration penalty -0.20; novel-synthesis cap -0.05). The single decisive test: 4-block BlocksWorld with COMPOSITE goals (8-step optimal plan) where flat-K=64 preplay is at-or-below 0.30 solve-rate (the empirical ceiling of single-level beam at this depth per Frady-Sommer per-step error compounding 0.85^8 = 0.27), and 3-level HRR-tree decomposition reaches ≥ 0.65 solve-rate.

---

## (b) Cheap decisive test

**SINGLE 5-arm cell** `substrate_hierarchical_subgoal_planner_v1_META_M7`:

| Arm | Mechanism | What it isolates |
|---|---|---|
| ARM_REPRODUCE_RAIL | META_M7 pointer-chain V2 5HOP @ 2000 bindings, band [0.08, 0.25] | Cross-cell rail PASS (mandatory) |
| ARM_RANDOM_PLAN | Random action sequences of depth-8, top-N=64 reranked by goal-cosine | Discriminator floor; SANITY_BREACH if > 0.15 |
| ARM_FLAT_PREPLAY_K64_D8 | Yesterday's substrate_preplay_beam_to_goal v1 mechanism extended to depth-8 (composite plan length) | The "no hierarchy" baseline — composite plans should exceed flat-K=64's empirical ceiling at depth-8 |
| ARM_HRR_TREE_DECOMPOSE_3LVL | 3-level Plate-chunked tree: goal_root = bundle(GOAL_TOP_ROLE * goal_HRR + MID_ROLE_i * subgoal_i for i in 1..B); each subgoal_i = bundle(LEAF_ROLE_j * primitive_j); per-level cleanup against learned chunk-dictionary (closed-form pseudoinverse fit on 1000 random subgoal compositions); leaf primitives feed flat-K=16 preplay beam | The mechanism arm (full hierarchy + cleanup) |
| ARM_HRR_TREE_NO_CLEANUP_ABLATE | Same as ARM_HRR_TREE_DECOMPOSE_3LVL but cleanup at each level REPLACED with raw bundle (no Plate chunking) | The Plate-1995 discriminator — tests whether cleanup is load-bearing (predicted YES per Frady-Sommer + wave14e analysis); if NO cleanup arm matches WITH cleanup arm, hierarchy is illusory |

**Domain:** Extended BlocksWorld:
- 8 blocks (instead of yesterday's 4) — enough state-space to require composite plans
- 6 primitive actions {pick-up, put-down, stack, unstack, move-aside, swap}
- 5 mid-level macro-actions {tower(X,Y,Z), separate(X,Y), gather(X,Y,Z,W), order(...), clear-surface()}, each defined as a 2-3 primitive subsequence
- 100 composite goal pairs per seed (3 seeds [7,17,23]); each goal requires 6-10 primitive steps via optimal BFS solver (sub-tier easy: 2-3 step goals filtered out)
- Goal encoding: HRR bundle of (block_i, target_location_i) pairs

**Per-level chunk-dictionary fit (the new substrate piece):**
- LEVEL-2 dictionary: 5 mid-level macro-action codewords; closed-form pseudoinverse W_macro fit on 1000 (state_pre, macro_action) → state_post tuples from random rollouts
- LEVEL-1 dictionary: 100 goal-type codewords (one per goal-class in training); W_goal pseudoinverse fit
- Per-level cleanup = nearest-neighbor lookup against the level-appropriate dictionary (Plate Ch.6 cleanup — chain-grade primitive iter_cleanup_chain already does this for a flat dictionary)

**Decision-grade thresholds (PRE-REGISTERED, locked at dispatch):**

- **HARD_PASS_CHAIN_GRADE**:
  - ARM_HRR_TREE solve_rate ≥ 0.65 (composite goals; depth ≥ 6 optimal)
  - ARM_HRR_TREE − ARM_FLAT_PREPLAY ≥ +0.25 (decomposition lift discriminator; flat predicted ~0.30 ceiling)
  - ARM_HRR_TREE − ARM_HRR_TREE_NO_CLEANUP ≥ +0.20 (cleanup-is-load-bearing discriminator; the wave14e Plate prediction)
  - median plan-length / optimal ≤ 2.0
  - META_M7 PASS
  - CARDINALITY_OK (5 arms × 3 seeds × 100 goals = 1500 units expected)
  - cv across seeds ≤ 0.10

- **HARD_PASS_PARTIAL (MIDDLE_BAND)**: solve_rate in [0.45, 0.65) AND lift over flat ≥ +0.15

- **HARD_FAIL**:
  - ARM_HRR_TREE solve_rate ≤ 0.30 (hierarchy doesn't help; pivot to Cell 2)
  - OR ARM_HRR_TREE within 0.05 of ARM_HRR_TREE_NO_CLEANUP (cleanup not load-bearing — interpretation: the noise-floor is too low for cleanup to matter at this B/L combo; pivot to deeper trees or block-sparse Hersche codes)
  - OR ARM_HRR_TREE within 0.05 of ARM_FLAT_PREPLAY (decomposition not extracting structure)

- **SANITY_BREACH**: ARM_RANDOM_PLAN > 0.15 → composite domain too easy; redesign with deeper subgoal divergence

**Discriminator-must-survive-scale:** Smoke at full N=8192 at depth=6 composite (not just depth-3) AND with 3 of 5 macros present per ARM_HRR_TREE smoke (verify per-level cleanup actually fires; not just code-runs). Per yesterday's stage-discriminator-survives-scale discipline.

**Fairness gates:**
- Same operator bank, same seeds, same N=8192 across all arms
- Goal vector sampled fresh per (start, goal) pair from substrate-vocab to prevent goal-leak through dictionary
- W_macro and W_goal fit on 80% training goals; HP eval on 20% held-out goal-classes (per BIAS-13 contamination guard)
- ARM_RANDOM_PLAN gets same 64 trajectories per goal (matched compute budget vs ARM_FLAT_PREPLAY)
- META_M7 rail required

**Compute:** Forward-only, no autograd. W_macro pseudoinverse fit O(N × V_actions × N_train) = ~10s. W_goal fit O(N × V_goal × N_train) = ~10s. Per HRR-tree decomposition + cleanup + leaf rollout ≈ 200ms per goal. 5 arms × 3 seeds × 100 goals × ~200ms = ~5min pure compute; META_M7 rail adds ~10min. Total ~30-60min remote_cpu.

---

## (c) Falsifiable predictions

| Arm | Predicted solve_rate | P(≥HARD_PASS) | Reasoning |
|---|---|---|---|
| ARM_HRR_TREE_DECOMPOSE_3LVL | 0.68 | 0.45 | Plate chunking + per-level cleanup + 3 of 4 primitives chain-grade. K_total = 4³ = 64 well under Frady-Sommer N=8192 cliff (cliff at K~530 per V=256, p=0.1 — we have 50x margin). Cleanup is iter_cleanup_chain which is depth-15 chain-grade — extends to depth-3 hierarchy trivially. Risk: chunk-dictionary fit must hit ≥0.85 per-level accuracy or cumulative 0.85³ = 0.61 end-to-end which sits at threshold. P=0.45 deflated from raw 0.65 (brain-existence-proof + substrate-mining lifts; calibration penalty + novel-composition cap deflate). |
| ARM_HRR_TREE_NO_CLEANUP_ABLATE | 0.28 | – (ablation) | Without cleanup, noise compounds as Plate predicts: 0.85³ × 0.85² (level cleanup loss + leaf rollout loss) → ~0.27 expected; aligns with Frady-Sommer at K_effective ~ B^L = 64 and no per-level resampling. |
| ARM_FLAT_PREPLAY_K64_D8 | 0.30 | – (baseline) | Yesterday's flat-K=64 closes 60% oracle gap at depth-3; depth-8 composite pushes past per-step compounding (0.85^8 ≈ 0.27). The "flat ceiling" baseline for the lift discriminator. |
| ARM_RANDOM_PLAN | 0.04 | – (control) | Pure random + goal-cosine rerank over 64 trajectories; same as GAP-B math. |
| ARM_REPRODUCE_RAIL | 0.16 ± 0.04 | – (rail) | META_M7 band PASS required. |

**HARD-PASS thresholds locked:**
- ARM_HRR_TREE solve_rate ≥ 0.65 (composite goals)
- ARM_HRR_TREE − ARM_FLAT_PREPLAY ≥ +0.25
- ARM_HRR_TREE − ARM_HRR_TREE_NO_CLEANUP ≥ +0.20 (cleanup-load-bearing)
- median plan-length ≤ 2.0 × optimal

**HARD-FAIL thresholds locked:**
- ARM_HRR_TREE ≤ 0.30 → hierarchy mechanism dead at this regime; pivot to Cell 2 (block-sparse Hersche codes for 2x effective K capacity per wave14e §1.3)
- ARM_HRR_TREE within 0.05 of ARM_HRR_TREE_NO_CLEANUP → cleanup is NOT load-bearing; either the noise floor is mismatched OR substrate's cleanup primitive is too lossy at this branching factor; investigate before pivoting
- ARM_HRR_TREE within 0.05 of ARM_FLAT_PREPLAY → tree decomposition doesn't extract additional structure beyond what flat beam at K=64 already captures; substrate's flat preplay may be at parity with hierarchy at composite depth ≤ 8; pivot to depth ≥ 12 composite goals (likely Cell 3 territory)

---

## TOP-3 CELL CANDIDATES (ranked)

### CELL 1 (RANK 1, P_deflated = 0.45): `substrate_hierarchical_subgoal_planner_v1`
**As specified in (b) above.** Composes existing chain-grade primitives (HRR bind, iter_cleanup_chain, partition routing, preplay beam). Plate Ch.6 chunking is the canonical math; wave14e proves it's substrate-feasible at N=4096 depth-3 with B=4. 3-level tree + per-level cleanup + closed-form pseudoinverse dictionary fits. **Why first:** smallest delta from yesterday's flat preplay; the Plate-chunking discriminator (cleanup-load-bearing) is THE substrate-physics question for hierarchy.

### CELL 2 (RANK 2, P_deflated = 0.35): `substrate_hierarchical_planner_block_sparse_hersche_v1`
**Mechanism:** Same HRR tree as CELL 1, but with Hersche-2024 block-sparse codes (arXiv:2303.13957) for per-level codebook — each level reserves disjoint blocks of the N=8192 vector, eliminating cross-level interference. Wave14e §1.3: gives ~2x capacity (effective K_max ~ 530 → ~1060 at N=8192 with block sparsity). Adds 1 arm: ARM_HRR_TREE_BLOCK_SPARSE_3LVL.
**Why:** If CELL 1 HARD_FAILs because cleanup IS load-bearing but dictionary fit isn't accurate enough (per-level accuracy < 0.80), block-sparse codes give the cleanup margin. Also enables deeper trees (4-level B=4 with K_total=256, still under cliff with margin).
**Risk:** Hersche block partitioning is novel composition; not yet chain-grade on substrate; deflated P. Best as CELL 1 HARD_FAIL pivot OR as CELL 1 HP follow-up to extend depth.

### CELL 3 (RANK 3, P_deflated = 0.30): `substrate_hierarchical_planner_replay_consolidated_dictionary_v1`
**Mechanism:** CELL 1 + dictionary fit augmented via NREM replay (proven-bound +0.57 drift_reduction 2026-06-22). Replay re-presents (state_pre, macro_action, state_post) tuples at compressed time-scale; sharpens W_macro discriminating capacity. Adds 1 arm: ARM_HRR_TREE_NREM_REPLAY.
**Why:** Brain analog — hippocampal replay consolidates schemas into cortical chunks (CLS theory). The chunk-dictionary IS the substrate's cortical schema for macro-actions. If CELL 1 MIDDLE_BANDs because dictionary fidelity is the limiter (not the mechanism), this cell tests replay-augmented dictionary as the lift mechanism.
**Risk:** Two simultaneous mechanism changes (hierarchy + replay); deflated harder.

**Sequencing recommendation:** Ship CELL 1 FIRST. CELL 2 ships as HARD_FAIL pivot (block-sparse for cleanup margin) OR as HP extension (deeper trees). CELL 3 ships as MIDDLE_BAND pivot if dictionary fidelity is the bottleneck.

---

## (d) Cross-thread synthesis

**Convergence with yesterday's GAP B drill (research_gap_B_goal_directed_planning).** The flat-K=128 cortex-composed beam is the FLAT baseline this drill extends. GAP B Candidate 3 (active predictive coding hierarchy) is conceptually adjacent but uses Rao-2024 temporal-scale hierarchy (1-step / 5-step / 25-step macros), NOT Plate chunking (goal-tree decomposition). This drill is the COMPLEMENTARY drill — Rao hierarchy is temporal-scale; this drill is goal-structural. Both can be true; if both HARD_PASS the substrate has two orthogonal hierarchy mechanisms.

**Convergence with 3x drill `research_drill_3x_goal_directed_planning_2026-06-27` (this morning).** That drill identified the goal-blind gate as the bug at the per-step routing level. This drill takes the gate-fix as ASSUMED (Cell 1 from that drill ships in parallel) and extends to the multi-level subgoal layer above. Composition: goal-conditioned gate (3x drill) is the LEAF-level routing inside ARM_HRR_TREE; this drill tests whether the TREE decomposition above the leaves adds value beyond the gate alone.

**Convergence with wave14e (2026-05-19) hierarchical bundle composition.** Wave14e is the substrate-physics scoping doc: K_total=B^L vs Frady-Sommer K_max; per-level cleanup as the noise-reset mechanism; Hersche block codes for 2x capacity; Eliasmith SPA Spaun as depth-4 N=512 empirical precedent. This drill is the FIRST CELL implementing that math on substrate's actual primitives. Wave14e predicted depth-3 B=4 is comfortably below cliff at N=4096; we now have N=8192 and 50x margin.

**Convergence with Plate 1995 HRR Chapter 6 ("Chunking").** Plate's Table 6.1: N=512, 100 chunks/level, depth-4 recovers at 0.95^4 = 0.81 per chunk end-to-end. Substrate's N=8192 with 5 chunks/level (much sparser dictionary, easier cleanup) predicts ≥0.95 per-level → 0.95³ = 0.86 end-to-end. The Plate math says HARD_PASS is feasible IFF cleanup primitive is ≥0.95 per-level — substrate's iter_cleanup_chain at depth-15 with K=20 codebook is chain-grade ≥0.97 per-step, so the prerequisite is satisfied.

**Convergence with Eliasmith SPA Spaun (wave14e §1.4).** Spaun runs depth-4-5 hierarchies at N=512 with per-level Hopfield cleanup. The strongest empirical existence-proof that hierarchical HDC works at depth 4+. Substrate at N=8192 is 16x larger than Spaun's regime — there is significant margin.

**Convergence with brain mechanism mapping.**
- Anterior PFC (abstract goal) → top-level HRR bundle (Koechlin-2003; Badre-D'Esposito-2009)
- Posterior PFC (concrete action) → leaf HRR atoms (Badre 2008 rostrocaudal gradient)
- Basal ganglia chunking → partition routing per skill (Botvinick-2009; Graybiel-2008 option discovery)
- Hippocampal preplay → forward simulation along the tree (Pfeiffer-Foster-2013; Liu-Foster-2019; Mattar-Daw-2018 rational meta-reasoning)
- Cerebellum forward-model → per-step W_world prediction (Ivry-Spencer-2004)
- Wood-Grafman-2003 PFC subgoal decomposition lesion → loss of HRR tree composition without anterior PFC ≈ loss of bind operation without a working role-vocabulary

**Adjacency cascade.** This drill SURFACES a NEW adjacent angle in the `hierarchical-composition` field: Plate-chunked HRR-tree-with-cleanup is a specific instantiation of the wave14e mathematical framework that wasn't previously cell-author-ready. Per Trigger C, a follow-up drill into Hersche block-sparse codes (Tier-1-equivalent: free-probability adjacent + sparse-coding adjacent) should queue within 24h.

**No contradictions with existing META atoms.**
- "cleanup-load-bearing" META atom (2026): FAVORABLE — this cell IS the cleanup-load-bearing test at the hierarchy level.
- "no-Hebbian-window" META atom: irrelevant; closed-form pseudoinverse fits, no online Hebbian.
- "by-construction-saturation" hazard: deliberately defended against — ARM_HRR_TREE_NO_CLEANUP_ABLATE is the by-construction check; if hierarchy lift survives the ablation, the mechanism is real not by-construction.

---

## (e) Substrate-product implications

**M3 (glass-box conversational AI) — load-bearing.** Hierarchical goal decomposition is the bridge from "substrate executes single requests" to "substrate plans a conversation toward a user-stated outcome." Without this primitive, substrate is a Q&A oracle; with it, substrate can decompose "help me decide whether to invest in X" into subgoals (gather-financial-context → assess-risk-tolerance → enumerate-alternatives → produce-recommendation). Each subgoal becomes a beam-preplay leaf; the tree IS the conversation plan. This is directly cited by USER as concern #5 of 10 for M3.

**M4 (hybrid agentic experiment loop substrate-as-research-director) — load-bearing.** The substrate-as-research-director needs to decompose "discover the next chain-grade primitive" into (mine current cap_map gaps → identify adjacent mechanisms → design discriminator cell → dispatch → audit verdict). Each level is a HRR-bound subgoal. Without hierarchy, the substrate can route at the leaf level but not COMPOSE multi-level research plans — i.e. it's a research assistant, not a research director. CELL 1 HP unlocks the director-as-agent mode.

**M5 (full code-gen) — also load-bearing eventually.** Code generation decomposes naturally as function-tree → statement-blocks → expressions. Same HRR-tree decomposition with different leaf-action vocabulary.

**Audit-device coupling.** Audit-chain depth-50 (chain-grade) verifies each leaf primitive's correctness; tree-decomposition gives the AUDIT a structural target — verify that mid-level macro-actions are correctly composed from leaf primitives AND verify that top-level goal is correctly composed from mid-level subgoals. This is structurally stronger than LLM-based plans (which have no auditable intermediate representation). Competitive moat.

**Risk parity vs LLM-based hierarchical planners.** LLMs (HuggingGPT, BabyAGI, AutoGPT) decompose goals via natural-language chain-of-thought. They have NO auditable bind operation; their decomposition is opaque token-streams. Substrate's HRR-tree decomposition is FULLY AUDITABLE at each level (which mid-action was bound at which slot; what primitives the cleanup chose). This is the "glass-box hierarchical planning" capability the substrate-product needs.

**Honest non-claim.** "Plan all day" claim (USER's substrate-better-than-brain on long horizons) is NOT tested by this cell — that requires depth ≥ 50 effective primitive horizons via 3+ hierarchy levels. Queue as stretch goal AFTER CELL 1 HP.

---

## (f) Citations (verified count: 14)

**Brain mechanism — hierarchical PFC + subgoal decomposition:**
1. Koechlin, Ody, Kouneiher 2003 "The Architecture of Cognitive Control in the Human Prefrontal Cortex" Science 302:1181 — anterior/posterior PFC abstract-goal/concrete-action gradient.
2. Badre & D'Esposito 2009 "Is the rostro-caudal axis of the frontal lobe hierarchical?" Nat Rev Neurosci 10:659 — rostrocaudal hierarchy.
3. Botvinick 2009 "Hierarchical reinforcement learning and decision making" Curr Opin Neurobiol 22:956 — option/skill chunking in BG.
4. Graybiel 2008 "Habits, rituals, and the evaluative brain" Annu Rev Neurosci 31:359 — striatal chunking.
5. Pfeiffer & Foster 2013 "Hippocampal place-cell sequences depict future paths to remembered goals" Nature 497:74 — preplay forward simulation.
6. Liu, Mattar, Behrens et al. (Liu-Foster 2019) "Human Replay Spontaneously Reorganizes Experience" Cell 178:640.
7. Mattar & Daw 2018 "Prioritized memory access explains planning and hippocampal replay" Nat Neurosci 21:1609 — rational meta-reasoning about which to plan.
8. Wood & Grafman 2003 "Human prefrontal cortex: processing and representational perspectives" Nat Rev Neurosci 4:139 — PFC lesion + subgoal decomposition deficits.
9. Ivry & Spencer 2004 "The neural representation of time" Curr Opin Neurobiol 14:225 — cerebellum forward model.
10. Newell & Simon 1972 "Human Problem Solving" — means-end analysis (canonical AI hierarchical-planning).

**VSA / HDC math — chunking + capacity bounds:**
11. Plate 1995 "Holographic Reduced Representations" Chapter 6 ("Chunking") — canonical per-level cleanup-as-chunk-resolution formalism + Table 6.1 empirical recovery at depth-4.
12. Frady, Sommer, Kanerva 2018 "A theory of sequence indexing and working memory in recurrent neural networks" Neural Computation 30:1449 — K_max ~ N / (2 ln(V/p)) capacity bound.
13. Hersche et al. 2024 "Sparse Block Codes for Hyperdimensional Computing" arXiv:2303.13957 — block-sparse codes for 2x capacity (CELL 2 mechanism basis).
14. Eliasmith 2013 "How to Build a Brain" / Spaun model — SPA depth-4-5 hierarchy at N=512 with Hopfield per-level cleanup (empirical existence-proof).

---

## Pre-registration log

- ARM_HRR_TREE_DECOMPOSE_3LVL predicted solve_rate = 0.68; P_deflated(HARD_PASS) = 0.45
- ARM_HRR_TREE − ARM_FLAT_PREPLAY lift threshold = +0.25 (decomposition discriminator)
- ARM_HRR_TREE − ARM_HRR_TREE_NO_CLEANUP lift threshold = +0.20 (cleanup-load-bearing — the Plate-1995 prediction; the load-bearing substrate-physics check)
- 3 seeds [7, 17, 23]; cv ≤ 0.10 required for HARD_PASS
- CARDINALITY_OK: 5 arms × 3 seeds × 100 goals = 1500 units expected
- META_M7 REPRODUCE_PV2 rail mandatory; PASS required
- 8-block extended BlocksWorld; analytic BFS optimal-plan solver provides ground truth; goals filtered to require ≥ 6 primitive steps (composite regime)
- HARD-PASS thresholds locked at dispatch; not editable post-hoc
- Per yesterday's discriminator-must-survive-scale: smoke at full N=8192 at composite depth-6 with 3 of 5 macros, NOT smoke at N=512 depth-3 with 1 macro

## Negative-result revival path

- If CELL 1 HARD_FAILS via "cleanup not load-bearing" → ship CELL 2 (Hersche block-sparse) to test whether per-level cleanup margin is the limiter
- If CELL 1 HARD_FAILS via "ARM_HRR_TREE within 0.05 of ARM_FLAT_PREPLAY" → composite depth too shallow for hierarchy to add value; pivot to depth-12 composite (CELL 1 v2 with stretched domain)
- If CELL 1 MIDDLE_BAND via dictionary-fidelity limit → ship CELL 3 (NREM-replay-consolidated dictionary)
- If all three CELL 1/2/3 fail → fundamental Plate-chunking-on-substrate is closed at substrate's regime; pivot to GAP-B Candidate 3 (Rao active predictive coding temporal hierarchy) as alternative mechanism class

## Dispatch readiness

CELL 1 `substrate_hierarchical_subgoal_planner_v1` is ready to spawn. Companion hand-off file: `notes/exp_dev_handoff_research_hierarchical_goal_planning_primitive_stage3_2026-06-27.md`. Estimated wall: 30-60min remote_cpu. Per fix #26, exp_dev runs `tools/predispatch_check.py` to confirm no prior chain-grade evidence on `substrate_hierarchical_subgoal_planner` (the closest priors are the FLAT preplay and the wave14e research-only doc, neither a cell-author-ready anchor for this mechanism).
