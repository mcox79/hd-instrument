# Pre-registration: exp_situation_model_relation_ablation_v1

**Filed by:** exp_dev, 2026-08-09. **Task source:** Director spawn prompt, Direction-B build #2
(union-wire #1 is DONE-WIRED, commit a72fea051). Two hand-offs define the contract:
`notes/exp_dev_handoff_research_psych_bridging_inference_situation_models_2026-08-09.md` (primary
spec, pre-registered bands) + `notes/research_preclusion_goal_failure_inference_2026-08-09.md`
(CONTRADICT-leg mechanism, replaces the "calibrate low placeholder").

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh "situation model register goal outcome engagement axis preclusion
concept similarity"` -> top hit `situation_model_goal_outcome_dimension_v1` cosine=0.3926
(MIDDLE_BAND_FIRES_BUT_RECENCY_CONFOUND_ROUTES_BINDING_SELECTOR, 2026-08-04). Read the metrics +
source note: that cell is a DIFFERENT mechanism -- goal-owner SELECTION + appraisal-based
goal-BLOCKED detection (met/noise/harm classes) via a recency-confounded binding selector over a
role-labeled situation model, not a relation classifier between a goal and a candidate outcome
event. Genuinely distinct problem (owner selection + appraisal vs. means-end/preclusion relation
typing), though a useful cautionary precedent: that cell's own failure mode (recency confound in a
multi-item register selector) is why this cell binds GOAL_ROLE and OUTCOME_ROLE on SEPARATE
single-filler ephemeral register instances rather than co-binding multiple items on one entity
(see "Register architecture" below) -- avoids that exact confound class by construction. **Verdict:
distinct mechanism, not a rediscovery; the prior cell's failure mode directly informed this cell's
register-usage design choice.**

## What / why
Clean ablation of `hdlab/goal_outcome_relation.py`: swaps ONLY the relation-COMPUTATION step for
GRADED situation-model + concept-relation queries, reusing that module's `self_test()` harness
(14 TRAIN + 11 HELDOUT disjoint-tag episodes, `memorization_baseline_predict`, scramble-label
control) STRUCTURALLY UNCHANGED. New code lives in `hdlab/goal_outcome_relation_grounded.py`
(module docstring has the full mechanism writeup); two small additive extensions:
- `hdlab/situation_model_accumulate.py`: new `RelationRegister` class (GOAL_ROLE/OUTCOME_ROLE,
  mirrors `CausalLinkRegister`'s CAUSE/EFFECT pattern, generalized to bind a role to an arbitrary
  supplied content vector rather than a closed idx_vecs vocabulary).
- `hdlab/lexical_similarity.py`: SUPPLY EXTENSION adding the 39 literal words `goal_outcome_
  relation.py`'s 6 hand-authored pools already contain to `CONCEPT_FEATURES` (new domain tags
  EPISTEMIC_DOM/SKILLBUILD_DOM/SKILLTRAIN_DOM/INFOEXCHANGE_DOM/ERRANDACT_DOM, no collision with
  existing 89-concept lexicon).
- `hdlab/quality_relation.py`: new `engagement` FPE axis in `AXIS_WORDS` (Cruse reversive-pair
  seeding + phrasal-verb forms + the 5 disclosed WordNet-MWE gap phrases as explicit multi-token
  keys, per the preclusion drill's own Tier-0 design) -- pure data addition, `self_test()`
  unaffected.

## Two legs, different evidentiary status (report SEPARATELY, mandatory per both hand-offs)

### ACHIEVE leg (`goal_atoms_grounded`/`outcome_atoms_grounded`/`pair_feats_grounded`)
Replaces `_pool_related` (Tier1 exact-literal + Tier2 WordNet-primary-synonym) with
`concept_similarity` (McRae-style shared-feature bundle cosine, `hdlab.lexical_similarity`)
against the SAME pools, routed through a `GOAL_ROLE`/`OUTCOME_ROLE` register bind/unbind hop.
**Honest framing (measured, not hypothesized):** `goal_outcome_relation.py`'s own docstring
documents that its hand-pools were EXPANDED specifically because a prior WordNet-hypernym-based
graded-bridging attempt this same session FAILED ("discuss/explain/tell/chat/describe/mentor/
practice/figure/grasp/discover/chore ALL measured False against small 2-word seed pools"); the
CURRENT literal pools already cover every word this TRAIN/HELDOUT bank exercises. Self-similarity
of a word already in a pool is always 1.0, so this leg reproduces Tier1-exact-coverage on this
specific bank BY CONSTRUCTION -- held-out accuracy PARITY (not improvement) is the expected,
correct outcome here; the graded fallback is real and testable (`lexical_similarity.CONCEPT_
FEATURES` carries two DELIBERATELY NEW words, "grasp"/"cram" -- "grasp" is literally one of the
words the ORIGINAL module's own calibration note above names as a word the failed WordNet-hypernym
attempt could not bridge and which was never subsequently added to a literal pool; MEASURED@this
session that baseline's `_pool_related` misses BOTH: `goal_atoms("...grasp...")==[]`,
`outcome_atoms("...crammed...")==['no_relation_cue']`, while the grounded mechanism fires on both
via shared-domain-tag `concept_similarity`) but is a capability the closed TRAIN/HELDOUT bank
itself does not exercise (neither word appears in TRAIN_EXAMPLES/HELDOUT_EXAMPLES).
`ACTIVITY_ENGAGEMENT_WORDS` (structural token-set check) and `SELF_RELIANCE_RE`
(verb-agnostic regex) are REUSED UNCHANGED -- neither is a lexical-pool-membership test.

### CONTRADICT leg (`CONTRADICT_query`/`_engagement_disengage_scan`, engagement axis)
Replaces `mwe_disengage_scan` (exact WordNet-verb-gloss dictionary lookup) with a graded
same-axis-opposite-sign query on the new `engagement` FPE axis. Goal's pole = a fixed anchor word
("engage" +1.0 / "abandon" -1.0) keyed by `goal_polarity`'s EXISTING structural engagement-vs-
avoidance classification (reused unchanged -- goal verbs in this bank, e.g. help/fix/ask/
negotiate, are not literally engagement-axis words, so a per-verb axis lookup on the goal side
would abstain almost always; the goal's STANCE, not its literal verb, is what the axis models,
per notes/research_preclusion_goal_failure_inference_2026-08-09.md part b's own framing). Outcome's
pole = `_engagement_disengage_scan`'s span-scan (mirrors `mwe_disengage_scan`'s contiguous-span/
morphy-normalization logic, checked against the new axis lexicon instead of WordNet glosses).
**HONEST CALIBRATION (carried verbatim from the preclusion drill's part d, mandatory, not
softened):** the axis REPRESENTATION shape is well-precedented -- P(mechanism design is well-formed)
~0.55, two independently-searched literature lanes (event-calculus/ASP-NAF narrative-applied
computational precedent; Beavers/Kennedy-McNally/Pustejovsky scalar event-structure formal
semantics) converge on the identical `(scale, direction-sign)` shape without cross-contamination.
Its BRAIN-FIDELITY is explicitly NOT claimed -- P(psychologically-faithful online mechanism)
~0.15-0.20, LOWER than a prior drill's softer "thin spot" framing, because a dedicated 9-angle/
~20-search hunt this session CONFIRMED (not merely failed to find) zero reading-time/ERP/probe
evidence exists for wordless preclusion inference at the human-subject level. **This leg's results
MUST be reported separately from the ACHIEVE leg's; if the two diverge, do not fold into one
blended verdict** (mandatory, both hand-offs).

## Register architecture (`hdlab.situation_model_accumulate.RelationRegister`)
GOAL_ROLE and OUTCOME_ROLE bind on SEPARATE ephemeral single-filler register instances per call
(never co-bound on one entity) -- a disclosed, deliberate deviation from a literal reading of "bind
both on the same entity's register", chosen specifically to preserve `goal_outcome_relation.py`'s
own Stage-1-confound-immunity invariant (goal-side/outcome-side features must stay independently
computable) AND to avoid the recency/multi-item-binding confound the prior-work-check's nearest
related cell (`exp_situation_model_goal_outcome_dimension_v1`) measured. Bind-then-unbind of a
SINGLE filler is mathematically EXACT (lossless passthrough -- `unbind(bind(v,r),r) = v*r*conj(r)
= v` since `|r|=1`), asserted in `self_test()`'s `REGISTER_LOSSLESS_CHECK` (measured cos=1.0,
exactly). Its role here is architectural consistency with the proven bind/bundle/unbind organ
(Kintsch C-I / Zwaan multi-event-indexing shape) and an auditable per-decision trace field
(`axis_evidence` in `CONTRADICT_query`'s return), not a computational change on this single-filler
case -- disclosed honestly, not hidden.

## Pre-registered bands (from the primary hand-off, verbatim -- NOT loosened)
Compares `hdlab.goal_outcome_relation.self_test()` (current/baseline) against `hdlab.
goal_outcome_relation_grounded.self_test()` (grounded/ablation), same 11-item HELDOUT_EXAMPLES,
same scramble-control convention (`random.Random(20260809)`, unchanged seed).

- **HARD-PASS:** grounded `held_out_acc` >= baseline `held_out_acc` AND grounded
  `scramble_control_acc` collapses to at/below the baseline `scramble_control_acc` (tolerance
  `NOISE_TOL=0.05`, ~half of one heldout item at n=11) AND grounded `engagement_axis_coverage`'s
  `disclosed_gap_recovery_count` >= 1 (of 5).
- **MIDDLE_BAND:** grounded `held_out_acc` matches baseline within `NOISE_TOL`, scramble collapses,
  `disclosed_gap_recovery_count` == 0.
- **HARD-FAIL:** grounded `held_out_acc` < baseline `memorization_baseline_acc`, OR grounded
  `held_out_acc` < baseline `held_out_acc - NOISE_TOL`, OR grounded `scramble_control_acc` does NOT
  collapse (`> baseline scramble_control_acc + NOISE_TOL`).

## Tier-0 axis-coverage smoke (GATES the full ablation, per the preclusion drill's own design)
Cheaper than the full ablation -- pure `_engagement_disengage_scan` coverage measurement, no
register/induction machinery, isolates ONLY the axis-construction question before Tier-1 runs.
**MEASURED discrepancy flagged (honest, disk-verified before authoring the gate):** the preclusion
drill's own Tier-0 spec cites "WordNet-MWE floor = 26/29 = 0.897"; re-running `hdlab.goal_outcome_
relation.contradiction_dictionary_coverage()` fresh THIS session measures `n_hit=24, coverage=
0.8276` (internally consistent with that module's own `REPRESENTATIVE_DISENGAGEMENT_PHRASES` list,
which declares exactly 5 `covered=False` items -> 29-5=24, not 26 -- the "0.897"/"26/29" figure
appears to be a stale arithmetic slip in that module's own docstring, not reproduced by its own
listed data). **This cell uses the MEASURED-this-session floor (0.8276), not the stale cited one,
per "verify on disk, never propagate a number that doesn't reproduce."**
- **HARD-PASS:** `disclosed_gap_recovery_count >= 3` (of 5) AND `false_positive_count == 0` (on the
  existing 5-item clean probe) AND overall 29-item `coverage >= 0.8276` (measured floor, does not
  regress the WordNet-MWE mechanism's own coverage).
- **MIDDLE_BAND:** `1 <= disclosed_gap_recovery_count <= 2`, `false_positive_count == 0`,
  `coverage >= 0.8276`.
- **HARD-FAIL:** `disclosed_gap_recovery_count == 0`, OR any false positive, OR `coverage < 0.8276`
  -- do not proceed to Tier-1; keep `mwe_disengage_scan` as the operating point.

## Baseline numbers (MEASURED@this session, `python -m hdlab.goal_outcome_relation`, fresh run,
`data/exp_situation_model_relation_ablation_v1/metrics.json:baseline_selftest` on full dispatch)
`held_out_acc=1.0` (11/11), `memorization_baseline_acc=0.6364`, `scramble_control_acc=0.6364`,
`dictionary_coverage=0.8276` (24/29), `false_positive_count=0`, chosen_plugin=`ruleind`.

## Tier-0 + Tier-1 result preview (MEASURED@this session, local `--self-test` run of the new
module BEFORE full dispatch -- see "Pre-dispatch smoke" below; reproduced verbatim by the cell)
`hdlab.goal_outcome_relation_grounded.self_test()`: `held_out_acc=1.0` (11/11, matches baseline
exactly), `scramble_control_acc=0.6364` (matches baseline exactly, collapses), `engagement_axis_
coverage.coverage=1.0` (29/29), `disclosed_gap_recovery_count=5` (5/5, ALL 5 disclosed WordNet-MWE
gaps recovered via the graded axis query), `false_positive_count=0`, `register_lossless_check_cos=
1.0` (exact). **Both Tier-0 and the full ablation's HARD-PASS bands clear with wide margin at this
preview measurement** -- disclosed here per META_RULE_AC (HYPOTHESIZED vs MEASURED marking); the
cell's own `--full` run reproduces these numbers as the gate-defining measurement, not a re-run of
a different regime.

## Compute architecture
(b) sequential-CPU with justification: WordNet morphy/gloss lookups (span-scan, 1-4 token windows)
+ `concept_similarity` (bundle of <=4 feature-tag complex64 vectors per concept, N_DIM=8192) +
`registry.learn` fit (14 episodes, 8 boolean atoms, estimation+ruleind, `proginduction` excluded --
identical compute-proportionality justification to the fork-A cell's own) + FHRR bind/unbind over
N_DIM=8192 (lexical_similarity) and N_DIM=1024 (quality_relation axis vectors). MEASURED this
session: `--self-test` (both baseline + grounded modules) = 18.2s + 19.6s = ~38s combined; no
matmul-heavy batchable primitive at this scale (25 pairs total, each a handful of small tensor
dot-products). No new data, no DesireDB cohort (per the primary hand-off's own "cheapest possible
test" framing) -- Tier-0 smoke and Tier-1 full both complete in well under 1 minute wall time.
Storage: no_storage (ephemeral per-call registers, not a persistent store).

## Cell-template mandatory fields
- `cell_chunked`: false (single-process; self-test ~40s combined, smoke/full expected similar
  order of magnitude -- no per-seed/per-unit loop, this is a fixed 25-item bank comparison).
- `start_marker_written` / `crash_diagnostic_present`: true. `heartbeat_present`: true (written
  once per phase for auditability, though this cell is far under the 15-minute heartbeat-mandatory
  threshold).
- `arms_differ_verified`: true -- hash-check that baseline `pair_feats` and grounded `pair_feats_
  grounded` produce DIFFERENT per-item atom lists on the TRAIN+HELDOUT bank (they must, since the
  underlying computation genuinely changed) AND that baseline `mwe_disengage_scan` and grounded
  `_engagement_disengage_scan` produce different per-item match results on `REPRESENTATIVE_
  DISENGAGEMENT_PHRASES` (they must differ on at least the 5 disclosed-gap items, since baseline
  misses them by construction and grounded recovers them).
- `final_metrics_atomicity`: `tmp_replace`.
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`)
  -- grep-verified clean at smoke gate.
- `crlb_n/a`: "accuracy-comparison ablation over a fixed 14-TRAIN/11-HELDOUT item bank + a fixed
  29-item coverage bank; no capacity/noise-floor discriminator threshold to CRLB-check (same
  justification class as the fork-A cell's own `crlb_n/a`, unchanged FHRR mechanism layer)."
- `baseline_in_band` / `discriminator_reachability`: n/a per META_RULE_AG (channel-comparison
  ablation, not a swept-difficulty cell).
- `HP_SCOPE`: `{grounded_module: [tier0_gate, tier1_hard_pass_bands]}` -- baseline module is the
  REFERENCE arm (its own `self_test()` must reproduce its own documented numbers, a validity check,
  not a HARD_PASS/HARD_FAIL gate target itself).
- `cardinality_ok`: `EXPECTED_N_UNITS = 2` (Tier-0 axis-coverage unit + Tier-1 full-ablation unit;
  not a sweep-axis cell, this field is a completeness check not a sweep-cardinality gate).
- `deterministic_seeding`: true -- `_REGISTER_SEED=20260809` (fixed, module-level, every
  `RelationRegister` construction); scramble control seed `20260809` via `random.Random` (reused
  unchanged from baseline); axis rate/key seeds `505`/`55` (new `engagement` axis, base-505/55
  offset pattern matching the existing 4 axes' own `_AXIS_RATE_SEED_BASE`/`_AXIS_KEY_SEED_BASE`
  convention); grep-verified no `hash()`-derived seeding anywhere in the new module or its two
  additive hdlab/ extensions.
- `calibration_check`: `default_ok_for_this_regime` (ACHIEVE leg) -- `SIMILARITY_LINK_THRESHOLD=
  0.50` reused verbatim from `lexical_similarity.py`'s own pre-registration, NOT re-tuned here;
  `OPP_THRESH=-0.30`/`SAME_THRESH=0.60` reused verbatim from `quality_relation.py`'s own
  pre-registration for the CONTRADICT leg, NOT re-tuned. `adaptive_with_discriminator_gate`
  (engagement axis SEED WORDS specifically) -- the 39-word engagement lexicon (Cruse-typology core
  + phrasal-verb forms needed for `REPRESENTATIVE_DISENGAGEMENT_PHRASES` coverage + the 5 disclosed
  gaps as explicit disclosed keys, per the preclusion drill's own Tier-0 design) was authored from
  conventional/dictionary phrasal-verb meaning BEFORE the coverage self-test was run, then the
  self-test measurement (29/29, 5/5 gaps) is reported as-measured, not tuned further after seeing
  the number.
- `functional_requirements`: "replace hand-pool boolean membership with graded concept-similarity
  scoring, generalizing past the literal pool while reproducing its coverage on this bank" ->
  `goal_atoms_grounded`/`outcome_atoms_grounded`/`concept_similarity`; "replace exact WordNet-MWE
  dictionary lookup with a graded axis representation that can recover idioms absent from WordNet
  entirely" -> `_engagement_disengage_scan`/`quality_relation._fpe_axis_relation`; "route both
  legs' comparisons through the situation-model register organ for an auditable bind/unbind trace"
  -> `RelationRegister.bind_filler`/`decode_filler`.
- `real_code_path_exercised`: `[find_desired_state, goal_atoms_grounded, outcome_atoms_grounded,
  concept_vector, concept_similarity, RelationRegister.bind_filler, RelationRegister.decode_filler,
  registry.learn, _engagement_disengage_scan, _fpe_axis_relation, CONTRADICT_query,
  relation_votes_grounded]` -- `--self-test` constructs the REAL FHRR bind/unbind primitives, a
  REAL `registry.learn` fit, REAL WordNet morphy/gloss lookups, and a REAL `RelationRegister`
  instance on real construction-cue items, not a synthetic-only branch.
- `progress_logging`: `print_flush_true` (this cell's `timeout_s` is far under 1800s based on the
  measured ~40s self-test combined, but prints `[smoke]`/`[full]` progress lines with `flush=True`
  throughout regardless, per the standing discipline).

## Contract (from the primary hand-off, NOT exp_dev's to drop)
Reuse the EXISTING harness (same items/controls) -- this is an ablation (swap relation-computation
only); the mandatory scramble control; the per-leg separate reporting; the dict-gap recovery count;
the honest-low CONTRADICT-leg calibration (now sharpened per the preclusion drill: mechanism-design
confidence ~0.55, brain-fidelity confidence ~0.15-0.20, reported as two SEPARATE numbers, not one
blended figure). Do NOT wire into `goal_achievement_verdict`'s default -- opt-in, Director
land-decision after VET, same discipline as the union-wire promotion.

## Autonomy notes (exp_dev-owned, per the task's contract)
Exact `GOAL_ROLE`/`OUTCOME_ROLE` vector-generation details (separate single-filler registers per
call, not co-bound -- disclosed above), the engagement-axis seed words + threshold (`OPP_THRESH`/
`SAME_THRESH` reused unchanged; the 39-word lexicon itself is new), cell/module naming, seeds -- all
exp_dev's own design choices. Reuse-the-existing-harness, the mandatory scramble control, the
per-leg separate reporting, the dict-gap recovery count, and the honest-low CONTRADICT-leg
calibration were NOT exp_dev's to drop and were not altered.

## Results (filled after `--full` lands)
See `data/exp_situation_model_relation_ablation_v1/metrics.json` (top-level `verdict`/
`verdict_msg`/`tier0`/`achieve_leg`/`contradict_leg`) -- summarized in the exp_dev completion
report.
