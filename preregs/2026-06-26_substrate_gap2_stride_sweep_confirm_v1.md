# Prereg: substrate_gap2_stride_sweep_confirm_v1

**Filed:** 2026-06-26
**Author:** exp_dev (cell-author thread)
**Trigger:** Research handoff Anchor 1 (Gap 2 CLOSE diagnostic).
**Source documents (AUTHORITATIVE):**
- `notes/research_gap2_capacity_side_analysis_NOT_geometry_2026-06-26.md`
- `notes/exp_dev_handoff_research_gap2_capacity_side_analysis_2026-06-26.md` (Anchor 1, Anchor 2)

## Diagnostic claim

Substrate's 1.8% recall at M=10k adversarial-stride-1 keys IS the cosine-physics
floor (test-design artifact), not a substrate capacity gap. Vary stride between
consecutive keys: stride=1 (15/16 token overlap; adversarial near-duplicates)
through stride=16 (disjoint windows; natural keys). Predict recall scales
monotonically from KNN-floor toward chain-grade. If confirmed, Gap 2 CLOSES.

Combined Anchor 2 analysis layer (refuse-gate top1-top2 cosine delta) reads
delta distribution per arm; the delta primitive is the substrate-product
mechanism for refusing adversarial near-duplicates that no cosine method can
distinguish.

## Mechanism

For each seed, encode a stride-1 pool of 16-token windows via Pythia-2.8b
(160m smoke), apply contrastive projection W (PROJ_DIM=768), then for each
stride S in [1, 4, 8, 16] subsample every S-th key to construct the M=10k key
set at that stride. This trick reuses ONE encoder pass across all 4 strides
(saves 4x encoder cost). Within each stride arm:
- KNN sentinel: exhaustive cosine recall@1 (rank-blind).
- Iso k-means partition routing (chain-grade mechanism; PART_SIZE_TARGET=2000).
- Recall@1, recall@10 via route + within-partition rerank.
- Top1-top2 cosine delta distribution (refuse-gate primitive).

NO geometry-side cleanup mechanisms (no whitening, MIMO, DG, polarimetric,
ScaNN VQ, anisotropy expansion). Per autonomy rule: 6 HARD_FAILs are conclusive
on that class.

## Pre-reg bands (LOCKED at module init)

HARD_PASS_GAP2_CLOSES (diagnosis confirmed; CLOSE Gap 2):
- recall(stride=16) >= 0.90
- AND recall(stride=8) >= 0.70
- AND monotone non-decreasing in stride (tol 0.02)
- AND cv across seeds for stride=16 recall <= 0.05

MIDDLE_BAND (partial signal):
- monotone AND recall(stride=16) in [0.70, 0.90)

HARD_FAIL_GAP2_REAL (re-open Gap 2 with M-scaling audit):
- recall(stride=16) < 0.70
- OR non-monotone stride curve

HARD_FAIL_KNN_SENTINEL_REGRESSION (corruption catch):
- knn_sentinel(stride=16) < 0.80 -> keys themselves degraded.

## Config

- ANCHOR: substrate_gap2_stride_sweep_confirm_v1
- M = 10000 full, 2000 smoke
- STRIDES = [1, 4, 8, 16] (4 arms)
- Seeds = [11, 13, 19] full, [11] smoke (matches partition routing chain-grade ledger)
- Encoder = EleutherAI/pythia-2.8b full, EleutherAI/pythia-160m smoke
- PROJ_DIM = 768; PART_SIZE_TARGET = 2000; KM_ITERS = 25; SIGMA = 0.1
- WINDOW_TOKENS = 16; CUE_SHIFT = 1 (cue is shift-1 of key; within-key noise model)
- Routing: local CPU (Tier A); numpy + matmul; ~1.5-2h wall full.

## Disciplines

- ASCII only.
- Per-arm metrics per stride (Fix #28); read metrics.json per-stride, NOT verdict_msg.
- META_M7 capacity-sensitive dims IDENTICAL across smoke and full.
- atexit per-seed checkpoint + restartable via experiments/_seed_checkpoint.
- Smoke gate FIRST: smoke MUST show monotone stride curve before full dispatch.
- Pre-dispatch Fix #26 verify-the-referent: predispatch_check.py confirmed PROCEED.

## What CLOSURE implies

If HARD_PASS_GAP2_CLOSES: cap_map re-classify Gap 2 from RED to GREEN -- substrate
is at cosine-physics floor; chain-grade at M=10M via hierarchical partition routing
on natural keys; refuses near-duplicate queries no cosine method can resolve.

If MIDDLE_BAND: substrate works on natural keys but not chain-grade at M=10k; refuse-
gate primitive may lift; route follow-up Anchor 2 standalone or other mechanism.

If HARD_FAIL_GAP2_REAL: re-open Gap 2 with Anchor 3 natural-keys M-scaling audit
(M=[10k, 100k, 1M, 10M] on natural keys) + new research drill on input-side
pattern separation (only mechanism class not yet exhausted).

## Q-discipline

Any arm >= 0.995 flags suspect saturation; bands favor under-claim per Fix #28.
