"""
A5-gated atomize: partition_oracle_v5_hardened_FULL_seed_13_v1 MIDDLE_BAND
                  + cross-seed aggregation atom (2-of-3 landed).

Verdict: MIDDLE_BAND. Cert class: mechanism_characterization. CERT delta = 0.

OFF-DATA recompute (verify-OFF-DATA, NOT verdict_msg):
  A=0.3650 B=0.8250 C=0.9250 D=0.6100 E=0.0000
  lift_B_A=0.4600 (>= 0.20) PASS
  lift_B_E=0.8250 (>= 0.30) PASS
  ARM_B in HP_band[0.50, 0.95]                  PASS
  saturation=False (max C=0.925 < 0.95)          PASS
  arms_distinct=True (5 unique SHA-256)          PASS
  cardinality_ok=True (5 arms observed)          PASS
  baseline_rail_ok=True (A=0.365 in [0.30,0.70]) PASS

Per-seed verdict per metrics.json = MIDDLE_BAND solely because per-cell cv is NaN
(only 1 seed in this chunk). HP_CV gate is RELAXED at per-cell tier (per prereg
CHUNKED-ARCHITECTURE annotation lines 209-214) and ENFORCED at cross-seed
aggregation tier. All 7 single-seed HP gates PASS for seed_13.

CROSS-SEED AGGREGATION (2 of 3 landed; seed_11 + seed_13):
  ARM_A: [0.295, 0.365] mean=0.330 sd=0.035 cv=0.106
  ARM_B: [0.835, 0.825] mean=0.830 sd=0.005 cv=0.006 (HP_cv_max=0.15: PASS by huge margin)
  baseline_rail_ok: seed_11=False (0.005 below floor; within binomial std) | seed_13=True (clearly in rail)
  2-of-3 status: 1 rail_ok + 1 marginal-breach-within-noise + 1 pending (seed_19)

Per seed_11 atom promotion criterion: "if 2 of 3 seeds satisfy baseline rail +
cv<0.15 with B-in-band, promote to chain-grade Barrier 1 break."
  - 2 seeds landed; both have B-in-band; cv_B=0.006 <<0.15; 1/2 strict rail-pass
  - If seed_19 lands rail-pass: 2/3 rail_ok = promotion trigger fires
  - If seed_19 lands rail-breach: USER/research consensus needed on rail interpretation
    (seed_11 breach 0.005 is binomial-noise; consistent breach pattern suggests
    rail floor itself may need re-derivation)

A5 protocol per write:
  1. Read pre-write line counts; build atom + ledger row in memory
  2. Append to math/atoms.jsonl via tmp -> os.replace (atomic)
  3. Append to meta/cert_ledger.jsonl via tmp -> os.replace
  4. Verify-load: count delta == +1 each; tail-line parses as JSON; round-trip ID match

Anchors:
  - metrics: data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_13_v1/metrics.json
  - prereg:  preregs/2026-06-28_substrate_multihop_partition_oracle_v5_hardened_v1.md
  - cell:    experiments/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_13_v1.py
  - sibling atom (seed_11): math::T3/EXP_partition_oracle_goal_conditioning_barrier_1_MIDDLE_BAND_at_FULL_2026-06-28
"""

import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

METRICS_PATH = "data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_13_v1/metrics.json"
PREREG_PATH = "preregs/2026-06-28_substrate_multihop_partition_oracle_v5_hardened_v1.md"
CELL_PATH = "experiments/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_13_v1.py"
SIBLING_SEED11_ATOM = "math::T3/EXP_partition_oracle_goal_conditioning_barrier_1_MIDDLE_BAND_at_FULL_2026-06-28"

ATOMIZED_BY = "skunkworks_atomize_partition_oracle_FULL_seed13_MB_2026-06-28"
ATOMIZED_DATE = "2026-06-28"
CELL_COMMIT = "47268ec5"  # latest staging commit (HEAD at atomization time)


# ============================================================
# ATOM 1: seed_13 per-cell record (math, T3, MIDDLE_BAND, mechanism_characterization)
# ============================================================
atom_seed13 = {
    "id": "T3/EXP_partition_oracle_goal_conditioning_barrier_1_FULL_seed_13_MIDDLE_BAND_baseline_in_rail_2026-06-28",
    "name": (
        "Partition-oracle goal-conditioning v5-hardened FULL seed_13 -- MIDDLE_BAND "
        "(all 7 single-seed HP gates PASS including baseline-in-rail; per-cell cv NaN due to chunked single-seed; "
        "promotion-VET gated on cross-seed aggregation tier per prereg)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Barrier 1 (compositional reasoning depth) test of partition-oracle goal-conditioning, seed_13 of 3. "
        "Single seed (seed=13) FULL at N=8192 V_C=4000 V_P=10 depth=15 n_chains_test=200. "
        "5-arm discriminator (BASELINE_A / ORACLE_B_psz800 / ORACLE_C_psz400 / ORACLE_D_psz2000 / RANDOM_E). "
        "OFF-DATA recompute: A=0.365 B=0.825 C=0.925 D=0.610 E=0.000; "
        "lift_B_A=0.460 (>=0.20 PASS); lift_B_E=0.825 (>=0.30 PASS); ARM_B in HP band [0.50, 0.95] PASS; "
        "saturation=False (max C=0.925 < 0.95) PASS; arms_distinct=True (5 unique SHA-256); "
        "cardinality_ok=True (5 arms); baseline_rail_ok=True (A=0.365 clearly in [0.30,0.70]) PASS. "
        "ALL 7 single-seed HP gates PASS. MIDDLE_BAND verdict comes solely from per-cell cv=NaN "
        "(only 1 seed in this chunk; per prereg CHUNKED-ARCHITECTURE annotation lines 209-214, "
        "cv gate is RELAXED at per-cell tier and ENFORCED at cross-seed aggregation tier). "
        "Versus seed_11 (sibling): A 0.295->0.365 (recovers rail; +0.070); B 0.835->0.825 (essentially unchanged; -0.010); "
        "lift_B_A 0.540->0.460 (still well above 0.20 floor). Mechanism (partition-oracle goal-conditioning narrows "
        "search via psz_B=800 5-partition oracle) confirmed at 2 independent seeds with very low cv_B=0.006. "
        "Cross-seed aggregation atom companion records 2-of-3 state; seed_19 pending local CPU. "
        "Chain-grade promotion gate (per seed_11 atom promotion_recommendation): 2 of 3 seeds satisfy baseline rail "
        "AND cross-seed cv < 0.15 AND ARM_B in HP band. Current state: cv_B=0.006 PASS by huge margin; "
        "ARM_B in HP for both seeds; 1/2 strict rail-pass (seed_11 breach 0.005 within binomial std). "
        "If seed_19 baseline-in-rail: 2/3 rail_ok fires Barrier 1 chain-grade promotion. "
        "Per feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28: MB does NOT trigger closure; "
        "mechanism INTACT and characterized. Per feedback_test_design_failure_diagnosis_and_hardening_USER_2026-06-28: "
        "seed_11 baseline drift was within binomial noise, not test-design failure."
    ),
    "aliases": [
        "partition_oracle_goal_conditioning_barrier_1_FULL_seed_13_MIDDLE_BAND_baseline_in_rail_2026-06-28",
        "partition_oracle_v5_hardened_FULL_seed_13_MB_baseline_in_rail",
        "barrier_1_compositional_reasoning_depth_15_seed_13_all_7_HP_gates_pass",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "middle_band",
        "cert_class": "mechanism_characterization",
        "verdict": "MIDDLE_BAND",
        "verdict_subtype": "PARTIAL_MECHANISM_AT_DEPTH15_PER_CELL_CV_NAN_CHUNKED_SINGLE_SEED",
        "cell_commit": CELL_COMMIT,
        "cell_path": CELL_PATH,
        "prereg_path": PREREG_PATH,
        "metrics_path": METRICS_PATH,
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on metrics.json per_seed[0]: "
            "A=0.365 B=0.825 C=0.925 D=0.610 E=0.000; lift_B_A=0.460 lift_B_E=0.825; "
            "B in HP band[0.50,0.95] PASS; A in rail[0.30,0.70] PASS; saturation max=0.925 < 0.95 PASS; "
            "arms_distinct SHA-256 unique count = 5 PASS; cardinality 5/5 PASS; "
            "ALL 7 single-seed HP gates PASS; per-cell verdict MIDDLE_BAND driven by cv=NaN only "
            "(single seed in chunked cell; cv enforced at cross-seed aggregation tier per prereg)"
        ),
        "n_seeds_run": 1,
        "n_seeds_planned_total": 3,
        "seed_index_in_aggregation": 2,
        "seeds_pending": [19],
        "seeds_pending_queue": "local_cpu_direct_background",
        "sibling_atoms": [SIBLING_SEED11_ATOM],
        "regime": {
            "N": 8192,
            "V_C": 4000,
            "V_P": 10,
            "depth": 15,
            "n_chains_train": 200,
            "n_chains_test": 200,
            "encoder": "SUBSTRATE_NATIVE_BIPOLAR",
            "n_partitions_B": 5,
            "part_size_B": 800,
            "n_partitions_C": 10,
            "part_size_C": 400,
            "n_partitions_D": 2,
            "part_size_D": 2000,
        },
        "per_arm_top1": {
            "A_baseline_full_V_C": 0.365,
            "B_oracle_part_5_psz_800": 0.825,
            "C_oracle_part_10_psz_400": 0.925,
            "D_oracle_part_2_psz_2000": 0.610,
            "E_no_oracle_random_part_5": 0.000,
        },
        "lifts": {
            "lift_B_A": 0.460,
            "lift_B_E": 0.825,
            "lift_C_A": 0.560,
            "lift_D_A": 0.245,
        },
        "elapsed_s": 374.4,
        "gates_evaluated": {
            "B_in_HP_band_0p50_0p95": True,
            "lift_B_A_ge_0p20": True,
            "lift_B_E_ge_0p30": True,
            "saturation_lt_0p95": True,
            "arms_distinct_sha256_5_unique": True,
            "cardinality_ok_5_arms_5_expected": True,
            "baseline_A_in_rail_0p30_0p70": True,
            "cv_lt_0p15_cross_seed": "PENDING_seed_19_aggregation_NaN_at_single_seed_tier",
        },
        "vs_seed_11_delta": {
            "A_seed11": 0.295,
            "A_seed13": 0.365,
            "A_delta": 0.070,
            "B_seed11": 0.835,
            "B_seed13": 0.825,
            "B_delta": -0.010,
            "lift_seed11": 0.540,
            "lift_seed13": 0.460,
            "rail_breach_seed11": True,
            "rail_breach_seed13": False,
            "note": "seed_13 recovers baseline rail; ARM_B essentially unchanged across seeds (cv_B=0.006)",
        },
        "promotion_recommendation": (
            "WAIT for seed_19 to land (local CPU direct background; ETA ~6 min from dispatch). "
            "Cross-seed aggregation atom (companion) tracks 2-of-3 state. "
            "If seed_19 baseline_rail_ok=True: 2/3 rail_ok satisfied + cv_B already << 0.15 + B-in-band 2/2 "
            "= Barrier 1 CHAIN-GRADE PROMOTION fires (CERT +1). "
            "If seed_19 baseline_rail_ok=False but A within ~0.005 of rail (binomial std): "
            "USER/research consensus needed on whether rail floor 0.30 is conservative vs strict; "
            "MIDDLE_BAND likely sustained as honest characterization."
        ),
        "barrier_1_status": "MIDDLE_BAND_at_seed_13_individual_promotion_VET_pending_seed_19_cross_seed_aggregation",
        "capability_closure_status": "DO_NOT_CLOSE_partition_oracle_direction_mechanism_INTACT_2_of_2_seeds",
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AG",
            "META_RULE_AH", "META_RULE_AL", "META_RULE_AN", "META_RULE_H",
            "META_RULE_G", "BIAS-Q", "BIAS-N", "BIAS-S",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
            "feedback_test_design_failure_diagnosis_and_hardening_USER_2026-06-28",
            "chunked_architecture_per_cell_cv_relaxed_aggregation_cv_enforced",
        ],
        "next_actions": [
            "wait_for_seed_19_landing_in_local_cpu_direct_background_eta_6min",
            "re_VET_at_3_seed_aggregation_via_cross_seed_aggregation_atom_update",
            "if_seed_19_rail_ok_promote_barrier_1_chain_grade_CERT_plus_1",
            "if_seed_19_rail_breach_USER_research_consensus_on_rail_floor_interpretation",
        ],
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# ATOM 2: cross-seed aggregation snapshot (math, T3, partial_aggregation)
# ============================================================
atom_aggregation = {
    "id": "T3/EXP_partition_oracle_goal_conditioning_barrier_1_CROSS_SEED_AGG_2of3_landed_2026-06-28",
    "name": (
        "Partition-oracle goal-conditioning Barrier 1 -- cross-seed aggregation 2-of-3 landed "
        "(seed_11 + seed_13; seed_19 pending; cv_B=0.006; 1/2 strict rail_ok; promotion gate live)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_aggregation_record",
    "description": (
        "Cross-seed aggregation snapshot for partition-oracle goal-conditioning Barrier 1 break, "
        "at 2-of-3 seeds landed (seed_11 + seed_13; seed_19 pending local CPU). "
        "Per-seed atoms: seed_11=math::T3/EXP_partition_oracle_goal_conditioning_barrier_1_MIDDLE_BAND_at_FULL_2026-06-28; "
        "seed_13=math::T3/EXP_partition_oracle_goal_conditioning_barrier_1_FULL_seed_13_MIDDLE_BAND_baseline_in_rail_2026-06-28. "
        "ARM_A (baseline): values [0.295, 0.365] mean=0.330 sd=0.035 cv=0.106 -- mean IN rail [0.30,0.70]; "
        "1/2 strict per-seed rail_ok (seed_11 breach 0.005 within binomial std sqrt(0.295*0.705/200)=0.032). "
        "ARM_B (oracle): values [0.835, 0.825] mean=0.830 sd=0.005 cv=0.006 -- DEEPLY in HP band [0.50,0.95]; "
        "cv_B=0.006 << HP_CV_MAX=0.15 by 25x margin; mechanism reproduces across seeds at very high reliability. "
        "ARM_E (random control): values [0.000, 0.000] mean=0.000 -- clean floor both seeds; "
        "lift_B_E mean=0.830 (>= 0.30 by 2.8x). "
        "PROMOTION GATE (per seed_11 atom promotion_recommendation): "
        "'2 of 3 seeds satisfy baseline rail + cv<0.15 with B-in-band -> chain-grade Barrier 1 break'. "
        "Current state: cv<0.15 satisfied (cv_B=0.006); B-in-band satisfied (2/2); rail status 1/2 strict (50%). "
        "If seed_19 baseline_rail_ok=True: 2/3 rail_ok = PROMOTE chain-grade (CERT +1). "
        "If seed_19 baseline_rail_ok=False: 1/3 rail_ok = MIDDLE_BAND sustained pending rail-floor re-derivation. "
        "This atom will be SUPERSEDED by a 3-of-3 aggregation atom after seed_19 lands."
    ),
    "aliases": [
        "partition_oracle_barrier_1_cross_seed_2of3_landed_2026-06-28",
        "partition_oracle_v5_hardened_FULL_aggregation_partial_2of3",
        "barrier_1_promotion_gate_live_pending_seed_19",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "partial_aggregation",
        "cert_class": "aggregation_snapshot",
        "verdict": "MIDDLE_BAND_AGGREGATION_PENDING_SEED_19",
        "verdict_subtype": "2_OF_3_LANDED_PROMOTION_GATE_LIVE",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python: seeds_A=[0.295,0.365] mean=0.330 sd=0.035 cv=0.106; "
            "seeds_B=[0.835,0.825] mean=0.830 sd=0.005 cv=0.006; cv_B << HP_CV_MAX=0.15 by 25x"
        ),
        "n_seeds_landed": 2,
        "n_seeds_planned_total": 3,
        "seeds_landed": [11, 13],
        "seeds_pending": [19],
        "seeds_pending_dispatch": {
            "seed_19": {
                "queue": "local_cpu_direct_background",
                "eta_minutes": 6,
                "dispatched_by": "research_director_2026-06-28",
            }
        },
        "per_seed_atom_ids": {
            "seed_11": SIBLING_SEED11_ATOM,
            "seed_13": f"math::{atom_seed13['id']}",
            "seed_19": "PENDING",
        },
        "per_seed_metrics_paths": {
            "seed_11": "data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1/metrics.json",
            "seed_13": METRICS_PATH,
            "seed_19": "data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_19_v1/metrics.json (PENDING)",
        },
        "cross_seed_stats": {
            "arm_A_baseline": {
                "values": [0.295, 0.365],
                "mean": 0.330,
                "sd": 0.035,
                "cv": 0.106,
                "mean_in_rail_0p30_0p70": True,
                "per_seed_rail_ok": [False, True],
                "strict_rail_pass_fraction": 0.5,
            },
            "arm_B_oracle": {
                "values": [0.835, 0.825],
                "mean": 0.830,
                "sd": 0.005,
                "cv": 0.006,
                "mean_in_HP_band_0p50_0p95": True,
                "per_seed_in_band": [True, True],
                "in_band_fraction": 1.0,
                "cv_lt_HP_CV_MAX_0p15": True,
                "cv_margin_factor_vs_threshold": 25.0,
            },
            "arm_E_random": {
                "values": [0.000, 0.000],
                "mean": 0.000,
                "clean_floor": True,
            },
            "lift_B_A": {
                "values": [0.540, 0.460],
                "mean": 0.500,
                "all_ge_0p20": True,
            },
            "lift_B_E": {
                "values": [0.835, 0.825],
                "mean": 0.830,
                "all_ge_0p30": True,
            },
        },
        "promotion_gate_evaluation": {
            "gate_text": "2 of 3 seeds satisfy baseline rail + cv<0.15 with B-in-band -> chain-grade Barrier 1 break",
            "current_2of3_status": {
                "rail_ok": "1_of_2_strict_50pct_pending_seed_19",
                "cv_lt_0p15": "PASS_cv_B_0p006_by_25x_margin",
                "B_in_band": "PASS_2_of_2",
            },
            "promotion_decision_tree": {
                "if_seed_19_rail_ok": "PROMOTE_chain_grade_CERT_plus_1_Barrier_1_BROKEN",
                "if_seed_19_rail_breach_within_noise": "USER_research_consensus_on_rail_floor_interpretation",
                "if_seed_19_rail_breach_large_or_B_drops": "MIDDLE_BAND_sustained_iterate_seeds_or_regime",
            },
        },
        "barrier_1_status": "PROMOTION_GATE_LIVE_2_OF_3_AGGREGATION_PENDING_SEED_19",
        "capability_closure_status": "DO_NOT_CLOSE_mechanism_INTACT_at_2_of_2_landed_with_cv_B_0p006",
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AL",
            "META_RULE_AN", "META_RULE_H", "BIAS-N", "BIAS-S",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
            "feedback_test_design_failure_diagnosis_and_hardening_USER_2026-06-28",
        ],
        "next_actions": [
            "wait_for_seed_19_metrics_json_landing_ETA_6min",
            "supersede_this_atom_with_3of3_aggregation_atom_post_seed_19_landing",
            "if_promote: file_chain_grade_barrier_1_break_atom_CERT_increment_plus_1",
        ],
        "superseded_by": "PENDING_3_of_3_aggregation_atom_post_seed_19",
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# CERT LEDGER ROW (seed_13 per-cell; op=cert_ruling; delta=0)
# ============================================================
ledger_row_seed13 = {
    "ts": time.time(),
    "op": "cert_ruling",
    "atom_id": f"math::{atom_seed13['id']}",
    "cert_status": "middle_band",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "MIDDLE_BAND_single_seed_FULL_A0p365_B0p825_lift_0p460_ALL_7_HP_gates_PASS_"
        "including_baseline_rail_per_cell_cv_NaN_chunked_relaxed_at_per_cell_tier_"
        "cross_seed_cv_B_0p006_pending_seed_19_for_chain_grade_promotion_decision"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path": METRICS_PATH,
        "prereg_path": PREREG_PATH,
        "cell_path": CELL_PATH,
        "atom_qualified_id": f"math::{atom_seed13['id']}",
        "sibling_seed_11_atom": SIBLING_SEED11_ATOM,
        "aggregation_atom": f"math::{atom_aggregation['id']}",
    },
    "supersedes": None,
    "note": (
        "partition_oracle_v5_hardened_FULL_seed_13_MIDDLE_BAND_all_7_single_seed_HP_gates_PASS_"
        "baseline_in_rail_A_0p365_recovers_from_seed_11_breach_ARM_B_essentially_unchanged_cv_B_0p006_"
        "mechanism_INTACT_2_of_2_landed_seed_19_pending_local_cpu_promotion_gate_live"
    ),
}


# ============================================================
# CERT LEDGER ROW (aggregation atom; op=cert_ruling; delta=0)
# ============================================================
ledger_row_aggregation = {
    "ts": time.time() + 0.001,  # small offset so post-load sort is deterministic
    "op": "cert_ruling",
    "atom_id": f"math::{atom_aggregation['id']}",
    "cert_status": "partial_aggregation",
    "cert_class": "aggregation_snapshot",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "CROSS_SEED_AGGREGATION_2_OF_3_LANDED_seeds_11_13_cv_B_0p006_25x_margin_"
        "B_in_band_2_of_2_rail_ok_1_of_2_strict_promotion_gate_LIVE_pending_seed_19_"
        "if_seed_19_rail_ok_PROMOTE_chain_grade_Barrier_1_BROKEN_CERT_plus_1"
    ),
    "cert_increment_delta": 0,
    "cv": 0.006,
    "referent_pointer": {
        "atom_qualified_id": f"math::{atom_aggregation['id']}",
        "per_seed_atoms": {
            "seed_11": SIBLING_SEED11_ATOM,
            "seed_13": f"math::{atom_seed13['id']}",
            "seed_19": "PENDING",
        },
        "prereg_path": PREREG_PATH,
    },
    "supersedes": None,
    "note": (
        "cross_seed_aggregation_2of3_landed_partition_oracle_barrier_1_promotion_gate_LIVE_"
        "cv_B_0p006_HP_band_2of2_rail_1of2_strict_pending_seed_19_decision_tree_locked_"
        "supersede_with_3of3_atom_post_seed_19_landing"
    ),
}


# ============================================================
# A5 WRITE PROTOCOL
# ============================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    """Atomic append with verify-load + integrity-check."""
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"target does not exist: {path}"

    # PRE: read full file + count
    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    # Validate every pre-line parses (integrity)
    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    # Build new content
    new_line = json.dumps(new_row, ensure_ascii=True)
    # Round-trip validate the new row
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id"), "round-trip id mismatch"
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id"), "round-trip atom_id mismatch"

    out_lines = pre_lines + [new_line]
    out_text = "\n".join(out_lines) + "\n"

    # tmp -> os.replace (atomic)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp_path), str(path))

    # POST: verify-load
    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1, f"count delta mismatch: {pre_count} -> {post_count}"

    # Tail must parse + match
    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"], f"tail id mismatch: {tail.get('id')} vs {new_row['id']}"
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"], f"tail atom_id mismatch"

    # Re-validate every line parses
    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK (atomic append + verify-load + integrity-check)")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    print(f"[A5] atom_seed13_id = math::{atom_seed13['id']}")
    print(f"[A5] atom_aggregation_id = math::{atom_aggregation['id']}")
    print(f"[A5] ledger seed13: cert_status={ledger_row_seed13['cert_status']} delta={ledger_row_seed13['cert_increment_delta']}")
    print(f"[A5] ledger aggregation: cert_status={ledger_row_aggregation['cert_status']} delta={ledger_row_aggregation['cert_increment_delta']}")

    # SERIALIZE: write atom 1 first, then atom 2; then ledger 1, then ledger 2
    # (Substrate Store partition writes NOT concurrency-safe per discipline.)
    append_jsonl_a5(MATH_ATOMS, atom_seed13, "math/atoms.jsonl (seed_13)")
    append_jsonl_a5(MATH_ATOMS, atom_aggregation, "math/atoms.jsonl (aggregation)")
    append_jsonl_a5(CERT_LEDGER, ledger_row_seed13, "meta/cert_ledger.jsonl (seed_13)")
    append_jsonl_a5(CERT_LEDGER, ledger_row_aggregation, "meta/cert_ledger.jsonl (aggregation)")

    print(f"[A5] DONE OK; CERT delta = 0 (both atoms mechanism_characterization / aggregation_snapshot)")
    print(f"[A5] Barrier 1 promotion gate LIVE pending seed_19 landing")


if __name__ == "__main__":
    main()
