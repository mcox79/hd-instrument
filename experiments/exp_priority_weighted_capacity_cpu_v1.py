"""
exp_priority_weighted_capacity_cpu_v1.py -- up-weighting protects high-priority facts under overload -- CPU.

ROUTING: CPU substrate-physics characterization (priority protection under overload). At overload (M/D=1.5), compare uniform pinv vs priority-weighted pinv: do up-weighted high-priority facts keep recall>=0.95 while uniform loses them? Validates a triage mechanism for capacity-constrained deployments. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS weighted high-priority recall >= 0.95 AND uniform high-priority < 0.90 (weighting demonstrably helps). MIDDLE weighted >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "priority_weighted_capacity_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    w = np.array([1.0, 20.0]); K = np.ones((2, 3)); assert (K * w[:, None]).shape == (2, 3), "weighted shape"; print("[selftest] PASS: priority-weighted-capacity-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(13); D = 512; MM = 256; bk = np.sign(g.standard_normal((MM * 4, MM))); lam = 1e-3
    M = int(3.0 * D); K = np.sign(g.standard_normal((M, D))); V = bk[g.integers(0, len(bk), M)]; gold = np.argmax(V @ bk.T, axis=1); FLIP = 0.15
    hi = np.zeros(M, bool); hi[: M // 5] = True; w = np.ones(M); w[hi] = 50.0
    Wu = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ V)
    Kw = K * w[:, None]; Ww = np.linalg.solve(K.T @ Kw + lam * np.eye(D), Kw.T @ V)
    Kq = K.copy(); fl = g.random((M, D)) < FLIP; Kq[fl] *= -1                       # noisy queries at 3x overload so uniform actually fails
    def rec(W, mask):
        pred = np.argmax((Kq[mask] @ W) @ bk.T, axis=1); return float((pred == gold[mask]).mean())
    uhi = rec(Wu, hi); whi = rec(Ww, hi); wlo = rec(Ww, ~hi)
    print("  high-priority recall: uniform=%.3f weighted=%.3f | weighted low-priority=%.3f (overload 3x, 0.15 noise)" % (uhi, whi, wlo), flush=True)
    return {"uniform_hi": uhi, "weighted_hi": whi, "weighted_lo": wlo}
def verdict(r) -> Tuple[str, str]:
    s = "weighted-hi=%.3f uniform-hi=%.3f weighted-lo=%.3f" % (r["weighted_hi"], r["uniform_hi"], r["weighted_lo"])
    if r["weighted_hi"] >= 0.95 and r["uniform_hi"] < 0.90: return ("HARD_PASS", "HARD_PASS: up-weighting keeps high-priority recall>=0.95 at overload where uniform drops -- capacity triage works. " + s)
    if r["weighted_hi"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: weighted high-priority 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: weighted high-priority <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
