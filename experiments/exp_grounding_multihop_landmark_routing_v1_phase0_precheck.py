"""PHASE 0 (zero-cost, no dispatch): KB-graph landmark-viability pre-check.

Characterizes the EXACT ConceptNet subgraph the reader cells use (load_typed_cn_subgraph at
FULL n_nodes=5000, SUBGRAPH_BASE_SEED=1234, then build_typed_diradj -> undirected typed multigraph).

Three questions (from notes/research_landmark_subgoal_hub_routing_autonomous_traversal_2026-07-09.md):
  Q1 degree distribution: heavy-tailed/hub-y OR uniform/expander-like?
  Q2 betweenness concentration: a few high-betweenness HUB nodes OR near-uniform?
  Q3 nearest-landmark hop distance: for typical path nodes, is a high-degree/high-betweenness
     landmark within ~1 hop (the certified short-range regime)?

DECISION GATE (pre-registered thresholds below):
  PROCEED if hub structure present AND landmarks ~1-hop reachable.
  STOP    if expander-like (no clean bottlenecks) OR landmarks too far (>1 hop).
ASCII-only. Read-only analysis. No graph mutation, no dispatch.
"""
import json
import os
import sys
from collections import deque

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import networkx as nx  # noqa: E402
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import SUBGRAPH_BASE_SEED  # noqa: E402
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import load_typed_cn_subgraph  # noqa: E402
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import build_typed_diradj, sample_chains  # noqa: E402

N_NODES = 5000            # FULL config (matches reader cell FULL_CFG)
MAX_REACH = 4
BETW_PIVOTS = 600         # sampled-betweenness pivots (exact is O(VE); sample is plenty for concentration)
LANDMARK_KS = [32, 64, 128, 256]   # candidate landmark-set sizes (~0.6%-5% of nodes)
N_CHAINS_SAMPLE = 1500    # sampled traversal chains -> the actual "path node" population

# --- pre-registered decision thresholds (structural; set BEFORE seeing numbers) ---
HUB_MAXdeg_over_MEAN = 10.0    # heavy tail: max degree >= 10x mean degree
HUB_TOP5PCT_SHARE = 0.30       # top-5% of nodes hold >= 30% of total degree (uniform would be ~5%)
HUB_BETW_TOP1PCT_SHARE = 0.20  # top-1% of nodes hold >= 20% of total betweenness (uniform ~1%)
LM_K_FOR_GATE = 128            # the landmark-set size the gate is evaluated at (~2.5% of nodes)
LM_MEDIAN_HOP_MAX = 1.0        # median nearest-landmark hop distance <= 1
LM_WITHIN1_FRAC_MIN = 0.60     # >= 60% of path nodes within 1 hop of a landmark


def gini(x):
    x = np.sort(np.asarray(x, dtype=np.float64))
    n = x.shape[0]
    if n == 0 or x.sum() == 0:
        return float("nan")
    cum = np.cumsum(x)
    return float((n + 1 - 2 * (cum / cum[-1]).sum()) / n)


def multi_source_bfs_dist(adj, sources, n):
    """distance from every node to nearest source (undirected BFS). -1 if unreachable."""
    dist = np.full(n, -1, dtype=np.int64)
    dq = deque()
    for s in sources:
        dist[s] = 0
        dq.append(s)
    while dq:
        u = dq.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                dq.append(v)
    return dist


def main():
    print("[phase0] loading typed CN subgraph n_nodes=%d seed=%d ..." % (N_NODES, SUBGRAPH_BASE_SEED), flush=True)
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(N_NODES, SUBGRAPH_BASE_SEED)
    n = len(node_ids)
    dir_adj = build_typed_diradj(edges, rels, n)

    # Undirected simple adjacency (dedup neighbors; dir_adj already symmetric)
    adj = [set() for _ in range(n)]
    for u in range(n):
        for (v, r) in dir_adj[u]:
            if v != u:
                adj[u].add(v)
    adj = [sorted(s) for s in adj]
    deg = np.array([len(a) for a in adj], dtype=np.int64)

    print("[phase0] meta: n_nodes=%d n_edges=%d median_degree(meta)=%s rel_types=%d"
          % (meta.get("n_nodes"), meta.get("n_edges"), meta.get("median_degree"), T), flush=True)

    # ---- Q1 degree distribution ----
    deg_pos = deg[deg > 0]
    mean_d = float(deg_pos.mean())
    median_d = float(np.median(deg_pos))
    max_d = int(deg_pos.max())
    total_deg = float(deg.sum())
    order = np.argsort(-deg)
    top5pct_n = max(1, int(round(0.05 * n)))
    top1pct_n = max(1, int(round(0.01 * n)))
    top5pct_share = float(deg[order[:top5pct_n]].sum() / total_deg)
    top1pct_share = float(deg[order[:top1pct_n]].sum() / total_deg)
    deg_gini = gini(deg_pos)
    frac_ge_5x_mean = float((deg_pos >= 5.0 * mean_d).mean())
    q1_hub = bool(max_d >= HUB_MAXdeg_over_MEAN * mean_d and top5pct_share >= HUB_TOP5PCT_SHARE)

    print("\n[Q1 DEGREE] n_pos=%d mean=%.2f median=%.1f max=%d (max/mean=%.1fx) gini=%.3f"
          % (deg_pos.shape[0], mean_d, median_d, max_d, max_d / mean_d, deg_gini), flush=True)
    print("[Q1 DEGREE] top1%%share=%.3f top5%%share=%.3f frac(deg>=5x mean)=%.3f | hub_by_degree=%s"
          % (top1pct_share, top5pct_share, frac_ge_5x_mean, q1_hub), flush=True)

    # ---- Q2 betweenness concentration (sampled pivots) ----
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for u in range(n):
        for v in adj[u]:
            if u < v:
                G.add_edge(u, v)
    kpiv = min(n, BETW_PIVOTS)
    print("\n[Q2 BETW] computing sampled betweenness (k=%d pivots on %d nodes / %d edges)..."
          % (kpiv, n, G.number_of_edges()), flush=True)
    bc = nx.betweenness_centrality(G, k=kpiv, normalized=True, seed=SUBGRAPH_BASE_SEED)
    bcv = np.array([bc[i] for i in range(n)], dtype=np.float64)
    bc_order = np.argsort(-bcv)
    bc_total = float(bcv.sum())
    bc_top1_share = float(bcv[bc_order[:top1pct_n]].sum() / bc_total) if bc_total > 0 else float("nan")
    bc_top5_share = float(bcv[bc_order[:top5pct_n]].sum() / bc_total) if bc_total > 0 else float("nan")
    bc_gini = gini(bcv)
    q2_hub = bool(bc_top1_share >= HUB_BETW_TOP1PCT_SHARE)
    print("[Q2 BETW] top1%%share=%.3f (uniform~0.01) top5%%share=%.3f gini=%.3f | betw_concentrated=%s"
          % (bc_top1_share, bc_top5_share, bc_gini, q2_hub), flush=True)
    # clustering (hub-and-spoke tends higher local clustering than a random expander of same degree)
    avg_clust = float(nx.average_clustering(G))
    print("[Q2 BETW] avg_clustering=%.4f" % avg_clust, flush=True)

    # ---- Q3 nearest-landmark hop distance ----
    # actual path-node population = nodes visited by sampled traversal chains
    rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 909)
    g_start, g_tgt, g_role = sample_chains(dir_adj, N_CHAINS_SAMPLE, MAX_REACH, rng)
    path_nodes = set(int(x) for x in g_start.tolist())
    for h in range(MAX_REACH):
        path_nodes.update(int(x) for x in g_tgt[h].tolist())
    path_nodes = np.array(sorted(path_nodes), dtype=np.int64)
    print("\n[Q3 LANDMARK] sampled %d chains -> %d distinct path nodes" % (len(g_start), path_nodes.shape[0]), flush=True)

    deg_lm_by_k = {}
    betw_lm_by_k = {}
    for K in LANDMARK_KS:
        lm_deg = order[:K].tolist()
        lm_betw = bc_order[:K].tolist()
        for tag, lm in (("degree", lm_deg), ("betweenness", lm_betw)):
            dist = multi_source_bfs_dist(adj, lm, n)
            d_path = dist[path_nodes]
            reachable = d_path >= 0
            d_ok = d_path[reachable]
            med = float(np.median(d_ok)) if d_ok.size else float("nan")
            within0 = float((d_ok == 0).mean()) if d_ok.size else float("nan")  # node IS a landmark
            within1 = float((d_ok <= 1).mean()) if d_ok.size else float("nan")
            within2 = float((d_ok <= 2).mean()) if d_ok.size else float("nan")
            rec = dict(K=K, median_hop=med, frac_within0=within0, frac_within1=within1,
                       frac_within2=within2, frac_unreachable=float((~reachable).mean()),
                       max_hop=int(d_ok.max()) if d_ok.size else -1)
            (deg_lm_by_k if tag == "degree" else betw_lm_by_k)[K] = rec
            print("[Q3 %s] K=%3d median_hop=%.2f within0=%.3f within1=%.3f within2=%.3f unreach=%.3f maxhop=%d"
                  % (tag[:4].upper(), K, med, within0, within1, within2, rec["frac_unreachable"], rec["max_hop"]),
                  flush=True)

    # gate evaluated at LM_K_FOR_GATE using the BETTER of degree/betweenness selection
    gate_deg = deg_lm_by_k[LM_K_FOR_GATE]
    gate_betw = betw_lm_by_k[LM_K_FOR_GATE]
    best = gate_deg if gate_deg["frac_within1"] >= gate_betw["frac_within1"] else gate_betw
    q3_reachable = bool(best["median_hop"] <= LM_MEDIAN_HOP_MAX and best["frac_within1"] >= LM_WITHIN1_FRAC_MIN)

    # ---- DECISION GATE ----
    hub_structure = bool(q1_hub and q2_hub)
    proceed = bool(hub_structure and q3_reachable)
    decision = "PROCEED_PHASE1" if proceed else "STOP_LANDMARKS_VACUOUS"

    print("\n" + "=" * 78, flush=True)
    print("[DECISION] hub_by_degree=%s betw_concentrated=%s => hub_structure=%s" % (q1_hub, q2_hub, hub_structure),
          flush=True)
    print("[DECISION] landmarks ~1-hop (K=%d, best sel): median_hop=%.2f within1=%.3f => reachable=%s"
          % (LM_K_FOR_GATE, best["median_hop"], best["frac_within1"], q3_reachable), flush=True)
    print("[DECISION] ==> %s" % decision, flush=True)
    print("=" * 78, flush=True)

    out = dict(
        n_nodes=n, n_edges=G.number_of_edges(), rel_types=T,
        q1_degree=dict(mean=mean_d, median=median_d, max=max_d, max_over_mean=max_d / mean_d,
                       gini=deg_gini, top1pct_share=top1pct_share, top5pct_share=top5pct_share,
                       frac_ge_5x_mean=frac_ge_5x_mean, hub_by_degree=q1_hub),
        q2_betweenness=dict(pivots=kpiv, top1pct_share=bc_top1_share, top5pct_share=bc_top5_share,
                            gini=bc_gini, avg_clustering=avg_clust, betw_concentrated=q2_hub),
        q3_landmark=dict(n_path_nodes=int(path_nodes.shape[0]), gate_K=LM_K_FOR_GATE,
                         degree_selection=deg_lm_by_k, betweenness_selection=betw_lm_by_k,
                         gate_best=best, reachable=q3_reachable),
        thresholds=dict(HUB_MAXdeg_over_MEAN=HUB_MAXdeg_over_MEAN, HUB_TOP5PCT_SHARE=HUB_TOP5PCT_SHARE,
                        HUB_BETW_TOP1PCT_SHARE=HUB_BETW_TOP1PCT_SHARE, LM_K_FOR_GATE=LM_K_FOR_GATE,
                        LM_MEDIAN_HOP_MAX=LM_MEDIAN_HOP_MAX, LM_WITHIN1_FRAC_MIN=LM_WITHIN1_FRAC_MIN),
        hub_structure=hub_structure, landmarks_1hop_reachable=q3_reachable, decision=decision,
    )
    op = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phase0_result.json")
    with open(op, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("[phase0] wrote %s" % op, flush=True)


if __name__ == "__main__":
    main()
