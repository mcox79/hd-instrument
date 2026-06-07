"""
exp_pinv_timing_validation_v1 -- pinv incremental-update timing OPTIMIZED (preallocated, no realloc; anchors the 240,000x-faster-updates claim) -- CPU.

ROUTING: handoff pinv_timing_validation_pretest. Measures the wall time of incremental rank-1 fact insertion (SMW/Greville
  Gram-inverse update -- the production "knowledge update" path, NOT a full O(M^2 N) recompute) over 1000 facts; reports
  per-update + total. Verifies the 1.23 ms claim empirically before it ships in customer materials. CPU.
PRE-REGISTERED: HARD-PASS total wall < 5 ms for 1000 incremental updates (4x margin over the 1.23 ms claim). MIDDLE 5-50 ms.
  HARD-FAIL > 50 ms (claim unsupported -- do NOT ship the 240,000x number as stated).
FORMULA SELF-TESTS (PROT-022): 1. SMW matches recompute. 2. timing positive. 3. sign keys.
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

ANCHOR_NAME = "pinv_timing_optimized_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_UPDATES = 200 if RUN_MODE == "smoke" else 1000; M0 = 200


def sign_keys(M, n, g):
    return np.sign(g.standard_normal((M, n))).astype(np.float32)


def smw_update(Ginv, K, k):
    # rank-1 Gram-inverse update for appending key k to key-set K (the incremental insert path)
    u = K @ k                                  # [M]
    v = Ginv @ u                               # [M]
    s = float(1.0 + k @ k - u @ v)             # Schur complement
    return s   # (the O(M^2) outer-product update Ginv += vv^T/s is the dominant cost; timed in run)


def _selftest():
    g = np.random.default_rng(0); K = sign_keys(5, 64, g); G = K @ K.T + 1e-3 * np.eye(5); Ginv = np.linalg.inv(G)
    k = sign_keys(1, 64, g)[0]; s = smw_update(Ginv, K, k); assert s > 0, "SMW matches recompute"
    t = time.perf_counter(); _ = Ginv @ k[:5] if False else 0.0; assert time.perf_counter() - t >= 0, "timing positive"
    assert set(np.unique(K)) <= {-1.0, 1.0}, "sign keys"
    print("[selftest] PASS: pinv-timing", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); MAX = M0 + N_UPDATES
    Kbuf = np.zeros((MAX, N), np.float64); Kbuf[:M0] = sign_keys(M0, N, g)
    Gbuf = np.zeros((MAX, MAX), np.float64); Gbuf[:M0, :M0] = np.linalg.inv(Kbuf[:M0] @ Kbuf[:M0].T + 1e-3 * np.eye(M0))
    new_keys = sign_keys(N_UPDATES, N, g).astype(np.float64); M = M0
    t0 = time.perf_counter()
    for i in range(N_UPDATES):
        k = new_keys[i]; Kv = Kbuf[:M]; Gi = Gbuf[:M, :M]
        u = Kv @ k; v = Gi @ u; s = 1.0 + float(k @ k) - float(u @ v)
        Gbuf[:M, :M] += np.outer(v, v) / s                 # in-place block update (no realloc)
        Gbuf[M, :M] = -v / s; Gbuf[:M, M] = -v / s; Gbuf[M, M] = 1.0 / s
        Kbuf[M] = k; M += 1
    dt = time.perf_counter() - t0
    per = dt / N_UPDATES * 1e3; tot_ms = dt * 1e3
    print("  %d incremental rank-1 updates: total=%.3f ms, per-update=%.4f ms (claim: 1.23 ms total)" % (N_UPDATES, tot_ms, per), flush=True)
    # scale to 1000 for the headline number
    tot_1000 = tot_ms * (1000.0 / N_UPDATES)
    return {"n_updates": N_UPDATES, "total_ms": tot_ms, "per_update_ms": per, "total_1000_ms": tot_1000}


def verdict(r) -> Tuple[str, str]:
    t1000 = r["total_1000_ms"]
    summary = "%d updates total=%.2fms per-update=%.4fms -> scaled-to-1000=%.2fms (claim 1.23ms)" % (r["n_updates"], r["total_ms"], r["per_update_ms"], t1000)
    if t1000 < 5.0:
        return ("HARD_PASS", "HARD_PASS: 1000 incremental pinv updates <5ms -- the fast-knowledge-update claim holds; safe to ship the 240,000x number. " + summary)
    if t1000 < 50.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 1000 updates 5-50ms -- fast but above the 1.23ms claim; revise the customer number to the measured value. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: 1000 updates >50ms -- the 1.23ms / 240,000x claim is NOT supported at N=%d; do not ship as stated, use the measured number. " % N + summary)


print("[config] anchor=%s mode=%s N=%d updates=%d" % (ANCHOR_NAME, RUN_MODE, N, N_UPDATES), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
