# Pre-registration: argument_structure_patient_extraction_v1 (2026-08-04)

## Problem (evidence-forced)
`exp_grounded_appraisal_transfer_to_text_v1.score_causal_item` builds both competing
causal candidates' events with `"patient": "VICTIM"` HARDCODED IDENTICALLY, and the
query is also literally `"VICTIM"`. Since `bridge_causal_antecedent`'s entity-linking gate
is `_corefers(ev["patient"], query_agent)`, this hardcoding makes the gate trivially pass
for BOTH candidates whenever their valence clears the HARM gate -- patient identity never
actually discriminates. `exp_appraisal_structure_extraction_v1` (FIX_HELPS_NARROW_
BOTTLENECK_REMAINS) fixed lexicon-coverage (valence) but left this patient collapse
untouched.

## Hypothesis
Replacing the hardcoded patient with a REAL per-candidate extracted patient (argument-
structure / thematic-role assignment on each candidate span) + coreference against a
declared per-item victim/goal-object identity will make the two candidates' patient sets
genuinely differ, and will remove any case where a candidate that should NOT qualify
(its patient does not corefer with the actual victim) is incorrectly admitted by the
gate merely because the hardcoded label matched by construction.

## Mechanism (reuse, not a new organ)
- Argument-structure extraction: `exp_read_nested_clause_relative_third_reader_v1.
  read_corpus` (the SAME hand-rule IFG-style SVO reader already validated against
  `data/gold_mcguffey_lccp_argstruct_v1.json` by `exp_learned_argstruct_parser_lccp_
  independent_gold_v1.py`), reused VERBATIM on each candidate span's raw text. One
  content-blind degenerate-tuple filter (`patient_token == verb_token`, an observed
  reader artifact) is applied identically everywhere the reader's output is consumed.
- Coreference: `hdlab.coreference_resolver.normalize_tokens` set-equality (the SAME
  primitive `exp_causal_attribution_bridging_v1._corefers` already uses), applied
  between each extracted patient token and a declared per-item VICTIM_ENTITY_ALIASES
  table (GIVEN factual identity -- proper-noun/definite-description aliases only, no
  generic pronouns, sourced from the novel's own plot facts, same tier as the accepted
  EVENT_ENTITIES table in exp_causal_attribution_bridging_v1). This is NOT the gold
  blocker/patient answer field.
- The bridge itself (`bridge_causal_antecedent`) is imported and called UNCHANGED; the
  only new code is how each event's `"patient"` field is derived before being handed to
  the unchanged bridge.

## Design (one variable)
Three patient-construction ARMS, holding theta (bit-identical reuse, digest-verified),
the bridge, `resolve_valence_blind`, and the arm_a oracle format all constant:
- `HARDCODED` (reproduces the parent transfer cell's current behavior exactly)
- `EXTRACTED_REAL` (the fix: NEST SVO reader + victim-alias coref, per candidate)
- `RANDOM_DEGENERATE` (negative control: patient token drawn from a fixed vocabulary
  disjoint-by-construction from every declared victim alias, via `torch.Generator`,
  ignoring span text entirely -- structurally CANNOT corefer)

## Primary metric
Correct-differentiation rate + deterministic (seed-consistent) correct-differentiation
item count on the 4 `multi_candidate_causal_attribution` items (per
`exp_appraisal_structure_extraction_v1`'s established convention: differentiation, not
the rec-contaminated downstream accuracy, is the trustworthy signal).
Secondary/qualitative: per-item patient sets for true vs distractor candidate (did they
become genuinely DIFFERENT?), and whether any previously-wrong-but-confident
differentiation is corrected to an honest non-answer.

## Anti-overfit (mandatory, n=100 pos instances / 114 sentences)
Validate the SAME extraction mechanism (NEST reader + degenerate filter, no per-item
victim table involved) against `data/gold_mcguffey_lccp_argstruct_v1.json` (the
independently-annotated, single-annotator argument-structure gold already used by
`exp_learned_argstruct_parser_lccp_independent_gold_v1.py`, reusing that module's own
`load_slice_and_reader`/`load_gold` on the SAME 7-lesson slice `cfg_full()` declares):
sentence-level RECALL@patient-set (does the gold patient head appear anywhere in the
extracted patient set for that sentence?) vs a shuffled-patient-set negative control.
REJECT the extraction mechanism if it helps the 4-item causal set but scores at/below
the shuffled control on the broader gold.

## Baseline-refinement note (added before the full run, after self-test tracing)
VALENCE is held constant at the prior cell's STEMMED state (`resolve_valence_fixed`), so the
HARDCODED baseline reproduces the "post-stemming 1/4 deterministic" figure the diagnosis cites
(HARDCODED correctly differentiates grapp_mcca_003 only because patient='VICTIM' trivially
matches the query 'VICTIM' — a lenient artifact of the collapse, not real patient reasoning).
This makes patient extraction the sole variable on top of the already-landed stemming fix.

## Predicted outcome (stated before running)
Given valence-lexicon coverage (not patient identity) was already diagnosed as the
dominant bottleneck on 3/4 causal items, and the NEST reader is known (informally
piloted) to return NO extractable SVO relation at all for 2/4 true-candidate spans
(embedded-PP / unaccusative constructions it was never built for), the most likely
outcome is: patient sets become genuinely different between candidates (fixing the
literal collapse the task describes), CORRECT differentiation on the 4-item causal set
stays flat (0/4 -> 0/4, since patient was never actually gating a would-be-correct
candidate here), but at least one previously wrong-but-confident differentiation
(grapp_mcca_005, distractor wrongly admitted only because the hardcoded patient
trivially matched) is corrected to an honest non-differentiation. This would be
EXTRACTION_STRUCTURALLY_FIXED_NO_SCALAR_LIFT, an informative negative on the tiny slice
paired with whatever the broader-gold recall number shows about the mechanism's general
quality -- not forced into a false positive.

## Verdict bands
- `PATIENT_FIX_IMPROVES_DIFFERENTIATION`: EXTRACTED_REAL correct-differentiation >
  HARDCODED correct-differentiation on the 4-item set, negative control fails, anti-
  overfit recall beats shuffled control.
- `PATIENT_FIX_STRUCTURAL_ONLY_NO_SCALAR_LIFT`: patients differ per-candidate on >=1
  item (collapse genuinely fixed), correct-differentiation flat (not regressed),
  negative control fails, anti-overfit recall beats shuffled control.
- `PATIENT_FIX_REJECTED`: regresses correct-differentiation, OR negative control passes,
  OR anti-overfit recall at/below shuffled control.

## Fairness / guards
- No gold-answer (`true_blocker_span`/`true_blocker_agent`) field is read by the
  extraction; VICTIM_ENTITY_ALIASES is declared BEFORE running, from plot facts only.
- `torch.Generator` seeding, `sorted(set())`, no `hash()`-seed.
- `arms_must_differ` (META_RULE_AF): HARDCODED vs EXTRACTED_REAL and HARDCODED vs
  RANDOM_DEGENERATE must differ on the 4-item vector (both do, via grapp_mcca_005).
  EXTRACTED_REAL vs RANDOM_DEGENERATE is EXPECTED to collapse on this 4-item slice
  (the real extractor finds zero alias matches here too, same operational outcome as
  random for structurally different reasons) -- exempted on the tiny slice, PROVEN
  to differ instead on the n=100 anti-overfit gold (real extraction sentence-level
  recall vs shuffled-patient-set recall), which is the more informative sample size.
- Resumable per-unit via `tools/exp_checkpoint.py`.
