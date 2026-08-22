"""A read that delivers a fraction of what was asked must say so.

Measured 2026-08-22: `Substrate.read(n_sentences=3000)`, `6000` and `10000` all returned 1,060
sentences -- silently, no exception, no warning -- across every seed and n_dim tried. Any number
computed afterwards described ~1,000 sentences while the caller believed it had supplied far more.
`ReadResult.n_sentences` already held the truth; nobody read it.

These tests pin the SHORTFALL as a field, so a caller cannot miss it by not thinking to check.
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.substrate import Substrate  # noqa: E402


def test_a_large_ask_is_flagged_as_a_short_read():
    """POSITIVE CONTROL on the real defect: this is the call shape that was silent."""
    r = Substrate(n_dim=256, seed=20260819).read(n_sentences=8000)
    assert r.n_sentences_requested == 8000
    assert r.n_sentences < 8000, "the read is no longer short -- if genuinely fixed, retire this test"
    assert r.short_read is True, (
        "read delivered %d of 8000 and did NOT flag it" % r.n_sentences)


def test_a_satisfiable_ask_is_not_flagged():
    """NEGATIVE CONTROL. A guard that fires on every read would be ignored within a day."""
    r = Substrate(n_dim=256, seed=20260819).read(n_sentences=300)
    assert r.n_sentences == 300
    assert r.short_read is False


def test_the_requested_count_is_recorded_even_when_satisfied():
    """The field must be usable as evidence, not only as an alarm."""
    r = Substrate(n_dim=256, seed=20260819).read(n_sentences=250)
    assert r.n_sentences_requested == 250
    d = r.to_dict()
    assert "short_read" in d and "n_sentences_requested" in d, (
        "the shortfall must survive to_dict(), which is what gets persisted into metrics.json")
