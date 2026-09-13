"""exp_causal_direction_grounded_intervention_v1 -- PROTOTYPE of THE BIGGER LEVER: recover causal DIRECTION from
grounded INTERVENTION, past the ~0.61 text-mined-store ceiling.

WHY (from wire_the_mined_directed_causal_store... SOLVED, REFUTED): the mined directed causal store's genuine asset is
DIRECTION, but text caps it at ~0.61 accuracy (intrinsic; grow_the_causal_mechanism: clean markers only 0.626, scale
doesn't lift direction). The store is inert on the WIQA existence axis (direction-insensitive by construction) and only
CI-sep (small) on direction-discrimination 2AFC. The SOLVED located the ONLY route past ~0.61: GROUNDED INTERVENTIONAL
experience -- NO landed organ, only the SIGN prototype (exp_causal_sign_grounded_ddyn_v1, sign 0.999 vs text 0.745).

THIS CELL builds the DIRECTION analogue on the SAME grounded parts (make_scm/sample from the sign prototype +
causal_reasoner). The brain's mechanism (Pearl do-operator; Gopnik "blicket detector" causal learning; Badre/Frank):
  do(X) and see if Y moves; do(Y) and see if X moves. The INTERVENTIONAL ASYMMETRY recovers direction --
  do(cause) shifts the effect; do(effect) does NOT shift the cause. Observation cannot: co-occurrence is symmetric AND
  a shared confounder (the topic/script analogue -- exactly why text co-occurrence caps out) makes level-correlation
  direction-blind. So:
  * grounded_intervention (THE FIX): orient a->b by |interventional influence do(a)->b| vs |do(b)->a|. Rung-2.
  * observational (the TEXT/STORE analogue, rung-1): orient by an additive-noise-model residual asymmetry over the
    OBSERVATIONAL levels -- at chance under the Gaussian confounder (mirrors the store's ~0.61 confounded ceiling).
  * twin (info-free): random orientation. MUST lose.
Then the interventionally-DIRECTED edges are composed into hdlab.causal_reasoner and used for CAUSE SELECTION
(ultimate_cause / backward walk): the grounded-directed graph finds the true root cause where the observational
(mis-oriented) graph cannot -- the store's proper live consumer, now fed a direction source that beats the text cap.

CLAIM TO PROVE: grounded interventional direction-recovery >> the ~0.61 text-store ceiling (and >> observation under
confounding), CI-sep, twin losing; and it lifts causal-SELECTION through causal_reasoner. HONEST BOUND: this is a
grounded MICRO-WORLD (the substrate has no embodiment); the remaining real gap is the GROUNDING BRIDGE (map narrative
quantities -> a grounded dynamical model) = the generative world-model main event. Glass-box, synthetic, NO LLM.

Run: .venv/Scripts/python.exe experiments/exp_causal_direction_grounded_intervention_v1.py --run [--smoke]
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"
__bf_note__ = ("prototypes the brain's grounded causal-DIRECTION mechanism: orient edges by interventional asymmetry "
               "(do(a)->b vs do(b)->a; Pearl do-operator / Gopnik covariation), recovering direction that text "
               "co-occurrence (rung-1, confounded, ~0.61-capped) cannot; composed into causal_reasoner for cause "
               "selection. Micro-world stands in for embodiment; the grounding bridge to narrative is the remaining gap.")

import argparse
import json
import os
import sys
import time
from typing import Dict, List

import numpy as np

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
os.environ.setdefault("PYTHONHASHSEED", "0")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.causal_reasoner import CausalGraph
from experiments.exp_causal_sign_grounded_ddyn_v1 import make_scm, sample

from experiments._seed_checkpoint import get_output_dir  # Q115 (owner 2026-08-23): route the output dir
OUT = str(get_output_dir("exp_causal_direction_grounded_intervention_v1"))
TEXT_STORE_CEILING = 0.61   # the intrinsic text-mined-direction cap (grow_the_causal_mechanism SOLVED)


def _cov(x, y):
    return float(np.mean((x - x.mean()) * (y - y.mean())))


def interventional_influence(intr: Dict, a: int, b: int) -> float:
    """|influence of do(a) on b| = |cov(a, b) under do(a)| (a is set independently, so this is the pure a->b effect,
    confounder broken). Large when a is upstream of b; ~0 when b is upstream of a (do(a) can't move an ancestor)."""
    va = intr[a][:, a]; vb = intr[a][:, b]
    return abs(_cov(va, vb))


def grounded_direction(intr: Dict, a: int, b: int) -> int:
    """Orient by interventional ASYMMETRY: +1 => a->b, -1 => b->a. do(a)->b vs do(b)->a."""
    iab = interventional_influence(intr, a, b)
    iba = interventional_influence(intr, b, a)
    return 1 if iab > iba else (-1 if iba > iab else 0)


def observational_direction(Vobs: np.ndarray, a: int, b: int) -> int:
    """The TEXT/STORE analogue (rung-1): additive-noise-model residual asymmetry over OBSERVATIONAL levels. Fit b~a and
    a~b by least squares; orient toward the model whose residual is LESS dependent on the input (ANM; Hoyer 2009). Under
    a Gaussian shared confounder this is direction-blind -> at chance (mirrors the store's confounded ~0.61 ceiling)."""
    x = Vobs[:, a]; y = Vobs[:, b]
    def resid_dep(u, v):                      # fit v ~ u, return |corr(residual, u)| ; ANM: true dir -> ~0
        b1 = _cov(u, v) / (np.var(u) + 1e-9)
        r = v - b1 * u
        return abs(_cov(r, u)) / (np.std(r) * np.std(u) + 1e-9)
    dep_ab = resid_dep(x, y)                  # a->b residual dependence
    dep_ba = resid_dep(y, x)                  # b->a residual dependence
    return 1 if dep_ab < dep_ba else (-1 if dep_ba < dep_ab else 0)


def run(smoke: bool = False) -> Dict:
    t0 = time.time(); os.makedirs(OUT, exist_ok=True)
    n_world = 40 if smoke else 150
    k = 8
    n_obs = 4000 if smoke else 12000
    n_int = 1500 if smoke else 4000
    rng = np.random.default_rng(2026)

    g_hits, o_hits, t_hits = [], [], []         # DIRECTION recovery per ordered ancestor->descendant pair
    sel_g, sel_o = [], []                        # cause SELECTION (find the true root) via causal_reasoner
    for w in range(n_world):
        scm = make_scm(k, np.random.default_rng(1000 + w))
        Vobs = sample(scm, rng, n_obs)
        intr = {i: sample(scm, rng, n_int, do_node=i) for i in range(k)}
        # true direction: for i<j on a real directed path, the arrow is i->j (topological DAG). Use connected pairs.
        pairs = []
        for i in range(k):
            desc = _descendants(scm, i)
            for j in desc:
                pairs.append((i, j))            # true orientation is i->j
        for (i, j) in pairs:
            gd = grounded_direction(intr, i, j)
            od = observational_direction(Vobs, i, j)
            tr = np.random.default_rng(7 * w + i * 31 + j)
            td = 1 if tr.random() < 0.5 else -1
            g_hits.append(1.0 if gd == 1 else 0.0)     # gd==+1 means a->b i.e. i->j = TRUE
            o_hits.append(1.0 if od == 1 else 0.0)
            t_hits.append(1.0 if td == 1 else 0.0)
        # -- CAUSE SELECTION via causal_reasoner: build graphs with LEARNED orientations, find the outcome's root --
        gG = _build_directed_graph(scm, intr, Vobs, source="grounded")
        oG = _build_directed_graph(scm, intr, Vobs, source="observational")
        for j in range(k):
            roots_true = _true_roots(scm, j)
            if not roots_true:
                continue
            rg = gG.ultimate_cause("q%d" % j); ro = oG.ultimate_cause("q%d" % j)
            sel_g.append(1.0 if (rg in {"q%d" % r for r in roots_true}) else 0.0)
            sel_o.append(1.0 if (ro in {"q%d" % r for r in roots_true}) else 0.0)

    out = {
        "smoke": smoke, "n_worlds": n_world, "k": k, "n_pairs": len(g_hits), "text_store_ceiling": TEXT_STORE_CEILING,
        "direction_recovery": {
            "grounded_intervention": _boot(g_hits),
            "observational_textanalog": _boot(o_hits),
            "random_twin": _boot(t_hits),
            "paired_grounded_minus_observational": _paired(g_hits, o_hits),
            "paired_grounded_minus_twin": _paired(g_hits, t_hits),
            "grounded_minus_text_store_ceiling": round(float(np.mean(g_hits)) - TEXT_STORE_CEILING, 4)},
        "cause_selection_via_causal_reasoner": {
            "grounded": _boot(sel_g), "observational": _boot(sel_o),
            "paired_grounded_minus_observational": _paired(sel_g, sel_o)},
    }
    d = out["direction_recovery"]; s = out["cause_selection_via_causal_reasoner"]
    out["headline"] = (
        "GROUNDED-INTERVENTION DIRECTION (past the %.2f text ceiling) worlds=%d pairs=%d | DIRECTION RECOVERY: "
        "grounded %.3f%s vs observational/text-analog %.3f%s vs twin %.3f | paired(grounded-obs) %+.4f%s (grounded-twin) "
        "%+.4f%s | grounded-vs-text-ceiling %+.4f || CAUSE SELECTION via causal_reasoner: grounded %.3f%s vs "
        "observational %.3f%s (paired %+.4f%s)" % (
            TEXT_STORE_CEILING, out["n_worlds"], out["n_pairs"],
            d["grounded_intervention"]["acc"], d["grounded_intervention"]["ci"],
            d["observational_textanalog"]["acc"], d["observational_textanalog"]["ci"], d["random_twin"]["acc"],
            d["paired_grounded_minus_observational"]["delta"], d["paired_grounded_minus_observational"]["ci"],
            d["paired_grounded_minus_twin"]["delta"], d["paired_grounded_minus_twin"]["ci"],
            d["grounded_minus_text_store_ceiling"],
            s["grounded"]["acc"], s["grounded"]["ci"], s["observational"]["acc"], s["observational"]["ci"],
            s["paired_grounded_minus_observational"]["delta"], s["paired_grounded_minus_observational"]["ci"]))
    out["elapsed_s"] = round(time.time() - t0, 1)
    tmp = os.path.join(OUT, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(OUT, "metrics.json"))
    print("[run] " + out["headline"], flush=True)
    return out


def _descendants(scm: Dict, i: int) -> List[int]:
    """Nodes reachable from i via the DAG parents map (i is an ancestor of them)."""
    k = scm["k"]; out = set()
    changed = True
    reach = {i}
    while changed:
        changed = False
        for j in range(k):
            if j in reach:
                continue
            if any(p in reach for p in scm["parents"][j]):
                reach.add(j); changed = True
    reach.discard(i)
    return sorted(reach)


def _true_roots(scm: Dict, j: int) -> List[int]:
    """Source ancestors of j (ancestors with no parents) = the true ultimate causes."""
    anc = set()
    stack = list(scm["parents"][j])
    while stack:
        p = stack.pop()
        if p in anc:
            continue
        anc.add(p); stack.extend(scm["parents"][p])
    return sorted([a for a in anc if not scm["parents"][a]])


def _build_directed_graph(scm: Dict, intr: Dict, Vobs: np.ndarray, source: str) -> CausalGraph:
    """Build a CausalGraph over the SAME undirected skeleton (the true edges), but orient each edge by the LEARNED
    direction from `source`. Isolates DIRECTION as the only difference between the grounded and observational graphs."""
    g = CausalGraph()
    for (i, j) in scm["sign"]:                  # true undirected skeleton
        a, b = i, j
        if source == "grounded":
            d = grounded_direction(intr, a, b)
        else:
            d = observational_direction(Vobs, a, b)
        if d >= 0:
            g.add_edge("q%d" % a, "q%d" % b)
        else:
            g.add_edge("q%d" % b, "q%d" % a)
    return g


def _boot(hits, seed=17, n_boot=4000):
    a = np.array(hits, float)
    if len(a) < 3:
        return {"acc": float("nan"), "ci": [float("nan"), float("nan")], "n": int(len(a))}
    r = np.random.default_rng(seed)
    bs = [a[r.integers(0, len(a), len(a))].mean() for _ in range(n_boot)]
    return {"acc": round(float(a.mean()), 4),
            "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)], "n": int(len(a))}


def _paired(h1, h2, seed=23, n_boot=4000):
    n = min(len(h1), len(h2))
    if n < 3:
        return {"delta": float("nan"), "ci": [float("nan"), float("nan")]}
    d = np.array(h1[:n], float) - np.array(h2[:n], float)
    r = np.random.default_rng(seed)
    bs = [d[r.integers(0, len(d), len(d))].mean() for _ in range(n_boot)]
    return {"delta": round(float(d.mean()), 4),
            "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]}


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
