"""
exp_sparse_hopfield_v1.py -- sparse (top-k) Hopfield retrieval matches softmax with interpretable support -- CPU.

ROUTING: field_modern_hopfield finding 4 (sparse Hopfield / sparsemax). Replace softmax attention with sparse top-k attention (sparsemax analog): keep only the top-k stored patterns by score, renormalize. Compare recall@1 + support size to dense softmax. Sparse retrieval = exact-zero, auditable attention. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS sparse recall@1 >= softmax recall - 0.02 at top-k=5 (sparsity with no recall loss). MIDDLE within 0.05. HARD-FAIL sparse loses > 0.05.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "sparse_hopfield_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def softmax(x):
    x = x - x.max(axis=-1, keepdims=True); e = np.exp(x); return e / e.sum(axis=-1, keepdims=True)
def _selftest():
    sm = softmax(np.array([[1.0, 2.0, 3.0]])); assert abs(sm.sum() - 1.0) < 1e-9, "softmax norm"
    a = np.array([0.1, 0.9, 0.5]); k = np.argsort(a)[::-1][:2]; assert set(k.tolist()) == {1, 2}, "top-k"
    assert np.sign(0.3) == 1, "sign"
    print("[selftest] PASS: sparse-hopfield", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2); N = 256; P = N; FLIP = 0.15; NQ = 200; BETA = 8.0; TOPK = 5
    X = np.sign(g.standard_normal((P, N))).astype(np.float64)
    qi = g.choice(P, min(NQ, P), replace=False); Q = X[qi].copy(); fl = g.random(Q.shape) < FLIP; Q[fl] *= -1
    sc = BETA * (Q @ X.T)
    dense = softmax(sc) @ X; rd = float(((np.sign(dense) * X[qi]).sum(1) / N >= 0.95).mean())
    # sparse: keep top-k scores per query, softmax over them only
    att = np.zeros_like(sc)
    for i in range(sc.shape[0]):
        idx = np.argsort(sc[i])[::-1][:TOPK]; att[i, idx] = softmax(sc[i, idx][None, :])[0]
    sparse = att @ X; rs = float(((np.sign(sparse) * X[qi]).sum(1) / N >= 0.95).mean())
    print("  dense recall@1=%.3f sparse(top-%d) recall@1=%.3f (delta=%.3f)" % (rd, TOPK, rs, rd - rs), flush=True)
    return {"dense": rd, "sparse": rs, "delta": rd - rs, "topk": TOPK}
def verdict(r) -> Tuple[str, str]:
    s = "dense=%.3f sparse=%.3f delta=%.3f (top-%d)" % (r["dense"], r["sparse"], r["delta"], r["topk"])
    if r["delta"] <= 0.02: return ("HARD_PASS", "HARD_PASS: sparse top-k Hopfield matches softmax within 0.02 -- exact-zero interpretable attention with no recall loss. " + s)
    if r["delta"] <= 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: sparse within 0.05 of dense. " + s)
    return ("HARD_FAIL", "HARD_FAIL: sparse loses >0.05 recall. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
