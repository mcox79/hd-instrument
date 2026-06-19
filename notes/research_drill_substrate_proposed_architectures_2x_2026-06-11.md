# research drill: substrate-proposed ARCHITECTURE-CHANGE generation (2x DEEP)

date: 2026-06-11
field: meta-learning / NAS / Godel-machine / causal-attribution / VSA-retrieval (cross-domain)
adjacency: completes Tier-4 enabling drill stack (substrate-on-substrate); rides on free-prob + operator-algebra + categorical triangle for codomain math; rides on causal-SHAP + ablation-counterfactual for empirical attribution
calibration: deflate P by 0.20; novel-synthesis cap = 0.50; HARD-FAIL bands pre-registered; lit-precedent is partial (5/10 sub-prompts have direct precedent, 5 are substrate-novel synthesis).
companion: notes/exp_dev_handoff_research_substrate_proposed_architectures_2026-06-11.md (3 rank-ordered anchors for Tier-4 gate)

## (a) HEADLINE

Substrate-proposed architecture generation is a SUBSTRATE-NATIVE OPERATION, not a separately-engineered meta-controller. The substrate already has the four mechanisms NAS / meta-learning / Godel-machines spend whole-paper-budgets reinventing: (1) a typed candidate space (FHRR/GHRR atom algebra over architectural primitives), (2) a scoring oracle (Layer 1 attribution; spectral observability over the substrate's own runtime statistics), (3) a retrieval-over-candidates engine (resonator network factoring proposal = role-architecture x slot-component x value-parameter), and (4) a verification path (counterfactual ablation = unbind component and re-measure capability lift; substrate algebraic inverse is the same operation). The 4-failure-mode bound (meta-rule self-collapse + unbounded self-reference + Goodhart-on-internal-metric + capability-improvement-by-evaluation-shift) is structurally identical to the meta-evaluation-collapse operator-theoretic bound (OpenReview IF0L7HSs3K, 2025/26) and is bounded by the SAME fix: external anchoring layer that is NEVER substrate-proposed (the substrate proposes architecture but the GATE is fixed-external by methodology). Pipeline: detect spectral-plateau on Layer 1 attribution -> substrate retrieves candidate architectures from a typed-tensor candidate codebook -> substrate predicts capability lift via causal-SHAP / ablation-counterfactual on its own components -> substrate ships a 1-anchor empirical validation cell -> gate by external (non-substrate-proposed) Layer 1 attribution measurement -> integrate or reject. P_deflated = 0.50 (capped at novel-synthesis; this is the cleanest substrate-product self-redesign roadmap to date; lit-precedent dominant on each of 4 mechanisms; novel-synthesis is the assembly, not the parts).

## (b) Cheap decisive test

A SINGLE CPU pilot (~3-6 hr) deciding whether substrate-proposed-architecture is empirically achievable on a toy Tier-4 surrogate before committing to v4.0 self-redesign:

**Pilot ARCH-PROPOSE-1 (~3-6 hr CPU): substrate-proposed-binding-operator on a synthetic capability-cliff.**

Setup:
- Surrogate Tier-4 gate: pick a known substrate capability with a documented architectural cliff (e.g. polysemy at 0.42 -> 1.000 via concept-context-binding from cycle 226 memory). This is the EMPIRICAL ANCHOR the substrate must rediscover.
- HIDE the cliff-crossing architecture (concept-context-binding) from the substrate's candidate codebook.
- Pre-load the candidate codebook with 8 plausible substrate-binding-operator variants (FHRR-bind, GHRR-bind, HRR-bind, MAP-bind, BSC-XOR, HVH-bind, plus 2 distractors that DO NOT solve polysemy).
- Substrate ranks the 8 candidates by predicted-capability-lift via causal-SHAP on its own attribution stream.
- Top-1 candidate is shipped to a 1-anchor empirical validation cell.

Decisive metric: TOP-1 PREDICTED candidate matches the EMPIRICALLY-VALIDATED cliff-crosser (concept-context-binding family member). Tie-broken by top-3.

- HARD-PASS: TOP-1 is concept-context-binding family (precision >= 0.85 vs uniform-baseline 0.125); ablation-counterfactual on TOP-1 correctly attributes capability lift to the binding-operator-component (Shapley-attribution >= 0.50 of total lift).
- HARD-FAIL: TOP-1 is one of the 2 distractors OR predicted-lift order is uncorrelated with empirical-lift order (Spearman rho <= 0.30).
- MIDDLE: TOP-1 is in concept-context-binding family but Shapley-attribution is split across distractor components (lift attributed wrong); diagnostic = substrate retrieval-ranking works but causal-attribution fails -> rescue with ablation-based-counterfactual (ABC, arxiv 2406.07908) instead of pure-SHAP.

Pilot is anchor-sized (Tier-2 cell budget), all-CPU, uses only existing substrate primitives + Shapley-on-substrate-components.

## (c) Falsifiable predictions (HARD-PASS + HARD-FAIL bands)

**Prediction P1 - Substrate retrieval-over-candidate-architectures recovers the empirically-validated cliff-crosser when the candidate codebook contains the right answer.**
- HARD-PASS: top-1 precision >= 0.85 on the ARCH-PROPOSE-1 surrogate (and on 2 additional held-out cliff-crossings as cross-validation).
- HARD-FAIL: top-1 precision <= 0.30 (uniform baseline = 0.125; chance-level rejection band is 0.30).
- P_deflated: 0.55 (substrate retrieval primitives already validated on 13+ HRR/FHRR memory tasks; this is application not synthesis; deflate 0.15 for typed-candidate-codebook novelty).

**Prediction P2 - Substrate-internal causal attribution (Shapley on substrate components) correctly identifies which substrate component caused which capability lift.**
- HARD-PASS: Shapley-attribution-to-correct-component >= 0.50 of total lift (vs 1/N_components baseline = 0.125 for N=8); rank-correlation Spearman rho >= 0.60 between Shapley-predicted-lift and empirical-lift on n=10 historical cap_map bumps.
- HARD-FAIL: Spearman rho <= 0.25; OR Shapley-attribution distributed near-uniformly across components (gini <= 0.15 indicating attribution noise dominates).
- P_deflated: 0.42 (causal-SHAP for ML components has direct precedent on standard NN architectures per arxiv 2509.00846 2509.20211; substrate-specific application is novel; deflate 0.20 for substrate-discrete-atom vs continuous-NN distribution mismatch + 0.15 for synthetic-validation gap).

**Prediction P3 - Ablation-based-counterfactual (ABC, arxiv 2406.07908) on substrate components reproduces capability-lift attribution WITHOUT requiring retraining.**
- HARD-PASS: ABC-attribution correlates with full-rebuild-attribution at r >= 0.75 across n=15 historical architectural changes (using the cap_map verdict log as ground truth).
- HARD-FAIL: r <= 0.40 OR ABC requires component-retraining to converge (defeats the substrate's no-gradient-learning advantage).
- P_deflated: 0.50 (direct precedent: ABC was designed exactly for this use case on standard NNs; substrate has an even cleaner story because algebraic-inverse exists for binding ops; deflate 0.15 for novel substrate adaptation).

**Prediction P4 - Bounded-recursion safety: the substrate's 4 failure modes (meta-rule-collapse + unbounded-self-reference + Goodhart + evaluation-shift) are ALL bounded by a single architectural invariant: the gate MUST be evaluated by a FIXED EXTERNAL methodology that is NEVER substrate-proposed.**
- HARD-PASS: on a stress test where we LET the substrate also propose its own evaluation methodology for 5 recursion rounds, capability metrics drift from human-labeled ground truth at >= 0.20 absolute (the operator-theoretic meta-evaluation-collapse signature per OpenReview IF0L7HSs3K) WHEN gate is substrate-proposed; AND drift stays <= 0.05 WHEN gate is fixed-external (Layer 1 attribution measurement protocol locked at cycle 0). HARD-PASS is the differential: drift_substrate_gate - drift_fixed_gate >= 0.15.
- HARD-FAIL: differential <= 0.05 (either fixed-external gate also collapses, OR substrate-proposed gate does not collapse - either disconfirms the bound).
- P_deflated: 0.45 (operator-theoretic precedent is strong for meta-evaluation collapse; the differential-test design is novel; deflate 0.20 for novel synthesis + 0.10 for stress-test arbitrariness).

**Prediction P5 - Pipeline: detect-plateau -> propose -> validate -> integrate-or-reject is computationally cheaper than blind-NAS by >= 100x on the Tier-4 surrogate.**
- HARD-PASS: substrate-proposal pipeline finds the cliff-crosser in <= 10 candidate evaluations vs >= 1000 for evolutionary-NAS baseline (NSGA-Net analog) at equivalent top-1 precision.
- HARD-FAIL: substrate-proposal pipeline requires >= 100 candidate evaluations (within 10x of evolutionary baseline) - the "smart retrieval" claim fails because the candidate codebook does not encode useful prior.
- P_deflated: 0.50 (retrieval-over-candidates intrinsically beats random-search at the rate of how-much-the-codebook-encodes-prior; substrate's typed-tensor codebook is information-rich on architectural primitives; cap at 0.50 and deflate 0.0; the prediction is bold but parameterized).

## (d) Cross-thread synthesis

### Four-mechanism substrate-native architecture-proposal stack

The substrate already has the four parts. Today's drill made the assembly explicit:

| Mechanism | NAS lit precedent | Meta-learning lit precedent | Substrate primitive (existing) |
|---|---|---|---|
| (1) Typed candidate space | RNN-controller proposes architectures token-by-token (Zoph-Le 2017; AGNN 2024) | self-referential RNN learns its own weight-change algorithm (Schmidhuber 1993; Backpropamine 2018) | FHRR/GHRR typed-tensor binding of architectural primitives: candidate-architecture = role_binding-op x slot_codebook x value_dimension; codebook of architectural primitives is itself a substrate-stored bundle |
| (2) Scoring oracle | RL reward = trained-and-evaluated accuracy (expensive: per-candidate train) | MetODS meta-rule learns scoring from a meta-distribution | Layer 1 attribution stream gives instant scoring without retraining; spectral observability (free-prob moments per today's free-prob drill) gives codebook-internal score |
| (3) Retrieval over candidates | DARTS uses continuous-relaxation gradient-search (Liu-Simonyan-Yang 2019) | population of progeny algorithms (Evo-PAC Godel Machine, KAUST 2026) | resonator network factorization (Frady-Kent-Olshausen-Sommer 2020): propose = factor unknown-architecture-vector into known-primitive codebooks; this IS substrate-native architecture proposal |
| (4) Verification path | full retrain (RL-NAS) or weight-sharing supernet (ENAS) | Godel machine: formal proof of expected-utility improvement | ablation-based-counterfactual (Dai-Zheng 2024, arxiv 2406.07908) on substrate components; substrate algebraic-inverse IS unbinding = component-ablation; causal-SHAP / interventional-Shapley gives the lift-attribution math |

The four mechanisms compose without engineering new primitives. The substrate's role-filler binding handles (1) and (3); the substrate's runtime attribution stream handles (2) and (4). The CRITICAL new piece is the CANDIDATE CODEBOOK design: it must encode architectural primitives as substrate atoms typed in a way that (a) the substrate retrieval ranks them by Layer 1 attribution prediction, (b) the substrate causal-attribution measures lift-per-component, (c) the resonator factor decoder can compose them into new architectures the codebook does NOT directly contain.

### Bounded-recursion safety: the meta-evaluation-collapse bound

The user's 4 failure modes have a unified operator-theoretic bound. From OpenReview IF0L7HSs3K (2025/26):

> "Unanchored evaluation hierarchies inevitably contract to biased equilibria, either collapsing into trivial consensus or amplifying systematic preferences such as fluency over accuracy ... Meta-evaluation collapse is a recurring structural risk when evaluators are recursively judged without external anchoring."

The operator-theoretic argument: when the evaluator and the evaluated are both elements of the same recursive operator family E_n+1 = phi(E_n), the map phi is a CONTRACTION in the space of evaluation distributions, and contractions have unique fixed points. The fixed point is NOT the ground truth - it is whatever bias the operator family encodes. For LLM-judges this is fluency bias. For SUBSTRATE-PROPOSED-architecture the analogous bias would be "architectures that score well on substrate-internal attribution" which is by construction NOT the same as "architectures that improve capability on external tasks."

The bound: any recursive self-evaluation loop where the GATE is itself proposed by the system being evaluated has a contraction-fixed-point at a biased equilibrium. The fix: the GATE must be fixed at recursion-cycle-0 by a methodology that is NEVER updated by the substrate. Specifically for our Tier-4 gate:

- ALLOWED to be substrate-proposed: candidate architectures, candidate components, proposed pipelines, proposed code, proposed pilots.
- FORBIDDEN to be substrate-proposed: the Layer 1 attribution measurement protocol; the cap_map verdict criteria; the HARD-PASS/HARD-FAIL thresholds; the external held-out test sets; the human-in-the-loop methodology audit cadence.

This is a 1-line architectural invariant ("gate-frozen-at-cycle-0") that bounds all 4 failure modes simultaneously per the operator-theoretic contraction argument.

### Counterfactual architecture: the ABC + algebraic-inverse coincidence

Ablation-based-counterfactuals (Dai et al. 2024, arxiv 2406.07908) was designed for standard NNs and works by training independent components on overlapping data splits then ablating combinations. Substrate has a CLEANER story: the algebraic-inverse (unbinding) IS already a per-component ablation operation. To ask "what if we had used GHRR instead of FHRR for binding?" the substrate does NOT retrain - it just rebinds with the alternate operator and re-measures Layer 1 attribution. The lift differential IS the counterfactual.

This converges with today's operator-algebras drill: the noncommutative-binding subfactor structure gives us algebraic machinery for counterfactual binding-operator substitution that NSGA-Net evolutionary NAS would need 1000+ trained-from-scratch evaluations to estimate.

### Plateau detection: spectral observability on the Layer 1 attribution stream

When to trigger architecture proposal? Three lit-precedent signals:

1. SpectralRadius plateau in thermal-equilibrium region (Nature npj AI 2025 architectural-optimization paper) - directly maps to substrate spectral statistics (today's free-prob 3x DEEP drill gives us Marchenko-Pastur edge as the plateau signature).
2. "When To Grow" risk-aware fitting policy (arxiv 2401.03104, 2024) - cap_map verdict log already provides the fitting risk signal (PARTIAL / INCONCLUSIVE / HARD-FAIL repeated in the same cap_map row across N cycles = empirical plateau).
3. Firefly growing on largest-initial-gradient analog - in substrate, "largest residual after cleanup" is the analog of unfit-gradient and tells us where the candidate codebook needs new primitives.

Pipeline trigger rule: when cap_map row has 3 consecutive verdicts at PARTIAL or worse AND Layer 1 attribution shows < 0.10 lift on the proposed-rescue intervention AND spectral-radius plateau detected on the residual histogram - dispatch substrate-proposed architecture. This is mechanical, not heuristic, and rides on existing logging.

### Connection to today's other drills

- [[research_drill_categorical_ai_discocat_2x_2026-06-11]]: the candidate codebook is exactly a MORPHISM library in the strong-monoidal-functor sense; substrate-proposed-architecture is morphism composition; this is the categorical-AI lineage of the architecture-proposal mechanism.
- [[research_drill_operator_algebras_subfactor_theory_2x_2026-06-11]] (today): the noncommutative-binding subfactor gives us algebraic-inverse for free; counterfactual-architecture is unbind-and-rebind.
- [[research_drill_rmt_beyond_free_probability_2x_2026-06-11]] (today): spectral statistics on the W matrix give the plateau-detection signal independent of cap_map verdict.
- [[research_drill_substrate_algebra_encoding_shared_basis_2x_2026-06-11]] (today): the hybrid two-index + RRF architecture IS an example of a substrate-proposed-architecture mechanism applied to its own retrieval index; the v1 -> v2 redesign is the working prototype of what Tier-4 should look like end-to-end.
- [[substrate_v32_engineered_wrapper_2026-06-11]] (memory, today): the 5-stream engineered wrapper is the FIRST validated substrate-proposed-architecture, where the substrate's own algebra carries the protection layers without core changes - existence proof that the proposal mechanism is meaningful.
- [[drill_pattern_temporal_contextual_not_structural_2026-06-11]] (memory, today): predicts that substrate-proposed architectures that are TEMPORAL or CONTEXTUAL will validate empirically; FIXED-STRUCTURAL proposals will fail. The candidate codebook should be weighted to favor temporal/contextual primitives.

## (e) Substrate-product implications

### Tier-4 gate concrete pipeline

```
0. STANDING GATE (frozen at cycle 0, NEVER substrate-proposed):
   - Layer 1 attribution measurement protocol
   - cap_map verdict criteria
   - external held-out test sets
   - HARD-PASS thresholds per pilot

1. PLATEAU DETECTION (mechanical, rides on existing logging):
   IF cap_map row has 3 consecutive verdicts at PARTIAL or worse
   AND Layer 1 attribution lift < 0.10 on last proposed-rescue intervention
   AND spectral-radius plateau on residual histogram (Marchenko-Pastur edge)
   THEN dispatch substrate-proposed-architecture cycle.

2. PROPOSAL (substrate-native):
   a. Substrate retrieves top-K candidate architectures from typed-tensor candidate codebook via resonator factoring on the "rescue-architecture" query atom.
   b. Substrate ranks candidates by predicted-lift via causal-SHAP / ABC on its own attribution stream.
   c. Substrate emits top-1 candidate as a pre-registered pilot anchor with HARD-PASS / HARD-FAIL thresholds drawn from the FIXED GATE (not substrate-proposed).

3. VALIDATION (1-anchor empirical cell):
   a. Ship anchor to GPU/CPU/local queue per existing exp_dev protocol.
   b. Measure capability lift on the FROZEN external held-out test set.
   c. Gate by FIXED HARD-PASS threshold.

4. INTEGRATE OR REJECT:
   a. IF HARD-PASS: integrate via existing engineered-wrapper protocol (5-stream wrapper paradigm); update cap_map row; archive proposal in candidate codebook with empirical-lift annotation.
   b. IF HARD-FAIL: reject; archive in candidate codebook with negative-result annotation; trigger meta-audit if N consecutive substrate-proposals fail (this is the bounded-recursion safety check).

5. RECURSIVE META-EVALUATION (PERIODIC, gated):
   a. Every K cycles, dispatch META-AUDIT on the proposal mechanism itself.
   b. Audit measures: drift between substrate-internal scoring and FROZEN external gate (Spearman rho >= 0.60 = healthy; <= 0.25 = meta-collapse).
   c. IF drift detected: roll back candidate codebook updates and freeze candidate-codebook for K more cycles while methodology is human-reviewed.
   d. THE META-AUDIT METHODOLOGY ITSELF IS FROZEN AT CYCLE 0 AND NEVER SUBSTRATE-PROPOSED.
```

This pipeline is implementable in Python over the existing substrate primitives in ~200-300 lines (resonator factoring already exists; causal-SHAP-on-substrate-components is ~50 lines per arxiv 2105.00108 propagation algorithm; Spearman / cap_map cross-correlation is ~20 lines).

### Commercial axis: substrate-as-self-redesigning-system

The substrate-product story for Tier-4:

1. CUSTOMER VALUE: substrate identifies its own capability gaps via cap_map plateau detection. No human-engineered architecture search budget. The substrate ships its own pilot proposals.
2. DIFFERENTIATOR vs LLM-only: LLMs propose code (Cursor / Claude Code) but cannot propose THEIR OWN ARCHITECTURE because they have no introspectable component-level attribution stream. Substrate's Layer 1 attribution IS the introspection stream.
3. SAFETY DIFFERENTIATOR vs Godel-machine literature: the "formal proof of expected utility improvement" requirement that makes Godel machines impractical (Schmidhuber 2003; KAUST self-rewriting 2026) is REPLACED by "empirical pilot under FROZEN external gate" - operationally tractable, safety-bounded by operator-theoretic meta-evaluation-collapse argument.
4. REVENUE IMPLICATION: substrate-as-self-redesigning is the path to Tier-5 (multi-substrate ecology) and ultimately the substrate-on-substrate program's terminal capability: a substrate that proposes its own next major architecture (v5.0) and proves the proposal empirically before integrating.

### Engineering implications for v4.0

v4.0 should ship with:
- A TYPED CANDIDATE CODEBOOK of ~30-50 architectural primitives drawn from the cross-domain probe + cap_map history.
- A RESONATOR-FACTOR DECODER on the candidate codebook (already a substrate primitive; just needs to be wired to the proposal API).
- A CAUSAL-SHAP / ABC ATTRIBUTION ENGINE on substrate components (~50 lines + 1 hr smoke).
- A FROZEN GATE registry (yaml file checked into git, requires human-approval-PR to modify).
- A PLATEAU DETECTOR on cap_map + spectral statistics (~30 lines + 1 hr smoke).
- A META-AUDIT cadence (every 10 substrate-proposed cycles, run drift-check; per K=10 default).

Total engineering: 2-4 days for v4.0 substrate-proposed-architecture mechanism MVP. Tier-4 gate is then validated empirically by ARCH-PROPOSE-1 + 2 cross-validation surrogates.

## (f) Citations (verified count)

NAS / RL-controller / evolutionary:
1. Zoph, B., Le, Q.V. (2017). Neural Architecture Search with Reinforcement Learning. ICLR. https://arxiv.org/abs/1611.01578 (referenced via PMC review)
2. Lu, Z., Whalen, I., Boddeti, V., et al. (2019). NSGA-Net: Neural Architecture Search using Multi-Objective Genetic Algorithm. GECCO. https://arxiv.org/abs/1810.03522
3. Scalable RL-NAS (2024). Neural Computing and Applications. https://link.springer.com/article/10.1007/s00521-024-10445-2
4. DQNAS (2023). Neural Architecture Search using Reinforcement Learning. https://arxiv.org/abs/2301.06687
5. Advances in NAS (2024). PMC review. https://pmc.ncbi.nlm.nih.gov/articles/PMC11389615/
6. AGNN: Auto-GNN reinforced conservative search (2024). https://arxiv.org/abs/1909.03184
7. Pareto Dominance-based Novelty Search for NAS (2024). https://arxiv.org/abs/2407.20656
8. NAS via Property Guided Synthesis (2022). https://arxiv.org/abs/2205.03960

Meta-learning / self-modification:
9. Schmidhuber, J. (2003). Goedel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements. https://arxiv.org/abs/cs/0309048
10. Self-Referential Meta Learning (2022). https://arxiv.org/abs/2212.14392
11. Meta-RL with Self-Modifying Networks - MetODS (2022). https://arxiv.org/abs/2202.02363
12. Backpropamine: differentiable neuromodulated plasticity (2018/2020). https://arxiv.org/abs/2002.10585
13. KAUST self-rewriting AI / Evo-PAC Godel Machine (2026). the-decoder.com coverage; arxiv 2606.09663
14. From 0-to-1 to 1-to-N Reproducible Engineering Evidence for MetaAI Recursive Self-Design (2026). https://arxiv.org/abs/2606.09663

Causal attribution / Shapley / ablation-counterfactual:
15. Chen, H., Lundberg, S.M., Lee, S.-I. (2022/2021). Explaining a series of models by propagating Shapley values. Nature Communications / arxiv 2105.00108. https://www.nature.com/articles/s41467-022-31384-3
16. Causal SHAP (2025). https://arxiv.org/abs/2509.00846
17. Practical do-Shapley Explanations (2025). https://arxiv.org/abs/2509.20211
18. Causal Shapley Values (Heskes, 2020). https://arxiv.org/abs/2011.01625
19. Towards Unified Attribution in Explainable AI, Data-Centric AI, and Mechanistic Interpretability (2025). https://arxiv.org/abs/2501.18887
20. Dai, Z., et al. (2024). Ablation Based Counterfactuals. https://arxiv.org/abs/2406.07908
21. Decomposing and Editing Predictions by Modeling Model Computation (2024). https://arxiv.org/abs/2404.11534
22. Optimal ablation for interpretability (2024). https://arxiv.org/abs/2409.09951

Recursive self-improvement / meta-evaluation collapse:
23. Meta-Evaluation Collapse: Who Judges the Judges of Judges? (2025/26). OpenReview IF0L7HSs3K. https://openreview.net/forum?id=IF0L7HSs3K
24. On Meta-Evaluation (2026). https://arxiv.org/abs/2601.14262
25. SIGMA: Scalable Spectral Insights for LLM Model Collapse (2026). https://arxiv.org/abs/2601.03385
26. The Evaluation Trap: Benchmark Design as Theoretical Commitment (2026). https://arxiv.org/abs/2605.14167

VSA / hyperdimensional / binding:
27. LARS-VSA (2024). https://arxiv.org/abs/2405.14436
28. Attention as Binding: VSA Perspective on Transformer Reasoning (2025). https://arxiv.org/abs/2512.14709
29. Hyperdimensional Probe: Decoding LLM Representations via VSA (2025). https://arxiv.org/abs/2509.25045
30. Efficient VSA from Histogram Recovery (2025). https://arxiv.org/abs/2511.01838

Plateau detection / architectural growth:
31. Architectural optimisation in deep neural networks (2025). Nature npj AI. https://www.nature.com/articles/s44387-025-00034-6
32. When To Grow? Fitting Risk-Aware Policy for Layer Growing (2024). https://arxiv.org/abs/2401.03104

Symbolic / neurosymbolic / theorem-prover:
33. Symbolic Regression with a Learned Concept Library (2024). https://www.researchgate.net/publication/384075671
34. Neurosymbolic Program Synthesis (Chaudhuri, 2025). https://www.cs.utexas.edu/~swarat/pubs/ns-handbook-2025.pdf
35. Symbolic Regression via Neural-Guided GP Population Seeding. https://openreview.net/pdf?id=tjwQaOI9tdy

Total verified citations: 35.

## Calibration notes

- Lit precedent dominant on 4 of 4 mechanisms (NAS-RL, meta-learning, causal-SHAP, ablation-counterfactual). The novel synthesis is the ASSEMBLY (substrate-native version of each).
- Operator-theoretic meta-evaluation-collapse bound is recent (2025/26) and directly applicable; this is load-bearing for the bounded-recursion safety claim.
- ARCH-PROPOSE-1 surrogate is designed to be EMPIRICALLY CHEAP (~3-6 hr CPU) and DECISIVE (HARD-PASS / HARD-FAIL well-separated).
- P_deflated values stay <= 0.55 across all predictions; novel-synthesis cap 0.50 enforced on P4 (bounded-recursion safety) and P5 (pipeline efficiency).
- Hard-fail bands explicit on all 5 predictions per [[feedback-lit-scan-calibration-penalty]].
- Adjacent methods NOT dismissed: Godel-machine formal-proof path is explicitly REPLACED by empirical-pilot path (per Schmidhuber 2003 impracticality bound + KAUST 2026 self-rewriting AI's empirical pivot) but the proof-based variant is preserved as a future Tier-5 option for formally-bounded substrate-product surfaces.
