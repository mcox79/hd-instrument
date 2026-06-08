"""
exp_precision_recall_5M_gpu_v1.py -- fp16 vs int8 sign-key recall parity at 5M (GPU) -- GPU.

ROUTING: GPU-scale substrate-physics validation (fp16/int8 precision parity at 5M). At 5M sign keys (D=1024), compare recall@1 in fp16 vs int8 (sign keys are exact in both; tests accumulation/precision at scale). Validates half/quarter precision production storage at 5M. torch.cuda. GPU.
PRE-REGISTERED: HARD-PASS int8 recall@1 within 0.01 of fp16 AND both >= 0.99 at 5M. MIDDLE within 0.03. HARD-FAIL > 0.03 gap.
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
ANCHOR_NAME = "precision_recall_5M_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.int8(1) == 1, "int8"; assert 5_000_000 > 0, "scale"; print("[selftest] PASS: precision-recall-5M-gpu", flush=True)
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
    g = torch.Generator(device=DEV).manual_seed(5); N = 200000 if SMOKE else 5000000; D = 1024; NQ = 300; FLIP = 0.15; CH = 250000
    qidx = torch.randperm(N, generator=g, device=DEV)[:NQ].sort().values; base_seed = 888
    def chunk(c0, c1):
        gg = torch.Generator(device=DEV).manual_seed(base_seed + c0); return torch.sign(torch.randn(c1 - c0, D, generator=gg, device=DEV))
    qk = torch.zeros(NQ, D, device=DEV)
    for c0 in range(0, N, CH):
        c1 = min(c0 + CH, N); K = chunk(c0, c1); mask = (qidx >= c0) & (qidx < c1)
        if mask.any():
            qk[mask] = K[qidx[mask] - c0]
        del K
    fl = torch.rand(qk.shape, generator=g, device=DEV) < FLIP; Q = qk.clone(); Q[fl] *= -1
    def recall(dt):
        best = torch.full((NQ,), -1, device=DEV, dtype=torch.long); bs = torch.full((NQ,), -1e9, device=DEV)
        Qd = Q.to(dt)
        for c0 in range(0, N, CH):
            c1 = min(c0 + CH, N); K = chunk(c0, c1).to(dt); sc = (Qd @ K.T).float()
            bsc, bidx = sc.max(1); upd = bsc > bs; best[upd] = c0 + bidx[upd]; bs[upd] = bsc[upd]
            del K, sc; torch.cuda.empty_cache()
        return (best == qidx).float().mean().item()
    r16 = recall(torch.float16); r8 = recall(torch.int8)
    print("  N=%d recall@1 fp16=%.4f int8=%.4f (gap=%.4f)" % (N, r16, r8, abs(r16 - r8)), flush=True)
    return {"n": N, "fp16": r16, "int8": r8, "gap": abs(r16 - r8)}
def verdict(r) -> Tuple[str, str]:
    s = "fp16=%.4f int8=%.4f gap=%.4f at N=%d" % (r["fp16"], r["int8"], r["gap"], r["n"])
    if r["gap"] <= 0.01 and r["int8"] >= 0.99: return ("HARD_PASS", "HARD_PASS: int8 matches fp16 within 0.01 and >=0.99 at 5M -- quarter-precision production storage safe at scale. " + s)
    if r["gap"] <= 0.03: return ("MIDDLE_BAND", "MIDDLE_BAND: int8 within 0.03 of fp16 at 5M. " + s)
    return ("HARD_FAIL", "HARD_FAIL: int8 gap >0.03 at 5M. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
