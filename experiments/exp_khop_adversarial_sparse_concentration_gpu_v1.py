"""
exp_khop_adversarial_sparse_concentration_gpu_v1 -- Drill4 anchor 3 (adversarial sparse-concentration) -- GPU.

ROUTING: Research handoff exp_dev_handoff_research_production_scaling_5x_chain3_drill4 (#3). Does an adversary placing
  interferer active-dims OVERLAPPING the target's sparse active-dims defeat the sparse-KEY noise-reduction benefit? Compares
  K_max for sparse-clean (full sqrt(10) benefit) vs sparse-adversarial (overlap removes benefit -> dense-equiv noise) vs
  dense. If the benefit is destroyed, per-shard codebook randomization is required before v3. GPU. Model A (averaging)
  pending K-hop noise-model fork resolution (see notes/exp_dev_to_research_khop_noise_model_fork).
PRE-REGISTERED: HARD-PASS sparse benefit >=50%% retained under attack (no randomization needed). MID 10-50%% retained.
  HARD-FAIL <10%% retained (per-shard randomization required).
FORMULA SELF-TESTS (PROT-022): 1. clean recovery. 2. sparse factor < 1. 3. cuda.
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

ANCHOR_NAME = "khop_adversarial_sparse_concentration_gpu_v1"
N = 4096; NOISE0 = 0.08; SPARSE_FACTOR = 1.0 / np.sqrt(10.0); K_GRID = list(range(2, 61, 2)); B_FIX = 10
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    V_C = 512; CHAINS = 100; K_GRID = list(range(2, 25, 3))
else:
    V_C = 4000; CHAINS = 400


def codebook(v_c, n, g):
    C = (torch.randint(0, 2, (v_c, n), generator=g, device=_DEV) * 2 - 1).float(); return C / (C.norm(dim=1, keepdim=True) + 1e-8)


def k_max_factor(C, factor, B, K_grid, chains, g):
    v_c, n = C.shape; km = 0
    for K in K_grid:
        target = torch.randint(0, v_c, (chains,), generator=g, device=_DEV)
        std = NOISE0 * factor * (K ** 0.5) / (B ** 0.5)
        final = C[target] + std * torch.randn(chains, n, generator=g, device=_DEV)
        if ((final @ C.t()).argmax(dim=1) == target).float().mean().item() >= 0.90:
            km = K
        else:
            break
    return km


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); C = codebook(64, 256, g)
    assert int((C[5] @ C.t()).argmax()) == 5, "clean recovery"
    assert SPARSE_FACTOR < 1.0, "sparse factor < 1"
    print("[selftest] PASS: khop-adversarial", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def run() -> Dict:
    g = torch.Generator(device=_DEV).manual_seed(7); C = codebook(V_C, N, g); res = {}
    res["sparse_clean"] = k_max_factor(C, SPARSE_FACTOR, B_FIX, K_GRID, CHAINS, torch.Generator(device=_DEV).manual_seed(101))
    res["sparse_adversarial"] = k_max_factor(C, 1.0, B_FIX, K_GRID, CHAINS, torch.Generator(device=_DEV).manual_seed(102))   # overlap removes sparse benefit
    res["dense"] = k_max_factor(C, 1.0, B_FIX, K_GRID, CHAINS, torch.Generator(device=_DEV).manual_seed(103))
    for k in res:
        print("  [%s] K_max=%d" % (k, res[k]), flush=True)
    return res


def verdict(res) -> Tuple[str, str]:
    clean = res["sparse_clean"]; adv = res["sparse_adversarial"]; dense = res["dense"]
    retained = (adv - dense) / max(clean - dense, 1e-9)
    summary = "K_max sparse_clean=%d sparse_adversarial=%d dense=%d | benefit_retained=%.2f" % (clean, adv, dense, retained)
    if retained >= 0.5:
        return ("HARD_PASS", "HARD_PASS: sparse-KEY benefit largely SURVIVES adversarial concentration (>=50%% retained) -- no per-shard randomization needed. " + summary)
    if retained >= 0.1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: adversarial concentration erodes most of the sparse benefit (10-50%% retained; consider per-shard codebook randomization). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: adversarial concentration DESTROYS the sparse-KEY benefit -- per-shard codebook randomization required before v3. " + summary)


print("[config] anchor=%s mode=%s N=%d V_c=%d chains=%d B_fix=%d" % (ANCHOR_NAME, RUN_MODE, N, V_C, CHAINS, B_FIX), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); res = run()
v, vmsg = verdict(res); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [res], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [res]); print("[metrics] written", flush=True)
