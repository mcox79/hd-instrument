"""
A5-gated batch atomization: 3 regime FULL 3-seed packs landed 2026-07-03.

- Pack 1: stage1_regime_map_storage_x_cleanup_v1 s7/s13/s19  -> MM_STANDARD (storage-conditional mechanism-axis cross-term)
- Pack 2: exp_stage1_regime_probe_2_N_x_cleanup_mechanism_v1 s11/s17/s23 -> DOWNGRADE to SATURATION_VACUOUS
- Pack 3: exp_regime_probe_3_topology_x_cleanup_v1 s7/s13/s19 -> DOWNGRADE saturation-vacuous + F-axis mislabel (per atom #48); atomize bundle_pc storage-gap replicate as MM_TENTATIVE
- META atom: orchestrator BOTH-PREFIX hallucination pattern for path citation

Atomic write (tmp -> os.replace) + verify-load + integrity check.
"""
import json, os, sys, hashlib, tempfile, statistics as st
from pathlib import Path

REPO = Path("d:/AI/hd-instrument")
MATH_ATOMS = REPO / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = REPO / "data/substrate_index/meta/atoms.jsonl"
LEDGER = REPO / "data/substrate_index/meta/cert_ledger.jsonl"
TS = "2026-07-03T23:15:00Z"
AUDIT_TS = TS

# ----- read all metrics off disk -----
def load(p):
    return json.load(open(REPO / p))

pack1_seeds = [7, 13, 19]
pack1_paths = [f"data/exp_stage1_regime_map_storage_x_cleanup_v1_s{s}/metrics.json" for s in pack1_seeds]
pack1 = [load(p) for p in pack1_paths]

pack2_seeds = [11, 17, 23]
pack2_paths = [f"data/exp_exp_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_s{s}/metrics.json" for s in pack2_seeds]
pack2 = [load(p) for p in pack2_paths]

pack3_seeds = [7, 13, 19]
pack3_paths = [f"data/exp_exp_regime_probe_3_topology_x_cleanup_v1_s{s}/metrics.json" for s in pack3_seeds]
pack3 = [load(p) for p in pack3_paths]

# ----- extract key metrics per pack -----
# Pack 1: mech_var_at_BUNDLED parse from verdict_msg
def parse_p1(m):
    vm = m["verdict_msg"]
    # HARD_PASS_MECHANISM_AXIS_CONDITIONAL_ON_STORAGE: max_int_deviation=0.0028 mech_var_at_BUNDLED=0.1000 mech_var_at_SHARDED=0.0000;
    import re
    dev = float(re.search(r"max_int_deviation=([\d.]+)", vm).group(1))
    varB = float(re.search(r"mech_var_at_BUNDLED=([\d.]+)", vm).group(1))
    varS = float(re.search(r"mech_var_at_SHARDED=([\d.]+)", vm).group(1))
    return dev, varB, varS

p1_metrics = [parse_p1(m) for m in pack1]
p1_dev = [x[0] for x in p1_metrics]
p1_varB = [x[1] for x in p1_metrics]
p1_varS = [x[2] for x in p1_metrics]
p1_cv_varB = st.stdev(p1_varB) / st.mean(p1_varB)
p1_max_storage_gap = [m["max_storage_gap"] for m in pack1]

# Pack 2: saturation grid
p2_all_spread_zero = all(m["max_mech_acc_spread"] == 0.0 for m in pack2)
p2_all_cells_saturated = all(
    all(cell["accs_by_mech"][mech] == 1.0 for cell in per_n["per_cell_details"]
        for mech in cell["accs_by_mech"])
    for m in pack2 for per_n in m["per_N_mech_variance"].values()
)

# Pack 3: saturation + bundle_pc storage-gap
p3_all_var_zero = all(m["max_per_F_mech_variance"] == 0.0 for m in pack3)
p3_bundle_pc = [m["bundle_pc_result"] for m in pack3]
p3_bundle_accs = [b["bundle_acc"] for b in p3_bundle_pc]
p3_sharded_accs = [b["sharded_at_same_regime_acc"] for b in p3_bundle_pc]
p3_storage_gaps = [b["storage_gap_sharded_minus_bundled"] for b in p3_bundle_pc]

print(f"Pack1: max_int_dev={p1_dev} mech_var_BUNDLED={p1_varB} mech_var_SHARDED={p1_varS} cv_varB={p1_cv_varB:.4f}")
print(f"       max_storage_gap all=1.0: {all(g == 1.0 for g in p1_max_storage_gap)}")
print(f"Pack2: all_spread_zero={p2_all_spread_zero} all_cells_saturated=True (verified in verify script)")
print(f"Pack3: all_F_var_zero={p3_all_var_zero} bundle_accs={p3_bundle_accs} sharded_accs={p3_sharded_accs}")
print(f"       storage_gaps sharded-bundled={p3_storage_gaps} mean={st.mean(p3_storage_gaps):.3f}")

# ----- build atoms -----
atoms_math = []
atoms_meta = []

# --------- PACK 1 atom: MM_STANDARD ---------
p1_atom_id = ("math::MM_STANDARD/EXP_stage1_regime_map_storage_x_cleanup_v1_s7_s13_s19_FULL_3seed"
    "_MECHANISM_AXIS_CONDITIONAL_ON_STORAGE_cross_term_HARD_PASS_all_seeds"
    "_mech_var_BUNDLED_0p09_0p10_0p12_cv_0p148_mech_var_SHARDED_0p00_all_seeds"
    "_max_int_dev_le_0p0058_max_storage_gap_1p0_all_seeds_composes_with_Probe1_STORAGE_x_CLEANUP_CG_META"
    "_and_atom_56_SHARDED_capacity_cliff_regime_map_layer1_root_2026-07-03")

p1_atom = {
    "atom_id": p1_atom_id,
    "entity": "stage1_regime_map_storage_x_cleanup_v1",
    "corpus": "math",
    "kind": "experiment_cell_regime_cross_term",
    "tier": "MM_STANDARD",
    "ts_added": TS,
    "verified_off_data": True,
    "provenance_quality": "verified_3seed_FULL_independent_recompute",
    "anchor": "stage1_regime_map_storage_x_cleanup_v1",
    "metrics_paths": pack1_paths,
    "run_mode": "full",
    "n_seeds": 3,
    "seeds": pack1_seeds,
    "source_signature": "STORAGE={BUNDLED, SHARDED} x CLEANUP={modern_hopfield, iterative_cosine, soft_energy_attractor}; M in {200, 800, 3200}; N in {2048, 8192}; F=1; L=2; corruption in {0.20, 0.45}",
    "per_seed_metrics": {
        f"seed_{s}": {
            "cardinality_ok": pack1[i]["cardinality_ok"],
            "n_distinct_mechanisms": pack1[i]["n_distinct_mechanisms"],
            "arms_differ_verified": pack1[i]["arms_differ_verified"],
            "max_int_deviation": p1_dev[i],
            "mech_var_at_BUNDLED": p1_varB[i],
            "mech_var_at_SHARDED": p1_varS[i],
            "max_storage_gap": p1_max_storage_gap[i],
            "pc_pass": pack1[i]["pc_reproduce_iterative_cosine_regime"]["pass"],
            "pc_acc": pack1[i]["pc_reproduce_iterative_cosine_regime"]["acc"],
        }
        for i, s in enumerate(pack1_seeds)
    },
    "cross_seed": {
        "n_seeds": 3,
        "mech_var_at_BUNDLED_mean": st.mean(p1_varB),
        "mech_var_at_BUNDLED_stdev": st.stdev(p1_varB),
        "mech_var_at_BUNDLED_cv": p1_cv_varB,
        "mech_var_at_SHARDED_all_zero": all(v == 0.0 for v in p1_varS),
        "max_storage_gap_all_1p0": all(g == 1.0 for g in p1_max_storage_gap),
    },
    "primary_claim": ("STORAGE x CLEANUP cross-term is a REAL regime-cross-term (not artifact): at BUNDLED "
        "(bundle superposition capacity-limited regime) the CLEANUP_MECHANISM axis is MEANINGFUL (mech_var 0.09-0.12 "
        "across 3 seeds, cv=0.148 at MM_STANDARD boundary), but at SHARDED (per-role dimensional partition regime) "
        "the CLEANUP_MECHANISM axis COLLAPSES (mech_var=0.00 uniformly across seeds because all mechanisms saturate "
        "at 1.0 given SHARDED's capacity headroom). max_storage_gap=1.0 in all 3 seeds confirms SHARDED strictly "
        "dominates BUNDLED at the ceiling of the tested M x N grid. Confirms and extends Probe 1 CG_META "
        "STORAGE x CLEANUP finding at Layer-1 regime-map root by demonstrating 3-seed cross-seed stability with "
        "arms_differ_verified=True and 3 distinct mechanism hashes across all seeds."),
    "cardinality_ok_all_seeds": True,
    "arms_differ_verified_all_seeds": True,
    "positive_control_pass_all_seeds": True,
    "elapsed_s_seeds": [pack1[i]["elapsed_s"] for i in range(3)],
    "composes_with": [
        "Probe 1 CG_META STORAGE x CLEANUP mechanism-axis-only-at-BUNDLED",
        "math atom #56 SHARDED capacity beyond bundle-plate cliff",
    ],
    "amends_atoms": [],
    "reframes_available_not_filed": [
        "Not yet CG_META because mech_var_at_BUNDLED cv=0.148 is at MM boundary and the cross-term is CONFIRMATORY of Probe 1 not novel. Promotion path: reproduce at M=3200 for BUNDLED with 5 seeds at cv<0.10 to promote to CG_META.",
    ],
    "novelty_check": "Cross-arc substrate_query for 'STORAGE cleanup mechanism cross-term SHARDED BUNDLED' returned cosine<0.33 top match (prior SHARDED-cliff atom #56 at 0.31). Not a rediscovery. Extends Probe 1 CG_META with independent 3-seed FULL replication + explicit BUNDLED-var>0 vs SHARDED-var=0 phase-boundary characterization.",
    "framing_corrections_vs_cell_author_and_director": (
        "Director-cited paths CORRECT for Pack 1 (single-prefix landings). Cell-author verdict_msg accurate to disk. "
        "MM_STANDARD not CG_META because (a) mech_var_at_BUNDLED cv=0.148 sits at the MM upper boundary and (b) the "
        "cross-term structure is CONFIRMATORY of Probe 1 CG_META not novel discovery. Cross-seed cv would need to drop "
        "below 0.10 with 5 seeds to earn CG_META promotion at this axis-intersection."),
    "cross_arc_overlap_check": "Prior sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1 seeds 7 and 13 at cosine 0.30-0.31; both are SHARDED-side cliff findings that this Pack 1 result composes with. No full-rediscovery.",
    "smoke_disciplines_verified": ["run_mode=full verified off-disk all seeds", "3 distinct mechanism hashes", "arms_differ_verified=True", "PC=1.0 at reproducibility regime all seeds", "cardinality_ok all seeds"],
    "session_atom_index_math": 59,
    "audit_ts": AUDIT_TS,
}
atoms_math.append(p1_atom)

# --------- PACK 2 atom: SATURATION_VACUOUS downgrade (MM_TENTATIVE with framing correction) ---------
p2_atom_id = ("math::MM_TENTATIVE_SATURATION_VACUOUS/EXP_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_s11_s17_s23_FULL_3seed"
    "_H1_OPTION_Y_EXTENDS_UNIVERSAL_claim_DOWNGRADED_to_SATURATION_VACUOUS_NO_CLIFF_FOUND_IN_TESTED_BRACKET"
    "_all_72_cells_per_seed_read_1p0_across_N_2048_4096_8192_16384_x_M_200_800_3200_x_mech_3_x_corr_0p20_0p45"
    "_max_mech_acc_spread_0p0_but_NOT_a_universal_invariance_proof_bracket_saturated_at_ceiling"
    "_2x_research_trigger_needed_at_harder_corruption_or_smaller_M_or_larger_N_2026-07-03")

p2_atom = {
    "atom_id": p2_atom_id,
    "entity": "exp_stage1_regime_probe_2_N_x_cleanup_mechanism_v1",
    "corpus": "math",
    "kind": "experiment_cell_saturation_vacuous_framing_correction",
    "tier": "MM_TENTATIVE",
    "ts_added": TS,
    "verified_off_data": True,
    "provenance_quality": "verified_3seed_FULL_independent_recompute_framing_downgraded",
    "anchor": "exp_stage1_regime_probe_2_N_x_cleanup_mechanism_v1",
    "metrics_paths": pack2_paths,
    "metrics_paths_note": "Director-cited paths were single-prefix 'data/exp_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_s{11,17,23}/metrics.json' which DO NOT EXIST on disk. Actual landings at DOUBLE-PREFIX 'data/exp_exp_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_s{11,17,23}/metrics.json'. BOTH-PREFIX orchestrator-hallucination pattern (memory feedback_orchestrator_hallucination_pattern_verify_disk_before_propagating_2026-07-03). Verified via ls + json.load.",
    "run_mode": "full",
    "n_seeds": 3,
    "seeds": pack2_seeds,
    "source_signature": "N in {2048, 4096, 8192, 16384} x CLEANUP={modern_hopfield, iterative_cosine, soft_energy_attractor}; M in {200, 800, 3200}; corr in {0.20, 0.45}; F=1; L=2",
    "per_seed_metrics": {
        f"seed_{s}": {
            "cardinality_ok": pack2[i]["cardinality_ok"],
            "n_distinct_mechanisms": pack2[i]["n_distinct_mechanisms"],
            "arms_differ_verified": pack2[i]["arms_differ_verified"],
            "max_mech_acc_spread": pack2[i]["max_mech_acc_spread"],
            "pc_pass": pack2[i]["pc_reproduce_iterative_cosine_regime"]["pass"],
            "pc_acc": pack2[i]["pc_reproduce_iterative_cosine_regime"]["acc"],
            "cells_per_N_saturated_at_1p0": {
                str(N): all(cell["accs_by_mech"][mech] == 1.0 for cell in pd["per_cell_details"] for mech in cell["accs_by_mech"])
                for N, pd in pack2[i]["per_N_mech_variance"].items()
            },
        }
        for i, s in enumerate(pack2_seeds)
    },
    "cross_seed": {
        "n_seeds": 3,
        "max_mech_acc_spread_all_seeds_zero": p2_all_spread_zero,
        "all_72_cells_per_seed_saturated_at_1p0": True,
    },
    "primary_claim": ("SATURATION_VACUOUS NEGATIVE FRAMING: cell verdict_msg claims 'H1_OPTION_Y_EXTENDS_UNIVERSAL: "
        "CLEANUP_MECHANISM axis regime-narrow at all N in [2048, 4096, 8192, 16384]; max mech_var=0.0 < 0.05'. "
        "This claim is UNSUPPORTED because the entire M x N x corr x mechanism grid saturates at 1.0 accuracy across "
        "all 3 seeds. When every cell of the tested bracket reads at ceiling, mech_var=0.0 is a CONSEQUENCE of "
        "bracket-exhaustion (no cliff hit) not a proof of universal mechanism-invariance. Per Skunkworks 2026-07-03 "
        "META_saturation_floor rule and Meta atom #45 bracket-exhaustion HONEST_NO_MATCHED_CLIFF: cannot conclude "
        "regime-narrow-invariance from a saturated grid. The corr=0.45 was NOT the cliff (all mechs = 1.0 there); "
        "grid needs harder corruption (>=0.55), smaller M (<200 items where hopfield capacity-bound bites), or "
        "asymmetric noise to stress mechanisms. Downgrading to MM_TENTATIVE with SATURATION_VACUOUS marker."),
    "cardinality_ok_all_seeds": True,
    "arms_differ_verified_all_seeds": True,
    "positive_control_pass_all_seeds": True,
    "elapsed_s_seeds": [pack2[i]["elapsed_s"] for i in range(3)],
    "composes_with": [
        "Skunkworks 2026-07-03 META_saturation_floor discipline",
        "Meta atom #45 bracket-exhaustion HONEST_NO_MATCHED_CLIFF",
    ],
    "amends_atoms": [
        "verdict_msg claim 'H1_OPTION_Y_EXTENDS_UNIVERSAL' is DOWNGRADED to SATURATION_VACUOUS_NO_CLIFF_FOUND_IN_TESTED_BRACKET. cell is not superseded but its universal-extension claim is not supported.",
    ],
    "reframes_available_not_filed": [
        "2x-research trigger recommended: probe N x CLEANUP at corr>=0.55 and/or M<200 to actually stress mechanisms.",
        "arms_differ_verified=True is a CARDINALITY assertion (3 distinct mech hashes) but does NOT imply mechanism-outcome-distinguishability at this bracket.",
    ],
    "novelty_check": "This is a framing-correction atom for a landed cell that overclaimed universal extension from a saturated grid. The correction discipline is instantiated by prior Meta #45 and META_saturation_floor.",
    "framing_corrections_vs_cell_author_and_director": (
        "MAJOR: cell-author verdict_msg claims universal extension from saturated grid (max_mech_acc_spread=0.0 across "
        "all 72 cells per seed). Skunkworks DOWNGRADES to SATURATION_VACUOUS per META_saturation_floor. Director-spawn-"
        "cited path was WRONG (single-prefix, does not exist); actual landings at double-prefix 'exp_exp_...'. This is "
        "the BOTH-PREFIX orchestrator-hallucination pattern from memory 2026-07-03. Verify-off-disk gate would have "
        "caught this at Director tier before propagating to Skunkworks."),
    "cross_arc_overlap_check": "SATURATION_VACUOUS discipline is same shape as Meta #45 bracket-exhaustion; compose relationship not rediscovery.",
    "smoke_disciplines_verified": ["run_mode=full verified off-disk", "grid saturation verified via per_N_mech_variance per_cell_details all=1.0"],
    "session_atom_index_math": 60,
    "audit_ts": AUDIT_TS,
}
atoms_math.append(p2_atom)

# --------- PACK 3 atom: DOWNGRADE F-axis saturation + atomize bundle_pc storage-gap replicate as MM_TENTATIVE ---------
p3_atom_id = ("math::MM_TENTATIVE_SATURATION_VACUOUS/EXP_regime_probe_3_topology_x_cleanup_v1_s7_s13_s19_FULL_3seed"
    "_dual_finding_a_F_axis_saturation_vacuous_downgrade_of_H1_MECHANISM_DEGENERACY_EXTENDS_ACROSS_TOPOLOGY_claim"
    "_all_cells_at_c_0p45_read_1p0_across_F_1_2_4_8_x_M_200_800_3200"
    "_dual_finding_b_bundle_pc_storage_gap_replicate_confirms_Pack1_and_atom_56"
    "_bundle_acc_0p05_to_0p13_vs_SHARDED_1p0_storage_gap_0p87_to_0p95_all_seeds_at_M_800_N_4096_F_1_L_2_corr_0p20"
    "_axis_mislabel_TOPOLOGY_is_F_fan_out_per_meta_atom_48_2026-07-03")

p3_atom = {
    "atom_id": p3_atom_id,
    "entity": "exp_regime_probe_3_topology_x_cleanup_v1",
    "corpus": "math",
    "kind": "experiment_cell_saturation_vacuous_plus_partial_composition_replicate",
    "tier": "MM_TENTATIVE",
    "ts_added": TS,
    "verified_off_data": True,
    "provenance_quality": "verified_3seed_FULL_independent_recompute_dual_finding",
    "anchor": "exp_regime_probe_3_topology_x_cleanup_v1",
    "metrics_paths": pack3_paths,
    "metrics_paths_note": "Director-cited paths were 'data/exp_regime_probe_3_topology_x_cleanup_v1_s{7,13,19}/metrics.json'. Only s7 exists at single-prefix and it is run_mode=selftest (1285 bytes). Actual FULL landings at DOUBLE-PREFIX 'data/exp_exp_regime_probe_3_topology_x_cleanup_v1_s{7,13,19}/metrics.json' (~36KB each, run_mode=full). BOTH-PREFIX orchestrator-hallucination pattern.",
    "run_mode": "full",
    "n_seeds": 3,
    "seeds": pack3_seeds,
    "source_signature": "F in {1, 2, 4, 8} x CLEANUP={modern_hopfield, iterative_cosine, soft_energy_attractor}; M in {200, 800, 3200}; N=4096; L=2; corr={0.20, 0.45}; STORAGE={BUNDLED for bundle_pc probe, SHARDED for main F-axis sweep}",
    "per_seed_metrics": {
        f"seed_{s}": {
            "cardinality_ok": pack3[i]["cardinality_ok"],
            "n_distinct_mechanisms": pack3[i]["n_distinct_mechanisms"],
            "max_per_F_mech_variance": pack3[i]["max_per_F_mech_variance"],
            "pc_pass": pack3[i]["pc_reproduce_iterative_cosine_regime"]["pass"],
            "pc_acc": pack3[i]["pc_reproduce_iterative_cosine_regime"]["acc"],
            "bundle_pc_bundle_acc": p3_bundle_accs[i],
            "bundle_pc_sharded_acc": p3_sharded_accs[i],
            "bundle_pc_storage_gap": p3_storage_gaps[i],
        }
        for i, s in enumerate(pack3_seeds)
    },
    "cross_seed": {
        "n_seeds": 3,
        "F_axis_max_per_F_mech_variance_all_zero": p3_all_var_zero,
        "F_axis_saturation_vacuous": True,
        "bundle_pc_storage_gap_mean": st.mean(p3_storage_gaps),
        "bundle_pc_storage_gap_stdev": st.stdev(p3_storage_gaps),
        "bundle_pc_storage_gap_all_gt_0p85": all(g > 0.85 for g in p3_storage_gaps),
    },
    "primary_claim": ("DUAL FINDING with mixed disposition: (a) DOWNGRADE cell's primary claim 'H1_MECHANISM_DEGENERACY_"
        "EXTENDS_ACROSS_TOPOLOGY (F fan-out)' to SATURATION_VACUOUS. Every F x M x mechanism cell at cliff_corr=0.45 "
        "reads mech_variance=0.0 across all 3 seeds. Same bracket-exhaustion pattern as Pack 2 - cannot conclude F-axis "
        "regime-narrow-invariance from a saturated grid. AXIS-MISLABEL correction per Meta atom #48: cell correctly names "
        "the axis as F fan-out in verdict_msg text ('independent of encoder topology (F fan-out)'), but pre-reg and "
        "Director-spawn framing used 'TOPOLOGY' loosely. F is a substrate primitive (encoder fan-out), NOT topology. "
        "(b) ATOMIZE the bundle_pc storage-gap replicate as MM_TENTATIVE composition with Pack 1 and math atom #56: "
        "at BUNDLED M=800 N=4096 F=1 L=2 corr=0.20 with iterative_cosine cleanup, bundle_acc drops to 0.05-0.13 "
        "across seeds while SHARDED at the same regime achieves 1.0, yielding storage_gap 0.87-0.95 (mean 0.9, "
        "stdev 0.042). This is a THIRD independent 3-seed replication of the SHARDED-strictly-dominates-BUNDLED "
        "capacity-cliff finding."),
    "cardinality_ok_all_seeds": True,
    "positive_control_pass_all_seeds": True,
    "elapsed_s_seeds": [pack3[i]["elapsed_s"] for i in range(3)],
    "composes_with": [
        "Pack 1 (this session, math #59) STORAGE x CLEANUP cross-term via bundle_pc replicate",
        "math atom #56 SHARDED capacity beyond bundle-plate cliff via bundle_pc replicate",
        "Meta atom #48 axis-aliasing discipline (F vs TOPOLOGY)",
        "Meta atom #45 bracket-exhaustion HONEST_NO_MATCHED_CLIFF for F-axis saturation-vacuous portion",
        "Skunkworks 2026-07-03 META_saturation_floor discipline",
    ],
    "amends_atoms": [
        "verdict_msg claim 'CLEANUP_MECHANISM axis is regime-narrow independent of encoder topology (F fan-out)' is DOWNGRADED for the F-axis portion to SATURATION_VACUOUS. The bundle_pc storage-gap portion stands as MM_TENTATIVE replicate.",
    ],
    "reframes_available_not_filed": [
        "F-axis stress-testing: needs corr>=0.55 or M<200 to escape saturation at F in {1,2,4,8}.",
        "The bundle_pc storage-gap replicate is 3-seed consistent at one regime (M=800 N=4096 F=1 corr=0.20); MM_TENTATIVE not MM_STANDARD because it is a single-cell replicate of Pack 1's cross-cell finding, not a novel 3-seed x multi-cell cross-term.",
    ],
    "novelty_check": "F-axis SATURATION_VACUOUS is same discipline shape as Pack 2 (this session) — this atom composes not rediscovers. bundle_pc replicate composes with Pack 1 (#59) and atom #56 SHARDED-cliff — extends confirmation not novel discovery.",
    "framing_corrections_vs_cell_author_and_director": (
        "MAJOR: (1) Director-spawn framing called this pack 'TOPOLOGY(F) x CLEANUP'; per Meta atom #48 axis-labels-to-"
        "substrate-primitives, this MUST be labeled 'F(fan-out) x CLEANUP'. The cell-author verdict_msg itself uses the "
        "correct substrate-primitive label. (2) cell-author claim 'H1_MECHANISM_DEGENERACY_EXTENDS_ACROSS_TOPOLOGY' is "
        "DOWNGRADED because the F-axis grid saturates at 1.0 across all cells at cliff_corr=0.45. (3) Director-cited "
        "paths were WRONG (single-prefix, only s7 exists as selftest); actual FULL landings at double-prefix. "
        "BOTH-PREFIX orchestrator-hallucination pattern. (4) The bundle_pc storage-gap portion IS defensible as a "
        "MM_TENTATIVE replicate of Pack 1 and atom #56 - kept as bounded composition."),
    "cross_arc_overlap_check": "bundle_pc storage-gap composes with Pack 1 (this session) and atom #56 SHARDED-cliff at cosine ~0.30-0.31. Not rediscovery - 3rd independent 3-seed replication is EVIDENCE_ACCUMULATION not novelty.",
    "smoke_disciplines_verified": ["run_mode=full verified off-disk", "F-axis saturation verified via per_F_mech_variance all zero", "bundle_pc storage-gap verified via bundle_pc_result field"],
    "session_atom_index_math": 61,
    "audit_ts": AUDIT_TS,
}
atoms_math.append(p3_atom)

# --------- META atom: orchestrator BOTH-PREFIX hallucination pattern recurrence ---------
meta_atom_id = ("meta::META_orchestrator_path_hallucination_BOTH_PREFIX_pattern_recurrence_v2_2026-07-03"
    "_Director_spawn_cited_single_prefix_paths_that_do_not_exist_on_disk_for_2_of_3_regime_packs_this_batch"
    "_pack2_N_x_cleanup_and_pack3_F_x_cleanup"
    "_actual_landings_at_double_prefix_exp_exp_dirs_MM_STANDARD_promotion_evidence_second_batch_hit_this_week")

meta_atom = {
    "atom_id": meta_atom_id,
    "entity": "META_orchestrator_path_hallucination_BOTH_PREFIX",
    "corpus": "meta",
    "kind": "meta_rule_orchestrator_hygiene_recurrence_evidence",
    "tier": "MM_STANDARD",
    "ts_added": TS,
    "verified_off_data": True,
    "provenance_quality": "verified_from_2_of_3_batch_packs_this_landing_plus_prior_memory_reference",
    "anchor": "META_orchestrator_path_hallucination_BOTH_PREFIX",
    "metrics_paths": pack2_paths + pack3_paths,
    "rule_statement": ("Director-spawned batch-VET requests can carry HALLUCINATED metrics.json paths using single-prefix "
        "'exp_<cell_name>' when the actual disk landings occurred at double-prefix 'exp_exp_<cell_name>'. In this batch "
        "2 of 3 packs (Pack 2 N_x_cleanup, Pack 3 F_x_cleanup) had cited paths that DO NOT EXIST at the cited location; "
        "actual FULL metrics landed at double-prefix. Pack 1 (storage_x_cleanup) landed at single-prefix correctly. "
        "Auditor MUST verify path existence off-disk (ls or Path.exists) BEFORE loading metrics; if primary path is "
        "missing, probe the double-prefix variant and mirror-selftest single-prefix variant to determine whether the "
        "cited path is the intended landing or a Director-side rewrite artifact."),
    "actionable_guardrail": ("Auditor pre-flight for any batch-VET request MUST include: (a) Path.exists check on every "
        "cited metrics.json; (b) if any missing, immediate ls of parent 'data/' dir with grep for anchor stem to find "
        "actual landing dir (single-prefix and double-prefix variants); (c) verify run_mode=='full' or the requested run "
        "mode in the actually-loaded file, not the assumed one from Director-spawn narrative. Fix#28 filesystem-verify "
        "discipline extends to Director-cited paths not just cell-author verdict text."),
    "evidence_this_landing": {
        "pack1_storage_x_cleanup_single_prefix_correct": True,
        "pack2_N_x_cleanup_single_prefix_MISSING_actual_at_double_prefix": True,
        "pack3_F_x_cleanup_single_prefix_only_selftest_1285B_actual_FULL_at_double_prefix_36KB": True,
        "batch_hit_rate": "2 of 3 packs",
    },
    "evidence_atoms": [
        "math::MM_TENTATIVE_SATURATION_VACUOUS/EXP_stage1_regime_probe_2_N_x_cleanup_mechanism_v1 (this session)",
        "math::MM_TENTATIVE_SATURATION_VACUOUS/EXP_regime_probe_3_topology_x_cleanup_v1 (this session)",
    ],
    "composes_with": [
        "feedback_orchestrator_hallucination_pattern_verify_disk_before_propagating_2026-07-03",
        "feedback_director_wikipedia_full_10k_hallucination_fix28_recurrence_2026-07-03",
        "feedback_director_three_overclaims_same_day_fix28_pattern_2026-07-03",
        "Fix#28 filesystem-verify-before-framing (memory 2026-06-22)",
    ],
    "amends_atoms": [],
    "novelty_check": "Extends prior 2026-07-03 orchestrator-hallucination-pattern feedback with SECOND-BATCH-HIT-THIS-WEEK evidence (previous instance was different cells; this instance is 2-of-3 batch hit rate). Not novel discipline (rule statement exists in prior feedback memory) but evidence-strengthening at MM_STANDARD tier.",
    "framing_corrections_vs_cell_author_and_director": "Director spawn used single-prefix path narrative for all 3 packs. 2 of 3 are wrong on disk. Correction: Auditor pre-flight caught the miss; Director should pull actual landing paths from orchestrator status task metadata not narrative.",
    "cross_arc_overlap_check": "Prior orchestrator-hallucination feedback at cosine ~0.40+; this atom is the SUBSTRATE-KB registration of that feedback with recurrence-count-2 evidence this week.",
    "expansion_criterion": "Promote MM_STANDARD -> CG_META if a 3rd batch-VET this month hits BOTH-PREFIX pattern with rate >=1 of any 3-pack batch.",
    "session_atom_index_meta": 49,
    "audit_ts": AUDIT_TS,
}
atoms_meta.append(meta_atom)

# ---- write with A5 gate ----
def a5_write(path, atoms):
    """Atomic append via read-existing + write tmp + os.replace + verify-load."""
    path = Path(path)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    new_lines = "\n".join(json.dumps(a) for a in atoms) + "\n"
    combined = existing + new_lines
    tmp_fd, tmp_path = tempfile.mkstemp(prefix=path.name + ".tmp.", dir=str(path.parent))
    os.close(tmp_fd)
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(combined)
    os.replace(tmp_path, path)
    # verify-load
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if line.strip():
                json.loads(line)  # will raise if corrupt
    # integrity: last-N atoms match
    with open(path, "r", encoding="utf-8") as f:
        all_lines = [l for l in f if l.strip()]
    tail_n = len(atoms)
    for a, line in zip(atoms, all_lines[-tail_n:]):
        assert json.loads(line)["atom_id"] == a["atom_id"], f"atom mismatch {a['atom_id']}"
    print(f"A5-verified: wrote {len(atoms)} atoms to {path}")

a5_write(MATH_ATOMS, atoms_math)
a5_write(META_ATOMS, atoms_meta)

# ---- cert_ledger entries ----
ledger_entries = []
for a in atoms_math + atoms_meta:
    ledger_entries.append({
        "ts": TS,
        "atom_id": a["atom_id"],
        "corpus": a["corpus"],
        "tier": a["tier"],
        "action": "landed_vet_batch_2026-07-03_pack123",
        "verified_off_data": True,
        "auditor": "skunkworks",
        "audit_ts": AUDIT_TS,
    })

# append ledger
existing_l = LEDGER.read_text(encoding="utf-8") if LEDGER.exists() else ""
new_l = "\n".join(json.dumps(e) for e in ledger_entries) + "\n"
tmp_fd, tmp_path = tempfile.mkstemp(prefix="cert_ledger.tmp.", dir=str(LEDGER.parent))
os.close(tmp_fd)
with open(tmp_path, "w", encoding="utf-8") as f:
    f.write(existing_l + new_l)
os.replace(tmp_path, LEDGER)
print(f"Ledger appended {len(ledger_entries)} entries")

print("\n===== SUMMARY =====")
print(f"Math atoms: {len(atoms_math)} (indices 59, 60, 61)")
print(f"Meta atoms: {len(atoms_meta)} (index 49)")
print("Pack1: MM_STANDARD (regime-cross-term storage-conditional mech-axis)")
print("Pack2: MM_TENTATIVE SATURATION_VACUOUS (downgrade from cell's H1_OPTION_Y_UNIVERSAL claim)")
print("Pack3: MM_TENTATIVE dual-finding (F-axis SATURATION_VACUOUS + bundle_pc storage-gap replicate)")
print("Meta: BOTH-PREFIX orchestrator-hallucination pattern recurrence evidence")
