"""
A5-gated atomization: exp_single_edge_grounding_hd_binding_verbnet_v1 (smoke, local, uncommitted a76c98885)
-> ONE atom (2026-07-20). MEASURED_MECHANISM (storage-format + recall + class-keyed-generalization mechanism;
   filler-TYPING is HAND-STIPULATED = the load-bearing ceiling; NOT a full end-to-end grounding capability CG).

Author verdict HARD_PASS_SINGLE_EDGE_GROUNDING (USER's proposed definitive existence proof of substrate-native
grounding) -> HARDEST scrutiny (this is the cleanest positive of the session + directly answers the USER's
"what do we store / how is it recalled" question). Auditor CONFIRMS every gate off-disk but TIERS to
MEASURED_MECHANISM: what is proven is the STORAGE-FORMAT + RECALL + class-keyed SCHEMA-GENERALIZATION MECHANISM
via genuine FHRR HD binding (not a dict), with the explicit, load-bearing ceiling that EVERY semantic decision
(verb->class, class->filler-type edge, noun->type) is HAND-INJECTED and the FHRR unbind does EXACT algebra on
hand-made codes. That is a real, valuable mechanism-level answer to the USER's storage/recall question -- but
NOT a grounding CAPABILITY (which requires the typing to be DERIVED from the noun's own encoding, the separate
29379-82 / codebook-29368 frontier, NOT tested here).

INDEPENDENT RECOMPUTE (.venv Scripts/python, off-disk, NOT verdict_msg; Fix #28). Rebuilt atoms/keys/webs from
scratch with the same seed + real hdlab.atoms/hdlab.binding primitives and reproduced EVERY margin BIT-EXACT:
  WEB_EMPTY   all 5 margin 0.000000 (zeros unbind to zeros)
  WEB_BUILD   T1/G1/G2 margin 1.026078 (score_true 1.000000, score_false -0.026078) resolved; X1/X2 -0.013947 fail
  WEB_EAT     T1/G1/G2 margin -0.026800 fail; X1/X2 0.979448 resolved
  WEB_BOTH    T1/G1/G2 margin 0.999278 (score_true 0.994281, cross-talk -0.004998); X1/X2 0.965501 resolved
  WEB_MEM     T1 margin 1.026078 resolved; G1 0.004898 fail; G2 0.006528 fail (both << 0.10 threshold)
All 11 gate booleans reproduce True as reported; cardinality 50/50; arms_differ 5/5 distinct sha256; verbnet
lookup real (build_classids ['build-26.1-1'], Product role present in build-26.1 THEMROLES).

THE DECISIVE VET QUESTIONS (independently answered):

Q1 HAND-STIPULATED vs DERIVED (the #1 inflation risk) -- CRUX, fully quantified off-disk:
  EVERY semantic decision in the scoring path is HAND-INJECTED; the FHRR unbind does EXACT algebra on hand-made
  codes. Three stages, all handed:
    (i)  verb -> verb-CLASS: the ITEMS table hardcodes vclass 'BUILD'/'EAT' per sentence; VC_BUILD/VC_EAT are
         random atoms. VerbNet's real classids lookup (build in build-26.1, eat in eat-39.1) is populated ONLY
         into the verbnet_facts logging block -- verified off-disk: verbnet_lookup_facts is NOT called in
         score_item and vn_facts is NOT read in build_verdict. So VerbNet is PROVENANCE-ONLY, not in the
         scoring path.
    (ii) verb-class -> filler-TYPE edge: WEB_BUILD_EDGE = bind(KEY_BUILD, TYPE_ARTIFACT) with TYPE_ARTIFACT an
         author-chosen constant. The prereg HONESTLY flags VerbNet's own SELRESTRS on Product is EMPTY; the
         "artifact-type" is the standard Dowty/Levin READING of a creation Product role, a hand INTERPRETATION,
         NOT a fetched VerbNet field.
    (iii) noun -> filler-TYPE: the TYPE_OF_NOUN lexicon (fort/cabin/bridge->ARTIFACT, river/lake/valley->LOCATION,
         ...) is entirely hand-stipulated.
  WHAT cosine=1.000 ACTUALLY PROVES: unbind(bind(a,b),a) = |a|^2 * b = b EXACTLY for unit-modulus FHRR, so
  WEB_BUILD queried with KEY_BUILD recovers TYPE_ARTIFACT exactly (independently confirmed: recovered vs
  TYPE_ARTIFACT sim = 1.000000). fort WINS because type_vec(fort) IS TYPE_ARTIFACT (hand-lexicon) AND the edge
  target IS TYPE_ARTIFACT (author-chosen) -- BOTH ends hand-assigned to the SAME symbol; exact algebra then
  faithfully composes them. This is the ALREADY-KNOWN free-algebra binding property (29332/29379 family): "if
  you hand-encode the semantics, exact binding faithfully composes it." It PROVES the storage FORMAT + recall
  are correct and dict-free; it ASSUMES (does not derive) all the semantic content.
  WHAT IS GENUINELY INCREMENTAL over 29379 (why this is MM, not a pure re-demo tier-down): (a) the
  memorization-vs-generalization contrast arm OPERATIONALIZES the design choice "key storage by verb-CLASS not
  by sentence-identity" as the lever for schema-generalization; (b) it concretely answers the USER's
  storage/recall question with a specific, superposition-tolerant representation. Both are simple/algebraically
  forced, but they are a legitimate mechanism-DESIGN demonstration, not a bare restatement of binding algebra.

Q2 GENERALIZATION genuine or constructed?: GENUINE IN A NARROW, CONSTRUCTION-BOUNDED SENSE. Off-disk: WEB_BUILD
  is built from KEY_BUILD + TYPE_ARTIFACT ONLY -- G1/G2's sentence/noun atoms NEVER enter any web (true by
  construction). G1/G2 resolve because they are queried with the SAME shared KEY_BUILD (verb-class key, not
  sentence key). The memorization control is the load-bearing evidence and it FIRES cleanly: WEB_MEMORIZATION
  (keyed by SENT_KEY_T1) solves T1 (margin 1.026) but FAILS G1 (0.0049) and G2 (0.0065), both far below the
  0.10 floor -- a sentence-scoped key does NOT transfer. So class-keyed storage genuinely generalizes where
  sentence-keyed storage memorizes. BUT the generalization to the NEW NOUNS cabin/bridge "works" ONLY because
  they were HAND-TYPED into the ARTIFACT bucket (verified: type_vec(cabin) IS TYPE_ARTIFACT). There is NO
  derivation that "cabin is an artifact" from cabin's own encoding. So this is "schema-generalization over a
  hand-built type lexicon", NOT "the substrate figured out cabin is an artifact" -- exactly the ceiling.

Q3 DIFFICULTY genuinely ON?: TAUTOLOGICALLY, not empirically. WEB_EMPTY margin == 0.0 on all 5 because zeros
  unbind to zeros and similarity to the zero vector is exactly 0 -- a CONSTRUCTED no-information baseline, NOT a
  real reader's candidate stream failing. It legitimately shows "the stored edge is doing the work, not a
  pre-existing signal in the web", but it is NOT evidence these 5 sentences are hard. The hardness premise rests
  ENTIRELY on the CITED atom-29375 null ("no self-supervised text-internal signal for patient selection",
  measured over the reader's OWN NEST candidate stream) -- which is a citation, NOT reproduced in this cell.
  Leaning on 29375 is legitimate for the PREMISE but must not be read as this cell demonstrating item difficulty.

Q4 WRONG-EDGE + specificity + superposition controls non-vacuous?: YES, all non-vacuous, all behave as designed.
  WEB_EAT_EDGE_ONLY genuinely FAILS T1/G1/G2 (margin -0.0268, predicts the LOCATION distractor -- a real
  mismatch recovering noise, not a vacuous zero) and SOLVES X1/X2 (0.9794); WEB_BUILD_EDGE genuinely FAILS X1/X2
  (-0.0139). WEB_BOTH_EDGES = superposition of the two facts in ONE vector solves ALL 5 despite cross-talk
  (build items 0.9993, eat items 0.9655; cross-talk term ~0.005-0.03, well under the recovered ~0.994 signal) --
  a genuine "not a single-slot dict" proof (a dict has O(1) exact per-key storage; a bundle tolerates measured
  cross-talk). Mechanism-integrity holds: every web is a torch.Tensor complex64 (N_DIM,), never a dict.

TIER: MEASURED_MECHANISM. BANKED = the storage-FORMAT (bind verb-class->role->type into a single HD vector) +
RECALL (unbind + similarity-cleanup vs a 3-entry TYPE codebook, no dict) + class-keyed SCHEMA-GENERALIZATION
(across same-verb-class sentences via the shared key, with the sentence-scoped memorization control cleanly
failing G1/G2) + the specificity/wrong-edge + superposition/not-a-dict controls -- ALL at the MECHANISM level,
answering the USER's "what to store / how recalled" question concretely. NOT BANKED = derived filler-typing
(deriving a noun's type from its OWN learned encoding is the separate, partially-bounded 29379-82 / codebook-
29368 frontier, explicitly not tested), production-reader integration (the NEST candidate stream / 29375 heavy
pipeline is not re-invoked -- premise cited only), corpus-scale coverage, and any claim these 5 items are
empirically hard (difficulty-on is tautological, resting on the cited 29375 null). CERT delta +0 CAPABILITY --
a mechanism/design-format validation that answers a real USER design question and de-risks the "bind facts into
the web" half of the plausibility-web representation, NOT a grounding capability chain-grade.

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
ATOMIZED_BY = ("skunkworks_landed_vet_single_edge_grounding_hd_binding_verbnet_v1_MM_storage_recall_class_keyed_"
               "generalization_MECHANISM_but_filler_TYPING_HAND_STIPULATED_free_algebra_on_handmade_codes_NOT_"
               "grounding_capability_CG_typing_not_derived_2026-07-20")
ATOMIZED_DATE = "2026-07-20"
ANCHOR = "single_edge_grounding_hd_binding_verbnet_v1"
CELL_COMMIT = "a76c98885"  # local-only, uncommitted-to-origin per prereg contract (design+smoke only, no push)

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

XARC = (
    "substrate_query 'single edge grounding HD binding verb-class role-filler type storage recall schema "
    "generalization superposition' -> top hits cosine 0.30-0.33, ALL generic role-filler / prior-negative "
    "concept nodes: 0.3252 = the 2026-06-26 batch9 negative that HRR unbind-chain systematic generalization is "
    "REFUTED (a DIFFERENT mechanism -- feature-overlap prototype composition, not single-edge storage/recall); "
    "0.3115 = generic 'Role-filler binding' concept atom; 0.3008 = the 2026-06-11 role-binding drill note. NONE "
    "is a prior instance of THIS single-edge VerbNet-sourced grounding + memorization/superposition-guard design. "
    "The exp_dev prereg's own check found top hit 0.3096 (an immune-OAS binding-decay architecture, unrelated) + "
    "0.3057 (WordNet 'sectionalization', irrelevant). CONFIRMED: a genuine new synthesis of already-VET'd "
    "machinery (FHRR bind/unbind, atoms.similarity, VerbNet lookup used identically in 29375), NOT a rediscovery; "
    "the incremental content (class-key-vs-sentence-key generalization contrast) is not a prior arc cell."
)

ATOM_ID = (
    "math::MEASURED_MECHANISM_single_edge_grounding_hd_binding_verbnet_v1_STORAGE_FORMAT_plus_RECALL_plus_CLASS_"
    "KEYED_SCHEMA_GENERALIZATION_MECHANISM_via_genuine_FHRR_binding_NOT_a_dict_answers_USER_what_to_store_how_"
    "recalled_question_at_MECHANISM_LEVEL_BUT_every_semantic_decision_HAND_INJECTED_verb_to_class_hardcoded_ITEMS_"
    "class_to_type_edge_bind_key_build_TYPE_ARTIFACT_author_chosen_noun_to_type_TYPE_OF_NOUN_hand_lexicon_VerbNet_"
    "PROVENANCE_ONLY_not_in_scoring_path_verbnet_lookup_facts_not_called_in_score_item_build_classids_build_26_1_1_"
    "Product_role_present_SELRESTRS_empty_artifact_type_is_Dowty_Levin_reading_NOT_a_fetched_field_cosine_1p000_"
    "PROVES_unbind_bind_a_b_a_eq_b_EXACT_for_unit_modulus_FHRR_faithfully_composes_hand_made_codes_ALREADY_KNOWN_"
    "free_algebra_29332_29379_family_reproduced_bit_exact_offdisk_WEB_BUILD_T1_G1_G2_margin_1p026078_score_true_"
    "1p000000_score_false_neg0p026078_X1_X2_neg0p013947_fail_WEB_EAT_T1_G1_G2_neg0p026800_fail_X1_X2_0p979448_"
    "WEB_BOTH_superposition_T1_G1_G2_0p999278_crosstalk_neg0p004998_X1_X2_0p965501_solves_ALL5_not_single_slot_"
    "dict_WEB_MEMORIZATION_sentence_scoped_key_T1_1p026078_solves_G1_0p004898_G2_0p006528_FAIL_both_far_below_"
    "0p10_class_key_generalizes_sentence_key_memorizes_GENERALIZATION_genuine_but_NEW_NOUN_works_ONLY_because_"
    "cabin_bridge_HAND_TYPED_ARTIFACT_no_derivation_from_noun_own_encoding_DIFFICULTY_ON_TAUTOLOGICAL_zeros_unbind_"
    "to_zeros_NOT_evidence_items_hard_hardness_rests_on_CITED_29375_null_not_reproduced_cardinality_50of50_arms_"
    "differ_5of5_mechanism_integrity_every_web_torch_complex64_never_dict_BANKED_storage_format_recall_class_keyed_"
    "generalization_specificity_superposition_controls_NOT_BANKED_derived_typing_29379_82_29368_frontier_production_"
    "reader_29375_pipeline_corpus_scale_coverage_item_difficulty_CERT_plus0_capability_MECHANISM_DESIGN_validation_"
    "answers_USER_bind_facts_into_web_half_NOT_grounding_capability_CG_LOCAL_ONLY_2026-07-20"
)

PLAIN = (
    "The USER asked for the simplest possible proof of substrate-native grounding: look up one fact, store it in "
    "the substrate's own math (an HD binding, NOT a lookup table), and show a reader that couldn't resolve a "
    "sentence now can -- and can also handle NEW sentences of the same kind. On five hand-built sentences it works "
    "perfectly: after storing the single edge 'build-verbs make artifacts', the reader correctly picks 'fort' over "
    "'river' for the stored sentence AND generalizes to unseen 'cabin/bridge' sentences (margin ~1.0 out of 1.0), "
    "while a wrong 'eat->food' edge does not help, and two facts stored in ONE vector still both resolve (proving "
    "it is not secretly a dictionary). A sentence-specific key solves only the exact stored sentence and fails to "
    "generalize -- the honest contrast that shows a verb-CLASS key is what buys generalization. So the STORAGE "
    "FORMAT and the RECALL METHOD genuinely work and are dict-free. THE HONEST CEILING: every piece of MEANING in "
    "this test was hand-typed in. 'Build makes artifacts' was hand-written as the edge (real VerbNet only confirms "
    "build has a distinct 'Product' role -- it does NOT tag it 'artifact'; that reading is the researcher's, and "
    "VerbNet is used only for a provenance note, not in the actual scoring). And 'cabin/bridge/fort are artifacts, "
    "river/lake/valley are locations' is a hand-written dictionary of noun types. So the perfect cosine=1.000 "
    "recovery is the ALREADY-KNOWN fact that exact HD binding faithfully re-composes whatever you hand-encode -- it "
    "proves the storage-and-recall PLUMBING and the class-key design, NOT that the substrate DERIVED any meaning. "
    "The 'reader fails without the edge' check is also trivially true (an empty store returns zero); that the items "
    "are genuinely HARD rests on a separate earlier result (atom 29375), not on anything measured here. What this "
    "IS: a clean, valuable answer to 'what do we store and how is it recalled', at the mechanism level. What it is "
    "NOT: a grounding capability -- that needs the substrate to DERIVE a noun's type from the noun's own learned "
    "encoding (the separate, still-open 29379-82 / codebook-29368 frontier), which this cell deliberately does not "
    "attempt."
)

IMPORTANCE = (
    "MEDIUM (a concrete, honest mechanism-level answer to a load-bearing USER design question; NOT capability "
    "progress). It answers the USER's 'what do we store / how is it recalled' question with a specific, working, "
    "dict-free, superposition-tolerant representation: bind(verb-class, role, filler-type) into one HD vector, "
    "recall via unbind + codebook-cleanup, and key by verb-CLASS (not sentence-identity) to get schema-"
    "generalization -- with the memorization control cleanly demonstrating the class-key-vs-sentence-key lever. "
    "That de-risks the 'bind facts into the web' half of the plausibility-web representation (composes with the "
    "reshape-concepts codebook half, 29368). Importance is CAPPED and must NOT be over-read as grounding: every "
    "semantic assignment (verb->class, class->type, noun->type) is hand-injected, the FHRR recovery is the "
    "already-known exact free-algebra property (29379 family), and difficulty-on is tautological. The real "
    "grounding capability -- deriving a filler's type from its OWN encoding -- is untouched here and is the "
    "partially-bounded 29379-82 frontier."
)

ATOM_CLAIM = (
    "MATH MEASURED_MECHANISM (storage-format + recall + class-keyed schema-generalization MECHANISM via genuine "
    "FHRR HD binding; filler-TYPING HAND-STIPULATED = the load-bearing ceiling; NOT a grounding capability CG). "
    "CLAIM: the USER's proposed minimal existence proof -- store ONE looked-up fact SUBSTRATE-NATIVE as an HD "
    "binding (WEB_BUILD_EDGE = bind(bind(VC_BUILD, ROLE_PATIENT), TYPE_ARTIFACT), a single torch.Tensor complex64, "
    "NOT a dict), recall via unbind + atoms.similarity cleanup vs a 3-entry TYPE codebook -- WORKS at the mechanism "
    "level and generalizes across same-verb-class sentences via the shared class key. Reproduced BIT-EXACT off-disk "
    "(.venv, real hdlab primitives, rebuilt from seed): WEB_BUILD resolves T1/G1/G2 (margin 1.026078, score_true "
    "1.000000, score_false -0.026078) and fails X1/X2 (-0.013947); WEB_EAT_EDGE_ONLY fails T1/G1/G2 (-0.026800) and "
    "resolves X1/X2 (0.979448); WEB_BOTH_EDGES superposition resolves ALL 5 (build 0.999278 with cross-talk "
    "-0.004998; eat 0.965501) = genuine not-a-single-slot-dict; WEB_MEMORIZATION (sentence-scoped key) resolves T1 "
    "(1.026078) but FAILS G1 (0.004898) and G2 (0.006528), both far below the 0.10 floor = the class-key-vs-"
    "sentence-key generalization contrast. WEB_EMPTY margin 0.0 all 5; cardinality 50/50; arms_differ 5/5; "
    "mechanism-integrity holds (every web torch.Tensor complex64 (1024,), never a dict). AUDITOR TIER "
    "(MEASURED_MECHANISM, tiered from author HARD_PASS): THE CRUX (Q1) -- EVERY semantic decision is HAND-INJECTED "
    "and FHRR does EXACT algebra on hand-made codes: (i) verb->class is hardcoded in the ITEMS table (VerbNet's "
    "real classids lookup is PROVENANCE-ONLY, verified off-disk that verbnet_lookup_facts is not called in "
    "score_item and vn_facts is not read in build_verdict; build_classids=['build-26.1-1'], Product role present, "
    "but SELRESTRS empty so the 'artifact-type' is the Dowty/Levin READING not a fetched field); (ii) the "
    "class->filler-type edge target TYPE_ARTIFACT is an author-chosen constant; (iii) noun->type is the "
    "hand-stipulated TYPE_OF_NOUN lexicon. So cosine=1.000 PROVES unbind(bind(a,b),a)=|a|^2*b=b EXACTLY for "
    "unit-modulus FHRR (recovered-vs-TYPE_ARTIFACT sim 1.000000 independently confirmed) faithfully COMPOSING "
    "hand-made codes -- the ALREADY-KNOWN free-algebra binding property (29332/29379); it proves the storage FORMAT "
    "+ recall are correct and dict-free, it ASSUMES all semantic content. GENERALIZATION (Q2) is genuine in a "
    "narrow construction-bounded sense: G1/G2 never enter any web and resolve via the SHARED class key, and the "
    "memorization control cleanly fails G1/G2 -- BUT new-noun generalization works ONLY because cabin/bridge were "
    "hand-typed ARTIFACT (no derivation from the noun's own encoding). DIFFICULTY-ON (Q3) is TAUTOLOGICAL (zeros "
    "unbind to zeros; not evidence the items are hard -- hardness rests on the CITED 29375 null, not reproduced "
    "here). Controls (Q4) are all non-vacuous and behave as designed. What IS genuinely incremental over 29379 "
    "(why MM not a pure-re-demo tier-down): the memorization-vs-generalization arm OPERATIONALIZES the class-key-"
    "not-sentence-key design lever, and the cell concretely answers the USER's storage/recall question with a "
    "superposition-tolerant representation."
)

ATOM_RECOMPUTE = (
    "INDEP recompute (.venv Scripts/python, off-disk, rebuilt atoms/keys/webs from seed 20260720 with real "
    "hdlab.atoms.make_atom_fhrr + hdlab.binding.bind/unbind + hdlab.atoms.similarity; NOT verdict_msg; Fix #28): "
    "(A) ALL margins BIT-EXACT vs metrics.json: WEB_EMPTY 5x 0.000000; WEB_BUILD T1/G1/G2 1.026078 "
    "(st 1.000000, sf -0.026078) resolved, X1/X2 -0.013947 fail; WEB_EAT T1/G1/G2 -0.026800 fail, X1/X2 0.979448 "
    "resolved; WEB_BOTH T1/G1/G2 0.999278 (st 0.994281, sf -0.004998), X1/X2 0.965501, ALL5 resolved; "
    "WEB_MEMORIZATION T1 1.026078 resolved, G1 0.004898 fail, G2 0.006528 fail. (B) Q1 hand-vs-derived: "
    "verbnet_lookup_facts NOT called in score_item (grep-confirmed False); vn_facts NOT read in build_verdict "
    "(False); vclass 'BUILD'/'EAT' hardcoded in ITEMS; edge target = author constant bind(key_build, "
    "TYPE_ARTIFACT); TYPE_OF_NOUN hand-lexicon present. recovered(WEB_BUILD, KEY_BUILD) vs TYPE_ARTIFACT sim = "
    "1.000000 (exact single-fact recovery). (C) Q2 generalization: WEB_BUILD depends on KEY_BUILD + TYPE_ARTIFACT "
    "only (no G1/G2 atoms); G1/G2 queried with the identical KEY_BUILD; type_vec(cabin) IS TYPE_ARTIFACT (hand); "
    "MEM-arm G1 recovered vs TYPE_ARTIFACT sim 0.00027 (near-zero -> fails). (D) Q3 difficulty: WEB_EMPTY unbind is "
    "exactly zeros -> similarity 0.0 by construction (tautological, not a real reader failing). (E) Q4 controls "
    "non-vacuous: EAT-edge actively recovers noise on build items (predicts LOCATION distractor, margin -0.0268, "
    "not a vacuous 0), BOTH-edges superposition tolerates ~0.005-0.03 cross-talk under ~0.994 signal. Cardinality "
    "50/50; arms_differ 5/5 distinct sha256; verbnet real (build-26.1-1, Product in THEMROLES)."
)

ATOM_SCOPE = (
    "Small hand-authored existence-proof regime: 5 sentences (T1 stored / G1,G2 held-out same-verb-class / X1,X2 "
    "cross-verb-class control), 5 arms x 5 items x 2 candidates = 50 similarity scores, N_DIM=1024, seed 20260720, "
    "FHRR complex64, closed-form exact-recovery measurement (no scale/statistical axis; smoke IS the decisive run). "
    "LOAD-BEARING BOUNDS: "
    "(a) STORAGE-FORMAT + RECALL + CLASS-KEYED GENERALIZATION MECHANISM PROOF, NOT A GROUNDING CAPABILITY WIN: the "
    "storage format (bind class->role->type into one HD vector), the recall (unbind + similarity-cleanup vs a "
    "3-entry codebook, dict-free), and the class-key-vs-sentence-key generalization lever are proven at the "
    "mechanism level, but EVERY semantic assignment is HAND-INJECTED and the cosine=1.000 recovery is the "
    "already-known exact free-algebra binding property. Do NOT read as 'the substrate grounds language' or "
    "'the substrate derived that cabin is an artifact'. "
    "(b) FILLER-TYPING IS HAND-STIPULATED (the crux ceiling): deriving a filler's TYPE from its OWN learned "
    "encoding -- so that generalization to a novel noun is EARNED not hand-typed -- is the separate, partially-"
    "bounded 29379-82 / codebook-29368 frontier, deliberately NOT tested here. The class->type edge is likewise "
    "a hand INTERPRETATION of VerbNet's Product role (SELRESTRS empty; VerbNet is provenance-only, not in the "
    "scoring path). "
    "(c) DIFFICULTY-ON IS TAUTOLOGICAL: WEB_EMPTY margin 0.0 because zeros unbind to zeros -- a constructed "
    "no-information baseline, not a real reader's candidate stream failing. The premise that these items are hard "
    "rests ENTIRELY on the CITED atom-29375 null (no self-sup text signal for patient selection, measured over the "
    "reader's OWN NEST pipeline), which is NOT reproduced in this cell. "
    "(d) NOT EXERCISED: production-reader integration (the 29375 NEST candidate stream / sklearn clause-classifier "
    "/ McGuffey corpus is not re-invoked); corpus-scale coverage; novel-NOUN (novel-atom) generalization; any "
    "learned (vs stipulated) codebook. "
    "BRAIN-CHECK: role-filler binding + cleanup-memory recall is a brain-grounded mechanism (VSA / Smolensky "
    "tensor-product role binding; hippocampal/cortical schema retrieval), and keying by CLASS to get schema-"
    "generalization is faithful; this cell only proves that mechanism's PLUMBING on hand-encoded semantics, not "
    "that the substrate learns the semantics. REVIVAL/PROMOTE toward a grounding CG requires: (1) DERIVE the "
    "filler-type from the noun's OWN encoding (learned codebook, 29368/29379-82) so novel-noun generalization is "
    "earned, not hand-typed; (2) DERIVE (not hand-write) the verb-class->type edge from a real lookup source; "
    "(3) integrate with the production reader's candidate stream (29375 pipeline) on real ambiguous corpus text so "
    "difficulty is empirical, not tautological. If the resolution survives when the TYPING is derived rather than "
    "handed, upgrade toward chain-grade."
)

ATOM_METRICS = {
    "WEB_EMPTY_margin_all5": 0.0,
    "WEB_BUILD_T1_G1_G2_margin": 1.026078, "WEB_BUILD_score_true": 1.000000, "WEB_BUILD_score_false": -0.026078,
    "WEB_BUILD_X1_X2_margin": -0.013947,
    "WEB_EAT_T1_G1_G2_margin": -0.026800, "WEB_EAT_X1_X2_margin": 0.979448,
    "WEB_BOTH_T1_G1_G2_margin": 0.999278, "WEB_BOTH_score_true": 0.994281, "WEB_BOTH_crosstalk_false": -0.004998,
    "WEB_BOTH_X1_X2_margin": 0.965501, "WEB_BOTH_solves_all5": True,
    "WEB_MEMORIZATION_T1_margin": 1.026078, "WEB_MEMORIZATION_G1_margin": 0.004898,
    "WEB_MEMORIZATION_G2_margin": 0.006528, "WEB_MEMORIZATION_solves_train_fails_gen": True,
    "margin_thresh": 0.10, "cardinality": "50/50", "arms_differ_verified": "5/5 distinct sha256",
    "recovered_WEB_BUILD_vs_TYPE_ARTIFACT_sim": 1.000000,
    "Q1_verbnet_lookup_facts_called_in_score_item": False,
    "Q1_vn_facts_read_in_build_verdict": False,
    "Q1_verb_to_class_hardcoded_in_ITEMS": True,
    "Q1_class_to_type_edge_author_constant_TYPE_ARTIFACT": True,
    "Q1_noun_to_type_hand_lexicon_TYPE_OF_NOUN": True,
    "Q1_build_classids": ["build-26.1-1"], "Q1_build_has_Product_role": True,
    "Q1_SELRESTRS_empty_artifact_type_is_Dowty_Levin_reading_not_field": True,
    "Q1_cosine_1p000_is_already_known_free_algebra_29379_family": True,
    "Q2_G1_G2_never_enter_any_web": True, "Q2_G1_G2_queried_with_shared_KEY_BUILD": True,
    "Q2_memorization_control_fails_G1_G2_cleanly": True,
    "Q2_new_noun_works_only_because_hand_typed_ARTIFACT": True,
    "Q2_MEM_arm_G1_recovered_vs_TYPE_ARTIFACT_sim": 0.00027,
    "Q3_difficulty_on_tautological_zeros_unbind_to_zeros": True,
    "Q3_hardness_rests_on_cited_29375_null_not_reproduced": True,
    "Q4_wrong_edge_fails_non_vacuously_recovers_noise": True,
    "Q4_superposition_tolerates_crosstalk_not_a_dict": True,
    "Q4_mechanism_integrity_every_web_torch_complex64_never_dict": True,
    "cell_verdict": "HARD_PASS_SINGLE_EDGE_GROUNDING",
    "auditor_tier": ("MEASURED_MECHANISM storage-format + recall + class-keyed generalization mechanism; filler-"
                     "TYPING hand-stipulated = load-bearing ceiling; NOT a grounding capability CG (typing not "
                     "derived); cosine=1.000 is the already-known exact free-algebra binding property"),
}

COMPOSES = [
    ("COMPOSES / RE-USES (does NOT supersede) the already-VET'd free-algebra binding property (atoms 29332/29379 "
     "family): the cosine=1.000 exact single-fact recovery and the ~0.005-0.03 superposition cross-talk are that "
     "known property applied to hand-encoded semantics -- this cell adds NO new binding algebra. What it adds is "
     "the class-key-vs-sentence-key generalization CONTRAST arm and a concrete storage/recall representation."),
    ("IS the 'bind facts into the web' half of the plausibility-web REPRESENTATION MAPPING (composes with the "
     "learned codebook / reshape-concepts half, atom 29368) at the smallest possible scale (one edge). NOTE this "
     "cell uses HAND-STIPULATED filler-type codes, NOT 29368's learned codebook -- so it validates the binding/"
     "recall half assuming the codebook half; the two together are not yet demonstrated end-to-end."),
    ("BUILDS ON the premise licensed by atom 29375 (affectedness / patient-selection design gate): 29375 VET'd "
     "that NO self-supervised text-internal signal correlates with gold patient-correctness for this reader "
     "failure class (6 signal families failed). That is the CITED null that makes 'the reader has zero "
     "selectional-preference signal pre-storage' a VET'd premise rather than a strawman -- BUT it is a citation, "
     "not reproduced here; this cell's WEB_EMPTY zero-margin is tautological (empty store), NOT a re-measurement "
     "of item difficulty on the production reader."),
    ("SIBLING of today's (2026-07-20) active-learning-loop v1/v2 and settling-fix MM atoms: the same session-wide "
     "pattern -- a clean HARD_PASS that is CONSTRUCTION-DETERMINED on closer look and tiers to MEASURED_MECHANISM. "
     "Here the construction-determinism is that every semantic assignment is hand-injected and FHRR does exact "
     "algebra; the mechanism/design content is real, the capability claim is not earned."),
    ("credit: Smolensky 1990 (tensor-product role-filler binding) / Plate 1995 (HRR) / Gayler 2003 (VSA) for the "
     "binding+cleanup mechanism; Dowty 1991 / Levin 1993 for the creation-verb Product-role -> created-artifact "
     "reading (the hand interpretation); NLTK VerbNet (build-26.1 Product role, provenance). The cell AUTHOR "
     "(exp_dev) CREDITED for an HONEST design: pre-registered falsifiable bands, explicit disclosure that the "
     "filler-typing is hand-stipulated and VerbNet's SELRESTRS is empty, a genuine memorization control, "
     "mechanism-integrity assertions (type is torch.Tensor never dict), and a correct claim_ceiling. The auditor's "
     "tier to MEASURED_MECHANISM CONFIRMS rather than contradicts the author's own disclosed ceiling."),
]

OVER_READS = [
    ("Do NOT read cosine=1.000 / margin ~1.026 as a grounding CAPABILITY. It is the ALREADY-KNOWN exact free-"
     "algebra binding property: unbind(bind(a,b),a)=|a|^2*b=b for unit-modulus FHRR, faithfully re-composing "
     "codes that were ALL hand-assigned (verb->class hardcoded, class->type an author constant, noun->type a hand "
     "lexicon). It proves the storage FORMAT + recall are correct and dict-free; it does NOT prove the substrate "
     "derived any semantic content. Report as 'storage/recall mechanism validated on hand-encoded semantics'."),
    ("Do NOT cite the VerbNet lookup as making the edge 'derived'. VerbNet is PROVENANCE-ONLY (verified off-disk: "
     "not called in the scoring path); it confirms build has a distinct Product role but its SELRESTRS is EMPTY, "
     "so 'created-artifact type' is the Dowty/Levin READING, a hand interpretation, NOT a fetched VerbNet field. "
     "The eat->food control edge is explicitly common-sense-sourced, not VerbNet-sourced."),
    ("Do NOT read the G1/G2 generalization as 'the substrate figured out cabin/bridge are artifacts'. G1/G2 "
     "resolve via the SHARED verb-class key (genuine, and the memorization control cleanly proves class-key beats "
     "sentence-key), but the NEW nouns resolve ONLY because cabin/bridge were HAND-TYPED into the ARTIFACT bucket. "
     "There is no derivation from the noun's own encoding -- that is the separate 29379-82 frontier."),
    ("Do NOT cite WEB_EMPTY margin=0.0 as evidence these 5 sentences are hard or that 'the reader fails'. It is "
     "tautological (zeros unbind to zeros). The difficulty premise rests ENTIRELY on the cited 29375 null, "
     "measured over the production reader's own candidate stream, which this cell does NOT reproduce."),
]

REVIVAL = [
    ("PROMOTE toward a grounding CG requires DERIVING the semantics rather than handing them: (1) derive each "
     "filler's TYPE from its OWN learned encoding (a real learned codebook, atoms 29368 / 29379-82) so that "
     "generalization to a NOVEL noun is EARNED, not hand-typed into the ARTIFACT bucket; (2) derive (not hand-"
     "write) the verb-class->filler-type edge from a real lookup source whose content is not authored to the "
     "answer; (3) integrate with the PRODUCTION reader's candidate stream (the 29375 NEST pipeline) on real "
     "ambiguous corpus text so difficulty is empirical, not the tautological empty-web zero. If the resolution "
     "survives when the typing is DERIVED, upgrade toward chain-grade."),
    ("EXERCISE the end-to-end representation: replace the hand-stipulated TYPE codes with the learned codebook "
     "(29368) and show the bind-facts-into-the-web half (this cell) composes with the reshape-concepts-into-"
     "codebook half WITHOUT the hand-off -- currently the two halves are validated separately, not together."),
    ("SCALE the sentence set beyond 5 hand-authored items and beyond 2 verb classes to test whether the class-"
     "keyed superposition tolerates realistic web density (many co-stored edges) before cross-talk swamps the "
     "recovered signal -- the 2-fact WEB_BOTH cross-talk (~0.005-0.03) is a floor, not a capacity measurement."),
]

GENUINE_POS = (
    "GENUINE positives preserved (symmetric anti-negativity): this is a REAL, clean, HONEST mechanism-level answer "
    "to a load-bearing USER design question -- 'what do we store and how is it recalled' -- and I do NOT dilute "
    "what it earns. Independently verified off-disk: (1) the storage FORMAT works -- one looked-up edge stored as "
    "a genuine FHRR HD binding (bind(verb-class, role, filler-type)), a single complex64 tensor, mechanism-"
    "integrity-asserted to never be a dict; (2) RECALL works -- unbind + atoms.similarity cleanup vs a 3-entry "
    "TYPE codebook recovers the stored type exactly (sim 1.000000) and picks the right candidate; (3) class-keyed "
    "SCHEMA-GENERALIZATION is genuine in a construction-bounded sense -- G1/G2 never enter any web yet resolve via "
    "the shared verb-class key, and the memorization control CLEANLY fails G1/G2 (margins 0.0049/0.0065 << 0.10), "
    "correctly operationalizing 'key by class not by sentence' as the generalization lever; (4) the specificity + "
    "wrong-edge + superposition controls are all NON-VACUOUS and behave exactly as designed (WEB_BOTH resolves all "
    "5 despite cross-talk = a real not-a-single-slot-dict proof); (5) the author's design is exemplary and HONEST "
    "(pre-registered bands, explicit hand-stipulation + empty-SELRESTRS disclosure, memorization control, "
    "mechanism-integrity assertions, correct claim_ceiling). What this IS: a construction-validated storage/recall/"
    "class-generalization MECHANISM proof that concretely de-risks the 'bind facts into the web' representation. "
    "What it is NOT (the scope that keeps it honest): a grounding CAPABILITY -- every semantic assignment is hand-"
    "injected, the cosine=1.000 recovery is the already-known exact free-algebra property, difficulty-on is "
    "tautological, and the real capability (deriving a filler's type from its own encoding) is untouched. The "
    "auditor's tier to MEASURED_MECHANISM CONFIRMS the author's own disclosed ceiling; it does not contradict a "
    "genuine mechanism win."
)


def build_atom():
    return {
        "id": ATOM_ID, "name": ATOM_CLAIM, "corpus": "math", "tier": "MEASURED_MECHANISM",
        "kind": "experiment_landed_vet",
        "cert_status": "proven-bound",
        "cert_class": ("single_edge_grounding_hd_binding_STORAGE_FORMAT_plus_RECALL_plus_CLASS_KEYED_SCHEMA_"
                       "GENERALIZATION_MECHANISM_via_genuine_FHRR_binding_not_a_dict_memorization_control_"
                       "operationalizes_class_key_vs_sentence_key_lever_superposition_tolerates_crosstalk_BUT_"
                       "filler_TYPING_HAND_STIPULATED_verb_to_class_hardcoded_class_to_type_author_constant_"
                       "noun_to_type_hand_lexicon_VerbNet_provenance_only_cosine_1p000_is_already_known_exact_"
                       "free_algebra_29379_family_difficulty_on_tautological_hardness_cited_29375_NOT_a_grounding_"
                       "capability_CG_typing_not_derived_29379_82_29368_frontier_untested"),
        "plain_language": PLAIN,
        "importance": IMPORTANCE,
        "description": (ATOM_CLAIM + "\n\nPLAIN LANGUAGE: " + PLAIN + "\n\nRECOMPUTE (off-disk .venv, Fix #28): "
                        + ATOM_RECOMPUTE + "\n\nHONEST SCOPE: " + ATOM_SCOPE),
        "aliases": [
            "single-edge substrate-native grounding via HD binding (VerbNet-sourced) v1 (MM)",
            "storage-format + recall + class-keyed schema-generalization MECHANISM, not a dict",
            "filler-TYPING is HAND-STIPULATED (the load-bearing ceiling); cosine=1.000 is already-known free algebra",
            "memorization control fails G1/G2 (class-key generalizes, sentence-key memorizes)",
            "superposition WEB_BOTH resolves all 5 despite cross-talk = not-a-single-slot-dict proof",
            "VerbNet lookup PROVENANCE-ONLY (build-26.1 Product role, SELRESTRS empty; not in scoring path)",
            "SCOPE: NOT a grounding capability CG; derived filler-typing (29379-82/29368) untested",
        ],
        "ts_iso": _iso, "ts": _ts,
        "serves_capability": ("learning_and_self_monitoring_layer_plausibility_web_bind_facts_into_web_half_"
                              "storage_recall_representation_mechanism_validation"),
        "metadata": {
            "provenance_quality": ("independent_venv_offdisk_rebuild_from_seed_all_margins_bit_exact_plus_"
                                   "scoring_path_grep_audit_verbnet_provenance_only_hand_lexicon_hand_edge_"
                                   "confirmed_memorization_control_subslice_superposition_crosstalk_arms_differ_"
                                   "hashes_mechanism_integrity_never_dict"),
            "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes": None,
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_single_edge_grounding_hd_binding_verbnet_v1_smoke/metrics.json",
            "plain_language": PLAIN, "importance": IMPORTANCE,
            "verified_off_data": ATOM_RECOMPUTE, "honest_scope": ATOM_SCOPE, "metrics": ATOM_METRICS,
            "over_reads_corrected": OVER_READS,
            "genuine_positives_symmetric_anti_negativity": GENUINE_POS,
            "revival_criteria": REVIVAL,
            "cross_arc_overlap_check": XARC,
            "hand_vs_derived_verdict": (
                "CRUX (Q1) -- EVERY semantic decision is HAND-INJECTED; FHRR does EXACT algebra on hand-made codes. "
                "(i) verb->verb-class: hardcoded in the ITEMS table (VC_BUILD/VC_EAT random atoms); VerbNet's real "
                "classids lookup is PROVENANCE-ONLY (verified off-disk: verbnet_lookup_facts not called in "
                "score_item; vn_facts not read in build_verdict; build_classids=['build-26.1-1'], Product role in "
                "THEMROLES, but SELRESTRS empty so 'artifact-type' is the Dowty/Levin READING, not a fetched field). "
                "(ii) class->filler-type edge: WEB_BUILD_EDGE = bind(KEY_BUILD, TYPE_ARTIFACT), TYPE_ARTIFACT an "
                "author-chosen constant. (iii) noun->type: the hand-stipulated TYPE_OF_NOUN lexicon. cosine=1.000 "
                "PROVES exact free-algebra recovery (unbind(bind(a,b),a)=b, sim 1.000000 confirmed) faithfully "
                "COMPOSING hand-made codes = the already-known 29332/29379 binding property; it proves storage "
                "FORMAT + recall + dict-free-ness, it ASSUMES all semantic content. => storage/recall + class-keyed "
                "generalization MECHANISM proof, NOT a grounding capability."),
            "difficulty_on_verdict": (
                "TAUTOLOGICAL (Q3): WEB_EMPTY margin 0.0 on all 5 because zeros unbind to zeros and similarity to "
                "the zero vector is exactly 0 -- a constructed no-information baseline, NOT a real reader's "
                "candidate stream failing. Legitimate as 'the stored edge does the work, not a pre-existing web "
                "signal', but NOT evidence the 5 items are hard. Hardness rests entirely on the CITED atom-29375 "
                "null (measured over the production reader's NEST pipeline), which is NOT reproduced in this cell."),
            "generalization_verdict": (
                "GENUINE IN A NARROW CONSTRUCTION-BOUNDED SENSE (Q2): WEB_BUILD is built from KEY_BUILD + "
                "TYPE_ARTIFACT ONLY (G1/G2 sentence/noun atoms never enter any web); G1/G2 resolve via the SAME "
                "shared KEY_BUILD; the memorization control (SENT_KEY_T1-keyed web) solves T1 (1.026) but FAILS "
                "G1 (0.0049) and G2 (0.0065) far below the 0.10 floor -- class-key generalizes, sentence-key "
                "memorizes. BUT new-noun generalization works ONLY because cabin/bridge were hand-typed ARTIFACT "
                "(type_vec(cabin) IS TYPE_ARTIFACT); no derivation from the noun's own encoding = the ceiling."),
            "controls_verdict": (
                "ALL NON-VACUOUS (Q4): WEB_EAT_EDGE_ONLY actively recovers noise on build items (predicts LOCATION "
                "distractor, margin -0.0268 -- a real mismatch, not a vacuous zero) and resolves eat items (0.979); "
                "WEB_BUILD fails eat items (-0.0139); WEB_BOTH_EDGES superposition resolves ALL 5 despite ~0.005-"
                "0.03 cross-talk under a ~0.994 recovered signal = genuine not-a-single-slot-dict proof; mechanism-"
                "integrity holds (every web a torch.Tensor complex64 (1024,), never a dict)."),
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "construction_proof_not_capability_win_could_it_fail_informatively",
                "synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data",
                "free_algebra_binding_property_already_known_29332_29379_dont_re_bank_as_new",
                "hand_stipulated_vs_derived_semantics_only_derived_counts_as_grounding_capability",
                "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
                "difficulty_on_via_empty_construct_is_tautological_not_item_hardness",
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
        "op": "landed_vet_atomize", "corpus": "math", "tier": atom["tier"], "cert_status": atom["cert_status"],
        "cert_class": ("MEASURED_MECHANISM_storage_format_recall_class_keyed_generalization_MECHANISM_filler_"
                       "typing_HAND_STIPULATED_free_algebra_on_handmade_codes_NOT_grounding_capability_CG"),
        "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes_commit": None,
        "supersedes_atom_id": None, "amends_atom_id": None,
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True,
        "auditor": "hdi_skunkworks", "atomized_by": ATOMIZED_BY,
        "author_verdict": "HARD_PASS_SINGLE_EDGE_GROUNDING",
        "verdict": ("MEASURED_MECHANISM storage-format + recall + class-keyed schema-generalization mechanism via "
                    "genuine FHRR binding (not a dict); filler-TYPING HAND-STIPULATED = load-bearing ceiling; "
                    "cosine=1.000 is the already-known exact free-algebra property (29379); difficulty-on "
                    "tautological (hardness cited to 29375, not reproduced); NOT a grounding capability CG "
                    "(typing not derived; 29379-82/29368 frontier untested). All margins reproduced bit-exact "
                    "off-disk; cardinality 50/50; arms_differ 5/5."),
        "cert_increment_delta": 0,
        "decision": (
            "MEASURED_MECHANISM. Author verdict HARD_PASS_SINGLE_EDGE_GROUNDING (USER's proposed definitive "
            "existence proof of substrate-native grounding) -> VET'd HARDEST, all gates reproduced BIT-EXACT "
            "off-disk (.venv, rebuilt from seed, Fix #28) but tiered to MEASURED_MECHANISM. (1) THE CRUX Q1: every "
            "semantic decision is HAND-INJECTED and FHRR does EXACT algebra on hand-made codes -- verb->class "
            "hardcoded in ITEMS (VerbNet PROVENANCE-ONLY, verified not in the scoring path; build-26.1 Product role "
            "real but SELRESTRS empty, 'artifact-type' is the Dowty/Levin reading not a field), class->type edge an "
            "author constant bind(KEY_BUILD, TYPE_ARTIFACT), noun->type the hand-stipulated TYPE_OF_NOUN lexicon. "
            "cosine=1.000 (recovered-vs-TYPE_ARTIFACT sim 1.000000) is the ALREADY-KNOWN exact free-algebra binding "
            "property (29332/29379) faithfully composing hand-made codes; it proves the storage FORMAT + recall + "
            "dict-free-ness, it ASSUMES the semantic content. (2) Q2 generalization genuine in a narrow "
            "construction-bounded sense: G1/G2 never enter any web and resolve via the shared class key; the "
            "memorization control cleanly fails G1/G2 (0.0049/0.0065 << 0.10) -- BUT new-noun generalization works "
            "only because cabin/bridge were hand-typed ARTIFACT (no derivation from the noun's own encoding). "
            "(3) Q3 difficulty-on TAUTOLOGICAL (zeros unbind to zeros; hardness rests on the cited 29375 null, not "
            "reproduced here). (4) Q4 controls all non-vacuous and behave as designed (EAT-edge recovers noise on "
            "build items; WEB_BOTH superposition resolves all 5 despite cross-talk = not-a-single-slot-dict; "
            "mechanism-integrity: every web torch.complex64, never a dict). WHY MM not a pure re-demo tier-down: "
            "the memorization-vs-generalization arm operationalizes the class-key-not-sentence-key design lever and "
            "the cell concretely answers the USER's storage/recall question with a superposition-tolerant "
            "representation -- a legitimate mechanism-DESIGN demonstration. BANKED: storage-format + recall + "
            "class-keyed generalization + specificity/superposition controls at the mechanism level. NOT BANKED: "
            "derived filler-typing (29379-82/29368 frontier), production-reader integration (29375 pipeline), "
            "corpus-scale coverage, item difficulty (only cited). CERT delta +0 capability (mechanism/design-format "
            "validation, de-risks the bind-facts-into-web half; not a grounding capability chain-grade). "
            "Local-only; needs orchestrator store sync."),
        "framing_correction_vs_director": (
            "Director framed this as 'the cleanest positive of the session and the USER's proposed definitive "
            "existence proof of substrate-native grounding' and asked me to VET it HARDEST -- and correctly "
            "predicted the likely honest tier is MEASURED_MECHANISM. RESULT (symmetric anti-negativity): I CONFIRM "
            "every gate off-disk AND confirm the MM tier. The cosine=1.000 result does NOT prove substrate-native "
            "GROUNDING -- it proves the storage FORMAT + recall MECHANISM on HAND-ENCODED semantics: every semantic "
            "assignment (verb->class, class->type, noun->type) is hand-injected, and the perfect recovery is the "
            "already-known exact free-algebra binding property (29379) faithfully composing hand-made codes. The "
            "genuine wins (independently banked): the storage/recall representation works and is dict-free; class-"
            "keyed storage genuinely generalizes where sentence-keyed memorizes (the memorization control cleanly "
            "fires); the superposition/specificity controls are non-vacuous. The load-bearing ceiling (matching the "
            "author's own disclosed claim_ceiling): the filler-TYPING is HAND-STIPULATED -- deriving a noun's type "
            "from its OWN encoding is the separate, partially-bounded 29379-82/codebook-29368 frontier, NOT tested "
            "here -- and difficulty-on is tautological, resting on the cited 29375 null rather than a reproduced "
            "reader failure. So this is a genuine + valuable answer to the USER's 'what to store / how recalled' "
            "question AT THE MECHANISM LEVEL, but NOT a full end-to-end grounding capability CG. exp_dev CREDITED "
            "for a clean, self-critical design (pre-registered bands, explicit hand-stipulation disclosure, "
            "memorization control, mechanism-integrity assertions, correct claim_ceiling)."),
        "cross_arc_overlap_check": XARC,
        "net_cert_delta": ("+0 CAPABILITY. Banks a storage-format + recall + class-keyed schema-generalization "
                           "MECHANISM proof: one looked-up edge stored as a genuine FHRR HD binding (not a dict), "
                           "recalled via unbind + codebook-cleanup, generalizing across same-verb-class sentences "
                           "via the shared class key (memorization control cleanly fails the held-out items), with "
                           "non-vacuous specificity/superposition controls. Answers the USER's 'what to store / how "
                           "recalled' question at the mechanism level and de-risks the 'bind facts into the web' "
                           "half of the plausibility-web representation. NOT a grounding capability chain-grade: "
                           "every semantic assignment is hand-injected, cosine=1.000 is the already-known exact "
                           "free-algebra property, difficulty-on is tautological, and the derived-typing capability "
                           "(29379-82/29368) is untested. Does not advance the capability CERT count."),
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
    print("=== A5 atom-write: single_edge_grounding_hd_binding_verbnet_v1 -> MEASURED_MECHANISM (2026-07-20) ===")
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
