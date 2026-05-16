"""Superposition (bundling) of hypervectors."""

from __future__ import annotations

import torch

from . import tracing


def bundle(vectors: torch.Tensor) -> torch.Tensor:
    """Superpose (k, n) -> (n,). FHRR: sum, renormalize each component. HRR: sum, L2-normalize."""
    if vectors.is_complex():
        s = vectors.sum(dim=0)
        mag = s.abs()
        mag = torch.where(mag > 0, mag, torch.ones_like(mag))
        out = s / mag.to(s.dtype)
    else:
        s = vectors.sum(dim=0)
        norm = s.norm()
        out = s / norm if float(norm) > 0 else s
    tracing.emit("bundling.bundle", {"shape": list(vectors.shape)}, out)
    return out
