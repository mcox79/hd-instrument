"""
exp_substrate_etf_hadamard_n_sweep_capacity_v1 -- Slot 10: ETF Hadamard capacity lift across N (Phase-3 gate) -- CPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot 10 (CRITICAL). ETF Hadamard gave 10.04x at N=4096. Phase-3 capacity blueprint depends
  on whether the lift PERSISTS to N=65536. Sweeps N in {4096, 16384, 32768, 65536}, Hadamard vs random patterns, W-FREE
  auto-assoc Hopfield (never materialize NxN W: W@s = P^T(P@s) - M*s) so large N fits in RAM. CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS ratio (Hadamard/random) stays >= 5x at N=65536. MIDDLE: 2-5x at N=65536. HARD-FAIL: < 2x
  at N=65536 (lift collapses at scale -> cubic-tensor is the only Phase-3 capacity path).
FORMULA SELF-TESTS (PROT-022): 1. W-free == explicit W. 2. Hadamard orthogonal. 3. hadamard recovers > random at load.
ASCII-only. write_metrics. PROT-018: no _nN (N-sweep).
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
import torch  # capacity matmuls run on GPU via _gpu_cap.hopfield_recall_t
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments._gpu_cap import recall_unique_t, hopfield_recall_t

ANCHOR_NAME = "substrate_etf_hadamard_n_sweep_capacity_v1"
FLIP = 0.05; STEPS = 6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_GRID = [1024, 2048]; LOADS = [0.05, 0.1, 0.2, 0.4]
else:
    SEEDS = [7, 17, 23]; N_GRID = [4096, 16384, 32768, 65536]; LOADS = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]


def hadamard(n):
    H = np.array([[1.0]], dtype=np.float32)
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    return H


def pats_random(M, n, g):
    return (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)


def pats_hadamard(M, n, g):
    H = hadamard(n); idx = g.choice(n, size=min(M, n), replace=False); P = H[idx]
    if M > n:
        P = np.vstack([P, pats_random(M - n, n, g)])
    return P.astype(np.float32)


def recall_wfree(P, g):
    return hopfield_recall_t(P, FLIP, STEPS, int(g.integers(0, 2**31)))   # GPU W-free Hopfield


def _selftest():
    g = np.random.default_rng(0); n = 128; P = pats_random(10, n, g)
    W = (P.T @ P).astype(np.float32); np.fill_diagonal(W, 0.0)
    s0 = P.copy(); gg = np.random.default_rng(1); s = s0 * np.where(gg.random((10, n)) < 0.05, -1.0, 1.0)
    expl = np.sign(s @ W.T); A = P @ s.T; wf = np.sign((P.T @ A).T - 10 * s)
    assert np.array_equal(expl, wf), "W-free == explicit W (one step)"
    H = hadamard(8); G = H @ H.T; assert np.allclose(G - np.diag(np.diag(G)), 0), "Hadamard orthogonal"
    assert recall_wfree(pats_hadamard(80, 256, g), g) >= 0.95 > recall_wfree(pats_random(80, 256, g), g), "hadamard>random at load"
    print("[selftest] PASS: wfree hadamard", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def capacity(n, patfn, seed):
    cap = 0
    for load in LOADS:
        M = max(2, int(load * n))
        if recall_wfree(patfn(M, n, np.random.default_rng(seed * 1000 + M)), np.random.default_rng(seed * 7 + M)) >= 0.95:
            cap = M
        else:
            break
    return cap


def run_seed(seed) -> Dict:
    by_N = {}
    for n in N_GRID:
        cr = capacity(n, pats_random, seed); ch = capacity(n, pats_hadamard, seed)
        by_N["N%d" % n] = {"random_cap": cr, "hadamard_cap": ch, "ratio": float(ch / max(cr, 1))}
        print("    [seed=%d N=%d] random_cap=%d hadamard_cap=%d ratio=%.2fx" % (seed, n, cr, ch, ch / max(cr, 1)), flush=True)
    return {"seed": seed, "by_N": by_N}


def verdict(ps) -> Tuple[str, str]:
    khi = "N%d" % N_GRID[-1]; rhi = float(np.mean([p["by_N"][khi]["ratio"] for p in ps]))
    parts = " ".join("N=%s: %.2fx" % (k[1:], np.mean([p["by_N"][k]["ratio"] for p in ps])) for k in ps[0]["by_N"])
    summary = "ratio (Hadamard/random) by N: %s" % parts
    if rhi >= 5.0:
        return ("HARD_PASS", "HARD_PASS: ETF Hadamard lift persists >=5x at N=%s -- Phase-3 linear capacity scales (~10x more facts). " % N_GRID[-1] + summary)
    if rhi >= 2.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: lift 2-5x at largest N (partial persistence). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: ETF lift collapses (<2x) at N=%s -- cubic-tensor is the only Phase-3 capacity path. " % N_GRID[-1] + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    ps.append(run_seed(seed))
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
