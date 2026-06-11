"""Layer 2 spectral observability v1.

Per Research FREE_PROBABILITY_OBSERVABILITY_INTEGRATION 2026-06-11:
~30-line numpy primitive computing 4 spectral measures on substrate codebook
eigenvalues:

1. Marchenko-Pastur bulk    -- codebook eigenvalue density vs MP prediction
2. Tracy-Widom edge          -- largest-eigenvalue fluctuations
3. kappa_4 free cumulant     -- semicircle deviation (m_4 - (1+lambda)*m_2^2)
4. Spectral gap              -- separability regime detection

Substrate-novel observability: LLM embedding cosine alone cannot give these
measurements. Substrate distinguishing axis #2 (after algebra-HRR Index 2).

Implementation: a single ~50-line function computing all 4 measures from a
codebook matrix. Returns a dict for easy logging + comparison across runs.

Activation threshold per Research: M >= 100 for reliable Tracy-Widom
estimates. v1 runs at any M; reports caveat when M < 100.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SpectralObservability:
    """Substrate-novel spectral measures on a codebook matrix.

    All measures derived from the eigenvalues of the Wishart-like matrix
    W = X X^T / N where X is the codebook (M atoms x N dim, L2-normalized).
    """
    M: int                    # number of atoms (samples)
    N: int                    # vector dimension
    aspect_ratio: float       # lambda = M / N (Marchenko-Pastur parameter)
    eig_min: float
    eig_max: float
    eig_mean: float
    eig_var: float
    spectral_gap: float       # eig[-1] - eig[-2]
    mp_bulk_kl: Optional[float]      # KL divergence between empirical
                                      # eigvalue density and MP prediction
                                      # (low = bulk follows MP; high = bulk
                                      # is non-MP, indicating non-random
                                      # structure)
    tw_edge_z: Optional[float]       # standardized z-score of max eigenvalue
                                      # under Tracy-Widom (large = strong edge)
    kappa_4_free: Optional[float]    # 4th free cumulant: m_4 - (1 + lambda)
                                      # * m_2^2; measures semicircle deviation
    insufficient_M_warning: bool     # True if M < 100; estimates unreliable

    def to_dict(self) -> dict:
        return {
            "M": self.M,
            "N": self.N,
            "aspect_ratio": round(self.aspect_ratio, 4),
            "eig_min": round(self.eig_min, 6),
            "eig_max": round(self.eig_max, 6),
            "eig_mean": round(self.eig_mean, 6),
            "eig_var": round(self.eig_var, 6),
            "spectral_gap": round(self.spectral_gap, 6),
            "mp_bulk_kl": round(self.mp_bulk_kl, 4) if self.mp_bulk_kl is not None else None,
            "tw_edge_z": round(self.tw_edge_z, 4) if self.tw_edge_z is not None else None,
            "kappa_4_free": round(self.kappa_4_free, 6) if self.kappa_4_free is not None else None,
            "insufficient_M_warning": self.insufficient_M_warning,
        }


def _mp_density(x: np.ndarray, lam: float) -> np.ndarray:
    """Marchenko-Pastur density at eigenvalue x for aspect ratio lam.

    For X with i.i.d. zero-mean unit-variance entries scaled by 1/sqrt(N),
    eigenvalues of X X^T / N follow MP distribution in the bulk:
        rho(x) = sqrt((lam_plus - x) * (x - lam_minus)) / (2 pi x lam)
    where lam_plus = (1 + sqrt(lam))^2, lam_minus = (1 - sqrt(lam))^2.
    """
    lam_plus = (1.0 + np.sqrt(lam)) ** 2
    lam_minus = (1.0 - np.sqrt(lam)) ** 2
    rho = np.zeros_like(x, dtype=np.float64)
    mask = (x > lam_minus) & (x < lam_plus) & (x > 1e-12)
    inner = (lam_plus - x[mask]) * (x[mask] - lam_minus)
    inner = np.clip(inner, 0, None)
    rho[mask] = np.sqrt(inner) / (2.0 * np.pi * x[mask] * lam)
    return rho


def spectral_observability(codebook: np.ndarray) -> SpectralObservability:
    """Compute 4 spectral measures on a codebook matrix.

    Args:
        codebook: shape (M, N) -- M atoms x N-dim L2-normalized vectors.
    """
    M, N = codebook.shape
    insufficient = M < 100
    if M < 4:
        return SpectralObservability(
            M=M, N=N, aspect_ratio=float(M) / N,
            eig_min=0.0, eig_max=0.0, eig_mean=0.0, eig_var=0.0,
            spectral_gap=0.0,
            mp_bulk_kl=None, tw_edge_z=None, kappa_4_free=None,
            insufficient_M_warning=True,
        )

    # Wishart-like form. For M << N (tall codebook) we use the M-sided
    # Wishart W = X X^T scaled by 1/N. Substrate atoms are L2-normalized
    # (row norm = 1), so the eigenvalue bulk mean is M/N (the aspect ratio).
    # To put eigenvalues in MP standard form (bulk centered at 1), divide
    # by aspect ratio.
    lam = float(M) / N
    W = codebook @ codebook.T / N
    eig = np.linalg.eigvalsh(W)
    # Standardize: bulk should center at 1 in MP standard form
    if lam > 1e-12:
        eig = eig / lam

    eig_min = float(eig[0])
    eig_max = float(eig[-1])
    eig_mean = float(eig.mean())
    eig_var = float(eig.var())
    spectral_gap = float(eig[-1] - eig[-2]) if len(eig) >= 2 else 0.0

    # Marchenko-Pastur bulk KL: build histogram of empirical eigs, compare
    # to MP density
    if M >= 20:
        n_bins = max(10, M // 5)
        lam_minus = (1.0 - np.sqrt(lam)) ** 2
        lam_plus = (1.0 + np.sqrt(lam)) ** 2
        bin_edges = np.linspace(max(0.0, lam_minus * 0.5), lam_plus * 1.2, n_bins + 1)
        hist, _ = np.histogram(eig, bins=bin_edges)
        emp = hist / hist.sum() + 1e-12
        mid = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        mp = _mp_density(mid, lam)
        mp = mp / (mp.sum() + 1e-12) + 1e-12
        mp_bulk_kl = float((emp * np.log(emp / mp)).sum())
    else:
        mp_bulk_kl = None

    # Tracy-Widom edge z-score: standardize eig_max against MP edge
    if M >= 20:
        lam_plus = (1.0 + np.sqrt(lam)) ** 2
        # Tracy-Widom scaling at the right edge
        scale = (1.0 + np.sqrt(lam)) * ((1.0 / np.sqrt(M) + 1.0 / np.sqrt(N)) ** (1.0 / 3.0))
        tw_edge_z = float((eig_max - lam_plus) / max(scale, 1e-12))
    else:
        tw_edge_z = None

    # kappa_4 free cumulant: m_4 - (1 + lambda) * m_2^2
    if M >= 4:
        m_2 = float((eig ** 2).mean())
        m_4 = float((eig ** 4).mean())
        kappa_4_free = m_4 - (1.0 + lam) * (m_2 ** 2)
    else:
        kappa_4_free = None

    return SpectralObservability(
        M=M, N=N,
        aspect_ratio=lam,
        eig_min=eig_min, eig_max=eig_max,
        eig_mean=eig_mean, eig_var=eig_var,
        spectral_gap=spectral_gap,
        mp_bulk_kl=mp_bulk_kl,
        tw_edge_z=tw_edge_z,
        kappa_4_free=kappa_4_free,
        insufficient_M_warning=insufficient,
    )
