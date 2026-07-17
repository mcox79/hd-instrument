"""exp_read_grow_openvocab_fastmap_v1 -- OPEN-VOCAB reading: learn NEW words WHILE reading, instead of abstaining.

QUESTION (the USER "read textbooks and learn new things efficiently" step): the glass-box IE parser
(exp_read_grow_foundation_realprose_glassbox_ie_v2) reads closed-schema early-reader prose at precision ~1.0 but
ABSTAINS on OUT-OF-VOCAB words -- an unknown noun (a new entity) or an unknown verb (a new relation) is tagged UNK,
dropped from the noun/verb slots, and the sentence yields no triple (NO_SUBJECT / NO_OBJECT / NO_VERB). The learned
lexicon (exp_lexicon_learned_grounding_scaled_v1, VET'd) already does cross-situational FAST-MAPPING of a new
word->concept in isolation. This cell INTEGRATES them: extend the read->grow loop so that when reading hits an
UNKNOWN word it LEARNS it on the fly -- FAST-MAP a new entity by ELIMINATION (the one unknown token in an otherwise
all-known sentence) + role-eligibility (the relation slot pins its type) + cross-situational CONFIRM (propose-but-
verify: provisional on a single exposure, committed only after a 2nd type-COHERENT exposure) -- and grow the
foundation with the newly-read facts, queryable. For an unknown VERB the cell TESTS relation-schema GROWTH (a new
relation grown on 2 coherent exposures, then guarded by rejecting a type-violating argument) rather than only
abstaining. Glass-box, NO LLM, local numpy.

HONEST ASYMMETRY (pre-registered expectation, per the dispatching steer + research note section (e)#5):
  NEW ENTITIES are tractable -- the relation's accumulated argument-type profile PINS the new entity's type by
    elimination, so the mapping is verifiable against the grown schema (a new eats-subject must behave like the
    known animals; a new lives_in-object like the known places).
  NEW RELATIONS are harder -- an unknown verb between two known nouns has NO tight type-elimination pinning its
    identity (any two new verbs with the same arg-types are indistinguishable by grounding), and its MEANING is
    unverifiable (no external referent). The cell can mechanically GROW a new relation + type-guard its arguments,
    but this is CONSTRUCTION-grade evidence, NOT the grounded/type-verified evidence the entity track earns. The
    two tracks are reported + tiered SEPARATELY; the honest expected landing is entities-strong / relations-weaker.

MECHANISM (fully glass-box, inspectable, NO LLM, NO neural parser):
  1. Parse each sentence with a deterministic POS-lexicon over the CURRENT known-noun / known-verb sets (mutable;
     grow as words are learned). n_unknown == 0 -> normal known fact. n_unknown == 1 -> FAST-MAP candidate (the
     single unknown is either a noun-slot new ENTITY or a verb-slot new RELATION, everything else known -- this IS
     the elimination constraint). n_unknown >= 2 -> ABSTAIN (too ambiguous to fast-map).
  2. Type-infer the new entity from the (relation, role) slot it fills (eats-subj ~ animal, eats-obj ~ food,
     lives_in-obj ~ place, chases-* ~ animal), read off the grown schema NOT ground truth.
  3. PROVISIONAL-HOLD (propose-but-verify): buffer the observation; do NOT commit on a single exposure. CONFIRM
     when the word has >= CONFIRM_K (=2) exposures whose slot-set is TYPE-COHERENT = a subset of some already-
     grounded concept's slot-profile (glass-box, uses only accepted facts). Then commit the buffered facts through
     the SAME ingest gate (novel-entity / schema-fit / hold) and add the word to the known set -> queryable.
  4. Precision guard: a type-INCONSISTENT new word (seen in mutually-incompatible slots) is never type-coherent ->
     never confirmed -> no fact injected. A single-exposure noise word never reaches CONFIRM_K -> never committed.

ARMS (per seed):
  FULL_FASTMAP    -- elimination fast-map + CONFIRM (>=2 coherent exposures) + type-guard (the mechanism).
  NO_CONFIRM      -- fast-map but commit on the FIRST exposure (no cross-situational confirm). Precision
                     discriminator: must admit the single-exposure noise word + the inconsistent word as FALSE
                     facts that FULL_FASTMAP rejects.
  ABSTAIN_BASELINE-- the v2 behavior: any sentence with an unknown word abstains. Lift discriminator: learns ZERO
                     new entities/relations (grows only the bootstrap block).

METRICS (reported SEPARATELY, never blobbed):
  (a) new_entity_fastmap_acc = fraction of target new ENTITIES correctly learned (confirmed + all true facts in
      store + queryable) from FEW (2) exposures.
  (b) new_entity_query_acc   = fraction of new-entity (s,r) unique cues whose VSA retrieval returns the correct
      object from the grown store (does the foundation now CONTAIN the newly-read facts, queryable?).
  (c) new_relation_grow_acc + relation_violation_rejected + relation_distractor_not_grown = new-RELATION handling
      (mechanical growth + arg-type guard) -- the harder track, reported apart from entities.
  (d) entity_false_fact_rate = fraction of the mis-fast-map distractor facts admitted (PRECISION preserved?).
      FULL must be 0.0; NO_CONFIRM must be > 0.0 (the confirm guard is what preserves precision).

PRE-REG (envelope-fail-bands; I own the bands; set BEFORE running):
  ENTITY track HARD-PASS: new_entity_fastmap_acc >= 0.80 AND new_entity_query_acc >= 0.80 AND
    entity_false_fact_rate == 0.0 AND ABSTAIN_BASELINE new_entity_fastmap_acc == 0.0 (lift is real) AND
    NO_CONFIRM entity_false_fact_rate > FULL entity_false_fact_rate (confirm guard fires).
  RELATION track PASS: new_relation_grow_acc >= 0.80 AND relation_violation_rejected AND
    relation_distractor_not_grown AND relation_false_fact_rate == 0.0.
  OVERALL:
    HARD_PASS = ENTITY track HARD-PASS AND RELATION track PASS.
    MIDDLE_BAND = ENTITY track HARD-PASS AND RELATION track NOT PASS (entities work, relations don't -- honest).
    HARD_FAIL = new_entity_fastmap_acc < 0.40 OR entity_false_fact_rate == 1.0 OR new_entity_query_acc < 0.40 OR
                ABSTAIN_BASELINE new_entity_fastmap_acc > 0.0 (baseline already learned them -> no lift).
  Even on HARD_PASS: the RELATION result is CONSTRUCTION-grade (meaning unverifiable) -- flagged in verdict_msg.

Local numpy, no queue/GPU/atoms/push. ASCII-only. Sequential-CPU (foundation grows fact-by-fact; wall < 10s).
Storage: SHARDED (one VSA vector per accepted fact). progress_logging = print_flush_true.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; FULL_FASTMAP vs NO_CONFIRM accepted-store hash differs;
#     FULL_FASTMAP vs ABSTAIN_BASELINE differ).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor. FHRR cleanup among ~30 concepts at N=1024 with 3-term bundle is
#     z ~ sqrt(2N/3) ~ 26 sigma -> VSA decode reachable ~1.0; the discriminator is the FAST-MAP CONFIRM decision +
#     the ingest gate, NOT phasor noise.
# - baseline_in_band at smoke: ABSTAIN_BASELINE learns 0 new entities (floor); NO_CONFIRM admits false facts
#     (>0 false); FULL learns entities + 0 false. All three arms measurably differ.
# - discriminator survives scale: corpus is FIXED-size (hand-authored GT). Discriminators asserted at self-test:
#     (1) FULL learns wug/glon/narn (few-exposure), (2) FULL rejects the noise + inconsistent distractors,
#     (3) NO_CONFIRM admits them (confirm guard is load-bearing), (4) ABSTAIN_BASELINE learns nothing (lift).
# - HARD_PASS strictly above floor; explicit bands in prereg JSON.
# - real_code_path (F.1): self_test constructs the REAL imported objects (FoundationStore + SVO encode/decode +
#     imported learn_lexicon) + the REAL open-vocab parser + reader at tiny scale, and asserts (not synthetic-only).
# - deterministic seeding (F.5): fixed int seeds; sorted() vocab ordering; per-seed rng; NO hash()/list(set()).
# - all numbers in comments tagged HYPOTHESIZED@prereg / THEORETICAL / MEASURED@metrics.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import argparse
import time
import json
import hashlib
import platform
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_grow_openvocab_fastmap_v1"

# --- GENUINE REUSE of the proven downstream (imported, not rebuilt) ---
from experiments.exp_read_grow_foundation_endtoend_v1 import (
    N_DIM,
    RELATIONS,
    ENTITIES,
    ANIMALS,
    FOODS,
    PLACES,
    GT_TYPE,
    build_typed_foundation,
    build_lexicon_train,
    FoundationStore,
    _svo_make_phasors,
    _bind,
    _unbind,
    _cleanup,
    _encode_meaning,
    _decode_meaning,
    _learn_lexicon,
    _lexicon_top,
)

SUBJ, VERB, OBJ = 0, 1, 2
CONFIRM_K = 2                         # cross-situational confirm: >= 2 type-coherent exposures before commit.

# ---------------------------------------------------------------------------
# Closed-class POS-lexicon (glass-box; injects WORD-CLASS + morphology, never facts).
# ---------------------------------------------------------------------------
DETS = {"the", "a", "an"}
PREPS = {"in", "on", "by", "at", "near", "under", "with", "to"}
BE_AUX = {"is", "are", "was", "were", "be", "been", "am"}
ADJS = {"hungry", "little", "small", "big", "brown", "fast", "lazy", "happy", "quick",
        "old", "young", "grey", "gray", "black", "white", "red", "wet", "green"}
ADVS = {"quickly", "slowly", "happily", "then", "always", "often", "gently"}
# known verb surface -> (canonical relation, needs_prep). live -> lives_in via 'in'.
KNOWN_VERB_FORMS = {
    "eat": ("eats", None), "eats": ("eats", None), "eating": ("eats", None),
    "ate": ("eats", None), "eaten": ("eats", None),
    "chase": ("chases", None), "chases": ("chases", None), "chasing": ("chases", None),
    "chased": ("chases", None),
    "live": ("live", "in"), "lives": ("live", "in"), "living": ("live", "in"), "lived": ("live", "in"),
}


def _noun_lemma(w, known_nouns):
    """productive singular morphology over the CURRENT known-noun set: birds->bird, foxes->fox."""
    if w in known_nouns:
        return w
    if len(w) > 3 and w.endswith("es") and w[:-2] in known_nouns:
        return w[:-2]
    if len(w) > 2 and w.endswith("s") and w[:-1] in known_nouns:
        return w[:-1]
    return None


def _tokenize(sentence):
    s = sentence.lower().strip()
    for p in [".", "!", "?", ",", ";", ":", '"', "'"]:
        s = s.replace(p, " ")
    return [t for t in s.split() if t]


def _tag(w, known_nouns, known_verbs):
    """(tag, lemma, prep_need). tag in {DET,AUX,PREP,ADV,ADJ,VERB,NOUN,UNK}. Known sets are MUTABLE (grow)."""
    if w in DETS:
        return "DET", None, None
    if w in BE_AUX:
        return "AUX", None, None
    if w in PREPS:
        return "PREP", w, None
    if w in ADVS:
        return "ADV", None, None
    if w in ADJS:
        return "ADJ", None, None
    if w in known_verbs:
        stem, need = KNOWN_VERB_FORMS.get(w, (w, None))   # grown relations map to themselves
        return "VERB", stem, need
    nl = _noun_lemma(w, known_nouns)
    if nl is not None:
        return "NOUN", nl, None
    return "UNK", w, None


def _resolve_relation(verb_stem, prep, known_rels):
    if verb_stem == "live":
        return "lives_in" if prep == "in" else None
    if verb_stem in known_rels:
        return verb_stem
    return None


# ---------------------------------------------------------------------------
# OPEN-VOCAB glass-box parser: at most ONE unknown token (elimination). Returns (triples, metas, rule, freason).
# meta per triple: {"new_subj","new_obj","new_rel", "new_word"}. Simple SVO / SVO-prep only (new-word scope);
# hard structures (passive/coord/rel-clause) are NOT in the open-vocab scope -> abstain if they carry an unknown.
# ---------------------------------------------------------------------------
def ie_extract_openvocab(sentence, known_nouns, known_verbs, known_rels):
    toks = _tokenize(sentence)
    T = [(w,) + _tag(w, known_nouns, known_verbs) for w in toks]   # (word, tag, lemma, prep_need)
    tags = [t[1] for t in T]
    lemmas = [t[2] for t in T]
    n = len(T)
    unk_idx = [i for i in range(n) if tags[i] == "UNK"]
    if len(unk_idx) >= 2:
        return [], [], "ELIM_TOO_MANY_UNKNOWNS", "more than one unknown token (cannot fast-map by elimination)"

    known_verb_pos = [i for i in range(n) if tags[i] == "VERB"]
    noun_pos = [i for i in range(n) if tags[i] == "NOUN"]

    # ---- decide verb slot + whether the verb is the (single) unknown (a NEW RELATION) ----
    new_rel = False
    if known_verb_pos:
        vi = known_verb_pos[0]
        verb_stem = lemmas[vi]
        verb_need = T[vi][3]
    elif len(unk_idx) == 1:
        # the single unknown is a candidate NEW VERB iff it sits between a noun-ish left and a noun-ish right.
        u = unk_idx[0]
        left = [i for i in noun_pos if i < u]
        right = [i for i in noun_pos if i > u]
        if not left or not right:
            return [], [], "NO_VERB", "unknown token is not a verb between two known nouns"
        vi = u
        verb_stem = lemmas[u]           # the surface unknown IS the new relation id
        verb_need = None
        new_rel = True
    else:
        return [], [], "NO_VERB", "no known verb and no fast-mappable new verb"

    # ---- subject: nearest noun/UNK left of the verb (skip DET/ADJ/AUX) ----
    subj = None
    new_subj = False
    for j in range(vi - 1, -1, -1):
        if tags[j] in ("DET", "ADJ", "AUX", "ADV"):
            continue
        if tags[j] == "NOUN":
            subj = lemmas[j]
            break
        if tags[j] == "UNK":
            subj = lemmas[j]
            new_subj = True
            break
        break
    if subj is None:
        return [], [], "NO_SUBJECT", "no subject noun/new-word left of verb"

    # ---- object: first noun/UNK right of the verb (skip DET/ADJ/ADV/AUX; capture governing prep) ----
    obj = None
    new_obj = False
    prep = None
    j = vi + 1
    while j < n:
        tg = tags[j]
        if tg in ("DET", "ADJ", "ADV", "AUX"):
            j += 1
            continue
        if tg == "PREP" and prep is None:
            prep = lemmas[j]
            j += 1
            continue
        if tg == "NOUN":
            obj = lemmas[j]
            break
        if tg == "UNK":
            obj = lemmas[j]
            new_obj = True
            break
        break
    if obj is None:
        return [], [], "NO_OBJECT", "no object noun/new-word right of verb"

    # ---- relation ----
    if new_rel:
        relation = verb_stem
    else:
        relation = _resolve_relation(verb_stem, prep, known_rels)
        if relation is None:
            if verb_stem == "live":
                return [], [], "LIVE_WITHOUT_IN", "live verb without a governing 'in'"
            return [], [], "UNKNOWN_VERB", "verb stem not in relation schema"

    if subj == obj:
        return [], [], "SUBJ_EQ_OBJ", "subject == object"

    triple = (subj, relation, obj)
    meta = {"new_subj": new_subj, "new_obj": new_obj, "new_rel": new_rel,
            "new_word": (subj if new_subj else obj if new_obj else relation if new_rel else None)}
    rule = ("NEW_RELATION" if new_rel else "NEW_ENTITY" if (new_subj or new_obj) else
            ("SVO_PREP" if relation == "lives_in" else "SVO_ACTIVE"))
    return [triple], [meta], rule, None


# ---------------------------------------------------------------------------
# CORPUS + GROUND TRUTH. Bootstrap block (known -> establishes relation argument-type profiles), then new-entity
# fast-map block, mis-fast-map distractors (precision guard), and the harder new-relation block.
# ---------------------------------------------------------------------------
def _row(text, gts, kind, note=""):
    return {"text": text, "gts": tuple(gts), "kind": kind, "note": note}


OPENVOCAB_CORPUS = [
    # -- bootstrap (KNOWN; establishes eats/lives_in/chases argument-type profiles) --
    _row("The cat eats the fish.", [("cat", "eats", "fish")], "known"),
    _row("The dog eats the bread.", [("dog", "eats", "bread")], "known"),
    _row("The cow eats grass.", [("cow", "eats", "grass")], "known"),
    _row("The bird eats a seed.", [("bird", "eats", "seed")], "known"),
    _row("The frog eats the worm.", [("frog", "eats", "worm")], "known"),
    _row("The cat lives in the barn.", [("cat", "lives_in", "barn")], "known"),
    _row("The dog lives in the barn.", [("dog", "lives_in", "barn")], "known"),
    _row("The bird lives in the nest.", [("bird", "lives_in", "nest")], "known"),
    _row("The fish lives in the pond.", [("fish", "lives_in", "pond")], "known"),
    _row("The frog lives in the pond.", [("frog", "lives_in", "pond")], "known"),
    _row("The cat chases the bird.", [("cat", "chases", "bird")], "known"),
    _row("The dog chases the cat.", [("dog", "chases", "cat")], "known"),
    _row("The bird chases the frog.", [("bird", "chases", "frog")], "known"),
    # -- NEW-ENTITY fast-map (each new entity introduced with 2 type-coherent exposures) --
    _row("The wug eats a seed.", [("wug", "eats", "seed")], "new_entity", "wug exposure 1 (animal, eats-subj)"),
    _row("The glon eats bread.", [("glon", "eats", "bread")], "new_entity", "glon exposure 1 (animal, eats-subj)"),
    _row("The cow lives in a narn.", [("cow", "lives_in", "narn")], "new_entity", "narn exposure 1 (place, lives_in-obj)"),
    # -- mis-fast-map distractors (PRECISION guard) --
    _row("The quon eats bread.", [("quon", "eats", "bread")], "distractor_single", "quon single exposure -> must NOT commit"),
    _row("The zib eats a seed.", [("zib", "eats", "seed")], "distractor_inconsistent", "zib exposure 1 (as animal-subj)"),
    # -- NEW-ENTITY exposure 2 (confirm) --
    _row("The wug lives in the nest.", [("wug", "lives_in", "nest")], "new_entity", "wug exposure 2 -> CONFIRM"),
    _row("The glon chases the cat.", [("glon", "chases", "cat")], "new_entity", "glon exposure 2 -> CONFIRM"),
    _row("The dog lives in a narn.", [("dog", "lives_in", "narn")], "new_entity", "narn exposure 2 -> CONFIRM"),
    # -- distractor: zib exposure 2 is TYPE-INCONSISTENT (as food-obj) -> incoherent -> must NOT confirm --
    _row("The cat eats a zib.", [("cat", "eats", "zib")], "distractor_inconsistent", "zib exposure 2 (as food-obj) -> reject"),
    # -- NEW-RELATION growth (harder track): 2 coherent exposures -> grow --
    _row("The cat grims the dog.", [("cat", "grims", "dog")], "new_relation", "grims exposure 1 (animal-animal)"),
    _row("The bird grims the frog.", [("bird", "grims", "frog")], "new_relation", "grims exposure 2 -> GROW"),
    # -- new-relation ARG-TYPE guard: type-violating arg under the grown relation -> must reject --
    _row("The seed grims the cat.", [("seed", "grims", "cat")], "relation_violation", "seed (food) as grims-subj -> reject"),
    # -- new-relation distractor: single exposure new verb -> must NOT grow --
    _row("The owl wobbles the mouse.", [("owl", "wobbles", "mouse")], "relation_distractor_single", "wobbles single -> abstain"),
]

# target new entities + their TRUE facts (should be learned + queryable).
NEW_ENTITY_FACTS = {
    "wug": [("wug", "eats", "seed"), ("wug", "lives_in", "nest")],
    "glon": [("glon", "eats", "bread"), ("glon", "chases", "cat")],
    "narn": [("cow", "lives_in", "narn"), ("dog", "lives_in", "narn")],
}
NEW_ENTITIES = sorted(NEW_ENTITY_FACTS.keys())
# unique (s,r)->o cues for queryability (each maps to exactly ONE object in the corpus).
NEW_ENTITY_QUERY_CUES = [
    ("wug", "eats", "seed"), ("wug", "lives_in", "nest"),
    ("glon", "eats", "bread"), ("glon", "chases", "cat"),
    ("cow", "lives_in", "narn"),
]
# facts that must NEVER enter the store (mis-fast-map precision guard).
SHOULD_REJECT_ENTITY = {("quon", "eats", "bread"), ("zib", "eats", "seed"), ("cat", "eats", "zib")}
# new-relation ground truth.
NEW_RELATION = "grims"
NEW_RELATION_FACTS = [("cat", "grims", "dog"), ("bird", "grims", "frog")]
RELATION_VIOLATION = ("seed", "grims", "cat")
RELATION_DISTRACTOR = ("owl", "wobbles", "mouse")
SHOULD_REJECT_RELATION = {RELATION_VIOLATION, RELATION_DISTRACTOR}

DISTINCT_NEW_WORDS = sorted(set(NEW_ENTITIES) | {"quon", "zib", "grims", "wobbles"})


# ---------------------------------------------------------------------------
# Extended concept codebook: deterministic phasor for EVERY token (known + new). Assigning a new word's vector is
# just infrastructure -- the LEARNING is whether the reader fast-maps + confirms + commits its facts (a word's
# vector existing is NOT "knowing" the fact). Glass-box: vector is a fixed function of the per-seed rng + a sorted
# concept ordering (no hash()/list(set())).
# ---------------------------------------------------------------------------
def build_ext_concepts():
    concepts = sorted(set(ENTITIES) | set(RELATIONS) | set(DISTINCT_NEW_WORDS))
    cid_idx = {c: i for i, c in enumerate(concepts)}
    return concepts, cid_idx


def _coherent_with_grounded(slot_set, store):
    """type-coherence: the new word's observed (rel, role) slot-set is a SUBSET of some already-grounded concept's
    slot-profile (glass-box; uses ONLY accepted facts). Returns the matching concept or None."""
    if not slot_set:
        return None
    for c, prof in store.type_profile.items():
        if prof and slot_set <= prof:
            return c
    return None


def _relation_args_coherent(subs, objs, store):
    """new-relation coherence: all subject args share a common accepted (rel,role) slot, and all object args do
    too (a stable arg-type signature). Glass-box; uses only accepted facts."""
    def common_slot(concepts):
        profs = [store.type_profile[c] for c in concepts if store.type_profile[c]]
        if len(profs) < len(concepts) or not profs:
            return False
        inter = set(profs[0])
        for p in profs[1:]:
            inter &= p
        return len(inter) > 0
    return common_slot(subs) and common_slot(objs)


# ---------------------------------------------------------------------------
# ONE open-vocab read->grow loop for one seed + one arm.
#   arm in {"full", "no_confirm", "baseline"}.
# ---------------------------------------------------------------------------
def run_openvocab_loop(seed, arm):
    rng = np.random.default_rng(seed)
    concepts, cid_idx = build_ext_concepts()
    n_concept = len(concepts)
    C = _svo_make_phasors(rng, n_concept, N_DIM)
    roles = _svo_make_phasors(rng, 3, N_DIM)
    inv = {i: c for c, i in cid_idx.items()}

    known_nouns = set(ENTITIES)                    # MUTABLE: grows as entities are learned
    known_verbs = set(KNOWN_VERB_FORMS.keys())     # MUTABLE: grows as relations are learned
    known_rels = set(RELATIONS)                    # MUTABLE: grows with new relations

    store = FoundationStore(C, roles, cid_idx)

    buffer = defaultdict(list)                      # new_word -> list of {"triple","slot","kind"}
    confirmed_entities = set()
    grown_relations = set()
    per_sentence = []

    def commit_through_gate(triple):
        """route a well-formed triple through the ingest gate + hold machinery (as endtoend does)."""
        dec, info = store.gate(triple)
        store.decisions.append({"stage": "read", **info, "decision": dec})
        if dec == "ACCEPT":
            store.commit(triple)
        elif dec == "HOLD":
            store.held.append([triple, 0])
        store.reeval_holds()
        return dec

    for d in OPENVOCAB_CORPUS:
        text = d["text"]
        triples, metas, rule, freason = ie_extract_openvocab(text, known_nouns, known_verbs, known_rels)
        rec = {"text": text, "kind": d["kind"], "rule": rule, "fail_reason": freason}
        if not triples:
            rec.update(action="ABSTAIN")
            per_sentence.append(rec)
            continue
        triple, meta = triples[0], metas[0]
        is_new = meta["new_subj"] or meta["new_obj"] or meta["new_rel"]

        if not is_new:
            # known fact -> gate + grow (bootstrap + any later all-known sentence).
            dec = commit_through_gate(triple)
            rec.update(action="KNOWN", triple=list(triple), gate=dec)
            per_sentence.append(rec)
            continue

        if arm == "baseline":
            # v2 behavior: an unknown word -> abstain (no on-the-fly learning).
            rec.update(action="ABSTAIN_OOV", triple=list(triple))
            per_sentence.append(rec)
            continue

        # ---- FAST-MAP path (arm in {full, no_confirm}) ----
        if meta["new_rel"]:
            nw = meta["new_word"]
            s, r, o = triple
            if arm == "no_confirm":
                # grow on first sight (no confirm) -> commit immediately.
                if nw not in grown_relations:
                    grown_relations.add(nw); known_verbs.add(nw); known_rels.add(nw)
                dec = commit_through_gate(triple)
                rec.update(action="GROW_RELATION_NOCONFIRM", triple=list(triple), gate=dec)
            else:
                buffer[nw].append({"triple": triple, "slot": (r, SUBJ), "kind": "relation"})
                obs = buffer[nw]
                if len(obs) >= CONFIRM_K:
                    subs = [t["triple"][0] for t in obs]
                    objs = [t["triple"][2] for t in obs]
                    if _relation_args_coherent(subs, objs, store) and nw not in grown_relations:
                        grown_relations.add(nw); known_verbs.add(nw); known_rels.add(nw)
                        for t in obs:
                            commit_through_gate(t["triple"])
                        rec.update(action="GROW_RELATION_CONFIRMED", triple=list(triple))
                    else:
                        rec.update(action="RELATION_HELD_INCOHERENT", triple=list(triple))
                else:
                    rec.update(action="RELATION_PROVISIONAL", triple=list(triple))
            per_sentence.append(rec)
            continue

        # new ENTITY (new_subj xor new_obj)
        nw = meta["new_word"]
        s, r, o = triple
        role = SUBJ if meta["new_subj"] else OBJ
        if arm == "no_confirm":
            if nw not in known_nouns:
                known_nouns.add(nw)
            dec = commit_through_gate(triple)
            rec.update(action="ENTITY_NOCONFIRM", triple=list(triple), gate=dec, new_word=nw)
            per_sentence.append(rec)
            continue

        # FULL: buffer + cross-situational confirm.
        buffer[nw].append({"triple": triple, "slot": (r, role), "kind": "entity"})
        obs = buffer[nw]
        slot_set = set(t["slot"] for t in obs)
        if len(obs) >= CONFIRM_K:
            match = _coherent_with_grounded(slot_set, store)
            if match is not None and nw not in confirmed_entities:
                confirmed_entities.add(nw); known_nouns.add(nw)
                for t in obs:
                    commit_through_gate(t["triple"])
                rec.update(action="ENTITY_CONFIRMED", triple=list(triple), new_word=nw, type_match=match)
            elif match is None:
                rec.update(action="ENTITY_HELD_INCOHERENT", triple=list(triple), new_word=nw, slot_set=sorted(map(list, slot_set)))
            else:
                rec.update(action="ENTITY_ALREADY_CONFIRMED", triple=list(triple), new_word=nw)
        else:
            rec.update(action="ENTITY_PROVISIONAL", triple=list(triple), new_word=nw)
        per_sentence.append(rec)

    store.reeval_holds()
    accepted = store.accepted

    # ---- METRIC (a): new-entity fast-map accuracy ----
    entity_learned = {}
    for e in NEW_ENTITIES:
        facts = NEW_ENTITY_FACTS[e]
        all_in = all(f in accepted for f in facts)
        entity_learned[e] = bool((e in confirmed_entities or arm != "full") and all_in) if arm != "baseline" else False
        # for no_confirm/baseline confirmed_entities may be empty; base on facts-in-store.
        if arm != "full":
            entity_learned[e] = bool(all(f in accepted for f in facts))
    new_entity_fastmap_acc = float(np.mean([entity_learned[e] for e in NEW_ENTITIES]))

    # ---- METRIC (b): new-entity queryability over unique cues ----
    q_ok = 0
    q_total = 0
    query_detail = []
    for (s, r, o) in NEW_ENTITY_QUERY_CUES:
        q_total += 1
        in_store = (s, r, o) in accepted
        got = store.query(s, r) if in_store else None
        ok = bool(in_store and got == o)
        q_ok += int(ok)
        query_detail.append({"cue": [s, r], "expected": o, "got": got, "in_store": in_store, "ok": ok})
    new_entity_query_acc = (q_ok / float(q_total)) if q_total else 0.0

    # ---- METRIC (d): entity precision (mis-fast-map guard) ----
    entity_false = accepted & SHOULD_REJECT_ENTITY
    entity_false_fact_rate = len(entity_false) / float(len(SHOULD_REJECT_ENTITY))

    # ---- METRIC (c): new-relation handling ----
    rel_grown = all(f in accepted for f in NEW_RELATION_FACTS) and (NEW_RELATION in grown_relations or arm != "full")
    if arm == "baseline":
        rel_grown = False
    new_relation_grow_acc = 1.0 if rel_grown else 0.0
    relation_violation_rejected = RELATION_VIOLATION not in accepted
    relation_distractor_not_grown = RELATION_DISTRACTOR not in accepted and "wobbles" not in grown_relations
    relation_false = accepted & SHOULD_REJECT_RELATION
    relation_false_fact_rate = len(relation_false) / float(len(SHOULD_REJECT_RELATION))
    # relation-query
    rq_ok = 0
    for (s, r, o) in NEW_RELATION_FACTS:
        if (s, r, o) in accepted and store.query(s, r) == o:
            rq_ok += 1
    new_relation_query_acc = rq_ok / float(len(NEW_RELATION_FACTS))

    return {
        "seed": seed, "arm": arm,
        "n_accepted": len(accepted),
        "new_entity_fastmap_acc": new_entity_fastmap_acc,
        "new_entity_query_acc": new_entity_query_acc,
        "entity_false_fact_rate": entity_false_fact_rate,
        "n_entity_false": len(entity_false),
        "entity_learned": entity_learned,
        "n_confirmed_entities": len(confirmed_entities),
        "new_relation_grow_acc": new_relation_grow_acc,
        "new_relation_query_acc": new_relation_query_acc,
        "relation_violation_rejected": bool(relation_violation_rejected),
        "relation_distractor_not_grown": bool(relation_distractor_not_grown),
        "relation_false_fact_rate": relation_false_fact_rate,
        "n_grown_relations": len(grown_relations),
        "query_detail": query_detail,
        "accepted_hash": store.accepted_hash(),
        "accepted_sorted": sorted(accepted),
        "buffer_unconfirmed": {w: len(v) for w, v in buffer.items()
                               if w not in confirmed_entities and w not in grown_relations},
    }


def avg_arm(seeds, arm):
    runs = [run_openvocab_loop(s, arm) for s in seeds]
    keys_mean = ["new_entity_fastmap_acc", "new_entity_query_acc", "entity_false_fact_rate",
                 "new_relation_grow_acc", "new_relation_query_acc", "relation_false_fact_rate",
                 "n_accepted", "n_entity_false", "n_confirmed_entities", "n_grown_relations"]
    keys_all = ["relation_violation_rejected", "relation_distractor_not_grown"]
    out = {k: float(np.mean([r[k] for r in runs])) for k in keys_mean}
    out.update({k: bool(all(r[k] for r in runs)) for k in keys_all})
    out["per_seed"] = runs
    return out


# ---------------------------------------------------------------------------
# Verdict (envelope-fail-bands per pre-reg).
# ---------------------------------------------------------------------------
def compute_verdict(full, no_confirm, baseline):
    entity_hp = (
        full["new_entity_fastmap_acc"] >= 0.80 and
        full["new_entity_query_acc"] >= 0.80 and
        full["entity_false_fact_rate"] == 0.0 and
        baseline["new_entity_fastmap_acc"] == 0.0 and
        no_confirm["entity_false_fact_rate"] > full["entity_false_fact_rate"]
    )
    relation_pass = (
        full["new_relation_grow_acc"] >= 0.80 and
        full["relation_violation_rejected"] and
        full["relation_distractor_not_grown"] and
        full["relation_false_fact_rate"] == 0.0
    )
    hard_fail = (
        full["new_entity_fastmap_acc"] < 0.40 or
        full["entity_false_fact_rate"] == 1.0 or
        full["new_entity_query_acc"] < 0.40 or
        baseline["new_entity_fastmap_acc"] > 0.0
    )
    if hard_fail:
        tier = "HARD_FAIL"
    elif entity_hp and relation_pass:
        tier = "HARD_PASS"
    elif entity_hp:
        tier = "MIDDLE_BAND"
    else:
        tier = "MIDDLE_BAND"

    localize = []
    if not entity_hp:
        if full["new_entity_fastmap_acc"] < 0.80:
            localize.append("entity fast-map below bar (%.2f)" % full["new_entity_fastmap_acc"])
        if full["entity_false_fact_rate"] > 0.0:
            localize.append("entity precision breach (false_fact_rate=%.2f -- confirm guard leaked)" % full["entity_false_fact_rate"])
        if no_confirm["entity_false_fact_rate"] <= full["entity_false_fact_rate"]:
            localize.append("confirm guard not load-bearing (NO_CONFIRM false<=FULL false)")
    if entity_hp and not relation_pass:
        localize.append("relation track partial: grow=%.2f violation_rej=%s distractor_not_grown=%s false=%.2f"
                        % (full["new_relation_grow_acc"], full["relation_violation_rejected"],
                           full["relation_distractor_not_grown"], full["relation_false_fact_rate"]))
    weakest = localize if localize else ["none (entities fast-mapped + grounded, precision preserved)"]

    rel_caveat = ("RELATION evidence is CONSTRUCTION-grade (mechanical grow + arg-type guard; MEANING unverifiable, "
                  "no external referent) -- weaker than the grounded/type-verified ENTITY evidence.")
    msg = (f"{tier} | ENTITY fast-map: acc={full['new_entity_fastmap_acc']:.2f} query={full['new_entity_query_acc']:.2f} "
           f"false_fact_rate={full['entity_false_fact_rate']:.2f} (NO_CONFIRM false={no_confirm['entity_false_fact_rate']:.2f}, "
           f"BASELINE learned={baseline['new_entity_fastmap_acc']:.2f}) | "
           f"RELATION: grow={full['new_relation_grow_acc']:.2f} query={full['new_relation_query_acc']:.2f} "
           f"violation_rejected={full['relation_violation_rejected']} distractor_not_grown={full['relation_distractor_not_grown']} "
           f"false={full['relation_false_fact_rate']:.2f} | {rel_caveat} | weakest={weakest}")
    return tier, msg, weakest


# ---------------------------------------------------------------------------
# infra.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": "exp_read_grow_openvocab_fastmap_v1",
           "smoke": "exp_read_grow_openvocab_fastmap_v1_smoke",
           "self_test": "exp_read_grow_openvocab_fastmap_v1_selftest"}[run_mode]
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert the discriminators FIRE.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (open-vocab parser + FoundationStore + SVO encode/decode + "
          "imported learn_lexicon)...", flush=True)
    exercised = set()

    # (1) parser: known SVO parses; a new-entity sentence flags the new word; two unknowns abstain.
    kn = set(ENTITIES); kv = set(KNOWN_VERB_FORMS.keys()); kr = set(RELATIONS)
    tr, mt, rule, fr = ie_extract_openvocab("The cat eats the fish.", kn, kv, kr)
    assert tr == [("cat", "eats", "fish")] and not any(mt[0].values()), "known SVO broke"
    tr, mt, rule, fr = ie_extract_openvocab("The wug eats a seed.", kn, kv, kr)
    assert tr == [("wug", "eats", "seed")] and mt[0]["new_subj"] and rule == "NEW_ENTITY", "new-subj entity not flagged"
    tr, mt, rule, fr = ie_extract_openvocab("The cow lives in a narn.", kn, kv, kr)
    assert tr == [("cow", "lives_in", "narn")] and mt[0]["new_obj"], "new-obj entity not flagged"
    tr, mt, rule, fr = ie_extract_openvocab("The cat grims the dog.", kn, kv, kr)
    assert tr == [("cat", "grims", "dog")] and mt[0]["new_rel"] and rule == "NEW_RELATION", "new relation not flagged"
    tr, mt, rule, fr = ie_extract_openvocab("The wug grims the zib.", kn, kv, kr)
    assert tr == [] and fr and "unknown" in fr.lower(), "two-unknown sentence must abstain (elimination)"
    exercised.add("ie_extract_openvocab")

    # (2) FULL arm: learns the new entities (few-exposure), rejects the distractors, grows the relation.
    full = run_openvocab_loop(11, "full"); exercised.add("run_openvocab_loop")
    assert full["new_entity_fastmap_acc"] >= 0.99, f"FULL did not fast-map the new entities: {full['new_entity_fastmap_acc']}"
    assert full["new_entity_query_acc"] >= 0.80, f"FULL new-entity facts not queryable: {full['new_entity_query_acc']}"
    assert full["entity_false_fact_rate"] == 0.0, f"FULL leaked a mis-fast-map false fact: {full['entity_false_fact_rate']}"
    assert full["n_confirmed_entities"] == len(NEW_ENTITIES), f"FULL confirmed {full['n_confirmed_entities']} != {len(NEW_ENTITIES)}"

    # (3) NO_CONFIRM: admits the mis-fast-map false facts (confirm guard is load-bearing).
    noc = run_openvocab_loop(11, "no_confirm")
    assert noc["entity_false_fact_rate"] > full["entity_false_fact_rate"], \
        "confirm guard not load-bearing: NO_CONFIRM false_fact_rate must exceed FULL"

    # (4) BASELINE: abstains on OOV -> learns ZERO new entities (lift is real).
    base = run_openvocab_loop(11, "baseline")
    assert base["new_entity_fastmap_acc"] == 0.0, f"BASELINE unexpectedly learned new entities: {base['new_entity_fastmap_acc']}"
    assert base["new_relation_grow_acc"] == 0.0, "BASELINE unexpectedly grew a relation"

    # (5) ARMS-MUST-DIFFER (META_RULE_AF): the three arms produce different accepted stores.
    assert full["accepted_hash"] != noc["accepted_hash"], "META_RULE_AF: FULL vs NO_CONFIRM stores bit-identical"
    assert full["accepted_hash"] != base["accepted_hash"], "META_RULE_AF: FULL vs BASELINE stores bit-identical"

    # (6) relation track: grown + queryable + violation rejected + single-exposure distractor not grown.
    assert full["new_relation_grow_acc"] >= 0.99, f"relation not grown: {full['new_relation_grow_acc']}"
    assert full["relation_violation_rejected"], "grown relation admitted a type-violating arg"
    assert full["relation_distractor_not_grown"], "single-exposure new verb was grown (should abstain)"

    # (7) REAL imported lexicon primitive still grounds known words (the piece being integrated).
    foundation = build_typed_foundation()
    train = build_lexicon_train(np.random.default_rng(5), foundation, n_per_word_min=10)
    assoc, _ = _learn_lexicon(train, foundation, np.random.default_rng(9), role_gating=True, soft_me=True,
                              fast_map=True, n_dist_noun=2, n_dist_verb=2, p_drop=0.05, p_syst=0.0)
    top = _lexicon_top(assoc, foundation); exercised.add("learn_lexicon")
    macc = float(np.mean([top.get(w) == foundation["true_map"][w] for w in foundation["words"]]))
    assert macc >= 0.5, f"imported lexicon degenerate: mapping_acc={macc}"

    for ep in ["ie_extract_openvocab", "run_openvocab_loop", "learn_lexicon"]:
        assert ep in exercised, f"real_code_path: entrypoint {ep} not exercised"
    print(f"[self_test] PASS | FULL fastmap_acc={full['new_entity_fastmap_acc']:.2f} query={full['new_entity_query_acc']:.2f} "
          f"entity_false={full['entity_false_fact_rate']:.2f} (NO_CONFIRM entity_false={noc['entity_false_fact_rate']:.2f}, "
          f"BASELINE learned={base['new_entity_fastmap_acc']:.2f}) | relation grow={full['new_relation_grow_acc']:.2f} "
          f"violation_rej={full['relation_violation_rejected']} | lexicon_macc={macc:.3f}", flush=True)
    return True


# ---------------------------------------------------------------------------
# main.
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)

    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    seeds = [11, 23] if run_mode == "smoke" else [11, 23, 37, 41, 53]
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seeds) * 3               # 3 arms x seeds
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[openvocab] run_mode={run_mode} seeds={seeds} corpus={len(OPENVOCAB_CORPUS)} sentences "
          f"({len(NEW_ENTITIES)} new entities + 1 new relation + distractors)", flush=True)

    full = avg_arm(seeds, "full")
    no_confirm = avg_arm(seeds, "no_confirm")
    baseline = avg_arm(seeds, "baseline")
    print(f"[openvocab] FULL       fastmap_acc={full['new_entity_fastmap_acc']:.3f} query={full['new_entity_query_acc']:.3f} "
          f"entity_false={full['entity_false_fact_rate']:.3f} rel_grow={full['new_relation_grow_acc']:.3f}", flush=True)
    print(f"[openvocab] NO_CONFIRM entity_false={no_confirm['entity_false_fact_rate']:.3f} "
          f"fastmap_acc={no_confirm['new_entity_fastmap_acc']:.3f}", flush=True)
    print(f"[openvocab] BASELINE   fastmap_acc={baseline['new_entity_fastmap_acc']:.3f} "
          f"rel_grow={baseline['new_relation_grow_acc']:.3f}", flush=True)

    tier, msg, weakest = compute_verdict(full, no_confirm, baseline)
    elapsed = time.perf_counter() - t0

    def strip(a):
        return {k: v for k, v in a.items() if k != "per_seed"}

    metrics = {
        "verdict": tier,
        "verdict_msg": msg,
        "summary": msg[:300],
        "run_mode": run_mode,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "n_read_sentences": len(OPENVOCAB_CORPUS),
        "expected_n_units": expected_n_units,
        "weakest_interface": weakest,
        # METRIC (a) new-entity fast-map
        "metric_a_new_entity_fastmap_acc_full": full["new_entity_fastmap_acc"],
        "metric_a_new_entity_fastmap_acc_baseline": baseline["new_entity_fastmap_acc"],
        # METRIC (b) queryable foundation grows with new facts
        "metric_b_new_entity_query_acc_full": full["new_entity_query_acc"],
        # METRIC (c) new-relation handling (harder track)
        "metric_c_new_relation_grow_acc_full": full["new_relation_grow_acc"],
        "metric_c_new_relation_query_acc_full": full["new_relation_query_acc"],
        "metric_c_relation_violation_rejected": full["relation_violation_rejected"],
        "metric_c_relation_distractor_not_grown": full["relation_distractor_not_grown"],
        # METRIC (d) precision preserved
        "metric_d_entity_false_fact_rate_full": full["entity_false_fact_rate"],
        "metric_d_entity_false_fact_rate_no_confirm": no_confirm["entity_false_fact_rate"],
        "metric_d_relation_false_fact_rate_full": full["relation_false_fact_rate"],
        "arms": {
            "FULL_FASTMAP": strip(full),
            "NO_CONFIRM": strip(no_confirm),
            "ABSTAIN_BASELINE": strip(baseline),
        },
        "full_per_seed": full["per_seed"],
        "no_confirm_per_seed": no_confirm["per_seed"],
        "prereg": {
            "entity_hard_pass": "new_entity_fastmap_acc>=0.80 & new_entity_query_acc>=0.80 & entity_false_fact_rate==0 "
                                "& BASELINE fastmap_acc==0 & NO_CONFIRM false>FULL false",
            "relation_pass": "new_relation_grow_acc>=0.80 & violation_rejected & distractor_not_grown & relation_false==0",
            "overall_hard_pass": "entity HARD-PASS AND relation PASS",
            "overall_middle": "entity HARD-PASS AND relation NOT PASS (entities work, relations weaker -- honest expected)",
            "overall_hard_fail": "fastmap_acc<0.40 | entity_false_fact_rate==1.0 | query<0.40 | BASELINE learned>0",
            "confirm_k": CONFIRM_K,
            "new_entities": NEW_ENTITIES,
            "new_relation": NEW_RELATION,
            "honesty_caveat": "relation growth is CONSTRUCTION-grade (meaning unverifiable, no external referent); "
                              "entity fast-map is grounded + type-verified against the accumulated schema.",
            "compute_architecture": "sequential-CPU (foundation grows fact-by-fact; gate state depends on prior admits)",
            "storage_strategy": "sharded (one VSA vector per accepted fact)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["ie_extract_openvocab", "run_openvocab_loop", "learn_lexicon"],
            "crlb_n/a": "no quantitative noise floor; discriminator is the fast-map CONFIRM decision + ingest gate",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[openvocab] {tier} in {elapsed:.2f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[openvocab] {msg}", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _md = "full"
    try:
        if "--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv):
            _md = "smoke"
        elif "--self-test" in sys.argv or "self_test" in sys.argv:
            _md = "self_test"
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
