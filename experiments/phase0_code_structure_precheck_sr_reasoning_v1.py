"""PHASE-0 CODE-STRUCTURE PRE-CHECK + SIZE-AXIS (zero-cost gate for the learned-SR reasoning cell).

QUESTION (Anchor-0 from notes/research_learned_partial_graph_SR_reasoning_vs_search_CG_path_2026-07-09.md):
does the substrate's LEARNED code space carry graph structure? If code-space cosine similarity meaningfully tracks
graph proximity (hop-distance / 1-hop reachability), then a code-space-smoothed learned SR CAN generalize to held-out
structure (PROCEED to Phase 1). If codes are structure-blind (cosine ~ uncorrelated with hop-distance), then
code-space smoothing degenerates to noise and the held-out reasoning cell would collapse regardless of mechanism
quality -> STOP; report "learned codes do not carry graph structure yet" (a real finding: encoder must learn structure).

SIZE AXIS (Director + USER hypothesis): is the substrate too SMALL (too little graph structure to LEARN a
generalizing map) vs the mechanism being wrong? Run the code-structure + held-out-generalization probe at 3 graph
SIZES. If held-out generalization (M5) IMPROVES with a larger/denser graph -> "too little structure to learn from"
(scale-of-experience) is a real factor. If M5 is FLAT across sizes -> the blocker is the mechanism/encoder (codes
map-blind / raw memorization), not size.

This is a DIAGNOSTIC pre-check, not a verdict cell. Single seed per size, moderate scale, CPU. Reuses the SAME
encoder / subgraph primitives as the SR-routing cell VERBATIM so the codes measured are the ones the real cell uses.

METRICS per size (all on the L2-normalized learned codes Z):
  M1 mean code-cosine per undirected hop-distance bucket (1,2,3,4,5,6+); monotonic DECREASE with hop = structure.
  M2 Spearman rho(cosine, hop-distance) over sampled pairs (expect NEGATIVE if codes track proximity).
  M3 1-hop-edge detection AUC: does cosine rank true 1-hop edges above far (hop>=3) non-edges? (> 0.5 = above chance)
  M4 code-kNN graph-proximity: for query nodes, mean undirected hop-distance of the top-K code-cosine neighbors vs K
     RANDOM nodes. THE mechanistically-relevant metric for Phase-1 code-space smoothing (Phase 1 estimates
     M_hat[v,G] as a code-kNN-weighted average of M[u,G]). code-kNN mean-hop << random = code neighbors ARE graph-near.
  M5 HELD-OUT leakage-safe probe (DECISIVE + the size-axis metric): withhold a random fraction of edges from encoder
     TRAINING, then among WITHHELD 1-hop edges (unseen by the encoder), is code-cosine still elevated vs far non-edges
     (AUC)? Tests whether the code space generalizes proximity to pairs whose connecting edge it never saw (= what
     Phase-1's held-out subgraph test needs). Guards against a falsely-optimistic PROCEED driven by memorized edges.

PRE-REGISTERED DECISION GATE (picked BEFORE the run; evaluated on the LARGEST size = "would more graph help"):
  PROCEED  if M3(full) >= 0.65 AND M1 strictly decreases over hops 1->2->3 AND M4 ratio <= 0.70 AND M5 >= 0.60.
  STOP     if M3(full) <= 0.55 OR (M1 non-monotonic AND M4 ratio >= 0.90) OR M5 <= 0.55.
  MIDDLE   otherwise -> report + judgment (lean STOP if M5 weak; held-out is load-bearing).
  SIZE VERDICT: M5(largest) - M5(smallest) >= 0.05 (and non-decreasing) -> "size_helps" (scale-of-experience real);
                |delta| < 0.05 -> "size_flat" (mechanism/encoder-bound, not size).

ASCII-only, device-aware (cpu here). Diagnostic script; prints a JSON blob + writes data/phase0_*_result.json.
"""

import json
import os
import sys
import time

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import char_trigram_features  # noqa: E402
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import SUBGRAPH_BASE_SEED  # noqa: E402
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph, make_unitary_roles,
)
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import (  # noqa: E402
    train_binding_encoder_dev,
)

# SIZE AXIS: target node counts. small / current(~SR-FULL=5000->~4440) / substantially-larger.
SIZE_TARGETS = [1500, 5000, 9000]
BASE_CFG = dict(epochs=80, batch=256, code_dim=512, feat_dim=4096,
                temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0)
SEED = 7
HELDOUT_FRAC = 0.30
KNN_K = 8
MAX_HOP = 6
RNG = np.random.default_rng(20260709)


def _log(m):
    print("[phase0] %s" % m, flush=True)


def build_undirected_adj(edges, n_nodes):
    adj = [[] for _ in range(n_nodes)]
    eset = set()
    for (a, b) in edges:
        a = int(a); b = int(b)
        if a == b:
            continue
        adj[a].append(b)
        adj[b].append(a)
        eset.add((a, b) if a < b else (b, a))
    return adj, eset


def bfs_hops(adj, src, max_hop):
    dist = {src: 0}
    frontier = [src]
    for h in range(1, max_hop + 1):
        nxt = []
        for u in frontier:
            for v in adj[u]:
                if v not in dist:
                    dist[v] = h
                    nxt.append(v)
        frontier = nxt
        if not frontier:
            break
    dist.pop(src, None)
    return dist


def spearman(x, y):
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    rx = np.argsort(np.argsort(x)).astype(np.float64)
    ry = np.argsort(np.argsort(y)).astype(np.float64)
    rx -= rx.mean(); ry -= ry.mean()
    den = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    return float((rx * ry).sum() / den) if den > 0 else float("nan")


def auc_pos_neg(pos_scores, neg_scores):
    pos = np.asarray(pos_scores, dtype=np.float64)
    neg = np.asarray(neg_scores, dtype=np.float64)
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    allv = np.concatenate([pos, neg])
    ranks = np.argsort(np.argsort(allv)).astype(np.float64) + 1.0
    r_pos = ranks[:len(pos)].sum()
    n1 = len(pos); n2 = len(neg)
    u = r_pos - n1 * (n1 + 1) / 2.0
    return float(u / (n1 * n2))


def train_codes(node_words, edges, rels, roles_t, cfg, seed, device):
    X = char_trigram_features(node_words, cfg["feat_dim"])
    Z = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=None, tag="phase0")
    return torch.nn.functional.normalize(Z.to(torch.float32), dim=1)


def sample_far_negatives(n_need, n_nodes, eset, adj_sets):
    """far negatives: random pairs, not an edge, not sharing a neighbor (hop>=3)."""
    neg = []
    tries = 0
    cap = max(n_need * 40, 10000)
    while len(neg) < n_need and tries < cap:
        tries += 1
        u = int(RNG.integers(0, n_nodes)); v = int(RNG.integers(0, n_nodes))
        if u == v:
            continue
        key = (u, v) if u < v else (v, u)
        if key in eset:
            continue
        if adj_sets[u] & adj_sets[v]:
            continue
        neg.append((u, v))
    return neg


def run_size(n_target, device):
    t0 = time.perf_counter()
    cfg = dict(BASE_CFG)
    _log("=== SIZE target n=%d : loading subgraph ===" % n_target)
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        n_target, SUBGRAPH_BASE_SEED)
    n_nodes = len(node_ids)
    edges = np.asarray(edges, dtype=np.int64)
    rels = np.asarray(rels)
    _log("subgraph n_nodes=%d n_edges=%d rel_types=%d median_degree=%s"
         % (n_nodes, edges.shape[0], T, meta.get("median_degree")))

    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_t = torch.from_numpy(make_unitary_roles(T, cfg["code_dim"], role_rng)).to(device)
    adj, eset = build_undirected_adj(edges, n_nodes)
    adj_sets = [set(a) for a in adj]

    _log("training FULL encoder (all edges) ...")
    Zn = train_codes(node_words, edges, rels, roles_t, cfg, SEED, device)

    deg = np.array([len(adj[u]) for u in range(n_nodes)])
    srcs_all = np.where(deg > 0)[0]
    n_src = min(300, len(srcs_all))
    bfs_srcs = RNG.choice(srcs_all, size=n_src, replace=False)

    # M1 + M2
    bucket_cos = {h: [] for h in range(1, MAX_HOP + 1)}
    pair_cos, pair_hop = [], []
    per_pair_cap = 40
    for s in bfs_srcs:
        dist = bfs_hops(adj, int(s), MAX_HOP)
        if not dist:
            continue
        items = list(dist.items())
        if len(items) > per_pair_cap:
            sel = RNG.choice(len(items), size=per_pair_cap, replace=False)
            items = [items[i] for i in sel]
        zs = Zn[int(s)]
        for (v, h) in items:
            c = float(torch.dot(zs, Zn[v]).item())
            bucket_cos[h].append(c); pair_cos.append(c); pair_hop.append(h)
    m1 = {h: (float(np.mean(bucket_cos[h])) if bucket_cos[h] else float("nan"),
              len(bucket_cos[h])) for h in range(1, MAX_HOP + 1)}
    m2 = spearman(pair_cos, pair_hop)

    # M3 full 1-hop AUC
    n_es = min(3000, edges.shape[0])
    esel = RNG.choice(edges.shape[0], size=n_es, replace=False)
    pos_full = [float(torch.dot(Zn[int(edges[i, 0])], Zn[int(edges[i, 1])]).item()) for i in esel]
    neg_pairs = sample_far_negatives(n_es, n_nodes, eset, adj_sets)
    neg_full = [float(torch.dot(Zn[u], Zn[v]).item()) for (u, v) in neg_pairs]
    m3 = auc_pos_neg(pos_full, neg_full)

    # M4 code-kNN graph proximity
    q_nodes = RNG.choice(srcs_all, size=min(250, len(srcs_all)), replace=False)
    knn_hops, rand_hops = [], []
    BIG = MAX_HOP + 2
    for q in q_nodes:
        q = int(q)
        sims = torch.mv(Zn, Zn[q]); sims[q] = -1e9
        topk = torch.topk(sims, KNN_K).indices.cpu().numpy().tolist()
        dist = bfs_hops(adj, q, MAX_HOP)
        for v in topk:
            knn_hops.append(dist.get(int(v), BIG))
        rnd = RNG.choice(n_nodes, size=KNN_K, replace=False)
        for v in rnd:
            if int(v) != q:
                rand_hops.append(dist.get(int(v), BIG))
    m4_knn = float(np.mean(knn_hops)) if knn_hops else float("nan")
    m4_rand = float(np.mean(rand_hops)) if rand_hops else float("nan")
    m4_ratio = (m4_knn / m4_rand) if m4_rand > 0 else float("nan")
    m4_knn_le2 = float(np.mean([1.0 if h <= 2 else 0.0 for h in knn_hops])) if knn_hops else float("nan")
    m4_rand_le2 = float(np.mean([1.0 if h <= 2 else 0.0 for h in rand_hops])) if rand_hops else float("nan")

    # M5 held-out
    _log("training HELD-OUT encoder (%.0f%% edges withheld) ..." % (HELDOUT_FRAC * 100))
    n_e = edges.shape[0]
    perm = RNG.permutation(n_e)
    n_hold = int(HELDOUT_FRAC * n_e)
    hold_idx, keep_idx = perm[:n_hold], perm[n_hold:]
    Zhn = train_codes(node_words, edges[keep_idx], rels[keep_idx], roles_t, cfg, SEED, device)
    hsel = hold_idx if n_hold <= 3000 else RNG.choice(hold_idx, size=3000, replace=False)
    pos_h = [float(torch.dot(Zhn[int(edges[i, 0])], Zhn[int(edges[i, 1])]).item()) for i in hsel]
    neg_h_pairs = sample_far_negatives(len(pos_h), n_nodes, eset, adj_sets)
    neg_h = [float(torch.dot(Zhn[u], Zhn[v]).item()) for (u, v) in neg_h_pairs]
    m5 = auc_pos_neg(pos_h, neg_h)
    ksel = keep_idx if len(keep_idx) <= 3000 else RNG.choice(keep_idx, size=3000, replace=False)
    pos_seen = [float(torch.dot(Zhn[int(edges[i, 0])], Zhn[int(edges[i, 1])]).item()) for i in ksel]
    m5_seen = auc_pos_neg(pos_seen, neg_h)

    m1_mono = bool(m1[1][0] == m1[1][0] and m1[2][0] == m1[2][0] and m1[3][0] == m1[3][0]
                   and m1[1][0] > m1[2][0] > m1[3][0])
    res = dict(
        n_target=n_target, n_nodes=n_nodes, n_edges=int(edges.shape[0]), rel_types=int(T),
        mean_degree=float(2.0 * edges.shape[0] / max(n_nodes, 1)),
        M1_mean_cosine_per_hop={h: m1[h][0] for h in range(1, MAX_HOP + 1)},
        M1_counts_per_hop={h: m1[h][1] for h in range(1, MAX_HOP + 1)},
        M1_monotonic_123=m1_mono,
        M2_spearman=m2,
        M3_1hop_auc_full=m3,
        M4_codeknn_meanhop=m4_knn, M4_random_meanhop=m4_rand, M4_ratio=m4_ratio,
        M4_codeknn_frac_le2=m4_knn_le2, M4_random_frac_le2=m4_rand_le2,
        M5_heldout_auc=m5, M5_seen_auc_heldout_encoder=m5_seen, M5_heldout_frac=HELDOUT_FRAC,
        elapsed_s=round(time.perf_counter() - t0, 1),
    )
    _log("size n=%d DONE: M3=%.3f M4ratio=%.3f M5heldout=%.3f (seen=%.3f) mono123=%s (%.1fs)"
         % (n_nodes, m3, m4_ratio, m5, m5_seen, m1_mono, res["elapsed_s"]))
    return res


def main():
    device = torch.device("cpu")
    t0 = time.perf_counter()
    per_size = []
    for nt in SIZE_TARGETS:
        try:
            per_size.append(run_size(nt, device))
        except Exception as e:
            _log("SIZE n=%d FAILED %s: %s" % (nt, type(e).__name__, str(e)[:200]))
            per_size.append(dict(n_target=nt, error="%s: %s" % (type(e).__name__, str(e)[:200])))

    ok_sizes = [r for r in per_size if "error" not in r]
    ok_sizes = sorted(ok_sizes, key=lambda r: r["n_nodes"])
    decision = "NO_VALID_SIZES"
    size_verdict = "n/a"
    if ok_sizes:
        big = ok_sizes[-1]
        proceed = bool(big["M3_1hop_auc_full"] >= 0.65 and big["M1_monotonic_123"]
                       and (big["M4_ratio"] == big["M4_ratio"] and big["M4_ratio"] <= 0.70)
                       and big["M5_heldout_auc"] >= 0.60)
        stop = bool(big["M3_1hop_auc_full"] <= 0.55
                    or ((not big["M1_monotonic_123"]) and (big["M4_ratio"] == big["M4_ratio"]
                                                           and big["M4_ratio"] >= 0.90))
                    or big["M5_heldout_auc"] <= 0.55)
        decision = "PROCEED" if (proceed and not stop) else ("STOP" if (stop and not proceed) else "MIDDLE_JUDGMENT")
        if len(ok_sizes) >= 2:
            d = ok_sizes[-1]["M5_heldout_auc"] - ok_sizes[0]["M5_heldout_auc"]
            m5s = [r["M5_heldout_auc"] for r in ok_sizes]
            nondec = all(m5s[i + 1] >= m5s[i] - 0.02 for i in range(len(m5s) - 1))
            size_verdict = ("size_helps" if (d >= 0.05 and nondec) else "size_flat")
            size_verdict += " (deltaM5=%.3f across n=%d->%d)" % (d, ok_sizes[0]["n_nodes"], ok_sizes[-1]["n_nodes"])

    out = dict(size_targets=SIZE_TARGETS, base_cfg=BASE_CFG, seed=SEED, heldout_frac=HELDOUT_FRAC,
               per_size=per_size, DECISION=decision, SIZE_VERDICT=size_verdict,
               total_elapsed_s=round(time.perf_counter() - t0, 1))
    _log("RESULT JSON:")
    print(json.dumps(out, indent=2), flush=True)
    dump = os.path.join(_REPO, "data", "phase0_code_structure_precheck_result.json")
    os.makedirs(os.path.dirname(dump), exist_ok=True)
    with open(dump, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    _log("wrote %s" % dump)
    _log("DECISION=%s | SIZE_VERDICT=%s | total=%.1fs" % (decision, size_verdict, time.perf_counter() - t0))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    main()
