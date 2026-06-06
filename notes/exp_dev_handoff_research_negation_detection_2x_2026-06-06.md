# exp_dev hand-off -- research: negation-detection-2x

**Filed-by:** research sub-agent, 2026-06-06
**Trigger:** 2x level-2 operational drill on negation-insensitive KF-1/MiniLM finding
**Research note path:** d:/AI/hd-instrument/notes/research_drill_negation_detection_hallucination_2x_2026-06-06.md

**Pause state:** Check data/orchestrator_paused.flag before dispatch.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off WHAT and WHY.
exp_dev owns all anchor names, sweep grids, threshold formulas, queue routing, and timing.

---

## Anchor candidates (rank-ordered)

### Rank 1: KF1_NLI_rescue -- highest P_deflated, cheapest test, no new training

**Anchor pointer:** Swap MiniLM cosine scorer in KF-1 with DeBERTa-v3-large NLI contradiction probability.

**Substrate-product reading:** KF-1 currently scores AUC=0.034 on TruthfulQA-style negated
false-fact queries (below chance). A cross-encoder NLI model trained on MNLI+FEVER+ANLI+LingNLI
scores contradiction probability instead of cosine similarity, achieving MNLI 91.2% and ANLI 70.2%
on adversarial NLI. The contradiction probability for a negated false fact vs. its grounding
document should be high; for a grounded true fact it should be low/neutral.

**P_deflated:** 0.72
**HP:** AUC >= 0.85 on TruthfulQA-style negations; AUC >= 0.90 on easy negatives
**MID:** AUC 0.70-0.85 on TruthfulQA-style (partial rescue)
**HF:** AUC < 0.60 on TruthfulQA-style; AUC < 0.80 on easy negatives
**Tier hint:** CPU-eligible (< 2h for N=1000 pairs on DeBERTa inference; no training)
**Why now:** This is the direct rescue for a confirmed HARD-FAIL. No training required.
  MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli is a drop-in model.

---

### Rank 2: KF1_polar_adapter -- cheap antonym coverage, handles "increases" vs "decreases" gap

**Anchor pointer:** Learn diagonal re-weighting vector on MiniLM embedding dimensions using
negation-flip contrastive pairs. Frozen backbone; only d=384 scalar weights trained.

**Substrate-product reading:** Cue features cannot detect antonym-based negation (no "not"
token present in "X increases" vs "X decreases"). A polarity adapter trained on 200-1000
negation-flip pairs re-weights which embedding dimensions are negation-sensitive, without
fine-tuning the model. arXiv:2504.00584 reports +14.52% on SemAntoNeg with this approach.

**P_deflated:** 0.55
**HP:** AUC >= 0.80 on explicit+antonym combined; AUC >= 0.92 on easy negatives (regression)
**MID:** AUC 0.65-0.80 on explicit+antonym
**HF:** AUC < 0.55 on antonym-only subclass; AUC < 0.88 on easy negatives
**Tier hint:** CPU (training ~minutes; inference zero-overhead vs MiniLM baseline)
**Why now:** Antonym substitution is the dominant gap cue features cannot cover.
  This is the cheapest path to antonym coverage and runs in parallel with Rank 1.

---

### Rank 3: KF1_cue_augment -- explicit negation baseline, runs before Rank 1 as cheap signal check

**Anchor pointer:** Concatenate 20-dim negation cue feature vector to MiniLM embedding;
train lightweight MLP head (~80K params). Cues: has_not, has_no, has_never, has_nt, has_without,
has_fails, has_cannot, negation_count, etc.

**Substrate-product reading:** Explicit-token negation ("X is NOT Y") should be caught
by cue features at near-zero compute cost. This does NOT cover antonyms -- structural ceiling
is ~60% of negation cases. Test as a lower bound; if AUC < 0.45 the test set has too many
antonym cases for cue features to help at all.

**P_deflated:** 0.48
**HP:** AUC >= 0.70 on TruthfulQA-style negations (explicit subset)
**MID:** AUC 0.55-0.70
**HF:** AUC < 0.45 (adds noise; discard)
**Tier hint:** CPU (feature extraction is string matching; MLP training < 5 min)
**Why now:** Cheap ablation establishing whether explicit-token baseline is worth keeping
  as a fast first-pass filter before invoking NLI cross-encoder.

---

### Rank 4: KF1_hybrid_fusion -- production recipe, highest ceiling AUC, runs after Rank 1 confirms NLI signal

**Anchor pointer:** Late fusion of three signals: (a) DeBERTa NLI contradiction score,
(b) word-bigram TF-IDF miss score, (c) Pythia-residual perplexity delta. Tune alpha/beta/gamma
on held-out validation; evaluate on full adversarial suite (negation + word-order + easy).

**Substrate-product reading:** Negation and word-order adversarials have DIFFERENT dominant
signals (NLI vs bigram/Pythia). A weighted sum covers both adversarial classes and the easy
baseline simultaneously. This is the production-grade KF-1 scorer that ships after individual
signal validation. AlignScore (RoBERTa + multi-task NLI, arXiv:2305.16739) achieves best AUC
on 4/6 SummaC factual consistency sets using a similar multi-task fusion approach.

**P_deflated:** 0.62
**HP:** Combined adversarial AUC >= 0.88; TruthfulQA-style AUC >= 0.85; word-order AUC >= 0.88
**MID:** HP1 in [0.75, 0.85) AND word-order in [0.78, 0.88)
**HF:** Combined adversarial AUC < 0.80; easy negatives AUC < 0.97
**Tier hint:** GPU preferred for DeBERTa throughput; CPU feasible at small N
**Why now:** Dispatch only after Rank 1 confirms NLI signal (AUC >= 0.70 at minimum).
  Rank 4 is the integration test, not the signal validation.

---

## Context pointers

- Research note (full derivations + lit citations): d:/AI/hd-instrument/notes/research_drill_negation_detection_hallucination_2x_2026-06-06.md
- Prior KF-1 MiniLM benchmark results: referenced in research note Section 2 (prior AUCs: easy=0.999, hard=0.975, TruthfulQA-style=0.034, word-shuffled=0.217)
- Drill B (word-order rescue): cross-reference notes for word-bigram TF-IDF + Pythia findings
- DeBERTa model: MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli (HuggingFace)
- Polarity adapter paper: arXiv:2504.00584

---

## Contract

exp_dev owns ALL of: anchor naming, sweep grid design, queue routing (CPU vs GPU),
timeout estimation, pre-reg HP/MID/HF numerical bounds, cap_map decision post-verdict.

This file is context + direction only. No experiment design is pre-committed here.

## Autonomy declaration

exp_dev may: modify rank order based on current queue depth; combine Rank 1 and Rank 3
into a single smoke run; defer Rank 4 until Rank 1 passes MID-band; substitute lighter
DeBERTa-base variant if GPU queue is saturated.
