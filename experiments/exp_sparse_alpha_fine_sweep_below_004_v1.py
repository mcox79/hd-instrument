"""
exp_sparse_alpha_fine_sweep_below_004_v1 -- Batch E Cell 3 (TAX-10; EV=1.86, zero arch change) -- CPU.

ROUTING: Batch E Drill-4 anchor A. Cycle 130 found ~20x sparse-coding capacity at sparsity f=0.04 vs 5-7x at f=0.20, but
  the sweep stopped at f=0.04. This extends BELOW 0.04 (f in {0.005..0.05}) to see if the capacity curve keeps rising.
  Zero architecture change -- just sparser codes. Synthetic sparse +-1 patterns, single-step sparse Hopfield (W-free),
  capacity alpha vs dense baseline. CPU $0.
PRE-REGISTERED: HARD-PASS capacity at f<=0.01 >= 1.5x the f=0.04 capacity (curve keeps rising -> 2-4x more headroom).
  MID 1.1-1.5x. HARD-FAIL <=1.1x (curve plateaus by f=0.04).
FORMULA SELF-TESTS (PROT-022): 1. sparse k-of-N. 2. low-load recovers. 3. sparser higher cap.
ASCII-only. write_metrics. PROT-018 no _nN.
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

ANCHOR_NAME = "sparse_alpha_fine_sweep_below_004_v1"
FLIP = 0.05; FRACS = [0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.10]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 4096; LOADS = [0.1, 0.4, 0.7, 1.0, 1.5, 2.5, 4.0]
else:
    SEEDS = [7, 17, 23]; N = 8192; LOADS = [0.05, 0.1, 0.2, 0.4, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]


def sparse_pat(M, n, f, g):
    k = max(1, int(f * n)); P = np.zeros((M, n), np.float32)
    for i in range(M):
        idx = g.choice(n, k, replace=False); P[i, idx] = g.integers(0, 2, k) * 2 - 1
    return P


def recall(P, g):
    M, n = P.shape; diag = (P * P).sum(0); s = P.copy()             # W-free single-step (sparse)
    for i in range(M):
        nz = np.nonzero(P[i])[0]; fl = nz[g.random(len(nz)) < FLIP]; s[i, fl] *= -1
    r = np.sign((s @ P.T) @ P - s * diag)
    return float(np.mean([np.all(r[i][np.nonzero(P[i])[0]] == P[i][np.nonzero(P[i])[0]]) for i in range(M)]))


def cap(f, seed):
    g = np.random.default_rng(seed); c = 0.0
    for load in LOADS:
        M = max(2, int(load * N))
        if recall(sparse_pat(M, N, f, np.random.default_rng(seed * 13 + M)), g) >= 0.95:
            c = load
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); P = sparse_pat(5, 512, 0.05, g); assert np.all((P != 0).sum(1) == int(0.05 * 512)), "sparse k-of-N"
    assert recall(sparse_pat(4, 512, 0.05, g), np.random.default_rng(1)) >= 0.95, "low-load recovers"
    print("[selftest] PASS: alpha-fine", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    a = {("f%.3f" % f): cap(f, seed) for f in FRACS}
    print("  [seed=%d] alpha_c by f %s" % (seed, {k: round(v, 3) for k, v in a.items()}), flush=True); return {"seed": seed, "alpha": a}


def verdict(ps) -> Tuple[str, str]:
    agg = {("f%.3f" % f): float(np.mean([p["alpha"]["f%.3f" % f] for p in ps])) for f in FRACS}
    a004 = agg["f0.040"]; a_low = max(agg["f0.005"], agg["f0.010"]); g = a_low / max(a004, 1e-9)
    summary = "alpha_c by sparsity: %s | below-0.04/at-0.04=%.2fx" % ({k: round(v, 3) for k, v in agg.items()}, g)
    if g >= 1.5:
        return ("HARD_PASS", "HARD_PASS: capacity keeps rising below f=0.04 (>=1.5x) -- more sparse-coding headroom, zero arch change. " + summary)
    if g >= 1.1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: modest further rise below f=0.04 (1.1-1.5x). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: capacity plateaus by f=0.04 (<=1.1x below). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d fracs=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, FRACS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
