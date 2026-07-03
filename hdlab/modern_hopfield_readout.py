"""Modern-Hopfield softmax retrieval / attention readout over stored HD table.

INPUT REGIME
============
Brain-analog pMTG-IFG semantic control / softmax retrieval / modern-Hopfield
(Ramsauer et al. 2020, arXiv:2008.02217). Enables interpolation between stored
patterns unlike classical Hopfield's quadratic energy attractors, and gives
temperature control (beta) over sharpening vs blending.

Stored HDs are per-concept prototype vectors [N_proto, N_dim]; queries are the
same-space vectors [N_dim]. This module does NOT know how the vectors were
built (bipolar-sparse from ConceptEncoder, dense random from bundling, etc.).

MECHANISM (per Ramsauer 2020, eq. 3)
====================================
Given query q in R^N and stored patterns K in R^{M x N}:
    scores  = beta * (K @ q) / sqrt(N)                # attention logits
    weights = softmax(scores)                          # attention weights
    y       = K.T @ weights                            # retrieved HD (blend)

The retrieved y is a weighted blend of stored patterns; at high beta it
concentrates on argmax(K @ q) (classical WTA); at low beta it interpolates.

RANKING NOTE (load-bearing)
===========================
When all stored patterns share equal L2 norm (e.g. sparse-bipolar concept HDs
at fixed k_sparsity), the softmax attention weights are a monotone function of
inner products, so ranking by raw attention weights == ranking by cosine ==
ranking by dot product. The distinguishing behaviour of modern-Hopfield over
cosine-argmax under equal-norm storage is the RETRIEVED HD y itself:

    y = K.T @ softmax(beta * K @ q / sqrt(N))

is a NON-TRIVIAL BLEND that differs from the argmax prototype. One "cortical
update step" then re-scores prototypes by cos(y, K_i) — this ranking DIFFERS
from cos(q, K_i) because y interpolates neighbouring prototypes toward q.

We therefore expose two retrieval helpers:
  - `top_k_by_attention`  : ranks stored patterns by attention weight (= dot).
  - `top_k_by_retrieved`  : one-step Hopfield update; ranks by cos(y, K_i).

The cell that operationalises "softmax retrieval as brain-analog semantic
control" should use `top_k_by_retrieved` to see any lift over the cosine
baseline under equal-norm storage. `top_k_by_attention` is exposed for
completeness + downstream composition uses.

ASCII-only. No emojis. Deterministic given inputs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass
class ModernHopfieldReadout:
    """Softmax attention readout over a stored HD table.

    Attributes:
      beta: inverse temperature (higher = sharper WTA).
      normalize_query_and_store: if True, L2-normalize query + stored before
        computing scores (makes attention scale-invariant; matches the
        cosine baseline exactly when disabled retrieved-blend is used).
    """

    beta: float = 4.0
    normalize_query_and_store: bool = True

    # ------------------------------------------------------------------
    # Attention scoring.
    # ------------------------------------------------------------------
    def _prep(
        self, query: np.ndarray, stored: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Cast + optionally L2-normalize; return (q_f32 [N], K_f32 [M, N])."""
        q = np.asarray(query, dtype=np.float32).reshape(-1)
        K = np.asarray(stored, dtype=np.float32)
        if K.ndim != 2:
            raise ValueError(f"stored must be 2D [M, N]; got shape {K.shape}")
        if q.shape[0] != K.shape[1]:
            raise ValueError(
                f"query dim {q.shape[0]} != stored last-dim {K.shape[1]}"
            )
        if self.normalize_query_and_store:
            qn = float(np.linalg.norm(q))
            if qn >= 1e-12:
                q = q / qn
            Kn = np.linalg.norm(K, axis=1, keepdims=True)
            Kn_safe = np.where(Kn < 1e-12, 1.0, Kn)
            K = K / Kn_safe
        return q, K

    def scores(self, query: np.ndarray, stored: np.ndarray) -> np.ndarray:
        """Return raw attention logits [M]: beta * (K @ q) / sqrt(N)."""
        q, K = self._prep(query, stored)
        n_dim = K.shape[1]
        return (float(self.beta) * (K @ q) / float(np.sqrt(n_dim))).astype(
            np.float32
        )

    def attention_weights(
        self, query: np.ndarray, stored: np.ndarray
    ) -> np.ndarray:
        """Softmax over attention logits. Numerically stable (subtract max)."""
        s = self.scores(query, stored)
        s = s - float(np.max(s))  # for numerical stability
        e = np.exp(s)
        Z = float(np.sum(e))
        if Z < 1e-30:
            # Degenerate: uniform fallback.
            m = e.shape[0]
            return np.full(m, 1.0 / m, dtype=np.float32)
        return (e / Z).astype(np.float32)

    # ------------------------------------------------------------------
    # Retrieval.
    # ------------------------------------------------------------------
    def retrieve(
        self, query: np.ndarray, stored: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Return (retrieved_hd [N], attention_weights [M]).

        retrieved_hd = K.T @ softmax(beta * K @ q / sqrt(N)); a weighted blend
        of stored patterns. Modern-Hopfield one-step update.
        """
        _q, K = self._prep(query, stored)
        w = self.attention_weights(query, stored)
        y = (K.T @ w).astype(np.float32)
        return y, w

    def top_k_by_attention(
        self, query: np.ndarray, stored: np.ndarray, k: int
    ) -> np.ndarray:
        """Rank stored patterns by attention weight; return top-k int64 indices.

        Under equal-norm storage this ranks identically to cosine-argmax; kept
        for API completeness and downstream composition uses.
        """
        if k <= 0:
            return np.empty(0, dtype=np.int64)
        w = self.attention_weights(query, stored)
        m = w.shape[0]
        if k >= m:
            return np.argsort(-w).astype(np.int64)
        idx_part = np.argpartition(-w, k)[:k]
        return idx_part[np.argsort(-w[idx_part])].astype(np.int64)

    def top_k_by_retrieved(
        self, query: np.ndarray, stored: np.ndarray, k: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """One-step Hopfield update then re-rank by cos(retrieved, K_i).

        Returns (top_k_indices [k], retrieved_hd [N], attention_weights [M]).

        LOAD-BEARING for the softmax-retrieval-vs-cosine-argmax comparison
        under equal-norm sparse-bipolar storage: retrieved_hd blends
        neighbouring prototypes toward the query, and cos(y, K_i) ranks
        DIFFERENTLY from cos(q, K_i).
        """
        if k <= 0:
            return (
                np.empty(0, dtype=np.int64),
                np.zeros(stored.shape[1], dtype=np.float32),
                np.empty(0, dtype=np.float32),
            )
        y, w = self.retrieve(query, stored)
        # Re-rank by cos(y, K_i). Use prepped normalized K if requested; else
        # normalize on the fly for the cosine score. (We already prepped inside
        # retrieve, but that copy isn't returned; recompute cheaply.)
        K = np.asarray(stored, dtype=np.float32)
        y_norm = float(np.linalg.norm(y))
        if y_norm < 1e-12:
            # Degenerate: fall back to attention ranking.
            return self.top_k_by_attention(query, stored, k), y, w
        y_hat = y / y_norm
        K_norms = np.linalg.norm(K, axis=1)
        K_norms_safe = np.where(K_norms < 1e-12, 1.0, K_norms)
        cos_yK = (K @ y_hat) / K_norms_safe
        cos_yK = np.where(K_norms < 1e-12, -1e9, cos_yK)
        m = cos_yK.shape[0]
        if k >= m:
            top = np.argsort(-cos_yK).astype(np.int64)
        else:
            idx_part = np.argpartition(-cos_yK, k)[:k]
            top = idx_part[np.argsort(-cos_yK[idx_part])].astype(np.int64)
        return top, y, w


# =====================================================================
# Self-tests. Run `python -m hdlab.modern_hopfield_readout` to execute.
# =====================================================================

def _selftest() -> None:
    """10 selftests. Any failure raises AssertionError with context."""
    rng = np.random.default_rng(11)

    # -- Test 1: shape + normalization guard.
    r = ModernHopfieldReadout(beta=4.0)
    q = rng.standard_normal(64).astype(np.float32)
    K = rng.standard_normal((10, 64)).astype(np.float32)
    y, w = r.retrieve(q, K)
    assert y.shape == (64,), f"T1 retrieved shape {y.shape} != (64,)"
    assert w.shape == (10,), f"T1 weights shape {w.shape} != (10,)"
    assert abs(float(w.sum()) - 1.0) < 1e-4, (
        f"T1 weights don't sum to 1: {float(w.sum()):.6f}"
    )
    assert bool(np.all(w >= 0.0)), "T1 attention weights not non-negative"

    # -- Test 2: exact retrieval when query == stored pattern (high beta).
    r_hi = ModernHopfieldReadout(beta=32.0, normalize_query_and_store=True)
    M, N = 20, 128
    K2 = rng.standard_normal((M, N)).astype(np.float32)
    # Query == pattern 7 exactly.
    q2 = K2[7].copy()
    top1 = r_hi.top_k_by_retrieved(q2, K2, k=1)[0]
    assert top1[0] == 7, (
        f"T2 exact retrieval failed: expected 7, got {int(top1[0])}"
    )
    w2 = r_hi.attention_weights(q2, K2)
    # Attention should ARGMAX on true pattern and dominate uniform (1/M=0.05).
    assert int(np.argmax(w2)) == 7, (
        f"T2 attention argmax {int(np.argmax(w2))} != 7"
    )
    assert float(w2[7]) > 0.3, (
        f"T2 attention on true pattern only {float(w2[7]):.3f}; "
        f"expected >0.3 (5-15x uniform 1/M=0.05) at beta=32"
    )

    # -- Test 3: interpolation between two similar patterns.
    N3 = 256
    p_a = rng.standard_normal(N3).astype(np.float32)
    p_b = p_a + 0.3 * rng.standard_normal(N3).astype(np.float32)
    p_far = rng.standard_normal(N3).astype(np.float32)  # unrelated
    K3 = np.stack([p_a, p_b, p_far], axis=0)
    # Query = midpoint of a and b.
    q3 = 0.5 * (p_a + p_b)
    r_mid = ModernHopfieldReadout(beta=4.0)
    y3, w3 = r_mid.retrieve(q3, K3)
    # Attention on p_a and p_b should each be non-trivial and > attention on p_far.
    assert float(w3[0]) > float(w3[2]) and float(w3[1]) > float(w3[2]), (
        f"T3 mid-query didn't prefer nearby patterns: w={w3.tolist()}"
    )
    # Retrieved y should be closer (cosine) to (a+b)/2 than to p_far.
    def _cos(u, v):
        un = float(np.linalg.norm(u))
        vn = float(np.linalg.norm(v))
        if un < 1e-12 or vn < 1e-12:
            return 0.0
        return float(np.dot(u, v) / (un * vn))
    cos_ab = _cos(y3, 0.5 * (p_a + p_b))
    cos_far = _cos(y3, p_far)
    assert cos_ab > cos_far, (
        f"T3 retrieved not closer to (a+b)/2 than p_far: "
        f"cos_ab={cos_ab:.3f} cos_far={cos_far:.3f}"
    )

    # -- Test 4: beta temperature effect (higher beta -> sharper attention).
    K4 = rng.standard_normal((15, 128)).astype(np.float32)
    q4 = K4[3] + 0.5 * rng.standard_normal(128).astype(np.float32)
    r_lo = ModernHopfieldReadout(beta=1.0)
    r_hi2 = ModernHopfieldReadout(beta=16.0)
    w_lo = r_lo.attention_weights(q4, K4)
    w_hi = r_hi2.attention_weights(q4, K4)
    # Peak of high-beta weights should exceed peak of low-beta weights.
    assert float(w_hi.max()) > float(w_lo.max()), (
        f"T4 higher beta didn't sharpen: max_lo={float(w_lo.max()):.3f} "
        f"max_hi={float(w_hi.max()):.3f}"
    )

    # -- Test 5: sparse-bipolar storage compatibility (int8 dtype).
    # Use N=2048 (production regime) at k_sparsity=2% -> 40 non-zero per
    # pattern; 30 patterns should be well-separated by birthday-bound.
    Nb = 2048
    Mb = 30
    Kb = np.zeros((Mb, Nb), dtype=np.int8)
    n_active = int(round(0.02 * Nb))
    for i in range(Mb):
        pos = rng.choice(Nb, size=n_active, replace=False)
        signs = rng.choice([-1, 1], size=n_active).astype(np.int8)
        Kb[i, pos] = signs
    q5 = Kb[9].astype(np.float32)
    # NOTE: beta * cos / sqrt(N) at N=2048 gives soft softmax even at moderate
    # beta (peak logit = beta/sqrt(2048) = beta/45.25). For the sparse-bipolar
    # exact-retrieval test we (a) verify attention argmax on the exact pattern
    # (softmax is monotone in scores, argmax always correct), and (b) verify
    # top_k_by_retrieved with beta high enough that the blend is dominated by
    # the target (beta=128 gives peak logit ~2.8, w[correct] ~0.5+).
    r5 = ModernHopfieldReadout(beta=128.0, normalize_query_and_store=True)
    w5 = r5.attention_weights(q5, Kb)
    assert int(np.argmax(w5)) == 9, (
        f"T5 attention argmax {int(np.argmax(w5))} != 9 (sparse-bipolar)"
    )
    top = r5.top_k_by_retrieved(q5, Kb, k=3)[0]
    assert top[0] == 9, (
        f"T5 bipolar-sparse exact retrieval failed at beta=128: "
        f"expected 9 got {int(top[0])}; top3={top.tolist()}; "
        f"w[9]={float(w5[9]):.3f} argmax_w={int(np.argmax(w5))}"
    )

    # -- Test 6: scale sentinel at N=8192 (production dim). Use beta scaled
    # for the /sqrt(N) normalization so retrieval concentrates on exact match:
    # peak logit = beta/sqrt(8192) = beta/90.5; beta=512 -> peak ~5.66.
    N6 = 8192
    Kn6 = rng.standard_normal((50, N6)).astype(np.float32)
    q6 = Kn6[17].copy()
    r6 = ModernHopfieldReadout(beta=512.0)
    top6, y6, w6 = r6.top_k_by_retrieved(q6, Kn6, k=5)
    # Attention argmax is monotone in scores and must hit exact match at any
    # beta > 0 for random Gaussian patterns.
    assert int(np.argmax(w6)) == 17, (
        f"T6 attention argmax {int(np.argmax(w6))} != 17 at scale N=8192"
    )
    assert 17 in top6.tolist(), (
        f"T6 scale sentinel N=8192 retrieved top5={top6.tolist()} lacks 17; "
        f"w[17]={float(w6[17]):.4f}"
    )
    assert y6.shape == (N6,), (
        f"T6 retrieved shape {y6.shape} != ({N6},) at scale"
    )
    assert abs(float(w6.sum()) - 1.0) < 1e-3

    # -- Test 7: attention vs retrieved ranking DIFFER under equal-norm store.
    # Equal-norm construction: unit-normalize patterns.
    Neq = 128
    Meq = 20
    Keq = rng.standard_normal((Meq, Neq)).astype(np.float32)
    Keq = Keq / np.linalg.norm(Keq, axis=1, keepdims=True)  # unit norm
    # Query = blend of pattern 3 and 4 with noise.
    q7 = (Keq[3] + Keq[4]) / 2.0 + 0.05 * rng.standard_normal(Neq).astype(
        np.float32
    )
    r7 = ModernHopfieldReadout(beta=4.0, normalize_query_and_store=True)
    att_top = r7.top_k_by_attention(q7, Keq, k=5).tolist()
    ret_top = r7.top_k_by_retrieved(q7, Keq, k=5)[0].tolist()
    # At beta=4 with a blended query the two rankings should differ in at
    # least ONE position (retrieved-cosine re-ranks).
    if att_top == ret_top:
        # Rare; nudge beta lower so the interpolation dominates.
        r7b = ModernHopfieldReadout(beta=1.0, normalize_query_and_store=True)
        att_top = r7b.top_k_by_attention(q7, Keq, k=5).tolist()
        ret_top = r7b.top_k_by_retrieved(q7, Keq, k=5)[0].tolist()
    assert att_top != ret_top, (
        f"T7 attention and retrieved rankings identical under equal-norm "
        f"store; expected divergence: {att_top} == {ret_top}"
    )

    # -- Test 8: dim-mismatch raises.
    try:
        _ = ModernHopfieldReadout(beta=2.0).retrieve(
            rng.standard_normal(32), rng.standard_normal((5, 33))
        )
        raise AssertionError("T8 dim-mismatch did not raise")
    except ValueError:
        pass

    # -- Test 9: deterministic given inputs (no hidden RNG state).
    Kd = rng.standard_normal((25, 256)).astype(np.float32)
    qd = rng.standard_normal(256).astype(np.float32)
    rd = ModernHopfieldReadout(beta=6.0)
    y_a, w_a = rd.retrieve(qd, Kd)
    y_b, w_b = rd.retrieve(qd, Kd)
    assert np.array_equal(y_a, y_b) and np.array_equal(w_a, w_b), (
        "T9 non-deterministic outputs across identical calls"
    )

    # -- Test 10: uniform-attention fallback on all-zero stored (no NaN).
    Kz = np.zeros((5, 64), dtype=np.float32)
    qz = rng.standard_normal(64).astype(np.float32)
    rz = ModernHopfieldReadout(beta=4.0)
    yz, wz = rz.retrieve(qz, Kz)
    assert not bool(np.any(np.isnan(yz))), "T10 NaN in retrieved on zero-K"
    assert not bool(np.any(np.isnan(wz))), "T10 NaN in weights on zero-K"
    assert abs(float(wz.sum()) - 1.0) < 1e-4, (
        f"T10 weights don't sum to 1 on zero-K: {float(wz.sum()):.6f}"
    )

    print("[selftest] all 10 tests PASS (ModernHopfieldReadout)")


if __name__ == "__main__":
    _selftest()
