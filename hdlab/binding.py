"""FHRR (elementwise complex multiplication) and HRR (circular convolution) binding."""

from __future__ import annotations

import torch

from . import tracing


def bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Bind two hypervectors. FHRR: elementwise complex mul. HRR: circular convolution via FFT."""
    if a.is_complex():
        out = a * b
    else:
        fa = torch.fft.fft(a)
        fb = torch.fft.fft(b)
        out = torch.fft.ifft(fa * fb).real.to(a.dtype)
    tracing.emit("binding.bind", {"shape_a": list(a.shape), "shape_b": list(b.shape)}, out)
    return out


def unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Inverse of bind. FHRR: mul by conjugate of b. HRR: circular correlation via FFT and conjugate."""
    if c.is_complex():
        out = c * b.conj()
    else:
        fc = torch.fft.fft(c)
        fb = torch.fft.fft(b)
        out = torch.fft.ifft(fc * fb.conj()).real.to(c.dtype)
    tracing.emit("binding.unbind", {"shape_c": list(c.shape), "shape_b": list(b.shape)}, out)
    return out
