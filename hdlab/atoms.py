"""FHRR and HRR atom generation, similarity, and batch operations."""

from __future__ import annotations

import torch


def make_atom_fhrr(n: int, generator: torch.Generator) -> torch.Tensor:
    """FHRR atom of dimension n: complex64 unit-magnitude with uniform random phases. Shape: (n,)."""
    raise NotImplementedError("Week 1")


def make_atom_hrr(n: int, generator: torch.Generator) -> torch.Tensor:
    """HRR atom of dimension n: float32 gaussian with std 1/sqrt(n). Shape: (n,)."""
    raise NotImplementedError("Week 1")


def make_atoms(
    k: int, n: int, dtype: torch.dtype, generator: torch.Generator
) -> torch.Tensor:
    """Batch of k atoms. Shape: (k, n)."""
    raise NotImplementedError("Week 1")


def similarity(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Real part of normalized inner product (FHRR) or cosine similarity (HRR)."""
    raise NotImplementedError("Week 1")
