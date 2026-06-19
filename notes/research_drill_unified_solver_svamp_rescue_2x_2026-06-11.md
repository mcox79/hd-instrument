# Research drill 2x DEEP: unified-solver SVAMP rescue
date: 2026-06-11
topic: unified-solver SVAMP rescue (training-pool interference)
scope: 2x DEEP operational drill on EXISTING finding (specialized SVAMP 0.297 -> unified SVAMP 0.147 under MAWPS-heavy combined pool); recover SVAMP toward 0.297 while keeping single benchmark-agnostic solver
calibration: lit-scan penalty 0.15-0.25; novel-synthesis cap 0.50
safety: ASCII; no project-specific numerical targets in queries; generic-math search terms only

## HEADLINE

The unified-solver SVAMP collapse is a textbook negative-transfer event: MAWPS-heavy combined pool dominates the gradient (and the prototype) for the single shared op-classifier, pulling the decision boundary toward MAWPS-style single-op surface cues and away from SVAMP's adversarial perturbations. Four substrate-native paths recover SVAMP-class accuracy without abandoning single-solver unification, ranked by mechanism-readiness:
(1) per-benchmark context-binding (TP-HDC pattern; substrate already supports this on PP-346) — single classifier, multiple bound prototypes, decoded by context;
(2) cleanup-margin-gated soft mixture-of-experts (substrate-native router; no learned-router needed);
(3) inverse-frequency / effective-number reweighting over (benchmark, op) cells at training-pool ingest;
(4) interleaved curriculum with similarity-ordered batches.
Paths (1) and (2) are pure substrate algebra (no new architecture), preserve "one classifier" externally, and are the cheap-decisive shipping order.

## Cheap decisive test (substrate-native, single-runner-cell)

Single CPU cell, ~30-60 min, no GPU:
- Reuse current unified richer-feature averaged perceptron pipeline.
- Build context vector ctx_b per benchmark b in {MAWPS, SVAMP, ASDiv, MultiArith} (random bipolar; orthogonal by construction at N=1024).
- During training: bind every training example's feature hypervector with its source-benchmark ctx_b before the perceptron update (or equivalently, store a per-class prototype bound with ctx_b). This is the TP-HDC pattern.
- At inference: probe each problem with all four ctx_b bindings, score against the shared prototype set, and select the (op, b)-pair with maximal cleanup margin. Externally still "one solver" (one weight set, one forward pass schedule); internally, context-binding partitions the prototype space.
- Decisive: if SVAMP recovers above the "unified-only" floor by a substantial margin (HARD-PASS threshold below) without dragging MAWPS down meaningfully, the path is validated.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

H1. Context-bound unification recovers most of the specialized SVAMP capability.
HARD-PASS: unified-with-context SVAMP >= 0.80 x specialized SVAMP, AND unified-with-context MAWPS >= 0.95 x current unified MAWPS.
HARD-FAIL: unified-with-context SVAMP < 1.10 x current unified-uncontextualized SVAMP, OR MAWPS drops below 0.90 x current unified MAWPS.
Mechanism: TP-HDC literature (Chang et al., "Task-Projected Hyperdimensional Computing for Multi-Task Learning") shows orthogonal context-binding suppresses cross-task interference by design (orthogonal codewords are mutually invisible under cleanup). Interference is the documented dominant cause of accuracy loss when prototypes are bundled across tasks.

H2. Cleanup-margin-gated soft routing beats hard per-benchmark routing.
HARD-PASS: soft-margin routing yields macro-mean strictly above unified-without-routing AND strictly above hard-arg-max-on-context-tag routing.
HARD-FAIL: soft routing within +/- 1 SE of unified-without-routing.
Mechanism: SVAMP's adversarial perturbations specifically break per-benchmark surface cues, so a hard benchmark-tag router will misroute SVAMP problems to MAWPS prototypes; the substrate cleanup margin is a calibrated confidence and gates the per-context decoded score before mixture.

H3. Inverse-frequency reweighting alone does NOT suffice.
HARD-PASS-of-the-NEGATIVE: reweighting-alone SVAMP improvement < 0.5 x context-binding SVAMP improvement.
HARD-FAIL: reweighting alone recovers >= 0.8 x context-binding gain (would mean the issue is class-imbalance not representational-interference).
Mechanism: Salmani & Worah 2025 ("Sampling and Loss Weights in Multi-Domain Training") show sampling/loss weights help when the per-domain optimum lies in a shared region; SVAMP's distinguishing features are antagonistic to MAWPS's, so geometry-changing (binding) should beat amplitude-changing (reweighting).

H4. Anti-curriculum (SVAMP first, MAWPS late) outperforms easy-first.
HARD-PASS: anti-curriculum order in unified training closes >= 30 percent of the unified-vs-specialized SVAMP gap.
HARD-FAIL: anti-curriculum order does not close any of the gap.
Mechanism: late-stage majority-domain exposure tends to overwrite earlier minority-domain decision boundaries (continual-learning literature; Bell & Lawrence 2022, "The Effect of Task Ordering in Continual Learning"). Anti-curriculum exposes the harder/minority pattern first then preserves it under MAWPS-heavy late training only if reweighting accompanies it (combine with path 3 for fair test).

## Substrate-native paths to recover SVAMP under unification (ranked)

### Path A. Context-binding per benchmark (TP-HDC pattern, substrate-native, READY)
- Mechanism: bind every training example's feature HV with a benchmark-context HV ctx_b (random bipolar, orthogonal by construction at N=1024). Single shared prototype codebook, but each class prototype effectively occupies an orthogonal projection per benchmark. Cross-benchmark interference is suppressed by design — orthogonal context HVs make MAWPS prototypes invisible to SVAMP queries at cleanup time. This is *exactly* the PP-346 concept-context-binding pattern that lifted image-schema polysemy 0.342 -> 1.000 HP.
- Substrate algebra: bind = XOR / circular-conv depending on substrate variant; cost is one binding op per train sample and four binding ops per inference query (one per ctx_b).
- Unification preservation: externally a single solver — one weight set, one architecture, one training loop. The "benchmark-aware-ness" is a property of the *binding step* not the *architecture*.
- Mechanism-readiness: HIGH. substrate already validated context-binding on PP-346 + slipnet polysemy work; the TP-HDC literature is the direct extra-substrate precedent.
- Risk: at inference time the benchmark is unknown for arbitrary user inputs. Mitigation: argmax over (op, b)-pairs picks the highest-margin context, effectively a substrate-native router (Path B emerges naturally).

### Path B. Cleanup-margin-gated soft mixture-of-experts (substrate-native router, READY)
- Mechanism: after Path A's context-binding, each inference query produces four candidate (op, b) decodings, each with a cleanup-margin score m_b (top1 - top2 in similarity). Soft-mixture the predictions weighted by softmax(m_b / tau). At tau -> 0 this is hard arg-max-context routing; at tau large it is uniform mixture. The substrate cleanup margin IS the natural router signal — no learned router needed.
- Sub-mechanism for full MoE flavor: per-benchmark Tier-2 schemas (separate prototype codebooks per b), all sharing a Tier-1 cleanup codebook. This separates the high-frequency MAWPS schema from the low-frequency SVAMP schema while keeping the shared math vocabulary.
- Mechanism-readiness: HIGH. substrate-internal — cleanup margin is already computed in every retrieval; soft mixture is a one-line addition.
- Risk: requires the four per-context margins to be calibrated (comparable across b). If one benchmark systematically yields higher margins (likely MAWPS, since its prototype is best-trained), the mixture biases toward it. Mitigation: per-benchmark margin normalization (z-score over a held-out calibration set).

### Path C. Inverse-frequency / effective-number reweighting at ingest (READY, weaker mechanism)
- Mechanism: during prototype bundling, weight each training example by 1 / sqrt(n_{b,op}) where n_{b,op} is the count of that (benchmark, op) cell in the training pool. Equivalently, downsample MAWPS to balance with SVAMP. Substrate-native: each bundled HV gets a real-valued amplitude weight.
- Effective-number variant (Cui et al. 2019, "Class-Balanced Loss Based on Effective Number of Samples"): weight = (1 - beta) / (1 - beta^{n_{b,op}}) with beta ~ 0.999. Compresses the effective-sample-count distribution.
- Mechanism-readiness: HIGH but EXPECTED-WEAKER than A or B. Reweighting addresses amplitude not geometry; if SVAMP and MAWPS class-conditional distributions overlap but disagree on labels (which is the adversarial nature of SVAMP), reweighting will not separate them.
- Use as ablation / control for H3.

### Path D. Interleaved curriculum with anti-curriculum tail (READY, combine with C)
- Mechanism: order training mini-batches so that (i) each batch is benchmark-balanced (interleaved practice — cog-sci shows interleaved beats blocked for transfer), (ii) early in training emphasize SVAMP (anti-curriculum: hard-first), (iii) preserve SVAMP late by combining with Path-C reweighting.
- Sub-mechanism: in cog-sci, contextual cueing (Lleras & Von Muhlenen) and task-set reconfiguration literature (Monsell 2003) shows humans handle multi-domain practice via cue-driven set reconfiguration — the substrate analog is the per-batch ctx_b being a cue.
- Mechanism-readiness: MEDIUM. Curriculum order is sensitive and brittle without context-binding; alone it will likely yield modest gains. Use as additive layer on top of A+B+C.

### Path E. Gradient-surgery / PCGrad analog (LOWER READINESS for substrate)
- Mechanism (PCGrad, Yu et al. 2020 NeurIPS): when two per-task gradients have negative cosine similarity, project each onto the normal plane of the other. Eliminates destructive interference.
- Substrate analog: when the per-benchmark prototype-update directions (delta-HV for class c from benchmark b) have negative cosine similarity, project each onto the orthogonal complement of the other before bundling.
- Why lower readiness: substrate prototypes are typically bundled (averaged) not gradient-descended; the "update" notion is amplitude-on-HV. The natural substrate analog of PCGrad is to detect cross-benchmark prototype conflict (low cosine similarity between per-b sub-prototypes for the same op) and bind with orthogonal context (which IS Path A). Path A is the substrate-native PCGrad.

### Path F. Information-geometric framing (NEW MATH, framing-grade not deployment-grade)
- Framing: multi-task interference is a curvature/conflict statement in the joint Fisher information manifold of the task losses. For substrate, replace Fisher with the substrate cleanup-similarity Gram matrix G_{ij} = <HV_i, HV_j>. Provable separation: if for every pair (i in MAWPS, j in SVAMP) the binding ctx_M and ctx_S satisfy <ctx_M, ctx_S> = epsilon, the cross-benchmark cleanup interference is O(epsilon) (concentration of measure at high N). At N=1024 random bipolar, |<ctx_M, ctx_S>| ~ 1/sqrt(N), giving an O(1/sqrt(N)) interference bound. This is a substrate-novel statement: orthogonal context-binding gives provable 1/sqrt(N) cross-task interference suppression — the high-D blessing-of-dimensionality applied to multi-task learning.
- Use: theory anchor for Paths A and B, justifies "binding alone should suffice."

## Cross-thread synthesis

- Substrate-classical NL methods outperform phasor (2026-06-11): the validated pattern is "count-based statistical methods stored as substrate Tier-2 bundles." The unified-solver perceptron is exactly that pattern. SVAMP-rescue is a Tier-2 schema separation problem solved by Tier-1-shared cleanup + Tier-2-per-domain prototypes.
- PP-346 / image-schema rescue 2026-06-10: concept-context binding lifted polysemy 0.342 -> 1.000 HP. The SVAMP collapse is structurally identical to image-schema polysemy — the same (sense / benchmark) discriminative dimension is collapsed by bundle averaging, and the same fix applies: bind by the discriminating context.
- Drill-pattern memory 2026-06-11 (TEMPORAL+CONTEXTUAL works, FIXED-ARCHITECTURE fails): Paths A and B are CONTEXTUAL (binding) — privileged P_deflated. Paths C and D are not contextual per se but are also not "fixed-architecture" claims, so neither penalty nor bonus applies.
- Cross-domain substrate retraction 2026-06-10: P9 cross-domain RETRACTED was within a *single* shared bundle (entity-geometry confound). Path-A context-binding is the architectural antidote — orthogonal binding makes cross-domain confound *impossible by construction*. So Path A is consistent with the retraction (the retraction motivates A, doesn't refute it).
- Substrate primitives YES integration NO 2026-06-10: cross-domain integration was the failure mode. Path B (cleanup-margin-gated MoE) is an *integration* primitive built from existing substrate primitives — solves "single solver appearance, separated internals" cleanly.

## Substrate-product implications

The unified-solver SVAMP regression is the cleanest possible motivating example for substrate's central value-proposition over LLM-only:
- LLM unification = monolithic mixed weights, every-domain interference at every parameter, no audit trail.
- Substrate unification with Path-A binding = single API surface, single prototype codebook, but provably separated context subspaces with a per-binding cleanup-margin score that IS the audit signal. The customer can see WHICH benchmark-context fired, with what margin, for any inference.
- This is the auditable-AI-memory-subsystem strategic direction in a tight package: same external simplicity as LLM monolith, but every routing decision is observable and the interference math is closed-form (1/sqrt(N) bound from concentration).
- For the v1 demo, the (op_predicted, benchmark_context, margin) triple is shippable as the audit envelope.

Recommendation to Exp-Dev: ship Path A as the cheap decisive test (single CPU cell, < 1 hr, no GPU). If H1 passes, ship A+B as the unified-solver v2; if H1 partial, layer C and D and re-test.

## Citations (verified count: 8)

1. Yu et al. 2020, "Gradient Surgery for Multi-Task Learning," NeurIPS / arXiv:2001.06782. PCGrad mechanism.
2. Chang et al. 2020, "Task-Projected Hyperdimensional Computing for Multi-task Learning," Springer / PMC7256401. Direct substrate-native precedent for Path A.
3. Salmani & Worah 2025, "Sampling and Loss Weights in Multi-Domain Training," arXiv:2511.06913. Reweighting framework for Path C.
4. Cui et al. 2019, "Class-Balanced Loss Based on Effective Number of Samples," CVPR. Effective-number reweighting for Path C.
5. Bell & Lawrence 2022, "The Effect of Task Ordering in Continual Learning," arXiv:2205.13323. Curriculum / anti-curriculum for Path D.
6. Monsell 2003, "Task switching," Trends in Cognitive Sciences. Cog-sci task-set reconfiguration, motivation for Path B routing.
7. Shazeer et al. 2017 / Fedus et al. 2022 (Switch Transformer) / Zhou et al. 2022 ("Mixture-of-Experts with Expert Choice Routing"). Sparse MoE precedent for Path B.
8. Sener & Koltun 2018, "Multi-Task Learning as Multi-Objective Optimization," NeurIPS. MGDA / Pareto-optimal task combination, theoretical context for H1/H2.

## Pre-registered HARD-PASS / HARD-FAIL summary (consolidated)

| Path | HARD-PASS | HARD-FAIL |
|---|---|---|
| A (context-bind) | unified-SVAMP >= 0.80 x specialized-SVAMP AND unified-MAWPS >= 0.95 x current-unified-MAWPS | unified-SVAMP < 1.10 x current-unified-SVAMP OR MAWPS drops below 0.90 x current-unified |
| B (soft margin route) | macro-mean strictly above A-only AND strictly above hard-arg-max routing | within +/- 1 SE of A-only |
| C (reweight) | recovers most of A's SVAMP gain on its own | recovers most of A's SVAMP gain on its own (would falsify H3) |
| D (anti-curriculum) | closes >= 30 percent of unified-vs-specialized SVAMP gap when combined with C | closes none of the gap |

## P_deflated estimates (lit-scan calibrated)

- Path A succeeds (H1 PASS): theoretical P 0.70 (direct TP-HDC precedent + substrate PP-346 precedent), DEFLATED 0.50 (substrate-novel composition with op-classifier setting).
- Path B improves over A: theoretical P 0.55, DEFLATED 0.40.
- Path C dominant on its own (would surprise): theoretical P 0.20, DEFLATED 0.15.
- Path D adds >= 30 percent gap closure on top of A+B+C: theoretical P 0.40, DEFLATED 0.30.
- Path F provable bound holds empirically at N=1024: theoretical P 0.80 (concentration of measure is well-established), DEFLATED 0.60 (cap at novel-synthesis 0.50 -> 0.50).

Headline P_deflated for the rescue program (at least one of A/B recovers SVAMP to >= 0.80 x specialized): 0.50.

Next-drill candidate field: free-probability (F4 free cumulants or F2 Tracy-Widom on substrate W eigenvalues) — adjacency to substrate prototype-codebook spectral statistics is the obvious next drill, and the field advisor already ranks F4 and F2 in the top 5.
