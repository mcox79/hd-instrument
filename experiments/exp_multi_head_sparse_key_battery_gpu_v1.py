"""
exp_multi_head_sparse_key_battery_gpu_v1 -- BUNDLED multi-head sparse-KEY H-scaling, all on GPU -- GPU.

ROUTING: Batch C bundled (covers C1#1 M=2 + C2#4 M=4 + extrapolation M=8) AND keeps GPU loaded (user rule). CPU M=2 cell
  already HARD_PASSed at 2.0x (beat sqrt(2)=1.41). This sweeps HEAD-COUNT H=[1,2,4,8] x N x seed on the GPU to map the
  full MMV scaling curve: each item has shared support S_i (k positions); head h = independent +-1 on S_i; per-head sparse
  Hopfield bank; recall combines sum_h|cue_h@W_h| -> top-k support recovery. capacity alpha = M_c/N. Vectorized torch.
PRE-REGISTERED: HARD-PASS H=2 >= 1.3x H=1 AND H=4 > H=2 (scaling continues). MID H=2 gain but H=4 plateaus. HARD-FAIL
  H=2 < 1.1x. Reports the H-scaling exponent (sqrt(M) => slope 0.5 in log-log).
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

ANCHOR_NAME = "multi_head_sparse_key_battery_gpu_v1"
F_SPARSE = 0.05; FLIP = 0.05
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
HEADS = [1, 2, 4, 8]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_GRID = [2048]; LOADS = [0.05, 0.1, 0.2, 0.4, 0.7]
else:
    SEEDS = [7, 17, 23, 29, 37, 41]; N_GRID = [4096, 8192, 16384, 32768]; LOADS = [0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0]


def support_recovery_rate(M, n, H, seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed)); k = max(1, int(F_SPARSE * n))
    # shared support per item
    supp = torch.stack([torch.randperm(n, generator=g, device=_DEV)[:k] for _ in range(M)])  # M x k
    onehot = torch.zeros(M, n, device=_DEV); onehot.scatter_(1, supp, 1.0)
    score = torch.zeros(M, n, device=_DEV)
    for h in range(H):
        signs = (torch.randint(0, 2, (M, k), generator=g, device=_DEV, dtype=torch.float32) * 2 - 1)
        P = torch.zeros(M, n, device=_DEV); P.scatter_(1, supp, signs)
        diag = (P * P).sum(0)                                          # W-free: avoid N x N per head (OOM at large N)
        cue = P.clone(); flip = (torch.rand(M, k, generator=g, device=_DEV) < FLIP).float() * -2 + 1
        cue.scatter_(1, supp, signs * flip)
        score += ((cue @ P.t()) @ P - cue * diag).abs()
    topk = score.topk(k, dim=1).indices; rec = torch.zeros(M, n, device=_DEV); rec.scatter_(1, topk, 1.0)
    return float(((rec * onehot).sum(1) == k).float().mean().item())


def cap(H, n, seed):
    c = 0
    for load in LOADS:
        M = max(2, int(load * n))
        if support_recovery_rate(M, n, H, seed * 100 + M) >= 0.95:
            c = M
        else:
            break
    return c / n


def _selftest():
    assert support_recovery_rate(4, 512, 1, 0) >= 0.95, "low-load recovers"
    assert support_recovery_rate(4, 512, 2, 0) >= 0.95, "H=2 low-load recovers"
    print("[selftest] PASS: mh battery", flush=True)


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
    def a(H):
        vs = [r["alpha"] for r in rows if r["H"] == H and r["N"] == nmax]; return float(np.mean(vs)) if vs else 0.0
    g2 = a(2) / max(a(1), 1e-9); g4 = a(4) / max(a(2), 1e-9)
    summary = "alpha by H at N=%d: %s | H2/H1=%.2f H4/H2=%.2f" % (nmax, {("H%d" % H): round(a(H), 4) for H in HEADS}, g2, g4)
    if g2 >= 1.3 and a(4) > a(2):
        return ("HARD_PASS", "HARD_PASS: multi-head sparse-KEY scales (H2>=1.3x H1, H4>H2) -- composition lever, Batch B 'sparse alone' premature. " + summary)
    if g2 >= 1.1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: H=2 gains but scaling plateaus. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: multi-head does not compose (H2<1.1x H1). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%s heads=%s f=%.2f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, HEADS, F_SPARSE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); rows = []
for n in N_GRID:
    torch.cuda.empty_cache()  # empty_cache() between N points (release fragments)
    for H in HEADS:
        for seed in SEEDS:
            rows.append({"H": H, "N": n, "seed": seed, "alpha": cap(H, n, seed)})
        av = float(np.mean([r["alpha"] for r in rows if r["H"] == H and r["N"] == n]))
        print("  [N=%d H=%d] alpha=%.4f" % (n, H, av), flush=True)
v, vmsg = verdict(rows); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": rows, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, rows); print("[metrics] written", flush=True)
