# Research Drill: Hallucination Order-Sensitivity -- Close the 0.702->0.85+ Gap (2x Level-2 Operational)
Date: 2026-06-06
Level: 2x operational (deepening KF-1 to KF-4 prior findings; NOT re-verification)

---

## HEADLINE

Word-level bigram augmentation of MiniLM is the cheapest, fastest path to close the 0.702->0.85+ gap on word-shuffle adversarial, because it directly fixes the root cause (BoW encoder cannot see order) without requiring a causal LM. Pythia fine-tuning on order-sensitive contrastive objectives is the highest-ceiling option and the recommended production path. Combined (Pythia residuals + word bigram) late fusion is the insurance policy.

---

## Cheap Decisive Test

Word-level bigram TF-IDF vector, cosine-scored against query bigrams, concatenated with existing MiniLM 384-dim embedding. Binary classifier (logistic regression or light MLP) on the concatenated 384+V_bigram vector, evaluated at AUC on the word-shuffle adversarial set. If AUC crosses 0.75 in this cheap setup, the architectural hypothesis (word n-grams DO capture order disruption) is confirmed and investment in the full Pythia fine-tune is justified.

Compute cost: CPU-only, <2 min. Vocabulary size V_bigram approximately 50k-200k (document-level, moderate corpus). No GPU required for smoke.

---

## Sub-question (1): Closing the 0.702 -> 0.85+ Gap -- Algebraic Analysis

### Background

Pythia-160m on word-shuffled adversarial: AUC = 0.702. HP gate = 0.85.
Gap to close: delta_AUC = 0.148.

Pythia-160m is a causal (autoregressive) LM; its residual stream at layer L encodes positional history via causal masking. MiniLM is bidirectional but effectively BoW (75-90% of BERT predictions unchanged under word shuffle; confirmed by arXiv:2012.15180). Pythia's causal masking IS the right architectural inductive bias -- the 0.702 baseline confirms this direction.

### Option A: Scale to Pythia-410m or Pythia-1b

Algebraic argument:
Let AUC(M) = AUC_inf - c / log(M) where M = model parameters, c is architecture-dependent constant.
Fitting two points: AUC(160m) = 0.702, saturated regime AUC_inf ~ 0.90 (ceiling from encoder capacity + task ceiling):
  c / log(160e6) = 0.90 - 0.702 = 0.198
  c = 0.198 * log(160e6) = 0.198 * 18.89 = 3.74
  AUC(410m) = 0.90 - 3.74/log(410e6) = 0.90 - 3.74/19.83 = 0.90 - 0.189 = 0.711
  AUC(1b) = 0.90 - 3.74/log(1e9) = 0.90 - 3.74/20.72 = 0.90 - 0.181 = 0.719

CRITICAL: This is a log-linear scaling argument. It suggests MARGINAL gains from size alone (0.702 -> ~0.72 at 1b). Size scaling with frozen weights is NOT the gap closer.

Calibration note: log-linear AUC-vs-log(M) is empirically observed for tasks where architecture is right and data/objective is fixed. The 0.702 plateau may be primarily a frozen-weights limitation, not a capacity limitation.

P_deflated (size-alone closes gap to 0.85): 0.12 (low; size without fine-tune unlikely to close full gap)

### Option B: Layer Choice -- Deeper Layers More Order-Sensitive

Causal transformer residual stream: earlier layers encode local syntax; deeper layers encode longer-range dependencies and positional history. For a causal LM, layer L residual encodes prefix context h_L(t) = sum_i=0^t alpha_{L,i,t} * v_{L,i} where the attention weights alpha_{L,i,t} are causally masked.

Empirical observation from LLM circuit analysis (arXiv:2407.10827): attention head functions are consistent across scale and training. Early layers (L < 4 for 160m): local bigram structure. Middle layers (L = 6-10): syntactic phrases, multi-token dependencies. Last layers (L > 10): high-level sequence semantics.

For WORD SHUFFLE adversarial, the disruption signal is STRONGEST at:
- Middle layers: local phrase structure is broken (bigrams disrupted)
- Last layer: sequence-level coherence is broken

Prediction: mean of [middle, last] layer residuals > last layer alone, by approximately 0.03-0.07 AUC.

Multi-layer concatenation formula:
AUC([L_mid, L_last]) >= max(AUC(L_mid), AUC(L_last)) + delta_ensemble
where delta_ensemble in [0.02, 0.08] from orthogonal information in different layers.

P_deflated (layer selection closes gap 0.702->0.78): 0.45
P_deflated (layer selection alone crosses 0.85): 0.18

### Option C: Fine-tune Pythia-160m on Hallucination Detection Objective

This is the highest-leverage option. Current setup uses frozen Pythia residuals. Fine-tuning on order-sensitive contrastive objective directly trains the model to discriminate word-shuffle adversarials.

Hard negative contrastive objective:
L = -log[ exp(sim(h(x), h(x+)) / tau) / sum_j exp(sim(h(x), h(x_j-)) / tau) ]
where x+ = semantically faithful continuation, x- = word-shuffled adversarial (hard negative).

arXiv:2403.11082 (RobustSentEmbed) shows adversarial self-supervised contrastive learning on BERT achieves highest average Spearman correlation (+1.59% over second-best). The key mechanism: hard negatives derived from adversarial perturbations teach the encoder to be sensitive to exactly the disrupted structure.

AUC prediction for fine-tuned Pythia-160m with order-sensitive hard negatives:
Starting from 0.702 frozen baseline, contrastive fine-tuning on N=5k-10k (x, x_shuffled) pairs:
Expected lift: 0.10-0.18 AUC from hard-negative fine-tuning (from RobustSentEmbed + adversarial contrastive literature).
Predicted AUC after fine-tune: 0.702 + [0.10, 0.18] = [0.80, 0.88]

P_deflated (fine-tune Pythia-160m crosses 0.85): 0.38 (cap at 0.50 novel synthesis; 0.45 - 0.07 calibration penalty = 0.38)

### Option D: Inject Positional Information from Query Pre-encoder

Substrate-specific variant: encode positional signal explicitly (e.g., learned absolute position embeddings from query concatenated with candidate, fed as extra token). This is analogous to "position-augmented input" rather than architecture change.

Algebraic argument: if the classifier sees explicit positional order of tokens in query, it has a reference against which to detect word-shuffle. But this requires knowing the "canonical order" which may not be available in production.

P_deflated: 0.22 (requires privileged access to ordered reference; may not generalize to semantic paraphrase attacks)

### Sub-question (1) Cell: Option C + B Combined

CELL: pythia_fine_tune_order_sensitive_n1
Anchor: Pythia-160m fine-tuned with order-sensitive contrastive hard negatives + multi-layer [mid, last] concatenation
Architecture: mean(residuals at layers {8, 11}) -> 768-dim -> binary head
Objective: contrastive with word-shuffle as hard negative, temperature tau=0.05
Training N: 5k-10k (x, x_shuffle) pairs
Smoke test: 100 pairs, confirm loss decreases monotonically
Full test: word-shuffle adversarial AUC

HARD-PASS: AUC >= 0.85 on word-shuffle adversarial
MID-BAND: AUC in [0.75, 0.85)
HARD-FAIL: AUC < 0.72 (no improvement over frozen baseline)

P_deflated: 0.38
Next-drill if MID-BAND: extend to Pythia-410m + same fine-tune objective

---

## Sub-question (2): Word-Level N-gram Architecture (G11 Root-Cause Fix)

### Root Cause Analysis

Char n-grams FAILED (ADV=0.192) because: char n-grams are intra-word; word-shuffle preserves all char n-grams; the adversarial cannot be detected at char level. This is algebraically certain, not probabilistic.

Word-level bigrams WOULD detect word-shuffle:
Given tokens [t_1, t_2, ..., t_n], word-bigrams = {(t_i, t_{i+1}) for i in 1..n-1}.
Word-shuffle permutes the sequence. Unless the shuffle happens to preserve all adjacent pairs (probability (n-1)!/n! = 1/n for any specific bigram), bigrams CHANGE.

For a uniformly random shuffle of n=50 tokens:
Expected fraction of bigrams preserved = (n-1) * (1/(n-1)) * (1/n) * n = 1/n ~ 0.02 for n=50.

So approximately 98% of word bigrams are disrupted by uniform word-shuffle. The MiniLM+bigram architecture can DETECT this disruption by comparing the bigram distribution of the candidate to the bigram distribution of the reference (query or expected answer).

### Architecture

MiniLM_384 + WordBigram_V:
Feature vector = [MiniLM(x); tfidf_bigram(x)]
where tfidf_bigram(x) is the TF-IDF vector over word-bigrams, dim V_bigram.

Cosine similarity scoring: sim = dot(f(x_query), f(x_candidate)) / (||f(x_query)|| * ||f(x_candidate)||)
Or: binary classifier on the concatenated [f(x_query); f(x_candidate); f(x_query) - f(x_candidate)] vector.

V_bigram estimation: for a 50k token vocabulary, V_bigram = 50k^2 = 2.5B (too large). In practice, use observed bigrams in training corpus: typically 100k-500k distinct bigrams (long tail cut at min_df=5). Dimension manageable (100k-500k sparse).

### AUC Prediction for Word-Shuffle Adversarial

For EASY negatives: MiniLM alone achieves 0.999. Bigrams add minimal signal (easy negatives are already detectable by semantics).

For HARD word-shuffle adversarial: MiniLM alone = 0.217 (near-random). Bigram alone:
- If query and candidate share domain: bigram overlap from same-domain vocabulary is high even after shuffle
- The SIGNAL is: shuffled text has DIFFERENT bigram sequence from query; but both may share similar VOCABULARY (same words, different order)
- Bigram cosine similarity: (num shared bigrams) / sqrt(num_bigrams_query * num_bigrams_candidate)
  
For shuffled vs correct: shared bigrams ~ 2% of total (from above analysis). Bigram cosine ~ 0.02-0.10.
For same-domain hard negative (different sentence, similar vocab): shared bigrams ~ 10-30%.
For correct match: shared bigrams ~ 90-100%.

This gives clean separation between correct vs shuffled on bigram cosine alone. Predicted AUC of bigram-cosine feature alone on word-shuffle adversarial: 0.80-0.92.

Combined MiniLM + bigram:
AUC_combined >= max(AUC_MiniLM=0.217, AUC_bigram~0.86) + delta_ensemble
AUC_combined ~ [0.86, 0.93] (pessimistic to optimistic)

CELL: minilm_word_bigram_concat_n1
Anchor: MiniLM 384 + word bigram TF-IDF, cosine scorer
Architecture: f(x) = [MiniLM(x) / ||MiniLM(x)||; tfidf_bigram(x) / ||tfidf_bigram(x)||], L2-normalized and concatenated
Scorer: logistic regression on [f(query) - f(candidate)] or cosine of f(query) dot f(candidate)
Training: 0 (unsupervised) or light LR on labeled pairs

HARD-PASS: AUC >= 0.85 on word-shuffle adversarial
MID-BAND: AUC in [0.72, 0.85)
HARD-FAIL: AUC < 0.65 (bigrams uninformative; vocabulary overlap dominates)

P_deflated: 0.52 (algebraically grounded; calibration cap at 0.50 for novel synthesis)
NOTE: capped at 0.52 because the algebraic argument is tight but domain vocabulary overlap is a genuine failure mode; production corpus may have high bigram overlap from same-domain hard negatives.

---

## Sub-question (3): Hybrid Pythia + Word Bigram Late Fusion

### Algebraic Argument

Two classifiers with scores s_1 (Pythia residuals, AUC_1) and s_2 (word bigram, AUC_2).
Late fusion: s_fused = alpha * s_1 + (1-alpha) * s_2.

For uncorrelated errors, the fused AUC is:
AUC_fused >= max(AUC_1, AUC_2)  [always, by ensemble lower bound]

More precisely, for error vectors e_1 and e_2 with correlation rho:
AUC_fused ~ AUC_1 + (AUC_2 - AUC_1) * (1 - rho) / 2  [approximate, assuming symmetry]

Are Pythia and bigram errors correlated?
Pythia (AUC=0.702): fails when word-shuffle produces a sequence whose AUTOREGRESSIVE perplexity is similar to the original (i.e., shuffled text by chance has reasonable bigram/trigram language model probability).
Bigram TF-IDF (AUC~0.86): fails when shuffled text has high bigram vocabulary overlap with query (same-domain hard negatives).

These are DIFFERENT failure modes. A shuffled text that fools Pythia (plausible language model score) is unlikely to also fool bigram-TF-IDF (requires preserved bigram order). Correlation rho ~ 0.2-0.4 (moderate, not high).

AUC_fused prediction (Pythia=0.702, Bigram=0.86, rho=0.3):
AUC_fused >= 0.86 + (0.86-0.702) * (1-0.3) / 2 = 0.86 + 0.158 * 0.35 = 0.86 + 0.055 = 0.915 (optimistic)
Conservative: 0.86 + 0.04 = 0.900

Combined prediction: AUC in [0.88, 0.92].

If Pythia is fine-tuned (AUC_1 rises to ~0.84), fusion with bigram (AUC_2~0.86) gives:
AUC_fused ~ 0.90-0.94.

CELL: hybrid_pythia_bigram_fusion_n1
Anchor: Pythia-160m residuals (frozen) + word bigram TF-IDF, late fusion alpha=0.4/0.6 sweep
Architecture: logistic regression on [pythia_score; bigram_score] features
Fusion sweep: alpha in {0.2, 0.4, 0.6, 0.8} on validation set
Training: calibrate alpha only (2 param fit); no deep training required

HARD-PASS: AUC >= 0.88 on word-shuffle adversarial
MID-BAND: AUC in [0.80, 0.88)
HARD-FAIL: AUC < 0.75 (fusion not helping; errors correlated)

P_deflated: 0.42 (calibration penalty applied; ensemble algebra is sound but rho estimate uncertain)

---

## Sub-question (4): Adversarial Diversity Matrix

### Attack Taxonomy

The production audit moat must handle attack diversity beyond word-shuffle. Known attack classes:

| Attack type | Mechanism | Bigram robust? | Pythia robust? | Notes |
|---|---|---|---|---|
| Word shuffle | uniform random permutation | YES (bigrams destroyed) | YES (partial) | KF-2,3 confirmed |
| Token reverse | reverse token sequence | YES (bigrams reversed) | PARTIAL | reversal preserves token set |
| Phrase-level shuffle | permute N-word chunks | PARTIAL (cross-chunk bigrams) | PARTIAL | depends on chunk size |
| Sentence-level reorder | permute sentences in doc | PARTIAL (cross-sentence) | WEAK | sentence = coherent unit |
| Subword reorder | shuffle subwords within word | NO (char-level) | NO | both fail here |
| Semantic paraphrase | LLM paraphrase, meaning preserved | NO | PARTIAL | hardest attack |
| Synonym substitution | word-level replacement | PARTIAL | PARTIAL | vocab shift |

Key insight from RAID benchmark (arXiv:2405.07940): paraphrase attacks (T5-11B-based) are the hardest for semantic detectors. Number shuffling and word-level attacks are easier. Adjacent word swap (a weaker form of word shuffle) is included in RAID.

Semantic paraphrase is the HARD CASE for both architectures:
- Bigram TF-IDF: paraphrase changes vocabulary -> different bigrams -> bigram similarity drops; but paraphrase is VALID (should be accepted). Creates false positives.
- Pythia residuals: paraphrase aligns with language model prior -> low disruption signal.

RECOMMENDATION: Adversarial diversity sweep should test:
1. Word shuffle (current) -- baseline
2. Phrase-level shuffle (chunk size 3, 5, 10 words)
3. Token reverse
4. Semantic paraphrase (from a SEPARATE paraphrase model; need to flag separately as it may require human evaluation)

The sweep disambiguates whether word-bigrams are sufficient or whether an order-sensitive encoder is REQUIRED for the full attack surface.

CELL: adversarial_diversity_sweep_n1
Anchor: run existing detectors (MiniLM, Pythia-160m frozen, MiniLM+Bigram) across 4 attack types
Architecture: detection matrix: rows=attack type, columns=detector, cells=AUC
HARD-PASS: MiniLM+Bigram AUC >= 0.75 across ALL 4 attack types (robustness claim)
MID-BAND: AUC >= 0.75 on >=3/4 attack types
HARD-FAIL: AUC < 0.65 on any non-paraphrase attack (indicates architectural gap)

P_deflated: 0.30 (sweep is purely diagnostic; hard to predict which attack exposes new gap)

---

## Sub-question (5): Production Deployment Recommendation

### Recommended Architecture for Phase 4 Audit Moat

TIER 1 (immediate, cheap): MiniLM-384 + Word Bigram TF-IDF late fusion
- Deploy: MiniLM for semantic, bigram for order
- Cost: <1ms inference (bigram is sparse dot product); ~50MB index
- Expected AUC on word-shuffle: 0.85-0.92
- Expected AUC on phrase-shuffle: 0.70-0.80
- Expected AUC on semantic paraphrase: 0.60-0.75 (weakness; acceptable for audit moat)
- Recommended for: Phase 4 v1 audit moat baseline

TIER 2 (medium term, 1-2 engineering days): Pythia-160m fine-tuned on order-sensitive hard negatives
- Add to Tier 1 as late-fusion component
- Cost: fine-tune ~30min on 5k pairs (CPU or GPU); inference ~10ms (residual extraction)
- Expected AUC on word-shuffle: 0.85-0.88 (fine-tune alone) or 0.90+ (fused with bigram)
- Recommended for: Phase 4 v2 hardened audit moat

TIER 3 (exploratory): Pythia-410m or larger, full fine-tune
- Cost: 1-2h GPU fine-tune; ~30ms inference
- Expected AUC uplift over Tier 2: +0.02-0.05 (marginal; size scaling is log-linear, not linear)
- Only justified if Tier 2 plateaus below 0.88

DEPLOYMENT ORDERING (by ROI):
1. CELL minilm_word_bigram_concat_n1 -- smoke in <2min CPU
2. CELL hybrid_pythia_bigram_fusion_n1 -- if (1) passes smoke, 30-min run
3. CELL pythia_fine_tune_order_sensitive_n1 -- if Phase 4 requires >0.88 hardened
4. CELL adversarial_diversity_sweep_n1 -- runs all above across attack types

---

## Falsifiable Predictions: HARD-PASS / HARD-FAIL Summary

| Cell | HARD-PASS | MID-BAND | HARD-FAIL | P_deflated |
|---|---|---|---|---|
| minilm_word_bigram_concat_n1 | AUC >= 0.85 | [0.72, 0.85) | < 0.65 | 0.50 |
| hybrid_pythia_bigram_fusion_n1 | AUC >= 0.88 | [0.80, 0.88) | < 0.75 | 0.42 |
| pythia_fine_tune_order_sensitive_n1 | AUC >= 0.85 | [0.75, 0.85) | < 0.72 | 0.38 |
| adversarial_diversity_sweep_n1 | AUC >= 0.75 all attacks | >= 0.75 on 3/4 | < 0.65 any non-paraphrase | 0.30 |

Pre-registered hard-fail implications:
- If minilm_word_bigram HARD-FAILS (AUC < 0.65): vocabulary overlap between shuffled and correct answers dominates; need to use discriminative bigram (not frequency-based) or switch to positional embedding approach.
- If hybrid fusion HARD-FAILS (AUC < 0.75): Pythia and bigram errors ARE correlated (rho > 0.7); fusion adds no value; must go to fine-tune.
- If pythia_fine_tune HARD-FAILS (AUC < 0.72): contrastive fine-tune with order-sensitive negatives does not increase sensitivity; architecture needs reconsideration (causal LM not the right inductive bias at 160m scale).

---

## Cross-Thread Synthesis

KF-1 (AUC=0.999 easy, 0.975 hard domain negatives): the semantic signal is strong for the MiniLM use case. Word-shuffle adversarial is a SEPARATE threat model, not a generalization failure of the existing approach.

The CORRECT framing: the audit moat has two security layers:
- Layer 1: semantic hallucination (MiniLM handles, AUC=0.975-0.999)
- Layer 2: order-sensitive adversarial attack (word-shuffle, phrase-shuffle; requires bigram or causal LM)

Both layers are needed for production. Layer 2 is the current gap.

The char n-gram failure (KF-4, ADV=0.192) is algebraically certain (char n-grams are order-insensitive at word level). Word bigrams are the minimal fix. Pythia is the principled fix.

Connection to substrate: the hallucination detector is part of the Phase 4 audit moat infrastructure. The KF-1 capability (AUC=0.999) is a production-grade signal. Closing the order-sensitivity gap to 0.85+ activates the full adversarial-robust audit moat row in the capability map.

---

## Substrate-Product Implications

1. The audit moat capability row (Cap K-F1) is currently partially activated: semantic hallucination detection is production-grade (AUC=0.975-0.999); adversarial order-sensitivity is below HP gate (AUC=0.702). The gap is closeable with 1-2 engineering days of work (word bigram augmentation + optional Pythia fine-tune).

2. Word bigram augmentation is ZERO additional model cost at inference: sparse TF-IDF dot product, <1ms. This is the correct first ship target. It activates adversarial-robust detection for the word-shuffle threat class at negligible cost.

3. The semantic paraphrase attack (hardest attack class) is NOT addressed by either word-bigram or Pythia causal LM. This is an open gap for Phase 4 v3. Paraphrase detection requires a dedicated reference-grounded comparison (entailment model or NLI). This should be flagged as a separate capability row.

4. Adversarial diversity sweep should be run BEFORE production deployment to confirm the word-bigram approach does not produce excessive false positives on VALID paraphrases (which change vocabulary and bigram distribution).

---

## Citations (Verified)

1. arXiv:2012.15180 "Out of Order: How Important Is The Sequential Order of Words in a Sentence in NLU Tasks?" -- confirms 75-90% of BERT predictions unchanged under word shuffle; bidirectional transformers are bag-of-words; key lit-scan grounding for why MiniLM fails at 0.217.

2. arXiv:2403.11082 "RobustSentEmbed: Robust Sentence Embeddings Using Adversarial Self-Supervised Contrastive Learning" -- adversarial contrastive fine-tuning on BERT achieves +1.59% avg Spearman; hard negative mining is key mechanism; grounds the fine-tune objective for Cell pythia_fine_tune_order_sensitive_n1.

3. arXiv:2509.05360 "Beyond ROUGE: N-Gram Subspace Features for LLM Hallucination Detection" -- N-gram frequency tensor with tensor decomposition for hallucination detection; competitive vs ROUGE/BERTScore/LLM-judge; confirms n-gram approaches are active research direction for hallucination.

4. arXiv:2405.07940 "RAID: A Shared Benchmark for Robust Evaluation of Machine-Generated Text Detectors" -- 11 attack types including word shuffling, paraphrase (T5-11B), homoglyph; documents robustness failure modes across detector architectures; grounds adversarial diversity taxonomy.

5. arXiv:2407.10827 "LLM Circuit Analyses Are Consistent Across Training and Scale" -- attention head functions consistent across scale; supports layer-depth analysis for where order information lives in causal LM residual stream.

6. ResearchGate: "Document Similarity Using TF-IDF and Cosine Similarity" -- bigram representation achieves 93.6% document similarity accuracy; false predictions occur for similar vocabulary but different semantics (the production failure mode to test for).

7. arXiv:2203.01677 "Detection of Word Adversarial Examples in Text Classification" -- BERT/RoBERTa AUC 67-97 range on word adversarial attacks depending on detection method; establishes AUC as correct evaluation metric for this task class.

Verified citation count: 7

---

## Next-Drill Candidate

Sub-question (4) + adversarial diversity sweep should run BEFORE OR IN PARALLEL with the fine-tune cell, to determine whether the 0.85 HP gate needs to hold across all attack types (not just word-shuffle). If phrase-shuffle exposes a new gap, the fine-tune training set needs to include phrase-shuffle negatives, not just word-shuffle negatives.

Next-drill field: adversarial-robustness (NLP) -- how does adversarial diversity change the fine-tune objective for order-sensitive contrastive training?
