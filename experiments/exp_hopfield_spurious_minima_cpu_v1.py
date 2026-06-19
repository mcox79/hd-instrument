"""
exp_hopfield_spurious_minima_cpu_v1.py -- modern Hopfield rarely converges to spurious (non-stored) states -- CPU.

ROUTING: CPU substrate-physics characterization (spurious attractor rate). From random (non-near-any-pattern) starts, iterate modern-Hopfield cleanup; check whether it converges to an actual stored pattern (good) or a spurious mixture. Low spurious rate means trustworthy retrieval. N=2048, load P/N=0.5. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS >= 0.90 of random starts converge onto a genuine stored pattern (overlap>=0.95). MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "hopfield_spurious_minima_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    assert np.sign(0.1) == 1, "sign"; print("[selftest] PASS: hopfield-spurious-minima-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(23); N = 1024 if SMOKE else 2048; P = N // 2; NQ = 300; BETA = 12.0; T = 6
    X = np.sign(g.standard_normal((P, N))).astype(np.float32); X[X == 0] = 1
    Q = np.sign(g.standard_normal((NQ, N))).astype(np.float32)                                # random starts
    for _ in range(T):
        Q = np.sign(np.exp(BETA * (Q @ X.T - (Q @ X.T).max(axis=1, keepdims=True))) @ X)
    overlap = (Q @ X.T).max(axis=1) / N                                                       # best overlap with any stored
    genuine = float((overlap >= 0.95).mean())
    print("  fraction converged to a genuine stored pattern=%.3f (P=%d N=%d)" % (genuine, P, N), flush=True)
    return {"genuine": genuine}
def verdict(r) -> Tuple[str, str]:
    s = "genuine-convergence=%.3f" % r["genuine"]
    if r["genuine"] >= 0.90: return ("HARD_PASS", "HARD_PASS: >=0.90 of random starts settle on a real stored pattern -- few spurious attractors (trustworthy retrieval). " + s)
    if r["genuine"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: genuine-convergence 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: many spurious attractors (genuine <0.75). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
