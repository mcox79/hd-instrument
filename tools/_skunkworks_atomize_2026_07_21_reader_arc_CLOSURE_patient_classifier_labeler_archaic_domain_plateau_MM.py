"""
A5-gated atomization: exp_patient_specific_classifier_reader_filter_v1 (full, local) -> ONE closure atom
(2026-07-21). MEASURED_MECHANISM / proven-bound. Records the CLOSED reader-arc state; AMENDS (composes, does NOT
supersede) the reader-arc consolidated bank atoms 29394 (reader-endtoend) and 29397 (labeler-recalibration).

Author verdict HARD_FAIL_CLF_HURTS. Director honest re-read = "lateral move; the labeler is an archaic-domain-
bound PLATEAU, not a liftable lever." VET'd HARDEST off-disk. All 5 load-bearing claims reproduce BIT-EXACT from
metrics.json via independent .venv recompute (Fix #28, NOT verdict_msg). Auditor CONFIRMS the PLATEAU conclusion
is SOUND, tiers MEASURED_MECHANISM, and applies three DOWNWARD framing corrections to the Director's proposed
atom text (symmetric anti-negativity):
  (1) "reader = 0.790" -> ACHIEVED backoff e2e mean = 0.7723 (0.79 is the backoff RECALL CEILING, not achieved);
      the best-achieved arm is CLF_REPLACE 0.791; the HARD_FAIL is CLF_BACKOFF 0.7535 (-0.0189 vs backoff).
  (2) "small +0.027 all-seeds" -> backoff-vs-v1 = +0.029 MEAN but NOT all-seeds (seed-7 exactly 0.0; seed-13
      +0.0606; seed-19 +0.0263). The all-seeds-positive lever is CLF_REPLACE-vs-v1 (+0.0476 mean; +0.0256/+0.0909/
      +0.0263). Recorded honestly.
  (3) "~2/3 decision-coupling" -> WRONG FRAME. The residual is 88% EXTRACTION-bound / 12% decision (backoff 22:3;
      clf_backoff 24:3). The reader is EXTRACTION(labeling)-bound, NOT decision-bound. What is ~2/3-3/4 is the
      REGISTER-DRIVEN share of the LABELER losses: 8/11 = 0.727 not-patient-shaped.

INDEPENDENT OFF-DISK RECOMPUTE (.venv Scripts/python, off metrics.json, NOT verdict_msg; Fix #28), all confirmed:
  CLAIM 1 (Phase-1 taxonomy): loss_buckets {LABELER 11, POS_MISS 4, VERB_NOT_FOUND 3, PARSER_ATTACH 3}, total 21
    -> LABELER 0.5238, POS 0.1905, VERB_NOT_FOUND 0.1429, PARSER_ATTACH 0.1429. Raw-recount of the 11 labeler
    cases: patient_shaped-fixable = 3, not-shaped (register-driven) = 8, clf_recovers_extraction = 1. Gold labels
    of the 11: obl 6, nsubj 2, nmod 2, ccomp 1 -- i.e. the TRUE patient carries a NON-obj deprel in archaic
    relative/coordination/oblique constructions => a UD-EWT labeling register-mismatch, not a decision error.
  CLAIM 2 (Phase-2 frontier): clf patient-F1 0.8697 (P 0.8414 / R 0.9000) vs labeler 0.8957 (P 0.8867 / R 0.9049);
    F1 recomputed from P/R exact. clf-lab = -0.026; the binary detector is STRICTLY INSIDE the labeler's P/R
    frontier (both P and R strictly lower => dominated). clf does NOT beat the labeler in-domain.
  CLAIM 3 (Phase-3 e2e, means over seeds 7/13/19): unlabeled 0.7436, labeled_v1 0.7434, labeled_backoff 0.7723,
    clf_replace 0.791, clf_backoff 0.7535. PRIMARY gain clf_backoff-vs-backoff = -0.0189 (per-seed 0.0/-0.0303/
    -0.0263; min -0.0303) => CLF as a backoff HURTS = the HARD_FAIL. labeler_recovered_endtoend sum = 0 (all seeds).
  CLAIM 4 (leak-hunt): leak_guard max_single_feature = f_adj 0.6364 < 0.95 giveaway threshold; grammatical cue
    features (f_passive_flip, f_prep_patient_sense, f_alternation, f_passive_subject, f_prep_nonpatient_sense) all
    exactly 0.0; leak flag False; n_usable_pools 22. gold_meta: McGuffey gold is the annotator's independent
    reading of the text, reader output used ONLY to key sentence-ids; the clf is UD-EWT-deprel-trained (McGuffey
    never in train/tune); accept_idx / patient_arc_features take no gold arg. leak_clean=True confirmed.
  CLAIM 5 (residual partition): backoff correct 85 / extraction_err 22 / decision_err 3 (ext_frac 0.88);
    clf_backoff correct 83 / extraction 24 / decision 3 (ext_frac 0.8889). Reader is extraction(labeling)-bound.

THE LOAD-BEARING PLATEAU CONCLUSION -- "the labeler is archaic-domain-bound (register mislabels that ANY UD-EWT-
trained model, binary OR 36-way, reproduces) = a PLATEAU, not a liftable lever" -- is SOUND. Evidence:
  (a) 8/11 (0.727) labeler losses are NOT patient-shaped: the true patient surfaces as obl/nsubj/nmod/ccomp in
      archaic relative/coordination/oblique constructions => a training-DOMAIN (UD-EWT web text vs McGuffey
      archaic narrative) register mismatch, inherent to the labeling MODEL, not a per-item decision bug.
  (b) The INDEPENDENT UD-EWT-trained binary clf recovers extraction on only 1/11 labeler cases and 0 end-to-end
      (labeler_recovered_endtoend sum = 0) -- swapping the label head (36-way -> binary) does NOT lift the ceiling.
  (c) The binary clf's in-domain F1 (0.8697) is strictly INSIDE the 36-way labeler's P/R frontier (0.8957) --
      both UD-EWT models plateau at the same detection frontier.
  (d) The e2e residual is 88% extraction(labeling)-bound; only 12% decision. The ceiling is a labeling ceiling.
  (e) Prior arc atoms already closed the sibling levers: recalibration (29397, dead no-op), robust features,
      parser-ladder, patient-selection self-sup signal (29375). This cell closes the patient-classifier lever.
SCOPE CAVEAT (kept honest): N=100 single-annotator gold; only 11 labeler cases => proven-BOUND, not chain-grade.
"Not fixable by grammar/supervision" is precisely: not liftable by any OUT-OF-DOMAIN(UD-EWT)-trained labeling
model (binary or 36-way); IN-DOMAIN (McGuffey-supervised) relabeling could in principle fix it but is unavailable
here and would be circular with the test. BRAIN-CHECK / fix per the standing anchor = GROUNDING / meaning-override
(Gleitman) -- humans resolve the archaic register by event-structure/type-facts, not by richer syntactic labels --
which is the deeper open frontier, NOT tested here.

LOCAL ONLY: store_head_at_write=unsynced_needs_orchestrator; needs_orchestrator_store_sync=True; NO origin push;
NO remote persist; no git add -A.
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
ATOMIZED_BY = ("skunkworks_landed_vet_patient_specific_classifier_reader_filter_v1_reader_arc_CLOSURE_labeler_"
               "archaic_domain_plateau_MM_backoff_0p772_clf_replace_0p791_clf_backoff_0p7535_HARD_FAIL_binary_"
               "clf_inside_labeler_frontier_8of11_labeler_losses_register_driven_88pct_extraction_bound_leak_"
               "clean_fix_is_grounding_Gleitman_2026-07-21")
ATOMIZED_DATE = "2026-07-21"
ANCHOR = "patient_specific_classifier_reader_filter_v1"
CELL_COMMIT = "local_full_run_2026-07-21T06:13Z"  # full run; local, per-prereg no-origin-push contract

# reader-arc consolidated bank atoms this closure AMENDS/COMPOSES (does NOT supersede):
AMEND_READER_ENDTOEND = ("math::MEASURED_MECHANISM_reader_endtoend_whoaffected_v1v2_glassbox_reader_BUILT_0p725_"
                         "unlab_0p742_labeled_2x_crude_0p362_EXTRACTION_BOUND_28to0_labeled_POOL_COLLAPSE_"
                         "conditional_abstain_lifts_committed_precision")
AMEND_LABELER_RECAL = ("math::MEASURED_MECHANISM_labeler_patient_role_recalibration_v1_recal_bias_tuning_DEAD_no_"
                       "op_obj_under_prediction_REFUTED_domain_shift_False_register_invariant_robust_features_"
                       "within_noise_plus0p0085_single_seed_no_in_domain_regression_asset_untouched")

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

XARC = (
    "substrate_query 'patient classifier labeler register archaic domain plateau extraction reader' -> top hits "
    "cosine 0.29-0.3525, ALL generic concept nodes (0.3525 'reader', 0.3252 'register', 0.3018 'CN_register', "
    "0.291 'labeler') -- NONE is a prior duplicate cell. This IS the intended closure of the reader arc: it "
    "AMENDS (composes, does NOT supersede) the 2026-07-20/21 reader-arc bank (29394 reader-endtoend, 29397 "
    "labeler-recalibration) and the patient-selection null (29375). It is a TARGETED EXTENSION -- a NEW lever "
    "(patient-specific binary classifier as label-head replacement/backoff) distinct from recalibration/robust-"
    "features/parser-ladder -- not a rediscovery of a prior arc cell. CONFIRMED novel-lever closure at cosine<0.30 "
    "for any prior CELL."
)

ATOM_ID = (
    "math::MEASURED_MECHANISM_reader_arc_CLOSURE_patient_specific_classifier_labeler_ARCHAIC_DOMAIN_PLATEAU_v1_"
    "patient_binary_clf_does_NOT_lift_the_labeler_ceiling_e2e_backoff_0p7723_achieved_recall_ceiling_0p79_best_"
    "arm_clf_replace_0p791_HARD_FAIL_clf_as_backoff_HURTS_clf_backoff_0p7535_neg0p0189_vs_backoff_perseed_0p0_"
    "neg0p0303_neg0p0263_min_neg0p0303_labeler_recovered_e2e_sum_0_PHASE2_binary_clf_STRICTLY_INSIDE_labeler_PR_"
    "frontier_clf_F1_0p8697_P0p8414_R0p900_vs_labeler_0p8957_P0p8867_R0p9049_both_lower_dominated_clf_minus_lab_"
    "neg0p026_EXTRACTION_LOSS_TAXONOMY_LABELER_0p5238_11of21_POS_MISS_0p1905_4of21_VERB_NOT_FOUND_0p1429_3of21_"
    "PARSER_ATTACH_0p1429_3of21_of_the_11_LABELER_cases_8_NOT_patient_shaped_register_driven_3_patient_shaped_"
    "fixable_clf_recovers_extraction_1of11_gold_labels_obl6_nsubj2_nmod2_ccomp1_true_patient_carries_NONobj_"
    "deprel_in_archaic_relative_coordination_oblique_constructions_UD_EWT_labeling_register_mismatch_NOT_decision_"
    "error_RESIDUAL_88pct_EXTRACTION_bound_backoff_22to3_clf_backoff_24to3_only_12pct_decision_reader_is_LABELING_"
    "bound_LEAK_CLEAN_max_single_feature_f_adj_0p6364_lt_0p95_grammatical_cues_passive_flip_prep_sense_alternation_"
    "all_0p0_clf_UD_EWT_deprel_trained_McGuffey_gold_never_in_train_annotator_independent_reader_output_ONLY_keys_"
    "sentence_ids_leak_False_the_LABELER_PLATEAU_is_ARCHAIC_DOMAIN_BOUND_register_mislabels_any_UD_EWT_model_binary_"
    "or_36way_reproduces_NOT_liftable_by_recalibration_29397_robust_features_parser_ladder_patient_classifier_ALL_"
    "EXHAUSTED_fix_per_brain_check_is_GROUNDING_meaning_override_Gleitman_the_deeper_frontier_N100_single_annotator_"
    "11_labeler_cases_proven_BOUND_not_CG_AMENDS_29394_29397_composes_29375_CERT_plus0_LOCAL_ONLY_2026-07-21"
)

PLAIN = (
    "This closes the 'who-was-affected' reader arc. The reader's job is, for each verb in an archaic McGuffey "
    "reading, to pick the entity that was acted on (the patient). Its best honest end-to-end score is about 0.77 "
    "(the backoff pipeline; the recall ceiling for that pipeline is 0.79, and the single best-scoring arm, which "
    "replaces the label head with a fresh classifier, reaches 0.791). The question this cell asked was: can a "
    "PURPOSE-BUILT patient/not-patient classifier fix the reader's weakest link? Answer: NO. Bolted onto the "
    "existing pipeline as a backoff it actually HURTS (drops to 0.75, -0.019, worse on 2 of 3 seeds, better on "
    "none), and standalone it is strictly WORSE than the existing labeler at the detection task (F1 0.870 vs "
    "0.896, lower on both precision and recall). WHY it can't help: we broke down every reader miss. More than half "
    "(11 of 21) are LABELER errors -- the parser assigns the true patient a label like 'oblique' or 'subject' or "
    "'noun-modifier' instead of 'object', so the extractor skips it. And 8 of those 11 are NOT fixable by a "
    "better patient-detector: they are archaic constructions (relative clauses, 'and'-coordinations, oblique "
    "phrasings) where the true patient genuinely carries a non-object grammatical label. Any parser/labeler trained "
    "on modern web text (UD-EWT) -- whether it emits 36 labels or just 2 -- reproduces the SAME register "
    "mislabels, which is exactly why the binary classifier recovers only 1 of the 11 and improves the final score "
    "on zero of them. The reader is bound by LABELING, not by its final choice: 88% of its remaining errors are "
    "extraction (labeling) errors, only 12% are decision errors. So the labeler is a PLATEAU that is bound to the "
    "archaic DOMAIN, not a lever we can pull with a smarter classifier. The leak checks are clean (no single "
    "feature can pick the gold answer more than 64% of the time; the classifier never saw the McGuffey gold; the "
    "grammatical cue features are all zero-incidence). The honest fix, per how humans read this text and per our "
    "standing anchor, is GROUNDING -- resolving the archaic register by event-structure and world/type facts "
    "(Gleitman), not by squeezing more out of syntactic labels. That is the deeper open frontier and is NOT what "
    "this cell tested. Caveat that keeps this a proven-BOUND and not a chain-grade: the gold is a single-annotator "
    "set of 100 verb instances with only 11 labeler cases."
)

IMPORTANCE = (
    "MEDIUM (negative/bound; arc-CLOSING). It CLOSES the reader's who-was-affected extraction arc by proving the "
    "last cheap lever -- a purpose-built patient/not-patient classifier -- does NOT lift the labeler ceiling "
    "(HARD_FAIL as a backoff, strictly inside the labeler's detection frontier standalone). Together with the "
    "recalibration null (29397), robust-features, and parser-ladder closures, this establishes that the reader's "
    "~0.77 end-to-end plateau is an ARCHAIC-DOMAIN labeling bound: any UD-EWT-trained labeling model reproduces the "
    "same register mislabels, so the plateau is not liftable by relabeling (binary or 36-way). Value is in "
    "REDIRECTING effort: stop tuning the extractor/labeler, and route the remaining headroom to the GROUNDING / "
    "meaning-override frontier (Gleitman) -- resolving archaic register by event-structure and type facts. "
    "Importance is CAPPED at proven-BOUND: N=100 single-annotator gold with only 11 labeler cases; the plateau "
    "value is 0.772 achieved (0.79 ceiling), and the finding is a scoped negative, not a capability advance."
)

ATOM_CLAIM = (
    "MATH MEASURED_MECHANISM (proven-bound; reader-arc CLOSURE). CLAIM: the who-was-affected reader's ~0.77 end-to-"
    "end plateau is an ARCHAIC-DOMAIN LABELING bound that a purpose-built patient/not-patient classifier does NOT "
    "lift. Reproduced BIT-EXACT off-disk (.venv, off metrics.json, Fix #28): PHASE-3 e2e means over seeds 7/13/19 "
    "-- unlabeled 0.7436, labeled_v1 0.7434, labeled_backoff 0.7723 (recall ceiling 0.79), clf_replace 0.791 (best "
    "arm), clf_backoff 0.7535; PRIMARY gain clf_backoff-vs-backoff -0.0189 (per-seed 0.0/-0.0303/-0.0263; min "
    "-0.0303) = CLF-as-backoff HURTS (the HARD_FAIL); labeler_recovered_endtoend sum = 0. PHASE-2: the binary clf "
    "is STRICTLY INSIDE the 36-way labeler's P/R frontier -- clf patient-F1 0.8697 (P 0.8414 / R 0.9000) vs labeler "
    "0.8957 (P 0.8867 / R 0.9049), both P and R strictly lower (dominated), clf-lab -0.026. PHASE-1 extraction-loss "
    "taxonomy over 21 misses: LABELER 11 (0.5238), POS_MISS 4 (0.1905), VERB_NOT_FOUND 3 (0.1429), PARSER_ATTACH 3 "
    "(0.1429). Raw-recount of the 11 labeler cases: 8 NOT patient-shaped (register-driven), 3 patient-shaped-"
    "fixable, clf recovers extraction on only 1/11; the 11 gold labels are obl 6 / nsubj 2 / nmod 2 / ccomp 1 -- "
    "the true patient carries a NON-obj deprel in archaic relative/coordination/oblique constructions => a UD-EWT "
    "training-DOMAIN register mismatch, not a per-item decision error. RESIDUAL is 88% extraction(labeling)-bound "
    "(backoff 22:3; clf_backoff 24:3), only 12% decision -- the reader is LABELING-bound. AUDITOR DOWNWARD FRAMING "
    "CORRECTIONS vs the proposed atom text (symmetric anti-negativity): (i) 'reader = 0.790' is the backoff RECALL "
    "CEILING, not achieved -- achieved backoff = 0.7723; best-achieved arm = clf_replace 0.791; (ii) the backoff "
    "lever is +0.029 MEAN vs v1 but NOT all-seeds-positive (seed-7 exactly 0.0), whereas clf_replace-vs-v1 is the "
    "all-seeds-positive +0.0476 lever; (iii) 'decision-coupling ~2/3' is the WRONG frame -- the residual is 88% "
    "EXTRACTION-bound; the ~2/3-3/4 figure is the register-driven share of the LABELER losses (8/11 = 0.727). "
    "PLATEAU verdict SOUND: the labeler is archaic-domain-bound -- register mislabels that ANY UD-EWT-trained model "
    "(binary or 36-way) reproduces -- so it is not liftable by recalibration (29397), robust features, parser-"
    "ladder, or a patient-classifier (all now exhausted). Per brain-check the fix is GROUNDING / meaning-override "
    "(Gleitman), the deeper frontier, NOT tested here."
)

ATOM_RECOMPUTE = (
    "INDEP recompute (.venv Scripts/python, off data/exp_patient_specific_classifier_reader_filter_v1/metrics.json, "
    "NOT verdict_msg; Fix #28). ALL 5 load-bearing claims reproduce BIT-EXACT: "
    "(1) PHASE-1 taxonomy: loss_buckets {LABELER 11, POS_MISS 4, VERB_NOT_FOUND 3, PARSER_ATTACH 3}/21 -> "
    "0.5238/0.1905/0.1429/0.1429; raw-recount of 11 labeler cases -> patient_shaped 3, not-shaped 8, clf_recovers "
    "1; gold-label Counter obl 6, nsubj 2, nmod 2, ccomp 1. (2) PHASE-2: F1 recomputed from P/R -- clf "
    "2*0.8414*0.9/(0.8414+0.9)=0.8697 (=stored), labeler 2*0.8867*0.9049/(0.8867+0.9049)=0.8957 (=stored); clf "
    "P<lab_P AND clf R<lab_R => strictly dominated (inside frontier); clf-lab -0.026, clf_beats_labeler_indomain "
    "False. (3) PHASE-3: recomputed arm means from per_seed endtoend -- unlabeled 0.7436, v1 0.7434, backoff "
    "0.7723, clf_replace 0.791, clf_backoff 0.7535 (all = stored); clf_backoff-backoff per-seed [0.0,-0.0303,"
    "-0.0263] mean -0.0189 (=PRIMARY), min -0.0303; backoff-v1 per-seed [0.0,+0.0606,+0.0263] mean +0.029 (NOT "
    "all-seeds); clf_replace-v1 per-seed [+0.0256,+0.0909,+0.0263] mean +0.0476 (all-seeds-positive); "
    "labeler_recovered_endtoend [0,0,0] sum 0. (4) LEAK: leak_guard max_single_feature f_adj 0.6364 < 0.95; "
    "f_passive_flip/f_prep_patient_sense/f_alternation/f_passive_subject/f_prep_nonpatient_sense all 0.0; leak "
    "False; n_usable_pools 22; gold_meta confirms McGuffey annotator-independent, reader output ONLY keys "
    "sentence-ids, clf UD-EWT-deprel-trained (McGuffey never in train/tune); verdict leak_clean=True. (5) RESIDUAL: "
    "backoff correct 85 / ext 22 / dec 3 (ext_frac 0.88); clf_backoff correct 83 / ext 24 / dec 3 (ext_frac "
    "0.8889). baseline_in_band True, positive_control_backoff_ok True, arms_differ_verified True."
)

ATOM_SCOPE = (
    "Full run, local. Gold = McGuffey Third Reader lessons L04/L05/L07/L08/L09/L10/L12, single-annotator (exp_dev "
    "glass-box), 100 gold pos verb-patient pairs, hard_frac 0.91; parser arc_parser_mst_retrain_ud_ewt.npz; 3 "
    "seeds (7/13/19); patient clf trained on UD-EWT deprel only (McGuffey never in train/tune), pos_weight 2.0. "
    "LOAD-BEARING BOUNDS: "
    "(a) PROVEN-BOUND, NOT CHAIN-GRADE: N=100 single-annotator gold with only 11 labeler cases and a 3-of-11 "
    "patient-shaped subset -- the sample bounds this to a proven boundary, not a certified capability. The pos/"
    "nopat boundary involves annotator judgment calls (disclosed in gold_meta caveat). "
    "(b) THE PLATEAU IS ARCHAIC-DOMAIN-BOUND, NOT ABSOLUTELY UNFIXABLE: 'not fixable by grammar/supervision' means "
    "precisely NOT liftable by any OUT-OF-DOMAIN (UD-EWT web-text)-trained labeling model, binary or 36-way, "
    "because they reproduce the same register mislabels (8/11 register-driven; binary clf recovers 1/11, 0 e2e; "
    "clf F1 inside labeler frontier). IN-DOMAIN (McGuffey-supervised) relabeling could in principle fix it but is "
    "unavailable here and would be circular with the held-out gold. Do NOT over-read as 'no method can ever fix "
    "labeling on archaic prose'. "
    "(c) THE READER IS LABELING(EXTRACTION)-BOUND, NOT DECISION-BOUND: 88% of the e2e residual is extraction/"
    "labeling error, only 12% decision. The proposed-atom framing 'decision-coupling ~2/3' is corrected -- the "
    "~2/3-3/4 figure is the register-driven share of the LABELER losses (8/11 = 0.727), an extraction-side, not "
    "decision-side, quantity. "
    "(d) ACHIEVED vs CEILING: the reader's achieved backoff e2e = 0.7723 (recall ceiling 0.79); the best-achieved "
    "arm is clf_replace 0.791; the HARD_FAIL is clf_backoff 0.7535. Do NOT cite '0.790' as an achieved reader "
    "score -- it is the backoff recall CEILING. "
    "BRAIN-CHECK: humans resolve the archaic register mostly by GRAMMAR/word-order + event-STRUCTURE / type facts "
    "(Gleitman: syntactic bootstrapping is bounded; observed event structure / world knowledge disambiguates), NOT "
    "by richer syntactic labels on an out-of-domain parser. Same limitation in the brain's syntax-only route => the "
    "labeling plateau is a REAL structural bound for the label-only approach; the brain's FIX (grounding / meaning-"
    "override) is the substrate-native lever, the deeper open frontier. REVIVAL toward chain-grade requires the "
    "GROUNDING route: resolve the register-mislabeled patients via event-structure / type-fact grounding (the "
    "single-edge-grounding / codebook / affectedness-grounding frontier) on this exact gold, and show the 8/11 "
    "register-driven labeler losses recover WITHOUT in-domain label supervision. Extending the gold to a multi-"
    "annotator, larger corpus would additionally lift the sample bound."
)

ATOM_METRICS = {
    "e2e_unlabeled_mean": 0.7436, "e2e_labeled_v1_mean": 0.7434, "e2e_labeled_backoff_mean": 0.7723,
    "e2e_clf_replace_mean": 0.791, "e2e_clf_backoff_mean": 0.7535,
    "backoff_recall_ceiling": 0.79, "clf_backoff_recall_ceiling": 0.78,
    "PRIMARY_gain_clf_backoff_vs_backoff_mean": -0.0189, "gain_clf_backoff_vs_backoff_perseed": [0.0, -0.0303, -0.0263],
    "gain_clf_backoff_vs_backoff_min": -0.0303,
    "gain_backoff_vs_v1_mean": 0.029, "gain_backoff_vs_v1_perseed": [0.0, 0.0606, 0.0263],
    "gain_backoff_vs_v1_all_seeds_positive": False,
    "gain_clf_replace_vs_v1_mean": 0.0476, "gain_clf_replace_vs_v1_perseed": [0.0256, 0.0909, 0.0263],
    "gain_clf_replace_vs_v1_all_seeds_positive": True,
    "labeler_recovered_endtoend_sum": 0,
    "phase2_clf_patient_f1": 0.8697, "phase2_clf_P": 0.8414, "phase2_clf_R": 0.9000,
    "phase2_labeler_patient_f1": 0.8957, "phase2_labeler_P": 0.8867, "phase2_labeler_R": 0.9049,
    "phase2_clf_minus_labeler_f1": -0.026, "phase2_clf_strictly_inside_labeler_PR_frontier": True,
    "phase2_clf_beats_labeler_indomain": False,
    "phase1_loss_buckets": {"LABELER": 11, "POS_MISS": 4, "VERB_NOT_FOUND": 3, "PARSER_ATTACH": 3},
    "phase1_loss_fracs": {"LABELER": 0.5238, "POS_MISS": 0.1905, "VERB_NOT_FOUND": 0.1429, "PARSER_ATTACH": 0.1429},
    "phase1_n_extraction_miss": 21,
    "phase1_labeler_patient_shaped_fixable": 3, "phase1_labeler_not_shaped_register_driven": 8,
    "phase1_labeler_not_shaped_frac": 0.727, "phase1_labeler_clf_recovers_extraction": 1,
    "phase1_labeler_gold_label_dist": {"obl": 6, "nsubj": 2, "nmod": 2, "ccomp": 1},
    "residual_backoff_ext_to_dec": "22:3", "residual_backoff_extraction_frac": 0.88,
    "residual_clf_backoff_ext_to_dec": "24:3", "residual_clf_backoff_extraction_frac": 0.8889,
    "leak_max_single_feature": "f_adj", "leak_max_single_feature_acc": 0.6364, "leak_giveaway_threshold": 0.95,
    "leak_grammatical_cue_features_all_zero": True, "leak_flag": False, "leak_clean": True,
    "clf_trained_on_ud_ewt_deprel_only_mcguffey_never_in_train": True,
    "gold_n_pos_pairs": 100, "gold_single_annotator": True, "gold_hard_frac": 0.91, "seeds": [7, 13, 19],
    "baseline_in_band": True, "positive_control_backoff_ok": True, "arms_differ_verified": True,
    "cell_verdict": "HARD_FAIL_CLF_HURTS",
    "auditor_tier": ("MEASURED_MECHANISM / proven-bound; reader-arc CLOSURE; labeler is archaic-domain-bound "
                     "PLATEAU (register mislabels any UD-EWT model reproduces, binary or 36-way); patient-"
                     "classifier lever exhausted; fix = grounding (Gleitman), deeper frontier, not tested here"),
}

COMPOSES = [
    ("AMENDS (composes, does NOT supersede) atom 29394 reader-endtoend-whoaffected v1v2 (reader BUILT 0.725 unlab / "
     "0.742 labeled, EXTRACTION-BOUND): this closure UPDATES the arc's achieved e2e to 0.7723 (backoff; recall "
     "ceiling 0.79) / 0.791 (clf_replace best arm) and CONFIRMS + SHARPENS the 'extraction-bound' finding to "
     "88%-extraction / 12%-decision, with the extraction bound now MECHANISM-ATTRIBUTED to archaic-domain LABELER "
     "register mislabels (LABELER 52% of misses; 8/11 register-driven). 29394's core claim stands; this atom adds "
     "the closed patient-classifier lever and the plateau attribution."),
    ("AMENDS (composes, does NOT supersede) atom 29397 labeler-patient-role-recalibration v1 (recal = dead no-op; "
     "obj-under-prediction REFUTED; domain_shift False): together with THIS cell, the two exhaust the label-head "
     "levers -- recalibration does not help AND a purpose-built binary patient classifier does not help (HARD_FAIL "
     "as backoff; strictly inside the labeler frontier standalone). Consistent mechanism: the labeler ceiling is "
     "not a bias/miscalibration and not a 36-way-vs-binary head issue -- it is an out-of-domain (UD-EWT) register "
     "bound reproduced by any such model."),
    ("BUILDS ON / composes atom 29375 (patient-selection / affectedness self-sup signal null): 29375 VET'd that no "
     "self-supervised text-internal signal correlates with gold patient-correctness for this reader failure class. "
     "This cell's leak-clean binary classifier (max single feature 0.636, grammatical cues zero-incidence) is a "
     "consistent corroboration -- a supervised UD-EWT detector also cannot beat the labeler frontier, and the "
     "residual is labeling-bound. Together they point the same way: the fix is GROUNDING, not more text-internal / "
     "syntactic signal."),
    ("SIBLING of the 2026-07-20 grounding-frontier bank (single-edge-grounding-hd-binding, affectedness-change-of-"
     "state, event-outcome-density, settling-fix-learned-recurrent -- all MM/negative): the same session-wide wall "
     "-- text-internal / distributional / out-of-domain-syntactic signals do NOT supply per-instance thematic "
     "affectedness; the standing FIX is grounding / meaning-override (Gleitman). This closure is the reader-side "
     "counterpart on the archaic McGuffey extraction pipeline."),
    ("credit: Gleitman 1990 (syntactic bootstrapping bounded; observed event structure / world knowledge "
     "disambiguates argument structure) for the brain-check fix framing; Universal Dependencies / UD-EWT for the "
     "labeler training domain; the McGuffey Third Reader (PG#14766, public domain) for the gold corpus. The cell "
     "AUTHOR (exp_dev) CREDITED for an HONEST design: a proper extraction-loss taxonomy, a leak guard (max single "
     "feature 0.636 < 0.95, grammatical cues zero-incidence), a positive control (backoff), arms-differ "
     "verification, and a correct HARD_FAIL verdict. The auditor CONFIRMS the HARD_FAIL and the plateau attribution "
     "off-disk and applies three downward framing corrections to the summary numbers (symmetric anti-negativity)."),
]

OVER_READS = [
    ("Do NOT cite '0.790' as the reader's ACHIEVED end-to-end score. 0.79 is the backoff RECALL CEILING "
     "(candidate_recall_ceilings.labeled_backoff); the ACHIEVED backoff e2e mean is 0.7723, and the best-achieved "
     "arm is clf_replace 0.791. Report achieved backoff 0.772 (ceiling 0.79) / clf_replace 0.791 best arm."),
    ("Do NOT describe the backoff lever as '+0.027 all-seeds'. Backoff-vs-v1 is +0.029 MEAN but NOT all-seeds-"
     "positive: seed-7 is exactly 0.0 (seed-13 +0.0606, seed-19 +0.0263). The all-seeds-positive lever is "
     "clf_replace-vs-v1 (+0.0476 mean; +0.0256/+0.0909/+0.0263). State the arm and the per-seed spread."),
    ("Do NOT frame the reader as '~2/3 decision-coupled'. The e2e residual is 88% EXTRACTION(labeling)-bound and "
     "only 12% decision (backoff 22:3). The ~2/3-3/4 figure is the REGISTER-DRIVEN share of the LABELER losses "
     "(8/11 = 0.727), an extraction-side quantity. The reader is LABELING-bound, not decision-bound."),
    ("Do NOT over-read the plateau as 'no method can fix archaic-prose labeling'. It is bound to OUT-OF-DOMAIN "
     "(UD-EWT)-trained labeling models (binary or 36-way); in-domain supervised relabeling could fix it but is "
     "unavailable/circular here. The proven claim is: the patient-CLASSIFIER lever (and recalibration, robust "
     "features, parser-ladder) do not lift it. The remaining route is GROUNDING (untested here)."),
]

REVIVAL = [
    ("PROMOTE toward chain-grade requires the GROUNDING route (the brain-check fix): resolve the register-"
     "mislabeled patients via event-structure / type-fact grounding (single-edge-grounding / learned-codebook / "
     "affectedness-grounding frontier) on THIS exact McGuffey gold, and show the 8/11 register-driven LABELER "
     "losses recover WITHOUT in-domain label supervision. If grounding lifts the labeling ceiling where "
     "relabeling/recalibration/classifier cannot, upgrade toward CG."),
    ("LIFT THE SAMPLE BOUND: re-run on a multi-annotator, larger (multi-reader / multi-domain) gold to convert the "
     "N=100 single-annotator, 11-labeler-case proven-BOUND into a stronger boundary; check the 88%-extraction / "
     "12%-decision split and the 8/11 register-driven share hold at scale."),
    ("CROSS-DOMAIN CONTROL: run the identical pipeline on modern (UD-EWT-domain) narrative text; if the LABELER "
     "loss fraction collapses there, that directly confirms the plateau is a training-DOMAIN register mismatch "
     "(archaic McGuffey) rather than an intrinsic labeling limit -- sharpening the 'archaic-domain-bound' attribution."),
]

GENUINE_POS = (
    "GENUINE positives preserved (symmetric anti-negativity): this is a CLEAN, well-designed, arc-CLOSING negative "
    "and I credit exactly what it earns. Independently verified off-disk: (1) the extraction-loss TAXONOMY is real "
    "and load-bearing -- it localizes 52% of reader misses to the LABELER and, crucially, shows 8/11 of those are "
    "register-driven (true patient carries a non-obj deprel in archaic constructions), which is the mechanism "
    "attribution that makes the plateau conclusion sound rather than asserted; (2) the leak guard is genuinely "
    "clean (max single feature 0.636 < 0.95, all grammatical-cue features zero-incidence, clf trained on UD-EWT "
    "with McGuffey gold never in train/tune, annotator-independent gold) -- the HARD_FAIL is a real substantive "
    "negative, not a leak or a test-design artifact; (3) the positive control (backoff) clears its own band and "
    "the arms provably differ -- the discriminator is live; (4) the decision (CLF-as-backoff HURTS -0.019, binary "
    "clf strictly inside the labeler's detection frontier) is a substantive, correctly-signed finding that closes "
    "the last cheap extractor/labeler lever. What this IS: a decisive CLOSURE of the reader's who-was-affected "
    "extraction arc with a mechanism-attributed plateau (archaic-domain labeling bound) that correctly REDIRECTS "
    "effort to the grounding frontier. What it is NOT (the scope that keeps it honest): a chain-grade result (N=100 "
    "single-annotator, 11 labeler cases = proven-BOUND), an absolute 'labeling is unfixable' claim (it is bound to "
    "out-of-domain relabeling), or evidence about the grounding fix (untested here). The auditor's three downward "
    "framing corrections (0.790->0.772 achieved; +0.027-all-seeds->+0.029-mean-not-all-seeds; decision-coupling->"
    "88%-extraction-bound) SHARPEN the honest state; they do not diminish a genuine, valuable arc closure."
)


def build_atom():
    return {
        "id": ATOM_ID, "name": ATOM_CLAIM, "corpus": "math", "tier": "MEASURED_MECHANISM",
        "kind": "experiment_landed_vet",
        "cert_status": "proven-bound",
        "cert_class": ("reader_arc_CLOSURE_patient_specific_classifier_labeler_ARCHAIC_DOMAIN_PLATEAU_binary_clf_"
                       "does_NOT_lift_labeler_ceiling_HARD_FAIL_clf_backoff_neg0p0189_strictly_inside_labeler_PR_"
                       "frontier_8of11_labeler_losses_register_driven_88pct_extraction_bound_leak_clean_not_"
                       "liftable_by_recalibration_robust_features_parser_ladder_patient_classifier_ALL_EXHAUSTED_"
                       "fix_is_GROUNDING_meaning_override_Gleitman_deeper_frontier_N100_single_annotator_proven_"
                       "bound_not_CG_amends_29394_29397_composes_29375"),
        "plain_language": PLAIN,
        "importance": IMPORTANCE,
        "description": (ATOM_CLAIM + "\n\nPLAIN LANGUAGE: " + PLAIN + "\n\nRECOMPUTE (off-disk .venv, Fix #28): "
                        + ATOM_RECOMPUTE + "\n\nHONEST SCOPE: " + ATOM_SCOPE),
        "aliases": [
            "reader who-was-affected arc CLOSURE: patient-classifier does NOT lift the labeler ceiling (MM)",
            "reader e2e backoff 0.7723 achieved (recall ceiling 0.79); best arm clf_replace 0.791; HARD_FAIL clf_backoff 0.7535 (-0.0189)",
            "binary patient clf strictly INSIDE the 36-way labeler P/R frontier (F1 0.8697 vs 0.8957)",
            "extraction-loss taxonomy: LABELER 52% / POS 19% / verb-not-found 14% / parser-attach 14%",
            "8/11 labeler losses register-driven (true patient carries non-obj deprel in archaic constructions)",
            "reader is 88% extraction(labeling)-bound / 12% decision-bound (NOT ~2/3 decision-coupled)",
            "labeler PLATEAU is ARCHAIC-DOMAIN-BOUND: any UD-EWT model (binary or 36-way) reproduces the register mislabels",
            "recalibration/robust-features/parser-ladder/patient-classifier ALL exhausted; fix = grounding (Gleitman)",
            "leak-clean (max single feature 0.636 < 0.95; grammatical cues zero; McGuffey gold never in clf train)",
            "SCOPE: N=100 single-annotator, 11 labeler cases => proven-BOUND not CG; grounding fix untested",
        ],
        "ts_iso": _iso, "ts": _ts,
        "serves_capability": ("who_was_affected_reader_extraction_arc_CLOSED_labeler_archaic_domain_plateau_"
                              "patient_classifier_lever_exhausted_redirect_to_grounding_frontier"),
        "metadata": {
            "provenance_quality": ("independent_venv_offdisk_recompute_off_metrics_json_all_5_load_bearing_claims_"
                                   "bit_exact_phase1_taxonomy_phase2_frontier_phase3_e2e_means_leak_guard_residual_"
                                   "partition_plus_raw_recount_of_11_labeler_cases_gold_label_dist_three_downward_"
                                   "framing_corrections_applied_symmetric_anti_negativity"),
            "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes": None,
            "amends_atom_ids": [AMEND_READER_ENDTOEND, AMEND_LABELER_RECAL],
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_patient_specific_classifier_reader_filter_v1/metrics.json",
            "plain_language": PLAIN, "importance": IMPORTANCE,
            "verified_off_data": ATOM_RECOMPUTE, "honest_scope": ATOM_SCOPE, "metrics": ATOM_METRICS,
            "over_reads_corrected": OVER_READS,
            "genuine_positives_symmetric_anti_negativity": GENUINE_POS,
            "revival_criteria": REVIVAL,
            "cross_arc_overlap_check": XARC,
            "plateau_soundness_verdict": (
                "SOUND. 'The labeler is archaic-domain-bound (register mislabels any UD-EWT model reproduces, binary "
                "or 36-way) = a PLATEAU not a liftable lever' is supported by: (a) 8/11 (0.727) labeler losses NOT "
                "patient-shaped -- true patient carries obl(6)/nsubj(2)/nmod(2)/ccomp(1) in archaic relative/"
                "coordination/oblique constructions = training-DOMAIN register mismatch; (b) independent UD-EWT "
                "binary clf recovers extraction on 1/11, 0 e2e; (c) clf in-domain F1 0.8697 strictly INSIDE labeler "
                "frontier 0.8957; (d) residual 88% extraction-bound; (e) sibling levers (recalibration 29397, robust "
                "features, parser-ladder, self-sup signal 29375) already closed. NOT over-read; scoped to out-of-"
                "domain relabeling (in-domain supervision unavailable/circular). Brain-check fix = grounding/meaning-"
                "override (Gleitman), the deeper frontier, untested here. Tier proven-BOUND (N=100 single-annotator, "
                "11 labeler cases), not chain-grade."),
            "framing_corrections_applied": {
                "reader_score_0p790": "backoff RECALL CEILING (0.79), not achieved; achieved backoff 0.7723; best arm clf_replace 0.791",
                "plus0p027_all_seeds": "backoff-vs-v1 +0.029 MEAN, NOT all-seeds (seed-7 = 0.0); all-seeds-positive lever is clf_replace-vs-v1 +0.0476",
                "decision_coupling_two_thirds": "WRONG frame; residual 88% EXTRACTION-bound / 12% decision; the ~2/3-3/4 is the register-driven share of LABELER losses (8/11 = 0.727)",
            },
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "every_negative_check_how_the_brain_does_it_proactively_USER",
                "HF_structural_bound_vs_test_design_failure_positive_control_clears_own_floor_first",
                "arc_continuation_is_not_closure_unless_lever_exhausted",
                "synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data",
                "substrate_kb_concept_overlap_check_on_schema_vet",
                "director_over_read_positives_this_session_VET_hardest_caveat_interpretation_not_just_verdicts",
                "grounding_meaning_override_Gleitman_is_the_standing_fix_for_the_affectedness_wall",
            ],
            "composes_with": COMPOSES,
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE,
            "needs_orchestrator_store_sync": True,
            "local_write_only_no_origin_push_no_remote_persist": True,
        },
    }


def ledger_row(atom):
    return {
        "op": "landed_vet_atomize", "corpus": "math", "tier": atom["tier"], "cert_status": atom["cert_status"],
        "cert_class": ("MEASURED_MECHANISM_reader_arc_CLOSURE_patient_classifier_labeler_ARCHAIC_DOMAIN_PLATEAU_"
                       "HARD_FAIL_clf_hurts_binary_clf_inside_labeler_frontier_88pct_extraction_bound_leak_clean_"
                       "fix_is_grounding_Gleitman_proven_bound_not_CG"),
        "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes_commit": None,
        "supersedes_atom_id": None,
        "amends_atom_id": [AMEND_READER_ENDTOEND, AMEND_LABELER_RECAL],
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True,
        "auditor": "hdi_skunkworks", "atomized_by": ATOMIZED_BY,
        "author_verdict": "HARD_FAIL_CLF_HURTS",
        "verdict": ("MEASURED_MECHANISM / proven-bound reader-arc CLOSURE. A purpose-built patient/not-patient "
                    "binary classifier does NOT lift the labeler ceiling: HARD_FAIL as a backoff (clf_backoff "
                    "0.7535, -0.0189 vs backoff 0.7723, per-seed 0.0/-0.0303/-0.0263), and strictly INSIDE the "
                    "36-way labeler's P/R frontier standalone (F1 0.8697 vs 0.8957, both P and R lower). "
                    "Extraction-loss taxonomy LABELER 52% / POS 19% / verb-not-found 14% / parser-attach 14%; 8/11 "
                    "labeler losses register-driven (true patient carries non-obj deprel in archaic constructions); "
                    "residual 88% extraction(labeling)-bound. Leak-clean (max single feature 0.636 < 0.95; "
                    "grammatical cues zero-incidence; clf UD-EWT-trained, McGuffey gold never in train; annotator-"
                    "independent). The labeler PLATEAU is archaic-domain-bound (any UD-EWT model, binary or 36-way, "
                    "reproduces the register mislabels); not liftable by recalibration (29397)/robust-features/"
                    "parser-ladder/patient-classifier -- ALL exhausted. Fix per brain-check = grounding/meaning-"
                    "override (Gleitman), the deeper frontier, not tested here. All 5 load-bearing claims reproduce "
                    "bit-exact off-disk."),
        "cert_increment_delta": 0,
        "decision": (
            "MEASURED_MECHANISM / proven-bound. Author verdict HARD_FAIL_CLF_HURTS confirmed off-disk; Director "
            "honest re-read 'lateral move; labeler is an archaic-domain-bound PLATEAU' is SOUND. Every load-bearing "
            "claim reproduces BIT-EXACT (.venv off metrics.json, Fix #28): Phase-1 taxonomy (LABELER 11/0.5238, POS "
            "4/0.1905, verb-not-found 3/0.1429, parser-attach 3/0.1429; raw-recount 8/11 register-driven, 3 patient-"
            "shaped, clf recovers 1/11; gold labels obl6/nsubj2/nmod2/ccomp1); Phase-2 (clf F1 0.8697 strictly "
            "inside labeler 0.8957 frontier, both P and R lower); Phase-3 (backoff 0.7723, clf_replace 0.791, "
            "clf_backoff 0.7535; PRIMARY -0.0189; labeler_recovered sum 0); leak (max single feature 0.636 < 0.95, "
            "grammatical cues 0.0, leak False); residual (88% extraction-bound). PLATEAU SOUND: the labeling ceiling "
            "is a training-DOMAIN (UD-EWT vs archaic McGuffey) register bound reproduced by any UD-EWT labeling "
            "model; the patient-classifier is the last cheap extractor/labeler lever and it is now closed alongside "
            "recalibration (29397), robust features, parser-ladder, and the self-sup signal null (29375). "
            "THREE DOWNWARD FRAMING CORRECTIONS applied (symmetric anti-negativity): (i) 0.790 is the backoff RECALL "
            "CEILING not achieved (achieved backoff 0.7723; best arm clf_replace 0.791); (ii) '+0.027 all-seeds' -> "
            "backoff-vs-v1 +0.029 MEAN but seed-7 exactly 0.0 (all-seeds-positive lever is clf_replace-vs-v1 "
            "+0.0476); (iii) 'decision-coupling ~2/3' is WRONG -- residual 88% extraction-bound; the ~2/3-3/4 is the "
            "register-driven share of LABELER losses (8/11 = 0.727). AMENDS (composes, does NOT supersede) 29394 "
            "reader-endtoend and 29397 labeler-recalibration; composes 29375 self-sup null. BANKED: the closed "
            "patient-classifier lever + the archaic-domain-labeling plateau attribution + the extraction/decision "
            "split. NOT BANKED: the grounding fix (untested), any in-domain-supervised relabeling, a larger/multi-"
            "annotator gold. CERT delta +0 (arc-closing proven boundary; N=100 single-annotator, 11 labeler cases "
            "= proven-BOUND, not chain-grade). Local-only; needs orchestrator store sync."),
        "framing_correction_vs_director": (
            "Director framed the closed state as 'reader backoff+MST = 0.790, small +0.027 all-seeds, ~2/3 decision-"
            "coupling' and asked me to VET the plateau conclusion + leak-hunt HARDEST. RESULT: the PLATEAU "
            "conclusion is SOUND and the HARD_FAIL is a genuine substantive negative (leak-clean; positive control "
            "clears its band). I apply THREE downward corrections to the summary numbers (symmetric anti-"
            "negativity): (1) '0.790' is the backoff RECALL CEILING (0.79), not an achieved score -- achieved "
            "backoff e2e = 0.7723; the best-achieved arm is clf_replace 0.791; the HARD_FAIL is clf_backoff 0.7535 "
            "(-0.0189). (2) '+0.027 all-seeds' -- backoff-vs-v1 is +0.029 MEAN but NOT all-seeds (seed-7 is exactly "
            "0.0); the all-seeds-positive lever is clf_replace-vs-v1 (+0.0476). (3) '~2/3 decision-coupling' is the "
            "WRONG frame -- the residual is 88% EXTRACTION(labeling)-bound / 12% decision; the ~2/3-3/4 figure is "
            "the register-driven share of the LABELER losses (8/11 = 0.727), an extraction-side quantity. The "
            "substance of the Director's read is fully confirmed: the labeler is an archaic-domain-bound plateau "
            "(register mislabels any UD-EWT model reproduces, binary or 36-way), the patient-classifier lever is "
            "exhausted, and the fix per brain-check is grounding/meaning-override (Gleitman). exp_dev CREDITED for "
            "a clean design (extraction-loss taxonomy, leak guard, positive control, arms-differ, correct HARD_FAIL)."),
        "cross_arc_overlap_check": XARC,
        "net_cert_delta": ("+0. Arc-CLOSING proven boundary. Banks the closed patient-classifier lever (HARD_FAIL "
                           "as backoff; binary clf strictly inside the 36-way labeler frontier) and the mechanism-"
                           "attributed archaic-domain LABELING plateau (8/11 labeler losses register-driven; 88% "
                           "extraction-bound residual; leak-clean). Establishes the reader's ~0.77 e2e plateau "
                           "(achieved backoff 0.7723; ceiling 0.79; best arm clf_replace 0.791) as not liftable by "
                           "any out-of-domain relabeling and redirects headroom to the grounding frontier "
                           "(Gleitman). Proven-BOUND (N=100 single-annotator, 11 labeler cases), not chain-grade; "
                           "does not advance the capability CERT count."),
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
    print("=== A5 atom-write: reader-arc CLOSURE patient_specific_classifier_reader_filter_v1 -> MM (2026-07-21) ===")
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
    pre_atom_count = len(existing)
    # confirm the 5 reader-arc bank atoms (29393-29397) are present + the 2 amend targets exist
    assert AMEND_READER_ENDTOEND in existing, "amend target 29394 (reader-endtoend) MISSING from store"
    assert AMEND_LABELER_RECAL in existing, "amend target 29397 (labeler-recal) MISSING from store"
    print("amend targets present: 29394 reader-endtoend OK, 29397 labeler-recal OK")
    if atom["id"] in existing:
        print("ABORT: id already in store:", atom["id"]); sys.exit(1)
    print("id-uniqueness OK (1 new, not pre-existing); pre-write atom count =", pre_atom_count)

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
    # earlier bank atoms still intact
    assert AMEND_READER_ENDTOEND in present and AMEND_LABELER_RECAL in present, "post-write: amend targets vanished"
    print("integrity: math/atoms.jsonl fully parses (%d lines), new id present, amend targets intact." % n_ok)
    print("new atom count =", len(present), "(was", pre_atom_count, ")")
    print()
    print("=== A5 WRITE COMPLETE (LOCAL ONLY; needs_orchestrator_store_sync=True; no origin push; no remote persist) ===")
    print("ATOM (MEASURED_MECHANISM / proven-bound):", atom["id"][:110], "...")


if __name__ == "__main__":
    main()
