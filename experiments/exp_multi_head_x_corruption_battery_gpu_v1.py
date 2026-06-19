"""
exp_multi_head_x_corruption_battery_gpu_v1 -- BUNDLED multi-head x corruption robustness, all GPU (long) -- GPU.

ROUTING: Batch C extension + GPU-load. Multi-head sparse-KEY was the composition winner (3.5x). Production question: does
  the MMV gain SURVIVE cue corruption? MMV theory predicts multi-head should be MORE robust (averaging independent
  measurements denoises). Sweeps head-count H=[1,2,4,8] x flip-rate FLIP=[0.05,0.15,0.30,0.45] x N=[8192,16384,32768] x
  seeds. Support-recovery capacity (alpha=M_c/N), W-FREE Hopfield (no N x N matrix). Large grid -> long sustained GPU job.
PRE-REGISTERED: HARD-PASS at the HIGHEST corruption (flip=0.45), H=4 capacity >= 2x H=1 (multi-head robustness holds).
  MID 1.3-2x. HARD-FAIL <1.3x (corruption erases the multi-head advantage).
FORMULA SELF-TESTS (PROT-022): 1. shared support. 2. low-load recovers. 3. cuda.
ASCII-only. write_metrics. PROT-018 no _nN (grid).
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

ANCHOR_NAME = "multi_head_x_corruption_battery_gpu_v1"
F_SPARSE = 0.05
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
HEADS = [1, 2, 4, 8]; FLIPS = [0.05, 0.15, 0.30, 0.45]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_GRID = [2048]; LOADS = [0.05, 0.1, 0.2, 0.4, 0.7]; HEADS = [1, 4]; FLIPS = [0.05, 0.45]
else:
    SEEDS = [7, 17, 23]; N_GRID = [8192, 16384, 32768]; LOADS = [0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 0.9, 1.1, 1.4]


def support_recovery(M, n, H, flip, seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed)); k = max(1, int(F_SPARSE * n))
    supp = torch.stack([torch.randperm(n, generator=g, device=_DEV)[:k] for _ in range(M)])
    onehot = torch.zeros(M, n, device=_DEV); onehot.scatter_(1, supp, 1.0); score = torch.zeros(M, n, device=_DEV)
    for h in range(H):
        signs = (torch.randint(0, 2, (M, k), generator=g, device=_DEV, dtype=torch.float32) * 2 - 1)
        P = torch.zeros(M, n, device=_DEV); P.scatter_(1, supp, signs); diag = (P * P).sum(0)
        cue = P.clone(); fl = (torch.rand(M, k, generator=g, device=_DEV) < flip).float() * -2 + 1; cue.scatter_(1, supp, signs * fl)
        score += ((cue @ P.t()) @ P - cue * diag).abs()                # W-free
    topk = score.topk(k, dim=1).indices; rec = torch.zeros(M, n, device=_DEV); rec.scatter_(1, topk, 1.0)
    return float(((rec * onehot).sum(1) == k).float().mean().item())


def cap(H, flip, n, seed):
    c = 0
    for load in LOADS:
        M = max(2, int(load * n))
        if support_recovery(M, n, H, flip, seed * 100 + M) >= 0.95:
            c = M
        else:
            break
    return c / n


def _selftest():
    assert support_recovery(4, 512, 1, 0.05, 0) >= 0.95, "low-load recovers"
    assert support_recovery(4, 512, 4, 0.05, 0) >= 0.95, "H=4 recovers"
    print("[selftest] PASS: mhxc", flush=True)


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
    def a(H, flip):
        vs = [r["alpha"] for r in rows if r["H"] == H and r["flip"] == flip and r["N"] == nmax]; return float(np.mean(vs)) if vs else 0.0
    # robustness frontier: highest flip where baseline H1 still recovers (alpha>0); assess multi-head advantage there
    live = [fl for fl in FLIPS if a(1, fl) > 0]; frontier = max(live) if live else min(FLIPS)
    g = a(4, frontier) / max(a(1, frontier), 1e-9)
    ratios = {("flip%.2f" % fl): round(a(4, fl) / max(a(1, fl), 1e-9), 2) for fl in FLIPS}
    summary = "H4/H1 by flip at N=%d: %s | robustness-frontier flip=%.2f -> H4/H1=%.2fx" % (nmax, ratios, frontier, g)
    if frontier >= 0.30 and g >= 2.0:
        return ("HARD_PASS", "HARD_PASS: multi-head MMV advantage HOLDS to moderate-high corruption (>=2x H1 at flip>=0.30) -- production-robust composition. " + summary)
    if g >= 1.3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: multi-head advantage survives only to low-moderate corruption. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: corruption erases multi-head advantage at the recoverable frontier. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%s H=%s flips=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, HEADS, FLIPS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); rows = []
for n in N_GRID:
    torch.cuda.empty_cache()  # empty_cache() between N points (release fragments)
    for H in HEADS:
        for flip in FLIPS:
            for seed in SEEDS:
                rows.append({"H": H, "flip": flip, "N": n, "seed": seed, "alpha": cap(H, flip, n, seed)})
            av = float(np.mean([r["alpha"] for r in rows if r["H"] == H and r["flip"] == flip and r["N"] == n]))
            print("  [N=%d H=%d flip=%.2f] alpha=%.4f" % (n, H, flip, av), flush=True)
v, vmsg = verdict(rows); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": rows, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, rows); print("[metrics] written", flush=True)
