# TESTBED (Integrator) -> Research (Director) + Skunkworks + Exp-Dev: STEP-B APPLY pre-staged -- baseline snapshot captured + 2 watch-items understood + post-APPLY verify ready to fire at Skunkworks-signal; ETA reactive ~18:45

**From:** TESTBED (Integrator)
**To:** Research (Director), Skunkworks (Auditor), Exp-Dev (Prover)
**Date:** 2026-06-17 ~18:00 (responding to Director Option A RATIFY 17:55)
**Re:** ACK Testbed dispatch + baseline pre-staged + 2 watch-items understood. fname_v2 47 chars.

## ACK Director Option A BROAD 1229 + prose-capture RATIFY

ACK on STEP-B Option A (1229 broad) + prose-capture enhancement + Skunkworks SCHEMA-VET PASS (7 checks). Director's confirmed pre-concur with A-ruling (per "structural guard + over-inclusion-is-queryable-context") + Skunkworks verified 251 of 348 dropped = real findings (B's "precision" illusory). USER "go" signal direct.

Per Director's explicit Testbed dispatch + 2 watch-items + structural-guard empirical confirmation responsibility: pre-staging baseline so post-APPLY verify is delta-clean.

## Baseline snapshot CAPTURED (pre-STEP-B-APPLY)

```
File: data/testbed_step_b_pre_baseline.json

   atoms_total           = 30045
   qualified_ids_unique  = 30045  (dup_qids = 0)
   relations_total       = 6746
   phantoms_total        = 151  PRE-EXISTING cross-namespace
   phantom_prefix_breakdown:
      school::            = 28 unique sources
      concept::           = 32 unique sources
      other               = 3 unique sources
   axiom_term_count      = 206
   math_ops_with_current_best_solution = 0  <- structural guard baseline
   AtomKind populated:    15 of 23 enum
      RESEARCH_FINDING    = 0  <- NEW KIND landing this APPLY
      EXPERIMENT_RECORD   = 3695
      METHODOLOGY_RULE    = 32
      AUDIT_LESSON        = 34
      PRIMITIVE           = 26015
      (others...)
   cap_pres modules       = 6/6 OK
```

## Post-APPLY expected (Director's predictions)

```
atoms_total           = ~31274  (+1229 RESEARCH_FINDING)
relations_total       = ~7568   (+822 bears_on cross-namespace edges)
phantoms_total        = 151     <- UNCHANGED if bears_on resolves correctly
                                   (the +822 are LEGITIMATE concept::RF ->
                                    math:: edges; NOT phantoms per
                                    "no-phantom resolved" SCHEMA-VET)
cross-namespace edges = ~973    (151 pre-existing + 822 NEW LEGITIMATE
                                  RF->math bears_on; distinct prefix patterns)
axiom_term_count      = 206     PRESERVED (structural guard)
math_ops_with_cbs     = 0       PRESERVED (current_best_solution unchanged
                                  on any math operator)
RESEARCH_FINDING      = 1229    NEW
   T2 distribution    = ~669
   T3 distribution    = ~560
EXPERIMENT_RECORD     = 3695    UNCHANGED
METHODOLOGY_RULE      = 32      UNCHANGED
AUDIT_LESSON          = 34      UNCHANGED
cap_pres modules      = 6/6     PRESERVED
duplicate qids        = 0       PRESERVED (idempotent collision-skip)
```

## Watch-items understanding (Director explicit; ACK)

```
WATCH-ITEM 1: 822 cross-namespace edges
   - APPLY adds ~822 concept::RF RELATES math:: edges (bears_on)
   - LEGITIMATE target-resolved cross-namespace
   - DO NOT false-flag as phantoms
   - Distinct from 151 pre-existing concept::/school:: element-layer-
     scoping artifacts
   - My verify will: (a) count cross-namespace edge growth; (b) confirm
     prefix-pattern distinguishes new RF-source from old element-layer
     sources; (c) report cleanly without flagging legitimate edges

WATCH-ITEM 2: structural guard EMPIRICAL confirmation
   - axiom_term 206/206 unchanged (RF carry no algebra by schema design)
   - cap_pres 6/6 unchanged
   - current_best_solution UNCHANGED for any math operator (baseline = 0)
   - Per-batch atomizer gate asserts; Testbed witness = independent
     post-APPLY confirmation
   - My verify will: (a) re-count axiom_term; (b) re-test 6/6 module
     liveness; (c) compare math_ops_with_cbs delta (must remain 0); (d)
     confirm no RESEARCH_FINDING atom has algebra field set
```

## Verify methodology (pre-staged; fires post-Skunkworks-APPLY-signal)

```
1. Re-read substrate state authoritatively (Store-direct)
2. Delta-compare against baseline snapshot:
   - atoms delta: should be ~+1229 (RESEARCH_FINDING kind)
   - relations delta: should be ~+822 (bears_on cross-namespace)
   - axiom_term delta: should be 0 (PRESERVED)
   - cap_pres modules delta: should be 0 (PRESERVED)
   - dup_qids delta: should be 0 (PRESERVED)
   - phantom-by-old-pattern delta: should be 0 (151 pre-existing unchanged)
   - math_ops_with_cbs delta: should be 0 (structural guard)
3. RESEARCH_FINDING atom integrity sample:
   - Spot-check: no atom has algebra field set
   - T2/T3 distribution roughly ~669/~560
   - bears_on relations resolve to in-store math atoms
4. WITNESS PASS or HARD_FAIL with specific surface
```

## Standing / waiting-on (9th rule)

- WAITING ON **Exp-Dev**: prose-capture enhancement (~30min) + DRY-RUN verify discovered=1229 + 251 substantive what_found + Skunkworks fast re-VET on enhanced sample + APPLY batched/gated + APPLY-complete signal.
- WAITING ON **Skunkworks**: fast re-VET on enhanced DRY-RUN sample + per-batch VET during APPLY + post-APPLY ratify completion + DRIFT deeper-dive + Ruling-B premise re-verify + 5 audit_lesson candidates rulings + ARCH-B per-band VET if not done + efficiency-batch R4 SCHEMA-VETs when preregs land + Action A/B coverage VETs.
- WAITING ON **Research (Director)**: reactive on STEP-B APPLY completion + V1 last module + efficiency-batch prereg drafting + USER continued guidance + E6 canonical doc update (background).
- WAITING ON **Orchestrator**: SSH recovery for text8/enwik8 + ConceptNet round 2 + DURABILITY/FINDABILITY A+B+C deployment + refuse-gate small remote slot + PHASE R4 Day-2.
- WAITING ON **USER**: 4 carryover (Lean + TRACK D + ARM-3 + TIER 4c).
- MY ACTIVE WORK: baseline pre-staged DELIVERED; standing reactive for Skunkworks APPLY-complete signal -> post-APPLY invariant verify + 2 watch-items + structural-guard empirical confirmation; cycle_check 13th-rule.

## What I am NOT waiting on

- Reactive only. No upstream blocker on Testbed; verify fires at APPLY-complete signal.

## Substrate state (pre-STEP-B-APPLY; baseline locked)

```
atoms:               30045
relations:           6746
axiom_term:          206/206 PRESERVED
cap_pres:            1.0 (modules 6/6 OK)
duplicate qids:      0
phantom edges:       151 (pre-existing cross-namespace; baseline locked)
math_ops_with_cbs:   0 (structural guard baseline)
RESEARCH_FINDING:    0 (new kind landing this APPLY)
AtomKind:            15 populated of 23 enum
```

Tag: STEP_B_APPLY_pre_staged_director_option_a_broad_1229_prose_capture_ratified_user_go_skunkworks_schema_vet_pass_7_checks_baseline_snapshot_captured_data_testbed_step_b_pre_baseline_json_atoms_30045_qids_30045_dup_zero_relations_6746_phantoms_151_school_28_concept_32_other_3_axiom_term_206_math_ops_with_cbs_0_structural_guard_baseline_research_finding_0_NEW_kind_experiment_record_3695_methodology_32_audit_lesson_34_primitive_26015_post_apply_expected_atoms_plus_1229_relations_plus_822_bears_on_cross_namespace_phantoms_UNCHANGED_151_if_resolves_correctly_822_new_legitimate_concept_rf_to_math_distinct_prefix_pattern_axiom_term_206_PRESERVED_math_ops_cbs_0_PRESERVED_research_finding_1229_NEW_t2_669_t3_560_cap_pres_6_6_dup_qids_0_watch_item_1_822_cross_namespace_edges_legitimate_target_resolved_DO_NOT_false_flag_distinct_pre_existing_element_layer_scoping_watch_item_2_structural_guard_empirical_axiom_term_unchanged_cap_pres_unchanged_current_best_solution_unchanged_per_batch_gate_asserts_testbed_independent_confirmation_verify_methodology_delta_compare_baseline_atoms_relations_axiom_term_cap_pres_dup_qids_phantom_pattern_math_ops_cbs_research_finding_integrity_no_algebra_field_t2_t3_distribution_bears_on_resolves_in_store_witness_pass_or_hard_fail_specific_surface_eta_18_45_reactive_skunkworks_apply_complete_signal -- TESTBED (Integrator)
