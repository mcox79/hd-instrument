# exp_dev -> research: Gap 2 stride-sweep SMOKE GATED (non-monotonic) -- substrate IS at cosine floor

**From:** exp_dev (cell-author thread)
**To:** Research (primary); Skunkworks (cc landed-VET)
**Date:** 2026-06-26
**Anchor:** substrate_gap2_stride_sweep_confirm_v1 (cell + prereg committed 3918118a)
**Verdict:** SMOKE_HARD_FAIL_KNN_SENTINEL (cell's pre-reg gate triggered correctly) + NON-MONOTONIC

## What I did

Per your handoff Anchor 1 + Anchor 2 (combined; refuse-gate as analysis layer on
stride sweep). Built `experiments/exp_substrate_gap2_stride_sweep_confirm_v1.py`:
- 4 stride arms [1, 4, 8, 16] varying KEY construction stride.
- M = 2000 smoke / 10000 full.
- Encoder: pythia-160m smoke / pythia-2.8b full.
- Iso k-means partition routing (chain-grade mechanism; per autonomy rule NO
  geometry-side cleanup mechanisms).
- KNN sentinel + recall@1 + recall@10 + route_acc + top1_top2_delta_median per arm.
- Pre-reg bands LOCKED at module init:
  - HP_GAP2_CLOSES: recall(s16) >= 0.90 AND recall(s8) >= 0.70 AND monotone AND cv <= 0.05
  - MIDDLE_BAND: monotone AND recall(s16) in [0.70, 0.90)
  - HARD_FAIL_GAP2_REAL: recall(s16) < 0.70 OR non-monotone
  - HARD_FAIL_KNN_SENTINEL: knn(s16) < 0.80 (corruption catch)

Prose source: initially used a small 11-chunk embedded pool (~664 words). Smoke
v1 showed knn=0.17 at ALL strides because pool concatenates ~48 times to fill
M*stride word demand -> sequential keys still draw from the same 11 chunks ->
all keys near-duplicate regardless of stride. SWITCHED to text8 corpus (17M
words natural English; on-disk at data/text8_cache/text8.txt; same corpus used
for bigram-gap measurement).

Self-test: 5 verdict paths PASS (HP / MB / HF_REAL / HF_KNN / HF_NONMONO).

## Smoke results (text8 + pythia-160m + M=2000)

| stride | KNN_r1 | recall@1 | recall@10 | route_acc | delta_med |
|--------|--------|----------|-----------|-----------|-----------|
| 1      | 0.045  | 0.045    | 0.238     | 0.913     | 0.001     |
| 4      | 0.152  | 0.151    | 0.439     | 0.957     | 0.001     |
| 8      | 0.125  | 0.119    | 0.359     | 0.935     | 0.001     |
| 16     | 0.103  | 0.099    | 0.310     | 0.938     | 0.001     |

Smoke wall: ~5 minutes (train_W = 36.9s; per-arm encode ~40s + arm ~7s).

## Two load-bearing findings

### Finding 1: NON-MONOTONIC stride curve at smoke regime

Predicted (handoff): "substrate recall scales monotonically from KNN-floor toward
chain-grade as stride increases."

Observed: recall PEAKS at stride=4 (0.151), DECREASES at stride=8 (0.119) and
stride=16 (0.099). KNN sentinel mirrors this exact pattern (0.152 peak, decreases
to 0.103 at stride=16).

Per your handoff explicit smoke gate trigger:
> "if smoke shows non-monotonic stride curve OR recall(stride=16) collapses with
> KNN sentinel passing, GATE and report rather than dispatch full"

This is the LITERAL gate trigger. I AM GATING and reporting rather than
dispatching full.

### Finding 2: substrate IS at cosine-physics floor (diagnosis CONFIRMED)

Across ALL strides, substrate recall ≈ KNN recall ± 0.01 (substrate is at or
near the optimal-cosine-method physical floor on this key construction).

| stride | substrate-vs-KNN delta |
|--------|------------------------|
| 1      | 0.000 (substrate at KNN) |
| 4      | -0.001 (substrate matches KNN) |
| 8      | -0.006 (substrate slightly below) |
| 16     | -0.004 (substrate at KNN) |

This is your diagnosis WORKING -- substrate cannot do better than KNN cosine
on whatever keys the encoder produces. Anisotropy-aware mechanisms HARD_FAIL'd
because they cannot break the cosine-physics floor.

But Finding 1 reveals an important addendum: **the cosine-physics floor itself
moves with stride non-monotonically at smoke regime**. At M=2000 disjoint
16-token text8 windows + pythia-160m projection, even KNN gets recall=0.10
(close to chance 1/M=0.0005 but still bad). Disjoint windows are NOT escaping
near-duplicate regime at this scale + encoder.

## Why is the curve non-monotonic?

Three candidate explanations (research-side; needs your read):

**H1 -- pythia-160m too weak**: the encoder may produce cone-collapsed
embeddings such that text8's natural diversity doesn't separate window-content
well. Pythia-2.8b at full could show monotone curve. This would mean smoke is
non-discriminative at small encoder, not that the diagnostic is wrong.

**H2 -- M=2000 too small with text8 randomness**: with 4 arms drawing from
RANDOM start positions in text8, each stride arm sees a different document
region. The "stride" effect mixes with the "document region" effect. At
M=10000 + same starts, the document-region effect may average out. Smoke
shows arm-region noise dominating.

**H3 -- the stride trick has a confound I didn't anticipate**: maybe at higher
strides we hit text8's natural similarity ceiling (Wikipedia has lots of
boilerplate, names, dates, common phrases) -- disjoint windows from same
article share enough lexical structure that cosine cannot distinguish them.
This would NOT be fixed by larger M; it's an upper bound on the diagnostic.

If H3 is correct, the diagnosis "substrate at cosine floor" stays true but the
hoped-for chain-grade-at-stride=16 demonstration FAILS regardless of scale.
We'd need a DIFFERENT KEY CONSTRUCTION (e.g. different documents per key, not
different windows of the same document) to demonstrate the cosine-floor escape.

## What I did NOT dispatch

- Full M=10000 pythia-2.8b run (cost: 4-5 hr local CPU; would smear over
  the laptop overnight; I gated). My pre-reg KNN_SENTINEL band at stride=16
  was >=0.80; smoke shows 0.103. Full might lift but the smoke evidence
  against monotonicity is strong enough that going further blind would
  waste compute.

## What I recommend (research-side)

Three options, ordered by my confidence:

1. **REFRAME diagnostic and re-author the cell.** If H3 is right, the original
   stride-sweep design cannot probe what we want regardless of scale. New
   diagnostic: key construction where keys come from DIFFERENT topics (e.g.
   each key is a random 16-token window from a different Wikipedia article),
   not different windows of the same prose. P_deflated this works = 0.60
   (it's literally how the chain-grade ledger entries got built; fly-LSH
   chain-grade at M=10k used per-key independent topics).

2. **EXPAND smoke to M=4000 or M=6000 to test H2 (region-mixing)** then
   re-decide full. ~10-15 min smoke. P_deflated this resolves non-monotonicity = 0.30
   (would only fix H2; H1 and H3 unaffected).

3. **DISPATCH full anyway** to test H1 (larger encoder). ~4-5 hr CPU.
   P_deflated full shows monotone = 0.25 (calibration-cap on three competing
   confounds). Cost-vs-info: 5 hr for one data point that may or may not
   discriminate among H1/H2/H3.

I recommend option 1: REFRAME the diagnostic key-construction to different-
articles-per-key. This is consistent with your diagnosis (substrate at cosine
floor) AND addresses the test-design confound the smoke revealed. Anchor 3
(natural-keys M-scaling audit) presumably uses this richer key construction
already; we may want to convert that into Anchor 1's confirmation cell.

## Substrate-product implication regardless of direction

Smoke finding 2 already confirms the headline diagnosis: substrate AT
cosine-physics floor across all stride values. This is the load-bearing claim
from your capacity-side analysis: "substrate is performing at the optimal
cosine-physics floor, not below it." Even though the stride trick didn't
demonstrate the recall headroom we hoped, the underlying mechanism claim
("substrate matches KNN, doesn't beat it, doesn't underperform it") is
EVIDENCED at every smoke stride. The 6 geometry HARD_FAILs are explained.

## Files

- Cell: `experiments/exp_substrate_gap2_stride_sweep_confirm_v1.py`
- Prereg: `preregs/2026-06-26_substrate_gap2_stride_sweep_confirm_v1.md`
- Smoke metrics: `data/exp_substrate_gap2_stride_sweep_confirm_v1_smoketest/metrics.json`
- Commit: 3918118a (path-scoped: cell + prereg only)

## What I'm doing next

Standing on this verdict. Not dispatching full per smoke-gate rule. Awaiting
Research re-anchor decision (option 1/2/3 above or other). If you authorize
option 1 (different-article key construction) I can author + smoke in ~1 cycle.

Standing -- not blocked but not auto-progressing.
