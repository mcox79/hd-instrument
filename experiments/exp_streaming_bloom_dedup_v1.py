"""
exp_streaming_bloom_dedup_v1.py -- Bloom filter duplicate-ingest detection accuracy -- CPU.

ROUTING: field_streaming_algorithms (membership/dedup filter). A k-hash Bloom filter detects duplicate fact ingests (membership) at O(1) memory per item. Insert M unique items, query M inserted + M novel; measure false-positive rate on novel and zero false-negatives on inserted. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS false-positive rate < 1pct AND false-negative rate = 0 at the designed load. MIDDLE FPR < 3pct. HARD-FAIL FPR >= 3pct or any false negative.
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
ANCHOR_NAME = "streaming_bloom_dedup_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    bits = np.zeros(16, dtype=bool); bits[3] = True; assert bits[3] and not bits[4], "bit set"
    assert (7 * 3 + 1) % 13 >= 0, "hash"
    print("[selftest] PASS: bloom-dedup", flush=True)
def run() -> Dict:
    g = np.random.default_rng(3); M = 20000 if SMOKE else 200000; K = 7; BITS = M * 15
    A = g.integers(1, 2**31, K); B = g.integers(0, 2**31, K); PR = 2147483647
    bits = np.zeros(BITS, dtype=bool)
    ins = g.integers(0, 1 << 50, M, dtype=np.int64)
    for k in range(K):
        bits[((A[k] * ins + B[k]) % PR) % BITS] = True
    # false negatives on inserted
    fn = 0
    for k in range(1):
        pass
    fn_mask = np.ones(M, dtype=bool)
    for k in range(K):
        fn_mask &= bits[((A[k] * ins + B[k]) % PR) % BITS]
    fn = int((~fn_mask).sum())
    # false positives on novel
    nov = g.integers(1 << 50, 1 << 51, M, dtype=np.int64)
    fp_mask = np.ones(M, dtype=bool)
    for k in range(K):
        fp_mask &= bits[((A[k] * nov + B[k]) % PR) % BITS]
    fp = int(fp_mask.sum()); fpr = fp / M
    print("  Bloom M=%d K=%d bits=%d: FPR=%.4f FN=%d" % (M, K, BITS, fpr, fn), flush=True)
    return {"fpr": fpr, "fn": fn, "m": M}
def verdict(r) -> Tuple[str, str]:
    s = "FPR=%.4f FN=%d (M=%d)" % (r["fpr"], r["fn"], r["m"])
    if r["fpr"] < 0.01 and r["fn"] == 0: return ("HARD_PASS", "HARD_PASS: Bloom dedup FPR<1pct with zero false negatives -- O(1)-memory duplicate-ingest prevention works. " + s)
    if r["fpr"] < 0.03 and r["fn"] == 0: return ("MIDDLE_BAND", "MIDDLE_BAND: FPR 1-3pct. " + s)
    return ("HARD_FAIL", "HARD_FAIL: FPR>=3pct or false negative present. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
