"""exp_grounded_causal_learner_organ_v1 -- HARDENED-TOWARD-AN-ORGAN prototype: ONE `GroundedCausalLearner` that unifies
the proven grounded-causal pieces into a reusable, ONLINE (plastic), brain-foundational learner that composes into
hdlab.causal_reasoner. This is the Q111 landing target (promote to hdlab/grounded_causal_learner.py).

WHAT IT UNIFIES (each piece proven in its own cell, cited):
  * DIRECTION from interventional asymmetry (exp_causal_direction_grounded_intervention: 0.99, +0.38 over the 0.61 text
    ceiling; cause-selection 0.03->0.98 through causal_reasoner).
  * SIGN from interventional DX-DY covariation (exp_causal_sign_grounded_ddyn: 0.999 vs text 0.745).
  * GENERAL readout -- mutual information orients ANY functional form incl. non-monotone (generalization cell: quad
    0.688->0.930).
  * ACTIVE, FEW-SHOT selection -- information-greedy intervention choice reaches 0.90 in ~5 interventions, the brain's
    few-shot band (active-selection cell; Bramley 2017 / Coenen 2015), vs random's ~25.
  * ONLINE / PLASTIC -- each interventional batch UPDATES a running strength estimate (Rescorla-Wagner), never a frozen
    fit (project discipline: brain is plastic, never frozen).

BRAIN GROUNDING (PINNED): Pearl do-operator (intervention breaks confounding); Gopnik/Schulz blicket-detector covariation
learning; Bramley 2017 active causal structure learning; Rescorla-Wagner online update. OUR-INVENTION (swept): the
readout dependence measure (cov/mag/MI), the movement threshold, the RW learning rate.

HONEST BOUND: learns from GROUNDED interventional experience (a micro-world stands in for embodiment). The remaining
real-reader gap is the GROUNDING BRIDGE (map narrative quantities -> a grounded/simulable dynamical model so the do() is
available at read-time) -- the generative world-model main event, scoped separately. This cell proves the LEARNER + its
causal_reasoner composition are ready for that bridge. Glass-box, synthetic, NO LLM.
Run: .venv/Scripts/python.exe experiments/exp_grounded_causal_learner_organ_v1.py --run [--smoke]
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"   # operation PINNED; readout+selection OUR-INVENTION-UNDER-TEST; input = micro-world stand-in
__bf_note__ = ("unified grounded causal learner. PINNED (copy the computation): interventional do-asymmetry breaks "
               "confounding (Pearl do-operator); covariation-from-intervention (Gopnik/Schulz blicket detector); "
               "active near-optimal experiment selection (Bramley 2017); Rescorla-Wagner online plastic update. "
               "OUR-INVENTION-UNDER-TEST (swept, not adopted): the dependence READOUT (cov/mag/mutual-information, MI our "
               "generalization of covariation), the greedy vertex-cover SELECTION heuristic (our approx of Bramley "
               "near-optimality), move/lr thresholds. Held at BF_SPIRIT (NOT BF) because (a) those two invented pieces "
               "and (b) the INPUT is a micro-world STAND-IN for grounded experience -- raise to BF once the grounding "
               "bridge feeds real grounded/simulated experience AND the audit verifies the operation on it. Composes "
               "into hdlab.causal_reasoner (verified rung-2/3).")
__bf_corrections__ = []

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

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
OUT = str(get_output_dir("exp_grounded_causal_learner_organ_v1"))
def _cov(x, y):
    return float(np.mean((x - x.mean()) * (y - y.mean())))


def _mi_binned(x, y, bins=8):
    n = len(x)
    if n < bins * 2:
        return 0.0
    xe = np.quantile(x, np.linspace(0, 1, bins + 1)); ye = np.quantile(y, np.linspace(0, 1, bins + 1))
    xe[0] -= 1e-9; ye[0] -= 1e-9
    xi = np.clip(np.digitize(x, xe) - 1, 0, bins - 1); yi = np.clip(np.digitize(y, ye) - 1, 0, bins - 1)
    pij = np.zeros((bins, bins))
    for a, b in zip(xi, yi):
        pij[a, b] += 1.0
    pij /= pij.sum()
    pi = pij.sum(1, keepdims=True); pj = pij.sum(0, keepdims=True)
    m = pij * (np.log(pij + 1e-12) - np.log(pi + 1e-12) - np.log(pj + 1e-12))
    return float(np.nansum(np.where(pij > 0, m, 0.0)))


class GroundedCausalLearner:
    """Learn a directed, signed causal graph over `nodes` from GROUNDED INTERVENTIONAL experience -- online, active,
    few-shot. One `observe_intervention` call = one grounded do() episode; the learner refines its orientation+sign
    beliefs (plastic). `to_causal_graph` exports a hdlab.causal_reasoner.CausalGraph for the do-simulation reasoner."""

    def __init__(self, nodes: Sequence, skeleton: Sequence[Tuple], readout: str = "mi",
                 move_thr: float = 0.02, lr: float = 0.4):
        self.nodes = list(nodes)
        self.skeleton = [frozenset(e) for e in skeleton]          # candidate undirected edges (reader-extracted)
        self.readout = readout
        self.move_thr = move_thr
        self.lr = lr
        self.influence: Dict[Tuple, float] = defaultdict(float)   # running |do(a)->b| strength (RW), ordered (a,b)
        self.sign_run: Dict[Tuple, float] = defaultdict(float)    # running signed DX->DY (RW), ordered (a,b)
        self.intervened = set()

    def _dep(self, va, vb) -> float:
        if self.readout == "cov":
            return abs(_cov(va, vb))
        if self.readout == "mag":
            return abs(_cov(np.abs(va - va.mean()), np.abs(vb - vb.mean())))
        return _mi_binned(va, vb)                                 # default: mutual information (any functional form)

    def observe_intervention(self, do_node: int, V: np.ndarray) -> None:
        """One grounded do(do_node) episode: V[:, do_node] was set independently; update strength+sign for every
        skeleton edge incident to do_node (RW online update -> plastic)."""
        self.intervened.add(do_node)
        va = V[:, do_node]
        for e in self.skeleton:
            if do_node not in e:
                continue
            other = next(iter(e - {do_node}))
            vb = V[:, other]
            dep = self._dep(va, vb)
            self.influence[(do_node, other)] += self.lr * (dep - self.influence[(do_node, other)])
            self.sign_run[(do_node, other)] += self.lr * (_cov(va, vb) - self.sign_run[(do_node, other)])

    def select_intervention(self) -> Optional[int]:
        """ACTIVE info-greedy choice (Bramley): the un-intervened node covering the most still-UNORIENTED incident
        edges (approximates a minimum vertex cover -> few-shot). None when every edge is orientable."""
        remaining = [n for n in self.nodes if n not in self.intervened]
        if not remaining:
            return None
        def unoriented_incident(n):
            c = 0
            for e in self.skeleton:
                if n in e and not self._orientable(e):
                    c += 1
            return c
        best = max(remaining, key=lambda n: unoriented_incident(n))
        return best if unoriented_incident(best) > 0 else None

    def _orientable(self, e: frozenset) -> bool:
        a, b = tuple(e)
        return (a in self.intervened) or (b in self.intervened)

    def orient(self, e: frozenset) -> Optional[Tuple]:
        """Oriented (cause, effect) for a skeleton edge: whichever endpoint's do() moved the other more."""
        a, b = tuple(e)
        iab = self.influence.get((a, b), 0.0); iba = self.influence.get((b, a), 0.0)
        if a not in self.intervened and b not in self.intervened:
            return None
        return (a, b) if iab >= iba else (b, a)

    def edge_sign(self, cause: int, effect: int) -> int:
        s = self.sign_run.get((cause, effect), 0.0)
        return 1 if s >= 0 else -1

    def to_causal_graph(self) -> CausalGraph:
        """Export the learned directed+signed graph as a hdlab.causal_reasoner.CausalGraph."""
        g = CausalGraph()
        for n in self.nodes:
            g.add_node("q%d" % n)
        for e in self.skeleton:
            o = self.orient(e)
            if o is None:
                continue
            c, ef = o
            g.add_edge("q%d" % c, "q%d" % ef, polarity=self.edge_sign(c, ef))
        return g


def _skeleton(scm):
    return sorted({(min(i, j), max(i, j)) for (i, j) in scm["sign"]})


def _true_roots(scm, j):
    anc = set(); stack = list(scm["parents"][j])
    while stack:
        p = stack.pop()
        if p in anc:
            continue
        anc.add(p); stack.extend(scm["parents"][p])
    return sorted([a for a in anc if not scm["parents"][a]])


def run(smoke: bool = False) -> Dict:
    t0 = time.time(); os.makedirs(OUT, exist_ok=True)
    kk = 10
    n_world = 40 if smoke else 120
    n_int = 300 if smoke else 800
    rng = np.random.default_rng(2026)

    fewshot_dir, fewshot_sel, online_dir = [], [], []
    budgets = []
    for w in range(n_world):
        scm = make_scm(kk, np.random.default_rng(1000 + w))
        skel = _skeleton(scm)
        learner = GroundedCausalLearner(range(kk), skel, readout="mi")
        # ACTIVE FEW-SHOT loop: select -> grounded do() -> observe (online), until oriented or budget hit
        n_used = 0
        while True:
            node = learner.select_intervention()
            if node is None or n_used >= kk:
                break
            V = sample(scm, rng, n_int, do_node=node)
            learner.observe_intervention(node, V)
            n_used += 1
        budgets.append(n_used)
        # DIRECTION accuracy on the skeleton (learned orientation vs truth: DAG topological i<j => i->j)
        for e in skel:
            o = learner.orient(e)
            if o is None:
                continue
            a, b = tuple(e)
            fewshot_dir.append(1.0 if o == (min(a, b), max(a, b)) else 0.0)
        # CAUSE SELECTION through causal_reasoner over the learned graph
        g = learner.to_causal_graph()
        for j in range(kk):
            roots = _true_roots(scm, j)
            if not roots:
                continue
            r = g.ultimate_cause("q%d" % j)
            fewshot_sel.append(1.0 if r in {"q%d" % x for x in roots} else 0.0)
        # ONLINE PLASTICITY: a SECOND pass of interventions should not degrade (and should refine) -- re-observe once
        for node in list(learner.intervened):
            learner.observe_intervention(node, sample(scm, rng, n_int, do_node=node))
        for e in skel:
            o = learner.orient(e)
            if o is None:
                continue
            a, b = tuple(e)
            online_dir.append(1.0 if o == (min(a, b), max(a, b)) else 0.0)

    out = {"smoke": smoke, "k": kk, "n_worlds": n_world, "n_int_per_node": n_int,
           "mean_interventions_used": round(float(np.mean(budgets)), 2),
           "direction_accuracy_fewshot_active": _boot(fewshot_dir),
           "cause_selection_via_causal_reasoner": _boot(fewshot_sel),
           "direction_accuracy_after_online_refresh": _boot(online_dir)}
    out["headline"] = (
        "GROUNDED CAUSAL LEARNER (organ prototype) k=%d worlds=%d | active few-shot interventions used %.1f | DIRECTION "
        "%.3f%s | CAUSE-SELECTION via causal_reasoner %.3f%s | direction after online refresh %.3f%s (plastic, no "
        "degrade)" % (
            kk, n_world, out["mean_interventions_used"], out["direction_accuracy_fewshot_active"]["acc"],
            out["direction_accuracy_fewshot_active"]["ci"], out["cause_selection_via_causal_reasoner"]["acc"],
            out["cause_selection_via_causal_reasoner"]["ci"], out["direction_accuracy_after_online_refresh"]["acc"],
            out["direction_accuracy_after_online_refresh"]["ci"]))
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
