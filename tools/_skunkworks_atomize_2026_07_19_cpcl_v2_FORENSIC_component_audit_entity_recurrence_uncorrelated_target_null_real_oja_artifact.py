"""A5-gated atomization: FORENSIC component-audit of exp_contrastive_entity_recurrence_reader_loop_cpcl_v2 (2026-07-19).
  HARD_FAIL / honest-negative. USER-directed DEEP FORENSIC COMPONENT-AUDIT (was the test FAIR, each component USED
  correctly, did each DO its job, WHERE did it go wrong) BEFORE any strategic signal-absence call. 5 decisive checks
  measured OFF-DISK via independent .venv recompute reusing the cell's OWN functions (Fix #28; NOT verdict_msg).

VERDICT: the HARD_FAIL (loop adds NO self-supervised gain to patient-selection) is a REAL NULL, robustly confirmed by
  TWO independent measurements -- NOT a harness bug. BUT the cell's "P1 loop ACTIVELY HURTS -0.060 / P3 DECREASING"
  narrative is an OJA OVER-DECAY TEST-DESIGN ARTIFACT: with Oja off, CONTRAST recovers to EXACTLY FROZEN (delta +0.0000)
  on ALL 3 seeds. Correct characterization = CLEAN NULL (adds nothing), not active harm. The TARGET (entity-recurrence
  continuation) is genuinely UNCORRELATED with patient-correctness (measured corr ~0; locatives recur as much as themes;
  min-err selects gold BELOW chance) -> entity-recurrence is a proven BAD/wrong TARGET, which distinguishes
  "bad-target" (proven here) from "no-target-possible" (NOT proven by one cell; rests on 6-signal induction + brain).

FORENSIC COMPONENT-BY-COMPONENT (all off-disk .venv recompute; forensic script reused cell functions at full config):
  CHECK 1  TARGET FAIRNESS (most load-bearing) -- FLAW BUT IT IS THE FINDING, NOT A SILENT DEGRADATION:
    corr(err, correct) = +0.011 (all 225 eval cands) / -0.045 (204 with a real continuation target); corr(f_pred,
    correct) = mirror +-0.04. NEAR-ZERO. mean err correct 0.2472 vs wrong 0.2448 (gap -0.0025); have-cont correct
    0.2148 vs wrong 0.2200 (gap +0.0052) = noise-level. min-err would SELECT gold in 5/19 = 0.263 of multi-rival pos
    instances vs chance 0.386 -- BELOW chance. LOCATIVE CONFOUND directly MEASURED (exp_dev only ASSERTED it): mean err
    over-extracted-on-nopat obliques/locatives 0.2512 ~= correct-patients 0.2472 (diff +0.0039). => the entity-
    recurrence signal carries ~zero patient-correctness information on this corpus; it CANNOT separate a contacted theme
    from a recurring locative/oblique. The TARGET is the wrong signal. This is a genuine measured finding (bad target),
    not a broken component.
  CHECK 2  CODEBOOK SURVIVAL under SimHash bipolarization -- FAIR/CORRECT:
    continuous ppmi_svd held-out relatedness AUC = 0.9264 (independently REPRODUCES the STEP-1 codebook CG's 0.927 off
    the cached codes + wordsim353+simlex999 top-tercile TRUE vs pooled RANDOM). SimHash-BIPOLAR codes the loop ACTUALLY
    consumed (sign(code @ P), P seed 404, N=1024) AUC = 0.8952 -> retains 92.7% of the above-chance signal. The codes
    were NOT degraded; the loop ran on validated-strength similarity structure. Component correct.
  CHECK 3  UPDATE DIRECTION -- CORRECT (not a sign error / mis-built contrast):
    104/104 mined contrast pairs have pos(low-err) f_pred > neg(high-err) f_pred (100%). The contrast pass up-weights
    the recurrence-fit feature f_pred as designed: coef[idx6] frozen 0.734 -> contrast 1.168 -> contrast-noOja 2.418.
    The loop correctly rewards low-err/high-recurrence-fit rivals. The -0.060 is NOT a sign bug; it is up-weighting a
    non-informative (Check 1) feature while the Oja decay crushes the good structural cues (idx3-5 frozen -12.4/-10.9/
    -12.0 -> Oja-contrast -1.3/-2.2/-2.4).
  CHECK 4  FROZEN-AT-CEILING -- NO (drop is informative, not forced):
    FROZEN precision 0.4337 with oracle(gold-in-rivals) = 1.000 -> gold is ALWAYS among the rivals, so 0.4337 is far
    from a hard ceiling; headroom exists IF a correlating feature existed. So "any added feature must hurt" is false;
    the null is about the feature, not saturation.
  CHECK 5  OJA OVER-DECAY -- THE "ACTIVELY HURTS" MAGNITUDE IS AN OJA ARTIFACT (decisive nuance):
    Re-ran CONTRAST with oja_eta=0 vs 0.002 across ALL 3 seeds: FROZEN=0.4337 every seed; CONTRAST(Oja)=0.4070/0.3394/
    0.3750 (d=-0.027/-0.094/-0.059, reproduces metrics per-seed EXACTLY); CONTRAST(noOja)=0.4337/0.4337/0.4337
    (d=+0.0000/+0.0000/+0.0000). Removing Oja returns EVERY seed to EXACTLY frozen. => the below-frozen "harm" and the
    DECREASING P3 curve are an Oja homeostatic-decay training-dynamics artifact (Oja shrinks ||w|| 20.6->3.7 at seed 7,
    crushing the discriminative structural cues relative to the repeatedly-re-boosted useless f_pred). The TRUE signal
    effect is a CLEAN NULL: best case (Oja off) == frozen, never positive. The null is ROBUST; the "hurts" is not.

IS THE HARD_FAIL REAL OR A TEST-DESIGN ARTIFACT: the NULL is REAL (loop provides no self-supervised gain), confirmed by
  TWO independent measurements (Check 1 target-uncorrelated at source + Check 5 noOja==frozen all seeds). It is NOT a
  harness bug (arms differ; codebook fair 0.895; update direction correct; frozen not saturated). The specific "actively
  hurts / decreasing curve" is a PARTIAL test-design artifact (Oja over-decay), corrected here to CLEAN NULL. The
  conclusion does NOT require a re-run: the Oja-off fix was RUN (still null) and the target is uncorrelated at the
  source; a re-run with the same target cannot change a corr~0 target. FRAMING CORRECTIONS banked (both directions,
  symmetric): (down) the cell over-states "loop actively hurts"; (up) the negative is CLEANER than reported (a pure null
  after the Oja artifact is removed) and the codebook/update/rival machinery are all FAIR -- a well-controlled cell.

STRATEGIC CALL (measured vs inductive, kept distinct per caveat-interpretation discipline):
  PROVEN (this cell + forensics): entity-recurrence continuation is a NON-TARGET for per-instance patient-correctness on
  this McGuffey corpus (corr ~0, directly measured). BAD-TARGET, not no-target-possible.
  STRATEGIC PRIOR (6-signal induction + brain-check, NOT a universal proven bound): this is the 6th text-internal self-
  supervised signal to fail at the SAME per-instance patient-selection residual (cosine/distributional-similarity,
  animacy, coref, scene-coherence, thematic-fit, entity-recurrence). Convergent with the arc's per-instance-STRUCTURAL
  residual (LCCP locative HF; CCL topical HF). The loop MACHINERY is fine and demonstrably WORKS elsewhere on the same
  substrate (codebook CG = representation learning; metacog-abstain CG = self-monitoring). => the loop is NOT DEAD, it is
  MIS-POINTED: the reader's patient-selection residual has no text-INTERNAL self-supervised signal. oracle=1.000 (rivals
  contain gold) means the task is selectable-IN-PRINCIPLE, so the missing ingredient is a signal that actually TRACKS
  correctness -> WEAK-SUPERVISION or a GROUNDED signal, NOT another self-supervised text signal. Confidence: entity-
  recurrence non-target = HIGH (measured); text-internal-self-supervision-class-closed = MODERATE-HIGH strategic prior
  (cannot prove no-target-exists from a finite set of tried targets).
  BRAIN-CHECK: patienthood = affectedness/change-of-state, grounded in event perception + causal force-dynamics (Talmy)
  and acquired via syntactic bootstrapping that REQUIRES the observed scene (Gleitman; Gillette/Gleitman Human
  Simulation Paradigm shows text-ALONE is insufficient to recover verb argument structure). The brain does NOT self-
  supervise per-instance patienthood from text-internal coherence/recurrence; it uses grounding + correction. So our
  failure is BRAIN-CONSISTENT (a real bound, not our deficiency), and the fix is grounded/weak-supervised (brain-
  faithful), not another self-supervised text signal.

CROSS-ARC OVERLAP: substrate_query on the mechanism -> top hit cosine 0.3604 is a generic identity-drive research note,
  NOT any prior experiment cell rediscovering this. Direct parents (cpcl_v1 null, codebook CG) are explicitly cited by
  the cell. Genuine targeted extension. NONE at experiment-cell level > 0.30.

TIER: HARD_FAIL / honest-negative (proven-bound). CERT delta +1 (a forensically-hardened proven negative that (a)
  MEASURES the entity-recurrence target as uncorrelated with patient-correctness, (b) corrects the "actively hurts" to a
  clean null via the Oja control, (c) confirms all other components FAIR, and (d) redirects the missing-learning-loop
  program to grounded/weak-supervision for patient-selection while keeping the loop for representation + self-
  monitoring). LOCAL ONLY; needs orchestrator store sync; no origin push; no remote persist.
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
ATOMIZED_BY = ("skunkworks_forensic_component_audit_cpcl_v2_entity_recurrence_target_UNCORRELATED_with_patient_"
               "correctness_measured_corr_near_zero_null_is_REAL_but_actively_hurts_is_an_OJA_over_decay_artifact_"
               "noOja_recovers_to_exactly_frozen_all_3_seeds_codebook_bipolar_AUC_0p895_FAIR_update_direction_correct_"
               "frozen_not_saturated_bad_target_not_no_target_possible_loop_misPOINTED_not_dead_fix_is_grounded_weak_"
               "supervision_brain_consistent_2026-07-19")
ATOMIZED_DATE = "2026-07-19"
ANCHOR = "contrastive_entity_recurrence_reader_loop_cpcl_v2"
CELL_COMMIT = "unknown_local_uncommitted_at_write_see_metrics_ts_2026-07-20T03:08:39Z"

V1_PARENT = ("math::LANDED_VET_contrastive_predictive_reader_loop_cpcl_v1_HONEST_NULL_CONFIRMED_but_DIAGNOSIS_CORRECTED_"
             "NOT_corpus_coarseness_DEEPER_OPERATIONALIZATION_NULL")  # ... _reproduces_byte_level
CODEBOOK_PARENT = ("math::CG_learned_codebook_generalization_gate_v1_LEARNED_DISTRIBUTIONAL_CONTENT_CODES_RI_PPMI_SVD_"
                   "from_text8_8M_GENERALIZE_to_HELDOUT_human_relatedness_ppmi_svd_AUC_0p927")  # ... _LOCAL_ONLY
LCCP_LOC_PARENT = "math::HF_lccp_locative_path_preposition_CLASS_patient_exclusion_feature_NO_ROOM_front_end (per-instance structural residual, 2026-07-19)"
METACOG_PARENT = "math::CG_metacog_abstain_readout_signal_thresholding_v1 (loop WORKS for self-monitoring)"

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

XARC = (
    "substrate_query 'entity recurrence persistence continuation self-supervised contrastive signal patient selection "
    "argument extraction reader loop' -> top hit cosine 0.3604 is a generic identity-drive research-drill NOTE "
    "(notes/research_drill_motivation_boundary_probe_2x), NOT any prior EXPERIMENT cell rediscovering this mechanism. "
    "NONE at experiment-cell level > 0.30. The two direct parents -- cpcl_v1 null (the memorization/at-chance result "
    "this cell fixes 4 root causes of) and the STEP-1 codebook CG (the learned similarity codes this cell consumes) -- "
    "are explicitly cited + credited by the cell and both independently confirmed off-disk here (v1's at-chance rival "
    "correctness reproduced in spirit by corr~0; codebook 0.927 continuous AUC reproduced at 0.9264). Genuine targeted "
    "extension, not a hidden rediscovery. Auditor accepts."
)

ATOM_ID = (
    "math::HF_FORENSIC_cpcl_v2_entity_recurrence_reader_loop_component_audit_HONEST_NEGATIVE_the_ENTITY_RECURRENCE_"
    "continuation_TARGET_is_UNCORRELATED_with_per_instance_PATIENT_CORRECTNESS_measured_offdisk_corr_err_correct_"
    "plus0p011_all_225_neg0p045_have_cont_corr_fpred_correct_mirror_pm0p04_NEAR_ZERO_mean_err_correct_0p2472_vs_wrong_"
    "0p2448_gap_neg0p0025_min_err_selects_gold_5of19_0p263_BELOW_chance_0p386_LOCATIVE_confound_DIRECTLY_MEASURED_"
    "overextracted_nopat_oblique_locative_err_0p2512_approx_correct_patient_0p2472_diff_plus0p0039_recurrence_CANNOT_"
    "separate_contacted_theme_from_recurring_locative_TARGET_is_wrong_signal_BAD_TARGET_not_no_target_possible_CHECK2_"
    "CODEBOOK_SURVIVES_bipolar_SimHash_AUC_0p8952_vs_continuous_ppmi_svd_0p9264_reproduces_STEP1_CG_0p927_retains_92p7pct_"
    "above_chance_codes_FAIR_not_degraded_CHECK3_UPDATE_DIRECTION_CORRECT_104of104_contrast_pairs_pos_fpred_gt_neg_loop_"
    "upweights_fpred_coef_0p734_to_1p168_no_sign_bug_CHECK4_FROZEN_0p4337_NOT_at_ceiling_oracle_gold_in_rivals_1p000_"
    "headroom_exists_drop_informative_CHECK5_OJA_OVER_DECAY_ARTIFACT_the_actively_hurts_neg0p060_and_DECREASING_P3_curve_"
    "are_an_Oja_homeostatic_decay_training_dynamics_artifact_noOja_recovers_CONTRAST_to_EXACTLY_FROZEN_0p4337_ALL_3_"
    "seeds_delta_plus0p0000_Oja_on_gives_0p4070_0p3394_0p3750_reproduces_metrics_exactly_TRUE_signal_effect_is_CLEAN_"
    "NULL_best_case_equals_frozen_never_positive_null_ROBUST_hurts_is_NOT_HARD_FAIL_is_REAL_NULL_confirmed_by_TWO_indep_"
    "measurements_target_uncorrelated_plus_noOja_eq_frozen_NOT_a_harness_bug_arms_differ_codebook_fair_update_correct_"
    "frozen_not_saturated_coverage_0p826_gt_0p60_shuffle_guard_holds_SHUFFLED_eq_FROZEN_MIDDLE_P2_is_a_band_quirk_not_"
    "leakage_p_shuffled_gt_p_contrast_only_because_contrast_fell_below_frozen_via_Oja_STRATEGIC_6th_text_internal_self_"
    "supervised_signal_to_fail_same_per_instance_patient_residual_cosine_animacy_coref_scene_coherence_thematic_fit_"
    "entity_recurrence_loop_MACHINERY_works_elsewhere_codebook_CG_representation_metacog_CG_self_monitoring_loop_NOT_"
    "dead_MIS_POINTED_patient_selection_residual_has_NO_text_internal_self_supervised_signal_oracle_1p000_selectable_in_"
    "principle_missing_ingredient_is_signal_that_TRACKS_correctness_WEAK_SUPERVISION_or_GROUNDED_not_another_self_"
    "supervised_text_signal_BRAIN_patienthood_is_affectedness_change_of_state_grounded_event_perception_Talmy_force_"
    "dynamics_syntactic_bootstrapping_needs_observed_scene_Gleitman_Human_Simulation_text_alone_insufficient_failure_"
    "BRAIN_CONSISTENT_fix_grounded_weak_supervised_brain_faithful_confidence_entity_recurrence_nontarget_HIGH_measured_"
    "class_closed_MODERATE_HIGH_strategic_prior_cannot_prove_no_target_from_finite_tried_targets_LOCAL_ONLY_2026-07-19"
)

ATOM_CLAIM = (
    "MATH HARD_FAIL / honest-negative (forensically-hardened). USER-directed DEEP FORENSIC COMPONENT-AUDIT of CPCL-v2 "
    "(was the test FAIR, each component USED correctly, did each DO its job, WHERE did it go wrong) BEFORE the strategic "
    "signal-absence call, because a silently-degraded component or a bad target produces the SAME null and would fake a "
    "'self-supervised learning is bounded' conclusion. 5 checks measured OFF-DISK reusing the cell's own functions at "
    "full config. HEADLINE: the HARD_FAIL is a REAL NULL (the entity-recurrence self-supervised loop adds no gain to "
    "patient-selection), robustly confirmed by TWO independent measurements -- NOT a harness bug -- BUT the cell's "
    "'loop ACTIVELY HURTS -0.060 / P3 DECREASING' narrative is an OJA OVER-DECAY test-design ARTIFACT, corrected here to "
    "a CLEAN NULL. COMPONENT-BY-COMPONENT: "
    "(1) TARGET FAIRNESS = THE FLAW (but a genuine measured finding, not a silent break): the entity-recurrence "
    "continuation target is UNCORRELATED with per-instance patient-correctness -- corr(err,correct)=+0.011 over all 225 "
    "eval candidates / -0.045 over the 204 with a real continuation, corr(f_pred,correct) mirror +-0.04, mean err "
    "correct 0.2472 vs wrong 0.2448 (gap -0.0025), and selecting the min-err rival picks gold in only 5/19=0.263 of "
    "multi-rival instances vs chance 0.386 (BELOW chance). LOCATIVE CONFOUND now DIRECTLY MEASURED (exp_dev only "
    "asserted it): over-extracted obliques/locatives on nopat verbs have err 0.2512 ~= correct patients 0.2472 -- "
    "recurrence CANNOT separate a contacted theme from a recurring locative. => a proven BAD/wrong TARGET, which "
    "distinguishes 'bad-target' (proven here) from 'no-target-possible' (NOT proven by one cell). "
    "(2) CODEBOOK = FAIR: the continuous ppmi_svd held-out relatedness AUC reproduces at 0.9264 (independently "
    "confirming the STEP-1 codebook CG's 0.927) and the SimHash-BIPOLAR codes the loop ACTUALLY consumed retain AUC "
    "0.8952 = 92.7% of the above-chance signal. Codes not degraded. "
    "(3) UPDATE DIRECTION = CORRECT: 104/104 contrast pairs have pos(low-err) f_pred > neg, the loop up-weights the "
    "recurrence-fit feature as designed (coef 0.734->1.168); no sign error. "
    "(4) FROZEN not at a hard ceiling: 0.4337 vs oracle(gold-always-in-rivals) 1.000 -> headroom exists; the drop is "
    "informative about the feature, not saturation. "
    "(5) OJA = the 'actively hurts' magnitude is an ARTIFACT: re-running CONTRAST with oja_eta=0 recovers precision to "
    "EXACTLY frozen 0.4337 on ALL 3 seeds (delta +0.0000/+0.0000/+0.0000), while Oja-on reproduces the metrics' "
    "-0.027/-0.094/-0.059 exactly. Oja homeostatic decay crushed the discriminative structural cues (||w|| 20.6->3.7) "
    "relative to the re-boosted useless f_pred; the TRUE signal effect is a clean null (best case == frozen, never "
    "positive). IS THE HARD_FAIL REAL OR A TEST-DESIGN ARTIFACT: the NULL is REAL (two independent confirmations: "
    "target uncorrelated at source + noOja==frozen all seeds) and NOT a harness bug; the 'hurts/decreasing' is a "
    "partial Oja artifact corrected to a clean null. No re-run needed to trust the null (the Oja-off fix was run and is "
    "null; a corr~0 target cannot be rescued by re-running the same target). STRATEGIC CALL (measured vs inductive kept "
    "distinct): entity-recurrence is a PROVEN non-target (HIGH confidence, measured); the broader 'text-internal self-"
    "supervision of the reader's patient-selection is closed' is a MODERATE-HIGH strategic PRIOR from the 6-signal "
    "induction (cosine/animacy/coref/scene-coherence/thematic-fit/entity-recurrence all fail the SAME per-instance "
    "residual) + brain-check, NOT a universal proven bound. The loop is NOT DEAD, it is MIS-POINTED: the machinery "
    "works elsewhere on the same substrate (codebook CG = representation; metacog-abstain CG = self-monitoring); the "
    "reader's patient-selection residual simply has no text-INTERNAL self-supervised signal. oracle=1.000 (rivals "
    "contain gold) => selectable in principle => the missing ingredient is a signal that TRACKS correctness = WEAK-"
    "SUPERVISION or GROUNDED, not another self-supervised text signal. BRAIN-CHECK: patienthood is affectedness/change-"
    "of-state, grounded in event perception + force-dynamics (Talmy) and acquired via syntactic bootstrapping that "
    "REQUIRES the observed scene (Gleitman; Human Simulation Paradigm: text-alone is insufficient) -> the brain does "
    "not self-supervise per-instance patienthood from text-internal coherence either, so our failure is BRAIN-"
    "CONSISTENT and the fix is grounded/weak-supervised, which is brain-faithful."
)

ATOM_RECOMPUTE = (
    "INDEP forensic recompute (.venv Scripts/python, OMP/MKL/OPENBLAS=1, off-disk, reusing the cell's OWN functions at "
    "cfg_full; NOT verdict_msg; Fix #28): "
    "VERDICT ARITHMETIC first reproduced from per_fraction_detail: CONTRAST 0.3738 = mean[0.407,0.3394,0.375]; FROZEN "
    "0.4337; per-seed C-F [-0.0267,-0.0943,-0.0587] ALL negative, mean -0.0599; SHUFFLED 0.4337 == FROZEN exactly "
    "(shuffle guard HOLDS; MIDDLE_P2 is a band quirk -- PASS_P2 needs p_shuffled<p_contrast but contrast fell below "
    "frozen so shuffled ends up above it; NOT leakage); real-vs-shuffled rel margin (0.0099-0.0086)/0.0099=0.1313 < "
    "0.20 (contrast_fires=False), smoke 0.2249 -> full 0.1313 (scale dilution). W hashes 4-distinct (arms_differ). "
    "coverage 0.8257 > 0.60 (not a corpus failure). "
    "CHECK1: corr(err,correct)=+0.011 all / -0.045 have-cont; corr(f_pred,correct)=-0.011/+0.045; mean err correct "
    "0.2472 vs wrong 0.2448; min-err picks gold 5/19=0.263 vs chance 0.386; oblique/locative err 0.2512 ~= theme "
    "0.2472 (diff +0.0039). "
    "CHECK2: continuous ppmi_svd AUC 0.9264 (reproduces CG 0.927 off cached codes + wordsim353+simlex999 TRUE=301 "
    "RANDOM=2000); SimHash-bipolar (sign(code@P), P seed404 N1024) AUC 0.8952 (92.7% above-chance retained). "
    "CHECK3: 104/104 pairs pos_fpred>neg_fpred; w[idx6] frozen 0.734 -> contrast 1.168 -> noOja 2.418. "
    "CHECK4: frozen 0.4337 vs oracle 1.000 (headroom). "
    "CHECK5: all-3-seed Oja control: FROZEN=0.4337 each; CONTRAST(Oja)=0.4070/0.3394/0.3750 (reproduces metrics); "
    "CONTRAST(noOja)=0.4337/0.4337/0.4337 (delta +0.0000 each) -> 'actively hurts' is an Oja artifact; true effect = "
    "clean null. ||w|| frozen 20.59 vs Oja-contrast 3.70 vs noOja-contrast 12.73."
)

ATOM_SCOPE = (
    "McGuffey Third Reader argument-structure extraction, slice L04+L05+L07+L08+L09+L10+L12 (163 eval sents, 225 reader "
    "candidates, 44 gold-correct); mining = McGuffey primer/1st/2nd/4th readers (4151 sents, third reader EXCLUDED); "
    "learned text8 ppmi_svd codebook (V=10000, N=1024) SimHash-bipolarized; INDEPENDENT single-annotator caveated gold. "
    "No LLM; deterministic (OMP/MKL/OPENBLAS=1). Load-bearing BOUNDS: "
    "(a) MEASURED/PROVEN: the entity-recurrence continuation target is uncorrelated (corr ~0) with per-instance "
    "patient-correctness on this corpus; it cannot separate a contacted theme from a recurring locative/oblique "
    "(err 0.2512 vs 0.2472). Entity-recurrence is a BAD TARGET for patient-selection. "
    "(b) FRAMING-CORRECTED: the loop provides NO self-supervised gain (a CLEAN NULL == frozen with Oja removed on all 3 "
    "seeds); it does NOT 'actively hurt' -- the below-frozen precision + decreasing P3 curve are an Oja over-decay "
    "training-dynamics artifact of THIS update rule, not a property of the signal. "
    "(c) ALL OTHER COMPONENTS FAIR: codebook survives bipolarization (0.895, 92.7% retained), update direction correct "
    "(up-weights f_pred), frozen not saturated (oracle 1.000). The test was fair; the target was the wrong choice. "
    "(d) STRATEGIC PRIOR (NOT a proven universal bound): 6th text-internal self-supervised signal to fail the SAME "
    "per-instance patient-selection residual -> text-internal self-supervision of the reader's patient-extraction is "
    "very likely closed, but this is inductive (cannot prove no-target-exists from finitely many tried targets), so it "
    "must be treated as a strong PIVOT prior, not a certified bound. "
    "(e) LOOP NOT DEAD, MIS-POINTED: the same predictive/contrastive machinery works for representation (codebook CG) "
    "and self-monitoring (metacog-abstain CG); only the reader's patient-selection residual lacks a text-internal self-"
    "supervised signal. "
    "BRAIN-CHECK (outcome not pre-assumed; the brain FAILS THE SAME WAY -> fix is native/grounded): patienthood = "
    "affectedness/change-of-state, grounded in event perception + causal force-dynamics (Talmy) and acquired via "
    "syntactic bootstrapping that REQUIRES the observed scene (Gleitman 1990; Gillette/Gleitman/Gleitman/Lederer 1999 "
    "Human Simulation Paradigm: from text alone even adults cannot reliably recover verb argument structure). The brain "
    "does NOT self-supervise per-instance patienthood from text-internal coherence/recurrence; it grounds + corrects. "
    "Our failure is BRAIN-CONSISTENT (a real bound, not our deficiency); the fix is grounded/weak-supervised, which IS "
    "the brain's mechanism, not another self-supervised text signal. "
    "REVIVAL: (1) a signal that DEMONSTRABLY correlates with patient-correctness before wiring it -- i.e. WEAK-"
    "SUPERVISION (a few labeled patients / an oracle-scored subset) or a GROUNDED referent (observed event / affected-"
    "entity), verified by measuring corr(signal, correct) > ~0.2 at design-gate BEFORE a full loop run; (2) if any "
    "future self-supervised target is tried, DROP or shrink Oja (oja_eta=0) so a real signal is not masked/inverted by "
    "homeostatic decay, and pre-register the corr(target, correct) design-gate; (3) keep the loop for representation + "
    "self-monitoring where it is already chain-grade."
)

ATOM_METRICS = {
    "slice": ["L04", "L05", "L07", "L08", "L09", "L10", "L12"], "n_eval_cands": 225, "n_gold_correct": 44,
    "n_with_real_continuation": 204, "n_default_err_no_cont": 21, "n_mining_sents": 4151,
    "verdict_arithmetic": {"CONTRAST_P": 0.3738, "FROZEN_P": 0.4337, "ABSOLUTE_P": 0.3322, "SHUFFLED_P": 0.4337,
                           "per_seed_C_minus_F": [-0.0267, -0.0943, -0.0587], "mean_delta": -0.0599,
                           "SHUFFLED_eq_FROZEN_shuffle_guard_holds": True,
                           "MIDDLE_P2_is_band_quirk_not_leakage": True,
                           "rel_gap_margin_full": 0.1313, "rel_gap_margin_smoke": 0.2249, "contrast_fires_full": False,
                           "coverage": 0.8257, "arms_differ_4_distinct_w_hashes": True},
    "check1_target_fairness": {
        "corr_err_correct_all": 0.0106, "corr_err_correct_have_cont": -0.0446,
        "corr_fpred_correct_all": -0.0106, "corr_fpred_correct_have_cont": 0.0446,
        "mean_err_correct": 0.2472, "mean_err_wrong": 0.2448, "gap_wrong_minus_correct": -0.0025,
        "min_err_selects_gold_rate": 0.263, "chance_rate": 0.386, "n_multi_rival_pos_with_gold": 19,
        "err_overextracted_nopat_oblique_locative": 0.2512, "err_correct_patient": 0.2472, "diff": 0.0039,
        "verdict": "TARGET UNCORRELATED with patient-correctness (bad target, measured); locatives recur ~as much as themes CONFIRMED off-disk; min-err selects gold BELOW chance"},
    "check2_codebook_survival": {"continuous_ppmi_svd_AUC": 0.9264, "reproduces_STEP1_CG_0p927": True,
                                 "simhash_bipolar_AUC_loop_consumed": 0.8952, "pct_above_chance_retained": 92.7,
                                 "true_pairs": 301, "random_pairs": 2000, "verdict": "FAIR / not degraded"},
    "check3_update_direction": {"contrast_pairs": 104, "pos_fpred_gt_neg_fpred": 104, "frac": 1.00,
                                "fpred_coef_frozen": 0.734, "fpred_coef_contrast": 1.168, "fpred_coef_noOja": 2.418,
                                "verdict": "CORRECT / up-weights recurrence-fit feature as designed; no sign bug"},
    "check4_frozen_ceiling": {"frozen_P": 0.4337, "oracle_gold_in_rivals": 1.000,
                              "verdict": "NOT at hard ceiling; headroom exists; drop is informative not forced"},
    "check5_oja_over_decay": {
        "per_seed_frozen": [0.4337, 0.4337, 0.4337],
        "per_seed_contrast_oja": [0.4070, 0.3394, 0.3750], "per_seed_contrast_oja_delta": [-0.0267, -0.0943, -0.0587],
        "per_seed_contrast_noOja": [0.4337, 0.4337, 0.4337], "per_seed_contrast_noOja_delta": [0.0, 0.0, 0.0],
        "wnorm_frozen": 20.59, "wnorm_contrast_oja": 3.70, "wnorm_contrast_noOja": 12.73,
        "verdict": "the -0.060 'actively hurts' + decreasing P3 curve are an OJA over-decay ARTIFACT; noOja recovers to EXACTLY frozen on ALL 3 seeds; TRUE effect is a CLEAN NULL (best case == frozen, never positive); null is ROBUST"},
    "hard_fail_real_or_artifact": "NULL is REAL (2 independent confirmations: target uncorrelated + noOja==frozen); NOT a harness bug (arms differ, codebook fair, update correct, frozen not saturated); the 'actively hurts' is a partial Oja test-design artifact, corrected to clean null; no re-run needed",
    "bad_target_vs_no_target_possible": "PROVEN bad-target (entity-recurrence corr~0, measured); no-target-possible NOT proven by one cell -- it is a MODERATE-HIGH strategic prior from the 6-signal induction + brain-check",
    "signals_failed_same_residual": ["cosine/distributional-similarity", "animacy", "coref", "scene-coherence", "thematic-fit", "entity-recurrence"],
    "loop_works_elsewhere": ["codebook CG (representation learning)", "metacog-abstain CG (self-monitoring)"],
    "oracle_meaning": "rivals contain gold (oracle 1.000) -> selectable in principle -> missing ingredient is a signal that TRACKS correctness = weak-supervision or grounded, NOT another self-supervised text signal",
    "cell_verdict": "HARD_FAIL_P1_LOOP_ADDS_NOTHING|MIDDLE_P2_SHUFFLED_PARTIAL|HARD_FAIL_P3_FLAT_OR_DECREASING",
    "auditor_tier": "HARD_FAIL / honest-negative (forensically-hardened; framing-corrected)",
}

COMPOSES = [
    ("EXTENDS + HARDENS cpcl_v1 null (" + V1_PARENT + "...): v1 measured gold-rival correctness at chance (correct err "
     "0.485 ~= wrong 0.476, margin -0.006) and diagnosed 4 root causes (random codes->memorize, bag-of-words target, "
     "in-sample scoring, non-isolated rivals). v2 FIXED all 4 (learned SimHash codes, entity-grid target, held-out "
     "curve, shared-(sid,verb) rivals) and STILL corr(recurrence, correct) ~ 0 -- so the residual is NOT any of v1's 4 "
     "confounds; it is that the entity-recurrence TARGET itself carries no patient-correctness signal. Does NOT "
     "supersede v1; confirms + sharpens it to a measured target-uncorrelation."),
    ("USES + INDEPENDENTLY REPRODUCES the STEP-1 codebook CG (" + CODEBOOK_PARENT + "...): the continuous ppmi_svd "
     "held-out relatedness AUC reproduces at 0.9264 off the cached codes (confirming 0.927), and the SimHash-bipolar "
     "codes the loop consumed retain 0.8952 (92.7% above-chance) -- so the CG's codes were delivered FAIR to the loop. "
     "The codebook CG is CORRECT and its consumption here is clean; this cell adds the measured caveat that a validated "
     "content codebook is NECESSARY-BUT-INSUFFICIENT when the TARGET is uncorrelated with the label."),
    ("CONVERGES with the per-instance STRUCTURAL residual family: LCCP locative HF (" + LCCP_LOC_PARENT + ") + CCL "
     "topical-coherence HF -- all locate the same wall: per-instance patient-selection needs a signal that tracks "
     "affectedness/argument-role, which topical/distributional/recurrence proxies do not carry. This is the 6th "
     "self-supervised signal at that residual; the convergence is what elevates the strategic prior (still inductive)."),
    ("CONTRASTS with the loop's SUCCESSES on the SAME substrate: metacog-abstain CG (" + METACOG_PARENT + ") + codebook "
     "CG -- the predictive/contrastive machinery is chain-grade for self-monitoring + representation. This is the "
     "evidence that the loop is MIS-POINTED (patient-selection has no text-internal signal), NOT dead."),
    ("credit: McGuffey readers (PD); text8 ppmi_svd codebook (Levy-Goldberg 2015; built in STEP-1); wordsim353 + "
     "simlex999 for the AUC survival check; Charikar 2002 (SimHash); Oja 1982 (the homeostatic rule shown here to be "
     "the source of the 'hurts' artifact); Talmy (force dynamics) + Gleitman 1990 + Gillette/Gleitman 1999 (Human "
     "Simulation) for the brain-check. exp_dev CREDITED: a well-controlled cell -- learned codes (fixes v1 "
     "memorization), held-out curve, isolated rivals, shuffle-test guard, oracle guard, coverage gate. The forensic "
     "audit CONFIRMS those components are fair; its contributions are (a) MEASURING the target-uncorrelation exp_dev "
     "only asserted, and (b) attributing the 'actively hurts' to Oja, correcting the framing to a clean null."),
]

OVER_READS = [
    ("FRAMING CORRECTION (down) vs the cell + Director: 'P1 loop ACTIVELY HURTS -0.060 / P3 DECREASING curve' OVERSTATES "
     "the negative. Off-disk Oja control (all 3 seeds): with oja_eta=0, CONTRAST recovers to EXACTLY frozen 0.4337 "
     "(delta +0.0000 every seed). The below-frozen precision and the decreasing curve are an Oja homeostatic-decay "
     "training-dynamics ARTIFACT (Oja crushes the discriminative structural cues relative to the re-boosted useless "
     "f_pred), NOT the entity-recurrence signal being anti-correlated. Correct characterization = CLEAN NULL (adds "
     "nothing), which is the well-controlled shape of the result."),
    ("SYMMETRIC (up) -- do NOT under-credit the cell: the audit finds all NON-target components FAIR (codebook survives "
     "bipolarization 0.895; update direction correct 104/104; frozen not saturated; shuffle guard holds; arms differ). "
     "The negative is CLEANER than reported, and the cell's 4 fixes over v1 are all real. A clean null on a fair test "
     "is a valuable cert, not a failure to minimize."),
    ("DISTINGUISH bad-target from no-target-possible (USER's explicit ask): this cell PROVES entity-recurrence is a "
     "non-target (measured corr~0) -- it does NOT alone prove NO self-supervised target exists. The 'self-supervised "
     "learning of patient-extraction is closed' call is a strong STRATEGIC PRIOR (6-signal induction + brain-check), "
     "NOT a certified universal bound. Atomize as a measured per-signal negative + a strategic synthesis, not as a "
     "proven wall."),
    ("Do NOT over-read as 'the missing-learning-loop program is dead'. The loop is MIS-POINTED, not dead: it is chain-"
     "grade for representation (codebook) and self-monitoring (metacog-abstain). Only the reader's patient-selection "
     "residual lacks a text-internal self-supervised signal; the fix there is grounded/weak-supervision."),
]

REVIVAL = [
    ("DESIGN-GATE any future self-supervised target BEFORE a full loop: measure corr(target_signal, gold "
     "patient-correctness) on a labeled subset and require > ~0.2 (or min-err-selects-gold ABOVE chance) BEFORE wiring "
     "it. This cell's target would have been caught at the gate (corr~0, select 0.263 < chance 0.386) without a "
     "578s full run."),
    ("WEAK-SUPERVISION / GROUNDED signal for patient-selection specifically: since oracle=1.000 (gold is always among "
     "rivals) the task is selectable in principle; supply a signal that tracks correctness -- a few labeled patients, "
     "an oracle-scored subset, or an observed affected-entity referent -- rather than another self-supervised text "
     "proxy. This is the brain-faithful fix (patienthood is grounded)."),
    ("If a self-supervised target IS retried, SET oja_eta=0 (or shrink it) so homeostatic decay cannot mask/invert a "
     "real signal into a spurious 'hurts'; the null here only became a clean null once Oja was removed."),
    ("KEEP the loop where it is already chain-grade: representation (codebook) + self-monitoring (metacog-abstain). The "
     "negative is scoped to the reader's patient-selection residual, not the loop machinery."),
]

GENUINE_POS = (
    "GENUINE CREDIT preserved symmetrically. The forensic audit CONFIRMS the cell is a well-controlled honest negative "
    "on a FAIR test: (1) the learned SimHash codebook the loop consumed is validated-strength (AUC 0.895 bipolar, 92.7% "
    "of the continuous 0.926 above-chance signal reproduced independently) -- v1's memorization confound is genuinely "
    "fixed; (2) the update direction is correct (104/104 pairs, up-weights f_pred as designed); (3) frozen is not "
    "saturated (oracle 1.000); (4) the shuffle-test guard holds (SHUFFLED == FROZEN exactly); (5) arms differ (4 "
    "distinct w-hashes); (6) coverage gate passed (0.826). The auditor's contribution is a SHARPENING + a framing "
    "correction in BOTH directions: (up) the negative is CLEANER than reported -- a pure null once the Oja over-decay "
    "artifact is removed, and the codebook/update/rival machinery are all fair; (down) the 'actively hurts / "
    "decreasing' story is an Oja artifact, not an anti-signal, and the target-uncorrelation exp_dev asserted is now "
    "MEASURED (corr~0; locative err 0.2512 ~= theme 0.2472). What this IS: proof that the entity-recurrence continuation "
    "target carries no per-instance patient-correctness signal on this corpus (a bad target on a fair test), that the "
    "loop provides a clean null (not harm) to patient-selection, and that the loop MACHINERY is sound (chain-grade "
    "elsewhere). What it is NOT: a certified universal bound that NO self-supervised signal can work (that is a strong "
    "strategic pivot prior, inductive), nor a death of the missing-learning-loop program (it is mis-pointed, and the "
    "fix for patient-selection is grounded/weak-supervision -- brain-consistent)."
)

PLAIN_LANGUAGE = (
    "We built a self-teaching loop to help the reader pick the correct object of a verb (its 'patient') by rewarding "
    "guesses whose entities keep showing up in the next sentences (entity recurrence). It failed. We forensically "
    "audited every part before believing it. The codebook of word meanings it used was fine (still strong after being "
    "compressed to +-1 codes). The learning update pushed in the right direction. The starting reader was not already "
    "maxed out. The one broken part was the IDEA ITSELF: we measured directly that 'how much an entity recurs' has "
    "essentially zero correlation with 'is it the correct patient' -- a recurring place-name recurs just as much as a "
    "real object (recurrence error 0.251 for over-picked locatives vs 0.247 for correct patients), and picking by this "
    "signal chooses the right answer LESS often than random. We also caught that the cell's claim the loop 'actively "
    "hurts' was really a side-effect of one stabilizer knob (Oja decay): turn it off and the loop lands exactly on the "
    "no-loop baseline on all three seeds -- so the honest result is 'adds nothing', a clean zero, not 'harmful'. This "
    "is the 6th self-teaching signal to fail at the SAME hard spot (picking the right patient per sentence). The "
    "machinery is not dead -- the same loop already works for learning word codes and for the reader knowing when to "
    "abstain -- it is just aimed at the wrong problem. The brain doesn't learn who-got-acted-on from text patterns "
    "alone either; it learns it by SEEING events and being corrected. So the fix is to give the loop a grounded or "
    "lightly-labeled signal for patient-selection, not yet another text-only self-teaching trick."
)

IMPORTANCE = (
    "HIGH / load-bearing for the whole 'build the missing learning loop' program. This is the session CRUX and the "
    "biggest result (a negative). It (1) forensically PROVES the crux HARD_FAIL is a real null, not a silent component "
    "bug -- which is exactly the trap USER flagged (a degraded part faking a 'bound'); (2) DECISIVELY narrows the "
    "strategy: text-internal self-supervision of the reader's patient-selection is the wrong tool (6th failed signal + "
    "brain-consistent), redirecting effort to grounded/weak-supervision for THAT residual while preserving the loop "
    "for representation + self-monitoring; (3) supplies a reusable DESIGN-GATE (measure corr(target,correct) before a "
    "full loop run) and an OJA caveat that will prevent future cells from mis-reading a null as harm; (4) keeps the "
    "honesty ledger straight by correcting an over-stated negative DOWN (not harm, just null) and an under-credited "
    "cell UP (fair components). Directly steers the next dispatch away from a 7th doomed self-supervised signal."
)


def build_atom():
    return {
        "id": ATOM_ID, "name": ATOM_CLAIM, "corpus": "math", "tier": "HARD_FAIL",
        "kind": "experiment_landed_vet_forensic_component_audit",
        "cert_status": "honest_negative_forensically_hardened",
        "cert_class": ("honest_negative_entity_recurrence_continuation_target_UNCORRELATED_with_per_instance_patient_"
                       "correctness_measured_corr_near_zero_locatives_recur_as_much_as_themes_min_err_selects_gold_"
                       "below_chance_BAD_TARGET_not_no_target_possible_codebook_survives_bipolarization_AUC_0p895_FAIR_"
                       "update_direction_correct_frozen_not_saturated_the_actively_hurts_neg0p060_is_an_OJA_over_decay_"
                       "artifact_noOja_recovers_to_exactly_frozen_all_3_seeds_true_effect_clean_null_HARD_FAIL_is_REAL_"
                       "NULL_not_harness_bug_6th_text_internal_self_supervised_signal_at_same_patient_selection_residual_"
                       "loop_MIS_POINTED_not_dead_works_for_representation_and_self_monitoring_fix_is_grounded_weak_"
                       "supervision_brain_consistent"),
        "description": (ATOM_CLAIM + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + ATOM_RECOMPUTE
                        + "\n\nHONEST SCOPE: " + ATOM_SCOPE),
        "aliases": [
            "CPCL-v2 forensic component-audit HARD_FAIL (entity-recurrence target uncorrelated with patient-correctness)",
            "entity-recurrence is a BAD TARGET for patient-selection: corr~0, locatives recur as much as themes (measured)",
            "the 'actively hurts -0.060' is an OJA over-decay artifact; noOja recovers to exactly frozen all 3 seeds (clean null)",
            "codebook survives SimHash bipolarization (AUC 0.895, 92.7% retained); update direction correct; frozen not saturated -- test was FAIR",
            "6th text-internal self-supervised signal to fail the reader's patient-selection residual; loop MIS-POINTED not dead; fix = grounded/weak-supervision",
            "bad-target proven vs no-target-possible (strategic prior only); brain-check: patienthood is grounded not self-supervised-from-text",
        ],
        "ts_iso": _iso, "ts": _ts,
        "metadata": {
            "provenance_quality": ("independent_venv_offdisk_forensic_recompute_reusing_cell_functions_at_full_config_"
                                   "5_checks_measured_target_correlation_codebook_AUC_survival_update_direction_sign_"
                                   "frozen_ceiling_oja_all_3_seed_control_plus_verdict_arithmetic_reproduced_from_per_"
                                   "fraction_detail"),
            "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes": None,
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_contrastive_entity_recurrence_reader_loop_cpcl_v2/metrics.json",
            "forensic_script": "tools/_skunkworks_atomize_2026_07_19_cpcl_v2_FORENSIC... (recompute logic; ran via scratchpad forensic_cpcl_v2.py)",
            "verified_off_data": ATOM_RECOMPUTE, "honest_scope": ATOM_SCOPE, "metrics": ATOM_METRICS,
            "plain_language": PLAIN_LANGUAGE, "importance": IMPORTANCE,
            "over_reads_corrected": OVER_READS,
            "genuine_positives_symmetric_anti_negativity": GENUINE_POS,
            "revival_criteria": REVIVAL,
            "cross_arc_overlap_check": XARC,
            "hard_fail_real_not_test_design_artifact": (
                "REAL NULL confirmed by TWO independent measurements (target uncorrelated at source; noOja==frozen all "
                "3 seeds); NOT a harness bug (arms differ, codebook fair 0.895, update direction correct, frozen not "
                "saturated). The cell's 'actively hurts -0.060 / decreasing P3' is a PARTIAL test-design artifact (Oja "
                "over-decay), corrected to a clean null. No re-run needed: the Oja-off fix was run (still null) and a "
                "corr~0 target cannot be rescued by re-running the same target."),
            "component_verdicts": {
                "target_entity_recurrence": "FLAW = THE FINDING (uncorrelated with correctness, measured; bad target, not a silent break)",
                "codebook_simhash_bipolar": "FAIR (AUC 0.895, 92.7% above-chance retained)",
                "update_direction": "CORRECT (104/104 pos>neg; up-weights f_pred; no sign bug)",
                "frozen_baseline": "NOT saturated (oracle 1.000; headroom exists)",
                "oja_homeostasis": "OVER-DECAY ARTIFACT source of the 'hurts'; noOja recovers to exactly frozen all seeds",
                "shuffle_guard": "HOLDS (SHUFFLED==FROZEN; MIDDLE_P2 is a band quirk, not leakage)",
            },
            "strategic_call": (
                "PROVEN (measured, HIGH conf): entity-recurrence is a non-target for patient-correctness. STRATEGIC "
                "PRIOR (inductive, MODERATE-HIGH): text-internal self-supervision of the reader's patient-selection is "
                "very likely closed (6th signal + brain-consistent) -> PIVOT to grounded/weak-supervision for that "
                "residual; keep the loop for representation + self-monitoring (chain-grade). The loop is MIS-POINTED, "
                "not dead. oracle=1.000 => selectable in principle => need a signal that TRACKS correctness."),
            "brain_check": (
                "patienthood = affectedness/change-of-state, grounded in event perception + force-dynamics (Talmy) and "
                "acquired via syntactic bootstrapping that requires the observed scene (Gleitman 1990; Gillette/"
                "Gleitman 1999 Human Simulation Paradigm -- text-alone insufficient). Brain does NOT self-supervise "
                "per-instance patienthood from text; it grounds + corrects. Failure is BRAIN-CONSISTENT; fix is "
                "grounded/weak-supervised (brain-faithful), not another self-supervised text signal."),
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "vet_a_negative_confirm_real_not_harness_bug_or_too_weak_implementation",
                "positive_control_clears_own_floor_before_trusting_a_negative",
                "USER_deep_forensic_component_audit_fair_test_each_component_used_correctly_before_strategic_call_2026-07-19",
                "distinguish_bad_target_chosen_from_no_target_possible_silent_degradation_fakes_same_null_USER",
                "every_negative_check_how_the_brain_does_it_proactively_USER",
                "dont_assume_brain_check_outcome_brain_may_fail_same_way_then_fix_is_native",
                "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
                "vet_every_base_ingredient_fair_correct_brain_faithful_USER",
                "substrate_kb_concept_overlap_check_on_schema_vet",
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
        "supersedes_atom_id": None, "amends_atom_id": None,
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True,
        "auditor": "hdi_skunkworks", "auditor_tier": "HARD_FAIL / honest-negative (forensically-hardened)",
        "atomized_by": ATOMIZED_BY, "live_reader": "LCCP reader run on eval slice + cached mining reader",
        "verdict": ("HARD_FAIL_forensic_component_audit_entity_recurrence_TARGET_UNCORRELATED_with_patient_correctness_"
                    "corr_near_zero_measured_bad_target_not_no_target_possible_codebook_bipolar_AUC_0p895_FAIR_update_"
                    "direction_correct_frozen_not_saturated_actively_hurts_neg0p060_is_OJA_over_decay_artifact_noOja_"
                    "recovers_exactly_frozen_all_3_seeds_TRUE_effect_CLEAN_NULL_hard_fail_is_REAL_null_not_harness_bug_"
                    "6th_self_supervised_signal_at_patient_selection_residual_loop_MIS_POINTED_not_dead_fix_grounded_"
                    "weak_supervision_brain_consistent"),
        "cell_verdict": "HARD_FAIL_P1_LOOP_ADDS_NOTHING|MIDDLE_P2_SHUFFLED_PARTIAL|HARD_FAIL_P3_FLAT_OR_DECREASING",
        "cert_class": atom["cert_class"], "cert_increment_delta": 1,
        "brain_check": ("patienthood grounded (affectedness/force-dynamics/observed-scene; Talmy, Gleitman, Human "
                        "Simulation) -> brain does not self-supervise per-instance patienthood from text; failure "
                        "BRAIN-CONSISTENT; fix grounded/weak-supervised."),
        "decisive_numbers": {"corr_err_correct": 0.011, "corr_have_cont": -0.045, "min_err_picks_gold": 0.263,
                             "chance": 0.386, "oblique_err": 0.2512, "theme_err": 0.2472,
                             "codebook_bipolar_AUC": 0.8952, "codebook_continuous_AUC": 0.9264,
                             "noOja_delta_all_seeds": [0.0, 0.0, 0.0], "oja_delta_all_seeds": [-0.0267, -0.0943, -0.0587]},
        "fairness_guards": "codebook survival + update-direction sign + frozen-ceiling + Oja all-seed control + verdict arithmetic + cross-arc overlap",
        "cross_arc_overlap_check": XARC,
        "decision": (
            "HARD_FAIL / honest-negative (forensically-hardened). USER-directed deep forensic component-audit BEFORE "
            "the strategic call. 5 checks measured off-disk (.venv, reusing the cell's own functions at full config; "
            "Fix #28). RESULT: the NULL (loop adds no self-supervised gain to patient-selection) is REAL -- confirmed "
            "independently by (1) CHECK-1 the entity-recurrence TARGET is uncorrelated with patient-correctness "
            "(corr(err,correct)=+0.011/-0.045, min-err selects gold 0.263 < chance 0.386, oblique/locative err 0.2512 "
            "~= theme 0.2472 -- locatives recur as much as themes, MEASURED not asserted) and (2) CHECK-5 removing Oja "
            "recovers CONTRAST to EXACTLY frozen on ALL 3 seeds (delta +0.0000). The other components are FAIR: CHECK-2 "
            "the SimHash-bipolar codes retain AUC 0.895 (92.7% of the continuous 0.926 above-chance, which itself "
            "reproduces the STEP-1 codebook CG 0.927); CHECK-3 update direction correct (104/104 pos>neg, up-weights "
            "f_pred); CHECK-4 frozen 0.4337 not saturated (oracle 1.000). FRAMING CORRECTION: the cell's 'loop ACTIVELY "
            "HURTS -0.060 / P3 DECREASING' is an Oja over-decay ARTIFACT; true effect is a CLEAN NULL. Is-it-real-or-"
            "artifact: the null is real (not a harness bug); the 'hurts' is a partial test-design artifact, corrected. "
            "No re-run needed (Oja-off fix run, still null; corr~0 target can't be rescued by re-running same target). "
            "STRATEGIC CALL: entity-recurrence is a PROVEN non-target (bad-target, HIGH conf); 'self-supervised "
            "learning of patient-extraction is closed' is a MODERATE-HIGH strategic prior (6th signal + brain-check), "
            "not a certified universal bound. The loop is MIS-POINTED not dead (chain-grade for representation + self-"
            "monitoring); the fix for patient-selection is grounded/weak-supervision (brain-consistent). Counts toward "
            "CERT as a forensically-hardened proven negative. Local-only; needs orchestrator store sync."),
        "framing_correction_vs_director": (
            "Director framed CPCL-v2 as the session CRUX HARD_FAIL and asked to confirm real+honest + adjudicate "
            "whether patient-selection is self-supervised-learnable at all. USER then reprioritized to a DEEP FORENSIC "
            "COMPONENT-AUDIT first (a silently-degraded component fakes the same null). RESULT: HARD_FAIL is a REAL "
            "NULL, with two corrections. (A) The 'loop ACTIVELY HURTS -0.060 / DECREASING curve' is an OJA OVER-DECAY "
            "ARTIFACT -- with oja_eta=0 CONTRAST lands on EXACTLY frozen on all 3 seeds (delta +0.0000); the honest "
            "characterization is a CLEAN NULL (adds nothing), not active harm. (B) exp_dev's mechanism read ('locatives "
            "recur as much as themes; recurrence doesn't isolate patient-correctness') is CONFIRMED and now DIRECTLY "
            "MEASURED (corr~0; oblique err 0.2512 ~= theme 0.2472; min-err selects gold BELOW chance) -- exp_dev only "
            "asserted it. (C) All other components FAIR (codebook 0.895, update direction correct, frozen not "
            "saturated) -- the test was FAIR; the TARGET was the wrong choice. (D) SCOPE GUARD on the strategic call: "
            "this PROVES entity-recurrence is a bad target; it does NOT alone prove no self-supervised target exists. "
            "'Patient-selection self-supervision is closed' is a MODERATE-HIGH strategic PRIOR from the 6-signal "
            "induction + brain-check, not a certified bound. The loop is MIS-POINTED, not dead (works for "
            "representation + self-monitoring); the fix is grounded/weak-supervision. Genuine credit preserved: a "
            "well-controlled cell on a fair test; the negative is CLEANER than reported."),
        "net_cert_delta": ("+1 forensically-hardened proven-negative: the entity-recurrence continuation target is "
                           "measured-uncorrelated with per-instance patient-correctness (bad target on a FAIR test -- "
                           "codebook/update/frozen all verified fair); the loop provides a CLEAN NULL to patient-"
                           "selection (the 'actively hurts' being an Oja over-decay artifact, noOja==frozen all seeds); "
                           "6th text-internal self-supervised signal at that residual; loop MIS-POINTED not dead; "
                           "redirect patient-selection to grounded/weak-supervision (brain-consistent), keep loop for "
                           "representation + self-monitoring."),
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
    print("=== A5 atom-write: CPCL-v2 FORENSIC component-audit -> HARD_FAIL / honest-negative (2026-07-19) ===")
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
    print("ATOM:", atom["id"][:120], "...")


if __name__ == "__main__":
    main()
