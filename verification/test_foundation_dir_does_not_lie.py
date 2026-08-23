"""`Substrate(foundation_dir=...)` must LOAD -- and must not be sold as a grounding fix.

HISTORY, because the name of this file only makes sense with it. This witness has asserted three
different contracts, in order:

1. The parameter was accepted and **silently ignored** -- a caller passing a path believed a
   foundation was loaded while the substrate re-entered its 92-fact cold start every run.
2. 2026-08-22: measured (descriptor spy, positive-controlled) that the attribute was read ZERO
   times, so the constructor was changed to **raise** rather than pretend. This file pinned the
   raise, and its own docstring said a future author who wired loading would see it fail.
3. 2026-08-23: loading is **wired**. That author was the `substrate_never_resumes` solver session,
   and this file failed on purpose exactly as designed. It now pins the loading.

🚨 **THE PART THAT MATTERS MORE THAN THE WIRING.** The measurement that arrived with this wiring
REFUTED the premise that motivated it. Resuming does not reduce the generic-attractor degeneracy
and does not improve grounding correctness:

  * COLD grounds **168** new meanings on a 4,000-sentence read; RESUMED grounds **9** -- resuming
    makes a matched re-read ~18x LESS productive, because the recurring vocabulary is already known
    and genuinely novel words do not clear the 0.45 similarity gate against the loaded anchors.
  * Grounding precision sits at its RANDOM_ANCHOR floor in EVERY arm (COLD 0.0199 = 3/151,
    RESUMED 0/9). Not CI-separated. No arm buys correctness.
  * A permuted-label **DECOY** arm matches RESUMED *exactly* (0/164 both), so what changes across
    the boundary is the anchor geometry, not the meaning.

The cause is that grounding here is **same-batch co-occurrence**, which by construction cannot
transfer across runs. Persistence is NECESSARY for a consolidated cortical store -- a system that
discards its store every run has no slow system at all -- and is NOT SUFFICIENT to make the reading
mean anything.

So the last test below pins the REFUTATION, not just the wiring. A future author who finds this
loading path and reaches for "resuming should improve grounding" is reaching for a retired
prediction, and this file should be what tells them.

Reproduce the measurement itself with:
    .venv/Scripts/python.exe verification/test_substrate_resume_measurement.py
"""
import io
import json
import os

import pytest

from hdlab.substrate import Substrate

SNAPSHOT = "data/exp_substrate_resume_solver/clean_snapshot_full"


def _n_live(s):
    """live_facts is a METHOD ON THE STORE, not an attribute on the state.

    Spelled out because guessing this name cost a debugging round on the day this was written --
    the repo's standing rule is to enumerate the fields that exist before asserting about one.
    """
    return len(s.state.store.live_facts())


def test_the_default_still_constructs_cold():
    """NEGATIVE CONTROL, and the additive claim: `None` must be exactly the old behaviour.

    If this drifts, the wiring regressed every existing caller -- and every caller in the repo
    passes `None` today, so this is the arm that protects all of them.
    """
    s = Substrate(n_dim=64)
    assert s.foundation_dir is None
    assert s._pass_idx == 0, "a cold start must not inherit a pass index"
    assert _n_live(s) == 92, "cold start is the 92-fact seed store; got %d" % _n_live(s)


def test_two_cold_builds_agree():
    """A determinism control, so the comparison below cannot be noise."""
    assert _n_live(Substrate(n_dim=64, seed=11)) == _n_live(Substrate(n_dim=64, seed=11))


@pytest.mark.skipif(not os.path.isdir(SNAPSHOT), reason="snapshot artifact absent")
def test_passing_a_foundation_dir_actually_loads():
    """The contract this file now exists for: passing a path LOADS, and is visibly different.

    Compared against the cold arm rather than against a hardcoded number, so the assertion stays
    true if the seed vocabulary changes.
    """
    cold = Substrate(n_dim=64, seed=11)
    warm = Substrate(n_dim=64, seed=11, foundation_dir=SNAPSHOT)
    assert warm.foundation_dir == SNAPSHOT
    assert _n_live(warm) > _n_live(cold), (
        "resumed store (%d) must carry more than cold (%d) -- otherwise loading is a no-op again, "
        "which is the exact defect this file was created for" % (_n_live(warm), _n_live(cold)))


@pytest.mark.skipif(not os.path.isdir(SNAPSHOT), reason="snapshot artifact absent")
def test_the_pass_index_survives_the_run_boundary():
    """Restarting `_pass_idx` at 0 would silently re-arm consolidation.

    The Dumay-Gaskell intervening-pass rule counts passes since exposure; a resumed run that
    forgets its count is not resumed for the purpose that matters.
    """
    warm = Substrate(n_dim=64, seed=11, foundation_dir=SNAPSHOT)
    manifest = json.load(io.open(os.path.join(SNAPSHOT, "manifest.json"), encoding="utf-8"))
    assert warm._pass_idx == int(manifest["next_pass_idx"])
    assert warm._pass_idx > 0, "the fixture must have a non-zero index or this proves nothing"


def test_the_refutation_is_recorded_where_the_wiring_is():
    """PINS THE FINDING, NOT THE CODE -- the one test here that is about a claim.

    A caution written as prose gets violated; this repo's standing escalation is to move it into
    the path. The risk after wiring is not that loading breaks -- it is that someone reads
    "foundation loading works now" and re-bills it as the fix for grounding degeneracy. That
    prediction is RETIRED, by measurement, and the constructor comment is where a reader will be
    standing when the thought occurs.
    """
    src = io.open("hdlab/substrate.py", encoding="utf-8").read()
    i = src.find("self.foundation_dir = foundation_dir")
    assert i > 0, "constructor assignment not found -- this test is anchored to it"
    window = src[max(0, i - 1600):i]
    for token in ("168", "9", "RANDOM_ANCHOR", "DECOY", "SAME-BATCH CO-OCCURRENCE"):
        assert token in window, (
            "the constructor no longer carries the refutation (%r missing). Persistence must not "
            "be presented as a grounding fix; see notes/problems/substrate_never_resumes/." % token)
    # NEGATIVE CONTROL: the window must be a real slice, or the loop above passes vacuously.
    assert "zzq_never_appears" not in window
    assert len(window) > 400
