"""Empirical bundle capacity matches Plate's theoretical prediction."""

from __future__ import annotations

import pytest
import torch

from hdlab import atoms
from verification import theory


def test_atom_similarity_std_matches_theory() -> None:
    """Off-diagonal pairwise similarity std ~= 1/sqrt(N) for random FHRR atoms."""
    for n in [256, 1024, 4096]:
        gen = torch.Generator().manual_seed(0)
        k = 200
        vecs = atoms.make_atoms(k, n, torch.complex64, gen)
        sims = (vecs @ vecs.conj().T).real / n
        mask = ~torch.eye(k, dtype=torch.bool)
        off = sims[mask]
        empirical = float(off.std())
        predicted = theory.atom_similarity_std(n)
        ratio = empirical / predicted
        assert 0.7 < ratio < 1.3, (
            f"N={n}: empirical std={empirical:.4f}, predicted={predicted:.4f}, ratio={ratio:.2f}"
        )


@pytest.mark.skip(reason="Week 3: capacity sweeps not yet implemented")
def test_capacity_curve_matches_theory() -> None:
    """Recovery accuracy vs k follows the predicted shape within tolerance."""
    pass
