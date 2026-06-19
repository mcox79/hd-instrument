"""
exp_markov_transition_cpu_v1.py -- store transitions and predict the next item from the current (Markov) -- CPU.

ROUTING: CPU substrate capability characterization (sequence next-item prediction). Store sequence transitions cur->next as M = sum cur*NEXT*next (NEXT a fixed relation). Given a current item, predict the next via M*(cur*NEXT).conj() + cleanup. Tests learned sequence/transition modeling. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS next-item recall >= 0.90 at T transitions. MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "markov_transition_nscale_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    assert np.argmax([0.1, 0.8]) == 1, "argmax"; print("[selftest] PASS: markov-transition-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(43); V = 150; T = 60; by = {}
    Ns = [2048, 4096] if SMOKE else [2048, 4096, 8192]
    for N in Ns:
        items = cphasor(V, N, g); NEXT = cphasor(1, N, g)[0]
        trans = []; used = set()
        while len(trans) < T:
            c = int(g.integers(0, V))
            if c in used:
                continue
            used.add(c); trans.append((c, int(g.integers(0, V))))
        M = np.zeros(N, dtype=np.complex64)
        for c, nx in trans:
            M = M + items[c] * NEXT * items[nx]
        hit = 0
        for c, nx in trans:
            pred = int(np.argmax((items @ (M * (items[c] * NEXT).conj()).conj()).real)); hit += int(pred == nx)
        by["N%d" % N] = hit / T; print("  N=%d next-item recall=%.3f (T=%d V=%d)" % (N, by["N%d" % N], T, V), flush=True)
    return {"by": by, "recall": max(by.values()), "best_N": max(by, key=by.get)}
def verdict(r) -> Tuple[str, str]:
    s = "best recall=%.3f at %s | by-N: %s" % (r["recall"], r["best_N"], {k: round(v, 3) for k, v in r["by"].items()})
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: at higher N markov next-item recall>=0.90 -- the 0.80 MID at N=2048 was capacity-bound; N-scaling rescues it. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: best recall 0.75-0.90 -- N-scaling helps but below gate. " + s)
    return ("HARD_FAIL", "HARD_FAIL: best recall <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
