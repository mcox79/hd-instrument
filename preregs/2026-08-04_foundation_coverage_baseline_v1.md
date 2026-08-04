# Prereg: foundation_coverage_baseline_v1

Date: 2026-08-04. Local-only cell (no queue / no remote / no push). Branch: dataprep/mcguffey-graded-corpus.

## Purpose (BASELINE MEASUREMENT, not pass/fail)
Track-1 step-1 of the foundation-building phase. Measure the CURRENT grounded foundation's
PER-CATEGORY coverage on the categorized causal-attribution ruler. The deliverable is a
category -> {accuracy, n, floors} MAP that ROUTES which grounded-knowledge category to ground
next. This is NOT a capability claim; per-category n is TINY (1-4). Directional only.

## Scope (causal-attribution categories only this pass)
Categories in {physical_harm, out_of_span_cause, counterfactual_cause,
multi_candidate_attribution, goal_blocking}. beneficiary/irony are separate read-paths, DEFERRED.

### Items included
From data/eval_gold_mention_role_mcguffey_v1/gold_grounded_comprehension_v4_DRAFT.jsonl
(causal-attribution item_type only; EXCLUDING the 3 Director-HOLD items grapp_v4_002, _004, _010):
  grapp_v4_001 (physical_harm), grapp_v4_003 (multi_candidate_attribution),
  grapp_v4_005 (out_of_span_cause), grapp_v4_006 (counterfactual_cause),
  grapp_v4_009 (goal_blocking), grapp_v4_011 (physical_harm), grapp_v4_013 (out_of_span_cause).
Prior Director-verified causal items (for power), category ASSIGNED by Director (disclosed in
metrics under category_assignment_note), from gold_grounded_appraisal_richer_v1.jsonl:
  grapp_mcca_001 (physical_harm), grapp_mcca_003 (multi_candidate_attribution),
  grapp_mcca_004 (goal_blocking), grapp_mcca_005 (multi_candidate_attribution);
from gold_grounded_causal_crossspan_v2_DRAFT.jsonl:
  grapp_mcca_007 (out_of_span_cause), grapp_mcca_008 (out_of_span_cause),
  grapp_mcca_009 (multi_candidate_attribution). EXCLUDE grapp_mcca_006 (Director-REJECTED).
Total = 14 items. Per-category n: physical_harm=3, multi_candidate_attribution=4,
out_of_span_cause=4, counterfactual_cause=1, goal_blocking=2.

## Mechanism (assemble pieces we HAVE; no new knowledge, no retrain -- bit-identical reuse)
The UNIFORM causal-attribution decision per item is the earned grounded HARM-VALENCE read from
exp_grounded_valence_read_from_text_v1, reused bit-identical (imported, not reimplemented):
  read_valences(view, "EARNED_GROUNDED", ...) = grounded_valence_evidence (situation-model
    appraisal accumulation over supplied harm/help primitives + patient/hypothetical guards) ->
    accumulate_valence (FHRR situation-model accumulate organ, hdlab.situation_model_accumulate,
    atom 29609); then
  select_from_valences = pick the candidate whose grounded valence is causally CONSISTENT with
    the (uniformly NEG) blocked/harmed outcome (=HARM); tie/neither -> ABSTAIN (counts incorrect).
Brain: hippocampal situation-model relational appraisal accumulation + appraisal->outcome
consistency selection. The valence read consumes ONLY the candidate span text (never goal/
outcome/query text) -> structurally immune to outcome-overlap gaming and leak-safe on goal.
A single uniform mechanism across all items is required for a FAIR per-category comparison.
NOTE: the effect-match/agent-attribution selector (exp_grounded_coherence_selector_v1) and the
cross-span binding organ (exp_cross_span_causal_binding_v1) are the same appraisal/selection
family; they are NOT separately combined this pass because (a) cross-span victim aliases exist
only for the mcca_001-005 slice, not v4, so they cannot be applied uniformly, and (b) the gold
already provides each item's true-cause span as candidate slot 0, so the read applied to that
span is the coverage question. out_of_span coverage landing at floor is exactly what would route
the cross-span/agent-attribution grounding as the next build.

## Arms
- EARNED_GROUNDED (mechanism): grounded valence read -> select_from_valences.
- SURFACE_VALENCE (floor): frozen blind lexicon (resolve_valence_blind) valence -> select.
- RECENCY (floor): positional -- pick the most-recent candidate at/before the query line; else
  nearest by line distance. Reads only line positions (not text), never a gold-answer field.
- RANDOM (floor): seeded uniform pick over {slot0, slot1}; expectation 0.5; multi-seed.

TRUE_SLOT = 0 (fixed bookkeeping: slot 0 = true_blocker_span). The mechanism is NOT told which
slot is the answer; it scores candidates symmetrically. Accuracy = fraction where pick == 0.

## Measurement + expectations (honest, pre-declared)
- PER-CATEGORY accuracy for each arm; overall combined accuracy.
- EXPECTED: physical_harm HIGHEST (we have that grounded knowledge -> the true span carries harm
  vocabulary the appraisal read grounds). out_of_span_cause / counterfactual_cause /
  multi_candidate_attribution / goal_blocking likely near floor (true-cause span often has NO
  surface harm verb, or needs agent-attribution/cross-span knowledge we have not grounded yet).
- Whatever the map shows IS the finding; it routes track-1.

## Determinism / floors / guards
- SEEDS = [0,1,2,3,4]; EARNED_GROUNDED/SURFACE_VALENCE/RECENCY are seed-independent (identical
  every seed); only RANDOM varies by seed. HARD_FAIL if < 5 seeds land.
- Floors-fail sanity: on the category that WORKS (physical_harm), EARNED_GROUNDED must exceed
  RANDOM and RECENCY (else mechanism is an artifact).
- Contamination: mechanism reads ONLY candidate span texts (+ line positions for recency);
  never goal/query text for valence; never any _forbidden_*/agent/recency_baseline_* field;
  primitive tables contain no proper nouns (asserted in self_test). Glass-box; NO borrowed
  embedding / LLM / parser; grounded primitives are SUPPLIED general world-knowledge (allowed),
  the READING mechanism is the substrate's own; no retrain (bit-identical import).
- Resumable per-seed (tools/exp_checkpoint.py); atomic metrics write (tmp + os.replace,
  newline='' binary); start marker + crash diag.

## Verdict bands (measurement, not pass/fail)
- HARD_FAIL_CARDINALITY if < 5 seeds.
- MECHANISM_ARTIFACT_HARM_READ_INCONSISTENT if the grounded read MISSES any item it DECODES as
  HARM-dominant true span AND non-HARM distractor (select_from_valences must attribute these) --
  that is a genuine internal-consistency/wiring failure of the mechanism. NOTE: the
  artifact gate is on the mechanism's INTERNAL CONSISTENCY, not on whether the physical_harm
  CATEGORY beats floors -- a category can fail to beat floors purely because its true-cause spans
  carry no harm vocabulary (provocation / dare / omission / misrepresentation causes), which is a
  ruler-content finding, not a broken mechanism. physical_harm-beats-floors is REPORTED as a
  diagnostic, not a gate.
- COVERAGE_MAP_MEASURED otherwise: report the per-category map + the direct-harm-act-cause
  coverage (on separable items) + the highest / floor categories + the routed next grounding
  target.
