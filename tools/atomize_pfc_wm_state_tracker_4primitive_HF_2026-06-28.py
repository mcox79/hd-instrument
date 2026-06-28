"""
A5-gated atomization: pfc_wm_state_tracker_v1 4-primitive composition HARD_FAIL
+ META_RULE_AP_v2 witness-chain AMENDMENT adding PFC-WM as valid witness #3
(V_C-sweep Path 3 is RETRACTED per name-collision deep audit, so the
chronological chain is now Path 1, Path 2, PFC-WM 4-primitive).

Cell:   experiments/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7.py
Metrics:data/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7_smoke/metrics.json
Pre-reg:preregs/2026-06-28_substrate_partition_oracle_pfc_wm_state_tracker_v1.md
Verdict:HARD_FAIL_ARMS_TIED + HARD_FAIL_ALL_ADAPTERS_DEAD (all 3 dlPFC-WM-state-tracker
        adapter sub-mechanisms HF at top1=0.00; per-hop part-acc at chance ~0.19)

OFF-DATA RECOMPUTE (seed=7 smoke at FULL N=8192 V_C=4000 d=15 n_chains_test=100):
  A_BASELINE        top1=0.4000  (rail OK in [0.05,0.95])
  B_PATH2_PER_CHAIN top1=0.0100  part-mean=0.2093 (reproduces today's PATH 2 HF)
  C_SUB_A_PRIOR_MOD top1=0.0000  part-mean=0.1880  part_h5/h10/h15=0.19/0.12/0.23
  C_SUB_B_FAKE_EVID top1=0.0000  part-mean=0.1907  part_h5/h10/h15=0.22/0.18/0.23
  C_SUB_C_STATE_COND top1=0.0000 part-mean=0.1900  part_h5/h10/h15=0.22/0.18/0.23
  D_ORACLE_PER_HOP  top1=0.8400  (upper bound; sanity OK)
  E_RANDOM          top1=0.0000  (floor OK; <0.05)

lift_sub_X_over_A = -0.40 for all 3 adapters; lift_sub_X_over_B = -0.01 for all 3.
HF band trips: top1<=0.30 AND lift_over_B<0.10 (BOTH; per-spec ALL 3 adapters HF).
arms_distinct = FALSE (SUB_B and SUB_C share SHA-256 c6217c981403fdd3 -- collision
flagged separately by cell-author; structural cause is both reduce to
argmax-over-clusters followed by cluster_to_target_part lookup, which is
hop-0-only and therefore identical when both pickers route through the same map).
cardinality_ok = TRUE (7/7 arms observed).
baseline_rail_ok = TRUE.
saturated_any = FALSE.
zero LLM calls at inference.

MECHANISM DIAGNOSIS (load-bearing for capability closure):
  Schema-to-partition map cluster_to_target_part[k] is computed in
  build_schema_prototypes (cell line 322-330) from FIRST-HOP targets only:
    member_parts = [chains_train[ci][0][2] // PART_SIZE ...]   (line 324)
  The [0] indexes the first hop's tuple. Every schema cluster k maps to
  the HOP-0 target partition of its training chains. State-context bias
  from WM (SUB_A multiplicative / SUB_B fake-evidence / SUB_C state-
  conditioned schema-recompute) can shift WHICH cluster fires per hop,
  but ALL clusters' partition outputs encode hop-0 partitions, not per-
  hop trajectory partitions. Per-hop partition-acc caps at ~1/N_PARTS=0.20=chance.

  The dlPFC WM state-tracker primitive IS in the composition (4th primitive
  added per META_RULE_AQ rescue path), but the upstream schema-Bayes
  primitive itself produces only per-chain (or hop-0-anchored per-cluster)
  partition signal. Adding state-tracking on top of a primitive whose
  native output is too coarse for the test regime cannot rescue it.

VINDICATES META_RULE_AP_v2: this is a 3rd valid witness (chronologically
the latest) of composition-failure rooted in operating-regime / signal-
shape incompatibility. SUB_A pre-reg flagged SHAPE_MATCH (multiplicative)
but the SHAPE_MATCH was at the QUERY level not at the OUTPUT level --
upstream primitive's native output is structurally hop-0-only regardless
of multiplicative biasing. AP_v2 SCHEMA-VET in v3 should also check
upstream primitive's NATIVE OUTPUT SEMANTICS for per-step capability tests.

VINDICATES META_RULE_AQ: adding dlPFC WM state-tracker primitive did not
rescue the composition because the UPSTREAM primitive (schema-Bayes) is
ALSO per-chain (or hop-0) by construction. AQ rescue path "use substrate
wm multi-bank K4096 as state-tracker" was followed (WM bank K=200 used)
but the primitive composed-around is still too coarse. AQ v2 should add:
"state-tracker rescues only if upstream primitive's native output is
re-firable per-step with state-conditional discrimination -- not if
upstream primitive's native output is hop-0-anchored regardless of query."

CAPABILITY CLOSURE STATUS: NOT YET CLOSED.
Per feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28:
capability closure requires 2 drills both confirming null. Today we have:
  Drill A: PFC-WM 4-primitive state-tracker (THIS cell; HF; 3 adapter
           sub-mechanisms tested; all failed; same root cause -- upstream
           schema primitive too coarse).
  Drill B: PENDING -- research drill to re-design schema-Bayes primitive
           to output PER-HOP partition (mechanism class 5 = substantively
           different rescue path; not a parameter tune of Drill A).
If Drill B also HARD_FAILs, brain-faithful 4-primitive composition CLOSES
(per project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28
M3 then needs external cortex layer).

CERT delta: +0 (mechanism_characterization HARD_FAIL; honest-negative;
counts as a proven NEGATIVE result; does not increment chain-grade portfolio
count per Skunkworks cert-tiering convention; HARD_FAIL is its own cert
class and is the disposition for this atom).
"""

import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_pfc_wm_state_tracker_4primitive_HF_2026-06-28"
ATOMIZED_DATE = "2026-06-28"

CELL_PATH = "experiments/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7.py"
PREREG_PATH = "preregs/2026-06-28_substrate_partition_oracle_pfc_wm_state_tracker_v1.md"
METRICS_PATH = "data/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7_smoke/metrics.json"
VERDICT_NOTE_PATH = "notes/exp_dev_verdict_pfc_wm_state_tracker_smoke_HARD_FAIL_all_3_adapters_2026-06-28.md"

CELL_COMMIT = "uncommitted_at_atomize_time_head_6f8fef0e"

PATH_1 = "math::T3/EXP_partition_oracle_substrate_derived_hint_naive_centroid_composition_HARD_FAIL_2026-06-28"
PATH_2 = "math::T3/EXP_partition_oracle_brain_composition_hint_vmPFC_cortex_hippo_3primitive_HARD_FAIL_2026-06-28"
# PATH 3 V_C-sweep RETRACTED per audit aa6636aa8b1e9b89c -- name-collision (cell did not
# actually invoke partition_oracle_v5_hardened mechanism). Quarantine note:
# notes/orchestrator_to_skunkworks_V_C_sweep_RETRACT_name_collision_quarantine_2026-06-28.md
PFC_WM_4PRIM = (
    "math::T3/EXP_partition_oracle_pfc_wm_state_tracker_4primitive_composition_HARD_FAIL_all_3_adapter_"
    "sub_mechanisms_dead_state_tracker_cannot_rescue_hop0_anchored_upstream_schema_primitive_2026-06-28"
)

AP_V2_ATOM_ID = (
    "META_RULE_AP_v2_chain_grade_eligible_composition_of_chain_grade_primitives_requires_signal_shape_"
    "adapter_OR_co_training_OR_pre_cell_compatibility_audit_2_witness_threshold_MET_witness_1_partition_"
    "oracle_substrate_derived_hint_v1_seed_7_HF_route_acc_at_chance_witness_2_narrative_partition_oracle_"
    "V_C_sweep_v1_seed_7_HF_oracle_Q2_at_floor_across_full_V_C_sweep_both_witnesses_show_same_failure_"
    "class_input_output_signal_shape_OR_operating_regime_incompatibility_between_chain_grade_primitive_"
    "validated_regime_AND_downstream_task_regime_SCHEMA_VET_directive_active_supersedes_v1_2026-06-28"
)


pfc_wm_atom = {
    "id": (
        "T3/EXP_partition_oracle_pfc_wm_state_tracker_4primitive_composition_HARD_FAIL_all_3_adapter_"
        "sub_mechanisms_dead_state_tracker_cannot_rescue_hop0_anchored_upstream_schema_primitive_2026-06-28"
    ),
    "name": (
        "Partition-oracle PFC-WM state-tracker v1 seed_7 smoke at FULL N=8192 d=15 -- "
        "HARD_FAIL_ARMS_TIED + HARD_FAIL_ALL_ADAPTERS_DEAD (4-primitive composition vmPFC schema-Bayes + "
        "dlPFC WM state-tracker + cortex partition + hippo cleanup; all 3 adapter sub-mechanisms "
        "PRIOR_MODULATION / FAKE_EVIDENCE / STATE_CONDITIONED_SCHEMA at top1=0.00; per-hop partition-"
        "correct at chance ~0.19; structural cause: upstream schema-to-partition map is hop-0-anchored "
        "in build_schema_prototypes line 324 -- state-tracker cannot rescue what upstream primitive "
        "cannot produce per-hop)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "M3 Barrier 1 break-candidate Drill A (4-primitive brain-faithful composition with explicit state-"
        "tracker) -- HARD_FAIL_ARMS_TIED with HARD_FAIL_ALL_ADAPTERS_DEAD also satisfied. "
        ""
        "COMPOSITION: vmPFC schema-Bayes (chain-grade schema_exemplar_bayes_ANCHOR_3 K_NEAREST_K20=0.728) "
        "+ dlPFC WM state-tracker (Frady-Sommer 2020 outer-product slot bank K=200; per-hop write of "
        "bound state, per-hop read for context-bias) + cortex partition argmax (M=10M routing_acc=0.97) "
        "+ hippo restricted cleanup over predicted partition E_part. The 4th primitive (dlPFC WM) is the "
        "META_RULE_AQ rescue path explicitly applied. "
        ""
        "REGIME: FULL N=8192 V_C=4000 V_P=10 depth=15 n_parts=5 part_size=800 n_schemas=20 wm_bank_K=200 "
        "n_chains_train=200 n_chains_test=100 (smoke); single seed=7 (chunked sibling design); encoder = "
        "SUBSTRATE_NATIVE_BIPOLAR (Path C compliant; zero LLM calls at inference). "
        ""
        "ARMS (7; cardinality_ok=True; expected_units=7 observed=7): "
        "A BASELINE per-hop cleanup over full V_C; B PATH2_PER_CHAIN (3-primitive reproducing today's HF); "
        "C_SUB_A PRIOR_MODULATION (WM state multiplies schema posterior; SHAPE_MATCH multiplicative); "
        "C_SUB_B FAKE_EVIDENCE (WM slot appended to evidence-set with harmonic-decay weight); "
        "C_SUB_C STATE_CONDITIONED_SCHEMA (per-hop schema vector recomputed with WM as superposed slot); "
        "D ORACLE_PER_HOP (upper bound); E RANDOM (floor). "
        ""
        "OFF-DATA RECOMPUTE (independent verify; seed=7 n_chains_test=100): "
        "A=0.4000 (rail OK in [0.05,0.95]); B=0.0100 (reproduces PATH 2 HF MEASURED@0.01); "
        "C_SUB_A=0.0000 lift_A=-0.40 lift_B=-0.01 part_h5/h10/h15=0.19/0.12/0.23 part_mean=0.1880; "
        "C_SUB_B=0.0000 lift_A=-0.40 lift_B=-0.01 part_h5/h10/h15=0.22/0.18/0.23 part_mean=0.1907; "
        "C_SUB_C=0.0000 lift_A=-0.40 lift_B=-0.01 part_h5/h10/h15=0.22/0.18/0.23 part_mean=0.1900; "
        "D=0.8400 (sanity; upper bound matches v5_hardened MEASURED@0.835-0.90); E=0.0000 (floor OK). "
        ""
        "BAND VERDICT (per pre-reg locked at module init): all 3 adapters trip HARD_FAIL "
        "(top1<=HF_ABS=0.30 AND lift_over_B<HF_LIFT_B=0.10); whole-cell HARD_FAIL satisfied. "
        "Additionally HARD_FAIL_ARMS_TIED trips FIRST: arms_distinct=False because SUB_B and SUB_C "
        "produce IDENTICAL SHA-256 (c6217c981403fdd3). Other 5 arms have distinct hashes. "
        ""
        "MECHANISM DIAGNOSIS (verified off-data from cell source; lines 286-332 build_schema_prototypes): "
        "  cluster_to_target_part[k] = argmax_p(counts of member_parts) where "
        "  member_parts = [chains_train[ci][0][2] // PART_SIZE ...]  -- the [0] indexes the FIRST hop's "
        "  tuple. Every schema cluster k maps to HOP-0 target partition of its training chains. State- "
        "  context bias from WM (SUB_A/B/C) shifts WHICH cluster fires per hop but ALL clusters' "
        "  partition outputs encode hop-0 partitions, NOT per-hop trajectory partitions. Per-hop "
        "  partition-acc caps at 1/N_PARTS=0.20=chance. Observed h5/h10/h15 in [0.12, 0.28] cluster around "
        "  chance, confirming structural cap. "
        ""
        "SUB_B === SUB_C COLLISION ROOT CAUSE: at the argmax-over-clusters stage, both pickers reduce "
        "to picking ONE cluster and routing through cluster_to_target_part[k]. SUB_B uses "
        "(q_hop + w*wm_state) with harmonic decay; SUB_C uses (sum_{j<=i} R[p_j] + wm_state). When "
        "both reduce to identical argmax inputs at the partition-vote stage (because both happen to "
        "select the same cluster on every test chain), they produce identical per-step accuracy "
        "sequences and identical SHA-256 hashes. This is NOT a code bug per se -- it is a NATURAL "
        "CONSEQUENCE of both adapters routing through the same hop-0-anchored cluster->partition map. "
        ""
        "RULE-OUTS: ingest bug ruled out (D=0.84 with same W); cleanup bug ruled out (D=0.84 uses same "
        "E_part subspace); schema-prototype construction ruled out (cell selftest passes; B at 0.01 "
        "matches PATH 2 historical regression); WM bank ruled out as load-bearing failure (the K=200 "
        "outer-product slot bank itself is FR1+FR2 chain-grade-eligible per WM_MULTIBANK_K_CLIFF_K4096 "
        "MEASURED@>0.95 retrieval; per-hop reads here are not the bottleneck). Failure is structural: "
        "upstream primitive (schema-Bayes -> partition map) is hop-0-only by construction. "
        ""
        "M3 IMPLICATION: 4-primitive brain-faithful composition with state-tracker FAILS when upstream "
        "primitive's native output is structurally too coarse for the test regime. Rescue paths from "
        "drill Rank 3 fallback (see verdict note): (1) re-design schema-Bayes primitive to output "
        "PER-HOP partition (option 3; substantively different mechanism class; queued as Drill B for "
        "capability-closure 2x-drill threshold); (2) per-state schema selector (option 1; Sutton-Precup "
        "analog; needs per-state-trained policies); (3) external cortex layer (option 2; non-brain-"
        "faithful; per project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28). "
        ""
        "CAPABILITY CLOSURE STATUS: NOT YET CLOSED. Per feedback_2x_drill_negatives_before_capability_"
        "closure_USER_2026-06-28, capability closure requires 2 drills both confirming null. Drill A = "
        "THIS cell (HF). Drill B = research drill to re-design schema-Bayes primitive (PENDING). If "
        "Drill B also HF, brain-faithful 4-primitive composition closes and M3 cortex-layer path "
        "promoted. "
        ""
        "META_RULE_AP_v2 WITNESS: this cell is the 3rd VALID witness (chronologically the latest) of "
        "composition-failure rooted in operating-regime / signal-shape incompatibility. Path 3 V_C-sweep "
        "is RETRACTED per name-collision deep audit (Skunkworks aa6636aa8b1e9b89c; quarantine note "
        "orchestrator_to_skunkworks_V_C_sweep_RETRACT_name_collision_quarantine_2026-06-28). Valid "
        "chronological chain is now: Path 1 substrate-derived hint -> Path 2 vmPFC+cortex+hippo "
        "3-primitive -> PFC-WM 4-primitive (this cell). 3-witness threshold for AP_v2 is preserved "
        "via PFC-WM swap; AP_v2 enforcement (SCHEMA-VET HARD GATE) unchanged. PFC-WM additionally "
        "refines AP_v2 sub-claim: SHAPE_MATCH at QUERY level (SUB_A multiplicative) is insufficient "
        "when upstream primitive's NATIVE OUTPUT SEMANTICS are too coarse -- future AP_v3 SCHEMA-VET "
        "should require upstream primitive NATIVE OUTPUT SEMANTICS audit for per-step capability tests. "
        ""
        "META_RULE_AQ WITNESS: this cell is the 2nd witness of iterated-state-tracker discipline. "
        "Witness 1 (Path 2) had NO state-tracker; witness 2 (PFC-WM this cell) HAS explicit state-"
        "tracker AND still HF -- demonstrating that AQ rescue path 'add state-tracker' is necessary "
        "but NOT sufficient. AQ v2 should add: state-tracker rescues only if upstream primitive's "
        "native output is re-firable per-step with state-conditional discrimination. AQ promotion to "
        "chain-grade-eligible meta_discipline now has 2-witness threshold MET; promotion is a separate "
        "amendment (not in this atom)."
    ),
    "aliases": [
        "pfc_wm_state_tracker_4primitive_composition_HARD_FAIL_2026-06-28",
        "substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7_HF",
        "barrier_1_M3_4primitive_brain_faithful_composition_with_state_tracker_dead",
        "drill_A_capability_closure_2x_drill_first_negative_2026-06-28",
        "META_RULE_AP_v2_witness_3_PFC_WM_replaces_V_C_sweep_retracted",
        "META_RULE_AQ_witness_2_state_tracker_necessary_not_sufficient",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "hard_fail",
        "cert_class": "mechanism_characterization",
        "verdict": "HARD_FAIL_ARMS_TIED_PLUS_HARD_FAIL_ALL_ADAPTERS_DEAD",
        "verdict_subtype": (
            "FOUR_PRIMITIVE_BRAIN_FAITHFUL_COMPOSITION_WITH_DLPFC_WM_STATE_TRACKER_FAILS_ALL_3_ADAPTER_"
            "SUB_MECHANISMS_TIED_AT_ZERO_TOP1_PER_HOP_PARTITION_ACCURACY_AT_CHANCE_DUE_TO_HOP_0_ANCHORED_"
            "UPSTREAM_SCHEMA_TO_PARTITION_MAP_STATE_TRACKER_CANNOT_RESCUE_UPSTREAM_PRIMITIVE_TOO_COARSE"
        ),
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "cell_commit": CELL_COMMIT,
        "cell_path": CELL_PATH,
        "prereg_path": PREREG_PATH,
        "metrics_path": METRICS_PATH,
        "verdict_note_path": VERDICT_NOTE_PATH,
        "verified_off_data": True,
        "regime": {
            "N_DIM": 8192,
            "V_CONCEPTS": 4000,
            "V_PRED": 10,
            "DEPTH": 15,
            "N_PARTS": 5,
            "PART_SIZE": 800,
            "N_SCHEMAS": 20,
            "WM_BANK_K": 200,
            "n_chains_train": 200,
            "n_chains_test": 100,
            "seeds": [7],
            "run_mode": "smoke",
            "encoder": "SUBSTRATE_NATIVE_BIPOLAR",
            "llm_calls_at_inference": 0,
        },
        "per_arm_top1": {
            "arm_a_baseline": 0.4000,
            "arm_b_path2_per_chain": 0.0100,
            "arm_c_sub_a_prior_modulation": 0.0000,
            "arm_c_sub_b_fake_evidence": 0.0000,
            "arm_c_sub_c_state_conditioned": 0.0000,
            "arm_d_oracle_per_hop": 0.8400,
            "arm_e_random": 0.0000,
        },
        "per_arm_partition_correct_mean": {
            "arm_b_path2_per_chain": 0.2093,
            "arm_c_sub_a_prior_modulation": 0.1880,
            "arm_c_sub_b_fake_evidence": 0.1907,
            "arm_c_sub_c_state_conditioned": 0.1900,
        },
        "per_arm_partition_correct_h5_h10_h15": {
            "arm_b_path2_per_chain": [0.20, 0.20, 0.24],
            "arm_c_sub_a_prior_modulation": [0.19, 0.12, 0.23],
            "arm_c_sub_b_fake_evidence": [0.22, 0.18, 0.23],
            "arm_c_sub_c_state_conditioned": [0.22, 0.18, 0.23],
        },
        "lifts": {
            "lift_sub_a_over_a": -0.4000,
            "lift_sub_a_over_b": -0.0100,
            "lift_sub_b_over_a": -0.4000,
            "lift_sub_b_over_b": -0.0100,
            "lift_sub_c_over_a": -0.4000,
            "lift_sub_c_over_b": -0.0100,
            "gap_d_minus_max_adapter": 0.8400,
        },
        "discipline_gates_observed": {
            "cardinality_ok": True,
            "expected_units": 7,
            "observed_units": 7,
            "baseline_rail_ok": True,
            "saturated_any": False,
            "arms_distinct": False,
            "arms_distinct_collision_pair": ["arm_c_sub_b_fake_evidence", "arm_c_sub_c_state_conditioned"],
            "arms_distinct_collision_sha256": "c6217c981403fdd3",
            "discriminator_survived_scale": True,
            "smoke_at_full_n_full_depth": True,
        },
        "mechanism_diagnosis": {
            "root_cause": "upstream_schema_to_partition_map_hop_0_anchored_by_construction",
            "evidence_line": "experiments/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7.py line 324",
            "evidence_code": "member_parts = [chains_train[ci][0][2] // PART_SIZE for ci ... ]",
            "structural_cap_per_hop_partition_acc": 0.20,
            "observed_per_hop_partition_acc_h5_to_h15_range": [0.12, 0.28],
            "state_tracker_primitive_present": True,
            "state_tracker_primitive_chain_grade_separately": "WM_MULTIBANK_K_CLIFF_K4096_retrieval_MEASURED_above_0p95",
            "rescue_paths_not_exhausted": [
                "redesign_schema_bayes_to_output_per_hop_partition_drill_B_pending",
                "per_state_schema_selector_Sutton_Precup_analog",
                "external_cortex_layer_M3_non_brain_faithful_fallback",
            ],
        },
        "capability_closure_status": "NOT_YET_CLOSED_pending_drill_B",
        "two_x_drill_status": {
            "drill_A_this_cell": "HARD_FAIL",
            "drill_B_pending": "research_drill_to_redesign_schema_bayes_primitive_for_per_hop_partition_output",
            "closure_triggers_if_drill_B_also_HARD_FAIL": True,
        },
        "discipline_compliance": [
            "META_RULE_AC_number_tagging",
            "META_RULE_AE_absolute_paths",
            "META_RULE_AF_arms_must_differ_sha256_VIOLATED_SUB_B_eq_SUB_C",
            "META_RULE_AG_discriminator_at_edge_of_capacity",
            "META_RULE_AH_atomic_metrics_json",
            "META_RULE_AL_HP_HF_bands_locked_at_import",
            "META_RULE_AN_substrate_empirical_anchor_path_2_measured_0p01",
            "META_RULE_AP_v2_signal_shape_audit_present_in_prereg",
            "META_RULE_AQ_state_tracker_present_4th_primitive",
            "META_RULE_H_cardinality_ok_expected_units_7",
            "META_RULE_T_per_arm_metric_verification_required_pre_atomization",
            "Fix28_per_arm_metrics_not_summary_verdict_text",
            "BIAS-N_per_arm_metrics_in_summary",
            "BIAS-Q_saturation_guard_at_0p95",
            "BIAS-S_baseline_rail_0p05_to_0p95",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_smoke_at_full_N_full_depth",
            "PROT-018_config_version_binding",
            "PROT-021_anchor_stamp_partial_load_guard",
            "PATH_C_substrate_native_encoder_only_zero_LLM_at_inference",
        ],
        "AP_v2_witness_role": "valid_witness_3_chronological_after_V_C_sweep_RETRACT",
        "AQ_witness_role": "witness_2_state_tracker_necessary_not_sufficient_promotes_AQ_to_2_witness_threshold",
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# AP_v2 amendment: replace witness #3 (V_C-sweep retracted) with PFC-WM 4-primitive
ap_v2_amendment_atom = {
    "id": (
        "META_RULE_AP_v2_witness_chain_amendment_replace_witness_3_V_C_sweep_RETRACTED_with_PFC_WM_4primitive_"
        "state_tracker_HF_full_chain_now_path1_substrate_derived_hint_path2_vmPFC_cortex_hippo_3primitive_path3_"
        "PFC_WM_4primitive_state_tracker_all_converge_on_upstream_primitive_output_semantics_too_coarse_for_"
        "per_step_capability_test_AP_v2_promotion_threshold_3_witnesses_preserved_2026-06-28"
    ),
    "name": (
        "META_RULE_AP_v2 witness-chain AMENDMENT (2nd): replace witness #3 (narrative V_C-sweep RETRACTED "
        "per name-collision deep audit aa6636aa8b1e9b89c) with PFC-WM 4-primitive state-tracker HF. Valid "
        "chronological chain is now Path 1 -> Path 2 -> PFC-WM. AP_v2 chain-grade-eligible promotion "
        "threshold preserved. Refines AP_v2: state-tracker rescue path INSUFFICIENT when upstream "
        "primitive's NATIVE OUTPUT SEMANTICS are too coarse -- AP_v3 SCHEMA-VET candidate"
    ),
    "corpus": "meta",
    "tier": "T_methodology",
    "kind": "discipline_rule_amendment",
    "description": (
        "SECOND AMENDMENT to META_RULE_AP_v2 witness chain (first amendment added Path 2; this amendment "
        "replaces Path 3 V_C-sweep with PFC-WM 4-primitive). "
        ""
        "RETRACTION CONTEXT: orchestrator_to_skunkworks_V_C_sweep_RETRACT_name_collision_quarantine_"
        "2026-06-28.md (Skunkworks deep audit aa6636aa8b1e9b89c) found that "
        "exp_substrate_narrative_partition_oracle_V_C_sweep_v1 contained a NAME-COLLISION arm labeled "
        "ARM_PARTITION_ORACLE_Q2 that did NOT actually invoke the chain-grade partition_oracle_v5_hardened "
        "mechanism. The cell's atom (math::T3/EXP_narrative_partition_oracle_V_C_sweep_HARD_FAIL_Q2_no_V_C_"
        "cliff_2026-06-28) is to be retraction-annotated as cert_class=RETRACTED_NAME_COLLISION_NOT_ACTUAL_"
        "PARTITION_ORACLE_INVOCATION. As a consequence, the V_C-sweep cell is NOT a valid composition-"
        "failure observation -- the cell never composed the chain-grade primitive. AP_v2 witness-chain "
        "must drop V_C-sweep. "
        ""
        "NEW WITNESS #3 (replaces V_C-sweep): PFC-WM 4-primitive state-tracker HF "
        "  - Composition: brain-faithful 4-primitive (vmPFC schema-Bayes + dlPFC WM state-tracker + "
        "    cortex partition + hippo cleanup) at FULL N=8192 V_C=4000 d=15 with 3 adapter sub-mechanisms "
        "    tested in parallel (PRIOR_MODULATION / FAKE_EVIDENCE / STATE_CONDITIONED_SCHEMA). "
        "  - Result: A=0.40 (rail OK); B=0.01 (PATH 2 HF reproduction); C_SUB_A/B/C all 0.00 with per-hop "
        "    partition-correct at chance ~0.19; D=0.84 (sanity); E=0.00 (floor). HARD_FAIL_ARMS_TIED + "
        "    HARD_FAIL_ALL_ADAPTERS_DEAD. Cell atom: math::T3/EXP_partition_oracle_pfc_wm_state_tracker_"
        "    4primitive_composition_HARD_FAIL_all_3_adapter_sub_mechanisms_dead_state_tracker_cannot_"
        "    rescue_hop0_anchored_upstream_schema_primitive_2026-06-28. "
        "  - Diagnosis: upstream schema-to-partition map cluster_to_target_part is hop-0-anchored "
        "    (build_schema_prototypes line 324: member_parts uses chains_train[ci][0][2]). State-context "
        "    bias shifts WHICH cluster fires but ALL clusters' partition outputs encode hop-0 partitions. "
        "    Adding state-tracker primitive (the AQ rescue path) is NECESSARY but NOT SUFFICIENT when "
        "    upstream primitive's NATIVE OUTPUT SEMANTICS are too coarse for per-hop discrimination. "
        ""
        "VALID CHAIN (post-amendment, chronological): "
        "  Witness #1: Path 1 partition_oracle_substrate_derived_hint_v1_seed_7 HF "
        "              (naive centroid composition; route_acc=0.2173 at chance 0.20). "
        "  Witness #2: Path 2 partition_oracle_brain_composition_hint_v1_seed_7 HF "
        "              (3-primitive vmPFC+cortex+hippo NO state-tracker; arm_c top1=0.01). "
        "  Witness #3: PFC-WM partition_oracle_pfc_wm_state_tracker_v1_seed_7 HF (THIS amendment) "
        "              (4-primitive WITH state-tracker; 3 adapter sub-mechanisms all HF top1=0.00). "
        "RETRACTED: V_C-sweep witness (name-collision; was witness #3 in prior amendment). "
        ""
        "WITNESS DIVERSITY (post-amendment 3-witness): 3 distinct primitives (naive centroid / vmPFC-"
        "schema-Bayes-cortex-hippo 3-prim / same + dlPFC WM 4-prim with 3 adapter variants); 3 distinct "
        "designs (Path 1 single-primitive routing; Path 2 single-shot composition; Path 3 iterated "
        "composition with explicit state-tracker); 3 distinct failure surfaces (cascade death / single-"
        "decision-15-uses mismatch / state-tracker-cannot-rescue-coarse-upstream). All 3 converge on the "
        "SAME root cause: composition-time semantic-shape compatibility between primitive outputs and "
        "downstream-task requirements. AP discipline is robust across 3 progressively more sophisticated "
        "composition designs. "
        ""
        "AP_v2 SUB-CLAIM REFINEMENT (PFC-WM specific): SHAPE_MATCH at QUERY level (e.g., SUB_A "
        "multiplicative WM-state biasing schema posterior) is INSUFFICIENT when upstream primitive's "
        "NATIVE OUTPUT SEMANTICS are structurally too coarse. AP_v3 SCHEMA-VET candidate gate (not yet "
        "promoted): require pre-reg to declare upstream primitive's NATIVE OUTPUT GRANULARITY (per-chain "
        "/ per-cluster / per-step / per-token / etc) and downstream-task REQUIRED GRANULARITY. Mismatch "
        "in granularity is a separate failure class from signal-shape mismatch at query level. "
        ""
        "AP_v2 ENFORCEMENT (unchanged): SCHEMA-VET HARD GATE; prereg must declare upstream-output-shape "
        "+ downstream-input-shape + compatibility argument OR adapter mechanism OR co-training plan. "
        "This amendment ONLY corrects the witness chain and adds a sub-claim refinement; does not change "
        "rule semantics or enforcement. Promotion to AP_v3 is a SEPARATE FUTURE amendment if a 4th "
        "witness lands or if Drill B confirms NATIVE-OUTPUT-GRANULARITY is a load-bearing audit field. "
        ""
        "CERT delta = 0 (amendment-only; no new rule promotion)."
    ),
    "aliases": [
        "AP_v2_chain_amendment_2_replace_V_C_sweep_with_PFC_WM_4primitive_2026-06-28",
        "META_RULE_AP_v2_witness_chain_post_retraction_correction",
        "AP_v3_candidate_NATIVE_OUTPUT_GRANULARITY_gate_proposed_pending_4th_witness",
    ],
    "metadata": {
        "provenance_quality": "AMENDMENT_TO_AP_V2",
        "cert_status": "amendment_record",
        "cert_class": "meta_discipline_amendment",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "amends_atom_id": f"meta::{AP_V2_ATOM_ID}",
        "supersedes_witness_chain_in_prior_amendment": (
            "meta::META_RULE_AP_v2_witness_chain_amendment_witness_3_path_2_brain_composition_vmPFC_cortex_"
            "hippo_3primitive_HF_added_to_chain_initial_AP_v2_atom_listed_path1_and_path3_only_path2_landed_"
            "chronologically_2nd_today_commit_1513e314_amendment_brings_total_chain_to_3_witnesses_2026-06-28"
        ),
        "full_witness_chain_chronological_post_amendment": [
            PATH_1,
            PATH_2,
            PFC_WM_4PRIM,
        ],
        "retracted_witness_atom_id": (
            "math::T3/EXP_narrative_partition_oracle_V_C_sweep_HARD_FAIL_Q2_no_V_C_cliff_2026-06-28"
        ),
        "retraction_reason": "name_collision_deep_audit_aa6636aa8b1e9b89c_cell_did_not_invoke_chain_grade_partition_oracle_v5_hardened",
        "retraction_quarantine_note": (
            "notes/orchestrator_to_skunkworks_V_C_sweep_RETRACT_name_collision_quarantine_2026-06-28.md"
        ),
        "witness_chain_diversity_check": (
            "3 distinct primitives + 3 distinct composition designs (single-primitive / single-shot multi-"
            "primitive / iterated multi-primitive with state-tracker) + 3 distinct failure surfaces -- "
            "all converge on composition-time semantic-shape compatibility root cause"
        ),
        "AP_v3_candidate_proposal": {
            "proposed_new_audit_field": "upstream_primitive_native_output_granularity",
            "proposed_compatibility_check": "native_output_granularity_must_match_or_exceed_downstream_task_required_granularity",
            "promotion_trigger": "4th_witness_landing_OR_drill_B_confirms_granularity_audit_load_bearing",
        },
        "cert_increment_delta": 0,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


pfc_wm_ledger_row = {
    "ts": time.time(),
    "op": "atomize_experiment_HF_mechanism_characterization",
    "atom_id": f"math::{pfc_wm_atom['id']}",
    "cert_status": "hard_fail",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "HARD_FAIL_ARMS_TIED_PLUS_HARD_FAIL_ALL_ADAPTERS_DEAD_4primitive_brain_faithful_composition_with_"
        "dlPFC_WM_state_tracker_all_3_adapter_sub_mechanisms_dead_top1_zero_per_hop_partition_at_chance_"
        "upstream_schema_to_partition_map_hop_0_anchored_state_tracker_cannot_rescue_coarse_upstream_"
        "primitive_capability_closure_pending_drill_B"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "cell_path": CELL_PATH,
        "prereg_path": PREREG_PATH,
        "metrics_path": METRICS_PATH,
        "verdict_note_path": VERDICT_NOTE_PATH,
        "ap_v2_witness_role": "valid_witness_3_chronological",
        "aq_witness_role": "witness_2_state_tracker_necessary_not_sufficient",
        "drill_A_for_capability_closure": True,
        "drill_B_pending": "research_drill_redesign_schema_bayes_per_hop_partition_output",
    },
    "supersedes": None,
    "note": (
        "PFC_WM_4primitive_state_tracker_HF_drill_A_AP_v2_valid_witness_3_AQ_witness_2_capability_closure_pending_drill_B"
    ),
}


ap_amendment_ledger_row = {
    "ts": time.time(),
    "op": "meta_rule_amendment_witness_chain_correction",
    "atom_id": f"meta::{ap_v2_amendment_atom['id']}",
    "cert_status": "amendment_record",
    "cert_class": "meta_discipline_amendment",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": "amendment_to_AP_v2_post_V_C_sweep_retraction",
    "verdict": (
        "META_RULE_AP_v2_witness_chain_amendment_2_replace_witness_3_V_C_sweep_RETRACTED_name_collision_"
        "with_PFC_WM_4primitive_state_tracker_HF_valid_chain_now_path1_path2_PFC_WM_AP_v2_promotion_threshold_3_"
        "witnesses_preserved_AP_v3_NATIVE_OUTPUT_GRANULARITY_candidate_proposed_pending_4th_witness"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "amends_atom_qualified_id": f"meta::{AP_V2_ATOM_ID}",
        "amendment_atom_qualified_id": f"meta::{ap_v2_amendment_atom['id']}",
        "valid_witness_chain": [PATH_1, PATH_2, f"math::{pfc_wm_atom['id']}"],
        "retracted_witness": (
            "math::T3/EXP_narrative_partition_oracle_V_C_sweep_HARD_FAIL_Q2_no_V_C_cliff_2026-06-28"
        ),
    },
    "supersedes": None,
    "note": (
        "AP_v2_chain_amendment_2_V_C_sweep_swap_PFC_WM_4primitive_AP_v3_granularity_candidate"
    ),
}


def append_jsonl_a5(path: Path, new_row: dict, label: str):
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"missing: {path}"
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
            raise RuntimeError(f"PRE integrity fail at line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed = json.loads(new_line)
    if "id" in new_row:
        assert parsed["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert parsed["atom_id"] == new_row["atom_id"]

    out = "\n".join(pre_lines + [new_line]) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(out)
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp), str(path))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    assert len(post_lines) == pre_count + 1, f"line-count mismatch pre={pre_count} post={len(post_lines)}"
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
            raise RuntimeError(f"POST integrity fail at line {i+1}: {e}")
    print(f"[A5] {label}: OK post_count={len(post_lines)}")


def main():
    print(f"[A5] PFC-WM HF + AP_v2 amendment 2 START {ATOMIZED_BY}")
    append_jsonl_a5(MATH_ATOMS, pfc_wm_atom, "math/atoms.jsonl [PFC_WM_4primitive_HF]")
    append_jsonl_a5(META_ATOMS, ap_v2_amendment_atom, "meta/atoms.jsonl [AP_v2_amendment_2]")
    append_jsonl_a5(CERT_LEDGER, pfc_wm_ledger_row, "meta/cert_ledger.jsonl [PFC_WM_HF_ledger]")
    append_jsonl_a5(CERT_LEDGER, ap_amendment_ledger_row, "meta/cert_ledger.jsonl [AP_v2_amendment_2_ledger]")
    print(f"[A5] DONE. CERT delta = 0 (HF mechanism_characterization + amendment-only)")


if __name__ == "__main__":
    main()
