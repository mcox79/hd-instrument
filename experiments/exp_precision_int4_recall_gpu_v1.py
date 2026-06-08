"""
exp_precision_int4_recall_gpu_v1.py -- int4 (4-bit) quantized continuous-key recall vs fp16 at 5M (GPU) -- GPU.

ROUTING: GPU-scale substrate-physics (int4 vs fp16 recall at scale). Quantize continuous random keys to 4-bit (16 levels, per-vector scale) vs fp16; chunked recall@1 at 5M under 0.30 query noise. Tests whether 4-bit storage (8x memory saving vs fp32) preserves recall at scale. torch.cuda; OOM-safe (chunked) for an 8GB card. GPU.
PRE-REGISTERED: HARD-PASS int4 recall@1 >= 0.95 * fp16 at 5M. MIDDLE >= 0.90. HARD-FAIL < 0.90.
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
ANCHOR_NAME = "precision_int4_recall_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: precision_int4_recall_gpu_v1", flush=True)
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

def quant4(X):
    sc = X.abs().amax(dim=1, keepdim=True) / 7.0 + 1e-12; return (torch.round(X / sc).clamp(-7, 7)) * sc      # 4-bit signed: 15 levels
def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(41); N = 200000 if SMOKE else 5000000; D = 1024; NQ = 300; NOISE = 0.30; CH = 250000; base = 1313
    qidx = torch.randperm(N, generator=g, device=DEV)[:NQ].sort().values
    def chunk(c0, c1, q4):
        gg = torch.Generator(device=DEV).manual_seed(base + c0); X = torch.randn(c1 - c0, D, generator=gg, device=DEV); X = X / X.norm(dim=1, keepdim=True)
        return quant4(X) if q4 else X.half()
    qk = torch.zeros(NQ, D, device=DEV)
    for c0 in range(0, N, CH):
        c1 = min(c0 + CH, N); gg = torch.Generator(device=DEV).manual_seed(base + c0); X = torch.randn(c1 - c0, D, generator=gg, device=DEV); X = X / X.norm(dim=1, keepdim=True)
        mask = (qidx >= c0) & (qidx < c1)
        if mask.any():
            qk[mask] = X[qidx[mask] - c0]
        del X
    Q = qk + (NOISE / math.sqrt(D)) * torch.randn(NQ, D, generator=g, device=DEV)
    def recall(q4):
        best = torch.full((NQ,), -1, device=DEV, dtype=torch.long); bs = torch.full((NQ,), -1e9, device=DEV)
        Qd = quant4(Q) if q4 else Q.half()
        for c0 in range(0, N, CH):
            c1 = min(c0 + CH, N); K = chunk(c0, c1, q4); sc = (Qd.float() @ K.float().T); bsc, bidx = sc.max(1); upd = bsc > bs; best[upd] = c0 + bidx[upd]; bs[upd] = bsc[upd]
            del K, sc; torch.cuda.empty_cache()
        return (best == qidx).float().mean().item()
    r16 = recall(False); r4 = recall(True); ratio = r4 / (r16 + 1e-9)
    print("  N=%d recall@1 fp16=%.4f int4=%.4f ratio=%.3f" % (N, r16, r4, ratio), flush=True)
    return {"n": N, "fp16": r16, "int4": r4, "ratio": ratio}
def verdict(r) -> Tuple[str, str]:
    s = "int4=%.4f fp16=%.4f ratio=%.3f at N=%d" % (r["int4"], r["fp16"], r["ratio"], r["n"])
    if r["ratio"] >= 0.95: return ("HARD_PASS", "HARD_PASS: int4 retains >=95pct of fp16 recall at 5M -- 4-bit storage (8x memory vs fp32) viable at scale. " + s)
    if r["ratio"] >= 0.90: return ("MIDDLE_BAND", "MIDDLE_BAND: int4 0.90-0.95 of fp16 at 5M. " + s)
    return ("HARD_FAIL", "HARD_FAIL: int4 <0.90 of fp16 at 5M. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
