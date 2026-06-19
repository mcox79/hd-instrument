"""
exp_khop_noise_model_AB_compare_gpu_v1 -- K-hop K_max vs dimension N scaling (Model A averaging, B=10) -- GPU. NOTE: assumes averaging model pending fork resolution.

ROUTING: Exp-Dev fork-resolution (see notes/exp_dev_to_research_khop_noise_model_fork). Rather than only escalate + wait,
  run BOTH candidate cross-shard relay noise models head-to-head so Research can pick the one matching the architecture:
  - Model A (superposition averaging): B shards return noisy copies of the SAME target; coordinator averages -> per-hop
    noise ~ noise0/sqrt(B). Prediction: K_max INCREASES with B.
  - Model B (distractor fan-out): fan-out hits B shards, 1 true + (B-1) attenuated distractors bundled in -> per-hop noise
    ~ noise0*sqrt(B-1). Prediction (Drill 3): K_max DECREASES with B.
  Reports K_max(B) for both models across B in {1,2,10,30,100}. GPU (matmul battery; W-free).
PRE-REGISTERED: this is a MODEL-SELECTION battery, not a pass/fail capability test. HARD-PASS = both curves computed cleanly
  AND they are qualitatively DISTINGUISHABLE (opposite monotonicity), so Research can decide. HARD-FAIL = a model crashes or
  both collapse to K_max=0 (uninformative).
FORMULA SELF-TESTS (PROT-022): 1. averaging noise < distractor noise at B>1. 2. clean recovery. 3. cuda.
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

ANCHOR_NAME = "khop_dim_scaling_gpu_v1"
NOISE0 = 0.08; K_GRID = list(range(2, 61, 2)); N_GRID = [2048, 4096, 8192, 16384]; B_FIX = 10
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    V_C = 512; CHAINS = 100; K_GRID = list(range(2, 25, 3)); N_GRID = [2048, 4096]; B_FIX = 10
else:
    V_C = 4000; CHAINS = 400


def codebook(v_c, n, g):
    C = (torch.randint(0, 2, (v_c, n), generator=g, device=_DEV) * 2 - 1).float(); return C / (C.norm(dim=1, keepdim=True) + 1e-8)


def eff_std(model, B, K):
    if model == "averaging":
        return NOISE0 * (K ** 0.5) / (B ** 0.5)
    return NOISE0 * (K ** 0.5) * (max(B - 1, 1) ** 0.5)             # distractor: noise grows with fan-out


def k_max(C, model, B, K_grid, chains, g):
    v_c, n = C.shape; km = 0
    for K in K_grid:
        target = torch.randint(0, v_c, (chains,), generator=g, device=_DEV)
        final = C[target] + eff_std(model, B, K) * torch.randn(chains, n, generator=g, device=_DEV)
        rec = ((final @ C.t()).argmax(dim=1) == target).float().mean().item()
        if rec >= 0.90:
            km = K
        else:
            break
    return km


def _selftest():
    assert eff_std("averaging", 10, 4) < eff_std("distractor", 10, 4), "averaging noise < distractor at B>1"
    g = torch.Generator(device=_DEV).manual_seed(0); C = codebook(64, 256, g)
    assert int((C[5] @ C.t()).argmax()) == 5, "clean recovery"
    print("[selftest] PASS: khop-AB-compare", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def run() -> Dict:
    res = {}
    for n in N_GRID:
        torch.cuda.empty_cache(); g = torch.Generator(device=_DEV).manual_seed(7); C = codebook(V_C, n, g)
        km = k_max(C, "averaging", B_FIX, K_GRID, CHAINS, torch.Generator(device=_DEV).manual_seed(100 + n))
        res["N%d" % n] = km; print("  [N=%d] K_max=%d" % (n, km), flush=True)
    return res


def _mono(vals):
    d = np.diff(vals); return "increasing" if np.all(d >= 0) and d.sum() > 0 else ("decreasing" if np.all(d <= 0) and d.sum() < 0 else "non-monotone")


def verdict(res) -> Tuple[str, str]:
    km = [res["N%d" % n] for n in N_GRID]; mono = _mono(km)
    summary = "K_max by N: %s (%s) | N_grid=%s" % (km, mono, N_GRID)
    if mono == "increasing" and km[-1] >= 18:
        return ("HARD_PASS", "HARD_PASS: K_max grows with dimension N (more codebook separation -> deeper hops); high-N substrate extends K-hop depth. " + summary)
    if max(km) > 0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: K_max computed but weak/flat N-scaling. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: K_max=0 (recalibrate). " + summary)


print("[config] anchor=%s mode=%s N_grid=%s V_c=%d chains=%d B_fix=%d" % (ANCHOR_NAME, RUN_MODE, N_GRID, V_C, CHAINS, B_FIX), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); res = run()
v, vmsg = verdict(res); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [res], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [res]); print("[metrics] written", flush=True)
