"""
A5-gated atomization: exp_reader_clauseseg_topical_animate_subject_v2 (LOCAL commit 2b85d7b0e) -> ONE atom (2026-07-18).
  MEASURED_MECHANISM / proven-bound REFINEMENT of the clause-seg chain. The topical-ANIMATE held subject
  (Centering backward-looking-center, animate-filtered via overlay _topical_ranked) KEEPS the full ceiling
  recovery AND fixes the held-subject SOURCE brain-faithfully (v1 inanimate 'time' -> animate 'george';
  inanimate_overfire 1->0) BUT precision is STILL below the do-nothing floor (0.4762 < 0.5143).
  LOAD-BEARING NEW FACT: the residual precision FP is SUBJECT-INDEPENDENT -- it is non-factive/mental-state
  VERB coordination over-firing (wished/thought), NOT the held subject. This CORRECTS the prior VET's own
  recompute (cert_ledger 2026-07-18T20:00:31, on v1 commit 775c6085c) which predicted topical-animate reaches
  ~floor (0.5128 AT floor); the empirical build shows 0.4762 BELOW floor. AMENDS (does NOT supersede) the v1
  parent atom: v1's recovery finding stands; only its 'animate fix reaches floor' recompute is corrected.
LOCAL ONLY: store_head_at_write=unsynced_needs_orchestrator; NO origin push; NO remote persist.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"
ATOMIZED_BY = "skunkworks_landed_vet_reader_clauseseg_topical_animate_subject_v2_MM_precision_gap_subject_independent_nonfactive_verb_2026-07-18"
ATOMIZED_DATE = "2026-07-18"
ANCHOR = "reader_clauseseg_topical_animate_subject_v2"
CELL_COMMIT = "2b85d7b0e"

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

PARENT_V1_ATOM_ID = (
    "math::MM_reader_learned_clauseseg_shared_subject_v1_LEARNED_OVERLAY_REUSE_CLAUSE_SEG_RECOVERS_ORACLE_"
    "BOUNDED_COMPOSITION_RECALL_PRIZE_but_NOT_PRECISION_NEUTRAL_commit_775c6085c_composes_oracle_parser_"
    "b85422616_cheapfix_077cfaa39_envelope_00c6688b6_MECHANISM_track_ACTIVE_SUBJECT_resolved_agent_head_of_"
    "last_explicit_subject_clause_on_COORD_preceded_bare_VP_prepend_held_subject_as_AGENT_sourced_from_working_"
    "memory_overlay_NOT_oracle_INJECT_SUBJ_boundaries_BYTE_IDENTICAL_to_handrule_splitter_ONE_variable_is_the_"
    "propagation_FIRST_NON_ORACLE_clause_seg_component_ALL_metrics_reproduce_BYTE_IDENTICAL_off_disk_full_rerun_"
    "only_ts_elapsed_differ_self_test_PASS_anti_copy_divergence_11of11_positive_control_envelope_floor_"
    "reproduces_envelope_3rd_store_EXACT_n_rel_36_CMP_0p333_ref_0p833_RELF1r_0p800_N5_missing_gold_ceiling_"
    "recovers_N5_determinism_confirmed_RECOVERY_REAL_learned_matches_ORACLE_on_BOTH_gold_shared_subject_sites_"
    "geo3_put_strawberry_george_and_wolf2_killed_sheep_wolf_ZERO_under_detect_ZERO_wrong_subject_vs_oracle_"
    "recovers_N5_relation_svo_killed_wolf_sheep_True_answer_False_same_as_gold_ceiling_orthogonal_great_many_"
    "answer_engine_artifact_reaches_gold_CEILING_100pct_of_gap_CMP_0p333_to_0p667_ceiling_0p667_RELF1_recall_"
    "0p800_to_0p933_ceiling_0p933_NO_control_regression_passive_1p00_reversal_1p00_ref_acc_0p8333_IDENTICAL_all_"
    "arms_overlay_witness_PASS_PROVEN_BOUND_PRECISION_unlike_oracle_which_is_precision_NEUTRAL_plus0p0015_above_"
    "floor_the_LEARNED_heuristic_REGRESSES_strict_precision_BELOW_orphan_floor_0p4651_learned_vs_0p5143_floor_vs_"
    "0p5263_gold_net_negative_on_foundation_precision_vs_doing_nothing_5_excess_FP_vs_oracle_localized_to_TWO_"
    "over_firings_ONE_genuine_error_inanimate_stale_held_subject_time_on_geo2_wished_for_a_cool_place_adds_4_FP_"
    "wished_time_cool_dinner_george_place_ONE_correct_subject_arg_structure_artifact_susie_on_susie2_thought_she_"
    "would_eat_her_lunch_subject_CORRECT_animate_topical_but_downstream_thought_lunch_patient_misparse_adds_1_FP_"
    "thought_susie_lunch_NOT_a_subject_prop_error_FIX_topical_ANIMATE_held_subject_via_topical_ranked_suppresses_"
    "inanimate_time_recompute_confirms_removes_exactly_4_time_FP_yields_20_of_39_equals_0p5128_which_lands_AT_"
    "floor_0p5143_NOT_above_residual_susie_FP_is_the_deferred_argument_structure_workstream_and_the_gold_0p5263_"
    "advantage_over_animate_fix_comes_from_oracle_EXACT_site_selection_not_firing_on_susie2_at_all_brain_check_"
    "Centering_Theory_brain_holds_animate_topical_protagonist_across_and_plus_prosody_text_lacks_so_text_only_"
    "over_propagation_is_brain_EXPECTED_fix_is_the_brains_mechanism_coordination_detection_is_NOT_broadly_broken_"
    "zero_under_detect_zero_wrong_subject_the_issue_is_which_held_subject_animate_filter_SCOPE_single_annotator_"
    "gold_n_rel_36_to_43_n_q_15_in_vocab_grade3_narrative_slice_modestly_powered_composition_recovery_rests_on_"
    "single_question_M3_george_out_of_vocab_poetry_long_sentences_UNTESTED_verified_off_data_2026-07-18"
)

XARC = (
    "substrate_query.sh 'non-factive verb coordination clause segmentation held subject propagation precision' "
    "-> top hits are GENERIC char-trigram lexical matches on the token 'propagation': 'propagation' cosine=0.4414 "
    "(concept/wordnet corpus), 'action potential propagation' 0.4189 (gene_ontology), 'CN_propagation' 0.4111, "
    "'nation'/'ration' 0.4033 (surface-form collisions). NONE is a prior reader/parser EXPERIMENT-ARC atom -- the "
    ">0.30 hits are foundation concept/wordnet atoms colliding on the substring 'propagation', not a prior "
    "clause-seg run. This is a TARGETED EXTENSION of the clause-seg chain (v1 775c6085c -> this v2), genuinely "
    "novel as a mechanism localization (non-factive verb / factivity filter). Not a rediscovery."
)

ATOM_ID = (
    "math::MM_reader_clauseseg_topical_animate_subject_v2_TOPICAL_ANIMATE_HELD_SUBJECT_KEEPS_full_ceiling_"
    "recovery_AND_fixes_held_subject_SOURCE_brainfaithfully_v1_inanimate_time_to_animate_george_inanimate_"
    "overfire_1_to_0_correct_Centering_backward_looking_center_via_overlay_topical_ranked_BUT_precision_STILL_"
    "below_floor_0p4762_vs_floor_0p5143_regress_below_floor_TRUE_LOAD_BEARING_the_residual_precision_FP_is_"
    "SUBJECT_INDEPENDENT_non_factive_mental_state_VERB_coordination_wished_thought_NOT_the_held_subject_CORRECTS_"
    "prior_VET_ledger_2026_07_18T20_00_31_on_v1_775c6085c_which_recomputed_topical_animate_removes_4_time_FP_"
    "yields_20of39_0p5128_AT_floor_WRONG_the_animate_filter_SWAPS_subject_time_to_george_NOT_suppresses_geo2_"
    "injection_george_still_fires_svo_wished_george_cool_dinner_place_because_wished_is_NONFACTIVE_only_1_FP_"
    "drops_the_self_loop_wished_george_george_so_20of42_0p4762_BELOW_floor_verified_off_disk_all_4_excess_FP_vs_"
    "gold_are_nonfactive_verb_wished_x3_george_plus_thought_susie_lunch_both_CORRECT_animate_subjects_gold_"
    "achieves_above_floor_0p5263_precisely_by_NOT_injecting_on_geo2_wished_or_susie2_thought_at_all_only_on_"
    "factive_transitive_geo3_put_and_wolf2_killed_so_gold_exact_site_selection_IS_effectively_a_factivity_filter_"
    "NEXT_LEVER_verb_class_factivity_filter_suppress_svo_on_nonfactive_mental_state_verbs_would_reach_gold_"
    "CEILING_not_merely_floor_UNIFIES_prior_two_residuals_susie_arg_structure_plus_oracle_exact_site_into_ONE_"
    "lever_recovery_KEPT_N5_True_CMP_0p667_ceiling_RELF1_recall_0p933_ceiling_no_regression_passive_1p00_"
    "reversal_1p00_coref_ref_acc_0p8333_identical_overlay_witness_PASS_self_test_PASS_anti_copy_divergence_11of11_"
    "positive_control_envelope_floor_reproduces_n_rel_36_CMP_0p333_ref_0p833_RELF1r_0p800_N5_missing_gold_"
    "recovers_N5_determinism_confirmed_can_fail_landed_PARTIAL_not_CLEAN_AMENDS_not_supersedes_v1_775c6085c_"
    "brain_check_nonfactive_irrealis_verbs_do_not_assert_a_real_event_Centering_handles_subject_factivity_handles_"
    "event_suppressing_nonfactive_coordinated_verbs_is_brain_faithful_SCOPE_single_annotator_gold_n_rel_35_to_42_"
    "n_q_15_in_vocab_grade3_narrative_slice_modestly_powered_commit_2b85d7b0e_verified_off_data_2026-07-18"
)

ATOM_CLAIM = (
    "MATH MEASURED_MECHANISM (proven-bound REFINEMENT of the clause-seg chain; the cell landed PARTIAL_PRECISION_"
    "STUCK, confirmed). The Centering-Theory TOPICAL-ANIMATE held subject (overlay _topical_ranked over grounded-"
    "animate entities, prepended as AGENT at a COORD-boundary bare-VP conjunct; ONE variable vs v1 = held-subject "
    "SOURCE, boundaries byte-identical) does TWO real things and reveals ONE proven bound: "
    "(1) KEEPS the full ceiling recovery -- N5 relation svo(killed,wolf,sheep)=True, CMP 0.333(floor)->0.667"
    "(=gold ceiling), RELF1-recall 0.800(floor)->0.933(=gold ceiling); no recovery lost by the subject change. "
    "(2) FIXES the held-subject SOURCE brain-faithfully -- v1's stale INANIMATE 'time' is replaced by the animate "
    "protagonist 'george' on geo2 (inanimate_overfire 1->0), correct Centering backward-looking-center. "
    "(3) BUT precision is STILL below the do-nothing floor: strict precision 0.4762 (20/42) < orphan floor 0.5143 "
    "(18/35); regress_below_floor stays True (v1 last-active was 0.4651; the animate fix moved precision only "
    "+0.0111). "
    "LOAD-BEARING NEW FACT (the whole point of this cell, verified off-disk): the residual precision FP is "
    "SUBJECT-INDEPENDENT. Even the CORRECT animate subject 'george' yields FPs svo(wished,george,cool/dinner/"
    "place) because 'wished' is a NON-FACTIVE verb -- george did not act on 'place'; 'wished for a cool place' "
    "asserts no real george-place event. The residual is NON-FACTIVE / MENTAL-STATE VERB coordination over-"
    "firing (wished, thought), NOT the held subject. All 4 excess FPs vs the gold oracle are exactly these: "
    "svo(wished,george,{cool,dinner,place}) + svo(thought,susie,lunch) -- both with CORRECT animate subjects. "
    "THIS CORRECTS THE PRIOR VET's OWN RECOMPUTE: the v1 landed-VET (cert_ledger 2026-07-18T20:00:31, on v1 "
    "775c6085c) predicted topical-animate 'removes exactly 4 time FP -> 20/39 = 0.5128, lands AT the floor'. That "
    "was WRONG -- the animate filter does not SUPPRESS the geo2 injection, it SWAPS the subject time->george; "
    "george still fires the non-factive FPs, and only ONE FP drops (the self-loop svo(wished,george,george) "
    "removed by the self-loop guard). Actual: 20/42 = 0.4762, still BELOW floor. The empirical build caught the "
    "VET's recompute error. "
    "NEXT LEVER (endorsed): a VERB-CLASS / FACTIVITY filter -- suppress svo extraction on non-factive / mental-"
    "state verbs (wished, thought), restricting propagation to factive transitive verbs. This is exactly what the "
    "gold oracle's site selection already does implicitly: gold injects ONLY on the factive-transitive sites geo3 "
    "(put strawberry) + wolf2 (killed sheep) and never on geo2 (wished) or susie2 (thought), which is why gold "
    "reaches 0.5263 ABOVE floor. So the factivity filter would reach the gold CEILING, not merely the floor, and "
    "it UNIFIES the prior VET's two separate residuals (susie 'arg-structure artifact' + 'oracle exact-site "
    "advantage') into ONE mechanism. Cheap and bounded (a verb-class list on the injection gate)."
)

ATOM_RECOMPUTE = (
    "INDEP recompute (.venv Scripts/python, NOT verdict_msg; Fix #28): "
    "(A) self-test PASSES: boundary seg byte-aligns with ORC.split_sentences (8 COORD boundaries); anti-copy-"
    "divergence extract(orphan|gold)==CFX.extract_passage_fixed 11/11 passages x2 modes; POS-CTRL envelope_floor "
    "reproduces envelope 3rd store EXACT (n_rel=36 CMP=0.333 ref=0.833 RELF1r=0.800, N5 missing); gold ceiling + "
    "v1 last-active both recover N5; determinism confirmed (run_arm twice, strict/correct/injections identical); "
    "controls passive 1.00 reversal 1.00, ref_acc 0.833 identical across arms; overlay witness PASS. "
    "(B) strict-precision re-derived from tp/fp arrays: floor 18/35=0.5143; v1_lastactive 20/43=0.4651; topical "
    "20/42=0.4762; gold 20/38=0.5263 -- all match report EXACT; fp_relations array lengths equal reported fp for "
    "all arms. "
    "(C) SUBJECT-INDEPENDENCE verified by relation inspection: v1_lastactive wished FPs = svo(wished,time,"
    "{cool,dinner,george,place}) (4); topical wished FPs = svo(wished,george,{cool,dinner,place}) (3 -- the 4th, "
    "svo(wished,george,george), is a self-loop removed by the guard). susie2 thought FP = svo(thought,susie,"
    "lunch) IDENTICAL in v1 and topical (susie was already the correct animate subject in v1). killed FP "
    "svo(killed,wolf,great) is present in ALL THREE of v1/topical/GOLD -> it is NOT the mechanism's fault "
    "(argument-structure / NP-head 'great many sheep', a different workstream). "
    "(D) EXCESS vs gold: topical FPs NOT in gold = {svo(wished,george,cool), svo(wished,george,dinner), "
    "svo(wished,george,place), svo(thought,susie,lunch)} = 4 (matches over_prop_fp_delta=4); gold FPs not in "
    "topical = 0. All 4 excess FPs are non-factive-verb over-injections with correct animate subjects. "
    "(E) INJECTION-SITE audit: topical injects on 4 sites [geo2 wished->george, geo3 put->george, wolf2 killed->"
    "wolf, susie2 thought->susie]; GOLD injects on ONLY 2 [geo3 put->george, wolf2 killed->wolf]. The 2 topical-"
    "only sites (geo2 wished, susie2 thought) are exactly the non-factive/mental-state verbs -> the gold oracle's "
    "site selection IS effectively a factivity filter. "
    "(F) PRIOR-VET-ERROR reproduction: prior VET modeled 'remove time -> drop 4 FP + suppress injection -> ext "
    "43->39, 20/39=0.5128'. Actual mechanism swaps subject (not suppress): ext 43->42, fp 23->22, tp 20 -> "
    "20/42=0.4762. The delta is the modeling error (suppress vs swap on a non-factive verb)."
)

ATOM_SCOPE = (
    "SAME mostly-in-vocab grade-3 McGuffey narrative slice as the parent chain (n_questions=15, n_relations 35->42, "
    "single-annotator COMPLETE_TRUTH reused verbatim from the oracle cell ORA) -- modestly powered; a correctly-"
    "propagated-but-unannotated relation would score as an FP (annotation incompleteness), but the 4 residual FPs "
    "here are GENUINE non-factive over-firings (verified against the passages: george did not act on place; susie "
    "did not act on lunch via 'thought'), NOT annotation undercount. Glass-box symbolic (POS + averaged perceptron "
    "+ overlay animacy grounding; NO LLM, NO HD primitive -- relations are Python tuples). BOUNDS: (a) 'precision-"
    "NEUTRAL' was NOT achieved -- the cell landed PARTIAL_PRECISION_STUCK, precision stays below floor; (b) the "
    "subject-source fix IS real (inanimate_overfire 1->0) but does not by itself buy precision; (c) the next lever "
    "(factivity filter) is HYPOTHESIZED from the excess-FP decomposition + the gold site-selection pattern, NOT "
    "yet built or measured -- its 'reaches gold ceiling' projection is an unVETted forward claim pending its own "
    "can-fail cell; (d) the whole clause-seg component lives INSIDE the hand-rule extraction wall (read_grow_reread "
    "HF 0.44 on real prose); this is grade-3 hand-matched narrative. BRAIN-CHECK (sound): non-factive / irrealis "
    "verbs (wished, thought) do not assert a real event; the brain does NOT extract 'george did X to place' from "
    "'wished for a place'. Centering handles the SUBJECT (which the animate filter got right), factivity handles "
    "whether the coordinated VP is a real event at all. So suppressing svo extraction on non-factive coordinated "
    "verbs is brain-faithful, and the residual over-propagation on a text that lacks prosody/factivity cues is "
    "brain-EXPECTED -- the fix is the brain's own factivity mechanism, not a patch."
)

ATOM_METRICS = {
    "strict_prec_orphan_floor": 0.5143, "strict_prec_v1_lastactive": 0.4651,
    "strict_prec_topical": 0.4762, "strict_prec_gold_ceiling": 0.5263,
    "prec_delta_topical_vs_v1": 0.0111, "regress_below_floor": True,
    "topical_tp_fp_ext": "20/22/42", "floor_tp_fp_ext": "18/17/35", "gold_tp_fp_ext": "20/18/38",
    "n5_relation_topical": True, "cmp_topical": 0.6667, "cmp_gold_ceiling": 0.6667,
    "relf1_recall_topical": 0.933, "relf1_recall_gold_ceiling": 0.933,
    "cmp_recovered_frac": 1.0, "recall_recovered_frac": 1.0,
    "inanimate_overfire_topical": 0, "inanimate_overfire_v1": 1,
    "subject_change_geo2": "time(inanimate)->george(animate)",
    "excess_fp_vs_gold": ["svo(wished,george,cool)", "svo(wished,george,dinner)", "svo(wished,george,place)",
                          "svo(thought,susie,lunch)"],
    "excess_fp_class": "non_factive_mental_state_verb_coordination_wished_thought_ALL_correct_animate_subject",
    "topical_injection_sites": ["geo2_wished->george", "geo3_put->george", "wolf2_killed->wolf",
                                "susie2_thought->susie"],
    "gold_injection_sites": ["geo3_put->george", "wolf2_killed->wolf"],
    "gold_site_selection_is_effectively_factivity_filter": True,
    "killed_wolf_great_FP_present_in_ALL_arms_incl_gold": "argument_structure_NP_head_not_mechanism_error",
    "prior_vet_recompute_corrected": "predicted 20/39=0.5128 AT floor; actual 20/42=0.4762 BELOW floor (suppress-vs-swap modeling error on non-factive verb)",
    "controls": {"passive": 1.00, "reversal": 1.00, "ref_acc_all_arms": 0.8333, "overlay_witness": "PASS"},
    "byte_reproduce": "self_test_PASS_anti_copy_divergence_11of11_POS_CTRL_exact_determinism_confirmed_seed12345_omp1",
    "cell_verdict": "PARTIAL_PRECISION_STUCK",
    "auditor_tier": "MEASURED_MECHANISM (proven-bound refinement; PARTIAL confirmed; corrects prior VET recompute)",
    "next_lever": "verb_class_factivity_filter_suppress_svo_on_nonfactive_mental_state_verbs_projected_to_reach_gold_ceiling_cheap_bounded_own_can_fail_cell",
}

COMPOSES = [
    "AMENDS (does NOT supersede) the v1 parent " + PARENT_V1_ATOM_ID[:120] + "... (commit 775c6085c, MM). The "
    "v1 RECOVERY finding stands unchanged (composition+recall reach the gold ceiling from working-memory reuse). "
    "What this cell CORRECTS is v1's forward recompute that the topical-animate fix 'removes exactly 4 time FP -> "
    "20/39=0.5128 AT floor': the empirical build shows the animate filter SWAPS the subject (time->george) "
    "rather than suppressing the injection, so george still fires 3 non-factive svo(wished,george,*) FPs and "
    "precision lands 0.4762 BELOW floor. The v1 atom's two separate residuals (the susie 'arg-structure "
    "artifact' + the 'oracle exact-site advantage') are UNIFIED here into ONE lever: a factivity / verb-class "
    "filter (gold's exact-site selection IS effectively factivity filtering).",
    "COMPOSES with math::MM_reader_oracle_parser_upperbound_v1 (commit b85422616, MM): that oracle diagnostic "
    "bounded the gold clause-seg as precision-NEUTRAL (+0.0015 above floor) and flagged argument-structure + "
    "role-assigner as the newly-dominant residual. This cell refines the LEARNED realization: after fixing the "
    "held subject to animate, the dominant clause-seg-attributable residual is NON-FACTIVE VERB propagation "
    "(distinct from the general argument-structure workstream), and the gold's above-floor precision is because "
    "it never injects on the two non-factive sites.",
    "USES the packaged hdlab.state_of_mind.WorkingOverlay _topical_ranked (Centering backward-looking-center) "
    "validated in the 2026-07-17 state-of-mind arc + longdist reference MM (49bb99c24). The animate-topical held "
    "subject is a within-regime application of that overlay's salience ranking; its correctness (inanimate_"
    "overfire 1->0) is a real confirmation the overlay exposes the right protagonist.",
    "credit: McGuffey Third Reader (public-domain grade-3 corpus); Centering Theory (Grosz/Joshi/Weinstein) for "
    "the backward-looking-center held subject; factivity/non-factive-verb linguistics (Kiparsky) for the next-"
    "lever localization. Cell + gold + COMPLETE_TRUTH original to the reader arc (hand-authored, honestly "
    "flagged single-annotator).",
]

OVER_READS = [
    "The cell's PARTIAL_PRECISION_STUCK verdict_msg hedges the residual as 'another inanimate/stale hold, OR the "
    "residual susie-class downstream complement mis-parse dominates'. Auditor SHARPENS (both disjuncts are "
    "imprecise): inanimate_overfire is 0 (no inanimate hold remains), and it is not only the susie case -- the "
    "geo2 'wished' residual is ALSO a non-factive verb FP with a CORRECT animate subject. Both geo2 (wished) and "
    "susie2 (thought) are the SAME class: non-factive/mental-state verb over-injection. The precise localization "
    "is SUBJECT-INDEPENDENT non-factive-verb coordination, unifying both sites.",
    "Any read that the topical-animate held subject 'restores precision to the floor' (the prior VET's projection "
    "and the cell's own CLAUSE_SEG_CLEAN branch hypothesis) is REFUTED off-disk: precision is 0.4762 < floor "
    "0.5143. The subject-source fix is real and brain-faithful but does NOT by itself buy precision.",
    "The 'factivity filter reaches the gold ceiling' projection is a HYPOTHESIS from the excess-FP decomposition "
    "+ gold site-selection pattern, NOT a measured result. It is well-motivated (the 4 excess FPs are exactly the "
    "2 non-factive sites gold skips) but must be built as its own can-fail cell before banking as achieved.",
]

REVIVAL = [
    "BUILD the verb-class / factivity filter as a can-fail cell: gate the COORD bare-VP injection (or the svo "
    "extraction on the injected clause) on the verb being factive-transitive, suppressing non-factive/mental-"
    "state verbs (wished, thought, hoped, believed, ...). Pre-register: it must REACH the gold ceiling (0.5263, "
    "above floor) -- not merely floor -- AND keep the N5/CMP/recall recovery, with no control regression. It "
    "CAN-FAIL if the verb-class list is too broad (loses a factive recovery) or too narrow (leaves a non-factive "
    "FP).",
    "verify the factivity lever on HELD-OUT passages / a LEARNED verb-class classifier (not a hand list matched to "
    "wished/thought), so the filter is not just curve-fit to these two sites -- the decisive test separating a "
    "genuine factivity mechanism from a 2-verb patch.",
    "expand N: the residual is 4 FPs on 2 verbs at n_relations~42, single-annotator gold; the composition "
    "recovery still rests on a single question (M3). More competitive non-factive coordination sites would "
    "harden the subject-independence claim.",
]

GENUINE_POS = (
    "GENUINE positives preserved symmetrically: (1) the topical-ANIMATE held subject KEEPS the full ceiling "
    "recovery (N5, CMP 0.667, RELF1-recall 0.933) -- the subject-source change cost nothing on the prize; (2) it "
    "FIXES the held-subject source brain-faithfully (v1 inanimate 'time' -> animate 'george', inanimate_overfire "
    "1->0), correct Centering; (3) it MEASURES a new, load-bearing fact the prior VET could not derive by "
    "recompute alone: the residual precision gap is SUBJECT-INDEPENDENT (non-factive verb), which cleanly "
    "localizes the next lever (factivity filter) AND unifies the parent's two separate residuals. The empirical "
    "build CORRECTING a prior VET's own recompute is exactly why landed-VET verifies OFF DATA, not off reports -- "
    "credited to the cell author; the auditor's own prior recompute (0.5128 at floor) was wrong (modeled suppress "
    "instead of swap on a non-factive verb), and this is an honest self-correction."
)


def build_atom():
    return {
        "id": ATOM_ID, "name": ATOM_CLAIM, "corpus": "math", "tier": "MEASURED_MECHANISM",
        "kind": "experiment_landed_vet",
        "cert_status": "proven_bound",
        "cert_class": ("reader_parser_clause_seg_topical_animate_held_subject_keeps_ceiling_recovery_and_fixes_"
                       "subject_source_brainfaithfully_but_precision_still_below_floor_residual_FP_is_SUBJECT_"
                       "INDEPENDENT_non_factive_mental_state_verb_coordination_corrects_prior_VET_recompute_next_"
                       "lever_verb_class_factivity_filter_projected_to_reach_gold_ceiling"),
        "description": (ATOM_CLAIM + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + ATOM_RECOMPUTE
                        + "\n\nHONEST SCOPE: " + ATOM_SCOPE),
        "aliases": [], "ts_iso": _iso, "ts": _ts,
        "metadata": {
            "provenance_quality": "self_test_PASS_byte_reproduce_exact_plus_independent_precision_and_relation_decomposition_off_disk",
            "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes": None,
            "amends_atom_id": PARENT_V1_ATOM_ID,
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_reader_clauseseg_topical_animate_subject_v2/metrics.json",
            "verified_off_data": ATOM_RECOMPUTE, "honest_scope": ATOM_SCOPE, "metrics": ATOM_METRICS,
            "over_reads_corrected": OVER_READS,
            "genuine_positives_symmetric_anti_negativity": GENUINE_POS,
            "revival_criteria": REVIVAL,
            "cross_arc_overlap_check": XARC,
            "corrects_prior_vet": (
                "cert_ledger 2026-07-18T20:00:31 (v1 landed-VET on commit 775c6085c) recomputed that the topical-"
                "animate fix 'removes exactly 4 time FP -> 20/39 = 0.5128, lands AT the floor 0.5143'. REFUTED "
                "off-disk: the animate filter SWAPS the geo2 subject time->george rather than suppressing the "
                "injection; george still fires 3 non-factive svo(wished,george,*) FPs, only the self-loop drops, "
                "actual precision 20/42 = 0.4762 BELOW floor. The empirical build caught the VET's recompute error "
                "(suppress-vs-swap on a non-factive verb). Honest self-correction; the v1 atom's recovery finding "
                "is unchanged."),
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "a_VET_can_be_wrong_empirical_build_caught_it_research_can_be_wrong",
                "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
                "every_negative_and_positive_brain_check_mechanism_vs_shortcut",
                "construction_proof_not_capability_win_could_it_fail_informatively",
            ],
            "composes_with": COMPOSES,
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE,
            "needs_orchestrator_store_sync": True,
            "local_write_only_no_origin_push_no_remote_persist": True,
        },
    }


def ledger_row(atom):
    return {
        "op": "cert_ruling", "corpus": "math", "tier": atom["tier"], "cert_status": atom["cert_status"],
        "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes_commit": None,
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True,
        "auditor": "hdi_skunkworks", "atomized_by": ATOMIZED_BY,
        "verdict": ("MEASURED_MECHANISM_proven_bound_refinement_PARTIAL_PRECISION_STUCK_confirmed_topical_animate_"
                    "held_subject_KEEPS_full_ceiling_recovery_N5_CMP_0p667_RELF1r_0p933_AND_fixes_subject_source_"
                    "brainfaithfully_inanimate_time_to_animate_george_inanimate_overfire_1_to_0_BUT_precision_"
                    "STILL_below_floor_0p4762_vs_0p5143_residual_FP_SUBJECT_INDEPENDENT_non_factive_verb_"
                    "coordination_wished_thought_CORRECTS_prior_VET_recompute_0p5128_at_floor_WRONG_actual_0p4762_"
                    "below_next_lever_verb_class_factivity_filter_byte_reproduce_exact_self_test_PASS"),
        "cert_increment_delta": 1,
        "cert_delta": {"CG": 0, "MM": 1, "HF": 0},
        "decision": (
            "MEASURED_MECHANISM / proven-bound (+1 MM), confirming the cell's PARTIAL_PRECISION_STUCK. Self-test "
            "PASSES; strict precision, FP decomposition, and injection-site audit all recompute EXACT off-disk "
            "(.venv, Fix #28), NOT from verdict_msg. THREE proven facts banked: (1) the topical-animate held "
            "subject KEEPS full ceiling recovery (N5 True, CMP 0.667=ceiling, RELF1-recall 0.933=ceiling), no "
            "regression (passive 1.00, reversal 1.00, ref_acc 0.8333 identical, overlay PASS); (2) it FIXES the "
            "held-subject source brain-faithfully (v1 inanimate 'time' -> animate 'george', inanimate_overfire "
            "1->0 = correct Centering backward-looking-center); (3) precision is STILL below floor (0.4762 < "
            "0.5143), and the residual FP is SUBJECT-INDEPENDENT -- non-factive/mental-state VERB coordination "
            "(wished, thought), NOT the held subject. Off-disk: all 4 excess FPs vs gold are svo(wished,george,"
            "{cool,dinner,place}) + svo(thought,susie,lunch), each with a CORRECT animate subject; the gold oracle "
            "reaches above-floor 0.5263 precisely by injecting ONLY on the factive-transitive sites (geo3 put, "
            "wolf2 killed) and never on the two non-factive sites -- so gold's site selection IS effectively a "
            "factivity filter. NEXT LEVER = verb-class/factivity filter, projected (unVETted) to reach the gold "
            "CEILING (not merely floor) and to UNIFY the parent's two separate residuals into one mechanism. MM "
            "(not CG): precision not clean/below floor, small N, single-annotator gold, composition rests on one "
            "question; NOT HF: recovery + subject fix are genuine and the next lever is localized + cheap. AMENDS "
            "(not supersedes) v1 775c6085c. Local-only; needs orchestrator store sync."),
        "hf_attribution": None,
        "framing_correction_vs_director": (
            "Director's load-bearing ask: verify the refined localization that the residual precision FP is "
            "SUBJECT-INDEPENDENT (non-factive-verb coordination), not the held subject, and that this CORRECTS the "
            "prior VET's own recompute. CONFIRMED off-disk, both parts. (1) SUBJECT-INDEPENDENCE: fixing time->"
            "george moved precision only +0.0111 (0.4651->0.4762); the animate 'george' still yields 3 non-factive "
            "svo(wished,george,*) FPs; susie2's FP was already subject-correct in v1 -> both residual sites are the "
            "SAME non-factive-verb class. (2) PRIOR-VET CORRECTION (symmetric honesty, my own prior recompute): the "
            "v1 landed-VET (cert_ledger 2026-07-18T20:00:31) predicted topical-animate reaches 20/39=0.5128 AT "
            "floor by 'removing 4 time FP'. That modeled the animate filter as SUPPRESSING the geo2 injection; it "
            "actually SWAPS the subject (time->george), george still fires because 'wished' is non-factive, and "
            "only the self-loop FP drops -> 20/42=0.4762 BELOW floor. The empirical build caught the VET error -- "
            "this is exactly why landed-VET verifies OFF DATA not off reports; the auditor's own prior recompute "
            "was wrong and is corrected here. CREDIT to the cell author: honest can-fail design (it landed PARTIAL, "
            "not the CLAUSE_SEG_CLEAN it hoped for), self-flagged the below-floor regression and the "
            "subject-independent hypothesis prominently, no goalpost move. AUDITOR SHARPENING: the cell's verdict_"
            "msg hedges the residual ('another inanimate hold OR susie-class complement mis-parse'); the precise "
            "truth is neither disjunct -- inanimate_overfire=0 and BOTH geo2 (wished) and susie2 (thought) are the "
            "same non-factive-verb class, so the next lever is a factivity filter, which (from the gold "
            "site-selection pattern) projects to the CEILING not just the floor. BRAIN-CHECK sound: non-factive/"
            "irrealis verbs assert no real event; the brain does not extract 'george did X to place' from 'wished "
            "for a place' -- Centering fixes the subject (done), factivity gates the event (the lever). Do NOT "
            "fold this as precision-neutral achieved; precision is still net-negative vs doing nothing until the "
            "factivity filter lands."),
        "cross_arc_overlap_check": XARC,
        "net_cert_delta": ("+1 MM (proven-bound refinement of the clause-seg chain; corrects the prior VET's "
                           "recompute). Genuine kernel = recovery kept + subject-source fixed brain-faithfully + "
                           "the new measured fact that the residual precision gap is subject-independent non-"
                           "factive-verb coordination. The verb-class/factivity filter (projected to reach the "
                           "gold ceiling) is the CG revival gate -- its own can-fail cell."),
        "supersedes": None,
        "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
        "ts_iso": _iso, "ts": _ts, "atom_id": atom["id"],
    }


def write_atomic_append(path, new_lines):
    if not path.exists():
        return (0, 0, False, "path does not exist: %s" % path)
    with open(path, "rb") as f:
        cur_bytes = f.read()
    cur_text = cur_bytes.decode("utf-8")
    pre_count = cur_text.count("\n")
    if cur_bytes and not cur_bytes.endswith(b"\n"):
        cur_bytes = cur_bytes + b"\n"
    parts = [cur_bytes]
    for line in new_lines:
        s = json.dumps(line, ensure_ascii=True)
        if "\n" in s:
            return (pre_count, pre_count, False, "JSON contains newline; not jsonl-safe")
        parts.append((s + "\n").encode("utf-8"))
    new_bytes = b"".join(parts)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "wb") as f:
        f.write(new_bytes); f.flush(); os.fsync(f.fileno())
    os.replace(tmp_path, path)
    with open(path, "rb") as f:
        verify_text = f.read().decode("utf-8")
    post_count = verify_text.count("\n")
    expected_post = pre_count + len(new_lines)
    if post_count != expected_post:
        return (pre_count, post_count, False, "line count mismatch: expected %d got %d" % (expected_post, post_count))
    tail = verify_text.rstrip("\n").split("\n")[-len(new_lines):]
    for i, tl in enumerate(tail):
        try:
            parsed = json.loads(tl)
        except Exception as e:
            return (pre_count, post_count, False, "tail-line %d JSON round-trip fail: %s" % (i, e))
        for key in ("id", "atom_id"):
            if key in new_lines[i] and parsed.get(key) != new_lines[i][key]:
                return (pre_count, post_count, False, "tail-line %d %s mismatch" % (i, key))
    return (pre_count, post_count, True, "OK")


def main():
    atom = build_atom()
    ledger = ledger_row(atom)
    print("=== A5 atom-write: reader_clauseseg_topical_animate_subject_v2 -> MM (precision gap SUBJECT-INDEPENDENT non-factive verb; corrects prior VET) (2026-07-18) ===")
    print("ts_iso =", _iso)
    assert atom["id"].isascii(), "non-ascii atom id"
    assert ledger["atom_id"] == atom["id"], "atom_id/id mismatch"

    existing = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                existing.add(json.loads(line).get("id"))
            except Exception:
                pass
    if atom["id"] in existing:
        print("ABORT: id already in store:", atom["id"]); sys.exit(1)
    print("id-uniqueness OK (1 new, not pre-existing)")

    print("Writing 1 atom to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, [atom])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 1 row to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, [ledger])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    n_ok = 0
    present = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            json.loads(line); n_ok += 1
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                present.add(json.loads(line).get("id"))
            except Exception:
                pass
    assert atom["id"] in present, "post-write integrity: new id missing"
    print("integrity: math/atoms.jsonl fully parses (%d lines), new id present." % n_ok)
    print()
    print("=== A5 WRITE COMPLETE (LOCAL ONLY; needs_orchestrator_store_sync=True; no origin push; no remote persist) ===")
    print("ATOM (MM):", atom["id"][:100], "...")


if __name__ == "__main__":
    main()
