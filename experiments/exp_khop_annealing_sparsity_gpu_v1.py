"""
exp_khop_annealing_sparsity_gpu_v1 -- Drill4 anchor 4 (non-uniform sparsity schedule) -- GPU.

ROUTING: Research handoff exp_dev_handoff_research_production_scaling_5x_chain3_drill4 (#4). Compares uniform sparse
  alpha=0.005 intermediates vs an ANNEALED per-hop schedule (sparser at later hops where accumulated noise dominates).
  If annealing extends K_max, it replaces uniform sparse as the default. GPU. Model A (averaging) pending K-hop noise-model
  fork resolution (see notes/exp_dev_to_research_khop_noise_model_fork).
PRE-REGISTERED: HARD-PASS annealed K_max >= uniform + 15%% (annealing is the new default). MID annealed >= uniform.
  HARD-FAIL annealed < uniform (keep uniform).
FORMULA SELF-TESTS (PROT-022): 1. clean recovery. 2. schedule decreasing factor. 3. cuda.
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

ANCHOR_NAME = "khop_annealing_sparsity_gpu_v1"
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


def uniform_factor(h, K):
    return SPARSE_FACTOR


def annealed_factor(h, K):
    return SPARSE_FACTOR * (1.0 - 0.5 * h / max(K, 1))              # sparser (lower noise) at later hops


def k_max_sched(C, sched, B, K_grid, chains, g):
    v_c, n = C.shape; km = 0
    for K in K_grid:
        target = torch.randint(0, v_c, (chains,), generator=g, device=_DEV)
        var = 0.0
        for h in range(1, K + 1):
            var += (NOISE0 * sched(h, K) / (B ** 0.5)) ** 2          # accumulate per-hop noise variance
        final = C[target] + (var ** 0.5) * torch.randn(chains, n, generator=g, device=_DEV)
        if ((final @ C.t()).argmax(dim=1) == target).float().mean().item() >= 0.90:
            km = K
        else:
            break
    return km


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); C = codebook(64, 256, g)
    assert int((C[5] @ C.t()).argmax()) == 5, "clean recovery"
    assert annealed_factor(8, 10) < annealed_factor(1, 10), "schedule decreasing factor"
    print("[selftest] PASS: khop-annealing", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def run() -> Dict:
    g = torch.Generator(device=_DEV).manual_seed(7); C = codebook(V_C, N, g); res = {}
    res["uniform"] = k_max_sched(C, uniform_factor, B_FIX, K_GRID, CHAINS, torch.Generator(device=_DEV).manual_seed(101))
    res["annealed"] = k_max_sched(C, annealed_factor, B_FIX, K_GRID, CHAINS, torch.Generator(device=_DEV).manual_seed(102))
    for k in res:
        print("  [%s] K_max=%d" % (k, res[k]), flush=True)
    return res


def verdict(res) -> Tuple[str, str]:
    u = res["uniform"]; a = res["annealed"]; gain = (a - u) / max(u, 1e-9)
    summary = "K_max uniform=%d annealed=%d | annealed gain=%.2f" % (u, a, gain)
    if a > u and gain >= 0.15:
        return ("HARD_PASS", "HARD_PASS: annealed sparsity schedule extends K_max >=15%% over uniform -- annealing replaces uniform sparse as default. " + summary)
    if a >= u:
        return ("MIDDLE_BAND", "MIDDLE_BAND: annealed >= uniform but <15%% gain (marginal). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: annealing does not beat uniform sparse -- keep uniform alpha. " + summary)


print("[config] anchor=%s mode=%s N=%d V_c=%d chains=%d B_fix=%d" % (ANCHOR_NAME, RUN_MODE, N, V_C, CHAINS, B_FIX), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); res = run()
v, vmsg = verdict(res); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [res], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [res]); print("[metrics] written", flush=True)
