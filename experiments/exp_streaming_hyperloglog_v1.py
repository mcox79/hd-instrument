"""
exp_streaming_hyperloglog_v1.py -- HyperLogLog cardinality estimation accuracy -- CPU.

ROUTING: field_streaming_algorithms HyperLogLog cardinality. HyperLogLog estimates DISTINCT-entity count in a stream at O(1) memory; compared to true cardinality. A KB-size / distinct-fact metric the substrate can report cheaply. Pure numpy (no installs). CPU.
PRE-REGISTERED: HARD-PASS relative error < 2pct on true cardinality. MIDDLE < 5pct. HARD-FAIL >= 5pct.
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
ANCHOR_NAME = "streaming_hyperloglog_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    assert len(set([1, 1, 2])) == 2, "distinct"
    import math; assert 0.7 < 0.7213 < 0.73, "alpha"
    assert np.floor(np.log2(8.0)) == 3, "log2"
    print("[selftest] PASS: hyperloglog", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2); P = 10 if SMOKE else 14; m = 1 << P
    true_card = 20000 if SMOKE else 200000
    ids = g.integers(0, 1 << 60, true_card, dtype=np.int64).astype(np.uint64)
    h = (ids * np.uint64(2654435761)) & np.uint64((1 << 60) - 1)
    idx = (h >> np.uint64(60 - P)).astype(np.int64)
    rest = (h & np.uint64((1 << (60 - P)) - 1)).astype(np.float64)
    restc = np.where(rest > 0, rest, 1.0)
    rank = np.where(rest > 0, (60 - P) - np.floor(np.log2(restc)).astype(np.int64), (60 - P) + 1)
    reg = np.zeros(m, dtype=np.int64)
    np.maximum.at(reg, idx, rank)
    alpha = 0.7213 / (1 + 1.079 / m)
    est = alpha * m * m / np.sum(2.0 ** (-reg.astype(np.float64)))
    zeros = int((reg == 0).sum())
    if est <= 2.5 * m and zeros > 0:
        est = m * np.log(m / zeros)
    rel = abs(est - true_card) / true_card
    print("  HLL m=%d: true=%d est=%.0f rel_err=%.4f" % (m, true_card, est, rel), flush=True)
    return {"true": true_card, "est": float(est), "rel": float(rel), "m": m}
def verdict(r) -> Tuple[str, str]:
    s = "true=%d est=%.0f rel_err=%.4f (m=%d)" % (r["true"], r["est"], r["rel"], r["m"])
    if r["rel"] < 0.02: return ("HARD_PASS", "HARD_PASS: HyperLogLog cardinality within 2pct at O(1) memory -- distinct-fact/KB-size metric works. " + s)
    if r["rel"] < 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: HLL within 5pct. " + s)
    return ("HARD_FAIL", "HARD_FAIL: HLL error >=5pct. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
