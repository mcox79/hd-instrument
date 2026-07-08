"""Cleanup primitive library: 4 cleanup primitives + 1 baseline.

Per spec: notes/director_cleanup_family_primitive_library_spec_2026-06-30.md

Common signature (numpy; CPU). For multi-bank WM K-cliff cell, see also the
torch-tensor versions in
experiments/_substrate_cleanup_family_wm_kcliff_v1_core.py (GPU + bipolar).

This module provides the substrate-flat numpy API for any cell that wants to
swap cleanup primitives as the OUTER axis. CPU-only; cells doing GPU-heavy
sweeps should use the torch versions in the cell core directly.

PRIMITIVES (single-vector cleanup; query -> cleaned vector):
  classical_hopfield(query, codebook, *, max_steps=8, sign_quantize=True)
  modern_hopfield_continuous(query, codebook, *, beta=8.0, max_steps=8)
  k_NN_lookup(query, codebook, *, k=1)
  iterative_attractor(query, codebook, *, temp=4.0, max_steps=8)
  no_cleanup(query, codebook)

Each returns (recovered_vector, diagnostics) where diagnostics has at least:
  n_iterations: int
  converged: bool
  final_argmax_idx: int  (or array for batch)

BUNDLE_READOUTS (multi-item bundle-set recovery; bundle + codebook -> member indices):
  peel_sic_readout(bundle, codebook, *, n_items, mode="unit"|"proj")
  flat_topk_readout(bundle, codebook, *, n_items)

These have a DIFFERENT contract from PRIMITIVES: input is a BUNDLE (sum of member
codes), output is the set of n_items member INDICES that compose it (not a single
cleaned vector). peel_sic_readout is the confidence-ordered successive-interference-
cancellation / matching-pursuit readout that beats flat top-J at high bundle load
(CG-certified: exp_encoder_peel_sic_readout_realcodes_v1 commit 916e6f7cb;
exp_bundling_slot_peel_sic_v1 commit c2f65e53d). It is a SIBLING registry; the
single-vector PRIMITIVES default path is unchanged. Real (HRR float32) and complex
(FHRR complex64/complex128) codebooks are both handled (conjugate-aware scoring).
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


# ==================== multi-item bundle-set-recovery readouts ================
# DIFFERENT contract from the single-vector PRIMITIVES above: input is a BUNDLE
# (sum of member codes), output is the set of member INDICES. Kept as a sibling
# registry (BUNDLE_READOUTS) so the single-vector default path is unchanged.
def _bundle_scores(residual: np.ndarray, codebook_conj: np.ndarray) -> np.ndarray:
    """Real cleanup scores of residual (B, D) vs conj(codebook) (M, D) -> (B, M).

    Re(<c_i, r>) with <a,b>=sum conj(a)*b; conj is a no-op for real dtypes so this
    is a plain dot product for HRR and the phasor cleanup score for FHRR.
    """
    return (residual @ codebook_conj.T).real


def flat_topk_readout(bundle: np.ndarray, codebook: np.ndarray, *, n_items: int,
                      **kw) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Flat top-J readout: one-shot argmax-cosine, take the n_items highest-scoring codes.

    bundle (D,) or (B, D); codebook (M, D) -> indices (n_items,) or (B, n_items) int64,
    ordered by descending score. This is the current default bundle readout that peel/SIC
    beats at high bundle load (the negative control).
    """
    b2, was_1d = _ensure_batch(bundle)
    cb = codebook
    M = cb.shape[0]
    if not (1 <= int(n_items) <= M):
        raise ValueError(f"flat_topk_readout n_items={n_items} must be in [1, M={M}]")
    n_items = int(n_items)
    scores = _bundle_scores(b2, cb.conj())                       # (B, M)
    part = np.argpartition(-scores, n_items - 1, axis=1)[:, :n_items]  # (B, n_items) unordered
    part_scores = np.take_along_axis(scores, part, axis=1)
    order = np.argsort(-part_scores, axis=1)                     # descending score
    idx = np.take_along_axis(part, order, axis=1).astype(np.int64)
    diag = {"primitive": "flat_topk_readout", "n_items": n_items,
            "converged": True, "final_argmax_idx": int(idx[0, 0]) if was_1d else idx[:, 0]}
    return (idx[0] if was_1d else idx), diag


def peel_sic_readout(bundle: np.ndarray, codebook: np.ndarray, *, n_items: int,
                     mode: str = "unit", eps: float = 1e-12,
                     **kw) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Confidence-ordered successive-interference-cancellation (matching pursuit) readout.

    bundle (D,) or (B, D); codebook (M, D) -> member indices (n_items,) or (B, n_items) int64,
    in confidence order (most-confident resolved first). Each round: score the running residual
    vs the codebook, pick the global argmax (most-confident member), record it, deflate its
    codeword from the residual, never repick. mode='unit' subtracts the codeword (unit-weight;
    correct for a sum of members each contributing weight 1); mode='proj' subtracts its
    projection <c,r>/<c,c> * c (magnitude-aware matching pursuit for non-unit / correlated codes).
    """
    if mode not in ("unit", "proj"):
        raise ValueError(f"peel_sic_readout mode must be 'unit' or 'proj', got {mode!r}")
    b2, was_1d = _ensure_batch(bundle)
    cb = codebook
    B, D = b2.shape
    M = cb.shape[0]
    if not (1 <= int(n_items) <= M):
        raise ValueError(f"peel_sic_readout n_items={n_items} must be in [1, M={M}]")
    n_items = int(n_items)
    cb_conj = cb.conj()                                          # (M, D); no-op for real
    cb_sqnorm = (cb_conj * cb).sum(axis=1).real.astype(np.float64) + eps  # (M,) >0
    resid = b2.astype(cb.dtype, copy=True)                      # running residual (B, D)
    preds = np.full((B, n_items), -1, dtype=np.int64)
    picked = np.zeros((B, M), dtype=bool)
    ar = np.arange(B)
    neg = np.float64(-np.inf)
    for r in range(n_items):
        scores = _bundle_scores(resid, cb_conj)                # (B, M)
        scores = np.where(picked, neg, scores)
        ih = scores.argmax(axis=1)                             # (B,) most-confident member
        preds[:, r] = ih
        picked[ar, ih] = True
        chosen = cb[ih]                                        # (B, D)
        if mode == "unit":
            resid = resid - chosen                            # unit-weight deflation
        else:
            coeff = (chosen.conj() * resid).sum(axis=1) / cb_sqnorm[ih]  # (B,) projection weight
            resid = resid - coeff[:, None] * chosen
    resid_norm = np.linalg.norm(resid.reshape(B, -1), axis=1).astype(np.float64)
    diag = {"primitive": "peel_sic_readout", "mode": mode, "n_items": n_items,
            "converged": True, "n_iterations": n_items,
            "final_residual_norm": float(resid_norm[0]) if was_1d else resid_norm,
            "final_argmax_idx": int(preds[0, 0]) if was_1d else preds[:, 0]}
    return (preds[0] if was_1d else preds), diag


def _readout_flat_topk(bundle, codebook, n_items):
    return flat_topk_readout(bundle, codebook, n_items=n_items)


def _readout_peel_unit(bundle, codebook, n_items):
    return peel_sic_readout(bundle, codebook, n_items=n_items, mode="unit")


def _readout_peel_proj(bundle, codebook, n_items):
    return peel_sic_readout(bundle, codebook, n_items=n_items, mode="proj")


BUNDLE_READOUTS = {
    "flat_topk": _readout_flat_topk,
    "peel_sic_unit": _readout_peel_unit,
    "peel_sic_proj": _readout_peel_proj,
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

    # bundle-set readouts (sibling contract): peel/SIC must beat flat top-J at high load
    J = 20
    members = rng.choice(M, size=J, replace=False)
    bundle = cb_norm[members].sum(axis=0).astype(np.float32)
    true_set = set(int(x) for x in members)
    for name, fn in BUNDLE_READOUTS.items():
        idx, diag = fn(bundle, cb_norm, J)
        assert idx.shape == (J,), f"{name}: bad readout shape {idx.shape}"
        assert idx.dtype == np.int64, f"{name}: readout dtype {idx.dtype}"
        assert set(int(x) for x in idx).issubset(range(M)), f"{name}: index out of range"
    flat_idx, _ = flat_topk_readout(bundle, cb_norm, n_items=J)
    peel_idx, _ = peel_sic_readout(bundle, cb_norm, n_items=J, mode="unit")
    flat_recall = len(set(int(x) for x in flat_idx) & true_set) / J
    peel_recall = len(set(int(x) for x in peel_idx) & true_set) / J
    assert peel_recall >= flat_recall, (
        f"peel/SIC ({peel_recall:.3f}) must not underperform flat top-J ({flat_recall:.3f})")
    # batch readout shape
    bundle_b = np.stack([cb_norm[rng.choice(M, size=J, replace=False)].sum(0) for _ in range(4)])
    for name, fn in BUNDLE_READOUTS.items():
        idx_b, _ = fn(bundle_b.astype(np.float32), cb_norm, J)
        assert idx_b.shape == (4, J), f"{name} batch: bad shape {idx_b.shape}"

    print("[hdlab.cleanup_family selftest] PASS: 5 primitives finite + correct shapes "
          "+ batch mode + diagnostics; 3 bundle readouts (peel_recall=%.3f >= flat=%.3f)"
          % (peel_recall, flat_recall), flush=True)


if __name__ == "__main__":
    _selftest()
