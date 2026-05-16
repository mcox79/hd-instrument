"""Cleanup memory: stores named atoms and supports nearest-neighbor retrieval."""

from __future__ import annotations

import torch

from . import atoms, tracing


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
        if vector.shape != (self.n,):
            raise ValueError(f"Expected shape ({self.n},), got {tuple(vector.shape)}")
        if vector.dtype != self.dtype:
            raise ValueError(f"Expected dtype {self.dtype}, got {vector.dtype}")
        self._names.append(name)
        self._vectors.append(vector)
        tracing.emit("memory.add", {"name": name, "shape": list(vector.shape)}, None)

    def lookup(self, query: torch.Tensor) -> tuple[str, float]:
        """Closest atom name and similarity score."""
        if not self._vectors:
            raise ValueError("Cannot lookup in an empty Codebook")
        stacked = torch.stack(self._vectors)
        sims = atoms.similarity(query, stacked)
        best = int(sims.argmax())
        score = float(sims[best])
        result = (self._names[best], score)
        tracing.emit(
            "memory.lookup",
            {"query_shape": list(query.shape), "k": len(self._vectors)},
            {"name": result[0], "score": result[1]},
        )
        return result
