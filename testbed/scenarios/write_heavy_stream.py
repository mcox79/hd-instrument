"""Scenario 10: write_heavy_stream (realistic workload).

Continuous write stream: store M_total items one-at-a-time in a loop.
Measures per-op store latency BY DECILE so we can see whether the write
rate degrades as the backend's state grows.

Real-world relevance: ingest workloads (log shipping, telemetry, document
indexing) hammer store() far more than retrieve(). Batch testing hides
capacity-related slowdown because all writes happen at once with no
intervening state-change cost; streamed writes surface the per-op fixed
cost that grows with stored count.

Substrate-specific signal: tracks the Frobenius RMS of the W matrix as it
grows. RMS growth is the analytic signal of capacity pressure (the outer-
product sum accumulates value-key correlations; |W|_F scales with sqrt(M)
in the BSC regime, and saturates near the spectral edge under crowding).
The deciles let us see whether per-op store wall correlates with capacity
load.

Baseline-specific signal: FAISS adds to a flat index; under IndexFlatIP
the per-add cost is dominated by the array append which should stay flat.
Dict and Chroma append rows or persist to disk; Chroma flushes can spike
the tail latency.

HARD_PASS substrate: p99 store latency at last decile <= 1.5x first decile
(sustained write rate; small drift is fine, large drift signals a capacity
issue or a quadratic).
HARD_PASS baselines: same 1.5x p99 sustained-rate gate.

Returns:
  per_decile: list of dicts, one per decile, with p50/p95/p99 store_us
  total_wall_s: total time to ingest M_total items
  ops_per_sec: M_total / total_wall_s
  w_rms_last: substrate Frobenius RMS at end of ingest (None for baselines)
  w_rms_per_decile: substrate W-RMS sampled at each decile boundary
  p99_last_over_first: ratio of last-decile p99 over first-decile p99
  hard_pass_substrate: bool
  hard_pass_baselines: bool
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


def _w_rms(backend: MemoryBackend) -> float | None:
    """Substrate Frobenius RMS = sqrt(mean(W**2)). None for non-substrate."""
    W = getattr(backend, "W", None)
    if W is None:
        # Sharded: aggregate over shard W matrices.
        shards = getattr(backend, "shards", None)
        if shards is None:
            return None
        try:
            total_sq = 0.0
            total_n = 0
            for shard in shards:
                Ws = getattr(shard, "W", None)
                if Ws is None:
                    continue
                arr = Ws.detach().cpu().numpy() if hasattr(Ws, "detach") else np.asarray(Ws)
                total_sq += float(np.sum(arr.astype(np.float64) ** 2))
                total_n += int(arr.size)
            if total_n == 0:
                return None
            return float(np.sqrt(total_sq / total_n))
        except Exception:
            return None
    try:
        arr = W.detach().cpu().numpy() if hasattr(W, "detach") else np.asarray(W)
        return float(np.sqrt(np.mean(arr.astype(np.float64) ** 2)))
    except Exception:
        return None


def setup(config: dict) -> dict:
    M = int(config.get("write_heavy_M_total", config.get("M_total", 5000)))
    dim = int(config.get("dim", 4096))
    seed = _first_seed(config)
    n_deciles = int(config.get("write_heavy_n_deciles", 10))
    batch_size = int(config.get("write_heavy_batch_size", config.get("batch_size", 1)))
    if batch_size < 1:
        batch_size = 1
    rng = np.random.default_rng(seed + 7100)

    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    key_vecs = raw * 2.0 - 1.0
    key_ids = [f"whs_{i:07d}" for i in range(M)]
    values = [f"wv_{i}" for i in range(M)]

    return {
        "key_ids": key_ids,
        "key_vecs": key_vecs,
        "values": values,
        "M": M,
        "dim": dim,
        "seed": seed,
        "n_deciles": n_deciles,
        "batch_size": batch_size,
    }


def run(backend: MemoryBackend, data: dict) -> dict:
    key_ids: list[str] = data["key_ids"]
    key_vecs: np.ndarray = data["key_vecs"]
    values: list[str] = data["values"]
    M = int(data["M"])
    n_deciles = int(data["n_deciles"])
    batch_size = int(data.get("batch_size", 1))

    decile_size = max(1, M // n_deciles)
    is_substrate = (
        backend.name == "substrate"
        or backend.name.startswith("substrate_v")
        or backend.name == "substrate_sharded"
    )

    store_us_per_decile: list[list[float]] = [[] for _ in range(n_deciles)]
    w_rms_per_decile: list[float | None] = []

    t_total_0 = time.perf_counter_ns()
    if batch_size <= 1:
        for i in range(M):
            d = min(i // decile_size, n_deciles - 1)
            t0 = time.perf_counter_ns()
            backend.store(key_ids[i], key_vecs[i], values[i])
            t1 = time.perf_counter_ns()
            store_us_per_decile[d].append((t1 - t0) / 1000.0)
            if is_substrate and ((i + 1) % decile_size == 0):
                w_rms_per_decile.append(_w_rms(backend))
    else:
        # Batched path. Each batch attributes its wall time evenly across the
        # B items so per-decile p50/p95/p99 still reflect "per-item amortized"
        # cost. ops_per_sec is computed from total wall and total M.
        i = 0
        while i < M:
            end = min(i + batch_size, M)
            chunk = [
                (key_ids[j], key_vecs[j], values[j]) for j in range(i, end)
            ]
            t0 = time.perf_counter_ns()
            backend.store_batch(chunk)
            t1 = time.perf_counter_ns()
            per_item_us = (t1 - t0) / 1000.0 / max(1, end - i)
            for j in range(i, end):
                d = min(j // decile_size, n_deciles - 1)
                store_us_per_decile[d].append(per_item_us)
                if is_substrate and ((j + 1) % decile_size == 0):
                    w_rms_per_decile.append(_w_rms(backend))
            i = end
    t_total_1 = time.perf_counter_ns()
    total_wall_s = (t_total_1 - t_total_0) / 1e9
    ops_per_sec = M / total_wall_s if total_wall_s > 0 else 0.0

    per_decile: list[dict] = []
    for d, samples in enumerate(store_us_per_decile):
        per_decile.append({
            "decile": d,
            "n_ops": len(samples),
            "p50_store_us": _percentile(samples, 50),
            "p95_store_us": _percentile(samples, 95),
            "p99_store_us": _percentile(samples, 99),
            "mean_store_us": float(np.mean(samples)) if samples else 0.0,
        })

    first_p99 = per_decile[0]["p99_store_us"]
    last_p99 = per_decile[-1]["p99_store_us"]
    if first_p99 > 0.0:
        p99_ratio = last_p99 / first_p99
    else:
        p99_ratio = float("inf") if last_p99 > 0.0 else 1.0

    hard_pass_substrate = bool(is_substrate and p99_ratio <= 1.5)
    hard_pass_baselines = bool((not is_substrate) and p99_ratio <= 1.5)

    w_rms_last = _w_rms(backend) if is_substrate else None

    return {
        "scenario": "write_heavy_stream",
        "backend": backend.name,
        "n_items": M,
        "n_deciles": n_deciles,
        "decile_size": decile_size,
        "batch_size_used": batch_size,
        "per_decile": per_decile,
        "total_wall_s": total_wall_s,
        "ops_per_sec": ops_per_sec,
        "p99_last_over_first": p99_ratio,
        "first_decile_p99_us": first_p99,
        "last_decile_p99_us": last_p99,
        "w_rms_last": w_rms_last,
        "w_rms_per_decile": w_rms_per_decile if is_substrate else None,
        "hard_pass_substrate": hard_pass_substrate,
        "hard_pass_baselines": hard_pass_baselines,
    }


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {"p99_last_over_first_le": 1.5},
            "hard_fail": {"p99_last_over_first_ge": 3.0},
        },
        "baselines": {
            "hard_pass": {"p99_last_over_first_le": 1.5},
            "hard_fail": {"p99_last_over_first_ge": 3.0},
        },
    }
