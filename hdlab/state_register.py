"""state_register -- the MISSING per-entity STATE-HISTORY dimension of the situation model (Zwaan &
Radvansky ENTITIES). Sibling of hdlab/location_register.py: the SAME per-entity interval bookkeeping,
a DIFFERENT attribute (what an entity IS / has-been, not where it is).

BRAIN FRAME (PINNED):
  * Perfect/stative ASPECT binds a STATE to an ENTITY over an interval, and routes to the ENTITY/state
    layer, distinct from the event-ORDER layer (Ferretti, Kutas & McRae 2007, "Verb aspect and the
    activation of event knowledge": perfect "had shattered" primes the RESULTANT/entity state; imperfective
    "was shattering" keeps the ONGOING event active). Zwaan & Radvansky 1998 ENTITIES dimension.
  * States DEFAULT-PERSIST until something contradicts them (temporal inertia -- Dowty 1986; commonsense
    inertia). Persistence is the default; a state does not silently end.
  * The PERFECT's currency is a CANCELLABLE pragmatic default, NOT an entailment (research drill
    2026-08-29; Iatridou/Anagnostopoulou/Izvorski on the perfect; Moens & Steedman 1988 "consequent
    state"). "He had been a soldier" does NOT entail he is no longer one -- it is open-through-the-
    reference-time by default, closable only by an explicit cancellation cue ("but now...", "no longer",
    an incompatible state). A naive "had-been-X auto-closes" rule OVERCLAIMS -- we do not do that.
  * A telic change-of-state event carries TWO things (neo-Davidsonian; Parsons 1990; Kratzer 2000):
    a CLOSABLE resultant TARGET-STATE ("the door opened" -> door is-open, cancellable by "was shut again")
    AND a PERMANENT OCCURRENCE-FACT (a door-opening happened; never retracted). We keep both fields.
  * Substrate: hippocampal-entorhinal relational binding of an attribute to an item over a temporal
    context (Eichenbaum; Ranganath) -- a per-entity state timeline is a real construct, dissociable from
    event-order memory.

THE COMPUTATION WE COPY (PINNED -- do not sweep):
  per-entity STATE spans (value, polarity, aspect, t_open, t_close), default-persisting, updated by
  copular/perfect predications and resultant states of telic events; a span CLOSES only on an explicit
  cancellation cue (an incompatible/antonym state or a negation/cessation), never silently.

THE REPRESENTATION / EXTRACTION WE SWEEP (OUR-INVENTION-UNDER-TEST -- labelled):
  * the state-EXTRACTION patterns (which constructions yield a state, and its canonical value/polarity);
  * the incompatibility/antonym lexicon that triggers a closure (an entity can be BOTH "ill" and "a
    soldier" -- states are NOT mutually exclusive, so closure must be EXPLICIT, not same-slot-overwrite);
  * the discrete-interval representation (reuses the location_register Interval shape).

The TRACKING CORE below is spaCy-FREE (consumes abstract state events -- like the location register's
core consumes abstract motion events), so the mechanism is isolable from the extraction. The prose->state
extraction is the StateReader adapter (lazy spaCy), the OUR-INVENTION front-end.

GLASS-BOX: pure symbolic; NO external LLM, NO network at inference. ASCII only, no em-dash.
This is an EXPERIMENTS-side organ (the solver may not write hdlab/); SOLVED.md states the proposed
hdlab landing (a first-class hdlab/state_register.py, sibling of location_register.py).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

# Aspect tags (which layer / timeline slot the state is filed under).
CURRENT = "current"   # copular present/past ("X is/was ill") -- holds at the reference time
PRIOR = "prior"       # perfect ("X had/has been ill") -- prior state, default open-through-R, cancellable
RESULT = "result"     # resultant target-state of a telic event ("the door opened" -> open)

ASPECTS = (CURRENT, PRIOR, RESULT)

# ---------------------------------------------------------------------------
# INCOMPATIBILITY lexicon (OUR-INVENTION-UNDER-TEST) as OPPOSING GROUPS, not flat mutually-exclusive sets.
# States are NOT mutually exclusive in general (ill + a soldier co-exist), so a span CLOSES only on an
# EXPLICITLY INCOMPATIBLE state. Two values are incompatible iff they sit on OPPOSITE sides of a dimension;
# values on the SAME side are SYNONYMS (ill/sick/unwell -- NOT incompatible; shattered entails broken).
# Each entry is (side_A, side_B): every A-value is incompatible with every B-value, and vice versa.
# ---------------------------------------------------------------------------
_OPPOSED: Tuple[Tuple[frozenset, frozenset], ...] = (
    (frozenset({"open"}), frozenset({"shut", "closed"})),
    (frozenset({"locked"}), frozenset({"unlocked"})),
    (frozenset({"alive"}), frozenset({"dead"})),
    (frozenset({"awake"}), frozenset({"asleep", "sleeping"})),
    (frozenset({"ill", "sick", "unwell", "ailing"}), frozenset({"well", "healthy", "better", "recovered", "cured"})),
    (frozenset({"present"}), frozenset({"absent", "gone", "away"})),
    (frozenset({"empty"}), frozenset({"full"})),
    (frozenset({"rich", "wealthy"}), frozenset({"poor"})),
    (frozenset({"young"}), frozenset({"old"})),
    (frozenset({"married"}), frozenset({"single", "unmarried", "widowed"})),
    (frozenset({"free"}), frozenset({"captive", "imprisoned", "bound"})),
    (frozenset({"lit"}), frozenset({"unlit", "dark"})),
    (frozenset({"clean"}), frozenset({"dirty"})),
    (frozenset({"whole", "mended", "repaired", "intact"}), frozenset({"broken", "shattered", "cracked", "smashed"})),
    (frozenset({"hidden"}), frozenset({"visible", "revealed"})),
    (frozenset({"lost"}), frozenset({"found"})),
    (frozenset({"hot", "warm"}), frozenset({"cold", "cool"})),
    (frozenset({"happy", "glad"}), frozenset({"sad", "miserable", "wretched", "unhappy"})),
    (frozenset({"calm"}), frozenset({"angry", "furious", "agitated"})),
)
# fast lookup: value -> the set of values on the OPPOSITE side (its incompatibles)
_INCOMPAT: Dict[str, frozenset] = {}
for _A, _B in _OPPOSED:
    for _v in _A:
        _INCOMPAT[_v] = _INCOMPAT.get(_v, frozenset()) | _B
    for _v in _B:
        _INCOMPAT[_v] = _INCOMPAT.get(_v, frozenset()) | _A


def _canon_value(v: str) -> str:
    """Canonicalise a state value: lowercase, strip a leading article, strip surrounding punctuation.
    Intensifier-stripping ('very ill' -> 'ill') also gives the scalar entailment 'very ill' |= 'ill' for free."""
    toks = v.lower().strip().strip(".,;:'\"!?()").split()
    while toks and toks[0] in ("a", "an", "the", "very", "quite", "so", "too", "most", "more"):
        toks = toks[1:]
    return " ".join(toks)


# ===========================================================================
# SEMANTIC STATE MATCHING (research drill 2026-08-29, GO-WITH-BOUNDS). The entity-state layer is the ATL
# semantic hub (Patterson, Nestor & Rogers 2007) -- graded/feature-based, NOT lexical-string. So a query
# 'is X unwell?' should match a stored 'ill' (synonymy), 'is the vase damaged?' should match 'shattered'
# (entailment). WordNet is a defensible CHEAP approximation with THREE MANDATORY guards the research named:
#   (1) PRIVATIVE modifiers ('fake/former soldier') cancel the noun -> block entailment (Kamp & Partee 1995);
#   (2) OPEN-scale (relative/contrary) vs CLOSED-scale (absolute/contradictory) adjectives (Kennedy 2007);
#   (3) TYPED antonymy: 'not alive' |= dead (contradictory, closed) but 'not tall' =/= short (contrary, open)
#       -- Fong 2004; Gotzner & Alexandropoulou 2024.
# Glass-box, lazy nltk (offline), NO external LLM. Scale-type lexicons are OUR-INVENTION-SWEPT.
# ===========================================================================
# CLOSED-scale = absolute/contradictory (negating one entails the other). OPEN-scale = relative/contrary
# (a middle exists; negation is NOT a flip). These also type the antonym pairs for guard (3).
_CLOSED_SCALE = {"open", "shut", "closed", "locked", "unlocked", "alive", "dead", "awake", "asleep",
                 "present", "absent", "empty", "full", "lit", "unlit", "dark", "hidden", "visible",
                 "revealed", "lost", "found", "whole", "broken", "shattered", "mended", "married",
                 "single", "free", "captive", "imprisoned"}
_OPEN_SCALE = {"ill", "sick", "unwell", "well", "healthy", "rich", "poor", "wealthy", "young", "old",
               "hot", "cold", "warm", "cool", "happy", "sad", "miserable", "calm", "angry", "furious",
               "clean", "dirty", "tall", "short", "big", "small", "large", "strong", "weak", "fast",
               "slow", "good", "bad", "high", "low", "near", "far", "heavy", "light", "expensive", "cheap"}
# privative / non-subsective modifiers: cancel or suspend the noun's properties -> block hypernym entailment.
_PRIVATIVE = {"fake", "former", "alleged", "counterfeit", "ex", "would-be", "pretend", "pretended",
              "fictional", "so-called", "self-proclaimed", "erstwhile", "wannabe", "mock", "sham",
              "bogus", "past", "one-time", "quondam", "putative", "supposed", "reputed", "aspiring"}
# curated scalar / degree entailment (stronger -> the weaker state it entails). Fills WordNet's ADJECTIVE
# hypernym gap (adjectives have no hypernymy; only similar_to/antonym). OUR-INVENTION-SWEPT.
_SCALAR_ENTAILS: Dict[str, frozenset] = {
    "shattered": frozenset({"broken", "damaged"}), "smashed": frozenset({"broken", "damaged"}),
    "broken": frozenset({"damaged"}), "cracked": frozenset({"damaged"}),
    "freezing": frozenset({"cold"}), "frozen": frozenset({"cold"}), "boiling": frozenset({"hot"}),
    "starving": frozenset({"hungry"}), "famished": frozenset({"hungry"}), "parched": frozenset({"thirsty"}),
    "drenched": frozenset({"wet"}), "soaked": frozenset({"wet"}), "furious": frozenset({"angry"}),
    "enraged": frozenset({"angry"}), "terrified": frozenset({"afraid", "frightened"}),
    "petrified": frozenset({"afraid"}), "delighted": frozenset({"happy", "glad"}),
    "elated": frozenset({"happy"}), "miserable": frozenset({"sad", "unhappy"}),
    "wretched": frozenset({"unhappy"}), "exhausted": frozenset({"tired", "weary"}),
    "ruined": frozenset({"damaged"}), "deceased": frozenset({"dead"}), "slain": frozenset({"dead"}),
}
_wn_syn_cache: Dict[str, frozenset] = {}


def _wn_synonyms(word: str) -> frozenset:
    """WordNet synonyms of `word` (synset lemmas across n/adj/v; adjective similar_to satellites included)."""
    if word in _wn_syn_cache:
        return _wn_syn_cache[word]
    out = set()
    try:
        from nltk.corpus import wordnet as wn
        for syn in wn.synsets(word)[:4]:
            for lm in syn.lemmas():
                out.add(lm.name().replace("_", " ").lower())
            if syn.pos() in ("a", "s"):
                for sim in syn.similar_tos()[:3]:
                    for lm in sim.lemmas():
                        out.add(lm.name().replace("_", " ").lower())
    except Exception:
        pass
    out.discard(word)
    _wn_syn_cache[word] = frozenset(out)
    return _wn_syn_cache[word]


def _wn_hypernym_entails(specific: str, general: str) -> bool:
    """True iff NOUN `specific` is a hyponym of `general` within 3 steps (so 'specific' entails 'general':
    a soldier is-a serviceman). Nouns/verbs only -- adjectives have no hypernymy (use _SCALAR_ENTAILS)."""
    try:
        from nltk.corpus import wordnet as wn
        gens = set(wn.synsets(general, "n")) | set(wn.synsets(general, "v"))
        if not gens:
            return False
        for syn in wn.synsets(specific, "n")[:3] + wn.synsets(specific, "v")[:2]:
            for path in syn.hypernym_paths():
                depth = 0
                for node in reversed(path):
                    if node in gens and 0 < depth <= 3:
                        return True
                    depth += 1
    except Exception:
        return False
    return False


def _are_synonyms(a: str, b: str) -> bool:
    return b in _wn_synonyms(a) or a in _wn_synonyms(b)


def _contradictory_pair(a: str, b: str) -> bool:
    """An antonym pair with NO middle (closed-scale/absolute): negating one entails the other."""
    if not incompatible(a, b):
        return False
    # a un-/in- morphological pair is contradictory (locked/unlocked); else both ends must be closed-scale
    if (a.startswith(("un", "in")) and a[2:] == b) or (b.startswith(("un", "in")) and b[2:] == a):
        return True
    return a in _CLOSED_SCALE and b in _CLOSED_SCALE


def state_match(query: str, stored: str, stored_polarity: int = 1, guards: bool = True) -> str:
    """Semantic match of a QUERY state against a STORED (value, polarity), with the three research guards.
    Returns 'MATCH' (query holds), 'NO' (query does not hold), or 'NONE' (undetermined). Glass-box.
    guards=False disables the typed contrary/contradictory antonymy guard (ablation -- then 'not tall'
    wrongly flips to 'short')."""
    q, s = _canon_value(query), _canon_value(stored)
    # a privative-modified stored/query is handled at EXTRACTION (the state is not stored); here q/s are heads.
    if q == s:
        return "MATCH" if stored_polarity == 1 else "NO"
    if incompatible(s, q):                     # opposites
        if stored_polarity == 1:
            return "NO"                        # stored HOLDS -> its opposite does not
        # 'not alive'->dead (contradictory, closed-scale); 'not tall'-/->short (contrary, open-scale).
        return "MATCH" if ((not guards) or _contradictory_pair(s, q)) else "NONE"
    if stored_polarity != 1:
        return "NONE"                          # a negated, non-opposite stored state says nothing about q
    # positive stored state: synonymy (symmetric) or scalar/hypernym ENTAILMENT (stored is more specific)
    if _are_synonyms(q, s):
        return "MATCH"
    if q in _SCALAR_ENTAILS.get(s, frozenset()):        # stored 'shattered' entails query 'broken'
        return "MATCH"
    if _wn_hypernym_entails(s, q):                       # stored 'soldier' entails query 'serviceman'
        return "MATCH"
    return "NONE"




def incompatible(v1: str, v2: str) -> bool:
    """True iff two state VALUES cannot hold simultaneously (an antonym pair, or an explicit un-/opposite).
    Morphological un-/in- negation is also treated as incompatible (locked vs unlocked)."""
    a, b = _canon_value(v1), _canon_value(v2)
    if a == b:
        return False
    if b in _INCOMPAT.get(a, frozenset()):
        return True
    # morphological negation: 'unlocked' vs 'locked', 'unbroken' vs 'broken'
    for x, y in ((a, b), (b, a)):
        if x.startswith("un") and x[2:] == y:
            return True
        if x.startswith("in") and x[2:] == y:
            return True
    return False


@dataclass
class StateSpan:
    """One (value, polarity) state holding over an interval on an entity's timeline. polarity=+1 means the
    state HOLDS; polarity=-1 means it explicitly does NOT hold (an asserted cessation/negation)."""
    value: str
    polarity: int          # +1 holds, -1 explicitly does-not-hold
    aspect: str            # CURRENT | PRIOR | RESULT
    t_open: int
    t_close: Optional[int] = None    # None = still open (default-persist)
    source: str = ""       # the raw predication, for glass-box provenance

    def active_at(self, t: int) -> bool:
        return self.t_open <= t and (self.t_close is None or t < self.t_close)


@dataclass
class OccurrenceFact:
    """A permanent record that a telic event happened to an entity (Parsons occurrence-fact) -- never
    retracted, distinct from the closable resultant STATE. 'the vase had been broken [once]' stays true."""
    event: str             # the change-of-state event lemma ('break', 'open', ...)
    t: int
    resultant: Optional[str] = None    # the target-state value it produced ('broken', 'open')


@dataclass
class EntityStateTrack:
    spans: List[StateSpan] = field(default_factory=list)
    occurrences: List[OccurrenceFact] = field(default_factory=list)

    def add_state(self, value: str, polarity: int, aspect: str, t: int, source: str = "") -> None:
        """Fold one state assertion. Default-persist: opens a span; closes any OPEN span it contradicts
        (an incompatible value, or the same value at opposite polarity). Never overwrites a compatible
        co-state (ill + soldier both stay open)."""
        value = _canon_value(value)
        for sp in self.spans:
            if sp.t_close is not None:
                continue
            contradicts = (incompatible(sp.value, value)
                           or (sp.value == value and sp.polarity != polarity))
            if contradicts:
                sp.t_close = t
        self.spans.append(StateSpan(value=value, polarity=polarity, aspect=aspect, t_open=t, source=source))

    def add_occurrence(self, event: str, t: int, resultant: Optional[str] = None) -> None:
        self.occurrences.append(OccurrenceFact(event=event, t=t, resultant=resultant))

    def active_spans(self, t: int) -> List[StateSpan]:
        return [sp for sp in self.spans if sp.active_at(t)]


class StateRegister:
    """Per-entity STATE-HISTORY register. Fold abstract state events over discourse; query the timeline.

    An abstract state event is a tuple  (entity, value, polarity, aspect, t)  (+ optional source), OR a
    resultant-of-telic event via apply_event. This CORE is spaCy-free (the prose->events extraction is the
    StateReader adapter). Reuses the location_register interval-bookkeeping shape (value/t_open/t_close),
    generalised to MULTIPLE concurrent spans per entity (states are not mutually exclusive) + a permanent
    occurrence log (telic two-field split).

    Usage:
        reg = StateRegister().start(["house", "she"])
        reg.apply_state("house", "grand", aspect=PRIOR, t=1)     # "the house had been grand"
        reg.apply_state("she", "ill", aspect=PRIOR, t=2)         # "she had been ill"
        reg.is_in_state("house", "grand", t=5)   # -> True  (default open-through, not cancelled)
        reg.had_been("she", t=5)                 # -> {"ill"}
    """

    def __init__(self) -> None:
        self.tracks: Dict[str, EntityStateTrack] = {}
        self.n_clauses: int = 0

    def start(self, entities: Sequence[str], n_clauses: int = 0) -> "StateRegister":
        self.tracks = {e: EntityStateTrack() for e in entities}
        self.n_clauses = int(n_clauses)
        return self

    def _track(self, entity: str) -> EntityStateTrack:
        if entity not in self.tracks:
            self.tracks[entity] = EntityStateTrack()
        return self.tracks[entity]

    def apply_state(self, entity: str, value: str, aspect: str = CURRENT, polarity: int = 1,
                    t: int = 0, source: str = "") -> None:
        """Fold one copular/perfect state predication onto an entity's timeline."""
        if aspect not in ASPECTS:
            raise ValueError(f"unknown aspect {aspect!r}; expected one of {ASPECTS}")
        if t + 1 > self.n_clauses:
            self.n_clauses = t + 1
        self._track(entity).add_state(value, int(polarity), aspect, t, source)

    def apply_event(self, entity: str, event: str, resultant: Optional[str], t: int, source: str = "") -> None:
        """Fold one telic change-of-state event: record the permanent OCCURRENCE-FACT AND, if it names a
        resultant target-state, open a default-persisting RESULT span (Parsons two-field split)."""
        if t + 1 > self.n_clauses:
            self.n_clauses = t + 1
        tr = self._track(entity)
        tr.add_occurrence(event, t, resultant)
        if resultant:
            tr.add_state(resultant, 1, RESULT, t, source or event)

    def fold(self, entities: Sequence[str],
             events: Sequence[Tuple], n_clauses: int = 0) -> "StateRegister":
        """Convenience: start(entities) then apply a list of events in order. Each event is either
        ('state', entity, value, aspect, polarity, t) or ('event', entity, verb, resultant, t)."""
        self.start(entities, n_clauses=n_clauses)
        for ev in events:
            if ev[0] == "state":
                _, entity, value, aspect, polarity, t = ev
                self.apply_state(entity, value, aspect=aspect, polarity=polarity, t=t)
            elif ev[0] == "event":
                _, entity, verb, resultant, t = ev
                self.apply_event(entity, verb, resultant, t)
            else:
                raise ValueError(f"unknown event kind {ev[0]!r}")
        return self

    # -- queries --------------------------------------------------------------
    def _t(self, t: Optional[int]) -> int:
        return (max(0, self.n_clauses - 1) if t is None else t)

    def is_in_state(self, entity: str, value: str, t: Optional[int] = None,
                    semantic: bool = False) -> Optional[bool]:
        """Is entity X in state `value` at clause t? True (an active span determines the value HOLDS), False
        (an active incompatible/negated span, or a CLOSED prior span that held -> no longer), or None
        (undetermined -> glass-box UNKNOWN, not a guess). semantic=True matches via the ATL-hub WordNet
        matcher (synonymy/entailment/typed-antonymy with the three guards); semantic=False is exact-value."""
        tr = self.tracks.get(entity)
        if tr is None:
            return None
        t = self._t(t)
        val = _canon_value(value)
        active_match = active_no = saw_before_t = False
        for sp in tr.spans:
            if semantic:
                m = state_match(val, sp.value, sp.polarity)          # MATCH / NO / NONE
            elif sp.value == val:
                m = "MATCH" if sp.polarity == 1 else "NO"
            elif sp.polarity == 1 and incompatible(sp.value, val):
                m = "NO"
            else:
                m = "NONE"
            if m == "NONE":
                continue
            if sp.t_open <= t:
                saw_before_t = True
            if sp.active_at(t):
                active_match |= (m == "MATCH")
                active_no |= (m == "NO")
        if active_match:            # a positive assertion of the queried state holds now
            return True
        if active_no:               # an incompatible/negated state actively holds now
            return False
        if saw_before_t:            # was determinable at/before t but nothing active now -> closed/superseded
            return False
        return None

    def state_at(self, entity: str, t: Optional[int] = None) -> Set[str]:
        """The set of state values that HOLD (active +span) for entity X at clause t."""
        tr = self.tracks.get(entity)
        if tr is None:
            return set()
        t = self._t(t)
        return {sp.value for sp in tr.spans if sp.active_at(t) and sp.polarity == 1}

    def had_been(self, entity: str, t: Optional[int] = None) -> Set[str]:
        """The set of states entity X HAS BEEN IN up to clause t (the state history): every +span whose
        value was asserted at/before t, whether still open or since closed. Answers 'what state had X
        been in?' -- the perfect/retrospective query. Includes resultant states of telic events."""
        tr = self.tracks.get(entity)
        if tr is None:
            return set()
        t = self._t(t)
        return {sp.value for sp in tr.spans if sp.polarity == 1 and sp.t_open <= t}

    def occurrences_of(self, entity: str, t: Optional[int] = None) -> List[OccurrenceFact]:
        """The permanent telic occurrence-facts for entity X at/before t (never retracted)."""
        tr = self.tracks.get(entity)
        if tr is None:
            return []
        t = self._t(t)
        return [o for o in tr.occurrences if o.t <= t]

    def spans_of(self, entity: str) -> List[StateSpan]:
        tr = self.tracks.get(entity)
        return list(tr.spans) if tr else []


def _self_test() -> None:
    ok = 0
    cases = []

    # 1. ENTITY BINDING: two entities, two prior states. A nearest/entity-blind guess mis-binds one.
    reg = StateRegister().fold(
        ["house", "she"],
        [("state", "house", "grand", PRIOR, 1, 1),
         ("state", "she", "ill", PRIOR, 1, 2)], n_clauses=6)
    cases.append(("bind: house had been grand", reg.is_in_state("house", "grand", 5) is True))
    cases.append(("bind: she was NOT the grand one", reg.is_in_state("she", "grand", 5) is None))
    cases.append(("bind: she had been ill", "ill" in reg.had_been("she", 5)))

    # 2. RESULTANT STATE from a telic verb (no adjective present): register infers 'open'.
    reg = StateRegister().fold(["door"], [("event", "door", "open", "open", 2)], n_clauses=5)
    cases.append(("result: door opened -> is open", reg.is_in_state("door", "open", 4) is True))
    cases.append(("result: occurrence-fact recorded", len(reg.occurrences_of("door", 4)) == 1))

    # 3. SUPERSEDE / cancellation: locked then unlocked -> not locked at end (interval closes on antonym).
    reg = StateRegister().fold(
        ["door"],
        [("state", "door", "locked", CURRENT, 1, 1),
         ("event", "door", "unlock", "unlocked", 3)], n_clauses=6)
    cases.append(("supersede: locked closed by unlock", reg.is_in_state("door", "locked", 5) is False))
    cases.append(("supersede: unlocked now holds", reg.is_in_state("door", "unlocked", 5) is True))
    cases.append(("supersede: had_been remembers locked", "locked" in reg.had_been("door", 5)))

    # 4. PERFECT does NOT auto-close (research: cancellable default). 'had been a soldier', never cancelled.
    reg = StateRegister().fold(["he"], [("state", "he", "soldier", PRIOR, 1, 1)], n_clauses=6)
    cases.append(("perfect: soldier default-open (not auto-closed)", reg.is_in_state("he", "soldier", 5) is True))

    # 5. CO-STATES are not mutually exclusive: ill AND soldier both hold.
    reg = StateRegister().fold(
        ["he"],
        [("state", "he", "soldier", PRIOR, 1, 1),
         ("state", "he", "ill", CURRENT, 1, 2)], n_clauses=6)
    cases.append(("co-state: soldier still holds after ill added", reg.is_in_state("he", "soldier", 5) is True))
    cases.append(("co-state: ill also holds", reg.is_in_state("he", "ill", 5) is True))

    for note, good in cases:
        ok += int(bool(good))
        print(f"  [{'PASS' if good else 'FAIL'}] {note}")
    print(f"SELF-TEST {ok}/{len(cases)} cases")
    assert ok == len(cases), f"state_register core self-test failed ({ok}/{len(cases)})"


if __name__ == "__main__":
    _self_test()
