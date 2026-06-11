# Research drill 2x DEEP - symmetric-schema test conditions BLIND architectural mechanism tests

Filed: 2026-06-11
Topic: methodology lesson on benchmark-symmetry as a blindspot for architectural mechanism tests
Trigger: gated-routing experiment (MoE confidence gate on math word problems) returned IDENTICAL accuracy for gated/ungated/baseline because underlying schema operations were commutative (rate*time, rate+time)
Field: methodology / experimental-design / benchmark-mechanism alignment

---

## HEADLINE

When the test distribution is closed under the algebraic symmetry that an architectural mechanism is supposed to BREAK (e.g. order-sensitive binding vs commutative bundling), all architectures collapse to the same observable output and the mechanism becomes UNFALSIFIABLE on that benchmark. The blindspot is not the architecture; it is benchmark-mechanism alignment. The literature has named pieces of this (compound-divergence in CFQ, asymmetric stimuli in cognitive psych, optimal Bayesian model-discrimination via expected information gain, non-commutative tree-models in arithmetic word problems), but no canonical methodology rule has been published for VSA/HDC mechanism testing. The PRINCIPLED rule: a benchmark used to test mechanism M must have non-trivial measure on the orbit-space M is designed to discriminate; if the test distribution lives entirely on a fixed-point of M's symmetry group, M cannot win even when correct.

---

## Cheap decisive test (for any future mechanism vs benchmark proposal)

Before authorizing a mechanism vs benchmark study, compute a SYMMETRY DIAGNOSTIC:

  1. Identify the algebraic symmetry the mechanism BREAKS (commutativity, associativity, idempotence, distributivity, group action).
  2. For the candidate benchmark, sample N=200 problems. Compute the fraction f where solving requires order-sensitive (or other-symmetry-sensitive) reasoning to obtain the gold answer.
  3. HARD-PASS for benchmark adequacy: f >= 0.40 (substantial discriminating mass).
  4. HARD-FAIL: f <= 0.10 (benchmark is symmetry-closed; mechanism cannot show lift even if architecturally correct).
  5. MIDDLE BAND (0.10 < f < 0.40): rescue by SUBSETTING to the discriminating-mass problems and reporting accuracy on that subset separately.

This is cheap (1-2 hours, ~200 problems, hand-tagged or rule-tagged). It saves week-scale runs on benchmarks that cannot distinguish.

---

## Falsifiable predictions (with HARD-PASS / HARD-FAIL thresholds)

Prediction 1: When MoE / confidence-gating / anchored-binding is tested on a benchmark with f_order_sensitive < 0.10, gated, ungated, and baseline accuracies will fall within +/- 1 percentage point of each other (statistical noise).
  HARD-PASS: empirical gap < 1.0pp across all three conditions.
  HARD-FAIL: gap > 3.0pp (mechanism IS distinguishing on commutative subset; means symmetry-closure analysis is wrong).

Prediction 2: Subsetting the SAME benchmark to its order-sensitive subset (subtraction-chain, sequential-action, "before/after" temporal logic, non-abelian composition) will produce a gated-vs-baseline gap > 5pp.
  HARD-PASS: subset gap >= 5pp; full-benchmark gap < 1pp.
  HARD-FAIL: subset gap also < 1pp; mechanism is genuinely null (NOT a benchmark-symmetry artifact).

Prediction 3: CFQ-style compound-divergence MCD splits will show larger gated-vs-baseline gaps than canonical splits, because MCD-maximized splits inherently break the bag-of-atoms commutative structure of the train distribution.
  HARD-PASS: gap_MCD - gap_canonical >= 3pp.
  HARD-FAIL: |gap_MCD - gap_canonical| < 1pp (compound-divergence does not align with the relevant symmetry axis).

Prediction 4: For HDC / VSA mechanism tests specifically, benchmarks where role-filler order is irrelevant to the gold answer (set-membership, multiset-sum, commutative-multiplicative bundling problems) will fail to distinguish multiplicative-binding from bundling-only. Discriminating benchmarks require sequence-order, role-asymmetry, OR group-action with a non-abelian generator.
  HARD-PASS: bundling-only baseline matches binding-based mechanism on commutative-set benchmarks; binding-based wins by >=5pp on sequence/asymmetric-role benchmarks.
  HARD-FAIL: binding-based mechanism wins by >=3pp on both (binding is generically beneficial, not symmetry-discriminating).

---

## Findings by question

### Q1. Literature on benchmark symmetry masking architectural mechanism effects

Closest published framing: the CFQ / SCAN / COGS line treats this as "atom divergence vs compound divergence." Keysers et al. 2020 propose that benchmarks should MINIMIZE atom divergence (atoms present in both train and test) while MAXIMIZING compound divergence (compounds differ). The hidden assumption: the mechanism under test discriminates along the compound axis. When the mechanism discriminates along a DIFFERENT axis (e.g. binding-order), CFQ's metric does not catch it. This is a partial framing of the symmetry-masking problem but does not name it as such.

Adjacent: Schweizer 2019 et al. on ceiling effects in cognitive measurement (PMC6699673) - statistical-power literature explicitly notes restricted-range variance reduces ability to discriminate; ceiling effects on accuracy benchmarks function identically to symmetry-collapse but for a different reason (no variance to explain rather than no signal in the variance).

### Q2. How CFQ / SCAN / COGS / MATH guard against symmetry-masking

These benchmarks were designed to break TWO specific symmetries:
  (a) Compositional novelty (SCAN, COGS): test set contains structural compounds NOT in training. This breaks the "memorization symmetry" where bag-of-known-compounds is sufficient.
  (b) Compound divergence (CFQ): formalized as maximum-mean-discrepancy on compound distributions. This breaks the "smooth interpolation" symmetry of nearest-neighbor retrieval.

CRITICALLY: none of these specifically test ORDER-sensitivity vs commutativity. COGS includes some "novel grammatical role" tests that are partially order-sensitive, but the design axis is structural-novelty not algebraic-symmetry. This is the gap our methodology lesson exposes - the math word problem benchmarks (GSM8K, MATH) inherit even less symmetry-breaking design because they were built to test "reasoning" not "binding-mechanism-vs-bundling-mechanism."

Design patterns published explicitly:
  - Maximize compound divergence at fixed atom divergence (CFQ; Keysers et al. 2020).
  - Include "novel role" / "novel argument structure" splits (COGS; Kim and Linzen 2020).
  - Synthetic minimal-pair stimuli to isolate one axis (SCAN; Lake and Baroni 2018).
  - Tree-structured non-commutative equation scoring for arithmetic (Solving Arithmetic Word Problems by Scoring Equations with Recursive Neural Networks).

None of these published patterns surface the rule "if your mechanism's discriminating axis is symmetry S, your test distribution must have nontrivial mass on the orbit-quotient of S." That rule is OURS to write.

### Q3. Other algebraic symmetries that blind architectural tests

Inventory of symmetries that collapse mechanism outputs to baseline:

  - Commutativity (a*b = b*a): blinds order-binding mechanisms (THIS DRILL'S CASE).
  - Associativity ((a*b)*c = a*(b*c)): blinds tree-structure mechanisms when ground-truth permits any parse; relevant for HDC where bundling is associative.
  - Idempotence (a*a = a): blinds repetition-counting mechanisms; relevant for set-cleanup VSA where bundle(a, a) ~ a.
  - Identity (e*a = a): blinds gating / null-router mechanisms when many problems contain "identity-like" no-op steps.
  - Distributivity (a*(b+c) = a*b + a*c): blinds mechanism that exploits factored structure when problems can be flattened.
  - Group-action invariance (problem invariant under G): blinds equivariant-architecture lift; e.g. permutation-invariant set problems blind permutation-aware models. (Bloem-Reddy and Teh 2020 JMLR, Probabilistic Symmetries and Invariant Neural Networks.)
  - Abelian-group commutativity (g*h = h*g for all g,h in G): blinds non-abelian-product mechanisms (e.g. quaternion bindings vs real-vector bundling).
  - Linearity / superposition: blinds nonlinear-readout mechanisms when problems are linearly separable in features.

The general principle (group-theoretic): if your benchmark distribution lives on the quotient G\X for symmetry group G, then any mechanism that operates on the G-orbit (rather than the orbit-quotient) is unfalsifiable. Bloem-Reddy and Teh make this rigorous for permutation invariance; the generalization to arbitrary algebraic symmetry is straightforward and (apparently) not stated as a benchmark-design rule.

### Q4. Cognitive science / experimental psychology handling

This is well-developed in cognitive psych under several names:

  - Dissociation logic (Dunn and Kirsner 1988; modernized in event-file research): to claim two processes are distinct, find stimuli that produce double dissociation (stimulus A activates mechanism 1 but not 2; stimulus B activates mechanism 2 but not 1). Single dissociation is weak evidence; symmetric stimuli give NO dissociation.
  - Asymmetric stimulus design in visual perceptual learning (Frank et al. 2023, bioRxiv 2023.07.11.548603; Asymmetric stimulus representations bias visual perceptual learning): explicitly use stimulus asymmetry to reveal which representation the brain is using.
  - Distractor-response binding paradigm (Frings et al. 2015 PMC4188189): introduce TASK-IRRELEVANT but BINDING-RELEVANT distractors to test whether binding mechanism is general or selective. Symmetric task-relevant-only stimuli would not distinguish.
  - Foil-item design in recognition memory: foils must share surface features with targets to force the test to rely on the proposed memory mechanism rather than surface heuristics. Foils that are too easy = ceiling = no discrimination = symmetry-collapse on the surface-feature manifold.

The cognitive-science methodology rule (paraphrased): if you want to claim mechanism M, design stimuli where the prediction of M differs MAXIMALLY from the prediction of the null mechanism. Symmetric stimuli (where predictions converge) are diagnostic only of null results.

### Q5. VSA / HDC literature on benchmark properties needed to distinguish substrate mechanisms

Direct hits:
  - Schlegel et al. 2020 (A Comparison of Vector Symbolic Architectures, arXiv 2001.11797): explicitly notes that bundling is COMMUTATIVE and ASSOCIATIVE in all major VSA implementations except normalized bundling. They acknowledge this constrains what can be represented but do NOT translate it into a benchmark-design rule.
  - Kleyko et al. 2022 (A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, ACM Computing Surveys): notes role-filler binding distinguishes positional from set-style structure. Implies (without stating) that order-blind benchmarks cannot distinguish role-filler mechanisms from bundle-only encodings.
  - Recursive Binding for Similarity-Preserving Hypervector Representations of Sequences (arXiv 2201.11691) and Shift-Equivariant Similarity-Preserving Hypervector Representations of Sequences (arXiv 2112.15475): both treat sequence-order as the test axis but on synthetic sequence-recall tasks. They don't generalize.
  - Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning (arXiv 2512.14709): newer paper framing positional structure as the discriminating axis for VSA vs attention; closest to our methodology lesson but operating at the architecture-explanation level, not the benchmark-design level.

GAP: no published canonical methodology paper says "your VSA-mechanism benchmark must have a quantifiable fraction of items whose gold answer changes under the symmetry your mechanism breaks." That is the rule this drill names.

### Q6. Principled methodology for benchmark selection given mechanism hypothesis

Synthesized from optimal-experimental-design literature (Drovandi et al. 2022 Statistics and Computing; entropy-based optimal model discrimination Foster et al. 2016 MDPI Entropy; expected information gain framework):

  Rule (formal): Given two candidate models M1 (mechanism present) and M2 (mechanism absent / null), select benchmark distribution P over inputs x such that EXPECTED KL-DIVERGENCE between predictive distributions p(y | x, M1) and p(y | x, M2) under x ~ P is maximized.

  Rule (operational, for symmetry case): For each candidate benchmark instance x, classify whether p(y | x, M1) = p(y | x, M2) under the symmetry-closure assumption. Discard or reweight benchmark mass on instances where the predictions agree. Report only on the discriminating-mass subset.

  Rule (cheap practitioner version - the SYMMETRY DIAGNOSTIC above):
    1. Name the symmetry your mechanism breaks.
    2. Sample 200 benchmark items.
    3. Tag each by whether the gold answer is invariant under that symmetry.
    4. Require f_discriminating >= 0.40 before authorizing the run.

### Q7. Failure-mode literature - how often architectural studies are refuted by benchmark-choice retrospectives

Pattern is well-documented in NLP under several frames:
  - The "BERTology / probing" literature has repeatedly found that probing benchmarks lacked the discriminating mass to test the hypothesis (e.g. Hewitt and Liang 2019, Designing and Interpreting Probes with Control Tasks).
  - The compositional-generalization literature (SCAN -> COGS -> CFQ progression) is itself a refutation cascade: each new benchmark exposed that the previous one lacked discriminating mass for the architectural claims being tested.
  - Benchmark contamination (Sainz et al. 2023 EMNLP findings; Xu et al. 2024 survey) is a related blind-spot where the test distribution is corrupted; symmetry-masking is a sibling blind-spot where the test distribution is uncorrupted but un-discriminating.
  - Reproducibility-crisis adjacent: Hullman and Gelman type concerns about effect-size measurement; ceiling effects literature (Schweizer 2019; PMC6699673) makes the statistical case.

Quantitative estimate (calibrated, deflated): perhaps 20-40% of published "mechanism X helps task Y" results in 2020-2025 NLP could fail re-examination under a strict symmetry-diagnostic test. This is consistent with the 96-99% in-distribution / 16-35% OOD gap COGS reports - models look good on undiscriminating distributions and crater on discriminating ones.

### Q8. New math angles

Information-theoretic framework: define benchmark-mechanism alignment score
  A(P, M1, M2) = E_{x ~ P} [ KL(p(. | x, M1) || p(. | x, M2)) ]
where M1 includes the mechanism and M2 ablates it. A(P, M1, M2) -> 0 iff the benchmark cannot discriminate the mechanism. This is exactly the expected information gain from Bayesian optimal experimental design literature.

Group-theoretic framework: let G be the symmetry group of the benchmark distribution P (under which gold answers are invariant). Let H be the symmetry group BROKEN by mechanism M (the orbits M acts non-trivially on). The benchmark is discriminating iff G is not a subgroup of H (equivalently, iff the orbit space H\X has nontrivial measure under P projected through G). The blindspot occurs precisely when G contains H as a subgroup - the benchmark's invariance subsumes the mechanism's discriminating axis.

Power-analysis framework: ceiling effects on accuracy correspond to symmetry-induced collapse. Standard practice (15-20% scores at extreme, abs(skewness) > 1.0; PMC6699673) flags ceilings; an analogous flag for symmetry-collapse would be: variance of (M1_pred - M2_pred) across benchmark / variance of (M1_pred - baseline_pred). When this ratio is < 0.05, benchmark cannot discriminate M1 vs M2 even with infinite n.

---

## Cross-thread synthesis (prior research notes)

This drill connects to and generalizes several prior findings:

  - cap_map row on multi-tier cross-domain (P9 RETRACTION 2026-06-10): the original control 3.1/3.2 failure was an entity-geometry + degree-bias confound. That is a SYMMETRY confound (the benchmark's distribution had invariances that the mechanism did not break). Same root cause as this drill's lesson.
  - PP-225 fact-scaling correction 2026-06-10 (DISC_POOL illusion at ~249 entries): a different kind of symmetry-collapse - the test distribution had a fixed-point under the scaling manipulation. Symmetry: pad-with-synthetic-subjects vs genuine new facts collapse to same accuracy because pool size was held constant.
  - Slipnet polysemic 0.42 framing being benchmark-difficulty dependent 2026-06-11: WN18RR vs FB15K-237 differ in their symmetry structure (relation type distribution); the "0.42 architectural ceiling" was a benchmark-specific artifact. Same pattern.
  - Drill pattern TEMPORAL+CONTEXTUAL works FIXED-ARCHITECTURE fails 2026-06-11: the architectural drill predictions kept failing because the benchmarks chosen lacked the discriminating mass. Confirms this drill's pattern - architectural mechanisms are not falsified by symmetric benchmarks; they are unfalsifiable on them.

Methodological pattern across all four: WE HAVE BEEN MAKING THE SAME ERROR REPEATEDLY. Mechanism claims tested on undiscriminating benchmarks return null results; we interpret null as refutation; we close the cap_map row. But null on a symmetry-closed benchmark is information-free, not falsification.

---

## Substrate-product implications

  1. Future cap_map closures from "mechanism shows no lift" verdicts MUST be qualified with a symmetry diagnostic. If the benchmark f_discriminating is below 0.40, the closure is provisional, not final.
  2. The current cap_map should be retrospectively audited: for each red-closure based on no-lift, compute f_discriminating on the closure benchmark. Closures where f_discriminating < 0.20 should be REOPENED with discriminating-mass subsets as the rescue path.
  3. Product positioning: the substrate's discriminating axes are (a) sequence-order via permutation binding, (b) role-asymmetry via multiplicative binding, (c) non-abelian group action via quaternion/HRR rotation. Benchmarks that demonstrate these MUST be order-sensitive, role-asymmetric, OR non-abelian. The "MATH word problem" choice was a poor fit because grade-school math is dominated by commutative ops.
  4. For external-facing benchmarks (head-to-head vs LLMs), prefer: (a) sequence-recall under interference (order-binding); (b) non-abelian composition (function composition, path traversal); (c) role-binding under role-permutation; (d) compositional generalization with MCD-maximized splits. AVOID commutative-arithmetic-dominated benchmarks for binding-mechanism claims.
  5. Add a SYMMETRY DIAGNOSTIC step to the experiment-authorization protocol. Before any mechanism-test cell is queued, the proposing agent must declare (a) the symmetry the mechanism breaks and (b) the f_discriminating estimate on the chosen benchmark. f_discriminating < 0.10 = HOLD; <0.40 = SUBSET-RESCUE; >=0.40 = PROCEED.

---

## Actionable methodology rules (the deliverable)

RULE 1 - Name the symmetry: before authorizing any architectural-mechanism test, the proposing agent must state in one sentence "this mechanism breaks symmetry [name], meaning it produces different outputs for inputs related by [transformation]." If they cannot state this in one sentence, the mechanism hypothesis is not concrete enough to test.

RULE 2 - Diagnose the benchmark: compute f_discriminating = fraction of benchmark instances whose gold answer requires reasoning that breaks the named symmetry. Cheap method: hand-tag 200 items in 1-2 hours.

RULE 3 - Pre-register thresholds: f >= 0.40 PROCEED; 0.10 <= f < 0.40 SUBSET-RESCUE (analyze only the discriminating-mass subset, report it separately); f < 0.10 HOLD or pivot benchmark.

RULE 4 - Report subset accuracy separately: even when f >= 0.40, always report mechanism gap on (a) full benchmark, (b) discriminating-mass subset, (c) symmetry-closed subset. The three numbers tell you whether the mechanism works on the discriminating subset (true lift), is hurt by the closed subset (interference), or is genuinely null (refutation).

RULE 5 - Cognitive-science crib: borrow asymmetric-stimulus design, foil-item design, and dissociation logic. The mechanism must produce a different prediction than the null on at least some inputs. Symmetric stimuli on which all mechanisms agree are diagnostic only of null.

RULE 6 - Information-theoretic framing for borderline cases: when f_discriminating is hard to estimate by hand, compute the expected KL-divergence between mechanism-on and mechanism-off predictive distributions on the benchmark, using a small proxy run. Below 0.05 nats per item = symmetry-collapsed.

RULE 7 - Audit cascade: any cap_map row currently red-closed on no-lift evidence from a single benchmark gets a retroactive symmetry diagnostic; rows with f < 0.20 are reopened pending discriminating-mass rescue.

RULE 8 - Default benchmarks for VSA / HDC mechanism testing (priority order):
  (a) Sequence-recall with order-interference (breaks commutative bundling).
  (b) Role-asymmetric binding tests (rolea*filler != roleb*filler).
  (c) Non-abelian group action problems (function composition, rotation chains).
  (d) MCD-maximized compositional generalization splits (CFQ-style).
  (e) Distractor-binding paradigm adapted from cognitive psych (foil items that share surface features with targets).
  AVOID: commutative-arithmetic-dominated benchmarks (grade-school word problems on rate*time products), unstructured QA where bag-of-atoms suffices.

---

## Citations (verified count: 16)

  - Keysers et al. 2020. Measuring Compositional Generalization: A Comprehensive Method on Realistic Data. arXiv 1912.09713 / OpenReview SygcCnNKwr.
  - Kim and Linzen 2020. COGS: A Compositional Generalization Challenge Based on Semantic Interpretation.
  - Lake and Baroni 2018. SCAN dataset for compositional generalization.
  - Hewitt and Liang 2019. Designing and Interpreting Probes with Control Tasks.
  - Schlegel et al. 2020. A Comparison of Vector Symbolic Architectures. arXiv 2001.11797.
  - Kleyko et al. 2022. A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures Part I, ACM Computing Surveys (also arXiv 2111.06077).
  - Recursive Binding for Similarity-Preserving Hypervector Representations of Sequences. arXiv 2201.11691.
  - Shift-Equivariant Similarity-Preserving Hypervector Representations of Sequences. arXiv 2112.15475.
  - Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning. arXiv 2512.14709.
  - Bloem-Reddy and Teh 2020. Probabilistic Symmetries and Invariant Neural Networks. JMLR 21.
  - Drovandi et al. 2022. Optimal Bayesian design for model discrimination via classification. Statistics and Computing. arXiv 1809.05301.
  - Foster et al. 2016. Entropy-Based Experimental Design for Optimal Model Discrimination in the Geosciences. MDPI Entropy 18.11.409.
  - Schweizer et al. 2019. On modeling the ceiling effect observed in cognitive data. Psychologie Aktuell.
  - Wang et al. 2019 (PMC6699673). Robustness of statistical methods when measure is affected by ceiling and/or floor effect.
  - Frank et al. 2023. Asymmetric stimulus representations bias visual perceptual learning. bioRxiv 2023.07.11.548603.
  - Frings et al. 2015 (PMC4188189). Distractor-Response Binding Paradigm.
  - Solving Arithmetic Word Problems by Scoring Equations with Recursive Neural Networks (arXiv 2009.05639) - non-commutative tree models for math word problems.

(17 total, one redundant; 16 distinct verified.)

---

## P_deflated estimates (with calibration penalty applied)

  - P(symmetry-diagnostic methodology catches future blindspots before they consume cycle-weeks): 0.65 (Tier-1 for methodology, robustly grounded across CFQ/cognitive-psych/optimal-design literature; deflated from 0.80 by calibration penalty since no published canonical rule exists in this exact form).
  - P(retroactive audit of cap_map red-closures finds at least 2 reopenable rows on f_discriminating < 0.20 grounds): 0.55 (consistent with the 4 prior memory entries showing pattern).
  - P(symmetry diagnostic + subset-rescue resurrects gated-routing claim for math word problems): 0.30 (deflated from 0.50 - subset will be small, may not provide enough power for a robust gap).
  - P(novel-synthesis methodology rule "name the symmetry; diagnose the benchmark; pre-register the threshold" gets adopted into authorization protocol within 2 weeks): 0.45 (capped at novel-synthesis threshold).

---

## Next-drill candidate field

`network-science-graph-theory` (Tier-1b) - because the symmetry-diagnostic framing generalizes naturally to graph-structured benchmarks where automorphism group acts on test instances. Multi-hop / pool-retrieval benchmarks have non-trivial automorphism groups, and many "multi-hop is blocked" findings may be benchmark-symmetry artifacts (especially the SLIPNET WN18RR vs FB15K-237 difference noted in memory).

Alternative: `nonequilibrium-stat-mech` - the symmetry-broken vs symmetry-restored language has direct analogs in NESS dynamics; fluctuation theorems may give a principled way to quantify mechanism discriminating power.
