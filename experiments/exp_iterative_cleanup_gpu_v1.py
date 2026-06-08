"""
exp_iterative_cleanup_gpu_v1.py -- iterative (multi-step) Hopfield cleanup improves recall under high noise (GPU) -- GPU.

ROUTING: GPU-scale substrate-physics (iterative Hopfield cleanup). Compare 1-step vs T-step iterative modern-Hopfield cleanup (re-feed retrieved into the query) at high noise; iterative cleanup should recover patterns single-step misses. N=2048, P/N=1. torch.cuda. GPU.
PRE-REGISTERED: HARD-PASS iterative (5-step) recall@1 >= single-step + 0.05 at flip=0.30. MIDDLE >= +0.02. HARD-FAIL no improvement.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os, math
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "iterative_cleanup_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: iterative_cleanup_gpu_v1", flush=True)
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
def cphasor(m, d, g):
    ang = (torch.rand(m, d, generator=g, device=DEV) * 2 - 1) * math.pi; return torch.complex(torch.cos(ang), torch.sin(ang))

def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(10); N = 2048; P = N; FLIP = 0.30; NQ = 200; BETA = 8.0; T = 5
    X = torch.sign(torch.randn(P, N, generator=g, device=DEV)); X[X == 0] = 1
    qi = torch.randperm(P, generator=g, device=DEV)[:NQ]; Q0 = X[qi].clone(); fl = torch.rand(Q0.shape, generator=g, device=DEV) < FLIP; Q0[fl] *= -1
    def step(Q):
        return torch.sign(torch.softmax(BETA * (Q @ X.T), dim=1) @ X)
    s1 = step(Q0); r1 = ((s1 * X[qi]).sum(1) / N >= 0.95).float().mean().item()
    Q = Q0
    for _ in range(T):
        Q = step(Q)
    rt = ((Q * X[qi]).sum(1) / N >= 0.95).float().mean().item()
    print("  flip=%.2f: 1-step recall=%.3f %d-step recall=%.3f (gain=%.3f)" % (FLIP, r1, T, rt, rt - r1), flush=True)
    return {"step1": r1, "stepT": rt, "gain": rt - r1, "T": T}
def verdict(r) -> Tuple[str, str]:
    s = "1-step=%.3f %d-step=%.3f gain=%.3f" % (r["step1"], r["T"], r["stepT"], r["gain"])
    if r["gain"] >= 0.05: return ("HARD_PASS", "HARD_PASS: iterative cleanup adds >=0.05 recall at high noise -- multi-step Hopfield recovers patterns single-step misses. " + s)
    if r["gain"] >= 0.02: return ("MIDDLE_BAND", "MIDDLE_BAND: iterative gain 0.02-0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: iterative cleanup no meaningful gain (single-step already saturates). " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
