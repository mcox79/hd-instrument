"""Witness: the INTRINSIC saturating gain-ratio replaces the fitted DEFAULT_W in convergent_cue_reader
(pri-2 meaning-representation, piece 3).

Proves (a) BYTE-IDENTICAL default -- with no gains supplied, convergent_pick is exactly the fitted-w behaviour
(all current callers unaffected); (b) the intrinsic weight is the SATURATING gain-ratio log1p(gain_sem)/
log1p(gain_epi): equal gains -> w=1 (equal-reliability), more semantic gain -> w>1, and it SATURATES (log1p, not
the raw count); (c) an empty earned episodic channel falls back gracefully (until reading exposure fills it);
(d) supplying gains actually re-weights the pick (the mechanism is live when opted in).
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.convergent_cue_reader import convergent_pick, intrinsic_gain_w, DEFAULT_W

_EPI = [2.0, 0.0, -1.0]      # episodic cue favours candidate 0
_SEM = [0.0, 2.0, 0.0]       # semantic cue favours candidate 1


def test_default_is_byte_identical():
    base = convergent_pick(_EPI, _SEM)                          # fitted DEFAULT_W path
    assert convergent_pick(_EPI, _SEM, gain_epi=None, gain_sem=None) == base
    assert convergent_pick(_EPI, _SEM, gain_sem=5.0) == base    # only one gain -> not opted in -> fitted
    assert convergent_pick(_EPI, _SEM, gain_epi=5.0) == base
    # the lesion / no-evidence paths are untouched
    assert convergent_pick(None, None) is None
    assert convergent_pick(_EPI, None) == 0                     # semantic lesion -> entity-solo (argmax epi)
    print("PASS default_is_byte_identical")


def test_intrinsic_gain_ratio_shape():
    # equal earned gains -> equal reliability -> w = 1 (no fitted 12x tilt)
    assert abs(intrinsic_gain_w(4.0, 4.0) - 1.0) < 1e-9
    # more semantic evidence -> w > 1; more episodic -> w < 1
    assert intrinsic_gain_w(1.0, 9.0) > 1.0 and intrinsic_gain_w(9.0, 1.0) < 1.0
    # SATURATING: log1p(3)/log1p(1) = 2.0, strictly BELOW the raw count-ratio 3.0 (Weber-Fechner)
    w = intrinsic_gain_w(1.0, 3.0)
    assert abs(w - 2.0) < 1e-6 and w < 3.0, w
    # empty earned episodic channel -> fitted fallback (until exposure); both empty -> equal
    assert intrinsic_gain_w(0.0, 5.0) == DEFAULT_W
    assert intrinsic_gain_w(0.0, 0.0) == 1.0
    print("PASS intrinsic_gain_ratio_shape")


def test_intrinsic_gain_reweights_the_pick():
    # with the fitted DEFAULT_W (=12) the semantic cue dominates -> candidate 1
    assert convergent_pick(_EPI, _SEM) == 1
    # opting in with EQUAL earned gains (w=1) removes the 12x semantic tilt -> the episodic cue can win
    equal = convergent_pick(_EPI, _SEM, gain_epi=4.0, gain_sem=4.0)
    assert equal == 0, ("equal-gain intrinsic weight should let the stronger episodic cue win", equal)
    # restoring a large semantic gain reproduces the semantic-dominant pick intrinsically (no fitting)
    assert convergent_pick(_EPI, _SEM, gain_epi=1.0, gain_sem=1e6) == 1
    print("PASS intrinsic_gain_reweights_the_pick")


if __name__ == "__main__":
    test_default_is_byte_identical()
    test_intrinsic_gain_ratio_shape()
    test_intrinsic_gain_reweights_the_pick()
    print("3/3 WITNESSES PASSED")
