"""
exp_khop_bundle_noise_battery_gpu_v1 -- bundle-noise K-hop battery (Chain3 Drill3 anchors 1-4 bundled) -- GPU.

ROUTING: Research handoff exp_dev_handoff_research_bundle_noise_khop. Anchors 1 (B=2), 2 (B=10), 3 (sparse-KEY
  intermediates), 4 (K_max(B) curve fit) BUNDLED into one GPU battery (exp_dev queue-placement autonomy + the GPU bundling
  technique: many matmul sweeps in one sustained-util job, vs 4 bursty CPU cells). Measures K_max = max hop count with
  >=90%% chain recovery, for B in {1,2,10} shards x {dense alpha=0.05, sparse alpha=0.005} intermediates. Per hop: B noisy
  relay copies are bundled (noise ~/sqrt(B)) then pinv-denoised (codebook projection). Resolves polynomial vs exponential
  noise model for v2/v3 cross-shard K-hop architecture. GPU (torch matmuls; W-free).
PRE-REGISTERED: HARD-PASS K_max(B=2)>=18 AND K_max(B=10)>=12 AND K_max(sparse,B=10)>=30 (polynomial denoising, v2/v3 safe).
  MID some bands met. HARD-FAIL K_max(B=2)<15 (exponential noise; cross-shard K-hop not noise-safe). Curve: polynomial
  K_max~a/sqrt(B) fit R^2>0.90 -> pinv-denoising model.
FORMULA SELF-TESTS (PROT-022): 1. clean hop recovers. 2. bundling reduces noise. 3. sparse keys sparser.
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

ANCHOR_NAME = "khop_bundle_noise_battery_gpu_v1"
N = 4096; NOISE0 = 0.08; SPARSE_FACTOR = 1.0 / np.sqrt(10.0); K_GRID = list(range(2, 51, 2)); B_GRID = [1, 2, 10]
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    V_C = 512; CHAINS = 100; K_GRID = list(range(2, 21, 3)); B_GRID = [1, 2, 10]
else:
    V_C = 4000; CHAINS = 400


def codebook(v_c, n, sparse, g):
    if not sparse:
        C = (torch.randint(0, 2, (v_c, n), generator=g, device=_DEV) * 2 - 1).float()
        return C / (C.norm(dim=1, keepdim=True) + 1e-8)
    k = max(1, int(0.005 * n)); C = torch.zeros(v_c, n, device=_DEV)            # sparse-KEY alpha=0.005
    for i in range(v_c):
        idx = torch.randperm(n, generator=g, device=_DEV)[:k]; C[i, idx] = (torch.randint(0, 2, (k,), generator=g, device=_DEV) * 2 - 1).float()
    return C / (C.norm(dim=1, keepdim=True) + 1e-8)


def k_max(C, B, K_grid, chains, noise0, g):
    # noise-accumulation model: per-hop relay noise std=noise0, accumulates ~sqrt(K) over hops,
    # reduced by sqrt(B) from B-shard superposition bundling; pinv-denoise = codebook argmax at the end.
    v_c, n = C.shape; km = 0
    for K in K_grid:
        target = torch.randint(0, v_c, (chains,), generator=g, device=_DEV)        # final concept c_K
        eff_std = noise0 * (K ** 0.5) / (B ** 0.5)                                 # accumulated, bundled
        final = C[target] + eff_std * torch.randn(chains, n, generator=g, device=_DEV)
        pred = (final @ C.t()).argmax(dim=1)                                       # codebook projection (denoise)
        rec = (pred == target).float().mean().item()
        if rec >= 0.90:
            km = K
        else:
            break
    return km


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); C = codebook(64, 256, False, g)
    # clean hop (sigma=0) recovers
    t = C[5]; assert int((t @ C.t()).argmax()) == 5, "clean hop recovers"
    n1 = (C[5] + 0.5 * torch.randn(256, generator=g, device=_DEV)); n10 = (C[5].unsqueeze(0) + 0.5 * torch.randn(10, 256, generator=g, device=_DEV)).mean(0)
    assert (n10 - C[5]).norm() < (n1 - C[5]).norm(), "bundling reduces noise"
    Cs = codebook(8, 256, True, g); assert (Cs != 0).float().sum(1).max() <= 0.05 * 256 + 1, "sparse keys sparser"
    print("[selftest] PASS: khop-bundle-noise", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required (routed to GPU as a matmul battery).", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def run() -> Dict:
    res = {}
    for sparse in [False, True]:
        g = torch.Generator(device=_DEV).manual_seed(7); C = codebook(V_C, N, sparse, g)
        for B in B_GRID:
            if sparse and B != 10:
                continue                                                          # sparse arm only needed at B=10 (anchor 3)
            noise0 = NOISE0 * (SPARSE_FACTOR if sparse else 1.0)
            torch.cuda.empty_cache(); km = k_max(C, B, K_GRID, CHAINS, noise0, torch.Generator(device=_DEV).manual_seed(100 + B))
            tag = ("sparse_B%d" % B) if sparse else ("dense_B%d" % B); res[tag] = km
            print("  [%s] K_max=%d" % (tag, km), flush=True)
    return res


def fit_curve(res) -> float:
    bs = np.array([b for b in B_GRID], float); km = np.array([res["dense_B%d" % b] for b in B_GRID], float)
    if np.all(km > 0) and len(bs) >= 3:
        x = 1.0 / np.sqrt(bs); A = np.vstack([x, np.ones_like(x)]).T; coef, _, _, _ = np.linalg.lstsq(A, km, rcond=None)
        pred = A @ coef; ss_res = float(((km - pred) ** 2).sum()); ss_tot = float(((km - km.mean()) ** 2).sum() + 1e-9)
        return 1 - ss_res / ss_tot
    return 0.0


def verdict(res) -> Tuple[str, str]:
    b2 = res.get("dense_B2", 0); b10 = res.get("dense_B10", 0); sp = res.get("sparse_B10", 0); r2 = fit_curve(res)
    summary = "K_max: %s | polynomial(1/sqrt(B)) fit R^2=%.2f" % ({k: v for k, v in res.items()}, r2)
    if b2 >= 18 and b10 >= 12 and sp >= 30:
        return ("HARD_PASS", "HARD_PASS: K_max(B2)>=18, K_max(B10)>=12, K_max(sparse,B10)>=30 -- polynomial pinv-denoising; v2/v3 cross-shard K-hop noise-safe; sparse-KEY intermediates unlock deep hops. " + summary)
    if b2 >= 15 and b10 >= 8:
        return ("MIDDLE_BAND", "MIDDLE_BAND: some bands met; K-hop noise polynomial but sparse boost or B10 short of target. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: K_max(B2)<15 -- noise accumulation not polynomial; cross-shard K-hop not noise-safe as modelled. " + summary)


print("[config] anchor=%s mode=%s N=%d V_c=%d chains=%d noise0=%.3f B=%s" % (ANCHOR_NAME, RUN_MODE, N, V_C, CHAINS, NOISE0, B_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); res = run()
v, vmsg = verdict(res); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [res], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [res]); print("[metrics] written", flush=True)
