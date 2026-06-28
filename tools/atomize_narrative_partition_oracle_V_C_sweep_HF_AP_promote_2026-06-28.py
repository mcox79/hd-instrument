"""
A5-gated atomize: substrate_narrative_partition_oracle_V_C_sweep_v1 HARD_FAIL
+ Q3 V_C-axis-invariance MEASURED_MECHANISM
+ META_RULE_AP promotion (cert_neutral -> chain_grade_eligible at 2nd witness threshold).

Verdict on disk: HARD_FAIL_ORACLE_NEVER_RESCUES_AT_V_C=4000.
Cert class HF: mechanism_characterization. CERT delta = 0 (HF, by definition).
Cert class Q3 V_C-invariance: mechanism_characterization (single seed; under-claim
  per Fix #28 / BIAS-Q; multi-seed cv promotion deferred to sibling chunks).
  CERT delta = 0 (single-seed witness; not chain-grade until cv-confirmed).
META_RULE_AP: 2nd witness landed (Path 1 partition_oracle_substrate_derived_hint v1
  was witness #1). AP's own promotion_criterion is "2 independent witness cells OR
  USER+research consensus"; 2nd witness now ATOMIZED.
  CERT delta = +1 (cert-neutral -> chain_grade_eligible meta_discipline; first AP
  promotion ever; new chain-grade meta rule entry to CERT N).

OFF-DATA recompute (verify-OFF-DATA, NOT verdict_msg):
  seed=7 single-seed smoke at FULL N_EVENTS=100 / 5 chars / 8 pronouns / Q_per_type=8
  V_C points {50, 200, 1000, 4000}:
    oracle_Q2:  0.125  0.250  0.125  0.125   (range 0.125; min == oracle@4000 == 0.125)
    naive_Q2:   0.375  0.250  0.250  0.125
    floor_Q2:   0.125  0.125  0.000  0.500   (floor at V_C=4000 is OUTLIER 0.500 on 5-way Q=8; binomial noise; cell's HF gate at >0.60 NOT tripped; HP_FLOOR_IMPOSSIBLE not fired)
    replay_Q3:  1.000  1.000  1.000  1.000   (unanimous Q3 across V_C; Q3 V_C-INDEPENDENT confirmed at this seed)
  oracle_Q2 - floor_Q2 lift across V_C: +0.000, +0.125, +0.125, -0.375 (no V_C trend)
  oracle_Q2 at V_C=4000 = 0.125 <= HF_PARTITION_Q2_AT_TOP_VC=0.30 -> HF tripped
  monotone_oracle_V_C = False (0.125 -> 0.250 -> 0.125 -> 0.125)
  arms_distinct = 16/16 SHA-distinct
  cardinality_ok = 16/16 expected vs observed
  replay_Q3 at V_C=4000 = 1.000 > HP_REPLAY_Q3_ALL_VC=0.60 (positive control passed)

HONEST CALLOUT: handoff note tables CLAIM 3-seed means across seeds {7,13,19} but
  ONLY seed=7 partials exist on disk; metrics.json is single-seed. Skunkworks
  atomizes the SEED=7 numbers from disk; cross-seed cv NOT YET MEASURED. This is
  the cert-trail boundary; full-N seed_13 + seed_19 chunked dispatches were
  documented as "not dispatching" per cell-author's THREE SMOKE DISCIPLINES
  framing (smoke fired the discriminator). Skunkworks NOTES this in the atom
  metadata field "cross_seed_status".

Mechanism diagnosis (load-bearing; per cell-author note):
  Partition_oracle_v5's V_C=4000 validation used a candidate-anchor projection
  basis SCALED with V_C (so anchor projections were discriminative per partition).
  This narrative-coref cell holds N_CHARACTERS=5 partitions FIXED while only
  scaling per-partition vocabulary -- WRONG AXIS. The substituted-cue magnitude
  signal |W_part[c] @ substituted_cue| does NOT discriminate because the
  partition contains many verb/obj combos and the substituted cue isn't specific
  to the true referent's stored memories.

  This is the SAME composition-discipline failure class as Path 1 (META_RULE_AP):
    Path 1: partition-routing primitive (input shape: dedicated category cue c_p)
            composed with multihop chain query (output shape: no category cue)
            -> route_acc fired at chance
    Path 3 (THIS): partition_oracle_v5 (input shape: candidate-anchor projection
            with V_C-scaled anchors) composed with narrative-coref pronoun task
            (output shape: char_id discrimination over fixed 5 partitions; no
            V_C-scaled anchor basis)
            -> oracle_Q2 fires at floor at all V_C
  Both fail because primitive A's NATURAL operating regime / signal shape does
  not match primitive B's regime / signal shape. META_RULE_AP applies.

A5 protocol:
  1. PRE: read full file + count + parse all lines for both math + meta + cert_ledger
  2. Append HF atom to math/atoms.jsonl via tmp -> os.replace
  3. Append Q3 V_C-invariance witness atom to math/atoms.jsonl
  4. Append META_RULE_AP_v2 PROMOTION atom to meta/atoms.jsonl (supersedes v1)
  5. Append 3 cert_ledger rows
  6. POST: verify-load on each (count delta + tail-parse + round-trip id + every-line integrity)

Anchors:
  - metrics: data/exp_substrate_narrative_partition_oracle_V_C_sweep_v1_smoke/metrics.json
  - prereg:  preregs/2026-06-28_substrate_narrative_partition_oracle_V_C_sweep_v1.md
  - cell:    experiments/exp_substrate_narrative_partition_oracle_V_C_sweep_v1.py
  - note:    notes/exp_dev_V_C_sweep_falsifies_partition_oracle_cliff_narrative_coref_2026-06-28.md
  - witness#1 (Path 1): math::T3/EXP_partition_oracle_substrate_derived_hint_naive_centroid_composition_HARD_FAIL_2026-06-28
  - parent CG primitive (Q3): data/exp_c3_compressed_sequence_replay_v1/metrics.json (K=20 chain-grade)
  - parent CG primitive (Q2 attempted): data/exp_substrate_multihop_partition_oracle_v5_hardened_v1_smoke/metrics.json (ORACLE_C=0.97 at V_C=4000)
"""

import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

METRICS_PATH = "data/exp_substrate_narrative_partition_oracle_V_C_sweep_v1_smoke/metrics.json"
PREREG_PATH = "preregs/2026-06-28_substrate_narrative_partition_oracle_V_C_sweep_v1.md"
CELL_PATH = "experiments/exp_substrate_narrative_partition_oracle_V_C_sweep_v1.py"
NOTE_PATH = "notes/exp_dev_V_C_sweep_falsifies_partition_oracle_cliff_narrative_coref_2026-06-28.md"

ATOMIZED_BY = "skunkworks_atomize_narrative_partition_oracle_V_C_sweep_HF_plus_Q3_V_C_invariance_plus_AP_promote_2026-06-28"
ATOMIZED_DATE = "2026-06-28"
CELL_COMMIT = "uncommitted_smoke_seed_7"  # cell-author note: no chunked full dispatch; smoke is the answer

# Witness #1 for META_RULE_AP (already atomized 2026-06-28)
WITNESS_1_AP = "math::T3/EXP_partition_oracle_substrate_derived_hint_naive_centroid_composition_HARD_FAIL_2026-06-28"

# Existing META_RULE_AP v1 atom (cert-neutral) to be superseded by v2 (chain-grade-eligible)
AP_V1_ATOM_ID = (
    "META_RULE_AP_composition_of_chain_grade_primitives_requires_signal_shape_adapter_OR_co_training_"
    "OR_pre_cell_compatibility_audit_naive_compose_breaks_when_primitive_A_natural_output_signal_shape_"
    "does_not_match_primitive_B_natural_input_signal_shape_witness_substrate_derived_hint_v1_seed_7_"
    "HARD_FAIL_route_acc_at_chance_despite_parent_routing_primitive_M10M_route_acc_0p97_2026-06-28_"
    "extends_META_RULE_AM_substrate_already_does_X_at_composition_layer_meta_discipline"
)


# ============================================================
# ATOM 1: math T3 HARD_FAIL on V_C-cliff hypothesis
# ============================================================
hf_atom = {
    "id": "T3/EXP_narrative_partition_oracle_V_C_sweep_HARD_FAIL_Q2_no_V_C_cliff_2026-06-28",
    "name": (
        "narrative partition oracle V_C sweep v1 smoke seed=7 at FULL N_EVENTS=100 5 chars 8 pronouns "
        "-- HARD_FAIL Q2_no_V_C_cliff (partition_oracle_v5 mechanism does NOT transfer to narrative-coref "
        "at ANY V_C in {50, 200, 1000, 4000}; oracle_Q2 stays at floor across full sweep; "
        "META_RULE_AP composition-discipline witness #2)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "V_C sweep of partition_oracle_v5_hardened primitive (chain-grade at V_C=4000 ORACLE_C=0.97) "
        "applied to narrative-coreference Q2 task across V_C in {50, 200, 1000, 4000}. Hypothesis was "
        "monotone Q2 lift with V_C and HARD_PASS at V_C >= 1000 (drill prediction THEORETICAL@). "
        "RESULT (smoke seed=7 single-seed at FULL N_EVENTS=100 / N_CHARS=5 / N_PRONOUN_EVENTS=12 / Q_per_type=8): "
        "oracle_Q2 = [0.125, 0.250, 0.125, 0.125] across V_C [50, 200, 1000, 4000]; "
        "naive_Q2 = [0.375, 0.250, 0.250, 0.125]; floor_Q2 = [0.125, 0.125, 0.000, 0.500]; "
        "replay_Q3 = [1.000, 1.000, 1.000, 1.000] (unanimous; positive control passed). "
        "oracle_Q2 at V_C=4000 = 0.125 <= HF_PARTITION_Q2_AT_TOP_VC=0.30 -> HF gate tripped. "
        "monotone_oracle_V_C = False (0.125 -> 0.250 -> 0.125 -> 0.125; no V_C trend). "
        "arms_distinct = 16/16 SHA; cardinality_ok = 16/16. "
        "MECHANISM DIAGNOSIS: partition_oracle_v5 was validated where candidate-anchor PROJECTION basis "
        "scaled WITH V_C (anchor projections discriminative per partition). This narrative cell holds "
        "N_CHARACTERS=5 partitions FIXED while only scaling per-partition vocab -- WRONG AXIS. "
        "Substituted-cue magnitude |W_part[c] @ substituted_cue| does not discriminate because partition "
        "contains many verb/obj combos and substituted cue isn't specific to true referent's stored memories. "
        "COMPOSITION-DISCIPLINE FAILURE CLASS: same as Path 1 witness (META_RULE_AP); both fail because "
        "primitive A's natural operating regime / signal shape does not match primitive B's regime. "
        "Path 1: routing primitive (dedicated category cue) composed into multihop (no category cue) -> chance. "
        "Path 3 (this): partition_oracle_v5 (V_C-scaled anchor basis) composed into 5-partition pronoun task "
        "(fixed partitions, no V_C-scaled anchor basis) -> floor. "
        "CROSS-SEED STATUS: smoke is SINGLE seed=7 from on-disk partials. Handoff note tables claim 3-seed "
        "means {7,13,19} but only seed=7 partials exist; cell-author elected not to dispatch chunked full "
        "per THREE_SMOKE_DISCIPLINES (smoke fired the discriminator at full N regime). cv not computed; "
        "atomizing seed=7 numbers; sibling-seed promotion deferred. "
        "META_RULE_AP witness #2 LANDED (was 1; AP promotion threshold = 2 -> NOW MET)."
    ),
    "aliases": [
        "narrative_partition_oracle_V_C_sweep_HARD_FAIL_Q2_no_V_C_cliff_2026-06-28",
        "substrate_narrative_partition_oracle_V_C_sweep_v1_seed_7_HF",
        "M3_concern_3_narrative_coref_Q2_NOT_resolved_by_V_C_scaling_alone",
        "composition_of_chain_grade_primitives_signal_shape_incompatible_witness_2",
        "partition_oracle_v5_does_NOT_transfer_to_narrative_coref_at_any_V_C",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "hard_fail",
        "cert_class": "mechanism_characterization",
        "verdict": "HARD_FAIL_ORACLE_NEVER_RESCUES_AT_V_C=4000",
        "verdict_subtype": "Q2_NO_V_C_CLIFF_ORACLE_AT_FLOOR_ACROSS_FULL_SWEEP",
        "cell_commit": CELL_COMMIT,
        "cell_path": CELL_PATH,
        "prereg_path": PREREG_PATH,
        "metrics_path": METRICS_PATH,
        "note_path": NOTE_PATH,
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on metrics.json sweep_summary: "
            "oracle_Q2_by_V_C=[0.125,0.250,0.125,0.125]; naive_Q2_by_V_C=[0.375,0.250,0.250,0.125]; "
            "floor_Q2_by_V_C=[0.125,0.125,0.000,0.500]; replay_Q3_by_V_C=[1.000,1.000,1.000,1.000]; "
            "oracle@V_C=4000=0.125 <= HF_PARTITION_Q2_AT_TOP_VC=0.30 -> HF; "
            "monotone_oracle=False; arms_distinct=16/16 SHA; cardinality_ok=16/16"
        ),
        "n_seeds_run": 1,
        "seed_run": 7,
        "n_seeds_planned": 3,
        "seeds_pending": [13, 19],
        "cross_seed_status": (
            "Single-seed smoke on disk. Handoff note tables claim 3-seed means {7,13,19}; "
            "only seed=7 partials exist. Cell-author elected NOT to dispatch chunked full seeds "
            "per THREE_SMOKE_DISCIPLINES (smoke fired discriminator at FULL N regime; band-floor "
            "result IS the answer). cv NOT computed. Sibling-seed dispatch optional; HF magnitude "
            "(oracle 0.125 vs HP 0.60; lift_over_naive 0.000 at V_C=4000) makes cv-flip implausible. "
            "Skunkworks atomization treats seed=7 numbers as the verified evidence; ANY upward "
            "promotion would require sibling-seed cv."
        ),
        "regime": {
            "N_HIPPO": 512,
            "N_CORTEX": 1024,
            "N_PART": 1024,
            "N_EVENTS": 100,
            "N_CHARS": 5,
            "K_SCENE_BOUNDARY": 10,
            "N_PRONOUN_EVENTS": 12,
            "Q_per_type": 8,
            "V_C_sweep": [50, 200, 1000, 4000],
            "V_C_configs": {
                "50": [12, 38], "200": [50, 150],
                "1000": [250, 750], "4000": [1000, 3000],
            },
            "arms_count": 4,
            "expected_n_units": 16,
            "observed_n_units": 16,
        },
        "sweep_summary": {
            "V_C_50": {
                "ARM_RANDOM_FLOOR": {"Q2": 0.125, "Q3": 0.0},
                "ARM_BASELINE_NAIVE": {"Q2": 0.375, "Q3": 0.375},
                "ARM_PARTITION_ORACLE_Q2": {"Q2": 0.125, "Q3": 0.375},
                "ARM_SEQUENCE_REPLAY_Q3": {"Q2": 0.375, "Q3": 1.0},
            },
            "V_C_200": {
                "ARM_RANDOM_FLOOR": {"Q2": 0.125, "Q3": 0.125},
                "ARM_BASELINE_NAIVE": {"Q2": 0.25, "Q3": 0.375},
                "ARM_PARTITION_ORACLE_Q2": {"Q2": 0.25, "Q3": 0.375},
                "ARM_SEQUENCE_REPLAY_Q3": {"Q2": 0.25, "Q3": 1.0},
            },
            "V_C_1000": {
                "ARM_RANDOM_FLOOR": {"Q2": 0.0, "Q3": 0.125},
                "ARM_BASELINE_NAIVE": {"Q2": 0.25, "Q3": 0.25},
                "ARM_PARTITION_ORACLE_Q2": {"Q2": 0.125, "Q3": 0.25},
                "ARM_SEQUENCE_REPLAY_Q3": {"Q2": 0.25, "Q3": 1.0},
            },
            "V_C_4000": {
                "ARM_RANDOM_FLOOR": {"Q2": 0.5, "Q3": 0.0},
                "ARM_BASELINE_NAIVE": {"Q2": 0.125, "Q3": 0.375},
                "ARM_PARTITION_ORACLE_Q2": {"Q2": 0.125, "Q3": 0.375},
                "ARM_SEQUENCE_REPLAY_Q3": {"Q2": 0.125, "Q3": 1.0},
            },
        },
        "gates_evaluated": {
            "HF_PARTITION_Q2_AT_TOP_VC_LE_0p30": True,  # oracle@V_C=4000 = 0.125
            "HF_REPLAY_Q3_ANY_VC_LE_0p20": False,       # all 1.000
            "HF_RANDOM_FLOOR_ANY_VC_GT_0p60": False,    # max 0.500 < 0.60 (cell uses 0.60 cap for impossible-bug detection)
            "HP_PARTITION_Q2_HIGH_VC_GE_0p60": False,   # max at high V_C = 0.125
            "HP_MONOTONE_ORACLE_V_C": False,            # 0.125 -> 0.250 -> 0.125 -> 0.125
            "HP_LIFT_OVER_NAIVE_GE_0p30_AT_HIGH_VC": False,  # max lift 0.000
            "HP_REPLAY_Q3_ALL_VC_GE_0p60": True,        # all 1.000 (positive control)
            "arms_distinct_16_unique_SHA": True,
            "cardinality_ok_16_expected_observed": True,
        },
        "BIAS_Q_check_replay_1p000": (
            "BIAS-Q (suspect 1.000): replay_Q3 = 1.000 at all V_C; this is NOT by-construction. "
            "c3_compressed_sequence_replay K=20 primitive is independently chain-grade per "
            "data/exp_c3_compressed_sequence_replay_v1/metrics.json (B_d5=1.000 HARD_PASS at "
            "parent atom). Q3 task = predict prior-event-in-scene; replay primitive's natural "
            "operating regime (intra-scene sequence binding) matches Q3 task design exactly. "
            "Not test-trivial; primitive working as designed at small intra-scene local-prediction. "
            "Single seed though -- cv pending."
        ),
        "hf_driver_primary": "Q2_oracle_at_floor_across_full_V_C_sweep_AND_no_V_C_trend_AND_no_lift_over_naive",
        "ruling_out_alternatives": {
            "smoke_too_small": "ruled out -- DISCRIMINATOR_MUST_SURVIVE_SCALE: smoke at FULL N_EVENTS=100 = source-cell regime",
            "Q_per_type_noise_floor": "tightened from source's Q=3 to Q=8; random floor expected 0.20 5-way; "
                                       "observed max 0.500 is +2sigma outlier on binomial (n=8 p=0.20); not a bug",
            "wrong_partition_oracle_impl": "Q2 readout function q2_partition_oracle_readout mirrors arm_part_oracle from "
                                            "partition_oracle_v5_hardened EXACTLY (substituted-cue, per-char W_part magnitude)",
            "replay_primitive_failure": "ruled out -- replay_Q3=1.000 at all 4 V_C (positive control passed unanimous)",
            "encoding_bug": "ruled out -- naive baseline distinguishes from floor at V_C=50/200/1000 (0.375/0.25/0.25 vs floor)",
        },
        "mechanism_root_cause": (
            "partition_oracle_v5's V_C=4000 validation used candidate-anchor PROJECTION basis SCALED with V_C "
            "(anchor projections discriminative per partition); validated arm worked because per-anchor "
            "projection was a high-dimensional signature unique to each partition at V_C=4000. THIS narrative "
            "cell holds N_CHARACTERS=5 partitions FIXED while only scaling per-partition vocab (jobs+objects); "
            "substituted-cue magnitude |W_part[c] @ substituted_cue| does NOT discriminate because the partition "
            "contains many verb/obj combos and substituted cue is not specific to true referent's stored "
            "memories. The signal shape (V_C-scaled anchor projection) required by primitive's natural operating "
            "regime is NOT realized in narrative-coref task design. WRONG-AXIS scaling: scaling within-partition "
            "vocab does not produce the per-partition discriminative signature primitive needs."
        ),
        "composition_failure_class": "operating_regime_signal_shape_incompatibility_between_chain_grade_primitive_validated_regime_AND_downstream_task_regime",
        "AP_witness_number": 2,
        "AP_witness_chain": [
            WITNESS_1_AP,
            "math::T3/EXP_narrative_partition_oracle_V_C_sweep_HARD_FAIL_Q2_no_V_C_cliff_2026-06-28",
        ],
        "rescue_paths_for_Q2_narrative_coref": [
            "HRR_context_bind_disambiguator: scene_context bundle bound to char identities via "
                "circular convolution; cosine(scene_context_bound_to_c, cue) per candidate char. "
                "Source primitive: contextual_encoding_hrr_binding_smoke_v1 WSD=1.000 chain-grade. "
                "Functional-req match: WSD = pick correct meaning given context = pronoun disambig "
                "given scene context. CANDIDATE NEXT CELL per drill escape hatch.",
            "co_training_partition_basis_with_narrative_anchors: train partition_oracle's anchor "
                "projection basis on narrative-task-specific anchors at fixed N_CHARS=5 partitions",
            "per_partition_signature_v2: contrastive per-partition embeddings learned from narrative "
                "co-occurrence (not magnitude-of-readout proxy)",
        ],
        "M3_concern_3_status": (
            "M3 concern #3 (long-narrative Q2 coref) NOT resolved by V_C scaling alone. Path to "
            "resolution is either (a) HRR context-bind primitive (chain-grade candidate per drill, "
            "contextual_encoding_hrr_binding_smoke_v1 WSD=1.000) or (b) a fundamentally different "
            "primitive for entity tracking. Recommend research drill: spawn cell-author on HRR "
            "context-bind disambiguator pivot per drill escape hatch."
        ),
        "capability_closure_status": (
            "DO_NOT_CLOSE_narrative_Q2_coref_direction yet. META_RULE_AO requires 3 mechanism-class "
            "HFs for preliminary closure. Current mechanism-class HF count for narrative-Q2-coref: "
            "1 (partition_oracle composition; this cell). Next mechanism class to try: HRR context-bind. "
            "If HRR also HF -> 2nd mechanism class; need 3rd before preliminary closure."
        ),
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AG",
            "META_RULE_AH", "META_RULE_AL", "META_RULE_AM", "META_RULE_AN",
            "META_RULE_AP",
            "META_RULE_H_CARDINALITY_OK",
            "META_RULE_J_NO_SILENT_EXCEPT",
            "META_RULE_L_STRICT_ABOVE_FLOOR",
            "BIAS-Q",
            "BIAS-S_band_calibration",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            "THREE_SMOKE_DISCIPLINES_2026-06-26",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "functional_requirement_first_USER_2026-06-28",
        ],
        "next_actions": [
            "spawn_research_drill_HRR_context_bind_disambiguator_for_narrative_Q2_coref",
            "do_not_dispatch_chunked_full_seeds_13_19_unless_USER_requests_cv_confirmation",
            "Path_2_vmPFC_composition_landing_will_be_AP_witness_3_if_HF_or_AP_negative_evidence_if_HP",
            "META_RULE_AP_PROMOTION_THIS_ATOMIZATION_to_chain_grade_eligible_via_2nd_witness_threshold",
        ],
        "parent_chain_grade_primitive_for_Q2": {
            "atom_id_pattern": "exp_substrate_multihop_partition_oracle_v5_hardened_v1*",
            "validated_at": "V_C=4000 ORACLE_C=0.97 depth=15",
            "key_design": "candidate-anchor projection basis SCALED with V_C",
            "design_delta_from_this_cell": (
                "narrative cell holds N_CHARS=5 partitions FIXED; only per-partition vocab scales with V_C; "
                "anchor projection basis is NOT V_C-scaled in narrative-coref task design"
            ),
        },
        "parent_chain_grade_primitive_for_Q3": {
            "atom_id_pattern": "exp_c3_compressed_sequence_replay_v1*",
            "validated_at": "B_d5=1.000 HARD_PASS K=20",
            "natural_regime_match": "intra-scene sequence binding == Q3 prior-event-in-scene prediction",
            "Q3_V_C_invariance_witness": "this cell shows Q3=1.000 at V_C in {50,200,1000,4000} at seed=7",
        },
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# ATOM 2: math T3 Q3 V_C-invariance MEASURED_MECHANISM (single-seed witness; not chain-grade promotion)
# ============================================================
q3_atom = {
    "id": "T3/EXP_narrative_Q3_temporal_via_sequence_replay_K20_V_C_axis_invariance_single_seed_MEASURED_2026-06-28",
    "name": (
        "narrative Q3 temporal-prediction via c3_compressed_sequence_replay K=20 primitive -- "
        "V_C-axis-invariance MEASURED at single seed=7 across V_C in {50, 200, 1000, 4000} (all 1.000); "
        "single-seed witness only; multi-seed cv promotion deferred"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Q3 temporal-prediction task (predict prior-event-in-scene) via c3_compressed_sequence_replay "
        "K=20 chain-grade primitive (parent: data/exp_c3_compressed_sequence_replay_v1/metrics.json "
        "B_d5=1.000 HARD_PASS) measured across V_C sweep {50, 200, 1000, 4000} at smoke seed=7 "
        "single-seed FULL N_EVENTS=100 5 chars 8 pronouns Q_per_type=8. RESULT: Q3 accuracy "
        "= 1.000 unanimous at all 4 V_C points (4/4 measurement units at this seed). "
        "Q3 V_C-axis-invariance MEASURED at this regime. NOT CHAIN_GRADE PROMOTION (single seed; "
        "cv not computed; META_RULE_AF requires cross-seed cv for chain-grade tier promotion). "
        "Honest under-claim per Fix #28 / BIAS-Q (suspect 1.000): Q3=1.000 is NOT test-trivial; "
        "primitive working as designed at intra-scene local-prediction; partial witness extending "
        "parent atom's regime validation along V_C axis only. "
        "PROMOTION PATH to chain-grade: dispatch sibling chunks seeds {13, 19} (each 4 V_C * 4 arms "
        "= 16 units; ~12 min CPU each); if Q3=1.000 holds with cv<0.05 across {7,13,19} -> promote "
        "to chain-grade narrative_Q3_V_C_invariance witness atom + CERT N +1."
    ),
    "aliases": [
        "narrative_Q3_temporal_via_sequence_replay_K20_V_C_independent_single_seed_2026-06-28",
        "c3_replay_K20_V_C_axis_invariance_at_narrative_Q3_seed_7_witness",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "measured_mechanism",
        "cert_class": "mechanism_characterization",
        "verdict": "Q3_V_C_INVARIANCE_MEASURED_SINGLE_SEED_4_OF_4_UNITS_AT_1p000",
        "cell_commit": CELL_COMMIT,
        "cell_path": CELL_PATH,
        "prereg_path": PREREG_PATH,
        "metrics_path": METRICS_PATH,
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on metrics.json sweep_summary: "
            "Q3=1.000 for ARM_SEQUENCE_REPLAY_Q3 at V_C in [50,200,1000,4000] (4/4 units at seed=7); "
            "verified replay_unanimity=True; SHA distinct from other arms per pred_sha 16/16 "
            "unique across full sweep"
        ),
        "n_seeds_run": 1,
        "seed_run": 7,
        "n_seeds_for_chain_grade_promotion": 3,
        "seeds_pending_for_promotion": [13, 19],
        "promotion_criterion": "cv < 0.05 across 3 seeds * 4 V_C = 12 measurement points; if achieved, promote to chain_grade",
        "cv_status": "NOT_COMPUTED_SINGLE_SEED",
        "regime": {
            "N_HIPPO": 512, "N_CORTEX": 1024, "N_EVENTS": 100,
            "N_CHARS": 5, "K_SCENE_BOUNDARY": 10, "Q_per_type": 8,
            "V_C_axis": [50, 200, 1000, 4000],
            "K_replay": 20,
        },
        "Q3_per_V_C": {"50": 1.0, "200": 1.0, "1000": 1.0, "4000": 1.0},
        "parent_chain_grade_primitive": {
            "atom_id_pattern": "exp_c3_compressed_sequence_replay_v1*",
            "validated_at": "B_d5=1.000 HARD_PASS K=20",
        },
        "BIAS_Q_check": (
            "Suspect 1.000 BIAS-Q: Q3=1.000 NOT by-construction. Replay primitive's natural "
            "operating regime (intra-scene K=20 sequence binding) matches Q3 task design exactly "
            "(predict prior-event-in-scene from S=K_prev.T @ K_curr / n_dim matrix). Not test-trivial; "
            "intra-scene local-prediction at K_SCENE_BOUNDARY=10 is well within K=20 capacity."
        ),
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AM",
            "BIAS-Q", "Fix_28_per_arm_metrics_not_verdict_msg",
        ],
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# ATOM 3: META_RULE_AP_v2 PROMOTION (cert-neutral -> chain-grade-eligible at 2-witness threshold)
# ============================================================
ap_v2_atom = {
    "id": (
        "META_RULE_AP_v2_chain_grade_eligible_composition_of_chain_grade_primitives_requires_signal_shape_"
        "adapter_OR_co_training_OR_pre_cell_compatibility_audit_2_witness_threshold_MET_witness_1_partition_"
        "oracle_substrate_derived_hint_v1_seed_7_HF_route_acc_at_chance_witness_2_narrative_partition_oracle_"
        "V_C_sweep_v1_seed_7_HF_oracle_Q2_at_floor_across_full_V_C_sweep_both_witnesses_show_same_failure_"
        "class_input_output_signal_shape_OR_operating_regime_incompatibility_between_chain_grade_primitive_"
        "validated_regime_AND_downstream_task_regime_SCHEMA_VET_directive_active_supersedes_v1_2026-06-28"
    ),
    "name": (
        "META_RULE_AP_v2 -- chain-grade-eligible PROMOTION via 2nd witness threshold MET "
        "(witness #2: narrative partition oracle V_C sweep HF). Composition of chain-grade primitives "
        "requires signal-shape adapter OR co-training OR pre-cell compatibility audit; SCHEMA-VET "
        "directive active; supersedes META_RULE_AP_v1 cert-neutral"
    ),
    "corpus": "meta",
    "tier": "T_methodology",
    "kind": "discipline_rule",
    "description": (
        "META_RULE_AP_v2 PROMOTION (v1 cert-neutral -> v2 chain-grade-eligible): "
        "v1 promotion_criterion stated '2 independent witness cells of composition-failure rooted in "
        "signal-shape incompatibility OR USER+research consensus'. 2nd independent witness landed "
        "2026-06-28 via narrative_partition_oracle_V_C_sweep HF. Threshold MET. AP promoted to "
        "chain-grade-eligible meta_discipline rule. "
        ""
        "WITNESS #1 (Path 1; atomized 2026-06-28 prior): exp_substrate_partition_oracle_substrate_derived_hint_v1_seed_7 "
        "HARD_FAIL. Composition: chain-grade partition-routing primitive M=10M (input shape: dedicated "
        "category cue c_p) -> multihop chain query (output shape: NO category cue) via naive centroid argmax. "
        "Result: route_acc=0.2173 vs 1/5=0.20 chance; lift -0.40; cascade death. "
        ""
        "WITNESS #2 (Path 3; THIS atomization 2026-06-28): exp_substrate_narrative_partition_oracle_V_C_sweep_v1_seed_7 "
        "HARD_FAIL. Composition: chain-grade partition_oracle_v5 primitive (validated at V_C=4000 ORACLE_C=0.97 "
        "with candidate-anchor projection basis SCALED with V_C) -> narrative-coref Q2 pronoun task (fixed "
        "N_CHARS=5 partitions; per-partition vocab scales with V_C; anchor projection basis NOT V_C-scaled). "
        "Result: oracle_Q2 at floor (0.125) across full V_C sweep {50, 200, 1000, 4000}; no V_C trend; "
        "lift_over_naive 0.000 at V_C=4000. "
        ""
        "BOTH WITNESSES exhibit SAME failure class: primitive A's natural operating regime / signal shape "
        "does not match primitive B's regime / signal shape. Naive composition breaks. The TWO witnesses "
        "differ in (a) primitive used, (b) downstream task, (c) failure mode (cascade death vs floor) -- "
        "yet converge on the same root cause -- making this a generalizable composition-discipline gap. "
        ""
        "v2 ENFORCEMENT (chain-grade-eligible): "
        "(1) SCHEMA-VET REJECTS any prereg proposing primitive-composition without explicit signal-shape "
        "    compatibility audit OR adapter mechanism OR co-training plan. Hard gate; not advisory. "
        "(2) Cell-authors required to document upstream-output-shape + downstream-input-shape + "
        "    compatibility-argument as a pre-reg field before dispatch. "
        "(3) Research dispatches involving primitive-composition automatically queued for AP-audit. "
        "(4) Future composition-failure witnesses extend AP's evidence chain at occurrences #3, #4, ... "
        "    Each new witness atom should link to AP_v2 atom via metadata.composition_discipline_witness. "
        ""
        "SUPERSEDES: META_RULE_AP_v1 (cert-neutral; witness_count=1). v1 atom remains in store as "
        "historical record of the cert-neutral stage; v2 is the authoritative chain-grade-eligible rule. "
        ""
        "CERT delta: +1 (first AP promotion ever; cert-neutral discipline_rule -> chain-grade-eligible "
        "meta_discipline; counts toward CERT N as a chain-grade methodology rule per current Skunkworks "
        "convention)."
    ),
    "aliases": [
        "META_RULE_AP_v2_chain_grade_composition_adapter_discipline_2_witness_threshold_met",
        "composition_of_chain_grade_primitives_requires_signal_shape_audit_PROMOTED_chain_grade_eligible",
        "AP_v2_promotion_2026-06-28",
    ],
    "metadata": {
        "provenance_quality": "DERIVED_FROM_2_INDEPENDENT_WITNESSES",
        "cert_status": "chain_grade_eligible_meta_discipline",
        "cert_class": "meta_discipline",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "rule_letter": "AP",
        "rule_version": "v2",
        "rule_layer": "composition",
        "supersedes_rule_atom_id": f"meta::{AP_V1_ATOM_ID}",
        "promotion_event": "v1_cert_neutral_to_v2_chain_grade_eligible_at_2nd_witness_threshold",
        "extends": ["META_RULE_AM"],
        "related": ["META_RULE_AL", "META_RULE_AN", "META_RULE_AO"],
        "witness_atom_ids": [
            WITNESS_1_AP,
            "math::T3/EXP_narrative_partition_oracle_V_C_sweep_HARD_FAIL_Q2_no_V_C_cliff_2026-06-28",
        ],
        "witness_count": 2,
        "witness_diversity_check": (
            "Two witnesses use DIFFERENT primitives, DIFFERENT downstream tasks, DIFFERENT failure modes; "
            "converge on SAME root cause (operating-regime / signal-shape incompatibility). Failure-class "
            "generalizes beyond single primitive or single task. AP is a real discipline gap, not a "
            "primitive-specific artifact."
        ),
        "promotion_criterion_satisfied": "2_independent_witness_cells_LANDED_2026-06-28",
        "schema_vet_directive_v2_HARD_GATE": (
            "Any prereg proposing primitive-composition MUST include: "
            "(a) upstream primitive natural output signal shape (cue type, dimensionality, basis, regime); "
            "(b) downstream primitive natural input signal shape (cue type, dimensionality, basis, regime); "
            "(c) compatibility ARGUMENT (with specific evidence) OR explicit adapter mechanism OR co-training plan. "
            "Skunkworks SCHEMA-VET will HARD-REJECT preregs lacking ANY of (a), (b), (c). "
            "Hard gate; advisory mode (v1) is closed."
        ),
        "applies_to_in_flight_cells": [
            "exp_dev_acf38256ac9fd3a60_Path_2_vmPFC_schema_Bayes_plus_cortex_partition_plus_hippo_pattern_completion_if_still_in_flight",
            "any_future_HRR_context_bind_narrative_Q2_pivot_cell",
        ],
        "next_actions_for_research": [
            "if_Path_2_HF_lands_extend_AP_evidence_chain_witness_3_no_re_atomization_needed",
            "spawn_HRR_context_bind_for_narrative_Q2_per_drill_escape_hatch_apply_AP_v2_SCHEMA_VET_to_prereg",
            "consider_AP_v3_adapter_mechanism_research_drill_if_3_witnesses_land",
        ],
        "cert_increment_delta": 1,
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
        "HARD_FAIL_ORACLE_NEVER_RESCUES_AT_V_C=4000_smoke_seed_7_FULL_N_EVENTS_100_5_chars_8_pronouns_"
        "Q_per_type_8_oracle_Q2_at_floor_across_full_sweep_V_C_50_200_1000_4000_oracle_max_0p25_lift_"
        "over_naive_0p00_at_V_C_4000_monotone_False_arms_distinct_16_of_16_cardinality_ok_16_of_16_"
        "replay_Q3_1p000_unanimous_positive_control_passed_ROOT_CAUSE_operating_regime_signal_shape_"
        "incompatibility_partition_oracle_v5_validated_with_V_C_scaled_anchor_basis_narrative_coref_holds_"
        "N_CHARS_5_partitions_fixed_wrong_axis_scaling_substituted_cue_magnitude_does_not_discriminate_"
        "META_RULE_AP_witness_2_landed_AP_promotion_threshold_met"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path": METRICS_PATH,
        "prereg_path": PREREG_PATH,
        "cell_path": CELL_PATH,
        "note_path": NOTE_PATH,
        "atom_qualified_id": f"math::{hf_atom['id']}",
    },
    "supersedes": None,
    "note": (
        "narrative_partition_oracle_V_C_sweep_HF_Q2_no_V_C_cliff_seed_7_smoke_FULL_N_partition_oracle_v5_"
        "mechanism_does_not_transfer_to_narrative_coref_at_any_V_C_recommended_pivot_HRR_context_bind_"
        "disambiguator_per_drill_escape_hatch_AP_witness_2_AP_promoted_v1_to_v2_chain_grade_eligible"
    ),
}


# ============================================================
# CERT_LEDGER ROW 2: Q3 V_C-invariance MEASURED_MECHANISM (delta=0; single seed)
# ============================================================
q3_ledger = {
    "ts": time.time(),
    "op": "cert_ruling",
    "atom_id": f"math::{q3_atom['id']}",
    "cert_status": "measured_mechanism",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "Q3_V_C_INVARIANCE_MEASURED_seed_7_single_seed_Q3_equals_1p000_at_V_C_in_50_200_1000_4000_"
        "4_of_4_units_NOT_chain_grade_promotion_cv_not_computed_single_seed_only_BIAS_Q_not_by_construction_"
        "c3_replay_K20_parent_chain_grade_primitive_natural_regime_match_intra_scene_local_prediction_"
        "promotion_to_chain_grade_requires_sibling_seeds_13_19_cv_lt_0p05_threshold"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path": METRICS_PATH,
        "prereg_path": PREREG_PATH,
        "cell_path": CELL_PATH,
        "atom_qualified_id": f"math::{q3_atom['id']}",
    },
    "supersedes": None,
    "note": (
        "Q3_V_C_invariance_single_seed_witness_MEASURED_MECHANISM_NOT_chain_grade_yet_cv_pending_"
        "sibling_seeds_13_19_optional_dispatch_for_chain_grade_promotion_NOT_required_for_now_"
        "primary_finding_is_HF_on_Q2_with_AP_promotion_secondary_finding_is_Q3_axis_invariance_partial_witness"
    ),
}


# ============================================================
# CERT_LEDGER ROW 3: META_RULE_AP_v2 PROMOTION (delta=+1; first AP promotion ever)
# ============================================================
ap_v2_ledger = {
    "ts": time.time(),
    "op": "meta_rule_promotion",
    "atom_id": f"meta::{ap_v2_atom['id']}",
    "cert_status": "chain_grade_eligible_meta_discipline",
    "cert_class": "meta_discipline",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "META_RULE_AP_v2_PROMOTION_from_v1_cert_neutral_to_v2_chain_grade_eligible_meta_discipline_"
        "2_witness_threshold_MET_witness_1_partition_oracle_substrate_derived_hint_v1_HF_witness_2_"
        "narrative_partition_oracle_V_C_sweep_v1_HF_both_show_same_failure_class_operating_regime_OR_"
        "signal_shape_incompatibility_between_chain_grade_primitive_validated_regime_AND_downstream_task_"
        "regime_witness_diversity_check_passed_different_primitives_different_downstream_tasks_different_"
        "failure_modes_converge_on_same_root_cause_SCHEMA_VET_directive_v2_HARD_GATE_active_first_AP_"
        "promotion_ever_CERT_delta_plus_1"
    ),
    "cert_increment_delta": 1,
    "cv": None,
    "referent_pointer": {
        "metrics_path": METRICS_PATH,
        "prereg_path": PREREG_PATH,
        "cell_path": CELL_PATH,
        "atom_qualified_id": f"meta::{ap_v2_atom['id']}",
        "witness_atom_qualified_ids": [
            WITNESS_1_AP,
            f"math::{hf_atom['id']}",
        ],
        "supersedes_atom_qualified_id": f"meta::{AP_V1_ATOM_ID}",
    },
    "supersedes": f"meta::{AP_V1_ATOM_ID}",
    "note": (
        "META_RULE_AP_v2_promoted_chain_grade_eligible_2_witness_threshold_met_SCHEMA_VET_HARD_GATE_active_"
        "applies_to_all_future_primitive_composition_preregs_immediately_first_AP_promotion_ever_CERT_plus_1"
    ),
}


# ============================================================
# A5 WRITE PROTOCOL
# ============================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    """Atomic append with verify-load + integrity-check."""
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"target does not exist: {path}"

    # PRE: read full file + count + integrity-check every line
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

    # Build new content + round-trip validate
    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id"), "round-trip id mismatch"
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id"), "round-trip atom_id mismatch"

    out_lines = pre_lines + [new_line]
    out_text = "\n".join(out_lines) + "\n"

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

    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"], "tail id mismatch"
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"], "tail atom_id mismatch"

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
    print(f"[A5] HF atom_id = math::{hf_atom['id']}")
    print(f"[A5] Q3 atom_id = math::{q3_atom['id']}")
    print(f"[A5] META_RULE_AP_v2 atom_id = meta::{ap_v2_atom['id'][:120]}...")
    print(f"[A5] cert_ledger ops: hf_ruling (delta=0) + q3_mm_ruling (delta=0) + ap_v2_promotion (delta=+1)")

    append_jsonl_a5(MATH_ATOMS, hf_atom, "math/atoms.jsonl [HF]")
    append_jsonl_a5(MATH_ATOMS, q3_atom, "math/atoms.jsonl [Q3_MM]")
    append_jsonl_a5(META_ATOMS, ap_v2_atom, "meta/atoms.jsonl [AP_v2]")
    append_jsonl_a5(CERT_LEDGER, hf_ledger, "meta/cert_ledger.jsonl [hf]")
    append_jsonl_a5(CERT_LEDGER, q3_ledger, "meta/cert_ledger.jsonl [q3_mm]")
    append_jsonl_a5(CERT_LEDGER, ap_v2_ledger, "meta/cert_ledger.jsonl [ap_v2]")

    print(f"[A5] DONE OK; CERT delta = 0 (HF) + 0 (Q3 single-seed MM) + 1 (AP_v2 promotion) = +1 net")


if __name__ == "__main__":
    main()
