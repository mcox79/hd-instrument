"""A parameter that does nothing must say so, not accept a path and ignore it.

Measured 2026-08-22 with a descriptor recording every READ of the attribute: across construction plus
a 120-sentence read, `Substrate.foundation_dir` is read ZERO times, and repo-wide no caller passes it.
So a caller supplying a foundation path got a substrate that silently re-entered its ~107-seed cold
start -- which is why the plan's "the degeneracy should fall as the vocabulary grows" prediction is
unreachable by construction.
"""

import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.substrate import Substrate  # noqa: E402


def test_passing_a_foundation_dir_refuses_loudly():
    """The whole point: silence here reads as a successfully loaded foundation."""
    with pytest.raises(NotImplementedError) as e:
        Substrate(n_dim=64, foundation_dir="data/foundation/reading_grounding_v2_qualityfix")
    msg = str(e.value)
    assert "never" in msg and "read" in msg, "the refusal must say WHY, not just refuse: %r" % msg


def test_the_default_still_constructs():
    """NEGATIVE CONTROL. A guard that breaks ordinary construction would be worse than the defect."""
    s = Substrate(n_dim=64)
    assert s.foundation_dir is None


def test_the_attribute_is_still_read_zero_times():
    """Pins the measurement itself, so a future author who wires loading sees this test fail.

    Carries its own POSITIVE CONTROL: a deliberate read must be observed, otherwise "zero reads"
    would be indistinguishable from a broken spy -- the absence-check failure this repo keeps paying
    for.
    """
    reads = []

    class Spy:
        priv = "_spy_foundation_dir"

        def __get__(self, obj, objtype=None):
            if obj is None:
                return self
            reads.append(1)
            return getattr(obj, self.priv, None)

        def __set__(self, obj, v):
            setattr(obj, self.priv, v)

    original = Substrate.__dict__.get("foundation_dir", None)
    Substrate.foundation_dir = Spy()
    try:
        s = Substrate(n_dim=64)
        assert len(reads) == 0, "construction read foundation_dir %d times" % len(reads)
        _ = s.foundation_dir                      # POSITIVE CONTROL
        assert len(reads) == 1, "the spy cannot see reads -- zero would prove nothing"
    finally:
        if original is None:
            del Substrate.foundation_dir
        else:                                     # pragma: no cover
            Substrate.foundation_dir = original
