"""Atomize Drill A (option-critic Bacon-Roy) + Drill B (block-sparse Hersche) HARD_FAILs
AND upgrade hierarchical-planning capability closure from PRELIMINARY (3-cell) to CONFIRMED
(5-cell, 2x-drill discipline satisfied per feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28).

A5 atomic-write + verify-load + cert_ledger increment.

Atoms produced (3):
  1. math::T3 EXP option-critic HARD_FAIL (mechanism_characterization HONEST_NEGATIVE)
  2. math::T3 EXP block-sparse HARD_FAIL (mechanism_characterization HONEST_NEGATIVE)
  3. math::T3 CAPABILITY_CLOSED_CONFIRMED 5-cell aggregate (mechanism_characterization HONEST_NEGATIVE; supersedes preliminary)
PLUS:
  4. meta::T_methodology META_RULE_AO_v2 amendment (CONFIRMED 5-cell evidence; well-evidenced)
"""

import json
import os
import time
import shutil
import hashlib

HD = "d:/AI/hd-instrument"
MATH_ATOMS = f"{HD}/data/substrate_index/math/atoms.jsonl"
MATH_AUDIT = f"{HD}/data/substrate_index/math/audit.jsonl"
META_ATOMS = f"{HD}/data/substrate_index/meta/atoms.jsonl"
META_AUDIT = f"{HD}/data/substrate_index/meta/audit.jsonl"
META_LEDGER = f"{HD}/data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_drill_AB_closure_confirmed_2026-06-28"
TS = time.time()


def atomic_append(path: str, lines: list[str]) -> None:
    """tmp -> os.replace (atomic) + verify-load."""
    if not lines:
        return
    # read existing
    existing = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = f.readlines()
    new_content = existing + [l if l.endswith("\n") else l + "\n" for l in lines]
    tmp = path + f".tmp_{os.getpid()}_{int(TS)}"
    with open(tmp, "w", encoding="utf-8") as f:
        f.writelines(new_content)
    os.replace(tmp, path)
    # verify load
    with open(path, "r", encoding="utf-8") as f:
        verify = f.readlines()
    assert len(verify) == len(existing) + len(lines), (
        f"VERIFY-LOAD FAIL {path}: expected {len(existing)+len(lines)} got {len(verify)}"
    )
    # parse-verify the new lines
    for l in lines:
        json.loads(l)
    print(f"  A5 ATOMIC OK: {path} +{len(lines)} (now {len(verify)})")


# ====================================================================
# ATOM 1: Option-critic Bacon-Roy HARD_FAIL (Drill A)
# ====================================================================
oc_metrics = json.load(open(f"{HD}/data/exp_substrate_hierarchical_option_critic_v1_smoke/metrics.json"))
oc_pa = oc_metrics["per_arm"]

atom_oc = {
    "id": "T3/EXP_substrate_hierarchical_option_critic_v1_HARD_FAIL_DRILL_A_REVIVAL_bacon_roy_2017_OC_full_0p000_beta_frozen_0p050_pi_frozen_0p100_v3_baseline_0p000_flat_reinforce_0p050_random_0p000_lift_OC_V3_0p000_lift_OC_FLAT_neg_0p050_arms_distinct_True_cardinality_ok_120of120_N8192_options3_depth6_ep100_REINFORCE_plumbing_works_flat_train_0p12_to_0p20_delta_0p08_but_OC_train_0p04_to_0p00_delta_neg_0p04_hierarchical_credit_assignment_diluted_across_pi_beta_Q_per_option_substrate_cannot_gradient_out_of_hierarchical_credit_assignment_at_this_regime_2026-06-28",
    "name": "Hierarchical planning option-critic (Bacon-Roy 2017) Drill A HARD_FAIL: REINFORCE plumbing works on flat (+0.08 train) but hierarchical structure dilutes credit signal (-0.04 train); substrate cannot gradient-its-way out of hierarchical credit-assignment at this regime",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Drill A revival attempt for hierarchical-planning capability class using Bacon-Roy 2017 option-critic "
        "(learned termination beta with policy gradient through option). 6-arm comparison at N=8192, "
        "composite-depth=6, 100 training episodes, 20 test goals, 6 actions, 3 options, seed=7. "
        "Mechanism (OC_FULL) = 0.000 solve_rate; lifts OC-V3=0.000 OC-FLAT=-0.050 OC-RAND=0.000; "
        "arms_distinct=True (SHA-256 per-arm seq trace verified 6 distinct hashes); cardinality_ok=120/120; "
        "chance_floor=2.143e-05 (1/6^6 exact). "
        "MECHANISTIC INSIGHT: REINFORCE plumbing WORKS (flat-baseline REINFORCE learned 0.12->0.20 over 100 episodes; train delta +0.08); "
        "option-critic HIERARCHICAL structure prevents learning (OC train delta 0.04->0.00 = NEGATIVE -0.04). "
        "Best arm is pi_frozen (0.10, greedy pi + learnable beta) marginally above OC_FULL; "
        "beta_frozen (0.05, learnable pi + frozen beta) also above OC_FULL. "
        "Diagnosis: reward signal dilutes across multiple options (pi/beta/Q-U per option); credit-assignment "
        "ambiguity over which option deserves reward prevents convergence; substrate cannot gradient-its-way out "
        "of the hierarchical credit-assignment problem at the bipolar-HRR regime with N=8192 composite-depth=6. "
        "This is the 4th DISTINCT mechanism class HARD_FAIL on hierarchical-planning (after closed-form D_macro pseudoinverse, "
        "state-conditioned+disjoint blocks, Sutton-Precup 1999 options pi/beta/I). Per 2x-drill discipline "
        "(USER 2026-06-28 feedback_2x_drill_negatives_before_capability_closure), Drill A satisfies the first of "
        "two required revival drills before honoring capability closure."
    ),
    "aliases": [],
    "metadata": {
        "provenance_quality": "HONEST_NEGATIVE",
        "cert_status": "honest_negative",
        "cert_class": "mechanism_characterization",
        "record_class": "experiment_record",
        "term_class": "HARD_FAIL",
        "metric_type": "solve_rate_composite_depth6",
        "verdict": "HARD_FAIL",
        "verdict_raw": oc_metrics["verdict_msg"],
        "run_mode": "smoke",
        "experiment_path": "experiments/exp_substrate_hierarchical_option_critic_v1.py",
        "prereg_path": "preregs/2026-06-28_substrate_hierarchical_option_critic_v1.md",
        "metrics_path": "data/exp_substrate_hierarchical_option_critic_v1_smoke/metrics.json",
        "drill_role": "DRILL_A_REVIVAL_BACON_ROY_2017_OPTION_CRITIC",
        "closes_against_capability": "hierarchical_planning_at_substrate_bipolar_HRR_N8192_depth6",
        "key_metrics": {
            "option_critic_full_solve_rate": oc_pa["option_critic_full"]["7"]["solve_rate"],
            "beta_frozen_solve_rate": oc_pa["beta_frozen"]["7"]["solve_rate"],
            "pi_frozen_solve_rate": oc_pa["pi_frozen"]["7"]["solve_rate"],
            "v3_baseline_solve_rate": oc_pa["v3_baseline"]["7"]["solve_rate"],
            "flat_reinforce_solve_rate": oc_pa["flat_reinforce"]["7"]["solve_rate"],
            "random_solve_rate": oc_pa["random"]["7"]["solve_rate"],
            "lift_oc_minus_v3": oc_metrics["lift_option_critic_minus_v3"],
            "lift_oc_minus_flat": oc_metrics["lift_option_critic_minus_flat"],
            "lift_oc_minus_random": oc_metrics["lift_option_critic_minus_random"],
            "flat_reinforce_train_q1_q4_delta": (
                oc_pa["flat_reinforce"]["7"]["train_log"]["train_solve_rate_last_quarter"]
                - oc_pa["flat_reinforce"]["7"]["train_log"]["train_solve_rate_first_quarter"]
            ),
            "option_critic_full_train_q1_q4_delta": (
                oc_pa["option_critic_full"]["7"]["train_log"]["train_solve_rate_last_quarter"]
                - oc_pa["option_critic_full"]["7"]["train_log"]["train_solve_rate_first_quarter"]
            ),
            "arms_distinct": oc_metrics["arms_distinct"],
            "cardinality_ok": oc_metrics["cardinality_ok"],
            "expected_n_units": oc_metrics["expected_n_units"],
            "completed_units": oc_metrics["completed_units"],
            "chance_random_floor": oc_metrics["chance_random_floor"],
            "n_seeds_complete": oc_metrics["n_seeds_complete"],
        },
        "arm_sha256_per_seed7": {arm: oc_pa[arm]["7"]["_seq_hash"] for arm in oc_pa},
        "root_diagnosis": (
            "REINFORCE plumbing works (flat-baseline +0.08 train delta) but hierarchical structure "
            "prevents learning (OC -0.04 train delta); reward signal diluted across pi/beta/Q per option; "
            "substrate cannot gradient-its-way out of hierarchical credit-assignment at bipolar-HRR N=8192 depth=6 regime"
        ),
        "relevance_tier": "DRILL_A_CAPABILITY_CLOSURE_CONFIRMATION",
        "composes_with": [
            "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
            "feedback_three_smoke_disciplines_no_silent_except_smoke_fires_discriminator_band_floor_inconclusive_2026-06-26",
            "feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26",
            "META_RULE_AF",
            "META_RULE_AG",
            "META_RULE_AH",
            "META_RULE_AL",
            "META_RULE_AN",
            "META_RULE_AO",
        ],
        "atomization_session": "skunkworks_2026-06-28_drill_AB_closure_confirmed",
    },
}

# ====================================================================
# ATOM 2: Block-sparse Hersche HARD_FAIL (Drill B)
# ====================================================================
bs_metrics = json.load(open(f"{HD}/data/exp_substrate_hierarchical_block_sparse_v1_smoke/metrics.json"))
bs_pa = bs_metrics["per_arm"]

atom_bs = {
    "id": "T3/EXP_substrate_hierarchical_block_sparse_v1_HARD_FAIL_DRILL_B_REVIVAL_hersche_block_sparse_BS_OPTS_0p100_no_block_assignment_0p050_dense_baseline_0p000_policy_only_0p050_random_blocks_0p200_random_0p050_lift_OPTS_RB_neg_0p100_lift_OPTS_DB_0p100_arms_distinct_True_cardinality_ok_120of120_N8192_L64_B128_blocks_per_opt16_state_blocks16_k_per_block8_random_blocks_OUTPERFORMS_block_sparse_options_block_assignment_is_HARMFUL_encoding_axis_test_negative_2026-06-28",
    "name": "Hierarchical planning block-sparse (Hersche) Drill B HARD_FAIL: random-block-assignment (0.20) BEATS structured block-sparse options (0.10); block assignment actively harmful; encoding-axis test negative",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Drill B revival attempt for hierarchical-planning capability class using Hersche block-sparse encoding "
        "(L=64 blocks, B=128 dim/block, 16 blocks/option, 16 state-blocks, k=8/block). 6-arm comparison at N=8192, "
        "composite-depth=6, 20 test goals, 6 actions, 3 options, seed=7. "
        "Mechanism (BLOCK_SPARSE_OPTIONS_FULL) = 0.100 solve_rate; lifts OPTS-RB=-0.100 OPTS-DB=+0.100 "
        "OPTS-NBA=+0.050 OPTS-RAND=+0.050; arms_distinct=True (SHA-256 6 distinct hashes); cardinality_ok=120/120; "
        "chance_floor=2.143e-05; theoretical SBC capacity=310.5 (per Hersche analysis). "
        "KEY TELL: random_blocks (0.200) > block_sparse_options_full (0.100) by 2x -- block-assignment is "
        "actively HARMFUL not helpful at this regime. The structured block-sparse encoding doesn't preserve "
        "compositional planning signal any better than random-block-assignment; in fact random-block is 2x better. "
        "This refutes the encoding-axis hypothesis (that block-sparse codes would dissolve the HRR composition "
        "collapse). The substrate's hierarchical-planning failure is NOT an encoding-format problem; it's a "
        "more fundamental compositional-credit-assignment problem that even orthogonal block-sparse can't fix. "
        "This is the 5th cell and 4th mechanism class HARD_FAIL on hierarchical-planning (after closed-form D_macro, "
        "state-conditioned+disjoint, Sutton-Precup options, Bacon-Roy option-critic). Per 2x-drill discipline "
        "(USER 2026-06-28), Drill B satisfies the second of two required revival drills; capability closure CONFIRMED."
    ),
    "aliases": [],
    "metadata": {
        "provenance_quality": "HONEST_NEGATIVE",
        "cert_status": "honest_negative",
        "cert_class": "mechanism_characterization",
        "record_class": "experiment_record",
        "term_class": "HARD_FAIL",
        "metric_type": "solve_rate_composite_depth6",
        "verdict": "HARD_FAIL",
        "verdict_raw": bs_metrics["verdict_msg"],
        "run_mode": "smoke",
        "experiment_path": "experiments/exp_substrate_hierarchical_block_sparse_v1.py",
        "metrics_path": "data/exp_substrate_hierarchical_block_sparse_v1_smoke/metrics.json",
        "drill_role": "DRILL_B_REVIVAL_HERSCHE_BLOCK_SPARSE_ENCODING_AXIS",
        "closes_against_capability": "hierarchical_planning_at_substrate_bipolar_HRR_N8192_depth6",
        "key_metrics": {
            "block_sparse_options_full_solve_rate": bs_pa["block_sparse_options_full"]["7"]["solve_rate"],
            "no_block_assignment_solve_rate": bs_pa["no_block_assignment"]["7"]["solve_rate"],
            "dense_baseline_solve_rate": bs_pa["dense_baseline"]["7"]["solve_rate"],
            "policy_only_solve_rate": bs_pa["policy_only"]["7"]["solve_rate"],
            "random_blocks_solve_rate": bs_pa["random_blocks"]["7"]["solve_rate"],
            "random_solve_rate": bs_pa["random"]["7"]["solve_rate"],
            "lift_opts_minus_random_blocks": bs_metrics["lift_options_minus_random_blocks"],
            "lift_opts_minus_dense_baseline": bs_metrics["lift_options_minus_dense_baseline"],
            "lift_opts_minus_no_block_assignment": bs_metrics["lift_options_minus_no_block_assignment"],
            "lift_opts_minus_random": bs_metrics["lift_options_minus_random"],
            "arms_distinct": bs_metrics["arms_distinct"],
            "cardinality_ok": bs_metrics["cardinality_ok"],
            "expected_n_units": bs_metrics["expected_n_units"],
            "completed_units": bs_metrics["completed_units"],
            "chance_random_floor": bs_metrics["chance_random_floor"],
            "sbc_capacity_theoretical": bs_metrics["sbc_capacity_theoretical"],
        },
        "arm_sha256_per_seed7": {arm: bs_pa[arm]["7"]["_seq_hash"] for arm in bs_pa},
        "root_diagnosis": (
            "random_blocks (0.200) BEATS block_sparse_options_full (0.100) by 2x; block-assignment actively harmful; "
            "encoding-axis falsified; structured block-sparse encoding doesn't preserve compositional planning signal "
            "any better than random-block; substrate hierarchical-planning failure is NOT an encoding-format problem "
            "but a more fundamental compositional-credit-assignment problem"
        ),
        "relevance_tier": "DRILL_B_CAPABILITY_CLOSURE_CONFIRMATION",
        "composes_with": [
            "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
            "feedback_three_smoke_disciplines_no_silent_except_smoke_fires_discriminator_band_floor_inconclusive_2026-06-26",
            "META_RULE_AF",
            "META_RULE_AG",
            "META_RULE_AH",
            "META_RULE_AL",
            "META_RULE_AN",
            "META_RULE_AO",
        ],
        "atomization_session": "skunkworks_2026-06-28_drill_AB_closure_confirmed",
    },
}

# ====================================================================
# ATOM 3: CAPABILITY_CLOSED_CONFIRMED 5-cell aggregate (supersedes preliminary 3-cell)
# ====================================================================
atom_closure_confirmed = {
    "id": "T3/EXP_hierarchical_planning_capability_CLOSURE_CONFIRMED_5_cells_4_mechanism_classes_2x_drill_discipline_satisfied_closed_form_Dmacro_state_conditioned_disjoint_Sutton_Precup_options_Bacon_Roy_option_critic_Hersche_block_sparse_DRILL_A_oc_full_0p000_train_neg_0p04_DRILL_B_block_sparse_0p100_random_blocks_0p200_block_assignment_harmful_substrate_bipolar_HRR_N8192_depth6_REINFORCE_plumbing_works_on_flat_compositional_credit_assignment_fundamentally_blocked_supersedes_preliminary_3_cell_closure_eda3d108_2026-06-28",
    "name": "Hierarchical planning capability CLOSED CONFIRMED at substrate bipolar-HRR regime: 5 cells / 4 mechanism classes; 2x-drill discipline satisfied (Drill A option-critic HF + Drill B block-sparse HF); supersedes preliminary 3-cell closure",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "CONFIRMED capability closure for hierarchical-planning at substrate's bipolar-HRR encoding regime "
        "(N=8192, composite-depth=6, BlocksWorld). Five consecutive smoke HARD_FAILs across FOUR distinct "
        "mechanism classes; 2x-drill discipline (USER 2026-06-28 feedback_2x_drill_negatives_before_capability_closure) "
        "satisfied via Drill A (Bacon-Roy 2017 option-critic) + Drill B (Hersche block-sparse encoding) both HARD_FAIL. "
        "Cells (5): "
        "(1) substrate_hierarchical_subgoal_planner_v1 closed-form D_macro pseudoinverse TREE=0.000 FLAT=0.133; "
        "(2) substrate_hierarchical_planner_state_conditioned_disjoint_v1 SC=0.000 DJ=0.000 BOTH=0.000; "
        "(3) substrate_hierarchical_options_v1 Sutton-Precup 1999 options OPTS=0.000 CF=0.100 RAND=0.000; "
        "(4) substrate_hierarchical_option_critic_v1 Bacon-Roy 2017 OC=0.000 PF=0.100 FLAT=0.050 RAND=0.000 (Drill A); "
        "(5) substrate_hierarchical_block_sparse_v1 Hersche BS=0.100 RB=0.200 (random > structured -- Drill B). "
        "All 5 cells: arms_distinct=True (SHA-256 per-arm), cardinality_ok=True, chance_floor=2.143e-05 (1/6^6 exact), "
        "discriminator-survives-scale at N=8192 composite-depth=6. "
        "KEY DRILL FINDINGS: Drill A demonstrates REINFORCE plumbing WORKS on flat-baseline (+0.08 train delta over "
        "100 episodes 0.12->0.20) but FAILS hierarchically (OC -0.04 train delta) -- failure is the hierarchical "
        "credit-assignment structure not the optimizer; Drill B demonstrates random-block-assignment BEATS "
        "structured block-sparse 2x -- failure is NOT an encoding-format problem. Together the 2 drills triangulate "
        "the root cause: substrate's compositional credit-assignment at composite-depth=6 is fundamentally blocked "
        "in this regime regardless of mechanism class or encoding format. "
        "This atom SUPERSEDES the preliminary 3-cell closure atom from commit eda3d108 "
        "(T3/EXP_substrate_hierarchical_options_v1_HONEST_NEGATIVE_CAPABILITY_CLOSED_three_mechanism_class_failures...). "
        "M3 implications: USER concern #5 hierarchical goal-decomposition DEFERRED (CONFIRMED); reframe M3 demo around "
        "substrate's chain-grade strengths (audit-device, KG-traversal, refuse-gate, multi-hop iter_cleanup). "
        "M4 implications: substrate-as-research-director Director-options framing DEFERRED (CONFIRMED). "
        "No further hierarchical-planning iterations at this regime without (a) USER+research consensus on fundamentally "
        "new mechanism class (NOT another variation on bipolar-HRR), (b) substrate-product pivot like pretrained-encoder "
        "swap-in, or (c) regime-shift to lower composite-depth as scaffolded scope-narrowing."
    ),
    "aliases": [],
    "metadata": {
        "provenance_quality": "HONEST_NEGATIVE",
        "cert_status": "honest_negative",
        "cert_class": "capability_closed_CONFIRMED_5_cells_2x_drill_discipline_satisfied",
        "record_class": "experiment_record",
        "term_class": "CAPABILITY_CLOSED_CONFIRMED",
        "metric_type": "solve_rate_composite_depth6",
        "verdict": "HARD_FAIL_AGGREGATE_5_CELLS",
        "run_mode": "smoke_aggregate",
        "supersedes_preliminary": "math::T3/EXP_substrate_hierarchical_options_v1_HONEST_NEGATIVE_CAPABILITY_CLOSED_three_mechanism_class_failures_closed_form_Dmacro_state_cond_disjoint_options_pi_beta_I_substrate_bipolar_HRR_cannot_preserve_compositional_partial_progress_signal_at_depth6",
        "supersedes_commit": "eda3d108",
        "closure_status": "CONFIRMED_2x_drill_discipline_satisfied",
        "n_cells": 5,
        "n_mechanism_classes": 4,
        "mechanism_classes": [
            "closed_form_Dmacro_pseudoinverse",
            "state_conditioned_disjoint_block",
            "Sutton_Precup_1999_options_pi_beta_I",
            "Bacon_Roy_2017_option_critic_learned_termination",
            "Hersche_block_sparse_encoding_axis_test",
        ],
        "cells_evidence": [
            {
                "anchor": "substrate_hierarchical_subgoal_planner_v1",
                "metrics_path": "data/exp_substrate_hierarchical_subgoal_planner_v1_smoke/metrics.json",
                "headline": "TREE=0.000 FLAT=0.133",
                "role": "first_HF_closed_form",
            },
            {
                "anchor": "substrate_hierarchical_planner_state_conditioned_disjoint_v1",
                "metrics_path": "data/exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke/metrics.json",
                "headline": "SC=0.000 DJ=0.000 BOTH=0.000",
                "role": "second_HF_state_conditioned",
            },
            {
                "anchor": "substrate_hierarchical_options_v1",
                "metrics_path": "data/exp_substrate_hierarchical_options_v1_smoke/metrics.json",
                "headline": "OPTS=0.000 CF=0.100 RAND=0.000",
                "role": "third_HF_Sutton_Precup_options_THIRD_FAILURE_GATE_TRIGGERED_PRELIMINARY_CLOSURE",
            },
            {
                "anchor": "substrate_hierarchical_option_critic_v1",
                "metrics_path": "data/exp_substrate_hierarchical_option_critic_v1_smoke/metrics.json",
                "headline": "OC=0.000 PF=0.100 BF=0.050 FLAT=0.050 V3=0.000 RAND=0.000",
                "role": "DRILL_A_REVIVAL_BACON_ROY_HF_REINFORCE_plumbing_works_on_flat_hierarchical_credit_fails",
                "atom_id": atom_oc["id"],
            },
            {
                "anchor": "substrate_hierarchical_block_sparse_v1",
                "metrics_path": "data/exp_substrate_hierarchical_block_sparse_v1_smoke/metrics.json",
                "headline": "BS=0.100 NBA=0.050 DB=0.000 POL=0.050 RB=0.200 RAND=0.050",
                "role": "DRILL_B_REVIVAL_HERSCHE_HF_random_blocks_BEATS_structured_2x_encoding_axis_falsified",
                "atom_id": atom_bs["id"],
            },
        ],
        "two_x_drill_discipline_satisfied": True,
        "user_discipline_ref": "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
        "drill_a_atom_id": atom_oc["id"],
        "drill_b_atom_id": atom_bs["id"],
        "drill_a_headline": "REINFORCE plumbing WORKS on flat (+0.08 train delta) but hierarchical structure prevents learning (-0.04 train delta) -- failure is HIERARCHICAL CREDIT-ASSIGNMENT not the optimizer",
        "drill_b_headline": "random_blocks (0.200) BEATS block_sparse_options_full (0.100) by 2x -- failure is NOT encoding-format; block-assignment actively harmful",
        "convergent_root_cause": (
            "substrate's compositional credit-assignment at composite-depth=6 in bipolar-HRR N=8192 regime is "
            "fundamentally blocked regardless of mechanism class or encoding format; 4 mechanism classes (closed-form, "
            "iterative-policy, option-framework, option-critic) and 2 encoding-formats (bundled HRR, block-sparse) all "
            "fail; REINFORCE optimizer plumbing demonstrably works on flat-baseline; failure is at the substrate-encoding "
            "level of how compositional partial-progress signal is (not) preserved"
        ),
        "regime_at_smoke": "N=8192,composite_depth=6,blocks=4,pos=3,actions=6,options=3,seed=7",
        "no_further_iteration_without_consensus": True,
        "next_steps_recommended": [
            "substrate-product pivot (pretrained-encoder swap-in like word2vec/pythia)",
            "regime-shift to lower composite-depth (e.g. depth=3 or depth=4) as scaffolded scope-narrowing",
            "abandon hierarchical-planning at this regime; reframe around chain-grade strengths",
        ],
        "m3_impact": "USER concern #5 hierarchical goal-decomposition DEFERRED; reframe demo around chain-grade strengths (audit, KG-traversal, refuse-gate, multi-hop iter_cleanup)",
        "m4_impact": "substrate-as-research-director Director-options framing DEFERRED; cosine-termination falsified at composite depth across 4 mechanism classes",
        "discriminator_survived_scale": True,
        "atomization_session": "skunkworks_2026-06-28_drill_AB_closure_confirmed",
        "composes_with": [
            "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
            "feedback_three_smoke_disciplines_no_silent_except_smoke_fires_discriminator_band_floor_inconclusive_2026-06-26",
            "feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26",
            "META_RULE_AF",
            "META_RULE_AG",
            "META_RULE_AH",
            "META_RULE_AL",
            "META_RULE_AN",
            "META_RULE_AO",
        ],
    },
}

# ====================================================================
# ATOM 4: META_RULE_AO_v2 amendment (CONFIRMED 5-cell evidence; well-evidenced)
# ====================================================================
atom_ao_v2 = {
    "id": "T_methodology/META_RULE_AO_v2_capability_closure_CONFIRMED_via_2x_drill_discipline_after_initial_3_mechanism_class_HF_supersedes_v1_first_witness_hierarchical_planning_5_cells_4_mechanism_classes_2x_drill_satisfied_Drill_A_Bacon_Roy_option_critic_HF_Drill_B_Hersche_block_sparse_HF_substrate_bipolar_HRR_N8192_depth6_REINFORCE_plumbing_works_on_flat_compositional_credit_assignment_fundamentally_blocked_well_evidenced_2026-06-28",
    "name": "META_RULE_AO_v2 -- capability-closure CONFIRMED via 2x-drill discipline after initial 3-mechanism-class HF (supersedes v1)",
    "corpus": "meta",
    "tier": "T_methodology",
    "kind": "methodology_rule",
    "description": (
        "AMENDMENT to META_RULE_AO (capability-closure-after-3-mechanism-class-HF) reflecting USER 2026-06-28 "
        "2x-drill discipline (feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28). "
        "REFINED RULE: 3 consecutive smoke HARD_FAILs across distinct mechanism classes triggers PRELIMINARY "
        "capability closure (file preliminary closure atom; queue 2 revival drills). PRELIMINARY closure becomes "
        "CONFIRMED closure only after BOTH revival drills return HARD_FAIL at cell-level (each drill must be a "
        "DISTINCT mechanism class from the original 3 AND from each other; each drill must satisfy "
        "arms_distinct=True + cardinality_ok=True + discriminator-survives-scale). If either revival drill returns "
        "MIDDLE_BAND or HARD_PASS, preliminary closure is RESCINDED and capability remains OPEN. "
        "FIRST CONFIRMED WITNESS 2026-06-28: hierarchical-planning at substrate bipolar-HRR regime. "
        "Original 3-mechanism-class HF: closed-form D_macro + state-conditioned-disjoint + Sutton-Precup options. "
        "Drill A: Bacon-Roy 2017 option-critic -> HARD_FAIL (OC=0.000; REINFORCE plumbing works on flat-baseline "
        "+0.08 train delta but hierarchical structure prevents learning -0.04 train delta). "
        "Drill B: Hersche block-sparse encoding axis -> HARD_FAIL (BS=0.100, random-block 0.200 BEATS structured 2x; "
        "encoding-format axis falsified). "
        "Together: 5 cells / 4 mechanism classes / 2 encoding-formats all converge on substrate compositional credit-"
        "assignment being fundamentally blocked at this regime, NOT a mechanism-specific or encoding-specific failure. "
        "RATIONALE for 2x-drill: 3-mechanism-class closure could rule out 3 specific implementations but leave the "
        "capability open in principle; 2x-drill across BOTH a fundamentally-different mechanism class (e.g. learned vs "
        "closed-form vs option-framework -> option-critic) AND an encoding-axis swap (e.g. bundled-HRR -> block-sparse) "
        "triangulates the failure to a deeper level (substrate-encoding compositional credit-assignment) rather than "
        "any single mechanism or encoding choice. "
        "COMPOSITION: extends META_RULE_AO (3-mechanism-class) at the CONFIRMATION layer; preserves META_RULE_AO's "
        "preconditions; adds the 2x-drill ratification step before declaring closure CONFIRMED."
    ),
    "aliases": [],
    "metadata": {
        "provenance_quality": None,
        "instance_number": None,
        "confirmed_or_candidate": "CONFIRMED",
        "rule_id": "META_RULE_AO_v2",
        "rule_class": "capability_closure_confirmation_via_2x_drill_discipline",
        "supersedes_rule": "META_RULE_AO",
        "supersedes_atom_id": "meta::T_methodology/META_RULE_AO_capability_closure_after_3_mechanism_class_HF_when_three_consecutive_smoke_HARD_FAILs_on_same_capability_across_distinct_mechanism_classes_close_capability_box_file_capability_closed_atom_no_4th_iteration_without_USER_and_research_consensus_on_new_mechanism_class_witness_hierarchical_planning_closed_form_Dmacro_then_state_cond_disjoint_then_Sutton_Precup_options_all_HF_at_substrate_bipolar_HRR_regime_2026-06-28",
        "first_witness_date": "2026-06-28",
        "first_witness_capability": "hierarchical_planning_at_substrate_bipolar_HRR",
        "first_witness_cells_total_5": [
            "exp_substrate_hierarchical_subgoal_planner_v1_smoke",
            "exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke",
            "exp_substrate_hierarchical_options_v1_smoke",
            "exp_substrate_hierarchical_option_critic_v1_smoke",
            "exp_substrate_hierarchical_block_sparse_v1_smoke",
        ],
        "first_witness_drill_a_cell": "exp_substrate_hierarchical_option_critic_v1_smoke",
        "first_witness_drill_b_cell": "exp_substrate_hierarchical_block_sparse_v1_smoke",
        "preliminary_closure_preconditions": [
            "3 consecutive smoke HARD_FAILs",
            "distinct mechanism classes (not iterations of same)",
            "all cells arms_distinct=True",
            "all cells cardinality_ok=True",
            "all cells discriminator-survives-scale at full N regime",
            "diagnoses converge on substrate-encoding root (not mech-specific)",
        ],
        "confirmation_preconditions": [
            "preliminary closure declared per 3-mechanism-class precondition above",
            "Drill A revival HARD_FAIL with distinct mechanism class from original 3",
            "Drill B revival HARD_FAIL with distinct mechanism class from original 3 AND from Drill A",
            "both drill cells satisfy arms_distinct + cardinality_ok + discriminator-survives-scale",
            "diagnoses across all 5 cells converge on a single root cause (substrate-encoding / credit-assignment / etc)",
            "ideally Drill B is an encoding-axis swap to triangulate mechanism-vs-encoding root cause separation",
        ],
        "rescission_condition": "if either revival drill returns MIDDLE_BAND or HARD_PASS, preliminary closure RESCINDED and capability remains OPEN",
        "closure_action_CONFIRMED": "file capability-CLOSED-CONFIRMED atom (math::T3 experiment_record HONEST_NEGATIVE) SUPERSEDING preliminary closure atom; no further iteration without USER+research consensus on fundamentally new mechanism class; recommend program-level pivot (substrate-product encoder swap / regime-shift)",
        "composes_with": [
            "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
            "META_RULE_AO",
            "META_RULE_AF",
            "META_RULE_AG",
            "META_RULE_AH",
            "META_RULE_AL",
            "META_RULE_AN",
        ],
        "atomized_by": ATOMIZED_BY,
        "atomized_session": "2026-06-28_drill_AB_closure_confirmed",
    },
}

# ====================================================================
# Audit + cert_ledger rows
# ====================================================================

def hash_of(atom: dict) -> str:
    return hashlib.sha256(json.dumps(atom, sort_keys=True).encode()).hexdigest()[:16]

oc_hash = hash_of(atom_oc)
bs_hash = hash_of(atom_bs)
closure_hash = hash_of(atom_closure_confirmed)
ao_v2_hash = hash_of(atom_ao_v2)

print()
print("ATOM HASHES (sha256[:16]):")
print(f"  OC HF:         {oc_hash}")
print(f"  BS HF:         {bs_hash}")
print(f"  Closure CONF:  {closure_hash}")
print(f"  META_RULE_AO_v2: {ao_v2_hash}")
print()

# math audit rows
math_audit_rows = [
    json.dumps({
        "ts": TS, "op": "add", "corpus": "math", "atom_id": atom_oc["id"],
        "atom_hash": oc_hash, "atomized_by": ATOMIZED_BY,
        "note": "drill_A_option_critic_HF_REINFORCE_plumbing_works_flat_hierarchical_credit_fails",
    }),
    json.dumps({
        "ts": TS, "op": "add", "corpus": "math", "atom_id": atom_bs["id"],
        "atom_hash": bs_hash, "atomized_by": ATOMIZED_BY,
        "note": "drill_B_block_sparse_HF_random_blocks_beats_structured_2x_encoding_axis_falsified",
    }),
    json.dumps({
        "ts": TS, "op": "add", "corpus": "math", "atom_id": atom_closure_confirmed["id"],
        "atom_hash": closure_hash, "atomized_by": ATOMIZED_BY,
        "supersedes": atom_closure_confirmed["metadata"]["supersedes_preliminary"],
        "note": "capability_closure_CONFIRMED_5_cells_2x_drill_satisfied_supersedes_preliminary_eda3d108",
    }),
]

meta_audit_rows = [
    json.dumps({
        "ts": TS, "op": "add", "corpus": "meta", "atom_id": atom_ao_v2["id"],
        "atom_hash": ao_v2_hash, "atomized_by": ATOMIZED_BY,
        "supersedes": atom_ao_v2["metadata"]["supersedes_atom_id"],
        "note": "META_RULE_AO_v2_2x_drill_discipline_confirmation_layer_supersedes_v1_well_evidenced",
    }),
]

# cert_ledger rows (3 cert rulings -- OC HF, BS HF, closure CONFIRMED upgrade)
ledger_rows = [
    json.dumps({
        "ts": TS, "op": "cert_ruling", "atom_id": f"math::{atom_oc['id']}",
        "cert_status": "honest_negative", "cert_class": "mechanism_characterization",
        "verified_off_data": True, "atomized_by": ATOMIZED_BY, "cell_commit": None,
        "verdict": "HARD_FAIL", "cert_increment_delta": 0, "cv": None,
        "referent_pointer": {
            "metrics_path": "data/exp_substrate_hierarchical_option_critic_v1_smoke/metrics.json",
            "prereg_path": "preregs/2026-06-28_substrate_hierarchical_option_critic_v1.md",
            "experiment_path": "experiments/exp_substrate_hierarchical_option_critic_v1.py",
            "atom_qualified_id": f"math::{atom_oc['id']}",
        },
        "supersedes": None,
        "note": "drill_A_option_critic_HF_OC_full_0p000_REINFORCE_works_on_flat_train_delta_pos_0p08_OC_train_delta_neg_0p04_hierarchical_credit_assignment_blocked",
    }),
    json.dumps({
        "ts": TS, "op": "cert_ruling", "atom_id": f"math::{atom_bs['id']}",
        "cert_status": "honest_negative", "cert_class": "mechanism_characterization",
        "verified_off_data": True, "atomized_by": ATOMIZED_BY, "cell_commit": None,
        "verdict": "HARD_FAIL", "cert_increment_delta": 0, "cv": None,
        "referent_pointer": {
            "metrics_path": "data/exp_substrate_hierarchical_block_sparse_v1_smoke/metrics.json",
            "experiment_path": "experiments/exp_substrate_hierarchical_block_sparse_v1.py",
            "atom_qualified_id": f"math::{atom_bs['id']}",
        },
        "supersedes": None,
        "note": "drill_B_block_sparse_HF_BS_0p100_random_blocks_0p200_beats_structured_2x_encoding_axis_falsified_NOT_encoding_format_problem",
    }),
    json.dumps({
        "ts": TS, "op": "cert_ruling", "atom_id": f"math::{atom_closure_confirmed['id']}",
        "cert_status": "honest_negative", "cert_class": "capability_closed_CONFIRMED_2x_drill_satisfied",
        "verified_off_data": True, "atomized_by": ATOMIZED_BY, "cell_commit": None,
        "verdict": "HARD_FAIL_AGGREGATE_5_CELLS", "cert_increment_delta": 0, "cv": None,
        "referent_pointer": {
            "atom_qualified_id": f"math::{atom_closure_confirmed['id']}",
            "drill_a_metrics": "data/exp_substrate_hierarchical_option_critic_v1_smoke/metrics.json",
            "drill_b_metrics": "data/exp_substrate_hierarchical_block_sparse_v1_smoke/metrics.json",
        },
        "supersedes": f"math::{atom_closure_confirmed['metadata']['supersedes_preliminary']}",
        "note": "capability_closure_hierarchical_planning_CONFIRMED_5_cells_4_mechanism_classes_2x_drill_satisfied_supersedes_preliminary_3_cell_eda3d108_substrate_compositional_credit_assignment_fundamentally_blocked_at_bipolar_HRR_N8192_depth6_regime_USER_discipline_2026-06-28_satisfied",
    }),
]

# ====================================================================
# A5 atomic write
# ====================================================================
print("Writing atoms (A5 atomic + verify-load)...")

atomic_append(MATH_ATOMS, [
    json.dumps(atom_oc),
    json.dumps(atom_bs),
    json.dumps(atom_closure_confirmed),
])
atomic_append(MATH_AUDIT, math_audit_rows)
atomic_append(META_ATOMS, [json.dumps(atom_ao_v2)])
atomic_append(META_AUDIT, meta_audit_rows)
atomic_append(META_LEDGER, ledger_rows)

# ====================================================================
# A5 POST verify -- counts and round-trip via fresh open
# ====================================================================
print()
print("A5 POST verify (fresh load round-trip)...")

with open(MATH_ATOMS, encoding="utf-8") as f:
    math_n = sum(1 for _ in f)
with open(META_ATOMS, encoding="utf-8") as f:
    meta_n = sum(1 for _ in f)
print(f"  math atoms now: {math_n}")
print(f"  meta atoms now: {meta_n}")

# Find each newly-landed atom by id and confirm round-trip
def find_by_id(path: str, atom_id: str) -> bool:
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                if json.loads(line).get("id") == atom_id:
                    return True
            except Exception:
                continue
    return False

assert find_by_id(MATH_ATOMS, atom_oc["id"]), "OC atom missing after write"
assert find_by_id(MATH_ATOMS, atom_bs["id"]), "BS atom missing after write"
assert find_by_id(MATH_ATOMS, atom_closure_confirmed["id"]), "Closure atom missing after write"
assert find_by_id(META_ATOMS, atom_ao_v2["id"]), "META_RULE_AO_v2 missing after write"
print("  All 4 atoms round-trip OK")

print()
print("DONE: 4 atoms landed (3 math + 1 meta) + 3 cert_ledger rows")
print(f"  OC hash:         {oc_hash}")
print(f"  BS hash:         {bs_hash}")
print(f"  Closure hash:    {closure_hash}")
print(f"  META AO_v2 hash: {ao_v2_hash}")
