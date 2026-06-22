"""Encoder-residual whitening: ZCA / PCA whitening primitives.

Operationalizes the 4 chain-grade whitening atoms in the substrate (the most-evidenced
mechanism gap per capability_gap_audit_hdlab_primitives_2026-06-22):
  - EXP_substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096 (PASS)
  - EXP_substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096 (PASS — cross-encoder)
  - EXP_substrate_pca_prewhitening_codebook_v1 (PASS — provides canonical ZCA impl)
  - EXP_substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1 (PASS — alternative)

Whitening removes the mean + decorrelates the dimensions of encoder residuals (e.g.
Pythia-160m mean-pool outputs). Substrate downstream (W matrix Hebbian writes) operates
on decorrelated keys, lifting effective rank + capacity (n10 smoke fired eff_rank
16.7 -> 230.3 = 13.8x).

ZCA whitening is the canonical substrate variant (symmetric, orientation-preserving):
  Kc = K - mean(K, axis=0)
  cov = Kc.T @ Kc / N
  U, S, _ = svd(cov)
  W = U @ diag(1/sqrt(S + eps)) @ U.T
  K_whitened = Kc @ W

The cross-encoder PASS pair (pythia + llama1b both at PASS post-whitening) is direct
chain-grade evidence the substrate's stored content is encoder-portable AFTER the
whitening step — load-bearing for the phase-diagram-action / data-survives-transform
lane (USER 2026-06-22 latent capability).
"""

from __future__ import annotations

import time

import numpy as np

from . import tracing


class WhiteningTransform:
    """ZCA / PCA whitening fit on a sample; transform new vectors at chat-time / ingest-time.

    Fit-once-transform-many primitive. Composes with the encoder pipeline used by
    KGStore / Codebook ingest: encode raw text -> WhiteningTransform.transform -> store/lookup.
    """

    def __init__(self, mode: str = "zca", eps: float = 1e-3) -> None:
        if mode not in ("zca", "pca"):
            raise ValueError(f"mode must be 'zca' or 'pca'; got {mode!r}")
        self.mode = mode
        self.eps = eps
        self.mean_: np.ndarray | None = None
        self.W_: np.ndarray | None = None
        self.U_: np.ndarray | None = None
        self.S_: np.ndarray | None = None
        self.n_samples_seen_: int = 0
        self.n_features_: int | None = None

    def fit(self, K: np.ndarray) -> "WhiteningTransform":
        """Fit on a [N, D] sample of vectors. Computes mean + covariance + decomposition."""
        t0 = time.perf_counter_ns()
        if K.ndim != 2:
            raise ValueError(f"Expected [N, D]; got shape {K.shape}")
        N, D = K.shape
        K = K.astype(np.float32, copy=False)
        self.mean_ = K.mean(axis=0)
        Kc = K - self.mean_
        # Covariance (D, D)
        cov = (Kc.T @ Kc) / max(N, 1)
        # SVD on covariance (symmetric => U == V); use eigendecomposition variant
        U, S, _ = np.linalg.svd(cov)
        self.U_ = U
        self.S_ = S
        if self.mode == "zca":
            # Symmetric ZCA: K_white = (K - mean) @ U @ diag(1/sqrt(S+eps)) @ U.T
            self.W_ = U @ np.diag(1.0 / np.sqrt(S + self.eps)) @ U.T
        else:
            # PCA: K_white = (K - mean) @ U @ diag(1/sqrt(S+eps))   (axis-aligned in PC space)
            self.W_ = U @ np.diag(1.0 / np.sqrt(S + self.eps))
        self.n_samples_seen_ = N
        self.n_features_ = D
        tracing.emit(
            "whitening.fit",
            {"mode": self.mode, "n_samples": N, "n_features": D, "eps": self.eps},
            {"smallest_eigenvalue": float(S[-1]) if S.size > 0 else 0.0, "largest_eigenvalue": float(S[0]) if S.size > 0 else 0.0},
            elapsed_ns=time.perf_counter_ns() - t0,
        )
        return self

    def transform(self, K: np.ndarray) -> np.ndarray:
        """Whiten a [N, D] (or [D,]) vector tensor; returns same shape."""
        if self.mean_ is None or self.W_ is None:
            raise RuntimeError("WhiteningTransform not fit; call .fit(K) first")
        single = (K.ndim == 1)
        if single:
            K = K[None, :]
        if K.shape[-1] != self.n_features_:
            raise ValueError(f"Expected {self.n_features_} features; got {K.shape[-1]}")
        K = K.astype(np.float32, copy=False)
        out = (K - self.mean_) @ self.W_
        return out[0] if single else out

    def fit_transform(self, K: np.ndarray) -> np.ndarray:
        """Convenience: fit + transform in one call."""
        self.fit(K)
        return self.transform(K)

    def effective_rank(self, threshold: float = 0.99) -> int:
        """Effective rank of the input covariance (# eigenvalues capturing `threshold` of variance).

        Useful diagnostic for "is the encoder using its full capacity?" — encoder residuals often
        have effective rank << ambient dim, motivating whitening + dim expansion.
        """
        if self.S_ is None:
            raise RuntimeError("WhiteningTransform not fit")
        total = self.S_.sum()
        if total <= 0:
            return 0
        cumvar = np.cumsum(self.S_) / total
        # Find smallest k such that cumvar[k] >= threshold
        return int(np.searchsorted(cumvar, threshold) + 1)

    def __repr__(self) -> str:
        if self.W_ is None:
            return f"WhiteningTransform(mode={self.mode!r}, eps={self.eps}, FIT=False)"
        return f"WhiteningTransform(mode={self.mode!r}, eps={self.eps}, n_features={self.n_features_}, n_samples_seen={self.n_samples_seen_}, effective_rank_99={self.effective_rank()})"


def zca_whiten(K: np.ndarray, eps: float = 1e-3) -> np.ndarray:
    """One-shot ZCA whitening; fits + transforms K in-place. Convenience wrapper."""
    return WhiteningTransform(mode="zca", eps=eps).fit_transform(K)


def pca_whiten(K: np.ndarray, eps: float = 1e-3) -> np.ndarray:
    """One-shot PCA whitening; fits + transforms K. Convenience wrapper."""
    return WhiteningTransform(mode="pca", eps=eps).fit_transform(K)
