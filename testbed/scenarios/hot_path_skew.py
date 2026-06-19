"""Scenario 12: hot_path_skew (realistic workload).

Setup: store M items. Stream: N_queries following a Zipfian distribution
(alpha = 1.2 by default) over the M stored items, so roughly 80% of
queries hit the top 20% "hot" items.

Real-world relevance: production retrieval is rarely uniform. A small
fraction of items (popular FAQs, trending docs, cached intents) absorbs
most of the query traffic. The question this scenario surfaces is:

  does any backend get a measurable speedup from skew, and which ones?

Substrate: per-query cost is matmul (W @ q_atom) + (codebook @ response).
Both are dense linear-algebra primitives on tensors that fit in cache for
this size; cost is INDEPENDENT of query frequency. We expect hot p50 to
equal cold p50 within noise.

FAISS Flat: per-query cost is brute-force inner product over all stored
vectors; also frequency-independent. Equal hot/cold p50.

Dict (cosine oracle): same; brute-force over all stored.

Chroma / sqlite_vec (when available): I/O backed; hot queries amortize
file cache hits and should show measurable hot < cold latency. (Not
asserted here; this scenario is descriptive.)

Substrate distinctive: the value-atom lookup table is a Python dict on
key_id -> value_row, which is O(1) regardless of frequency, AND the
W @ q_atom is the same dense matmul regardless of which q_atom. So
substrate's hot and cold are statistically indistinguishable; this is
the "uniform-cost-per-query" property that lets capacity planners reason
about p99 from a single benchmark.

This scenario is DESCRIPTIVE; no HARD_PASS / HARD_FAIL gates. It reports:
  hot_p50_retrieve_us
  cold_p50_retrieve_us
  hot_p95_retrieve_us
  cold_p95_retrieve_us
  hot_cold_ratio = hot_p50 / cold_p50 (close to 1.0 = uniform; <<1 = hot
    benefits from caching; >>1 = cold benefits, unlikely)
  hot_fraction_of_M  (default top 20%)
  hot_query_share   (fraction of queries that landed in the hot set)
  zipf_alpha        (Zipfian parameter used)
  zipf_top20_share  (concentration check: should be ~0.8 at alpha=1.2)
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from testbed.api import MemoryBackend


def _first_seed(config: dict) -> int:
    seeds = config.get("seeds", [7])
    if not seeds:
        return 7
    return int(seeds[0])


def _percentile(samples: list[float], q: float) -> float:
    if not samples:
        return 0.0
    return float(np.percentile(np.asarray(samples, dtype=np.float64), q))


def _draw_zipf_indices(
    rng: np.random.Generator, M: int, n_queries: int, alpha: float
) -> np.ndarray:
    """Sample n_queries indices in [0, M) under a truncated Zipfian.

    Uses inverse CDF on the explicit weight vector w[i] = 1 / (i+1)**alpha.
    Avoids np.random.zipf which is the open-ended Zeta distribution.
    """
    ranks = np.arange(1, M + 1, dtype=np.float64)
    weights = 1.0 / np.power(ranks, alpha)
    weights /= weights.sum()
    # cumulative CDF, then inverse via searchsorted
    cdf = np.cumsum(weights)
    u = rng.random(n_queries)
    idx = np.searchsorted(cdf, u, side="right")
    idx = np.clip(idx, 0, M - 1)
    return idx.astype(np.int64)


def setup(config: dict) -> dict:
    M = int(config.get("hot_path_M", config.get("M_base", 2000)))
    n_queries = int(config.get("hot_path_N_queries", 5000))
    dim = int(config.get("dim", 4096))
    alpha = float(config.get("hot_path_zipf_alpha", 1.2))
    hot_fraction = float(config.get("hot_path_hot_fraction", 0.2))
    seed = _first_seed(config)
    rng = np.random.default_rng(seed + 7300)

    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    key_vecs = raw * 2.0 - 1.0
    key_ids = [f"hps_{i:07d}" for i in range(M)]
    values = [f"hv_{i}" for i in range(M)]

    # Random permutation of M -> Zipfian ranks. Otherwise the hot set is
    # always {0, 1, ...}; permuting makes the hot set unrelated to insertion
    # order so substrate-internal optimizations (none expected) can't game it.
    rank_to_item = rng.permutation(M)
    query_ranks = _draw_zipf_indices(rng, M, n_queries, alpha)
    query_idx = rank_to_item[query_ranks]

    # Hot set: the rank_to_item[0 : floor(M * hot_fraction)]
    n_hot = max(1, int(np.floor(M * hot_fraction)))
    hot_items = set(rank_to_item[:n_hot].tolist())

    # Sanity: what fraction of queries actually fell in the top 20% of ranks?
    top20_count = int(np.sum(query_ranks < max(1, int(np.floor(M * 0.2)))))
    top20_share = top20_count / n_queries if n_queries else 0.0

    return {
        "key_ids": key_ids,
        "key_vecs": key_vecs,
        "values": values,
        "query_idx": query_idx,
        "hot_items": hot_items,
        "M": M,
        "n_queries": n_queries,
        "alpha": alpha,
        "hot_fraction": hot_fraction,
        "zipf_top20_share": top20_share,
        "seed": seed,
    }


def run(backend: MemoryBackend, data: dict) -> dict:
    key_ids: list[str] = data["key_ids"]
    key_vecs: np.ndarray = data["key_vecs"]
    values: list[str] = data["values"]
    query_idx: np.ndarray = data["query_idx"]
    hot_items: set = data["hot_items"]
    M = int(data["M"])
    n_queries = int(data["n_queries"])
    alpha = float(data["alpha"])
    hot_fraction = float(data["hot_fraction"])
    top20_share = float(data["zipf_top20_share"])

    # Setup
    for i in range(M):
        backend.store(key_ids[i], key_vecs[i], values[i])

    hot_us: list[float] = []
    cold_us: list[float] = []
    hot_count = 0

    for idx in query_idx:
        i = int(idx)
        kvec = key_vecs[i]
        t0 = time.perf_counter_ns()
        backend.retrieve(kvec, k=1)
        t1 = time.perf_counter_ns()
        wall_us = (t1 - t0) / 1000.0
        if i in hot_items:
            hot_us.append(wall_us)
            hot_count += 1
        else:
            cold_us.append(wall_us)

    hot_p50 = _percentile(hot_us, 50)
    cold_p50 = _percentile(cold_us, 50)
    if cold_p50 > 0.0:
        ratio = hot_p50 / cold_p50
    else:
        ratio = float("inf") if hot_p50 > 0.0 else 1.0

    return {
        "scenario": "hot_path_skew",
        "backend": backend.name,
        "M": M,
        "n_queries": n_queries,
        "zipf_alpha": alpha,
        "hot_fraction_of_M": hot_fraction,
        "hot_query_share": hot_count / n_queries if n_queries else 0.0,
        "zipf_top20_share": top20_share,
        "hot_p50_retrieve_us": hot_p50,
        "cold_p50_retrieve_us": cold_p50,
        "hot_p95_retrieve_us": _percentile(hot_us, 95),
        "cold_p95_retrieve_us": _percentile(cold_us, 95),
        "hot_mean_retrieve_us": float(np.mean(hot_us)) if hot_us else 0.0,
        "cold_mean_retrieve_us": float(np.mean(cold_us)) if cold_us else 0.0,
        "hot_cold_ratio": ratio,
        "n_hot_samples": len(hot_us),
        "n_cold_samples": len(cold_us),
    }


def thresholds() -> dict:
    # Descriptive scenario. The point is to show that substrate (and FAISS
    # Flat) are frequency-independent (hot_cold_ratio ~ 1.0), while disk-
    # backed baselines may show ratio < 1.0 from page-cache amortization.
    return {
        "substrate": {"hard_pass": {}, "hard_fail": {}},
        "baselines": {"hard_pass": {}, "hard_fail": {}},
    }
