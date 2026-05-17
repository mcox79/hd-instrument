"""Sparse VSA (k-of-N bipolar block code variant) reference implementation.

Sparse VSA atoms have only `k_active` non-zero components out of N, each set to +/- 1. Density
d = k_active / N typically in [0.01, 0.1]. Binding is elementwise multiplication on the
sparse representation. Bundling sums the dense form, then re-sparsifies via top-k_active by
magnitude. This is a simplified variant of work by Laiho, Frady, Schlegel, and others.

Hardware appeal: sparse representations need fewer bits to store (just indices + signs);
binding is sparse-vector multiply; cleanup can use sparse hashing tricks for faster NN search.
"""

from __future__ import annotations

import torch


def make_atom(n: int, k_active: int, generator: torch.Generator) -> torch.Tensor:
    """Sparse atom: k_active non-zero +/-1 components scattered at random positions.

    Returned as a dense int8 tensor for simplicity; production impls would use indices+signs.
    """
    out = torch.zeros(n, dtype=torch.int8)
    # Pick k_active random positions without replacement
    positions = torch.randperm(n, generator=generator)[:k_active]
    # Random +/-1 signs
    signs = (2 * torch.randint(0, 2, (k_active,), generator=generator) - 1).to(torch.int8)
    out[positions] = signs
    return out


def bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Elementwise multiplication. Non-zero only where BOTH a and b are non-zero, so
    binding tends to reduce sparsity (more zeros) by a factor depending on overlap.
    """
    return (a * b).to(torch.int8)


def unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Same as bind for bipolar +/-1 multiplication (self-inverse on the overlap)."""
    return (c * b).to(torch.int8)


def bundle(vectors: torch.Tensor, k_active: int) -> torch.Tensor:
    """Sum + top-k re-sparsify: keep the k_active components with the largest absolute sum.
    Their signs are determined by the column sum's sign.
    """
    s = vectors.to(torch.int32).sum(dim=0)
    # Top k_active by absolute magnitude
    top_indices = s.abs().argsort(descending=True)[:k_active]
    out = torch.zeros(s.shape[0], dtype=torch.int8)
    selected = s[top_indices]
    out[top_indices] = torch.where(selected >= 0, torch.ones_like(selected, dtype=torch.int8), torch.full_like(selected, -1, dtype=torch.int8))
    return out


def similarity(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Normalized overlap on +/-1 bipolar vectors. Range: [-1, 1] for equal-density atoms.

    For sparse vectors with k_active non-zero components each, the maximum positive overlap
    (a == b at every non-zero position) is k_active / N where N is the vector length.
    """
    n = a.shape[-1]
    return (a.to(torch.float32) * b.to(torch.float32)).sum(dim=-1) / n
