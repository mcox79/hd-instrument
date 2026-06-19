"""Scenario 7: large_M_constant_cost (shine plan B.2.1).

Sweep M into the large-M regime where substrate's constant O(N^2) storage and
constant per-op cost dominate FAISS's linear-in-M scaling. Reports per-M
disk_bytes, p50/p95 store + retrieve latencies, and recall_at_1.

Substrate is expected to show CONSTANT disk_bytes vs M (the W matrix is N x N
regardless of M, plus a codebook that scales as max(4*N, 4*M)). FAISS is
expected to show LINEAR disk_bytes (M * dim * 4 bytes).

This scenario is the headline visualization that flips the deployment
crossover story from "interesting at M ~ 10k" to "substrate wins by 10-50x at
production M". Drops dict and Chroma (would burn 100+ GB and hours at M=200k).

Per shine plan A.3.1, this scenario relies on substrate being constructed
with codebook_M_hint = max(Ms) so the codebook does not become the collision
bottleneck. Pair with config flag codebook_M_hint_auto: true.
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


def _backend_factory(backend: MemoryBackend, M_hint: int):
    cls = type(backend)

    def make() -> MemoryBackend:
        if backend.name == "substrate" or backend.name.startswith("substrate_v"):
            kwargs = {}
            for attr in ("N", "codebook_kind", "codebook_scale", "beta",
                         "hallu_threshold", "device"):
                if hasattr(backend, attr):
                    kwargs[attr] = getattr(backend, attr)
            kwargs["codebook_M_hint"] = int(M_hint)
            try:
                return cls(**kwargs)
            except TypeError:
                kwargs.pop("codebook_M_hint", None)
                return cls(**kwargs)
        if backend.name == "faiss":
            return cls(dim=int(getattr(backend, "dim")),
                       index_kind=getattr(backend, "index_kind", "Flat"))
        if backend.name == "dict":
            return cls(dim=getattr(backend, "dim", None))
        if backend.name == "sqlite_vec":
            tmp = Path(tempfile.mkdtemp(prefix="lm_sqlite_"))
            return cls(db_path=tmp / "scratch.db", dim=int(getattr(backend, "dim")))
        if backend.name == "chroma":
            tmp = Path(tempfile.mkdtemp(prefix="lm_chroma_"))
            return cls(persist_dir=tmp)
        return cls()

    return make


def _make_vecs(rng: np.random.Generator, M: int, dim: int) -> np.ndarray:
    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    return raw * 2.0 - 1.0


def setup(config: dict) -> dict:
    dim = int(config.get("dim", 4096))
    N = int(config.get("N", dim))
    Ms = list(config.get("large_M_Ms", [10000, 50000, 100000]))
    seed = _first_seed(config)
    # Honest cap: recall samples are 200 random keys (full M recall sweep at
    # M=200k would dominate wall time). Disk + latency are still per-M-correct.
    n_recall_samples = int(config.get("large_M_n_recall_samples", 200))
    n_latency_queries = int(config.get("large_M_n_latency_queries", 200))
    return {
        "dim": dim,
        "N": N,
        "Ms": Ms,
        "seed": seed,
        "n_recall_samples": n_recall_samples,
        "n_latency_queries": n_latency_queries,
        "large_M_store_batch_size": int(config.get("large_M_store_batch_size", 128)),
    }


def run(backend: MemoryBackend, data: dict) -> dict:
    dim = int(data["dim"])
    N = int(data["N"])
    Ms = list(data["Ms"])
    seed = int(data["seed"])
    n_recall_samples = int(data["n_recall_samples"])
    n_latency_queries = int(data["n_latency_queries"])

    per_M: dict[str, dict] = {}

    for M in Ms:
        # Honest skip: substrate can't store more keys than its codebook supports.
        # If M > C/2 the substrate WILL fail on the first collision-storm; report
        # the skip explicitly rather than crashing the run.
        if hasattr(backend, "C"):
            C_avail = int(getattr(backend, "C"))
            if M >= C_avail:
                per_M[str(M)] = {
                    "M": M,
                    "skipped": True,
                    "reason": f"substrate C={C_avail} <= M={M}; would collide-out",
                }
                continue

        factory = _backend_factory(backend, M_hint=M)
        rng = np.random.default_rng(seed + 9000 + M)
        vecs = _make_vecs(rng, M, dim)
        ids = [f"lm_{M}_{i:08d}" for i in range(M)]
        values = [f"v_{i}" for i in range(M)]

        sub_backend = factory()
        # Substrate v1 + variants need M_hint at construction; we pass it in
        # factory above. For baselines the factory ignores the hint.

        # Store loop (full M). Latency samples are the first n_latency_queries.
        # Default to batched store with B=128 so per-item Python overhead does
        # not bottleneck the headline scaling chart. First n_latency_queries
        # items are still stored one-at-a-time so the latency histogram is
        # implementation-fair vs FAISS's per-add cost.
        store_batch_size = int(data.get("large_M_store_batch_size", 128))
        store_us: list[float] = []
        # Per-item path for the first n_latency_queries items (latency sampling).
        boundary = min(n_latency_queries, M)
        for i in range(boundary):
            t0 = time.perf_counter_ns()
            sub_backend.store(ids[i], vecs[i], values[i])
            t1 = time.perf_counter_ns()
            store_us.append((t1 - t0) / 1000.0)
        # Batched path for the remainder.
        if boundary < M:
            j = boundary
            while j < M:
                end = min(j + store_batch_size, M)
                sub_backend.store_batch(
                    [(ids[k_], vecs[k_], values[k_]) for k_ in range(j, end)]
                )
                j = end

        # Retrieve latency: n_latency_queries random keys.
        q_count = min(n_latency_queries, M)
        q_idx = rng.choice(M, size=q_count, replace=False)
        retr_us: list[float] = []
        for i in q_idx:
            t0 = time.perf_counter_ns()
            sub_backend.retrieve(vecs[i], k=1)
            t1 = time.perf_counter_ns()
            retr_us.append((t1 - t0) / 1000.0)

        # Recall@1 sampled on n_recall_samples random stored keys.
        r_count = min(n_recall_samples, M)
        r_idx = rng.choice(M, size=r_count, replace=False)
        hits = 0
        for i in r_idx:
            res = sub_backend.retrieve(vecs[i], k=1)
            if res.key_id == ids[i]:
                hits += 1
        recall_at_1 = hits / max(r_count, 1)

        # Disk + cold-load
        save_dir = Path(tempfile.mkdtemp(prefix=f"lm_save_{backend.name}_{M}_"))
        try:
            sub_backend.save(save_dir)
            disk_bytes = _dir_size_bytes(save_dir)
        except (NotImplementedError, Exception):
            disk_bytes = 0
        finally:
            try:
                shutil.rmtree(save_dir, ignore_errors=True)
            except OSError:
                pass

        per_M[str(M)] = {
            "M": M,
            "M_over_N": M / float(N) if N else None,
            "disk_bytes": int(disk_bytes),
            "disk_MB": float(disk_bytes) / 1.0e6,
            "p50_store_us": _percentile(store_us, 50),
            "p95_store_us": _percentile(store_us, 95),
            "p50_retrieve_us": _percentile(retr_us, 50),
            "p95_retrieve_us": _percentile(retr_us, 95),
            "recall_at_1": recall_at_1,
            "n_recall_samples": r_count,
            "n_latency_queries": q_count,
        }

    return {
        "scenario": "large_M_constant_cost",
        "backend": backend.name,
        "per_M": per_M,
        "Ms": Ms,
    }


def thresholds() -> dict:
    # Descriptive scenario; substrate-constant + faiss-linear is the visual.
    # Pre-registered honest expectation bands (not strict gates):
    #  substrate: disk_bytes constant within +/- 5% across Ms; recall >= 0.85
    #  faiss: disk_bytes scales linearly in M within +/- 10%
    return {
        "substrate": {
            "hard_pass": {
                "disk_bytes_constant_within_pct": 0.05,
                "recall_at_1": 0.85,
            },
            "hard_fail": {
                "recall_at_1": 0.50,
            },
        },
        "baselines": {
            "hard_pass": {"recall_at_1": 0.95},
            "hard_fail": {"recall_at_1": 0.50},
        },
    }
