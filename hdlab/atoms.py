"""FHRR and HRR atom generation, similarity, and batch operations."""

from __future__ import annotations

import math
import time

import torch

from . import tracing


def make_atom_fhrr(n: int, generator: torch.Generator) -> torch.Tensor:
    """FHRR atom of dimension n: complex64 unit-magnitude with uniform random phases. Shape: (n,)."""
    t0 = time.perf_counter_ns()
    phases = torch.rand(n, generator=generator) * (2.0 * math.pi)
    out = torch.complex(torch.cos(phases), torch.sin(phases)).to(torch.complex64)
    tracing.emit("atoms.make_atom_fhrr", {"n": n}, out, elapsed_ns=time.perf_counter_ns() - t0)
    return out


def make_atom_hrr(n: int, generator: torch.Generator) -> torch.Tensor:
    """HRR atom of dimension n: float32 gaussian with std 1/sqrt(n). Shape: (n,)."""
    t0 = time.perf_counter_ns()
    out = torch.randn(n, generator=generator, dtype=torch.float32) / math.sqrt(n)
    tracing.emit("atoms.make_atom_hrr", {"n": n}, out, elapsed_ns=time.perf_counter_ns() - t0)
    return out


def make_atoms(k: int, n: int, dtype: torch.dtype, generator: torch.Generator) -> torch.Tensor:
    """Batch of k atoms of dimension n. Shape: (k, n)."""
    t0 = time.perf_counter_ns()
    if dtype == torch.complex64:
        phases = torch.rand((k, n), generator=generator) * (2.0 * math.pi)
        out = torch.complex(torch.cos(phases), torch.sin(phases)).to(torch.complex64)
    elif dtype == torch.float32:
        out = torch.randn((k, n), generator=generator, dtype=torch.float32) / math.sqrt(n)
    else:
        raise ValueError(f"Unsupported atom dtype: {dtype}")
    tracing.emit(
        "atoms.make_atoms",
        {"k": k, "n": n, "dtype": str(dtype)},
        out,
        elapsed_ns=time.perf_counter_ns() - t0,
    )
    return out


def similarity(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Real part of normalized inner product (FHRR) or cosine similarity (HRR), last-dim broadcast."""
    t0 = time.perf_counter_ns()
    if a.is_complex():
        n = a.shape[-1]
        result = (a * b.conj()).sum(dim=-1).real / n
    else:
        dot = (a * b).sum(dim=-1)
        na = a.norm(dim=-1)
        nb = b.norm(dim=-1)
        denom = na * nb
        safe = torch.where(denom > 0, denom, torch.ones_like(denom))
        result = dot / safe
    tracing.emit(
        "atoms.similarity",
        {"shape_a": list(a.shape), "shape_b": list(b.shape)},
        result,
        elapsed_ns=time.perf_counter_ns() - t0,
    )
    return result
