"""
exp_rrf_fusion_cpu_v1.py -- RRF fusion of two noisy rankers beats either alone -- CPU.

ROUTING: hybrid-architecture / KG-QA mechanism (H2 reciprocal-rank fusion). Two independent noisy rankings of the same gold set (e.g. a fuzzy retriever + a native retriever, each with its own errors); reciprocal-rank fusion (sum 1/(k+rank)) combines them. Tests whether fusion recall@10 exceeds the best single ranker. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS RRF recall@10 >= 1.2x the best single ranker. MIDDLE >= best single. HARD-FAIL < best single.
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
ANCHOR_NAME = "rrf_fusion_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg); alls = np.concatenate([pos, neg]); lab = np.concatenate([np.ones(len(pos)), np.zeros(len(neg))])
    order = np.argsort(alls); ranks = np.empty_like(order, dtype=np.float64); ranks[order] = np.arange(1, len(alls) + 1)
    return float((ranks[lab == 1].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg) + 1e-9))

def _selftest():
    assert 1.0 / (60 + 1) > 1.0 / (60 + 5), "rrf rank weighting"; print("[selftest] PASS: rrf-fusion", flush=True)
def run() -> Dict:
    g = np.random.default_rng(52); V = 500; GOLD = 20; TR = 60 if SMOKE else 200; KRRF = 60; krecall = 10
    rA = []; rB = []; rF = []
    for _ in range(TR):
        gold = set(g.choice(V, GOLD, replace=False).tolist())
        truth = np.zeros(V); truth[list(gold)] = 1.0
        sA = truth + 1.3 * g.standard_normal(V); sB = truth + 1.3 * g.standard_normal(V)   # two noisy rankers
        ordA = np.argsort(-sA); ordB = np.argsort(-sB)
        rankA = np.empty(V); rankA[ordA] = np.arange(V); rankB = np.empty(V); rankB[ordB] = np.arange(V)
        fused = 1.0 / (KRRF + rankA) + 1.0 / (KRRF + rankB); ordF = np.argsort(-fused)
        def rec(order):
            return len(set(order[:krecall].tolist()) & gold) / GOLD
        rA.append(rec(ordA)); rB.append(rec(ordB)); rF.append(rec(ordF))
    a, b, f = float(np.mean(rA)), float(np.mean(rB)), float(np.mean(rF)); best = max(a, b)
    print("  recall@10: rankerA=%.3f rankerB=%.3f RRF=%.3f (RRF/best=%.2f)" % (a, b, f, f / (best + 1e-9)), flush=True)
    return {"A": a, "B": b, "fused": f, "ratio": f / (best + 1e-9)}
def verdict(r) -> Tuple[str, str]:
    s = "RRF=%.3f vs best-single=%.3f (ratio=%.2f)" % (r["fused"], max(r["A"], r["B"]), r["ratio"])
    if r["ratio"] >= 1.2: return ("HARD_PASS", "HARD_PASS: RRF fusion recall@10 >=1.2x best single ranker -- hybrid parallel fusion adds real recall. " + s)
    if r["ratio"] >= 1.0: return ("MIDDLE_BAND", "MIDDLE_BAND: RRF >= best single but <1.2x. " + s)
    return ("HARD_FAIL", "HARD_FAIL: RRF worse than best single. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
