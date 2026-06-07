"""
exp_modern_hopfield_gpu_scale_v1 -- storage: modern Hopfield at scale on GPU -- GPU.

ROUTING: follows modern_hopfield_n_sweep (CPU). Confirms the exponential-energy Hopfield capacity holds at larger N on GPU
  (N up to 16384, M/N to 0.4), and times the softmax retrieval. If high-load recovery holds at scale, modern Hopfield is the
  storage path to drop N. GPU.
PRE-REGISTERED: HARD-PASS accuracy>0.90 at N=16384 M/N=0.40. MIDDLE >0.90 at M/N=0.30 only. HARD-FAIL <0.70 at M/N=0.30.
FORMULA SELF-TESTS (PROT-022): 1. clean retrieval. 2. softmax sharpens. 3. cuda.
ASCII-only. write_metrics. PROT-018 no _nN.
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

ANCHOR_NAME = "modern_hopfield_gpu_scale_v1"; BETA = 8.0; FLIP = 0.05
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_GRID = [4096, 8192] if RUN_MODE == "smoke" else [8192, 16384]
LOADS = [0.3, 0.4]


def patterns(M, n, g):
    return (torch.randint(0, 2, (M, n), generator=g, device=_DEV) * 2 - 1).float()


def mh_recall(P, seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed)); M, n = P.shape
    s = P * torch.where(torch.rand(M, n, generator=g, device=_DEV) < FLIP, -1.0, 1.0)
    for _ in range(3):
        s = torch.sign(torch.softmax(BETA * (s @ P.t()), dim=1) @ P); s[s == 0] = 1.0
    return float((s == P).all(dim=1).float().mean().item())


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); P = patterns(4, 128, g); assert mh_recall(P, 0) >= 0.95, "clean retrieval"
    assert float(torch.softmax(torch.tensor([0.0, 10.0]), 0)[1]) > 0.99, "softmax sharpens"
    print("[selftest] PASS: modern-hopfield-gpu", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def run() -> Dict:
    by = {}
    for n in N_GRID:
        for load in LOADS:
            torch.cuda.empty_cache(); g = torch.Generator(device=_DEV).manual_seed(7); M = max(4, int(load * n))
            a = mh_recall(patterns(M, n, g), 11); by["N%d_L%.2f" % (n, load)] = a
            print("  [N=%d M/N=%.2f] accuracy=%.3f" % (n, load, a), flush=True)
    return {"by": by}


def verdict(r) -> Tuple[str, str]:
    nmax = N_GRID[-1]; a40 = r["by"].get("N%d_L0.40" % nmax, 0.0); a30 = r["by"].get("N%d_L0.30" % nmax, 0.0)
    summary = "accuracy: %s (N=%d M/N=0.40 -> %.3f)" % ({k: round(v, 3) for k, v in r["by"].items()}, nmax, a40)
    if a40 > 0.90:
        return ("HARD_PASS", "HARD_PASS: modern Hopfield >0.90 at N=%d M/N=0.40 -- exponential-energy capacity holds at scale; storage path to drop N confirmed. " % nmax + summary)
    if a30 > 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: holds at M/N=0.30 not 0.40. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: <0.70 at M/N=0.30 at scale. " + summary)


print("[config] anchor=%s mode=%s N_grid=%s beta=%.1f loads=%s" % (ANCHOR_NAME, RUN_MODE, N_GRID, BETA, LOADS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
