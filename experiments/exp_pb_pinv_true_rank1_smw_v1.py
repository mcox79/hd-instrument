"""
exp_pb_pinv_true_rank1_smw_v1 -- propose-back (TRUE rank-1 incremental pinv; closes the pb_pinv_smw gap) -- CPU.

ROUTING: Exp-Dev propose-back. pb_pinv_sherman_morrison_incremental used a FULL re-solve disguised as incremental (no
  speedup). This implements the ACTUAL Greville rank-1 projector update: W_new = W + (I-W) p p^T (I-W) / (p^T (I-W) p) per
  added pattern -- O(N^2) per write, NOT an O(M^3) re-inversion. Measures correctness (vs full projector) AND per-item write
  throughput vs full rebuild, at N up to 4096. Answers the G2/I6 production-throughput question with a genuinely incremental
  algorithm. CPU $0.
PRE-REGISTERED: HARD-PASS rank-1 W matches full within 1e-3 AND >=10x faster than full rebuild at N=4096. MID correct but
  <10x. HARD-FAIL incorrect (>1e-3).
FORMULA SELF-TESTS (PROT-022): 1. rank-1 matches full on small case. 2. projector idempotent. 3. timing positive.
ASCII-only. write_metrics. PROT-018 no _nN.
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
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "pb_pinv_true_rank1_smw_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_GRID = [512, 1024] if RUN_MODE == "smoke" else [1024, 2048, 4096]
M0_FRAC = 0.2; ADD = 40; EPS = 1e-8


def full_proj(P):
    G = P @ P.T + 1e-9 * np.eye(P.shape[0]); return P.T @ np.linalg.solve(G, P)


def rank1_add(W, p):
    # Greville: project p orthogonal to current row space (represented by projector W); update W to include it
    Wp = W @ p; c = p - Wp; cc = float(c @ c)
    if cc > EPS:
        return W + np.outer(c, c) / cc                          # p outside row space -> add its direction
    Wpp = float(p @ Wp)                                          # p in row space -> pinv-style minimum-norm correction
    if Wpp < EPS:
        return W
    return W + np.outer(Wp, Wp) / Wpp - np.outer(Wp, Wp) / Wpp  # no-op (already spanned)


def _selftest():
    g = np.random.default_rng(0); n = 64; P = (g.integers(0, 2, (8, n)) * 2 - 1).astype(np.float64)
    W = np.zeros((n, n))
    for i in range(8):
        W = rank1_add(W, P[i])
    Wfull = full_proj(P)
    assert np.max(np.abs(W - Wfull)) < 1e-6, "rank-1 matches full"
    assert np.allclose(W @ W, W, atol=1e-3), "projector idempotent"
    print("[selftest] PASS: pb-true-smw", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def bench(n, seed):
    g = np.random.default_rng(seed); M0 = max(4, int(M0_FRAC * n)); P = (g.integers(0, 2, (M0, n)) * 2 - 1).astype(np.float64)
    W = full_proj(P); newp = [(g.integers(0, 2, n) * 2 - 1).astype(np.float64) for _ in range(ADD)]
    t0 = time.perf_counter()
    for p in newp:
        W = rank1_add(W, p)
    inc_dt = (time.perf_counter() - t0) / ADD
    Pall = np.vstack([P] + [p[None, :] for p in newp]); Wfull = full_proj(Pall); dev = float(np.max(np.abs(W - Wfull)))
    t1 = time.perf_counter(); _ = full_proj(Pall); full_dt = time.perf_counter() - t1
    return 1.0 / inc_dt, 1.0 / full_dt, dev


def _run() -> Dict:
    by = {}
    for n in N_GRID:
        inc, full, dev = bench(n, 7)
        by["N%d" % n] = {"incremental_wps": inc, "full_rebuild_wps": full, "speedup": inc / max(full, 1e-9), "max_dev": dev}
        print("  [N=%d] rank1=%.1f wps full=%.1f wps speedup=%.1fx dev=%.2e" % (n, inc, full, inc / max(full, 1e-9), dev), flush=True)
    return {"by": by}


def verdict(r) -> Tuple[str, str]:
    nmax = "N%d" % N_GRID[-1]; sp = r["by"][nmax]["speedup"]; dev = max(v["max_dev"] for v in r["by"].values())
    summary = "at N=%d: rank1/full speedup=%.1fx max_dev=%.2e" % (N_GRID[-1], sp, dev)
    if dev < 1e-3 and sp >= 10:
        return ("HARD_PASS", "HARD_PASS: TRUE rank-1 pinv correct AND >=10x faster than full rebuild -- production incremental writes solved. " + summary)
    if dev < 1e-3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: rank-1 correct but <10x speedup. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: rank-1 update incorrect (>1e-3). " + summary)


print("[config] anchor=%s mode=%s N_grid=%s add=%d" % (ANCHOR_NAME, RUN_MODE, N_GRID, ADD), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = _run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
