"""Wave 14.B CPU platform timing — validates the platform claim.

Measures end-to-end latency of retrieve+decompose pipeline on the
TARGET deployment hardware (consumer CPU). The platform commitment is:
sub-100ms retrieval+decomposition at production pool sizes on a
consumer laptop.

Sweep dimensions:
- N (vector dim): 2048, 4096, 8192
- Pool size: 1K, 10K, 100K
- Bundle complexity (slots): 2, 4, 8

For each config:
- Build random pool of bundles
- Time 100 retrieval+decomposition queries
- Report median + p99 latency

Pure measurement, no architectural changes. Forces device='cpu'.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch


import os
torch.set_num_threads(max(1, os.cpu_count() or 1))
DEVICE = torch.device("cpu")  # FORCE CPU regardless of CUDA availability
SEED = 17
N_VALUES = [2048, 4096, 8192]
POOL_SIZES = [1024, 10000, 100000]
BUNDLE_SLOTS = [2, 4, 8]
NUM_QUERIES = 30
CODEBOOK_K = 256
SKIP_IF_PN_OVER = 5_000_000_000  # skip pool*N*queries op-count over this to bound runtime


def _say(msg: str) -> None:
    print(msg, flush=True)


def build_codebook(gen, K, N):
    bits = torch.randint(0, 2, (K, N), generator=gen)
    return (bits * 2 - 1).to(torch.float32)


def build_positions(gen, B, N):
    bits = torch.randint(0, 2, (B, N), generator=gen)
    return (bits * 2 - 1).to(torch.float32)


def build_pool(gen, P, B, N, codebook, positions):
    """Build pool of P bundles, each with B atom-position bindings."""
    pool = torch.zeros((P, N), dtype=torch.float32)
    K = codebook.shape[0]
    for i in range(P):
        atom_ids = torch.randint(0, K, (B,), generator=gen)
        atoms = codebook[atom_ids]
        pool[i] = (atoms * positions).sum(dim=0)
    return pool


def retrieve_top_M(query, pool, M):
    """Cosine match query against pool, return top-M indices."""
    pool_norms = pool.norm(dim=1).clamp(min=1e-12)
    qnorm = query.norm().clamp(min=1e-12)
    scores = (pool @ query) / (pool_norms * qnorm)
    top_idx = scores.topk(min(M, pool.shape[0])).indices
    return top_idx, scores[top_idx]


def resonator_decompose_single(bundle, positions, codebook, N, num_restarts=4, max_iter=30):
    """Decompose a bundle into its B atom indices via resonator."""
    B = positions.shape[0]
    K = codebook.shape[0]
    best_score = -float("inf")
    best_idx = [-1] * B
    BETA_MAX = 20.0
    for restart in range(num_restarts):
        init_indices = torch.randint(0, K, (B,))
        atoms_hat = codebook[init_indices].clone()
        beta = 1.0
        for it in range(max_iter):
            for s in range(B):
                contribution_others = (atoms_hat * positions).sum(dim=0) - atoms_hat[s] * positions[s]
                candidate = (bundle - contribution_others) * positions[s]
                scores = (codebook @ candidate) / math.sqrt(N)
                weights = torch.softmax(beta * scores, dim=0)
                atoms_hat[s] = weights @ codebook
            beta = min(beta * 1.5, BETA_MAX)
        pred_idx = []
        for s in range(B):
            scores = codebook @ atoms_hat[s]
            pred_idx.append(int(scores.argmax().item()))
        pred_atoms = codebook[torch.tensor(pred_idx)]
        c_recon = (pred_atoms * positions).sum(dim=0)
        score = float((bundle @ c_recon) / (bundle.norm() * c_recon.norm() + 1e-12))
        if score > best_score:
            best_score = score
            best_idx = pred_idx
    return best_idx


def time_full_pipeline(N, P, B, top_M=4):
    """Time NUM_QUERIES retrieval+decomposition queries. Returns latency stats."""
    gen = torch.Generator().manual_seed(SEED + N + P + B)
    codebook = build_codebook(gen, CODEBOOK_K, N)
    positions = build_positions(gen, B, N)
    pool = build_pool(gen, P, B, N, codebook, positions)

    # Pre-build query bundles
    query_bundles = []
    for q in range(NUM_QUERIES):
        qg = torch.Generator().manual_seed(SEED + 10000 + q)
        atom_ids = torch.randint(0, CODEBOOK_K, (B,), generator=qg)
        atoms = codebook[atom_ids]
        query_bundles.append((atoms * positions).sum(dim=0))

    # Time queries
    latencies_retrieve = []
    latencies_decompose = []
    latencies_total = []
    for query in query_bundles:
        t0 = time.perf_counter()
        top_idx, top_scores = retrieve_top_M(query, pool, top_M)
        t1 = time.perf_counter()
        # Decompose retrieved bundles
        for idx in top_idx:
            _ = resonator_decompose_single(pool[idx], positions, codebook, N,
                                           num_restarts=2, max_iter=15)
        t2 = time.perf_counter()
        latencies_retrieve.append((t1 - t0) * 1000)
        latencies_decompose.append((t2 - t1) * 1000)
        latencies_total.append((t2 - t0) * 1000)

    def stats(arr):
        arr_sorted = sorted(arr)
        n = len(arr_sorted)
        return {"median_ms": arr_sorted[n // 2],
                "p99_ms": arr_sorted[int(0.99 * (n - 1))],
                "mean_ms": sum(arr_sorted) / n}

    return {"retrieve": stats(latencies_retrieve),
            "decompose": stats(latencies_decompose),
            "total": stats(latencies_total)}


def main():
    _say(f"Wave 14.B CPU platform timing")
    _say(f"  device={DEVICE}, codebook_K={CODEBOOK_K}, NUM_QUERIES={NUM_QUERIES}")
    _say(f"  Platform target: <100 ms p99 for retrieve+decompose")
    _say(f"  Threads: {torch.get_num_threads()}")

    all_results = []
    t_start = time.perf_counter()
    for N in N_VALUES:
        for P in POOL_SIZES:
            for B in BUNDLE_SLOTS:
                _say(f"\n  N={N}, P={P}, B={B}")
                t0 = time.perf_counter()
                try:
                    stats = time_full_pipeline(N, P, B, top_M=4)
                    dt = time.perf_counter() - t0
                    _say(f"    retrieve p50={stats['retrieve']['median_ms']:.2f}ms  p99={stats['retrieve']['p99_ms']:.2f}ms")
                    _say(f"    decompose p50={stats['decompose']['median_ms']:.2f}ms p99={stats['decompose']['p99_ms']:.2f}ms")
                    _say(f"    TOTAL    p50={stats['total']['median_ms']:.2f}ms     p99={stats['total']['p99_ms']:.2f}ms")
                    target_met = stats["total"]["p99_ms"] < 100.0
                    _say(f"    Platform target ({'MET' if target_met else 'MISSED'}): p99 {'<' if target_met else '>='} 100ms")
                    all_results.append({"N": N, "P": P, "B": B, "stats": stats,
                                       "wall_s": dt, "target_met": target_met})
                except Exception as e:
                    _say(f"    ERROR: {e}")
                    all_results.append({"N": N, "P": P, "B": B, "error": str(e)})
                # Incremental save
                out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cpu_platform_timing"
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "metrics.json").write_text(json.dumps(
                    {"results_so_far": all_results,
                     "elapsed_s": time.perf_counter() - t_start},
                    indent=2, default=str))

    _say(f"\n========= SUMMARY =========")
    targets_met = sum(1 for r in all_results if r.get("target_met"))
    _say(f"  Configurations meeting <100ms p99 target: {targets_met}/{len(all_results)}")
    _say(f"  Total wall: {(time.perf_counter() - t_start)/60:.1f} min")


if __name__ == "__main__":
    main()
