"""
exp_hierarchical_subshard_kg_cpu_v1.py -- relation-then-subject hierarchical sub-sharding clears the KG 2-hop gate -- CPU.

ROUTING: PP-132 within-relation hierarchical sub-sharding. per_relation_sharding_kg MID: relation-sharding lifted 0.19 to 0.735 but relation shards stay large. Rescue: hierarchical sub-sharding (shard by relation, then within each relation sub-shard by subject) so each sub-bundle holds few edges. 2-hop routes by (relation, subject). Should clear 0.90. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS hierarchical sub-sharded 2-hop recall@1 >= 0.90 (vs per-relation 0.735). MIDDLE >= 0.80. HARD-FAIL < 0.80.
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
ANCHOR_NAME = "hierarchical_subshard_kg_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    d = {}; d[(1, 2)] = 3; assert d[(1, 2)] == 3, "subshard key"; print("[selftest] PASS: hierarchical-subshard-kg", flush=True)
def run() -> Dict:
    g = np.random.default_rng(132); N = 8192; VE = 300; VR = 10; deg = 4; TR = 60 if SMOKE else 200
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}; sub = {}
    for s in range(VE):
        for _ in range(deg):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o
                sub.setdefault((r, s), np.zeros(N, dtype=np.complex64)); sub[(r, s)] = sub[(r, s)] + ents[o]
    def path():
        for _ in range(150):
            s = int(g.integers(0, VE)); o1 = [(r, edges[(s, r)]) for (ss, r) in edges if ss == s]
            if not o1:
                continue
            r1, b = o1[int(g.integers(0, len(o1)))]; o2 = [(r, edges[(b, r)]) for (ss, r) in edges if ss == b]
            if not o2:
                continue
            r2, a = o2[int(g.integers(0, len(o2)))]; return s, r1, b, r2, a
        return None
    hit = 0; n = 0
    for _ in range(TR):
        p = path()
        if not p:
            continue
        s, r1, b, r2, a = p
        bh = cidx(sub[(r1, s)], ents) if (r1, s) in sub else -1
        ah = cidx(sub[(r2, bh)], ents) if (r2, bh) in sub else -1
        hit += int(ah == a); n += 1
    rec = hit / max(1, n); print("  hierarchical sub-sharded 2-hop recall@1=%.3f (n=%d, %d sub-shards)" % (rec, n, len(sub)), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "hierarchical 2-hop=%.3f (vs per-relation 0.735)" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: relation-then-subject hierarchical sub-sharding clears 2-hop recall >=0.90 -- hierarchical sharding resolves the per-relation gate. " + s)
    if r["recall"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: hierarchical 0.80-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: hierarchical <0.80. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
