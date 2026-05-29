"""Scenario 2: edit_isolation (substrate KF-2).

Store M items, edit one, measure how much the responses for the *other*
items change. Substrate gets a numeric isolation ratio bounded by 1/sqrt(N);
baselines are 0 by construction (key-isolated). The point of running this
on baselines is to make the contrast visible in the report.

Isolation ratio definition (own, since architect was non-prescriptive on
this metric for the baseline case):
    For a non-edited key j with native pre-edit confidence c_before(j) and
    post-edit confidence c_after(j), iso(j) = abs(c_after(j) - c_before(j))
    measured in the backend's native confidence units. The contrast vs the
    substrate analytic KF-2 bound is informational, not strict.
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


def setup(config: dict) -> dict:
    M = int(config.get("edit_isolation_M", 1000))
    dim = int(config.get("dim", 4096))
    N = int(config.get("N", dim))
    seed = _first_seed(config)
    rng = np.random.default_rng(seed + 1001)

    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    key_vecs = raw * 2.0 - 1.0
    key_ids = [f"ei_{i:06d}" for i in range(M)]
    values = [f"val_{i}" for i in range(M)]
    edit_idx = int(rng.integers(0, M))
    new_value = f"edited_val_{edit_idx}"

    return {
        "key_ids": key_ids,
        "key_vecs": key_vecs,
        "values": values,
        "edit_idx": edit_idx,
        "new_value": new_value,
        "M": M,
        "dim": dim,
        "N": N,
        "seed": seed,
    }


def run(backend: MemoryBackend, data: dict) -> dict:
    key_ids: list[str] = data["key_ids"]
    key_vecs: np.ndarray = data["key_vecs"]
    values: list[str] = data["values"]
    edit_idx: int = data["edit_idx"]
    new_value: str = data["new_value"]
    M = len(key_ids)
    N = int(data["N"])

    # Store all M items.
    for i in range(M):
        backend.store(key_ids[i], key_vecs[i], values[i])

    # Pre-edit baseline: native confidence on every non-edited key.
    conf_before = np.zeros(M, dtype=np.float64)
    for i in range(M):
        res = backend.retrieve(key_vecs[i], k=1)
        conf_before[i] = float(res.confidence) if res.confidence is not None else 0.0

    # Edit one key.
    t0 = time.perf_counter_ns()
    backend.edit(key_ids[edit_idx], new_value)
    t1 = time.perf_counter_ns()
    edit_wall_us = (t1 - t0) / 1000.0

    # Post-edit: confidence on every non-edited key.
    conf_after = np.zeros(M, dtype=np.float64)
    for i in range(M):
        res = backend.retrieve(key_vecs[i], k=1)
        conf_after[i] = float(res.confidence) if res.confidence is not None else 0.0

    deltas = np.abs(conf_after - conf_before)
    # Exclude the edited row.
    mask = np.ones(M, dtype=bool)
    mask[edit_idx] = False
    others = deltas[mask]

    max_iso = float(others.max()) if others.size > 0 else 0.0
    mean_iso = float(others.mean()) if others.size > 0 else 0.0

    # within_theory_frac is substrate-only (the 1/sqrt(N) bound is a substrate
    # analytic). For baselines we emit None.
    within_theory_frac: float | None
    if backend.supports_killer_features():
        threshold = 1.0 / float(np.sqrt(N))
        within_theory_frac = float((others < threshold).mean()) if others.size > 0 else 1.0
    else:
        within_theory_frac = None

    return {
        "scenario": "edit_isolation",
        "backend": backend.name,
        "n_items": M,
        "edit_idx": edit_idx,
        "max_isolation_ratio": max_iso,
        "mean_isolation_ratio": mean_iso,
        "within_theory_frac": within_theory_frac,
        "edit_wall_us": edit_wall_us,
    }


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {"max_isolation_ratio": 0.05},
            "hard_fail": {"max_isolation_ratio": 0.10},
        },
        "baselines": {
            # Trivially zero by construction.
            "hard_pass": {"max_isolation_ratio": 1e-9},
            "hard_fail": {"max_isolation_ratio": 1e-6},
        },
    }
