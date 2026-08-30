"""Per-agent BELIEF TIMELINE -- what an agent knew AT A GIVEN POINT in the story.

THE GAP THIS FILLS (disk-verified). `hdlab/belief_partition.py` (integrated ToM) tracks a SINGLE
belief per (agent, object): `believed_location(observed, initial, final) = final if observed else
initial`. That is a SNAPSHOT of ONE change -- it cannot answer "what did A think at time T?",
cannot handle a SEQUENCE of changes (some observed, some not), and cannot express a STALE belief
that is later corrected. The `_temporal_order_register` (integrated) gives event ORDER but knows
nothing about agents. NOTHING composes them into a per-agent belief that is a function of
reading-time. This module is that composition.

BRAIN GROUNDING (PINNED -- copy the operation):
  - Per-agent belief is kept SEPARATE from reality (mentalizing network, TPJ/mPFC; Saxe & Kanwisher
    2003). belief_partition already does this; we reuse its FHRR banks.
  - Belief updates ONLY on OBSERVED events ("seeing leads to knowing"; Wimmer & Perner 1983). A false
    belief is a belief formed BEFORE an unobserved change.
  - THE COMPOSITION (the new, pinned part): an agent's belief about a fact is a PIECEWISE-CONSTANT
    (sample-and-hold) function of story-time -- it JUMPS at an observed event and PERSISTS unchanged
    between events (default-persist / temporal inertia; Dowty 1986, the same persistence the SPACE
    location_register and the entity state register use). "What did A know at time T" is that
    function read at T. The event ORDER (which change is before which, and where T sits) comes from
    the temporal-order register (episodic/relational temporal memory; Reichenbach reference time
    carried across discourse). This is a faithful GENERALIZATION of belief_partition from n=1 change
    to n changes over the register's ordered timeline.

OUR-INVENTION-UNDER-TEST (sweep, do not adopt): the timeline REPRESENTATION.
  - REP A (INTERVAL sample-and-hold): explicit per-(agent,object) update list; belief(T) = value of
    the latest OBSERVED event with chrono <= T (else the initial observed value). Read OUT on the
    substrate's OWN FHRR organs (belief_partition.code + hdlab.binding.bind/unbind + cleanup_argmax),
    so the answer comes from the substrate, glass-box.
  - REP B (FHRR TEMPORAL-CONTEXT register): bind each observed (object,value) to a graded temporal
    context code ctx(chrono) (hdlab.graded_temporal_context) and superpose per agent; read at T by
    probing with the context. Measures whether a smooth episodic-contiguity code recovers the exact
    sample-and-hold (expected: a lossy CONFIDENCE layer, not extra accuracy -- the same finding the
    temporal-order problem reported for discrete-vs-continuous).

Reuses (does NOT rebuild): hdlab.belief_partition (per-agent FHRR banks + the knowledge gate),
hdlab.binding, hdlab.situation_model_accumulate.cleanup_argmax, hdlab.graded_temporal_context.
ASCII-only. Deterministic given fixed seeds. Substrate-only (no LLM at inference).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class WorldEvent:
    """A change to (or an assertion about) the world. After this event an observer takes `obj` to
    have value `value`. `chrono` is the event's position on the reconstructed CHRONOLOGY (from the
    temporal-order register); `narr` is its position in the TEXT (narration order -- differs under a
    flashback). `affects_reality=True` for a real world-change; `affects_reality=False` for a
    COMMUNICATED assertion (testimony) that updates a told agent's BELIEF but not the world -- so a
    FALSE assertion produces a false belief by a non-observation route (the deception case; research
    drill Q5-Wall4: belief also updates by communication, not only observation)."""
    obj: str
    value: str
    chrono: int
    narr: int
    kind: str = "move"          # "initial" placement / "move" / "testimony" (asserted, may be false)
    affects_reality: bool = True


@dataclass
class InferenceEdge:
    """An INFERRED belief-update (research drill 2026-08-30; Sodian & Wimmer 1987 -- inference is a
    dissociable knowledge SOURCE, attributed ~2 years after perception). An agent comes to believe
    `conclusion` about `obj` by REASONING from premises it OBSERVED, without perceiving the conclusion
    directly. It fires ONLY if the agent observed ALL `premise_chronos` (strictly evidence-gated -- the
    inference analog of observation-gating / anti-curse-of-knowledge), and is time-stamped at
    `fire_chrono` (the last premise's arrival), NOT earlier. `schema` names a brain-plausible closed
    rule (exclusion / transitive-spatial / modus-ponens); the general derivation engine is a separate
    next problem."""
    obj: str
    conclusion: str
    premise_chronos: tuple
    fire_chrono: float
    schema: str = "exclusion"


def fired_inference_events(agent: str, edges, observed, mode: str = "gated"):
    """Return the inference-derived pseudo-events for `agent` (WorldEvents that update BELIEF but not
    the world), plus the observed-bits that attach them. mode: 'gated' = fire only if the agent
    observed ALL premises (brain-faithful); 'omniscient' = fire regardless (the OVER-ATTRIBUTION floor,
    curse-of-knowledge for inference); 'never' = no inference (the UNDER-ATTRIBUTION floor)."""
    ev, obs = [], {}
    if mode == "never":
        return ev, obs
    for e in edges:
        has_all = all(observed.get((agent, pc), False) for pc in e.premise_chronos)
        if mode == "gated" and not has_all:
            continue
        ev.append(WorldEvent(e.obj, e.conclusion, chrono=e.fire_chrono, narr=e.fire_chrono,
                             kind="inferred", affects_reality=False))
        obs[(agent, e.fire_chrono)] = True
    return ev, obs


@dataclass
class Scenario:
    """One false-belief-over-time narrative: a set of world events, per-(agent,event) observation
    bits, and belief/reality/memory queries at specified story-times."""
    sid: str
    agents: List[str]
    events: List[WorldEvent]
    observed: Dict[Tuple[str, int], bool]   # (agent, chrono) -> did agent witness that event?
    queries: List[dict]                      # {agent,obj,t,type in {belief,false_belief,reality,memory},gold}
    text: str = ""
    tags: List[str] = field(default_factory=list)   # e.g. ["past_t","re_observe","flashback"]


# ---------------------------------------------------------------------------
# The SYMBOLIC computations (the mechanism; the substrate read-out wraps these).
# ---------------------------------------------------------------------------
def _events_about(events: Sequence[WorldEvent], obj: str) -> List[WorldEvent]:
    return [e for e in events if e.obj == obj]


def initial_value(events: Sequence[WorldEvent], obj: str) -> Optional[str]:
    """The object's first REAL (world-affecting) placement value on the chronology (testimony
    pseudo-events do not count as the object's true initial location)."""
    ev = sorted([e for e in _events_about(events, obj) if e.affects_reality], key=lambda e: e.chrono)
    return ev[0].value if ev else None


def reality_at(events: Sequence[WorldEvent], obj: str, t: float) -> Optional[str]:
    """TRUE value of obj at story-time t = value of the latest REAL (world-affecting) event about obj
    with chrono <= t. Testimony (affects_reality=False) never moves the world."""
    ev = [e for e in _events_about(events, obj) if e.affects_reality and e.chrono <= t]
    if not ev:
        return None
    return max(ev, key=lambda e: e.chrono).value


def timeline_belief(events, observed, agent: str, obj: str, t: float) -> Optional[str]:
    """THE BELIEF TIMELINE (rep A, sample-and-hold): agent's belief about obj at story-time t =
    value of the LATEST event about obj that the agent OBSERVED with chrono <= t. Persists between
    observed events (default-persist). None if the agent has observed nothing about obj by t."""
    ev = [e for e in _events_about(events, obj)
          if e.chrono <= t and observed.get((agent, e.chrono), False)]
    if not ev:
        return None
    return max(ev, key=lambda e: e.chrono).value


def divergence(events, observed, a: str, b: str, obj: str, t: float, belief_fn=None) -> Optional[bool]:
    """KNOWLEDGE-GAP query (dramatic irony / secret / deception substrate): do agents a and b hold
    DIFFERENT beliefs about obj at story-time t? True if their beliefs disagree. belief_fn selects the
    tracker (timeline vs a floor) so the same query scores every arm."""
    fn = belief_fn or timeline_belief
    ba = fn(events, observed, a, obj, t)
    bb = fn(events, observed, b, obj, t)
    if ba is None or bb is None:
        return None
    return ba != bb


def knowledge_advantage(events, observed, a: str, b: str, obj: str, t: float,
                        belief_fn=None) -> Optional[bool]:
    """The reader-level DECEPTION/IRONY-opportunity gap: at t, does a hold the CURRENT-TRUE belief
    about obj while b holds a FALSE (stale) one? True = a is informed and b is not -- the asymmetry a
    deceiver exploits and a dramatic-irony scene turns on. Computed by the reader's belief timeline
    (first-order: the reader detects the asymmetry; it does not require a to model b's mind)."""
    fn = belief_fn or timeline_belief
    ba = fn(events, observed, a, obj, t)
    bb = fn(events, observed, b, obj, t)
    r = reality_at(events, obj, t)
    if ba is None or bb is None or r is None:
        return None
    return (ba == r) and (bb != r)


def current_belief_floor(events, observed, agent: str, obj: str, t: float) -> Optional[str]:
    """TIMELINE-AGNOSTIC floor: a single 'current belief' per (agent,obj) = the LATEST value the
    agent ever observed, IGNORING the query time t. This is the strongest naive tracker -- it is
    observation-gated (same cue as the timeline) but has NO reading-time axis, so it always reports
    the agent's FINAL observed value. It is wrong exactly when belief-at-t differs from that."""
    ev = [e for e in _events_about(events, obj) if observed.get((agent, e.chrono), False)]
    if not ev:
        return None
    return max(ev, key=lambda e: e.chrono).value


def hindsight_invariant(events, observed, agent: str, obj: str, t: float,
                        novel_value: str = "__novel__") -> Optional[bool]:
    """DECOUPLING / anti-hindsight control (research drill #1, Q5-Wall1). A correct reader's answer to
    'what did A believe about obj at T' must NOT change when a LATER, UNOBSERVED world event is
    altered -- a clean agent-belief store is decoupled from the world store, so later reality cannot
    contaminate a past belief (the curse-of-knowledge the brain suffers and a clean store beats).
    Returns True if invariant, False if it leaked, None if there is no later unobserved event to
    perturb. Mutates a COPY only."""
    later = [e for e in _events_about(events, obj)
             if e.affects_reality and e.chrono > t and not observed.get((agent, e.chrono), False)]
    if not later:
        return None
    target = max(later, key=lambda e: e.chrono)
    base = timeline_belief(events, observed, agent, obj, t)
    mutated = [WorldEvent(e.obj, (novel_value if e is target else e.value), e.chrono, e.narr,
                          e.kind, e.affects_reality) for e in events]
    after = timeline_belief(mutated, observed, agent, obj, t)
    return base == after


def narration_timeline_belief(events, observed, agent: str, obj: str, t: float) -> Optional[str]:
    """Ablation that ISOLATES the temporal-order register's contribution: identical sample-and-hold
    to the belief timeline BUT ordered by NARRATION position (narr) instead of the register's
    chronology (chrono). Wrong whenever narration order != chronological order (a flashback)."""
    ev = [e for e in _events_about(events, obj)
          if e.narr <= t and observed.get((agent, e.chrono), False)]
    if not ev:
        return None
    return max(ev, key=lambda e: e.narr).value


# ---------------------------------------------------------------------------
# The SUBSTRATE read-out -- the answers above are decoded through the FHRR organs
# (belief_partition codes + hdlab.binding + cleanup_argmax), so the belief is
# READ OFF the substrate exactly as the integrated ToM organ reads it.
# ---------------------------------------------------------------------------
class SubstrateReadout:
    """Encodes a (object, believed-value) pair into an FHRR bank via the integrated belief_partition
    organ's codebook and decodes it back by unbind + cleanup over the value vocabulary. This is the
    glass-box read-out: the timeline computes WHICH value is believed; the substrate stores and
    recovers it the same way the ToM organ does."""

    def __init__(self, d: int = 1024, seed: int = 20260829) -> None:
        from hdlab.belief_partition import BeliefPartition
        self._bp = BeliefPartition(d=d, seed=seed)

    def readout(self, obj: str, value: Optional[str], vocab: Sequence[str]) -> Optional[str]:
        """Bind(obj, value) -> unbind by obj -> cleanup over the value vocab. Returns the recovered
        value symbol (identity round-trip on a clean bank; the point is that it runs on-substrate)."""
        if value is None:
            return None
        from hdlab import binding
        from hdlab.situation_model_accumulate import cleanup_argmax
        bank = binding.bind(self._bp.code("obj", obj), self._bp.code("loc", value))
        readback = binding.unbind(bank, self._bp.code("obj", obj))
        locvocab = {v: self._bp.code("loc", v) for v in vocab}
        best, _ = cleanup_argmax(readback, locvocab)
        return best


# ---------------------------------------------------------------------------
# REP B -- FHRR temporal-context belief register (the swept representation).
# ---------------------------------------------------------------------------
class TemporalContextBeliefRegister:
    """Per-agent belief stored as an FHRR superposition of observed (object,value) pairs each bound
    to a graded temporal-context code ctx(chrono) (hdlab.graded_temporal_context). Reading belief
    about obj at time t: for each candidate value v, form bind(code(obj), code(v)) and correlate the
    register, weighting by the temporal-context similarity to the LATEST observed context <= t; take
    the argmax value. A smooth-contiguity approximation to the exact sample-and-hold (rep A)."""

    def __init__(self, d: int = 1024, seed: int = 20260829, horizon: float = 64.0) -> None:
        import torch
        from hdlab.belief_partition import BeliefPartition
        from hdlab.graded_temporal_context import GradedTemporalContext
        self.d = int(d)
        self._bp = BeliefPartition(d=d, seed=seed)
        self._gtc = GradedTemporalContext(d=d, seed=seed, horizon=horizon)
        self._banks: Dict[str, "torch.Tensor"] = {}      # agent -> superposed register
        self._last_ctx: Dict[Tuple[str, str], float] = {}  # (agent,obj) -> latest observed chrono
        self._torch = torch

    def build(self, agent: str, events: Sequence[WorldEvent], observed) -> None:
        """Kept for API symmetry; the causal per-query register is built inside belief()."""
        self._banks[agent] = True

    def _causal_register(self, agent: str, obj: str, t: float, events, observed):
        """Incremental (causal) register: superpose ONLY the agent's observed (obj,value) events with
        chrono <= t, each bound to its temporal-context code. This is how an on-line reader holds the
        belief -- at reading-time t only past events are encoded (research drill Q3b: the belief(x)when
        BINDING is the FHRR bind's job; a symmetric contiguity kernel over the FULL trace would leak
        FUTURE observations, so the faithful read builds up to t)."""
        torch = self._torch
        reg = torch.zeros(self.d, dtype=torch.complex64)
        n = 0
        for e in sorted(events, key=lambda e: e.chrono):
            if e.obj != obj or e.chrono > t or not observed.get((agent, e.chrono), False):
                continue
            content = self._bp.code("obj", e.obj) * self._bp.code("loc", e.value)
            reg = reg + content * self._gtc.ctx(float(e.chrono))
            n += 1
        return (reg if n else None)

    def belief(self, agent: str, obj: str, t: float, events, observed, vocab: Sequence[str]) -> Optional[str]:
        """GRADED-CONTIGUITY read (rep B): probe the causal register at the QUERY-time context ctx(t)
        and cleanup -- the nearest PAST observed event dominates (temporal contiguity = sample-and-
        hold), with attenuated crosstalk from earlier events. No exact index is pre-resolved, so this
        genuinely tests whether the drifting temporal-context code recovers the belief value."""
        torch = self._torch
        reg = self._causal_register(agent, obj, t, events, observed)
        if reg is None:
            return None
        content = reg * torch.conj(self._gtc.ctx(float(t)))        # cue with the query-time context
        readback = content * torch.conj(self._bp.code("obj", obj))  # unbind the object
        scores = {}
        for v in vocab:
            cv = self._bp.code("loc", v)
            scores[v] = float(torch.real(torch.sum(torch.conj(cv) * readback))) / self.d
        return max(scores.items(), key=lambda kv: kv[1])[0]


# ---------------------------------------------------------------------------
# Info-free twin -- shuffle the event/observation ORDER (destroys "which change is
# before T / which observed change is latest"). The timeline must collapse.
# ---------------------------------------------------------------------------
def shuffle_order_twin(events: Sequence[WorldEvent], rng) -> List[WorldEvent]:
    """Permute the chrono indices across events (keep values + narr positions + count) -> the
    sample-and-hold 'latest observed <= t' signal is destroyed while shape is matched."""
    evs = [WorldEvent(obj=e.obj, value=e.value, chrono=e.chrono, narr=e.narr, kind=e.kind)
           for e in events]
    chronos = [e.chrono for e in evs]
    perm = list(range(len(chronos)))
    rng.shuffle(perm)
    for i, e in enumerate(evs):
        e.chrono = chronos[perm[i]]
    return evs


def remap_observed_after_twin(observed, orig_events, twin_events):
    """The observation bits are keyed by (agent, chrono). After the twin permutes chrono, re-key so
    the SAME (agent, event-identity) observation follows the event to its new shuffled chrono."""
    # map original event identity (obj,value,narr) -> new chrono
    id2new = {(e.obj, e.value, e.narr): e.chrono for e in twin_events}
    id2old = {(e.obj, e.value, e.narr): e.chrono for e in orig_events}
    new_obs = {}
    for (agent, old_chrono), bit in observed.items():
        # find the event(s) that had old_chrono, map to its new chrono
        for ident, oc in id2old.items():
            if oc == old_chrono and ident in id2new:
                new_obs[(agent, id2new[ident])] = bit
    return new_obs


# ---------------------------------------------------------------------------
# Arm registry: a uniform interface answer(agent,obj,t,vocab) for every arm.
# ---------------------------------------------------------------------------
ARMS = ("timeline", "current_belief", "narration_timeline", "omniscient", "always_initial",
        "twin", "empty", "repB_tempctx")


def make_answerer(arm: str, scen: Scenario, vocab: Sequence[str], readout: SubstrateReadout,
                  seed: int = 0, repB: Optional[TemporalContextBeliefRegister] = None):
    """Return a function answer(agent,obj,t) -> value symbol (or None), decoded on-substrate."""
    events, observed = scen.events, scen.observed

    if arm == "twin":
        import random
        rng = random.Random(seed + hash(scen.sid) % 100000)
        tw = shuffle_order_twin(events, rng)
        tw_obs = remap_observed_after_twin(observed, events, tw)
        events, observed = tw, tw_obs

    def answer(agent: str, obj: str, t: float) -> Optional[str]:
        if arm == "empty":
            val = None
        elif arm in ("timeline", "twin"):
            val = timeline_belief(events, observed, agent, obj, t)
        elif arm == "current_belief":
            val = current_belief_floor(events, observed, agent, obj, t)
        elif arm == "narration_timeline":
            val = narration_timeline_belief(events, observed, agent, obj, t)
        elif arm == "omniscient":
            val = reality_at(events, obj, t)
        elif arm == "always_initial":
            val = initial_value(events, obj)
        elif arm == "repB_tempctx":
            return repB.belief(agent, obj, t, events, observed, vocab) if repB else None
        else:
            raise ValueError(f"unknown arm {arm}")
        return readout.readout(obj, val, vocab)

    return answer


def _self_test() -> None:
    """Sally-Anne over time + a re-observe case: the timeline answers past-T correctly where the
    current-belief floor cannot; the twin loses; reality is intact."""
    # Anna puts marble in basket (t0, Anna sees). Ben moves basket->box (t1, Anna absent).
    # Anna returns and sees it in box (t2, Anna sees).
    events = [
        WorldEvent("marble", "basket", chrono=0, narr=0, kind="initial"),
        WorldEvent("marble", "box", chrono=1, narr=1, kind="move"),
        WorldEvent("marble", "box", chrono=2, narr=2, kind="move"),  # Anna re-sees (same value)
    ]
    observed = {("Anna", 0): True, ("Anna", 1): False, ("Anna", 2): True}
    vocab = ["basket", "box", "drawer"]
    ro = SubstrateReadout(d=512)

    # belief at t=0.5 (before the move): basket
    assert timeline_belief(events, observed, "Anna", "marble", 0.5) == "basket"
    # belief at t=1.5 (after unobserved move, before re-see): STALE basket (false belief)
    assert timeline_belief(events, observed, "Anna", "marble", 1.5) == "basket"
    # belief at t=2.5 (after re-see): box (corrected)
    assert timeline_belief(events, observed, "Anna", "marble", 2.5) == "box"
    # the timeline-agnostic floor reports the FINAL observed value (box) at EVERY t -> wrong at t=1.5
    assert current_belief_floor(events, observed, "Anna", "marble", 1.5) == "box"
    # reality at t=1.5 is box (true), and at t=0.5 basket
    assert reality_at(events, "marble", 1.5) == "box"
    assert reality_at(events, "marble", 0.5) == "basket"
    # substrate read-out round-trips
    assert ro.readout("marble", "basket", vocab) == "basket"
    assert ro.readout("marble", "box", vocab) == "box"

    # twin: shuffle order -> the stale-belief signal should be destroyed on at least some seeds
    import random
    tw = shuffle_order_twin(events, random.Random(3))
    assert sorted(e.chrono for e in tw) == [0, 1, 2]  # same multiset of positions
    print("belief_timeline self-test PASS")


if __name__ == "__main__":
    _self_test()
