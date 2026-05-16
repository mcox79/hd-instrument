"""Reference HRR: naive circular-convolution variant, read-only oracle for verification."""

from __future__ import annotations

import math

import torch


def make_atom(n: int, generator: torch.Generator) -> torch.Tensor:
    """HRR atom: float32, gaussian with std 1/sqrt(n)."""
    return torch.randn(n, generator=generator, dtype=torch.float32) / math.sqrt(n)


def bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """HRR bind: circular convolution via FFT. Returns float32."""
    fa = torch.fft.fft(a)
    fb = torch.fft.fft(b)
    return torch.fft.ifft(fa * fb).real.to(a.dtype)


def unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """HRR unbind: circular correlation via involution of b (FFT(b).conj())."""
    fc = torch.fft.fft(c)
    fb = torch.fft.fft(b)
    return torch.fft.ifft(fc * fb.conj()).real.to(c.dtype)


def bundle(vectors: torch.Tensor) -> torch.Tensor:
    """HRR bundle: sum then L2-normalize the whole vector. Shape (k, n) -> (n,)."""
    s = vectors.sum(dim=0)
    norm = s.norm()
    if float(norm) > 0:
        return s / norm
    return s


def similarity(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """HRR similarity: cosine similarity (last-dim broadcasting)."""
    dot = (a * b).sum(dim=-1)
    na = a.norm(dim=-1)
    nb = b.norm(dim=-1)
    denom = na * nb
    safe = torch.where(denom > 0, denom, torch.ones_like(denom))
    return dot / safe
