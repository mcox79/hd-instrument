"""
A5-gated atomization: coherence-scalar-score v5 -> CORRECTED MEASURED_MECHANISM (NOT HARD_FAIL), plus a
v4 encoding-contingency AMENDMENT atom (2026-07-17). Director-authorized (GO); Store-write ONLY.

VET off-disk (.venv, this session): scipy MWU AUC == cell rank_auc to 4 decimals on all spot units (byte-level
reproduce). FAIRNESS-CRUX recompute: the cell's HARD_FAIL is an ARTIFACT of ~2x-net-anti-HD byte accounting.
Under SYMMETRIC-HONEST encoding (HD int8 2B/dim N=4096 vs symbolic 2B/prop C=4096, quantization-tested) the HD
lossy bundle CROSSES OVER and WINS at >=8x overload (x8 +0.053, x16 +0.069; float16 caveat: x16 ties +0.025).
-> two-layer boundary near ~8x overload, NOT "symbolic structural across all modes".

v4 amendment: v4's "bit-honest makes symbolic STRONGER (HD 65536 vs 28672 bits, 2.29x more, C=2N generous)" rests
on complex64=64bit/dim STORAGE. int8 storage = 16 bits/dim -> HD 16384 bits < symbolic 28672 (ratio 0.57,
bit-matched sym only 1.14N) -> the bit-honest sub-claim INVERTS. v4's EARNED regime core (symbolic wins
membership at WM/low-overload footprint; v4's own equal-DIM +0.034@6x crossover) is CONSISTENT with the v5
two-layer picture and is NOT challenged. Append pointer/amendment; do NOT supersede v4.

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
ATOMIZED_BY = "skunkworks_landed_vet_coherence_scalar_score_v5_corrected_MM_2026-07-17"
ATOMIZED_DATE = "2026-07-17"
ANCHOR_V5 = "read_discourse_state_hd_vs_symbolic_coherence_scalar_score_v1"
CELL_COMMIT_V5 = "f5bbd3b72"
V4_ATOM_ID = ("math::MEASURED_MECHANISM_read_discourse_state_hd_vs_symbolic_query_distribution_map_v1_HD_bundle_"
              "membership_earns_NO_equal_FOOTPRINT_keep_state_of_mind_MEMBERSHIP_overlay_go_SYMBOLIC_structural_"
              "Frady_crosstalk_ceiling_bit_honest_makes_symbolic_STRONGER_HD_2p29x_more_bits_65536_vs_28672_still_"
              "loses_C2N_GENEROUS_bit_matched_4p57N_crossover_qstar_monotonic_0p56_0p86_equal_DIM_win_plus0p034_"
              "6x_1sigma_only_6x_never_equal_float_MAP2_fuzzy_CLOSES_HD_door_equal_budget_symbolic_NN_cleanup_"
              "wins_0p96_1p00_vs_HD_0p53_0p64_win_was_no_cleanup_strawman_REVIVAL_aggregate_coherence_SCALAR_"
              "SCORE_Kintsch_CI_BEAGLE_O1_graded_similarity_NOT_membership_UNTESTED_LIVE_not_HD_has_no_state_of_"
              "mind_role_not_source_durable_fuzzy_to_this_cell_v4_shows_HD_LOSING_fuzzy_membership_CLOSES_v3_open_"
              "regimes_pop_weighted_AND_fuzzy_key_composes_29277_v3_29278_v2_VET_off_disk_byte_identical_0e00_"
              "5seed_2026-07-17")
V4_ANCHOR = "read_discourse_state_hd_vs_symbolic_query_distribution_map_v1"
V4_COMMIT = "dad41123a"

XARC_V5 = ("substrate_query.sh 'coherence scalar score HD bundle vs symbolic exact tuple equal byte footprint "
           "proposition overload eviction' -> top hit cosine=0.2715 lexical 'exaction' + a symbolic-execution "
           "note 0.258; NONE >0.30, no prior arc EXPERIMENT cell on HD coherence-scalar-score. v2/v3/v4 are "
           "credited lineage (membership-mode), not rediscovery -- this is the distinct coherence-scalar-score "
           "door they explicitly preserved as the revival criterion.")

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

# ---------------------------------------------------------------------------
# ATOM 1: corrected v5 MEASURED_MECHANISM (NOT HARD_FAIL)
# ---------------------------------------------------------------------------
ATOM_ID_V5 = ("math::MM_MEASURED_MECHANISM_read_discourse_state_hd_vs_symbolic_coherence_scalar_score_v1_CORRECTED_"
              "NOT_HARD_FAIL_two_layer_boundary_near_8x_overload_at_WM_load_le_capacity_no_overload_the_actual_"
              "overlay_operating_point_exact_symbolic_storage_BEATS_lossy_HD_coherence_bundle_EVERY_encoding_"
              "REGIME_consequence_NOT_byte_budget_structural_under_SYMMETRIC_HONEST_encoding_HD_int8_2Bdim_N4096_"
              "vs_symbolic_2Bprop_C4096_HD_lossy_bundle_CROSSES_OVER_WINS_at_ge_8x_overload_x8_plus0p053_x16_"
              "plus0p069_float16_caveat_x16_ties_plus0p025_flip_depends_on_int8_data_justify_a_long_term_memory_"
              "corpus_scale_regime_FOUNDATION_layer_not_overlay_cell_HARD_FAIL_was_ARTIFACT_of_2x_net_anti_HD_"
              "accounting_complex64_overcharged_HD_4x_a_COMPUTE_dtype_not_storage_mandate_symbolic_undercharged_"
              "4B_vs_honest_2Bprop_GIST_semantic_generalization_UNTESTED_a_FOUNDATION_embedding_layer_question_"
              "random_phasors_here_gist_impossible_by_construction_byte_level_scipy_MWU_matches_rank_auc_composes_"
              "29277_v3_29278_v2_29279_v4_2026-07-17")

CLAIM_V5 = (
    "MATH MEASURED_MECHANISM (CORRECTED landed-VET; the cell self-verdict HARD_FAIL is NOT robust). For the "
    "discrete-proposition state-of-mind overlay AT WORKING-MEMORY LOAD (<= capacity, no overload = the actual "
    "overlay operating point), exact symbolic storage BEATS the lossy HD coherence bundle in EVERY encoding "
    "tested -- a REGIME consequence (no overload -> exact wins), NOT the byte-budget-STRUCTURAL bound the cell "
    "claimed. Under SYMMETRIC-HONEST encoding (HD int8 2B/dim N=4096 vs symbolic 2B/prop C=4096, quantization-"
    "tested) the HD lossy bundle CROSSES OVER and WINS at >=8x overload: x8 +0.053, x16 +0.069 (float16 caveat: "
    "x16 ties +0.025, so flip-strength depends on accepting int8 storage, which the data justify -- int8 barely "
    "degrades the readout). That deep-overload win is a LONG-TERM-MEMORY / corpus-scale regime belonging to the "
    "FOUNDATION layer, not the working-memory overlay. The cell's HARD_FAIL was an ARTIFACT of ~2x NET anti-HD "
    "byte accounting: complex64 over-charged HD 4x (8B/dim; a COMPUTE dtype, NOT a storage mandate -- int8 2B/dim "
    "preserves the readout), and symbolic was over-charged (4B/prop vs honest 2B/prop for a 256x256=16-bit fact "
    "grid). The semantic-generalization / GIST mode (coherence vs propositions never exactly asserted but "
    "similar) is UNTESTED and is a FOUNDATION/embedding-layer question (all phasors here are random -> gist is "
    "impossible BY CONSTRUCTION regardless of arm). ARC REFRAME: the v2-v5 state-of-mind conclusion is 'SYMBOLIC "
    "overlay at the WM operating point + HD wins at overload/corpus scale = a two-layer boundary LOCATED near "
    "~8x overload', NOT 'symbolic structural across all modes'.")

RECOMPUTE_V5 = (
    "INDEP off-disk recompute (.venv; scipy.stats.mannwhitneyu, a DIFFERENT code path than the cell's own "
    "rank_auc): AUC matches to 4 decimals on every spot unit (agg x0.5 HD 0.8167, x2 0.7199, x4 0.5881, x8 "
    "0.5830, recent x4 0.6416; symEq exact). Gates independently confirmed: random 0.46-0.52, hd_add 0.50-0.57, "
    "sym_pair_marginal pinned 0.500 (conjunction-sensitive discriminator), symEq exact 1.0 low-load and "
    "un-saturated <0.95 top-overload, arms_differ all-true. Cell HARD_FAIL is CORRECTLY COMPUTED FOR ITS "
    "ENCODING (HD margin +0.029@x8, +0.023@x16, both under the 0.03 bar). FAIRNESS-CRUX sweep (8192-byte budget, "
    "5 seeds, aggregate, ACTUAL quantized storage): HD margin vs symEq at [x4,x8,x16] = complex64 N=1024 "
    "[-0.002,+0.048,+0.030]; float16 N=2048 [+0.007,+0.081,+0.067]; int8 N=4096 [+0.110,+0.120,+0.111]. "
    "FULLY-SYMMETRIC (HD int8 N=4096 vs sym 2B/prop C=4096): x1 -0.134, x2 -0.183, x4 -0.024, x8 +0.053, x16 "
    "+0.069 -> crossover (symbolic wins <=4x, HD wins >=8x). Bit-count: HD complex64=65536 bits, int8=16384 "
    "bits, symbolic C=2N=28672 bits -> int8 makes HD CHEAPER than symbolic (ratio 0.57).")

SCOPE_V5 = (
    "Synthetic integer-id facts/stream (256 agents x 256 patients, random FHRR phasors), glass-box, no LLM. "
    "MEASURED_MECHANISM (proven-bound), NOT a HARD_FAIL and NOT 'symbolic structural across all modes'. The "
    "verdict is ENCODING-CONTINGENT: it depends on (a) HD storage precision (complex64 8B/dim vs int8 2B/dim = a "
    "4x lever; int8 is a legitimate honest storage -- verified to barely degrade the readout at this scale) and "
    "(b) symbolic per-prop cost (4B vs honest 2B for a 65536-item grid = a 2x lever). The DEFENSIBLE settling "
    "reason for 'symbolic wins the overlay' is a REGIME argument (working memory operates at low proposition "
    "count where there is no overload, so exact storage is unbeatable), NOT the structural 'exact-storage-beats-"
    "lossy-bundle-at-equal-footprint' claim the cell/Director asserted. Do NOT bank as HARD_FAIL; do NOT foreclose "
    "the gist door (a foundation/embedding-layer question, not an overlay question).")

METRICS_V5 = {
    "byte_level_reproduce": "scipy_MWU_matches_cell_rank_auc_4_decimals_all_units",
    "cell_verdict": "HARD_FAIL", "auditor_tier": "MEASURED_MECHANISM",
    "cell_encoding_margin_hd_vs_symEq": {"x4": 0.000, "x8": 0.029, "x16": 0.023},
    "symmetric_honest_hd_int8_N4096_vs_sym_2Bprop_C4096": {
        "x1": -0.134, "x2": -0.183, "x4": -0.024, "x8": 0.053, "x16": 0.069},
    "float16_N2048_vs_sym_4Bprop_C2048_margin": {"x4": 0.007, "x8": 0.081, "x16": 0.067},
    "int8_N4096_vs_sym_4Bprop_C2048_margin": {"x2": 0.059, "x4": 0.110, "x8": 0.120, "x16": 0.111},
    "bit_counts": {"hd_complex64": 65536, "hd_int8": 16384, "sym_c2n_14bit": 28672,
                   "hd_int8_over_sym_ratio": 0.57, "bit_matched_sym_slots_over_N_at_hd_int8": 1.14},
    "crossover_located_near_overload": 8, "n_seeds": 5, "n_dim_cell": 1024,
    "gist_semantic_generalization": "untested_foundation_embedding_layer_question_random_phasors_gist_impossible_by_construction",
}

COMPOSES_V5 = [
    "AMENDS/REFRAMES the v2-v5 state-of-mind arc conclusion: from 'symbolic structural across all modes' to "
    "'two-layer boundary near ~8x overload -- symbolic overlay at the WM operating point, HD wins at overload/"
    "corpus (foundation) scale'.",
    "composes_with v4 query-distribution-map (dad41123a / atom 29279) -- membership-mode go-symbolic; v4's OWN "
    "equal-DIM +0.034@6x crossover is the same two-layer signal; see the companion v4 encoding-amendment atom.",
    "composes_with v3 membership-overload MM (75ffcb67c / atom 29277) and v2 companion negative (4487bd222 / "
    "atom 29278) -- the exact/membership-mode negatives; this v5 closes the coherence-scalar-score door they "
    "explicitly preserved as the revival criterion.",
    "points to the FOUNDATION layer: the deep-overload HD win + the gist/semantic-generalization door both "
    "belong to the long-term-memory / embedding layer where HD/embeddings are already the design, NOT the "
    "working-memory state-of-mind overlay.",
]

atom_v5 = {
    "id": ATOM_ID_V5,
    "name": CLAIM_V5,
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet_proven_bound",
    "cert_status": ("measured_mechanism_coherence_scalar_score_CORRECTED_not_hard_fail_two_layer_boundary_near_8x_"
                    "wm_load_exact_symbolic_beats_lossy_hd_regime_not_structural_symmetric_honest_int8_hd_crosses_"
                    "over_wins_ge_8x_x8_p053_x16_p069_float16_x16_ties_p025_foundation_layer_cell_hard_fail_"
                    "artifact_2x_net_anti_hd_accounting_complex64_overcharged_hd_4x_symbolic_4B_vs_2B_gist_"
                    "untested_foundation_question_composes_29277_v3_29278_v2_29279_v4"),
    "cert_class": ("vsa_fhrr_hd_discourse_state_coherence_scalar_score_two_layer_boundary_symbolic_wins_wm_load_"
                   "regime_hd_wins_deep_overload_foundation_scale_under_symmetric_honest_encoding_proven_bound_"
                   "corrects_cell_hard_fail_encoding_artifact"),
    "description": (CLAIM_V5 + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + RECOMPUTE_V5
                    + "\n\nHONEST SCOPE: " + SCOPE_V5),
    "aliases": [
        "coherence-scalar-score v5: HARD_FAIL NOT robust -> corrected MEASURED_MECHANISM",
        "state-of-mind overlay is SYMBOLIC BY REGIME at WM load, NOT structural across all modes",
        "two-layer boundary near ~8x overload: symbolic overlay + HD foundation-scale coherence",
        "complex64 over-charges HD 4x (compute dtype != storage mandate); int8 2B/dim flips the equal-byte fight",
        "gist/semantic-generalization mode untested = a foundation/embedding-layer question, not overlay",
    ],
    "ts_iso": _iso,
    "ts": _ts,
    "metadata": {
        "provenance_quality": "independent_off_disk_recompute_scipy_MWU_different_code_path_matches_rank_auc_4dp_plus_quantization_tested_fairness_crux_sweep_in_venv_not_verdict_msg",
        "anchor": ANCHOR_V5,
        "cell_commit": CELL_COMMIT_V5,
        "supersedes": None,
        "supersedes_commit": None,
        "amends_anchor": "v2-v5 state-of-mind arc conclusion (reframe: two-layer, not symbolic-structural)",
        "amends_commit": None,
        "store_head_at_write": "unsynced_needs_orchestrator",
        "metrics_path": "data/exp_read_discourse_state_hd_vs_symbolic_coherence_scalar_score_v1/metrics.json",
        "verified_off_data": RECOMPUTE_V5,
        "honest_scope": SCOPE_V5,
        "metrics": METRICS_V5,
        "bounding_ruling": ("At working-memory load (<= capacity) exact symbolic storage beats the lossy HD "
                            "coherence bundle in every encoding -- a REGIME bound (no overload). Under symmetric-"
                            "honest byte encoding the HD bundle crosses over and wins at >=8x overload (foundation/"
                            "corpus scale). The cell's HARD_FAIL is an artifact of net-2x-anti-HD accounting and is "
                            "NOT a structural byte-budget bound. Bankable at MEASURED_MECHANISM."),
        "over_reads_corrected": [
            "CELL/DIRECTOR over-read CORRECTED (symmetric anti-negativity, honest UPWARD for HD): 'HARD_FAIL "
            "settles the ENTIRE state-of-mind overlay = SYMBOLIC across all modes; exact-storage-beats-lossy-"
            "bundle-for-discrete-facts is structural' is NOT earned. The HARD_FAIL is encoding-fragile: it flips "
            "to an HD crossover under a defensible symmetric-honest encoding (HD int8 2B/dim, symbolic 2B/prop).",
            "'HD only edges where BOTH are near chance' is NOT a fair denial -- under fair encoding HD reaches "
            "0.64-0.68 at 8-16x while symbolic collapses to 0.57-0.63.",
            "The DEFENSIBLE reason symbolic wins the OVERLAY is a REGIME argument (WM operates at low load, no "
            "overload -> exact wins), NOT the structural claim the cell made. Bank the regime reason, not the "
            "structural one.",
            "Do NOT foreclose the gist/semantic-generalization mode -- it is genuinely untested AND is a "
            "FOUNDATION/embedding-layer question (needs similarity-structured embeddings; impossible here by "
            "construction with random phasors). Foreclosing it as 'overlay symbolic' would be an over-read.",
        ],
        "symmetric_anti_negativity": ("Honest UPWARD correction for HD (same rigor as a downward one): the cell's "
                                      "clean-negative was not robust to a fair re-encoding. Capped at MEASURED_"
                                      "MECHANISM, NOT promoted to an HD chain-grade keep -- the HD win is confined "
                                      "to deep overload (absolute AUC 0.64-0.68, a mediocre detector) and lives in "
                                      "the foundation layer, not the working-memory overlay."),
        "revival_criteria": ("(1) A fair-encoding follow-up cell (HD int8 2B/dim N=4096 vs symbolic 2B/prop "
                             "C=4096) to lock the two-layer crossover as a first-class result. (2) The GIST / "
                             "semantic-generalization mode with SIMILARITY-STRUCTURED embeddings (foundation "
                             "layer): q+ semantically similar to but never exactly asserted, where exact-lookup "
                             "returns 'not found' and distributed similarity generalizes. (3) Test at genuine "
                             "working-memory scale (dozens-hundreds of props) to confirm the overlay operating "
                             "point sits in the symbolic-wins regime."),
        "cross_arc_overlap_check": XARC_V5,
        "cites": [CELL_COMMIT_V5,
                  "Fix_28_verify_off_data_not_verdict_msg",
                  "symmetric_anti_negativity_verify_both_directions_USER",
                  "cited_number_must_reproduce_from_cell",
                  "feedback_construction_proof_is_not_a_capability_win",
                  "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts"],
        "composes_with": COMPOSES_V5,
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "vet_id": "skunkworks_landed_vet_f5bbd3b72_coherence_scalar_score_corrected_2026-07-17",
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
    },
}

# ---------------------------------------------------------------------------
# ATOM 2: v4 encoding-contingency AMENDMENT (amends v4; does NOT supersede)
# ---------------------------------------------------------------------------
ATOM_ID_V4AMEND = ("math::AMENDMENT_encoding_contingency_of_v4_query_distribution_map_bit_honest_gloss_the_v4_claim_"
                   "bit_honest_makes_symbolic_STRONGER_HD_65536_vs_28672_bits_2p29x_more_C2N_generous_RESTS_on_"
                   "complex64_64bit_per_dim_STORAGE_a_COMPUTE_dtype_NOT_a_storage_mandate_v5_audit_shows_int8_"
                   "16bit_per_dim_preserves_the_FHRR_bundle_readout_under_which_HD_costs_16384_bits_LESS_than_"
                   "symbolic_28672_ratio_0p57_bit_matched_symbolic_only_1p14N_INVERTING_the_bit_honest_sub_claim_"
                   "v4_EARNED_regime_core_symbolic_wins_membership_at_WM_low_overload_footprint_and_v4_OWN_equal_"
                   "DIM_plus0p034_6x_crossover_STAND_and_are_CONSISTENT_with_v5_two_layer_boundary_membership_"
                   "specific_int8_BA_robustness_is_the_one_unverified_step_and_the_explicit_recheck_criterion_"
                   "amends_29279_NOT_superseded_2026-07-17")

CLAIM_V4AMEND = (
    "MATH AMENDMENT (encoding-contingency pointer to v4 query-distribution-map atom 29279; AMENDS, does NOT "
    "supersede). v4's affirmative sub-claim 'bit-honest accounting makes symbolic STRONGER: HD complex64 bundle "
    "= 65,536 bits vs symbolic C=2N = 28,672 bits (HD spends 2.29x more bits and STILL loses; C=2N was GENEROUS "
    "to HD)' RESTS ENTIRELY on charging the HD bundle complex64 = 64 bits/dim, which is a COMPUTE dtype (CLAUDE.md "
    "FHRR convention), NOT the minimal STORAGE footprint. The v5 coherence-scalar-score audit demonstrated (off-"
    "disk, quantization-tested) that the FHRR bundle readout survives int8 storage = 16 bits/dim; the bundle is "
    "the SAME object in v4 and v5, so its byte cost is not readout-dependent. Under int8 storage HD = 16,384 "
    "bits < symbolic 28,672 (ratio 0.57), and a bit-matched symbolic gets only ~1.14N slots (not 4.57N) -- "
    "INVERTING the direction of v4's bit-honest gloss. Therefore v4's 'bit-honest makes symbolic stronger' should "
    "be read as ENCODING-CONTINGENT (true only at complex64 storage), NOT as an unconditional structural fact. "
    "v4's EARNED regime core is NOT challenged: symbolic wins the MEMBERSHIP overlay at working-memory / low-"
    "overload FOOTPRINT, and v4's OWN equal-DIM crossover (HD +0.034@6x, marginal at high overload) is the SAME "
    "two-layer signal the v5 corrected atom locates near ~8x overload. The ONE unverified step is whether v4's "
    "specific MEMBERSHIP-DECODE balanced-accuracy (not the coherence scalar score) survives int8 quantization as "
    "well as v5's readout did -- that is the explicit re-check criterion, not asserted here.")

atom_v4amend = {
    "id": ATOM_ID_V4AMEND,
    "name": CLAIM_V4AMEND,
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet_amendment",
    "cert_status": ("amendment_encoding_contingency_v4_bit_honest_gloss_rests_on_complex64_storage_int8_inverts_"
                    "hd_16384_lt_symbolic_28672_ratio_0p57_v4_earned_regime_core_and_equal_dim_crossover_stand_"
                    "consistent_with_v5_two_layer_membership_int8_BA_robustness_is_the_recheck_criterion_amends_"
                    "29279_not_superseded"),
    "cert_class": ("vsa_fhrr_bit_accounting_encoding_contingency_complex64_compute_dtype_not_storage_mandate_int8_"
                   "storage_inverts_bit_honest_ratio_amendment_to_membership_overlay_proven_bound"),
    "description": CLAIM_V4AMEND + "\n\nRECOMPUTE (.venv): " + (
        "HD N=1024 storage bits: complex64 65536, int8 16384. Symbolic C=2N=2048 x 14 bits = 28672. "
        "int8 ratio HD/sym = 0.57; bit-matched symbolic at HD-int8 budget = 16384//14 = 1170 slots = 1.14N "
        "(vs v4's stated 4.57N at complex64). int8 barely degrades the FHRR bundle readout (v5 coherence sweep: "
        "int8 N=4096 tracks full-precision N=4096 to ~0.0003 AUC). The bundle byte cost is readout-independent; "
        "the residual empirical question is int8's effect on v4's specific membership-decode BA."),
    "aliases": [
        "v4 'bit-honest makes symbolic stronger' is encoding-contingent (complex64-only), inverts under int8",
        "complex64 is a COMPUTE dtype not a storage mandate -- FHRR bundle stores fine at int8 16 bits/dim",
        "v4 regime core (symbolic wins membership at WM footprint) + equal-DIM +0.034@6x crossover STAND",
    ],
    "ts_iso": _iso,
    "ts": _ts,
    "metadata": {
        "provenance_quality": "bit_count_recompute_in_venv_plus_v5_quantization_tested_bundle_readout_int8_robustness_bundle_is_same_object_across_cells",
        "anchor": V4_ANCHOR,
        "cell_commit": V4_COMMIT,
        "supersedes": None,
        "supersedes_commit": None,
        "amends_anchor": V4_ANCHOR,
        "amends_commit": V4_COMMIT,
        "amends_atom_id": V4_ATOM_ID,
        "store_head_at_write": "unsynced_needs_orchestrator",
        "metrics_path": "data/exp_read_discourse_state_hd_vs_symbolic_query_distribution_map_v1/metrics.json",
        "verified_off_data": ("Bit-count arithmetic recomputed in .venv (HD complex64 65536 / int8 16384; sym "
                              "C=2N 28672; int8 ratio 0.57; bit-matched sym 1.14N). int8 bundle-readout robustness "
                              "established on the v5 coherence sweep (int8 N=4096 ~= full-precision N=4096). NOT a "
                              "re-run of v4's membership task -- that int8-BA robustness is flagged as the residual "
                              "check, not asserted."),
        "honest_scope": ("Amendment to v4's BIT-HONEST sub-claim only. Does NOT supersede or demote v4: v4's "
                         "membership-overlay MEASURED_MECHANISM (symbolic wins at equal FOOTPRINT at WM/low-"
                         "overload load) stands, as does v4's equal-DIM +0.034@6x HD crossover. The correction is "
                         "narrow: the 'complex64 bit-honest makes symbolic STRONGER' gloss is storage-precision-"
                         "contingent and inverts under int8, consistent with the v5 two-layer picture."),
        "bounding_ruling": ("v4's bit-honest 'symbolic stronger' claim is contingent on complex64 storage and "
                            "inverts under int8; report v4's boundary as ENCODING-CONTINGENT + regime-located, "
                            "not unconditionally structural. v4's regime core is unaffected."),
        "over_reads_corrected": [
            "v4 atom's 'bit-honest accounting makes symbolic STRONGER not weaker (HD 2.29x more bits, C=2N "
            "generous)' over-reads a complex64-storage-specific fact as unconditional; under honest int8 storage "
            "the ratio inverts to 0.57 (HD cheaper).",
        ],
        "symmetric_anti_negativity": ("Honest correction of a prior auditor over-statement (my own v4 atom): the "
                                      "bit-honest gloss over-charged HD. Kept as an AMENDMENT (not a demote) "
                                      "because v4's regime core and equal-DIM crossover are intact and were "
                                      "already recorded."),
        "revival_criteria": ("Re-run v4's membership-decode arms with an int8-stored bundle (2B/dim N=4096) vs "
                             "symbolic 2B/prop C=4096 to confirm whether v4's balanced-accuracy crossover matches "
                             "the v5 coherence crossover under fully-symmetric honest encoding."),
        "cross_arc_overlap_check": ("Amends the existing v4 atom (29279); same arc; no new cross-arc collision. "
                                    "The complex64-over-charge finding is the v5 audit's, applied to v4's shared "
                                    "bundle object."),
        "cites": [V4_COMMIT, CELL_COMMIT_V5, "symmetric_anti_negativity_verify_both_directions_USER",
                  "verify_the_referent_atom_ids_mechanism_metric_regime"],
        "composes_with": [
            "AMENDS v4 query-distribution-map MEASURED_MECHANISM (dad41123a / atom 29279) -- bit-honest sub-claim "
            "encoding-contingency; regime core NOT superseded.",
            "companion to the v5 coherence-scalar-score corrected MM (this batch) -- shares the complex64-over-"
            "charge / int8-storage finding and the two-layer boundary framing.",
        ],
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "vet_id": "skunkworks_landed_vet_f5bbd3b72_v4_encoding_amendment_2026-07-17",
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
    },
}

# ---------------------------------------------------------------------------
# LEDGER ROWS
# ---------------------------------------------------------------------------
ledger_v5 = {
    "op": "add_proven_bound_measured_mechanism_corrects_cell_hard_fail_encoding_artifact",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": atom_v5["cert_status"],
    "anchor": ANCHOR_V5,
    "cell_commit": CELL_COMMIT_V5,
    "supersedes_commit": None,
    "amends_commit": None,
    "store_head_at_write": "unsynced_needs_orchestrator",
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": ATOMIZED_BY,
    "verdict": ("MEASURED_MECHANISM (CORRECTED; NOT the cell's HARD_FAIL). Byte-level reproduce confirmed (scipy "
                "MWU == rank_auc 4dp). Two-layer boundary near ~8x overload: at WM load symbolic exact storage "
                "beats the lossy HD bundle in every encoding (REGIME, not structural); under symmetric-honest "
                "encoding (HD int8 2B/dim N=4096 vs sym 2B/prop C=4096) HD crosses over and WINS at >=8x (x8 "
                "+0.053, x16 +0.069; float16 x16 ties +0.025). Cell HARD_FAIL = artifact of ~2x net anti-HD "
                "accounting (complex64 over-charged HD 4x; symbolic 4B vs honest 2B/prop). GIST mode untested = "
                "foundation-layer question. Capped at MM (HD win = deep-overload, foundation scale, AUC 0.64-0.68)."),
    "cert_increment_delta": 1,
    "decision": ("ADD MEASURED_MECHANISM (corrected). Do NOT bank as HARD_FAIL; do NOT bank 'symbolic across all "
                 "modes structural'. Bank the NARROWED claim: symbolic wins the overlay BY REGIME at WM load; HD "
                 "wins deep overload (foundation scale) under fair encoding = a two-layer boundary near ~8x. "
                 "Composes with 29277 (v3) + 29278 (v2) + 29279 (v4); none superseded. Gist door left LIVE as a "
                 "foundation/embedding-layer question."),
    "framing_correction_vs_director": ("Director's worry was correct and is CONFIRMED: the symbolic direction was "
                                       "OVER-READ. HARD_FAIL is encoding-fragile and flips to an HD crossover under "
                                       "symmetric-honest encoding. HD was UNDER-served by the cell (complex64 = a "
                                       "4x storage over-charge; symbolic given the cheaper unit). Honest UPWARD "
                                       "correction for HD, same rigor as a downward one. Still capped at MM: the HD "
                                       "win is confined to deep-overload/foundation scale, not the WM overlay "
                                       "operating point, so 'symbolic overlay at WM load' survives as a REGIME "
                                       "result."),
    "cross_arc_overlap_check": XARC_V5,
    "net_cert_delta": ("+1 MM (two-layer boundary; corrects the cell's HARD_FAIL as an encoding artifact; closes "
                       "the coherence-scalar-score door as REGIME-symbolic-at-WM-load + HD-wins-at-overload)."),
    "supersedes": None,
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
    "ts_iso": _iso,
    "ts": _ts,
    "atom_id": ATOM_ID_V5,
}

ledger_v4amend = {
    "op": "amend_encoding_contingency_of_v4_bit_honest_gloss_not_superseded",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": atom_v4amend["cert_status"],
    "anchor": V4_ANCHOR,
    "cell_commit": V4_COMMIT,
    "supersedes_commit": None,
    "amends_commit": V4_COMMIT,
    "store_head_at_write": "unsynced_needs_orchestrator",
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": ATOMIZED_BY,
    "verdict": ("AMENDMENT (amends v4 atom 29279; does NOT supersede). v4's 'bit-honest makes symbolic STRONGER "
                "(HD 65536 vs 28672 bits, 2.29x more, C=2N generous)' rests on complex64=64bit/dim STORAGE (a "
                "compute dtype). Under int8=16bit/dim storage HD=16384 bits < symbolic 28672 (ratio 0.57, "
                "bit-matched sym 1.14N) -> the bit-honest sub-claim INVERTS. v4's regime core (symbolic wins "
                "membership at WM footprint) + v4's own equal-DIM +0.034@6x crossover STAND and are consistent "
                "with the v5 two-layer boundary. int8 effect on v4's membership-decode BA = the residual recheck."),
    "cert_increment_delta": 0,
    "decision": ("APPEND encoding-contingency amendment atom. v4 NOT superseded, NOT demoted. Narrow correction "
                 "to v4's bit-honest gloss only (encoding-contingent, inverts under int8). Consistent with the v5 "
                 "corrected atom's two-layer framing."),
    "framing_correction_vs_director": ("Per Director's defer-to-judgment: v4 is NOT 'already fine' -- it carries a "
                                       "specific affirmative bit-accounting claim my v5 audit contradicts, so an "
                                       "amendment is warranted (not left to read as 'symbolic structural'). But v4's "
                                       "regime core and its already-recorded equal-DIM crossover are intact, so "
                                       "amendment (delta 0), not demote."),
    "cross_arc_overlap_check": "amends 29279 same arc; no new collision",
    "net_cert_delta": "0 (amendment; no new proven bound; v4 not superseded)",
    "supersedes": None,
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
    "ts_iso": _iso,
    "ts": _ts,
    "atom_id": ATOM_ID_V4AMEND,
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
    print("=== A5 atom-write: coherence-scalar-score v5 corrected MM + v4 encoding amendment (2026-07-17) ===")
    print("ts_iso =", _iso)
    for a in (atom_v5, atom_v4amend, ledger_v5, ledger_v4amend):
        assert json.dumps(a).isascii(), "non-ascii payload"
    assert ledger_v5["atom_id"] == atom_v5["id"]
    assert ledger_v4amend["atom_id"] == atom_v4amend["id"]
    assert atom_v5["id"] != atom_v4amend["id"]

    existing = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                existing.add(json.loads(line).get("id"))
            except Exception:
                pass
    for a in (atom_v5, atom_v4amend):
        if a["id"] in existing:
            print("ABORT: id already in store:", a["id"][:80]); sys.exit(1)
    print("id-uniqueness OK (2 new atoms, neither pre-existing)")

    print("Writing 2 atoms to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, [atom_v5, atom_v4amend])
    print("  math atoms: pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 2:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 2 rows to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, [ledger_v5, ledger_v4amend])
    print("  cert_ledger: pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 2:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    # integrity: full reload of math atoms; all parse + both new ids present
    n_ok = 0
    present = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            present.add(json.loads(line).get("id")); n_ok += 1
    assert atom_v5["id"] in present and atom_v4amend["id"] in present, "post-write integrity: new id missing"
    print("integrity: math/atoms.jsonl fully parses (%d lines), both new ids present." % n_ok)

    # integrity: full reload of ledger
    l_ok = 0
    with open(CERT_LEDGER, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            json.loads(line); l_ok += 1
    print("integrity: meta/cert_ledger.jsonl fully parses (%d lines)." % l_ok)
    print()
    print("=== A5 WRITE COMPLETE (LOCAL ONLY; needs_orchestrator_store_sync=True) ===")
    print("V5_ATOM_ID:", atom_v5["id"])
    print("V4_AMEND_ATOM_ID:", atom_v4amend["id"])


if __name__ == "__main__":
    main()
