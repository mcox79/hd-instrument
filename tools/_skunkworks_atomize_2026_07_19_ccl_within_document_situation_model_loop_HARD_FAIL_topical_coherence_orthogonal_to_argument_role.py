"""
A5-gated atomization: exp_compress_and_carry_comprehension_loop_ccl_v1 (LOCAL commit 8ad34ea9) -> ONE atom (2026-07-19).
  HARD_FAIL / honest-negative (proven-bound direction-closure). Cell verdict HARD_FAIL_CCL CONFIRMED off-disk on BOTH axes.
  A clean, well-controlled NEGATIVE that CLOSES the within-document topical-situation-model-cue direction + redirects
  compounding to cross-document consolidation. Auditor CONFIRMS the negative is REAL (not a too-weak/broken cue) AND
  sharpens the mechanism: topical document-coherence is ORTHOGONAL to argument-role correctness (a framing correction to
  the cell's "strong local cues resist a weak doc cue" story -- the DEFER never fired; the cue actively mis-selects).

INDEPENDENT RECOMPUTE (off-disk, .venv Scripts/python, Fix #28; NOT verdict_msg):
  - BYTE-REPRO: full re-run reproduces metrics.json identically (modulo ts/elapsed). OMP/MKL/OPENBLAS=1 in-cell.
  - GATE-D (harness valid): ARM A kept-hash abbed72715740f6e == LCCP arm C hash -- confirmed INDEPENDENTLY against
    data/exp_learned_argstruct_parser_lccp_independent_gold_v1/metrics.json (kept_hashes.C_lccp = abbed72715740f6e).
    Passes at smoke AND full AND self-test. ARM A IS the true LCCP baseline; downstream arms trustworthy.
  - DISCRIMINATOR FIRES: 3 distinct arm hashes (A abbed7.., B b1d5525.., C 63a85cd..); n_doc_flip B/C = 15/16.
  - AXIS-1 (precision-raise) FAIL, and precision DROPS not merely fails-to-rise: A P=0.500 -> B/C P=0.456
    (dP(C-A)=-0.044); within_frame_fp 6 -> 9; within-frame precision 0.850 -> 0.775. doc_weight SWEPT 0.1/0.3/0.5/0.7/
    1.0/1.2 -> ALL give P=0.456, wf_fp=9 (recomputed off-code). The finding is NOT a too-weak-weight artifact.
  - ANGLE-1 (DECISIVE) -- is the negative REAL or a broken/too-weak cue? Off-code flip analysis: among within-frame
    KEPT decisions the cue CHANGED (A->C), 3/3 are TP->fp and 0/3 fp->TP: L09_05 build huts(gold)->lakes,
    L10_38 rule copybook(gold)->joe, L12_10 admire beauty(gold)->boy. The cue NEVER fixes a within-frame error; it
    only DISPLACES correct grammatical patients with topically-salient-but-wrong ones (recurring characters / topics).
    The cue is a FAIR, competent implementation (causal prior-sentences-only, real GloVe centroids over committed
    entities + sentence content, glass-box, weighted parallel cue with DEFER, swept). It is NOT broken. The negative
    is REAL: topical document-coherence is ORTHOGONAL to argument-role correctness. FRAMING CORRECTION vs the cell's
    "strong local cues resist a weak doc cue" story: n_defer=0 (DEFER never fired) -> the failures are NOT the base
    resisting; they are the doc cue WINNING and mis-selecting toward salient-but-wrong. The cue is ANTI-correlated
    with correctness on the decisions it influences -- a stronger negative than "too weak". SCOPE: this closes the
    TOPICAL-COHERENCE parallel-cue instantiation of a situation model, NOT a structurally-different (role/event-
    binding) situation model, which is a different mechanism, not a re-weighting.
  - ANGLE-2 (COMPOUNDING construct-validity kill) -- VALID and airtight: ARM A (no situation model) precision-slope
    +0.1891 is EQUAL-OR-LARGER than ARM C +0.1757. The within-document precision rise (C 2nd-half 0.474 > 1st 0.433,
    +0.040) EXISTS in the no-situation-model baseline (A +0.060) -> a GENERIC ORDER EFFECT, mechanistically the LCCP
    running per-verb transitivity prior accumulating, NOT the carried situation model. doc-coh discriminative-margin
    slope +0.0293 with bootstrap 90% CI [-0.2322, +0.4106] SPANS 0 (excludes_zero=False); at smoke it sign-flips to
    -0.134 (CI [-0.4831,+0.4505], also spans 0). Robustly null; the apparent compounding is NOT attributable to the
    situation model. Confirmed.
  - ANGLE-4 (slice-robustness): the negative holds at BOTH slices -- full (dP -0.044, margin +0.029 CI spans 0) AND
    smoke (dP -0.026, margin -0.134 CI spans 0); precision DROPS at both. The margin-slope point estimate SIGN-FLIPS
    across slices = consistent with a true null, strengthening (not weakening) the negative.
  - CROSS-ARC OVERLAP: substrate_query on the mechanism returns only generic concept-nodes ('document', cosine ~0.35),
    NO prior experiment cell rediscovering this. The two direct parents (LCCP 29338, coherence-gate 29337) are
    explicitly cited by the cell. Genuine targeted extension.

TIER: HARD_FAIL / honest-negative (proven-bound = DIRECTION CLOSURE). A clean negative: a carried topical situation-
  model DOCUMENT-COHERENCE cue, integrated as one weighted parallel cue into the LCCP scorer with macrorule-compressed
  MAP/SHIFT carry, (a) does NOT raise argument-extraction precision past the LCCP 0.500 ceiling (it DROPS it to 0.456,
  robust across doc_weight 0.1-1.2, because topicality is orthogonal to patienthood + the cue anti-selects), and (b)
  does NOT produce within-document compounding attributable to the carried model (the apparent rise is a generic order
  effect from the subcat prior, control-killed; margin-slope CI spans 0 at both slices). Counts as a PROVEN NEGATIVE
  that closes the within-document-topical-loop direction. REDIRECT (sound): compounding belongs on the cross-document
  schema-fit-gated consolidation axis (Matthew effect is cross-session, has human precedent; within-document
  compounding does not). REVIVAL: a STRUCTURED (role/event-binding) carry, not a topical centroid; + independent
  (non-self-consistent, multi-annotator) gold before calling 0.50 a universal bound. CERT delta +1 (proven negative).

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
ATOMIZED_BY = ("skunkworks_landed_vet_compress_and_carry_comprehension_loop_ccl_v1_HARD_FAIL_within_document_topical_"
               "situation_model_cue_does_not_raise_precision_topicality_orthogonal_to_argument_role_and_does_not_"
               "compound_generic_order_effect_control_killed_2026-07-19")
ATOMIZED_DATE = "2026-07-19"
ANCHOR = "compress_and_carry_comprehension_loop_ccl_v1"
CELL_COMMIT = "8ad34ea96379aaf462fae89bb8c0aab07c70840a"

LCCP_PARENT = ("math::MM_learned_argstruct_parser_lccp_independent_gold_v1_REAL_NONCIRCULAR_learned_cue_competition_"
               "parser_reduces_arg_misattachment_A_P0p196_R0p440_fp0p804_to_C_P0p500_R0p340_fp0p500_dFPrate_plus0p304")  # ..._29338
LCCP_PARENT_SHORT = "LCCP atom 29338 / commit 3c6ff0f3 (ends ..._29338)"

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

XARC = (
    "substrate_query 'situation model document coherence carried context compounding within document reading loop' -> "
    "top hits are generic concept-nodes only (CN_document cosine 0.3545, document 0.3486, creating document 0.3379) -- "
    "lexical char-trigram matches to 'document', NOT any prior EXPERIMENT cell rediscovering this mechanism. NONE at "
    "experiment-cell level > 0.30. The two direct parents -- LCCP (29338, commit 3c6ff0f3) which ARM A byte-reproduces, "
    "and the coherence-gate (29337) whose DEFERRED state is reused -- are EXPLICITLY cited + credited by the cell and "
    "confirmed off-disk. Genuine targeted extension (add a carried situation-model cue to the LCCP scorer), NOT a "
    "hidden rediscovery. Auditor accepts."
)

ATOM_ID = (
    "math::HF_compress_and_carry_comprehension_loop_ccl_v1_HONEST_NEGATIVE_within_document_topical_situation_model_"
    "DOCUMENT_COHERENCE_cue_wired_as_one_weighted_parallel_cue_into_LCCP_scorer_with_macrorule_compressed_MAP_SHIFT_"
    "carry_plus_LTWM_gist_DOES_NOT_raise_argument_extraction_precision_past_LCCP_0p500_ceiling_DROPS_to_0p456_wf_fp_6_"
    "to_9_within_frame_precision_0p850_to_0p775_doc_weight_SWEPT_0p1_0p3_0p5_0p7_1p0_1p2_ALL_P0p456_wf_fp_9_NOT_a_too_"
    "weak_weight_artifact_DECISIVE_off_code_flip_analysis_among_within_frame_kept_flips_3of3_TP_to_fp_0_fp_to_TP_"
    "L09_05_build_huts_gold_to_lakes_L10_38_rule_copybook_gold_to_joe_L12_10_admire_beauty_gold_to_boy_cue_NEVER_fixes_"
    "only_displaces_correct_patient_with_topically_salient_wrong_one_recurring_character_or_topic_TOPICAL_document_"
    "coherence_ORTHOGONAL_to_argument_role_correctness_FRAMING_CORRECTION_n_defer_0_DEFER_never_fired_failures_NOT_base_"
    "resisting_weak_cue_but_doc_cue_WINNING_and_mis_selecting_cue_ANTI_correlated_with_correctness_on_influenced_"
    "decisions_stronger_negative_than_too_weak_cue_is_FAIR_competent_causal_prior_sentences_only_real_GloVe_centroids_"
    "glass_box_weighted_parallel_DEFER_swept_NOT_broken_n_flip_13_to_16_AXIS2_COMPOUNDING_construct_validity_KILL_ARM_A_"
    "no_situation_model_precision_slope_plus0p1891_EQUAL_OR_LARGER_than_ARM_C_plus0p1757_within_doc_rise_C_2nd_0p474_gt_"
    "1st_0p433_EXISTS_in_baseline_A_plus0p060_GENERIC_ORDER_EFFECT_from_LCCP_running_transitivity_prior_NOT_carried_"
    "situation_model_doccoh_margin_slope_plus0p0293_bootstrap_ci90_neg0p2322_to_plus0p4106_SPANS_0_smoke_sign_flips_to_"
    "neg0p134_ci_neg0p4831_plus0p4505_also_spans_0_robustly_null_slice_robust_both_slices_precision_DROPS_margin_ci_"
    "spans_0_sign_flip_consistent_with_true_null_GATE_D_A_hash_abbed72715740f6e_eq_LCCP_arm_C_confirmed_independently_"
    "vs_LCCP_metrics_passes_smoke_full_selftest_discriminator_fires_3_distinct_hashes_n_flip_15_16_can_fail_both_ways_"
    "cue_COULD_help_demonstrably_HURT_byte_repro_full_run_identical_EXTENDS_29338_which_already_flagged_does_NOT_"
    "compound_slope_neg0p16_NOT_improving_as_it_reads_now_confirmed_even_WITH_carried_topical_cue_REDIRECT_compounding_"
    "belongs_on_cross_document_schema_fit_gated_consolidation_Matthew_effect_cross_session_has_human_precedent_within_"
    "document_compounding_does_not_REVIVAL_structured_role_event_binding_carry_not_topical_centroid_plus_independent_"
    "multi_annotator_gold_before_0p50_called_universal_bound_single_annotator_caveated_McGuffey_gold_no_LLM_deterministic_"
    "OMP1_8ad34ea9_LOCAL_ONLY_2026-07-19"
)

ATOM_CLAIM = (
    "MATH HARD_FAIL / honest-negative (proven-bound = DIRECTION CLOSURE). CLAIM (the NEGATIVE, confirmed off-disk on "
    "BOTH pre-registered axes): a carried, situation-model DOCUMENT-COHERENCE cue -- integrated as ONE weighted "
    "parallel cue into the LCCP argument-structure scorer (per Angle-2, not a late rerank), with macrorule-COMPRESSED "
    "MAP/SHIFT carry + LTWM gist retrieval -- (a) does NOT raise argument-extraction precision past LCCP's 0.500 "
    "ceiling: it DROPS precision to 0.456 (dP -0.044), raises within-frame FPs 6->9, drops within-frame precision "
    "0.850->0.775, and HURTS identically at every doc_weight swept 0.1-1.2 (recomputed off-code); and (b) does NOT "
    "produce within-document COMPOUNDING attributable to the carried model: the apparent precision rise (C 2nd-half "
    "0.474 > 1st 0.433) EXISTS in the ARM-A no-situation-model baseline (slope +0.189 >= C's +0.176) -- a generic "
    "order effect from the LCCP running transitivity prior, control-killed -- and the doc-coh discriminative-margin "
    "slope +0.029 has bootstrap 90% CI [-0.232, +0.411] spanning 0 (sign-flips to -0.134 at smoke, also spanning 0). "
    "IS THE NEGATIVE REAL OR A WEAK/BROKEN CUE? -- REAL. The cue is a FAIR, competent implementation (causal, "
    "prior-sentences-only; real GloVe content centroids over the parser's OWN committed entities + sentence content; "
    "glass-box; weighted parallel cue with a DEFER state; doc_weight swept) and is demonstrably ACTIVE (n_doc_flip "
    "13-16), NOT broken. The DECISIVE off-code flip analysis: among the within-frame KEPT decisions the cue changed, "
    "3/3 are TP->fp and 0/3 fp->TP (build huts->lakes, rule copybook->joe, admire beauty->boy) -- the cue NEVER fixes "
    "a within-frame error, it only DISPLACES the correct grammatical patient with a topically-salient-but-wrong one "
    "(a recurring character or topic). MECHANISM (and FRAMING CORRECTION vs the cell's 'strong local cues resist a "
    "weak doc cue' story): topical document-coherence is ORTHOGONAL to argument-role correctness. n_defer=0 -- the "
    "DEFER guard NEVER fired, so the failures are NOT the base resisting a weak cue; they are the doc cue WINNING and "
    "mis-selecting toward salience. The cue is ANTI-correlated with correctness on the decisions it influences -- a "
    "STRONGER negative than 'too weak'. HONEST SCOPE: this closes the TOPICAL-COHERENCE parallel-cue instantiation of "
    "a within-document situation model; it does NOT refute a structurally-different (role/event-binding) situation "
    "model, which is a different mechanism (not a re-weighting). REDIRECT (sound): within-document compounding failed "
    "here AND has no human precedent, while knowledge-compounding (the Matthew effect) is a cross-session/cross-"
    "document phenomenon -> move compounding to the cross-document schema-fit-gated CONSOLIDATION axis, carrying the "
    "lesson that the carry must be STRUCTURED (role/schema), not a topical centroid, or it hits the same wall. This "
    "EXTENDS LCCP 29338, which already measured 'does NOT compound online, NOT improving as it reads' -- now confirmed "
    "to hold even WITH a carried topical situation-model cue."
)

ATOM_RECOMPUTE = (
    "INDEP recompute (.venv Scripts/python, off-disk, NOT verdict_msg; Fix #28): "
    "(A) BYTE-REPRO: full re-run reproduces metrics.json identically (modulo ts/elapsed); OMP/MKL/OPENBLAS=1 in-cell. "
    "(B) GATE-D: ARM A kept-hash abbed72715740f6e == LCCP arm C hash, confirmed INDEPENDENTLY vs "
    "data/exp_learned_argstruct_parser_lccp_independent_gold_v1/metrics.json (kept_hashes.C_lccp=abbed72715740f6e); "
    "passes at smoke, full, and self-test -> harness valid, ARM A is the true LCCP baseline. "
    "(C) DISCRIMINATOR: 3 distinct arm hashes (A abbed7.. B b1d5525.. C 63a85cd..); n_doc_flip B/C = 15/16 -> arms "
    "genuinely differ, cue active. "
    "(D) AXIS-1 FAIL (precision DROPS): A P=0.500 R=0.340 wf_fp=6 wfP=0.850 -> C P=0.456 R=0.310 wf_fp=9 wfP=0.775; "
    "doc_weight SWEEP recomputed off-code {0.1,0.3,0.5,0.7,1.0,1.2} ALL -> P=0.456, wf_fp=9 (n_flip 13-16). Not a "
    "too-weak-weight artifact. "
    "(E) ANGLE-1 DECISIVE flip analysis (off-code): among within-frame kept flips A->C, 3/3 TP->fp, 0/3 fp->TP -- "
    "L09_05 build gold huts -> lakes; L10_38 rule gold copybook -> joe; L12_10 admire gold beauty -> boy. Cue never "
    "fixes, only displaces correct patient with topically-salient-but-wrong. n_defer=0 (DEFER never fired). Cue is "
    "FAIR/competent (causal, real GloVe centroids over committed entities + sentence content, glass-box, DEFER, swept) "
    "and ACTIVE, not broken -> negative is REAL: topicality orthogonal to argument-role; cue anti-selects. "
    "(F) AXIS-2 KILL: ARM A precision-slope +0.1891 >= ARM C +0.1757; C 2nd-half 0.474 > 1st 0.433 (+0.040) but A "
    "also +0.060 -> generic order effect (LCCP running transitivity prior), NOT the carried model. doc-coh margin "
    "slope +0.0293, bootstrap ci90 [-0.2322,+0.4106] excludes_zero=False (spans 0). "
    "(G) SLICE-ROBUST: smoke dP -0.026, margin slope -0.134 ci90 [-0.4831,+0.4505] (spans 0); precision drops at BOTH "
    "slices; margin-slope sign-flip across slices = consistent with a true null."
)

ATOM_SCOPE = (
    "McGuffey reader argument-structure extraction, slice L04+L05+L07+L08+L09+L10+L12 (163 sents, 225 reader "
    "candidates); INDEPENDENT single-annotator caveated gold (data/gold_mcguffey_lccp_argstruct_v1.json); mechanism = "
    "situation-model-guided construction-integration with macrostructure-compressed carry (Kintsch/van Dijk CI, "
    "Ericsson&Kintsch LTWM, Zwaan/Gernsbacher MAP/SHIFT). No LLM; deterministic (OMP/MKL/OPENBLAS=1). Load-bearing "
    "BOUNDS: "
    "(a) DIRECTION CLOSED = the TOPICAL-COHERENCE parallel-cue instantiation of a within-document situation model. A "
    "carried topical-centroid document-coherence cue does not and cannot raise argument-extraction precision here "
    "because the most document-coherent candidate (a recurring character / topical entity) is systematically NOT the "
    "grammatical patient. The cue anti-selects; DEFER cannot save it (never fires). This is a REAL bound for this "
    "mechanism class, robust across doc_weight and slice. "
    "(b) NOT CLOSED = a structurally-different situation model. A role/event-binding carry (who-did-what-to-whom "
    "tracked across sentences), as opposed to a topical centroid, is a DIFFERENT mechanism and is UNTESTED here. The "
    "negative must NOT be over-read as 'no situation model can help argument extraction'. "
    "(c) COMPOUNDING is not achievable within a single short document via this cue: the only within-document "
    "improvement present (A slope +0.19) is the LCCP subcat/transitivity prior accreting per-verb evidence, not a "
    "growing world-model; the carried situation-model cue adds nothing (C slope slightly LOWER). "
    "(d) 0.50 PRECISION RESIDUAL is a real bound FOR THIS mechanism class (sentence-local LCCP + topical-doc cue) but "
    "should NOT be called a universal brain-faithful ceiling: the gold is single-annotator + caveated and the reader "
    "extractions are themselves noisy, so part of the 'coherent-but-wrong' residual is gold/extraction noise, not a "
    "proven wetware limit. "
    "BRAIN-CHECK (outcome not pre-assumed, and it FAILED THE SAME WAY here in part): the literature the cell cites "
    "(Mitchell/Corley/Garnham 1992; Britt 1994) shows some mis-attachments resist even human discourse-context when a "
    "local obligatory-argument cue is strong -- a REAL shared bound, ACCEPT. BUT the dominant failure here is NOT "
    "'strong local cue resists' (DEFER never fired); it is 'topical coherence is the wrong signal for argument role'. "
    "The brain does NOT resolve patienthood by topical salience -- it uses structured event/role expectations (thematic "
    "roles, verb-specific selectional structure) integrated with discourse. So the FIX is SUBSTRATE-NATIVE/structured "
    "(a role-binding situation model), not a heavier weight on a topical centroid. "
    "REDIRECT (sound): within-document compounding has no human precedent and failed here; the Matthew effect / "
    "knowledge-compounding IS cross-session/cross-document. Move the compounding hypothesis to the D1 cross-document "
    "schema-fit-gated CONSOLIDATION axis -- WITH a structured (role/schema) carry, or it re-hits the topicality!="
    "correctness wall. "
    "REVIVAL: (1) a STRUCTURED role/event-binding situation model (not a topical centroid) fed into argument "
    "selection; (2) cross-document schema-fit-gated consolidation for the compounding axis (where accretion + human "
    "precedent both exist); (3) independent MULTI-annotator gold before treating 0.50 as a universal precision bound."
)

ATOM_METRICS = {
    "slice": ["L04", "L05", "L07", "L08", "L09", "L10", "L12"], "n_sents": 163, "n_reader_cands": 225,
    "arm_A_lccp_local": {"P": 0.500, "R": 0.340, "wf_fp": 6, "wf_precision": 0.850, "hash": "abbed72715740f6e"},
    "arm_B_doccoh_flat": {"P": 0.4559, "R": 0.310, "wf_fp": 9, "wf_precision": 0.775, "hash": "b1d5525cfbaa8709"},
    "arm_C_ccl_compressed": {"P": 0.4559, "R": 0.310, "wf_fp": 9, "wf_precision": 0.775, "hash": "63a85cd4eaa35ecc"},
    "axis1_precision_raise_pass": False, "dP_C_minus_A": -0.044, "recall_retention_C_over_A": 0.9118,
    "doc_weight_sweep_all_P0p456_wf_fp9": {"0.1": [0.456, 9], "0.3": [0.456, 9], "0.5": [0.456, 9],
                                           "0.7": [0.456, 9], "1.0": [0.456, 9], "1.2": [0.456, 9]},
    "angle1_within_frame_flips_A_to_C": {"TP_to_fp": 3, "fp_to_TP": 0,
                                         "cases": ["L09_05 build gold=huts -> lakes",
                                                   "L10_38 rule gold=copybook -> joe",
                                                   "L12_10 admire gold=beauty -> boy"]},
    "n_defer_B_C": [0, 0], "n_doc_flip_B_C": [15, 16], "n_shifts_C": 20,
    "angle1_verdict": "REAL BOUND (topicality orthogonal to argument-role; cue anti-selects; DEFER never fires), NOT a too-weak/broken cue; cue is fair+competent+active",
    "axis2_compounding_pass": False,
    "compounding_A_control_precision_slope": 0.1891, "compounding_C_precision_slope": 0.1757,
    "compounding_A_2nd_minus_1st": 0.060, "compounding_C_2nd_minus_1st": 0.040,
    "doccoh_margin_slope_C": 0.0293, "bootstrap_ci90_C": [-0.2322, 0.4106], "ci_excludes_zero": False,
    "smoke_dP": -0.026, "smoke_margin_slope": -0.134, "smoke_ci90": [-0.4831, 0.4505], "smoke_ci_spans_zero": True,
    "axis2_construct_validity_kill": "ARM A control slope +0.1891 >= ARM C +0.1757 => within-doc rise is generic order effect (LCCP running transitivity prior), NOT carried situation model; margin-slope CI spans 0 at both slices",
    "gate_d_A_eq_LCCP_arm_C": True, "gate_d_hash": "abbed72715740f6e",
    "gate_d_confirmed_independently": "vs data/exp_learned_argstruct_parser_lccp_independent_gold_v1/metrics.json kept_hashes.C_lccp=abbed72715740f6e; passes smoke+full+self-test",
    "discriminator_fires": True, "baseline_in_band": True, "byte_repro_full_run": True,
    "can_fail_both_ways": "cue COULD help (real added signal), demonstrably HURT (0.500 -> 0.456)",
    "cell_verdict": "HARD_FAIL_CCL", "auditor_tier": "HARD_FAIL / honest-negative (proven-bound direction-closure)",
}

COMPOSES = [
    ("EXTENDS " + LCCP_PARENT_SHORT + " (ARM A byte-reproduces it; Gate-D confirmed): the LCCP atom ALREADY measured "
     "'does NOT compound online, slope -0.16, NOT improving as it reads' and flagged a within-frame residual + "
     "document-scope as an unbuilt fix. THIS cell built the document-scope fix (a carried topical situation-model "
     "cue) and shows it does NOT close either gap: precision DROPS (not just fails to rise) AND the apparent "
     "within-doc compounding is a generic order effect (the very subcat prior LCCP already had), control-killed. It "
     "does NOT supersede 29338 (LCCP remains proven-bound); it CONFIRMS and SHARPENS its non-compounding bound to "
     "include the carried-topical-cue case, and localizes WHY: topicality is orthogonal to argument-role."),
    ("REUSES the coherence-gate (atom 29337) DEFERRED state (base-vs-doc conflict). The VET finds the DEFER guard "
     "NEVER fired here (n_defer=0, defer_margin=0.20): the base scores were not confident enough to trigger it, so "
     "the topical cue won the changed decisions and mis-selected. This repositions the DEFER guard: it protects "
     "confident base decisions, but the damage here comes from LOW-confidence decisions where a wrong-signal cue "
     "should have been down-weighted, not deferred-only-when-base-confident."),
    ("credit: McGuffey reader (PD); GloVe (Pennington 2014) for the content centroids; Kintsch & van Dijk "
     "(construction-integration), Ericsson & Kintsch 1995 (LTWM), Zwaan/Gernsbacher (MAP/SHIFT event segmentation) for "
     "the brain-faithful mechanism framing; Mitchell/Corley/Garnham 1992 + Britt 1994 for the human-discourse-override "
     "bound. Author (exp_dev) CREDITED: a clean, well-controlled negative -- ARM-A control that KILLS the compounding "
     "confound, doc_weight swept, brain-check + literature, can-fail both ways demonstrated, Gate-D positive control, "
     "byte-repro, deterministic. This is exactly the discipline: a negative that closes a direction + redirects."),
]

OVER_READS = [
    ("Cell brain-check framing '(1) strong local cues resist a weak doc cue -> residual FPs = real shared ceiling' is "
     "PARTIALLY right but MIS-LOCATES the dominant mechanism. FRAMING CORRECTION (off-code): n_defer=0 -- the DEFER "
     "guard NEVER fired, so the failures are NOT the base resisting a weak cue. They are the doc cue WINNING "
     "low-confidence decisions and mis-selecting toward topical salience (3/3 within-frame flips TP->fp). The precise "
     "bound is not 'local cue too strong for the doc cue' but 'topical document-coherence is the WRONG SIGNAL for "
     "argument-role selection' -- an orthogonality, not a strength mismatch. This makes the negative STRONGER (the "
     "cue is anti-correlated with correctness), not merely a weak-cue null."),
    ("Do NOT over-read '0.50 precision residual = brain-faithful bound' as a UNIVERSAL ceiling. It is a real bound for "
     "THIS mechanism class (sentence-local LCCP + topical-doc cue) on THIS single-annotator caveated gold with noisy "
     "reader extractions. Part of the 'coherent-but-wrong' residual is gold/extraction noise. A structured role-"
     "binding situation model + independent multi-annotator gold are needed before 0.50 is called a wetware limit."),
    ("Do NOT over-read the HARD_FAIL as closing the SITUATION-MODEL idea. It closes ONE instantiation (topical-"
     "coherence parallel cue). A structurally-different (role/event-binding) carry is a different mechanism, untested "
     "here. The redirect to cross-document consolidation is sound BUT must carry a STRUCTURED signal or it re-hits the "
     "same topicality!=correctness wall."),
]

REVIVAL = [
    ("STRUCTURED situation model: feed a role/event-binding carry (thematic-role/verb-selectional expectations tracked "
     "across sentences) into argument selection, NOT a topical GloVe centroid. The brain resolves patienthood by "
     "structured event/role expectations integrated with discourse, not by topical salience -- this is the substrate-"
     "native fix, not a heavier weight on the topical cue."),
    ("CROSS-DOCUMENT CONSOLIDATION for compounding: move the improving-as-it-reads hypothesis to the D1 cross-document "
     "schema-fit-gated consolidation axis, where knowledge accretion AND human precedent (Matthew effect) both exist. "
     "Within a single short document there is neither enough accretion nor a human precedent."),
    ("INDEPENDENT MULTI-ANNOTATOR gold before treating the 0.50 precision plateau as a universal bound; the current "
     "single-annotator caveated gold + noisy reader extractions leave part of the residual as measurement noise."),
]

GENUINE_POS = (
    "GENUINE CREDIT preserved symmetrically (a clean negative is a valuable cert, NOT a failure to minimize): this is "
    "exactly the discipline. The cell is a WELL-CONTROLLED honest negative -- (1) the ARM-A control (no situation "
    "model) KILLS the compounding confound decisively (control slope +0.189 >= C +0.176 => the apparent rise is a "
    "generic order effect, not the carried model); (2) doc_weight swept 0.1-1.2 (rules out a too-weak-weight "
    "artifact); (3) brain-check with primary literature, outcome not pre-assumed; (4) can-fail-both-ways demonstrated "
    "(the cue COULD help, provably HURT); (5) Gate-D positive control passes (ARM A byte-reproduces LCCP arm C); (6) "
    "byte-repro + determinism; (7) discriminator fires (3 distinct hashes). It CLOSES a direction (within-document "
    "topical situation-model cue) AND redirects (compounding -> cross-document consolidation) -- the ideal shape of a "
    "negative. The auditor's contribution is a SHARPENING, not an overturn: the mechanism is localized (topicality "
    "orthogonal to argument-role; cue anti-selects; DEFER never fires) and the framing corrected (stronger negative "
    "than the cell's 'weak cue' story), while the negative itself is fully CONFIRMED off-disk on both axes. What this "
    "IS: proof that a carried topical situation-model cue is the wrong signal for within-document argument-extraction "
    "precision and does not compound. What it is NOT: a refutation of structured (role-binding) situation models or a "
    "universal 0.50 ceiling."
)


def build_atom():
    return {
        "id": ATOM_ID, "name": ATOM_CLAIM, "corpus": "math", "tier": "HARD_FAIL",
        "kind": "experiment_landed_vet",
        "cert_status": "honest_negative_proven_bound",
        "cert_class": ("honest_negative_within_document_topical_situation_model_document_coherence_cue_does_not_raise_"
                       "argument_extraction_precision_drops_LCCP_0p500_to_0p456_robust_across_doc_weight_topicality_"
                       "orthogonal_to_argument_role_cue_anti_selects_3of3_within_frame_flips_TP_to_fp_DEFER_never_"
                       "fires_AND_does_not_compound_apparent_within_doc_rise_is_generic_order_effect_from_LCCP_"
                       "transitivity_prior_control_killed_margin_slope_ci_spans_0_both_slices_gate_D_passes_direction_"
                       "closed_redirect_to_cross_document_consolidation_revival_structured_role_binding_carry"),
        "description": (ATOM_CLAIM + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + ATOM_RECOMPUTE
                        + "\n\nHONEST SCOPE: " + ATOM_SCOPE),
        "aliases": [
            "CCL compress-and-carry comprehension loop HARD_FAIL",
            "within-document topical situation-model cue does not raise argument-extraction precision (drops 0.500->0.456)",
            "topicality orthogonal to argument-role; doc-coherence cue anti-selects (3/3 within-frame flips TP->fp)",
            "no within-document compounding: apparent rise is generic order effect, ARM-A control-killed",
            "redirect compounding to cross-document schema-fit-gated consolidation; revival = structured role-binding carry",
        ],
        "ts_iso": _iso, "ts": _ts,
        "metadata": {
            "provenance_quality": ("independent_venv_offdisk_recompute_byte_repro_full_run_plus_doc_weight_sweep_"
                                   "recompute_plus_off_code_flip_analysis_3of3_TP_to_fp_plus_gate_d_confirmed_vs_LCCP_"
                                   "metrics_plus_smoke_slice_robustness_plus_control_slope_comparison"),
            "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes": None,
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_compress_and_carry_comprehension_loop_ccl_v1/metrics.json",
            "verified_off_data": ATOM_RECOMPUTE, "honest_scope": ATOM_SCOPE, "metrics": ATOM_METRICS,
            "over_reads_corrected": OVER_READS,
            "genuine_positives_symmetric_anti_negativity": GENUINE_POS,
            "revival_criteria": REVIVAL,
            "cross_arc_overlap_check": XARC,
            "negative_is_real_not_weak_implementation": True,
            "angle1_decisive_verdict": ("REAL BOUND: topical document-coherence orthogonal to argument-role; cue "
                                        "anti-selects (3/3 within-frame flips TP->fp, 0 fixes); DEFER never fires "
                                        "(n_defer=0); cue is fair/competent/active, NOT broken; robust across "
                                        "doc_weight 0.1-1.2. Direction closed for TOPICAL cue; a structured role-"
                                        "binding situation model is untested."),
            "angle2_construct_validity_kill_valid": ("ARM A control slope +0.1891 >= ARM C +0.1757; apparent within-"
                                                     "doc rise is a generic order effect from the LCCP running "
                                                     "transitivity prior, NOT the carried situation model; margin-"
                                                     "slope CI [-0.2322,+0.4106] spans 0, sign-flips to -0.134 at "
                                                     "smoke (also spans 0)."),
            "redirect_sound": ("Compounding -> cross-document schema-fit-gated consolidation (D1): within-document "
                               "compounding has no human precedent + failed here; Matthew effect is cross-session. "
                               "Carry must be STRUCTURED (role/schema) not topical, or it re-hits the same wall."),
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "vet_a_negative_confirm_real_not_harness_bug_or_too_weak_implementation",
                "positive_control_clears_own_floor_before_trusting_a_negative",
                "every_negative_check_how_the_brain_does_it_proactively_USER",
                "dont_assume_brain_check_outcome_brain_may_fail_same_way_then_fix_is_native",
                "construction_proof_not_capability_win_could_it_fail_informatively",
                "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
                "substrate_kb_concept_overlap_check_on_schema_vet",
                "arc_continuation_is_not_closure_drill_negatives_for_mechanism",
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
        "auditor": "hdi_skunkworks", "atomized_by": ATOMIZED_BY,
        "verdict": ("HARD_FAIL_honest_negative_proven_bound_within_document_topical_situation_model_document_coherence_"
                    "cue_does_NOT_raise_argument_extraction_precision_DROPS_LCCP_0p500_to_0p456_robust_doc_weight_0p1_"
                    "1p2_topicality_orthogonal_to_argument_role_3of3_within_frame_flips_TP_to_fp_DEFER_never_fires_AND_"
                    "does_NOT_compound_apparent_rise_generic_order_effect_ARM_A_control_slope_plus0p189_ge_C_plus0p176_"
                    "margin_slope_ci_spans_0_both_slices_gate_D_passes_direction_closed_redirect_cross_document_"
                    "consolidation"),
        "cert_increment_delta": 1,
        "decision": (
            "HARD_FAIL / honest-negative (proven-bound = direction closure). Cell verdict HARD_FAIL_CCL CONFIRMED "
            "off-disk on BOTH pre-registered axes; banked as a PROVEN NEGATIVE. Off-disk recompute (.venv, Fix #28): "
            "(1) BYTE-REPRO full run identical; GATE-D ARM A hash abbed72715740f6e == LCCP arm C (confirmed "
            "independently vs LCCP metrics.json, passes smoke+full+self-test) -> harness valid, A is true baseline; "
            "discriminator fires (3 distinct hashes, n_flip 15/16). (2) AXIS-1 FAIL and precision DROPS: A P=0.500 -> "
            "C P=0.456, wf_fp 6->9, wfP 0.850->0.775; doc_weight SWEPT 0.1-1.2 all P=0.456 (not a weak-weight "
            "artifact). (3) ANGLE-1 DECISIVE (is the negative real or a broken/too-weak cue?): REAL. The cue is fair/"
            "competent/active (causal, real GloVe centroids, glass-box, DEFER, swept); off-code flip analysis shows "
            "3/3 within-frame kept flips are TP->fp (build huts->lakes, rule copybook->joe, admire beauty->boy), 0 "
            "fixes -> topical document-coherence is ORTHOGONAL to argument-role; the cue anti-selects toward salient-"
            "but-wrong patients. FRAMING CORRECTION: n_defer=0 (DEFER never fired) -> not 'strong local cue resists a "
            "weak doc cue' but 'doc cue wins low-confidence decisions and mis-selects' -- a STRONGER negative. (4) "
            "AXIS-2 construct-validity KILL VALID: ARM-A control slope +0.1891 >= C +0.1757 -> apparent within-doc "
            "rise is a generic order effect (LCCP running transitivity prior), not the carried model; margin-slope "
            "+0.0293 CI [-0.2322,+0.4106] spans 0, sign-flips to -0.134 at smoke (also spans 0), robustly null. (5) "
            "Slice-robust: negative holds at smoke + full. EXTENDS LCCP 29338 (already 'does not compound') to the "
            "carried-topical-cue case. Counts toward CERT as a proven negative that CLOSES the within-document "
            "topical-situation-model-cue direction. Local-only; needs orchestrator store sync."),
        "framing_correction_vs_director": (
            "Director framed this as HARD_FAIL_CCL on both axes + asked to confirm the negative is REAL (not harness "
            "bug / too-weak implementation) and the compounding construct-validity kill is decisive. RESULT: "
            "CONFIRMED, with two sharpenings. (A) ANGLE-1 is REAL BOUND, not weak-implementation: the cue is fair, "
            "competent, and active (swept doc_weight, causal, real content centroids) -- but off-code the 3 within-"
            "frame flips it makes are ALL TP->fp (it displaces correct patients with topically-salient-but-wrong "
            "ones). The precise mechanism is TOPICALITY ORTHOGONAL TO ARGUMENT-ROLE, not 'weak cue vs strong local "
            "cue'. FRAMING CORRECTION to the cell's brain-check story: n_defer=0, the DEFER guard NEVER fired, so the "
            "failures are the doc cue WINNING and mis-selecting, NOT the base resisting -- the negative is STRONGER "
            "(the cue is anti-correlated with correctness on influenced decisions), not merely a weak-cue null. (B) "
            "AXIS-2 kill is airtight: ARM-A control slope +0.189 >= C +0.176, so 'improving as it reads' exists in the "
            "no-situation-model baseline (from the LCCP subcat/transitivity prior) and is NOT attributable to the "
            "carried model; the doc-coh margin CI genuinely spans 0 at BOTH slices (sign-flips), robustly null. (C) "
            "The redirect (compounding -> cross-document schema-fit-gated consolidation) is SOUND -- within-document "
            "compounding has no human precedent and failed here; the Matthew effect is cross-session -- BUT it must "
            "carry a STRUCTURED (role/event-binding) signal, not a topical centroid, or it re-hits the same wall. (D) "
            "SCOPE GUARD: this closes the TOPICAL-cue instantiation, NOT structured situation models; and 0.50 is a "
            "real bound for THIS mechanism class, NOT a proven universal ceiling (single-annotator caveated gold + "
            "noisy extractions). Genuine credit preserved: a clean, well-controlled negative that closes a direction + "
            "redirects -- exactly the discipline; exp_dev CREDITED for the ARM-A control, the doc_weight sweep, the "
            "brain-check, can-fail-both-ways, Gate-D, and byte-repro."),
        "cross_arc_overlap_check": XARC,
        "net_cert_delta": ("+1 proven-negative (within-document topical situation-model DOCUMENT-COHERENCE cue does NOT "
                           "raise argument-extraction precision -- drops LCCP 0.500 to 0.456, robust across doc_weight, "
                           "because topicality is orthogonal to argument-role and the cue anti-selects -- AND does NOT "
                           "compound within-document, the apparent rise being a generic order effect from the LCCP "
                           "transitivity prior (ARM-A control-killed). Direction CLOSED for the topical-cue "
                           "instantiation; revival = structured role-binding carry + cross-document consolidation for "
                           "the compounding axis)."),
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
    print("=== A5 atom-write: compress_and_carry_comprehension_loop_ccl_v1 -> HARD_FAIL / honest-negative (2026-07-19) ===")
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
    print("ATOM (HARD_FAIL / honest-negative):", atom["id"][:110], "...")


if __name__ == "__main__":
    main()
