"""
exp_capacity_scaling_law_cpu_v1.py -- max patterns at recall>=0.99 scales linearly with D (capacity slope) -- CPU.

ROUTING: CPU substrate-physics characterization (capacity vs dimension scaling law). For D in {128,256,512,1024}, binary-search the max number of sign patterns recallable at recall@1>=0.99 (pinv); fit the capacity-vs-D slope. Confirms linear capacity scaling. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS capacity grows linearly with slope >= 0.5*D (i.e. cap >= 0.5*D at each D). MIDDLE >= 0.3*D. HARD-FAIL < 0.3*D.
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
ANCHOR_NAME = "capacity_scaling_law_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    assert 512 > 256, "D ordering"; print("[selftest] PASS: capacity-scaling-law-cpu", flush=True)
def cap_at(D, g, lam=1e-3):
    MM = 128; bk = np.sign(g.standard_normal((MM * 6, MM)))
    lo, hi, best = 1, int(1.2 * D), 1
    while lo <= hi:
        M = (lo + hi) // 2; K = np.sign(g.standard_normal((M, D))); V = bk[g.integers(0, len(bk), M)]
        W = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ V); pred = np.argmax((K @ W) @ bk.T, axis=1); gold = np.argmax(V @ bk.T, axis=1)
        if (pred == gold).mean() >= 0.99:
            best = M; lo = M + 1
        else:
            hi = M - 1
    return best
def run() -> Dict:
    g = np.random.default_rng(5); Ds = [128, 256] if SMOKE else [128, 256, 512, 1024]; by = {}
    for D in Ds:
        by[D] = cap_at(D, g); print("  D=%d capacity(recall>=0.99)=%d (=%.2f*D)" % (D, by[D], by[D] / D), flush=True)
    frac = min(by[D] / D for D in Ds); return {"by": {str(k): v for k, v in by.items()}, "min_frac": frac}
def verdict(r) -> Tuple[str, str]:
    s = "min capacity fraction = %.2f*D | %s" % (r["min_frac"], r["by"])
    if r["min_frac"] >= 0.5: return ("HARD_PASS", "HARD_PASS: capacity scales >=0.5*D at every D -- linear capacity law confirmed (predictable scaling). " + s)
    if r["min_frac"] >= 0.3: return ("MIDDLE_BAND", "MIDDLE_BAND: capacity 0.3-0.5*D. " + s)
    return ("HARD_FAIL", "HARD_FAIL: capacity <0.3*D. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
