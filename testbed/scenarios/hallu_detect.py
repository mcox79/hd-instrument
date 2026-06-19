"""Scenario 4: hallu_detect (substrate KF-1).

For each M/N fraction in config["hallu_M_fracs"], store fresh items, then
query with 1000 OOS vectors that are NOT in the stored set. Measures the
fraction of OOS queries that produce above-threshold confidence (the
hallucination signal). Substrate is expected to be 0 at under-cap; FAISS
and friends always return their argmin and so produce 1.0 unless a
distance threshold is applied. We also report recall_at_1_on_OOS as the
killer contrast metric (should be ~0 for any sane backend, since OOS keys
have no stored ground truth).

Sub-runs handled by the scenario itself looping over M values per the
architect doc recommendation.
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
    dim = int(config.get("dim", 4096))
    N = int(config.get("N", dim))
    seed = _first_seed(config)
    n_oos = int(config.get("hallu_n_oos", 1000))
    hallu_threshold = float(config.get("hallu_threshold", 0.5))
    fracs = list(config.get("hallu_M_fracs", [0.25, 0.5, 1.0]))
    codebook_C = int(config.get("codebook_C", 4 * N))

    return {
        "dim": dim,
        "N": N,
        "seed": seed,
        "n_oos": n_oos,
        "hallu_threshold": hallu_threshold,
        "fracs": fracs,
        "codebook_C": codebook_C,
    }


def _backend_factory(backend: MemoryBackend):
    """Return a callable that produces a fresh, empty instance with the same
    config as `backend`. Used so each M-fraction sub-run gets a clean store.

    We rely on the backend exposing the constructor kwargs as attributes
    (dim, N, codebook_kind, etc). For backends that hold heavy file state,
    callers should pass a fresh persistence directory if needed; for the
    point of this scenario in-memory is enough.
    """
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
            import tempfile
            from pathlib import Path
            tmp = Path(tempfile.mkdtemp(prefix="hallu_sqlite_"))
            return cls(db_path=tmp / "scratch.db", dim=int(getattr(backend, "dim")))
        if backend.name == "chroma":
            import tempfile
            from pathlib import Path
            tmp = Path(tempfile.mkdtemp(prefix="hallu_chroma_"))
            return cls(persist_dir=tmp)
        # Fallback: try the default ctor.
        return cls()

    return make


def run(backend: MemoryBackend, data: dict) -> dict:
    dim = int(data["dim"])
    N = int(data["N"])
    seed = int(data["seed"])
    n_oos = int(data["n_oos"])
    threshold = float(data["hallu_threshold"])
    fracs = list(data["fracs"])
    codebook_C = int(data["codebook_C"])

    near_uniform_cutoff = 50.0 / float(codebook_C)
    factory = _backend_factory(backend)

    per_subrun: list[dict] = []

    for frac in fracs:
        M = max(1, int(round(frac * N)))
        rng_store = np.random.default_rng(seed + 3000 + int(frac * 10_000))
        rng_oos = np.random.default_rng(seed + 7000 + int(frac * 10_000))

        # Stored keys live in one random subspace; OOS keys live in another
        # disjoint stream by virtue of a different rng seed offset.
        stored_vecs = _make_vecs(rng_store, M, dim)
        stored_ids = [f"hd_f{int(frac * 1000):04d}_{i:06d}" for i in range(M)]
        oos_vecs = _make_vecs(rng_oos, n_oos, dim)

        # Fresh backend per sub-run so each M is measured independently.
        sub_backend = factory()
        for i in range(M):
            sub_backend.store(stored_ids[i], stored_vecs[i], f"v_{i}")

        oos_conf: list[float] = []
        above_thresh = 0
        near_uniform = 0
        hits_on_oos = 0
        stored_id_set = set(stored_ids)

        for q in oos_vecs:
            res = sub_backend.retrieve(q, k=1)
            c = float(res.confidence) if res.confidence is not None else 0.0
            oos_conf.append(c)
            if c >= threshold:
                above_thresh += 1
            if res.near_uniform_flag or c < near_uniform_cutoff:
                near_uniform += 1
            # recall_at_1 on OOS: should be 0 because OOS keys were never stored
            # (we count any non-None returned id as a "false positive" hit).
            if res.key_id is not None and res.key_id in stored_id_set:
                hits_on_oos += 1

        mean_conf = float(np.mean(oos_conf)) if oos_conf else 0.0
        per_subrun.append({
            "M_over_N": float(frac),
            "M": M,
            "mean_oos_max_conf": mean_conf,
            "above_thresh_frac": above_thresh / n_oos if n_oos else 0.0,
            "near_uniform_frac": near_uniform / n_oos if n_oos else 0.0,
            "recall_at_1_on_OOS": hits_on_oos / n_oos if n_oos else 0.0,
        })

    # Top-level aggregate across sub-runs (worst-cell convention).
    max_above_thresh = max((s["above_thresh_frac"] for s in per_subrun), default=0.0)
    max_mean_conf = max((s["mean_oos_max_conf"] for s in per_subrun), default=0.0)

    return {
        "scenario": "hallu_detect",
        "backend": backend.name,
        "threshold": threshold,
        "near_uniform_cutoff": near_uniform_cutoff,
        "per_subrun": per_subrun,
        "max_above_thresh_frac": max_above_thresh,
        "max_mean_oos_max_conf": max_mean_conf,
    }


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {"above_thresh_frac": 0.0, "mean_oos_max_conf": 0.001},
            "hard_fail": {"above_thresh_frac_strictly_gt": 0.0},
        },
        "baselines": {
            # Baselines structurally fail KF-1; this is the contrast.
            "hard_pass": {"recall_at_1_on_OOS": 0.01},
            "hard_fail": {"recall_at_1_on_OOS": 0.05},
        },
    }
