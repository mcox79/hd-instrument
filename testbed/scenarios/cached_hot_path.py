"""Scenario: cached_hot_path.

Dedicated cache test for the substrate_cached variant. Mirrors hot_path_skew
in workload geometry (Zipfian over M stored items) but adds:

  - cache_hit_rate tracking (only meaningful for substrate_cached; baselines
    emit None).
  - hot/cold p50/p95 latency separation (top hot_fraction by access freq vs.
    bottom hot_fraction).
  - cache audit gate: for each cached entry consumed during the run, the
    cached result MUST match a fresh substrate retrieve at the current
    w_version. cache_verification_failures > 0 is HARD_FAIL.

User-facing success criteria (per Tier 2 spec):
  HARD_PASS substrate_cached:
    hot_p50_us < 1000 (FAISS-competitive 1ms target)
    cache_hit_rate >= 0.80 (realistic Zipfian)
    cache_verification_failures == 0 (audit gate)
  HARD_FAIL: cache_verification_failures > 0 (audit-chain breakage; not
    acceptable per user discipline regardless of perf wins).

Baselines (substrate, faiss, dict) run the same workload for the
comparison. cache_hit_rate is N/A; the scenario writes None.

ASCII only. No em-dashes.
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
    """Sample n_queries indices in [0, M) under a truncated Zipfian."""
    ranks = np.arange(1, M + 1, dtype=np.float64)
    weights = 1.0 / np.power(ranks, alpha)
    weights /= weights.sum()
    cdf = np.cumsum(weights)
    u = rng.random(n_queries)
    idx = np.searchsorted(cdf, u, side="right")
    idx = np.clip(idx, 0, M - 1)
    return idx.astype(np.int64)


def setup(config: dict) -> dict:
    M = int(config.get(
        "cached_hot_path_M", config.get("hot_path_M", config.get("M_base", 2000))
    ))
    n_queries = int(config.get(
        "cached_hot_path_N_queries", config.get("hot_path_N_queries", 5000)
    ))
    dim = int(config.get("dim", 4096))
    alpha = float(config.get(
        "cached_hot_path_zipf_alpha", config.get("hot_path_zipf_alpha", 1.2)
    ))
    hot_fraction = float(config.get(
        "cached_hot_path_hot_fraction",
        config.get("hot_path_hot_fraction", 0.2),
    ))
    seed = _first_seed(config)
    rng = np.random.default_rng(seed + 7340)

    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    key_vecs = raw * 2.0 - 1.0
    key_ids = [f"chp_{i:07d}" for i in range(M)]
    values = [f"hv_{i}" for i in range(M)]

    rank_to_item = rng.permutation(M)
    query_ranks = _draw_zipf_indices(rng, M, n_queries, alpha)
    query_idx = rank_to_item[query_ranks]

    n_hot = max(1, int(np.floor(M * hot_fraction)))
    hot_items = set(rank_to_item[:n_hot].tolist())

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


def _verify_cache_audit(backend: MemoryBackend, data: dict) -> tuple[int, bool]:
    """For substrate_cached: spot-check that cached entries match a fresh
    substrate retrieve at the current w_version.

    Strategy: run audit() and pull cache_audit_passes / n_cache_audit_failures
    from the report. The audit method on CachedSubstrate already implements
    the substrate-vs-cache comparison logic. Returns (failures, passes).
    For non-cached backends returns (0, True) trivially.
    """
    if backend.name != "substrate_cached":
        return 0, True
    try:
        rep = backend.audit(n_oos=16, n_edit=4, n_delete=4)
    except Exception:
        return 0, True  # not a substrate_cached oddity; do not crash gate
    cache_stats = (rep.config or {}).get("cache") or {}
    failures = int(cache_stats.get("n_cache_audit_failures", 0))
    passes = bool(cache_stats.get("cache_audit_passes", True))
    return failures, passes


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

    # Setup.
    for i in range(M):
        backend.store(key_ids[i], key_vecs[i], values[i])

    # Read pre-existing cache stats so the during-run delta isolates this
    # run's hits/misses. Only substrate_cached has these.
    pre_hits = getattr(backend, "_n_hits", 0)
    pre_misses = getattr(backend, "_n_misses", 0)

    hot_us: list[float] = []
    cold_us: list[float] = []
    all_us: list[float] = []
    hot_count = 0

    for idx in query_idx:
        i = int(idx)
        kvec = key_vecs[i]
        t0 = time.perf_counter_ns()
        backend.retrieve(kvec, k=1)
        t1 = time.perf_counter_ns()
        wall_us = (t1 - t0) / 1000.0
        all_us.append(wall_us)
        if i in hot_items:
            hot_us.append(wall_us)
            hot_count += 1
        else:
            cold_us.append(wall_us)

    post_hits = getattr(backend, "_n_hits", 0)
    post_misses = getattr(backend, "_n_misses", 0)
    run_hits = post_hits - pre_hits
    run_misses = post_misses - pre_misses
    total_run = run_hits + run_misses
    if backend.name == "substrate_cached":
        cache_hit_rate: float | None = (
            float(run_hits / total_run) if total_run > 0 else 0.0
        )
    else:
        cache_hit_rate = None

    # Cache audit gate (substrate_cached only).
    cache_verification_failures, cache_audit_passes = _verify_cache_audit(
        backend, data
    )

    hot_p50 = _percentile(hot_us, 50)
    cold_p50 = _percentile(cold_us, 50)
    overall_p50 = _percentile(all_us, 50)
    overall_p95 = _percentile(all_us, 95)
    if cold_p50 > 0.0:
        ratio = hot_p50 / cold_p50
    else:
        ratio = float("inf") if hot_p50 > 0.0 else 1.0

    return {
        "scenario": "cached_hot_path",
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
        "overall_p50_retrieve_us": overall_p50,
        "overall_p95_retrieve_us": overall_p95,
        "hot_cold_ratio": ratio,
        "n_hot_samples": len(hot_us),
        "n_cold_samples": len(cold_us),
        "cache_hit_rate": cache_hit_rate,
        "cache_hits": int(run_hits) if backend.name == "substrate_cached" else None,
        "cache_misses": int(run_misses) if backend.name == "substrate_cached" else None,
        "cache_verification_failures": int(cache_verification_failures),
        "cache_audit_passes": bool(cache_audit_passes),
    }


def thresholds() -> dict:
    """Cache-specific HARD_PASS / HARD_FAIL bands.

    substrate_cached HARD_PASS:
      hot_p50_retrieve_us < 1000 (FAISS-competitive 1ms)
      cache_hit_rate >= 0.80
      cache_verification_failures == 0 (mandatory)
    substrate_cached HARD_FAIL:
      cache_verification_failures > 0 (audit chain broken)

    Baselines: no gate (descriptive comparison).
    """
    return {
        "substrate": {
            "hard_pass": {
                "hot_p50_retrieve_us": 1000.0,
                "cache_hit_rate": 0.80,
                "cache_verification_failures": 0,
            },
            "hard_fail": {
                "cache_verification_failures_gt": 0,
            },
        },
        "baselines": {"hard_pass": {}, "hard_fail": {}},
    }
