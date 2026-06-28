"""
A5-gated atomize: substrate_partition_oracle_brain_composition_hint_v1_seed_7 HARD_FAIL
+ META_RULE_AQ (multi-step composition requires explicit state-tracker primitive).

Verdict: HARD_FAIL_COMPOSITION_COLLAPSE.
Cert class: mechanism_characterization. CERT delta = 0 (HF).
This atom ALSO PROMOTES META_RULE_AP from cert-neutral to chain-grade
(2nd independent witness; AP promotion criterion satisfied).

OFF-DATA recompute (verify-OFF-DATA, NOT verdict_msg):
  A=0.40 B=0.00 C=0.01 D=0.84 E=0.01 F=0.00
  lift_C_A=-0.39 lift_C_B=+0.01 lift_C_E=0.00 lift_C_F=+0.01
  gap_D_C=0.83
  PATH2 partition-correct-per-step mean = 0.2093 (vs 1/5=0.20 chance = +0.009 ~chance)
  PATH1 partition-correct-per-step mean = 0.1813
  SCHEMA_ONLY partition-correct-per-step mean = 0.1953
  ORACLE partition-correct-per-step mean = 1.0 (sanity: oracle picks correct partition)
  arms_distinct=True (6 unique SHA-256), cardinality_ok=True (6/6)
  saturation=False rail_A in [0.30,0.70]=True

Mechanism diagnosis (load-bearing for AQ + 2nd witness for AP):
  PATH 2 mechanism: schema vector = bipolar(sum of all 15 hop predicates) -> argmax
  over 20 schema-prototype clusters -> static cluster->partition map (FR1+FR2).
  At inference, schema is computed ONCE per chain (vmPFC abstracts whole task);
  predicted partition is SAME for all 15 hops.

  But each of the 15 hops targets a DIFFERENT partition (chain target_o varies
  per hop). A single static partition prediction can be correct for AT MOST
  1/15 of hops on average -- and we observe ~chance partition-correctness (0.209
  vs 0.20). This is BOTH:
    (i) signal-shape compatibility issue (training distribution = 1st-hop tuples;
        inference distribution = arbitrary hops 2..15 with novel (s_pred, p_next)
        pairs OOD relative to schema training) -- this is the AP failure mode.
    (ii) iterated-state mismatch (the 3-primitive composition has no per-hop
        state-tracker; schema fires ONCE, partition decided ONCE, but the test
        regime requires 15 sequential partition decisions) -- this is a NEW
        mechanism-class failure: missing iterated state-tracker primitive.

  AQ candidate: brain-grounded multi-primitive compositions for multi-hop /
  multi-step capabilities require an EXPLICIT STATE-TRACKER primitive (per-step
  working-memory of accumulated context) that re-fires the upstream primitives
  per step. Single-shot composition fails when the "fire mechanism once"
  assumption doesn't match the iterated test regime. Maps to dorsolateral PFC
  working-memory in brain anatomy; substrate has WM multi-bank K=4096 chain-
  grade primitive but it was NOT included in this 3-primitive composition.

A5 protocol:
  1. PRE: read full file + count + parse all lines
  2. Append HF atom to math/atoms.jsonl via tmp -> os.replace
  3. Append META_RULE_AQ atom to meta/atoms.jsonl via tmp -> os.replace
  4. Append META_RULE_AP-PROMOTION ledger row (cert-neutral -> chain-grade meta) to meta/cert_ledger.jsonl
  5. Append 2 cert_ledger rows for HF + AQ to meta/cert_ledger.jsonl
  6. POST: verify-load: count delta + tail-line parses + round-trip ID match + every-line integrity

Anchors:
  - metrics: data/exp_substrate_partition_oracle_brain_composition_hint_v1_seed_7_smoke/metrics.json
  - prereg:  preregs/2026-06-28_substrate_partition_oracle_brain_composition_hint_v1.md
  - cell:    experiments/exp_substrate_partition_oracle_brain_composition_hint_v1_seed_7.py
  - sibling Path 1 (1st AP witness): math::T3/EXP_partition_oracle_substrate_derived_hint_naive_centroid_composition_HARD_FAIL_2026-06-28
"""

import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

METRICS_PATH = "data/exp_substrate_partition_oracle_brain_composition_hint_v1_seed_7_smoke/metrics.json"
PREREG_PATH = "preregs/2026-06-28_substrate_partition_oracle_brain_composition_hint_v1.md"
CELL_PATH = "experiments/exp_substrate_partition_oracle_brain_composition_hint_v1_seed_7.py"

ATOMIZED_BY = "skunkworks_atomize_partition_oracle_brain_composition_hint_v1_HF_AQ_2026-06-28"
ATOMIZED_DATE = "2026-06-28"
CELL_COMMIT = "fade4410"  # parent commit (sibling Path 1 AP atomize)

PATH1_HF_ATOM_ID = (
    "T3/EXP_partition_oracle_substrate_derived_hint_naive_centroid_"
    "composition_HARD_FAIL_2026-06-28"
)
AP_ATOM_ID = (
    "META_RULE_AP_composition_of_chain_grade_primitives_requires_signal_shape_adapter_"
    "OR_co_training_OR_pre_cell_compatibility_audit_naive_compose_breaks_when_primitive_A_"
    "natural_output_signal_shape_does_not_match_primitive_B_natural_input_signal_shape_"
    "witness_substrate_derived_hint_v1_seed_7_HARD_FAIL_route_acc_at_chance_despite_parent_"
    "routing_primitive_M10M_route_acc_0p97_2026-06-28_extends_META_RULE_AM_substrate_already_"
    "does_X_at_composition_layer_meta_discipline"
)


# ============================================================
# ATOM 1: math T3 experiment_record HARD_FAIL (Path 2)
# ============================================================
hf_atom = {
    "id": (
        "T3/EXP_partition_oracle_brain_composition_hint_vmPFC_cortex_hippo_3primitive_"
        "HARD_FAIL_2026-06-28"
    ),
    "name": (
        "Partition-oracle brain-composition hint v1 seed_7 smoke at FULL-N=8192 d=15 "
        "-- HARD_FAIL_COMPOSITION_COLLAPSE (3-primitive composition vmPFC schema-Bayes + "
        "cortex partition activation + hippo restricted cleanup; partition-correct-per-step "
        "= 0.209 at chance 0.200; single static partition decision per chain vs 15 distinct "
        "per-hop partition targets)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "M3-usable Barrier 1 break candidate -- PATH 2 (brain-faithful): "
        "compose 3 chain-grade primitives (vmPFC schema-Bayes "
        "schema_exemplar_bayes_ANCHOR_3 K_NEAREST_K20=0.728; cortex partition "
        "routing M=10M routing_acc=0.97; hippo pattern completion top1=1.000 "
        "from 50% corruption) per CLS architecture (McClelland-O'Reilly-McNaughton 1995). "
        "FR1: schema vector = bipolar(sum of all 15 hop predicates) per chain. "
        "FR2: schema cluster -> static partition map W_schema_to_part. "
        "FR3: hippo cleanup over predicted partition E_part. "
        "Smoke single seed=7 at FULL N=8192 V_C=4000 V_P=10 depth=15 n_chains_test=100 (6-arm). "
        ""
        "OFF-DATA recompute: A_BASELINE=0.40 (rail PASS [0.30,0.70]); "
        "B_PATH1_ROUTING_ONLY=0.00; C_PATH2_CORTEX_COMPOSITION=0.01; "
        "D_ORACLE=0.84; E_SCHEMA_ONLY=0.01; F_RANDOM=0.00. "
        "lift_C_A = -0.39 (NEGATIVE; PATH2 WORSE than baseline). "
        "lift_C_B = +0.01 (PATH2 essentially TIED with PATH1 -- composition "
        "adds nothing over single-primitive routing-only). "
        "gap_D_C = 0.83 (ORACLE retains 0.84 -- ingest/cleanup proven intact). "
        ""
        "DIAGNOSTIC SIGNAL: partition-correct-per-step mean across 15 hops: "
        "PATH2_C=0.2093 vs 1/N_PARTS=0.20 chance = +0.009 (at chance); "
        "PATH1_B=0.1813 (below chance); SCHEMA_ONLY_E=0.1953 (at chance); "
        "ORACLE_D=1.0 (sanity). Per-step shows NO decay because static schema "
        "predicts ONE partition fixed for all 15 hops -- correct ONLY when the "
        "single static prediction matches that hop's target. With 5 partitions "
        "and ~uniform target distribution per hop, expected match rate = 1/5 = "
        "0.20. Observed = 0.21. The 3-primitive composition has ZERO learning "
        "of the iterated multi-hop partition trajectory. "
        ""
        "arms_distinct=True (6 unique SHA-256); cardinality_ok=True (6/6); "
        "saturation=False; baseline rail OK. "
        ""
        "MECHANISM DIAGNOSIS (dual-mode failure): "
        "(i) SIGNAL-SHAPE INCOMPATIBILITY (extends META_RULE_AP from Path 1): "
        "    schema-Bayes was trained on first-hop (s,p,o) tuples implicitly via "
        "    chain-membership; multihop chain produces hops 2..15 with NOVEL "
        "    (s_pred, p_next) pairs OUT-OF-DISTRIBUTION relative to schema "
        "    training distribution. Schema posterior at inference is fired ONCE "
        "    on full predicate-sequence superposition -- but cluster-to-partition "
        "    map was learned from first-hop targets only. PATH 1's failure was "
        "    multihop W-state lacking the dedicated category cue the parent "
        "    routing primitive expected; PATH 2's failure is structurally similar "
        "    -- schema posterior over chain-level superposition does not carry "
        "    per-hop partition signal because the schema is permutation-invariant "
        "    over hops. "
        "(ii) ITERATED-STATE MISMATCH (NOVEL claim -- META_RULE_AQ): the 3-primitive "
        "    composition has NO PER-HOP STATE-TRACKER. Schema fires once per chain "
        "    (vmPFC abstracts whole task); partition decided once (cortex argmax); "
        "    hippo cleanup runs 15 times BUT with the SAME chosen_part for every "
        "    hop. The test regime requires 15 sequential partition decisions, one "
        "    per hop. Brain anatomy has a 4TH primitive missing from this composition: "
        "    dorsolateral PFC working memory maintains current-hop state and re-"
        "    fires schema-Bayes + cortex partition per hop with updated context. "
        "    Substrate HAS such a primitive (WM multi-bank K=4096 chain-grade) "
        "    but it was NOT included in this 3-primitive composition. "
        ""
        "RULE-OUT: ingest bug ruled out (ORACLE arm D=0.84 works with same W); "
        "cleanup bug ruled out (ORACLE arm D=0.84 uses same E_part subspace); "
        "schema-prototype construction ruled out (selftest T4/T5 pass with "
        "valid prototypes; SCHEMA_ONLY arm at 0.20 partition-correct confirms "
        "schema vectors and cluster assignments are stable, just uninformative "
        "for per-hop targets). "
        ""
        "CROSS-CELL EVIDENCE -- 2nd META_RULE_AP WITNESS: PATH 1 sibling "
        "(substrate_derived_hint_v1 seed_7) HARD_FAILed with naive centroid "
        "composition signal-shape incompatibility (1st AP witness). PATH 2 here "
        "HARD_FAILs with brain-faithful 3-primitive composition signal-shape "
        "incompatibility + iterated-state mismatch (2nd AP witness; 1st AQ "
        "witness). AP promotion criterion (2 independent witness cells of "
        "composition-failure rooted in signal-shape incompatibility) satisfied. "
        ""
        "M3 IMPLICATION: 3-primitive brain-faithful composition (vmPFC + cortex + "
        "hippo) is INSUFFICIENT for multi-hop chain queries as currently designed. "
        "M3 cortex layer needs to ADD a state-tracker primitive (substrate WM "
        "multi-bank or equivalent) before composition works. Capability closure "
        "(META_RULE_AO) NOT triggered (2 HF on related-but-distinct mechanism "
        "classes; need 3rd mechanism class HF before closure)."
    ),
    "aliases": [
        "partition_oracle_brain_composition_per_chain_HARD_FAIL_needs_per_hop_2026-06-28",
        "substrate_partition_oracle_brain_composition_hint_v1_seed_7_HF",
        "barrier_1_M3_usable_brain_faithful_3primitive_composition_dead",
        "composition_of_chain_grade_primitives_iterated_state_missing_witness_1",
        "META_RULE_AP_witness_2_composition_signal_shape_incompatibility",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "hard_fail",
        "cert_class": "mechanism_characterization",
        "verdict": "HARD_FAIL_COMPOSITION_COLLAPSE",
        "verdict_subtype": (
            "BRAIN_FAITHFUL_3PRIMITIVE_COMPOSITION_STATIC_SINGLE_PARTITION_DECISION_"
            "MISMATCHES_15_HOP_ITERATED_TARGETS_PARTITION_CORRECT_AT_CHANCE"
        ),
        "cell_commit": CELL_COMMIT,
        "cell_path": CELL_PATH,
        "prereg_path": PREREG_PATH,
        "metrics_path": METRICS_PATH,
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on metrics.json per_seed[0]: "
            "A=0.40 B=0.00 C=0.01 D=0.84 E=0.01 F=0.00; "
            "lift_C_A=-0.39 lift_C_B=0.01 gap_D_C=0.83; "
            "partition-correct-per-step mean PATH2=0.2093 PATH1=0.1813 "
            "SCHEMA_ONLY=0.1953 ORACLE=1.0; "
            "cardinality_ok=True (6/6); arms_distinct=True (6 unique SHA-256); "
            "saturation=False; baseline rail OK in [0.30,0.70]"
        ),
        "n_seeds_run": 1,
        "n_seeds_planned_total": 3,
        "seeds_pending": [13, 19],
        "seeds_pending_note": (
            "Sibling cells seed_13 + seed_19 exist but not yet dispatched. Given HF "
            "magnitude (arm_c=0.01; lift_C_A=-0.39; partition-correct at chance), "
            "additional seeds will not change verdict class -- the mechanism is dead "
            "at this composition. Sibling dispatch optional for cv-confirmation; "
            "primary action is research drill on adding state-tracker primitive."
        ),
        "regime": {
            "N": 8192,
            "V_C": 4000,
            "V_P": 10,
            "depth": 15,
            "n_chains_train": 200,
            "n_chains_test": 100,
            "n_partitions": 5,
            "part_size": 800,
            "n_schemas": 20,
            "encoder": "SUBSTRATE_NATIVE_BIPOLAR",
            "crosstalk_part": 0.3123,
            "crosstalk_baseline": 0.6987,
        },
        "per_arm_top1": {
            "A_baseline_full_V_C": 0.40,
            "B_path1_routing_only": 0.00,
            "C_path2_cortex_composition": 0.01,
            "D_oracle_ground_truth": 0.84,
            "E_schema_only_ablation": 0.01,
            "F_random_floor": 0.00,
        },
        "lifts_gaps": {
            "lift_C_A": -0.39,
            "lift_C_B": 0.01,
            "lift_C_E": 0.00,
            "lift_C_F": 0.01,
            "gap_D_C": 0.83,
        },
        "partition_correct_per_step_diagnostic": {
            "PATH2_C_mean": 0.2093,
            "PATH1_B_mean": 0.1813,
            "SCHEMA_ONLY_E_mean": 0.1953,
            "ORACLE_D_mean": 1.0,
            "chance_floor_5_partitions": 0.20,
            "above_chance_delta_PATH2": 0.0093,
            "interpretation": (
                "PATH2 partition-correct = chance because schema picks ONE static "
                "partition for whole chain but 15 hops target different partitions"
            ),
        },
        "per_step_acc_arm_c": [0.19, 0.06, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.01, 0.00, 0.00, 0.00, 0.00, 0.01, 0.01],
        "partition_correct_per_step_arm_c": [0.19, 0.22, 0.15, 0.22, 0.20, 0.19, 0.26, 0.23, 0.26, 0.20, 0.16, 0.24, 0.14, 0.24, 0.24],
        "gates_evaluated": {
            "C_in_HP_band_0p50_0p95": False,
            "C_above_HF_floor_0p30": False,
            "lift_C_A_ge_0p30_HP": False,
            "lift_C_B_ge_0p05_richer_than_path1": False,
            "lift_C_E_ge_0p10_richer_than_schema_only": False,
            "lift_C_F_ge_0p20_above_random_goal_info": False,
            "gap_D_C_le_0p05_retains_oracle": False,
            "baseline_A_in_rail_0p30_0p70": True,
            "saturation_lt_0p95": True,
            "arms_distinct_sha256_6_unique": True,
            "cardinality_ok_6_arms_6_expected": True,
            "brain_faithful_PATH2_richer_than_PATH1": False,
        },
        "hf_driver_primary": "C_below_HF_floor_AND_no_lift_over_PATH1_AND_partition_correct_at_chance",
        "ruling_out_alternatives": {
            "ingest_bug": "ruled out -- ORACLE arm D=0.84 works (same W matrix)",
            "cleanup_bug": "ruled out -- ORACLE arm D=0.84 works (same E_part cleanup)",
            "schema_prototype_construction_bug": "ruled out -- selftest T4/T5 pass; SCHEMA_ONLY arm partition-correct at chance confirms stable but uninformative",
            "cortex_W_construction_bug": "ruled out -- W_schema_to_part shape + normalization correct per selftest T5",
            "smoke_too_small": "ruled out -- DISCRIMINATOR-MUST-SURVIVE-SCALE smoke at FULL N + FULL depth",
            "schema_cluster_degeneracy": "partially supported -- 20 clusters x 200 train chains = 10 chains/cluster average; sparse but not pathological; bigger issue is single-static-prediction-for-15-hops",
        },
        "mechanism_root_cause_dual": (
            "DUAL FAILURE MODE: "
            "(i) Signal-shape: schema-Bayes prototype is bipolar(sum-of-all-15-predicates) "
            "summary of the chain; predicate-superposition is permutation-invariant over "
            "hops, so the schema cannot encode the per-hop partition trajectory. Cluster-"
            "to-partition map learned from first-hop targets is structurally unable to "
            "predict hop-i targets for i>1. Inference distribution OOD relative to "
            "training distribution at the schema layer. "
            "(ii) Iterated-state: composition fires schema ONCE per chain; partition decision "
            "is GLOBAL not per-hop; hippo cleanup uses SAME chosen_part for all 15 hops. "
            "Brain solves this with dorsolateral PFC working memory that maintains current-"
            "hop state and re-fires schema+cortex per hop. The 3 primitives chosen "
            "(vmPFC schema, cortex routing, hippo cleanup) are NOT closed under iteration -- "
            "they need an explicit state-tracker (4th primitive) that re-binds upstream "
            "primitives per step with updated context."
        ),
        "composition_failure_class": (
            "iterated_state_missing_AND_signal_shape_incompatibility_dual_mode_AP_AQ"
        ),
        "rescue_paths_for_future_work": [
            "add_state_tracker_primitive_re_fire_schema_per_hop_with_current_s_pred_as_context (META_RULE_AQ direct rescue)",
            "schema_v2_per_hop_indexed_prototypes_train_on_per_hop_targets_not_chain_targets",
            "cortex_W_per_hop_position_indexed_n_schemas_x_depth_partition_targets",
            "adapter_head_W_state_to_per_hop_partition_via_learned_projection (META_RULE_AP rescue)",
            "substrate_wm_multi_bank_K4096_integrated_as_4th_primitive_re_binds_schema_per_hop",
        ],
        "barrier_1_status": (
            "M3_usable_brain_composition_3_primitive_DEAD; "
            "ground-truth ORACLE arm still chain-grade-eligible at MIDDLE_BAND (sibling cell single seed); "
            "META_RULE_AO 3-HF capability-closure NOT triggered (2 HF on related-but-distinct "
            "mechanism classes; need 3rd to close partition-oracle direction)"
        ),
        "ap_witness_role": (
            "2nd_independent_witness_of_composition_signal_shape_incompatibility_"
            "satisfying_AP_promotion_criterion_2_witnesses"
        ),
        "aq_witness_role": (
            "1st_witness_of_iterated_state_missing_in_multi_primitive_composition_for_"
            "multi_step_test_regimes_promotion_pending_2nd_witness"
        ),
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AG",
            "META_RULE_AH", "META_RULE_AL", "META_RULE_AN", "META_RULE_AP",
            "META_RULE_AQ_candidate",
            "META_RULE_H", "BIAS-Q", "BIAS-N", "BIAS-S",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "functional_requirement_first_USER_2026-06-28",
        ],
        "next_actions": [
            "decide_research_drill_now_state_tracker_primitive_addition_vs_wait_Q2_V_C_sweep",
            "if_state_tracker_added_re_dispatch_v2_with_WM_multi_bank_as_4th_primitive",
            "if_2nd_AQ_witness_lands_promote_AQ_to_chain_grade_meta_rule",
            "no_blind_re_dispatch_of_static_schema_variants_without_iterated_state",
        ],
        "parent_chain_grade_primitives_composed": {
            "FR1_vmPFC_schema_bayes": {
                "atom_pattern": "schema_exemplar_bayes_ANCHOR_3",
                "K_NEAREST_K20": 0.728,
                "cv": 0.015,
            },
            "FR2_cortex_partition_routing": {
                "atom_pattern": "exp_substrate_partition_routing*",
                "M": "10M",
                "routing_acc": 0.97,
            },
            "FR3_hippo_pattern_completion": {
                "top1": 1.000,
                "corruption": 0.50,
            },
            "FR4_MISSING_state_tracker": {
                "atom_pattern": "wm_multi_bank_K4096_chain_grade",
                "status": "EXISTS_in_substrate_but_NOT_included_in_3_primitive_composition",
                "AQ_rescue_recommendation": (
                    "compose 4 primitives: vmPFC + cortex + hippo + WM-bank "
                    "with WM-bank holding current s_pred at each hop and "
                    "re-firing schema-Bayes+cortex with updated query context"
                ),
            },
        },
        "sibling_path1_atom_id": f"math::{PATH1_HF_ATOM_ID}",
        "cross_cell_evidence": (
            "Path 1 (substrate_derived_hint_v1) HF: naive centroid composition signal-shape "
            "incompatibility (W-state vs c_p cue). "
            "Path 2 (this cell) HF: brain-faithful 3-primitive composition; same signal-shape "
            "issue (schema-prototype training distribution vs multihop inference) PLUS "
            "missing iterated-state primitive. "
            "Two cell-level mechanisms, same composition-discipline gap. "
            "META_RULE_AP promotion to chain-grade triggered by 2nd independent witness."
        ),
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# ATOM 2: META_RULE_AQ (meta corpus; cert-neutral pending 2nd witness)
# ============================================================
aq_atom = {
    "id": (
        "META_RULE_AQ_brain_grounded_multi_primitive_composition_for_multi_hop_multi_step_"
        "capabilities_requires_explicit_state_tracker_primitive_that_re_fires_upstream_"
        "primitives_per_step_with_accumulated_context_single_shot_composition_fails_when_"
        "fire_mechanism_once_assumption_does_not_match_iterated_test_regime_witness_1_"
        "brain_composition_hint_v1_seed_7_HF_3primitive_vmPFC_cortex_hippo_lacks_4th_"
        "primitive_dorsolateral_PFC_working_memory_2026-06-28_extends_META_RULE_AP_at_"
        "iteration_layer_meta_discipline"
    ),
    "name": (
        "META_RULE_AQ -- brain-grounded multi-primitive compositions for multi-hop / "
        "multi-step capabilities require an EXPLICIT STATE-TRACKER primitive (per-step "
        "working-memory of accumulated context) that re-fires upstream primitives per "
        "step; single-shot composition fails when fire-once assumption mismatches "
        "iterated test regime"
    ),
    "corpus": "meta",
    "tier": "T_methodology",
    "kind": "discipline_rule",
    "description": (
        "META_RULE_AQ (composition-discipline at iteration layer; extends AP at composition layer): "
        ""
        "Brain-grounded multi-primitive compositions proposed for multi-step capabilities "
        "(multi-hop chains, multi-turn reasoning, multi-step plans, etc.) MUST include an "
        "explicit STATE-TRACKER primitive that maintains per-step working memory of "
        "accumulated context AND re-fires the upstream primitives per step with updated "
        "query context. Single-shot composition (fire-once-decide-once-use-decision-N-times) "
        "fails when the test regime requires N sequential decisions because static decisions "
        "cannot track the N-hop trajectory. "
        ""
        "BRAIN GROUNDING (load-bearing): brain anatomy for multi-hop reasoning has a 4-primitive "
        "circuit: "
        "(1) vmPFC schema-Bayes (cortex schema prototype matching; CITED@OReilly2014); "
        "(2) cortex partition activation (schema-conditioned routing; CITED@Mante2013); "
        "(3) hippo pattern completion (Marr 1971); "
        "(4) dorsolateral PFC working memory (MAINTAINS current-hop state and RE-FIRES "
        "    primitives 1-3 per hop with updated context; CITED@GoldmanRakic1995 + "
        "    CITED@MillerCohen2001). "
        "The cited 3 primitives are necessary but NOT SUFFICIENT for multi-hop chains. "
        "Compositions that omit primitive (4) are structurally limited to single-shot decisions. "
        ""
        "PRE-CELL DISCIPLINE (cell-author + Skunkworks SCHEMA-VET): when a cell proposes "
        "to compose multiple primitives for a MULTI-STEP capability test (multi-hop chain, "
        "multi-turn reasoning, multi-step plan, etc.), the prereg must explicitly state "
        "(a) the iteration regime (N steps; per-step target distribution); "
        "(b) which primitive maintains per-step state; "
        "(c) which primitive re-fires upstream primitives per step with updated context; "
        "(d) the structural argument that the composition CAN produce N distinct decisions "
        "    rather than ONE decision used N times. "
        "Pre-reg lacking (b)+(c)+(d) triggers SCHEMA-VET REJECT pending state-tracker addition. "
        ""
        "WITNESS 1 (atomized 2026-06-28): "
        "exp_substrate_partition_oracle_brain_composition_hint_v1_seed_7 HARD_FAIL: "
        "3-primitive composition (vmPFC schema-Bayes + cortex partition + hippo cleanup) "
        "fires schema ONCE per chain (schema = bipolar(sum-of-all-15-predicates)), decides "
        "partition ONCE via cortex argmax, runs hippo cleanup 15 times with SAME chosen_part. "
        "Test regime requires 15 distinct per-hop partition decisions. Observed partition-"
        "correct-per-step = 0.2093 (vs 1/5 chance = 0.20); arm_c top1 = 0.01. Substrate "
        "HAS a chain-grade state-tracker primitive (WM multi-bank K=4096) but the 3-primitive "
        "composition did NOT include it. "
        ""
        "RELATION TO OTHER META_RULES: "
        "- Extends META_RULE_AP (composition signal-shape adapter) at the ITERATION layer: "
        "  AP addresses primitive-to-primitive compatibility within ONE step; AQ addresses "
        "  composition closure under iteration across N steps. Both apply when composing "
        "  chain-grade primitives -- AP for shape, AQ for iteration. "
        "- Distinct from META_RULE_AO (3-HF capability closure): AO is about knowing when "
        "  to stop iterating on a capability box; AQ is about correct composition design "
        "  for capabilities that REQUIRE iteration. "
        "- Distinct from META_RULE_AM (substrate-already-does-X): AM forces demonstration "
        "  that existing primitive FAILS before adding mechanism; AQ forces demonstration "
        "  that proposed composition has structural state-tracking primitive for iteration. "
        ""
        "M3 IMPLICATION: M3 cortex layer's compositional reasoning capability requires "
        "explicit state-tracker primitive in any multi-step composition. Substrate has "
        "the primitive (WM multi-bank) -- it just needs to be INCLUDED in compositions, "
        "not omitted. Path 2 v2 should add WM-bank as 4th primitive."
    ),
    "aliases": [
        "multi_step_composition_requires_state_tracker_primitive_discipline",
        "no_fire_once_decide_once_for_iterated_test_regimes",
        "META_RULE_AQ_iteration_layer_state_tracker_discipline",
        "brain_4primitive_circuit_for_multihop_3plus_state_tracker",
    ],
    "metadata": {
        "provenance_quality": "DERIVED_FROM_WITNESS",
        "cert_status": "cert_neutral_discipline_rule",
        "cert_class": "meta_discipline",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "rule_letter": "AQ",
        "rule_layer": "iteration",
        "extends": ["META_RULE_AP"],
        "related": ["META_RULE_AM", "META_RULE_AO"],
        "witness_atom_ids": [
            f"math::{hf_atom['id']}",
        ],
        "witness_count": 1,
        "promotion_criterion_for_chain_grade_meta_rule": (
            "2 independent witness cells of multi-step composition failing because the "
            "composition lacks an explicit state-tracker primitive (e.g., any future "
            "multi-step composition cell HARD_FAILing with a static-decision diagnostic) "
            "OR USER+research consensus that single witness + brain-anatomy mechanism "
            "diagnosis + substrate-has-the-primitive-just-not-included is sufficient"
        ),
        "rescue_paths": [
            "add_state_tracker_primitive_explicitly_to_composition",
            "use_substrate_wm_multi_bank_K4096_as_state_tracker",
            "per_hop_re_fire_schema_with_current_s_pred_in_query_context",
            "per_hop_indexed_schema_prototypes_train_on_hop_position_aware_targets",
        ],
        "brain_anatomy_grounding": {
            "vmPFC_schema_bayes": "CITED@OReilly2014",
            "cortex_partition_activation": "CITED@Mante2013",
            "hippo_pattern_completion": "CITED@Marr1971",
            "dlPFC_working_memory": "CITED@GoldmanRakic1995_CITED@MillerCohen2001",
            "circuit_role": "4-primitive multi-hop reasoning circuit; dlPFC re-fires 1-3 per hop",
        },
        "applies_to_in_flight_cells": [],
        "schema_vet_directive": (
            "Any prereg proposing primitive-composition for a MULTI-STEP capability test "
            "must include: (a) iteration regime N + per-step target distribution; "
            "(b) which primitive maintains per-step state; (c) which primitive re-fires "
            "upstream primitives per step; (d) structural argument the composition can "
            "produce N distinct decisions not 1 decision used N times. Skunkworks SCHEMA-VET "
            "will REJECT preregs lacking (b)+(c)+(d)."
        ),
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# CERT_LEDGER ROW 1: HF cert_ruling (delta=0)
# ============================================================
hf_ledger = {
    "ts": time.time(),
    "op": "cert_ruling",
    "atom_id": f"math::{hf_atom['id']}",
    "cert_status": "hard_fail",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "HARD_FAIL_COMPOSITION_COLLAPSE_smoke_at_FULL_N8192_d15_arm_c_0p01_partition_"
        "correct_per_step_at_chance_0p209_vs_0p20_lift_C_A_negative_0p39_lift_C_B_"
        "tied_at_0p01_oracle_D_0p84_rules_out_ingest_cleanup_bug_ROOT_CAUSE_dual_mode_"
        "signal_shape_incompatibility_AP_witness_2_PLUS_iterated_state_missing_AQ_witness_1_"
        "brain_4_primitive_circuit_missing_dlPFC_working_memory_state_tracker"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path": METRICS_PATH,
        "prereg_path": PREREG_PATH,
        "cell_path": CELL_PATH,
        "atom_qualified_id": f"math::{hf_atom['id']}",
        "sibling_path1_atom": f"math::{PATH1_HF_ATOM_ID}",
    },
    "supersedes": None,
    "note": (
        "partition_oracle_brain_composition_hint_v1_seed_7_HARD_FAIL_3primitive_vmPFC_"
        "cortex_hippo_composition_partition_correct_at_chance_0p209_static_single_decision_"
        "mismatches_15_hop_iterated_targets_DO_NOT_close_partition_oracle_direction_HF_count_"
        "2_of_3_per_META_RULE_AO_2nd_independent_AP_witness_PROMOTES_AP_to_chain_grade_"
        "1st_AQ_witness_iterated_state_missing_in_multi_primitive_composition"
    ),
}


# ============================================================
# CERT_LEDGER ROW 2: META_RULE_AP PROMOTION to chain-grade (2nd witness satisfied)
# ============================================================
ap_promotion_ledger = {
    "ts": time.time(),
    "op": "meta_rule_promotion_to_chain_grade",
    "atom_id": f"meta::{AP_ATOM_ID}",
    "cert_status": "chain_grade_meta_rule",
    "cert_class": "meta_discipline",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "META_RULE_AP_PROMOTED_from_cert_neutral_to_chain_grade_meta_rule_2nd_independent_"
        "witness_cell_substrate_partition_oracle_brain_composition_hint_v1_seed_7_HF_satisfies_"
        "promotion_criterion_2_witnesses_of_composition_signal_shape_incompatibility_"
        "PATH1_naive_centroid_W_state_vs_c_p_cue_AND_PATH2_schema_prototype_training_dist_vs_"
        "multihop_inference_dist_both_root_caused_by_signal_shape_mismatch_between_chain_"
        "grade_primitives_in_composition"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "atom_qualified_id": f"meta::{AP_ATOM_ID}",
        "witness_1_atom": f"math::{PATH1_HF_ATOM_ID}",
        "witness_2_atom": f"math::{hf_atom['id']}",
    },
    "supersedes": None,
    "note": (
        "META_RULE_AP_promotion_event_cert_neutral_to_chain_grade_meta_rule_2_independent_"
        "witness_criterion_satisfied_AP_now_load_bearing_for_all_future_prereg_SCHEMA_VET_"
        "compositions_must_satisfy_signal_shape_compatibility_OR_adapter_OR_co_training"
    ),
}


# ============================================================
# CERT_LEDGER ROW 3: META_RULE_AQ first atomization (cert-neutral)
# ============================================================
aq_ledger = {
    "ts": time.time(),
    "op": "meta_rule_atomization",
    "atom_id": f"meta::{aq_atom['id']}",
    "cert_status": "cert_neutral_discipline_rule",
    "cert_class": "meta_discipline",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "META_RULE_AQ_first_atomized_multi_step_composition_requires_explicit_state_tracker_"
        "primitive_witness_1_brain_composition_hint_v1_seed_7_HF_3primitive_vmPFC_cortex_"
        "hippo_lacks_dlPFC_WM_4th_primitive_extends_META_RULE_AP_at_iteration_layer_"
        "cert_neutral_pending_2nd_witness_or_USER_research_consensus_for_chain_grade_promotion"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path": METRICS_PATH,
        "prereg_path": PREREG_PATH,
        "cell_path": CELL_PATH,
        "atom_qualified_id": f"meta::{aq_atom['id']}",
        "witness_atom_qualified_ids": [f"math::{hf_atom['id']}"],
    },
    "supersedes": None,
    "note": (
        "META_RULE_AQ_iteration_layer_state_tracker_discipline_atomized_cert_neutral_"
        "pending_2nd_witness_SCHEMA_VET_directive_active_immediately_for_all_future_multi_"
        "step_composition_preregs_must_declare_state_tracker_primitive_substrate_has_WM_"
        "multi_bank_K4096_chain_grade_primitive_available_for_inclusion_as_4th_primitive"
    ),
}


# ============================================================
# A5 WRITE PROTOCOL
# ============================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str) -> int:
    """Atomic append with verify-load + integrity-check."""
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"target does not exist: {path}"

    # PRE: read full file + count
    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    # Validate every pre-line parses (integrity)
    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    # Build new content
    new_line = json.dumps(new_row, ensure_ascii=True)
    # Round-trip validate
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id"), "round-trip id mismatch"
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id"), "round-trip atom_id mismatch"

    out_lines = pre_lines + [new_line]
    out_text = "\n".join(out_lines) + "\n"

    # tmp -> os.replace (atomic)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp_path), str(path))

    # POST: verify-load
    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1, f"count delta mismatch: {pre_count} -> {post_count}"

    # Tail must parse + match
    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"], "tail id mismatch"
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"], "tail atom_id mismatch"

    # Re-validate every line parses
    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK (atomic append + verify-load + integrity-check)")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    print(f"[A5] HF atom_id      = math::{hf_atom['id']}")
    print(f"[A5] META_RULE_AQ id = meta::{aq_atom['id'][:80]}...")
    print(f"[A5] AP_promotion -> chain-grade (2 witnesses satisfied)")
    print(f"[A5] cert_ledger ops: hf_ruling (delta=0) + ap_promotion (delta=0) + aq_atomization (delta=0)")

    append_jsonl_a5(MATH_ATOMS, hf_atom, "math/atoms.jsonl")
    append_jsonl_a5(META_ATOMS, aq_atom, "meta/atoms.jsonl")
    append_jsonl_a5(CERT_LEDGER, hf_ledger, "meta/cert_ledger.jsonl[hf]")
    append_jsonl_a5(CERT_LEDGER, ap_promotion_ledger, "meta/cert_ledger.jsonl[ap_promotion]")
    append_jsonl_a5(CERT_LEDGER, aq_ledger, "meta/cert_ledger.jsonl[aq]")

    print(f"[A5] DONE OK; CERT delta = 0 (HF) + 0 (AP promotion event) + 0 (AQ cert-neutral pending 2nd witness)")


if __name__ == "__main__":
    main()
