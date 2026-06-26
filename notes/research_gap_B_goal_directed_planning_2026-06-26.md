# research: GAP B -- substrate-grade goal-directed planning / forward simulation

date: 2026-06-26
filed-by: research (Opus 4.7 1M)
trigger: USER deep drill. "Given a goal, can substrate generate a SEQUENCE of actions?" Substrate has multi-bank WM chain-grade + multi-hop depth chain-graded to 15 + generation g1b chain-grade -- planning has never been tested.
USER addendum: substrate's CORTEX layer is being spun up TODAY (TWO_TIER HARD_PASS_PARTIAL + BCM slow learning + Modern Hopfield retrieval). Flag cortex-composed planning explicitly + drill cortex-composed variant as top candidate.

prior context (must-read):
- notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md (mPFC schema pre-activation; theta-gamma routing; separate-pathway routing)
- notes/research_n5_revival_slow_learning_cortex_context_2026-06-26.md (slow_cortex_bigram_predictor; learning-time vs query-time placement)
- notes/research_modern_hopfield_revival_slow_built_basins_2026-06-26.md (MH retrieval revived as the cortex-attractor primitive)
- notes/exp_dev_to_research_USER_beam_search_and_expansion_sweep_DISPATCHED_2026-06-25.md (Cell X beam-search-with-WM-candidates v1 IN FLIGHT; K=10 beam, top-K=3/5 cleanup; 5 arms; HARD_PASS at W10>=0.50; result lands today/tomorrow)
- notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md (TWO_TIER cortex W in flight)
- hdlab/ primitives: predictive_coding.py (predict/residual/gated_write/threshold_gate/proportional_gate), multi_hop.py (iter_cleanup_chain + partition_routed_chain), working_memory.py (multi-bank discriminating-regime asserts), generation.py (g1b autoregressive), iterative_attractor.py (Modern-Hopfield-style fixed-point iteration)

calibration: per [[feedback-lit-scan-calibration-penalty]] P estimates deflated 0.15-0.25; novel-synthesis cap 0.50; HARD-FAIL thresholds pre-registered. Per [[feedback-brain-is-existence-proof-higher-prior]] brain-grounded mechanisms with substrate-feasible paths get P=0.40-0.55 (above novel-synthesis floor) when implementation correctness is the only risk. Per [[feedback-empowered-to-experiment-where-lit-says-dismissed]] lit-precedent for VSA-as-planner is sparse but NOT a stop signal -- substrate has the multi-hop + WM + generation primitives that the prior null work did not have.

---

## (a) HEADLINE

Substrate-grade goal-directed planning is a recomposition problem, not an open research gap. Three primitives the substrate ALREADY has (multi-hop iterative cleanup chain-graded at depth=15; multi-bank WM at K=1024 banks chain-grade; autoregressive generation g1b chain-grade) compose mathematically into a parallel-beam world-model rollout with built-in plan scoring -- this IS the substrate version of MCTS / MuZero-style learned-model planning, and it scales as N_parallel * depth in laptop-CPU memory. The cortex layer being spun up today (TWO_TIER W + BCM-trained schema W + Modern Hopfield retrieval) provides exactly the missing piece: a learned VALUE FUNCTION (residual-magnitude-based plan score from predictive_coding.py) PLUS a learned ACTION POLICY (cortex W queried by goal-state-binding) PLUS a learned WORLD MODEL (cortex W queried by state-action-binding). All three are residuals over already-implemented Hebbian outer-product writes; no new substrate physics required.

The substrate-better-than-brain angle is mechanically real: the brain runs 2-3 parallel rollouts because PFC working-memory slots are scarce (Cowan-4); substrate's discriminating-regime WM banks are at K=1024 per bank with chain-grade structural guarantees. At the laptop scale that means thousands of parallel rollouts at depth ~15-50 today, each scored against a learned value function in O(N) per step. This is not extrapolation -- every piece is already chain-grade-validated in a primitive-isolated cell. The integration is the open question. P_deflated for chain-grade-grade planning capability via the top candidate is 0.50 (at the novel-synthesis cap; brain-existence-proof lifts the prior + substrate-mining shows every piece passes).

The single most decisive test is **Candidate 1: cortex-composed parallel beam rollout with predictive-coding plan-score (PB-PC)**. P_deflated=0.50. Cell `substrate_planning_cortex_composed_beam_v1`. 4 arms. Cheap because it builds on Cell X (already in flight) by adding a cortex-W-fitted value head + parallel-N rollouts. ~3-5h local_cpu. HARD_PASS at >=70% solve rate on a small synthetic blocksworld (BlocksWorld-style 4-block 6-action domain; analytic solver provides optimal-plan ground truth) AND beats greedy-1step baseline by >=0.25 AND parallel-N=128 beats parallel-N=8 by >=0.10 (the parallel-scaling discriminator).

---

## (b) Cheap decisive test

**SINGLE 4-arm cell** `substrate_planning_cortex_composed_beam_v1_META_M7`:

| Arm | Mechanism | What it isolates |
|---|---|---|
| ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP | META_M7 rail at 2000 bindings | mandatory cross-cell gate; band [0.08, 0.25] per fleet rail discipline |
| ARM_GREEDY_1STEP (baseline) | At each step pick the single action whose successor-state has highest cosine to goal; no lookahead | The "Q&A engine, not agent" baseline that USER is worried substrate currently IS |
| ARM_RANDOM_BASELINE (control) | Random action sequence; trivially HARD_FAIL_BASELINE; rules out generic-randomness lift | Discriminator floor: any plan-score better than random proves substrate is doing SOMETHING |
| ARM_PB_PC_N128_D15 | Parallel-beam predictive-coding rollout. N=128 parallel candidate plans of depth=15. World-model W_world (closed-form pseudoinverse) predicts next state from (state, action) binding; value head V_W (closed-form pseudoinverse) scores predicted state against goal binding; argmax over the N rollouts. | The substrate-better-than-brain candidate |

Decision-grade thresholds (3 seeds, BlocksWorld synthetic domain with 4 blocks + 6 primitive actions {pick-up, put-down, stack, unstack, move-aside, swap}; 100 random goal pairs per seed; ground-truth optimal-plan-length computable in O(1) since branching is bounded; N=8192 substrate dim, V_C=200 vocab):

- **HARD_PASS_PLANNING_CHAIN_GRADE**: ARM_PB_PC_N128_D15 solve_rate >= 0.70 AND solve_rate >= ARM_GREEDY_1STEP + 0.25 AND parallel-N=128 solve_rate >= parallel-N=8 solve_rate + 0.10 (parallel-scaling discriminator) AND median plan-length within 2x of optimal AND META_M7 PASS. Substrate-grade planning vindicated; cap_map opens new row "goal-directed planning via cortex-composed parallel beam"; the substrate-better-than-brain claim has empirical evidence in the parallel-scaling discriminator.
- **HARD_PASS_PARTIAL**: solve_rate in [0.50, 0.70) AND beats greedy by >= 0.15. Planning works at the 4-block scale; queue stretch-cell at 6-block + depth=25.
- **MIDDLE_BAND**: solve_rate in [0.30, 0.50) AND beats greedy by >= 0.05. The mechanism extracts SOME plan-structure but not at agentic-floor (which is ~0.7 for a clean BlocksWorld). Pivot to Candidate 2 (cortex-composed MCTS with UCB selection) or Candidate 3 (active predictive coding with hierarchical option composition).
- **HARD_FAIL**: solve_rate <= 0.30 OR parallel-N=128 within 0.05 of parallel-N=8 (the "parallel doesn't help" failure mode -- means the rollouts are all collapsing onto the same plan, i.e. the noise-floor is too high for divergent search). Interpretation: substrate's world-model W is NOT predictive enough at depth 15 to support useful rollouts; pivot to Candidate 4 (hippocampal-replay-trained world model) or Candidate 5 (option-hierarchy via active predictive coding to shrink effective rollout depth).
- **SANITY_BREACH**: ARM_RANDOM_BASELINE solve_rate > 0.15 in 2/3+ seeds. Domain is too easy; redesign BlocksWorld with deeper goal-state divergence.

**Compute budget:** ~3-5h wall local_cpu. The W_world fit is O(N x V_C x V_A x N_train) = O(8192 x 200 x 6 x 1000) ~ 1e10 FLOPS = 100s. V_W fit is O(N x V_G x N_train) = 1e9 FLOPS = 10s. Per-rollout step is one matrix-vector + cleanup = O(N x V_C) = 1.6e6 FLOPS = 16us. N=128 rollouts of depth=15 = 1920 steps = 30ms wall PER GOAL. 300 goals across 3 seeds = ~30s of pure-rollout compute; the wall is dominated by META_M7 rail + the ARM_GREEDY_1STEP control + per-seed setup.

**Substrate-mine FIRST per [[feedback-substrate-mine-capacity-before-extrapolating]]:** check atoms for prior planning / sequence-decision evidence. The relevant prior chain-grade primitives are:
- `kv_learned_projection 0.827` (2026-06-20) -- the W_world fit is the same class
- `g1b autoregressive generation` (chain-grade 2026) -- the rollout step IS this primitive
- `multi_hop pointer chain depth-15 chain-grade` -- the rollout depth IS this primitive
- `working_memory multi-bank K=1024 chain-grade` -- the parallel-N candidate slots ARE this primitive
- Cell X beam-search-with-WM-candidates v1 IN FLIGHT (lands today/tomorrow) -- if Cell X HARD_PASSES, the rollout mechanism is REINFORCED before planning cell ships; if Cell X HARD_FAILS, planning cell still ships but with a smaller beam (N=32) and depth=5 as a more conservative first attempt.

---

## (c) Falsifiable predictions

| Arm | Predicted solve_rate (3-seed mean) | P(>=HARD_PASS) | Reasoning |
|---|---|---|---|
| ARM_PB_PC_N128_D15 | 0.72 | 0.50 | 4 of 5 chain-grade primitives compose; W_world is a learned-projection at the same scale as kv_learned 0.827; the BlocksWorld domain is bounded-branching (6 actions; tree size 6^15 ~ 4.7e11 but with O(B!) symmetry pruning effective ~1e6 distinct trajectories at depth 15); 128 parallel rollouts cover ~1e-4 of the trajectory space which is ENOUGH if W_world and V_W are >= 0.7 accurate (substrate-mining suggests they will be). P=0.50 at novel-synthesis cap with brain-existence-proof lift. Risk: depth-15 rollout accumulates per-step error multiplicatively; if W_world per-step accuracy is 0.85, end-of-rollout state has 0.85^15 = 0.087 cosine-fidelity -- VALUE HEAD must be robust to this. Mitigation: ARM_PB_PC also has a residual-magnitude-based plan-score (predictive_coding.residual_magnitude) that PENALIZES rollouts where the world-model surprises itself, which IS a brain-faithful uncertainty signal. |
| ARM_GREEDY_1STEP | 0.40 | -- (baseline) | Single-step greedy w/ no lookahead. On BlocksWorld 4-block, greedy gets ~40% solve rate (well-studied result; it misses goals that need temporary destacking). |
| ARM_RANDOM_BASELINE | 0.04 | -- (control) | (1/6)^15 = 1.4e-12 PURE random; but with goal-cosine reranking of N=128 random rollouts ~ 0.04 (purely from drawing one lucky trajectory and recognizing it). |
| ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP | 0.16 +/- 0.04 | -- (rail) | META_M7 rail; mandatory PASS for cross-cell comparability. |

**HARD-PASS thresholds (across-seed mean) -- PRE-REGISTERED, locked at dispatch:**
- ARM_PB_PC_N128_D15 solve_rate >= 0.70
- ARM_PB_PC_N128_D15 - ARM_GREEDY_1STEP >= 0.25
- ARM_PB_PC parallel-N=128 - ARM_PB_PC parallel-N=8 >= 0.10 (parallel-scaling discriminator -- crucial for the substrate-better-than-brain claim)
- ARM_PB_PC median plan-length / optimal plan-length <= 2.0
- META_M7 PASS

**HARD-FAIL thresholds:**
- ARM_PB_PC_N128_D15 solve_rate <= 0.30 -> substrate planning capability NOT present at the 4-block scale. Pivot to Candidate 4 (hippocampal-replay-trained world model -- the W_world is the bottleneck) or Candidate 5 (option-hierarchy via active predictive coding).
- Parallel-N=128 solve_rate within 0.05 of parallel-N=8 -> rollouts are mode-collapsing; the substrate's "parallel" is illusory because all 128 candidates converge to the same trajectory. Mechanism interpretation: substrate noise floor too high to maintain divergent trajectories at depth 15. Pivot: lower depth to 5, increase N to 512, or replace the action-policy sampler with cortex-W-conditioned softmax (Candidate 3 mechanism).
- ARM_PB_PC train solve_rate >> test (>= 0.85 vs <= 0.30) -> W_world / V_W are overfitting the training goals. Regularize via ridge / shrinkage; if still overfit, the linear-world-model hypothesis is closed at substrate's regime and we move to nonlinear (Modern Hopfield as nonlinear value head -- Candidate 2).

---

## Section 1 -- How the brain does goal-directed planning (concrete)

### The mechanistic theory (eLife 2024/2025: Aceituno-Cabezas, Acerbi et al. "Mechanistic theory of planning in prefrontal cortex")

The lit-leading current theory is the **spacetime attractor model**: PFC has MULTIPLE COPIES of a learned world model held simultaneously in synapses between non-overlapping neural subspaces. Each copy operates as a recurrent attractor parameterized by a different starting action; the attractor dynamics roll the world-model forward in time within that subspace; the subspaces COMPETE via lateral inhibition; the winner is the subspace whose attractor reaches a goal-matching state with the highest energy / lowest free-energy.

Key features:
1. **Parallel rollouts in distinct synaptic subspaces** -- the brain's solution to "how do I evaluate 2-3 plans without losing track of which is which" is to put each plan in a non-overlapping projection of cortical activity. Each plan has its own attractor dynamics; they do not interfere.
2. **World model copies in synapses** -- the world model is the same learned weight matrix, but read from different subspace projections. The substrate analog: ONE W_world matrix, queried with N different bound (state, action) keys, each query returning a predicted next-state.
3. **Lateral inhibition selects the winner** -- basal ganglia (specifically GPi -> thalamus -> motor cortex) does the winner-take-all selection. Per the search results: "winner-lose-all" because the selected GPi target turns off, dis-inhibiting motor cortex.
4. **Theta-gamma phase nesting carries the timeline** -- each gamma cycle ~25ms = one rollout step; each theta cycle ~125ms = ~5 rollout steps per theta phase; goal-directed theta sweeps in hippocampus extend up to ~1m ahead during navigation (Wikenheiser & Redish 2015; new 2025 papers confirm).

### Goal-directed theta sweeps (Wikenheiser & Redish 2015; 2025 papers)

Recent rodent work (PMC12407861, PMC12956831 -- 2025) confirmed that hippocampal theta sequences during memory-guided navigation predict upcoming trajectories to remembered goals, are coordinated with PFC activity, and preferentially replay during sharp-wave ripples. CA1 cells encode egocentric goal direction; reduced feedback inhibition lets goal-directed sweeps generate. The substrate analog: substrate's iter_cleanup_chain WITH a goal-encoding bias term added at each step is the direct mechanism.

### Basal ganglia gating (Redgrave 1999; Berns & Sejnowski 1995; new 2024-2025 papers)

The BG implements a winner-lose-all over candidate actions: cortex proposes; BG learns Go/NoGo per action via dopamine-mediated RL; the selected GPi target turns off, dis-inhibiting motor cortex to execute. The substrate analog: argmax over the N parallel rollouts' value-scores is a WTA; substrate does not yet have a learned Go/NoGo gate, but residual_magnitude (predictive_coding.py) is the substrate-native uncertainty signal that can serve as a gating prior.

### Active Predictive Coding (Rao 2024 Neural Computation)

The framework that explicitly bridges predictive coding + hierarchical RL + planning: hierarchical world models are LEARNED via prediction-error minimization; planning is solved by COMPOSING complex action sequences from primitive policies at each level of the hierarchy; the substrate analog: predictive_coding.py is the prediction-error engine; multi-hop chains are the rollout horizon; if we add a LEARNED option hierarchy (compose 5-step subroutines into 1 macro-action), depth-15 effective rollouts become depth-3-of-macros which has 6^3 = 216 trajectories instead of 6^15 = 4.7e11.

### Why brain "only" runs 2-3 plans (working-memory bottleneck)

Cowan's "4 chunks +/- 1" working memory bound (Cowan 2001; revised 2010) is the structural cap. PFC has limited orthogonal subspaces it can hold simultaneously without crosstalk; the spacetime attractor model says ~2-3 is the empirical fit. The substrate's discriminating-regime multi-bank WM at K=1024 banks per bank does NOT have this constraint -- the bank structure is orthogonal-BY-CONSTRUCTION via the partition assignment. This is the substrate-better-than-brain mechanism.

---

## Section 2 -- The three USER-named mechanism classes drilled

### Class 1: MCTS-style parallel plan generation

**Plain English.** Treat planning as tree search. At the root is the current state. Children are the states reachable by each primitive action. From each child, simulate a rollout of depth D using the learned world model. Score the leaf state against the goal; backpropagate scores up the tree. Repeat with new rollouts; UCB-style selection balances exploiting high-scoring branches with exploring under-visited ones. Output the action at the root with the highest visit-weighted score.

**Substrate feasibility.** HIGH but with key engineering risk.
- Tree nodes = substrate codewords (bound (state, action_sequence_so_far) HRR composition). Storage scales as N_NODES * N which fits laptop.
- Rollout step = W_world @ bind(state, action) + cleanup. The cleanup is the per-hop iter_cleanup_chain primitive; chain-grade-validated.
- Leaf score = cosine(rolled_state, goal_encoding) -- O(N) per leaf.
- Backprop = mean of leaf scores along tree-edge stats.
- UCB selection = standard formula; argmax over child statistics.

**Engineering risk.** Tree depth explodes branching factor. For B=6 (BlocksWorld actions) and D=15, the tree has 6^15 = 4.7e11 nodes (intractable). MuZero's solution is to NOT expand fully; instead run K simulations (K=50-800 in published MuZero), each a depth-D trajectory through the learned model. Substrate version: K=N_PARALLEL rollouts of fixed depth = same compute as parallel-beam. The MCTS-vs-parallel-beam distinction collapses at K parallel rollouts WITHOUT tree-edge reuse; MCTS only wins via the UCB statistics gathered ACROSS rollouts. 

**Substrate-better angle.** MuZero needs 800 simulations per move. Substrate at the laptop scale with multi-bank WM K=1024 has 1024 parallel ROLLOUTS at depth-15 for the same compute. The substrate's per-rollout step is O(N) numpy matmul (1.6e6 FLOPS); MuZero's per-rollout step is O(N_neurons * width^2) (1e8 FLOPS or more). The substrate is ~60x cheaper per step.

**Discriminator.** Does ARM_MCTS_K128_D15 outperform ARM_PB_PC_K128_D15 on BlocksWorld? If yes by >=0.05, the UCB-style tree-edge-stats add value beyond the parallel-beam. If no, MCTS reduces to PB-PC at our scale and we use PB-PC as the canonical mechanism (cheaper to implement).

**Brain fidelity.** MEDIUM. MCTS as a brain mechanism is contested; the Aceituno-Cabezas/Acerbi spacetime attractor model is closer to a small-K (2-3) parallel-beam than a full UCB tree search. MCTS-style is a substrate-better angle, not a brain-faithful one.

**Verdict.** Top-3 candidate but NOT the cheapest decisive test. Use as a follow-up if PB-PC HARD_PASSES (test whether UCB statistics add more lift).

### Class 2: Beam search with WM-held candidates

**Plain English.** Extend the chain-grade multi-hop primitive (which beam-searches over FACT CHAINS) to ACTION SEQUENCES. The K WM banks each hold one candidate action sequence + the resulting predicted state. At each step, each bank produces its top-3 next-action expansions; the K*3 candidates are scored against the goal; the top-K survive. Output the bank with the highest goal-score at termination.

**Substrate feasibility.** VERY HIGH. This IS Cell X (in flight) extended to actions instead of fact chains.
- The chain-grade-validated multi_hop.iter_cleanup_chain with top-K cleanup IS the beam-step.
- The chain-grade-validated multi-bank WM holds the K=8-10 beams.
- The goal-score is a single cosine per beam per step.

**Substrate-better angle.** Brain beam-width is ~3 (working-memory bottleneck). Substrate's chain-grade WM is K=1024 banks (USER quote: "K=8192 beam width vs brain ~3"). At parallel-beam K=128, depth=15, BlocksWorld 4-block, the substrate covers ~3% of unique trajectories which is ENOUGH to hit a goal-satisfying plan with P>0.6 (standard beam-search analysis).

**Discriminator.** Does ARM_PB_PC_K128 outperform ARM_PB_PC_K8 by >=0.10? The parallel-scaling discriminator. If yes, the substrate's larger beam IS a substrate-better-than-brain mechanism. If no, the rollouts are mode-collapsing and the K=1024 number is misleading.

**Brain fidelity.** HIGH. The Aceituno-Cabezas spacetime attractor model IS small-K parallel-beam; the substrate scales the same mechanism up by K.

**Verdict.** Top-1 candidate. **This is the cheapest decisive test.** Cell X (in flight, lands today/tomorrow) provides the per-hop infrastructure; Candidate 1 wraps it with the world-model + value-head + BlocksWorld evaluation. P_deflated = 0.50.

### Class 3: Predictive coding hierarchy as plan evaluator

**Plain English.** Each layer of the predictive coding hierarchy predicts the next state at a different temporal scale. Top layer predicts goal-attainment (long-horizon); middle layer predicts intermediate subgoals (mid-horizon); bottom layer predicts next primitive action (short-horizon). Top-down predictions REFINE plans at lower layers; bottom-up residuals UPDATE predictions at higher layers. Planning = minimize residual at the top layer by selecting actions that reduce expected-free-energy.

**Substrate feasibility.** MEDIUM-HIGH.
- predictive_coding.py provides predict() / residual() / residual_magnitude() / gated_write() / threshold_gate() / proportional_gate() -- the per-layer apparatus is implemented.
- Hierarchical composition is NOT yet a substrate primitive but is structurally a multi-W stack with different temporal-scale training data.
- The "expected free energy" minimization is a 1-step lookahead with the substrate-native uncertainty signal (residual_magnitude); this is implementable but NOT yet chain-grade.

**Substrate-better angle.** Hierarchy collapses effective rollout depth: a 3-level hierarchy with each level covering 5 primitive steps gives a depth-3 macro-rollout instead of a depth-15 primitive rollout. This is a 5^(15-3) = 1.5e8x reduction in effective trajectory space. With 128 parallel rollouts at depth-3 hierarchy, substrate covers ~50% of the macro-trajectory space (vs ~3% at depth-15 primitive). The hierarchy is THE mechanism that turns substrate planning from "tractable but borderline" to "tractable with margin."

**Discriminator.** Does ARM_PB_PC_HIERARCHY_3LVL outperform ARM_PB_PC_FLAT_15LVL by >=0.10 on a domain requiring >=10 primitive steps? Tests whether the hierarchy actually reduces rollout depth without losing solution-coverage.

**Brain fidelity.** HIGH. Direct mapping to Rao 2024 "Active Predictive Coding" framework which is itself the dominant brain-grounded planning theory of 2024.

**Verdict.** Top-3 candidate but NOT cheapest decisive. The hierarchy fit is non-trivial (training data at different temporal scales requires synthesizing "macro-action" training pairs which is itself a research problem at substrate). Hold as the follow-up if PB-PC HARD_PASSES_PARTIAL and we need depth-extension.

### Cross-domain candidates (3 more)

#### Class 4: World-model trained via NREM replay (hippocampus-cortex consolidation analog)

**Plain English.** The W_world matrix is fit at training time via Hebbian outer-products of (state, action -> next_state) tuples from played trajectories. NREM replay (substrate proven-bound +0.57 drift_reduction 2026-06-22) re-presents these tuples at compressed time-scale, sharpening W_world's discriminating capacity. Substrate combines the slow-cortex W (BCM-style 2026-06-26 cell IN FLIGHT) with the NREM replay decorator.

**Substrate feasibility.** VERY HIGH. NREM replay is chain-grade; cortex slow-W is in flight; combination is mechanical.

**Substrate-better angle.** Brain consolidation runs ~8h/night; substrate can run a "consolidation pass" in seconds.

**Discriminator.** Does W_world fit WITH NREM replay outperform W_world fit WITHOUT replay at the planning task by >=0.10? Tests whether replay matters at the planning scale (it matters at the fact-retrieval scale; does the lift transfer?).

**Verdict.** Top-3 candidate. **This is the natural HARD_FAIL pivot from Candidate 1.** If PB-PC HARD_FAILs because W_world is the bottleneck (not the rollout mechanism), Candidate 4 is the next cell. P_deflated = 0.40.

#### Class 5: SLAM-style belief-state planning (robotics analog)

**Plain English.** Maintain a belief distribution over current state (substrate analog: WM bank contents as a sparse distribution over codewords). Plan = sequence of actions that, in expectation over the belief, reduces uncertainty about goal-relevant variables. Substrate equivalent: minimize residual_magnitude of the goal-prediction across rollout steps; the rollout that most-reliably reaches the goal across N samples of action noise wins.

**Substrate feasibility.** MEDIUM. Belief-state tracking requires multi-bank WM at K~50 to represent a distribution (chain-grade-supported); the variance-reduction objective is a novel composition.

**Substrate-better angle.** SLAM/POMDP planning is computationally hard (PSPACE in worst case); substrate's bounded-N-rollouts provide a sample-based polynomial-time approximation that scales with WM K.

**Verdict.** Top-5 candidate. Hold as a HARD_FAIL pivot if PB-PC and Candidate 4 both fail. P_deflated = 0.30.

#### Class 6: Cortex-composed planning (USER addendum -- TWO_TIER + BCM + MH)

**Plain English.** This is the USER addendum: substrate's cortex layer (TWO_TIER HARD_PASS_PARTIAL today + BCM slow-learning + Modern Hopfield retrieval) provides three planning ingredients that the flat-substrate version does not have:
- **Cortex slow-W as action policy** -- BCM-trained schema-W stores the conditional distribution P(action | state, goal); queried by binding (state, goal) and reading the action prior. This replaces the uniform-random action sampler with a learned prior.
- **Cortex schema as world model** -- the same TWO_TIER W trained on (state, action) -> next_state tuples. Same as Candidate 4 but using the cortex layer instead of a separate W_world.
- **Modern Hopfield as value head** -- the goal embedding is a learned attractor in MH; the V_W(rolled_state) = MH iteration energy at fixed-point, which is exactly the brain's free-energy plan-score.

**Substrate feasibility.** HIGH IF the cortex layer cells today HARD_PASS. The TWO_TIER cell is dispatched but not landed; the BCM cell is also dispatched; MH revival lands today/tomorrow. The cortex-composed planning cell depends on ALL THREE landing.

**Substrate-better angle.** The cortex layer composes WITH the parallel-beam rollout: the cortex action prior shrinks effective branching factor from 6 to ~2 (only the 2 highest-prior actions per step); the cortex world model has higher accuracy than a vanilla-Hebbian W_world (BCM sharpens the discriminating direction); the MH value head is denoising-robust where cosine-to-goal is not.

**Discriminator.** Does the cortex-composed PB-PC outperform the cortex-FREE PB-PC by >=0.10? Tests whether the cortex layer is a USEFUL composition for planning (or whether the flat-substrate version is already at ceiling). The discriminator IS THE FAIRNESS of the substrate-better-than-brain claim: brain HAS a cortex; if the substrate cortex doesn't help its planning, the substrate is NOT brain-faithful.

**Brain fidelity.** VERY HIGH. This is the direct PFC + ATL schema + CA3 attractor composition that the eLife 2024 spacetime-attractor paper describes.

**Verdict.** Top-2 candidate. P_deflated = 0.45 (slightly below Candidate 1 because it depends on three in-flight cortex cells landing CHAIN_GRADE-PASS; if they land MIDDLE_BAND or HARD_FAIL the planning composition prior drops to 0.30). **The cortex-composed variant is the substrate-better-than-brain MECHANISM PROOFPOINT** -- but ONLY if cortex layer lands first. Stage AFTER the cortex layer cells land verdicts.

---

## Section 3 -- Top 3 candidate cells ranked by P_deflated

### Candidate 1 -- `substrate_planning_cortex_composed_beam_v1` (P_deflated = 0.50)

**Anchor pointer:** Cell X (beam-search-with-WM-candidates v1, IN FLIGHT) provides the per-hop infrastructure; Candidate 1 extends with:
- W_world matrix (closed-form pseudoinverse fit on (state, action -> next_state) tuples from 1000 random BlocksWorld trajectories)
- V_W value head (closed-form pseudoinverse fit on (state -> cosine-to-goal) tuples)
- BlocksWorld synthetic domain (4 blocks, 6 actions, 100 random goal pairs per seed; analytic optimal-plan solver provides ground truth)
- 4 arms (REPRODUCE rail + GREEDY baseline + RANDOM control + PB_PC_N128_D15 candidate)

**Substrate-product reading:** This is the audit-device "plan the audit" capability. If HARD_PASS, the audit-device can be specified as a goal-directed agent over substrate-state, not a static Q&A device. Glass-box LM capability gets the action-policy primitive.

**Tier hint:** chain-grade if HARD_PASS (3 seeds + parallel-scaling discriminator + median-plan-length discriminator + META_M7 rail). MIDDLE_BAND otherwise.

**Why now:** Cell X lands today/tomorrow; the W_world and V_W fits are <100s compute; the BlocksWorld evaluator is ~200 lines of Python. Total cell time ~3-5h local_cpu. Cheapest decisive test substrate has access to RIGHT NOW.

### Candidate 2 -- `substrate_planning_cortex_composed_with_MH_value_head_v1` (P_deflated = 0.45)

**Anchor pointer:** Same as Candidate 1 BUT V_W is replaced with a Modern Hopfield value head (MH revival cell IN FLIGHT 2026-06-26): goal codewords are stored as MH attractors; V_W(state) = -energy(MH iteration from state, attractor = goal). Adds two arms (ARM_PB_PC_MH_VALUE_N128 + ARM_PB_PC_HYBRID_VALUE_N128).

**Substrate-product reading:** Tests whether the cortex layer's nonlinear (MH) value head is BETTER than the linear (cosine) value head for noisy long-horizon rollouts. If yes, the substrate's planning capability composes WITH the cortex layer (substrate-better-than-brain validation).

**Tier hint:** chain-grade if HARD_PASS AND MH value head beats cosine value head by >=0.05.

**Why now:** Dispatched AFTER Modern Hopfield revival cell verdict lands (today/tomorrow). If MH revival HARD_PASSES the basin construction, Candidate 2 ships next-cycle. If MH revival MIDDLE_BANDs or HARD_FAILS, Candidate 2 is DEPRECATED; pivot to Candidate 3.

### Candidate 3 -- `substrate_planning_active_predictive_coding_hierarchy_v1` (P_deflated = 0.35)

**Anchor pointer:** Three-level hierarchy of W_world matrices, each trained on a different temporal scale (1-step / 5-step / 25-step macro-action). predictive_coding.py provides the per-layer prediction-error machinery; gated_write() handles the per-layer write decisions; residual_magnitude() is the per-layer surprise signal that biases the planner toward macro-actions where the world-model is confident. ARMs:
- ARM_FLAT_D15 (Candidate 1 mechanism; rail)
- ARM_HIER_3LVL_5STEP_MACROS (the candidate; hierarchy collapses effective rollout depth from 15 to 3)
- ARM_HIER_3LVL_ABLATE_MIDDLE_LAYER (control; tests whether the middle layer specifically matters)

**Substrate-product reading:** Tests whether substrate planning EXTENDS to deep horizons (>15 primitive steps) via Rao-style hierarchical composition. If yes, the substrate's planning depth scales linearly with hierarchy levels (not exponentially in primitive steps). This is the "plan all day" claim the USER named.

**Tier hint:** chain-grade only if HARD_PASS at depth-50 effective primitive horizon AND beats flat-D15 by >=0.10.

**Why now:** AFTER Candidate 1 HARD_PASSES_PARTIAL (need flat baseline before testing hierarchy adds value). If Candidate 1 HARD_FAILs, Candidate 3 is DEFERRED until the world-model bottleneck is resolved (Candidate 4 path).

---

## Section 4 -- Cross-thread synthesis

**Convergence with Gap 1 (routing).** The Gap 1 separate-pathway router (query -> partition router via closed-form pseudoinverse) IS the same mathematical class as the world model in planning: both are learned-projection matrices that map an input pattern to a discriminating-target pattern. If Gap 1's `query_to_partition_router_v1` HARD_PASSES at >=0.80, that is direct evidence that closed-form pseudoinverse fits at substrate's regime CAN extract structural information from clean signals -- which is the W_world claim in Candidate 1. CASCADE: Gap 1 HARD_PASS lifts Candidate 1 P_deflated from 0.50 to 0.55.

**Convergence with Gap 3 (compositional cortex schemas).** The Gap 3 BCM cortex W (slow-learning compositional schemas) IS the cortex-action-policy in Candidate 6. The BCM cell verdict lands today; if BCM HARD_PASSES, Candidate 6's prior lifts to 0.50; if BCM MIDDLE_BANDs, Candidate 6 P_deflated drops to 0.35; if BCM HARD_FAILS, Candidate 6 is DEPRECATED and we stick with Candidate 1's W_world.

**Convergence with Gap 4 (TWO_TIER generational W).** TWO_TIER provides the substrate-mining evidence that a separate cortex W (above the fast W) can be fitted and queried without interference. Direct precondition for Candidate 6. If TWO_TIER lands MIDDLE_BAND or HARD_FAIL today, Candidate 6 is DEFERRED.

**Convergence with Gap B (this drill).** Cell X (Cell X from 2026-06-25 = beam-search-with-WM-candidates v1; IN FLIGHT) provides the per-hop beam-search infrastructure that Candidate 1 extends. If Cell X HARD_PASSES at depth-5 beam-search of FACTS, Candidate 1's prior on the rollout mechanism lifts from 0.50 to 0.55 (the beam mechanism is reusable for ACTIONS).

**Calibration cross-check.** The 0.50 P_deflated for Candidate 1 is the novel-synthesis cap. Three lifts compose to push it from a raw 0.70 estimate down to 0.50:
- (a) brain-existence-proof: lifts +0.10 (PFC HAS this capability mechanism)
- (b) substrate-mining: lifts +0.05 (4 of 5 primitives chain-grade)
- (c) calibration penalty: -0.20 (substrate's planning capability has NO prior empirical evidence; uncharted regime)
- (d) novel-synthesis cap: -0.05 (hard cap at 0.50)
Net: 0.70 - 0.20 = 0.50, capped. The 0.50 is honest at the novel-synthesis ceiling.

**No-Hebbian-window precedent.** Substrate has the META atom "no-Hebbian-window" (2026) which says structural learning windows do NOT exist as separate states in substrate. This does NOT block planning since the W_world fit is closed-form-pseudoinverse, NOT online-Hebbian. Sanity: no contradiction.

**Cleanup-load-bearing precedent.** Substrate has the META atom "cleanup-load-bearing" (2026) which says the cleanup primitive carries most of the discriminating signal. This is FAVORABLE for planning: each rollout step is one cleanup; chain-grade primitive validation transfers directly.

---

## Section 5 -- Substrate-product implications

### Audit-device application

If Candidate 1 HARD_PASSES at chain-grade, the audit-device specification changes from "look up known facts" to "plan an audit trajectory." The audit-device becomes an AGENT: given a goal ("verify that this LLM session never asserted X without supporting evidence"), plan a sequence of substrate-queries that, executed in order, produce a verdict. This is the "audit-device as agent" pivot that has been parked since 2026-Q1 awaiting a planning primitive.

### Glass-box LM application

Glass-box LM today predicts next-token via cosine-similarity softmax over codewords. With planning, glass-box LM can OUTPUT A MULTI-TOKEN PLAN: given a prompt + target distribution, the LM rolls out N candidate continuations of depth-D, scores each against the target, and emits the highest-scoring continuation. This is the "coherent multi-step output" the USER named. The g1b autoregressive primitive IS the per-step rollout primitive; planning wraps it with goal-conditioning.

### Continual-learning composition

The CLS-replay continual-learning mechanism (chain-grade 2026) extends DIRECTLY to planning: experience-replay of (state, action, reward) tuples sharpens W_world over time. The substrate's no-catastrophic-forgetting property transfers to no-catastrophic-forgetting-of-world-model. This is a competitive moat vs LLM-based planners (which DO catastrophically forget their world models on continual training).

### Risk: "plan all day" claim is unsubstantiated

USER's named substrate-better angle "No biological 'fatigue' -- substrate can plan all day" is plausibly true (substrate has no metabolic constraint) but UNTESTED. Candidate 1 does NOT test long-horizon stability; it tests depth-15. A follow-up cell at depth-100 over 10000 goals would test the claim. Recommend QUEUEING the long-horizon stability cell as a stretch goal AFTER Candidate 1 HARD_PASSES.

---

## (f) Citations (verified count: 12)

Brain mechanism (planning + PFC + theta sweeps + BG):
1. Aceituno-Cabezas, Acerbi et al. 2024/2025 "A mechanistic theory of planning in prefrontal cortex" -- eLife Reviewed Preprints 109757 -- spacetime attractor model with parallel world-model copies in synaptic subspaces. https://elifesciences.org/reviewed-preprints/109757
2. Special Collection: Computational Properties of the Prefrontal Cortex Review (J Neurosci 2025, e1944242025).
3. Wikenheiser & Redish 2015 + 2025 papers (PMC12407861, PMC12956831, biorxiv 2025.08.26.672489 and 2025.08.21.671551) "Goal-directed hippocampal theta sweeps during memory-guided navigation."
4. Redgrave et al. 1999 "The basal ganglia: A vertebrate solution to the selection problem."
5. Berns & Sejnowski 1996 "How the Basal Ganglia Make Decisions."

Cross-domain (MCTS, world models, predictive coding planning):
6. MuZero Intuition (Schrittwieser et al. follow-ups; julian.ac blog summary 2020-2022). https://www.julian.ac/blog/2020/12/22/muzero-intuition/
7. Schrittwieser et al. 2020 MuZero / DeepMind -- learned world model + MCTS planner.
8. Rao 2024 "Active Predictive Coding: A Unifying Neural Model for Active Perception, Compositional Learning, and Hierarchical Planning" Neural Computation 36(1):1. https://direct.mit.edu/neco/article/36/1/1/118264
9. Rao 2022 ResearchGate preprint same line (publication/364732567).
10. Friston Free-Energy Principle (Springer 2024 chapter explaining FEP + predictive coding integration with RL).

VSA / HDC planning:
11. Kleyko et al. 2021 "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part I" arXiv 2111.06077.
12. Kelly et al. 2024 "A demonstration of vector symbolic architecture as an effective planning approach" SPIE 2024.

---

## Pre-registration log

- ARM_PB_PC_N128_D15 predicted solve_rate = 0.72; P_deflated(HARD_PASS) = 0.50
- HARD_PASS thresholds locked at dispatch; not editable post-hoc
- 3 seeds [7, 17, 23] for cross-seed cv; cv <= 0.07 required for HARD_PASS
- BlocksWorld 4-block analytic optimal-plan solver REQUIRED at smoke gate to validate ground-truth pipeline
- Parallel-scaling discriminator (N=128 vs N=8, lift >=0.10) is REQUIRED for chain-grade HARD_PASS -- without it the "substrate-better-than-brain" claim is UNSUBSTANTIATED and the cell tiers down to MIDDLE_BAND even if absolute solve_rate >=0.70

## Negative-result revival path (per [[feedback-route-negatives-to-research-2x-3x-revival-drills]])

If Candidate 1 HARD_FAILS:
- pivot 1: Candidate 4 (NREM-replay-trained W_world)
- pivot 2: Candidate 5 (SLAM-style belief-state planning with WM K=50)
- pivot 3: depth-5 instead of depth-15 (BlocksWorld 2-block; simpler domain)
- pivot 4: lift cortex layer cells FIRST (Candidate 6 path) and retry as cortex-composed planning

If Candidate 1 HARD_PASSES_PARTIAL (MIDDLE_BAND):
- pivot 1: Candidate 3 (hierarchical PC)
- pivot 2: Candidate 2 (MH value head)

## Dispatch readiness

Cell `substrate_planning_cortex_composed_beam_v1_META_M7` is ready to dispatch AFTER Cell X verdict lands (sequencing avoids redundant beam-infrastructure development).
- Hand-off file: `notes/exp_dev_handoff_research_gap_B_goal_directed_planning_2026-06-26.md` (companion to this note)
- Estimated wall: 3-5h local_cpu
- Estimated context: ~600 lines of cell code + 200 lines of BlocksWorld evaluator
- Risk: pause-gated; if data/orchestrator_paused.flag exists, defer
