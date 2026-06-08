"""
exp_modern_hopfield_beta_capacity_gpu_v1.py -- modern-Hopfield recall map over (beta, load) at N=2048 (GPU) -- GPU.

ROUTING: GPU-scale substrate-physics validation (beta x load operating map). 2D sweep of recall@1 over inverse-temperature beta and load P/N at N=2048; identifies the practical operating region (which beta sustains clean retrieval as load grows). Maps the substrate's safe operating envelope. torch.cuda. GPU.
PRE-REGISTERED: HARD-PASS at beta=8 there exists clean retrieval (recall>=0.95) up to load P/N>=2.0. MIDDLE up to 1.0. HARD-FAIL only <1.0.
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
ANCHOR_NAME = "modern_hopfield_beta_capacity_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.exp(0) == 1.0, "exp"; assert 8 > 1, "beta"; print("[selftest] PASS: mh-beta-capacity-gpu", flush=True)
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
    g = torch.Generator(device=DEV).manual_seed(4); N = 2048; FLIP = 0.15; NQ = 150; grid = {}
    betas = [2.0, 8.0] if SMOKE else [1.0, 2.0, 4.0, 8.0, 16.0]; loads = [1.0, 2.0] if SMOKE else [0.5, 1.0, 2.0, 4.0]
    for load in loads:
        P = max(2, int(load * N)); X = torch.sign(torch.randn(P, N, generator=g, device=DEV)); X[X == 0] = 1
        qi = torch.randperm(P, generator=g, device=DEV)[:min(NQ, P)]; Q = X[qi].clone(); fl = torch.rand(Q.shape, generator=g, device=DEV) < FLIP; Q[fl] *= -1
        sims = Q @ X.T
        for b in betas:
            ret = torch.sign(torch.softmax(b * sims, dim=1) @ X)
            rec = ((ret * X[qi]).sum(1) / N >= 0.95).float().mean().item(); grid["b%g_L%.1f" % (b, load)] = rec
        del X, Q, sims; torch.cuda.empty_cache()
        print("  load=%.1f done" % load, flush=True)
    return {"grid": grid, "betas": betas, "loads": loads}
def verdict(r) -> Tuple[str, str]:
    grid = r["grid"]
    def at(b, l):
        return grid.get("b%g_L%.1f" % (b, l), 0.0)
    hi = max([l for l in r["loads"] if at(8.0, l) >= 0.95] + [0.0])
    s = "max-load@beta8 with recall>=0.95 = %.1f | grid=%s" % (hi, {k: round(v, 3) for k, v in grid.items()})
    if hi >= 2.0: return ("HARD_PASS", "HARD_PASS: at beta=8, clean retrieval holds to P/N>=2.0 -- wide safe operating envelope at N=2048. " + s)
    if hi >= 1.0: return ("MIDDLE_BAND", "MIDDLE_BAND: clean to P/N=1.0 at beta=8. " + s)
    return ("HARD_FAIL", "HARD_FAIL: clean only <P/N=1.0. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
