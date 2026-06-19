"""Reference BSC (Binary Spatter Codes): bipolar variant using +/- 1.

Atoms are random +/-1 vectors. Binding is elementwise multiplication (self-inverse).
Bundling is sign of sum (ties broken to +1). Similarity is normalized dot product in [-1, 1].

Hardware appeal: every component fits in 1 bit (or 1 sign bit), binding/unbinding is XOR-class,
bundling is integer addition then sign. This is the canonical neuromorphic-friendly VSA flavor.
"""

from __future__ import annotations

import torch


def make_atom(n: int, generator: torch.Generator) -> torch.Tensor:
    """BSC atom: random +/-1 vector of dimension n, stored as int8."""
    bits = torch.randint(0, 2, (n,), generator=generator)
    return (2 * bits - 1).to(torch.int8)


def bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """BSC bind: elementwise multiplication (self-inverse: a * b * b = a)."""
    return (a * b).to(torch.int8)


def unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """BSC unbind: same as bind, since multiplication of +/-1 is self-inverse."""
    return (c * b).to(torch.int8)


def bundle(vectors: torch.Tensor) -> torch.Tensor:
    """BSC bundle: sign of sum, ties broken to +1. Shape (k, n) -> (n,)."""
    s = vectors.to(torch.int32).sum(dim=0)
    out = torch.where(s >= 0, torch.ones_like(s), -torch.ones_like(s))
    return out.to(torch.int8)


def similarity(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """BSC similarity: normalized dot product in [-1, 1] (= 1 - 2 * hamming / N)."""
    n = a.shape[-1]
    return (a.to(torch.float32) * b.to(torch.float32)).sum(dim=-1) / n
