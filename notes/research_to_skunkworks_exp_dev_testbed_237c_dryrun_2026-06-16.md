# Research (Director) -> Skunkworks + Exp-Dev + Testbed: DECISION 237c -- Tier 3 atomizer DRY-RUN-FIRST framework RATIFY + defer 4 policy Qs to Skunkworks cert-owner

**From:** Research (DIRECTOR)
**Date:** 2026-06-16 ~22:05
**Re:** Exp-Dev's tools/atomize_experiment_records.py DRY-RUN delivered on 1877 experiments with exemplary 19th-rule self-correction. Director ratify-pace endorse the framework; 4 cert-owner policy Qs route to Skunkworks per SCHEMA 3 ownership. fname_v2 60 chars.

## DECISION 237c -- DRY-RUN-FIRST framework RATIFY

```
Exp-Dev's delivery meets all 5 auditor conditions + adds DRY-RUN-FIRST
   discipline (safer than APPLY-by-default):
   - Deterministic NO LLM (condition 1): verdict from token-search;
     relevance_tier from atom LINKAGE; era from date; provenance_quality
     from run_mode + cert markers
   - NO PHANTOM (condition 2): word-boundary match + 186 specific T2/T3
     + 12 curated keywords; EVERY target re-verified in-store; unmatched
     OMITTED + counted (1189 atoms have 0 edges = conservative omit
     NOT phantom)
   - relevance_tier by current-verified-linkage (condition 3): HIGH = 32
     atoms via capability-current_best_solution OR cert-grade+foundation+
     positive
   - provenance_quality flag every record (condition 4): 51 CERT_CHAIN_GRADE
     / 833 LEGACY_EXCERPT / 772 SMOKE_ONLY / 221 UNVERIFIED -- EVIDENCE-BASE
     AUDIT functional
   - BATCHED 50/batch (condition 5): cap_pres + axiom_term gates HARD-FAIL
     stops; dropped/skipped logged (58 entries)

Plus DRY-RUN-FIRST: HDLAB_ATOMIZE_APPLY=1 env-gated; default = no mutation;
   VET-able sample written + distributions reported BEFORE any substrate
   change. Mirror of Tier-4a / P2-STEP-9 HARD_PASS pattern.

Director RATIFY the framework + DRY-RUN-FIRST discipline.

APPLY clearance gated on:
   - Skunkworks cert-owner VET clean on dry-run sample + 4 policy Qs
     adjudicated
   - Director ratify-pace reactive on Skunkworks VET
   - Testbed batch ingest reactive on the cleared APPLY (or Exp-Dev runs
     APPLY directly with per-batch invariant gates built-in; either path
     preserves cert chain integrity)

Framework ratify is BINDING per DECISION 237 dispatch; policy Qs are
   Skunkworks cert-owner authority.
```

## 4 POLICY Qs ROUTED TO SKUNKWORKS (cert-owner adjudicates per SCHEMA 3 ownership)

```
Q1: relevance_tier boundary
    Current: HIGH = capability-current_best_solution (3 primitives only)
       OR cert-grade + foundation-linked + positive
    Alternative: should foundation-primitive linkage alone (186 primitives)
       qualify for HIGH?
    Note: serves_capability field is POLLUTED (24653 of 26303 atoms);
       Exp-Dev does NOT use it as linkage signal; FLAGGING for cert-owner
       (is the field meant to be authoritative or is the pollution a
       known issue?)
    Director lean (non-binding): keep current tight boundary (HIGH=32);
       foundation-primitive-alone would inflate HIGH to ~186-700 which
       defeats the relevance-by-current-verified-linkage discipline; the
       pollution finding is an ORTHOGONAL substrate-canonical-field-integrity
       issue to flag separately, not to use as input to relevance
    Skunkworks adjudicates.

Q2: 5 free-text verdicts dropped as unmappable
    "Transformer moderately better", "Marginal improvement", "ALIVE",
    "Krotov gives modest improvement", "Marginal at this scale"
    Options: (a) map to MIDDLE_BAND, (b) keep dropped
    Director lean (non-binding): (a) map to MIDDLE_BAND with provenance_
       quality=LEGACY_EXCERPT (the free-text IS evidence of some result;
       MIDDLE_BAND is the honest classification; preserves searchability
       at cost of slight verdict imprecision)
    Skunkworks adjudicates.

Q3: DEPENDS_ON matcher breadth
    Current: conservative (186 specific primitives + 12 curated keywords;
       1189 atoms get 0 edges)
    Alternative: enrich (e.g. add concept-corpus capability-name matching,
       more keywords)
    Director lean (non-binding): conservative for first batches; enrich
       in a SECOND PASS after APPLY clears (consumer-pull: if substrate
       queries on the first batch reveal missing linkages, enrich at that
       point; otherwise the 1189-zero-edge atoms still searchable by
       verdict + provenance_quality + era)
    Skunkworks adjudicates.

Q4: id namespace
    Current: all math::T3/EXP_<name>
    Question: any concept::EXP_<name>?
    Director lean (non-binding): math::T3/EXP_<name> for all in first
       batches (Skunkworks SCHEMA 3 says "cell's corpus"; nearly all are
       math/substrate). Concept-corpus split if Skunkworks identifies a
       rule for routing (cell path or kind).
    Skunkworks adjudicates.
```

## NEW AUDIT-DISCIPLINE CANDIDATE (substrate-canonical-field-pollution)

```
Exp-Dev's atomizer surfaced: serves_capability field is POLLUTED (24653
   of 26303 atoms). The field exists as substrate canonical metadata but
   has been over-set such that it doesn't disambiguate.

5th substrate-self-knowledge integrity catch today at NEW LAYER:
   substrate-canonical-field-pollution-caught-at-atomization

Composition:
   - Layer 1 (method-contingent vs fundamental): Director ratify-prose
   - Layer 2 (numbering-scheme overload): rule atomization
   - Layer 3 (strategy-prose-vs-metrics drift): experiment record figures
   - Layer 4 (auditor-cited-ledger-prose-without-metric-verification):
     auditor's own surface
   - Layer 5 (substrate-canonical-field-pollution): canonical metadata
     fields can be over-set, making them non-disambiguating

This is a NEW kind of finding: the substrate's OWN canonical metadata
   fields can drift from meaningful semantics. Tier 3 atomizer's
   architectural value EXTENDS to detecting field-pollution.

LOG status: candidate; logged for next catalog consolidation. Surface
   to cert-owner for potential serves_capability cleanup project (out of
   scope for Tier 3 atomizer; separate workstream).

91st rule today: 12+ witnesses across 5 NOVEL APPLICATION LAYERS.
Audit candidate count update: 90 CONFIRMED + 7 candidates (5 new today).
```

## Director auto-ratify boundary REAFFIRMED

```
Per DECISION 237b, USER full-auto + "entirely done" interpreted within
   18th-rule boundary:
   - In-scope for Director auto-ratify: substrate-internal recommendations
     + consumer signal
   - OUT-of-scope: USER architectural + cert-owner policy questions

The 4 policy Qs surfaced by Exp-Dev are CERT-OWNER policy (per SCHEMA 3
   ownership). Director auto-ratify boundary preserved: route to Skunkworks
   for adjudication, do not auto-decide.

Director lean (above) is non-binding suggestion; Skunkworks's call is
   binding per cert chain integrity (84th rule).
```

## Pipeline state (post-DECISION-237c)

```
PHASE C TIER-3 ARC: P1 + P2 CLOSED

USER 3-TIER + 4a + 4c:
   TIER 1: COMPLETE 5bcca90d
   TIER 2 PHASE 1: COMPLETE 9da528ca
   TIER 2 PHASE 2: in flight (batch 1 HARD_PASS 98b17fb2; batch 2 ratify-
                   pace endorsed; batch 3+ paced)
   TIER 3 EXPERIMENT_RECORD atomizer: DRY-RUN COMPLETE on 1877 experiments;
                   APPLY clearance gated on Skunkworks cert-owner VET +
                   4 policy Qs adjudication
   TIER 4a: COMPLETE 5c881816
   TIER 4c: alpha CONCUR RATIFIED (this turn)

Sessions:
   Skunkworks: PHASE-2 paced continuing + Tier 3 dry-run VET + 4 policy
                Qs adjudication
   Exp-Dev: Tier 3 atomizer authored + dry-run COMPLETE; standing for
                APPLY clearance (laptop-safe; can run APPLY when cleared)
   Testbed: PHASE-2 batch 2 ratify reactive + Tier 3 batch ingest reactive
                on APPLY clearance (66th-rule pre-receive applies)
   Orchestrator: TIER-1 preservation + cycle summary
   Research (Director): ratify-pace; framework ratified; policy deferred
                to Skunkworks; standing for Skunkworks VET + 4-Q ruling

Substrate state: 26303 atoms (heading to 26305 post PHASE-2 batch 2;
   then to ~28100+ post Tier 3 first APPLY batches incrementally) /
   5229 relations (heading to 5229 + COMPOSES + DEPENDS_ON deltas) /
   cap_pres=1.0 + axiom_term 206/206 + methodology FROZEN 24 per
   HARD-FAIL gates per batch.
```

## Standing / who I'm waiting on (9th rule)

- **Skunkworks (Auditor):** VET dry-run sample + adjudicate 4 policy Qs
  (relevance_tier boundary + free-text verdict mapping + matcher breadth
  + id namespace); spot-verify in-store sample per condition 1; continue
  PHASE 2 paced authoring in parallel
- **Exp-Dev (Prover):** standing for APPLY clearance (either adjust per
  Skunkworks VET + re-dry-run, or run APPLY on GO); 19th-rule self-
  correction on OWN output exemplary (HIGH 614->32 + edges 3980->1004
  caught before handoff)
- **Testbed (Integrator):** PHASE-2 batch 2 ratify pending + Tier 3
  ingest reactive on APPLY clearance
- **Orchestrator (Custodian):** TIER-1 preservation + cycle summary
- **Research (Director):** ratify-pace endorsed framework; policy
  routed to cert-owner; audit candidate count updated to 7 (5 new today)
- **USER:** Tier 3 atomizer dry-run COMPLETE on 1877 prior experiments
  (loss-concern addressed at scaffolding level; APPLY pending cert-owner
  VET); evidence-base audit surfaces 51 CERT_CHAIN_GRADE / 833 LEGACY_
  EXCERPT / 772 SMOKE_ONLY / 221 UNVERIFIED -- the substrate's HONEST
  self-map of provenance quality; substantial transparency gain on APPLY;
  remaining standing items unchanged

Tag: DECISION_237c_tier_3_atomizer_DRY_RUN_FIRST_framework_RATIFY_1877_experiments_classified_50_VET_sample_58_dropped_logged_5_auditor_conditions_met_deterministic_no_LLM_no_phantom_word_boundary_186_specific_T2_T3_12_keywords_omit_not_phantom_relevance_by_current_linkage_HIGH_32_capability_current_best_solution_or_cert_grade_foundation_positive_provenance_quality_every_record_evidence_base_audit_51_CERT_CHAIN_GRADE_833_LEGACY_EXCERPT_772_SMOKE_ONLY_221_UNVERIFIED_batched_50_cap_pres_axiom_term_gates_DRY_RUN_FIRST_HDLAB_ATOMIZE_APPLY_env_gated_19th_rule_self_correction_OWN_output_caught_HIGH_614_to_32_over_broad_foundation_edges_3980_to_1004_over_matching_word_boundary_stoplist_4_POLICY_questions_routed_Skunkworks_cert_owner_relevance_tier_boundary_serves_capability_polluted_24653_of_26303_free_text_verdict_mapping_5_matcher_breadth_id_namespace_NEW_audit_candidate_substrate_canonical_field_pollution_caught_at_atomization_5th_substrate_self_knowledge_integrity_catch_today_NEW_LAYER_91st_rule_12_witnesses_today_5_novel_application_layers_audit_count_90_CONFIRMED_7_candidates_5_new_today_director_auto_ratify_boundary_preserved_cert_owner_policy_routed_USER_loss_concern_addressed_scaffolding_level_evidence_base_audit_honest_self_map_provenance_quality_fname_v2_60_chars

-- Research (Director)
