"""Substrate audit primitives for Phase 0.5 LLM-coupled tests.

Three load-bearing primitives:

    (1) Streaming Hebbian write:  W_t = (1 - decay) W_{t-1} + (1/N) xi_t xi_t^T
    (2) Whitened kappa_3:          kappa_3(Sigma^{-1/2} W Sigma^{-1/2}) via Hutchinson
                                   (per I-10 kappa_3-mixing drill mitigation)
    (3) Rank-1 deletion + cert:    W' = W - (1/N) xi_f xi_f^T;  cert = xi_f^T (W' - W) xi_f
                                   exact closed-form cert per COMBO-3 P9 = - ||xi_f||^4 / N

All primitives are dtype/shape-strict numpy; designed to compose with bipolar
codewords from HyperprobeEncoder.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


def hebbian_write(W: np.ndarray, xi: np.ndarray, decay: float = 0.0) -> np.ndarray:
    """One-step streaming write.

    Args:
        W:    (N, N) substrate
        xi:   (N,)   bipolar codeword
        decay: 0 = no decay; otherwise (1-decay) * W before update
    """
    N = W.shape[0]
    if decay > 0:
        W = (1.0 - decay) * W
    return W + np.outer(xi, xi).astype(W.dtype) / float(N)


def build_W_from_patterns(Xi: np.ndarray) -> np.ndarray:
    """Build W = (1/N) Xi^T Xi from bipolar pattern matrix Xi of shape (M, N)."""
    M, N = Xi.shape
    W = (Xi.T.astype(np.float32) @ Xi.astype(np.float32)) / float(N)
    return W


def estimate_sigma_from_patterns(Xi: np.ndarray, ridge: float = 1e-4) -> Tuple[np.ndarray, np.ndarray]:
    """Empirical covariance Sigma = (1/M) Xi^T Xi (no centering for bipolar) + ridge.

    Returns (Sigma, Sigma_inv_half) where Sigma_inv_half = Sigma^{-1/2}.
    """
    M, N = Xi.shape
    Sigma = (Xi.T.astype(np.float32) @ Xi.astype(np.float32)) / float(M)
    # Add small ridge to ensure invertibility
    Sigma = Sigma + ridge * np.eye(N, dtype=np.float32)
    # Symmetric matrix square root inverse via eigendecomposition
    w, V = np.linalg.eigh(Sigma)
    w_clipped = np.maximum(w, ridge)
    Sigma_inv_half = (V * (w_clipped ** -0.5)) @ V.T
    return Sigma, Sigma_inv_half.astype(np.float32)


def whitened_W(W: np.ndarray, Sigma_inv_half: np.ndarray) -> np.ndarray:
    """W_white = Sigma^{-1/2} W Sigma^{-1/2}."""
    return (Sigma_inv_half @ W @ Sigma_inv_half).astype(W.dtype)


def kappa_3_hutchinson(W: np.ndarray, n_probes: int,
                       rng: np.random.Generator) -> Tuple[float, float]:
    """Hutchinson estimator for kappa_3 = Tr(W^3) / N.

    Returns (mean, std_error). per_probe = (V0 * (W @ W @ W @ V0)).sum(0) / N
    """
    N = W.shape[0]
    V0 = rng.choice([-1.0, 1.0], size=(N, n_probes)).astype(np.float32)
    V1 = (W @ V0)
    V2 = (W @ V1)
    V3 = (W @ V2)
    per_probe = (V0.astype(np.float64) * V3.astype(np.float64)).sum(axis=0) / float(N)
    mean = float(np.mean(per_probe))
    se = float(np.std(per_probe, ddof=1)) / math.sqrt(max(1, n_probes))
    return mean, se


def deletion_cert(W: np.ndarray, xi: np.ndarray) -> Tuple[np.ndarray, float, float]:
    """Rank-1 deletion. Returns (W_post, cert, signal_norm).

    cert = xi^T (W_post - W) xi = - ||xi||^4 / N (closed form for bipolar xi with ||xi||^2 = N)
    signal_norm = ||W_post @ xi - W @ xi|| (deletion-cert Z-ratio signal)
    """
    N = W.shape[0]
    delta = np.outer(xi, xi).astype(W.dtype) / float(N)
    W_post = W - delta
    cert = float(xi @ (W_post - W) @ xi)
    diff = (W_post @ xi) - (W @ xi)
    signal_norm = float(np.linalg.norm(diff))
    return W_post, cert, signal_norm


def retrieval_cosine(W: np.ndarray, xi: np.ndarray) -> float:
    """Soft retrieval cosine: cos(W @ xi, xi). 1.0 = perfectly stored; ~0 = erased."""
    y = W @ xi
    yn = float(np.linalg.norm(y))
    xn = float(np.linalg.norm(xi))
    if yn < 1e-30 or xn < 1e-30:
        return 0.0
    return float((y @ xi) / (yn * xn))


def null_distribution_norm(W: np.ndarray, n_probes: int,
                           rng: np.random.Generator) -> Tuple[float, float]:
    """||W @ eta|| for random bipolar eta (null hypothesis for deletion-cert Z).

    Returns (mean, std) over n_probes samples.
    """
    N = W.shape[0]
    norms = np.zeros(n_probes, dtype=np.float64)
    for i in range(n_probes):
        eta = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
        norms[i] = float(np.linalg.norm(W @ eta))
    return float(np.mean(norms)), float(np.std(norms, ddof=1))


def _selftest() -> None:
    """Identity-check + closed-form cert + whitening fixed-point."""
    rng = np.random.default_rng(0)
    N = 128

    # 1. kappa_3 of identity W=I should be 1.0
    W_id = np.eye(N, dtype=np.float32)
    k3_id, _ = kappa_3_hutchinson(W_id, 200, rng)
    assert abs(k3_id - 1.0) < 0.1, f"kappa_3(I) = {k3_id}, expected ~1.0"

    # 2. closed-form deletion cert for bipolar xi: cert = -1 exactly (||xi||^2 = N)
    Xi = rng.choice([-1.0, 1.0], size=(20, N)).astype(np.float32)
    W = build_W_from_patterns(Xi)
    xi = Xi[3]
    W_post, cert, _ = deletion_cert(W, xi)
    expected_cert = -1.0  # = -||xi||^4 / N = -N^2 / N
    assert abs(cert - expected_cert * float(N)) < 1e-3, \
        f"cert = {cert}, expected closed-form ~{expected_cert * N}"
    # Cert per algebra: xi^T (-1/N) xi xi^T xi = - (xi^T xi)^2 / N = -N
    # (our cert returns the scalar in the W-norm; both forms valid)

    # 3. whitening: Sigma^{-1/2} Sigma Sigma^{-1/2} = I
    Sigma, Sinv = estimate_sigma_from_patterns(Xi)
    I_approx = Sinv @ Sigma @ Sinv
    err = float(np.linalg.norm(I_approx - np.eye(N, dtype=np.float32)) / np.sqrt(N))
    assert err < 0.1, f"whitening fixed-point error {err}, expected < 0.1"

    # 4. retrieval cosine on stored vs unstored: stored > unstored
    cos_stored = retrieval_cosine(W, Xi[3])
    eta = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    cos_null = retrieval_cosine(W, eta)
    assert cos_stored > cos_null, \
        f"stored {cos_stored} should beat null {cos_null}"

    print("[selftest] PASS: substrate_audit kappa_3 + cert + whitening + retrieval", flush=True)


if __name__ == "__main__":
    _selftest()
