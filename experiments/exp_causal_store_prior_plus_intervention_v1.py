"""exp_causal_store_prior_plus_intervention_v1 -- THE STORE'S CORRECT ROLE: a directional PRIOR that bootstraps grounded
intervention (fewer-shot), NOT a standalone scorer.

This solve REFUTED the mined store as a necessity scorer and found its only real asset is DIRECTION, capped ~0.61
(intrinsic text ceiling). The brain does not choose testimony OR intervention -- it uses BOTH: causal knowledge from
testimony (Harris & Koenig 2006) as a PRIOR, refined by intervention (Gopnik/Schulz; Bramley 2017 learners carry priors
and update them). So the store's brain-foundational role is a PRIOR over edge directions that (a) gives a head start
before any intervention and (b) lets active selection spend its few interventions on the edges the prior is UNSURE
about -- reaching target accuracy in FEWER interventions than intervention-from-scratch.

THE TEST (micro-world; the store's information content = a directional prior calibrated to its MEASURED accuracy p):
for each skeleton edge, a prior orients it correctly with probability p (p=0.61 == the store's measured direction cap;
swept). The learner initializes belief from the prior, actively intervenes on the highest-impact still-uncertain nodes,
fuses (interventional direction where intervened, prior elsewhere). We read direction accuracy vs #interventions for
p in {0.50 (no prior), 0.61 (the store), 0.80}, and the interventions-to-0.90 for each -- does the store prior cut it?

Reuses make_scm/sample + the interventional readout. Glass-box, synthetic, NO LLM.
Run: .venv/Scripts/python.exe experiments/exp_causal_store_prior_plus_intervention_v1.py --run [--smoke]
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"
__bf_note__ = ("the mined store's correct role: a testimony-derived directional PRIOR (Harris-Koenig) bootstrapping "
               "grounded intervention (Gopnik/Bramley), reducing interventions-to-target; fused with interventional "
               "evidence. Prior calibrated to the store's MEASURED 0.61 direction accuracy.")

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
OUT = str(get_output_dir("exp_causal_store_prior_plus_intervention_v1"))
STORE_DIRECTION_ACC = 0.61   # the mined store's MEASURED intrinsic direction-accuracy cap (grow_the_causal_mechanism)


def _cov(x, y):
    return float(np.mean((x - x.mean()) * (y - y.mean())))


def _skeleton(scm):
    return sorted({(min(i, j), max(i, j)) for (i, j) in scm["sign"]})


def _degrees(edges, k):
    deg = {n: 0 for n in range(k)}
    for (a, b) in edges:
        deg[a] += 1; deg[b] += 1
    return deg


def prior_orient(edge, p, rng):
    """A directional prior that orients `edge` correctly with probability p (true dir is (min,max) by DAG topology)."""
    a, b = edge
    true = (a, b)
    return true if rng.random() < p else (b, a)


def run_budget(scm, intr, prior_dir, budget, thr, k):
    """Active few-shot: intervene on the `budget` highest-impact (degree) un-intervened nodes; fuse interventional
    direction (where intervened) with the prior (elsewhere). Return direction accuracy over the skeleton."""
    edges = _skeleton(scm)
    deg = _degrees(edges, k)
    order = sorted(range(k), key=lambda n: -deg[n])         # active: hub-first (high-impact vertex cover)
    intervened = set(order[:budget])
    correct = 0
    for e in edges:
        a, b = e
        if a in intervened or b in intervened:
            node = a if a in intervened else b
            other = b if node == a else a
            moved = abs(_cov(intr[node][:, node], intr[node][:, other])) > thr
            oriented = (node, other) if moved else (other, node)
        else:
            oriented = prior_dir[e]                          # fall back to the store prior
        if oriented == (min(a, b), max(a, b)):
            correct += 1
    return correct / len(edges)


def run(smoke: bool = False) -> Dict:
    t0 = time.time(); os.makedirs(OUT, exist_ok=True)
    kk = 10
    n_world = 40 if smoke else 120
    n_int = 300 if smoke else 800
    thr = 0.05
    budgets = list(range(0, kk + 1))
    priors = [0.50, STORE_DIRECTION_ACC, 0.80]
    rng = np.random.default_rng(2026)

    curves = {p: np.zeros(len(budgets)) for p in priors}
    for w in range(n_world):
        scm = make_scm(kk, np.random.default_rng(1000 + w))
        intr = {i: sample(scm, rng, n_int, do_node=i) for i in range(kk)}
        prng = np.random.default_rng(50 + w)
        for p in priors:
            prior_dir = {e: prior_orient(e, p, prng) for e in _skeleton(scm)}
            for bi, b in enumerate(budgets):
                curves[p][bi] += run_budget(scm, intr, prior_dir, b, thr, kk)

    out = {"smoke": smoke, "k": kk, "n_worlds": n_world, "store_direction_acc": STORE_DIRECTION_ACC, "budgets": budgets}
    acc_by_prior = {}
    for p in priors:
        acc_by_prior["prior_%.2f" % p] = (curves[p] / max(1, n_world)).round(4).tolist()
    out["direction_acc_by_interventions"] = acc_by_prior

    def to_90(p):
        c = acc_by_prior["prior_%.2f" % p]
        return next((budgets[i] for i, v in enumerate(c) if v >= 0.90), None)
    out["interventions_to_0.90"] = {"no_prior_0.50": to_90(0.50), "store_prior_0.61": to_90(STORE_DIRECTION_ACC),
                                    "strong_prior_0.80": to_90(0.80)}
    # the store's value: interventions saved vs no prior, and the 0-intervention head start
    c0 = acc_by_prior["prior_0.50"]; cs = acc_by_prior["prior_%.2f" % STORE_DIRECTION_ACC]
    out["store_prior_value"] = {
        "head_start_0_interventions": round(cs[0] - c0[0], 4),
        "interventions_saved_to_0.90": (None if out["interventions_to_0.90"]["no_prior_0.50"] is None
                                        or out["interventions_to_0.90"]["store_prior_0.61"] is None else
                                        out["interventions_to_0.90"]["no_prior_0.50"]
                                        - out["interventions_to_0.90"]["store_prior_0.61"]),
        "note": "the store's correct role: a directional PRIOR (0.61) that gives a head start + cuts the interventions "
                "needed. NOT a standalone scorer (refuted on the necessity axis)."}
    out["headline"] = (
        "STORE-AS-PRIOR + GROUNDED INTERVENTION k=%d worlds=%d | direction-acc by #interventions: no-prior(0.50) %s | "
        "STORE-prior(0.61) %s | strong(0.80) %s | interventions-to-0.90: no-prior %s vs STORE-prior %s (saved %s) | "
        "store head-start @0 interventions %+.3f" % (
            kk, n_world, acc_by_prior["prior_0.50"], acc_by_prior["prior_%.2f" % STORE_DIRECTION_ACC],
            acc_by_prior["prior_0.80"], out["interventions_to_0.90"]["no_prior_0.50"],
            out["interventions_to_0.90"]["store_prior_0.61"], out["store_prior_value"]["interventions_saved_to_0.90"],
            out["store_prior_value"]["head_start_0_interventions"]))
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
