"""Production hdlab outputs match the naive reference impl (bit-identical FHRR, tolerance for HRR)."""

import pytest


@pytest.mark.skip(reason="Week 1: substrate not yet implemented")
def test_fhrr_parity_with_reference() -> None:
    """hdlab FHRR ops produce identical outputs to reference.fhrr on shared inputs."""
    pass


@pytest.mark.skip(reason="Week 1: substrate not yet implemented")
def test_hrr_parity_with_reference() -> None:
    """hdlab HRR ops match reference.hrr within numerical tolerance."""
    pass
