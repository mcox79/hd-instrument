"""
exp_khop_noise_model_AB_compare_gpu_v1 -- K-hop K_max vs codebook size V_C scaling (Model A averaging, B=10) -- GPU. NOTE: assumes averaging model pending fork resolution.

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

ANCHOR_NAME = "khop_vc_scaling_gpu_v1"
N = 4096; NOISE0 = 0.08; K_GRID = list(range(2, 61, 2)); VC_GRID = [500, 2000, 8000, 32000]; B_FIX = 10
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    CHAINS = 100; K_GRID = list(range(2, 25, 3)); VC_GRID = [500, 4000]; B_FIX = 10
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
    for vc in VC_GRID:
        torch.cuda.empty_cache(); g = torch.Generator(device=_DEV).manual_seed(7); C = codebook(vc, N, g)
        km = k_max(C, "averaging", B_FIX, K_GRID, CHAINS, torch.Generator(device=_DEV).manual_seed(100 + vc))
        res["VC%d" % vc] = km; print("  [V_C=%d] K_max=%d" % (vc, km), flush=True)
    return res


def _mono(vals):
    d = np.diff(vals); return "increasing" if np.all(d >= 0) and d.sum() > 0 else ("decreasing" if np.all(d <= 0) and d.sum() < 0 else "non-monotone")


def verdict(res) -> Tuple[str, str]:
    km = [res["VC%d" % vc] for vc in VC_GRID]; mono = _mono(km)
    summary = "K_max by V_C: %s (%s) | VC_grid=%s" % (km, mono, VC_GRID)
    if km[-1] >= 10:
        return ("HARD_PASS", "HARD_PASS: K_max stays >=10 even at large KB (V_C=%d) -- deep K-hop survives production-scale knowledge bases. " % VC_GRID[-1] + summary)
    if max(km) > 0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: K_max degrades with KB size (distractor floor rises). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: K_max=0 at scale (recalibrate). " + summary)


print("[config] anchor=%s mode=%s N=%d VC_grid=%s chains=%d B_fix=%d" % (ANCHOR_NAME, RUN_MODE, N, VC_GRID, CHAINS, B_FIX), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); res = run()
v, vmsg = verdict(res); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [res], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [res]); print("[metrics] written", flush=True)
