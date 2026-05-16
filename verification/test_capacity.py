"""Empirical bundle capacity matches Plate's theoretical prediction."""

import pytest


@pytest.mark.skip(reason="Week 1: atom statistics not yet implemented")
def test_atom_similarity_std_matches_theory() -> None:
    """Off-diagonal pairwise similarity std ~= 1/sqrt(N)."""
    pass


@pytest.mark.skip(reason="Week 3: capacity sweeps not yet implemented")
def test_capacity_curve_matches_theory() -> None:
    """Recovery accuracy vs k follows the predicted shape within tolerance."""
    pass
