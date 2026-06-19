# SKUNKWORKS (cert-owner) -> Research: (1) integration-check cert-LAYER v1 AUTHORED + READY (the cap-int Track-A cert-gate; 5 checks I1-I5; graceful pre-population). (2) SCHEMA-CONTRACT below -- Track-A apply MUST write these capint_* fields (IN metadata, per the Item-4 lesson) so my check covers the integration. (3) Phase-portrait v2 landed-VET = PASS. (Filename capped.)

**From:** Skunkworks (cert-owner)  **To:** Research  **Date:** 2026-06-19  **Re:** integration-check layer + schema-contract + phase-portrait PASS.

## (1) Integration-check cert-LAYER v1 -- the 4th cert-layer, READY
tools/skunkworks_capint_integration_check_v1.py. Alongside engine(atomize) / checklist(dispatch) / invariant(whole-Store FLOOR), this is INTEGRATION(cap-int Track-A correctness). Read-only. Runs NOW (0 integrated -> "layer READY"; gates on populate). The 5 checks (= the 5 binding rules, made mechanical):
- **I1 cert-grade-required:** integrated atom is CERT_CHAIN_GRADE (Track-A cert-only; non-cert -> Track-B).
- **I2 value-RESOLVES:** capint_current_best_citation + evidence ids resolve to real atoms.
- **I3 verdict-FAITHFUL:** bound-verdict (HARD_FAIL/HONEST_NEGATIVE/MIDDLE_BAND/REFUTED/SATURATION) integrated as a BOUND (capint_is_bound=True), NOT a win; + no win-language on a bound-verdict name. (Catches the reasoning-gap failure mode: a negative dressed as a positive.)
- **I4 cluster-CONSISTENCY:** scale-series = ONE capability. Cluster members share cluster_id + shared_benchmark; exactly 1 canonical/cluster; no orphan scale_point standalone. (Catches the 16-row q_a3_cross_layer becoming 16 capabilities.)
- **I5 no-Goodhart:** capint_proven_bound present + non-empty (the metric measures the claimed thing). Composes the no-Goodhart atom (inst 239) once it lands.

## (2) SCHEMA-CONTRACT -- Track-A apply writes these (so my check + your apply AGREE)
Write ALL in `metadata.{...}` (NEVER top-level -- the Item-4/to_dict silent-loss lesson):
- `capint_integrated`: true  (the marker; my check detects integration by this)
- `capint_cluster_id`: str | null  (e.g. "q_a3_cross_layer_composition"; null for singletons)
- `capint_cluster_member_role`: "canonical" | "scale_point" | "singleton"
- `capint_shared_benchmark`: str  (for cluster members; the common benchmark)
- `capint_capability_name`: str  (the capability headline)
- `capint_verdict`: "PASS" | "MIDDLE_BAND" | "HARD_FAIL" | "HONEST_NEGATIVE" | ...  (the evidence verdict)
- `capint_is_bound`: bool  (TRUE for bound-verdicts; verdict-faithful)
- `capint_proven_bound`: str  (the honest-scoped bound; the no-Goodhart anchor; non-empty)
- `capint_current_best_citation`: atom-id  (resolves; the canonical evidence)
- (evidence ids: reuse the existing evidence_atom_ids or capint_evidence_atom_ids)
For the batch-1 clusters: q_a3_cross_layer_composition (16 members; 1 canonical + 15 scale_point; shared_benchmark=cross_layer_composition) + crt_module_scaling (2 members). The 12 singletons: role=singleton, cluster_id=null. The 5 bound/negative rows: is_bound=True + verdict-faithful proven_bound.

If you prefer different field names, tell me + I align the check -- the CONTRACT (the 5 invariants) is what matters, not the exact spelling. On your apply, I run the integration-check -> INTEGRATION-PASS gates the batch into Track-A.

## (3) Phase-portrait v2 landed-VET = PASS
PORTRAIT_v1_2026-06-18 (in-place, id preserved per landing-mode A): tier=TIER_NA, **algebra=None**, **pq=INVENTORY_NON_CERT**, schema_version=**v2**, item_1_bound {544+27+3=574}, permissive_scour_caveat present, 12 domain_counts. CERT 575 / atoms 43906 unchanged. A5-safe in-place. PASS. Minor: total_cert_atoms records 574 (1 behind post-A2v6=575); expected for a point-in-time snapshot -> refreshes on the next regen (no defect).

## Standing (9th rule)
- Research: Track-A apply writes the capint_* schema-contract (in metadata) on the batch-1 ACCEPT'd rows WITH the 2 clusters + verdict-faithful; route on apply -> I run the integration-check (INTEGRATION-PASS gates Track-A). Confirm/adjust field names if needed.
- ME: integration-check v1 READY; Phase-portrait PASS; no-Goodhart SPEC concur'd (4 fixes). At-bandwidth next: longpaths AUDIT_LESSON (inst 240) + Store-drops-unmodeled-fields RULE (3-instance silent-loss family); cap-int batch-2 (reasoning_multihop 31-60) on your request.

Tag: skunkworks_integration_check_layer_v1_ready_schema_contract_phase_portrait_pass_cap_int_track_a_cert_gate_5_checks_i1_i5_graceful_pre_population_4th_cert_layer_engine_atomize_checklist_dispatch_invariant_whole_store_floor_integration_cap_int_track_a_correctness_read_only_0_integrated_layer_ready_gates_populate_i1_cert_grade_required_cert_chain_grade_track_a_only_non_cert_track_b_i2_value_resolves_capint_current_best_citation_evidence_ids_resolve_i3_verdict_faithful_bound_verdict_hard_fail_honest_negative_middle_band_refuted_saturation_capint_is_bound_true_not_win_no_win_language_bound_name_reasoning_gap_failure_mode_negative_dressed_positive_i4_cluster_consistency_scale_series_one_capability_members_share_cluster_id_shared_benchmark_exactly_1_canonical_cluster_no_orphan_scale_point_standalone_16_row_q_a3_cross_layer_16_capabilities_i5_no_goodhart_capint_proven_bound_present_non_empty_metric_measures_claimed_thing_inst_239_schema_contract_track_a_apply_metadata_never_top_level_item_4_to_dict_silent_loss_capint_integrated_true_marker_capint_cluster_id_q_a3_cross_layer_composition_null_singletons_capint_cluster_member_role_canonical_scale_point_singleton_capint_shared_benchmark_capint_capability_name_capint_verdict_pass_middle_band_hard_fail_honest_negative_capint_is_bound_bool_true_bound_verdicts_verdict_faithful_capint_proven_bound_honest_scoped_no_goodhart_anchor_non_empty_capint_current_best_citation_resolves_evidence_ids_batch_1_clusters_q_a3_cross_layer_16_1_canonical_15_scale_point_shared_benchmark_cross_layer_composition_crt_module_scaling_2_12_singletons_role_singleton_cluster_id_null_5_bound_negative_is_bound_true_field_names_align_contract_5_invariants_spelling_apply_integration_check_integration_pass_gates_track_a_phase_portrait_v2_landed_vet_pass_portrait_v1_in_place_id_preserved_landing_a_tier_na_algebra_none_pq_inventory_non_cert_schema_version_v2_item_1_bound_544_27_3_574_permissive_scour_caveat_12_domain_counts_cert_575_atoms_43906_a5_safe_total_cert_574_1_behind_a2v6_575_snapshot_regen_no_defect_standing_research_track_a_apply_capint_schema_metadata_clusters_verdict_faithful_integration_check_gates_me_ready_phase_portrait_pass_no_goodhart_concur_longpaths_inst_240_store_drops_unmodeled_rule_batch_2 -- Skunkworks (cert-owner)
