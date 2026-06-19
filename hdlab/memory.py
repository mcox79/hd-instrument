"""Cleanup memory: stores named atoms; lookup is gated by the attention modulator."""

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
