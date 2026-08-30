"""Construction gold for the belief timeline: false-belief-OVER-TIME narratives with query points
at multiple story-times. Golds are DEFINITIONAL and unambiguous by construction (an agent believes
what it last OBSERVED; a false belief = that stale value differs from reality) -- the same
by-construction basis as the integrated ToM gold and the temporal-order construction gold.

The population is built to be UNSOLVABLE by a timeline-agnostic current-belief tracker:
  - MULTI_CHANGE + past-T query: "what did A think EARLIER?" -- the timeline knows the earlier
    belief; a current-belief-only tracker only holds the latest.
  - RE_OBSERVE + intermediate-T query: A's belief is STALE (false) between an unobserved change and
    a later re-observation that corrects it; the current-belief tracker reports the corrected value
    for all t.
  - TWO_AGENT: two agents with divergent observation histories, queried at several times.
  - FLASHBACK: narration order != chronological order (isolates the temporal-order register).
Reality + memory queries are controls (the timeline must not corrupt world/initial tracking).

ASCII-only. Deterministic given the seed.
"""
from __future__ import annotations

import random
from typing import List

from experiments.belief_timeline import (
    Scenario, WorldEvent, timeline_belief, reality_at, initial_value,
)

LOCATIONS = ["basket", "box", "drawer", "cupboard", "shelf", "bag", "chest", "pocket",
             "crate", "trunk", "cabinet", "bin"]
AGENTS = ["Anna", "Ben", "Cora", "Dan", "Ella", "Finn", "Gina", "Hugo", "Iris", "Jack"]
OBJECTS = ["marble", "ball", "key", "letter", "ring", "coin", "book", "apple", "watch", "toy"]


def _queries_for_agent(events, observed, agent, obj, tags):
    """Belief queries at each INTERMEDIATE gap (past-T) plus the final time, a false_belief query at
    each gap, and reality/memory controls. Golds computed from the mechanism (definitional)."""
    qs = []
    chronos = sorted(e.chrono for e in events if e.obj == obj)
    # query at t just after each event (t = chrono + 0.5), and after the last
    tpoints = [c + 0.5 for c in chronos]
    for t in tpoints:
        b = timeline_belief(events, observed, agent, obj, t)
        if b is not None:
            qs.append({"agent": agent, "obj": obj, "t": t, "type": "belief", "gold": b})
            r = reality_at(events, obj, t)
            qs.append({"agent": agent, "obj": obj, "t": t, "type": "false_belief",
                       "gold": bool(b != r)})
    # reality control at the final time
    tf = tpoints[-1]
    qs.append({"agent": agent, "obj": obj, "t": tf, "type": "reality",
               "gold": reality_at(events, obj, tf)})
    # memory control (the initial placement)
    qs.append({"agent": agent, "obj": obj, "t": tf, "type": "memory",
               "gold": initial_value(events, obj)})
    return qs


def _mk_multi_change(rng, sid) -> Scenario:
    """A observes a SEQUENCE of moves; past-T queries recover the earlier belief a current-belief
    tracker has overwritten."""
    a = rng.choice(AGENTS)
    obj = rng.choice(OBJECTS)
    locs = rng.sample(LOCATIONS, k=rng.randint(3, 4))
    events, observed = [], {}
    for i, loc in enumerate(locs):
        events.append(WorldEvent(obj, loc, chrono=i, narr=i, kind="initial" if i == 0 else "move"))
        observed[(a, i)] = True   # A witnesses every change -> belief tracks each, past-T recovers
    qs = _queries_for_agent(events, observed, a, obj, ["multi_change", "past_t"])
    return Scenario(sid, [a], events, observed, qs, tags=["multi_change", "past_t"])


def _mk_re_observe(rng, sid) -> Scenario:
    """A sees init, misses an unobserved move (stale/false belief), then RE-OBSERVES (corrected).
    The intermediate-T query is the stale belief a current-belief tracker overwrites."""
    a = rng.choice(AGENTS)
    obj = rng.choice(OBJECTS)
    l0, l1 = rng.sample(LOCATIONS, k=2)
    events = [
        WorldEvent(obj, l0, chrono=0, narr=0, kind="initial"),
        WorldEvent(obj, l1, chrono=1, narr=1, kind="move"),     # unobserved by A
        WorldEvent(obj, l1, chrono=2, narr=2, kind="move"),     # A re-observes at l1
    ]
    observed = {(a, 0): True, (a, 1): False, (a, 2): True}
    qs = _queries_for_agent(events, observed, a, obj, ["re_observe"])
    return Scenario(sid, [a], events, observed, qs, tags=["re_observe", "past_t"])


def _mk_stale(rng, sid) -> Scenario:
    """Classic Sally-Anne: A sees init, misses the move; belief stays stale. Discriminates the
    timeline from the omniscient/reality reader and always-initial, not from current-belief."""
    a = rng.choice(AGENTS)
    obj = rng.choice(OBJECTS)
    l0, l1 = rng.sample(LOCATIONS, k=2)
    events = [
        WorldEvent(obj, l0, chrono=0, narr=0, kind="initial"),
        WorldEvent(obj, l1, chrono=1, narr=1, kind="move"),
    ]
    observed = {(a, 0): True, (a, 1): False}
    qs = _queries_for_agent(events, observed, a, obj, ["stale"])
    return Scenario(sid, [a], events, observed, qs, tags=["stale"])


def _mk_two_agent(rng, sid) -> Scenario:
    """Two agents with divergent observation of the same object's moves; queried at several times."""
    a, b = rng.sample(AGENTS, k=2)
    obj = rng.choice(OBJECTS)
    locs = rng.sample(LOCATIONS, k=3)
    events, observed = [], {}
    for i, loc in enumerate(locs):
        events.append(WorldEvent(obj, loc, chrono=i, narr=i, kind="initial" if i == 0 else "move"))
        observed[(a, i)] = True                       # A sees everything
        observed[(b, i)] = (i == 0)                   # B only saw the start -> stale for later moves
    qs = _queries_for_agent(events, observed, a, obj, ["two_agent"])
    qs += _queries_for_agent(events, observed, b, obj, ["two_agent"])
    return Scenario(sid, [a, b], events, observed, qs, tags=["two_agent", "past_t"])


def _mk_flashback(rng, sid) -> Scenario:
    """narration order != chronological order: the LATER-narrated event happened FIRST (past-perfect
    flashback). narr is scrambled relative to chrono; the narration-order timeline mis-sequences."""
    a = rng.choice(AGENTS)
    obj = rng.choice(OBJECTS)
    locs = rng.sample(LOCATIONS, k=3)
    events, observed = [], {}
    # chrono 0,1,2 but narration presents them 2,0,1 (a flashback reveals the earliest change last)
    narr_perm = [1, 2, 0]
    for i, loc in enumerate(locs):
        events.append(WorldEvent(obj, loc, chrono=i, narr=narr_perm[i],
                                 kind="initial" if i == 0 else "move"))
        observed[(a, i)] = True
    qs = _queries_for_agent(events, observed, a, obj, ["flashback"])
    return Scenario(sid, [a], events, observed, qs, tags=["flashback", "past_t"])


def _mk_deception(rng, sid) -> Scenario:
    """DECEPTION (research drill Q5-Wall4: belief updates by COMMUNICATION, not only observation). A
    sees the object in l0; then someone ASSERTS (falsely) it is in l1 -- the object never moved. A
    believes the lie (false belief by testimony). The current-belief floor overwrites the earlier
    true belief; the past-T query recovers it. reality stays l0 (testimony does not move the world)."""
    a = rng.choice(AGENTS)
    obj = rng.choice(OBJECTS)
    l0, l1 = rng.sample(LOCATIONS, k=2)
    events = [
        WorldEvent(obj, l0, chrono=0, narr=0, kind="initial", affects_reality=True),
        WorldEvent(obj, l1, chrono=1, narr=1, kind="testimony", affects_reality=False),  # a LIE
    ]
    observed = {(a, 0): True, (a, 1): True}   # A witnesses the placement AND receives the assertion
    qs = _queries_for_agent(events, observed, a, obj, ["deception"])
    return Scenario(sid, [a], events, observed, qs, tags=["deception", "past_t"])


def _mk_informed(rng, sid) -> Scenario:
    """TRUE testimony control (belief tracks the CONTENT communicated -- makes deception can-fail). A
    misses a real move (l0->l1 unobserved), then is TRUTHFULLY told it is in l1 -> belief corrected
    to the true value by testimony. Stale (false) before being told, true after."""
    a = rng.choice(AGENTS)
    obj = rng.choice(OBJECTS)
    l0, l1 = rng.sample(LOCATIONS, k=2)
    events = [
        WorldEvent(obj, l0, chrono=0, narr=0, kind="initial", affects_reality=True),
        WorldEvent(obj, l1, chrono=1, narr=1, kind="move", affects_reality=True),        # unobserved
        WorldEvent(obj, l1, chrono=2, narr=2, kind="testimony", affects_reality=False),  # truthful
    ]
    observed = {(a, 0): True, (a, 1): False, (a, 2): True}
    qs = _queries_for_agent(events, observed, a, obj, ["informed"])
    return Scenario(sid, [a], events, observed, qs, tags=["informed", "past_t"])


BUILDERS = {
    "multi_change": _mk_multi_change,
    "re_observe": _mk_re_observe,
    "stale": _mk_stale,
    "two_agent": _mk_two_agent,
    "flashback": _mk_flashback,
    "deception": _mk_deception,
    "informed": _mk_informed,
}
# weighted toward the discriminating structures
MIX = (["multi_change"] * 4 + ["re_observe"] * 4 + ["two_agent"] * 3 + ["stale"] * 2
       + ["flashback"] * 2 + ["deception"] * 2 + ["informed"] * 1)


def generate_gold(n: int = 60, seed: int = 20260829) -> List[Scenario]:
    rng = random.Random(seed)
    out = []
    for i in range(n):
        kind = MIX[i % len(MIX)]
        out.append(BUILDERS[kind](rng, f"{kind}_{i:03d}"))
    return out


def gold_stats(scens):
    from collections import Counter
    qtypes = Counter(q["type"] for s in scens for q in s.queries)
    tagc = Counter(t for s in scens for t in s.tags)
    n_belief = qtypes.get("belief", 0)
    return {"n_scenarios": len(scens), "n_queries": sum(len(s.queries) for s in scens),
            "qtypes": dict(qtypes), "tags": dict(tagc), "n_belief": n_belief}


if __name__ == "__main__":
    g = generate_gold()
    print(gold_stats(g))
    # sanity: the current-belief floor must be WRONG on a meaningful fraction of belief queries
    from experiments.belief_timeline import current_belief_floor
    disc = 0
    tot = 0
    for s in g:
        for q in s.queries:
            if q["type"] != "belief":
                continue
            tot += 1
            fl = current_belief_floor(s.events, s.observed, q["agent"], q["obj"], q["t"])
            if fl != q["gold"]:
                disc += 1
    print(f"belief queries where current-belief floor != timeline gold: {disc}/{tot} "
          f"({disc/tot:.3f})")
