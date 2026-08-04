# Pre-reg: does the accumulate-register decode-margin discriminate TRUE-vs-WRONG binding on goal-outcome, the way it does on coref, or does it tie like causal?

Anchor: `coherence_margin_discriminates_goal_outcome_v1`
Date: 2026-08-04. Author: exp_dev (cell author/prover role).

## Why (pointer, not re-derivation)

`notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md` Section 7 names this
the BIGGEST RISK of the coherence-based-binding-selector build: `decode_coherence_margins`
(`hdlab/self_improving_loop.py`) is DISPROVEN as a discriminator for causal antecedent selection
(`CausalLinkRegister` write-then-read is symmetric -- a wrong link decodes at the same ~0.97
fidelity as a right one, disk-verified `notes/research_drill_biology_led_causal_coherence_
credit_assignment_2026-08-03.md`) but NO ONE HAS CHECKED whether goal-outcome binding is
symmetric the same way. This cell is that check, with a coref positive control (known-live) and
the causal negative control (predicted-tie, empirically confirmed rather than merely asserted).

## What (mechanism under test)

`hdlab/self_improving_loop.py::route_passage` / `decode_coherence_margins` / `decide_keep_or_revert`
REUSED VERBATIM (no fork). Per item: a baseline (WRONG) whole-position-array cluster assignment
and one candidate (TRUE) assignment that differ ONLY at the query position; `route_passage`
computes each position's coherence margin under both assignments, aggregates the delta at the
flagged (query) position, and `decide_keep_or_revert` adopts TRUE iff its margin beats WRONG by
`> abstain_band` (default 0.02). "Discriminates" = adopt == "true".

**FAIRNESS TIGHTENING (mid-task correction from Director, both mandatory):**
1. **WRONG-owner = the recency foil, by construction, not a random/unrelated entity**, on BOTH
   the coref positive-control arm and the goal-outcome treatment arm (causal already satisfies
   this by construction -- the 4 real gold items' `distractor_agent` IS explicitly the
   most-recently-narrated/prominent agent per the gold file's own `recency_note` field). Without
   this, a "true beats wrong" win could be a token/frequency artifact instead of coherence beating
   recency, which is the actual claim under test.
2. **Shuffled-coherence control on the goal-outcome arm** (mirrors `exp_coherence_selector_
   insim_v2`'s shuffled-structure control, `data/exp_coherence_selector_insim_v2/metrics.json`,
   acc 1.0000 -> 0.2700 under shuffle). Each goal-outcome item's role_seq is rotated by 1 position
   (deterministic, same rotation applied to both TRUE-run and WRONG-run) before rerunning
   route_passage. If the margin STILL discriminates TRUE-vs-WRONG on the scrambled role structure,
   the intact-arm "win" is a positional/memorization artifact, not real coherence -- HARD-FAIL
   regardless of the raw intact discrimination number.

## 3 arms

- **ARM `coref` (POSITIVE CONTROL, n=5 items):** `role_vocab=["agent","mentioned"]`. Each item:
  TRUE owner has 1-3 prior "agent" mentions (supporting history); FOIL (the recency competitor,
  introduced more recently in the item's linear position) has 0-2 of its own "agent" mentions. The
  query position ("mentioned" = pronoun) is bound to TRUE (candidate) vs FOIL (baseline/recency).
  Must discriminate (this arm's own AccumulateRegister organ + margin mechanism is already
  validated live on dense McGuffey content, atom 29609 lineage) -- proves the harness/metric is
  not degenerate before trusting the other two arms.
- **ARM `causal` (NEGATIVE CONTROL, n=4 items, REAL gold data):** the 4 gold items in
  `data/eval_gold_mention_role_mcguffey_v1/gold_grounded_appraisal_richer_v1.jsonl`
  (`grapp_mcca_001/003/004/005`). `role_vocab=["CAUSE","EFFECT"]`. Each item is a SINGLE
  write-then-read (one CAUSE fact bound to the effect's slot, no supporting/corroborating
  events) -- this mirrors `CausalLinkRegister`'s real write pattern exactly (write ONE link,
  read it back; no accumulation). `true_blocker_agent` (candidate) vs `distractor_agent`
  (baseline) -- the gold file's own `recency_note` confirms distractor = the recency pick.
  PREDICTED: ties (near-abstain), confirming write-then-read symmetry empirically rather than
  merely asserting it from the 2026-08-03 drill.
- **ARM `goal_outcome` (TREATMENT, n=4 items):** `role_vocab=["GOAL","ACTION_AGAINST",
  "OUTCOME_UNMET","OUTCOME_MET"]` (`GoalOutcomeRegister`'s live role vocab, `experiments/
  exp_situation_model_goal_outcome_dimension_v1.py`). 2 items are structural analogs of that
  cell's own disk-verified RECENCY set (`recency_amy_blocked_pronoun_foil_jo`,
  `recency_tom_blocked_pronoun_foil_sid` -- owner blocked, own unmet outcome via pronoun whose
  true antecedent is the owner, foil more recently mentioned); 2 more synthetic items of the same
  shape for n=4. Each item: owner has a GOAL event + an owner-centric ACTION_AGAINST event
  (supporting history); foil has its own unrelated event (recency-salient, mentioned closer to the
  query). Query = OUTCOME_UNMET bound to TRUE owner (candidate) vs FOIL (baseline/recency). BOTH
  intact and shuffled-role variants are run (see fairness tightening #2).

## Bands (pre-registered before running)

Discrimination rate per arm = fraction of items (mean over seeds) where `adopt == "true"`.

- **Harness-sanity precondition** (both must hold or the goal-outcome read is untrustworthy,
  regardless of its own number): `coref_rate >= 0.8` AND `causal_rate <= 0.25`.
- **HARD_PASS:** harness-sanity holds AND `goal_outcome_intact_rate >= 0.8` AND the shuffled
  control COLLAPSES (`goal_outcome_shuffled_rate <= 0.25` OR
  `goal_outcome_intact_rate - goal_outcome_shuffled_rate >= 0.5`) => the accumulate-margin signal
  genuinely discriminates goal-outcome binding by real role-structure coherence, not artifact;
  the "SCORE reused across 2/3 instances" thesis in the build spec holds.
- **HARD_FAIL:** EITHER `goal_outcome_intact_rate` ties `causal_rate` (within 0.1) => accumulate-
  margin is the wrong quantity for goal-outcome too (the SCORE-reuse thesis collapses to 1/3, a
  real publishable negative reshaping the build) -- OR the shuffled control does NOT collapse
  (shuffled rate stays within 0.15 of intact rate) => any apparent intact-arm discrimination is a
  positional/memorization construction artifact, HARD_FAIL regardless of the raw intact number
  (per Director's explicit instruction: this overrides a naive "intact passed" read).
- **MIDDLE_BAND:** harness-sanity precondition fails (coref/causal controls underpowered or
  inconclusive at this tiny n) OR goal_outcome discriminates partially (`0.25 < intact_rate <
  0.8`) with a shuffled collapse that IS present -- right-mechanism-class/underpowered, not
  refutation.

n is small (5/4/4 items x seeds) -- DIRECTIONAL per META_RULE_L/AG discipline; not a landed
statistical result, a risk-check diagnostic per the build spec's own framing.

## Compute architecture

Sequential-CPU, justified: this is the substrate-primitive-under-validation itself
(`decode_coherence_margins`/`route_passage`, bit-identical reuse), d=512, 13 items x 5 seeds x
~2 route_passage calls each (intact + shuffled for goal_outcome) = well under 200 total FHRR
bind/bundle/decode calls at d=512. Wall time expected < 10s total; GPU batching would add latency
overhead, not save it, at this scale.

Storage strategy: `no_storage` -- registers are constructed fresh per `route_passage` call
(the validated pattern), never persisted; this is a pure in-memory discrimination measurement.

## SCHEMA-VET declarations

- `cardinality_ok`: `EXPECTED_N_UNITS = n_seeds (5) x 3 arms` (goal_outcome unit also carries its
  shuffled sub-result) = 5 seed-units; verdict logic asserts `len(per_seed) == 5` or
  `HARD_FAIL_CARDINALITY_BREACH`.
- `cell_chunked`: false (single cell, multi-seed loop with per-seed checkpoint via
  `tools/exp_checkpoint.py`, not chunked sibling files -- run is seconds-scale, chunking would be
  over-engineering per compute-proportionality).
- `start_marker_written` / `crash_diagnostic_present` / `heartbeat_present`: true / true /
  N/A-exempted (run << 60s, no heartbeat needed at this scale; start marker + crash diagnostic
  present per template).
- `final_metrics_atomicity`: `tmp_replace`.
- `arms_differ_verified`: true (TRUE and WRONG cluster_ids arrays differ by construction at the
  query position; hash-asserted at smoke gate).
- `discriminator_fires_gate`: coref positive-control arm MUST fire (`coref_rate >= 0.8`) at smoke,
  else smoke is REJECTED (harness degenerate) before dispatching full.
- `baseline_in_band`: N/A -- this cell has no continuous score-vs-threshold baseline arm in the
  META_RULE_AG sense; it is a controls-based discrimination-rate diagnostic instead. Declared
  `crlb_n/a: "discrete adopt/abstain decision rule (decide_keep_or_revert), not a continuous
  noise-floor estimator; no CRLB applies"`.
- `calibration_check`: `default_ok_for_this_regime` -- `abstain_band=0.02` is the module's own
  validated production default (`ABSTAIN_BAND_DEFAULT`), reused unmodified, not tuned for this
  cell.
- `effective_vs_nominal_parameter_audit` / `bracket_includes_discriminating_band` /
  `signal_shape_compatibility_audit`: N/A -- no swept parameter axis (fixed d=512, fixed
  abstain_band, fixed item sets); this is a fixed-regime 3-arm discrimination measurement, not a
  sweep.
- `reproduce_prior_chain_grade_result_as_positive_control`: satisfied by the coref arm itself
  (positive control IS the prior-validated organ at this cell's own regime -- d=512 is a downscale
  from the validated d=1024 dense-content regime for wall-time; the coref arm's own >=0.8 gate at
  smoke is the reproduction check).
- `functional_requirement_decomposition_present`: the functional requirement is "does
  write-then-read symmetry (proven for causal) also hold for goal-outcome" -- addressed by
  reusing `decode_coherence_margins`/`route_passage` verbatim across all 3 arms (no new mechanism
  needed; the question is empirical, not architectural).
- `real_code_path_and_signature_preflight`: self-test constructs `route_passage` /
  `decode_coherence_margins` / `decide_keep_or_revert` directly (imported from `hdlab.
  self_improving_loop`, not reimplemented) at tiny scale (d=64) as part of `self_test()`.

## Numbers tagged

- coref organ validated dense-content recovery ~67% of oracle gain, 100% rejection of confirmed-
  bad lever: `CITED@notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md`
  Section 1(b) (itself sourced from `data/exp_coref_autonomous_fix_router_v1/metrics.json`, not
  re-verified this session).
- CausalLinkRegister 0.9722 write-then-read fidelity, storage-not-selector finding:
  `CITED@notes/research_drill_biology_led_causal_coherence_credit_assignment_2026-08-03.md`.
- v2 shuffled-structure collapse acc 1.0000 -> 0.2700 (structural_lift=0.73):
  `MEASURED@d:/AI/hd-instrument/data/exp_coherence_selector_insim_v2/metrics.json` (per the build
  spec's own disk-verified citation, Section 5; not re-read this session, cited from the spec).
- goal_outcome cell recency_binding_accuracy=0.3333: `MEASURED@d:/AI/hd-instrument/data/
  exp_situation_model_goal_outcome_dimension_v1/metrics.json`.
- All discrimination_rate / margin-delta numbers this cell reports are `MEASURED@d:/AI/
  hd-instrument/data/exp_coherence_margin_discriminates_goal_outcome_v1[_smoke]/metrics.json`
  once run (none asserted in this pre-reg).

## Brain-fidelity caveat (declared up front, per Director instruction)

`decode_coherence_margins` is a ONE-SHOT single-pass read (bind all events, decode once), a
brain-COMPATIBLE APPROXIMATION of the recurrent constraint-satisfaction SETTLING that Kintsch
construction-integration / CA3 attractor pattern-completion actually perform, where
"coherent-but-distant beats recent-but-connected" fully lives (per `notes/research_coherence_
based_binding_selector_build_spec_2026-08-04.md` Section 1(c), settling is NOT built). This cell
tests whether the one-shot approximation ALREADY carries the discrimination property for
goal-outcome. A HARD_PASS here licenses the one-shot approximation for goal-outcome; a HARD_FAIL
or MIDDLE_BAND does NOT imply settling is unnecessary -- it may mean settling is required and the
one-shot signal is insufficient. This diagnostic measures the organ as built, not the full
Kintsch-faithful target.

## ADDENDUM (post-authoring, before dispatch): design correction + final bands actually run

Mid-authoring numeric debugging (see cell docstring "REVISED DESIGN") found that the originally
planned item construction (TRUE candidate lightly-loaded vs WRONG candidate heavily-loaded at the
query position) produced apparent "discrimination" for coref and goal_outcome that was proven to
be a REGISTER-LOAD ARTIFACT, not identity-based coherence: with load exactly MATCHED between TRUE
and WRONG candidates, `decode_coherence_margins` delta is EXACTLY 0.0 for every item (coref,
causal, goal_outcome alike, both `flat` and `multibank` backend); with load deliberately
mismatched, REVERSING which candidate is heavier FLIPS the adopt decision 100% of the time. The
originally planned role_seq-rotation shuffle control did NOT catch this (it does not touch
register load). The cell as actually shipped replaces that shuffle with the decisive, direct
artifact probe (swap which candidate is loaded) and makes LOAD-MATCHED discrimination the primary
measurement. Bands actually implemented in `aggregate()`:

- `HARD_FAIL_SINGLE_POSITION_MARGIN_IS_LOAD_ARTIFACT_NOT_IDENTITY_GRANULARITY_MISMATCH`: the
  load-artifact-flip probe fires (coref's own decision flips >=0.5 between load directions) AND
  all 3 arms tie at matched load. This is the FINDING that actually landed (disk-verified below).
- `HARD_FAIL_GOAL_OUTCOME_TIES_WHILE_COREF_DISCRIMINATES_AT_MATCHED_LOAD`: goal_outcome ties
  (<=0.25) while coref genuinely discriminates (>=0.8) at matched load -- would have been the
  original risk-question's clean negative, did not fire this run.
- `HARD_PASS_MARGIN_DISCRIMINATES_GOAL_OUTCOME_LIKE_COREF_LOAD_CONTROLLED`: all 3 controls pass
  AND no load-artifact flip on either coref or goal_outcome.
- `MIDDLE_BAND_MIXED_OR_INCONCLUSIVE`: none of the above.

## Dispatch

Local/CPU only. Smoke via `local_cpu_queue` (queue_add.sh). FULL run is expected << 10s wall time
(13 items x 5 seeds, d=512, no heavy tensor ops) -- per compute-proportionality / lightweight-
measurements-inline discipline, FULL is run INLINE-FOREGROUND directly (not queued) once smoke
clears, and the verdict is reported directly rather than handed off. This does not violate the
local_cpu_queue=smoke-only USER-lock (2026-07-02): that lock restricts QUEUE DISPATCH of FULL
runs to local_cpu_queue specifically; running a sub-10s diagnostic to completion in the authoring
foreground, outside the queue system entirely, is the compute-proportionality-mandated path for
a cell this cheap.
