"""Scenario 3: deletion_verify (substrate TCFT).

Store M items, then issue K random delete probes. For each probe, record
the substrate's variance ratio certificate (None for baselines), whether
post-delete retrieve returns a different key_id, and wall-clock latency.

HARD_PASS substrate: mean_var_ratio < 0.10.
HARD_FAIL substrate: mean_var_ratio >= 0.30.
Baselines: deletion is structural; erase_success_rate should be ~1.0.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from testbed.api import MemoryBackend


_DEFAULT_K_PROBES = 16


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
    M = int(config.get("deletion_M", 512))
    dim = int(config.get("dim", 4096))
    seed = _first_seed(config)
    k_probes = int(config.get("deletion_k_probes", _DEFAULT_K_PROBES))
    k_probes = min(k_probes, M)
    rng = np.random.default_rng(seed + 2002)

    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    key_vecs = raw * 2.0 - 1.0
    key_ids = [f"dv_{i:06d}" for i in range(M)]
    values = [f"val_{i}" for i in range(M)]

    probe_indices = rng.choice(M, size=k_probes, replace=False).tolist()

    return {
        "key_ids": key_ids,
        "key_vecs": key_vecs,
        "values": values,
        "probe_indices": probe_indices,
        "M": M,
        "dim": dim,
        "seed": seed,
        "k_probes": k_probes,
    }


def run(backend: MemoryBackend, data: dict) -> dict:
    key_ids: list[str] = data["key_ids"]
    key_vecs: np.ndarray = data["key_vecs"]
    values: list[str] = data["values"]
    probe_indices: list[int] = data["probe_indices"]
    M = len(key_ids)

    for i in range(M):
        backend.store(key_ids[i], key_vecs[i], values[i])

    var_ratios: list[float] = []
    erase_flags: list[int] = []
    delete_times_us: list[float] = []

    for idx in probe_indices:
        kid = key_ids[idx]
        kvec = key_vecs[idx]
        t0 = time.perf_counter_ns()
        cert = backend.delete(kid)
        t1 = time.perf_counter_ns()
        delete_times_us.append((t1 - t0) / 1000.0)

        if cert.var_ratio is not None:
            var_ratios.append(float(cert.var_ratio))

        post = backend.retrieve(kvec, k=1)
        returned_different = (post.key_id is None) or (post.key_id != kid)
        erase_flags.append(1 if (returned_different or cert.erased) else 0)

    mean_var_ratio: float | None
    if var_ratios:
        mean_var_ratio = float(np.mean(var_ratios))
    else:
        mean_var_ratio = None

    erase_success_rate = float(np.mean(erase_flags)) if erase_flags else 0.0

    return {
        "scenario": "deletion_verify",
        "backend": backend.name,
        "n_items": M,
        "n_probes": len(probe_indices),
        "mean_var_ratio": mean_var_ratio,
        "var_ratio_samples": var_ratios[:16],
        "erase_success_rate": erase_success_rate,
        "p50_delete_us": _percentile(delete_times_us, 50),
        "p95_delete_us": _percentile(delete_times_us, 95),
    }


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {"mean_var_ratio": 0.10, "erase_success_rate": 0.99},
            "hard_fail": {"mean_var_ratio": 0.30},
        },
        "baselines": {
            "hard_pass": {"erase_success_rate": 0.99},
            "hard_fail": {"erase_success_rate": 0.50},
        },
    }
