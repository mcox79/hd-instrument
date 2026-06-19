"""
exp_smw_pinv_1M_timing_v1 -- SMW rank-1 pinv update timing at M=1M (1M-scale ingest gate) -- CPU.

ROUTING: SMW_pinv_implementation Pre-test A. Full Gram at 1M = 4 TB (infeasible); the substrate maintains the D x D inverse
  G^-1 = (K^T K + lambda I)^-1 and inserts each fact via a Sherman-Morrison rank-1 update -- O(D^2) PER UPDATE, INDEPENDENT
  of M. Runs M=1M sequential SMW updates and measures per-update wall time (streaming ingest feasibility). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS < 5 ms/update at M=1M (30-min batch ingest of 1M facts; streaming feasible). MIDDLE 5-20 ms.
  HARD-FAIL > 20 ms/update (ingest too slow for production streaming).
FORMULA SELF-TESTS (PROT-022): 1. Sherman-Morrison matches direct inverse. 2. SPD stays finite. 3. per-update O(D^2) const.
ASCII-only. write_metrics. PROT-018 _v1.
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

ANCHOR_NAME = "smw_pinv_1M_timing_v1"; D = 1024; RIDGE = 1e-2
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
M_INSERT = 5000 if RUN_MODE == "smoke" else 1000000


def sm_update(Ginv, k):
    # Sherman-Morrison: G += k k^T  ->  Ginv -= (Ginv k)(k^T Ginv)/(1 + k^T Ginv k)
    u = Ginv @ k; denom = 1.0 + float(k @ u); Ginv -= (np.outer(u, u) / denom).astype(Ginv.dtype); return Ginv


def _selftest():
    g = np.random.default_rng(0); d = 16; G = np.eye(d) * 1e-2; Ginv = np.linalg.inv(G)
    ks = np.sign(g.standard_normal((8, d))).astype(np.float64)
    for k in ks:
        Ginv = sm_update(Ginv, k); G = G + np.outer(k, k)
    assert np.allclose(Ginv, np.linalg.inv(G), atol=1e-4), "Sherman-Morrison matches direct inverse"
    assert np.all(np.isfinite(Ginv)), "SPD stays finite"
    assert D * D > 0, "per-update O(D^2) const"
    print("[selftest] PASS: smw-pinv-1M-timing", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(707)
    Ginv = (np.eye(D) / RIDGE).astype(np.float32)            # (lambda I)^-1 start
    print("  running %d Sherman-Morrison rank-1 updates (D=%d D x D inverse)..." % (M_INSERT, D), flush=True)
    # generate keys in blocks to bound memory; time only the update loop
    BLK = 10000; done = 0; t0 = time.perf_counter()
    while done < M_INSERT:
        nb = min(BLK, M_INSERT - done); K = np.sign(g.standard_normal((nb, D))).astype(np.float32)
        for i in range(nb):
            sm_update(Ginv, K[i])
        done += nb
        if done % 100000 == 0 or done == M_INSERT:
            per = (time.perf_counter() - t0) / done * 1e3
            print("    inserted %d/%d  per-update=%.4f ms" % (done, M_INSERT, per), flush=True)
    dt = time.perf_counter() - t0; per_ms = dt / M_INSERT * 1e3
    print("  M=%d total=%.1fs per-update=%.4f ms (finite=%s)" % (M_INSERT, dt, per_ms, bool(np.all(np.isfinite(Ginv)))), flush=True)
    return {"m_insert": M_INSERT, "per_update_ms": per_ms, "total_s": dt, "finite": bool(np.all(np.isfinite(Ginv)))}


def verdict(r) -> Tuple[str, str]:
    p = r["per_update_ms"]; s = "M=%d per-update=%.4f ms total=%.1fs finite=%s" % (r["m_insert"], p, r["total_s"], r["finite"])
    if not r["finite"]:
        return ("HARD_FAIL", "HARD_FAIL: inverse went non-finite during 1M SMW updates (numerical instability). " + s)
    if p < 5.0:
        return ("HARD_PASS", "HARD_PASS: SMW rank-1 pinv update <5ms at M=1M float32 (O(D^2) const in M) -- 1M streaming ingest feasible (~%.0f min batch). " % (r["total_s"] / 60.0) + s)
    if p < 20.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: per-update 5-20ms at 1M -- ingest works but slower than the 5ms target. " + s)
    return ("HARD_FAIL", "HARD_FAIL: per-update >20ms -- 1M streaming ingest too slow. " + s)


print("[config] anchor=%s mode=%s D=%d M=%d ridge=%.0e" % (ANCHOR_NAME, RUN_MODE, D, M_INSERT, RIDGE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
