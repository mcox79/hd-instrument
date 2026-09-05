"""predicate_argument_frontend -- the SHARED event-semantic predicate-argument (shallow-SRL) front-end.

Landed 2026-08-29 from the integrated `no_shared_shallow_predicate_argument_front_end` (owner-DONE, PARTIAL/STRONG):
the reusable CORE that maps a parsed clause to argument roles -- agent, theme (moved-thing), goal, location, path,
source, recipient, direction, instrument -- by the BRAIN'S event-semantic mechanism, replacing the reader's three
inline, ad-hoc argument-structure copies. On FrameNet 1.7's independent frame-element gold (58,808 real-prose items)
this router recovers location/path/source/recipient/direction -- five roles the conflating inline rule scores exactly
0.000 on -- all CI-separated with the info-free twin below each; theme/agent above; caused-motion theme-attribution
8/8; positive control 0.886 vs 0.648 (the shipped result; this module IS that mechanism, witnessed store-agnostically
in verification/test_predicate_argument_frontend_organ.py).

PINNED (copied -- the computation): spatial roles are typed by GRADED event-semantic cue-integration -- the
PREPOSITION's telicity as the primary Place-vs-Path cue (Jackendoff Place/Path; Talmy Figure/Ground; Zwarts
boundedness), modulated by the verb's VerbNet event-class and object animacy; place vs path are separable brain
networks (Kemmerer & Tranel 2003). Caused-motion is CONSTRUCTIONAL (Goldberg -- the goal binds to the moved THEME and
ANY verb can enter it), so the moved-theme gate is verb-independent. A curated motion-verb list is the wrong SHAPE.
OUR-INVENTION-UNDER-TEST (swept, not adopted): the exact cue precedence + the destination-frame gate thresholds.

NO external LLM at inference (the invariant). VerbNet event-classes and WordNet place-typing come from the static nltk
lexical resources (a glass-box static asset, not an LLM -- the same live-nltk path the validated experiment used, and
consistent with the landed `location_register` using nltk wordnet), cached per process. The caller supplies a parse
as (tokens, upos, heads[1-based child->head], verb_idx); this module composes the landed graded binder / passive
detector / animacy organs and returns 1-based token indices. The live-reader routing (situation_reader default-off)
and the de-duplication of the three inline copies (measured no-regression) are a queued careful follow-on; this is the
store-agnostic scoring core any caller can use.
"""
from __future__ import annotations

import os
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

from hdlab.graded_role_assigner import hybrid_role_patient, robust_passive
from hdlab.relcl_resolver import precise_passive
from hdlab.thematic_role_labeler import lemma_verb, is_strictly_intransitive
from hdlab.verb_subcat import suppress_patient
from hdlab.animacy_lexicon import lookup_animacy

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LAB_ASSET = os.path.join(_REPO, "data", "frontend_assets", "arc_labeler_hashed_ud_ewt.json")
_LABELER = None


def _labeler():
    """The shared arc_labeler (lazy singleton; SAME asset copular_binding uses). Loaded only when the labeled
    patient readout is actually exercised, so the module import + the structural_patient=OFF path stay cheap."""
    global _LABELER
    if _LABELER is None:
        from hdlab.arc_labeler import ArcLabeler
        _LABELER = ArcLabeler.load(_LAB_ASSET)
    return _LABELER

# ------------------------------------------------------------------------------------------------
# structural plumbing (copied UNCHANGED from the validated exp_shared_predarg_frontend_v1/v2)
# ------------------------------------------------------------------------------------------------
NOMINAL = {"NOUN", "PROPN", "PRON"}
BY = {"by"}
MAX_HOPS = 4
# theme words that, when the binder picks them, mean the goal belongs to the AGENT (self-motion idiom / reflexive /
# path-noun), never a distinct moved theme.
IDIOM_THEME_WORDS = {"way", "himself", "herself", "themselves", "myself", "ourselves", "yourself",
                     "yourselves", "course", "steps", "footsteps", "path", "route", "head", "feet"}

# CUE 1 -- preposition telicity (PRIMARY; fires verb-independently).
_PREP_TO_BASE: Dict[str, str] = {
    "to": "GOAL", "into": "GOAL", "onto": "GOAL", "unto": "GOAL",
    "toward": "DIRECTION", "towards": "DIRECTION",
    "in": "LOCATION", "on": "LOCATION", "at": "LOCATION", "inside": "LOCATION",
    "within": "LOCATION", "upon": "LOCATION", "atop": "LOCATION", "near": "LOCATION",
    "beside": "LOCATION", "among": "LOCATION",
    "from": "SOURCE", "off": "SOURCE",
    "through": "PATH", "across": "PATH", "along": "PATH", "over": "PATH", "around": "PATH",
    "past": "PATH", "down": "PATH", "up": "PATH", "about": "PATH",
    "for": "GOAL_OR_BENEF",
    "with": "INSTR_OR_COMIT",
}

# CUE 2 -- VerbNet event-class (modulates ONLY the to/for GOAL-vs-RECIPIENT ambiguity). Matched by SUBSTRING
# containment against nltk.corpus.verbnet classids (vn.classids(lemma) returns the verb's SUBCLASS ids).
_EVENT_CLASS_PATTERNS: Dict[str, Tuple[str, ...]] = {
    "MOTION": ("run-51", "escape-51", "roll-51", "motion", "nonvehicle-51", "waltz-51"),
    "TRANSFER": ("give-13", "send-11", "contribute-13", "future_having-13"),
    "COMM": ("say-37", "tell-37", "advise-37", "transfer_mesg-37"),
    "PUT": ("put-9", "funnel-9", "spray-9", "throw-17", "pour-9"),
}
_verbnet_class_cache: Dict[str, FrozenSet[str]] = {}


def classify_event_classids(classids: Sequence[str]) -> FrozenSet[str]:
    cats = set()
    for cid in classids:
        for cat, patterns in _EVENT_CLASS_PATTERNS.items():
            if any(p in cid for p in patterns):
                cats.add(cat)
    return frozenset(cats)


def get_event_classes(lemma: str) -> FrozenSet[str]:
    """Live classification via nltk.corpus.verbnet (a static lexical DB -- glass-box, not an LLM), cached
    per-process. Empty frozenset if VerbNet is unavailable or the lemma is unknown."""
    if lemma in _verbnet_class_cache:
        return _verbnet_class_cache[lemma]
    try:
        from nltk.corpus import verbnet as vn
        classids = vn.classids(lemma)
    except Exception:
        classids = []
    cats = classify_event_classids(classids)
    _verbnet_class_cache[lemma] = cats
    return cats


# CUE 5 -- GATED VerbNet DESTINATION-frame goal cue (for verbs whose class carries an explicit Destination
# endpoint role, an at/in/on-PP or a bare object IS the destination, not a peripheral location). GATED to this
# curated set ONLY -- the general population's at/in/on stays LOCATION.
_DESTINATION_VERB_PATTERNS: Tuple[str, ...] = (
    "accompany-51.7", "banish-10.2", "bring-11.3", "butter-9.9", "carry-11.4", "confine-92",
    "convert-26.6.2", "drive-11.5", "fill-9.8", "funnel-9.3", "illustrate-25.3",
    "image_impression-25.1", "pelt-17.2", "poke-19", "put-9.1", "put_spatial-9.2", "reach-51.8",
    "scribble-25.2", "send-11.1", "slide-11.2", "throw-17.1", "transcribe-25.4",
    "wipe_instr-10.4.2-1",
    "escape-51.1", "appear-48",  # arrive/enter/escape/approach/appear: VerbNet names this "Location"
)
# Narrower subset for CUE 5(ii) ONLY (the bare-direct-object rule) -- the pure self-motion-with-locative-complement
# family (reach/enter/arrive/escape/approach/appear), which has NO separate theme distinct from the agent.
_BARE_OBJECT_DEST_PATTERNS: Tuple[str, ...] = ("escape-51.1", "appear-48", "reach-51.8")
_destination_verb_cache: Dict[str, bool] = {}
_bare_object_dest_cache: Dict[str, bool] = {}


def _classify_by_patterns(lemma: str, patterns: Tuple[str, ...], cache: Dict[str, bool]) -> bool:
    if lemma in cache:
        return cache[lemma]
    try:
        from nltk.corpus import verbnet as vn
        classids = vn.classids(lemma)
    except Exception:
        classids = []
    ans = any(p in cid for cid in classids for p in patterns)
    cache[lemma] = ans
    return ans


def is_destination_verb(lemma: str) -> bool:
    return _classify_by_patterns(lemma, _DESTINATION_VERB_PATTERNS, _destination_verb_cache)


def is_bare_object_destination_verb(lemma: str) -> bool:
    return _classify_by_patterns(lemma, _BARE_OBJECT_DEST_PATTERNS, _bare_object_dest_cache)


# ------------------------------------------------------------------------------------------------
# place typing (is_place_ground, copied UNCHANGED from the validated location_register drill): a LOCATION is
# the curated scene lexicon OR a WordNet location-hypernym. Rejects abstract/idiomatic non-places.
# ------------------------------------------------------------------------------------------------
_LOC_HYPERNYM_ROOTS = {"location.n.01", "region.n.03", "structure.n.01", "way.n.06",
                       "geological_formation.n.01", "body_of_water.n.01", "land.n.04", "tract.n.01",
                       "room.n.01", "area.n.01", "space.n.01", "building.n.01", "point.n.02"}
_CURATED_PLACES = {"garden", "kitchen", "study", "cellar", "orchard", "stable", "library", "nursery",
                   "meadow", "barn", "attic", "garret", "shop", "field", "gallery", "greenhouse",
                   "workshop", "room", "house", "hall", "parlour", "parlor", "chamber", "cottage",
                   "bedroom", "office", "cabin", "hut", "shore", "village", "town", "church", "market",
                   "school", "castle", "park", "wood", "woods", "forest", "yard", "porch", "landing",
                   "lodgings", "hotel", "inn", "tavern", "cottage", "farm", "hill", "valley", "river",
                   "bridge", "gate", "road", "lane", "street", "path", "upstairs", "downstairs",
                   "indoors", "outdoors", "cloister", "courtyard", "stairs", "staircase", "closet",
                   "pantry", "scullery", "dining", "drawing", "sitting", "conservatory", "veranda",
                   "terrace", "balcony", "corridor", "passage", "vestibule", "lobby", "arbour", "arbor"}
_place_cache: Dict[str, bool] = {}


def is_place_ground(word: Optional[str]) -> bool:
    """True if `word` is a LOCATION (ATL-style semantic typing): curated scene lexicon OR a WordNet
    location-hypernym. Rejects abstract/idiomatic non-places ('laugh', 'feather', 'verses'). live-nltk wordnet."""
    if not word:
        return False
    w = word.lower()
    if w in _CURATED_PLACES:
        return True
    if w in _place_cache:
        return _place_cache[w]
    ans = False
    try:
        from nltk.corpus import wordnet as wn
        for syn in wn.synsets(w, "n"):
            for path in syn.hypernym_paths():
                if {s.name() for s in path} & _LOC_HYPERNYM_ROOTS:
                    ans = True
                    break
            if ans:
                break
    except Exception:
        ans = w in _CURATED_PLACES     # WordNet unavailable -> curated-only
    _place_cache[w] = ans
    return ans


# ------------------------------------------------------------------------------------------------
# parse helpers (copied UNCHANGED from exp_shared_predarg_frontend_v1)
# ------------------------------------------------------------------------------------------------
def _cands(pos: Sequence[str]) -> List[int]:
    return [i for i in range(1, len(pos) + 1) if pos[i - 1] in NOMINAL]


# ------------------------------------------------------------------------------------------------
# STRUCTURE-FIRST PATIENT (opt-in, default OFF; promoted 2026-09-04 from the owner-DONE who-did-what
# drill `consume_the_graded_pos_posterior_...`). The stock THEME/patient is a flat cue/position selector
# (hybrid_role_patient) -- the brain's DAMAGED-BACKUP/agrammatic route (no arc heads). The brain reads the
# core patient off the PARSE STRUCTURE: the verb's object (active) / promoted subject (passive, voice via
# robust_passive) / coordination-control-shared object -- grammatical relations + linking rules + voice
# remapping (Hagoort MUC; Levin-Rappaport-Hovav; agrammatism dual-route parallel). On CLEAN UD-EWT gold
# (patient := obj|nsubj:pass off gold relations) the structure-first HYBRID (structure if the parse yields a
# core object, else the heuristic fallback) beats the live heuristic +0.088 test / +0.076 train with ZERO
# tuned parameters (generalizes; unlike the register-fitted Competition Model), ceiling 0.91 with a perfect
# parse (residual = parser quality). NO-REGRESS through the live reader (non-role outputs byte-stable). Bodies
# copied VERBATIM from experiments/exp_structural_role_reader_v1.structural_roles (+ its _verb_nom_deps /
# _by_agent / _shared_object helpers) and experiments/exp_structural_patient_noregress_v1.hybrid_patient.
# The AGENT is UNCHANGED (the nearest-pre-verbal / by-phrase / cm_agent path is already stronger than the
# parse's raw subject); this changes ONLY the THEME/patient. Glass-box, NO LLM.
# ------------------------------------------------------------------------------------------------
def _verb_nom_deps(pos, heads, v, n):
    return [c for c in range(1, n + 1) if heads.get(c) == v and pos[c - 1] in NOMINAL]


def _by_agent(toks, pos, heads, v, n):
    """a nominal governed by the verb whose left edge is 'by' (the demoted agent of a passive)."""
    for c in range(1, n + 1):
        if pos[c - 1] in NOMINAL and heads.get(c) == v:
            j = c - 1
            while j - 1 >= 1 and pos[j - 2] in ("ADJ", "NOUN", "PROPN", "DET"):
                j -= 1
            if j - 1 >= 1 and toks[j - 2].lower() in BY:
                return c
    return None


def _shared_object(toks, pos, heads, v, n):
    """coordination/control SHARING: if v has no object of its own, borrow the object of a coordinated verb
    (a verb sharing v's head, or v's head if v is a conjunct). Mirrors UD enhanced-dependency argument sharing."""
    hv = heads.get(v)
    sib_verbs = [u for u in range(1, n + 1) if pos[u - 1] == "VERB" and u != v and (heads.get(u) == hv or u == hv or heads.get(v) == u)]
    for u in sib_verbs:
        post = [c for c in _verb_nom_deps(pos, heads, u, n) if c > u]
        if post:
            return post[0]
    return None


def structural_roles(toks, pos, heads, v, is_passive=None):
    """Read (agent, patient) off the verb's grammatical relations in the parse + voice remapping. 1-based."""
    n = len(toks)
    if is_passive is None:
        is_passive = robust_passive(toks, pos, v)
    nom = _verb_nom_deps(pos, heads, v, n)
    pre = [c for c in nom if c < v]; post = [c for c in nom if c > v]
    if is_passive:
        patient = pre[-1] if pre else (post[0] if post else None)   # promoted subject
        agent = _by_agent(toks, pos, heads, v, n)                    # by-phrase (often absent)
    else:
        patient = post[0] if post else None                         # object
        agent = pre[-1] if pre else None                            # subject
    if patient is None:
        patient = _shared_object(toks, pos, heads, v, n)            # coordination/control sharing
    return {"agent": agent, "patient": patient}


# ------------------------------------------------------------------------------------------------
# LABELED PATIENT READOUT (promoted 2026-09-04 from the owner-DONE
# improve_the_parser_verb_argument_attachment_for_who_did_what). Read the patient the brain's way --
# the verb's LABELED obj/nsubj:pass grammatical relation + a PRECISE voice remapping + VALENCY-gated
# binding of a missed argument (Hagoort MUC valency unification; Levin/Rappaport-Hovav linking rules) --
# NOT by position with the lossy robust_passive. +0.086 CI-sep on clean UD-EWT (0.745->0.831), +0.097 on
# 19c clean-DO, head-independent, zero tuned parameters. Bodies (position_pick / _transitive / labeled_pick)
# copied VERBATIM from experiments/exp_valency_labeled_patient_v1. Glass-box, NO LLM.
# ------------------------------------------------------------------------------------------------
def position_pick(toks, pos, v, heads, is_passive):
    """the PRIOR readout: nearest post-verbal (active) / pre-verbal (passive) NOMINAL dependent."""
    n = len(toks)
    deps = [c for c in range(1, n + 1) if heads.get(c) == v and pos[c - 1] in NOMINAL]
    pre = [c for c in deps if c < v]; post = [c for c in deps if c > v]
    if is_passive:
        return pre[-1] if pre else (post[0] if post else None)
    return post[0] if post else (pre[-1] if pre else None)


def _transitive(lemma):
    """valency: does the verb expect a direct object? (glass-box subcat signal)."""
    return not is_strictly_intransitive(lemma) and not suppress_patient(lemma, 0.35)


def labeled_pick(toks, pos, v, heads, labels, is_passive, valency=False):
    """BRAIN-FAITHFUL: fill the verb's obj (active) / nsubj:pass (passive) LABELED slot; if the parse
    labeled no such dependent, valency-gated bind the nearest non-PP nominal on the expected side when the
    verb's frame expects an argument (unification into the open slot). Falls back to position otherwise."""
    n = len(toks)
    deps = [c for c in range(1, n + 1) if heads.get(c) == v and pos[c - 1] in NOMINAL]
    want = "nsubj:pass" if is_passive else "obj"
    lab = [c for c in deps if labels.get(c) == want]
    if lab:
        side = [c for c in lab if (c < v if is_passive else c > v)]
        if side:
            return side[-1] if is_passive else side[0]
        return lab[-1] if is_passive else lab[0]
    if valency:
        lemma = lemma_verb(toks[v - 1])
        if is_passive:
            for c in range(v - 1, 0, -1):
                if pos[c - 1] in NOMINAL and not (c - 2 >= 0 and pos[c - 2] == "ADP"):
                    return c
        elif _transitive(lemma):
            for c in range(v + 1, n + 1):
                if pos[c - 1] in NOMINAL and not (c - 2 >= 0 and pos[c - 2] == "ADP"):
                    return c
        else:
            return None                      # intransitive frame -> no object bound
    return position_pick(toks, pos, v, heads, is_passive)


def structural_patient_pick(tokens: Sequence[str], upos: Sequence[str], heads: Dict[int, int], v: int,
                            cands: Optional[List[int]] = None, np_head_reduce: bool = False) -> Optional[int]:
    """The DEPLOYABLE who-did-what PATIENT (1-based, or None), read the brain's way off the LABELED parse:
    the verb's obj (active) / nsubj:pass (passive) grammatical relation with a PRECISE voice remapping +
    VALENCY-gated binding of a missed argument (labeled_pick, valency=True); net-safe fallback to the
    heuristic cue/position patient (hybrid_role_patient) ONLY where the labeled readout binds nothing --
    never worse than the heuristic on uncovered items. +0.086 CI-sep over the prior position readout on
    clean UD-EWT (0.745->0.831), register-general (+0.097 on 19c clean-DO), head-independent, zero tuned
    parameters (owner-DONE improve_the_parser_verb_argument_attachment_for_who_did_what, 2026-09-04). Body
    promoted VERBATIM from exp_valency_labeled_live_reader_v1.improved_structural_patient_pick (the drop-in
    that passed the live-reader no-regress) + exp_valency_labeled_patient_v1.labeled_pick."""
    labels = _labeler().label(list(tokens), list(upos), heads)
    pp = precise_passive(tokens, upos, v)
    pick = labeled_pick(tokens, upos, v, heads, labels, pp, valency=True)
    if pick is None:
        if cands is None:
            cands = _cands(upos)
        pick = hybrid_role_patient(tokens, upos, v, cands=cands, np_head_reduce=np_head_reduce)
    return pick


def matrix_verbs(tokens: Sequence[str], upos: Sequence[str], heads: Dict[int, int]) -> List[int]:
    """The clause's matrix predicate(s) (1-based): the ROOT verb (head==0) + verbs coordinated to it
    (head==root). Excludes embedded participles/relatives so the who-did-what is the CLAUSE's assertion,
    not a modifier (matches the positional rule's single-predicate scope; good-enough parsing reads the
    main clause). Copied VERBATIM from the validated exp_wire_predarg_binder_live_reader_v1 -- the shared
    matrix-verb selector the reader-role-routing needs to feed route_predicate_arguments per matrix verb."""
    verbs = [i for i in range(1, len(tokens) + 1) if upos[i - 1] == "VERB"]
    if not verbs:
        return []
    roots = [v for v in verbs if heads.get(v, 0) == 0]
    if not roots:
        roots = [verbs[0]]
    keep = set(roots)
    for v in verbs:
        if heads.get(v) in keep:            # coordinated / chained to a matrix verb
            keep.add(v)
    return sorted(keep)


def _attaches_to_verb(start: int, v: int, heads: Dict[int, int], pos: Sequence[str],
                      max_hops: int = MAX_HOPS) -> bool:
    """Walk UP the head chain from `start`; True iff verb v is reached within max_hops without first hitting a
    DIFFERENT verb or the root. Tolerates one intervening ADV/NOUN hop (this UD-EWT parser sometimes attaches a
    caused-motion goal PP to the moved-theme NOUN rather than the verb directly)."""
    cur = start
    for _ in range(max_hops + 1):
        if cur == v:
            return True
        if cur is None or cur == 0:
            return False
        if pos[cur - 1] == "VERB" and cur != v:
            return False
        cur = heads.get(cur)
    return False


def _pp_args_for_verb(tokens: Sequence[str], pos: Sequence[str], heads: Dict[int, int], v: int,
                      max_hops: int = MAX_HOPS) -> List[Tuple[str, int]]:
    """[(prep_lower, obj_idx), ...] sorted by obj position, for every ADP token whose own head (its UD 'case'
    relation target -- the nominal it introduces) transitively attaches to verb v."""
    n = len(tokens)
    out = []
    for p in range(1, n + 1):
        if pos[p - 1] != "ADP":
            continue
        obj = heads.get(p)
        if obj is None or obj in (0, p):
            continue
        if _attaches_to_verb(obj, v, heads, pos, max_hops=max_hops):
            out.append((tokens[p - 1].lower(), obj))
    out.sort(key=lambda x: x[1])
    return out


def _goal_belongs_to(theme_idx: Optional[int], goal_obj_idx: int, tokens: Sequence[str]) -> str:
    """MOVED-THEME GATE: a non-idiom theme DISTINCT from the PP's own object is the true goal-holder (caused-motion:
    'shoved him to the ground' -> him). If the theme binder found nothing, found the PP object itself, or found an
    idiom/reflexive path-noun, the goal belongs to the agent (self-motion: 'hurried to the ground')."""
    if theme_idx is None or theme_idx == goal_obj_idx:
        return "agent"
    if tokens[theme_idx - 1].lower() in IDIOM_THEME_WORDS:
        return "agent"
    return "theme"


# ------------------------------------------------------------------------------------------------
# QUOTATIVE INVERSION (landed 2026-08-30 from the integrated assembly
# `wire_the_predarg_frontend_and_binder_into_the_live_reader`, owner-DONE, SOLVED/STRONG). The router
# computed the COMM VerbNet class but used it ONLY for recipient routing, never to fix the AGENT of a
# quotative: on "said Fred" the linear `agent = nearest nominal before the verb` rule branded the
# POSTVERBAL speaker the object. On real narrative dialogue this was the single largest role error
# (+0.253 CI-sep to fix). Quotative inversion is the frame semantics of communication verbs (FrameNet
# Statement; VerbNet say-37.7; Goldberg 1995 construction grammar) + animacy proto-agent prominence
# (eADM, Bornkessel-Schlesewsky & Schlesewsky 2006, Psych Review 113:787, PMID 17014303) -- PINNED-in-
# principle; the exact positional mechanism is OUR-INVENTION-UNDER-TEST (no ERP isolates "said Mary"
# online). The speech-verb set + animacy check are copied VERBATIM from the validated
# exp_wire_organs_endtoend_v1 (the prior negative's quotative pieces the assembly reused). This fix is
# ADDITIVE: it changes the router's agent ONLY for a speech/COMM verb that has an animate speaker
# outside quotes -- byte-identical for every non-speech verb. NO external LLM (the invariant).
# ------------------------------------------------------------------------------------------------
_PRO_F = {"she", "her", "hers", "herself"}
_PRO_M = {"he", "him", "his", "himself"}
_ANIMATE_PRO = _PRO_F | _PRO_M | {"they", "them", "their"}
ANIMATE_NOUNS = {
    "mother", "father", "aunt", "uncle", "man", "woman", "boy", "girl", "child", "children", "boatman",
    "brother", "sister", "schoolmaster", "lady", "gentleman", "gentlemen", "people", "folks", "son",
    "daughter", "friend", "teacher", "doctor", "king", "queen", "baby", "nurse", "master", "mistress",
    "cousin", "parents", "dog", "cat", "bird", "horse", "men", "boys", "girls", "sir", "madam", "captain",
    "farmer", "soldier", "servant", "maid", "widow", "beggar", "stranger", "neighbor", "neighbour",
}
# Curated speech-verb set covering archaic verbs VerbNet's COMM class misses (exclaim/murmur/...); the
# COMM VerbNet class is the glass-box static-asset primary cue, this set is the recall backstop.
SPEECH_VERBS = {
    "say", "said", "says", "answer", "answered", "answers", "ask", "asked", "asks", "reply", "replied",
    "exclaim", "exclaimed", "cry", "cried", "cries", "shout", "shouted", "call", "called", "tell", "told",
    "whisper", "whispered", "add", "added", "remark", "remarked", "speak", "spoke", "declare", "declared",
    "inquire", "inquired", "observe", "observed", "respond", "responded", "continue", "continued",
    "return", "returned", "repeat", "repeated", "murmur", "murmured", "groan", "groaned", "sob", "sobbed",
}


def _is_animate_head(word: str, tag: str) -> bool:
    """True if `word` is an animate NOMINAL head (a candidate speaker). `tag` is Penn-ish (NNP proper
    name / PRP pronoun / NN common); use `_penn_hint` to feed it from UPOS. Copied VERBATIM from the
    validated exp_wire_organs_endtoend_v1."""
    wl = word.strip(".,\"'").lower()
    if wl in _ANIMATE_PRO:
        return True
    if tag == "NNP" and word[:1].isupper():   # proper name
        return True
    if wl in ANIMATE_NOUNS:
        return True
    return False


def _penn_hint(upos: str, tok: str) -> str:
    """_is_animate_head expects a Penn-ish tag; map UPOS PROPN->NNP so its proper-name branch fires."""
    return "NNP" if upos == "PROPN" else ("PRP" if upos == "PRON" else "NN")


def _quote_mask(tokens: Sequence[str]) -> List[bool]:
    """True for tokens INSIDE a quoted span (quoted speech is the message, never the matrix argument)."""
    inq = [False] * len(tokens)
    q = False
    for i, w in enumerate(tokens):
        if w in ('"', '``', "''", "“", "”"):
            q = not q
        inq[i] = q
    return inq


def is_speech_verb(lemma: str, vclasses: Optional[FrozenSet[str]] = None) -> bool:
    """COMM event-class (the router's OWN VerbNet class, glass-box static asset) OR the validated curated
    speech-verb set. Pass `vclasses` (already computed) to avoid a redundant VerbNet lookup."""
    vc = vclasses if vclasses is not None else get_event_classes(lemma)
    return ("COMM" in vc) or (lemma in SPEECH_VERBS)


def quotative_speaker(tokens: Sequence[str], upos: Sequence[str], v: int) -> Optional[int]:
    """QUOTATIVE-INVERSION agent: for a speech/COMM verb the SPEAKER is the nearest ANIMATE nominal
    OUTSIDE quotes, preferring POSTVERBAL ('said Fred') then preverbal; the quoted content is not a
    filler. Returns a 1-based token index or None. `v` is 1-based. Copied from the validated experiment."""
    inq = _quote_mask(tokens)
    v0 = v - 1
    order = list(range(v0 + 1, len(tokens))) + list(range(v0 - 1, -1, -1))   # postverbal first
    for i in order:
        if inq[i]:
            continue
        if upos[i] in ("NOUN", "PROPN", "PRON") and _is_animate_head(tokens[i], _penn_hint(upos[i], tokens[i])):
            return i + 1
    return None


# ------------------------------------------------------------------------------------------------
# the event-semantic router (copied UNCHANGED from exp_shared_predarg_frontend_v2)
# ------------------------------------------------------------------------------------------------
def _route_one_pp(prep: str, obj: int, tokens: Sequence[str], upos: Sequence[str],
                  is_motion_or_put: bool, is_xfer_or_comm: bool, is_dest: bool,
                  theme_idx: Optional[int], roles: Dict[str, Optional[int]],
                  goal_belongs_to: Optional[str], animacy_fn=lookup_animacy,
                  prep_to_base: Optional[Dict[str, str]] = None) -> Optional[str]:
    """Types a SINGLE (prep, obj) pair against the CURRENT `roles` dict (mutated in place, 'first wins' per field)
    using the pinned CUE1(prep-telicity)/CUE2(verb-class)/CUE3(animacy)/CUE5(destination) precedence. Returns the
    (possibly updated) goal_belongs_to."""
    prep_to_base = prep_to_base if prep_to_base is not None else _PREP_TO_BASE
    if prep == "by":
        return goal_belongs_to
    obj_word = tokens[obj - 1]
    obj_pos = upos[obj - 1] if obj - 1 < len(upos) else None
    anim = animacy_fn(obj_word, obj_pos)
    animate = bool(anim) and anim.get("animacy") == "animate"
    base = prep_to_base.get(prep)
    if base is None:
        return goal_belongs_to

    if base == "INSTR_OR_COMIT":                          # 'with'
        if roles["instrument"] is None and not animate and not is_place_ground(obj_word):
            roles["instrument"] = obj
        return goal_belongs_to

    if base == "GOAL_OR_BENEF":                            # 'for'
        if roles["recipient"] is None and (is_xfer_or_comm or animate):
            roles["recipient"] = obj
        return goal_belongs_to

    if base == "GOAL":                                     # to / into / onto / unto
        if is_xfer_or_comm and prep == "to":                # CUE2: transfer/comm 'to' -> RECIPIENT
            if roles["recipient"] is None:
                roles["recipient"] = obj
            return goal_belongs_to
        if is_motion_or_put:                                # CUE2: motion/put -> GOAL confirmed
            if roles["goal"] is None:
                roles["goal"] = obj
                goal_belongs_to = _goal_belongs_to(theme_idx, obj, tokens)
            return goal_belongs_to
        if prep == "to" and animate:                        # CUE3: unclassified verb, animate 'to'
            if roles["recipient"] is None:
                roles["recipient"] = obj
            return goal_belongs_to
        if roles["goal"] is None:                           # CUE1 default stands
            roles["goal"] = obj
            goal_belongs_to = _goal_belongs_to(theme_idx, obj, tokens)
        return goal_belongs_to

    if base == "LOCATION" and prep in ("at", "in", "on") and is_dest:
        # CUE 5: DESTINATION-classified verb -- at/in/on is the endpoint, not a peripheral place.
        if roles["goal"] is None:
            roles["goal"] = obj
            goal_belongs_to = _goal_belongs_to(theme_idx, obj, tokens)
        return goal_belongs_to

    # LOCATION / PATH / SOURCE / DIRECTION: CUE1 fires directly, verb-independent.
    role_key = base.lower()
    if roles.get(role_key) is None:
        roles[role_key] = obj
    return goal_belongs_to


def route_predicate_arguments(tokens: Sequence[str], upos: Sequence[str], heads: Dict[int, int],
                              verb_idx: int, prep_to_base: Optional[Dict[str, str]] = None,
                              event_classes_fn=None, dest_fn=None,
                              animacy_fn=lookup_animacy, max_hops: int = MAX_HOPS,
                              quotative: bool = True, np_head_reduce: bool = False,
                              structural_patient: bool = False) -> dict:
    """The SHARED event-semantic predicate-argument router. Returns 1-based token indices (or None):
    {agent, theme, goal, location, path, source, recipient, direction, instrument, goal_belongs_to}.
    prep_to_base / event_classes_fn / dest_fn are override points ONLY for the info-free TWIN control; the
    defaults are the true _PREP_TO_BASE / get_event_classes / is_destination_verb. `quotative` (default
    True) applies quotative-inversion agent handling for speech/COMM verbs ("said Fred" -> Fred=AGENT);
    pass False to disable it (ablation, or callers that apply their own quotative handling separately).
    `structural_patient` (default False = byte-identical historical THEME): when True, the THEME/patient is read
    STRUCTURE-FIRST off the parse relations + voice remapping (structural_patient_pick: object[active] /
    promoted-subject[passive] / coordination-share, heuristic fallback when the parse yields no core object)
    instead of the flat cue/position heuristic -- the brain's main (parse-structure) role route. AGENT unchanged.

    Precedence for the to/for GOAL-vs-RECIPIENT ambiguity (Competition-Model style): (1) TRANSFER/COMM + 'to' ->
    RECIPIENT; (2) MOTION/PUT (to/into/onto/unto) -> GOAL; (3) unclassified verb, 'to', animate object -> RECIPIENT;
    (4) otherwise -> GOAL (CUE1 default). LOCATION/PATH/SOURCE/DIRECTION fire directly off CUE1, verb-independent."""
    prep_to_base = prep_to_base if prep_to_base is not None else _PREP_TO_BASE
    event_classes_fn = event_classes_fn if event_classes_fn is not None else get_event_classes
    dest_fn = dest_fn if dest_fn is not None else is_destination_verb

    v = verb_idx
    cands = _cands(upos)
    passive = precise_passive(tokens, upos, v)
    # THEME/patient: structure-first (opt-in) reads the object/promoted-subject off the parse relations + voice
    # (structural_patient_pick), else the stock flat cue/position heuristic. structural_patient=False is
    # byte-identical to the historical router (the heuristic pick). Only the THEME changes -- the AGENT below is
    # untouched. The heuristic fallback inside structural_patient_pick uses the SAME hybrid_role_patient call, so
    # uncovered items (no parse object) stay byte-identical to the OFF path.
    if structural_patient:
        theme_idx = structural_patient_pick(tokens, upos, heads, v, cands=cands, np_head_reduce=np_head_reduce)
    else:
        theme_idx = hybrid_role_patient(tokens, upos, v, cands=cands, np_head_reduce=np_head_reduce)
    pp_args = _pp_args_for_verb(tokens, upos, heads, v, max_hops=max_hops)

    by_obj = next((o for (p, o) in pp_args if p == "by"), None)
    if passive:
        agent_idx = by_obj
    else:
        before = [i for i in cands if i < v]
        agent_idx = before[-1] if before else None

    lemma = lemma_verb(tokens[v - 1])
    vclasses = event_classes_fn(lemma)
    is_motion_or_put = ("MOTION" in vclasses) or ("PUT" in vclasses)
    is_xfer_or_comm = ("TRANSFER" in vclasses) or ("COMM" in vclasses)
    is_dest = dest_fn(lemma)

    # QUOTATIVE INVERSION (default ON): for a speech/COMM verb, the AGENT is the SPEAKER (nearest animate
    # nominal outside quotes, postverbal-first), not the linear pre-verb nominal, and the quoted content is
    # not a theme. ADDITIVE -- fires only for a speech verb WITH an animate speaker; byte-identical
    # otherwise. `quotative=False` disables it (an ablation/twin hook, like the other override points; used
    # by callers -- e.g. the validating experiment -- that apply their own quotative handling separately).
    if quotative and is_speech_verb(lemma, vclasses):
        sp = quotative_speaker(tokens, upos, v)
        if sp is not None:
            agent_idx = sp
            theme_idx = None

    roles: Dict[str, Optional[int]] = {k: None for k in
                                       ("goal", "location", "path", "source", "recipient",
                                        "direction", "instrument")}
    goal_belongs_to: Optional[str] = None

    for prep, obj in pp_args:
        goal_belongs_to = _route_one_pp(prep, obj, tokens, upos, is_motion_or_put, is_xfer_or_comm,
                                        is_dest, theme_idx, roles, goal_belongs_to,
                                        animacy_fn=animacy_fn, prep_to_base=prep_to_base)

    _no_pp_stole_theme = True
    if theme_idx is not None:
        # Defensive check for long/complex sentences where the parser resolves no heads: a bare-object destination
        # requires NO preposition of any kind between the verb and the candidate object.
        _no_pp_stole_theme = not any(upos[i - 1] == "ADP" for i in range(v + 1, theme_idx))
    if (is_dest and is_bare_object_destination_verb(lemma) and roles["goal"] is None
            and theme_idx is not None and _no_pp_stole_theme
            and not any(rv is not None for rk, rv in roles.items() if rk != "goal")):
        # CUE 5(ii): bare direct-object destination -- self-motion (reach/enter/arrive/escape/approach) with no
        # separate moved theme; the theme binder's own pick IS the endpoint.
        roles["goal"] = theme_idx
        goal_belongs_to = "agent"

    return {"agent": agent_idx, "theme": theme_idx, "goal_belongs_to": goal_belongs_to, **roles}
