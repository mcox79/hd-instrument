"""Reference implementation of VTB (Vector-Derived Transformation Binding) per Gosmann 2019.

VTB defines binding via a block-diagonal matrix. Given n = d^2 dimensions, we reshape y into
an m x m matrix V_y' (where m = d = sqrt(n)) and apply V_y' independently to each of the m
chunks of x.

Construction:
    V_y' = (n^(1/4)) * reshape(y, m, m)
    bind(x, y): split x into m chunks of size m, apply V_y' to each, concatenate
    unbind(z, y): apply V_y'.T to each chunk (approx inverse since V_y' is approx orthogonal)

The scaling factor n^(1/4) is chosen so that for HRR-distributed atoms (std=1/sqrt(n)),
V_y'.T @ V_y' is approximately the identity matrix. Off-diagonal error scales as n^(-1/4).

Key property: matrix multiplication preserves vector norms in expectation (unlike circular
convolution, where magnitude drifts at depth). This is why VTB shows better stack-depth
recovery than HRR per Gosmann.

bundle: standard whole-vector L2 sum normalization.
similarity: cosine.
"""

from __future__ import annotations

import math

import torch


def _check_square_dim(n: int) -> int:
    m = int(math.isqrt(n))
    if m * m != n:
        raise ValueError(f"VTB requires n to be a perfect square, got n={n}")
    return m


def make_atom(n: int, generator: torch.Generator) -> torch.Tensor:
    """HRR-style atom: float32, gaussian with std 1/sqrt(n)."""
    _check_square_dim(n)
    return torch.randn(n, generator=generator, dtype=torch.float32) / math.sqrt(n)


def bind(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Apply V_y' (d'-by-d' block derived from y) to each of m chunks of x.

    Implementation: x.reshape(m, m) has chunks as rows. Apply V_y'.T on the right so each row
    of the result is (V_y' @ chunk_i^T)^T = chunk_i @ V_y'.T. This is the block-diagonal
    multiplication done with one m x m matmul.
    """
    n = y.shape[-1]
    m = _check_square_dim(n)
    scale = n ** 0.25
    V_y = y.reshape(m, m) * scale
    X = x.reshape(m, m)
    Z = X @ V_y.T
    return Z.reshape(n)


def unbind(z: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Apply V_y'^T (approximate inverse) to each chunk of z."""
    n = y.shape[-1]
    m = _check_square_dim(n)
    scale = n ** 0.25
    V_y = y.reshape(m, m) * scale
    Z = z.reshape(m, m)
    X = Z @ V_y
    return X.reshape(n)


def bundle(vectors: torch.Tensor) -> torch.Tensor:
    """HRR-style bundle: sum + whole-vector L2 normalize."""
    s = vectors.sum(dim=0)
    norm = s.norm()
    if float(norm) > 0:
        return s / norm
    return s


def similarity(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Cosine similarity, last-dim broadcasting."""
    dot = (a * b).sum(dim=-1)
    na = a.norm(dim=-1)
    nb = b.norm(dim=-1)
    denom = na * nb
    safe = torch.where(denom > 0, denom, torch.ones_like(denom))
    return dot / safe
