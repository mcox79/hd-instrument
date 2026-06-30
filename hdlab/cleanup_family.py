"""Cleanup primitive library: 4 cleanup primitives + 1 baseline.

Per spec: notes/director_cleanup_family_primitive_library_spec_2026-06-30.md

Common signature (numpy; CPU). For multi-bank WM K-cliff cell, see also the
torch-tensor versions in
experiments/_substrate_cleanup_family_wm_kcliff_v1_core.py (GPU + bipolar).

This module provides the substrate-flat numpy API for any cell that wants to
swap cleanup primitives as the OUTER axis. CPU-only; cells doing GPU-heavy
sweeps should use the torch versions in the cell core directly.

PRIMITIVES:
  classical_hopfield(query, codebook, *, max_steps=8, sign_quantize=True)
  modern_hopfield_continuous(query, codebook, *, beta=8.0, max_steps=8)
  k_NN_lookup(query, codebook, *, k=1)
  iterative_attractor(query, codebook, *, temp=4.0, max_steps=8)
  no_cleanup(query, codebook)

Each returns (recovered_vector, diagnostics) where diagnostics has at least:
  n_iterations: int
  converged: bool
  final_argmax_idx: int  (or array for batch)
"""
from __future__ import annotations

from typing import Tuple, Any, Dict

import numpy as np

from hdlab.iterative_attractor import iterative_cleanup


def _l2_normalize(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Row-wise L2 normalize (B, D) or (D,) -> same shape; safe."""
    if X.ndim == 1:
        n = float(np.linalg.norm(X) + eps)
        return (X / n).astype(np.float32)
    n = np.linalg.norm(X, axis=1, keepdims=True) + eps
    return (X / n).astype(np.float32)


def _ensure_batch(q: np.ndarray) -> Tuple[np.ndarray, bool]:
    """Ensure (B, D); return (q_2d, was_1d)."""
    if q.ndim == 1:
        return q[None, :], True
    return q, False


def no_cleanup(query: np.ndarray, codebook: np.ndarray, **kw):
    """Baseline: return query unchanged (no cleanup operation)."""
    q2, was_1d = _ensure_batch(query.astype(np.float32))
    cb = codebook.astype(np.float32)
    scores = q2 @ cb.T
    argmax = scores.argmax(axis=1).astype(np.int64)
    out = q2[0] if was_1d else q2
    diag = {
        "n_iterations": 0,
        "converged": True,
        "final_argmax_idx": int(argmax[0]) if was_1d else argmax,
        "primitive": "no_cleanup",
    }
    return out, diag


def k_NN_lookup(query: np.ndarray, codebook: np.ndarray, *, k: int = 1, **kw):
    """k-NN cleanup: one-shot top-k argmax (k=1) or top-k averaged (k>1).

    Strict baseline: no iteration; pure retrieval. k=1 = argmax (substrate default).
    """
    q2, was_1d = _ensure_batch(query.astype(np.float32))
    cb = codebook.astype(np.float32)
    scores = q2 @ cb.T  # (B, M)
    if k <= 1:
        topk_idx = scores.argmax(axis=1, keepdims=True)  # (B, 1)
        recovered = cb[topk_idx[:, 0]]  # (B, D)
    else:
        topk_idx = np.argpartition(scores, -k, axis=1)[:, -k:]  # (B, k)
        # average top-k codebook entries
        # cb[topk_idx] has shape (B, k, D)
        recovered = cb[topk_idx].mean(axis=1)  # (B, D)
    final_argmax = scores.argmax(axis=1).astype(np.int64)
    out = recovered[0] if was_1d else recovered
    diag = {
        "n_iterations": 0,
        "converged": True,
        "final_argmax_idx": int(final_argmax[0]) if was_1d else final_argmax,
        "primitive": "k_NN_lookup",
        "k": int(k),
    }
    return out, diag


def classical_hopfield(query: np.ndarray, codebook: np.ndarray, *,
                       max_steps: int = 8, sign_quantize: bool = True,
                       tol: float = 1e-4, **kw):
    """Classical Hopfield (Hopfield 1982): outer-product Hebbian W + sign update.

    W = codebook.T @ codebook / M (zero diagonal).
    State update: s_next = sign(W @ s) if sign_quantize else (W @ s).

    Capacity ~0.14 * D (Hopfield original). At M/D > 0.14 spurious minima dominate.
    """
    q2, was_1d = _ensure_batch(query.astype(np.float32))
    cb = codebook.astype(np.float32)
    M, D = cb.shape
    # Hebbian weight matrix
    W = (cb.T @ cb) / float(M)  # (D, D)
    np.fill_diagonal(W, 0.0)

    state = q2.copy()
    n_iter = 0
    converged = False
    for step in range(max_steps):
        h = state @ W  # (B, D)
        if sign_quantize:
            s_next = np.sign(h)
            s_next = np.where(s_next == 0, np.ones_like(s_next), s_next).astype(np.float32)
        else:
            # continuous: L2-normalize to avoid blow-up
            s_next = _l2_normalize(h)
        step_dist = float(np.mean(np.linalg.norm(s_next - state, axis=1)))
        state = s_next
        n_iter = step + 1
        if step_dist < tol * np.sqrt(D):
            converged = True
            break

    scores = state @ cb.T
    argmax = scores.argmax(axis=1).astype(np.int64)
    out = state[0] if was_1d else state
    diag = {
        "n_iterations": n_iter,
        "converged": converged,
        "final_argmax_idx": int(argmax[0]) if was_1d else argmax,
        "primitive": "classical_hopfield",
        "sign_quantize": bool(sign_quantize),
    }
    return out, diag


def modern_hopfield_continuous(query: np.ndarray, codebook: np.ndarray, *,
                               beta: float = 8.0, max_steps: int = 8,
                               tol: float = 1e-4, **kw):
    """Modern dense Hopfield / Ramsauer 2021: softmax-attention update rule.

    Exponential capacity (~exp(D)). Equivalent to transformer attention with
    codebook serving as both keys and values.

    s_next = sign(softmax(beta * s @ X.T) @ X)
    """
    q2, was_1d = _ensure_batch(query.astype(np.float32))
    cb = codebook.astype(np.float32)
    D = cb.shape[1]

    state = q2.copy()
    n_iter = 0
    converged = False
    for step in range(max_steps):
        scores = beta * (state @ cb.T)  # (B, M)
        # stable softmax
        scores = scores - scores.max(axis=1, keepdims=True)
        ez = np.exp(scores.astype(np.float64))
        weights = (ez / (ez.sum(axis=1, keepdims=True) + 1e-30)).astype(np.float32)
        s_mix = weights @ cb  # (B, D)
        s_next = np.sign(s_mix)
        s_next = np.where(s_next == 0, np.ones_like(s_next), s_next).astype(np.float32)
        step_dist = float(np.mean(np.linalg.norm(s_next - state, axis=1)))
        state = s_next
        n_iter = step + 1
        if step_dist < tol * np.sqrt(D):
            converged = True
            break

    final_scores = state @ cb.T
    argmax = final_scores.argmax(axis=1).astype(np.int64)
    out = state[0] if was_1d else state
    diag = {
        "n_iterations": n_iter,
        "converged": converged,
        "final_argmax_idx": int(argmax[0]) if was_1d else argmax,
        "primitive": "modern_hopfield_continuous",
        "beta": float(beta),
    }
    return out, diag


def iterative_attractor(query: np.ndarray, codebook: np.ndarray, *,
                        temp: float = 4.0, max_steps: int = 8,
                        tol: float = 1e-3, alpha: float = 0.0, **kw):
    """Wrap hdlab.iterative_attractor.iterative_cleanup with common signature.

    L2-normalized cosine-similarity attractor with softmax weights. Brain-canonical
    via CA3 / DG attractor dynamics (Treves-Rolls).
    """
    out_dict = iterative_cleanup(query, codebook, temp=temp, max_steps=max_steps,
                                  tol=tol, scale_by_sqrt_d=True, alpha=alpha,
                                  return_trace=False)
    diag = {
        "n_iterations": out_dict["n_iterations"],
        "converged": bool(out_dict["converged"]),
        "final_argmax_idx": (int(out_dict["argmax_idx"])
                             if np.isscalar(out_dict["argmax_idx"])
                             else out_dict["argmax_idx"]),
        "primitive": "iterative_attractor",
        "temp": float(temp),
        "alpha": float(alpha),
    }
    return out_dict["state"], diag


PRIMITIVES = {
    "no_cleanup": no_cleanup,
    "classical_hopfield": classical_hopfield,
    "modern_hopfield_continuous": modern_hopfield_continuous,
    "iterative_attractor": iterative_attractor,
    "k_NN_lookup": k_NN_lookup,
}


def _selftest() -> None:
    """Quick selftest: each primitive returns finite recovered + diagnostics."""
    rng = np.random.default_rng(0)
    M, D = 64, 256
    cb = rng.standard_normal((M, D)).astype(np.float32)
    cb_norm = _l2_normalize(cb)

    # Clean query (codebook entry)
    q_clean = cb_norm[7]
    # Noisy query
    q_noisy = cb_norm[7] + 0.1 * rng.standard_normal(D).astype(np.float32)

    for name, fn in PRIMITIVES.items():
        recovered, diag = fn(q_noisy, cb_norm)
        assert np.all(np.isfinite(recovered)), f"{name}: non-finite output"
        assert recovered.shape == (D,), f"{name}: bad shape {recovered.shape}"
        assert "n_iterations" in diag, f"{name}: missing n_iterations"
        assert "converged" in diag, f"{name}: missing converged"
        assert "final_argmax_idx" in diag, f"{name}: missing final_argmax_idx"

    # batch mode
    B = 5
    q_batch = cb_norm[:B] + 0.05 * rng.standard_normal((B, D)).astype(np.float32)
    for name, fn in PRIMITIVES.items():
        recovered, diag = fn(q_batch, cb_norm)
        assert recovered.shape == (B, D), f"{name} batch: bad shape {recovered.shape}"

    print("[hdlab.cleanup_family selftest] PASS: 5 primitives finite + correct shapes "
          "+ batch mode + diagnostics", flush=True)


if __name__ == "__main__":
    _selftest()
