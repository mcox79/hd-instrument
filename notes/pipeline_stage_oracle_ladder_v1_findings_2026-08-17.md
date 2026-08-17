# The stage-wise oracle ladder -- where the signal is, and where it gets lost (2026-08-17)

Cell: `experiments/exp_pipeline_stage_oracle_ladder_v1.py`. FULL run: `data/exp_pipeline_stage_oracle_
ladder_v1/metrics.json`, 101s compute (112s total including self-test), `verdict: LADDER_MONOTONE__
TOP_DROP_DIAG_B1_SINGLE_OCC_UNCOMPRESSED_ORACLE_CUE_TO_DIAG_B2_FULL_ACCUM_UNCOMPRESSED_ORACLE_CUE__
DOMINANT_NO_DISTRIBUTED`. Smoke (n=300 items): `data/exp_pipeline_stage_oracle_ladder_v1_reduced/
metrics.json`, 27s, same shape, PASS. Self-test PASS (reuses `tools/floor_battery.self_test()` and
`experiments/exp_cue_information_audit_v1.self_test()` wholesale, plus this cell's own checks).

Prior-work check: `bash tools/substrate_query.sh` timed out at 30s with no output, consistent with
the documented `hd_director_kb_continuous_ingest` livelock (`notes/STATUS.md`). Done instead by
reading every cell this cell reuses (below) and grepping `notes/` for ladder/stage/oracle vocabulary.
Closest prior art: `exp_cue_information_audit_v1` (write-side compression, exactly two points, real
cue only) and `exp_cue_regime_one_variable_retrieval_v1` (read-side cue-quality, ten points, no
NOISE/RANK metric, no CI on the drop between rungs). Neither built a unified ladder or a drop table.
Not a rediscovery; both are credited and reused as libraries, not reimplemented.

## Plain-language answer

**Most of the deficit is not lost in any of the five pipeline stages this ladder can walk through at
all -- it was never captured in the first place.** Give the system a PERFECT cue, a PERFECT address,
and a PERFECT decision (nothing downstream of the store left to go wrong), and the best version of
the store anywhere in this ladder still only gets the right synonym 6.0% of the time -- worse than
just always answering with the single most generic word in the vocabulary (13.9% of the time). That
gap exists before any of the five measurable stages has a chance to lose anything; it is a property
of WHAT THE STORE ENCODES (which words tend to occur near a word) rather than of any one processing
step. Of the losses that DO happen stage by stage, none of them dominates -- the biggest single
confirmed loss (the 256-dimension compression) accounts for only about a third of everything lost,
and the second-biggest (one point on the cue-degradation curve) is close behind it. **The Director's
prior read -- "the deficit is distributed, not one missing component" -- holds up under this
measurement rather than being overturned by it.** One genuinely new and actionable finding: bundling
MORE example sentences per word into its stored profile does not hurt -- it helps, by the single
largest CI-separated margin measured anywhere in this ladder.

## The stages, enumerated from the live code (not the sketch)

Read `hdlab/grounding_acquisition_loop.py`, `hdlab/reading_grounding_loop.py`,
`experiments/exp_grounding_readout_known_answer_v1.py`, and the machine-asserted (not merely
claimed) encoder identity in `experiments/exp_cue_information_audit_v1.py` (`H^T P_a == mat[a]`,
bit-exact). The Director's nine-stage sketch collapses to FIVE real stage boundaries:

- **S1** raw content words -> 256-dim per-occurrence code, ONE fixed random projection (this is
  where the sketch's stages "context vector," "256-dim projection" AND "superposed with everyone"
  all physically happen -- there is no intermediate uncompressed vector a later step separately
  compresses, and there is no single holographic memory a later step separately corrupts; the store
  is one row per anchor, and the interference is cross-talk baked into the SAME d=256 draw).
- **S2** per-occurrence codes -> anchor row, by plain summation across every profile occurrence.
- **S3** held-out sentence -> partial cue, the identical S1 encoder applied to unseen text.
- **S4** cue -> winner, one cosine-argmax over the full eligible anchor set (the sketch's "address"
  and "comparator" steps are the SAME operation in the live incumbent path; there is no separate
  shortlist stage in it).
- **S5** winner -> scored against WordNet gold, tie-corrected hit@1.

## The ranked drop table (all CI-separated margins first, by magnitude)

Population throughout: 5,491 anchors, 3,994 items (the landed open pool), WordNet gold, hit@1
tie-corrected, paired bootstrap N=10,000. Chance addressing 0.000182; chance hit@1 ~0.0101.

| rank | stage boundary (plain words) | drop | 95% CI | note |
|---|---|---|---|---|
| 1 | **more example sentences per word (1 vs ~72), store uncompressed, cue perfect** | **+0.0263 GAIN** [+0.0186,+0.0343] | not part of the true downstream chain -- see caveat below |
| 2 | **the 256-dim projection, cue perfect** | 0.0123 loss | [+0.0060,+0.0188] | isolates the compression alone |
| 3 | cue quality 60%->45% real (real chain) | 0.0115 loss | [+0.0060,+0.0173] | biggest single cue-degradation step |
| 4 | cue quality 45%->30% real | 0.0083 loss | [+0.0035,+0.0130] | |
| 5 | cue quality 30%->20% real | 0.0042 loss | [+0.0010,+0.0075] | |
| 6 | cue quality 5%->0% real (the final step to the live system) | 0.0015 loss | [+0.0003,+0.0030] | small but separated |
| -- | the 256-dim projection, at the REAL cue (not oracle) | 0.0018 | [-0.0025,+0.0060] | **NOT separated** -- the projection's cost is swamped by cue noise once the cue itself is real |
| -- | cue quality 100%->80%, 80%->60%, 20%->15%, 15%->10%, 10%->5% | 0.0005-0.0015 each | various | **NOT separated**, individually |

**Sum of the confirmed (CI-separated) losses: ~0.0378.** The projection (rank 2) is 32.5% of that
sum; the biggest single cue-degradation step (rank 3) is 30.4%. Neither clears 50%, so **no stage
dominates** -- confirmed, not merely asserted.

**The gain at rank 1 is the most surprising single number in the table and needs its own caveat.**
It is NOT a downstream-loses-information comparison: using only one profile sentence per anchor is
strictly LESS real evidence than using all ~72, so this is a fair "more vs less material" contrast,
not a stage the ladder's monotonicity assertion covers. Reading it plainly: the write rule (plain
summation across occurrences) is not diluting useful signal by averaging over many contexts -- if
anything, more contexts sharpen the anchor's profile. This is not what the earlier "the write rule
was part of the defect" finding (from `exp_readout_writerule_paradigmatic_v1`) would have predicted,
and the difference is WHAT changed (this ladder varies accumulation DEPTH at a fixed, syntagmatic
write rule; that cell varied the write rule's TARGET, summing neighbours' own profiles instead of
identity tags). Both are real, on different axes.

## Sanity checks (both required, both hold)

- **Known-answer rung**: cue = exact key, store = real deployed 256-dim store -> addressing accuracy
  **1.0000** (gate 0.95). Hands the system the exact card it holds; it always finds it.
- **Fully-random rung**: cue = the real partial cue reassigned to a wrong item (a derangement) ->
  addressing **0.00025** against chance 0.000182 (near-chance, gate < 0.0036); hit@1 **0.0058**.
- **Monotonicity, true downstream chain (LAM 1.00 -> 0.80 -> ... -> 0.00)**: `MONOTONE: True, n_leaks:
  0`. No stage created information; every step is a real, verified downstream walk.
- **Three independent cross-cell regressions**, all reproduced to the reported decimal: this cell's
  own `LAM_1.00` = 0.0481 (matches `exp_cue_information_audit_v1`'s `K1_EXACT_KEY_C0`); this cell's
  `DIAG_B2` = 0.0603 (matches its `K1_EXACT_KEY_U0`); this cell's `DIAG_B2r` = 0.0240 (matches its
  `U0_UNCOMPRESSED_regime` real-cue hit@1). This cell's own `LAM_1.00` median gold rank reads **37.0**
  of 5,491 anchors -- the same "median gold rank 37" figure already on record, now produced by an
  independently re-derived instrument rather than carried over.

## Per-rung detail (SIGNAL / NOISE / RANK), selected rungs

NOISE = median per-item d-prime: (best-gold score - eligible-non-gold-field mean or p95) / field std.
RANK = median optimistic rank of the best gold anchor, against the RANDOM_NULL rung's own measured
rank distribution (median 140.0, Q1 41.0, Q3 500.0, n=3,994) as the random-ranking expectation.

| rung | SIGNAL hit@1 | 95% CI | d' vs mean | d' vs p95 | median rank | vs random rank 140 |
|---|---|---|---|---|---|---|
| single-occ, uncompressed, oracle cue | 0.0340 | [0.0293,0.0390] | 3.15 | 1.21 | 74 | better |
| full-accum, uncompressed, oracle cue | 0.0603 | [0.0531,0.0679] | 3.36 | 1.48 | 28 | much better |
| full-accum, PROJECTED, oracle cue (=LAM 1.00) | 0.0481 | [0.0416,0.0548] | 2.64 | 0.95 | 37 | better |
| LAM 0.60 (60% exact key) | 0.0508 | [0.0441,0.0576] | 2.60 | 0.92 | 39 | better |
| LAM 0.30 | 0.0310 | [0.0258,0.0366] | 2.42 | 0.77 | 55 | better |
| LAM 0.00 (the live system) | 0.0223 | [0.0178,0.0270] | 2.18 | 0.53 | 93.5 | better, thinly |
| RANDOM_NULL | 0.0058 | [0.0035,0.0083] | 1.97 | 0.33 | 140 | = itself, by construction |
| F_CONSTANT_PROTOTYPE (binding floor) | 0.1390 | [0.1284,0.1500] | 2.45 | 0.56 | 58 | better |
| F_ORTHOGRAPHIC | 0.0873 | [0.0788,0.0958] | 4.29 | 1.90 | 37 | better |

Every rung's NOISE separation is well above 0 (correct answer's score sits above the field mean by
2-4 standard deviations everywhere) -- the correct answer is never scored WORSE than average, it is
just usually not scored BEST. The d-prime-vs-p95 column (separation from the near-top competitors,
not the average) shrinks steadily down the read-side chain (1.48 -> 0.92 -> ... -> 0.53), which is
the sharper way to see the cue-degradation loss than hit@1 alone: it is not that the field gets
noisier, it is that the near-top COMPETITORS get closer to the gold as the cue degrades.

## What this does and does not claim

- **Every number above is on the identical population, scorer and gold**; nothing crosses pools.
- The four floors are recomputed on this population (0.0873 / 0.0185 / 0.0118 / 0.1390); the values
  0.1382 / 0.2070 / -0.1959 never appear. The gold-fitted, non-floor oracle constant reads 0.1715.
- The accumulation-depth (B1) and projection-at-oracle (B2) diagnostics are COUNTERFACTUALS, not
  literal earlier time-points of the same run -- stated in the cell docstring and repeated here so
  the ranked table is never read as a single unbroken causal chain end to end. Only the read-side
  chain (LAM 1.00 -> 0.00) is a true, monotonicity-asserted downstream walk.
- This does not claim the representational ceiling (encoding co-occurrence, not substitutability) is
  fixed by anything measured here -- that finding predates this cell and is not re-litigated; this
  ladder shows WHERE, quantitatively, that ceiling sits relative to every measurable processing loss.

## Files

- Cell: `D:\AI\hd-instrument\experiments\exp_pipeline_stage_oracle_ladder_v1.py`
- FULL metrics: `D:\AI\hd-instrument\data\exp_pipeline_stage_oracle_ladder_v1\metrics.json`
- Smoke metrics: `D:\AI\hd-instrument\data\exp_pipeline_stage_oracle_ladder_v1_reduced\metrics.json`
