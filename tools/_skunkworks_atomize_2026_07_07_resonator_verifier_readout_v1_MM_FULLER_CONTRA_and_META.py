"""
A5-gated atomize: LANDED-VET (AUDIT-ONLY) of exp_resonator_verifier_readout_v1, commit 09446de2d.

CELL: experiments/exp_resonator_verifier_readout_v1.py
ANCHOR: resonator_verifier_readout_v1
METRICS: data/exp_resonator_verifier_readout_v1/metrics.json (run_mode=full, seeds [3,7,13], elapsed 1303.5s)
PREREG: preregs/2026-07-07_resonator_verifier_readout_v1.md
PARENT: math::MEASURED_MECHANISM_resonator_K4_external_reset_PARTIAL_CONTRA_..._2026-07-07 (plurality MIDDLE 0.464)

OFF-DISK INDEPENDENT RECOMPUTE (this session, .venv python):
  K4 T0=0.5 per-seed verifier = [0.825, 0.825, 0.7667] -> mean 0.8056
  K4 T0=0.5 per-seed plurality= [0.4667, 0.5083, 0.3833] -> mean 0.4528
  K4 T0=0.5 per-seed oracle   = [0.825, 0.825, 0.7667] -> mean 0.8056 == verifier (harvest==oracle EXACT)
  lift = 0.3528; cross-seed cv verifier (pop) 0.0341 / (sample) 0.0418 -> tight
  baseline K4 = [0.1583,0.0917,0.15] mean 0.1333; baseline K3 = [0.7083,0.7833,0.7333] mean 0.7417 in [0.40,0.95]
  ACROSS ALL 30 verifier arms: harvest==oracle EXACT (0 mismatches), 0 invariant violations, 0 verifier>oracle
  arms-differ: verifier-winner-hash != plurality-winner-hash on ALL 30 arm-instances
  T0 sweep K4: 0.00->0.2472, 0.10->0.7472, 0.20->0.7889, 0.35->0.8000, 0.50->0.8056 (monotone; lift 0.10..0.36)
  Every recorded detail-block number reproduced to 1e-9.

MECHANISM AUDIT (no oracle leak):
  _recon_score(books,s,cand,K) (line 95) scores candidate reconstruction against input probe s ONLY;
  never compares cand==true. Probe s rebuilt at line 300-303 from books[k][true[k]] = the input being
  factored (the product of true factors IS the probe by definition of the factorization task; this is
  the legitimate decode-time input, NOT a label peek). ver_winner = max(uniq, recon_score) drawn from
  uniq = set(candidate tuples). Therefore ver_hit (ver_winner==true) STRUCTURALLY implies truth_present,
  so verifier <= oracle_any is guaranteed BY CONSTRUCTION -- the invariant cannot be violated. The
  NON-trivial empirical finding is harvest == oracle EXACTLY at every arm: whenever truth is among the
  ~9 distinct candidates (mean_within_trial_distinct 9.19 at K4), the phasor margin (true score 1.0 vs
  wrong ~1/sqrt(N) ~0.0156 at N=4096) makes the verifier pick truth with ZERO failures across 3 seeds.

TIER: MEASURED_MECHANISM (proven-bound), NOT chain-grade. Reasons:
  (1) Headline 0.806 IS the oracle_any ceiling -- the verifier adds NO new reach; it is a read-out that
      realizes an already-MEASURED ceiling (parent atom measured oracle_any=0.80). Definitionally verifier
      cannot exceed oracle.
  (2) harvest==oracle is theory-predicted and by-construction-adjacent: the phasor inner-product margin
      (1.0 vs 0.0156) makes truth-when-present recovery deterministic at N=4096. Clean confirmation of a
      mechanism, not a surprising hard-won capability.
  (3) The claim is honestly WEAKER than "verifier rescues K4": the read-out CLOSES the aggregation gap
      (0.453->0.806, harvesting the full oracle ceiling) but the ceiling itself (0.806 < 1.0) is a
      SEPARATE, still-open reachability bound (~19% of trials the answer is NEVER reached in R=10). That
      residual is restart-budget / basin-reachability, NOT aggregation.
  --> proven boundary + mechanism decomposition = MEASURED_MECHANISM. cert_delta MM +1 (realizes the
      parent atom's registered promotion path: "reachable via verifier over candidate tuples").

STRATEGIC VERDICT (fuller contra WITH honest residual):
  External reset (Glauber finite-T dither + R=10 restart) reaches the K4 answer in ~80.6% of trials
  (oracle_any). The verifier read-out now HARVESTS that full 80.6% (vs plurality's 45.3%) -- via read-out
  ALONE, no new decode dynamics. So the recurrent-noise-compounding / basin-proliferation bound is a
  FULLER CONTRA for the resonator: the aggregation gap that held plurality at MIDDLE 0.464 is CLOSED.
  HONEST RESIDUAL (do not overclaim): oracle_any = 0.806 < 1.0. ~19% of trials the true tuple is NEVER
  reached in any of the R=10 restarts. That reachability ceiling is a SEPARATE open limit (restart budget
  / basin reachability), NOT aggregation-loss. So: aggregation gap CLOSED; reachability ceiling (0.806)
  REMAINS. Two distinct bounds, cleanly decomposed.

FIRING/POSITIVE CONTROLS: K3 baseline 0.742 in [0.40,0.95] (positive control fires); K4 baseline 0.133
  not saturated; arms differ on all 30 instances; verifier vs plurality computed on the SAME paired trials
  (within-trial: same candidate set `tuples`, plurality via Counter, verifier via recon argmax -> lift is
  within-trial not cross-run); cv tight; invariant clean. positive_control_ok=True verified off-disk.

CROSS-ARC OVERLAP: composes DIRECTLY with parent plurality atom (targeted pre-registered extension that
  swaps ONLY the aggregator; decode_trial held verbatim). Parent NOT superseded (plurality read-out still
  gives 0.464; that fact stands). This cell REALIZES the parent's promotion_path. No rediscovery.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_07_resonator_verifier_readout_v1_MM_FULLER_CONTRA_and_META"
CELL_COMMIT = "09446de2d"
TS_ISO = "2026-07-07T21:40:00Z"
TS = 1783460400.0

PARENT_ID = (
    "math::MEASURED_MECHANISM_resonator_K4_external_reset_PARTIAL_CONTRA_of_basin_proliferation_bound_"
    "Glauber_finiteT_dither_plus_R10_restart_plurality_vote_3seed_3_7_13_FULL_N4096_M30_MAXIT60_K4_"
    "plurality_0p133_singleshot_and_0p144_R10_nodither_TO_0p464_at_T0_0p35_best_3p2x_LIFT_cv0p081_scatter_"
    "ok_distinct_wrong_min_992_ge_5_and_wtd_9p18_ge_1p5_so_NOT_basin_measure_trap_failures_DIVERSELY_"
    "scattered_NOT_concentrated_on_1_2_spurious_basins_oracle_any_0p800_true_config_appears_in_ge1_of_R10_"
    "restarts_80pct_but_plurality_harvests_only_46p4pct_so_RESIDUAL_GAP_is_AGGREGATION_LOSS_near_all_10_"
    "restarts_distinct_wtd_9p2_plurality_cannot_concentrate_votes_NOT_unreachable_basins_BOUND_below_0p50_"
    "HARD_PASS_floor_so_PARTIAL_not_full_rescue_REFUTES_fundamental_uncontrable_framing_promotion_path_"
    "oracle_ceiling_0p80_gt_0p50_reachable_with_verifier_aggregator_or_larger_R_positive_controls_K3_base_"
    "0p742_K4_base_0p133_both_pass_composes_basin_proliferation_MM_2026-07-07"
)

atom_math = {
    "id": (
        "math::MEASURED_MECHANISM_resonator_K4_verifier_readout_FULLER_CONTRA_aggregation_gap_CLOSED_"
        "reachability_ceiling_OPEN_reconstruction_verifier_harvests_full_oracle_ceiling_via_readout_alone_"
        "3seed_3_7_13_FULL_N4096_M30_MAXIT60_R10_Glauber_dither_decode_trial_HELD_VERBATIM_only_aggregator_"
        "swapped_plurality_to_argmax_recon_score_K4_T0_0p5_verifier_0p8056_EXACT_EQ_oracle_any_0p8056_"
        "harvest_eq_oracle_at_ALL_30_arms_0_mismatch_lift_plus_0p3528_over_plurality_0p4528_cross_seed_cv_"
        "0p034_pop_0p042_sample_per_seed_0p825_0p825_0p767_baseline_K4_0p133_K3_0p742_in_band_arms_differ_"
        "ALL_30_verifier_hash_ne_plurality_hash_invariant_verifier_le_oracle_0_violations_BY_CONSTRUCTION_"
        "ver_winner_drawn_from_uniq_so_ver_hit_implies_truth_present_NO_ORACLE_LEAK_recon_score_uses_probe_s_"
        "plus_codebooks_only_never_true_tuple_phasor_margin_true_1p0_vs_wrong_1_over_sqrtN_0p0156_at_N4096_"
        "makes_truth_recovery_deterministic_zero_failures_over_wtd_9p19_candidates_TIER_MM_because_0p806_IS_"
        "oracle_ceiling_no_new_reach_readout_realizes_measured_ceiling_and_ceiling_0p806_lt_1p0_reachability_"
        "bound_19pct_never_reached_in_R10_is_SEPARATE_open_limit_restart_budget_NOT_aggregation_STRATEGIC_"
        "aggregation_gap_CLOSED_via_readout_alone_no_new_dynamics_reachability_ceiling_REMAINS_realizes_"
        "parent_plurality_promotion_path_verifier_over_candidate_tuples_composes_partial_contra_MM_2026-07-07"
    ),
    "name": (
        "MATH MM: resonator K4 verifier read-out FULLER CONTRA -- reconstruction verifier harvests the "
        "full oracle ceiling (0.806) via read-out alone; aggregation gap CLOSED, reachability ceiling OPEN"
    ),
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": "proven_fuller_contra_aggregation_gap_closed_reachability_ceiling_0p806_remains_open",
    "cert_class": "resonator_verifier_readout_harvests_oracle_ceiling_aggregation_vs_reachability_decomposition",
    "description": (
        "LANDED-VET (AUDIT-ONLY) of exp_resonator_verifier_readout_v1 commit 09446de2d, 3-seed [3,7,13] "
        "FULL (N=4096, M=30, MAXIT=60, R=10, elapsed 1303.5s). Pre-registered follow-up to the plurality "
        "PARTIAL-CONTRA (parent MM 0.464): decode_trial held VERBATIM (identical Glauber finite-T dither + "
        "R=10 restart machinery, so oracle_any ceiling unchanged); ONLY the aggregator swapped from "
        "plurality vote to argmax reconstruction score. The verifier scores each candidate tuple by "
        "reconstruction fidelity to the input probe s (bind candidate factors -> s_hat; normalized real "
        "inner product Re(<s,s_hat>)/N) and picks argmax -- using ONLY s + codebooks, never the true tuple. "
        "OFF-DISK INDEPENDENT RECOMPUTE (this session): K4 T0=0.5 verifier per-seed [0.825,0.825,0.7667] "
        "mean 0.8056 == oracle_any per-seed [0.825,0.825,0.7667] mean 0.8056 (harvest == oracle EXACT), "
        "lift +0.3528 over plurality mean 0.4528, cross-seed cv 0.034 (pop) / 0.042 (sample). Across ALL 30 "
        "verifier arms harvest==oracle EXACT (0 mismatches), verifier_le_oracle invariant 0 violations, 0 "
        "verifier>oracle, arms-differ on all 30 (verifier-winner-hash != plurality-winner-hash). Baselines: "
        "K4 0.133 (not saturated), K3 0.742 in [0.40,0.95] (positive control fires). T0 sweep monotone: "
        "0.00->0.247, 0.10->0.747, 0.20->0.789, 0.35->0.800, 0.50->0.806. MECHANISM (no oracle leak): probe "
        "s is the legitimate decode-time input (product of true factors, by definition of the factorization "
        "task), NOT a label peek; recon_score compares to s only. verifier<=oracle holds BY CONSTRUCTION "
        "(ver_winner drawn from candidate set uniq, so ver_hit implies truth_present); the NON-trivial "
        "finding is harvest==oracle EXACTLY -- the phasor margin (true 1.0 vs wrong ~1/sqrt(N)=0.0156 at "
        "N=4096) makes truth-when-present recovery deterministic over ~9.19 distinct candidates with ZERO "
        "failures across 3 seeds. TIER MEASURED_MECHANISM (proven-bound, NOT chain-grade): (a) headline "
        "0.806 IS the oracle ceiling -- read-out adds no new reach, it realizes an already-measured ceiling; "
        "(b) harvest==oracle is theory-predicted / by-construction-adjacent given the deterministic phasor "
        "margin; (c) the honest claim is WEAKER than 'verifier rescues K4' -- the read-out CLOSES the "
        "aggregation gap but the ceiling 0.806<1.0 (~19% of trials truth NEVER reached in R=10) is a "
        "SEPARATE open reachability bound (restart budget / basin reachability), NOT aggregation. STRATEGIC: "
        "FULLER CONTRA of the recurrent-noise-compounding / basin-proliferation bound for the resonator -- "
        "the aggregation gap that held plurality at MIDDLE 0.464 is CLOSED via read-out ALONE (no new decode "
        "dynamics); reachability ceiling (0.806) REMAINS the open frontier. Realizes the parent atom's "
        "registered promotion_path ('reachable via verifier over candidate tuples'); parent NOT superseded "
        "(plurality still 0.464)."
    ),
    "provenance": {
        "cell": "experiments/exp_resonator_verifier_readout_v1.py",
        "commit": CELL_COMMIT,
        "prereg": "preregs/2026-07-07_resonator_verifier_readout_v1.md",
        "anchor": "resonator_verifier_readout_v1",
        "metrics_path": "data/exp_resonator_verifier_readout_v1/metrics.json",
        "seeds": [3, 7, 13],
        "run_mode": "full",
        "elapsed_s": 1303.523870700039,
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent .venv recompute: harvest==oracle EXACT at all 30 verifier arms (0 mismatch), 0 "
            "invariant violations, 0 verifier>oracle; K4 T0=0.5 verifier 0.8056 plurality 0.4528 lift "
            "0.3528 cv 0.034/0.042; baselines K4 0.133 K3 0.742; arms differ all 30; T0 sweep monotone. "
            "Every detail-block number reproduced to 1e-9. Mechanism inspected line 95/300-322: no oracle "
            "leak; verifier<=oracle by construction."
        ),
    },
    "verified_numbers": {
        "K4_T0_0p5": {"verifier_per_seed": [0.825, 0.825, 0.7666666666666667],
                      "plurality_per_seed": [0.4666666666666667, 0.5083333333333333, 0.38333333333333336],
                      "oracle_per_seed": [0.825, 0.825, 0.7666666666666667],
                      "verifier_mean": 0.8055555555555555, "plurality_mean": 0.4527777777777778,
                      "oracle_mean": 0.8055555555555555, "lift": 0.3527777777777777,
                      "cv_pop": 0.0341, "cv_sample": 0.0418},
        "baseline_K4_mean": 0.13333333333333333,
        "baseline_K3_mean": 0.7416666666666667,
        "harvest_eq_oracle_arms": "30/30 EXACT",
        "invariant_violations": 0,
        "verifier_gt_oracle_arms": 0,
        "arms_differ_instances": "30/30 verifier_hash != plurality_hash",
        "K4_verifier_by_t0": {"0.0": 0.2472, "0.1": 0.7472, "0.2": 0.7889, "0.35": 0.8000, "0.5": 0.8056},
    },
    "tier_reasons": [
        "headline 0.806 IS the oracle_any ceiling -- verifier adds no new reach, realizes an already-measured ceiling",
        "harvest==oracle is theory-predicted / by-construction-adjacent (deterministic phasor margin 1.0 vs 0.0156 at N=4096)",
        "honest claim weaker than initial framing: aggregation gap CLOSED but reachability ceiling 0.806<1.0 remains a SEPARATE open bound",
        "proven boundary + clean mechanism decomposition = MEASURED_MECHANISM, not chain-grade",
    ],
    "strategic_verdict": {
        "fuller_contra": "aggregation gap CLOSED via read-out alone (no new decode dynamics); plurality MIDDLE 0.464 -> verifier HARD_PASS 0.806",
        "honest_residual_reachability_ceiling": "oracle_any=0.806<1.0; ~19% of trials truth NEVER reached in R=10 restarts; SEPARATE open bound (restart budget / basin reachability), NOT aggregation",
        "two_bounds_decomposed": "aggregation-loss CLOSED; reachability-ceiling OPEN",
        "realizes_parent_promotion_path": "parent registered 'reachable via verifier over candidate tuples'; this cell realizes it",
    },
    "no_oracle_leak_audit": (
        "_recon_score(books,s,cand,K) line 95 scores candidate reconstruction vs input probe s only; never "
        "compares cand==true. Probe s rebuilt line 300-303 from books[k][true[k]] = the legitimate "
        "decode-time input (product of true factors IS the probe by definition of factorization), not a "
        "label peek. ver_winner=max(uniq,recon) drawn from candidate set, so ver_hit implies truth_present "
        "-> verifier<=oracle BY CONSTRUCTION. harvest==oracle EXACT is the empirical finding (phasor margin "
        "deterministic at N=4096)."
    ),
    "positive_control_check": (
        "K3 baseline 0.742 in [0.40,0.95] fires; K4 baseline 0.133 not saturated; verifier vs plurality on "
        "SAME paired within-trial candidate set (lift within-trial not cross-run); arms differ all 30; cv "
        "tight 0.034; invariant clean. positive_control_ok=True off-disk. Auditor-2026-07-01 rule cleared."
    ),
    "composes": [PARENT_ID],
    "compose_note": (
        "Targeted pre-registered extension of parent plurality PARTIAL-CONTRA: decode_trial held VERBATIM, "
        "ONLY aggregator swapped. Parent NOT superseded (plurality 0.464 stands). This cell REALIZES the "
        "parent's registered promotion_path."
    ),
    "cross_arc_overlap_check": (
        "Direct compose with parent resonator_glauber_plurality_v1 MM (same anchor family, cosine>0.30 "
        "expected). NOT a rediscovery -- pre-registered aggregator-only swap realizing the parent's promotion "
        "path. Genuinely new: the oracle ceiling is now ACHIEVED by a leak-free read-out, not just measured."
    ),
    "residual_caveats": [
        "0.806 is the oracle ceiling, not 1.0: ~19% reachability gap is a SEPARATE open bound (restart budget / basin reachability)",
        "harvest==oracle is by-construction-deterministic at N=4096 (phasor margin); would need re-verification if N shrinks toward the 1/sqrt(N)~wrong-score regime",
        "verifier is a perfect factorization-checker given probe+codebooks; this is a read-out mechanism, not a new decode capability",
    ],
    "anchor": "resonator_verifier_readout_v1",
    "cell_commit": CELL_COMMIT,
    "seeds": [3, 7, 13],
    "run_mode": "full",
    "cardinality_ok": True,
    "arms_differ_verified": True,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": "2026-07-07_resonator_verifier_readout_vet",
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "resonator K4 verifier read-out harvests oracle ceiling 0.806 aggregation gap closed",
        "reconstruction verifier argmax recon-score fuller contra basin-proliferation bound read-out alone",
        "aggregation-loss vs reachability-ceiling decomposition K4 plurality 0.464 to verifier 0.806",
        "verifier<=oracle by construction harvest==oracle exact phasor margin deterministic N4096 no oracle leak",
    ],
}
atom_math["added_atom_id"] = atom_math["id"]

atom_meta = {
    "id": (
        "meta::DISCIPLINE_residual_gap_decomposition_aggregation_loss_vs_reachability_ceiling_a_readout_that_"
        "harvests_the_oracle_ceiling_CLOSES_aggregation_loss_but_NOT_reachability_before_calling_a_recurrent_"
        "noise_bound_fundamental_MEASURE_oracle_any_prob_truth_in_ge1_restart_then_split_residual_into_"
        "AGGREGATION_LOSS_truth_reached_but_outvoted_recoverable_by_smarter_readout_verifier_over_candidates_"
        "vs_REACHABILITY_CEILING_truth_never_reached_in_restart_budget_needs_new_dynamics_or_larger_R_"
        "verifier_readout_recon_score_vs_input_probe_recovers_ALL_reached_answers_when_phasor_margin_large_"
        "true_1p0_vs_wrong_1_over_sqrtN_so_verifier_harvest_eq_oracle_any_by_deterministic_margin_leak_free_"
        "uses_probe_plus_codebooks_only_evidenced_resonator_K4_plurality_MIDDLE_0p464_to_verifier_0p806_eq_"
        "oracle_aggregation_CLOSED_reachability_0p806_lt_1p0_still_OPEN_2026-07-07"
    ),
    "name": (
        "META: decompose a residual capability gap into AGGREGATION-LOSS (recoverable by smarter read-out) "
        "vs REACHABILITY-CEILING (needs new dynamics) BEFORE calling a recurrent-noise bound fundamental"
    ),
    "corpus": "meta",
    "tier": "META_RULE",
    "kind": "methodology_discipline",
    "cert_status": "cert_neutral_methodology",
    "cert_class": "residual_gap_decomposition_aggregation_vs_reachability_readout_harvest",
    "description": (
        "CERT-NEUTRAL DISCIPLINE (evidenced by the resonator external-reset arc, plurality->verifier "
        "read-out). When an iterated/restart-based decoder falls short of a success bar, do NOT immediately "
        "attribute the residual gap to a 'fundamental' recurrent-noise-compounding / basin bound. First "
        "MEASURE oracle_any = P(truth appears in >=1 of the R restarts), then DECOMPOSE the residual into "
        "two orthogonal bounds: (1) AGGREGATION-LOSS = truth was reached but the read-out (e.g. plurality "
        "vote) failed to select it -- this is recoverable by a SMARTER read-out with NO new dynamics; "
        "(2) REACHABILITY-CEILING = truth was NEVER reached within the restart budget -- this needs new "
        "dynamics or a larger R and is a SEPARATE bound. A reconstruction VERIFIER read-out (score each "
        "candidate by fidelity to the input probe s -- bind candidate factors -> s_hat, normalized real "
        "inner product -- argmax) HARVESTS the full oracle ceiling when the discriminating margin is large: "
        "for FHRR phasor products the true tuple scores 1.0 and any wrong tuple ~1/sqrt(N), so at large N "
        "the verifier recovers EVERY reached answer deterministically and leak-free (uses probe + codebooks "
        "only, never the label). Consequence: harvest == oracle_any by the deterministic margin, so the "
        "verifier CLOSES aggregation-loss entirely but CANNOT move the reachability ceiling. EVIDENCE: "
        "resonator K4, decode_trial held verbatim, aggregator-only swap -- plurality MIDDLE 0.464 -> "
        "verifier 0.806 == oracle_any (aggregation CLOSED); the residual 0.806 < 1.0 (~19% never reached) "
        "is the still-OPEN reachability ceiling. PRACTICE: (a) always report oracle_any alongside the "
        "achieved read-out; (b) label which sub-bound a negative belongs to before claiming 'fundamental'; "
        "(c) a read-out rescue is a FULLER-but-still-bounded contra (MEASURED_MECHANISM), not a full "
        "capability rescue, because the reachability ceiling remains."
    ),
    "provenance": {
        "evidenced_by_math_atom": atom_math["id"],
        "parent_partial_contra": PARENT_ID,
        "cells": [
            "experiments/exp_resonator_glauber_plurality_v1.py (plurality, oracle_any measured 0.80)",
            "experiments/exp_resonator_verifier_readout_v1.py (verifier harvest 0.806 == oracle)",
        ],
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
    },
    "practice_rules": [
        "measure oracle_any = P(truth in >=1 restart) before attributing a residual gap to a fundamental bound",
        "split residual into AGGREGATION-LOSS (reached-but-outvoted, read-out-recoverable) vs REACHABILITY-CEILING (never-reached, needs new dynamics / larger R)",
        "a reconstruction verifier read-out (score vs input probe, leak-free) harvests the full oracle ceiling when the discriminating margin is large (phasor true 1.0 vs wrong 1/sqrt(N))",
        "harvest==oracle by deterministic margin -> read-out CLOSES aggregation-loss but CANNOT move reachability ceiling",
        "a read-out rescue is a FULLER-but-bounded contra (MM), not a full capability rescue -- report the reachability ceiling as the remaining frontier",
    ],
    "anchor": "resonator_verifier_readout_v1",
    "cell_commit": CELL_COMMIT,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": "2026-07-07_resonator_verifier_readout_vet",
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "aggregation-loss vs reachability-ceiling decomposition",
        "measure oracle_any before calling a recurrent-noise bound fundamental",
        "verifier read-out harvests oracle ceiling when phasor margin large closes aggregation not reachability",
        "read-out rescue is fuller-but-bounded contra not full capability rescue",
    ],
}
atom_meta["added_atom_id"] = atom_meta["id"]

ledger_math = {
    "ts": TS,
    "ts_iso": TS_ISO,
    "atom_id": atom_math["id"],
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "disposition": "proven_fuller_contra_aggregation_gap_closed_reachability_ceiling_open",
    "cert_status": "proven_fuller_contra_verifier_readout_harvests_oracle_ceiling_0p806_reachability_0p806_remains",
    "cert_class": "resonator_verifier_readout_harvests_oracle_ceiling_aggregation_vs_reachability_decomposition",
    "cert_increment_delta": 1,
    "cert_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cert_delta_note": (
        "MM +1: verifier read-out realizes the parent atom's registered promotion path (oracle ceiling "
        "reachable via verifier over candidate tuples). Aggregation gap CLOSED (plurality 0.464 -> verifier "
        "0.806 == oracle_any). Tier MM (not CG): 0.806 IS the oracle ceiling (no new reach), harvest==oracle "
        "is by-construction-deterministic phasor margin, and reachability ceiling 0.806<1.0 remains a "
        "SEPARATE open bound. Parent NOT superseded (plurality 0.464 stands)."
    ),
    "verified_off_data": True,
    "anchor": "resonator_verifier_readout_v1",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": "2026-07-07_resonator_verifier_readout_vet",
    "composes": [PARENT_ID],
}

ledger_meta = {
    "ts": TS,
    "ts_iso": TS_ISO,
    "atom_id": atom_meta["id"],
    "corpus": "meta",
    "tier": "META_RULE",
    "disposition": "cert_neutral_methodology_discipline",
    "cert_status": "cert_neutral_residual_gap_decomposition_aggregation_vs_reachability",
    "cert_class": "residual_gap_decomposition_aggregation_vs_reachability_readout_harvest",
    "cert_increment_delta": 0,
    "cert_delta": {"CG": 0, "MM": 0, "HF": 0},
    "cert_delta_note": "CERT-neutral META discipline; no cert increment.",
    "verified_off_data": True,
    "anchor": "resonator_verifier_readout_v1",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": "2026-07-07_resonator_verifier_readout_vet",
    "evidenced_by": atom_math["id"],
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
    import time as _time
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            _time.sleep(0.1 * (2 ** _attempt))

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
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_math, "math/atoms (resonator verifier read-out MM FULLER CONTRA)")
    append_jsonl_a5(META_ATOMS, atom_meta, "meta/atoms (residual-gap decomposition discipline)")
    append_jsonl_a5(CERT_LEDGER, ledger_math, "cert_ledger (MM +1 verifier read-out)")
    append_jsonl_a5(CERT_LEDGER, ledger_meta, "cert_ledger (META discipline, cert-neutral)")
    print(f"[A5] DONE OK")
    print(f"[A5] resonator_verifier_readout_v1 -> MM +1 (fuller contra; aggregation CLOSED, reachability OPEN) + META discipline")


if __name__ == "__main__":
    main()
