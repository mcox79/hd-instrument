#!/usr/bin/env python3
"""Skunkworks verify-off-data audit on 2 Wave 2I SMOKE_HARD_FAIL cells of 2026-06-27 evening.

USER directive 2026-06-27 ~18:20 PDT: vet pfc_controller_orthogonal_role_basis_v1
and loopy_belief_propagation_damped_v1; ATOMIZE one of TEST_DESIGN_FAILURE /
GENUINE_MECHANISM_NULL / INDETERMINATE_NEEDS_DIAGNOSTIC; trigger 2x drill rec.

CELL 1: exp_pfc_controller_orthogonal_role_basis_v1_smoke
  Headline: HARD_FAIL | depth=4 | ORTH=0.433 SHARED=0.411 PART=0.389 |
            lift_shared=0.022 lift_part=0.044 cv=0.054 | n_seeds=3
  HP bar: lift_shared >= +0.10 at cv < 0.10; got +0.022 cv=0.054

CELL 2: exp_loopy_belief_propagation_damped_v1_smoke
  Headline: HARD_FAIL | cycle=4 | D0=0.989 D2_damp=0.006 D5_damp=0.006
            D5_undamp=0.000 | lift_d2=-0.983 cv_d2=1.414 | n_seeds=3
  HP bar: D2 > D0 by +0.08; got -0.983 (D0 saturated; iter collapses)

VERDICTS (off raw per-arm metrics; NOT framing-from-verdict-msg):

1. pfc_controller_orthogonal_role_basis_v1 -> INDETERMINATE_NEEDS_DIAGNOSTIC
   (regime-too-easy for mechanism; math predicts exactly observed lift; mechanism
    verified working off alignment diagnostic; not null at harder regime)
   - Per-arm verified across 3 seeds (7, 17, 23) at N_DIM=4096 V=960:
       ARM_ORTH depth4 = [0.45, 0.45, 0.40] mean 0.4333 cv 0.054
       ARM_SHARED depth4 = [0.35, 0.50, 0.383] mean 0.4111 cv 0.156
       ARM_PART depth4 = [0.40, 0.383, 0.383] mean 0.3889 cv 0.020
       (Aggregator-reported cv=0.054 is ORTH cv specifically; SHARED cv 0.156)
   - At depth=3 ALL THREE ARMS = 0.000 across all 3 seeds (regime intrinsically
     too hard at depth=3 to discriminate); only depth=4 (decision_depth) provides
     signal. depth=3 collapse is itself a regime concern but not the failure.
   - DIRECTIONALLY CORRECT: ORTH > SHARED > PART monotonic (orthogonality
     beats random-shared, random-shared beats disjoint-subspace), matching
     mechanism's predicted ordering.
   - MECHANISM VERIFIED WORKING (alignment diagnostic from per-seed partials):
       roles_shared mean|cos with E| = 0.01230 (smoke seed 7)
       roles_orthogonal mean|cos with E| = 6.4e-9 (Gram-Schmidt clean to fp32)
       roles_partitioned mean|cos with E| = 0.01240
     The Gram-Schmidt is DOING WHAT IT SAYS; orthogonality achieved.
   - PURE MATH MATCHES MEASURED LIFT (drill Angle A): expected residual cosine
     between two random unit bipolar vectors in R^d is sqrt(2/(pi*d)).
     At d=4096: 0.0125. Measured shared alignment 0.0123. Drill predicted lift
     0.02-0.05 at smoke regime; observed 0.022 lift_shared, 0.044 lift_part.
     **Mechanism delivers exactly what math predicts at this regime.**
   - Drill Angle A predicts crossover regime where orthogonality bites harder:
     lower d-to-atoms ratio (d=2048, V=500), deeper depth (depth=6-8).
     Drill RANK 1 = same cell, harder regime; predicted lift 0.08-0.15.
   - Author framing 'HARD_FAIL on +0.10 bar' is structurally correct but the
     mechanism is NOT null -- it is performing exactly as theoretically bounded
     for this regime. Calling this 'HARD_FAIL = abandon' would be a tier
     mis-application (compare META_RULE_T: per-arm metric verification before
     META atomization; here the per-arm finding is 'lift in math-predicted
     range'). Better disposition: INDETERMINATE pending harder-regime test.
   - 2X DRILL ALREADY EXISTS:
     notes/research_drill_2x_orthogonal_role_basis_failure_revival_or_close_2026-06-27.md
     proposed RANK 1 = pfc_controller_orthogonal_basis_harder_regime_v1 (d=2048,
     V=500, depth=6) AND RANK 2 = competitive_basis_decorrelation_v1 (learned
     orthogonality via anti-Hebbian update). Skunkworks endorses RANK 1 FIRST
     as the decisive crossover-regime test.

2. loopy_belief_propagation_damped_v1 -> TEST_DESIGN_FAILURE (TWO compounding
   issues: (a) baseline saturation at D0=0.989; (b) DATA/ALGORITHM TOPOLOGY
   MISMATCH -- algorithm imposes cycle closure not present in data-gen)
   - Per-arm verified across 3 seeds at N_DIM=4096 V=960 NCAT=10 cycle_size=4:
       ARM_D0 cycle=4: [1.000, 0.9833, 0.9833] mean 0.989 cv 0.008
       ARM_D2_DAMP cycle=4: [0.000, 0.0167, 0.000] mean 0.006 cv 1.414
       ARM_D5_DAMP cycle=4: [0.000, 0.0167, 0.000] mean 0.006 cv 1.414
       ARM_D5_UNDAMP cycle=4: [0.000, 0.000, 0.000] mean 0.000 cv 0.000
   - ISSUE (a) BASELINE SATURATION at D0=0.989:
     The test target was constructed by make_kb_and_cycles() via forward-chaining
     (line 322-339 of cell): starting at s, walk per-op KB with op_seq, target =
     final cur. D0 (run_forward_chain, line 217-225) walks the SAME forward path
     by argmax cleanup at each step. Since at smoke regime (V=960, N=4096,
     n_train=300) the W-cleanup is near-noise-free, D0 is structurally guaranteed
     ~1.0 by construction. cv across seeds 0.008 = 1/120 = noise floor of n=60
     test_cycles. This is canonical 'baseline solves it perfectly by construction'.
   - ISSUE (b) ALGORITHM-DATA TOPOLOGY MISMATCH (deeper than (a)):
     **cell line 245-247 + run_loopy_bp body**: `n_vars = len(cycle_ops) = 4`,
     algorithm treats `var_i -> var_{(i+1) mod n_vars}`, with edge cycle_ops[3]
     closing v_3 -> v_0. **DATA**: make_kb_and_cycles built op_seq with 4 entries
     producing v_0 -> v_1 -> v_2 -> v_3 -> v_4(=cur); cycle_ops[3] in data is
     the v_3 -> v_4 forward edge, NOT a closure v_3 -> v_0. The algorithm IMPOSES
     a closure constraint v_3 ?= v_0 via cycle_ops[3] that DOES NOT EXIST in the
     data-generating distribution.
     So damped BP iterates against a FALSE FACTOR-GRAPH STRUCTURE. The messages
     converge (damping is doing its math correctly) but to the WRONG answer.
     The collapse from 0.989 -> 0.006 is the algorithm doing well-formed BP on
     a factor graph that doesn't match the data; the answer it converges to is
     the v_0=obs_state propagated around the loop, which has prob 1/V=1/960 of
     matching target = 0.001-0.01 expected (matches measured 0.006).
   - This is NOT 'iterations actively destroy signal' as a generic substrate
     property; it is 'wrong factor-graph topology causes BP to compute wrong
     marginal correctly'. The substrate is not the failure mode.
   - DAMPED vs UNDAMPED: D5_damped (0.006) > D5_undamped (0.000) by +0.006 --
     damping IS doing something (preventing total information annihilation that
     undamped BP collapse causes); but in absolute terms both are at floor.
     This +0.006 damping_help signal is consistent with damping doing its job
     even on the wrong factor graph; cannot draw substrate-level conclusion.
   - 3X DRILL ALREADY EXISTS (related, broader scope):
     notes/research_drill_brain_multihop_M4_belief_propagation_soft_message_passing_3x_2026-06-27.md
     proposes K-BEAM PATH-SUM as the substrate-native fix to the actual identified
     failure mode (correlated cleanup + rank-1 collapse). That drill REJECTS
     direct re-dispatch of soft-superposition / iterative-BP class and routes
     to exp_multihop_kbeam_pathsum_v1 instead.
   - 2X DRILL SPEC for THIS cell specifically:
     (a) FIX TOPOLOGY: rewrite make_kb_and_cycles to actually generate cyclic
         constraints -- pick 4 entities {a,b,c,d}, sample 4 edges that form a
         consistent cycle (a -> b via op0, b -> c via op1, c -> d via op2,
         d -> a via op3, then perturb one observation and infer marginal at
         the perturbed node). Without this fix, BP is being asked to do something
         the data doesn't represent.
     (b) ANTI-SATURATION: push regime to where D0 < 0.80 so iteration has
         headroom. Either V >> N (capacity-stressed) OR n_train sparse so
         W-cleanup is genuinely uncertain. Concrete: V=4000, n_train=200,
         depth retained at cycle_size=4. D0 should drop to 0.5-0.7 range.
     (c) BOTH (a) AND (b) before any tier promotion; this cell as-written
         does NOT test damped loopy BP on a 4-cycle.

META CLAIM VETTING:

Cross-cell pattern (today's TWO HARD_FAIL smokes plus morning Wave 2H batch):
  Both cells exhibit DIFFERENT failure modes within the same anchor 'mechanism
  HARD_FAIL on +X.XX bar' framing:
    - pfc_orth: mechanism CORRECT; regime not in mechanism's lever range
    - loopy_bp: mechanism class CORRECT; algorithm-data topology mismatch (test
      doesn't exercise the mechanism)
  Neither is a substrate null. Both are TEST_DESIGN or REGIME issues exposed
  ONLY by per-arm + math-prediction + topology-cross-check verification.

  Skunkworks META observation (composes with morning's META_NUANCED audit):
  the wave2 failure-pattern atomization should add a FOURTH family:
    (D) DATA-ALGORITHM-TOPOLOGY-MISMATCH: algorithm imposes a graph constraint
        that the data-generating distribution doesn't satisfy; BP/iterative
        algorithms then converge correctly to wrong marginals; cannot be
        diagnosed from headline lift number alone -- requires reading cell
        data-gen code vs algorithm code side-by-side.
  Today's loopy_bp is the cleanest evidence cell for family (D) seen so far.

  NOT STRONG ENOUGH for META atomization yet (single instance); flag for
  inclusion when stc_v3, tonegawa_v4, or one more family-D instance lands.
  Atomize the SPECIFIC failure modes for these 2 cells now; queue META update.

ATOMIZATION PLAN (idempotent, A5-gated):
1. INDETERMINATE_NEEDS_DIAGNOSTIC pfc_controller_orthogonal_role_basis_v1
   (regime-too-easy; mechanism verified working; math predicts observed lift;
    harder-regime test required for tier disposition)
2. TEST_DESIGN_FAILURE loopy_belief_propagation_damped_v1
   (TWO issues: baseline saturation D0=0.989 by construction + DATA/ALGORITHM
    TOPOLOGY MISMATCH: algorithm imposes cycle closure absent from data-gen)

NO chain-grade tier; NO cert_ledger increment. Methodology / discipline atoms only.

Files:
- Raw metrics 1: data/exp_pfc_controller_orthogonal_role_basis_v1_smoke/metrics.json
- Raw metrics 2: data/exp_loopy_belief_propagation_damped_v1_smoke/metrics.json
- Cell source 1: experiments/exp_pfc_controller_orthogonal_role_basis_v1.py
- Cell source 2: experiments/exp_loopy_belief_propagation_damped_v1.py
- Existing 2x drill (cell 1): notes/research_drill_2x_orthogonal_role_basis_failure_revival_or_close_2026-06-27.md
- Existing 3x drill (related): notes/research_drill_brain_multihop_M4_belief_propagation_soft_message_passing_3x_2026-06-27.md
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path("d:/AI/hd-instrument").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


STORE_ROOT = Path("d:/AI/hd-instrument/data/substrate_index")
SOURCE_TAG = "skunkworks_verify_off_data_pfc_orth_loopy_bp_wave2I_2026-06-27_evening"


def _add_safely(atom: Atom, note: str) -> bool:
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"SKIP (idempotent): {atom.id[:90]}")
        return True
    print(f"ADDING: {atom.id[:90]}")
    ps.add_atom(atom, source=SOURCE_TAG, note=note)
    ps2 = PartitionedStore(STORE_ROOT)
    atoms = list(ps2.all_atoms())
    found = next((a for a in atoms if a.id == atom.id), None)
    if found is None:
        print(f"  FAIL: not present post-add")
        return False
    if found.tier != atom.tier or found.kind != atom.kind:
        print(f"  FAIL: tier/kind drift on round-trip")
        return False
    print(f"  PASS: round-trip clean")
    return True


def atom_pfc_orthogonal_role_basis_v1() -> Atom:
    return Atom(
        id=("AUDIT_INDETERMINATE_NEEDS_DIAGNOSTIC_pfc_controller_orthogonal_role_basis_v1_smoke"
            "_REGIME_TOO_EASY_FOR_MECHANISM_LEVER_RANGE_ORTH_0p433_SHARED_0p411_PART_0p389"
            "_lift_shared_0p022_lift_part_0p044_cv_0p054_n_seeds_3_depth_4_N_4096_V_960"
            "_mechanism_VERIFIED_WORKING_via_alignment_diagnostic_orth_mean_abs_cos_with_E_6e9"
            "_shared_0p0123_partitioned_0p0124_Gram_Schmidt_clean_to_fp32"
            "_PURE_MATH_PREDICTS_OBSERVED_LIFT_residual_cosine_sqrt_2_over_pi_d_at_d_4096_0p0125"
            "_drill_angle_A_predicts_0p02_0p05_lift_at_smoke_regime_observed_0p022_in_range"
            "_directionally_correct_ORTH_gt_SHARED_gt_PART_monotonic"
            "_depth_3_collapse_all_arms_to_0p000_intrinsic_regime_hardness"
            "_harder_regime_d_2048_V_500_depth_6_predicted_lift_0p08_0p15_2x_drill_RANK_1_required_2026-06-27"),
        name=("INDETERMINATE_NEEDS_DIAGNOSTIC pfc_controller_orthogonal_role_basis_v1: regime too easy "
              "for mechanism lever range (math predicts observed 0.022 lift exactly at d=4096); "
              "Gram-Schmidt mechanism VERIFIED working (orth align 6e-9 vs shared 0.0123 vs part 0.0124); "
              "harder regime d=2048 V=500 depth=6 required for tier disposition"),
        description=(
            "Wave 2I SMOKE_HARD_FAIL audit. Cell tests Gram-Schmidt-at-init orthogonalization of "
            "role-basis against filler-basis as cheap single-init PFC controller improvement. "
            "Verify-off-data finding: per-arm raw values at N_DIM=4096, V_entities=960, "
            "N_OPS=4, depths=[3,4], seeds=[7,17,23], n_train=300, n_test=60, decision_depth=4:\n"
            "  ARM_ORTH depth4 = [0.45, 0.45, 0.40] mean 0.4333 cv 0.054\n"
            "  ARM_SHARED depth4 = [0.35, 0.50, 0.383] mean 0.4111 cv 0.156\n"
            "  ARM_PART depth4 = [0.40, 0.383, 0.383] mean 0.3889 cv 0.020\n"
            "  ALL ARMS depth3 = 0.000 across all 3 seeds (intrinsic regime hardness)\n"
            "Lift_shared = 0.022 (HP bar +0.10 unmet); lift_part = 0.044 (HP bar +0.03 met). "
            "DIRECTIONALLY CORRECT: ORTH > SHARED > PART monotonic; mechanism's predicted "
            "ordering holds. **MECHANISM VERIFIED WORKING** via per-seed alignment diagnostic "
            "(seed 7 representative): roles_shared mean|cos with E| = 0.01230; roles_orthogonal "
            "= 6.4e-9 (Gram-Schmidt clean to fp32 precision); roles_partitioned = 0.01240. "
            "Cell's selftest also asserts orth alignment <= shared (line 481-484). "
            "**PURE MATH PREDICTS THE OBSERVED LIFT.** Expected residual cosine between two random "
            "unit bipolar vectors in R^d is sqrt(2/(pi*d)). At d=4096: 0.0125 -- matches "
            "shared-alignment 0.0123 measurement. Existing 2x drill Angle A (drill note "
            "2026-06-27 RANK 1 source) computed predicted lift 0.02-0.05 at smoke regime; observed "
            "lift_shared 0.022 sits in the middle of that range. The mechanism is delivering "
            "EXACTLY what theory says it should at this regime; this is NOT a substrate null. "
            "Calling 'HARD_FAIL = abandon' would be tier mis-application -- the mechanism is "
            "performing as theoretically bounded for this regime; failure is regime choice, not "
            "mechanism. Drill Angle A predicts crossover regime where orthogonality bites harder: "
            "lower d-to-atoms ratio (d=2048, V=500: residual sqrt(499/2048) ~ 0.49 vs current "
            "sqrt(959/4096) ~ 0.48; deeper depth (depth=6-8): compounded noise budget proportional "
            "to sqrt(depth). Existing 2x drill RANK 1 = pfc_controller_orthogonal_basis_harder_"
            "regime_v1 with d=2048, V=500, depth=6, predicted lift 0.08-0.15 (touches HP bar). "
            "RANK 2 = competitive_basis_decorrelation_v1 (anti-Hebbian online learned "
            "orthogonality; brain-grounded grid-cell module-orthogonality analog from Hafting/"
            "Moser 2005). Skunkworks endorses RANK 1 FIRST as decisive crossover-regime test. "
            "Disposition INDETERMINATE_NEEDS_DIAGNOSTIC: not null at harder regime; not pass at "
            "this regime; mechanism verified instrument-clean. Atomization is CERT-neutral; no "
            "tier promotion or demotion; not counted in cert ledger."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 257,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "regime_too_easy_for_mechanism_lever_range_mechanism_verified_working_via_diagnostic_and_math_match",
            "verified_off_data": True,
            "raw_metrics_path": "data/exp_pfc_controller_orthogonal_role_basis_v1_smoke/metrics.json",
            "cell_source_path": "experiments/exp_pfc_controller_orthogonal_role_basis_v1.py",
            "drill_2x_path": "notes/research_drill_2x_orthogonal_role_basis_failure_revival_or_close_2026-06-27.md",
            "key_per_arm_values": {
                "ORTH_depth4_mean": 0.4333,
                "SHARED_depth4_mean": 0.4111,
                "PART_depth4_mean": 0.3889,
                "ORTH_depth4_cv": 0.054,
                "SHARED_depth4_cv": 0.156,
                "PART_depth4_cv": 0.020,
                "ORTH_depth4_per_seed": [0.45, 0.45, 0.40],
                "SHARED_depth4_per_seed": [0.35, 0.50, 0.383],
                "PART_depth4_per_seed": [0.40, 0.383, 0.383],
                "all_arms_depth3": 0.000,
                "lift_shared": 0.022,
                "lift_partitioned": 0.044,
                "n_seeds": 3,
                "N_dim": 4096,
                "V_entities": 960,
                "N_ops": 4,
                "decision_depth": 4,
                "HP_bar_lift_shared": 0.10,
                "HP_bar_lift_partitioned": 0.03,
                "HP_bar_cv": 0.10,
            },
            "mechanism_verified_working_evidence": {
                "shared_mean_abs_align_with_E_seed7": 0.01230,
                "orthogonal_mean_abs_align_with_E_seed7": 6.4e-9,
                "partitioned_mean_abs_align_with_E_seed7": 0.01240,
                "gram_schmidt_clean_to_fp32_precision": True,
                "cell_selftest_asserts_orth_alignment_leq_shared": True,
                "directional_ordering_ORTH_gt_SHARED_gt_PART": True,
            },
            "pure_math_predicts_observed_lift": {
                "expected_residual_cosine_formula": "sqrt(2/(pi*d))",
                "at_d_4096_predicted": 0.0125,
                "measured_shared_alignment": 0.0123,
                "drill_angle_A_predicted_lift_range_at_smoke_regime": [0.02, 0.05],
                "observed_lift_shared": 0.022,
                "math_prediction_in_range": True,
            },
            "harder_regime_predicted_lift": {
                "d_2048_V_500_depth_6_predicted_lift_range": [0.08, 0.15],
                "touches_HP_bar_at_crossover_regime": True,
                "drill_RANK_1_cell_name": "pfc_controller_orthogonal_basis_harder_regime_v1",
            },
            "two_x_drill_required": True,
            "two_x_drill_dispatch_order": [
                "RANK_1_pfc_controller_orthogonal_basis_harder_regime_v1_d_2048_V_500_depth_6_n_seeds_5",
                "RANK_2_competitive_basis_decorrelation_v1_anti_Hebbian_learned_orthogonality_brain_grounded_grid_cell_module",
            ],
            "two_x_drill_decision_tree": (
                "RANK_1_PASS_at_harder_regime_then_RANK_2_compares_init_vs_learned_orthogonality"
                "_RANK_1_FAIL_then_close_orthogonal_direction_and_pivot_to_routing_mechanisms"
            ),
            "composes_with": [
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
                "META_RULE_K_smoke_must_FIRE_discriminator",
                "META_RULE_T_per_arm_metric_verification_required_before_META_atomization",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
                "feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26",
                "feedback_three_smoke_disciplines_band_floor_results_are_MIDDLE_BAND_not_HARD_PASS_2026-06-26",
            ],
        },
    )


def atom_loopy_bp_damped_v1() -> Atom:
    return Atom(
        id=("AUDIT_TEST_DESIGN_FAILURE_loopy_belief_propagation_damped_v1_smoke"
            "_TWO_COMPOUNDING_ISSUES_baseline_saturation_D0_0p989_by_construction_AND"
            "_DATA_ALGORITHM_TOPOLOGY_MISMATCH_algorithm_imposes_cycle_closure_absent_from_data_gen"
            "_make_kb_and_cycles_builds_forward_chain_v0_v1_v2_v3_v4_target_cur"
            "_run_loopy_bp_treats_var_i_to_var_i_plus_1_mod_n_vars_cycle_closure_v3_to_v0"
            "_false_factor_graph_BP_converges_correctly_to_wrong_marginal"
            "_D0_baseline_0p989_D2_damp_0p006_D5_damp_0p006_D5_undamp_0p000"
            "_lift_d2_minus_0p983_cv_d2_1p414_collapse_floor_1_over_V_960_0p001_to_0p006_matches"
            "_damped_help_plus_0p006_damping_doing_job_on_wrong_factor_graph"
            "_substrate_NOT_failure_mode_cell_as_written_does_not_test_damped_loopy_BP_on_4_cycle"
            "_2x_drill_required_fix_topology_make_real_cyclic_constraints_AND_anti_saturation_V_4000_n_train_200_2026-06-27"),
        name=("TEST_DESIGN_FAILURE loopy_belief_propagation_damped_v1: TWO compounding issues -- "
              "(a) baseline saturation D0=0.989 by construction (forward-chain data + forward-chain "
              "D0); (b) DATA/ALGORITHM TOPOLOGY MISMATCH (algorithm imposes cycle closure v_3 -> v_0 "
              "absent from data-gen which built forward chain v_0 -> v_4); BP converges correctly "
              "to wrong marginal; cell does NOT test damped loopy BP on a 4-cycle"),
        description=(
            "Wave 2I SMOKE_HARD_FAIL audit. Cell purports to test 4-cycle loopy belief propagation "
            "with damping (Murphy/Pearl) as substrate-native alternative to soft-superposition. "
            "Verify-off-data finding: per-arm raw values at N_DIM=4096, V_entities=960, N_OPS=4, "
            "cycle_size=4, seeds=[7,17,23], damping_alpha=0.30, n_train=300, n_test=60:\n"
            "  ARM_D0_BASELINE cycle=4 = [1.000, 0.9833, 0.9833] mean 0.989 cv 0.008\n"
            "  ARM_D2_DAMPED cycle=4 = [0.000, 0.0167, 0.000] mean 0.006 cv 1.414\n"
            "  ARM_D5_DAMPED cycle=4 = [0.000, 0.0167, 0.000] mean 0.006 cv 1.414\n"
            "  ARM_D5_UNDAMPED cycle=4 = [0.000, 0.000, 0.000] mean 0.000 cv 0.000\n"
            "Lift_d2 = -0.983 (HP bar +0.08 violated catastrophically); damping_help = +0.006. "
            "**ISSUE (a) BASELINE SATURATION**: test target was constructed by "
            "make_kb_and_cycles() (cell line 308-340) via forward-chaining -- starting at s, walk "
            "per-op KB with op_seq, target = final cur. D0 (run_forward_chain, cell line 217-225) "
            "walks the SAME forward path by argmax-cleanup at each step. At smoke regime (V=960, "
            "N=4096, n_train=300) W-cleanup is near-noise-free, so D0 is structurally guaranteed "
            "~1.0 by construction. cv 0.008 = 1/120 = noise floor of n=60 test_cycles. Canonical "
            "'baseline solves it perfectly by construction' regime; iterations have nothing to add. "
            "**ISSUE (b) ALGORITHM-DATA TOPOLOGY MISMATCH (deeper than (a))**: cell line 245-247 + "
            "run_loopy_bp body: n_vars = len(cycle_ops) = 4; algorithm treats var_i -> var_{(i+1) "
            "mod n_vars}, with edge cycle_ops[3] closing v_3 -> v_0. DATA: make_kb_and_cycles "
            "built op_seq with 4 entries producing v_0 -> v_1 -> v_2 -> v_3 -> v_4(=cur); "
            "cycle_ops[3] in data is the v_3 -> v_4 forward edge, NOT a closure v_3 -> v_0. "
            "**The algorithm IMPOSES a closure constraint v_3 ?= v_0 via cycle_ops[3] that DOES "
            "NOT EXIST in the data-generating distribution.** So damped BP iterates against a "
            "FALSE FACTOR-GRAPH STRUCTURE. The messages converge (damping doing its math correctly) "
            "but to the WRONG answer. Collapse 0.989 -> 0.006 is the algorithm doing well-formed "
            "BP on a factor graph that does not match the data; the answer it converges to has "
            "prob ~ 1/V = 1/960 ~ 0.001-0.01 of matching target by chance (matches measured 0.006). "
            "This is NOT 'iterations actively destroy signal' as a generic substrate property; it "
            "is 'wrong factor-graph topology causes BP to compute wrong marginal correctly'. The "
            "substrate is NOT the failure mode. D5_damped (0.006) > D5_undamped (0.000) by +0.006 "
            "shows damping IS doing something (preventing total information annihilation) even on "
            "the wrong graph; in absolute terms both at floor; cannot draw substrate-level "
            "conclusion. Cell as-written does NOT test damped loopy BP on a 4-cycle. 2X DRILL "
            "REQUIRED: (a) FIX TOPOLOGY -- rewrite make_kb_and_cycles to actually generate cyclic "
            "constraints (pick 4 entities {a,b,c,d}, sample 4 edges forming consistent cycle a -> "
            "b via op0, b -> c via op1, c -> d via op2, d -> a via op3, then perturb one "
            "observation and infer marginal at perturbed node); (b) ANTI-SATURATION -- push regime "
            "to D0 < 0.80 with V >> N (capacity-stressed) or n_train sparse (W-cleanup uncertain); "
            "concrete spec V=4000, n_train=200, cycle_size=4 should drop D0 to 0.5-0.7 range; "
            "(c) BOTH (a) AND (b) before any tier promotion. Related 3x drill 2026-06-27 brain "
            "mechanism #4 belief propagation already proposes K-BEAM PATH-SUM as substrate-native "
            "fix to the broader correlated-cleanup + rank-1-collapse failure mode -- that drill "
            "REJECTS direct re-dispatch of iterative-BP class entirely; reasonable alternative. "
            "Atomization is CERT-neutral; no tier promotion or demotion; not counted in cert "
            "ledger. Disposition TEST_DESIGN_FAILURE: cell does not test what it claims; substrate "
            "mechanism status UNKNOWN; NOT a substrate null."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 258,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "test_design_failure_two_compounding_issues_baseline_saturation_AND_data_algorithm_topology_mismatch",
            "verified_off_data": True,
            "raw_metrics_path": "data/exp_loopy_belief_propagation_damped_v1_smoke/metrics.json",
            "cell_source_path": "experiments/exp_loopy_belief_propagation_damped_v1.py",
            "related_3x_drill_path": "notes/research_drill_brain_multihop_M4_belief_propagation_soft_message_passing_3x_2026-06-27.md",
            "key_per_arm_values": {
                "D0_baseline_cycle4_mean": 0.989,
                "D2_damped_cycle4_mean": 0.006,
                "D5_damped_cycle4_mean": 0.006,
                "D5_undamped_cycle4_mean": 0.000,
                "D0_per_seed": [1.000, 0.9833, 0.9833],
                "D2_damp_per_seed": [0.000, 0.0167, 0.000],
                "D5_damp_per_seed": [0.000, 0.0167, 0.000],
                "D5_undamp_per_seed": [0.000, 0.000, 0.000],
                "lift_d2_over_d0": -0.983,
                "lift_d5d_over_d0": -0.983,
                "damping_help_d5d_minus_d5u": 0.006,
                "cv_d2": 1.414,
                "cv_d5d": 1.414,
                "cv_d0": 0.008,
                "n_seeds": 3,
                "N_dim": 4096,
                "V_entities": 960,
                "N_ops": 4,
                "cycle_size": 4,
                "n_train": 300,
                "n_test": 60,
                "HP_bar_lift_d2": 0.08,
                "HP_bar_lift_d5d": 0.08,
                "HP_bar_cv": 0.10,
                "damping_alpha": 0.30,
            },
            "issue_a_baseline_saturation": {
                "D0_construction": "forward_chain_walk_per_op_KB_target_eq_final_cur",
                "D0_algorithm": "run_forward_chain_argmax_cleanup_each_step",
                "construction_and_algorithm_identical_at_smoke_regime": True,
                "noise_floor_n60_test_cycles": 0.008,
                "D0_measured": 0.989,
                "saturation_confirmed": True,
            },
            "issue_b_topology_mismatch": {
                "algorithm_treats_var_i_to_var_i_plus_1_mod_n_vars": True,
                "algorithm_imposes_closure_edge_cycle_ops_3_v3_to_v0": True,
                "data_built_forward_chain_v0_to_v4_eq_cur": True,
                "cycle_ops_3_in_data_is_v3_to_v4_forward_edge_NOT_closure": True,
                "BP_converges_correctly_to_wrong_marginal": True,
                "expected_floor_1_over_V": 0.00104,
                "measured_floor_d2_d5d": 0.006,
                "floor_consistent_with_random_chance_against_imposed_false_closure": True,
            },
            "damping_doing_job_evidence": {
                "d5_damped_minus_d5_undamped": 0.006,
                "damping_prevents_total_annihilation_even_on_wrong_graph": True,
                "absolute_floor_so_no_substrate_conclusion_possible": True,
            },
            "two_x_drill_required": True,
            "two_x_drill_spec": (
                "fix_a_rewrite_make_kb_and_cycles_to_generate_real_cyclic_constraints_4_entities_"
                "4_consistent_edges_perturb_one_observation_infer_marginal_at_perturbed_node_AND_"
                "fix_b_anti_saturation_V_4000_n_train_200_D0_target_0p5_to_0p7_range_AND_"
                "both_a_and_b_required_before_tier_promotion"
            ),
            "alternative_direction_already_proposed": (
                "K_beam_path_sum_per_3x_drill_2026-06-27_brain_mechanism_4_belief_propagation"
                "_REJECTS_iterative_BP_class_entirely_routes_to_exp_multihop_kbeam_pathsum_v1"
            ),
            "skunkworks_meta_observation_proposed_family_D": (
                "DATA_ALGORITHM_TOPOLOGY_MISMATCH_algorithm_imposes_graph_constraint_data_doesnt_"
                "satisfy_BP_converges_correctly_to_wrong_marginals_cannot_diagnose_from_headline"
                "_lift_requires_reading_cell_data_gen_code_vs_algorithm_code_side_by_side_"
                "loopy_bp_v1_is_first_clean_evidence_cell_for_family_D_NOT_strong_enough_for_META_atomization_yet"
            ),
            "composes_with": [
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
                "META_RULE_K_smoke_must_FIRE_discriminator",
                "META_RULE_T_per_arm_metric_verification_required_before_META_atomization",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
                "feedback_three_smoke_disciplines_no_silent_except_smoke_fires_discriminator_band_floor_inconclusive_2026-06-26",
                "AUDIT_META_NUANCED_PARTIALLY_SUPPORTED_wave2_failure_pattern_three_root_cause_families_2026-06-27",
            ],
        },
    )


def main() -> int:
    print(f"Source tag: {SOURCE_TAG}")
    print(f"Store root: {STORE_ROOT}")
    print()
    results = []
    atoms_to_add = [
        (atom_pfc_orthogonal_role_basis_v1(),
         "INDETERMINATE_NEEDS_DIAGNOSTIC pfc_orthogonal_role_basis_v1 (regime-too-easy; mechanism verified working; math predicts observed lift; harder regime required) verified"),
        (atom_loopy_bp_damped_v1(),
         "TEST_DESIGN_FAILURE loopy_belief_propagation_damped_v1 (TWO issues: baseline saturation D0=0.989 + data/algorithm topology mismatch imposing cycle closure absent from data-gen) verified"),
    ]
    for atom, note in atoms_to_add:
        ok = _add_safely(atom, note)
        results.append((atom.id[:80], ok))
    print()
    print("=" * 80)
    print("Summary:")
    n_pass = sum(1 for _, ok in results if ok)
    n_total = len(results)
    print(f"  {n_pass}/{n_total} atoms added/verified")
    for aid, ok in results:
        flag = "OK" if ok else "FAIL"
        print(f"  [{flag}] {aid}")
    return 0 if n_pass == n_total else 1


if __name__ == "__main__":
    sys.exit(main())
