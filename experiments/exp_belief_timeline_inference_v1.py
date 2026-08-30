"""INFERRED belief-update edge -- an agent believes a conclusion it REASONED to from observed
premises (the last un-built update route; research drill 2026-08-30). Brain-PINNED: inference is a
dissociable knowledge source (Sodian & Wimmer 1987), attributed ~2 years after perception; it must be
strictly EVIDENCE-GATED (credit only inferences the agent could make from what IT observed -- the
inference analog of observation-gating / anti-curse-of-knowledge).

Closed schema set (brain-plausible; the general derivation engine is a SEPARATE next problem):
  exclusion  -- Sodian & Wimmer's canonical schema: object is in {A,B}; agent sees A is empty ->
                infers B (without seeing it there).
  transitive -- object in container C; C is at place P -> infers object at P.
Inference-based DECEPTION: true-but-misleading premises -> the agent validly infers a FALSE conclusion
(unrepresentable with the assertion-only deception route; Sperber Epistemic Vigilance).

Arms (belief decoded on the belief_partition FHRR organs):
  timeline (gated)   -- infer ONLY if the agent observed ALL premises  [the mechanism]
  never_infer FLOOR  -- observation/testimony only, never infer         [UNDER-attributes]
  omniscient FLOOR   -- infer regardless of the agent's evidence        [OVER-attributes: the key control]
  twin               -- info-free: shuffle which premises the agent observed (gating misfires)
Gate: the gated timeline CI-separated over BOTH floors (each fails a different half); twin LOSES.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

from experiments.belief_timeline import (
    WorldEvent, InferenceEdge, SubstrateReadout, fired_inference_events,
    timeline_belief, reality_at,
)

OUTDIR = os.path.join(_REPO, "data", "exp_belief_timeline_inference_v1")
LOCS = ["red_box", "blue_box", "green_box", "jar", "shelf", "pocket", "drawer", "crate", "chest"]


def _mk_exclusion(rng, sid, partial=False, deception=False):
    """object in {A,B}; agent knows the disjunction (c1) and sees A empty (c2) -> infers B (fire 2.5).
    partial: agent misses the disjunction -> cannot infer. deception: object really in C (misleading
    disjunction) -> agent validly infers B but B is false."""
    a = "Agent"
    A, B, C = rng.sample(LOCS, 3)
    real = C if deception else B
    events = [WorldEvent("obj", real, chrono=0.0, narr=0, kind="initial", affects_reality=True)]  # hidden truth
    # premise events (abstract; observed or not by the agent). They do not move the world.
    events += [WorldEvent("premise_disj", A + "|" + B, chrono=1.0, narr=1, kind="premise", affects_reality=False),
               WorldEvent("premise_empty", A, chrono=2.0, narr=2, kind="premise", affects_reality=False)]
    observed = {(a, 0.0): False,                      # agent never sees the object directly
                (a, 1.0): (not partial), (a, 2.0): True}
    edge = InferenceEdge(obj="obj", conclusion=B, premise_chronos=(1.0, 2.0), fire_chrono=2.5,
                         schema="exclusion")
    tags = ["exclusion"] + (["partial"] if partial else []) + (["deception"] if deception else [])
    return {"sid": sid, "agent": a, "events": events, "observed": observed, "edges": [edge],
            "vocab": [A, B, C] + [l for l in LOCS if l not in (A, B, C)][:2], "tags": tags,
            "query_t": 3.0, "partial": partial, "deception": deception, "concl": B, "real": real}


def _mk_transitive(rng, sid, partial=False):
    """object in container C (c1, agent sees); C at place P (c2, agent sees) -> infers object at P."""
    a = "Agent"
    C, P, X = rng.sample(LOCS, 3)
    events = [WorldEvent("obj", P, chrono=0.0, narr=0, kind="initial", affects_reality=True),  # truth: at P
              WorldEvent("premise_in", C, chrono=1.0, narr=1, kind="premise", affects_reality=False),
              WorldEvent("premise_at", P, chrono=2.0, narr=2, kind="premise", affects_reality=False)]
    observed = {(a, 0.0): False, (a, 1.0): True, (a, 2.0): (not partial)}
    edge = InferenceEdge(obj="obj", conclusion=P, premise_chronos=(1.0, 2.0), fire_chrono=2.5,
                         schema="transitive")
    tags = ["transitive"] + (["partial"] if partial else [])
    return {"sid": sid, "agent": a, "events": events, "observed": observed, "edges": [edge],
            "vocab": [C, P, X] + [l for l in LOCS if l not in (C, P, X)][:2], "tags": tags,
            "query_t": 3.0, "partial": partial, "deception": False, "concl": P, "real": P}


def _gold(sc):
    """Human-reader gold: the agent believes the inferred conclusion iff it observed all premises
    (evidence-gated). partial -> no inference (None). The gated timeline IS this by construction."""
    if sc["partial"]:
        return None
    return sc["concl"]


def _answer(mode, sc, readout, twin_seed=None):
    events, observed = list(sc["events"]), dict(sc["observed"])
    if mode == "twin":
        # info-free: shuffle which premise-observations the agent has (destroys evidence gating)
        r = random.Random(twin_seed)
        keys = [k for k in observed if k[0] == sc["agent"]]
        vals = [observed[k] for k in keys]
        r.shuffle(vals)
        for k, v in zip(keys, vals):
            observed[k] = v
        inf_ev, inf_obs = fired_inference_events(sc["agent"], sc["edges"], observed, mode="gated")
    else:
        fire_mode = {"timeline": "gated", "never_infer": "never", "omniscient": "omniscient"}[mode]
        inf_ev, inf_obs = fired_inference_events(sc["agent"], sc["edges"], observed, mode=fire_mode)
    events += inf_ev
    observed.update(inf_obs)
    val = timeline_belief(events, observed, sc["agent"], "obj", sc["query_t"])
    return readout.readout("obj", val, sc["vocab"])


def generate(n=60, seed=20260830):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        r = i % 5
        if r == 0:
            out.append(_mk_exclusion(rng, f"excl_{i}"))
        elif r == 1:
            out.append(_mk_exclusion(rng, f"excl_partial_{i}", partial=True))
        elif r == 2:
            out.append(_mk_transitive(rng, f"trans_{i}"))
        elif r == 3:
            out.append(_mk_transitive(rng, f"trans_partial_{i}", partial=True))
        else:
            out.append(_mk_exclusion(rng, f"excl_deceive_{i}", deception=True))
    return out


def _boot_ci(v, n_boot=2000, seed=0):
    v = np.asarray(v, float)
    rng = np.random.default_rng(seed)
    means = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(n_boot)]
    return float(v.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def run(n=60, seed=20260830, d=1024, twin_seeds=200):
    scens = generate(n=n, seed=seed)
    ro = SubstrateReadout(d=d, seed=seed)

    arms = {"timeline": [], "never_infer": [], "omniscient": []}
    # per-arm belief correctness, and a deception-gap sub-metric
    dec_ok = 0
    dec_n = 0
    for sc in scens:
        gold = _gold(sc)
        gold_dec = readout_gold = None
        for arm in arms:
            pred = _answer(arm, sc, ro)
            gold_sym = ro.readout("obj", gold, sc["vocab"]) if gold is not None else None
            arms[arm].append(int(pred == gold_sym))
        # inference-based deception: the agent holds a FALSE inferred belief (concl != reality)
        if sc["deception"]:
            bel = _answer("timeline", sc, ro)
            rea = ro.readout("obj", reality_at(sc["events"], "obj", sc["query_t"]), sc["vocab"])
            dec_n += 1
            dec_ok += int(bel is not None and bel != rea)   # a false belief exists by inference

    res = {arm: {"acc": _boot_ci(v, seed=seed)[0], "ci": list(_boot_ci(v, seed=seed)[1:])}
           for arm, v in arms.items()}

    # per-condition breakdown (shows each floor fails a DIFFERENT half)
    def cond_acc(arm, tag_pred):
        v = []
        for i, sc in enumerate(scens):
            if not tag_pred(sc):
                continue
            v.append(arms[arm][i])
        return (float(np.mean(v)) if v else None, len(v))
    full = lambda sc: not sc["partial"]
    partial = lambda sc: sc["partial"]
    breakdown = {arm: {"all_premises": cond_acc(arm, full), "partial_premise": cond_acc(arm, partial)}
                 for arm in arms}

    twin_accs = []
    for ts in range(twin_seeds):
        v = []
        for sc in scens:
            gold = _gold(sc)
            gold_sym = ro.readout("obj", gold, sc["vocab"]) if gold is not None else None
            v.append(int(_answer("twin", sc, ro, twin_seed=ts * 131 + hash(sc["sid"]) % 997) == gold_sym))
        twin_accs.append(float(np.mean(v)))
    twin_p95 = float(np.percentile(twin_accs, 95))

    metrics = {
        "seed": seed, "n": len(scens),
        "arms": res, "breakdown": breakdown,
        "twin": {"p95": twin_p95, "mean": float(np.mean(twin_accs))},
        "inference_deception": {"false_belief_by_inference": (dec_ok / dec_n if dec_n else None), "n": dec_n},
        "verdict": {
            "beats_never_infer": res["timeline"]["ci"][0] > res["never_infer"]["ci"][1],
            "beats_omniscient": res["timeline"]["ci"][0] > res["omniscient"]["ci"][1],
            "beats_twin": res["timeline"]["ci"][0] > twin_p95,
        },
    }
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run(n=(20 if args.self_test else 60), twin_seeds=(40 if args.self_test else 200))
    if args.self_test:
        v = m["verdict"]
        assert v["beats_never_infer"] and v["beats_omniscient"] and v["beats_twin"], v
        print("self-test PASS", json.dumps(v))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 78)
    print("INFERRED belief edge (evidence-gated inference; Sodian & Wimmer partial-premise controls)")
    print("=" * 78)
    a = m["arms"]
    print(f"  TIMELINE (gated)     {a['timeline']['acc']:.3f}  CI {a['timeline']['ci']}")
    print(f"  never-infer FLOOR    {a['never_infer']['acc']:.3f}  CI {a['never_infer']['ci']}  (under-attributes)")
    print(f"  omniscient FLOOR     {a['omniscient']['acc']:.3f}  CI {a['omniscient']['ci']}  (over-attributes)")
    print(f"  info-free TWIN p95   {m['twin']['p95']:.3f}")
    print("  breakdown (each floor fails a DIFFERENT half):")
    for arm in a:
        b = m["breakdown"][arm]
        print(f"    {arm:14s} all-premises {b['all_premises'][0]} (n={b['all_premises'][1]})  "
              f"partial {b['partial_premise'][0]} (n={b['partial_premise'][1]})")
    di = m["inference_deception"]
    print(f"  inference-based deception: false belief by inference in {di['false_belief_by_inference']} "
          f"of n={di['n']} cases")
    print(f"  verdict: {json.dumps(m['verdict'])}")
    print(f"written {OUTDIR}/metrics.json")


if __name__ == "__main__":
    main()
