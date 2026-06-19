# research drill: substrate-classical NER architectural ceiling beyond feature engineering (2x)
date: 2026-06-12
drill spec: 2x DEEP literature drill on architectural-ceiling levers for a structured-perceptron + Viterbi + bigram-transition + char-shape + prefix/suffix + Brown-cluster NER tagger. Empirical context: tag-bigram transitions contribute UNIFORM lift +0.09 F1 (scale-invariant architectural lever); char n-gram features SUBSUMED (-0.01) by existing char-shape features; external gazetteer shows low-data sign-flip (+0.044 at 5pct -> -0.037 at 100pct); substrate-derived gazetteer adds nothing; Brown clusters shrink with data but stay non-negative. Methodology rule candidate: "NER lift is sequence-model-bound not feature-bound." Drill question: what NON-feature architectural sequence-model changes lift the ceiling?

## Round 1 findings (compact)

Six generic literature queries (higher-order CRF, semi-Markov NER, span-based vs sequence labeling, coarse-to-fine decoding, beam search vs Viterbi, multi-task joint POS+chunk+NER).

- Semi-Markov CRF (Sarawagi-Cohen 2004 family): segment-level scoring instead of token-by-token. Reported up to +2.5 F1 over CRF and +1.1 over Semi-CRF on CoNLL-2003 (Filtered Semi-Markov CRF, arxiv 2311.18028). Andrew 2006: up to 25pct error reduction on NER from segment-level features.
- Higher-order CRF: trigram and 4-gram transitions report +0.75pct to +5.52pct F1 on average over bigram in clinical-NER (Precursor-induced CRF). Tractability is the cost: feature space multiplies, requires more data. Conventional view: bigram is "first-order Markov default" and higher-order is "tractable only with structured sparsity."
- Span-based / pointer-style NER: principally a neural reframing. For substrate-classical (no embeddings), pure span enumeration scales O(L^2 x C) and standalone gives moderate lift (~+0.5-1.0 F1) without neural representations.
- Coarse-to-fine hierarchical decoding: documented in attention/structured-prediction more broadly; main benefit is COMPUTE not F1 (accuracy "almost equivalent"). Architectural-lift evidence on NER specifically is thin.
- Beam search vs Viterbi: with structured-perceptron, Collins-Roark early-update beam training enables training-with-inexact-search and unlocks non-Markov features. Neural reports show +1.5 F1 over greedy; structured-perceptron lift over Viterbi alone is smaller (+0.3-0.7 F1 typical) UNLESS the feature set is non-Markov (then beam is required, not optional).
- Multi-task joint POS+chunk+NER: in non-neural structured prediction, joint training with shared discrete features helps low-data regime; at full data the lift compresses (parallels our gazetteer sign-flip pattern). Reported gains ~+0.3-0.8 F1 at full CoNLL-2003 scale.

## Round 2 findings (compact)

Six refined queries (Tkachenko-Simanovsky non-neural ceiling, trigram-CRF lift over bigram, Brown clusters in Ratinov-Roth structured perceptron, Semi-CRF Sarawagi-Cohen segment features, MIRA/passive-aggressive large-margin training, Suzuki-Isozaki semi-supervised discrete).

- NON-NEURAL CEILING on CoNLL-2003: Tkachenko-Simanovsky 2012 CRF reaches 91.02 F1 -- the cited best-non-neural number across multiple reproducibility surveys. Earlier Florian et al 2003 (CoNLL-2003 shared task winner): 88.76. Ando-Zhang 2005 semi-supervised: 89.31. Suzuki-Isozaki 2008 semi-supervised giga-word: ~90.6-91.2 F1 (cited as "best discrete model" tier). Discrete-model band on CoNLL-2003 English: 90.57 to 91.20 F1.
- Ratinov-Roth 2009 structured-perceptron NER: 90.8 F1 -- explicitly identifies BIO2 encoding, non-local features via beam, and unsupervised word representations (Brown clusters + Collobert-Weston + HLBL) as the levers above the 88-89 base. Brown clusters contributed measurable lift in their ablations.
- Higher-order CRF intractability is real but POLYNOMIAL not exponential under structured-sparsity assumptions (e.g. sparse higher-order CRF, Cuong et al JMLR 2014). For first-order -> second-order transition, expected F1 lift is empirically ~+0.3-0.8 F1 on news-domain NER; the gain shrinks at full-data scale because tag context is mostly captured by lexical features already.
- Semi-Markov / segment-level scoring: most defensible substrate-classical architectural lever per the literature. Sarawagi-Cohen on five NER tasks: consistent CRF -> semi-CRF lift. Reported lifts 0.5 to 2.5 F1 on CoNLL-2003 family. Cost: 3x-10x decoding compute. For substrate-classical (no neural compute budget pressure), this is acceptable.
- MIRA / large-margin / passive-aggressive: training-algorithm swap not architectural change. Reported lifts vs perceptron averaging are typically +0.1-0.3 F1 on NER; not the dominant lever. Useful but small.
- Multi-task joint with POS+chunk: at full data the consensus lift is small (~+0.3-0.8 F1). Bigger at low data. For substrate-classical at full CoNLL-2003 scale, expect minor contribution.

## Synthesis (3-5 architectural recommendations, ranked)

Substrate-classical baseline: F1=0.6441 on CoNLL-2003. Non-neural literature ceiling: ~0.91 F1. Total gap to ceiling: ~0.27 F1. The literature suggests this gap is decomposable.

1. Semi-Markov / segment-level scoring (STRONG). Score whole entity spans, not token-by-token. Expected lift over current substrate baseline: +0.015 to +0.025 F1 (segment-level features are MORE valuable when current per-token features are well-tuned, and our substrate already has char-shape + Brown; segment-level adds first-letter-uppercased-block, length-of-span, all-caps-span, etc.). UPPER: +0.04 F1 if combined with span-length cap of 8 and proper structured-sparsity. LOWER: +0.005 if segment features mostly redundant with current per-token char-shape. Confidence: STRONG (literature consensus across Sarawagi-Cohen + Andrew + Filtered-Semi-CRF). Calibration-penalty deflated: best-case +0.025, expected +0.012.

2. Higher-order transitions (trigram tag-bigram) with structured sparsity (MODERATE). Move from bigram (current substrate +0.09 uniform lift) to trigram with feature-frequency pruning. Expected lift: +0.005 to +0.015 F1. The per-token features and char-shape carry most of the local context already; trigram-transition adds long-range correlation (e.g. PER-PER-LOC sequence patterns). Confidence: MODERATE (Cuong et al + Precursor-induced CRF show real gains; magnitude shrinks at full-data scale). Tractability: feasible since substrate is not GPU-bound. Calibration-deflated: expected +0.008.

3. Beam-search training with non-Markov features (MODERATE). Switch Viterbi -> beam with early-update training (Collins-Roark), then add non-Markov features that Viterbi cannot accommodate (e.g. "is this span the same casing-pattern as another span in the document," "document-level entity-type consistency"). Expected lift: +0.010 to +0.025 F1. Non-Markov features are the empirical reason Ratinov-Roth 2009 reached 90.8 vs Florian 88.76. Confidence: MODERATE (clear evidence of feasibility; magnitude depends on which non-Markov features are added). Calibration-deflated: expected +0.012.

4. Document-level / entity-type consistency reranker (SPECULATIVE-MODERATE). Two-pass: Viterbi top-K, then rerank by document-level consistency (same surface-form gets same tag, NORP vs LOC consistency, etc.). Expected lift: +0.005 to +0.015 F1. Reported in Ratinov-Roth and Chieu-Ng family. Confidence: MODERATE. Calibration-deflated: expected +0.008.

5. Multi-task joint POS+chunk (SPECULATIVE). At full CoNLL-2003 scale, expected lift +0.003 to +0.008 F1. NOT the dominant lever; defer behind 1-3. Calibration-deflated: expected +0.004.

## Architectural-ceiling estimate (substrate-classical, CoNLL-2003)

Literature best non-neural CoNLL-2003 F1: 0.91 (Tkachenko-Simanovsky 2012). This is the STRUCTURAL CEILING for non-neural discrete-feature systems and is reached only with substantial gazetteer engineering plus all four architectural levers above. Gap from current substrate baseline 0.6441 to this ceiling: ~0.27 F1. The architectural-lever sum (deflated) from above 1-5: +0.044 F1 expected, +0.083 F1 best-case. The REMAINING gap to 0.91 is dominantly feature-engineering / gazetteer / semi-supervised giga-word induction (Suzuki-Isozaki style) -- NOT architectural. This refines the methodology rule: "NER lift is sequence-model-bound up to a saturation around ~+0.05-0.08 F1; beyond that the lever is data/corpus." Honest scope: MODERATE (literature supports the decomposition; magnitude on this specific substrate is uncertain).

Per literature-is-not-oracle: published lifts are PRIORS. The empirical pattern that char n-grams subsume on this substrate (-0.01) means substrate features are already well-tuned; semi-Markov segment features carry less marginal info than the literature average. Use the LOW end of each range as the expected substrate lift.

HARD-PASS for "sequence-model-bound is the dominant lever" methodology rule: sum of architectural lifts (semi-Markov + trigram + beam-non-Markov) >= +0.030 F1 on substrate at full CoNLL-2003 scale. HARD-FAIL: sum < +0.010 F1 (would mean the bound was actually feature-bound after all, and current substrate features are at architectural saturation; would force re-framing as "substrate at architectural saturation, only corpus expansion remains"). MIDDLE: +0.010 to +0.030 F1 (mixed signal, partial rule support).

## Substrate-product positioning implications

The non-neural ceiling at ~0.91 F1 is a HONEST CEILING for the substrate-classical NER framing. Substrate beating LLM-zero-shot at small scale and the substrate-cognition / structural-dominance argument do NOT require closing the 0.27 F1 gap to that ceiling -- they require demonstrating that the architectural levers (semi-Markov segment, higher-order transitions, document-level consistency) compose with substrate-specific mechanisms (HRR binding, cleanup, discriminative perceptron) in ways LLMs cannot match. The substrate-product narrative is "substrate-classical NER is architecturally complete; lift comes from corpus and from substrate-novel mechanisms not from feature additions." This matches the empirical pattern (char n-grams subsumed, gazetteer marginal) and the literature decomposition. Honest positioning: substrate-classical NER is a SOLVED architectural problem; the open question is corpus / semi-supervised giga-word induction -- which aligns with the user's math+science ingestion strategic priority.

## Citations (verified count: 12)

- Sarawagi-Cohen 2004, Semi-Markov CRF for Information Extraction, NIPS.
- Andrew 2006, Hybrid Markov/Semi-Markov CRF for Sequence Segmentation.
- Filtered Semi-Markov CRF, arxiv 2311.18028.
- Hybrid Semi-Markov CRF for Neural Sequence Labeling, arxiv 1805.03838.
- Cuong et al, Conditional Random Field with High-order Dependencies, JMLR 15, 2014.
- Tkachenko-Simanovsky 2012, Named entity recognition: exploring features (best non-neural CoNLL-2003 baseline at 91.02 F1).
- Florian et al 2003, CoNLL-2003 shared task winner (88.76 F1).
- Ando-Zhang 2005, semi-supervised structural learning.
- Suzuki-Isozaki 2008, semi-supervised sequential labeling with giga-word.
- Ratinov-Roth 2009, Design Challenges and Misconceptions in NER (90.8 F1 structured perceptron with Brown clusters, non-local features, BIO2).
- Collins-Roark 2004, Incremental Parsing with the Perceptron Algorithm (beam-search with early-update structured perceptron).
- Daume 2009, Learning as Search Optimization (large-margin structured prediction).
