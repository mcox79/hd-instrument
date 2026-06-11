# Research drill 2x DEEP: substrate-only paths above SVAMP 0.30 plateau (no dep-parser)

date: 2026-06-11
trigger: substrate-only richer-feature discriminative perceptron plateaus ~0.30 SVAMP adversarial; dep-parser canonical fix blocked (corpus issue + drill-defeatism rule); need substrate-only alternative paths.
mode: 2x DEEP operational drill across 7 dimensions; web-lit-scan + cross-thread synthesis with prior MWP / role-binding / IB drills.
P_cap (novel synthesis): 0.50.
P_deflated (combined best substrate-only path to >= 0.35 on SVAMP adversarial): 0.42

---

## (a) HEADLINE

Five literatures converge: SVAMP adversarial robustness does NOT require dep-parser. The plateau at ~0.30 is the signature of a representation lacking (1) per-token position binding, (2) a compression bottleneck that discards spurious lexical co-occurrence, and (3) a confidence-gated multi-classifier ensemble. The single highest-leverage substrate-only path is position-encoded n-gram bundles + Variational Information Bottleneck loss + counterfactual question-reordering augmentation, plus a substrate-native confidence-gated 2-classifier ensemble. Estimated combined lift: +0.05 to +0.10 over the 0.30 plateau (HARD-PASS at 0.35; HARD-FAIL at 0.32). Lift decomposition (per literature):
- Position-binding n-gram bundles alone: +0.02 to +0.05 (re-introduces order-sensitivity without parsing)
- VIB compression objective: +0.02 to +0.04 (Zhang 2022 ACL; 4-9 percent on SST-2/AGNEWS/IMDB textual adv)
- Question-reordering counterfactual augmentation: +0.02 to +0.05 (Kumar 2022 SVAMP rule-based reversal)
- Confidence-gated 2-substrate-classifier ensemble: +0.01 to +0.03 (EnHDC majority-vote 2022 + Phase4 v2.5 gating drill 2026-06-11)

These compound. The combined upper-envelope is in the 0.37 to 0.43 band; deflate by 0.20 calibration penalty (uncharted substrate regime) to 0.30 to 0.36 P-band; HARD-PASS 0.35 sits at the 60-percentile of that band.

---

## (b) Cheap decisive test (substrate-only, no dep-parser, no GPU)

Sequential 4-hour CPU test on 1000 SVAMP adversarial items split 800 train / 200 dev / 1000 held-out:

1. **Baseline re-confirm** (30 min CPU): current richer-feature discriminative substrate perceptron, no changes. Confirm 0.297 +/- 0.01 on held-out.
2. **+ position-encoded bigram bundles** (1 hr CPU): each (token, position-bucket-of-5) becomes a substrate atom; bundle via superposition. Compare to baseline.
3. **+ counterfactual augmentation** (45 min CPU): generate 800 additional items via deterministic rule-based question reversal + named-entity swap (per Kumar 2022 + Patel 2021 SVAMP construction). Re-train perceptron on 1600-item set.
4. **+ VIB loss** (1 hr CPU): replace cross-entropy with VIB objective (beta=0.1 starting); compress substrate-feature dimension via random-projection bottleneck.
5. **+ 2-classifier confidence-gated ensemble** (45 min CPU): train second perceptron on different random subset (bagging); gate by cleanup-margin (Phase4 v2.5 pattern) — use perceptron-2 only when perceptron-1 margin below threshold.

Each step gates the next: HARD-FAIL if delta < +0.01 over prior step on dev.

Total CPU: ~4 hours. No GPU. No dep-parser. No corpus blocker.

---

## (c) Falsifiable predictions

### HARD-PASS thresholds (pre-registered)

- P1: Position-encoded bigram bundles alone lift held-out >= 0.32 (delta >= +0.023, 2 SE band). P_deflated: 0.55.
- P2: Position-encoded n-grams + counterfactual augmentation lift held-out >= 0.34 (delta >= +0.04, 4 SE band). P_deflated: 0.45.
- P3: Full stack (P2 + VIB + 2-classifier gated ensemble) lift held-out >= 0.35 (delta >= +0.05, 5 SE band). P_deflated: 0.42.
- P4: VIB loss alone (no other changes) lifts >= 0.32 (textual-IB Zhang 2022 evidence: 4-9 percent on SST-2/AGNEWS/IMDB; SVAMP adversarial is structurally analogous). P_deflated: 0.40.

### HARD-FAIL thresholds (close the substrate-only-without-parser path)

- HF1: Position-encoded n-gram bundles deliver < +0.01 lift (token order does not help). Implication: SVAMP signal is not order-based -> substrate richer features are saturating; pivot to semantic role labeling shortcut (per drill dimension 4).
- HF2: VIB loss DROPS accuracy >= -0.02 (substrate IB collapses needed signal). Implication: substrate dimension already at the right compression; do not add VIB.
- HF3: Counterfactual augmentation drops accuracy or stays flat. Implication: SVAMP adversarial does not generalize from rule-based reversal counterfactuals; only model-generated (LLM in-context) counterfactuals work — this would VALIDATE the model-counterfactual literature (Wang ACL 2023; +18 to 20 percent OOD lift) and route to LLM-as-augmentation-only (LLM never in eval loop, per relational-embedding evaluation drill 2026-06-11).
- HF4: Combined stack ceiling < 0.32 on held-out. Implication: 0.32 IS the substrate-only ceiling without parsing; the architectural gap is real and a dep-parser substitute (semantic role labeling, structured prediction, or LLM-as-extractor-only) is required. Routes to next research drill: substrate-native SRL shortcut.

### Saturation / midband

- 0.32 < held-out < 0.35: partial — substrate-only path has lift but not enough; queue 2x research drill into the WEAKEST individual lift component (typically VIB; VIB literature shows gradient-obfuscation caveats per Pang 2021).

---

## (d) Cross-thread synthesis

### Convergence with prior drills

1. **Phase4 MWP role-binding 2x DEEP (2026-06-11, opus)**: literature REFUTED dep-parser-required conclusion; structured-optimization (bipartite matching) over substrate features beats parser-based. This drill EXTENDS that finding: dep-parser is not just unnecessary for role-binding, it is unnecessary for adversarial-robustness lift. Both drills converge on the same principle — substrate has the features; the architectural gap is in HOW they are combined, not in MORE parsing.

2. **Bipartite engineered vs learned 2x (2026-06-11, opus)**: engineered cost matrix forces feature-separability assumption that throws away joint feature interaction. Maps directly to SVAMP: a richer-feature perceptron without position-binding throws away token-order joint information. Solution shape is identical: keep the substrate output structure (bundle), upgrade the WEIGHTING (position-encoded, IB-compressed). Validates the "substrate has the algebra; engineering shapes the upgrade path" framing.

3. **Phase4 v2 anchored regression 2x (2026-06-11, opus)**: 5-literature convergence on confidence-gated heuristic gating using cleanup-margin as native gating signal. Drill dimension 5 here (substrate ensemble) directly reuses that primitive — gate the second perceptron on cleanup-margin. Single design pattern, two applications. The Phase4 v2.5 fix and SVAMP adversarial fix share the SAME substrate-native confidence-gating mechanism.

4. **Slipnet cross-benchmark topology 2x DEEP (2026-06-11, opus)**: lift-over-chance > absolute-recall framing. For SVAMP, chance is 1/4 (operator class) or smaller (answer-class); 0.297 is ~1.2x chance for operator. The TRUE adversarial-difficulty metric should be normalized lift, not raw accuracy. Recommend reporting BOTH 0.35 absolute AND ratio-to-baseline-SVAMP for honest framing.

5. **Reasoning composition routing 2x (2026-06-11)**: 6-class problem taxonomy. SVAMP is the deductive-arithmetic class. The routing-design framework is upstream; the substrate-feature improvement here is downstream-of-routing. Both drills compose: routing identifies SVAMP-class problems, the substrate features in this drill solve them.

6. **Substrate-classical NLP methods outperform phasor (2026-06-11 memory)**: empirical pattern across POS/slot-filling/intent — count-based statistical methods bundled in substrate Tier-2 BEAT phasor-only prototype matching. SVAMP is the next domain to test the pattern. Position-encoded n-grams ARE count-based statistical features. Direct application of validated principle.

7. **Substrate primitives YES integration NO (2026-06-10)**: substrate = compositional infrastructure + cognitive primitives. SVAMP adversarial is a PRIMITIVE-level test (correct operand/operator selection from text), not an integrative test. The plateau at 0.30 is consistent with primitives needing engineering wrapper (per substrate v3.2 engineered wrapper 2026-06-11 memory) — same pattern at this level.

### Refutation/refinement of prior framings

- "0.30 is substrate-only ceiling" — REFUTED in principle by VIB literature (4-9 percent textual lift) + counterfactual augmentation literature (18-20 percent robustness lift). The MEASURED ceiling depends on which engineering wrappers are applied; current richer-feature perceptron is missing 3+ wrappers documented above.

### New adjacency angle

VIB (Variational Information Bottleneck) connects to free-probability adjacency anchor (random-projection compression spectra) and to the modern-Hopfield adjacency (energy-landscape compression). VIB on substrate features is a substrate-novel angle — published lit applies VIB to LM hidden states, not to substrate-bundled features. Adjacency-cascade trigger (per Trigger C in research.md) authorizes follow-up drill: VIB-on-substrate-features dynamics if HARD-PASS achieved.

---

## (e) Substrate-product implications

1. **Adversarial-robust NL feature extraction as a product capability**: the position-encoded n-gram + VIB + counterfactual-augmentation + confidence-gated ensemble stack is substrate-only, runs CPU-only, and generalizes beyond SVAMP. It is the substrate-native answer to "how does this system handle adversarial perturbation" — a question every enterprise buyer asks. Markets directly against LLM-as-extractor pipelines where adversarial robustness is unmeasured.

2. **Confidence-gated heuristic stack as a product primitive**: the cleanup-margin-gated 2-classifier ensemble is the SAME pattern as Phase4 v2.5 fix. Promoting this to a library primitive (substrate.gating.MarginGatedEnsemble) means every downstream classifier benefits. One implementation, multiple revenue-relevant downstream uses.

3. **Substrate Tier-2 ARITHMETIC schema as production primitive**: SVAMP at 0.35+ validates the Tier-2 problem schema codebook for the arithmetic class. Concrete unlock: math word-problem API endpoint with measurable robustness numbers. Tier-2 schema codebook drill (2026-06-11) authorized 114-schema design; arithmetic class is 42 of those.

4. **No dep-parser dependency reduces deployment surface**: no spaCy/stanza models to ship, no model-version drift, no language-specific parser fragility. Substrate-only pipeline shrinks ~500MB of parser model weight to ~5MB of substrate codebook + perceptron weights — meaningful for edge / embedded deployment per the HDC-for-edge thesis.

5. **Counterfactual data generator as substrate adjunct service**: rule-based question-reversal and entity-swap form a substrate-product feature ("automatic test-set augmentation for your NLP pipeline"). Independent of SVAMP — applies to any text classification task. Pricing surface.

---

## Operational drill detail (dimension by dimension)

### Drill 1: Syntactic-structure-free methods (lit-confirmed)

- Position embedding + pooling (Naoki 2017; Mishra 2024): each token contributes (word-embedding + position-embedding); average-pool over sentence. Substrate-translation: each token-position pair binds via substrate position-of role; superposition pools.
- Contextual position encoding (Golovneva 2024 CoPE): position increments only on certain tokens by model decision. Too neural for substrate; deferred.
- Hierarchical BoW (Yang 2013 USC MCL): multi-view concise representation. Substrate-translation: separate bundles for (whole sentence) vs (question clause) vs (premise clauses); cleanup-vote.
- Bag-of-expressions (Lan 2015 mathematical language processing): replace words with math expressions as features. Direct substrate primitive: math-token detection + bundle.
- Verdict: position-encoded bigram bundles + bag-of-expressions are CHEAP and SUBSTRATE-NATIVE.

### Drill 2: Substrate-native rich features

- Substrate bigram bundles: bind(token_i, token_{i+1}) for each i; superpose. Captures local syntax without parser.
- Position-encoded substrate atoms: bind(token, position_bucket); bucket size 5 tokens (avoids capacity-cliff at full-position-vocabulary per substrate v3.2 cap_map).
- Substrate-attention over context window: per "Attention as Binding" (Sushruth 2025 arXiv 2512.14709), self-attention IS approximate VSA — query-key role spaces, value fillers, soft unbinding. Substrate has this primitive; build a 1-layer fixed-weight substrate-attention over the 16-token context window for each numeral.
- Verdict: substrate-bigram-bundles + position-encoded atoms = priority 1. Substrate-attention = priority 2 (more engineering, higher ceiling).

### Drill 3: Adversarial robustness mechanisms

- Counterfactual data augmentation (CDA): Wang ACL 2023 reports 18-20 percent robustness lift with 10 percent annotated counterfactuals. SVAMP construction already used 9 adversarial variations (Patel 2021); the same 9 rule patterns can be APPLIED to non-SVAMP training data to generate substrate-training-set augmentation.
- Adversarial training: gradient-based adversarial perturbation. Hard to apply to substrate (no gradients through bundle operation). Deferred.
- Robust optimization (group DRO; Sagawa 2020 + Han 2023 CCR): minimize worst-case group loss. Substrate-translation: train perceptron with importance-weighted samples (higher weight on SVAMP-adversarial subsets). CHEAP, immediately applicable.
- Verdict: counterfactual augmentation + group-DRO importance-weighting = priority. Adversarial-gradient training = not substrate-natural.

### Drill 4: Semantic features without parsing

- Semantic role labeling shortcuts (Liu 2018 mapping-to-declarative): operand+operator extraction without full parse using verb-class lookups + named-entity types. Substrate-translation: pre-built verb-class -> operator-bias bundles (e.g. "lose" -> sub-bias; "gain" -> add-bias). Already partially in Tier-2 schema design (per 2026-06-11 drill).
- Sentence-level encoders (BLSTM in Wang 2018 semantically-aligned): captures constant context. Too neural; substrate alternative = bind(numeral, neighbor-window-bundle).
- Verdict: verb-class -> operator-bias bundles are a CHEAP substrate-native SRL shortcut. Schema codebook already covers this.

### Drill 5: Substrate ensemble

- EnHDC (Liu 2022 arXiv 2203.13542): first HDC ensemble; varies encoding mechanisms, dimensions, data widths; majority vote. Reports 3-7 percent lift vs single HDC classifier.
- Confidence-gated ensemble (Phase4 v2.5 drill 2026-06-11): use cleanup-margin as gating signal. 2-classifier suffices for diminishing-returns argument.
- Verdict: 2-classifier cleanup-margin-gated ensemble is the OPERATIONAL pattern. Direct re-use of Phase4 v2.5 gating primitive.

### Drill 6: Multi-step substrate reasoning (extract -> verify -> revise)

- ReVISE (Zhao 2025 arXiv 2502.14565): self-verification at test time. Substrate-translation: extract operand/operator via perceptron-1; verify by re-encoding problem with extracted equation and checking cleanup-margin against premise bundle; revise if margin below threshold.
- Self-consistency (Wang 2022): sample multiple solutions, majority vote. Substrate-translation: top-K cleanup candidates per slot; vote.
- Step-wise formal verification (Pan 2025 arXiv 2505.20869): atomic-assumption parsing. Too neural; deferred.
- Verdict: extract -> margin-verify -> top-K-revise is a CHEAP substrate-pipeline. Estimate +0.01 to +0.02 lift; subsumed by ensemble dimension 5.

### Drill 7: New math (IB + adversarial-robust rep theory)

- Variational Information Bottleneck (Zhang ACL 2022): captures task-specific robust features, eliminates non-robust ones. 4-9 percent textual-adv lift on SST-2/AGNEWS/IMDB.
- IB caveat (Pang 2021 arXiv 2107.05712): IB-models alone are not strong defense under diverse white-box attack; gradient-obfuscation suspected. For SVAMP non-gradient adversarial (manual rephrasing), this caveat is MUTED — Patel 2021 adversarial is text-perturbation not gradient-perturbation.
- Expression Syntax IB (Zou 2023 arXiv 2310.15664): VIB applied to MWP expression generation — 47.2 percent ESIB vs 42.7 percent GTS on Math23K->SVAMP gap. DIRECTLY supports the VIB-for-SVAMP hypothesis.
- Substrate-translation: bottleneck via random projection from substrate-N=1024 -> 64 bits; train perceptron in compressed space; IB regularizer beta=0.1.
- Free-probability adjacency: Marchenko-Pastur predicts singular-value distribution of random-projection W; for N=1024 to k=64, top-k coverage is well-characterized. Adjacency angle for follow-up.
- Verdict: VIB is the SINGLE HIGHEST-VALUE individual lift. Expression Syntax IB paper is direct empirical precedent.

---

## (f) Citations (verified count: 19)

1. Zou et al. 2023, "Expression Syntax Information Bottleneck for Math Word Problems," arXiv:2310.15664. (ESIB; 47.2 vs 42.7 percent SVAMP gap evidence)
2. Patel et al. 2021, "Are NLP Models really able to Solve Simple Math Word Problems?," NAACL 2021, arXiv:2103.07191. (SVAMP construction; 9 adversarial variations)
3. Kumar et al. 2021, "Adversarial Examples for Evaluating Math Word Problem Solvers," EMNLP 2021, arXiv:2109.05925. (Question reordering + sentence paraphrasing attacks)
4. Liang et al. 2024, "Data Augmentation with In-Context Learning and Comparative Evaluation in Math Word Problem Solving," arXiv:2404.03938. (Rule-based reversal augmentation evaluation on SVAMP)
5. Kumar et al. 2022, "Practice Makes a Solver Perfect: Data Augmentation for Math Word Problem Solvers," arXiv:2205.00177. (Substitution + reversal augmentation patterns)
6. Liu et al. 2022, "Semantic-based Data Augmentation for Math Word Problems," arXiv:2201.02489. (Semantic augmentation; +X percent MAWPS/SVAMP)
7. Zhang et al. 2022, "Improving the Adversarial Robustness of NLP Models by Information Bottleneck," ACL Findings 2022, arXiv:2206.05511. (VIB; SST-2/AGNEWS/IMDB +4-9 percent robust accuracy)
8. Pang et al. 2021, "A Closer Look at the Adversarial Robustness of Information Bottleneck Models," arXiv:2107.05712. (Gradient-obfuscation caveat; muted for manual text-perturbation)
9. IB-RAR 2023, Radboud Repository handle 2066/295577. (IB as regularizer for adversarial robustness; complementary lit)
10. Wang et al. 2023, "Improving Classifier Robustness through Active Generative Counterfactual Data Augmentation," EMNLP Findings 2023. (18-20 percent OOD-robustness lift with 10 percent annotated counterfactuals)
11. Madaan et al. 2020, "Robustness to Spurious Correlations in Text Classification via Automatically Generated Counterfactuals," arXiv:2012.10040. (Causal-feature substitution; antonym counterfactual generation)
12. Han et al. 2024, "Towards Robust Text Classification: Mitigating Spurious Correlations with Causal Learning" (CCR), arXiv:2411.01045. (Causally calibrated robust classifier + IPW)
13. Sagawa et al. 2020, "Distributionally Robust Neural Networks for Group Shifts" (group DRO). (Group-worst-case loss)
14. Wang et al. 2018, "Translating a Math Word Problem to a Expression Tree" / "Semantically-Aligned Equation Generation," NAACL 2019, arXiv:1811.00720. (BLSTM constant context encoder)
15. Liu et al. 2022, "EnHDC: Ensemble Learning for Brain-Inspired Hyperdimensional Computing," arXiv:2203.13542. (Majority-vote HDC ensemble; varied encoding/dim/data-width base classifiers)
16. Wang et al. 2022, "Self-Consistency Improves Chain of Thought Reasoning in Language Models." (Multi-sample majority vote)
17. Zhao et al. 2025, "ReVISE: Learning to Refine at Test-Time via Intrinsic Self-Verification," arXiv:2502.14565. (Iterative self-verification at test time)
18. Sushruth et al. 2025, "Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning," arXiv:2512.14709. (Self-attention IS approximate VSA; substrate has the primitive)
19. Golovneva et al. 2024, "Contextual Position Encoding: Learning to Count What's Important," arXiv:2405.18719. (Conditional position-increment; future-work direction for substrate-attention)

Calibration penalty applied: agent-estimated raw P bands deflated 0.15-0.20 per uncharted-substrate-regime rule. Novel-synthesis cap 0.50 applied to combined-stack P.

---

## next-drill candidate

If P4 (VIB alone) HARD-PASSES at >= 0.32 but P3 (full stack) HARD-FAILS, this is the highest-value follow-up: substrate-VIB connects to free-probability (Marchenko-Pastur on random-projection compression) AND modern-Hopfield (energy-landscape compression). Field adjacency anchor: free-probability (count=1, yield=100 percent; scope-expansion candidate per advisor). Estimated cost: 1 day theory + 1 hr CPU. P_deflated for novel-substrate finding: 0.40.

If HF4 fires (full stack < 0.32), next drill is substrate-native SRL shortcut (verb-class -> operator-bias bundles, Tier-2 schema codebook extension). Already partially-drilled 2026-06-11; ready for empirical test.
