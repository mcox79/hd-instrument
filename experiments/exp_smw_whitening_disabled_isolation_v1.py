"""
exp_smw_whitening_disabled_isolation_v1 -- rank-1 SMW BLAS-regime drill anchor 2 -- GPU.

ROUTING: Research handoff exp_dev_handoff_research_rank1_smw_rank_k_woodbury. Cycle-148 measured SMW speedup WITH whitening,
  which adds a double-update that may be absorbed into the timing. This isolates the PURE SMW speedup (rank-1 incremental
  inverse-Gram update vs full rebuild) with whitening DISABLED, across N, focusing on N=2048 where the decay appeared. GPU.
PRE-REGISTERED (research bands): HARD-PASS pure SMW speedup at N=2048 > 6x (matches predicted theory). MID 3-6x (whitening
  was significant overhead). HARD-FAIL < 3x (different mechanism).
FORMULA SELF-TESTS (PROT-022): 1. schur correctness. 2. full rebuild correctness. 3. cuda.
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

ANCHOR_NAME = "smw_whitening_disabled_isolation_v1"
RIDGE = 1e-3; M0_FRAC = 0.2; ADD = 30
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_GRID = [512, 1024] if RUN_MODE == "smoke" else [1024, 2048, 4096]


def full_inv(P):
    return torch.linalg.inv(P @ P.t() + RIDGE * torch.eye(P.shape[0], device=P.device, dtype=P.dtype))


def smw_rank1(P, Gi, p):
    b = P @ p; Gib = Gi @ b; s = (p @ p) + RIDGE - (b @ Gib)
    M = P.shape[0]; new = torch.zeros((M + 1, M + 1), device=P.device, dtype=P.dtype)
    new[:M, :M] = Gi + torch.outer(Gib, Gib) / s; new[:M, M] = -Gib / s; new[M, :M] = -Gib / s; new[M, M] = 1.0 / s
    return new


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); n = 64
    P = (torch.randint(0, 2, (6, n), generator=g, device=_DEV) * 2 - 1).float()
    p = (torch.randint(0, 2, (n,), generator=g, device=_DEV) * 2 - 1).float()
    Gi2 = smw_rank1(P, full_inv(P), p); P2 = torch.cat([P, p[None, :]])
    assert torch.max(torch.abs(Gi2 - full_inv(P2))).item() < 1e-3, "schur correctness"
    assert torch.allclose(full_inv(P) @ (P @ P.t() + RIDGE * torch.eye(6, device=_DEV)), torch.eye(6, device=_DEV), atol=1e-2), "full rebuild correctness"
    print("[selftest] PASS: smw-whiten-disabled", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def measure(n):
    g = torch.Generator(device=_DEV).manual_seed(7); M0 = max(8, int(M0_FRAC * n))
    P0 = (torch.randint(0, 2, (M0 + ADD, n), generator=g, device=_DEV) * 2 - 1).float()
    # incremental: start from M0, add ADD rows one at a time via SMW
    P = P0[:M0].clone(); Gi = full_inv(P); torch.cuda.synchronize(); t0 = time.perf_counter()
    for k in range(ADD):
        p = P0[M0 + k]; Gi = smw_rank1(P, Gi, p); P = torch.cat([P, p[None, :]])
    torch.cuda.synchronize(); inc = (time.perf_counter() - t0) / ADD
    # full rebuild: rebuild the inverse from scratch ADD times (each at the grown size)
    torch.cuda.synchronize(); t1 = time.perf_counter()
    for k in range(ADD):
        _ = full_inv(P0[:M0 + k + 1])
    torch.cuda.synchronize(); full = (time.perf_counter() - t1) / ADD
    return inc, full, full / max(inc, 1e-12)


def run() -> Dict:
    by = {}
    for n in N_GRID:
        torch.cuda.empty_cache(); inc, full, sp = measure(n)
        by["N%d" % n] = {"incremental_s": inc, "full_rebuild_s": full, "speedup": sp}
        print("  [N=%d] incr=%.4fms full=%.4fms speedup=%.2fx" % (n, inc * 1e3, full * 1e3, sp), flush=True)
    return {"by": by}


def verdict(r) -> Tuple[str, str]:
    key = "N2048" if "N2048" in r["by"] else ("N1024" if "N1024" in r["by"] else list(r["by"])[-1])
    sp = r["by"][key]["speedup"]
    summary = "pure SMW speedup (whitening OFF) by N: %s | at %s=%.2fx" % ({k: round(v["speedup"], 2) for k, v in r["by"].items()}, key, sp)
    if sp > 6.0:
        return ("HARD_PASS", "HARD_PASS: pure SMW speedup >6x at N=2048 (whitening removed) -- the cycle-148 decay was whitening double-update overhead, not SMW. " + summary)
    if sp >= 3.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: pure SMW speedup 3-6x -- whitening was significant but not the whole story. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: pure SMW speedup <3x -- decay is intrinsic to SMW at this N, not whitening. " + summary)


print("[config] anchor=%s mode=%s N_grid=%s add=%d" % (ANCHOR_NAME, RUN_MODE, N_GRID, ADD), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
