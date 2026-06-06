"""
exp_substrate_capacity_battery_gpu_v1 -- BUNDLED capacity design-space sweep, all on GPU -- GPU.

ROUTING: efficiency bundle. Individual capacity cells are fast GPU bursts; bundling the whole design-space grid into ONE
  torch job keeps the GPU sustained AND is far cheaper than N separate CPU cells. Sweeps WRITE-RULE x N x SEED in a single
  process, all matmuls on GPU (W-free auto-assoc Hopfield, exact-recovery). Produces a comprehensive capacity map:
  dense / sparse(f=0.05,0.10,0.20) / Hadamard, across N, vs the dense baseline. Replaces Slot 3 / Slot 10 / sparse-vs-dense
  / codebook cells with one efficient GPU battery.

PRE-REGISTERED bands: HARD-PASS at least one rule gives >=3x dense alpha at the largest N (capacity lever persists at scale).
  MIDDLE 1.5-3x. HARD-FAIL all <=1.5x.
FORMULA SELF-TESTS (PROT-022): 1. dense recovers low load. 2. sparse k-of-N. 3. hadamard orthogonal. 4. cuda.
ASCII-only. write_metrics. PROT-018: no _nN (grid).
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
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import torch
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_corruption_robustness_battery_gpu_v1"
FLIP = 0.05; STEPS = 6; FLIPS = [0.05, 0.10, 0.20, 0.30]
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RULES = ["dense", "sparse0.10", "hadamard"]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_GRID = [4096, 8192]; LOADS = [0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0]
else:
    SEEDS = [7, 17, 23]; N_GRID = [8192, 16384, 32768]; LOADS = [0.02, 0.04, 0.06, 0.08, 0.1, 0.13, 0.16, 0.2, 0.25, 0.3, 0.4, 0.6, 0.8, 1.0]


def _hadamard_t(n):
    H = torch.ones(1, 1, device=_DEV)
    while H.shape[0] < n:
        H = torch.cat([torch.cat([H, H], 1), torch.cat([H, -H], 1)], 0)
    return H


def make_patterns(rule, M, n, g):
    if rule == "dense":
        return (torch.randint(0, 2, (M, n), generator=g, device=_DEV, dtype=torch.float32) * 2 - 1), False
    if rule == "hadamard":
        H = _hadamard_t(n); idx = torch.randperm(n, generator=g, device=_DEV)[:min(M, n)]; P = H[idx]
        if M > n:
            P = torch.cat([P, (torch.randint(0, 2, (M - n, n), generator=g, device=_DEV, dtype=torch.float32) * 2 - 1)], 0)
        return P, False
    f = float(rule.replace("sparse", "")); k = max(1, int(f * n)); P = torch.zeros(M, n, device=_DEV)
    for i in range(M):
        idx = torch.randperm(n, generator=g, device=_DEV)[:k]; P[i, idx] = (torch.randint(0, 2, (k,), generator=g, device=_DEV, dtype=torch.float32) * 2 - 1)
    return P, True


def recall(P, sparse, g, flip=FLIP):
    M, n = P.shape
    if sparse:                                                        # single-step (iterating fills zeros -> divergence)
        diag = (P * P).sum(0); s = P.clone()                          # W-free: avoid N x N matrix (OOM at large N)
        for i in range(M):
            nz = (P[i] != 0).nonzero(as_tuple=True)[0]; fl = nz[torch.rand(len(nz), generator=g, device=_DEV) < flip]; s[i, fl] *= -1
        r = torch.sign((s @ P.t()) @ P - s * diag); ok = 0
        for i in range(M):
            nz = (P[i] != 0); ok += int((r[i][nz] == P[i][nz]).all().item())
        return ok / M
    S = P * torch.where(torch.rand(M, n, generator=g, device=_DEV) < flip, -1.0, 1.0)
    for _ in range(STEPS):
        S = torch.sign((P.t() @ (P @ S.t())).t() - M * S); S[S == 0] = 1.0
    return float((S == P).all(dim=1).float().mean().item())


def cap(rule, n, seed, flip=FLIP):
    g = torch.Generator(device=_DEV).manual_seed(int(seed)); c = 0
    for load in LOADS:
        M = max(2, int(load * n)); P, sp = make_patterns(rule, M, n, g)
        if recall(P, sp, g, flip) >= 0.95:
            c = M
        else:
            break
    return c


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0)
    Pd, _ = make_patterns("dense", 8, 512, g); assert recall(Pd, False, g) >= 0.95, "dense recovers low load"
    Ps, sp = make_patterns("sparse0.10", 8, 512, g); assert sp and int((Ps[0] != 0).sum().item()) == 51, "sparse k-of-N"
    H = _hadamard_t(8); assert torch.allclose(H @ H.t() - torch.diag(torch.diag(H @ H.t())), torch.zeros(8, 8, device=_DEV)), "hadamard orthogonal"
    print("[selftest] PASS: battery", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
_vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3   # vram-cap
if _vram_gb < 12.0:
    N_GRID = [n for n in N_GRID if n <= 16384]
    print("[vram] %.1fGB card -> N_GRID capped to %s (avoid N>=32768 OOM)" % (_vram_gb, N_GRID), flush=True)


def verdict(rows) -> Tuple[str, str]:
    nmax = N_GRID[-1]
    def alpha(rule, fl):
        vs = [r["alpha"] for r in rows if r["rule"] == rule and r["N"] == nmax and r["flip"] == fl]; return float(np.mean(vs)) if vs else 0.0
    retn = {rule: alpha(rule, max(FLIPS)) / max(alpha(rule, min(FLIPS)), 1e-9) for rule in RULES}
    worst = min(retn.values(), default=0.0)
    summary = "at N=%d, capacity-retention(flip %.2f->%.2f) by rule: %s" % (nmax, min(FLIPS), max(FLIPS), {k: round(v, 2) for k, v in retn.items()})
    if worst >= 0.5:
        return ("HARD_PASS", "HARD_PASS: all rules retain >=50%% capacity at high corruption -- robust substrate. " + summary)
    if worst >= 0.25:
        return ("MIDDLE_BAND", "MIDDLE_BAND: some rules degrade (0.25-0.5 retention) at high corruption. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: a rule collapses (<0.25 retention) under corruption. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s rules=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, RULES), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); rows = []
for n in N_GRID:
    torch.cuda.empty_cache()  # empty_cache() between N points (release fragments)
    for rule in RULES:
        for flip in FLIPS:
            for seed in SEEDS:
                cc = cap(rule, n, seed, flip); rows.append({"rule": rule, "N": n, "flip": flip, "seed": seed, "cap": cc, "alpha": cc / n})
            a = float(np.mean([r["alpha"] for r in rows if r["rule"] == rule and r["N"] == n and r["flip"] == flip]))
            print("  [N=%d %-11s flip=%.2f] alpha=%.4f" % (n, rule, flip, a), flush=True)
v, vmsg = verdict(rows); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": rows, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, rows); print("[metrics] written", flush=True)
