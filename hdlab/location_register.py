"""Per-entity spatial LOCATION REGISTER -- the Zwaan & Radvansky event-indexing SPACE dimension of the situation
model (the tracking CORE).

Landed 2026-08-28 from the integrated `situation_model_has_no_spatial_location_dimension` (SOLVED/EXCELLENT,
owner-DONE; witnesses verification/test_location_register.py). This is the spaCy-FREE TRACKING core: it maintains,
per entity, a list of presence INTERVALS `(location_node, t_open, t_close)` over discourse time and answers
`where_is(entity, t)` / `present_in_scene(entity, t)` / region-containment queries -- the brain-faithful COMPUTATION
(PINNED: per-entity location STATE, updated only by MOTION events, PERSISTING between updates; Zwaan & Radvansky 1998;
hippocampal place / entorhinal grid allocentric map; parahippocampal, Speer & Zacks 2009).

SEPARATION OF CONCERNS (why this is spaCy-free): the prose -> MOTION-EVENT extraction (reading the PATH satellite /
Source-Goal-Path off a parse, deixis dominating, Goal-over-Source, the VerbNet Destination-vs-Recipient + ATL
place-typing gates) is an OUR-INVENTION adapter that stays in `experiments/location_register.py` (it needs a parser).
This organ consumes the ABSTRACT motion events that adapter emits -- `(entity, kind, node, t)` with kind in
{arrive, return, depart, stative, present, absent} -- so the tracking COMPUTATION composes with any front-end and this
module imports NO spaCy and NO experiment code. `spatial_region` uses a curated taxonomy + a LAZY, guarded WordNet
lookup (nltk) only for out-of-taxonomy nodes -- import stays clean.

REPRESENTATION (OUR-INVENTION, swept): categorical topological scene nodes (Rinck 1997 rules out metric coords for
narrative space). An FHRR-bound alternative (`to_fhrr_readout` in the source cell) that gives the identical answer is a
queued follow-on (keeps this module torch-free).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

DEICTIC_SCENE = "<scene>"   # the narrated here-and-now scene (entity present, node unnamed)
AWAY = "<away>"             # entity has departed; current node unknown but last-known named node is recoverable
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
_INDOOR_QUERY = {"house", "home", "dwelling", "building", "cottage", "cabin", "hut", "mansion", "indoors",
                 "inside", "hall", "manor", "residence", "abode", "lodging", "lodgings", "apartment"}
_OUTDOOR_QUERY = {"outdoors", "outside", "grounds", "garden", "open", "air", "street", "road"}
_region_cache: Dict[str, Optional[str]] = {}

MOTION_KINDS = ("arrive", "return", "depart", "stative", "present", "absent")


def _canon(q: str) -> str:
    """Minimal node canonicalization for an exact-place query: lowercase, strip a leading article/possessive."""
    toks = q.lower().strip().split()
    while toks and toks[0] in ("the", "a", "an", "his", "her", "their", "its", "my", "our", "your"):
        toks = toks[1:]
    return " ".join(toks)


def spatial_region(node: Optional[str]) -> Optional[str]:
    """Coarse REGION of a fine location node: INDOORS, OUTDOORS, or None (unknown). Curated taxonomy first, then a
    LAZY WordNet part-meronymy check (a room part_holonym a dwelling/house -> INDOORS). The nested cognitive-map level
    above the specific place (Wiener & Mallot 2003 region-based navigation; Peer & Epstein 2025)."""
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
        """The node of the interval active at clause t (the most recent interval opened at/before t). Returns a named
        place, DEICTIC_SCENE, or AWAY (departed to an unnamed destination -- reporting the last-known named place would
        be WRONG, the entity has left it). None if never located."""
        active = None
        for iv in self.intervals:
            if iv.t_open <= t and (iv.t_close is None or t < iv.t_close):
                active = iv
                break
            if iv.t_open <= t:
                active = iv  # most recent opened at/before t (covers the trailing open interval)
        return active.node if active is not None else None

    def last_named_at(self, t: int) -> Optional[str]:
        """The last NAMED node opened at/before t -- 'where was X last seen', distinct from node_at (which returns
        AWAY once the entity departs an unnamed destination)."""
        named = None
        for iv in self.intervals:
            if iv.t_open <= t and iv.node not in (DEICTIC_SCENE, AWAY):
                named = iv.node
        return named


class LocationRegister:
    """Per-entity spatial register: fold MOTION EVENTS over discourse, query where_is(entity, t). The spaCy-free
    tracking core (the prose->events extraction is an experiment-side adapter -- see the module docstring).

    Usage:
        reg = LocationRegister()
        reg.start(["Anna", "Ben"], n_clauses=6)          # everyone starts present in the narrated scene at t=0
        reg.apply_motion("Anna", "arrive", "kitchen", 2)  # Anna -> kitchen at clause 2
        reg.apply_motion("Anna", "depart", None, 4)       # Anna leaves for an unnamed destination at clause 4
        reg.where_is("Anna", 3)      # -> 'kitchen'
        reg.is_in_region("Anna", "house", 3)   # -> True (kitchen is INDOORS)

    Or fold a whole event list at once:
        reg.fold(["Anna", "Ben"], [("Anna","arrive","kitchen",2), ("Anna","depart",None,4)], n_clauses=6)
    """

    def __init__(self) -> None:
        self.tracks: Dict[str, EntityTrack] = {}
        self.n_clauses: int = 0

    def start(self, entities: Sequence[str], n_clauses: int = 0) -> "LocationRegister":
        """Initialize tracks; every entity starts PRESENT in the narrated scene at clause 0 (Zwaan: default co-presence
        until a motion event moves them)."""
        self.tracks = {e: EntityTrack() for e in entities}
        for e in entities:
            self.tracks[e].open_interval(DEICTIC_SCENE, 0)
        self.n_clauses = int(n_clauses)
        return self

    def apply_motion(self, entity: str, kind: str, node: Optional[str], t: int) -> None:
        """Apply ONE abstract motion event to an entity's track (the spaCy-free STATE UPDATE). kind:
        arrive  -> open an interval at the named destination `node`;
        return  -> open at `node`, or the deictic scene if node is None/DEICTIC_SCENE (came/returned back);
        depart  -> open an AWAY interval (left for an unnamed destination);
        stative -> open at `node` (a locative 'X sat in the kitchen'; not necessarily a move, but the current place);
        present -> open a DEICTIC_SCENE interval (asserted present / 'X was back');
        absent  -> open an AWAY interval (asserted absent / 'X was gone').
        The entity must have been registered via start()."""
        tr = self.tracks.get(entity)
        if tr is None:
            raise KeyError(f"unknown entity {entity!r}; call start([...]) first")
        if kind not in MOTION_KINDS:
            raise ValueError(f"unknown motion kind {kind!r}; expected one of {MOTION_KINDS}")
        if t + 1 > self.n_clauses:
            self.n_clauses = t + 1
        if kind == "arrive":
            tr.open_interval(node, t)
        elif kind == "return":
            tr.open_interval(node if (node is not None and node != DEICTIC_SCENE) else DEICTIC_SCENE, t)
        elif kind == "depart":
            tr.open_interval(AWAY, t)
        elif kind == "stative":
            tr.open_interval(node, t)
        elif kind == "present":
            tr.open_interval(DEICTIC_SCENE, t)
        elif kind == "absent":
            tr.open_interval(AWAY, t)

    def fold(self, entities: Sequence[str], events: Sequence[Tuple[str, str, Optional[str], int]],
             n_clauses: int = 0) -> "LocationRegister":
        """Convenience: start(entities) then apply a list of (entity, kind, node, t) motion events in order."""
        self.start(entities, n_clauses=n_clauses)
        for (entity, kind, node, t) in events:
            self.apply_motion(entity, kind, node, t)
        return self

    # -- queries --------------------------------------------------------------
    def where_is(self, entity: str, t: Optional[int] = None) -> Optional[str]:
        """The entity's location node at clause t (default = end). DEICTIC_SCENE = 'in the narrated scene'; a place key
        names a location; AWAY = departed with no recoverable named node; None = never located."""
        tr = self.tracks.get(entity)
        if tr is None:
            return None
        if t is None:
            t = max(0, self.n_clauses - 1)
        return tr.node_at(t)

    def present_in_scene(self, entity: str, t: Optional[int] = None) -> bool:
        """True iff the entity is co-present in the narrated scene at clause t (the bit the ToM observation cue
        consumes: co-presence with a scene event)."""
        return self.where_is(entity, t) == DEICTIC_SCENE

    def last_seen(self, entity: str, t: Optional[int] = None) -> Optional[str]:
        """The last NAMED place the entity was at, at/before t (survives a subsequent AWAY/scene stretch)."""
        tr = self.tracks.get(entity)
        if tr is None:
            return None
        if t is None:
            t = max(0, self.n_clauses - 1)
        return tr.last_named_at(t)

    def intervals_of(self, entity: str) -> List[Interval]:
        tr = self.tracks.get(entity)
        return list(tr.intervals) if tr else []

    # -- HIERARCHICAL queries (region-based scene membership) -----------------
    def region_of(self, entity: str, t: Optional[int] = None) -> Optional[str]:
        """The coarse REGION (INDOORS / OUTDOORS / None) of the entity's current fine node."""
        return spatial_region(self.where_is(entity, t))

    def is_in_region(self, entity: str, query_region: str, t: Optional[int] = None) -> Optional[bool]:
        """Answer 'is entity X in <query_region>?' at multiple granularities via place containment. Returns True/False,
        or None when the fine location is unknown/unresolved (a glass-box UNKNOWN, not a guess). Handles an INDOORS
        query ('house'/'indoors') true iff the fine node is a room/indoors; an OUTDOORS query true iff an outdoor
        place; an EXACT-place query true iff the node equals it."""
        node = self.where_is(entity, t)
        if node in (None, AWAY):
            return None
        q = _canon(query_region)
        reg = spatial_region(node)
        if q in _INDOOR_QUERY:
            return None if reg is None and node != DEICTIC_SCENE else (reg == INDOORS)
        if q in _OUTDOOR_QUERY:
            return None if reg is None else (reg == OUTDOORS)
        if node == DEICTIC_SCENE:
            return None
        return node == q
