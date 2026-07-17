"""exp_read_grow_foundation_endtoend_v1 -- THE MAIN-LINE JOIN: read text -> grow a foundation, end-to-end, NO LLM.

QUESTION: wire the three separately-proven pieces into ONE loop for the first time -- the substrate READS a
small graded text corpus, PARSES it glass-box, uses its LEARNED lexicon to EXTRACT (s,r,o) facts, runs each
through the INGEST GATE (schema-fit / novelty / provisional-hold), and BUILDS a queryable foundation from
scratch. Then verify the grown foundation is correct + retrievable. Glass-box, no LLM, local numpy.

THE THREE PROVEN PIECES COMPOSED (reuse of mechanism, with provenance):
  (1) LEARNED LEXICON (chain-grade): experiments/exp_lexicon_learned_grounding_scaled_v1.py::learn_lexicon
      -- IMPORTED directly. Glass-box cross-situational word->concept disambiguation over ambiguous scenes.
  (2) GROUNDING / SVO parse+bind: experiments/exp_nativelang_svo_vsa_probe_v1.py::encode_meaning/decode_meaning
      -- IMPORTED directly. M = sum_i bind(role_i, filler_i); decode = unbind(role_i)+cleanup. Role-filler VSA.
  (3) INGEST GATE (banked): schema-fit accept/hold/reject. The banked cells
      (exp_curriculum_order_ingest_schema_fit_v1.py::ingest, exp_provisional_hold_bootstrap_arbitrary_order_v1.py,
      exp_multisource_arena_v1.py) gate over a GEOMETRIC displacement-graph. This cell FAITHFULLY RE-EXPRESSES
      that same accept-if-schema-fit>=tau / provisional-hold-until-support / novelty rule over TYPED TRIPLES
      (the read-corpus regime). The gate rule is identical in spirit (schema_fit = pairwise type compatibility
      of the triple's args against the relation's accumulated argument-type profile; provisional-hold when
      support is not yet grounded; anchor/bootstrap-accept before the schema is establishable). NOT the
      geometric ingest() verbatim -- re-expressed because the data format (typed triple) differs from the
      banked graph format. Flagged transparently.

THE SMALLEST HONEST END-TO-END LOOP (per read sentence, curriculum order):
  glass-box parse (positional SVO) -> learned-lexicon map words->concepts -> encode role-filler bundle ->
  decode (unbind+cleanup) EXTRACT (s,r,o) concept triple -> INGEST GATE decides accept/hold/reject ->
  write accepted facts to a growing SHARDED VSA foundation store. Then query stored facts by (s,r) cue.

ARMS / CONTROLS:
  (1) FULL_LOOP  = parse + learned-lexicon + gate + grow (the read->grow loop).
  (2) NO_GATE    = accept everything (no gate) -> does the gate improve foundation quality vs accept-all?
  (3) a CONTRADICTION / FALSE (type-violating) fact injected mid-stream -> does the SELF-GROWN schema
      reject/hold it (not corrupt the foundation)?  [2 injected false facts]
  (4) a NOVEL fact + an OUT-OF-ORDER (provisional-hold) fact late in the stream -> does the foundation
      grow to include the novel entity + become queryable, and does the held fact release on support?

METRICS (reported SEPARATELY, never blobbed):
  (a) EXTRACTION accuracy   = decoded concept-triple == ground-truth triple (learned-lexicon o parse).
  (b) FOUNDATION correctness = precision (accepted has no false fact) + recall (accepted has the true facts).
  (c) QUERY accuracy        = retrieve a stored object given an (s,r) cue via the VSA store.
  (d) GATE behavior         = accept-true rate + reject-or-hold-false rate.
  Plus LOCALIZATION diagnostics (mapping_acc, oracle-lexicon extraction, store round-trip) so a fail
  attributes to a SPECIFIC interface: parse->lexicon / lexicon->triple / triple->gate / gate->store / store->query.

PRE-REG (envelope-fail-bands; I own the bands):
  HARD-PASS (loop reads corpus + builds a CORRECT queryable foundation glass-box):
    extraction_acc >= 0.90 AND FULL_LOOP foundation precision == 1.0 (excludes both false facts) AND
    FULL_LOOP true-recall >= 0.90 AND accept_false_rate == 0.0 AND accept_true_rate >= 0.85 AND
    FULL_LOOP precision >= NO_GATE precision + 0.05 (gate beats accept-all) AND novel fact accepted+queryable
    AND query_acc >= 0.85.
  HARD-FAIL (loop breaks): extraction_acc < 0.50 (can't read) OR accept_false_rate == 1.0 (gate lets the
    false fact corrupt the store) OR accept_true_rate < 0.50 (gate rejects true facts) OR FULL_LOOP
    precision < 0.70 (foundation corrupts) OR query_acc < 0.50 (can't retrieve).
  MIDDLE otherwise. If HARD-FAIL -> localize WHICH interface breaks + report; do NOT over-read a partial loop.

Local numpy, no queue/GPU/atoms/push. ASCII-only. FHRR = complex128 unit phasors. Sequential-CPU (genuine
sequential dependency: foundation grows fact-by-fact, gate state depends on prior admissions -> chained).
Storage: SHARDED (each accepted fact its own VSA vector) per META_STORAGE_STRATEGY (facts are composed/retrieved).
Compute: V ~ 25 concepts, N=1024, <=5 seeds, ~24 read sentences -> wall < 10s. progress_logging=print_flush_true.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; FULL_LOOP vs NO_GATE accepted-store hash differs)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no quantitative noise floor; FHRR cleanup among ~25 concepts at N=1024 with 3-term bundle is
#     z ~ sqrt(2N/3) ~ 26 sigma -> decode reachable ~1.0; extraction is gated by LEXICON map errors not noise.
# - baseline_in_band at smoke: NO_GATE precision < 1.0 (admits false facts); FULL_LOOP precision target 1.0;
#     RANDOM-lexicon control extraction ~ chance (1/V) -> not saturated.
# - discriminator survives scale: scale is FIXED (small corpus); discriminator = gate-vs-nogate precision +
#     accept_false_rate. Fires because the injected false fact is a deterministic type-violation the grown
#     schema catches (verified at smoke: FULL rejects it, NO_GATE admits it).
# - HARD_PASS strictly above floor + margins declared in prereg JSON.
# - real_code_path (F.1): self_test constructs the REAL objects (imported learn_lexicon + encode/decode_meaning
#     + FoundationStore) at tiny scale and asserts (not a synthetic-only branch).
# - deterministic seeding (F.5): fixed int seeds; sorted() vocab ordering; NO hash()/list(set()) for seeds/splits.
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
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_grow_foundation_endtoend_v1"
N_DIM = 1024

# --- PIECE 1 + 2: genuine imports of the proven mechanisms (reuse, not rebuild) ---
# FHRR primitives + role-filler SVO parse+bind (exp_nativelang_svo_vsa_probe_v1).
from experiments.exp_nativelang_svo_vsa_probe_v1 import (
    make_phasors as _svo_make_phasors,
    bind as _bind,
    unbind as _unbind,
    cleanup as _cleanup,
    encode_meaning as _encode_meaning,   # M = sum_i bind(role_i, filler_i)
    decode_meaning as _decode_meaning,   # unbind(role_i) + cleanup -> recovered slot-tuple
)
# Glass-box cross-situational lexicon learner (exp_lexicon_learned_grounding_scaled_v1).
from experiments.exp_lexicon_learned_grounding_scaled_v1 import (
    learn_lexicon as _learn_lexicon,
    lexicon_top as _lexicon_top,
)

# ---------------------------------------------------------------------------
# CORPUS + GROUND TRUTH (small graded SVO set; curriculum order; per-sentence GT triple + gate label).
# concept == surface token here (as in the proven lexicon cell); the learner never receives the map --
# it must recover which concept each token denotes by cross-situational disambiguation over ambiguous scenes.
# Ground-truth TYPES below are used ONLY to build scenes + score foundation-correctness; the GATE never sees
# them (it INFERS argument-type profiles from accepted facts).
# ---------------------------------------------------------------------------
# concept -> ground-truth semantic type (metric-only; gate infers its own type clusters)
GT_TYPE = {
    # animals
    "cat": "animal", "dog": "animal", "bird": "animal", "fish": "animal", "frog": "animal",
    "cow": "animal", "owl": "animal", "kitten": "animal", "mouse": "animal",
    # foods
    "seed": "food", "worm": "food", "grass": "food", "bread": "food", "apple": "food",
    # places
    "barn": "food_or_place_placeholder",  # overwritten below
}
GT_TYPE.update({"barn": "place", "nest": "place", "pond": "place", "tree": "place", "field": "place"})
RELATIONS = ["eats", "lives_in", "chases"]
# GT relation argument-type signature (metric/design only; gate never receives it)
GT_REL_SIG = {"eats": ("animal", "food"), "lives_in": ("animal", "place"), "chases": ("animal", "animal")}

ANIMALS = sorted([c for c, t in GT_TYPE.items() if t == "animal"])
FOODS = sorted([c for c, t in GT_TYPE.items() if t == "food"])
PLACES = sorted([c for c, t in GT_TYPE.items() if t == "place"])
ENTITIES = sorted(ANIMALS + FOODS + PLACES)   # all "nouns" for the lexicon (role-gating = noun-vs-verb)

# gate labels: TRUE_ACCEPT (should be admitted), FALSE_REJECT (type-violation; must NOT corrupt store),
# NOVEL (new entity slotting into known schema -> admit + queryable), HOLD_THEN_ACCEPT (out-of-order;
# provisional-hold then release on support).
# READ_CORPUS: list of (subj, rel, obj, gate_label). Curriculum order: foundational TRUE block first
# (bootstraps the schema), then schema-checkable TRUE facts, then the mid-stream FALSE injection, then the
# NOVEL + out-of-order HOLD facts.
READ_CORPUS = [
    # -- foundational block (curriculum: establishes the relation argument-type profiles) --
    ("cat", "eats", "fish", "TRUE_ACCEPT"),
    ("dog", "eats", "bread", "TRUE_ACCEPT"),
    ("cow", "eats", "grass", "TRUE_ACCEPT"),
    ("bird", "eats", "seed", "TRUE_ACCEPT"),
    ("frog", "eats", "worm", "TRUE_ACCEPT"),
    ("cat", "lives_in", "barn", "TRUE_ACCEPT"),
    ("dog", "lives_in", "barn", "TRUE_ACCEPT"),
    ("bird", "lives_in", "nest", "TRUE_ACCEPT"),
    ("fish", "lives_in", "pond", "TRUE_ACCEPT"),
    ("frog", "lives_in", "pond", "TRUE_ACCEPT"),
    ("cat", "chases", "bird", "TRUE_ACCEPT"),
    ("dog", "chases", "cat", "TRUE_ACCEPT"),
    ("bird", "chases", "frog", "TRUE_ACCEPT"),
    # -- schema-checkable TRUE facts (gate now has argument-type profiles) --
    ("cow", "lives_in", "field", "TRUE_ACCEPT"),   # field: novel PLACE filler into known lives_in schema
    ("frog", "eats", "seed", "TRUE_ACCEPT"),
    ("cat", "eats", "worm", "TRUE_ACCEPT"),
    # -- FALSE injection (mid-stream, schema-checkable, TYPE-VIOLATING) --
    ("cat", "eats", "barn", "FALSE_REJECT"),       # barn=place; eats-objects are foods -> type mismatch
    ("bird", "lives_in", "worm", "FALSE_REJECT"),  # worm=food; lives_in-objects are places -> type mismatch
    # -- OUT-OF-ORDER (provisional-hold-bootstrap): both concepts ungrounded on arrival -> HOLD --
    ("kitten", "chases", "mouse", "HOLD_THEN_ACCEPT"),
    # -- support arrives (grounds kitten + mouse as eats-subjects=animal-like) -> held fact releases --
    ("kitten", "eats", "seed", "NOVEL"),
    ("mouse", "eats", "grass", "NOVEL"),
    # -- NOVEL entity late (owl) slots into known schema -> admit + queryable --
    ("owl", "eats", "worm", "NOVEL"),
    ("owl", "lives_in", "nest", "NOVEL"),
]

# Facts that SHOULD end up admitted (ground-truth accept-set for precision/recall).
SHOULD_ACCEPT = set((s, r, o) for (s, r, o, lab) in READ_CORPUS if lab != "FALSE_REJECT")
SHOULD_REJECT = set((s, r, o) for (s, r, o, lab) in READ_CORPUS if lab == "FALSE_REJECT")

# ---------------------------------------------------------------------------
# Foundation dict compatible with the imported learn_lexicon + its internal build_scene.
# (concept_id == token; role-gating category = noun-vs-verb; companions disabled for a clean lexicon.)
# ---------------------------------------------------------------------------
def build_typed_foundation():
    nouns = sorted(ENTITIES)
    verbs = sorted(RELATIONS)
    words = sorted(nouns + verbs)
    concept_ids = sorted(set(nouns) | set(verbs))
    cid_idx = {c: i for i, c in enumerate(concept_ids)}
    return {
        "words": words, "nouns": nouns, "verbs": verbs,
        "concept_ids": concept_ids, "cid_idx": cid_idx,
        "true_map": {w: w for w in words},
        "noun_concepts": set(nouns), "verb_concepts": set(verbs),
        "companion": {w: [] for w in nouns},   # no systematic confound -> clean lexicon (I own regime)
        "V": len(words), "V_noun": len(nouns), "V_verb": len(verbs),
    }

def build_lexicon_train(rng, foundation, n_per_word_min=14):
    """Grounded SVO training corpus over the vocab for the LEXICON-LEARNING phase (separate exposure from the
    read corpus). Coverage-seeded (every animal as subj + as obj-eligible, every relation) then random fill,
    so every read-corpus token gets >= n_per_word_min exposures. Type-consistent (animal rel food/place/animal)."""
    animals, foods, places = ANIMALS, FOODS, PLACES
    seen = set()
    train = []

    def add(s, r, o):
        t = (s, r, o)
        if s != o and t not in seen:
            seen.add(t)
            train.append(t)

    # coverage: each animal subj across each relation with a type-consistent object.
    for i, a in enumerate(animals):
        add(a, "eats", foods[i % len(foods)])
        add(a, "lives_in", places[i % len(places)])
        add(a, "chases", animals[(i + 1) % len(animals)])
    # random type-consistent fill until every token is well-exposed.
    counts = defaultdict(int)
    for (s, r, o) in train:
        counts[s] += 1; counts[r] += 1; counts[o] += 1
    guard = 0
    target = n_per_word_min
    while guard < 20000 and min(counts.get(w, 0) for w in (animals + foods + places + RELATIONS)) < target:
        guard += 1
        a = animals[rng.integers(len(animals))]
        r = RELATIONS[rng.integers(len(RELATIONS))]
        if r == "eats":
            o = foods[rng.integers(len(foods))]
        elif r == "lives_in":
            o = places[rng.integers(len(places))]
        else:
            o = animals[rng.integers(len(animals))]
        add(a, r, o)
        counts[a] += 1; counts[r] += 1; counts[o] += 1
    return train

# ---------------------------------------------------------------------------
# INGEST GATE + growing SHARDED VSA foundation store (faithful re-expression of the banked schema-fit /
# provisional-hold / novelty gate over typed triples).
# ---------------------------------------------------------------------------
SUBJ, VERB, OBJ = 0, 1, 2

class FoundationStore:
    # permissive_until = the PERMISSIVE->SELECTIVE schedule switch (banked build recipe): early on the
    # substrate accepts axiom/grounding facts freely to bootstrap the foundation (a concept's earliest
    # exposures ARE its grounding -- you do not reject a learner's first sentences); once the foundation
    # is mature it gates SELECTIVELY (both-novel -> provisional-hold; type-violations always rejected).
    def __init__(self, C, roles, cid_idx, tau_accept=0.20, tau_reject=0.05, min_members=2,
                 max_hold_passes=3, permissive_until=13):
        self.C = C                       # (n_concept, N) concept phasor codebook
        self.roles = roles               # (3, N) SUBJ/VERB/OBJ role phasors
        self.cid_idx = cid_idx
        self.tau_accept = tau_accept
        self.tau_reject = tau_reject
        self.min_members = min_members
        self.max_hold_passes = max_hold_passes
        self.permissive_until = permissive_until
        self.accepted = set()            # set of (s, r, o) concept triples
        self.store_M = []                # SHARDED: one VSA vector per accepted fact
        self.store_T = []                # parallel list of (s, r, o)
        self.type_profile = defaultdict(set)   # concept -> set of (rel, role) slots it has filled (accepted only)
        self.rel_members = defaultdict(lambda: {SUBJ: set(), OBJ: set()})  # rel -> {role: set(concepts)}
        self.held = []                   # provisional-hold queue: list of [ (s,r,o), passes ]
        self.decisions = []              # per-sentence gate log (glass-box)

    def _grounded(self, c):
        return len(self.type_profile[c]) > 0

    def _typesim(self, a, b):
        pa, pb = self.type_profile[a], self.type_profile[b]
        if not pa or not pb:
            return None                  # undefined (a novel concept) -> NOVELTY signal, not a fit score
        inter = len(pa & pb)
        union = len(pa | pb)
        return inter / float(union) if union else 0.0

    def _slot_fit(self, concept, rel, role):
        """max pairwise type-compat of `concept` against concepts already accepted in (rel, role).
        Returns (fit, status): status in {FIT, NOVEL_CONCEPT, NO_MEMBERS}."""
        members = [m for m in self.rel_members[rel][role] if m != concept]
        if not members:
            return None, "NO_MEMBERS"
        if not self._grounded(concept):
            return None, "NOVEL_CONCEPT"
        sims = [self._typesim(concept, m) for m in members]
        sims = [x for x in sims if x is not None]
        if not sims:
            return None, "NOVEL_CONCEPT"
        return max(sims), "FIT"

    def _schema_checkable(self, rel):
        rm = self.rel_members[rel]
        return len(rm[SUBJ]) >= self.min_members and len(rm[OBJ]) >= self.min_members

    def gate(self, triple):
        """accept/hold/reject decision for a candidate concept triple. Glass-box; returns (decision, info)."""
        s, r, o = triple
        info = {"triple": triple}
        # bootstrap / anchor: before the relation's argument-type profile is establishable, admit (curriculum
        # foundational facts ground the schema; analogous to anchor-grounded nodes sf=1.0 in the banked ingest).
        if not self._schema_checkable(r):
            info.update(reason="BOOTSTRAP_ANCHOR")
            return "ACCEPT", info
        sfit, sstat = self._slot_fit(s, r, SUBJ)
        ofit, ostat = self._slot_fit(o, r, OBJ)
        info.update(subj_fit=sfit, subj_status=sstat, obj_fit=ofit, obj_status=ostat)
        # novelty routing: a novel (ungrounded) concept in exactly one slot, the other slot fitting -> admit
        # the new entity into the known schema; BOTH slots novel -> insufficient support -> provisional HOLD.
        s_novel = (sstat == "NOVEL_CONCEPT")
        o_novel = (ostat == "NOVEL_CONCEPT")
        if s_novel and o_novel:
            # PERMISSIVE phase: ground both novel concepts (axiom/grounding fact). SELECTIVE phase: hold
            # until support arrives (the out-of-order provisional-hold-bootstrap case).
            if len(self.accepted) < self.permissive_until:
                info.update(reason="ACCEPT_PERMISSIVE_GROUNDING")
                return "ACCEPT", info
            info.update(reason="HOLD_BOTH_NOVEL")
            return "HOLD", info
        if s_novel or o_novel:
            other_fit = ofit if s_novel else sfit
            other_stat = ostat if s_novel else sstat
            # the grounded slot must FIT (not be a type violation) to admit the novel entity.
            if other_stat == "NO_MEMBERS" or (other_fit is not None and other_fit > self.tau_reject):
                info.update(reason="ACCEPT_NOVEL_ENTITY")
                return "ACCEPT", info
            info.update(reason="REJECT_NOVEL_WITH_VIOLATION")
            return "REJECT", info
        # both slots grounded + members present -> pairwise schema fit = min over the two roles.
        fits = [f for f in (sfit, ofit) if f is not None]
        if not fits:
            info.update(reason="HOLD_NO_FIT_DEFINED")
            return "HOLD", info
        schema_fit = min(fits)
        info.update(schema_fit=schema_fit)
        if schema_fit >= self.tau_accept:
            info.update(reason="ACCEPT_SCHEMA_FIT")
            return "ACCEPT", info
        if schema_fit <= self.tau_reject:
            info.update(reason="REJECT_TYPE_VIOLATION")
            return "REJECT", info
        info.update(reason="HOLD_MIDBAND")
        return "HOLD", info

    def commit(self, triple):
        s, r, o = triple
        if triple in self.accepted:
            return
        self.accepted.add(triple)
        si, ri, oi = self.cid_idx[s], self.cid_idx[r], self.cid_idx[o]
        M = _encode_meaning((si, ri, oi), self.C, self.roles)   # SHARDED: one vector per fact
        self.store_M.append(M)
        self.store_T.append(triple)
        self.type_profile[s].add((r, SUBJ))
        self.type_profile[o].add((r, OBJ))
        self.rel_members[r][SUBJ].add(s)
        self.rel_members[r][OBJ].add(o)

    def reeval_holds(self):
        """provisional-hold-bootstrap: retry held facts as support accrues; drop after max passes."""
        still = []
        for item in self.held:
            triple, passes = item
            dec, info = self.gate(triple)
            if dec == "ACCEPT":
                self.commit(triple)
                self.decisions.append({"stage": "hold_release", **info, "decision": "ACCEPT"})
            elif dec == "REJECT":
                self.decisions.append({"stage": "hold_release", **info, "decision": "REJECT"})
            else:
                passes += 1
                if passes < self.max_hold_passes:
                    still.append([triple, passes])
                else:
                    self.decisions.append({"stage": "hold_expire", **info, "decision": "DROP"})
        self.held = still

    def query(self, s, r):
        """VSA associative retrieval: cue = bind(SUBJ,s)+bind(VERB,r); pick nearest stored fact; unbind OBJ+cleanup.
        Returns recovered object concept string, or None if store empty."""
        if not self.store_M:
            return None
        si, ri = self.cid_idx[s], self.cid_idx[r]
        cue = _bind(self.roles[SUBJ], self.C[si]) + _bind(self.roles[VERB], self.C[ri])
        Mst = np.stack(self.store_M, axis=0)          # (F, N)
        scores = (Mst.conj() @ cue).real              # match fact whose (subj,verb) aligns
        j = int(np.argmax(scores))
        oi = _cleanup(_unbind(self.store_M[j], self.roles[OBJ]), self.C)
        # map concept index back to string
        for c, idx in self.cid_idx.items():
            if idx == oi:
                return c
        return None

    def accepted_hash(self):
        payload = "|".join(",".join(t) for t in sorted(self.accepted)).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

# ---------------------------------------------------------------------------
# ONE end-to-end loop for one seed + one arm (use_gate True=FULL_LOOP, False=NO_GATE), one lexicon (learned/oracle/random).
# ---------------------------------------------------------------------------
def run_loop(seed, use_gate, lexicon_kind="learned"):
    rng = np.random.default_rng(seed)
    scene_rng = np.random.default_rng(seed * 7 + 1)
    foundation = build_typed_foundation()
    cid_idx = foundation["cid_idx"]
    n_concept = len(foundation["concept_ids"])
    # concept phasor codebook + role vectors (fixed per seed).
    C = _svo_make_phasors(rng, n_concept, N_DIM)                 # (n_concept, N)
    roles = _svo_make_phasors(rng, 3, N_DIM)                     # SUBJ / VERB / OBJ

    # --- PIECE 1: LEARN the lexicon (glass-box cross-situational; gentle ambiguity so it is reliable) ---
    if lexicon_kind == "random":
        top_map = {w: foundation["concept_ids"][rng.integers(n_concept)] for w in foundation["words"]}
        mapping_acc = float(np.mean([top_map[w] == foundation["true_map"][w] for w in foundation["words"]]))
    elif lexicon_kind == "oracle":
        top_map = dict(foundation["true_map"])
        mapping_acc = 1.0
    else:  # learned
        train = build_lexicon_train(rng, foundation, n_per_word_min=14)
        assoc, _ = _learn_lexicon(
            train, foundation, scene_rng,
            role_gating=True, soft_me=True, fast_map=True,
            n_dist_noun=2, n_dist_verb=2, p_drop=0.05, p_syst=0.0,  # gentle ambiguity (I own regime)
        )
        top_map = _lexicon_top(assoc, foundation)
        tm = foundation["true_map"]
        mapping_acc = float(np.mean([top_map.get(w) == tm[w] for w in foundation["words"]]))

    store = FoundationStore(C, roles, cid_idx)

    # --- PIECE 2 + 3: READ each sentence -> parse+bind -> EXTRACT triple -> GATE -> GROW ---
    n_extract_ok = 0
    n_sent = len(READ_CORPUS)
    per_sentence = []
    for (s_w, r_w, o_w, label) in READ_CORPUS:
        # glass-box positional SVO parse -> (subj, verb, obj) surface tokens
        words = (s_w, r_w, o_w)
        # learned-lexicon map words -> concepts; encode role-filler bundle; decode -> extracted concept triple
        try:
            learned_concepts = tuple(top_map.get(w) for w in words)
            filler_idx = tuple(cid_idx[c] if c in cid_idx else 0 for c in learned_concepts)
            M = _encode_meaning(filler_idx, C, roles)
            dec_idx = _decode_meaning(M, C, roles, 3)
            inv = {v: k for k, v in cid_idx.items()}
            extracted = tuple(inv[i] for i in dec_idx)
        except Exception as ex:  # attributable interface failure, never silent
            per_sentence.append({"words": words, "stage_fail": "parse_lexicon", "err": repr(ex)})
            continue
        gt_triple = (s_w, r_w, o_w)
        extract_ok = (extracted == gt_triple)
        if extract_ok:
            n_extract_ok += 1
        # the triple fed to the gate is what the loop EXTRACTED (not the GT) -- genuine end-to-end.
        cand = extracted
        rec = {"words": words, "gt": gt_triple, "extracted": extracted, "extract_ok": extract_ok, "label": label}
        # only well-formed extracted triples (known rel + distinct s,o) proceed to the gate; else record.
        well_formed = (cand[1] in RELATIONS and cand[0] != cand[2] and cand[0] in ENTITIES and cand[2] in (ENTITIES))
        if not well_formed:
            rec.update(gate="SKIP_MALFORMED")
            per_sentence.append(rec)
            continue
        if use_gate:
            dec, info = store.gate(cand)
            rec.update(gate=dec, gate_reason=info.get("reason"))
            store.decisions.append({"stage": "read", **info, "decision": dec})
            if dec == "ACCEPT":
                store.commit(cand)
            elif dec == "HOLD":
                store.held.append([cand, 0])
            # REJECT -> drop
            store.reeval_holds()
        else:
            rec.update(gate="ACCEPT_NOGATE")
            store.commit(cand)
        per_sentence.append(rec)
    # final hold flush (a held fact whose support arrived on the last sentence)
    if use_gate:
        store.reeval_holds()

    extraction_acc = n_extract_ok / float(n_sent)

    # --- METRIC (b): FOUNDATION correctness (dict of accepted concept triples vs GT accept-set) ---
    # only score triples that were extracted correctly enough to BE the intended fact; but precision/recall
    # measured over the store's accepted set vs ground-truth accept/reject sets (the honest foundation quality).
    accepted = store.accepted
    n_false_in_store = len(accepted & SHOULD_REJECT)
    true_in_store = accepted & SHOULD_ACCEPT
    precision = (len(true_in_store) / float(len(accepted))) if accepted else 0.0
    true_recall = len(true_in_store) / float(len(SHOULD_ACCEPT))
    accept_false_rate = (n_false_in_store / float(len(SHOULD_REJECT))) if SHOULD_REJECT else 0.0

    # --- METRIC (d): GATE behavior over correctly-extracted, well-formed candidates ---
    # accept_true_rate = of the TRUE facts the loop correctly extracted, how many did the gate admit.
    true_extracted = [r for r in per_sentence if r.get("extract_ok") and r.get("label") in ("TRUE_ACCEPT", "NOVEL")]
    true_accepted = [r for r in true_extracted if (r.get("triple_in_store") if False else r["gt"] in accepted)]
    accept_true_rate = (len(true_accepted) / float(len(true_extracted))) if true_extracted else 0.0

    # --- METRIC (c): QUERY accuracy (VSA retrieval over the grown store) ---
    q_total = 0
    q_ok = 0
    # object-set per (s,r) among accepted true facts
    obj_sets = defaultdict(set)
    for (s, r, o) in accepted:
        if (s, r, o) in SHOULD_ACCEPT:
            obj_sets[(s, r)].add(o)
    for (s, r), objs in sorted(obj_sets.items()):
        got = store.query(s, r)
        q_total += 1
        if got in objs:
            q_ok += 1
    query_acc = (q_ok / float(q_total)) if q_total else 0.0

    # --- targeted NOVEL + HOLD queryability checks ---
    novel_owl_ok = ("owl", "eats", "worm") in accepted and store.query("owl", "eats") == "worm"
    novel_owl_place_ok = ("owl", "lives_in", "nest") in accepted
    hold_release_ok = ("kitten", "chases", "mouse") in accepted   # provisional-hold released on support
    kitten_query_ok = store.query("kitten", "eats") in obj_sets.get(("kitten", "eats"), {"seed"})

    # --- store round-trip (localizes gate->store / store->query): write then read each accepted true fact ---
    rt_total = 0
    rt_ok = 0
    for (s, r, o) in sorted(true_in_store):
        rt_total += 1
        if store.query(s, r) in obj_sets.get((s, r), {o}):
            rt_ok += 1
    store_roundtrip_acc = (rt_ok / float(rt_total)) if rt_total else 0.0

    return {
        "seed": seed, "use_gate": use_gate, "lexicon_kind": lexicon_kind,
        "mapping_acc": mapping_acc,
        "extraction_acc": extraction_acc,
        "n_sentences": n_sent,
        "n_accepted": len(accepted),
        "foundation_precision": precision,
        "true_recall": true_recall,
        "accept_false_rate": accept_false_rate,
        "n_false_in_store": n_false_in_store,
        "accept_true_rate": accept_true_rate,
        "query_acc": query_acc,
        "store_roundtrip_acc": store_roundtrip_acc,
        "novel_owl_ok": bool(novel_owl_ok),
        "novel_owl_place_ok": bool(novel_owl_place_ok),
        "hold_release_ok": bool(hold_release_ok),
        "kitten_query_ok": bool(kitten_query_ok),
        "accepted_hash": store.accepted_hash(),
        "accepted_sorted": sorted(accepted),
    }

def avg_arm(seeds, use_gate, lexicon_kind="learned"):
    runs = [run_loop(s, use_gate, lexicon_kind) for s in seeds]
    keys_mean = ["mapping_acc", "extraction_acc", "foundation_precision", "true_recall",
                 "accept_false_rate", "accept_true_rate", "query_acc", "store_roundtrip_acc",
                 "n_accepted", "n_false_in_store"]
    keys_all = ["novel_owl_ok", "novel_owl_place_ok", "hold_release_ok", "kitten_query_ok"]
    out = {k: float(np.mean([r[k] for r in runs])) for k in keys_mean}
    out.update({k: bool(all(r[k] for r in runs)) for k in keys_all})
    out["per_seed"] = runs
    return out

# ---------------------------------------------------------------------------
# Verdict.
# ---------------------------------------------------------------------------
def compute_verdict(full, nogate, oracle, random_ctrl):
    hp = (
        full["extraction_acc"] >= 0.90 and
        full["foundation_precision"] >= 1.0 and
        full["true_recall"] >= 0.90 and
        full["accept_false_rate"] == 0.0 and
        full["accept_true_rate"] >= 0.85 and
        (full["foundation_precision"] - nogate["foundation_precision"]) >= 0.05 and
        full["novel_owl_ok"] and full["hold_release_ok"] and
        full["query_acc"] >= 0.85
    )
    hf = (
        full["extraction_acc"] < 0.50 or
        full["accept_false_rate"] == 1.0 or
        full["accept_true_rate"] < 0.50 or
        full["foundation_precision"] < 0.70 or
        full["query_acc"] < 0.50
    )
    if hp:
        tier = "HARD_PASS"
    elif hf:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"
    # localization: which interface is weakest (attributable)
    localize = []
    if full["extraction_acc"] < 0.90:
        if oracle["extraction_acc"] >= 0.90:
            localize.append("parse->lexicon (oracle-lexicon parses fine; learned map is the bottleneck)")
        else:
            localize.append("lexicon->triple (role-filler parse fails even with oracle lexicon)")
    if full["accept_false_rate"] > 0.0:
        localize.append("triple->gate (gate admitted a type-violating false fact)")
    if full["true_recall"] < 0.90:
        localize.append("triple->gate (gate rejected/held true facts)")
    if full["store_roundtrip_acc"] < full["extraction_acc"] - 0.05:
        localize.append("gate->store / store->query (accepted facts not retrievable)")
    if full["query_acc"] < 0.85 and full["store_roundtrip_acc"] >= 0.85:
        localize.append("store->query (round-trip ok but multi-object cue retrieval degrades)")
    weakest = localize if localize else ["none (all interfaces at/above target)"]
    msg = (f"{tier} | extract={full['extraction_acc']:.3f} (oracle={oracle['extraction_acc']:.3f}, "
           f"random={random_ctrl['extraction_acc']:.3f}) | foundation_prec FULL={full['foundation_precision']:.3f} "
           f"vs NO_GATE={nogate['foundation_precision']:.3f} | true_recall={full['true_recall']:.3f} | "
           f"accept_false_rate={full['accept_false_rate']:.3f} | accept_true_rate={full['accept_true_rate']:.3f} | "
           f"query_acc={full['query_acc']:.3f} | novel_owl={full['novel_owl_ok']} hold_release={full['hold_release_ok']} | "
           f"weakest_interface={weakest}")
    return tier, msg, weakest

# ---------------------------------------------------------------------------
# infra: start-marker / crash-metrics / atomic write.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = "exp_read_grow_foundation_endtoend_v1" if run_mode == "full" else \
          ("exp_read_grow_foundation_endtoend_v1_smoke" if run_mode == "smoke" else
           "exp_read_grow_foundation_endtoend_v1_selftest")
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d

def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": __import__("platform").node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")

def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")   # atomic per META_RULE_AH

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
# self-test: EXERCISE THE REAL code path (imported learn_lexicon + encode/decode + FoundationStore) at tiny
# scale + assert core behaviors (F.1 real_code_path).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (imported learn_lexicon + SVO encode/decode + FoundationStore)...", flush=True)
    exercised = set()
    # real SVO parse+bind round-trip at tiny scale.
    rng = np.random.default_rng(3)
    C = _svo_make_phasors(rng, 8, 256); exercised.add("make_phasors")
    roles = _svo_make_phasors(rng, 3, 256)
    M = _encode_meaning((1, 4, 6), C, roles); exercised.add("encode_meaning")
    dec = _decode_meaning(M, C, roles, 3); exercised.add("decode_meaning")
    assert dec == (1, 4, 6), f"SVO round-trip failed: {dec}"
    # real lexicon learner over a tiny grounded corpus.
    foundation = build_typed_foundation()
    train = build_lexicon_train(np.random.default_rng(5), foundation, n_per_word_min=10)
    assoc, _ = _learn_lexicon(train, foundation, np.random.default_rng(9),
                              role_gating=True, soft_me=True, fast_map=True,
                              n_dist_noun=2, n_dist_verb=2, p_drop=0.05, p_syst=0.0)
    top = _lexicon_top(assoc, foundation); exercised.add("learn_lexicon")
    macc = float(np.mean([top.get(w) == foundation["true_map"][w] for w in foundation["words"]]))
    assert macc >= 0.5, f"lexicon learner degenerate in self-test: mapping_acc={macc}"
    # real end-to-end single seed (FULL_LOOP) + assertions on gate + store.
    full = run_loop(11, use_gate=True, lexicon_kind="learned"); exercised.add("run_loop")
    nogate = run_loop(11, use_gate=False, lexicon_kind="learned")
    assert full["extraction_acc"] > 0.0, "extraction cratered in self-test"
    assert full["accepted_hash"] != nogate["accepted_hash"], "META_RULE_AF: FULL_LOOP and NO_GATE accepted-store bit-identical (gate not firing)"
    assert full["n_false_in_store"] <= nogate["n_false_in_store"], "gate did not reduce false facts vs accept-all"
    # gate must FIRE (reject at least one false fact that NO_GATE would admit) at this scale.
    assert nogate["n_false_in_store"] >= 1, "smoke-vacuous: NO_GATE did not admit the false fact (discriminator not exercised)"
    for ep in ["make_phasors", "encode_meaning", "decode_meaning", "learn_lexicon", "run_loop"]:
        assert ep in exercised, f"real_code_path: entrypoint {ep} not exercised"
    print(f"[self_test] PASS | svo_roundtrip=ok lexicon_macc={macc:.3f} extraction={full['extraction_acc']:.3f} "
          f"full_false={full['n_false_in_store']} nogate_false={nogate['n_false_in_store']} "
          f"gate_fires={full['accepted_hash']!=nogate['accepted_hash']}", flush=True)
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
    expected_n_units = len(seeds) * 4   # 4 arms x seeds
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[read_grow] run_mode={run_mode} seeds={seeds} corpus={len(READ_CORPUS)} sentences", flush=True)

    full = avg_arm(seeds, use_gate=True, lexicon_kind="learned")
    print(f"[read_grow] FULL_LOOP done extract={full['extraction_acc']:.3f} prec={full['foundation_precision']:.3f}", flush=True)
    nogate = avg_arm(seeds, use_gate=False, lexicon_kind="learned")
    print(f"[read_grow] NO_GATE done prec={nogate['foundation_precision']:.3f} false={nogate['n_false_in_store']:.2f}", flush=True)
    oracle = avg_arm(seeds, use_gate=True, lexicon_kind="oracle")
    random_ctrl = avg_arm(seeds, use_gate=True, lexicon_kind="random")
    print(f"[read_grow] oracle extract={oracle['extraction_acc']:.3f} random extract={random_ctrl['extraction_acc']:.3f}", flush=True)

    tier, msg, weakest = compute_verdict(full, nogate, oracle, random_ctrl)
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
        "n_read_sentences": len(READ_CORPUS),
        "expected_n_units": expected_n_units,
        "weakest_interface": weakest,
        "arms": {
            "FULL_LOOP": strip(full),
            "NO_GATE": strip(nogate),
            "ORACLE_LEXICON": strip(oracle),
            "RANDOM_LEXICON": random_ctrl and strip(random_ctrl),
        },
        "metric_a_extraction_acc": full["extraction_acc"],
        "metric_b_foundation_precision": full["foundation_precision"],
        "metric_b_true_recall": full["true_recall"],
        "metric_c_query_acc": full["query_acc"],
        "metric_d_accept_true_rate": full["accept_true_rate"],
        "metric_d_accept_false_rate": full["accept_false_rate"],
        "gate_vs_accept_all_precision_gain": full["foundation_precision"] - nogate["foundation_precision"],
        "full_loop_per_seed": full["per_seed"],
        "prereg": {
            "hard_pass": "extract>=0.90 & FULL prec==1.0 & recall>=0.90 & accept_false_rate==0 & "
                         "accept_true_rate>=0.85 & (FULL-NOGATE prec)>=0.05 & novel_owl & hold_release & query>=0.85",
            "hard_fail": "extract<0.50 | accept_false_rate==1.0 | accept_true_rate<0.50 | FULL prec<0.70 | query<0.50",
            "compute_architecture": "sequential-CPU (genuine sequential dependency: foundation grows fact-by-fact)",
            "storage_strategy": "sharded (one VSA vector per accepted fact)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["learn_lexicon", "encode_meaning", "decode_meaning", "make_phasors", "run_loop"],
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[read_grow] {tier} in {elapsed:.2f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[read_grow] {msg}", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _md = "full"
    try:
        if "--smoke" in sys.argv or "--run-mode" in sys.argv and "smoke" in sys.argv:
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
