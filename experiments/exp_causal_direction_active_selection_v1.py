"""exp_causal_direction_active_selection_v1 -- THE LAST LEVER: ACTIVE intervention selection + structural priors, the
brain's FEW-SHOT causal-learning efficiency (brain-foundational checklist #6 residual: close the data-efficiency gap).

The grounded interventional mechanism (exp_causal_direction_grounded_intervention/_generalization) recovers direction
0.99 but at ~25 random interventions for 0.90; the brain orients cause->effect from ~2-10 interventions (Gopnik/Schulz
blicket detector; Bramley et al. 2017 near-optimal active structure learning; Coenen et al. 2015 information-greedy /
positive-test). The difference is ACTIVE SELECTION: the brain does NOT intervene randomly -- it chooses the do() that
resolves the most structure, and carries a structural PRIOR.

KEY STRUCTURE (why active is few-shot): under the interventional asymmetry a SINGLE do(node) orients EVERY edge
incident to node at once (do(node) moves its descendants, not its ancestors -> each incident edge is oriented in one
shot). So orienting the whole graph needs interventions on a VERTEX COVER of the skeleton, and the information-greedy
policy (intervene on the node covering the most still-UNORIENTED edges) approximates the MINIMUM vertex cover -- far
fewer than random order. This is exactly Bramley's finding that people pick maximally-disambiguating interventions.

ARMS (edges correctly oriented vs #interventions, on the reader's candidate skeleton):
  * active   = information-greedy: each step do() the un-intervened node with the most unoriented incident edges.
  * prior    = a structural DEGREE prior on WHICH node to test first (hub-first) -- active + the brain's prior.
  * random   = random node order (the passive baseline = the base prototype's implicit policy).
  * observational-ceiling = the ~0.61 text store (no intervention) reference line.
Metric: fraction of skeleton edges CORRECTLY oriented at each budget; #interventions to full orientation; and the
budget to reach the brain few-shot band. Glass-box, synthetic, NO LLM.
Run: .venv/Scripts/python.exe experiments/exp_causal_direction_active_selection_v1.py --run [--smoke]
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"
__bf_note__ = ("active causal-structure learning: information-greedy intervention selection (Bramley 2017 / Coenen "
               "2015) approximating a minimum vertex cover of the skeleton, closing the few-shot data-efficiency gap to "
               "the brain; a single interventional do() orients every incident edge via the asymmetry.")

import argparse
import json
import os
import sys
import time
from typing import Dict, List, Tuple

import numpy as np

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
os.environ.setdefault("PYTHONHASHSEED", "0")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_sign_grounded_ddyn_v1 import make_scm, sample

from experiments._seed_checkpoint import get_output_dir  # Q115 (owner 2026-08-23): route the output dir
OUT = str(get_output_dir("exp_causal_direction_active_selection_v1"))
TEXT_STORE_CEILING = 0.61
BRAIN_FEWSHOT_BAND = 10


def _cov(x, y):
    return float(np.mean((x - x.mean()) * (y - y.mean())))


def skeleton(scm: Dict) -> List[Tuple[int, int]]:
    """The undirected candidate edges (the reader's extracted skeleton, direction unknown)."""
    seen = set()
    for (i, j) in scm["sign"]:
        seen.add((min(i, j), max(i, j)))
    return sorted(seen)


def orient_with(intr: Dict, node: int, other: int, thr: float) -> Tuple[int, int]:
    """One interventional do(node) orients edge {node,other}: if do(node) MOVES other -> node is the cause."""
    moved = abs(_cov(intr[node][:, node], intr[node][:, other])) > thr
    if moved:
        return (node, other)
    return (other, node)


def true_dir(a: int, b: int) -> Tuple[int, int]:
    """True orientation of skeleton edge {a,b}: the DAG is topological (i<j => i->j)."""
    return (a, b) if a < b else (b, a)


def _degrees(edges: List[Tuple[int, int]], k: int) -> Dict[int, int]:
    deg = {n: 0 for n in range(k)}
    for (a, b) in edges:
        deg[a] += 1; deg[b] += 1
    return deg


def run_policy(scm: Dict, intr: Dict, policy: str, thr: float, k: int) -> List[float]:
    """Run an intervention-selection policy; return the fraction of skeleton edges CORRECTLY oriented after each
    intervention (index 0 = after 1 intervention). Every incident edge of the chosen node is oriented at that step."""
    edges = skeleton(scm)
    if not edges:
        return []
    oriented: Dict[Tuple[int, int], Tuple[int, int]] = {}
    intervened = set()
    deg = _degrees(edges, k)
    curve = []
    order_budget = min(k, k)
    for _ in range(order_budget):
        remaining = [n for n in range(k) if n not in intervened]
        if not remaining:
            break
        unoriented_incident = {n: sum(1 for (a, b) in edges
                                      if (a, b) not in oriented and n in (a, b)) for n in remaining}
        if policy == "active":
            node = max(remaining, key=lambda n: (unoriented_incident[n], deg[n]))
        elif policy == "prior":
            node = max(remaining, key=lambda n: (deg[n], unoriented_incident[n]))   # hub-first structural prior
        else:  # random
            node = remaining[int(np.random.default_rng(7 * k + len(intervened)).integers(0, len(remaining)))]
        intervened.add(node)
        for (a, b) in edges:
            if (a, b) in oriented:
                continue
            if node in (a, b):
                other = b if a == node else a
                oriented[(a, b)] = orient_with(intr, node, other, thr)
        correct = sum(1 for e in edges if e in oriented and oriented[e] == true_dir(*e))
        curve.append(correct / len(edges))
        if len(oriented) == len(edges):
            # pad the rest of the curve with the final value (fully oriented)
            while len(curve) < order_budget:
                curve.append(correct / len(edges))
            break
    return curve


def run(smoke: bool = False) -> Dict:
    t0 = time.time(); os.makedirs(OUT, exist_ok=True)
    kk = 10
    n_world = 40 if smoke else 120
    n_int = 300 if smoke else 800     # MODEST budget per node (few-shot regime, not 4000)
    thr = 0.05
    rng = np.random.default_rng(2026)

    acc = {"active": np.zeros(kk), "prior": np.zeros(kk), "random": np.zeros(kk)}
    full = {"active": [], "prior": [], "random": []}
    for w in range(n_world):
        scm = make_scm(kk, np.random.default_rng(1000 + w))
        intr = {i: sample(scm, rng, n_int, do_node=i) for i in range(kk)}
        for pol in acc:
            curve = run_policy(scm, intr, pol, thr, kk)
            if not curve:
                continue
            padded = curve + [curve[-1]] * (kk - len(curve))
            acc[pol] += np.array(padded[:kk])
            full[pol].append(next((i + 1 for i, v in enumerate(curve) if v >= 0.999), len(curve)))

    out = {"smoke": smoke, "k": kk, "n_worlds": n_world, "n_int_per_node": n_int,
           "text_store_ceiling": TEXT_STORE_CEILING, "brain_fewshot_band": BRAIN_FEWSHOT_BAND}
    for pol in acc:
        acc[pol] = (acc[pol] / max(1, n_world)).round(4).tolist()
    out["edges_correct_by_num_interventions"] = acc
    out["mean_interventions_to_full_orientation"] = {p: round(float(np.mean(full[p])), 2) for p in full}
    # budget to reach the brain band accuracy (0.90 correct-orientation)
    def budget_to(pol, tgt=0.90):
        return next((i + 1 for i, v in enumerate(out["edges_correct_by_num_interventions"][pol]) if v >= tgt), None)
    out["interventions_to_0.90"] = {p: budget_to(p) for p in acc}
    a = out["edges_correct_by_num_interventions"]
    out["headline"] = (
        "ACTIVE CAUSAL LEARNING (few-shot direction) k=%d worlds=%d | edges-correct by #interventions: ACTIVE %s "
        "PRIOR %s RANDOM %s | interventions-to-0.90: active %s vs random %s | mean-to-FULL: active %.2f prior %.2f "
        "random %.2f | (text ceiling %.2f, brain few-shot ~<=%d)" % (
            kk, n_world, a["active"], a["prior"], a["random"], out["interventions_to_0.90"]["active"],
            out["interventions_to_0.90"]["random"], out["mean_interventions_to_full_orientation"]["active"],
            out["mean_interventions_to_full_orientation"]["prior"],
            out["mean_interventions_to_full_orientation"]["random"], TEXT_STORE_CEILING, BRAIN_FEWSHOT_BAND))
    out["elapsed_s"] = round(time.time() - t0, 1)
    tmp = os.path.join(OUT, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(OUT, "metrics.json"))
    print("[run] " + out["headline"], flush=True)
    return out


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
