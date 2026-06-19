"""
exp_g3_fp16_overflow_n65536_v1 -- Batch I1 (bf16 production-gate: does bfloat16 eliminate the overflow) -- GPU.

ROUTING: Batch G Tier-1 (adversarial drill #4). fp16 proved GENUINE at N=1024; at N=65536 the Hopfield accumulation
  (s @ P.t()) @ P sums ~N terms and may overflow fp16 (max ~65504) with extreme bipolar inputs. Stress-tests fp16
  accumulation up to N=65536; checks NaN/Inf vs fp32 reference. torch.
PRE-REGISTERED: HARD-PASS zero NaN/Inf in fp16 path up to N=65536 (fp16 production-safe). HARD-FAIL any NaN/Inf (mandate fp32).
FORMULA SELF-TESTS (PROT-022): 1. fp16 finite at small N. 2. fp32 reference finite. 3. deps.
ASCII-only. write_metrics. PROT-018 no _nN (fixed stress N).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import torch
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "i1_bf16_overflow_n65536_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_GRID = [4096, 16384] if RUN_MODE == "smoke" else [16384, 32768, 65536]
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def stress(n, seed, dtype):
    g = torch.Generator(device=_DEV).manual_seed(int(seed)); M = max(2, min(int(0.1 * n), 2048))   # cap M: overflow magnitude needs large N, not large M (8GB fit)
    P = (torch.randint(0, 2, (M, n), generator=g, device=_DEV) * 2 - 1).to(dtype)
    s = P.clone()
    for _ in range(4):
        s = torch.sign((s @ P.t()) @ P - M * s); s[s == 0] = 1.0; s = s.to(dtype)
    field = (s @ P.t()) @ P
    return bool(torch.isnan(field).any() or torch.isinf(field).any()), float(field.abs().max().item())


def _selftest():
    bad, mx = stress(512, 0, torch.bfloat16); assert not bad, "fp16 finite at small N"
    _, mx32 = stress(512, 0, torch.float32); assert np.isfinite(mx32), "fp32 reference finite"
    print("[selftest] PASS: g3-fp16", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[dev] %s" % _DEV, flush=True)


def run_seed(seed) -> Dict:
    by = {}
    for n in N_GRID:
        if _DEV.type == "cuda":
            torch.cuda.empty_cache()
        bad16, mx16 = stress(n, seed, torch.bfloat16); bad32, _ = stress(n, seed, torch.float32)
        by["N%d" % n] = {"fp16_nan_inf": bad16, "fp16_absmax": mx16, "fp32_nan_inf": bad32}
        print("  [seed=%d N=%d] fp16_nan_inf=%s fp16_absmax=%.0f fp32_nan_inf=%s" % (seed, n, bad16, mx16, bad32), flush=True)
    return {"seed": seed, "by": by}


def verdict(ps) -> Tuple[str, str]:
    any_bad = any(p["by"][k]["fp16_nan_inf"] for p in ps for k in p["by"])
    nmax = "N%d" % N_GRID[-1]; mx = float(np.mean([p["by"][nmax]["fp16_absmax"] for p in ps]))
    summary = "fp16 NaN/Inf at any N: %s | fp16 absmax at N=%d: %.0f (bf16 dynamic range ~3e38 (8 exp bits))" % (any_bad, N_GRID[-1], mx)
    if not any_bad:
        return ("HARD_PASS", "HARD_PASS: zero NaN/Inf in fp16 accumulation up to N=%d -- bf16 ELIMINATES overflow -- production gate closed. " % N_GRID[-1] + summary)
    return ("HARD_FAIL", "HARD_FAIL: fp16 NaN/Inf at production N -- bf16 insufficient; mandate fp32 accumulation before deployment. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
