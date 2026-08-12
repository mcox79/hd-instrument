"""
A5-gated atomize: LANDED-VET (AUDIT-ONLY, XHIGH) of substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu.
CAPSTONE of the attention-routing arc: a SINGLE parameter-free gate that ARBITRATES recency + content.

CELL: experiments/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu.py (commit 4227e7e97)
METRICS: data/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu/metrics.json (run_mode=full,
  3 seeds 7/17/23, N=8192, K_GRID=6,10, headline K6 q0.25, verdict HARD_PASS[COMBINED]_ARBITRATION, 150/150)

INDEPENDENT OFF-DISK RECOMPUTE (.venv python off per_seed[], this session -- matched the cell exactly):
  @K6 q0.25 AGG: RAW=0.186 REC=0.673 CON=0.726 COMB=1.000 SCR=0.342
  COMB-REC=+0.327  COMB-CON=+0.274  scramble_sep=+0.658
  conflict win  = COMB 1.000 - REC 0.000 = +1.000   (per-seed COMB conflict 1.0/1.0/1.0 cv 0)
  cue_absent win= COMB 1.000 - CON 0.199 = +0.801   (per-seed COMB cue_absent 1.0/1.0/1.0 cv 0)
  PER-SEED COMBINED @K6q0.25 = 1.000/1.000/1.000 (cv 0); beats BOTH singles in EACH seed.
  REC per-seed 0.675/0.674/0.671 (cv 0.0023); CON per-seed 0.717/0.730/0.732 (cv 0.009);
  SCR per-seed 0.350/0.335/0.340 (cv 0.017); RAW per-seed 0.191/0.188/0.179 (in band).
  RESIDUAL-LEAK CHECK (the load-bearing one): CONTENT_ONLY cue_absent = 0.191/0.194/0.211 (mean ~0.199)
    = the cap 1/(K-1)=0.200 EXACTLY. NOT the buggy 0.702 the learned-W leak produced at smoke -> the
    parameter-free gate-select + cleanup readout does NOT absorb the corpus positional (recency) prior.
    RECENCY_ONLY conflict = 0.000 in ALL 3 seeds -> the recency gate genuinely FAILS where content should win.
    The exp_dev's smoke fix (learned Hebbian W -> parameter-free gate-select) HELD at FULL. No residual leak.
  ENVELOPE (invariant COMB - max(single) per q @K6): q1.0/0.5/0.25 = +0.274, q0.12 = -0.039, q0.06 = -0.053.
    Crosses zero between q=0.25 (+0.274) and q=0.12 (-0.039), bracketing the analytic boundary q*=0.15
    (=GATE_TAU*RECENCY_GAP_TARGET=0.05*3.0). Below q* the content logit q/tau < recency gap -> COMBINED
    correctly falls back to recency (holds ~0.67-0.69, NEVER catastrophic). Honest mechanism-with-range.
  HARNESS: cardinality 150/150; arm_digests 5 distinct (ARMS-MUST-DIFFER); RAW in (1.3*chance,0.50) all q.

ADJUDICATION (Director's 5 asks):
  1. NO RESIDUAL POSITIONAL-PRIOR LEAK -- CONFIRMED off-disk. CONTENT_ONLY cue_absent sits at the 0.20 cap
     (picks 1 of 5 non-first slots at random on flat noise), not leaking recency; RECENCY_ONLY conflict=0.000.
     Readout verified parameter-free off CODE (gate_readout = gate-weighted superposition of raw slot codes
     + codebook cleanup; NO learned W, NO train pass; learn_recency_gate uses ONLY position stats and feeds
     ONLY the RECENCY/COMBINED gates, by design). The fix held.
  2. ARBITRATION GENUINE PER-SEED -- YES. COMBINED beats BOTH singles in each of 3 seeds (cv 0); conflict-win
     and cue_absent-win are +1.000 / ~+0.80 in EVERY seed, not one seed carrying it.
  3. TELEMETRY-SENSITIVE (not pinned) -- YES. The scramble control (same combined formula, content relevance
     DERANGED) drops COMBINED 1.000 -> 0.342 (sep +0.658) -> content ORDERING is load-bearing. The T1/T2
     self-tests (relabel targets -> collapse to chance; relocate flag -> recovered token follows the new slot)
     run at module import on EVERY invocation incl. the FULL dispatch and PASSED (main() would not have
     written HARD_PASS metrics otherwise). A metric analytically pinned to the config would pass both
     regardless; this one MOVES -> genuine substrate readout, not a tautological discriminator.
  4. HONEST ENVELOPE -- the COMB-max(single) zero-crossing between q0.25 and q0.12 brackets the analytic
     fall-back boundary q*=0.15. Framed as a mechanism-with-operating-range (win for q>=q*~0.15, graded
     recency-fallback below), NOT a point claim; the invariant (never catastrophically worse than best single)
     holds across the whole grid.
  5. TIER = CHAIN_GRADE. CG bar met on every axis: PARAMETER-FREE (no fit to inflate); 3-seed robust (cv 0);
     telemetry-sensitive discriminator with a paired scramble control that fires; GENUINELY ARBITRATES --
     beats BOTH singles on the mix AND rescues EACH single's failure sub-regime (conflict +1.000 vs recency,
     cue_absent +0.801 vs content). This is the full glass-box attention-routing capability certified.
     Composes v5 recency-MM + v6 clean-content-MM + v7 noisy-content-CG into the arbitration capstone.

HONEST SCOPE / non-inflation notes (locked):
  - COMBINED=1.000 exactly is the CLEAN-ENCODING/high-SNR regime (N=8192, near-orthogonal codes, cue_snr=22.6
    at headline q): once the gate SELECTS the right slot the parameter-free cleanup recovers the token
    deterministically. The certified difficulty is the ARBITRATION (which slot), NOT a hard readout -- the
    scramble (0.342) and relabel (chance) controls prove the 1.000 is genuine selection, not a pinned constant.
  - The MIXED-corpus win magnitude (COMB-CON +0.274) is a direct function of the 1/3-1/3-1/3 type mix; the
    mix-INDEPENDENT proofs are the sub-regime wins (conflict +1.000, cue_absent +0.801). Cite those as the
    load-bearing arbitration evidence, not the mix-weighted mixed delta.
  - Certified operating range: reliable cue q >= q*~0.15. Below the boundary arbitration degrades to
    recency-fallback (proven envelope, NOT open failure).

CROSS-ARC OVERLAP CHECK (substrate_query, mandatory): top cosine 0.419 (wordnet 'contention'), 0.385
  (coordination/contention note), 0.380 (wordnet/framenet 'attention'), 0.372 ('combination') -- ALL surface
  char-trigram lexical hits (contention/attention/coordination/combination), NONE touches the arbitration
  MECHANISM at cosine>0.30. Consistent with SUBSTRATE-KNOWS-NOTHING. The genuine predecessors are v5/v6/v7
  (explicit composition, not rediscovery). No prior arc cell duplicates this synthesis.

PARENTS/COMPOSES (verified present in Store):
  v5 contextgate_depth_v5 (MEASURED_MECHANISM, recency selective-admission half)
  v6 contentgate_flagdep_v6 (MEASURED_MECHANISM, clean-cue content half)
  v7 contentgate_noisycue_v7 (CHAIN_GRADE, noisy-cue content-inference half)
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_08_combinedgate_recency_content_v8_ARBITRATION_CHAIN_GRADE"
CELL_COMMIT = "4227e7e97"
TS = time.time()
TS_ISO = "2026-07-08T09:05:00Z"
SESSION = "2026-07-08_combinedgate_recency_content_v8_landed_vet_ARBITRATION_CAPSTONE_CG"

V5 = ("math::MEASURED_MECHANISM_contextgate_depth_v5_n8192_gpu_CONTEXT_GATE_selective_admission_gating_"
      "FLATTENS_noise_compounding_FIRST_POSITIVE_on_Stage4_attention_routing_gap_dGATE_plus0p0028_vs_"
      "dRAW_plus0p6486_99p56pct_reduction_3of3_seeds_perseed_dGATE_plus0p0002_neg0p0050_plus0p0134_all_"
      "flat_gap_gate_Kmax_plus0p646_ge_0p30_SCRAMBLE_is_PERMUTATION_ONLY_of_gate_weights_sorted_g_eq_"
      "sorted_gs_sum_1p0_g_perm_eq_gs_moves_dominant_0p78to0p89_weight_OFF_most_recent_slot_blows_up_"
      "dGSCR_plus1p730_worse_than_RAW_separation_plus1p727_ge_0p15_by_11x_benefit_is_SELECTION_not_"
      "renormalization_gate_concentrates_argmax_K_minus_1_gKm1_0p69to0p89_gt_0p5_healthy_GATE_at_Kmax_"
      "2p710_eq_RAW_at_K1_2p707_fully_DISCARDS_noise_slots_reduces_to_single_token_MISSES_strict_prereg_"
      "dGATE_le_0_by_plus0p003_soft_gate_leakage_as_flagged_NOT_clean_HARD_PASS_whole_cell_MIDDLE_BAND_"
      "correct_RECENCY_gate_1st_order_corpus_optimal_selection_SIMPLE_content_dependent_higher_order_"
      "UNTESTED_regime_fair_RAW_K1_2p707_between_bigram_oracle_1p982_unigram_floor_5p745_learns_then_"
      "degrades_monotone_3of3_K1_anchor_identity_cardinality_84of84_commit_4692cd9cc_2026-07-08")
V6 = ("math::MEASURED_MECHANISM_contentgate_flagdep_v6_n8192_gpu_CONTENT_GATE_content_addressed_query_key_"
      "admission_EXECUTES_correctly_over_K_temporal_slots_WITH_a_CLEAN_EXPLICIT_cue_CONTENT_1p000_3of3_seeds_"
      "all_K_cv0_RECENCY_0p272_near_analytic_cap_0p200_RAW_0p265_SCRAMBLE_0p069_at_chance_0p0625_lift_vs_"
      "recency_plus0p728_scramble_sep_plus0p931_but_1p000_is_BY_CONSTRUCTION_EASY_FLAG_reserved_unique_"
      "codebook_vector_true_slot_predecessor_is_EXACTLY_FLAG_cos_1p0_exact_tau_0p05_gate_perfect_measures_"
      "MECHANISM_EXECUTION_not_learned_noisy_relevance_scramble_derange_to_chance_rescues_from_pure_tautology_"
      "proves_correct_alignment_required_not_renormalization_K4_RECENCY_0p511_BREACHES_0p50_guard_clean_"
      "discrimination_K6_and_K8_only_composes_v5_recency_MM_two_halves_selective_admission_learned_noisy_"
      "relevance_no_explicit_flag_UNTESTED_commit_9d298c81_2026-07-08")
V7 = ("math::CHAIN_GRADE_contentgate_noisycue_v7_n8192_gpu_CONTENT_GATE_content_addressed_query_key_admission_"
      "INFERS_relevance_from_a_GRADED_NOISY_cue_and_beats_1_over_Km1_cap_down_to_the_DETECTABILITY_FLOOR_"
      "promotes_v6_clean_cue_MM_to_CG_cos_true_TRACKS_q_perseed_0p0797_at_q0p08_0p0201_at_q0p02_0p0103_at_"
      "q0p01_genuine_noise_injection_NOT_handed_metric_is_SENSITIVE_not_analytically_pinned_CON_1p000_to_"
      "0p515_as_q_falls_prereg_realistic_q0p08_cue_snr7p24_is_SNR_INFLATED_plus6sigma_over_distractor_max_"
      "trivially_clear_BUT_promotion_HOLDS_at_honestly_hard_q0p02_cue_snr1p81_plus0p65sigma_cos_true0p020_"
      "CON_0p729_3of3_cv0p064_lift_vs_recency_plus0p454_crushes_cap_0p200_scramble_sep_q1p0_plus0p932_BREAK_"
      "at_q0p01_cue_snr0p91_minus0p26sigma_lift_plus0p237_at_detectability_floor_RECENCY_0p280_RAW_0p254_flat_"
      "SCRAMBLE_at_chance_composes_v6_content_clean_MM_v5_recency_MM_answers_v6_own_revival_criterion_216of216_"
      "units_commit_aa0ebb9bb_2026-07-08")

atom = {
    "id": (
        "math::CHAIN_GRADE_combinedgate_recency_content_v8_n8192_gpu_COMBINED_GATE_parameter_free_biased_"
        "competition_ARBITRATES_recency_prior_and_content_cue_bias_softmax_content_rel_over_tau_plus_recency_"
        "bias_CAPSTONE_of_attention_routing_arc_beats_BOTH_singles_on_mixed_COMB_REC_plus0p327_COMB_CON_"
        "plus0p274_AND_rescues_EACH_singles_failure_subregime_conflict_content_wins_COMB_1p000_vs_REC_0p000_"
        "win_plus1p000_cue_absent_falls_back_to_recency_COMB_1p000_vs_CON_0p199_win_plus0p801_3of3_seeds_"
        "COMBINED_1p000_cv0_conflict_and_cue_absent_win_in_EVERY_seed_content_ordering_load_bearing_scramble_"
        "sep_plus0p658_derange_drops_1p000_to_0p342_telemetry_T1_relocate_flag_follows_T2_relabel_collapses_"
        "to_chance_pass_at_import_NO_RESIDUAL_POSITIONAL_PRIOR_LEAK_CONTENT_ONLY_cue_absent_0p199_at_cap_1_"
        "over_Km1_NOT_buggy_0p702_learned_W_leak_RECENCY_ONLY_conflict_0p000_readout_PARAMETER_FREE_gate_"
        "select_superposition_plus_codebook_cleanup_no_learned_W_smoke_fix_HELD_at_FULL_envelope_invariant_"
        "COMB_minus_max_single_crosses_zero_between_q0p25_plus0p274_and_q0p12_neg0p039_brackets_analytic_"
        "boundary_qstar_0p15_eq_GATE_TAU_0p05_times_RECENCY_GAP_3p0_below_qstar_graded_recency_fallback_never_"
        "catastrophic_holds_0p67to0p69_operating_range_q_ge_0p15_RAW_0p186_in_band_composes_v5_recency_MM_v6_"
        "clean_content_MM_v7_noisy_content_CG_full_glass_box_attention_routing_certified_cardinality_150of150_"
        "commit_4227e7e97_2026-07-08"
    ),
    "name": (
        "COMBINED GATE parameter-free biased-competition ARBITRATES a recency prior and a content-cue bias "
        "(softmax(content_rel/tau + recency_bias)) -- the attention-routing CAPSTONE. Beats BOTH single gates "
        "on the mixed corpus (COMB-REC +0.327, COMB-CON +0.274) AND rescues EACH single's failure sub-regime "
        "(conflict: content wins +1.000 vs recency; cue_absent: recency-fallback +0.801 vs content), 3/3 seeds "
        "cv0, content-ordering load-bearing (scramble_sep +0.658). NO residual positional-prior leak "
        "(CONTENT_ONLY cue_absent at the 0.20 cap, not the buggy 0.702; readout parameter-free); the smoke fix "
        "HELD at FULL. Honest operating range q >= q*~0.15 (graded recency-fallback below). CHAIN_GRADE."
    ),
    "corpus": "math",
    "tier": "CHAIN_GRADE",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "cg_parameter_free_biased_competition_gate_arbitrates_recency_prior_and_content_cue_bias_beats_both_"
        "singles_on_mix_and_rescues_each_failure_subregime_3seed_robust_telemetry_sensitive_attention_routing_"
        "capstone_operating_range_q_ge_qstar_0p15"
    ),
    "cert_class": (
        "single_softmax_gate_over_sum_of_a_fixed_topdown_recency_bias_in_logit_units_and_a_per_instance_scaled_"
        "content_query_key_relevance_arbitrates_by_normalization_no_hand_set_switch_no_learned_readout_weight_"
        "parameter_free_gate_select_plus_codebook_cleanup_readout_rescues_recency_on_conflict_and_content_on_"
        "cue_absent_operating_range_bounded_by_analytic_boundary_qstar_eq_gate_tau_times_recency_gap"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY, XHIGH) of exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu "
        "(commit 4227e7e97; FULL, 3 seeds 7/17/23, N=8192, K_GRID=6,10, headline K6 q0.25, 150/150 units, "
        "verdict HARD_PASS[COMBINED]_ARBITRATION). CLAIM VERIFIED off-disk (independent .venv recompute off "
        "per_seed[], matched the cell exactly). The COMBINED gate = a SINGLE softmax over "
        "content_rel/GATE_TAU + recency_bias (GATE_TAU=0.05, recency_bias a fixed top-down prior normalized to "
        "a RECENCY_GAP_TARGET=3.0 logit gap; both FIXED a priori, nothing tuned per-q/per-instance). It "
        "ARBITRATES: @K6 q0.25 (cue_snr 22.6) AGG COMB=1.000 vs REC=0.673 CON=0.726 -> beats BOTH singles on "
        "the mixed corpus (COMB-REC +0.327, COMB-CON +0.274). It rescues EACH single on the sub-regime where "
        "that one fails: on CONFLICT content wins (COMB 1.000 vs REC 0.000, win +1.000); on CUE_ABSENT it falls "
        "back to recency (COMB 1.000 vs CON 0.199, win +0.801). PER-SEED (3/3): COMBINED=1.000/1.000/1.000 "
        "(cv 0), conflict-win and cue_absent-win in EVERY seed -- no single seed carries it. REC per-seed "
        "0.675/0.674/0.671 (cv 0.0023), CON 0.717/0.730/0.732 (cv 0.009), SCR 0.350/0.335/0.340 (cv 0.017), "
        "RAW ~0.186 (in (1.3*chance,0.50)). NO RESIDUAL POSITIONAL-PRIOR LEAK (the load-bearing check): "
        "CONTENT_ONLY on cue_absent = 0.191/0.194/0.211 (mean ~0.199) = the content-blind cap 1/(K-1)=0.200 "
        "EXACTLY (flat-noise softmax picks 1 of the 5 non-first slots at random), NOT the 0.702 the buggy "
        "learned-Hebbian-W readout produced at smoke; RECENCY_ONLY conflict = 0.000 in ALL 3 seeds (genuinely "
        "fails where content should win). Readout verified PARAMETER-FREE off CODE: gate_readout = gate-weighted "
        "superposition of the raw slot codes + codebook cleanup (cos vs codebook, argmax over the VALUE "
        "sub-vocab), NO learned W and NO train pass; learn_recency_gate uses ONLY per-position statistics and "
        "feeds ONLY the RECENCY/COMBINED gates (by design) -- so the readout cannot absorb the corpus slot-K-1 "
        "prior. The exp_dev's smoke fix (learned Hebbian W -> parameter-free gate-select) HELD at FULL. "
        "CONTENT-ORDERING LOAD-BEARING: COMBINED_SCRAMBLED (same combined formula, content relevance DERANGED "
        "by a fixed per-seed permutation) drops COMBINED 1.000 -> 0.342 (scramble_sep +0.658) -- a sharp cue on "
        "the WRONG slot breaks it; recency still rescues cue_absent. TELEMETRY-SENSITIVE (not analytically "
        "pinned): the self-test T1 (relocate the flag on conflict instances -> the COMBINED-recovered token "
        "FOLLOWS the new slot) and T2 (relabel targets to random tokens -> COMBINED collapses toward chance) "
        "run at module import on EVERY invocation incl. the FULL dispatch and passed (main() would not have "
        "written HARD_PASS otherwise). ENVELOPE (honest, reported regardless of tier): the invariant "
        "COMB-max(single) per q @K6 = +0.274 (q1.0/0.5/0.25), -0.039 (q0.12), -0.053 (q0.06) -- crosses zero "
        "between q0.25 and q0.12, bracketing the ANALYTIC fall-back boundary q*=GATE_TAU*RECENCY_GAP_TARGET="
        "0.15. Below q* the content logit q/tau < recency gap so COMBINED correctly falls back to recency "
        "(holds ~0.67-0.69, NEVER catastrophic; the invariant that it is never much worse than the best single "
        "holds across the whole grid). TIER = CHAIN_GRADE: the CG bar is met on every axis -- PARAMETER-FREE "
        "(no fit to inflate), 3-seed robust (cv 0), telemetry-sensitive discriminator with a paired scramble "
        "control that fires, and it GENUINELY ARBITRATES (beats both singles on the mix AND rescues each "
        "single's failure regime). The full glass-box attention-routing capability certified. HONEST SCOPE "
        "(locked): COMBINED=1.000 exactly is the clean-encoding/high-SNR regime -- once the gate SELECTS the "
        "right slot the parameter-free cleanup recovers the token deterministically; the certified difficulty "
        "is the ARBITRATION (which slot), not a hard readout (scramble 0.342 + relabel-to-chance prove it is "
        "genuine selection, not a pinned constant). The MIXED win magnitude (+0.274) is mix-weighted (1/3 each "
        "type); cite the mix-INDEPENDENT sub-regime wins (conflict +1.000, cue_absent +0.801) as the "
        "load-bearing arbitration evidence. Operating range: reliable cue q >= q*~0.15; below it arbitration "
        "degrades to recency-fallback (proven envelope, not open failure). HARNESS: cardinality 150/150; "
        "arm_digests 5 distinct (ARMS-MUST-DIFFER); GATE_TAU/RECENCY_GAP_TARGET fixed a priori. CROSS-ARC "
        "OVERLAP: top cosine 0.419 (wordnet 'contention'), all surface lexical, NONE on the arbitration "
        "mechanism at >0.30 -> genuine novel synthesis of v5/v6/v7, not a rediscovery."
    ),
    "provenance": {
        "cell": "experiments/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu.py",
        "commit": CELL_COMMIT,
        "metrics_path": "data/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu/metrics.json",
        "seeds": [7, 17, 23],
        "run_mode": "full",
        "whole_cell_verdict": "HARD_PASS",
        "audit_tier": "CHAIN_GRADE",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent .venv recompute off per_seed[] (150/150 units). @K6q0.25 AGG COMB=1.000 REC=0.673 "
            "CON=0.726 RAW=0.186 SCR=0.342; COMB-REC +0.327, COMB-CON +0.274, scramble_sep +0.658; conflict "
            "win +1.000 (COMB 1.0/1.0/1.0 vs REC 0.0/0.0/0.0), cue_absent win +0.801 (COMB 1.0/1.0/1.0 vs CON "
            "0.191/0.194/0.211). Per-seed COMBINED=1.000 cv0; REC cv0.0023, CON cv0.009, SCR cv0.017. LEAK "
            "CHECK: CONTENT_ONLY cue_absent ~0.199 = cap 1/(K-1)=0.20 (NOT 0.702); RECENCY_ONLY conflict "
            "0.000 all seeds. Readout parameter-free off code (gate-weighted superposition + cleanup, no "
            "learned W). Envelope invariant @K6 {1.0/0.5/0.25:+0.274, 0.12:-0.039, 0.06:-0.053}; zero-crossing "
            "brackets analytic q*=0.15. cardinality 150/150; 5 distinct arm_digests."
        ),
    },
    "verified_numbers": {
        "headline_K": 6, "headline_q": 0.25, "N": 8192, "cue_snr_at_headline": 22.627,
        "chance_1_over_Vsub": 0.0625, "content_blind_cap_1_over_Km1_K6": 0.2,
        "gate_tau": 0.05, "recency_gap_target": 3.0, "arb_boundary_qstar": 0.15,
        "COMB_K6q025_agg": 1.0, "REC_K6q025_agg": 0.6733, "CON_K6q025_agg": 0.7263,
        "RAW_K6q025_agg": 0.1860, "SCR_K6q025_agg": 0.3415,
        "COMB_minus_REC": 0.3267, "COMB_minus_CON": 0.2737, "scramble_sep": 0.6585,
        "conflict_win_COMB_minus_REC": 1.0000, "cue_absent_win_COMB_minus_CON": 0.8015,
        "COMBINED_per_seed_K6q025": [1.0, 1.0, 1.0], "COMBINED_cv": 0.0,
        "RECENCY_per_seed_K6q025": [0.675, 0.6738, 0.6713], "RECENCY_cv": 0.0023,
        "CONTENT_per_seed_K6q025": [0.7171, 0.7296, 0.7321], "CONTENT_cv": 0.0090,
        "SCRAMBLED_per_seed_K6q025": [0.3496, 0.3354, 0.3396], "SCRAMBLED_cv": 0.0174,
        "COMBINED_conflict_per_seed": [1.0, 1.0, 1.0], "RECENCY_conflict_per_seed": [0.0, 0.0, 0.0],
        "COMBINED_cue_absent_per_seed": [1.0, 1.0, 1.0],
        "CONTENT_cue_absent_per_seed_AT_CAP_no_leak": [0.1907, 0.1938, 0.2110],
        "LEAK_buggy_smoke_learnedW_value_for_contrast": 0.702,
        "envelope_invariant_COMB_minus_maxsingle_K6": {"1.0": 0.2737, "0.5": 0.2737, "0.25": 0.2737,
                                                        "0.12": -0.0385, "0.06": -0.0529},
        "envelope_zero_crossing_between_q": [0.25, 0.12], "analytic_qstar": 0.15,
        "readout_parameter_free": True, "learned_readout_weight": False,
        "cardinality_units": 150, "cardinality_expected": 150, "arm_digests_distinct": True,
    },
    "can_fail_discriminator_verdict": (
        "FIRES against REAL can-fail alternatives on multiple axes. (1) COMBINED_SCRAMBLED (same combined "
        "formula, content relevance DERANGED) could have replicated the gain if the benefit were any peaked "
        "admission / renormalization; it does the OPPOSITE (1.000 -> 0.342, sep +0.658) -> the content "
        "ORDERING is load-bearing, the benefit is SELECTION. (2) Telemetry T1/T2 (relocate flag -> recovered "
        "token follows; relabel targets -> collapse to chance) fire -> the metric is a genuine substrate "
        "readout, not analytically pinned. (3) VALID-ONLY-IF held: each single gate genuinely FAILS on its "
        "intended sub-regime (RECENCY conflict 0.000, CONTENT cue_absent 0.199) so the corpus creates real "
        "arbitration pressure; RAW capped (~0.186) -> not saturation-vacuous."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "HARD_PASS[COMBINED]_ARBITRATION (cell verdict) UPHELD at CHAIN_GRADE off independent recompute -- every "
        "headline number reproduces exactly. This is a genuine CG, not an over-claim; symmetric anti-negativity "
        "-- do NOT deflate a parameter-free 3-seed arbitration that rescues both failure regimes.",
        "RESIDUAL-LEAK CALL (Director's load-bearing ask): NO residual positional-prior leak. CONTENT_ONLY on "
        "cue_absent sits at the 0.20 cap in all 3 seeds (0.191/0.194/0.211), NOT the 0.702 the buggy learned-W "
        "readout leaked at smoke; RECENCY_ONLY conflict=0.000. The parameter-free gate-select + cleanup readout "
        "(verified off code: no learned W, no train pass) removes the confound. The exp_dev smoke fix HELD at FULL.",
        "NON-INFLATION on the perfect 1.000: COMBINED=1.000 across all types is the CLEAN-ENCODING regime "
        "(N=8192, cue_snr 22.6) where selection is deterministic once the right slot is chosen. The certified "
        "capability is the ARBITRATION (which-slot), NOT a hard readout. The scramble (0.342) and relabel "
        "(chance) controls prove it is genuine selection, not a pinned/tautological constant -- so 1.000 is "
        "earned, not suspect. But frame the finding as 'arbitrates cleanly in-regime', not 'perfect LM'.",
        "ANCHOR the arbitration claim on the mix-INDEPENDENT sub-regime wins (conflict +1.000 vs recency, "
        "cue_absent +0.801 vs content), NOT the mixed-corpus deltas (+0.327/+0.274) whose magnitude is a "
        "direct function of the 1/3-1/3-1/3 type mix. The sub-regime rescues are the load-bearing proof.",
        "OPERATING RANGE, not a point claim: the win holds for reliable cue q >= q*~0.15; the envelope invariant "
        "crosses zero between q0.25 and q0.12, bracketing the analytic boundary q*=GATE_TAU*RECENCY_GAP=0.15. "
        "Below q* COMBINED falls back to recency (~0.67-0.69), NEVER catastrophic -- a mechanism-with-range, the "
        "honest envelope edge (headline q0.25 is solidly in the win regime).",
        "CAPSTONE scope: this certifies glass-box attention-routing ARBITRATION of a recency prior vs a "
        "content-cue bias via biased-competition normalization -- composing v5 recency-MM + v6 clean-content-MM "
        "+ v7 noisy-content-CG. It does NOT claim multi-cue (>2 signals) arbitration or value-based (PBWM) "
        "gating; those remain untested extensions.",
    ],
    "revival_or_extension_criterion": (
        "CG scope LOCKED to: parameter-free biased-competition arbitration of a SINGLE recency prior against a "
        "SINGLE content-cue bias, on a corpus that creates both failure sub-regimes, for reliable cue q>=q*~0.15 "
        "at K in {6,10}. EXTENSION paths (each a new cell, not covered here): (1) MULTI-CUE arbitration -- 3+ "
        "competing top-down biases through the shared normalization pool (does the graded competition still pick "
        "the right one). (2) VALUE-BASED gating (PBWM) -- arbitrate by learned value/reward rather than a fixed "
        "recency prior. (3) LEARNED (not fixed) recency_bias strength that adapts per-context. (4) below-boundary "
        "recovery -- a cell that pushes the win below q*~0.15 (e.g. an adaptive tau) would extend the operating "
        "range. DEMOTION trigger: if a re-run shows the sub-regime wins depend on the readout absorbing the "
        "positional prior (i.e. a learned W creeps back), or the scramble control stops firing."
    ),
    "composes": [V5, V6, V7],
    "compose_note": (
        "The ARBITRATION capstone of the attention-routing arc. Composes the two proven halves of selective "
        "admission: v5 contextgate_depth (recency selective-admission, MM) + v6 contentgate_flagdep (clean-cue "
        "content admission, MM) promoted by v7 contentgate_noisycue (noisy-cue content inference, CG). v8 is the "
        "NOVEL synthesis: a single gate that ARBITRATES both signals when both are present -- content wins when a "
        "reliable cue exists, recency wins when it does not -- via softmax over their SUM (biased-competition "
        "normalization), with NO hand-set switch. None of v5/v6/v7 is superseded; v8 extends them into the "
        "combined-gate capability. Brain-grounding: Desimone & Duncan 1995 / Reynolds & Heeger 2009 normalization "
        "(shared pool arbitrates multiple top-down biases); PBWM value-gating (Frank/O'Reilly) is the untested "
        "value-based extension."
    ),
    "cross_arc_overlap_check": (
        "substrate_query 'combined recency content gate arbitration biased competition attention routing' -> top "
        "cosine 0.419 (wordnet 'contention'), 0.385 (coordination/contention note), 0.380 (wordnet/framenet "
        "'attention'), 0.372 ('combination') -- ALL surface char-trigram lexical hits, NONE touches the "
        "arbitration MECHANISM at cosine>0.30. Consistent with SUBSTRATE-KNOWS-NOTHING. The genuine predecessors "
        "are v5/v6/v7 (explicit composition). No prior arc cell duplicates this synthesis -> genuine novel "
        "capstone, not a rediscovery (the July-1 INT8-rediscovery pattern does NOT apply)."
    ),
    "anchor": "substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu",
    "cell_commit": CELL_COMMIT,
    "seeds": [7, 17, 23],
    "run_mode": "full",
    "cardinality_ok": True,
    "arms_differ_verified": True,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "needs_orchestrator_store_sync": True,
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "parameter-free biased-competition gate arbitrates a recency prior and a content-cue bias (softmax(content_rel/tau + recency_bias)) -- attention-routing capstone, CHAIN_GRADE",
        "beats BOTH single gates on the mix (COMB-REC +0.327, COMB-CON +0.274) AND rescues EACH failure sub-regime (conflict +1.000 vs recency, cue_absent +0.801 vs content), 3/3 seeds cv0",
        "NO residual positional-prior leak: CONTENT_ONLY cue_absent at the 0.20 cap (not the buggy 0.702 learned-W leak), RECENCY_ONLY conflict 0.000; readout parameter-free gate-select + cleanup; smoke fix HELD at FULL",
        "content-ordering load-bearing (scramble 1.000->0.342, sep +0.658); telemetry T1/T2 fire (relocate-follows, relabel-to-chance) -> genuine selection, not a pinned discriminator",
        "operating range q >= q*~0.15 (=GATE_TAU*RECENCY_GAP=0.05*3.0); envelope invariant crosses zero between q0.25 and q0.12, graded recency-fallback below (never catastrophic)",
        "composes v5 recency MM + v6 clean-content MM + v7 noisy-content CG into the combined-gate arbitration capability -- glass-box attention-routing certified",
    ],
    "added_atom_id": None,
}
atom["added_atom_id"] = atom["id"]

ledger = {
    "ts": TS, "ts_iso": TS_ISO, "op": "add", "atom_id": atom["id"], "corpus": "math",
    "tier": "CHAIN_GRADE",
    "disposition": "chain_grade_new_capability_arbitration_capstone",
    "cert_status": (
        "cg_parameter_free_biased_competition_gate_arbitrates_recency_prior_and_content_cue_bias_beats_both_"
        "singles_and_rescues_each_failure_subregime_3seed_robust_attention_routing_capstone"
    ),
    "cert_class": (
        "single_softmax_gate_over_sum_of_fixed_topdown_recency_bias_and_per_instance_content_query_key_"
        "relevance_arbitrates_by_normalization_no_switch_parameter_free_readout_operating_range_q_ge_qstar"
    ),
    "cert_increment_delta": {"CG": 1, "MM": 0, "HF": 0},
    "cert_delta": {"CG": 1, "MM": 0, "HF": 0},
    "cert_delta_note": (
        "CG +1: NEW capability (arbitration capstone), not a promotion of an existing atom. A parameter-free "
        "biased-competition gate ARBITRATES a recency prior and a content-cue bias (softmax(content_rel/tau + "
        "recency_bias)): @K6 q0.25 beats BOTH singles on the mixed corpus (COMB-REC +0.327, COMB-CON +0.274) "
        "AND rescues EACH single's failure sub-regime (conflict: content wins, +1.000 vs recency; cue_absent: "
        "recency-fallback, +0.801 vs content), 3/3 seeds COMBINED=1.000 cv0, content-ordering load-bearing "
        "(scramble_sep +0.658). NO residual positional-prior leak (CONTENT_ONLY cue_absent at 0.20 cap not the "
        "buggy 0.702; readout parameter-free; smoke fix HELD at FULL). Telemetry T1/T2 fire (not pinned). "
        "Honest operating range q>=q*~0.15 (analytic boundary GATE_TAU*RECENCY_GAP=0.15; graded recency-fallback "
        "below, never catastrophic). Composes v5 recency-MM + v6 clean-content-MM + v7 noisy-content-CG (none "
        "superseded). Whole-cell HARD_PASS verdict UPHELD at CG. Needs orchestrator Store-sync (atoms.jsonl "
        "append; skunkworks atoms do not auto-persist)."
    ),
    "verified_off_data": True,
    "anchor": "substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "composes": [V5, V6, V7],
    "needs_orchestrator_store_sync": True,
    "raw_metrics_paths": ["data/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu/metrics.json"],
}


def append_jsonl_a5(path: Path, new_row: dict, label: str) -> int:
    pre_lines = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")
    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")
    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id")
    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            time.sleep(0.1 * (2 ** _attempt))
    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1
    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"]
    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")
    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={TS:.3f}")
    append_jsonl_a5(MATH_ATOMS, atom, "math/atoms (COMBINED_GATE ARBITRATION CHAIN_GRADE)")
    append_jsonl_a5(CERT_LEDGER, ledger, "cert_ledger (CG +1)")
    print(f"[A5] DONE OK -> COMBINED_GATE arbitration CHAIN_GRADE (CG +1); whole-cell HARD_PASS upheld")


if __name__ == "__main__":
    main()
