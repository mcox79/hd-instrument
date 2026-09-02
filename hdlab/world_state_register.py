"""world_state_register -- the situation model's MISSING mutable WORLD-STATE dimension as a set of
STRIPS-style operators over RELATIONAL predicates, driven by event EFFECTS and read by event
PRECONDITIONS. Problem: situation_model_has_no_mutable_world_state_register.

PROMOTED VERBATIM (2026-09-01, Q111) from experiments/world_state_register.py -- the owner-DONE problem
`situation_model_has_no_mutable_world_state_register` (PARTIAL = mechanism+learning SOLVED with the full
control battery; open-text a located coref residual; reverified 36/36 first-hand, EXCELLENT). The CODE is
byte-for-byte identical to the validated cell so a register the live reader builds equals the cell's
`WorldState().fold(reps)`; the reader wires it behind a default-off `track_world_state` flag.

WHAT THIS ADDS OVER WHAT ALREADY EXISTS ON DISK (the disk outranks the brief):
  * hdlab/location_register.py ALREADY is a mutable register for at(obj,loc): apply_motion(effect) ->
    where_is(entity,t)(query). SPACE dimension, promoted+wired.
  * hdlab/state_register.py ALREADY is a mutable register for entity ATTRIBUTE states (open/broken/ill)
    read from EXPLICIT copular/perfect/resultant constructions. ENTITIES dimension, promoted+wired.
  * The aligner (exp_operator_partial_order_mcscript_v1) ALREADY prototyped avail/at/open STRIPS
    operators -- but ONLY as a static enable-DAG for ORDER (found ~99% causally independent -> the
    WRONG fix for order), with "NO forward simulation of a mutable state" because on short scripts
    re-toggles/transfers are RARE.
  So the genuinely-missing pieces this module builds are:
   (1) POSSESSION have(holder,obj) -- the one predicate in the brief's own list (have/at/open) with NO
       register; the MAXIMALLY-MUTABLE predicate (transfer A->B->C flips have() true<->false), where a
       static "ever-held" bag and a last-mention/recency floor are both fooled.
   (2) a MUTABLE FORWARD-APPLICATION over story-time -- has(e,obj,t) = state AFTER events <= t (the thing
       the aligner's static DAG explicitly omitted), so the register TRACKS state, not recency.
   (3) a PRECONDITION-READ / violation layer -- every existing register is WRITE+query; NONE reads state
       as an event PRECONDITION. An event whose precondition is unmet in the register flags a
       bridging-inference demand (Haviland & Clark 1974). This is what makes it a world MODEL, not a log.

BRAIN FRAME:
  PINNED (copy the COMPUTATION):
    * the situation model maintains a MUTABLE CURRENT STATE, updated incrementally by event EFFECTS and
      read by event PRECONDITIONS (Zwaan & Radvansky 1998 event-indexing; van Dijk & Kintsch 1983).
    * an object's representational availability tracks its CURRENT relation to the protagonist, NOT its
      last mention (Glenberg, Meyer & Lindem 1987 -- "put on / took off the sweatshirt" changes the
      object's accessibility): this is exactly the possession/association relation, PINNED.
    * an event has PRECONDITIONS (state required) and EFFECTS (state changed); the STRIPS/operator form
      (Fikes & Nilsson 1971) is the computational-level description of the brain's forward model; an
      unmet precondition triggers a bridging inference (Haviland & Clark 1974).
  OUR-INVENTION-UNDER-TEST (SWEEP, do not adopt): the verb->operator lexicon (GIVE/GET/LOSE/TOGGLE
    classes -- seeded conceptually from VerbNet give-13.1/get-13.5.1/send-11.1/obtain-13.5.2 caused-
    possession classes; a full VerbNet-derived asset is the foundation upgrade), the single-holder
    possession assumption, the discrete-interval representation (reuses the location_register shape).

GLASS-BOX: pure symbolic, NO external LLM, NO network at inference. spaCy-FREE core (consumes abstract
events like the location/state register cores) so the mechanism is isolable from extraction. ASCII only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

# --------------------------------------------------------------------------- verb -> operator lexicon
# OUR-INVENTION-UNDER-TEST. Seeded conceptually from VerbNet caused-possession classes; swept, not adopted.
GIVE = set((
    "give hand pass offer sell lend feed send mail deliver grant award present donate loan bequeath "
    "toss throw serve return provide supply entrust bring"
).split())                       # agent -> recipient (ARG2). effect: ~have(agent,obj) & have(recipient,obj)
GET = set((
    "take grab get receive buy steal obtain pick fetch seize accept collect snatch acquire retrieve "
    "win inherit borrow gather claim"
).split())                       # possession to agent (optionally from a source ARG2)
LOSE = set((
    "drop lose discard leave release abandon misplace relinquish surrender forfeit spend"
).split())                       # effect: ~have(agent,obj)
TOGGLE_ON = set("open unlock unfasten uncover start light activate".split())    # state(obj) = OPEN
TOGGLE_OFF = set("close shut lock fasten cover seal".split())                   # state(obj) = CLOSED
USE = set((
    "use drink eat wash dry wear read play watch finish apply clean cut chop stir spread pour fill "
    "unlock open close draw"
).split())                       # PRECONDITION: agent must HAVE the object used (glass-box, fires on join)

OPEN = "open"
CLOSED = "closed"


# --------------------------------------------------------------------------- single-valued interval track
@dataclass
class Span:
    value: Optional[str]
    t_open: int
    t_close: Optional[int] = None   # None = still holds

    def holds_at(self, t: int) -> bool:
        return self.t_open <= t and (self.t_close is None or t < self.t_close)


class SingleValueTrack:
    """A key's single current value over story-time (possession: key=obj,value=holder; toggle:
    key=obj,value=state). Overwrite-on-change: a new value closes the current span and opens a new one.
    Mirrors hdlab/location_register.EntityTrack (single-valued: one place / one holder at a time)."""

    def __init__(self) -> None:
        self.spans: List[Span] = []

    def set(self, value: Optional[str], t: int) -> None:
        if self.spans and self.spans[-1].t_close is None:
            if self.spans[-1].value == value:
                return
            self.spans[-1].t_close = t
        self.spans.append(Span(value, t))

    def value_at(self, t: Optional[int] = None) -> Optional[str]:
        best = None
        for s in self.spans:
            if s.t_open <= (t if t is not None else 10 ** 9) and (s.t_close is None or (t is not None and t < s.t_close)):
                best = s.value
        return best

    def ever(self) -> Set[str]:
        return {s.value for s in self.spans if s.value is not None}


# --------------------------------------------------------------------------- the mutable world state
@dataclass
class Effect:
    pred: str                 # "have" | "state"
    obj: str
    value: Optional[str]      # have: holder (or None = no holder); state: OPEN/CLOSED
    t: int


@dataclass
class PreCheck:
    pred: str
    obj: str
    need: Optional[str]       # required value
    met: Optional[bool]       # True/False/None(unknown -> abstain)
    t: int
    verb: str


class WorldState:
    """Mutable relational world-state register. Possession is single-holder per object; toggle-states are
    single-valued per object. Effects applied in event order; queries return the state AFTER events <= t."""

    def __init__(self) -> None:
        self.have: Dict[str, SingleValueTrack] = {}     # obj -> holder track
        self.state: Dict[str, SingleValueTrack] = {}    # obj -> open/closed track
        self.effects: List[Effect] = []
        self.prechecks: List[PreCheck] = []

    # -- effect application ------------------------------------------------
    def _set_have(self, obj: str, holder: Optional[str], t: int) -> None:
        self.have.setdefault(obj, SingleValueTrack()).set(holder, t)
        self.effects.append(Effect("have", obj, holder, t))

    def _set_state(self, obj: str, val: str, t: int) -> None:
        self.state.setdefault(obj, SingleValueTrack()).set(val, t)
        self.effects.append(Effect("state", obj, val, t))

    @staticmethod
    def classify(v: str) -> Optional[str]:
        """Built-in fallback verb->op classifier (used only when a rep carries no explicit OP).
        The DEFAULT operator source is the FrameNet-derived lexicon (hdlab/possession_operators.py),
        supplied per-rep as rep['OP']; these sets are a small offline fallback so the core runs without nltk."""
        if v in GIVE:
            return "GIVE"
        if v in GET:
            return "GET"
        if v in LOSE:
            return "LOSE"
        if v in TOGGLE_ON:
            return "TOGGLE_ON"
        if v in TOGGLE_OFF:
            return "TOGGLE_OFF"
        return None

    def apply_event(self, rep: dict, t: int, read_preconditions: bool = True) -> None:
        """Apply one event's STRIPS effects at story-time t. rep = {PRED, AGENT, PATIENT, ARG2, PATH, OP?}.
        The operator class is rep['OP'] when supplied (FrameNet-derived or LEARNED), else the built-in
        fallback classifier -- so the SAME register runs off a resource-derived or a learned lexicon."""
        v = (rep.get("PRED") or "").lower()
        agent = rep.get("AGENT"); obj = rep.get("PATIENT"); arg2 = rep.get("ARG2")
        op = rep.get("OP") or self.classify(v)
        if read_preconditions:
            self._read_preconditions(v, agent, obj, arg2, t, op=op)
        if op == "GIVE" and obj:
            # caused change of possession: giver loses, recipient (ARG2) gains
            if agent:
                self._set_have(obj, None, t) if not arg2 else None
            if arg2:
                self._set_have(obj, arg2, t)
            elif agent:
                # give with no recipient recovered: possession leaves the agent (unknown recipient)
                self._set_have(obj, None, t)
        elif op == "GET" and obj:
            if arg2:                                  # take X from SOURCE(arg2): source loses first
                self._set_have(obj, arg2, t)          # placeholder; overwritten below by agent
            if agent:
                self._set_have(obj, agent, t)
        elif op == "LOSE" and obj:
            self._set_have(obj, None, t)
        elif op == "TOGGLE_ON" and obj:
            self._set_state(obj, OPEN, t)
        elif op == "TOGGLE_OFF" and obj:
            self._set_state(obj, CLOSED, t)

    def _read_preconditions(self, v: str, agent, obj, arg2, t: int, op: Optional[str] = None) -> None:
        """READ the current state as the event's precondition (the layer no existing register has)."""
        if v in USE and obj and agent:
            # using an object presupposes the agent has access to it (possession) -- fires as a check only
            # if the object is TRACKED (something established a holder); else unknown -> abstain.
            if obj in self.have:
                cur = self.have[obj].value_at(t)
                self.prechecks.append(PreCheck("have", obj, agent, (cur == agent), t, v))
        if op == "TOGGLE_OFF" and obj and (obj in self.state):
            cur = self.state[obj].value_at(t)
            self.prechecks.append(PreCheck("state", obj, OPEN, (cur == OPEN), t, v))   # can't close a closed thing
        if op == "GIVE" and obj and agent and (obj in self.have):
            cur = self.have[obj].value_at(t)
            self.prechecks.append(PreCheck("have", obj, agent, (cur == agent), t, v))  # can't give what you lack

    def fold(self, events: Sequence[dict], read_preconditions: bool = True) -> "WorldState":
        for t, rep in enumerate(events):
            self.apply_event(rep, t, read_preconditions=read_preconditions)
        return self

    # -- queries -----------------------------------------------------------
    def holder_of(self, obj: str, t: Optional[int] = None) -> Optional[str]:
        tr = self.have.get(obj)
        return tr.value_at(t) if tr else None

    def has(self, entity: str, obj: str, t: Optional[int] = None) -> bool:
        return self.holder_of(obj, t) == entity

    def is_open(self, obj: str, t: Optional[int] = None) -> Optional[bool]:
        tr = self.state.get(obj)
        if not tr:
            return None
        val = tr.value_at(t)
        return None if val is None else (val == OPEN)

    def unmet_preconditions(self) -> List[PreCheck]:
        """Events whose precondition was READ as FALSE -> bridging-inference demand."""
        return [p for p in self.prechecks if p.met is False]


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    ok = True

    # POSSESSION transfer chain: A has book; A gives it to B; B gives it to C.
    evs = [
        {"PRED": "get", "AGENT": "anna", "PATIENT": "book"},
        {"PRED": "give", "AGENT": "anna", "PATIENT": "book", "ARG2": "ben"},
        {"PRED": "give", "AGENT": "ben", "PATIENT": "book", "ARG2": "cara"},
    ]
    ws = WorldState().fold(evs)
    checks = [
        ("anna has book @0", ws.has("anna", "book", 0), True),
        ("anna has book @1 (just gave away)", ws.has("anna", "book", 1), False),
        ("ben has book @1", ws.has("ben", "book", 1), True),
        ("ben has book @2 (gave to cara)", ws.has("ben", "book", 2), False),
        ("cara has book @2", ws.has("cara", "book", 2), True),
        ("holder_of book @end", ws.holder_of("book"), "cara"),
        ("anna EVER held book (static bag would say yes)", "anna" in ws.have["book"].ever(), True),
    ]
    for name, got, exp in checks:
        good = got == exp
        ok = ok and good
        print("[self-test] %-45s got=%s exp=%s %s" % (name, got, exp, "OK" if good else "FAIL"), flush=True)

    # CHANGE-POINT: has(anna,book) must FLIP true->false exactly at the give (t=1), not echo recency.
    flip = ws.has("anna", "book", 0) and not ws.has("anna", "book", 1)
    print("[self-test] change-point flip at give event: %s %s" % (flip, "OK" if flip else "FAIL"), flush=True)
    ok = ok and flip

    # TOGGLE re-toggle: door opened then closed.
    evs2 = [{"PRED": "open", "AGENT": "x", "PATIENT": "door"},
            {"PRED": "close", "AGENT": "x", "PATIENT": "door"}]
    ws2 = WorldState().fold(evs2)
    tog = (ws2.is_open("door", 0) is True) and (ws2.is_open("door", 1) is False)
    print("[self-test] door open@0 then closed@1: %s %s" % (tog, "OK" if tog else "FAIL"), flush=True)
    ok = ok and tog

    # PRECONDITION violation: use a key the agent does not have.
    evs3 = [{"PRED": "get", "AGENT": "anna", "PATIENT": "key"},
            {"PRED": "give", "AGENT": "anna", "PATIENT": "key", "ARG2": "ben"},
            {"PRED": "use", "AGENT": "anna", "PATIENT": "key"}]        # anna no longer has the key
    ws3 = WorldState().fold(evs3)
    unmet = ws3.unmet_preconditions()
    viol = any(p.verb == "use" and p.obj == "key" for p in unmet)
    print("[self-test] precondition violation (anna uses key she gave away): %s %s"
          % (viol, "OK" if viol else "FAIL"), flush=True)
    ok = ok and viol

    print("[self-test] " + ("ALL OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(self_test())
