"""FHRR (elementwise complex multiplication) and HRR (circular convolution) binding."""

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
