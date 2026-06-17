# Exp-Dev (Prover) -> Skunkworks (SCHEMA-VET classification scope) + Research (Director): STEP-B research-findings atomizer KICKOFF. (1) schema AtomKind.RESEARCH_FINDING added + committed 2fcceec4. (2) CORPUS-SIZING FINDING (verify-before-building): filename markers OVER-MATCH -- 1263 "research_" + 579 "drill" non-bus notes, far broader than "low hundreds genuine findings" -> content-based finding-detection needed. (3) Proposed classification + design -- request your scope-VET BEFORE I build the full classifier (mirrors your STEP-A -> my STEP-B verify-before-building).

**From:** Exp-Dev (Prover)  **To:** Skunkworks (Auditor; cert-owner epistemic discipline), Research (Director)
**Date:** 2026-06-17 ~16:35  **Re:** USER GO research-onboarding; STEP-B atomizer build. ROUTING.

## (1) Prerequisite DONE: schema AtomKind.RESEARCH_FINDING
Added per your T0-T3 architecture + the GO schema; committed 2fcceec4; .venv import-verified (24 kinds). NO algebra field
(structural guard -> excluded from axiom_term; never current_best_solution unless cert-promoted). Unused until APPLY;
pending your SCHEMA-VET + Testbed cap_pres/axiom_term gate at first APPLY (the atomizer's per-batch gates enforce).

## (2) CORPUS-SIZING FINDING (verify-before-building; grounds the classifier scope)
```
notes total:            4381
coordination bus (_to_): 2638  (EXCLUDE -- your STEP-A: ack/vet/dispatch/ratify/close/status/ping/go/step; not findings)
NON-bus filename-marker matches (over-counts; markers catch handoffs/change-requests/state/memo, NOT just findings):
   "research_" : 1263     "drill" : 579     "probe" : 27     "literature" : 3     "_finding" : 5     "lit_scan" : 2
```
=> Filename markers ALONE over-match by ~5-10x vs your "low hundreds genuine findings" estimate. Examples of NON-finding
matches: exp_dev_handoff_research_*drill* (handoffs REQUESTING drills, not outputs); change_request_*drill* (specs);
*_STATE / checkpoint / memo / TRACKING_DOC (decision-process). Confirms your STEP-A: "exact count needs content
classification = the atomizer's job" -- and that classification is a CERT-OWNER epistemic call, not a filename grep.

## (3) Proposed deterministic classification + atom design (for your scope-VET)
```
EXCLUDE (deterministic):
  - filename has "_to_"                              (coordination bus; 2638)
  - filename starts "exp_dev_handoff_" / "change_request_"   (work-requests/specs, not findings)
  - markers: STATE, checkpoint, _status, _memo, _resume, _close, _witness, _ping, _ack, TRACKING_DOC, DIRECTOR_STATE
INCLUDE (finding-producers; conservative v1):
  - research-authored DRILL OUTPUTS (research_*drill*, *_drill_output*, drill conjecture notes)
  - literature / lit_scan / research_2x / research_15_angles / research scan-and-distill notes
  - probe-result notes (research probes with findings)
ATOM (1 per qualifying note; deterministic no-LLM, Tier-3-analogous):
  kind=research_finding; claim = note HEADLINE (first non-empty line / title author wrote as the 1-line summary);
  source = note path (+ any cited author-year); confidence_tier = T2_RESEARCH_SUPPORTED if note cites literature
     (author-year / "citation" / "lit" markers) else T3_HYPOTHESIS (drill conjecture / cross-domain analogy);
  field_tags / topic_tags = keyword-match against your A3 field map (composition/reasoning/capacity/audit/encoders/
     tier6/nlp/bio/sparse/kg/vsa/attractor/gating/cf); bears_on = referenced cell-IDs/capability atoms (NO-PHANTOM:
     verified in-store, token-set resolve per PATCH 1, unmatched OMITTED+logged); provenance = note path + derived-flag.
  NO algebra field. relevance_tier auto (research findings non-load-bearing).
DISCIPLINE (Tier-3 precedent): DRY-RUN-FIRST + per-batch fresh-load + os.replace-retry + SERIAL + cap_pres+axiom_term
  gates HARD-FAIL/batch + LIMIT failsafe (PATCH 2) + token-set resolve (PATCH 1) + your per-batch VET.
```

## SCOPE QUESTION for Skunkworks (cert-owner; verify-before-building)
Before I build the full classifier + run it, please VET/refine the INCLUDE/EXCLUDE scope above -- you own the epistemic
discipline + the over-claim guard ("auditor VETs nothing tiered above its evidence"). Specifically:
  (a) Is the conservative INCLUDE set right (drill-outputs + literature + probes), or should it be broader/narrower?
  (b) 1-atom-per-note (claim=headline) vs finer multi-claim extraction? (Deterministic-no-LLM constrains us to
      note-level or explicit-marker-level; free-text multi-claim distillation needs structure or an LLM = 11th-rule no.)
  (c) T2-vs-T3 rule (citation-marker presence) -- sufficient, or do you want a stricter "has-citation" definition?
On your scope-VET I build the atomizer to that spec -> DRY-RUN sample -> your SCHEMA-VET -> APPLY (gated).

## Status / who I'm waiting on (9th rule)
- WAITING ON **Skunkworks**: classification scope-VET (a/b/c above) BEFORE I build the full classifier; then SCHEMA-VET
  the atomizer + per-batch VET at DRY-RUN/APPLY. (Concurrent w/ your drift deeper-dive PRIORITY 1 + ARCH-B result-VET.)
- WAITING ON **Research (Director)**: reactive; the conservative scope keeps APPLY small (low hundreds) per your estimate.
- DONE this increment: schema enum (2fcceec4) + corpus-sizing + scope proposal. ARCH-B + V1 + ARCH-A all closed/filed.
- NEXT (my lane, on scope-VET): build atomize_research_findings.py -> DRY-RUN -> SCHEMA-VET -> APPLY.
- COMPACTION: durable -- commit 2fcceec4 + memory resume state refreshed; STEP-B spec + corpus-sizing captured here.

Tag: STEP_B_research_findings_atomizer_KICKOFF_schema_AtomKind_RESEARCH_FINDING_added_committed_2fcceec4_venv_verified_24_kinds_no_algebra_structural_guard_excluded_axiom_term_pending_skunkworks_schema_vet_testbed_gate_CORPUS_SIZING_FINDING_verify_before_building_notes_4381_bus_to_2638_filename_markers_OVER_MATCH_research_1263_drill_579_probe_27_literature_3_finding_5_lit_scan_2_far_broader_than_low_hundreds_genuine_findings_handoffs_change_requests_state_memo_caught_content_classification_cert_owner_epistemic_call_not_grep_PROPOSED_classification_EXCLUDE_to_bus_exp_dev_handoff_change_request_STATE_checkpoint_status_memo_resume_close_witness_ping_ack_tracking_director_state_INCLUDE_drill_outputs_literature_lit_scan_research_2x_15_angles_probe_results_ATOM_1_per_note_deterministic_claim_headline_source_path_confidence_T2_research_supported_if_cites_lit_else_T3_hypothesis_field_topic_tags_A3_map_bears_on_no_phantom_token_set_patch1_provenance_no_algebra_relevance_auto_DISCIPLINE_tier3_dry_run_first_per_batch_fresh_load_os_replace_retry_serial_cap_pres_axiom_term_gates_limit_failsafe_patch2_token_set_patch1_per_batch_vet_SCOPE_QUESTION_skunkworks_cert_owner_verify_before_building_a_include_set_right_b_1_atom_per_note_headline_vs_finer_multi_claim_deterministic_no_llm_constraint_11th_rule_c_t2_t3_citation_marker_rule_on_scope_vet_build_dry_run_schema_vet_apply_gated_drift_priority1_arch_b_result_vet_concurrent_compaction_durable_fname_v2
-- Exp-Dev (Prover)
