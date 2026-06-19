# Pre-registration: wave14d_icl_via_pool_v3_scaling

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14d_icl_via_pool_v3_scaling.py](../experiments/exp_wave14d_icl_via_pool_v3_scaling.py)
Priority source: [active_priorities.md](../notes/active_priorities.md) Bet 1
Author: experiment_dev session, cycle 2

## Why

[active_priorities.md](../notes/active_priorities.md) Bet 1 names the
substrate's ICL-saturation envelope as the top Tier-S gap. Two prior runs
bracket the question:

- `wave14d_icl_via_pool_v2`: positive ICL at small ICTX, but never tested ICTX > 2048.
- `wave14f_icl_scaling_pool`: pool-SIZE sweep (different sweep, fixed ICTX) gave
  slope_log2(pool) = **−0.067** — inverted. Implication flagged: "corpus too
  small for larger pool; relevant items run out."
- `wave14g_icl_saturation_extended`: the intended close-test. Crashed at
  `augment_pool` when `n_new > POOL_SIZE` (hardcoded POOL_SIZE=4096 vs ICTX=8192+).

v3 fixes both: (a) augment_pool no longer uses a fixed-size circular buffer —
it allocates `pool_used + n_new` rows so any ICTX fits; (b) Corpus B is
assembled from `experiments/*.py` (stable, ~2.4 MB on remote) instead of
`session_events.jsonl` (volatile, ~1 KB locally). Corpus B size is asserted
at runtime; smoke aborts if too small for the largest requested ICTX.

## Hypothesis

Across ICTX ∈ {64, 256, 1024, 4096, 16384} at ALPHA=1.0, 3 seeds, with a
substrate of N=4096 trained on Corpus A:

- The bpc gain (irrelevant_bpc − relevant_bpc on Corpus B test) is positive
  at every ICTX.
- The slope of mean gain vs log2(ICTX) is **> +0.10** across the tested range.
- gain at ICTX=16384 is not statistically below gain at ICTX=4096
  (i.e., no saturation collapse between the two largest ICTX points).

Backup if any single criterion fails — see Verdict labels below.

## Multi-probe success criteria (all required for VALIDATED)

1. bpc gain (irr − rel) at ICTX ∈ {64, 256, 1024, 4096, 16384}, ALPHA=1.0, 3 seeds.
2. Slope of mean_gain vs log2(ICTX), least-squares: **> +0.10**.
3. Positive gain at ICTX=16384: mean_gain_16384 > 0.
4. No collapse at largest ICTX: (mean_gain_16384 + σ_16384) ≥ (mean_gain_4096 − σ_4096).
5. Distinct-chunk floor: every seed produced ≥ ICTX distinct relevant chunks at
   every ICTX (i.e., corpus didn't run out).
6. Pool retrieval entropy at ICTX=16384 ≥ 1.0 nat per query (no collapse to ≤2 items).

## Kill criterion

Either of the following retracts the "kNN-LM-like ICL scaling" framing and
drops ICL to "small-ICTX capability only" in the capability map:

- Slope of mean_gain vs log2(ICTX) ≤ 0 across the subset ICTX ≥ 1024.
- mean_gain_16384 < mean_gain_4096 − σ_4096 (collapse worse than 1σ).

## Verdict labels

- `ICL_SATURATION_VALIDATED` — criteria 1–6 all satisfied.
- `ICL_SATURATION_INVERTED` — either kill criterion triggered. Retraction
  routed to Strategy session for cap_map update.
- `ICL_SATURATION_WEAK` — slope > 0 but < 0.10; gain_16384 > 0; no kill triggers.
  Suggests ICL works but plateaus; product story becomes "log scaling within
  bounded ICTX, not unbounded kNN-LM-like."
- `ICL_SATURATION_INSUFFICIENT_CORPUS` — distinct-chunk floor (criterion 5)
  failed. Re-route to Corpus expansion before re-running.
- `ICL_SATURATION_POOL_COLLAPSE` — criterion 6 failed (entropy < 1.0 at largest
  ICTX). Indicates retrieval saturation, not a substrate saturation. Distinct
  failure mode — gain may still scale but retrieval mechanism is at limit.
- `ICL_SATURATION_INCONCLUSIVE` — missing data in summary.

## Oracle assertions (smoke mode, abort on fail)

1. `assert_in_range("rel_bpc_smoke", rel_bpc[ICTX_smoke_max], (0.5, 8.0))` —
   bpc values are in a plausible byte-LM range (0.5 trivial floor, 8 = uniform).
2. `assert_in_range("off_bpc_smoke", off_baseline_bpc, (0.5, 8.0))` —
   substrate baseline produces a numeric result.
3. `assert_distinguishable("irr_vs_rel_smoke", irr_bpc[ICTX_smoke_max],
   rel_bpc[ICTX_smoke_max], min_gap=0.005)` — at the smoke's largest ICTX, the
   irr vs rel arms must differ; if not, the augment_pool/eval pipeline is
   broken (substrate cannot tell relevant from irrelevant).
4. Distinct-chunk assertion: train_b chunks ≥ max_smoke_ICTX (else corpus
   assembly is broken).

## Pre-mortem (3 failure causes)

1. **Corpus-B exhaustion at large ICTX** — relevant chunks duplicate because
   train_b has too few distinct K-byte slices. Inflates retrieval (each query
   matches a clone) and produces fake positive scaling. Mitigation: validate
   `distinct_chunks ≥ ICTX` per seed; report this as criterion 5; verdict
   `INSUFFICIENT_CORPUS` if violated.

2. **Pool retrieval collapse** — at large ICTX, softmax over similarities
   concentrates on a single near-duplicate; pool retrieval becomes 1-NN, gain
   plateaus. Looks like saturation in the substrate but is a retrieval issue.
   Mitigation: report per-ICTX pool entropy; verdict `POOL_COLLAPSE` if
   entropy < 1.0 nat at largest ICTX.

3. **Phase-A overfitting masks the ICL signal** — substrate W already encodes
   so much of Corpus A that residual bpc gap is small and noisy. Could give
   fake-flat scaling. Mitigation: report ALPHA=0.0 baseline alongside, and
   require irr/rel gap (which doesn't depend on W) to scale.

## Parameter-matched non-bio control

This test is not brain-inspired (no neuromodulator claim). The control is
the irr arm: same number of augmentations, same pool structure, but drawn
from Corpus A (training distribution) instead of Corpus B (eval distribution).
If the substrate "ICL" effect were artifactual — just pool-size noise — irr
and rel would scale the same. The DIFFERENCE between them is what we
attribute to ICL.

## Carnap operational definition

ICL_gain(ICTX) := mean over 3 seeds of [irr_bpc(ICTX) − rel_bpc(ICTX)] on
held-out test_b. irr_bpc is bpc on test_b when the substrate pool is
augmented with ICTX random K-byte chunks from train_a. rel_bpc is the same
but augmented from train_b. The substrate, pool baseline, eval batches, and
seed are identical between the two arms; only the augment source differs.

slope := least-squares slope of ICL_gain[i] vs log2(ICTX[i]) over the 5 ICTX.

## Cited mechanism / sources

- kNN-LM: Khandelwal et al. 2020 (arXiv:1911.00172). Predicts ~log-linear bpc
  improvement vs neighbor count up to corpus exhaustion.
- Plate 1995 / Kanerva 2009: pool-based associative retrieval as bundle
  cleanup.
- This substrate's prior wins: [`wave14d_icl_via_pool_v2`] positive at
  ICTX ≤ 2048, ALPHA=0.3; [`wave14d_icl_via_pool_K8`] positive at K=8.

## Expected runtime

- Smoke (N=1024, ICTX={16, 64}, 1 seed, 1 epoch, BATCH_SIZE=32): ~3–8 s on CPU
- Full (N=4096, ICTX={64, 256, 1024, 4096, 16384}, 3 seeds, MAX_EPOCHS=10):
  estimated 4–12 min on the workstation GPU. Phase-A train dominates;
  per-ICTX evals are cheap matmuls.

If full mode exceeds 15 min, halve MAX_EPOCHS and re-prereg.

## What product decision this enables

- `VALIDATED` → "log-linear ICL up to 16384 examples at the tested width"
  becomes a defensible capability claim. Closes the Tier-S #1 ICL gap.
- `WEAK` → log-scaling story holds but bounded; capability stays ✅ with a
  saturation caveat in the cap_map.
- `INVERTED` → retraction. Bet 1 closes ❌. Strategy re-prioritizes.
- `POOL_COLLAPSE` or `INSUFFICIENT_CORPUS` → re-run after fixing the
  identified upstream issue, not a substrate verdict.
