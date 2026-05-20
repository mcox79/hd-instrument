"""LSH for BSC bipolar pool indexing — minimal viable probe.

Bipolar dot-product = N - 2*hamming(x,y). So bipolar similarity reduces to
Hamming similarity, where SimHash / random hyperplane LSH is the natural fit
(Charikar 2002).

Minimal test:
- Build pool of P=10000 random BSC bipolar vectors.
- Build query set of Q=1000 vectors, each near a random pool entry.
- LSH index: M=8 hash tables, each L=16 bits (random sign projections).
- Measure recall@10 vs brute-force ground truth + query latency.

Pass: recall@10 >= 0.9 AND query latency reduction >= 10x vs brute-force.
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
NEAR_FLIP_RATE = 0.1  # 10% bit flips for "near" query
NUM_TABLES = 8
HASH_BITS = 16
SEED = 17


def _say(m): print(m, flush=True)


def make_bsc(p, n, gen):
    return 2.0 * (torch.rand((p, n), generator=gen) > 0.5).float() - 1.0


def make_near_queries(pool, num, flip_rate, gen):
    """For each query, pick a random pool entry and flip flip_rate fraction of bits."""
    src_idx = torch.randint(0, pool.shape[0], (num,), generator=gen).tolist()
    queries = pool[src_idx].clone()
    n_flip = int(N * flip_rate)
    for q in range(num):
        flip_positions = torch.randperm(N, generator=gen)[:n_flip]
        queries[q, flip_positions] *= -1
    return queries.to(DEVICE), src_idx


def brute_force_topk(pool, queries, k=10):
    sims = (queries @ pool.T) / N
    return sims.topk(k, dim=1).indices


def build_lsh(pool, num_tables, bits, gen):
    """Build LSH: num_tables hash tables, each bits-wide. Returns projection matrices and bucket dicts."""
    projections = []
    bucket_lists = []
    for _ in range(num_tables):
        proj = 2.0 * (torch.rand((bits, N), generator=gen) > 0.5).float() - 1.0
        proj = proj.to(DEVICE)
        # Hash each pool entry: sign(proj @ entry) -> int
        signs = ((pool @ proj.T) > 0).int()  # (P, bits)
        # Combine bits into integer keys
        weights = 1 << torch.arange(bits, device=DEVICE)
        keys = (signs * weights).sum(dim=1).tolist()
        buckets = {}
        for idx, key in enumerate(keys):
            buckets.setdefault(key, []).append(idx)
        projections.append(proj)
        bucket_lists.append(buckets)
    return projections, bucket_lists


def lsh_query(query, projections, bucket_lists, pool, k=10):
    """Return top-k indices via LSH."""
    candidate_set = set()
    for proj, buckets in zip(projections, bucket_lists):
        signs = ((query @ proj.T) > 0).int()
        weights = 1 << torch.arange(len(signs), device=DEVICE)
        key = int((signs * weights).sum().item())
        if key in buckets:
            candidate_set.update(buckets[key])
    if not candidate_set:
        return torch.tensor([], dtype=torch.long, device=DEVICE)
    candidates = torch.tensor(list(candidate_set), dtype=torch.long, device=DEVICE)
    sims = (pool[candidates] @ query) / N
    top = sims.topk(min(k, len(candidates))).indices
    return candidates[top]


def main():
    _say(f"LSH for BSC: N={N}, P={POOL_SIZE}, Q={QUERY_COUNT}, M={NUM_TABLES} tables x {HASH_BITS} bits")
    gen = torch.Generator().manual_seed(SEED)

    pool = make_bsc(POOL_SIZE, N, gen).to(DEVICE)
    queries, src_idx = make_near_queries(pool, QUERY_COUNT, NEAR_FLIP_RATE, gen)
    _say(f"  Pool built. {QUERY_COUNT} queries near random pool entries (flip rate {NEAR_FLIP_RATE}).")

    # Brute force ground truth
    t0 = time.time()
    truth_top10 = brute_force_topk(pool, queries, k=10)
    bf_time = (time.time() - t0) / QUERY_COUNT * 1000  # ms per query
    _say(f"  Brute force: {bf_time:.3f}ms per query")

    # LSH build
    t0 = time.time()
    projs, buckets = build_lsh(pool, NUM_TABLES, HASH_BITS, gen)
    build_time = time.time() - t0
    _say(f"  LSH build: {build_time:.2f}s ({sum(len(b) for b in buckets)} total bucket entries)")

    # LSH query
    t0 = time.time()
    lsh_results = []
    for q in range(QUERY_COUNT):
        res = lsh_query(queries[q], projs, buckets, pool, k=10)
        lsh_results.append(res)
    lsh_time = (time.time() - t0) / QUERY_COUNT * 1000
    _say(f"  LSH query: {lsh_time:.3f}ms per query  speedup={bf_time/max(lsh_time,1e-6):.1f}x")

    # Recall@10
    recalls = []
    for q in range(QUERY_COUNT):
        truth = set(truth_top10[q].tolist())
        retrieved = set(lsh_results[q].tolist())
        if truth:
            recalls.append(len(truth & retrieved) / len(truth))
        else:
            recalls.append(0.0)
    mean_recall = sum(recalls) / len(recalls)
    _say(f"\n  Recall@10: {mean_recall:.3f}")
    _say(f"  Speedup: {bf_time/max(lsh_time, 1e-6):.1f}x")

    if mean_recall >= 0.9 and (bf_time / max(lsh_time, 1e-6)) >= 10:
        _say(f"\n  PASS: BSC LSH works. Pool indexing path open.")
    elif mean_recall >= 0.7:
        _say(f"\n  PARTIAL: recall solid but speedup small or vice versa. Worth tuning M, bits.")
    else:
        _say(f"\n  WEAK: recall {mean_recall:.2f} < 0.7. SimHash insufficient at this N/P; try MIH.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14e_lsh_for_bsc"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "POOL_SIZE": POOL_SIZE, "QUERY_COUNT": QUERY_COUNT,
        "NUM_TABLES": NUM_TABLES, "HASH_BITS": HASH_BITS,
        "mean_recall_at_10": mean_recall,
        "brute_force_ms": bf_time, "lsh_ms": lsh_time,
        "speedup": bf_time / max(lsh_time, 1e-6),
    }, indent=2))


if __name__ == "__main__":
    main()
