# Pre-registration: wave14w_icl_extended

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14w_icl_extended.py](../experiments/exp_wave14w_icl_extended.py)
Priority source: follow-up to validated [wave14d_icl_via_pool_v3_scaling](../experiments/exp_wave14d_icl_via_pool_v3_scaling.py)
(ICL_SATURATION_VALIDATED at ICTX=16384, slope +0.1425)
Author: experiment_dev session, pipeline tick 8

## Why

Bet 1 closed clean at ICTX=16384: slope of mean_gain vs log2(ICTX) = +0.1425
> 0.10 threshold, gain at ICTX=16384 = +1.4148, no collapse vs ICTX=4096.
The kNN-LM-like log-linear ICL story was validated through the tested range.

What we don't know: where does it actually saturate? The substrate's
relevant-example bandwidth at N=4096 isn't infinite; eventually the pool
retrieval should plateau (corpus exhaustion OR pool entropy collapse OR
substrate noise floor).

v4 = ICL extension. Same setup as v3 but extended ICTX range
{4096, 16384, 32768, 65536} (the top half of the curve, sampling the
plateau if there is one). Outputs: saturation point or "no saturation
through ICTX=65536."

## Hypothesis

At N=4096, ALPHA=1.0, 3 seeds, ICTX in {4096, 16384, 32768, 65536}:

- gain at ICTX=65536 > gain at ICTX=16384 (capability continues to
  scale, no plateau detected)
- OR gain plateaus at some ICTX in {32768, 65536} (saturation point
  found)

## Multi-probe success criteria (4 outcomes)

The verdict characterizes the saturation behavior:

- `ICL_EXTENDED_NO_SATURATION`: slope on log2(ICTX) across all 4 points
  > +0.10 AND gain at ICTX=65536 > gain at ICTX=16384 by more than 1σ
- `ICL_EXTENDED_SOFT_SATURATION`: gain at ICTX=65536 > gain at ICTX=16384
  but slope across the upper half (ICTX ≥ 16384) is < 0.05 (plateau
  starting)
- `ICL_EXTENDED_SATURATION_AT_<I>`: gain at ICTX=<I> peaks; subsequent
  ICTX values give equal or lower gain (within 1σ)
- `ICL_EXTENDED_DECAY_AT_HIGH_ICTX`: gain at ICTX=65536 < gain at
  ICTX=16384 by more than 1σ (capability reverses — interesting failure
  mode)

Plus criterion shared with v3: pool entropy at largest ICTX ≥ 1.0 and
distinct_chunks count at largest ICTX = ICTX (corpus not exhausted).

## Kill criterion

Pool retrieval entropy < 1.0 at any tested ICTX → `ICL_POOL_COLLAPSE_AT_<I>`
(saturating because retrieval collapsed, not because substrate plateau).

Distinct relevant chunks < ICTX at any tested ICTX → `ICL_CORPUS_TOO_SMALL`
(test setup off; corpus exhausted).

## Verdict labels (6)

- `ICL_EXTENDED_NO_SATURATION`
- `ICL_EXTENDED_SOFT_SATURATION`
- `ICL_EXTENDED_SATURATION_AT_<I>`
- `ICL_EXTENDED_DECAY_AT_HIGH_ICTX`
- `ICL_POOL_COLLAPSE_AT_<I>` or `ICL_CORPUS_TOO_SMALL` (kill)
- `ICL_EXTENDED_INCONCLUSIVE`

## Oracle assertions (smoke mode)

1. `oracle.assert_in_range("rel_bpc_smoke", rel_bpc_smoke_max, (0.5, 8.0))`
2. distinct_chunks at smoke max ICTX >= ICTX (sanity on corpus assembly)

## Pre-mortem (3 failure causes)

1. **Corpus B exhaustion at ICTX=65536**: Corpus B (experiments/*.py)
   is ~2.4 MB; chunks of K=4 give ~2.4M distinct K-byte positions. Plenty
   for 65536. But test_b portion (~700KB after 70/30 split) gives ~700K
   chunks. Mitigation: explicit distinct_chunks count + corpus-too-small
   kill criterion.

2. **GPU memory at pool_used + 65536 ≈ 70K vectors of N=4096**: ~1.15 GB
   in float32. Should fit on workstation GPU; if OOM, the experiment
   crashes early. Mitigation: smoke catches at small scale; full mode
   would surface OOM in runtime logs.

3. **Slope misleading at non-uniform spacing**: log2(ICTX) values 12, 14,
   15, 16 (for 4096, 16384, 32768, 65536) are not equally spaced. Slope
   computed by least-squares on log2 scale is fine but interpretation as
   "per doubling" needs care. Mitigation: report per-pair slope (between
   adjacent ICTX) as well as overall slope.

## Operational definition

Reuses [exp_wave14d_icl_via_pool_v3_scaling.py](../experiments/exp_wave14d_icl_via_pool_v3_scaling.py)
infrastructure: same corpus assembly, same training, same
augment_pool_dynamic, same eval_with_pool.

Differences:
- ICTX_FULL = [4096, 16384, 32768, 65536]
- 3 seeds (same as v3)
- Verdict logic is different (characterizes saturation, not the
  log-linear-extends-to-16384 question)

## Cited mechanism / sources

Same as v3. This is an ICTX-axis extension of v3's exact mechanism.

## Expected runtime

- Smoke (N=1024, ICTX=[256, 1024], 1 seed, 1 epoch): ~5-10 s on CPU
- Full (N=4096, ICTX up to 65536, 3 seeds, 10 epochs):
  estimated 5-12 min on GPU. Pool eval at ICTX=65536 is the dominant
  cost (~30s per eval, 6 evals = 3 min plus train).

## What product decision this enables

- `NO_SATURATION` → ICL scaling extends arbitrarily; cap_map row
  upgrades with explicit "tested through ICTX=65536"
- `SATURATION_AT_<I>` → cap_map row gets explicit operating ceiling
- `DECAY_AT_HIGH_ICTX` → surprising finding; would suggest the substrate
  has a noise floor that breaks at very high ICTX. Routes to mechanism
  investigation.
- `POOL_COLLAPSE` / `CORPUS_TOO_SMALL` → test-setup issue, re-run after fix.
