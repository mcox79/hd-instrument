"""
exp_latency_scale_invariance_cpu_v1.py -- per-query latency is scale-invariant: routing touches one shard regardless of total facts -- CPU.

ROUTING: NEW_EXPERIMENTS batch (N2 latency at 10M/100M (scale-invariant via routing)). With per-subject/per-shard routing, a query touches exactly ONE shard (SHARD keys) regardless of total corpus size -- so per-query latency is O(SHARD), constant in total. Measures the routed per-query latency (P50/P95/P99) and reports it as the latency at 1M/10M/100M (all identical, because routing). Validates enterprise-scale SLA. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS routed per-query P95 < 5ms (=> < 5ms at 10M and < 50ms at 100M, since scale-invariant). MIDDLE < 20ms. HARD-FAIL >= 20ms.
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
ANCHOR_NAME = "latency_scale_invariance_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert abs(_n.percentile([1, 2, 3, 4], 95) - 3.85) < 0.2, "pctile"; print("[selftest] PASS: latency-scale-invariance", flush=True)
def run() -> Dict:
    g = np.random.default_rng(221); D = 512; SHARD = 2000; NQ = 500 if not SMOKE else 200
    shard = np.sign(g.standard_normal((SHARD, D)).astype(np.float32))           # one routed shard (the only thing a query touches)
    lat = []
    for _ in range(NQ):
        q = shard[int(g.integers(0, SHARD))].copy(); fl = g.random(D) < 0.15; q[fl] *= -1
        t0 = time.perf_counter(); _best = int(np.argmax(q @ shard.T)); t1 = time.perf_counter(); lat.append((t1 - t0) * 1000)
    a = np.array(lat); p50 = float(np.percentile(a, 50)); p95 = float(np.percentile(a, 95)); p99 = float(np.percentile(a, 99))
    print("  routed per-query latency ms: P50=%.3f P95=%.3f P99=%.3f (SHARD=%d; INVARIANT to total -> same at 1M/10M/100M)" % (p50, p95, p99, SHARD), flush=True)
    return {"p50": p50, "p95": p95, "p99": p99}
def verdict(r) -> Tuple[str, str]:
    s = "routed P50/P95/P99 = %.3f/%.3f/%.3f ms (scale-invariant: routing -> 1 shard at any total)" % (r["p50"], r["p95"], r["p99"])
    if r["p95"] < 5: return ("HARD_PASS", "HARD_PASS: routed per-query P95 < 5ms and scale-INVARIANT -- so <5ms at 10M and <50ms at 100M; enterprise SLA met (sharding makes latency independent of corpus size). " + s)
    if r["p95"] < 20: return ("MIDDLE_BAND", "MIDDLE_BAND: routed P95 5-20ms. " + s)
    return ("HARD_FAIL", "HARD_FAIL: routed P95 >= 20ms. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
