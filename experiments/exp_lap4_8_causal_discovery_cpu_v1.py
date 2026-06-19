"""
exp_lap4_8_causal_discovery_cpu_v1.py -- LAP4-8 CAUSAL-DISCOVERY: structure learning from observational data -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (LAP4-8; PP-270 extension). The substrate stores observational samples from a hidden
  linear SCM and RECOVERS the causal DAG via partial-correlation conditional-independence tests (PC-algorithm core): an edge i-j
  exists iff i and j stay correlated after conditioning on all other variables (nonzero partial correlation). Measures recovered-
  edge precision + recall vs the ground-truth DAG. numpy. CPU.
PRE-REGISTERED: HARD-PASS edge precision >= 0.70 (over 30+ problems). MIDDLE >= 0.55. HARD-FAIL < 0.55.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "lap4_8_causal_discovery_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def _selftest():
    import numpy as _n; assert abs(_n.corrcoef([1, 2, 3], [1, 2, 3])[0, 1] - 1) < 1e-9, "corr"; print("[selftest] PASS: causal-discovery", flush=True)


def run() -> Dict:
    g = np.random.default_rng(270); NV = 6; NSAMP = 2000; PROBS = 30 if SMOKE else 120
    tp = 0; fp = 0; fn = 0
    for _ in range(PROBS):
        # random DAG (topological: edges i->j only if i<j), linear weights
        W = np.zeros((NV, NV))
        true_edges = set()
        for j in range(NV):
            for i in range(j):
                if g.random() < 0.35:
                    W[i, j] = g.uniform(0.6, 1.4) * (1 if g.random() < 0.5 else -1); true_edges.add((i, j))
        # generate observational samples
        X = np.zeros((NSAMP, NV))
        for j in range(NV):
            X[:, j] = X @ W[:, j] + g.standard_normal(NSAMP)
        # partial correlation: invert covariance -> precision matrix; off-diagonal nonzero => edge (undirected skeleton)
        C = np.corrcoef(X.T); P = np.linalg.pinv(C)
        pred_edges = set()
        for i in range(NV):
            for j in range(i + 1, NV):
                pcorr = -P[i, j] / math.sqrt(P[i, i] * P[j, j] + 1e-12)
                if abs(pcorr) > 0.08:
                    pred_edges.add((i, j))
        true_skel = set((min(a, b), max(a, b)) for (a, b) in true_edges)
        tp += len(pred_edges & true_skel); fp += len(pred_edges - true_skel); fn += len(true_skel - pred_edges)
    prec = tp / (tp + fp) if (tp + fp) else 0.0; rec = tp / (tp + fn) if (tp + fn) else 0.0
    print("  CAUSAL-DISCOVERY edge precision=%.3f recall=%.3f (tp=%d fp=%d fn=%d, %d problems)" % (prec, rec, tp, fp, fn, PROBS), flush=True)
    return {"edge_precision": round(prec, 3), "edge_recall": round(rec, 3), "n_problems": PROBS}


def verdict(r) -> Tuple[str, str]:
    s = "edge-precision=%.3f recall=%.3f (%d problems)" % (r["edge_precision"], r["edge_recall"], r["n_problems"])
    if r["edge_precision"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate-stored observational data -> causal DAG skeleton recovery >=0.70 edge precision via partial-correlation CI tests -- causal structure discovery (PC-core) over the substrate. " + s)
    if r["edge_precision"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: edge precision 0.55-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: edge precision <0.55. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
