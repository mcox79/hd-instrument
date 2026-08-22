"""A replayed checkpoint must never be readable as a reproduction.

Scaffold-free witness for `tools/reproduction_check.py`. The incident it pins
(`notes/RESUMABILITY_DEFEATS_REPRODUCTION_CHECKING_2026-08-22.md`): re-running a landed cell finished
in `elapsed 0.0s`, skipped every unit, and returned the verdict line and every number unchanged.
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.reproduction_check import (  # noqa: E402
    PARTIAL, RECOMPUTED, REPLAYED, census, classify_run, would_replay)


def test_the_real_incident_is_classified_as_a_replay():
    """5 units in, 5 out, zero seconds -- the shape that was nearly reported as verified."""
    assert classify_run(units_before=5, units_after=5, elapsed_s=0.0).status == REPLAYED


def test_a_genuine_recompute_is_not_flagged():
    """NEGATIVE CONTROL. A guard that flags everything gets ignored."""
    assert classify_run(0, 5, 61.0).status == RECOMPUTED
    assert classify_run(2, 5, 30.0).status == PARTIAL


def test_the_verdict_cannot_collapse_to_a_boolean():
    """The collapse IS the incident: one glance at a pass-shaped line and the check is defeated."""
    v = classify_run(5, 5, 0.0)
    try:
        bool(v)
    except TypeError:
        pass
    else:                                    # pragma: no cover
        raise AssertionError("bool(ReproductionVerdict) must raise, not return a value")
    assert v.is_evidence_of_reproduction() is False
    assert classify_run(0, 3, 12.0).is_evidence_of_reproduction() is True


def test_census_reads_the_real_archive_and_finds_the_exposure():
    """POSITIVE CONTROL against real data -- a census that CANNOT return non-zero proves nothing."""
    landed, replay_landed, _orphan, rows = census()
    assert landed > 1000, "census did not see the archive (%d landed)" % landed
    assert replay_landed > 0, "no landed cell would replay -- verify the detector, not the archive"
    name, n = rows[0]
    ok, k = would_replay(os.path.join(REPO_ROOT, "data", name))
    assert ok and k == n


def test_an_empty_dir_is_not_a_replay(tmp_path):
    """NEGATIVE CONTROL on the filesystem side."""
    ok, n = would_replay(str(tmp_path))
    assert (not ok) and n == 0
