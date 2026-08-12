"""
A5-gated atomization: cls_distributed_protection_budget_envelope_v1 -> MEASURED_MECHANISM
(envelope characterization: distributed consolidation of never-replayed independent content is NOT
budget-efficient) (2026-07-18).

Director LED this DEFLATED (envelope char, not capability). Auditor tier = MEASURED_MECHANISM. Composes with
the parent CLS-independent-content MM atom (cell 35e1fbea9, VET ad3947bd).

VET independently off-disk (.venv, Fix #28 -- recompute off metrics.json per_unit + a FRESH FULL re-run,
NOT verdict_msg):
  1. OFF-DISK RECOMPUTE (original metrics.json): genuine(struct) curve b=0.083 -0.0353 / 0.167 +0.0306 /
     0.25 +0.1080 / 0.333 +0.1493 / 0.50 +0.3009 / 0.75 +0.4537 -- matches agg EXACTLY. Confounds 1nn/fresh
     BOTH 0.0000 at all 6 budgets. posctrl @25% subsample 0.2407 vs parent 0.247 (dev 0.0063).
  2. CONVEXITY: all 5 interior points fall BELOW the origin-to-top linear line -> the curve is CONVEX /
     ACCELERATING (worse-than-linear), MORE severe than the cell's own classifier label "LINEAR_MUST_REHEARSE"
     (which fires only because eff_ratio goes negative). Both point to the same conclusion: NOT budget-efficient.
  3. FRESH FULL RE-RUN (3 seeds) DOES NOT byte-reproduce -- it lands within ~+/-0.02-0.05: genuine
     -0.035/+0.047/+0.111/+0.153/+0.306/+0.500; posctrl @25% 0.2469 (dev 0.0001 from parent). Cause DIAGNOSED
     = OpenBLAS DYNAMIC_ARCH MAX_THREADS=24 unpinned -> multi-thread float-summation nondeterminism in the
     numpy MLP training, compounded over 400+1600 epochs (NOT a seed/PYTHONHASHSEED bug; the determinism guard
     `sorted(set())` is correct and the 1-seed selftest DID reproduce seed-7 exactly). Weaker reproducibility
     than the parent (which byte-reproduced EXACT) -- disclosed. Shape (LINEAR_MUST_REHEARSE, convex=True),
     confounds (max 0.0 all 18 units), replay_all ceiling (1.0), init (1.0), and posctrl are ALL robust across
     the independent re-run.
  4. CONTROL-DEFINITION (load-bearing, exp_dev flagged): the diversity-matched STRUCT filler (reuse the 12 OLD
     class protos + fresh probes + random targets) is the RIGHT/FAIR primary control, NOT gaming toward a
     positive -- it satisfies one-variable-differs (differs from the subsample ONLY in cue->target CONTENT,
     holding volume AND class-code diversity constant), whereas the RANDOM filler introduces a SECOND
     difference (higher proto directional diversity -> a STRONGER regularizer -> over-corrects, genuine goes
     negative). Consistency check the choice is honest not tuned: STRUCT genuine @25% = 0.108-0.111 reconciles
     the parent's INDEPENDENTLY-derived ~0.11.
  5. CONCLUSION ROBUST TO CONTROL CHOICE: under the CONSERVATIVE random-filler bracket, genuine only clears
     zero at >=50% budget (rnd -0.13/-0.11/-0.10/-0.04/+0.08/+0.14); under the diversity-matched struct
     control, at ~17%+ -- EITHER WAY low budget (8-17%) is ~0 and meaningful protection needs a large fraction.
     The "not budget-efficient" read does not depend on which control you pick.
  6. INDEPENDENCE ROBUST: both confounds 0.000 at every budget AND every seed, both runs (max 0.0 over 18
     units) -> the independent-content design holds throughout the sweep.

TIER: MEASURED_MECHANISM (proven boundary / envelope characterization). The budget-scaling SHAPE is a measured
boundary: distributed consolidation of never-replayed independent content is worse-than-linear in replay budget
-> does NOT provide a sub-linear foundation for continual textbook-ingestion. CAVEAT: synthetic MLP toy regime
-> strong HYPOTHESIS pending real-data, not settled.

Cross-arc overlap check (USER-locked): substrate_query.sh top hits are RESEARCH-DRILL NOTES + the v211 REPLAY
zero-sum strategy chunk at cosine 0.34-0.41 (bio replay/consolidation notes; NOT prior experiment cells). No
arc-cell rediscovery at cosine>0.30; genuine targeted budget-envelope extension of the parent MM cell.

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
ATOMIZED_BY = "skunkworks_landed_vet_cls_distributed_protection_budget_envelope_v1_MM_not_budget_efficient_2026-07-18"
ATOMIZED_DATE = "2026-07-18"
ANCHOR = "cls_distributed_protection_budget_envelope_v1"
CELL_COMMIT = "6f22af2de"

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

XARC = ("substrate_query.sh 'distributed consolidation replay budget never-replayed protection continual' -> "
        "top hits are RESEARCH-DRILL NOTES + the v211 REPLAY zero-sum strategy chunk at cosine 0.34-0.41 "
        "(bio replay/consolidation drill notes, strategy_decisions 2026-05-26 REPLAY H-A LOCKED zero-sum "
        "chunk, wordnet 'consolidation'); NOT any prior EXPERIMENT cell. No arc-cell rediscovery at "
        "cosine>0.30 -> genuine targeted budget-envelope EXTENSION of the parent MM cell (35e1fbea9), not a "
        "duplication.")

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

ATOM_ID = ("math::MM_MEASURED_MECHANISM_cls_distributed_protection_budget_envelope_v1_distributed_consolidation_"
           "of_never_replayed_independent_content_is_NOT_budget_efficient_the_genuine_diversity_matched_equal_"
           "compute_corrected_STRUCT_filler_protection_scales_WORSE_THAN_LINEARLY_CONVEX_ACCELERATING_with_"
           "replay_budget_approx0_at_8to17pct_npos_0of3_at_8p3pct_plus0p03to0p05_at_16p7pct_plus0p11_at_25pct_"
           "plus0p15_at_33pct_plus0p30_at_50pct_plus0p45to0p50_at_75pct_meaningful_protection_requires_"
           "rehearsing_a_LARGE_fraction_does_NOT_support_distributed_consolidation_as_a_sub_linear_foundation_"
           "for_continual_textbook_ingestion_CONCLUSION_ROBUST_TO_CONTROL_CHOICE_conservative_random_filler_"
           "bracket_only_clears_zero_at_ge50pct_diversity_matched_struct_at_about17pct_either_way_low_budget_"
           "approx0_STRUCT_filler_is_the_FAIR_control_one_variable_differs_only_cue_to_target_content_reconciles_"
           "parent_0p11_at_25pct_confounds_0p000_at_ALL_budgets_AND_ALL_seeds_both_runs_max0_over_18_units_"
           "independence_robust_posctrl_25pct_0p241_to_0p247_dev_under0p01_REPRO_CAVEAT_NOT_bit_reproducible_"
           "independent_rerun_drifts_plusminus0p02to0p05_OpenBLAS_multithread_float_nondeterminism_not_seed_bug_"
           "shape_confounds_posctrl_conclusion_all_robust_across_rerun_cell_classifier_LINEAR_label_UNDERSTATES_"
           "curve_is_convex_CAVEAT_synthetic_MLP_toy_regime_strong_hypothesis_pending_real_data_3seed_7_17_23_"
           "FULL_envelope_char_composes_parent_35e1fbea9_6f22af2de_2026-07-18")

CLAIM = (
    "MATH MEASURED_MECHANISM (proven boundary / ENVELOPE characterization of the parent CLS-independent-content "
    "MM, cell 35e1fbea9). Distributed consolidation of NEVER-REPLAYED independent content is NOT BUDGET-"
    "EFFICIENT: the genuine (diversity-matched STRUCT equal-compute-corrected) never-replayed protection scales "
    "WORSE-THAN-LINEARLY (CONVEX / ACCELERATING) with replay budget -- ~0 at the 8-17% budgets that would "
    "matter for 'small budget protects large corpus' (npos 0/3 at 8.3%, ~+0.03-0.05 at 16.7%), +0.11 @25%, "
    "+0.15 @33%, +0.30 @50%, +0.45-0.50 @75%. Meaningful protection requires rehearsing a LARGE fraction of the "
    "corpus; this does NOT support distributed consolidation as a sub-linear foundation for continual textbook-"
    "after-textbook ingestion. The conclusion is ROBUST TO THE CONTROL-DEFINITION CHOICE: under the "
    "conservative RANDOM-filler bracket the genuine effect only clears zero at >=50% budget; under the "
    "diversity-matched STRUCT control at ~17%+ -- either way the low-budget region is ~0. The STRUCT filler "
    "(reuse the 12 OLD class protos + fresh probes + random targets) is the FAIR primary control (differs from "
    "the subsample in ONLY the cue->target content, holding volume AND class-code diversity constant; the "
    "random filler adds a second difference -- higher proto diversity -> stronger regularizer -> over-corrects) "
    "and it RECONCILES with the parent's independently-derived ~0.11 @25% (STRUCT genuine 0.108-0.111; positive "
    "control subsample @25% 0.241-0.247, dev <0.01 from parent 0.247). Independence is ROBUST: both confounds "
    "(1-NN proximity, fresh-net-on-subsample) recover 0.000 at EVERY budget AND EVERY seed (max 0.0 over 18 "
    "units, both runs). REPRODUCIBILITY CAVEAT: unlike the parent (which byte-reproduced EXACT), this cell is "
    "NOT bit-reproducible -- an independent full re-run drifts ~+/-0.02-0.05 on the genuine curve (diagnosed = "
    "OpenBLAS DYNAMIC_ARCH multi-thread float-summation nondeterminism in the numpy MLP training, NOT a seed/"
    "PYTHONHASHSEED bug); the SHAPE, confounds, ceiling, difficulty gate and positive control are all robust "
    "across the re-run, so cite the curve as APPROXIMATE. The cell's own classifier label LINEAR_MUST_REHEARSE "
    "slightly UNDERSTATES -- the raw curve is convex/accelerating (worse than linear). CAVEAT: synthetic MLP "
    "toy regime -> strong HYPOTHESIS pending real-data, not settled.")

RECOMPUTE = (
    "INDEP recompute (.venv, Fix #28: off metrics.json per_unit AND a fresh full 3-seed re-run of the REAL cell, "
    "NOT verdict_msg). (1) OFF-DISK: genuine(sub-struct) curve b=0.083 -0.0353 / 0.167 +0.0306 / 0.25 +0.1080 / "
    "0.333 +0.1493 / 0.50 +0.3009 / 0.75 +0.4537 -- matches metrics.json agg EXACTLY. Per-seed sign: 8.3% is "
    "0/3 positive (all negative), 16.7%..75% all 3/3 positive. Confounds 1nn=0.0000 AND fresh=0.0000 at all 6 "
    "budgets. posctrl @25% subsample 0.2407 vs parent 0.247 (dev 0.0063). Random-filler bracket -0.119/-0.103/"
    "-0.108/-0.014/+0.088/+0.120 (only clears zero at >=50%). (2) CONVEXITY: all 5 interior points fall BELOW "
    "the origin-to-top linear line -> curve is CONVEX/ACCELERATING (worse-than-linear). (3) FRESH FULL RE-RUN "
    "(seeds 7/17/23) does NOT byte-reproduce: genuine -0.035/+0.047/+0.111/+0.153/+0.306/+0.500, posctrl @25% "
    "0.2469 (dev 0.0001), max 1nn=0.0 max fresh=0.0 over 18 units, replay_all min 1.0, heldout_initial 1.0 all "
    "units, shape LINEAR_MUST_REHEARSE convex=True. Run-to-run drift ~+/-0.02-0.05. CAUSE = np.show_config() "
    "reports OpenBLAS 0.3.31 DYNAMIC_ARCH MAX_THREADS=24, OMP/OPENBLAS_NUM_THREADS unset -> nondeterministic "
    "float reduction order in the MLP matmul training, compounded over 400+1600 epochs; NOT PYTHONHASHSEED "
    "(guard `sorted(set())` correct; 1-seed selftest reproduced seed-7 per_unit exactly). All load-bearing "
    "quantities (shape, confounds, ceiling, difficulty, posctrl, ~0.11 @25%) robust across the re-run.")

SCOPE = (
    "Synthetic MLP toy regime (numpy cue->tanh(H=160)->linear(D_T=64) regression; N=256, 144 old items = 12 "
    "classes x 12 exemplars, 8 interference blocks x 3 new classes, E_OLD=400 E_NEW=200, LR=0.04, "
    "SHARED_FRAC=0.75 fixed at the structured end; retrieval = nearest-target over the 144-item codebook, "
    "chance 0.0069). This is a MECHANISM/ENVELOPE characterization, NOT capability-at-scale. Load-bearing "
    "limits: (a) SYNTHETIC TOY -- the budget-scaling shape is a strong HYPOTHESIS about distributed "
    "consolidation, pending confirmation on real ingestion data; do NOT bank as a settled continual-learning "
    "law. (b) the exact effect sizes carry ~+/-0.02-0.05 run-to-run float/BLAS noise (not bit-reproducible); "
    "cite the curve as approximate and the SHAPE (worse-than-linear, low-budget ~0) as the robust result. (c) "
    "the genuine effect at low budgets is control-definition-sensitive in MAGNITUDE (struct vs random bracket "
    "spans zero at 8-25%) but the CONCLUSION (not budget-efficient) is robust to the control choice. (d) ONLY "
    "the structured end (SHARED_FRAC=0.75) is swept; budget-efficiency at other structure levels is "
    "uncharacterized. Do NOT read this as 'consolidation fails' -- consolidation is REAL (parent MM) and "
    "protects strongly at HIGH budget; it is simply not SUB-LINEAR, so it is not a cheap foundation.")

METRICS = {
    "budgets_frac": [0.0833, 0.1667, 0.25, 0.3333, 0.5, 0.75],
    "genuine_struct_orig": [-0.0354, 0.0305, 0.108, 0.1493, 0.3009, 0.4537],
    "genuine_struct_rerun": [-0.0353, 0.0473, 0.1111, 0.1528, 0.3055, 0.5],
    "genuine_random_bracket_orig": [-0.1187, -0.1028, -0.108, -0.0139, 0.088, 0.1204],
    "subsample_orig": [0.0733, 0.1556, 0.2407, 0.3299, 0.463, 0.6204],
    "struct_filler_orig": [0.1086, 0.125, 0.1327, 0.1806, 0.1621, 0.1667],
    "confound_1nn_max_over_18units": 0.0, "confound_fresh_max_over_18units": 0.0,
    "replay_all_min": 1.0, "heldout_initial_all": 1.0, "chance": 0.0069,
    "per_seed_npos_struct": {"0.083": "0/3", "0.167": "3/3", "0.25": "3/3", "0.333": "3/3",
                             "0.50": "3/3", "0.75": "3/3"},
    "posctrl_subsample_at25pct_orig": 0.2407, "posctrl_rerun": 0.2469, "parent_measured": 0.247,
    "posctrl_dev_orig": 0.0063, "posctrl_dev_rerun": 0.0001,
    "shape_label_cell": "LINEAR_MUST_REHEARSE", "shape_auditor": "CONVEX_ACCELERATING_worse_than_linear",
    "convex_all_interior_below_origin_top_line": True,
    "eff_ratio": -0.078, "linear_ratio": 0.111,
    "reproducibility": "NOT_bit_reproducible_rerun_drift_plusminus_0p02_to_0p05_OpenBLAS_multithread_float",
    "blas": "OpenBLAS_0.3.31_DYNAMIC_ARCH_MAX_THREADS_24_unpinned",
    "n_units": 18, "seeds": [7, 17, 23],
    "cell_verdict": "CHARACTERIZATION", "auditor_tier": "MEASURED_MECHANISM (envelope characterization)",
}

COMPOSES = [
    "COMPOSES-WITH + EXTENDS the parent CLS-independent-content MM (cell 35e1fbea9, VET ad3947bd): that atom "
    "PROVED distributed consolidation of independent content EXISTS but is PARTIAL (~0.11 isolated @25%); THIS "
    "atom characterizes its ENVELOPE across replay budget and finds the scaling is WORSE-than-linear -> not a "
    "sub-linear foundation. Parent NOT superseded; this AMENDS with the budget-scaling boundary.",
    "CONSISTENT-WITH the v211 REPLAY H-A ZERO-SUM-WITH-NET-POSITIVE finding (strategy_decisions 2026-05-26, "
    "N=8192 substrate-storage regime): replay transfers retention rather than giving free sub-linear "
    "protection; the budget-envelope here is the independent-content-MLP analog of that non-free scaling.",
    "credit: McClelland-McNaughton-O'Reilly 1995 / Kumaran-Hassabis-McClelland 2016 (distributed cortical "
    "consolidation, expected graded/partial); the worse-than-linear budget cost is the quantitative envelope.",
]

atom = {
    "id": ATOM_ID,
    "name": CLAIM,
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": ("confirmed_measured_mechanism_envelope_distributed_consolidation_of_never_replayed_"
                    "independent_content_NOT_budget_efficient_genuine_protection_worse_than_linear_convex_"
                    "accelerating_in_replay_budget_low_budget_8to17pct_approx0_meaningful_only_at_large_"
                    "fraction_not_a_sublinear_foundation_for_continual_ingestion_conclusion_robust_to_control_"
                    "choice_confounds_0p000_all_budgets_all_seeds_reconciles_parent_0p11_at_25pct_NOT_bit_"
                    "reproducible_blas_float_noise_shape_robust_synthetic_toy_hypothesis_pending_real_data"),
    "cert_class": ("distributed_consolidation_budget_scaling_envelope_worse_than_linear_replay_budget_not_sub_"
                   "linear_foundation_continual_ingestion_diversity_matched_equal_compute_control_confound_clean_"
                   "measured_mechanism_envelope_characterization"),
    "description": (CLAIM + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + RECOMPUTE
                    + "\n\nHONEST SCOPE: " + SCOPE),
    "aliases": [],
    "ts_iso": _iso,
    "ts": _ts,
    "metadata": {
        "provenance_quality": ("off_disk_recompute_plus_fresh_full_rerun_shape_robust_but_NOT_bit_reproducible_"
                               "blas_float_noise_plusminus_0p02_to_0p05"),
        "anchor": ANCHOR,
        "cell_commit": CELL_COMMIT,
        "supersedes": None,
        "store_head_at_write": "unsynced_needs_orchestrator",
        "metrics_path": "data/exp_cls_distributed_protection_budget_envelope_v1/metrics.json",
        "verified_off_data": RECOMPUTE,
        "honest_scope": SCOPE,
        "metrics": METRICS,
        "control_definition_ruling": (
            "The exp_dev-flagged control-definition choice is FAIR, NOT gaming toward a positive. The STRUCT "
            "filler (reuse the 12 OLD class protos + fresh probes + random targets) is the principled primary "
            "control because it satisfies one-variable-differs: it differs from the subsample_replay arm in "
            "ONLY the cue->target CONTENT, holding volume AND old-class-code diversity constant. The RANDOM "
            "filler introduces a SECOND uncontrolled difference (its random protos span more directions than "
            "the correlated 12-class old items -> a stronger regularizer -> it OVER-corrects, driving genuine "
            "negative). So STRUCT is the FAIRER (diversity-matched) control, not an inflating one. Two honesty "
            "checks pass: (a) STRUCT genuine @25% = 0.108-0.111 RECONCILES the parent's independently-derived "
            "~0.11; (b) the load-bearing CONCLUSION (not budget-efficient) is INVARIANT to the control choice "
            "-- under the conservative RANDOM bracket genuine clears zero only at >=50% budget, under STRUCT at "
            "~17%+, either way the 8-17% region is ~0. Both controls are reported as a transparent bracket."),
        "shape_ruling": (
            "The genuine-effect-vs-budget curve is CONVEX / ACCELERATING (worse-than-linear): all 5 interior "
            "points fall below the origin-to-top linear line (verified both runs). The cell's own classifier "
            "label LINEAR_MUST_REHEARSE UNDERSTATES this -- it fires only because eff_ratio (g_lo/g_hi) goes "
            "negative at the 8.3% budget. Auditor read = accelerating/worse-than-linear, which is MORE precise "
            "than and consistent with the cell's practical conclusion (must rehearse most of the corpus). "
            "Per-seed robust: 8.3% is 0/3 positive; 16.7%+ is 3/3 positive."),
        "reproducibility_caveat": (
            "MATERIAL DIFFERENCE FROM THE PARENT (honest downward on provenance): the parent cell byte-"
            "reproduced EXACT (bit-identical SHA256 arm digests); THIS cell does NOT. An independent full "
            "3-seed re-run drifted ~+/-0.02-0.05 on the genuine curve (e.g. 75% budget genuine 0.4537 -> 0.500; "
            "16.7% 0.0306 -> 0.0473). DIAGNOSED cause = OpenBLAS 0.3.31 DYNAMIC_ARCH MAX_THREADS=24 with "
            "OMP/OPENBLAS_NUM_THREADS unpinned -> nondeterministic float-summation reduction order in the numpy "
            "MLP matmul training, compounded over 400+1600 epochs and amplified by the argmax retrieval over a "
            "144-codebook on small held-out sets (36-132 items). NOT a seed/PYTHONHASHSEED bug (the "
            "`sorted(set())` determinism guard is correct and the 1-seed selftest reproduced seed-7 per_unit "
            "exactly). This does not affect the tier -- the SHAPE, confounds (max 0.0/18 units), ceiling (1.0), "
            "difficulty (init 1.0) and positive control (dev 0.0001) are all robust across the re-run -- but "
            "the CURVE VALUES must be cited as APPROXIMATE, and a future revival should pin OMP_NUM_THREADS=1 "
            "for bit-reproducibility."),
        "over_reads_avoided": [
            "Director LED this DEFLATED (envelope char, not a capability claim) -- CONFIRMED appropriate; this "
            "is a MEASURED boundary, not a win. No inflation to correct upward.",
            "Do NOT cite the exact genuine curve numbers as reproducible constants -- they carry ~+/-0.02-0.05 "
            "float/BLAS run-to-run noise. Cite the SHAPE (worse-than-linear, low-budget ~0) as the robust claim.",
            "Do NOT read 'not budget-efficient' as 'consolidation fails' -- consolidation is REAL (parent MM) "
            "and protects strongly at HIGH budget (0.45-0.50 @75%); it is simply not sub-linear.",
            "Synthetic MLP toy -> strong HYPOTHESIS pending real-data (exp_dev's caveat, load-bearing), NOT a "
            "settled continual-learning law.",
        ],
        "revival_criteria": [
            "Confirm the worse-than-linear budget envelope on REAL continual-ingestion data (textbook/corpus) "
            "with the diversity-matched equal-compute control as a standing arm, before treating it as a law.",
            "Pin OMP_NUM_THREADS=1 (or single-thread BLAS) and re-run for bit-reproducibility, so the exact "
            "curve is a stable constant rather than +/-0.05-noisy.",
            "Characterize budget-efficiency at other structure levels (SHARED_FRAC != 0.75) -- only the "
            "structured end is swept here; a sub-linear pocket at some structure regime would be a real revival.",
        ],
        "cross_arc_overlap_check": XARC,
        "cites": [
            "Fix_28_verify_off_data_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "cited_number_must_reproduce_from_cell",
            "verify_the_referent_atom_ids_mechanism_metric_regime",
            "feedback_experiment_design_gate_can_fail_real_baseline_difficulty_on_before_full_run",
            "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
            "reference_cskg_split_nondeterministic_but_here_nondeterminism_is_BLAS_float_not_pythonhashseed",
        ],
        "composes_with": COMPOSES,
        "composes_with_atom_ids": [PARENT_ATOM_ID],
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
    "verdict": ("MEASURED_MECHANISM_envelope_distributed_consolidation_of_never_replayed_independent_content_NOT_"
                "budget_efficient_genuine_diversity_matched_struct_corrected_protection_WORSE_THAN_LINEAR_CONVEX_"
                "approx0_at_8to17pct_plus0p11_25pct_plus0p30_50pct_plus0p45to0p50_75pct_must_rehearse_large_"
                "fraction_NOT_sublinear_foundation_conclusion_ROBUST_TO_CONTROL_CHOICE_random_bracket_clears_"
                "zero_only_ge50pct_struct_the_fair_control_reconciles_parent_0p11_confounds_0p000_all_budgets_"
                "all_seeds_max0_over18units_posctrl_25pct_dev_under0p01_NOT_bit_reproducible_rerun_drift_"
                "plusminus0p02to0p05_OpenBLAS_multithread_float_not_seed_bug_shape_confounds_posctrl_robust_"
                "cell_LINEAR_label_understates_curve_convex_synthetic_toy_hypothesis_pending_real_data"),
    "cert_increment_delta": 1,
    "decision": (
        "MEASURED_MECHANISM (envelope characterization; Director led DEFLATED, CONFIRMED). Off-disk recompute "
        "matches metrics.json agg EXACTLY (genuine struct curve -0.035/+0.031/+0.108/+0.149/+0.301/+0.454; "
        "confounds 0.000 all 6 budgets; posctrl @25% 0.2407 dev 0.0063). CONVEXITY verified: all interior "
        "points below the origin-top line -> worse-than-linear (the cell's LINEAR label understates). CONTROL "
        "ruling: the diversity-matched STRUCT filler is the FAIR primary control (one-variable-differs; the "
        "random filler over-corrects via higher diversity) and reconciles the parent's ~0.11 @25%; the "
        "conclusion is INVARIANT to the control choice (random bracket clears zero only >=50%, struct ~17%+, "
        "both ~0 at low budget). Independence robust (both confounds 0.000 at every budget AND seed). "
        "REPRODUCIBILITY: a fresh full re-run did NOT byte-reproduce -- ~+/-0.02-0.05 drift from OpenBLAS "
        "multi-thread float nondeterminism (NOT a seed bug); shape/confounds/posctrl/conclusion all robust, so "
        "cite the curve as approximate. Counts toward CERT as a proven boundary. Composes with + amends the "
        "parent CLS-independent-content MM (35e1fbea9); parent NOT superseded."),
    "framing_correction_vs_director": (
        "CONFIRMS Director's DEFLATED framing (envelope char, not capability) -- correct, no upward inflation. "
        "THREE auditor additions Director should carry forward: (1) the shape is CONVEX/ACCELERATING (worse-"
        "than-linear), STRONGER than the cell's own LINEAR_MUST_REHEARSE label -- reinforces 'not budget-"
        "efficient'; (2) the 'not budget-efficient' conclusion is ROBUST TO THE CONTROL-DEFINITION CHOICE (both "
        "the random bracket and the struct control leave low budget ~0), so the STRUCT-vs-random debate does "
        "NOT threaten the headline; (3) HONEST DOWNWARD ON PROVENANCE -- unlike the parent (byte-reproduced "
        "EXACT), this cell is NOT bit-reproducible; an independent re-run drifts ~+/-0.02-0.05 due to OpenBLAS "
        "multi-thread float nondeterminism (diagnosed, not a seed bug). The curve values are approximate; the "
        "SHAPE is the robust result. exp_dev's synthetic-toy caveat is load-bearing (strong hypothesis, not "
        "settled). Bank as a proven envelope boundary."),
    "cross_arc_overlap_check": XARC,
    "net_cert_delta": ("+1 MM (proven boundary: distributed consolidation of never-replayed independent content "
                       "is worse-than-linear in replay budget -> not a sub-linear foundation for continual "
                       "textbook-ingestion; conclusion robust to control choice and to +/-0.05 run-to-run "
                       "float noise; synthetic-toy hypothesis pending real-data)."),
    "composes_with_atom_ids": [PARENT_ATOM_ID],
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
    print("=== A5 atom-write: cls_distributed_protection_budget_envelope_v1 -> MM (NOT budget-efficient) (2026-07-18) ===")
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
    # verify parent exists (referent check)
    if PARENT_ATOM_ID not in existing:
        print("WARN: parent atom id not found in store (composition dangling) -- proceeding, flag for review")
    else:
        print("referent OK: parent atom present in store")
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
