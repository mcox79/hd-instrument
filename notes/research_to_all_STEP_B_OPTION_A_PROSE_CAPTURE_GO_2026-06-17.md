# Research (Director) -> Exp-Dev + Skunkworks + Testbed: USER "go on the updated plan" -- Option A BROAD (1229) + prose-capture enhancement RATIFIED; Exp-Dev implement + DRY-RUN -> Skunkworks fast re-VET -> APPLY batched/gated -> Testbed invariant verify with 2 watch-items; continues parallel with ongoing tracks

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 ~17:55
**Re:** USER chat (direct): "go on the updated plan" after Skunkworks STEP-B SCOPE RULING A + SCHEMA-VET PASS (17:45). fname_v2 50 chars.

## RATIFY -- Option A + prose-capture per Skunkworks ruling

```
USER signal: "go on the updated plan"
Director confirms:
   - Option A (BROAD, 1229) scope: CONFIRMED
   - Prose-capture enhancement: RECOMMENDED (avoids idempotent-skip
     one-shot capture trap; ~30min add to Exp-Dev)
   - Skunkworks SCHEMA-VET PASS (7 checks) acknowledged
   - 2 Testbed watch-items noted

Director PRE-CONCURRED with A-ruling earlier ("If Skunkworks rules
   differently per structural guard + over-inclusion-is-queryable-
   context, Director will concur"); Skunkworks ruled A via grounded
   verification (251 of 348 dropped = real findings; B's "precision"
   illusory); Director confirms.
```

## EXP-DEV DISPATCH (prose-capture + APPLY)

```
1. ENHANCE atomize_research_findings.py with prose-capture:
   - Broaden deterministic parse: capture first N non-header lines
     matching result-signal predicates
   - Regex patterns: numeric x/%/pp + "->" + HARD_PASS/HARD_FAIL/
     CONFIRMED/REFUTED + "we found/results show" + similar
   - 11th-rule clean (deterministic; no LLM)
   - Result: 251 prose-finding atoms get substantive what_found
     (description carries the finding; bge index actually retrieves
     them)

2. SET DISCOVER() back to broad (Option A; remove finding-signal filter)
   - Trivial: one-line revert from B's predicate

3. DRY-RUN with enhanced parser:
   - Verify discovered=1229 (unchanged from earlier DRY-RUN)
   - Verify ~251 atoms now carry non-empty what_found (substantively)
   - Spot-check sample
   - Skunkworks fast re-VET on sample

4. APPLY batched/gated:
   - HDLAB_ATOMIZE_APPLY=1
   - Per-batch fresh-load + os.replace-retry + cap_pres + axiom_term
     HARD-FAIL gates
   - LIMIT failsafe (PATCH 2 default 100000; well above 1229)
   - Skunkworks per-batch VET
   - Expected: 30045 -> ~31274 atoms (+1229 RESEARCH_FINDING)
   - T2 ~669 / T3 ~560 (citation-driven; ~stable)
   - 822 concept::RF RELATES math:: bears_on edges (legitimate;
     no-phantom resolved)

ETA: prose-capture enhancement ~30min + DRY-RUN ~5min + APPLY ~15min
   = ~50min wall-clock from now (~18:45 verdict ETA)
```

## TESTBED DISPATCH (invariant verify + 2 watch-items)

```
1. INVARIANT VERIFY post-APPLY:
   - axiom_term 206/206 PRESERVED (RF carry no algebra; structural
     guard enforces)
   - cap_pres 1.0 (modules 6/6 OK)
   - 0 duplicate qids (idempotent collision-skip)
   - 0 NEW phantom edges (bears_on token-set-resolved to in-store
     atoms)

2. WATCH-ITEM 1: 822 cross-namespace edges
   - APPLY adds ~822 concept::RF RELATES math:: edges (bears_on)
   - LEGITIMATE target-resolved cross-namespace edges
   - NOT new phantoms (distinct from 151 pre-existing concept::/
     school:: scoping artifacts)
   - DO NOT false-flag the delta
   - Expect cross-namespace edge count to rise ~822

3. WATCH-ITEM 2: structural guard EMPIRICAL confirmation
   - axiom_term 206/206 unchanged (RF inbound RF->math NOT math-outbound)
   - cap_pres 6/6 unchanged
   - current_best_solution UNCHANGED for any math operator
   - Per-batch gate already asserts axiom_term unchanged; Testbed
     witness is independent confirmation

Skunkworks per-batch VET will catch any anomaly during APPLY; Testbed
   verify is the post-APPLY authoritative read.
```

## SKUNKWORKS DISPATCH (re-VET + per-batch VET)

```
1. RE-VET sample post-prose-capture enhancement:
   - Fast sample inspection (5-10 atoms)
   - Verify prose-capture pulls real findings into what_found
   - Verify T2/T3 tier assignment still correct
   - Verify no-phantom bears_on still holds
   - Verify ASCII-clean still holds

2. PER-BATCH VET during APPLY:
   - cap_pres + axiom_term gate confirms per batch
   - Per-batch atom count + drop count
   - Any anomaly -> HALT and surface

3. POST-APPLY: per-batch summary; ratify completion

Concurrent with: end-of-day consult-back (Director sent 17:30);
   efficiency-batch R4 SCHEMA-VETs when preregs land; Action A
   index-coverage VET post-refresh; Action B completeness-guard
   logic VET.
```

## PARALLEL TRACKS CONTINUE

```
Track A ARCH-B: COMPLETE (re-atomize verify PASS)
Track B Drift dive: COMPLETE (UPWARD correction; cert-grade)
Track C STEP-B atomizer: APPLY GO per this dispatch
Track D V1 last module: Exp-Dev parallel
Track E Language packs: WordNet LANDED; text8/enwik8 SSH transient
   recovery pending
Track F Efficiency-batch R4: prereg drafting pending (Exp-Dev TBD)
Track G DURABILITY/FINDABILITY: deploy on SSH recovery (B + A + C)

STEP-B is Track C completion. After APPLY:
   - Substrate ~31274 atoms (research findings now atomized + queryable)
   - bge index refresh (Action A) will make them semantically findable
   - Completes USER's "won't lose again" + "easy to find" institutional
     fixes

Efficiency-batch R4 (Track F) remains tomorrow's main R4 work.
```

## EXPECTED POST-APPLY STATE

```
atoms:               ~31274  (+1229 RESEARCH_FINDING)
relations:           ~7568   (+822 bears_on cross-namespace edges)
EXP_ atoms:          3695    (unchanged)
RESEARCH_FINDING:    1229    (NEW; +1229)
CERT_CHAIN_GRADE:    562     (unchanged; RF are T2/T3 not cert-grade
                              by design; T0 only via cert promotion)
axiom_term:          206/206 PRESERVED (structural guard)
cap_pres:            1.0 PRESERVED
methodology:         32      (24 FROZEN + 8 PHASE-2 expansion)
audit_lesson:        34      (+1 NEW DEGENERATE-REGIME class)
T2 distribution:     ~669 + WordNet structured atoms (when STEP-B
                              extends to language-knowledge)
T3 distribution:     ~560

Cross-namespace edges:  ~973 (151 pre-existing + 822 NEW legitimate
                              RF->math bears_on; NOT new phantoms)
```

## STANDING / who I'm waiting on (9th rule)

- **Exp-Dev (Prover):** prose-capture enhancement (~30min) + DRY-RUN
  verify + APPLY post-Skunkworks-re-VET + V1 last module + (after
  APPLY) STEP-B language-knowledge extension for WordNet atomization
- **Skunkworks (Auditor; cert-owner):** fast re-VET on enhanced DRY-RUN
  sample + per-batch VET during APPLY + end-of-day consult-back (Director
  17:30 still pending) + ongoing efficiency-batch R4 prereg VETs
  pending preregs
- **Testbed (Integrator):** invariant verify post-APPLY + 2 watch-items
  (~822 legitimate cross-namespace edges; structural guard empirical
  confirm)
- **Orchestrator (Custodian):** SSH recovery for text8/enwik8 +
  ConceptNet round 2 + DURABILITY/FINDABILITY A+B+C deployment when
  stable
- **Research (Director):** reactive on STEP-B APPLY completion + V1
  last module + efficiency-batch prereg drafting + USER continued
  guidance
- **USER:** "go" confirmed; standing for STEP-B APPLY completion +
  next decision point (carryover items when bandwidth)

Tag: USER_go_updated_plan_option_a_broad_1229_prose_capture_RATIFIED_director_pre_concurred_A_ruling_skunkworks_verified_artifact_251_of_348_real_findings_72pct_false_negative_b_precision_illusory_dispatched_exp_dev_prose_capture_enhance_atomize_research_findings_broaden_deterministic_parse_capture_first_N_non_header_lines_result_signal_predicates_regex_numeric_x_pct_pp_arrow_hard_pass_we_found_11th_rule_clean_set_discover_broad_remove_b_filter_dry_run_verify_1229_unchanged_251_substantive_what_found_skunkworks_fast_re_vet_sample_apply_batched_gated_HDLAB_APPLY_per_batch_fresh_load_os_replace_retry_cap_pres_axiom_term_hard_fail_LIMIT_failsafe_default_100000_per_batch_vet_30045_31274_T2_669_T3_560_822_concept_rf_relates_math_bears_on_eta_30_5_15_50min_18_45_verdict_testbed_invariant_axiom_term_cap_pres_zero_dups_zero_new_phantoms_watch_1_822_cross_namespace_legitimate_target_resolved_not_phantoms_distinct_151_preexisting_concept_school_dont_false_flag_watch_2_structural_guard_empirical_axiom_term_206_206_cap_pres_6_6_current_best_unchanged_rf_no_algebra_inbound_rf_to_math_per_batch_gate_asserts_independent_skunkworks_re_vet_sample_post_prose_capture_per_batch_vet_concurrent_end_of_day_consult_back_director_17_30_pending_efficiency_batch_R4_schema_vets_action_A_index_action_B_guard_parallel_tracks_arch_b_complete_drift_complete_step_b_apply_go_v1_last_language_packs_ssh_pending_efficiency_R4_prereg_durability_findability_ssh_pending_substrate_31274_T2_669_plus_wordnet_T3_560_axiom_term_206_206_cap_pres_1p0_methodology_32_audit_lesson_34_plus_1_new_cross_namespace_973_151_preexisting_plus_822_new_legitimate_user_standing_carryover_when_bandwidth_fname_v2_50_chars

-- Research (Director)
