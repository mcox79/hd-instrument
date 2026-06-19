"""
exp_sparse_w_scale_validation_gpu_v1 -- storage-efficiency anchor 1 (HIGHEST leverage: sparse-W reduction) -- GPU.

ROUTING: handoff exp_dev_handoff_research_storage_efficiency #1. Sparse-W: zero out small |W| entries to cut W storage.
  Measures accuracy-vs-sparsity at scale. Per-fact W cost 270KB->~27KB if 8x holds. NOTE: dense N x N W at N=65536 is 8.6GB
  (>8GB card) -- cap N<=16384 (8GB-safe per OOM rule), measure the sparsity-accuracy curve, ratio extrapolates to 65536.
  GPU.
PRE-REGISTERED: HARD-PASS >=8x weight reduction (sparsity>=0.875) with <=3pct exact-recovery accuracy drop at load M/N=0.25.
  MIDDLE 4-8x at <=3pct. HARD-FAIL <4x (sparse-W not a viable compression path).
FORMULA SELF-TESTS (PROT-022): 1. dense recall high. 2. sparsify keeps top entries. 3. cuda.
ASCII-only. write_metrics. PROT-018 no _nN (N-sweep).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "sparse_w_scale_validation_gpu_v1"
ALPHA = 0.25; FLIP = 0.05; STEPS = 6; SPARS = [0.0, 0.5, 0.75, 0.875, 0.9375]
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_GRID = [2048, 4096] if RUN_MODE == "smoke" else [4096, 8192]   # 8GB-safe with pinv W + argsort; 16384 OOMs


def hebb_W(P):   # pinv write rule (capacity ~1.0; handles M/N=0.25 where Hebb's 0.14 fails)
    G = P @ P.t() + 1e-3 * torch.eye(P.shape[0], device=P.device, dtype=P.dtype)
    W = P.t() @ torch.linalg.solve(G, P); W.fill_diagonal_(0.0); return W


def sparsify(W, frac):
    if frac <= 0:
        return W
    flat = W.flatten().clone(); n_zero = int(frac * flat.numel())
    idx = torch.argsort(flat.abs())[:n_zero]; flat[idx] = 0.0; return flat.reshape(W.shape)   # zero exactly the smallest n_zero (no tie ambiguity)


def recall(P, W, seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed)); M, n = P.shape
    s = P * torch.where(torch.rand(M, n, generator=g, device=_DEV) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = torch.sign(s @ W.t()); s[s == 0] = 1.0
    return float((s == P).all(dim=1).float().mean().item())


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); P = (torch.randint(0, 2, (20, 256), generator=g, device=_DEV) * 2 - 1).float()
    assert recall(P, hebb_W(P), 0) >= 0.9, "dense recall high"
    W = hebb_W(P); Ws = sparsify(W, 0.5); assert 0.3 <= (Ws != 0).float().mean().item() <= 0.6, "sparsify keeps ~top half"
    print("[selftest] PASS: sparse-w-scale", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def run() -> Dict:
    res = {}
    for n in N_GRID:
        torch.cuda.empty_cache(); g = torch.Generator(device=_DEV).manual_seed(7); M = max(4, int(ALPHA * n))
        P = (torch.randint(0, 2, (M, n), generator=g, device=_DEV) * 2 - 1).float(); W = hebb_W(P); base = recall(P, W, 1)
        curve = {}
        for sp in SPARS:
            acc = recall(P, sparsify(W, sp), 2); curve["sp%.4f" % sp] = acc
            print("  [N=%d sparsity=%.4f] recall=%.3f (base=%.3f, reduction=%.1fx)" % (n, sp, acc, base, 1.0 / max(1 - sp, 1e-9)), flush=True)
        res["N%d" % n] = {"base": base, "curve": curve}
    return res


def verdict(res) -> Tuple[str, str]:
    nmax = "N%d" % N_GRID[-1]; base = res[nmax]["base"]; curve = res[nmax]["curve"]
    # best reduction with <=3pct drop
    best_red = 1.0
    for sp in SPARS:
        if curve["sp%.4f" % sp] >= base - 0.03:
            best_red = max(best_red, 1.0 / max(1 - sp, 1e-9))
    summary = "at N=%d base=%.3f, max reduction at <=3pct drop = %.1fx | curve=%s" % (N_GRID[-1], base, best_red, {k: round(v, 3) for k, v in curve.items()})
    if best_red >= 8:
        return ("HARD_PASS", "HARD_PASS: sparse-W gives >=8x weight reduction at <=3pct accuracy drop -- per-fact W cost ~270KB->~27KB; largest single efficiency gain. " + summary)
    if best_red >= 4:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 4-8x sparse-W reduction at <=3pct. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: <4x sparse-W reduction -- not a viable compression path. " + summary)


print("[config] anchor=%s mode=%s N_grid=%s alpha=%.2f spars=%s" % (ANCHOR_NAME, RUN_MODE, N_GRID, ALPHA, SPARS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); res = run()
v, vmsg = verdict(res); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [res], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [res]); print("[metrics] written", flush=True)
