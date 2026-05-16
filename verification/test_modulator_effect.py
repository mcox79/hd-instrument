"""Each modulator moves its target metric monotonically; non-target metrics are isolated."""

import pytest


@pytest.mark.skip(reason="Week 2: modulators not yet implemented")
def test_attention_changes_cleanup_precision() -> None:
    """Raising attention raises cleanup precision and lowers recall."""
    pass


@pytest.mark.skip(reason="Week 2: modulators not yet implemented")
def test_recency_biases_bundling() -> None:
    """Raising recency makes newer bundled items dominate retrieval."""
    pass


@pytest.mark.skip(reason="Week 2: modulators not yet implemented")
def test_modulator_isolation() -> None:
    """Changing one modulator does not move metrics controlled by another."""
    pass
