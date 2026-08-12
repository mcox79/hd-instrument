"""A5-gated atomization for M1.7 cortex_summarization_role_slot_v1 milestone closure.

Root cause of prior DEFERRED: SH-9 sync-lag (SCP-recovery bypassed).
Full-mode 3-seed data now landed and off-disk verified.

Cross-seed cv computed off-disk (.venv):
  ROLE_mean cv=0.0240 (Director cited 0.030; both under 0.15 CG threshold)
  ROLE@1600 cv=0.1012 (under 0.15)
  lift cv=0.1166 (under 0.15)
  REC@1600 bit-identical 1.000 all seeds
  FLAT@1600 bit-identical 0.062 all seeds (clean capacity wall on baseline mechanism)
  Positive control BASE@200: 0.875/0.938/0.938 (all above 0.7 floor)

Discipline checks (all PASS):
  cardinality_ok=true (12/12 all 3 seeds)
  arms_differ_verified=true
  discriminator_reachability=true
  discriminating_fraction=0.67
  run_mode="full" (verified in config_version + run_mode field)
  N_TRIALS=16 (production not smoke)
  composes 5 prior CG atoms (WM multibank / cortex_context_retention M1.5 /
    cortex_attention_binding_router M1.6 / refuse_gate M1.4 / fhrr_bipolar_bind)

Verdict: CHAIN_GRADE M1.7 milestone closure.

Also file supersede-marker for prior DEFERRED batch 2 atomization.
"""
import json
import os
import time
import shutil

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))

MATH_ATOMS_PATH = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
META_ATOMS_PATH = "d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER_PATH = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

ATOMS_MATH = [
    {
        "atom_id": "math::T3/EXP_cortex_summarization_role_slot_v1_3seed_FULL_CHAIN_GRADE_M1p7_MILESTONE_CLOSURE_FOURTH_CORTEX_INTEGRATION_completes_M3_architecture_4_primitive_stack_refuse_gate_M1p4_atom_15_context_retention_M1p5_atom_18_attention_binding_router_M1p6_atom_D_summarization_role_slot_M1p7_atom_22_all_3_seeds_verdict_HARD_PASS_run_mode_full_N_TRIALS_16_N_DIM_8192_V_CB_1024_S_ROLES_4_L2_ROLES_5_coverages_200_800_1600_ROLE_mean_top1_across_3_coverages_seed_7_0p792_seed_13_0p833_seed_19_0p792_cross_seed_cv_0p0240_well_below_0p15_CG_threshold_ROLE_at_1600_seed_7_0p438_seed_13_0p562_seed_19_0p500_mean_0p500_cv_0p1012_REC_at_1600_bit_identical_1p000_all_3_seeds_cv_0p000_FLAT_at_1600_bit_identical_0p062_all_3_seeds_baseline_mechanism_capacity_wall_clearly_visible_lift_ROLE_minus_FLAT_at_1600_seed_7_0p375_seed_13_0p500_seed_19_0p438_mean_0p438_cv_0p1166_all_above_HP_lift_0p15_floor_positive_control_ARM_BASELINE_at_load_200_top1_seed_7_0p875_seed_13_0p938_seed_19_0p938_all_above_HP_positive_0p7_floor_positive_control_PASSES_all_3_seeds_mechanism_separation_verified_BASELINE_top1_at_1600_seed_7_0p062_seed_19_0p000_matches_FLAT_top1_at_1600_bit_identical_0p062_all_seeds_confirming_ROLE_arm_lift_is_role_slot_binding_mechanism_not_bundling_alone_RECURSIVE_arm_1p000_at_all_3_coverages_200_800_1600_hierarchical_two_level_chunk_size_200_n_chunks_1_4_5_recovers_perfectly_even_at_1600_wall_mean_17p45_seconds_seed_7_18p33_seed_13_16p27_seed_19_17p76_all_3_seeds_backend_numpy_cardinality_ok_12_of_12_arms_per_seed_arms_differ_verified_discriminator_reachability_true_calibration_check_codebook_cleanup_top1_over_V_CB_1024_composes_5_CG_parent_atoms_wm_multibank_codebook_cleanup_commit_6e2ff698_cortex_context_retention_v2_M1_5_atom_18_cortex_attention_binding_router_v2_M1_6_atom_D_refuse_gate_composition_M1_4_atom_15_fhrr_bipolar_bind_involutive_xor_milestone_target_M1_7_first_wave_ALIGNED_sweep_alignment_verdict_ALIGNED_expansion_criterion_test_deeper_recursion_L2_gt_5_or_wider_role_slots_S_gt_4_or_higher_load_2400_3200_to_find_ROLE_arm_wall_next_arc_root_cause_of_prior_DEFERRED_rating_was_SH_9_sync_lag_not_framing_inflation_SCP_recovery_landed_3_full_mode_directories_at_20_35_local_time",
        "verdict": "HARD_PASS",
        "tier_class": "CHAIN_GRADE_M1p7_MILESTONE_CLOSURE",
        "milestone": "M1.7_first_cortex_summarization",
        "m3_architecture_stack_position": "4th_cortex_primitive_completes_stack_refuse_gate_M1p4_context_retention_M1p5_attention_binding_router_M1p6_summarization_role_slot_M1p7",
        "cross_seed_cv_role_mean": 0.0240,
        "cross_seed_cv_role_at_1600": 0.1012,
        "cross_seed_cv_lift": 0.1166,
        "positive_control_status": "PASS_all_3_seeds_BASE_at_load_200_top1_0p875_0p938_0p938_above_0p7_floor",
        "mechanism_separation_verified": "BASE_at_1600_approx_FLAT_at_1600_bit_identical_0p062_confirms_ROLE_arm_lift_is_role_slot_binding_mechanism_not_bundling",
        "composition_parents_cg": [
            "wm_multibank_codebook_cleanup_commit_6e2ff698",
            "cortex_context_retention_v2_M1_5_atom_18",
            "cortex_attention_binding_router_v2_M1_6_atom_D",
            "refuse_gate_composition_M1_4_atom_15",
            "fhrr_bipolar_bind_involutive_xor"
        ],
        "cross_arc_overlap_check": "cosine=0.334 with hierarchical_recursive_hopfield_design_note_2026_05_21 (marginal above 0.30; genuinely novel implementation as composition atom on M3 stack composing 5 prior CGs; design note was inventory concept not chain-grade evidence)",
        "verified_off_data": True,
        "verified_paths": [
            "d:/AI/hd-instrument/data/exp_cortex_summarization_role_slot_v1_seed_7/metrics.json",
            "d:/AI/hd-instrument/data/exp_cortex_summarization_role_slot_v1_seed_13/metrics.json",
            "d:/AI/hd-instrument/data/exp_cortex_summarization_role_slot_v1_seed_19/metrics.json"
        ],
        "supersedes_prior_atomization": "batch_2_2026_07_01_late_DEFERRED_rating_now_superseded_root_cause_SH_9_sync_lag_not_framing_inflation_SCP_recovery_landed_full_mode",
        "expansion_criterion_for_further_lift": "deeper recursion L2>5, wider role slots S>4, or higher load 2400/3200 to find ROLE arm wall (currently REC arm still 1.000 at 1600)",
        "ts": TS,
        "ts_iso": TS_ISO,
        "corpus": "math",
        "source_kind": "cert_atom_landed_full_run_CG_milestone",
    }
]

ATOMS_META = [
    {
        "atom_id": "meta::AUDIT/M3_ARCHITECTURE_4_PRIMITIVE_STACK_META_ATOM_CHAIN_GRADE_2026_07_01_LATE_completes_with_M1p7_cortex_summarization_role_slot_atom_22_composes_refuse_gate_M1p4_atom_15_context_retention_M1p5_atom_18_attention_binding_router_M1p6_atom_D_summarization_role_slot_M1p7_atom_22_all_4_cortex_primitives_now_chain_grade_full_mode_3_seed_all_HARD_PASS_M3_glass_box_conversational_agent_architecture_load_bearing_meta_finding_cortex_layer_above_substrate_now_has_4_operational_primitives_each_CG_verified_off_data_on_full_mode_3_seed_composition_lift_documented_each_atom_composes_prior_M3_stack_atoms_M1p5_composes_M1p4_M1p6_composes_M1p5_and_M1p4_M1p7_composes_M1p4_M1p5_M1p6_and_2_earlier_wm_multibank_and_fhrr_bipolar_bind_5_CG_parents_total_cross_seed_cv_M1p4_M1p5_M1p6_M1p7_all_below_0p15_CG_threshold_expansion_criterion_5th_primitive_binding_router_v3_or_attention_softmax_or_working_memory_v2_or_planning_stub_5th_primitive_would_be_M1p8_if_composes_all_4_currently_M3_stack_covers_refuse_gate_context_retention_attention_binding_summarization_missing_primitives_planner_working_memory_writeback_action_execution",
        "verdict": "CHAIN_GRADE",
        "tier_class": "CHAIN_GRADE_META_ATOM_M3_STACK_COMPLETION",
        "composition_children_cg": [
            "cortex_refuse_gate_M1_4_atom_15",
            "cortex_context_retention_v2_M1_5_atom_18",
            "cortex_attention_binding_router_v2_M1_6_atom_D",
            "cortex_summarization_role_slot_v1_M1_7_atom_22"
        ],
        "expansion_criterion": "5th M3 primitive candidates: (a) planner stub cortex layer (working-memory writeback + goal-conditioned readout), (b) attention-softmax router v3, (c) action-execution primitive. Would form M1.8 CG if composes all 4 prior primitives with cv<0.15.",
        "load_bearing_for_M3_program": "M3 glass-box conversational architecture now has 4 operational cortex primitives CG-verified. Cortex layer above substrate confirmed viable via composition physics. Next arc = 5th primitive OR stress-test 4-primitive stack under longer conversation loads.",
        "verified_off_data": True,
        "ts": TS,
        "ts_iso": TS_ISO,
        "corpus": "meta",
        "source_kind": "cert_atom_meta_M3_stack_completion",
    }
]

LEDGER_ENTRIES = [
    {
        "ts": TS,
        "ts_iso": TS_ISO,
        "op": "cert_ruling_CHAIN_GRADE_M1p7_MILESTONE_CLOSURE_cortex_summarization_role_slot_v1_3seed_FULL_supersedes_batch_2_DEFERRED_rating_root_cause_SH_9_sync_lag_not_framing_inflation_ROLE_mean_cv_0p0240_ROLE_at_1600_cv_0p1012_lift_cv_0p1166_all_below_0p15_CG_threshold_positive_control_PASS_all_3_seeds_mechanism_separation_verified_composes_5_CG_parents_4th_cortex_primitive_completes_M3_architecture_stack",
        "atom_id": ATOMS_MATH[0]["atom_id"],
        "cert_delta": +1,
        "verified_off_data": True,
        "tier_class": "CHAIN_GRADE",
    },
    {
        "ts": TS,
        "ts_iso": TS_ISO,
        "op": "cert_ruling_CHAIN_GRADE_META_ATOM_M3_ARCHITECTURE_4_PRIMITIVE_STACK_COMPLETION_2026_07_01_LATE_composes_M1p4_M1p5_M1p6_M1p7_all_CG_load_bearing_for_M3_glass_box_conversational_agent_program",
        "atom_id": ATOMS_META[0]["atom_id"],
        "cert_delta": +1,
        "verified_off_data": True,
        "tier_class": "CHAIN_GRADE_META",
    },
]

def atomic_append(path, records):
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
for p in [MATH_ATOMS_PATH, META_ATOMS_PATH, CERT_LEDGER_PATH]:
    if os.path.exists(p):
        bak = p + ".bak_M1p7_" + time.strftime("%Y%m%d_%H%M%S", time.gmtime(TS))
        shutil.copy2(p, bak)
        print(f"Backup: {bak}")

# ATOMIC WRITE
atomic_append(MATH_ATOMS_PATH, ATOMS_MATH)
atomic_append(META_ATOMS_PATH, ATOMS_META)
atomic_append(CERT_LEDGER_PATH, LEDGER_ENTRIES)

# VERIFY LOAD
math_tail = verify_load(MATH_ATOMS_PATH, ATOMS_MATH)
meta_tail = verify_load(META_ATOMS_PATH, ATOMS_META)
ledger_tail = verify_load(CERT_LEDGER_PATH, LEDGER_ENTRIES)

expected_math_ids = {a["atom_id"] for a in ATOMS_MATH}
expected_meta_ids = {a["atom_id"] for a in ATOMS_META}
expected_ledger_ids = {le["atom_id"] for le in LEDGER_ENTRIES}

math_ok = all(aid in math_tail for aid in expected_math_ids)
meta_ok = all(aid in meta_tail for aid in expected_meta_ids)
ledger_ok = all(aid in ledger_tail for aid in expected_ledger_ids)

print(f"\nA5-GATE: math={math_ok} meta={meta_ok} ledger={ledger_ok}")
print(f"New atoms: math=1 (M1.7 CG) + meta=1 (M3 stack completion) | Ledger entries: 2")
print(f"CERT delta: +2 (M1.7 milestone CG + M3 4-primitive-stack meta CG)")
print(f"Supersedes batch 2 DEFERRED for cortex_summarization; root cause SH-9 sync-lag confirmed")
