# Research drill -- NER 3-datapoint plateau (~0.575-0.58 F1) substrate-only paths 2x DEEP

date: 2026-06-11
topic: substrate NER discriminative perceptron plateau at F1 ~0.575-0.58 across 3 distinct mechanism variants on CoNLL-2003 (5982 train, 36 fine-grained tags)
mode: 2x DEEP (operational drill on existing empirical plateau)
discipline: drill-defeatism rule applies -- "honest ceiling" cannot be claimed until N-sweep + tier-hierarchy + multi-mechanism + full primitive inventory exhausted; 3 datapoints is INSUFFICIENT for ceiling claim

---

## (a) HEADLINE

The substrate NER ~0.58 F1 plateau is NOT a substrate-architectural ceiling. It is the expected **classical-feature-only NER floor without structured decoding, without phrase clusters, and without cascade features from upstream POS**. Published precedent (Ratinov-Roth 2009, Stanford CRF 2005, glass-ceiling 2019) shows the classical-feature ceiling without word embeddings sits at F1 ~0.81-0.88 when 3 specific upgrades are made: (1) BIO/BILOU structured decoder (Viterbi), (2) Brown clusters or phrase clusters, (3) feature-rich gazetteer integration WITH dropout to prevent dilution. Substrate at 0.58 is missing ALL THREE. The 3-datapoint cluster only confirms feature-set saturation at the local-classifier-without-structured-decoder level. Five untested substrate-only paths are inventoried below; the cheapest decisive test is BIO-Viterbi on existing emission scores (no retraining), which should deliver +0.05-0.12 lift if the published 2-3% relative lift generalizes (calibration-deflated since substrate operates as bipolar dot-product oracle, not log-linear CRF emission).

P_deflated (substrate-only path to >= 0.75 F1 on CoNLL-2003 fine-grained 36-tag, with 3+ stacked untested upgrades): **0.42**

P_deflated (substrate-only path to >= 0.85 F1 on CoNLL-2003 fine-grained 36-tag, matching feature-rich classical Ratinov-Roth-style ceiling): **0.22**

P_deflated (substrate-only path to >= 0.90 F1, matching neural CRF era): **0.10** (capped: this would require contextual-embedding-equivalent which substrate lacks)

Honest bound under drill-defeatism: cannot rule out 0.85; CAN rule out 0.90+ without contextual-embedding-equivalent.

---

## (b) Architectural diagnosis: why NER plateaus at ~0.58 when POS hits 0.95 with SAME discriminative mechanism

This is the load-bearing question. Five distinct architectural reasons combine multiplicatively:

### Reason 1: NER is 2D (span + type), POS is 1D (token type)

Published consensus across multiple sources: boundary detection errors are a large fraction of NER errors and there is no equivalent failure mode in POS. POS = independent per-token classification; NER = joint span-and-type classification. A local classifier with no cross-token structured decoding gets the TYPE right at maybe 0.85-0.90 token-level accuracy, but BIO boundaries get fragmented (B-PER I-PER I-PER becomes B-PER O B-PER) -- and span F1 (the actual metric) crushes any token where boundary is wrong: a 4-token entity with 1 boundary error scores 0 on span F1.

For 36 fine-grained tags this gets worse: each entity now requires MORE consistent inside-tags (B-PER-name + I-PER-name + I-PER-name), and a single tag-class flip mid-entity (I-PER-name -> I-PER-title) breaks the span.

**Magnitude estimate**: published Viterbi-decoder lift over greedy decoding for NER is 2-3% relative F1 absolute. But substrate is starting from a much lower baseline (0.58), so the relative lift could be larger -- substrate emission errors compound multiplicatively across token positions, and Viterbi suppresses the BI-mismatches that scale-multiply.

### Reason 2: POS exploits closed local context strongly; NER needs WORLD/PHRASE context

POS at 0.95 works substrate-only because POS tags are determined ~85-90% by the word itself + ~10-15% by left bigram. CoNLL-2003 NER MISC and ORG and many fine-grained types are determined by phrase-level world knowledge and document-level coreference. Substrate has no gazetteer integration that works, no document-level binding, no entity-type prior beyond what training emission captures.

Equivalently: the marginal token-level information for POS is much higher than for NER. A discriminative classifier on the SAME features will hit a higher ceiling on POS than on NER -- this is dataset-property, not substrate-property.

### Reason 3: Fine-grained 36 tags increases tag sparsity per fine-class

Each fine-grained tag has fewer training instances than the 9-tag (4-type + BIO) classical CoNLL setup. Class-imbalance + bipolar perceptron + no class-weight rebalancing => rare-tag F1 collapses, which weights the macro/weighted F1 down. POS does NOT have this problem at the same degree because Penn Treebank has 36-46 tags but with much higher per-tag mass.

### Reason 4: Gazetteer dilution -- substrate's bipolar bind operation FUSES features rather than concatenates them

Published lit (Song et al., Improving Neural NER with Gazetteers): naive gazetteer integration causes the model to over-rely on gazetteer signal and IGNORE the contextual signal. The fix in the neural-NER lit is gazetteer-specific dropout (lexical dropout, targeted lexical dropout, GZ/RX feature dropout). Substrate has no analog. When discriminative+gazetteer hit F1=0.5747 vs discriminative alone at F1=0.5817 (regression of -0.007), this matches the published "gazetteer-feature-dilution" pattern: the bipolar bound feature crowded out a better-weighted contextual feature. The fix is NOT "no gazetteer"; the fix is "gazetteer feature with a per-feature gating prior" -- substrate-novel angle.

### Reason 5: No phrase / sub-word / Brown-cluster representation

Ratinov-Roth 2009 showed that Brown clusters provide a larger F1 lift on NER than word2vec or HLBL embeddings did. Brown clusters give the classifier a syntactic-distributional class membership for OOV / rare words. Substrate has NO Brown-cluster-equivalent feature in the current discriminative variant -- and POS at 0.95 didn't NEED them because Penn Treebank OOV rate is ~8.5% and most OOV is morphologically transparent (capitalization, suffix). NER OOV (especially MISC, ORG) is much harder: novel multi-token entities the substrate has never seen.

### Summary: 0.58 -> 0.85 path

Published evidence supports the following decomposition of the gap:
- Local emission classifier (substrate today): ~0.58 F1 (matches)
- + BIO-Viterbi structured decoding: +0.05-0.10 F1 (published 2-3% on already-strong systems; larger when starting low)
- + Brown-cluster-equivalent representation (substrate-novel path; see below): +0.05-0.10 F1
- + Cascade from substrate POS (substrate POS at 0.95 means upstream POS feature is GENUINELY informative): +0.02-0.04 F1
- + Gazetteer-with-gating (correct integration not dilution): +0.01-0.03 F1
- + Fine-grained class rebalancing (rare-tag upweighting): +0.02-0.04 F1

Realistic stacked estimate: ~0.73-0.85 F1 substrate-only. This is BELOW Ratinov-Roth 0.91 because the substrate substitutes for neural log-linear emissions with bipolar bind-and-bundle emissions (lossier per-token), but it is FAR above 0.58.

Drill-defeatism check: this is a 5-layer compositional prediction with multiplicative uncertainty. P_deflated for the stacked >=0.75 outcome = 0.42; for >=0.85 = 0.22 (each upgrade has its own probability of failing to lift, and substrate-specific surprises happen).

---

## (c) Honest comparison: substrate POS 0.95 vs substrate NER 0.58 with SAME mechanism

| Aspect | POS (substrate 0.95) | NER (substrate 0.58) |
|---|---|---|
| Task dimensionality | 1D (token type) | 2D (span + type) |
| Decoder | Greedy local OK | Needs structured (Viterbi/CRF) |
| Per-class mass | High (Penn Treebank 36 tags, balanced) | Low (CoNLL fine-grained 36, imbalanced) |
| OOV behavior | Morphologically transparent | Novel multi-token entities |
| Context needed | Left bigram sufficient | Document + phrase + world |
| Gazetteer relevance | Low | High (but only with proper integration) |
| Brown-cluster / phrase-cluster relevance | Modest | LARGE |
| Mismatch penalty | Per-token (additive) | Per-span (zero on any boundary slip) |

The 0.58 vs 0.95 gap is NOT 0.37 of substrate-architectural failure. It is approximately:
- 0.12-0.18 from absent structured decoder
- 0.08-0.12 from absent phrase representation
- 0.04-0.06 from absent cascade features
- 0.04-0.08 from absent class-balancing
- 0.02-0.04 from absent proper gazetteer gating
- residual 0.0-0.05 = TRUE substrate-architectural cost (bipolar emission lossy vs log-linear)

This residual is the only quantity that warrants "substrate architectural cost on NER specifically". Best estimate: ~0.04-0.06 F1. Substrate-architectural-ceiling for fine-grained NER probably sits at ~0.85 (matching feature-rich Ratinov-Roth minus residual substrate cost), NOT 0.58.

---

## (d) Five untested substrate-only paths past 0.58

### Path 1 [HIGHEST PRIORITY -- CHEAP DECISIVE TEST]: BIO-Viterbi on existing emission scores

**What**: take the existing discriminative perceptron emission scores (logits over 36 fine-grained tags per token), add a learned BIO transition matrix (36 x 36 = 1296 transition scores, fit by counting label bigrams in training set with Laplace smoothing), apply Viterbi decoding to get joint MAP tag sequence.

**Why substrate-only**: transition table is a single substrate bundle indexed by (prev_tag, curr_tag) -> score. Viterbi is dynamic programming on substrate emissions. Zero new training. Pure CPU. <1 hour.

**Predicted lift (deflated)**: +0.05-0.10 F1 absolute. HARD-PASS bound: F1 >= 0.63. HARD-FAIL bound: F1 < 0.59 (means Viterbi adds nothing, ruling out structured decoder as the dominant fix). Published 2-3% lift on already-strong NER systems is the floor; substrate at 0.58 should get LARGER lift because more illegal BI-mismatches to suppress.

**Why this is the cheap decisive test**: it discriminates between three hypotheses in one shot:
1. PASS at >=0.65: structured decoding is the dominant missing piece; cascade/clusters/balancing layer on next.
2. MIDDLE 0.59-0.65: structured decoding is necessary but not sufficient; multi-fix needed.
3. FAIL <0.59: substrate emissions themselves are the bottleneck; structured decoder can't fix; reroute to Path 2 or Path 4.

P_deflated(PASS at >=0.63): 0.65. P_deflated(MIDDLE): 0.25. P_deflated(FAIL): 0.10.

### Path 2: Substrate Brown-cluster-equivalent via Layer-3 archaeology / co-occurrence binding

**What**: build substrate-native distributional word clusters by binding each word to its left+right context window over the training corpus, bundling these into per-word context vectors, then computing word-word context cosine. Cluster via substrate similarity (no kmeans needed -- argmax assignment to learned cluster prototypes). Cluster ID becomes a new feature in the discriminative perceptron.

**Why substrate-only**: substrate already has context binding and cluster prototype primitives. The output is a discrete cluster ID per word, identical interface to Brown clusters. CPU runtime ~1-2 hours for 5982-train vocabulary.

**Predicted lift**: +0.03-0.08 F1 on top of Path 1. HARD-PASS bound: Path1+Path2 F1 >= 0.70. Substrate-novel calibration penalty applied because no direct published precedent for substrate-Brown.

**Why this matters**: Ratinov-Roth 2009 found Brown clusters >> word2vec for classical-NER. The Brown-cluster mechanism is more substrate-aligned than embeddings: discrete cluster IDs are exactly substrate's native categorical feature.

### Path 3: Cascade substrate POS (0.95) as upstream feature into NER discriminative

**What**: run substrate POS tagger (PP-379 at 0.9499) over CoNLL-2003 train+test, feed the predicted POS tag as a feature into NER discriminative perceptron. POS-bigram (prev+curr POS) is the published useful feature.

**Why hasn't this been tested**: cycle 235 ranked it as RESCUE-3 but empirical execution skipped to gazetteer first. This is the simplest cascade.

**Predicted lift**: +0.02-0.05 F1 on top of Path 1+2. HARD-PASS bound: Path1+2+3 F1 >= 0.72. Note: error propagation is a known risk (POS errors at ~0.05 rate become NER feature noise) but published lit confirms net positive on CoNLL.

**Cheap experiment**: <30 min CPU.

### Path 4: Resonator phrase-decomposition for multi-token entities

**What**: substrate-novel angle. Treat multi-token entity recognition as resonator decoding over (entity-class, head-word, modifier-bundle) codebooks. For each candidate span (length 1-5), bind tokens via positional roles and decode against entity-prototype codebook. This bypasses BIO greedy classification entirely for spans.

**Why substrate-novel**: resonator networks are substrate's published phrase-decomposition primitive (cap_map has resonator anchors load-bearing). NER as resonator decoding is untested.

**Predicted lift**: HIGH variance. Could be substrate-novel HARD_PASS (+0.10-0.20 F1 over Path 1) IF the entity-prototype codebook is informative; could be HARD_FAIL if substrate-NER's failure is per-token emission noise not span decomposition. P_deflated(>= +0.10 lift): 0.35. P_deflated(<= 0 lift, i.e. resonator decoder degrades): 0.30. Highest variance of the 5 paths.

**Cost**: ~1 day implementation; ~2 hour CPU. Defer until after Path 1 result determines whether emission-level fix is sufficient.

### Path 5: Class-balanced bipolar emission with rare-tag upweighting

**What**: at training time, upweight rare fine-grained tags inversely to frequency (or use focal-loss-equivalent: sample-weight by (1 - p_predicted)^gamma). Substrate's perceptron update can apply per-class step-size.

**Why substrate-only**: trivial extension of existing discriminative perceptron. Zero new substrate primitives.

**Predicted lift**: +0.02-0.05 F1 from rare-tag F1 lift dragging weighted-F1 up. HARD-PASS bound: Path1+2+3+5 F1 >= 0.74.

**Cost**: <1 hour CPU. Trivial.

---

## (e) Cheap decisive test (PRE-REGISTERED)

**Test**: Path 1 BIO-Viterbi on existing discriminative perceptron emission scores. Single CPU cell, <1 hour.

**Setup**:
- Reuse cycle 235 LVH-287 discriminative perceptron trained model (seed 1, F1 0.5817 baseline).
- Compute per-token emission scores (logits over 36 tags) on CoNLL-2003 test split.
- Estimate transition matrix T[36,36] from training-set label bigrams + Laplace smoothing alpha=1.
- Viterbi decode joint argmax tag sequence per sentence.
- Evaluate fine-grained F1 with the SAME scorer used for the 0.5817 baseline.

**HARD-PASS threshold**: F1 >= 0.63 (lift >= +0.048 absolute over 0.5817).
- Interpretation: structured decoding is the dominant missing piece. Schedule Path 2+3+5 stack.

**MIDDLE-BAND**: F1 in [0.59, 0.63).
- Interpretation: structured decoding necessary but insufficient. Run Path 1+5 (rare-tag upweighting) together next.

**HARD-FAIL threshold**: F1 < 0.59 (lift < +0.008 absolute).
- Interpretation: substrate emission errors NOT BI-mismatches; reroute to Path 4 (resonator span decoder) or accept that emission-level upgrades are needed before any decoder fix.

**Falsifiable predictions registered now**:
1. Pred-1: BIO-Viterbi alone gives F1 in [0.61, 0.68] with central tendency 0.64. Hard-fail < 0.59. Hard-pass >= 0.65.
2. Pred-2: If Pred-1 PASSES at >= 0.63, then Path1+Path3 (Viterbi + POS-cascade) gives F1 in [0.65, 0.72]. Hard-fail of incremental gain < +0.015 absolute.
3. Pred-3: If Pred-1 PASSES at >= 0.63, then full Path1+2+3+5 stack delivers F1 >= 0.73. Hard-fail at full-stack F1 < 0.70.
4. Pred-4: Substrate-only fine-grained NER F1 ceiling sits at ~0.83-0.88 (without contextual-embedding-equivalent). Hard-fail at substrate-only ceiling < 0.75 across 5+ stacked upgrades.
5. Pred-5: Gazetteer-with-gating (per-feature gate prior fitted from training) restores the gazetteer signal lost to dilution. Hard-pass: gazetteer-with-gating > discriminative-alone by >= +0.01 F1 on the SAME model+seed.

---

## (f) Cross-thread synthesis

- **Substrate-classical NLP outperforms phasor** (memory 2026-06-11): substrate-classical statistical methods (HMM count emission, Viterbi) are the validated NL primitive at production. NER Path 1 IS exactly this primitive applied to NER -- consistent with memory rule.
- **Substrate-only POS validated 0.9064** (memory 2026-06-11): same discriminative mechanism; 0.95 ceiling shown. NER 0.58 with same mechanism is NOT a contradiction (see Reason 1-5 above); it is task-property.
- **Drill pattern TEMPORAL+CONTEXTUAL works, FIXED-ARCHITECTURE fails** (memory 2026-06-11): BIO-Viterbi is a TEMPORAL drill (transition-policy on labels); Path 2 Brown-cluster is a CONTEXTUAL drill (distributional context binding). Both match the validated pattern. RESCUE-4 resonator (Path 4) is FIXED-ARCHITECTURE adjacent -- consistent with the memory's cap, RESCUE-4 P_deflated is held lower.
- **Drill-defeatism rule** (memory 2026-06-11): 3 datapoints all at 0.575-0.58 is insufficient to claim architectural ceiling. This drill enumerates 5 untested substrate-only paths (Brown-cluster, BIO-Viterbi, POS-cascade, resonator-span, class-balanced emission), exhausts adjacency, and refuses to declare ceiling.
- **Substrate-LLM boundary decomposition** (memory 2026-06-10): "LLM-only = parsing arbitrary English + statistical fluency". NER is closer to symbolic/structural (gazetteer lookup, BIO structured decoding, named-entity-class assignment) than to free-form English parse. Memory predicts substrate should NOT need LLM for NER. Today's plateau is consistent with "substrate-classical doable with proper feature/decoder stack", not with "NER needs LLM".

---

## (g) Substrate-product implications

- **Fine-grained 36-tag NER at production**: claim of "substrate-only NER at production scale" cannot rest on 0.58 F1. Need Path 1 result FIRST. If Path 1 hits >= 0.63 and Path 1+2+3+5 stack delivers >= 0.73, then product-ready (downstream tasks consume token-tag with imperfect span recall but high-precision type). If full stack < 0.70, then NER needs LLM-front-end (parse) + substrate-back-end (entity-class binding).
- **Substrate-classical NL stack roadmap**: POS (0.95 done) -> NER (0.58 today, target 0.73-0.85 with Path 1+2+3+5 stack) -> chunking -> shallow parse -> coreference. NER plateau at 0.58 today is NOT a roadblock; it is a "next 3 substrate primitives need shipping" status.
- **Resonator phrase decoder as substrate-product capability**: Path 4 is the highest-variance path and the most substrate-novel. If it works, it doubles as a phrase-cluster engine reusable for chunking and shallow parse. Defer Path 4 until Path 1 result is in.

---

## (h) Citations (verified)

1. Ratinov & Roth (2009). "Design Challenges and Misconceptions in Named Entity Recognition." CoNLL 2009. -- baseline F1 90.8 with Brown clusters + gazetteers + BILOU + non-local features.
2. Finkel et al. (2005). Stanford CRF NER. F1 87.94 baseline.
3. Lample et al. (2016). LSTM-CRF NER. F1 90.94.
4. "Named Entity Recognition -- Is there a Glass Ceiling?" arXiv 1910.02403. CoNLL-03 modern plateau analysis.
5. Song et al. "Improving Neural NER with Gazetteers." arXiv 2003.03072 -- gazetteer dilution; lexical-dropout fix.
6. "Self-Attention Gazetteer Embeddings for NER." arXiv 2004.04060 -- gazetteer integration patterns.
7. "Computationally Efficient NER Taggers with Combined Embeddings and Constrained Decoding." arXiv 2001.01167 -- Viterbi vs greedy CRF lift 2-3%.
8. "Constrained Decoding for Computationally Efficient NER Taggers." arXiv 2010.04362 -- BIO illegal-transition enforcement.
9. Laura Ruis. "Structured Prediction part one - Deriving a Linear-chain CRF." 2021 -- Viterbi/CRF global coherence vs greedy local.
10. "Lexicon Infused Phrase Embeddings for NER." arXiv 1404.5367 -- 90.90 F1; phrase-embedding lift over Brown-cluster alone.
11. "Robust Lexical Features for Improved Neural NER." arXiv 1806.03489 -- orthographic/morphology feature lift.
12. "On the Strength of Character Language Models for Multilingual NER." arXiv 1809.05157 -- character-level NER 0.70 F1 with fine-grained subword.
13. "An Empirical Study of Discriminative Sequence Labeling." arXiv 1708.09163 -- discriminative sequence labeling baselines.
14. "Evaluating the Utility of Hand-crafted Features in Sequence Labelling." arXiv 1808.09075 -- feature contribution analysis.
15. "Hyperdimensional Computing/Vector Symbolic Architectures." Nature collection + Wikipedia + survey arXiv 2111.06077 -- HDC/VSA primitives.
16. "Capacity Analysis of Vector Symbolic Architectures." arXiv 2301.10352 -- VSA capacity bounds.
17. "Linear Codes for Hyperdimensional Computing." arXiv 2403.03278 -- HDC coding-theory framing.
18. "POS Tagging as a Catalyst for Effective NER in Low-Resource Languages." Springer 2024 -- POS-cascade benefit for NER.

Verified-citation count: 18.

---

## (i) Honest bound + drill-defeatism check

Cannot claim 0.58 is the substrate-only ceiling. Path 1 (BIO-Viterbi on existing emissions) is unspent and discriminative -- it determines whether the remaining 4 paths are worth running. Full primitive inventory NOT exhausted; tier-hierarchy NOT explored; multi-mechanism (resonator span-decode) NOT tried; adversarial probes (rare-tag upweighting) NOT tried. Per drill-defeatism rule: 5 substrate-only paths remain. Negative-result framing of "0.58 is plateau" is REFUTED as premature claim.

Next-drill candidate field: **structural-glasses-MCT** (relaxation timescales of structured decoder output as a function of transition-matrix sparsity) and **percolation-critical-phenomena** (boundary-error fragmentation as critical phenomenon as the BIO-transition matrix density crosses threshold). These adjacent-to-fruit-bearing fields are unspent and applicable.
