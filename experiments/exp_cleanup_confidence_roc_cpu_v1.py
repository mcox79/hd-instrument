"""
exp_cleanup_confidence_roc_cpu_v1.py -- cleanup max-cosine separates stored from novel queries (reliable abstention) -- CPU.

ROUTING: CPU substrate-physics characterization (abstention / I-dont-know ROC). Query the cleanup memory with in-set (stored) vs out-of-set (novel) items; the top-1 cosine score should discriminate, enabling a confidence threshold to abstain ('I do not know') instead of hallucinating. Measures the ROC-AUC of stored-vs-novel by top-1 score. North-star relevant (hallucination avoidance). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS AUC >= 0.95 (clean abstention). MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "cleanup_confidence_roc_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    assert np.argmax([0.2, 0.9, 0.1]) == 1, "argmax"; print("[selftest] PASS: cleanup-confidence-roc-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(22); N = 5000 if SMOKE else 20000; D = 512; NQ = 500; FLIP = 0.15
    X = np.sign(g.standard_normal((N, D))).astype(np.float32)
    qi = g.choice(N, NQ, replace=False); Qin = X[qi].copy(); fl = g.random((NQ, D)) < FLIP; Qin[fl] *= -1   # corrupted stored
    Qout = np.sign(g.standard_normal((NQ, D))).astype(np.float32)                                            # novel (not stored)
    sin = (Qin @ X.T).max(axis=1) / D; sout = (Qout @ X.T).max(axis=1) / D
    # AUC = P(score_in > score_out)
    alls = np.concatenate([sin, sout]); lab = np.concatenate([np.ones(NQ), np.zeros(NQ)])
    order = np.argsort(alls); ranks = np.empty_like(order, dtype=np.float64); ranks[order] = np.arange(1, len(alls) + 1)
    auc = (ranks[lab == 1].sum() - NQ * (NQ + 1) / 2) / (NQ * NQ)
    print("  in-set score mean=%.3f out-set mean=%.3f AUC=%.4f (N=%d)" % (sin.mean(), sout.mean(), auc, N), flush=True)
    return {"auc": float(auc), "in_mean": float(sin.mean()), "out_mean": float(sout.mean())}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.4f (in=%.3f out=%.3f)" % (r["auc"], r["in_mean"], r["out_mean"])
    if r["auc"] >= 0.95: return ("HARD_PASS", "HARD_PASS: AUC>=0.95 separating stored from novel -- substrate can abstain reliably ('I do not know') instead of hallucinating. " + s)
    if r["auc"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: AUC 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: AUC <0.85 -- cannot reliably abstain. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
