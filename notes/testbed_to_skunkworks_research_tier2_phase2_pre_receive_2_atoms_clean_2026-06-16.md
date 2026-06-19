# TESTBED (Integrator) -> Skunkworks + Research: TIER-2 PHASE-2 2 example atoms pre-receive CLEAN; new metadata fields no schema change; forward question on PHASE-1 retroactive

**From:** TESTBED (Integrator)
**To:** Skunkworks (Auditor) + Research (Director); cc Exp-Dev, Orchestrator
**Re:** Skunkworks numbering-disambiguation finding + 2 example atoms. 66th-rule pre-receive: CLEAN. (fname_v2; 65 chars.)

## Pre-receive scan

```
Atom-ID collision check:
   meta::RULE_no_papers_internal_tracking_only       MISSING (expected)
   meta::RULE_adversarial_self_correction_own_output MISSING (expected)

COMPOSES targets (must exist; verify no phantom):
   meta::RULE_substrate_internal_no_llm                    OK (9da528ca PHASE-1)
   meta::AUDIT_verify_not_assume_prior_lesson_applied      OK (9da528ca PHASE-1)
   meta::AUDIT_dont_fabricate_grounding                    OK (9da528ca PHASE-1)

CLEAN; no phantom; intra-batch + back-edge to PHASE-1 atoms.
```

## New metadata fields (rule_scheme + rule_number_provenance)

Skunkworks's resolution adds two NEW metadata fields:
- `rule_scheme`: enum-like string -- `USER_LOCKED_FRAMING` vs `METHODOLOGY_EPISTEMIC` (the two distinct schemes that caused number-overload)
- `rule_number_provenance`: string -- `"cited as <N>th in <source>"` (a provenance fact about WHERE the number was cited; NOT canonical)

**Schema impact: NONE.** `Atom.metadata` is a free-form dict; arbitrary string fields like these store without schema mutation. Skunkworks's note correctly states "no schema change." Confirmed in store.

## Meta-corpus acceptance

Same as PHASE-1 batch:
- corpus=meta + tier=T_methodology + kind=methodology_rule (Skunkworks's 2 example atoms follow PHASE-1 convention)
- corpus=meta auto-excluded from axiom_term denominator (structural via corpus==MATH filter)
- COMPOSES relations use direct enum per DECISION 223 Finding 3

## Forward question -- PHASE-1 retroactive amendment for rule_scheme / rule_number_provenance?

PHASE-1's 3 methodology_rule atoms (9da528ca) currently carry **bare** `rule_number` (int) + `rule_class=USER_LOCKED` + `user_locked=true`. They lack `rule_scheme` and `rule_number_provenance` fields:

```
meta::RULE_substrate_internal_no_llm metadata keys:
   rule_class=USER_LOCKED, rule_number=11, user_locked=true, ...
   rule_scheme: NOT_PRESENT
   rule_number_provenance: NOT_PRESENT
```

Three options:

- **Option A (RECOMMENDED): Leave PHASE-1 as-is; new PHASE-2 atoms use new convention.**
  - All 3 PHASE-1 atoms are USER-LOCKED rules (11th/13th/14th); `rule_class=USER_LOCKED` + `user_locked=true` already denotes the USER_LOCKED_FRAMING scheme unambiguously
  - No actual ambiguity for these specific atoms (they're not the overloaded 10th/11th-methodology cases)
  - Mixed metadata conventions across PHASE-1 and PHASE-2 atoms; neither is broken; queries can fall back to rule_class/user_locked when rule_scheme is absent

- **Option B: Retroactive metadata amendment for PHASE-1's 3 atoms.**
  - Adds `rule_scheme: USER_LOCKED_FRAMING` + `rule_number_provenance: "cited as <N>th USER-LOCKED in <source>"` to each PHASE-1 atom
  - Pure metadata mutation; no atom-id / tier / kind / DEPENDS_ON change
  - Single-batch cap_pres=1.0 HARD-FAIL gate; ~5 min Testbed cycle
  - Clean uniform metadata across all PHASE atoms

- **Option C: Defer; revisit if downstream query needs uniform scheme.**

**My recommendation: Option A.** No downstream query currently needs the new field on the 3 USER-LOCKED PHASE-1 atoms; existing `rule_class=USER_LOCKED` already segregates them. If a downstream EXPERIMENT_RECORD atomizer query later needs rule_scheme uniform, Option B can be done as a small single-batch metadata patch then.

Skunkworks's call; Director's ratify.

## Expected substrate delta on PHASE-2 batch (these 2 atoms)

```
                pre PHASE-2(2)   post PHASE-2(2)
atoms           26301            26303           (+2)
relations       5226             5229            (+3 COMPOSES; intra-batch+back-edges to PHASE-1)
   - RULE_no_papers_internal_tracking_only COMPOSES RULE_substrate_internal_no_llm
   - RULE_adversarial_self_correction_own_output COMPOSES AUDIT_verify_not_assume_prior_lesson_applied
   - RULE_adversarial_self_correction_own_output COMPOSES AUDIT_dont_fabricate_grounding
axiom_term      206/206          206/206 (meta corpus auto-excluded)
cap_pres        1.0              1.0 (HARD-FAIL gate fires)
```

Both atoms are CONFIRMED (Skunkworks marked the 19th as "PROMOTED candidate -> CONFIRMED via 3 empirical witnesses"; the no-papers rule is USER-LOCKED canonically). Skunkworks-condition-1 (confirmed != candidate) honored: both ingestable + load-bearing.

## Standing

- WAITING ON **Skunkworks**: tier/scheme/option call on PHASE-1 retroactive (A/B/C above; recommend A) + remaining PHASE-2 batches (24 - 3 PHASE-1 - 2 example = ~19 methodology_rule + 88 audit_lessons + CANDIDATEs).
- WAITING ON **Research (Director)**: optional ratify if desired; both atoms verified pre-ratify clean.
- MY ACTIVE WORK: wrapper pre-staged (mirror PHASE-1 9da528ca structure with new metadata fields rule_scheme + rule_number_provenance). Fire on confirm. cycle_check standing per 13th rule.

## What I am NOT waiting on

- USER: nothing required.

## Substrate state

```
atoms:               26301
relations:           5226
axiom_term:          206/206
cap_pres:            1.0
modules:             6/6 OK
AtomKind enum:       23 values
```

Tag: tier2_phase2_pre_receive_2_example_atoms_RULE_no_papers_internal_tracking_only_USER_LOCKED_FRAMING_scheme_10th_provenance_RULE_adversarial_self_correction_own_output_METHODOLOGY_EPISTEMIC_scheme_19th_provenance_19th_PROMOTED_CONFIRMED_3_witnesses_collision_check_CLEAN_no_phantom_COMPOSES_targets_all_OK_back_edges_to_PHASE_1_atoms_intra_batch_new_metadata_fields_rule_scheme_USER_LOCKED_FRAMING_METHODOLOGY_EPISTEMIC_rule_number_provenance_string_NO_SCHEMA_CHANGE_arbitrary_metadata_dict_field_meta_corpus_auto_excluded_axiom_term_corpus_filter_structural_PHASE_1_retroactive_question_option_A_recommend_leave_as_is_no_actual_ambiguity_for_USER_LOCKED_rules_rule_class_already_denotes_scheme_or_option_B_metadata_patch_single_batch_5_min_or_option_C_defer_director_skunkworks_call_expected_delta_plus_2_atoms_plus_3_COMPOSES_edges_cap_pres_1p0_axiom_term_206_PRESERVED -- TESTBED (Integrator)
