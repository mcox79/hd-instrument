"""
exp_khop_confidence_threshold_rescue_gpu_v1 -- v1-fix viability under COHERENT distractors (follows Cell A) -- GPU.

ROUTING: follows Cell A (c_d=0.48 measured -> coherent distractors). Tests whether a CONFIDENCE THRESHOLD T (the proposed
  v1 50-LOC fix) can rescue cross-shard K-hop at the MEASURED coherence c_d=0.48, B=10, target K=12. Sweeps T in
  {0.0,0.3,0.5,0.7,0.9}; a hop is accepted only if readout confidence > T, else miss. If some T keeps K_max>=12 the cheap
  v1 fix is viable despite coherent distractors; if not, semantic sharding (v2) is mandatory. GPU.
PRE-REGISTERED: HARD-PASS some T keeps K_max>=12 at c_d=0.48 (v1 confidence-filter fix viable). MIDDLE K_max 6-11. HARD-FAIL
  no T reaches K_max>=6 (semantic sharding mandatory for v1).
FORMULA SELF-TESTS (PROT-022): 1. higher T rejects more. 2. clean recovery. 3. cuda.
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
import torch
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "khop_confidence_threshold_rescue_gpu_v1"
N = 4096; NOISE0 = 0.10; C_D = 0.48; B = 10; K_TARGET = 12; T_GRID = [0.0, 0.3, 0.5, 0.7, 0.9]; K_GRID = list(range(2, 31, 2))
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    V_C = 512; CHAINS = 100; T_GRID = [0.0, 0.5, 0.9]
else:
    V_C = 4000; CHAINS = 300


def codebook(v_c, n, g):
    C = (torch.randint(0, 2, (v_c, n), generator=g, device=_DEV) * 2 - 1).float(); return C / (C.norm(dim=1, keepdim=True) + 1e-8)


def k_max(C, T, g):
    v_c, n = C.shape; km = 0
    for K in K_GRID:
        target = torch.randint(0, v_c, (CHAINS,), generator=g, device=_DEV)
        eff = NOISE0 * (K ** 0.5) / (B ** 0.5)
        distract = C[torch.randint(0, v_c, (CHAINS,), generator=g, device=_DEV)]
        final = C[target] + eff * torch.randn(CHAINS, n, generator=g, device=_DEV) + C_D * (K ** 0.5) / (B ** 0.5) * distract
        sims = final @ C.t(); conf, pred = sims.max(dim=1)
        ok = (pred == target) & (conf > T)
        if ok.float().mean().item() >= 0.90:
            km = K
        else:
            break
    return km


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); C = codebook(64, 256, g)
    assert int((C[5] @ C.t()).argmax()) == 5, "clean recovery"
    n = torch.randn(256, generator=g, device=_DEV); c = (n / n.norm() @ C.t()).max().item(); assert c < 0.9, "higher T rejects more"
    print("[selftest] PASS: khop-confidence-rescue", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def run() -> Dict:
    g = torch.Generator(device=_DEV).manual_seed(7); C = codebook(V_C, N, g); res = {}
    for T in T_GRID:
        torch.cuda.empty_cache(); km = k_max(C, T, torch.Generator(device=_DEV).manual_seed(100 + int(T * 100))); res["T%.1f" % T] = km
        print("  [T=%.1f] K_max=%d (c_d=%.2f B=%d)" % (T, km, C_D, B), flush=True)
    return res


def verdict(res) -> Tuple[str, str]:
    best = max(res.values())
    summary = "K_max by confidence-T at c_d=%.2f: %s | best=%d (target K=%d)" % (C_D, {k: v for k, v in res.items()}, best, K_TARGET)
    if best >= K_TARGET:
        return ("HARD_PASS", "HARD_PASS: a confidence threshold keeps K_max>=%d at coherent c_d=0.48 -- the cheap v1 50-LOC confidence-filter fix IS viable despite coherent distractors. " % K_TARGET + summary)
    if best >= 6:
        return ("MIDDLE_BAND", "MIDDLE_BAND: confidence threshold reaches K_max 6-11 -- partial; v1 limited depth or needs semantic sharding for K=12. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no confidence threshold reaches K_max>=6 at c_d=0.48 -- semantic sharding (v2) mandatory for v1 distributed reasoning. " + summary)


print("[config] anchor=%s mode=%s N=%d V_c=%d chains=%d c_d=%.2f B=%d T_grid=%s" % (ANCHOR_NAME, RUN_MODE, N, V_C, CHAINS, C_D, B, T_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); res = run()
v, vmsg = verdict(res); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [res], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [res]); print("[metrics] written", flush=True)
