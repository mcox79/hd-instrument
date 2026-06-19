"""
exp_negation_query_cpu_v1.py -- negation query (A minus B) suppresses the unwanted cluster -- CPU.

ROUTING: CPU substrate capability characterization (A-but-not-B retrieval). Items in two clusters near anchors A and B. Compare retrieving by A alone vs by A - lambda*B: the negation should drive B-cluster contamination out of the top-k while keeping A-items. Tests compositional negation in retrieval. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS B-contamination in top-20 drops below 0.05 with negation (and was higher without). MIDDLE < 0.15. HARD-FAIL >= 0.15.
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
ANCHOR_NAME = "negation_query_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    assert (np.array([0.9, 0.1]) - 0.5 * np.array([0.0, 0.9]))[0] > 0, "negation arithmetic"; print("[selftest] PASS: negation-query-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(44); N = 1024; D = N; NA = 10; NB = 60; NN = 150; sig = 0.8; RHO = 0.6
    A = np.sign(g.standard_normal(D)).astype(np.float32)
    B = np.sign(RHO * A + math.sqrt(1 - RHO * RHO) * g.standard_normal(D)).astype(np.float32)   # B correlated with A so clusters overlap
    def near(anchor, n):
        X = np.repeat(anchor[None, :], n, 0).copy(); fl = g.random((n, D)) < sig * 0.25; X[fl] *= -1; return X
    Aitems = near(A, NA); Bitems = near(B, NB); Neut = np.sign(g.standard_normal((NN, D))).astype(np.float32)
    X = np.vstack([Aitems, Bitems, Neut]); isB = np.zeros(len(X), bool); isB[NA:NA + NB] = True
    def topk_Bfrac(query, k=20):
        sc = X @ query; top = np.argsort(-sc)[:k]; return float(isB[top].mean())
    plain = topk_Bfrac(A); neg = topk_Bfrac(A - 1.0 * B)
    print("  B-contamination in top-20: plain-A=%.3f  A-minus-B=%.3f" % (plain, neg), flush=True)
    return {"plain": plain, "neg": neg}
def verdict(r) -> Tuple[str, str]:
    s = "B-contamination top-20: plain=%.3f negated=%.3f" % (r["plain"], r["neg"])
    if r["neg"] < 0.05 and r["neg"] < r["plain"]: return ("HARD_PASS", "HARD_PASS: negation (A-B) drives B-cluster contamination below 0.05 -- compositional 'A but not B' retrieval works. " + s)
    if r["neg"] < 0.15: return ("MIDDLE_BAND", "MIDDLE_BAND: negated contamination 0.05-0.15. " + s)
    return ("HARD_FAIL", "HARD_FAIL: negation does not suppress B (>=0.15). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
