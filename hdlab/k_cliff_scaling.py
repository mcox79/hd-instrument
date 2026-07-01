"""K_cliff scaling law — analytical closed-form for sequence-binding capacity.

Derived from 5x-drill 2026-07-01 (`notes/research_5x_drill_N_scaling_analytical_formula_2026-07-01.md`).
Plate FHRR closed-form:

    K_cliff(N) = 0.87 * N / log2(N)

Cross-N validation: cv(c)=0.03 across N in {4096, 8192, 16384}, R^2=0.99 vs
observed. Empirical 0.828 slope (Batch B v2 fit) was K-grid resolution artifact;
true underlying slope is ~0.92.

Use case: cell-authors can now size cells analytically:
- pick target N
- compute K_cliff(N) as your discriminator anchor
- put smoke points at K_cliff/2, K_cliff, 2*K_cliff to catch the cliff

References:
- Plate 1995 (Holographic Reduced Representations capacity)
- FHRR extension: complex-valued unit-magnitude codebook
- Empirical anchors: K_cliff=500 @ N=8192 (Batch B v2, 2f6262b4)
"""
from __future__ import annotations

import math


C_PLATE_FHRR = 0.87  # Plate FHRR constant (cross-N cv 0.03)


def k_cliff(n_dim: int, c: float = C_PLATE_FHRR) -> int:
    """K_cliff analytical for FHRR at N_dim.

    Args:
        n_dim: substrate dimensionality
        c: Plate constant (default 0.87 per 5x-drill; can override for
           encoder-specific calibrations)

    Returns:
        Analytical K_cliff (int). Use as discriminator anchor for
        sequence-binding phase-diagram cells.
    """
    if n_dim < 4:
        raise ValueError(f"n_dim must be >= 4; got {n_dim}")
    return int(round(c * n_dim / math.log2(n_dim)))


def k_cliff_range(n_dim: int, factor: float = 4.0) -> tuple[int, int, int]:
    """Return (K_below, K_cliff, K_above) for smoke gate discriminator anchors.

    K_below = K_cliff / factor (should saturate above 0.9 recall)
    K_cliff = K_cliff analytical
    K_above = K_cliff * factor (should drop below 0.3 recall)
    """
    k = k_cliff(n_dim)
    return (max(1, int(k / factor)), k, int(k * factor))


__all__ = ["k_cliff", "k_cliff_range", "C_PLATE_FHRR"]
