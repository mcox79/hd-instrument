"""
A5-gated atomization batch — Skunkworks landed-VET / re-audit 2026-07-04.

Probe 1 STORAGE x CLEANUP_MECHANISM CG_META cross-term re-audit (family sub-audit
flagged by the P8 demote atom this same day). NONE of these had touched the ledger.

BATCH CONTENTS (5 atoms, matching TS_ISO):
  (1) math AMEND_DEMOTE  — Probe 1 CG_META cross-term (line 28996)
        CHAIN_GRADE_META -> DEMOTE. The "mechanism axis meaningful only at BUNDLED"
        cross-term is a TR=100 unpaired-salt noise artifact. CG -1.
  (2) math AMEND_DEMOTE  — MM_STANDARD confirmatory replication (line 29012)
        "cross-term is a REAL regime-cross-term (not artifact)" is falsified. MM -1.
  (3) math SPLIT-A CG confirmatory — STORAGE MAIN EFFECT survives (median gap 0.93).
        Confirms prior SHARDED-capacity-cliff atom #56; NOT novel -> cert delta 0.
  (4) math SPLIT-B MEASURED_MECHANISM — the 3 cleanup mechanisms are argmax-degenerate
        for index readout: paired TR=400 range EXACTLY 0.0000 on all 36 BUNDLED cells.
        The cross-term is provably ABSENT (not merely unproven). MM +1.
  (5) meta MM_STANDARD — paired-trials MANDATORY for arm-comparison max/range
        discriminators (unpaired manufactures phantom cross-terms). MM +1. Composes with
        + promotes the P8 MM_TENTATIVE extreme-value-null calibration meta.

NET CERT DELTA (this batch): CG -1, MM +1.

======================= INDEPENDENT RECOMPUTE EVIDENCE (Skunkworks, off-disk) =======================
Data: data/exp_stage1_regime_map_storage_x_cleanup_v1_s{7,13,19}/metrics.json
Cell core: experiments/_stage1_regime_map_storage_x_cleanup_v1_core.py (commit cdc81fddb lineage)

DISCRIMINATOR REPRODUCE-CHECK: recomputed mechanism_variance_at_BUNDLED (= range max-min of
  3 mechanism accuracies per (M,N,corr) cell) from raw phase_map. max|recomp - stored| = 0.0
  all 3 seeds. Stored discriminator = range of 3 UNPAIRED mechanism accuracies. Verdict on
  disk all seeds: HARD_PASS_MECHANISM_AXIS_CONDITIONAL_ON_STORAGE. The HARD_PASS trigger was
  mech_var_at_BUNDLED >= 0.05 (0.10/0.12/0.09); the ANOVA interaction map itself is ~0
  (max_abs_dev_storage_x_cleanup = 0.0028/0.0058/0.0024).

SALT STRUCTURE (structural crux): eval_phase_point sets gen.manual_seed(seed*100003 + salt);
  run_one_seed does salt += 1 per (storage, mech, M, N, corr) tuple. => the 3 mechanisms at a
  given BUNDLED cell each get a DISTINCT seed => UNPAIRED random items+corruptions. The range
  of 3 iid-ish Binomial(TR, p_cell)/TR draws IS a noise floor by construction.

TR=100 data-driven binomial extreme-value null (Skunkworks NDRAW=200000, each cell own p_cell/TR):
  stat        obs      null_mean   z       P(null>=obs)
  MAX range   0.1200   0.1353     -0.62    0.786
  MEAN range  0.0306   0.0351     -1.11    0.877
  COUNT>0.02  15/36    17.4       -1.46    0.957
  => observed sits BELOW the noise-floor mean in ALL THREE statistics (sub-null).

TR=400 UNPAIRED revival (Skunkworks re-ran BUNDLED grid via cell's own eval_phase_point):
  MAX range obs 0.0750 (null 0.0677, z +0.58, P 0.259) — tracked the floor DOWN from 0.10
    (pure-noise prediction 0.10*sqrt(100/400)=0.05); MEAN 0.0214 (null 0.0179, z +1.71, marginal);
  a REAL 0.10 effect would have HELD ~0.10 and cleared the tighter TR=400 floor (~0.068). It did not.

TR=400 PAIRED (shared salt across the 3 mechs per cell; most-sensitive; common-noise cancels):
  MAX range 0.000000, MEAN range 0.000000, COUNT>0 = 0/36 cells. z = -5.44 (max), -8.88 (mean).
  => when the 3 mechanisms see IDENTICAL items+corruptions they produce BIT-IDENTICAL accuracy on
  all 36 BUNDLED cells. 100% of the TR=100 "mechanism variance" was unpaired sampling noise.
  (Matches Director estimate z -5.45/-8.68 essentially exactly.)

MECHANISTIC ROOT (why range=0): the chain readout is ci = cleanup_argmax_idx(Q_clean, props) =
  argmax Re(Q_clean @ props*.T). All 3 mechanisms preserve that argmax index at the cell's
  BETA/ALPHA_SOFT: iterative_cosine snaps to the nearest codeword (= argmax); modern_hopfield
  softmax-weights (top entry dominates argmax); soft_energy nudges toward target (argmax
  preserved). ACCURACY depends ONLY on the argmax index, so it is mechanism-invariant even
  though arms_differ_verified passed on output-VECTOR hashes (the vectors do differ; the
  argmax indices do not). This is a genuine READOUT_DEGENERATE finding (cf. prior
  cross_layer_compose_LM_v2 READOUT_DEGENERATE->MEASURED_MECHANISM precedent, cosine 0.30).

STORAGE MAIN EFFECT (survivor, off raw 36 SHARDED-BUNDLED pairs/seed):
  median gap 0.935/0.93/0.92 (reproduces stored median_storage_gap); 36/36 pairs positive;
  min gap 0.76; SHARDED mean=1.000 min=1.000 all seeds; BUNDLED mean 0.093/0.094/0.087, max 0.24.
  CAVEAT (symmetric): SHARDED is CEILING-SATURATED (acc=1.0 everywhere) so (a) the gap is a LOWER
  bound on true separation, and (b) the "0/36 mech var at SHARDED" is saturation-vacuous (range=0
  by construction), carrying no evidential weight for the "collapses at SHARDED" half of the
  original verdict. The BUNDLED floor (~0.09) is genuine bundle-superposition capacity limit.

FRAMING CORRECTION (Fix#28, downward, on a PRIOR SKUNKWORKS atom — "correct my own flattering
  reconciliation" discipline): the 2026-07-03 landed-VET accepted the cross-term as CG_META and
  recorded "auditor_framing_correction_vs_cell_author: NONE — cell-author framing precise". The
  discriminator VALUE was recomputed correctly (reproduces exactly), but the INFERENCE (nonzero
  BUNDLED range = real mechanism moderation) was never gated against a binomial extreme-value
  null or a paired-trial design. Both now show the effect is exactly 0. Honest downward.
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
META_ATOMS = "d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))

ANCHOR = "stage1_regime_map_storage_x_cleanup_v1"
PROBE1_CG_ID = ("math::T1/MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_MECHANISM_CROSS_TERM_FULL_CG_META_3_seeds_7_13_19_GPU_HARD_PASS_MECHANISM_AXIS_CONDITIONAL_ON_STORAGE_categorical_interaction_at_BUNDLED_24of36_subregime_cells_show_nonzero_cross_mechanism_variance_max_0p12_at_SHARDED_0of36_cells_all_exactly_0p00_across_full_factorial_M_in_200_800_3200_x_N_in_2048_8192_x_corruption_0p20_0p45_x_3_mechanisms_modern_hopfield_iterative_cosine_soft_energy_attractor_per_seed_max_mv_BUND_0p10_0p12_0p09_mean_0p1033_stdev_0p01528_cv_0p148_under_0p15_CG_threshold_max_int_deviation_0p0024_to_0p0058_cardinality_ok_arms_differ_verified_positive_control_iterative_cosine_regime_pass_acc_1p000_all_seeds_median_storage_gap_SHARDED_minus_BUNDLED_0p93_confirms_storage_dominates_readout_quality_secondary_but_load_bearing_finding_is_the_cross_term_mechanism_choice_matters_ONLY_at_BUNDLED_not_at_SHARDED_2026_07_03")
PROBE1_MM_ID = ("math::MM_STANDARD/EXP_stage1_regime_map_storage_x_cleanup_v1_s7_s13_s19_FULL_3seed_MECHANISM_AXIS_CONDITIONAL_ON_STORAGE_cross_term_HARD_PASS_all_seeds_mech_var_BUNDLED_0p09_0p10_0p12_cv_0p148_mech_var_SHARDED_0p00_all_seeds_max_int_dev_le_0p0058_max_storage_gap_1p0_all_seeds_composes_with_Probe1_STORAGE_x_CLEANUP_CG_META_and_atom_56_SHARDED_capacity_cliff_regime_map_layer1_root_2026-07-03")

METRICS = [f"data/exp_{ANCHOR}_s{s}/metrics.json" for s in (7, 13, 19)]

atom_1_probe1_cg_demote = {
    "id": "math::AMEND_DEMOTE_stage1_regime_map_PROBE1_STORAGE_x_CLEANUP_MECHANISM_CROSS_TERM_CG_META_to_DEMOTED_3seed_FULL_the_mechanism_moderation_at_BUNDLED_is_a_TR100_unpaired_salt_noise_artifact_TR100_range_obs_max0p12_mean0p031_count15of36_all_BELOW_binomial_extreme_value_null_z_neg0p62_neg1p11_neg1p46_TR400_unpaired_tracks_floor_down_0p10_to_0p075_TR400_PAIRED_shared_salt_range_EXACTLY_0p0000_all_36_cells_z_neg8p88_mechanisms_argmax_degenerate_for_index_readout_SHARDED_0of36_is_ceiling_saturation_vacuous_storage_main_effect_median_gap_0p93_SURVIVES_as_confirmation_of_atom56_2026-07-04",
    "name": "MATH Probe 1 CG_META cross-term DEMOTED: STORAGE x CLEANUP mechanism-moderation is a TR=100 unpaired-salt noise artifact (paired TR=400 range EXACTLY 0 on all 36 cells; z=-8.88). Storage MAIN effect survives; cross-term falls.",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_demotion_amendment",
    "description": (
        "DEMOTES the Probe 1 CG_META cross-term atom (CHAIN_GRADE_META, filed 2026-07-03T18:16:35Z "
        "landed-VET). Honest downward correction of a PRIOR SKUNKWORKS atom, symmetric anti-negativity: "
        "the demotion is itself Monte-Carlo verified AND directly proven by a paired experiment. "
        "CLAIM DEMOTED: 'CLEANUP_MECHANISM choice matters ONLY at BUNDLED (mech_var 0.09-0.12), collapses "
        "at SHARDED (0/36)'. Both halves fail: the BUNDLED 'signal' is unpaired sampling noise; the "
        "SHARDED 'collapse' is ceiling saturation (vacuous). "
        "REPRODUCE-CHECK: recomputed mechanism_variance_at_BUNDLED (=range of 3 mechanism accuracies per "
        "(M,N,corr) cell) off raw phase_map; max|recomp-stored|=0.0 all 3 seeds. Stored discriminator "
        "confirmed = UNPAIRED-salt range. The HARD_PASS trigger was mech_var>=0.05, not the ANOVA "
        "interaction (max_abs_dev = 0.0028/0.0058/0.0024, i.e. ~0). "
        "SALT STRUCTURE: eval_phase_point seeds gen with seed*100003+salt; salt++ per grid tuple => the "
        "3 mechanisms per BUNDLED cell get DISTINCT seeds => independent items+corruptions => the range "
        "of 3 iid Binomial(TR,p)/TR draws is a noise floor by construction. "
        "TR=100 data-driven binomial extreme-value null (NDRAW=2e5, each cell own p_cell/TR): MAX range "
        "obs 0.120 vs null_mean 0.135 z=-0.62 P(null>=obs)=0.786; MEAN 0.0306 vs 0.0351 z=-1.11 P=0.877; "
        "COUNT>0.02 15/36 vs 17.4 z=-1.46 P=0.957 -> observed BELOW noise-floor mean in all 3 statistics. "
        "TR=400 UNPAIRED revival (re-ran BUNDLED grid via cell's own eval_phase_point): MAX range 0.075 "
        "(null 0.068, z+0.58 ns), MEAN 0.0214 (null 0.0179, z+1.71 marginal) -> the spread TRACKED THE "
        "FLOOR DOWN from 0.10 (pure-noise prediction 0.05); a real 0.10 effect would have held ~0.10 and "
        "cleared the tighter floor. It did not. "
        "TR=400 PAIRED (shared salt across the 3 mechs per cell; common-noise cancels): MAX range 0.000000, "
        "MEAN 0.000000, 0/36 nonzero, z=-5.44 (max)/-8.88 (mean). When the mechanisms see IDENTICAL "
        "items+corruptions they produce BIT-IDENTICAL accuracy on all 36 BUNDLED cells. 100% of the "
        "TR=100 'mechanism variance' was unpaired sampling noise. "
        "MECHANISTIC ROOT: chain readout is ci = argmax Re(Q_clean @ props*.T); all 3 mechanisms preserve "
        "that argmax index at the cell BETA/ALPHA_SOFT, so ACCURACY is mechanism-invariant even though the "
        "output VECTORS differ (arms_differ_verified passed on vector hashes; accuracy depends only on the "
        "argmax index). See MEASURED_MECHANISM split atom this batch. "
        "SURVIVES (see SPLIT-A atom this batch): the STORAGE main effect. median SHARDED-BUNDLED gap "
        "0.935/0.93/0.92, 36/36 pairs positive, min gap 0.76; this restates/confirms prior SHARDED-capacity "
        "atom #56 (already CG) and is NOT novel. Probe 1 is NOT worthless; only the cross-term novelty falls. "
        "REVIVAL: EXHAUSTED for accuracy-based mechanism moderation in this regime (paired range provably 0). "
        "A different discriminator (e.g. margin/energy of the cleaned vector, not argmax accuracy) at TR>=400 "
        "PAIRED would be required to revive any mechanism-axis claim; the accuracy cross-term is closed."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment_amendment_demotion",
        "term_class": "STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_CROSS_TERM_DEMOTION_PAIRED_TRIAL_AUDIT",
        "cert_status": "demoted_cross_term_noise_artifact_storage_main_effect_survives",
        "cert_class": "DEMOTE_CG_META_cross_term_paired_trial_and_extreme_value_null_audit",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_probe1_cross_term_paired_reaudit",
        "amends_atom": PROBE1_CG_ID,
        "action": "DEMOTE",
        "raw_metrics_paths": METRICS,
        "cell_source_path": f"experiments/_{ANCHOR}_core.py",
        "n_seeds": 3, "seeds": [7, 13, 19],
        "regime_signature": {"STORAGE": ["SHARDED", "BUNDLED"],
                             "MECH": ["modern_hopfield", "iterative_cosine", "soft_energy_attractor"],
                             "M_grid": [200, 800, 3200], "N_grid": [2048, 8192], "F": 1, "L": 2,
                             "corruption_grid": [0.20, 0.45], "TR_original": 100},
        "reproduce_check_max_abs_diff_vs_stored": 0.0,
        "tr100_binomial_ev_null": {"NDRAW": 200000,
                                   "MAX": {"obs": 0.120, "null_mean": 0.1353, "z": -0.62, "p_null_ge_obs": 0.786},
                                   "MEAN": {"obs": 0.0306, "null_mean": 0.0351, "z": -1.11, "p_null_ge_obs": 0.877},
                                   "COUNT_gt_0p02": {"obs": 15, "null_mean": 17.4, "z": -1.46, "p_null_ge_obs": 0.957}},
        "tr400_unpaired": {"MAX": {"obs": 0.075, "null_mean": 0.0677, "z": 0.58},
                           "MEAN": {"obs": 0.0214, "null_mean": 0.0179, "z": 1.71},
                           "note": "spread tracked noise floor down 0.10->0.075; pure-noise prediction 0.05"},
        "tr400_paired": {"MAX_range": 0.0, "MEAN_range": 0.0, "nonzero_cells_of_36": 0,
                         "z_max": -5.44, "z_mean": -8.88,
                         "interpretation": "bit-identical accuracy on identical inputs; cross-term provably absent"},
        "mechanistic_root": "readout ci=argmax Re(Q_clean @ props*.T); 3 mechanisms argmax-equivalent -> accuracy mechanism-invariant; output vectors differ but argmax indices do not",
        "sharded_0of36_status": "ceiling-saturation-vacuous (acc=1.0 everywhere); no evidential weight for 'collapses at SHARDED'",
        "storage_main_effect_survives": {"median_gap_per_seed": {"7": 0.935, "13": 0.93, "19": 0.92},
                                         "all_36_pairs_positive": True, "min_gap": 0.76,
                                         "status": "confirms prior SHARDED-capacity atom #56; NOT novel"},
        "prior_skunkworks_framing_corrected": "2026-07-03 landed-VET recorded 'auditor_framing_correction: NONE'; discriminator value reproduced but inference (nonzero BUNDLED range = real mechanism effect) never gated vs noise floor/paired trials",
        "family_implication": "P6v2/P7v2 (already MIDDLE_BAND) near-certain same artifact; P8 already DEMOTED (z=0.40); this closes the regime-map mechanism-moderation cross-term family as noise",
        "revival_criteria": ["accuracy cross-term CLOSED (paired range provably 0)",
                             "only a non-argmax discriminator (cleaned-vector margin/energy) at TR>=400 PAIRED could revive a mechanism-axis claim"],
        "cross_arc_overlap_check_2026_07_01_USER_locked": "top hit cosine 0.3115 generic 'Mechanism'; 0.3037 = prior READOUT_DEGENERATE->MEASURED_MECHANISM ruling (different cell, supports disposition); NONE >0.35 duplicating this finding",
        "cert_increment_delta": -1
    }
}

atom_2_mm_confirmatory_demote = {
    "id": "math::AMEND_DEMOTE_stage1_regime_map_storage_x_cleanup_MM_STANDARD_confirmatory_replication_cross_term_is_a_REAL_regime_cross_term_not_artifact_claim_FALSIFIED_paired_TR400_range_exactly_0_z_neg8p88_the_3seed_replication_reproduced_the_SAME_unpaired_salt_noise_floor_not_a_real_effect_storage_main_effect_and_3seed_cardinality_survive_but_were_non_novel_2026-07-04",
    "name": "MATH Probe 1 MM_STANDARD confirmatory replication DEMOTED: its 'cross-term is a REAL regime-cross-term (not artifact)' primary claim is falsified by the paired TR=400 test (range exactly 0).",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_demotion_amendment",
    "description": (
        "DEMOTES the MM_STANDARD confirmatory-replication atom (filed 2026-07-03T23:15Z, math session "
        "index 59) that composed with the Probe 1 CG_META. Its explicit primary_claim was 'STORAGE x "
        "CLEANUP cross-term is a REAL regime-cross-term (not artifact): at BUNDLED the CLEANUP_MECHANISM "
        "axis is MEANINGFUL'. That claim is FALSIFIED: the 3-seed replication faithfully reproduced the "
        "SAME UNPAIRED-salt noise floor (mech_var 0.09/0.10/0.12), which the paired TR=400 test collapses "
        "to EXACTLY 0 on all 36 cells (z=-8.88). Replicating a noise floor across seeds does not make it a "
        "signal. Its own framing already conceded the storage main-effect component 'restates prior "
        "sharded_fhrr_cleanup_capacity_beyond_bundle_bound' (non-novel), so its unique increment was the "
        "cross-term confirmation, which now falls. cross_seed cv=0.148 was measuring the stability of a "
        "noise floor, not of an effect. See the CG demote and MEASURED_MECHANISM split atoms this batch "
        "for full evidence. Storage-dominance (max_storage_gap=1.0 all seeds) survives as confirmation of "
        "atom #56, not as this atom's novel content."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment_amendment_demotion",
        "term_class": "STAGE1_REGIME_MAP_PROBE1_MM_CONFIRMATORY_CROSS_TERM_DEMOTION",
        "cert_status": "demoted_confirmatory_replication_of_noise_floor",
        "cert_class": "DEMOTE_MM_STANDARD_confirmatory_cross_term_paired_trial_audit",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_probe1_cross_term_paired_reaudit",
        "amends_atom": PROBE1_MM_ID,
        "action": "DEMOTE",
        "raw_metrics_paths": METRICS,
        "reason": "primary_claim 'cross-term is REAL not artifact' falsified; 3-seed cv=0.148 measured stability of an unpaired noise floor; paired TR=400 range=0 (z=-8.88)",
        "storage_main_effect_note": "max_storage_gap=1.0 all seeds survives but was self-declared non-novel (restates atom #56)",
        "composes_with_demote": atom_1_probe1_cg_demote["id"],
        "cross_arc_overlap_check_2026_07_01_USER_locked": "same finding as CG demote; NONE >0.35 novel-duplicate",
        "cert_increment_delta": -1
    }
}

atom_3_split_storage_main_effect = {
    "id": "math::SPLIT_stage1_regime_map_storage_x_cleanup_STORAGE_MAIN_EFFECT_survivor_CG_grade_confirmatory_SHARDED_dominates_BUNDLED_readout_quality_median_gap_0p935_0p93_0p92_3seed_FULL_36of36_pairs_positive_min_gap_0p76_SHARDED_mean_1p000_BUNDLED_mean_0p09_confirms_prior_SHARDED_capacity_beyond_bundle_bound_atom56_NOT_novel_delta0_SHARDED_ceiling_saturated_so_gap_is_lower_bound_2026-07-04",
    "name": "MATH Probe 1 SPLIT survivor: STORAGE main effect (SHARDED dominates BUNDLED readout quality; median gap 0.93, 36/36 pairs positive) survives at CG-grade, confirming atom #56 (non-novel, cert delta 0).",
    "corpus": "math",
    "tier": "T2",
    "kind": "experiment_record_main_effect_survivor",
    "description": (
        "SPLIT-off SURVIVOR of the Probe 1 demote. The STORAGE main effect is real, enormous, and 3-seed "
        "stable: recomputed off raw phase_map over 36 SHARDED-BUNDLED matched pairs per seed. Median gap "
        "0.935/0.93/0.92 (reproduces stored median_storage_gap exactly), 36/36 pairs positive, min gap 0.76, "
        "SHARDED mean=1.000 (min 1.000) all seeds, BUNDLED mean 0.093/0.094/0.087 (max 0.24). 'Storage "
        "strategy dominates readout quality in FHRR chain composition' stands firmly. "
        "NOVELTY / DELTA: this CONFIRMS the prior SHARDED-capacity-beyond-bundle-bound atom (#56, already "
        "CG) and the STORAGE x N non-interaction atom (P4); it is a factorial re-confirmation, NOT a new "
        "discovery, so cert_increment_delta = 0 (symmetric anti-inflation; does not re-earn the CG that the "
        "false cross-term forfeited). Filed to preserve the survivor explicitly so the Probe 1 audit does "
        "not lose the real finding. "
        "CAVEAT (symmetric honesty): SHARDED is CEILING-SATURATED (acc=1.0 everywhere in the tested grid), "
        "so (a) the measured gap is a LOWER bound on the true SHARDED-BUNDLED separation and (b) the "
        "'0/36 mechanism variance at SHARDED' is saturation-vacuous, carrying no weight for any "
        "'mechanism collapses at SHARDED' reading. The BUNDLED floor (~0.09) is a genuine "
        "bundle-superposition capacity limit at M in {200,800,3200} with corruption in {0.20,0.45}, not a "
        "construction artifact."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment_main_effect_survivor",
        "term_class": "STAGE1_REGIME_MAP_PROBE1_STORAGE_MAIN_EFFECT_CG_CONFIRMATORY",
        "cert_status": "chain_grade_confirmatory_non_novel_storage_dominance",
        "cert_class": "CG_confirmatory_storage_main_effect_confirms_atom56",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_probe1_cross_term_paired_reaudit",
        "raw_metrics_paths": METRICS,
        "n_seeds": 3, "seeds": [7, 13, 19],
        "median_gap_per_seed": {"7": 0.935, "13": 0.93, "19": 0.92},
        "all_36_pairs_positive_per_seed": True, "min_gap_observed": 0.76,
        "sharded_mean_acc": 1.000, "bundled_mean_acc_per_seed": {"7": 0.0928, "13": 0.0942, "19": 0.0869},
        "sharded_ceiling_saturated": True, "gap_is_lower_bound": True,
        "confirms_atoms": ["#56 sharded_fhrr_cleanup_capacity_beyond_bundle_bound",
                           "stage1_regime_probe_4_STORAGE_x_N_non_interaction_v1"],
        "novelty": "confirmatory factorial re-derivation; NOT novel",
        "cross_arc_overlap_check_2026_07_01_USER_locked": "storage-dominance is prior CG (#56); intentionally CONFIRMATORY not novel; delta 0",
        "cert_increment_delta": 0
    }
}

atom_4_split_measured_mechanism = {
    "id": "math::SPLIT_stage1_regime_map_storage_x_cleanup_MEASURED_MECHANISM_three_cleanup_mechanisms_are_ARGMAX_DEGENERATE_for_index_readout_in_BUNDLED_paired_TR400_range_EXACTLY_0p0000_all_36_cells_z_neg8p88_modern_hopfield_iterative_cosine_soft_energy_attractor_produce_bit_identical_accuracy_on_identical_items_corruptions_because_readout_is_argmax_ReQ_clean_props_conj_output_vectors_differ_but_argmax_indices_do_not_cross_term_provably_absent_2026-07-04",
    "name": "MATH Probe 1 SPLIT MEASURED_MECHANISM: the 3 cleanup mechanisms are argmax-degenerate for index readout in BUNDLED (paired TR=400 range EXACTLY 0 on all 36 cells); cross-term provably absent, not merely unproven.",
    "corpus": "math",
    "tier": "T2",
    "kind": "experiment_record_measured_mechanism_boundary",
    "description": (
        "MEASURED_MECHANISM proven boundary (the substantive product of the Probe 1 re-audit). In the "
        "BUNDLED FHRR chain-composition regime, the three cleanup mechanisms {modern_hopfield, "
        "iterative_cosine, soft_energy_attractor} are ARGMAX-DEGENERATE for the index readout: under a "
        "PAIRED TR=400 design (shared salt => identical items+corruptions across mechanisms) they produce "
        "BIT-IDENTICAL accuracy on ALL 36 sub-regime cells (range EXACTLY 0.000000; z=-8.88 vs the "
        "unpaired binomial null). The cross-term ('mechanism moderates readout at BUNDLED') is therefore "
        "PROVABLY ABSENT, not merely unproven. "
        "MECHANISM: the chain readout is ci = argmax_j Re(Q_clean @ props[j].conj()). iterative_cosine "
        "returns the nearest codeword (argmax by definition); modern_hopfield returns cnorm(softmax(beta*"
        "sim) @ props) whose argmax is dominated by the top entry; soft_energy returns cnorm(Q + "
        "alpha*(target - Q)), a nudge that preserves the argmax. At the cell's BETA/ALPHA_SOFT all three "
        "leave the argmax index unchanged, so accuracy (a function of the index alone) is mechanism-"
        "invariant. The arms_differ_verified gate passed because it hashes the output VECTORS (which do "
        "differ); it does NOT witness accuracy-relevant difference, because accuracy ignores everything "
        "but the argmax. This is a READOUT_DEGENERATE instrument characterization (cf. prior "
        "cross_layer_compose_LM_v2 READOUT_DEGENERATE->MEASURED_MECHANISM precedent, cosine 0.30). "
        "BOUND SCOPE (method-contingent): shown at TR=400 paired, 3 seeds, BUNDLED, M in {200,800,3200}, "
        "N in {2048,8192}, corr in {0.20,0.45}, F=1, L=2, beta/alpha at cell defaults. A mechanism axis "
        "could still discriminate on a NON-argmax metric (cleaned-vector margin, energy, calibration) or "
        "at very low beta; those are open. The ACCURACY cross-term is closed. "
        "COMPOSES WITH: the paired-trials-mandatory meta (this batch) and the P8 extreme-value-null meta; "
        "supersedes the 'mechanism axis meaningful at BUNDLED' reading in the demoted Probe 1 atoms."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment_measured_mechanism",
        "term_class": "STAGE1_REGIME_MAP_PROBE1_CLEANUP_MECHANISM_ARGMAX_DEGENERATE_READOUT",
        "cert_status": "measured_mechanism_argmax_degenerate_cross_term_provably_absent",
        "cert_class": "MEASURED_MECHANISM_readout_argmax_degeneracy_paired_TR400",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_probe1_cross_term_paired_reaudit",
        "raw_metrics_paths": METRICS,
        "cell_source_path": f"experiments/_{ANCHOR}_core.py",
        "primitive_source": "experiments/_stage1_physics_law_joint_composition_factorial_v1_core.py::{run_chain,cleanup_argmax_idx,cleanup_*}",
        "n_seeds": 3, "seeds": [7, 13, 19],
        "paired_tr400_range_all_cells": 0.0, "nonzero_cells_of_36": 0, "z_mean": -8.88, "z_max": -5.44,
        "readout_formula": "ci = argmax_j Re(Q_clean @ props[j].conj())",
        "why_arms_differ_passed_but_accuracy_did_not": "arms_differ hashes output vectors (differ); accuracy depends only on argmax index (invariant)",
        "bound_scope": {"TR": 400, "design": "paired shared-salt", "storage": "BUNDLED",
                        "M": [200, 800, 3200], "N": [2048, 8192], "corr": [0.20, 0.45], "F": 1, "L": 2},
        "open_directions": ["non-argmax discriminator (cleaned-vector margin/energy/calibration)", "very-low-beta regime"],
        "composes_with_atoms": ["meta paired-trials-mandatory (this batch)",
                                "meta::T4/META_extreme_value_null_calibration (P8)",
                                "prior READOUT_DEGENERATE->MEASURED_MECHANISM cross_layer_compose_LM_v2 precedent"],
        "cross_arc_overlap_check_2026_07_01_USER_locked": "cosine 0.3037 prior READOUT_DEGENERATE ruling (different cell) supports disposition; NONE >0.35 duplicate; novel for this cell+axis",
        "cert_increment_delta": 1
    }
}

atom_5_meta_paired_trials = {
    "id": "meta::T4/META_paired_trials_MANDATORY_for_arm_comparison_max_or_range_discriminators_unpaired_independent_salts_MANUFACTURE_phantom_cross_terms_shared_items_corruptions_across_arms_OR_data_driven_binomial_extreme_value_null_REQUIRED_at_prereg_case_study_Probe1_storage_x_cleanup_TR100_unpaired_range_0p10_looked_like_moderation_paired_TR400_range_EXACTLY_0_z_neg8p88_retroactive_to_regime_map_cross_term_family_P1_P6_P7_P8_promotes_P8_extreme_value_null_meta_MM_STANDARD_2026-07-04",
    "name": "META: paired trials MANDATORY for arm-comparison max/range discriminators — unpaired (independent salts) manufacture phantom cross-terms; require shared items/salts across arms OR a data-driven binomial extreme-value null at pre-reg. (MM_STANDARD; retroactive to regime-map family)",
    "corpus": "meta",
    "tier": "T4",
    "kind": "methodology_rule",
    "description": (
        "RULE (strengthens + promotes the P8 MM_TENTATIVE extreme-value-null calibration meta): any cell "
        "that compares mechanisms/arms via a MAX-or-RANGE statistic of a per-arm metric MUST either (a) use "
        "PAIRED trials — shared items/corruptions/salts across the compared arms so common instance noise "
        "cancels — OR (b) gate the discriminator threshold against a DATA-DRIVEN binomial extreme-value "
        "null (Monte Carlo with each cell's own p and TR). Unpaired designs (independent salt per arm) turn "
        "the range of k iid Binomial(TR,p)/TR draws into a NOISE FLOOR that at small TR (~100) reaches "
        "0.10-0.13 and is routinely MISLABELED as arm/mechanism moderation. Paired trials remove instance "
        "noise for free and typically tighten the null by >2x. "
        "DECISIVE CASE STUDY (Probe 1 storage_x_cleanup, this batch): TR=100 UNPAIRED range 0.09-0.12 at "
        "BUNDLED read as a CG_META regime-conditional cross-term; the TR=100 range actually sits BELOW its "
        "own binomial extreme-value null (z=-0.62/-1.11/-1.46); TR=400 unpaired tracks the floor DOWN to "
        "0.075; and the TR=400 PAIRED design gives range EXACTLY 0.0000 on all 36 cells (z=-8.88) — proving "
        "the mechanisms are argmax-degenerate and the entire 'moderation' was unpaired sampling noise. "
        "SECOND CASE (P8 F x CLEANUP, 2026-07-04): same failure mode, z=0.40 vs extreme-value null, already "
        "demoted MM_STANDARD->MIDDLE_BAND. "
        "TIERING: MM_STANDARD, not MM_TENTATIVE — the paired-trials mandate here is DIRECTLY PROVEN by "
        "experiment (paired range provably 0), not inferred, and it is now the second independent regime-map "
        "family catch. It composes with and promotes the P8 extreme-value-null MM_TENTATIVE meta. "
        "RETROACTIVE SCOPE: the whole stage1 regime-map mechanism-moderation cross-term family (P1 demoted "
        "this batch; P8 demoted; P6v2/P7v2 already MIDDLE_BAND and near-certain same artifact) was gated on "
        "unpaired max/range at TR=100 without a noise floor. A family SCHEMA-VET sweep + TR>=400 PAIRED "
        "re-run is the correct revival, NOT a permutation test on the underpowered data. "
        "SCHEMA-VET GATE (adds to pre-dispatch checklist): for any arm-comparison max/range discriminator, "
        "REQUIRE paired trials in the design OR an MC extreme-value null threshold in the prereg; reject "
        "otherwise. PROMOTION TO CG_META: when this gate is wired into SCHEMA-VET as a hard reject."
    ),
    "aliases": ["meta_paired_trials_mandatory_arm_comparison", "meta_unpaired_phantom_cross_term"],
    "metadata": {
        "verified_off_data": True,
        "verified_ts": TS_ISO,
        "verifier": "hdi_skunkworks",
        "cert_status": "mm_standard_methodology_rule",
        "cert_class": "MM_STANDARD_META_RULE_paired_trials_mandatory_arm_comparison",
        "case_study_primary": {"cell": ANCHOR,
                               "tr100_unpaired_range": [0.09, 0.10, 0.12],
                               "tr100_null_z": [-0.62, -1.11, -1.46],
                               "tr400_paired_range": 0.0, "tr400_paired_z_mean": -8.88},
        "case_study_secondary": {"cell": "stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1", "z": 0.40},
        "composes_with_atoms": ["meta::T4/META_extreme_value_discriminator_thresholds_must_be_calibrated_against_max_statistic_null (P8)"],
        "promotes_atom": "meta::T4/META_extreme_value_null_calibration (P8 MM_TENTATIVE -> supported by 2nd catch + decisive paired proof)",
        "retroactive_scope": ["P1", "P6v2", "P7v2", "P8"],
        "memory_rule_ref": "C:/Users/marsh/.claude/projects/d--AI/memory/feedback_paired_trials_mandatory_for_arm_comparison_discriminators_2026-07-04.md",
        "promotion_criterion": "CG_META when wired into SCHEMA-VET as hard reject gate",
        "cross_arc_overlap_check_2026_07_01_USER_locked": "composes/promotes existing P8 EV-null meta; distinct stronger paired-trials mandate; not a duplicate",
        "cert_increment_delta": 1
    }
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
    # verify-load + integrity: every line parses, target id present exactly once
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


def ledger_append(atom, session_tag, extra=None, ledger_path=CERT_LEDGER):
    entry = {
        "ts": TS,
        "ts_iso": TS_ISO,
        "atom_id": atom["id"],
        "corpus": atom["corpus"],
        "cert_status": atom["metadata"].get("cert_status"),
        "cert_class": atom["metadata"].get("cert_class"),
        "cert_increment_delta": atom["metadata"].get("cert_increment_delta", 0),
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_probe1_cross_term_paired_reaudit",
        "landed_VET_session": session_tag,
    }
    if extra:
        entry.update(extra)
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
    tag = "2026-07-04_probe1_cross_term_paired_reaudit_demote_split_and_paired_trials_meta"

    n = a5_append(MATH_ATOMS, atom_1_probe1_cg_demote)
    print(f"[atomize] (1) math Probe1 CG_META DEMOTE appended; math lines={n}")
    ledger_append(atom_1_probe1_cg_demote, tag,
                  extra={"amends_atom": PROBE1_CG_ID, "action": "DEMOTE"})

    n = a5_append(MATH_ATOMS, atom_2_mm_confirmatory_demote)
    print(f"[atomize] (2) math MM_STANDARD confirmatory DEMOTE appended; math lines={n}")
    ledger_append(atom_2_mm_confirmatory_demote, tag,
                  extra={"amends_atom": PROBE1_MM_ID, "action": "DEMOTE"})

    n = a5_append(MATH_ATOMS, atom_3_split_storage_main_effect)
    print(f"[atomize] (3) math SPLIT-A storage main effect CG confirmatory (delta 0) appended; math lines={n}")
    ledger_append(atom_3_split_storage_main_effect, tag)

    n = a5_append(MATH_ATOMS, atom_4_split_measured_mechanism)
    print(f"[atomize] (4) math SPLIT-B MEASURED_MECHANISM argmax-degeneracy appended; math lines={n}")
    ledger_append(atom_4_split_measured_mechanism, tag)

    n = a5_append(META_ATOMS, atom_5_meta_paired_trials)
    print(f"[atomize] (5) meta paired-trials MANDATORY MM_STANDARD appended; meta lines={n}")
    ledger_append(atom_5_meta_paired_trials, tag)

    print("[atomize] DONE 5 atoms + 5 ledger entries; A5-gated (tmp+os.replace+verify-load+json-integrity); matching TS_ISO")
    print("[atomize] NET CERT DELTA: CG -1 (Probe1 CG_META demote), MM +1 (SPLIT-B MEASURED_MECHANISM +1, meta paired-trials +1, MM confirmatory demote -1); SPLIT-A survivor delta 0")
