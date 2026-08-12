"""Skunkworks atomize: binding-op + refuse-gate v1 POST-SYNC (8 atoms; supersede stale HF/SELFTEST)

After Lead retraction + Orchestrator SSH verification on remote: binding-op + refuse-gate v1 cells
ACTUALLY landed at 17:43-17:44 UTC with MIDDLE_BAND verdicts FULL run_mode (not pre-flight HF or
SELFTEST). The hd_metrics_sync merger is preserve-existing -- stale 2026-06-29 files (GPU-mandate
breach + selftest_only) blocked the fresh remote files from being pulled. Skunkworks side-pulled
the fresh remote metrics.json via direct SCP under .fresh_2026-06-30.json suffix and re-VET'd.

Off-disk verification confirms:
  binding-op seed 7/13/19: MIDDLE_BAND verdict run_mode=full cardinality 48/48 backend=torch.cuda
    elapsed 1.32-1.55s gpu_util 0.56 verdict_msg=MIDDLE_BAND_BINDING_DIFFERS_BUT_LOW_DISC
    n_disc=7-8/48 (need >=14); n_pairs_differ=6/6; n_ops_above_30pct=0
    op_tiers={cc/fhrr/hadamard: COMPETITIVE_BINDING, outer_product: DOMINATED_BINDING}
    positive_control: circular_conv N=4096 c=0.10 measured_top1=0.99 pass=True (>=0.50 floor)
    ALL 4 op mechanism_hashes DISTINCT per seed (META_RULE_AX satisfied)

  refuse-gate seed 7/13/19: MIDDLE_BAND verdict run_mode=full cardinality 48/48 backend=numpy.cpu
    elapsed 14.7-16.9s verdict_msg=MIDDLE_BAND_ADAPTIVITY_DIFFERS_BUT_LOW_DISC
    0/48 HP+MB < threshold 15; family pairs differ 4/6 (NOT 6/6 -- META_RULE_AX TRIGGERS:
    fixed_threshold and learned_logistic produce IDENTICAL mechanism_hash 4542fd54;
    adaptive_bayesian_CI and percentile_based produce IDENTICAL mechanism_hash 48301b90;
    4 family slots collapse to 2 distinct mechanism implementations)
    family_tiers={fixed/learned: COMPETITIVE, bayesian/percentile: DOMINATED}
    positive_control: fixed_threshold PURE_OUT cal=256 refuse_rate=1.000 pass=True

  per-cell tier: 6 MM atoms (3 binding-op + 3 refuse-gate) + 2 CROSS_SEED_AGG MM atoms = 8 atoms
  delta=0 per atom (MM tier per Director ACK)

  These NEW MM atoms SUPERSEDE the stale HF/SELFTEST atoms from a009a44a in the framing sense
  (cells actually ran when properly queue_added). Both old + new atoms remain in ledger as
  historical record per Director: "OLD HF/SELFTEST atoms ... should remain in the ledger as
  historical record. The NEW MM atoms supersede the framing as 'v1 cells actually ran when
  properly queue_added.'"

  ADDITIONAL DISCIPLINE FLAG (informational; not META rule yet -- 1-cell witness only): refuse-gate
  family-axis 2-of-4 mechanism_hash collapse is a partial-encoder-not-wired signature; the cell
  honestly reports n_family_pairs_differ=4/6 and lands MIDDLE_BAND not HARD_PASS, which the cell's
  verdict-banding correctly handles. META_RULE_AX (atomized in prior 3cell batch) covers the
  full-collapse case; refuse-gate is a successful AX-honest-handling example, not a violation.

A5-discipline: atomic write via tmp + os.replace; verify-load + integrity-check.
Idempotent: skip atoms already present.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List

DATE_ISO = "2026-06-30"
ATOMIZED_BY = "skunkworks_atomize_binding_refuse_post_sync_8atoms_2026-06-30"
SEEDS = [7, 13, 19]


# ---- BINDING-OP per-seed MM ----

BINDING_OP_PER_SEED_VET = {
    7: {
        "verdict": "MIDDLE_BAND",
        "elapsed_s": 1.55,
        "n_disc": 8,
        "tier_counts": {"SATURATED": 11, "HARD_PASS": 3, "MIDDLE_BAND": 5, "FLOOR": 17, "HARD_FAIL": 12},
        "per_op_top1_mean": {
            "circular_convolution": 0.4183,
            "element_wise_fhrr": 0.4100,
            "hadamard_real": 0.4125,
            "outer_product_tensor": 0.3583,
        },
        "ts_iso": "2026-06-30T17:43:21Z",
    },
    13: {
        "verdict": "MIDDLE_BAND",
        "elapsed_s": 1.32,
        "n_disc": 8,
        "tier_counts": {"SATURATED": 10, "HARD_PASS": 2, "MIDDLE_BAND": 6, "FLOOR": 17, "HARD_FAIL": 13},
        "per_op_top1_mean": {
            "circular_convolution": 0.4125,
            "element_wise_fhrr": 0.4058,
            "hadamard_real": 0.4125,
            "outer_product_tensor": 0.3575,
        },
        "ts_iso": "2026-06-30T17:43:29Z",
    },
    19: {
        "verdict": "MIDDLE_BAND",
        "elapsed_s": 1.34,
        "n_disc": 7,
        "tier_counts": {"SATURATED": 10, "HARD_PASS": 2, "MIDDLE_BAND": 5, "FLOOR": 17, "HARD_FAIL": 14},
        "per_op_top1_mean": {
            "circular_convolution": 0.4133,
            "element_wise_fhrr": 0.4042,
            "hadamard_real": 0.4192,
            "outer_product_tensor": 0.3392,
        },
        "ts_iso": "2026-06-30T17:43:43Z",
    },
}


def binding_op_per_seed_mm_atom(seed: int) -> Dict[str, Any]:
    v = BINDING_OP_PER_SEED_VET[seed]
    aid = (f"T3/EXP_substrate_pc_binding_operation_family_phase_diagram_v1_FULL_seed_{seed}_"
           f"MEASURED_MECHANISM_per_op_characterization_3_of_4_COMPETITIVE_outer_product_DOMINATED_"
           f"n_disc_{v['n_disc']}_of_48_low_disc_arm_hashes_4_distinct_supersedes_stale_HF_GPU_mandate_breach_"
           f"actually_ran_FULL_at_17_43_UTC_{DATE_ISO}")
    return {
        "id": aid,
        "name": (
            f"substrate_pc_binding_operation_family v1 FULL seed_{seed} MEASURED_MECHANISM: 4 binding "
            f"operations (circular_conv / fhrr / hadamard / outer_product) compared at 48 phase pts (N x "
            f"corruption); 3 of 4 COMPETITIVE_BINDING / outer_product DOMINATED_BINDING; n_disc={v['n_disc']}/48; "
            f"positive control circ_conv N=4096 c=0.10 top1=0.99 PASS; supersedes stale GPU_mandate_breach atom"
        ),
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": (
            f"Stage 2 substrate binding-operation phase-diagram cell v1 seed_{seed} FULL run (actually landed at "
            f"{v['ts_iso']} on REMOTE GPU after proper queue_add, not the stale HARD_FAIL_GPU_MANDATE_BREACH "
            f"from earlier 2026-06-29 dispatch). 4 binding ops (circular_convolution, element_wise_fhrr, "
            f"hadamard_real, outer_product_tensor) compared at 12 inner pts per op (N in [1024, 4096, 8192] x "
            f"corruption in [0.10, 0.25, 0.40, 0.475]) = 48 phase pts. Verdict MIDDLE_BAND honest-low-disc: "
            f"n_disc={v['n_disc']}/48 below the >=14 chain-grade threshold; n_pairs_differ=6/6 (all 4 op mech-hashes "
            f"distinct -- META_RULE_AX satisfied); n_ops_above_30pct_disc_frac=0 (no op breaks the 30% disc "
            f"threshold). per_op_top1_mean cross-12-pts: circ_conv={v['per_op_top1_mean']['circular_convolution']:.4f} "
            f"fhrr={v['per_op_top1_mean']['element_wise_fhrr']:.4f} hadamard={v['per_op_top1_mean']['hadamard_real']:.4f} "
            f"outer={v['per_op_top1_mean']['outer_product_tensor']:.4f}. tier_counts={v['tier_counts']} -- the "
            f"dominant SATURATED + FLOOR + HARD_FAIL counts make the discriminating-regime band thin; 5-6 "
            f"MIDDLE_BAND + 2-3 HARD_PASS points provide partial regime characterization but not a chain-grade "
            f"discrimination. Positive control: circular_convolution N=4096 corruption=0.10 cleanup_iters=3 "
            f"M_items=100 measured_top1=0.99 PASS (>=0.50 floor); the cell's mechanism plumbing works. op_tiers: "
            f"circ_conv/fhrr/hadamard = COMPETITIVE_BINDING; outer_product = DOMINATED_BINDING (top1_mean ~0.34-"
            f"0.36 vs 0.40-0.42 for the other 3). elapsed_s={v['elapsed_s']} on backend=torch.cuda gpu_util=0.56. "
            f"TIER: MEASURED_MECHANISM (per-seed per-op characterization; 3-seed agg in sibling atom). "
            f"SUPERSEDES (framing): stale HARD_FAIL_GPU_MANDATE_BREACH atom from a009a44a -- that atom records "
            f"the 2026-06-29 pre-flight refusal correctly, but the cell actually ran on FULL at 17:43 UTC "
            f"2026-06-30 after proper HDLAB_QUEUE setup. Both atoms remain in ledger per Director directive."
        ),
        "aliases": [
            f"pc_binding_op_family_v1_FULL_seed_{seed}_MM_{DATE_ISO}",
            f"binding_op_seed_{seed}_post_sync_MM",
        ],
        "metadata": {
            "provenance_quality": "MEASURED",
            "cert_status": "measured_mechanism",
            "cert_class": "per_seed_phase_characterization_MM",
            "verdict": "MIDDLE_BAND",
            "verdict_subtype": "BINDING_DIFFERS_BUT_LOW_DISC_3_COMPETITIVE_1_DOMINATED",
            "atomized_by": ATOMIZED_BY,
            "atomized_date": DATE_ISO,
            "verified_off_data": True,
            "verified_off_data_evidence": (
                f".venv python OFF-DATA recompute on FRESH-PULLED metrics.fresh_2026-06-30.json for seed_{seed}: "
                f"verdict=MIDDLE_BAND run_mode=full _phase=None cardinality_ok=True observed_n=48 expected_n=48 "
                f"elapsed_s={v['elapsed_s']} backend=torch.cuda gpu_util=0.56 device=cuda. "
                f"per_op_top1_mean = {v['per_op_top1_mean']}. tier_counts = {v['tier_counts']}. "
                f"n_disc = {v['n_disc']}/48. n_pairs_differ = 6/6 (all 4 op mech-hashes distinct). "
                f"positive_control circ_conv N=4096 c=0.10 measured_top1=0.99 pass=True."
            ),
            "seed": seed,
            "ts_iso_landing": v["ts_iso"],
            "metrics_path": (
                f"data/exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_{seed}/"
                f"metrics.fresh_2026-06-30.json"
            ),
            "metrics_path_stale_local": (
                f"data/exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_{seed}/metrics.json"
                f" (STALE 2026-06-29 GPU_mandate_breach -- preserved by hd_metrics_sync merger; do not read)"
            ),
            "elapsed_s": v["elapsed_s"],
            "n_disc": v["n_disc"],
            "tier_counts": v["tier_counts"],
            "per_op_top1_mean": v["per_op_top1_mean"],
            "n_pairs_differ_6_of_6_all_op_mech_hashes_distinct_META_RULE_AX_satisfied": True,
            "supersedes_framing": (
                f"math::T3/EXP_substrate_pc_binding_operation_family_phase_diagram_v1_seed_{seed}_HONEST_NEGATIVE_"
                f"INFRA_DEP_GPU_mandate_breach_HDLAB_QUEUE_empty_no_mechanism_arm_ran_NOT_substantive_negative_"
                f"2026-06-30 (stale atom remains for historical record per Director)"
            ),
            "cert_increment_delta": 0,
        },
        "serves_capability": [
            "concept::CAP_substrate_binding_operation_phase_characterization"
        ],
    }


def binding_op_cross_seed_mm_atom() -> Dict[str, Any]:
    aid = (f"T3/EXP_substrate_pc_binding_operation_family_phase_diagram_v1_FULL_3seed_CROSS_SEED_AGG_MM_"
           f"per_op_characterization_stable_cross_seed_n_disc_7_to_8_of_48_low_disc_3_COMPETITIVE_1_DOMINATED_"
           f"actually_ran_FULL_at_17_43_UTC_supersedes_stale_AGG_HF_{DATE_ISO}")
    cs_top1 = {op: round(sum(BINDING_OP_PER_SEED_VET[s]["per_op_top1_mean"][op] for s in SEEDS) / 3, 4)
               for op in ["circular_convolution","element_wise_fhrr","hadamard_real","outer_product_tensor"]}
    return {
        "id": aid,
        "name": (
            "substrate_pc_binding_operation_family v1 FULL 3-seed CROSS_SEED_AGG MEASURED_MECHANISM: "
            "per-op characterization stable cross-seed (3-seed-mean top1: circ_conv=0.415 fhrr=0.407 "
            "hadamard=0.415 outer=0.352); 3 of 4 ops COMPETITIVE / outer_product DOMINATED across all 3 seeds; "
            "n_disc 7-8/48 below chain-grade threshold; MIDDLE_BAND stable cross-seed"
        ),
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": (
            "3-seed cross-seed aggregation of substrate_pc_binding_operation_family_phase_diagram v1 FULL "
            "(seeds 7/13/19 at 17:43-17:44 UTC 2026-06-30). 144 total inner phase pts. CROSS-SEED STABLE "
            "FINDINGS: per-op top1_mean cross-3-seed: "
            f"circular_convolution={cs_top1['circular_convolution']:.4f} (3-seed range 0.4125-0.4183), "
            f"element_wise_fhrr={cs_top1['element_wise_fhrr']:.4f} (range 0.4042-0.4100), "
            f"hadamard_real={cs_top1['hadamard_real']:.4f} (range 0.4125-0.4192), "
            f"outer_product_tensor={cs_top1['outer_product_tensor']:.4f} (range 0.3392-0.3583). "
            "Per-seed n_disc: 8/8/7 of 48 -- below chain-grade threshold >=14 in all 3 seeds; n_pairs_differ=6/6 "
            "in all 3 seeds (4 op mech-hashes distinct per seed, META_RULE_AX satisfied). op_tiers cross-seed "
            "stable: circ_conv/fhrr/hadamard = COMPETITIVE_BINDING; outer_product_tensor = DOMINATED_BINDING. "
            "positive_control cross-seed stable: circular_convolution N=4096 c=0.10 measured_top1=0.99 pass=True "
            "in all 3 seeds (mechanism plumbing works). cliff_locator cross-op-and-seed stable: N=1024 cliff "
            "at corruption 0.10-0.25; N=4096 cliff at 0.40; N=8192 cliff at 0.40 -- the substrate is "
            "corruption-tolerant up to ~0.40 at N>=4096 regardless of binding op choice within the COMPETITIVE "
            "set. INTERPRETATION: 3 of 4 binding ops produce equivalent substrate behavior under the tested "
            "(N, corruption) regime; outer_product_tensor underperforms by ~0.06 in top1_mean (~14% relative "
            "drop). The 30%-disc-threshold filter is too strict for the observed band -- no single (N, c, op) "
            "regime crosses 30% mechanism-vs-random advantage to call a HARD_PASS, but 5-6 MB + 2-3 HP points "
            "per seed do characterize partial regime mapping. TIER: MEASURED_MECHANISM with 3-seed-stable "
            "per-op characterization. Not chain-grade (disc threshold not met). delta=0. SUPERSEDES (framing): "
            "stale CROSS_SEED_AGG_HONEST_NEGATIVE_INFRA_DEP_GPU_mandate_breach atom from a009a44a -- both "
            "remain in ledger per Director directive."
        ),
        "aliases": [
            f"pc_binding_op_family_v1_3seed_CROSS_SEED_AGG_MM_{DATE_ISO}",
            "binding_op_cross_seed_agg_post_sync_MM",
        ],
        "metadata": {
            "provenance_quality": "MEASURED",
            "cert_status": "measured_mechanism",
            "cert_class": "cross_seed_phase_characterization_MM",
            "verdict": "MIDDLE_BAND",
            "verdict_subtype": "CROSS_SEED_STABLE_PER_OP_CHARACTERIZATION_3_COMPETITIVE_1_DOMINATED",
            "atomized_by": ATOMIZED_BY,
            "atomized_date": DATE_ISO,
            "verified_off_data": True,
            "verified_off_data_evidence": (
                ".venv python OFF-DATA recompute on 3 FRESH-PULLED metrics.fresh_2026-06-30.json files: "
                f"cross-seed top1_mean per op {cs_top1}; per-seed n_disc {{7:8, 13:8, 19:7}}; "
                "all 3 seeds verdict=MIDDLE_BAND run_mode=full cardinality 48/48 backend=torch.cuda; "
                "positive control circ_conv N=4096 c=0.10 top1=0.99 pass=True all 3 seeds; "
                "op_tiers stable {circ_conv: COMPETITIVE, fhrr: COMPETITIVE, hadamard: COMPETITIVE, outer: DOMINATED}; "
                "per-op 4 mech-hashes distinct per seed (12 hashes total, all distinct within seed)."
            ),
            "stage": 2,
            "n_seeds": 3,
            "seeds": SEEDS,
            "n_total_inner_pts": 144,
            "n_inner_pts_per_seed": 48,
            "n_ops": 4,
            "ops": ["circular_convolution", "element_wise_fhrr", "hadamard_real", "outer_product_tensor"],
            "cross_seed_top1_mean_per_op": cs_top1,
            "cross_seed_op_tiers": {
                "circular_convolution": "COMPETITIVE_BINDING",
                "element_wise_fhrr": "COMPETITIVE_BINDING",
                "hadamard_real": "COMPETITIVE_BINDING",
                "outer_product_tensor": "DOMINATED_BINDING",
            },
            "per_seed_atoms": {
                f"seed_{s}": (
                    f"math::T3/EXP_substrate_pc_binding_operation_family_phase_diagram_v1_FULL_seed_{s}_"
                    f"MEASURED_MECHANISM_per_op_characterization_3_of_4_COMPETITIVE_outer_product_DOMINATED_"
                    f"n_disc_{BINDING_OP_PER_SEED_VET[s]['n_disc']}_of_48_low_disc_arm_hashes_4_distinct_"
                    f"supersedes_stale_HF_GPU_mandate_breach_actually_ran_FULL_at_17_43_UTC_{DATE_ISO}"
                )
                for s in SEEDS
            },
            "supersedes_framing": (
                "math::T3/EXP_substrate_pc_binding_operation_family_phase_diagram_v1_3seed_CROSS_SEED_AGG_"
                "HONEST_NEGATIVE_INFRA_DEP_GPU_mandate_breach_all_3_seeds_CORRECTS_DIRECTOR_FRAMING_2026-06-30 "
                "(stale atom remains for historical record per Director)"
            ),
            "metrics_paths": [
                f"data/exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_{s}/"
                f"metrics.fresh_2026-06-30.json" for s in SEEDS
            ],
            "cert_increment_delta": 0,
        },
        "serves_capability": ["concept::CAP_substrate_binding_operation_phase_characterization"],
    }


# ---- REFUSE-GATE per-seed MM ----

REFUSE_GATE_PER_SEED_VET = {
    7:  {"verdict": "MIDDLE_BAND", "elapsed_s": 16.94, "ts_iso": "2026-06-30T17:44:04Z"},
    13: {"verdict": "MIDDLE_BAND", "elapsed_s": 15.93, "ts_iso": "2026-06-30T17:44:22Z"},
    19: {"verdict": "MIDDLE_BAND", "elapsed_s": 14.73, "ts_iso": "2026-06-30T17:44:39Z"},
}

REFUSE_GATE_PER_FAMILY_F1_MEAN = {
    "fixed_threshold": 0.75,
    "adaptive_bayesian_CI": 0.5,
    "learned_logistic": 0.75,
    "percentile_based": 0.5,
}


def refuse_gate_per_seed_mm_atom(seed: int) -> Dict[str, Any]:
    v = REFUSE_GATE_PER_SEED_VET[seed]
    aid = (f"T3/EXP_substrate_refuse_gate_adaptivity_phase_diagram_v1_FULL_seed_{seed}_"
           f"MEASURED_MECHANISM_per_family_characterization_2_of_4_distinct_mechanisms_"
           f"fixed_eq_learned_logistic_bayesian_CI_eq_percentile_n_family_pairs_differ_4_of_6_"
           f"family_axis_partial_collapse_self_flagged_by_cell_supersedes_stale_SELFTEST_OK_"
           f"actually_ran_FULL_at_17_44_UTC_{DATE_ISO}")
    return {
        "id": aid,
        "name": (
            f"substrate_refuse_gate_adaptivity v1 FULL seed_{seed} MEASURED_MECHANISM: 4 family slots collapse "
            f"to 2 distinct mechanism implementations (fixed_threshold==learned_logistic both COMPETITIVE; "
            f"adaptive_bayesian_CI==percentile_based both DOMINATED); n_family_pairs_differ=4/6 self-flagged by "
            f"cell; verdict MIDDLE_BAND honest; supersedes stale SELFTEST_OK atom"
        ),
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": (
            f"Stage 2 substrate refuse-gate adaptivity phase-diagram cell v1 seed_{seed} FULL run (actually "
            f"landed at {v['ts_iso']} on REMOTE CPU after proper queue_add, not the stale SELFTEST_OK from "
            f"earlier 2026-06-29 selftest-only artifact). 4 refuse-gate families (fixed_threshold, "
            f"adaptive_bayesian_CI, learned_logistic, percentile_based) compared across 4 regimes (PURE_IN, "
            f"PURE_OUT, NEAR_DOMAIN_MIXED, AMBIGUOUS_BOUNDARY) x 3 cal_sizes (64, 256, 1024) = 48 phase pts. "
            f"Verdict MIDDLE_BAND honest-low-disc: 0/48 HARD_PASS + MIDDLE_BAND below the chain-grade "
            f"threshold of 15. CRITICAL FORENSIC (META_RULE_AX adjacent): family_mech_hashes show "
            f"4-of-4-collapse-to-2: fixed_threshold and learned_logistic produce IDENTICAL "
            f"mechanism_hash=4542fd54a4a78bdf5caaa3f355717c7954a3cc2c6986dd22627e7a53f5717d3c; "
            f"adaptive_bayesian_CI and percentile_based produce IDENTICAL "
            f"mechanism_hash=48301b905c050fc6ae89c1b90aa447ee7985a140f1bd0a19070ac476a040e3a6. "
            f"4 family slots collapse to 2 distinct mechanism implementations. The cell HONESTLY self-flags "
            f"this: n_family_pairs_differ=4/6 (not 6/6); family_pair_distinctness reports "
            f"fixed_vs_learned_logistic=False and bayesian_CI_vs_percentile=False; verdict-banding correctly "
            f"defaults to MIDDLE_BAND (not HARD_PASS) and verdict_msg explicitly cites 'family pairs differ "
            f"(4/6)'. This is a SUCCESSFUL META_RULE_AX-honest-handling pattern (cell built-in cross-family "
            f"hash check + verdict-banding correctly degrades). Per-family f1_mean: fixed=0.75 bayesian=0.50 "
            f"learned=0.75 percentile=0.50 -- 2 COMPETITIVE / 2 DOMINATED. cal_size_sensitivity=0 across all "
            f"4 families (no calibration-size lift; the family choice trumps cal_size effect). Positive "
            f"control: fixed_threshold PURE_OUT_OF_DOMAIN cal=256 refuse_rate_floor=0.85 observed=1.000 "
            f"PASS. elapsed_s={v['elapsed_s']} backend=numpy.cpu. TIER: MEASURED_MECHANISM (per-seed per-family "
            f"characterization with HONEST partial-collapse self-flag; 3-seed agg in sibling atom). "
            f"SUPERSEDES (framing): stale SELFTEST_OK atom from a009a44a -- that atom records the 2026-06-29 "
            f"selftest-only output correctly, but the cell actually ran FULL at 17:44 UTC 2026-06-30 after "
            f"proper queue_add. Both atoms remain in ledger per Director directive."
        ),
        "aliases": [
            f"refuse_gate_adaptivity_v1_FULL_seed_{seed}_MM_{DATE_ISO}",
            f"refuse_gate_seed_{seed}_post_sync_MM",
        ],
        "metadata": {
            "provenance_quality": "MEASURED",
            "cert_status": "measured_mechanism",
            "cert_class": "per_seed_phase_characterization_MM_with_partial_family_collapse_honest_flag",
            "verdict": "MIDDLE_BAND",
            "verdict_subtype": (
                "ADAPTIVITY_DIFFERS_BUT_LOW_DISC_2_OF_4_FAMILY_HASHES_COLLAPSE_FIXED_EQ_LEARNED_LOGISTIC_"
                "BAYESIAN_CI_EQ_PERCENTILE_BASED_HONEST_FLAGGED_BY_CELL_n_family_pairs_4_of_6"
            ),
            "atomized_by": ATOMIZED_BY,
            "atomized_date": DATE_ISO,
            "verified_off_data": True,
            "verified_off_data_evidence": (
                f".venv python OFF-DATA recompute on FRESH-PULLED metrics.fresh_2026-06-30.json for seed_{seed}: "
                f"verdict=MIDDLE_BAND run_mode=full _phase=None cardinality_ok=True observed_n=48 expected_n=48 "
                f"elapsed_s={v['elapsed_s']} backend=numpy.cpu. per_family_f1_mean = "
                f"{REFUSE_GATE_PER_FAMILY_F1_MEAN}. family_mech_hashes confirms 2-of-4 collapse: "
                f"fixed_threshold and learned_logistic share 4542fd54...; adaptive_bayesian_CI and "
                f"percentile_based share 48301b90.... family_pair_distinctness reports 4 True + 2 False; "
                f"n_family_pairs_differ=4/6. positive_control fixed_threshold PURE_OUT cal=256 refuse_rate=1.000 "
                f"pass=True."
            ),
            "seed": seed,
            "ts_iso_landing": v["ts_iso"],
            "metrics_path": (
                f"data/exp_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_{seed}/"
                f"metrics.fresh_2026-06-30.json"
            ),
            "metrics_path_stale_local": (
                f"data/exp_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_{seed}/metrics.json"
                f" (STALE 2026-06-29 SELFTEST_OK -- preserved by hd_metrics_sync merger; do not read)"
            ),
            "elapsed_s": v["elapsed_s"],
            "n_disc": 0,
            "n_family_pairs_differ": 4,
            "n_family_pairs_total": 6,
            "family_axis_2_of_4_mechanism_hash_collapse_self_flagged_by_cell": True,
            "family_mech_hash_groups": {
                "group_a_fixed_threshold_and_learned_logistic": (
                    "4542fd54a4a78bdf5caaa3f355717c7954a3cc2c6986dd22627e7a53f5717d3c"
                ),
                "group_b_adaptive_bayesian_CI_and_percentile_based": (
                    "48301b905c050fc6ae89c1b90aa447ee7985a140f1bd0a19070ac476a040e3a6"
                ),
            },
            "per_family_f1_mean": REFUSE_GATE_PER_FAMILY_F1_MEAN,
            "per_family_tier": {
                "fixed_threshold": "COMPETITIVE_FAMILY",
                "adaptive_bayesian_CI": "DOMINATED_FAMILY",
                "learned_logistic": "COMPETITIVE_FAMILY",
                "percentile_based": "DOMINATED_FAMILY",
            },
            "positive_control_pass": True,
            "supersedes_framing": (
                f"math::T3/EXP_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_{seed}_HONEST_NEGATIVE_"
                f"INFRA_DEP_run_mode_selftest_only_FULL_never_landed_selftest_AMBIGUOUS_2_of_4_distinct_"
                f"decision_tuples_2026-06-30 (stale atom remains for historical record per Director)"
            ),
            "cert_increment_delta": 0,
        },
        "serves_capability": ["concept::CAP_substrate_refuse_gate_adaptivity_phase_characterization"],
    }


def refuse_gate_cross_seed_mm_atom() -> Dict[str, Any]:
    aid = (f"T3/EXP_substrate_refuse_gate_adaptivity_phase_diagram_v1_FULL_3seed_CROSS_SEED_AGG_MM_"
           f"per_family_characterization_stable_cross_seed_2_of_4_mech_hash_collapse_fixed_eq_learned_"
           f"bayesian_CI_eq_percentile_supersedes_stale_AGG_HF_actually_ran_FULL_at_17_44_UTC_{DATE_ISO}")
    return {
        "id": aid,
        "name": (
            "substrate_refuse_gate_adaptivity v1 FULL 3-seed CROSS_SEED_AGG MEASURED_MECHANISM: "
            "per-family characterization stable cross-seed (3-seed f1_mean: fixed=0.75 bayesian=0.50 "
            "learned=0.75 percentile=0.50); 4 family slots collapse to 2 distinct mechanism hashes per seed "
            "(fixed==learned; bayesian==percentile) -- honestly self-flagged by cell as n_pairs_differ=4/6"
        ),
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": (
            "3-seed cross-seed aggregation of substrate_refuse_gate_adaptivity_phase_diagram v1 FULL (seeds "
            "7/13/19 at 17:44 UTC 2026-06-30). 144 total inner phase pts. CROSS-SEED STABLE FINDINGS: "
            "per-family f1_mean is BIT-IDENTICAL across all 3 seeds (fixed=0.75 bayesian=0.50 learned=0.75 "
            "percentile=0.50) -- this is a regime-saturation signature, the family choice fully determines "
            "the observed f1 within the tested regime grid (cal_sizes are all in a saturated band). "
            "FORENSIC: family_mech_hashes are bit-identical PER SEED across the 2 grouped families: "
            "(fixed_threshold, learned_logistic) share one hash; (adaptive_bayesian_CI, percentile_based) "
            "share another. This collapse is STABLE CROSS-SEED (same partition cross-seed). The cell HONESTLY "
            "flags it via n_family_pairs_differ=4/6 and verdict-bands MIDDLE_BAND (NOT HARD_PASS) -- a "
            "successful META_RULE_AX-honest-handling pattern. cross-seed n_passing_points=0/0/0 (none of 48 "
            "pts per seed are HARD_PASS); verdict_msg cites '0/48 HARD_PASS+MIDDLE_BAND < threshold 15'. "
            "Positive control cross-seed stable: fixed_threshold PURE_OUT cal=256 observed_refuse_rate=1.000 "
            "PASS in all 3 seeds. INTERPRETATION: refuse-gate family-axis is implemented as 2 distinct "
            "mechanisms wearing 4 labels -- cell-author should either (a) implement 4 genuinely different "
            "families OR (b) re-label as 2-family comparison. Until then, the substrate-level finding is "
            "'fixed-threshold-family wins (f1=0.75) over bayesian-CI-family (f1=0.50)' which is the "
            "meaningful 2-family discrimination. TIER: MEASURED_MECHANISM with 3-seed-stable per-family "
            "characterization and honest 2-of-4 collapse flag. Not chain-grade (disc threshold not met; "
            "family-axis under-collapses to 2 mechanisms). delta=0. SUPERSEDES (framing): stale "
            "CROSS_SEED_AGG_HONEST_NEGATIVE_INFRA_DEP_selftest_only_FULL_never_landed_all_3_seeds atom from "
            "a009a44a -- both remain in ledger per Director directive."
        ),
        "aliases": [
            f"refuse_gate_adaptivity_v1_3seed_CROSS_SEED_AGG_MM_{DATE_ISO}",
            "refuse_gate_cross_seed_agg_post_sync_MM",
        ],
        "metadata": {
            "provenance_quality": "MEASURED",
            "cert_status": "measured_mechanism",
            "cert_class": (
                "cross_seed_phase_characterization_MM_with_partial_family_collapse_honest_flag_cross_seed_stable"
            ),
            "verdict": "MIDDLE_BAND",
            "verdict_subtype": (
                "CROSS_SEED_STABLE_PER_FAMILY_F1_MEAN_BIT_IDENTICAL_FAMILY_AXIS_2_OF_4_MECHANISM_HASH_COLLAPSE_"
                "fixed_eq_learned_bayesian_eq_percentile_HONEST_FLAGGED_AS_4_OF_6_PAIRS_DIFFER"
            ),
            "atomized_by": ATOMIZED_BY,
            "atomized_date": DATE_ISO,
            "verified_off_data": True,
            "verified_off_data_evidence": (
                ".venv python OFF-DATA recompute on 3 FRESH-PULLED metrics.fresh_2026-06-30.json files: "
                "per-family f1_mean bit-identical across 3 seeds = fixed=0.75 bayesian=0.50 learned=0.75 "
                "percentile=0.50. family_mech_hashes per seed: fixed_threshold and learned_logistic share "
                "4542fd54a4a78bdf5caaa3f355717c7954a3cc2c6986dd22627e7a53f5717d3c; adaptive_bayesian_CI and "
                "percentile_based share 48301b905c050fc6ae89c1b90aa447ee7985a140f1bd0a19070ac476a040e3a6. "
                "Hash partition stable cross-seed. n_family_pairs_differ=4/6 per seed (not 6/6). All 3 seeds "
                "verdict=MIDDLE_BAND run_mode=full cardinality 48/48 backend=numpy.cpu. positive_control "
                "fixed_threshold PURE_OUT cal=256 observed_refuse_rate=1.000 pass=True all 3 seeds."
            ),
            "stage": 2,
            "n_seeds": 3,
            "seeds": SEEDS,
            "n_total_inner_pts": 144,
            "n_inner_pts_per_seed": 48,
            "n_families_labeled": 4,
            "n_families_distinct_mechanism": 2,
            "families_labeled": [
                "fixed_threshold", "adaptive_bayesian_CI", "learned_logistic", "percentile_based"
            ],
            "family_mechanism_partition": {
                "group_a": ["fixed_threshold", "learned_logistic"],
                "group_b": ["adaptive_bayesian_CI", "percentile_based"],
            },
            "cross_seed_per_family_f1_mean": REFUSE_GATE_PER_FAMILY_F1_MEAN,
            "cross_seed_per_family_tier": {
                "fixed_threshold": "COMPETITIVE_FAMILY",
                "adaptive_bayesian_CI": "DOMINATED_FAMILY",
                "learned_logistic": "COMPETITIVE_FAMILY",
                "percentile_based": "DOMINATED_FAMILY",
            },
            "per_seed_atoms": {
                f"seed_{s}": (
                    f"math::T3/EXP_substrate_refuse_gate_adaptivity_phase_diagram_v1_FULL_seed_{s}_"
                    f"MEASURED_MECHANISM_per_family_characterization_2_of_4_distinct_mechanisms_"
                    f"fixed_eq_learned_logistic_bayesian_CI_eq_percentile_n_family_pairs_differ_4_of_6_"
                    f"family_axis_partial_collapse_self_flagged_by_cell_supersedes_stale_SELFTEST_OK_"
                    f"actually_ran_FULL_at_17_44_UTC_{DATE_ISO}"
                )
                for s in SEEDS
            },
            "supersedes_framing": (
                "math::T3/EXP_substrate_refuse_gate_adaptivity_phase_diagram_v1_3seed_CROSS_SEED_AGG_HONEST_"
                "NEGATIVE_INFRA_DEP_selftest_only_FULL_never_landed_all_3_seeds_CORRECTS_DIRECTOR_FRAMING_"
                "2026-06-30 (stale atom remains for historical record per Director)"
            ),
            "metrics_paths": [
                f"data/exp_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_{s}/"
                f"metrics.fresh_2026-06-30.json" for s in SEEDS
            ],
            "cert_increment_delta": 0,
        },
        "serves_capability": ["concept::CAP_substrate_refuse_gate_adaptivity_phase_characterization"],
    }


# ---- A5 atomic write ----

def append_jsonl_atomic(path: Path, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    n_before = 0
    if path.exists():
        with open(path, "rb") as f:
            for _ in f:
                n_before += 1

    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}.{int(time.time()*1000)}")
    if path.exists():
        with open(path, "rb") as fr, open(tmp, "wb") as fw:
            fw.write(fr.read())
            for e in entries:
                line = json.dumps(e, ensure_ascii=False, separators=(",", ":")) + "\n"
                fw.write(line.encode("utf-8"))
    else:
        with open(tmp, "wb") as fw:
            for e in entries:
                line = json.dumps(e, ensure_ascii=False, separators=(",", ":")) + "\n"
                fw.write(line.encode("utf-8"))

    os.replace(tmp, path)

    n_after = 0
    written_keys = set()
    with open(path, "rb") as f:
        for line_b in f:
            n_after += 1
            try:
                d = json.loads(line_b.decode("utf-8", errors="replace"))
                key = d.get("id") or d.get("atom_id")
                if key is not None:
                    written_keys.add(key)
            except Exception:
                pass

    expected_after = n_before + len(entries)
    ok = n_after == expected_after
    for e in entries:
        key = e.get("id") or e.get("atom_id")
        if key is not None and key not in written_keys:
            ok = False

    return {
        "path": str(path),
        "n_before": n_before,
        "n_after": n_after,
        "n_appended": len(entries),
        "expected_after": expected_after,
        "integrity_ok": ok,
    }


def idempotent_filter(path: Path, atoms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    existing = set()
    if path.exists():
        with open(path, "rb") as f:
            for line_b in f:
                try:
                    d = json.loads(line_b.decode("utf-8", errors="replace"))
                    if d.get("id"):
                        existing.add(d["id"])
                except Exception:
                    pass
    return [a for a in atoms if a["id"] not in existing]


def main():
    repo = Path("d:/AI/hd-instrument")
    math_atoms_p = repo / "data" / "substrate_index" / "math" / "atoms.jsonl"
    math_audit_p = repo / "data" / "substrate_index" / "math" / "audit.jsonl"
    cert_ledger_p = repo / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"

    # Build atoms (8 total: 3+1 binding-op + 3+1 refuse-gate)
    bop_per_seed = [binding_op_per_seed_mm_atom(s) for s in SEEDS]
    bop_cross = binding_op_cross_seed_mm_atom()
    rg_per_seed = [refuse_gate_per_seed_mm_atom(s) for s in SEEDS]
    rg_cross = refuse_gate_cross_seed_mm_atom()

    math_atoms = bop_per_seed + [bop_cross] + rg_per_seed + [rg_cross]
    assert len(math_atoms) == 8

    print("=== A5-DISCIPLINED ATOMIZE 8atom binding+refuse post-sync 2026-06-30 ===")
    for a in math_atoms:
        print(f"  math/{a['id']}")
    print()

    ts = time.time()
    # 8 cert_ledger entries (all delta=0; MM tier per Director ACK)
    ledger_entries = []
    for i, a in enumerate(math_atoms):
        ledger_entries.append({
            "ts": ts + 0.001 * (i + 1),
            "op": "cert_ruling_promotion_measured_mechanism",
            "atom_id": f"math::{a['id']}",
            "cert_status": "measured_mechanism",
            "cert_class": a["metadata"]["cert_class"],
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": "n/a-2026-06-30-batch-binding-refuse-post-sync-8atoms",
            "verdict": (
                f"MEASURED_MECHANISM_post_sync_8atom_batch_{a['metadata']['verdict_subtype']}_"
                f"actually_ran_FULL_at_17_43_to_17_44_UTC_supersedes_stale_HF_or_SELFTEST_OK_"
                f"atom_from_a009a44a_in_framing_sense_both_remain_in_ledger_for_historical_record_"
                f"per_Director_directive_delta_0"
            ),
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "atom_qualified_id": f"math::{a['id']}",
                "metrics_path_fresh": a["metadata"].get("metrics_path") or (
                    a["metadata"].get("metrics_paths", [None])[0]
                ),
                "supersedes_framing": a["metadata"].get("supersedes_framing"),
            },
            "supersedes": a["metadata"].get("supersedes_framing"),
            "note": (
                f"binding_refuse_post_sync_8atom_2026-06-30/"
                f"{'binding_op' if 'pc_binding_operation_family' in a['id'] else 'refuse_gate'}/"
                f"{'cross_seed_agg' if 'CROSS_SEED_AGG' in a['id'] else 'per_seed'}"
            ),
        })
    assert len(ledger_entries) == 8

    # Audit rows
    audit_rows = [
        {
            "ts": ts,
            "op": "atomize",
            "atom_id": a["id"],
            "corpus": "math",
            "cert_status": a["metadata"]["cert_status"],
            "atomized_by": ATOMIZED_BY,
            "cell_commit": "n/a-2026-06-30-batch-binding-refuse-post-sync-8atoms",
        }
        for a in math_atoms
    ]

    # 1. math/atoms idempotent
    math_to_write = idempotent_filter(math_atoms_p, math_atoms)
    if math_to_write:
        r1 = append_jsonl_atomic(math_atoms_p, math_to_write)
        print(f"math/atoms.jsonl: {r1}")
        assert r1["integrity_ok"], "math/atoms integrity FAILED"
    else:
        print(f"math/atoms.jsonl: all 8 atoms present (idempotent skip)")
        r1 = {"integrity_ok": True, "n_appended": 0}

    # 2. math/audit
    r2 = append_jsonl_atomic(math_audit_p, audit_rows)
    print(f"math/audit.jsonl: {r2}")
    assert r2["integrity_ok"], "math/audit integrity FAILED"

    # 3. cert_ledger
    r5 = append_jsonl_atomic(cert_ledger_p, ledger_entries)
    print(f"meta/cert_ledger.jsonl: {r5}")
    assert r5["integrity_ok"], "cert_ledger integrity FAILED"

    print()
    print("=== ALL A5-DISCIPLINED ATOMIC WRITES OK ===")
    print(f"  CERT delta net=0 (8 MM atoms; delta=0 per Director MM tier)")
    print(f"  MEMORY.md headline post-batch: still 634 (cumulative w/ hippo v2 MM +1 from prior batch)")
    print()
    print(f"  Atom IDs:")
    for a in math_atoms:
        print(f"    - math::{a['id']}")


if __name__ == "__main__":
    main()
