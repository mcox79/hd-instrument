"""
A5-gated atomize:
  (1) ANCHOR4 encoder family N=16384 3-seed CHAIN_GRADE (4th CG of 2026-07-01)
  (2) Cross-modal binding 3rd modality single-seed MM

INDEPENDENT OFF-DATA RECOMPUTE via .venv python (skunkworks 2026-07-01):

Substrate-KB overlap check (per new 2026-07-01 discipline rule):
  ANCHOR4 N=16384: cosine 0.31 top match = note-chunk (encoder-family concept
    at N=16384 discussed in prereg-chunks 2026-06-06); no prior Store atom for
    THIS specific N=16384 cell. Prior ANCHOR4 N=8192 v4 is CG-atomized already
    (commit a17e13be 2026-06-30). This extends N to 16384.
  Cross-modal 3rd modality: cosine 0.50 top match = note-chunks (cross-modal
    binding concept in older research notes); no prior Store atom. Composes
    with prior cross-modal visual+auditory CG (per Director framing).

============================================================
(1) ANCHOR4 encoder family N=16384 3-seed CG
============================================================

Cell path: data/exp_substrate_anchor4_encoder_family_N16384_gpu_v1_seed_{7,13,19}/metrics.json
Pre-reg: preregs/2026-07-01_substrate_anchor4_encoder_family_N16384_gpu_v1.md

Off-data facts:
  All 3 seeds run_mode=full; verdict=HARD_PASS; cardinality 60/60 units per seed
  (60 phase points x 1 seed per file; 3 files = 180 total phase measurements).
  overall_dominance_rate = 1.000 all 3 seeds (cv=0.000)
  overall_net_dominance  = 1.000 all 3 seeds
  overall_rd_loss_rate   = 0.000 all 3 seeds
  saturation_frac_total  = 0.000 all 3 seeds
  n_pts / n_pts_total    = 60/60 all seeds
  5/5 encoders per_encoder_chain_grade_pass = True all seeds:
    binary_bipolar / hrr_real / fhrr / sparse_bipolar / sparse_real
  arms_differ_per_encoder: 5/5 encoders mechanism vs random hashes distinct all seeds
  encoder_tiers: all 5 = COMPETITIVE_ENCODER all seeds

DIRECTOR'S FIX Q ALERT (overall_dom=1.000) INVESTIGATED:
  overall_dominance_rate=1.000 is the COUNT-of-points-TD-beats-RANDOM metric,
  NOT raw recall or saturation of a bounded metric. Per-point inspection:
    recency_decode_acc ~ 0.73-0.77 (NOT at ceiling; ceiling would be 0.97-1.00)
    ARM_TIME_DECAY composite ~ 0.67-0.74 (well below 1.0 upper bound)
    ARM_RANDOM composite ~ -0.26 to -0.33 (clean floor for baseline)
    td_minus_random_composite ~ 0.94-1.06 (TD wins by ~1.0 composite units)
    pareto_outcome = TD_DOMINATES all 60 points
    saturated=False per point (saturation_frac_total=0.000)
  BIAS-Q verdict: NOT trapped. The 1.000 is discriminator-count not metric-ceiling.
  Mechanism wins all 60/60 points against RANDOM baseline; that's the design.
  Real recall is 0.73-0.77; ample headroom; no saturation.

Cross-seed cv on ARM_TIME_DECAY composite (representative first point of each seed):
  seed_7  = 0.702
  seed_13 = 0.723
  seed_19 = 0.727
  mean = 0.717; sd = 0.013; cv = 0.019 (excellent stability; well below 0.10 CG cv)

Cross-seed cv on td_minus_random_composite (representative first point):
  seed_7  = 0.961
  seed_13 = 1.050
  seed_19 = 1.000
  mean = 1.004; sd = 0.045; cv = 0.045 (very stable)

TIER: CHAIN_GRADE.
  All 3 seeds HP per-cell; all 5 encoders CG-pass all 3 seeds; overall_dom=1.000
  interpreted correctly as discriminator-count NOT metric-saturation (composite
  metrics show 0.67-0.74 recall with 0.94-1.06 lift over RANDOM baseline; ample
  headroom); cross-seed cv on primary discriminator metrics = 0.019-0.045 (well
  below 0.10 CG threshold); arms_differ_per_encoder 5/5 all seeds; positive
  control (RANDOM eviction) at clean floor; saturation_frac=0.000.

  Extends prior ANCHOR4 N=8192 v4 CG atom (commit a17e13be 2026-06-30) to
  N=16384 regime. 5/5 encoders remain competitive at N=16384 (previously
  demonstrated at N=8192). No encoder collapse at 2x-N.

  cert_increment_delta = +1. FOURTH CG of 2026-07-01 (after A_v2 c7feb0c4,
  E_v5 716174a7, Cell D v2 863e14b5).

  SUBSTRATE DESIGN IMPLICATION (chain-grade):
    At N=16384 with capacity_load_ratio in [16, 24, 32, ...], time-decay
    eviction dominates random-eviction on all 60 phase points across 5 encoder
    families. Mechanism scales to N=16384; encoder-agnostic (5/5 families
    competitive). Complements Time-Decay Pareto AUC v2 CG atom from 2026-06-28.

============================================================
(2) Cross-modal binding 3rd modality single-seed MM
============================================================

Cell path: data/exp_substrate_cross_modal_binding_3rd_modality_v1_seed_7/metrics.json

Off-data facts:
  run_mode=full; verdict=HARD_PASS; elapsed_s=41.7; n_seeds_complete=1; single seed.
  cardinality 2700/2700 records; observed_n_units_per_seed observed OK.
  positive_control_recall = 1.000 (cv = 0.000; PASS above 0.7 floor)
  positive_control_met = True
  saturated = False (all_saturated=False)
  near_identical_arms = False (arms differ)
  n_discriminating_points = 17 / 45 (>= 8 required; disc gate PASS)
  n_three_vs_two_ok_points = 20 / 45 (>= 8 required; 3v2 gate PASS)
  Arms: BIND_3MOD / NO_BIND_BASELINE / TWO_MOD_BIND_CONTROL
  Config: 3 mechanisms (HRR_bind3, sum_then_query, position_key_bind3),
    K in [10,50,100,500,1000], N in [2048,4096,8192], V_MOD_A=B=C=2048

TIER: MM_SINGLE_SEED.
  HP verdict per-cell; all pre-reg gates fire (disc >=8, 3v2 >=8, pos_ctrl PASS
  non-saturated); positive control cv=0.000. But single seed only; cross-seed
  replication required for CG per canonical rules.

  Composes with prior cross-modal visual+auditory CG (per Director framing);
  extends to 3rd modality (audio? visual+auditory+text?). Substantive extension
  of cross-modal binding capability.

  cert_increment_delta = 0. Path to CG: dispatch seed_13 + seed_19 for 3-seed
  cross-seed replication.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_ANCHOR4_N16384_CG_and_cross_modal_3rd_MM_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

# ============================================================================
# ATOM 1: ANCHOR4 N=16384 3-seed CHAIN_GRADE
# ============================================================================
atom_ANCHOR4_N16384_CG = {
    "id": (
        "T3/EXP_substrate_anchor4_encoder_family_N16384_gpu_v1_3seed_CHAIN_GRADE_"
        "5_of_5_encoders_COMPETITIVE_all_seeds_binary_bipolar_hrr_real_fhrr_sparse_bipolar_sparse_real_"
        "overall_dominance_rate_1p000_correctly_interpreted_as_discriminator_count_not_metric_saturation_"
        "per_point_recall_0p73_to_0p77_ample_headroom_composite_metrics_0p67_to_0p74_"
        "TD_minus_RANDOM_composite_0p94_to_1p06_across_60_of_60_phase_points_all_seeds_"
        "cross_seed_cv_composite_0p019_td_minus_random_0p045_extends_N_8192_v4_CG_a17e13be_to_N_16384_"
        "4th_CG_of_2026_07_01_2026-07-01"
    ),
    "name": (
        "CHAIN-GRADE ANCHOR4 encoder family N=16384 GPU v1 3-seed FULL: all 5 encoders "
        "(binary_bipolar / hrr_real / fhrr / sparse_bipolar / sparse_real) pass CG at N=16384 "
        "all 3 seeds; overall_dominance_rate=1.000 correctly interpreted as discriminator-count "
        "(TD wins all 60/60 points vs RANDOM baseline; NOT metric saturation; per-point recall "
        "0.73-0.77 with ample headroom); ARM_TIME_DECAY composite 0.67-0.74; ARM_RANDOM composite "
        "-0.26 to -0.33; TD_minus_RANDOM composite 0.94-1.06. Cross-seed cv composite=0.019; "
        "cv td_minus_random=0.045. saturation_frac=0.000 all seeds. Extends prior ANCHOR4 N=8192 "
        "v4 CG atom (a17e13be 2026-06-30) to N=16384 regime. 5/5 encoders remain competitive at "
        "2x N. Director's Fix Q flag investigated and NOT trapped. FOURTH CG of 2026-07-01. CERT +1."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL ANCHOR4 encoder family at N=16384 (extends prior N=8192 v4 CG). Pre-reg: "
        "2026-07-01_substrate_anchor4_encoder_family_N16384_gpu_v1.md.\n"
        "\n"
        "SUBSTRATE-KB OVERLAP CHECK (per new 2026-07-01 discipline): cosine 0.31 top match = "
        "note-chunk 'Axis 1 (load-bearing): encoder family' in research notes; prereg chunks for "
        "N=16384 variants from 2026-06-06 dim_expanded and 2026-06-27 higher_alpha; no prior "
        "Store atom for THIS specific N=16384 3-seed CG cell.\n"
        "\n"
        "OFF-DATA verification: all 3 seeds run_mode=full; verdict=HARD_PASS; elapsed 2.14-3.72s; "
        "cardinality 60/60 units per seed; n_seeds=1 per file (3 separate files).\n"
        "\n"
        "PER-SEED PRIMARY METRICS (identical structure all 3 seeds):\n"
        "  overall_dominance_rate  = 1.000  cross-seed cv = 0.000\n"
        "  overall_net_dominance   = 1.000  cross-seed cv = 0.000\n"
        "  overall_rd_loss_rate    = 0.000  cross-seed cv = 0.000\n"
        "  saturation_frac_total   = 0.000  cross-seed cv = 0.000 (NO saturation)\n"
        "  n_pts_total             = 60     cross-seed cv = 0.000\n"
        "  per_encoder_chain_grade_pass = 5/5 (all encoders) all seeds\n"
        "  encoder_tiers = 5/5 COMPETITIVE_ENCODER all seeds\n"
        "  arms_differ_per_encoder = 5/5 mechanism vs random hashes distinct all seeds\n"
        "\n"
        "DIRECTOR'S FIX Q ALERT INVESTIGATED (overall_dom=1.000):\n"
        "  overall_dominance_rate=1.000 is the COUNT of phase points where TIME_DECAY beats\n"
        "  RANDOM baseline, NOT raw recall or saturation of a bounded metric. Per-point:\n"
        "    recency_decode_acc = 0.73-0.77 (NOT at ceiling; 0.97+ would be saturation)\n"
        "    ARM_TIME_DECAY composite = 0.67-0.74 (well below 1.0 upper bound)\n"
        "    ARM_RANDOM composite = -0.26 to -0.33 (clean floor for RANDOM baseline)\n"
        "    td_minus_random_composite = 0.94-1.06 (TD lift over RANDOM)\n"
        "    pareto_outcome = 'TD_DOMINATES' all 60 points\n"
        "    saturated = False per point (saturation_frac_total=0.000)\n"
        "  BIAS-Q verdict: NOT trapped. The 1.000 is discriminator-count not metric-ceiling.\n"
        "  Mechanism wins all 60/60 points against RANDOM baseline; that's the discriminator's\n"
        "  design. Real recall is 0.73-0.77; ample headroom; no saturation.\n"
        "\n"
        "CROSS-SEED CV ON KEY DISCRIMINATOR METRICS (representative point):\n"
        "  ARM_TIME_DECAY composite: [0.702, 0.723, 0.727] cv=0.019\n"
        "  td_minus_random_composite: [0.961, 1.050, 1.000] cv=0.045\n"
        "  Both cv << 0.10 CG threshold.\n"
        "\n"
        "COMPOSES WITH:\n"
        "  Prior ANCHOR4 N=8192 v4 CG atom (commit a17e13be 2026-06-30; 5/5 encoders CG at N=8192).\n"
        "  Time-Decay Pareto AUC v2 CG (commit 2026-06-28; TD_wins vs RD_wins).\n"
        "  This atom EXTENDS ANCHOR4 to N=16384; mechanism scales; encoder-agnostic at 2x N.\n"
        "\n"
        "TIER: CHAIN_GRADE. cert_increment_delta = +1. FOURTH CG of 2026-07-01.\n"
        "\n"
        "SUBSTRATE DESIGN IMPLICATION (chain-grade):\n"
        "  At N=16384 with capacity_load_ratio in [16, 24, 32], time-decay eviction dominates\n"
        "  random-eviction on all 60 phase points across 5 encoder families. Mechanism scales\n"
        "  to N=16384; encoder-agnostic. Encoder-family axis remains capacity-competitive at\n"
        "  2x N vs prior CG landing at N=8192."
    ),
    "metadata": {
        "provenance_quality": "CERT_CHAIN_GRADE",
        "verdict": "HARD_PASS",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on 3 seeds metrics.json: run_mode=full all 3; "
            "cardinality 60/60 per seed; all 5 encoders CG-pass all seeds; overall_dominance_rate "
            "1.000 correctly interpreted as discriminator-count (per-point recall 0.73-0.77 NOT "
            "at ceiling; ARM_TIME_DECAY composite 0.67-0.74; td_minus_random composite 0.94-1.06); "
            "saturation_frac_total=0.000 all seeds; cross-seed cv composite=0.019; cv "
            "td_minus_random=0.045; arms_differ 5/5 all seeds; Fix Q flag investigated NOT trapped"
        ),
        "regime": {
            "N_dim_input": 16384, "capacity_load_ratios": [16, 24, 32],
            "encoders": ["binary_bipolar","hrr_real","fhrr","sparse_bipolar","sparse_real"],
            "n_phase_points_per_seed": 60, "n_atoms": 1500, "n_days": 365, "n_buckets": 128,
            "noise_sigma": 0.1, "decay_rate_days": 30, "backend": "gpu",
        },
        "per_seed_metrics_paths": {
            "seed_7":  "data/exp_substrate_anchor4_encoder_family_N16384_gpu_v1_seed_7/metrics.json",
            "seed_13": "data/exp_substrate_anchor4_encoder_family_N16384_gpu_v1_seed_13/metrics.json",
            "seed_19": "data/exp_substrate_anchor4_encoder_family_N16384_gpu_v1_seed_19/metrics.json",
        },
        "prereg_path": "preregs/2026-07-01_substrate_anchor4_encoder_family_N16384_gpu_v1.md",
        "overall_dominance_rate_all_seeds": 1.000,
        "overall_dominance_correctly_interpreted_as_discriminator_count_not_metric_saturation": True,
        "director_Fix_Q_alert_investigated_and_NOT_trapped": True,
        "per_encoder_chain_grade_pass_all_seeds": {
            "binary_bipolar": True, "hrr_real": True, "fhrr": True,
            "sparse_bipolar": True, "sparse_real": True,
        },
        "saturation_frac_total_all_seeds": 0.000,
        "cross_seed_cv_composite_ARM_TIME_DECAY": 0.019,
        "cross_seed_cv_td_minus_random_composite": 0.045,
        "per_point_recency_decode_acc_range_ample_headroom": [0.73, 0.77],
        "ARM_TIME_DECAY_composite_range": [0.67, 0.74],
        "ARM_RANDOM_composite_range_clean_floor": [-0.33, -0.26],
        "td_minus_random_composite_range": [0.94, 1.06],
        "extends_prior_ANCHOR4_N_8192_v4_CG_atom_commit": "a17e13be_2026-06-30",
        "composes_with_time_decay_pareto_AUC_v2_CG_2026-06-28": True,
        "cert_increment_delta": 1,
        "cg_promotion_note": "FOURTH CG of 2026-07-01 (after A_v2 c7feb0c4, E_v5 716174a7, Cell D v2 863e14b5)",
        "discipline_tags": [
            "META_RULE_Q_1p000_correctly_interpreted_as_discriminator_count_NOT_metric_saturation",
            "META_RULE_H_cardinality_ok_60_of_60_per_seed",
            "META_RULE_AV_all_5_encoder_CG_gates_fire_cross_seed",
            "META_RULE_AH_arms_differ_5_of_5_encoders_mech_vs_random_hashes_distinct",
            "META_RULE_AN_positive_control_RANDOM_at_clean_floor_negative_composite_-0p26_to_-0p33",
            "extends_ANCHOR4_N_8192_v4_CG_a17e13be_to_N_16384_regime_2x_N_scale",
            "director_Fix_Q_alert_investigated_off_data_and_ruled_NOT_trapped",
            "encoder_agnostic_capability_5_of_5_encoders_competitive_at_N_16384",
            "4th_CG_promotion_of_2026_07_01",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# ATOM 2: Cross-modal 3rd modality single-seed MM
# ============================================================================
atom_cross_modal_3rd_MM = {
    "id": (
        "T3/EXP_substrate_cross_modal_binding_3rd_modality_v1_seed_7_single_seed_FULL_MM_"
        "HP_verdict_per_cell_disc_pts_17_of_45_ge_8_gate_3v2_ok_20_of_45_ge_8_gate_"
        "positive_control_recall_1p000_cv_0p000_ge_0p7_floor_saturated_False_near_identical_False_"
        "extends_cross_modal_visual_auditory_CG_to_3rd_modality_single_seed_prevents_CG_2026-07-01"
    ),
    "name": (
        "MM_SINGLE_SEED cross-modal binding 3rd modality v1: HP verdict per-cell with all "
        "pre-reg gates firing (disc_pts=17/45 >=8, 3v2_ok=20/45 >=8, pos_ctrl_recall=1.000 "
        "cv=0.000 above 0.7 floor, saturated=False, near_identical_arms=False). Substantive "
        "extension of cross-modal binding to 3rd modality. Composes with prior cross-modal "
        "visual+auditory CG. Single-seed prevents CG per canonical rules; path to CG is 3-seed "
        "replication. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Cross-modal binding 3rd modality v1 seed_7 single-seed FULL. Substrate-KB overlap "
        "check: cosine 0.50 top match = note-chunks on cross-modal binding concept (older "
        "research 2026-05-31, 2026-06-08, prereg 2026-06-05 multimodal binding text_kg); no "
        "prior Store atom for this specific 3rd-modality cell.\n"
        "\n"
        "OFF-DATA verification: run_mode=full; verdict=HARD_PASS; elapsed_s=41.7; single seed_7.\n"
        "cardinality: 2700/2700 records; observed_n=expected_n=2700.\n"
        "Config: 3 mechanisms (HRR_bind3, sum_then_query, position_key_bind3); K in [10,50,100,"
        "500,1000]; N in [2048,4096,8192]; V_MOD_A=B=C=2048; V_POS=2048; arms = "
        "BIND_3MOD / NO_BIND_BASELINE / TWO_MOD_BIND_CONTROL.\n"
        "\n"
        "PRE-REG GATES ALL FIRE:\n"
        "  disc_pts = 17/45 (>= 8 required; PASS)\n"
        "  3v2_ok   = 20/45 (>= 8 required; PASS)\n"
        "  positive_control_recall = 1.000 (>= 0.7 floor; PASS)\n"
        "  positive_control_cv = 0.000 (< 0.1 threshold; PASS)\n"
        "  saturated = False (NOT ceiling-saturated)\n"
        "  near_identical_arms = False (arms differ; not degenerate)\n"
        "\n"
        "TIER: MM_SINGLE_SEED. HP per-cell + all gates fire; but single-seed FULL prevents CG.\n"
        "Path to CG: dispatch seed_13 + seed_19 for 3-seed cross-seed replication.\n"
        "\n"
        "COMPOSES WITH: prior cross-modal visual+auditory CG (per Director framing). This atom\n"
        "extends the cross-modal capability to a 3rd modality; substantive capability extension.\n"
        "\n"
        "cert_increment_delta = 0 (single-seed prevents CG per canonical rules)."
    ),
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM_SINGLE_SEED",
        "verdict": "HARD_PASS_single_seed_MM_per_canonical_rules",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA verification via .venv python on metrics.json: run_mode=full; verdict=HARD_PASS; "
            "cardinality 2700/2700; disc_pts=17/45>=8; 3v2_ok=20/45>=8; pos_ctrl_recall=1.0 cv=0.0 "
            "above 0.7 floor; saturated=False; near_identical_arms=False; single seed_7 only; "
            "single-seed prevents CG"
        ),
        "regime": {
            "modalities": ["MOD_A", "MOD_B", "MOD_C"],
            "V_MOD_A": 2048, "V_MOD_B": 2048, "V_MOD_C": 2048, "V_POS": 2048,
            "N_sweep": [2048, 4096, 8192], "K_sweep": [10, 50, 100, 500, 1000],
            "mechanisms": ["HRR_bind3", "sum_then_query", "position_key_bind3"],
            "arms": ["BIND_3MOD", "NO_BIND_BASELINE", "TWO_MOD_BIND_CONTROL"],
        },
        "metrics_path": "data/exp_substrate_cross_modal_binding_3rd_modality_v1_seed_7/metrics.json",
        "prereg_gates": {
            "disc_pts_ge_8": {"value": 17, "total": 45, "passed": True},
            "3v2_ok_ge_8": {"value": 20, "total": 45, "passed": True},
            "positive_control_recall_ge_0p7": {"value": 1.000, "cv": 0.000, "passed": True},
            "saturated_False": True,
            "near_identical_arms_False": True,
        },
        "single_seed_prevents_CG_needs_3_seed_replication": True,
        "composes_with_prior_cross_modal_visual_auditory_CG_per_director_framing": True,
        "cert_increment_delta": 0,
        "discipline_tags": [
            "MM_single_seed_per_canonical_rules_HP_verdict_all_gates_fire",
            "substrate_KB_query_first_confirms_no_prior_atom",
            "composes_with_prior_cross_modal_visual_auditory_CG_extends_to_3rd_modality",
            "META_RULE_H_cardinality_ok_2700_of_2700_records",
            "META_RULE_AV_all_prereg_gates_fire_disc_ge_8_3v2_ge_8_posctrl_ge_0p7",
            "META_RULE_AH_positive_control_1p000_non_saturated_near_identical_arms_False",
            "path_to_CG_dispatch_seed_13_and_seed_19_for_3_seed_replication",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================================
# CERT LEDGER ROWS
# ============================================================================
_t0 = time.time()

ledger_ANCHOR4_N16384_CG = {
    "ts": _t0,
    "op": "cert_ruling_promotion_chain_grade",
    "atom_id": f"math::{atom_ANCHOR4_N16384_CG['id']}",
    "cert_status": "chain_grade",
    "cert_class": "pre_reg_pass_ANCHOR4_encoder_family_extended_to_N_16384",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "CHAIN_GRADE_3seed_HP_all_5_encoders_COMPETITIVE_all_seeds_at_N_16384_"
        "binary_hrr_fhrr_sparse_bipolar_sparse_real_overall_dom_1p000_discriminator_count_NOT_saturation_"
        "per_point_recall_0p73_to_0p77_ample_headroom_composite_0p67_to_0p74_td_minus_random_0p94_to_1p06_"
        "cross_seed_cv_composite_0p019_td_minus_random_0p045_all_60_of_60_pts_all_seeds_TD_DOMINATES_"
        "director_Fix_Q_investigated_NOT_trapped_extends_N_8192_v4_CG_a17e13be_4th_CG_of_2026_07_01"
    ),
    "cert_increment_delta": 1,
    "cv": 0.019,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_anchor4_encoder_family_N16384_gpu_v1_seed_{7,13,19}/metrics.json",
        "prereg_path": "preregs/2026-07-01_substrate_anchor4_encoder_family_N16384_gpu_v1.md",
        "extends_prior_ANCHOR4_N_8192_v4_CG_commit": "a17e13be_2026-06-30",
        "atom_qualified_id": f"math::{atom_ANCHOR4_N16384_CG['id']}",
    },
    "supersedes": None,  # extends N=8192 v4 CG; does not supersede; complementary
    "note": (
        "ANCHOR4_encoder_family_N_16384_3seed_CHAIN_GRADE_4th_CG_of_2026_07_01_"
        "5_of_5_encoders_binary_hrr_fhrr_sparse_bipolar_sparse_real_all_COMPETITIVE_all_seeds_"
        "overall_dominance_rate_1p000_correctly_interpreted_discriminator_count_TD_wins_all_60_of_60_vs_RANDOM_baseline_"
        "per_point_recency_decode_acc_0p73_to_0p77_NOT_at_ceiling_ample_headroom_"
        "ARM_TIME_DECAY_composite_0p67_to_0p74_ARM_RANDOM_composite_neg_0p26_to_neg_0p33_clean_floor_"
        "td_minus_random_composite_0p94_to_1p06_saturation_frac_0p000_all_seeds_"
        "cross_seed_cv_composite_0p019_td_minus_random_0p045_both_well_below_0p10_CG_threshold_"
        "arms_differ_per_encoder_5_of_5_mech_vs_random_hashes_distinct_all_seeds_"
        "director_Fix_Q_alert_investigated_off_data_and_ruled_NOT_trapped_1p000_is_discriminator_count_not_metric_saturation_"
        "extends_prior_ANCHOR4_N_8192_v4_CG_a17e13be_2026_06_30_to_N_16384_regime_2x_N_scale_"
        "encoder_agnostic_capability_all_5_families_competitive_at_N_16384_"
        "composes_with_time_decay_pareto_AUC_v2_CG_2026_06_28_"
        "hdlab_encoder_family_agnostic_at_N_16384_confirmed"
    ),
}

ledger_cross_modal_3rd_MM = {
    "ts": _t0 + 0.001,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_cross_modal_3rd_MM['id']}",
    "cert_status": "measured_mechanism_single_seed",
    "cert_class": "MM_single_seed_HP_verdict_all_prereg_gates_fire_but_cross_seed_replication_needed",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "MM_single_seed_HP_cross_modal_3rd_modality_disc_pts_17_of_45_ge_8_3v2_ok_20_of_45_ge_8_"
        "positive_control_recall_1p0_cv_0p0_above_0p7_floor_saturated_False_near_identical_False_"
        "all_prereg_gates_fire_but_single_seed_prevents_CG_extends_cross_modal_visual_auditory_CG_to_3rd_modality"
    ),
    "cert_increment_delta": 0,
    "cv": 0.000,  # positive control cv
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_cross_modal_binding_3rd_modality_v1_seed_7/metrics.json",
        "atom_qualified_id": f"math::{atom_cross_modal_3rd_MM['id']}",
    },
    "supersedes": None,
    "note": (
        "cross_modal_binding_3rd_modality_v1_seed_7_single_seed_MM_HP_verdict_"
        "disc_pts_17_of_45_ge_8_gate_3v2_ok_20_of_45_ge_8_gate_"
        "positive_control_recall_1p000_cv_0p000_above_0p7_floor_saturated_False_near_identical_False_"
        "all_prereg_gates_fire_but_single_seed_only_prevents_CG_per_canonical_rules_"
        "composes_with_prior_cross_modal_visual_auditory_CG_extends_to_3rd_modality_"
        "substrate_KB_query_first_confirms_no_prior_Store_atom_only_note_chunk_concept_references_"
        "path_to_CG_dispatch_seed_13_and_seed_19_for_3_seed_cross_seed_replication"
    ),
}


# ============================================================================
# A5 write protocol
# ============================================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    print(f"[A5] {label}: path={path}")
    assert path.exists()

    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    for i, ln in enumerate(pre_lines):
        if not ln.strip(): continue
        try: json.loads(ln)
        except Exception as e: raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row: assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row: assert parsed_back.get("atom_id") == new_row.get("atom_id")

    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text); f.flush(); os.fsync(f.fileno())
    import time as _time
    for _attempt in range(10):
        try: os.replace(str(tmp_path), str(path)); break
        except PermissionError:
            if _attempt == 9: raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1

    tail = json.loads(post_lines[-1])
    if "id" in new_row: assert tail["id"] == new_row["id"]
    if "atom_id" in new_row: assert tail["atom_id"] == new_row["atom_id"]

    for i, ln in enumerate(post_lines):
        if not ln.strip(): continue
        try: json.loads(ln)
        except Exception as e: raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_ANCHOR4_N16384_CG,       "math/atoms (ANCHOR4 N=16384 3-seed CHAIN_GRADE)")
    append_jsonl_a5(MATH_ATOMS, atom_cross_modal_3rd_MM,      "math/atoms (cross-modal 3rd modality single-seed MM)")
    append_jsonl_a5(CERT_LEDGER, ledger_ANCHOR4_N16384_CG,    "cert_ledger (ANCHOR4 N=16384 CG +1; 4th CG of 2026-07-01)")
    append_jsonl_a5(CERT_LEDGER, ledger_cross_modal_3rd_MM,   "cert_ledger (cross-modal 3rd MM)")
    print(f"[A5] DONE OK")
    print(f"[A5] ANCHOR4 N=16384 3-seed: CHAIN_GRADE +1 (4th CG of 2026-07-01)")
    print(f"[A5] Cross-modal 3rd modality single-seed: MM (needs 3-seed for CG)")
    print(f"[A5] CERT delta = +1")


if __name__ == "__main__":
    main()
