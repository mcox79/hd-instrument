"""SECOND GOLD (external validity): hand-authored real-English belief-timeline passages with
HAND-SET golds, to show the headline (timeline 1.000 vs current-belief floor 0.460) is NOT an
artifact of the programmatic generator. Golds are set by what a human reader would say and are
INDEPENDENT of the mechanism (the cell also reports any passage where the mechanism disagrees with
the hand gold -- a disagreement would be a finding, not a pass).

Covers the discriminating structures on natural prose: past-T multi-change, re-observe
(stale-then-corrected), deception (false testimony), true testimony, and two-agent divergence.
Same scoring as the construction cell: belief-question accuracy of the timeline vs the timeline-
agnostic current-belief floor, with the info-free order-shuffle twin losing.
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
    WorldEvent, Scenario, SubstrateReadout, make_answerer,
    timeline_belief, current_belief_floor, reality_at,
)

OUTDIR = os.path.join(_REPO, "data", "exp_belief_timeline_authored_v1")


# Each passage: prose (for the record), the world events (chrono/narr/observed hand-encoded from the
# text), a location vocabulary, and belief queries with HAND-SET golds (t is the story-time the
# question asks about). Golds reflect a human reader's judgement, independent of the mechanism.
PASSAGES = [
    {
        "sid": "a_multi_desk",
        "text": ("Nora set her glasses on the desk. Later she carried them to the kitchen. "
                 "Later still she took them out to the porch. Where did Nora think her glasses "
                 "were WHILE they sat in the kitchen?"),
        "agent": "Nora", "obj": "glasses",
        "events": [("desk", 0, 0, True), ("kitchen", 1, 1, True), ("porch", 2, 2, True)],
        "vocab": ["desk", "kitchen", "porch", "shed", "car"],
        "queries": [{"t": 1.5, "type": "belief", "gold": "kitchen"},   # past-T, not the final porch
                    {"t": 0.5, "type": "belief", "gold": "desk"},
                    {"t": 2.5, "type": "belief", "gold": "porch"}],
    },
    {
        "sid": "a_reobs_wallet",
        "text": ("Sam left his wallet on the hall table and went to shower. While he showered his "
                 "sister moved it to the drawer. He did not hear her. He came out and, seeing it "
                 "gone, found it in the drawer. Between the move and his finding it, where did Sam "
                 "think the wallet was?"),
        "agent": "Sam", "obj": "wallet",
        "events": [("table", 0, 0, True), ("drawer", 1, 1, False), ("drawer", 2, 2, True)],
        "vocab": ["table", "drawer", "shelf", "bag"],
        "queries": [{"t": 1.5, "type": "belief", "gold": "table"},     # stale before he finds it
                    {"t": 1.5, "type": "false_belief", "gold": True},
                    {"t": 2.5, "type": "belief", "gold": "drawer"},     # corrected after
                    {"t": 2.5, "type": "false_belief", "gold": False}],
    },
    {
        "sid": "a_deceive_ring",
        "text": ("Mia saw the ring in the jewelry box. Her cousin, to trick her, told her it had "
                 "been moved to the safe, though it had not. After hearing this, where did Mia "
                 "think the ring was, and where was it really?"),
        "agent": "Mia", "obj": "ring",
        "events": [("box", 0, 0, True), ("safe", 1, 1, True)],   # 2nd is testimony (a lie)
        "testimony_idx": [1],
        "vocab": ["box", "safe", "drawer", "pocket"],
        "queries": [{"t": 1.5, "type": "belief", "gold": "safe"},       # believes the lie
                    {"t": 1.5, "type": "reality", "gold": "box"},        # the lie did not move it
                    {"t": 0.5, "type": "belief", "gold": "box"}],
    },
    {
        "sid": "a_informed_keys",
        "text": ("Theo hung the keys by the door and left for work. His flatmate moved them to the "
                 "bowl while he was out; Theo did not see. That evening the flatmate phoned and told "
                 "him truthfully they were in the bowl. Before the call, where did Theo think the "
                 "keys were? After it?"),
        "agent": "Theo", "obj": "keys",
        "events": [("hook", 0, 0, True), ("bowl", 1, 1, False), ("bowl", 2, 2, True)],  # 3rd = told
        "testimony_idx": [2],
        "vocab": ["hook", "bowl", "drawer", "pocket"],
        "queries": [{"t": 1.5, "type": "belief", "gold": "hook"},       # stale before the call
                    {"t": 2.5, "type": "belief", "gold": "bowl"},        # corrected by testimony
                    {"t": 2.5, "type": "false_belief", "gold": False}],
    },
    {
        "sid": "a_two_agent_book",
        "text": ("Both Ada and Ben saw the book on the coffee table. Ben went out. Ada then shelved "
                 "the book; Ben was not there. While Ben was away, did Ada and Ben think the book was "
                 "in the same place?"),
        "agents": ["Ada", "Ben"], "obj": "book",
        "events": [("table", 0, 0, {"Ada": True, "Ben": True}),
                   ("shelf", 1, 1, {"Ada": True, "Ben": False})],
        "vocab": ["table", "shelf", "box", "desk"],
        "queries": [{"t": 1.5, "type": "belief", "agent": "Ada", "gold": "shelf"},
                    {"t": 1.5, "type": "belief", "agent": "Ben", "gold": "table"},   # stale
                    {"t": 0.5, "type": "belief", "agent": "Ben", "gold": "table"}],
    },
    {
        "sid": "a_past_letter",
        "text": ("Grandpa tucked the letter into the Bible. Months later he moved it to the trunk. "
                 "At the time it lay in the Bible, where did he believe it was?"),
        "agent": "Grandpa", "obj": "letter",
        "events": [("bible", 0, 0, True), ("trunk", 1, 1, True)],
        "vocab": ["bible", "trunk", "drawer", "box"],
        "queries": [{"t": 0.5, "type": "belief", "gold": "bible"},
                    {"t": 1.5, "type": "belief", "gold": "trunk"}],
    },
    {
        "sid": "a_reobs_phone",
        "text": ("Lena put her phone on the couch and stepped into the garden. Her brother slipped "
                 "it under a cushion while she was outside. She did not notice. When she came back she "
                 "spotted it under the cushion. While she was in the garden, where did Lena think her "
                 "phone was?"),
        "agent": "Lena", "obj": "phone",
        "events": [("couch", 0, 0, True), ("cushion", 1, 1, False), ("cushion", 2, 2, True)],
        "vocab": ["couch", "cushion", "table", "bag"],
        "queries": [{"t": 1.5, "type": "belief", "gold": "couch"},
                    {"t": 1.5, "type": "false_belief", "gold": True},
                    {"t": 2.5, "type": "belief", "gold": "cushion"}],
    },
    {
        "sid": "a_multi_toy",
        "text": ("The toy started in the crib. The nanny moved it to the playpen, then to the shelf, "
                 "with the child watching each time. When it was in the playpen, where did the child "
                 "think it was?"),
        "agent": "child", "obj": "toy",
        "events": [("crib", 0, 0, True), ("playpen", 1, 1, True), ("shelf", 2, 2, True)],
        "vocab": ["crib", "playpen", "shelf", "box"],
        "queries": [{"t": 1.5, "type": "belief", "gold": "playpen"},
                    {"t": 0.5, "type": "belief", "gold": "crib"},
                    {"t": 2.5, "type": "belief", "gold": "shelf"}],
    },
]


def _to_scenario(p):
    events, observed = [], {}
    tsty = set(p.get("testimony_idx", []))
    agents = p.get("agents", [p.get("agent")])
    for i, ev in enumerate(p["events"]):
        val, chrono, narr, obs = ev
        affects = i not in tsty
        events.append(WorldEvent(p["obj"], val, chrono=chrono, narr=narr,
                                 kind=("testimony" if i in tsty else ("initial" if i == 0 else "move")),
                                 affects_reality=affects))
        if isinstance(obs, dict):
            for ag, bit in obs.items():
                observed[(ag, chrono)] = bit
        else:
            for ag in agents:
                observed[(ag, chrono)] = obs
    queries = []
    for q in p["queries"]:
        queries.append({"agent": q.get("agent", p.get("agent", agents[0])), "obj": p["obj"],
                        "t": q["t"], "type": q["type"], "gold": q["gold"]})
    return Scenario(p["sid"], agents, events, observed, queries, text=p["text"]), p["vocab"]


def _score_arm(arm, scen, vocab, readout, seed=0):
    ans = make_answerer(arm, scen, vocab, readout, seed=seed)
    ok = []
    for q in scen.queries:
        typ = q["type"]
        if typ == "belief":
            pred = ans(q["agent"], q["obj"], q["t"]); ok.append(int(pred == q["gold"]))
        elif typ == "false_belief":
            bel = ans(q["agent"], q["obj"], q["t"])
            rea = readout.readout(q["obj"], reality_at(scen.events, q["obj"], q["t"]), vocab)
            ok.append(int(bool(bel is not None and bel != rea) == q["gold"]))
        elif typ == "reality":
            pred = readout.readout(q["obj"], reality_at(scen.events, q["obj"], q["t"]), vocab)
            ok.append(int(pred == q["gold"]))
    return ok


def _boot_ci(v, n_boot=2000, seed=0):
    v = np.asarray(v, float)
    rng = np.random.default_rng(seed)
    means = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(n_boot)]
    return float(v.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def run(seed=20260830, d=1024, twin_seeds=300):
    readout = SubstrateReadout(d=d, seed=seed)
    scens = [_to_scenario(p) for p in PASSAGES]

    # non-circularity: does the mechanism ever DISAGREE with a hand gold? (report it)
    mism = []
    for scen, vocab in scens:
        for q in scen.queries:
            if q["type"] == "belief":
                mech = timeline_belief(scen.events, scen.observed, q["agent"], q["obj"], q["t"])
                if mech != q["gold"]:
                    mism.append({"sid": scen.sid, "q": q, "mech": mech})

    tl, fl = [], []
    for scen, vocab in scens:
        tl += _score_arm("timeline", scen, vocab, readout, seed=seed)
        fl += _score_arm("current_belief", scen, vocab, readout, seed=seed)
    tl_m, tl_lo, tl_hi = _boot_ci(tl, seed=seed)
    fl_m, fl_lo, fl_hi = _boot_ci(fl, seed=seed)

    twin_accs = []
    for ts in range(twin_seeds):
        vv = []
        for scen, vocab in scens:
            vv += _score_arm("twin", scen, vocab, readout, seed=ts)
        twin_accs.append(float(np.mean(vv)))
    twin_p95 = float(np.percentile(twin_accs, 95))

    metrics = {
        "seed": seed, "n_passages": len(scens), "n_queries": len(tl),
        "timeline": {"acc": tl_m, "ci": [tl_lo, tl_hi]},
        "current_belief_floor": {"acc": fl_m, "ci": [fl_lo, fl_hi]},
        "twin": {"p95": twin_p95, "mean": float(np.mean(twin_accs))},
        "mechanism_vs_handgold_mismatches": mism,
        "verdict": {"ci_separated": tl_lo > fl_hi, "beats_twin": tl_lo > twin_p95,
                    "mechanism_matches_handgold": len(mism) == 0},
    }
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run(twin_seeds=(40 if args.self_test else 300))
    if args.self_test:
        assert m["verdict"]["ci_separated"] and m["verdict"]["mechanism_matches_handgold"], m["verdict"]
        print("self-test PASS", json.dumps(m["verdict"]))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 78)
    print("SECOND GOLD -- hand-authored real-English belief-timeline passages")
    print("=" * 78)
    print(f"{m['n_passages']} passages, {m['n_queries']} belief-questions (HAND golds)")
    print(f"  TIMELINE     {m['timeline']['acc']:.3f}  CI {m['timeline']['ci']}")
    print(f"  FLOOR        {m['current_belief_floor']['acc']:.3f}  CI {m['current_belief_floor']['ci']}")
    print(f"  TWIN p95     {m['twin']['p95']:.3f}")
    print(f"  mechanism vs hand-gold mismatches: {len(m['mechanism_vs_handgold_mismatches'])} "
          f"(0 = the mechanism reproduces human judgement independently)")
    print(f"  CI-SEPARATED {m['verdict']['ci_separated']}  BEATS TWIN {m['verdict']['beats_twin']}")
    print(f"written {OUTDIR}/metrics.json")


if __name__ == "__main__":
    main()
