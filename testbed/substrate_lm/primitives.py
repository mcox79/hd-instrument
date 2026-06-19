"""4-primitive substrate-native LM core.

ALGEBRA (load-bearing reference; PROT-022 selftests at module bottom):

  Primitive 1 -- Outer-product Hopfield write (re-exported from substrate_audit).
      W <- W + (1/N) xi xi^T
      Standard Hebbian rule. Symmetric, PSD-tending under streaming bipolar inputs.

  Primitive 2 -- Anti-Hebbian bipartite contrastive (NEW).
      Given positive pair (xi_pos_a, xi_pos_b) and negative pair (xi_neg_a, xi_neg_b),
          W <- W + (1/N)(xi_pos_a xi_pos_b^T + xi_pos_b xi_pos_a^T)
                  - (1/N)(xi_neg_a xi_neg_b^T + xi_neg_b xi_neg_a^T)
      Symmetric (undirected substrate); pulls positives together, pushes negatives apart.
      Substitutes for InfoNCE / triplet loss in a NO-GRADIENT setting.

  Primitive 3 -- Hierarchical recurrent retrieval (NEW).
      For t in range(n_steps):
          xi_{t+1} = sign(W @ xi_t)
      Default n_steps = 3. Substitutes for attention-as-routing; iterative
      pattern lookup that cleans noise via repeated thresholded matvec.

  Primitive 4 -- Stacked independent-W composition (NEW).
      4 layers, each with its own W_k. Forward pass:
          h_0 = x
          h_{k+1} = recurrent_retrieve(W_k, h_k, n_steps)
      Each W_k must satisfy alpha_k = M_k / N < alpha_c ~= 0.138 (Error-Correction-Chain
      criterion: max_k alpha_k < alpha_c, NOT sum_k; no cumulative-alpha cliff).

ASCII-only; bipolar codes in {-1, +1}^N as float32; W is (N, N) float32.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np

# Re-use the canonical Hopfield write from substrate_audit (Primitive 1).
_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
from testbed.llm_integration.substrate_audit import (  # noqa: E402
    hebbian_write,
    build_W_from_patterns,
    retrieval_cosine,
)


# Hopfield critical capacity (single-layer; per Hopfield 1982 / Amit et al. 1985).
ALPHA_C_HOPFIELD: float = 0.138


__all__ = [
    "hebbian_write",
    "build_W_from_patterns",
    "retrieval_cosine",
    "anti_hebbian_contrastive_update",
    "hierarchical_recurrent_retrieve",
    "StackedSubstrate",
    "primitive_health_report",
    "ALPHA_C_HOPFIELD",
]


# ---------------------------------------------------------------------------
# Primitive 2: anti-Hebbian bipartite contrastive
# ---------------------------------------------------------------------------

def anti_hebbian_contrastive_update(
    W: np.ndarray,
    xi_pos_a: np.ndarray,
    xi_pos_b: np.ndarray,
    xi_neg_a: np.ndarray,
    xi_neg_b: np.ndarray,
    lr: float = 1.0,
) -> np.ndarray:
    """Symmetric anti-Hebbian bipartite contrastive update.

        W <- W + (lr/N) (xi_pos_a xi_pos_b^T + xi_pos_b xi_pos_a^T)
              - (lr/N) (xi_neg_a xi_neg_b^T + xi_neg_b xi_neg_a^T)

    Pulls the positive pair together (raises cos(W @ pos_a, pos_b)) and pushes
    the negative pair apart (lowers cos(W @ neg_a, neg_b)). Substrate-native
    contrastive: NO gradient, NO logsumexp, NO temperature.

    Args:
        W:         (N, N) float32 substrate (modified-out-of-place; returns new W).
        xi_pos_a:  (N,) float32 bipolar codeword (positive pair, "anchor side").
        xi_pos_b:  (N,) float32 bipolar codeword (positive pair, "partner side").
        xi_neg_a:  (N,) float32 bipolar codeword (negative pair, anchor).
        xi_neg_b:  (N,) float32 bipolar codeword (negative pair, partner).
        lr:        learning-rate scalar (default 1.0; matches Hebbian scale).
    """
    N = W.shape[0]
    coef = lr / float(N)
    pos = np.outer(xi_pos_a, xi_pos_b) + np.outer(xi_pos_b, xi_pos_a)
    neg = np.outer(xi_neg_a, xi_neg_b) + np.outer(xi_neg_b, xi_neg_a)
    return (W + coef * pos.astype(W.dtype) - coef * neg.astype(W.dtype)).astype(W.dtype)


# ---------------------------------------------------------------------------
# Primitive 3: hierarchical recurrent retrieval
# ---------------------------------------------------------------------------

def hierarchical_recurrent_retrieve(
    W: np.ndarray,
    xi_query: np.ndarray,
    n_steps: int = 3,
    return_trajectory: bool = False,
) -> np.ndarray:
    """Multi-step pattern lookup. Iteratively refines query via sign(W @ x).

        x_0 = xi_query
        x_{t+1} = sign(W @ x_t)
        return x_{n_steps}

    Substitutes for attention-as-routing: instead of softmax-weighted retrieval,
    the substrate's quadratic energy landscape pulls a noisy query toward the
    nearest stored attractor via fixed-point iteration.

    Args:
        W:        (N, N) float32 substrate.
        xi_query: (N,) float32 bipolar (or near-bipolar) query.
        n_steps:  number of refinement steps (default 3).
        return_trajectory: if True, return list of all intermediate states.

    Returns:
        (N,) float32 bipolar attractor (or list of (N,) if return_trajectory).
    """
    x = xi_query.astype(W.dtype, copy=True)
    traj: List[np.ndarray] = [x.copy()] if return_trajectory else []
    for _ in range(max(0, int(n_steps))):
        y = W @ x
        # sign with deterministic tiebreak: zero -> +1
        x = np.where(y >= 0.0, 1.0, -1.0).astype(W.dtype)
        if return_trajectory:
            traj.append(x.copy())
    if return_trajectory:
        return traj  # type: ignore[return-value]
    return x


# ---------------------------------------------------------------------------
# Primitive 4: stacked independent-W composition
# ---------------------------------------------------------------------------

class StackedSubstrate:
    """4-layer (configurable) substrate with INDEPENDENT W per layer.

    Information flow:
        h_0 = x
        h_{k+1} = hierarchical_recurrent_retrieve(W_k, h_k, n_steps_per_layer)
        y = h_n_layers

    Each layer's alpha_k = M_k / N must stay below alpha_c per the
    Error-Correction-Chain criterion (max_k alpha_k < alpha_c). The class
    refuses to write past alpha_max (default 0.10, well below alpha_c=0.138).
    """

    def __init__(
        self,
        n_layers: int = 4,
        N: int = 2048,
        alpha_max: float = 0.10,
        n_steps_per_layer: int = 3,
        dtype: np.dtype = np.float32,
    ) -> None:
        if n_layers < 1:
            raise ValueError("n_layers must be >= 1")
        if N < 8:
            raise ValueError("N must be >= 8 for non-degenerate substrate")
        if not (0.0 < alpha_max < ALPHA_C_HOPFIELD):
            raise ValueError(
                f"alpha_max={alpha_max} must lie in (0, {ALPHA_C_HOPFIELD}) per "
                f"Error-Correction-Chain criterion"
            )
        self.n_layers = int(n_layers)
        self.N = int(N)
        self.alpha_max = float(alpha_max)
        self.n_steps_per_layer = int(n_steps_per_layer)
        self.dtype = np.dtype(dtype)
        self.Ws: List[np.ndarray] = [
            np.zeros((self.N, self.N), dtype=self.dtype) for _ in range(self.n_layers)
        ]
        # writes_per_layer[k] counts effective pattern-equivalents stored in W_k.
        # Both hebbian_write and anti_hebbian_contrastive_update count as +1 each
        # (each contributes ~one rank-1 (or rank-2 symmetric) update).
        self.writes_per_layer: List[int] = [0] * self.n_layers

    # --- alpha tracking ---------------------------------------------------

    def alpha(self, layer: int) -> float:
        return self.writes_per_layer[layer] / float(self.N)

    def alphas(self) -> List[float]:
        return [self.alpha(k) for k in range(self.n_layers)]

    def max_alpha(self) -> float:
        return max(self.alphas()) if self.n_layers > 0 else 0.0

    def layer_full(self, layer: int) -> bool:
        return self.alpha(layer) >= self.alpha_max

    def any_layer_full(self) -> bool:
        return any(self.layer_full(k) for k in range(self.n_layers))

    # --- write paths ------------------------------------------------------

    def write_hebbian(self, layer: int, xi: np.ndarray) -> bool:
        """Apply Hopfield outer-product write to layer-k. Returns True iff written."""
        if self.layer_full(layer):
            return False
        self.Ws[layer] = hebbian_write(self.Ws[layer], xi.astype(self.dtype))
        self.writes_per_layer[layer] += 1
        return True

    def write_contrastive(
        self,
        layer: int,
        xi_pos_a: np.ndarray,
        xi_pos_b: np.ndarray,
        xi_neg_a: np.ndarray,
        xi_neg_b: np.ndarray,
        lr: float = 1.0,
    ) -> bool:
        """Apply anti-Hebbian bipartite contrastive update to layer-k."""
        if self.layer_full(layer):
            return False
        self.Ws[layer] = anti_hebbian_contrastive_update(
            self.Ws[layer],
            xi_pos_a.astype(self.dtype),
            xi_pos_b.astype(self.dtype),
            xi_neg_a.astype(self.dtype),
            xi_neg_b.astype(self.dtype),
            lr=lr,
        )
        self.writes_per_layer[layer] += 1
        return True

    # --- forward (retrieval) ---------------------------------------------

    def forward(self, x: np.ndarray, n_steps: Optional[int] = None) -> np.ndarray:
        """Stacked recurrent retrieval through all n_layers."""
        steps = self.n_steps_per_layer if n_steps is None else int(n_steps)
        h = x.astype(self.dtype, copy=True)
        for k in range(self.n_layers):
            h = hierarchical_recurrent_retrieve(self.Ws[k], h, n_steps=steps)
        return h

    def forward_with_trace(self, x: np.ndarray) -> List[np.ndarray]:
        """Returns h_0, h_1, ..., h_{n_layers}."""
        trace = [x.astype(self.dtype, copy=True)]
        for k in range(self.n_layers):
            trace.append(
                hierarchical_recurrent_retrieve(
                    self.Ws[k], trace[-1], n_steps=self.n_steps_per_layer
                )
            )
        return trace


# ---------------------------------------------------------------------------
# Primitive-health report (for HP "no primitive collapse" gate)
# ---------------------------------------------------------------------------

def _safe_max_eigenvalue(W: np.ndarray, sample_cap: int = 1024) -> float:
    """Largest eigenvalue magnitude of symmetric W. Uses dense eigh for small N,
    Lanczos-equivalent power iteration for large N. Returns float."""
    N = W.shape[0]
    if N <= sample_cap:
        try:
            eigs = np.linalg.eigvalsh(W.astype(np.float64))
            return float(np.max(np.abs(eigs)))
        except np.linalg.LinAlgError:
            return float("nan")
    # Power iteration (matches symmetric W ; ~20 iters fine for substrate eigvals).
    rng = np.random.default_rng(0)
    v = rng.standard_normal(N).astype(np.float64)
    v /= max(np.linalg.norm(v), 1e-30)
    lam = 0.0
    Wf = W.astype(np.float64, copy=False)
    for _ in range(20):
        w = Wf @ v
        lam = float(np.linalg.norm(w))
        if lam < 1e-30:
            return 0.0
        v = w / lam
    return lam


def primitive_health_report(stack: "StackedSubstrate") -> dict:
    """Per-layer alpha, max-|eig|, frobenius-norm, condition-number proxy.

    Used by the experiment script's HP gate ("all primitives operational
    throughout training; no primitive collapse mid-run").
    """
    per_layer = []
    any_collapse = False
    for k in range(stack.n_layers):
        W = stack.Ws[k]
        alpha_k = stack.alpha(k)
        fro = float(np.linalg.norm(W))
        lam_max = _safe_max_eigenvalue(W)
        # NaN / inf == collapse
        finite = np.isfinite([fro, lam_max]).all()
        # Frobenius blow-up (>> sqrt(N) * lam_max) suggests numerical instability.
        # Empty W (no writes) is NOT a collapse -- it's just unused.
        collapsed = (not finite) or (alpha_k > 0 and fro < 1e-10)
        if collapsed:
            any_collapse = True
        per_layer.append(
            {
                "layer": int(k),
                "alpha": float(alpha_k),
                "writes": int(stack.writes_per_layer[k]),
                "fro_norm": fro,
                "max_abs_eig": lam_max,
                "collapsed": bool(collapsed),
            }
        )
    return {
        "n_layers": stack.n_layers,
        "N": stack.N,
        "alpha_max_observed": stack.max_alpha(),
        "alpha_max_threshold": stack.alpha_max,
        "alpha_c_hopfield": ALPHA_C_HOPFIELD,
        "any_primitive_collapse": bool(any_collapse),
        "per_layer": per_layer,
    }


# ---------------------------------------------------------------------------
# PROT-022 self-tests
# ---------------------------------------------------------------------------

def _selftest_primitive_1_hopfield_write() -> None:
    """Primitive 1: standard Hopfield write recovers stored bipolar pattern."""
    rng = np.random.default_rng(1)
    N = 256
    xi = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    W = np.zeros((N, N), dtype=np.float32)
    W = hebbian_write(W, xi)
    # W @ xi should align with xi (cosine ~ 1 since W = xi xi^T / N, so W @ xi = xi).
    cos = retrieval_cosine(W, xi)
    assert cos > 0.99, f"P1 hebbian_write: cos(W@xi, xi)={cos}, expected ~1"
    print(f"[PROT-022 P1] PASS hebbian_write cos={cos:.4f}", flush=True)


def _selftest_primitive_2_anti_hebbian_contrastive() -> None:
    """Primitive 2: anti-Hebbian raises pos-cos and lowers neg-cos vs random init."""
    rng = np.random.default_rng(2)
    N = 256
    pos_a = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    pos_b = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    neg_a = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    neg_b = rng.choice([-1.0, 1.0], size=N).astype(np.float32)

    # Random W with the same scale a Hebbian write would produce.
    W0 = rng.standard_normal((N, N)).astype(np.float32) * (1.0 / np.sqrt(N))

    def _pair_cos(W, a, b):
        y = W @ a
        nb = float(np.linalg.norm(b)); ny = float(np.linalg.norm(y))
        if nb < 1e-30 or ny < 1e-30:
            return 0.0
        return float((y @ b) / (nb * ny))

    pos_cos_0 = _pair_cos(W0, pos_a, pos_b)
    neg_cos_0 = _pair_cos(W0, neg_a, neg_b)

    # Apply a strong contrastive update.
    W1 = anti_hebbian_contrastive_update(W0, pos_a, pos_b, neg_a, neg_b, lr=10.0)

    pos_cos_1 = _pair_cos(W1, pos_a, pos_b)
    neg_cos_1 = _pair_cos(W1, neg_a, neg_b)

    # Positive partner alignment should rise.
    assert pos_cos_1 > pos_cos_0, (
        f"P2 anti-Hebbian: pos_cos did not rise ({pos_cos_0:.4f} -> {pos_cos_1:.4f})"
    )
    # Negative partner alignment should fall.
    assert neg_cos_1 < neg_cos_0, (
        f"P2 anti-Hebbian: neg_cos did not fall ({neg_cos_0:.4f} -> {neg_cos_1:.4f})"
    )
    print(
        f"[PROT-022 P2] PASS anti-Hebbian pos_cos {pos_cos_0:+.4f}->{pos_cos_1:+.4f} "
        f"neg_cos {neg_cos_0:+.4f}->{neg_cos_1:+.4f}",
        flush=True,
    )


def _selftest_primitive_3_recurrent_retrieve() -> None:
    """Primitive 3: noisy query gets cleaned by recurrent retrieval."""
    rng = np.random.default_rng(3)
    N = 512
    M = 8
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    W = build_W_from_patterns(Xi)

    target = Xi[0]
    # Flip ~15% of bits -> noisy query.
    n_flip = int(0.15 * N)
    idx = rng.choice(N, size=n_flip, replace=False)
    noisy = target.copy()
    noisy[idx] *= -1.0

    def _cos(a, b):
        na = float(np.linalg.norm(a)); nb = float(np.linalg.norm(b))
        if na < 1e-30 or nb < 1e-30:
            return 0.0
        return float((a @ b) / (na * nb))

    cos_initial = _cos(noisy, target)
    cleaned = hierarchical_recurrent_retrieve(W, noisy, n_steps=3)
    cos_final = _cos(cleaned, target)

    assert cos_final > cos_initial, (
        f"P3 recurrent retrieve did not clean noise: "
        f"cos_initial={cos_initial:.4f} -> cos_final={cos_final:.4f}"
    )
    assert cos_final > 0.9, (
        f"P3 recurrent retrieve: final cos {cos_final:.4f} should be >0.9 "
        f"for 15% noise at alpha={M/N:.3f}"
    )
    print(
        f"[PROT-022 P3] PASS recurrent retrieve cos {cos_initial:.4f}->{cos_final:.4f}",
        flush=True,
    )


def _selftest_primitive_4_stacked_composition() -> None:
    """Primitive 4: 4 stacked Ws at alpha<=0.10 preserve a clean stored pattern."""
    rng = np.random.default_rng(4)
    N = 256
    n_layers = 4
    M_per_layer = int(0.08 * N)  # alpha = 0.08 < alpha_max = 0.10 < alpha_c = 0.138

    stack = StackedSubstrate(
        n_layers=n_layers, N=N, alpha_max=0.10, n_steps_per_layer=3
    )

    # Each layer learns its OWN M independent patterns. To make the forward pass
    # meaningful, we store the SAME "shared pattern" xi_shared in EVERY layer
    # so it is a fixed point of every layer. Then we forward and check it stays.
    xi_shared = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    for k in range(n_layers):
        # Store the shared pattern + M_per_layer - 1 layer-specific decoys.
        stack.write_hebbian(k, xi_shared)
        for _ in range(M_per_layer - 1):
            decoy = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
            stack.write_hebbian(k, decoy)

    # Forward the shared pattern through the stack.
    out = stack.forward(xi_shared)
    cos = float(xi_shared @ out / (np.linalg.norm(xi_shared) * np.linalg.norm(out)))

    assert cos > 0.95, (
        f"P4 stacked composition: shared pattern not preserved (cos={cos:.4f}) at "
        f"alpha={stack.max_alpha():.3f} (alpha_max={stack.alpha_max}, "
        f"alpha_c={ALPHA_C_HOPFIELD})"
    )

    # No layer should have collapsed.
    report = primitive_health_report(stack)
    assert not report["any_primitive_collapse"], (
        f"P4 health report flagged collapse: {report}"
    )
    print(
        f"[PROT-022 P4] PASS stacked-W preserves shared pattern cos={cos:.4f}, "
        f"max_alpha={stack.max_alpha():.3f}, no collapse",
        flush=True,
    )


def _selftest() -> None:
    _selftest_primitive_1_hopfield_write()
    _selftest_primitive_2_anti_hebbian_contrastive()
    _selftest_primitive_3_recurrent_retrieve()
    _selftest_primitive_4_stacked_composition()
    print("[PROT-022] ALL 4 primitive selftests PASS", flush=True)


if __name__ == "__main__":
    _selftest()
