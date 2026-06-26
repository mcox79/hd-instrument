# Prereg: substrate_gap2_stride_sweep_confirm_v2_different_articles_per_key

**Filed:** 2026-06-26
**Author:** exp_dev (cell-author thread)
**Trigger:** Research re-author authorization Option 1 (REFRAME after v1 SMOKE_GATED non-monotonic).
**Source documents (AUTHORITATIVE):**
- `notes/exp_dev_to_research_gap2_stride_sweep_SMOKE_GATED_nonmonotonic_2026-06-26.md` (v1 gate)
- `notes/research_gap2_capacity_side_analysis_NOT_geometry_2026-06-26.md` (diagnosis)
- `notes/exp_dev_handoff_research_gap2_capacity_side_analysis_2026-06-26.md` (Anchor 1+2)

## Why a reframe was needed (v1 lesson)

v1 stride-sweep SMOKE_GATED non-monotonic. Across all strides [1,4,8,16], substrate
recall tracked KNN within +-0.01 (substrate IS at cosine-physics floor; that part of
the diagnosis is CONFIRMED). But the absolute curve peaked at stride=4 (recall=0.151)
and DECREASED at stride=16 (recall=0.099) -- not the predicted monotone climb toward
chain-grade. Hypothesis H3 from gate report: text8 boilerplate-rich Wikipedia has a
natural similarity ceiling on disjoint windows from SAME ARTICLE -- the stride trick
cannot escape it regardless of M.

Research authorized Option 1 reframe: change KEY CONSTRUCTION so each key is from a
DIFFERENT article (topically distant region of text8), not different windows of the
same prose region.

## Diagnostic claim (unchanged from v1)

Substrate's 1.8% recall at M=10k adversarial-stride-1 keys IS the cosine-physics
floor. With PROPER KEY INDEPENDENCE, substrate (still at cosine-floor) should achieve
chain-grade >=0.90 at M=10k.

If yes -> Gap 2 CLOSES cleanly:
- Substrate IS at cosine-physics optimum (proven by v1 + corroborated by v2 KNN sentinel)
- Cosine-physics IS chain-grade-capable on properly-independent keys

If no even with proper independence -> Gap 2 is a REAL capacity gap; need new mechanism.

## Mechanism (v2 reframe)

For each seed:
1. Train ONE contrastive projection W on a contiguous text8 train pool (PROJ_DIM=768).
2. Build ARM_DIFFERENT_ARTICLES keys: M random start positions in text8, spaced
   KEY_STRIDE_WORDS_DIFFERENT_ARTICLES=10000 words apart with small jitter; shuffle
   order. Each key is a 16-token window from a topically distant region (text8 has
   17M words and average Wikipedia article ~few thousand words, so 10000-word
   spacing near-certainly crosses article boundaries).
3. Build ARM_SAME_ARTICLE_STRIDE_16 keys (the rail): contiguous text8 region;
   M consecutive 16-token windows at stride=16 (v1's stride=16 reproduced; disjoint
   windows from likely-same article).
4. Encode both arm key sets through same W.
5. Per arm: KNN sentinel, iso k-means partition routing, recall@1/@10, route_acc,
   top1-top2 delta distribution.

KNN sentinel role: verifies substrate-at-cosine-floor relationship holds on the new
key construction. If |substrate - knn| > 0.05 on ARM_DIFFERENT_ARTICLES, the new
construction itself is confounded (cell is the confound, not Gap 2 verdict).

## Pre-reg bands (LOCKED at module init)

### HARD_PASS_GAP2_CLOSES (Gap 2 CLOSES)
- ARM_DIFFERENT_ARTICLES recall_at_1 >= 0.90
- AND beats ARM_SAME_ARTICLE_STRIDE_16 by >= 0.50
- AND substrate-vs-KNN |delta| <= 0.05 (substrate-at-floor preserved)
- AND cv across seeds <= 0.05

### HARD_PASS_PARTIAL (significant lift; not chain-grade)
- ARM_DIFFERENT_ARTICLES recall_at_1 in [0.70, 0.90)
- (substrate-vs-KNN gate must also pass)

### MIDDLE_BAND (modest lift)
- ARM_DIFFERENT_ARTICLES recall_at_1 in [0.50, 0.70)

### HARD_FAIL_GAP2_REAL (Gap 2 is real)
- ARM_DIFFERENT_ARTICLES recall_at_1 < 0.50
  -- even with proper key independence, substrate can't chain-grade at M=10k.
  Gap 2 is a real capacity gap. New mechanism needed.

### HARD_FAIL_KNN_DIVERGENCE (test-bed confound; GATE_AND_REPORT)
- |substrate(DIFF_ART) recall_at_1 - knn(DIFF_ART) recall_at_1| > 0.05
  -- the different-articles construction broke the substrate-at-cosine-floor
  relationship; the cell is the confound, NOT a Gap 2 verdict. Route back to
  Research for further reframe (different-articles construction may itself be
  contaminated -- e.g. if KNN spikes high without substrate following, the W
  projection might not generalize across topical regions).

## Config

- ANCHOR: `substrate_gap2_stride_sweep_confirm_v2_different_articles_per_key`
- M = 10000 full, 2000 smoke
- ARM_NAMES = ["DIFFERENT_ARTICLES", "SAME_ARTICLE_STRIDE_16"]
- KEY_STRIDE_WORDS_DIFFERENT_ARTICLES = 10000
- KEY_STRIDE_WORDS_SAME_ARTICLE = 16
- Seeds = [11, 13, 19] full, [11] smoke
- Encoder = EleutherAI/pythia-2.8b full, EleutherAI/pythia-160m smoke
- PROJ_DIM = 768; PART_SIZE_TARGET = 2000; KM_ITERS = 25; SIGMA = 0.1
- WINDOW_TOKENS = 16; CUE_SHIFT = 1
- Routing: local CPU (Tier A); ~1.5-2h wall full.

## Disciplines

- ASCII only.
- Per-arm metrics (Fix #28); read metrics.json per-arm, NOT verdict_msg.
- META_M7 capacity-sensitive dims IDENTICAL across smoke and full.
- atexit per-seed checkpoint + restartable via experiments/_seed_checkpoint.
- Smoke gate FIRST: if smoke shows substrate-vs-KNN |delta| > 0.05 on ARM_
  DIFFERENT_ARTICLES, GATE (different-articles construction confounded; route to
  Research). If smoke shows ARM_DIFFERENT_ARTICLES recall >= 0.85 with substrate-
  at-floor preserved, FULL DISPATCH is justified.
- Pre-dispatch Fix #26 verify-the-referent: predispatch_check.py PROCEED.

## Smoke gate criteria (explicit)

1. self-test PASS (5 verdict paths) -- DONE before this prereg was committed.
2. smoke runs to completion on pythia-160m + M=2000 + 1 seed.
3. smoke ARM_DIFFERENT_ARTICLES knn_recall_at_1 should be >= 0.5 (sanity: with
   topically diverse keys at small encoder + small M, KNN should be reasonable).
4. smoke |substrate - knn| <= 0.05 on ARM_DIFFERENT_ARTICLES (substrate-at-floor
   preserved by new construction).
5. smoke ARM_DIFFERENT_ARTICLES recall_at_1 ideally >= 0.85; if 0.50-0.85, full
   dispatch still justified as the discriminating regime; if <0.50 with KNN also
   <0.50 it confirms the gap (still informative).

If gates 3-5 trip in pathological ways (e.g. KNN diverges from substrate by >>0.05),
GATE and route back to Research.

## What CLOSURE implies

If HARD_PASS_GAP2_CLOSES: cap_map re-classify Gap 2 RED -> GREEN. The cosine-physics
floor explanation is COMPLETE: substrate is at the optimal floor (proven by
sentinel) AND that floor IS chain-grade-capable on independent keys (proven by the
DIFFERENT_ARTICLES arm).

If HARD_PASS_PARTIAL / MIDDLE: substrate gains independent-keys lift but cosine-
physics is not chain-grade-capable at M=10k. Refuse-gate primitive may be the
substrate-product mechanism. Route Anchor 2 refuse-gate standalone.

If HARD_FAIL_GAP2_REAL: Gap 2 is real; Anchor 3 natural-keys M-scaling audit
(M=[10k, 100k, 1M, 10M] on natural keys with input-side pattern separation as
the new candidate mechanism).

If HARD_FAIL_KNN_DIVERGENCE: cell is confounded; route to Research for further
reframe. The W projection may not generalize across topical regions; Research
should consider per-arm W or a topic-stratified train pool.

## Q-discipline

Any arm recall >= 0.995 flags suspect saturation; bands favor under-claim per Fix #28.
