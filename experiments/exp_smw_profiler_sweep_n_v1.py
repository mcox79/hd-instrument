"""
exp_smw_profiler_sweep_n_v1 -- rank-1 SMW BLAS-regime drill anchor 1 (CHEAPEST DECISIVE) -- GPU.

ROUTING: Research handoff exp_dev_handoff_research_rank1_smw_rank_k_woodbury. Cycle-148 rank-1 SMW shows 10x at N=1024 but
  decays to 5-6x at N>=2048. Hypothesis: BLAS-2 (memory-bound) vs BLAS-3 (compute-bound) regime shift. This times the rank-1
  SMW Schur update across N={512,1024,2048,4096,8192} and reports achieved bandwidth utilization (vs a GPU memcpy baseline)
  per N. If the update is memory-bound (high bandwidth util), the BLAS-2 hypothesis is confirmed. GPU (W-free; only the
  M x M Gram inverse + rank-1 vectors live).
PRE-REGISTERED (research bands): HARD-PASS bandwidth util > 70%% at all N (memory-bound SMW confirmed). MID 30-70%%.
  HARD-FAIL < 30%% (kernel-launch overhead dominates; different bottleneck).
FORMULA SELF-TESTS (PROT-022): 1. schur update correctness. 2. memcpy baseline positive. 3. cuda.
ASCII-only. write_metrics. PROT-018 no _nN (N-sweep).
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

ANCHOR_NAME = "smw_profiler_sweep_n_v1"
RIDGE = 1e-3; M0_FRAC = 0.2; REPEAT = 50
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_GRID = [512, 1024] if RUN_MODE == "smoke" else [512, 1024, 2048, 4096, 8192]


def smw_rank1(P, Gi, p):
    # Schur up-date of (PP^T+ridge)^-1 when appending row p (the production incremental write); BLAS-2 dominated
    b = P @ p; Gib = Gi @ b; s = (p @ p) + RIDGE - (b @ Gib)
    M = P.shape[0]; new = torch.zeros((M + 1, M + 1), device=P.device, dtype=P.dtype)
    new[:M, :M] = Gi + torch.outer(Gib, Gib) / s; new[:M, M] = -Gib / s; new[M, :M] = -Gib / s; new[M, M] = 1.0 / s
    return new


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); n = 64
    P = (torch.randint(0, 2, (6, n), generator=g, device=_DEV) * 2 - 1).float()
    Gi = torch.linalg.inv(P @ P.t() + RIDGE * torch.eye(6, device=_DEV))
    p = (torch.randint(0, 2, (n,), generator=g, device=_DEV) * 2 - 1).float(); Gi2 = smw_rank1(P, Gi, p)
    P2 = torch.cat([P, p[None, :]]); ref = torch.linalg.inv(P2 @ P2.t() + RIDGE * torch.eye(7, device=_DEV))
    assert torch.max(torch.abs(Gi2 - ref)).item() < 1e-3, "schur update correctness"
    print("[selftest] PASS: smw-profiler", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def memcpy_bw(nbytes):
    a = torch.empty(nbytes // 4, device=_DEV, dtype=torch.float32); torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(REPEAT):
        b = a.clone()
    torch.cuda.synchronize(); dt = (time.perf_counter() - t0) / REPEAT
    return 2 * nbytes / dt / 1e9                                    # GB/s (read+write)


def time_update(n):
    g = torch.Generator(device=_DEV).manual_seed(7); M = max(8, int(M0_FRAC * n))
    P = (torch.randint(0, 2, (M, n), generator=g, device=_DEV) * 2 - 1).float()
    Gi = torch.linalg.inv(P @ P.t() + RIDGE * torch.eye(M, device=_DEV))
    p = (torch.randint(0, 2, (n,), generator=g, device=_DEV) * 2 - 1).float(); torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(REPEAT):
        _ = smw_rank1(P, Gi, p)
    torch.cuda.synchronize(); dt = (time.perf_counter() - t0) / REPEAT
    bytes_moved = (M * n + M * M) * 4                               # P + Gi reads dominate
    return dt, bytes_moved / dt / 1e9, M


def run() -> Dict:
    peak = max(memcpy_bw(256 * 1024 * 1024), 1e-9); by = {}
    print("  [peak memcpy bandwidth] %.0f GB/s" % peak, flush=True)
    for n in N_GRID:
        torch.cuda.empty_cache(); dt, bw, M = time_update(n); util = bw / peak
        by["N%d" % n] = {"sec": dt, "achieved_gbps": bw, "bw_util": util, "M": M}
        print("  [N=%d M=%d] %.4f ms  %.0f GB/s  util=%.2f" % (n, M, dt * 1e3, bw, util), flush=True)
    return {"peak_gbps": peak, "by": by}


def verdict(r) -> Tuple[str, str]:
    utils = [v["bw_util"] for v in r["by"].values()]; mn = float(np.min(utils))
    summary = "peak=%.0f GB/s | bw_util by N: %s | min=%.2f" % (r["peak_gbps"], {k: round(v["bw_util"], 2) for k, v in r["by"].items()}, mn)
    if mn > 0.70:
        return ("HARD_PASS", "HARD_PASS: rank-1 SMW is memory-bound (bw util >70%% at all N) -- BLAS-2 regime confirmed; rank-k Woodbury (BLAS-3) is the right speedup lever. " + summary)
    if mn >= 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 30-70%% bandwidth util (partial BLAS-2 confirmation). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: <30%% bandwidth util -- kernel-launch overhead dominates, not BLAS-2. " + summary)


print("[config] anchor=%s mode=%s N_grid=%s" % (ANCHOR_NAME, RUN_MODE, N_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
