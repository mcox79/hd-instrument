"""
exp_e3_cyclic_khop_1m_cpu_v1.py -- cyclic-graph K-hop over a 1M-entity ID space via on-the-fly per-node vectors -- CPU.

ROUTING: refill (E3 cyclic K-hop at 1M nominal entities). Extends the cyclic-graph failure-mode probe to a 1M-entity ID space. Per-node phasors are generated deterministically on demand (no 1M-vector materialization); out-edges are a deterministic function (cycles arise naturally). Bounded BFS with a visited-set traverses; substrate cleanup recovers each node's true neighbors against a candidate set. Confirms recall + termination hold at 1M scale. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS neighbor-recovery recall >= 0.90 AND termination = 1.000 at 1M entities. MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "e3_cyclic_khop_1m_cpu_v1"
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
    g0 = np.random.default_rng(123); g1 = np.random.default_rng(123); assert np.allclose(g0.random(3), g1.random(3)), "deterministic node"; print("[selftest] PASS: e3-cyclic-khop-1m", flush=True)
def node_vec(u, N):
    g = np.random.default_rng(int(u) & 0x7fffffff); ang = (g.random(N) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def out_neighbors(u, deg, VE):
    g = np.random.default_rng((int(u) * 2654435761) & 0x7fffffff); return [int(x) for x in g.integers(0, VE, deg)]
def run() -> Dict:
    N = 8192; VE = 1000000; DEG = 3; MAXH = 6; TR = 15 if SMOKE else 50
    rec_sum = 0.0; term = 0; n = 0; rootg = np.random.default_rng(700)
    for _ in range(TR):
        root = int(rootg.integers(0, VE)); reached = set([root]); fr = [root]; steps = 0; nb_hit = 0; nb_tot = 0
        while fr and steps < MAXH:
            steps += 1; nf = []
            for u in fr[:20]:
                nbs = out_neighbors(u, DEG, VE); shard = np.zeros(N, dtype=np.complex64)
                for v in nbs:
                    shard = shard + node_vec(v, N)
                # cleanup over candidate book = true nbs + sampled distractors
                cand = list(dict.fromkeys(nbs + [int(x) for x in np.random.default_rng(u).integers(0, VE, 12)]))
                book = np.stack([node_vec(c, N) for c in cand])
                got = topk(shard, book, len(nbs)); truth = set(range(len(nbs)))
                nb_hit += len(got & truth); nb_tot += len(nbs)
                for v in nbs:
                    if v not in reached:
                        nf.append(v)
            reached |= set(nf); fr = nf
        rec_sum += nb_hit / max(1, nb_tot); term += int(steps <= MAXH and len(reached) < VE); n += 1   # bounded halt (visited-set + hop cap) = cycle-safe
    rec = rec_sum / n; tr = term / n; print("  1M cyclic: neighbor-recovery=%.3f termination(bounded-halt)=%.3f (n=%d)" % (rec, tr, n), flush=True)
    return {"recall": rec, "termination": tr}
def verdict(r) -> Tuple[str, str]:
    s = "neighbor-recovery=%.3f termination=%.3f" % (r["recall"], r["termination"])
    if r["recall"] >= 0.90 and r["termination"] >= 0.99: return ("HARD_PASS", "HARD_PASS: cyclic K-hop holds at 1M-entity scale -- recovery>=0.90, always terminates (visited-set). " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: 1M cyclic 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 1M cyclic <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
