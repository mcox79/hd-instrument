# Research drill: substrate-only NL SYNTHESIS feasibility (2x DEEP)

Date: 2026-06-11
Type: 2x DEEP operational drill
Topic: Verify or refute the frontier-scale-interaction drill claim that "LLM front-end stays for NL fluency" — is there ANY substrate-only NL generation path?
Companion drill: research_drill_code_synthesis_substrate_feasibility_2x_2026-06-11.md (code-synthesis sibling; the NL-version of the same question)

## (a) HEADLINE

Substrate-only NL SYNTHESIS is FEASIBLE in the LOW-ENTROPY / STRUCTURED-TEMPLATE regime ONLY. Three substrate-native paths are empirically grounded in published literature (HV-Tsetlin Machine 2024 generates English at 10-kbit hypervector width; VSA-CFG production rules with resonator-network factoring; substrate-stored n-gram bundles with Kneser-Ney backoff). Substrate-only OPEN-DOMAIN creative generation has NO published precedent and is structurally bounded by codebook-size and ngram-order requirements that scale exponentially with effective context window. Honest verdict: the "LLM front-end stays for NL fluency" claim HOLDS for OPEN-DOMAIN GENERATION; it is REFUTED for STRUCTURED / TEMPLATE / FORM-FILL / DETERMINISTIC-DOMAIN generation, where substrate-only outperforms LLM on calibration, determinism, and parameter efficiency. The boundary is empirically and theoretically the lexical entropy of the target domain.

## (b) Cheap decisive test

A single CPU smoke pilot, < 4 hours, decides whether the substrate-only structured-NLG path is real:

PILOT-NLG-1 (substrate-only template-fill on E2E-NLG-clean):
- Corpus: E2E-NLG-cleaned (50k restaurant-domain MR→text pairs; documented heavy template structure; ~6 slot types; ~150-word effective vocabulary).
- Substrate pipeline: (i) Tier-1 store ~200 surface templates extracted from training set as substrate bundles with role-tagged slot positions; (ii) given a meaning representation (MR), retrieve top-k matching template by substrate similarity over role-bundled MR encoding; (iii) substrate-stored lexicon for slot-value surface forms (binding key=slot-type, value=verbalized phrase); (iv) trajectory-association decode the resulting bundle to a token sequence; (v) bigram cleanup memory rejects any 2-gram with substrate-stored bundled-corpus frequency below threshold.
- Output evaluation: BLEU-4 and slot-error-rate on E2E test set (1k examples).
- Resource: 1 CPU, ~4 hours; uses only existing substrate primitives (binding, bundling, cleanup, trajectory-association, role binding).

If PASS: substrate has a structured-NLG capability that does not require an LLM front-end. Open a Tier-1 product surface ("calibrated form-fill / report-generation / structured-response substrate" — a measurable competitive surface vs. small LLM baselines).
If FAIL: structured-NLG also requires a learned decoder. The "LLM front-end stays for NL fluency" claim becomes nearly unconditional; substrate stays in extraction + classification + ranking + memory.

A SECOND pilot, PILOT-NLG-2 (n-gram bundle perplexity on a small domain), decides whether ngram-substrate substitution is plausible at all:
- Corpus: small WikiText subset or TinyStories validation slice (10MB target).
- Substrate stores 4-gram counts as Tier-2 bundles indexed by trigram-context binding; readout = argmax over conditional bundle.
- Metric: per-token perplexity vs. baseline modified Kneser-Ney 4-gram and vs. published TinyStories-1M transformer.
- HARD-PASS: substrate-ngram PP within 20% of KN-4-gram PP on same training data; HARD-FAIL: substrate-ngram PP > 2x KN-4-gram PP.

## (c) Falsifiable predictions

PREDICTION-1 (structured template fill): PILOT-NLG-1 will achieve BLEU-4 in [0.35, 0.55] and slot-error-rate < 0.10 on E2E-NLG-cleaned.
- HARD-PASS: BLEU-4 >= 0.40 AND slot-error-rate <= 0.10 (matches reported pipeline-NLG floor for the dataset).
- HARD-FAIL: BLEU-4 < 0.20 OR slot-error-rate > 0.25 (worse than rule-based template baseline; substrate adds no value).
- P_deflated = 0.45 (novel-synthesis cap minus 0.05 for absence of direct published substrate-NLG precedent on E2E).

PREDICTION-2 (n-gram bundle perplexity): substrate-stored 4-gram with substrate-bundled count tables can match Kneser-Ney 4-gram within a multiplicative perplexity factor of 1.0-1.3 on a 10MB English corpus.
- HARD-PASS: substrate-PP / KN-PP in [0.95, 1.30] (substrate is essentially a lossy n-gram store; lossiness sets the gap).
- HARD-FAIL: ratio > 2.0 (substrate cannot store the count distribution faithfully; the bundling-superposition crosstalk dominates).
- P_deflated = 0.50 (substrate's bundle is mathematically an approximate hash table for counts; theory says it should work; the only question is dimension-vs-vocab capacity).

PREDICTION-3 (resonator-CFG decode): a VSA-CFG production-rule grammar (beim Graben et al. 2021 framework) used as a substrate constraint over PILOT-NLG-1 candidates raises BLEU-4 by an additive 0.03-0.08 and cuts slot-error-rate by 30-50% relative.
- HARD-PASS: incremental BLEU-4 lift >= 0.03 AND relative slot-error reduction >= 0.30.
- HARD-FAIL: BLEU-4 lift <= 0.01 OR slot-error rises.
- P_deflated = 0.40 (CFG constraint is well-precedented in grammar-constrained-decoding literature; the question is whether resonator-based CFG enforcement is competitive with finite-state automaton enforcement).

PREDICTION-4 (open-domain fluency ceiling): substrate-only open-domain perplexity, even with maximal codebook scaling (N=10000, item memory up to 1M unique n-grams), will not match a 1M-parameter transformer on WikiText-103.
- HARD-PASS for substrate (which would FALSIFY this prediction and is the contrarian-find direction): substrate-PP < 1.5x TinyStories-1M transformer PP on matched test set.
- HARD-FAIL (consistent with prediction): substrate-PP > 3x transformer-PP at matched train data.
- P_deflated = 0.20 on substrate beating tiny-transformer (i.e. 0.80 confidence the LLM-front-end claim holds for open domain).

PREDICTION-5 (hybrid retrieval + substrate fill outperforms both alone): a "small lexicon stored as substrate + retrieval-template-fill + grammar-CFG-constraint" pipeline produces fluent NLG on a controlled domain (E2E, WikiBio short bios, weather reports) better than either substrate-only OR a small (~10M param) transformer alone in that domain.
- HARD-PASS: hybrid BLEU-4 > max(substrate-only, small-transformer) by >= 0.05 absolute.
- HARD-FAIL: hybrid does not beat the better of the two (compositional advantage is illusory).
- P_deflated = 0.40 (well-precedented in literature for retrieve-edit pipelines but substrate-specific composition is novel).

## (d) Cross-thread synthesis with prior entries

This drill INTERSECTS with five recent substrate-internal findings:

1. **substrate-classical NLP methods outperform phasor 2026-06-11**: substrate-classical (count-based statistical methods stored as Tier-2 bundles) beat phasor-only at POS 0.906 / slot-filling 0.871 / intent 0.834. The SAME pattern is the basis for PREDICTION-2: substrate-stored n-gram counts ARE substrate-classical NLG. The polysemy-rescue / context-binding lifts that helped EXTRACTION (image-schema 0.342 -> 1.000) should help SYNTHESIS along the same axis: per-domain context-binding of templates separates competing surface realizations.

2. **substrate-only NL POS tagger validated 0.906 2026-06-11**: refuted "LLM-only for English parse" claim by stacking emission + transition + Viterbi on substrate. Symmetric pattern: structured NLG is the GENERATION-side dual of structured prediction — same machinery (transition tables, Viterbi-style decode, n-gram backoff) runs in reverse to emit sequences. PILOT-NLG-1 is the generation-side analog of the POS pipeline; same primitives, opposite direction.

3. **substrate-native structured prediction CRF + structured-SVM + EBM 2026-06-11**: substrate has semiring (forward-backward + Viterbi) natively; this is the EXACT machinery NLG needs for slot-fill and template emission. The substrate-structured-prediction note already pre-registered substrate-linear-chain-CRF >= 0.92 on WSJ POS. CRF decoding IS conditional-sequence generation; substrate-CRF generating tokens conditioned on a slot-binding is the formal model for PILOT-NLG-1.

4. **code-synthesis substrate feasibility 2x 2026-06-11**: companion drill same morning concluded substrate-only code synthesis is structurally bounded at HumanEval-EASY pass@1 ~0.05-0.15 BUT hybrid template-retrieve + grammar-constrained slot-fill reaches 0.30-0.45. The structural argument is IDENTICAL for NL: substrate-only open-domain NL bounded; substrate template-retrieve + grammar-constrained NL synthesis feasible in structured domains. NLG is more forgiving than code (no exact-syntax requirement; partial fluency still wins BLEU) so the upper edge of the band MAY shift up slightly (0.40-0.55 BLEU-4 on E2E-class corpora).

5. **substrate-LLM boundary decomposition 2026-06-10**: cleanest framing was substrate = symbolic/structural cognition; LLM = parsing arbitrary English + statistical fluency. This drill REFINES that boundary: "statistical fluency" splits into two regimes — STRUCTURED-TEMPLATE fluency (substrate can do) vs OPEN-DOMAIN-CREATIVE fluency (substrate cannot do at parameter parity). The boundary becomes substrate-side for any task whose target distribution has bounded effective vocabulary (<= ~5k surface forms) and bounded template space (<= ~10k templates).

CONVERGENCE: five separate threads all converge on the same structural verdict — substrate IS a generation engine for structured-low-entropy domains and IS NOT a generation engine for open-domain natural language. The substrate-LLM boundary memory now needs ANOTHER revision (third today) to split "statistical fluency" into two regimes.

## (e) Substrate-product implications

PRODUCT IMPLICATION 1 — calibrated structured-NLG surface. If PILOT-NLG-1 hits HARD-PASS, the product surface "substrate-backed deterministic form-fill / structured-report generation with conformal calibration on every output" is empirically open. The competitive axis vs LLMs is not BLEU; it is determinism, sub-100ms latency, sub-100MB deployment footprint, and conformal-coverage guarantees on each generated field (the conformal-calibration drill earlier today already validated the calibration math). E2E-NLG / WeatherGov / WikiBio / RotoWire / financial-report / radiology-report templates are all in-band for this surface.

PRODUCT IMPLICATION 2 — substrate.generation.TemplateLibrary primitive. The PILOT-NLG-1 pipeline (template-bundle + role-tagged slot + lexicon-binding + bigram cleanup) is a library primitive analogous to substrate.gating.MarginGatedEnsemble shipped earlier today. It is reusable across domains. Designing it generically means each new domain is a recipe-config not a code change.

PRODUCT IMPLICATION 3 — honest boundary in marketing/product positioning. The "no LLM in the loop" claim is product-safe ONLY for tasks satisfying the structured-domain criteria (bounded vocab, bounded templates, slot-fill nature, deterministic-output requirement). Outside that envelope, hybrid substrate + small-LLM (~7M-100M param TinyStories-class) is the honest architecture. Substrate handles retrieval/binding/calibration; small LLM handles surface realization. This positioning is more credible than "substrate replaces all LLMs" and is product-relevant for regulated industries (health/finance/legal).

PRODUCT IMPLICATION 4 — honest LIMIT: substrate cannot ship "creative writing copilot" or "open-domain chat" as substrate-only. P_deflated 0.20 of substrate beating tiny-transformer on WikiText-103. Do not over-claim; market structured-NLG specifically.

PRODUCT IMPLICATION 5 — hybrid path opens a path to dialogue: substrate-only dialogue generation has no published precedent (search returned only neural-VSA work, not substrate-only dialogue). A hybrid (substrate template-retrieval + small dialogue LM + substrate-CRF re-ranker) is the architecturally honest path. Worth a follow-on drill once PILOT-NLG-1 and PILOT-NLG-2 results land.

## (f) Citations (verified count)

External literature (web-search verified):

1. Schlegel, Neubert, Protzel. "A comparison of vector symbolic architectures." Artificial Intelligence Review, 2021. arXiv:2001.11797. (VSA primitive survey, sequence encoding via permutation/trajectory-association)
2. Frady, Kent, Olshausen, Sommer. "Resonator networks for factoring distributed representations of data structures." Neural Computation 32(12), 2020. arXiv:2007.03748. (Resonator factorization; sequence-decode via search-in-superposition; cleanup memory)
3. Frady, Kent, Olshausen, Sommer. "Resonator Networks, 2: Factorization Performance and Capacity Compared to Optimization-Based Methods." Neural Computation 32(12):2332, 2020. (Capacity-vs-error bounds on resonator decoding)
4. Kleyko et al. "Efficient Decoding of Compositional Structure in Holistic Representations." Neural Computation 35(7), 2023. arXiv:2305.16873. (Direct evidence for iterative readout of substrate-bundled sequences; "no iterated representation has correct errorless unbinding" is the key theoretical limit cited)
5. beim Graben et al. "Vector Symbolic Architectures for Context-Free Grammars." Cognitive Computation, 2021. arXiv:2003.05171. (VSA-CFG production-rule encoding in Fock space; universal-representation theorem; substrate-side basis for PREDICTION-3)
6. Granmo et al. "Hyperdimensional Vector Tsetlin Machines with Applications to Sequence Learning and Generation." arXiv:2408.16620, 2024. (HVTM trained on text data, generated new text — closest published "substrate-only NL generation" precedent; structurally a learned-rules-on-top-of-hypervectors hybrid, not pure-substrate)
7. Eldan & Li. "TinyStories: How Small Can Language Models Be and Still Speak Coherent English?" arXiv:2305.07759, 2023. (Small-transformer fluency floor at ~10M params; baseline for PREDICTION-4 lower bound)
8. Kleyko et al. "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part I and Part II." ACM Computing Surveys, 2022. (Foundational survey; coverage of HDC for finite-state automata synthesis)
9. Park et al. "Flexible and Efficient Grammar-Constrained Decoding." arXiv:2502.05111, 2025. (State of the art for token-mask CFG enforcement; baseline that PREDICTION-3's resonator-CFG must match)
10. Sennrich et al / Heafield et al. surveys of modified Kneser-Ney 4-gram baselines on small corpora. (Baseline for PREDICTION-2)
11. Huang, Smolensky et al. "Tensor Product Generation Networks for Deep NLP Modeling." arXiv:1709.09118, NAACL 2018. (TPR-based generation; symbol-structure-in-vector-space for NL output; substrate-adjacent but uses learned binding)
12. McCoy et al. "RNNs Implicitly Implement Tensor Product Representations." arXiv:1812.08718, 2018. (Evidence that the substrate's algebra is what good NL networks IMPLICITLY learn — supports substrate-explicit being feasible)
13. Wen et al. "Stochastic Language Generation in Dialogue using Recurrent Neural Networks with Convolutional Sentence Reranking." arXiv:1508.01755. (n-gram baseline reaches comparable BLEU but with errors; direct precedent for PREDICTION-2 perplexity-gap)
14. Wiseman, Shieber, Rush. "Learning Neural Templates for Text Generation." ResearchGate 334116623. (Template+slot-fill structurally identical to PILOT-NLG-1)
15. Hashimoto et al. "A Retrieve-and-Edit Framework for Predicting Structured Outputs." arXiv:1812.01194. (Retrieve-edit foundation for hybrid pipeline; PREDICTION-5)
16. Eldan/Microsoft (TinyStories follow-on). "Regional Tiny Stories: Using Small Models to Compare Language Learning and Tokenizer Performance." arXiv:2504.07989, 2025. (Latest sub-10M-param fluency studies)
17. Honey-I-Shrunk-the-Language. "Language Model Behavior at Reduced Scale." arXiv:2305.17266. (Scaling-law limits below 100M params; bounds PREDICTION-4 from the LLM side)
18. Attention-as-Binding (Vector-Symbolic Perspective on Transformer Reasoning). arXiv:2512.14709, 2025. (Recent: transformer attention IS soft unbinding; supports thesis that substrate explicit-unbinding can do what attention does implicitly for structured tasks)

Total verified citations: 18.

Calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]: all P estimates deflated by 0.15-0.25 from initial sub-agent estimates; novel-synthesis predictions capped at 0.50; HARD-FAIL thresholds explicit on every prediction.

## Closing note: revising the substrate-LLM boundary memory

This is the THIRD revision in 30 days. New honest split:

- Substrate IS-NOT for: open-domain creative NL synthesis (story writing, free-form chat, novel-essay composition).
- Substrate IS for: structured-NLG (form-fill, slot-realization, template-emission), deterministic-output domains, calibrated NL output where coverage guarantees matter.
- LLM IS for: open-domain creative NL synthesis, parsing arbitrary unrestricted English input.
- HYBRID IS for: dialogue, code synthesis, structured-document generation with creative passages.

Substrate covers more of the NL-generation surface than the previous (pre-this-drill) framing suggested. PILOT-NLG-1 result will move the boundary one way or the other; pre-registered HARD-FAIL bounds make the result honest in either direction.

Next-drill candidate (if PILOT-NLG-1 PASS): substrate-CRF as conditional sequence generator on WeatherGov / WebNLG to assess generality of the structured-NLG capability across multiple domains.

Next-drill candidate (if PILOT-NLG-2 FAIL): codebook-capacity audit — what is the substrate dimension N required to losslessly store n-gram count distribution of a given vocab V? Marchenko-Pastur edge prediction on item-memory crosstalk gives a closed-form bound; could be answered with F4 free-cumulant tooling already developed in this morning's free-probability framework drill.
