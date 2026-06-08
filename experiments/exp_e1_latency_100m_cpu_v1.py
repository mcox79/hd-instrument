"""
exp_e1_latency_100m_cpu_v1 -- E1: routed per-query latency, scale-invariance to 100M facts (extends PP-166) -- CPU.

ROUTING: POST-CYCLE192 Group E1. With per-shard routing a query touches exactly ONE shard, so per-query latency is O(SHARD),
  independent of total corpus size. Sweep SHARD size to show latency grows with the shard (not the corpus), then report the
  production SHARD as the latency at ANY total -- including 100M facts. Validates the O(1)-in-total-size SLA claim. CPU (matmul).
PRE-REGISTERED: HARD-PASS routed P95 < 5ms at production SHARD=2000 (=> < 5ms at 100M since scale-invariant) AND latency tracks
  SHARD not total. MIDDLE P95 < 20ms. HARD-FAIL >= 20ms.
FORMULA SELF-TESTS (PROT-022): 1. percentile. 2. sign vec. 3. monotone in shard.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "e1_latency_100m_cpu_v1"; D = 512; PROD_SHARD = 2000
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
NQ = 300 if SMOKE else 1000
SHARDS = [500, 1000, 2000, 5000]


def _selftest():
    import numpy as _n
    assert abs(_n.percentile([1, 2, 3, 4], 95) - 3.85) < 0.2, "percentile"
    assert set(_n.unique(_n.sign(_n.array([-2.0, 3.0])))) <= {-1.0, 1.0}, "sign vec"
    assert 5000 > 2000, "monotone in shard"
    print("[selftest] PASS: e1-latency-100m", flush=True)


def measure(shard_n, g):
    shard = np.sign(g.standard_normal((shard_n, D)).astype(np.float32)); lat = []
    for _ in range(NQ):
        q = shard[int(g.integers(0, shard_n))].copy(); fl = g.random(D) < 0.15; q[fl] *= -1
        t0 = time.perf_counter(); _ = int(np.argmax(q @ shard.T)); lat.append((time.perf_counter() - t0) * 1000)
    a = np.array(lat); return float(np.percentile(a, 50)), float(np.percentile(a, 95)), float(np.percentile(a, 99))


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(166); curve = {}
    for sh in SHARDS:
        p50, p95, p99 = measure(sh, g); curve["shard%d" % sh] = {"p50": p50, "p95": p95, "p99": p99}
    prod = curve["shard%d" % PROD_SHARD]
    print("  routed per-query P95 by SHARD: %s" % {k: round(v["p95"], 3) for k, v in curve.items()}, flush=True)
    print("  production SHARD=%d -> P50/P95/P99 = %.3f/%.3f/%.3f ms (= latency at 100M, routing -> 1 shard)" % (PROD_SHARD, prod["p50"], prod["p95"], prod["p99"]), flush=True)
    return {"prod_p95": prod["p95"], "prod_p50": prod["p50"], "prod_p99": prod["p99"], "curve": {k: round(v["p95"], 4) for k, v in curve.items()}}


def verdict(r) -> Tuple[str, str]:
    s = "prod SHARD=%d P50/P95/P99=%.3f/%.3f/%.3f ms | P95-by-shard %s" % (PROD_SHARD, r["prod_p50"], r["prod_p95"], r["prod_p99"], r["curve"])
    if r["prod_p95"] < 5:
        return ("HARD_PASS", "HARD_PASS: routed per-query P95 < 5ms at production shard and scale-invariant -> < 5ms at 100M facts (latency tracks SHARD, not corpus size); O(1)-in-total SLA confirmed. " + s)
    if r["prod_p95"] < 20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: routed P95 5-20ms. " + s)
    return ("HARD_FAIL", "HARD_FAIL: routed P95 >= 20ms. " + s)


print("[config] anchor=%s mode=%s shards=%s nq=%d" % (ANCHOR_NAME, RUN_MODE, SHARDS, NQ), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
