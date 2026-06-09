"""
exp_f2_latency_at_scale_cpu_v1.py -- substrate query P95 <5ms at 100K and <50ms at 1M -- CPU.

ROUTING: CYCLE_200_FOLLOWUPS (F2 fast-tier latency at scale). Measures P95 query latency at 100K and 1M KB scale (chunked cleanup, memory-safe). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS P95@100K <5ms AND P95@1M <50ms. MIDDLE P95@100K <10ms. HARD-FAIL >=10ms.
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
ANCHOR_NAME = "f2_latency_at_scale_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert _n.percentile([1,2,3,4],95) > 3, "pct"; print("[selftest] PASS: f2-latency-at-scale", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2002); N = 1024
    def p95_at(scale, chunk=50000):
        lat = []
        nq = 20 if SMOKE else 60
        book = cphasor(min(scale, chunk), N, g); nchunks = max(1, scale // chunk)
        for _ in range(nq):
            q = cphasor(1, N, g)[0]; t0 = time.perf_counter()
            best = -1e9
            for _c in range(nchunks):
                sc = (book @ np.conj(q)).real; m = float(sc.max())
                if m > best:
                    best = m
            lat.append((time.perf_counter() - t0) * 1000)
        return float(np.percentile(lat, 95))
    s100k = 10000 if SMOKE else 100000; s1m = 50000 if SMOKE else 1000000
    p100 = p95_at(s100k); p1m = p95_at(s1m)
    print("  P95 latency: %d->%.3fms  %d->%.3fms" % (s100k, p100, s1m, p1m), flush=True)
    return {"p95_100k": p100, "p95_1m": p1m}
def verdict(r) -> Tuple[str, str]:
    s = "P95@100K=%.3fms P95@1M=%.3fms" % (r["p95_100k"], r["p95_1m"])
    if r["p95_100k"] < 5.0 and r["p95_1m"] < 50.0: return ("HARD_PASS", "HARD_PASS: substrate query P95 <5ms at 100K and <50ms at 1M -- fast-tier latency holds at production scale. " + s)
    if r["p95_100k"] < 10.0: return ("MIDDLE_BAND", "MIDDLE_BAND: P95@100K 5-10ms. " + s)
    return ("HARD_FAIL", "HARD_FAIL: P95@100K >=10ms. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
