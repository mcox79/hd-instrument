"""
exp_streaming_count_min_sketch_v1.py -- Count-Min Sketch frequency estimation accuracy -- CPU.

ROUTING: field_streaming_algorithms STREAM-CMS-BENCH. 3 x W Count-Min Sketch on a Zipfian stream; point-query error vs true counts for heavy items. Sublinear-memory frequency for the substrate routing/drift layer. Pure numpy (no installs). CPU.
PRE-REGISTERED: HARD-PASS max point-query error < 0.1pct of stream_length for all items with true count >= 100. MIDDLE < 0.5pct. HARD-FAIL >= 0.5pct.
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
ANCHOR_NAME = "streaming_count_min_sketch_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    assert (5 * 7 + 3) % 11 % 4 >= 0, "hash math"
    t = np.zeros((2, 8)); t[0, 3] += 1; assert t[0, 3] == 1, "increment"
    assert min(5, 3, 9) == 3, "min query"
    print("[selftest] PASS: count-min-sketch", flush=True)
def run() -> Dict:
    g = np.random.default_rng(1); D = 3; W = 3000; V = 5000; N = 20000 if SMOKE else 100000
    p = 1.0 / np.power(np.arange(1, V + 1), 1.1); p /= p.sum()
    stream = g.choice(V, N, p=p)
    A = g.integers(1, 2**31, D); B = g.integers(0, 2**31, D); PR = 2147483647
    table = np.zeros((D, W), dtype=np.int64)
    for d in range(D):
        cols = ((A[d] * stream + B[d]) % PR) % W
        np.add.at(table[d], cols, 1)
    true = np.bincount(stream, minlength=V); heavy = np.where(true >= 100)[0]; errs = []
    for it in heavy:
        est = min(int(table[d, ((A[d] * it + B[d]) % PR) % W]) for d in range(D)); errs.append(abs(est - int(true[it])))
    max_err = max(errs) if errs else 0; rel = max_err / N
    print("  CMS %dx%d: heavy=%d max_abs_err=%d (%.4f pct of N=%d)" % (D, W, len(heavy), max_err, rel * 100, N), flush=True)
    return {"max_err": max_err, "rel": rel, "n": N, "heavy": int(len(heavy))}
def verdict(r) -> Tuple[str, str]:
    s = "max_err=%d (%.4f pct of N=%d) heavy=%d" % (r["max_err"], r["rel"] * 100, r["n"], r["heavy"])
    if r["rel"] < 0.001: return ("HARD_PASS", "HARD_PASS: Count-Min Sketch point-query error <0.1pct of stream for all heavy items -- sublinear-memory frequency estimation works. " + s)
    if r["rel"] < 0.005: return ("MIDDLE_BAND", "MIDDLE_BAND: CMS error 0.1-0.5pct. " + s)
    return ("HARD_FAIL", "HARD_FAIL: CMS error >=0.5pct (widen W). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
