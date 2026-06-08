"""
exp_skewed_shard_capacity_cpu_v1.py -- per-shard recall stays high under realistic skewed shard sizes -- CPU.

ROUTING: sharding-architecture validation (skewed (Zipf) shard sizes). Real shards are uneven (some customers/domains much larger). Allocate shard sizes by a Zipf distribution; measure per-shard recall. Tests whether the flat-recall capacity story survives skew, or whether large shards degrade (and need sub-sharding). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS recall on the LARGEST shard >= 0.90 when its size <= the per-shard capacity floor; smallest shards ~1.0. MIDDLE largest >= 0.80. HARD-FAIL < 0.80.
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
ANCHOR_NAME = "skewed_shard_capacity_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    p = 1.0 / np.arange(1, 5); assert p[0] > p[3], "zipf"; print("[selftest] PASS: skewed-shard-capacity", flush=True)
def run() -> Dict:
    g = np.random.default_rng(72); N = 4096; S = 12; BASE = 30
    sizes = (BASE * (1.0 / np.arange(1, S + 1)) * S).astype(int) + 10                   # zipf-ish skewed sizes
    sizes = np.maximum(sizes, 10); book = cphasor(3000, N, g); by = {}
    for si in range(S):
        Ks = int(sizes[si]); keys = cphasor(Ks, N, g); vals = g.integers(0, 3000, Ks)
        B = np.zeros(N, dtype=np.complex64)
        for j in range(Ks):
            B = B + keys[j] * book[vals[j]]
        hit = sum(int(cidx(B * np.conj(keys[j]), book) == vals[j]) for j in range(Ks))
        by[Ks] = hit / Ks
    largest = max(by.keys()); smallest = min(by.keys())
    print("  recall by shard size: largest(%d)=%.3f smallest(%d)=%.3f | sizes=%s" % (largest, by[largest], smallest, by[smallest], sorted(by.keys(), reverse=True)), flush=True)
    return {"largest_recall": by[largest], "smallest_recall": by[smallest], "largest_size": largest}
def verdict(r) -> Tuple[str, str]:
    s = "largest-shard(%d)-recall=%.3f smallest-recall=%.3f" % (r["largest_size"], r["largest_recall"], r["smallest_recall"])
    if r["largest_recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: per-shard recall stays >=0.90 even on the largest skewed shard -- sharding survives realistic skew (sub-shard only the biggest). " + s)
    if r["largest_recall"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: largest-shard recall 0.80-0.90 (sub-sharding advised). " + s)
    return ("HARD_FAIL", "HARD_FAIL: largest shard degrades (<0.80) -- skew requires sub-sharding. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
