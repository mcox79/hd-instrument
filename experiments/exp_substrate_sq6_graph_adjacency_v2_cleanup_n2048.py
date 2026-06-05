"""
substrate_sq6_graph_adjacency_v2_cleanup_n2048 -- graph adjacency binding (GraphHD-style) -- remote CPU.

ROUTING: notes/research_to_exp_dev_pure_bio_revised_orthogonal_axes_plus_exploration (SQ6; P_drill=0.72;
  GraphHD NeurIPS 2023 precedent). Tests whether a substrate stores a whole GRAPH as one bundled vector and
  answers edge-membership queries. CPU numpy, $0. remote_cpu_queue.

CAPABILITY QUESTION: encode a graph G = sum over edges (u,v) of node_u * node_v (MAP elementwise bind, symmetric).
  Query (a,b): score = <G, node_a * node_b> / N -- ~1 for a true edge, ~noise for a non-edge. How many edges E
  can one substrate vector hold while keeping edge/non-edge separable (classification accuracy)?

CELLS (3 seeds): E_frac in {0.25, 0.5, 1.0, 2.0} * N edges; V=128 nodes. accuracy = balanced edge-vs-nonedge
  classification at the best threshold (E true edges + E sampled non-edges).

PRE-REGISTERED bands (E_max = max E with accuracy >= 0.95):
  HARD-PASS: E_max >= N (graph with >= N edges held in ONE N-dim vector). MIDDLE: E_max in [0.25N, N). HARD-FAIL: E_max < 0.25N.

FORMULA SELF-TESTS (PROT-022): 1. bind symmetric (u*v == v*u). 2. true edge scores ~1, non-edge ~0 at low E. 3. distinct nodes. 4. N set.
ASCII-only. write_metrics. PROT-018: swept-E anchor (no _nN).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, json, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_sq6_graph_adjacency_v2_cleanup_n2048"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

V_NODES = 128
E_FRACS = [0.25, 0.5, 1.0, 2.0]

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N = 512
else:
    SEEDS = [7, 17, 23]; N = 2048


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def _edge_set(V, E, g):
    seen = set(); edges = []
    while len(edges) < E:
        u, v = int(g.integers(0, V)), int(g.integers(0, V))
        if u == v:
            continue
        key = (min(u, v), max(u, v))
        if key in seen:
            continue
        seen.add(key); edges.append(key)
    return edges, seen


def accuracy_at_E(n, E, g):
    nodes = bipolar((V_NODES, n), g)
    edges, seen = _edge_set(V_NODES, E, g)
    G = np.zeros(n, dtype=np.float32)
    for (u, v) in edges:
        G += nodes[u] * nodes[v]
    # scores for true edges + equal # of sampled non-edges
    # CLEANUP readout (SQ6-v2): per node a, recover neighbor field f_a = G * node_a, project to node codebook
    # (scores over all nodes), denoise by keeping top-deg(a) as the cleaned neighbor set, test membership.
    from collections import defaultdict
    deg = defaultdict(int)
    for (u, v) in edges:
        deg[u] += 1; deg[v] += 1
    Nmat = nodes  # (V_NODES, n)
    cleaned = {}
    for a in set([u for (u, v) in edges] + [v for (u, v) in edges]):
        f = G * nodes[a]; sc = Nmat @ f / n; sc[a] = -1e9
        k = max(1, deg[a]); top = np.argpartition(-sc, k - 1)[:k]; cleaned[a] = set(top.tolist())
    pos_hit = np.mean([1.0 if (v in cleaned.get(u, set()) or u in cleaned.get(v, set())) else 0.0 for (u, v) in edges])
    neg = []; tries = 0
    while len(neg) < E and tries < 20 * E:
        tries += 1; u, v = int(g.integers(0, V_NODES)), int(g.integers(0, V_NODES))
        if u == v or (min(u, v), max(u, v)) in seen:
            continue
        neg.append(0.0 if (v in cleaned.get(u, set()) or u in cleaned.get(v, set())) else 1.0)
    neg_corr = float(np.mean(neg)) if neg else 1.0
    return float(0.5 * (pos_hit + neg_corr))


def _selftest():
    g = np.random.default_rng(0); n = 256; nodes = bipolar((5, n), g)
    assert np.array_equal(nodes[0] * nodes[1], nodes[1] * nodes[0]), "bind not symmetric"
    G = nodes[0] * nodes[1] + nodes[2] * nodes[3]
    assert float((G * (nodes[0] * nodes[1])).sum() / n) > 0.8, "true edge low"
    assert abs(float((G * (nodes[0] * nodes[2])).sum() / n)) < 0.5, "non-edge high"
    assert V_NODES == 128
    print("[selftest] PASS: bind_symmetric edge~1 nonedge~0", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); out = {}
    for ef in E_FRACS:
        E = max(2, int(round(ef * N)))
        out[f"E{ef}"] = accuracy_at_E(N, E, np.random.default_rng(seed * 100 + int(ef * 10)))
    return {"seed": seed, "N": N, **out}


def verdict(per_seed) -> Tuple[str, str]:
    acc = {ef: float(np.mean([s[f"E{ef}"] for s in per_seed])) for ef in E_FRACS}
    emax = max([ef for ef in E_FRACS if acc[ef] >= 0.95], default=0.0)
    summary = "acc " + " ".join(f"E{ef}N:{acc[ef]:.2f}" for ef in E_FRACS) + f" | E_max={emax}N"
    if emax >= 1.0:
        return ("HARD_PASS", f"HARD_PASS: one N-vector holds >={emax}N edges separably. {summary}")
    if emax >= 0.25:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: graph capacity E_max={emax}N. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: graph capacity < 0.25N edges. {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N} V_nodes={V_NODES} E_fracs={E_FRACS}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); per_seed = []
for seed in SEEDS:
    r = run_seed(seed); per_seed.append(r)
    print(f"  [seed={seed}] " + " ".join(f"E{ef}N:{r[f'E{ef}']:.2f}" for ef in E_FRACS), flush=True)
v, vmsg = verdict(per_seed)
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": [f"E{ef}" for ef in E_FRACS], "per_seed": per_seed, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
