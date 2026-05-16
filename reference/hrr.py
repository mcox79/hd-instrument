"""Reference HRR: naive circular-convolution variant, read-only oracle for verification."""

from __future__ import annotations

import torch


def make_atom(n: int, generator: torch.Generator) -> torch.Tensor:
    """HRR atom: float32, gaussian with std 1/sqrt(n)."""
    raise NotImplementedError("Week 1")


def bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """HRR bind: circular convolution via FFT."""
    raise NotImplementedError("Week 1")


def unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """HRR unbind: circular correlation via FFT and conjugate."""
    raise NotImplementedError("Week 1")


def bundle(vectors: torch.Tensor) -> torch.Tensor:
    """HRR bundle: sum then normalize the whole vector."""
    raise NotImplementedError("Week 1")


def similarity(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """HRR similarity: cosine similarity."""
    raise NotImplementedError("Week 1")
