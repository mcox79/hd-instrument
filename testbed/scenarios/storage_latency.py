"""Scenario 6: storage_latency.

Sweep M in config["storage_latency_Ms"], measure store latency, retrieve
latency, on-disk footprint after save(), and cold-load wall. Descriptive
only; no HARD_PASS / HARD_FAIL bands.
"""

from __future__ import annotations

import shutil
import tempfile
import time
from pathlib import Path
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


def _dir_size_bytes(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for p in path.rglob("*"):
        try:
            if p.is_file():
                total += p.stat().st_size
        except OSError:
            continue
    return total


def _backend_factory(backend: MemoryBackend):
    cls = type(backend)

    def make() -> MemoryBackend:
        if backend.name == "substrate":
            kwargs = {}
            for attr in ("N", "codebook_kind", "codebook_scale", "beta",
                         "hallu_threshold", "device"):
                if hasattr(backend, attr):
                    kwargs[attr] = getattr(backend, attr)
            return cls(**kwargs)
        if backend.name == "faiss":
            return cls(dim=int(getattr(backend, "dim")),
                       index_kind=getattr(backend, "index_kind", "Flat"))
        if backend.name == "dict":
            return cls(dim=getattr(backend, "dim", None))
        if backend.name == "sqlite_vec":
            tmp = Path(tempfile.mkdtemp(prefix="lat_sqlite_"))
            return cls(db_path=tmp / "scratch.db", dim=int(getattr(backend, "dim")))
        if backend.name == "chroma":
            tmp = Path(tempfile.mkdtemp(prefix="lat_chroma_"))
            return cls(persist_dir=tmp)
        return cls()

    return make


def _make_vecs(rng: np.random.Generator, M: int, dim: int) -> np.ndarray:
    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    return raw * 2.0 - 1.0


def setup(config: dict) -> dict:
    dim = int(config.get("dim", 4096))
    Ms = list(config.get("storage_latency_Ms", [1000, 5000, 10000]))
    seed = _first_seed(config)
    n_queries = int(config.get("storage_latency_n_queries", 1000))
    return {
        "dim": dim,
        "Ms": Ms,
        "seed": seed,
        "n_queries": n_queries,
    }


def run(backend: MemoryBackend, data: dict) -> dict:
    dim = int(data["dim"])
    Ms = list(data["Ms"])
    seed = int(data["seed"])
    n_queries = int(data["n_queries"])
    factory = _backend_factory(backend)

    per_M: dict[str, dict] = {}

    for M in Ms:
        rng = np.random.default_rng(seed + 5000 + M)
        vecs = _make_vecs(rng, M, dim)
        ids = [f"sl_{M}_{i:06d}" for i in range(M)]

        sub_backend = factory()

        # Store loop
        store_us: list[float] = []
        for i in range(M):
            t0 = time.perf_counter_ns()
            sub_backend.store(ids[i], vecs[i], f"v_{i}")
            t1 = time.perf_counter_ns()
            store_us.append((t1 - t0) / 1000.0)

        # Retrieve loop (n_queries random keys with replacement)
        q_count = min(n_queries, M)
        q_idx = rng.choice(M, size=q_count, replace=False)
        retr_us: list[float] = []
        for i in q_idx:
            t0 = time.perf_counter_ns()
            sub_backend.retrieve(vecs[i], k=1)
            t1 = time.perf_counter_ns()
            retr_us.append((t1 - t0) / 1000.0)

        # Save + cold-load
        save_dir = Path(tempfile.mkdtemp(prefix=f"sl_save_{backend.name}_{M}_"))
        try:
            sub_backend.save(save_dir)
            disk_bytes = _dir_size_bytes(save_dir)

            cold = factory()
            t0 = time.perf_counter_ns()
            try:
                cold.load(save_dir)
                cold_load_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
            except (FileNotFoundError, NotImplementedError, Exception):
                cold_load_ms = None
        except (NotImplementedError, Exception):
            disk_bytes = 0
            cold_load_ms = None
        finally:
            try:
                shutil.rmtree(save_dir, ignore_errors=True)
            except OSError:
                pass

        per_M[str(M)] = {
            "M": M,
            "disk_bytes": int(disk_bytes),
            "p50_store_us": _percentile(store_us, 50),
            "p95_store_us": _percentile(store_us, 95),
            "p50_retrieve_us": _percentile(retr_us, 50),
            "p95_retrieve_us": _percentile(retr_us, 95),
            "cold_load_ms": cold_load_ms,
        }

    return {
        "scenario": "storage_latency",
        "backend": backend.name,
        "per_M": per_M,
        "Ms": Ms,
    }


def thresholds() -> dict:
    # Descriptive scenario; no pre-registered bands.
    return {
        "substrate": {"hard_pass": {}, "hard_fail": {}},
        "baselines": {"hard_pass": {}, "hard_fail": {}},
    }
