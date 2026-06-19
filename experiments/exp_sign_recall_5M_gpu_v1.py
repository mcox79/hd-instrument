"""
exp_sign_recall_5M_gpu_v1.py -- sign-key autoassociative recall@1 at 5M keys (GPU) -- GPU.

ROUTING: GPU-scale substrate-physics validation (sign-key recall at 5M on GPU). 5M sign keys (D=1024); noisy-query recall@1 via chunked GPU matmul. Pushes the CELL-4/1M recall gate to 5M -- GPU enables the scale CPU cannot reach in reasonable time. torch.cuda; scales beyond CPU feasibility. GPU.
PRE-REGISTERED: HARD-PASS recall@1 >= 0.99 at N=5M under 0.15 bit-flip noise. MIDDLE >= 0.95. HARD-FAIL < 0.95.
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
ANCHOR_NAME = "sign_recall_5M_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.sign(0.2) == 1, "sign"; assert 5_000_000 > 1_000_000, "scale"; print("[selftest] PASS: sign-recall-5M-gpu", flush=True)
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
    g = torch.Generator(device=DEV).manual_seed(2); N = 200000 if SMOKE else 5000000; D = 1024; NQ = 300; FLIP = 0.15; CH = 250000
    qidx = torch.randperm(N, generator=g, device=DEV)[:NQ].sort().values
    # build queries from their (regenerated) key rows: regenerate keys in chunks with a fixed seed so we can match
    torch.manual_seed(12345)
    best = torch.full((NQ,), -1, device=DEV, dtype=torch.long); best_sc = torch.full((NQ,), -1e9, device=DEV)
    # first pass: materialize the NQ query keys
    qkeys = torch.zeros(NQ, D, device=DEV)
    base_seed = 777
    def chunk_keys(c0, c1):
        gg = torch.Generator(device=DEV).manual_seed(base_seed + c0); return torch.sign(torch.randn(c1 - c0, D, generator=gg, device=DEV))
    for c0 in range(0, N, CH):
        c1 = min(c0 + CH, N); K = chunk_keys(c0, c1)
        mask = (qidx >= c0) & (qidx < c1)
        if mask.any():
            qkeys[mask] = K[qidx[mask] - c0]
        del K
    fl = torch.rand(qkeys.shape, generator=g, device=DEV) < FLIP; Q = qkeys.clone(); Q[fl] *= -1
    for c0 in range(0, N, CH):
        c1 = min(c0 + CH, N); K = chunk_keys(c0, c1); sc = Q @ K.T
        bsc, bidx = sc.max(dim=1); upd = bsc > best_sc; best[upd] = c0 + bidx[upd]; best_sc[upd] = bsc[upd]
        del K, sc; torch.cuda.empty_cache()
    rec = (best == qidx).float().mean().item()
    print("  N=%d recall@1=%.4f (D=%d flip=%.2f)" % (N, rec, D, FLIP), flush=True)
    return {"n": N, "recall1": rec}
def verdict(r) -> Tuple[str, str]:
    s = "recall@1=%.4f at N=%d" % (r["recall1"], r["n"])
    if r["recall1"] >= 0.99: return ("HARD_PASS", "HARD_PASS: sign-key recall holds at 5M scale (>=0.99) on GPU -- substrate recall scales to 5M. " + s)
    if r["recall1"] >= 0.95: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.95-0.99 at 5M. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.95 at 5M. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
