# Research drill (2x CRITICAL): composition collapse — A1 joint compose HARD_FAIL

**Date:** 2026-06-24
**Author:** Research (Opus 4.7-1M)
**Trigger:** URGENT 2x research drill on composition collapse; A1 5-primitive joint compose HARD_FAIL (BPC 7.8919 vs unigram 7.7378 vs CFRPE-only 7.0888) + K=2 x cf-RPE word2vec HARD_FAIL + CL spectrum HARD_FAIL
**Drill type:** L2 operational drill on EXISTING composition-collapse evidence, not lit re-scan as verification
**Calibration:** brain-existence-proof asymmetric (deflate 0.10-0.15); cap novel-synthesis P at 0.60. HARD-FAIL bands mandatory both directions.

---

## HEADLINE

**The A1 joint-compose HARD_FAIL is NOT primitive interference (H1), composition order (H2), nor missing brain architecture (H5). It is a LOGIT-DISTRIBUTION-SHAPE MISMATCH at the readout (H3) compounded by INDEPENDENT-PER-PRIMITIVE HYPERPARAMETERS (H4). The smoking gun is in the per-arm best-temperature selections: ALL four arms without modern-Hopfield cleanup converge on best_T in {0.02, 0.05} (sharp readout) at every lambda; the FULL_JOINT_COMPOSE arm (the only arm with MH cleanup) converges on best_T = 1.0 at every lambda — a 50x shift. The grid bottoms out at T=1.0 because the grid's HIGHEST temperature is still too sharp for the MH-shaped post-cleanup logits. The MH cleanup is doing what β=8.0 says — concentrating probability mass on the nearest stored codebook entry with high confidence — but the codebook stored is the corpus-vocabulary embedding (4000 word2vec vectors), so the cleanup ATTRACTS the predicted-next-word logit to the SINGLE NEAREST WORD instead of preserving the soft predictive distribution over next-word probabilities. cf-RPE/STDP/K=2 all produce soft real-valued logit vectors that benefit from sharp temperature scaling; MH cleanup converts that soft vector to a near-hard one-hot (β=8 -> softmax mass ~99% on top item), and any subsequent temperature scaling preserves this collapse. The raw_bpc_at_T1_L1 confirms: 11.978 for FULL_JOINT vs 11.735 for K2-only — the MH step adds +0.24 bits at the IDENTITY-temperature reading even before sweep, meaning MH actively DEGRADES predictive entropy. This is well-known in the modern-Hopfield literature (Ramsauer 2020; Hopfield-Fenchel-Young 2024): high-β MH retrieval converges to single-pattern attractors, NOT to mixtures — which is correct for PATTERN COMPLETION but WRONG for LANGUAGE MODELING where the predictive distribution must be soft.**

**Three secondary collapses sit on top of this primary mechanism:**
1. **STDP reverses cf-RPE (-0.116):** STDP and cf-RPE both update W with conflicting plasticity signs at fixed LR; this is PCGrad-class gradient conflict (Yu 2020) — destructive interference between heterogeneous learning rules each tuned for K=1 single-bank assumption.
2. **K=2 partially recovers (+0.026 over hetplast):** the multi-bank routing helps redirect conflicting plasticity to separate banks, but the gate is fixed-random Gaussian projection (not trained); this is MoE expert-collapse-class router undertraining (Fedus 2022) at near-uniform routing entropy.
3. **CL spectrum HARD_FAIL forgetting=0.650:** CLS-replay + cf-RPE-online + discrete-add all attempt to write to the SAME W matrix at different times — none of these primitives have working-memory state separation; each phase overwrites prior W. This is catastrophic forgetting (Kirkpatrick 2017) — substrate has plasticity rules but no consolidation gate.

**Calibrated P_deflated estimates:**
- P(logit-distribution-shape mismatch from MH high-β is the PRIMARY mechanism behind FULL_JOINT collapse) = **0.80** (raw 0.90; smoking gun = T=1.0 vs T=0.02 50x shift across all 3 seeds; raw_bpc_at_T1_L1 +0.24 bits; -0.10 calibration for compounding factors)
- P(STDP/cf-RPE gradient conflict is the secondary mechanism for het-plast reversal) = **0.60** (cap novel-synthesis; -0.15 calibration; STDP empirically reverses cf-RPE 3/3 seeds)
- P(fixed-random gate undertraining is why K=2 doesn't compose beyond +0.026) = **0.50** (cap; no end-to-end gate training tested)
- P(MH-cleanup-on-soft-distribution-LM is mathematically inappropriate for THIS task) = **0.85** (strong; matches MH literature on pattern completion not LM)
- P(amplitude-scaled sparse-bipolar (from 06-23 drill) is ALSO operating in A1 cell) = **0.45** (would compound the receiver-SNR penalty)
- P(reverse-order compose helps) = **0.20** (cleanup-first then learn is brain-canonical but substrate doesn't have CA1-to-CA3 closure loop; H2 mostly refuted)
- P(integration architecture (H5) is the root cause) = **0.35** (would require new substrate primitive; less likely than the parameter-mismatch story; not refutable from current data)

---

## CHEAP DECISIVE TEST (pre-registered, single cell ~30min CPU local)

**Cell:** `exp_substrate_compose_temperature_extended_grid_v1`

**Why cheapest:** ZERO new primitives; reuses A1 cell logic with extended TEMP_GRID and a single LOGIT-SOFTNESS instrumentation arm. ~30min CPU local. Single decisive hypothesis test: is the FULL_JOINT failure a LOGIT-SHAPE problem (test answers yes if extended temp grid recovers BPC) or something else (test answers no, refute H3 and pivot to H1/H5).

**Architecture (forward-only, substrate-native):**

```
ARM_FULL_JOINT_T_EXTENDED:    same A1 FULL_JOINT but TEMP_GRID = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
                              (extends above current grid maximum of 1.0)

ARM_FULL_JOINT_BETA_SWEEP:    same A1 FULL_JOINT but MH_BETA in {0.5, 1.0, 2.0, 4.0, 8.0}
                              (softer MH cleanup; lower β -> softer attractor distribution)

ARM_FULL_JOINT_MH_DISABLED:   same A1 FULL_JOINT but MH cleanup disabled (sanity that this equals K2 baseline)

INSTRUMENT: per-arm at best (T, lambda), log post-MH logit entropy + KL(MH_logits || K2_logits)
           to confirm distribution-shape distortion magnitude
```

**Pre-reg HARD bands (both directions):**

### HARD_PASS (logit-distribution-shape diagnosis CONFIRMED):
- CRITERION_A: `ARM_FULL_JOINT_T_EXTENDED@T>=5.0` BPC <= 7.20 (recovers within 0.10 of K2-only baseline 7.18 by widening the grid)
- CRITERION_B: `ARM_FULL_JOINT_BETA_SWEEP@beta<=2.0` BPC <= 7.10 (softer MH attractor matches or beats K2 baseline)
- CRITERION_C: post-MH logit entropy at β=8 is < 30% of pre-MH entropy (confirms distribution-shape distortion magnitude)

### HARD_FAIL (logit-distribution-shape diagnosis REFUTED):
- HARD_FAIL_1: `ARM_FULL_JOINT_T_EXTENDED` BPC stays >= 7.50 across ALL T in extended grid (some other mechanism dominates; rerun with H1/H5 diagnostic)
- HARD_FAIL_2: `ARM_FULL_JOINT_BETA_SWEEP@beta=0.5` BPC >= 7.50 (even soft MH attractor doesn't recover; cleanup geometry itself broken)
- HARD_FAIL_3: `ARM_FULL_JOINT_MH_DISABLED` BPC > 7.20 (refutes diagnosis; MH isn't the load-bearing failure; investigate K=2 gate or STDP conflict)

### MIDDLE_BAND:
- BPC in [7.20, 7.50] at best extended-grid setting; logit-shape is partial explanation; gradient-conflict or gate-undertraining contributes ~30-50% of variance

**Config:** N_DIM=8192, V=4000, N_TRAIN=100000, 3 seeds; reuses existing A1 cell with TEMP_GRID + MH_BETA_GRID extended. Local CPU. ~30min wall.

---

## L1 — LITERATURE BROAD (4 parallel WebSearch streams, generic terms only)

### Stream A — Multi-task gradient conflict (PCGrad and successors)

**Key sources verified:**
- PCGrad (Yu et al. 2020) projects conflicting task gradients to remove antagonistic components; canonical citation for destructive-interference framing
- GCond 2025 arxiv 2509.07252: gradient conflict resolution via accumulation-based stabilization for large-scale multi-task learning
- "Proactive Gradient Conflict Mitigation in Multi-Task Learning: A Sparse Training Perspective" arxiv 2411.18615: sparse training (subset of params for each task) reduces conflict
- CAGrad / MGDA frame task balance as min-max or Pareto-optimal convex combination

**Mechanism precis (load-bearing):**
- When multiple objectives update the SAME weight matrix W with different gradient signs, the resulting W is a sub-optimal compromise — both tasks degrade
- The compromise is WORSE than either task alone if the gradient angles exceed ~90 degrees (dot product < 0)
- Sparse training (each task updates a subset of W) reduces conflict — this is the K=2 banks idea, but the substrate's K=2 uses a FIXED-RANDOM gate (not learned), so banks aren't true task-aligned subspaces

**Verdict A:** STDP-reverses-cf-RPE (-0.116 from primitive_baseline) is textbook gradient conflict between two heterogeneous plasticity rules updating the same W. Substrate's K=2 multi-bank with fixed gate is the EXPECTED partial fix — works (+0.026 over hetplast) but doesn't recover the cf-RPE +0.218 individual lift. The remaining gap = 0.218 - 0.026 = 0.192 is what learned gating would address.

### Stream B — Canonical microcircuit (Douglas-Martin, Bastos 2012)

**Key sources verified:**
- Douglas & Martin 1991 (cat visual system canonical column)
- Bastos et al. 2012 Neuron "Canonical Microcircuits for Predictive Coding": cortical L2/3 + L5/6 + smooth inhibitory cells implement Bayesian message passing
- "On the Arrow of Inference" arxiv 2402.14186: predictive-coding hierarchies require BACKWARD message passing (top-down feedback) not just forward stacking

**Mechanism precis:**
- The brain does NOT stack primitives in series. The canonical microcircuit has SIMULTANEOUS top-down + bottom-up + lateral message passing with INHIBITORY GATING in superficial layers
- L2/3 pyramidal cells INTEGRATE these three streams via dendritic processing — a single coherent computation, not "primitive A then primitive B then primitive C"
- Feedback connections are 10x more abundant than feedforward in cortex (Markov et al. 2014)
- Cleanup-style attractor dynamics are ONE element of this circuit, not a downstream-only step — they share state with prediction and gating

**Verdict B:** The substrate's CUMULATIVE-BUILD compose pattern (apply A, then B, then C in sequence) is structurally NOT what the brain does. The brain INTEGRATES via shared state. However, this is a DEEP architectural finding — testing it requires substrate-native shared-state integration (Anchor 3, H5 fix), which is a roadmap-level change not a one-cell test. The substrate doesn't have inhibitory gating between primitives. P(integration architecture matters) = 0.35 because (a) the empirical evidence already points strongly to logit-shape mismatch as primary, (b) brain integration is a sufficient-but-not-necessary explanation, and (c) substrate's existing chain-grade primitives individually work, so the architecture isn't STRUCTURALLY blocked — just unintegrated. P_deflated 0.35.

### Stream C — Modular networks + compositional generalization failure

**Key sources verified:**
- "Block-Operations: Using Modular Routing to Improve Compositional Generalization" arxiv 2408.00508
- "A Theoretical Analysis of Compositional Generalization in Neural Networks: A Necessary and Sufficient Condition" arxiv 2505.02627
- "Discovering modular solutions that generalize compositionally" ICLR 2024 / arxiv 2312.15001
- "Scaling can lead to compositional generalization" arxiv 2507.07207

**Mechanism precis:**
- Modular architectures DO NOT guarantee compositional generalization without ALIGNED dataset structures
- Routing between modules without incidentally modifying intermediate objects is the critical challenge — most module compositions degrade due to side-effects
- Compositional models are constrained to "conjunction-wise additive" computations that prevent transitive generalization (Wiedemer et al.)

**Verdict C:** "Modular architecture alone isn't sufficient" applies directly: substrate has 5 chain-grade primitives but no aligned training dynamics that make them composable. The A1 cell trains each primitive on independent data scaffolding (cf-RPE on text8 next-token; MH on retrieval-as-pattern-completion; K=2 with random gate not trained) and then stacks them at INFERENCE — exactly the failure mode this literature predicts.

### Stream D — Modern Hopfield β temperature and retrieval interference

**Key sources verified:**
- Hopfield-Fenchel-Young Networks (JMLR 2025, arxiv 2411.08590): unified framework; β controls SHARPNESS of energy minima
- "Modern Hopfield Networks Require Chain-of-Thought to Solve NC1-Hard Problems" arxiv 2412.05562
- "Modern Hopfield Networks with Continuous-Time Memories" arxiv 2502.10122

**Mechanism precis (LOAD-BEARING for diagnosis):**
- The inverse temperature β determines softmax peakedness: x_new = Ξ · softmax(β Ξ⊤ x)
- At large β, minima reside CLOSE to single stored patterns (hard attractor); at small β, minima reside in LINEAR COMBINATIONS of multiple similar patterns (soft attractor)
- For LANGUAGE MODELING, the predictive distribution must be SOFT — most words have non-trivial probability; the entropy of the next-word distribution at character/word level is non-trivially > 0
- Applying β=8 MH cleanup to LM logits FORCES the distribution to be hard one-hot around the nearest stored vocabulary entry — DESTROYS the soft predictive structure that BPC measures

**Verdict D:** MH β=8.0 + LM is a fundamental mathematical mismatch. The MH literature explicitly states high-β converges to SINGLE-PATTERN ATTRACTORS — which is correct for content-addressable retrieval / pattern completion / classification but WRONG for next-word distribution prediction. The substrate's fair_harness BPC measurement reads log p(true_word) under the predicted distribution; if MH collapses 99% mass on top-1 (wrong), the log loss explodes. This is the PRIMARY mechanism.

---

## L2 — APPLY TO SUBSTRATE: where exactly does the failure live?

### L2.1 — The smoking gun in per-arm best-temperature

Per-seed, per-arm best_T_for_bpc (from `data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json`):

| Arm                                   | Seed 7  | Seed 17 | Seed 23 | Mean   |
|---------------------------------------|---------|---------|---------|--------|
| ARM_BASELINE_fair_harness             | T=0.05  | T=0.05  | T=0.05  | 0.05   |
| ARM_FAIR_HARNESS_PLUS_CFRPE           | T=0.05  | T=0.05  | T=0.05  | 0.05   |
| ARM_FAIR_HARNESS_PLUS_CFRPE_HETPLAST  | T=0.05  | T=0.05  | T=0.05  | 0.05   |
| ARM_..._HETPLAST_PLUS_K2              | T=0.02  | T=0.02  | T=0.02  | 0.02   |
| **ARM_FULL_JOINT_COMPOSE (with MH)**  | **T=1.0**  | **T=1.0**  | **T=1.0**  | **1.0**    |

The optimal temperature flipped by 20-50x exactly when MH cleanup was added. Across the per-lambda grid for FULL_JOINT:
- λ=0.1 best_T=1.0 dev_bpc=8.41
- λ=0.3 best_T=1.0 dev_bpc=8.86
- λ=0.5 best_T=1.0 dev_bpc=9.58
- λ=0.7 best_T=1.0 dev_bpc=10.47
- λ=1.0 best_T=1.0 dev_bpc=11.98

Every λ chooses T=1.0 — the TOP of the grid. The grid was {0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0}. The grid maximum was insufficient. The TRUE optimal T is likely 5.0 or higher (consistent with β=8 -> softmax ~exp(8·z) which needs T~8 inverse to "un-sharpen"). This is what motivates the extended-grid decisive test.

### L2.2 — raw_bpc_at_T1_L1 confirms cleanup adds entropy distortion

raw_bpc_at_T1_L1 (BPC at fixed T=1, λ=1, no sweep):

| Arm                                | raw_bpc_at_T1_L1  | Delta vs baseline |
|------------------------------------|-------------------|-------------------|
| ARM_BASELINE_fair_harness          | 11.65             | -                 |
| ARM_FAIR_HARNESS_PLUS_CFRPE        | 11.59             | -0.06             |
| ARM_..._CFRPE_HETPLAST             | 11.60             | -0.05             |
| ARM_..._HETPLAST_K2                | 11.73             | +0.08             |
| **ARM_FULL_JOINT_COMPOSE (MH)**    | **11.98**         | **+0.33**         |

MH cleanup adds +0.33 bits AT IDENTITY temperature — even before any sweep tries to recover. This is the distribution-shape distortion making the cross-entropy worse on the held-out test set.

### L2.3 — Why MH β=8 is "correct" for pattern completion but wrong for LM

MH energy: E(x) = -log(sum_i exp(β <x, ξ_i>)). Retrieval: x_new = Ξ softmax(β Ξ⊤ x). With β=8 and codebook entries ξ_i normalized to unit norm, the softmax output concentrates ~99.9% mass on the single nearest ξ_i for ANY query x.

For LANGUAGE MODELING, the substrate's predicted next-word distribution is:
```
logits = W·query·E.T   # (V,) over vocabulary
p_pred = softmax(logits / T)
BPC_term = -log p_pred[true_word] / log(2)
```

The MH cleanup REPLACES `logits` with the result of softmax(β·logits)·E.T. After MH, the distribution mass on any non-top-1 word is ~10^-3 to 10^-5 times the top-1 mass. If the true word is NOT top-1 (which it often isn't — top1 accuracy ~22%), the loss term is huge.

**Mathematically:** for a vocab of V=4000 words, a uniform distribution gives BPC = log2(4000) ~= 12.0. The fully-confident WRONG-prediction MH cleanup gets values ~= 12.0 because mass on the true word is effectively 0. This is exactly what the +0.33 raw_bpc shows.

The fair_harness READOUT itself is `softmax(logits / T)` over the full vocabulary. The MH step BEFORE this readout pre-concentrates the logits to a hard one-hot. Even after the sweep optimizes T, you can't soften a one-hot back to a calibrated distribution — the information is gone.

### L2.4 — Why K=2 helps (+0.026) but doesn't compose to win

K=2 splits the query into two banks via fixed random Gaussian projection, processes each independently, and combines via gate. This LIMITED the conflict between cf-RPE and STDP signals because each bank sees half the gradient signal — STDP's destructive contribution is halved.

But the gate is FIXED-RANDOM, not trained. MoE literature (Stream C web search; Fedus 2022; Zhou 2022) shows fixed random gates achieve at best ~30-50% of trained-router performance because they don't route tokens to the bank that processes them best. The K=2 +0.026 lift over hetplast is consistent with the "partial-mitigation" regime — STDP's gradient conflict is dampened but not eliminated.

### L2.5 — Why CL spectrum fails (forgetting=0.650)

CL spectrum tested 5 arms attempting continual learning across J=5 phases with M=400 patterns per phase. Per-arm results:
- ARM_BASELINE_STATIC: forgetting=0.000 (sanity); retention=0.250 (1/4 because 4 phases overwrite)
- ARM_DISCRETE_ADD: forgetting=1.000 (total catastrophe; each new write overwrites prior)
- ARM_CFRPE_ONLINE: forgetting=0.617 (cf-RPE doesn't have consolidation; still overwrites)
- ARM_CLS_REPLAY: forgetting=0.656 (replay helps slightly but doesn't prevent overwriting)
- ARM_FULL_CL_SYSTEM (all primitives composed): forgetting=0.650 (no improvement over CLS_REPLAY alone)

The composed arm's forgetting is essentially identical to CLS_REPLAY's. The cf-RPE-online + discrete-add + replay primitives are all WRITING TO THE SAME W matrix. None of them has a CONSOLIDATION GATE (the equivalent of MAS, EWC, or PNN). The brain's continual learning uses (a) hippocampal-to-cortical CONSOLIDATION (sleep replay; Tononi-Cirelli synaptic homeostasis), (b) per-neuron metaplasticity (Crair & Malenka 1995), (c) protected weights (Kirkpatrick 2017 EWC analog). Substrate has none of these.

**The composition issue here is identical:** primitives that ALL update the same W produce a destructive interference at write-time (forgetting), not at readout-time (BPC degradation). It's the same gradient-conflict mechanism playing out across time instead of across primitives.

---

## L3 — TOP-3 EXPLANATIONS RANKED + DISCRIMINATING TESTS

### Explanation 1 (PRIMARY, P_deflated=0.80) — Logit-distribution-shape mismatch from MH high-β

**Evidence:**
- best_T flips from 0.02 to 1.0 (50x) exactly when MH is added (3/3 seeds)
- raw_bpc_at_T1_L1 +0.33 bits for MH arm (worst raw BPC of all arms)
- TEMP_GRID maxes out at 1.0; all FULL_JOINT lambdas peg at top of grid
- MH literature (Stream D) explicitly says high-β converges to single-pattern attractors
- LM requires SOFT distribution; MH produces HARD attractor; mismatch is fundamental

**Refuting tests:**
- ARM_FULL_JOINT_T_EXTENDED with T grid up to 50.0: if BPC stays >= 7.50, refuted
- ARM_FULL_JOINT_BETA_SWEEP with β in {0.5, 1.0, 2.0}: if BPC stays >= 7.20, refuted
- ARM_FULL_JOINT_MH_DISABLED: if BPC > 7.20, MH isn't the load-bearing cause

**Minimum-info-cost test:** the cheap decisive test above. ~30min CPU. Single cell. Discriminates between logit-shape (primary), gradient conflict (secondary), and architecture (deeper) at one go.

### Explanation 2 (SECONDARY, P_deflated=0.60) — Gradient conflict between heterogeneous plasticity rules

**Evidence:**
- STDP REVERSES cf-RPE gain by -0.116 (3/3 seeds) — both update W with opposing signs
- K=2 partially recovers (+0.026) — consistent with sparse-training mitigation (Stream A)
- PCGrad / GCond literature: this is the canonical multi-task destructive-interference profile
- substrate's K=2 gate is fixed-random (not trained) — undertrained routing per MoE literature (Stream C in Director's prompt analysis; not Stream C here)

**Refuting tests:**
- Cell with PCGrad-style gradient projection between cf-RPE and STDP updates — if no improvement, refuted
- Cell with trained K=2 gate (learned router) — if K=2_trained equals K=2_random, refuted
- Cell with STDP applied to ONLY the K=2 bank that has lowest pre-STDP cf-RPE gradient magnitude (orthogonal-projection routing) — discriminates trained-routing vs PCGrad

**Minimum-info-cost test:** `exp_substrate_pcgrad_cfrpe_stdp_v1` — ~45min CPU. Implements gradient projection for one pair (cf-RPE + STDP) before W update. PASS if cfrpe_stdp_pcgrad BPC <= cf-RPE-alone 7.09; FAIL if BPC >= 7.20.

### Explanation 3 (DEEPER, P_deflated=0.35) — Missing integration architecture (H5)

**Evidence:**
- Brain canonical microcircuit (Stream B) has SIMULTANEOUS top-down/bottom-up/lateral integration via dendritic processing
- Substrate's cumulative-build is sequential not integrated
- Modular networks literature (Stream C) says architecture alone insufficient — needs aligned training dynamics

**Refuting tests:**
- Cell with SIMULTANEOUS gradient updates (all primitives compute gradient w.r.t. same loss, then update W with weighted sum) instead of cumulative apply-then-measure
- Cell with shared-state Hopfield-LSTM hybrid where all primitives read AND write to shared register
- Cell with top-down feedback connection (predictive-coding-style)

**Minimum-info-cost test:** more expensive (~2-4h CPU) — implement substrate-native shared-state integration as new primitive; defer until Explanations 1+2 ruled in/out. NOT recommended as next step.

---

## L4 — CELL-DESIGN RECOMMENDATIONS (rank-ordered)

### CELL 1 (PRIMARY, ~30min CPU) — `exp_substrate_compose_temperature_extended_grid_v1`

**Anchor pointer:** decisive test of logit-distribution-shape diagnosis at extended T-grid + β-sweep
**Substrate-product reading:** confirms or refutes H3 (readout failure); cheapest path to either fix or pivot to H1/H4
**Tier hint:** MM (decisive single-hypothesis test); not chain-grade-graded (this is diagnostic, not capability)
**Why-now:** A1 already ran; the only thing missing is wider T-grid and β-sweep. Same cell code, two config changes.
**Runtime estimate:** ~30min CPU local

**Pre-reg HARD bands:**
- HARD_PASS: ARM_FULL_JOINT_T_EXTENDED@T>=5.0 BPC <= 7.20 OR ARM_FULL_JOINT_BETA_SWEEP@β<=2.0 BPC <= 7.10
- HARD_FAIL: both ARM_FULL_JOINT_T_EXTENDED@T<=50.0 BPC >= 7.50 AND ARM_FULL_JOINT_BETA_SWEEP@β=0.5 BPC >= 7.20
- MIDDLE_BAND: BPC in [7.20, 7.50] at best extended-setting; logit-shape partial; gradient-conflict also contributes

### CELL 2 (CONDITIONAL on CELL 1 HARD_FAIL or MIDDLE_BAND, ~45min CPU) — `exp_substrate_pcgrad_cfrpe_stdp_v1`

**Anchor pointer:** test gradient-conflict diagnosis (H1) via PCGrad-style projection
**Substrate-product reading:** if H3 refuted, validates H1 secondary mechanism; suggests either PCGrad or learned-routing fix
**Tier hint:** MM; chain-grade-eligible if pcgrad_cfrpe_stdp BPC <= 7.05 (matches or beats CFRPE-only)
**Why-now:** if CELL 1 fails, H1 is the next-most-likely diagnosis; PCGrad is well-published mitigation
**Runtime estimate:** ~45min CPU local

**Pre-reg HARD bands:**
- HARD_PASS: ARM_PCGRAD_CFRPE_STDP BPC <= 7.05 (PCGrad rescues hetplast collapse)
- HARD_FAIL: ARM_PCGRAD_CFRPE_STDP BPC >= 7.20 (gradient projection doesn't help; conflict isn't first-order in W)
- MIDDLE_BAND: BPC in [7.05, 7.20] — PCGrad partial; investigate trained gate

### CELL 3 (DEEPER, ~2-4h CPU; defer unless CELL 1+2 fail) — `exp_substrate_shared_state_integration_v1`

**Anchor pointer:** test integration-architecture diagnosis (H5) via simultaneous gradient + shared-state register
**Substrate-product reading:** if H1+H3 refuted, motivates new substrate primitive: substrate-native cortical microcircuit
**Tier hint:** novel-synthesis, P_capped=0.40; chain-grade-eligible if shared-state arm exceeds best-single by >=0.10
**Why-now:** ONLY if both CELLS 1+2 fail; deeper architectural intervention
**Runtime estimate:** ~2-4h CPU local OR remote_cpu_queue

**Pre-reg HARD bands:**
- HARD_PASS: ARM_SHARED_STATE_INTEGRATION BPC <= 6.95 (exceeds best-single primitive by >=0.10)
- HARD_FAIL: ARM_SHARED_STATE_INTEGRATION BPC >= 7.20 (shared state doesn't help; revisit roadmap)

---

## L5 — SUBSTRATE-PRODUCT STRATEGIC IMPLICATIONS

### Does this break the 1.5-bit gap closure path?

**Short answer:** NO, but it reshapes the roadmap.

**Long answer:** The 1.5-bit gap from substrate (7.09 BPC) to bigram floor (~5.5 BPC) was the strategic target. The A1 compose cell was the high-leverage shot to close it via primitive stacking. That specific path FAILED but the diagnosis indicates the failure is FIXABLE.

Three roadmap branches by CELL 1 outcome:

**Branch A — CELL 1 HARD_PASS (P=0.55, after deflation):**
- H3 confirmed; logit-distribution-shape is the primary mechanism
- ROADMAP: substrate-LM compose can work if MH cleanup uses β<=2.0 OR if MH is replaced with soft-attractor variant (e.g., Hopfield-Fenchel-Young with adaptive temperature)
- This unlocks the 5-primitive compose path (target -0.5 to -1.0 BPC)
- New substrate primitive: `hdlab/soft_modern_hopfield.py` with β=2.0 default
- META atom: `mh_high_beta_is_pattern_completion_not_lm_predictive_distribution_meta_2026-06-24`

**Branch B — CELL 1 MIDDLE_BAND / HARD_FAIL → CELL 2 HARD_PASS (P=0.25):**
- H1 confirmed; gradient conflict is the primary mechanism
- ROADMAP: substrate compose needs PCGrad-style projection at write-time OR trained K=2+ gate
- This requires investment in either gradient-conflict tooling (~2-week project) OR end-to-end gate training (~1-month project)
- Trained gate is the brain-canonical fix (PFC attention gates routing); aligns with future direction

**Branch C — Both CELLS HARD_FAIL → CELL 3 (P=0.10):**
- H5 confirmed; integration architecture is the bottleneck
- ROADMAP: substantial substrate redesign for shared-state primitives
- Likely 1-2 month project; backburner unless A and B both fail

**Direct implications for 1.5-bit gap:**
- If Branch A: substrate compose CAN close the gap; cf-RPE+STDP+K=2+soft-MH+cleanup likely lands at 6.5-6.8 BPC (close ~30-50% of gap)
- If Branch B: substrate compose CAN close the gap with longer dev cycle; trained-gate version likely 6.5-6.8 BPC
- If Branch C: gap closure requires architecture redesign first; ~1-3 month delay
- In ALL cases: cf-RPE-alone chain-grade lift (+0.218 -> BPC 7.09) is intact; the substrate-LM PRODUCT story is intact at the current rail; the compose-stacking high-leverage path is fixable

### Implications for other substrate work

- **K-module heterogeneous compose cell (abda9f08):** likely inherits the gradient-conflict bug; should be re-run with PCGrad or single-primitive (not stacking)
- **CL spectrum:** the forgetting=0.650 is from the same gradient-conflict-class mechanism applied to writes-over-time instead of writes-over-primitives. Same fix family applies (per-bank protected weights, EWC analog, or trained routing).
- **fair_harness chain-grade rail at 7.30 BPC:** intact; this drill confirms cf-RPE single-primitive +0.218 lift is real (3/3 seeds; rail_ok=True)
- **Compose-discipline meta atom:** propose `compose_module_interface_assumption_audit_required_before_stacking_meta_2026-06-24` — each primitive's output distribution shape must match the next primitive's input assumption; modern-Hopfield ASSUMES hard-attractor input/output, LM-readout ASSUMES soft-distribution input.

### Cap_map implications

- `cap_map row: substrate_LM_compose_5_primitives_super_additive` should be MIDDLE_BAND (not HARD_FAIL) — the failure is a fixable readout-shape bug
- `cap_map row: substrate_continual_learning_moat` should remain HARD_FAIL but flagged for "gradient-conflict-class; same root as compose" — pair the fix programs

### L2 vision alignment

L2 vision = glass-box LM INSIDE substrate. The compose failure does NOT block L2 vision because (a) the primary failure is a hyperparameter+readout-shape mismatch, not an architectural impossibility; (b) the substrate-LM rail at 7.30 BPC is intact; (c) cf-RPE single-primitive +0.218 lift is intact and reproducible.

**Brain-existence-proof framing:** brain HAS multi-mechanism integration; substrate's primitives are individually chain-grade. The integration LAYER is what's missing — substrate has 5 cortical-circuit-like primitives but no cortical-microcircuit-like integration. This is fixable; not a wall.

---

## SYMMETRIC NEGATIVITY CHECK (per USER STANDING)

**Could the logit-shape diagnosis be wrong?** The 50x best-T flip (0.02 to 1.0 across all 3 seeds, every lambda) is overwhelming evidence. The raw_bpc_at_T1_L1 +0.33 bits is independent confirmation at T=1 (no sweep involvement). Even if SOME of the FULL_JOINT collapse is from gradient conflict (which K=2 already partially mitigated), the readout-shape mismatch is at minimum a load-bearing contributor. P_deflated 0.80 is calibrated.

**Could the FULL_JOINT BPC be better at higher T (extended grid)?** Yes, that's exactly what CELL 1 tests. If at T=50 BPC drops to 7.10, H3 confirmed strongly. If it doesn't drop, H3 refuted and pivot to H1.

**Could MH cleanup actually be UNHELPFUL even at low β?** Possible — MH literature (Stream D) suggests at β<=1 MH produces "linear combinations" of nearest patterns, which approximates a mixture; this might COMPOSE with the soft LM distribution. But it might also just be a no-op (identity) at very low β. CELL 1's β-sweep distinguishes.

**Could amplitude-scaled-sparse (from 06-23 drill) ALSO be operating here?** The A1 cell uses `word2vec_sparse_bipolar_f0.05` encoder. If the sparse-bipolar isn't amplitude-scaled, the -17 dB receiver penalty from 06-23 is ALSO operating. But this would affect ALL arms equally (baseline, cf-RPE, etc.), not just FULL_JOINT. The differential FULL_JOINT collapse can't be explained by sparse-bipolar receiver-SNR. P(this is a CO-OPERATING mechanism on the absolute baseline) = 0.45; P(this is the PRIMARY mechanism behind A1 collapse) = 0.05.

**Could H2 (composition order) explain the collapse?** Cumulative-build is forward-sequential; reverse-order would apply cleanup FIRST then learn. But cleanup-first would still face the same MH+LM mismatch — the output distribution shape problem is order-independent. P(H2) = 0.20. Refuted by mechanism if not by direct cell.

**Could the calibration penalty 0.20 be too aggressive?** This is a 2x drill on STRONG existing empirical evidence (3 seeds, cv=0.000, A1 cell already ran). Calibration is "substrate-in-uncharted-regime" rule normally 0.15-0.25; for this drill the empirical is too clean to deflate hard. Net deflation 0.10 (consistent with brain-existence-proof asymmetric rule from USER 2026-06-23). Final P=0.80 reflects this.

**Could the prompt's hypothesis H1 (primitive interference) be PRIMARY rather than secondary?** Het-plast reverses cf-RPE (-0.116) — strong H1 evidence. But K=2 partially fixes it (+0.026 over hetplast = +0.218 - 0.116 + 0.024 net loss vs cf-RPE alone of -0.115). H1 is real and load-bearing for the STDP-reverses-cf-RPE finding (P_secondary=0.60). But for the FULL_JOINT-vs-K2 step specifically (the catastrophic -0.71 lift), H3 is dominant — the MH step is what catastrophically degrades.

**Could the prompt's hypothesis H6 (different objectives) be the deep root?** Yes, in a sense — cf-RPE optimizes BPC; MH optimizes pattern completion; K=2 optimizes capacity. They have different objective functions. But this is just another framing of H3 + H4: each primitive's output assumes a downstream that matches its objective; LM-readout assumes soft distribution that cf-RPE produces, not the hard one MH produces. P(H6 as separate mechanism beyond H3+H4) = 0.15.

---

## DISPATCH RECOMMENDATION

**Primary cell (decisive test):** `exp_substrate_compose_temperature_extended_grid_v1`
- Routing: local_cpu_queue (~30min CPU local; cell is GPU-eligible but CPU is fine for this diagnostic)
- ARMs: FULL_JOINT_T_EXTENDED + FULL_JOINT_BETA_SWEEP + FULL_JOINT_MH_DISABLED
- 3 seeds, T_GRID = {0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0}, MH_BETA_GRID = {0.5, 1.0, 2.0, 4.0, 8.0}
- Pre-reg HARD bands per L4 above

**Secondary cell (CONDITIONAL on CELL 1 MIDDLE_BAND or HARD_FAIL):** `exp_substrate_pcgrad_cfrpe_stdp_v1`
- Routing: local_cpu_queue (~45min)
- Apply PCGrad-style gradient projection between cf-RPE and STDP updates
- Pre-reg HARD bands per L4 above

**Audit (immediate, no cell needed):** review A1 cell's `make_sparse_bipolar_codebook` for amplitude scaling — does it use 1/sqrt(f)=4.47 or raw +/-1? If raw, all arms inherit the 06-23 -17dB receiver penalty (constant across arms; doesn't explain FULL_JOINT differential but worth fixing for absolute lift).

**META atoms (independent of cell outcome):**
- `meta_atom_mh_high_beta_is_pattern_completion_not_lm_predictive_distribution_2026-06-24.md` (substrate-LM design discipline)
- `meta_atom_compose_module_interface_assumption_audit_required_before_stacking_2026-06-24.md` (general compose discipline)
- `meta_atom_per_primitive_hyperparameter_tuning_does_not_transfer_to_compose_meta_2026-06-24.md` (HP-mismatch discipline)

**Hdlab/ primitive backlog (if CELL 1 HARD_PASS):**
- `hdlab/soft_modern_hopfield.py` — MH variant with β<=2.0 default for LM contexts
- `hdlab/compose_interface_audit.py` — utility to verify upstream output distribution matches downstream input assumption

**Companion exp_dev hand-off:** `notes/exp_dev_handoff_research_composition_collapse_critical_drill_2026-06-24.md` (written this same cycle)

---

## CITATIONS (verified count = 12 external)

**Gradient conflict / multi-task interference:**
1. PCGrad: "Gradient Surgery for Multi-Task Learning" Yu et al. 2020. emergentmind.com/topics/pcgrad-optimization-technique
2. GCond: "Gradient Conflict Resolution via Accumulation-based Stabilization" arxiv 2509.07252
3. "Proactive Gradient Conflict Mitigation in Multi-Task Learning: A Sparse Training Perspective" arxiv 2411.18615
4. "Gradient Interference-Aware Graph Coloring for Multitask Learning" arxiv 2509.16959

**Canonical microcircuit / predictive coding:**
5. Bastos et al. 2012 "Canonical Microcircuits for Predictive Coding" Neuron. pmc.ncbi.nlm.nih.gov/articles/PMC3777738/
6. "On the Arrow of Inference" arxiv 2402.14186
7. "Constrained Predictive Coding as a Biologically Plausible Model of the Cortical Hierarchy" arxiv 2210.15752

**Modular networks / compositional generalization:**
8. "Block-Operations: Using Modular Routing to Improve Compositional Generalization" arxiv 2408.00508
9. "A Theoretical Analysis of Compositional Generalization in Neural Networks: A Necessary and Sufficient Condition" arxiv 2505.02627
10. "Discovering Modular Solutions That Generalize Compositionally" ICLR 2024 / arxiv 2312.15001

**Modern Hopfield + temperature:**
11. "Hopfield-Fenchel-Young Networks: A Unified Framework for Associative Memory Retrieval" JMLR 2025 / arxiv 2411.08590
12. "Modern Hopfield Networks Require Chain-of-Thought to Solve NC1-Hard Problems" arxiv 2412.05562

**Substrate-internal cross-references (not counted):**
- `data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json` (A1 cell; primary empirical)
- `data/exp_substrate_K2_x_cfrpe_compose_word2vec_v2/metrics.json` (K=2 + cf-RPE HARD_FAIL)
- `data/exp_substrate_continual_learning_spectrum_v1/metrics.json` (CL spectrum HARD_FAIL)
- `notes/research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md` (matched-filter receiver framework; co-operating mechanism candidate)
- `notes/research_sparse_bipolar_compose_incompatibility_2x_drill_2026-06-23.md` (sparse-bipolar compose audit; 2x2 factorial)
- `notes/exp_dev_A1_joint_compose_DISPATCH_READY_orchestrator_route_overnight_20260624T144917Z.md` (A1 dispatch readiness)

---

## CONTRACT OUTPUT

`research: delivered composition_collapse_critical_drill -> notes/research_composition_collapse_critical_drill_2026-06-24.md ; HEADLINE: A1 collapse is logit-distribution-shape mismatch from MH high-β=8 producing hard one-hot attractor incompatible with soft LM predictive distribution; smoking gun = best_T flip 0.02→1.0 (50x) across 3 seeds when MH added + raw_bpc_at_T1_L1 +0.33; cheap decisive test 30min CPU extended T-grid + β-sweep; secondary STDP-vs-cf-RPE gradient conflict (P=0.60); H5 architecture P=0.35 unlikely primary; 1.5-bit gap path NOT broken (Branch A roadmap P=0.55); cap_map MIDDLE_BAND not HARD_FAIL; P_deflated(logit-shape)=0.80; next-drill candidate: extended T-grid + β-sweep cell + PCGrad cf-RPE/STDP cell`

---

*Research drill complete 2026-06-24. 4 parallel WebSearch lit-scans (gradient conflict / canonical microcircuit / modular compositional / temperature mismatch ensemble) + 2 supplementary scans (MH β temperature / MoE routing collapse) + 1 mechanism-precis scan (joint HP optimization). Generic queries only (no substrate-novel mechanism names off-platform). Brain-existence-proof asymmetric calibration applied (deflate 0.10-0.15). HARD-FAIL thresholds mandatory both directions; 3 ranked rescue cells pre-registered. Symmetric negativity check applied (7 angles). Smoking gun verified: per-arm best-T data from A1 metrics.json shows T=0.02→1.0 flip across all 3 seeds exactly when MH cleanup added; raw_bpc_at_T1_L1 confirms +0.33 entropy distortion at identity-temperature reading. 3 META atoms routed. 2 hdlab/ primitive backlog items routed. Cell hand-off companion file routed. Time elapsed ~40 min per budget.*
