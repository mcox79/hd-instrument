"""Skunkworks 2026-06-25 -- tier ruling for 3 production-scale cells post 5x disparate-fields drill.

DRILL: notes/research_readout_degeneracy_5x_disparate_drill_2026-06-25.md
DIRECTOR SYNTHESIS: notes/director_5_intuitive_barriers_with_analogies_2026-06-25.md
TIER RULING NOTE: notes/skunkworks_tier_ruling_3cells_post_drill_2026-06-25.md

Three EXPERIMENT_RECORD MEASURED_MECHANISM atoms (CERT-neutral, delta=0 each):

1. EXP_substrate_cross_layer_compose_LM_v2_RESCUE_FULL_MM
   cell verdict: READOUT_DEGENERATE (verdict-classifier instrument bug)
   skunkworks ruling: MEASURED_MECHANISM (NOT chain-grade despite director re-tier request)
   Mechanism: cross-layer independent-W beats shared-W +0.376 BPC at production scale
   (N=8192 V=4000 text8 100k 3 seeds, cv=0.005). BPC chain-grade BLOCKED under
   META_HARNESS_RIGGED (cert row 698); top1 chain-grade BLOCKED (lift +7% rel vs unigram;
   n1_v3 bar +61.6% rel; 0.11x bar). Same signature as cert rows 707/708 ruled MM.
   READOUT_DEGENERATE label retired: raw_at_T1=11.55 is mathematically forced near
   vocab-entropy 11.97 when tuned T=0.05; tuned BPC at T=0.05 = 7.168 (4.8 bits below
   vocab-entropy = NOT collapsed). Verdict classifier should use tuned metrics.

2. EXP_substrate_hub_spoke_E1_v2_diverse_algorithm_MM
   cell verdict: MIDDLE_BAND (preserved as cell-self verdict)
   skunkworks ruling: MEASURED_MECHANISM (instrument bug)
   Mechanism: SoftHebb spoke spoke_recon_err=NaN across all 3 seeds x all arms;
   cf-RPE routing collapses to gates [0.96, 0.03, 0.01] picking the broken (NaN) spoke 0.
   3 spoke-arms all output bpc=7.7378 identical to unigram (substrate falls back to
   unigram-equivalent when routing picks NaN keys). This is M3 bundle-health-check
   gap, not a substrate-mechanism failure.

3. EXP_substrate_compose_heterogeneous_routing_v2_RESCUE_MM
   cell verdict: HARD_FAIL_PROVENANCE (preserved)
   skunkworks ruling: MEASURED_MECHANISM (instrument calibration)
   Rail referent fair_harness_substrate_as_lm_v1: N_DIM=8192 N_TRAIN=100k 3-seed cuda;
   v2_RESCUE: N_DIM=4096 N_TRAIN=50k 2-seed cpu. Drift +0.35 BPC vs tol 0.05 explained
   by 2x N + 2x data + 1-fewer seed reduction (half-N capacity scaling). Direction-
   correct signal: ARM_FREQ_ROUTED_K2 best_het bpc=7.4321 beats in-cell baseline 7.6563
   by -0.224 BPC. M2 tight-rail-from-different-config can mask direction-correct lift.

Plus 3 META rule atoms (CERT-neutral, meta corpus, delta=0):

  M1 verdict-classifier-use-tuned-metrics-never-raw-at-T1
  M2 tight-rail-from-different-config-HARD_FAIL_PROVENANCE-can-mask-direction-correct-lift
  M3 bundle-health-check-NaN-spoke-can-win-cf_RPE-routing

DISCIPLINES HONORED:
  - Fix #28 default under-claim: cell 7 director request CHAIN_GRADE rejected per
    by-construction-saturation + META_HARNESS_RIGGED precedent (cert rows 698/699/707/708)
  - per-arm metrics read directly off detail.by_arm_agg + per_seed
  - verify-the-referent: rail config independently confirmed off fair_harness metrics
  - A5 PRE/POST snapshot across writes; round-trip pq verification
  - Idempotency: skip atoms already in Store
  - Foreground execution (Fix #20)
  - ASCII only
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path("D:/AI/hd-instrument").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_measured_mechanism_row,
)


STORE_ROOT = Path("D:/AI/hd-instrument/data/substrate_index")
ATOMIZED_BY = "skunkworks_atomize_tier_ruling_3cells_post_drill_2026-06-25"

NOTES_PATH_RULING = "notes/skunkworks_tier_ruling_3cells_post_drill_2026-06-25.md"
NOTES_PATH_DRILL = "notes/research_readout_degeneracy_5x_disparate_drill_2026-06-25.md"


# ============================================================================
# Atom builders -- experiment records
# ============================================================================

def build_cross_layer_compose_LM_v2_RESCUE_FULL_MM() -> Atom:
    return Atom(
        id="T3/EXP_substrate_cross_layer_compose_LM_v2_RESCUE_FULL_MM",
        name=(
            "Cross-layer compose LM v2 RESCUE FULL -- MEASURED_MECHANISM "
            "(independent-W beats shared-W +0.376 BPC at production scale; "
            "cell verdict READOUT_DEGENERATE retired as verdict-classifier "
            "instrument bug; BPC chain-grade BLOCKED under META_HARNESS_RIGGED "
            "row 698; top1 chain-grade BLOCKED at 0.11x n1_v3 bar)"
        ),
        description=(
            "Cell landed READOUT_DEGENERATE on raw_bpc_at_T1_L1_mean=11.5518 near "
            "vocab-entropy 11.9658. Cert-owner ruling: MEASURED_MECHANISM, NOT "
            "chain-grade. Verify-OFF-DATA reproduces all cited numbers.\n\n"
            "PER-ARM (3 seeds [7, 17, 23], independently recomputed from per_seed):\n"
            "  ARM_UNIGRAM                  bpc=7.7378  cv=0.0000\n"
            "  ARM_SINGLE_LAYER_CFRPE       bpc=7.0888  cv=0.0030  top1=0.2327\n"
            "  ARM_2_LAYER_INDEPENDENT      bpc=7.1679  cv=0.0050  top1=0.2324\n"
            "  ARM_3_LAYER_INDEPENDENT      bpc=7.1771  cv=0.0077  top1=0.2248\n"
            "  ARM_2_LAYER_SHARED_W         bpc=7.5442  cv=0.0008  top1=0.2171\n"
            "  indep_vs_shared_gap = +0.376 BPC (line 133)\n"
            "  indep_vs_single_lift = -0.079 BPC (single beats 2L-indep on BPC)\n\n"
            "WHY READOUT_DEGENERATE IS A VERDICT-CLASSIFIER BUG (concur with drill):\n"
            "  raw_bpc_at_T1_L1=11.55 is BPC at T=1.0 lambda=1.0 (untuned). Best "
            "tuned BPC=7.168 sits at T=0.05 lambda=0.3 (per_seed) -- 20x temperature "
            "scaling away. raw_at_T1 is mathematically forced toward vocab-entropy "
            "by wave14b CE_floor regardless of substrate signal. tuned BPC at 7.168 "
            "is 4.8 bits BELOW vocab-entropy = NOT collapse. shared_W reads raw_at_T1 "
            "11.64 (closer to vocab-entropy) but has WORSE capability -- the "
            "degen classifier is measurement-mode-confused. M1 lesson: verdict "
            "classifiers must use tuned metrics, never raw_at_T1.\n\n"
            "WHY NOT CHAIN_GRADE (Fix #28 default under-claim + META_HARNESS_RIGGED):\n"
            "  Cell's OWN pre-registered chain-grade bar (line 157 honest_scope):\n"
            "  'HARD_PASS_CHAIN_GRADE = best_indep BPC <= 6.95 AND beats SHARED_W "
            "by >= 0.15 BPC AND cv<=0.03'. best_indep BPC = 7.168, NOT <= 6.95. "
            "Director's CHAIN_GRADE request waives the primary BPC bar -- exactly "
            "the move META_HARNESS_RIGGED (cert row 698) was atomized to catch.\n"
            "  Top1 numbers: indep_2L=0.2324 vs unigram=0.2171 = +0.0153 abs = "
            "+7.05% rel. n1_v3 chain-grade bar (cert row 699) = +61.6% rel. This "
            "cell sits at 0.11x the top1 chain-grade bar.\n"
            "  PRECEDENT: cert rows 707 (cfrpe_n_steps_curve_v1) + 708 "
            "(cfrpe_per_token_adaptive_lr_v1) ruled MEASURED_MECHANISM on the "
            "same signature (BPC improvement without top1 propagation) in the "
            "past 48h. This is the third instance.\n\n"
            "WHAT IS PROVEN (mechanism characterization, CERT-neutral):\n"
            "  Cross-layer 2L-INDEPENDENT cf-RPE beats SHARED-W by +0.376 BPC at "
            "production scale (N_DIM=8192, V=4000, text8 100k, 3 seeds, cv 0.005). "
            "This refutes the strong-form hypothesis that shared-W is "
            "architecturally sufficient. Going from 2L to 3L does NOT help "
            "(7.168 -> 7.177; saturates at 2L). Single-layer (7.089) BEATS 2L-indep "
            "on BPC: layer-composition is BPC-NEGATIVE at N=8192; the architectural "
            "lift is over SHARED-W only, not over single-layer.\n\n"
            "REVIVAL PATHS (route to research-lane):\n"
            "  (i) top1-targeted readout on existing indep_2L W matrices "
            "(BPC-tuned T,lambda may hide top1 lift; matches angle 1 from row 708)\n"
            "  (ii) cross-layer indep cf-RPE x STDP heterogeneous compose "
            "(fair_harness STDP HET top1=0.2368 candidate for super-additive)\n"
            "  (iii) indep_2L + cleanup-load-bearing (modern-Hopfield over W)\n"
            "  (iv) N_STEPS>=15000 extension on indep_2L (does BPC gap widen?)\n\n"
            "TIER: MEASURED_MECHANISM; delta=0; mechanism preserved for downstream "
            "compose tests + revival; chain-grade path open via top1-targeted readout."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "verdict": (
                "MEASURED_MECHANISM_cross_layer_compose_LM_v2_RESCUE_FULL_3seeds_"
                "7_17_23_N_DIM_8192_V_4000_text8_100k_indep_2L_bpc_7p168_cv_0p005_"
                "shared_W_bpc_7p544_cv_0p0008_indep_vs_shared_gap_plus_0p376_BPC_"
                "indep_vs_single_lift_minus_0p079_BPC_top1_indep_2L_0p2324_vs_"
                "unigram_0p2171_lift_plus_0p0153_abs_plus_7p05_pct_rel_vs_n1_v3_"
                "chain_grade_bar_plus_61p6_pct_rel_0p11x_bar_cell_self_verdict_"
                "READOUT_DEGENERATE_RETIRED_as_verdict_classifier_instrument_bug_"
                "raw_at_T1_11p55_mathematically_forced_near_vocab_entropy_at_"
                "tuned_T_0p05_director_CHAIN_GRADE_request_REJECTED_per_Fix28_"
                "default_under_claim_BPC_chain_grade_BLOCKED_META_HARNESS_RIGGED_"
                "row_698_top1_chain_grade_BLOCKED_n1_v3_row_699_bar_precedent_"
                "cert_rows_707_708_MM_same_signature_past_48h_revival_via_top1_"
                "targeted_readout_OR_STDP_compose_OR_cleanup_load_bearing_OR_"
                "N_STEPS_15000_extension"
            ),
            "cell_commit": "6ba0ef08",
            "metrics_path": "data/exp_substrate_cross_layer_compose_LM_v2_RESCUE_FULL/metrics.json",
            "prereg_path": "preregs/2026-06-24_substrate_cross_layer_compose_LM_v2_RESCUE_FULL.md",
            "notes_path": NOTES_PATH_RULING,
            "verified_off_data": (
                "Cert-owner read detail.by_arm_agg + per_seed directly from "
                "metrics.json (no verdict_msg framing reliance). Per-seed gaps: "
                "s7: shared 7.5509 - indep_2L 7.1313 = 0.4196; s17: 7.5456 - "
                "7.2165 = 0.3291; s23: 7.5361 - 7.1559 = 0.3802. Mean gap "
                "+0.3763 across 3 seeds; cv tight on both arms (shared cv=0.0008, "
                "indep_2L cv=0.005). top1 indep_2L per_seed: 0.2449, 0.2172, "
                "0.2350; mean 0.2324 vs unigram 0.2171 (+0.0153 abs); 0.11x of "
                "n1_v3 chain-grade bar +61.6%. raw_bpc_at_T1_L1 indep_2L "
                "per_seed: 11.5627, 11.5586, 11.5342; mean 11.5518; shared_W "
                "raw mean 11.6353. zero_llm_calls_at_inference=True. run_mode='full'."
            ),
            "honest_scope": (
                "Full-scale production-LM RESCUE cell at N_DIM=8192 V=4000 text8 "
                "100k 3 seeds. DOES measure independent-W beats shared-W by "
                "+0.376 BPC at production scale (cv 0.005). DOES measure 3L "
                "saturates vs 2L (no additional gain). DOES measure single-layer "
                "BEATS 2L-indep on BPC (layer-composition is BPC-NEGATIVE at "
                "N=8192). DOES NOT clear BPC chain-grade bar (pre-reg bar <= "
                "6.95; observed 7.168). DOES NOT clear top1 chain-grade bar "
                "(observed +7% rel; n1_v3 bar +61.6% rel). DOES NOT measure "
                "compose with STDP / cleanup / N_STEPS>=15000 extension (4 "
                "revival paths open). Per Fix #28 default under-claim + "
                "META_HARNESS_RIGGED precedent + cert rows 707/708 same signature: "
                "tier MEASURED_MECHANISM, NOT chain-grade. Director's CHAIN_GRADE "
                "re-tier request rejected; READOUT_DEGENERATE label retired."
            ),
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N_DIM": 8192,
            "N_TRAIN": 100000,
            "N_HELD": 20000,
            "VOCAB_CAP": 4000,
            "N_STEPS": 1000,
            "CFRPE_LR": 0.5,
            "SPARSE_BIPOLAR_F": 0.05,
            "arms": [
                "ARM_UNIGRAM",
                "ARM_SINGLE_LAYER_CFRPE",
                "ARM_2_LAYER_INDEPENDENT_CFRPE",
                "ARM_3_LAYER_INDEPENDENT_CFRPE",
                "ARM_2_LAYER_SHARED_W_CFRPE",
            ],
            "best_indep_arm": "ARM_2_LAYER_INDEPENDENT_CFRPE",
            "best_indep_bpc": 7.1679,
            "best_indep_cv": 0.005,
            "single_bpc": 7.0888,
            "shared_W_bpc": 7.5442,
            "indep_vs_shared_gap_bpc": 0.3763,
            "indep_vs_single_lift_bpc": -0.0791,
            "indep_2L_top1": 0.2324,
            "unigram_top1": 0.2171,
            "top1_lift_over_unigram_abs": 0.0153,
            "top1_lift_over_unigram_rel_pct": 7.05,
            "n1_v3_chain_grade_top1_bar_rel_pct": 61.6,
            "fraction_of_top1_chain_grade_bar": 0.1145,
            "cell_self_verdict": "READOUT_DEGENERATE",
            "cell_self_verdict_retired_as_instrument_bug": True,
            "director_request_tier": "CHAIN_GRADE",
            "director_request_rejected_per_fix28_default_under_claim": True,
            "precedent_cert_rows": [698, 699, 707, 708],
            "vocab_entropy_uniform_bits": 11.9658,
            "raw_bpc_at_T1_L1_indep_2L_mean": 11.5518,
            "raw_bpc_at_T1_L1_shared_W_mean": 11.6353,
            "revival_paths_open": [
                "top1_targeted_readout_on_existing_indep_2L_W_matrices",
                "indep_2L_cfrpe_x_STDP_heterogeneous_compose",
                "indep_2L_plus_cleanup_load_bearing_modern_hopfield",
                "N_STEPS_15000_extension_does_BPC_gap_widen",
            ],
            "device": "cuda",
            "elapsed_s": 808.8,
            "run_mode": "full",
            "zero_llm_calls_at_inference": True,
            "n_llm_calls": 0,
            "composes_with": [
                "T3/META_HARNESS_RIGGED_substrate_LM_readout_uncalibrated_temperature_BPC_wrong_metric_2026-06-23",
                "T3/EXP_n1_concept_lm_substrate_native_token_decode_v3_TOP1_CG",
                "T3/EXP_substrate_cfrpe_n_steps_curve_v1_MM",
                "T3/EXP_substrate_cfrpe_per_token_adaptive_lr_v1_MM",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_not_verdict_msg_framing",
                "Fix_28_default_under_claim_by_construction_saturation",
                "META_HARNESS_RIGGED_cert_row_698_BPC_wrong_metric",
                "n1_v3_cert_row_699_top1_chain_grade_bar",
                "cert_row_707_708_MM_same_signature_precedent",
                "USER_drill_5x_disparate_fields_readout_degeneracy_2026-06-25",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
        },
    )


def build_hub_spoke_E1_v2_diverse_algorithm_MM() -> Atom:
    return Atom(
        id="T3/EXP_substrate_hub_spoke_E1_v2_diverse_algorithm_MM",
        name=(
            "Hub-spoke E1 v2 diverse-algorithm -- MEASURED_MECHANISM (SoftHebb "
            "spoke recon_err=NaN across all 3 seeds x 4 arms; cf-RPE routing "
            "gates collapse to [0.96, 0.03, 0.01] picking broken spoke 0; "
            "3-spoke arms fall back to unigram-equivalent bpc=7.7378; M3 "
            "bundle-health-check gap, NOT substrate-mechanism failure)"
        ),
        description=(
            "Cell self-verdict MIDDLE_BAND (READOUT_DEGENERATE_NOT_SUBSTRATE_"
            "FAILURE). Cert-owner ruling: MEASURED_MECHANISM. Verify-OFF-DATA "
            "confirms all drill claims off metrics.json.\n\n"
            "INSTRUMENT BUG (confirmed off per_seed encoder_meta):\n"
            "  SoftHebb spoke spoke_recon_err = NaN across all 3 seeds [7, 17, 23] "
            "x all 3 arms that include SoftHebb (DIVERSE_ALGO, DIVERSE_PLUS_FPE, "
            "DIVERSE_WITH_CFRPE_GATING). Other spokes well-defined:\n"
            "    chartrigram_x_random_indexing recon_err ~1.0002\n"
            "    path_c_pc_3layer            recon_err ~92.3\n"
            "    fractional_power_encoding   recon_err ~1.476\n"
            "  cf-RPE gates per seed:\n"
            "    seed 7:  [0.9587, 0.0323, 0.0090]\n"
            "    seed 17: [0.9552, 0.0357, 0.0091]\n"
            "    seed 23: [0.9526, 0.0356, 0.0117]\n"
            "  Gates collapse to spoke 0 (SoftHebb with NaN keys) across all 3 "
            "seeds; cfrpe_gate_std_over_mean ~ 1.62 (extreme dispersion).\n\n"
            "DOWNSTREAM IMPACT:\n"
            "  All 3 spoke-bundle arms bpc = 7.7378 exactly = unigram bpc 7.7378 "
            "(cv 0.0000 across seeds). top1 identical to unigram 0.2171. The "
            "substrate falls back to unigram-equivalent output when routing "
            "selects NaN keys -- structural failure mode signature, not capability.\n"
            "  Baseline path_C single arm bpc = 7.6665 cv 0.0016 (line 62) is "
            "well-defined (no SoftHebb in path; only path_c_pc_3layer spoke), "
            "confirming the NaN problem is local to SoftHebb implementation.\n\n"
            "WHY MEASURED_MECHANISM (M3 bundle-health-check gap):\n"
            "  The cell measured an INSTRUMENT FAILURE (broken SoftHebb spoke "
            "wins cf-RPE routing), not a substrate-mechanism failure. The "
            "hub-spoke architecture itself is untestable from this cell because "
            "the cf-RPE gate selected a spoke with NaN keys -- no information "
            "flowed through the routing layer. M3 lesson: when a spoke can "
            "return NaN keys, the hub-spoke routing has no signal to "
            "discriminate against it; a per-spoke health-check gate (drop any "
            "spoke with NaN keys before routing) is structurally load-bearing.\n\n"
            "REVIVAL PATH (load-bearing for chain-grade tier):\n"
            "  (i) Fix SoftHebb k-WTA recon: likely an iteration count / lr / "
            "threshold init issue producing zero-norm keys -> recon_err NaN. "
            "Inspect n_updates=98 (suspicious for 100k tokens at typical k-WTA "
            "init). Compare against canonical SoftHebb impl.\n"
            "  (ii) Add per-spoke health-check gate: any spoke with NaN keys OR "
            "recon_err > threshold drops out before routing.\n"
            "  (iii) Re-run hub-spoke E1 v3 with fix + health-check + 3 seeds.\n\n"
            "TIER: MEASURED_MECHANISM; delta=0; does NOT rule hub-spoke mechanism "
            "dead; revival open at SoftHebb fix + health-check + re-run."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "instrument_bug_mm",
            "instrument_bug": True,
            "verdict": (
                "MEASURED_MECHANISM_hub_spoke_E1_v2_diverse_algorithm_3seeds_"
                "7_17_23_N_DIM_8192_V_4000_text8_100k_SoftHebb_spoke_recon_err_"
                "NaN_across_all_seeds_all_4_arms_cf_RPE_gates_collapse_0p96_"
                "0p03_0p01_picking_broken_spoke_0_all_3_spoke_bundle_arms_bpc_"
                "7p7378_eq_unigram_7p7378_cv_0p000_substrate_falls_back_to_"
                "unigram_equivalent_when_routing_picks_NaN_keys_baseline_path_C_"
                "single_arm_bpc_7p6665_well_defined_NaN_local_to_SoftHebb_M3_"
                "bundle_health_check_gap_NOT_substrate_mechanism_failure_revival_"
                "at_SoftHebb_fix_plus_per_spoke_health_check_gate_plus_re_run"
            ),
            "cell_commit": "abc5887b",
            "metrics_path": "data/exp_substrate_hub_spoke_E1_v2_diverse_algorithm/metrics.json",
            "prereg_path": "preregs/2026-06-24_substrate_hub_spoke_E1_v2_diverse_algorithm.md",
            "notes_path": NOTES_PATH_RULING,
            "verified_off_data": (
                "Cert-owner read per_seed encoder_meta + cfrpe_gates directly "
                "from metrics.json. NaN at spoke_recon_err confirmed at lines "
                "241, 298, 370, 488, 545, 617, 735, 792, 864 (every seed x "
                "every arm that includes SoftHebb). cfrpe_gates confirmed at "
                "lines 356-359, 603-606, 850-853 (3 seeds; each collapses to "
                "spoke 0 dominant). cfrpe_gate_std_over_mean = [1.6251, 1.6161, "
                "1.6093] (extreme dispersion = single-spoke dominance). All 3 "
                "spoke arms bpc_best = 7.7378 = unigram exactly (cv 0.0000). "
                "Baseline path_C single arm bpc 7.6665 cv 0.0016 (no SoftHebb) "
                "well-defined, isolating NaN to SoftHebb implementation. "
                "zero_llm_calls_at_inference=True. run_mode='full'."
            ),
            "honest_scope": (
                "Full-scale hub-spoke v2 RESCUE at N_DIM=8192 V=4000 text8 100k "
                "3 seeds. DOES measure SoftHebb k-WTA spoke produces NaN "
                "recon_err structurally across all seeds. DOES measure cf-RPE "
                "routing gate collapses to broken spoke when given NaN keys "
                "(gate_std_over_mean ~1.62; spoke 0 weight ~0.96). DOES measure "
                "spoke-bundle output collapses to unigram-equivalent when "
                "routing selects NaN keys. DOES NOT measure hub-spoke "
                "composition mechanism (untestable until SoftHebb fixed). DOES "
                "NOT rule the diverse-algorithm-spoke approach dead; revival "
                "via SoftHebb fix + health-check gate is uncontaminated by "
                "this run. Per Fix #28 default under-claim + by-construction-"
                "saturation: tier MEASURED_MECHANISM (instrument bug class), "
                "NOT honest-negative on the hub-spoke architecture itself."
            ),
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N_DIM": 8192,
            "N_TRAIN": 100000,
            "N_HELD": 20000,
            "VOCAB_CAP": 4000,
            "SPARSE_BIPOLAR_F": 0.02,
            "SOFTHEBB_K_WTA": 64,
            "SOFTHEBB_LR": 0.01,
            "arms": [
                "ARM_BASELINE_PATH_C_SINGLE",
                "ARM_HUB_3SPOKE_DIVERSE_ALGO",
                "ARM_HUB_3SPOKE_DIVERSE_PLUS_FPE",
                "ARM_HUB_3SPOKE_DIVERSE_WITH_CFRPE_GATING",
            ],
            "baseline_path_C_single_bpc": 7.6665,
            "baseline_path_C_cv": 0.0016,
            "hub_3spoke_diverse_algo_bpc": 7.7378,
            "hub_3spoke_diverse_plus_FPE_bpc": 7.7378,
            "hub_3spoke_diverse_with_cfrpe_gating_bpc": 7.7378,
            "unigram_bpc": 7.7378,
            "softhebb_spoke_recon_err_NaN_all_seeds_all_arms": True,
            "cfrpe_gates_mean_across_seeds": [0.9555, 0.0345, 0.0099],
            "cfrpe_gate_std_over_mean_mean_across_seeds": 1.6168,
            "all_3_spoke_arms_bpc_eq_unigram_to_4_decimals": True,
            "cv_max_across_spoke_arms": 0.0000,
            "instrument_bug_root_cause": (
                "softhebb_kwta_spoke_returns_NaN_keys_n_updates_98_only_likely_"
                "iteration_count_or_lr_or_threshold_init_issue_producing_zero_"
                "norm_keys_causing_recon_err_NaN_propagation_through_cf_RPE_"
                "gate_routing"
            ),
            "revival_paths_open": [
                "fix_softhebb_kwta_n_updates_lr_threshold_init",
                "add_per_spoke_health_check_gate_drop_NaN_keys_before_routing",
                "rerun_hub_spoke_E1_v3_with_fix_plus_health_check_3_seeds",
            ],
            "cell_self_verdict": "MIDDLE_BAND",
            "cell_self_verdict_subclassified_to_MM_by_skunkworks": True,
            "device": "cuda",
            "run_mode": "full",
            "zero_llm_calls_at_inference": True,
            "n_llm_calls": 0,
            "composes_with": [
                "T3/META_M3_bundle_health_check_NaN_spoke_can_win_cf_RPE_routing",
                "T3/META_phase_diagram_action_at_any_position_v1",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_not_verdict_msg_framing",
                "Fix_28_default_under_claim_by_construction_saturation_not_HN",
                "drill_5x_disparate_fields_2026-06-25_anchor_2_SoftHebb_NaN",
                "USER_drill_5x_disparate_fields_readout_degeneracy_2026-06-25",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
        },
    )


def build_compose_heterogeneous_routing_v2_RESCUE_MM() -> Atom:
    return Atom(
        id="T3/EXP_substrate_compose_heterogeneous_routing_v2_RESCUE_MM",
        name=(
            "Compose heterogeneous routing v2 RESCUE -- MEASURED_MECHANISM "
            "(rail referent N_DIM=8192 N_TRAIN=100k 3-seed cuda; v2 ran "
            "N_DIM=4096 N_TRAIN=50k 2-seed cpu; +0.35 BPC drift vs tol 0.05 "
            "explained by half-N capacity scaling; ARM_FREQ_ROUTED_K2 lift "
            "-0.224 BPC over in-cell baseline is direction-correct; M2 "
            "tight-rail-from-different-config can mask direction-correct lift)"
        ),
        description=(
            "Cell self-verdict HARD_FAIL_PROVENANCE on rail drift. Cert-owner "
            "ruling: MEASURED_MECHANISM (instrument calibration, NOT mechanism "
            "failure). Verify-OFF-DATA confirms drill claims off both metrics.\n\n"
            "RAIL REFERENT CONFIG (fair_harness_substrate_as_lm_v1 / cert row 698):\n"
            "  N_DIM = 8192, N_TRAIN = 100000, n_seeds = 3, seeds = [7, 17, 23]\n"
            "  sparse_f = 0.050, device = cuda\n"
            "  ARM_SUBSTRATE_SPARSE_BIPOLAR bpc_best_mean = 7.3065 cv 0.0018\n"
            "  CONFIRMED off data/exp_fair_harness_substrate_as_lm_v1/metrics.json\n\n"
            "v2 RESCUE CELL CONFIG:\n"
            "  N_DIM = 4096 (2x reduction), N_TRAIN = 50000 (2x reduction)\n"
            "  n_seeds = 2, seeds = [7, 17] (1 fewer seed)\n"
            "  sparse_f = 0.05, device = cpu\n"
            "  ARM_BASELINE_FAIR_HARNESS bpc_best_mean = 7.6563 cv 0.0003\n"
            "  Drift +0.3498 vs rail 7.3065; tolerance 0.05 -> HARD_FAIL_PROVENANCE.\n\n"
            "PER-ARM (2 seeds [7, 17]):\n"
            "  ARM_UNIGRAM               bpc=7.863  (off cell vs 7.738 at FULL N -- "
            "different unigram because N_TRAIN=50k vs 100k)\n"
            "  ARM_BASELINE_FAIR_HARNESS bpc=7.6563 cv=0.0003 (rail drift +0.35)\n"
            "  ARM_THETA_PHASE_TWO_W     bpc=7.5528 cv=0.0025 (-0.1035 vs base)\n"
            "  ARM_FREQ_ROUTED_K2        bpc=7.4321 cv=0.0031 (-0.2242 vs base)\n"
            "  ARM_ORTHOG_SUBSPACE       bpc=7.7728 cv=0.0138 (+0.1165 vs base)\n\n"
            "WHY MEASURED_MECHANISM:\n"
            "  Direction-correct underlying signal: ARM_FREQ_ROUTED_K2 lift "
            "-0.224 BPC over in-cell baseline (best_het) is direction-correct "
            "evidence that frequency-routed K=2 composition outperforms theta-"
            "phase two-W and orthogonal-subspace at half-N. The rail-drift "
            "instrument-gate is correct to fire (config mismatch is real), but "
            "the underlying mechanism signal is intact. M2 lesson: when a "
            "rail is set from a different config and the cell runs under "
            "reduced N, tight rail-tolerance can fire HARD_FAIL_PROVENANCE "
            "even when the mechanism signal is direction-correct beneath.\n\n"
            "REVIVAL PATH (load-bearing for chain-grade tier):\n"
            "  Re-run v3 at fair_harness-matched config: N_DIM=8192, N_TRAIN=100k, "
            "3 seeds [7, 17, 23], device=cuda. The cell author already shipped "
            "the FREQ_ROUTED_K2 architecture; only the runtime parameters need "
            "fair_harness-matching. If ARM_FREQ_ROUTED_K2 then clears HARD_PASS "
            "BPC band at chain-grade cv, route to chain-grade promotion at "
            "matched-config replication.\n\n"
            "TIER: MEASURED_MECHANISM; delta=0; HARD_FAIL_PROVENANCE preserved "
            "as cell self-verdict; mechanism characterization (direction-correct "
            "+0.224 BPC FREQ_K2 lift over half-N baseline) retained; revival "
            "via matched-config v3."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "instrument_calibration_mm",
            "instrument_calibration_bug": True,
            "verdict": (
                "MEASURED_MECHANISM_compose_heterogeneous_routing_v2_RESCUE_"
                "2seeds_7_17_N_DIM_4096_N_TRAIN_50k_cpu_rail_fair_harness_"
                "N_DIM_8192_N_TRAIN_100k_3seed_cuda_drift_plus_0p3498_vs_"
                "tol_0p05_HARD_FAIL_PROVENANCE_fired_correctly_at_2x_N_2x_"
                "data_half_capacity_scaling_underlying_signal_direction_"
                "correct_ARM_FREQ_ROUTED_K2_bpc_7p4321_cv_0p0031_lift_minus_"
                "0p224_BPC_over_baseline_7p6563_outperforms_THETA_PHASE_two_W_"
                "7p5528_and_ORTHOG_SUBSPACE_7p7728_M2_tight_rail_from_different_"
                "config_can_mask_direction_correct_lift_revival_at_matched_"
                "config_v3_N_DIM_8192_N_TRAIN_100k_3seed_cuda_replication"
            ),
            "cell_commit": "b143c179",
            "metrics_path": "data/exp_substrate_compose_heterogeneous_routing_v2_RESCUE/metrics.json",
            "rail_referent_metrics_path": "data/exp_fair_harness_substrate_as_lm_v1/metrics.json",
            "prereg_path": "preregs/2026-06-24_substrate_compose_heterogeneous_routing_v2_RESCUE.md",
            "notes_path": NOTES_PATH_RULING,
            "verified_off_data": (
                "Cert-owner read both cells' metrics.json directly. Rail "
                "referent config confirmed (fair_harness_substrate_as_lm_v1 "
                "lines 7, 9, 39, 149): N_DIM=8192 N_TRAIN=100000 3 seeds cuda "
                "sparse_f=0.050 ARM_SUBSTRATE_SPARSE_BIPOLAR bpc 7.3065 cv 0.0018. "
                "v2_RESCUE config confirmed (lines 9, 10, 42, 16, 8): N_DIM=4096 "
                "N_TRAIN=50000 seeds [7, 17] sparse_f=0.05 device='cpu'. "
                "ARM_BASELINE_FAIR_HARNESS per_seed: s7 bpc 7.6587, s17 bpc "
                "7.654; mean 7.6563 cv 0.0003. Drift 7.6563 - 7.3065 = 0.3498. "
                "ARM_FREQ_ROUTED_K2 per_seed: s7 bpc 7.4553, s17 bpc 7.4088; "
                "mean 7.4321 cv 0.0031; lift over in-cell baseline -0.2242 BPC. "
                "Outperforms ARM_THETA_PHASE_TWO_W mean 7.5528 and "
                "ARM_ORTHOG_SUBSPACE mean 7.7728. zero_llm_calls_at_inference=True. "
                "run_mode='full'."
            ),
            "honest_scope": (
                "v2 RESCUE at HALF the rail referent's N_DIM and HALF its "
                "N_TRAIN with 1 fewer seed and cpu device. DOES measure "
                "heterogeneous routing arm ordering at half-N (FREQ_K2 > "
                "THETA_TWO_W > ORTHOG_SUBSPACE in lift over baseline). DOES "
                "measure ARM_FREQ_ROUTED_K2 lift -0.2242 BPC over in-cell "
                "baseline cv 0.0031 (clean signal). DOES measure rail-drift "
                "+0.35 BPC vs tight tolerance 0.05 (HARD_FAIL_PROVENANCE fires "
                "correctly as instrument-calibration gate). DOES NOT measure "
                "heterogeneous-routing benefit at production scale N_DIM=8192 "
                "N_TRAIN=100k (the rail referent's config) -- the half-N "
                "discriminator may be weaker than full-N. DOES NOT test K>2 "
                "routing or modern-Hopfield cleanup stacked above. DOES NOT "
                "rule heterogeneous-routing mechanism dead; revival at "
                "matched-config v3 is uncontaminated. Per Fix #28 default "
                "under-claim + by-construction-saturation: tier MEASURED_"
                "MECHANISM, NOT honest-negative."
            ),
            "n_seeds": 2,
            "seeds": [7, 17],
            "N_DIM": 4096,
            "N_TRAIN": 50000,
            "N_HELD": 10000,
            "VOCAB_CAP": 4000,
            "N_STEPS": 1000,
            "SPARSE_BIPOLAR_F": 0.05,
            "FREQ_ROUTE_RANK": 100,
            "FREQ_LR_HIGH": 0.5,
            "FREQ_LR_RARE": 0.2,
            "arms": [
                "ARM_BASELINE_FAIR_HARNESS",
                "ARM_THETA_PHASE_TWO_W",
                "ARM_FREQ_ROUTED_K2",
                "ARM_ORTHOG_SUBSPACE",
            ],
            "baseline_fair_harness_bpc": 7.6563,
            "theta_phase_two_W_bpc": 7.5528,
            "freq_routed_K2_bpc": 7.4321,
            "freq_routed_K2_cv": 0.0031,
            "orthog_subspace_bpc": 7.7728,
            "best_het_arm": "ARM_FREQ_ROUTED_K2",
            "best_het_lift_over_baseline_bpc": -0.2242,
            "rail_referent_bpc": 7.3065,
            "rail_referent_N_DIM": 8192,
            "rail_referent_N_TRAIN": 100000,
            "rail_referent_n_seeds": 3,
            "rail_referent_device": "cuda",
            "rail_referent_sparse_f": 0.050,
            "rail_drift_bpc": 0.3498,
            "rail_tolerance": 0.05,
            "rail_drift_explained_by_half_N_capacity_scaling": True,
            "cell_self_verdict": "HARD_FAIL_PROVENANCE",
            "cell_self_verdict_preserved_under_MM_subclassification": True,
            "revival_paths_open": [
                "matched_config_v3_N_DIM_8192_N_TRAIN_100k_3_seeds_cuda",
                "K_greater_than_2_routing_sweep_at_matched_config",
                "freq_routed_K2_plus_modern_hopfield_cleanup_stacked",
            ],
            "device": "cpu",
            "elapsed_s": 1916.5,
            "run_mode": "full",
            "zero_llm_calls_at_inference": True,
            "n_llm_calls": 0,
            "composes_with": [
                "T3/META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift",
                "T3/META_phase_diagram_action_at_any_position_v1",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_not_verdict_msg_framing",
                "Fix_28_default_under_claim_by_construction_saturation_not_HN",
                "verify_referent_discipline_rail_config_must_match",
                "drill_5x_disparate_fields_2026-06-25_anchor_3_rail_mismatch",
                "USER_drill_5x_disparate_fields_readout_degeneracy_2026-06-25",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
        },
    )


# ============================================================================
# Atom builders -- META rules (M1, M2, M3)
# ============================================================================

def build_meta_M1_verdict_classifier_use_tuned_metrics() -> Atom:
    return Atom(
        id="T3/META_M1_verdict_classifier_use_tuned_metrics_never_raw_at_T1",
        name=(
            "META M1: verdict classifiers must use tuned metrics, never "
            "raw_at_T1 (at T=1.0 lambda=1.0 untuned). raw_at_T1 is "
            "mathematically forced near vocab-entropy when tuned T << 1.0 "
            "regardless of substrate capability; degen-flag triggered on "
            "raw_at_T1 is an instrument bug, not a substrate failure mode."
        ),
        description=(
            "RULE (cert-discipline, CERT-neutral): the readout-degenerate "
            "verdict classifier that checks raw_bpc_at_T1_L1 against vocab-"
            "entropy uniform must instead check the TUNED bpc_best (at the T "
            "and lambda that minimize dev BPC) against vocab-entropy. \n\n"
            "RATIONALE: raw_bpc_at_T1_L1 is the bpc obtained at T=1.0 and "
            "lambda=1.0 (untuned). When the tuned operating point is at much "
            "lower T (e.g., T=0.05), the wave14b CE_floor math forces "
            "raw_at_T1 toward vocab-entropy regardless of substrate signal. "
            "A capability arm and a non-capability arm at the same T have "
            "similar raw_at_T1, but very different tuned BPC.\n\n"
            "OBSERVED INSTANCE: substrate_cross_layer_compose_LM_v2_RESCUE_FULL "
            "(2026-06-24) tuned BPC indep_2L = 7.168 (4.8 bits below vocab-"
            "entropy 11.97) BUT raw_at_T1_L1 = 11.55 (within 0.5 of 11.97) -> "
            "READOUT_DEGENERATE incorrectly fired. The shared-W arm, which "
            "underperforms by +0.376 BPC architecturally, reads raw_at_T1 = "
            "11.64 (HIGHER, closer to vocab-entropy) -- the worse arm reads "
            "HIGHER on the degen-classifier metric. The classifier is "
            "measurement-mode-confused.\n\n"
            "DISCIPLINE: every cell author MUST classify readout-degeneracy "
            "from tuned bpc_best, never from raw_at_T1. Cert-owner adds "
            "READOUT_DEGENERATE rebuttal check at landed-VET: if tuned "
            "bpc_best - vocab_entropy >= 0.5 bits, the degen-flag is an "
            "instrument bug; retire it.\n\n"
            "SCOPE: applies to all substrate-as-LM cells with TEMP_GRID + "
            "LAMBDA_GRID joint sweep. Does not apply to deterministic-readout "
            "cells (no temperature/lambda freedom)."
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline",
            "rule_id": "M1",
            "rule_category": "verdict_classifier_correctness",
            "rule_name": "verdict_classifier_use_tuned_metrics_never_raw_at_T1",
            "rule_text": (
                "Verdict classifiers in substrate-as-LM cells MUST use the "
                "tuned bpc_best (T*, lambda*) against vocab-entropy uniform "
                "to detect readout-degeneracy. Using raw_bpc_at_T1_L1 "
                "(untuned at T=1.0 lambda=1.0) systematically triggers false "
                "READOUT_DEGENERATE fires because raw_at_T1 is mathematically "
                "forced near vocab-entropy when the tuned operating point is "
                "at low T regardless of substrate capability."
            ),
            "rebuttal_check_for_skunkworks_landed_VET": (
                "if tuned bpc_best <= (vocab_entropy_uniform_bits - 0.5):"
                "  degen_flag is an instrument bug; retire it."
            ),
            "observed_instances": [
                "substrate_cross_layer_compose_LM_v2_RESCUE_FULL (2026-06-24): "
                "tuned BPC indep_2L=7.168, raw_at_T1=11.55, vocab_entropy=11.97. "
                "tuned BPC is 4.8 bits below uniform = NOT collapse. Cell "
                "wrongly fired READOUT_DEGENERATE; cert-owner retired the label."
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "honest_scope": (
                "Applies to substrate-as-LM cells with TEMP_GRID + LAMBDA_GRID "
                "joint sweep producing both raw_at_T1 AND tuned bpc_best metrics. "
                "Does NOT apply to deterministic-readout cells (no freedom)."
            ),
            "composes_with": [
                "T3/META_HARNESS_RIGGED_substrate_LM_readout_uncalibrated_temperature_BPC_wrong_metric_2026-06-23",
            ],
            "cites": [
                "USER_drill_5x_disparate_fields_readout_degeneracy_2026-06-25",
                "exp_substrate_cross_layer_compose_LM_v2_RESCUE_FULL_observed_instance",
            ],
        },
    )


def build_meta_M2_tight_rail_from_different_config() -> Atom:
    return Atom(
        id="T3/META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift",
        name=(
            "META M2: HARD_FAIL_PROVENANCE on tight rail from different "
            "config can mask direction-correct lift in mechanism arms; "
            "rail tolerance must match the rail-referent config exactly "
            "(N_DIM, N_TRAIN, n_seeds, device) or be widened to absorb "
            "capacity-scaling drift."
        ),
        description=(
            "RULE (cert-discipline, CERT-neutral): when a HARD_FAIL_PROVENANCE "
            "gate is set against a rail referent measured at a DIFFERENT "
            "config (different N_DIM, N_TRAIN, n_seeds, or device), the "
            "tolerance must either:\n"
            "  (a) match the referent config exactly, or\n"
            "  (b) be widened by the expected capacity-scaling drift "
            "(approximately +0.15 BPC per 2x N reduction at production-LM scale).\n"
            "Otherwise, HARD_FAIL_PROVENANCE will fire on instrument-"
            "calibration drift even when the underlying mechanism signal is "
            "direction-correct.\n\n"
            "RATIONALE: rail referents are typically set at the cleanest "
            "available production-scale config (e.g., fair_harness N_DIM=8192 "
            "N_TRAIN=100k 3-seed cuda). When a rescue cell runs at reduced "
            "N (e.g., to fit a CPU-time budget), the in-cell baseline arm "
            "naturally drifts by the capacity-scaling penalty. A tight "
            "tolerance (e.g., 0.05 BPC) measured at the FULL config will "
            "fire on the reduced-N cell's baseline even when the mechanism "
            "arm shows direction-correct lift.\n\n"
            "OBSERVED INSTANCE: substrate_compose_heterogeneous_routing_v2_"
            "RESCUE (2026-06-24): rail referent fair_harness at N_DIM=8192 "
            "N_TRAIN=100k 3-seed cuda; cell ran at N_DIM=4096 N_TRAIN=50k "
            "2-seed cpu. ARM_BASELINE drifted +0.35 BPC vs rail tol 0.05 -> "
            "HARD_FAIL_PROVENANCE fired correctly as an instrument-calibration "
            "gate. But ARM_FREQ_ROUTED_K2 showed -0.224 BPC direction-correct "
            "lift over the in-cell baseline (cv 0.0031, 2 seeds), beating "
            "two other het-routing arms. The mechanism signal was real "
            "beneath the rail-instrument failure.\n\n"
            "DISCIPLINE: cell authors MUST either (a) match rail-referent "
            "config exactly OR (b) widen tolerance by predicted capacity-"
            "scaling drift. Cert-owner adds rail-config-match check at "
            "landed-VET: if rail tolerance < predicted_capacity_scaling_drift "
            "(roughly 0.15 BPC per 2x N reduction), HARD_FAIL_PROVENANCE is "
            "an instrument-calibration MM, not mechanism failure.\n\n"
            "SCOPE: applies to all cells with provenance_check_active=True + "
            "rail referent measured at non-matching config. Does not apply "
            "to within-config replications (same N_DIM N_TRAIN n_seeds device)."
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline",
            "rule_id": "M2",
            "rule_category": "rail_provenance_calibration",
            "rule_name": "tight_rail_from_different_config_can_mask_direction_correct_lift",
            "rule_text": (
                "When HARD_FAIL_PROVENANCE rail is set from a different-config "
                "referent, the tolerance MUST be widened by predicted "
                "capacity-scaling drift (roughly +0.15 BPC per 2x N reduction "
                "at production-LM scale) OR the cell MUST match the referent "
                "config exactly. Otherwise the provenance gate fires on "
                "instrument-calibration drift while masking direction-correct "
                "mechanism lift beneath."
            ),
            "rebuttal_check_for_skunkworks_landed_VET": (
                "if cell config != rail_referent_config AND rail_tolerance < "
                "predicted_capacity_scaling_drift: HARD_FAIL_PROVENANCE is "
                "instrument-calibration MM. Verify direction-correct mechanism "
                "signal off per-arm before ruling honest-negative."
            ),
            "predicted_capacity_scaling_drift_rule_of_thumb": (
                "roughly +0.15 BPC per 2x N_DIM reduction; +0.15 BPC per 2x "
                "N_TRAIN reduction; additional noise from cpu vs cuda "
                "quantization +0.01-0.05 BPC"
            ),
            "observed_instances": [
                "substrate_compose_heterogeneous_routing_v2_RESCUE (2026-06-24): "
                "rail referent fair_harness N_DIM=8192 N_TRAIN=100k 3-seed "
                "cuda 7.3065 tol 0.05; cell ran N_DIM=4096 N_TRAIN=50k 2-seed "
                "cpu; drift +0.35 vs tol 0.05; underlying ARM_FREQ_ROUTED_K2 "
                "direction-correct -0.224 BPC over in-cell baseline."
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "honest_scope": (
                "Applies to cells with provenance_check_active=True + rail "
                "referent measured at non-matching config. Does NOT apply to "
                "within-config replications."
            ),
            "composes_with": [
                "T3/META_phase_diagram_action_at_any_position_v1",
            ],
            "cites": [
                "USER_drill_5x_disparate_fields_readout_degeneracy_2026-06-25",
                "exp_substrate_compose_heterogeneous_routing_v2_RESCUE_observed_instance",
                "exp_fair_harness_substrate_as_lm_v1_rail_referent",
            ],
        },
    )


def build_meta_M3_bundle_health_check_nan_spoke() -> Atom:
    return Atom(
        id="T3/META_M3_bundle_health_check_NaN_spoke_can_win_cf_RPE_routing",
        name=(
            "META M3: hub-spoke / spoke-bundle architectures with cf-RPE "
            "(or similar reward-based) routing require a per-spoke health-"
            "check gate before routing; a spoke returning NaN keys (e.g., "
            "from a broken k-WTA / k-NN init) will trivially win the "
            "routing softmax and collapse the bundle to unigram-equivalent "
            "fallback."
        ),
        description=(
            "RULE (cert-discipline, CERT-neutral): hub-spoke architectures "
            "with cf-RPE (or analogous gating) routing MUST validate each "
            "spoke's output health BEFORE feeding it to the routing layer:\n"
            "  (a) per-spoke recon_err must be finite (NaN -> drop)\n"
            "  (b) per-spoke key-norm must be > epsilon (zero-norm -> drop)\n"
            "  (c) per-spoke recon_err must be within a sensible range "
            "(>>1000 -> drop as numerically diverged)\n"
            "Otherwise the gate has no signal to discriminate against a "
            "broken spoke; the cf-RPE softmax will collapse to whichever "
            "spoke happens to dominate the (possibly garbage) features.\n\n"
            "RATIONALE: cf-RPE routing computes spoke weights from an "
            "expected-future-reward signal applied to each spoke's outputs. "
            "If a spoke returns NaN or zero-norm keys, the downstream "
            "recall is uninformative; the routing layer has no way to "
            "detect this from output alone. The signal that the spoke is "
            "broken comes from recon_err, but recon_err is computed during "
            "encoding, not during routing. A health-check gate must consume "
            "encoding-time diagnostics before routing fires.\n\n"
            "OBSERVED INSTANCE: substrate_hub_spoke_E1_v2_diverse_algorithm "
            "(2026-06-24): SoftHebb k-WTA spoke produced NaN recon_err "
            "across all 3 seeds [7, 17, 23] x all 3 arms that included "
            "SoftHebb. cf-RPE gates collapsed to [0.96, 0.03, 0.01] "
            "(spoke 0 dominant) across all seeds; all 3 spoke-bundle arms "
            "fell back to bpc=7.7378 identical to unigram. The hub-spoke "
            "architecture itself was untestable because routing selected "
            "the broken spoke; no health-check gate was in place to drop "
            "the NaN spoke before routing.\n\n"
            "DISCIPLINE: cell authors of hub-spoke / spoke-bundle "
            "architectures MUST include a per-spoke health-check gate as a "
            "pre-routing step. Smoke tests MUST verify the health-check "
            "gate fires when planted broken spokes are injected.\n\n"
            "SCOPE: applies to all hub-spoke / mixture-of-experts / spoke-"
            "bundle architectures with learned routing (cf-RPE, softmax-"
            "gating, gumbel-routing, etc). Does not apply to single-spoke "
            "or unconditional-routing architectures."
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline",
            "rule_id": "M3",
            "rule_category": "bundle_routing_robustness",
            "rule_name": "bundle_health_check_NaN_spoke_can_win_cf_RPE_routing",
            "rule_text": (
                "Hub-spoke / spoke-bundle architectures with learned routing "
                "(cf-RPE, softmax-gating, gumbel) MUST validate each spoke's "
                "output health before routing: drop spokes with NaN keys, "
                "zero-norm keys, or recon_err numerically diverged (>>1000). "
                "Otherwise a broken spoke can trivially win the routing "
                "softmax and collapse the bundle output to unconditional/"
                "unigram-equivalent fallback."
            ),
            "rebuttal_check_for_skunkworks_landed_VET": (
                "if any spoke's per_seed encoder_meta.spokes[i].spoke_recon_err "
                "is NaN OR zero-norm OR >>1000 across all seeds: cell "
                "result is M3 instrument-bug MM not honest-negative on the "
                "hub-spoke architecture itself."
            ),
            "required_pre_routing_gates": [
                "spoke_recon_err_is_finite",
                "spoke_key_norm_above_epsilon",
                "spoke_recon_err_within_sensible_range",
            ],
            "observed_instances": [
                "substrate_hub_spoke_E1_v2_diverse_algorithm (2026-06-24): "
                "SoftHebb k-WTA spoke NaN recon_err across all 3 seeds x 4 "
                "arms; cf-RPE gates collapsed to [0.96, 0.03, 0.01] picking "
                "broken spoke 0; all spoke-bundle arms fell back to "
                "bpc=7.7378 unigram-equivalent."
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "honest_scope": (
                "Applies to all hub-spoke / mixture-of-experts / spoke-bundle "
                "architectures with learned routing (cf-RPE, softmax, gumbel, "
                "etc). Does NOT apply to single-spoke or unconditional-routing "
                "architectures."
            ),
            "composes_with": [
                "T3/META_phase_diagram_action_at_any_position_v1",
            ],
            "cites": [
                "USER_drill_5x_disparate_fields_readout_degeneracy_2026-06-25",
                "exp_substrate_hub_spoke_E1_v2_diverse_algorithm_observed_instance",
            ],
        },
    )


# ============================================================================
# Safe add helper
# ============================================================================

def safe_add_with_ledger(atom: Atom, source: str, note: str,
                         notes_path: str, metrics_path: str, verdict_text: str,
                         atom_id_full: str, cell_commit: str):
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent): {atom.id} already present.")
    else:
        print(f"  ADDING atom: {atom.id}")
        ps.add_atom(atom, source=source, note=note)
        ps2 = PartitionedStore(STORE_ROOT)
        atoms = list(ps2.all_atoms())
        found = next((a for a in atoms if a.id == atom.id), None)
        if found is None:
            print("  FAIL: atom not found post-add")
            return (False, None)
        md = found.metadata or {}
        expected_pq = (atom.metadata or {}).get("provenance_quality")
        if md.get("provenance_quality") != expected_pq:
            print(f"  FAIL: pq mismatch (expected {expected_pq}, got {md.get('provenance_quality')})")
            return (False, None)
        print(f"  PASS: round-trip OK (pq={expected_pq})")

    ps_live = PartitionedStore(STORE_ROOT)
    live_cert = sum(
        1 for a in ps_live.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )

    row = build_measured_mechanism_row(
        atom_id=atom_id_full, cell_commit=cell_commit, verdict=verdict_text,
        notes_path=notes_path, metrics_path=metrics_path,
        atomized_by=ATOMIZED_BY, note=note,
    )

    print(
        f"  appending cert-ledger row (op={row['op']} status={row['cert_status']} "
        f"delta={row['cert_increment_delta']})"
    )
    try:
        h = append_cert_ledger_row(
            row,
            expected_cert_n_pre=live_cert,
            expected_cert_n_post=live_cert,
        )
        print(f"  row_hash={h}")
        return (True, h)
    except Exception as e:
        print(f"  FAIL: ledger append errored: {e}")
        return (False, None)


# ============================================================================
# Main plan
# ============================================================================

ATOM_PLAN = [
    # (builder, notes_path, metrics_path, verdict_text, cell_commit, ledger_note)
    (
        build_cross_layer_compose_LM_v2_RESCUE_FULL_MM,
        NOTES_PATH_RULING,
        "data/exp_substrate_cross_layer_compose_LM_v2_RESCUE_FULL/metrics.json",
        "READOUT_DEGENERATE_retired_skunkworks_MM_override_director_CHAIN_GRADE_rejected",
        "6ba0ef08",
        (
            "MM_cross_layer_compose_LM_v2_RESCUE_FULL_indep_W_beats_shared_W_"
            "plus_0p376_BPC_production_scale_cv_0p005_3_seeds_BPC_chain_grade_"
            "BLOCKED_META_HARNESS_RIGGED_top1_chain_grade_BLOCKED_0p11x_n1_v3_"
            "bar_director_CHAIN_GRADE_rejected_per_Fix28_default_under_claim_"
            "READOUT_DEGENERATE_retired_as_verdict_classifier_instrument_bug_"
            "revival_top1_targeted_readout_STDP_compose_cleanup_load_bearing"
        ),
    ),
    (
        build_hub_spoke_E1_v2_diverse_algorithm_MM,
        NOTES_PATH_RULING,
        "data/exp_substrate_hub_spoke_E1_v2_diverse_algorithm/metrics.json",
        "MIDDLE_BAND_skunkworks_subclassified_to_MM_softhebb_NaN_spoke_wins_cfrpe_routing",
        "abc5887b",
        (
            "MM_hub_spoke_E1_v2_diverse_algorithm_SoftHebb_spoke_recon_err_NaN_"
            "all_3_seeds_all_arms_cfrpe_gates_collapse_0p96_0p03_0p01_picking_"
            "broken_spoke_0_all_3_spoke_bundle_arms_bpc_7p7378_eq_unigram_cv_0_"
            "baseline_path_C_single_well_defined_7p6665_NaN_local_to_SoftHebb_"
            "M3_bundle_health_check_gap_revival_SoftHebb_fix_plus_health_check"
        ),
    ),
    (
        build_compose_heterogeneous_routing_v2_RESCUE_MM,
        NOTES_PATH_RULING,
        "data/exp_substrate_compose_heterogeneous_routing_v2_RESCUE/metrics.json",
        "HARD_FAIL_PROVENANCE_skunkworks_subclassified_to_MM_rail_calibration_mismatch",
        "b143c179",
        (
            "MM_compose_heterogeneous_routing_v2_RESCUE_rail_referent_fair_harness_"
            "N_DIM_8192_N_TRAIN_100k_3seed_cuda_cell_ran_N_DIM_4096_N_TRAIN_50k_"
            "2seed_cpu_drift_plus_0p35_BPC_explained_by_half_N_capacity_scaling_"
            "ARM_FREQ_ROUTED_K2_direction_correct_minus_0p224_BPC_lift_over_in_"
            "cell_baseline_cv_0p0031_M2_tight_rail_different_config_revival_at_"
            "matched_config_v3"
        ),
    ),
    (
        build_meta_M1_verdict_classifier_use_tuned_metrics,
        NOTES_PATH_RULING,
        "META_RULE_no_metrics_path",
        "META_M1_verdict_classifier_use_tuned_metrics_never_raw_at_T1",
        "skunkworks_atomize_tier_ruling_3cells_2026-06-25",
        (
            "META_M1_verdict_classifier_use_tuned_metrics_never_raw_at_T1_"
            "observed_in_cross_layer_compose_LM_v2_RESCUE_FULL_cell_wrongly_"
            "fired_READOUT_DEGENERATE_on_raw_at_T1_11p55_while_tuned_BPC_was_"
            "7p168_4p8_bits_below_vocab_entropy_NOT_collapse_classifier_must_"
            "use_tuned_bpc_best_against_vocab_entropy_rebuttal_at_landed_VET"
        ),
    ),
    (
        build_meta_M2_tight_rail_from_different_config,
        NOTES_PATH_RULING,
        "META_RULE_no_metrics_path",
        "META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift",
        "skunkworks_atomize_tier_ruling_3cells_2026-06-25",
        (
            "META_M2_tight_rail_from_different_config_can_mask_direction_"
            "correct_lift_observed_in_compose_heterogeneous_routing_v2_"
            "RESCUE_rail_fair_harness_FULL_config_cell_HALF_N_capacity_"
            "scaling_drift_plus_0p35_BPC_vs_tol_0p05_HARD_FAIL_PROVENANCE_"
            "fired_correctly_but_underlying_ARM_FREQ_ROUTED_K2_direction_"
            "correct_rule_widen_tolerance_or_match_config_exactly"
        ),
    ),
    (
        build_meta_M3_bundle_health_check_nan_spoke,
        NOTES_PATH_RULING,
        "META_RULE_no_metrics_path",
        "META_M3_bundle_health_check_NaN_spoke_can_win_cf_RPE_routing",
        "skunkworks_atomize_tier_ruling_3cells_2026-06-25",
        (
            "META_M3_bundle_health_check_NaN_spoke_can_win_cf_RPE_routing_"
            "observed_in_hub_spoke_E1_v2_diverse_algorithm_SoftHebb_NaN_recon_"
            "err_all_seeds_all_arms_cf_RPE_routing_picks_broken_spoke_0_"
            "bundle_collapses_to_unigram_equivalent_rule_require_per_spoke_"
            "health_check_gate_drop_NaN_zero_norm_diverged_recon_err_pre_routing"
        ),
    ),
]


def main() -> int:
    if "--apply" not in sys.argv:
        print("DRY: pass --apply to mutate Store + ledger.")
        print(f"Plan: {len(ATOM_PLAN)} atomizations (all MEASURED_MECHANISM / META; delta=0)")
        for i, item in enumerate(ATOM_PLAN, 1):
            builder, _, _, _, _, _ = item
            a = builder()
            print(f"  {i}. {a.corpus.value}::{a.id}  pq={a.metadata['provenance_quality']}  delta=+0")
        return 0

    ps = PartitionedStore(STORE_ROOT)
    atoms_pre = list(ps.all_atoms())
    n_atoms_pre = len(atoms_pre)
    cert_pre = sum(
        1 for a in atoms_pre
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    print(f"A5-PRE: n_atoms={n_atoms_pre} CERT N={cert_pre}")
    expected_delta_atoms = len(ATOM_PLAN)
    expected_delta_cert = 0
    print(f"Expected delta: atoms +{expected_delta_atoms}; CERT +{expected_delta_cert}")
    print()

    row_hashes = []
    for i, item in enumerate(ATOM_PLAN, 1):
        builder, notes_path, metrics_path, verdict_text, cell_commit, ledger_note = item
        atom = builder()
        atom_id_full = f"{atom.corpus.value}::{atom.id}"
        print(f"=== {i}/{len(ATOM_PLAN)}: {atom_id_full}  (pq={atom.metadata['provenance_quality']} delta=+0)")
        ok, h = safe_add_with_ledger(
            atom,
            source=ATOMIZED_BY,
            note=ledger_note,
            notes_path=notes_path,
            metrics_path=metrics_path,
            verdict_text=verdict_text,
            atom_id_full=atom_id_full,
            cell_commit=cell_commit,
        )
        if not ok:
            print(f"ABORT at item {i}")
            return 1
        row_hashes.append((atom.id, h))
        print()

    ps_post = PartitionedStore(STORE_ROOT)
    atoms_post = list(ps_post.all_atoms())
    n_atoms_post = len(atoms_post)
    cert_post = sum(
        1 for a in atoms_post
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    print("=" * 72)
    print(f"A5-POST: n_atoms={n_atoms_post} (delta +{n_atoms_post - n_atoms_pre}, expected +{expected_delta_atoms})")
    print(f"         CERT N={cert_post} (delta +{cert_post - cert_pre}, expected +{expected_delta_cert})")
    print("=" * 72)
    print("Row hashes:")
    for aid, h in row_hashes:
        print(f"  {h}  {aid}")

    if (n_atoms_post - n_atoms_pre) != expected_delta_atoms:
        print("WARNING: atom count drift")
        return 1
    if (cert_post - cert_pre) != expected_delta_cert:
        print("WARNING: CERT count drift")
        return 1
    print("A5 invariants PRESERVED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
