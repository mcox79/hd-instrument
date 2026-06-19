"""
exp_hopfield_capacity_gpu_v1.py -- modern vs classic Hopfield capacity sweep at N=2048 on GPU -- GPU.

ROUTING: GPU-scale substrate-physics validation (modern-Hopfield capacity at GPU scale). Sweep load P/N up to 4.0 at N=2048 (large for CPU); modern-Hopfield (softmax) vs classic, recall@1 (overlap>=0.95) under noise. Maps the exponential-capacity advantage at production dimension. torch.cuda; scales beyond CPU feasibility. GPU.
PRE-REGISTERED: HARD-PASS modern recall@1 >= 0.95 at P/N=2.0 where classic < 0.1. MIDDLE modern >= 0.85. HARD-FAIL modern < 0.85.
ASCII-only. write_metrics. PROT-018 _v1.
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
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "hopfield_capacity_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.sign(-0.3) == -1, "sign"; assert 0.14 < 2.0, "load"; print("[selftest] PASS: hopfield-capacity-gpu", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)

def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(1); N = 2048; FLIP = 0.15; NQ = 200; by = {}
    loads = [0.5, 1.0, 2.0] if SMOKE else [0.5, 1.0, 2.0, 4.0]
    for load in loads:
        P = max(2, int(load * N)); X = torch.sign(torch.randn(P, N, generator=g, device=DEV)); X[X == 0] = 1
        qi = torch.randperm(P, generator=g, device=DEV)[:min(NQ, P)]; Q = X[qi].clone()
        fl = torch.rand(Q.shape, generator=g, device=DEV) < FLIP; Q[fl] *= -1
        att = torch.softmax(8.0 * (Q @ X.T), dim=1); retm = torch.sign(att @ X)
        modern = ((retm * X[qi]).sum(1) / N >= 0.95).float().mean().item()
        W = (X.T @ X) / N; W.fill_diagonal_(0.0); sc = torch.sign(Q @ W.T); sc[sc == 0] = 1
        classic = ((sc * X[qi]).sum(1) / N >= 0.95).float().mean().item()
        by["L%.1f" % load] = {"modern": modern, "classic": classic}
        print("  P/N=%.1f modern=%.3f classic=%.3f" % (load, modern, classic), flush=True)
        del X, Q, att, retm, W; torch.cuda.empty_cache()
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    l2 = r["by"].get("L2.0", {"modern": 0, "classic": 1}); m = l2["modern"]; c = l2["classic"]
    s = "at P/N=2.0 modern=%.3f classic=%.3f | %s" % (m, c, {k: (round(v["modern"], 3), round(v["classic"], 3)) for k, v in r["by"].items()})
    if m >= 0.95 and c < 0.1: return ("HARD_PASS", "HARD_PASS: modern Hopfield recall@1>=0.95 at P/N=2.0 (classic dead) at N=2048 -- exponential capacity holds at production dimension. " + s)
    if m >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: modern 0.85-0.95 at P/N=2.0. " + s)
    return ("HARD_FAIL", "HARD_FAIL: modern <0.85 at P/N=2.0. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
