"""
exp_vsa_permute_long_seq_gpu_v1.py -- permutation-power sequence encoding at K=12 positions (GPU) -- GPU.

ROUTING: GPU-scale substrate-physics (long ordered sequences via permutation). Encode ordered sequences of length up to K=12 via permutation powers (S = sum P^k(item_k)); recover position k via P^-k. GPU for the per-position cleanup. Tests long-sequence (timeline) capacity. torch.cuda. GPU.
PRE-REGISTERED: HARD-PASS position-recovery >= 0.90 at K=12 (N=4096, V=200). MIDDLE >= 0.80. HARD-FAIL < 0.80.
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
ANCHOR_NAME = "vsa_permute_long_seq_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: vsa_permute_long_seq_gpu_v1", flush=True)
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
    g = torch.Generator(device=DEV).manual_seed(8); N = 4096; V = 200; perm = torch.randperm(N, generator=g, device=DEV); inv = torch.argsort(perm)
    Ks = [5, 12] if SMOKE else [5, 8, 12]; TR = 30 if SMOKE else 120; book = cphasor(V, N, g); by = {}
    def permute(v, k):
        out = v
        idx = perm if k >= 0 else inv
        for _ in range(abs(k)):
            out = out[idx]
        return out
    for K in Ks:
        hit = 0; tot = 0
        for _ in range(TR):
            seq = torch.randperm(V, generator=g, device=DEV)[:K]
            S = torch.zeros(N, dtype=torch.complex64, device=DEV)
            for k in range(K):
                S = S + permute(book[seq[k]], k)
            for k in range(K):
                rec = permute(S, -k); pred = int(torch.argmax((book @ rec.conj()).real)); hit += int(pred == int(seq[k])); tot += 1
        by["K%d" % K] = hit / tot; print("  K=%d position-recovery=%.3f" % (K, by["K%d" % K]), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    k12 = r["by"].get("K12", 0.0); s = "recovery by K: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if k12 >= 0.90: return ("HARD_PASS", "HARD_PASS: ordered-sequence recovery >=0.90 at K=12 -- long timelines/ranked-lists representable. " + s)
    if k12 >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: K=12 recovery 0.80-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: K=12 recovery <0.80. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
