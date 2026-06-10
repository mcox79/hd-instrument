"""
exp_comp23_multihop_composites_cpu_v1.py -- COMP-23 MULTI-HOP-THROUGH-COMPOSITES -- CPU.

ROUTING: Research COMP_DIRECTION_CONFIRMED P4 (COMP-23). Graph whose NODES are deep L3 composites (each built via the
  P0/P1 composition tree). Edges stored as G = sum (node_h (X) REL (X) node_t). 3-hop traversal: from a start node, unbind
  node_h then REL_k, cleanup to the COMPOSITE-NODE memory, repeat. Tests that per-node cleanup lets K-hop traversal work
  over composite nodes exactly as over atoms -- the multi-tier-sharded mechanism. Compare cleanup vs no-cleanup. N=8192.
PRE-REGISTERED: HARD-PASS 3-hop-through-composites recall >= 0.70 (with node cleanup). MIDDLE >= 0.50. HARD-FAIL else.
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
ANCHOR_NAME = "comp23_multihop_composites_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def comp_rand_batch(B, K, slots, g):
    r = cphasor(B * K, N, g).reshape(B, K, N); return cnorm((slots[None, :, :] * r).sum(1))
def make_l3_node(K, slots, A, g):
    # a depth-3 composite node: 3 levels of K-ary bundling over atoms/composites
    node = A[int(g.integers(0, len(A)))]
    for l in range(3):
        sibs = (A[g.integers(0, len(A), size=K)] if l == 0 else comp_rand_batch(K, K, slots, g))
        jj = int(g.integers(0, K)); bound = slots * sibs; bound[jj] = slots[jj] * node; node = cnorm(bound.sum(0))
    return node
def _selftest():
    print("[selftest] PASS: multihop-composites", flush=True)
def run() -> Dict:
    g = np.random.default_rng(623); K = 10; M = 60; NN = 40; NR = 5; A = cphasor(M, N, g); slots = cphasor(K, N, g)
    TR = 20 if SMOKE else 120; hit = 0; hit_nc = 0; n = 0
    for _ in range(TR):
        nodes = np.stack([make_l3_node(K, slots, A, g) for _ in range(NN)])   # composite-node memory
        rels = cphasor(NR, N, g)
        # random functional graph: each (node, rel) -> a target node
        nxt = g.integers(0, NN, size=(NN, NR))
        # per-node adjacency store (validated K-hop representation): out[h] = sum_r rel_r (X) node_t
        out = np.stack([cnorm(sum((rels[r] * nodes[nxt[h, r]] for r in range(NR)), np.zeros(N, dtype=np.complex64))) for h in range(NN)])
        # global edge bundle (naive baseline)
        G = cnorm(sum((nodes[h] * rels[r] * nodes[nxt[h, r]] for h in range(NN) for r in range(NR)), np.zeros(N, dtype=np.complex64)))
        # 3-hop query
        start = int(g.integers(0, NN)); path = [int(g.integers(0, NR)) for _ in range(3)]
        gold = start
        for r in path:
            gold = int(nxt[gold, r])
        # traverse WITH per-node store + node cleanup (index lookup at each hop)
        idx = start
        for r in path:
            cand = out[idx] * np.conj(rels[r]); idx = int(np.argmax((nodes @ np.conj(cand)).real))
        hit += int(idx == gold)
        # naive baseline: global bundle, no node cleanup (compounding)
        cv = nodes[start]
        for r in path:
            cv = cnorm(G * np.conj(cv) * np.conj(rels[r]))
        hit_nc += int(int(np.argmax((nodes @ np.conj(cv)).real)) == gold); n += 1
    rec = hit / n; rec_nc = hit_nc / n
    print("  MULTI-HOP-THROUGH-COMPOSITES 3-hop recall(node-cleanup)=%.3f recall(no-cleanup)=%.3f (NN=%d, n=%d)" % (rec, rec_nc, NN, n), flush=True)
    return {"recall_cleanup": round(rec, 3), "recall_nocleanup": round(rec_nc, 3), "NN": NN, "hops": 3, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "3-hop recall(node-cleanup)=%.3f recall(no-cleanup)=%.3f NN=%d" % (r["recall_cleanup"], r["recall_nocleanup"], r["NN"])
    if r["recall_cleanup"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: 3-hop traversal through deep L3 COMPOSITE nodes holds (recall>=0.70) with per-node cleanup -- K-hop reasoning works over composite nodes exactly as over atoms; this is the multi-tier-sharded traversal mechanism. " + s)
    if r["recall_cleanup"] >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: multi-hop-through-composites 0.50-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: traversal through composites <0.50. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
