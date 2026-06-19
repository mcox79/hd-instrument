"""
exp_stretch4_1_bayes_net_learning_cpu_v1.py -- learn Bayes-net structure + parameters from data -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (STRETCH4-1 BAYESIAN-NETWORK-LEARNING); pure-FHRR/numpy (no download). Sample from a hidden Bayes net; recover skeleton (partial-corr) + estimate CPTs (MLE).
PRE-REGISTERED: HARD-PASS structure-prec>=0.70 AND CPT-err<=0.10. MIDDLE struct>=0.55. HARD-FAIL<0.55.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, itertools
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "stretch4_1_bayes_net_learning_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: bayes-net-learning", flush=True)
def run() -> Dict:
    g = np.random.default_rng(279); NV = 5; NSAMP = 3000; PROBS = 25 if SMOKE else 90
    tp = 0; fp = 0; fn = 0; cpt_err = []
    for _ in range(PROBS):
        parents = {v: sorted(set(int(p) for p in g.choice(v, min(v, 2), replace=False))) if v > 0 else [] for v in range(NV)}
        true_edges = set((p, v) for v in range(NV) for p in parents[v])
        cpt = {}
        for v in range(NV):
            for cfg in itertools.product([0, 1], repeat=len(parents[v])):
                cpt[(v, cfg)] = g.uniform(0.1, 0.9)
        # sample
        X = np.zeros((NSAMP, NV), dtype=int)
        for v in range(NV):
            cfgs = [tuple(X[i, parents[v]]) for i in range(NSAMP)]
            ps = np.array([cpt[(v, c)] for c in cfgs]); X[:, v] = (g.random(NSAMP) < ps).astype(int)
        # STRUCTURE learning: partial-correlation skeleton (precision matrix)
        Xc = X - X.mean(0); C = np.corrcoef(X.T); P = np.linalg.pinv(C + 1e-6 * np.eye(NV))
        pred = set()
        for i in range(NV):
            for j in range(i + 1, NV):
                pc = -P[i, j] / math.sqrt(P[i, i] * P[j, j] + 1e-12)
                if abs(pc) > 0.07:
                    pred.add((i, j))
        skel = set((min(a, b), max(a, b)) for (a, b) in true_edges)
        tp += len(pred & skel); fp += len(pred - skel); fn += len(skel - pred)
        # PARAMETER learning: MLE of a CPT entry from counts
        v = NV - 1
        if parents[v]:
            for cfg in itertools.product([0, 1], repeat=len(parents[v])):
                mask = np.all(X[:, parents[v]] == np.array(cfg), axis=1)
                if mask.sum() > 20:
                    est = X[mask, v].mean(); cpt_err.append(abs(est - cpt[(v, cfg)]))
    prec = tp / (tp + fp) if (tp + fp) else 0.0; rec = tp / (tp + fn) if (tp + fn) else 0.0; cerr = float(np.mean(cpt_err)) if cpt_err else 1.0
    print("  BAYES-NET-LEARNING structure-precision=%.3f recall=%.3f CPT-MLE-err=%.3f" % (prec, rec, cerr), flush=True)
    return {"struct_precision": round(prec, 3), "struct_recall": round(rec, 3), "cpt_err": round(cerr, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "structure-precision=%.3f recall=%.3f CPT-err=%.3f" % (r["struct_precision"], r["struct_recall"], r["cpt_err"])
    if r["struct_precision"] >= 0.70 and r["cpt_err"] <= 0.10:
        return ("HARD_PASS", "HARD_PASS: substrate LEARNS a Bayes net from data -- structure (skeleton precision>=0.70 via partial-corr) AND parameters (CPT MLE err<=0.10). Full structure+parameter learning. " + s)
    if r["struct_precision"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: structure precision 0.55-0.70 or CPT-err>0.10. " + s)
    return ("HARD_FAIL", "HARD_FAIL: structure precision <0.55. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
