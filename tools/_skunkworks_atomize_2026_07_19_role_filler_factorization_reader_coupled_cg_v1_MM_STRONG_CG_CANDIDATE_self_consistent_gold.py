"""
A5-gated atomization: exp_role_filler_factorization_reader_coupled_cg_v1 (LOCAL commit a3816adc2) -> ONE atom (2026-07-19).
  MEASURED_MECHANISM / proven-bound = STRONG-CG-CANDIDATE (ADVANCED). Cell verdict HARD_PASS_READING_AXIS_FIRST_CG.
  Auditor CONFIRMS the mechanism + the two gaps it fixes vs 29335 (reader-coupling + real-difficulty can-fail) BUT
  DEMOTES the verdict name from "reading-axis CG" to STRONG-CG-CANDIDATE on the exp_dev's self-flagged DEEPER caveat
  (confirmed off-code): the gold IS the reader's OWN memberships (self-consistent), so extraction-CORRECTNESS is
  invisible to the metric -- the algebra absorbs a wrong extraction cleanly. Reading-STRUCTURE coupled + real-
  difficulty can-fail = real advance; reading-CORRECTNESS = NOT measured -> not chain-grade.

INDEPENDENT RECOMPUTE (off-disk, .venv Scripts/python, Fix #28; NOT verdict_msg):
  - DETERMINISM: full run reproduced twice; aggregate + arms_differ_hashes byte-identical across runs (modulo ts/
    elapsed). OMP/MKL/OPENBLAS=1 set in-cell. Cross-seed factored_range @N40 real = 0.0225 (tight, cv<0.03).
  - SELF-CONSISTENCY (THE DECISIVE CAVEAT) confirmed OFF-CODE: eval_heldout builds S = encode_situation(assign) =
    sum bind(g_true[slot], x[filler]) where filler = the reader's own membership, then recovers argmax; the gold
    true_f = assign[s_star] = a (concept,slot) pair drawn from held_by_slot <- build_split(slot_fillers) <-
    reader's cached memberships. NO independent ground-truth text alignment ANYWHERE. The cache
    (data/_reader_extractions_third_reader_v1.json) stores ONLY reader output tuples (svo/goal/recipient/loc/poss/
    nest), NO gold annotation. Concretely-noisy extractions in the cache (e.g. ['acted','grandmother','lie'],
    ['admiring','frank','boy'|'flower'] over-extraction) become memberships treated as gold; the situation binds
    x[wrong_filler] into the slot and the FHRR unbind recovers it cleanly. So a WRONG extraction is scored
    "correct". Extraction-CORRECTNESS noise is ABSORBED BY CONSTRUCTION. CONFIRMED: the metric measures compgen on
    the reader's real noisy STRUCTURE, NOT whether the reader comprehended the text correctly.
  - TWO GAPS 29335 NAMED ARE DELIVERED (symmetric credit): (1) READING COUPLED -- relations are OUR reader's actual
    extractions on the McGuffey Third Reader (3823 tuples, 2355 svo, GloVe cov 0.97), not curated ConceptNet;
    V=207, 59 surviving slots. (2) REAL-DIFFICULTY CAN-FAIL -- realcost +0.091 at headline N=40,
    difficulty_is_capacity=False. Confirmed off-disk across the sweep: realcost +0.091(N40) +0.062(N48) +0.032(N64)
    +0.013(N96) +0.002(N128) 0(N192+). This is REAL content-confusability difficulty (real narrative vocab -- names
    james/john/george, pronouns you/we -- is MORE confusable than ConceptNet concepts) but it is the SAME
    MECHANISTIC CLASS 29335 characterized (content cost grows under capacity pressure, vanishes by mid-N); the
    advance is magnitude (0.091 vs ConceptNet 0.047) + a lower headline N=40 that clears the 0.05 flag. Both real
    and control saturate to 1.000 by N128-192. Honest: genuine real-difficulty signal, not a categorically new
    difficulty.
  - MUST-FAIL FAIR + FIRES: FLAT held-out 0.005 << chance 0.0625 (BELOW chance = genuine anti-generalization; the
    held filler is by construction atypical for the slot's trained fillers, so content-typicality points away),
    gap 0.818. Both arms use the identical pool (present m + top-KNN global content-neighbors). arms_differ hashes
    distinct (factored cacbcbd6.. vs flat 69c99174..). FAIR.
  - COHERENCE-GATE NULL genuine: gate_effect +0.004 at headline, and within +-0.007 (noise) across the WHOLE sweep;
    drops 19.4% of memberships as content-outliers with NO accuracy gain. Confirms the residual difficulty is
    content-confusability + sparsity, NOT droppable incoherent mis-extractions detectable by content-outlier
    scoring. And because gold = reader's own memberships, the gate CANNOT help correctness (no correctness signal
    to improve against). Repositions the gate: NOT for noise-tolerance (the algebra already absorbs it), but for
    extraction CORRECTNESS against an INDEPENDENT ground truth -- the real remaining gap.
  - SPLIT POWER adequate (refutes the "handful of slots" worry): build_split -> 203 held-out pairs across 53-55 of
    59 slots per seed; surviving-slot median 11 fillers (min_slot_fillers=8 floor); n_test=400 held-out evaluations.
    N=40 is the vector DIMENSION at the capacity edge (headroom F=0.823, not saturated), NOT test-set size; not
    under-powered. per-type: svo:OBJ F=0.819 (n~233), svo:SUBJ F=0.830 (n~156), recip:AGT 0.772 (n~10), recip:RECIP
    1.0 (n~6) -- the two big buckets carry it and both sit ~0.82.
  - WITNESS re-runs the REAL reader (nest ON) on a tiny text -> real svo ['chased','dog','cat'] -> FACTORED recovers
    held-out chase-OBJ=cat, FLAT fails. But NOTE: the witness held-out is ALSO self-consistent (trains chase-OBJ
    with 'ball', tests chase-OBJ=cat -- both defined by the test setup, not by what the text said). So the witness
    too demonstrates STRUCTURE generalization, not extraction correctness.
  - CROSS-ARC OVERLAP: substrate_query 'structure content factorization reader extraction compositional
    generalization' -> top hits are NOTE-level compgen concepts (cosine ~0.55), not rediscovering experiment cells.
    The two direct parents (29335 ConceptNet, 29334 realcontent) are EXPLICITLY cited by the cell -- deliberate
    targeted extension, not a hidden rediscovery.

TIER: MEASURED_MECHANISM / proven-bound = STRONG-CG-CANDIDATE (ADVANCED beyond 29335). NOT chain-grade. The
  factorization generalizes compositionally on OUR reader's REAL noisy extraction STRUCTURE with a genuine (modest)
  real-difficulty can-fail where flat anti-generalizes -- a real step past 29335's capacity-only headroom AND past
  its "no reading happened" count. BUT scored SELF-CONSISTENTLY (gold = reader's own memberships), so extraction-
  CORRECTNESS is NOT measured. "Reading-axis CG" would imply generalization over CORRECTLY-comprehended relations,
  which this test cannot establish. The ONE step to a TRUE reading-axis CG: INDEPENDENT ground-truth relations
  (hand-annotated / independent gold from the text) so the metric measures CORRECT comprehension, + the coherence-
  gate scored FOR correctness against that gold. CERT delta +1 MM.

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
ATOMIZED_BY = "skunkworks_landed_vet_role_filler_factorization_reader_coupled_cg_v1_MM_STRONG_CG_CANDIDATE_self_consistent_gold_extraction_correctness_unmeasured_2026-07-19"
ATOMIZED_DATE = "2026-07-19"
ANCHOR = "role_filler_factorization_reader_coupled_cg_v1"
CELL_COMMIT = "a3816adc2"

CONCEPTNET_PARENT = "math::MM_role_filler_factorization_conceptnet_cg_v1_CG_CANDIDATE_ADVANCED_learned_structure_content_factorization_content_blind_g"
REALCONTENT_PARENT = "math::MM_role_filler_factorization_realcontent_cg_v1_CG_CANDIDATE_structure_content_factorization_TRANSFERS_to_REAL_correlated_gro"

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

XARC = (
    "substrate_query 'structure content factorization reader extraction compositional generalization' -> top hits "
    "are NOTE-level compgen concepts (entity 'Compositional generalization' cosine ~0.556, 'Compositional "
    "generalization context' ~0.552), NOT prior experiment cells rediscovering the mechanism. The two direct "
    "parents -- 29335 (ConceptNet CG-candidate, c880a8680) and 29334 (realcontent CG-candidate, 8751c22d8) -- are "
    "EXPLICITLY cited by the cell and confirmed off-disk. This is a DELIBERATE targeted extension (couple OUR "
    "reader's real narrative extractions + measure real-difficulty), NOT a hidden rediscovery. Auditor accepts."
)

ATOM_ID = (
    "math::MM_role_filler_factorization_reader_coupled_cg_v1_STRONG_CG_CANDIDATE_ADVANCED_structure_content_"
    "factorization_LEARNED_content_blind_g_hat_plus_native_FHRR_bind_GENERALIZES_COMPOSITIONALLY_on_OUR_READERs_REAL_"
    "NOISY_EXTRACTION_STRUCTURE_McGuffey_Third_Reader_exp_read_nested_clause_relative_third_reader_v1_nest_ON_3823_"
    "tuples_2355_svo_GloVe_cov_0p97_slot_eq_verb_lemma_arg_role_V207_59_slots_REAL_F_heldout_0p823_N40_m6_chance_"
    "0p062_3seed_FLAT_0p005_BELOW_chance_genuine_anti_generalization_gap_0p818_where_FLAT_content_typicality_FAILS_"
    "svoOBJ_0p819_svoSUBJ_0p830_positive_control_synthetic_Gate_D_F_0p914_gap_0p900_reproduces_mechanism_at_reader_"
    "extracted_regime_must_fail_FIRED_TWO_GAPS_29335_NAMED_DELIVERED_1_READING_COUPLED_relations_are_OUR_readers_"
    "ACTUAL_extractions_not_curated_ConceptNet_2_REAL_DIFFICULTY_CAN_FAIL_realcost_plus0p091_N40_difficulty_is_"
    "capacity_FALSE_confirmed_sweep_plus0p091_N40_0p062_N48_0p032_N64_0p013_N96_vanishes_N192_real_narrative_vocab_"
    "names_pronouns_MORE_confusable_than_ConceptNet_SAME_mechanistic_class_content_cost_under_capacity_pressure_"
    "vanishes_mid_N_advance_is_magnitude_0p091_vs_0p047_plus_lower_headline_N40_BUT_DECISIVE_BLOCKER_SELF_CONSISTENT_"
    "GOLD_confirmed_off_code_gold_true_f_IS_the_readers_OWN_membership_situation_S_binds_x_filler_from_reader_output_"
    "then_unbinds_NO_independent_ground_truth_text_alignment_anywhere_cache_stores_ONLY_reader_tuples_no_gold_"
    "annotation_wrong_extraction_dog_chased_BALL_vs_text_CAT_still_binds_unbinds_cleanly_scored_correct_algebra_"
    "ABSORBS_extraction_correctness_noise_BY_CONSTRUCTION_so_metric_measures_compgen_on_readers_real_noisy_STRUCTURE_"
    "NOT_whether_reader_comprehended_CORRECTLY_reading_axis_CG_verdict_name_OVERCLAIMS_correctness_COHERENCE_GATE_"
    "NULL_plus0p004_headline_within_0p007_whole_sweep_drops_19p4pct_no_gain_gate_repositioned_for_extraction_"
    "CORRECTNESS_vs_independent_gold_NOT_noise_tolerance_algebra_already_absorbs_noise_split_powered_203_heldout_"
    "pairs_53to55_of_59_slots_median_11_fillers_ntest_400_cross_seed_range_0p0225_determinism_byte_identical_2runs_"
    "MM_STRONG_CG_CANDIDATE_NOT_chain_grade_ONE_STEP_TO_TRUE_READING_AXIS_CG_INDEPENDENT_ground_truth_relations_hand_"
    "annotated_gold_from_text_so_metric_measures_CORRECT_comprehension_plus_coherence_gate_FOR_correctness_a3816adc2_"
    "LOCAL_ONLY_2026-07-19"
)

ATOM_CLAIM = (
    "MATH MEASURED_MECHANISM (proven-bound) = STRONG-CG-CANDIDATE (ADVANCED). CLAIM: the brain-faithful STRUCTURE-"
    "CONTENT FACTORIZATION (a LEARNED content-blind structural code g_hat[slot] = (verb-lemma, argument-role) bound "
    "to REAL GloVe content x via native FHRR conjunctive binding) gives held-out-COMBINATION generalization when fed "
    "the role-filler tuples OUR OWN READER (exp_read_nested_clause_relative_third_reader_v1, nest ON) EXTRACTS from "
    "the McGuffey Third Reader (3823 noisy tuples, 2355 svo, GloVe coverage 0.97; V=207 concepts, 59 surviving "
    "slots): REAL FACTORED held-out 0.823 at N=40/m=6 (chance 0.062, 3 seeds), FLAT 0.005 (BELOW chance -- genuine "
    "anti-generalization), gap 0.818, un-saturated; positive control (random content on the SAME reader structure) "
    "reproduces F=0.914 gap=0.900; must-fail fired. "
    "TWO GAPS THE CONCEPTNET VET (29335, aea157d4-lineage) NAMED ARE DELIVERED (symmetric credit): "
    "(1) READING IS COUPLED -- relations are OUR reader's ACTUAL noisy extractions on real narrative, not curated "
    "ConceptNet triples. (2) REAL-DIFFICULTY CAN-FAIL -- realcost +0.091 at headline N=40, difficulty_is_capacity="
    "FALSE (real content sits 0.091/0.062/0.032 below clean-control at N=40/48/64, a genuine content-confusability "
    "cost, not pure capacity). "
    "AUDITOR TIER (BANKED MM / STRONG-CG-CANDIDATE, NOT CG) on the DEEPER self-flagged blocker, confirmed off-code: "
    "SELF-CONSISTENT GOLD / NO INDEPENDENT GROUND TRUTH -- the situations are BUILT from the reader's memberships AND "
    "held-out recovery is scored against those SAME memberships (gold true_f = the reader's own (concept,slot) "
    "output). A WRONG extraction (reader says dog-chased-BALL when the text says dog-chased-CAT) still binds and "
    "unbinds cleanly and is scored 'correct'. The cache stores ONLY reader output tuples with NO gold-text "
    "alignment. So the FHRR algebra ABSORBS extraction-CORRECTNESS noise BY CONSTRUCTION: the cell proves the "
    "factorization generalizes compositionally on the reader's REAL noisy STRUCTURE (with a genuine, modest real-"
    "difficulty cost), but does NOT measure whether the reader extracted the CORRECT relations. 'Reading-axis CG' "
    "would imply generalization over CORRECTLY-comprehended relations, which this test cannot establish -> STRONG-CG-"
    "CANDIDATE, not chain-grade. The real-difficulty can-fail, while genuine, is the SAME mechanistic class 29335 "
    "characterized (content cost under capacity pressure, vanishing by mid-N: both real and control saturate to "
    "1.000 by N128-192); the advance is magnitude (real narrative vocab -- names, pronouns -- is more confusable, "
    "0.091 vs ConceptNet's 0.047) plus a lower headline N=40 that clears the 0.05 flag. The COHERENCE-GATE is a "
    "clean NULL (+0.004 at headline, within +-0.007 across the whole sweep; drops 19.4% of memberships with no "
    "gain): the residual difficulty is content-confusability + sparsity, NOT droppable incoherent mis-extractions "
    "detectable by content-outlier scoring -- and because gold = the reader's own memberships, the gate CANNOT help "
    "correctness (no correctness signal exists to improve against)."
)

ATOM_RECOMPUTE = (
    "INDEP recompute (.venv Scripts/python, off-disk, NOT verdict_msg; Fix #28): "
    "(A) SELF-CONSISTENCY confirmed OFF-CODE (the decisive caveat): eval_heldout builds S = encode_situation(assign) "
    "= sum bind(g_true[slot], x[filler]) with filler = reader membership, then est=unbind(S,g_hat[q]) argmax; gold "
    "true_f = assign[s_star] drawn from held_by_slot <- build_split(slot_fillers) <- reader's cached memberships. NO "
    "independent ground-truth text alignment anywhere; cache _reader_extractions_third_reader_v1.json stores ONLY "
    "reader output tuples (keys: corpus/reader/svo/goal/recipient/loc/poss/nest, NO gold). Visibly-noisy tuples "
    "(['acted','grandmother','lie'], ['admiring','frank','boy'|'flower'] over-extraction) become gold memberships; "
    "the situation binds them and the algebra recovers them -> extraction-correctness invisible. CONFIRMED. "
    "(B) DETERMINISM: full run reproduced twice -> aggregate + arms_differ_hashes byte-identical (modulo ts/elapsed); "
    "OMP/MKL/OPENBLAS=1 in-cell; cross-seed factored_range @N40 real = 0.0225. "
    "(C) TWO GAPS DELIVERED: reader-coupled extractions (V=207, 59 slots, 3823 reader tuples); realcost sweep "
    "+0.091(N40) +0.062(N48) +0.032(N64) +0.013(N96) +0.002(N128) 0.000(N192,256); difficulty_is_capacity=False; "
    "both saturate 1.000 by N128-192 -> genuine real-difficulty, SAME class as 29335 (content cost under capacity "
    "pressure), magnitude larger (confusable real vocab) at lower headline N=40. "
    "(D) MUST-FAIL FAIR+FIRES: FLAT 0.005 << chance 0.0625 (below chance = anti-generalization), gap 0.818; both "
    "arms identical pool; arms_differ hashes distinct (fac cacbcbd6.. vs flat 69c99174..). "
    "(E) GATE NULL: gate_effect +0.004 headline, +-0.007 across the whole sweep; drop_frac 0.194; no gain -> not for "
    "noise-tolerance; repositioned for extraction-correctness vs independent gold. "
    "(F) SPLIT POWER: 203 held-out pairs across 53-55 of 59 slots/seed; surviving-slot median 11 fillers; n_test=400; "
    "per-type svo:OBJ 0.819(n~233) svo:SUBJ 0.830(n~156). N=40 is vector DIM at capacity edge, not test-set size; "
    "adequately powered. "
    "(G) WITNESS re-runs REAL reader nest ON -> real svo ['chased','dog','cat'], FACTORED recovers held-out chase-"
    "OBJ=cat, FLAT fails -- but the witness held-out is ALSO self-consistent (structure, not correctness)."
)

ATOM_SCOPE = (
    "McGuffey Third Reader (PG#14766, PD), OUR reader exp_read_nested_clause_relative_third_reader_v1 (nest ON) real "
    "cached noisy extractions; content REAL GloVe-wiki-gigaword-300 FHRR-encoded (beta 1.5); native FHRR bind/unbind "
    "(hdlab.binding, witness-verified equal to the cell ops); mechanism BYTE-IMPORTED from the ConceptNet CG cell "
    "(FZ.build_split/balanced_train/make_heldout_set/learn/eval_heldout). NO LLM. Load-bearing BOUNDS: "
    "(a) SELF-CONSISTENT GOLD (the CG blocker): gold = the reader's OWN (concept,slot) memberships; the metric "
    "scores compgen on the reader's real noisy STRUCTURE, NOT extraction CORRECTNESS. A wrong extraction is scored "
    "correct because the algebra binds/unbinds whatever was bound in. No independent ground truth exists in the "
    "pipeline. 'Reading-axis CG' (generalization over CORRECTLY-read relations) is NOT established. "
    "(b) REAL-DIFFICULTY CAN-FAIL IS GENUINE BUT MODEST AND SAME-CLASS: realcost +0.091 at N=40 is real content-"
    "confusability (more-confusable real narrative vocab), but it is the content-cost-under-capacity-pressure axis "
    "29335 already characterized -- it vanishes by mid-N (both saturate 1.000 by N128-192). It advances 29335 by "
    "magnitude + lower headline N, not by a new difficulty class. "
    "(c) COHERENCE-GATE NULL here: the gate does not help (algebra already tolerates the noise). It is UNTESTED for "
    "its actual job (extraction correctness vs independent gold) because no correctness signal exists in this test. "
    "(d) SPARSE STRUCTURE: raw median 1 filler/verb-slot; the surviving inventory (min_slot_fillers=8) has median 11 "
    "fillers; recip:AGT thin (n~10), recip:RECIP tiny (n~6). The load-bearing per-type numbers are svo:OBJ 0.819 / "
    "svo:SUBJ 0.830. "
    "BRAIN-CHECK: the substrate tolerating the reader's extraction noise gracefully (distributed factorization + "
    "partial-match readout) IS brain-faithful (robust distributed memory; TEM/grid structural codes reused across "
    "content, Whittington 2020). BUT the brain ALSO gets the relations CORRECT (comprehension) via coherence/schema-"
    "fit against GROUND MEANING -- which THIS test cannot measure (self-consistent gold). So the honest remaining "
    "gap is extraction CORRECTNESS, which needs INDEPENDENT ground truth + the coherence-gate scored FOR correctness. "
    "The brain-faithful robustness is REAL; the brain-faithful correctness is UNMEASURED. "
    "REVIVAL to CG: (1) THE decisive gate -- supply INDEPENDENT ground-truth relations (hand-annotated gold, or "
    "independent gold extracted from the text by a different method) so the held-out metric measures CORRECT "
    "comprehension, not self-consistent structure; (2) score the coherence/schema-fit gate AGAINST that independent "
    "gold (does dropping content-outliers raise CORRECTNESS?) -- its real job; (3) push the headline N even lower / "
    "harder readout to widen the genuine real-difficulty margin beyond the same-class content-cost band."
)

ATOM_METRICS = {
    "headline_N_dim": 40, "m": 6, "knn": 10, "chance": 0.0625, "seeds": [7, 13, 19],
    "control_synthetic_F_headline": 0.9142, "control_gap": 0.900,
    "real_reader_F_headline": 0.8233, "real_reader_FLAT": 0.005, "real_reader_gap": 0.8183,
    "real_FLAT_below_chance": "0.005 << 0.0625 (genuine anti-generalization)",
    "per_type": {"svo:OBJ": 0.8194, "svo:SUBJ": 0.8302, "recip:AGT": 0.7724, "recip:RECIP": 1.0},
    "realcost_sweep": {"N40": 0.091, "N48": 0.062, "N64": 0.032, "N96": 0.013, "N128": 0.002, "N192": 0.0, "N256": 0.0},
    "difficulty_is_capacity_not_noise": False,
    "realcost_note": "genuine content-confusability but SAME class as 29335 (cost under capacity pressure, vanishes by N128-192); advance = magnitude (0.091 vs 0.047) + lower headline N=40",
    "coherence_gate_effect_headline": 0.0042,
    "coherence_gate_sweep_range": "+-0.007 across whole sweep (clean null)",
    "gate_drop_frac": 0.194,
    "gate_note": "null here; algebra already absorbs noise; gate UNTESTED for extraction-correctness (its real job) because gold is self-consistent",
    "self_consistent_gold": "gold true_f = reader's OWN membership; extraction-correctness invisible; wrong extraction scored correct by construction",
    "reader_tuples": 3823, "reader_svo": 2355, "glove_coverage": 0.97,
    "V_vocab": 207, "n_slots": 59,
    "split_power": "203 held-out pairs across 53-55 of 59 slots/seed; surviving-slot median 11 fillers; n_test=400",
    "cross_seed_range_N40_real": 0.0225,
    "determinism": "aggregate + arms_differ_hashes byte-identical across 2 full runs (modulo ts/elapsed)",
    "arms_differ_hashes": {"factored": "cacbcbd6d01033b8", "flat": "69c99174e64eb4a3"},
    "witness": "REAL reader nest ON -> svo ['chased','dog','cat']; FACTORED recovers held-out chase-OBJ=cat, FLAT fails (also self-consistent = structure not correctness)",
    "cell_verdict": "HARD_PASS_READING_AXIS_FIRST_CG",
    "auditor_tier": "MEASURED_MECHANISM (proven-bound) = STRONG-CG-CANDIDATE (ADVANCED); NOT chain-grade due to self-consistent gold / extraction-correctness unmeasured",
}

COMPOSES = [
    ("ADVANCES the CG-candidate " + CONCEPTNET_PARENT + " (29335, ConceptNet, c880a8680): that atom NAMED the exact "
     "promotion path -- 'ONE STEP TO FULL READING-AXIS CG: relations extracted by OUR reader on real narrative "
     "(couples reader extraction noise) PLUS genuine in-primary can-fail from REAL difficulty not just capacity'. "
     "THIS cell DELIVERS BOTH named counts (reader-coupled extractions + realcost +0.091 difficulty!=capacity). So "
     "on the two counts 29335 flagged it is a genuine advance. It does NOT supersede 29335 (both remain proven-bound "
     "CG-candidates in the same family); it EXTENDS the family one rung."),
    ("Does NOT reach CG because of a THIRD, DEEPER blocker neither prior VET fully confronted: SELF-CONSISTENT GOLD. "
     "29335's ConceptNet relations were curated KB triples (correct by curation); here the reader's extractions "
     "are noisy AND scored against themselves, so extraction-correctness is invisible. The reader-arc VET now "
     "identifies extraction CORRECTNESS (independent ground truth) as the load-bearing CG gate, sharper than "
     "29335's 'no reading happened' + 'capacity-only headroom'."),
    ("Shares the mechanism + saturation lineage with " + REALCONTENT_PARENT + " (29334, realcontent, 8751c22d8): "
     "same FHRR unbind dominates content confusability; the only principled un-saturator is native superposition "
     "capacity (Plate 1995). This cell reuses that stress-map insight to expose the real-difficulty cost at low N."),
    ("BOUNDED BY the reader arc's hand-rule extraction wall: math::MM_read_nested_clause_relative_third_reader_v1 "
     "(550455f5f) measured corpus-wide RC precision ~0.40-0.55, and the reader's overall extraction precision is "
     "cited ~0.40-0.60. That wall is EXACTLY what the self-consistent-gold metric here CANNOT see: the ~40-60% of "
     "extractions that are WRONG still score 'correct'. The two cohere -- this cell's 0.823 is compgen on structure "
     "that is itself ~40-60% incorrect, and closing the CG gate requires measuring against that correctness wall."),
    ("credit: McGuffey Third Reader (PD); GloVe (Pennington 2014); ConceptNet5 (Speer 2017) via the parent; Plate "
     "1995 (superposition capacity); Whittington et al. 2020 (TEM relational/structural-code transfer) for the "
     "brain-faithfulness framing. Author (exp_dev) CREDITED for the honesty that lets this adjudicate: self-flagged "
     "the self-consistency / no-independent-ground-truth caveat (the decisive one), the modest real-difficulty cost, "
     "the coherence-gate null, and the sparsity -- and the cell's design-gate (must-fail fired, arms differ, "
     "determinism, positive control, byte-repro metrics) is clean."),
]

OVER_READS = [
    ("The verdict name HARD_PASS_READING_AXIS_FIRST_CG OVER-READS on CORRECTNESS. Confirmed off-code: the gold IS "
     "the reader's own memberships (self-consistent). A wrong extraction is scored correct because the FHRR algebra "
     "binds/unbinds whatever filler was bound in. The metric measures compgen on the reader's real noisy STRUCTURE, "
     "NOT whether the reader comprehended the text correctly. Honest framing: STRONG-CG-CANDIDATE (advanced), not a "
     "reading-axis chain-grade. Report the 0.823 strictly as 'structure-coupled compgen with a real-difficulty "
     "cost', with 'extraction-correctness unmeasured' as the load-bearing bound."),
    ("difficulty_is_capacity=False is TRUE at the headline but should NOT be read as a categorically new difficulty. "
     "Off-disk the realcost profile (+0.091 N40 -> 0 by N192) is the SAME content-cost-under-capacity-pressure axis "
     "29335 characterized for ConceptNet; the advance is magnitude (more-confusable real vocab) + a lower headline "
     "N=40 that clears the 0.05 flag. Genuine real-difficulty signal, same mechanistic class."),
    ("The coherence-gate null (+0.004) is NOT evidence the gate is useless. It is UNTESTED for its actual job "
     "(extraction correctness vs independent gold) because the self-consistent metric has no correctness signal. "
     "The null only shows the gate does not help NOISE-tolerance -- which the algebra already provides. Do not read "
     "'gate doesn't help' as 'gate not needed'; it is needed precisely for the CORRECTNESS axis this test omits."),
]

REVIVAL = [
    ("THE decisive CG gate: supply INDEPENDENT ground-truth relations (hand-annotated gold, or independent gold "
     "extracted from the text by a different method) so the held-out metric measures CORRECT comprehension rather "
     "than self-consistent structure. Only then does 'reading-axis CG' become measurable."),
    ("Score the coherence/schema-fit gate AGAINST that independent gold: does dropping content-outlier memberships "
     "raise CORRECTNESS (not just leave self-consistent accuracy flat)? That is the gate's real, currently-untested "
     "job."),
    ("Widen the genuine real-difficulty margin: push headline N even lower / use a harder global-neighbor readout so "
     "the content-confusability cost exceeds the same-class content-cost band, giving in-primary difficulty that is "
     "not just capacity-pressure content cost."),
]

GENUINE_POS = (
    "GENUINE kernel preserved symmetrically (NOT dismissed): this is a REAL advance over 29335. The factorization "
    "genuinely generalizes compositionally (REAL F 0.823, gap 0.818, must-fail FLAT 0.005 below chance) on OUR "
    "reader's ACTUAL noisy extraction STRUCTURE from real narrative -- end-to-end read->extract->build-inventory->"
    "factorize->generalize on the reader's own sparse/skewed/noisy output, where a flat content baseline anti-"
    "generalizes. It DELIVERS both gaps the ConceptNet VET named (reader-coupling + a genuine real-difficulty cost "
    "realcost +0.091, difficulty!=capacity). The design is clean: positive control reproduces (F 0.914), arms "
    "differ (distinct hashes), determinism byte-identical across runs, split adequately powered (203 pairs / 53-55 "
    "slots), witness re-runs the REAL reader. And the substrate's graceful tolerance of extraction noise IS brain-"
    "faithful robust distributed memory. The auditor's demotion to STRONG-CG-CANDIDATE SHARPENS (pins the self-"
    "consistent-gold blocker + the same-class real-difficulty framing + the gate's true untested job); it does NOT "
    "overturn the author's own stated caveats -- the exp_dev self-flagged the decisive self-consistency caveat, the "
    "modest cost, the gate null, and the sparsity. What this IS: an advanced structure-coupled compgen CG-candidate. "
    "What it is NOT (yet): a measurement of CORRECT comprehension -> not chain-grade."
)


def build_atom():
    return {
        "id": ATOM_ID, "name": ATOM_CLAIM, "corpus": "math", "tier": "MEASURED_MECHANISM",
        "kind": "experiment_landed_vet",
        "cert_status": "proven_bound",
        "cert_class": ("STRONG_cg_candidate_ADVANCED_structure_content_factorization_compositional_generalization_on_"
                       "OUR_readers_REAL_noisy_extraction_STRUCTURE_McGuffey_Third_Reader_reader_coupled_where_flat_"
                       "anti_generalizes_F_0p823_N40_gap_0p818_delivers_two_gaps_29335_named_reader_coupling_plus_"
                       "real_difficulty_can_fail_realcost_plus0p091_difficulty_not_capacity_same_class_content_cost_"
                       "under_capacity_pressure_BUT_NOT_chain_grade_SELF_CONSISTENT_GOLD_extraction_correctness_"
                       "invisible_wrong_extraction_scored_correct_by_construction_algebra_absorbs_correctness_noise_"
                       "coherence_gate_null_here_untested_for_correctness_inside_0p40_0p60_reader_extraction_wall"),
        "description": (ATOM_CLAIM + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + ATOM_RECOMPUTE
                        + "\n\nHONEST SCOPE: " + ATOM_SCOPE),
        "aliases": [
            "reader-coupled structure-content factorization v1",
            "STRONG-CG-candidate reader-coupled compgen on real noisy extraction structure",
            "self-consistent gold: extraction-correctness unmeasured (wrong extraction scored correct)",
            "delivers 29335's two gaps (reader-coupling + real-difficulty) but blocked by self-consistency",
            "real-difficulty can-fail realcost +0.091 same class as ConceptNet content-cost-under-capacity",
        ],
        "ts_iso": _iso, "ts": _ts,
        "metadata": {
            "provenance_quality": ("independent_venv_offdisk_recompute_two_full_runs_byte_identical_plus_code_trace_"
                                   "of_eval_heldout_gold_is_reader_membership_plus_cache_inspection_no_gold_"
                                   "annotation_plus_realcost_sweep_plus_split_power_recompute"),
            "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes": None,
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_role_filler_factorization_reader_coupled_cg_v1/metrics.json",
            "verified_off_data": ATOM_RECOMPUTE, "honest_scope": ATOM_SCOPE, "metrics": ATOM_METRICS,
            "over_reads_corrected": OVER_READS,
            "genuine_positives_symmetric_anti_negativity": GENUINE_POS,
            "revival_criteria": REVIVAL,
            "cross_arc_overlap_check": XARC,
            "self_consistent_gold_confirmed_off_code": True,
            "cg_blocker": "gold = reader's own memberships; extraction-correctness invisible; needs INDEPENDENT ground truth for reading-axis CG",
            "two_gaps_29335_named_delivered": "reader-coupling YES + real-difficulty can-fail YES (realcost +0.091, difficulty!=capacity)",
            "real_difficulty_same_class": "content-cost-under-capacity-pressure (same as 29335), advance = magnitude + lower headline N=40",
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data",
                "construction_proof_not_capability_win_could_it_fail_informatively",
                "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
                "every_negative_and_positive_brain_check_mechanism_vs_shortcut",
                "substrate_kb_concept_overlap_check_on_schema_vet",
                "vet_every_base_ingredient_fair_correct_brain_faithful_USER",
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
        "verdict": ("MEASURED_MECHANISM_proven_bound_STRONG_CG_CANDIDATE_ADVANCED_reader_coupled_structure_content_"
                    "factorization_generalizes_on_OUR_readers_REAL_noisy_extraction_structure_F_0p823_gap_0p818_"
                    "delivers_two_gaps_29335_named_reader_coupling_plus_real_difficulty_can_fail_realcost_plus0p091_"
                    "BUT_NOT_chain_grade_SELF_CONSISTENT_GOLD_extraction_correctness_invisible_wrong_extraction_"
                    "scored_correct_algebra_absorbs_correctness_noise_gate_null_untested_for_correctness"),
        "cert_increment_delta": 1,
        "decision": (
            "MM (proven-bound) = STRONG-CG-CANDIDATE (ADVANCED). Cell verdict HARD_PASS_READING_AXIS_FIRST_CG "
            "CONFIRMED on the mechanism + the two gaps it fixes vs 29335, but the VERDICT NAME is DEMOTED to STRONG-"
            "CG-CANDIDATE and BANKED MM. Off-disk recompute (.venv, Fix #28): (1) DECISIVE -- self-consistency "
            "confirmed OFF-CODE: eval_heldout builds S by binding x[filler] (reader membership) into the slot then "
            "unbinds; gold true_f = the reader's OWN (concept,slot) output; cache stores ONLY reader tuples, NO gold-"
            "text alignment; a wrong extraction binds/unbinds cleanly and is scored 'correct'. Extraction-CORRECTNESS "
            "is invisible; the metric measures compgen on the reader's real noisy STRUCTURE, not correct "
            "comprehension. (2) SYMMETRIC CREDIT -- the two gaps 29335 named ARE delivered: reader-coupled real "
            "extractions (V=207, 59 slots, 3823 tuples) + real-difficulty can-fail (realcost +0.091 at N40, "
            "difficulty!=capacity), though the cost is the SAME content-cost-under-capacity-pressure class as 29335 "
            "(vanishes by N128-192), advanced by magnitude + lower headline N. (3) must-fail FAIR+fires (FLAT 0.005 "
            "below chance 0.0625, gap 0.818, arms hashes distinct); coherence-gate a clean NULL (+0.004, +-0.007 "
            "across sweep, drops 19.4% no gain) -- untested for its real job (correctness vs independent gold); "
            "split powered (203 pairs / 53-55 of 59 slots, n_test 400); determinism byte-identical across 2 runs. "
            "Counts toward CERT as a proven-bound advanced CG-candidate. Local-only; needs orchestrator store sync."),
        "framing_correction_vs_director": (
            "Director asked to adjudicate EARNED reading-axis CG vs STRONG-CG-CANDIDATE, with the exp_dev's self-"
            "consistency caveat as the crux. RESULT (symmetric): the mechanism + BOTH gaps 29335 named (reader-"
            "coupling + real-difficulty can-fail) are CONFIRMED delivered -- a genuine advance -- AND the self-"
            "consistency caveat is CONFIRMED off-code as DECISIVE: gold = the reader's own memberships, so a wrong "
            "extraction is scored correct and extraction-CORRECTNESS is unmeasured. I BANK MM = STRONG-CG-CANDIDATE "
            "(advanced), NOT the inflated reading-axis CG. Precise honest claim: the factorization generalizes "
            "compositionally on OUR reader's REAL noisy extraction STRUCTURE with a genuine (modest, same-class) "
            "real-difficulty can-fail where flat anti-generalizes -- a real step beyond 29335's capacity-only "
            "headroom and 'no reading happened' counts -- BUT scored self-consistently, so it does NOT measure "
            "whether the reader read CORRECTLY. The ONE step to a TRUE reading-axis CG: INDEPENDENT ground-truth "
            "relations so the metric measures CORRECT comprehension, + the coherence-gate scored FOR correctness. "
            "The real-difficulty can-fail is genuine but should NOT be read as a new difficulty class (same content-"
            "cost-under-capacity-pressure as 29335). The coherence-gate null means the gate does not help noise-"
            "tolerance (algebra already does), NOT that the gate is unneeded -- it is needed precisely for the "
            "correctness axis this test omits. Genuine positive preserved; exp_dev CREDITED for self-flagging the "
            "decisive caveat, the modest cost, the gate null, and the sparsity (that honesty is what lets this "
            "adjudicate cleanly)."),
        "cross_arc_overlap_check": XARC,
        "net_cert_delta": ("+1 MM (advanced structure-coupled reader compgen CG-candidate: factorization generalizes "
                           "on OUR reader's REAL noisy extraction STRUCTURE F=0.823 where flat anti-generalizes, "
                           "delivering the two gaps 29335 named (reader-coupling + real-difficulty can-fail); bounded "
                           "by SELF-CONSISTENT GOLD -- extraction-correctness invisible, no independent ground truth. "
                           "INDEPENDENT ground-truth relations + coherence-gate-for-correctness are the CG revival "
                           "gates)."),
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
    print("=== A5 atom-write: role_filler_factorization_reader_coupled_cg_v1 -> MM / STRONG-CG-CANDIDATE (self-consistent gold) (2026-07-19) ===")
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
    print("ATOM (MM / STRONG-CG-CANDIDATE):", atom["id"][:100], "...")


if __name__ == "__main__":
    main()
