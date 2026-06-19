"""
exp_topk_recall_cpu_v1.py -- top-k recall recovers the true item even when top-1 fails -- CPU.

ROUTING: CPU substrate capability characterization (recall@k under heavy noise). Measure recall@k (k=1,5,10) for sign-key queries under heavy bit-flip (0.20,0.35); even when top-1 misses, the true item should sit in the top-k -- supports a re-rank/verify stage. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS recall@5 >= 0.95 at 0.35 bit-flip. MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "topk_recall_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    a = np.array([3, 1, 2]); assert set(np.argsort(-a)[:2].tolist()) == {0, 2}, "topk"; print("[selftest] PASS: topk-recall-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(31); N = 5000 if SMOKE else 20000; D = 512; NQ = 400; by = {}
    X = np.sign(g.standard_normal((N, D))).astype(np.float32); qi = g.choice(N, NQ, replace=False)
    for flip in [0.20, 0.35]:
        Q = X[qi].copy(); fl = g.random((NQ, D)) < flip; Q[fl] *= -1; sc = Q @ X.T; ordr = np.argsort(-sc, axis=1)
        for k in [1, 5, 10]:
            topk = ordr[:, :k]; hit = float(np.mean([qi[i] in topk[i] for i in range(NQ)])); by["f%.2f_k%d" % (flip, k)] = hit
    print("  recall@k: %s" % {k: round(v, 3) for k, v in by.items()}, flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    r5 = r["by"].get("f0.35_k5", 0.0); s = "recall@k: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if r5 >= 0.95: return ("HARD_PASS", "HARD_PASS: recall@5>=0.95 even at 0.35 bit-flip -- a cheap re-rank stage recovers what top-1 misses. " + s)
    if r5 >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: recall@5 0.85-0.95 at 0.35 flip. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall@5 <0.85 at 0.35 flip. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
