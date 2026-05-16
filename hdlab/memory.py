"""Cleanup memory: stores named atoms and supports nearest-neighbor retrieval."""

from __future__ import annotations

import torch


class Codebook:
    """Named hypervectors with similarity-based cleanup."""

    def __init__(self, n: int, dtype: torch.dtype) -> None:
        raise NotImplementedError("Week 1")

    def add(self, name: str, vector: torch.Tensor) -> None:
        """Register a named atom."""
        raise NotImplementedError("Week 1")

    def lookup(self, query: torch.Tensor) -> tuple[str, float]:
        """Closest atom name and similarity score."""
        raise NotImplementedError("Week 1")
