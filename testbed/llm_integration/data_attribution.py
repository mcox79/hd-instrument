"""Substrate-native data attribution primitives.

Two attribution functions on a Hebbian associative-memory substrate
W = (1/N) Xi^T Xi (bipolar, shape (N, N)):

    compute_cpe(W, xi_train, query)
        Counterfactual prediction error via rank-1 substitution.
        Mechanism: W_minus = W - (1/N) xi_train xi_train^T
                   pred_with    = W       @ query  (continuous pre-sign retrieval)
                   pred_without = W_minus @ query
                   CPE          = 1.0 - cosine(pred_with, pred_without)
        High CPE = removing xi_train changes the substrate's retrieval direction
        on `query` significantly = xi_train was load-bearing for that prediction.

        Implementation note: we use the CONTINUOUS pre-sign retrieval rather
        than hard sign() because at N >> 1 the rank-1 (1/N) perturbation is
        smaller than the sign-quantization step for most bits, so sign() loses
        all of the attribution signal. The cosine-of-W-q form is exactly what
        `retrieval_cosine` measures, preserves the rank-1-as-RPE algebraic
        structure, and matches the spec's "cosine(prediction_with,
        prediction_without)" reading at the continuous-retrieval level.
        Range: [0, ~2]; typically [0, 0.1] for well-stored M << N patterns.

    compute_tracin(W, xi_train, query, target=None)
        Continuous-Hebbian TracIn-relaxation attribution.
        Mechanism: relax sign(W @ q) -> W @ q (linear retrieval).
                   grad_W loss(q) = -(target_q - W q) q^T
                   grad_W loss(t) = -(target_t - W t) t^T
                   TracIn = <grad_q, grad_t> = (target_q - W q)^T (target_t - W t)
                                              * (q^T t)
        If target is None (data attribution mode), use target_q = query and
        target_t = xi_train (each example's "target" is itself, as in
        autoencoder-Hebbian training). Then:
           TracIn = (query - W query)^T (xi_train - W xi_train) * (query^T xi_train)

Both functions take numpy arrays, return Python floats.
Reuses primitives from substrate_audit.py: deletion_cert, retrieval_cosine.

PROT-022 selftests run at import time.
ASCII-only; no emojis or em-dashes.
"""
from __future__ import annotations

import numpy as np

from testbed.llm_integration.substrate_audit import (
    build_W_from_patterns,
    deletion_cert,
    retrieval_cosine,
)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two equal-length vectors. Returns 0.0 if either has zero norm."""
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-30 or nb < 1e-30:
        return 0.0
    return float((a @ b) / (na * nb))


def compute_cpe(W: np.ndarray, xi_train: np.ndarray, query: np.ndarray) -> float:
    """Counterfactual prediction error of xi_train on query.

    CPE = 1 - cosine(W @ query, W_minus @ query)
    where W_minus = W - (1/N) xi_train xi_train^T (rank-1 deletion).

    Uses continuous pre-sign retrieval (the same object `retrieval_cosine`
    measures); sign() quantization erases the rank-1 perturbation signal at
    practical N.

    Returns a non-negative float; ~0 means xi_train was irrelevant to this
    query's retrieval; larger means xi_train was load-bearing.
    """
    pred_with = W @ query
    W_minus, _, _ = deletion_cert(W, xi_train)
    pred_without = W_minus @ query
    cos = _cosine(pred_with, pred_without)
    return float(1.0 - cos)


def compute_cpe_batch(W: np.ndarray, Xi_train: np.ndarray, query: np.ndarray) -> np.ndarray:
    """Vectorized CPE for many train examples vs a single query.

    Args:
        W:        (N, N) substrate
        Xi_train: (M, N) train patterns
        query:    (N,)   test query

    Returns (M,) CPE values.
    For each row xi_e: predict_without = sign((W - (1/N) xi_e xi_e^T) @ q)
                                       = sign(W q - (1/N) (xi_e . q) xi_e)
    Compute W q ONCE; per-row deletion via the closed-form shift above.
    Then CPE = 1 - cos(sign(W q), sign(W q - (1/N) (xi_e . q) xi_e)).
    """
    N = W.shape[0]
    M = Xi_train.shape[0]

    Wq = (W @ query).astype(np.float32)                  # (N,) continuous
    dots = (Xi_train @ query).astype(np.float32)          # (M,) scalar xi_e . q
    # Per row: pred_without = Wq - (dots[e] / N) * Xi_train[e]
    # Broadcast: shape (M, N) = (1, N) - (M, 1) * (M, N)
    pred_without = Wq[None, :] - (dots[:, None] / float(N)) * Xi_train

    # Cosine row-wise vs Wq (continuous)
    num = pred_without @ Wq                               # (M,)
    norms_w = float(np.linalg.norm(Wq))
    norms_pw = np.linalg.norm(pred_without, axis=1)       # (M,)
    denom = norms_pw * norms_w + 1e-30
    cos = num / denom
    return (1.0 - cos).astype(np.float32)


def compute_tracin(W: np.ndarray, xi_train: np.ndarray, query: np.ndarray) -> float:
    """Continuous-Hebbian TracIn-relaxation attribution score.

    Linear-relaxation retrieval f(x) = W @ x; per-example "target" is x itself
    (autoencoder-Hebbian framing). Loss = 0.5 ||x - W x||^2; grad_W = -(x - W x) x^T.
    Then TracIn(train e, query q) = <grad_e, grad_q>
                                  = ((q - W q)^T (e - W e)) * (q^T e).
    High positive value = train example e and query q have aligned gradients.
    """
    q_residual = query - (W @ query)             # (N,)
    e_residual = xi_train - (W @ xi_train)       # (N,)
    resid_inner = float(q_residual @ e_residual)
    qe = float(query @ xi_train)
    return float(resid_inner * qe)


def compute_tracin_batch(W: np.ndarray, Xi_train: np.ndarray, query: np.ndarray) -> np.ndarray:
    """Vectorized TracIn for many train examples vs a single query.

    Returns (M,) TracIn scores.
    Computes W q once; W Xi_train as (M, N) once; then row-wise inner products.
    """
    Wq = W @ query                                # (N,)
    q_res = query - Wq                            # (N,)

    WXi = (Xi_train @ W.T)                        # (M, N): (W @ xi_e) per row
    Xi_res = Xi_train - WXi                       # (M, N)

    resid_inner = Xi_res @ q_res                  # (M,)
    qe = Xi_train @ query                         # (M,)
    return (resid_inner * qe).astype(np.float32)


def spearman_rho(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman rank correlation. Uses scipy.stats.spearmanr when available;
    otherwise falls back to manual ranks + Pearson.

    Returns float; NaN-safe (returns 0.0 if input length < 2 or zero variance).
    """
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    if a.size < 2 or b.size < 2 or a.size != b.size:
        return 0.0
    try:
        from scipy.stats import spearmanr
        r, _ = spearmanr(a, b)
        if r is None or np.isnan(r):
            return 0.0
        return float(r)
    except Exception:
        ra = _rankdata(a)
        rb = _rankdata(b)
        ra_c = ra - ra.mean()
        rb_c = rb - rb.mean()
        denom = float(np.sqrt((ra_c ** 2).sum() * (rb_c ** 2).sum()))
        if denom < 1e-30:
            return 0.0
        return float((ra_c * rb_c).sum() / denom)


def _rankdata(x: np.ndarray) -> np.ndarray:
    """Average-tie ranks (1-indexed). Pure numpy fallback for spearman_rho."""
    x = np.asarray(x, dtype=np.float64)
    n = x.size
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(n, dtype=np.float64)
    ranks[order] = np.arange(1, n + 1, dtype=np.float64)
    # Tie-average pass
    # Cheap implementation: skip ties for our use case (continuous scores), but
    # handle them properly via a sort+group:
    sorted_x = x[order]
    i = 0
    while i < n:
        j = i + 1
        while j < n and sorted_x[j] == sorted_x[i]:
            j += 1
        if j - i > 1:
            avg = 0.5 * (ranks[order[i]] + ranks[order[j - 1]])
            for k in range(i, j):
                ranks[order[k]] = avg
        i = j
    return ranks


def _selftest() -> None:
    """PROT-022 selftests for compute_cpe / compute_tracin / spearman_rho."""
    rng = np.random.default_rng(0)
    N = 256
    M = 20

    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    W = build_W_from_patterns(Xi)

    # --- Test 1: CPE on a STORED pattern (query == one of its stored patterns)
    # Deleting that exact pattern should noticeably change the continuous
    # retrieval direction. With M=20, N=256 the rank-1 deletion subtracts
    # (1/N) ||xi||^2 xi = xi from the W xi direction; magnitude is O(1/M).
    stored = Xi[3]
    cpe_self = compute_cpe(W, stored, stored)
    assert cpe_self > 1e-4, f"CPE on stored should be > 1e-4, got {cpe_self:.6e}"

    # --- Test 2: CPE of a RANDOM unrelated pattern on the same query
    # Should be much smaller than self-CPE.
    unrelated = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    cpe_unrelated = compute_cpe(W, unrelated, stored)
    assert cpe_self > cpe_unrelated, (
        f"CPE(stored on stored)={cpe_self:.4f} should beat "
        f"CPE(unrelated on stored)={cpe_unrelated:.4f}")

    # --- Test 3: batched CPE matches scalar CPE
    cpe_vec = compute_cpe_batch(W, Xi, stored)
    cpe_scalar_3 = compute_cpe(W, Xi[3], stored)
    cpe_scalar_7 = compute_cpe(W, Xi[7], stored)
    assert abs(cpe_vec[3] - cpe_scalar_3) < 1e-4, (
        f"batched CPE row 3 mismatch: {cpe_vec[3]:.6f} vs {cpe_scalar_3:.6f}")
    assert abs(cpe_vec[7] - cpe_scalar_7) < 1e-4, (
        f"batched CPE row 7 mismatch: {cpe_vec[7]:.6f} vs {cpe_scalar_7:.6f}")

    # --- Test 4: TracIn same train/query gives positive inner product
    # If train == query == one stored pattern, residual = (xi - W xi) is
    # aligned across both arguments; the inner product squared is positive,
    # and q^T t = N > 0.
    ti_self = compute_tracin(W, stored, stored)
    assert ti_self > 0.0, f"TracIn(stored, stored) should be > 0, got {ti_self:.6f}"

    # --- Test 5: TracIn batched matches scalar
    ti_vec = compute_tracin_batch(W, Xi, stored)
    ti_scalar_3 = compute_tracin(W, Xi[3], stored)
    rel = abs(ti_vec[3] - ti_scalar_3) / max(abs(ti_scalar_3), 1e-9)
    assert rel < 1e-3, (
        f"batched TracIn row 3 mismatch: {ti_vec[3]:.6f} vs {ti_scalar_3:.6f}")

    # --- Test 6: spearman_rho matches scipy on a toy case
    a = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    b = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
    rho = spearman_rho(a, b)
    assert abs(rho - (-1.0)) < 1e-6, f"spearman_rho perfect-anticorr = {rho}, expected -1.0"

    a2 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    b2 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    rho2 = spearman_rho(a2, b2)
    assert abs(rho2 - 1.0) < 1e-6, f"spearman_rho perfect-corr = {rho2}, expected 1.0"

    # Compare to scipy if present
    try:
        from scipy.stats import spearmanr as _sp
        c = rng.standard_normal(50)
        d = rng.standard_normal(50)
        our = spearman_rho(c, d)
        ref, _ = _sp(c, d)
        assert abs(our - float(ref)) < 1e-6, f"spearman_rho mismatch vs scipy: {our} vs {ref}"
    except ImportError:
        pass

    print("[selftest] PASS: data_attribution CPE + TracIn + spearman_rho", flush=True)


_selftest()


__all__ = [
    "compute_cpe",
    "compute_cpe_batch",
    "compute_tracin",
    "compute_tracin_batch",
    "spearman_rho",
]


if __name__ == "__main__":
    _selftest()
