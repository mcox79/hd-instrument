"""
exp_substrate_sparse_vs_dense_large_n_gpu_v1 -- GPU-optimized: sparse-coding capacity advantage at LARGE N -- GPU.

ROUTING: GPU-bound capacity science. Slot 3 showed sparse PATTERN coding ~12x dense at small N (numpy). This extends it
  to LARGE N {16384, 32768, 65536} on the GPU (W-free auto-assoc Hopfield, exact-recovery) -- the matmuls P^T(P S) at
  these N are large + sustained -> genuinely GPU-bound (not encode-then-numpy). Synthetic +/-1 patterns (no encoder rank
  limit). Does the sparse-coding capacity advantage persist at production N? torch GPU throughout.

PRE-REGISTERED: HARD-PASS sparse alpha (M_max/N) >= 3x dense at N=65536. MIDDLE 1.5-3x. HARD-FAIL <1.5x.
FORMULA SELF-TESTS (PROT-022): 1. dense recovers low load. 2. sparse k-of-N. 3. cuda.
ASCII-only. write_metrics. PROT-018: no _nN (N-sweep).
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os, argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
import numpy as np
import torch
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_sparse_vs_dense_large_n_gpu_v1"
FLIP = 0.05; STEPS = 6; F_SPARSE = 0.10
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_GRID = [4096, 8192]; LOADS = [0.02, 0.05, 0.1, 0.2, 0.4]
else:
    SEEDS = [7, 17, 23]; N_GRID = [16384, 32768, 65536]; LOADS = [0.02, 0.04, 0.06, 0.08, 0.1, 0.13, 0.16, 0.2, 0.25, 0.3]


def dense_recall_t(M, n, seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed))
    P = (torch.randint(0, 2, (M, n), generator=g, device=_DEV, dtype=torch.float32) * 2 - 1)
    S = P * torch.where(torch.rand(M, n, generator=g, device=_DEV) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        S = torch.sign((P.t() @ (P @ S.t())).t() - M * S); S[S == 0] = 1.0
    return float((S == P).all(dim=1).float().mean().item())


def sparse_recall_t(M, n, seed):
    # sparse PATTERN coding: k=f*n active +/-1; single-step retrieval (iterating fills zeros -> dense divergence)
    g = torch.Generator(device=_DEV).manual_seed(int(seed)); k = max(1, int(F_SPARSE * n))
    P = torch.zeros(M, n, device=_DEV)
    for i in range(M):
        idx = torch.randperm(n, generator=g, device=_DEV)[:k]; P[i, idx] = (torch.randint(0, 2, (k,), generator=g, device=_DEV, dtype=torch.float32) * 2 - 1)
    W = (P.t() @ P); W.fill_diagonal_(0.0)
    s = P.clone()
    for i in range(M):
        nz = (P[i] != 0).nonzero(as_tuple=True)[0]; fl = nz[torch.rand(len(nz), generator=g, device=_DEV) < FLIP]; s[i, fl] *= -1
    r = torch.sign(s @ W.t())
    ok = 0
    for i in range(M):
        nz = (P[i] != 0); ok += int((r[i][nz] == P[i][nz]).all().item())
    return ok / M


def cap(recall_fn, n, seed):
    c = 0
    for load in LOADS:
        M = max(2, int(load * n))
        if recall_fn(M, n, seed * 100 + M) >= 0.95:
            c = M
        else:
            break
    return c


def _selftest():
    assert dense_recall_t(8, 512, 1) >= 0.95, "dense recovers low load"
    assert sparse_recall_t(8, 512, 1) >= 0.95, "sparse recovers low load"
    print("[selftest] PASS: dense sparse", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def run_seed(seed) -> Dict:
    by_N = {}
    for n in N_GRID:
        cd = cap(dense_recall_t, n, seed); cs = cap(sparse_recall_t, n, seed)
        by_N["N%d" % n] = {"dense_alpha": cd / n, "sparse_alpha": cs / n, "ratio": float((cs / n) / max(cd / n, 1e-9))}
        print("    [seed=%d N=%d] dense_alpha=%.4f sparse_alpha=%.4f ratio=%.2fx" % (seed, n, cd / n, cs / n, (cs / max(cd, 1))), flush=True)
    return {"seed": seed, "by_N": by_N}


def verdict(ps) -> Tuple[str, str]:
    khi = "N%d" % N_GRID[-1]; r = float(np.mean([p["by_N"][khi]["ratio"] for p in ps]))
    parts = " ".join("N=%s: %.2fx" % (k[1:], np.mean([p["by_N"][k]["ratio"] for p in ps])) for k in ps[0]["by_N"])
    summary = "sparse/dense alpha ratio by N: %s" % parts
    if r >= 3.0:
        return ("HARD_PASS", "HARD_PASS: sparse-coding capacity advantage persists >=3x at N=%s -- production-scale capacity lever. " % N_GRID[-1] + summary)
    if r >= 1.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sparse 1.5-3x at largest N. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: sparse advantage collapses (<1.5x) at scale. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s f_sparse=%.2f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, F_SPARSE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    ps.append(run_seed(seed))
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
