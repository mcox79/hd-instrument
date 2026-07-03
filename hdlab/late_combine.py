"""Substrate-native LATE-COMBINE parallel-stream integrator (N400-window analog).

INPUT REGIME DOCSTRING BLOCK:
    Input: N parallel HD streams (numpy arrays of shape [n_dim] each) plus
        per-stream scalar weights.
    Output: single HD vector of shape [n_dim], unit-L2-normalized.
    Regime type: STREAM COMPOSITION.  Combines independent spoke HDs into a
        single query HD via weighted sum; final L2 normalization keeps
        cosine-argmax retrieval scale-invariant.  Late-combine analog of
        N400-window integration across VWFA + morphological + ATL streams.
    Brain analog: N400 window (300-500ms post-stimulus).  Marinkovic 2003,
        Solomyak/Marantz 2010 -- parallel-streams-late-combine architecture,
        not sequential-cascade.  N400 amplitude reflects INTEGRATION difficulty
        across streams (Kutas/Federmeier 2011).

Backward compatibility:
    LateCombine(alpha=0, beta=0, gamma=1).combine(v_ortho, v_morph, v_sem)
    == unit-normalized v_sem.  Preserves current concept_encoder behavior
    exactly when other streams are absent.

Weight fitting:
    fit_weights_grid(v_ortho_query, v_sem_query, prototypes_ortho,
                     prototypes_sem, labels, k_grid)
    Grid-search 1D or 2D over (alpha, gamma).  Returns weights maximizing
    recall@1 on the supplied held-out validation split.  Simple and honest:
    no gradient descent, no over-fit hazard beyond the coarse grid.

Pure substrate; NumPy; no torch.  ASCII-only.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np


def _l2_normalize(v: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n < eps:
        return v.astype(np.float32, copy=True)
    return (v / n).astype(np.float32)


class LateCombine:
    """Weighted-sum stream combiner for 2- or 3-spoke architectures.

    combine(v_ortho, v_morph, v_sem) returns L2-normalized
        alpha * v_ortho + beta * v_morph + gamma * v_sem

    Any stream may be None (treated as zero contribution).  Backward-compat
    identity (alpha=beta=0, gamma=1) recovers unit-normalized v_sem exactly.
    """

    def __init__(
        self,
        alpha: float = 0.0,
        beta: float = 0.0,
        gamma: float = 1.0,
    ) -> None:
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.gamma = float(gamma)

    def combine(
        self,
        v_ortho: Optional[np.ndarray] = None,
        v_morph: Optional[np.ndarray] = None,
        v_sem: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        # Determine dim.
        n_dim = None
        for v in (v_ortho, v_morph, v_sem):
            if v is not None:
                n_dim = int(v.shape[0])
                break
        if n_dim is None:
            raise ValueError("all streams None; cannot combine")
        acc = np.zeros(n_dim, dtype=np.float32)
        if v_ortho is not None and self.alpha != 0.0:
            # Normalize each stream first so the scale of alpha/beta/gamma is
            # comparable across streams with different raw magnitudes.
            acc = acc + float(self.alpha) * _l2_normalize(v_ortho.astype(np.float32))
        if v_morph is not None and self.beta != 0.0:
            acc = acc + float(self.beta) * _l2_normalize(v_morph.astype(np.float32))
        if v_sem is not None and self.gamma != 0.0:
            acc = acc + float(self.gamma) * _l2_normalize(v_sem.astype(np.float32))
        # Final normalize so retrieval is cosine-only.
        return _l2_normalize(acc)

    def weights_dict(self) -> Dict[str, float]:
        return {"alpha": self.alpha, "beta": self.beta, "gamma": self.gamma}

    def __repr__(self) -> str:
        return f"LateCombine(alpha={self.alpha}, beta={self.beta}, gamma={self.gamma})"


def _cosine_argmax_topk(
    query_hd: np.ndarray, prototypes: np.ndarray, k: int
) -> np.ndarray:
    q = query_hd.astype(np.float32)
    p = prototypes.astype(np.float32)
    q_norm = float(np.linalg.norm(q))
    if q_norm < 1e-12:
        return np.arange(min(k, p.shape[0]), dtype=np.int64)
    p_norms = np.linalg.norm(p, axis=1)
    p_norms_safe = np.where(p_norms < 1e-12, 1.0, p_norms)
    scores = (p @ q) / (p_norms_safe * q_norm)
    scores = np.where(p_norms < 1e-12, -1e9, scores)
    if k >= scores.shape[0]:
        order = np.argsort(-scores)
    else:
        idx_part = np.argpartition(-scores, k)[:k]
        order = idx_part[np.argsort(-scores[idx_part])]
    return order.astype(np.int64)


def fit_weights_grid_2spoke(
    per_query_ortho: List[np.ndarray],
    per_query_sem: List[np.ndarray],
    prototypes_ortho: np.ndarray,
    prototypes_sem: np.ndarray,
    labels: Sequence[int],
    alpha_grid: Optional[Sequence[float]] = None,
) -> Tuple[float, float, float]:
    """Grid-search (alpha, gamma) with gamma = 1 - alpha; return best weights.

    Approach: for each alpha in the grid, compute combined-query HDs on the
    validation split, retrieve top-1 from BOTH prototype tables via a
    late-combined score.  We do NOT combine the prototypes themselves (they
    live in DIFFERENT HD codebook namespaces so cannot be summed directly);
    instead we combine the per-atom SCORES from cosine-against-each-table.

    Returns (best_alpha, best_beta=0.0, best_gamma, best_recall_at_1).
    """
    if alpha_grid is None:
        alpha_grid = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
    n = len(per_query_ortho)
    if n == 0:
        return (0.0, 0.0, 1.0, 0.0)
    if n != len(per_query_sem) or n != len(labels):
        raise ValueError(
            f"per_query_ortho ({n}) / per_query_sem ({len(per_query_sem)}) / "
            f"labels ({len(labels)}) length mismatch"
        )

    def _cos_row(q: np.ndarray, protos: np.ndarray) -> np.ndarray:
        qn = float(np.linalg.norm(q))
        if qn < 1e-12:
            return np.zeros(protos.shape[0], dtype=np.float32)
        p = protos.astype(np.float32)
        pn = np.linalg.norm(p, axis=1)
        pn_safe = np.where(pn < 1e-12, 1.0, pn)
        return ((p @ q.astype(np.float32)) / (pn_safe * qn)).astype(np.float32)

    # Pre-compute cosine tables once per query per table.
    ortho_scores: List[np.ndarray] = [
        _cos_row(per_query_ortho[i], prototypes_ortho) for i in range(n)
    ]
    sem_scores: List[np.ndarray] = [
        _cos_row(per_query_sem[i], prototypes_sem) for i in range(n)
    ]

    best_alpha = 0.0
    best_recall = -1.0
    for alpha in alpha_grid:
        a = float(alpha)
        g = 1.0 - a
        correct = 0
        for i in range(n):
            combined = a * ortho_scores[i] + g * sem_scores[i]
            top1 = int(np.argmax(combined))
            if top1 == int(labels[i]):
                correct += 1
        recall = correct / max(1, n)
        if recall > best_recall:
            best_recall = float(recall)
            best_alpha = a
    return (best_alpha, 0.0, 1.0 - best_alpha, best_recall)


def score_combined_topk(
    query_ortho: np.ndarray,
    query_sem: np.ndarray,
    prototypes_ortho: np.ndarray,
    prototypes_sem: np.ndarray,
    alpha: float,
    gamma: float,
    k: int,
) -> np.ndarray:
    """Score-level late-combine top-k retrieval.

    Returns top-k atom indices by combined cosine score.
    """
    def _cos_row(q: np.ndarray, protos: np.ndarray) -> np.ndarray:
        qn = float(np.linalg.norm(q))
        if qn < 1e-12:
            return np.zeros(protos.shape[0], dtype=np.float32)
        p = protos.astype(np.float32)
        pn = np.linalg.norm(p, axis=1)
        pn_safe = np.where(pn < 1e-12, 1.0, pn)
        return ((p @ q.astype(np.float32)) / (pn_safe * qn)).astype(np.float32)

    ortho_scores = _cos_row(query_ortho, prototypes_ortho)
    sem_scores = _cos_row(query_sem, prototypes_sem)
    combined = float(alpha) * ortho_scores + float(gamma) * sem_scores
    if k >= combined.shape[0]:
        return np.argsort(-combined).astype(np.int64)
    idx_part = np.argpartition(-combined, k)[:k]
    order = idx_part[np.argsort(-combined[idx_part])]
    return order.astype(np.int64)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest() -> None:
    rng = np.random.default_rng(42)
    n_dim = 512

    # Backward-compat identity: alpha=0, beta=0, gamma=1 on v_sem.
    v_sem = rng.standard_normal(n_dim).astype(np.float32)
    lc_id = LateCombine(alpha=0.0, beta=0.0, gamma=1.0)
    out = lc_id.combine(v_ortho=None, v_morph=None, v_sem=v_sem)
    expected = _l2_normalize(v_sem)
    assert np.allclose(out, expected, atol=1e-6), (
        "backward-compat identity failed: alpha=0,beta=0,gamma=1 must recover "
        "unit-normalized v_sem"
    )
    assert abs(float(np.linalg.norm(out)) - 1.0) < 1e-5, (
        f"output not unit-normed: |out|={float(np.linalg.norm(out)):.6f}"
    )

    # Two-stream weighted sum: alpha=0.5, gamma=0.5.
    v_ortho = rng.standard_normal(n_dim).astype(np.float32)
    lc_eq = LateCombine(alpha=0.5, beta=0.0, gamma=0.5)
    out_eq = lc_eq.combine(v_ortho=v_ortho, v_morph=None, v_sem=v_sem)
    assert abs(float(np.linalg.norm(out_eq)) - 1.0) < 1e-5, (
        "equal-weight output not unit-normed"
    )
    # Should be neither v_ortho alone nor v_sem alone.
    cos_out_ortho = float(np.dot(out_eq, _l2_normalize(v_ortho)))
    cos_out_sem = float(np.dot(out_eq, _l2_normalize(v_sem)))
    assert cos_out_ortho < 0.99, (
        f"equal-weight out too close to v_ortho: cos={cos_out_ortho:.4f}"
    )
    assert cos_out_sem < 0.99, (
        f"equal-weight out too close to v_sem: cos={cos_out_sem:.4f}"
    )

    # All-None error path.
    try:
        lc_id.combine(v_ortho=None, v_morph=None, v_sem=None)
        raise AssertionError("expected ValueError on all-None streams")
    except ValueError:
        pass

    # Score-combined top-k basic sanity: identical prototype tables + same
    # query should give the same top-1 whether alpha=1 or alpha=0.
    N = 20
    prot = rng.standard_normal((N, n_dim)).astype(np.float32)
    q = prot[7].copy()  # target atom 7
    top_all_ortho = int(score_combined_topk(q, q, prot, prot, alpha=1.0, gamma=0.0, k=1)[0])
    top_all_sem = int(score_combined_topk(q, q, prot, prot, alpha=0.0, gamma=1.0, k=1)[0])
    assert top_all_ortho == 7 and top_all_sem == 7, (
        f"self-consistency broken: ortho-only top1={top_all_ortho} sem-only "
        f"top1={top_all_sem} (both should retrieve atom 7)"
    )

    # Weight-fit grid: construct a scenario where sem is discriminative and
    # ortho is noise; grid search should pick alpha close to 0.
    prot_sem = rng.standard_normal((N, n_dim)).astype(np.float32)
    prot_ortho = rng.standard_normal((N, n_dim)).astype(np.float32)
    labels = list(range(N))
    # Queries: sem query == prot_sem[i] + small noise (highly discriminative);
    # ortho query == pure noise (uninformative).
    per_q_sem = [
        prot_sem[i] + 0.05 * rng.standard_normal(n_dim).astype(np.float32)
        for i in range(N)
    ]
    per_q_ortho = [
        rng.standard_normal(n_dim).astype(np.float32) for _ in range(N)
    ]
    best_alpha, best_beta, best_gamma, best_recall = fit_weights_grid_2spoke(
        per_q_ortho, per_q_sem, prot_ortho, prot_sem, labels
    )
    assert best_beta == 0.0, "2-spoke fit should leave beta=0"
    assert abs(best_alpha + best_gamma - 1.0) < 1e-6, (
        f"alpha+gamma should sum to 1: got {best_alpha}+{best_gamma}"
    )
    assert best_alpha <= 0.2, (
        f"expected alpha near 0 when sem is discriminative; got {best_alpha}"
    )
    assert best_recall >= 0.8, (
        f"expected high recall when sem is nearly perfect; got {best_recall}"
    )

    # Reverse scenario: ortho discriminative, sem noise -> alpha near 1.
    per_q_ortho2 = [
        prot_ortho[i] + 0.05 * rng.standard_normal(n_dim).astype(np.float32)
        for i in range(N)
    ]
    per_q_sem2 = [
        rng.standard_normal(n_dim).astype(np.float32) for _ in range(N)
    ]
    best_alpha2, _, best_gamma2, best_recall2 = fit_weights_grid_2spoke(
        per_q_ortho2, per_q_sem2, prot_ortho, prot_sem, labels
    )
    # Note: grid search returns FIRST alpha achieving max recall; when the
    # ortho signal is strong enough to dominate at low alpha, best_alpha2 may
    # be small.  Honest assertion: alpha must be STRICTLY > 0 (ortho used at
    # all) and recall must saturate high.  Cross-check that alpha=0 (sem-only)
    # gives chance-level recall separately.
    assert best_alpha2 > 0.0, (
        f"expected alpha > 0 when ortho is discriminative; got {best_alpha2}"
    )
    assert best_recall2 >= 0.8, (
        f"expected high recall when ortho is nearly perfect; got {best_recall2}"
    )
    # Separate probe: sem-only (alpha=0) on this data should be chance-level.
    _, _, _, recall_sem_only2 = fit_weights_grid_2spoke(
        per_q_ortho2, per_q_sem2, prot_ortho, prot_sem, labels,
        alpha_grid=(0.0,),
    )
    assert recall_sem_only2 <= 0.30, (
        f"sem-only on noise queries should be chance ~0.05, got {recall_sem_only2}"
    )

    print(
        "[late_combine selftest] PASS  "
        f"identity_backcompat=OK  "
        f"unit_normalized=OK  "
        f"fit_sem-discriminative: alpha={best_alpha:.2f} gamma={best_gamma:.2f} "
        f"recall@1={best_recall:.3f}  "
        f"fit_ortho-discriminative: alpha={best_alpha2:.2f} gamma={best_gamma2:.2f} "
        f"recall@1={best_recall2:.3f}",
        flush=True,
    )


if __name__ == "__main__":
    _selftest()
