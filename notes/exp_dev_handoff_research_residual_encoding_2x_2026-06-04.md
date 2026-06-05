# exp_dev hand-off -- research: residual encoding representation question 2x

**Filed-by:** research sub-agent
**Date:** 2026-06-04
**Trigger:** notes/research_drill_residual_encoding_representation_question_2x_2026-06-04.md
**Pause state:** check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file contains TASK + WHY + CONTRACT + AUTONOMY pointers only. Exp-dev designs anchor names, sweep grids, threshold formulas, queue choice, and pre-committed cap_map decisions autonomously.

---

## Why this hand-off exists

Exp-Dev empirical (2026-06-04) confirmed r=0.86 with random bipolar codebook + bigram base predictor. Research 2x drill establishes that this is algebraically inevitable: near-orthogonality of random codebooks means bigram base predictions are uncorrelated with targets, so residual norm does not decrease. Three alternative mechanisms are now algebraically characterized and ready for empirical test.

---

## Anchor Candidates (rank-ordered)

### 1. Logit-space residual encoding (HIGHEST PRIORITY)

**Anchor pointer:** Cell 4 from research note, logit-space sparse residual
**Substrate-product reading:** Instead of residual in codebook space, substrate stores sign(logit-residual) for K most-surprised symbols (actual vs predicted distribution). Algebraic prediction r ~ sqrt(K/V) ~ 0.27 for K=5, V=70. Capacity gain ~14x algebraic ceiling. Bypasses structured-embedding requirement entirely.
**Tier hint:** Cheap CPU smoke (no embedding training; corpus bigram statistics only)
**Why-now:** Highest algebraic upside, lowest implementation cost. If this cell passes (r < 0.40), the entire residual encoding mechanism is validated without requiring pre-trained embeddings.

### 2. PCA base predictor (SAFE FALLBACK)

**Anchor pointer:** Cell 2 from research note, PCA-projection of context histograms
**Substrate-product reading:** Compute PCA of bigram context means from Wikitext-2. Project expected pattern onto top-K PCs before residual computation. Eckart-Young theorem guarantees r reduction. Algebraic prediction r ~ 0.63-0.77, capacity gain ~1.7-2.5x. No neural training required.
**Tier hint:** Cheap CPU smoke (corpus statistics PCA, no GPU)
**Why-now:** Algebraically guaranteed to reduce r below baseline. Low risk. One-time preprocessing step, not per-query overhead.

### 3. Learned character embeddings + JL projection (LONGER TERM)

**Anchor pointer:** Cell 3 from research note, tiny learned embedding + random projection
**Substrate-product reading:** Train 2-layer char bigram model on Wikitext-2 (embedding dim=64), project to substrate dim via random matrix. Algebraic prediction r ~ 0.35-0.55 if JL projection preserves semantic cosines after binarization. Uncertain: binarization may destroy structure.
**Tier hint:** CPU or small GPU (1 epoch char-LM training on Wikitext-2)
**Why-now:** Theoretical ceiling r ~ 0.35 but uncertain after sign(.) binarization. Sequence after Cell 4 and Cell 2 confirm/deny the structured-embedding story.

---

## Context Pointers

- Research note (full algebraic derivations + pre-reg thresholds):
  d:/AI/hd-instrument/notes/research_drill_residual_encoding_representation_question_2x_2026-06-04.md
- Prior empirical result (r=0.86 baseline):
  Check data/exp_*/metrics.json for the 2026-06-04 bigram-base-predictor anchor
- Corpus: Wikitext-2 (standard; already available in repo or trivially downloaded)
- Substrate dim: N=2048 (standard smoke scale)

---

## Contract

- Pre-reg HARD-PASS / MIDDLE-BAND / HARD-FAIL thresholds per research note (Section: Falsifiable Predictions)
- Cell 4 HARD-PASS: r < 0.40; Cell 2 HARD-PASS: r < 0.70; Cell 3 HARD-PASS: r < 0.55
- Smoke gates before full sweep
- ASCII-only in verdict_msg (Windows cp1252 constraint)
- No silent defaults: --timeout required per exp formula
- Post-ship REMOTE VERIFY

## Autonomy Declaration

Exp-dev owns: anchor naming, sweep grid, queue routing (CPU vs GPU), exact threshold formulas, cap_map decision language. Research has pre-registered only the r thresholds above as algebraically grounded bounds -- exp-dev may tighten these after smoke confirmation.
