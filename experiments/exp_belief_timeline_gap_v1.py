"""The KNOWLEDGE GAP between agents over time -- the dramatic-irony / deception substrate.

The brief names dramatic irony and deception as the point; the research drill's build-change #7 was
"make the belief-vs-belief GAP a first-class query." Per-agent beliefs are necessary but the
DECISION-relevant quantity is the DIFFERENCE (Frontiers 2023 / 2025 dramatic-irony work: readers
track the reader-character and character-character knowledge GAP, and it drives real-time attention).

Two query types, over time:
  divergence(A,B,X,T)          -- do A and B disagree about X at T? (a secret / diverged knowledge)
  knowledge_advantage(A,B,X,T) -- at T, does A hold the TRUE belief while B holds a FALSE one?
                                  (the asymmetry a deceiver exploits / dramatic irony turns on)

Scenario (divergence-over-time): both see the start (agree); B departs; the object moves while A
watches and B is absent (A updates, B stale -> DIVERGE); B returns and sees (RE-CONVERGE). A
timeline-agnostic tracker sees only the FINAL state (agree) and misses the divergence window; the
belief timeline recovers the gap at each T. Info-free twin (shuffled order) LOSES.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

from experiments.belief_timeline import (
    WorldEvent, Scenario, divergence, knowledge_advantage,
    timeline_belief, current_belief_floor, shuffle_order_twin, remap_observed_after_twin,
)
from experiments.belief_timeline_gold import LOCATIONS, AGENTS, OBJECTS

OUTDIR = os.path.join(_REPO, "data", "exp_belief_timeline_gap_v1")


def _mk_divergence_scenario(rng, sid):
    """both-see-start -> B departs -> move (A sees, B absent) -> B returns-and-sees. Gap queries at
    each interval."""
    a, b = rng.sample(AGENTS, k=2)
    obj = rng.choice(OBJECTS)
    l0, l1 = rng.sample(LOCATIONS, k=2)
    events = [
        WorldEvent(obj, l0, chrono=0, narr=0, kind="initial"),   # both see the start
        WorldEvent(obj, l1, chrono=1, narr=1, kind="move"),      # A sees, B absent -> DIVERGE
        WorldEvent(obj, l1, chrono=2, narr=2, kind="move"),      # B returns and sees -> RECONVERGE
    ]
    observed = {("%s" % a, 0): True, ("%s" % b, 0): True,
                (a, 1): True, (b, 1): False,
                (a, 2): True, (b, 2): True}
    # gold gap queries at t=0.5 (agree), 1.5 (diverge, A-advantage), 2.5 (agree)
    queries = []
    for t in (0.5, 1.5, 2.5):
        queries.append({"a": a, "b": b, "obj": obj, "t": t, "type": "divergence",
                        "gold": divergence(events, observed, a, b, obj, t)})
        queries.append({"a": a, "b": b, "obj": obj, "t": t, "type": "advantage",
                        "gold": knowledge_advantage(events, observed, a, b, obj, t)})
    return Scenario(sid, [a, b], events, observed, queries, tags=["divergence"])


def _answer(qtype, events, observed, q, belief_fn):
    if qtype == "divergence":
        return divergence(events, observed, q["a"], q["b"], q["obj"], q["t"], belief_fn=belief_fn)
    return knowledge_advantage(events, observed, q["a"], q["b"], q["obj"], q["t"], belief_fn=belief_fn)


def _boot_ci(v, n_boot=2000, seed=0):
    v = np.asarray(v, float)
    if len(v) == 0:
        return (0.0, 0.0, 0.0)
    rng = np.random.default_rng(seed)
    means = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(n_boot)]
    return float(v.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def run(n=80, seed=20260830, twin_seeds=200):
    import random
    rng = random.Random(seed)
    scens = [_mk_divergence_scenario(rng, f"gap_{i:03d}") for i in range(n)]

    def score(belief_fn, twin=False, twin_seed=0):
        vv = []
        for scen in scens:
            events, observed = scen.events, scen.observed
            if twin:
                tw = shuffle_order_twin(events, random.Random(twin_seed + hash(scen.sid) % 99991))
                events2, observed2 = tw, remap_observed_after_twin(observed, events, tw)
            else:
                events2, observed2 = events, observed
            for q in scen.queries:
                pred = _answer(q["type"], events2, observed2, q, belief_fn)
                vv.append(int(pred == q["gold"]))
        return vv

    tl = score(timeline_belief)
    fl = score(current_belief_floor)
    tl_m, tl_lo, tl_hi = _boot_ci(tl, seed=seed)
    fl_m, fl_lo, fl_hi = _boot_ci(fl, seed=seed)

    twin_accs = [float(np.mean(score(timeline_belief, twin=True, twin_seed=ts)))
                 for ts in range(twin_seeds)]
    twin_p95 = float(np.percentile(twin_accs, 95))

    # split by query type + by the divergence window (t=1.5 is where the floor should fail)
    def subset(pred):
        tlv, flv = [], []
        for scen in scens:
            for q in scen.queries:
                if not pred(q):
                    continue
                tlv.append(int(_answer(q["type"], scen.events, scen.observed, q, timeline_belief) == q["gold"]))
                flv.append(int(_answer(q["type"], scen.events, scen.observed, q, current_belief_floor) == q["gold"]))
        return (float(np.mean(tlv)) if tlv else None, float(np.mean(flv)) if flv else None, len(tlv))
    div_window = subset(lambda q: abs(q["t"] - 1.5) < 1e-6)
    div_type = subset(lambda q: q["type"] == "divergence")
    adv_type = subset(lambda q: q["type"] == "advantage")

    metrics = {
        "seed": seed, "n_scenarios": len(scens), "n_queries": sum(len(s.queries) for s in scens),
        "timeline": {"acc": tl_m, "ci": [tl_lo, tl_hi]},
        "current_belief_floor": {"acc": fl_m, "ci": [fl_lo, fl_hi]},
        "twin": {"p95": twin_p95, "mean": float(np.mean(twin_accs)), "n": len(twin_accs)},
        "divergence_window_t1.5": {"timeline": div_window[0], "floor": div_window[1], "n": div_window[2]},
        "by_type": {"divergence": {"timeline": div_type[0], "floor": div_type[1], "n": div_type[2]},
                    "advantage": {"timeline": adv_type[0], "floor": adv_type[1], "n": adv_type[2]}},
        "verdict": {"ci_separated": tl_lo > fl_hi, "beats_twin": tl_lo > twin_p95},
    }
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run(n=(20 if args.self_test else 80), twin_seeds=(30 if args.self_test else 200))
    if args.self_test:
        assert m["verdict"]["ci_separated"] and m["verdict"]["beats_twin"], m["verdict"]
        print("self-test PASS", json.dumps(m["verdict"]))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 78)
    print("KNOWLEDGE GAP over time (dramatic-irony / deception substrate)")
    print("=" * 78)
    print(f"{m['n_scenarios']} scenarios, {m['n_queries']} gap queries")
    print(f"  BELIEF-TIMELINE gap-acc   {m['timeline']['acc']:.3f}  CI {m['timeline']['ci']}")
    print(f"  current-belief FLOOR      {m['current_belief_floor']['acc']:.3f}  CI {m['current_belief_floor']['ci']}")
    print(f"  info-free TWIN p95        {m['twin']['p95']:.3f}")
    print(f"  divergence window (t=1.5): timeline {m['divergence_window_t1.5']['timeline']} "
          f"vs floor {m['divergence_window_t1.5']['floor']} (n={m['divergence_window_t1.5']['n']})")
    print(f"  by type: {json.dumps(m['by_type'])}")
    print(f"  CI-SEPARATED {m['verdict']['ci_separated']}   BEATS TWIN {m['verdict']['beats_twin']}")
    print(f"written {OUTDIR}/metrics.json")


if __name__ == "__main__":
    main()
