"""Empirical pairwise-similarity distribution matches the closed-form prediction for each substrate."""

from __future__ import annotations

import pytest
import torch

from hdlab import atoms
from verification import theory


def _pairwise_std(vecs: torch.Tensor, complex_: bool) -> float:
    k, n = vecs.shape
    if complex_:
        sims = (vecs @ vecs.conj().T).real / n
    else:
        norms = vecs.norm(dim=-1, keepdim=True)
        normed = vecs / torch.where(norms > 0, norms, torch.ones_like(norms))
        sims = normed @ normed.T
    mask = ~torch.eye(k, dtype=torch.bool)
    return float(sims[mask].std())


def test_fhrr_atom_similarity_std_matches_theory() -> None:
    """FHRR off-diagonal pairwise similarity std == 1/sqrt(2N) within 10%."""
    k = 300
    for n in [256, 1024, 4096]:
        gen = torch.Generator().manual_seed(0)
        vecs = atoms.make_atoms(k, n, torch.complex64, gen)
        empirical = _pairwise_std(vecs, complex_=True)
        predicted = theory.atom_similarity_std(n, dtype="complex64")
        ratio = empirical / predicted
        assert 0.9 < ratio < 1.1, (
            f"FHRR N={n}: empirical={empirical:.5f}, predicted={predicted:.5f}, ratio={ratio:.3f}"
        )


def test_hrr_atom_similarity_std_matches_theory() -> None:
    """HRR off-diagonal pairwise cosine-similarity std == 1/sqrt(N) within 10%."""
    k = 300
    for n in [256, 1024, 4096]:
        gen = torch.Generator().manual_seed(0)
        vecs = atoms.make_atoms(k, n, torch.float32, gen)
        empirical = _pairwise_std(vecs, complex_=False)
        predicted = theory.atom_similarity_std(n, dtype="float32")
        ratio = empirical / predicted
        assert 0.9 < ratio < 1.1, (
            f"HRR N={n}: empirical={empirical:.5f}, predicted={predicted:.5f}, ratio={ratio:.3f}"
        )


@pytest.mark.skip(reason="Week 7: capacity sweeps not yet implemented")
def test_capacity_curve_matches_theory() -> None:
    """Recovery accuracy vs k follows the predicted shape within tolerance."""
    pass
