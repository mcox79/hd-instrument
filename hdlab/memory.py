"""Cleanup memory: stores named atoms; lookup is gated by the attention modulator.

Cosine-floor bound (Skunkworks landed-VET 2026-06-26; meta::T3/META_substrate_tracks_
KNN_cosine_floor_within_0p007_across_eight_construction_param_combinations): the
similarity-based cleanup recall implemented here is bounded ABOVE by exhaustive-
cosine-KNN recall on the same key distribution (proven 8/8 in smoke at M=2000
pythia-160m windows 16-64; delta(knn - sub) in [+0.0006, +0.0067] all non-negative;
substrate NEVER beats KNN within this regime). The bound is ONE-SIDED (above) and
REGIME-BOUNDED: the cosine-physics ceiling is itself regime-dependent. Short-LM-
window (<=64 tokens) at M=2000 with pythia-160m keeps recall@1 <= 0.158 -- below
chain-grade band -- per meta::T3/META_cosine_physics_floor_on_short_LM_window_keys.
Natural-distribution keys at M=10k+ with pythia-2.8b reach chain-grade recall per
partition_routing M=10M / fly-LSH M=10k / KV-learned M=10k chain-grade ledger
entries. For short-LM-window regimes where the cosine ceiling is below chain-
grade, the productized high-M path is NON-COSINE mechanism (refuse-gate / sparse-
tag retrieval / sparse-fan-in / learned-projection metric), NOT geometric rescue
of cosine-based dense cleanup (per meta::T3/META_when_substrate_tracks_an_external_
baseline_within_smoke_noise_band_AND_baseline_itself_is_low_the_chain_grade_path_is_
baseline_replacement_not_baseline_rescue, the Fix #26 pre-dispatch matcher discipline).
"""

from __future__ import annotations

import time

import torch

from . import atoms, modulators, tracing


class Codebook:
    """Named hypervectors with similarity-based cleanup."""

    def __init__(self, n: int, dtype: torch.dtype) -> None:
        self.n = n
        self.dtype = dtype
        self._names: list[str] = []
        self._vectors: list[torch.Tensor] = []

    def __len__(self) -> int:
        return len(self._names)

    def add(self, name: str, vector: torch.Tensor) -> None:
        """Register a named atom."""
        t0 = time.perf_counter_ns()
        if vector.shape != (self.n,):
            raise ValueError(f"Expected shape ({self.n},), got {tuple(vector.shape)}")
        if vector.dtype != self.dtype:
            raise ValueError(f"Expected dtype {self.dtype}, got {vector.dtype}")
        self._names.append(name)
        self._vectors.append(vector)
        tracing.emit(
            "memory.add",
            {"name": name, "shape": list(vector.shape)},
            None,
            elapsed_ns=time.perf_counter_ns() - t0,
        )

    def lookup(self, query: torch.Tensor) -> tuple[str | None, float]:
        """Closest atom and similarity score; returns (None, score) when below the attention threshold."""
        t0 = time.perf_counter_ns()
        if not self._vectors:
            raise ValueError("Cannot lookup in an empty Codebook")
        stacked = torch.stack(self._vectors)
        sims = atoms.similarity(query, stacked)
        best = int(sims.argmax())
        score = float(sims[best])
        threshold = modulators.current().attention
        name: str | None = self._names[best] if score >= threshold else None
        tracing.emit(
            "memory.lookup",
            {"query_shape": list(query.shape), "k": len(self._vectors)},
            {"name": name, "score": score},
            elapsed_ns=time.perf_counter_ns() - t0,
        )
        return name, score
