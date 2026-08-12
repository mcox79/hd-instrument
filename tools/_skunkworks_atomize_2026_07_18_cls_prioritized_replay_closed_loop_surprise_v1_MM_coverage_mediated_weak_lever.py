"""
A5-gated atomization: cls_prioritized_replay_closed_loop_surprise_v1 -> MEASURED_MECHANISM
(weak coverage-mediated priority lever; NOT a capability win) (2026-07-18).

Director framed MIDDLE_BAND_WEAK_LEVER + honest deflation (did NOT declare HARD_PASS on a positive-sign result).
Auditor tier = MEASURED_MECHANISM: the BANKABLE content is the MECHANISM DECOMPOSITION, not the weak delta_E.

VET independently off-disk (.venv, Fix #28 -- recompute off metrics.json per_unit + a FRESH FULL re-run, NOT
verdict_msg):
  1. BYTE-REPRO: fresh full 3-seed re-run is BIT-IDENTICAL -- 0/36 arm-digest mismatches, mean_dE [0.055,0.125]
     reproduced EXACT. (This cell PINS OMP/OPENBLAS_NUM_THREADS=1 at import, so unlike the budget-envelope
     sibling 6f22af2de it IS bit-reproducible -- provenance STRENGTH.)
  2. delta_E (closed_loop_E - uniform_E): structured end SF0.75 per-seed 0.010/0.062/0.093 mean 0.055, sd 0.042,
     t=2.27 (n=3, NOT sig at 0.05); SF0.55 0.093/0.177/0.104 mean 0.125, t=4.73. Sign POSITIVE on ALL 6
     seed-instances across both SF (sign test p=(1/2)^6=0.0156) -- the SIGN is robust, the MAGNITUDE is weak and
     below the pre-reg 0.08 bar at the structured end (hp=1/3, hf=1/3). Confirms MIDDLE, not null, not positive.
  3. COVERAGE-MEDIATION (the crux mechanism): n_distinct_replayed clos 74.7 > unif 66.3 > stat 61.0 (both SF).
     E-retention TRACKS distinct-coverage: pooled linear fit E ~ 0.72*(distinct/96)+0.018, r=0.944 at SF0.75
     (r=0.887 SF0.55). Implied per-replayed-item retention q is PRIORITY-INVARIANT at the structured end:
     uniform 0.711, closed 0.713, static 0.688 (spread 0.025). => priority does NOT give better per-item
     protection; it only changes HOW MANY distinct items get touched. Closed-loop wins by ROTATING priority to
     newly-at-risk items -> touches more distinct items -> wastes fewer exposures re-protecting already-safe
     items = a COVERAGE-EFFICIENCY effect, NOT targeted protection.
  4. static BELOW uniform (the interesting sub-result): SF0.75 3/3 seeds (mean -0.049), SF0.55 2/3 (mean -0.028,
     NOT all -- honest downward vs a clean 'always below' read). MECHANISM: after the old block the net has
     memorized all items (E_init 1.0) so snapshot surprise ~0 for all -> a weakly-biased FROZEN weight
     concentrates replay on a fixed small subset every block -> fewer distinct (61) -> below uniform's broader
     coverage. A frozen priority is coverage-HARMFUL; it must be CURRENT. Not a timing artifact -- it is the
     coverage mechanism running in reverse.
  5. delta_Q ~0 (no distributed benefit): SF0.75 -0.014 (per-seed -0.125/-0.042/+0.125), SF0.55 +0.021 --
     STRADDLES zero, no consistent sign. Fresh-net confounds recover 0.000 of never-replayed Q (fn_u 0.000,
     fn_s 0.000 at SF0.75; fn_s 0.007 at SF0.55) -> the independent-content design DEFEATS the generalization
     confound (same design as parent 35e1fbea9). Replay benefit is CONFINED to the directly-allocated E-pool.
  6. DESIGN-GATE: real uniform baseline in-band (0.521/0.642); can-fail (HARD_FAIL band delta_E<=0.02 defined,
     did NOT trigger -- weak positive); difficulty-ON (all 6 gates pass: init 1.0, no_replay collapses to 0.097,
     uniform>floor, uniform in band, both confounds fail Q); ONE variable (arms_differ=True, matched exposures
     96/96/96). Compliant.

TIER: MEASURED_MECHANISM. The weak delta_E alone would be MIDDLE_BAND / near-null; the PROVEN BOUNDARY worth
banking is the mechanism decomposition -- priority replay in a rank-1 Hebbian / additive store is a
COVERAGE-EFFICIENCY lever (reshuffles WHICH items are covered within a fixed per-item protection capacity), NOT
a targeted-protection lever, and a FROZEN priority is coverage-harmful. Counts toward CERT as a proven boundary.

THREE-FACTOR CROSS-CHECK (over-reach guard): the cell is CONSISTENT WITH but does NOT PROVE the three-factor /
eligibility-trace plasticity prescription. It shows per-item protection is priority-INVARIANT (you cannot
protect an at-risk item HARDER by prioritizing it, only cover MORE items), which MOTIVATES the need for a
differential-weighting plasticity rule IF targeted per-item protection is the goal -- but the cell's own outcome
is a weak POSITIVE via coverage, not the HARD_FAIL the prereg envisioned, so 'this cell supports three-factor
plasticity' would be a mild over-reach. Correct framing: the cell LOCALIZES that priority-alone buys only
coverage; targeted per-item protection is an untested hypothesis this cell motivates.

Cross-arc overlap check (USER-locked): substrate_query.sh top hit is the RESEARCH-DRILL NOTE that inspired the
cell (SuRe surprise-prioritized-replay template, cosine 0.3154, credited scaffold NOT a prior finding); nearest
ATOM is generic 'consolidation' (0.2998, below 0.30). No prior EXPERIMENT-cell finding on coverage-mediated
priority replay at cosine>0.30 -> genuine novel allocation-axis extension of the CLS arc, not a rediscovery.

A5: read -> build -> tmp write + fsync -> os.replace -> re-read + verify count delta + tail-id match, both files.
LOCAL ONLY: store_head_at_write=unsynced_needs_orchestrator + needs_orchestrator_store_sync=True; NO origin push.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"
ATOMIZED_BY = "skunkworks_landed_vet_cls_prioritized_replay_closed_loop_surprise_v1_MM_coverage_mediated_weak_lever_2026-07-18"
ATOMIZED_DATE = "2026-07-18"
ANCHOR = "cls_prioritized_replay_closed_loop_surprise_v1"
CELL_COMMIT = "5e929df81"

# Primary parent: CLS-independent-content MM (independent-content design this cell reuses)
PARENT_ATOM_ID = ("math::LANDED_VET_cls_distributed_protection_independent_content_v1_MEASURED_MECHANISM_"
                  "REVIVAL_confound_DISSOLVED_but_consolidation_PARTIAL_the_a15e4d91_generalization_confound_"
                  "GENUINELY_dissolved_with_INDEPENDENT_per_item_targets_codebook_vec_unique_per_item_"
                  "independent_of_class_FOUR_independent_confounds_ALL_recover_0p000_of_heldout_at_EVERY_"
                  "structure_level_1NN_proximity_fresh_net_on_subsample_AND_auditor_added_fresh_net_2x_epochs_"
                  "800_rules_out_train_subsample_longer_AND_class_centroid_predictor_argmax_over_codebook_of_"
                  "mean_eligible_in_class_target_rules_out_class_to_target_leakage_DIRECTLY_independence_design_"
                  "SOUND_byte_reproduce_EXACT_per_unit_plus_all_5_arm_SHA256_digests_bit_identical_subsample_"
                  "recovers_0p247_0p343_0p392_at_SF0p75_0p55_0p35_vs_confounds_0p000_confound_margin_0p23_to_"
                  "0p48_all3seeds_distributed_consolidation_of_independent_content_EXISTS_NOT_generalization_"
                  "confound_beating_3of3_BUT_TIER_MM_not_CG_cell_own_HARD_PASS_bar_NOT_met_abs_0of3_max_0p269_"
                  "below_0p40_floor_margin_over_no_replay_1of3_0p148_0p167_0p139_below_0p15_supported_claim_"
                  "WEAKER_than_initial_framing_AUDITOR_REFINEMENT_equal_compute_control_no_replay_plus_same_"
                  "extra_samples_per_block_but_RANDOM_fillers_recovers_0p139_0p120_0p157_ABOVE_plain_no_replay_"
                  "0p096_so_of_raw_floor_margin_0p151_about_0p043_generic_anti_overfit_regularization_and_only_"
                  "0p108_REAL_structure_carrying_trace_specific_McClelland_consolidation_sub_minus_equalcompute_"
                  "0p092_0p121_0p112_all3_positive_0p247_abs_decomposes_0p096_residual_survives_anyway_plus_"
                  "0p043_generic_reg_plus_0p108_genuine_structure_consolidation_isolated_effect_about_0p11_NOT_"
                  "0p25_abs_NOR_0p15_floor_margin_ENVELOPE_structure_dependence_directional_floor_margin_plus0p151"
                  "_plus0p083_minus0p077_SF0p75_0p55_0p35_BUT_arbitrary_end_difficulty_OFF_no_replay_does_not_"
                  "forget_0p407_at_SF0p35_changes_2_things_NOT_clean_control_noted_trend_3seed_7_17_23_FULL_"
                  "confirms_and_REINFORCES_exp_dev_MIDDLE_BAND_35e1fbea9_2026-07-18")

# Sibling parent: budget-envelope MM (E-pool-coverage-vs-Q-distributed picture; reshuffle-not-add)
BUDGET_ENV_ATOM_ID = ("math::MM_MEASURED_MECHANISM_cls_distributed_protection_budget_envelope_v1_distributed_"
                      "consolidation_of_never_replayed_independent_content_is_NOT_budget_efficient_the_genuine_"
                      "diversity_matched_equal_compute_corrected_STRUCT_filler_protection_scales_WORSE_THAN_"
                      "LINEARLY_CONVEX_ACCELERATING_with_replay_budget_approx0_at_8to17pct_npos_0of3_at_8p3pct_"
                      "plus0p03to0p05_at_16p7pct_plus0p11_at_25pct_plus0p15_at_33pct_plus0p30_at_50pct_"
                      "plus0p45to0p50_at_75pct_meaningful_protection_requires_rehearsing_a_LARGE_fraction_does_"
                      "NOT_support_distributed_consolidation_as_a_sub_linear_foundation_for_continual_textbook_"
                      "ingestion_CONCLUSION_ROBUST_TO_CONTROL_CHOICE_conservative_random_filler_bracket_only_"
                      "clears_zero_at_ge50pct_diversity_matched_struct_at_about17pct_either_way_low_budget_"
                      "approx0_STRUCT_filler_is_the_FAIR_control_one_variable_differs_only_cue_to_target_content_"
                      "reconciles_parent_0p11_at_25pct_confounds_0p000_at_ALL_budgets_AND_ALL_seeds_both_runs_"
                      "max0_over_18_units_independence_robust_posctrl_25pct_0p241_to_0p247_dev_under0p01_REPRO_"
                      "CAVEAT_NOT_bit_reproducible_independent_rerun_drifts_plusminus0p02to0p05_OpenBLAS_"
                      "multithread_float_nondeterminism_not_seed_bug_shape_confounds_posctrl_conclusion_all_"
                      "robust_across_rerun_cell_classifier_LINEAR_label_UNDERSTATES_curve_is_convex_CAVEAT_"
                      "synthetic_MLP_toy_regime_strong_hypothesis_pending_real_data_3seed_7_17_23_FULL_envelope_"
                      "char_composes_parent_35e1fbea9_6f22af2de_2026-07-18")

XARC = ("substrate_query.sh 'surprise prioritized replay uniform matched budget consolidation coverage rank-1 "
        "Hebbian distinct' -> top hit is the RESEARCH-DRILL NOTE that inspired the cell (SuRe arXiv 2511.22367 "
        "surprise-prioritized-replay template, cosine 0.3154, source notes/research_drill_per_bio_primitive_"
        "empirical_tests_substrate_3x_2026-06-04.md -- a CREDITED design scaffold, NOT a prior finding); nearest "
        "ATOM is generic 'consolidation' concept (0.2998, below 0.30). No prior EXPERIMENT-cell finding on "
        "coverage-mediated priority replay at cosine>0.30 -> genuine novel allocation-axis extension of the CLS "
        "arc, not a rediscovery.")

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

ATOM_ID = ("math::MM_MEASURED_MECHANISM_cls_prioritized_replay_closed_loop_surprise_v1_closed_loop_surprise_"
           "prioritized_replay_is_a_COVERAGE_EFFICIENCY_lever_NOT_targeted_protection_at_matched_budget_"
           "closed_loop_E_beats_uniform_E_WEAKLY_delta_E_0p055_structured_SF0p75_perseed_0p010_0p062_0p093_"
           "t2p27_n3_NOT_sig_below_0p08_bar_hp1of3_hf1of3_and_0p125_at_SF0p55_but_SIGN_POSITIVE_all_6_seed_"
           "instances_signtest_p0p0156_MECHANISM_the_ordering_closed_gt_uniform_gt_static_is_MEDIATED_by_"
           "DISTINCT_COVERAGE_n_distinct_replayed_74p7_gt_66p3_gt_61p0_E_tracks_coverage_r0p944_slope0p72_"
           "per_replayed_item_retention_q_PRIORITY_INVARIANT_0p711_0p713_0p688_at_SF0p75_closed_loop_wins_by_"
           "ROTATING_priority_to_newly_at_risk_items_touching_more_distinct_items_wasting_fewer_exposures_"
           "reprotecting_safe_items_FROZEN_static_snapshot_concentrates_on_fixed_subset_fewer_distinct_falls_"
           "BELOW_uniform_3of3_SF0p75_priority_must_be_CURRENT_NO_distributed_benefit_delta_Q_straddles_zero_"
           "minus0p014_SF0p75_plus0p021_SF0p55_fresh_net_confounds_recover_0p000_of_never_replayed_Q_"
           "independent_content_design_defeats_generalization_confound_replay_benefit_CONFINED_to_directly_"
           "allocated_pool_priority_RESHUFFLES_which_items_covered_within_FIXED_per_item_capacity_does_NOT_ADD_"
           "net_protected_capacity_per_exposure_CONSISTENT_WITH_but_does_NOT_PROVE_three_factor_plasticity_"
           "prescription_byte_reproduce_EXACT_0of36_arm_digest_mismatch_OMP1_pinned_design_gate_compliant_real_"
           "uniform_baseline_in_band_can_fail_HF_band_not_triggered_difficulty_ON_one_variable_matched_exposures_"
           "96_synthetic_MLP_toy_hypothesis_pending_real_data_3seed_7_17_23_FULL_composes_35e1fbea9_6f22af2de_"
           "DEFLATED_from_positive_sign_result_5e929df81_2026-07-18")

CLAIM = (
    "MATH MEASURED_MECHANISM (weak COVERAGE-MEDIATED priority lever; DEFLATED from a positive-sign result, NOT a "
    "capability win). At MATCHED replay budget (B=12 distinct eligible items/block over E=96, ALPHA=1.0), "
    "CLOSED-LOOP surprise-prioritized replay (sample by the net's CURRENT 1-reciprocal_rank surprise, recomputed "
    "each block) beats UNIFORM random replay on directly-allocated E-pool retention WEAKLY: delta_E=0.055 at the "
    "structured end (SHARED_FRAC=0.75; per-seed 0.010/0.062/0.093, sd 0.042, t=2.27 n=3 NOT significant, below "
    "the pre-reg 0.08 bar, hp=1/3 hf=1/3), delta_E=0.125 at SF=0.55 (0.093/0.177/0.104). The SIGN is positive on "
    "ALL 6 seed-instances across both structure levels (sign test p=0.0156) but the MAGNITUDE is weak and "
    "regime-dependent -> MIDDLE_BAND, not null, not positive. THE BANKABLE CONTENT IS THE MECHANISM: the ordering "
    "closed_loop (0.576) > uniform (0.521) > static-snapshot (0.472) is FULLY MEDIATED BY DISTINCT-COVERAGE of "
    "the eligible pool -- n_distinct_replayed is 74.7 (closed) > 66.3 (uniform) > 61.0 (static), and E-retention "
    "tracks distinct-coverage across arms (pooled fit E ~ 0.72*(distinct/96)+0.018, r=0.944 at SF0.75) with "
    "per-replayed-item retention q PRIORITY-INVARIANT (0.711 uniform / 0.713 closed / 0.688 static, spread "
    "0.025). Closed-loop wins by ROTATING priority to newly-at-risk items -> touching MORE distinct items -> "
    "wasting fewer exposures re-protecting already-safe items = a COVERAGE-EFFICIENCY effect, NOT better per-item "
    "protection. A FROZEN priority snapshot is coverage-HARMFUL: because the net has just memorized all items "
    "(E_init=1.0) snapshot surprise ~0, so the weakly-biased frozen weight concentrates replay on a fixed small "
    "subset every block -> FEWER distinct (61) -> BELOW uniform (3/3 seeds at SF0.75; 2/3 at SF0.55, honest "
    "downward vs an 'always below' read) -> priority must be CURRENT. NO distributed benefit: delta_Q straddles "
    "zero (-0.014 SF0.75, +0.021 SF0.55) and both fresh-net confounds recover 0.000 of the never-replayed Q "
    "(independent-content design defeats the generalization confound, same design as parent 35e1fbea9) -> replay "
    "benefit is CONFINED to the directly-allocated pool. NET: priority replay in a rank-1 Hebbian / additive "
    "store RESHUFFLES WHICH items are covered within a FIXED per-item protection capacity; it does NOT add net "
    "protected capacity per exposure. THREE-FACTOR CROSS-CHECK: this is CONSISTENT WITH but does NOT PROVE the "
    "three-factor / eligibility-trace plasticity prescription -- it shows per-item protection is priority-"
    "invariant (motivating a differential-weighting rule IF targeted protection is wanted), but its own outcome "
    "is a weak coverage-positive, not the HARD_FAIL the pre-reg envisioned; 'supports three-factor plasticity' "
    "is a mild over-reach. CAVEAT: synthetic MLP toy regime -> mechanism HYPOTHESIS, not a settled law.")

RECOMPUTE = (
    "INDEP recompute (.venv, Fix #28: off metrics.json per_unit AND a fresh full 3-seed re-run of the REAL cell, "
    "NOT verdict_msg). (1) BYTE-REPRO: fresh full re-run is BIT-IDENTICAL -- 0/36 arm-digest SHA256 mismatches, "
    "mean_dE [0.055,0.125] reproduced EXACT (this cell pins OMP/OPENBLAS/MKL/NUMEXPR_NUM_THREADS=1 at import, so "
    "unlike sibling 6f22af2de it IS bit-reproducible -- provenance strength). (2) delta_E clos-unif: SF0.75 "
    "per-seed 0.010/0.062/0.093 mean 0.055 sd 0.042 se 0.024 t=2.27 (df=2, p~0.075 NOT sig); SF0.55 0.093/0.177/"
    "0.104 mean 0.125 t=4.73. Sign positive 6/6 seed-instances -> sign test p=(1/2)^6=0.0156. HP requires "
    "delta_E>=0.08 AND delta_Q>=-0.03: at SF0.75 only seed23 clears (hp=1/3); seed7 delta_E=0.010<=0.02 (hf=1/3). "
    "(3) COVERAGE-MEDIATION: n_distinct clos 74.7 > unif 66.3 > stat 61.0 (both SF). Pooled E-on-(distinct/96) "
    "lstsq fit slope 0.720 intercept 0.018 r=0.944 (SF0.75), slope 0.914 r=0.887 (SF0.55). Implied per-replayed-"
    "item q=(E-floor*(1-frac))/frac with no_replay floor 0.097: uniform 0.711, closed 0.713, static 0.688 at "
    "SF0.75 (INVARIANT); at SF0.55 (floor 0.257) 0.815/0.896/0.820 (closed marginally higher -> a small genuine "
    "per-item bonus MAY exist at the easier regime, absent at the structured end). (4) static-below-uniform: "
    "SF0.75 per-seed -0.114/-0.021/-0.011 (all<0, 3/3); SF0.55 -0.042/+0.011/-0.052 (2/3, NOT all -- honest "
    "downward). closed-static robust 6/6: SF0.75 +0.124/+0.083/+0.104, SF0.55 +0.135/+0.166/+0.156. (5) delta_Q "
    "clos-unif: SF0.75 -0.125/-0.042/+0.125 mean -0.014; SF0.55 +0.062/-0.042/+0.042 mean +0.021 -> straddles 0. "
    "fresh_net confounds Q: fn_u 0.000 fn_s 0.000 (SF0.75), fn_s 0.007 (SF0.55) -> generalization confound "
    "defeated. (6) DESIGN-GATE: uniform in band (0.521/0.642), can-fail (HF delta_E<=0.02 defined, not "
    "triggered), difficulty-ON (all 6 gates pass), one-variable (arms_differ=True, matched exposures 96/96/96).")

SCOPE = (
    "Synthetic MLP toy regime (numpy cue(256)->tanh(H=160)->linear(D_T=64) MSE regression; 144 old items = 12 "
    "classes x 12 exemplars; E=96 replay-eligible / Q=48 never-replayed held-out; 8 interference blocks x 3 new "
    "classes; E_OLD=400 E_NEW=200 LR=0.04; matched budget B=12/block; ALPHA=1.0; retrieval = nearest-target over "
    "the 144-item codebook, chance 0.0069). This is a MECHANISM DECOMPOSITION, NOT capability-at-scale. "
    "Load-bearing limits: (a) SYNTHETIC TOY -- the coverage-mediation mechanism is a strong HYPOTHESIS pending "
    "real ingestion data. (b) OPERATING-POINT-SCOPED: swept only SF in {0.75,0.55} at ALPHA=1.0, B=12/96; ALPHA "
    "(priority sharpness) and budget were NOT swept. The MM claim is 'weak coverage-mediated lever AT THIS "
    "operating point', NOT 'weak universally' -- the coverage mechanism is DIRECTLY MEASURED (n_distinct_"
    "replayed), so it does not depend on the omitted sweep; a HIGHER ALPHA would likely REDUCE distinct coverage "
    "(sharper per-block concentration) and could weaken/flip the sign, which if anything STRENGTHENS 'coverage "
    "is the mechanism'. (c) the weak per-item bonus hint at SF0.55 (q 0.896 closed vs 0.815 uniform) is single-"
    "regime and NOT load-bearing; at the structured end q is invariant (pure coverage). (d) Do NOT read this as "
    "'priority replay is useless' (it weakly helps via coverage) NOR as 'proof you need three-factor plasticity' "
    "(consistent-with, not proof). The robust bankable results: coverage-mediation (per-item protection priority-"
    "invariant), current-not-frozen priority, no distributed benefit, replay confined to the touched pool.")

METRICS = {
    "shared_fracs": [0.75, 0.55], "seeds": [7, 17, 23], "n_units": 6, "b_replay": 12, "n_eligible": 96,
    "n_never_replayed": 48, "alpha": 1.0, "chance": 0.0069,
    "delta_E_SF075_perseed": [0.010, 0.062, 0.093], "delta_E_SF075_mean": 0.055,
    "delta_E_SF075_sd": 0.042, "delta_E_SF075_t": 2.27, "delta_E_SF075_hp": "1/3", "delta_E_SF075_hf": "1/3",
    "delta_E_SF055_perseed": [0.093, 0.177, 0.104], "delta_E_SF055_mean": 0.125, "delta_E_SF055_hp": "2/3",
    "sign_positive_all_6_instances": True, "sign_test_p": 0.0156,
    "E_ret_SF075": {"no_replay": 0.097, "uniform": 0.521, "closed": 0.576, "static": 0.472},
    "E_ret_SF055": {"no_replay": 0.257, "uniform": 0.642, "closed": 0.767, "static": 0.615},
    "n_distinct_replayed": {"uniform": 66.3, "closed": 74.7, "static": 61.0},
    "coverage_fit_SF075": {"slope": 0.720, "intercept": 0.018, "r": 0.944},
    "coverage_fit_SF055": {"slope": 0.914, "r": 0.887},
    "implied_per_item_q_SF075": {"uniform": 0.711, "closed": 0.713, "static": 0.688, "spread": 0.025},
    "implied_per_item_q_SF055": {"uniform": 0.815, "closed": 0.896, "static": 0.820},
    "static_below_uniform_SF075_perseed": [-0.114, -0.021, -0.011],
    "static_below_uniform_SF055_perseed": [-0.042, 0.011, -0.052],
    "closed_minus_static_SF075": [0.124, 0.083, 0.104], "closed_minus_static_SF055": [0.135, 0.166, 0.156],
    "delta_Q_SF075_mean": -0.014, "delta_Q_SF055_mean": 0.021,
    "confound_fresh_net_Q": {"fn_uniform_SF075": 0.000, "fn_surprise_SF075": 0.000, "fn_surprise_SF055": 0.007},
    "byte_reproduce": "EXACT_0of36_arm_digest_mismatch_OMP1_pinned",
    "design_gate": "compliant_real_baseline_in_band_can_fail_difficulty_on_one_variable_matched_exposures_96",
    "cell_verdict": "MIDDLE_BAND_WEAK_LEVER", "auditor_tier": "MEASURED_MECHANISM (mechanism decomposition)",
}

COMPOSES = [
    "COMPOSES-WITH the parent CLS-independent-content MM (cell 35e1fbea9): reuses its independent-content design "
    "(unique codebook target per item) which defeats the generalization confound (fresh-net confounds 0.000 on "
    "Q). That atom proved distributed consolidation of independent content EXISTS but PARTIAL (~0.11 @25%); THIS "
    "atom adds the ALLOCATION axis -- given a fixed budget, priority (vs uniform) only buys COVERAGE, not "
    "per-item protection. Parent NOT superseded.",
    "COMPOSES-WITH + SHARPENS the budget-envelope MM (cell 6f22af2de): that atom showed never-replayed Q "
    "(distributed) protection scales WORSE-than-linearly with budget; THIS atom shows directly-allocated E-pool "
    "protection scales ~LINEARLY with distinct-COVERAGE (E ~ 0.72*coverage) with priority-invariant per-item q "
    "-> together: replay protects ~linearly what it TOUCHES, spillover to untouched is convex/weak, and priority "
    "changes only WHICH items are touched. Consistent 'reshuffle-within-fixed-capacity, does-not-add' picture.",
    "credit: Schaul 2016 Prioritized Experience Replay (surprise-ordered replay beat uniform on 41/49 Atari) -- "
    "the DL analog; here the substrate's rank-1 Hebbian analog realizes the priority advantage as a COVERAGE-"
    "efficiency effect rather than the targeted-protection effect PER exploits in a gradient-trained DQN. "
    "Lillicrap 2020 NGRAD / three-factor rules = the untested differential-weighting hypothesis this motivates.",
]

atom = {
    "id": ATOM_ID,
    "name": CLAIM,
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": ("confirmed_measured_mechanism_closed_loop_surprise_prioritized_replay_is_a_coverage_"
                    "efficiency_lever_not_targeted_protection_weak_delta_E_0p055_structured_sign_positive_all_6_"
                    "seed_instances_but_below_0p08_bar_ordering_closed_gt_uniform_gt_static_mediated_by_distinct_"
                    "coverage_per_item_retention_priority_invariant_frozen_priority_coverage_harmful_must_be_"
                    "current_no_distributed_benefit_delta_Q_straddles_zero_confounds_0p000_replay_confined_to_"
                    "touched_pool_reshuffle_not_add_net_capacity_consistent_with_but_not_proof_of_three_factor_"
                    "plasticity_byte_reproduce_exact_design_gate_compliant_synthetic_toy_hypothesis_pending_real"),
    "cert_class": ("prioritized_replay_allocation_coverage_mediated_weak_lever_per_item_protection_priority_"
                   "invariant_current_not_frozen_no_distributed_benefit_reshuffle_not_add_capacity_measured_"
                   "mechanism_decomposition"),
    "description": (CLAIM + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + RECOMPUTE
                    + "\n\nHONEST SCOPE: " + SCOPE),
    "aliases": [],
    "ts_iso": _iso,
    "ts": _ts,
    "metadata": {
        "provenance_quality": "off_disk_recompute_plus_fresh_full_rerun_BYTE_IDENTICAL_0of36_digest_mismatch_OMP1_pinned",
        "anchor": ANCHOR,
        "cell_commit": CELL_COMMIT,
        "supersedes": None,
        "store_head_at_write": "unsynced_needs_orchestrator",
        "metrics_path": "data/exp_cls_prioritized_replay_closed_loop_surprise_v1/metrics.json",
        "verified_off_data": RECOMPUTE,
        "honest_scope": SCOPE,
        "metrics": METRICS,
        "mechanism_ruling": (
            "The bankable content is the MECHANISM DECOMPOSITION, not the weak delta_E. The closed>uniform>static "
            "E-ordering is FULLY accounted for by n_distinct_replayed (coverage): pooled E-on-coverage fit r=0.944 "
            "at the structured end, and implied per-replayed-item retention q is PRIORITY-INVARIANT (0.711/0.713/"
            "0.688). So closed-loop's weak win is a COVERAGE-EFFICIENCY effect (it rotates priority to newly-at-"
            "risk items -> touches more distinct items -> spends fewer exposures re-protecting already-safe items), "
            "NOT targeted per-item protection. Frozen (static-snapshot) priority is coverage-HARMFUL because "
            "post-memorization surprise ~0 makes the frozen weight concentrate on a fixed small subset -> fewer "
            "distinct -> below uniform. This precisely operationalizes 'reshuffle within fixed per-item capacity, "
            "does not add net protected capacity per exposure'."),
        "three_factor_over_read_guard": (
            "The cell is CONSISTENT WITH but does NOT PROVE the three-factor / eligibility-trace plasticity "
            "prescription. It shows per-item protection is priority-INVARIANT (you cannot protect an at-risk item "
            "HARDER by prioritizing it, only cover MORE items), which MOTIVATES a differential-weighting plasticity "
            "rule IF targeted per-item protection is the goal -- but the cell's own outcome is a weak coverage-"
            "POSITIVE, not the HARD_FAIL the pre-reg envisioned (priority ties/loses). Stating 'this cell supports "
            "the fix is a differentially-weighting plasticity rule' is a MILD OVER-REACH; the honest framing is "
            "that the cell LOCALIZES that priority-alone buys only coverage, leaving targeted protection an "
            "untested hypothesis."),
        "over_reads_avoided": [
            "Director LED this DEFLATED (weak-lever + mechanism, NOT HARD_PASS on a positive-sign result) -- "
            "CONFIRMED appropriate. The delta_E is weak (t=2.27 n=3 NOT significant at the structured end); only "
            "the SIGN (6/6 positive) and the MECHANISM are robust. No inflation to a capability claim.",
            "Do NOT cite delta_E=0.055 as a demonstrated lever magnitude -- it is below the pre-reg 0.08 bar and "
            "not individually significant; cite the COVERAGE MECHANISM (per-item protection priority-invariant) "
            "as the robust result.",
            "Do NOT read 'weak win' as 'proof three-factor plasticity is the fix' -- consistent-with, not proof.",
            "Do NOT generalize past the operating point (ALPHA=1.0, B=12/96, SF in {0.75,0.55}); ALPHA/budget "
            "unswept. The coverage mechanism is measured, so it holds AT this point regardless.",
            "Synthetic MLP toy -> mechanism HYPOTHESIS pending real ingestion data, NOT a settled law.",
        ],
        "revival_criteria": [
            "Test whether a three-factor / eligibility-trace plasticity rule (differential per-item update "
            "weighting) breaks the priority-invariant per-item-q ceiling and yields TARGETED protection beyond "
            "coverage -- this is the untested hypothesis this cell motivates (would be the real positive result).",
            "Sweep ALPHA (priority sharpness) and budget to map where coverage-efficiency is maximized vs where "
            "sharpening hurts by over-concentrating (predicted: high ALPHA reduces distinct coverage -> weakens).",
            "Confirm coverage-mediation on REAL continual-ingestion data before treating it as a law; the "
            "synthetic-toy mechanism is a strong hypothesis.",
        ],
        "cross_arc_overlap_check": XARC,
        "cites": [
            "Fix_28_verify_off_data_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "cited_number_must_reproduce_from_cell",
            "verify_the_referent_atom_ids_mechanism_metric_regime",
            "feedback_experiment_design_gate_can_fail_real_baseline_difficulty_on_before_full_run",
            "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
            "construction_proof_is_not_capability_win_could_it_fail_informatively",
        ],
        "composes_with": COMPOSES,
        "composes_with_atom_ids": [PARENT_ATOM_ID, BUDGET_ENV_ATOM_ID],
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
    },
}

ledger = {
    "op": "cert_ruling",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": atom["cert_status"],
    "anchor": ANCHOR,
    "cell_commit": CELL_COMMIT,
    "supersedes_commit": None,
    "store_head_at_write": "unsynced_needs_orchestrator",
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": ATOMIZED_BY,
    "verdict": ("MEASURED_MECHANISM_closed_loop_surprise_prioritized_replay_COVERAGE_EFFICIENCY_lever_NOT_"
                "targeted_protection_weak_delta_E_0p055_structured_sign_positive_6of6_below_0p08_bar_ordering_"
                "closed_gt_uniform_gt_static_MEDIATED_by_distinct_coverage_74p7_66p3_61p0_E_tracks_coverage_"
                "r0p944_per_item_q_priority_invariant_0p711_0p713_0p688_frozen_priority_coverage_harmful_below_"
                "uniform_must_be_current_no_distributed_benefit_delta_Q_straddles_zero_confounds_0p000_replay_"
                "confined_to_touched_pool_reshuffle_not_add_capacity_CONSISTENT_WITH_but_not_proof_three_factor_"
                "plasticity_byte_reproduce_EXACT_0of36_design_gate_compliant_synthetic_toy_hypothesis_pending_real"),
    "cert_increment_delta": 1,
    "decision": (
        "MEASURED_MECHANISM (mechanism decomposition; Director led DEFLATED weak-lever, CONFIRMED). Byte-repro "
        "BIT-IDENTICAL (0/36 arm-digest mismatch; OMP=1 pinned). delta_E clos-unif weak: 0.055 structured (t=2.27 "
        "n=3 NOT sig, below 0.08 bar, hp=1/3 hf=1/3), 0.125 SF0.55; sign positive 6/6 seed-instances (sign test "
        "p=0.0156) -> MIDDLE not null not positive. CRUX MECHANISM: closed>uniform>static ordering fully mediated "
        "by distinct-coverage (n_distinct 74.7>66.3>61.0; E~0.72*coverage+0.018 r=0.944; per-item q priority-"
        "INVARIANT 0.711/0.713/0.688). Closed-loop wins via coverage-efficiency (rotates priority to newly-at-risk "
        "items -> more distinct touched); frozen static concentrates -> fewer distinct -> BELOW uniform (must be "
        "current). No distributed benefit (delta_Q straddles 0; confounds 0.000 on Q -> generalization defeated). "
        "Priority RESHUFFLES which items covered within fixed per-item capacity, does NOT add net capacity. "
        "Design-gate compliant (real baseline in-band, can-fail, difficulty-ON, one-variable). Counts toward CERT "
        "as a proven boundary. Composes with parent 35e1fbea9 (independent-content) + sibling 6f22af2de (budget "
        "envelope); neither superseded."),
    "framing_correction_vs_director": (
        "CONFIRMS Director's DEFLATED framing (weak-lever + mechanism, did NOT declare HARD_PASS on positive sign) "
        "-- correct, CREDITED, no upward inflation. Auditor SHARPENINGS Director should carry forward: (1) the "
        "mechanism is COVERAGE-MEDIATION, made precise -- closed>uniform>static is EXPLAINED by n_distinct_"
        "replayed (E~0.72*coverage r=0.944) with per-item protection PRIORITY-INVARIANT (q 0.711/0.713/0.688); "
        "closed-loop's advantage is coverage-efficiency (rotating priority), NOT targeted protection. (2) "
        "static-below-uniform is REAL and mechanistically a coverage effect in reverse (frozen weak priority "
        "concentrates on a fixed subset), robust 3/3 at SF0.75 but ONLY 2/3 at SF0.55 (honest downward vs an "
        "'always below' read). (3) HONEST GUARD ON THE THREE-FACTOR READ: the cell is CONSISTENT WITH but does "
        "NOT PROVE 'the fix is a differentially-weighting plasticity rule' -- it motivates it (per-item protection "
        "priority-invariant) but its own outcome is a weak coverage-positive, not the HARD_FAIL the pre-reg "
        "framed; stating the cell supports three-factor plasticity is a mild over-reach. (4) delta_E=0.055 is NOT "
        "a demonstrated lever magnitude (t=2.27 n=3 not sig, below the 0.08 bar) -- only the SIGN and the "
        "MECHANISM are robust. PROVENANCE STRENGTH: unlike the sibling budget-envelope, this cell IS bit-"
        "reproducible (OMP=1 pinned). Bank as a proven mechanism boundary."),
    "cross_arc_overlap_check": XARC,
    "net_cert_delta": ("+1 MM (proven boundary: closed-loop surprise-prioritized replay in a rank-1 Hebbian / "
                       "additive store is a COVERAGE-EFFICIENCY lever, not targeted protection -- per-item "
                       "protection priority-invariant, priority reshuffles which items are covered within fixed "
                       "capacity, frozen priority is coverage-harmful, no distributed benefit; weak positive sign "
                       "6/6 but below the 0.08 bar; consistent-with but not proof of three-factor plasticity; "
                       "synthetic-toy hypothesis pending real-data)."),
    "composes_with_atom_ids": [PARENT_ATOM_ID, BUDGET_ENV_ATOM_ID],
    "supersedes": None,
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
    "ts_iso": _iso,
    "ts": _ts,
    "atom_id": ATOM_ID,
}


def write_atomic_append(path, new_lines):
    if not path.exists():
        return (0, 0, False, "path does not exist: %s" % path)
    with open(path, "rb") as f:
        cur_bytes = f.read()
    cur_text = cur_bytes.decode("utf-8")
    pre_count = cur_text.count("\n")
    if cur_bytes and not cur_bytes.endswith(b"\n"):
        cur_bytes = cur_bytes + b"\n"
    parts = [cur_bytes]
    for line in new_lines:
        s = json.dumps(line, ensure_ascii=True)
        if "\n" in s:
            return (pre_count, pre_count, False, "JSON contains newline; not jsonl-safe")
        parts.append((s + "\n").encode("utf-8"))
    new_bytes = b"".join(parts)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "wb") as f:
        f.write(new_bytes); f.flush(); os.fsync(f.fileno())
    os.replace(tmp_path, path)
    with open(path, "rb") as f:
        verify_text = f.read().decode("utf-8")
    post_count = verify_text.count("\n")
    expected_post = pre_count + len(new_lines)
    if post_count != expected_post:
        return (pre_count, post_count, False, "line count mismatch: expected %d got %d" % (expected_post, post_count))
    tail = verify_text.rstrip("\n").split("\n")[-len(new_lines):]
    for i, tl in enumerate(tail):
        try:
            parsed = json.loads(tl)
        except Exception as e:
            return (pre_count, post_count, False, "tail-line %d JSON round-trip fail: %s" % (i, e))
        for key in ("id", "atom_id"):
            if key in new_lines[i] and parsed.get(key) != new_lines[i][key]:
                return (pre_count, post_count, False, "tail-line %d %s mismatch" % (i, key))
    return (pre_count, post_count, True, "OK")


def main():
    print("=== A5 atom-write: cls_prioritized_replay_closed_loop_surprise_v1 -> MM (coverage-mediated weak lever) (2026-07-18) ===")
    print("ts_iso =", _iso)
    assert atom["id"].isascii(), "non-ascii atom id"
    assert ledger["atom_id"] == atom["id"], "atom_id / id mismatch"

    existing = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                existing.add(json.loads(line).get("id"))
            except Exception:
                pass
    if atom["id"] in existing:
        print("ABORT: id already in store"); sys.exit(1)
    for pid, lbl in ((PARENT_ATOM_ID, "independent-content parent"), (BUDGET_ENV_ATOM_ID, "budget-envelope sibling")):
        if pid not in existing:
            print("WARN: composed atom id not found (%s) -- proceeding, flag for review" % lbl)
        else:
            print("referent OK: %s present in store" % lbl)
    print("id-uniqueness OK (1 new, not pre-existing)")

    print("Writing 1 atom to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, [atom])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 1 row to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, [ledger])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    n_ok = 0
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            json.loads(line); n_ok += 1
    present = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                present.add(json.loads(line).get("id"))
            except Exception:
                pass
    assert atom["id"] in present, "post-write integrity: new id missing"
    print("integrity: math/atoms.jsonl fully parses (%d lines), new id present." % n_ok)
    print()
    print("=== A5 WRITE COMPLETE (LOCAL ONLY; needs_orchestrator_store_sync=True) ===")
    print("ATOM_ID:", atom["id"])


if __name__ == "__main__":
    main()
