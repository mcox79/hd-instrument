"""
exp_n_reduction_storage_v1 -- storage-efficiency anchor 3 (N-reduction path) -- CPU.
ROUTING: handoff storage_efficiency #3. Does reducing dimension N (lower per-fact key storage) preserve exact-recovery
  capacity per stored bit? Sweeps N {1024,2048,4096,8192}; measures alpha_c (capacity fraction). If alpha_c is N-independent,
  smaller N stores the same fraction at lower cost. CPU.
PRE-REGISTERED: HARD-PASS alpha_c roughly N-independent (min/max >= 0.8 across N) -> N-reduction is free storage savings.
  MIDDLE 0.5-0.8. HARD-FAIL alpha_c collapses at low N.
FORMULA SELF-TESTS (PROT-022): 1. low-load recovers. 2. patterns bipolar. 3. grid ordered.
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
ANCHOR_NAME = "n_reduction_storage_v1"
FLIP = 0.05; STEPS = 8; LOADS = [0.5, 0.7, 0.85, 0.95]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]
N_GRID = [512, 1024] if RUN_MODE == "smoke" else [1024, 2048, 4096, 8192]
def patterns(M, n, g): return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)
def W_pinv(P):
    G = P @ P.T + 1e-3 * np.eye(P.shape[0], dtype=np.float32); W = (P.T @ np.linalg.solve(G, P)).astype(np.float32); np.fill_diagonal(W, 0.0); return W
def recall(P, W, seed):
    g = np.random.default_rng(seed); M, n = P.shape; s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))
def alpha_c(n, seed):
    g = np.random.default_rng(seed); c = 0.0
    for load in LOADS:
        M = max(2, int(load * n)); P = patterns(M, n, g)
        if recall(P, W_pinv(P), seed * 7 + M) >= 0.95: c = load
        else: break
    return c
def _selftest():
    g = np.random.default_rng(0); P = patterns(1, 128, g); assert recall(P, W_pinv(P), 0) >= 0.95, "low-load recovers"
    assert set(np.unique(patterns(4, 16, g))) <= {-1.0, 1.0}, "patterns bipolar"
    assert N_GRID[-1] > N_GRID[0], "grid ordered"
    print("[selftest] PASS: n-reduction", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    by = {}
    for n in N_GRID:
        a = float(np.mean([alpha_c(n, s) for s in SEEDS])); by["N%d" % n] = a; print("  [N=%d] alpha_c=%.3f" % (n, a), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    vals = np.array([r["by"]["N%d" % n] for n in N_GRID]); flat = float(vals.min() / max(vals.max(), 1e-9))
    summary = "alpha_c by N: %s | flatness=%.2f" % ({k: round(v, 3) for k, v in r["by"].items()}, flat)
    if flat >= 0.8:
        return ("HARD_PASS", "HARD_PASS: alpha_c is ~N-independent (flatness>=0.8) -- N-reduction is near-free storage savings; pick smallest N meeting capacity. " + summary)
    if flat >= 0.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: alpha_c partly N-dependent (flatness 0.5-0.8). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: alpha_c collapses at low N -- N-reduction costs capacity. " + summary)
print("[config] anchor=%s mode=%s seeds=%s N_grid=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
