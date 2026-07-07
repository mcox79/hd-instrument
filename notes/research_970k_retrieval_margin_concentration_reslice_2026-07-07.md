# Bounded convergence drill -- is the encoder's retrieval margin concentrated in Test 0's near-dup pool?

Date: 2026-07-07. Owner: research (Sonnet). Trigger: USER-directed bounded CONVERGENCE drill,
CPU-only, re-slice EXISTING results, no GPU, no new cell. Follows
`notes/research_970k_kb_near_duplicate_density_test0_2026-07-07.md` (Test 0), which found a
15.86%-of-V near-duplicate pool (document-chunk siblings + WordNet polysemy) in the 970K KB and
named "re-slice existing keyed@J5/shuffled_key per-item results by chunk-vs-non-chunk membership"
as the single highest-value next CPU-only action.

## HEADLINE

**The re-slice cannot be performed -- not because the numbers come out ambiguous, but because the
per-item data it requires was never written to disk.** I pulled every `metrics.json` in the
encoder lineage at or near production/full scale (`exp_encoder_step2step3_inbatch_rkd_shipmetric_
carrythrough_v1` seeds 7/13/23/29/31, `exp_encoder_migration_step1b_v4_joint_reverify_relock_v1`
seeds 7/13, `exp_encoder_gsbc_gradedcode_retrieval_v1` seeds 7/13, `exp_encoder_migration_step1b_
v3c_paired_rkd_only` seeds 7/13/23/29/31 -- 14 files) and every non-`metrics.json` file under
`data/exp_encoder_*` and `data/substrate_concept_encoder*` (training-data shards, checkpoints,
manifests -- 100+ files). None of them contain a per-item, per-row, or per-trial breakdown of
`keyed@J5` / `shuffled_key` outcomes. Every one stores only the reduced scalar aggregates
(`acc_at1`, `hit_any_member`, `ret_agree10`, `spearman_all`, etc.).

I then read the eval code itself to confirm this is structural, not a missing-file accident.
`experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_
core.py`:
- `_keyed_unit` (lines 790-839) draws `J`-member trials (`fi = torch.randint(0, V, (J,), ...)`),
  builds `queries` / `targets` / `members` lists that DO carry KB-row identity in memory, runs
  cleanup-argmax, computes `acc = (pred == tgt).float().mean()` and `hit_any_member`, and returns
  ONLY those two scalars plus `snr_margin_mean` and `n_trials` -- the `members`/`pred`/`targets`
  arrays that would let a re-slice classify each trial by chunk-vs-non-chunk membership are
  discarded at function return, never serialized.
- `_semantic_unit` (lines 718-758), which backs `ret_agree10`, does the same thing one level
  deeper: it computes a per-held-row top-10 rank-overlap inside a `for r in range(hi - lo)` loop
  (line 746-747) and accumulates it into a single running scalar (`agree`) before dividing by
  `n_he` -- the per-row agreement values are never retained even transiently as an array, let
  alone written out.
- `MID_TRIALS = 60` (line 172) is the trial count feeding every landed `keyed@J5`/`shuffled_key`
  number in the lineage -- even if per-trial identity had been logged, 60 trials x J=5 members =
  300 KB-row draws per unit is a thin sample for a 15.86%-vs-84.14% subgroup split (expected ~48
  draws would land in the near-dup pool by chance, per trial-run, and that count was never
  computed or retained by any run to date).

**VERDICT: neither CONCENTRATED nor DIFFUSE nor MIXED -- this is a 4th outcome, DATA-ABSENT.** The
question Test 0 posed cannot be answered by re-slicing, because there is nothing on disk to slice.
This is itself the decisive, in-scope finding for this bounded drill (an instrumentation gap in
the eval harness), not a refusal to answer.

## Cheap decisive test

This drill's designated test WAS the re-slice itself -- and executing it correctly means
confirming the data doesn't exist rather than fabricating a stratified count from aggregate
numbers. No new computation was run (per the "no new cell" / "re-slice EXISTING results"
constraint); this is a pure filesystem-and-code audit, ~10 minutes, CPU-only, zero GPU, zero
training, zero queue dispatch.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

Because no data exists to test against, the original Test 0 HARD-PASS/HARD-FAIL bands (chunk-
subset leak rate vs non-chunk subset leak rate, 1.5x / 2x thresholds) remain **UNRESOLVED**, not
refuted and not confirmed. The one new falsifiable claim this drill can register:

**HARD-PASS (instrumentation-gap claim):** if `_keyed_unit` and `_semantic_unit` are re-run with a
one-line addition (persist `members`/`pred`/`targets` for `_keyed_unit`; persist per-row `agree`
values for `_semantic_unit`) against an EXISTING already-trained checkpoint (no new training), the
resulting per-item logs will be nonempty and joinable to the KB row index used by Test 0's
chunk-membership classification -- confirming the gap is purely a logging omission, not a deeper
problem with recovering row identity. **HARD-FAIL:** the held-out split (`Xhe`) used by
`_semantic_unit` is NOT indexed by the same raw KB row order as `entities.jsonl` (i.e., there's an
undocumented reindexing between the teacher cache and the raw KB), which would mean even a
logging fix could not directly join to Test 0's chunk-membership labels without an additional
index-mapping step -- this was NOT checked in this drill (out of the strict re-slice scope) and is
flagged, not resolved.

Calibration (per [[feedback-lit-scan-calibration-penalty]]): this drill produces no new evidence
either way on Test 0's underlying substantive hypothesis (near-dup clusters produce excess
codeword/retrieval collisions). Test 0's own P_deflated (~0.35-0.45, capped at 0.50) for that
hypothesis stands UNCHANGED -- neither raised nor lowered by this drill, since this drill measured
data-availability, not the phenomenon itself.

## Cross-thread synthesis

Directly extends Test 0's own "Not measured at all" section, which already flagged that testing
the encoder's actual codeword-assignment skew for near-dup clusters "requires running the
(already-trained) distillation MLP forward pass... but was not done in this drill." This drill
confirms the STRONGER claim: it's not merely "not done yet," it's "not recoverable after the fact"
-- the historical `keyed@J5`/`shuffled_key`/`ret_agree10` numbers already landed in `metrics.json`
across the whole lineage cannot be retroactively stratified, because the eval harness itself never
retained per-item identity. This closes the loop on Test 0's named next step: there is no
cheaper-than-inference path. Any future attempt to test Test 0's structured-collision hypothesis
needs either (a) a new inference-only pass over an existing checkpoint with per-item logging
added, or (b) a fresh cell with the logging built in from the start.

## Substrate-product implications

For Director: (1) this closes out the "re-slice existing results" branch of Test 0's action list
as a dead end -- not a wasted effort, since ruling it out cheaply (no GPU, no training) is exactly
what a bounded CPU drill should do before anyone spends compute assuming the data was there. (2)
It surfaces a general eval-harness gap worth noting for any FUTURE encoder cell: `_keyed_unit` and
`_semantic_unit` are the two functions backing every ship-metric gate in this lineage, and neither
persists per-item outcomes -- so no past or current landed run can be stratified by ANY covariate
(chunk-membership, polysemy, source category, entity length, etc.) after the fact. This is a
one-line-per-function fix (append the in-memory arrays to the returned dict, or dump them to a
sibling `.npz`) if Director wants future runs to support this kind of post-hoc stratification;
that is a process observation, not a proposal to act on now, and is offered only as context for
why this specific drill dead-ended. (3) Net effect on the open question: Test 0's near-dup-pool
hypothesis (dedup as a cheap margin fix) remains exactly where Test 0 left it -- plausible
(P_deflated 0.35-0.45), mechanistically motivated, but empirically untested. Neither this drill nor
Test 0 changes the recommended posture: the near-zero-cost dedup of note/prereg chunk siblings
(shrinking V by ~14%, per Test 0 Item 3) remains a reasonable pre-scale hygiene step on its own
structural merits (reduces V, removes an identified near-dup risk pool) independent of whether the
retrieval-margin concentration hypothesis is ever directly confirmed.

## Honest bounds -- what this drill can and cannot conclude

**Solid (verified directly):** 14 metrics.json files spanning the full-scale (`teacher_n_concepts
=177899`, `n_train=160109`) encoder lineage contain no per-item retrieval outcome data, only
aggregate scalars; the eval code (`_keyed_unit`, `_semantic_unit`, `_bundle_unit` in
`exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py`)
computes per-trial/per-row identity transiently and never serializes it; `MID_TRIALS=60` is the
trial count used for every landed keyed/shuffled-key number to date; a filesystem sweep of all
non-metrics.json artifacts under `data/exp_encoder_*` and `data/substrate_concept_encoder*` found
only training shards and checkpoints, zero eval-output logs.

**Not established by this drill:** whether the held-out row indexing (`Xhe`) used by
`_semantic_unit` maps cleanly back to `entities.jsonl` row order (relevant only if per-item logging
is added later); whether adding per-item logging and re-running eval on an existing checkpoint
would actually show concentration or diffusion (that is a new inference computation, explicitly
out of this drill's "re-slice existing results, no new cell" scope, and is not run here).

This drill stops here per its own scope -- no further drill proposed.

## Citations (verified count: 0 external -- this was an internal filesystem-and-code audit, not a
literature scan, consistent with Test 0's own citation posture)
