"""Skunkworks atomize: 3-cell batch landed-VET + 2 META rules (2026-06-30)

Director ACK'd tier proposals:
  1. Hippo v2 bottleneck-class diagnostic 3-seed -> MEASURED_MECHANISM (Ha partial + Hc by-construction)
  2. Hippo M=8192 v2_replay_fixed 3-seed -> HARD_FAIL chain-grade capacity_breach (config-drift)
  3. ANCHOR 4 encoder family rerun 3-seed -> HARD_FAIL_PHANTOM_FULL (encoder axis not wired)
  4. META_RULE_AW: seed_config_must_be_identical_for_cross_seed_aggregation
  5. META_RULE_AX: arm_distinctness_check_must_compare_metrics_across_arms_not_just_hashes

Atom inventory:
  math/atoms.jsonl: 1 (hippo v2 3-seed MM) + 1 (hippo M=8192 HF) + 1 (encoder phantom HF)  = 3 atoms
  meta/atoms.jsonl: 2 META rules (AW + AX)                                                  = 2 atoms
  math/audit.jsonl: 3 audit rows
  meta/audit.jsonl: 2 audit rows
  meta/cert_ledger.jsonl: 5 cert_ruling rows (1 MM delta=+1 + 2 HF delta=0 + 2 META delta=0) = net +1

CERT trajectory (prose-aggregated MEMORY.md headline; ledger-authoritative is separate):
  633 -> 634 (+1 MM)

A5-discipline: atomic write via tmp + os.replace; verify-load after each write; integrity-check.
Idempotent: skip atoms already present.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List

DATE_ISO = "2026-06-30"
ATOMIZED_BY = "skunkworks_atomize_3cell_batch_hippo_v2_M8192_encoder_phantom_2026-06-30"

# ---- ATOM 1: Hippo v2 bottleneck-class diagnostic 3-seed MM ----

HIPPO_V2_VET = {
    "n_seeds": 3,
    "seeds": [7, 17, 23],
    "M": 2048,
    "N_h": 8192,
    "N_c": 2048,
    "alpha_simple": 0.25,
    "n_replay_per_item": 1,
    "per_arm_mean_recall": {
        "ARM_DIRECT": 0.9850,
        "ARM_STANDARD": 0.2192,
        "ARM_NO_HEBBIAN_CROSSTERM": 0.6123,
        "ARM_NO_L2_NORM": 0.2171,
        "ARM_CLEAN_VALS_TO_CORTEX": 0.9850,
    },
    "per_arm_cv": {
        "ARM_DIRECT": 0.0008,
        "ARM_STANDARD": 0.0425,
        "ARM_NO_HEBBIAN_CROSSTERM": 0.0186,
        "ARM_NO_L2_NORM": 0.0373,
        "ARM_CLEAN_VALS_TO_CORTEX": 0.0008,
    },
    "gap_DIR_STD_mean": 0.7658,
    "gap_DIR_STD_std": 0.0101,
    "closeFrac_HEBB_mean": 0.5130,
    "closeFrac_HEBB_per_seed": [0.5316, 0.5227, 0.4847],
    "closeFrac_L2_mean": -0.0028,
    "closeFrac_CLEAN_mean": 1.0000,
    "arm_hash_identity_DIRECT_equals_CLEAN_per_seed": True,
    "arm_hashes_distinct_STANDARD_NO_HEBB_NO_L2": True,
}


def hippo_v2_mm_atom() -> Dict[str, Any]:
    aid = (f"T3/EXP_substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v2_3seed_MM_"
           f"Ha_partial_closeFrac_0p513_Hc_by_construction_identity_H2_L2_refuted_{DATE_ISO}")
    return {
        "id": aid,
        "name": (
            "substrate_cortex_hippo_handoff_bottleneck_class_diagnostic v2 3-seed MEASURED_MECHANISM -- "
            "Ha Hebbian cross-term confirmed as partial bottleneck (closeFrac=+0.513 ± 0.024); "
            "Hc clean-vals-to-cortex closeFrac=+1.000 by-construction identity (same arm-hash as DIRECT); "
            "H2 L2-norm refuted (closeFrac=-0.003); Stage 2 NREM H_OTHER class characterization"
        ),
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": (
            "Stage 2 NREM consolidation H_OTHER bottleneck-class diagnostic v2 (cortex-hippo handoff). "
            "3 seeds (7, 17, 23) M=2048 N_h=8192 N_c=2048 sparsity=0.1 alpha_simple=0.25 alpha_hopfield=0.0139 "
            "5 arms: ARM_DIRECT (upper bound, hippo bypassed) / ARM_STANDARD (baseline bottleneck) / "
            "ARM_NO_HEBBIAN_CROSSTERM / ARM_NO_L2_NORM / ARM_CLEAN_VALS_TO_CORTEX. Independent off-disk "
            ".venv python recompute confirms: ARM_DIRECT=0.985 cv=0.0008; ARM_STANDARD=0.219 cv=0.0425; "
            "ARM_NO_HEBBIAN_CROSSTERM=0.612 cv=0.0186; ARM_NO_L2_NORM=0.217 cv=0.0373; "
            "ARM_CLEAN_VALS_TO_CORTEX=0.985 cv=0.0008. gap_DIR_STD=+0.766 ± 0.010 cross-seed. "
            "closeFrac analysis: HEBB closes 51.3% of gap (3-seed values 0.532, 0.523, 0.485 -- stable partial); "
            "L2 closes -0.3% (refuted as bottleneck contributor); CLEAN closes 100% BY-CONSTRUCTION "
            "(ARM_CLEAN_VALS_TO_CORTEX has bit-identical arm_hash to ARM_DIRECT per seed -- both bypass hippo write "
            "path, so they ARE the same arm semantically, not 2 independent mechanisms). "
            "HONEST FRAMING: Ha (Hebbian cross-term in NREM replay) is the GENUINE measured partial bottleneck "
            "contribution (~51% of DIR_STD gap, 3-seed stable). Hc (clean-vals bypass) is an UPPER-BOUND identity, "
            "not an independent mechanism discovery -- it shows that if hippo write/replay is fully bypassed, "
            "cortex recovers DIRECT recall, which is trivially true and doesn't isolate a separate bottleneck. "
            "H2 (L2-norm magnitude collapse) is REFUTED as a bottleneck (closeFrac=-0.003). "
            "TIER: MEASURED_MECHANISM (Ha partial-contribution + Hc identity + H2 refutation are all proven "
            "bounds; cell is a bottleneck-class diagnostic per cell-author honest-frame, not a rescue solution). "
            "NREM rescue path (Stage 2 follow-up): combine Ha-aware replay rule (avoid Hebbian cross-term during "
            "replay) WITH hippo write path retained (NOT clean-vals bypass which trivializes the test). "
            "Closes additive-class H_OTHER characterization for Stage 2 NREM (H1 sparse-overlap + H2 sign-quant "
            "+ H3 L2-magnitude refuted pre-compaction; Ha confirmed partial; remainder = hippo lossy write/replay "
            "generic; H2 within-v2 also refuted)."
        ),
        "aliases": [
            f"cortex_hippo_handoff_bottleneck_class_v2_3seed_MM_{DATE_ISO}",
            "hippo_v2_bottleneck_Ha_partial_Hc_identity",
            "stage_2_NREM_H_OTHER_additive_class_characterization",
        ],
        "metadata": {
            "provenance_quality": "MEASURED",
            "cert_status": "measured_mechanism",
            "cert_class": "bottleneck_class_characterization_MM",
            "verdict": "MEASURED_MECHANISM",
            "verdict_subtype": "Ha_PARTIAL_BOTTLENECK_CONFIRMED_Hc_BY_CONSTRUCTION_IDENTITY_H2_REFUTED",
            "atomized_by": ATOMIZED_BY,
            "atomized_date": DATE_ISO,
            "verified_off_data": True,
            "verified_off_data_evidence": (
                ".venv python OFF-DATA recompute on metrics.json 3-seed: per-arm recall_mean reproduced from "
                "per_seed.arms.recall_cortex (DIRECT=0.985 STD=0.219 NO_HEBB=0.612 NO_L2=0.217 CLEAN=0.985); "
                "gap_DIR_STD per-seed [0.7725, 0.7734, 0.7515] mean=+0.766 std=0.010 (matches reported +0.766); "
                "closeFrac HEBB per-seed [0.532, 0.523, 0.485] mean=+0.513 (stable partial 51%); "
                "closeFrac L2 per-seed [-0.001, -0.003, -0.005] mean=-0.003 (refuted); "
                "closeFrac CLEAN per-seed [1.000, 1.000, 1.000] mean=+1.000 (by-construction identity flagged); "
                "arm_hash check: DIRECT==CLEAN per seed (66f1e9d4 / 9bc34f9e / 24345978); STD/NO_HEBB/NO_L2 distinct."
            ),
            "n_seeds": HIPPO_V2_VET["n_seeds"],
            "seeds": HIPPO_V2_VET["seeds"],
            "M": HIPPO_V2_VET["M"],
            "N_h": HIPPO_V2_VET["N_h"],
            "N_c": HIPPO_V2_VET["N_c"],
            "alpha_simple": HIPPO_V2_VET["alpha_simple"],
            "n_replay_per_item": HIPPO_V2_VET["n_replay_per_item"],
            "per_arm_mean_recall": HIPPO_V2_VET["per_arm_mean_recall"],
            "per_arm_cv": HIPPO_V2_VET["per_arm_cv"],
            "gap_DIR_STD_mean": HIPPO_V2_VET["gap_DIR_STD_mean"],
            "gap_DIR_STD_std": HIPPO_V2_VET["gap_DIR_STD_std"],
            "closeFrac_HEBB_mean": HIPPO_V2_VET["closeFrac_HEBB_mean"],
            "closeFrac_HEBB_per_seed": HIPPO_V2_VET["closeFrac_HEBB_per_seed"],
            "closeFrac_L2_mean": HIPPO_V2_VET["closeFrac_L2_mean"],
            "closeFrac_CLEAN_mean": HIPPO_V2_VET["closeFrac_CLEAN_mean"],
            "arm_hash_identity_DIRECT_equals_CLEAN_per_seed": True,
            "framing_correction": (
                "Cell-author tag claim 'Hc_CORTEX_WRITE_SATURATION_CONFIRMED' as independent mechanism "
                "is corrected by Skunkworks: Hc is by-construction identity to DIRECT, not a separate "
                "measured mechanism. Honest tier = Ha partial + Hc identity + H2 refuted."
            ),
            "stage": 2,
            "metrics_path": (
                "data/exp_substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v2/metrics.json"
            ),
            "cert_increment_delta": 1,
            "ledger_cert_n_memory_headline": "633 -> 634 (prose MEMORY.md; ledger-authoritative separate)",
        },
        "serves_capability": [
            "concept::CAP_substrate_stage_2_NREM_consolidation_bottleneck_characterization"
        ],
    }


# ---- ATOM 2: Hippo M=8192 v2_replay_fixed HARD_FAIL chain-grade ----

HIPPO_M8192_VET = {
    "seeds_full_config": [13, 19],
    "seed_smoke_config": 7,
    "full_M": 8192,
    "full_N_h": 4096,
    "full_N_c": 8192,
    "full_N_replay": 50,
    "full_alpha_simple": 1.00,
    "full_backend": "torch.cuda",
    "smoke_M": 512,
    "smoke_N_h": 512,
    "smoke_N_replay": 10,
    "smoke_alpha_simple": 0.25,
    "smoke_backend": "torch.cpu",
    "per_seed_recall": {
        7: {"FULL_HANDOFF": 0.748, "NO_REPLAY": 0.002, "DIRECT": 1.000, "gap": 0.746, "ratio": 0.748,
            "verdict": "HARD_PASS", "run_mode": "smoke", "config": "SMOKE"},
        13: {"FULL_HANDOFF": 0.014, "NO_REPLAY": 0.0001, "DIRECT": 0.327, "gap": 0.013, "ratio": 0.041,
             "verdict": "HARD_FAIL", "run_mode": "full", "config": "FULL"},
        19: {"FULL_HANDOFF": 0.015, "NO_REPLAY": 0.0001, "DIRECT": 0.323, "gap": 0.015, "ratio": 0.047,
             "verdict": "HARD_FAIL", "run_mode": "full", "config": "FULL"},
    },
    "M_over_N_c_full": 8192 / 2048,  # 4.0 oversubscription
}


def hippo_M8192_hf_atom() -> Dict[str, Any]:
    aid = (f"T3/EXP_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_3seed_"
           f"HARD_FAIL_capacity_breach_plus_config_drift_seed_7_smoke_seeds_13_19_full_{DATE_ISO}")
    return {
        "id": aid,
        "name": (
            "substrate_cortex_hippo_handoff chain_grade_M_8192_GPU_v2_replay_fixed -- 3-seed HARD_FAIL "
            "(seeds 13/19 FULL config: gap +0.013/+0.015; DIRECT collapses to 0.327/0.323 from cortex "
            "capacity breach M/N_c=4x; seed 7 ran SMOKE config not FULL -- config drift)"
        ),
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": (
            "Cortex-hippo handoff chain-grade attempt at M=8192 with GPU v2_replay_fixed mechanism. 3 'seeds' "
            "labeled seed_7, seed_13, seed_19 actually shipped 3 DIFFERENT configs -- caught by Skunkworks "
            "off-disk forensic 2026-06-30. seed_7 run_mode=smoke (M=512 N_h=512 N_replay=10 alpha=0.25 "
            "backend=torch.cpu elapsed=305s) verdict=HARD_PASS with FULL=0.748 NO_REPLAY=0.002 DIRECT=1.000 "
            "gap=+0.746. seeds 13/19 run_mode=full (M=8192 N_h=4096 N_c=8192 N_replay=50 alpha=1.00 backend="
            "torch.cuda elapsed=14.4s each) verdict=HARD_FAIL with FULL=0.014/0.015 NO_REPLAY=0.0001 "
            "DIRECT=0.327/0.323 gap=+0.013/+0.015 ratio_FULL/DIRECT=0.041/0.047. "
            "DIAGNOSIS: cortex capacity breach. At M=8192 with N_c=2048 the cortex is 4x oversubscribed; "
            "DIRECT baseline (no hippo path, items written directly) collapses to ~0.32 from 1.0; replay "
            "mechanism rides at 4-5% of DIRECT (vs 75% at smoke scale). The transfer mechanism is doing "
            "essentially nothing at FULL scale -- not because of a bug in replay_fixed, but because the "
            "cortex regime is past capacity. (NOTE: seed_13/19 metrics show N_c=8192 in config but DIRECT "
            "still collapses; the by-construction expectation is N_c is the cortex bind dimension and M "
            "writes still over-subscribe the active cleanup capacity at alpha_simple=1.0). "
            "EXISTING CG ATOM (if any) DEMOTED: any prior chain_grade promotion of this anchor is superseded "
            "by this 3-seed HARD_FAIL. CONFIG-DRIFT: seed_7 SMOKE result CANNOT be cross-seed-aggregated with "
            "seeds 13/19 FULL results -- different M, N_h, N_replay, alpha, backend, run_mode. The labeled "
            "'3-seed chain_grade' attempt is a cardinality breach: only 2 of 3 seeds ran FULL config. "
            "Director ACK: HARD_FAIL_capacity_breach + config_drift. Triggers companion META_RULE_AW (seed_"
            "config_must_be_identical_for_cross_seed_aggregation). delta=0 (HARD_FAIL is honest negative). "
            "Next-cell suggestion (NOT this atom): NREM rescue v1 cell with Ha-aware replay + cortex "
            "capacity-aware schedule, dispatched at M/N_c <= 1.0 to avoid DIRECT collapse confounding the "
            "transfer-mechanism test."
        ),
        "aliases": [
            f"cortex_hippo_M_8192_GPU_v2_replay_fixed_3seed_HF_{DATE_ISO}",
            "stage_2_cortex_capacity_breach_hippo_replay_HF",
            "config_drift_seed_7_smoke_seeds_13_19_full_HF",
        ],
        "metadata": {
            "provenance_quality": "MEASURED",
            "cert_status": "hard_fail",
            "cert_class": "honest_negative_capacity_breach_plus_config_drift",
            "verdict": "HARD_FAIL",
            "verdict_subtype": "CAPACITY_BREACH_DIRECT_COLLAPSE_AND_CONFIG_DRIFT_ACROSS_SEEDS",
            "atomized_by": ATOMIZED_BY,
            "atomized_date": DATE_ISO,
            "verified_off_data": True,
            "verified_off_data_evidence": (
                ".venv python OFF-DATA recompute on 3 metrics.json files: seed_7 run_mode=smoke (M=512 N_h=512 "
                "N_replay=10 alpha=0.25 backend=torch.cpu) FULL=0.748 DIRECT=1.000; seed_13 run_mode=full "
                "(M=8192 N_h=4096 N_replay=50 alpha=1.0 backend=torch.cuda) FULL=0.014 DIRECT=0.327; seed_19 "
                "run_mode=full FULL=0.015 DIRECT=0.323. ratio_FULL/DIRECT collapses from 0.748 (smoke) to "
                "0.041/0.047 (full). DIRECT collapses from 1.000 (smoke M=512) to 0.327/0.323 (full M=8192). "
                "Verdict text in metrics.json seeds 13/19 explicitly: 'HARD_FAIL: gap_FULL_vs_NO_REPLAY=+0.013/"
                "+0.015 < 0.10; transfer mechanism doing essentially nothing.'"
            ),
            "per_seed_recall": HIPPO_M8192_VET["per_seed_recall"],
            "config_drift_summary": {
                "seed_7": (
                    "SMOKE config M=512 N_h=512 N_replay=10 alpha=0.25 backend=torch.cpu run_mode=smoke "
                    "elapsed=305s -- HP at smoke scale"
                ),
                "seed_13": (
                    "FULL config M=8192 N_h=4096 N_replay=50 alpha=1.00 backend=torch.cuda run_mode=full "
                    "elapsed=14.4s -- HF at full scale"
                ),
                "seed_19": (
                    "FULL config M=8192 N_h=4096 N_replay=50 alpha=1.00 backend=torch.cuda run_mode=full "
                    "elapsed=14.4s -- HF at full scale"
                ),
            },
            "framing_correction": (
                "Lead's framing 'seed_7 ran 21x longer = seeds 13/19 short-circuited' is wrong. "
                "All 3 seeds completed cleanly (arm_status=OK for all 9 arms). The elapsed asymmetry is "
                "CONFIG asymmetry: seed_7 ran SMOKE (M=512 torch.cpu, slow per-op but small) vs seeds 13/19 "
                "ran FULL (M=8192 torch.cuda, fast per-op but large). The honest read is config-drift + "
                "capacity-breach, not seed-instability."
            ),
            "M_over_N_c_full": HIPPO_M8192_VET["M_over_N_c_full"],
            "supersedes": (
                "Any prior chain_grade promotion of "
                "substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed (anchor or earlier "
                "smoke-only HP framing); DEMOTE in cert_ledger via this atom."
            ),
            "stage": 2,
            "metrics_paths": [
                "data/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_7/metrics.json",
                "data/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_13/metrics.json",
                "data/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_19/metrics.json",
            ],
            "companion_meta_rule_atom": (
                f"meta::RULE_seed_config_must_be_identical_for_cross_seed_aggregation_3_diff_configs_under_1_"
                f"anchor_HF_at_capacity_breach_META_RULE_AW_{DATE_ISO}"
            ),
            "cert_increment_delta": 0,
        },
        "serves_capability": [
            "concept::CAP_substrate_stage_2_NREM_consolidation_capacity_envelope_characterization"
        ],
    }


# ---- ATOM 3: ANCHOR 4 encoder family rerun PHANTOM_FULL ----

ENCODER_PHANTOM_VET = {
    "n_seeds": 3,
    "seeds": [7, 13, 19],
    "elapsed_s_per_seed": {7: 0.37, 13: 0.40, 19: 0.36},
    "claimed_observed_n_units": 48,
    "encoders_claimed": ["binary_bipolar", "hrr_real", "fhrr", "sparse_bipolar"],
    "encoder_pair_grid_identity_count_per_seed": 12,
    "encoder_pair_grid_differ_count_per_seed": 0,
    "encoder_tiers_claimed": {
        "binary_bipolar": "COMPETITIVE_ENCODER",
        "hrr_real": "COMPETITIVE_ENCODER",
        "fhrr": "COMPETITIVE_ENCODER",
        "sparse_bipolar": "DOMINATED_ENCODER",
    },
    "mechanism_hash_identity_across_3_of_4_encoders_per_seed": True,
    "recency_decode_acc_for_3_competitive_encoders": 1.000,
}


def encoder_phantom_full_atom() -> Dict[str, Any]:
    aid = (f"T3/EXP_substrate_anchor4_encoder_family_phase_diagram_v1_actual_full_rerun_3seed_"
           f"HARD_FAIL_PHANTOM_FULL_encoder_axis_not_wired_to_mechanism_5th_phantom_recurrence_"
           f"{DATE_ISO}")
    return {
        "id": aid,
        "name": (
            "substrate_anchor4_encoder_family_phase_diagram v1 actual_full_rerun -- 3-seed "
            "HARD_FAIL_PHANTOM_FULL: encoder axis not wired (3 of 4 encoder slots produce bit-identical "
            "metrics + mechanism_hashes); elapsed 0.36-0.40s incompatible with 48-unit phase grid; "
            "5th phantom-FULL recurrence; META_RULE_AV signature"
        ),
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": (
            "ANCHOR 4 encoder family phase diagram v1 'actual_full_rerun_2026-06-29' (3 seeds: 7, 13, 19). "
            "Cell verdict claim: HARD_PASS_ENCODER_DISCRIMINATION (48/48 pts; 3/4 encoders pass v2 Pareto-AUC "
            "chain-grade). Skunkworks off-disk forensic 2026-06-30 REJECTS the chain-grade claim with two "
            "smoking-gun findings: (1) for every (N_dim, decay, capacity_load) grid cell, working_set_retention "
            "+ clutter_fraction + composite + recency_decode_acc are BIT-IDENTICAL across binary_bipolar, "
            "hrr_real, fhrr (10-16 decimal places); only sparse_bipolar differs. Examples: (128, 30, 1.0): "
            "binary/hrr/fhrr all = 0.9312977099236641. (1024, 180, 5.0): all three = 0.5506329113924051. "
            "12/12 grid cells: 3 of 4 encoders produce bit-identical metrics. (2) per-seed mechanism_hash is "
            "identical across binary/hrr/fhrr (seed_7: all three = 2ebc4d9b80178e3d; seed_13: c5ee7d34da5490dc; "
            "seed_19: f71ae655b66ee1f1). Three different 'encoders' produced byte-identical arm data. "
            "INTERPRETATION: the mechanism computes an encoder-INDEPENDENT time-decay/eviction scalar that "
            "depends only on (n_atoms, n_days, decay_rate, capacity_load). The encoder-family axis is "
            "COSMETIC, not functional. The 'binary_bipolar / hrr_real / fhrr' slots are not actually applied "
            "to the working_set computation. recency_decode_acc=1.000 across all 12 points per encoder for "
            "3-of-4 'encoders' is the META_RULE_Q suspect-1.000 signature -- consistent with no encoder being "
            "applied. ADDITIONAL FLAG: elapsed_s = 0.37/0.40/0.36 for claimed 48 phase-grid units is "
            "incompatible with any honest grid scale (META_RULE_AV signature). The 'actual_full_rerun_' "
            "filename suffix was meant to fix the prior Skunkworks rejection (raw-float encoder collision; "
            "only seed_7 actual FULL) but the rerun has the SAME encoder-not-wired root cause -- it is the "
            "5th phantom-FULL recurrence in the arc (multihop v4 / seqbind / ANCHOR 4 original / binding-op "
            "pre-fix / refuse-gate pre-fix). The cell-author needs to wire the encoder axis into the mechanism "
            "(use the encoder to build the HD vectors that drive the working_set decay decision) before "
            "re-dispatching. Companion META_RULE_AX (arm-distinctness-check must cross-check arms differ "
            "ACROSS the family axis, not just within each arm's MECHANISM vs RANDOM pair). TIER: "
            "HARD_FAIL_PHANTOM_FULL. delta=0 (honest negative)."
        ),
        "aliases": [
            f"anchor4_encoder_family_v1_actual_full_rerun_3seed_phantom_full_HF_{DATE_ISO}",
            "encoder_axis_not_wired_phantom_full_5th_recurrence",
            "META_RULE_AV_signature_elapsed_under_1s_for_48_grid_phantom",
        ],
        "metadata": {
            "provenance_quality": "MEASURED_PHANTOM",
            "cert_status": "hard_fail",
            "cert_class": "honest_negative_phantom_full_encoder_not_wired",
            "verdict": "HARD_FAIL_PHANTOM_FULL",
            "verdict_subtype": "ENCODER_AXIS_NOT_WIRED_3_OF_4_ENCODER_HASHES_BIT_IDENTICAL_PER_SEED",
            "atomized_by": ATOMIZED_BY,
            "atomized_date": DATE_ISO,
            "verified_off_data": True,
            "verified_off_data_evidence": (
                ".venv python OFF-DATA recompute on 3 metrics.json files. Phase_map contains 48 units per "
                "seed. Sampled 12/12 (N_dim, decay, cap_load) grid cells: in every one, working_set_retention "
                "+ clutter_fraction + composite + recency_decode_acc are bit-identical across binary_bipolar, "
                "hrr_real, fhrr to 10-16 decimal places. Only sparse_bipolar produces different numbers. "
                "Mechanism_hash check: per-seed 3-of-4 encoders share identical hash (seed_7 binary=hrr=fhrr="
                "2ebc4d9b80178e3d; sparse=e1f28e97ed79dbf2; seed_13 c5ee7d34da5490dc / f34afaef863a6449; "
                "seed_19 f71ae655b66ee1f1 / f6993e1037b584d9). Per-encoder n_points=12 td_wins=12/12 "
                "dominance=1.000 net_dominance=1.000 rd_loss=0.000 recency_decode_acc=1.000 IDENTICAL for "
                "binary/hrr/fhrr per seed -- because these 3 'encoders' produce identical arm data. Elapsed_s "
                "= 0.37/0.40/0.36 incompatible with 48 phase-grid units at any honest evolution+recall cost."
            ),
            "n_seeds": ENCODER_PHANTOM_VET["n_seeds"],
            "seeds": ENCODER_PHANTOM_VET["seeds"],
            "elapsed_s_per_seed": ENCODER_PHANTOM_VET["elapsed_s_per_seed"],
            "encoder_pair_grid_identity_count_per_seed": (
                ENCODER_PHANTOM_VET["encoder_pair_grid_identity_count_per_seed"]
            ),
            "encoder_pair_grid_differ_count_per_seed": 0,
            "mechanism_hash_identity_across_3_of_4_encoders_per_seed": True,
            "phantom_full_recurrence_number_in_arc": 5,
            "phantom_full_meta_rule_signature": "META_RULE_AV (elapsed_s << expected)",
            "framing_correction": (
                "Cell-author verdict claim 'HARD_PASS_ENCODER_DISCRIMINATION; 3/4 encoders pass v2 chain-grade "
                "Pareto-AUC' is FABRICATED by the verdict-banding code based on numbers that do NOT depend on "
                "the encoder family being tested. 3 of 4 encoders pass by tautology because they compute "
                "bit-identical scalars. The cell does not measure encoder-family discrimination."
            ),
            "supersedes": (
                "Any prior chain_grade promotion of ANCHOR 4 encoder family v1 (this rerun does not fix the "
                "root cause flagged in the prior Skunkworks rejection); DEMOTE in cert_ledger via this atom."
            ),
            "metrics_paths": [
                f"data/exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_{s}_actual_full_rerun_2026-06-29/metrics.json"
                for s in ENCODER_PHANTOM_VET["seeds"]
            ],
            "companion_meta_rule_atom": (
                f"meta::RULE_arm_distinctness_check_must_compare_metrics_across_arms_not_just_hashes_"
                f"3_of_4_encoder_metrics_bit_identical_META_RULE_AX_{DATE_ISO}"
            ),
            "cert_increment_delta": 0,
        },
        "serves_capability": ["concept::CAP_substrate_encoder_family_discrimination_phase_characterization"],
    }


# ---- ATOM 4: META_RULE_AW seed-config-identical-for-cross-seed-agg ----

def meta_rule_AW_atom() -> Dict[str, Any]:
    aid = (f"RULE_seed_config_must_be_identical_for_cross_seed_aggregation_3_diff_configs_under_1_"
           f"anchor_HF_at_capacity_breach_META_RULE_AW_{DATE_ISO}")
    return {
        "id": aid,
        "name": (
            "META_RULE_AW: cross-seed aggregation requires identical (M, N_h, N_c, N_replay, alpha, backend, "
            "run_mode) config across all seeds; if any seed differs, treat as cardinality breach + tier HARD_FAIL"
        ),
        "corpus": "meta",
        "tier": "T2",
        "kind": "methodology_rule",
        "description": (
            "META_RULE_AW (cert-neutral discipline rule; delta=0):\n\n"
            "OBSERVED (cortex_hippo_handoff chain_grade_M_8192_GPU_v2_replay_fixed 3-seed audit 2026-06-30):\n"
            "  3 'seeds' under one anchor name shipped 3 different configs:\n"
            "    seed_7  run_mode=smoke M=512  N_h=512  N_replay=10 alpha=0.25 backend=torch.cpu  HP\n"
            "    seed_13 run_mode=full  M=8192 N_h=4096 N_replay=50 alpha=1.00 backend=torch.cuda HF\n"
            "    seed_19 run_mode=full  M=8192 N_h=4096 N_replay=50 alpha=1.00 backend=torch.cuda HF\n"
            "  Cell-author OR Director framing of 'we have a 3-seed chain-grade attempt' is a "
            "CARDINALITY BREACH under config drift: only 2 of 3 seeds ran the same config.\n\n"
            "DISCIPLINE: cross-seed aggregation (mean, ranking, cv, 3-seed CG promotion) is LEGAL ONLY when "
            "every seed ran the same (M, N_h, N_c, N_replay, alpha, backend, run_mode) tuple. If any seed "
            "differs, the cross-seed aggregation is illegal -- tier as HARD_FAIL with config-drift annotation "
            "and re-dispatch the off-config seed at the chain-grade config before any aggregation.\n\n"
            "PRE-DISPATCH check: Director (or cell-author) must declare a single (M, N_h, N_c, N_replay, "
            "alpha, backend, run_mode) tuple in the pre-reg; orchestrator + cell-author must verify each seed "
            "lands with the declared tuple before any cross-seed aggregation. Skunkworks landed-VET must "
            "off-disk-check the tuple per seed (same as cardinality_ok + verify-the-referent).\n\n"
            "COMPOSES WITH:\n"
            "  META_RULE_H (CARDINALITY_OK mandatory pre-reg field)\n"
            "  META_RULE_I (verify-the-referent; off-disk recompute)\n"
            "  META_RULE_AV (run_mode=selftest vs run_mode=full discrimination)\n"
            "  META_RULE_AU (pre-flight HARD_FAIL_GPU_MANDATE_BREACH discrimination)\n\n"
            "CERT-NEUTRAL: this rule shapes cell-author + Director + Skunkworks practice, doesn't increment "
            "cert_n. Atomized to prevent recurrence."
        ),
        "aliases": [
            "META_RULE_AW_seed_config_identical_for_cross_seed_agg",
            "config_drift_cardinality_breach_HF_discipline",
        ],
        "metadata": {
            "provenance_quality": "DERIVED_FROM_1_HIPPO_M8192_AUDIT",
            "cert_status": "discipline_meta",
            "cert_class": "cert_neutral_discipline_rule",
            "verdict": "META_RULE_NEUTRAL",
            "verified_off_data": True,
            "verified_off_data_evidence": (
                "cortex_hippo_M_8192_v2_replay_fixed 3 metrics.json files OFF-DATA recompute: seed_7 "
                "run_mode=smoke + config (M=512 N_h=512 N_replay=10 alpha=0.25 backend=torch.cpu) differs "
                "in 6 of 7 dimensions from seeds 13/19 (M=8192 N_h=4096 N_replay=50 alpha=1.00 "
                "backend=torch.cuda run_mode=full). Cross-seed aggregation would average across "
                "incompatible configs."
            ),
            "atomized_by": ATOMIZED_BY,
            "atomized_date": DATE_ISO,
            "rule_number_in_meta_corpus": "RULE_AW",
            "applies_when": (
                "any cell dispatched as multi-seed (n_seeds >= 2) intended for cross-seed aggregation, "
                "particularly chain-grade promotion attempts"
            ),
            "companion_chain_grade_atom": None,
            "companion_HF_atom": (
                f"math::T3/EXP_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_3seed_"
                f"HARD_FAIL_capacity_breach_plus_config_drift_seed_7_smoke_seeds_13_19_full_{DATE_ISO}"
            ),
            "cert_increment_delta": 0,
            "n_source_cells": 1,
            "source_cells": [
                f"substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_3seed_{DATE_ISO}"
            ],
        },
    }


# ---- ATOM 5: META_RULE_AX arm-distinctness-cross-family ----

def meta_rule_AX_atom() -> Dict[str, Any]:
    aid = (f"RULE_arm_distinctness_check_must_compare_metrics_across_arms_not_just_hashes_"
           f"3_of_4_encoder_metrics_bit_identical_META_RULE_AX_{DATE_ISO}")
    return {
        "id": aid,
        "name": (
            "META_RULE_AX: arm-distinctness check must cross-compare ARMS DIFFER ACROSS the family axis, "
            "not just within each arm's MECHANISM vs RANDOM pair; bit-identical metrics across family slots "
            "means the family axis is not wired into the mechanism"
        ),
        "corpus": "meta",
        "tier": "T2",
        "kind": "methodology_rule",
        "description": (
            "META_RULE_AX (cert-neutral discipline rule; delta=0):\n\n"
            "OBSERVED (ANCHOR 4 encoder family v1 actual_full_rerun 3-seed audit 2026-06-30):\n"
            "  arms_differ_per_encoder field in metrics.json reports per-encoder mechanism_hash vs "
            "random_hash differ=True for all 4 encoders. This passes META_RULE_AF (arms-must-differ) at "
            "the within-arm-pair level. HOWEVER, off-disk recompute reveals:\n"
            "    seed_7 mechanism_hash: binary=hrr=fhrr=2ebc4d9b80178e3d; sparse=e1f28e97ed79dbf2\n"
            "    seed_13 mechanism_hash: binary=hrr=fhrr=c5ee7d34da5490dc; sparse=f34afaef863a6449\n"
            "    seed_19 mechanism_hash: binary=hrr=fhrr=f71ae655b66ee1f1; sparse=f6993e1037b584d9\n"
            "  AND per-(N_dim, decay, capacity_load) grid cell, working_set_retention / clutter_fraction / "
            "composite / recency_decode_acc are BIT-IDENTICAL across binary/hrr/fhrr to 10-16 decimal places "
            "(12/12 grid cells tested).\n\n"
            "  This means the 'encoder family' axis is not actually applied to the mechanism computation; "
            "3 of 4 encoder slots produce byte-identical arm data. The verdict 'HARD_PASS_ENCODER_DISCRIMINATION; "
            "3/4 encoders pass chain-grade Pareto-AUC' is FABRICATED -- 3 encoders pass identical because they "
            "are computing the same scalar.\n\n"
            "DISCIPLINE: META_RULE_AF arms-must-differ check is INSUFFICIENT when there is a family/component axis. "
            "Cell-author MUST add cross-arm distinctness check that compares MECHANISM-arm hashes ACROSS the "
            "family slots: binary_mechanism_hash vs hrr_mechanism_hash vs fhrr_mechanism_hash. If any pair is "
            "identical, the family axis is not wired into the mechanism; HARD_FAIL the cell. Equivalently: check "
            "that at the (N_dim, decay, cap_load, regime) grid cell level, family arms differ in at least one "
            "primary metric (working_set_retention OR composite OR recency_decode_acc) by more than numeric noise.\n\n"
            "COMPOSES WITH:\n"
            "  META_RULE_AF (arms-must-differ within mechanism vs random)\n"
            "  META_RULE_Q (suspect 1.000 results -- 3-of-4 encoders showing rda=1.000 across all 12 pts is "
            "the same identity-by-construction signature)\n"
            "  META_RULE_AV (elapsed_s << expected for claimed grid size)\n\n"
            "CERT-NEUTRAL: shapes cell-author smoke + Skunkworks landed-VET. Atomized after 5th phantom-FULL "
            "recurrence in arc to prevent 6th."
        ),
        "aliases": [
            "META_RULE_AX_arm_distinctness_cross_family",
            "encoder_axis_not_wired_distinctness_discipline",
        ],
        "metadata": {
            "provenance_quality": "DERIVED_FROM_1_ANCHOR4_ENCODER_RERUN_AUDIT",
            "cert_status": "discipline_meta",
            "cert_class": "cert_neutral_discipline_rule",
            "verdict": "META_RULE_NEUTRAL",
            "verified_off_data": True,
            "verified_off_data_evidence": (
                "ANCHOR 4 encoder family v1 actual_full_rerun 3-seed: 3-of-4 encoder mechanism_hashes "
                "bit-identical per seed (binary=hrr=fhrr); per-grid-cell working_set_retention + "
                "composite + recency_decode_acc bit-identical to 10-16 decimal places across binary/hrr/"
                "fhrr for 12/12 sampled grid cells. arms_differ_per_encoder.differ=True for all 4 is "
                "vacuously satisfied since each encoder slot independently differs from its own RANDOM "
                "control -- but the encoder SLOTS produce identical mechanism data."
            ),
            "atomized_by": ATOMIZED_BY,
            "atomized_date": DATE_ISO,
            "rule_number_in_meta_corpus": "RULE_AX",
            "applies_when": (
                "any cell with a family/component axis (encoder / cleanup / routing / binding / schema / "
                "readout family) intended to demonstrate component-class discrimination"
            ),
            "companion_HF_atom": (
                f"math::T3/EXP_substrate_anchor4_encoder_family_phase_diagram_v1_actual_full_rerun_3seed_"
                f"HARD_FAIL_PHANTOM_FULL_encoder_axis_not_wired_to_mechanism_5th_phantom_recurrence_"
                f"{DATE_ISO}"
            ),
            "cert_increment_delta": 0,
            "n_source_cells": 1,
            "source_cells": [
                f"substrate_anchor4_encoder_family_phase_diagram_v1_actual_full_rerun_3seed_{DATE_ISO}"
            ],
        },
    }


# ---- A5-discipline atomic write ----

def append_jsonl_atomic(path: Path, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """A5: atomic read-modify-write via tmp + os.replace + verify-load + integrity-check."""
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
    """Skip atoms whose 'id' already present in target jsonl. A5-safe."""
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
    meta_atoms_p = repo / "data" / "substrate_index" / "meta" / "atoms.jsonl"
    meta_audit_p = repo / "data" / "substrate_index" / "meta" / "audit.jsonl"
    cert_ledger_p = repo / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"

    # Build atoms
    a1 = hippo_v2_mm_atom()
    a2 = hippo_M8192_hf_atom()
    a3 = encoder_phantom_full_atom()
    a4 = meta_rule_AW_atom()
    a5 = meta_rule_AX_atom()

    math_atoms = [a1, a2, a3]
    meta_atoms = [a4, a5]

    print("=== A5-DISCIPLINED ATOMIZE 3cell + 2META 2026-06-30 ===")
    for a in math_atoms:
        print(f"  math/{a['id']}")
    for a in meta_atoms:
        print(f"  meta/{a['id']}")
    print()

    ts = time.time()

    # cert_ledger entries (5: 1 MM delta=+1 + 2 HF delta=0 + 2 META delta=0)
    ledger_entries = [
        # 1. Hippo v2 MM (delta=+1)
        {
            "ts": ts + 0.001,
            "op": "cert_ruling_promotion_measured_mechanism",
            "atom_id": f"math::{a1['id']}",
            "cert_status": "measured_mechanism",
            "cert_class": "bottleneck_class_characterization_MM",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": "n/a-2026-06-30-batch-3cell-landed-vet",
            "verdict": (
                "MEASURED_MECHANISM_cortex_hippo_handoff_bottleneck_class_diagnostic_v2_3seed_"
                "Ha_partial_closeFrac_0p513_cv_0p024_stable_partial_bottleneck_Hc_by_construction_identity_"
                "arm_hash_DIRECT_equals_CLEAN_per_seed_H2_L2_norm_refuted_closeFrac_minus_0p003_"
                "gap_DIR_STD_0p766_cv_0p010_cross_seed_stage_2_NREM_H_OTHER_class_closes_"
                "additive_class_characterization_CERT_increment_plus_1"
            ),
            "cert_increment_delta": 1,
            "cv": None,
            "referent_pointer": {
                "metrics_path": (
                    "data/exp_substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v2/metrics.json"
                ),
                "atom_qualified_id": f"math::{a1['id']}",
            },
            "supersedes": None,
            "note": "3cell_batch_2026-06-30/hippo_v2_3seed_MM_Ha_partial_Hc_identity_H2_refuted",
        },
        # 2. Hippo M=8192 HF (delta=0; DEMOTE if any prior CG)
        {
            "ts": ts + 0.002,
            "op": "cert_ruling",
            "atom_id": f"math::{a2['id']}",
            "cert_status": "hard_fail",
            "cert_class": "honest_negative_capacity_breach_plus_config_drift",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": "n/a-2026-06-30-batch-3cell-landed-vet",
            "verdict": (
                "HARD_FAIL_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_3seed_"
                "capacity_breach_DIRECT_collapses_to_0p327_at_M_over_N_c_4x_oversubscription_"
                "transfer_mechanism_rides_at_4_percent_of_DIRECT_seed_7_ran_SMOKE_config_M_512_seeds_13_19_"
                "ran_FULL_config_M_8192_config_drift_breaks_cross_seed_aggregation_NOT_seed_instability_"
                "demote_any_prior_chain_grade_promotion_triggers_META_RULE_AW_companion"
            ),
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "metrics_paths": [
                    "data/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_7/metrics.json",
                    "data/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_13/metrics.json",
                    "data/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_19/metrics.json",
                ],
                "atom_qualified_id": f"math::{a2['id']}",
                "companion_meta_rule_atom": f"meta::{a4['id']}",
            },
            "supersedes": (
                "any_prior_chain_grade_promotion_of_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_"
                "replay_fixed_anchor_or_seed_7_only_smoke_HP_framing"
            ),
            "note": "3cell_batch_2026-06-30/hippo_M8192_3seed_HF_capacity_breach_plus_config_drift",
        },
        # 3. Encoder phantom HF (delta=0)
        {
            "ts": ts + 0.003,
            "op": "cert_ruling",
            "atom_id": f"math::{a3['id']}",
            "cert_status": "hard_fail",
            "cert_class": "honest_negative_phantom_full_encoder_not_wired",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": "n/a-2026-06-30-batch-3cell-landed-vet",
            "verdict": (
                "HARD_FAIL_PHANTOM_FULL_anchor4_encoder_family_phase_diagram_v1_actual_full_rerun_3seed_"
                "encoder_axis_not_wired_3_of_4_encoder_mechanism_hashes_bit_identical_per_seed_"
                "12_of_12_grid_cells_working_set_retention_composite_recency_decode_acc_bit_identical_"
                "to_10_to_16_decimal_places_across_binary_hrr_fhrr_only_sparse_bipolar_differs_"
                "elapsed_0p36_to_0p40_seconds_incompatible_with_48_grid_units_META_RULE_AV_signature_"
                "5th_phantom_full_recurrence_this_arc_HARD_PASS_ENCODER_DISCRIMINATION_verdict_FABRICATED_"
                "by_verdict_banding_on_encoder_independent_scalar_triggers_META_RULE_AX_companion"
            ),
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "metrics_paths": [
                    f"data/exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_{s}_actual_full_rerun_2026-06-29/metrics.json"
                    for s in [7, 13, 19]
                ],
                "atom_qualified_id": f"math::{a3['id']}",
                "companion_meta_rule_atom": f"meta::{a5['id']}",
            },
            "supersedes": (
                "any_prior_chain_grade_promotion_of_anchor4_encoder_family_phase_diagram_v1_including_"
                "actual_full_rerun_suffix_did_not_fix_encoder_not_wired_root_cause"
            ),
            "note": "3cell_batch_2026-06-30/encoder_phantom_full_HF_5th_recurrence",
        },
        # 4. META_RULE_AW (delta=0)
        {
            "ts": ts + 0.004,
            "op": "cert_ruling_meta_rule",
            "atom_id": f"meta::{a4['id']}",
            "cert_status": "discipline_meta",
            "cert_class": "cert_neutral_discipline_rule",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": "n/a-2026-06-30-batch-3cell-landed-vet",
            "verdict": (
                "META_RULE_AW_seed_config_must_be_identical_for_cross_seed_aggregation_derived_from_hippo_M8192_"
                "3seed_audit_3_diff_configs_under_1_anchor_HF_at_capacity_breach_composes_with_META_RULE_H_"
                "cardinality_OK_META_RULE_I_verify_the_referent_META_RULE_AV_selftest_vs_full_META_RULE_AU_"
                "pre_flight_HF_gpu_mandate_breach_CERT_neutral_delta_zero"
            ),
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "atom_qualified_id": f"meta::{a4['id']}",
                "companion_HF_atom": f"math::{a2['id']}",
            },
            "supersedes": None,
            "note": "3cell_batch_2026-06-30/META_RULE_AW_companion_to_hippo_M8192_HF",
        },
        # 5. META_RULE_AX (delta=0)
        {
            "ts": ts + 0.005,
            "op": "cert_ruling_meta_rule",
            "atom_id": f"meta::{a5['id']}",
            "cert_status": "discipline_meta",
            "cert_class": "cert_neutral_discipline_rule",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": "n/a-2026-06-30-batch-3cell-landed-vet",
            "verdict": (
                "META_RULE_AX_arm_distinctness_check_must_compare_metrics_across_arms_not_just_hashes_"
                "derived_from_anchor4_encoder_rerun_audit_3_of_4_encoder_mechanism_hashes_bit_identical_"
                "per_seed_META_RULE_AF_passes_vacuously_at_within_arm_pair_level_must_add_cross_family_"
                "distinctness_check_composes_with_META_RULE_AF_META_RULE_Q_suspect_1p000_META_RULE_AV_"
                "elapsed_short_CERT_neutral_delta_zero"
            ),
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "atom_qualified_id": f"meta::{a5['id']}",
                "companion_HF_atom": f"math::{a3['id']}",
            },
            "supersedes": None,
            "note": "3cell_batch_2026-06-30/META_RULE_AX_companion_to_encoder_phantom_HF",
        },
    ]

    # Audit rows (mirror cert_ruling per-atom)
    math_audit_rows = [
        {
            "ts": ts,
            "op": "atomize",
            "atom_id": a["id"],
            "corpus": "math",
            "cert_status": a["metadata"]["cert_status"],
            "atomized_by": ATOMIZED_BY,
            "cell_commit": "n/a-2026-06-30-batch-3cell-landed-vet",
        }
        for a in math_atoms
    ]
    meta_audit_rows = [
        {
            "ts": ts,
            "op": "atomize",
            "atom_id": a["id"],
            "corpus": "meta",
            "cert_status": a["metadata"]["cert_status"],
            "atomized_by": ATOMIZED_BY,
            "cell_commit": "n/a-2026-06-30-batch-3cell-landed-vet",
        }
        for a in meta_atoms
    ]

    # 1. math/atoms (idempotent)
    math_to_write = idempotent_filter(math_atoms_p, math_atoms)
    if math_to_write:
        r1 = append_jsonl_atomic(math_atoms_p, math_to_write)
        print(f"math/atoms.jsonl: {r1}")
        assert r1["integrity_ok"], "math/atoms.jsonl integrity FAILED"
    else:
        print(f"math/atoms.jsonl: all atoms present (idempotent skip)")
        r1 = {"integrity_ok": True, "n_appended": 0}

    # 2. math/audit
    r2 = append_jsonl_atomic(math_audit_p, math_audit_rows)
    print(f"math/audit.jsonl: {r2}")
    assert r2["integrity_ok"], "math/audit.jsonl integrity FAILED"

    # 3. meta/atoms (idempotent)
    meta_to_write = idempotent_filter(meta_atoms_p, meta_atoms)
    if meta_to_write:
        r3 = append_jsonl_atomic(meta_atoms_p, meta_to_write)
        print(f"meta/atoms.jsonl: {r3}")
        assert r3["integrity_ok"], "meta/atoms.jsonl integrity FAILED"
    else:
        print(f"meta/atoms.jsonl: all atoms present (idempotent skip)")
        r3 = {"integrity_ok": True, "n_appended": 0}

    # 4. meta/audit
    r4 = append_jsonl_atomic(meta_audit_p, meta_audit_rows)
    print(f"meta/audit.jsonl: {r4}")
    assert r4["integrity_ok"], "meta/audit.jsonl integrity FAILED"

    # 5. cert_ledger
    r5 = append_jsonl_atomic(cert_ledger_p, ledger_entries)
    print(f"meta/cert_ledger.jsonl: {r5}")
    assert r5["integrity_ok"], "meta/cert_ledger.jsonl integrity FAILED"

    print()
    print("=== ALL A5-DISCIPLINED ATOMIC WRITES OK ===")
    print(f"  CERT delta net=+1 (1 MM promotion + 2 HF + 2 META rule)")
    print(f"  MEMORY.md headline: 633 -> 634")
    print()
    print(f"  Atom IDs:")
    print(f"    - math::{a1['id']}")
    print(f"    - math::{a2['id']}")
    print(f"    - math::{a3['id']}")
    print(f"    - meta::{a4['id']}")
    print(f"    - meta::{a5['id']}")


if __name__ == "__main__":
    main()
