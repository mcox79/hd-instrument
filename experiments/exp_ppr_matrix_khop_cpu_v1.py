"""
exp_ppr_matrix_khop_cpu_v1.py -- matrix PPR over substrate-derived adjacency (proper HippoRAG) -- CPU.

ROUTING: hybrid / native multi-hop mechanism (I3-rescue matrix personalized-PageRank). RESCUE of naive iterative-unbind PPR (HARD_FAIL 0.22). Build the adjacency matrix by reading neighbors out of the substrate (per node, per relation, threshold), then run TRUE personalized PageRank (power iteration on the row-normalized matrix). Measures recall@K of the 2-hop neighborhood. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS recall@K of 2-hop neighborhood >= 0.70 with convergence <= 20 iters. MIDDLE >= 0.55. HARD-FAIL < 0.55.
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
ANCHOR_NAME = "ppr_matrix_khop_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def build_kg(g, N, VE, VR, deg):
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}; M = np.zeros(N, dtype=np.complex64)
    for s in range(VE):
        for _ in range(deg):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]
    return ents, rels, edges, M
def sample_path(edges, VE, g, hops):
    for _ in range(150):
        s = int(g.integers(0, VE)); path = [s]; rseq = []
        ok = True
        for _h in range(hops):
            outs = [r for (ss, r) in edges if ss == path[-1]]
            if not outs:
                ok = False; break
            r = int(g.choice(outs)); rseq.append(r); path.append(edges[(path[-1], r)])
        if ok:
            return path, rseq
    return None, None

def _selftest():
    A = np.array([[0.0, 1.0], [1.0, 0.0]]); An = A / A.sum(1, keepdims=True); assert np.allclose(An.sum(1), 1), "row norm"; print("[selftest] PASS: ppr-matrix-khop", flush=True)
def run() -> Dict:
    g = np.random.default_rng(64); N = 8192; VE = 120; VR = 8; DAMP = 0.5; TR = 20 if SMOKE else 60
    ents, rels, edges, M = build_kg(g, N, VE, VR, 2)
    adj = {i: [] for i in range(VE)}
    for (s, r), o in edges.items():
        adj[s].append(o)
    # build adjacency MATRIX by reading neighbors out of the substrate (per node, per relation)
    A = np.zeros((VE, VE))
    for u in range(VE):
        for r in range(VR):
            v = cidx(M * np.conj(ents[u] * rels[r]), ents)
            if (ents[v] @ np.conj(M * np.conj(ents[u] * rels[r]))).real / N > 0.30:
                A[u, v] = 1.0
    An = A / np.clip(A.sum(1, keepdims=True), 1, None)
    def true_2hop(seed):
        h1 = set(adj[seed]); h2 = set()
        for u in h1:
            h2 |= set(adj[u])
        return (h1 | h2) - {seed}
    recs = []; iters = []
    for _ in range(TR):
        seed = int(g.integers(0, VE)); tgt = true_2hop(seed)
        if not tgt:
            continue
        e = np.zeros(VE); e[seed] = 1.0; pi = e.copy()
        it = 20
        for k in range(50):
            new = (1 - DAMP) * e + DAMP * (An.T @ pi)
            if np.abs(new - pi).sum() < 1e-4:
                it = k; pi = new; break
            pi = new
        retr = set(np.argsort(-pi)[:len(tgt) + 1].tolist()) - {seed}
        recs.append(len(retr & tgt) / len(tgt)); iters.append(it)
    rec = float(np.mean(recs)); itc = float(np.mean(iters)); print("  matrix-PPR recall@K=%.3f convergence-iters=%.1f" % (rec, itc), flush=True)
    return {"recall": rec, "iters": itc}
def verdict(r) -> Tuple[str, str]:
    s = "matrix-PPR recall=%.3f iters=%.1f" % (r["recall"], r["iters"])
    if r["recall"] >= 0.70 and r["iters"] <= 20: return ("HARD_PASS", "HARD_PASS: matrix PPR over substrate-derived adjacency recall>=0.70 with fast convergence -- proper HippoRAG spreading works (rescues the naive iterative-unbind PPR). " + s)
    if r["recall"] >= 0.55: return ("MIDDLE_BAND", "MIDDLE_BAND: matrix-PPR recall 0.55-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: matrix-PPR recall <0.55. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
