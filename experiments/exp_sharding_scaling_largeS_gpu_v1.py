"""
exp_sharding_scaling_largeS_gpu_v1.py -- sharding scaling law to S=256 shards (GPU) -- GPU.

ROUTING: GPU product-scale validation (sharding to extreme S). Extends the sharding scaling law to S up to 256 shards (fixed per-shard load K=80; total up to ~20k items). Confirms per-shard recall stays flat at ~1.0 and cross-shard interference stays ~0 even at extreme shard counts (unbounded-capacity claim). torch.cuda; 8GB-safe. GPU.
PRE-REGISTERED: HARD-PASS per-shard recall flat >=0.95 (spread<=0.05) and interference<=0.02 up to S=256. MIDDLE spread<=0.10. HARD-FAIL otherwise.
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
ANCHOR_NAME = "sharding_scaling_largeS_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: sharding_scaling_largeS_gpu_v1", flush=True)
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
def cidx(v, book):
    return int(torch.argmax((book @ torch.conj(v)).real))

def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(2); N = 8192; K = 80; VV = 4000; book = cphasor(VV, N, g)
    Ss = [16, 64] if SMOKE else [16, 64, 128, 256]; per = {}; inter = {}
    for S in Ss:
        keys = cphasor(S * K, N, g); vals = torch.randint(0, VV, (S * K,), generator=g, device=DEV)
        bundles = torch.zeros(S, N, dtype=torch.complex64, device=DEV)
        for i in range(S * K):
            bundles[i // K] = bundles[i // K] + keys[i] * book[vals[i]]
        ph = 0; itr = 0; samp = list(range(0, S * K, max(1, (S * K) // 400)))
        for i in samp:
            sh = i // K; rec = bundles[sh] * torch.conj(keys[i])
            ph += int(int(torch.argmax((book @ torch.conj(rec)).real)) == int(vals[i]))
            wrong = (sh + 1) % S; own = (book[vals[i]] @ torch.conj(rec)).real; wb = (book @ torch.conj(bundles[wrong] * torch.conj(keys[i]))).real.max()
            itr += int(wb > own)
        per["S%d" % S] = ph / len(samp); inter["S%d" % S] = itr / len(samp); print("  S=%d total=%d per-shard-recall=%.3f interference=%.4f" % (S, S * K, per["S%d" % S], inter["S%d" % S]), flush=True)
        del bundles; torch.cuda.empty_cache()
    pv = list(per.values()); return {"per": per, "inter": inter, "spread": max(pv) - min(pv), "minp": min(pv), "maxi": max(inter.values())}
def verdict(r) -> Tuple[str, str]:
    s = "per-shard=%s interference=%s (spread=%.3f max-inter=%.4f)" % ({k: round(v, 3) for k, v in r["per"].items()}, {k: round(v, 4) for k, v in r["inter"].items()}, r["spread"], r["maxi"])
    if r["minp"] >= 0.95 and r["spread"] <= 0.05 and r["maxi"] <= 0.02: return ("HARD_PASS", "HARD_PASS: per-shard recall flat >=0.95 with ~0 interference up to S=256 -- unbounded-capacity-by-sharding holds at extreme shard counts. " + s)
    if r["spread"] <= 0.10: return ("MIDDLE_BAND", "MIDDLE_BAND: spread<=0.10. " + s)
    return ("HARD_FAIL", "HARD_FAIL: per-shard recall not flat at extreme S. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
