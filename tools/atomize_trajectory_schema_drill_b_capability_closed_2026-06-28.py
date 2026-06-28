#!/usr/bin/env python3
"""Atomize: Drill B trajectory_schema_per_hop_v1 HARD_FAIL CAPABILITY_CLOSURE 2026-06-28.

Closes the brain-faithful 4-primitive multi-hop chain composition capability box
per the 2x-drill discipline (`feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28`).

Drill A (pfc_wm_state_tracker_v1; state-bias adapter mechanism class):
    HARD_FAIL all 3 adapters; atomized 2026-06-28
    atom_id math::T3/EXP_partition_oracle_pfc_wm_state_tracker_4primitive...

Drill B (trajectory_schema_per_hop_v1; primitive output redesign mechanism class):
    HARD_FAIL_CAPABILITY_CLOSURE seed_7 smoke 2026-06-28
    Per-arm verified-off-data via .venv recompute (skunkworks landed-VET PASS).
    arm_d_path4_trajectory_schema top1=0.0000 (HF gates D<=0.30, lift_C<0.10,
    D<A=0.40 cascade, per_hop h10=0.18 below 0.25). Root cause: k_pred vs
    k_train mismatch 92%->0% across hops; trajectory readout S @ traj_key reads
    WRONG ROW because schema-Bayes partial-prefix query is structurally not a
    stable cluster-identity signal.

Two structurally-distinct mechanism classes -> 2x discipline satisfied
-> capability box CLOSES on brain-faithful 4-primitive composition.

Atomizes:
  1) Drill B HF atom (math::T3 EXPERIMENT_RECORD; cert_class=mechanism_characterization)
  2) Capability-closed atom (math::T3 EXPERIMENT_RECORD; cert_class=
     capability_closed_two_drill_discipline_satisfied; cross-cites Drill A + Drill B)
  3) META_RULE_AP v3 promotion atom (meta::T_methodology METHODOLOGY_RULE; CONFIRMED;
     adds NATIVE_OUTPUT_GRANULARITY clause; 4+ witnesses today)

Auditor: skunkworks (cert-owner; A5 PRE/POST + round-trip verify + cert-ledger).
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_honest_negative_row,
)

STORE_ROOT = REPO / 'data' / 'substrate_index'

# Cross-cite anchors (verified pre-atomization)
DRILL_A_ATOM_ID = (
    "math::T3/EXP_partition_oracle_pfc_wm_state_tracker_4primitive_composition_"
    "HARD_FAIL_all_3_adapter_sub_mechanisms_dead_state_tracker_cannot_rescue_"
    "hop0_anchored_upstream_schema_primitive_2026-06-28"
)
DRILL_A_COMMIT_HASH = "69544689c4f302bb"  # per spawn prompt
DRILL_A_METRICS = (
    "data/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7_smoke/"
    "metrics.json"
)


def build_drill_b_hf_atom() -> Atom:
    """Drill B HF atom: per-hop schema-Bayes redesign HARD_FAIL via k_pred/k_train mismatch."""
    return Atom(
        id=(
            "T3/EXP_partition_oracle_trajectory_schema_per_hop_v1_HARD_FAIL_"
            "drill_B_per_hop_schema_bayes_redesign_k_pred_train_mismatch_92pct_"
            "to_0pct_across_hops_S_matrix_readout_high_cosine_0p72_but_wrong_row_"
            "schema_bayes_partial_prefix_NOT_stable_cluster_identity_signal_"
            "trajectory_primitive_redesign_does_not_rescue_per_hop_partition_"
            "discrimination_2026-06-28"
        ),
        name=(
            "Drill B per-hop schema-Bayes redesign HARD_FAIL -- k_pred vs k_train "
            "mismatch (92%->0% across 15 hops); S matrix readout strong cosine "
            "(~0.72) but reads WRONG ROW because partial-prefix schema query "
            "lands in different cluster than full-chain training"
        ),
        description=(
            "Drill B HARD_FAIL diagnosis for the brain-faithful 4-primitive "
            "multi-hop chain composition: replacing Drill A's hop-0-locked "
            "cluster_to_target_part[k] map with a per-(cluster, hop_idx) -> "
            "partition trajectory store via the substrate's chain-grade "
            "sequence-binding S matrix in its native shape FAILS to rescue. "
            "Smoke seed_7 (full N=8192, depth=15, n_chains_test=100; elapsed "
            "888s) per-arm MEASURED@2026-06-28: "
            "A BASELINE=0.4000 (rail OK); "
            "B PATH2_PERCHAIN=0.0100 (reproduces today's HF); "
            "C PATH3_4PRIM_HOP0_LOCKED=0.0000 (Gate D positive control PASS; "
            "reproduces Drill A SUB_A at SAME regime); "
            "D PATH4_TRAJECTORY_SCHEMA (the new mechanism)=0.0000 (HARD_FAIL); "
            "E ORACLE_PER_HOP=0.8400 (upper bound replicates Drill A); "
            "F RANDOM=0.0000 (floor). "
            "HARD_FAIL gates tripped simultaneously: D<=0.30 (0.0000); "
            "lift_C<0.10 (0.0000); D<A cascade collapse (-0.4000); "
            "per_hop part-acc at hop 10 <= 0.25 (0.180). "
            "ROOT CAUSE: drill pre-mortem mode #1 (P=0.40) CONFIRMED. "
            "k_pred_per_hop_vs_k_train_mismatch_rate = [0.92, 0.84, 0.86, 0.85, "
            "0.79, 0.78, 0.75, 0.69, 0.57, 0.56, 0.51, 0.48, 0.41, 0.25, 0.00] "
            "(high at early hops -> zero at last hop). "
            "trajectory_readout_cosine_per_hop = [0.70, 0.69, 0.76, 0.69, 0.74, "
            "0.76, 0.74, 0.76, 0.74, 0.72, 0.75, 0.72, 0.69, 0.70, 0.78] "
            "(strong throughout). "
            "The S matrix IS storing and reading per-(cluster, hop) -> partition "
            "pairs with high SNR (capacity ratio 300/8192=0.037 well below "
            "cliff). Edge 3 (S @ traj_key readout) works as theorized. The "
            "failure is structural to the schema-Bayes primitive itself: "
            "partial-prefix query (past predicates only) is NOT a stable "
            "cluster-identity signal early in chain; cluster identity emerges "
            "only when most/all predicates of the chain are in scope. "
            "Trajectory primitive reads the wrong row of S because the cluster "
            "key is wrong, not because the trajectory store is wrong. "
            "arms_distinct=True (6 unique SHA-256); cardinality_ok=True "
            "(expected_n_units=6, observed=6); baseline_rail_ok=True; "
            "saturated_any=False. Gate D positive control PASSED (arm_c=0.00 "
            "within expected [0.00,0.30]); regime invocation correct -> the "
            "HF is a REAL mechanism failure not a setup bug."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "record_class": "experiment_record",
            "term_class": "HARD_FAIL",
            "verdict": "HARD_FAIL_CAPABILITY_CLOSURE",
            "verdict_raw": (
                "HARD_FAIL_4_PRIMITIVE_BRAIN_FAITHFUL_COMPOSITION_CLOSES_PER_2X_"
                "DRILL_DISCIPLINE_DRILL_A_AND_B_BOTH_NULL_M3_NEEDS_EXTERNAL_"
                "CORTEX_LAYER"
            ),
            "metric_type": "per_hop_partition_accuracy_top1_depth15",
            "run_mode": "smoke",
            "experiment_path": (
                "experiments/exp_substrate_partition_oracle_trajectory_schema_"
                "per_hop_v1_seed_7.py"
            ),
            "prereg_path": (
                "preregs/2026-06-28_substrate_partition_oracle_trajectory_schema_"
                "per_hop_v1.md"
            ),
            "metrics_path": (
                "data/exp_substrate_partition_oracle_trajectory_schema_per_hop_"
                "v1_seed_7_smoke/metrics.json"
            ),
            "verdict_note_path": (
                "notes/exp_dev_verdict_trajectory_schema_per_hop_v1_smoke_HARD_"
                "FAIL_CAPABILITY_CLOSURE_2026-06-28.md"
            ),
            "cell_sha": None,
            "remote_run_id": None,
            "hypothesis": (
                "Per-(cluster, hop_idx) -> partition trajectory store built via "
                "substrate's chain-grade sequence-binding S matrix in native "
                "shape will rescue per-hop partition discrimination to top1 in "
                "[0.50, 0.95]."
            ),
            "metrics_headline": (
                "PATH4_D=0.0000 (HF) | PATH3_C=0.0000 (Gate D PASS) | "
                "BASELINE_A=0.4000 | PATH2_B=0.0100 | ORACLE_E=0.8400 | "
                "RANDOM_F=0.0000"
            ),
            "key_metrics": {
                "arm_d_path4_trajectory_schema_top1": 0.0000,
                "arm_c_path3_4prim_hop0_locked_top1": 0.0000,
                "arm_a_baseline_top1": 0.4000,
                "arm_b_path2_perchain_top1": 0.0100,
                "arm_e_oracle_per_hop_top1": 0.8400,
                "arm_f_random_top1": 0.0000,
                "lift_d_over_c": 0.0000,
                "lift_d_over_a": -0.4000,
                "lift_d_over_b": -0.0100,
                "gap_e_minus_d": 0.8400,
                "per_hop_part_acc_arm_d_h5": 0.150,
                "per_hop_part_acc_arm_d_h10": 0.180,
                "per_hop_part_acc_arm_d_h15": 0.250,
                "k_pred_train_mismatch_h0": 0.92,
                "k_pred_train_mismatch_h10": 0.51,
                "k_pred_train_mismatch_h14": 0.00,
                "trajectory_readout_cosine_h0": 0.7014,
                "trajectory_readout_cosine_h14": 0.7814,
                "capacity_ratio_K_seq_N": 0.0366,
                "K_seq_effective": 300,
                "n_seeds_complete": 1,
                "cardinality_ok": True,
                "expected_n_units": 6,
                "baseline_rail_ok": True,
                "saturated_any": False,
                "arms_distinct": True,
                "gate_d_positive_control_pass": True,
                "gate_d_arm_c_top1": 0.0000,
                "elapsed_s": 887.9,
            },
            "arm_sha256_per_seed7": {
                "arm_a_baseline": "a5d3c04e17f38855",
                "arm_b_path2_perchain": "b25b9c3114886f90",
                "arm_c_path3_4prim_hop0_locked": "21e3bb76c47f7c22",
                "arm_d_path4_trajectory_schema": "bb61b0003d3ebf0d",
                "arm_e_oracle_per_hop": "bd0c50a94606ef95",
                "arm_f_random": "626d10a177bd418c",
            },
            "regime_at_smoke": (
                "N=8192,V_C=4000,V_P=10,depth=15,n_parts=5,psz=800,n_schemas=20,"
                "wm_bank_K=200,n_chains_train=200,n_chains_test=100,seeds=[7],"
                "encoder=SUBSTRATE_NATIVE_BIPOLAR"
            ),
            "root_diagnosis": (
                "drill pre-mortem mode #1 P=0.40 CONFIRMED: k_pred vs k_train "
                "mismatch 92% at hop 0 decaying to 0% at hop 14; trajectory "
                "readout S @ traj_key cosine 0.69-0.78 throughout (mechanism "
                "works as theorized) BUT reads WRONG ROW because partial-prefix "
                "schema-Bayes query is not a stable cluster-identity signal "
                "early in chain; structural to schema-Bayes primitive"
            ),
            "verified_off_data": True,
            "verified_off_data_evidence": (
                ".venv python independent recompute off raw per_step_acc + "
                "partition_correct_per_step + k_pred_per_hop_vs_k_train_mismatch_"
                "rate arrays in metrics.json; all 6 arm top1 values cited "
                "reproduce from final-hop per_step_acc; all 4 HF gates "
                "(D<=0.30, lift_C<0.10, D<A, per_hop_h10<=0.25) verified "
                "independently; Gate D positive control (arm_c in [0.00,0.30]) "
                "verified; arms_distinct (6 unique SHA) verified; cardinality_ok "
                "verified"
            ),
            "skunkworks_landed_vet_verdict": "HARD_FAIL_CONFIRMED",
            "skunkworks_schema_vet_verdict": (
                "PASS_pre_reg_5_gates_A_B_C_D_E_compliant_with_full_§15_"
                "discipline_per_dispatch_check"
            ),
            "discriminator_survived_scale": True,
            "discriminator_survived_scale_evidence": (
                "smoke at FULL N=8192 and FULL depth=15 (Check A); only "
                "n_chains_test reduced 200->100; HF gates fire at smoke scale"
            ),
            "atomization_session": (
                "skunkworks_2026-06-28_drill_b_capability_closure"
            ),
            "two_x_drill_discipline_role": "drill_B_negative_2_of_2",
            "two_x_drill_partner_atom_id": DRILL_A_ATOM_ID,
            "two_x_drill_partner_commit_hash": DRILL_A_COMMIT_HASH,
            "composes_with": [
                "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
                "feedback_chain_grade_primitives_not_trivially_composable_2026-06-28",
                "feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26",
                "feedback_test_design_failure_diagnosis_and_hardening_USER_2026-06-28",
                "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AG",
                "META_RULE_AH", "META_RULE_AL", "META_RULE_AN", "META_RULE_AP",
                "META_RULE_H",
                "BIAS-N", "BIAS-Q", "BIAS-S",
                "PROT-018", "PROT-021", "Fix-28", "NO-LOCAL-PROMOTE",
            ],
        },
    )


def build_capability_closed_atom() -> Atom:
    """Capability-closure atom: 2x-drill discipline satisfied for brain-faithful 4-primitive composition."""
    return Atom(
        id=(
            "T3/EXP_brain_faithful_4_primitive_multihop_chain_composition_"
            "CAPABILITY_CLOSED_2x_drill_discipline_satisfied_drill_A_state_bias_"
            "adapter_HF_drill_B_per_hop_schema_bayes_primitive_redesign_HF_"
            "substrate_native_chain_grade_primitives_cannot_compose_multi_hop_"
            "chain_at_depth_15_M3_needs_external_cortex_layer_for_hint_derivation_"
            "2026-06-28"
        ),
        name=(
            "Brain-faithful 4-primitive multi-hop chain composition CAPABILITY "
            "CLOSED -- 2x-drill discipline satisfied (Drill A state-bias adapter "
            "HF + Drill B per-hop schema-Bayes primitive redesign HF; M3 needs "
            "external cortex layer for hint derivation)"
        ),
        description=(
            "Closure of the brain-faithful 4-primitive multi-hop chain "
            "composition capability box per the 2x-drill discipline "
            "(`feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28`): "
            "two structurally-different mechanism classes both NULL on the "
            "same capability (per-hop partition discrimination at depth=15 "
            "from past-predicate-only context). "
            "Drill A (state-bias adapter mechanism class; "
            "exp_substrate_partition_oracle_pfc_wm_state_tracker_v1; commit "
            "hash 69544689c4f302bb): HARD_FAILed all 3 adapters; root cause = "
            "cluster_to_target_part[k] map is hop-0-locked. "
            "Drill B (primitive output redesign mechanism class; "
            "exp_substrate_partition_oracle_trajectory_schema_per_hop_v1; this "
            "atom): HARD_FAILed; root cause = schema-Bayes partial-prefix query "
            "is not a stable cluster-identity signal early in chain. "
            "Both null at the SAME regime (N=8192 V_C=4000 d=15 psz=800 K=200) "
            "but for structurally-DIFFERENT reasons (state-tracker injection "
            "vs primitive output granularity redesign). The 2x discipline is "
            "designed for exactly this: redesign exhausts the mechanism class "
            "when 2 distinct redesign attempts converge on null. "
            "CAPABILITY BOX CLOSES: brain-faithful 4-primitive composition "
            "(schema-Bayes + sequence-binding + WM/state-tracker + partition-"
            "routing + cleanup) CANNOT do multi-hop chain reasoning at the "
            "substrate-native level at this depth. "
            "M3 ARCHITECTURE IMPLICATION (NOW FIRMLY CONFIRMED): M3 needs "
            "external cortex/planner layer for hint derivation. The partition-"
            "oracle substrate-side composition primitive is already chain-grade "
            "today (`chain_grade_barrier1_substrate_native_break_partition_"
            "oracle_goal_conditioning_3seed_verified_2026-06-28`) and takes "
            "ground-truth hints. The external layer's job is to derive the "
            "partition hint from a query; this can be an LLM router, a learned "
            "planner, or a NEW primitive class (e.g. dopaminergic gating, "
            "online cluster re-identification, content-addressed routing). "
            "M3 architecture = SUBSTRATE (chain-grade composition + memory + "
            "audit + KG traversal + refuse-gate) + EXTERNAL_LAYER (hint "
            "derivation) = working multi-hop reasoning. "
            "This closure aggregates the Drill A and Drill B HF evidence; "
            "supersedes prior open-ended exploration of brain-faithful 4-"
            "primitive composition at substrate-native level (no 3rd iteration "
            "without USER + research consensus on a new mechanism class)."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "capability_closed_two_drill_discipline_satisfied",
            "record_class": "experiment_record",
            "term_class": "CAPABILITY_CLOSED",
            "verdict": "HARD_FAIL",
            "verdict_raw": (
                "CAPABILITY_CLOSED_per_2x_drill_discipline_drill_A_state_bias_"
                "adapter_HF_drill_B_per_hop_schema_bayes_primitive_redesign_HF_"
                "both_null_on_same_capability_at_same_regime"
            ),
            "metric_type": "per_hop_partition_accuracy_top1_depth15",
            "run_mode": "smoke",
            "closure_note_path": (
                "notes/exp_dev_verdict_trajectory_schema_per_hop_v1_smoke_HARD_"
                "FAIL_CAPABILITY_CLOSURE_2026-06-28.md"
            ),
            "drill_a_atom_id": DRILL_A_ATOM_ID,
            "drill_a_commit_hash": DRILL_A_COMMIT_HASH,
            "drill_a_metrics_path": DRILL_A_METRICS,
            "drill_b_atom_id": (
                "math::T3/EXP_partition_oracle_trajectory_schema_per_hop_v1_HARD_"
                "FAIL_drill_B_per_hop_schema_bayes_redesign_k_pred_train_mismatch_"
                "92pct_to_0pct_across_hops_S_matrix_readout_high_cosine_0p72_but_"
                "wrong_row_schema_bayes_partial_prefix_NOT_stable_cluster_"
                "identity_signal_trajectory_primitive_redesign_does_not_rescue_"
                "per_hop_partition_discrimination_2026-06-28"
            ),
            "drill_b_metrics_path": (
                "data/exp_substrate_partition_oracle_trajectory_schema_per_hop_"
                "v1_seed_7_smoke/metrics.json"
            ),
            "closure_mechanism_classes": [
                "state_bias_adapter_drill_A",
                "primitive_output_granularity_redesign_drill_B",
            ],
            "two_x_drill_satisfied": True,
            "regime_at_closure": (
                "N=8192,V_C=4000,V_P=10,depth=15,n_parts=5,psz=800,"
                "encoder=SUBSTRATE_NATIVE_BIPOLAR"
            ),
            "verified_off_data": True,
            "verified_off_data_evidence": (
                "Drill B: .venv python independent recompute confirms all 6 "
                "arm top1 and all 4 HF gates fire; Gate D positive control "
                "PASSED; arms_distinct + cardinality_ok verified. Drill A: "
                "prior atomization 2026-06-28 commit 47268ec5 (per spawn "
                "prompt; hash 69544689c4f302bb)"
            ),
            "m3_architecture_implication": (
                "M3 needs external cortex/planner layer for hint derivation; "
                "SUBSTRATE side (chain-grade composition + memory + audit) "
                "remains intact and takes ground-truth hints (partition-oracle "
                "goal-conditioning chain-grade 3-seed verified 2026-06-28); "
                "EXTERNAL_LAYER candidates: LLM router, learned planner, NEW "
                "primitive class (dopaminergic gating / online cluster re-"
                "identification / content-addressed routing)"
            ),
            "m3_architecture_atom_to_update": (
                "project_M3_architecture_needs_cortex_layer_above_substrate_"
                "USER_2026-06-28"
            ),
            "no_3rd_iteration_without_consensus": True,
            "cert_increment_delta": 0,
            "atomization_session": (
                "skunkworks_2026-06-28_drill_b_capability_closure"
            ),
            "composes_with": [
                "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
                "feedback_chain_grade_primitives_not_trivially_composable_2026-06-28",
                "feedback_test_design_failure_diagnosis_and_hardening_USER_2026-06-28",
                "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
                "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AG",
                "META_RULE_AH", "META_RULE_AL", "META_RULE_AN", "META_RULE_AP",
                "META_RULE_H",
            ],
        },
    )


def build_meta_rule_ap_v3_atom() -> Atom:
    """META_RULE_AP v3: chain-grade primitives not trivially composable + NATIVE_OUTPUT_GRANULARITY clause."""
    return Atom(
        id=(
            "T_methodology/META_RULE_AP_v3_chain_grade_primitives_not_trivially_"
            "composable_PROMOTED_CONFIRMED_with_NATIVE_OUTPUT_GRANULARITY_clause_"
            "4_witnesses_2026-06-28_path1_path2_pfc_wm_state_tracker_drill_A_"
            "trajectory_schema_drill_B_redesigning_primitive_does_not_rescue_if_"
            "underlying_training_distribution_is_wrong_granularity_2026-06-28"
        ),
        name=(
            "META_RULE_AP v3 -- chain-grade primitives not trivially composable "
            "(PROMOTED CONFIRMED with NATIVE_OUTPUT_GRANULARITY clause; 4 "
            "witnesses 2026-06-28)"
        ),
        description=(
            "META_RULE_AP v3 promotion to fully chain-grade CONFIRMED with new "
            "NATIVE_OUTPUT_GRANULARITY clause. Discipline statement: "
            "(v1) Chain-grade primitives do not trivially compose into a chain-"
            "grade multi-primitive pipeline; SHAPE_MATCH + capacity-feasible at "
            "every edge are NECESSARY but not SUFFICIENT for end-to-end "
            "capability to emerge. "
            "(v2 amendment, this atom NATIVE_OUTPUT_GRANULARITY clause): "
            "Primitives compose only if their NATIVE output granularity matches "
            "the downstream primitive's expected INPUT granularity. Redesigning "
            "the upstream primitive's READOUT does NOT rescue composition if "
            "the underlying TRAINING DISTRIBUTION encodes the wrong granularity. "
            "Witness pattern 2026-06-28 (4 witnesses): "
            "(1) Path 1 partition-oracle brain-composition-hint HF: schema-"
            "Bayes + cortex-routing edges SHAPE_MATCH but per-hop discrimination "
            "below floor; "
            "(2) Path 2 partition-oracle per-chain-schema HF: schema fires once "
            "per chain; partition signal pinned to hop-0; "
            "(3) Drill A PFC-WM state-tracker HF: state injection cannot "
            "rescue when cluster_to_target_part[k] map is hop-0-locked (root "
            "cause is the cluster->partition map granularity, not the absence "
            "of state); "
            "(4) Drill B per-hop schema-Bayes redesign HF: even redesigning "
            "the primitive's output via per-(cluster,hop) trajectory store "
            "does NOT rescue if the underlying schema-Bayes training "
            "distribution does not learn partial-prefix cluster identity (the "
            "PRIMITIVE'S native output is full-chain cluster-id, not partial-"
            "prefix cluster-id; downstream consumer needs partial-prefix). "
            "Practical implications: "
            "(a) Before any 4-primitive composition cell, audit each edge for "
            "TRAINING DISTRIBUTION granularity match (NOT just inference-time "
            "SHAPE_MATCH); "
            "(b) If output-granularity mismatch is structural to the primitive "
            "(as in schema-Bayes full-chain vs partial-prefix), no readout "
            "redesign at the consumer side will fix it; the granularity must "
            "be addressed at the SOURCE primitive (re-train OR new primitive "
            "class); "
            "(c) The 2x-drill discipline applied at MECHANISM CLASS level "
            "(state-tracker injection vs primitive output redesign) is the "
            "correct closure pattern for this rule; both classes failing on "
            "the same capability is structural evidence the primitive set "
            "itself is the bottleneck. "
            "Composes with META_RULE_AO (3-mechanism-class HF closure) at the "
            "MULTI-CELL aggregation layer; AP-v3 fires at the per-cell smoke "
            "discriminator-design layer."
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "CONFIRMED",
            "instance_number": None,
            "confirmed_or_candidate": "CONFIRMED",
            "rule_id": "META_RULE_AP",
            "rule_version": "v3",
            "rule_class": (
                "compositional_capability_emergence_pre_design_discipline"
            ),
            "first_witness_date": "2026-06-28",
            "first_witness_capability": (
                "brain_faithful_4_primitive_multi_hop_chain_composition_at_"
                "substrate_native_bipolar_HRR"
            ),
            "first_witness_cells": [
                "exp_substrate_partition_oracle_brain_composition_hint_v1",
                "exp_substrate_partition_oracle_per_chain_schema_v1",
                "exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7",
                "exp_substrate_partition_oracle_trajectory_schema_per_hop_v1_seed_7",
            ],
            "new_clause_added_v3": "NATIVE_OUTPUT_GRANULARITY",
            "new_clause_statement_v3": (
                "Primitives compose only if their NATIVE output granularity "
                "matches the downstream primitive's expected INPUT granularity; "
                "redesigning the upstream primitive's READOUT does NOT rescue "
                "composition if the underlying TRAINING DISTRIBUTION encodes "
                "the wrong granularity"
            ),
            "preconditions_for_invocation": [
                "cell pre-reg involves 3+ chain-grade primitives composed end-to-end",
                "any edge requires the upstream primitive to deliver output at "
                "a granularity finer or different from its native training "
                "distribution (e.g. partial-prefix vs full-chain)",
            ],
            "discipline_action": (
                "in pre-reg signal-shape audit, add NATIVE_OUTPUT_GRANULARITY "
                "check per edge: 'does the upstream primitive's TRAINING "
                "distribution learn the granularity the downstream needs?' "
                "If NO, REJECT the composition or split into two cells "
                "(first cell: re-train upstream on the needed granularity; "
                "second cell: compose)"
            ),
            "composes_with": [
                "META_RULE_AF",   # arms-must-differ
                "META_RULE_AG",   # un-saturated band
                "META_RULE_AH",   # atomic-write + cardinality_ok
                "META_RULE_AL",   # encoding-before-readout
                "META_RULE_AN",   # cone-collapse extrapolation
                "META_RULE_AO",   # 3-mech-class HF closure (multi-cell layer)
            ],
            "supersedes": None,
            "supersedes_prior_version": "META_RULE_AP_v1 + v2 candidate (not formally atomized)",
            "atomized_by": "skunkworks",
            "atomized_session": (
                "skunkworks_2026-06-28_drill_b_capability_closure_AP_v3_promote"
            ),
        },
    )


def main():
    apply_mode = "--apply" in sys.argv
    if not apply_mode:
        print("USAGE: python tools/atomize_trajectory_schema_drill_b_capability_closed_2026-06-28.py --apply")
        print()
        a1 = build_drill_b_hf_atom()
        a2 = build_capability_closed_atom()
        a3 = build_meta_rule_ap_v3_atom()
        for i, a in enumerate([a1, a2, a3], 1):
            print(f"  {i}. {a.id[:120]}")
            print(f"     kind={a.kind.value} tier={a.tier.value} corpus={a.corpus.value}")
            md = a.metadata or {}
            print(f"     pq={md.get('provenance_quality')} cert_status={md.get('cert_status')} cert_class={md.get('cert_class')}")
        return 0

    # A5 PRE-snapshot
    ps = PartitionedStore(STORE_ROOT)
    cert_n_pre = sum(
        1 for a in ps.all_atoms()
        if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE'
    )
    print(f"A5 PRE: CERT_N={cert_n_pre}")

    # Atom 1: Drill B HF
    a1 = build_drill_b_hf_atom()
    qid1 = f"{a1.corpus.value}::{a1.id}"
    if ps.get_atom(qid1) is not None:
        print(f"SKIP a1 (idempotent): present")
    else:
        print(f"ADDING a1: {a1.id[:100]}...")
        ps.add_atom(a1,
            source="skunkworks_atomize_drill_b_trajectory_schema_HF_2026-06-28",
            note=(
                "Drill B trajectory_schema_per_hop_v1 HARD_FAIL; per-hop schema-"
                "Bayes redesign via sequence-binding S matrix does not rescue "
                "(k_pred vs k_train mismatch 92->0% across hops); MM "
                "characterization; verified-off-data via .venv recompute"
            ),
        )

    # Atom 2: capability-closed
    a2 = build_capability_closed_atom()
    qid2 = f"{a2.corpus.value}::{a2.id}"
    if ps.get_atom(qid2) is not None:
        print(f"SKIP a2 (idempotent): present")
    else:
        print(f"ADDING a2: {a2.id[:100]}...")
        ps.add_atom(a2,
            source="skunkworks_atomize_brain_faithful_4primitive_capability_closed_2x_drill_2026-06-28",
            note=(
                "Brain-faithful 4-primitive multi-hop chain composition "
                "CAPABILITY CLOSED per 2x-drill discipline (Drill A "
                "state-bias HF + Drill B primitive redesign HF); M3 needs "
                "external cortex layer for hint derivation; HONEST_NEGATIVE"
            ),
        )

    # Atom 3: META_RULE_AP v3
    a3 = build_meta_rule_ap_v3_atom()
    qid3 = f"{a3.corpus.value}::{a3.id}"
    if ps.get_atom(qid3) is not None:
        print(f"SKIP a3 (idempotent): present")
    else:
        print(f"ADDING a3: {a3.id[:100]}...")
        ps.add_atom(a3,
            source="skunkworks_atomize_META_RULE_AP_v3_NATIVE_OUTPUT_GRANULARITY_2026-06-28",
            note=(
                "META_RULE_AP v3 promote to CONFIRMED chain-grade; adds "
                "NATIVE_OUTPUT_GRANULARITY clause; 4 witnesses 2026-06-28 "
                "(Path1, Path2, Drill A, Drill B)"
            ),
        )

    # Fresh-Store round-trip verify
    ps2 = PartitionedStore(STORE_ROOT)
    all_atoms = list(ps2.all_atoms())
    for a in [a1, a2, a3]:
        found = next((x for x in all_atoms if x.id == a.id), None)
        assert found is not None, f"round-trip FAIL: {a.id[:80]}"
        assert found.kind == a.kind, f"kind mismatch {a.id[:80]}: {found.kind} != {a.kind}"
        assert found.tier == a.tier, f"tier mismatch {a.id[:80]}: {found.tier} != {a.tier}"
    print("PASS: round-trip survival OK for all 3 atoms")

    # A5 POST-snapshot
    cert_n_post = sum(
        1 for a in ps2.all_atoms()
        if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE'
    )
    expected_delta = 0  # MM + honest_neg + methodology_rule -> 0 cert delta
    actual_delta = cert_n_post - cert_n_pre
    print(f"A5 POST: CERT_N={cert_n_post} (delta={actual_delta}, expected={expected_delta})")
    assert actual_delta == expected_delta, (
        f"A5 violation: delta {actual_delta} != expected {expected_delta}"
    )

    # Cert-ledger rows: one for HF (MM), one for capability-closure (honest_negative)
    ledger_row_hf = build_honest_negative_row(
        atom_id=f"math::{a1.id}",
        cell_commit=None,
        notes_path=(
            "notes/exp_dev_verdict_trajectory_schema_per_hop_v1_smoke_HARD_FAIL_"
            "CAPABILITY_CLOSURE_2026-06-28.md"
        ),
        metrics_path=(
            "data/exp_substrate_partition_oracle_trajectory_schema_per_hop_v1_"
            "seed_7_smoke/metrics.json"
        ),
        verdict="HARD_FAIL",
        cert_class="mechanism_characterization",
        note=(
            "drill_b_trajectory_schema_per_hop_HARD_FAIL_k_pred_train_mismatch_"
            "trajectory_redesign_does_not_rescue_2026-06-28"
        ),
    )
    print(f"Appending HF ledger row: op={ledger_row_hf['op']} status={ledger_row_hf['cert_status']} delta={ledger_row_hf['cert_increment_delta']}")
    h1 = append_cert_ledger_row(
        ledger_row_hf,
        expected_cert_n_pre=cert_n_pre,
        expected_cert_n_post=cert_n_post,
    )
    print(f"HF ledger row appended; hash={h1}")

    # Ledger cert_class allowlist (cert_ledger_writer) is constrained; use the
    # closest match 'pre_reg_miss_proven_bound' (the capability closure IS a
    # pre-reg miss for the HARD_PASS band, proving the capability bound).
    # The ATOM metadata carries the precise cert_class
    # 'capability_closed_two_drill_discipline_satisfied' for queryability.
    ledger_row_closure = build_honest_negative_row(
        atom_id=f"math::{a2.id}",
        cell_commit=None,
        notes_path=(
            "notes/exp_dev_verdict_trajectory_schema_per_hop_v1_smoke_HARD_FAIL_"
            "CAPABILITY_CLOSURE_2026-06-28.md"
        ),
        metrics_path=(
            "data/exp_substrate_partition_oracle_trajectory_schema_per_hop_v1_"
            "seed_7_smoke/metrics.json"
        ),
        verdict="HARD_FAIL",
        cert_class="pre_reg_miss_proven_bound",
        note=(
            "brain_faithful_4_primitive_multi_hop_chain_composition_capability_"
            "closed_2x_drill_discipline_satisfied_drill_A_state_bias_drill_B_"
            "primitive_redesign_M3_needs_external_cortex_layer_2026-06-28_"
            "atom_carries_cert_class_capability_closed_two_drill_discipline_"
            "satisfied_ledger_uses_pre_reg_miss_proven_bound_per_allowlist"
        ),
    )
    print(f"Appending closure ledger row: op={ledger_row_closure['op']} status={ledger_row_closure['cert_status']} delta={ledger_row_closure['cert_increment_delta']}")
    h2 = append_cert_ledger_row(
        ledger_row_closure,
        expected_cert_n_pre=cert_n_pre,
        expected_cert_n_post=cert_n_post,
    )
    print(f"Closure ledger row appended; hash={h2}")

    print()
    print("=" * 80)
    print("ATOMIZE COMPLETE")
    print(f"  CERT_N: {cert_n_pre} -> {cert_n_post} (delta=0; MM + honest_negative + methodology_rule)")
    print(f"  Atoms: 3 (Drill B HF + capability-closed + META_RULE_AP v3 promote)")
    print(f"  Ledger hashes: HF={h1}  closure={h2}")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
