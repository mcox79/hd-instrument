"""Reference FHRR: naive implementation, read-only oracle for verification."""

from __future__ import annotations

import math

import torch


def make_atom(n: int, generator: torch.Generator) -> torch.Tensor:
    """FHRR atom: complex64 unit-magnitude with uniformly random phases."""
    phases = torch.rand(n, generator=generator) * (2.0 * math.pi)
    return torch.complex(torch.cos(phases), torch.sin(phases)).to(torch.complex64)


def bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """FHRR bind: elementwise complex multiplication."""
    return a * b


def unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """FHRR unbind: elementwise multiplication by complex conjugate of b."""
    return c * b.conj()


def bundle(vectors: torch.Tensor) -> torch.Tensor:
    """FHRR bundle: sum, then renormalize each component to unit magnitude. Shape (k, n) -> (n,)."""
    s = vectors.sum(dim=0)
    mag = s.abs()
    mag = torch.where(mag > 0, mag, torch.ones_like(mag))
    return s / mag.to(s.dtype)


def similarity(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """FHRR similarity: real part of normalized inner product (last-dim broadcasting)."""
    n = a.shape[-1]
    return (a * b.conj()).sum(dim=-1).real / n
