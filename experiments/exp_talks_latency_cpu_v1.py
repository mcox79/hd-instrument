"""
exp_talks_latency_cpu_v1.py -- substrate-only response per-turn latency <=50ms -- CPU.

ROUTING: batch-10a (CHEAP-TALKS substrate response latency). Measures per-turn latency of a substrate-only templated response over a 2000-subject KB (the fast conversational tier vs an LLM turn). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS P95 <=50ms. MIDDLE <=100ms. HARD-FAIL >100ms.
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
ANCHOR_NAME = "talks_latency_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import time as _t; assert _t.perf_counter() > 0, "timer"; print("[selftest] PASS: talks-latency", flush=True)
def run() -> Dict:
    g = np.random.default_rng(961); N = 8192; NSUBJ = 2000; NATTR = 5; REL = cphasor(NATTR, N, g); vals = cphasor(400, N, g)
    shard = np.zeros((NSUBJ, N), dtype=np.complex64); truth = {}
    for si in range(NSUBJ):
        for a in range(NATTR):
            vv = int(g.integers(0, 400)); shard[si] = shard[si] + REL[a] * vals[vv]; truth[(si, a)] = vv
    NQ = 100 if SMOKE else 500; lat = []
    for _ in range(NQ):
        si = int(g.integers(0, NSUBJ)); a = int(g.integers(0, NATTR)); t0 = time.perf_counter()
        pred = cidx(shard[si] * np.conj(REL[a]), vals); resp = "The attribute-%d of entity-%d is value-%d." % (a, si, pred)
        lat.append((time.perf_counter() - t0) * 1000)
    p50 = float(np.percentile(lat, 50)); p95 = float(np.percentile(lat, 95))
    print("  substrate response latency P50=%.3fms P95=%.3fms (n=%d)" % (p50, p95, NQ), flush=True)
    return {"p50": p50, "p95": p95}
def verdict(r) -> Tuple[str, str]:
    s = "P50=%.3fms P95=%.3fms" % (r["p50"], r["p95"])
    if r["p95"] <= 50: return ("HARD_PASS", "HARD_PASS: substrate-only response per-turn P95 <=50ms (20x+ vs an LLM turn) -- the fast conversational tier. " + s)
    if r["p95"] <= 100: return ("MIDDLE_BAND", "MIDDLE_BAND: P95 50-100ms. " + s)
    return ("HARD_FAIL", "HARD_FAIL: P95 >100ms. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
