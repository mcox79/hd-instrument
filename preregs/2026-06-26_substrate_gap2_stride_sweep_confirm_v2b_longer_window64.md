# Prereg: substrate_gap2_stride_sweep_confirm_v2b_longer_window64

**Filed:** 2026-06-26
**Author:** exp_dev (cell-author thread)
**Trigger:** Research Option B authorization after v2 smoke gate.
**Source documents (AUTHORITATIVE):**
- `notes/exp_dev_to_research_gap2_v2_different_articles_SMOKE_GATED_2026-06-26.md` (v2 gate)
- Research SendMessage 2026-06-26 (Option B authorize; "longer windows immediate; trial A if B in [0.30, 0.50); accept C if neither lifts KNN above 0.50")

## Why v2b

v2 smoke showed KNN=0.143 on ARM_DIFFERENT_ARTICLES at pythia-160m + M=2000 +
16-token windows; substrate-at-cosine-floor PRESERVED (delta=0.007) but cosine-
physics floor itself was below chain-grade. Research Option B: isolate the
structural variable (window length) by doubling+ window from 16 to 64 tokens.

Hypothesis: 16-token windows are the cosine-physics-floor bottleneck. Longer
windows -> more lexical content per key -> better cosine separation at fixed M ->
KNN floor lifts; substrate (at floor) follows.

## Changes from v2

- WINDOW_TOKENS: 16 -> 64
- CUE_SHIFT: 1 -> 4 (proportional: 4/64 = 1/16 = same density as v2's 1/16)
- Local encode wrapper with max_length=128 (canonical probe uses 48; too short
  for 64 words -> ~80-128 subword tokens). Cached model (one load per cell run).
- Anchor: `substrate_gap2_stride_sweep_confirm_v2b_longer_window64`

Otherwise IDENTICAL to v2 (same arms, same iso k-means partition routing, same
contrastive W, same band thresholds, same self-tests).

## Pre-reg bands (LOCKED at module init; INHERITED from v2)

### HARD_PASS_GAP2_CLOSES (Gap 2 CLOSES + window-length is the lever)
- ARM_DIFFERENT_ARTICLES recall_at_1 >= 0.90 AND beats SAME_ARTICLE rail by >= 0.50
- AND substrate-vs-KNN within 0.05 AND cv <= 0.05

### HARD_PASS_PARTIAL (significant lift from window-length)
- ARM_DIFFERENT_ARTICLES recall_at_1 in [0.70, 0.90)

### MIDDLE_BAND (modest lift)
- ARM_DIFFERENT_ARTICLES recall_at_1 in [0.50, 0.70)

### HARD_FAIL_GAP2_REAL (Gap 2 is real even at long windows + independent keys)
- ARM_DIFFERENT_ARTICLES recall_at_1 < 0.50

### HARD_FAIL_KNN_DIVERGENCE (test-bed confound)
- |substrate(DIFF) - KNN(DIFF)| > 0.05

## Smoke gate (per Research decision tree)

- If KNN(DIFF) >= 0.50 -> dispatch full
- If KNN(DIFF) in [0.30, 0.50) -> also try Option A (pythia-2.8b smoke; window=64)
- If KNN(DIFF) < 0.30 (neither A nor B will plausibly bridge to 0.50) ->
  accept Option C (cosine-physics floor IS structural ceiling)

## Config

- ANCHOR: `substrate_gap2_stride_sweep_confirm_v2b_longer_window64`
- M = 10000 full, 2000 smoke
- WINDOW_TOKENS = 64; CUE_SHIFT = 4
- KEY_STRIDE_WORDS_DIFFERENT_ARTICLES = 10000
- Encoder = EleutherAI/pythia-160m smoke (pythia-2.8b full IF lift justifies)
- PROJ_DIM = 768; PART_SIZE_TARGET = 2000; KM_ITERS = 25; SIGMA = 0.1
- Local encode max_length=128 (override canonical 48 for longer windows)

## Q-discipline

Any arm recall >= 0.995 flags suspect saturation; bands favor under-claim per Fix #28.
