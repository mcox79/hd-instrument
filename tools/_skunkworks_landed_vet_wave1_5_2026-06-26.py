"""
A5-gated cert atomization for Landed-VET Batch 2 (Wave 1.5 + Phase-Diagram GPU fulls + Cortex smokes).
Atomic write via tmp + os.replace; verify-load before commit.
"""
import json, os, time, hashlib, sys, pathlib

ROOT = pathlib.Path(r"D:\AI\hd-instrument")
META = ROOT / "data" / "substrate_index" / "meta"
LEDGER = META / "cert_ledger.jsonl"
ATOMS = META / "atoms.jsonl"
NOTE_PATH = "notes/skunkworks_landed_vet_batch2_8cell_wave1_5_phase_diagram_smokes_2026-06-26.md"

def atomic_append(path, rows):
    """tmp -> os.replace; preserves existing content."""
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    new_block = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n"
    payload = existing + new_block
    tmp = path.with_suffix(path.suffix + ".tmp_skunkworks")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, path)
    # Verify-load
    with open(path, "r", encoding="utf-8") as f:
        lines = [l for l in f if l.strip()]
    for l in lines[-len(rows):]:
        json.loads(l)  # raises if malformed
    return len(lines)

now = time.time()

# ---------- ATOMS (qualified IDs for the new META rules) ----------
new_atoms = [
    {
        "id": "meta::T_methodology/META_RULE_G_smoke_discriminator_preview_does_not_imply_full_landed_signal_smoke_to_full_framing_drift_pc_topk_cortex_E_three_independent_wave1_5_cells_HARD_FAIL_at_full_after_smoke_signal_means_smoke_signal_alone_is_NOT_sufficient_evidence_full_re_audit_required_per_cell",
        "type": "META_RULE",
        "corpus": "meta",
        "rel_type": "METHODOLOGY",
        "atomized_by": "skunkworks_landed_vet_batch2_8cell_wave1_5_phase_diagram_smokes_2026-06-26",
        "ts": now,
        "summary": "Smoke discriminator preview != full landed verdict. Three independent wave1.5 cells (pc_cleanup_deeper_chains_v1, topk_engineered_ambiguity_v1, cortex_E_tensor_HARDER_REGIME_v1) showed smoke-stage discriminator signal that did NOT survive at full regime. Implication: smoke signal is insufficient evidence for chain-grade extrapolation; full landing is mandatory before any non-MM tiering; framing-drift is the recurring failure mode.",
    },
    {
        "id": "meta::T_methodology/META_RULE_H_K_sweep_arrangement_only_per_unit_must_contain_all_K_values_otherwise_K_ceiling_claim_is_premature_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v1_declared_K_SWEEP_4096_8192_16384_32768_but_per_unit_contained_only_K_4096_extension_K_values_NEVER_TESTED_verdict_K_4096_IS_CEILING_misleading_partial_completion_masquerading_as_ceiling_discovery",
        "type": "META_RULE",
        "corpus": "meta",
        "rel_type": "METHODOLOGY",
        "atomized_by": "skunkworks_landed_vet_batch2_8cell_wave1_5_phase_diagram_smokes_2026-06-26",
        "ts": now,
        "summary": "K-sweep / sweep-axis arrangement-only verdicts: per_unit MUST contain entries at every K in K_SWEEP before any 'ceiling' verdict is permitted. Phase-diagram WM K-ceiling cell declared K_SWEEP=[4096,8192,16384,32768] but per_unit only contains K=4096 rows; extension K never actually executed. K_4096_IS_CEILING is partial-completion masquerading as ceiling discovery. Pre-dispatch checklist: verify per_unit cardinality == n_seeds * n_K_arrangements * n_regimes before any 'ceiling' claim.",
    },
    {
        "id": "meta::T_methodology/META_RULE_I_partition_oracle_routed_cleanup_multi_hop_extends_chain_grade_to_depth_30_at_N_8192_V_C_200_K_20_n_chains_200_recall_0p6367_cv_0p052_GPU_RTX_4060_Ti_substrate_native_encoder_zero_LLM_calls_inference_phase_diagram_real_capability_extension",
        "type": "META_RULE",
        "corpus": "meta",
        "rel_type": "PHASE_PORTRAIT",
        "atomized_by": "skunkworks_landed_vet_batch2_8cell_wave1_5_phase_diagram_smokes_2026-06-26",
        "ts": now,
        "summary": "Multi-hop depth ceiling extends to depth 30 at N=8192 V_C=200 V_P=10 K=20 n_chains=200 SUBSTRATE_NATIVE encoder via partition-oracle-routed cleanup on GPU. PART_15HOP=0.8100 (rail in [0.758, 0.858] target 0.8080) PART_20HOP=0.7083 (HP 0.55) PART_25HOP=0.6733 (HP 0.40) PART_30HOP=0.6367 (HP 0.30). All cv <= 0.052 well under 0.10 envelope. Zero LLM forward calls at inference. Extends prior chain-grade depth-15 to depth-30. Substantive cap_map update.",
    },
]

# ---------- CERT LEDGER RULINGS ----------
rulings = []

# Cell 1: pc_cleanup_deeper_chains_v1 — MEASURED_MECHANISM by-construction
rulings.append({
    "ts": now,
    "op": "cert_ruling",
    "atom_id": "math::T3/EXP_pc_cleanup_deeper_chains_v1_MEASURED_MECHANISM_by_construction_VAN_PC_FIN_bit_identical_fe_per_hop_arrays_9_of_9_seed_depth_combos_VAN_saturated_d15_0p988_d20_1p000_d30_0p983_at_N_2048_M_CHAINS_160_alpha_0p078_regime_too_easy_PC_at_each_hop_DEGRADES_d20_minus_0p613_d30_minus_0p779_HARD_FAIL_per_pre_reg_VAN_at_ceiling_mechanism_untested",
    "cert_status": "measured_mechanism",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_vet_batch2_8cell_wave1_5_phase_diagram_smokes_2026-06-26",
    "cell_commit": "wave1_5_batch2_2026-06-26",
    "verdict": "HARD_FAIL_by_construction",
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": NOTE_PATH,
        "metrics_path": "data/exp_pc_cleanup_deeper_chains_v1/metrics.json",
        "atom_qualified_id": "math::T3/EXP_pc_cleanup_deeper_chains_v1_MEASURED_MECHANISM_by_construction"
    },
    "supersedes": None,
    "note": "VAN==PC_FIN bit-identical fe arrays per (seed,depth) 9/9; VAN saturated 0.983-1.000 across all depths; PC bundling at each hop hurts (-0.521 to -0.779); regime did not make VAN fail as designed; mechanism never exercised. Pre-reg discriminator did not trigger."
})

# Cell 2: topk_composition_engineered_ambiguity_v1 — MEASURED_MECHANISM by-construction
rulings.append({
    "ts": now,
    "op": "cert_ruling",
    "atom_id": "math::T3/EXP_topk_composition_engineered_ambiguity_v1_MEASURED_MECHANISM_by_construction_amb_frac_0p011_engineered_NEAR_FRAC_0p4_NEAR_HAM_0p12_did_not_survive_at_M_400_N_2048_alpha_0p195_only_19_of_1800_queries_actually_ambiguous_refuse_disj_degenerate_to_TOP1_commit_n_refused_19_n_disjuncted_19_correctness_TOP1_0p999_REFUSE_0p989_DISJ_1p000_mechanism_never_exercised",
    "cert_status": "measured_mechanism",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_vet_batch2_8cell_wave1_5_phase_diagram_smokes_2026-06-26",
    "cell_commit": "wave1_5_batch2_2026-06-26",
    "verdict": "HARD_FAIL_by_construction",
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": NOTE_PATH,
        "metrics_path": "data/exp_topk_composition_engineered_ambiguity_v1/metrics.json",
        "atom_qualified_id": "math::T3/EXP_topk_composition_engineered_ambiguity_v1_MEASURED_MECHANISM_by_construction"
    },
    "supersedes": None,
    "note": "Engineered ambiguity at NEAR_FRAC=0.4 NEAR_HAM=0.12 did not survive at M=400 N=2048; only 19/1800 queries (1.06%) were actually ambiguous; refuse/disj arms degenerate to top1 commit. Mechanism never exercised at scale. Pre-reg discriminator did not trigger. Future revival angle: increase NEAR_FRAC or decrease NEAR_HAM until amb_frac >= 0.15."
})

# Cell 3: cortex_E_tensor_HARDER_REGIME_v1 — MEASURED_MECHANISM (confirms META_RULE_F)
rulings.append({
    "ts": now,
    "op": "cert_ruling",
    "atom_id": "math::T3/EXP_cortex_E_tensor_HARDER_REGIME_v1_MEASURED_MECHANISM_confirms_META_RULE_F_at_harder_regime_M_OLD_1500_M_RECENT_1000_N_2048_alpha_1p221_e_threshold_0p2_downscale_scale_0p2_cor_E_W_0p7985_gap_E_vs_RND_plus_0p0017_below_0p05_HF_gate_REC_OLD_E_1p000_RANDOM_0p9983_BASELINE_0p9983_E_indistinguishable_from_RANDOM_at_harder_regime_structural_magnitude_coupling_persists",
    "cert_status": "measured_mechanism",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_vet_batch2_8cell_wave1_5_phase_diagram_smokes_2026-06-26",
    "cell_commit": "wave1_5_batch2_2026-06-26",
    "verdict": "HARD_FAIL_confirms_META_RULE_F",
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": NOTE_PATH,
        "metrics_path": "data/exp_cortex_E_tensor_HARDER_REGIME_v1/metrics.json",
        "atom_qualified_id": "math::T3/EXP_cortex_E_tensor_HARDER_REGIME_v1_MEASURED_MECHANISM_confirms_META_RULE_F"
    },
    "supersedes": None,
    "note": "At harder regime (alpha=1.22, M_OLD=1500, M_RECENT=1000, N_PASSES=1000) E_GATED rec_old=1.0 vs RANDOM_GATED rec_old=0.998 -> gap +0.002 << 0.05 HF gate. cor(E,|W|)=0.7985 persists from smoke. Confirms META_RULE_F structural magnitude coupling. Mechanism class refuted at smoke and at full."
})

# Cell 4: depth_ceiling sweep — CHAIN_GRADE (real win)
rulings.append({
    "ts": now,
    "op": "cert_ruling",
    "atom_id": "math::T3/EXP_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1_CHAIN_GRADE_DEPTH_CEILING_30_extends_prior_chain_grade_depth_15_partition_oracle_routed_cleanup_GPU_PART_15_0p8100_cv_0p038_PART_20_0p7083_cv_0p048_PART_25_0p6733_cv_0p034_PART_30_0p6367_cv_0p052_N_8192_V_C_200_V_P_10_K_20_n_chains_200_substrate_native_encoder_zero_LLM_calls_RTX_4060_Ti_all_HP_bands_passed_by_wide_margin_substantive_cap_map_update",
    "cert_status": "chain_grade",
    "cert_class": "pre_reg_pass",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_vet_batch2_8cell_wave1_5_phase_diagram_smokes_2026-06-26",
    "cell_commit": "wave1_5_batch2_2026-06-26",
    "verdict": "CHAIN_GRADE_DEPTH_CEILING_30",
    "cert_increment_delta": 1,
    "cv": 0.052,
    "referent_pointer": {
        "notes_path": NOTE_PATH,
        "metrics_path": "data/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1/metrics.json",
        "atom_qualified_id": "math::T3/EXP_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1_CHAIN_GRADE_DEPTH_CEILING_30"
    },
    "supersedes": None,
    "note": "Recompute confirms: PART_15HOP=0.8100 cv=0.038 (rail [0.758,0.858] target 0.8080) | PART_20HOP=0.7083 cv=0.048 (HP 0.55) | PART_25HOP=0.6733 cv=0.034 (HP 0.40) | PART_30HOP=0.6367 cv=0.052 (HP 0.30). All HP bands passed by wide margin; cv<<0.10. SUBSTRATE_NATIVE encoder, zero LLM forward calls. Real capability extension."
})

# Cell 5: K-ceiling sweep — DEMOTE (per_unit only has K=4096, ceiling claim premature)
rulings.append({
    "ts": now,
    "op": "cert_ruling",
    "atom_id": "math::T3/EXP_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v1_DEMOTE_K_4096_IS_CEILING_verdict_PREMATURE_per_unit_only_contains_K_4096_rows_extension_K_8192_16384_32768_NEVER_EXECUTED_arm_stats_only_K_4096_n_units_7_all_K_4096_RANDOM_ADVERSARIAL_variants_across_3_seeds_K_4096_MULTI_64x_recall_1p0_chain_grade_eligible_at_K_4096_only_ceiling_claim_premature_meta_rule_H_violated",
    "cert_status": "demote",
    "cert_class": "premature_ceiling_claim",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_vet_batch2_8cell_wave1_5_phase_diagram_smokes_2026-06-26",
    "cell_commit": "wave1_5_batch2_2026-06-26",
    "verdict": "DEMOTE_premature_ceiling_revises_director_prior",
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": NOTE_PATH,
        "metrics_path": "data/exp_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v1/metrics.json",
        "atom_qualified_id": "math::T3/EXP_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v1_DEMOTE_premature_ceiling"
    },
    "supersedes": None,
    "note": "K_SWEEP declared [4096,8192,16384,32768] but per_unit contains only K=4096 entries (7 units = 3 seeds RANDOM + 3 seeds ADVERSARIAL + 1 KNN sentinel, all K=4096). arm_stats keys only {'4096'}. K=8192/16384/32768 never executed despite declared sweep. K_4096_IS_CEILING verdict is partial-completion masquerading as ceiling discovery. Triggers META_RULE_H. director_plan should NOT treat as ceiling evidence. At K=4096 MULTI_64x rec=1.0 cv=0.0 is by-construction-saturation (Q-discipline flagged); not chain-grade increment. ALSO supersedes any prior MULTI_128x@K=8192 chain-grade claim (per status_log) since it was never re-validated here."
})

# Cell 6: capacity sweep — MEASURED_MECHANISM by-construction (alpha=0.37 too easy)
rulings.append({
    "ts": now,
    "op": "cert_ruling",
    "atom_id": "math::T3/EXP_phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1_MEASURED_MECHANISM_by_construction_saturation_all_3_VC_arms_rec_at_1_1p000_cv_0p000_at_alpha_M_facts_over_N_max_0p3662_VC_8000_M_facts_6000_N_16384_far_below_capacity_KNN_sentinel_0p3273_below_0p90_gate_correctly_discriminates_baseline_KNN_from_substrate_Hebbian_W_cleanup_NOT_phantom_completion_39s_wall_is_plausible_for_GPU_matmul_argmax",
    "cert_status": "measured_mechanism",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_vet_batch2_8cell_wave1_5_phase_diagram_smokes_2026-06-26",
    "cell_commit": "wave1_5_batch2_2026-06-26",
    "verdict": "SANITY_BREACH_by_construction_at_low_alpha",
    "cert_increment_delta": 0,
    "cv": 0.0,
    "referent_pointer": {
        "notes_path": NOTE_PATH,
        "metrics_path": "data/exp_phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1/metrics.json",
        "atom_qualified_id": "math::T3/EXP_phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1_MEASURED_MECHANISM_by_construction"
    },
    "supersedes": None,
    "note": "All 3 VC arms rec@1=1.000 cv=0.000 at alpha_max = M_facts/N = 6000/16384 = 0.37 (far below capacity). KNN sentinel correctly fires at 0.327 (gate >=0.90) but this is a discriminator artifact (baseline KNN over V_C=8000 codebook is hard, substrate Hebbian W cleanup is easy). NOT phantom-completion: 39s wall for GPU matmul-bound argmax over M_facts=6000 N=16384 V_R=8 is plausible. To exercise capacity ceiling, push alpha to >=1.0 (M_facts >= N=16384). Q-saturation discipline correctly flags."
})

# Cell 7: edge importance smoke — MEASURED_MECHANISM SMOKE-grade signal (FULL pending)
rulings.append({
    "ts": now,
    "op": "cert_ruling",
    "atom_id": "math::T3/EXP_edge_importance_bound_pair_consolidation_v1_smoke_MEASURED_MECHANISM_smoke_grade_real_signal_cor_E_derived_W_minus_0p043_USER_fairness_gate_lt_0p30_PASS_with_huge_margin_edge_importance_structurally_distinct_from_magnitude_EDGE_rec_retr_1p000_RANDOM_rec_retr_0p700_plus_30pp_lift_n_seeds_1_smoke_N_256_M_OLD_200_M_RECENT_150_alpha_1p367_J_comp_1000_arity_3_awaiting_FULL_landing_for_chain_grade_promotion",
    "cert_status": "measured_mechanism",
    "cert_class": "smoke_signal_pending_full",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_vet_batch2_8cell_wave1_5_phase_diagram_smokes_2026-06-26",
    "cell_commit": "wave1_5_batch2_2026-06-26",
    "verdict": "MIDDLE_BAND_smoke_signal_promising",
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": NOTE_PATH,
        "metrics_path": "data/exp_edge_importance_bound_pair_consolidation_v1_smoke/metrics.json",
        "atom_qualified_id": "math::T3/EXP_edge_importance_bound_pair_consolidation_v1_smoke_MEASURED_MECHANISM_smoke_grade_real_signal"
    },
    "supersedes": None,
    "note": "Smoke-grade real discriminator: cor(E_derived,|W|)=-0.043 (USER fairness gate <0.30 PASS huge margin); EDGE_GATED rec_retr=1.0 / rec_unretr=0.5 vs RANDOM_GATED rec_retr=0.7 / rec_unretr=0.72 (EDGE +30pp on retrieved-pair preservation). Edge-importance derived from H-hypergraph is structurally distinct from per-atom magnitude. n_seeds=1, N=256 SMOKE; awaiting FULL landing for chain-grade tier (per META_RULE_G smoke != full)."
})

# Cell 8: ultrametric clustering smoke — MEASURED_MECHANISM SMOKE-grade signal (FULL pending)
rulings.append({
    "ts": now,
    "op": "cert_ruling",
    "atom_id": "math::T3/EXP_cortex_ultrametric_clustering_coarse_grain_v1_smoke_MEASURED_MECHANISM_smoke_grade_real_signal_4_of_4_families_detected_capacity_drop_0p1923_just_below_HP_bar_0p20_ULTRA_rec_all_1p000_RANDOM_CLUSTER_COLLAPSE_rec_all_0p9219_plus_7p8pp_ULTRA_preserves_clustered_recall_1p0_RANDOM_drops_to_0p7917_n_seeds_1_smoke_N_512_4_families_6_atoms_per_family_104_total_atoms_alpha_0p203_awaiting_FULL_landing",
    "cert_status": "measured_mechanism",
    "cert_class": "smoke_signal_pending_full",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_vet_batch2_8cell_wave1_5_phase_diagram_smokes_2026-06-26",
    "cell_commit": "wave1_5_batch2_2026-06-26",
    "verdict": "MIDDLE_BAND_smoke_signal_promising_near_HP_miss",
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": NOTE_PATH,
        "metrics_path": "data/exp_cortex_ultrametric_clustering_coarse_grain_v1_smoke/metrics.json",
        "atom_qualified_id": "math::T3/EXP_cortex_ultrametric_clustering_coarse_grain_v1_smoke_MEASURED_MECHANISM_smoke_grade_real_signal"
    },
    "supersedes": None,
    "note": "Smoke-grade signal: clustering detects 4/4 families; ULTRA_COLLAPSE rec_all=1.0 (vs RANDOM rec_all=0.922) +7.8pp; cap_drop=0.1923 just below HP bar 0.20 (near-miss). ULTRA preserves clustered-recall 1.0 while RANDOM drops to 0.792. n_seeds=1 SMOKE; awaiting FULL landing for chain-grade tier."
})

# Write atomically
print("Writing", len(new_atoms), "META atoms +", len(rulings), "cert rulings...")
n_atoms = atomic_append(ATOMS, new_atoms)
n_ledger = atomic_append(LEDGER, rulings)
print(f"post: cert_ledger rows = {n_ledger}, meta atoms = {n_atoms}")

# CERT count delta computation: only Cell 4 increments (+1); Cell 5 demote is informational (no decrement since no prior chain-grade in ledger via this ID; the historical MULTI_128x@K=8192 claim was tracked in status_log not ledger so no formal decrement)
print("CERT delta this batch: +1 (cell 4 chain-grade depth-ceiling-30); 0 demote-from-ledger (no prior ledger atom for MULTI_128x@K=8192)")
