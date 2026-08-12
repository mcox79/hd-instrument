"""
A5-gated atomization -- Skunkworks landed-VET / ship-gate RE-VERDICT 2026-07-05. AUDIT-ONLY.

TASK: re-verdict the ALREADY-LANDED graded-code encoder results (v11/v12) against the PERCEPTION
SHIP GATE (ret_agree10>=0.30 AND cosine_to_gold>=0.80 AND composed_roundtrip@J10>=0.95), to decide
whether the perception retrieval-agreement gap (seed_7 ship metric MIDDLE_BAND: ret 0.1837 missed 0.30)
is genuinely SOLVED by graded GSBC codes. Cheap re-verdict, no new dispatch; independent off-disk recompute.

TIER: MEASURED_MECHANISM (proven-bound). Retrieval-gap is SOLVED (chain-grade-strength sub-claim);
perception EFFECTIVELY clears the joint ship gate; the ONE honest reservation is that no strict
single-run carry-through co-measures all three gates on the EXACT deployed graded code with a J10 point.
That confirming FULL is a cheap formality (high prior of PASS), NOT an open research question.

OFF-DISK RECOMPUTE (six metrics.json read + arithmetic reproduced via .venv):
  BASELINE seed_7 (deployed=SIGN INBATCH_BLOCK, the MIDDLE_BAND): cosine 0.8611 (pass), composed@J10
    0.9833 (pass), ret_agree10 0.1837 (MISS 0.30). Only the ret axis failed. Cause = hard-STE sign
    quantization: CONFIRMED off-disk (all hard-sign codes sit ret 0.18-0.22: seed_7 0.1837;
    v11 SIGN_BLOCK 0.2117/0.2177).
  GRADED FIX (v11 GSBC_FULL, graded block-topm=3, FULL recipe, 2 seeds):
    ret 0.3986/0.3968 (BOTH clear 0.30; +0.1869/+0.1791 lift vs SIGN 0.2117/0.2177);
    cosine(hi80) 0.8338/0.8300 (BOTH clear 0.80); keyed@J5 1.000 both, shuffled 0.000.
    cross-seed cv: ret 0.0023, cos 0.0023 (tight).
  DEPTH (composed@J10): J-sweep was {1,2,5,8,16,32,64} -> NO exact J10 point anywhere.
    v11 gated keyed@J5 ONLY. J10 is bracketed by J8,J16. keyed roundtrip acc is monotone-NONincreasing
    in J (more bound items = more crosstalk) => composed@J10 >= composed@J16.
    Same-geometry graded block code (v12 GSBC_RKD_BLOCK, block-topm=3 == GSBC_FULL geometry, rkd recipe):
      seed7 J8=0.9833 J16=0.9833 => J10 >= 0.9833 >= 0.95  TRUE
      seed13 J8=1.000 J16=1.000 => J10 >= 1.000 >= 0.95    TRUE
    Full-recipe does NOT degrade keyed margin (GSBC_FULL J5 snr 0.0575 ~ GSBC_RKD 0.0580), so
    GSBC_FULL@J10 tracks block@J10 -> composed@J10>=0.95 EFFECTIVELY MET for the graded block family.

THE KEY GAP the task asked to be rigorous about (does v12 EXPAND2X J8=J16=1.0 close the J10-for-
GSBC_FULL gap?): NO. GSBC_EXPAND2X is a DIFFERENT CODE -- code_mode=gwta (global top-K), out_dim=8192,
kb64, recipe=rkd_only -- vs GSBC_FULL's code_mode=block (per-block top-m=3), out_dim=4096, recipe=full.
Different sha256, different geometry, different width, different recipe, different depth envelope.
EXPAND2X's J8=J16=1.0 depth does NOT transfer to certify GSBC_FULL's J10. The Director's suspicion is
CORRECT. The proper J10 evidence for the block family comes from the SAME-geometry GSBC_RKD_BLOCK arm
(J10 >= J16 >= 0.9833, 2 seeds, monotone lower bound), NOT from EXPAND2X.

VERDICT: perception PASSES the joint ship gate with graded codes (ret>=0.30 AND cosine>=0.80 both direct
on GSBC_FULL 2 seeds; composed@J10>=0.95 by sound monotone bracketing on same-geometry graded block code
2 seeds). The retrieval-gap that produced the seed_7 MIDDLE_BAND is SOLVED. RESERVATION (why MM not a
clean chain-grade PASS): no STRICT single carry-through run co-measures ret+cosine+keyed@J10 on ONE
deployed graded code with an EXACT J10 point. A confirming FULL is warranted but CHEAP: re-run the
deployed graded block code (GSBC_FULL or the GSBC_RKD_BLOCK winner) through Step2 sparse-encode + Step3
ship metric with the keyed J-sweep including J=10 co-measured. High prior of PASS; not a research risk.

CROSS-ARC OVERLAP CHECK (USER-locked 2026-07-01): substrate_query 'graded GSBC sparse block code
retrieval agreement encoder ship gate perception' -> top cosine 0.2842 (< 0.30), hits = REALM/Atlas
two-tower retrieval notes + generic 'sparse block codes' note; NOT this GSBC ship-gate chain. KB blind to
this chain (as the Director flagged). NOVEL synthesis; no rediscovery.

COMPOSES WITH (does NOT supersede): the two prior 2026-07-04 encoder-lever MM atoms (v11 GSBC_GRADED_
SINGLE_CODE; v12 GSBC_EXPAND2X). Those atomized the encoder retrieval LEVERS (ret lifts + depth
envelopes); this atom is the PERCEPTION SHIP-GATE re-verdict connecting them to the seed_7 MIDDLE_BAND
ship metric -- a distinct claim. NOTE: v12's prior 'seed13 NOT LANDED, paired confirmation REQUIRED'
reservation is now SATISFIED off-disk -- v12 seed13 landed (EXPAND2X 0.6802, GWTA 0.6224, BLOCK 0.4664;
depth J8=J16=1.0), consistent with seed7.

NET CERT DELTA (this batch): MM +1, CG 0, HF 0. No DEMOTE.
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))
SESSION_TAG = "2026-07-05_perception_shipgate_reverdict_graded_GSBC_codes_MEASURED_MECHANISM"

PRIOR_V11_ID = "math::MM_STANDARD_v1_encoder_GSBC_GRADED_SINGLE_CODE_clears_0p35_retrieval_JOINTLY_with_NATIVE_calibration_and_rank_fidelity_at_2p34pct_active_ONE_code_2seed_FULL178k_PAIRED_GSBC_RKD_rkd_only_kb32_blk128_m3_96of4096_active_final_step_block_readout_ret_agree10_0p4447_0p4664_cv2p4pct_BEATS_sign_argmax_K128_ortho_ceiling_0p4295_by_pos0p015_pos0p037_hi80_cos_0p842_0p838_calib_err_0p0024_0p0009_NATIVE_no_isotonic_spearman_0p973_0p973_keyed_J5_gsbc_circconv_1p000_shuffled_0p000_bounded_5item_integrity_RETAINED_format_inherent_random_block_also_1p000_snr_eroded_0p35_to_0p072_under_retrieval_training_control_SIGN_BLOCK_reproduces_v3e_0p2117_0p2177_GSBC_FULL_annealed_STE_plus_ListNet_plus_anchor_UNDERPERFORMS_0p3986_0p3968_BELOW_sign_ceiling_confirms_lever_B_dead_headroom_remains_vs_zero_training_format_ceiling_0p62_capacity_NOT_bottleneck_training_is_the_gap_2026-07-04"
PRIOR_V12_ID = "math::MM_STANDARD_v1_encoder_GSBC_EXPAND2X_graded_global_topk_plus_2x_FLYHASH_EXPANSION_is_the_WINNING_SINGLE_CODE_encoder_candidate_TRAINED_confirm_of_the_zero_training_dual_readout_de_risk_prediction_seed7_FULL_M177899_gwta_out8192_kb64_global_top192_2p34pct_active_192of8192_final_step_deployed_code_ret_agree10_0p6027_lift_pos0p1581_vs_GSBC_BLOCK_0p4447_and_pos0p0398_vs_GSBC_GWTA_0p5629_JOINT_gate_ALL_FOUR_NATIVE_clean_no_isotonic_keyed_J5_gsbc_circconv_1p000_ge0p95_hi80_cos_0p8449_no_collapse_calib_err_0p0009_in_band_spearman_0p9846_shuffled_key_0p000_random_key_1p000_harness_sane_random_semantic_ret_0p0005_depth_envelope_keyed_ge0p95_through_J32_J32_0p9667_J64_0p7833_so_J32_PROVEN_algebra_depth_sufficient_for_operating_band_J5_10_where_keyed_1p000_Gate_D_BLOCK_arm_ret_0p4446767847_reproduces_v11_seed7_EXACT_deterministic_harness_confirmed_zero_training_probe_predicted_EXPAND2x_8192_graded_0p6505_now_TRAINED_0p6027_transfer_to_trained_VALIDATED_1seed_DOMINATES_two_store_regime_switch_on_single_store_elegance_native_calib_sparsity_and_retrieval_TRADES_deep_composition_depth_J32_vs_regime_switch_J64_SINGLE_SEED_seed13_NOT_LANDED_paired_confirmation_REQUIRED_and_FULL_deployable_ckpt_REMOTE_ONLY_not_persisted_local_before_CG_arc_closure_2026-07-04"

atom = {
    "id": "math::MEASURED_MECHANISM_PERCEPTION_SHIP_GATE_re_verdict_graded_GSBC_codes_SOLVE_the_retrieval_agreement_gap_that_made_the_seed7_ship_metric_MIDDLE_BAND_baseline_SIGN_INBATCH_BLOCK_cosine_0p8611_PASS_composed_at_J10_0p9833_PASS_ret_agree10_0p1837_MISS_0p30_ONLY_the_ret_axis_failed_and_hard_STE_sign_quantization_is_CONFIRMED_the_cause_all_hard_sign_codes_sit_0p18_to_0p22_the_GRADED_fix_v11_GSBC_FULL_block_topm3_full_recipe_2seed_ret_0p3986_0p3968_BOTH_clear_0p30_lift_pos0p1869_pos0p1791_cosine_hi80_0p8338_0p8300_BOTH_clear_0p80_keyed_J5_1p000_shuffled_0p000_cv_ret_0p0023_cos_0p0023_composed_at_J10_ge_0p95_by_SOUND_monotone_bracketing_no_exact_J10_point_exists_Jsweep_1_2_5_8_16_32_64_keyed_acc_monotone_nonincreasing_in_J_so_J10_ge_J16_and_same_geometry_graded_block_v12_GSBC_RKD_BLOCK_J16_0p9833_seed7_1p000_seed13_full_recipe_does_NOT_degrade_keyed_margin_snr_0p0575_vs_0p0580_so_GSBC_FULL_at_J10_tracks_block_the_KEY_GAP_v12_EXPAND2X_J8_eq_J16_eq_1p000_does_NOT_close_the_J10_for_GSBC_FULL_gap_because_EXPAND2X_is_a_DIFFERENT_code_gwta_global_topk_out8192_kb64_rkd_vs_GSBC_FULL_block_topm3_out4096_full_different_sha256_geometry_width_recipe_Director_suspicion_CORRECT_use_same_geometry_RKD_BLOCK_not_EXPAND2X_VERDICT_perception_PASSES_the_joint_ship_gate_with_graded_codes_retrieval_gap_SOLVED_RESERVATION_no_strict_single_carrythrough_run_co_measures_ret_plus_cosine_plus_keyed_at_J10_on_ONE_deployed_graded_code_with_an_exact_J10_point_confirming_FULL_is_CHEAP_high_prior_PASS_not_a_research_risk_2seed_FULL178k_2026-07-05",
    "name": "MATH MEASURED_MECHANISM (perception SHIP-GATE re-verdict): graded GSBC codes SOLVE the retrieval-agreement gap that made the seed_7 ship metric MIDDLE_BAND. Baseline (SIGN INBATCH_BLOCK) failed ONLY the ret axis (cosine 0.8611 PASS, composed@J10 0.9833 PASS, ret_agree10 0.1837 MISS 0.30); hard-STE sign quantization CONFIRMED the cause (all hard-sign codes sit ret 0.18-0.22). Graded fix (v11 GSBC_FULL block-topm=3, full recipe, 2 seeds): ret 0.3986/0.3968 (both clear 0.30; +0.1869/+0.1791 lift), cosine 0.8338/0.8300 (both clear 0.80), keyed@J5 1.000 shuffled 0.000, cv ~0.002. composed@J10>=0.95 met by SOUND monotone bracketing (no exact J10 point; keyed acc monotone-decreasing in J so J10>=J16; same-geometry graded block v12 GSBC_RKD_BLOCK J16=0.9833/1.000 both seeds; full recipe does NOT degrade keyed margin). KEY GAP: v12 EXPAND2X J8=J16=1.000 does NOT close the J10-for-GSBC_FULL gap -- EXPAND2X is a DIFFERENT code (gwta/8192/rkd vs block/4096/full). VERDICT: perception PASSES the joint ship gate with graded codes; retrieval-gap SOLVED. RESERVATION: no strict single carry-through co-measures all three on the exact deployed code with a J10 point -> a CHEAP confirming FULL is warranted (high prior of PASS, not a research risk).",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": "proven_bound_perception_ship_gate_retrieval_gap_SOLVED_by_graded_codes_joint_gate_met_ret_cosine_direct_composedJ10_by_monotone_bracketing_strict_single_run_co_measurement_on_exact_deployed_code_pending_cheap_confirming_FULL",
    "cert_class": "perception_ship_gate_reverdict_graded_GSBC_codes_close_retrieval_agreement_gap_hard_STE_sign_quantization_confirmed_bottleneck_ret_030_cosine_080_direct_2seed_composed_at_J10_095_by_sound_monotone_bracketing_same_geometry_block_arm_EXPAND2X_different_code_does_not_close_J10_gap",
    "description": (
        "SHIP-GATE RE-VERDICT of the already-landed graded-code encoder chain (v11/v12) against the "
        "perception ship gate: ret_agree10>=0.30 AND cosine_to_gold>=0.80 AND composed_roundtrip@J10>=0.95. "
        "AUDIT-ONLY, no new dispatch. Six metrics.json read + arithmetic independently reproduced via .venv "
        "(NOT verdict_msg). "
        "\n"
        "BASELINE (the MIDDLE_BAND being re-verdicted): exp_encoder_step2step3_inbatch_rkd_shipmetric_"
        "carrythrough_v1_seed_7 (run_mode=full, N=4096, mlp_hidden=2048, teacher_n=177899). Deployed code = "
        "SIGN INBATCH_BLOCK (sbc block-local circular-conv). cosine_to_gold=0.8611 (PASS>=0.80); "
        "composed_roundtrip@J10=0.9833 (PASS>=0.95, keyed INBATCH_BLOCK J10 acc_at1); ret_agree10=0.18367 "
        "(MISS<0.30). So the seed_7 ship metric failed ONLY on the retrieval-agreement axis; cosine and the "
        "J10 composition were already clear on the hard-sign code. Cause = hard-STE argmax-to-sign "
        "quantization: CONFIRMED off-disk -- all hard-sign codes cluster at ret 0.18-0.22 (seed_7 0.1837; "
        "v11 SIGN_BLOCK final 0.2117 seed7 / 0.2177 seed13). "
        "\n"
        "GRADED FIX (does graded genuinely clear 0.30, is +0.187 real, cosine held, algebra preserved UNDER "
        "GRADED): v11 GSBC_FULL (graded GSBC block-topm=3, kb32/blk128/m3, out_dim=4096, FULL recipe = "
        "annealed soft->hard STE + soft/hard consistency + ListNet listwise-rank + absolute-cosine anchor), "
        "2 seeds [7,13]: ret_agree10 = 0.39861 / 0.39676 (BOTH clear 0.30; margin ~+0.10). LIFT vs paired "
        "hard SIGN_BLOCK = 0.39861-0.21172 = +0.18689 (seed7, reproduces the cited +0.1869 EXACT) and "
        "0.39676-0.21766 = +0.17910 (seed13). cosine_to_gold(hi80) = 0.83380 / 0.83001 (BOTH clear 0.80). "
        "cross-seed cv: ret 0.0023, cosine 0.0023 (tight). ALGEBRA UNDER GRADED preserved: keyed@J5 "
        "gsbc_circconv acc_at1=1.000 (both seeds), shuffled_key=0.000; smoke corroborates (RANDOM_GRADED "
        "J5=1.000, GRADED J5=J8=1.000). So the retrieval-gap that produced the MIDDLE_BAND is genuinely "
        "closed while cosine and algebra hold. (The higher-ret graded arms clear 0.30 by even more: v12 "
        "GSBC_RKD_BLOCK 0.4447/0.4664, GWTA 0.5629/0.6224, EXPAND2X 0.6027/0.6802.) "
        "\n"
        "THE J10 QUESTION (rigorous, per task): the ship gate wants composed_roundtrip@J10>=0.95 for the "
        "deployed GRADED code. NO exact J10 point exists anywhere -- v11 gated keyed@J5 ONLY; the v12 J-sweep "
        "is {1,2,5,8,16,32,64}. J10 falls between J8 and J16 and is bracketed. keyed roundtrip acc_at1 is "
        "MONOTONE-NONINCREASING in J (binding more items into a bundle monotonically increases crosstalk), so "
        "composed@J10 >= composed@J16 is a SOUND lower bound. For the SAME-geometry graded block code (v12 "
        "GSBC_RKD_BLOCK, code_mode=block, top-m=3, out_dim=4096 -- identical geometry to GSBC_FULL, differing "
        "ONLY in recipe rkd vs full): J16 = 0.9833 (seed7) / 1.000 (seed13) => composed@J10 >= 0.9833 >= 0.95, "
        "BOTH seeds. The full-recipe change does NOT degrade the keyed binding margin (GSBC_FULL J5 "
        "snr_margin=0.0575 ~ GSBC_RKD J5 snr_margin=0.0580 seed7), so GSBC_FULL@J10 tracks the block@J10 lower "
        "bound. Additionally the baseline HARD block code already cleared composed@J10=0.9833 with the SAME "
        "block-circular-conv binding algebra, and graded only changes activations (sign->graded), not the "
        "binding -- so there is no mechanism by which graded would DEGRADE composition depth. composed@J10>=0.95 "
        "is therefore EFFECTIVELY MET for the graded block family. "
        "\n"
        "KEY GAP -- does v12 EXPAND2X J8=J16=1.000 close the J10-for-GSBC_FULL gap? NO. GSBC_EXPAND2X is a "
        "DIFFERENT CODE: code_mode=gwta (global top-K), out_dim=8192, kb64, sparsity=192, recipe=rkd_only, "
        "distinct sha256; GSBC_FULL is code_mode=block (per-block top-m=3), out_dim=4096, kb32, recipe=full. "
        "Different geometry, width, recipe, and depth envelope. EXPAND2X's J8=J16=1.000 depth does NOT transfer "
        "to certify GSBC_FULL's J10. The Director's suspicion is CORRECT -- the J10-for-GSBC_FULL concern is NOT "
        "closed by EXPAND2X. The proper depth evidence for the block family is the SAME-geometry GSBC_RKD_BLOCK "
        "arm (J10 >= J16 >= 0.9833, 2 seeds), NOT EXPAND2X. "
        "\n"
        "VERDICT: perception PASSES the joint ship gate with graded codes. ret>=0.30 and cosine>=0.80 are "
        "DIRECT on GSBC_FULL, 2 seeds, tight cv; composed@J10>=0.95 is met by a SOUND monotone lower bound on "
        "the same-geometry graded block code, 2 seeds. The retrieval-agreement gap that made seed_7 MIDDLE_BAND "
        "is SOLVED -- graded codes fix exactly the one failing axis (ret) without disturbing cosine or "
        "composition depth. "
        "\n"
        "WHY MEASURED_MECHANISM NOT A CLEAN CHAIN_GRADE PASS (honest, symmetric reservation -- NOT deflating "
        "the win): no STRICT single carry-through run co-measures ret_agree10 + cosine_to_gold + keyed@J10 on "
        "ONE deployed graded code with an EXACT J=10 point (the discipline the seed_7 carry-through embodied: "
        "one code through Step2 sparse-encode + Step3 ship metric, all gates on the same artifact). ret+cosine "
        "are measured on GSBC_FULL; the J10 lower bound is on the rkd-recipe block arm; no exact J10 point "
        "exists. This is a CO-MEASUREMENT gap, not a mechanism gap. A CONFIRMING FULL is warranted but CHEAP: "
        "re-run the deployed graded block code (GSBC_FULL or the GSBC_RKD_BLOCK winner) through the ship "
        "carry-through with the keyed J-sweep INCLUDING J=10 co-measured alongside ret+cosine. Very high prior "
        "of PASS (all pieces already evidenced); it is a formality, not a research risk. "
        "\n"
        "IS A CONFIRMING FULL ACTUALLY NEEDED? For engineering deployment: effectively NO -- the retrieval-gap "
        "is solved and all three gates are evidenced. For a STRICT single-artifact chain-grade PASS stamp: YES, "
        "one cheap confirming carry-through with a J=10 point on the deployed graded code."
    ),
    "aliases": [
        "perception_ship_gate_retrieval_gap_solved_by_graded_GSBC_codes_composedJ10_by_monotone_bracketing_MM",
        "graded_codes_fix_the_one_failing_ret_axis_of_seed7_MIDDLE_BAND_EXPAND2X_different_code_does_not_close_J10_for_GSBC_FULL",
    ],
    "metadata": {
        "record_class": "experiment_landed_vet_ship_gate_reverdict_measured_mechanism_proven_bound",
        "term_class": "PERCEPTION_SHIP_GATE_REVERDICT_GRADED_GSBC_CODES_SOLVE_RETRIEVAL_AGREEMENT_GAP_JOINT_GATE_MET_COMPOSED_J10_BY_MONOTONE_BRACKETING_STRICT_SINGLE_RUN_CO_MEASUREMENT_PENDING",
        "cert_status": "proven_bound_perception_ship_gate_retrieval_gap_SOLVED_by_graded_codes_joint_gate_met_ret_cosine_direct_composedJ10_by_monotone_bracketing_strict_single_run_co_measurement_on_exact_deployed_code_pending_cheap_confirming_FULL",
        "cert_class": "perception_ship_gate_reverdict_graded_GSBC_codes_close_retrieval_agreement_gap_hard_STE_sign_quantization_confirmed_bottleneck_ret_030_cosine_080_direct_2seed_composed_at_J10_095_by_sound_monotone_bracketing_same_geometry_block_arm_EXPAND2X_different_code_does_not_close_J10_gap",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "verified_via": "independent .venv off-disk recompute of 6 metrics.json (v11 seed7/13, v12 seed7/13, smoke, seed_7 baseline): lift arithmetic reproduced EXACT, cross-seed cv, monotone-bracketing lower bound for composed@J10, code-identity/sha256 distinctness EXPAND2X vs GSBC_FULL vs RKD_BLOCK; NOT verdict_msg",
        "atomized_by": "skunkworks_landed_VET_2026-07-05_perception_shipgate_reverdict_graded_codes_MM",
        "anchor": "encoder_gsbc_gradedcode_retrieval_v1_and_v11_v12_shipgate_reverdict_vs_step2step3_shipmetric_carrythrough_seed7",
        "cell_commit": "034b145d7",
        "raw_metrics_paths": [
            "data/exp_encoder_v11_gsbc_graded_sparse_v1_seed7/metrics.json",
            "data/exp_encoder_v11_gsbc_graded_sparse_v1_seed13/metrics.json",
            "data/exp_encoder_v12_gsbc_gwta_expansion_v1_seed7/metrics.json",
            "data/exp_encoder_v12_gsbc_gwta_expansion_v1_seed13/metrics.json",
            "data/exp_encoder_gsbc_gradedcode_retrieval_v1_smoke/metrics.json",
            "data/exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_seed_7/metrics.json",
        ],
        "run_mode": "full", "N": 4096, "teacher_n_concepts": 177899, "n_seeds": 2, "seeds": [7, 13],
        "ship_gate": {"ret_agree10_min": 0.30, "cosine_to_gold_min": 0.80, "composed_roundtrip_J10_min": 0.95},
        "recompute_off_disk": {
            "baseline_seed7_deployed_SIGN_INBATCH_BLOCK": {
                "cosine_to_gold": 0.8610670566558838, "cosine_pass": True,
                "composed_roundtrip_at_J10": 0.9833333492279053, "composed_pass": True,
                "ret_agree10": 0.18367060146147768, "ret_pass": False,
                "verdict": "MIDDLE_BAND failed ONLY the ret axis; cosine and composed@J10 already clear on hard-sign code",
            },
            "hard_sign_ret_cluster_confirms_quantization_cause": {
                "seed7_carrythrough_INBATCH_BLOCK": 0.1837, "v11_SIGN_BLOCK_seed7": 0.2117, "v11_SIGN_BLOCK_seed13": 0.2177,
                "verdict": "all hard-STE sign codes sit 0.18-0.22 << 0.30 -> hard-STE sign quantization is the confirmed retrieval-agreement bottleneck",
            },
            "graded_fix_v11_GSBC_FULL_block_topm3_full_recipe": {
                "ret_agree10_seed7": 0.3986059584035945, "ret_agree10_seed13": 0.39675660483417435,
                "both_clear_0p30": True,
                "lift_vs_SIGN_seed7": 0.18688589, "lift_vs_SIGN_seed13": 0.17909500,
                "cited_lift_0p1869_reproduces_EXACT": True,
                "cosine_hi80_seed7": 0.8337977528572083, "cosine_hi80_seed13": 0.8300113677978516,
                "both_clear_0p80": True,
                "ret_cross_seed_cv": 0.0023, "cosine_cross_seed_cv": 0.0023,
                "keyed_J5_gsbc_circconv_acc1_both_seeds": 1.000, "shuffled_key": 0.000,
                "algebra_preserved_under_graded": True,
            },
            "composed_at_J10_by_monotone_bracketing": {
                "j_sweep": [1, 2, 5, 8, 16, 32, 64], "exact_J10_point_exists": False,
                "keyed_acc_monotone_nonincreasing_in_J": True,
                "lower_bound_rule": "composed@J10 >= composed@J16 (fewer bound items = less crosstalk)",
                "same_geometry_graded_block_GSBC_RKD_BLOCK_J16_seed7": 0.9833333492279053,
                "same_geometry_graded_block_GSBC_RKD_BLOCK_J16_seed13": 1.0,
                "composed_J10_lower_bound_seed7": 0.9833, "composed_J10_lower_bound_seed13": 1.0,
                "both_clear_0p95": True,
                "full_recipe_does_not_degrade_keyed_margin": {"GSBC_FULL_J5_snr": 0.0575, "GSBC_RKD_J5_snr": 0.0580},
                "verdict": "composed@J10>=0.95 EFFECTIVELY MET for graded block family by sound monotone lower bound, 2 seeds; NOT co-measured on exact GSBC_FULL run",
            },
            "KEY_GAP_EXPAND2X_is_a_DIFFERENT_code": {
                "GSBC_FULL_geom": "code_mode=block(per-block top-m=3), out_dim=4096, kb32, recipe=full",
                "GSBC_EXPAND2X_geom": "code_mode=gwta(global top-K), out_dim=8192, kb64, sparsity=192, recipe=rkd_only",
                "distinct_sha256": True,
                "EXPAND2X_J8_J16_seed7": [1.0, 1.0], "EXPAND2X_J8_J16_seed13": [1.0, 1.0],
                "closes_J10_for_GSBC_FULL": False,
                "verdict": "EXPAND2X J8=J16=1.0 does NOT certify GSBC_FULL's J10 (different geometry/width/recipe); use SAME-geometry GSBC_RKD_BLOCK bracket instead. Director suspicion CORRECT.",
            },
            "v12_seed13_paired_confirmation_now_landed": {
                "EXPAND2X_seed13": 0.6802023608769148, "GWTA_seed13": 0.6223833614390318, "BLOCK_seed13": 0.46636874648679005,
                "note": "prior v12 atom's 'seed13 NOT LANDED, paired confirmation REQUIRED' reservation is now SATISFIED off-disk (both seeds consistent)",
            },
        },
        "non_vacuity_checks": {
            "paired_hard_vs_graded_control_fires": "hard SIGN_BLOCK ret 0.2117/0.2177 (fail) vs graded GSBC_FULL 0.3986/0.3968 (pass), same trainer/pairing -> the lift is attributable to dropping argmax-to-sign quantization, not to training length or config drift",
            "algebra_positive_control": "keyed@J5 gsbc_circconv=1.000 both seeds and shuffled_key=0.000; random-block/random-key also 1.000 (harness sane) while random SEMANTIC ret ~0.0005 (near chance) -> retrieval discriminator is real, not saturated",
            "cardinality_and_arms_differ": "v11 n_units 28/28 both seeds cardinality_ok; v12 37/37; arms_differ_verified True; distinct arm_code_sha256 per arm",
            "baseline_in_band": "all cells baseline_in_band True; CHARPOS surface control ret 0.066-0.068 (near floor) confirms the metric is not trivially passable",
        },
        "cross_arc_overlap_check_2026_07_01_USER_locked": "substrate_query 'graded GSBC sparse block code retrieval agreement encoder ship gate perception' -> top cosine 0.2842 (< 0.30 threshold); hits = notes/research_drill_path_b_variations REALM/Atlas two-tower retrieval + notes/wave14e 'Sparse block codes' generic mention; NOT this GSBC ship-gate retrieval-agreement chain. KB blind to this chain (Director flagged). NOVEL synthesis; no rediscovery.",
        "composes_with_atoms": [PRIOR_V11_ID, PRIOR_V12_ID],
        "composition_note": "COMPOSES WITH (does NOT supersede) the two 2026-07-04 encoder-lever MM atoms: v11 GSBC_GRADED_SINGLE_CODE (atomized the graded ret lifts + calibration) and v12 GSBC_EXPAND2X (atomized the winning-code lever + depth envelope). Those atomized the ENCODER retrieval LEVERS; THIS atom is the distinct PERCEPTION SHIP-GATE re-verdict connecting them to the seed_7 MIDDLE_BAND ship metric (ret>=0.30 AND cosine>=0.80 AND composed@J10>=0.95). Neither prior atom is superseded. Amends the v12 atom's 'seed13 NOT LANDED' reservation: now satisfied off-disk.",
        "framing_corrections_vs_director_and_cell": "AFFIRM: (1) graded GSBC_FULL genuinely clears ret 0.30 (0.3986/0.3968, 2 seeds) and the +0.1869 lift reproduces EXACT off-disk; (2) cosine stays >=0.80 (0.834/0.830) and algebra roundtrip is preserved UNDER GRADED (keyed@J5=1.000, shuffled 0.000); (3) the Director's suspicion that v12 EXPAND2X does NOT close the J10-for-GSBC_FULL gap is CORRECT -- EXPAND2X is a different code (gwta/8192/rkd). ADD/CORRECT: (a) the seed_7 MIDDLE_BAND failed ONLY the ret axis -- cosine (0.8611) and composed@J10 (0.9833) were ALREADY clear on the hard code, so graded fixing ret is exactly sufficient; (b) the STRONGER J10 evidence is NOT EXPAND2X but the SAME-geometry graded block arm GSBC_RKD_BLOCK, where composed@J10 >= J16 >= 0.9833 by a SOUND monotone lower bound, both seeds -> the J10 concern is EFFECTIVELY closed for the graded block family, not genuinely wide-open; (c) so the honest bottom line is NOT 'gap open needing a research FULL' but 'gap effectively met; one CHEAP confirming carry-through with a J=10 point on the deployed code would stamp the strict single-run joint gate.' No over-claim (no strict single-artifact PASS yet) and no unfair deflation (retrieval-gap is genuinely SOLVED).",
        "envelope_and_next_test": "The one open item is a CO-MEASUREMENT, not a mechanism: run the deployed graded block code (GSBC_FULL or GSBC_RKD_BLOCK winner) through the Step2 sparse-encode + Step3 ship-metric carry-through with the keyed J-sweep INCLUDING J=10, so ret_agree10 + cosine_to_gold + composed_roundtrip@J10 are all co-measured on ONE deployed artifact, >=2 seeds. High prior of PASS. Optional stretch: confirm on the higher-ret EXPAND2X code too (ret 0.60-0.68) if single-store elegance is not required, noting its J32<0.97 shallower-than-block deep-composition tradeoff.",
        "expansion_criterion": "PROMOTES to CHAIN_GRADE iff a single carry-through run co-measures ret>=0.30 AND cosine>=0.80 AND composed_roundtrip@J10>=0.95 on ONE deployed graded code (exact J=10 point), >=2 seeds, tight cv. Stays MEASURED_MECHANISM if the pieces remain measured on separate runs/arms. DEMOTES only if a confirming run fails to reproduce the graded ret lift or the J10 depth (NOT expected; lift reproduced exact, J10 bracketed >=0.9833 both seeds).",
        "disposition": "MEASURED_MECHANISM_perception_ship_gate_retrieval_gap_SOLVED_by_graded_GSBC_codes_ret_030_and_cosine_080_direct_on_GSBC_FULL_2seed_composed_at_J10_095_by_sound_monotone_bracketing_on_same_geometry_graded_block_arm_EXPAND2X_different_code_does_not_close_J10_gap_strict_single_run_co_measurement_pending_cheap_confirming_FULL_high_prior_PASS",
        "cert_increment_delta": 1,
    },
}


def a5_append(path, atom):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_atoms_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    n_lines = 0
    found = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_lines += 1
            obj = json.loads(line)  # integrity: raises on corrupt line
            aid = obj.get("id") or obj.get("atom_id")
            if aid == atom["id"]:
                found += 1
    if found != 1:
        raise RuntimeError(f"verify-load failed: atom id found {found}x (expected 1) in {path}")
    return n_lines


def ledger_append(atom, ledger_path=CERT_LEDGER):
    md = atom["metadata"]
    entry = {
        "ts": TS,
        "ts_iso": TS_ISO,
        "atom_id": atom["id"],
        "corpus": atom["corpus"],
        "tier": atom["tier"],
        "cert_status": md.get("cert_status"),
        "cert_class": md.get("cert_class"),
        "cert_increment_delta": md.get("cert_increment_delta", 0),
        "verified_off_data": True,
        "anchor": md.get("anchor"),
        "cell_commit": md.get("cell_commit"),
        "auditor": "skunkworks",
        "atomized_by": md.get("atomized_by"),
        "landed_VET_session": SESSION_TAG,
        "note": "perception SHIP-GATE re-verdict: graded GSBC codes SOLVE the retrieval-agreement gap (ret 0.18->0.30-0.68, cosine held >=0.80, algebra preserved); joint gate met (ret+cosine direct on GSBC_FULL 2seed; composed@J10>=0.95 by SOUND monotone bracketing on same-geometry graded block arm, J10>=J16>=0.9833 both seeds); v12 EXPAND2X (different code) does NOT close the J10-for-GSBC_FULL gap; strict single-run co-measurement on exact deployed code pending -> CHEAP confirming FULL, high prior PASS",
    }
    d = os.path.dirname(ledger_path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_ledger_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(ledger_path):
                with open(ledger_path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ledger_path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


if __name__ == "__main__":
    print(f"[atomize] ts_iso={TS_ISO}")
    n = a5_append(MATH_ATOMS, atom)
    print(f"[atomize] math MEASURED_MECHANISM perception-ship-gate-reverdict appended; math lines={n}")
    ledger_append(atom)
    print("[atomize] DONE 1 atom + 1 ledger entry; A5-gated (tmp+os.replace+verify-load+json-integrity); matching TS_ISO")
    print("[atomize] NET CERT DELTA: MM +1 (perception ship-gate retrieval-gap SOLVED by graded codes, strict single-run co-measurement pending), CG 0, HF 0")
