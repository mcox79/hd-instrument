"""
exp_subspace_storage_capacity_cpu_v1.py -- storing keys in a d-dim random subspace scales capacity with d -- CPU.

ROUTING: CPU substrate-physics characterization (random-subspace storage). Confine keys to a random d-dimensional subspace of R^D (d < D); measure max patterns at recall>=0.99. Tests whether effective capacity follows the subspace dimension d (not the ambient D) -- relevant to projected/compressed key designs. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS capacity scales with d (cap(d=D/2) approx 0.5x cap(d=D), within 30pct). MIDDLE within 50pct. HARD-FAIL otherwise.
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
ANCHOR_NAME = "subspace_storage_capacity_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    g = np.random.default_rng(0); B, _ = np.linalg.qr(g.standard_normal((8, 4))); assert B.shape == (8, 4), "basis"; print("[selftest] PASS: subspace-storage-capacity-cpu", flush=True)
def cap_sub(D, d, g, lam=1e-3):
    MM = 128; bk = np.sign(g.standard_normal((MM * 6, MM))); B, _ = np.linalg.qr(g.standard_normal((D, d)))    # D x d orthonormal basis
    lo, hi, best = 1, int(1.3 * d), 1
    while lo <= hi:
        M = (lo + hi) // 2; coords = g.standard_normal((M, d)); K = np.sign(coords @ B.T); V = bk[g.integers(0, len(bk), M)]
        W = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ V); pred = np.argmax((K @ W) @ bk.T, axis=1); gold = np.argmax(V @ bk.T, axis=1)
        if (pred == gold).mean() >= 0.99:
            best = M; lo = M + 1
        else:
            hi = M - 1
    return best
def run() -> Dict:
    g = np.random.default_rng(26); D = 256 if SMOKE else 512
    full = cap_sub(D, D, g); half = cap_sub(D, D // 2, g); ratio = half / (full + 1e-9)
    print("  cap(d=D)=%d cap(d=D/2)=%d ratio=%.2f (expect ~0.5, D=%d)" % (full, half, ratio, D), flush=True)
    return {"full": full, "half": half, "ratio": ratio}
def verdict(r) -> Tuple[str, str]:
    dev = abs(r["ratio"] - 0.5) / 0.5; s = "cap-ratio(half/full)=%.2f (cap_full=%d cap_half=%d)" % (r["ratio"], r["full"], r["half"])
    if dev <= 0.30: return ("HARD_PASS", "HARD_PASS: capacity scales with subspace dim d (half-subspace approx half-capacity) -- effective capacity follows d not ambient D (projected-key designs predictable). " + s)
    if dev <= 0.50: return ("MIDDLE_BAND", "MIDDLE_BAND: subspace ratio within 50pct of 0.5. " + s)
    return ("HARD_FAIL", "HARD_FAIL: subspace capacity does not track d. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
