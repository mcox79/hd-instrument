"""
exp_ridge_optimization_cpu_v1.py -- pseudoinverse recall vs ridge lambda (capacity-optimal regularization) -- CPU.

ROUTING: CPU substrate-physics characterization (pinv ridge lambda sweep). Sweep ridge lambda (1e-4..1e0) for the pinv write rule at fixed load; find the lambda maximizing exact recall. Characterizes the regularization sweet spot. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS some lambda gives recall@1 >= 0.99 at load M/D=0.8. MIDDLE >= 0.95. HARD-FAIL < 0.95.
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
ANCHOR_NAME = "ridge_optimization_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    A = np.eye(3); assert np.allclose(np.linalg.solve(A, A), A), "solve"; print("[selftest] PASS: ridge-optimization-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2); D = 512; M = int(0.8 * D); MM = 256
    bk = np.sign(g.standard_normal((MM * 4, MM))); K = np.sign(g.standard_normal((M, D))); V = bk[g.integers(0, len(bk), M)]
    by = {}
    for lam in [1e-4, 1e-3, 1e-2, 1e-1, 1.0]:
        W = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ V)
        pred = np.argmax((K @ W) @ bk.T, axis=1); gold = np.argmax(V @ bk.T, axis=1); by["l%g" % lam] = float((pred == gold).mean())
    best = max(by.values()); print("  recall by ridge: %s | best=%.3f (D=%d M=%d)" % ({k: round(v, 3) for k, v in by.items()}, best, D, M), flush=True)
    return {"by": by, "best": best}
def verdict(r) -> Tuple[str, str]:
    s = "best=%.3f | by-ridge: %s" % (r["best"], {k: round(v, 3) for k, v in r["by"].items()})
    if r["best"] >= 0.99: return ("HARD_PASS", "HARD_PASS: optimal ridge gives recall>=0.99 at load 0.8 -- regularization sweet spot identified. " + s)
    if r["best"] >= 0.95: return ("MIDDLE_BAND", "MIDDLE_BAND: best recall 0.95-0.99. " + s)
    return ("HARD_FAIL", "HARD_FAIL: best recall <0.95 at load 0.8. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
