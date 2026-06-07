"""
exp_w_4bit_quantization_gpu_v1 -- storage-efficiency anchor 2 (4-bit W quantization) -- GPU.

ROUTING: handoff exp_dev_handoff_research_storage_efficiency #2. Quantize the W matrix to 4 bits (per-row absmax scale) for
  ~4x storage reduction; measure exact-recovery accuracy vs full-precision. GPU.
PRE-REGISTERED: HARD-PASS 4-bit recall >= fp32 recall - 0.03 (4x reduction near-free). MIDDLE 0.03-0.10 drop. HARD-FAIL >0.10
  (precision loss breaks retrieval).
FORMULA SELF-TESTS (PROT-022): 1. dense recall high. 2. quant preserves sign. 3. cuda.
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

ANCHOR_NAME = "w_4bit_quantization_gpu_v1"
ALPHA = 0.2; FLIP = 0.05; STEPS = 6
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_GRID = [4096, 8192] if RUN_MODE == "smoke" else [8192, 16384]


def hebb_W(P):
    W = (P.t() @ P); W.fill_diagonal_(0.0); return W / P.shape[1]


def quant4(W):
    scale = W.abs().amax(dim=1, keepdim=True) / 7.0 + 1e-12; q = torch.clamp(torch.round(W / scale), -8, 7); return q * scale   # 4-bit symmetric per-row


def recall(P, W, seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed)); M, n = P.shape
    s = P * torch.where(torch.rand(M, n, generator=g, device=_DEV) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = torch.sign(s @ W.t()); s[s == 0] = 1.0
    return float((s == P).all(dim=1).float().mean().item())


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); P = (torch.randint(0, 2, (20, 256), generator=g, device=_DEV) * 2 - 1).float()
    assert recall(P, hebb_W(P), 0) >= 0.9, "dense recall high"
    W = hebb_W(P); assert torch.sign(quant4(W)).eq(torch.sign(W)).float().mean() > 0.9, "quant preserves sign"
    print("[selftest] PASS: w-4bit", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def run() -> Dict:
    res = {}
    for n in N_GRID:
        torch.cuda.empty_cache(); g = torch.Generator(device=_DEV).manual_seed(7); M = max(4, int(ALPHA * n))
        P = (torch.randint(0, 2, (M, n), generator=g, device=_DEV) * 2 - 1).float(); W = hebb_W(P)
        fp = recall(P, W, 1); q4 = recall(P, quant4(W), 2)
        res["N%d" % n] = {"fp32": fp, "q4bit": q4, "drop": fp - q4}
        print("  [N=%d] fp32=%.3f 4bit=%.3f drop=%.4f" % (n, fp, q4, fp - q4), flush=True)
    return res


def verdict(res) -> Tuple[str, str]:
    nmax = "N%d" % N_GRID[-1]; drop = res[nmax]["drop"]
    summary = "at N=%d fp32=%.3f 4bit=%.3f drop=%.4f (4x storage reduction)" % (N_GRID[-1], res[nmax]["fp32"], res[nmax]["q4bit"], drop)
    if drop <= 0.03:
        return ("HARD_PASS", "HARD_PASS: 4-bit W quantization costs <=3pct accuracy -- 4x W storage reduction near-free. " + summary)
    if drop <= 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 4-bit costs 3-10pct accuracy. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: 4-bit precision loss >10pct -- breaks retrieval. " + summary)


print("[config] anchor=%s mode=%s N_grid=%s alpha=%.2f" % (ANCHOR_NAME, RUN_MODE, N_GRID, ALPHA), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); res = run()
v, vmsg = verdict(res); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [res], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [res]); print("[metrics] written", flush=True)
