"""
exp_substrate_sparse_hadamard_mixture_N_sweep_v1 -- SSOT DAMB2 (combined H1+H2 attack) -- CPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot DAMB2 (drill A Cell 2). Sparse-Hadamard-Mixture (SHM): each pattern = sign of a SPARSE
  combination of Hadamard basis rows (s random rows summed) -- keeps Hadamard orthogonal structure but adds sparse mixing
  to decorrelate anisotropy (H1) and delay subspace saturation (H2). Sweeps Q(N) for SHM vs plain Hadamard at
  N in {512,1024,2048} (powers of 2 for Hadamard; ~spec 384/1024/2048). If SHM Q(N) is FLAT and beats Hadamard, it ships
  as the single highest-leverage training-free codebook intervention. Hopfield exact-recovery capacity. CPU $0.
PRE-REGISTERED: HARD-PASS SHM Q(N) flat across N AND SHM >= 1.5x Hadamard at N=2048. MID one of the two. HF neither.
FORMULA SELF-TESTS (PROT-022): 1. hadamard orthogonal. 2. SHM sparse-mix valid. 3. Hopfield recovers low load.
ASCII-only. write_metrics. PROT-018 no _nN (N-sweep).
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

ANCHOR_NAME = "substrate_sparse_hadamard_mixture_N_sweep_v1"
FLIP = 0.05; STEPS = 6; S_MIX = 4   # sparse-mixture order (rows summed per pattern)
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_SWEEP = [512, 1024]; LOADS = [0.02, 0.05, 0.1, 0.2, 0.4]
else:
    SEEDS = [7, 17, 23]; N_SWEEP = [512, 1024, 2048]; LOADS = [0.02, 0.04, 0.06, 0.1, 0.15, 0.2, 0.3, 0.45, 0.6, 0.8]


def hadamard(n):
    H = np.array([[1.0]], np.float32)
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    return H


def make(arm, M, n, g):
    H = hadamard(n)
    if arm == "hadamard":
        idx = g.choice(n, min(M, n), replace=False); P = H[idx]
        return P if M <= n else np.vstack([P, (g.integers(0, 2, (M - n, n)) * 2 - 1).astype(np.float32)])
    # SHM: each pattern = sign(sum of S_MIX random Hadamard rows)
    P = np.zeros((M, n), np.float32)
    for i in range(M):
        rows = g.choice(n, S_MIX, replace=False); v = H[rows].sum(0); s = np.sign(v); s[s == 0] = 1.0; P[i] = s
    return P


def hop_recall(P, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign((s @ P.T) @ P - M * s); s[s == 0] = 1.0          # W-free dense Hopfield
    return float(np.mean(np.all(s == P, axis=1)))


def cap(arm, n, seed):
    g = np.random.default_rng(seed); c = 0
    for load in LOADS:
        M = max(2, int(load * n))
        if hop_recall(make(arm, M, n, g), seed * 100 + M) >= 0.95:
            c = M
        else:
            break
    return c / n


def _selftest():
    H = hadamard(8); G = H @ H.T; assert np.allclose(G - np.diag(np.diag(G)), 0), "hadamard orthogonal"
    g = np.random.default_rng(0); P = make("shm", 5, 256, g); assert set(np.unique(P)).issubset({-1.0, 1.0}), "SHM sparse-mix valid"
    Pd = (g.integers(0, 2, (6, 256)) * 2 - 1).astype(np.float32); assert hop_recall(Pd, 0) >= 0.95, "hopfield recovers low load"
    print("[selftest] PASS: shm", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    by_N = {}
    for n in N_SWEEP:
        ch = cap("hadamard", n, seed); cs = cap("shm", n, seed)
        by_N["N%d" % n] = {"hadamard": ch, "shm": cs, "ratio": cs / max(ch, 1e-9)}
        print("  [seed=%d N=%d] hadamard_alpha=%.4f shm_alpha=%.4f ratio=%.2fx" % (seed, n, ch, cs, cs / max(ch, 1e-9)), flush=True)
    return {"seed": seed, "by_N": by_N}


def verdict(ps) -> Tuple[str, str]:
    shm = np.array([np.mean([p["by_N"]["N%d" % n]["shm"] for p in ps]) for n in N_SWEEP])
    nmax = "N%d" % N_SWEEP[-1]; ratio_max = float(np.mean([p["by_N"][nmax]["ratio"] for p in ps]))
    flat = float(shm.min() / max(shm.max(), 1e-9)) >= 0.7            # flat = min/max within 30pct
    summary = "shm_alpha by N=%s | shm/hadamard at N=%d=%.2fx | flatness=%.2f" % ([round(x, 4) for x in shm], N_SWEEP[-1], ratio_max, float(shm.min() / max(shm.max(), 1e-9)))
    if flat and ratio_max >= 1.5:
        return ("HARD_PASS", "HARD_PASS: SHM Q(N) flat AND >=1.5x Hadamard at N=%d -- ships as highest-leverage training-free codebook. " % N_SWEEP[-1] + summary)
    if flat or ratio_max >= 1.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: SHM flat OR beats Hadamard but not both. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: SHM neither flat nor beats Hadamard. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_sweep=%s s_mix=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_SWEEP, S_MIX), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
