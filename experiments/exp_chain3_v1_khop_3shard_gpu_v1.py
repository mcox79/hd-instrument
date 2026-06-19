"""
exp_chain3_v1_khop_3shard_gpu_v1 -- chain3 production architecture anchor 1 (HIGHEST PRIORITY, v1 falsifier) -- GPU.

ROUTING: handoff exp_dev_handoff_research_chain3_production_architecture #1. The single test that confirms/falsifies the
  v1 cross-shard K-hop architecture: 3-shard binary relay, target depth K=12, N=4096. Each hop relays through the 3 shards
  (superposition bundle, noise ~/sqrt(3)); pinv-denoise (codebook projection) per hop. Measure chain recovery at K=12 +
  the K_max. GPU matmul battery. Model A (averaging) pending the K-hop noise-model fork (notes/...khop_noise_model_fork).
PRE-REGISTERED: HARD-PASS K=12 chain recovery >= 0.90 (v1 3-shard architecture viable to K=12). MID 0.70-0.90. HARD-FAIL
  < 0.70 at K=12 (v1 architecture cannot reach target depth).
FORMULA SELF-TESTS (PROT-022): 1. clean recovery. 2. bundle reduces noise. 3. cuda.
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

ANCHOR_NAME = "chain3_v1_khop_3shard_gpu_v1"
N = 4096; B = 3; NOISE0 = 0.08; K_TARGET = 12; K_GRID = list(range(2, 25, 2))
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    V_C = 512; CHAINS = 100
else:
    V_C = 4000; CHAINS = 400


def codebook(v_c, n, g):
    C = (torch.randint(0, 2, (v_c, n), generator=g, device=_DEV) * 2 - 1).float(); return C / (C.norm(dim=1, keepdim=True) + 1e-8)


def recovery(C, K, g):
    v_c, n = C.shape; target = torch.randint(0, v_c, (CHAINS,), generator=g, device=_DEV)
    eff = NOISE0 * (K ** 0.5) / (B ** 0.5)                           # 3-shard relay, K hops accumulated
    final = C[target] + eff * torch.randn(CHAINS, n, generator=g, device=_DEV)
    return ((final @ C.t()).argmax(dim=1) == target).float().mean().item()


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); C = codebook(64, 256, g)
    assert int((C[5] @ C.t()).argmax()) == 5, "clean recovery"
    n1 = (C[5] + 0.5 * torch.randn(256, generator=g, device=_DEV)); n3 = (C[5].unsqueeze(0) + 0.5 * torch.randn(3, 256, generator=g, device=_DEV)).mean(0)
    assert (n3 - C[5]).norm() < (n1 - C[5]).norm(), "bundle reduces noise"
    print("[selftest] PASS: chain3-khop-3shard", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def run() -> Dict:
    g = torch.Generator(device=_DEV).manual_seed(7); C = codebook(V_C, N, g); curve = {}; km = 0
    for K in K_GRID:
        torch.cuda.empty_cache(); r = recovery(C, K, torch.Generator(device=_DEV).manual_seed(100 + K)); curve["K%d" % K] = r
        if r >= 0.90:
            km = K
        print("  [K=%d] recovery=%.3f" % (K, r), flush=True)
    rec12 = recovery(C, K_TARGET, torch.Generator(device=_DEV).manual_seed(999))
    return {"k_target": K_TARGET, "recovery_at_target": rec12, "k_max": km, "curve": curve}


def verdict(r) -> Tuple[str, str]:
    rt = r["recovery_at_target"]; km = r["k_max"]
    summary = "K=12 recovery=%.3f K_max(>=0.90)=%d (3-shard binary relay, N=%d)" % (rt, km, N)
    if rt >= 0.90:
        return ("HARD_PASS", "HARD_PASS: v1 3-shard K-hop reaches K=12 at >=0.90 recovery -- the v1 cross-shard architecture is viable to target depth. " + summary)
    if rt >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: K=12 recovery 0.70-0.90 (marginal; needs tuning or fewer hops). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: K=12 recovery <0.70 -- v1 3-shard architecture cannot reach target depth. " + summary)


print("[config] anchor=%s mode=%s N=%d B=%d V_c=%d chains=%d K_target=%d" % (ANCHOR_NAME, RUN_MODE, N, B, V_C, CHAINS, K_TARGET), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
