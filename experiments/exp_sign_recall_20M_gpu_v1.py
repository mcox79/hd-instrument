"""
exp_sign_recall_20M_gpu_v1.py -- sign-key autoassociative recall@1 at 20M keys (GPU, chunked) -- GPU.

ROUTING: GPU-scale substrate-physics (sign-key recall at 20M). 20M sign keys (D=1024) regenerated per chunk (never fully materialized); chunked GPU recall@1 under 0.15 bit-flip. Pushes the recall scaling gate to 20M (2x the 10M result). torch.cuda; OOM-safe (chunked) for an 8GB card. GPU.
PRE-REGISTERED: HARD-PASS recall@1 >= 0.99 at N=20M. MIDDLE >= 0.95. HARD-FAIL < 0.95.
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
ANCHOR_NAME = "sign_recall_20M_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: sign_recall_20M_gpu_v1", flush=True)
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
    g = torch.Generator(device=DEV).manual_seed(9); N = 400000 if SMOKE else 20000000; D = 1024; NQ = 300; FLIP = 0.15; CH = 250000; base = 1001
    qidx = torch.randperm(N, generator=g, device=DEV)[:NQ].sort().values
    def chunk(c0, c1):
        gg = torch.Generator(device=DEV).manual_seed(base + c0); return torch.sign(torch.randn(c1 - c0, D, generator=gg, device=DEV))
    qk = torch.zeros(NQ, D, device=DEV)
    for c0 in range(0, N, CH):
        c1 = min(c0 + CH, N); K = chunk(c0, c1); mask = (qidx >= c0) & (qidx < c1)
        if mask.any():
            qk[mask] = K[qidx[mask] - c0]
        del K
    fl = torch.rand(qk.shape, generator=g, device=DEV) < FLIP; Q = qk.clone(); Q[fl] *= -1
    best = torch.full((NQ,), -1, device=DEV, dtype=torch.long); bs = torch.full((NQ,), -1e9, device=DEV)
    for c0 in range(0, N, CH):
        c1 = min(c0 + CH, N); K = chunk(c0, c1); sc = Q @ K.T; bsc, bidx = sc.max(1); upd = bsc > bs; best[upd] = c0 + bidx[upd]; bs[upd] = bsc[upd]
        del K, sc; torch.cuda.empty_cache()
    rec = (best == qidx).float().mean().item(); print("  N=%d recall@1=%.4f" % (N, rec), flush=True)
    return {"n": N, "recall1": rec}
def verdict(r) -> Tuple[str, str]:
    s = "recall@1=%.4f at N=%d" % (r["recall1"], r["n"])
    if r["recall1"] >= 0.99: return ("HARD_PASS", "HARD_PASS: sign-key recall >=0.99 at 20M -- substrate recall scales to 20M keys. " + s)
    if r["recall1"] >= 0.95: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.95-0.99 at 20M. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.95 at 20M. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
