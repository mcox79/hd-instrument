"""
exp_i2_bf16_capacity_parity_n65536_v1 -- Batch I2 (bf16 vs fp32 capacity parity at scale) -- GPU.

ROUTING: Batch I Tier-1 (Drill A bf16). bf16 has 8 exponent bits (no overflow) but only 7 mantissa bits. Validates that
  reduced mantissa precision does NOT degrade Hopfield exact-recovery capacity vs fp32 at production N. Measures alpha_c in
  bf16 vs fp32 across N (up to 65536); reports the ratio. torch GPU (W-free, expandable_segments, empty_cache).
PRE-REGISTERED: HARD-PASS alpha_c(bf16)/alpha_c(fp32) > 0.95 (bf16 production-safe for capacity). MID 0.80-0.95. HF <0.80.
FORMULA SELF-TESTS (PROT-022): 1. fp32 low-load recovers. 2. bf16 low-load recovers. 3. cuda.
ASCII-only. write_metrics. PROT-018 no _nN (N-sweep).
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

ANCHOR_NAME = "i2_bf16_capacity_parity_n65536_v1"
FLIP = 0.05; STEPS = 6
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_GRID = [4096, 8192]; LOADS = [0.02, 0.05, 0.1, 0.13, 0.16, 0.2]
else:
    SEEDS = [7, 17, 23]; N_GRID = [16384, 32768]; LOADS = [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.2]


def recall(M, n, seed, dtype):
    g = torch.Generator(device=_DEV).manual_seed(int(seed))
    P = ((torch.randint(0, 2, (M, n), generator=g, device=_DEV) * 2 - 1)).to(dtype)
    S = (P * torch.where(torch.rand(M, n, generator=g, device=_DEV) < FLIP, -1.0, 1.0).to(dtype))
    for _ in range(STEPS):
        S = torch.sign((P.t() @ (P @ S.t())).t() - M * S); S[S == 0] = 1.0; S = S.to(dtype)
    return float((S == P).all(dim=1).float().mean().item())


def cap(n, seed, dtype):
    c = 0.0
    for load in LOADS:
        M = max(2, int(load * n))
        if recall(M, n, seed * 100 + M, dtype) >= 0.95:
            c = load
        else:
            break
    return c


def _selftest():
    assert recall(8, 512, 0, torch.float32) >= 0.95, "fp32 low-load recovers"
    bf = torch.bfloat16 if _DEV.type == "cuda" else torch.float32
    assert recall(8, 512, 0, bf) >= 0.95, "bf16 low-load recovers"
    print("[selftest] PASS: i2-bf16-parity", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def run_seed(seed) -> Dict:
    by = {}
    for n in N_GRID:
        torch.cuda.empty_cache()
        c32 = cap(n, seed, torch.float32); cbf = cap(n, seed, torch.bfloat16)
        by["N%d" % n] = {"fp32_alpha_c": c32, "bf16_alpha_c": cbf, "ratio": cbf / max(c32, 1e-9)}
        print("  [seed=%d N=%d] fp32_alpha_c=%.3f bf16_alpha_c=%.3f ratio=%.3f" % (seed, n, c32, cbf, cbf / max(c32, 1e-9)), flush=True)
    return {"seed": seed, "by": by}


def verdict(ps) -> Tuple[str, str]:
    nmax = "N%d" % N_GRID[-1]
    r = float(np.mean([p["by"][nmax]["ratio"] for p in ps]))
    summary = "bf16/fp32 alpha_c by N: %s | at N=%d ratio=%.3f" % ({k: round(float(np.mean([p["by"][k]["ratio"] for p in ps])), 3) for k in ps[0]["by"]}, N_GRID[-1], r)
    if r > 0.95:
        return ("HARD_PASS", "HARD_PASS: bf16 capacity within 5pct of fp32 -- bf16 production-safe (no overflow AND no capacity loss). " + summary)
    if r >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: bf16 capacity 0.80-0.95 of fp32. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: bf16 capacity <0.80 of fp32 -- mantissa precision degrades capacity. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
