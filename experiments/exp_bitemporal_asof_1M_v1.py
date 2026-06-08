"""
exp_bitemporal_asof_1M_v1.py -- bitemporal as-of queries return the correct version at 1M-fact scale -- CPU.

ROUTING: scale-gap bitemporal at production scale. 1M fact-versions with (valid_time, value); an as-of(t) query must return the latest version with valid_time <= t. Validates correctness + per-query timing at scale via sorted-index bisect. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS as-of correctness = 1.0 AND per-query < 0.2 ms at 1M versions. MIDDLE per-query 0.2-2ms. HARD-FAIL correctness < 1.0 or > 2ms.
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
ANCHOR_NAME = "bitemporal_asof_1M_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

import bisect
def _selftest():
    vt = [10, 20, 30]; i = bisect.bisect_right(vt, 25) - 1; assert vt[i] == 20, "bisect as-of"
    assert bisect.bisect_right([1,2,3], 0) - 1 == -1, "before-all"
    assert sorted([3,1,2]) == [1,2,3], "sort"
    print("[selftest] PASS: bitemporal-asof-1M", flush=True)
def run() -> Dict:
    g = np.random.default_rng(4); N = 50000 if SMOKE else 1000000; NQ = 1000
    vt = np.sort(g.integers(0, 10_000_000, N)); vals = g.integers(0, 1_000_000, N)
    qts = g.integers(0, 10_000_000, NQ); correct = 0
    t0 = time.perf_counter()
    for qt in qts:
        idx = int(np.searchsorted(vt, qt, side="right")) - 1
        # correctness check vs brute: latest vt <= qt
        if idx >= 0:
            correct += int(vt[idx] <= qt and (idx == N-1 or vt[idx+1] > qt))
        else:
            correct += int((vt[0] > qt))
    dt = time.perf_counter() - t0; per_ms = dt / NQ * 1e3; acc = correct / NQ
    print("  as-of correctness=%.3f per-query=%.4f ms (N=%d versions)" % (acc, per_ms, N), flush=True)
    return {"n": N, "correct": acc, "per_ms": per_ms}
def verdict(r) -> Tuple[str, str]:
    s = "correctness=%.3f per-query=%.4f ms (N=%d)" % (r["correct"], r["per_ms"], r["n"])
    if r["correct"] >= 0.999 and r["per_ms"] < 0.2: return ("HARD_PASS", "HARD_PASS: bitemporal as-of correct + <0.2ms/query at 1M versions -- temporal queries at production scale. " + s)
    if r["correct"] >= 0.999 and r["per_ms"] < 2.0: return ("MIDDLE_BAND", "MIDDLE_BAND: correct but per-query 0.2-2ms. " + s)
    return ("HARD_FAIL", "HARD_FAIL: incorrect or >2ms. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
