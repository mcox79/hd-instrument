"""
A5-gated atomization: exp_active_learning_loop_gap_detect_lookup_revise_v1 (smoke, local, uncommitted)
-> ONE atom (2026-07-20). MEASURED_MECHANISM (construction-validated wiring proof; positive-control class).

Author verdict HARD_PASS -> HARDEST scrutiny (Director over-read ~a dozen positives this session; HARD_PASS
on the active-learning LOOP must be adversarially verified before banking). Author was already honest
(flagged clean-wiring proof not capability win, disclosed a NO_EVIDENCE blind spot, recommended NOT scaling).
Auditor CONFIRMS that framing and TIERS DOWN from any capability read: this is a genuine architecture/wiring
validation + a load-bearing-gate demonstration + a real glass-box invariant, IN A CONSTRUCTION-DETERMINED
CLEAN REGIME -- NOT a capability chain-grade. GATED_CLEAN=1.000 and gap=+0.583 are FORCED by construction.

INDEPENDENT RECOMPUTE (.venv Scripts/python, off-disk, NOT verdict_msg; Fix #28). Smoke re-run reproduced
BIT-EXACT (PASSIVE=0.417 GATED_CLEAN=1.000 gap +0.583; GATED_BADSOURCE=0.417 UNGATED_BADSOURCE=0.000
margin +0.417; reject clean 0.000 bad 1.000; RANDOMIZED delta -0.028; GAP_NO_LOOKUP +0.000; learning-curve
occ2 +0.556; glassbox_hits 0; arms_differ_verified True; provenance_complete True, 270 records). Then five
decisive questions probed independently by rebuilding the item set and interrogating the construction:

Q1 CONSTRUCTION-DETERMINISM (the #1 risk): CONFIRMED. classify_gloss(true_gloss)==true_cat for ALL 48/48
  glosses (self-test even ASSERTS this round-trip), so GATED_CLEAN=1.000 is GUARANTEED by construction -- the
  fact list was authored so each gloss carries the SAME hand-built keyword classifier's category-diagnostic
  keywords (e.g. ANIMAL[0] pangolin gloss hits creature/nocturnal/preys/offspring). The verbatim guard DOES
  hold (0/48 glosses contain their own category NAME), so it is not literal-name match -- but it is
  category-diagnostic-KEYWORD match, an obfuscated hand-off. PASSIVE is a FAIR baseline in DIRECTION
  (15/18 AMBIGUOUS items are genuine 2-way sibling ties, all 6 NO_EVIDENCE have all-zero context scores =>
  genuinely under-determined; conformal set sizes exactly STRONG=1/AMBIG=2/NO_EV=0/MALF=4 as designed). BUT a
  minor construction blemish: the AMBIGUOUS template string contains the word "expedition", which is itself a
  DISTINCT PLACE cue -> every AMBIGUOUS sentence gives PLACE +1, making PASSIVE DETERMINISTIC on 6/18 items
  (3 PLACE forced-correct, 3 EMOTION forced-wrong) instead of a coin-flip. This SELF-CANCELS (PASSIVE stays
  ~0.50 on ambiguous) and does NOT bias the GATED_CLEAN gap, so it is a blemish not a fairness breach.
  NET: the ACTIVE-vs-PASSIVE gap is REAL IN SIGN (lookup content resolves context-underdetermination) but its
  MAGNITUDE (+0.583, GATED_CLEAN=1.000) is CONSTRUCTION-SET, not a measured capability. This CAPS the tier.

Q2 MUST-FAIL #2 non-vacuous?: FIRES and is load-bearing IN THE WIRING SENSE (disabling the gate on bad
  content moves the outcome 0.417 -> 0.000), but the discrimination is TRIVIAL BY CONSTRUCTION, not graded
  reliability. bad_gloss classifies to a WRONG category 48/48 and lands INSIDE the true sibling pair 0/48
  (maximally, deterministically wrong content), AND the reliability draw is hardwired-separated
  (rel_good 0.762/0.810/0.786 always >=0.5; rel_bad 0.143/0.381/0.238 always <0.5; P_GOOD=0.85 vs P_BAD=0.25).
  So BOTH gate channels (coherence: bad cat outside candidate set; reliability: bad below threshold) reject the
  bad source by construction. The control is NON-vacuous (removing the gate really tanks accuracy to 0) but the
  DIFFICULTY is trivial -- it validates the WIRING (gate is load-bearing), NOT graded reliability estimation on
  hard/near-threshold cases.

Q3 GLASS-BOX real?: property HOLDS. Manual full-import audit: only argparse/hashlib/json/os/platform/sys/time/
  traceback/datetime + torch + hdlab.conformal (real production calibrate_quantile, line 29 of hdlab/conformal.py)
  -- ZERO network on the accept/reject/revise path (classify_gloss + coherence + reliability are pure in-process
  dict/torch). Independent full-source scan: forbidden substrings occur ONLY inside the FORBIDDEN_SUBSTRINGS
  literal + docstring prose; subprocess/http:///https:///eval(/exec( all 0. CAVEAT (auditor-added): the cell's
  own glassbox_scan() BLANKET-EXEMPTS the first 2500 chars (to avoid self-matching the docstring), which bleeds
  into the import region (~line 40) -- a real coverage GAP: a network import placed in the first ~2500 chars
  would be MISSED. No such import exists here, so the property is true, but the automated scanner is weaker than
  a full-coverage scan and should be tightened (exempt only string-literal contexts, not a char-offset window).

Q4 DISCLOSED BLIND SPOT impact: REAL and BOUNDED, does not undermine any wiring band. For NO_EVIDENCE
  (empty candidate set), coherence = (set_size==0) auto-passes, so a real-but-irrelevant lookup slips through on
  the reliability channel ALONE. Recompute per sub-slice (seed7): RANDOMIZED == PASSIVE on AMBIGUOUS (unrelated
  gloss classifies OUTSIDE candidate set -> incoherent -> rejected -> passive fallback), and RANDOMIZED <= PASSIVE
  on NO_EVIDENCE (accepted-wrong -> loses PASSIVE's ~1/6 chance hits). Net 3-seed band4_delta_randomized = -0.028,
  well inside the +/-0.10 tolerance, so the randomized control still PASSES (no gain from more text). The blind
  spot would matter for a REAL-NOISE capability claim (coherence as built is candidate-set-membership only, not a
  content-relevance check), and is correctly disclosed by the author.

Q5 ARMS-DIFFER exemptions legit?: YES, all 4 follow from mechanism, none masks a wiring bug. PASSIVE==GAP_NO_LOOKUP
  (gap logged, no lookup -> passive fallback); PASSIVE==GATED_BADSOURCE (gate rejects bad on both channels ->
  passive fallback everywhere); GAP_NO_LOOKUP==GATED_BADSOURCE (follows); GATED_CLEAN==UNGATED_CLEAN (clean lookups
  accepted identically, zero false-rejects). The 4 must-DIFFER pairs are distinct via sha256 prediction-vector
  hashes in metrics.json (GATED_CLEAN vs PASSIVE/UNGATED_BADSOURCE, GATED_BADSOURCE vs UNGATED_BADSOURCE,
  UNGATED_BADSOURCE vs PASSIVE).

TIER: MEASURED_MECHANISM -- construction-validated WIRING PROOF (positive-control class). NOT a CG. What IS banked:
  (i) the active-learning loop is CORRECTLY WIRED end-to-end (gap-detect via conformal 3-way set-size split ->
  internal-retrieve codebook dict -> external lookup -> reliability+coherence gate -> provenance-revise), verified
  across 7 conditions x 3 seeds, cardinality clean (21/21), arms-differ verified; (ii) the gate is LOAD-BEARING
  not decorative (must-fail #2 fires: ungated bad content 0.417->0.000); (iii) the glass-box invariant HOLDS
  (zero external-LLM/network on the reasoning path, manually verified); (iv) the learning-curve mechanism is
  mechanically real (a fact banked at occurrence-1 is reused via internal-retrieve at occurrence-2 with zero new
  lookup: occ2 GATED_CLEAN 1.000 vs PASSIVE 0.444); (v) real production conformal import exercised; provenance
  complete (270 records, all 4 fields). What is NOT banked: NO capability claim (GATED_CLEAN=1.000, gap +0.583,
  UNGATED_BADSOURCE=0.000 are all CONSTRUCTION-DETERMINED); NO graded-reliability claim (hardwired-separated,
  not estimated on hard cases); NO real-corpus / noise-robustness claim; the NO_EVIDENCE coherence blind spot is
  unpatched; common-mode/multi-source (29378) not exercised. CERT delta: +0 CAPABILITY -- this is a wiring/
  positive-control validation that de-risks the architecture, NOT capability progress. Counts as a proven-bound
  mechanism record.

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
ATOMIZED_BY = ("skunkworks_landed_vet_active_learning_loop_gap_detect_lookup_revise_v1_MM_construction_validated_"
               "wiring_proof_gate_load_bearing_glassbox_holds_NOT_capability_CG_gated_clean_1p000_construction_"
               "forced_2026-07-20")
ATOMIZED_DATE = "2026-07-20"
ANCHOR = "exp_active_learning_loop_gap_detect_lookup_revise_v1"
CELL_COMMIT = None  # smoke-only, local, uncommitted per prereg contract (no push, no queue_add)

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

XARC = (
    "substrate_query 'active learning loop gap detect external lookup reliability gate provenance revise "
    "glass-box' -> top hit cosine=0.2686 (generic 'reliability' wordnet/concept node), 0.2617 'Provenance gates' "
    "(ingest pre-reg notes); NO prior EXPERIMENT-cell atom at cosine>0.30. The exp_dev prereg's own check found "
    "top hit 0.3057 (PROACTIVE_GAP_LOOP cleanup-margin-as-gap-signal, 2026-06-14) -- a RELATED but DISTINCT prior "
    "mechanism (routing/refuse via cleanup-margin, NOT external-lookup+reliability-gate+provenance-revise). This "
    "is a genuine new integration cell composing already-VET'd components (metacognition/abstain 29367/29370, "
    "reliability-gate 29376, codebook 29368), NOT a rediscovery. NONE at cosine>0.30 for the compound loop."
)

ATOM_ID = (
    "math::MEASURED_MECHANISM_active_learning_loop_gap_detect_internal_retrieve_external_lookup_reliability_"
    "coherence_gate_provenance_revise_v1_CONSTRUCTION_VALIDATED_WIRING_PROOF_positive_control_class_NOT_capability_"
    "CG_author_HARD_PASS_confirmed_as_wiring_not_capability_LOOP_CORRECTLY_WIRED_end_to_end_7cond_x_3seed_21of21_"
    "cardinality_arms_differ_verified_GATE_LOAD_BEARING_mustfail2_fires_ungated_badsource_0p417_to_0p000_GLASSBOX_"
    "HOLDS_zero_network_on_accept_reject_revise_path_learning_curve_MECHANICALLY_REAL_occ2_gated_clean_1p000_vs_"
    "passive_0p444_banked_fact_reused_via_internal_retrieve_zero_new_lookup_real_conformal_calibrate_quantile_"
    "import_provenance_270_records_complete_BUT_GATED_CLEAN_1p000_and_gap_plus0p583_CONSTRUCTION_DETERMINED_"
    "classify_gloss_true_gloss_eq_true_cat_48of48_selftest_asserts_roundtrip_verbatim_guard_holds_0of48_but_"
    "keyword_handoff_UNGATED_BADSOURCE_0p000_construction_forced_bad_gloss_wrong_48of48_in_sibling_0of48_reliability_"
    "hardwired_separated_good_0p76_0p81_always_ge0p5_bad_0p14_0p38_always_lt0p5_NOT_graded_PASSIVE_fair_in_direction_"
    "15of18_ambiguous_genuine_ties_no_evidence_all_zero_but_expedition_cue_leak_in_ambiguous_template_3_place_forced_"
    "win_3_emotion_forced_loss_SELF_CANCELS_NO_EVIDENCE_coherence_blind_spot_real_bounded_randomized_delta_neg0p028_"
    "in_band4_glassbox_scanner_exempts_first_2500_chars_coverage_gap_no_violation_exists_CERT_plus0_capability_"
    "SCOPED_construction_determined_clean_regime_real_data_noise_robustness_graded_reliability_UNTESTED_LOCAL_ONLY_"
    "2026-07-20"
)

PLAIN = (
    "We wanted to prove that a 'know-when-you-don't-know, go look it up, check the source, and only then update' "
    "loop is wired up correctly and honestly. On a small hand-built test the loop scored perfectly (100%) versus "
    "a passive reader's 42%, and the trust-gate correctly threw out a deliberately bad source (dropping a "
    "no-gate version to 0%). The honest reading: those exact numbers are BAKED IN by how the test was built. The "
    "'look it up' answers were written so the reader's own keyword-matcher always classifies them to the right "
    "category (the self-test even checks this), so the 100% is guaranteed, not earned; and the 'bad source' "
    "answers were written to always be maximally wrong, with a trust score hardwired below the accept threshold, "
    "so the gate catching them is guaranteed too. So what IS genuinely proven: the loop's plumbing is correct "
    "end-to-end, the trust-gate is load-bearing (removing it really does let bad information through and wreck "
    "the result), the whole reasoning path uses no external AI or network calls (a real, checked property), and "
    "the memory genuinely works -- a fact learned once is reused later without a fresh lookup. What is NOT "
    "proven: that any of this helps on real, noisy text, or that the trust score can be ESTIMATED on hard cases "
    "(here good and bad sources are trivially far apart). It is a clean wiring/positive-control proof, exactly as "
    "the author said -- not a capability win. It should NOT be scaled or cited as 'active learning improves "
    "reading' until it is re-run with a real lookup source that does not hand over the answer."
)

IMPORTANCE = (
    "MEDIUM (de-risking, not capability). This validates the ARCHITECTURE and control logic of the missing "
    "active-learning loop (gap-detect -> internal-retrieve -> external-lookup -> reliability/coherence-gate -> "
    "provenance-revise), and confirms the three load-bearing invariants a real version must keep: the gate is "
    "load-bearing (must-fail #2 fires), the glass-box property holds (no external LLM/network on the accept/"
    "reject/revise path), and internal-retrieve genuinely banks-and-reuses facts (the learning-curve mechanism is "
    "real). That de-risks building the real-data version on top. Importance is CAPPED because every headline "
    "number is construction-determined: it proves the WIRING is sound, not that active learning is a capability. "
    "It must NOT be over-read (the session's recurring failure mode) as evidence the self-monitoring/learning "
    "layer works on real data."
)

ATOM_CLAIM = (
    "MATH MEASURED_MECHANISM (construction-validated WIRING PROOF, positive-control class; NOT a capability CG). "
    "CLAIM: the active-learning loop -- gap-detect (conformal/Chow 3-way set-size split via real hdlab.conformal."
    "calibrate_quantile) -> internal-retrieve (per-condition codebook dict) -> external-lookup (in-process "
    "controlled fact list; data/wordnet_cache empty at snapshot) -> reliability+coherence gate -> provenance-"
    "revise -- is CORRECTLY WIRED end-to-end and its gate is LOAD-BEARING, verified across 7 conditions x 3 seeds "
    "(cardinality 21/21, arms_differ_verified True, provenance_complete 270 records). Smoke reproduced BIT-EXACT "
    "off-disk: PASSIVE=0.417, GATED_CLEAN=1.000 (gap +0.583); GATED_BADSOURCE=0.417 vs UNGATED_BADSOURCE=0.000 "
    "(margin-of-margins +0.417); reject_rate clean 0.000 bad 1.000; RANDOMIZED delta -0.028; GAP_NO_LOOKUP +0.000; "
    "learning-curve occ2 GATED_CLEAN 1.000 vs PASSIVE 0.444 (+0.556); glassbox_hits 0. AUDITOR TIER "
    "(MEASURED_MECHANISM, tiered DOWN from any capability read, CONFIRMING the author's own honest framing): the "
    "loop WIRING + load-bearing-gate + glass-box invariant + learning-curve mechanism are all VALIDATED, but in a "
    "CONSTRUCTION-DETERMINED CLEAN REGIME. THE #1 RISK CONFIRMED: GATED_CLEAN=1.000 is FORCED by construction -- "
    "classify_gloss(true_gloss)==true_cat for ALL 48/48 glosses (self-test asserts this round-trip); the verbatim "
    "guard DOES hold (0/48 glosses contain their own category name) so it is not literal-name match, but the "
    "glosses carry the SAME hand-built classifier's category-diagnostic keywords (keyword hand-off). "
    "UNGATED_BADSOURCE=0.000 is ALSO construction-forced (bad_gloss classifies WRONG 48/48, inside sibling pair "
    "0/48 = maximally wrong) and the reliability separation is HARDWIRED (rel_good 0.762/0.810/0.786 always >=0.5; "
    "rel_bad 0.143/0.381/0.238 always <0.5) -- so the gate fires for a TRIVIAL by-construction reason, validating "
    "wiring NOT graded reliability. PASSIVE is a FAIR baseline in DIRECTION (15/18 AMBIGUOUS are genuine 2-way "
    "sibling ties, all 6 NO_EVIDENCE have all-zero context scores) with a minor SELF-CANCELLING blemish (the "
    "AMBIGUOUS template word 'expedition' is a distinct PLACE cue -> 3 PLACE forced-correct + 3 EMOTION forced-"
    "wrong, PASSIVE stays ~0.50, gap not inflated). The DISCLOSED NO_EVIDENCE blind spot is REAL but BOUNDED "
    "(empty candidate set -> coherence auto-passes -> RANDOMIZED accepted via reliability alone -> net band4 delta "
    "-0.028, inside +/-0.10). Glass-box property HOLDS (only stdlib+torch+hdlab.conformal, zero network on the "
    "reasoning path) though the scanner blanket-exempts the first 2500 chars (a coverage gap; no violation "
    "exists). Arms-differ exemptions all mechanism-legit. WHAT IS BANKED: correct end-to-end wiring, load-bearing "
    "gate, glass-box invariant, mechanically-real learning-curve (banked fact reused via internal-retrieve with "
    "zero new lookup), real conformal import, complete provenance. WHAT IS NOT BANKED: any capability claim (all "
    "headline numbers construction-determined), graded-reliability, real-corpus/noise robustness; the coherence "
    "blind spot is unpatched and common-mode/multi-source (29378) is not exercised."
)

ATOM_RECOMPUTE = (
    "INDEP recompute (.venv Scripts/python, off-disk, NOT verdict_msg; Fix #28): "
    "(A) Smoke re-run BIT-EXACT: PASSIVE=0.4167, GATED_CLEAN=1.000 (gap +0.5833), UNGATED_CLEAN=1.000, "
    "GATED_BADSOURCE=0.4167, UNGATED_BADSOURCE=0.000, RANDOMIZED_LOOKUP=0.3889 (delta -0.0278), GAP_NO_LOOKUP="
    "0.4167 (delta +0.000); margin_of_margins +0.4167; reject clean 0.000 bad 1.000; occ2 GATED_CLEAN 1.000 vs "
    "PASSIVE 0.4444 (+0.5556); cardinality 21/21; arms_differ_verified True; provenance_complete True (270). "
    "(B) Q1 CONSTRUCTION: classify_gloss(true_gloss)==true_cat 48/48 (GATED_CLEAN=1.000 forced); verbatim "
    "violations 0/48; conformal set sizes STRONG=1 AMBIG=2 NO_EV=0 MALF=4 (goldilocks). PASSIVE fairness: "
    "AMBIGUOUS uniquely-context-resolvable 3/18 (the 3 PLACE items via the 'expedition' template cue-leak; the "
    "matching 3 EMOTION items are forced-WRONG -> self-cancels; other 12 are clean 2-way ties); NO_EVIDENCE "
    "all-zero-context True. (C) Q2 must-fail: bad_gloss classifies WRONG 48/48, in-sibling-pair 0/48; "
    "rel_good/rel_bad per seed {7:0.762/0.143, 13:0.810/0.381, 19:0.786/0.238} -- good always >=0.5, bad always "
    "<0.5 (hardwired, not graded). (D) Q4 blind spot (seed7): RANDOMIZED==PASSIVE on AMBIGUOUS (0.500/0.500), "
    "RANDOMIZED<=PASSIVE on NO_EVIDENCE; 3-seed band4 delta -0.028 (in-band). (E) Q3 glass-box: full-source scan "
    "-> forbidden substrings only in FORBIDDEN_SUBSTRINGS literal + docstring; subprocess/http:///https:///eval(/"
    "exec( all 0; import audit = stdlib+torch+hdlab.conformal only (real calibrate_quantile, hdlab/conformal.py:29). "
    "Scanner first-2500-char exemption bleeds into imports = coverage gap, no violation exists. (F) Q5 arms-differ: "
    "4 exemptions mechanism-legit; 4 must-differ pairs distinct via sha256 prediction-vector hashes."
)

ATOM_SCOPE = (
    "Construction-determined clean synthetic regime: 6-category taxonomy, 48 base + 6 dependent items, 4 context "
    "regimes (STRONG/AMBIGUOUS/NO_EVIDENCE/MALFORMED), hand-authored controlled fact list, 7 conditions, 3 seeds. "
    "LOAD-BEARING BOUNDS: "
    "(a) WIRING/POSITIVE-CONTROL PROOF, NOT A CAPABILITY WIN: the loop is proven correctly wired + the gate "
    "load-bearing + the glass-box invariant true, but GATED_CLEAN=1.000, gap +0.583, and UNGATED_BADSOURCE=0.000 "
    "are ALL construction-determined (the fact list is authored so true glosses classify correct via the same "
    "keyword classifier and bad glosses classify maximally wrong; reliability is hardwired-separated). Do NOT read "
    "as 'active learning improves reading' or 'the self-monitoring layer works'. "
    "(b) RELIABILITY IS NOT GRADED HERE: good vs bad sources are trivially far apart (P=0.85 vs 0.25, threshold "
    "0.5, always cleanly separated) -- the cell validates that a gate CAN reject a bad source, not that the "
    "substrate can ESTIMATE reliability on hard/near-threshold cases (that is the sibling cell's job, atom 29376). "
    "(c) COHERENCE BLIND SPOT (disclosed, unpatched): on empty-candidate-set (NO_EVIDENCE) items coherence "
    "auto-passes, so a real-but-irrelevant lookup is accepted on the reliability channel alone -- bounded here "
    "(net randomized delta -0.028, in-band) but a real gap for noisy data; fix = add a content-relevance check "
    "against the query context for the empty-set case. "
    "(d) GLASS-BOX SCANNER COVERAGE GAP: glassbox_scan() exempts the first 2500 chars (to avoid self-matching the "
    "docstring), which bleeds into the import region -- would MISS a network import placed there. No such import "
    "exists (property holds by manual audit), but the scanner should be tightened to string-literal contexts only. "
    "(e) NOT EXERCISED: common-mode/multi-source detector (29378, single source per item); real HD codebook/"
    "cleanup for internal-retrieve (plain dict here); real corpus / noise robustness. "
    "BRAIN-CHECK: the composed loop is brain-grounded (Loewenstein/Kidd-Piantadosi curiosity/Goldilocks gating; "
    "Baker&Brown/Palincsar internal-first fix-up escalation; Johnson&Seifert replacement-explanation revision with "
    "provenance) -- the ARCHITECTURE is faithful; this cell only proves the wiring of that architecture, not that "
    "the substrate realizes the capability on real input. REVIVAL/PROMOTE toward capability: re-run with (1) a "
    "real lookup source (populated wordnet_cache or an uncurated fact list) whose glosses are NOT authored to the "
    "classifier's keywords; (2) graded reliability estimated from noisy overlapping histories near threshold; "
    "(3) a content-relevance coherence check patching the NO_EVIDENCE blind spot; (4) real ambiguous corpus text. "
    "If the ACTIVE gap survives with the answer NOT handed by construction, upgrade toward CG."
)

ATOM_METRICS = {
    "PASSIVE_primary": 0.4167, "GATED_CLEAN_primary": 1.000, "band1_gap": 0.5833,
    "UNGATED_CLEAN_primary": 1.000, "GATED_BADSOURCE_primary": 0.4167, "UNGATED_BADSOURCE_primary": 0.000,
    "delta_bad": 0.4167, "delta_clean": 0.000, "band2_margin_of_margins": 0.4167,
    "reject_rate_clean": 0.000, "reject_rate_bad": 1.000, "band3_metric": 1.000,
    "RANDOMIZED_delta": -0.0278, "band4_in_band": True, "GAP_NO_LOOKUP_delta": 0.000,
    "learning_curve_occ2_gap": 0.5556, "occ2_GATED_CLEAN": 1.000, "occ2_PASSIVE": 0.4444,
    "cardinality": "21/21", "arms_differ_verified": True, "provenance_records": 270, "glassbox_hits": 0,
    "Q1_classify_true_gloss_eq_cat": "48/48 (GATED_CLEAN=1.000 construction-forced)",
    "Q1_verbatim_violations": "0/48", "Q1_ambiguous_uniquely_resolvable": "3/18 (self-cancelling PLACE cue-leak)",
    "Q1_no_evidence_all_zero_context": True,
    "Q2_bad_gloss_classifies_wrong": "48/48", "Q2_bad_gloss_in_sibling_pair": "0/48",
    "Q2_rel_good_per_seed": [0.762, 0.810, 0.786], "Q2_rel_bad_per_seed": [0.143, 0.381, 0.238],
    "Q2_reliability_hardwired_separated_not_graded": True,
    "Q3_glassbox_property_holds": True, "Q3_network_on_reasoning_path": 0,
    "Q3_scanner_first_2500_char_exemption_coverage_gap": True,
    "Q4_no_evidence_blind_spot_real_but_bounded_randomized_delta": -0.0278,
    "Q5_arms_differ_exemptions_all_mechanism_legit": True,
    "cell_verdict": "HARD_PASS",
    "auditor_tier": ("MEASURED_MECHANISM construction-validated wiring proof (positive-control class); NOT a "
                     "capability CG -- GATED_CLEAN=1.000 / gap +0.583 / UNGATED_BADSOURCE=0.000 all construction-"
                     "determined; wiring + load-bearing gate + glass-box + learning-curve genuinely validated"),
}

COMPOSES = [
    ("COMPOSES / INTEGRATION-VALIDATES (does NOT supersede) the already-VET'd components it wires together: "
     "metacognition/conformal abstain (atoms 29367/29370, chain-grade) as the gap-detect TRIGGER; the "
     "independent-channel reliability-gate pattern (atom 29376, real-data validated scale-bounded) as the trust "
     "layer -- NOTE this cell uses a HARDWIRED-separated reliability (P=0.85 vs 0.25), NOT 29376's derived "
     "estimate, so it validates gate WIRING not graded reliability; the learned codebook (atom 29368) is stood in "
     "by a plain dict for internal-retrieve. All parents stand on their own; this cell proves the compound loop's "
     "plumbing, not a new capability."),
    ("SIBLING of atom (attention_salience_reliability_gate_independent_channel_v1, CHAIN_GRADE, same day): that "
     "cell earned CG by DERIVING a leak-free reliability estimate on a non-ceiling task (AUC 0.686 below oracle "
     "0.698); THIS cell does the opposite on the reliability axis -- it uses a hardwired good/bad separation, so it "
     "is explicitly a WIRING proof not a derivation win. The two are complementary: 29376/the CG sibling proves "
     "reliability can be ESTIMATED; this proves the ESTIMATE can be routed into a gap-detect->lookup->revise loop."),
    ("credit: Loewenstein 1994 / Kidd-Piantadosi-Aslin 2012 (curiosity/Goldilocks gap-gating); Vovk-Gammerman-"
     "Shafer 2005 split-conformal + Chow 1970 reject-option (gap-detect); Baker&Brown 1984 / Palincsar&Brown 1984 "
     "(internal-first fix-up escalation); Johnson&Seifert 1994 (replacement-explanation revision with provenance). "
     "The cell AUTHOR (exp_dev) CREDITED for a clean, HONEST design and self-critique: pre-registered falsifiable "
     "bands, a mechanical verbatim-answer guard, a glass-box static scan, must-fail controls, AND explicit "
     "disclosure of the construction-determined nature + the NO_EVIDENCE blind spot + the recommendation NOT to "
     "scale. The auditor's tier-down to MEASURED_MECHANISM CONFIRMS rather than contradicts the author's framing."),
]

OVER_READS = [
    ("Do NOT read GATED_CLEAN=1.000 or gap +0.583 as a capability result. Both are CONSTRUCTION-DETERMINED: "
     "classify_gloss(true_gloss)==true_cat for all 48/48 glosses and the self-test ASSERTS this round-trip, so a "
     "perfect ACTIVE score is guaranteed by how the fact list was authored (glosses carry the same classifier's "
     "category-diagnostic keywords). The verbatim guard holding (no literal category name) does NOT make it a "
     "capability -- it is a keyword hand-off. Report as 'the ACTIVE-vs-PASSIVE gap is real in SIGN but "
     "construction-set in MAGNITUDE'."),
    ("Do NOT cite must-fail #2 (UNGATED_BADSOURCE=0.000) as proof of graded reliability discrimination. The bad "
     "source is maximally, deterministically wrong (48/48 wrong category, 0/48 near-miss) AND its reliability draw "
     "is hardwired below threshold (0.14-0.38 < 0.5 always). BOTH gate channels reject it by construction. It "
     "proves the gate is LOAD-BEARING (removing it tanks 0.417->0.000), NOT that the substrate can estimate "
     "reliability on hard cases."),
    ("Do NOT treat the glass-box scan's 0 hits as a full-coverage guarantee. The scanner blanket-exempts the "
     "first 2500 chars (docstring self-match avoidance), which bleeds into the import region and would MISS a "
     "network import placed there. The property genuinely holds by manual import audit (stdlib+torch+hdlab only), "
     "but the automated check is weaker than advertised and should be tightened."),
    ("Do NOT scale or dispatch a full run on this design expecting a capability signal -- the author explicitly "
     "recommended against it and the auditor agrees. The next step is a real lookup source that does not hand the "
     "answer, graded reliability, and a content-relevance coherence patch; only then is a capability claim "
     "testable."),
]

REVIVAL = [
    ("PROMOTE toward CG requires ALL of: (1) a REAL lookup source (populated data/wordnet_cache or a large "
     "uncurated fact list) whose glosses are NOT authored to the reader's own keyword classifier -- so GATED_CLEAN "
     "correctness is EARNED not asserted; (2) GRADED reliability estimated from noisy overlapping source histories "
     "near the threshold (not a hardwired 0.85-vs-0.25 gap) -- ideally wired to the derived channel of atom 29376 "
     "/ the same-day CG sibling; (3) a content-relevance coherence check patching the NO_EVIDENCE empty-candidate-"
     "set blind spot; (4) real ambiguous corpus text (noise-robustness). If the ACTIVE-vs-PASSIVE gap survives "
     "when the answer is NOT handed by construction, upgrade toward chain-grade."),
    ("HARDEN the internal-retrieve step onto the real HD codebook / cleanup memory (atom 29368) instead of a "
     "plain dict, and exercise the common-mode/source-independence detector (atom 29378) with multiple "
     "corroborating sources per item -- both are not exercised at this scale."),
    ("TIGHTEN the glass-box scanner: exempt only string-literal / comment contexts, not a fixed char-offset "
     "window, so a network import in the first ~2500 chars cannot be missed."),
]

GENUINE_POS = (
    "GENUINE positives preserved (symmetric anti-negativity): this is a REAL, clean architecture/wiring "
    "validation and I do NOT dilute what it earns. Independently verified off-disk: (1) the active-learning loop "
    "is CORRECTLY WIRED end-to-end across 7 conditions x 3 seeds (cardinality 21/21, arms-differ verified, "
    "provenance complete 270 records); (2) the reliability/coherence gate is LOAD-BEARING, not decorative -- "
    "must-fail #2 genuinely fires (disabling the gate on bad content moves the outcome 0.417 -> 0.000); (3) the "
    "glass-box invariant HOLDS -- zero external-LLM/network calls on the accept/reject/revise path, confirmed by "
    "manual import audit (only stdlib + torch + real hdlab.conformal.calibrate_quantile), a genuine and important "
    "property; (4) the learning-curve mechanism is MECHANICALLY REAL -- a fact banked at occurrence-1 is reused "
    "via internal-retrieve at occurrence-2 with zero new lookup (occ2 GATED_CLEAN 1.000 vs PASSIVE 0.444); (5) the "
    "author's design and self-critique are exemplary (pre-registered bands, verbatim guard, must-fail controls, "
    "explicit construction-determinism + blind-spot disclosure, correct recommendation not to scale). What this "
    "IS: a construction-validated wiring/positive-control proof that de-risks the loop ARCHITECTURE for a real-"
    "data build. What it is NOT (the scope that keeps it honest): a capability win -- GATED_CLEAN=1.000, "
    "gap +0.583, and UNGATED_BADSOURCE=0.000 are all construction-determined, reliability is hardwired-separated "
    "(not graded), and real-corpus / noise robustness / graded reliability are all UNTESTED. The auditor's tier-"
    "down to MEASURED_MECHANISM CONFIRMS the author's own framing; it does not contradict a genuine wiring win."
)


def build_atom():
    return {
        "id": ATOM_ID, "name": ATOM_CLAIM, "corpus": "math", "tier": "MEASURED_MECHANISM",
        "kind": "experiment_landed_vet",
        "cert_status": "proven-bound",
        "cert_class": ("active_learning_loop_gap_detect_lookup_reliability_coherence_gate_provenance_revise_"
                       "CONSTRUCTION_VALIDATED_WIRING_PROOF_positive_control_class_gate_load_bearing_glassbox_holds_"
                       "learning_curve_mechanically_real_NOT_capability_CG_gated_clean_1p000_and_ungated_badsource_"
                       "0p000_construction_determined_reliability_hardwired_separated_not_graded_real_data_noise_"
                       "robustness_UNTESTED"),
        "plain_language": PLAIN,
        "importance": IMPORTANCE,
        "description": (ATOM_CLAIM + "\n\nPLAIN LANGUAGE: " + PLAIN + "\n\nRECOMPUTE (off-disk .venv, Fix #28): "
                        + ATOM_RECOMPUTE + "\n\nHONEST SCOPE: " + ATOM_SCOPE),
        "aliases": [
            "active-learning loop gap-detect -> lookup -> reliability/coherence gate -> provenance-revise v1 (MM)",
            "construction-validated wiring proof / positive-control: loop wired, gate load-bearing, glass-box holds",
            "GATED_CLEAN=1.000 and gap +0.583 are CONSTRUCTION-DETERMINED (classify_gloss(true_gloss)==cat 48/48)",
            "must-fail #2 fires but trivially-by-construction (bad source maximally wrong + reliability hardwired)",
            "learning-curve mechanically real: banked fact reused via internal-retrieve, zero new lookup",
            "SCOPE: NOT a capability CG; real-data / noise-robustness / graded-reliability UNTESTED",
        ],
        "ts_iso": _iso, "ts": _ts,
        "serves_capability": "learning_and_self_monitoring_layer_active_learning_loop_architecture_validation",
        "metadata": {
            "provenance_quality": ("independent_venv_offdisk_smoke_rerun_bit_exact_plus_independent_item_set_"
                                   "rebuild_probing_classify_gloss_roundtrip_verbatim_guard_bad_gloss_classification_"
                                   "reliability_separation_no_evidence_blind_spot_subslice_full_source_network_scan_"
                                   "arms_differ_hashes"),
            "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes": None,
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_active_learning_loop_gap_detect_lookup_revise_v1_smoke/metrics.json",
            "plain_language": PLAIN, "importance": IMPORTANCE,
            "verified_off_data": ATOM_RECOMPUTE, "honest_scope": ATOM_SCOPE, "metrics": ATOM_METRICS,
            "over_reads_corrected": OVER_READS,
            "genuine_positives_symmetric_anti_negativity": GENUINE_POS,
            "revival_criteria": REVIVAL,
            "cross_arc_overlap_check": XARC,
            "construction_determinism_verdict": (
                "CONFIRMED (the #1 risk). GATED_CLEAN=1.000 is FORCED: classify_gloss(true_gloss)==true_cat 48/48, "
                "self-test asserts the round-trip, glosses carry the same classifier's category-diagnostic "
                "keywords (verbatim category-NAME guard holds 0/48, but it is a keyword hand-off). "
                "UNGATED_BADSOURCE=0.000 is FORCED: bad_gloss classifies WRONG 48/48, in-sibling-pair 0/48 "
                "(maximally wrong), reliability hardwired-separated (good>=0.5 always, bad<0.5 always). PASSIVE "
                "fair in DIRECTION (15/18 ambiguous genuine ties, NO_EVIDENCE all-zero) with a self-cancelling "
                "'expedition' PLACE cue-leak (3 forced-win + 3 forced-loss, gap not inflated). => wiring proof, "
                "not capability."),
            "glassbox_result": (
                "Property HOLDS by manual import audit (stdlib+torch+hdlab.conformal only, zero network on the "
                "accept/reject/revise path). Full-source scan: forbidden substrings only in FORBIDDEN_SUBSTRINGS "
                "literal + docstring; subprocess/http:///https:///eval(/exec( all 0. CAVEAT: cell's glassbox_scan() "
                "blanket-exempts first 2500 chars -> bleeds into import region -> would miss a network import "
                "there; no such import exists. Real production hdlab.conformal.calibrate_quantile exercised."),
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "construction_proof_not_capability_win_could_it_fail_informatively",
                "synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data",
                "positive_control_must_clear_its_own_floor_before_HF_or_capability_claim",
                "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
                "must_fail_control_non_vacuous_but_check_if_trivially_by_construction",
                "glassbox_invariant_is_a_testable_property_verify_full_coverage_not_superficial_grep",
                "substrate_kb_concept_overlap_check_on_schema_vet",
                "director_over_read_dozen_positives_this_session_VET_hardest",
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
        "author_verdict": "HARD_PASS",
        "verdict": ("MEASURED_MECHANISM_construction_validated_WIRING_PROOF_positive_control_class_NOT_capability_"
                    "CG_loop_correctly_wired_7cond_3seed_21of21_gate_LOAD_BEARING_mustfail2_fires_ungated_badsource_"
                    "0p417_to_0p000_glassbox_HOLDS_zero_network_learning_curve_mechanically_real_occ2_1p000_vs_"
                    "0p444_BUT_gated_clean_1p000_gap_0p583_ungated_badsource_0p000_all_CONSTRUCTION_DETERMINED_"
                    "classify_true_gloss_eq_cat_48of48_reliability_hardwired_separated_not_graded_no_evidence_"
                    "coherence_blind_spot_real_bounded_neg0p028_glassbox_scanner_2500char_coverage_gap_real_data_"
                    "UNTESTED"),
        "cert_increment_delta": 0,
        "decision": (
            "MEASURED_MECHANISM (construction-validated wiring proof, positive-control class). Author verdict "
            "HARD_PASS -> tiered DOWN from any capability read, CONFIRMING the author's own honest framing "
            "(clean-wiring proof not capability win; disclosed blind spot; recommended not to scale). Off-disk "
            "(.venv, Fix #28): (1) smoke reproduced BIT-EXACT (PASSIVE 0.417, GATED_CLEAN 1.000 gap +0.583, "
            "UNGATED_BADSOURCE 0.000, margin +0.417, occ2 +0.556, glassbox_hits 0, cardinality 21/21, arms-differ "
            "verified, provenance 270). (2) CONSTRUCTION-DETERMINISM CONFIRMED (the #1 risk): classify_gloss("
            "true_gloss)==true_cat 48/48 (self-test asserts round-trip) so GATED_CLEAN=1.000 is FORCED; verbatim "
            "guard holds 0/48 but it is a keyword hand-off; bad_gloss classifies wrong 48/48 in-sibling 0/48 and "
            "reliability is hardwired-separated (good>=0.5 always, bad<0.5 always) so UNGATED_BADSOURCE=0.000 and "
            "the must-fail firing are also construction-forced (validates WIRING/load-bearing gate, NOT graded "
            "reliability). (3) PASSIVE fair in direction (15/18 ambiguous genuine ties, NO_EVIDENCE all-zero) with "
            "a self-cancelling 'expedition' PLACE cue-leak that does not inflate the gap. (4) glass-box property "
            "HOLDS by manual audit (zero network on reasoning path) though the scanner exempts the first 2500 chars "
            "(coverage gap, no violation). (5) NO_EVIDENCE coherence blind spot real but bounded (randomized delta "
            "-0.028 in-band). (6) arms-differ exemptions all mechanism-legit; must-differ pairs distinct via hashes. "
            "BANKED: correct end-to-end loop wiring + load-bearing gate + glass-box invariant + mechanically-real "
            "learning-curve + real conformal import + complete provenance. NOT BANKED: any capability claim (all "
            "headline numbers construction-determined), graded reliability, real-corpus/noise robustness. CERT "
            "delta +0 capability (positive-control/wiring validation, de-risks architecture, not capability "
            "progress). Local-only; needs orchestrator store sync."),
        "framing_correction_vs_director": (
            "Director flagged a HARD_PASS on the active-learning LOOP and warned of ~a dozen over-read positives "
            "this session -- correctly. RESULT (symmetric): I DECLINE to grant capability CG and tier this "
            "MEASURED_MECHANISM (construction-validated wiring proof), which MATCHES the cell author's own honest "
            "framing rather than the HARD_PASS headline. The +0.583 ACTIVE-vs-PASSIVE gap and the perfect "
            "GATED_CLEAN=1.000 are CONSTRUCTION-DETERMINED (the fact list is authored so true glosses classify "
            "correct via the same keyword classifier -- the self-test asserts it -- and bad glosses classify "
            "maximally wrong with reliability hardwired below threshold). What is genuinely and independently "
            "banked: the loop is correctly wired end-to-end, the gate is LOAD-BEARING (must-fail #2 fires: "
            "0.417->0.000), the glass-box invariant HOLDS (zero network on the reasoning path, manually audited), "
            "and the learning-curve is mechanically real (banked fact reused, zero new lookup). What is NOT: any "
            "capability/real-noise claim, or graded reliability. exp_dev CREDITED for a clean, self-critical design "
            "(pre-registered bands, verbatim guard, must-fail controls, explicit construction + blind-spot "
            "disclosure, correct do-not-scale recommendation). Do NOT scale this design expecting a capability "
            "signal; the revival path is a real lookup source that does not hand the answer + graded reliability + "
            "a content-relevance coherence patch."),
        "cross_arc_overlap_check": XARC,
        "net_cert_delta": ("+0 CAPABILITY. Banks a construction-validated WIRING / positive-control proof: the "
                           "active-learning loop is correctly wired end-to-end, the reliability/coherence gate is "
                           "load-bearing (must-fail #2 fires), the glass-box invariant holds (zero network on the "
                           "reasoning path), and the learning-curve mechanism is mechanically real -- all in a "
                           "CONSTRUCTION-DETERMINED clean regime. NOT a capability chain-grade: GATED_CLEAN=1.000, "
                           "gap +0.583, and UNGATED_BADSOURCE=0.000 are all forced by construction, and reliability "
                           "is hardwired-separated not graded. De-risks the architecture for a real-data build; "
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
    print("=== A5 atom-write: active_learning_loop_gap_detect_lookup_revise_v1 -> MEASURED_MECHANISM (construction-validated wiring proof) (2026-07-20) ===")
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
    print("ATOM (MEASURED_MECHANISM):", atom["id"][:110], "...")


if __name__ == "__main__":
    main()
