"""
A5-gated atomization (2026-07-19): SECOND-WITNESS VET on exp_dev's DESIGN-GATE ABORT of the locative/path
preposition-class patient-exclusion feature over the LCCP stacked reader. NO cell shipped (cheap triage, scratch
removed) -> the auditor INDEPENDENTLY reproduced every load-bearing number off the LIVE reader (the LCCP cell
exp_lccp_fullnopat_syntactic_frame_teacher_stack_v1 --full at seed 7 + gold_mcguffey_lccp_argstruct_v1.json),
NOT from any summary. ONE atom: HARD_FAIL / honest-negative = the last cheap STRUCTURAL FRONT-END lever (a
locative/path preposition-CLASS patient-exclusion rule) has NO ROOM; the reading-axis front-end is exhausted.

INDEPENDENT RECOMPUTE (off live reader, .venv Scripts/python, Fix #28; NOT a summary):
  - BASELINE reproduced EXACTLY at seed 7: Q_base precision 0.5574 (tp=34 / n_pred=61), recall 0.3400, total_fp=27,
    FP-split subcat=18 / within=5 / spurious=4. (Full-cell also re-ran clean; seed-7 positive-control = published 0.5574.)
  - PARTITION of the 27 residual FPs reproduced by dumping every FP's tokenized sentence + verb/patient positions +
    prev1/prev2/prev3 + f_prep@window2/@window3 off the live LCCP feature extractor:
      (a) locative/path PP-adjunct, preposition-CLASS addressable = 2: lay/dam "near a beaver dam" (near @ ip-3),
          walk/gravel "along the neat gravel" (along @ ip-3). BOTH prepositions (near, along) ALREADY in LCCP PREPS;
          BOTH are ip-3 window-MISSES (f_prep@2=0, f_prep@3=1) -> the existing 2-token f_prep lookback already covers
          the 2-token cases; these 2 need a 3-token window.
      (b) material/instrument/comitative homonymy, held-OUT = 2: sit/son "with his little son" (with @ ip-3),
          build/stream "of a running stream" (of @ ip-3). Prepositions with/of are homonymous (comitative/partitive)
          and appear in genuine-patient contexts -> not cleanly class-widenable.
      (c) OUT-OF-SCOPE, no surface prep in a 3-token window (f_prep@3=0) = 23 = 85.2% of the 27. CONFIRMED counts 2/2/23.
  - DECISIVE window-3 CEILING test (re-derived off-code over the live kept set): widening the f_prep lookback 2->3
    suppresses exactly 4 FPs BUT ALSO loses exactly 4 TRUE patients -- rub/castle "against his mimic castle" (against),
    obey/parents "to obey his parents" (infinitival to), choose/places "in choosing your/their places" x2 (in) -- all
    STRUCTURAL TWINS of the FPs (same [PREP][det/mod][N] surface at ip-3). Net: P 0.5574 -> 0.5660 (+0.0086, BELOW the
    +0.02 material bar); R 0.34 -> 0.30. The 4-FP / 4-TP trade is the load-bearing point.
  - ADVERSARIAL BREAK attempts (try to keep the 4 FPs while retaining the 4 TPs -> FAILED to break the no-room call):
      * A cheap syntactic cue that separates the twins does NOT exist at the surface: lay/dam "near a beaver dam"
        (adjunct location) and rub/castle "against his mimic castle" (contacted theme) are byte-structurally identical
        (PREP + det/poss + modifier + N at ip-3). Separation requires knowing dam=place-adjunct vs castle=object-
        contacted = noun PLACE-vs-ARTIFACT ontology / verb-specific PP argument-vs-adjunct subcat. walk/gravel "along
        the neat gravel" (FP) vs choose/places "in choosing your places" (TP): "in" governs the gerund "choosing", not
        "places" -> needs PP-attachment / nested parse, not a window cue.
      * The "needs noun place-vs-artifact ontology" fix lands in ALREADY-CLOSED thematic-fit territory: atom 29361
        (graded_thematic_fit_integrated_reader_gate HARD_FAIL -- class-typicality DEMOTES genuine low-typicality
        patients, dense cue 2-hurt/0-help) and atom 29360 (scene_coherence_verifier HARD_FAIL). Confirmed off-disk at
        store lines 29360/29361. NOT a new open lever.
      * LOCATIVE-CLASS-restricted window-3 variants (recomputed off-code): none clears the +0.02 bar and all trade real
        TPs -- locative-only {near,along,against,...} -> P=0.5690 (33/58); locative+in/of/with -> P=0.5741 (31/54).
        [HONEST DISCREPANCY vs exp_dev's cited P=31/56=0.5536 "worse than baseline": I could NOT reproduce that exact
        figure under reasonable class definitions -- my locative reconstructions land 0.5690-0.5741 (marginally BETTER
        than baseline, still below +0.02). IMMATERIAL to the verdict: every window/class variant stays below the +0.02
        material bar AND trades true patients; the no-room conclusion is robust to the exact restricted number.]
  - SPOT-CHECK of the 23 out-of-scope (are any catchable by a cheap NON-prep-class syntactic cue?): the 23 are genuinely
    per-instance STRUCTURAL -- light/report-verb patient mis-extraction (say/show/leave/call: say->come, say->hour,
    show->you, leave->mr, meet->eyes, pass->harm), clause-boundary SUBJECT mis-attach / coref / head-finding
    (come->charles, leave->gardener, say->he, stand->hut locative-inversion), wrong-head into an EMBEDDED verb/gerund
    (build->sentence, wish->gate, commence->houses, meet->plenty), ditransitive wrong-object (show->him). No single
    cheap cue catches these. TWO tiny imperfections found (neither a structural lever): lie/skin "lies next the skin"
    -- "next" (archaic prep = next-to) is MISSING from LCCP PREPS at ip-2, a 1-FP lexical patch technically prep-
    adjacent not out-of-scope; struggle/tide "against the wind and the tide" -- coordination-under-preposition (prep 6
    tokens back), catchable only by conjunction-scope parsing, not a cheap window. Each is worth ~1 FP (~0.016 P) and
    neither reopens the preposition-CLASS lever.

VERDICT: CONFIRMED. The no-room / front-end-structural-levers-exhausted call HOLDS. The specified locative/path
  preposition-class patient-exclusion feature has no room: only 4/27 residual FPs are window/prep-window-addressable at
  all, and widening the f_prep lookback trades 4 true patients for 4 FPs (structural twins), netting +0.0086 << +0.02.
  The dominant residual (23/27 = 85%) is light/report-verb patient-mis-extraction + clause-boundary coref/head-finding
  + wrong-head-into-embedded-verb -- per-instance STRUCTURAL, requiring a deeper parse + coref/carry-context loop, not
  a cheap front-end feature. This EARNS the pivot off cheap front-end levers.

TIER: HARD_FAIL / honest-negative (proven-bound = FRONT-END LEVER CLOSURE). Clean, well-controlled negative; second-
  witness independently reproduces the load-bearing numbers off the live reader. CERT delta +1 (proven negative).

LOCAL ONLY: store_head_at_write=unsynced_needs_orchestrator; NO origin push; NO remote persist; NO git add -A.
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
ATOMIZED_BY = ("skunkworks_second_witness_vet_lccp_locative_path_preposition_class_patient_exclusion_feature_NO_ROOM_"
               "front_end_structural_levers_exhausted_only_4of27_FP_window_addressable_window3_trades_4_true_patients_"
               "for_4_FP_structural_twins_dominant_residual_85pct_light_report_verb_plus_coref_per_instance_structural_"
               "2026-07-19")
ATOMIZED_DATE = "2026-07-19"
ANCHOR = "lccp_locative_prep_class_patient_exclusion_frontend_exhausted_triage_v1"
# Second-witness on a design-gate ABORT: no cell shipped. Evidence = the LIVE LCCP reader re-run + gold.
LIVE_READER = "exp_lccp_fullnopat_syntactic_frame_teacher_stack_v1 (--full, seed 7)"
GOLD = "data/gold_mcguffey_lccp_argstruct_v1.json"

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

XARC = (
    "This is a triage/negative-closure of a cheap FRONT-END lever, not a new mechanism. Concept-overlap check against "
    "the reader arc: the 'needs noun place-vs-artifact ontology / thematic-fit' conclusion lands squarely in ALREADY-"
    "CLOSED territory -- store lines 29360 (scene_coherence_verifier_contrastive_scv_v1 HARD_FAIL) and 29361 "
    "(graded_thematic_fit_integrated_reader_gate_v1 HARD_FAIL: graded thematic-fit / class-typicality is DENSE but "
    "ACTIVELY HURTS the reader, demoting genuine low-typicality patients) -- confirmed off-disk. The frame-teacher "
    "parent (line 29349, lccp_motion_aspectual_syntactic_frame_teacher MM: P_do 2-token f_prep + subcat) is the "
    "existing lookback this triage probes. So this atom is a genuine CLOSURE (no cheap prep-class room left), NOT a "
    "rediscovery: it proves the locative/path preposition-CLASS variant of the front-end lever is exhausted and routes "
    "the residual to the already-flagged deeper-parse + coref/carry-context axis."
)

ATOM_ID = (
    "math::HF_lccp_locative_path_preposition_CLASS_patient_exclusion_feature_NO_ROOM_front_end_structural_levers_"
    "EXHAUSTED_second_witness_independently_reproduced_off_LIVE_reader_seed7_baseline_Q_base_P0p5574_tp34_npred61_"
    "R0p3400_total_fp27_split_subcat18_within5_spurious4_EXACT_of_the_27_residual_FP_only_4_are_window_prep_addressable_"
    "partition_2_locative_path_near_along_ALREADY_in_PREPS_lay_dam_near_a_beaver_dam_walk_gravel_along_the_neat_gravel_"
    "BOTH_ip3_window_misses_fprep_at2_zero_at3_one_plus_2_homonymy_held_out_with_of_sit_son_with_his_little_son_build_"
    "stream_of_a_running_stream_plus_23_out_of_scope_no_surface_prep_in_3_token_window_equals_85pct_DECISIVE_window3_"
    "ceiling_widen_fprep_lookback_2to3_suppresses_exactly_4_FP_but_LOSES_exactly_4_TRUE_patients_rub_castle_against_"
    "obey_parents_infinitival_to_choose_places_in_x2_all_STRUCTURAL_TWINS_same_PREP_det_mod_N_at_ip3_net_P_0p5574_to_"
    "0p5660_plus0p0086_BELOW_plus0p02_bar_R_0p34_to_0p30_locative_class_restricted_variants_recomputed_none_clears_"
    "plus0p02_all_trade_TPs_0p5690_33of58_to_0p5741_31of54_NO_cheap_syntactic_cue_separates_the_twins_dam_place_adjunct_"
    "vs_castle_contacted_theme_byte_structurally_identical_needs_noun_place_vs_artifact_ontology_or_PP_attachment_lands_"
    "in_ALREADY_CLOSED_thematic_fit_territory_atoms_29360_scv_29361_graded_thematic_fit_HARD_FAIL_dominant_residual_"
    "23of27_85pct_light_report_verb_patient_mis_extraction_say_show_leave_call_plus_clause_boundary_coref_head_finding_"
    "come_charles_leave_gardener_stand_hut_locative_inversion_plus_wrong_head_into_embedded_verb_build_sentence_wish_"
    "gate_commence_houses_ALL_per_instance_STRUCTURAL_needs_deeper_parse_and_coref_carry_context_loop_NOT_a_cheap_front_"
    "end_feature_two_tiny_imperfections_lie_skin_next_missing_from_PREPS_1FP_lexical_patch_struggle_tide_coordination_"
    "under_prep_neither_reopens_the_class_lever_FRONT_END_EXHAUSTED_PIVOT_EARNED_second_witness_off_live_reader_Fix28_"
    "OMP1_deterministic_LOCAL_ONLY_2026-07-19"
)

ATOM_CLAIM = (
    "MATH HARD_FAIL / honest-negative (proven-bound = FRONT-END STRUCTURAL LEVER CLOSURE). Second-witness VET on a "
    "design-gate ABORT (no cell shipped; auditor independently reproduced every load-bearing number off the LIVE LCCP "
    "stacked reader at seed 7 + the independent gold, NOT from any summary). CLAIM (the NEGATIVE, confirmed off the "
    "live reader): the specified LOCATIVE/PATH PREPOSITION-CLASS patient-exclusion feature has NO ROOM over the 0.5574 "
    "stacked reader, so the cheap reading-axis STRUCTURAL FRONT-END is exhausted. (1) BASELINE reproduced EXACTLY: "
    "Q_base precision 0.5574 (tp=34/n_pred=61), recall 0.3400, 27 residual FP, split subcat=18/within=5/spurious=4. "
    "(2) Of the 27 residual FPs, only 4 are prep-WINDOW-addressable at all; the partition is 2 locative/path (near, "
    "along -- both ALREADY in LCCP PREPS -- lay/dam 'near a beaver dam', walk/gravel 'along the neat gravel', both ip-3 "
    "window-misses that the existing 2-token f_prep lookback simply doesn't reach) + 2 homonymy held-out (with/of, not "
    "cleanly class-widenable) + 23 out-of-scope with NO surface preposition in a 3-token window = 85.2%. (3) DECISIVE "
    "window-3 ceiling: widening the f_prep lookback 2->3 suppresses exactly 4 FPs but ALSO destroys exactly 4 TRUE "
    "patients -- rub/castle 'against his mimic castle', obey/parents infinitival 'to obey his parents', choose/places "
    "'in choosing your/their places' x2 -- which are STRUCTURAL TWINS of the FPs (identical [PREP][det/mod][N] surface "
    "at ip-3). Net P 0.5574->0.5660 (+0.0086, BELOW the +0.02 material bar); R 0.34->0.30. No cheap syntactic cue "
    "separates the twins: dam (place-adjunct) vs castle (contacted-theme) are byte-structurally identical; the "
    "separation requires noun PLACE-vs-ARTIFACT ontology / verb PP-argument-vs-adjunct subcat -- which lands in "
    "ALREADY-CLOSED thematic-fit territory (atoms 29360 SCV / 29361 graded-thematic-fit, both HARD_FAIL). (4) The "
    "dominant residual (23/27 = 85%) is light/report-verb patient mis-extraction (say/show/leave/call) + clause-"
    "boundary coref/head-finding (come/charles, leave/gardener, stand/hut locative-inversion) + wrong-head into an "
    "embedded verb (build/sentence, wish/gate, commence/houses) -- all PER-INSTANCE STRUCTURAL, needing a deeper parse "
    "+ coref/carry-context loop, NOT a cheap front-end feature. VERDICT: CONFIRMED -- the front-end structural levers "
    "are exhausted; the pivot off cheap front-end features to the deeper-parse + coref/carry-context loop is EARNED. "
    "This is a clean, well-controlled negative independently second-witnessed off the live reader."
)

ATOM_RECOMPUTE = (
    "INDEP recompute (.venv Scripts/python, OFF THE LIVE READER, NOT a summary; Fix #28): "
    "(A) BASELINE seed 7: re-ran " + LIVE_READER + " -> Q_base precision 0.5574, tp=34, n_pred=61, recall 0.3400, "
    "total_fp=27, subcat_fp=18, within_frame_fp=5, spurious_verb_fp=4 (EXACT). Full-cell positive control: seed-7 "
    "Q_base reproduces the published 0.5574. "
    "(B) PARTITION: dumped every one of the 27 FPs with tokenized sentence + verb/patient index + prev1/prev2/prev3 + "
    "f_prep@window2/@window3 from the live LCCP candidate_features extractor. Exactly 4 FPs have a preposition in a "
    "3-token window (f_prep@2=0, f_prep@3=1): 2 locative/path {lay/dam near, walk/gravel along -- near & along both in "
    "PREPS} + 2 homonymy {sit/son with, build/stream of}; the other 23 have NO preposition in a 3-token window "
    "(f_prep@3=0) = 23/27 = 85.2%. Counts 2/2/23 CONFIRMED. "
    "(C) WINDOW-3 CEILING (re-derived off-code, re-scored on the live kept set): win2 P=0.5574 (34/61) -> win3-full "
    "P=0.5660 (30/53), R 0.34->0.30, fp 27->23; suppresses 4 FPs, loses 4 TRUE patients {rub/castle against, "
    "obey/parents to, choose/places in x2}. delta_abs +0.0086 << +0.02. "
    "(D) LOCATIVE-CLASS-restricted variants (off-code): locative-only P=0.5690 (33/58), locative+in/of/with P=0.5741 "
    "(31/54) -- none clears +0.02, all trade TPs. [Could NOT reproduce exp_dev's exact P=31/56=0.5536; immaterial -- "
    "the no-room conclusion is robust to the exact restricted figure.] "
    "(E) TWIN-SEPARATION break attempt: FP lay/dam 'near a beaver dam' and TP rub/castle 'against his mimic castle' are "
    "byte-structurally identical (PREP+det/poss+mod+N at ip-3) -> no cheap syntactic cue separates them; needs noun "
    "place-vs-artifact ontology / PP-attachment -> already-closed thematic-fit (29360/29361, confirmed off-disk). "
    "(F) 23 OUT-OF-SCOPE spot-check: genuinely per-instance structural (light/report-verb mis-extraction + clause-"
    "boundary coref/head-finding + wrong-head into embedded verb). Two tiny imperfections (neither a lever): lie/skin "
    "'next' missing from PREPS (1-FP lexical patch), struggle/tide coordination-under-prep (conjunction-scope)."
)

ATOM_SCOPE = (
    "McGuffey reader argument-structure extraction, slice L04+L05+L07+L08+L09+L10+L12; the LCCP stacked patient-lens "
    "reader (LCCP arm-C semantic teacher -> ARG categorial arg/adjunct cascade -> quotative arm = the 0.5574 reference "
    "reader), at seed 7, vs the INDEPENDENT single-annotator caveated gold (" + GOLD + "). No LLM; deterministic "
    "(OMP/MKL/OPENBLAS=1). Load-bearing BOUNDS: "
    "(a) LEVER CLOSED = the LOCATIVE/PATH PREPOSITION-CLASS patient-exclusion front-end feature. Only 4/27 residual FPs "
    "are prep-window-addressable at all, and the ONLY way to catch them (widen the f_prep lookback 2->3, or a locative-"
    "class-restricted version) trades one true patient per false positive because the FPs and TPs are structural twins "
    "at the surface. The net move (+0.0086) is below the +0.02 material bar; recall drops 0.34->0.30. This is a REAL "
    "bound for the cheap-surface-cue mechanism class. "
    "(b) NOT a NEW lever = the noun PLACE-vs-ARTIFACT ontology / verb PP-argument-vs-adjunct subcat that WOULD separate "
    "the twins is NOT open: it lands in the already-closed thematic-fit territory (atoms 29360 SCV HARD_FAIL, 29361 "
    "graded-thematic-fit HARD_FAIL -- class-typicality is dense but actively hurts the reader). Do NOT re-open it as a "
    "cheap front-end feature. "
    "(c) DOMINANT RESIDUAL (23/27 = 85%) is per-instance STRUCTURAL: light/report-verb patient mis-extraction + clause-"
    "boundary coref/head-finding + wrong-head-into-embedded-verb. This is the load-bearing localization for the "
    "strategic pivot: the reader's remaining front-end walls are NOT surface-cue-addressable; they need a deeper parse "
    "and a coref/carry-context loop. "
    "(d) The 0.5574 precision is a real bound for THIS reader on THIS single-annotator caveated gold, NOT a proven "
    "universal ceiling (part of the residual is gold/extraction noise). "
    "BRAIN-CHECK (outcome not pre-assumed): the 23-FP dominant class (light/report verbs whose patient slot is mis-"
    "extracted + clause-boundary subject/coref) -- does the brain resolve these structurally (construction/frame) or "
    "via discourse/coref+world-knowledge? MIXED, and the split IS the pivot signal. Quotative speech-content ('say X') "
    "and clause-boundary subject mis-attach ('when the hour came, Charles put') are resolved by the brain via CLAUSE "
    "SEGMENTATION + direct-speech construction + tracking that the NP is the subject of the NEXT clause's verb -- "
    "STRUCTURAL/construction (a deeper incremental parser), which the current shallow front-end lacks. Wrong-head into "
    "an embedded verb (wish the gate = open's object) is resolved by verb subcat + attachment -- also structural. BUT "
    "the idiom/light-verb tail (meet->eyes) and the twin-separation (place-vs-artifact) need lexicalized construction "
    "retrieval + world-knowledge/thematic-fit. The brain does NOT resolve any of these with a cheap 1-token surface "
    "cue; it uses a FULL incremental parse integrated with discourse/coref. So the pivot target is CORRECT: a deeper "
    "parser + the coref/carry-context loop (the recon's flagged next-drill), NOT another cheap front-end feature. "
    "REVIVAL: (1) a deeper incremental parser with clause segmentation + PP-attachment + direct-speech construction "
    "(addresses the bulk of the 23); (2) a coref/carry-context loop for the clause-boundary subject/head-finding "
    "residual; (3) independent multi-annotator gold before calling 0.5574 a universal precision bound. Do NOT revive "
    "the locative/path preposition-CLASS feature: it is proven to have no room."
)

ATOM_METRICS = {
    "slice": ["L04", "L05", "L07", "L08", "L09", "L10", "L12"], "eval_seed": 7,
    "live_reader": LIVE_READER, "gold": GOLD,
    "baseline_Q_base": {"precision": 0.5574, "recall": 0.3400, "tp": 34, "n_pred": 61, "total_fp": 27,
                        "subcat_fp": 18, "within_frame_fp": 5, "spurious_verb_fp": 4},
    "baseline_reproduced_exact": True,
    "residual_fp_partition": {"locative_path_prepclass_addressable": 2, "material_instrument_homonymy_heldout": 2,
                              "out_of_scope_no_surface_prep_in_3token_window": 23, "total": 27,
                              "out_of_scope_fraction": 0.852},
    "partition_detail": {
        "a_locative_path": ["L09_18 lay->dam 'near a beaver dam' (near @ip-3, in PREPS)",
                            "L12_06 walk->gravel 'along the neat gravel' (along @ip-3, in PREPS)"],
        "b_homonymy_heldout": ["L04_19 sit->son 'with his little son' (with @ip-3)",
                               "L09_06 build->stream 'of a running stream' (of @ip-3)"],
        "both_locative_preps_already_in_PREPS": True, "all_4_are_ip3_window_misses_fprep_at2_zero_at3_one": True,
    },
    "window3_ceiling_test": {
        "win2_baseline": {"P": 0.5574, "tp": 34, "n_pred": 61, "R": 0.34, "fp": 27},
        "win3_full": {"P": 0.5660, "tp": 30, "n_pred": 53, "R": 0.30, "fp": 23},
        "delta_abs_vs_baseline": 0.0086, "material_bar": 0.02, "clears_bar": False,
        "fps_suppressed": 4, "true_patients_lost": 4,
        "true_patients_lost_detail": ["L04_02 rub->castle 'against his mimic castle' (against @ip-3)",
                                      "L07_25 obey->parents 'to obey his parents' (infinitival to @ip-3)",
                                      "L08_02 choose->places 'in choosing your places' (in @ip-3)",
                                      "L08_08 choose->places 'in choosing their places' (in @ip-3)"],
        "structural_twins_no_cheap_separation": True,
    },
    "locative_class_restricted_variants_recomputed": {
        "locative_only": {"P": 0.5690, "tp": 33, "n_pred": 58}, "locative_plus_in_of_with": {"P": 0.5741, "tp": 31, "n_pred": 54},
        "none_clears_plus0p02": True, "all_trade_true_patients": True,
        "exp_dev_cited_31_of_56_0p5536_NOT_reproduced": "auditor got 0.5690-0.5741 under reasonable class defs; immaterial, all below +0.02",
    },
    "twin_separation_needs": "noun place-vs-artifact ontology / verb PP-argument-vs-adjunct subcat -> already-closed thematic-fit (atoms 29360 SCV, 29361 graded-thematic-fit, both HARD_FAIL)",
    "dominant_residual_localization": ("23/27 = 85% per-instance STRUCTURAL: light/report-verb patient mis-extraction "
                                       "(say/show/leave/call) + clause-boundary coref/head-finding (come/charles, "
                                       "leave/gardener, stand/hut locative-inversion) + wrong-head into embedded verb "
                                       "(build/sentence, wish/gate, commence/houses) + ditransitive wrong-object"),
    "spot_check_23_two_minor_imperfections": {
        "lie_skin_next_missing_from_PREPS": "'lies next the skin' -- 'next' (archaic prep) at ip-2 not in PREPS; 1-FP lexical patch, prep-adjacent not out-of-scope, NOT a structural lever",
        "struggle_tide_coordination_under_prep": "'against the wind and the tide' -- prep 6 tokens back; needs conjunction-scope, not a cheap window",
    },
    "verdict": "CONFIRMED: front-end structural levers EXHAUSTED; locative/path preposition-class patient-exclusion has NO ROOM; pivot to deeper-parse + coref/carry-context earned",
    "second_witness_off_live_reader": True, "cell_shipped": False, "auditor_tier": "HARD_FAIL / honest-negative (front-end lever closure)",
}

COMPOSES = [
    ("COMPOSES with the frame-teacher parent (store line 29349, lccp_motion_aspectual_syntactic_frame_teacher MM): "
     "that atom established the P_do + 2-token f_prep syntactic lookback that is the EXISTING coverage this triage "
     "probes. THIS atom proves the natural cheap EXTENSION (widen to 3, or a locative/path preposition-CLASS variant) "
     "has no room -- it trades true patients 1:1 with FPs (structural twins). Does NOT supersede 29349; CLOSES its "
     "cheap-extension frontier."),
    ("COMPOSES with the thematic-fit closures (store lines 29360 scene_coherence_verifier HARD_FAIL, 29361 graded_"
     "thematic_fit_integrated_reader_gate HARD_FAIL). The ONLY signal that would separate the FP/TP structural twins "
     "(dam=place-adjunct vs castle=contacted-theme) is a noun place-vs-artifact ontology / thematic-fit -- which those "
     "atoms already proved dense-but-harmful / null. So the twin-separation route is NOT an open lever; this atom "
     "confirms the residual routes AWAY from thematic-fit and toward deeper-parse + coref."),
    ("COMPOSES with the CCL within-document loop HARD_FAIL (2026-07-19, HF_compress_and_carry_comprehension_loop_ccl): "
     "together they map the reader's front-end frontier -- surface prep-class cues (THIS atom) AND topical situation-"
     "model cues (CCL) are BOTH exhausted; the live remaining lever is a STRUCTURED deeper parse + coref/carry-context, "
     "consistent across both closures."),
    ("credit: McGuffey reader (PD); the LCCP stacked-reader machinery (exp_dev, prior arc) that this second-witnesses; "
     "GloVe (Pennington 2014) for the LCCP semantic teacher. exp_dev CREDITED for the cheap triage discipline: running "
     "a free preposition-class partition + window-3 ceiling test BEFORE shipping a cell, and aborting at the design "
     "gate when the lever showed no room -- exactly the design-gate discipline (a can't-clear-the-bar cell is worse "
     "than idle). This atom is the auditor's INDEPENDENT second-witness confirming that abort off the live reader."),
]

OVER_READS = [
    ("Do NOT over-read 'front-end levers exhausted' as 'the reader is done' or '0.5574 is a universal ceiling'. It is a "
     "bound for the CHEAP-SURFACE-CUE front-end on THIS single-annotator caveated gold. The reader's remaining walls "
     "are STRUCTURAL/per-instance (deeper parse + coref), which are UNBUILT, not proven-impossible. The pivot is to "
     "BUILD those, not to stop."),
    ("HONEST DISCREPANCY (symmetric anti-negativity): exp_dev's secondary cited figure P=31/56=0.5536 (locative-class-"
     "restricted 'worse than baseline') did NOT reproduce under the auditor's reasonable class definitions -- I got "
     "0.5690-0.5741 (marginally BETTER than the 0.5574 baseline, still below +0.02). The exact restricted number is "
     "class-definition-dependent and immaterial: every window/class variant stays below the +0.02 bar AND trades true "
     "patients, so the no-room verdict is robust. Do NOT cite '0.5536 worse than baseline' as reproduced."),
    ("Two tiny imperfections in exp_dev's 23-out-of-scope bucket (neither a structural lever, neither changes the "
     "verdict): (i) lie/skin 'lies next the skin' -- 'next' (archaic prep=next-to) is a PREPS-list GAP at ip-2, so "
     "it's technically prep-adjacent (a 1-FP lexical patch), not truly out-of-scope; (ii) struggle/tide 'against the "
     "wind and the tide' is coordination-under-a-preposition (prep 6 back), catchable only by conjunction-scope. Each "
     "is ~1 FP (~0.016 P) and neither reopens the preposition-CLASS lever."),
    ("The dominant-residual localization is 'light/report-verb + coref' as the PLURALITY, but the honest full "
     "composition of the 23 is BROADER: it also includes wrong-head-into-embedded-verb (build/sentence, wish/gate, "
     "commence/houses, meet/plenty) and ditransitive wrong-object (show/you, show/him) and quotative-leak (say/come, "
     "say/hour). This is a broadening, not a contradiction -- all are per-instance structural, and the pivot target "
     "(deeper parse + coref loop) is the same."),
]

REVIVAL = [
    ("DEEPER INCREMENTAL PARSER with clause segmentation + PP-attachment + direct-speech construction detection -- "
     "addresses the bulk of the 23 (quotative leaks, clause-boundary subject mis-attach, wrong-head into embedded "
     "verbs). This is the substrate-native structural fix, NOT another cheap surface cue."),
    ("COREF / CARRY-CONTEXT LOOP for the clause-boundary subject / head-finding residual (come->charles, leave->"
     "gardener, stand->hut). The recon's flagged next-drill."),
    ("INDEPENDENT MULTI-ANNOTATOR gold before treating 0.5574 as a universal precision bound. Do NOT revive the "
     "locative/path preposition-CLASS patient-exclusion feature -- it is PROVEN to have no room (4/27 addressable, "
     "structural-twin TP-loss)."),
]

GENUINE_POS = (
    "GENUINE CREDIT preserved symmetrically (a clean negative closure is a valuable cert): this is a well-executed "
    "cheap design-gate triage by exp_dev -- a free preposition-class partition + window-3 ceiling test run BEFORE "
    "committing a cell, correctly aborting when the lever showed no room (a can't-clear-the-bar cell is worse than "
    "idle). The auditor's INDEPENDENT second-witness off the LIVE reader CONFIRMS every load-bearing number exactly "
    "(baseline 0.5574 tp=34/n=61, split 18/5/4, partition 2/2/23=85%, window-3 +0.0086 with 4-FP/4-TP structural-twin "
    "trade). What this IS: proof that the last cheap surface-cue front-end lever (locative/path preposition-CLASS "
    "patient-exclusion) has no room, so the reading-axis front-end is exhausted and the pivot to a deeper parse + "
    "coref/carry-context loop is EARNED. What it is NOT: a claim that the reader is done or that 0.5574 is a universal "
    "ceiling -- the remaining walls are structural/per-instance and UNBUILT. The auditor's contribution is a "
    "confirmation + two honest framing corrections (the 0.5536 secondary figure did not reproduce; two 23-bucket items "
    "are minor prep-adjacent/coordination cases), neither of which reopens the lever."
)


def build_atom():
    return {
        "id": ATOM_ID, "name": ATOM_CLAIM, "corpus": "math", "tier": "HARD_FAIL",
        "kind": "experiment_landed_vet",
        "cert_status": "honest_negative_proven_bound_front_end_lever_closure",
        "cert_class": ("honest_negative_locative_path_preposition_class_patient_exclusion_feature_NO_ROOM_over_LCCP_"
                       "0p5574_stacked_reader_only_4of27_residual_FP_prep_window_addressable_2_locative_near_along_"
                       "already_in_PREPS_ip3_misses_plus_2_homonymy_with_of_plus_23_out_of_scope_85pct_window3_widen_"
                       "suppresses_4FP_but_loses_4_true_patients_structural_twins_net_plus0p0086_below_plus0p02_no_"
                       "cheap_syntactic_cue_separates_twins_needs_noun_place_vs_artifact_ontology_already_closed_"
                       "thematic_fit_29360_29361_dominant_residual_85pct_light_report_verb_plus_coref_per_instance_"
                       "structural_deeper_parse_and_coref_carry_context_front_end_exhausted_pivot_earned_second_"
                       "witness_off_live_reader"),
        "description": (ATOM_CLAIM + "\n\nRECOMPUTE (off the LIVE reader, .venv, Fix #28): " + ATOM_RECOMPUTE
                        + "\n\nHONEST SCOPE: " + ATOM_SCOPE),
        "aliases": [
            "LCCP locative/path preposition-class patient-exclusion feature has NO ROOM (front-end exhausted)",
            "only 4/27 residual FPs prep-window-addressable; window-3 trades 4 true patients for 4 FPs (structural twins)",
            "reading-axis structural front-end levers EXHAUSTED; pivot to deeper parse + coref/carry-context earned",
            "dominant residual 23/27=85% = light/report-verb patient mis-extraction + clause-boundary coref/head-finding",
            "twin-separation needs noun place-vs-artifact ontology = already-closed thematic-fit (atoms 29360/29361)",
            "second-witness VET off the live LCCP reader confirms baseline 0.5574 (34/61) + window-3 +0.0086 < +0.02 exactly",
        ],
        "ts_iso": _iso, "ts": _ts,
        "metadata": {
            "provenance_quality": ("independent_venv_offdisk_second_witness_off_LIVE_reader_full_cell_rerun_seed7_"
                                   "baseline_exact_plus_27_FP_dumped_with_token_context_and_fprep_window_values_plus_"
                                   "window3_ceiling_rederived_off_code_plus_locative_class_variants_recomputed_plus_"
                                   "twin_separation_break_attempt_plus_thematic_fit_closure_confirmed_off_disk_29360_29361"),
            "anchor": ANCHOR, "second_witness_on_design_gate_abort": True, "cell_shipped": False,
            "live_reader": LIVE_READER, "gold": GOLD, "supersedes": None,
            "store_head_at_write": "unsynced_needs_orchestrator",
            "verified_off_data": ATOM_RECOMPUTE, "honest_scope": ATOM_SCOPE, "metrics": ATOM_METRICS,
            "over_reads_corrected": OVER_READS,
            "genuine_positives_symmetric_anti_negativity": GENUINE_POS,
            "revival_criteria": REVIVAL,
            "cross_arc_overlap_check": XARC,
            "negative_is_real_not_weak_implementation": True,
            "front_end_lever_closure_verdict": ("CONFIRMED: locative/path preposition-CLASS patient-exclusion feature "
                                                "has NO ROOM (4/27 addressable, window-3 trades 4 TP for 4 FP, "
                                                "+0.0086 << +0.02); reading-axis structural front-end exhausted; pivot "
                                                "to deeper parse + coref/carry-context loop earned."),
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "vet_a_negative_confirm_real_not_harness_bug_or_too_weak_implementation",
                "second_witness_reproduce_load_bearing_numbers_off_live_reader_not_summary",
                "every_negative_check_how_the_brain_does_it_proactively_USER",
                "dont_assume_brain_check_outcome_brain_may_fail_same_way_then_fix_is_native",
                "experiment_design_gate_can_fail_real_baseline_difficulty_on_before_full_run",
                "substrate_kb_concept_overlap_check_on_schema_vet",
                "arc_continuation_is_not_closure_drill_negatives_for_mechanism",
                "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
            ],
            "composes_with": COMPOSES,
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE,
            "needs_orchestrator_store_sync": True,
            "local_write_only_no_origin_push_no_remote_persist": True,
            "importance": ("HIGH / LINCHPIN: this is the closing negative for the reading-axis STRUCTURAL FRONT-END. "
                           "With the surface prep-class lever (this atom) and the topical situation-model lever (CCL "
                           "HARD_FAIL) both proven exhausted, the cheap front-end is closed and the strategic pivot to "
                           "a deeper parser + coref/carry-context loop is EARNED (not premature). The load-bearing "
                           "input to that pivot is the localization: 85% of the residual is per-instance structural "
                           "(light/report-verb mis-extraction + clause-boundary coref), NOT surface-cue-addressable."),
            "plain_language": ("We tried the last cheap trick for cleaning up the reader's wrong answers: a rule that "
                               "throws out a candidate object when it sits right after a location/path preposition "
                               "(like 'near', 'along'). Reproducing everything off the live reader ourselves (not "
                               "trusting the summary), it has NO ROOM. Out of the 27 remaining mistakes, only 4 even "
                               "have such a preposition nearby, and the only way to catch those 4 (look one word "
                               "further back) ALSO throws out 4 genuinely correct objects that sit in the exact same "
                               "surface shape -- 'against his mimic castle' (correct) looks identical to 'near a beaver "
                               "dam' (wrong). Telling them apart needs knowing whether the noun is a PLACE or a THING, "
                               "which is a semantic ability we already proved doesn't help here (it actually hurt). The "
                               "real remaining 85% of mistakes are deeper: the reader grabs the wrong word after "
                               "reporting verbs like 'say/show', or grabs a subject from the next clause, or grabs an "
                               "object that belongs to an embedded verb. None of these is fixable with a cheap surface "
                               "rule -- they need a proper deeper parser and a memory/coreference loop. So the cheap "
                               "front-end is genuinely exhausted, and moving on to build the deeper machinery is the "
                               "right call, not giving up too early."),
        },
    }


def ledger_row(atom):
    return {
        "op": "cert_ruling_second_witness_lccp_locative_prep_class_patient_exclusion_NO_ROOM_front_end_exhausted",
        "corpus": "math", "tier": atom["tier"], "cert_status": atom["cert_status"],
        "cert_class": atom["cert_class"], "anchor": ANCHOR,
        "second_witness_on_design_gate_abort_no_cell_shipped": True, "live_reader": LIVE_READER,
        "atom_id": atom["id"],
        "cert_delta": {"CG": 0, "MM": 0, "HF": 1},
        "cell_verdict": "DESIGN_GATE_ABORT (exp_dev triage: locative/path prep-class patient-exclusion has no room)",
        "auditor_tier": "HARD_FAIL / honest-negative (front-end lever closure)",
        "verdict": ("CONFIRMED_HARD_FAIL_locative_path_preposition_class_patient_exclusion_feature_NO_ROOM_over_LCCP_"
                    "0p5574_stacked_reader_second_witness_reproduced_off_LIVE_reader_baseline_exact_P0p5574_tp34_npred61_"
                    "R0p34_fp27_split18_5_4_only_4of27_prep_window_addressable_2_locative_near_along_already_in_PREPS_"
                    "ip3_misses_plus_2_homonymy_plus_23_out_of_scope_85pct_window3_widen_suppresses_4FP_loses_4_true_"
                    "patients_structural_twins_net_plus0p0086_below_plus0p02_R_0p34_to_0p30_no_cheap_cue_separates_"
                    "twins_needs_place_vs_artifact_ontology_already_closed_thematic_fit_29360_29361_dominant_residual_"
                    "85pct_light_report_verb_plus_coref_per_instance_structural_front_end_EXHAUSTED_pivot_to_deeper_"
                    "parse_and_coref_carry_context_EARNED"),
        "verified_off_data": True,
        "decisive_numbers": {
            "baseline_Q_base_seed7": {"P": 0.5574, "tp": 34, "n_pred": 61, "R": 0.34, "fp": 27,
                                      "subcat": 18, "within": 5, "spurious": 4, "reproduced_exact": True},
            "partition_2_2_23": True, "out_of_scope_fraction": 0.852,
            "window3": {"P_before": 0.5574, "P_after": 0.5660, "delta_abs": 0.0086, "material_bar": 0.02,
                        "clears": False, "fps_suppressed": 4, "true_patients_lost": 4, "R_after": 0.30,
                        "structural_twins": True},
            "locative_class_restricted": {"locative_only": 0.5690, "locative_plus_in_of_with": 0.5741,
                                          "none_clears_plus0p02": True},
            "twin_separation_needs": "noun place-vs-artifact ontology (already-closed thematic-fit atoms 29360/29361)",
            "dominant_residual_85pct": "light/report-verb patient mis-extraction + clause-boundary coref/head-finding + wrong-head-into-embedded-verb (per-instance structural)",
        },
        "framing_correction_vs_director": (
            "Director asked (expecting YES) whether the no-room / front-end-structural-levers-exhausted call is "
            "CONFIRMED, reproduced off the live reader not the summary. RESULT: CONFIRMED. Second-witness off the live "
            "LCCP reader reproduces EXACTLY: baseline Q_base 0.5574 (34/61), R 0.34, 27 FP split 18/5/4; partition "
            "2 locative/path (near/along, both already in PREPS, both ip-3 window-misses) + 2 homonymy (with/of) + 23 "
            "out-of-scope (85.2%); window-3 widen suppresses 4 FP but loses 4 TRUE patients (rub/castle against, "
            "obey/parents to, choose/places in x2 -- structural twins), net +0.0086 << +0.02, R 0.34->0.30. No cheap "
            "syntactic cue separates the twins (dam=place-adjunct vs castle=contacted-theme are byte-structurally "
            "identical) -> needs noun place-vs-artifact ontology, which lands in ALREADY-CLOSED thematic-fit territory "
            "(atoms 29360 SCV / 29361 graded-thematic-fit, both HARD_FAIL, confirmed off-disk). Dominant residual "
            "23/27=85% is light/report-verb patient mis-extraction + clause-boundary coref/head-finding + wrong-head-"
            "into-embedded-verb = per-instance STRUCTURAL, needing a deeper parse + coref/carry-context loop. TWO honest "
            "framing corrections (neither reopens the lever): (i) exp_dev's secondary figure P=31/56=0.5536 'worse than "
            "baseline' did NOT reproduce -- auditor got 0.5690-0.5741, marginally BETTER but still below +0.02, so "
            "immaterial; (ii) two of the 23 out-of-scope items are minor prep-adjacent/coordination cases (lie/skin "
            "'next' is a PREPS-list gap = 1-FP lexical patch; struggle/tide is coordination-under-prep). VERDICT: the "
            "front-end structural levers are EXHAUSTED and the pivot is EARNED, not premature."),
        "framing_correction_vs_exp_dev": (
            "exp_dev's triage is CONFIRMED on every load-bearing number (baseline, 2/2/23 partition, window-3 4-FP/4-TP "
            "structural-twin trade, +0.0086 below bar, place-vs-artifact-ontology conclusion). Two honest corrections: "
            "(1) the secondary locative-CLASS-restricted figure P=31/56=0.5536 ('worse than baseline') did NOT "
            "reproduce under the auditor's reasonable class definitions (got 0.5690-0.5741, marginally BETTER than "
            "0.5574); the exact number is class-definition-dependent and IMMATERIAL since all variants stay below the "
            "+0.02 bar and trade true patients. (2) Two of the 23 'out-of-scope' items are technically prep-adjacent, "
            "not truly out-of-scope: lie/skin 'lies next the skin' misses because 'next' (archaic prep) is absent from "
            "the PREPS list (a 1-FP lexical patch), and struggle/tide 'against the wind and the tide' is coordination-"
            "under-a-preposition. Neither is a structural preposition-CLASS lever; each is ~1 FP and neither changes "
            "the verdict. exp_dev CREDITED for the design-gate discipline (free triage + ceiling test BEFORE shipping, "
            "correct abort)."),
        "brain_check": (
            "Does the brain resolve the 23-FP dominant class (light/report-verb patient mis-extraction + clause-"
            "boundary subject/coref) structurally or via discourse/coref+world-knowledge? MIXED -- and the split IS the "
            "pivot signal. Quotative speech-content and clause-boundary subject mis-attach are resolved by CLAUSE "
            "SEGMENTATION + direct-speech construction + tracking the NP as the NEXT clause's subject (structural, a "
            "deeper incremental parser the shallow front-end lacks); wrong-head-into-embedded-verb by subcat + "
            "attachment (structural); the idiom/light-verb tail + the place-vs-artifact twin-separation need lexicalized "
            "construction retrieval + thematic-fit/world-knowledge. The brain uses NO cheap 1-token surface cue for any "
            "of these -- it runs a full incremental parse integrated with discourse/coref. So the pivot target is "
            "CORRECT: a deeper parser + the coref/carry-context loop (the recon's flagged next-drill), not another "
            "cheap front-end feature."),
        "revival_criterion": ("Deeper incremental parser (clause segmentation + PP-attachment + direct-speech "
                              "construction) + coref/carry-context loop; independent multi-annotator gold before "
                              "0.5574 is called a universal bound. Do NOT revive the locative/path preposition-CLASS "
                              "feature -- proven no room."),
        "fairness_guards": ("Independent off-live-reader recompute (not the summary); baseline positive control "
                            "reproduces published 0.5574 at seed 7; window-3 ceiling re-derived off-code on the live "
                            "kept set; can-fail check (the lever COULD have cleared +0.02 with clean FP suppression -- "
                            "it demonstrably does not, and costs recall); symmetric anti-negativity (two honest "
                            "corrections that do NOT reopen the lever; credit preserved for a clean negative)."),
        "cross_arc_overlap_check": XARC,
        "net_cert_delta": ("+1 proven-negative (front-end lever closure): the locative/path preposition-CLASS patient-"
                           "exclusion feature has NO ROOM over the 0.5574 LCCP stacked reader (4/27 addressable; "
                           "window-3 trades 4 true patients for 4 FPs as structural twins; +0.0086 << +0.02; recall "
                           "0.34->0.30), the twin-separation needs already-closed thematic-fit, and the dominant 85% "
                           "residual is per-instance structural (light/report-verb + coref). Reading-axis STRUCTURAL "
                           "FRONT-END exhausted; pivot to deeper parse + coref/carry-context loop EARNED. Revival = "
                           "deeper parser + coref loop, NOT the prep-class feature."),
        "auditor": "hdi_skunkworks", "decision": "atomize_local_only_hard_fail_front_end_lever_closure",
        "needs_orchestrator_store_sync": True, "local_write_only": True,
        "ts_iso": _iso, "ts": _ts,
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
    print("=== A5 atom-write: lccp_locative_prep_class_patient_exclusion NO ROOM / front-end exhausted (2026-07-19) ===")
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
    print("ATOM (HARD_FAIL / honest-negative front-end lever closure):", atom["id"][:110], "...")
    print("new store line =", n_ok)


if __name__ == "__main__":
    main()
