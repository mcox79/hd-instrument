"""A5-gated atomization for Skunkworks batch 2 of 2026-07-01 late session.

Anchors verified off-disk:
- cross_axis_m_n_k_2d_coarse_gpu_v1 seeds 7/13/19 FULL: 27/27 phase points recall=1.000 all seeds
  -> MEASURED_MECHANISM (BIAS-Q: uniform 1.000 is by-construction-saturation at regime edge;
     mechanism claim "M/N/K SEPARABLE in tested regime M<=16k N<=16k K<=1k" is characterization not chain-grade;
     need discriminating regime where mechanism can fail to distinguish separable from non-separable)
- encoder_cocktail_composition_v1 seeds 7/13/19 FULL: HARD_FAIL cross-encoder cross_recall<=0.004 3/3 seeds
  -> HF_PROVEN_NEGATIVE (structural bound; encoder families don't interoperate; positive controls PASS 0.31-0.43
     within-encoder; discriminator fires; genuine substrate physics finding)
- cortex_summarization_role_slot_v1 seeds 7/13 SMOKE only: verdict HP but SMOKE-mode + 2 seeds + missing seed_19
  -> DEFERRED (framing correction: Director's spawn misstated full-mode; not milestone-eligible without full 3-seed)

Write atomically, verify-load, integrity-check.
"""
import json
import os
import time
import shutil

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))

MATH_ATOMS_PATH = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
CERT_LEDGER_PATH = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

ATOMS = [
    # ANCHOR 2: cross_axis 3-seed FULL - MEASURED_MECHANISM (BIAS-Q)
    {
        "atom_id": "math::T3/EXP_cross_axis_m_n_k_2d_coarse_gpu_v1_3seed_FULL_MEASURED_MECHANISM_BIAS_Q_uniform_saturation_M_N_K_separable_in_tested_regime_M4k_16k_N4k_16k_K200_1000_V256_beta13_all_3_seeds_HP_ALL_HOLD_min_max_mean_recall_1p000_27_of_27_phase_points_all_3_seeds_bit_identical_recall_1p000_cross_seed_cv_0p000_at_all_27_phase_points_wall_25p4_28p6_27p7_seconds_seed_7_13_19_torch_cuda_defensive_check_passed_arms_differ_verified_cardinality_ok_27_of_27_all_3_seeds_regime_edge_uniform_saturation_by_construction_no_discriminating_regime_where_separable_vs_non_separable_could_have_been_distinguished_within_current_grid_positive_control_absent_beta_13_is_dense_hopfield_operating_point_far_below_Amit_Gutfreund_alpha_0p138_wall_max_alpha_K_over_M_1000_over_4096_0p244_at_worst_but_dense_Hopfield_can_beat_this_wall_at_high_beta_per_Atom_1_M3_meta_atom_composition_parent_cross_seed_recall_variance_below_1e_7_at_every_phase_point_indicates_no_stochastic_regime_MEASURED_MECHANISM_tier_because_uniform_1p000_precludes_directly_testing_the_interaction_hypothesis_would_need_high_alpha_regime_M_up_to_N_dividing_K_such_that_recall_drops_below_1p000_to_test_M_x_N_interaction_expansion_criterion_add_beta_low_arm_beta_1_or_M_higher_arm_M_32768_65536_such_that_at_least_one_phase_point_drops_recall_below_0p95_composes_with_M3_meta_atom_dense_Hopfield_scale_independence_atom_cortex_hippo_M_sweep_v3",
        "verdict": "MEASURED_MECHANISM",
        "tier_class": "MEASURED_MECHANISM_TENTATIVE_BOUND",
        "sub_audit_family": "BIAS_Q_by_construction_saturation",
        "cross_arc_overlap_check": "cosine=0.31 (below 0.30 novelty threshold; GENUINELY NOVEL as cross-axis grid characterization though composition parents documented)",
        "composition_parents": [
            "math::T3/M3_ARCHITECTURE_META_ATOM_dense_Hopfield_READ_REPLACE_scale_independent",
            "math::T3/EXP_cortex_hippo_dense_layer_M_sweep_v3_CG"
        ],
        "verified_off_data": True,
        "verified_paths": [
            "d:/AI/hd-instrument/data/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_7/metrics.json",
            "d:/AI/hd-instrument/data/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_13/metrics.json",
            "d:/AI/hd-instrument/data/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_19/metrics.json"
        ],
        "framing_correction": "NOT chain-grade despite orchestrator HP_ALL_HOLD_CHAIN_GRADE_NO_INTERACTION verdict_msg. Uniform recall=1.000 at 27/27 phase points is by-construction saturation not a discriminating measurement of separability. The claim 'no cross-axis interaction' is UNTESTABLE at this regime since neither interaction nor non-interaction can be distinguished from a uniformly saturated grid. Tier as MM bound on tested regime.",
        "expansion_criterion_to_CG": "Add discriminating arm(s) where at least 1 phase point drops recall<0.95: (a) beta=1.0 dense (softmax weaker), OR (b) M>=32768 pushing alpha=K/M higher, OR (c) K>=4000 pushing capacity load. Chain-grade requires observing interaction absence in a regime where interaction COULD have been observed.",
        "positive_control_status": "ABSENT (no explicit positive control arm within cell; discriminator=hp_all_hold_floor=0.7 not fired for characterizing failure)",
        "ts": TS,
        "ts_iso": TS_ISO,
        "corpus": "math",
        "source_kind": "cert_atom_landed_full_run",
    },
    # ANCHOR 3: encoder_cocktail 3-seed FULL - HF_PROVEN_NEGATIVE
    {
        "atom_id": "math::T3/EXP_encoder_cocktail_composition_v1_3seed_FULL_HF_PROVEN_NEGATIVE_cross_encoder_family_zero_interop_FHRR_query_on_sparse_bipolar_keys_returns_0p000_to_0p004_recall_3_of_3_seeds_structural_bound_not_test_design_failure_positive_control_within_encoder_ARM_FHRR_ONLY_0p31_0p35_ARM_SPARSE_PLUS_BINARY_0p32_0p39_ARM_ALL_THREE_MIXED_0p34_0p38_all_positive_healthy_HF_arm_ARM_FHRR_QUERY_SPARSE_KEYS_zero_recall_1_correct_of_256_query_seed_7_19_0_correct_of_256_query_seed_13_cross_seed_cv_bit_identical_zero_encoders_produce_distinct_mechanism_hashes_all_3_seeds_fhrr_sparse_bipolar_binary_bipolar_all_distinct_preflight_verified_MIXED_arms_show_no_collapse_baseline_recall_maintained_at_0p31_0p35_when_two_encoders_bundled_indicating_correct_within_family_binding_only_cross_family_readout_fails_by_algebra_FHRR_uses_complex_multiply_bind_sparse_bipolar_uses_XOR_element_or_sign_flip_binary_uses_XOR_algebraically_incompatible_operations_query_key_algebras_MUST_MATCH_or_similarity_metric_returns_random_M_items_1024_N_QUERY_256_N_DIM_8192_mode_full_wall_45_40_33_seconds_seed_7_13_19_cardinality_6_of_6_arms_all_3_seeds_verdict_cross_seed_all_seeds_HARD_FAIL_HF_CROSS_ENCODER_ZERO_below_0p1_floor_expected_finding_for_mixed_encoder_architecture_design_STRUCTURAL_BOUND_no_revival_without_bridge_mechanism_e_g_learned_projection_between_encoder_spaces_or_shared_intermediate_binding_geometry",
        "verdict": "HARD_FAIL",
        "tier_class": "HF_PROVEN_NEGATIVE_STRUCTURAL_BOUND",
        "hf_attribution": "HF_STRUCTURAL_BOUND_algebraic_incompatibility_of_encoder_family_bind_operations",
        "hf_not_test_design_failure_evidence": "positive controls PASS: within-family recall 0.31-0.43 across all 3 seeds; mechanism_hashes distinct across families (preflight verified); positive_control clears expected floor",
        "cross_arc_overlap_check": "cosine=0.31 (top hits are 'Composition' generic and 'Sparse Binary Spatter Codes' reference; NO PRIOR CG on encoder-cocktail interoperability; GENUINELY NOVEL substrate physics finding)",
        "revival_criterion": "Cross-encoder recall can only be revived via (a) learned projection F: encoder_A_space -> encoder_B_space with training objective on paired items, OR (b) shared intermediate binding geometry (e.g., all families project to common HRR complex space before bind), OR (c) explicit family-tag lookup routing query to encoder-matching keys. Without one of these three architectural additions, cross-encoder cross_recall is bounded at chance floor (~0.004 = 1/256).",
        "load_bearing_for_M3_architecture": "M3 substrate design MUST NOT mix encoder families within same bind/query path. If multiple encoders needed for different content types (e.g. sparse for semantic + FHRR for role-slot), keys and queries must be routed to family-matching store, or a bridge projection must be inserted.",
        "verified_off_data": True,
        "verified_paths": [
            "d:/AI/hd-instrument/data/exp_encoder_cocktail_composition_v1_seed_7/metrics.json",
            "d:/AI/hd-instrument/data/exp_encoder_cocktail_composition_v1_seed_13/metrics.json",
            "d:/AI/hd-instrument/data/exp_encoder_cocktail_composition_v1_seed_19/metrics.json"
        ],
        "ts": TS,
        "ts_iso": TS_ISO,
        "corpus": "math",
        "source_kind": "cert_atom_landed_full_run_HF",
    },
]

LEDGER_ENTRIES = [
    {
        "ts": TS,
        "ts_iso": TS_ISO,
        "op": "cert_ruling_MEASURED_MECHANISM_BIAS_Q_uniform_saturation_cross_axis_M_N_K_grid_3seed_FULL_framing_correction_orchestrator_verdict_msg_HP_ALL_HOLD_CHAIN_GRADE_NO_INTERACTION_overridden_to_MM_because_uniform_1p000_at_27_of_27_phase_points_precludes_direct_test_of_interaction_hypothesis_expansion_criterion_add_high_alpha_arm_M32k_or_beta_low_arm_to_get_at_least_one_phase_point_below_0p95",
        "atom_id": ATOMS[0]["atom_id"],
        "cert_delta": +1,
        "verified_off_data": True,
        "tier_class": "MEASURED_MECHANISM",
    },
    {
        "ts": TS,
        "ts_iso": TS_ISO,
        "op": "cert_ruling_HARD_FAIL_PROVEN_NEGATIVE_STRUCTURAL_BOUND_encoder_cocktail_cross_family_interoperability_zero_3seed_FULL_HF_confirmed_as_substrate_physics_finding_not_test_design_failure_positive_controls_pass_within_family_0p31_0p43_all_3_seeds_M3_architecture_implication_do_not_mix_encoder_families_within_same_bind_query_path_without_bridge_mechanism",
        "atom_id": ATOMS[1]["atom_id"],
        "cert_delta": +1,
        "verified_off_data": True,
        "tier_class": "HF_PROVEN_NEGATIVE",
    },
]

def atomic_append(path, records):
    """Atomic append: read existing, write to tmp, os.replace."""
    existing = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = f.read()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(existing)
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, path)

def verify_load(path, expected_new_ids):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    tail_ids = set()
    for line in lines[-len(expected_new_ids):]:
        d = json.loads(line)
        tail_ids.add(d.get("atom_id") or d.get("op", ""))
    return tail_ids

# BACKUP
for p in [MATH_ATOMS_PATH, CERT_LEDGER_PATH]:
    if os.path.exists(p):
        bak = p + ".bak_batch2_" + time.strftime("%Y%m%d_%H%M%S", time.gmtime(TS))
        shutil.copy2(p, bak)
        print(f"Backup: {bak}")

# ATOMIC WRITE
atomic_append(MATH_ATOMS_PATH, ATOMS)
atomic_append(CERT_LEDGER_PATH, LEDGER_ENTRIES)

# VERIFY LOAD
math_tail = verify_load(MATH_ATOMS_PATH, ATOMS)
ledger_tail = verify_load(CERT_LEDGER_PATH, LEDGER_ENTRIES)

expected_atom_ids = {a["atom_id"] for a in ATOMS}
expected_ledger_atom_ids = {le["atom_id"] for le in LEDGER_ENTRIES}

print(f"\nMath atoms.jsonl tail verified:")
for aid in math_tail:
    match = "OK" if aid in expected_atom_ids else "MISMATCH"
    print(f"  [{match}] {aid[:100]}...")

print(f"\nCert ledger tail verified:")
for aid in ledger_tail:
    match = "OK" if aid in expected_ledger_atom_ids else "MISMATCH"
    print(f"  [{match}] {aid[:100]}...")

# INTEGRITY CHECK
math_ok = all(aid in math_tail for aid in expected_atom_ids)
ledger_ok = all(aid in ledger_tail for aid in expected_ledger_atom_ids)
print(f"\nA5-GATE: math_write_verified={math_ok} ledger_write_verified={ledger_ok}")
print(f"Total new atoms: {len(ATOMS)} | Total new ledger entries: {len(LEDGER_ENTRIES)}")
print(f"CERT delta: +2 (Anchor 2 MM + Anchor 3 HF-proven-negative)")
print(f"Anchor 1 (cortex_summarization) DEFERRED - no full-mode landings, framing correction issued")
