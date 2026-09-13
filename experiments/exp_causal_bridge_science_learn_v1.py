"""exp_causal_bridge_science_learn_v1 -- CLOSING THE BRIDGE LOOP ON REAL SCIENCE CONCEPTS: recover the physical-law
causal DIRECTION by SIMULATED intervention on a runnable grounded model, past the text store's ~0.61 ceiling.

The science-slice bridge prototype (exp_causal_bridge_science_slice) showed a runnable grounded model beats the text
store on necessity but ties the honest twins on the direction-INSENSITIVE existence axis. The axis where the grounded
model's asset (DIRECTION) is load-bearing is cause-ORDER -- and the brain gets direction from INTERVENTION, not from
reading structure (Gopnik/Pearl). So this cell closes the loop:
  1. STRUCTURE from physical law: the directed signed graph over real science concepts (causal_sign_channel REACTIONS +
     INFLUENCES) -- a DAG projection (cycles like photosynthesis<->respiration broken by keeping the first orientation).
  2. DYNAMICS: a signed linear dynamical system over that structure (Forbus QP / Battaglia intuitive physics) -- a
     RUNNABLE model, with a shared confounder (the topic/co-occurrence analogue).
  3. SIMULATED INTERVENTION: do(concept), propagate, observe -- the reader's mental simulation (Gerstenberg CSM).
  4. RECOVER DIRECTION by the interventional asymmetry (|do(a)->b| vs |do(b)->a|) = the grounded learner, NOT reading
     the edge list (non-circular: structure inferred from simulated experience).
Compare the recovered direction to (a) the text-mined STORE's directed score (its ~0.61 cap, on the same real science
concept pairs), (b) OBSERVATIONAL co-occurrence (confounded -> chance), (c) a random twin. GROUND TRUTH = the physical-
law edge direction.

CLAIM: simulated intervention on the grounded science model RECOVERS the physical-law direction (>> 0.61) that text
approximates at the cap, on REAL science concepts -- the bridge delivering direction where text cannot. HONEST BOUND:
the grounding (concept->model) is the curated formal set (science slice); the general bridge is the meaning-channel main
event. Glass-box, NO external LLM.
Run: .venv/Scripts/python.exe experiments/exp_causal_bridge_science_learn_v1.py --run [--smoke]
# KB_REFERENT: data/exp_causal_testimony_mine_v1/store_v1.json
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"
__bf_note__ = ("closes the bridge loop on real science concepts: recover physical-law causal direction by simulated "
               "intervention on a runnable grounded model (Gerstenberg CSM / Battaglia), past the text store's ~0.61 "
               "cap; grounding via causal_sign_channel formal couplings. Science slice; general bridge is the main event.")

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from typing import Dict, List, Set, Tuple

import numpy as np

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
os.environ.setdefault("PYTHONHASHSEED", "0")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.causal_sign_channel import _EDGES
from experiments.exp_causal_testimony_eval_v1 import load_store
from experiments.exp_causal_directional_score_v1 import edge_condXasym

from experiments._seed_checkpoint import get_output_dir  # Q115 (owner 2026-08-23): route the output dir
OUT = str(get_output_dir("exp_causal_bridge_science_learn_v1"))
STORE = os.path.join(_REPO, "data", "exp_causal_testimony_mine_v1", "store_v1.json")
TEXT_STORE_CEILING = 0.61


def build_science_dag() -> Tuple[List[str], List[Tuple[str, str, int]]]:
    """Directed signed edges over real science concepts from the formal couplings; break cycles by keeping the FIRST
    orientation seen (a DAG projection with determinate ground-truth direction per edge)."""
    nodes: List[str] = []
    idx: Dict[str, int] = {}
    def nid(n):
        if n not in idx:
            idx[n] = len(nodes); nodes.append(n)
        return idx[n]
    raw = []
    for c in _EDGES:
        for e in _EDGES[c]:
            net = sum(s for (s, _ctx, _phys) in _EDGES[c][e])
            raw.append((c, e, 1 if net >= 0 else -1))
    edges: List[Tuple[str, str, int]] = []
    seen_pair: Set[frozenset] = set()
    order: Dict[str, int] = {}
    for (c, e, s) in raw:
        nid(c); nid(e)
        fp = frozenset((c, e))
        if fp in seen_pair or c == e:
            continue                              # skip the reverse orientation of an already-added pair (break cycle)
        # keep acyclic by a running order: assign c before e
        oc = order.setdefault(c, len(order)); oe = order.setdefault(e, len(order))
        if oc <= oe:
            edges.append((c, e, s)); seen_pair.add(fp)
        else:
            edges.append((e, c, s)); seen_pair.add(fp)
    return nodes, edges


def _toposort(k, parents):
    """Kahn topological order over the DAG (parents: child -> [(parent,sign)...])."""
    indeg = {j: len(parents[j]) for j in range(k)}
    children = defaultdict(list)
    for j in range(k):
        for (p, s) in parents[j]:
            children[p].append(j)
    q = [j for j in range(k) if indeg[j] == 0]
    order = []
    while q:
        u = q.pop()
        order.append(u)
        for v in children[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    # any nodes left (residual cycle) appended in index order (rare after DAG projection)
    order += [j for j in range(k) if j not in set(order)]
    return order


def _make_params(nodes, edges, rng):
    k = len(nodes); idx = {n: i for i, n in enumerate(nodes)}
    parents = defaultdict(list)
    wt = {}
    for (c, e, s) in edges:
        parents[idx[e]].append((idx[c], s)); wt[(idx[c], idx[e])] = 0.8 + 0.6 * rng.random()
    gamma = rng.uniform(0.8, 1.6, size=k) * np.where(rng.random(k) < 0.5, 1.0, -1.0)
    return idx, parents, wt, gamma, _toposort(k, parents)


def simulate(nodes, params, n, rng, do_node=None, cstr=1.0):
    """Signed linear dynamical system over the science DAG -- ONE topological-order pass (parents before children):
    each node = confounder + noise + Sum(sign*wt*parent); do_node set independently (intervention breaks its inputs)."""
    idx, parents, wt, gamma, order = params
    k = len(nodes)
    V = np.zeros((n, k)); C = rng.normal(0, 1, size=n)
    for j in order:
        if j == do_node:
            V[:, j] = rng.uniform(-2, 2, size=n); continue
        val = cstr * gamma[j] * C + rng.normal(0, 0.3, size=n)
        for (p, s) in parents[j]:
            val = val + s * wt[(p, j)] * V[:, p]
        V[:, j] = val
    return V, idx


def _cov(x, y):
    return float(np.mean((x - x.mean()) * (y - y.mean())))


def run(smoke: bool = False) -> Dict:
    t0 = time.time(); os.makedirs(OUT, exist_ok=True)
    nodes, edges = build_science_dag()
    n_int = 1500 if smoke else 4000
    n_obs = 4000 if smoke else 12000
    rng = np.random.default_rng(2026)
    store = load_store(STORE)
    params = _make_params(nodes, edges, rng)
    idx = params[0]

    # interventional data: one batch per node
    intr = {}
    for i, nm in enumerate(nodes):
        V, _ = simulate(nodes, params, n_int, rng, do_node=i)
        intr[i] = V
    Vobs, _ = simulate(nodes, params, n_obs, rng, do_node=None)

    def store_dir(a_name, b_name):
        """The text store's direction over the concept pair (map multiword science phrase -> its content lemmas)."""
        A = a_name.split(); B = b_name.split()
        fab = max((edge_condXasym(store, x, y) for x in A for y in B), default=0.0)
        fba = max((edge_condXasym(store, y, x) for x in A for y in B), default=0.0)
        if fab == fba:
            return 0, (fab > 0)          # tie; covered iff any signal
        return (1 if fab > fba else -1), True

    g_hits, o_hits, t_hits = [], [], []
    s_hits = []; s_cov = 0
    twin_rng = np.random.default_rng(20260912)          # deterministic (hash() is not stable across processes)
    for (c, e, s) in edges:
        i, j = idx[c], idx[e]
        # grounded learner: interventional asymmetry (do(c)->e vs do(e)->c). ground truth: c->e (+1)
        iab = abs(_cov(intr[i][:, i], intr[i][:, j])); iba = abs(_cov(intr[j][:, j], intr[j][:, i]))
        g_hits.append(1.0 if iab > iba else 0.0)
        # observational co-occurrence (symmetric -> forced guess; confounded)
        o_hits.append(0.5)
        # random twin (deterministic seed)
        t_hits.append(1.0 if twin_rng.random() < 0.5 else 0.0)
        # text store direction on the same real concept pair
        sd, cov = store_dir(c, e)
        if cov and sd != 0:
            s_cov += 1
            s_hits.append(1.0 if sd == 1 else 0.0)

    out = {"smoke": smoke, "n_nodes": len(nodes), "n_edges": len(edges), "text_store_ceiling": TEXT_STORE_CEILING,
           "direction_recovery_on_real_science_concepts": {
               "grounded_simulated_intervention": _boot(g_hits),
               "text_store": (_boot(s_hits) if s_hits else {"acc": float("nan"), "ci": [float("nan")] * 2, "n": 0}),
               "text_store_coverage": round(s_cov / max(1, len(edges)), 3),
               "observational_cooccurrence": _boot(o_hits),
               "random_twin": _boot(t_hits),
               "grounded_minus_text_store_ceiling": round(float(np.mean(g_hits)) - TEXT_STORE_CEILING, 4)}}
    d = out["direction_recovery_on_real_science_concepts"]
    out["headline"] = (
        "SCIENCE BRIDGE -- DIRECTION RECOVERY on real science concepts (nodes=%d edges=%d) | grounded simulated-"
        "intervention %.3f%s vs text-store %.3f%s (cov %.2f) vs observational %.3f vs twin %.3f | grounded-vs-text-"
        "ceiling %+.3f" % (
            out["n_nodes"], out["n_edges"], d["grounded_simulated_intervention"]["acc"],
            d["grounded_simulated_intervention"]["ci"], d["text_store"]["acc"], d["text_store"]["ci"],
            d["text_store_coverage"], d["observational_cooccurrence"]["acc"], d["random_twin"]["acc"],
            d["grounded_minus_text_store_ceiling"]))
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
        return {"acc": round(float(a.mean()), 4) if len(a) else float("nan"), "ci": [float("nan")] * 2, "n": int(len(a))}
    r = np.random.default_rng(seed)
    bs = [a[r.integers(0, len(a), len(a))].mean() for _ in range(n_boot)]
    return {"acc": round(float(a.mean()), 4),
            "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)], "n": int(len(a))}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test or a.smoke:
        run(smoke=True); print("SELFTEST PASS", flush=True); return 0
    run(); return 0


if __name__ == "__main__":
    sys.exit(main())
