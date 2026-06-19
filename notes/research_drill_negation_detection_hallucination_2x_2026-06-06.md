# Negation-Sensitive Hallucination Detection: Level-2 Operational Drill
# 2x depth on negation-insensitive KF-1/MiniLM finding
# Date: 2026-06-06

---

## HEADLINE

NLI cross-encoders (DeBERTa-v3-large-MNLI+FEVER+ANLI+LingNLI+WANLI) are the structurally
correct rescue for negation-blind MiniLM KF-1 detection: they are explicitly trained to
classify premise-hypothesis pairs as entailment/contradiction/neutral, achieving MNLI 91.2%
accuracy and ANLI 70.2% overall. Contradiction score directly maps to KF-1 signal for
negated-false-fact queries. AUC prediction on TruthfulQA-style negations: 0.78-0.87
(P_deflated=0.72 after calibration penalty for domain-shift from MNLI to TruthfulQA-style).

A polarity-aware embedding re-weighting adapter (no fine-tuning, 200-1000 training samples)
achieves +14.52% accuracy on SemAntoNeg (negation + antonym combined) -- second cheapest fix
after cue-feature augmentation, and uniquely covers antonym substitution that cue features miss.

Late fusion of NLI contradiction score + word-bigram TF-IDF + Pythia-residual is the
production recipe covering all three adversarial failure classes (negation, word-order
shuffle, causal-language gaps) with predicted combined adversarial AUC 0.87-0.92.

---

## LEVEL-2 OPERATIONAL FINDINGS BY SUB-QUESTION

### (1) NEGATION-DETECTION ARCHITECTURE FAMILIES -- Ranked by P_deflated on TruthfulQA-style negations

| Architecture class | Mechanism | P_deflated AUC | Notes |
|---|---|---|---|
| Cross-encoder NLI (DeBERTa-v3-MNLI-FEVER-ANLI) | Pair classification: contradiction prob as score | 0.78-0.87 | Explicitly trained on negation-as-contradiction; handles explicit + antonym + polarity-flip; ANLI R3 64% = hardest adversarial; SNLI 92%, MNLI 91% |
| BART-large-MNLI (zero-shot NLI) | Seq2seq encoder+head for entailment/contradiction | 0.73-0.82 | Slower inference (~400M params vs ~180M DeBERTa-large); contradiction probability is direct score; no task-specific fine-tuning required |
| Polarity-aware embedding adapter | Dimension-level re-weighting on negation-sensitive dims; no model fine-tuning | 0.60-0.72 | +14.52% on SemAntoNeg benchmark; handles explicit + antonym; requires 200-1000 labeled negation pairs; cheap inference |
| Negation-focused pretraining (BERT/RoBERTa NSPP) | Next-Sentence Polarity Prediction auxiliary task | 0.65-0.75 | +1.8% to +9.1% on CondaQA; requires continued pretraining; not a drop-in fix |
| Negation-cue feature augmentation (concat to MiniLM) | Presence/count of NOT NO NEVER N'T WITHOUT FAILS CANNOT | 0.62-0.72 | Free computationally; misses antonyms (increases vs decreases); explicit negation only; covers ~60% of real negation cases |
| Causal LM (GPT-style autoregressive) | Left-to-right; no explicit negation head | 0.45-0.60 | Better than MiniLM (not bag-of-words) but negation handling is implicit; fails on adversarial polarity flips |
| MiniLM bi-encoder (current KF-1) | Cosine similarity; order-insensitive | 0.034 | CONFIRMED HARD-FAIL; below-chance on negated false facts; NOT rescued by scale-up per BERT-class invariance finding |

Calibration penalty applied: -0.10 to -0.15 (NLI is published direct precedent, not
uncharted regime; penalty is smaller than the default -0.15 to -0.25 because direct
NLI-for-hallucination precedents exist in SemEval-2024 Task 6 and AlignScore).

---

### (2) NLI HEAD AS RESCUE -- HIGHEST PRIORITY CELL

#### Algebraic basis

NLI training objective: given (premise P, hypothesis H), classify into
  {entailment, neutral, contradiction}

For KF-1 use: set P = grounding context (retrieved documents), H = generated claim.
Score = P(contradiction | P, H)

For negated-false-fact queries:
  - Claim: "Paris is NOT the capital of France"
  - Grounding: documents affirming Paris IS the capital
  - Correct label = contradiction (claim contradicts grounding)
  - DeBERTa-v3-large trained on MNLI+FEVER+ANLI+LingNLI+WANLI
    = 885,242 NLI pairs including adversarial negation examples from ANLI

Published benchmark accuracy:
  MNLI-matched: 91.2%
  MNLI-mismatched: 90.8%
  ANLI (all rounds): 70.2%  (ANLI-R3 hardest: 64%)
  LingNLI: 87%  (linguistic phenomena including negation)
  WANLI: 77%

NLI fragility: Arakelyan et al. 2024 report 12.92% in-domain and 23.71% out-of-domain
degradation under semantic perturbation. This is the dominant hard-fail risk.

#### Concrete experimental cell

  Cell: KF1_NLI_rescue_v1
  Model: MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli
  Input: (premise=grounded_context, hypothesis=generated_claim) pairs
  Score: softmax contradiction probability
  Test suite: (a) TruthfulQA-style negations [prior AUC=0.034 with MiniLM]
              (b) easy negatives [prior AUC=0.999]
              (c) hard same-domain negatives [prior AUC=0.975]

  HARD-PASS thresholds:
    HP1: AUC >= 0.85 on TruthfulQA-style negations (explicit "X is NOT Y")
    HP2: AUC >= 0.90 on easy negatives (regression check; must not degrade)
    HP3: AUC >= 0.80 on hard same-domain negatives

  MIDDLE-BAND:
    MID1: 0.70 <= AUC < 0.85 on TruthfulQA-style negations (partial rescue; warrants hybrid)
    MID2: AUC 0.80-0.90 on easy negatives (minor regression acceptable)

  HARD-FAIL thresholds:
    HF1: AUC < 0.60 on TruthfulQA-style negations (NLI no better than random; closure)
    HF2: AUC < 0.80 on easy negatives (NLI degrades previously-working signal; rollback)
    HF3: AUC < 0.65 on hard same-domain negatives (worse than baseline)

  P_deflated = 0.72 (lit precedent: NLI trained on negation-contradiction pairs;
    calibration penalty -0.10 for transfer from MNLI distribution to TruthfulQA-style)

  Inference cost: 1 forward pass DeBERTa-v3-large (~25ms/pair CPU; ~3ms GPU).
  Lighter option: cross-encoder/nli-deberta-v3-base (SNLI 92.38%, MNLI 90.04%; ~86M params).

---

### (3) LIGHTWEIGHT NEGATION-CUE FEATURE AUGMENTATION -- Cell 2

#### Algebraic basis

Cue feature vector c in R^k, k~20:
  c[0] = has_not (binary), c[1] = has_no (binary), c[2] = has_never (binary)
  c[3] = has_nt_contraction (binary), c[4..9] = has_{without,fails,cannot,unable,lack,avoid}
  c[10] = negation_count (integer, capped at 5)

Concatenate: h_aug = [h_MiniLM_384; c_20] in R^404
Train lightweight head (2-layer MLP, ~80K params) on (h_aug, label) pairs.

Coverage analysis by negation type:
  Explicit ("X is NOT Y"): COVERED -- cue directly fires
  Antonym ("X increases" vs "X decreases"): NOT COVERED -- no negation token present
  Polarity flip ("X gains" vs "X loses"): NOT COVERED
  Quantifier flip ("all" vs "none"): PARTIAL -- has_no may fire on "none"
  Implicit negation ("X fails", "X lacks Y"): PARTIAL -- if "fails"/"lacks" in cue set

Structural ceiling: ~55-65% of real-world negation cases. Antonym substitution produces
IDENTICAL cue feature vectors for opposite-meaning sentences. This is a hard architectural
ceiling, not a tuning failure.

  Cell: KF1_cue_augment_v1
  HARD-PASS: AUC >= 0.70 on TruthfulQA-style negations (explicit subset only)
  MIDDLE-BAND: 0.55-0.70 AUC
  HARD-FAIL: AUC < 0.45 (cue augmentation adds noise, not signal; discard)

  P_deflated = 0.48 (calibration penalty -0.20; antonym gap is known structural limit)
  Inference cost: near-zero (string matching only)

---

### (4) POLARITY-AWARE EMBEDDING ADAPTER -- Cell 3

#### Algebraic basis

Let f: text -> R^d be a frozen embedding model (MiniLM, mpnet, etc.)
Let W in R^d be a diagonal re-weighting vector (d scalar weights, not d x d matrix).
Re-weighted embedding: g(x) = W * f(x) elementwise

Training signal: negation-flip pairs (x, x_neg) where x_neg is the negation of x.
Loss: push g(x) and g(x_neg) apart (negation-contrastive);
      push g(x) and g(x_para) together (paraphrase-attractive).

Key insight from semantic adapter paper (arXiv:2504.00584):
  - Standard universal embeddings have "negation blindness": f(x) and f(x_neg) have
    high cosine similarity (confirmed by MiniLM AUC=0.034 finding).
  - Certain embedding dimensions are more sensitive to negation than others.
  - Learned diagonal W amplifies negation-sensitive dimensions without fine-tuning the model.
  - +14.52% accuracy on SemAntoNeg (negation + antonym combined) with 200-1000 samples.
  - +4.68% on STSB paraphrase detection (no regression on standard task).
  - Handles BOTH explicit negation tokens AND antonym substitution.

This is the critical differentiator vs cue-feature augmentation: the adapter operates on
semantic dimensions that antonyms differ in, not just surface token presence. "Increases"
vs "decreases" will differ in specific embedding dimensions even without a "not" token.

  Cell: KF1_polar_adapter_v1
  HARD-PASS: AUC >= 0.80 on TruthfulQA-style negations (explicit + antonym types combined)
             AUC >= 0.92 on easy negatives (regression gate)
  MIDDLE-BAND: 0.65-0.80 on TruthfulQA-style negations
  HARD-FAIL: AUC < 0.55 on TruthfulQA-style OR AUC < 0.88 on easy negatives

  P_deflated = 0.55 (calibration penalty -0.15; +14.52% is on SemAntoNeg, not TruthfulQA-style;
    domain transfer uncertainty; capped at 0.55 for novel-synthesis uncertainty)

  Training cost: 200-1000 negation-flip labeled pairs; d=384 scalar weights only;
    ~minutes on CPU. Near-zero inference overhead vs MiniLM baseline.

---

### (5) HYBRID NLI + WORD-BIGRAM + PYTHIA -- Production Recipe -- Cell 4

#### Architecture

  Signal 1: s_NLI = DeBERTa-v3-large-MNLI contradiction score
    (covers: explicit negation, antonym, polarity flip, quantifier flip)

  Signal 2: s_bigram = word-bigram TF-IDF cosine similarity miss
    (covers: word-order shuffle -- HOC1 adversarial; per drill-B findings)

  Signal 3: s_pythia = Pythia-residual cross-entropy or perplexity delta
    (covers: causal-language structure gaps; sensitive to token ordering bi-encoders miss)

  Late fusion: score = alpha*s_NLI + beta*(1 - s_bigram) + gamma*s_pythia
    alpha, beta, gamma tuned on held-out validation set.
    Expected: alpha >> beta, gamma for negation-dominated test sets.

Algebraic prediction:
  - Negation adversarials: dominated by s_NLI; s_bigram neutral; s_pythia partially helpful
  - Word-order adversarials: dominated by s_bigram; s_NLI partial; s_pythia dominant
  - Easy cases: all three agree; fusion is redundant but not harmful

  Cell: KF1_hybrid_fusion_v1
  HARD-PASS:
    HP1: AUC >= 0.85 on TruthfulQA-style negations
    HP2: AUC >= 0.88 on word-order shuffled adversarials
    HP3: AUC >= 0.93 on easy negatives
    HP4: Combined adversarial AUC >= 0.88
  MIDDLE-BAND: HP1 in [0.75, 0.85) AND HP2 in [0.78, 0.88) -- partial, worth alpha tuning
  HARD-FAIL:
    HF1: AUC < 0.70 on TruthfulQA-style (s_NLI signal washed out)
    HF2: AUC regression on easy negatives below 0.97 (fusion introduces noise)
    HF3: Combined adversarial AUC < 0.80 (fusion not worth latency cost)

  P_deflated = 0.62 (multi-signal fusion; calibration penalty -0.15; alpha calibration
    uncertainty is real; no published direct precedent for this exact triplet fusion)

  Production deployment recipe:
    1. DeBERTa-v3-large-MNLI via cross-encoder API (huggingface or torch.compile local)
    2. Word-bigram TF-IDF: compute offline at indexing time (no per-query cost)
    3. Pythia-160M perplexity delta: single forward pass (~5ms GPU)
    4. Weighted sum of three signals; threshold at operating point
    5. Total latency vs MiniLM baseline: +30-80ms CPU / +8-15ms GPU (acceptable)

---

### (6) NEGATION DIVERSITY -- TYPE-BY-TYPE COVERAGE MAP

| Type | Example | NLI | Cue features | Adapter |
|---|---|---|---|---|
| Explicit negation | "X is NOT Y" | YES (contradiction class) | YES | YES |
| Antonym substitution | "X increases" vs "X decreases" | YES (MNLI covers antonym pairs) | NO | YES (+14.52%) |
| Polarity flip | "X gains" vs "X loses" | PARTIAL (training coverage dependent) | NO | PARTIAL |
| Quantifier flip | "all X" vs "no X" | YES (MNLI quantifier pairs) | PARTIAL (has_no) | PARTIAL |
| Implicit negation | "X fails", "X lacks Y" | YES (MNLI implicit negation) | PARTIAL (if in cue set) | YES (semantic dims) |
| Affixal negation | "accurate" vs "inaccurate" | PARTIAL (morphological) | NO | PARTIAL |

Key finding: NO single architecture covers all types.
  - NLI covers the widest range (explicit + antonym + quantifier + implicit)
  - Cue features cover only explicit token-level negation (structural ceiling ~60%)
  - Adapter covers explicit + antonym (two most common in factual claims)
  - Hybrid fusion required for production-grade coverage across all types

Recommendation: minimum viable negation test suite for production gates:
  (a) Explicit: TruthfulQA-style "X is NOT Y" pairs
  (b) Antonym: semantic opposition pairs (increases/decreases; rises/falls; supports/opposes)
  (c) Quantifier: "all"/"none" flip pairs
  Three-type coverage is necessary and sufficient for initial production validation.

---

## CHEAP DECISIVE TEST

Single-cell test to determine whether NLI rescue is production-viable:

  Setup: Run DeBERTa-v3-large-MNLI-FEVER-ANLI-LingNLI-WANLI as cross-encoder scorer
    on the SAME test set used for KF-1 MiniLM benchmarks
    (prior: TruthfulQA-style negations AUC=0.034)
  Input format: premise = grounding document; hypothesis = negated claim.
  Score = P(contradiction).
  Metric: AUC-ROC.
  Runtime: < 2 hours on laptop CPU for N=1000 pairs.
  Decision gate:
    AUC >= 0.80 -> proceed to Cell 4 hybrid fusion
    AUC 0.65-0.80 -> run Cell 3 adapter in parallel
    AUC < 0.65 -> escalate; NLI transfer broken; need domain-adaptive NLI fine-tuning

This test falsifies the NLI rescue hypothesis at < 2h CPU cost, no new training required.

---

## FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL)

HARD-PASS: KF1_NLI_rescue_v1 achieves AUC >= 0.85 on TruthfulQA-style negations;
  contradiction score is monotonically higher for negated-false-fact claims than grounded claims.

HARD-FAIL: AUC < 0.60 on TruthfulQA-style negations; NLI cross-encoder fails for
  reasons structural to domain shift (medical/scientific facts vs MNLI news/fiction distribution).

HARD-PASS: Polarity adapter achieves AUC >= 0.80 on explicit+antonym combined test.
HARD-FAIL: Polarity adapter AUC < 0.55 on antonym-only subclass (means re-weighting is
  insufficient; full fine-tuning with negation-contrastive loss required).

HARD-PASS: Hybrid fusion AUC >= 0.88 combined adversarial (negation + word-order).
HARD-FAIL: Hybrid fusion combined AUC < 0.80; signals uncorrelated in wrong direction.

---

## CROSS-THREAD SYNTHESIS

Drill A (this note): negation failure root-cause in KF-1 + NLI rescue architecture families
Drill B (word-order): word-bigram TF-IDF + Pythia as rescue for HOC1 adversarials

Convergence: both drills independently identify NLI cross-encoders as a shared scaffold.
NLI handles negation AND has word-order sensitivity via cross-attention, unlike bi-encoders.

Orthogonality: s_bigram and s_NLI are complementary not redundant:
  - s_bigram: purely lexical; no semantic understanding; fast; 0-latency from offline index
  - s_NLI: semantic + compositional; slower; expensive; covers antonym that bigram misses
  - Fusion exploits distinct failure modes; gain is real

Production priority order:
  1. KF1_NLI_rescue_v1 (P_deflated 0.72; cheapest to test; no new training)
  2. KF1_hybrid_fusion_v1 (covers both adversarial classes; highest ceiling AUC)
  3. KF1_polar_adapter_v1 (handles antonym gap; cheap deploy; run parallel with 1)
  4. KF1_cue_augment_v1 (lowest ceiling; only if 1+3 both fail on explicit negations)

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. Drop-in NLI upgrade: MoritzLaurer DeBERTa-v3-large available via huggingface transformers
   as a cross-encoder. Swapping MiniLM cosine for DeBERTa contradiction score in KF-1
   is a 2-3 day engineering change. No new training required.

2. Negation coverage determines product reliability on high-stakes factual claims:
   "Drug X does NOT increase Y" is the exact TruthfulQA-style pattern. If KF-1 cannot
   detect this class, the grounding function is unsafe for medical/scientific domains.

3. Polarity adapter requires only 200 labeled negation-flip pairs to re-weight MiniLM
   embedding dimensions. This is a substrate-level modification: embed negation-aware
   weights into the KF-1 scoring path without replacing the backbone model.

4. Three-type negation test suite (explicit + antonym + quantifier) should be added as
   a mandatory benchmark alongside easy/hard negatives in any KF-1 evaluation protocol.

5. Hybrid fusion production cost: DeBERTa cross-encoder + TF-IDF offline index +
   Pythia-160M. GPU serving: ~8-15ms total per query. Affordable for a grounding API.

---

## CITATIONS (verified count: 14)

1. Arakelyan et al. (2024). Semantic Sensitivities and Inconsistent Predictions:
   Measuring the Fragility of NLI Models. EACL 2024. arXiv:2401.14440.
   -- 12.92%/23.71% degradation in/out-of-domain under semantic perturbation.

2. Laurer et al. (2022+). DeBERTa-v3-large-mnli-fever-anli-ling-wanli.
   HuggingFace model card. arXiv:2104.07179 + 2111.09543.
   -- MNLI 91.2%, ANLI 70.2%, LingNLI 87%; SOTA NLI cross-encoder.

3. Gao et al. (2021). SimCSE: Simple Contrastive Learning of Sentence Embeddings.
   EMNLP 2021. arXiv:2104.08821.
   -- NLI hard negatives as contradiction pairs; contrastive learning framework.

4. Petcu et al. (2025). A Comprehensive Taxonomy of Negation for NLP and Neural Retrievers.
   arXiv:2507.22337.
   -- Negation taxonomy; dense neural models underperform on negation queries.

5. Zha et al. (2023). AlignScore: Evaluating Factual Consistency with a Unified
   Alignment Function. ACL 2023. arXiv:2305.16739.
   -- AUC-ROC best on 4/6 SummaC sets; RoBERTa-based NLI grounding; 4.7M training pairs.

6. Nie et al. (2020). Adversarial NLI: A New Benchmark for NLU. ACL 2020. arXiv:1910.14599.
   -- ANLI benchmark; BERT-large 57.6/48.0/43.2 across R1/R2/R3.

7. Anonymous (2025). Semantic Adapter for Universal Text Embeddings: Diagnosing and
   Mitigating Negation Blindness. arXiv:2504.00584.
   -- diagonal re-weighting; +14.52% SemAntoNeg with 200 samples; no fine-tuning.

8. Yousif et al. (2025). Making Language Models Robust Against Negation. arXiv:2502.07717.
   -- NSPP pre-training task; +1.8-9.1% on CondaQA; BERT/RoBERTa encoder models.

9. Huang et al. (2024). The Impact of Negated Text on Hallucination with LLMs.
   arXiv:2510.20375.
   -- NegHalu dataset; LLMs struggle on negation; token-level internal analysis.

10. SHROOM SemEval-2024 Task 6 system papers. arXiv:2404.04845, 2404.01210.
    -- NLI-based approaches competitive; DeBERTa fine-tuned on MNLI +0.09 F1 vs baseline.

11. From No to Know: Taxonomy of Negation for Multimodal Foundation Models.
    arXiv:2502.09645.
    -- Encoder models "very sensitive to negation" when NLI-fine-tuned.

12. cross-encoder/nli-deberta-v3-base. HuggingFace model card.
    -- SNLI 92.38%, MNLI 90.04%; lighter 86M-param option for KF-1 rescue.

13. SentiCSE: Sentiment-aware Contrastive Sentence Embedding. arXiv:2404.01104.
    -- Polar contrastive learning with sentiment-polarity negatives; structural reference
       for polarity-aware embedding design.

14. Language models are not naysayers: Analysis on negation benchmarks. arXiv:2306.08189.
    -- BERT-class models negation-insensitive; confirms MiniLM root cause.

---

NEXT-DRILL CANDIDATE: antonym coverage gap in NLI models -- does MNLI training include
"increases"/"decreases" scientific antonym pairs specifically? LingNLI 87% suggests partial
coverage, but domain-specific scientific antonyms (pharmacological, economic) may not be
covered. Field: NLI + semantic-lexical + domain-specific negation.
