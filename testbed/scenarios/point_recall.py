"""Scenario 1: point_recall.

Stores M deterministic key vectors with short-string values, then queries
each key vector against the backend. Measures argmax recall, top-5 recall,
both native and normalized confidence, and per-call store/retrieve wall
latencies.

Determinism: random vectors are drawn from np.random.default_rng(seed) where
seed = config["seeds"][0]. Multi-seed averaging is the caller's job (harness).
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


def setup(config: dict) -> dict:
    """Build M random float32 key vectors of dimension `dim`.

    Keys are sampled from a Rademacher (+/-1) distribution so they double as
    valid substrate atoms while still being plain float32 ndarrays for the
    baselines.
    """
    M = int(config.get("M_total", config.get("point_recall_M", 1000)))
    dim = int(config.get("dim", 4096))
    seed = _first_seed(config)
    rng = np.random.default_rng(seed)

    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    key_vecs = (raw * 2.0 - 1.0)
    key_ids = [f"pr_{i:06d}" for i in range(M)]
    values = [f"fact_{i}" for i in range(M)]
    query_vecs = key_vecs.copy()

    return {
        "key_ids": key_ids,
        "key_vecs": key_vecs,
        "values": values,
        "query_vecs": query_vecs,
        "M": M,
        "dim": dim,
        "seed": seed,
    }


def run(backend: MemoryBackend, data: dict) -> dict:
    key_ids: list[str] = data["key_ids"]
    key_vecs: np.ndarray = data["key_vecs"]
    values: list[str] = data["values"]
    query_vecs: np.ndarray = data["query_vecs"]
    M = len(key_ids)

    store_times_us: list[float] = []
    retrieve_times_us: list[float] = []

    for i in range(M):
        t0 = time.perf_counter_ns()
        backend.store(key_ids[i], key_vecs[i], values[i])
        t1 = time.perf_counter_ns()
        store_times_us.append((t1 - t0) / 1000.0)

    hits_top1 = 0
    hits_top5 = 0
    native_conf: list[float] = []
    normalized_conf: list[float] = []

    for i in range(M):
        t0 = time.perf_counter_ns()
        res = backend.retrieve(query_vecs[i], k=5)
        t1 = time.perf_counter_ns()
        retrieve_times_us.append((t1 - t0) / 1000.0)

        correct_id = key_ids[i]
        top_ids = list(res.top_k_ids) if res.top_k_ids else (
            [res.key_id] if res.key_id is not None else []
        )
        if top_ids and top_ids[0] == correct_id:
            hits_top1 += 1
            normalized_conf.append(1.0)
        else:
            normalized_conf.append(0.0)
        if correct_id in top_ids:
            hits_top5 += 1
        native_conf.append(float(res.confidence) if res.confidence is not None else 0.0)

    recall_at_1 = hits_top1 / M if M else 0.0
    recall_at_5 = hits_top5 / M if M else 0.0

    return {
        "scenario": "point_recall",
        "backend": backend.name,
        "n_items": M,
        "recall_at_1": recall_at_1,
        "recall_at_5": recall_at_5,
        "mean_native_confidence": float(np.mean(native_conf)) if native_conf else 0.0,
        "mean_normalized_correctness": float(np.mean(normalized_conf)) if normalized_conf else 0.0,
        "p50_store_us": _percentile(store_times_us, 50),
        "p95_store_us": _percentile(store_times_us, 95),
        "p50_retrieve_us": _percentile(retrieve_times_us, 50),
        "p95_retrieve_us": _percentile(retrieve_times_us, 95),
        "native_confidence_samples": native_conf[:32],
    }


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {"recall_at_1_at_M_over_N_le_1": 0.95},
            "hard_fail": {"recall_at_1_at_M_over_N_eq_0p25": 0.50},
            "above_capacity_pass": {"recall_at_1_at_M_over_N_le_2": 0.80},
        },
        "baselines": {
            "hard_pass": {"recall_at_1": 0.99},
            "hard_fail": {"recall_at_1": 0.50},
        },
    }
