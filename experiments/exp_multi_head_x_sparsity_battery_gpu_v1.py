"""
exp_multi_head_x_sparsity_battery_gpu_v1 -- BUNDLED multi-head x sparsity cross-product, all GPU (long) -- GPU.

ROUTING: Batch C extension + GPU-load. Multi-head sparse-KEY was the Batch C winner (3.5x). This maps the FULL interaction
  surface: head-count H=[1,2,4,8] x sparsity f=[0.02,0.05,0.10,0.20] x N=[8192,16384,32768] x seeds. Does the multi-head
  MMV gain compound with sparser coding, or do they trade off? Support-recovery capacity (alpha=M_c/N), W-FREE Hopfield
  (no N x N matrix). Large grid -> long sustained GPU job.
PRE-REGISTERED: HARD-PASS best (H,f) cell alpha >= 5x the (H=1, f=0.10) reference -- multi-head and sparsity compound.
  MID 2-5x. HARD-FAIL <2x (they trade off, no compounding).
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

ANCHOR_NAME = "multi_head_x_sparsity_battery_gpu_v1"
FLIP = 0.05
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
HEADS = [1, 2, 4, 8]; FRACS = [0.02, 0.05, 0.10, 0.20]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_GRID = [2048]; LOADS = [0.05, 0.1, 0.2, 0.4, 0.7]; HEADS = [1, 2]; FRACS = [0.05, 0.10]
else:
    SEEDS = [7, 17, 23]; N_GRID = [8192, 16384, 32768]; LOADS = [0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 0.9, 1.1, 1.4]


def support_recovery(M, n, H, f, seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed)); k = max(1, int(f * n))
    supp = torch.stack([torch.randperm(n, generator=g, device=_DEV)[:k] for _ in range(M)])
    onehot = torch.zeros(M, n, device=_DEV); onehot.scatter_(1, supp, 1.0); score = torch.zeros(M, n, device=_DEV)
    for h in range(H):
        signs = (torch.randint(0, 2, (M, k), generator=g, device=_DEV, dtype=torch.float32) * 2 - 1)
        P = torch.zeros(M, n, device=_DEV); P.scatter_(1, supp, signs); diag = (P * P).sum(0)
        cue = P.clone(); flip = (torch.rand(M, k, generator=g, device=_DEV) < FLIP).float() * -2 + 1; cue.scatter_(1, supp, signs * flip)
        score += ((cue @ P.t()) @ P - cue * diag).abs()                # W-free
    topk = score.topk(k, dim=1).indices; rec = torch.zeros(M, n, device=_DEV); rec.scatter_(1, topk, 1.0)
    return float(((rec * onehot).sum(1) == k).float().mean().item())


def cap(H, f, n, seed):
    c = 0
    for load in LOADS:
        M = max(2, int(load * n))
        if support_recovery(M, n, H, f, seed * 100 + M) >= 0.95:
            c = M
        else:
            break
    return c / n


def _selftest():
    assert support_recovery(4, 512, 1, 0.05, 0) >= 0.95, "low-load recovers"
    assert support_recovery(4, 512, 2, 0.05, 0) >= 0.95, "H=2 recovers"
    print("[selftest] PASS: mhxs", flush=True)


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
    def a(H, f):
        vs = [r["alpha"] for r in rows if r["H"] == H and r["f"] == f and r["N"] == nmax]; return float(np.mean(vs)) if vs else 0.0
    ref = a(1, 0.10); best = max(a(H, f) for H in HEADS for f in FRACS); g = best / max(ref, 1e-9)
    argbest = max(((H, f) for H in HEADS for f in FRACS), key=lambda hf: a(*hf))
    summary = "ref(H1,f0.10)=%.4f best=%.4f at (H,f)=%s | best/ref=%.2fx" % (ref, best, argbest, g)
    if g >= 5.0:
        return ("HARD_PASS", "HARD_PASS: multi-head and sparsity COMPOUND (best >=5x ref) -- joint composition lever. " + summary)
    if g >= 2.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial compounding (2-5x). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: multi-head and sparsity trade off (<2x). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%s H=%s f=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, HEADS, FRACS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); rows = []
for n in N_GRID:
    torch.cuda.empty_cache()  # empty_cache() between N points (release fragments)
    for H in HEADS:
        for f in FRACS:
            for seed in SEEDS:
                rows.append({"H": H, "f": f, "N": n, "seed": seed, "alpha": cap(H, f, n, seed)})
            av = float(np.mean([r["alpha"] for r in rows if r["H"] == H and r["f"] == f and r["N"] == n]))
            print("  [N=%d H=%d f=%.2f] alpha=%.4f" % (n, H, f, av), flush=True)
v, vmsg = verdict(rows); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": rows, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, rows); print("[metrics] written", flush=True)
