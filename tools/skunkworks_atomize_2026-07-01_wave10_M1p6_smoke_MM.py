"""A5-gated atomization of M1.6 cortex_attention_binding_router smoke single-seed HP.

Landing 22 status per verify_landing.py + off-disk check:
  - FULL 3-seed files (data/exp_cortex_attention_binding_router_v1_seed_{7,13,19}/) DO NOT EXIST
  - Smoke variants exist for seeds 7 and 13 with verdict HARD_PASS run_mode=smoke
  - Director framings referenced FULL data but sync tick has not yet landed FULL files

Standing discipline (post-Wave 7 lesson):
  - Use verify_landing.py output as authoritative
  - Do NOT propagate Director framings about files not yet on disk
  - Same pattern applied to Wave 6 Atom 13 (v8 smoke MM) -> Wave 7 Atom 15 (v8 3-seed FULL CG lift with supersession)

Tier decision:
  MEASURED_MECHANISM (single-seed smoke evidence; awaits 3-seed FULL for CG lift + M1.6 closure).
  When FULL 3-seed lands, this atom will be superseded by a proper CG atom.

Composes 5 CG parents:
  - Atom 15 (M1.4 v8 CONFORMAL_MODERATE refuse-gate CG)
  - Atom 18 (M1.5 v2 TWOTIER context retention CG)
  - WM_multibank_codebook_cleanup (prior CG)
  - Atom 6 (multihop d20-40 partition-oracle CG)
  - Atom 1 (cortex_hippo_dense M-sweep v3 READ-REPLACE CG)

Discipline invariants:
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
COMMIT = "3ade828d"

# =====================================================================
# Atom 23: M1.6 cortex_attention_binding_router smoke seed 7 MM
# =====================================================================
ATOM_23_ID = (
    "T3/EXP_cortex_attention_binding_router_v1_seed_7_smoke_HP_MEASURED_MECHANISM_"
    "single_seed_smoke_HP_at_N_8192_V_CB_1024_N_CLASSES_4_"
    "verify_landing_py_FAIL_on_FULL_3_seed_paths_files_not_yet_synced_"
    "smoke_seed_7_verdict_HARD_PASS_elapsed_0p167s_smoke_seed_13_also_HP_elapsed_0p272s_"
    "CM_confusion_matrix_top1_0p9165_cross_regime_dialogue_1p000_ood_novel_bind_0p833_"
    "NR_null_router_baseline_0p2500_exactly_at_chance_1_over_N_CLASSES_positive_control_passes_"
    "ISO_M14_M15_composition_baseline_0p7085_cross_regime_dialogue_0p667_ood_novel_bind_0p750_"
    "lift_null_CM_minus_NR_0p667_ge_0p3_HP_threshold_"
    "lift_iso_CM_minus_ISO_0p209_ge_0p15_HP_threshold_"
    "min_class_precision_MULTI_HOP_cross_regime_avg_0p800_dialogue_1p000_ood_0p600_ge_0p7_HP_threshold_"
    "HP_ROUTE_ACCURACY_0p85_HP_LIFT_NULL_0p3_HP_PER_CLASS_PREC_0p7_HP_LIFT_ISO_0p15_ALL_gates_cleared_"
    "cardinality_14_of_14_units_arms_differ_verified_zero_LLM_calls_"
    "META_RULE_Q_saturation_at_dialogue_pronoun_regime_expected_in_distribution_saturation_ood_novel_bind_at_0p833_confirms_genuine_discrimination_"
    "M1p6_milestone_NOT_closed_on_smoke_single_seed_awaits_3_seed_FULL_"
    "composes_5_CG_parent_atoms_M1p4_v8_Atom_15_M1p5_v2_Atom_18_WM_multibank_multihop_Atom_6_dense_hopfield_Atom_1_"
    "second_cortex_integration_cell_in_M3_stack_per_cell_author_annotation_"
    "test_design_concern_n_3_per_class_per_regime_binomial_stddev_0p289_at_smoke_full_at_60_items_tightens_to_0p112_"
    "OOD_novel_bind_MULTI_HOP_class_precision_0p60_in_that_specific_regime_3_of_5_statistical_wobble_will_tighten_at_full_"
    "auditor_MM_tier_captures_smoke_HP_mechanism_validated_at_single_seed_awaits_cross_seed_and_full_N_statistical_power_"
    "expansion_criterion_to_CG_land_3_seed_FULL_all_HP_gates_cleared_cross_seed_cv_le_0p10_M1p6_milestone_closure_"
    "sync_lag_pattern_same_as_Wave_7_Atom_13_v8_smoke_MM_lifted_to_Atom_15_CG_when_FULL_landed_"
    "20th_atom_of_today_MM_not_CG_2026-07-01"
)
ATOM_23 = {
    "id": ATOM_23_ID,
    "name": (
        "MEASURED_MECHANISM M1.6 cortex_attention_binding_router smoke single-seed HP: verify_landing.py "
        "FAIL on FULL 3-seed paths (files not yet synced from remote). Smoke seed 7 verdict HARD_PASS "
        "(smoke seed 13 also HP). Cell tests 4-class cortex router (REFUSE/RETRIEVE/BIND/MULTI_HOP) "
        "composing 5 CG parents. Smoke seed 7: CM=0.917 (confusion matrix accuracy; cross-regime "
        "dialogue_pronoun 1.000 / ood_novel_bind 0.833); NR=0.250 (null router baseline exactly at "
        "chance 1/N_CLASSES; positive control passes); ISO=0.708 (M14_M15 composition baseline; "
        "cross-regime dialogue 0.667 / ood 0.750); lift_null=0.667 >= 0.3 HP; lift_iso=0.209 >= 0.15 "
        "HP; min_class_prec MULTI_HOP cross-regime avg 0.800 >= 0.7 HP (dialogue 1.000 / ood 0.600). "
        "ALL 4 HP gates cleared. Cardinality 14/14 units; arms_differ_verified; zero LLM calls. "
        "META_RULE_Q: saturation at dialogue_pronoun regime is EXPECTED in-distribution behavior "
        "(router should saturate on in-distribution class); ood_novel_bind at 0.833 confirms genuine "
        "discrimination (not universal saturation). AUDITOR MM tier NOT CG because: (a) FULL 3-seed "
        "files DO NOT EXIST on disk per verify_landing.py; (b) smoke is single-seed evidence; (c) "
        "n=3 test items per class per regime gives binomial stddev 0.289 at smoke - low statistical "
        "power. M1.6 MILESTONE NOT CLOSED on smoke alone. Cell composes 5 CG parents (M1.4 v8 Atom "
        "15 + M1.5 v2 Atom 18 + WM_multibank + multihop Atom 6 + dense-Hopfield Atom 1). GENUINELY "
        "NOVEL composition (cross-arc cosine=0.34 below 0.40 threshold). Same sync-lag pattern as "
        "Wave 6/7 Atom 13 (v8 smoke MM) which was lifted to Atom 15 (v8 3-seed FULL CG) when files "
        "synced. Expansion criterion to CG: 3-seed FULL with all HP gates cleared, cross-seed cv <= "
        "0.10, cardinality 24/24 units per seed at full. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_awaits_full_data",
    "description": (
        f"OFF-DATA verification (verify_landing.py):\n"
        f"  FAIL cortex_attention_binding_router_v1_seed_7   metrics_path_missing\n"
        f"  FAIL cortex_attention_binding_router_v1_seed_13  metrics_path_missing\n"
        f"  FAIL cortex_attention_binding_router_v1_seed_19  metrics_path_missing\n"
        f"\n"
        f"Available on disk:\n"
        f"  OK smoke seed 7  verdict=HARD_PASS run_mode=smoke elapsed=0.167s\n"
        f"  OK smoke seed 13 verdict=HARD_PASS run_mode=smoke elapsed=0.272s\n"
        f"\n"
        f"AUDITOR DOWNWARD FRAMING CORRECTION:\n"
        f"  Director spawn framed 'M1.6 CLOSURE CANDIDATE 3-seed FULL HP' with specific paths and\n"
        f"  numbers (CM=0.933, NR=0.250, ISO=0.667, lift_null=+0.683, lift_iso=+0.267, min_class_prec\n"
        f"  RETRIEVE=0.849 at 21 rows). Those numbers reflect FULL 3-seed data that has NOT synced yet.\n"
        f"  \n"
        f"  Auditor tiers based on WHAT'S ACTUALLY ON DISK per post-Wave-7 discipline:\n"
        f"    - Only smoke variants exist (14 rows each; 2 regimes; n=3 per class per regime)\n"
        f"    - Cell is inherently 200x faster than pessimistic prereg estimate per cell-author note;\n"
        f"      wall 0.16s smoke -> ~0.15s full possible per Director frame\n"
        f"    - But smoke != full: smoke has 14 units (7 arms x 2 regimes); full has 21 units\n"
        f"      (7 arms x 3 regimes) or higher n_test_per_class\n"
        f"\n"
        f"Recompute Skunkworks {DATE} (smoke seed 7 arm-by-arm):\n"
        f"  Configuration: N=8192, V_CB=1024, N_CLASSES=4, regimes=2\n"
        f"    (dialogue_pronoun in-distribution; ood_novel_bind out-of-distribution)\n"
        f"  N_train_per_class=6, N_test_per_class=3 (SMOKE)\n"
        f"\n"
        f"  PER-ARM SUMMARY (smoke seed 7; 14 rows = 7 arms x 2 regimes):\n"
        f"    Regime = dialogue_pronoun:\n"
        f"      ARM_TRUE_REFUSE:            top1=1.000 (per-class check REFUSE only)\n"
        f"      ARM_TRUE_RETRIEVE:          top1=1.000 (per-class check RETRIEVE only)\n"
        f"      ARM_TRUE_BIND:              top1=1.000 (per-class check BIND only)\n"
        f"      ARM_TRUE_MULTI_HOP:         top1=1.000 (per-class check MULTI_HOP only)\n"
        f"      ARM_ROUTE_CONFUSION_MATRIX: top1=1.000 all 4 classes precision 1.000\n"
        f"      ARM_NO_ROUTER:              top1=0.250 (chance floor; positive control)\n"
        f"      ARM_M14_M15_ISOLATED:       top1=0.667 (composition baseline; M14-only variant)\n"
        f"    Regime = ood_novel_bind:\n"
        f"      ARM_TRUE_REFUSE:            top1=1.000\n"
        f"      ARM_TRUE_RETRIEVE:          top1=0.333 (interesting; RETRIEVE class weaker ood)\n"
        f"      ARM_TRUE_BIND:              top1=1.000\n"
        f"      ARM_TRUE_MULTI_HOP:         top1=1.000\n"
        f"      ARM_ROUTE_CONFUSION_MATRIX: top1=0.833 (REFUSE=1.0, RETRIEVE=1.0, BIND=1.0, MULTI_HOP=0.6)\n"
        f"      ARM_NO_ROUTER:              top1=0.250 (chance floor; positive control)\n"
        f"      ARM_M14_M15_ISOLATED:       top1=0.750 (composition baseline; M14-only variant)\n"
        f"\n"
        f"CROSS-REGIME COMPUTATION (matches cell-emitted metrics):\n"
        f"  CM (confusion matrix accuracy cross-regime avg):\n"
        f"    (1.000 + 0.833) / 2 = 0.9165 (rounds to 0.917 as reported)\n"
        f"  NR (null router baseline):\n"
        f"    (0.250 + 0.250) / 2 = 0.2500 (exactly at chance)\n"
        f"  ISO (M14_M15 composition baseline):\n"
        f"    (0.667 + 0.750) / 2 = 0.7085 (rounds to 0.708 as reported)\n"
        f"  lift_null = CM - NR = 0.9165 - 0.2500 = 0.6665 (rounds to 0.667)\n"
        f"  lift_iso  = CM - ISO = 0.9165 - 0.7085 = 0.2080 (rounds to 0.208)\n"
        f"  min_class_prec MULTI_HOP cross-regime = (1.000 + 0.600) / 2 = 0.800\n"
        f"\n"
        f"HP GATES (all pre-reg conditions):\n"
        f"  HP_route_accuracy (CM >= 0.85):        0.917 PASS\n"
        f"  HP_lift_over_null (lift_null >= 0.3):   0.667 PASS (2.2x threshold)\n"
        f"  HP_per_class_precision (min >= 0.7):   0.800 PASS (cross-regime avg)\n"
        f"  HP_lift_over_isolated (lift_iso >= 0.15): 0.208 PASS\n"
        f"  cardinality_ok: 14/14 PASS\n"
        f"  arms_differ_verified: True PASS (all 14 pred_digest_sha256 checked; distinct per arm/regime)\n"
        f"  n_llm_calls == 0: 0 PASS\n"
        f"  Verdict: HARD_PASS at smoke (cell-emitted; auditor confirms)\n"
        f"\n"
        f"BROKEN-PC-BEFORE-STRUCTURAL-FRAMING (July 1 auditor discipline):\n"
        f"  Positive control ARM_NO_ROUTER at chance 0.250 both regimes (deviation 0.000).\n"
        f"  Baseline mechanism NOT broken; structural framing of router mechanism is legitimate.\n"
        f"  Gate passes cleanly.\n"
        f"\n"
        f"META_RULE_Q SATURATION CHECK (regime-not-too-easy discipline):\n"
        f"  ARM_ROUTE_CONFUSION_MATRIX at dialogue_pronoun saturates at 1.000.\n"
        f"    IS this universal saturation (META_RULE_Q violation)?\n"
        f"    Analysis: dialogue_pronoun is the IN-DISTRIBUTION regime; router SHOULD saturate here.\n"
        f"    ood_novel_bind regime same arm shows 0.833 (below saturation); confirms genuine\n"
        f"    discrimination between in-distribution and out-of-distribution.\n"
        f"    NOT a META_RULE_Q violation; expected in-distribution vs OOD behavior split.\n"
        f"  \n"
        f"  ARM_NO_ROUTER at 0.250 exactly at chance; positive control cleanly discriminates.\n"
        f"  ARM_M14_M15_ISOLATED at 0.667-0.750; below CM by ~0.15-0.25; composition lift is real.\n"
        f"\n"
        f"WHY AUDITOR MM NOT CG (or M1.6 CLOSURE):\n"
        f"  (a) FULL 3-seed files DO NOT EXIST per verify_landing.py output; sync-lag from remote\n"
        f"  (b) Only smoke variants exist (single-seed; n=3 per class per regime; low power)\n"
        f"  (c) M1.6 closure requires 3-seed FULL cross-seed reproducibility (standard discipline)\n"
        f"  (d) All prior 2 milestone closures today (M1.4 Atom 15, M1.5 Atom 18) required 3-seed\n"
        f"      FULL with bit-identical or near-identical cross-seed cv <= 0.10\n"
        f"  (e) Bar not lowered on M1.6 despite smoke HP\n"
        f"\n"
        f"WHY AUDITOR DID NOT DOWNGRADE PAST MM:\n"
        f"  (a) Smoke seed 7 legitimately clears all 4 HP gates (auditor recomputed all fields)\n"
        f"  (b) Smoke seed 13 ALSO HP per file inspection (independent second data point)\n"
        f"  (c) 5-CG-parent composition is legitimate substantive claim if lifts to CG when FULL lands\n"
        f"  (d) Cell-author annotations acknowledge test-design limitations honestly (n=3 stat wobble)\n"
        f"  (e) MM tier captures: mechanism validated at single-seed smoke; awaits cross-seed + full-N power\n"
        f"\n"
        f"OOD NOVEL BIND MULTI_HOP CLASS PRECISION 0.60 (test-design concern):\n"
        f"  At ood_novel_bind regime specifically, MULTI_HOP class precision = 0.60 (3 tp, 2 fp).\n"
        f"  Binomial stddev at n=5 (predicted MULTI_HOP): sqrt(0.6*0.4/5) = 0.219 (1sigma).\n"
        f"  0.60 is 0.45 sigma below 0.70 HP threshold - statistical wobble, not clean failure.\n"
        f"  \n"
        f"  Cross-regime average smooths this to 0.800 which passes HP; cell verdict uses avg.\n"
        f"  This is legitimate discipline but hides regime-specific weakness. Auditor annotates.\n"
        f"  \n"
        f"  At full (60 items per class per regime), Bernoulli sigma tightens to 0.089 for MULTI_HOP.\n"
        f"  If ood_novel_bind MULTI_HOP is genuinely at 0.6, at full it will be measured at 0.60 +/-\n"
        f"  0.09 - if 0.60 is real it would fail HP_per_class_precision >= 0.7 by 1.1 sigma.\n"
        f"  \n"
        f"  Cell-author annotation acknowledges this: 'ood_novel_bind regime seed_7 lift only 0.083\n"
        f"  in that specific regime; cross-regime mean 0.208 clears clean'. Auditor concurs.\n"
        f"\n"
        f"SYNC-LAG PATTERN (same as Wave 6/7 Atom 13/15):\n"
        f"  Wave 6: Atom 13 tiered v8 seed 7 smoke MM because Director framed 3-seed FULL but only\n"
        f"    selftest_ok artifacts + smoke existed on disk.\n"
        f"  Wave 7: Atom 15 tiered v8 3-seed FULL CG when sync tick landed FULL files.\n"
        f"    Atom 15 SUPERSEDED Atom 13 via supersession chain.\n"
        f"  \n"
        f"  Landing 22 is at same sync-lag stage. When FULL 3-seed lands + verify_landing.py OK,\n"
        f"    file a proper CG atom that SUPERSEDES this Atom 23.\n"
        f"\n"
        f"EXPANSION CRITERION TO CG + M1.6 CLOSURE:\n"
        f"  Land 3-seed FULL run with:\n"
        f"    (a) verify_landing.py OK all 3 seeds run_mode=full verdict=HARD_PASS\n"
        f"    (b) all 3 seeds CM >= 0.85 (probably tightens vs smoke's 0.917 due to lower variance)\n"
        f"    (c) all 3 seeds lift_null >= 0.3 (mechanism lift over null router baseline)\n"
        f"    (d) all 3 seeds min_class_prec >= 0.7 cross-regime (particularly OOD MULTI_HOP)\n"
        f"    (e) all 3 seeds lift_iso >= 0.15 (composition lift over M14_M15 isolated baseline)\n"
        f"    (f) cross-seed cv on best_conformal-analog CM <= 0.10\n"
        f"    (g) cardinality 24/24 units per seed (assuming full has 3 regimes)\n"
        f"    (h) META_RULE_Q not violated (dialogue_pronoun saturation OK; other regimes not saturated)\n"
        f"  If all met: M1.6 CLOSED; 3 cortex milestones today (M1.4 + M1.5 + M1.6).\n"
        f"\n"
        f"COMPOSITION (5 CG parents):\n"
        f"  - Atom 15 (M1.4 v8 CONFORMAL_MODERATE refuse-gate CG): REFUSE class mechanism\n"
        f"  - Atom 18 (M1.5 v2 TWOTIER context retention CG): RETRIEVE class mechanism\n"
        f"  - WM_multibank_codebook_cleanup (prior CG): shared codebook cleanup primitive\n"
        f"  - Atom 6 (multihop d20-40 partition-oracle CG): MULTI_HOP class mechanism\n"
        f"  - Atom 1 (cortex_hippo_dense M-sweep v3 READ-REPLACE CG): BIND class mechanism\n"
        f"  \n"
        f"  Cell is GENUINELY NOVEL COMPOSITION of 5 CG primitives via LeHDC class-HV routing;\n"
        f"  cross-arc cosine=0.34 below 0.40 threshold.\n"
        f"\n"
        f"CROSS-ARC OVERLAP CHECK {DATE}: substrate_query 'cortex attention binding router 4 class\n"
        f"  refuse retrieve bind multihop class HV composition' top-1 cosine=0.34 (LeHDC HD classifier\n"
        f"  concept notes; no prior atom on cortex 4-class router). GENUINELY NOVEL composition.\n"
        f"\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_M1p6_smoke_MM."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "verify_landing_py_status": "FAIL_all_3_seeds_FULL_paths_metrics_path_missing",
        "verify_landing_py_smoke_OK": "seeds_7_13_HP",
        "run_mode": "smoke",
        "n_seeds_landed": 1,
        "seeds_landed_HP_smoke": [7, 13],
        "auditor_downward_correction_reason": "Director_framed_3_seed_FULL_but_verify_landing_py_FAIL_on_all_3_FULL_paths_files_not_yet_synced_smoke_only_evidence",
        "N_DIM": 8192,
        "V_CB": 1024,
        "N_CLASSES": 4,
        "regimes_smoke": ["dialogue_pronoun", "ood_novel_bind"],
        "N_train_per_class_smoke": 6,
        "N_test_per_class_smoke": 3,
        "cardinality_ok": True,
        "n_units_smoke_expected": 14,
        "n_units_smoke_observed": 14,
        "arms_differ_verified": True,
        "n_llm_calls": 0,
        "CM_cross_regime_smoke_seed_7": 0.9165,
        "NR_cross_regime_smoke_seed_7": 0.2500,
        "ISO_cross_regime_smoke_seed_7": 0.7085,
        "lift_null_smoke_seed_7": 0.6665,
        "lift_iso_smoke_seed_7": 0.2080,
        "min_class_precision_MULTI_HOP_cross_regime_smoke_seed_7": 0.800,
        "per_class_precision_smoke_seed_7_dialogue_pronoun": {"REFUSE": 1.0, "RETRIEVE": 1.0, "BIND": 1.0, "MULTI_HOP": 1.0},
        "per_class_precision_smoke_seed_7_ood_novel_bind": {"REFUSE": 1.0, "RETRIEVE": 1.0, "BIND": 1.0, "MULTI_HOP": 0.6},
        "HP_route_accuracy_threshold": 0.85,
        "HP_lift_null_threshold": 0.30,
        "HP_per_class_precision_threshold": 0.70,
        "HP_lift_iso_threshold": 0.15,
        "hp_gates_smoke_seed_7_all_cleared": True,
        "positive_control_ARM_NO_ROUTER_at_chance_0p25": True,
        "positive_control_passed_broken_PC_gate": True,
        "META_RULE_Q_saturation_at_dialogue_pronoun_regime": "EXPECTED_in_distribution_saturation_not_a_violation",
        "META_RULE_Q_ood_novel_bind_at_0p833_confirms_genuine_discrimination": True,
        "test_design_concern_n_3_per_class_per_regime_binomial_stddev_0p289": True,
        "test_design_concern_full_n_60_binomial_stddev_0p089": True,
        "OOD_novel_bind_MULTI_HOP_class_precision_0p60_will_tighten_at_full": True,
        "OOD_MULTI_HOP_0p60_is_0p45_sigma_below_0p70_HP_at_smoke": True,
        "sync_lag_pattern_matches_Atom_13_v8_smoke_MM_which_was_lifted_to_Atom_15_CG_when_FULL_landed": True,
        "elapsed_s_smoke_seed_7": 0.167,
        "elapsed_s_smoke_seed_13": 0.272,
        "verified_off_data": True,
        "metrics_path_smoke_seed_7": "data/exp_cortex_attention_binding_router_v1_seed_7_smoke/metrics.json",
        "metrics_path_smoke_seed_13": "data/exp_cortex_attention_binding_router_v1_seed_13_smoke/metrics.json",
        "prereg_path": "preregs/2026-07-01_cortex_attention_binding_router_v1.md",
        "composition_parents_cg_5": [
            "T3/EXP_substrate_refuse_gate_v8_conformal_v1_3seed_FULL_CHAIN_GRADE_M1p4_MILESTONE_CLOSED",
            "T3/EXP_cortex_context_retention_v2_3seed_FULL_CHAIN_GRADE_M1p5_MILESTONE_FIRST_CORTEX_INTEGRATION_CG_IN_M3_STACK",
            "wm_multibank_codebook_cleanup_prior_CG",
            "T3/EXP_multihop_reasoning_depth_20_to_40_gpu_v1_3seed_CHAIN_GRADE_envelope_extends_to_depth_40",
            "T3/EXP_substrate_cortex_hippo_dense_layer_M_sweep_v3_3seed_CHAIN_GRADE",
        ],
        "milestone": "M1p6_first_shot_v1_second_cortex_integration_cell_in_M3_stack",
        "milestone_status": "NOT_closed_smoke_single_seed_awaits_3_seed_FULL",
        "cert_tier": "measured_mechanism",
        "cert_increment_delta": 0,
        "expansion_criterion_to_CG_and_M1p6_closure": (
            "land_3_seed_FULL_verify_landing_py_OK_all_HP_gates_cleared_all_3_seeds_"
            "cross_seed_cv_le_0p10_cardinality_full_META_RULE_Q_not_violated_"
            "particularly_verify_OOD_MULTI_HOP_class_precision_at_full_n_60_tightened_from_smoke_0p60"
        ),
    },
}
LEDGER_23 = {
    "ts": TS_NOW,
    "op": "cert_ruling_measured_mechanism_auditor_downward_from_M1p6_closure_framing_to_single_seed_smoke_MM",
    "atom_id": f"math::{ATOM_23_ID}",
    "cert_status": "measured_mechanism",
    "cert_class": "single_seed_smoke_HP_at_M1p6_awaits_3_seed_FULL_for_CG_lift_and_milestone_closure",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_M1p6_smoke_MM",
    "cell_commit": COMMIT,
    "verdict": (
        "MEASURED_MECHANISM_auditor_downward_correction_from_M1p6_closure_framing_"
        "verify_landing_py_FAIL_all_3_FULL_paths_metrics_path_missing_files_not_yet_synced_"
        "smoke_seed_7_HP_smoke_seed_13_HP_available_on_disk_"
        "smoke_seed_7_CM_0p917_NR_0p250_ISO_0p708_lift_null_0p667_lift_iso_0p208_min_class_prec_0p800_"
        "all_4_HP_gates_cleared_cardinality_14_of_14_arms_differ_zero_LLM_calls_"
        "positive_control_ARM_NO_ROUTER_at_chance_0p250_both_regimes_broken_PC_gate_passes_"
        "META_RULE_Q_dialogue_pronoun_saturation_EXPECTED_in_distribution_ood_novel_bind_at_0p833_confirms_genuine_discrimination_"
        "OOD_MULTI_HOP_class_precision_0p60_at_smoke_0p45_sigma_below_0p70_HP_full_at_n_60_tightens_stddev_from_0p289_to_0p089_will_reveal_regime_specific_behavior_"
        "M1p6_milestone_NOT_closed_on_smoke_single_seed_awaits_3_seed_FULL_"
        "composes_5_CG_parent_atoms_M1p4_v8_Atom_15_M1p5_v2_Atom_18_WM_multibank_multihop_Atom_6_dense_hopfield_Atom_1_"
        "GENUINELY_NOVEL_composition_cross_arc_cosine_0p34_below_0p40_threshold_"
        "second_cortex_integration_cell_in_M3_stack_per_cell_author_annotation_"
        "sync_lag_pattern_matches_Wave_6_Atom_13_v8_smoke_MM_lifted_to_Wave_7_Atom_15_v8_3_seed_FULL_CG_when_files_synced_"
        "expansion_criterion_land_3_seed_FULL_verify_landing_py_OK_all_HP_gates_cross_seed_cv_le_0p10_M1p6_closes"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "metrics_paths_smoke_available": [
            "data/exp_cortex_attention_binding_router_v1_seed_7_smoke/metrics.json",
            "data/exp_cortex_attention_binding_router_v1_seed_13_smoke/metrics.json",
        ],
        "metrics_paths_FULL_missing": [
            "data/exp_cortex_attention_binding_router_v1_seed_7/metrics.json (NOT ON DISK)",
            "data/exp_cortex_attention_binding_router_v1_seed_13/metrics.json (NOT ON DISK)",
            "data/exp_cortex_attention_binding_router_v1_seed_19/metrics.json (NOT ON DISK)",
        ],
        "prereg_path": "preregs/2026-07-01_cortex_attention_binding_router_v1.md",
        "future_CG_atom_will_supersede_this": True,
        "atom_qualified_id": f"math::{ATOM_23_ID}",
    },
    "supersedes": None,
    "note": (
        "M1p6_cortex_attention_binding_router_smoke_MEASURED_MECHANISM_auditor_downward_from_closure_framing_"
        "verify_landing_py_FAIL_all_3_seed_FULL_paths_files_not_yet_synced_smoke_variants_only_"
        "smoke_seed_7_and_13_both_HP_all_4_HP_gates_cleared_positive_control_at_chance_META_RULE_Q_not_violated_"
        "OOD_MULTI_HOP_class_precision_0p60_at_smoke_will_tighten_at_full_n_60_reveals_regime_specific_behavior_"
        "M1p6_milestone_NOT_closed_awaits_3_seed_FULL_all_prior_milestones_today_M1p4_M1p5_required_3_seed_FULL_"
        "composes_5_CG_parents_M1p4_v8_M1p5_v2_WM_multibank_multihop_dense_hopfield_"
        "second_cortex_integration_cell_in_M3_stack_LeHDC_class_HV_routing_pattern_"
        "GENUINELY_NOVEL_composition_cross_arc_cosine_0p34_below_novelty_threshold_"
        "sync_lag_pattern_matches_Wave_6_Atom_13_and_Wave_7_Atom_15_supersession_chain_"
        "when_FULL_3_seed_lands_a_proper_CG_atom_will_be_filed_and_will_supersede_this_atom_"
        "if_M1p6_closes_at_FULL_this_would_be_third_cortex_milestone_closure_today_M1p4_M1p5_M1p6_"
        "test_design_concern_n_3_at_smoke_binomial_stddev_0p289_full_at_n_60_tightens_to_0p089_2p2x_reduction_"
        "cell_author_annotations_honest_ood_novel_bind_MULTI_HOP_0p60_will_be_measured_definitively_at_full"
    ),
}

# =====================================================================
# Atomic write
# =====================================================================
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
    math_before, math_after = atomic_append_jsonl(MATH_ATOMS, [ATOM_23])
    print(f"math/atoms.jsonl: {math_before} -> {math_after} (+{math_after - math_before})")

    ledger_records = [LEDGER_23]
    led_before, led_after = atomic_append_jsonl(CERT_LEDGER, ledger_records)
    print(f"meta/cert_ledger.jsonl: {led_before} -> {led_after} (+{led_after - led_before})")

    print()
    print(f"CERT delta: +0 (Atom 23 M1.6 smoke MM; awaits FULL 3-seed for CG lift + milestone closure)")
    print(f"  Atom 23: cortex_attention_binding_router_v1 smoke seed 7 MM (single-seed)")
    print(f"           verify_landing.py FAIL on 3-seed FULL paths - files NOT yet on disk")
    print(f"           Smoke seeds 7 + 13 both HP; all 4 HP gates cleared cross-regime")
    print(f"           OOD MULTI_HOP class precision 0.60 at smoke will tighten at full")
    print(f"           Sync-lag pattern matches Atom 13 (v8 smoke MM) -> Atom 15 (v8 3-seed FULL CG)")
    print(f"           M1.6 milestone NOT closed awaits 3-seed FULL")
    print(f"           Composes 5 CG parents; genuinely novel composition")
    print(f"Session-cumulative today: CG=+13, MM=+8, HF=+2, meta_amendment=+2")
    print(f"Timestamp: {TS_NOW}")
    print(f"Commit: {COMMIT}")


if __name__ == "__main__":
    main()
