# HUMAN-JUDGEMENT INSTRUMENT v2: `POWER_INSUFFICIENT` AT n=7, CONFIRMED AND NOW HONESTLY RECORDED

**2026-08-18. `experiments/exp_dissociation_score_instrument_human_v2.py`, commit pending. FULL run
completed to a clean `metrics.json` (7.2s) at `data/exp_dissociation_score_instrument_human_v2/`.**

## What changed from v1, and what did not

v1 (`experiments/exp_dissociation_score_instrument_human_v1.py`, commit `3f498cf52`) halted with a
bare `SystemExit` at `n_match=7` (below its own `n_match<20` floor) and wrote **no** metrics.json.
That file is left untouched -- it is the permanent record of the null and is cited by
`notes/human_judgement_instrument_power_failure_2026-08-18.md`.

v2 is a new file, not an edit of v1. Its **population and matching construction are byte-identical**
to v1's: `combine_benchmark_pairs(anchor_set)` is called over the full 5,491-anchor set (never
restricted to the WordNet-licensed instrument's own, much smaller, matched population), and
`DSI.match_cells` is reused verbatim with the same per-dimension caliper. Verified off v1's own
checkpoint (`data/exp_dissociation_score_instrument_human_v1/units.jsonl`, unit
`POPULATION_HUMAN|v1.0|full`) before touching any code.

What v2 changes is **process**, not population or caliper:
1. The `SystemExit`-with-no-metrics-file at `n_match<20` is replaced with an explicit
   `POWER_INSUFFICIENT` verdict **written to metrics.json** with the full funnel, at a raised
   threshold `n_match < POWER_INSUFFICIENT_MIN_N=60` (per the dispatch brief).
2. The **license gate** (four floors + known-answer + random-store, all cheap -- no matrix rebuild)
   now runs and is checked **before** any of the seven expensive re-scored arms
   (INCUMBENT/RAW_COUNT/PARADIGMATIC/T0/T2), so an unlicensed population never pays for a PPMI+SVD
   rebuild.
3. `max(four floors)` is computed and reported as the real bar, not 0.5, per plan sec 6.29(1)'s
   correction. On the WordNet instrument this reads **0.5431** (`F_CONSTANT_PROTOTYPE`), verified
   fresh off `data/exp_dissociation_score_instrument_v1/metrics.json` at run time.

## Why n=7, measured (not guessed) -- correcting the record

The dispatch brief that commissioned this rebuild attributed v1's collapse to "restricting itself to
the other instrument's population" (the WordNet instrument's 617 scored words). **That is not what
v1's code did.** v1's own checkpoint diagnostics show the actual mechanism:

- `matching.pre_match_smd.mean_log_freq = -1.8396` -- `SET_P_HUMAN` (human-rated similar, zero
  corpus co-occurrence) pairs are structurally far rarer than `SET_S_HUMAN` (highly co-occurring)
  pairs. This is not an artifact: rare words are more likely to be human-judged similar and never
  co-occur in a 34,169-sentence corpus; frequent words co-occur a lot.
- The matching caliper's frequency covariates (`mean_log_freq`, `abs_freq_diff`) are capped at
  `0.02` (i.e. `|z-diff| <= 0.14` SD) -- tightened to that value specifically during the WordNet
  instrument's own four-round matching repair (`exp_dissociation_score_instrument_v1.py`,
  `DEFAULT_CALIPER_SQ_PER_DIM`), reused here verbatim per the standing rule against loosening a
  caliper to buy sample size.
- Result: **429 of 436 SET_P_HUMAN candidates (98.4%) are caliper-dropped.** By POS stratum:
  adjective (19P/3S) and noun (47P/27S) strata drop to **zero** matches; verb (370P/92S) yields the
  seven pairs that survive.

This funnel (`2,233 -> 436/122 -> 7`) reproduced **exactly** on this rebuild, as expected for a
byte-identical, seeded, deterministic construction. It is a genuine structural finding about this
population's frequency geometry under a caliper honestly inherited from a different instrument, not
a restriction bug.

## Full funnel, this run

| stage | n |
|---|---|
| benchmark pairs (SimLex-999 + SimVerb-3500) restricted to the full 5,491-anchor set | 2,233 |
| `SET_P_HUMAN` raw candidates (zero co-occurrence, score >= 6.0) | 436 |
| `SET_S_HUMAN` raw candidates (>= decile-90 co-occurrence, score <= 4.0) | 122 |
| matched (per-dimension caliper, reused verbatim) | **7 per cell** |

`POWER_INSUFFICIENT_MIN_N = 60`. 7 < 60 -> **STOP-IF (0) fired.** No floor, known-answer,
random-store, or expensive arm was built or scored. `metrics.json` records this cleanly:
`verdict = DISSOCIATION_INSTRUMENT_HUMAN_UNLICENSED__POWER_INSUFFICIENT__n_match=7__min_required=60__STOPPED_BEFORE_ANY_ARM`.

## What is and is not resolved

- **Licensed:** N/A -- not reached. No floor was scored on this population.
- **max(four floors):** not recomputed on this population (no arms scored); the WordNet instrument's
  own value, 0.5431, is carried in the metrics.json `WORDNET_INSTRUMENT_CONTEXT_MAX_FLOOR_AUC` block
  as context only, read fresh off disk, never interpreted as a finding about this population.
- **Rank correlation (the decisive number):** not computed. No arm was scored on either side of the
  comparison for this run.
- **Plan sec 6.24's WordNet-scope caveat: still OPEN, not resolved in either direction.** A null here
  is not evidence the WordNet dependency was harmless -- the same standing rule that governed v1's
  read applies unchanged.
- **One plain sentence:** this run cannot say whether Organ A's closure is about our store or about
  WordNet; the SimLex/SimVerb population, honestly matched with the same caliper the WordNet
  instrument required, is too thin at the zero-co-occurrence/high-similarity/frequency-matched
  intersection to support the comparison, and that is a property of this population's frequency
  geometry, not of the matching's leniency.

## What would actually answer the question (unchanged from v1's own assessment)

A benchmark with far greater coverage of the 5,491 anchors; or a label source that does not require
zero co-occurrence by construction; or an operationalisation of substitutability that is neither
WordNet-derived nor dependent on a small curated pair list (e.g. held-out cloze interchangeability
measured on our own corpus, which has no coverage ceiling). Each needs its own circularity audit.

## DO NOT

- Do not loosen the caliper on a future attempt to buy n -- that produces a bigger sample of an
  unlicensed instrument, which plan sec 6.27/6.29 already established is worse than no sample.
- Do not re-run this exact construction hoping for a different draw -- it is deterministic and will
  reproduce n=7 every time, as it just did.
- Do not read "n=7, twice" as evidence the WordNet dependency is harmless or harmful. It is silent on
  that question.

**Status: v2 is committed as a corrected, process-honest re-run of the same structural null v1 found.
v1 is untouched and remains the primary historical record. Neither file is wired or registered; no
capability claim follows from either.**
