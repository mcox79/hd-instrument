# Pre-registration: exp_direction_b_M3inc1_coverage_expansion_v1

**Filed by:** exp_dev, 2026-08-09. **Task source:** Director spawn prompt (the M3-cost crux test:
does expanding M2's learned result-type coverage + combining it with M1's idiom channel push GATE-2
recovery toward the DesireDB majority (linear returns = M3 tractable), and does the combined channel
earn a WIRE?), citing `notes/direction_b_grounded_knowledge_build_plan_2026-08-09.md` M2/M3 +
`data/exp_direction_b_M1_idiom_grounding_recovery_v1/metrics.json` (MIDDLE_BAND, PRIMARY 2/8=0.25,
BREADTH 0/37=0.0) + `data/exp_direction_b_M2_speechact_result_generalization_v1/metrics.json`
(MIDDLE_BAND, GATE-1 HARD_PASS held_out_acc=0.8846, GATE-2 PRIMARY 3/8=0.375, BREADTH 9/37=0.2432).

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh "combine idiom lexicon result type classifier precedence fallback
coverage expansion construction cue atom pool WordNet verb class"` -> top hit cosine=0.2861 (a TIER2
atomization-methodology doc, unrelated). All top-5 hits below cosine=0.30. **Verdict: no prior-work
match; genuinely novel increment of the M1/M2 arc within this session, not a rediscovery.**

## What / why
Two orthogonal levers, tested together because they answer the SAME strategic question (is Direction
B's M3 -- the multi-month full concept/script/idiom-inventory scaling leg -- worth committing to):
1. **Coverage expansion**: M2's own cell disclosed 4 known construction-cue-pool gaps
   ("objected"/"awarded"/"provided"/"quit" do not fire their intended verb-class atom via WordNet
   primary-sense overlap). Closing them (+broader dictionary-grounded vocabulary) tests whether
   pool-growth shows roughly LINEAR returns on DesireDB recovery (M3 tractable) or DIMINISHING/
   plateauing returns (M3 not justified by this lever).
2. **Channel combination**: M1's idiom lexicon (non-compositional tail, 0/37 breadth) and M2's
   result-type classifier (compositional core, 9/37 breadth) target DIFFERENT residual slices.
   Combining them (result-type first, idiom-lexicon fallback only when result-type genuinely found
   nothing) tests whether the union clears the GATE-2 PRIMARY HARD_PASS bar (>=0.40) M2 alone missed
   (0.375) -- the bar for a WIRE-candidate recommendation (director makes the actual land decision).

## Coverage-expansion design (hdlab/result_type_induction.py POOL_STAGES)
Three staged pool versions, each an ordered superset, added to `hdlab/result_type_induction.py`
(module docstring's 2026-08-09 addendum has the full WordNet-gloss citation per word):
- `v0_baseline` -- exactly M2's original 3-4-word pools (COMM/GIVE/ACHIEVE/FAIL).
- `v1_targeted_gap_close` -- + the literal base form of each of the 4 disclosed gaps: "object"
  (object.v.01 "express or raise an objection or protest..."), "award" (award.v.01 "give, especially
  as an honor or reward"), "provide" (supply.v.01 "give something useful or necessary to" -- also
  transitively covers "supply"/"render"/"furnish" via that synset's own lemmas), "quit"
  (discontinue.v.01 "put an end to a state or an activity" -- also transitively covers "stop"/
  "cease"/"discontinue"/"give up"/"lay off"). Each addition authored from the CANDIDATE WORD'S OWN
  WordNet primary-sense gloss, never by checking which DesireDB item it would flip (calibration-
  honesty, same discipline `idiom_grounding._RAW_IDIOMS` already follows).
- `v2_broader_class_expansion` -- + 3 further GENUINE dictionary-grounded class members NOT tied to
  any specific known gap (general vocabulary breadth): "deny" (deny.v.01), "reject" (reject.v.01) for
  REFUSAL/comm_verb; "abandon" (abandon.v.01) for FAIL/fail_verb.
`ACTIVE_POOL_STAGE = v2_broader_class_expansion` is the new module default (every existing caller
that does not pass `pool_stage=` explicitly -- M2's own cell/self-test, `goal_achievement.py`'s
default call sites -- transparently picks up the expansion going forward).

**MEASURED (this session's self-test, GATE-1 no-DesireDB check):** `held_out_acc` v0=0.8846 (23/26,
cited from M2's own landed number) -> v2=0.9615 (25/26) at this cell's `--self-test`;
`scramble_control_acc` 0.0769 -> 0.0 (collapse strengthened, not weakened). Full v0/v1/v2 GATE-1
table + PRIMARY/BREADTH numbers per stage are in `data/exp_direction_b_M3inc1_coverage_expansion_v1/
metrics.json:returns_per_expansion` after `--full` lands (see Results section below, filled post-run).

## Channel-combination design (hdlab/goal_achievement.py)
New `_attribute_outcome_state_combined_grounded` / `utility_channel_trace_combined_grounded` /
`utility_channel_combined_grounded`: same per-token WordNet vote as Stage-2/M1/M2, PLUS exactly ONE
supplementary vote chosen by PRECEDENCE (never both, keeps the trace auditable via
`grounding_trace.secondary_source` in {'resulttype','idiom_fallback','none'}):
1. Try `hdlab.result_type_induction.result_type_votes` (M2, the compositional core) first.
2. Fall back to `hdlab.idiom_grounding.idiom_votes` (M1, the non-compositional tail) ONLY when
   result-type genuinely returned an honest all-zero abstain (no construction cue fired at all).
Both self-tested (`self_test_combined_grounded_channel`) on two real-DesireDB-flavored flagship
cases: "Uh. No." (must engage the `resulttype` precedence path, matching M2's own flagship case) and
"I put the kabash on that idea..." (result-type atoms find NOTHING -- `span_feats` ==
`['no_verb_class_cue']`, verified as a fixture assertion -- so the fallback engages `idiom_fallback`
and recovers the correct verdict, matching M1's own flagship phrase).

## Three units (`--unit`, one per invocation; `tools/exp_checkpoint.py` per-unit resumable shard)
- **v1_resulttype** -- pool_stage=v1, channel=resulttype-only. PRIMARY cohort only (no breadth pass
  -- compute-proportionality; see Compute architecture).
- **v2_resulttype** -- pool_stage=v2, channel=resulttype-only. PRIMARY + full BREADTH (900-row,
  ENLARGED_SEED=20260809, identical to M1/M2). Isolates POOL-EXPANSION's own contribution, holding
  channel fixed at resulttype-only (the same channel M2 measured 9/37 with).
- **v2_combined** -- pool_stage=v2, channel=combined. PRIMARY + full BREADTH. THE GATE-DEFINING UNIT.

Cohort/loader reused verbatim from `exp_utility_satisfaction_channel_v1` (SEED=20260808,
FULL_N_PER_CLASS=80 -> n=160 draw -> PRIMARY cohort n=22, 8 gold-Unfulfilled -- identical to Stage-2/
M1/M2). Arms (PRIMARY, per unit): (i) majority baseline, (ii) `utility_channel` WordNet-only
reference (unchanged), (iii) the unit's mechanism arm, (iv) mechanism arm with SCRAMBLED goal cue
(mandatory pairscramble control, `_s2._scrambled_desires`, deterministic derangement, PROT-023
compliant -- no `hash()`-derived seeding anywhere in this cell).

## Pre-registered gates

### GATE-1 (regression guard, per unit's pool_stage; no DesireDB)
- **PASS floor:** `held_out_acc >= 0.60` AND `scramble_control_acc <= 0.35` (26-item HELDOUT set,
  same threshold M2 used -- majority-class share 6/26=0.231 unaffected by pool_stage).
- **HARD-FAIL (kill criterion for the overall verdict):** `held_out_acc < 0.40` on the
  GATE_DEFINING_UNIT (v2_combined)'s pool_stage (v2) -- "expansion broke generalization."

### GATE-2 PRIMARY (reused verbatim from M1/M2's own thresholds; applies to `v2_combined`)
- **HARD-PASS (WIRE-candidate bar):** `recovery_iii >= 0.40` AND pairscramble collapses
  (`|acc_iv-acc_i| <= 0.05`) AND does not leak (`|acc_iv-acc_iii| > 0.03`).
- **MIDDLE_BAND:** `0.15 <= recovery_iii < 0.40`, pairscramble collapses.
- **HARD-FAIL:** `recovery_iii < 0.15` OR pairscramble does not collapse OR leaks.

### GATE-2 BREADTH (context/M3-tractability signal; `v2_resulttype` + `v2_combined`, denom=37)
Reported vs M2's cited 9/37=0.2432 and M1's cited 0/37=0.0. Pairscramble-at-scale collapse
(`|acc_scrambled-acc_i| <= 0.05`) is MANDATORY on the `v2_combined` breadth pass -- non-collapse here
is an overall HARD-FAIL condition (below), same weight as the PRIMARY-cohort pairscramble control.

### Overall verdict (computed once all 3 units are recorded; `cardinality_ok`)
- **HARD-FAIL** if ANY of: GATE-1 `held_out_acc < 0.40` (expansion broke it) OR GATE-2 PRIMARY
  hard-fails (rate<0.15, leaks, or primary pairscramble does not collapse) OR BREADTH pairscramble
  does not collapse OR **"no returns"**: `primary_rate <= M2_PRIMARY_RATE(0.375) AND breadth_rate <=
  M2_BREADTH_RATE(0.2432)` (task's explicit "combined recovery does not beat M2" condition -- both
  numbers must fail to improve for this to fire; either one improving is a genuine return).
- **HARD-PASS (WIRE-candidate):** not hard-fail, AND GATE-2 PRIMARY hard-passes (`>=0.40`, collapses,
  no leak), AND GATE-1 clears its PASS floor + collapses.
- **MIDDLE_BAND:** everything else (some improvement, not enough for HARD-PASS).
- Director makes the actual land/WIRE decision post-VET, per the task's explicit instruction --
  this cell only reports `wire_candidate: bool` (== GATE-2 PRIMARY hard-pass), never wires.

## RETURNS-PER-EXPANSION report (`metrics.json:returns_per_expansion`, mandatory field)
- `gate1_held_out_acc`: {v0 cited, v1 measured, v2 measured} -- fast, no-DesireDB trend.
- `primary_recovery_rate`: {v0_M2 cited=0.375, v1_resulttype, v2_resulttype, v2_combined} measured.
- `breadth_recovery_rate`: {v0_M2 cited=0.2432, v0_M1 cited=0.0, v2_resulttype_pool_expansion_only,
  v2_combined_plus_idiom_fallback} measured.
- `breadth_delta_from_pool_expansion_v0_to_v2resulttype` / `..._from_combination_v2resulttype_to_
  v2combined` -- the two-step decomposition (how much did POOL EXPANSION alone add vs how much did
  ADDING the idiom-fallback COMBINATION add, on top of that).
- `m3_tractability_trend_assessment`: `roughly_linear` (second delta within 0.4x-2.5x of the first,
  both positive) / `diminishing` (second delta <0.4x the first) / `accelerating` (second delta >2.5x
  the first) / `flat_or_negative` (neither delta positive) / `mixed` (signs differ). An HONEST,
  DISCLOSED heuristic on a 2-delta series -- not a statistical claim, a directional read for the
  director's M3 go/no-go.

## Compute architecture
(b) sequential-CPU with justification: same construction-cue extraction + FHRR bind/bundle/unbind
(N=2048 complex64) as Stage-2/M1/M2, unchanged. **Compute-proportionality scope note (measured this
session):** this host's per-process WordNet-corpus import cost was MEASURED at 225s during this
session's design-probe diagnostic (a plain `import hdlab.result_type_induction` with no other work) --
contended-host reading, not necessarily representative of an idle host, but real for THIS dispatch.
Consequently: (1) each of the 3 units is its OWN foreground process invocation (`--unit`,
`tools/exp_checkpoint.py` per-unit resumable shard -- a killed/hung call loses at most the
in-progress unit, per the repo's mandatory multi-unit-checkpoint convention), keeping every
individual call inside the 10-min single-foreground-call budget; (2) `v1_resulttype` skips the
900-row BREADTH pass (PRIMARY-cohort-only) -- its role is the GATE-1 regression check + a fast
PRIMARY-cohort trend point, not a second full breadth measurement; the two BREADTH passes that DO
run (`v2_resulttype`, `v2_combined`) are the ones that isolate the two levers this cell exists to
measure (pool-expansion-alone vs +combination). Storage: no_storage/no_composition.

## Cell-template mandatory fields
- `cell_chunked`: **true** (ONE unit per invocation via `--unit`; departs from M1/M2's single-process
  convention specifically because of the measured per-process import cost above -- declared and
  justified, not a silent scope cut).
- `start_marker_written` / `crash_diagnostic_present` / `heartbeat_present`: true.
- `arms_differ_verified`: true (hash-check on arms i/ii/iii/iv PRIMARY-cohort prediction vectors,
  smoke + every full unit).
- `final_metrics_atomicity`: `tmp_replace`, rebuilt from `load_units()` on every write (each unit's
  own `record_unit` append is itself atomic per `tools/exp_checkpoint.py`; the top-level `metrics.json` is
  always a complete, self-consistent snapshot of whatever units are recorded so far -- no partial-
  mutation state, satisfies META_RULE_AH without needing per-iteration distinct paths).
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`) --
  grep-verified clean.
- `crlb_n/a`: "deterministic construction-cue-vote learner (ruleind/estimation/proginduction over a
  fixed 7-atom boolean feature space) + idiom-regex lexicon + FHRR bind/bundle/cleanup over a fixed
  6-role x 3-filler codebook, no decoded/noisy continuous signal from a swept capacity regime --
  identical justification to Stage-2/M1/M2's crlb_n/a, unchanged FHRR mechanism layer."
- `HP_SCOPE`: `{v2_combined.arm_iii: [gate2_primary_hard_pass, pairscramble_collapse_primary,
  pairscramble_collapse_breadth]}` -- v1_resulttype/v2_resulttype are context/decomposition units,
  not independently HARD_PASS/HARD_FAIL-gated; only `v2_combined`'s PRIMARY arm-iii gates the overall
  verdict + wire_candidate flag.
- `cardinality_ok`: `EXPECTED_N_UNITS = 3` (v1_resulttype, v2_resulttype, v2_combined).
- `deterministic_seeding`: true (GATE-1 scramble seed 20260809 via `random.Random`; DesireDB draw
  seed 20260808; ENLARGED seed 20260809; FHRR role/filler vectors seeded 20260809 -- all reused
  unchanged from Stage-2/M1/M2; no `hash()`-derived seeding anywhere in this cell, grep-verified).
- `calibration_check`: `adaptive_with_discriminator_gate` -- every pool-stage addition was authored
  from the candidate word's OWN WordNet primary-sense gloss BEFORE any GATE-2 DesireDB number was
  computed (see "Coverage-expansion design" above for the per-word citations); the combined-channel
  precedence rule (result-type first, idiom fallback only on genuine abstain) was fixed as a design
  choice before any scored run, not tuned post-hoc against a specific item's gold label.
- `functional_requirements`: "grow construction-cue verb-class coverage without re-tuning against
  eval labels" -> `hdlab.result_type_induction.POOL_STAGES` (WordNet-gloss-grounded, pool_stage
  threaded through `span_feats`/`build_episode`/`get_induced_hypothesis`/`result_type_votes`);
  "combine two complementary grounding sources with an auditable precedence, not a blind merge" ->
  `hdlab.goal_achievement._attribute_outcome_state_combined_grounded` (trace field
  `secondary_source`).
- `real_code_path_exercised`: `[span_feats, POOL_STAGES, registry.learn, result_type_votes,
  idiom_votes, _attribute_outcome_state_combined_grounded, bind, unbind, bundle,
  utility_channel_trace_combined_grounded]` -- `--self-test` constructs the REAL construction-cue
  extraction + a REAL `registry.learn` fit (at all 3 pool stages) + the REAL FHRR primitives on real-
  DesireDB-flavored flagship cases, not a synthetic-only branch.
- `progress_logging`: `print_flush_true` (this cell's wall-time can exceed 1800s on this contended
  host; `[unit=...]`/`[full]`/`[smoke]` progress lines print with `flush=True` throughout).

## Autonomy notes (exp_dev-owned, per the task's contract)
Which verbs to add to the atom pools (from WordNet, not DesireDB labels -- documented per-word
above), the M1+M2 precedence/combination logic (result-type first, idiom fallback -- the task's own
suggested design, adopted as-is), cell/module naming, seeds (all reused verbatim from Stage-2/M1/M2
for direct comparability), the `--unit` chunking split (a compute-proportionality response to this
session's measured import-cost finding). The anti-circular + calibration-honesty discipline (author
atoms from WordNet not eval labels, score once), the gates (GATE-1 regression floor, GATE-2 PRIMARY
HARD_PASS>=0.40 bar, the mandatory pairscramble control on BOTH cohorts), and the "no returns" /
"does not beat M2" HARD-FAIL condition are NOT exp_dev's to drop and were not altered.

## Results (filled after `--full` lands for all 3 units)
See `data/exp_direction_b_M3inc1_coverage_expansion_v1/metrics.json` (top-level `verdict` /
`verdict_msg` / `returns_per_expansion` / `units`) -- summarized in the exp_dev completion report.
