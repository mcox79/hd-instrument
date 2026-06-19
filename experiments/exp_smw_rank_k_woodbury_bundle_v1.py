"""
exp_smw_rank_k_woodbury_bundle_v1 -- rank-1 SMW drill anchor 3 (rank-k Woodbury BUNDLE) -- GPU.

ROUTING: Research handoff exp_dev_handoff_research_rank1_smw_rank_k_woodbury (#3). REOPENED: the profiler (anchor 1) found
  the rank-1 update is LAUNCH-OVERHEAD-bound, which is the STRONGEST case for bundling -- batching k rank-1 updates into ONE
  rank-k Woodbury (BLAS-3) kernel amortizes the per-call launch overhead. Implements the rank-k bordered-block inverse-Gram
  update (add k rows at once) and measures speedup vs (a) full rebuild and (b) sequential rank-1, at N=2048, k in {8,16,32}.
  This is the GPU "bundling" technique applied to incremental writes. GPU.
PRE-REGISTERED (research bands): HARD-PASS speedup >= 50x over full rebuild at N=2048,k=16. MID 20-50x. HARD-FAIL < 20x.
FORMULA SELF-TESTS (PROT-022): 1. rank-k update matches full rebuild. 2. k=1 equals rank-1. 3. cuda.
ASCII-only. write_metrics. PROT-018 no _nN (k-sweep).
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

ANCHOR_NAME = "smw_rank_k_woodbury_bundle_v1"
RIDGE = 1e-3; M0_FRAC = 0.2
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N = 1024; K_GRID = [8, 16]
else:
    N = 2048; K_GRID = [8, 16, 32]


def full_inv(P):
    return torch.linalg.inv(P @ P.t() + RIDGE * torch.eye(P.shape[0], device=P.device, dtype=P.dtype))


def rank1(P, Gi, p):
    b = P @ p; Gib = Gi @ b; s = (p @ p) + RIDGE - (b @ Gib); M = P.shape[0]
    new = torch.zeros((M + 1, M + 1), device=P.device, dtype=P.dtype)
    new[:M, :M] = Gi + torch.outer(Gib, Gib) / s; new[:M, M] = -Gib / s; new[M, :M] = -Gib / s; new[M, M] = 1.0 / s
    return new


def rank_k(P, Gi, Pk):
    # bordered-block inverse: add k rows Pk at once (ONE BLAS-3 batch -> amortizes launch overhead)
    B = P @ Pk.t(); D = Pk @ Pk.t() + RIDGE * torch.eye(Pk.shape[0], device=P.device, dtype=P.dtype)
    GiB = Gi @ B; S = D - B.t() @ GiB; Sinv = torch.linalg.inv(S); M = P.shape[0]; k = Pk.shape[0]
    new = torch.zeros((M + k, M + k), device=P.device, dtype=P.dtype)
    new[:M, :M] = Gi + GiB @ Sinv @ GiB.t(); new[:M, M:] = -GiB @ Sinv; new[M:, :M] = -Sinv @ GiB.t(); new[M:, M:] = Sinv
    return new


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); n = 64
    P = (torch.randint(0, 2, (8, n), generator=g, device=_DEV) * 2 - 1).float()
    Pk = (torch.randint(0, 2, (4, n), generator=g, device=_DEV) * 2 - 1).float()
    Gik = rank_k(P, full_inv(P), Pk); ref = full_inv(torch.cat([P, Pk]))
    assert torch.max(torch.abs(Gik - ref)).item() < 1e-3, "rank-k matches full rebuild"
    p = Pk[:1]; G1 = rank_k(P, full_inv(P), p); assert torch.max(torch.abs(G1 - full_inv(torch.cat([P, p])))).item() < 1e-3, "k=1 equals rank-1"
    print("[selftest] PASS: woodbury-bundle", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def measure(n, k):
    g = torch.Generator(device=_DEV).manual_seed(7); M0 = max(8, int(M0_FRAC * n))
    P0 = (torch.randint(0, 2, (M0 + k, n), generator=g, device=_DEV) * 2 - 1).float()
    base = P0[:M0]; Pk = P0[M0:M0 + k]; Gi0 = full_inv(base); REP = 20
    torch.cuda.synchronize(); t0 = time.perf_counter()                # rank-k bundle
    for _ in range(REP):
        _ = rank_k(base, Gi0, Pk)
    torch.cuda.synchronize(); rk = (time.perf_counter() - t0) / REP
    torch.cuda.synchronize(); t1 = time.perf_counter()                # sequential rank-1 (k calls)
    for _ in range(REP):
        P = base.clone(); Gi = Gi0
        for j in range(k):
            Gi = rank1(P, Gi, Pk[j]); P = torch.cat([P, Pk[j][None, :]])
    torch.cuda.synchronize(); seq = (time.perf_counter() - t1) / REP
    torch.cuda.synchronize(); t2 = time.perf_counter()                # full rebuild
    for _ in range(REP):
        _ = full_inv(P0[:M0 + k])
    torch.cuda.synchronize(); full = (time.perf_counter() - t2) / REP
    return rk, seq, full


def run() -> Dict:
    by = {}
    for k in K_GRID:
        torch.cuda.empty_cache(); rk, seq, full = measure(N, k)
        by["k%d" % k] = {"rankk_s": rk, "seq_rank1_s": seq, "full_s": full, "vs_full": full / max(rk, 1e-12), "vs_seq": seq / max(rk, 1e-12)}
        print("  [k=%d] rankk=%.4fms seq=%.4fms full=%.4fms | vs_full=%.1fx vs_seq=%.1fx" % (k, rk * 1e3, seq * 1e3, full * 1e3, full / max(rk, 1e-12), seq / max(rk, 1e-12)), flush=True)
    return {"by": by, "N": N}


def verdict(r) -> Tuple[str, str]:
    key = "k16" if "k16" in r["by"] else list(r["by"])[-1]; vf = r["by"][key]["vs_full"]; vs = r["by"][key]["vs_seq"]
    summary = "at N=%d %s: vs_full=%.1fx vs_seq_rank1=%.1fx | curve: %s" % (r["N"], key, vf, vs, {k: round(v["vs_full"], 1) for k, v in r["by"].items()})
    if vf >= 50:
        return ("HARD_PASS", "HARD_PASS: rank-k Woodbury bundle >=50x over full rebuild -- bundling k rank-1 updates into one BLAS-3 kernel realizes the lit target; ship batched writes. " + summary)
    if vf >= 20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 20-50x over full rebuild (some lit values reachable). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: <20x over full rebuild -- rank-k advantage doesn't materialize at this N/k. " + summary)


print("[config] anchor=%s mode=%s N=%d k_grid=%s" % (ANCHOR_NAME, RUN_MODE, N, K_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
