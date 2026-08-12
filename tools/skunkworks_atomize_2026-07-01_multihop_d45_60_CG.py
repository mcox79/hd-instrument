"""A5-gated atomization of multihop_reasoning_depth_45_to_60_gpu_v1 3-seed landing.

Landing (verified off-disk by Skunkworks independent recompute):
  Cell verdict on-disk: DEPTH_60_CROSSED_HALF (crossing_bracket=45-60)
  Cross-seed tier: CHAIN_GRADE (13th CG of 2026-07-01)

Rationale:
  - USER 0.50-crossing discriminator ANSWERED: crossing_bracket=[45, 60]
    cross-seed mean d45=0.5317 (above 0.50) + cross-seed mean d60=0.480 (below 0.50)
  - All 3 seeds UNANIMOUS above-half at d45 (0.515/0.535/0.545)
  - 2/3 seeds per-seed crossed at d60; seed 7 at 0.535 just above; cross-seed mean crossed
  - Pre-reg policy: rails "verdict pre-emption on MAJORITY-SEED breach"; rail_15 has
    1/3 breach at 0.003 magnitude (NOT majority; policy allows)
  - All PHASE_CV_MAX gates cleared (max 0.086 vs 0.10 threshold)
  - Zero LLM leak; cardinality 3/3
  - Per-step accuracy REMARKABLY STABLE 0.9824-0.9878 across d15-d60 4x range;
    load-bearing scientific finding on scale-invariant per-step decay rate.
  - Extends prior Landing 6 CG (d20-40; 10th CG of today) by two additional phase points;
    consistent tier with policy precedent using cross-seed MEAN discrimination.

Comparison with Landing 9 (theta_gamma v3 MM):
  - theta_gamma v3: pre-reg had LOCKED HP gate (nested_vs_flat32>=0.1) that seed 7 failed
    cleanly -> auditor MM was correct (bar not lowered when parent had 3/3 HP at cv=0.000)
  - d45-60 multihop: pre-reg rail policy is explicitly MAJORITY-SEED breach; rail_15
    has 1/3 breach at 0.003 magnitude which is NOT majority -> policy allows verdict.
    Different pre-reg contract -> different tier decision, both consistent with prior CGs.

Discipline invariants (per hdi_skunkworks.md):
  - Atomic tmp-write + os.replace on atoms.jsonl AND cert_ledger.jsonl
  - Matching timestamps between atom + ledger entries
  - verified_off_data=True on ledger entries
  - Load-verify after write
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
COMMIT = "657ae50a"

# ---------- Atom 10: multihop d45-60 CG ----------
ATOM_10_ID = (
    "T3/EXP_multihop_reasoning_depth_45_to_60_gpu_v1_3seed_CHAIN_GRADE_"
    "USER_0p50_crossing_discriminator_ANSWERED_crossing_bracket_45_to_60_"
    "PART_15HOP_0p7983_cv_0p046_rail15_breach_1_of_3_seed_7_at_0p755_below_lower_band_0p758_by_0p003_NOT_majority_policy_allows_"
    "PART_20HOP_0p7017_cv_0p032_rail20_breach_0_of_3_clean_"
    "PART_30HOP_0p6333_cv_0p007_rail30_breach_0_of_3_clean_"
    "PART_45HOP_0p5317_cv_0p023_ABOVE_half_line_0p50_all_3_seeds_unanimous_0p515_0p535_0p545_"
    "PART_60HOP_0p4800_cv_0p086_BELOW_half_line_cross_seed_mean_crossed_2_of_3_seeds_per_seed_crossed_seed_7_at_0p535_just_above_"
    "cross_seed_mean_discrimination_policy_consistent_with_Landing_6_10th_CG_where_seed_13_at_0p495_also_per_seed_below_but_mean_above_"
    "per_step_accuracy_REMARKABLY_STABLE_0p9851_0p9824_0p9849_0p9861_0p9878_across_d15_to_d60_4x_range_scale_invariant_decay_rate_"
    "all_PHASE_CV_MAX_gates_cleared_0p007_to_0p086_less_than_0p10_threshold_"
    "no_mechanism_death_at_any_depth_all_much_greater_than_HF_0p10_"
    "zero_LLM_forward_calls_all_seeds_substrate_native_"
    "cardinality_3_of_3_seeds_GPU_RTX_4060_Ti_1p96GB_peak_"
    "extends_prior_Landing_6_10th_CG_d20_40_by_2_novel_phase_points_d45_d60_"
    "USER_declared_informational_but_verdict_DEPTH_60_CROSSED_HALF_is_hard_decision_locked_answer_13th_CG_of_2026_07_01_2026-07-01"
)
ATOM_10 = {
    "id": ATOM_10_ID,
    "name": (
        "CG multihop_reasoning_depth_45_to_60_gpu_v1 3-seed FULL: USER's 0.50-crossing "
        "discriminator ANSWERED - crossing_bracket=[45, 60] (cross-seed mean d45=0.5317 above; "
        "cross-seed mean d60=0.480 below). Per-depth cross-seed: PART_15HOP=0.798 cv=0.046 "
        "(seeds [0.755, 0.845, 0.795]; rail_15 breach 1/3 at 0.003 magnitude - NOT majority; "
        "pre-reg policy 'verdict pre-emption on MAJORITY-SEED breach' allows this); PART_20HOP=0.702 "
        "cv=0.032 rail_20 breach 0/3; PART_30HOP=0.633 cv=0.007 rail_30 breach 0/3 clean; "
        "PART_45HOP=0.5317 cv=0.023 ALL 3 seeds UNANIMOUS above 0.50 half-line (0.515/0.535/0.545); "
        "PART_60HOP=0.480 cv=0.086 cross-seed mean BELOW 0.50 (2/3 per-seed crossed; seed 7 at 0.535 "
        "just above; cross-seed mean discrimination policy consistent with Landing 6 10th CG where "
        "seed 13 at 0.495 was per-seed below half but mean was above). Per-step accuracy "
        "REMARKABLY STABLE across 4x depth range: 0.9851/0.9824/0.9849/0.9861/0.9878 at d15/20/30/45/60 "
        "(scale-invariant decay rate - the SUBSTANTIVE scientific finding). ALL cv gates cleared "
        "(max 0.086 vs 0.10 PHASE_CV_MAX); no mechanism death at any depth (all >> HF=0.10; d60 min=0.435); "
        "zero LLM forward calls (substrate-native); cardinality 3/3; GPU RTX 4060 Ti 1.96GB peak; "
        "total wall 146.8s. Extends prior Landing 6 (10th CG of today; d20-40) by adding depth 45 "
        "and depth 60 as novel phase points. USER declared informational but verdict DEPTH_60_CROSSED_HALF "
        "is a HARD-DECISION-LOCKED answer per pre-reg tier logic. CERT +1."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        f"OFF-DATA verified: data/exp_multihop_reasoning_depth_45_to_60_gpu_v1/metrics.json.\n\n"
        f"Recompute Skunkworks {DATE}:\n"
        f"  depth=15: tops=[0.755, 0.845, 0.795] mean=0.7983 sd=0.0368 cv=0.0461\n"
        f"    rail_15 [0.758, 0.858] target=0.808: seed_7 0.755 breach (0.003 below lower band)\n"
        f"    seed_13 0.845 OK, seed_19 0.795 OK. breach_count=1/3; NOT majority.\n"
        f"    Pre-reg line 62 policy: 'Sanity rails (verdict pre-emption on MAJORITY-SEED breach)'.\n"
        f"    1/3 breach is NOT majority; policy explicitly allows this. Statistical fluctuation\n"
        f"    at n_queries=200 has stddev sqrt(0.808*0.192/200)=0.028; seed_7 is 1.9 sigma below\n"
        f"    target - within normal seed variance.\n"
        f"  depth=20: tops=[0.715, 0.72, 0.67] mean=0.7017 sd=0.0225 cv=0.0320\n"
        f"    rail_20 [0.658, 0.758] target=0.708: 3/3 seeds OK; breach_count=0/3\n"
        f"  depth=30: tops=[0.64, 0.63, 0.63] mean=0.6333 sd=0.0047 cv=0.0074\n"
        f"    rail_30 [0.587, 0.687] target=0.637: 3/3 seeds OK; breach_count=0/3\n"
        f"  depth=45: tops=[0.515, 0.535, 0.545] mean=0.5317 sd=0.0125 cv=0.0235\n"
        f"    ALL 3 seeds UNANIMOUS above 0.50 half-line; cross-seed mean above 0.50.\n"
        f"    HP_45HOP_STILL_ABOVE_HALF=0.50 gate CLEARED unanimously.\n"
        f"  depth=60: tops=[0.535, 0.435, 0.47] mean=0.4800 sd=0.0414 cv=0.0863\n"
        f"    Cross-seed mean BELOW 0.50 half-line (0.480 <= 0.50).\n"
        f"    Per-seed: seed_7 at 0.535 just above; seed_13 at 0.435 below; seed_19 at 0.47 below.\n"
        f"    2/3 per-seed crossed; 1/3 per-seed above; cross-seed mean discrimination policy.\n"
        f"    HP_60HOP_CROSSED=0.50 gate CLEARED on cross-seed mean.\n"
        f"\n"
        f"CROSS-SEED CONSISTENCY WITH LANDING 6 (10th CG of today; d20-40):\n"
        f"  Landing 6 also had per-seed non-unanimity at the depth-40 half-line: seed_13 at 0.495\n"
        f"  was per-seed BELOW half but cross-seed mean 0.533 was ABOVE half. Skunkworks tiered\n"
        f"  Landing 6 CG using cross-seed MEAN discrimination policy. Same policy applied here\n"
        f"  gives consistent CG tier for Landing 10.\n"
        f"\n"
        f"USER DISCRIMINATOR ANSWERED (LOAD-BEARING SCIENTIFIC CLAIM):\n"
        f"  USER 2026-07-01: 'find the actual 0.50 crossing depth'\n"
        f"  Answer: 0.50 crossing depth d* lies in bracket (45, 60] under this substrate config\n"
        f"  (N=8192, V_C=200, V_P=10, K_set=20, n_partitions=20, n_chains=200).\n"
        f"  d45 cross-seed mean 0.5317 (above); d60 cross-seed mean 0.480 (below).\n"
        f"  Bracket half-width 15 hops; d* localized within 25% relative uncertainty.\n"
        f"  Finer bracket (e.g., d=50, 55) would tighten but pre-reg gates hit at d=45/60.\n"
        f"\n"
        f"LOAD-BEARING SCIENTIFIC FINDING (per-step accuracy stability):\n"
        f"  Per-step accuracy = top1^(1/depth):\n"
        f"    d=15: 0.9851; d=20: 0.9824; d=30: 0.9849; d=45: 0.9861; d=60: 0.9878\n"
        f"  Per-step accuracy is REMARKABLY STABLE across a 4x depth range (d=15 to d=60).\n"
        f"  This is a SCALE-INVARIANT DECAY RATE finding: partition-oracle per-hop cleanup\n"
        f"  primitive has empirical per-step accuracy ~0.985 regardless of chain depth.\n"
        f"  Interpretation: substrate does NOT degrade per-hop as depth grows (no compounding\n"
        f"  error accumulation beyond simple product 0.985^d); the mechanism is genuinely\n"
        f"  depth-invariant modulo the 0.985 per-hop floor.\n"
        f"  d=60 per-step (0.9878) is SLIGHTLY HIGHER than d=15 per-step (0.9851); this is\n"
        f"  binomial noise at n_queries=200 (stddev ~0.028 on top1) not a real trend.\n"
        f"\n"
        f"HP GATE ANALYSIS (all pre-reg conditions):\n"
        f"  cardinality_ok:             3/3 seeds OK (expected_n_units=3)\n"
        f"  RAIL_15 majority breach:    NO (1/3 breach; policy requires >=2)\n"
        f"  RAIL_20 majority breach:    NO (0/3 breach)\n"
        f"  RAIL_30 majority breach:    NO (0/3 breach)\n"
        f"  HP_45HOP >= 0.50 (mean):    YES (0.5317 >= 0.50); ALL 3 seeds unanimous above\n"
        f"  HP_60HOP <= 0.50 (mean):    YES (0.480 <= 0.50); 2/3 seeds per-seed crossed\n"
        f"  HF mechanism death:         NO (d60 min=0.435 >> 0.10 HF threshold)\n"
        f"  PHASE_CV_MAX <= 0.10:       YES all depths (max 0.086 at d=60)\n"
        f"  n_llm_calls = 0:            YES (3/3 seeds)\n"
        f"  Verdict emitted: DEPTH_60_CROSSED_HALF (5-way tier hit correctly by pre-reg logic)\n"
        f"\n"
        f"BROKEN-PC-BEFORE-STRUCTURAL-FRAMING (July 1 auditor discipline):\n"
        f"  What serves as positive control here? Three rail depths (d15, d20, d30) reproduce\n"
        f"  prior CG MEASURED targets. Rails are the positive control.\n"
        f"  Rail_15 breach on seed_7 at 0.003 magnitude: 0.755 vs [0.758, 0.858] band with target 0.808.\n"
        f"  Statistical significance: at n_queries=200 top1 has binomial stddev 0.028 at p=0.808.\n"
        f"  seed_7 is 1.9 sigma below target - normal seed variance, NOT rail failure.\n"
        f"  Cross-seed mean rail_15=0.798 is 0.010 below target 0.808 (0.4 sigma) - within noise.\n"
        f"  Positive control HOLDS on cross-seed mean; per-seed variance is expected at n=200.\n"
        f"\n"
        f"COMPARISON WITH LANDING 9 (theta_gamma v3 MM; auditor MM tier):\n"
        f"  Landing 9: pre-reg had LOCKED HP gate (nested_vs_flat32 >= 0.1) that seed 7 failed\n"
        f"    cleanly. Prior v2 parent CG had cliff cv=0.000 (perfect reproducibility). Auditor\n"
        f"    tier MM: 'bar not lowered when parent had 3/3 HP at cv=0.000'.\n"
        f"  Landing 10 (this): pre-reg rail policy is explicitly MAJORITY-SEED breach; rail_15\n"
        f"    breach is 1/3 at 0.003 magnitude - NOT majority - policy allows verdict. Verdict\n"
        f"    correctly emits DEPTH_60_CROSSED_HALF. Prior Landing 6 parent CG had per-seed\n"
        f"    non-unanimity at half-line too and was tiered CG on cross-seed mean.\n"
        f"  Different pre-reg contracts -> different tier decisions; both consistent with prior CGs.\n"
        f"  Auditor discipline: respect the pre-reg's LOCKED policy AS the policy.\n"
        f"\n"
        f"CROSS-ARC OVERLAP CHECK {DATE}: substrate_query 'multihop reasoning depth 45 60 half\n"
        f"  line crossing partition oracle' top-1 cosine=0.295 (below 0.30 novelty threshold;\n"
        f"  consistent with cell-author's own 0.282 finding). Prior chain-grade rails at\n"
        f"  d15/20/30 are DIRECT parents. Depths 45 and 60 are GENUINELY NEW phase points.\n"
        f"\n"
        f"COMPOSES WITH:\n"
        f"  - Landing 6 (10th CG of today): multihop d20-40 CG at same substrate config.\n"
        f"    This landing (Landing 10) extends envelope by 2 novel phase points (d45, d60).\n"
        f"  - Prior CG rails d15/20/30 reproduce prior chain-grade MEASURED targets within noise.\n"
        f"  - Not superseded; Landing 6 remains valid at d20-40 setpoint.\n"
        f"  - Together: full envelope d15/20/30/40/45/60 characterization of partition-oracle\n"
        f"    multi-hop primitive with scale-invariant per-step accuracy ~0.985.\n"
        f"\n"
        f"REVIVAL CRITERION for finer d* bracketing:\n"
        f"  Add d=50, d=55 phase points to tighten crossing bracket from [45, 60] to [50, 55]\n"
        f"  or better. Predicted at 0.985 per-step: d=50 -> 0.469; d=55 -> 0.435. Both below\n"
        f"  half. Actual crossing d* is likely around d=48-50 given cross-seed mean 0.5317 at\n"
        f"  d=45 and 0.480 at d=60. A d=48 phase point at 0.985 per-step predicts 0.484.\n"
        f"\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_multihop_d45_60."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "run_mode": "full",
        "n_seeds": 3,
        "seeds": [7, 13, 19],
        "depths": [15, 20, 30, 45, 60],
        "N": 8192,
        "V_C": 200,
        "V_P": 10,
        "K_set": 20,
        "n_partitions": 20,
        "part_size": 10,
        "n_chains": 200,
        "encoder_provenance": "SUBSTRATE_NATIVE",
        "cardinality_ok": True,
        "n_units_expected": 3,
        "n_units_observed": 3,
        "top1_per_depth_cross_seed_mean": {15: 0.7983, 20: 0.7017, 30: 0.6333, 45: 0.5317, 60: 0.4800},
        "top1_per_depth_cross_seed_cv": {15: 0.0461, 20: 0.0320, 30: 0.0074, 45: 0.0235, 60: 0.0863},
        "top1_per_depth_per_seed": {
            15: [0.755, 0.845, 0.795],
            20: [0.715, 0.72, 0.67],
            30: [0.64, 0.63, 0.63],
            45: [0.515, 0.535, 0.545],
            60: [0.535, 0.435, 0.47],
        },
        "per_step_accuracy_per_depth": {15: 0.9851, 20: 0.9824, 30: 0.9849, 45: 0.9861, 60: 0.9878},
        "per_step_scale_invariant_across_4x_depth_range": True,
        "rails_targets": {15: 0.808, 20: 0.708, 30: 0.637},
        "rails_bands": {15: [0.758, 0.858], 20: [0.658, 0.758], 30: [0.587, 0.687]},
        "rail_breach_count_per_depth": {15: 1, 20: 0, 30: 0},
        "rail_policy_majority_seed_breach": True,
        "rail_15_seed_7_breach_magnitude": 0.003,
        "rail_15_seed_7_sigma_below_target": 1.9,
        "rail_15_cross_seed_mean_delta_from_target_sigma": 0.4,
        "USER_discriminator_answered": True,
        "USER_discriminator_crossing_bracket": [45, 60],
        "HP_45HOP_above_half_threshold": 0.50,
        "HP_45HOP_above_half_per_seed": [True, True, True],
        "HP_45HOP_cross_seed_mean_above_half": True,
        "HP_60HOP_crossed_threshold": 0.50,
        "HP_60HOP_crossed_per_seed": [False, True, True],
        "HP_60HOP_cross_seed_mean_crossed": True,
        "HF_mechanism_death_threshold": 0.10,
        "HF_any_depth_death": False,
        "d60_min_across_seeds": 0.435,
        "PHASE_CV_MAX_threshold": 0.10,
        "PHASE_CV_MAX_all_depths_ok": True,
        "PHASE_CV_MAX_worst": 0.0863,
        "PHASE_CV_MAX_worst_at_depth": 60,
        "no_position_positive_control_via_rail_reproduction": True,
        "rail_reproduction_holds_on_cross_seed_mean": True,
        "gpu_peak_memory_mb": 1961.85,
        "elapsed_s_per_seed": {"7": 49.1, "13": 51.4, "19": 46.2},
        "total_elapsed_s": 146.8,
        "n_llm_forward_calls_per_seed": {"7": 0, "13": 0, "19": 0},
        "verified_off_data": True,
        "metrics_path": "data/exp_multihop_reasoning_depth_45_to_60_gpu_v1/metrics.json",
        "prereg_path": "preregs/2026-07-01_multihop_reasoning_depth_45_to_60_gpu_v1.md",
        "parent_atoms": [
            "T3/EXP_multihop_reasoning_depth_20_to_40_gpu_v1_3seed_CHAIN_GRADE_envelope_extends_to_depth_40",
            "T3/EXP_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1_CHAIN_GRADE_DEPTH_CEILING_30",
        ],
        "cert_tier": "chain_grade",
        "cert_increment_delta": 1,
        "revival_criterion": (
            "add_d_50_and_d_55_phase_points_to_tighten_crossing_bracket_from_45_60_to_50_55_or_better_"
            "predicted_at_0p985_per_step_d_50_yields_0p469_d_55_yields_0p435_actual_crossing_likely_d_48_50_"
            "given_cross_seed_mean_0p5317_at_d_45_and_0p480_at_d_60"
        ),
    },
}
LEDGER_10 = {
    "ts": TS_NOW,
    "op": "cert_ruling_promotion_chain_grade",
    "atom_id": f"math::{ATOM_10_ID}",
    "cert_status": "chain_grade",
    "cert_class": "pre_reg_pass_multihop_depth_envelope_extension_to_depth_60_partition_oracle_USER_crossing_discriminator_answered",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_multihop_d45_60",
    "cell_commit": COMMIT,
    "verdict": (
        "CHAIN_GRADE_3seed_HP_USER_0p50_crossing_discriminator_ANSWERED_crossing_bracket_45_60_"
        "d45_cross_seed_mean_0p5317_ALL_3_seeds_unanimous_above_half_line_0p50_"
        "d60_cross_seed_mean_0p480_below_half_line_2_of_3_per_seed_crossed_seed_7_at_0p535_just_above_"
        "cross_seed_mean_discrimination_policy_consistent_with_Landing_6_10th_CG_"
        "rail_15_breach_1_of_3_at_0p003_magnitude_NOT_majority_pre_reg_policy_allows_"
        "rail_20_and_rail_30_clean_0_of_3_breach_"
        "all_PHASE_CV_MAX_gates_cleared_worst_0p086_at_d60_below_0p10_threshold_"
        "no_mechanism_death_at_any_depth_d60_min_0p435_well_above_HF_0p10_"
        "per_step_accuracy_REMARKABLY_STABLE_0p9824_to_0p9878_across_d15_to_d60_4x_range_scale_invariant_"
        "zero_LLM_forward_calls_substrate_native_cardinality_3_of_3_seeds_"
        "GPU_RTX_4060_Ti_1p96GB_peak_wall_146p8s_"
        "extends_Landing_6_10th_CG_d20_40_by_2_novel_phase_points_d45_d60_"
        "13th_CG_of_2026_07_01"
    ),
    "cert_increment_delta": 1,
    "cv": 0.0863,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_multihop_reasoning_depth_45_to_60_gpu_v1/metrics.json",
        "prereg_path": "preregs/2026-07-01_multihop_reasoning_depth_45_to_60_gpu_v1.md",
        "parent_CG_atom_landing_6": "T3/EXP_multihop_reasoning_depth_20_to_40_gpu_v1_3seed_CHAIN_GRADE_envelope_extends_to_depth_40",
        "atom_qualified_id": f"math::{ATOM_10_ID}",
    },
    "supersedes": None,
    "note": (
        "multihop_reasoning_depth_45_to_60_gpu_v1_3seed_CHAIN_GRADE_13th_CG_of_2026_07_01_"
        "USER_0p50_crossing_discriminator_ANSWERED_crossing_bracket_45_60_"
        "d45_cross_seed_mean_0p5317_all_3_seeds_unanimous_above_half_line_"
        "d60_cross_seed_mean_0p480_below_half_line_2_of_3_per_seed_crossed_"
        "rail_15_breach_1_of_3_at_0p003_magnitude_1p9_sigma_below_target_within_normal_binomial_seed_variance_at_n_queries_200_"
        "pre_reg_policy_majority_seed_breach_1_of_3_is_not_majority_policy_allows_verdict_"
        "cross_seed_mean_rail_15_at_0p798_is_only_0p4_sigma_below_target_0p808_within_noise_"
        "per_step_accuracy_scale_invariant_load_bearing_scientific_finding_"
        "extends_Landing_6_10th_CG_d20_40_by_novel_d45_d60_phase_points_"
        "consistent_tier_precedent_cross_seed_mean_discrimination_policy_"
        "revival_criterion_add_d_50_and_d_55_to_tighten_crossing_bracket_actual_d_star_likely_48_to_50_"
        "hdlab_primitives_can_ship_partition_oracle_multihop_up_to_d_45_above_half_and_d_60_crossing_at_this_substrate_config"
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
    math_before, math_after = atomic_append_jsonl(MATH_ATOMS, [ATOM_10])
    print(f"math/atoms.jsonl: {math_before} -> {math_after} (+{math_after - math_before})")

    ledger_records = [LEDGER_10]
    led_before, led_after = atomic_append_jsonl(CERT_LEDGER, ledger_records)
    print(f"meta/cert_ledger.jsonl: {led_before} -> {led_after} (+{led_after - led_before})")

    print()
    print(f"CERT delta: +1 (Atom 10 multihop d45-60 CG; USER 0.50-crossing discriminator answered)")
    print(f"Session-cumulative today: CG=+7, MM=+2, HF=+1, meta_amendment=+1")
    print(f"  Wave 1 CG: Atom 1 (M-sweep v3), Atom 2 (population coding), Atom 5 (task_vector K500)")
    print(f"  Wave 2 CG: Atom 6 (multihop d20-40), Atom 7 (refuse-gate V_REL)")
    print(f"  Wave 3 CG: Atom 8 (N-sweep amended-scope)")
    print(f"  Wave 4 MM: Atom 9 (theta_gamma v3 N=16384 cross-seed unanimity broken)")
    print(f"  Wave 5 CG: Atom 10 (multihop d45-60 crossing bracket answered)")
    print(f"Timestamp: {TS_NOW}")
    print(f"Commit: {COMMIT}")


if __name__ == "__main__":
    main()
