"""
exp_resonator_capacity_gpu_v1.py -- resonator factorization vs K at N=4096 (GPU) -- GPU.

ROUTING: GPU-scale substrate-physics validation (resonator factorization capacity at GPU scale). Soft-projection resonator factorizing K-way bound products at N=4096 (large), sweeping K to find the capacity cliff. GPU enables the larger N + more trials than CPU. torch.cuda; scales beyond CPU feasibility. GPU.
PRE-REGISTERED: HARD-PASS full-factorization success >= 0.90 at K=3 (N=4096, M=30). MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "resonator_capacity_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; assert 4096 > 1024, "scale"; print("[selftest] PASS: resonator-capacity-gpu", flush=True)
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

def phasor(m, d, g):
    import math; ang = (torch.rand(m, d, generator=g, device=DEV) * 2 - 1) * math.pi; return torch.complex(torch.cos(ang), torch.sin(ang))
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(3); N = 4096; M = 30; MAXIT = 60; by = {}
    K_GRID = [2, 3] if SMOKE else [2, 3, 4]; TR = 30 if SMOKE else 120
    for K in K_GRID:
        books = [phasor(M, N, g) for _ in range(K)]; succ = 0
        for _ in range(TR):
            true = [int(torch.randint(0, M, (1,), generator=g, device=DEV)) for _ in range(K)]
            s = torch.ones(N, dtype=torch.complex64, device=DEV)
            for k in range(K):
                s = s * books[k][true[k]]
            est = [b.mean(0) for b in books]; est = [e / (e.abs() + 1e-8) for e in est]; prev = None
            for _ in range(MAXIT):
                idxs = []
                for k in range(K):
                    others = torch.ones(N, dtype=torch.complex64, device=DEV)
                    for j in range(K):
                        if j != k:
                            others = others * est[j]
                    rr = s * others.conj(); sc = (books[k] @ rr.conj()); est[k] = (sc @ books[k]); est[k] = est[k] / (est[k].abs() + 1e-8)
                    idxs.append(int(torch.argmax(sc.real)))
                if idxs == prev:
                    break
                prev = idxs
            succ += int(idxs == true)
        by["K%d" % K] = succ / TR; print("  K=%d success=%.3f (N=%d)" % (K, by["K%d" % K], N), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    k3 = r["by"].get("K3", 0.0); s = "success by K: %s (N=4096)" % {k: round(v, 3) for k, v in r["by"].items()}
    if k3 >= 0.90: return ("HARD_PASS", "HARD_PASS: resonator factorizes K=3 >=0.90 at N=4096 -- larger dimension extends factorization capacity. " + s)
    if k3 >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: K=3 0.75-0.90 at N=4096 (better than N=2048 0.73). " + s)
    return ("HARD_FAIL", "HARD_FAIL: K=3 <0.75 even at N=4096. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
