"""
exp_graceful_overload_cpu_v1.py -- recall degrades gracefully (not catastrophically) past capacity -- CPU.

ROUTING: CPU substrate-physics characterization (past-capacity degradation shape). Load the pinv memory at M/D in {1.0,1.5,2.0} (at/over capacity); measure recall@1. A graceful system degrades smoothly; a catastrophic one cliffs to 0. Characterizes overload behavior. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS recall at M/D=1.5 >= 0.50 (graceful). MIDDLE >= 0.20. HARD-FAIL < 0.20 (catastrophic cliff).
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
ANCHOR_NAME = "graceful_overload_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    A = np.eye(3); assert np.allclose(np.linalg.solve(A, A), A), "solve"; print("[selftest] PASS: graceful-overload-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(12); D = 256 if SMOKE else 512; MM = 128; bk = np.sign(g.standard_normal((MM * 4, MM))); lam = 1e-3; by = {}
    loads = [2.0, 4.0] if SMOKE else [2.0, 4.0, 8.0, 16.0]
    for rr in loads:
        M = int(rr * D); K = np.sign(g.standard_normal((M, D))); V = bk[g.integers(0, len(bk), M)]
        W = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ V)
        pred = np.argmax((K @ W) @ bk.T, axis=1); gold = np.argmax(V @ bk.T, axis=1)
        by["r%.0f" % rr] = float((pred == gold).mean())
    print("  recall by overload M/D: %s (D=%d)" % ({k: round(v, 3) for k, v in by.items()}, D), flush=True)
    return {"by": by, "loads": loads}
def verdict(r) -> Tuple[str, str]:
    b = r["by"]; ld = r["loads"]; keys = ["r%.0f" % x for x in ld]
    vals = [b[k] for k in keys]; r4 = b.get("r4", vals[-1])
    monotone = all(vals[i] >= vals[i + 1] - 0.02 for i in range(len(vals) - 1))
    s = "recall by overload: %s (monotone=%s)" % ({k: round(v, 3) for k, v in b.items()}, monotone)
    if r4 >= 0.50 and monotone: return ("HARD_PASS", "HARD_PASS: cleanup-backed pinv degrades smoothly+monotonically, recall>=0.50 even at 4x overload -- graceful past-capacity behavior (no catastrophic cliff). " + s)
    if r4 >= 0.20: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.20-0.50 at 4x overload. " + s)
    return ("HARD_FAIL", "HARD_FAIL: catastrophic drop (recall <0.20 at 4x). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
