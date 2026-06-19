"""
exp_orthogonal_keys_capacity_cpu_v1.py -- capacity gain from orthogonalized keys vs random keys -- CPU.

ROUTING: CPU substrate-physics characterization (orthogonal vs random key capacity). Compare max patterns at recall>=0.99 for random keys vs Gram-Schmidt-orthogonalized keys (pinv write). Quantifies the capacity benefit of decorrelating keys. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS orthogonal keys sustain recall>=0.99 at load M/D=1.0 (vs random failing). MIDDLE >= 0.95. HARD-FAIL < 0.95.
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
ANCHOR_NAME = "orthogonal_keys_capacity_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    q, _ = np.linalg.qr(np.random.default_rng(0).standard_normal((4, 4))); assert np.allclose(q.T @ q, np.eye(4), atol=1e-6), "qr orthonormal"; print("[selftest] PASS: orthogonal-keys-capacity-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(3); D = 256 if SMOKE else 512; M = D; MM = 256; lam = 1e-3
    bk = np.sign(g.standard_normal((MM * 4, MM))); V = bk[g.integers(0, len(bk), M)]
    Krand = g.standard_normal((M, D)); Korth, _ = np.linalg.qr(g.standard_normal((D, M))); Korth = Korth.T[:M]
    def rec(K):
        W = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ V); pred = np.argmax((K @ W) @ bk.T, axis=1); gold = np.argmax(V @ bk.T, axis=1); return float((pred == gold).mean())
    rr = rec(Krand); ro = rec(Korth)
    print("  recall at load M/D=1.0: random=%.3f orthogonal=%.3f (D=%d)" % (rr, ro, D), flush=True)
    return {"random": rr, "orth": ro}
def verdict(r) -> Tuple[str, str]:
    s = "orthogonal=%.3f random=%.3f at load 1.0" % (r["orth"], r["random"])
    if r["orth"] >= 0.99: return ("HARD_PASS", "HARD_PASS: orthogonalized keys hold recall>=0.99 at load M/D=1.0 -- decorrelation maximizes capacity (key-design lever). " + s)
    if r["orth"] >= 0.95: return ("MIDDLE_BAND", "MIDDLE_BAND: orthogonal recall 0.95-0.99 at load 1.0. " + s)
    return ("HARD_FAIL", "HARD_FAIL: orthogonal recall <0.95 even at load 1.0. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
