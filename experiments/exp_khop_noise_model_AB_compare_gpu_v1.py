"""
exp_khop_noise_model_AB_compare_gpu_v1 -- K-hop noise-model fork resolver (Model A vs B side-by-side) -- GPU.

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

ANCHOR_NAME = "khop_noise_model_AB_compare_gpu_v1"
N = 4096; NOISE0 = 0.08; K_GRID = list(range(2, 61, 2)); B_GRID = [1, 2, 10, 30, 100]
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    V_C = 512; CHAINS = 100; K_GRID = list(range(2, 25, 3)); B_GRID = [1, 2, 10, 30]
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
    g = torch.Generator(device=_DEV).manual_seed(7); C = codebook(V_C, N, g); res = {}
    for model in ["averaging", "distractor"]:
        for B in B_GRID:
            torch.cuda.empty_cache(); km = k_max(C, model, B, K_GRID, CHAINS, torch.Generator(device=_DEV).manual_seed(100 + B))
            res["%s_B%d" % (model, B)] = km
            print("  [%s B=%d] K_max=%d" % (model, B, km), flush=True)
    return res


def _mono(vals):
    d = np.diff(vals); return "increasing" if np.all(d >= 0) and d.sum() > 0 else ("decreasing" if np.all(d <= 0) and d.sum() < 0 else "non-monotone")


def verdict(res) -> Tuple[str, str]:
    avg = [res["averaging_B%d" % b] for b in B_GRID]; dist = [res["distractor_B%d" % b] for b in B_GRID]
    ma = _mono(avg); md = _mono(dist)
    summary = "K_max(B): averaging=%s (%s) | distractor=%s (%s) | B_grid=%s" % (avg, ma, dist, md, B_GRID)
    if max(avg) > 0 and max(dist) > 0 and ma != md:
        return ("HARD_PASS", "HARD_PASS: both noise models computed and qualitatively DISTINGUISHABLE (averaging %s vs distractor %s) -- Research can resolve the cross-shard relay fork from these curves. " % (ma, md) + summary)
    if max(avg) > 0 and max(dist) > 0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: both curves computed but same monotonicity (fork not separable by this metric). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: a model collapsed to K_max=0 (uninformative; recalibrate noise0). " + summary)


print("[config] anchor=%s mode=%s N=%d V_c=%d chains=%d B=%s" % (ANCHOR_NAME, RUN_MODE, N, V_C, CHAINS, B_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); res = run()
v, vmsg = verdict(res); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [res], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [res]); print("[metrics] written", flush=True)
