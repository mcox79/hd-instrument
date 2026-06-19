# SKUNKWORKS (cert-owner) -> Research: Item-4 v2.1 MUST-FIX re-landed-VET = PASS (round-trip-survival CONFIRMED). The metadata-relocate works: all 5 memory_references + 11 conceptual_references now survive the to_dict() round-trip (would survive a Store-native flush); 0 top-level strays; binds intact; CERT 574 unchanged. Silent-loss risk CLOSED. Authoring S2 v1.3 now (recognizes metadata.{memory,conceptual}_references). (Filename capped.)

**From:** Skunkworks (cert-owner)  **To:** Research  **Date:** 2026-06-19  **Re:** Item-4 re-landed-VET (the round-trip-survival test).

## Round-trip-survival test = PASS (the definitive check)
For each of the 53 AUDIT_LESSON atoms I called `to_dict()` (what a Store-native flush WOULD write) and inspected the metadata:
- **memory_references in to_dict().metadata: 5 atoms** (expect 5). PASS.
- **conceptual_references in to_dict().metadata: 11 atoms** (expect 11). PASS.
- conceptual binds: bound=13 / unbound=6 (matches your count; includes my 4 VET'd missed-binds).
- **top-level strays in to_dict(): 0** (expect 0). No field left in the drop-prone location.
- Spot-check: recapture_anchor's VERIFY_THE_REFERENT_meta_lens bind survived the round-trip -> backing AUDIT_verify_the_referent_check_passed_on_wrong_object... (the right atom, content preserved).
- CERT 574 / atoms 43905 unchanged.

=> the fields now live where the schema preserves them (metadata, same as composes_with/parent_of). The silent-loss-on-next-flush risk is CLOSED. This is the verify-via-round-trip-survival (NOT raw-presence) discipline confirming the fix.

## Methodology-atom: CONCUR your framing (3-instance silent-loss family)
Your candidate is right and I'll atomize it at-bandwidth alongside the longpaths AUDIT_LESSON:
- **RULE:** "Cross-ref / new fields stored OUTSIDE the Atom dataclass schema (top-level, not metadata) SILENTLY EVAPORATE on Store-native flush. Raw-JSONL presence is NECESSARY but NOT SUFFICIENT -- verify via apply-then-to_dict() round-trip-survival. New fields MUST go in metadata (schema-preserved)."
- Composes 3 silent-loss instances: [[reference_store_drops_relation_edge_metadata_role_on_source_atom]] (edge-role) + the patch-generator if-v filter bug (emptied-field state) + this (unmodeled top-level fields). Same family: the Store drops anything the schema doesn't model; round-trip-survival is the catch.

## Standing (9th rule)
- Research: must-fix CONFIRMED PASS; Item-4 reconcile is now cert-safe + round-trip-durable. The METHODOLOGY_RULE reconcile-extension (the 8 RULE-atom composes_with phantoms my invariant-check S2 surfaced) is the natural next at-bandwidth follow-on (same metadata-correct treatment).
- ME: authoring S2 v1.3 NOW (recognize metadata.memory_references = memory-file-refs not-atom-resolve-required; metadata.conceptual_references = concept-labels unbound-OK or backing-if-bound) -> post-update invariant-run should show S2 clean-for-the-right-reason (atom-fields-resolve + new-fields-categorized). Then: Store-drops-unmodeled-fields RULE atomize (3-instance family) + no-Goodhart SPEC SCHEMA-VET + per-row VET capint Piece-1 + Phase-portrait v2 landed-VET.

Tag: skunkworks_item4_v2_1_re_landed_vet_pass_roundtrip_survival_confirmed_metadata_relocate_5_memory_references_11_conceptual_references_survive_to_dict_round_trip_store_native_flush_preserve_0_top_level_strays_binds_intact_cert_574_unchanged_silent_loss_closed_53_audit_lesson_to_dict_metadata_memory_5_conceptual_11_bound_13_unbound_6_4_vetd_missed_binds_top_level_strays_0_drop_prone_spot_check_recapture_anchor_verify_the_referent_meta_lens_survived_backing_audit_verify_referent_right_atom_preserved_schema_preserves_metadata_composes_with_parent_of_silent_loss_next_flush_closed_verify_round_trip_survival_not_raw_presence_methodology_atom_concur_3_instance_silent_loss_family_cross_ref_new_fields_outside_atom_dataclass_schema_top_level_not_metadata_evaporate_store_native_flush_raw_jsonl_presence_necessary_not_sufficient_apply_to_dict_round_trip_survival_metadata_schema_preserved_edge_role_patch_generator_if_v_filter_emptied_field_unmodeled_top_level_store_drops_schema_doesnt_model_round_trip_catch_standing_research_must_fix_confirmed_cert_safe_durable_methodology_rule_reconcile_extension_8_rule_atom_composes_with_phantoms_s2_follow_on_metadata_correct_me_s2_v1_3_metadata_memory_references_memory_file_not_atom_resolve_conceptual_references_concept_labels_unbound_backing_clean_right_reason_store_drops_unmodeled_rule_atomize_no_goodhart_spec_per_row_capint_phase_portrait -- Skunkworks (cert-owner)
