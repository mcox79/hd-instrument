"""
A5-gated atomization for Landings A (cortex_attention_binding_router_v1) and B (sparsity_free_axis_v4_pc_only_n4096).
Session 2026-07-01. Skunkworks landed-VET after off-disk recompute.

Landing A: 3-seed FULL, HP_route_accuracy 0.933/0.983/0.917 clears 0.85; HP_lift_over_null clears 0.30;
HP_lift_over_isolated clears 0.15; but HP_per_class_precision BREACHES 0.70 at seed_13 chain_multihop RETRIEVE (0.625).
Pre-reg §MIDDLE_BAND: "HP gates split (e.g., overall accuracy >= 0.85 but per-class precision splits below 0.70 on one)"
=> MEASURED_MECHANISM (proven bound on M1.6 cortex routing).

Landing B: 3-seed FULL, HP_PC_MONOTONE requires rho <= -0.80 at ALL 5 M values × 3 seeds. seed_19 PC_M1000 rho=-0.5
breaches at 1/15 (M,seed) pairs. Numerics cross-seed IDENTICAL (cv < 0.02). Pre-reg strict-reading =>
MEASURED_MECHANISM (proven bound; sparsity lever weakens at M=1000/mid-alpha at some seeds).

Both cells supersede prior single-seed MM atoms Director cited as Atom 23 (cortex router) and Atom 25 (sparsity).
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

TS = time.time()
COMMIT = "ed5153b3"

# ============= LANDING A: cortex_attention_binding_router_v1 =============
atom_A = {
    "id": "math::T3/EXP_cortex_attention_binding_router_v1_3seed_FULL_MEASURED_MECHANISM_M1p6_composition_router_HP_route_accuracy_HP_lift_over_null_HP_lift_over_isolated_all_pass_3_seeds_ROUTE_CONFUSION_MATRIX_top1_dialogue_pronoun_0p933_ood_novel_bind_0p983_chain_multihop_0p917_no_router_baseline_0p250_all_3_regimes_correctly_at_4_class_random_isolated_baseline_0p717_0p683_0p733_composition_lift_over_isolated_0p216_0p300_0p184_all_ge_0p15_HP_PER_CLASS_PRECISION_BREACH_seed_13_chain_multihop_RETRIEVE_class_precision_0p625_below_0p70_gate_pre_reg_MIDDLE_BAND_criterion_HP_gates_split_ROUTE_ACC_clears_but_per_class_splits_MEASURED_bound_M1p6_composition_works_at_aggregate_but_per_class_precision_at_RETRIEVE_class_in_chain_multihop_regime_is_capacity_limited_at_N_test_5_per_class_20_items_total_composes_M1p4_v8_refuse_gate_Atom_15_M1p5_v2_context_retention_Atom_18_WM_multibank_K4096_multihop_partition_oracle_Atom_6_dense_hopfield_Atom_1_supersedes_prior_seed_7_smoke_MM_atom_at_ts_1782935173p99_wall_0p15s_seed_7_0p15s_seed_13_0p25s_seed_19_2026-07-01",
    "name": "EXP cortex_attention_binding_router_v1 3seed FULL MM (M1.6 composition router; 1/9 per-class precision breach)",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": "Experiment record: exp_cortex_attention_binding_router_v1 (M1.6 milestone; wires 5 CG substrate primitives via signal-HV composition classifier). 3 seeds full FULL, verdict per-cell HARD_PASS at gate-level but pre-reg MIDDLE_BAND applies: HP_PER_CLASS_PRECISION gate splits below 0.70 at seed_13 chain_multihop RETRIEVE (0.625, 5/8). ROUTE_CONFUSION_MATRIX top1 cross-seed means: dialogue_pronoun 0.933 cv=0.031; ood_novel_bind 0.983 cv=0.029; chain_multihop 0.917 cv=0.083. NO_ROUTER control identically 0.250 across all seeds (4-class random floor). M14_M15_ISOLATED lift check: composition beats isolated by 0.216/0.300/0.184 (all clear HP_LIFT_OVER_ISOLATED >= 0.15). Suspect-1.000 arms in {REFUSE, BIND} across regimes are pre-reg-legitimated by META_RULE_Q clause on small-item N_test=5 per class. Test cardinality 20 items per arm (small; 0.05 resolution). Cell wall extremely fast (0.15-0.25s per seed) because composition is a bit-op over 5 already-cleared signal HVs. Composes Atoms 15/18/1/6 + WM K=4096. Supersedes prior single-seed MM at ts=1782935173.",
    "aliases": [],
    "metadata": {
        "record_class": "experiment_record",
        "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
        "metric_type": None,
        "experiment_path": "experiments\\exp_cortex_attention_binding_router_v1.py",
        "prereg_path": "preregs\\2026-07-01_cortex_attention_binding_router_v1.md",
        "metrics_paths": [
            "data\\exp_cortex_attention_binding_router_v1_seed_7\\metrics.json",
            "data\\exp_cortex_attention_binding_router_v1_seed_13\\metrics.json",
            "data\\exp_cortex_attention_binding_router_v1_seed_19\\metrics.json"
        ],
        "cell_sha": COMMIT,
        "remote_run_id": None,
        "verdict": "MEASURED_MECHANISM_M1p6_composition_router",
        "run_mode": "full",
        "provenance_quality": "FULL_3_SEEDS_INDEPENDENT_RECOMPUTE",
        "relevance_tier": "HIGH",
        "era": "POST_SUBSTRATE_BUILD_STAGE_3",
        "cert_status": "measured_mechanism",
        "cert_class": "M1p6_cortex_composition_router_bound_by_per_class_precision_at_small_N_test",
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-01_landing_A",
        "cert_ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS)),
        "hypothesis": "cortex_attention_binding_router_v1 -- M1.6 composition classifier over 5 substrate primitives",
        "supersedes": "prior_seed_7_smoke_MM_atom_ts_1782935173",
        "composes": ["Atom_1_dense_hopfield", "Atom_6_multihop_partition_oracle", "Atom_15_M1p4_refuse_gate", "Atom_18_M1p5_context_retention", "WM_multibank_K4096"],
        "auditor_framing_correction_vs_director": "Director framed as HP_full_3seed. Off-disk pre-reg reading: MIDDLE_BAND applies per §MIDDLE_BAND clause. HP_per_class_precision gate breaches at seed_13 chain_multihop RETRIEVE=0.625 < 0.70.",
        "cross_seed_cv_headline_arm": {"dialogue_pronoun": 0.031, "ood_novel_bind": 0.029, "chain_multihop": 0.083},
        "n_test_per_class": 5,
        "n_test_total_per_arm": 20,
        "expected_n_units": 21,
        "observed_n_arm_rows": 21,
        "cardinality_ok": True
    }
}

# ============= LANDING B: substrate_sparsity_free_axis_v4_pc_only_n4096 =============
atom_B = {
    "id": "math::T3/EXP_substrate_sparsity_free_axis_v4_pc_only_n4096_3seed_FULL_MEASURED_MECHANISM_sparsity_axis_extended_M_grid_800_to_2500_alpha_0p05_0p10_0p20_HP_PC_MONOTONE_CLEARS_at_14_of_15_M_seed_pairs_seed_7_all_5_M_rho_neg_1p0_seed_13_all_5_M_rho_neg_1p0_seed_19_PC_M1000_rho_neg_0p5_breaches_neg_0p8_gate_top1_by_alpha_at_PC_M1000_seed_19_0p713_0p725_0p540_non_monotone_at_first_2_alphas_cross_seed_cv_less_than_0p02_everywhere_numerics_essentially_identical_across_seeds_HP_PC_IN_BAND_all_15_points_in_0p30_0p90_HP_CROSS_SEED_TIGHT_cv_lt_0p05_HP_POSITIVE_CONTROL_PC_M2000_alpha_0p10_top1_0p507_0p530_0p508_all_in_band_MEASURED_bound_sparsity_lever_operates_monotone_in_capacity_pressure_regime_but_breaks_monotonicity_at_M_1000_mid_alpha_grid_on_1_of_3_seeds_supersedes_prior_seed_7_MM_atom_ts_1782935469_wall_16p3s_seed_7_14p2s_seed_13_13p4s_seed_19_2026-07-01",
    "name": "EXP substrate_sparsity_free_axis_v4_pc_only_n4096 3seed FULL MM (sparsity axis; 1/15 monotonicity breach)",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": "Experiment record: exp_substrate_sparsity_free_axis_v4_pc_only_n4096. 3 seeds FULL, verdicts HP/HP/MB. Cross-seed numerics essentially IDENTICAL (cv<0.02 at PC_M800 alpha=0.05: [0.789/0.764/0.773]; cv<0.02 at PC_M2500 alpha=0.20: [0.305/0.301/0.294]). HP_PC_MONOTONE requires rho<=-0.80 at ALL 5 M x 3 seeds = 15 (M,seed) pairs; PASSES at 14/15. Breach: seed_19 PC_M1000 rho=-0.5 (non-monotone at first 2 alphas: 0.713->0.725->0.540). Otherwise all rho=-1.0. HP_PC_IN_BAND: all 15 points in [0.30,0.90]. HP_CROSS_SEED_TIGHT: cv<0.05 everywhere. HP_POSITIVE_CONTROL PC M=2000 alpha=0.10: [0.5075, 0.530, 0.5075] all in band. Verdict tier MEASURED_MECHANISM (proven bound: sparsity lever is monotone at capacity-pressure regime but breaks monotonicity at M=1000 mid-alpha on some seeds). NOT chain-grade under strict pre-reg reading (rho<=-0.80 at ALL 5 M). Numerics tightness (cv<0.02) is remarkable — the MB tier is driven by one narrow gate breach not by cross-seed disagreement on the actual measurements. Supersedes prior seed_7 MM at ts=1782935469.",
    "aliases": [],
    "metadata": {
        "record_class": "experiment_record",
        "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
        "metric_type": None,
        "experiment_path": "experiments\\exp_substrate_sparsity_free_axis_v4_pc_only_n4096.py",
        "prereg_path": "preregs\\2026-07-01_substrate_sparsity_free_axis_v4_pc_only_n4096.md",
        "metrics_paths": [
            "data\\exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_7\\metrics.json",
            "data\\exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_13\\metrics.json",
            "data\\exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_19\\metrics.json"
        ],
        "cell_sha": COMMIT,
        "remote_run_id": None,
        "verdict": "MEASURED_MECHANISM_sparsity_axis_monotone_at_capacity_pressure_regime_partial_breach_at_M1000_mid_alpha",
        "run_mode": "full",
        "provenance_quality": "FULL_3_SEEDS_INDEPENDENT_RECOMPUTE",
        "relevance_tier": "HIGH",
        "era": "POST_SUBSTRATE_BUILD_STAGE_3",
        "cert_status": "measured_mechanism",
        "cert_class": "sparsity_axis_monotone_bounded_by_M1000_mid_alpha_non_monotone_at_1_of_3_seeds",
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-01_landing_B",
        "cert_ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS)),
        "hypothesis": "sparsity axis is monotone-decreasing lever on PC recall at capacity pressure across extended M grid 800-2500",
        "supersedes": "prior_seed_7_MM_atom_ts_1782935469",
        "composes": ["Atom_v2_sparsity_axis_PC_prior_MEASURED", "Modern_Hopfield_HRR_real_primitive"],
        "auditor_framing_correction_vs_director": "Director framed as 2/3 HP + 1/3 MB -> likely MM. Off-disk confirms exactly this. Ruling MM (proven-bound). Cross-seed unanimity broken at 1/15 (M,seed) breach not broad divergence — numerics remarkably tight (cv<0.02).",
        "expected_n_units": 15,
        "observed_n_units_per_seed": 15,
        "cardinality_ok": True,
        "positive_control_pc_M2000_alpha_0p10": {"seed_7": 0.507, "seed_13": 0.530, "seed_19": 0.5075},
        "breach_details": {
            "seed_19_PC_M1000_rho": -0.5,
            "seed_19_PC_M1000_top1_by_alpha": [0.713, 0.725, 0.540],
            "gate_threshold": -0.80,
            "n_breaches_over_total": "1/15"
        }
    }
}

# ============= LEDGER ENTRIES =============
ledger_A = {
    "ts": TS,
    "op": "cert_ruling_measured_mechanism_3seed_full_pre_reg_middle_band_hp_gates_split_per_class_precision_breach",
    "atom_id": atom_A["id"],
    "cert_status": "measured_mechanism",
    "cert_class": "M1p6_cortex_composition_router_bound_by_per_class_precision_at_small_N_test",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_2026-07-01_landing_A",
    "cell_commit": COMMIT,
    "verdict": "MEASURED_MECHANISM_M1p6_composition_router_3seed_FULL_HP_route_accuracy_HP_lift_all_pass_HP_per_class_precision_breach_1_of_9_regime_seed_cells_seed_13_chain_multihop_RETRIEVE_0p625",
    "supersedes_atom_id": "math::T3/EXP_cortex_attention_binding_router_v1_seed_7_smoke_HP_MEASURED_MECHANISM_single_seed_smoke_HP_at_N_8192_V_CB_1024_N_CLASSES_4_verify_landing",
    "cross_seed_cv_headline": {"dialogue_pronoun": 0.031, "ood_novel_bind": 0.029, "chain_multihop": 0.083},
    "auditor_framing_correction_vs_director": "Director framed as HP full 3 seeds. Pre-reg §MIDDLE_BAND explicitly names this pattern (HP gates split; per-class precision splits below 0.70 on one). MM, not CG."
}

ledger_B = {
    "ts": TS,
    "op": "cert_ruling_measured_mechanism_3seed_full_pre_reg_hp_pc_monotone_breach_1_of_15_M_seed_pairs",
    "atom_id": atom_B["id"],
    "cert_status": "measured_mechanism",
    "cert_class": "sparsity_axis_monotone_bounded_by_M1000_mid_alpha_non_monotone_at_1_of_3_seeds",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_2026-07-01_landing_B",
    "cell_commit": COMMIT,
    "verdict": "MEASURED_MECHANISM_sparsity_axis_v4_3seed_FULL_2HP_1MB_seed_19_PC_M1000_rho_neg_0p5_breaches_neg_0p80_gate_numerics_cv_lt_0p02_cross_seed",
    "supersedes_atom_id": "math::T3/EXP_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_7_FULL_MEASURED_MECHANISM_single_seed_FULL_HP_all_HP_gates_cleared_awaits_seeds_13_19"
}

# ============= A5-GATED ATOMIC WRITES =============
def atomic_append(path, records):
    """Atomic write: read existing + append records + write to tmp + os.replace."""
    with open(path, encoding='utf-8') as f:
        existing = f.read()
    tmpf = tempfile.NamedTemporaryFile(mode='w', delete=False, dir=os.path.dirname(path), suffix='.tmp', encoding='utf-8')
    try:
        tmpf.write(existing)
        for rec in records:
            tmpf.write(json.dumps(rec, ensure_ascii=False) + "\n")
        tmpf.flush()
        os.fsync(tmpf.fileno())
        tmpf.close()
        # verify parse before swap
        with open(tmpf.name, encoding='utf-8') as vf:
            count = 0
            for line in vf:
                json.loads(line)
                count += 1
        os.replace(tmpf.name, path)
        return count
    except Exception:
        os.unlink(tmpf.name)
        raise

# WRITE ATOMS
n_atoms_after = atomic_append(MATH_ATOMS, [atom_A, atom_B])
# VERIFY LOAD
with open(MATH_ATOMS, encoding='utf-8') as f:
    reloaded_ids = set()
    for line in f:
        try:
            a = json.loads(line)
            reloaded_ids.add(a['id'])
        except:
            pass
assert atom_A['id'] in reloaded_ids, "Atom A did not load"
assert atom_B['id'] in reloaded_ids, "Atom B did not load"

# WRITE LEDGER
n_ledger_after = atomic_append(CERT_LEDGER, [ledger_A, ledger_B])

print(f"OK: math/atoms.jsonl now {n_atoms_after} atoms; meta/cert_ledger.jsonl now {n_ledger_after} entries")
print(f"Atom A id: {atom_A['id'][:120]}...")
print(f"Atom B id: {atom_B['id'][:120]}...")
print(f"Landing A: MEASURED_MECHANISM (pre-reg MIDDLE_BAND per §HP-gates-split)")
print(f"Landing B: MEASURED_MECHANISM (pre-reg 2/3 HP + 1/3 MB; 1/15 monotonicity breach)")
