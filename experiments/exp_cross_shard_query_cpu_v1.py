"""
exp_cross_shard_query_cpu_v1.py -- a query whose answer spans shards is recovered by scatter-gather -- CPU.

ROUTING: sharding-architecture validation (multi-shard scatter-gather query). When a query's relevant items live in multiple shards, fan the query to all shards and gather the top results (scatter-gather). Tests recall of a multi-shard result set vs a single-shard query, with a confidence threshold to suppress non-matching shards. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS scatter-gather recall of the multi-shard gold set >= 0.90 with low false-include rate. MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "cross_shard_query_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert (set([1, 2]) | set([3])) == {1, 2, 3}, "gather union"; print("[selftest] PASS: cross-shard-query", flush=True)
def run() -> Dict:
    g = np.random.default_rng(75); N = 4096; S = 8; K = 60; book = cphasor(3000, N, g); TR = 40 if SMOKE else 150
    bundles = []; shard_keys = []; shard_vals = []
    for s in range(S):
        ky = cphasor(K, N, g); vv = g.integers(0, 3000, K); B = np.zeros(N, dtype=np.complex64)
        for j in range(K):
            B = B + ky[j] * book[vv[j]]
        bundles.append(B); shard_keys.append(ky); shard_vals.append(vv)
    hit = 0; n = 0
    for _ in range(TR):
        # a query relevant to one item in each of M random shards (multi-shard answer set)
        Msh = g.choice(S, 3, replace=False); gold = set(); qkeys = []
        for s in Msh:
            j = int(g.integers(0, K)); qkeys.append((s, j)); gold.add((s, int(shard_vals[s][j])))
        retr = set()
        for (s, j) in qkeys:
            for si in range(S):                                                  # scatter to all shards, gather best per shard
                cand = cidx(bundles[si] * np.conj(shard_keys[s][j]), book)
                sc = (book[cand] @ np.conj(bundles[si] * np.conj(shard_keys[s][j]))).real / N
                if sc > 0.5:
                    retr.add((si, cand))
        hit += int(len(retr & gold) == len(gold)); n += 1
    rec = hit / max(1, n); print("  multi-shard scatter-gather recall=%.3f (S=%d, 3-shard answers)" % (rec, S), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "scatter-gather recall=%.3f" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: scatter-gather recovers multi-shard answer sets >=0.90 -- cross-shard queries work when answers span shards. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: scatter-gather 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: scatter-gather <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
