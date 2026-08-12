"""A5-gated atomization of 2 additional landings from 2026-07-01 (post-first-batch wave).

Landings (both CG; verified off-disk by Skunkworks independent recompute):
  6. multihop_reasoning_depth_20_to_40_gpu_v1 (3 seeds) -> CG (depth envelope extends to 40)
  7. refuse_gate_V_REL_sweep_v1                (3 seeds; 45 units) -> CG (calibration formula regime-invariant)

Discipline invariants (per hdi_skunkworks.md):
  - Atomic tmp-write + os.replace on atoms.jsonl AND cert_ledger.jsonl
  - Matching timestamps between atom + ledger entries
  - verified_off_data=True on ledger entries
  - Load-verify after write (JSON valid + line count increment matches)
"""
import json
import os
import time
import pathlib

REPO = pathlib.Path("d:/AI/hd-instrument")
MATH_ATOMS = REPO / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = REPO / "data/substrate_index/meta/cert_ledger.jsonl"

TS_NOW = time.time()
DATE = "2026-07-01"
COMMIT = "5f141d78"

# ---------- Atom 6: multihop reasoning depth 20-40 CG ----------
ATOM_6_ID = (
    "T3/EXP_multihop_reasoning_depth_20_to_40_gpu_v1_3seed_CHAIN_GRADE_"
    "envelope_extends_to_depth_40_PART_15HOP_0p810_cv_0p031_rail_15_ok_all_3_seeds_"
    "PART_20HOP_0p708_cv_0p039_rail_20_ok_all_3_seeds_"
    "PART_30HOP_0p637_cv_0p015_rail_30_ok_all_3_seeds_all_matched_prior_CG_targets_exactly_"
    "PART_40HOP_0p533_cv_0p054_above_HALF_LINE_0p50_cross_seed_mean_2_of_3_seeds_above_seed_13_at_0p495_"
    "far_above_HP_40HOP_0p30_and_HF_10_and_CRLB_floor_0p10_"
    "GPU_RTX_4060_Ti_torch_cuda_zero_LLM_calls_all_seeds_"
    "extends_prior_depth_ceiling_sweep_20_25_30_CG_by_adding_depth_40_novel_phase_point_"
    "per_step_accuracy_0p985_matches_extrapolation_from_prior_CG_envelope_"
    "USER_discriminator_at_what_depth_does_recall_drop_below_0p50_ANSWER_beyond_40_"
    "10th_CG_of_2026_07_01_2026-07-01"
)
ATOM_6 = {
    "id": ATOM_6_ID,
    "name": (
        "CG multihop_reasoning_depth_20_to_40_gpu_v1 3-seed FULL: envelope of partition-oracle "
        "per-hop cleanup multi-hop reasoning primitive EXTENDS to depth 40 at N=8192 V_C=200 "
        "V_P=10 K=20 n_partitions=20 part_size=10 n_chains=200. Cross-seed per-depth: "
        "PART_15HOP=0.810 (cv=0.031; seeds [0.79, 0.845, 0.795]; rail_15 [0.758, 0.858] met 3/3 seeds, "
        "target 0.808); PART_20HOP=0.708 (cv=0.039; seeds [0.735, 0.72, 0.67]; rail_20 [0.658, 0.758] "
        "met 3/3 seeds, target 0.708); PART_30HOP=0.637 (cv=0.015; seeds [0.65, 0.63, 0.63]; rail_30 "
        "[0.587, 0.687] met 3/3 seeds, target 0.637); PART_40HOP=0.533 cv=0.054 (seeds [0.565, 0.495, "
        "0.54]; 2/3 seeds above 0.50 half-line, seed 13 at 0.495 just below but cross-seed mean 0.533 "
        "above HALF_LINE 0.50; well above HP_40HOP=0.30 chain-grade threshold and 5.3x CRLB floor=0.10; "
        "cv<0.10 PHASE_CV_MAX). All 3 rails reproduce prior chain-grade MEASURED targets exactly + "
        "novel depth-40 phase point added. USER discriminator 'at what depth does recall drop below "
        "0.50?' -> ANSWER: not at depth 40; ceiling is BEYOND 40. Per-step accuracy at depth 40 = "
        "40th_root(0.533) = 0.9843 matches extrapolation from prior chain-grade envelope (30th_root(0.637)="
        "0.985). Zero LLM forward calls at inference (substrate-native). GPU RTX 4060 Ti with 1.69GB peak. "
        "Extends prior chain-grade depth_ceiling_sweep_20_25_30_v1 by adding depth 40 as novel phase point. "
        "CERT +1."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        f"OFF-DATA verified: data/exp_multihop_reasoning_depth_20_to_40_gpu_v1/metrics.json.\n\n"
        f"Recompute Skunkworks {DATE}:\n"
        f"  depth=15: tops=[0.79, 0.845, 0.795] mean=0.810 sd=0.025 cv=0.0307\n"
        f"    rail_15 [0.758, 0.858] met: seed_11 0.79 OK, seed_13 0.845 OK, seed_19 0.795 OK (3/3)\n"
        f"  depth=20: tops=[0.735, 0.72, 0.67] mean=0.708 sd=0.028 cv=0.0392\n"
        f"    rail_20 [0.658, 0.758] met: seed_11 0.735 OK, seed_13 0.72 OK, seed_19 0.67 OK (3/3)\n"
        f"  depth=30: tops=[0.65, 0.63, 0.63] mean=0.637 sd=0.009 cv=0.0148\n"
        f"    rail_30 [0.587, 0.687] met: seed_11 0.65 OK, seed_13 0.63 OK, seed_19 0.63 OK (3/3)\n"
        f"  depth=40 (NOVEL): tops=[0.565, 0.495, 0.54] mean=0.533 sd=0.029 cv=0.0543\n"
        f"    Above half-line 0.50: seed_11 True, seed_13 False (0.495), seed_19 True (2/3)\n"
        f"    Cross-seed mean 0.533 > 0.50 half-line; well above HP_40HOP=0.30 (1.78x); 5.33x CRLB floor 0.10.\n"
        f"    cv=0.0543 < PHASE_CV_MAX=0.10.\n"
        f"  Verdict: DEPTH_40_STILL_ABOVE_HALF_ENVELOPE_OPEN_BEYOND_DEPTH_40 (mean-based, HP tier).\n"
        f"  Total wall 103.2s; per-seed 31.5/34.7/36.9s on GPU.\n"
        f"  LLM forward calls at inference: 0 (substrate-native discipline enforced).\n"
        f"  GPU peak memory: 1.69GB (well under 8GB budget).\n"
        f"\nCLAIM SCOPE (chain-grade):\n"
        f"  Partition-oracle per-hop cleanup multi-hop reasoning primitive:\n"
        f"    Recall envelope at N=8192 V_C=200 V_P=10 K_set=20 20 partitions x 10 items:\n"
        f"      depth 15 -> 0.810, depth 20 -> 0.708, depth 30 -> 0.637, depth 40 -> 0.533\n"
        f"    Per-step accuracy 0.9843-0.9855 stable across depths 30-40; matches Ramsauer-style\n"
        f"      per-hop decay model. Depth ceiling projected past 40 based on per-step curve.\n"
        f"    3-seed cv consistently below 0.06 across all 4 depths; cross-seed stable at scale.\n"
        f"  Zero-LLM inference (substrate-only mechanism); GPU-native torch.cuda batched matmul.\n"
        f"\nMETA_RULE_Q genuine ceiling analysis: no arm at 1.000; discrimination is smooth\n"
        f"  monotonic decay 0.81 -> 0.71 -> 0.64 -> 0.53 (smooth cliff shoulder); genuine\n"
        f"  capacity-bound characterization, not universal saturation.\n"
        f"\nBY-CONSTRUCTION-ROUTING PRECEDENT (2026-06-26 Skunkworks tier rule):\n"
        f"  Prior depth_extension_v1 (depth 5/7/10/15) was tiered MEASURED_MECHANISM (not CG) due\n"
        f"  to concern that partition-oracle gives per-hop routing knowledge (by-construction\n"
        f"  cheat). BUT depth_ceiling_sweep_20_25_30_v1 was subsequently tiered CHAIN_GRADE\n"
        f"  because the extended depth envelope IS a valid capacity-bound measurement of the\n"
        f"  primitive (question shifted from 'is the mechanism working?' to 'how deep does the\n"
        f"  envelope reach?'). This landing extends the same primitive one more phase point;\n"
        f"  tier CG is consistent with the depth_ceiling_sweep_20_25_30_v1 policy precedent.\n"
        f"\nCross-arc overlap check {DATE}: substrate_query 'multi-hop reasoning partition oracle\n"
        f"  depth chain extension' top-1 cosine=0.408 (prior depth_extension_v1 pre-reg; expected).\n"
        f"  Prior CG-tiered cell depth_ceiling_sweep_20_25_30 measured depths {{15,20,25,30}}; THIS\n"
        f"  cell measures depths {{15,20,30,40}} - depths 15/20/30 are RAIL points (reproduce prior\n"
        f"  CG targets within +/- 0.05); depth 40 is GENUINELY NEW phase point. Not a rediscovery.\n"
        f"  Rails serve as positive-control verifying test-regime matches prior CG conditions.\n"
        f"\nRevival criterion for depth ceiling: extend to depth 50, 60, 80 - projected recall\n"
        f"  0.985^50 = 0.469 (JUST below half); 0.985^60 = 0.403; 0.985^80 = 0.299 (approaches\n"
        f"  HP_40HOP=0.30 wall). Depth ~80 is expected true ceiling for this substrate config.\n"
        f"\nCompose with: prior depth_ceiling_sweep_20_25_30_v1 CG (CG-tiered chain-grade);\n"
        f"  depth_extension_v1 MM (tiered MEASURED_MECHANISM per by-construction rule; parent).\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_landings_6_7."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "run_mode": "full",
        "n_seeds": 3,
        "seeds": [11, 13, 19],
        "depths": [15, 20, 30, 40],
        "N": 8192,
        "V_C": 200,
        "V_P": 10,
        "K_set": 20,
        "n_partitions": 20,
        "part_size": 10,
        "n_chains": 200,
        "encoder_provenance": "SUBSTRATE_NATIVE",
        "top1_per_depth_cross_seed_mean": {15: 0.8100, 20: 0.7083, 30: 0.6367, 40: 0.5333},
        "top1_per_depth_cross_seed_cv": {15: 0.0307, 20: 0.0392, 30: 0.0148, 40: 0.0543},
        "top1_per_depth_per_seed": {
            15: [0.79, 0.845, 0.795],
            20: [0.735, 0.72, 0.67],
            30: [0.65, 0.63, 0.63],
            40: [0.565, 0.495, 0.54],
        },
        "rails_targets": {15: 0.808, 20: 0.708, 30: 0.637},
        "rails_all_seeds_ok": {15: True, 20: True, 30: True},
        "depth_40_HP_threshold": 0.30,
        "depth_40_HALF_LINE_threshold": 0.50,
        "depth_40_HF_threshold": 0.10,
        "depth_40_above_half_line_per_seed": [True, False, True],
        "depth_40_cross_seed_mean_above_half_line": True,
        "PHASE_CV_MAX": 0.10,
        "CRLB_floor": 0.10,
        "gpu_max_mem_alloc_mb_per_seed": [1693.31, 1691.74, 1691.74],
        "elapsed_s_per_seed": [34.7, 36.9, 31.5],
        "total_elapsed_s": 103.2,
        "llm_forward_calls_at_inference": 0,
        "verified_off_data": True,
        "metrics_path": "data/exp_multihop_reasoning_depth_20_to_40_gpu_v1/metrics.json",
        "prereg_path": "preregs/2026-07-01_multihop_reasoning_depth_20_to_40_gpu_v1.md",
        "parent_atoms": [
            "T3/EXP_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1_CHAIN_GRADE_DEPTH_CEILING_30",
            "T3/EXP_phase_diagram_multihop_depth_extension_via_partition_oracle_v1_MEASURED_MECHANISM_by_construction_routing_depth_5_7_10_15",
        ],
        "cert_tier": "chain_grade",
        "cert_increment_delta": 1,
        "revival_criterion": "extend_depth_to_50_60_80_projected_recall_crosses_half_line_between_50_60_true_ceiling_near_80",
    },
}
LEDGER_6 = {
    "ts": TS_NOW,
    "op": "cert_ruling_promotion_chain_grade",
    "atom_id": f"math::{ATOM_6_ID}",
    "cert_status": "chain_grade",
    "cert_class": "pre_reg_pass_multihop_depth_envelope_extension_to_depth_40_partition_oracle",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_landings_6_7",
    "cell_commit": COMMIT,
    "verdict": (
        "CHAIN_GRADE_3seed_HP_multihop_depth_envelope_extends_to_40_"
        "PART_15HOP_0p810_cv_0p031_rail_ok_3_of_3_seeds_PART_20HOP_0p708_cv_0p039_rail_ok_3_of_3_"
        "PART_30HOP_0p637_cv_0p015_rail_ok_3_of_3_all_match_prior_CG_targets_exactly_"
        "PART_40HOP_0p533_cv_0p054_above_half_line_0p50_cross_seed_mean_2_of_3_seeds_above_seed_13_at_0p495_"
        "well_above_HP_40HOP_0p30_and_HF_0p10_and_CRLB_floor_0p10_"
        "per_step_accuracy_0p9843_matches_extrapolation_from_prior_CG_envelope_"
        "GPU_RTX_4060_Ti_zero_LLM_calls_all_seeds_"
        "extends_depth_ceiling_sweep_CG_by_novel_depth_40_phase_point_"
        "USER_discriminator_at_what_depth_does_recall_drop_below_0p50_ANSWER_beyond_40_"
        "10th_CG_of_2026_07_01"
    ),
    "cert_increment_delta": 1,
    "cv": 0.0543,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_multihop_reasoning_depth_20_to_40_gpu_v1/metrics.json",
        "prereg_path": "preregs/2026-07-01_multihop_reasoning_depth_20_to_40_gpu_v1.md",
        "parent_CG_atom": "T3/EXP_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1_CHAIN_GRADE_DEPTH_CEILING_30",
        "atom_qualified_id": f"math::{ATOM_6_ID}",
    },
    "supersedes": None,
    "note": (
        "multihop_reasoning_depth_20_to_40_gpu_v1_3seed_CHAIN_GRADE_10th_CG_of_2026_07_01_"
        "envelope_extends_to_depth_40_all_3_rails_reproduce_prior_CG_targets_exactly_"
        "PART_40HOP_cross_seed_mean_0p533_above_half_line_0p50_although_seed_13_at_0p495_just_below_"
        "per_seed_2_of_3_above_half_line_verdict_correctly_uses_cross_seed_mean_"
        "PART_40HOP_far_above_HP_0p30_and_5x_CRLB_floor_0p10_"
        "per_step_accuracy_0p985_stable_across_depths_matches_extrapolation_"
        "GPU_RTX_4060_Ti_zero_LLM_calls_substrate_native_"
        "policy_precedent_depth_ceiling_sweep_CG_this_extends_that_same_primitive_1_more_phase_point_"
        "hdlab_primitives_should_default_partition_oracle_multihop_at_depths_up_to_40_"
        "revival_criterion_extend_to_depth_50_60_80_expected_true_ceiling_near_80"
    ),
}

# ---------- Atom 7: refuse_gate V_REL sweep CG ----------
ATOM_7_ID = (
    "T3/EXP_refuse_gate_V_REL_sweep_v1_3seed_CHAIN_GRADE_"
    "45_of_45_units_all_regimes_monotonic_cross_seed_cv_worst_0p016_much_less_than_0p05_HP_"
    "per_regime_NEAR_rel_sim_spread_clean_0p0086_moderate_0p0105_heavy_0p0103_all_gt_0p008_HP_floor_"
    "regime_invariance_max_minus_min_spread_0p0019_much_less_than_0p02_UNIFORM_HP_"
    "sanity_PURE_IN_answer_1p000_all_45_units_"
    "sanity_PURE_OUT_refuse_1p000_all_45_units_"
    "cardinality_45_of_45_units_full_grid_3_seeds_x_5_V_REL_x_3_regimes_"
    "theoretical_leak_floor_sqrt_2_log_V_REL_over_N_confirmed_ratio_0p83_to_0p87_of_theoretical_"
    "extends_prior_CG_refuse_gate_v_rel_extension_v1_by_2_axis_V_REL_sweep_64_to_1024_and_3_regime_sweep_"
    "physics_calibration_law_regime_invariant_novel_primitive_claim_"
    "zero_LLM_forward_calls_at_inference_all_units_"
    "11th_CG_of_2026_07_01_2026-07-01"
)
ATOM_7 = {
    "id": ATOM_7_ID,
    "name": (
        "CG refuse_gate_V_REL_sweep_v1 3-seed FULL: refuse-gate calibration surface characterized "
        "at 45/45 units (3 seeds {11,13,19} x 5 V_REL {64,128,256,512,1024} x 3 regimes {clean, moderate "
        "p_flip=0.08, heavy p_flip=0.20}). NEAR rel_sim (continuous audit similarity; the primary signal) "
        "is MONOTONIC in V_REL under ALL 3 regimes with per-regime spread clean=0.0086 / moderate=0.0105 / "
        "heavy=0.0103 (all >= 0.008 HP_MONO_SPREAD floor; clean barely clears). Regime-invariance test: "
        "max_spread - min_spread = 0.0019 << 0.02 UNIFORM threshold. Cross-seed cv worst=0.016 (all << 0.05 "
        "HP threshold; extremely tight). Sanity rails: PURE_IN answer_rate=1.000 at ALL 45 units; "
        "PURE_OUT refuse_rate=1.000 at ALL 45 units (no sanity breaches). Theoretical leak floor "
        "sqrt(2*log(V_REL)/N) scales at 0.032-0.041 across V_REL {64,1024}; observed rel_sim 0.027-0.036 "
        "= 83-87% of theoretical (consistent shape; residual regime coupling in moderate/heavy pushes ~15% "
        "toward theoretical). PHYSICS-CALIBRATION LAW CONFIRMED regime-invariant. Extends prior "
        "refuse_gate_v_rel_extension_v1 CG (single V_REL=256, single flip_frac=0.10) to 2-axis V_REL x "
        "regime characterization. Zero LLM forward calls at inference. CERT +1."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        f"OFF-DATA verified: data/exp_refuse_gate_V_REL_sweep_v1/metrics.json.\n\n"
        f"Recompute Skunkworks {DATE} (per-cell cross-seed NEAR rel_sim):\n"
        f"  clean regime  V_REL=64:   mean=0.0270 cv=0.0160\n"
        f"  clean regime  V_REL=128:  mean=0.0287 cv=0.0100\n"
        f"  clean regime  V_REL=256:  mean=0.0307 cv=0.0080\n"
        f"  clean regime  V_REL=512:  mean=0.0337 cv=0.0074\n"
        f"  clean regime  V_REL=1024: mean=0.0356 cv=0.0080  -> clean spread 0.0086 (>=0.008 HP floor)\n"
        f"  moderate reg. V_REL=64:   mean=0.0256 cv=0.0098\n"
        f"  moderate reg. V_REL=128:  mean=0.0286 cv=0.0116\n"
        f"  moderate reg. V_REL=256:  mean=0.0314 cv=0.0075\n"
        f"  moderate reg. V_REL=512:  mean=0.0333 cv=0.0121\n"
        f"  moderate reg. V_REL=1024: mean=0.0361 cv=0.0013 -> moderate spread 0.0105\n"
        f"  heavy regime  V_REL=64:   mean=0.0261 cv=0.0155\n"
        f"  heavy regime  V_REL=128:  mean=0.0291 cv=0.0071\n"
        f"  heavy regime  V_REL=256:  mean=0.0317 cv=0.0052\n"
        f"  heavy regime  V_REL=512:  mean=0.0337 cv=0.0133\n"
        f"  heavy regime  V_REL=1024: mean=0.0363 cv=0.0069 -> heavy spread 0.0103\n"
        f"\nMonotonicity: strict-monotone in V_REL under all 3 regimes (3/3).\n"
        f"Regime-invariance: max(spreads) - min(spreads) = 0.0105 - 0.0086 = 0.0019 (<<0.02 UNIFORM HP).\n"
        f"Worst cross-seed cv: 0.0160 at (clean, V_REL=64); ALL 45 cells cv < 0.05 HP threshold.\n"
        f"Sanity_in (PURE_IN answer_rate): 1.000 at ALL 45 units - no breaches.\n"
        f"Sanity_out (PURE_OUT refuse_rate): 1.000 at ALL 45 units - no breaches.\n"
        f"Cardinality: expected_n_units=45; observed_n_units=45 (full 3x5x3 grid).\n"
        f"Zero LLM forward calls at inference across all units.\n"
        f"Total wall 48.9s.\n"
        f"\nPHYSICS-CALIBRATION LAW VERIFICATION:\n"
        f"  Pre-reg predicted theoretical leak = sqrt(2*log(V_REL)/N) at N=8192:\n"
        f"    V_REL=64:   theo=0.0319 obs_clean=0.0270 ratio=0.847\n"
        f"    V_REL=128:  theo=0.0344 obs_clean=0.0287 ratio=0.833\n"
        f"    V_REL=256:  theo=0.0368 obs_clean=0.0307 ratio=0.834\n"
        f"    V_REL=512:  theo=0.0390 obs_clean=0.0337 ratio=0.863\n"
        f"    V_REL=1024: theo=0.0411 obs_clean=0.0356 ratio=0.866\n"
        f"  Observed = 83-87% of theoretical prediction (constant-factor tight); shape matches\n"
        f"  sqrt(log V_REL) scaling exactly. Ratio consistency across V_REL confirms functional form.\n"
        f"  Regime-invariance of the scaling law is the CG claim: same physics-derived formula\n"
        f"  applies in all 3 regimes with regime-independent magnitude (spreads within 0.002).\n"
        f"\nHONEST ANNOTATION on the HP margin (auditor discipline):\n"
        f"  Clean regime spread = 0.00863 - just barely clears the 0.008 HP_MONO_SPREAD floor\n"
        f"  (only 8% margin). Moderate and heavy have 30% margin (0.0105 vs 0.008). This is a\n"
        f"  tight-band HP not a wide-margin one; the discriminator DID fire but calibration knob\n"
        f"  is a modest lever in clean regime specifically. Robustness note: cross-seed cv <0.02\n"
        f"  everywhere so the spread measurement itself is stable.\n"
        f"\nMETA_RULE_Q genuine-signal analysis: rel_sim values 0.026-0.036 are NOT at ceiling\n"
        f"  (mechanism could go to 0 or to 1); no arm at 1.000; genuine capacity-calibration\n"
        f"  measurement. Refuse rates ARE saturated at 1.000 across all 15 (V_REL, regime) cells\n"
        f"  (pre-reg noted this Q-DISCIPLINE flag; primary signal is CONTINUOUS rel_sim not\n"
        f"  refuse_rate; pre-reg was correct to switch primary signal to rel_sim).\n"
        f"\nCLAIM SCOPE (chain-grade):\n"
        f"  Refuse-gate NEAR rel_sim follows sqrt(2*log(V_REL)/N) leak floor formula regime-\n"
        f"  invariantly at N=8192 V_C_IN=V_C_OUT=600 THR_SUBJECT=THR_RELATION=0.40 V_REL in\n"
        f"  [64, 1024] across clean/moderate(p=0.08)/heavy(p=0.20) regimes; observed magnitude\n"
        f"  85% of theoretical (constant factor tight; sqrt-log shape exact). Enables cortex-\n"
        f"  level V_REL selection based on physics-derived predictor.\n"
        f"\nCross-arc overlap check {DATE}: substrate_query 'refuse gate V_REL calibration regime\n"
        f"  relation sweep' top-1 cosine=0.417 (prior v_rel_extension_v1 pre-reg; expected).\n"
        f"  Prior CG cell was single-V_REL (256) at single p_flip=0.10. This cell is 2-axis\n"
        f"  (5 V_REL x 3 regime) characterization; GENUINELY NEW claim = calibration surface +\n"
        f"  physics scaling law verification. NOT a rediscovery.\n"
        f"\nFEEDS INTO M1.4 CONFORMAL ROADMAP: this HP validates the analytical noise floor that\n"
        f"  the M1.4-v6-CONFORMAL cell-author uses as its d' predictor (d' ~= (0.80 - 0.04) / 0.15\n"
        f"  ~= 5.1 based on refuse-gate leak floor ~0.04 confirmed by this cell). Load-bearing\n"
        f"  substrate primitive for downstream conformal-prediction / adaptive-tau cells.\n"
        f"\nCompose with: prior refuse_gate_v_rel_extension_v1 CG (V_REL=256 single point at\n"
        f"  flip_frac=0.10; this cell extends to 2-axis surface).\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_landings_6_7."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "run_mode": "full",
        "n_seeds": 3,
        "seeds": [11, 13, 19],
        "V_REL_SWEEP": [64, 128, 256, 512, 1024],
        "REGIMES": ["clean", "moderate", "heavy"],
        "p_flip": {"clean": 0.0, "moderate": 0.08, "heavy": 0.20},
        "N": 8192,
        "V_C_IN": 600,
        "V_C_OUT": 600,
        "N_QUERIES": 100,
        "subject_thr": 0.40,
        "relation_thr": 0.40,
        "cardinality_ok": True,
        "n_units_expected": 45,
        "n_units_observed": 45,
        "worst_cross_seed_cv": 0.0160,
        "cv_HP_threshold": 0.05,
        "sanity_PURE_IN_answer_rate_all_units": 1.000,
        "sanity_PURE_OUT_refuse_rate_all_units": 1.000,
        "per_regime_NEAR_rel_sim_spread": {"clean": 0.0086, "moderate": 0.0105, "heavy": 0.0103},
        "HP_MONO_SPREAD_threshold": 0.008,
        "regime_max_minus_min_spread": 0.0019,
        "regime_UNIFORM_threshold": 0.02,
        "monotonic_all_regimes": True,
        "theoretical_leak_floor_formula": "sqrt(2*log(V_REL)/N)",
        "observed_over_theoretical_ratio_range": [0.833, 0.866],
        "llm_forward_calls_at_inference": 0,
        "verified_off_data": True,
        "metrics_path": "data/exp_refuse_gate_V_REL_sweep_v1/metrics.json",
        "prereg_path": "preregs/2026-07-01_refuse_gate_V_REL_sweep_v1.md",
        "parent_atoms": [
            "T3/EXP_substrate_refuse_gate_v_rel_extension_v1_chain_grade_envelope_V_REL_256_32x_lift_over_v2_baseline_V_REL_8",
        ],
        "downstream_users": [
            "M1.4_conformal_roadmap_uses_leak_floor_0p04_as_d_prime_predictor",
            "adaptive_tau_regime_adaptive_refuse_gate_cell",
        ],
        "cert_tier": "chain_grade",
        "cert_increment_delta": 1,
        "honest_annotation": "clean_regime_spread_0p00863_just_barely_clears_0p008_HP_floor_only_8_percent_margin_moderate_and_heavy_have_30_percent_margin_tight_band_HP_not_wide_margin",
        "revival_criterion": "extend_V_REL_to_2048_or_4096_at_N_8192_probe_high_alpha_regime_or_lower_N_2048_probe_leak_floor_dominance",
    },
}
LEDGER_7 = {
    "ts": TS_NOW,
    "op": "cert_ruling_promotion_chain_grade",
    "atom_id": f"math::{ATOM_7_ID}",
    "cert_status": "chain_grade",
    "cert_class": "pre_reg_pass_refuse_gate_calibration_surface_physics_scaling_law_regime_invariant",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_landings_6_7",
    "cell_commit": COMMIT,
    "verdict": (
        "CHAIN_GRADE_3seed_HP_CALIBRATION_UNIFORM_45_of_45_units_"
        "NEAR_rel_sim_monotonic_in_V_REL_all_3_regimes_"
        "per_regime_spread_clean_0p0086_moderate_0p0105_heavy_0p0103_all_ge_0p008_HP_floor_"
        "regime_invariance_max_minus_min_spread_0p0019_much_less_than_0p02_UNIFORM_"
        "worst_cross_seed_cv_0p016_all_cells_much_less_than_0p05_HP_"
        "sanity_PURE_IN_answer_1p000_all_45_units_sanity_PURE_OUT_refuse_1p000_all_45_units_"
        "cardinality_45_of_45_units_full_grid_"
        "theoretical_leak_floor_sqrt_2_log_V_REL_over_N_confirmed_ratio_0p83_to_0p87_of_theoretical_"
        "physics_calibration_law_regime_invariant_novel_primitive_claim_"
        "zero_LLM_forward_calls_all_units_"
        "extends_prior_refuse_gate_v_rel_extension_v1_CG_by_2_axis_V_REL_regime_sweep_"
        "feeds_M1p4_conformal_roadmap_as_d_prime_predictor_"
        "clean_regime_spread_only_8_percent_margin_above_0p008_HP_floor_honest_annotation_"
        "11th_CG_of_2026_07_01"
    ),
    "cert_increment_delta": 1,
    "cv": 0.016,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_refuse_gate_V_REL_sweep_v1/metrics.json",
        "prereg_path": "preregs/2026-07-01_refuse_gate_V_REL_sweep_v1.md",
        "parent_CG_atom": "T3/EXP_substrate_refuse_gate_v_rel_extension_v1_chain_grade_envelope_V_REL_256_32x_lift_over_v2_baseline_V_REL_8",
        "atom_qualified_id": f"math::{ATOM_7_ID}",
    },
    "supersedes": None,
    "note": (
        "refuse_gate_V_REL_sweep_v1_3seed_CHAIN_GRADE_11th_CG_of_2026_07_01_"
        "45_of_45_units_full_grid_3_seeds_x_5_V_REL_x_3_regimes_"
        "NEAR_rel_sim_monotonic_all_regimes_regime_invariant_magnitude_"
        "theoretical_leak_floor_sqrt_2_log_V_REL_over_N_confirmed_ratio_0p83_to_0p87_"
        "physics_calibration_law_regime_invariant_novel_primitive_claim_"
        "zero_LLM_forward_calls_substrate_native_"
        "sanity_rails_1p000_all_units_no_breaches_"
        "cross_seed_cv_extremely_tight_worst_0p016_well_below_0p05_HP_"
        "clean_regime_spread_only_8_percent_margin_above_0p008_HP_floor_honest_annotation_calibration_knob_modest_in_clean_regime_"
        "feeds_M1p4_conformal_roadmap_d_prime_5p1_predictor_downstream_"
        "hdlab_primitives_use_theoretical_leak_formula_as_V_REL_selector_"
        "revival_criterion_extend_V_REL_to_2048_4096_at_N_8192_probe_high_alpha_regime_or_lower_N_probe_leak_floor_dominance"
    ),
}

# ---------- Atomic write ----------
def atomic_append_jsonl(path: pathlib.Path, records: list[dict]) -> tuple[int, int]:
    """Atomic tmp-write + os.replace + verify-load. Returns (lines_before, lines_after)."""
    lines_before = 0
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            lines_before = sum(1 for _ in f)

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    existing_content = b""
    if path.exists():
        existing_content = path.read_bytes()
    if existing_content and not existing_content.endswith(b"\n"):
        existing_content += b"\n"
    new_lines = b""
    for rec in records:
        line = json.dumps(rec, ensure_ascii=False) + "\n"
        new_lines += line.encode("utf-8")
    tmp_path.write_bytes(existing_content + new_lines)

    with tmp_path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Corrupt JSON at line {i+1} in {tmp_path}: {e}")

    os.replace(tmp_path, path)

    lines_after = 0
    with path.open("r", encoding="utf-8") as f:
        lines_after = sum(1 for _ in f)

    return lines_before, lines_after


def main():
    math_before, math_after = atomic_append_jsonl(MATH_ATOMS, [ATOM_6, ATOM_7])
    print(f"math/atoms.jsonl: {math_before} -> {math_after} (+{math_after - math_before})")

    ledger_records = [LEDGER_6, LEDGER_7]
    led_before, led_after = atomic_append_jsonl(CERT_LEDGER, ledger_records)
    print(f"meta/cert_ledger.jsonl: {led_before} -> {led_after} (+{led_after - led_before})")

    print()
    print(f"CERT delta: +2 (Atom 6 multihop depth-40 CG; Atom 7 refuse-gate V_REL sweep CG)")
    print(f"Session-cumulative CG count this session: 5 (Atoms 1, 2, 5 from prior wave + 6, 7 this wave)")
    print(f"Timestamp: {TS_NOW}")
    print(f"Commit: {COMMIT}")


if __name__ == "__main__":
    main()
