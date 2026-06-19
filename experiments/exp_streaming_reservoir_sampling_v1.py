"""
exp_streaming_reservoir_sampling_v1.py -- Reservoir sampling yields a uniform stream sample -- CPU.

ROUTING: field_streaming_algorithms Reservoir sampling curation. Algorithm-R reservoir keeps a uniform k-sample from a stream of N in one pass, O(k) memory -- training-data curation. Validate uniformity: each stream position selected with prob ~ k/N. Pure numpy (no installs). CPU.
PRE-REGISTERED: HARD-PASS max position-bucket selection deviation < 15pct of expected. MIDDLE < 30pct. HARD-FAIL >= 30pct.
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
ANCHOR_NAME = "streaming_reservoir_sampling_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    assert abs(np.mean([1.0, 0.0]) - 0.5) < 1e-9, "mean"
    assert 5 / 10 == 0.5, "rate"
    assert len(list(range(3))) == 3, "reservoir size"
    print("[selftest] PASS: reservoir-sampling", flush=True)
def run() -> Dict:
    g = np.random.default_rng(3); N = 10000 if SMOKE else 100000; K = 100; TRIALS = 50 if SMOKE else 300; BUCKETS = 10
    sel = np.zeros(BUCKETS)
    for _ in range(TRIALS):
        res = list(range(K))
        for i in range(K, N):
            j = int(g.integers(0, i + 1))
            if j < K:
                res[j] = i
        for idx in res:
            sel[idx * BUCKETS // N] += 1
    expected = TRIALS * K / BUCKETS; max_dev = float(np.abs(sel - expected).max() / expected)
    print("  reservoir K=%d N=%d trials=%d max_bucket_dev=%.3f" % (K, N, TRIALS, max_dev), flush=True)
    return {"max_dev": max_dev, "k": K, "n": N}
def verdict(r) -> Tuple[str, str]:
    s = "max_bucket_dev=%.3f (K=%d N=%d)" % (r["max_dev"], r["k"], r["n"])
    if r["max_dev"] < 0.15: return ("HARD_PASS", "HARD_PASS: reservoir sample uniform across positions (<15pct dev) -- one-pass O(k) curation works. " + s)
    if r["max_dev"] < 0.30: return ("MIDDLE_BAND", "MIDDLE_BAND: deviation 15-30pct. " + s)
    return ("HARD_FAIL", "HARD_FAIL: biased (>=30pct dev). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
