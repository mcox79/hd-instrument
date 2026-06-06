"""
exp_sparse_key_composition_battery_gpu_v1 -- BUNDLED Batch C1 #2+#3 composition arms, all GPU -- GPU.

ROUTING: Batch C1 bundled (hadamard-independent-mask #2 + block-sparse #3) + GPU depth (user rule). Tests two constructions
  the drill said Batch B foreclosed prematurely:
  (#2) Hadamard rows x INDEPENDENT per-row sparse mask (cycle 130 used a SHARED mask which destroyed orthogonality;
       independent masks may preserve it). HP: hadamard_indep >= 0.80 * max(hadamard, flat_sparse).
  (#3) Block-sparse nesting (active in a sparse subset of blocks, dense within) vs flat-sparse at matched total density.
       Block-RIP (Eldar-Mishali 2009) predicts 1.3-2x. HP: block_sparse >= 1.3x flat_sparse.
  Arms: flat_sparse / hadamard / hadamard_indep_mask / block_sparse. Capacity (Hopfield exact-recovery) x N x seed. torch GPU.
PRE-REGISTERED bands per-arm above; battery reports both ratios + classifies.
FORMULA SELF-TESTS (PROT-022): 1. hadamard orthogonal. 2. block-sparse density matched. 3. cuda.
ASCII-only. write_metrics. PROT-018 no _nN.
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

ANCHOR_NAME = "sparse_key_composition_battery_gpu_v1"
FLIP = 0.05; F_SPARSE = 0.10; N_BLOCKS = 16
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
ARMS = ["flat_sparse", "hadamard", "hadamard_indep_mask", "block_sparse"]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_GRID = [2048]; LOADS = [0.05, 0.1, 0.2, 0.4, 0.7]
else:
    SEEDS = [7, 17, 23]; N_GRID = [4096, 8192, 16384]; LOADS = [0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0]


def _had(n):
    H = torch.ones(1, 1, device=_DEV)
    while H.shape[0] < n:
        H = torch.cat([torch.cat([H, H], 1), torch.cat([H, -H], 1)], 0)
    return H


def make(arm, M, n, g):
    k = max(1, int(F_SPARSE * n))
    if arm == "flat_sparse":
        P = torch.zeros(M, n, device=_DEV)
        for i in range(M):
            idx = torch.randperm(n, generator=g, device=_DEV)[:k]; P[i, idx] = torch.randint(0, 2, (k,), generator=g, device=_DEV, dtype=torch.float32) * 2 - 1
        return P
    if arm == "hadamard":
        H = _had(n); idx = torch.randperm(n, generator=g, device=_DEV)[:min(M, n)]; P = H[idx]
        return P if M <= n else torch.cat([P, (torch.randint(0, 2, (M - n, n), generator=g, device=_DEV, dtype=torch.float32) * 2 - 1)], 0)
    if arm == "hadamard_indep_mask":
        H = _had(n); idx = torch.randperm(n, generator=g, device=_DEV)[:min(M, n)]; base = H[idx]
        if M > n:
            base = torch.cat([base, (torch.randint(0, 2, (M - n, n), generator=g, device=_DEV, dtype=torch.float32) * 2 - 1)], 0)
        P = torch.zeros(M, n, device=_DEV)                          # INDEPENDENT per-row mask
        for i in range(M):
            keep = torch.randperm(n, generator=g, device=_DEV)[:k]; P[i, keep] = base[i, keep]
        return P
    # block_sparse: choose sparse subset of blocks, dense within (matched total density ~ F_SPARSE)
    bs = n // N_BLOCKS; active_blocks = max(1, int(F_SPARSE * N_BLOCKS)); P = torch.zeros(M, n, device=_DEV)
    for i in range(M):
        blk = torch.randperm(N_BLOCKS, generator=g, device=_DEV)[:active_blocks]
        for b in blk.tolist():
            P[i, b * bs:(b + 1) * bs] = torch.randint(0, 2, (bs,), generator=g, device=_DEV, dtype=torch.float32) * 2 - 1
    return P


def recall(P, g):
    M, n = P.shape; diag = (P * P).sum(0); s = P.clone()              # W-free: avoid N x N matrix (OOM at large N)
    for i in range(M):
        nz = (P[i] != 0).nonzero(as_tuple=True)[0]; fl = nz[torch.rand(len(nz), generator=g, device=_DEV) < FLIP]; s[i, fl] *= -1
    r = torch.sign((s @ P.t()) @ P - s * diag); ok = 0
    for i in range(M):
        nz = (P[i] != 0); ok += int((r[i][nz] == P[i][nz]).all().item())
    return ok / M


def cap(arm, n, seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed)); c = 0
    for load in LOADS:
        M = max(2, int(load * n))
        if recall(make(arm, M, n, g), g) >= 0.95:
            c = M
        else:
            break
    return c / n


def _selftest():
    H = _had(8); G = H @ H.t(); assert torch.allclose(G - torch.diag(torch.diag(G)), torch.zeros(8, 8, device=_DEV)), "hadamard orthogonal"
    g = torch.Generator(device=_DEV).manual_seed(0); P = make("block_sparse", 4, 256, g)
    assert abs(float((P != 0).float().mean().item()) - F_SPARSE) < 0.05, "block-sparse density matched"
    print("[selftest] PASS: comp battery", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def verdict(rows) -> Tuple[str, str]:
    nmax = N_GRID[-1]
    def a(arm):
        vs = [r["alpha"] for r in rows if r["arm"] == arm and r["N"] == nmax]; return float(np.mean(vs)) if vs else 0.0
    indep_ratio = a("hadamard_indep_mask") / max(max(a("hadamard"), a("flat_sparse")), 1e-9)
    block_ratio = a("block_sparse") / max(a("flat_sparse"), 1e-9)
    summary = "alpha: %s | hadamard_indep/best=%.2f block/flat=%.2f" % ({arm: round(a(arm), 4) for arm in ARMS}, indep_ratio, block_ratio)
    wins = int(indep_ratio >= 0.80) + int(block_ratio >= 1.3)
    if wins == 2:
        return ("HARD_PASS", "HARD_PASS: BOTH compose -- hadamard-indep-mask within 20pct of best single AND block-sparse >=1.3x flat. " + summary)
    if wins == 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one composition arm passes. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: neither hadamard-indep-mask nor block-sparse composes. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%s arms=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, ARMS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); rows = []
for n in N_GRID:
    for arm in ARMS:
        for seed in SEEDS:
            rows.append({"arm": arm, "N": n, "seed": seed, "alpha": cap(arm, n, seed)})
        av = float(np.mean([r["alpha"] for r in rows if r["arm"] == arm and r["N"] == n]))
        print("  [N=%d %-20s] alpha=%.4f" % (n, arm, av), flush=True)
v, vmsg = verdict(rows); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": rows, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, rows); print("[metrics] written", flush=True)
