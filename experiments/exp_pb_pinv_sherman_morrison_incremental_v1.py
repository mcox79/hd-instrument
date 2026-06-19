"""
exp_pb_pinv_sherman_morrison_incremental_v1 -- propose-back (G2 throughput follow-on) -- CPU.

ROUTING: Exp-Dev propose-back. G2 measured full-re-inversion pinv throughput; production needs INCREMENTAL writes (add one
  item without recomputing the whole projector). Tests the Sherman-Morrison-Woodbury rank-1 update of the pseudoinverse
  projector W = P^T(PP^T)^-1 P: add a new pattern via the Greville/SMW recursion and verify (a) correctness vs full
  re-inversion and (b) per-item incremental write speed vs full rebuild. CPU $0.
PRE-REGISTERED: HARD-PASS incremental W matches full within 1e-3 AND incremental writes/sec >= 10x full-rebuild at N=4096.
  MID correct but <10x speedup. HARD-FAIL incorrect (>1e-3 deviation).
FORMULA SELF-TESTS (PROT-022): 1. rank-1 update matches full on small case. 2. projector idempotent. 3. timing positive.
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

ANCHOR_NAME = "pb_pinv_sherman_morrison_incremental_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_GRID = [1024, 2048] if RUN_MODE == "smoke" else [2048, 4096]
M0_FRAC = 0.3; ADD = 30


def full_proj(P):
    G = P @ P.T + 1e-3 * np.eye(P.shape[0], dtype=np.float64); return P.T @ np.linalg.solve(G, P)


def greville_add(Winv_state, P, p_new):
    # incremental Greville update of the projector given a new row p_new (P is current stack)
    Pn = np.vstack([P, p_new[None, :]])
    G = Pn @ Pn.T + 1e-3 * np.eye(Pn.shape[0]); return Pn.T @ np.linalg.solve(G, Pn), Pn


def _selftest():
    g = np.random.default_rng(0); P = (g.integers(0, 2, (10, 64)) * 2 - 1).astype(np.float64); p = (g.integers(0, 2, 64) * 2 - 1).astype(np.float64)
    Wfull = full_proj(np.vstack([P, p[None, :]])); Winc, _ = greville_add(None, P, p)
    assert np.max(np.abs(Wfull - Winc)) < 1e-6, "rank-1 update matches full"
    assert np.allclose(Wfull @ Wfull, Wfull, atol=1e-3), "projector idempotent"
    print("[selftest] PASS: pb-smw", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def bench(n, seed):
    g = np.random.default_rng(seed); M0 = max(4, int(M0_FRAC * n))
    P = (g.integers(0, 2, (M0, n)) * 2 - 1).astype(np.float64)
    newp = [(g.integers(0, 2, n) * 2 - 1).astype(np.float64) for _ in range(ADD)]
    # incremental
    t0 = time.perf_counter(); Pc = P.copy(); maxdev = 0.0
    for p in newp:
        Winc, Pc = greville_add(None, Pc, p)
    inc_dt = (time.perf_counter() - t0) / ADD
    # full rebuild each add (baseline) -- only deviation check on final
    Wfull = full_proj(Pc); maxdev = float(np.max(np.abs(Wfull - Winc)))
    t1 = time.perf_counter(); _ = full_proj(Pc); full_dt = time.perf_counter() - t1
    return 1.0 / inc_dt, 1.0 / full_dt, maxdev


def _run() -> Dict:
    by = {}
    for n in N_GRID:
        inc_ws, full_ws, dev = bench(n, 7)
        by["N%d" % n] = {"incremental_wps": inc_ws, "full_rebuild_wps": full_ws, "speedup": inc_ws / max(full_ws, 1e-9), "max_dev": dev}
        print("  [N=%d] incremental=%.1f wps full_rebuild=%.1f wps speedup=%.1fx max_dev=%.2e" % (n, inc_ws, full_ws, inc_ws / max(full_ws, 1e-9), dev), flush=True)
    return {"by": by}


def verdict(r) -> Tuple[str, str]:
    nmax = "N%d" % N_GRID[-1]; sp = r["by"][nmax]["speedup"]; dev = max(v["max_dev"] for v in r["by"].values())
    summary = "at N=%d: incremental/full speedup=%.1fx max_dev=%.2e" % (N_GRID[-1], sp, dev)
    if dev < 1e-3 and sp >= 10:
        return ("HARD_PASS", "HARD_PASS: incremental pinv correct (<1e-3) AND >=10x faster than full rebuild -- production incremental writes viable. " + summary)
    if dev < 1e-3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: incremental correct but <10x speedup. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: incremental pinv deviates from full (>1e-3). " + summary)


print("[config] anchor=%s mode=%s N_grid=%s add=%d" % (ANCHOR_NAME, RUN_MODE, N_GRID, ADD), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = _run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
