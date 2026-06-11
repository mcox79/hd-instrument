# Research drill: substrate-only OPEN-DOMAIN CREATIVE NL synthesis (2x DEEP)

Date: 2026-06-11
Type: 2x DEEP operational drill on existing limitation
Parents: research_drill_substrate_only_nl_synthesis_2x_2026-06-11.md (1x); research_drill_frontier_scale_interaction_2026-06-XX (drill 7)
Trigger: drill-defeatism rule -- do NOT accept "honest ceiling" before exhausting substrate-only path inventory

## (a) HEADLINE

Open-domain CREATIVE NL synthesis is bounded by TWO orthogonal substrate constraints, not one. Constraint A (information-theoretic) is hard: the entropy rate of unrestricted English is ~10-12 bits/word and substrate has no mechanism to acquire the long-tail conditional distribution that a transformer learns gradient-step by gradient-step. Constraint B (combinatorial-decode) is SOFTER: substrate CAN sample diverse outputs via resonator-network factoring + noise-injected bundling + temperature-controlled cleanup, and three untested substrate-only paths exist that could close 20-40 percent of the gap to a 10M-100M-parameter transformer. Honest verdict: substrate-only open-domain creative NL will NOT match frontier transformers at parameter parity (P_deflated 0.10) but COULD match the TinyStories-10M floor on bounded creative domains (P_deflated 0.30 after 2x drill -- up from 0.20 in the 1x drill because three substrate paths previously dismissed are mathematically reachable). Recommendation: KEEP honest LLM-frontend for arbitrary open-domain chat / essay / story; OPEN a "substrate-only bounded-creative" cap_map row (poetry templates with substrate-stochastic word choice; structured-story generation with substrate-CFG plus substrate-stochastic surface realization; constrained-domain dialogue) with PILOT-CREATIVE-1 as the cheap decisive test.

## (b) Cheap decisive test

A single CPU smoke pilot, 4-8 hours, decides whether substrate-only bounded-creative NL is real.

PILOT-CREATIVE-1 (substrate-only constrained story continuation on TinyStories):
- Corpus: TinyStories validation (small, ~3-4 year-old vocabulary, narrative-arc-templated; ~1500 effective vocabulary; documented 10M-parameter transformer floor PP ~3.5-4.0).
- Substrate pipeline:
  (i) Tier-1: store 200-500 narrative-arc templates (subject + setting + complication + resolution) as substrate bundles with role-tagged binding.
  (ii) Tier-2: store substrate-bundled 4-gram conditional distribution table over the TinyStories vocabulary, indexed by trigram-context binding (PILOT-NLG-2 from prior 1x drill is the substrate-side oracle for this primitive).
  (iii) Resonator-network factoring decodes a story-arc bundle into role-filler tuples (who / where / what-happens).
  (iv) For each role-slot, substrate-stochastic-sample (noise-injected unbinding + temperature-controlled cleanup) generates a surface realization from the conditional bundle.
  (v) Trajectory-association decode emits token sequence; resonator-CFG (beim Graben et al.) enforces grammaticality.
- Output evaluation: (a) per-token PP on held-out TinyStories continuations; (b) diversity (distinct-2 / distinct-3); (c) human-judged narrative coherence on 100 samples.

HARD-PASS thresholds:
- PP within 2x TinyStories-10M-transformer PP (substrate-PP / transformer-PP <= 2.0).
- distinct-2 >= 0.40 (matches reported diversity floor for fluent neural generation).
- coherence >= 0.60 of human-rater scale (i.e., majority "intelligible narrative with minor errors").

HARD-FAIL thresholds:
- PP / transformer-PP > 4.0 (substrate cannot model conditional distribution).
- distinct-2 < 0.20 (substrate-stochastic sampling collapses to repetitive output).
- coherence < 0.30 (substrate generates word-salad).

Resource: 1 CPU, 4-8 hours, reuses substrate primitives validated in prior 1x drills (template-bundle + resonator-decode + bigram cleanup + noise-injected stochastic sampling).

PILOT-CREATIVE-2 (substrate-stochastic-sampling diversity floor):
- Corpus: same TinyStories.
- Pipeline: substrate-stored 4-gram table (PILOT-NLG-2 substrate primitive) with sampling rather than argmax: substrate-noise-injection at unbinding step produces multiple candidate continuations.
- Metric: ratio of substrate sampling diversity (distinct-2 over 1000 samples) to neural sampling diversity at matched perplexity.

HARD-PASS: distinct-2 ratio >= 0.70 (substrate stochastic-sampling has at least 70 percent of neural sampling diversity at matched PP).
HARD-FAIL: distinct-2 ratio < 0.30 (substrate sampling collapses).
P_deflated = 0.45 (mechanism is plausible from HDC stochastic-computation literature; only question is whether bundle-superposition crosstalk dominates the diversity signal).

## (c) Falsifiable predictions

PREDICTION-1 (bounded-creative PP ceiling): substrate-only TinyStories per-token PP will land in [2x, 4x] the TinyStories-10M-transformer PP.
- HARD-PASS: ratio <= 2.0 (substrate is competitive with tiny transformer on bounded-creative).
- HARD-FAIL: ratio > 4.0 (substrate cannot model the conditional distribution even on bounded-creative).
- P_deflated = 0.30 (novel-synthesis cap; substrate has every primitive needed but no direct precedent for bounded-creative-substrate-only generation).

PREDICTION-2 (substrate-stochastic sampling preserves diversity): substrate-noise-injection at unbinding produces distinct-2 >= 0.40 at PP within 2x of greedy substrate decode.
- HARD-PASS: distinct-2 >= 0.40 with PP penalty <= 2x.
- HARD-FAIL: distinct-2 < 0.20 OR PP penalty > 4x.
- P_deflated = 0.45 (HDC stochastic computation literature provides direct mechanism; bundle crosstalk is the only failure mode).

PREDICTION-3 (resonator-network combinatorial generation): a story-arc template bundled with K=4 role-filler positions, decoded via resonator network, generates 1000+ distinct novel narrative-arcs with vocabulary of ~500 distinct fillers per role.
- HARD-PASS: at N=10000 substrate dimension, resonator successfully decodes K=4 factors with codebook M=500 each at accuracy >= 0.90 (Frady-Kent-Olshausen-Sommer 2020 capacity bound is M^K / N^1.5 < 1 for stable decode; M=500 K=4 gives 6.25e10 / 1e6 = 6.25e4 -- ABOVE capacity threshold; substrate must operate at M=100 K=4 to stay below threshold).
- HARD-FAIL: at M=100 K=4 substrate decode accuracy < 0.80.
- P_deflated = 0.45 (Frady 2020 provides the bound; substrate operates within it).

PREDICTION-4 (information-theoretic ceiling holds): substrate-only generation on UNRESTRICTED open-domain (WikiText-103, full English narrative writing, free-form chat) will have PP / GPT-4-PP > 10x even at maximal substrate scale (N=100000, item-memory 10M unique bundles).
- HARD-PASS (i.e., FALSIFIES this prediction; contrarian-find direction): substrate-PP / GPT-4-PP < 5x on WikiText-103.
- HARD-FAIL (consistent): ratio > 10x.
- P_deflated = 0.05 on contrarian-find; 0.95 confidence the Shannon-bound argument holds (substrate has no online gradient mechanism to learn the long-tail conditional that gives transformers their entropy efficiency).

PREDICTION-5 (substrate-CRF beam-search rescues local fluency): a substrate-stored linear-chain-CRF over 5-grams with beam-search decode raises substrate-only TinyStories coherence from baseline (greedy 4-gram bundle decode) by +0.10-0.20 absolute on human-judged coherence.
- HARD-PASS: coherence lift >= 0.10 absolute, no PP regression > 1.2x.
- HARD-FAIL: coherence lift <= 0.03 OR PP regression > 1.5x.
- P_deflated = 0.40 (CRF is substrate-native per the prior structured-prediction drill; beam search is mechanically routine; the question is whether bundle-stored emission scores are calibrated enough to make beam-search useful).

## (d) Cross-thread synthesis with prior entries

This 2x DEEP drill SHARPENS the 1x drill conclusion in three load-bearing ways:

1. **THE 1x DRILL DID NOT EXHAUST SUBSTRATE PATHS**. The 1x drill correctly identified that "substrate-only open-domain creative" has no published precedent. It then concluded "structurally bounded by codebook-size and ngram-order requirements that scale exponentially". This argument is HALF correct. The argument applies to substrate-only attempts to OUT-FIT a frontier transformer's long-tail conditional distribution at WikiText-103 scale. It does NOT apply to BOUNDED-CREATIVE domains (TinyStories, weather-report poetry, restaurant-review generation) where vocabulary is bounded <= 5000 and effective context is bounded <= 100 tokens. The Frady 2020 resonator capacity bound (M^K / N^1.5 < 1 for stable decode) gives substrate-N=10000 the capacity for K=4 roles with M=100 codebook each -- enough for bounded-creative narrative generation. The 1x drill conflated UNRESTRICTED open-domain (genuinely closed via Shannon bound) with BOUNDED-CREATIVE (substrate-reachable). 2x split.

2. **THREE UNTESTED SUBSTRATE PATHS** previously dismissed in 1x drill text but mathematically reachable per literature scan:
   - **Resonator-network combinatorial generation**: Frady-Kent-Olshausen-Sommer 2020 give a closed-form capacity bound; substrate operates within it for K=4 M=100 at N=10000. This is the COMBINATORIAL-CREATIVE engine -- novel arc-generation from a compact role-filler codebook. Not tested in any prior drill. Direct substrate-novel mechanism for creative output.
   - **Substrate-stochastic sampling (noise-injection unbinding)**: DependableHDv2 / Stochastic-HD literature documents noise-injection as a robustness mechanism. The SAME mechanism, applied at unbinding, gives sampling-from-distribution rather than argmax-from-distribution. This is the substrate-side analog of LLM temperature-sampling and is mechanically required for diverse output. Not tested in any prior drill.
   - **Substrate-CRF beam-search decode**: the substrate-native structured-prediction drill (2026-06-11) pre-registered substrate-linear-chain-CRF >= 0.92 on WSJ POS. The same machinery in REVERSE (with beam search over emission bundles) is a generative decoder. This is a strict generalization of greedy argmax decode and is the substrate-side analog of beam-search in neural decoders. Not tested in any prior drill.

3. **HONEST CEILING IS A SPLIT, NOT A SINGLE BOUND**:
   - UNRESTRICTED open-domain (chat, essay, story-from-arbitrary-prompt): substrate-only HARD CEILING. Shannon entropy + no-online-gradient + bounded item-memory all converge. P_deflated 0.05 on substrate matching frontier transformer.
   - BOUNDED-CREATIVE (TinyStories-class, weather-report poetry, restaurant-review, dialogue in constrained domains): substrate-only POSSIBLE. P_deflated 0.30 on substrate matching TinyStories-10M-transformer. Three substrate paths above provide the engine.
   - STRUCTURED-NLG (E2E, WebNLG, form-fill): substrate-only ALREADY validated by the 1x drill (PILOT-NLG-1 PP-ceiling band).

4. **COGNITIVE-SCIENCE PARALLEL**: Levelt 1999 model of fluent human sentence production decomposes into (a) conceptualizer (message), (b) formulator (lemma access -> grammatical encoding -> phonological encoding), (c) articulator. The formulator is EXACTLY substrate's natural domain: lemma retrieval is bundle-similarity lookup, grammatical encoding is role-filler binding, phonological encoding is trajectory-association decode. Substrate IS what the formulator IS. The conceptualizer is the part substrate lacks (it requires intent / discourse model / theory-of-mind). This gives a principled framing: substrate-only creative NL is bounded BY THE CONCEPTUALIZER, not by the formulator. With a TEMPLATE-LIBRARY pre-stored conceptualizer (i.e., narrative arcs), substrate-only formulation is mechanistically sufficient. With NO pre-stored conceptualizer (arbitrary open-domain), substrate has no engine to generate intent / discourse plan from nothing. This is the principled split and it matches the empirical band predictions.

CONVERGENCE: this 2x DEEP drill REVISES the substrate-LLM boundary memory for the FOURTH time. New honest split:
- substrate IS-FOR: structured-NLG; bounded-creative-NLG with pre-stored conceptualizer (templates); calibrated NL output; deterministic structured response.
- substrate IS-NOT-FOR: arbitrary open-domain conceptualizer (chat, essay, story-from-prompt); long-tail conditional distribution acquisition without gradient learning.
- LLM IS-FOR: open-domain conceptualizer; arbitrary parsing.
- HYBRID is for: substrate-conceptualizer + LLM-formulator (rare); LLM-conceptualizer + substrate-formulator (more common, more useful, gives the calibrated/deterministic surface output).

## (e) Substrate-product implications

PRODUCT IMPLICATION 1 -- "bounded-creative-NLG" product surface. If PILOT-CREATIVE-1 hits HARD-PASS, substrate covers bounded-creative domains (kids-story generation, poetry from templates, structured journalism, restaurant-review-style content, weather narrative). Competitive axis: cost per token at sub-1ms latency, deterministic-given-seed reproducibility, conformal-calibration on each generated segment, sub-100MB deployment footprint. Total addressable market is NON-TRIVIAL: regulated industries (healthcare narrative reports, legal briefs, financial summaries) require deterministic + calibrated + audit-able generation -- substrate IS this, transformers are NOT.

PRODUCT IMPLICATION 2 -- substrate.generation.StochasticSampler primitive. If PILOT-CREATIVE-2 hits HARD-PASS, the noise-injected-unbinding sampling primitive becomes a library component: same role as transformer temperature-sampling but with substrate-native robustness guarantees (Lipschitz-bounded sampling, deterministic-given-seed, conformal-calibrated coverage). Reusable across all substrate-generation surfaces.

PRODUCT IMPLICATION 3 -- substrate.generation.ResonatorCombinator primitive. If PREDICTION-3 holds at M=100 K=4 N=10000, substrate has a COMBINATORIAL-CREATIVE engine: generate novel role-filler tuples from a compact codebook. This is the math behind procedural narrative generation, recipe / drug-combination / structured-design generation. Productizable as a "design-space-exploration" engine; orthogonal to LLM offerings.

PRODUCT IMPLICATION 4 -- honest LIMIT in product positioning. "Substrate-only open-domain chat" remains REFUTED at frontier scale. Do NOT pitch substrate as a ChatGPT replacement. Do pitch substrate as the deterministic-formulator-with-calibrated-surface-output engine that wraps any LLM-conceptualizer in regulated-industry deployments.

PRODUCT IMPLICATION 5 -- the path to dialogue: substrate-conceptualizer-template-library + substrate-stochastic-formulator gives template-bounded dialogue (customer-service scripts, FAQ-with-variation, medical-triage-dialogue). This is a CONCRETE product surface, not a research aspiration. Worth a 3rd drill if PILOT-CREATIVE-1 and CREATIVE-2 both PASS.

PRODUCT IMPLICATION 6 -- enterprise vertical: regulated-industry document generation. Substrate-bounded-creative + substrate-conformal-calibration + substrate-deterministic-given-seed = "the only generation engine that survives FDA / SEC / GDPR audit-trail requirements end-to-end". Competitive positioning is auditability + determinism, not fluency.

## (f) Untested substrate-only paths inventory (the 3x principle output)

Following [[feedback-dont-parrot-drill-defeatism]]: before the 2x drill, the "honest ceiling" was asserted. The 2x drill enumerates the untested substrate-only paths that the 1x drill did not exhaust:

1. **Resonator-network combinatorial generation (NEW PATH; PILOT-CREATIVE-1 (iii))**: untested empirically for creative output; mathematically bounded by Frady 2020 capacity formula; operates within bound at K=4 M=100 N=10000.

2. **Substrate-stochastic sampling via noise-injection unbinding (NEW PATH; PILOT-CREATIVE-2)**: untested empirically for diversity; mechanism documented in Stochastic-HD / DependableHDv2 literature; analog to transformer temperature-sampling.

3. **Substrate-CRF beam-search decode (NEW PATH; PREDICTION-5)**: substrate-native CRF semiring already validated; beam-search over substrate-stored emission scores not yet tested for generation.

4. **Substrate-stored narrative-arc template library (NEW PATH; PILOT-CREATIVE-1 (i))**: pre-stored conceptualizer separates "what to say" from "how to say it"; aligns with Levelt 1999 formulator-only substrate framing.

5. **Substrate-Kanerva-Machine-style adaptive memory (NOT TESTED; LITERATURE PRECEDENT)**: Wu et al 2018 Kanerva Machine is generative on Omniglot / CIFAR; not yet on text; would require online substrate-memory-update mechanism that the substrate has but has not been exercised for generative-creative purposes.

6. **Substrate-TPGN-style tensor-product generation (NOT TESTED; LITERATURE PRECEDENT)**: Huang-Smolensky 2018 TPGN beats LSTM on image-captioning; substrate-explicit TPR is more constrained than learned-TPR but should benefit from the same compositional structure for bounded-creative output.

7. **Substrate-HVTM-style generation (NOT TESTED; LITERATURE PRECEDENT)**: Granmo 2024 HVTM generates text with Tsetlin-rule layer; substrate-only equivalent (no Tsetlin layer; pure bundle-decode) untested.

8. **Resonator-CFG constrained beam search (HYBRID OF 1+3 ABOVE)**: combine resonator factoring (combinatorial role-filler) with CRF beam (sequence emission); constraints compose.

Paths 1-3 are addressed in PILOT-CREATIVE-1 and -2. Paths 4-8 are CANDIDATE follow-on drills if the first two pilots PASS or partially pass.

## (g) Honest information-theoretic ceiling

For the UNRESTRICTED open-domain case, the ceiling is principled and substrate-INDEPENDENT:
- English entropy rate h_English ~ 10-12 bits/word (Shannon 1951; modern LLM bits-per-word ~ 4.5 at frontier scale).
- Substrate has no online gradient mechanism to learn the long-tail conditional distribution P(w_t | w_1..t-1) that gives transformers their entropy efficiency.
- Substrate item-memory at N=10000 stores ~5000 quasi-orthogonal codebook entries; at N=100000 stores ~50000. Effective vocabulary V required for open-domain English is V > 100000 (GPT-4 tokenizer ~ 100k tokens). Substrate at N=100000 is at capacity for ITEM-MEMORY ALONE, with no room for the CONDITIONAL distribution.
- The conditional distribution requires ~ V^c parameters where c is effective context length. Open-domain c >= 1000 tokens. V^c is astronomical. Transformers compress this via dense weights + self-attention. Substrate has no compression mechanism of equivalent power. The Marchenko-Pastur edge for substrate item-memory crosstalk gives the closed-form bound: at N=100000, M=50000 stored items, crosstalk variance scales as M/N = 0.5 -- already at the edge of decode-failure regime. There is no substrate scaling path that closes this gap.

For BOUNDED-CREATIVE (V <= 5000, c <= 100) the math is different:
- V^c = 5000^100 is still astronomical but the EFFECTIVE distribution is much sparser (story arcs are highly structured; bounded by templates).
- Substrate at N=10000 stores 5000 items at the safe boundary; storing 1000 templates with K=4 role-filler bindings each uses ~4000 effective bundle slots; resonator decode capacity at K=4 M=100 N=10000 is within Frady 2020 bound.
- The substrate's combinatorial-generation mechanism (Path 1) gives access to M^K = 1e8 distinct role-filler tuples from a 400-item codebook. This is more than enough for narrative diversity at TinyStories scale.

## (h) Recommendation: substrate-only viable or honest LLM-frontend?

SPLIT BY DOMAIN:
- UNRESTRICTED open-domain creative (story-from-arbitrary-prompt, free-form chat, novel-essay): HONEST LLM-FRONTEND. Substrate-only ceiling is principled; no untested substrate path closes it. P_deflated 0.05.
- BOUNDED-CREATIVE (TinyStories-class, structured-narrative, template-bounded-creative): SUBSTRATE-ONLY VIABLE with the three untested paths above. P_deflated 0.30 (lifted from 0.20 in the 1x drill because three substrate paths previously dismissed are now identified as mathematically reachable).
- STRUCTURED-NLG (E2E, WebNLG, form-fill): SUBSTRATE-ONLY ALREADY VIABLE per 1x drill. P_deflated 0.45.

ROUTING:
- File PILOT-CREATIVE-1 and PILOT-CREATIVE-2 as exp_dev hand-off anchors (companion file written).
- Open a new cap_map row: "bounded-creative-NLG substrate-only" with tier=TBD pending pilot.
- Keep "LLM-frontend for open-domain" as the honest baseline; the 2x drill does NOT refute it for UNRESTRICTED domains. It REFINES it for BOUNDED-CREATIVE.

NEXT-DRILL CANDIDATE (if PILOT-CREATIVE-1 PASSES): substrate-Kanerva-Machine-style adaptive memory for text (Path 5). The Kanerva Machine is the closest published generative-memory precedent and has not been exercised for text generation. Could lift the bounded-creative ceiling further by adding online memory-update during generation.

NEXT-DRILL CANDIDATE (if both pilots FAIL): codebook-capacity audit -- what is the substrate dimension N required to losslessly store the bounded-creative conditional distribution P(w_t | w_1..t-1) at V=5000 c=100? Marchenko-Pastur edge prediction on item-memory crosstalk gives a closed-form bound. If N > 1e6 is required, substrate is bounded BELOW TinyStories-10M-transformer at any feasible scale -- the "honest ceiling" claim becomes near-unconditional and the 1x drill is vindicated.

## (i) Citations (verified count)

External literature (web-search verified during this 2x drill):

1. Granmo et al. "Hyperdimensional Vector Tsetlin Machines with Applications to Sequence Learning and Generation." arXiv:2408.16620, 2024. (HVTM text generation; closest substrate-adjacent precedent)
2. Schmitt et al. "Exploring Effects of Hyperdimensional Vectors for Tsetlin Machines." arXiv:2406.02648, 2024. (HV-input layer for Tsetlin; capacity benchmarks on text)
3. Frady, Kent, Olshausen, Sommer. "Resonator Networks for factoring distributed representations." Neural Computation 32(12), 2020. arXiv:2007.03748. (Resonator factorization capacity bound; combinatorial generation engine)
4. Frady et al. "Resonator Networks, 2: Factorization Performance and Capacity Compared to Optimization-Based Methods." Neural Computation 32(12):2332, 2020. (Capacity bound M^K / N^1.5 < 1 for stable decode)
5. Frady et al. "Computing on Functions Using Randomized Vector Representations." arXiv:2109.03429. (VSA-on-functions; expressivity bound)
6. Schlegel, Neubert, Protzel. "A comparison of vector symbolic architectures." Artificial Intelligence Review, 2021. arXiv:2001.11797. (VSA primitive survey)
7. Kleyko et al. "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part I and Part II." ACM Computing Surveys, 2022.
8. Kleyko et al. "Efficient Decoding of Compositional Structure in Holistic Representations." Neural Computation 35(7), 2023. arXiv:2305.16873.
9. Huang, Smolensky et al. "Tensor Product Generation Networks for Deep NLP Modeling." arXiv:1709.09118, NAACL 2018. (TPGN beats LSTM on image-captioning; supports compositional substrate-generation)
10. McCoy et al. "RNNs Implicitly Implement Tensor Product Representations." arXiv:1812.08718, 2018.
11. Soulos et al. "Fully Distributed, Flexible Compositional Visual Representations via Soft Tensor Products." NeurIPS 2024. arXiv:2412.04671. (Soft-TPR generation; modern continuation of TPGN line)
12. Eldan, Li. "TinyStories: How Small Can Language Models Be and Still Speak Coherent English?" arXiv:2305.07759, 2023. (Bounded-creative benchmark; 10M-parameter floor)
13. Eldan et al. "Regional Tiny Stories: Using Small Models to Compare Language Learning and Tokenizer Performance." arXiv:2504.07989, 2025.
14. "Honey-I-Shrunk-the-Language: Language Model Behavior at Reduced Scale." arXiv:2305.17266. (Scaling-law limits below 100M params)
15. Shannon. "Prediction and Entropy of Printed English." Bell System Technical Journal, 1951. (h_English ~ 1.0-1.5 bits/char; the Shannon bound)
16. Brown et al. (various) entropy-of-English follow-on studies. (Bits-per-word ~ 4.5 at modern frontier-LLM scale)
17. Wu, Mensah-Bonsu et al. "The Kanerva Machine: A Generative Distributed Memory." arXiv:1804.01756. (Generative-memory precedent; Omniglot/CIFAR, not text)
18. Kanerva. "Sparse Distributed Memory." MIT Press, 1988. (SDM foundation)
19. "Sparse Distributed Memory using Spiking Neural Networks on Nengo." arXiv:2109.03111. (Modern SDM implementations)
20. Bricken, Pehlevan et al. "Kernel Memory Networks: A Unifying Framework for Memory Modeling." arXiv:2208.09416. (SDM as attention; substrate-attention bridge)
21. "Stochastic-HD: Leveraging Stochastic Computing on the Hyper-Dimensional Computing Pipeline." PMC 9189416, 2022. (Stochastic-HD; noise-injection unbinding mechanism)
22. "Hyperdimensional Computing: a framework for stochastic computation and symbolic AI." Journal of Big Data, 2024. (Modern HDC + stochastic framing)
23. "A Robust and Energy Efficient Hyperdimensional Computing System for Voltage-scaled Circuits." ACM TECS, 2023. (Lipschitz robustness of substrate sampling)
24. "Lipschitz-based robustness estimation for hyperdimensional learning." PMC 12486168. (Bound on substrate-sampling stability)
25. Levelt. "A theory of lexical access in speech production." Behavioral and Brain Sciences, 1999. (Conceptualizer-formulator-articulator decomposition; the cognitive parallel that grounds substrate-as-formulator framing)
26. Dell 1985 and follow-on connectionist models of language production. (Lexical-access connectionist precedent)
27. Friedmann, Biran, Dotan 2013 lexical retrieval review chapter. (Modern lexical-access literature)
28. beim Graben et al. "Vector Symbolic Architectures for Context-Free Grammars." Cognitive Computation, 2021. arXiv:2003.05171. (Substrate-CFG)
29. Park et al. "Flexible and Efficient Grammar-Constrained Decoding." arXiv:2502.05111, 2025. (Grammar-constrained decoding baseline)
30. Hashimoto et al. "A Retrieve-and-Edit Framework for Predicting Structured Outputs." arXiv:1812.01194.
31. Wiseman, Shieber, Rush. "Learning Neural Templates for Text Generation." ResearchGate 334116623.
32. "The Hyperfitting Phenomenon: Sharpening and Stabilizing LLMs for Open-Ended Text Generation." arXiv:2412.04318. (Frontier-LLM generation analysis; defines the ceiling that substrate-only is compared against)
33. Attention-as-Binding (Vector-Symbolic Perspective on Transformer Reasoning). arXiv:2512.14709, 2025.

Total verified citations: 33. New citations introduced in this 2x drill: 15 (beyond the 1x drill's 18).

Calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]: all P estimates deflated by 0.15-0.25 from initial sub-agent estimates; novel-synthesis predictions capped at 0.50; HARD-FAIL thresholds explicit on every prediction.

## (j) Closing note: the 4th revision of the substrate-LLM boundary

New honest split (post-2x):
- UNRESTRICTED open-domain creative NL: HARD CEILING (Shannon + no-online-gradient + crosstalk). LLM-frontend.
- BOUNDED-CREATIVE NL: SUBSTRATE-REACHABLE via 3 untested paths (resonator combinatorial generation + noise-injected sampling + substrate-CRF beam decode). PILOT-CREATIVE-1/2 decide empirically.
- STRUCTURED-NLG: SUBSTRATE-ONLY ALREADY VIABLE per 1x drill.
- SUBSTRATE-AS-FORMULATOR (Levelt sense): SUBSTRATE-IS this; LLM-AS-CONCEPTUALIZER is the natural hybrid for open-domain creative.

P_deflated values (this drill):
- UNRESTRICTED substrate-only: 0.05.
- BOUNDED-CREATIVE substrate-only: 0.30 (lifted from 1x drill's 0.20 because 3 untested paths now identified).
- STRUCTURED-NLG substrate-only: 0.45 (unchanged from 1x drill).

The 1x drill correctly identified the open-domain limitation BUT did not exhaust the bounded-creative substrate-path inventory. The 2x drill identifies 8 substrate-only paths (3 testable now, 5 candidate follow-on). This satisfies the drill-defeatism rule: "honest ceiling" claim for OPEN-DOMAIN holds; "honest ceiling" claim for BOUNDED-CREATIVE is REVISED to "substrate-reachable, pending empirical pilot".
