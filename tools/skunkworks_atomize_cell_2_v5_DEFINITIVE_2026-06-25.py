"""Skunkworks 2026-06-25 -- A5 atomize for Cell 2 v5 DEFINITIVE tier ruling.

TIER RULING NOTE: notes/skunkworks_tier_ruling_cell_2_v5_DEFINITIVE_2026-06-25.md
SOURCE DATA: data/exp_substrate_compose_freq_routing_v5_DEFINITIVE/metrics.json
PRIOR v4 REFERENT: data/exp_substrate_compose_freq_routing_v4_hparam_sweep/metrics.json
PRIOR v4 ATOM STATE: prose-only (no entry in math/atoms.jsonl, meta/atoms.jsonl, cert_ledger.jsonl)
DIRECTOR RATIFICATION: in-thread 2026-06-25

Two atoms:

1. math::T3/EXP_substrate_compose_freq_routing_v5_DEFINITIVE
   CHAIN_GRADE_DEFINITIVE; cert_increment_delta = +1
   Mechanism: frequency-routed differential plasticity (freq_rank=100,
   lr_high=0.5, lr_rare=0.2, n_steps=2000) on Hebbian outer-product W
   matrix beats baseline by +0.148 BPC at N_DIM=8192 AND +0.144 BPC at
   N_DIM=4096; 5 fresh seeds [7, 13, 17, 23, 29]; all per-seed paired
   lifts above +0.10 gate; n_steps=3000 plateaus; v4 number replicates.

2. meta::META/CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION
   META rule; CERT-neutral (delta=0)
   Minimal upgrade path from CHAIN_GRADE_PARTIAL to CHAIN_GRADE_DEFINITIVE.

DISCIPLINES HONORED:
  - Fix #28 default under-claim: cross-N capacity-graded scaling NOT separately
    atomized (delta 0.0065 BPC below CV noise floor for 2-point scaling claim)
  - Per-arm metrics read directly off per_seed (NOT verdict_msg framing)
  - verify-the-referent: v4 atomization state checked across math+meta+ledger,
    confirmed prose-only (fresh write, no supersede needed)
  - A5 PRE/POST: snapshot atom counts before+after; verify round-trip load
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
    build_chain_grade_ruling_row,
    build_measured_mechanism_row,
)


STORE_ROOT = Path("D:/AI/hd-instrument/data/substrate_index")
ATOMIZED_BY = "skunkworks_atomize_cell_2_v5_DEFINITIVE_2026-06-25"
NOTES_PATH_RULING = "notes/skunkworks_tier_ruling_cell_2_v5_DEFINITIVE_2026-06-25.md"
METRICS_PATH_V5 = "data/exp_substrate_compose_freq_routing_v5_DEFINITIVE/metrics.json"
PREREG_PATH_V5 = "preregs/2026-06-25_substrate_compose_freq_routing_v5_DEFINITIVE.md"


# ============================================================================
# Atom 1 -- math::T3/EXP_substrate_compose_freq_routing_v5_DEFINITIVE
# ============================================================================

def build_atom_v5_definitive() -> Atom:
    return Atom(
        id="T3/EXP_substrate_compose_freq_routing_v5_DEFINITIVE",
        name=(
            "Substrate compose freq routing v5 DEFINITIVE -- CHAIN_GRADE_DEFINITIVE "
            "(FREQ_ROUTED_DEEPER beats baseline by +0.148 BPC at N=8192 AND "
            "+0.144 BPC at N=4096; 5 fresh seeds; n_steps=3000 plateaus; "
            "v4 number replicates; first Stage 2 architectural atom at "
            "CHAIN_GRADE_DEFINITIVE)"
        ),
        description=(
            "At V=4000 / N_TRAIN=100k text8 / word2vec sparse-bipolar f=0.05 "
            "encoder, frequency-routed differential plasticity on Hebbian "
            "outer-product W matrix achieves CHAIN_GRADE_DEFINITIVE tier:\n\n"
            "PER-ARM (5 seeds [7, 13, 17, 23, 29], recomputed off per_seed):\n"
            "  ARM_BASELINE_N8192            bpc_best_mean=7.3124  cv=0.0018\n"
            "  ARM_FREQ_DEEPER_N8192         bpc_best_mean=7.1647  cv=0.0009\n"
            "  ARM_BASELINE_N4096            bpc_best_mean=7.3148  cv=0.0015\n"
            "  ARM_FREQ_DEEPER_N4096         bpc_best_mean=7.1712  cv=0.0009\n"
            "  ARM_FREQ_DEEPER_NSTEPS_3000   bpc_best_mean=7.1610  cv=0.0013\n\n"
            "KEY LIFTS (paired same-N):\n"
            "  N8192 lift = 7.3124 - 7.1647 = +0.1477 BPC\n"
            "  N4096 lift = 7.3148 - 7.1712 = +0.1435 BPC\n"
            "  Lift delta cross-N = 0.0042 BPC (similar but NOT identical -> "
            "rules out co-saturation at metric ceiling; capacity-graded)\n"
            "  n_steps 2000->3000 delta = 0.0037 BPC (plateaued; 2.5% of "
            "n_steps 0->2000 gain)\n\n"
            "ALL 5 PER-SEED PAIRED LIFTS PASS >=0.10 CHAIN-GRADE GATE:\n"
            "  s7:  base 7.3187 - freq 7.1632 = +0.1555\n"
            "  s13: base 7.3153 - freq 7.1543 = +0.1610\n"
            "  s17: base 7.2882 - freq 7.1626 = +0.1256 (min)\n"
            "  s23: base 7.3126 - freq 7.1710 = +0.1416\n"
            "  s29: base 7.3270 - freq 7.1723 = +0.1547\n\n"
            "SANITY RAILS:\n"
            "  BASE_N8192 7.3124 vs fair_harness rail 7.3065: drift +0.0059, "
            "tolerance 0.05 -> PASS (12% of budget)\n"
            "  v4 ARM_FREQ_DEEPER_TRAIN 3-seed mean 7.1590 vs v5 5-seed mean "
            "7.1647: drift +0.0057, tolerance 0.05 -> PASS (v4 number "
            "replicates under expanded seed pool)\n\n"
            "DISCRIMINATING MECHANISM (per arm, all 5 seeds consistent):\n"
            "  top1 on top-100 high-freq tokens = 0.335-0.348\n"
            "  top1 on tail-3900 rare tokens = 0.000-0.002\n"
            "  differential ~ 0.33-0.36 per seed (FREQ_DEEPER_N8192)\n"
            "  -> Frequency-routed learning is doing what its name says: "
            "high-freq tokens get learned, rare tokens stay near-uniform.\n\n"
            "BANDS CLEARED:\n"
            "  HARD_PASS cap 7.20 -> cleared at 7.1647 (0.035 BPC below cap)\n"
            "  Chain-grade gap >=0.10 -> cleared at +0.148 (1.48x gate)\n"
            "  CV <=0.03 (chain-grade definitive) -> cleared at 0.0009 (33x "
            "below cap; mechanism-consistent, NOT by-construction-saturation; "
            "baseline-CV at same regime = 0.0018, both arms show real seed "
            "variability; top1 std=0.0037, MRR std=0.0025, multiple metrics "
            "show non-degenerate spread)\n\n"
            "SKEPTIC CHECKS RESOLVED:\n"
            "  (A) CV=0.0009 NOT by-construction-saturation: BASELINE_CV=0.0018 "
            "in same regime; per-seed FREQ_N8192 ranges 7.1543-7.1723 (real "
            "0.018 spread); top-1 std non-zero; multiple metrics show "
            "seed-level variation.\n"
            "  (B) n_steps=3000 plateau NOT artifact: top-1 still climbing "
            "(0.2459 at 3000 vs 0.2398 at 2000); BPC plateau is at chosen "
            "(T, lambda) grid operating point.\n"
            "  (C) Cell I v4 (basis-layer) contamination: orthogonal "
            "(encoder-architectural vs learning-rule discipline; different "
            "encoder).\n\n"
            "PRIOR v4 PARTIAL ATOM STATE: PROSE-ONLY (confirmed via grep on "
            "math/atoms.jsonl + meta/atoms.jsonl + cert_ledger.jsonl; "
            "intended atom-id T3/EXP_substrate_compose_freq_routing_v4_"
            "DEEPER_TRAIN_CGP from notes/skunkworks_tier_ruling_3landings_"
            "post_user_away_2026-06-25.md was never actually written to "
            "Store). v5 lands FRESH as CHAIN_GRADE_DEFINITIVE; no demote "
            "or supersede entry needed; net +1 to CERT N.\n\n"
            "HONEST SCOPE (what this atom does NOT show):\n"
            "  - Does not test other (rank, lr, n_steps) regions of hparam "
            "space outside v4 sweep grid.\n"
            "  - Does not test cross-V scaling (V=4000 only).\n"
            "  - Does not test cross-corpus (text8 only).\n"
            "  - Cross-N at only two points (4096 + 8192); no capacity-graded "
            "scaling law claim.\n"
            "  - n_steps=3000 arm tests upper-bound at N=8192 only.\n"
            "  - Encoder is word2vec sparse-bipolar (pretrained-borrowed); "
            "substrate-native-encoder swap remains an open variable.\n\n"
            "TIER: CHAIN_GRADE_DEFINITIVE; delta=+1; first Stage 2 architectural "
            "atom at DEFINITIVE tier in compose lane."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CHAIN_GRADE_DEFINITIVE",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "verdict": (
                "CHAIN_GRADE_DEFINITIVE_substrate_compose_freq_routing_v5_5seeds_"
                "7_13_17_23_29_N_DIM_8192_AND_N_DIM_4096_V_4000_text8_100k_"
                "word2vec_sparse_bipolar_f_0p05_FREQ_DEEPER_N8192_bpc_7p1647_"
                "cv_0p0009_lift_plus_0p1477_FREQ_DEEPER_N4096_bpc_7p1712_cv_"
                "0p0009_lift_plus_0p1435_lift_delta_cross_N_0p0042_capacity_"
                "graded_not_co_saturating_n_steps_3000_plateau_delta_0p0037_"
                "v4_3seed_number_7p1590_replicates_drift_0p0057_within_tol_"
                "0p05_BASELINE_N8192_rail_drift_0p0059_within_tol_0p05_all_"
                "5_per_seed_paired_lifts_above_0p10_gate_min_seed17_plus_"
                "0p1256_max_seed13_plus_0p1610_discriminating_top1_high_freq_"
                "0p34_to_0p35_top1_low_freq_0p000_to_0p002_differential_0p33_"
                "to_0p36_HARD_PASS_cap_7p20_cleared_CV_0p03_cleared_at_0p0009_"
                "33x_below_cap_NOT_by_construction_saturation_baseline_CV_"
                "0p0018_real_seed_spread_top1_std_0p0037_MRR_std_0p0025_"
                "skeptic_checks_A_B_C_all_resolved_v4_atom_was_prose_only_"
                "fresh_write_no_supersede_first_Stage_2_architectural_"
                "DEFINITIVE_atom_compose_lane"
            ),
            "cell_commit": "v5_DEFINITIVE",
            "metrics_path": METRICS_PATH_V5,
            "prereg_path": PREREG_PATH_V5,
            "notes_path": NOTES_PATH_RULING,
            "verified_off_data": (
                "Cert-owner read detail.by_arm_agg + per_seed directly from "
                "metrics.json via .venv recompute (NOT verdict_msg framing). "
                "Per-arm bpc_best_mean reproduced via population stdev / mean "
                "for cv. Per-seed paired lifts computed off per_seed[i].by_arm "
                "dict (same-seed paired). Sanity rails cross-checked against "
                "data/exp_fair_harness_substrate_as_lm_v1/metrics.json (rail "
                "7.3065). v4 replication cross-checked against data/exp_"
                "substrate_compose_freq_routing_v4_hparam_sweep/metrics.json "
                "(v4 ARM_FREQ_DEEPER_TRAIN bpc_best_mean=7.159 cv=0.0029 "
                "n_seeds=3 seeds [7, 17, 23]). v5 expanded seed pool with "
                "[13, 29] (set-disjoint additions; seeds [7, 17, 23] match v4 "
                "for direct paired replication). zero_llm_calls_at_inference="
                "True (n_llm=0 verified per per_seed). run_mode='full'. "
                "device='cuda'. crossN_check.both_pass=True. v4_replication_"
                "check.ok=True. nsteps_upper_bound_check.plateaued=True. "
                "Both sanity rails OK. v4 atomization state checked via "
                "grep on math/atoms.jsonl + meta/atoms.jsonl + cert_ledger."
                "jsonl for 'freq_routing|FREQ_DEEPER|substrate_compose_freq' "
                "-> ZERO HITS (prose-only). v5 lands fresh, no supersede."
            ),
            "honest_scope": (
                "v5 DEFINITIVE upgrade of v4 ARM_FREQ_DEEPER_TRAIN (was "
                "CHAIN_GRADE_PARTIAL prose-only, never atomized). v5 ships "
                "5 seeds + cross-N replication (N_DIM=8192 + N_DIM=4096) + "
                "upper-bound n_steps probe (2000 vs 3000). DEFINITIVE = "
                "primary FREQ_DEEPER at N=8192 reproduces v4 7.159 within "
                "+/-0.05 AND beats same-N baseline by >=0.10 AND FREQ_DEEPER "
                "at N=4096 also beats its baseline by >=0.10 AND CV<=0.03 "
                "across 5 seeds AND both sanity rails pass AND n_steps=3000 "
                "plateaus AND all 5 per-seed paired lifts above +0.10 gate. "
                "WHAT THIS DOES NOT SHOW: doesn't test other (rank/lr/"
                "architectural-composition) knobs; doesn't test V scaling; "
                "doesn't test cross-corpus scaling; cross-N at only two "
                "points (4096 + 8192) so no capacity-graded scaling-law "
                "claim; n_steps=3000 arm tests upper-bound at N=8192 only "
                "(not at N=4096); encoder is word2vec sparse-bipolar "
                "(pretrained-borrowed Path-C debate open). Per Fix #28 "
                "default under-claim: cross-N capacity-graded scaling NOT "
                "separately atomized (delta 0.0065 BPC across N is below "
                "CV noise floor for 2-point scaling claim)."
            ),
            "n_seeds": 5,
            "seeds": [7, 13, 17, 23, 29],
            "primary_arm": "ARM_FREQ_DEEPER_N8192",
            "primary_arm_bpc_best_mean": 7.1647,
            "primary_arm_bpc_best_cv": 0.0009,
            "primary_arm_lift_over_baseline_bpc": 0.1477,
            "secondary_arm": "ARM_FREQ_DEEPER_N4096",
            "secondary_arm_bpc_best_mean": 7.1712,
            "secondary_arm_lift_over_baseline_bpc": 0.1435,
            "upper_bound_arm": "ARM_FREQ_DEEPER_NSTEPS_3000",
            "upper_bound_arm_bpc_best_mean": 7.1610,
            "upper_bound_arm_delta_from_n2000_bpc": 0.0037,
            "upper_bound_arm_plateaued": True,
            "baseline_n8192_bpc": 7.3124,
            "baseline_n4096_bpc": 7.3148,
            "fair_harness_rail_bpc": 7.3065,
            "rail_drift_bpc": 0.0059,
            "rail_drift_within_tolerance": True,
            "v4_reference_bpc": 7.159,
            "v4_replication_drift_bpc": 0.0057,
            "v4_replication_ok": True,
            "v4_prior_atom_state": "PROSE_ONLY_NEVER_WRITTEN_TO_STORE_OR_LEDGER",
            "supersedes_atom_id": None,
            "cross_N_replication_both_pass": True,
            "cross_N_lift_delta_bpc": 0.0042,
            "co_saturation_ruled_out": True,
            "all_5_per_seed_paired_lifts_pass_gate": True,
            "per_seed_lifts_bpc": {
                "7": 0.1555,
                "13": 0.1610,
                "17": 0.1256,
                "23": 0.1416,
                "29": 0.1547,
            },
            "min_per_seed_lift_bpc": 0.1256,
            "discriminating_top1_high_freq_range": [0.335, 0.348],
            "discriminating_top1_low_freq_range": [0.000, 0.002],
            "discriminating_freq_differential_range": [0.3335, 0.3480],
            "N_DIM_primary": 8192,
            "N_DIM_secondary": 4096,
            "N_TRAIN": 100000,
            "N_HELD": 20000,
            "VOCAB_CAP": 4000,
            "ENCODER": "word2vec_sparse_bipolar_f_0p05",
            "FREQ_ROUTE_RANK": 100,
            "FREQ_LR_HIGH": 0.5,
            "FREQ_LR_RARE": 0.2,
            "N_STEPS_PRIMARY": 2000,
            "N_STEPS_UPPER_BOUND": 3000,
            "arms": [
                "ARM_BASELINE_N8192",
                "ARM_FREQ_DEEPER_N8192",
                "ARM_BASELINE_N4096",
                "ARM_FREQ_DEEPER_N4096",
                "ARM_FREQ_DEEPER_NSTEPS_3000",
            ],
            "cell_self_verdict": "HARD_PASS_CHAIN_GRADE_DEFINITIVE",
            "device": "cuda",
            "elapsed_s": 2618.63,
            "gpu_peak_mem_gb": 2.433,
            "run_mode": "full",
            "zero_llm_calls_at_inference": True,
            "n_llm_calls": 0,
            "composes_with": [
                "META_PROSPECTIVE_BANDS_FRESH_SEEDS_eliminates_retrofit_confound",
                "META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift",
                "META_CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION",
                "META_phase_diagram_action_at_any_position_v1",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_not_verdict_msg_framing",
                "Fix_28_default_under_claim_by_construction_saturation_not_chain_grade",
                "verify_referent_discipline_v4_atom_state_grep",
                "Cell_I_v4_DEFINITIVE_companion_ruling_same_day_2026-06-25",
                "USER_results_to_application_cadence_same_cycle_atomize",
                "USER_brain_is_existence_proof_higher_prior_for_brain_grounded",
                "Director_ratification_in_thread_2026-06-25",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
        },
        aliases=[],
    )


# ============================================================================
# Atom 2 -- meta::META/CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION
# ============================================================================

def build_atom_meta_cross_N_rule() -> Atom:
    return Atom(
        id="META/CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION",
        name=(
            "META: cross-N replication as definitive upgrade criterion "
            "(minimal upgrade path CHAIN_GRADE_PARTIAL -> CHAIN_GRADE_"
            "DEFINITIVE when prior PARTIAL rests on single-N evidence; "
            "validated by substrate_compose_freq_routing v4 -> v5)"
        ),
        description=(
            "META RULE (CERT-neutral discipline atom):\n\n"
            "When a CHAIN_GRADE_PARTIAL ruling rests on single-N evidence "
            "(e.g., v4 at N_DIM=8192 only), the minimal upgrade path to "
            "CHAIN_GRADE_DEFINITIVE is:\n\n"
            "  (a) Expand seed pool by >=2 fresh seeds set-disjoint from "
            "prior (v4 used [7, 17, 23]; v5 added [13, 29] to enable both "
            "paired direct replication AND fresh-seed verification).\n\n"
            "  (b) Add cross-N arm at a different capacity (e.g., N/2 OR "
            "2N). v5 added N_DIM=4096 alongside N_DIM=8192.\n\n"
            "  (c) Verify cross-N lifts are within ~+/-0.02 BPC of each "
            "other (similar but NOT identical). v5: N8192 lift +0.1477, "
            "N4096 lift +0.1435, delta 0.0042 -> within tolerance. \n"
            "      IDENTICAL lifts indicate co-saturation at metric ceiling, "
            "NOT capacity-graded computation -- this is a key failure mode "
            "the rule guards against.\n\n"
            "  (d) Add upper-bound probe on the relevant knob (e.g., "
            "n_steps x 1.5 OR 2x), and verify plateau. v5: n_steps=3000 arm "
            "delta from n_steps=2000 = 0.0037 BPC (2.5% of n_steps 0->2000 "
            "gain). Plateau confirmed -> rules out 'just train longer' "
            "interpretation.\n\n"
            "COMPOSES WITH (cert-ladder upgrade-path discipline set, 3 "
            "rules now codified):\n"
            "  - META_PROSPECTIVE_BANDS_FRESH_SEEDS (Cell I v4 ruling "
            "2026-06-25 morning): locked-via-assertion + previously-unseen "
            "seeds eliminates C3_retrofit_risk_band_tuning confound.\n"
            "  - META_M2_tight_rail_from_different_config_can_mask_direction_"
            "correct_lift (compose_heterogeneous_routing_v2_RESCUE 2026-06-25): "
            "rail-tolerance must be config-matched OR widened when cell runs "
            "under reduced capacity vs the rail's referent config.\n"
            "  - THIS RULE: cross-N replication + upper-bound probe + fresh "
            "seeds = the cert-ladder DEFINITIVE upgrade path.\n\n"
            "OPERATIONAL CHECKLIST FOR DIRECTOR-SIDE PRE-DISPATCH:\n"
            "  When designing a v5+ upgrade cell for a v(N) CHAIN_GRADE_"
            "PARTIAL referent, the prereg MUST include:\n"
            "    [ ] Seeds: existing seed set + >=2 set-disjoint additions\n"
            "    [ ] Cross-N: original N + at least one other N (typically "
            "N/2 OR 2N)\n"
            "    [ ] Upper-bound knob probe: >=1 arm at 1.5x or 2x the "
            "knob value of the principle arm\n"
            "    [ ] Pre-reg bands: HARD_PASS cap + chain-grade gap + CV "
            "max defined BEFORE data lands\n"
            "    [ ] Sanity rails: compare baseline to known rail referent\n"
            "    [ ] Verify-the-referent: confirm prior PARTIAL atom-state "
            "in Store vs prose-only (determines whether v(N+1) is "
            "supersede+1 or fresh +1).\n\n"
            "VALIDATED BY: substrate_compose_freq_routing v4 (CHAIN_GRADE_"
            "PARTIAL, prose-only, single N=8192, 3 seeds) -> v5 (CHAIN_GRADE_"
            "DEFINITIVE, cross-N + 5 seeds + n_steps upper-bound) succeeded "
            "on first dispatch.\n\n"
            "FALSIFICATION CONDITIONS (when this rule WOULD NOT enable "
            "definitive upgrade):\n"
            "  - Cross-N lifts identical to >3 decimal places -> "
            "co-saturation, NOT capacity-graded; rule (c) catches this.\n"
            "  - Cross-N lift on secondary N below +0.05 of primary lift "
            "while primary stays high -> the principle is N-specific not "
            "architectural; route to capacity-bound MEASURED_MECHANISM "
            "instead of DEFINITIVE.\n"
            "  - Upper-bound knob arm shows >>50% additional gain -> the "
            "v(N) PARTIAL was a knob-cranking artifact; demote v(N+1) "
            "to PARTIAL and re-prereg with hardened knob bound.\n"
            "  - Any per-seed paired lift fails chain-grade gate -> single "
            "seed failure flags to MIDDLE_BAND not DEFINITIVE.\n\n"
            "TIER: META rule (CERT-neutral, delta=0)."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE",
            "cert_status": "measured_mechanism",
            "cert_class": "discipline_meta",
            "verdict": (
                "META_CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION_"
                "minimal_upgrade_path_CHAIN_GRADE_PARTIAL_to_CHAIN_GRADE_"
                "DEFINITIVE_when_PARTIAL_rests_on_single_N_evidence_4_step_"
                "rule_expand_seed_pool_2plus_fresh_set_disjoint_add_cross_N_"
                "arm_different_capacity_verify_lifts_within_pm_0p02_BPC_"
                "similar_not_identical_rule_out_co_saturation_add_upper_"
                "bound_knob_probe_verify_plateau_composes_with_META_PROSPECTIVE_"
                "BANDS_FRESH_SEEDS_Cell_I_v4_and_META_M2_tight_rail_from_"
                "different_config_3_rule_cert_ladder_upgrade_path_discipline_"
                "set_validated_by_substrate_compose_freq_routing_v4_to_v5_"
                "first_dispatch_success_falsification_conditions_cross_N_"
                "identical_co_saturation_secondary_N_lift_below_primary_minus_"
                "0p05_capacity_bound_MM_upper_bound_arm_gt_50_pct_additional_"
                "gain_knob_cranking_artifact_any_per_seed_lift_fail_MIDDLE_BAND"
            ),
            "cell_commit": ATOMIZED_BY,
            "metrics_path": "META_RULE_no_metrics_path",
            "notes_path": NOTES_PATH_RULING,
            "verified_off_data": (
                "META rule derived from successful Cell 2 v4 -> v5 upgrade. "
                "Validation: v4 (CHAIN_GRADE_PARTIAL prose-only, single "
                "N=8192, 3 seeds [7, 17, 23], n_steps=2000) -> v5 (CHAIN_"
                "GRADE_DEFINITIVE: cross-N N=4096+N=8192, 5 seeds [7, 13, "
                "17, 23, 29], n_steps=2000+3000 upper-bound). All 4 rule "
                "components fired successfully: (a) +2 fresh seeds [13, "
                "29], (b) cross-N at N/2=4096, (c) lift delta 0.0042 BPC "
                "(within +/-0.02), (d) upper-bound n_steps=3000 plateau "
                "0.0037 BPC delta. Cert-ladder upgrade succeeded on first "
                "dispatch."
            ),
            "honest_scope": (
                "META rule. Codifies the cert-ladder DEFINITIVE-upgrade path "
                "for cases where a CHAIN_GRADE_PARTIAL referent rests on "
                "single-N evidence. Composes with 2 prior META rules from "
                "same-day rulings to form a 3-rule upgrade-path discipline "
                "set. Validated by Cell 2 v4 -> v5 succeeding on first "
                "dispatch. DOES NOT apply to: (a) PARTIAL referents already "
                "tested at multi-N (use a different upgrade lever -- cross-V "
                "OR cross-corpus instead), (b) MEASURED_MECHANISM referents "
                "that are by-construction-saturated (the upgrade question is "
                "different there). DOES NOT specify the exact tolerance for "
                "cross-N lift similarity (rule of thumb +/-0.02 BPC based on "
                "Cell 2 v5 success at 0.0042 BPC delta; cells with tighter "
                "noise floors should use proportionally tighter tolerance)."
            ),
            "rule_components": [
                "expand_seed_pool_by_2_fresh_set_disjoint",
                "add_cross_N_arm_at_different_capacity",
                "verify_lifts_within_pm_0p02_BPC_similar_not_identical",
                "add_upper_bound_knob_probe_verify_plateau",
            ],
            "composes_with": [
                "META_PROSPECTIVE_BANDS_FRESH_SEEDS_eliminates_retrofit_confound",
                "META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift",
            ],
            "discipline_set_size": 3,
            "discipline_set_name": "cert_ladder_upgrade_path_discipline_set",
            "validated_by_atom_id": "math::T3/EXP_substrate_compose_freq_routing_v5_DEFINITIVE",
            "first_dispatch_success": True,
            "falsification_conditions": [
                "cross_N_lifts_identical_to_3_decimals_co_saturation",
                "secondary_N_lift_below_primary_lift_minus_0p05_capacity_bound_MM",
                "upper_bound_knob_arm_shows_gt_50_pct_additional_gain_knob_cranking",
                "any_per_seed_paired_lift_fails_chain_grade_gate_MIDDLE_BAND",
            ],
            "cites": [
                "Cell_2_v4_to_v5_DEFINITIVE_upgrade_2026-06-25",
                "Cell_I_v4_DEFINITIVE_companion_ruling_same_day_2026-06-25",
                "META_PROSPECTIVE_BANDS_FRESH_SEEDS_atomized_2026-06-25_morning",
                "META_M2_tight_rail_from_different_config_atomized_2026-06-25",
                "Fix_28_default_under_claim_by_construction_saturation",
                "USER_results_to_application_cadence_same_cycle_atomize",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
        },
        aliases=[],
    )


# ============================================================================
# Main: A5-gated write
# ============================================================================

def main() -> int:
    store = PartitionedStore(STORE_ROOT)

    # ---- PRE snapshot ----
    pre_stats = store.stats()
    print("PRE-snapshot:")
    print(f"  total_atoms: {pre_stats.get('total_atoms')}")
    print(f"  total_relations: {pre_stats.get('total_relations')}")
    pre_parts = pre_stats.get('partitions', {})
    print(f"  math.n_atoms: {pre_parts.get('math',{}).get('n_atoms')}")
    print(f"  meta.n_atoms: {pre_parts.get('meta',{}).get('n_atoms')}")

    a1 = build_atom_v5_definitive()
    a2 = build_atom_meta_cross_N_rule()

    a1_qid = f"{a1.corpus.value}::{a1.id}"
    a2_qid = f"{a2.corpus.value}::{a2.id}"

    # ---- Collision check (idempotency) ----
    a1_exists = store.has_atom(a1_qid)
    a2_exists = store.has_atom(a2_qid)
    print(f"\nCollision check:")
    print(f"  {a1_qid}  exists={a1_exists}")
    print(f"  {a2_qid}  exists={a2_exists}")

    if a1_exists:
        print(f"ABORT: atom {a1_qid} already exists; refusing to overwrite. "
              "Manual review needed.")
        return 2
    if a2_exists:
        print(f"ABORT: atom {a2_qid} already exists; refusing to overwrite. "
              "Manual review needed.")
        return 2

    # ---- Write atoms (A5: PartitionedStore.add_atom does atomic tmp+replace) ----
    print(f"\nWriting atom 1: {a1_qid}")
    store.add_atom(a1)
    print(f"Writing atom 2: {a2_qid}")
    store.add_atom(a2)

    # ---- Verify-load round-trip ----
    store2 = PartitionedStore(STORE_ROOT)  # fresh load from disk
    a1_loaded = store2.get_atom(a1_qid)
    a2_loaded = store2.get_atom(a2_qid)
    if a1_loaded is None:
        print(f"FATAL: round-trip load failed for {a1_qid}")
        return 3
    if a2_loaded is None:
        print(f"FATAL: round-trip load failed for {a2_qid}")
        return 3
    if a1_loaded.metadata.get("cert_status") != "chain_grade":
        print(f"FATAL: cert_status mismatch on {a1_qid}: "
              f"got {a1_loaded.metadata.get('cert_status')}")
        return 3
    if a2_loaded.metadata.get("cert_status") != "measured_mechanism":
        print(f"FATAL: cert_status mismatch on {a2_qid}: "
              f"got {a2_loaded.metadata.get('cert_status')}")
        return 3
    print(f"\nRound-trip verification PASS:")
    print(f"  {a1_qid}  cert_status={a1_loaded.metadata.get('cert_status')}")
    print(f"  {a2_qid}  cert_status={a2_loaded.metadata.get('cert_status')}")

    # ---- POST snapshot ----
    post_stats = store2.stats()
    print(f"\nPOST-snapshot:")
    print(f"  total_atoms: {post_stats.get('total_atoms')}")
    print(f"  total_relations: {post_stats.get('total_relations')}")
    post_parts = post_stats.get('partitions', {})
    print(f"  math.n_atoms: {post_parts.get('math',{}).get('n_atoms')}  "
          f"(delta {post_parts.get('math',{}).get('n_atoms', 0) - pre_parts.get('math',{}).get('n_atoms', 0):+d})")
    print(f"  meta.n_atoms: {post_parts.get('meta',{}).get('n_atoms')}  "
          f"(delta {post_parts.get('meta',{}).get('n_atoms', 0) - pre_parts.get('meta',{}).get('n_atoms', 0):+d})")

    # ---- Cert ledger writes ----
    print(f"\nAppending cert_ledger rows...")

    # Row 1: chain_grade ruling for v5 DEFINITIVE
    row1 = build_chain_grade_ruling_row(
        atom_id=a1_qid,
        cell_commit="v5_DEFINITIVE",
        verdict=(
            "CHAIN_GRADE_DEFINITIVE_substrate_compose_freq_routing_v5_5seeds_"
            "N_DIM_8192_AND_N_DIM_4096_FREQ_DEEPER_N8192_bpc_7p1647_cv_0p0009_"
            "lift_plus_0p1477_FREQ_DEEPER_N4096_bpc_7p1712_cv_0p0009_lift_plus_"
            "0p1435_cross_N_lift_delta_0p0042_capacity_graded_not_co_saturating_"
            "n_steps_3000_plateau_v4_replicates_drift_0p0057_BASELINE_rail_drift_"
            "0p0059_all_5_per_seed_paired_lifts_above_0p10_gate_min_seed17_plus_"
            "0p1256_first_Stage_2_architectural_DEFINITIVE_atom_compose_lane_v4_"
            "atom_was_prose_only_fresh_write_no_supersede"
        ),
        notes_path=NOTES_PATH_RULING,
        metrics_path=METRICS_PATH_V5,
        cv=0.0009,
        cert_class="pre_reg_pass",
        atomized_by=ATOMIZED_BY,
        note=(
            "v5_DEFINITIVE_upgrade_of_v4_CHAIN_GRADE_PARTIAL_prose_only_never_"
            "written_to_Store_5_seeds_7_13_17_23_29_cross_N_8192_plus_4096_"
            "lifts_plus_0p1477_plus_0p1435_within_0p02_tolerance_capacity_"
            "graded_n_steps_3000_plateau_v4_number_replicates_BASELINE_rail_"
            "pass_5_of_5_per_seed_paired_lifts_pass_0p10_gate_discriminating_"
            "top1_high_freq_0p34_low_freq_0p002_first_Stage_2_DEFINITIVE_"
            "compose_lane_Director_ratified_in_thread_2026-06-25_composes_"
            "with_3_rule_cert_ladder_upgrade_path_discipline_set"
        ),
    )
    append_cert_ledger_row(row1)
    print(f"  Ledger row 1 (chain_grade) appended.")

    # Row 2: measured_mechanism / discipline_meta for META rule
    row2 = build_measured_mechanism_row(
        atom_id=a2_qid,
        cell_commit=ATOMIZED_BY,
        verdict=(
            "META_CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION_minimal_"
            "upgrade_path_PARTIAL_to_DEFINITIVE_when_PARTIAL_rests_on_single_N_"
            "4_step_rule_seed_expand_cross_N_lift_similarity_pm_0p02_upper_"
            "bound_knob_plateau_composes_with_META_PROSPECTIVE_BANDS_FRESH_SEEDS_"
            "and_META_M2_tight_rail_3_rule_cert_ladder_upgrade_path_discipline_"
            "set_validated_by_Cell_2_v4_to_v5_first_dispatch_success_2026-06-25"
        ),
        notes_path=NOTES_PATH_RULING,
        metrics_path="META_RULE_no_metrics_path",
        atomized_by=ATOMIZED_BY,
        note=(
            "META_CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION_CERT_"
            "neutral_discipline_atom_delta_0_validated_by_Cell_2_v4_to_v5_"
            "succeeded_on_first_dispatch_4_components_a_2plus_fresh_seeds_b_"
            "cross_N_arm_different_capacity_c_lifts_within_pm_0p02_BPC_not_"
            "identical_rules_out_co_saturation_d_upper_bound_knob_probe_"
            "plateau_composes_with_META_PROSPECTIVE_BANDS_FRESH_SEEDS_Cell_I_"
            "v4_and_META_M2_tight_rail_different_config_3_rule_cert_ladder_"
            "discipline_set_falsification_conditions_co_saturation_capacity_"
            "bound_knob_cranking_per_seed_failure_4_recommend_Director_side_"
            "pre_dispatch_checklist_codification"
        ),
    )
    append_cert_ledger_row(row2)
    print(f"  Ledger row 2 (meta_rule) appended.")

    # ---- Cert N delta ----
    print(f"\nExpected CERT N delta:")
    print(f"  +1 chain_grade (math::T3/EXP_substrate_compose_freq_routing_v5_DEFINITIVE)")
    print(f"  +0 meta_rule (meta::META/CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION)")
    print(f"  TOTAL: +1 (590 -> 591)")
    print(f"\ncert_ledger gains 2 rows.")
    print(f"\nA5 atomize COMPLETE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
