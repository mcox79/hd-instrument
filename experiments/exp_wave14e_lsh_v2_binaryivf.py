"""LSH v2 -- BinaryIVF (inverted-list partitioning with Hamming-centroid k-means).

Per wave14e_lsh_for_bsc_research: at our target similarity (s in [0.1, 0.3] which
maps to Hamming radius d_H/N in [0.35, 0.45]) we're in the HIGH-RADIUS regime where
classical LSH (SimHash, MIH) degrades. BinaryIVF exploits actual pool clustering
induced by sum-bundle key-sharing structure.

Minimal viable BinaryIVF in pure PyTorch:
- Train k-means in Hamming space (median-based centroids for bipolar).
- Assign each pool entry to its nearest centroid (Voronoi partition).
- Query: find top-K nearest centroids, search only those Voronoi cells.

Test on P=10K pool with near-queries (10% bit flip). Measure recall@10 vs brute force.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N = 4096
POOL_SIZE = 10000
QUERY_COUNT = 1000
NEAR_FLIP_RATE = 0.10
NUM_CENTROIDS = 100  # IVF nlist
KMEANS_ITERS = 10
NUM_CENTROIDS_PROBE = 5  # nprobe (search only top-nprobe Voronoi cells)
SEED = 17


def _say(m): print(m, flush=True)


def make_bsc(p, n, gen):
    return 2.0 * (torch.rand((p, n), generator=gen) > 0.5).float() - 1.0


def make_near_queries(pool, num, flip_rate, gen):
    src_idx = torch.randint(0, pool.shape[0], (num,), generator=gen).tolist()
    queries = pool[src_idx].clone()
    n_flip = int(N * flip_rate)
    for q in range(num):
        flip_positions = torch.randperm(N, generator=gen)[:n_flip]
        queries[q, flip_positions] *= -1
    return queries.to(DEVICE), src_idx


def kmeans_bipolar(pool, num_centroids, iters, gen):
    """k-means in Hamming/bipolar space. Centroids are bipolar (sign-quantized mean)."""
    P, _ = pool.shape
    init = torch.randperm(P, generator=gen)[:num_centroids]
    centroids = pool[init].clone()
    for it in range(iters):
        # Assign each point to nearest centroid (max dot-product)
        sims = pool @ centroids.T / N  # (P, k)
        assignments = sims.argmax(dim=1)
        # Recompute centroids: per cluster, sign(mean)
        new_centroids = torch.zeros_like(centroids)
        for c in range(num_centroids):
            mask = assignments == c
            if mask.any():
                mean = pool[mask].mean(dim=0)
                new_c = torch.sign(mean)
                new_c = torch.where(new_c == 0, torch.ones_like(new_c), new_c)
                new_centroids[c] = new_c
            else:
                new_centroids[c] = centroids[c]  # keep
        # Check convergence
        delta = (new_centroids != centroids).float().mean().item()
        centroids = new_centroids
        if delta < 0.001:
            break
    # Final assignment
    sims = pool @ centroids.T / N
    assignments = sims.argmax(dim=1)
    return centroids, assignments


def brute_force_topk(pool, queries, k=10):
    sims = (queries @ pool.T) / N
    return sims.topk(k, dim=1).indices


def ivf_query(query, centroids, assignments, pool, nprobe, k=10):
    """Search only top-nprobe Voronoi cells."""
    sims_c = centroids @ query / N
    top_cells = sims_c.topk(nprobe).indices
    candidate_mask = torch.zeros(pool.shape[0], dtype=torch.bool, device=DEVICE)
    for c in top_cells:
        candidate_mask |= (assignments == c)
    if not candidate_mask.any():
        return torch.tensor([], dtype=torch.long, device=DEVICE)
    candidates = torch.nonzero(candidate_mask).squeeze(1)
    sims = pool[candidates] @ query / N
    top = sims.topk(min(k, len(candidates))).indices
    return candidates[top]


def main():
    _say(f"LSH v2 (BinaryIVF): N={N}, P={POOL_SIZE}, Q={QUERY_COUNT}, nlist={NUM_CENTROIDS}, nprobe={NUM_CENTROIDS_PROBE}")
    gen = torch.Generator().manual_seed(SEED)
    pool = make_bsc(POOL_SIZE, N, gen).to(DEVICE)
    queries, _ = make_near_queries(pool, QUERY_COUNT, NEAR_FLIP_RATE, gen)

    # Brute force ground truth
    t0 = time.time()
    truth_top10 = brute_force_topk(pool, queries, k=10)
    bf_time = (time.time() - t0) / QUERY_COUNT * 1000
    _say(f"  Brute force: {bf_time:.3f}ms per query")

    # Build IVF index
    t0 = time.time()
    centroids, assignments = kmeans_bipolar(pool, NUM_CENTROIDS, KMEANS_ITERS, gen)
    build_time = time.time() - t0
    cluster_sizes = [int((assignments == c).sum().item()) for c in range(NUM_CENTROIDS)]
    _say(f"  IVF build: {build_time:.2f}s, cluster sizes min/max/mean: {min(cluster_sizes)}/{max(cluster_sizes)}/{sum(cluster_sizes)/NUM_CENTROIDS:.0f}")

    # IVF query
    t0 = time.time()
    ivf_results = [ivf_query(queries[q], centroids, assignments, pool, NUM_CENTROIDS_PROBE, k=10) for q in range(QUERY_COUNT)]
    ivf_time = (time.time() - t0) / QUERY_COUNT * 1000
    _say(f"  IVF query: {ivf_time:.3f}ms per query  speedup={bf_time/max(ivf_time,1e-6):.1f}x")

    # Recall@10
    recalls = []
    for q in range(QUERY_COUNT):
        truth = set(truth_top10[q].tolist())
        retrieved = set(ivf_results[q].tolist())
        if truth:
            recalls.append(len(truth & retrieved) / len(truth))
    mean_recall = sum(recalls) / len(recalls)
    _say(f"\n  Recall@10: {mean_recall:.3f}")

    if mean_recall >= 0.9 and bf_time/max(ivf_time, 1e-6) >= 5:
        _say(f"\n  PASS: BinaryIVF gives high recall + meaningful speedup at P=10K.")
    elif mean_recall >= 0.7:
        _say(f"\n  PARTIAL: recall solid but speedup small. Tune nlist/nprobe.")
    else:
        _say(f"\n  WEAK: recall {mean_recall:.2f}. Clusters not aligning with query similarity.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14e_lsh_v2_binaryivf"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "POOL_SIZE": POOL_SIZE, "QUERY_COUNT": QUERY_COUNT,
        "NUM_CENTROIDS": NUM_CENTROIDS, "NUM_CENTROIDS_PROBE": NUM_CENTROIDS_PROBE,
        "mean_recall_at_10": mean_recall,
        "brute_force_ms": bf_time, "ivf_ms": ivf_time,
        "speedup": bf_time / max(ivf_time, 1e-6),
        "cluster_sizes_min": min(cluster_sizes), "cluster_sizes_max": max(cluster_sizes),
    }, indent=2))


if __name__ == "__main__":
    main()
