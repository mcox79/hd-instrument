# SKUNKWORKS (Auditor) -> Testbed + Research: TIER-2 PHASE-1 validation batch (DECISION 222a PHASE-1 + 223 conventions). 6 atom specs: 3 highest-value methodology_rule (11th/13th/14th USER-LOCKED) + 3 highest-value confirmed audit_lesson (verify-not-assume [91st, just CONFIRMED] + 53rd don't-fabricate-grounding + 66th integrator-pre-ratify-catch). Authored per the RATIFIED conventions (DECISION 223: meta::RULE_<name> + corpus=meta + tier=T_methodology for methodology_rule; COMPOSES/SUPERSEDES enums for relations; term_class descriptive). audit_lesson convention PROPOSED (meta::AUDIT_<name>, corpus=meta, tier=T_audit) -- Testbed confirm. This is the small-batch spec-validation before the full ~24+88. 66th-rule pre-receive welcome.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** TIER_2_PHASE_1_atom_specs_3_methodology_rule_3_audit_lesson_validation_batch_per_ratified_conventions

## Convention note (Testbed confirm)
- methodology_rule: meta::RULE_<name>, corpus=meta, tier=T_methodology, kind=methodology_rule (RATIFIED DECISION 223).
- audit_lesson: PROPOSED meta::AUDIT_<name>, corpus=meta, tier=T_audit, kind=audit_lesson (new kind; meta corpus
  -> auto-excluded from axiom-term denominator per the corpus==MATH filter; condition-2 free). Testbed: confirm
  tier=T_audit (or reuse T_methodology) before ingest.
- relations: use COMPOSES (sibling/related rules+lessons) per Finding-3; term_class=PROCESS_KNOWLEDGE_NON_MATH
  (descriptive; gate is structural via corpus). prose_source = pointer back (condition 3).

## METHODOLOGY_RULE x3 (USER-LOCKED; highest-value)
```
  meta::RULE_substrate_internal_no_llm
     kind: methodology_rule ; corpus: meta ; tier: T_methodology ; metric_type: null
     term_class: PROCESS_KNOWLEDGE_NON_MATH ; rule_class: USER_LOCKED ; rule_number: 11 ; frozen: true
     description: "11th rule (USER-LOCKED): substrate capabilities must be demonstrated SUBSTRATE-INTERNALLY --
       deterministic, no LLM in the capability/decode/cleanup loop and no learned vector layer. Soundness is on the
       SIGNATURES, not on LLM assistance. LLM-assisted candidate SELECTION is permitted only as a bootstrap until the
       substrate self-selects; the demonstrated capability itself must run with no LLM."
     provenance: { source: "USER directive; substrate-on-its-own thesis", user_locked: true,
                   prose_source: "MEMORY.md + feedback_LLM_assisted_candidate_selection_OK_as_bootstrap" }
     relations: COMPOSES -> meta::RULE_active_state_check, COMPOSES -> meta::RULE_no_stand_default

  meta::RULE_active_state_check
     kind: methodology_rule ; corpus: meta ; tier: T_methodology ; metric_type: null
     term_class: PROCESS_KNOWLEDGE_NON_MATH ; rule_class: USER_LOCKED ; rule_number: 13 ; frozen: true
     description: "13th rule (USER-LOCKED): ACTIVE state-check every 10-15 min BETWEEN monitor events -- scan notes/
       + git log + trigger-scan + silent-session detection; do NOT wait for the monitor to fire; no meta-narration
       when execute is needed. Operationalizes the 12th rule (never-go-passive)."
     provenance: { source: "USER 2026-06-16 (kicked 3x same session same root cause)", user_locked: true,
                   prose_source: "feedback_active_state_check_every_10_15_min" }
     relations: COMPOSES -> meta::RULE_no_stand_default

  meta::RULE_no_stand_default
     kind: methodology_rule ; corpus: meta ; tier: T_methodology ; metric_type: null
     term_class: PROCESS_KNOWLEDGE_NON_MATH ; rule_class: USER_LOCKED ; rule_number: 14 ; frozen: true
     description: "14th rule (USER-LOCKED): NO STAND default at a phase boundary or wait-window. Every session has
       concrete bounded forward-work until the next gate; 'stand' or 'wait until X' is NEVER the default. The
       Director dispatches concrete next-phase prep to ALL sessions in the same turn at a phase boundary."
     provenance: { source: "USER 2026-06-16 ('everyone has stopped')", user_locked: true,
                   prose_source: "feedback_14th_rule_phase_boundary_dispatch_next_phase_prep" }
     relations: COMPOSES -> meta::RULE_active_state_check
```

## AUDIT_LESSON x3 (highest-value confirmed)
```
  meta::AUDIT_verify_not_assume_prior_lesson_applied
     kind: audit_lesson ; corpus: meta ; tier: T_audit ; metric_type: null
     term_class: PROCESS_KNOWLEDGE_NON_MATH ; lesson_class: VERIFY_DISCIPLINE
     confirmed_or_candidate: CONFIRMED ; witnesses_count: 3 ; instance_number: 91
     description: "Prior-audit-lesson-applied-to-current-observation: the auditor consciously RESISTS a pattern-match
       instinct when it contradicts a prior lesson the auditor themselves learned, and instead lets MEASUREMENT
       adjudicate. Applies to BOTH tempting NEGATIVE conclusions (don't assert 'algebraically false' at smoke) AND
       tempting POSITIVE conclusions (don't accept '1.0 accuracy = solved'; accuracy != the work claim). 3 witnesses:
       (1) DECISION-213 GATE-B structural-not-algebraic resistance; (2) STEP-7 C1 structural-vs-finite-N call;
       (3) HEAD-4 accuracy-vs-work distinction."
     provenance: { first_witness: "DECISION 213 (2026-06-16)", witness_sources: ["DECISION 213","DECISION 218","DECISION 225"],
                   prose_source: "DECISION 225b promotion record" }
     relations: COMPOSES -> meta::AUDIT_dont_fabricate_grounding, COMPOSES -> meta::AUDIT_integrator_pre_ratify_catch

  meta::AUDIT_dont_fabricate_grounding
     kind: audit_lesson ; corpus: meta ; tier: T_audit ; metric_type: null
     term_class: PROCESS_KNOWLEDGE_NON_MATH ; lesson_class: PROVENANCE_INTEGRITY
     confirmed_or_candidate: CONFIRMED ; witnesses_count: 3 ; instance_number: 53
     description: "Don't-fabricate-grounding: never ratify an atom whose grounding/DEPENDS_ON edges point to non-
       existent or low-quality dependencies. Grounding must be real-edge-walkable to atoms that exist; a named-by-
       function dependency ('CRT', 'FPE primitives') must resolve to a substrate id or be authored first
       (forward-grounded, CRT precedent)."
     provenance: { first_witness: "earlier cycle", prose_source: "MEMORY.md audit-discipline catalog" }
     relations: COMPOSES -> meta::AUDIT_integrator_pre_ratify_catch

  meta::AUDIT_integrator_pre_ratify_catch
     kind: audit_lesson ; corpus: meta ; tier: T_audit ; metric_type: null
     term_class: PROCESS_KNOWLEDGE_NON_MATH ; lesson_class: INTEGRATOR_DISCIPLINE
     confirmed_or_candidate: CONFIRMED ; witnesses_count: 3 ; instance_number: 66
     description: "Integrator-pre-ratify-catch: the integrator's pre-ratify substrate scan catches issues upstream
       sessions miss (schema drift, phantom DEPENDS_ON, convention divergence) BEFORE the ratify wrapper + upstream
       VET cycles run -- preserving cert-chain efficiency. The integrator-value-of-pre-scan. (Witnessed repeatedly:
       P1 phantom-CRT catch [92nd]; P2 HEAD-3 sparse-Hopfield gap; Tier-2 enum/convention findings [93rd cand])."
     provenance: { first_witness: "earlier cycle", prose_source: "MEMORY.md audit-discipline catalog" }
     relations: COMPOSES -> meta::AUDIT_dont_fabricate_grounding
```

## Notes for Testbed (66th-rule pre-receive welcome on this batch)
- All relations are COMPOSES to atoms CO-AUTHORED in THIS batch (no phantom; the 6 form a small closed composes-graph).
  If you ingest in sub-batches, author all 6 before wiring COMPOSES edges (or wire intra-batch only).
- CANDIDATEs are NOT in this batch (all 6 are CONFIRMED rules/lessons) -- condition-1 (candidate!=load-bearing) is
  exercised in PHASE-2 when 89th/90th/92nd land as CANDIDATEs.
- term_class is descriptive (DECISION 223: gate is structural via corpus==MATH; meta corpus auto-excluded). cap_pres
  =1.0 HARD-FAIL gate per batch. Expected delta: +6 atoms, + COMPOSES edges; axiom_term 206/206 UNCHANGED (meta corpus).
- This validates the spec end-to-end on a small batch before the full ~24 methodology_rule + 88 audit_lesson.

## Who I am gating / waiting on (9th rule)
- WAITING ON **Testbed**: 66th-rule pre-receive on these 6 specs + confirm audit_lesson tier convention (T_audit
  vs T_methodology) + ingest per CRT-pattern; report substrate delta + any spec-in-practice issues for PHASE-2.
- WAITING ON **Research (Director)**: ratify PHASE-1 ingest (1-line) if you want a ratify gate before Testbed runs.
- MY active work: PHASE-2 full batch on PHASE-1 clean; P2 STEP-4 cell-vs-cert VET reactive when Exp-Dev's cell lands;
  Tier-4a atomization support.

Tag: TIER_2_PHASE_1_atom_specs_validation_batch_3_methodology_rule_RULE_substrate_internal_no_llm_11_RULE_active_state_check_13_RULE_no_stand_default_14_USER_LOCKED_meta_corpus_T_methodology_3_audit_lesson_AUDIT_verify_not_assume_91_CONFIRMED_3_witnesses_VERIFY_DISCIPLINE_AUDIT_dont_fabricate_grounding_53_PROVENANCE_INTEGRITY_AUDIT_integrator_pre_ratify_catch_66_INTEGRATOR_DISCIPLINE_meta_AUDIT_prefix_T_audit_proposed_testbed_confirm_COMPOSES_relations_closed_graph_no_phantom_term_class_descriptive_corpus_filter_structural_cap_pres_per_batch_axiom_term_206_unchanged_meta_corpus_validates_spec_before_full_24_plus_88 -- SKUNKWORKS (Auditor)
