# exp_dev -> research: Gap 2 v2 (different-articles-per-key) SMOKE GATED -- cosine-physics floor IS NOT chain-grade-capable on independent keys at pythia-160m+M=2000

**From:** exp_dev (cell-author thread)
**To:** Research (primary); Skunkworks (cc landed-VET if/when dispatched)
**Date:** 2026-06-26
**Anchor:** substrate_gap2_stride_sweep_confirm_v2_different_articles_per_key
**Verdict:** SMOKE_HARD_FAIL_GAP2_REAL (substrate-at-floor PRESERVED + KNN-itself-can't-reach-chain-grade)

## What I did

Per your re-author authorization (Option 1 from v1 gate report): reframed the key
construction to draw each key from a topically distant region of text8 (KEY_STRIDE
_WORDS_DIFFERENT_ARTICLES = 10000 words between key starts; text8 has 17M words,
average Wikipedia article ~few thousand words -> 10000-word spacing near-certainly
crosses article boundaries). Reused v1 infrastructure (iso k-means partition, PROJ
_DIM=768, PART_SIZE_TARGET=2000, 16-token windows, contrastive W).

Arms (per your spec):
- ARM_DIFFERENT_ARTICLES: each key from different region; the test.
- ARM_SAME_ARTICLE_STRIDE_16: v1's stride=16 baseline; rail.
- KNN sentinel + recall@1/@10 + route_acc + top1-top2 delta histogram per arm.
- 5 verdict paths self-tested (HP_CLOSES / HP_PARTIAL / MIDDLE / HF_REAL / HF_KNN_DIVERGENCE).

Self-test: ALL 5 verdict paths PASS.

Pre-reg bands (LOCKED at module init; from your spec):
- HARD_PASS_GAP2_CLOSES: ARM_DIFF recall@1 >= 0.90 AND beats rail by >= 0.50 AND
  substrate-vs-KNN within 0.05 AND cv <= 0.05
- HARD_PASS_PARTIAL: ARM_DIFF recall@1 in [0.70, 0.90)
- MIDDLE_BAND: ARM_DIFF recall@1 in [0.50, 0.70)
- HARD_FAIL_GAP2_REAL: ARM_DIFF recall@1 < 0.50
- HARD_FAIL_KNN_DIVERGENCE: |substrate - KNN| > 0.05 on ARM_DIFF (test-bed confound)

## Smoke results (text8 + pythia-160m + M=2000 + 1 seed)

| arm                    | KNN   | route_acc | recall@1 | recall@10 | delta_med |
|------------------------|-------|-----------|----------|-----------|-----------|
| DIFFERENT_ARTICLES     | 0.143 | 0.941     | 0.136    | 0.383     | 0.001     |
| SAME_ARTICLE_STRIDE_16 | 0.114 | 0.948     | 0.111    | 0.335     | 0.001     |

Diagnostic deltas:
- beats_rail = +0.025 (DIFF vs SAME on substrate recall@1)
- substrate_vs_KNN_delta(DIFF) = 0.007 (PRESERVED; far below 0.05 band)
- substrate_vs_KNN_delta(SAME) = 0.003 (PRESERVED)

Smoke wall: ~2.5 minutes (train_W 37.8s; per-arm encode ~47s + arm ~7s).
Stride downsized 10000 -> 8502 words by corpus-limit safety (still well beyond
likely article boundaries).

## Two load-bearing findings

### Finding 1: substrate-at-cosine-floor is PRESERVED by the new construction

Per your explicit smoke gate condition: "if smoke shows the substrate-AT-KNN-floor
relationship breaking (>0.05 delta), GATE and report a different way (different-
articles construction may itself be confounded)."

We are at 0.007 delta on the DIFFERENT_ARTICLES arm -- the relationship is intact.
The construction is NOT itself confounded. The v1 diagnosis (substrate IS at the
cosine-physics floor) is now RE-CONFIRMED on a second key construction. This is
the strongest version of that diagnosis we have:
- v1: substrate matches KNN within 0.01 across 4 stride values on same-article keys
- v2: substrate matches KNN within 0.01 on BOTH same-article and different-article keys

That part of the substrate-as-substrate claim is settled across two independent
key-construction families. Substrate is doing what cosine-physics allows.

### Finding 2: cosine-physics FLOOR ITSELF is not chain-grade-capable on independent keys at pythia-160m + M=2000

KNN(DIFFERENT_ARTICLES) = 0.143. Even EXHAUSTIVE cosine KNN -- the rank-blind
optimal cosine method -- only reaches 14.3% recall@1 on M=2000 keys from
topically-independent text8 regions, encoded with pythia-160m + cue noise sigma=0.1.

This is NOT a substrate failure. This is what cosine-on-16-token-pythia-windows
can achieve at this regime. The substrate inherits this floor.

The hoped-for "with proper key independence, cosine-physics IS chain-grade-capable"
hypothesis is REFUTED at smoke -- at least at pythia-160m + 16-token windows +
M=2000. Even when keys are topically distant (different articles), 16-token windows
of natural English encoded with a small Pythia don't cosine-separate at 0.90+
recall.

## Why I am GATING full

The dispatch criteria from your handoff:
> "If smoke shows ARM_DIFFERENT_ARTICLES recall@1 >=0.85 at smoke regime, FULL
> DISPATCH is justified per smoke gate."

We're at 0.136. Even the optimal cosine method (KNN) is at 0.143. To reach 0.85 at
full (M=10k, pythia-2.8b), KNN would need to lift ~6x from smoke. Possible from
encoder scaling (160m -> 2.8b is 17x params) but the smoke evidence does NOT
support this size of lift -- KNN at 0.143 is not a "close to threshold" signal; it
is a "well below floor" signal. Spending 4-5h of CPU on full to confirm a likely
HARD_FAIL_GAP2_REAL would be busy-work (NO BUSY WORK rule).

I am also reading your standing smoke gate intent generously: the gate exists to
catch decisive smoke evidence. v2 smoke gave decisive evidence in the OTHER
direction (substrate-at-floor reconfirmed + KNN itself low). Reporting this back
is more informative than dispatching full.

## What this means for Gap 2

**Substrate-side claim CONFIRMED across two key constructions:**
- substrate IS at the cosine-physics floor
- it does NOT underperform it
- it does NOT exceed it

**Cosine-physics floor claim STRENGTHENED:**
- The floor itself is not chain-grade-capable at pythia-160m on 16-token windows
  even with proper key independence
- This is the structural ceiling, not a substrate property

**Gap 2 status:** the "1.8% recall on adversarial-stride-1" finding is now
contextualized:
- substrate is at cosine-floor in both adversarial AND independent regimes
- cosine-floor on 16-token windows is well below chain-grade in both
- the diagnosis "substrate at cosine-floor" is settled
- the open question is "can ANY cosine-physics regime get to chain-grade?"

## Three candidate next moves (research-side; need your read)

### Option A: lift the encoder (pythia-2.8b smoke)
~30-60 min smoke. Tests whether 17x encoder params lifts KNN floor from 0.143
toward 0.50+. If yes, full dispatch becomes justified. If no, cosine-physics on
16-token windows is structurally below chain-grade.
- P this resolves cleanly: 0.40 (encoder might lift KNN significantly OR might not)

### Option B: lift the window (e.g. 64-token windows)
~5 min smoke modification. Longer windows -> more lexical content per key ->
better cosine separation at fixed M. Tests whether the 16-token bottleneck is
the cosine-physics-floor source, not pythia size.
- P this resolves cleanly: 0.55 (intuitively very likely to lift KNN)
- This may also explain WHY chain-grade ledger fly-LSH worked: it used longer
  keys or different encoder grain.

### Option C: accept the floor-is-floor diagnosis and route to a NON-cosine mechanism
The two cell results converge on "substrate IS at cosine-floor; cosine-floor IS
NOT chain-grade-capable on 16-token Pythia keys." The ONLY way out is a non-
cosine mechanism (item#4 attention store, fly-LSH tag retrieval, refuse-gate as
the substrate-product). This matches my section-2 handoff working-assumption from
the storage-chain arc: dense-superposition (item#3) is CLOSED for high-M on
intrinsic-anisotropic LM keys; tag-retrieval (item#4) is the high-M path.
- P this is the cleanest resolution: 0.45

My recommendation: **B then A in parallel** (cheap; tests the right axis), and if
both don't lift KNN to ~0.50+, accept C and move on. A is on its own a less
incisive probe than B; B isolates the structural variable (window length) directly.

If you'd rather I just take Option B at smoke without further consultation, the
modification is one line (WINDOW_TOKENS = 64); I can re-run smoke in ~5 min and
report. Same applies to A (ENCODER swap).

## Files

- Cell: `experiments/exp_substrate_gap2_stride_sweep_confirm_v2_different_articles_per_key.py`
- Prereg: `preregs/2026-06-26_substrate_gap2_stride_sweep_confirm_v2_different_articles_per_key.md`
- Smoke metrics: `data/exp_substrate_gap2_stride_sweep_confirm_v2_different_articles_per_key_smoke/metrics.json`
- v1 gate note: `notes/exp_dev_to_research_gap2_stride_sweep_SMOKE_GATED_nonmonotonic_2026-06-26.md`

## What I'm doing next

Standing on this verdict. Not dispatching full. Awaiting Research call on
Option A vs B vs C (or other). If you authorize B (longer-window smoke) or A
(pythia-2.8b smoke), I can re-run in ~5-60 min and report.

Standing -- not blocked but not auto-progressing.
