"""Scenario: approx_retrieve_sweep (Path 5 randomized matvec).

Sweeps sample_frac in [1.0, 0.5, 0.3, 0.2, 0.1, 0.05] for the substrate's
retrieve_approx() method (Halko-Martinsson-Tropp randomized column sampling).
sample_frac=1.0 is the EXACT baseline; lower values trade recall for latency.

At each sample_frac:
  - run n_queries retrievals on stored keys (random subset)
  - record recall_at_1 (was the stored key_id returned)
  - record p50 / p95 wall latency in microseconds

Returns per-sample-frac dict plus an operating-point recommendation: the
smallest sample_frac whose recall_at_1 is at least op_recall_target (default
0.85). HARD_PASS requires sample_frac=0.3 to deliver recall_at_1 >= 0.80 AND
latency <= 0.5 * exact_latency.

This scenario is substrate-only; other backends do not have a column-sampling
analog. Falls back to a single-row passthrough for non-substrate backends so
the cross-backend table doesn't go empty.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from testbed.api import MemoryBackend


_SAMPLE_FRACS = [1.0, 0.5, 0.3, 0.2, 0.1, 0.05]


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
    M = int(config.get("approx_M", config.get("M_total", 1024)))
    n_queries = int(config.get("approx_n_queries", 500))
    dim = int(config.get("dim", config.get("N", 4096)))
    op_recall_target = float(config.get("approx_op_recall_target", 0.85))
    sample_fracs = config.get("approx_sample_fracs", _SAMPLE_FRACS)
    sample_fracs = [float(x) for x in sample_fracs]
    seed = _first_seed(config)
    rng = np.random.default_rng(seed + 9100)

    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    key_vecs = raw * 2.0 - 1.0
    key_ids = [f"ap_{i:07d}" for i in range(M)]
    values = [f"av_{i}" for i in range(M)]

    if n_queries >= M:
        query_idx = rng.permutation(M)[:n_queries] if n_queries <= M else rng.integers(0, M, size=n_queries)
    else:
        query_idx = rng.choice(M, size=n_queries, replace=False)

    return {
        "key_ids": key_ids,
        "key_vecs": key_vecs,
        "values": values,
        "query_idx": query_idx,
        "sample_fracs": sample_fracs,
        "M": M,
        "n_queries": n_queries,
        "op_recall_target": op_recall_target,
        "seed": seed,
    }


def _run_one_frac(
    backend: MemoryBackend,
    key_vecs: np.ndarray,
    key_ids: list[str],
    query_idx: np.ndarray,
    sample_frac: float,
    seed: int,
) -> dict:
    """Run n_queries retrievals at one sample_frac, return per-cell metrics."""
    is_substrate = hasattr(backend, "retrieve_approx")
    hits = 0
    lat_us: list[float] = []
    n = len(query_idx)
    for j, idx in enumerate(query_idx):
        i = int(idx)
        kvec = key_vecs[i]
        t0 = time.perf_counter_ns()
        if is_substrate:
            # Per-query rng seed for reproducibility while keeping variance.
            res = backend.retrieve_approx(
                kvec, sample_frac=sample_frac, k=1, seed=seed + j
            )
        else:
            res = backend.retrieve(kvec, k=1)
        t1 = time.perf_counter_ns()
        lat_us.append((t1 - t0) / 1000.0)
        if res.key_id == key_ids[i]:
            hits += 1
    recall = hits / n if n else 0.0
    return {
        "sample_frac": float(sample_frac),
        "recall_at_1": float(recall),
        "p50_latency_us": _percentile(lat_us, 50),
        "p95_latency_us": _percentile(lat_us, 95),
        "mean_latency_us": float(np.mean(lat_us)) if lat_us else 0.0,
        "n_queries": int(n),
    }


def run(backend: MemoryBackend, data: dict) -> dict:
    key_ids: list[str] = data["key_ids"]
    key_vecs: np.ndarray = data["key_vecs"]
    values: list[str] = data["values"]
    query_idx: np.ndarray = data["query_idx"]
    sample_fracs: list[float] = data["sample_fracs"]
    M = int(data["M"])
    n_queries = int(data["n_queries"])
    op_recall_target = float(data["op_recall_target"])
    seed = int(data["seed"])

    # Setup phase: store M items.
    if hasattr(backend, "store_batch"):
        items = [(key_ids[i], key_vecs[i], values[i]) for i in range(M)]
        backend.store_batch(items)
    else:
        for i in range(M):
            backend.store(key_ids[i], key_vecs[i], values[i])

    is_substrate = hasattr(backend, "retrieve_approx")

    per_frac: dict[str, dict] = {}
    for sf in sample_fracs:
        cell = _run_one_frac(backend, key_vecs, key_ids, query_idx, sf, seed)
        per_frac[f"{sf:.4f}"] = cell

    # Baseline (sample_frac=1.0) for ratio calcs.
    exact_key = f"{1.0:.4f}"
    exact_cell = per_frac.get(exact_key)
    exact_lat = exact_cell["p50_latency_us"] if exact_cell else 0.0
    exact_recall = exact_cell["recall_at_1"] if exact_cell else 0.0

    # Annotate ratios for downstream reporting.
    for key, cell in per_frac.items():
        if exact_lat > 0.0:
            cell["latency_ratio_vs_exact"] = cell["p50_latency_us"] / exact_lat
        else:
            cell["latency_ratio_vs_exact"] = None
        cell["recall_delta_vs_exact"] = cell["recall_at_1"] - exact_recall

    # Operating point: smallest sample_frac with recall >= op_recall_target.
    op_pt: dict | None = None
    sorted_fracs = sorted(per_frac.values(), key=lambda c: c["sample_frac"])
    for cell in sorted_fracs:
        if cell["recall_at_1"] >= op_recall_target:
            op_pt = {
                "sample_frac": cell["sample_frac"],
                "recall_at_1": cell["recall_at_1"],
                "p50_latency_us": cell["p50_latency_us"],
                "latency_ratio_vs_exact": cell.get("latency_ratio_vs_exact"),
            }
            break

    # HARD_PASS gate (substrate only): at sf=0.3, recall>=0.80 AND lat<=0.5*exact.
    hard_pass_03 = None
    cell_03 = per_frac.get(f"{0.3:.4f}")
    if cell_03 is not None and exact_lat > 0.0:
        hard_pass_03 = bool(
            cell_03["recall_at_1"] >= 0.80
            and cell_03["p50_latency_us"] <= 0.5 * exact_lat
        )

    # Print a tabulated summary (ASCII only).
    header = "  sample_frac | recall@1 |  p50 us  |  p95 us  | lat_ratio | recall_delta"
    sep    = "  ------------+----------+----------+----------+-----------+-------------"
    print(f"[approx_retrieve_sweep] backend={backend.name} M={M} n_queries={n_queries}")
    print(header)
    print(sep)
    for cell in sorted_fracs[::-1]:  # print high -> low frac
        lr = cell.get("latency_ratio_vs_exact")
        lr_str = f"{lr:>8.3f} " if lr is not None else "    N/A  "
        print(
            f"  {cell['sample_frac']:>10.4f} |"
            f" {cell['recall_at_1']*100:>7.2f}% |"
            f" {cell['p50_latency_us']:>8.1f} |"
            f" {cell['p95_latency_us']:>8.1f} |"
            f"{lr_str}|"
            f" {cell['recall_delta_vs_exact']*100:>+10.2f}%"
        )
    if op_pt is not None:
        print(
            f"[approx_retrieve_sweep] operating_point: sample_frac={op_pt['sample_frac']:.4f}"
            f" recall={op_pt['recall_at_1']*100:.2f}%"
            f" p50={op_pt['p50_latency_us']:.1f}us"
            f" lat_ratio={op_pt['latency_ratio_vs_exact']:.3f}"
        )
    else:
        print(
            f"[approx_retrieve_sweep] operating_point: NONE met recall >= "
            f"{op_recall_target*100:.0f}%"
        )
    if hard_pass_03 is not None:
        print(f"[approx_retrieve_sweep] HARD_PASS@sf=0.3 (recall>=0.80, lat<=0.5x): {hard_pass_03}")

    return {
        "scenario": "approx_retrieve_sweep",
        "backend": backend.name,
        "is_substrate": bool(is_substrate),
        "M": M,
        "n_queries": n_queries,
        "sample_fracs": sample_fracs,
        "op_recall_target": op_recall_target,
        "per_sample_frac": per_frac,
        "exact_p50_latency_us": exact_lat,
        "exact_recall_at_1": exact_recall,
        "operating_point": op_pt,
        "hard_pass_at_sf_0p3": hard_pass_03,
    }


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {
                "sf_0p3_recall_at_1": 0.80,
                "sf_0p3_latency_ratio_max": 0.5,
            },
            "hard_fail": {
                "sf_0p3_recall_at_1_min": 0.50,
            },
        },
        "baselines": {"hard_pass": {}, "hard_fail": {}},
    }
