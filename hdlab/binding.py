"""Binding primitives: FHRR (elementwise complex mul), HRR (circular convolution), BSC (bipolar mul).

bind/unbind dispatch on dtype: complex64 -> FHRR, float32 real -> HRR (FFT circular convolution).
BSC (Binary Spatter Code) uses bipolar {-1, +1} vectors, which share the real dtype with HRR, so
BSC cannot be dtype-dispatched apart from HRR. It is therefore exposed as explicit named siblings
(bsc_bind / bsc_unbind / bsc_bundle) that keep the HRR/FHRR dispatch path bit-identical. BSC bind is
elementwise multiply and is exactly self-inverse for bipolar b; bundle is majority-sign of the sum.

Theory anchor (Week 8 scaling-law, see PROGRESS.md): BSC bundle capacity k_50% ~ N^1.004
(R^2 = 0.9999); FHRR/BSC capacity ratio is constant at 2.52x. BSC is the memory-bound-edge flavor
(every component is 1 sign bit; bind/unbind are XOR-class; bundle is integer add then sign).
"""

from __future__ import annotations

import time

import torch

from . import tracing


def bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Bind two hypervectors. FHRR: elementwise complex mul. HRR: circular convolution via FFT."""
    t0 = time.perf_counter_ns()
    if a.is_complex():
        out = a * b
    else:
        # Windows MKL FFT is strict about strides; expand_as/broadcast views crash with
        # "Inconsistent configuration parameters" on non-contiguous input. Guard at primitive.
        if not a.is_contiguous():
            a = a.contiguous()
        if not b.is_contiguous():
            b = b.contiguous()
        fa = torch.fft.fft(a)
        fb = torch.fft.fft(b)
        out = torch.fft.ifft(fa * fb).real.to(a.dtype)
    tracing.emit(
        "binding.bind",
        {"shape_a": list(a.shape), "shape_b": list(b.shape)},
        out,
        elapsed_ns=time.perf_counter_ns() - t0,
    )
    return out


def unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Inverse of bind. FHRR: mul by conjugate of b. HRR: circular correlation via FFT and conjugate."""
    t0 = time.perf_counter_ns()
    if c.is_complex():
        out = c * b.conj()
    else:
        # Windows MKL FFT is strict about strides; expand_as/broadcast views crash with
        # "Inconsistent configuration parameters" on non-contiguous input. Guard at primitive.
        if not c.is_contiguous():
            c = c.contiguous()
        if not b.is_contiguous():
            b = b.contiguous()
        fc = torch.fft.fft(c)
        fb = torch.fft.fft(b)
        out = torch.fft.ifft(fc * fb.conj()).real.to(c.dtype)
    tracing.emit(
        "binding.unbind",
        {"shape_c": list(c.shape), "shape_b": list(b.shape)},
        out,
        elapsed_ns=time.perf_counter_ns() - t0,
    )
    return out


def bsc_bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """BSC bind: elementwise multiply of bipolar {-1,+1} vectors (self-inverse). Preserves dtype."""
    t0 = time.perf_counter_ns()
    out = a * b
    tracing.emit(
        "binding.bsc_bind",
        {"shape_a": list(a.shape), "shape_b": list(b.shape)},
        out,
        elapsed_ns=time.perf_counter_ns() - t0,
    )
    return out


def bsc_unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """BSC unbind: elementwise multiply (bind is self-inverse for bipolar b). Preserves dtype."""
    t0 = time.perf_counter_ns()
    out = c * b
    tracing.emit(
        "binding.bsc_unbind",
        {"shape_c": list(c.shape), "shape_b": list(b.shape)},
        out,
        elapsed_ns=time.perf_counter_ns() - t0,
    )
    return out


def bsc_bundle(vectors: torch.Tensor) -> torch.Tensor:
    """BSC bundle: majority sign of the sum, ties to +1. Shape (k, n) -> (n,). Preserves dtype."""
    t0 = time.perf_counter_ns()
    if vectors.dim() != 2:
        raise ValueError(
            f"bsc_bundle expects a 2-D (k, n) stack; got shape {list(vectors.shape)}"
        )
    s = vectors.to(torch.float32).sum(dim=0)
    out = torch.where(s >= 0, torch.ones_like(s), -torch.ones_like(s)).to(vectors.dtype)
    tracing.emit(
        "binding.bsc_bundle",
        {"shape": list(vectors.shape)},
        out,
        elapsed_ns=time.perf_counter_ns() - t0,
    )
    return out
