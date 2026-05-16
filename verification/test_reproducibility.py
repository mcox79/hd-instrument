"""Same seed produces identical results across runs."""

import pytest


@pytest.mark.skip(reason="Week 5: experiment harness not yet implemented")
def test_deterministic_with_seed() -> None:
    """Two runs with the same seed produce bit-identical traces."""
    pass
