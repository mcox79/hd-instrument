"""Beta-regime guard for Modern-Hopfield softmax in multi-hop chains.

Would-have-caught test (research_5cell_cross_HARDFAIL_synthesis_2026-06-24):

  Two cells (exp_substrate_resonator_multihop_integration_v1 +
  exp_substrate_soft_chain_dfe_multihop_v1) shipped with beta=N_DIM=8192 on
  multi-hop chains. At that beta, softmax(beta * top_cos) is a Dirac delta at
  argmax; the soft Modern-Hopfield bundle reduces to E[argmax] exactly --
  identical to naive_chain. Empirical proof: per-seed top1 values were BIT-
  IDENTICAL between RESONATOR_HARD and SOFT_CHAIN arms (0.61/0.61, 0.645/0.645,
  0.64/0.64). The soft mechanism was never exercised.

This test asserts two things:

  (T1) softmax-entropy at beta=10 over K=20 distinct top similarities is
       > 0.1 nats. This is the "soft posterior carries information"
       precondition; if violated the soft mechanism degenerates.

  (T2) the hdlab.multi_hop.iter_cleanup_chain function emits a UserWarning
       when called with beta >= n_dim/2 on a chain of length >= 2.
"""
from __future__ import annotations

import warnings

import numpy as np
import pytest
import torch

from hdlab.multi_hop import iter_cleanup_chain
from hdlab.kg_traversal import KGStore


def _softmax_entropy_nats(scores: np.ndarray) -> float:
    """Entropy in nats of softmax(scores) along the last axis."""
    z = scores - scores.max()
    p = np.exp(z) / np.exp(z).sum()
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def test_beta_10_soft_posterior_has_information() -> None:
    """T1: softmax-entropy at beta=10 over K=20 distinct similarities > 0.1 nats.

    Uses cosine similarities in the substrate's empirically observed range
    (top-1 ~ 0.98 down to top-20 ~ 0.88) to reflect the actual regime where
    the soft DFE mechanism is supposed to operate.
    """
    K = 20
    # 20 distinct similarities decreasing linearly from 0.98 to 0.88
    top_conf = np.linspace(0.98, 0.88, K).astype(np.float64)
    beta = 10.0
    ent = _softmax_entropy_nats(beta * top_conf)
    assert ent > 0.1, (
        f"beta=10 over K={K} distinct similarities collapsed: entropy={ent:.6f} nats; "
        f"soft posterior carries no information"
    )


def test_beta_n_dim_collapses_to_dirac() -> None:
    """Cross-check: beta=N_DIM=8192 produces a near-Dirac (entropy < 1e-3 nats).

    This is the bug regime. Asserting the collapse itself locks in the witness
    that motivated the guard.
    """
    K = 20
    top_conf = np.linspace(0.98, 0.88, K).astype(np.float64)
    beta = 8192.0
    ent = _softmax_entropy_nats(beta * top_conf)
    assert ent < 1e-3, (
        f"beta=8192 unexpectedly retained entropy={ent:.6e} nats; expected Dirac"
    )


def test_iter_cleanup_chain_warns_on_high_beta_multihop() -> None:
    """T2: iter_cleanup_chain emits UserWarning when beta >= n_dim/2 on K>=2 chain.

    Builds a minimal KGStore (small n_dim) and asserts the warning fires when
    a multi-hop call is made with the saturating-beta default. Single-hop call
    must NOT warn (saturated cleanup is the legitimate use case).
    """
    n_dim = 64
    n_ent = 32
    n_rel = 4
    g = torch.Generator()
    g.manual_seed(0)
    kg = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=n_dim, generator=g)
    # Ingest a tiny chain so traversal has something to bind on
    triples = torch.tensor([[0, 0, 1], [1, 1, 2], [2, 2, 3]], dtype=torch.long)
    kg.ingest_triples(triples)

    # k_set must be <= n_ent
    k_set_test = min(20, n_ent)

    # Multi-hop with beta = n_dim must warn
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _ = iter_cleanup_chain(
            kg, start=0, relations=[0, 1], k_set=k_set_test, beta=float(n_dim)
        )
        msgs = [str(x.message) for x in w if issubclass(x.category, UserWarning)]
    assert any("beta=" in m and "n_dim/2" in m for m in msgs), (
        f"expected beta-regime UserWarning on K=2 beta=n_dim call; got: {msgs}"
    )

    # Multi-hop with safe beta (beta=10) must NOT warn
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _ = iter_cleanup_chain(
            kg, start=0, relations=[0, 1], k_set=k_set_test, beta=10.0
        )
        msgs = [str(x.message) for x in w if issubclass(x.category, UserWarning)]
    assert not any("beta=" in m and "n_dim/2" in m for m in msgs), (
        f"unexpected beta-regime warning at beta=10 K=2: {msgs}"
    )

    # Single-hop with beta = n_dim must NOT warn (saturated single-hop is legit)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _ = iter_cleanup_chain(
            kg, start=0, relations=[0], k_set=k_set_test, beta=float(n_dim)
        )
        msgs = [str(x.message) for x in w if issubclass(x.category, UserWarning)]
    assert not any("beta=" in m and "n_dim/2" in m for m in msgs), (
        f"unexpected beta-regime warning on single-hop call: {msgs}"
    )


if __name__ == "__main__":
    test_beta_10_soft_posterior_has_information()
    test_beta_n_dim_collapses_to_dirac()
    test_iter_cleanup_chain_warns_on_high_beta_multihop()
    print("[verification/test_softmax_beta_regime] PASS: T1 entropy + T2 warn-on-high-beta-multihop")
