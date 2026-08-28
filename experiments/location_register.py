"""location_register -- the MISSING per-entity SPATIAL dimension of the situation model.

BRAIN FRAME (Zwaan & Radvansky 1998 event-indexing model; O'Keefe & Nadel / Moser & Moser
allocentric map; Speer & Zacks 2009 parahippocampal+hippocampus fire on a character's LOCATION
CHANGE during ordinary reading):

  A competent reader maintains, for EACH tracked entity, WHERE it is over narrative time -- one of the
  five PINNED situation-model dimensions (SPACE). The value is a STATE carried across the whole
  narrative, updated only at motion events, NOT a local read of the current sentence. A spatial shift
  is an event boundary.

  location_register[X] = an ordered list of PRESENCE INTERVALS  (location_node, t_open, t_close)
                         opened by an ARRIVAL, closed by a DEPARTURE.  where_is(X, t) = the node of
                         the interval containing t (the last-known node if the current interval is
                         "away"/unknown).

THE COMPUTATION WE COPY (PINNED -- do not sweep):
  * per-entity location STATE, updated by MOTION events, PERSISTING between updates (interval bookkeeping);
  * motion read off the realized PATH SATELLITE / Source-Goal-Path PP ("out", "into X", "back",
    "upstairs"), with DEIXIS DOMINATING (come/return = toward the narrated scene; go/leave = away) --
    Talmy 1985; Papafragou 2008. NOT a manner-verb whitelist (the ToM solver proved that is an
    implementation trap the brain does not have: "she florped out" still departs via "out").
  * Goal-over-Source asymmetry (Lakusta & Landau 2005): a realized GOAL sets the new node; a Source-only
    departure sets the entity "away" (node unknown) but leaves the last-known node recoverable.

THE REPRESENTATION WE SWEEP (OUR-INVENTION-UNDER-TEST -- labelled):
  * a symbolic scene NODE (topological scene membership: room / garden / upstairs ...) -- the primary
    representation, matching the situation model's categorical SPACE dimension (readers track scene
    membership, not metric coordinates);
  * a VSA-BOUND location code composed with the entity code via the substrate's existing FHRR binding
    (situation_model_accumulate.RelationRegister.bind_filler) -- proves the register is FHRR-COMPATIBLE
    and COMPOSES with the (entity, role, event) binding rather than replacing it (bar requirement).
  * metric coordinates are the un-swept alternative: rejected as NOT brain-faithful for reading (the
    reading situation model is categorical/topological; metric place-cell geometry is for navigation of
    perceived space, not narrated scene membership) -- noted, not built.

GLASS-BOX: pure symbolic inference over a spaCy dependency parse (perception-of-syntax), NO external LLM
  and NO network at inference. Reuses the PATH-satellite / deixis lexicons of perceptual_access_ledger so
  the motion reader cannot drift between the two organs. ASCII only.

This is an EXPERIMENTS-side organ (the solver may not write hdlab/). SOLVED.md states the proposed hdlab
landing (a first-class hdlab/location_register.py the ToM front-end and "where is X?" QA consume).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

# Reuse the PATH-satellite / deixis lexicons from the ToM ledger -- ONE source of truth for motion reading.
from experiments.perceptual_access_ledger import (
    DEIXIS_AWAY, DEIXIS_TOWARD, GOAL_PREPS, PerceptualAccessLedger,
)

# A directional adverb/particle that IS its own destination node, and how it maps.
# upstairs/downstairs name a scene node; indoors/inside = return to the deictic scene; the SOURCE
# particles (out/away/off/abroad/forth/outside) mean "away from the scene" -> node unknown (AWAY).
# 'home' defaults to AWAY (narrative 'going home' = leaving the narrated scene); a deictic 'came/returned
# home' is caught by toward-deixis in the direction reader BEFORE the particle, so it maps back to the scene.
_PLACE_PARTICLE = {"upstairs": "upstairs", "downstairs": "downstairs",
                   "indoors": None, "inside": None,                 # None sentinel -> DEICTIC_SCENE
                   "out": "<away>", "outside": "<away>", "away": "<away>", "off": "<away>",
                   "abroad": "<away>", "forth": "<away>", "outdoors": "<away>", "afield": "<away>",
                   "home": "<away>"}
_PRON_ALL = {"he", "she", "they", "him", "her", "them", "his", "hers", "their", "it", "its",
             "himself", "herself", "themselves", "itself", "myself", "me", "i", "you", "we", "us",
             "one", "oneself", "each", "other", "another"}
# Nouns that are NOT places: temporal ('in a minute'), manner/abstract ('in a rage'), OCCLUSION-state
# ('in the dark' -- a field state, not a location), body parts ('in his hand'), meals/activities ('at
# dinner' -- a social event, not a place). These would spuriously relocate an entity that is still present.
_NON_LOCATIVE_NOUN = {"minute", "moment", "instant", "trice", "jiffy", "flash", "twinkling", "second",
                      "while", "hour", "day", "morning", "afternoon", "evening", "night", "week", "year",
                      "time", "spell", "breath", "silence", "moment", "rage", "fury", "temper", "passion",
                      "manner", "way", "fashion", "spreadeagle", "sleep", "thought", "reverie", "dream",
                      "haste", "hurry", "earnest", "vain", "return", "answer", "reply", "surprise",
                      # occlusion / field states (handled by the perceptual-field organ, not location)
                      "dark", "darkness", "gloom", "shadow", "shade", "twilight", "dusk", "mist", "fog",
                      # body parts ('a letter in his hand', 'jumped to her feet', 'the child in her arms')
                      "hand", "hands", "arm", "arms", "lap", "side", "grasp", "grip", "embrace",
                      "feet", "foot", "knee", "knees", "face", "head", "back", "breast", "shoulder",
                      # meals / social events, not places
                      "dinner", "supper", "breakfast", "tea", "luncheon", "lunch", "meal", "table"}
# Within-scene FURNITURE / fixtures: an entity 'on the lounge' / 'by the fire' is PRESENT in the scene,
# not relocated to another place. A stative locative on these keeps the entity in the deictic scene.
_WITHIN_SCENE_GROUND = {"lounge", "couch", "sofa", "settee", "armchair", "chair", "seat", "stool", "bench",
                        "bed", "fire", "fireside", "hearth", "window", "sill", "mantel", "table", "desk",
                        "floor", "corner", "rug", "carpet", "cushion", "pillow", "piano", "doorway", "step"}

# ---------------------------------------------------------------------------
# Location-NODE canonicalisation. A "node" is a topological scene label. Grounds that name the CURRENT
# indoor scene collapse to the deictic scene node; named destinations become their own nodes.
# ---------------------------------------------------------------------------
# DEICTIC-return words: arriving "here" = back in the current narrated scene, node unnamed.
# (Distinct from named rooms: a location register that tracks WHERE must keep 'kitchen' != 'parlour';
# the ToM ledger collapsed all rooms to "the scene" because it only tracked present/absent for ONE scene.)
DEICTIC_RETURN_GROUND = {"indoors", "inside", "home", "back", "here"}
# stopwords stripped from a ground phrase when forming the node key
_GROUND_STOP = {"the", "a", "an", "his", "her", "their", "my", "our", "your", "its", "that", "this",
                "some", "to", "into", "toward", "towards", "unto", "from", "onto", "out", "of", "in",
                "at", "on", "back", "again", "there", "here", "far", "near", "old", "great", "little"}
DEICTIC_SCENE = "<scene>"   # the narrated here-and-now scene (entity present, node unnamed)
AWAY = "<away>"             # entity has departed; current node unknown but last-known is recoverable


# ---------------------------------------------------------------------------
# PLACE-TYPING (the ATL semantic gate). On raw literary prose the motion reader over-fires on abstract /
# idiomatic 'to X' PPs ('broke into a laugh', 'started off in high feather', 'to the memorizing of verses').
# The brain knows 'kitchen' is a place and 'laugh' is not via anterior-temporal-lobe semantic memory. We
# approximate that with WordNet location-hypernym typing (glass-box, offline) + a curated scene lexicon.
# ---------------------------------------------------------------------------
_LOC_HYPERNYM_ROOTS = {"location.n.01", "region.n.03", "structure.n.01", "way.n.06",
                       "geological_formation.n.01", "body_of_water.n.01", "land.n.04", "tract.n.01",
                       "room.n.01", "area.n.01", "space.n.01", "building.n.01", "point.n.02"}
# curated scene/place words (rooms, buildings, outdoor features) -- covers WordNet's material-sense misses
# ('wood') and common narrative places; a fast path before the WordNet lookup.
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

# ---------------------------------------------------------------------------
# MOTION-FRAME TYPING (the second ATL/VerbNet gate, from the real-prose wall drill). A BARE goal PP ('to X')
# is the agent's DESTINATION only if the verb evokes a self-MOTION frame. A COMMUNICATION/TRANSFER verb's
# 'to X' is the ADDRESSEE/RECIPIENT ('said to Alice', 'pointed to the door', 'gave it to her'), never a
# destination. This is the linguistic fact the brain uses (VerbNet motion vs communication classes). It does
# NOT reintroduce the manner-verb-whitelist trap: PATH SATELLITES ('out','back','upstairs') bypass the verb
# entirely (still 'florped out' departs) -- the verb gate applies ONLY to satellite-free goal PPs, where the
# verb genuinely IS the Goal-vs-Addressee disambiguator.
# ---------------------------------------------------------------------------
_MOTION_VERBS = {
    "go", "come", "walk", "run", "ride", "drive", "swim", "fly", "climb", "creep", "crawl", "dash",
    "rush", "hurry", "hasten", "stride", "step", "slip", "stroll", "wander", "march", "proceed",
    "advance", "retreat", "flee", "escape", "journey", "travel", "move", "return", "depart", "head",
    "sail", "row", "gallop", "trot", "scramble", "dart", "bolt", "sprint", "tiptoe", "saunter", "plod",
    "trudge", "wade", "drift", "roam", "venture", "withdraw", "retire", "set", "wend", "hop", "leap",
    "jump", "spring", "race", "glide", "slink", "steal", "slide", "tramp", "trek", "roll", "sally",
    "repair", "betake", "hie", "speed", "fare", "pass", "get", "make", "turn",   # turn only via 'made way'/motion
    "enter", "reenter", "arrive", "approach", "rejoin", "quit", "exit", "leave", "start", "hastened",
}
# communication / transfer / orientation verbs whose 'to X' is an ADDRESSEE/RECIPIENT, never a destination.
_COMM_TRANSFER_BLOCK = {
    "say", "tell", "whisper", "murmur", "mutter", "remark", "reply", "answer", "speak", "ask", "call",
    "cry", "shout", "exclaim", "declare", "announce", "add", "respond", "object", "observe", "continue",
    "point", "gesture", "wave", "nod", "beckon", "refer", "allude", "listen", "attend", "give", "hand",
    "show", "offer", "pass", "send", "lend", "read", "sing", "explain", "repeat", "mention", "confess",
    "admit", "promise", "swear", "complain", "grumble", "sigh", "laugh", "smile", "look", "turn",
}
_PATH_DOBJ = {"way", "course", "path", "route", "steps", "footsteps"}
_motion_cache: Dict[str, bool] = {}


def is_motion_verb(lemma: str) -> bool:
    """True if `lemma` evokes a self-MOTION frame (VerbNet motion classes): curated set OR WordNet
    first-sense troponym of travel/move/go. Communication/transfer verbs are excluded by the caller."""
    if not lemma:
        return False
    w = lemma.lower()
    if w in _motion_cache:
        return _motion_cache[w]
    ans = w in _MOTION_VERBS
    if not ans:
        try:
            from nltk.corpus import wordnet as wn
            ss = wn.synsets(w, "v")
            if ss:
                seen, stack = set(), [ss[0]]     # FIRST (most frequent) sense only -> low polysemy noise
                roots = {"travel.v.01", "move.v.02", "go.v.01", "run.v.01", "fly.v.01", "come.v.01"}
                while stack:
                    s = stack.pop()
                    if s.name() in roots:
                        ans = True
                        break
                    for h in s.hypernyms():
                        if h.name() not in seen:
                            seen.add(h.name())
                            stack.append(h)
        except Exception:
            pass
    _motion_cache[w] = ans
    return ans


def is_place_ground(word: Optional[str]) -> bool:
    """True if `word` is a LOCATION (ATL-style semantic typing): curated scene lexicon OR a WordNet
    location-hypernym. Rejects abstract/idiomatic non-places ('laugh', 'feather', 'verses')."""
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


def canon_node(ground: Optional[str]) -> Optional[str]:
    """Map a raw ground phrase ('to the far field', 'the garden', 'upstairs') to a canonical node key.
    Deictic-return words -> DEICTIC_SCENE; a NAMED place -> its head-noun key; None if empty."""
    if not ground:
        return None
    toks = [t for t in re.findall(r"[a-z]+", ground.lower()) if t not in _GROUND_STOP]
    if not toks:
        # the ground was ONLY deictic-return words ('back inside') -> the scene
        raw = set(re.findall(r"[a-z]+", ground.lower()))
        return DEICTIC_SCENE if (raw & DEICTIC_RETURN_GROUND) else None
    if all(t in DEICTIC_RETURN_GROUND for t in toks):
        return DEICTIC_SCENE
    # head noun = last content token that is NOT a deictic-return word ('the drawing ROOM' -> room)
    named = [t for t in toks if t not in DEICTIC_RETURN_GROUND]
    return named[-1] if named else DEICTIC_SCENE


# ---------------------------------------------------------------------------
# HIERARCHICAL / REGION-BASED spatial structure (brain-foundational: the cognitive map is organized into
# nested REGIONS, not a flat set of places -- region-based navigation and hierarchical spatial memory, Wiener
# & Mallot 2003; Hirtle & Jonides 1985 hierarchical cognitive maps; McNamara regional hierarchies). A reader
# who knows X is in the study also knows X is in the house. We build a shallow place-containment relation from
# a curated room/outdoor taxonomy + WordNet part-meronymy, so where_is can be answered at multiple
# granularities and "is X in the house / indoors?" resolves via ancestry (the brief's scene-membership use).
# ---------------------------------------------------------------------------
INDOORS = "<indoors>"
OUTDOORS = "<outdoors>"
_INDOOR_ROOMS = {"kitchen", "study", "bedroom", "parlour", "parlor", "hall", "cellar", "attic", "garret",
                 "pantry", "scullery", "library", "office", "nursery", "chamber", "closet", "corridor",
                 "passage", "landing", "lobby", "vestibule", "gallery", "conservatory", "bedchamber",
                 "workshop", "dining", "drawing", "sitting", "boudoir", "larder", "loft", "cloakroom",
                 "hallway", "stairway", "staircase", "stairs", "upstairs", "downstairs", "indoors", "inside"}
_OUTDOOR_PLACES = {"garden", "orchard", "meadow", "field", "yard", "stable", "barn", "shed", "greenhouse",
                   "grounds", "lawn", "terrace", "courtyard", "arbour", "arbor", "wood", "woods", "forest",
                   "hill", "valley", "river", "park", "road", "lane", "street", "path", "shore", "beach",
                   "moor", "heath", "common", "green", "paddock", "pasture", "vineyard", "outdoors",
                   "outside", "porch", "veranda", "balcony", "gate", "bridge", "well", "brook", "stream"}
# generic building / dwelling words -> a query for any of these is equivalent to INDOORS
_INDOOR_QUERY = {"house", "home", "dwelling", "building", "cottage", "cabin", "hut", "mansion", "indoors",
                 "inside", "hall", "manor", "residence", "abode", "lodging", "lodgings", "apartment"}
_OUTDOOR_QUERY = {"outdoors", "outside", "grounds", "garden", "open", "air", "street", "road"}
_region_cache: Dict[str, Optional[str]] = {}


def spatial_region(node: Optional[str]) -> Optional[str]:
    """Coarse region of a fine location node: INDOORS, OUTDOORS, or None (unknown). Curated taxonomy first,
    then WordNet part-meronymy (a room part_holonym a dwelling/house -> INDOORS)."""
    if node in (None, DEICTIC_SCENE, AWAY):
        return None
    if node in _region_cache:
        return _region_cache[node]
    ans = None
    if node in _INDOOR_ROOMS:
        ans = INDOORS
    elif node in _OUTDOOR_PLACES:
        ans = OUTDOORS
    else:
        try:
            from nltk.corpus import wordnet as wn
            for syn in wn.synsets(node, "n")[:2]:
                hol = {h.name().split(".")[0] for h in syn.part_holonyms() + syn.member_holonyms()}
                if hol & {"house", "dwelling", "building", "mansion", "home"}:
                    ans = INDOORS
                    break
        except Exception:
            ans = None
    _region_cache[node] = ans
    return ans


@dataclass
class Interval:
    node: str          # canonical location node (a place key, DEICTIC_SCENE, or AWAY)
    t_open: int        # clause index the interval opened at
    t_close: Optional[int] = None   # clause index it closed at (None = still open)


@dataclass
class EntityTrack:
    intervals: List[Interval] = field(default_factory=list)
    last_named: Optional[str] = None   # the last NAMED node (survives an <away>/<scene> stretch)

    def open_interval(self, node: str, t: int) -> None:
        if self.intervals and self.intervals[-1].t_close is None:
            self.intervals[-1].t_close = t
        self.intervals.append(Interval(node=node, t_open=t))
        if node not in (DEICTIC_SCENE, AWAY):
            self.last_named = node

    def node_at(self, t: int) -> Optional[str]:
        """The node of the interval active at clause t (the most recent interval opened at/before t).
        Returns a named place, DEICTIC_SCENE, or AWAY (departed to an unnamed destination -- reporting
        the last-known named place would be WRONG, the entity has left it). None if never located."""
        active = None
        for iv in self.intervals:
            if iv.t_open <= t and (iv.t_close is None or t < iv.t_close):
                active = iv
                break
            if iv.t_open <= t:
                active = iv  # most recent opened at/before t (covers the trailing open interval)
        return active.node if active is not None else None

    def last_named_at(self, t: int) -> Optional[str]:
        """The last NAMED node opened at/before t -- 'where was X last seen', distinct from where_is
        (which returns AWAY once the entity departs an unnamed destination)."""
        named = None
        for iv in self.intervals:
            if iv.t_open <= t and iv.node not in (DEICTIC_SCENE, AWAY):
                named = iv.node
        return named


class LocationRegister:
    """Per-entity spatial register. Fold motion events over discourse; query where_is(entity, t).

    Usage:
        reg = LocationRegister(nlp)
        reg.read(text, entities={"Anna": ["Anna", "she", "her"], ...})
        reg.where_is("Anna", t=7)     # -> a location node (place key / '<scene>' / last-known)
    """

    def __init__(self, nlp=None, place_typing: bool = True, motion_frame: bool = True):
        self._nlp = nlp
        self._led = PerceptualAccessLedger(nlp)   # reuse its parser + motion/subject readers (no drift)
        self.tracks: Dict[str, EntityTrack] = {}
        self.n_clauses: int = 0
        # place_typing: gate goal/stative grounds through the ATL semantic type (is it a location?). ON for
        # raw prose (rejects 'to the laugh'); can be turned OFF for a controlled vocab that is all places.
        self.place_typing = place_typing
        # motion_frame: gate a BARE goal PP on the verb's motion-vs-communication frame (VerbNet Destination
        # vs Recipient). ON for raw prose (blocks 'said to X'); OFF isolates the gate's contribution.
        self.motion_frame = motion_frame

    def _nlp_or_load(self):
        if self._nlp is None:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
            self._led._nlp = self._nlp
        return self._nlp

    # -- goal-ground extraction (Talmy Goal-over-Source; locative filter) ---------------------------
    def _is_locative_pobj(self, tok, aliases: Sequence[str]) -> bool:
        """A prepositional object is a LOCATION (not a person / reflexive / temporal / abstract). A pobj is
        functioning NOMINALLY regardless of the fine POS tag -- en_core_web_sm mis-tags place nouns like
        'stable'/'study' as ADJ/VERB, so we accept by exclusion (reject pronoun / temporal / person),
        not by requiring a NOUN tag."""
        low = tok.text.lower()
        if low in _PRON_ALL or tok.pos_ == "PRON":
            return False
        if low in _NON_LOCATIVE_NOUN:                 # 'in a minute', 'in a rage', 'in his manner'
            return False
        # a proper noun that is a tracked person, not a place -> not locative ('came to Anna')
        if low in {a.lower() for a in aliases}:
            return False
        if tok.pos_ in ("PART", "ADP", "CCONJ", "SCONJ", "AUX", "DET", "NUM", "SYM", "PUNCT"):
            return False                              # function words are never a locative ground
        return True                                   # NOUN/PROPN/ADJ(mistag)/VERB(mistag) nominal pobj

    # dobj heads that are NOT a competing moved theme (idioms / reflexive self-motion).
    _OK_DOBJ = {"way", "himself", "herself", "themselves", "myself", "ourselves", "yourself", "course",
                "steps", "path", "route", "head", "feet"}

    def _goal_node(self, sent, v, aliases: Sequence[str]) -> Optional[str]:
        """Extract a realized GOAL destination node for verb v: a GOAL preposition PP (into/to/onto/...)
        with a LOCATIVE object -> that place; a place particle (upstairs/indoors/...) -> its node. Returns
        a node key, DEICTIC_SCENE, '<away>', or None (no realized locative goal).

        ARGUMENT STRUCTURE: if v has a direct object that is a competing MOVED THEME ('struck them to the
        ground', 'traded the chance for a kite'), the goal PP is the OBJECT's path, not the agent's -- so no
        agent goal (generalizes the placement-verb skip). Reflexive / 'made his way' idioms are exempt."""
        bad_dobj = any(c.dep_ in ("dobj", "obj") and c.text.lower() not in self._OK_DOBJ
                       and c.lemma_.lower() not in self._OK_DOBJ for c in v.children)
        if bad_dobj:
            return None
        # MOTION-FRAME gate for a BARE goal PP: the verb must evoke self-motion and NOT be a communication/
        # transfer verb ('said/pointed/gave to X' = addressee, not destination). Exempt: a 'made his WAY to'
        # path-noun idiom. (Satellites like 'out'/'upstairs' bypass this in path (2).)
        vlem = v.lemma_.lower()
        has_path_dobj = any(c.dep_ in ("dobj", "obj") and c.text.lower() in _PATH_DOBJ for c in v.children)
        goal_verb_ok = (not self.motion_frame) or has_path_dobj \
            or (is_motion_verb(vlem) and vlem not in _COMM_TRANSFER_BLOCK)
        # (1) explicit GOAL preposition PP with a locative object -- the strongest destination signal.
        # 'for' is a directional GOAL under a motion verb ('set off for the meadow'); safe here because we
        # only reach _goal_node once _motion_signal has confirmed motion (scoped, not the shared lexicon).
        goal_preps = GOAL_PREPS | {"for"}
        for c in v.subtree:
            if c.dep_ == "prep" and c.text.lower() in goal_preps:
                if not goal_verb_ok:
                    continue                          # 'said to X' / 'gave to X' -> addressee, not a goal
                pobjs = [g for g in c.children if g.dep_ == "pobj"]
                for p in pobjs:
                    if self._is_locative_pobj(p, aliases):
                        # within-scene furniture as a GOAL ('went/returned to the fire/window') = moved
                        # WITHIN the scene, still present -- same rule as the stative path.
                        if p.text.lower() in _WITHIN_SCENE_GROUND:
                            return DEICTIC_SCENE
                        phrase = " ".join(x.text for x in p.subtree)
                        node = canon_node(phrase)
                        # ATL place-typing: reject an abstract/idiomatic ground ('into a laugh')
                        if self.place_typing and node not in (DEICTIC_SCENE, "<away>") \
                                and not is_place_ground(node):
                            continue
                        return node
        # (2) place particle (adverb/particle that names a node).
        for c in v.subtree:
            if c is v:
                continue
            w = c.text.lower()
            if w in _PLACE_PARTICLE and c.pos_ in ("ADV", "ADP", "PART", "NOUN"):
                node = _PLACE_PARTICLE[w]
                return DEICTIC_SCENE if node is None else node
        return None

    # -- motion -> (kind, node): 'arrive'(node) | 'depart'(node-or-None) | 'return'(scene) ------------
    def _entity_move(self, sent, aliases: Sequence[str], name_head: str) -> Optional[Tuple[str, Optional[str]]]:
        """If `aliases`' entity is the main-clause subject and self-moves in `sent`, return the motion.
        Reuses the ToM ledger's PINNED reader for DIRECTION (subject resolution, deixis dominance,
        PATH-satellite-not-manner-verb); ADDS Goal-ground extraction so a destination is named.
        ('arrive', node)  a realized locative GOAL   -> new named/scene node
        ('return', scene) deixis toward, no named goal-> back in the deictic scene
        ('depart', None)  left, no locative goal      -> <away> (last-known named node recoverable)"""
        if not self._led._subject_is_agent(sent, aliases, name_head):
            return None
        mo = self._led._motion_signal(sent)   # -> ('depart'|'return', ground) | None  (PINNED direction)
        if mo is None:
            return None
        direction, _sig_ground = mo
        # EXPLICIT RETURN SATELLITE dominates deixis: 'went back', 'go back', 'came back again'. The ToM
        # ledger's _motion_signal checks deixis-away ('went') before the 'back' particle, so 'went back'
        # reads as depart there; 'back'/'again' is an explicit Source-return satellite and must win.
        if direction == "depart" and any(
            t.text.lower() in ("back", "again") and t.dep_ in ("advmod", "prt", "npadvmod", "advcl", "dep")
            for t in sent):
            direction = "return"
        # find the main-clause motion verb to hang goal extraction on (root or first VERB)
        vmain = next((t for t in sent if t.dep_ == "ROOT" and t.pos_ == "VERB"), None)
        if vmain is None:
            vmain = next((t for t in sent if t.pos_ == "VERB"), None)
        goal = self._goal_node(sent, vmain, aliases) if vmain is not None else None
        sub = list(vmain.subtree) if vmain is not None else []
        has_path_particle = any(c.text.lower() in _PLACE_PARTICLE for c in sub)
        # SOURCE PP realized ('from the room', 'out of the house'): Source-only -> departure (Talmy;
        # Lakusta&Landau -- Source realized without a Goal means absent from that ground).
        has_source = False
        for c in sub:
            if c.dep_ == "prep":
                w = c.text.lower()
                nxt = c.nbor().text.lower() if (c.i + 1 < len(c.doc)) else ""
                if w == "from" or (w == "out" and nxt == "of"):
                    pobjs = [g for g in c.children if g.dep_ == "pobj"]
                    if any(self._is_locative_pobj(p, aliases) for p in pobjs) or w == "out":
                        has_source = True
        deixis = any((t.lemma_.lower() in (DEIXIS_AWAY | DEIXIS_TOWARD)
                      or t.text.lower() in (DEIXIS_AWAY | DEIXIS_TOWARD)) for t in sent if t.pos_ == "VERB")
        has_leave = any(t.lemma_.lower() in ("leave", "quit", "exit") for t in sent if t.pos_ == "VERB")
        has_return_cue = any(t.text.lower() in ("back", "again")
                             and t.dep_ in ("advmod", "prt", "npadvmod", "advcl", "dep") for t in sent)
        # a RETURN is motion (the register updates to the scene) -- handle it before the depart gate so a
        # 'made his way back' (return cue but no goal/particle) is not dropped.
        if direction == "return":
            return ("return", goal if (goal and goal not in ("<away>",)) else DEICTIC_SCENE)
        # depart direction: reject the non-locative-'to' false positive ('sighed to himself') -- fired on a
        # prep but with NO locative evidence of any kind.
        locative_evidence = ((goal is not None) or has_path_particle or has_source or deixis
                             or has_leave or has_return_cue)
        if not locative_evidence:
            return None
        if goal is not None and goal not in ("<away>", DEICTIC_SCENE):
            return ("arrive", goal)            # departed the scene AND arrived at a named place (Goal wins)
        if goal == DEICTIC_SCENE:
            return ("return", DEICTIC_SCENE)   # 'hurried indoors' -> back in scene
        return ("depart", None)                # departure (source/particle/deixis/leave), dest unnamed -> away

    # -- stative locative predication: 'X was/sat/stood/stayed in <place>' sets the node (not only motion) --
    _POSTURE = {"be", "sit", "stand", "lie", "kneel", "wait", "remain", "stay", "linger", "rest",
                "sleep", "work", "read", "write", "dine", "recline", "crouch", "lounge", "loll"}

    def _stative_location(self, sent, aliases: Sequence[str], name_head: str) -> Optional[str]:
        """If the entity is the subject of a copula/posture verb with a locative 'in/at/on <place>' PP,
        return that node. The situation model sets SPACE from explicit locative predication, not only from
        motion (Zwaan). Returns a named node, DEICTIC_SCENE, or None."""
        if not self._led._subject_is_agent(sent, aliases, name_head):
            return None
        for v in sent:
            if v.pos_ not in ("VERB", "AUX"):
                continue
            if v.lemma_.lower() not in self._POSTURE:
                continue
            for c in v.children:
                if c.dep_ == "prep" and c.text.lower() in ("in", "at", "into", "inside", "within", "on"):
                    pobjs = [g for g in c.children if g.dep_ == "pobj"]
                    for p in pobjs:
                        if self._is_locative_pobj(p, aliases):
                            # within-scene furniture ('asleep on the lounge', 'by the fire') = PRESENT in
                            # the scene, not a relocation. A named room/place = its own node.
                            if p.text.lower() in _WITHIN_SCENE_GROUND:
                                return DEICTIC_SCENE
                            phrase = " ".join(x.text for x in p.subtree)
                            node = canon_node(phrase)
                            if node and node != DEICTIC_SCENE and self.place_typing \
                                    and not is_place_ground(node):
                                continue                      # 'sat in judgement/silence' -> not a location
                            if node:
                                return node
        return None

    def read(self, text: str, entities: Dict[str, Sequence[str]], reset_scene: bool = True) -> "LocationRegister":
        """Walk the discourse once, updating each entity's presence intervals from motion events.
        entities: {canonical_name: [aliases...]} (aliases[0] treated as the canonical name).
        Every entity starts in the DEICTIC_SCENE (present) unless/until it moves. Glass-box, incremental."""
        nlp = self._nlp_or_load()
        sents = list(nlp(text).sents)
        self.n_clauses = len(sents)
        self.tracks = {name: EntityTrack() for name in entities}
        for name in entities:                # everyone starts present in the narrated scene
            self.tracks[name].open_interval(DEICTIC_SCENE, 0)
        for i, s in enumerate(sents):
            for name, aliases in entities.items():
                head = aliases[0] if aliases else name
                mv = self._entity_move(s, list(aliases), head)
                if mv is None:
                    # motion absent: try a stative LOCATIVE ('X sat in the kitchen') then a bare
                    # absence/presence predicate ('X was gone/away', 'X was back').
                    loc = self._stative_location(s, list(aliases), head)
                    if loc is not None:
                        self.tracks[name].open_interval(loc, i)
                        continue
                    ap = self._led._absence_predicate(s, list(aliases))
                    if ap is True:
                        self.tracks[name].open_interval(AWAY, i)
                    elif ap is False:
                        self.tracks[name].open_interval(DEICTIC_SCENE, i)
                    continue
                kind, node = mv
                if kind == "arrive":
                    self.tracks[name].open_interval(node, i)
                elif kind == "return":
                    self.tracks[name].open_interval(node if node != DEICTIC_SCENE else DEICTIC_SCENE, i)
                else:  # depart, unnamed destination
                    self.tracks[name].open_interval(AWAY, i)
        return self

    # -- queries --------------------------------------------------------------
    def where_is(self, entity: str, t: Optional[int] = None) -> Optional[str]:
        """The entity's location node at clause t (default = end of text). DEICTIC_SCENE means 'in the
        narrated scene'; a place key names a location; AWAY means departed with no recoverable named node;
        None means never located."""
        tr = self.tracks.get(entity)
        if tr is None:
            return None
        if t is None:
            t = max(0, self.n_clauses - 1)
        return tr.node_at(t)

    def present_in_scene(self, entity: str, t: Optional[int] = None) -> bool:
        """True iff the entity is co-present in the narrated scene at clause t (the bit the ToM
        observation cue consumes: co-presence with a scene event)."""
        return self.where_is(entity, t) == DEICTIC_SCENE

    def intervals_of(self, entity: str) -> List[Interval]:
        tr = self.tracks.get(entity)
        return list(tr.intervals) if tr else []

    # -- HIERARCHICAL queries (region-based scene membership) -----------------
    def region_of(self, entity: str, t: Optional[int] = None) -> Optional[str]:
        """The coarse REGION (INDOORS / OUTDOORS / None) of the entity's current fine node -- the nested
        cognitive-map level above the specific place."""
        return spatial_region(self.where_is(entity, t))

    def is_in_region(self, entity: str, query_region: str, t: Optional[int] = None) -> Optional[bool]:
        """Answer 'is entity X in <query_region>?' at multiple granularities via place containment. Returns
        True/False, or None when the fine location is unknown/unresolved (a glass-box UNKNOWN, not a guess).
        Handles: an INDOORS query ('the house/indoors') true iff the fine node is a room/indoors; an OUTDOORS
        query true iff the node is an outdoor place; an EXACT-place query true iff the node equals it."""
        node = self.where_is(entity, t)
        if node in (None, AWAY):
            return None
        q = query_region.lower().strip()
        reg = spatial_region(node)
        if q in _INDOOR_QUERY:
            return None if reg is None and node != DEICTIC_SCENE else (reg == INDOORS)
        if q in _OUTDOOR_QUERY:
            return None if reg is None else (reg == OUTDOORS)
        # an exact-place query: is the current node that place (or the scene, if the place is the scene)?
        if node == DEICTIC_SCENE:
            return None
        return node == canon_node(q)

    # -- FHRR-compatible representation (SWEEP): bind the current node into the substrate binding algebra --
    def to_fhrr_readout(self, entity: str, t: Optional[int] = None, d: int = 4096, seed: int = 20260828):
        """Bind (entity, 'location') -> current-node code through the EXISTING FHRR RelationRegister and
        decode it back. Returns (decoded_node, cos) or (None, 0.0). Proves the register composes with the
        substrate's binding algebra (an alternative REPRESENTATION giving the SAME answer as the symbolic
        node), not a bolt-on. Import is lazy so the symbolic path stays torch-free."""
        node = self.where_is(entity, t)
        if node is None:
            return None, 0.0
        import torch
        from hdlab.situation_model_accumulate import RelationRegister, unit_phase_vec, cleanup_argmax
        g = torch.Generator().manual_seed(seed)
        rr = RelationRegister(d=d, generator=g)
        # a small FHRR codebook (unit-phasor complex codes) of the candidate nodes for this entity + answer
        vocab = sorted({iv.node for iv in self.intervals_of(entity)} | {node})
        codes = {}
        for i, v in enumerate(vocab):
            gg = torch.Generator().manual_seed((seed + 101 * (i + 1)) % (2**31 - 1))
            codes[v] = unit_phase_vec(d, gg)
        # bind the current-location code onto the GOAL role (the entity's current place = its destination),
        # decode it back, and FHRR cleanup-argmax against the node codebook -- a round-trip through the
        # substrate's existing binding algebra (proves the register is FHRR-compatible, not a bolt-on).
        rr.bind_filler(entity, RelationRegister.GOAL_ROLE, codes[node])
        dec = rr.decode_filler(entity, RelationRegister.GOAL_ROLE)
        best, scores = cleanup_argmax(dec, codes)
        return best, float(scores[best])


def _unit_code(symbol: str, d: int, seed: int):
    import torch
    h = (hash(symbol) ^ (seed * 2654435761)) & 0x7FFFFFFF
    g = torch.Generator().manual_seed(h % (2**31 - 1))
    v = torch.randn(d, generator=g)
    return v / (v.norm() + 1e-9)


# ---------------------------------------------------------------------------
# Self-test: the discriminating cases a STATELESS last-mention baseline gets WRONG.
# ---------------------------------------------------------------------------
def _self_test():
    import spacy
    nlp = spacy.load("en_core_web_sm")
    cases = [
        # (text, entity aliases, query_t (None=end), expected where_is node, note)
        ("Anna was in the parlour. Anna went out to the garden. The clock ticked on the mantel. "
         "Ben read his book by the fire.",
         ["Anna", "she", "her"], None, "garden",
         "departed to a named place; last-mention-loc would say 'fire/mantel' (current scene)"),
        # RE-ENTRY: A -> garden -> back to scene. last-known-named would say 'garden'; register says scene.
        ("Anna was in the parlour. Anna went out to the garden. Then Anna came back inside. "
         "She sat down by the fire.",
         ["Anna", "she", "her"], None, DEICTIC_SCENE, "re-entry: back in the scene, not the garden"),
        # PERSISTENCE across a mention that does NOT restate location.
        ("Thomas walked upstairs to his room. A long while passed. Thomas sighed to himself.",
         ["Thomas", "he", "him"], None, "room", "stays upstairs across a locationless mention"),
        # DEPARTURE with unnamed destination -> away, last-known named recoverable (started in scene -> <away>).
        ("Clara was in the kitchen. Clara went away. The fire burned low.",
         ["Clara", "she", "her"], None, AWAY, "left, destination unnamed -> away"),
    ]
    ok = 0
    for text, aliases, t, exp, note in cases:
        reg = LocationRegister(nlp)
        reg.read(text, {aliases[0]: aliases})
        got = reg.where_is(aliases[0], t)
        good = (got == exp)
        ok += int(good)
        print(f"  [{'PASS' if good else 'FAIL'}] {note}: where_is={got!r} (exp {exp!r})")
    print(f"SELF-TEST {ok}/{len(cases)} cases")
    assert ok == len(cases), f"location_register self-test failed ({ok}/{len(cases)})"


if __name__ == "__main__":
    _self_test()
