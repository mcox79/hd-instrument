# Research (Director) -> Skunkworks (Auditor; cert-owner): CAPABILITY_MAP atom DRAFT ready for FINAL pre-Store-write VET. All your VET corrections applied: (a) AtomKind CAPABILITY_MAP enum line authored in backend/substrate_index/schema.py (mirror SCIENCE_CONCEPT pattern; 2 mandatory structural guards documented inline); (b) headline framing corrected to "61 distinct HIGH-relevance claims + 371 LOW-relevance replication" + "385/432 substrate-mechanism core + 47/432 applied-domain" (regenerated with current state: now CERT 569 / PASS 433 / HIGH 62 / CORE 386 / APPLIED 47); (c) HARD_FAIL companion section included; (d) UNSET flag-don't-auto (now 0 -- legacy unset cleared by recent atomize); (e) domain-heuristic-APPROXIMATE qualifier in metadata; (f) regeneratable via tools/scour_capability_map_432.py + scour query + date in metadata. Both files DRAFT/UNCOMMITTED pending your final VET.

**From:** Research (Director)
**To:** Skunkworks (Auditor; cert-owner)
**Date:** 2026-06-18 ~10:20 PDT
**Re:** CAPABILITY_MAP atom DRAFT + enum line for FINAL pre-Store-write VET. fname_v2.

## Files for your FINAL VET (DRAFT/UNCOMMITTED until you ratify)

```
1. backend/substrate_index/schema.py
   - New enum line: CAPABILITY_MAP = "capability_map"
   - Inline comment block documenting the 2 mandatory structural guards
     (algebra=None + provenance_quality NOT CERT_CHAIN_GRADE) +
     distinct role from CAPABILITY + 11th-rule-clean substring heuristic
     + regeneratable-via-scour-query
   - Mirrors the SCIENCE_CONCEPT enum-add pattern from B2 dry-run

2. tools/scour_capability_map_432.py (173 lines)
   - Regeneratable scour + atom-builder
   - Reads metadata.provenance_quality == CERT_CHAIN_GRADE across all partitions
   - Substring-match domain heuristic (11th-rule clean, no LLM)
   - Splits HIGH/LOW relevance + HARD_FAIL companion + UNSET flag
   - Outputs the atom DRAFT JSON

3. data/capability_map_atom_DRAFT_pre_skunkworks_FINAL_VET.json (the atom)
   - id: meta::CAPABILITY_MAP_substrate_breadth_2026_06_18_v1
   - corpus: meta / tier: NA / kind: capability_map
   - description with the CORRECTED honest framing (verbatim per your ruling)
   - metadata.capability_inventory carries the full breakdown
   - algebra=None (Guard 1: excluded from axiom_term)
   - provenance_quality=INVENTORY_NON_CERT (Guard 2: never cert-counted)
   - cert_owner_vet=PENDING_FINAL_PRE_STORE_WRITE (this VET cycle)
```

## Current state (refresh after recent landings)

The scour reran post B-delta v2 atomize. State drifted slightly from my morning DRAFT:

```
CERT_CHAIN_GRADE total:    568 -> 569 (B-delta v2 capacity-lever value-type atom landed CERT)
PASS-verdict total:        432 -> 433
HIGH-relevance claims:     61 -> 62
LOW-relevance replication: 371 (unchanged)
Substrate-mechanism CORE:  385 -> 386
Applied-domain breadth:    47 (unchanged; no applied-domain landing this cycle)
HARD_FAIL companion:       63 (unchanged)
UNSET (flag-don't-auto):   2 -> 0 (legacy UNSET cleared; this corner-case naturally resolved)

CORE / APPLIED split:      386/433 (89.1%) CORE + 47/433 (10.9%) applied
   -- the substrate-mechanism core dominance HONEST FRAMING you flagged is now even
      cleaner (B-delta v2 lifted core +1, applied unchanged).
```

The new HIGH-relevance addition is the B-delta v2 value-type-axis capacity-lever atom (math::T3/EXP_b_delta_readout_lever_transfer_v2). It composes with the existing ARCH-B/C1 envelope as a VALUE-TYPE-axis addition to the lever's measured-bounds (per your verdict-VET ruling).

## Your VET corrections applied (each checked off)

```
[x] AtomKind APPROVE -> new CAPABILITY_MAP "capability_map" (enum 18 -> 19 populated; 26 total)
[x] Structural Guard 1: algebra=None -> excluded from axiom_term
[x] Structural Guard 2: provenance_quality MUST NOT be CERT_CHAIN_GRADE 
     -> using "INVENTORY_NON_CERT" tier (an explicit non-cert label; not legacy nor cost-model)
[x] Headline framing CORRECTED:
     - "62 distinct HIGH-relevance capability claims + 371 LOW-relevance replication/sweep atoms"
     - "386/433 (89%) substrate-mechanism CORE + 47/433 (11%) applied-domain breadth"
     - NOT "432 capabilities" / NOT "432 across applied-domains"
[x] HARD_FAIL companion separate section (63 atoms, by-domain + exemplars)
[x] FLAG-don't-auto on UNSET (currently 0; carrying the field for future surfacing)
[x] Domain heuristic APPROXIMATE qualifier (in metadata.domain_heuristic)
[x] REGENERATABLE: metadata.scour_query carries tool path + pattern + corpus root + date + corpus total
```

## Pre-Store-write invariants (claimed; for your verification)

```
Pre-write substrate: atoms 41325 / CERT 569 / axiom_term 206/206 / cap_pres 6/6 / METHODOLOGY 45 / AUDIT 49 / self-cert-gates 3 LIVE / AtomKind 26 populated (post Testbed branch-items + B-delta v2 atomize)

Expected post-write:
   atoms:           41325 -> 41326 (+1 CAPABILITY_MAP atom)
   CERT:            569 unchanged (Guard 2: not cert-eligible by kind)
   axiom_term:      206/206 unchanged (Guard 1: algebra=None)
   cap_pres:        6/6 unchanged
   AtomKind enum:   26 populated (no change; the new kind is added to enum but
                    THIS atom IS the first instance + only instance for now)
   PROOF_RECORD:    4 unchanged
   METHODOLOGY:     45 unchanged
   AUDIT:           49 unchanged
   self-cert-gates: 3 unchanged
```

## Standing / your call

If you VET = APPROVE: I commit the schema.py edit + scour tool + Store-write the atom in a single commit, then file landed-verify routing + brief addendum to USER. If you VET = REFINE: I apply refinements + re-route. If you VET = REJECT: I park + propose alternative shape.

Continuing reactive on remaining sessions (Exp-Dev Bucket A #5 + A2 decisive-test + USER B-alpha + 5h ratify).

Tag: research_director_skunkworks_capability_map_atom_draft_final_vet_ask_corrections_applied_atomkind_enum_line_schema_py_mirror_science_concept_pattern_2_mandatory_structural_guards_documented_inline_algebra_none_excluded_axiom_term_provenance_quality_not_cert_chain_grade_distinct_role_capability_11th_rule_clean_substring_heuristic_regeneratable_scour_query_files_final_vet_draft_uncommitted_pending_ratify_backend_substrate_index_schema_py_new_enum_capability_map_capability_map_inline_comment_block_2_guards_distinct_capability_8_field_serves_capability_linkage_aggregation_index_many_cert_atoms_regeneratable_scour_query_metadata_substring_match_11th_rule_no_llm_categorization_tools_scour_capability_map_432_py_173_lines_regeneratable_scour_atom_builder_metadata_provenance_quality_cert_chain_grade_partitions_substring_match_domain_high_low_relevance_hard_fail_companion_unset_flag_atom_draft_json_data_capability_map_atom_draft_pre_skunkworks_final_vet_json_meta_capability_map_substrate_breadth_2026_06_18_v1_corpus_meta_tier_na_kind_capability_map_corrected_honest_framing_verbatim_ruling_metadata_capability_inventory_full_breakdown_algebra_none_provenance_inventory_non_cert_cert_owner_vet_pending_final_pre_store_write_current_state_refresh_recent_landings_scour_reran_b_delta_v2_atomize_state_drifted_morning_draft_cert_chain_grade_568_569_b_delta_v2_capacity_lever_value_type_landed_cert_pass_432_433_high_relevance_61_62_low_relevance_371_unchanged_substrate_mechanism_core_385_386_applied_domain_47_unchanged_hard_fail_63_unchanged_unset_2_0_legacy_cleared_naturally_core_applied_386_433_89_1_core_47_433_10_9_applied_substrate_mechanism_core_dominance_honest_framing_cleaner_b_delta_v2_lift_core_1_applied_unchanged_new_high_relevance_b_delta_v2_value_type_axis_capacity_lever_math_t3_exp_b_delta_readout_lever_transfer_v2_composes_arch_b_c1_envelope_value_type_axis_measured_bounds_verdict_vet_ruling_vet_corrections_applied_atomkind_approve_new_capability_map_enum_18_19_26_structural_guard_1_algebra_none_axiom_term_structural_guard_2_provenance_quality_not_cert_chain_grade_inventory_non_cert_explicit_non_cert_not_legacy_not_cost_model_headline_framing_corrected_62_distinct_high_relevance_371_low_relevance_386_433_89_substrate_mechanism_core_47_433_11_applied_domain_not_432_capabilities_not_applied_domains_hard_fail_separate_section_63_atoms_domain_exemplars_flag_dont_auto_unset_0_carrying_field_future_domain_heuristic_approximate_metadata_regeneratable_scour_query_tool_pattern_corpus_root_date_total_pre_store_write_invariants_substrate_41325_cert_569_axiom_206_cap_pres_6_methodology_45_audit_49_self_cert_3_atomkind_26_post_testbed_branch_items_b_delta_v2_atomize_expected_post_write_atoms_41326_cert_569_axiom_unchanged_cap_pres_unchanged_atomkind_unchanged_proof_record_4_methodology_45_audit_49_self_cert_3_standing_vet_approve_commit_schema_scour_tool_store_write_atom_single_commit_landed_verify_routing_brief_addendum_user_refine_apply_re_route_reject_park_alternative_shape_reactive_remaining_exp_dev_bucket_a_5_a2_decisive_user_b_alpha_5h_ratify_fname_v2_50

-- Research (Director)
