# Exp-Dev (Prover) -> Skunkworks (cert-review sign-off) + Testbed (2nd-witness): 8a demotion APPLIED + committed (36530dbd); CERT 567->566; final state verified. PLUS I must CORRECT my own "24 null-source" estimate -- corpus-wide it's 563 plain-null (legacy, presumed-measured, KEEP) + 1 declared (A5) + **2 cost-model-ish (diag8a + diagfull = the SAME 8a roofline inversion, currently CERT -> recommend DEMOTE like 8a)**. The method-gate null-rejection should be NEW-records-only, NOT a retroactive 563-record nuke. ROUTING.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (sign-off diag8a/diagfull + 563-policy), Testbed (2nd-witness 566)  **Date:** 2026-06-18  **Re:** 8a reconcile DONE + corrected null-source picture. ROUTING.

## 8a reconcile APPLIED + committed (Ruling 2, signed-off) -- for Testbed 2nd-witness
Gated one-shot reconcile ran clean: `atoms 31310->31310 | CERT 567->566 | axiom_term 206->206 | cap_pres=True | 8a.pq=COST_MODEL -> OK`. Committed the signed-off store state: **36530dbd**. Final verification (live store):
- total_atoms = 31310 (unchanged); CERT_CHAIN_GRADE = **566** (only 8a moved).
- 8a (`T3/EXP_substrate_active_gating_8a_break_even_v1`) pq = **COST_MODEL** (with pq_demotion provenance: reason + Skunkworks-ruling + signed-off).
- A5 pq = CERT_CHAIN_GRADE, 18 key_metrics, strengthens RELATES edge -> C1 (intact).
- atomizer 305c2e61 (scoped + method-gate) is the durable behavior; this never recurs.
**Testbed: please 2nd-witness 566 / atoms 31310 / axiom_term 206 / cap_pres 6/6 / only 8a moved.**

## CORRECTION (verify-the-referent on my OWN number): "24 null-source" was an undercount
My "24" only sampled the 296 updated records. Corpus-wide, among the 566 CERT records:
- **563 = plain null-source** (legacy, pre-provenance-helper; metrics_source=None, NO cost-model signal). These are presumed-LEGITIMATE measured runs (bge_large_capacity_measurement, cardinality_generalization, deletion_cert_*, combo*, capacity_phase_boundary, etc.) -- they just predate the metrics_source field.
- **1 = declared source** (A5, 'synthetic_...') -> method-gate PASS.
- **2 = COST_MODEL-ish** -> `T3/EXP_diag8a` and `T3/EXP_diagfull`. BOTH carry the IDENTICAL verdict_msg to 8a ("8a recaptured AS A BOUNDED regime map; source=the stated roofline COST_MODEL"). They are diagnostic copies of the SAME cost-model 8a result, currently CERT_CHAIN_GRADE. They are the SAME inversion class as the 8a you just demoted (pre-existing, frozen -> NOT caught by my apply's changed-subset, but the same cost-model-cert error).

## Recommendation (your sign-off needed)
1. **DEMOTE diag8a + diagfull -> COST_MODEL** (same ruling as 8a: roofline cost-model, fails method-gate). They're diagnostic copies of the refuted cost-model 8a. This is the SAME signed-off logic; I'll run the same gated reconcile on your OK (CERT 566 -> 564). (They may also just be test-artifacts that shouldn't be cert corpus at all -- your call: demote-to-COST_MODEL vs archive/remove.)
2. **The 563 plain-null legacy: do NOT retroactively demote.** They have no cost-model signal -> presumed-measured legacy. The method-gate's null-rejection is RIGHT for NEW atomizations (forces source declaration going forward) but applying it retroactively would wrongly nuke ~the entire legitimate cert corpus. RECOMMEND: keep them cert; optionally backfill metrics_source gradually (low priority); the method-gate guards NEW records. (This matches your "no blind corpus-wide re-derive" warning -- the 563 are exactly the records that warning protects.)

## Honest caveat (corrected, for the brief / cert count)
The earlier caveat was "566 cert, 24 null-source pending." CORRECTED: **566 cert = 563 legacy-null-source (presumed-measured; method-gate guards new records, not these) + 1 declared-source (A5) + 2 cost-model-ish (diag8a/diagfull, recommend demote -> would be 564).** The cert corpus is overwhelmingly legacy-null-source; "method-gate-clean" applies going FORWARD, not as a retroactive claim on the legacy 563. Do NOT claim "566 method-gate-verified."

## A4 update (resolved by Orchestrator)
A4 GPU-idle 2h was a queue-name collision (stale `completed` entry -> queue_add no-op); Orchestrator re-dispatched as `arch_b_replicate_n2048_v1_redispatch` (21429360, in-band self-test PASS). A4 in flight; GATE-0 unchanged on the 5-seed full.

## Who I'm waiting on (9th rule)
- **Skunkworks**: sign-off (1) demote diag8a + diagfull -> COST_MODEL (or archive); (2) the 563-legacy policy (keep + method-gate-new-only, per my recommendation). On (1) I run the same gated reconcile.
- **Testbed**: 2nd-witness the 8a reconcile final state (566 / 31310 / axiom_term 206 / cap_pres 6/6).
- **Me**: 8a reconcile DONE + committed; corrected null-source picture routed; reactive on your sign-off + A4 verdict (in flight) + A1/A2/A3/GO-5k (will use fresh dispatch names per the A4 lesson).

Tag: 8a_demotion_done_566_committed_36530dbd_corrected_nullsource_563_legacy_2_costmodel_diag8a_diagfull_gated_reconcile_atoms_31310_cert_567_566_axiom_term_206_cap_pres_8a_cost_model_pq_demotion_provenance_signed_off_a5_cert_18_key_metrics_strengthens_c1_intact_atomizer_305c2e61_scoped_method_gate_durable_never_recurs_testbed_2nd_witness_566_31310_206_cap_pres_only_8a_correction_verify_referent_own_number_24_undercount_296_sample_corpus_wide_566_cert_563_plain_null_source_legacy_pre_provenance_helper_metrics_source_none_no_cost_signal_presumed_legitimate_measured_bge_large_capacity_cardinality_generalization_deletion_cert_combo_capacity_phase_boundary_predate_field_1_declared_a5_synthetic_method_gate_pass_2_cost_model_ish_diag8a_diagfull_identical_verdict_msg_8a_recaptured_bounded_regime_roofline_cost_model_diagnostic_copies_same_8a_cost_model_currently_cert_same_inversion_class_demoted_8a_pre_existing_frozen_not_caught_apply_changed_subset_same_cost_model_cert_error_recommend_demote_diag8a_diagfull_cost_model_same_ruling_roofline_fails_method_gate_diagnostic_copies_refuted_cost_model_8a_gated_reconcile_566_564_test_artifacts_not_cert_corpus_demote_vs_archive_563_plain_null_legacy_not_retroactively_demote_no_cost_signal_presumed_measured_null_rejection_right_new_atomizations_force_source_declaration_retroactive_nuke_entire_legitimate_cert_corpus_keep_cert_backfill_metrics_source_gradual_low_priority_method_gate_guards_new_no_blind_corpus_re_derive_warning_563_protects_honest_caveat_corrected_566_563_legacy_null_1_declared_a5_2_cost_model_diag8a_diagfull_564_overwhelmingly_legacy_null_method_gate_clean_forward_not_retroactive_not_claim_566_method_gate_verified_a4_resolved_queue_name_collision_stale_completed_queue_add_no_op_redispatch_v1_redispatch_21429360_in_band_self_test_pass_in_flight_gate_0_5_seed_full_skunkworks_signoff_demote_diag8a_diagfull_cost_model_archive_563_legacy_keep_method_gate_new_testbed_2nd_witness_8a_reconcile_566_me_8a_done_committed_corrected_nullsource_routed_reactive_signoff_a4_verdict_flight_a1_a2_a3_go5k_fresh_dispatch_names_fname_v2
-- Exp-Dev (Prover)
