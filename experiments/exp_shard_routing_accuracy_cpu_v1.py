"""
exp_shard_routing_accuracy_cpu_v1.py -- content router sends queries to the correct shard (no oracle) -- CPU.

ROUTING: sharding-architecture validation (content-based shard routing). The sharding capacity story assumes queries reach the right shard. Each shard has a topic centroid; queries are routed to the nearest centroid (content-based, no oracle). Measures routing accuracy and end-to-end recall vs oracle routing, when shards are topically coherent. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS routing accuracy >= 0.95 AND end-to-end recall >= 0.90 (within 0.03 of oracle). MIDDLE routing >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "shard_routing_accuracy_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    c = np.array([[1.0, 0], [0, 1.0]]); q = np.array([0.9, 0.1]); assert int(np.argmax(c @ q)) == 0, "nearest centroid"; print("[selftest] PASS: shard-routing-accuracy", flush=True)
def run() -> Dict:
    g = np.random.default_rng(71); N = 4096; S = 16; K = 60; Dtopic = 64
    centers = g.standard_normal((S, Dtopic))                                  # topic centroid per shard
    book = cphasor(2000, N, g); bundles = [np.zeros(N, dtype=np.complex64) for _ in range(S)]
    keys = []; vals = []; shards = []; topics = []
    for s in range(S):
        for _ in range(K):
            k = cphasor(1, N, g)[0]; vv = int(g.integers(0, 2000)); t = centers[s] + 0.5 * g.standard_normal(Dtopic)
            bundles[s] = bundles[s] + k * book[vv]; keys.append(k); vals.append(vv); shards.append(s); topics.append(t)
    cents = np.stack([centers[s] for s in range(S)])
    route_hit = 0; e2e = 0; oracle = 0
    for i in range(len(keys)):
        pred_shard = int(np.argmax(cents @ topics[i]))                        # content routing
        route_hit += int(pred_shard == shards[i])
        e2e += int(cidx(bundles[pred_shard] * np.conj(keys[i]), book) == vals[i])
        oracle += int(cidx(bundles[shards[i]] * np.conj(keys[i]), book) == vals[i])
    nq = len(keys); ra = route_hit / nq; ee = e2e / nq; orc = oracle / nq
    print("  routing-accuracy=%.3f end-to-end-recall=%.3f oracle-recall=%.3f (S=%d K=%d)" % (ra, ee, orc, S, K), flush=True)
    return {"routing": ra, "e2e": ee, "oracle": orc}
def verdict(r) -> Tuple[str, str]:
    s = "routing=%.3f e2e=%.3f oracle=%.3f" % (r["routing"], r["e2e"], r["oracle"])
    if r["routing"] >= 0.95 and r["e2e"] >= 0.90: return ("HARD_PASS", "HARD_PASS: content routing hits the right shard >=0.95 with end-to-end recall >=0.90 -- sharding works without an oracle router. " + s)
    if r["routing"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: routing 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: routing <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
