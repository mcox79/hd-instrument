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

from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

from hdlab.graded_role_assigner import hybrid_role_patient
from hdlab.relcl_resolver import precise_passive
from hdlab.thematic_role_labeler import lemma_verb
from hdlab.animacy_lexicon import lookup_animacy

# ------------------------------------------------------------------------------------------------
# structural plumbing (copied UNCHANGED from the validated exp_shared_predarg_frontend_v1/v2)
# ------------------------------------------------------------------------------------------------
NOMINAL = {"NOUN", "PROPN", "PRON"}
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
                              animacy_fn=lookup_animacy, max_hops: int = MAX_HOPS) -> dict:
    """The SHARED event-semantic predicate-argument router. Returns 1-based token indices (or None):
    {agent, theme, goal, location, path, source, recipient, direction, instrument, goal_belongs_to}.
    prep_to_base / event_classes_fn / dest_fn are override points ONLY for the info-free TWIN control; the
    defaults are the true _PREP_TO_BASE / get_event_classes / is_destination_verb.

    Precedence for the to/for GOAL-vs-RECIPIENT ambiguity (Competition-Model style): (1) TRANSFER/COMM + 'to' ->
    RECIPIENT; (2) MOTION/PUT (to/into/onto/unto) -> GOAL; (3) unclassified verb, 'to', animate object -> RECIPIENT;
    (4) otherwise -> GOAL (CUE1 default). LOCATION/PATH/SOURCE/DIRECTION fire directly off CUE1, verb-independent."""
    prep_to_base = prep_to_base if prep_to_base is not None else _PREP_TO_BASE
    event_classes_fn = event_classes_fn if event_classes_fn is not None else get_event_classes
    dest_fn = dest_fn if dest_fn is not None else is_destination_verb

    v = verb_idx
    cands = _cands(upos)
    passive = precise_passive(tokens, upos, v)
    theme_idx = hybrid_role_patient(tokens, upos, v, cands=cands)
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
