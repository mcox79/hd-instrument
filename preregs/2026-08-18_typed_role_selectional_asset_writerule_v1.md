# Pre-reg: exp_typed_role_selectional_asset_writerule_v1

## Question
Does a word's code, built from the TYPED grammatical slots (verb+ROLE) it fills, encode
substitutability better than the incumbent bag-of-words store, as measured by
`exp_dissociation_score_instrument_v1`'s licensed AUC instrument (SET P = WordNet-synonym,
zero-cooccurrence pairs; SET S = top-cooccurring, non-synonym pairs; both NOUNS)?

## Prior art (credit)
`experiments/exp_dependency_context_codebook_location_artifact_v1.py` (+ `_weight_sweep_v2`):
same PPMI+SVD pipeline, dependency-typed vs window co-occurrence feature. NEVER RUN (no `data/`
dir) -- unproven, not refuted. Cites Levy & Goldberg 2014 (typed relations shift induced
similarity toward co-type) and Komninos & Manandhar 2016 (window+dependency combined beats
either alone); both credited here too. Reuses `exp_learned_codebook_generalization_gate_v1
.build_ppmi` (Levy-Goldberg 2015 context-distribution-smoothed PPMI) unmodified, the same
function the prior-art cell itself reused.

## SCOPE CAVEAT -- CORPUS CONFOUND, disclosed not hidden
A0_INCUMBENT is DSI's regression-gated arm, built from the project's own 34,169-sentence
corpus (`exp_cue_information_audit_v1`). T1/T2/T3's typed-role features are built from
`data/selectional_preferences_v1/` -- a DIFFERENT, larger (64MB, 737,488-sentence) SimpleWiki
corpus, extracted 2026-08-16 by this project's own real parser (no WordNet, no LLM). A T1-vs-A0
gap therefore conflates "typed vs bag context" with "which corpus" -- reported explicitly, never
interpreted as a clean single-variable result on its own.

A parallel, same-corpus cell exists: `experiments/exp_typed_role_context_write_rule_dissociation_v1.py`
(teammate "typed-role-writerule", self-test green as of authoring, not yet landed) parses THIS
project's own 34,169-sentence corpus directly via `hdlab.arc_parser`/`arc_labeler`/`pos_tagger`,
avoiding this confound entirely. That is the cell to trust for a clean typed-vs-bag comparison;
THIS cell is a cheaper, confounded, complementary check: does the pre-built, larger-corpus
selectional-slot asset carry substitutability signal at all. Overlap disclosed peer-to-peer via
SendMessage before authoring; teammate confirmed this is a genuinely different test (different
corpus, different coverage) worth running independently, not a duplicate.

## Population / scorer (reused verbatim, never re-derived)
`exp_dissociation_score_instrument_v1` (DSI) checkpoint `data/exp_dissociation_score_instrument_v1
/units.jsonl`, key `POPULATION|v1.7|full`: 242 matched (SET P, SET S) noun pairs per cell,
frequency/length/POS/orthography/constant-prototype matched. `SCORES|v1.7|full` for the 8
regression-gate values. `DSI.auc_of` / `DSI.auc_bootstrap` (Mann-Whitney AUC + paired bootstrap
CI) reused directly, not re-implemented. `DSI.dense_scores_from_dict_store` reused for pair
scoring from any word->vector store.

## Asset
`data/selectional_preferences_v1/selectional_slots_v1.pkl`: `slot_filler` dict keyed
`(verb, ROLE)` -> `{filler_word: count}`. 41,529 slots, 944,990 observations, ROLE in
{SUBJ, OBJ, IOBJ, obl:*}. MEASURED (this cell's own pre-authoring probe): 617 distinct words
needed across the 242+242 matched pairs; 555/617 (90.0%) have >=1 slot-filler count in this
asset; 218/242 SET P pairs and 185/242 SET S pairs have BOTH members covered.

## Regression gate (MANDATORY, EXIT ON FAILURE before anything else runs)
Recompute POINT AUC (`DSI.auc_of`, deterministic, bootstrap-independent) on the SCORES|v1.7|full
checkpoint's raw P/S score arrays for 8 named checks, assert `abs(delta) <= 0.0005` against the
cached values below (each `MEASURED@d:/AI/hd-instrument/data/exp_dissociation_score_instrument_v1
/metrics.json:report.AUC_PER_ARM.<name>.auc`):
- F_ORTHOGRAPHIC = 0.5000, F_FREQUENCY = 0.4901, F_SCRAMBLE = 0.4664,
  F_CONSTANT_PROTOTYPE = 0.5431 (max of the four -- THE BAR)
- KNOWN_ANSWER_WORDNET_PATH_SIM (K1) = 0.9599
- RANDOM_VECTOR_STORE (N0) = 0.4862
- INCUMBENT_LIVE_STORE (A0) = 0.0710
- RAW_COUNT_FULL_ACCUM = 0.0510
Any miss -> `SystemExit`, cell publishes only the regression-gate failure (STOP-IF v).

## Arms
- **A0_INCUMBENT**: DSI's cached INCUMBENT_LIVE_STORE arm, cited not rebuilt.
- **T1_TYPED_ROLE**: word x (verb,ROLE) count matrix over the 617 words needed (built from the
  asset, restricted to words actually needed -- MEASURED: 101,021 nonzero entries, 20,600
  distinct (verb,ROLE) columns used, 555/617 rows nonzero) -> `build_ppmi` (Levy-Goldberg
  smoothed) -> `TruncatedSVD` rank 128 (`algorithm=randomized, n_iter=5`) -> L2-normalized rows.
  The arm this cell exists for.
- **T2_UNTYPED_SAME_COVERAGE**: T1's matrix with the ROLE axis collapsed -- columns become VERB
  only (MEASURED: 5,536 distinct verbs), identical nonzero support/contributing words, role label
  stripped. Same PPMI+SVD pipeline, same target rank 128. Isolates word-selection from typing.
- **T3_COMBINED**: `L2norm(T1) concat L2norm(A0)`, L2-renormalized (Komninos & Manandhar 2016
  recipe, same `combine_method` string as the prior-art cell).
- **N1_LABEL_PERMUTED**: T1's raw count matrix with the nonzero entries' COLUMN index permuted
  (fixed seed; same design pattern as the prior-art cell's `build_random_context_cooc` --
  preserves row mass, destroys word<->slot-type association), then same PPMI+SVD pipeline.
  Must-fail identity control.
- **N3_MAGNITUDE_PERMUTED**: T1's raw count matrix with the nonzero entries' DATA (count) values
  permuted across the SAME (row,col) support (fixed seed) -- preserves exactly which word fills
  which slot, destroys the magnitude/frequency information. New control, not reused from prior
  art; tests whether count-weighting (vs mere presence) carries the signal.
- **N5_COVERAGE_MATCHED**: T1's own embeddings, pairs restricted to those where BOTH members are
  covered by the asset (MEASURED: SET P 218/242, SET S 185/242). Reports n before/after.
- **K1** (`KNOWN_ANSWER_WORDNET_PATH_SIM`) and **N0** (`RANDOM_VECTOR_STORE`): cited from the
  regression gate, calibration/null only, not rebuilt.

## Bands
Bar = max(4 floor AUCs) = 0.5431 (F_CONSTANT_PROTOTYPE), NOT 0.5. Every margin reported against
BOTH. "CI-separated above X" = 95% CI lower bound > X. "A beats B" (dominance) = A's CI lower
bound > B's CI upper bound (whole-CI separation, non-overlapping).

## STOP-IF (evaluated in this order)
0. Regression gate OR DSI's own floor-licensing fails -> publish only that (`REGRESSION_GATE_
   FAILED`), no arm number interpreted.
1. T1 CI-separated above bar AND dominates T2, N1, AND N5 independently CI-separates above bar
   -> `HARD_PASS_FIRST_TYPED_WRITE_RULE` (the win survives role-stripping, permutation, and
   coverage restriction).
2. T1 dominates A0 but NOT T2 -> `WORD_SELECTION_NOT_TYPE` (gain is which words co-occur as
   arguments, not the role label).
3. T1 dominates A0 but N5 does NOT independently clear the bar (or drops CI-separated below T1's
   full-population AUC) -> `COVERAGE_ARTIFACT`.
4. T1 ties A0 (CIs overlap, neither dominates) -> `TYPED_STRUCTURE_NO_HELP` -- last unexplored
   write-rule axis (per the dispatch brief) closes on this asset.
5. Otherwise -> `PARTIAL_UNRESOLVED`, report the numbers, no verdict forced.

## Pre-registered priors (deflated, stated before running)
P(HARD_PASS, outcome 1) = 0.15; P(outcome 2, word-selection-not-type) = 0.20;
P(clean negative, outcomes 3/4) = 0.45; residual (partial/unresolved) = 0.20.

## Compute architecture
Sequential-CPU, single-threaded (OMP/OPENBLAS/MKL pinned to 1). Wall time < 10s for population
load; PPMI+SVD on <=617x20600 sparse matrices at rank 128 measured in the low single-digit
seconds; bootstrap AUC (N_BOOT=10000 full / 1500 reduced) over ~200-length arrays for 6 new arms.
Total expected wall time well under 2 minutes -- run FOREGROUND to completion (INLINE-LOCAL
mandate: light compute runs fast in the foreground, not detached/backgrounded).
Storage: no_storage (representation-only cell, no composition/chaining).

## Cell-template mandates
arms_differ_verified (sha256 over {T1,T2,T3,N1,N3} + A0-from-checkpoint score vectors, >1
distinct digest); final_metrics_atomicity=tmp_replace; except SystemExit: raise BEFORE except
Exception (no bare except, no BaseException); per-unit checkpoint (POPULATION/SCORES reused
read-only from DSI; this cell's own SCORES_TYPED as one checkpointed unit); discriminator
survives scale (full population run, no scale-preview needed -- population is fixed/licensed by
DSI, not swept); calibration_check=default_ok_for_this_regime (reuses DSI's licensed instrument
unmodified); progress_logging=print_flush_true; baseline_in_band=n/a (dissociation-AUC licensing
instrument, not a 0.05-0.95-band baseline, declared explicitly); crlb_floor_computed=n/a
(AUC dissociation measurement, not a capacity sweep, declared explicitly); deterministic_seeding
true (fixed integer seeds throughout, no hash()/list(set()) ordering).

ASCII-only. NO LLM anywhere in this runtime path. CPU only. `data/foundation/**` never opened.
Writes only under `data/exp_typed_role_selectional_asset_writerule_v1[_reduced]/`.
Not wired into `hdlab/`.
