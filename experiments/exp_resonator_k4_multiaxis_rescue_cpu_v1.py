"""
exp_resonator_k4_multiaxis_rescue_cpu_v1.py -- resonator K=4 factorization rescue via N up + M down + more iterations -- CPU.

ROUTING: v1.5 LOCK batch (F2 resonator K=4 multi-axis rescue). K=4 resonator factorization was HARD_FAIL (~0.5 at N=4096). Multi-axis rescue: larger N=16384, smaller codebook M=15, more iterations (200), and codebook-mean init. Tests whether combined axes lift K=4 full-factorization to a usable level. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS K=4 full-factorization success >= 0.85. MIDDLE >= 0.65. HARD-FAIL < 0.65.
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
ANCHOR_NAME = "resonator_k4_multiaxis_rescue_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; b = cphasor(1, 32, g)[0]; assert np.allclose(a * b * np.conj(b), a, atol=1e-3), "bind"; print("[selftest] PASS: resonator-k4-multiaxis-rescue", flush=True)
def run() -> Dict:
    g = np.random.default_rng(84); N = 8192 if SMOKE else 16384; M = 15; K = 4; MAXIT = 200; TR = 25 if SMOKE else 80
    succ = 0
    for _ in range(TR):
        books = [cphasor(M, N, g) for _ in range(K)]
        true = [int(g.integers(0, M)) for _ in range(K)]
        s = np.ones(N, dtype=np.complex64)
        for k in range(K):
            s = s * books[k][true[k]]
        est = [b.mean(0) for b in books]; est = [e / (np.abs(e) + 1e-8) for e in est]; prev = None
        for _ in range(MAXIT):
            idxs = []
            for k in range(K):
                others = np.ones(N, dtype=np.complex64)
                for j in range(K):
                    if j != k:
                        others = others * est[j]
                rr = s * np.conj(others); sc = books[k] @ np.conj(rr); est[k] = (sc @ books[k]); est[k] = est[k] / (np.abs(est[k]) + 1e-8)
                idxs.append(int(np.argmax(sc.real)))
            if idxs == prev:
                break
            prev = idxs
        succ += int(idxs == true)
    rec = succ / TR; print("  K=4 full-factorization success=%.3f (N=%d M=%d iters<=%d)" % (rec, N, M, MAXIT), flush=True)
    return {"recall": rec, "N": N}
def verdict(r) -> Tuple[str, str]:
    s = "K=4 success=%.3f at N=%d" % (r["recall"], r["N"])
    if r["recall"] >= 0.85: return ("HARD_PASS", "HARD_PASS: multi-axis rescue lifts K=4 resonator factorization to >=0.85 -- 4-factor disentangling is usable at N=16384/M=15. " + s)
    if r["recall"] >= 0.65: return ("MIDDLE_BAND", "MIDDLE_BAND: K=4 0.65-0.85 (improved; 4-factor near limit). " + s)
    return ("HARD_FAIL", "HARD_FAIL: K=4 <0.65 even multi-axis -- 4-factor joint disentangling is a hard limit. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
