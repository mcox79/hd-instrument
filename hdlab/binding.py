"""FHRR (elementwise complex multiplication) and HRR (circular convolution) binding."""

from __future__ import annotations

import torch


def bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Bind two hypervectors. FHRR: elementwise complex mul. HRR: circular convolution via FFT."""
    raise NotImplementedError("Week 1")


def unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Inverse of bind. FHRR: mul by conjugate of b. HRR: circular correlation via FFT and conjugate."""
    raise NotImplementedError("Week 1")
