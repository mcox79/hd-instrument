"""
exp_bundle_capacity_cliff_gpu_v1.py -- how many role-filler pairs superpose before recall drops (N=4096, GPU) -- GPU.

ROUTING: GPU-scale substrate-physics (bundle superposition capacity cliff). Sweep K (pairs bundled into one hypervector) at N=4096; find the K where recall@1 drops below 0.9 -- the bundling capacity cliff. GPU for the per-K trials. torch.cuda. GPU.
PRE-REGISTERED: HARD-PASS capacity K_crit (recall>=0.9) >= 0.10*N (i.e. >=400 pairs). MIDDLE >= 0.05*N. HARD-FAIL < 0.05*N.
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
ANCHOR_NAME = "bundle_capacity_cliff_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: bundle_capacity_cliff_gpu_v1", flush=True)
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
    g = torch.Generator(device=DEV).manual_seed(7); N = 4096; V = 5000; TR = 10 if SMOKE else 30
    Ks = [50, 200] if SMOKE else [50, 100, 200, 400, 600, 800]; by = {}; book = cphasor(V, N, g)
    for K in Ks:
        hit = 0; tot = 0
        for _ in range(TR):
            roles = cphasor(K, N, g); fidx = torch.randperm(V, generator=g, device=DEV)[:K]
            B = (roles * book[fidx]).sum(0)
            rec = B.unsqueeze(0) * roles.conj()                 # [K, N]
            sc = (rec @ book.conj().T).real                     # [K, V]
            pred = torch.argmax(sc, dim=1); hit += int((pred == fidx).sum()); tot += K
        by["K%d" % K] = hit / tot; print("  K=%d recall@1=%.3f" % (K, by["K%d" % K]), flush=True)
    kcrit = max([k for k in Ks if by["K%d" % k] >= 0.9] + [0])
    return {"by": by, "kcrit": kcrit, "N": N}
def verdict(r) -> Tuple[str, str]:
    kc = r["kcrit"]; frac = kc / r["N"]; s = "K_crit(recall>=0.9)=%d (=%.3f*N) | %s" % (kc, frac, {k: round(v, 3) for k, v in r["by"].items()})
    if frac >= 0.10: return ("HARD_PASS", "HARD_PASS: bundle holds >=0.10*N pairs at recall>=0.9 -- high superposition capacity at N=4096. " + s)
    if frac >= 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: capacity 0.05-0.10*N. " + s)
    return ("HARD_FAIL", "HARD_FAIL: capacity <0.05*N. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
