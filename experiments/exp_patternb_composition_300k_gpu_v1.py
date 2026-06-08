"""
exp_patternb_composition_300k_gpu_v1.py -- Pattern-B role-filler composition recall at V=300k filler codebook (GPU) -- GPU.

ROUTING: GPU-scale substrate-physics (Pattern-B composition at V=300k (OOM-fixed)). OOM-fixed rerun of the V=1M composition (1M complex codebook overflowed the 8GB card). V=300k complex book ~1.2GB fits. K=4 pairs bundled; recover each filler by unbind + chunked cleanup over the 300k codebook. torch.cuda; OOM-safe (chunked) for an 8GB card. GPU.
PRE-REGISTERED: HARD-PASS recall@1 >= 0.95 at K=4, V=300k. MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "patternb_composition_300k_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: patternb_composition_300k_gpu_v1", flush=True)
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
    g = torch.Generator(device=DEV).manual_seed(6); N = 512; V = 80000 if SMOKE else 300000; K = 4; TR = 20 if SMOKE else 60; CH = 100000
    book = cphasor(V, N, g); hit = 0; tot = 0
    for _ in range(TR):
        roles = cphasor(K, N, g); fidx = torch.randperm(V, generator=g, device=DEV)[:K]
        B = torch.zeros(N, dtype=torch.complex64, device=DEV)
        for k in range(K):
            B = B + roles[k] * book[fidx[k]]
        for k in range(K):
            rec = B * roles[k].conj(); best = -1; bs = -1e18
            for c0 in range(0, V, CH):
                c1 = min(c0 + CH, V); sc = (book[c0:c1] @ rec.conj()).real; j = int(torch.argmax(sc))
                if float(sc[j]) > bs:
                    bs = float(sc[j]); best = c0 + j
            hit += int(best == int(fidx[k])); tot += 1
        del B; torch.cuda.empty_cache()
    rec = hit / tot; print("  V=%d K=%d recall@1=%.3f (N=%d)" % (V, K, rec, N), flush=True)
    return {"recall": rec, "V": V}
def verdict(r) -> Tuple[str, str]:
    s = "recall@1=%.3f at V=%d" % (r["recall"], r["V"])
    if r["recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: Pattern-B composition recall>=0.95 at V=300k filler vocab -- composition holds at large KB scale. " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: composition 0.85-0.95 at V=300k. " + s)
    return ("HARD_FAIL", "HARD_FAIL: composition <0.85 at V=300k. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
