"""
A5-gated atomization -- Skunkworks landed-VET 2026-07-05.
THREE FULLs (generation RNS/CRT HARD_PASS, integration HARD_v2 HARD_FAIL,
generalization reframe MIDDLE_BAND) + ONE META (best-of-slot paired-rms phantom).
AUDIT-ONLY. Every headline number RE-COMPUTED off each cell's own metrics.json
(.venv) -- verified_off_data via off-disk recompute, NOT verdict-report.

BATCH CONTENTS (4 atoms, matching TS_ISO):
  (1) math CHAIN_GRADE (envelope-extension) -- generation_decoder_rns_crt_highvocab_v1.
      RNS/CRT sub-block decode holds exact-ordered 1.000 cv=0.000 to V=65536/D=26 where
      the CORRELATED single-block cliffs (0.16). SCOPE BAKED IN: RNS *matches* the IID
      ceiling (single_synth=1.000, no cliff), does NOT beat single-block in general.
      Real wins = (a) ~528x codebook compression (124 sum-of-moduli codes for V_eff 70520),
      (b) correlation-immunity BY CONSTRUCTION (residue labels non-semantic -> decorrelated,
      grid-cell property). scram control 0.000 (CRT load-bearing, non-vacuous). CG +1.
  (2) math HARD_FAIL (HF_STRUCTURAL_BOUND, glass-box-POSITIVE) -- integration ..._HARD_v2.
      Co-trained LINEAR bridge does NOT beat parameter-free symbolic cleanup at hard regime
      (margin=-0.706). Positive control clears (stored_direct=1.000 >> 0.7 floor) => genuine
      substantive negative, task solvable, NOT test-design failure. Broken/randproj collapse
      (rails fire); sym=0.806 in [0.15,0.9] (not saturation-vacuous). FINDING: reason->generate
      composition is EFFECTIVELY SYMBOLIC (NN-argmax attractor cleanup re-emits a clean code);
      learned linear bridge emits a noisy code, two-slot gating amplifies it. SCOPE: linear
      bridge; MLP/nonlinear denoiser untested (revival). Composes with v1 easy-regime CG. HF +1.
  (3) math MIDDLE_BAND -- schema_relation_hitsatk_mrr_reframe_v1.
      Filtered-rank reframe recovers REAL partial signal (REAL>SHUFFLED at every slot/metric,
      synth null clean, synth signal fires) BUT the "best filtered Hits@10 rms=0.653" headline
      is a BEST-OF-SLOT PHANTOM: REAL Hits@10~0.75 is IDENTICAL across FROZEN/JOINT/KNN; the rms
      differs ONLY because the JOINT-SHUFFLED arm collapses (0.100) while FROZEN/KNN shuffled
      retain the popularity trap (0.578/0.556). Best-of-slot selects the collapsed-baseline slot.
      FAIR popularity-controlled lift = FROZEN/KNN Hits@10 rms ~0.17-0.20 (BELOW the 0.20 gate);
      rank-1 fair lift ~0.087 (== prior atom's V300 exact-match rms, entropy ceiling unchanged).
      MIDDLE_BAND CONFIRMED (if anything MORE middle than headline). Refines the prior entropy-
      ceiling MM; redirect = trained hard-negative mining. MB +1.
  (4) meta META_RULE (auditor discipline) -- best-of-slot over a paired-rms (real-minus-shuffled)
      discriminator can INFLATE the apparent lift when one scorer slot's control collapses while
      others retain a structural baseline; anchor on the popularity-robust slot's absolute lift.

NET CERT DELTA (this batch): CG +1, HF +1, MB +1, META +1 (meta CERT-neutral).
DEMOTE: none (VET1/VET2 anchors held no prior cert; VET3 refines-not-supersedes prior MM).
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

SESSION_TAG = "2026-07-05_rns_crt_CG_integration_symbolic_HF_generalization_reframe_MB_landed_VET_batch"

# Parent atoms (composition; surfaced by concept-overlap check + ledger scan).
PARENT_GEN_CG = ("math::CHAIN_GRADE_generation_decoder_native_GSBC_block_local_sparse_resonator_round_trips_"
                 "REAL_native_GSBC_EXPAND2X_fillers_PERFECTLY_exact_ordered_1p000_cv0_across_full_envelope_"
                 "V256_to_8192_at_D3_D6_and_V1024_at_D12_and_0p9889_at_V1024D26_3seed_ENCODING_MISMATCH_PROVEN_"
                 "dense_bipolar_BSC_full_resonator_0p000_on_SAME_GSBC_fillers_vs_1p000_on_iid_synth_NON_VACUOUS_"
                 "noorder_ctrl_0p000_and_dense_gsbc_fullreso_0p000_collapse_dense_synth_1p000_ceiling_PLUS_"
                 "MEASURED_capacity_boundary_at_V8192D26_exact_0p856_3seed_mean_reconciled_with_sparse_Hebbian_"
                 "law_Vmax_0p7n_over_a_ln_inv_a_cliff_at_V_over_Vmax_2p9x_holds_below_1x_block_local_is_brain_"
                 "grounded_Sparse_Block_Codes_not_a_partition_cheat_positions_known_by_construction_for_"
                 "generation_decode_3seed_FULL_N8192_K192_2026-07-05")
PARENT_INTEGRATION_CG = ("math::CHAIN_GRADE_integration_end_to_end_substrate_loop_perceive_store_reason_bridge_"
                         "generate_COMPOSES_at_easy_regime_D3_single_hop_V1024_cotrained_AND_symbolic_bridge_"
                         "end2end_1p000_broken_reasoning_and_naive_randproj_collapse_to_0p000_discrim_gap_1p000_"
                         "reasoning_hop_LOAD_BEARING_sever_unbind_role_to_chance_bit_agree_0p4987_BUT_SCOPE_"
                         "HONEST_end2end_EQUALS_object_slot_acc_because_subj_rel_handed_CLEAN_so_it_is_OBJECT_"
                         "SLOT_recovery_NOT_3_slot_compositional_triple_and_symbolic_cleanup_TIES_cotrained_so_"
                         "cotrained_bridge_NOT_shown_uniquely_necessary_advantage_only_vs_naive_randproj_bolt_on_"
                         "cone_0p51_is_BGE_anisotropy_not_chance_harder_task_0p78_bit_agree_gives_perfect_argmax_"
                         "over_V1024_at_N8192_3seed_FULL_2026-07-05")
PARENT_SCHEMA_MM = ("math::MEASURED_MECHANISM_inductive_relational_transfer_via_content_conditioned_SCORER_"
                    "bilinear_reaches_USEFUL_MAGNITUDE_rms_ge_0p2075_ONLY_in_a_NARROW_smallest_vocabulary_"
                    "regime_NOT_from_scaling_headline_HARD_PASS_is_an_ENVELOPE_MAX_single_cell_crossing_1_of_56_"
                    "semantic_SCORER_cells_V100_CausesDesire_bge_semantic_real_ind_0p2311_sd0p0139_minus_shuf_"
                    "0p0178_eq_rms_0p2133_3seed_cv0p060_STABLE_but_margin_above_bar_only_plus0p0058_and_runner_"
                    "up_0p1489_gap_plus0p064_isolated_peak_the_SYSTEMATIC_SCALING_AXES_PLATEAU_WELL_BELOW_BAR_"
                    "M_scaling_mop_ladder_MOP3000_0p109_df_scan_DF768_0p098_steps_scan_ST6000_0p087_the_ONLY_"
                    "axis_producing_the_crossing_is_VOCABULARY_and_it_goes_DOWNWARD_V100_0p213_V300_0p087_V1000_"
                    "0p038_monotone_steep_so_crossing_is_TASK_EASING_not_capability_scaling_AtLocation_NEVER_"
                    "crosses_0p149_gsbc_NEVER_crosses_0p144_binding_constraint_is_the_CANDIDATE_COUNT_one_to_"
                    "many_ENTROPY_CEILING_V_axis_NOT_under_parameterization_DerivedFrom_surface_negative_"
                    "baseline_watchdog_correctly_excluded_crosses_15of16_up_to_0p871_at_V100_confirms_mechanism_"
                    "learns_SURFACE_patterns_4x_to_6x_stronger_than_semantic_non_vacuous_synth_content_GLOBAL_"
                    "0p035_vs_SCORER_0p207_adv_0p172_not_saturated_bind_roundtrip_1p000_arms_differ_8640of8640_"
                    "units_shuffle_at_chance_CORRECTS_cell_self_verdict_HARD_PASS_scaling_reaches_useful_"
                    "magnitude_to_MEASURED_MECHANISM_genuine_but_narrow_RESOLVES_prior_MM_dual_hypothesis_it_is_"
                    "the_ENTROPY_CEILING_not_data_starvation_3seed_FULL_N8192_seeds7_13_19_2026-07-05")

# ---------------------------------------------------------------------------
# ATOM 1 -- GENERATION RNS/CRT (math, CHAIN_GRADE envelope-extension)
# ---------------------------------------------------------------------------
atom_rns = {
    "id": ("math::CHAIN_GRADE_generation_decoder_RNS_CRT_subblock_decomposition_holds_exact_ordered_1p000_"
           "cv0_to_V65536_D26_where_CORRELATED_single_block_CLIFFS_0p16_gap_0p840_3seed_ENVELOPE_EXTENSION_"
           "SCOPE_HONEST_RNS_MATCHES_the_IID_ceiling_single_synth_1p000_NO_cliff_does_NOT_beat_single_block_"
           "IN_GENERAL_the_win_is_TWO_FOLD_a_528x_codebook_compression_124_sum_of_moduli_codes_40_41_43_"
           "represent_V_eff_70520_product_of_moduli_vs_65536_dense_entries_and_b_CORRELATION_IMMUNITY_BY_"
           "CONSTRUCTION_residue_labels_non_semantic_so_decorrelated_grid_cell_property_the_single_corr_cliff_"
           "0p693_0p48_0p32_0p213_0p16_across_V8192_to_65536_is_a_CORRELATION_artifact_confirmed_by_iid_"
           "single_synth_holding_1p000_at_every_V_scram_residue_control_collapses_0p000_so_CRT_binding_is_"
           "LOAD_BEARING_non_vacuous_D16_boundary_single_corr_1p000_no_cliff_rns_matches_D32_boundary_single_"
           "corr_0p027_heavy_cliff_rns_holds_1p000_3seed_FULL_N8192_seeds7_13_19_2026-07-05"),
    "name": ("MATH CHAIN_GRADE (envelope-extension): RNS/CRT sub-block decode holds exact-ordered=1.000 cv=0.000 "
             "to V=65536/D=26 where the CORRELATED single-block cliffs (0.16, gap=0.840). SCOPE HONEST -- RNS "
             "MATCHES the IID ceiling (single_synth=1.000, NO cliff), does NOT beat single-block in general. "
             "Win is two-fold: (a) ~528x codebook compression (124 sum-of-moduli codes 40+41+43 represent "
             "V_eff=70520=40*41*43 vs 65536 dense entries); (b) correlation-immunity BY CONSTRUCTION (residue "
             "labels non-semantic -> decorrelated, grid-cell property). scram residue control 0.000 (CRT "
             "load-bearing, non-vacuous)."),
    "corpus": "math",
    "tier": "CHAIN_GRADE",
    "kind": "experiment_landed_vet",
    "cert_status": "chain_grade_envelope_extension_rns_crt_high_vocab_correlation_immune_compressed_decode_matches_iid_ceiling_not_beats_single_block_scope_honest",
    "cert_class": "generation_rns_crt_subblock_decomposition_correlation_immune_compressed_high_vocab_ordered_decode_envelope_extension_of_block_local_generation",
    "description": (
        "LANDED-VET of exp_generation_decoder_rns_crt_highvocab_v1 (self-verdict HARD_PASS, run_mode=full, "
        "N=8192, F_SPARSE=0.02, R_MODULI=3, 3 seeds [7,13,19], 84 units, expected 84, cardinality_ok, "
        "arms_differ_verified, scram_collapsed=True; commit 4c7088694). "
        "AUDITOR INDEPENDENT OFF-DISK RECOMPUTE (recomputed every headline off arms/efficiency/per_unit, did "
        "NOT read the verdict_msg): ALL numbers reproduce EXACTLY. "
        "ENVELOPE V65536D26: rns_crt exact_ordered per-seed [1.0,1.0,1.0] cv=0.000; single_synth(IID)=1.000 "
        "(NO cliff); single_corr=0.160 (mean of [0.16,0.12,0.20]); rns_scram=0.000; gap(rns-single_corr)=0.840. "
        "CORRELATED-CLIFF sweep D26 (single_corr exact_ordered): V8192=0.693, V16384=0.48, V32768=0.32, "
        "V49152=0.213, V65536=0.16 (monotone cliff); rns_crt holds 1.000 at EVERY V; iid single_synth holds "
        "1.000 at EVERY V (so the cliff is a CORRELATION artifact, not a vocab/capacity limit). "
        "EFFICIENCY V65536: moduli [40,41,43], 40*41*43=70520=M_effective_vocab, 40+41+43=124 rns_codebook_"
        "entries vs 65536 single_codebook_entries, 65536/124=528.52x codebook compression (all arithmetic "
        "re-derived and matches disk). "
        "BOUNDARY axes: D16 -- single_corr=1.000 (correlation stays high at low D, NO cliff) and rns matches "
        "1.000; D32 -- single_corr=0.0267 (heavy cliff, corr collapses) and rns still holds 1.000. So RNS is "
        "INVARIANT to the correlation/D axis while the single-block degrades with it. "
        "MECHANISM: RNS/CRT sub-block decomposition -- a symbol is stored as residues (r mod m_i) across R=3 "
        "disjoint sub-block codebooks; effective vocab = product(moduli) reached with sum(moduli) codes. "
        "Residue labels are NON-SEMANTIC, so the per-symbol residue pattern is decorrelated regardless of the "
        "semantic correlation of the underlying symbols -- this is the grid-cell / modular-code property that "
        "makes decode correlation-IMMUNE. "
        "NON-VACUITY: the rns_scram arm (residue binding scrambled) collapses to exact_ordered=0.000 at EVERY "
        "V/D -- the CRT residue structure is genuinely load-bearing, this is NOT a by-construction saturation "
        "(scramble the structure and it dies). iid single_synth=1.000 is the honest POSITIVE-control ceiling "
        "(the ordered-decode metric CAN be 1.000 when content is decorrelated). "
        "SCOPE (load-bearing, baked in so this atom is NEVER mis-cited as 'RNS beats single-block'): RNS/CRT "
        "MATCHES the IID single-block ceiling (both 1.000); it does NOT beat single-block IN GENERAL. Its two "
        "real, distinct wins are: (1) ~528x codebook COMPRESSION (124 residue codes vs 65536 dense entries for "
        "the same V_eff=70520); (2) CORRELATION-IMMUNITY -- it holds 1.000 where the CORRELATED (realistic) "
        "single-block cliffs to 0.16. The 'pushes past the cliff' framing is TRUE strictly against the "
        "correlated/realistic baseline, and the cell's own verdict_msg states this honestly (it cites the iid "
        "ceiling as the proof the cliff is a correlation artifact). No over-claim to trim; scope pinned. "
        "TIER RATIONALE: CHAIN_GRADE envelope-extension -- clean controlled result (3 seeds, cv=0.000 on the CG "
        "arm, positive+negative controls both fire, discriminator gap=0.840, cardinality_ok, arms_differ). It "
        "EXTENDS the same-day block-local generation CG (which MEASURED a capacity boundary at V8192D26~0.856 "
        "under the sparse-Hebbian law): RNS decomposition is the mechanism that carries correlation-immune "
        "high-vocab ordered decode past the correlated cliff with a compressed codebook. Composes with, does "
        "NOT supersede, that parent."
    ),
    "aliases": ["generation_rns_crt_high_vocab_correlation_immune_compressed_decode_CG_envelope_extension",
                "residue_number_system_crt_subblock_matches_iid_ceiling_528x_compression_grid_cell_decorrelated"],
    "metadata": {
        "record_class": "experiment_landed_vet_chain_grade_envelope_extension",
        "term_class": "GENERATION_RNS_CRT_SUBBLOCK_CORRELATION_IMMUNE_COMPRESSED_HIGH_VOCAB_ORDERED_DECODE",
        "cert_status": "chain_grade_envelope_extension_rns_crt_matches_iid_ceiling_correlation_immune_528x_compression_scope_honest",
        "cert_class": "generation_rns_crt_subblock_decomposition_correlation_immune_compressed_high_vocab_ordered_decode",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "verified_via": "off-disk recompute of arms/efficiency/per_unit (product+sum of moduli, compression ratio, cliff sweep, cv); reproduced disk EXACTLY; not verdict-report",
        "atomized_by": "skunkworks_landed_VET_2026-07-05_rns_crt_high_vocab_CHAIN_GRADE_envelope_extension",
        "anchor": "generation_decoder_rns_crt_highvocab_v1",
        "cell_commit": "4c7088694",
        "raw_metrics_path": "data/exp_generation_decoder_rns_crt_highvocab_v1/metrics.json",
        "run_mode": "full", "N": 8192, "R_MODULI": 3, "F_SPARSE": 0.02,
        "n_seeds": 3, "seeds": [7, 13, 19], "n_units": 84, "cardinality_ok": True,
        "recompute_off_disk": {
            "envelope_V65536D26": {"rns_crt_exact_ordered": 1.0, "rns_cv": 0.0,
                                    "single_synth_iid_exact_ordered": 1.0, "single_corr_exact_ordered": 0.16,
                                    "rns_scram_exact_ordered": 0.0, "gap": 0.84},
            "single_corr_cliff_sweep_D26": {"8192": 0.693, "16384": 0.48, "32768": 0.32, "49152": 0.213, "65536": 0.16},
            "rns_holds_sweep_D26_all": 1.0, "iid_single_synth_sweep_D26_all": 1.0,
            "efficiency_V65536": {"moduli": [40, 41, 43], "product_M_eff": 70520, "sum_codes": 124,
                                   "single_codebook_entries": 65536, "compression_x": 528.52},
            "boundary_D16": {"single_corr": 1.0, "rns": 1.0, "note": "low-D no cliff, rns matches"},
            "boundary_D32": {"single_corr": 0.0267, "rns": 1.0, "note": "heavy cliff, rns holds"},
            "match_disk": "EXACT",
        },
        "scope_caveat": "RNS MATCHES the IID single-block ceiling (both 1.000); does NOT beat single-block IN GENERAL. Wins = (1) ~528x codebook compression (124 residue codes for V_eff 70520); (2) correlation-immunity by construction (residue labels non-semantic -> decorrelated, grid-cell property). 'Past the cliff' is strictly vs the CORRELATED realistic baseline.",
        "non_vacuity_checks": {
            "negative_control_scram": "rns_scram exact_ordered=0.000 at every V/D -> CRT residue structure load-bearing (not by-construction saturation)",
            "positive_control_iid_ceiling": "single_synth(iid)=1.000 at every V -> ordered-decode CAN be perfect on decorrelated content (honest ceiling)",
            "discriminator": "single_corr cliffs 0.693->0.16 while rns holds 1.000 -> gap=0.84 fires; iid holds -> cliff is correlation artifact not capacity",
        },
        "cross_arc_overlap_check_2026_07_01_USER_locked": "substrate_query 'RNS CRT residue number system sub-block high vocab generation decoder correlation immune codebook compression' -> top experiment/lit hit 0.354 is a LIT note (Kymn et al. 2024 RNS resonator, 5.5x codebook reduction; notes/research_drill_codebook_capacity_negative_2x_2026-06-10.md); 'compression'/'correlation' wordnet at 0.34-0.36. NO prior EXPERIMENT/CERT atom on on-substrate RNS/CRT generation decode. TARGETED EXTENSION: this cell is the empirical on-substrate demonstration (528x compression via sum-of-moduli + correlation-immunity envelope) of the RNS codebook-compression concept the June-10 lit note flagged; NOT a rediscovery of a prior cell.",
        "composes_with_atoms": [PARENT_GEN_CG],
        "composition_note": "COMPOSES WITH (does NOT supersede) the same-day block-local generation CG (parent MEASURED a capacity boundary at V8192D26~0.856 under the sparse-Hebbian Vmax law). This atom shows RNS/CRT sub-block decomposition is the mechanism that carries correlation-immune ORDERED high-vocab decode past the CORRELATED single-block cliff with a ~528x-compressed codebook -- an envelope-extension of the generation capability, not a new standalone claim.",
        "framing_corrections_vs_director_and_cell": "AGREE with cell HARD_PASS and with Director's honest-scope flag (symmetric: no inflation). CONFIRMED off-disk: (i) RNS matches the iid ceiling and does NOT beat single-block in general (single_synth=1.000 does NOT cliff at any V); (ii) the win is correlation-immunity + 528x compression vs the CORRELATED baseline. The atom id/name/scope are written so it can NEVER be mis-cited as 'RNS beats single-block'. No over-claim required trimming -- the cell's verdict_msg already cites the iid ceiling as proof the cliff is a correlation artifact.",
        "expansion_criterion": "Already CHAIN_GRADE within scope. Further work (not required for CG): test RNS/CRT on REAL correlated content encodings (native GSBC / BGE) where the correlation-immunity claim would face genuinely non-synthetic correlation structure; and confirm the compression advantage survives a resonator-network factorization decode (vs the current disjoint-block-index decode).",
        "disposition": "CHAIN_GRADE_generation_rns_crt_correlation_immune_compressed_high_vocab_ordered_decode_matches_iid_ceiling_not_beats_single_block_win_is_528x_compression_plus_correlation_immunity_by_construction",
        "cert_increment_delta": 1,
    },
}

# ---------------------------------------------------------------------------
# ATOM 2 -- INTEGRATION HARD-REGIME (math, HARD_FAIL / HF_STRUCTURAL_BOUND, glass-box positive)
# ---------------------------------------------------------------------------
atom_integration = {
    "id": ("math::HARD_FAIL_STRUCTURAL_BOUND_integration_end_to_end_loop_HARD_regime_co_trained_LINEAR_bridge_"
           "does_NOT_beat_parameter_free_symbolic_cleanup_margin_neg0p706_cot_0p100_sym_0p806_glass_box_POSITIVE_"
           "reason_to_generate_composition_is_EFFECTIVELY_SYMBOLIC_NN_argmax_attractor_cleanup_RE_EMITS_a_CLEAN_"
           "code_the_learned_linear_bridge_emits_a_NOISY_code_and_two_slot_gating_AMPLIFIES_it_positive_control_"
           "stored_direct_1p000_clears_0p7_floor_so_task_SOLVABLE_genuine_substantive_negative_NOT_test_design_"
           "failure_broken_reasoning_0p000_and_naive_randproj_0p000_rails_FIRE_so_not_any_bridge_works_sym_0p806_"
           "in_0p15_0p9_room_NOT_saturation_vacuous_easy_rail_cot_0p828_sym_1p000_margin_neg0p172_per_seed_"
           "margin_negative_all_3_SCOPE_LINEAR_bridge_MLP_nonlinear_denoiser_untested_revival_composes_with_v1_"
           "easy_regime_CHAIN_GRADE_3seed_FULL_N_R1024_N_G8192_2026-07-05"),
    "name": ("MATH HARD_FAIL (HF_STRUCTURAL_BOUND; glass-box POSITIVE): at the hard regime a co-trained LINEAR "
             "bridge does NOT beat parameter-free symbolic cleanup (margin=-0.706; cot=0.100 sym=0.806). "
             "Positive control stored_direct=1.000 (clears 0.7 floor -> task solvable, genuine substantive "
             "negative, NOT test-design failure); broken/randproj collapse to 0.000 (rails fire); sym=0.806 in "
             "[0.15,0.9] (not saturation-vacuous). FINDING: reason->generate composition is EFFECTIVELY "
             "SYMBOLIC -- NN-argmax attractor cleanup re-emits a CLEAN code; the learned linear bridge emits a "
             "NOISY code and two-slot gating amplifies it. SCOPE: linear bridge; MLP/nonlinear denoiser untested."),
    "corpus": "math",
    "tier": "HARD_FAIL",
    "kind": "experiment_landed_vet",
    "cert_status": "honest_negative_hard_fail_structural_bound_learned_linear_bridge_not_load_bearing_composition_is_effectively_symbolic_positive_control_clears_floor_task_solvable",
    "cert_class": "integration_reason_to_generate_composition_effectively_symbolic_nn_argmax_cleanup_suffices_learned_linear_bridge_not_load_bearing_scope_linear",
    "description": (
        "LANDED-VET of exp_integration_end_to_end_loop_bridge_HARD_v2 (self-verdict HARD_FAIL, run_mode=full, "
        "3 seeds [7,13,19], 30 units, expected 30, cardinality_ok, arms_differ_verified; commit 24e840833). "
        "AUDITOR INDEPENDENT OFF-DISK RECOMPUTE (recomputed every headline off regimes/controls/per_seed, did "
        "NOT read the verdict_msg): ALL numbers reproduce EXACTLY. "
        "HARD regime end2end: cotrained_linear=0.100, naive_symbolic=0.8056, margin(cot-sym)=-0.7056; "
        "positive control stored_direct=1.000; broken_reasoning=0.000; naive_randproj=0.000; cv_cotrained=0.236. "
        "EASY-RAIL end2end: cotrained_linear=0.8278, naive_symbolic=1.000, margin=-0.1722. "
        "Per-seed hard: cot [0.0667,0.1167,0.1167] sym [0.8333,0.80,0.7833] -> margin NEGATIVE at every seed "
        "(symbolic wins robustly, not a variance artifact). "
        "DISCRIMINATOR RAILS ALL FIRE: (a) positive control stored_direct=1.000 (both regimes) >> POSCTRL_FLOOR="
        "0.7 -- feeding a clean stored HV straight to the generator makes the loop work perfectly, so the "
        "end-to-end wiring is sound and the task is SOLVABLE; (b) broken_reasoning=0.000 (severed reasoning "
        "collapses -> the reasoning hop is load-bearing); (c) naive_randproj=0.000 (a random-projection bridge "
        "fails -> it is NOT that 'any bridge works'); (d) naive_symbolic hard=0.806 sits inside SYM_ROOM "
        "[0.15,0.90] -- symbolic was DEGRADED into the measurable band, so the comparison is NOT saturation-"
        "vacuous (symbolic had room to be beaten and was not). "
        "POSITIVE-CONTROL-CLEARS-FLOOR discipline (2026-07-01 auditor rule) SATISFIED FIRST: stored_direct=1.000 "
        "clears its own 0.7 floor -> this is a GENUINE SUBSTANTIVE negative, NOT a test-design failure. "
        "ATTRIBUTION: HF_STRUCTURAL_BOUND (scope: LINEAR bridge). The learned co-trained linear bridge is not "
        "load-bearing for the glass-box reason->generate loop. "
        "GLASS-BOX-POSITIVE FINDING (the load-bearing takeaway): the reason->generate composition is EFFECTIVELY "
        "SYMBOLIC. Root cause (from the cell's glassbox_trace, re-read): the SYMBOLIC path runs an NN-argmax "
        "attractor cleanup on the recovered noisy HV and RE-EMITS a CLEAN codeword; the learned LINEAR bridge "
        "emits a NOISY code, and the two-slot (subject+object) gating in the generator AMPLIFIES that residual "
        "noise -- so symbolic ties/beats wherever the loop works at all. Parameter-free symbolic cleanup -> "
        "clean-code SUFFICES; a learned linear map adds noise, not value. "
        "SCOPE (baked in): the negative is scoped to a LINEAR bridge. A NONLINEAR (MLP) denoiser bridge is an "
        "explicit UNTESTED follow-up -- it could in principle match symbolic by learning the snap-to-codeword "
        "nonlinearity; this cell does not test it and does not claim learned bridges are dead in general. "
        "TIER RATIONALE: HARD_FAIL as a clean, well-controlled honest negative for the tested hypothesis "
        "('does a co-trained LINEAR bridge beat parameter-free symbolic cleanup at hard regime?' -> NO, by "
        "-0.706). It simultaneously carries a MEASURED-MECHANISM-flavored POSITIVE (composition holds at hard "
        "regime via symbolic cleanup at 0.806), which is captured in the finding above and by composition with "
        "the v1 easy-regime CG."
    ),
    "aliases": ["integration_hard_regime_learned_linear_bridge_not_load_bearing_composition_is_symbolic_HF",
                "reason_to_generate_effectively_symbolic_nn_argmax_cleanup_suffices_linear_bridge_adds_noise"],
    "metadata": {
        "record_class": "experiment_landed_vet_hard_fail_structural_bound_glass_box_positive",
        "term_class": "INTEGRATION_REASON_TO_GENERATE_COMPOSITION_EFFECTIVELY_SYMBOLIC_LEARNED_LINEAR_BRIDGE_NOT_LOAD_BEARING",
        "cert_status": "honest_negative_hard_fail_structural_bound_learned_linear_bridge_not_load_bearing_composition_effectively_symbolic",
        "cert_class": "integration_reason_to_generate_composition_effectively_symbolic_learned_linear_bridge_not_load_bearing_scope_linear",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "verified_via": "off-disk recompute of regimes/controls/per_seed/glassbox_trace (margin arithmetic, posctrl floor, rail collapse, sym-room, per-seed sign); reproduced disk EXACTLY; not verdict-report",
        "atomized_by": "skunkworks_landed_VET_2026-07-05_integration_HARD_v2_HF_STRUCTURAL_BOUND_glass_box_positive",
        "anchor": "integration_end_to_end_loop_bridge_HARD_v2",
        "cell_commit": "24e840833",
        "raw_metrics_path": "data/exp_integration_end_to_end_loop_bridge_HARD_v2/metrics.json",
        "run_mode": "full", "N_R": 1024, "N_G": 8192, "GEN_SLOTS": 3,
        "n_seeds": 3, "seeds": [7, 13, 19], "n_units": 30, "cardinality_ok": True,
        "recompute_off_disk": {
            "hard": {"cotrained_linear": 0.1, "naive_symbolic": 0.8056, "margin_cot_minus_sym": -0.7056,
                     "stored_direct_posctrl": 1.0, "broken_reasoning": 0.0, "naive_randproj": 0.0,
                     "cv_cotrained": 0.2356},
            "easy": {"cotrained_linear": 0.8278, "naive_symbolic": 1.0, "margin_cot_minus_sym": -0.1722,
                     "stored_direct_posctrl": 1.0},
            "per_seed_hard": {"cot": [0.0667, 0.1167, 0.1167], "sym": [0.8333, 0.80, 0.7833],
                              "margin_negative_all_seeds": True},
            "sym_room_check": "sym hard 0.806 in [0.15,0.90] -> not saturation-vacuous",
            "match_disk": "EXACT",
        },
        "positive_control_check": "stored_direct end2end=1.000 (easy AND hard) clears POSCTRL_FLOOR=0.7 -> loop wiring sound, task SOLVABLE, genuine substantive negative NOT test-design failure. broken=0.000 + randproj=0.000 -> reasoning hop load-bearing AND not-any-bridge-works.",
        "hard_fail_attribution": "HF_STRUCTURAL_BOUND (scope: LINEAR bridge). Learned co-trained linear bridge not load-bearing; parameter-free symbolic NN-argmax cleanup suffices and beats it by 0.706 at hard regime.",
        "glass_box_positive": "reason->generate composition is EFFECTIVELY SYMBOLIC: symbolic re-emits a CLEAN codeword after NN-argmax attractor cleanup; the learned linear bridge emits a NOISY code and two-slot gating amplifies it. Symbolic ties/beats wherever the loop works.",
        "scope_caveat": "LINEAR bridge only. MLP/nonlinear denoiser bridge is an explicit UNTESTED follow-up (could learn the snap-to-codeword nonlinearity). Does NOT claim learned bridges dead in general.",
        "cross_arc_overlap_check_2026_07_01_USER_locked": "substrate_query 'integration end to end loop reason generate bridge symbolic cleanup learned linear not load bearing hard regime' -> top hit 0.264 (below 0.30 threshold): cortex_integration_end_to_end_v1_selftest metrics + nonlinear-readout self-dominance note. Related lineage but sub-threshold; this is the HARD-regime v2 follow-up of the v1 easy-regime CG. Not a rediscovery.",
        "composes_with_atoms": [PARENT_INTEGRATION_CG],
        "composition_note": "COMPOSES WITH (does NOT supersede) the v1 easy-regime CHAIN_GRADE (which already noted symbolic cleanup TIES co-trained and the co-trained bridge was NOT shown uniquely necessary at easy regime). This HARD_v2 STRENGTHENS that scope-honest finding: at the HARD regime the learned linear bridge does not just tie -- it LOSES by 0.706, and symbolic cleanup carries the composition alone (0.806). Confirms the v1 caution that the co-trained bridge is not load-bearing.",
        "framing_corrections_vs_director": "AGREE with Director's framing (symmetric). Director asked to (i) confirm the negative is real + rails fire, and (ii) atomize as the glass-box-positive 'composition is effectively symbolic; learned linear bridge not load-bearing (scope linear)'. CONFIRMED both off-disk: margin=-0.706 robust across all 3 seeds, all four rails fire (posctrl 1.000, broken 0.000, randproj 0.000, sym-room satisfied), and the finding is exactly as framed. Added rigor: positive control clears its 0.7 floor FIRST -> HF_STRUCTURAL_BOUND not HF_TEST_DESIGN_FAILURE.",
        "revival_criteria": [
            "Test a NONLINEAR (MLP) denoiser bridge co-trained on recovered noisy HVs: if it matches/beats symbolic at hard regime, learned bridges become load-bearing for a nonlinear cleanup the linear map cannot express (snap-to-codeword).",
            "OR reframe the loop to NOT require a learned bridge at all -- accept symbolic NN-argmax cleanup as the canonical reason->generate seam (the glass-box-positive reading).",
        ],
        "expansion_criterion": "This HF closes the LINEAR-bridge question. The capability question (does a learned bridge ever beat symbolic at hard regime?) reopens only with the MLP-denoiser follow-up; absent that, symbolic cleanup is the proven seam.",
        "disposition": "HARD_FAIL_STRUCTURAL_BOUND_learned_linear_bridge_not_load_bearing_composition_effectively_symbolic_NN_argmax_cleanup_suffices_scope_linear_MLP_denoiser_untested_revival",
        "cert_increment_delta": 1,
    },
}

# ---------------------------------------------------------------------------
# ATOM 3 -- GENERALIZATION REFRAME (math, MIDDLE_BAND; phantom trim)
# ---------------------------------------------------------------------------
atom_reframe = {
    "id": ("math::MIDDLE_BAND_schema_relation_filtered_rank_hitsatk_mrr_reframe_recovers_REAL_partial_signal_"
           "REAL_gt_SHUFFLED_at_every_slot_synth_null_clean_neg0p007_synth_signal_fires_0p513_BUT_the_best_"
           "filtered_Hits10_rms_0p653_HEADLINE_is_a_BEST_OF_SLOT_PHANTOM_REAL_Hits10_approx_0p75_is_IDENTICAL_"
           "across_FROZEN_0p751_JOINT_0p753_KNN_0p753_the_rms_differs_ONLY_because_the_JOINT_SHUFFLED_arm_"
           "COLLAPSES_0p100_while_FROZEN_KNN_shuffled_retain_the_popularity_trap_0p578_0p556_so_best_of_slot_"
           "SELECTS_the_collapsed_baseline_slot_the_FAIR_popularity_controlled_lift_is_FROZEN_KNN_Hits10_rms_"
           "0p173_0p198_BELOW_the_0p20_gate_and_rank1_fair_lift_only_0p087_EQUALS_prior_atoms_V300_exact_match_"
           "rms_entropy_ceiling_UNCHANGED_expansion_criterion_NOT_met_only_CausesDesire_wins_on_the_JOINT_"
           "phantom_the_recovery_is_GENUINE_at_higher_k_one_to_many_single_answer_was_ILL_POSED_but_rank1_"
           "precision_remains_GATED_by_hubness_popularity_redirect_trained_hard_negative_mining_3seed_FULL_"
           "N8192_648units_2026-07-05"),
    "name": ("MATH MIDDLE_BAND: filtered-rank (Bordes Hits@k/MRR) reframe recovers REAL partial signal "
             "(REAL>SHUFFLED at every slot/metric; synth null clean -0.007; synth signal fires 0.513) -- BUT the "
             "'best filtered Hits@10 rms=0.653' headline is a BEST-OF-SLOT PHANTOM. REAL Hits@10~0.75 is "
             "IDENTICAL across FROZEN/JOINT/KNN; the rms differs ONLY because the JOINT-SHUFFLED arm collapses "
             "(0.100) while FROZEN/KNN shuffled retain the popularity trap (0.578/0.556). FAIR popularity-"
             "controlled lift = FROZEN/KNN Hits@10 rms ~0.17-0.20 (BELOW the 0.20 gate); rank-1 fair lift ~0.087 "
             "(= prior atom's V300 exact-match rms, entropy ceiling UNCHANGED). Genuine top-k recovery; rank-1 "
             "still gated by hubness/popularity."),
    "corpus": "math",
    "tier": "MIDDLE_BAND",
    "kind": "experiment_landed_vet",
    "cert_status": "middle_band_partial_rank_recovery_real_but_headline_best_of_slot_phantom_fair_lift_below_gate_rank1_at_entropy_ceiling",
    "cert_class": "generalization_filtered_rank_reframe_genuine_topk_partial_recovery_rank1_gated_by_hubness_popularity_headline_inflated_by_joint_shuffled_collapse",
    "description": (
        "LANDED-VET of exp_schema_relation_hitsatk_mrr_reframe_v1 (self-verdict MIDDLE_BAND, run_mode=full, "
        "N=8192, 3 seeds [7,13,19], 648 units expected/counted, 0 failed, cardinality_ok, arms_differ_verified, "
        "bind_roundtrip=1.000; commit 9cf4cc8c9). AUDITOR CONFIRMS MIDDLE_BAND but with a MATERIAL DOWNWARD "
        "FRAMING CORRECTION on the headline (symmetric anti-negativity: the finding survives, the number is "
        "trimmed). "
        "METRIC DEFINITION (verified in source, lines 760/981): 'rms' = REAL_filt - SHUFFLED_filt (Real Minus "
        "Shuffled, a PAIRED-differenced discriminator, Bordes-filtered protocol). "
        "AUDITOR OFF-DISK RECOMPUTE of the raw ABSOLUTE per-slot REAL and SHUFFLED (from cells_aggregate, the "
        "load-bearing phantom check flagged by this cell's lineage): for the reported win V300 CausesDesire "
        "bge_semantic (inductive, filtered Hits@10): FROZEN REAL=0.751 SHUF=0.578 rms=+0.173; JOINT REAL=0.753 "
        "SHUF=0.100 rms=+0.653; KNN REAL=0.753 SHUF=0.556 rms=+0.198. gsbc mirrors it (JOINT REAL=0.709 "
        "SHUF=0.102 rms=+0.607; FROZEN rms=+0.158; KNN rms=+0.207). "
        "THE PHANTOM (load-bearing): the REAL filtered Hits@10 is ~0.75 and IDENTICAL across all three slots -- "
        "the REAL scorer is equally good everywhere. The reported 'best 0.653' rms is the JOINT slot, and it is "
        "large ONLY because the JOINT-SHUFFLED arm COLLAPSES to 0.100 (a co-trained autograd model trained on "
        "RANDOM labels overfits noise and loses the popularity prior), while the FROZEN (ridge) and KNN "
        "(cosine-vote) shuffled arms RETAIN the popularity trap at ~0.56-0.58. best-of-{FROZEN,JOINT} therefore "
        "SELECTS the slot whose control collapses hardest, INFLATING the differenced lift. This is exactly the "
        "'shuffled-collapse-phantom' risk the cell's lineage carried, and it is REAL here. "
        "FAIR (popularity-robust) LIFT: the honest, popularity-controlled Hits@10 lift is the FROZEN/KNN rms "
        "~0.17-0.20 -- BOTH BELOW the 0.20 gate. At rank-1 the fair lift is even smaller: FROZEN Hits@1 REAL="
        "0.618 SHUF=0.531 rms=+0.087 -- and +0.087 EXACTLY reproduces the prior MEASURED_MECHANISM atom's V300 "
        "CausesDesire exact-match rms (0.087). So rank-1 precision is UNCHANGED at the one-to-many entropy "
        "ceiling; the 'recovery' is entirely at higher k (the true object lands in the top-10 more often than "
        "popularity predicts, but rarely at rank-1). "
        "THE 'WIN' IS PHANTOM-DRIVEN: the only slot_clears_both (Hits@10 rms>=0.20 AND MRR rms>=0.15) is the "
        "JOINT slot (0.653/0.248), i.e. the collapsed-baseline slot. NO popularity-robust slot clears the gate "
        "(FROZEN Hits@10 rms=0.173 fails; KNN=0.198 fails). expansion_criterion_met=False (only CausesDesire "
        "wins, and that win rests on the phantom). AtLocation never crosses. "
        "DISCRIMINATOR IS CLEAN in the 'is there ANY signal' sense (verified): REAL>SHUFFLED at every slot and "
        "metric; synth_rank_null hits10_rms=-0.0067 (clean, invents no false signal); synth_rank_signal "
        "hits10_rms=+0.513 (fires on a clean planted map). So the partial recovery is a REAL absolute effect, "
        "NOT a paired-rms artifact of the null. The artifact is confined to the HEADLINE MAGNITUDE via "
        "best-of-slot selection, not to the existence of signal. "
        "HONEST TIER: MIDDLE_BAND (CONFIRM) -- if anything the phantom makes it MORE middle than the headline. "
        "LOAD-BEARING NUMBER: REAL filtered Hits@10 ~0.75 vs a popularity baseline ~0.57 => fair lift ~0.17-0.20 "
        "(below the 0.20 gate); rank-1 fair lift ~0.087 (entropy ceiling). "
        "FINDING: generalization = GENUINE partial rank recovery. The one-to-many single-answer exact-match "
        "framing was ILL-POSED (a relation with many valid objects cannot put the one held-out object at rank-1 "
        "against equally-valid + popular distractors); reframing to top-k recovers real signal above chance and "
        "above popularity at higher k. But PRECISE rank-1 remains GATED by hubness/label-prior. Redirect: "
        "trained HARD-NEGATIVE mining -- the failure is precisely the inability to separate the true object "
        "from POPULAR distractors at rank-1, which is what hard-neg mining targets."
    ),
    "aliases": ["schema_relation_filtered_rank_reframe_partial_recovery_MIDDLE_BAND_headline_phantom_trimmed",
                "generalization_topk_recovery_rank1_entropy_ceiling_best_of_slot_joint_shuffled_collapse_phantom"],
    "metadata": {
        "record_class": "experiment_landed_vet_middle_band_headline_downward_corrected",
        "term_class": "GENERALIZATION_FILTERED_RANK_REFRAME_PARTIAL_TOPK_RECOVERY_RANK1_ENTROPY_CEILING_HEADLINE_PHANTOM",
        "cert_status": "middle_band_partial_rank_recovery_real_headline_best_of_slot_phantom_fair_lift_below_gate_rank1_at_entropy_ceiling",
        "cert_class": "generalization_filtered_rank_reframe_genuine_topk_recovery_rank1_gated_hubness_popularity_headline_inflated_by_joint_shuffled_collapse",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "verified_via": "off-disk recompute of raw absolute per-slot REAL/SHUFFLED from cells_aggregate + metric-def read from source (rms=REAL-SHUFFLED); phantom isolated; not verdict-report",
        "atomized_by": "skunkworks_landed_VET_2026-07-05_schema_relation_reframe_MIDDLE_BAND_phantom_trim",
        "anchor": "schema_relation_hitsatk_mrr_reframe_v1",
        "cell_commit": "9cf4cc8c9",
        "raw_metrics_path": "data/exp_schema_relation_hitsatk_mrr_reframe_v1/metrics.json",
        "run_mode": "full", "N": 8192,
        "n_seeds": 3, "seeds": [7, 13, 19], "n_units": 648, "cardinality_ok": True,
        "recompute_off_disk": {
            "metric_definition": "rms = REAL_filt - SHUFFLED_filt (paired-differenced, Bordes-filtered)",
            "V300_CausesDesire_bge_absolute_Hits10": {
                "FROZEN": {"REAL": 0.751, "SHUF": 0.578, "rms": 0.173},
                "JOINT": {"REAL": 0.753, "SHUF": 0.100, "rms": 0.653},
                "KNN": {"REAL": 0.753, "SHUF": 0.556, "rms": 0.198}},
            "V300_CausesDesire_bge_Hits1": {"FROZEN": {"REAL": 0.618, "SHUF": 0.531, "rms": 0.087}},
            "V300_CausesDesire_gsbc_JOINT_Hits10": {"REAL": 0.709, "SHUF": 0.102, "rms": 0.607},
            "headline_best_hits10_rms": 0.6533, "headline_best_mrr_rms": 0.2479,
            "fair_popularity_robust_Hits10_rms": "0.173 (FROZEN) / 0.198 (KNN) -- both < 0.20 gate",
            "rank1_fair_lift": "0.087 (== prior MM atom V300 exact-match rms; entropy ceiling unchanged)",
            "synth_rank_null_hits10_rms": -0.0067, "synth_rank_signal_hits10_rms": 0.5133,
            "expansion_criterion_met": False, "win_rels": ["CausesDesire"], "win_encs": ["bge_semantic", "gsbc"],
            "match_disk": "EXACT",
        },
        "phantom_diagnosis": "best-of-{FROZEN,JOINT} selects the JOINT slot whose SHUFFLED control collapses (0.100) because a co-trained autograd model overfits random labels and loses the popularity prior; FROZEN/KNN shuffled retain the popularity trap (~0.56-0.58). REAL Hits@10 is ~0.75 identical across slots -> the 0.653 rms is baseline-collapse-driven, not REAL-superiority-driven. The only gate-clearing slot IS the phantom slot; no popularity-robust slot clears 0.20.",
        "over_claim_trimmed": "TRIM 'best filtered Hits@10 rms=0.653' as phantom-inflated. Re-anchor on the fair popularity-controlled lift: REAL Hits@10 ~0.75 vs popularity ~0.57 => ~0.17-0.20 (below gate); rank-1 fair lift ~0.087 (entropy ceiling).",
        "discriminator_clean_check": "REAL>SHUFFLED at every slot/metric; synth_rank_null=-0.007 (clean); synth_rank_signal=+0.513 (fires). Partial recovery is a REAL absolute effect; the artifact is confined to headline MAGNITUDE via best-of-slot, not to signal existence.",
        "cross_arc_overlap_check_2026_07_01_USER_locked": "substrate_query 'schema relation filtered rank hits at k mrr partial recovery one to many hubness popularity generalization gated' -> top hit 0.318 is a failure-modes note chunk (Zipf/extreme-skew relation distribution) + GO/framenet at 0.29. NO prior experiment atom above 0.30 on the reframe, but ledger-scan surfaces the DIRECT parent MM (TEM scorer scaleup v2, exact-match, same V300 CausesDesire 0.087). Targeted reframe of that exact-match MM, not a rediscovery.",
        "composes_with_atoms": [PARENT_SCHEMA_MM],
        "composition_note": "COMPOSES WITH / REFINES (does NOT supersede) the prior TEM-scorer-scaleup MEASURED_MECHANISM (which diagnosed a one-to-many ENTROPY CEILING: V-axis crossing goes DOWNWARD V100 0.213 -> V300 0.087 -> V1000 0.038; rank-1 crossing was task-easing not scaling). This reframe REFINES it: moving from exact-match (rank-1) to top-k (filtered Hits@10) recovers REAL partial signal above the entropy ceiling at higher k (fair rms ~0.17-0.20), while rank-1 stays pinned at 0.087 (the SAME entropy ceiling). The apparent gate-clearing 0.653 is a best-of-slot phantom, not a break of the ceiling.",
        "framing_corrections_vs_director": "Director flagged EXACTLY this risk ('DO NOT let best 0.653 over-read... verify the reported lift is REAL-absolute not paired-rms-gamed'). VALIDATED: the 0.653 IS paired-rms-gamed via best-of-slot landing on the collapsed-JOINT-shuffled baseline. The fair popularity-controlled lift is ~0.17-0.20 (below gate) and rank-1 is unchanged at 0.087. Director's MIDDLE_BAND tier and 'one-to-many single-answer ill-posed; rank-1 gated by hubness/label-prior; trained hard-neg mining is the redirect' are all CONFIRMED and, if anything, the phantom makes the finding MORE middle than the headline suggested.",
        "revival_criteria": [
            "Trained HARD-NEGATIVE mining: sample popular/near-neighbor distractors as negatives during scorer training to sharpen rank-1 separation of the true object from popular decoys (directly targets the hubness/label-prior failure).",
            "Richer/structured content encoding so the true object is distinguishable from equally-valid siblings at rank-1 (attacks the one-to-many entropy ceiling at its source).",
        ],
        "expansion_criterion": "PROMOTES toward CG iff a popularity-ROBUST slot (FROZEN or KNN, not the collapse-prone JOINT) clears Hits@10 rms>=0.20 AND MRR rms>=0.15 on >=2 relations x >=2 encoders at V>=300 -- i.e. a real lift that does NOT depend on the shuffled control collapsing. DEMOTES if even the ~0.17-0.20 FROZEN/KNN lift fails to survive a fair popularity-matched baseline.",
        "disposition": "MIDDLE_BAND_generalization_genuine_topk_partial_recovery_but_headline_0p653_is_best_of_slot_phantom_fair_lift_0p17_to_0p20_below_gate_rank1_at_entropy_ceiling_0p087_redirect_trained_hard_negative_mining",
        "cert_increment_delta": 1,
    },
}

# ---------------------------------------------------------------------------
# ATOM 4 -- META RULE (meta corpus, CERT-neutral auditor discipline)
# ---------------------------------------------------------------------------
atom_meta = {
    "id": ("meta::META_RULE_best_of_slot_selection_over_a_paired_rms_real_minus_shuffled_discriminator_can_"
           "INFLATE_the_apparent_lift_when_ONE_scorer_slot_control_COLLAPSES_while_others_retain_a_structural_"
           "popularity_baseline_a_co_trained_autograd_model_overfits_RANDOM_labels_and_loses_the_prior_so_its_"
           "SHUFFLED_arm_drops_to_near_zero_making_REAL_minus_SHUFFLED_large_even_though_REAL_is_IDENTICAL_"
           "across_slots_ANCHOR_on_the_popularity_ROBUST_slot_absolute_lift_FROZEN_ridge_or_KNN_not_the_best_of_"
           "slot_rms_2026-07-05"),
    "name": ("META (auditor discipline): best-of-slot over a paired-rms (REAL-minus-SHUFFLED) discriminator can "
             "INFLATE the apparent lift when ONE scorer slot's control collapses while others retain a "
             "structural/popularity baseline. A co-trained autograd model overfits RANDOM labels and loses the "
             "prior, so its SHUFFLED arm drops to ~0, making REAL-SHUFFLED large even though REAL is IDENTICAL "
             "across slots. Anchor on the popularity-ROBUST slot's ABSOLUTE lift, not the best-of-slot rms."),
    "corpus": "meta",
    "tier": "META_RULE",
    "kind": "auditor_discipline",
    "cert_status": "meta_rule_cert_neutral_landed_vet_discipline",
    "cert_class": "auditor_paired_rms_discriminator_best_of_slot_selection_baseline_collapse_phantom_anchor_on_robust_slot_absolute_lift",
    "description": (
        "AUDITOR DISCIPLINE derived from the landed-VET of schema_relation_hitsatk_mrr_reframe_v1 (2026-07-05, "
        "commit 9cf4cc8c9), where the cell's own lineage carried a 'shuffled-collapse-phantom' risk that FIRED. "
        "PATTERN: a discriminator defined as best-of-{slots} of a PAIRED difference (REAL - SHUFFLED, e.g. "
        "filtered Hits@10 real-minus-shuffled) is NOT robust to per-slot BASELINE COLLAPSE. When one scorer "
        "slot is a co-trained autograd model, training it on the SHUFFLED (random-label) arm makes it OVERFIT "
        "the noise and LOSE the structural/popularity prior, so its SHUFFLED filtered-rank collapses to near "
        "the spread-out floor; whereas closed-form / parameter-free slots (ridge FROZEN, cosine-vote KNN) "
        "RETAIN the popularity trap under shuffled labels. If the REAL scorer performs IDENTICALLY across slots "
        "(as it did: REAL Hits@10 ~0.75 in all three), then best-of-slot MECHANICALLY selects the slot with the "
        "most-collapsed baseline, INFLATING the differenced 'lift' (0.653) far above the fair popularity-"
        "controlled lift (0.17-0.20 on the robust slots), and can spuriously CLEAR a gate that no robust slot "
        "clears. "
        "RULE (for landed-VET of any paired-rms / real-minus-shuffled discriminator that takes best-of across "
        "scorer variants): (1) recompute the RAW ABSOLUTE REAL and SHUFFLED per slot, not just the differenced "
        "best-of-slot rms; (2) if REAL is ~constant across slots but the rms varies, the variation is a "
        "BASELINE-collapse artifact -- anchor on the popularity-ROBUST slot's absolute lift (FROZEN/KNN), not "
        "the collapse-prone trained slot; (3) a shuffled/null control that COLLAPSES is NOT automatically a "
        "clean control -- a GOOD null preserves the structural prior (popularity), a collapsed null OVERSTATES "
        "signal; (4) require the gate-clearing slot to be a popularity-ROBUST slot before promoting. "
        "RELATION TO PRIOR RULES: complements the joint-gate rule (retrieval+calibration+rank-fidelity single-"
        "metric false-pass, 2026-07-04) -- there a single metric hides failure on others; HERE a single SLOT "
        "hides that its lift is baseline-collapse-driven. Both defeat a headline by decomposing it. CERT-"
        "neutral (does not increment/decrement any experiment cert)."
    ),
    "aliases": ["best_of_slot_paired_rms_baseline_collapse_phantom_anchor_on_robust_slot_META",
                "shuffled_control_collapse_is_not_clean_a_good_null_preserves_the_popularity_prior"],
    "metadata": {
        "record_class": "auditor_discipline_meta_rule_cert_neutral",
        "term_class": "META_PAIRED_RMS_BEST_OF_SLOT_BASELINE_COLLAPSE_PHANTOM_ANCHOR_ROBUST_SLOT",
        "cert_status": "meta_rule_cert_neutral",
        "cert_class": "auditor_paired_rms_best_of_slot_baseline_collapse_phantom_anchor_on_robust_slot_absolute_lift",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "verified_via": "derived from off-disk recompute of schema_relation_hitsatk_mrr_reframe_v1 per-slot absolute REAL/SHUFFLED (JOINT-shuf collapse 0.100 vs FROZEN/KNN-shuf 0.578/0.556 while REAL~0.75 all slots)",
        "atomized_by": "skunkworks_landed_VET_2026-07-05_meta_best_of_slot_paired_rms_phantom",
        "source_anchor": "schema_relation_hitsatk_mrr_reframe_v1",
        "source_cell_commit": "9cf4cc8c9",
        "evidence": {
            "REAL_Hits10_across_slots": {"FROZEN": 0.751, "JOINT": 0.753, "KNN": 0.753},
            "SHUFFLED_Hits10_across_slots": {"FROZEN": 0.578, "JOINT": 0.100, "KNN": 0.556},
            "rms_across_slots": {"FROZEN": 0.173, "JOINT": 0.653, "KNN": 0.198},
            "phantom": "best-of-slot picks JOINT (collapsed shuffled) -> rms 0.653 >> fair robust-slot lift 0.17-0.20",
        },
        "cert_increment_delta": 0,
        "cert_neutral": True,
        "related_rules": ["joint_gate_single_metric_false_pass_2026-07-04",
                          "auditor_flag_broken_pc_before_structural_framing_2026-07-01"],
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
        "anchor": md.get("anchor") or md.get("source_anchor"),
        "cell_commit": md.get("cell_commit") or md.get("source_cell_commit"),
        "auditor": "skunkworks",
        "atomized_by": md.get("atomized_by"),
        "landed_VET_session": SESSION_TAG,
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

    n = a5_append(MATH_ATOMS, atom_rns)
    print(f"[atomize] (1) math CHAIN_GRADE generation-RNS/CRT appended; math lines={n}")
    ledger_append(atom_rns)

    n = a5_append(MATH_ATOMS, atom_integration)
    print(f"[atomize] (2) math HARD_FAIL integration-HARD_v2 (HF_STRUCTURAL_BOUND) appended; math lines={n}")
    ledger_append(atom_integration)

    n = a5_append(MATH_ATOMS, atom_reframe)
    print(f"[atomize] (3) math MIDDLE_BAND schema-reframe (phantom-trimmed) appended; math lines={n}")
    ledger_append(atom_reframe)

    n = a5_append(META_ATOMS, atom_meta)
    print(f"[atomize] (4) meta META_RULE best-of-slot phantom appended; meta lines={n}")
    ledger_append(atom_meta)

    print("[atomize] DONE 4 atoms + 4 ledger entries; A5-gated (tmp+os.replace+verify-load+json-integrity); matching TS_ISO")
    print("[atomize] NET CERT DELTA: CG +1 (RNS/CRT), HF +1 (integration), MB +1 (reframe), META +1 (cert-neutral)")
