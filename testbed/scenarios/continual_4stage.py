"""Scenario 5: continual_4stage.

Light Bet B 4-stage CL probe. Split M into 4 equal batches A, B, C, D.
Store A; measure ret_A. Store B; remeasure ret_A. Store C; remeasure A and
B. Store D; remeasure A, B, and C. Substrate's expected band is
ret_A_after_D in [0.65, 0.81]; baselines should sit at ~1.0 by exact key
isolation. The CONTRAST is the point.
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


def _make_vecs(rng: np.random.Generator, M: int, dim: int) -> np.ndarray:
    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    return raw * 2.0 - 1.0


def setup(config: dict) -> dict:
    M_total = int(config.get("continual_M", 800))
    # Round down to multiple of 4.
    M = (M_total // 4) * 4
    if M < 4:
        M = 4
    dim = int(config.get("dim", 4096))
    seed = _first_seed(config)
    rng = np.random.default_rng(seed + 4004)

    per_batch = M // 4
    batches: dict[str, dict[str, Any]] = {}
    for tag_idx, tag in enumerate(("A", "B", "C", "D")):
        vecs = _make_vecs(rng, per_batch, dim)
        ids = [f"cl_{tag}_{i:06d}" for i in range(per_batch)]
        vals = [f"{tag}_val_{i}" for i in range(per_batch)]
        batches[tag] = {
            "ids": ids,
            "vecs": vecs,
            "values": vals,
        }
    return {
        "batches": batches,
        "M_per_batch": per_batch,
        "dim": dim,
        "seed": seed,
        "M_total": per_batch * 4,
    }


def _measure_recall(backend: MemoryBackend, batch: dict[str, Any]) -> float:
    ids = batch["ids"]
    vecs = batch["vecs"]
    if not ids:
        return 0.0
    hits = 0
    for i, kid in enumerate(ids):
        res = backend.retrieve(vecs[i], k=1)
        if res.key_id == kid:
            hits += 1
    return hits / len(ids)


def _store_batch(backend: MemoryBackend, batch: dict[str, Any]) -> None:
    ids = batch["ids"]
    vecs = batch["vecs"]
    vals = batch["values"]
    for i, kid in enumerate(ids):
        backend.store(kid, vecs[i], vals[i])


def run(backend: MemoryBackend, data: dict) -> dict:
    batches = data["batches"]
    A, B, C, D = batches["A"], batches["B"], batches["C"], batches["D"]

    _store_batch(backend, A)
    ret_A_after_A = _measure_recall(backend, A)

    _store_batch(backend, B)
    ret_A_after_B = _measure_recall(backend, B if False else A)
    ret_B_after_B = _measure_recall(backend, B)

    _store_batch(backend, C)
    ret_A_after_C = _measure_recall(backend, A)
    ret_B_after_C = _measure_recall(backend, B)
    ret_C_after_C = _measure_recall(backend, C)

    _store_batch(backend, D)
    ret_A_after_D = _measure_recall(backend, A)
    ret_B_after_D = _measure_recall(backend, B)
    ret_C_after_D = _measure_recall(backend, C)
    ret_D_after_D = _measure_recall(backend, D)

    return {
        "scenario": "continual_4stage",
        "backend": backend.name,
        "M_per_batch": data["M_per_batch"],
        "M_total": data["M_total"],
        "ret_A_after_A": ret_A_after_A,
        "ret_A_after_B": ret_A_after_B,
        "ret_A_after_C": ret_A_after_C,
        "ret_A_after_D": ret_A_after_D,
        "ret_B_after_B": ret_B_after_B,
        "ret_B_after_C": ret_B_after_C,
        "ret_B_after_D": ret_B_after_D,
        "ret_C_after_C": ret_C_after_C,
        "ret_C_after_D": ret_C_after_D,
        "ret_D_after_D": ret_D_after_D,
    }


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {"ret_A_after_D": 0.65},
            "hard_fail": {"ret_A_after_D": 0.40},
        },
        "baselines": {
            "hard_pass": {"ret_A_after_D": 0.99},
            "hard_fail": {"ret_A_after_D": 0.80},
        },
    }
