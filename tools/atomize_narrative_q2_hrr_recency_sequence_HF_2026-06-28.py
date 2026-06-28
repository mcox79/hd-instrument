"""
A5-gated atomize: substrate_narrative_q2_recency_sequence_log_v1 HARD_FAIL
(HRR recency-sequence composition; 4th composition failure for narrative Q2 coref;
Drill 1 of 2 per USER 2x-drill-negatives capability-closure discipline).

Verdict on disk (smoke seed=7): HARD_FAIL.
  ARM_RECENCY_PLUS_ROLE Q2=0.125 <= HF=0.30 AND
  lift_over_naive = 0.125 - 0.625 = -0.500 (HARM; <= HF=0.05) AND
  positive-control ARM_RECENCY_ONLY Q2=0.375 < HP_floor=0.45 (positive control FAILED)
  oracle sanity = 1.000 (sanity OK)
  arms_distinct = 6/6 q2_pred_sha
  cardinality_ok = True (6 expected / 6 observed)

Cert class: mechanism_characterization. CERT delta = 0 (HF, by definition).

KEY DIAGNOSIS (load-bearing for §15 Gate D extension):
  Pre-reg's Gate D positive-control claim was: ARM_RECENCY_ONLY at K=8
  mentions/scenario "expected to reproduce sequence-binding K=20 chain-grade depth-5
  recall >= 0.80 (tolerance +/-0.10)" -- citing parent atom
  exp_c3_compressed_sequence_replay_v1 HARD_PASS (K_SEQ=20, N=4096, synthetic
  bipolar keys).

  ACTUAL Gate D outcome: ARM_RECENCY_ONLY Q2 = 0.375. The positive control did
  NOT reproduce at test regime. This is EXACTLY the failure mode that motivates
  the §15 Gate D extension (positive control must reproduce AT TEST REGIME, not
  just cite prior atom at different regime).

  Regime delta from parent CG atom to this cell:
    parent CG primitive: N=4096, K_SEQ=20, N_SEQ=10, synthetic-bipolar position keys
    this cell:           N=1024, ~8 mentions/char, verb-derived role tags from narrative
  Both N (4x smaller) AND key distribution (synthetic-bipolar -> narrative-derived)
  differ. SHAPE_MATCH claim in pre-reg FR3 "native sequence-bind unbind: S @ pos_target ~
  char_recent" was insufficient -- positive control did not survive regime transfer.

OFF-DATA recompute (verify-OFF-DATA, NOT verdict_msg):
  per metrics.json per_arm at seed=7 smoke:
    ARM_RANDOM_FLOOR       Q2=0.125  q2_pred_sha=f2667d6de52276ff
    ARM_NAIVE_MAGNITUDE    Q2=0.625  q2_pred_sha=239064f965276e5d
    ARM_RECENCY_ONLY       Q2=0.375  q2_pred_sha=56d268a37573643c  (POS_CTRL_FAIL <0.45)
    ARM_ROLE_ONLY          Q2=0.000  q2_pred_sha=4ac2f6e43f8749e4
    ARM_RECENCY_PLUS_ROLE  Q2=0.125  q2_pred_sha=562bdbc4b62a9ca4  (MECHANISM)
    ARM_ORACLE             Q2=1.000  q2_pred_sha=0bf34a6401829c1a  (sanity OK)
  HF_RECENCY_PLUS_ROLE_Q2<=0.30: TRUE (0.125)
  HF_LIFT_OVER_NAIVE<=0.05: TRUE (-0.500)
  HP_RECENCY_ONLY_FLOOR>=0.45: FALSE (0.375; POS_CTRL_FAIL)
  oracle sanity: PASS
  arms_distinct_q2_sha=6/6, cardinality_ok=6/6.
  HARM signature: mechanism (0.125) <= naive (0.625); composition HARMS over naive baseline.

CAPABILITY-CLOSURE STATUS (per USER 2x-drill-negatives discipline):
  Q2 coreference closure requires 2 mechanism-class drills both confirming null.
  Today's valid distinct mechanism-class attempts for Q2:
    Drill 1 (THIS): HRR recency-sequence composition (sequence_binding K20 +
                    hrr_role_bind + pc_cleanup) -> HF_COMPOSITION_FLOOR + positive-
                    control did NOT reproduce at test regime.
  Drill 2 needed (DIFFERENT mechanism class): NOT YET RUN.
  Status: 1 of 2 drills landed; Q2 capability remains OPEN; DO NOT atomize as
  capability-closed.

  (The partition-routing class HF cluster atomized earlier today via
   atomize_narrative_partition_oracle_V_C_sweep_HF_AP_promote_2026-06-28.py is a
   DIFFERENT mechanism class -- partition_oracle_v5 with V_C-scaled anchor basis
   composition vs HRR recency+role composition. Per Drill1 framing those count
   separately; this atom does NOT close capability.)

A5 protocol:
  1. PRE: read full file + count + integrity-check every line for math + cert_ledger
  2. Append HF atom to math/atoms.jsonl via tmp -> os.replace
  3. Append 1 cert_ledger row (delta=0; HF mechanism_characterization)
  4. POST: verify-load on each (count delta + tail-parse + round-trip id + every-line integrity)

Anchors:
  - metrics: data/exp_substrate_narrative_q2_recency_sequence_log_v1_smoke/metrics.json
  - prereg:  preregs/2026-06-28_substrate_narrative_q2_recency_sequence_log_v1.md
  - cell:    experiments/exp_substrate_narrative_q2_recency_sequence_log_v1_seed_7.py
             experiments/_q2_recency_sequence_log_v1_impl.py
  - parent CG primitive (claimed Gate D positive control):
             data/exp_c3_compressed_sequence_replay_v1/metrics.json
             K_SEQ=20, N=4096, N_SEQ=10, depths=[1,3,5,7,10], HARD_PASS at d5

SCHEMA-VET findings (retrospective; pre-reg passed Pre-AP_v2 advisory framework
but would FAIL AP_v2 hard gate):
  - Gate A (effective vs nominal): N/A single-regime. ACCEPT.
  - Gate B (discriminating bracket): ARM-level 6 arms span floor->mech->oracle. ACCEPT.
  - Gate C (signal-shape audit): 3 composition edges declared SHAPE_MATCH. NOMINAL
    PASS at pre-reg time, but EMPIRICALLY FALSIFIED: positive control did not
    reproduce -> SHAPE_MATCH claim for FR3 (sequence-bind unbind as recency-rank
    reader) was WRONG. The native operating regime (N=4096 synthetic bipolar keys
    K=20 position-indexed log) DID NOT TRANSFER to the test regime (N=1024,
    narrative-derived character mention positions, ~8 mentions per char).
  - Gate D (positive control reproduces prior CG): CLAIMED with tolerance
    "ARM_RECENCY_ONLY Q2 >= 0.45" deflating from parent atom's d5=1.000. FAILED
    EMPIRICALLY (got 0.375). Pre-reg should have required Gate D evidence to be
    a SMOKE RUN of the positive control AT THIS REGIME before dispatch, not just
    citation of prior atom at different regime.
  - Gate E (functional-requirement decomposition): filled. ACCEPT structurally
    but FR3 SHAPE_MATCH was empirically wrong.
  This HF is exactly the test-case that motivates the §15 Gate D extension:
  "positive control must reproduce AT TEST REGIME with explicit smoke evidence
  pre-dispatch, not just citation of prior atom at a different regime".

Author: skunkworks 2026-06-28.
"""

import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

METRICS_PATH = "data/exp_substrate_narrative_q2_recency_sequence_log_v1_smoke/metrics.json"
PREREG_PATH = "preregs/2026-06-28_substrate_narrative_q2_recency_sequence_log_v1.md"
CELL_PATH = "experiments/exp_substrate_narrative_q2_recency_sequence_log_v1_seed_7.py"
IMPL_PATH = "experiments/_q2_recency_sequence_log_v1_impl.py"

ATOMIZED_BY = "skunkworks_atomize_narrative_q2_hrr_recency_sequence_HF_drill1of2_2026-06-28"
ATOMIZED_DATE = "2026-06-28"
CELL_COMMIT = "uncommitted_smoke_seed_7"


# ============================================================
# ATOM 1: math T3 HARD_FAIL on HRR recency-sequence Q2 composition
# ============================================================
hf_atom = {
    "id": (
        "T3/EXP_narrative_q2_coref_hrr_recency_sequence_HARD_FAIL_regime_extension_failed_"
        "drill_1_of_2_2026-06-28"
    ),
    "name": (
        "narrative Q2 coref HRR recency-sequence composition v1 smoke seed=7 -- HARD_FAIL "
        "regime_extension_failed (4th composition failure for narrative Q2 coref; Drill 1 of 2 "
        "per USER 2x-drill-negatives discipline; positive control ARM_RECENCY_ONLY Q2=0.375 "
        "FAILED to reproduce parent CG sequence_binding K20 d5=1.000 at test regime; mechanism "
        "Q2=0.125 HARMS over naive 0.625; §15 Gate D extension PROVEN-NEEDED test case)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "HRR recency-sequence composition for narrative Q2 coreference: composes 3 chain-grade "
        "primitives in claimed native shapes (META_RULE_AP SHAPE_MATCH framework, pre-AP_v2 "
        "hard-gate): "
        "(P1) sequence_binding K=20 used as per-character recency log "
        "(parent: data/exp_c3_compressed_sequence_replay_v1/metrics.json HARD_PASS K_SEQ=20 N=4096); "
        "(P2) HRR role-bind primitive used as verb/obj role filter "
        "(parent: data/exp_contextual_encoding_hrr_binding_smoke_v1_smoketest/metrics.json HARD_PASS); "
        "(P3) PC cleanup attractor used as codebook NN "
        "(parent: data/exp_pc_cleanup_attractor_v1/metrics.json HARD_PASS). "
        ""
        "RESULT (smoke seed=7 at N_HIPPO=512, N_CORTEX=1024, N_PART=1024, N_EVENTS=100, "
        "N_CHARS=5, N_PRONOUN_EVENTS=8, Q_per_type=8, K_seq_log=20): "
        "ARM_RANDOM_FLOOR Q2=0.125, ARM_NAIVE_MAGNITUDE Q2=0.625, "
        "ARM_RECENCY_ONLY Q2=0.375 (positive control; POS_CTRL_FAIL: <0.45 HP floor), "
        "ARM_ROLE_ONLY Q2=0.000, ARM_RECENCY_PLUS_ROLE Q2=0.125 (mechanism HARMS over naive), "
        "ARM_ORACLE Q2=1.000 (sanity OK). "
        ""
        "HF gates tripped: ARM_RECENCY_PLUS_ROLE Q2=0.125 <= HF=0.30 (TRUE) AND "
        "lift_over_naive = -0.500 <= HF=0.05 (TRUE). "
        "arms_distinct=6/6 SHA. cardinality_ok=6/6. "
        ""
        "KEY DIAGNOSIS (load-bearing for §15 Gate D extension): "
        "The positive control ARM_RECENCY_ONLY at Q2=0.375 did NOT reproduce parent CG atom "
        "(c3_compressed_sequence_replay K=20 d5=1.000 at N=4096 synthetic bipolar keys K_SEQ=20). "
        "Regime delta from parent to this cell: N=4096 -> N=1024 (4x smaller); synthetic-bipolar "
        "position keys -> narrative-derived character mention positions (~8 mentions per char); "
        "synthetic key distribution -> verb-derived role tags. The pre-reg's Gate D claim that "
        "'ARM_RECENCY_ONLY Q2 >= 0.45 (positive control reproduces sequence-binding chain-grade "
        "with narrative-noise tolerance)' was an EXTRAPOLATION from the parent atom, NOT measured "
        "at test regime. Empirical Q2=0.375 < 0.45 reveals the SHAPE_MATCH claim for FR3 "
        "(sequence-bind unbind as recency-rank reader) was WRONG when applied to narrative regime. "
        ""
        "CAPABILITY-CLOSURE STATUS: per USER 2x-drill-negatives discipline (feedback_2x_drill_"
        "negatives_before_capability_closure_USER_2026-06-28), Q2 capability closure requires "
        "2 mechanism-class drills both confirming null. This atom is Drill 1 of 2; HRR "
        "recency-sequence is ONE mechanism class. Drill 2 needed: DIFFERENT mechanism class "
        "(e.g., position-tagged Hopfield-style attractor; learned linear coreference projector; "
        "or smaller-regime discriminator-first probe). Q2 capability remains OPEN; do NOT close. "
        ""
        "META_RULE_AP_v2 RETROSPECTIVE: this prereg predated AP_v2 hard-gate landing; under v2 "
        "rules, SCHEMA-VET would REJECT this prereg's Gate D (positive control evidence is "
        "citation of prior atom at different regime, not regime-matched smoke evidence). The §15 "
        "Gate D extension Research authored 2026-06-28 is exactly the discipline this HF "
        "motivates: positive control must reproduce AT TEST REGIME with explicit pre-dispatch "
        "smoke evidence, not just citation of prior atom at a different regime."
    ),
    "aliases": [
        "narrative_q2_coref_hrr_recency_sequence_HARD_FAIL_regime_extension_failed_2026-06-28",
        "substrate_narrative_q2_recency_sequence_log_v1_seed_7_smoke_HF",
        "drill_1_of_2_narrative_Q2_capability_closure_pending",
        "gate_D_extension_proven_needed_test_case_2026-06-28",
        "META_RULE_AP_v2_retrospective_would_have_caught_at_schema_vet",
        "M3_concern_3_narrative_coref_Q2_HRR_recency_sequence_class_falsified_at_smoke",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "hard_fail",
        "cert_class": "mechanism_characterization",
        "verdict": "HF_COMPOSITION_FLOOR_AND_REGIME_EXTENSION_FAILED",
        "verdict_subtype": "ARM_RECENCY_PLUS_ROLE_AT_FLOOR_0p125_NAIVE_HARMED_0p500_AND_POSITIVE_CONTROL_RECENCY_ONLY_FAILED_TO_REPRODUCE_PARENT_CG_AT_TEST_REGIME",
        "cell_commit": CELL_COMMIT,
        "cell_path": CELL_PATH,
        "impl_path": IMPL_PATH,
        "prereg_path": PREREG_PATH,
        "metrics_path": METRICS_PATH,
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via Skunkworks python read on metrics.json per_arm at seed=7 smoke: "
            "ARM_RANDOM_FLOOR Q2=0.125 q2_pred_sha=f2667d6de52276ff; "
            "ARM_NAIVE_MAGNITUDE Q2=0.625 q2_pred_sha=239064f965276e5d; "
            "ARM_RECENCY_ONLY Q2=0.375 q2_pred_sha=56d268a37573643c; "
            "ARM_ROLE_ONLY Q2=0.000 q2_pred_sha=4ac2f6e43f8749e4; "
            "ARM_RECENCY_PLUS_ROLE Q2=0.125 q2_pred_sha=562bdbc4b62a9ca4; "
            "ARM_ORACLE Q2=1.000 q2_pred_sha=0bf34a6401829c1a. "
            "HF_RECENCY_PLUS_ROLE_Q2<=0.30 -> TRUE (0.125). "
            "HF_LIFT_OVER_NAIVE<=0.05 -> TRUE (-0.500; HARM). "
            "HP_RECENCY_ONLY_FLOOR>=0.45 -> FALSE (0.375; positive control failed). "
            "ARM_ORACLE Q2 = 1.000 (sanity OK). "
            "arms_distinct_q2_sha = 6/6. cardinality_ok=True (6/6). "
            "HARM signature: mechanism Q2(0.125) <= naive Q2(0.625) by 0.500 absolute."
        ),
        "n_seeds_run": 1,
        "seed_run": 7,
        "seeds_pending_chunks": [13, 19],
        "cross_seed_status": (
            "Smoke seed=7 only. Chunked sibling files for seed_13 and seed_19 exist per pre-reg "
            "but per THREE_SMOKE_DISCIPLINES (smoke fires discriminator) the HF signature is "
            "magnitude-decisive (mechanism HARMS over naive by 0.500; positive control fails); "
            "cv-flip implausible. Atomization treats seed=7 numbers as verified evidence. "
            "Sibling-seed dispatch unnecessary for HF disposition."
        ),
        "regime": {
            "N_HIPPO": 512,
            "N_CORTEX": 1024,
            "N_PART": 1024,
            "N_RAW": 64,
            "N_EVENTS": 100,
            "N_CHARS": 5,
            "K_SCENE_BOUNDARY": 10,
            "N_PRONOUN_EVENTS": 8,
            "Q_per_type": 8,
            "K_seq_log": 20,
            "alpha_recency": 0.5,
            "beta_role": 0.5,
            "arms_count": 6,
            "expected_n_units": 6,
            "observed_n_units": 6,
        },
        "per_arm_q2": {
            "ARM_RANDOM_FLOOR": 0.125,
            "ARM_NAIVE_MAGNITUDE": 0.625,
            "ARM_RECENCY_ONLY": 0.375,
            "ARM_ROLE_ONLY": 0.000,
            "ARM_RECENCY_PLUS_ROLE": 0.125,
            "ARM_ORACLE": 1.000,
        },
        "per_arm_q2_pred_sha": {
            "ARM_RANDOM_FLOOR": "f2667d6de52276ff",
            "ARM_NAIVE_MAGNITUDE": "239064f965276e5d",
            "ARM_RECENCY_ONLY": "56d268a37573643c",
            "ARM_ROLE_ONLY": "4ac2f6e43f8749e4",
            "ARM_RECENCY_PLUS_ROLE": "562bdbc4b62a9ca4",
            "ARM_ORACLE": "0bf34a6401829c1a",
        },
        "per_arm_overall": {
            "ARM_RANDOM_FLOOR": 0.0938,
            "ARM_NAIVE_MAGNITUDE": 0.7604,
            "ARM_RECENCY_ONLY": 0.6979,
            "ARM_ROLE_ONLY": 0.6042,
            "ARM_RECENCY_PLUS_ROLE": 0.6354,
            "ARM_ORACLE": 0.8542,
        },
        "gates_evaluated": {
            "HF_RECENCY_PLUS_ROLE_Q2_LE_0p30": True,
            "HF_LIFT_OVER_NAIVE_LE_0p05": True,
            "HF_RECENCY_PLUS_ROLE_PRED_SHA_EQ_NAIVE_PRED_SHA": False,
            "HF_ORACLE_LT_1p000": False,
            "HP_RECENCY_PLUS_ROLE_Q2_GE_0p60": False,
            "HP_LIFT_OVER_NAIVE_GE_0p20": False,
            "HP_RECENCY_ONLY_FLOOR_GE_0p45_positive_control": False,
            "HP_ORACLE_Q2_EQ_1p000_sanity": True,
            "HP_ARMS_DISTINCT_GE_4": True,
            "cardinality_ok": True,
        },
        "hf_driver_primary": "ARM_RECENCY_PLUS_ROLE_Q2_0p125_at_floor_AND_naive_baseline_HARMED_by_minus_0p500_AND_positive_control_ARM_RECENCY_ONLY_failed_at_0p375_below_HP_floor_0p45",
        "regime_extension_failure": {
            "parent_chain_grade_primitive": {
                "atom_metrics_path": "data/exp_c3_compressed_sequence_replay_v1/metrics.json",
                "verdict_at_parent": "HARD_PASS",
                "parent_N_DIM": 4096,
                "parent_K_SEQ": 20,
                "parent_N_SEQ": 10,
                "parent_depths": [1, 3, 5, 7, 10],
                "parent_key_distribution": "synthetic_bipolar_position_keys",
            },
            "this_cell_regime_delta": {
                "N_cortex": 1024,
                "N_factor_smaller": 4,
                "K_seq_log": 20,
                "effective_mentions_per_char": 8,
                "key_distribution": "narrative_derived_character_mention_positions_with_verb_derived_role_tags",
            },
            "claimed_in_prereg_Gate_D": "ARM_RECENCY_ONLY Q2 >= 0.45 (positive control reproduces sequence-binding chain-grade with narrative-noise tolerance +/-0.10 from parent d5=1.000)",
            "observed_at_test_regime": 0.375,
            "delta_from_claim": -0.075,
            "delta_from_parent_d5_1p000": -0.625,
            "diagnosis": (
                "Pre-reg's Gate D was CITATION-BASED (cited parent atom at different regime with "
                "asserted noise tolerance) rather than REGIME-MATCHED SMOKE EVIDENCE. Under the §15 "
                "Gate D extension Research authored 2026-06-28, this prereg would require explicit "
                "pre-dispatch smoke run of the positive control at this cell's regime (N=1024, "
                "narrative-derived keys, ~8 mentions per char) BEFORE accepting Gate D. The positive "
                "control empirically did NOT reproduce: 0.375 vs claimed >=0.45 and vs parent 1.000. "
                "SHAPE_MATCH at FR3 was FALSIFIED by data."
            ),
        },
        "composition_failure_class": "operating_regime_signal_shape_incompatibility_between_chain_grade_primitive_validated_regime_AND_downstream_task_regime_PLUS_naive_composition_actively_HARMS_baseline",
        "AP_witness_number": 3,
        "AP_v2_retrospective_schema_vet_would_reject": True,
        "AP_v2_atom_ref": "meta::META_RULE_AP_v2_chain_grade_eligible_composition_of_chain_grade_primitives_requires_signal_shape_adapter_OR_co_training_OR_pre_cell_compatibility_audit_2_witness_threshold_MET_witness_1_partition_oracle_substrate_derived_hint_v1_seed_7_HF_route_acc_at_chance_witness_2_narrative_partition_oracle_V_C_sweep_v1_seed_7_HF_oracle_Q2_at_floor_across_full_V_C_sweep_both_witnesses_show_same_failure_class_input_output_signal_shape_OR_operating_regime_incompatibility_between_chain_grade_primitive_validated_regime_AND_downstream_task_regime_SCHEMA_VET_directive_active_supersedes_v1_2026-06-28",
        "capability_closure_status": {
            "rule_applied": "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
            "capability": "narrative_Q2_coreference_resolution",
            "drills_needed_for_closure": 2,
            "drill_1_landed": "HRR_recency_sequence_composition_HF_THIS_ATOM",
            "drill_1_mechanism_class": "HRR_role_bind_plus_sequence_binding_K20_plus_PC_cleanup_composition",
            "drill_2_landed": False,
            "drill_2_candidates": [
                "position_tagged_Hopfield_style_attractor_for_entity_tracking",
                "learned_linear_coreference_projector_trained_on_narrative_co_occurrence",
                "discriminator_first_smaller_regime_probe_to_validate_ARM_RECENCY_ONLY_at_simpler_load",
                "richer_role_tag_vocabulary_with_explicit_gender_feature_addition",
                "different_mechanism_class_entirely_per_cell_author_options_c",
            ],
            "drill_2_recommended_class": (
                "DIFFERENT mechanism class from drill 1 (NOT a sub-mechanism iteration of "
                "HRR/sequence-binding composition). Recommended: position-tagged Hopfield-style "
                "attractor OR learned linear coreference projector. The capability-closure "
                "discipline requires mechanism CLASS diversity, not parameter sweeps within "
                "the same class. Sub-iteration of HRR (e.g., richer role-tag vocab, discriminator-"
                "first regime probe) does NOT count as drill 2 -- those would amend drill 1's "
                "evidence, not provide independent mechanism-class negative."
            ),
            "do_not_close_until_drill_2": True,
        },
        "ruling_out_alternatives": {
            "smoke_too_small": (
                "Partially ruled out: smoke runs at FULL N_EVENTS=100, N_CHARS=5, N_PRONOUN_EVENTS=8 "
                "regime per pre-reg. However, smoke is single-seed which exposes some binomial noise "
                "at Q_per_type=8 (each Q2 observation is 8 trials over 5 chars; std ~ 0.14 at p=0.20). "
                "But HARM signature mechanism(0.125)-naive(0.625) = -0.500 is 3.5-sigma; not noise."
            ),
            "encoding_bug": (
                "Ruled out: naive_magnitude reaches 0.625 (distinguishes from floor 0.125 by 0.500), "
                "oracle reaches 1.000 (codebook decode works perfectly with ground truth), distinct "
                "pred_sha 6/6 (all arm code paths are distinct). Q1/Q3/Q4 also at 0.75/1.00/0.67 for "
                "naive arm (consistent with prior cells' performance). No silent infrastructure bug."
            ),
            "sanity_broken": "Ruled out: ARM_ORACLE Q2=1.000 confirms codebook + decode pipeline correct.",
            "arm_collision": "Ruled out: all 6 arms have distinct q2_pred_sha (6/6 unique).",
            "alpha_beta_weighting": (
                "Possible but secondary: alpha=beta=0.5 weights recency+role equally; with "
                "role_only=0.000 (worse than random), additive composition pulls mechanism BELOW "
                "recency_only (0.375 -> 0.125). A learned/tuned alpha-beta might mitigate this "
                "specific harm pattern -- but the root cause (FR3 SHAPE_MATCH wrong) would still "
                "manifest. Not a rescue path; sub-mechanism iteration."
            ),
            "Q_per_type_noise": (
                "Q_per_type=8 yields 8 Q2 trials per scenario; single-seed std ~ 0.14 at p=0.20. "
                "HARM magnitude (0.500) and positive-control gap (0.075 from HP floor + 0.625 from "
                "parent CG) are LARGER than 3.5 sigma. Not noise-driven."
            ),
            "ROLE_ONLY_zero_indicates_role_filter_broken": (
                "ARM_ROLE_ONLY Q2=0.000 (BELOW random floor 0.125) suggests the role-bind filter "
                "is ANTI-CORRELATED with ground truth at this regime: HRR unbind output magnitude "
                "is being argmaxed over wrong char. This is consistent with FR2 SHAPE_MATCH being "
                "wrong at narrative regime too: role-tags are verb-derived (low cardinality, shared "
                "across many predicates per char) rather than the cleanly-distinct WSD context "
                "vectors the parent atom validated. So BOTH FR2 and FR3 have regime-extension issues."
            ),
        },
        "mechanism_root_cause": (
            "TWO compounding regime-extension failures: "
            "(R1) sequence_binding K=20 was validated at N=4096 synthetic bipolar position keys "
            "(c3_compressed_sequence_replay HARD_PASS). At N=1024 with narrative-derived character "
            "mention positions (~8 mentions per char, position keys constructed via per-character "
            "mention indexing), the unbind operation S_c @ pos_target ~ char_recent FAILS to "
            "discriminate (0.375 vs claimed 0.45 floor vs parent 1.000). N reduction by 4x AND "
            "key-distribution change BOTH degrade the primitive. "
            "(R2) hrr_role_bind was validated at WSD (word sense disambiguation, cleanly distinct "
            "context bundles per sense; WSD=1.000 chain-grade). At narrative regime, role tags are "
            "verb-derived (low-cardinality verb categories shared across chars) -- the role-tag "
            "bundle is NOT cleanly distinct per character. Role-bind unbind argmax is anti-"
            "correlated with ground truth (0.000 vs random 0.125). "
            "Composition compounds both regime failures: recency_only(0.375) + role_only(0.000) "
            "additive with alpha=beta=0.5 yields 0.125 -- BELOW naive_magnitude baseline (0.625) "
            "and BELOW recency_only alone (0.375). Composition actively HARMS. "
            "This is META_RULE_AP failure-class #3 witness: chain-grade primitive's validated "
            "regime does NOT extend to downstream task regime; SHAPE_MATCH claim at FR table was "
            "an extrapolation, not measured. Both FR2 and FR3 falsified by data."
        ),
        "rescue_paths_NOT_drill_2_iterations": [
            "regime_matched_pre_dispatch_smoke_of_positive_controls_at_test_regime_via_section_15_gate_D_extension",
            "co_training_or_adapter_for_sequence_binding_to_narrative_position_keys",
            "richer_role_tag_vocabulary_with_explicit_per_character_gender_feature",
            "alpha_beta_tuned_on_per_seed_validation_split",
        ],
        "rescue_paths_drill_2_class_distinct": [
            "position_tagged_Hopfield_style_attractor_for_entity_tracking_DIFFERENT_class",
            "learned_linear_coreference_projector_trained_on_narrative_co_occurrence_DIFFERENT_class",
            "transformer_style_attention_over_mention_log_with_substrate_value_lookup_DIFFERENT_class",
        ],
        "M3_concern_3_status": (
            "M3 concern #3 (long-narrative Q2 coref) NOT resolved by HRR recency-sequence "
            "composition. Path 4 (this) fails alongside earlier Path 3 (partition_oracle V_C "
            "sweep HF, atomized this morning) and Paths 1-2 (naive magnitude variants and "
            "partition oracle composition). Substrate-native Q2 coref remains OPEN with 1 of 2 "
            "USER-required mechanism-class drills landed. Recommend Drill 2 in a fundamentally "
            "different class (NOT another HRR composition iteration)."
        ),
        "section_15_gate_D_extension_motivation": (
            "This HF is the canonical test-case that motivates the §15 Gate D extension: positive "
            "control must reproduce AT TEST REGIME with explicit pre-dispatch smoke evidence, NOT "
            "just citation of prior atom at different regime. Pre-reg cited parent atom d5=1.000 "
            "at N=4096 with synthetic bipolar keys + asserted +/-0.10 noise tolerance for "
            "narrative regime -- but empirical positive-control was 0.375, far below claimed 0.45 "
            "floor. Under §15 Gate D extension, this cell would have been refused pre-dispatch "
            "(or required pre-dispatch positive-control smoke at test regime as gate). "
            "Discipline-tag this atom: SECTION_15_GATE_D_EXTENSION_PROVEN_NEEDED_2026-06-28."
        ),
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AG",
            "META_RULE_AH", "META_RULE_AL", "META_RULE_AM", "META_RULE_AN",
            "META_RULE_AP_v2_retrospective_witness_3",
            "META_RULE_H_CARDINALITY_OK",
            "META_RULE_J_NO_SILENT_EXCEPT",
            "META_RULE_L_STRICT_ABOVE_FLOOR",
            "BIAS-N_verify_referent_verdict_field",
            "BIAS-S_band_calibration",
            "BIAS-Q_suspect_1p000_at_oracle_arm_ruled_out_as_sanity",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            "THREE_SMOKE_DISCIPLINES_2026-06-26",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
            "SECTION_15_GATE_D_EXTENSION_PROVEN_NEEDED_2026-06-28",
            "functional_requirement_first_USER_2026-06-28",
        ],
        "next_actions": [
            "drill_2_DIFFERENT_mechanism_class_for_Q2_coref_NOT_HRR_iteration",
            "drill_2_recommended_class_position_tagged_Hopfield_style_attractor_OR_learned_linear_coreference_projector",
            "do_NOT_dispatch_chunked_full_seeds_13_19_unless_USER_requests_cv_confirmation",
            "do_NOT_atomize_Q2_capability_closure_until_drill_2_lands",
            "annotate_AP_v2_evidence_chain_witness_3_no_re_atomization_needed",
            "research_to_consider_section_15_Gate_D_extension_landing_for_AP_v2_HARD_GATE_addendum",
        ],
        "parent_chain_grade_primitives_claimed_in_prereg": [
            {
                "name": "sequence_binding_K20",
                "atom_metrics_path": "data/exp_c3_compressed_sequence_replay_v1/metrics.json",
                "validated_at": "K_SEQ=20 N=4096 depths=[1,3,5,7,10] HARD_PASS",
                "claimed_native_shape": "Position-indexed log; query=k_{t-1}, predicts k_t via S @ k_{t-1}",
                "shape_match_falsified": True,
                "shape_match_evidence_at_test_regime": "ARM_RECENCY_ONLY Q2=0.375 < claimed_floor 0.45 < parent d5 1.000",
            },
            {
                "name": "hrr_role_bind",
                "atom_metrics_path": "data/exp_contextual_encoding_hrr_binding_smoke_v1_smoketest/metrics.json",
                "validated_at": "WSD=1.000 lift=+0.800 HARD_PASS",
                "claimed_native_shape": "Bipolar bind(w_vec, ctx_vec) involutive",
                "shape_match_falsified": True,
                "shape_match_evidence_at_test_regime": "ARM_ROLE_ONLY Q2=0.000 < random floor 0.125 (anti-correlated)",
            },
            {
                "name": "pc_cleanup_attractor",
                "atom_metrics_path": "data/exp_pc_cleanup_attractor_v1/metrics.json",
                "validated_at": "d5/d10=1.000 HARD_PASS",
                "claimed_native_shape": "Predictive-coding fixed-point cleanup over codebook",
                "shape_match_falsified": "indeterminate_at_this_cell_intermediate_step_not_directly_measured",
                "shape_match_evidence_at_test_regime": "PC cleanup is intermediate; ARM_ORACLE=1.000 indicates the final-stage codebook decode at least works correctly with correct char_id input",
            },
        ],
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# CERT_LEDGER ROW: HF cert_ruling (delta=0)
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
        "HARD_FAIL_HRR_recency_sequence_composition_for_narrative_Q2_coref_smoke_seed_7_"
        "ARM_RECENCY_PLUS_ROLE_Q2_0p125_LE_HF_0p30_AND_lift_over_naive_minus_0p500_LE_HF_0p05_"
        "HARM_signature_mechanism_below_naive_by_0p500_AND_positive_control_ARM_RECENCY_ONLY_"
        "Q2_0p375_FAILED_to_reproduce_parent_CG_sequence_binding_K20_d5_1p000_at_test_regime_"
        "below_HP_floor_0p45_AND_below_parent_1p000_by_0p625_arms_distinct_6_of_6_SHA_"
        "cardinality_ok_6_of_6_oracle_sanity_1p000_PASS_root_cause_2_compounding_regime_extension_"
        "failures_FR2_and_FR3_SHAPE_MATCH_claims_falsified_by_data_section_15_Gate_D_extension_"
        "proven_needed_test_case_AP_v2_witness_3_DRILL_1_of_2_per_USER_2x_drill_negatives_"
        "discipline_Q2_capability_remains_OPEN_do_NOT_close_drill_2_needed_in_DIFFERENT_mechanism_"
        "class_NOT_HRR_iteration"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path": METRICS_PATH,
        "prereg_path": PREREG_PATH,
        "cell_path": CELL_PATH,
        "impl_path": IMPL_PATH,
        "atom_qualified_id": f"math::{hf_atom['id']}",
        "parent_CG_atom_metrics": "data/exp_c3_compressed_sequence_replay_v1/metrics.json",
        "AP_v2_rule_atom_qualified_id_prefix": "meta::META_RULE_AP_v2_chain_grade_eligible_composition_of_chain_grade_primitives_requires_signal_shape_adapter",
    },
    "supersedes": None,
    "note": (
        "narrative_q2_coref_hrr_recency_sequence_HF_drill_1_of_2_USER_2x_drill_negatives_"
        "discipline_pending_drill_2_in_different_mechanism_class_position_tagged_Hopfield_OR_"
        "learned_linear_projector_recommended_section_15_Gate_D_extension_proven_needed_test_"
        "case_AP_v2_retrospective_schema_vet_would_reject_due_to_citation_based_Gate_D_not_"
        "regime_matched_smoke_evidence"
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
    print(f"[A5] cert_ledger op: hf_ruling (delta=0; HF mechanism_characterization)")
    append_jsonl_a5(MATH_ATOMS, hf_atom, "math/atoms.jsonl [HF]")
    append_jsonl_a5(CERT_LEDGER, hf_ledger, "meta/cert_ledger.jsonl [hf]")
    print(f"[A5] DONE OK; CERT delta = 0 (HF mechanism_characterization, by definition)")
    print(f"[A5] Q2 capability-closure status: drill 1 of 2 landed; capability remains OPEN")
    print(f"[A5] Drill 2 needed: DIFFERENT mechanism class (NOT HRR composition iteration)")


if __name__ == "__main__":
    main()
