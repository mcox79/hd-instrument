"""Trace replay reconstructs system state. The observer must not lie."""

import pytest


@pytest.mark.skip(reason="Week 4: trace bus + replay not yet implemented")
def test_replay_reconstructs_state() -> None:
    """Running from a persisted trace produces identical state to the original run."""
    pass


@pytest.mark.skip(reason="Week 4: trace bus + replay not yet implemented")
def test_every_public_op_emits_event() -> None:
    """Static check: every public op in hdlab has a corresponding trace event in a sample run."""
    pass
