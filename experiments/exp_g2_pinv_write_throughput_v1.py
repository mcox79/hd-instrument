"""
exp_g2_pinv_write_throughput_v1 -- Batch G2 (pinv writes/sec benchmark) -- CPU/GPU.

ROUTING: Batch G Tier-1 (strategic-priority Rank-3). The pseudoinverse write rule W = P^T(PP^T)^-1 P costs O(M^2 N + M^3);
  writes/sec was never measured. Profiles full-store throughput (items/sec) at N=2048,4096,8192,16384 (M=alpha*N). torch
  (GPU if available). Decides whether pinv ships as-is or needs Sherman-Morrison-Woodbury incremental rank-k updates.
PRE-REGISTERED: HARD-PASS >200 writes/sec at N=16384 (production-viable). MID 50-200 (needs SMW incremental). HF <50 (redesign).
FORMULA SELF-TESTS (PROT-022): 1. pinv projector idempotent. 2. timing positive. 3. deps.
ASCII-only. write_metrics. PROT-018 no _nN (N-sweep).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
import torch
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "g2_pinv_write_throughput_v1"
ALPHA = 0.5
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_GRID = [2048, 4096] if RUN_MODE == "smoke" else [2048, 4096, 8192, 16384]


def pinv_write(P):
    G = P @ P.t() + 1e-3 * torch.eye(P.shape[0], device=_DEV, dtype=P.dtype)
    return P.t() @ torch.linalg.solve(G, P)


def throughput(n, seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed)); M = max(2, int(ALPHA * n))
    P = (torch.randint(0, 2, (M, n), generator=g, device=_DEV) * 2 - 1).float()
    if _DEV.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.perf_counter(); W = pinv_write(P)
    if _DEV.type == "cuda":
        torch.cuda.synchronize()
    return M / (time.perf_counter() - t0)


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); P = (torch.randint(0, 2, (20, 128), generator=g, device=_DEV) * 2 - 1).float()
    W = pinv_write(P); assert torch.allclose(W @ W, W, atol=1e-2), "pinv projector idempotent"
    assert throughput(256, 0) > 0, "timing positive"
    print("[selftest] PASS: g2-throughput", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[dev] %s" % _DEV, flush=True)


def run() -> Dict:
    by = {}
    for n in N_GRID:
        tp = float(np.median([throughput(n, 7 + i) for i in range(3)]))
        by["N%d" % n] = {"writes_per_sec": tp, "M": int(ALPHA * n)}
        print("  [N=%d] writes/sec=%.1f (M=%d)" % (n, tp, int(ALPHA * n)), flush=True)
    return {"by": by, "device": _DEV.type}


def verdict(r) -> Tuple[str, str]:
    nmax = "N%d" % N_GRID[-1]; tp = r["by"][nmax]["writes_per_sec"]
    summary = "writes/sec by N: %s | at N=%d=%.1f (%s)" % ({k: round(v["writes_per_sec"], 1) for k, v in r["by"].items()}, N_GRID[-1], tp, r["device"])
    if tp > 200:
        return ("HARD_PASS", "HARD_PASS: pinv throughput >200 writes/sec at N=%d -- production-viable as-is. " % N_GRID[-1] + summary)
    if tp >= 50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: pinv 50-200 writes/sec -- needs Sherman-Morrison-Woodbury incremental updates. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: pinv <50 writes/sec -- write rule needs redesign for production throughput. " + summary)


print("[config] anchor=%s mode=%s N_grid=%s alpha=%.2f" % (ANCHOR_NAME, RUN_MODE, N_GRID, ALPHA), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
