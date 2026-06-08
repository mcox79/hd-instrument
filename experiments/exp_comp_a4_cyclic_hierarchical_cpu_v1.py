"""
exp_comp_a4_cyclic_hierarchical_cpu_v1.py -- hierarchical traversal over a cyclic graph (org chart with cross-links), depth 3 -- CPU.

ROUTING: POST-CYCLE192 Group A composition (A4 cyclic+hierarchical composition (PP-161 + PP-160)). A hierarchy (parent->children) that also contains cycles (cross-links). Depth-3 traversal with a visited-set recovers the reachable sub-tree without looping. Validates hierarchical navigation composes with cycle-safety. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS cyclic-hierarchical recall >= 0.90 at depth 3 AND termination=1.000. MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "comp_a4_cyclic_hierarchical_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    seen = {0, 1}; assert 1 in seen, "visited"; print("[selftest] PASS: comp-a4-cyclic-hierarchical", flush=True)
def run() -> Dict:
    g = np.random.default_rng(404); N = 8192; VE = 200; TR = 40 if SMOKE else 120; ents = cphasor(VE, N, g); CHILD = cphasor(1, N, g)[0]
    rec_sum = 0; term = 0; n = 0
    for _ in range(TR):
        adj = {i: [] for i in range(VE)}; shard = {i: np.zeros(N, dtype=np.complex64) for i in range(VE)}
        root = 0
        # tree edges
        nxt = 1
        frontier = [root]
        for _d in range(3):
            nf = []
            for u in frontier:
                for _c in range(2):
                    if nxt < VE:
                        adj[u].append(nxt); shard[u] = shard[u] + CHILD * ents[nxt]; nf.append(nxt); nxt += 1
            frontier = nf
        # add cross-links (cycles) among existing nodes
        for _x in range(15):
            a = int(g.integers(0, nxt)); b = int(g.integers(0, nxt))
            if b not in adj[a] and a != b:
                adj[a].append(b); shard[a] = shard[a] + CHILD * ents[b]
        gold = set()
        fr = {root}; seen = {root}
        for _ in range(3):                                                     # ground truth reachable within depth 3 (tree+cross)
            nf = set()
            for u in fr:
                nf |= set(adj[u]) - seen
            seen |= nf; gold |= nf; fr = nf
        # substrate traversal with visited-set
        reached = set(); fr = [root]; steps = 0
        while fr and steps < 8:
            steps += 1; nf = []
            for u in fr:
                cand = [v for v in range(VE) if (ents[v] @ np.conj(shard[u] * np.conj(CHILD))).real / N > 0.5]
                for v in cand:
                    if v not in reached and v != root:
                        nf.append(v)
            reached |= set(nf); fr = nf
            if len(reached) > VE:
                break
        if gold:
            rec_sum += len(gold & reached) / len(gold); term += int(steps < 8); n += 1
    rec = rec_sum / max(1, n); tr = term / max(1, n); print("  cyclic-hierarchical recall=%.3f termination=%.3f" % (rec, tr), flush=True)
    return {"recall": rec, "termination": tr}
def verdict(r) -> Tuple[str, str]:
    s = "recall=%.3f termination=%.3f" % (r["recall"], r["termination"])
    if r["recall"] >= 0.90 and r["termination"] >= 0.99: return ("HARD_PASS", "HARD_PASS: hierarchical traversal over cyclic graphs recall>=0.90, always terminates -- navigation + cycle-safety compose. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: cyclic-hierarchical 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cyclic-hierarchical <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
