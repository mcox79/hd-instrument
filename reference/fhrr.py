"""Reference FHRR: naive implementation, read-only oracle for verification."""

from __future__ import annotations

import torch


def make_atom(n: int, generator: torch.Generator) -> torch.Tensor:
    """FHRR atom: complex64 unit-magnitude with uniformly random phases."""
    raise NotImplementedError("Week 1")


def bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """FHRR bind: elementwise complex multiplication."""
    raise NotImplementedError("Week 1")


def unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """FHRR unbind: elementwise multiplication by complex conjugate of b."""
    raise NotImplementedError("Week 1")


def bundle(vectors: torch.Tensor) -> torch.Tensor:
    """FHRR bundle: sum, then renormalize each component to unit magnitude."""
    raise NotImplementedError("Week 1")


def similarity(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """FHRR similarity: real part of normalized inner product."""
    raise NotImplementedError("Week 1")
