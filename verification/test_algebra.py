"""Algebraic identity tests for FHRR and HRR. Runs with tracing disabled."""

import pytest


@pytest.mark.skip(reason="Week 1: substrate not yet implemented")
def test_fhrr_bind_unbind_inverse() -> None:
    """unbind(bind(a, b), b) == a for FHRR (exact)."""
    pass


@pytest.mark.skip(reason="Week 1: substrate not yet implemented")
def test_hrr_bind_unbind_inverse() -> None:
    """unbind(bind(a, b), b) ~= a for HRR (within tolerance)."""
    pass


@pytest.mark.skip(reason="Week 1: substrate not yet implemented")
def test_bind_commutative_fhrr() -> None:
    """bind(a, b) == bind(b, a) for FHRR."""
    pass


@pytest.mark.skip(reason="Week 1: substrate not yet implemented")
def test_bind_commutative_hrr() -> None:
    """bind(a, b) == bind(b, a) for HRR."""
    pass
