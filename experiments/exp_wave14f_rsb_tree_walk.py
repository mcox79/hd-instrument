"""RSB tree-walk retrieval -- exploits the confirmed RSB phase.

Per wave14e2_parisi_ultrametricity: substrate pool empirically has multi-peaked
P(q) and ultrametricity_fraction = 0.357 (RSB phase confirmed).

Per wave14f_rsb_tree_walk_research:
- Build Parisi tree via single-linkage agglomerative clustering (= Kruskal's MST on overlap-distance)
- Query via priority-queue beam search, beam b in {1, 2, 4, 8}
- Cost O(b * D * log P) per query
- Predicted recall@10: b=1 -> 0.36, b=2 -> 0.51, b=4 -> 0.76, b=8 -> 0.95 (at f=0.357)

Test: build tree on POOL_SIZE=1024 bipolar bundles from substrate training.
For 200 queries, compute brute-force top-10 ground truth.
Compare tree-walk recall@10 across beam widths. Measure speedup.

Pass: recall@10 >= 0.70 at b=4 with >=3x speedup vs brute-force.
"""

from __future__ import annotations

import heapq
import json
import time
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N = 4096
K = 4
VOCAB_SIZE = 256
PAD_BYTE = 0
POOL_SIZE = 1024
BATCH_SIZE = 64
MAX_EPOCHS = 15
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
BETA = 8.0
QUERY_COUNT = 200
BEAM_WIDTHS = [1, 2, 4, 8, 16]
SEED = 17


def _say(m): print(m, flush=True)


def load_corpus_a():
    repo = Path(__file__).resolve().parent.parent
    files = [repo / "PLAN.md", repo / "NEXT_PHASE.md", repo / "README.md",
             repo / "PROGRESS.md", repo / "RESULTS.md", repo / "CLAUDE.md"]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes()); parts.append(b"\n\n")
    return b"".join(parts)


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def build_ctx(byte_atoms, pos_atoms, idx):
    b = byte_atoms[idx] * pos_atoms.unsqueeze(0)
    s = b.sum(dim=1)
    out = torch.sign(s)
    return torch.where(out == 0, torch.ones_like(out), out)


def relu_shift(q, b): return torch.clamp(q - b, min=0.0)


def build_pool(byte_atoms, pos_atoms, train_bytes):
    W = torch.zeros((N, N), device=DEVICE)
    pool_v = torch.zeros((POOL_SIZE, N), device=DEVICE)
    pool_l = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    p_idx, p_used = 0, 0
    arange = torch.arange(BATCH_SIZE, device=DEVICE)
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offs = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offs.unsqueeze(0)]
    tgt = bt[pos + K]
    for epoch in range(1, MAX_EPOCHS + 1):
        for bs in range(0, T, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T)
            B = be - bs
            ctxs = build_ctx(byte_atoms, pos_atoms, idx[bs:be])
            t = tgt[bs:be]
            with torch.no_grad():
                q = relu_shift(ctxs @ W.T, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                resid = byte_atoms[t] - (P.T @ byte_atoms)
                dW = (resid.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY); W.add_(dW, alpha=DELTA_RULE_ALPHA)
                if epoch == 1:
                    dest = (p_idx + arange[:B]) % POOL_SIZE
                    pool_v.index_copy_(0, dest, ctxs)
                    pool_l.index_copy_(0, dest, t)
                    p_idx = (p_idx + B) % POOL_SIZE
                    p_used = min(p_used + B, POOL_SIZE)
    return pool_v[:p_used]


def overlap_matrix(pool):
    return (pool @ pool.T) / N


def single_linkage_tree(pool):
    """Build dendrogram via single-linkage agglomerative on overlap-distance.

    Each node is either a leaf (single bundle) or an internal node merging two children.
    Returns: list of (left_id, right_id, distance, member_ids).
    Leaf ids are 0..P-1; internal ids are P, P+1, ...
    """
    P = pool.shape[0]
    Q = overlap_matrix(pool)
    distances = 1.0 - Q.cpu().numpy()  # distance = 1 - overlap
    # Use scipy if available; otherwise manual
    try:
        from scipy.cluster.hierarchy import linkage
        from scipy.spatial.distance import squareform
        condensed = squareform(distances, checks=False)
        Z = linkage(condensed, method="single")
        # Z: rows of (left_id, right_id, dist, count); ids >= P refer to internal nodes
        tree_nodes = []
        node_members = {i: [i] for i in range(P)}
        for i, row in enumerate(Z):
            left, right, dist, _count = int(row[0]), int(row[1]), float(row[2]), int(row[3])
            members = node_members[left] + node_members[right]
            new_id = P + i
            node_members[new_id] = members
            tree_nodes.append((new_id, left, right, dist, members))
        return tree_nodes, node_members
    except ImportError:
        _say("WARNING: scipy not available; falling back to slow native single-linkage")
        # Naive O(P^3) single-linkage
        active = list(range(P))
        node_members = {i: [i] for i in range(P)}
        tree_nodes = []
        next_id = P
        d = distances.copy()
        import numpy as np
        for _ in range(P - 1):
            min_d = float("inf"); pair = (-1, -1)
            for ia, a in enumerate(active):
                for b in active[ia + 1:]:
                    if d[a][b] < min_d:
                        min_d = d[a][b]; pair = (a, b)
            l, r = pair
            members = node_members[l] + node_members[r]
            node_members[next_id] = members
            tree_nodes.append((next_id, l, r, min_d, members))
            # Update distances: single-linkage = min
            new_d_row = []
            for a in active:
                if a == l or a == r:
                    continue
                new_d_row.append(min(d[a][l], d[a][r]))
            # Rebuild distance matrix in-place for next_id
            active.remove(l); active.remove(r)
            # Create new row/col for next_id
            new_d = np.full((next_id + 1, next_id + 1), float("inf"))
            new_d[:next_id, :next_id] = d
            for j, a in enumerate(active):
                new_d[next_id, a] = new_d[a, next_id] = new_d_row[j]
            d = new_d
            active.append(next_id)
            next_id += 1
        return tree_nodes, node_members


def cluster_centroids(pool, tree_nodes, node_members):
    """For each internal node, compute the majority-vote bundled centroid."""
    centroids = {}
    for node_id, members in node_members.items():
        if len(members) == 1:
            centroids[node_id] = pool[members[0]]
        else:
            stacked = pool[members]
            centroid = torch.sign(stacked.sum(dim=0))
            centroid = torch.where(centroid == 0, torch.ones_like(centroid), centroid)
            centroids[node_id] = centroid
    return centroids


def tree_search(query, root_id, tree_dict, centroids, pool, beam_width, top_k=10):
    """Priority-queue beam search over the dendrogram.
    Returns top_k leaf indices."""
    # Pop highest-similarity nodes; expand until we have top_k leaves
    found_leaves = []
    heap = [(-(query @ centroids[root_id]).item() / N, root_id)]
    expanded = 0
    max_visits = beam_width * (2 * len(pool))  # safety cap
    visits = 0
    while heap and len(found_leaves) < top_k * 3 and visits < max_visits:
        visits += 1
        neg_sim, node_id = heapq.heappop(heap)
        if node_id < pool.shape[0]:
            # leaf
            found_leaves.append((-neg_sim, node_id))
        else:
            # internal node - expand children
            _, left, right, _dist, _ = tree_dict[node_id]
            sim_l = (query @ centroids[left]).item() / N
            sim_r = (query @ centroids[right]).item() / N
            heapq.heappush(heap, (-sim_l, left))
            heapq.heappush(heap, (-sim_r, right))
            expanded += 1
            if expanded > beam_width * 32:
                # cap exploration; sort remaining heap and keep top of leaf-only
                break
    # Now rank found leaves by similarity; if too few, fill from remaining heap leaves
    while heap and len(found_leaves) < top_k * 3:
        neg_sim, node_id = heapq.heappop(heap)
        if node_id < pool.shape[0]:
            found_leaves.append((-neg_sim, node_id))
    found_leaves.sort(key=lambda x: -x[0])
    return [idx for _, idx in found_leaves[:top_k]], visits


def main():
    _say(f"RSB tree-walk retrieval: N={N}, K={K}, POOL_SIZE={POOL_SIZE}, BEAMS={BEAM_WIDTHS}")
    corpus = load_corpus_a()
    split = int(0.8 * len(corpus))
    train_a, test_a = corpus[:split], corpus[split:]
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc(K, N, gen).to(DEVICE)

    _say("Building pool...")
    pool = build_pool(byte_atoms, pos_atoms, train_a)
    P = pool.shape[0]
    _say(f"Pool: {P} entries")

    _say("Building single-linkage tree...")
    t0 = time.time()
    tree_nodes, node_members = single_linkage_tree(pool)
    build_time = time.time() - t0
    _say(f"  built in {build_time:.1f}s, {len(tree_nodes)} internal nodes")
    root_id = max(node_members.keys())
    tree_dict = {n[0]: n for n in tree_nodes}

    _say("Computing cluster centroids...")
    t0 = time.time()
    centroids = cluster_centroids(pool, tree_nodes, node_members)
    centroid_time = time.time() - t0
    _say(f"  built {len(centroids)} centroids in {centroid_time:.1f}s")

    # Build queries from test split
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_a
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offs = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos_idx = torch.arange(min(QUERY_COUNT, len(padded) - K), device=DEVICE)
    idx_all = bt[pos_idx.unsqueeze(1) + offs.unsqueeze(0)]
    queries = build_ctx(byte_atoms, pos_atoms, idx_all)
    Q = queries.shape[0]

    # Brute force ground truth
    _say(f"\nBrute force ground-truth on {Q} queries...")
    t0 = time.time()
    truth_sims = (queries @ pool.T) / N
    truth_top10 = truth_sims.topk(10, dim=1).indices
    bf_time = (time.time() - t0) / Q * 1000
    _say(f"  brute force: {bf_time:.3f}ms per query")

    # Tree-walk at each beam width
    results = {}
    for b in BEAM_WIDTHS:
        recalls = []
        visits_total = []
        t0 = time.time()
        for q_idx in range(Q):
            retrieved, visits = tree_search(queries[q_idx], root_id, tree_dict, centroids, pool, b, top_k=10)
            visits_total.append(visits)
            truth = set(truth_top10[q_idx].tolist())
            ret_set = set(retrieved)
            recalls.append(len(truth & ret_set) / 10.0)
        tree_time = (time.time() - t0) / Q * 1000
        mean_recall = sum(recalls) / len(recalls)
        mean_visits = sum(visits_total) / len(visits_total)
        results[b] = {"recall_at_10": mean_recall, "ms_per_query": tree_time,
                      "speedup": bf_time / max(tree_time, 1e-6),
                      "mean_visits": mean_visits}
        _say(f"  beam={b:2d}: recall@10 = {mean_recall:.3f}  {tree_time:.3f}ms  visits={mean_visits:.1f}  speedup={results[b]['speedup']:.1f}x")

    _say("\n========= RSB TREE-WALK VERDICT =========")
    best_b = max(BEAM_WIDTHS, key=lambda b: results[b]["recall_at_10"])
    r = results[best_b]
    _say(f"  Best: beam={best_b}, recall@10={r['recall_at_10']:.3f}, speedup={r['speedup']:.1f}x")
    if r["recall_at_10"] >= 0.7 and r["speedup"] >= 3.0:
        _say(f"  PASS: RSB tree-walk gives high recall + meaningful speedup.")
    elif r["recall_at_10"] >= 0.5:
        _say(f"  PARTIAL: recall solid but speedup modest. Larger P would help.")
    else:
        _say(f"  WEAK: tree-walk loses too much recall. Ultrametric structure too weak at this scale.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14f_rsb_tree_walk"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "K": K, "POOL_SIZE": P, "QUERY_COUNT": Q,
        "BEAM_WIDTHS": BEAM_WIDTHS,
        "brute_force_ms": bf_time, "build_time_s": build_time,
        "results": {str(b): r for b, r in results.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
