"""
A5-gated atomization: exp_affectedness_change_of_state_patient_selection_design_gate_v1 (LOCAL working-tree,
HEAD ea5a35dca) -> ONE atom (2026-07-20). MEASURED_MECHANISM / proven-bound.

REVIVAL-of-HARD_FAIL, false-rescue risk -> HARDEST scrutiny. Cell verdict HARD_PASS_DESIGN_GATE (winner
SIG_COS_VERB_GATED_ONTOLOGY corr 0.3561). Auditor UPHOLDS that the design-gate PASS is REAL (survives the
decisive leakage killer) but BANKS MM not clean-CG: the HARD_PASS >=0.20 clearance is a CURATED / weak-sup
USE-win, NOT a derivation-win, and the >=0.20 number leans on at least one hand-curated component.

INDEPENDENT RECOMPUTE (.venv Scripts/python, off-disk, NOT verdict_msg; Fix #28):
  BASE reproduced EXACTLY off-disk (rebuilt the 225-cand / 44-gold slice from L.load_slice_and_reader +
    CPCL.build_candidates + L.match_pos, independent of stored metrics): COS_VERB_GATED corr=+0.3561,
    VERBNET_COS_GATED=+0.2213, PROTO_PATIENT_raw=+0.0755, PLACE_GAZETTEER=+0.1041. All match metrics.json.
  Q1 LEAKAGE (the killer): the NP-ontology buckets were assigned after an exploratory PEEK at this eval
    set's patient-word frequencies -> ground-by-X/grade-by-X risk. DECISIVE BLIND TEST: re-derive the NP
    ontology from WordNet lexname of the token's first noun sense (noun.artifact/food/substance +1.0,
    noun.animal/person +0.8, noun.body +0.6, noun.location -1.0, abstract lexnames -0.3) -- ZERO eval peek.
    WN_COS_GATED corr = +0.2732 (>= the 0.20 HARD_PASS floor). Does NOT collapse toward the text-internal
    null (0.044). WN raw ontology = +0.0363 (raw fails, same as hand raw 0.0755). Hand-vs-WN bucket sign
    agreement 50/61 (10 disagree e.g. book/kite/money WN->communication/possession, garden/room WN->
    artifact) yet the GATED signal still clears 0.20 despite the noisy independent bucketing -> NOT
    leakage-inflated to the point of circularity. LEAVE-ONE-LESSON-OUT (COS_VERB_GATED): corr 0.3341 / 0.3325
    / 0.3862 / 0.3619 / 0.3540 / 0.3579 / 0.3621 across the 7 held-out lessons -> rock-stable, no single
    lesson drives it. CONCLUSION: the curated affectedness signal SURVIVES the leakage test; not circular.
  Q2 CURATED vs DERIVED: winner SIG_COS_VERB_GATED_ONTOLOGY = hand-curated Dowty proto-patient NP ontology
    x hand-curated Levin change-of-state verb class = CURATED / weak-supervision. The genuinely TEXT-INTERNAL
    derivation (SIG_ALTERNATION_TEXT_INTERNAL: Levin causative-inchoative alternation scanned from the mining
    corpus, no lexicon) HARD_FAILED at corr +0.0443, and the scan was NON-VACUOUS (independently reran
    CELL.scan_alternation_evidence over the 4 mining files: 70/77 verbs with evidence, 1532 intransitive +
    207 passive hits). So text-internal DERIVATION of affectedness genuinely fails; only the INJECTED/curated
    signal tracks correctness. This CONVERGES with CPCL-v2 injected-vs-derived + the attention-gate
    construction-proof (29371): substrate USES a supplied signal it cannot DERIVE.
  Q3 BAND-FLOOR (VerbNet corroboration, 0.2213 = only 0.021 above the 0.20 floor): bootstrap 5000x over
    content candidates -> corr 0.2213, 95% CI [+0.013, +0.403], P(corr<=0)=0.018, P(corr<0.10)=0.126. The CI
    lower bound nearly touches zero and 12.6% of resamples fall below the middle-band floor -> VerbNet
    corroboration is POSITIVE but FRAGILE; its HARD_PASS label is not robust. Suggestive, not decisive.
  Q4 ROBUSTNESS: COS_VERB_GATED bootstrap corr 0.3561, 95% CI [+0.169, +0.507], P(<=0)=0.001, P(<0.10)=0.006
    -> robustly nonzero, BUT the CI lower bound (0.169) dips just below the 0.20 HARD_PASS floor. WN blind
    version 0.2732, 95% CI [+0.087, +0.448], P(<=0)=0.002, P(<0.10)=0.034. Selection-margin: winner sel_rate
    0.8235 vs chance 0.3829 = +0.4406 on 17 scored multi-rival groups (block-bootstrap over groups: mean
    +0.4398, 95% CI [+0.228, +0.615], P(<=0.10)=0.001 -> robust) BUT IDENTICAL to plain PLACE_GAZETTEER
    (+0.4406) and near PROTO_raw (+0.3818): the selection-rate is dominated by LOCATIVE EXCLUSION and is NOT
    specific to the COS-verb winner. DOUBLE-INDEPENDENT (WN ontology x VerbNet gate, both components blind) =
    +0.1443 = MIDDLE band. So the >=0.20 HARD_PASS requires at least one hand-curated component; with the most
    conservative independent inventory for BOTH, the signal is middle-band.

TIER: MEASURED_MECHANISM / proven-bound. The design-gate PASS is REAL and survives the decisive leakage
  killer (blind WordNet ontology 0.273 >> text-internal null 0.044; leave-one-lesson-out 0.33-0.39 stable;
  bootstrap robustly nonzero) -> NOT a false-rescue of a null, NOT HARD_FAIL. But it is a bounded CURATED /
  weak-supervision USE-win, NOT a derivation-win: (a) the genuinely text-internal derivation HARD_FAILED
  non-vacuously (0.044); (b) the raw NP ontology alone is ~0.04-0.08 -- the discriminative power is the
  CONJUNCTION (proto-patient NP AND change-of-state verb), consistent with Dowty/Levin theory; (c) the
  >=0.20 clearance leans on >=1 hand-curated component (double-blind = 0.144 middle-band); (d) the corr
  bootstrap CI dips below 0.20 and the selection-rate is non-specific (= locative exclusion). Honest cert =
  a proven, bounded GREEN-LIGHT: a curated affectedness signal DOES track per-instance patient-correctness
  (a weak-sup loop target is warranted), with the proven boundary that it must be INJECTED/curated (not
  text-derived) and its effect size is curation-dependent (~0.14 double-blind to ~0.36 fully hand-curated).
  CERT delta +1 MM.

LOCAL ONLY: store_head_at_write=unsynced_needs_orchestrator; NO origin push; NO remote persist; no git add -A.
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
ATOMIZED_BY = ("skunkworks_landed_vet_affectedness_change_of_state_patient_selection_design_gate_v1_MM_"
               "curated_signal_survives_leakage_blind_wordnet_0p273_derivation_failed_0p044_2026-07-20")
ATOMIZED_DATE = "2026-07-20"
ANCHOR = "affectedness_change_of_state_patient_selection_design_gate_v1"
CELL_COMMIT = "LOCAL_uncommitted_working_tree_HEAD_ea5a35dca"

FORENSIC_PARENT = ("math::HF_FORENSIC_cpcl_v2_entity_recurrence_reader_loop_component_audit_HONEST_NEGATIVE_"
                   "the_ENTITY_RECURRENCE_continuation_TARGET_is_UNCORRELATED_with_per_instance_PATIENT_"
                   "CORRECTNESS")  # prefix-match; direct parent forensic (corr~0 target, 6th self-sup fail)

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

XARC = (
    "substrate_query 'affectedness change of state proto-patient verb gated ontology patient selection "
    "curated leakage' -> top hit cosine 0.2949 entity 'patient_of' (WordNet cache), the medical/relational "
    "doctor-patient homonym cluster, NOT any prior experiment cell (our sense = direct-object/theme of a "
    "verb). NO experiment-cell hit >= 0.30. The direct parent is the CPCL-v2 forensic (entity-recurrence "
    "corr~0 null, 6th self-sup signal to fail the same residual), EXPLICITLY cited by the cell as its "
    "revival-prescription origin -- a deliberate targeted next-signal-class test (grounded/weak-sup "
    "affectedness), NOT a hidden rediscovery. Auditor accepts."
)

ATOM_ID = (
    "math::MM_affectedness_change_of_state_patient_selection_design_gate_v1_CURATED_WEAK_SUP_AFFECTEDNESS_"
    "SIGNAL_TRACKS_per_instance_PATIENT_CORRECTNESS_and_SURVIVES_LEAKAGE_but_DERIVATION_FAILED_winner_SIG_"
    "COS_VERB_GATED_ONTOLOGY_Dowty_proto_patient_NP_ontology_x_Levin_change_of_state_verb_class_corr_plus0p3561_"
    "REPRODUCED_offdisk_225cand_44gold_100content_DECISIVE_BLIND_LEAKAGE_TEST_reassign_NP_ontology_from_"
    "WORDNET_lexname_zero_eval_peek_WN_COS_GATED_corr_plus0p2732_STILL_clears_0p20_floor_does_NOT_collapse_"
    "toward_text_internal_null_0p044_leave_one_lesson_out_0p3341_to_0p3862_ROCK_STABLE_bootstrap_COS_95CI_"
    "0p169_to_0p507_Ple0_0p001_so_NOT_circular_NOT_leakage_inflated_to_circularity_BUT_it_is_a_CURATED_USE_"
    "WIN_NOT_a_DERIVATION_WIN_genuinely_TEXT_INTERNAL_alternation_scan_SIG_ALTERNATION_TEXT_INTERNAL_Levin_"
    "causative_inchoative_from_mining_corpus_no_lexicon_HARD_FAILED_corr_plus0p0443_scan_NON_VACUOUS_70of77_"
    "verbs_1532_intrans_207_passive_hits_so_text_derivation_of_affectedness_FAILS_only_INJECTED_curated_"
    "signal_tracks_correctness_CONVERGES_cpcl_v2_injected_vs_derived_plus_attention_gate_construction_proof_"
    "raw_NP_ontology_alone_0p0755_the_power_is_the_CONJUNCTION_proto_patient_NP_AND_change_of_state_verb_"
    "Dowty_Levin_consistent_gate_carries_load_DOUBLE_INDEPENDENT_WN_ontology_x_VERBNET_gate_both_blind_"
    "0p1443_MIDDLE_band_so_0p20_clearance_leans_on_ge1_handcurated_component_VERBNET_corroboration_0p2213_"
    "FRAGILE_95CI_0p013_to_0p403_Plt0p10_0p126_selection_margin_plus0p4406_ROBUST_block_bootstrap_0p228_to_"
    "0p615_BUT_NON_SPECIFIC_identical_to_plain_PLACE_GAZETTEER_exclusion_dominated_by_locative_exclusion_"
    "sanity_oracle_1p000_random_0p016_MM_proven_bounded_GREEN_LIGHT_curated_affectedness_is_a_valid_weak_sup_"
    "loop_target_bound_must_be_INJECTED_not_text_derived_effect_0p14_double_blind_to_0p36_full_handcurated_"
    "LOCAL_ONLY_2026-07-20"
)

ATOM_CLAIM = (
    "MATH MEASURED_MECHANISM (proven-bound). CLAIM: a design-gate measurement (measure ONLY, no loop built) "
    "on the SAME 225-reader-candidate / 44-gold / 100-content-scored held-out third-reader slice CPCL-v2 used "
    "shows that a CURATED / weak-supervised AFFECTEDNESS signal DOES track per-instance patient-correctness -- "
    "clearing the forensic VET's pre-registered correlation floor that all 6 prior self-supervised text-"
    "internal signals (cosine, animacy, coref, scene-coherence, thematic-fit, entity-recurrence) FAILED. "
    "The winner SIG_COS_VERB_GATED_ONTOLOGY (Dowty proto-patient NP ontology x Levin change-of-state verb "
    "class) reproduces corr=+0.3561 off-disk; VerbNet-gated variant +0.2213; sel_rate 0.8235 vs chance "
    "0.3829 (margin +0.4406). SANITY clean (oracle 1.000, random 0.016). "
    "AUDITOR TIER (BANKED MM, NOT clean CG): the gate PASS is REAL and SURVIVES the decisive LEAKAGE killer -- "
    "the NP-ontology buckets were assigned after an exploratory PEEK at this eval set's patient-word "
    "frequencies (ground-by-X/grade-by-X risk), so I re-derived the NP ontology BLIND from WordNet lexnames "
    "(zero eval peek): WN_COS_GATED corr=+0.2732 STILL clears the 0.20 floor and does NOT collapse toward the "
    "text-internal null (0.044); leave-one-lesson-out corr 0.33-0.39 rock-stable; COS bootstrap 95% CI "
    "[+0.169,+0.507], P(corr<=0)=0.001 -> NOT circular. BUT it is a CURATED / weak-sup USE-win, NOT a "
    "derivation-win: the genuinely TEXT-INTERNAL alternation-scan derivation (SIG_ALTERNATION_TEXT_INTERNAL, "
    "Levin causative-inchoative mined from the corpus, no lexicon) HARD_FAILED at corr +0.0443 with a "
    "NON-VACUOUS scan (70/77 verbs, 1532 intransitive + 207 passive hits) -- text-derivation of affectedness "
    "genuinely fails; only the INJECTED curated signal tracks correctness (CONVERGES with CPCL-v2 injected-vs-"
    "derived + the attention-gate construction-proof). Raw NP ontology alone is only ~0.08 -- the "
    "discriminative power is the CONJUNCTION (proto-patient NP AND change-of-state verb), Dowty/Levin-"
    "consistent, with the verb-gate carrying most of the load. Bounds on the strength: (i) DOUBLE-INDEPENDENT "
    "(WordNet ontology x VerbNet gate, both components blind) = +0.1443 = MIDDLE band, so the >=0.20 HARD_PASS "
    "requires at least one hand-curated component; (ii) the COS corr bootstrap CI lower bound (0.169) dips "
    "below 0.20; (iii) VerbNet corroboration (0.2213) is FRAGILE (95% CI [+0.013,+0.403], P(<0.10)=0.126); "
    "(iv) the selection-margin (+0.4406) is robust but NON-SPECIFIC -- IDENTICAL to plain locative-exclusion "
    "(PLACE_GAZETTEER +0.4406), i.e. driven by locative exclusion not by the COS-verb gating. Honest cert: a "
    "proven, bounded GREEN-LIGHT that a curated affectedness signal is a valid weak-sup loop target, with the "
    "proven boundary that it must be INJECTED/curated (not text-derived) and its effect size is curation-"
    "dependent (~0.14 double-blind to ~0.36 fully hand-curated)."
)

ATOM_RECOMPUTE = (
    "INDEP recompute (.venv Scripts/python, off-disk, NOT verdict_msg; Fix #28): "
    "(A) BASE reproduced EXACTLY by rebuilding the slice independently (L.load_slice_and_reader + gold + "
    "CPCL.build_candidates + L.match_pos -> 225 cands, 44 gold): COS_VERB_GATED corr=+0.3561, VERBNET_COS_"
    "GATED=+0.2213, PROTO_PATIENT_raw=+0.0755, PLACE_GAZETTEER=+0.1041 -- all match metrics.json. "
    "(B) LEAKAGE KILLER -- BLIND WordNet-derived NP ontology (lexname of first noun sense; noun.artifact/food/"
    "substance/object/plant +1.0, noun.animal/person +0.8, noun.body +0.6, noun.location -1.0, abstract "
    "lexnames -0.3; ZERO eval peek): WN_COS_GATED corr=+0.2732 (>= 0.20 floor); WN raw ontology=+0.0363; "
    "WN_VERBNET_GATED=+0.1443. Hand-vs-WN bucket sign agreement 50/61 (10 disagree e.g. book/kite/money/"
    "copybook, room/garden/fields) yet gated signal still clears 0.20 despite noisy independent bucketing. "
    "(C) LEAVE-ONE-LESSON-OUT (COS_VERB_GATED): 0.3341/0.3325/0.3862/0.3619/0.3540/0.3579/0.3621 across the 7 "
    "held-out lessons -> rock-stable, no single lesson drives it. "
    "(D) DERIVATION check -- independently reran CELL.scan_alternation_evidence over the 4 mining files: 70/77 "
    "verbs with evidence, 1532 intransitive + 207 passive hits (NON-VACUOUS); SIG_ALTERNATION_TEXT_INTERNAL "
    "corr=+0.0443 -> genuine text-internal derivation HARD_FAIL. "
    "(E) BOOTSTRAP (5000x over content candidates): COS_VERB_GATED corr 0.3561 95% CI [+0.169,+0.507] "
    "P(<=0)=0.001 P(<0.10)=0.006; VERBNET 0.2213 95% CI [+0.013,+0.403] P(<=0)=0.018 P(<0.10)=0.126 (FRAGILE); "
    "PROTO_raw 0.0755 95% CI [-0.119,+0.261] P(<=0)=0.218; WN_COS_GATED 0.2732 95% CI [+0.087,+0.448] "
    "P(<=0)=0.002 P(<0.10)=0.034. "
    "(F) SELECTION reproduced: COS sel_rate 0.8235 vs chance 0.3829 margin +0.4406 on 17 scored multi-rival "
    "groups; IDENTICAL to PLACE_GAZETTEER (+0.4406) and near PROTO_raw (+0.3818) -> NON-SPECIFIC (= locative "
    "exclusion). Block-bootstrap over groups: margin mean +0.4398 95% CI [+0.228,+0.615] P(<=0.10)=0.001 -> "
    "robust magnitude but not winner-specific. "
    "(G) SANITY: oracle corr 1.000, random |corr| 0.016 -- pipeline clean."
)

ATOM_SCOPE = (
    "McGuffey Third Reader (PG#14766, PD), lessons L04,L05,L07,L08,L09,L10,L12; SAME held-out slice + SAME "
    "independent single-annotator gold CPCL-v2 used (225 reader candidates, 44 gold-correct, 100 non-None "
    "content-scored). Design-gate MEASUREMENT ONLY -- NO loop, no training, pure deterministic lexicon lookup "
    "+ correlation/selection arithmetic. Load-bearing BOUNDS: "
    "(a) CURATED / WEAK-SUP USE-WIN, NOT A DERIVATION-WIN: the signal that clears the floor is a hand-curated "
    "(and WordNet/VerbNet-corroborated) ontology x verb-class LOOKUP; the genuinely text-internal derivation "
    "of the same affectedness (Levin alternation scan, no lexicon) HARD_FAILED non-vacuously (0.0443). The "
    "substrate can USE an injected affectedness signal it cannot DERIVE from raw text. "
    "(b) LEAKAGE SURVIVED BUT STRENGTH IS CURATION-DEPENDENT: the peeked NP-ontology is NOT circular (blind "
    "WordNet re-derivation holds at 0.273, leave-one-lesson-out stable), but the >=0.20 HARD_PASS clearance "
    "needs at least one hand-curated component -- the double-independent (WordNet ontology x VerbNet gate) "
    "version is 0.1443 (MIDDLE band). Report the effect as a band (~0.14 double-blind to ~0.36 fully hand-"
    "curated), NOT the single 0.356 headline. "
    "(c) CONJUNCTION, NOT NP ALONE: raw NP ontology corr ~0.04-0.08; the discriminative power is the verb-"
    "gated conjunction (proto-patient NP AND change-of-state verb), Dowty/Levin-consistent -- affectedness "
    "needs BOTH a proto-patient and a change-of-state predicate. "
    "(d) SELECTION-RATE NON-SPECIFIC: the +0.4406 selection margin is robust but IDENTICAL to plain locative "
    "exclusion; it does NOT discriminate the COS-verb winner and is dominated by excluding over-extracted "
    "locatives. Corroboration from VerbNet (0.2213) is FRAGILE (CI touches zero). "
    "(e) SMALL-N / SINGLE-ANNOTATOR: 100 content candidates, 17-19 multi-rival selection groups, one "
    "annotator; corr CI is wide (COS [0.169,0.507]). "
    "BRAIN-CHECK: affectedness / proto-patienthood (Dowty 1991 entailments; Talmy 1988 force-dynamics) IS a "
    "grounded semantic feature the brain uses for argument-role assignment, and the human system ACQUIRES it "
    "from grounded experience (seeing things change state), NOT purely from text distribution -- consistent "
    "with the text-internal derivation failing here while the injected/grounded signal succeeds. The honest "
    "brain-faithful reading: patient-selection needs a GROUNDED affectedness feature, which the substrate "
    "cannot bootstrap from raw text alone but CAN use once supplied. "
    "GREEN-LIGHT / NEXT: a weak-sup loop wired to a curated affectedness signal is WARRANTED (clears the "
    "design-gate) -- but (1) source BOTH the NP ontology and the verb class from independent inventories "
    "(WordNet + VerbNet) and accept the middle-band ~0.14 as the honest blind effect, or broaden coverage "
    "(only 44% of candidates got a non-None ontology score); (2) do NOT claim a text-DERIVED affectedness "
    "capability -- that failed; (3) the real remaining question is whether a GROUNDED (observed-event / "
    "labeled-patient) weak-supervision signal beats the curated-lookup ceiling, per the forensic's revival."
)

ATOM_METRICS = {
    "n_cands": 225, "n_gold": 44, "n_content_scored": 100, "coverage": 0.4444,
    "winner": "SIG_COS_VERB_GATED_ONTOLOGY",
    "winner_corr_reproduced": 0.3561, "verbnet_gated_corr": 0.2213,
    "proto_patient_raw_corr": 0.0755, "place_gazetteer_corr": 0.1041,
    "text_internal_alternation_DERIVED_corr": 0.0443,
    "alternation_scan_nonvacuous": "70/77 verbs with evidence, 1532 intransitive + 207 passive hits",
    "LEAKAGE_blind_wordnet_ontology_x_hand_verb_gate_corr": 0.2732,
    "blind_wordnet_raw_ontology_corr": 0.0363,
    "double_independent_wordnet_ontology_x_verbnet_gate_corr": 0.1443,
    "double_independent_band": "MIDDLE (0.10-0.20): >=0.20 clearance requires >=1 hand-curated component",
    "hand_vs_wordnet_bucket_sign_agreement": "50/61 agree, 10 disagree, 1 wn-missing",
    "leave_one_lesson_out_corr_COS": [0.3341, 0.3325, 0.3862, 0.3619, 0.3540, 0.3579, 0.3621],
    "bootstrap_COS_corr": {"point": 0.3561, "ci95": [0.169, 0.507], "P_le0": 0.001, "P_lt0.10": 0.006},
    "bootstrap_VERBNET_corr": {"point": 0.2213, "ci95": [0.013, 0.403], "P_le0": 0.018, "P_lt0.10": 0.126,
                               "note": "FRAGILE corroboration; CI nearly touches zero"},
    "bootstrap_WN_COS_corr": {"point": 0.2732, "ci95": [0.087, 0.448], "P_le0": 0.002, "P_lt0.10": 0.034},
    "selection_margin_winner": 0.4406, "selection_margin_place_gazetteer": 0.4406,
    "selection_margin_NON_SPECIFIC": "identical to plain locative exclusion; driven by locative exclusion",
    "selection_block_bootstrap_margin": {"mean": 0.4398, "ci95": [0.228, 0.615], "P_le0.10": 0.001},
    "sanity_oracle_corr": 1.0, "sanity_random_corr": 0.0162,
    "cell_verdict": "HARD_PASS_DESIGN_GATE (winner SIG_COS_VERB_GATED_ONTOLOGY 0.3561)",
    "auditor_tier": ("MEASURED_MECHANISM (proven-bound): design-gate PASS is REAL + survives the leakage "
                     "killer (blind WordNet 0.273, LOO stable), but a CURATED/weak-sup USE-win not a "
                     "derivation-win (text-internal derivation HARD_FAILED 0.044); >=0.20 leans on >=1 hand-"
                     "curated component (double-blind 0.144 middle-band); selection non-specific"),
}

COMPOSES = [
    ("EXTENDS the direct-parent CPCL-v2 forensic (" + FORENSIC_PARENT + " ...): that HARD_FAIL proved the "
     "entity-recurrence continuation target is UNCORRELATED with per-instance patient-correctness (corr~0, "
     "the 6th self-supervised text-internal signal to fail the same residual) and PRESCRIBED the exact revival "
     "gate THIS cell executes -- 'before wiring any candidate signal into a loop, measure corr(signal, gold-"
     "patient-correct) and require it clear a floor'. THIS cell answers that gate for the next signal CLASS "
     "(grounded/weak-sup affectedness, distinct in KIND from the 6 self-sup failures): a CURATED affectedness "
     "signal DOES clear the floor (0.273 blind), while a genuinely text-internal DERIVATION of the same "
     "affectedness does NOT (0.044). Does NOT supersede the forensic; it CLOSES the forensic's open revival "
     "question in the affirmative for the curated/injected case and in the NEGATIVE for the derived case."),
    ("CONVERGES with the INJECTED-vs-DERIVED pattern the substrate keeps showing: CPCL-v2 injected-vs-derived "
     "+ the attention-salience-reliability-gate CONSTRUCTION-PROOF (29371, MEASURED_MECHANISM: the gate is "
     "consolidation machinery that USES a supplied reliability signal, not a capability that DERIVES it). Same "
     "shape here: the substrate can USE a curated affectedness signal it cannot DERIVE from raw text. This is "
     "a recurring, load-bearing boundary of the current substrate -- signals must be injected/grounded, not "
     "bootstrapped from corpus statistics."),
    ("COHERES with the reader/argument-structure arc bound: the LCCP reader's per-instance patient extraction "
     "sits ~0.557 and the forensic showed the residual is a WRONG-TARGET (locative confound) problem. The "
     "selection-rate here being dominated by LOCATIVE EXCLUSION (curated gazetteer, +0.4406 identical to the "
     "full ontology) directly targets that confound -- the curated locative gazetteer does the selection work "
     "the self-supervised signals could not. But that is a CURATED patch, not a learned/derived fix."),
    ("credit: Dowty 1991 (proto-patient entailments); Talmy 1988 (force-dynamics); Levin 1993 (causative-"
     "inchoative alternation + verb classes); NLTK VerbNet (Kipper-Schuler) for the independent verb-class "
     "inventory; WordNet (Miller/Fellbaum) for the auditor's BLIND ontology re-derivation; McGuffey Third "
     "Reader (PD). Author (exp_dev) CREDITED for the honest design: pre-registered bands not tuned, sanity "
     "controls clean (oracle 1.000 / random 0.016), the text-internal derivation candidate included as a "
     "genuine can-fail (and it DID fail), the peek-then-relabel leakage risk SELF-FLAGGED in the prereg's "
     "non-construction guard, and the alternation-scan non-vacuousness checked before trusting its null. That "
     "honesty is what lets the leakage adjudication land cleanly."),
]

OVER_READS = [
    ("The verdict name HARD_PASS_DESIGN_GATE + the single 0.3561 headline OVER-READ the strength. Off-disk: "
     "the >=0.20 clearance requires at least one HAND-CURATED component -- with BOTH the NP ontology (WordNet) "
     "and the verb gate (VerbNet) independently sourced the corr is 0.1443 (MIDDLE band). Report the effect as "
     "a BAND (~0.14 double-blind to ~0.36 fully hand-curated), and label it a CURATED / weak-sup USE-win, NOT "
     "a text-derived affectedness capability."),
    ("Do NOT read the +0.4406 selection margin as evidence for the COS-verb-gated ontology specifically -- it "
     "is IDENTICAL to plain locative-exclusion (PLACE_GAZETTEER +0.4406) and is dominated by excluding over-"
     "extracted locatives. The selection metric does not discriminate the winner; the corr is the "
     "discriminating measure, and there the winner (0.356/0.273 blind) does separate from place-exclusion "
     "(0.104)."),
    ("VerbNet corroboration (0.2213, '0.021 above the floor') is FRAGILE, not solid: bootstrap 95% CI "
     "[+0.013,+0.403] nearly touches zero and P(corr<0.10)=0.126. Treat it as suggestive that the hand verb-"
     "list is not the whole story, NOT as an independent second HARD_PASS."),
    ("The leakage test PASSING does NOT license 'the substrate derives affectedness'. The opposite is proven: "
     "the genuinely text-internal derivation HARD_FAILED non-vacuously (0.0443). The win is entirely on the "
     "INJECTED/curated side. The honest capability claim is 'substrate USES a supplied affectedness signal', "
     "not 'substrate learns affectedness from text'."),
]

REVIVAL = [
    ("A weak-sup loop wired to a curated affectedness signal is WARRANTED (clears the design-gate) -- but "
     "source BOTH the NP ontology and the verb class from INDEPENDENT inventories (WordNet lexnames + VerbNet "
     "classids) and pre-register the honest blind effect (~0.14 middle-band), not the hand-curated 0.356. If "
     "the loop needs >=0.20, first broaden ontology coverage (only 44% of candidates got a non-None score) "
     "and re-measure blind."),
    ("The real open question the forensic named: does a GROUNDED (observed change-of-state event / labeled-"
     "patient weak-supervision) signal BEAT the curated-lookup ceiling? This cell only settles the curated-"
     "lookup + text-derived cases; a grounded-referent signal is the untested live option (text-derivation is "
     "now CLOSED-negative, non-vacuous)."),
    ("If a loop is built, hold out a SECOND corpus / independent gold to confirm the curated signal is not "
     "fit to this single-annotator 225-candidate slice -- the corr CI is wide (COS [0.169,0.507]) and the "
     "annotator is single. A genuinely held-out replication is the remaining leakage-robustness step."),
]

GENUINE_POS = (
    "GENUINE kernel preserved symmetrically (NOT dismissed as leakage): this is a REAL, non-circular positive "
    "result and the FIRST signal to clear the forensic's floor after 6 self-supervised failures. The decisive "
    "leakage killer PASSED cleanly -- re-deriving the NP ontology BLIND from WordNet lexnames (zero eval peek) "
    "holds the gated corr at 0.2732 (>= 0.20), it does NOT collapse toward the text-internal null (0.044), "
    "leave-one-lesson-out is rock-stable (0.33-0.39), and the bootstrap is robustly nonzero (P(corr<=0)=0.001). "
    "So the curated affectedness signal genuinely TRACKS per-instance patient-correctness -- a real green-light "
    "that a weak-sup affectedness loop is worth building, and a clean demonstration that the substrate can USE "
    "a grounded/injected feature it cannot DERIVE. The design is clean (sanity oracle 1.000 / random 0.016, "
    "pre-registered bands, a genuine text-internal can-fail that DID fail non-vacuously). The auditor's "
    "demotion to MM SHARPENS (curated-USE not derivation; band ~0.14-0.36 not single 0.356; selection non-"
    "specific; VerbNet fragile); it does NOT overturn the author's clean gate or the reality of the signal. "
    "What this IS: a proven, bounded green-light for a curated/weak-sup affectedness loop target. What it is "
    "NOT: a text-derived affectedness capability (that HARD_FAILED), nor a robust >=0.20 effect independent of "
    "all hand-curation (double-blind is middle-band)."
)


def build_atom():
    return {
        "id": ATOM_ID, "name": ATOM_CLAIM, "corpus": "math", "tier": "MEASURED_MECHANISM",
        "kind": "experiment_landed_vet",
        "cert_status": "proven_bound",
        "cert_class": ("curated_weak_sup_affectedness_signal_TRACKS_per_instance_patient_correctness_clears_"
                       "forensic_floor_after_6_self_sup_failures_winner_cos_verb_gated_ontology_corr_0p356_"
                       "SURVIVES_LEAKAGE_blind_wordnet_reassignment_0p273_LOO_stable_NOT_circular_BUT_a_"
                       "CURATED_USE_WIN_not_a_DERIVATION_WIN_text_internal_alternation_scan_HARD_FAILED_0p044_"
                       "nonvacuous_conjunction_np_and_cos_verb_carries_it_double_independent_wordnet_x_verbnet_"
                       "0p144_middle_band_so_0p20_needs_ge1_handcurated_component_selection_margin_nonspecific_"
                       "equals_locative_exclusion_verbnet_corroboration_fragile_proven_bounded_green_light_"
                       "weak_sup_loop_target_must_be_injected_not_text_derived"),
        "description": (ATOM_CLAIM + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + ATOM_RECOMPUTE
                        + "\n\nHONEST SCOPE: " + ATOM_SCOPE),
        "aliases": [
            "affectedness change-of-state patient-selection design-gate v1",
            "curated affectedness signal tracks patient-correctness (survives leakage, blind WordNet 0.273)",
            "curated USE-win not derivation-win: text-internal alternation derivation HARD_FAILED 0.044",
            "first signal to clear forensic floor after 6 self-supervised failures",
            "double-independent WordNet x VerbNet = 0.144 middle-band: >=0.20 needs >=1 hand-curated component",
            "selection margin non-specific (= locative exclusion); VerbNet corroboration fragile",
        ],
        "ts_iso": _iso, "ts": _ts,
        "metadata": {
            "provenance_quality": ("independent_venv_offdisk_recompute_rebuilt_slice_from_source_plus_blind_"
                                   "wordnet_ontology_leakage_test_plus_leave_one_lesson_out_plus_5000x_"
                                   "bootstrap_plus_independent_rerun_of_alternation_scan_plus_double_"
                                   "independent_wordnet_x_verbnet_control"),
            "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes": None,
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_affectedness_change_of_state_patient_selection_design_gate_v1/metrics.json",
            "verified_off_data": ATOM_RECOMPUTE, "honest_scope": ATOM_SCOPE, "metrics": ATOM_METRICS,
            "over_reads_corrected": OVER_READS,
            "genuine_positives_symmetric_anti_negativity": GENUINE_POS,
            "revival_criteria": REVIVAL,
            "cross_arc_overlap_check": XARC,
            "leakage_test_result": ("SURVIVES: blind WordNet-lexname NP-ontology re-derivation (zero eval "
                                    "peek) gated corr=+0.2732 >= 0.20; does NOT collapse to text-internal null "
                                    "0.044; leave-one-lesson-out 0.33-0.39 stable; bootstrap P(corr<=0)=0.001. "
                                    "NOT circular. BUT >=0.20 leans on >=1 hand-curated component (double-blind "
                                    "WordNet x VerbNet = 0.1443 middle-band)."),
            "curated_vs_derived": ("CURATED / weak-sup USE-win. Text-internal DERIVATION (Levin alternation "
                                   "scan, no lexicon) HARD_FAILED corr=+0.0443, scan NON-VACUOUS (70/77 verbs, "
                                   "1739 hits). Substrate USES an injected affectedness signal it cannot "
                                   "DERIVE from raw text."),
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "ground_by_X_grade_by_X_circularity_leakage_require_independent_blind_or_heldout",
                "construction_proof_not_capability_win_could_it_fail_informatively",
                "synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data",
                "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
                "every_negative_and_positive_brain_check_mechanism_vs_shortcut",
                "substrate_kb_concept_overlap_check_on_schema_vet",
                "vet_every_base_ingredient_fair_correct_brain_faithful_USER",
                "revival_of_hard_fail_false_rescue_risk_apply_hardest_scrutiny",
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
        "verdict": ("MEASURED_MECHANISM_proven_bound_CURATED_WEAK_SUP_AFFECTEDNESS_signal_TRACKS_patient_"
                    "correctness_clears_forensic_floor_winner_cos_verb_gated_ontology_0p3561_SURVIVES_LEAKAGE_"
                    "blind_wordnet_0p2732_LOO_stable_NOT_circular_but_CURATED_USE_WIN_not_DERIVATION_text_"
                    "internal_alternation_HARD_FAILED_0p0443_nonvacuous_double_independent_wordnet_x_verbnet_"
                    "0p1443_middle_band_selection_margin_nonspecific_equals_locative_exclusion_verbnet_fragile"),
        "cert_increment_delta": 1,
        "decision": (
            "MM (proven-bound). Cell verdict HARD_PASS_DESIGN_GATE CONFIRMED as a REAL, non-circular signal but "
            "BANKED MM not clean-CG. REVIVAL-of-HARD_FAIL, false-rescue risk -> hardest scrutiny. Off-disk "
            "(.venv, Fix #28): (1) BASE reproduced exactly by rebuilding the 225/44 slice from source. (2) "
            "LEAKAGE KILLER PASSED: the NP-ontology buckets were assigned after an eval-set peek; re-derived "
            "BLIND from WordNet lexnames (zero peek) -> WN_COS_GATED corr +0.2732 still clears 0.20, does NOT "
            "collapse to the text-internal null 0.044; leave-one-lesson-out 0.33-0.39 stable; bootstrap 95% CI "
            "[0.169,0.507] P(<=0)=0.001 -> NOT circular. (3) BUT a CURATED / weak-sup USE-win, NOT a derivation-"
            "win: the genuinely text-internal alternation-scan derivation HARD_FAILED 0.0443 with a NON-VACUOUS "
            "scan (70/77 verbs, 1739 hits). (4) STRENGTH BOUNDED: double-independent WordNet ontology x VerbNet "
            "gate = 0.1443 (MIDDLE band) -> >=0.20 needs >=1 hand-curated component; VerbNet corroboration "
            "fragile (CI [0.013,0.403], P(<0.10)=0.126); selection margin +0.4406 robust but NON-SPECIFIC "
            "(identical to plain locative exclusion). SANITY clean (oracle 1.000, random 0.016). Counts toward "
            "CERT as a proven-bound green-light for a curated/weak-sup affectedness loop target. Local-only; "
            "needs orchestrator store sync."),
        "framing_correction_vs_director": (
            "Director asked: is the HARD_PASS revival a real curated-signal win or leakage-inflated/circular? "
            "RESULT (symmetric): the decisive blind/held-out leakage test PASSED -- blind WordNet NP-ontology "
            "re-derivation holds at corr +0.2732 (>= 0.20), leave-one-lesson-out 0.33-0.39 stable, bootstrap "
            "robustly nonzero -> NOT circular, a REAL signal, the first to clear the forensic floor after 6 "
            "self-sup failures. I therefore do NOT HARD_FAIL it. But I BANK MM not clean-CG because the win is "
            "a CURATED / weak-sup USE-win (the genuinely text-internal DERIVATION HARD_FAILED non-vacuously at "
            "0.044) AND the >=0.20 HARD_PASS number leans on >=1 hand-curated component (double-independent "
            "WordNet x VerbNet = 0.1443 middle-band); the selection margin is non-specific (= locative "
            "exclusion) and VerbNet corroboration is fragile. Precise honest claim: a curated affectedness "
            "signal DOES track per-instance patient-correctness (weak-sup loop warranted), effect ~0.14 double-"
            "blind to ~0.36 fully hand-curated, with the proven boundary that it must be INJECTED/curated -- "
            "the substrate cannot DERIVE affectedness from raw text. Genuine positive preserved; exp_dev "
            "CREDITED for the clean design (pre-registered bands, sanity controls, a real text-internal can-"
            "fail that DID fail, self-flagged peek risk)."),
        "cross_arc_overlap_check": XARC,
        "net_cert_delta": ("+1 MM (curated/weak-sup affectedness signal tracks per-instance patient-"
                           "correctness; survives the blind-WordNet leakage test at 0.273 -> NOT circular; but "
                           "a curated USE-win not a text-derivation win -- derivation HARD_FAILED 0.044 -- and "
                           "the >=0.20 clearance leans on >=1 hand-curated component (double-blind 0.144 "
                           "middle-band). GREEN-LIGHT for a curated weak-sup affectedness loop; grounded-"
                           "referent signal remains the untested live option)."),
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
    print("=== A5 atom-write: affectedness_change_of_state_patient_selection_design_gate_v1 -> MM (curated signal survives leakage; derivation failed) (2026-07-20) ===")
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
    print("ATOM (MM):", atom["id"][:110], "...")


if __name__ == "__main__":
    main()
