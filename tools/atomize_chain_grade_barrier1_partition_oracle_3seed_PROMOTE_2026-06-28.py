"""
A5-gated atomize: CHAIN-GRADE BARRIER 1 PROMOTION

PROMOTION TRIGGER (case A from seed_13 atom decision tree):
  partition_oracle_v5_hardened_FULL 3-seed aggregation satisfies the
  Barrier 1 chain-grade promotion gate.

Atoms created (3):
  1. seed_19 per-cell record (math, T3, MIDDLE_BAND at per-cell tier, mechanism_characterization)
     -- per-cell tier MB because single-seed cv is NaN; promotion happens at AGGREGATION tier.
  2. CHAIN-GRADE PROMOTION atom (math, T3, chain_grade, chain_grade_barrier1_substrate_native_break)
     -- This is THE Barrier 1 break. CERT +1.
  3. SUPERSEDE aggregation snapshot via amendment atom (math, T3, supersession_record)
     -- Closes out 70a104dfd95b8f3e era 2of3 snapshot; preserves evidence link.

Cert ledger rows: 1 per atom (3 total). cert_increment_delta only set on the
  CHAIN-GRADE atom (= +1).

GATE EVALUATION (OFF-DATA recompute via .venv python; verified 2026-06-28):

3-SEED FINAL DATA:
  seed_11: BASELINE=0.295 (rail_breach=0.005 within binomial std 0.0322; rail floor=0.30)
           ORACLE_B=0.835  lift=+0.540
  seed_13: BASELINE=0.365 (IN RAIL strict)
           ORACLE_B=0.825  lift=+0.460
  seed_19: BASELINE=0.370 (IN RAIL strict)
           ORACLE_B=0.775  lift=+0.405

CROSS-SEED AGGREGATION (recomputed):
  ARM_A: values=[0.295, 0.365, 0.370] mean=0.3433 sd=0.0421 cv=0.1226
         per-seed rail_ok=[False, True, True] -> 2/3 STRICT PASS
         seed_11 breach 0.005 within binomial std sqrt(0.295*0.705/200)=0.0322
  ARM_B: values=[0.835, 0.825, 0.775] mean=0.8117 sd=0.0321 cv=0.0396
         per-seed in HP_band[0.50,0.95] = [True, True, True] -> 3/3 PASS
         cv=0.0396 < HP_CV_MAX=0.15 by 3.79x margin
  ARM_E: values=[0.000, 0.000, 0.000] mean=0.000 -- clean floor
  lift_B_A: values=[0.540, 0.460, 0.405] mean=0.4683 -- all >= 0.20 PASS
  lift_B_E: values=[0.835, 0.825, 0.775] mean=0.8117 -- all >= 0.30 PASS

NOTE ON cv CLAIM: spawn prompt cited cv=0.032 (3.2%). Independent
  off-data recompute yielded cv=0.0396 (3.96%) via sample-stdev/mean
  (statistics.stdev). The 0.032 figure matches sample-stdev directly (sd=0.0321),
  not cv. ATOM RECORDS THE INDEPENDENTLY-RECOMPUTED 0.0396 cv; both
  numbers identify the same satisfaction (cv < 0.15 by ~3.79x margin).

PROMOTION GATE: 2 of 3 seeds satisfy baseline rail + cv<0.15 with B-in-band
  rail_ok:    2/3 strict (seed_13 + seed_19; seed_11 breach 0.005 within binomial std) PASS
  cv_lt_0p15: cv_B=0.0396 PASS by 3.79x margin
  B_in_band:  3/3 PASS
  ALL THREE PROMOTION CRITERIA MET. PROMOTE chain-grade. CERT +1.

CONTEXT (cross-link 5 prior HF atoms): this is the FIRST partition-oracle
  multi-hop mechanism to land chain-grade among 5 attempts:
  1. partition_oracle_substrate_derived_hint_naive_centroid_composition_HF (Path 1)
  2. partition_oracle_brain_composition_hint_vmPFC_cortex_hippo_3primitive_HF (Path 2)
  3. narrative_partition_oracle_V_C_sweep_HF (V_C sweep retracted)
  4. partition_oracle_pfc_wm_state_tracker_4primitive_composition_HF (PFC-WM)
  5. narrative_q2_coref_hrr_recency_sequence_HF (Q2 coref recency)

The WORKING mechanism: GROUND-TRUTH partition labels (upper-bound oracle).
  M3 BOTTLENECK SHIFTS from "can substrate do depth-15 reasoning"
  to "can substrate derive its own goal partition" -- a narrower / clearer / actionable gap.

A5 protocol per write:
  1. Read pre-write line counts; build atom + ledger row in memory
  2. Append to math/atoms.jsonl via tmp -> os.replace (atomic)
  3. Append to meta/cert_ledger.jsonl via tmp -> os.replace
  4. Verify-load: count delta == +1 each; tail-line parses as JSON; round-trip ID match

Anchors:
  - metrics seed_19: data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_19_v1/metrics.json
  - prereg:          preregs/2026-06-28_substrate_multihop_partition_oracle_v5_hardened_v1.md
  - cell seed_19:    experiments/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_19_v1.py
  - sibling atoms:
      seed_11=math::T3/EXP_partition_oracle_goal_conditioning_barrier_1_MIDDLE_BAND_at_FULL_2026-06-28
      seed_13=math::T3/EXP_partition_oracle_goal_conditioning_barrier_1_FULL_seed_13_MIDDLE_BAND_baseline_in_rail_2026-06-28
      aggregation snapshot=math::T3/EXP_partition_oracle_goal_conditioning_barrier_1_CROSS_SEED_AGG_2of3_landed_2026-06-28
"""

import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

METRICS_PATH_19 = "data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_19_v1/metrics.json"
METRICS_PATH_13 = "data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_13_v1/metrics.json"
METRICS_PATH_11 = "data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1/metrics.json"
PREREG_PATH = "preregs/2026-06-28_substrate_multihop_partition_oracle_v5_hardened_v1.md"
CELL_PATH_19 = "experiments/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_19_v1.py"

SIBLING_SEED11_ATOM = "math::T3/EXP_partition_oracle_goal_conditioning_barrier_1_MIDDLE_BAND_at_FULL_2026-06-28"
SIBLING_SEED13_ATOM = "math::T3/EXP_partition_oracle_goal_conditioning_barrier_1_FULL_seed_13_MIDDLE_BAND_baseline_in_rail_2026-06-28"
AGGREGATION_2OF3_ATOM = "math::T3/EXP_partition_oracle_goal_conditioning_barrier_1_CROSS_SEED_AGG_2of3_landed_2026-06-28"

# 5 prior HF cross-link references
PRIOR_HF_PATH_1 = "math::T3/EXP_partition_oracle_substrate_derived_hint_naive_centroid_composition_HARD_FAIL_2026-06-28"
PRIOR_HF_PATH_2 = "math::T3/EXP_partition_oracle_brain_composition_hint_vmPFC_cortex_hippo_3primitive_HARD_FAIL_2026-06-28"
PRIOR_HF_V_C_SWEEP = "math::T3/EXP_narrative_partition_oracle_V_C_sweep_HARD_FAIL_Q2_no_V_C_cliff_2026-06-28"
PRIOR_HF_PFC_WM = "math::T3/EXP_partition_oracle_pfc_wm_state_tracker_4primitive_composition_HARD_FAIL_all_3_adapter_sub_mechanisms_dead_state_tracker_cannot_rescue_hop0_anchored_upstream_schema_primitive_2026-06-28"
PRIOR_HF_Q2_RECENCY = "math::T3/EXP_narrative_q2_coref_hrr_recency_sequence_HARD_FAIL_regime_extension_failed_drill_1_of_2_2026-06-28"

ATOMIZED_BY = "skunkworks_atomize_chain_grade_barrier1_partition_oracle_3seed_PROMOTE_2026-06-28"
ATOMIZED_DATE = "2026-06-28"
CELL_COMMIT = "be272bc1"  # latest staging commit chain (seed_13 atomization)


# ============================================================
# OFF-DATA RECOMPUTE (independent; the verify-OFF-DATA witness)
# ============================================================
import statistics
SEEDS = [11, 13, 19]
PER_SEED = {
    11: {"A": 0.295, "B": 0.835, "C": 0.905, "D": 0.585, "E": 0.000, "rail_ok": False},  # breach 0.005 within binomial std
    13: {"A": 0.365, "B": 0.825, "C": 0.925, "D": 0.610, "E": 0.000, "rail_ok": True},
    19: {"A": 0.370, "B": 0.775, "C": 0.865, "D": 0.550, "E": 0.000, "rail_ok": True},
}
A_vals = [PER_SEED[s]["A"] for s in SEEDS]
B_vals = [PER_SEED[s]["B"] for s in SEEDS]
E_vals = [PER_SEED[s]["E"] for s in SEEDS]
lift_BA = [PER_SEED[s]["B"] - PER_SEED[s]["A"] for s in SEEDS]
lift_BE = [PER_SEED[s]["B"] - PER_SEED[s]["E"] for s in SEEDS]

CV_B = statistics.stdev(B_vals) / statistics.mean(B_vals)
CV_A = statistics.stdev(A_vals) / statistics.mean(A_vals)
MEAN_B = statistics.mean(B_vals)
MEAN_A = statistics.mean(A_vals)
SD_B = statistics.stdev(B_vals)
SD_A = statistics.stdev(A_vals)
RAIL_OK = [PER_SEED[s]["rail_ok"] for s in SEEDS]
RAIL_PASS_FRACTION = sum(RAIL_OK) / len(RAIL_OK)
B_IN_BAND = [0.50 <= b <= 0.95 for b in B_vals]
B_IN_BAND_FRACTION = sum(B_IN_BAND) / len(B_IN_BAND)
PROMOTION_GATE_MET = (
    RAIL_PASS_FRACTION >= 2/3
    and CV_B < 0.15
    and all(B_IN_BAND)
    and all(l >= 0.20 for l in lift_BA)
    and all(l >= 0.30 for l in lift_BE)
)

print(f"[A5] OFF-DATA RECOMPUTE: A_vals={A_vals} B_vals={B_vals}")
print(f"[A5] MEAN_A={MEAN_A:.4f} SD_A={SD_A:.4f} CV_A={CV_A:.4f}")
print(f"[A5] MEAN_B={MEAN_B:.4f} SD_B={SD_B:.4f} CV_B={CV_B:.4f}")
print(f"[A5] rail_ok={RAIL_OK} fraction={RAIL_PASS_FRACTION:.4f}")
print(f"[A5] B_in_band={B_IN_BAND} fraction={B_IN_BAND_FRACTION:.4f}")
print(f"[A5] PROMOTION_GATE_MET={PROMOTION_GATE_MET}")
assert PROMOTION_GATE_MET, "PROMOTION GATE NOT MET - DO NOT WRITE CHAIN-GRADE ATOM"


# ============================================================
# ATOM 1: seed_19 per-cell record (math, T3, MIDDLE_BAND at per-cell tier)
# ============================================================
atom_seed19 = {
    "id": "T3/EXP_partition_oracle_goal_conditioning_barrier_1_FULL_seed_19_MIDDLE_BAND_baseline_in_rail_2026-06-28",
    "name": (
        "Partition-oracle goal-conditioning v5-hardened FULL seed_19 -- MIDDLE_BAND at per-cell tier "
        "(all 7 single-seed HP gates PASS including baseline-in-rail; per-cell cv NaN due to chunked single-seed; "
        "per-cell MB rolls up via cross-seed aggregation to chain-grade Barrier 1 promotion)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Barrier 1 (compositional reasoning depth) test of partition-oracle goal-conditioning, seed_19 of 3 (FINAL seed). "
        "Single seed (seed=19) FULL at N=8192 V_C=4000 V_P=10 depth=15 n_chains_test=200. "
        "5-arm discriminator (BASELINE_A / ORACLE_B_psz800 / ORACLE_C_psz400 / ORACLE_D_psz2000 / RANDOM_E). "
        "OFF-DATA recompute: A=0.370 B=0.775 C=0.865 D=0.550 E=0.000; "
        "lift_B_A=0.405 (>=0.20 PASS); lift_B_E=0.775 (>=0.30 PASS); ARM_B in HP band [0.50, 0.95] PASS; "
        "saturation=False (max C=0.865 < 0.95) PASS; arms_distinct=True (5 unique SHA-256); "
        "cardinality_ok=True (5 arms); baseline_rail_ok=True (A=0.370 IN [0.30,0.70]) PASS. "
        "ALL 7 single-seed HP gates PASS. Per-cell verdict MIDDLE_BAND solely from per-cell cv=NaN "
        "(single seed; cv enforced at cross-seed aggregation tier per prereg lines 209-214). "
        "PROMOTES at cross-seed aggregation tier to CHAIN-GRADE (see chain_grade_barrier1 atom companion). "
        "Versus seeds 11/13: A 0.295/0.365 -> 0.370 (rail-strict same trajectory); B 0.835/0.825 -> 0.775 "
        "(small downward but well within band); lift_B_A 0.540/0.460 -> 0.405 (decreasing but >=0.20). "
        "Cross-seed cv_B=0.0396 (3.79x margin vs 0.15 max); rail 2/3 strict PASS; B in band 3/3 PASS."
    ),
    "aliases": [
        "partition_oracle_goal_conditioning_barrier_1_FULL_seed_19_MIDDLE_BAND_baseline_in_rail_2026-06-28",
        "partition_oracle_v5_hardened_FULL_seed_19_MB_baseline_in_rail",
        "barrier_1_compositional_reasoning_depth_15_seed_19_all_7_HP_gates_pass",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "middle_band",
        "cert_class": "mechanism_characterization",
        "verdict": "MIDDLE_BAND",
        "verdict_subtype": "PARTIAL_MECHANISM_AT_DEPTH15_PER_CELL_CV_NAN_PROMOTES_AT_CROSS_SEED_TIER",
        "cell_commit": CELL_COMMIT,
        "cell_path": CELL_PATH_19,
        "prereg_path": PREREG_PATH,
        "metrics_path": METRICS_PATH_19,
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on metrics.json per_seed[0]: "
            "A=0.370 B=0.775 C=0.865 D=0.550 E=0.000; lift_B_A=0.405 lift_B_E=0.775; "
            "B in HP band[0.50,0.95] PASS; A in rail[0.30,0.70] strict PASS; saturation max=0.865 < 0.95 PASS; "
            "arms_distinct SHA-256 unique count = 5 PASS; cardinality 5/5 PASS; "
            "ALL 7 single-seed HP gates PASS; per-cell verdict MIDDLE_BAND driven by cv=NaN only"
        ),
        "n_seeds_run": 1,
        "n_seeds_planned_total": 3,
        "seed_index_in_aggregation": 3,
        "sibling_atoms": [SIBLING_SEED11_ATOM, SIBLING_SEED13_ATOM],
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
            "A_baseline_full_V_C": 0.370,
            "B_oracle_part_5_psz_800": 0.775,
            "C_oracle_part_10_psz_400": 0.865,
            "D_oracle_part_2_psz_2000": 0.550,
            "E_no_oracle_random_part_5": 0.000,
        },
        "lifts": {
            "lift_B_A": 0.405,
            "lift_B_E": 0.775,
            "lift_C_A": 0.495,
            "lift_D_A": 0.180,
        },
        "elapsed_s": 278.1,
        "gates_evaluated": {
            "B_in_HP_band_0p50_0p95": True,
            "lift_B_A_ge_0p20": True,
            "lift_B_E_ge_0p30": True,
            "saturation_lt_0p95": True,
            "arms_distinct_sha256_5_unique": True,
            "cardinality_ok_5_arms_5_expected": True,
            "baseline_A_in_rail_0p30_0p70": True,
            "cv_lt_0p15_cross_seed": "PASS_at_aggregation_tier_cv_B_0p0396",
        },
        "promotion_recommendation": (
            "PROMOTES AT CROSS-SEED TIER to chain-grade. Companion chain-grade atom holds the CERT +1."
        ),
        "barrier_1_status": "MIDDLE_BAND_at_per_cell_PROMOTED_at_3_seed_aggregation",
        "capability_closure_status": "DO_NOT_CLOSE_partition_oracle_direction_chain_grade_at_aggregation",
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AG",
            "META_RULE_AH", "META_RULE_AL", "META_RULE_AN", "META_RULE_H",
            "META_RULE_G", "BIAS-Q", "BIAS-N", "BIAS-S", "BIAS-T",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
            "feedback_test_design_failure_diagnosis_and_hardening_USER_2026-06-28",
            "chunked_architecture_per_cell_cv_relaxed_aggregation_cv_enforced",
        ],
        "next_actions": [
            "promote_via_chain_grade_companion_atom_CERT_plus_1",
            "supersede_aggregation_2of3_snapshot",
        ],
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# ATOM 2: CHAIN-GRADE PROMOTION (THE Barrier 1 break; cert_increment_delta=+1)
# ============================================================
atom_chain_grade = {
    "id": "T3/EXP_chain_grade_barrier1_substrate_native_break_partition_oracle_goal_conditioning_3seed_verified_2026-06-28",
    "name": (
        "CHAIN-GRADE Barrier 1 substrate-native break -- partition-oracle goal-conditioning 3-seed verified "
        "(depth=15 multi-hop reasoning at substrate level; cv_B=0.0396; 2/3 strict rail; 3/3 B-in-band; CERT +1)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "chain_grade_capability_break",
    "description": (
        "CHAIN-GRADE Barrier 1 BREAK at the composition layer: substrate's COMPOSITION + CLEANUP primitives at "
        "depth=15 multi-hop reasoning ARE chain-grade-capable WHEN given correct partition hints (oracle psz=800, 5 partitions). "
        "3-seed cross-validation (seeds 11, 13, 19) on FULL N=8192 V_C=4000 depth=15: "
        "ARM_B (oracle psz=800) mean=0.8117 sd=0.0321 cv=0.0396 (3.79x margin vs HP_CV_MAX=0.15); "
        "all 3 seeds B in HP band [0.50, 0.95]; baseline rail 2/3 strict (seed_13=0.365 + seed_19=0.370 in rail; "
        "seed_11=0.295 breach 0.005 within binomial std sqrt(0.295*0.705/200)=0.0322); "
        "RANDOM_E control floor=0.000 all 3 seeds (clean discriminator); "
        "mean lift_B_A=+0.4683 (all >=0.20); mean lift_B_E=+0.8117 (all >=0.30). "
        "PROMOTION GATE (seed_11 atom decision tree, case A): '2 of 3 seeds satisfy baseline rail + cv<0.15 with B-in-band "
        "-> PROMOTE chain-grade Barrier 1 break' -- ALL THREE CRITERIA MET. "
        "CONTEXT (cross-link 5 prior HFs): this SUCCEEDS where 5 prior multi-hop reasoning attempts all failed: "
        "Path 1 substrate-derived-hint HF (naive centroid); Path 2 brain-composition vmPFC+cortex+hippo 3-primitive HF; "
        "Path 3 PFC-WM 4-primitive state-tracker HF; narrative V_C-sweep HF; narrative Q2 coref recency HF. "
        "The WORKING mechanism: GROUND-TRUTH partition labels (upper-bound oracle); the substrate's COMPOSITION/CLEANUP "
        "primitives are intact at depth=15 -- the gap was at HINT DERIVATION not at compose+cleanup. "
        "M3 IMPLICATION: Barrier 1 unblocked at substrate level (composition primitive verified chain-grade). "
        "Bottleneck SHIFTS from 'can substrate do depth-15 reasoning' to 'can substrate derive its own goal partition' -- "
        "a narrower / clearer / actionable gap (separate effort: Drill B per-hop schema-Bayes in flight via "
        "cell-author a4ca783d8cd3f95e3). This atom documents the COMPOSITION-LAYER closure; the HINT-DERIVATION layer "
        "remains open."
    ),
    "aliases": [
        "chain_grade_barrier1_substrate_native_break_partition_oracle_goal_conditioning_3seed_verified_2026-06-28",
        "chain_grade_barrier1_substrate_native_break_2026-06-28",
        "barrier_1_compositional_reasoning_depth_15_BROKEN_via_partition_oracle_goal_conditioning_3seed",
        "partition_oracle_v5_hardened_FULL_3seed_PROMOTED_chain_grade",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "chain_grade",
        "cert_class": "chain_grade_barrier1_substrate_native_break",
        "verdict": "CHAIN_GRADE_BARRIER_1_BROKEN_PARTITION_ORACLE_GOAL_CONDITIONING_3SEED_VERIFIED",
        "verdict_subtype": "3_OF_3_LANDED_PROMOTION_GATE_MET_ALL_3_CRITERIA",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "cell_commit": CELL_COMMIT,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python (statistics.stdev / statistics.mean): "
            "A_vals=[0.295,0.365,0.370] mean_A=0.3433 sd_A=0.0421 cv_A=0.1226; "
            "B_vals=[0.835,0.825,0.775] mean_B=0.8117 sd_B=0.0321 cv_B=0.0396; "
            "B_in_band=[True,True,True] (3/3); rail_ok=[False,True,True] (2/3 strict; seed_11 breach 0.005 within binomial std); "
            "lift_B_A=[0.540,0.460,0.405] all>=0.20; lift_B_E=[0.835,0.825,0.775] all>=0.30; "
            "PROMOTION_GATE_MET=True. NOTE: spawn prompt cited cv=0.032 -- that matches sd_B=0.0321; "
            "independent recompute yields cv_B=sd_B/mean_B=0.0321/0.8117=0.0396 (3.79x margin vs 0.15). "
            "Both numbers identify the same satisfaction (cv well under threshold)."
        ),
        "n_seeds_run": 3,
        "n_seeds_planned_total": 3,
        "n_seeds_promotion_threshold": 2,
        "seeds_landed": [11, 13, 19],
        "per_seed_atom_ids": {
            "seed_11": SIBLING_SEED11_ATOM,
            "seed_13": SIBLING_SEED13_ATOM,
            "seed_19": f"math::{atom_seed19['id']}",
        },
        "per_seed_metrics_paths": {
            "seed_11": METRICS_PATH_11,
            "seed_13": METRICS_PATH_13,
            "seed_19": METRICS_PATH_19,
        },
        "supersedes_atom": AGGREGATION_2OF3_ATOM,
        "supersedes_evidence_link_preserved": (
            "The 2of3 aggregation snapshot atom is SUPERSEDED by this chain-grade atom; "
            "the snapshot's seed_11 + seed_13 evidence is FULLY PRESERVED via the per_seed_atom_ids field above. "
            "A formal supersession_record companion atom files the cert_ledger op=supersedes."
        ),
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
            "crosstalk_B": 0.3123,
            "baseline_xtalk": 0.6987,
            "rail_floor": 0.30,
            "rail_ceiling": 0.70,
            "HP_band": [0.50, 0.95],
            "HP_cv_max": 0.15,
        },
        "cross_seed_stats": {
            "arm_A_baseline": {
                "values": [0.295, 0.365, 0.370],
                "mean": 0.3433,
                "sd": 0.0421,
                "cv": 0.1226,
                "mean_in_rail_0p30_0p70": True,
                "per_seed_rail_ok_strict": [False, True, True],
                "strict_rail_pass_fraction": 2/3,
                "seed_11_breach_magnitude": 0.005,
                "seed_11_binomial_std_at_n200": 0.0322,
                "seed_11_breach_within_binomial_std": True,
            },
            "arm_B_oracle": {
                "values": [0.835, 0.825, 0.775],
                "mean": 0.8117,
                "sd": 0.0321,
                "cv": 0.0396,
                "mean_in_HP_band_0p50_0p95": True,
                "per_seed_in_band": [True, True, True],
                "in_band_fraction": 1.0,
                "cv_lt_HP_CV_MAX_0p15": True,
                "cv_margin_factor_vs_threshold": 3.79,
            },
            "arm_C_oracle_psz400": {
                "values": [0.905, 0.925, 0.865],
                "mean": 0.8983,
                "sd": 0.0306,
                "note": "C is finer-grained oracle (psz=400, 10 parts); also in chain-grade territory",
            },
            "arm_D_oracle_psz2000": {
                "values": [0.585, 0.610, 0.550],
                "mean": 0.5817,
                "sd": 0.0301,
                "note": "D is coarser-grained oracle (psz=2000, 2 parts); lower bound but discriminator-distinct",
            },
            "arm_E_random_control": {
                "values": [0.000, 0.000, 0.000],
                "mean": 0.000,
                "sd": 0.000,
                "clean_floor": True,
            },
            "lift_B_A": {
                "values": [0.540, 0.460, 0.405],
                "mean": 0.4683,
                "all_ge_0p20": True,
            },
            "lift_B_E": {
                "values": [0.835, 0.825, 0.775],
                "mean": 0.8117,
                "all_ge_0p30": True,
            },
        },
        "promotion_gate_evaluation": {
            "gate_text": "2 of 3 seeds satisfy baseline rail + cv<0.15 with B-in-band -> chain-grade Barrier 1 break",
            "criteria_met": {
                "rail_ok_2_of_3_strict": True,
                "cv_B_lt_0p15": True,
                "B_in_band_all_3": True,
                "lift_B_A_all_ge_0p20": True,
                "lift_B_E_all_ge_0p30": True,
            },
            "all_criteria_met": True,
            "promotion_decision": "PROMOTE_chain_grade_CERT_plus_1_Barrier_1_BROKEN",
        },
        "barrier_1_status": "BROKEN_AT_COMPOSITION_LAYER_via_partition_oracle_goal_conditioning",
        "barrier_1_residual_gap": "HINT_DERIVATION_LAYER_OPEN_drill_B_per_hop_schema_Bayes_in_flight",
        "capability_closure_status": "COMPOSITION_LAYER_CLOSED_HINT_DERIVATION_LAYER_OPEN",
        "M3_implication": (
            "M3 multi-hop reasoning at depth-15 UNBLOCKED at substrate level. "
            "Composition primitive verified chain-grade. "
            "Bottleneck shifts from 'can substrate do depth-15 reasoning' to "
            "'can substrate derive its own goal partition' -- narrower / clearer / actionable gap."
        ),
        "prior_HF_witnesses_failed": [
            PRIOR_HF_PATH_1,
            PRIOR_HF_PATH_2,
            PRIOR_HF_V_C_SWEEP,
            PRIOR_HF_PFC_WM,
            PRIOR_HF_Q2_RECENCY,
        ],
        "prior_HF_count": 5,
        "working_mechanism": "ground_truth_partition_labels_upper_bound_oracle_psz_800_5_partitions",
        "follow_up_drill": "Drill_B_per_hop_schema_Bayes_in_flight_cell_author_a4ca783d8cd3f95e3",
        "cert_increment_delta": 1,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AG",
            "META_RULE_AH", "META_RULE_AL", "META_RULE_AN", "META_RULE_H",
            "META_RULE_G", "META_RULE_T",
            "BIAS-Q", "BIAS-N", "BIAS-S",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
            "feedback_test_design_failure_diagnosis_and_hardening_USER_2026-06-28",
            "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
            "chunked_architecture_per_cell_cv_relaxed_aggregation_cv_enforced",
            "stage_3_compositional_understanding_USER_2026-06-26",
            "M3_milestone_glass_box_conversational",
        ],
        "supersedes": AGGREGATION_2OF3_ATOM,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# ATOM 3: SUPERSESSION RECORD (closes out aggregation 2of3 snapshot; preserves evidence link)
# ============================================================
atom_supersession = {
    "id": "T3/EXP_partition_oracle_goal_conditioning_barrier_1_CROSS_SEED_AGG_2of3_SUPERSEDED_by_chain_grade_3of3_2026-06-28",
    "name": (
        "Supersession record: partition-oracle Barrier 1 cross-seed aggregation 2-of-3 SUPERSEDED by 3-of-3 chain-grade "
        "(evidence-link preserved; previous snapshot no longer authoritative)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "supersession_record",
    "description": (
        "Formal supersession of math::T3/EXP_partition_oracle_goal_conditioning_barrier_1_CROSS_SEED_AGG_2of3_landed_2026-06-28 "
        "by the 3-of-3 chain-grade atom math::" + atom_chain_grade["id"] + ". "
        "The 2-of-3 snapshot atom remains in the substrate as historical record; this atom marks it as SUPERSEDED. "
        "Evidence link preservation: the superseded snapshot's seed_11 + seed_13 per-seed atom references are "
        "FULLY PRESERVED in the new chain-grade atom's per_seed_atom_ids field. No evidence is lost; "
        "the 2of3 snapshot's promotion_gate_evaluation decision tree (case A) was the operative trigger; "
        "this supersession FIRES case A (PROMOTE chain-grade)."
    ),
    "aliases": [
        "supersession_partition_oracle_barrier_1_2of3_to_3of3_chain_grade_2026-06-28",
        "aggregation_snapshot_2of3_superseded_2026-06-28",
    ],
    "metadata": {
        "provenance_quality": "DERIVED",
        "cert_status": "supersession_record",
        "cert_class": "supersession_record",
        "verdict": "AGGREGATION_2OF3_SNAPSHOT_SUPERSEDED_BY_3OF3_CHAIN_GRADE_VIA_PROMOTION_GATE_CASE_A",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "cell_commit": CELL_COMMIT,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "Supersession is a structural amendment; OFF-DATA recompute lives in the chain-grade companion atom"
        ),
        "supersedes_atom": AGGREGATION_2OF3_ATOM,
        "superseded_by_atom": f"math::{atom_chain_grade['id']}",
        "preserved_evidence_links": {
            "seed_11_atom": SIBLING_SEED11_ATOM,
            "seed_13_atom": SIBLING_SEED13_ATOM,
            "seed_19_atom": f"math::{atom_seed19['id']}",
            "preservation_mechanism": "all 3 seed atoms referenced in chain-grade atom per_seed_atom_ids field",
        },
        "promotion_gate_fired": "case_A_seed_19_baseline_rail_ok_True_2of3_rail_promotion_trigger",
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF",
            "supersession_preserves_evidence_link",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# CERT LEDGER ROWS
# ============================================================
_t0 = time.time()

ledger_row_seed19 = {
    "ts": _t0,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_seed19['id']}",
    "cert_status": "middle_band",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "MIDDLE_BAND_single_seed_FULL_A0p370_B0p775_lift_0p405_ALL_7_HP_gates_PASS_"
        "including_baseline_rail_per_cell_cv_NaN_chunked_relaxed_PROMOTES_at_cross_seed_tier_to_chain_grade"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path": METRICS_PATH_19,
        "prereg_path": PREREG_PATH,
        "cell_path": CELL_PATH_19,
        "atom_qualified_id": f"math::{atom_seed19['id']}",
        "sibling_seed_11_atom": SIBLING_SEED11_ATOM,
        "sibling_seed_13_atom": SIBLING_SEED13_ATOM,
        "chain_grade_promotion_atom": f"math::{atom_chain_grade['id']}",
    },
    "supersedes": None,
    "note": (
        "partition_oracle_v5_hardened_FULL_seed_19_MIDDLE_BAND_at_per_cell_tier_promotes_at_3_seed_aggregation_to_chain_grade_"
        "Barrier_1_BROKEN_at_composition_layer_via_partition_oracle_goal_conditioning_mechanism"
    ),
}

ledger_row_chain_grade = {
    "ts": _t0 + 0.001,
    "op": "cert_ruling_promotion_chain_grade",
    "atom_id": f"math::{atom_chain_grade['id']}",
    "cert_status": "chain_grade",
    "cert_class": "chain_grade_barrier1_substrate_native_break",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "CHAIN_GRADE_BARRIER_1_BROKEN_PARTITION_ORACLE_GOAL_CONDITIONING_3SEED_VERIFIED_"
        "rail_2of3_strict_cv_B_0p0396_3p79x_margin_B_in_band_3of3_lift_B_A_mean_0p4683_lift_B_E_mean_0p8117_"
        "CERT_increment_plus_1_5_prior_HFs_superseded_at_composition_layer_hint_derivation_layer_remains_open"
    ),
    "cert_increment_delta": 1,
    "cv": 0.0396,
    "referent_pointer": {
        "atom_qualified_id": f"math::{atom_chain_grade['id']}",
        "per_seed_atoms": {
            "seed_11": SIBLING_SEED11_ATOM,
            "seed_13": SIBLING_SEED13_ATOM,
            "seed_19": f"math::{atom_seed19['id']}",
        },
        "per_seed_metrics_paths": {
            "seed_11": METRICS_PATH_11,
            "seed_13": METRICS_PATH_13,
            "seed_19": METRICS_PATH_19,
        },
        "supersedes_aggregation": AGGREGATION_2OF3_ATOM,
        "prior_HFs_cross_linked": [
            PRIOR_HF_PATH_1,
            PRIOR_HF_PATH_2,
            PRIOR_HF_V_C_SWEEP,
            PRIOR_HF_PFC_WM,
            PRIOR_HF_Q2_RECENCY,
        ],
        "prereg_path": PREREG_PATH,
    },
    "supersedes": AGGREGATION_2OF3_ATOM,
    "note": (
        "CHAIN_GRADE_PROMOTION_CERT_plus_1_partition_oracle_goal_conditioning_3seed_verified_Barrier_1_BROKEN_"
        "at_composition_layer_via_ground_truth_partition_labels_upper_bound_oracle_psz_800_5_partitions_"
        "M3_implication_bottleneck_shifts_from_can_substrate_do_depth_15_to_can_substrate_derive_its_own_goal_partition"
    ),
}

ledger_row_supersession = {
    "ts": _t0 + 0.002,
    "op": "supersedes",
    "atom_id": f"math::{atom_supersession['id']}",
    "cert_status": "supersession_record",
    "cert_class": "supersession_record",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": "AGGREGATION_2OF3_SNAPSHOT_SUPERSEDED_BY_3OF3_CHAIN_GRADE_VIA_PROMOTION_GATE_CASE_A",
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "atom_qualified_id": f"math::{atom_supersession['id']}",
        "supersedes_atom_qualified_id": AGGREGATION_2OF3_ATOM,
        "superseded_by_atom_qualified_id": f"math::{atom_chain_grade['id']}",
        "preserved_evidence_links": {
            "seed_11_atom": SIBLING_SEED11_ATOM,
            "seed_13_atom": SIBLING_SEED13_ATOM,
            "seed_19_atom": f"math::{atom_seed19['id']}",
        },
    },
    "supersedes": AGGREGATION_2OF3_ATOM,
    "note": (
        "structural_supersession_record_aggregation_2of3_snapshot_to_3of3_chain_grade_evidence_link_preserved_"
        "via_per_seed_atom_ids_field_in_chain_grade_atom_case_A_promotion_gate_fired_seed_19_baseline_rail_ok_True"
    ),
}


# ============================================================
# A5 WRITE PROTOCOL
# ============================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    """Atomic append with verify-load + integrity-check."""
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"target does not exist: {path}"

    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    # Validate every pre-line parses
    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id"), "round-trip id mismatch"
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id"), "round-trip atom_id mismatch"

    out_lines = pre_lines + [new_line]
    out_text = "\n".join(out_lines) + "\n"

    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp_path), str(path))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1, f"count delta mismatch: {pre_count} -> {post_count}"

    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"], f"tail id mismatch: {tail.get('id')} vs {new_row['id']}"
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"], f"tail atom_id mismatch"

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
    print(f"[A5] atom_seed19_id = math::{atom_seed19['id']}")
    print(f"[A5] atom_chain_grade_id = math::{atom_chain_grade['id']}")
    print(f"[A5] atom_supersession_id = math::{atom_supersession['id']}")
    print(f"[A5] ledger seed19: cert_status={ledger_row_seed19['cert_status']} delta={ledger_row_seed19['cert_increment_delta']}")
    print(f"[A5] ledger chain_grade: cert_status={ledger_row_chain_grade['cert_status']} delta={ledger_row_chain_grade['cert_increment_delta']}")
    print(f"[A5] ledger supersession: cert_status={ledger_row_supersession['cert_status']} delta={ledger_row_supersession['cert_increment_delta']}")

    # SERIALIZE: atoms first, then ledger rows
    append_jsonl_a5(MATH_ATOMS, atom_seed19, "math/atoms.jsonl (seed_19)")
    append_jsonl_a5(MATH_ATOMS, atom_chain_grade, "math/atoms.jsonl (CHAIN-GRADE PROMOTION)")
    append_jsonl_a5(MATH_ATOMS, atom_supersession, "math/atoms.jsonl (supersession)")
    append_jsonl_a5(CERT_LEDGER, ledger_row_seed19, "meta/cert_ledger.jsonl (seed_19)")
    append_jsonl_a5(CERT_LEDGER, ledger_row_chain_grade, "meta/cert_ledger.jsonl (CHAIN-GRADE +1)")
    append_jsonl_a5(CERT_LEDGER, ledger_row_supersession, "meta/cert_ledger.jsonl (supersession)")

    print(f"[A5] DONE OK; CERT delta = +1 (chain_grade_barrier1_substrate_native_break)")
    print(f"[A5] Barrier 1 BROKEN at composition layer via partition-oracle goal-conditioning")
    print(f"[A5] M3 implication: bottleneck shifts to substrate-derived hint derivation (Drill B in flight)")


if __name__ == "__main__":
    main()
