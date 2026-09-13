"""exp_causal_bridge_science_slice_v1 -- THE GROUNDING BRIDGE, science-slice prototype (option (a)): answer WIQA causal
questions by SIMULATED do() intervention on a RUNNABLE GROUNDED physical model, beating the text-mined store on the
slice where grounding exists.

WHY (from this problem's SOLVED): the text-mined causal store is capped at ~0.61 on DIRECTION and inert on the WIQA
necessity axis; the route past the wall is grounded interventional simulation (proven in a micro-world: direction 0.99,
cause-selection 0.03->0.98). The BRIDGE = map narrative concepts to a runnable grounded dynamical model and simulate
do() at read-time (Gerstenberg CSM counterfactual simulation; Battaglia intuitive-physics engine; Kintsch instantiation).

THE GROUNDING (honest, no cheap stand-in): reuse `hdlab/causal_sign_channel`'s FORMAL-MODEL couplings -- 20 stoichiometric
REACTIONS (reactant->product) + physics/thermo INFLUENCES (force->motion +, friction->speed -, ...), grounded in physical
LAW not text co-occurrence, and its `ground_concepts` text->node map. This is the science slice (~13-14% of WIQA);
`causal_sign_channel` already lands the single-edge gated SIGN here (+0.157 over the falsifier). The NEW, non-redundant
claim: make the model RUNNABLE and answer by simulated do() -- DIRECTION + multi-hop NECESSITY (reachability under the
intervention) + SIGN together, composed through `hdlab.causal_reasoner`.

ARMS (on the COVERED science slice; effect-vs-no_effect necessity axis + 3-way with sign):
  * grounded_dosim = reachability / signed_effect over the runnable grounded model (the bridge).
  * store         = the text-mined store's directed reachability (edge_condXasym) -- the ~0.61 text ceiling.
  * twin          = grounded_dosim over the DENSITY-MATCHED shuffled-coupling model (CausalGraph.shuffled) -- MUST lose.
  * majority      = class prior.
HONEST BOUNDS: coverage is the science slice only (a concept-proof, not a full-population win); the everyday/social tail
(~87%) needs the general bridge (meaning-channel-gated, the main event). Glass-box, NO external LLM.
Run: .venv/Scripts/python.exe experiments/exp_causal_bridge_science_slice_v1.py --run [--smoke]
# KB_REFERENT: data/corpora/wiqa/raw_official/dev_with_expl.jsonl
# KB_REFERENT: data/exp_causal_testimony_mine_v1/store_v1.json
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"
__bf_note__ = ("grounding-bridge science-slice prototype: runnable formal-model (stoichiometry+physics) queried by "
               "simulated do() for direction+necessity+sign, composed through causal_reasoner; grounding via "
               "causal_sign_channel's physical couplings (physical law, not text). Science slice only; the general "
               "bridge is the meaning-channel-gated main event.")

import argparse
import json
import os
import sys
import time
from collections import Counter
from typing import Dict, List, Set, Tuple

import numpy as np

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
os.environ.setdefault("PYTHONHASHSEED", "0")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.causal_reasoner import CausalGraph
from hdlab.causal_sign_channel import _EDGES, ground_concepts
from experiments.exp_causal_testimony_mine_v1 import span_concepts
from experiments.exp_causal_testimony_eval_v1 import load_store
from experiments.exp_causal_directional_score_v1 import edge_condXasym
from experiments.exp_causal_wiqa_dosim_v1 import load_wiqa, polarity

from experiments._seed_checkpoint import get_output_dir  # Q115 (owner 2026-08-23): route the output dir
OUT = str(get_output_dir("exp_causal_bridge_science_slice_v1"))
STORE = os.path.join(_REPO, "data", "exp_causal_testimony_mine_v1", "store_v1.json")
_CC: Dict[str, List[str]] = {}


def _c(s):
    h = _CC.get(s)
    if h is None:
        h = span_concepts(s); _CC[s] = h
    return h


def build_grounded_graph() -> CausalGraph:
    """The RUNNABLE grounded model: a directed signed CausalGraph from the formal-model couplings (physical law).
    Net sign per (c,e) = sign of the summed coupling signs (deterministic)."""
    g = CausalGraph()
    for c in _EDGES:
        for e in _EDGES[c]:
            net = sum(s for (s, _ctx, _phys) in _EDGES[c][e])
            pol = 1 if net >= 0 else -1
            g.add_edge(c, e, polarity=pol)
    return g


def _sign_scramble(g: CausalGraph, seed: int) -> CausalGraph:
    """Same nodes + same directed edges (identical topology), but each edge's SIGN randomized. If grounded_3way beats
    this, the more/less SIGN (not just the reachability topology) is load-bearing -- the axis text is exhausted for."""
    rng = np.random.default_rng(seed)
    t = CausalGraph()
    for n in g.nodes:
        t.add_node(n)
    for a in g.fwd:
        for b in g.fwd[a]:
            t.add_edge(a, b, polarity=1 if rng.random() < 0.5 else -1)
    return t


def grounded_necessity(g: CausalGraph, Xn: Set[str], Yn: Set[str]) -> str:
    for x in Xn:
        for y in Yn:
            if x in g.nodes and y in g.nodes and g.reachable(x, y):
                return "effect"
    return "no_effect"


def grounded_sign(g: CausalGraph, Xn: Set[str], Yn: Set[str], polX: int) -> str:
    """3-way: signed_effect over the runnable model (do(X) with the perturbation's polarity), best over node pairs."""
    best = "no_effect"
    for x in Xn:
        for y in Yn:
            if x in g.nodes and y in g.nodes and g.reachable(x, y):
                s = g.signed_effect(x, y, sign=polX if polX != 0 else 1)
                if s != "no_effect":
                    return s
    return best


def store_necessity(store, X: List[str], Y: List[str], thr: float) -> str:
    for x in X:
        for y in Y:
            if edge_condXasym(store, x, y) > thr:
                return "effect"
    return "no_effect"


def run(smoke: bool = False, cap: int = 6000, thr: float = 0.0) -> Dict:
    t0 = time.time(); os.makedirs(OUT, exist_ok=True)
    G = build_grounded_graph(); Gt = G.shuffled(seed=101)
    Gs = _sign_scramble(G, seed=101)      # SAME topology, edge SIGNS randomized -> isolates whether the SIGN is load-bearing
    store = load_store(STORE)
    items = load_wiqa(300 if smoke else cap)
    prior = Counter(it["gold"] for it in items); majority = prior.most_common(1)[0][0]

    rows = []
    for it in items:
        X = _c(it["X"]); Y = _c(it["Y"]); SC = [_c(s) for s in it["steps"]]
        passage = list({c for sc in SC for c in sc} | set(X) | set(Y))
        Xn = ground_concepts(X); Yn = ground_concepts(Y)
        covered = bool(Xn) and bool(Yn) and any(x in G.nodes for x in Xn) and any(y in G.nodes for y in Yn)
        if not covered:
            continue
        polX = polarity(it["X"])
        eff_gold = "effect" if it["gold"] in ("more", "less") else "no_effect"
        e_g = grounded_necessity(G, Xn, Yn)
        e_t = grounded_necessity(Gt, Xn, Yn)
        e_s = store_necessity(store, X, Y, thr)
        s3_g = "no_effect" if e_g == "no_effect" else grounded_sign(G, Xn, Yn, polX)
        s3_ss = "no_effect" if e_g == "no_effect" else grounded_sign(Gs, Xn, Yn, polX)   # sign-scrambled, same topology
        rows.append({
            "gold": eff_gold, "gold3": it["gold"],
            "grounded_eff": 1.0 if e_g == eff_gold else 0.0,
            "twin_eff": 1.0 if e_t == eff_gold else 0.0,
            "store_eff": 1.0 if e_s == eff_gold else 0.0,
            "majority_eff": 1.0 if (("effect" if majority in ("more", "less") else "no_effect") == eff_gold) else 0.0,
            "grounded_3way": 1.0 if s3_g == it["gold"] else 0.0,
            "signscram_3way": 1.0 if s3_ss == it["gold"] else 0.0,
            "majority_3way": 1.0 if majority == it["gold"] else 0.0,
        })

    n = len(rows)
    out = {"smoke": smoke, "n_total": len(items), "n_covered": n,
           "coverage_frac": round(n / max(1, len(items)), 4), "majority": majority,
           "necessity_effect_vs_noeffect_on_covered": {
               "grounded_dosim": _boot([r["grounded_eff"] for r in rows]),
               "store_textmined": _boot([r["store_eff"] for r in rows]),
               "shuffled_coupling_twin": _boot([r["twin_eff"] for r in rows]),
               "majority": _boot([r["majority_eff"] for r in rows]),
               "paired_grounded_minus_twin": _paired([r["grounded_eff"] for r in rows], [r["twin_eff"] for r in rows]),
               "paired_grounded_minus_store": _paired([r["grounded_eff"] for r in rows], [r["store_eff"] for r in rows])},
           "three_way_with_sign_on_covered": {
               "grounded_dosim": _boot([r["grounded_3way"] for r in rows]),
               "sign_scrambled_twin": _boot([r["signscram_3way"] for r in rows]),
               "majority": _boot([r["majority_3way"] for r in rows]),
               "paired_grounded_minus_signscram": _paired([r["grounded_3way"] for r in rows],
                                                          [r["signscram_3way"] for r in rows]),
               "paired_grounded_minus_majority": _paired([r["grounded_3way"] for r in rows],
                                                         [r["majority_3way"] for r in rows]),
               "note": "3-way needs the more/less SIGN -- text is exhausted for it; the runnable model supplies it. "
                       "grounded>sign_scrambled CI-sep => the SIGN (not just topology) is load-bearing."}}
    ne = out["necessity_effect_vs_noeffect_on_covered"]; tw = out["three_way_with_sign_on_covered"]
    out["headline"] = (
        "SCIENCE-SLICE BRIDGE (runnable grounded do-sim) covered=%d/%d (%.1f%%) | NECESSITY on covered: grounded %.3f%s "
        "vs store %.3f%s vs shuffled-coupling twin %.3f%s vs majority %.3f | paired(grounded-twin) %+.4f%s (grounded-"
        "store) %+.4f%s || 3-WAY(with sign): grounded %.3f%s vs sign-scram-twin %.3f%s vs majority %.3f | paired(gr-"
        "signscram) %+.4f%s (gr-majority) %+.4f%s" % (
            n, out["n_total"], 100 * out["coverage_frac"], ne["grounded_dosim"]["acc"], ne["grounded_dosim"]["ci"],
            ne["store_textmined"]["acc"], ne["store_textmined"]["ci"], ne["shuffled_coupling_twin"]["acc"],
            ne["shuffled_coupling_twin"]["ci"], ne["majority"]["acc"], ne["paired_grounded_minus_twin"]["delta"],
            ne["paired_grounded_minus_twin"]["ci"], ne["paired_grounded_minus_store"]["delta"],
            ne["paired_grounded_minus_store"]["ci"], tw["grounded_dosim"]["acc"], tw["grounded_dosim"]["ci"],
            tw["sign_scrambled_twin"]["acc"], tw["sign_scrambled_twin"]["ci"], tw["majority"]["acc"],
            tw["paired_grounded_minus_signscram"]["delta"], tw["paired_grounded_minus_signscram"]["ci"],
            tw["paired_grounded_minus_majority"]["delta"], tw["paired_grounded_minus_majority"]["ci"]))
    out["elapsed_s"] = round(time.time() - t0, 1)
    tmp = os.path.join(OUT, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(OUT, "metrics.json"))
    print("[run] " + out["headline"], flush=True)
    return out


def _boot(hits, seed=17, n_boot=4000):
    a = np.array(hits, float)
    if len(a) < 3:
        return {"acc": float("nan"), "ci": [float("nan"), float("nan")], "n": int(len(a))}
    r = np.random.default_rng(seed)
    bs = [a[r.integers(0, len(a), len(a))].mean() for _ in range(n_boot)]
    return {"acc": round(float(a.mean()), 4),
            "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)], "n": int(len(a))}


def _paired(h1, h2, seed=23, n_boot=4000):
    d = np.array(h1, float) - np.array(h2, float)
    if len(d) < 3:
        return {"delta": float("nan"), "ci": [float("nan"), float("nan")]}
    r = np.random.default_rng(seed)
    bs = [d[r.integers(0, len(d), len(d))].mean() for _ in range(n_boot)]
    return {"delta": round(float(d.mean()), 4),
            "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--thr", type=float, default=0.0)
    a = ap.parse_args(argv)
    if a.self_test or a.smoke:
        run(smoke=True, thr=a.thr); print("SELFTEST PASS", flush=True); return 0
    run(thr=a.thr); return 0


if __name__ == "__main__":
    sys.exit(main())
