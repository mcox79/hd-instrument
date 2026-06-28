"""
A5-gated atomize: substrate_narrative_q2_coref_lappin_leass_drill2_v1 -- ORACLE-LEAK INVALID

DISPOSITION: HARD_FAIL_ORACLE_LEAK_INVALIDATES_REPORTED_HARD_PASS

LANDED VERDICTS ON DISK (3-seed full):
  seed=7  reported HARD_PASS  (lappin_Q2=0.875, lift_over_naive=+0.250 vs naive 0.625)
  seed=13 reported HARD_PASS  (lappin_Q2=0.875, lift_over_naive=+0.750 vs naive 0.125)
  seed=19 reported MIDDLE_BAND (lappin_Q2=0.750, lift_over_naive=+0.625 vs naive 0.125)

SKUNKWORKS LANDED-VET (verify-OFF-DATA, NOT verdict_msg):
  Off-disk recompute via independent feature-ablation confirms the cell-author's
  reported per-arm numbers exactly reproduce. The PROBLEM is not numeric integrity
  -- it is the MECHANISM CLAIM.

  The pre-reg's Gate E (functional-requirement decomposition) claimed all 5 Lappin-
  Leass feature inputs come from substrate state:
    "FR1 mention positions from partition store W_part[c]"
    "FR2 scene-membership readout from W_part[c]"
    "FR3 subject-role tally from W_part[c]"
    "FR4 scene-focus pointer from narrative scene-focus tracker"
    "FR5 parallelism from mention history + verb-id comparison"

  ACTUAL implementation (per-source-read of _q2_lappin_leass_drill2_v1_impl.py):

  - _build_mention_history(narr) (line 619-639):
      for ev in narr.events:
          if ev.get("is_pronoun"): continue
          c = ev["char_id"]    # <-- reads narrative ground truth dict
          table[c].append({
              "pos": ev["event_idx"],
              "scene_id": ev["scene_id"],
              "role_tag_idx": ev["role_tag_idx"],
              "is_subject_role": ev["is_subject_role"],
              "verb_id": ev["verb_id"],
          })

    The function reads the narrative event dict DIRECTLY. NO W_part query. NO
    cortex readout. The docstring admits this explicitly:
      "Substrate-faithful: this is what the partition store would extract via
       per-character query against W_part[c]; we compute it directly here to
       keep the cell numpy-only without a full cortex-readout layer."

    This is an explicit oracle-bypass: feature extractors consume ground-truth
    narrative dict rather than substrate-recovered state. None of the
    pre-reg Gate E features actually consult the substrate.

  - _feature_focus(c, scene_id_pronoun, narr) (line 672-676):
      if int(narr.scene_focus[scene_id_pronoun]) == int(c):
          return 1.0
      return 0.0

    This reads narr.scene_focus, which is the corpus's ground-truth scene-focus
    table. Combined with narrative-gen line 396 (`ev["char_id"] = scene_focus[
    scene_id]` for ALL pronoun events), this f_focus feature IS the ground-truth
    Q2 answer for every pronoun query.

  - The discriminator-must-fire gate at line 1097-1098 mentions that f_focus is
    "also the naive baseline" and "must add INFORMATION beyond it", but the
    verdict-logic at line 1015-1022 then EXEMPTS the (ARM_LAPPIN_LEASS_FULL
    pred_sha == ARM_SCENE_FOCUS_ONLY pred_sha) collision from META_RULE_AF check
    -- explicitly calling it "expected at HARD_PASS" since scene_focus IS the
    ground-truth-for-pronouns by corpus construction. This is bias-justification,
    not bias-prevention.

  Empirical confirmation via Skunkworks independent recompute (Q2 ablation):

  | seed | full Lappin-Leass | no_focus (rec+scene+subj+par) | only_focus (W_FOCUS * f_foc) |
  |------|---|---|---|
  |  7   | 7/8 = 0.875       | 4/8 = 0.500                   | 8/8 = 1.000                   |
  | 13   | 7/8 = 0.875       | 4/8 = 0.500                   | 8/8 = 1.000                   |
  | 19   | 6/8 = 0.750       | 2/8 = 0.250                   | 8/8 = 1.000                   |

  The "only_focus" ablation (W_FOCUS=40.0 * f_focus, with all 4 other features
  zeroed out) gives perfect 1.000 across all 3 seeds. This is the same arm as
  ARM_SCENE_FOCUS_ONLY (q2_pred_sha matches ARM_ORACLE exactly across all 3
  seeds; verified in metrics.json arms_must_differ_q2_pred_sha block).

  The OTHER 4 "substrate features" (recency / scene / subject / parallelism)
  collectively achieve only 0.500 / 0.500 / 0.250 -- WORSE than the noise-floor
  for the corpus structure. They actively DEGRADE the f_focus oracle: full
  Lappin-Leass (0.875/0.875/0.750) is BELOW the f_focus-only ablation (1.000)
  because the other 4 features inject noise that occasionally outvotes the
  ground-truth focus pointer.

  The "mechanism" is therefore: read ground-truth scene_focus from the narrative
  dict (which IS the Q2 answer for all pronoun events), weight it at 40.0, mix
  in 4 narrative-ground-truth-derived "features" that average lower than the
  noise threshold, argmax. This is not a symbolic algorithm over substrate
  features -- it's a noised oracle lookup.

ORACLE-LEAK CLASSIFICATION (per BIAS-Q + experiment-bias-master-checklist):
  - BIAS-13 (by-construction-saturation): ARM_SCENE_FOCUS_ONLY Q2=1.000 across
    all 3 seeds and identical q2_pred_sha to ARM_ORACLE -- pinned saturated by
    corpus construction (narrative-gen line 396).
  - BIAS-Q (suspect 1.000 results): ARM_ORACLE Q2=1.000 is expected; ARM_SCENE_
    FOCUS_ONLY Q2=1.000 is *the smoking gun* (scene_focus lookup IS the answer).
  - BIAS-N (verify-the-referent): cell claims "substrate provides FEATURES"
    (pre-reg Gate E + DESIGN_NOTE in metrics.json) but features are extracted
    from narrative dict ground truth, not from substrate state (W_part / cortex
    readout / partition store). Referent mismatch.
  - META_RULE_AF (arms-must-differ pred_sha): SCENE_FOCUS_ONLY pred_sha ==
    ORACLE pred_sha across all 3 seeds. The cell's verdict-logic at line 1015-
    1022 exempts this collision; it should NOT (oracle-class arm should never
    share pred_sha with ground-truth oracle arm unless explicitly an upper-
    bound positive control, which is what ORACLE is).

  Discipline-rule violation: META_RULE_AP_v3 (substrate primitives must operate
  on substrate-recovered state, not ground-truth dict references). The cell's
  feature extractors are not chain-grade-eligible compositions -- they bypass
  the substrate entirely.

DISPOSITION:
  HARD_FAIL_ORACLE_LEAK_INVALIDATES_REPORTED_HARD_PASS. The reported HARD_PASS
  verdicts for seeds 7 and 13 (and MIDDLE_BAND for seed 19) are NOT evidence
  of substrate capability for Q2 coref. The "mechanism" is a noised oracle
  lookup that bypasses the substrate via direct narrative-dict reads.

CAPABILITY-CLOSURE STATUS:
  Drill 2 (this) does NOT satisfy the USER 2x-drill-before-capability-closure
  rule. The rule requires a GENUINELY DIFFERENT mechanism class to be tested;
  this cell tested narrative-ground-truth-dict-lookup masquerading as Lappin-
  Leass. Q2 capability remains OPEN with 1 of 2 valid drills landed (Drill 1 =
  HRR recency-sequence HF; this drill = INVALID-mechanism).

  Drill 2 is NEEDED in a mechanism class that ACTUALLY consults substrate state:
    Option A: build the Lappin-Leass features from W_part[c] cosine queries
              (per-char recency via partition cosine, scene-membership via cortex
              key-query, etc.) -- substrate-faithful version of this cell.
    Option B: position-tagged Hopfield-style attractor over substrate state.
    Option C: learned linear coreference projector trained on substrate state
              (parallel to Barrier 1 drill 2 design pattern).

  The valid options share a substrate-state forward pass; the failed cell does
  not.

CERT DELTA: 0 (HF mechanism_characterization; the "passing" verdicts are
oracle-leak artifacts; capability-closure unaffected).

A5 protocol:
  1. PRE: read full math/atoms.jsonl + count + integrity-check every line
  2. Append 1 INVALID atom + 1 mechanism-ruled-out atom + 1 meta-rule witness
     to math/atoms.jsonl
  3. Append matching cert_ledger rows (delta=0; HF; INVALID-MECHANISM-CLAIM)
  4. POST: verify-load (count delta + tail parse + round-trip id + every-line
     integrity)

Anchors:
  - cell:  experiments/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_{7,13,19}.py
  - impl:  experiments/_q2_lappin_leass_drill2_v1_impl.py
  - prereg: preregs/2026-06-28_substrate_narrative_q2_coref_lappin_leass_drill2_v1.md
  - metrics: data/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_{7,13,19}/metrics.json
  - drill 1: data/exp_substrate_narrative_q2_recency_sequence_log_v1_smoke/metrics.json (HF; atomized)

Author: skunkworks 2026-06-28 (audit of main-thread-authored cell).
"""

import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

METRICS_PATHS = {
    "seed_7":  "data/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_7/metrics.json",
    "seed_13": "data/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_13/metrics.json",
    "seed_19": "data/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_19/metrics.json",
}
PREREG_PATH = "preregs/2026-06-28_substrate_narrative_q2_coref_lappin_leass_drill2_v1.md"
IMPL_PATH = "experiments/_q2_lappin_leass_drill2_v1_impl.py"
CELL_PATH_SEED_7 = "experiments/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_7.py"

ATOMIZED_BY = "skunkworks_atomize_narrative_q2_lappin_leass_drill2_ORACLE_LEAK_INVALID_2026-06-28"
ATOMIZED_DATE = "2026-06-28"
CELL_COMMIT = "uncommitted_main_thread_authored_q2_lappin_leass_drill2"


# Common verified-off-data evidence string
VERIFIED_OFF_DATA = (
    "Skunkworks independent recompute via .venv python on metrics.json per_arm fields "
    "+ feature-ablation reconstruction over narrative-gen Narrative class and "
    "_q2_lappin_leass_drill2_v1_impl feature functions. "
    "Cross-seed Q2: ARM_LAPPIN_LEASS_FULL mean=0.8333 sd=0.0589 vals=[0.875, 0.875, 0.750]; "
    "ARM_SCENE_FOCUS_ONLY mean=1.000 sd=0.000 vals=[1.000, 1.000, 1.000]; "
    "ARM_NAIVE_MAGNITUDE mean=0.2917 sd=0.2357 vals=[0.625, 0.125, 0.125]; "
    "ARM_ORACLE mean=1.000 sd=0.000 vals=[1.000, 1.000, 1.000]. "
    "ARM_SCENE_FOCUS_ONLY q2_pred_sha == ARM_ORACLE q2_pred_sha across all 3 seeds "
    "(seed_7: both = 0bf34a6401829c1a; seed_13: both = 6ddde45e2077e802; "
    "seed_19: both = c889b430f8a34a7f). "
    "Feature ablation (Skunkworks independent recompute over narrative): "
    "(1) full Lappin-Leass 5-feature scorer: seed_7=0.875 seed_13=0.875 seed_19=0.750; "
    "(2) no_focus ablation (rec+scene+subj+par; f_focus zeroed): "
    "seed_7=0.500 seed_13=0.500 seed_19=0.250 -- WORSE than naive random baseline; "
    "(3) only_focus ablation (W_FOCUS * f_focus; other 4 features zeroed): "
    "seed_7=1.000 seed_13=1.000 seed_19=1.000 -- PERFECT and identical to ARM_SCENE_FOCUS_ONLY. "
    "The full Lappin-Leass mechanism is WORSE than only-f_focus across all seeds -- the other "
    "4 substrate-claimed features inject noise that degrades the ground-truth oracle. "
    "_build_mention_history(narr) reads narr.events dict directly (no W_part query); "
    "_feature_focus(c, scene_id, narr) reads narr.scene_focus dict directly. "
    "Narrative-gen line 396: `ev['char_id'] = scene_focus[scene_id]` for all pronoun events "
    "-- meaning scene_focus lookup IS the Q2 ground-truth answer by corpus construction."
)


# ============================================================
# ATOM 1: 3 per-seed INVALID atoms (one per seed) — the 3 cell results
# Each documents the per-seed disposition with oracle-leak diagnosis.
# ============================================================

def make_per_seed_invalid_atom(seed: int, reported_verdict: str,
                                lappin_q2: float, naive_q2: float,
                                rec_q2: float, sf_q2: float, oracle_q2: float,
                                lift_over_naive: float, metrics_path: str) -> dict:
    return {
        "id": (
            "T3/EXP_narrative_q2_coref_lappin_leass_drill2_seed_%d_"
            "INVALID_MECHANISM_oracle_leak_via_narrative_dict_direct_reads_"
            "reported_%s_2026-06-28"
        ) % (seed, reported_verdict.lower()),
        "name": (
            "narrative Q2 coref Lappin-Leass drill 2 seed=%d -- INVALID-MECHANISM "
            "(reported %s; cell-author-claimed substrate-feature symbolic scorer "
            "actually reads narr.events + narr.scene_focus ground-truth dicts "
            "directly; ARM_SCENE_FOCUS_ONLY q2_pred_sha == ARM_ORACLE q2_pred_sha "
            "by corpus construction line 396; feature-ablation: only_focus=1.000 vs "
            "full mech=%.3f vs no_focus=%.3f -- mechanism is noised oracle lookup, "
            "not substrate readout)"
        ) % (seed, reported_verdict, lappin_q2,
             {7: 0.500, 13: 0.500, 19: 0.250}[seed]),
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": (
            "Drill 2 of 2x-drill-before-capability-closure for narrative Q2 coref "
            "(symbolic Lappin-Leass weighted-salience scorer over claimed substrate "
            "features). Cell reported verdict for seed=%d = %s. SKUNKWORKS AUDIT: "
            "the mechanism class claimed in pre-reg Gate E (5 features extracted from "
            "substrate state: W_part partition store, scene tagging, role-tag tally, "
            "scene-focus pointer, parallelism heuristic) was NOT implemented as "
            "claimed. Instead: (a) _build_mention_history(narr) iterates over "
            "narr.events directly and reads ev['char_id']/scene_id/role_tag_idx/"
            "is_subject_role/verb_id from the corpus dict, NOT from W_part[c]; "
            "(b) _feature_focus(c, scene_id, narr) reads narr.scene_focus directly. "
            "Per narrative-gen line 396, pronoun events have ev['char_id'] = "
            "scene_focus[scene_id], so f_focus IS the Q2 ground-truth answer. "
            "ARM_SCENE_FOCUS_ONLY q2_pred_sha == ARM_ORACLE q2_pred_sha across all "
            "3 seeds. Feature-ablation: only_focus=1.000 vs full_mech=%.3f vs "
            "no_focus=%.3f -- the other 4 'substrate features' inject noise that "
            "DEGRADES the oracle lookup. The 'mechanism' is a noised oracle, not "
            "a substrate-feature symbolic scorer. The reported HARD_PASS / "
            "MIDDLE_BAND verdicts are oracle-leak artifacts and do NOT count toward "
            "Q2 capability evidence. "
            "MEASURED (per metrics.json per_arm at seed=%d): "
            "ARM_LAPPIN_LEASS_FULL Q2=%.3f, ARM_NAIVE_MAGNITUDE Q2=%.3f, "
            "ARM_SCENE_FOCUS_ONLY Q2=%.3f, ARM_RECENCY_ONLY_DRILL2 Q2=%.3f, "
            "ARM_ORACLE Q2=%.3f, lift_over_naive=%.3f. arms_distinct_q2_sha=5/6 "
            "(SF==ORACLE collision). cardinality_ok=6/6."
        ) % (seed, reported_verdict, lappin_q2,
             {7: 0.500, 13: 0.500, 19: 0.250}[seed],
             seed, lappin_q2, naive_q2, sf_q2, rec_q2, oracle_q2,
             lift_over_naive),
        "aliases": [
            "narrative_q2_coref_lappin_leass_drill2_seed_%d_ORACLE_LEAK_INVALID_2026-06-28" % seed,
            "substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_%d_INVALID_MECHANISM" % seed,
            "Q2_drill_2_oracle_leak_does_not_satisfy_capability_closure_seed_%d" % seed,
            "META_RULE_AP_v3_witness_substrate_primitive_must_actually_consult_substrate_seed_%d" % seed,
            "BIAS_Q_BIAS_13_witness_arm_pred_sha_equals_oracle_by_corpus_construction_seed_%d" % seed,
            "main_thread_authored_cell_skunkworks_caught_oracle_leak_at_landed_VET_seed_%d" % seed,
        ],
        "metadata": {
            "provenance_quality": "MEASURED",
            "cert_status": "hard_fail",
            "cert_class": "mechanism_characterization",
            "verdict": "HARD_FAIL_ORACLE_LEAK_INVALIDATES_REPORTED_%s" % reported_verdict,
            "verdict_subtype": "MECHANISM_IS_NOISED_ORACLE_LOOKUP_NOT_SUBSTRATE_FEATURE_SYMBOLIC_SCORER",
            "reported_verdict_by_cell": reported_verdict,
            "skunkworks_override_to": "hard_fail_oracle_leak_invalid",
            "cell_commit": CELL_COMMIT,
            "cell_path": "experiments/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_%d.py" % seed,
            "impl_path": IMPL_PATH,
            "prereg_path": PREREG_PATH,
            "metrics_path": metrics_path,
            "atomized_by": ATOMIZED_BY,
            "atomized_date": ATOMIZED_DATE,
            "verified_off_data": True,
            "verified_off_data_evidence": VERIFIED_OFF_DATA,
            "main_thread_authored": True,
            "main_thread_authored_disclosure": "USER and Director both disclosed at task spawn that this cell was authored in main thread (not via hdi_exp_dev sub-agent) and is audit-suspect. Skunkworks audit caught the oracle-leak via independent feature-ablation recompute.",
            "n_seeds_run": 1,
            "seed_run": seed,
            "regime": {
                "N_HIPPO": 512, "N_CORTEX": 1024, "N_PART": 1024,
                "N_EVENTS": 100, "N_CHARS": 5, "K_SCENE_BOUNDARY": 10,
                "N_PRONOUN_EVENTS": 8, "Q_per_type": 8, "arms_count": 6,
                "expected_n_units": 6, "observed_n_units": 6,
            },
            "per_arm_q2": {
                "ARM_RANDOM_FLOOR": {7: 0.125, 13: 0.250, 19: 0.000}[seed],
                "ARM_NAIVE_MAGNITUDE": naive_q2,
                "ARM_SCENE_FOCUS_ONLY": sf_q2,
                "ARM_RECENCY_ONLY_DRILL2": rec_q2,
                "ARM_LAPPIN_LEASS_FULL": lappin_q2,
                "ARM_ORACLE": oracle_q2,
            },
            "feature_ablation_skunkworks_independent_recompute": {
                "full_lappin_leass_5_feature": lappin_q2,
                "no_focus_4_feature_rec_scene_subj_par": {7: 0.500, 13: 0.500, 19: 0.250}[seed],
                "only_focus_W_focus_times_f_focus": 1.000,
                "interpretation": (
                    "only_focus_ablation_perfect_means_W_FOCUS_dot_f_focus_IS_the_oracle; "
                    "no_focus_ablation_below_random_floor_means_other_4_substrate_claimed_features_"
                    "carry_NEGATIVE_information_for_Q2_relative_to_corpus_construction; "
                    "full_lappin_leass_is_BELOW_only_focus_because_other_4_features_inject_noise_"
                    "that_occasionally_outvotes_the_ground_truth_focus_pointer"
                ),
            },
            "oracle_leak_evidence": {
                "narrative_gen_line_396": "ev['char_id'] = scene_focus[scene_id] for ALL pronoun events",
                "_build_mention_history_line_619_to_639": "reads narr.events dict directly; reads ev['char_id'], ev['scene_id'], ev['role_tag_idx'], ev['is_subject_role'], ev['verb_id'] from corpus ground-truth; NO W_part[c] query; NO cortex readout",
                "_build_mention_history_docstring_admission": "we compute it directly here to keep the cell numpy-only without a full cortex-readout layer",
                "_feature_focus_line_672_to_676": "reads narr.scene_focus directly; returns 1.0 iff narr.scene_focus[scene_id_pronoun] == c (this is the Q2 ground-truth lookup)",
                "ARM_SCENE_FOCUS_ONLY_q2_pred_sha_equals_ARM_ORACLE_q2_pred_sha": "True across all 3 seeds (seed_7: 0bf34a6401829c1a; seed_13: 6ddde45e2077e802; seed_19: c889b430f8a34a7f)",
                "cell_verdict_logic_line_1015_to_1022": "EXEMPTS the SF==ORACLE pred_sha collision from META_RULE_AF check, calling it 'expected at HARD_PASS' -- bias-justification not bias-prevention",
            },
            "discipline_rule_violations": [
                "META_RULE_AP_v3_substrate_primitive_must_actually_consult_substrate_state",
                "BIAS_13_by_construction_saturation_arm_pinned_at_1p000_by_corpus_construction",
                "BIAS_Q_suspect_1p000_results_ARM_SCENE_FOCUS_pinned_oracle_class",
                "BIAS_N_verify_the_referent_mechanism_referent_is_noised_oracle_not_symbolic_scorer",
                "META_RULE_AF_arms_must_differ_q2_pred_sha_SF_equals_ORACLE_should_NOT_be_exempted_in_verdict_logic",
                "preReg_Gate_E_functional_requirement_decomposition_false_substrate_provides_features_claim",
                "preReg_DESIGN_NOTE_substrate_provides_FEATURE_INPUTS_claim_falsified_by_implementation",
                "pre_VET_authorship_path_violation_main_thread_authored_skipped_hdi_exp_dev_sub_agent_role_separation",
            ],
            "what_a_valid_drill_2_would_look_like": (
                "A valid drill 2 must consult substrate state for each feature. For example: "
                "(a) f_recency: cosine similarity between cortex query at pronoun position and "
                "cortex key bank at each (char, position) -- W @ key readout, NOT mention_history "
                "dict lookup; "
                "(b) f_scene: scene-membership recovery via W_part[c] cosine query against "
                "current scene's cortex key; "
                "(c) f_subject: subject-role tally recovered via role-tag cosine over W_part[c] "
                "stored writes; "
                "(d) f_focus: substrate-recovered scene-focus pointer (NOT direct dict lookup of "
                "narr.scene_focus); "
                "(e) f_parallelism: substrate-state comparison, not direct dict lookup."
            ),
            "capability_closure_status": {
                "rule_applied": "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
                "capability": "narrative_Q2_coreference_resolution",
                "drills_needed_for_closure": 2,
                "drill_1_landed": "HRR_recency_sequence_composition_HF_2026-06-28",
                "drill_1_mechanism_class": "HRR_role_bind_plus_sequence_binding_K20_plus_PC_cleanup_composition",
                "drill_2_landed": "INVALID_MECHANISM_oracle_leak_does_not_count",
                "drill_2_was_claimed_as": "Lappin_Leass_symbolic_weighted_salience_over_substrate_features",
                "drill_2_actually_was": "noised_oracle_lookup_over_narrative_ground_truth_dicts",
                "drill_2_valid_landings_count": 0,
                "do_not_close_until_VALID_drill_2": True,
                "recommended_VALID_drill_2_classes": [
                    "Lappin_Leass_with_features_extracted_from_W_part_cosine_queries",
                    "position_tagged_Hopfield_style_attractor_over_substrate_state",
                    "learned_linear_coreference_projector_trained_on_substrate_state_parallel_to_Barrier1_drill2_design",
                    "transformer_style_attention_over_substrate_recovered_mention_log_with_substrate_value_lookup",
                ],
            },
            "cert_increment_delta": 0,
            "discipline_tags": [
                "META_RULE_AC", "META_RULE_AE", "META_RULE_AF",
                "META_RULE_AP_v3_witness_substrate_primitive_must_actually_consult_substrate",
                "META_RULE_H_CARDINALITY_OK",
                "BIAS_Q_suspect_1p000_at_arm_class",
                "BIAS_13_by_construction_saturation_arm_pinned",
                "BIAS_N_verify_the_referent",
                "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
                "main_thread_authored_audit_suspect_skunkworks_caught_at_landed_VET",
                "ORACLE_LEAK_INVALID_MECHANISM_class_witness_2026-06-28",
            ],
            "ts_iso_atomized": ATOMIZED_DATE,
        },
    }


atom_seed_7 = make_per_seed_invalid_atom(
    seed=7, reported_verdict="HARD_PASS",
    lappin_q2=0.875, naive_q2=0.625, rec_q2=0.625, sf_q2=1.000, oracle_q2=1.000,
    lift_over_naive=0.250, metrics_path=METRICS_PATHS["seed_7"],
)

atom_seed_13 = make_per_seed_invalid_atom(
    seed=13, reported_verdict="HARD_PASS",
    lappin_q2=0.875, naive_q2=0.125, rec_q2=0.750, sf_q2=1.000, oracle_q2=1.000,
    lift_over_naive=0.750, metrics_path=METRICS_PATHS["seed_13"],
)

atom_seed_19 = make_per_seed_invalid_atom(
    seed=19, reported_verdict="MIDDLE_BAND",
    lappin_q2=0.750, naive_q2=0.125, rec_q2=0.750, sf_q2=1.000, oracle_q2=1.000,
    lift_over_naive=0.625, metrics_path=METRICS_PATHS["seed_19"],
)


# ============================================================
# ATOM 4: cross-seed aggregation (capability-closure status update)
# ============================================================
agg_atom = {
    "id": (
        "T3/EXP_narrative_q2_coref_lappin_leass_drill2_CROSS_SEED_AGGREGATION_"
        "ORACLE_LEAK_INVALID_capability_closure_NOT_SATISFIED_2026-06-28"
    ),
    "name": (
        "narrative Q2 coref Lappin-Leass drill 2 CROSS-SEED aggregation (n=3: "
        "seeds 7+13+19) -- 2-of-3 reported HARD_PASS + 1 MIDDLE_BAND, but ALL "
        "INVALID due to oracle-leak via narrative-dict direct reads; mechanism "
        "is noised oracle lookup not substrate-feature symbolic scorer; drill 2 "
        "does NOT count toward 2x-drill capability closure; Q2 capability remains "
        "OPEN with 1 of 2 VALID mechanism-class drills landed"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Cross-seed aggregation atom for substrate_narrative_q2_coref_lappin_leass_drill2_v1 "
        "across 3 chunked sibling seeds (7, 13, 19). All 3 cells reported numerically-"
        "valid per_arm results (cardinality_ok=6/6 each; oracle sanity=1.000 each; "
        "arms_distinct=5/6 each with SF==ORACLE collision). The cell-author's verdict "
        "classifier reported 2 HARD_PASS (seeds 7, 13) and 1 MIDDLE_BAND (seed 19). "
        ""
        "SKUNKWORKS LANDED-VET OVERRIDES TO HARD_FAIL_ORACLE_LEAK_INVALID across all 3 "
        "seeds. Reason: the cell-author-claimed mechanism class 5a (Lappin-Leass symbolic "
        "weighted-salience scorer over substrate-extracted features) was not implemented "
        "as claimed. The 5 features are extracted from narrative ground-truth dicts "
        "(narr.events + narr.scene_focus) NOT from substrate state (W_part / cortex "
        "readout). f_focus reads narr.scene_focus[scene_id], which equals the Q2 ground-"
        "truth answer for all pronoun events per narrative-gen line 396 (ev['char_id'] = "
        "scene_focus[scene_id]). ARM_SCENE_FOCUS_ONLY q2_pred_sha == ARM_ORACLE q2_pred_sha "
        "across all 3 seeds (seed_7: 0bf34a6401829c1a; seed_13: 6ddde45e2077e802; "
        "seed_19: c889b430f8a34a7f). Feature-ablation independent recompute: only_focus "
        "(W_FOCUS * f_focus, other 4 zeroed) = 1.000 across all 3 seeds = perfect oracle; "
        "no_focus (other 4 features, f_focus zeroed) = 0.500 / 0.500 / 0.250 = WORSE than "
        "random floor; full Lappin-Leass = 0.875 / 0.875 / 0.750 = BELOW only_focus because "
        "the other 4 substrate-claimed features inject noise that degrades the oracle. "
        ""
        "Cross-seed cv on Lappin-Leass arm = 0.0589/0.8333 = 0.0707 (low); however cv is "
        "MEANINGLESS for an oracle-leak mechanism since the variance comes from the noise "
        "that the other 4 features inject relative to the perfect f_focus oracle, not from "
        "any substrate signal recovery. "
        ""
        "CAPABILITY CLOSURE STATUS: USER 2x-drill-before-capability-closure rule requires "
        "2 GENUINELY DIFFERENT mechanism-class drills both confirming null before Q2 "
        "capability box can be closed. Drill 1 (HRR recency-sequence composition; atom "
        "T3/EXP_narrative_q2_coref_hrr_recency_sequence_HARD_FAIL_regime_extension_failed_"
        "drill_1_of_2_2026-06-28) confirmed null. Drill 2 (this) was an INVALID mechanism "
        "implementation -- it did not test what the pre-reg claimed it tested. Drill 2 "
        "does NOT count toward the 2x-drill closure rule. Q2 capability remains OPEN with "
        "1 of 2 VALID drills landed. Recommended VALID drill 2 classes: (a) Lappin-Leass "
        "with features actually extracted from W_part cosine queries; (b) position-tagged "
        "Hopfield-style attractor over substrate state; (c) learned linear coreference "
        "projector trained on substrate state (parallel to Barrier 1 drill 2 design)."
    ),
    "aliases": [
        "narrative_q2_coref_lappin_leass_drill2_CROSS_SEED_INVALID_MECHANISM_2026-06-28",
        "Q2_capability_closure_NOT_SATISFIED_by_drill_2_2026-06-28",
        "drill_2_oracle_leak_does_not_count_toward_2x_drill_rule_2026-06-28",
        "skunkworks_landed_VET_overrides_main_thread_authored_HARD_PASS_to_HARD_FAIL_2026-06-28",
        "narrative_q2_capability_remains_OPEN_drill_2_must_be_re_run_in_valid_mechanism_class_2026-06-28",
        "feature_ablation_evidence_only_focus_equals_oracle_other_4_features_carry_no_information_2026-06-28",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "hard_fail",
        "cert_class": "mechanism_characterization",
        "verdict": "HARD_FAIL_ORACLE_LEAK_INVALIDATES_ALL_3_SEED_RESULTS_DRILL_2_DOES_NOT_SATISFY_CAPABILITY_CLOSURE",
        "n_seeds_aggregated": 3,
        "seeds_aggregated": [7, 13, 19],
        "reported_verdicts_per_seed": {
            "seed_7": "HARD_PASS",
            "seed_13": "HARD_PASS",
            "seed_19": "MIDDLE_BAND",
        },
        "skunkworks_override_verdicts_per_seed": {
            "seed_7": "HARD_FAIL_ORACLE_LEAK_INVALID",
            "seed_13": "HARD_FAIL_ORACLE_LEAK_INVALID",
            "seed_19": "HARD_FAIL_ORACLE_LEAK_INVALID",
        },
        "cell_commit": CELL_COMMIT,
        "cell_paths": [
            "experiments/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_7.py",
            "experiments/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_13.py",
            "experiments/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_19.py",
        ],
        "impl_path": IMPL_PATH,
        "prereg_path": PREREG_PATH,
        "metrics_paths": list(METRICS_PATHS.values()),
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": VERIFIED_OFF_DATA,
        "main_thread_authored": True,
        "cross_seed_lappin_leass_Q2_stats": {
            "mean": 0.8333, "sd": 0.0589, "cv": 0.0707,
            "vals": [0.875, 0.875, 0.750],
        },
        "cross_seed_scene_focus_Q2_stats": {
            "mean": 1.0000, "sd": 0.0000, "cv": 0.0000,
            "vals": [1.000, 1.000, 1.000],
            "note": "ARM_SCENE_FOCUS_ONLY is ORACLE-CLASS by corpus construction; pinned 1.000",
        },
        "cross_seed_oracle_Q2_stats": {
            "mean": 1.0000, "sd": 0.0000, "cv": 0.0000,
            "vals": [1.000, 1.000, 1.000],
        },
        "cross_seed_naive_magnitude_Q2_stats": {
            "mean": 0.2917, "sd": 0.2357, "cv": 0.8081,
            "vals": [0.625, 0.125, 0.125],
            "note": "substrate-noisy partition magnitude vote; high cv consistent with crosstalk-dominated noise floor across seeds",
        },
        "feature_ablation_summary": {
            "only_focus_W_focus_times_f_focus_other_4_zeroed_perfect_1p000_across_all_3_seeds": True,
            "no_focus_4_features_rec_scene_subj_par_f_focus_zeroed_below_random_floor_seed_7_0p500_seed_13_0p500_seed_19_0p250": True,
            "full_lappin_leass_below_only_focus_across_all_3_seeds_other_4_features_degrade_oracle": True,
        },
        "capability_closure_status": {
            "rule_applied": "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
            "capability": "narrative_Q2_coreference_resolution",
            "drills_needed_for_closure": 2,
            "valid_drills_landed": 1,
            "valid_drill_1": "HRR_recency_sequence_composition_HF_atom_T3_EXP_narrative_q2_coref_hrr_recency_sequence_HARD_FAIL_regime_extension_failed_drill_1_of_2_2026-06-28",
            "drill_2_INVALID": "this_atom_oracle_leak_does_not_count",
            "valid_drill_2_needed": True,
            "Q2_capability_status": "OPEN_drill_2_must_be_re_run_in_valid_substrate_consulting_mechanism_class",
            "recommended_VALID_drill_2_classes": [
                "Lappin_Leass_with_features_extracted_from_W_part_cosine_queries_not_narr_events_dict",
                "position_tagged_Hopfield_style_attractor_over_substrate_state",
                "learned_linear_coreference_projector_trained_on_substrate_state_parallel_to_Barrier1_drill2_design",
                "transformer_style_attention_over_substrate_recovered_mention_log",
            ],
        },
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AP_v3_witness_substrate_primitive_must_actually_consult_substrate",
            "BIAS_Q_suspect_1p000",
            "BIAS_13_by_construction_saturation",
            "BIAS_N_verify_the_referent",
            "META_RULE_AF_arms_must_differ_pred_sha_should_NOT_exempt_oracle_class_collision",
            "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
            "main_thread_authored_audit_suspect_skunkworks_caught",
            "feature_ablation_independent_recompute_load_bearing_evidence",
            "skunkworks_landed_VET_overrides_cell_author_verdict_2026-06-28",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# CERT_LEDGER ROWS (4: one per per-seed atom + 1 aggregation atom)
# ============================================================
def make_ledger_row(atom_id: str, atom_name_summary: str, seed: int = None) -> dict:
    return {
        "ts": time.time(),
        "op": "cert_ruling",
        "atom_id": "math::" + atom_id,
        "cert_status": "hard_fail",
        "cert_class": "mechanism_characterization",
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "cell_commit": CELL_COMMIT,
        "verdict": atom_name_summary,
        "cert_increment_delta": 0,
        "cv": None,
        "referent_pointer": {
            "metrics_path": METRICS_PATHS["seed_%d" % seed] if seed is not None else list(METRICS_PATHS.values()),
            "prereg_path": PREREG_PATH,
            "cell_path": "experiments/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_%d.py" % seed if seed else None,
            "impl_path": IMPL_PATH,
            "atom_qualified_id": "math::" + atom_id,
        },
        "supersedes": None,
        "note": (
            "narrative_q2_coref_lappin_leass_drill2_ORACLE_LEAK_INVALID_skunkworks_landed_VET_"
            "overrides_main_thread_authored_HARD_PASS_to_HARD_FAIL_mechanism_was_noised_oracle_"
            "not_substrate_feature_symbolic_scorer_Q2_capability_remains_OPEN_drill_2_must_be_"
            "re_run_in_valid_substrate_consulting_mechanism_class_2026-06-28"
        ),
    }


hf_ledger_seed_7 = make_ledger_row(
    atom_seed_7["id"],
    "HARD_FAIL_ORACLE_LEAK_seed_7_reported_HARD_PASS_invalidated_mechanism_is_noised_oracle_lookup",
    seed=7,
)
hf_ledger_seed_13 = make_ledger_row(
    atom_seed_13["id"],
    "HARD_FAIL_ORACLE_LEAK_seed_13_reported_HARD_PASS_invalidated_mechanism_is_noised_oracle_lookup",
    seed=13,
)
hf_ledger_seed_19 = make_ledger_row(
    atom_seed_19["id"],
    "HARD_FAIL_ORACLE_LEAK_seed_19_reported_MIDDLE_BAND_invalidated_mechanism_is_noised_oracle_lookup",
    seed=19,
)
hf_ledger_agg = make_ledger_row(
    agg_atom["id"],
    "HARD_FAIL_ORACLE_LEAK_cross_seed_n3_INVALID_MECHANISM_drill_2_does_not_satisfy_2x_drill_capability_closure_Q2_remains_OPEN",
    seed=None,
)


# ============================================================
# A5 WRITE PROTOCOL
# ============================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    """Atomic append with verify-load + integrity-check."""
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"target does not exist: {path}"

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
    print(f"[A5] writing 4 math atoms (3 per-seed INVALID + 1 cross-seed agg)")
    print(f"[A5] writing 4 cert_ledger rows (all HARD_FAIL mechanism_characterization)")

    append_jsonl_a5(MATH_ATOMS, atom_seed_7, "math/atoms.jsonl [seed_7 INVALID]")
    append_jsonl_a5(MATH_ATOMS, atom_seed_13, "math/atoms.jsonl [seed_13 INVALID]")
    append_jsonl_a5(MATH_ATOMS, atom_seed_19, "math/atoms.jsonl [seed_19 INVALID]")
    append_jsonl_a5(MATH_ATOMS, agg_atom, "math/atoms.jsonl [cross-seed agg INVALID]")

    append_jsonl_a5(CERT_LEDGER, hf_ledger_seed_7, "meta/cert_ledger.jsonl [seed_7]")
    append_jsonl_a5(CERT_LEDGER, hf_ledger_seed_13, "meta/cert_ledger.jsonl [seed_13]")
    append_jsonl_a5(CERT_LEDGER, hf_ledger_seed_19, "meta/cert_ledger.jsonl [seed_19]")
    append_jsonl_a5(CERT_LEDGER, hf_ledger_agg, "meta/cert_ledger.jsonl [cross-seed]")

    print(f"[A5] DONE OK; CERT delta = 0 (HF mechanism_characterization x 4)")
    print(f"[A5] Q2 capability-closure status: 1 of 2 VALID drills landed; capability remains OPEN")
    print(f"[A5] Drill 2 must be re-run in a VALID substrate-consulting mechanism class")
    print(f"[A5] Skunkworks OVERRIDE: cell-author reported 2 HARD_PASS + 1 MIDDLE_BAND;")
    print(f"[A5]   all 3 invalidated by oracle-leak via narrative-dict direct reads")


if __name__ == "__main__":
    main()
