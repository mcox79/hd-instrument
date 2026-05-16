"""Superposition (bundling) of hypervectors."""

from __future__ import annotations

import torch


def bundle(vectors: torch.Tensor) -> torch.Tensor:
    """Superpose (k, n) -> (n,). FHRR: sum, renormalize each component. HRR: sum, normalize whole vector."""
    raise NotImplementedError("Week 1")
