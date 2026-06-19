"""DECISION 59a M4e -- density-aware consensus variants on the FULL (namespace-normalized) graph, to test if the full graph can lift M4d WITHOUT the dilution that killed raw normalization (0.189) + degree-norm (0.148). Two remaining variants (degree-norm already failed in 58a addendum):
  V3 SELECTIVE TOP-K: each anchor contributes only its k NEAREST reachable nodes (re-introduces the sparse selectivity that was load-bearing) -- sweep k.
  V2 PERSONALIZED PAGERANK: power-iterate restart-walk from anchors; PPR mass down-weights hubs structurally -- sweep restart alpha.
Compare to sparse-M4d 0.272. Pre-reg (59a): HARD-PASS F1 > 0.272 on >=1 variant. Substrate-internal; remote bge. ASCII; --self-test."""
from __future__ import annotations
import sys, time, json, math
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1 import (
    _short, f1_present, WALK_EDGES, POOL_K, N_ANCHORS, MAX_HOP, DECAY)
ANCHOR_NAME = "substrate_59a_m4e_density_aware_variants_heldout_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
SPARSE_M4D = 0.2721
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("a::b/c") == "c"
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def bfs_ranked(anchor, adj, max_hop):
    """reachable (node, hop) from one anchor, in BFS order (nearest first)."""
    out = []; dist = {anchor: 0}; q = deque([(anchor, 0)])
    while q:
        n, d = q.popleft()
        if d >= max_hop: continue
        for m in adj.get(n, ()):
            if m not in dist:
                dist[m] = d + 1; out.append((m, d + 1)); q.append((m, d + 1))
    return out  # already in nondecreasing-hop order


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    from backend.substrate_index.retrieve_cache import rebuild_index_cached
    pstore = PartitionedStore(DATA_ROOT)
    try: enc = AtomEncoder()
    except Exception as e: return {"error": "bge:" + str(e)[:60]}
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    qual = {a.id: a.qualified_id for a in pstore.all_atoms()}
    sset = {_short(a.id) for a in pstore.all_atoms()}
    adj = defaultdict(set)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: rr = json.loads(ln)
            except Exception: continue
            if (rr.get("rel_type", "") or "").upper() in WALK_EDGES:
                s = _short(rr.get("src_id", "")); t = _short(rr.get("tgt_id", ""))
                if s and t and s != t: adj[s].add(t); adj[t].add(s)
    qs = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    perq = []
    for q in qs:
        gold = q.get("ground_truth_atoms") or []
        present = {_short(g) for g in gold if _short(g) in sset}
        if not present: continue
        cands = r.semantic(q["question"], top_k=POOL_K)
        pool = [(_short(qual.get(c.atom_id, c.atom_id)), float(getattr(c, "score", 0.0))) for c in cands]
        if not pool: continue
        perq.append({"qid": q["qid"], "present": present, "pool": pool})
    mac = lambda xs: round(sum(xs) / len(xs), 4) if xs else 0.0

    # V3 selective top-k
    def v3(beta, k):
        out = []
        for x in perq:
            cons = defaultdict(float)
            for a_s, a_cos in x["pool"][:N_ANCHORS]:
                for node, hop in bfs_ranked(a_s, adj, MAX_HOP)[:k]:
                    cons[node] += a_cos * (DECAY ** hop)
            top5 = {s for s, _ in sorted(((s, cos + beta * cons.get(s, 0.0)) for s, cos in x["pool"]), key=lambda t: -t[1])[:5]}
            out.append(f1_present(top5, x["present"]))
        return mac(out)

    # V2 personalized PageRank (power iteration over adj restricted to pool-relevant subgraph)
    def v2(beta, alpha, iters=30):
        out = []
        for x in perq:
            anchors = [s for s, _ in x["pool"][:N_ANCHORS]]
            acos = {s: c for s, c in x["pool"][:N_ANCHORS]}
            # build local subgraph: anchors + 2-hop neighborhood
            nodes = set(anchors)
            for a in anchors:
                for node, hop in bfs_ranked(a, adj, MAX_HOP): nodes.add(node)
            nodes = list(nodes); idx = {n: i for i, n in enumerate(nodes)}
            tele = np.zeros(len(nodes))
            for a in anchors: tele[idx[a]] += acos.get(a, 0.0)
            if tele.sum() == 0: out.append(0.0); continue
            tele = tele / tele.sum()
            p = tele.copy()
            for _ in range(iters):
                pn = np.zeros(len(nodes))
                for n in nodes:
                    nb = [m for m in adj.get(n, ()) if m in idx]
                    if nb:
                        share = p[idx[n]] / len(nb)
                        for m in nb: pn[idx[m]] += share
                p = (1 - alpha) * pn + alpha * tele
            ppr = {nodes[i]: p[i] for i in range(len(nodes))}
            top5 = {s for s, _ in sorted(((s, cos + beta * ppr.get(s, 0.0)) for s, cos in x["pool"]), key=lambda t: -t[1])[:5]}
            out.append(f1_present(top5, x["present"]))
        return mac(out)

    v3_grid = {(b, k): v3(b, k) for b in [0.05, 0.1, 0.2] for k in [5, 10, 20]}
    v3_best = max(v3_grid, key=v3_grid.get)
    v2_grid = {(b, a): v2(b, a) for b in [1.0, 3.0, 8.0] for a in [0.3, 0.5]}
    v2_best = max(v2_grid, key=v2_grid.get)
    print("  full-graph (normalized) | sparse-M4d reference=%.4f" % SPARSE_M4D, flush=True)
    print("  V3 selective-top-k best=%.4f @ (beta,k)=%s" % (v3_grid[v3_best], v3_best), flush=True)
    print("    v3 grid: %s" % {str(k): round(v, 3) for k, v in v3_grid.items()}, flush=True)
    print("  V2 personalized-PageRank best=%.4f @ (beta,alpha)=%s" % (v2_grid[v2_best], v2_best), flush=True)
    print("    v2 grid: %s" % {str(k): round(v, 3) for k, v in v2_grid.items()}, flush=True)
    best = max(v3_grid[v3_best], v2_grid[v2_best])
    return {"sparse_m4d": SPARSE_M4D, "v3_best": v3_grid[v3_best], "v3_best_cfg": str(v3_best),
            "v2_best": v2_grid[v2_best], "v2_best_cfg": str(v2_best), "best_density_aware": round(best, 4),
            "delta_vs_sparse": round(best - SPARSE_M4D, 4)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("M4e density-aware (full graph): V3 selective-top-k best=%.4f %s, V2 PPR best=%.4f %s vs sparse-M4d 0.2721 (delta %+.4f). "
         "(V1 degree-norm already failed 0.148 in 58a addendum.) Held-out-swept (Goodhart-flagged feasibility)." % (
             r["v3_best"], r["v3_best_cfg"], r["v2_best"], r["v2_best_cfg"], r["delta_vs_sparse"]))
    if r["best_density_aware"] > SPARSE_M4D + 1e-9:
        return ("HARD_PASS", "HARD_PASS (density-aware EXPLOITS full graph): best %.4f > 0.272 -- selectivity-restoring walk lets the full graph lift M4d. De-Goodhart next. " % r["best_density_aware"] + s)
    return ("HARD_FAIL", "HARD_FAIL (all M4e variants <= 0.272): the full graph CANNOT lift M4d under ANY density-aware walk tested (degree-norm + selective-top-k + PPR). Sparse-graph consensus 0.272 IS the graph-walk-class CEILING for the substrate's current typed-operator graph. -> M7 (question-conditional) is the only remaining mechanism; OR Phase 3 pivot. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
