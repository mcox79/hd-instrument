"""Witness for hdlab.scalar_adjective_operation (landed 2026-08-28, landing-step 2 of the p1 magnitude channel).

Self-contained construction proof of the OPERATION on synthetic assets (no data files -- the human-gold performance is
the solver's `verify_composed_magnitude_channel.py`, re-verified at integration):
  [1] GROUNDED ORIENTED AXIS carries polarity: the SemAxis recovers the valence direction from its antonym seed pairs;
      a positive word projects positive (pole +1), a negative word negative (pole -1) -- one oriented projection = both.
  [2] MARKEDNESS DEGREE = log-distance: a RARER word has a larger degree (-log freq) than a common one.
  [3] STORED CODE + NATIVE COMPARATOR: code(w) = bind(DIM, POLE, FPE_log(degree)); for a SAME-POLE pair, compare()
      decodes the log-RATIO of their degrees (one substrate unbind == FPE_log(deg1/deg2), cos ~ 1.0).
  [4] INFO-FREE + glass-box: a scrambled (random) axis does NOT systematically order the valence words; no gold in the API.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.scalar_adjective_operation import ScalarMagnitudeChannel, dim_axis, DIM_SEEDS  # noqa: E402
from hdlab.fractional_power_encoding import log_encode  # noqa: E402
from hdlab.lexical_similarity import _cos_complex  # noqa: E402

DIMV = 16
POS = ["good", "pleasant", "happy", "positive", "nice", "wonderful", "excellent", "great"]
NEG = ["bad", "unpleasant", "sad", "negative", "nasty", "awful", "terrible", "poor"]


def _build_gv():
    """Synthetic GloVe: e_0 is the valence direction; positive words +e_0, negative -e_0 (+ tiny per-word offset)."""
    rng = np.random.default_rng(7)
    gv = {}
    for i, w in enumerate(POS):
        v = np.zeros(DIMV); v[0] = 1.0; v[1:] = rng.normal(0, 0.05, DIMV - 1); gv[w] = v
    for i, w in enumerate(NEG):
        v = np.zeros(DIMV); v[0] = -1.0; v[1:] = rng.normal(0, 0.05, DIMV - 1); gv[w] = v
    return gv


def main() -> int:
    gv = _build_gv()
    # freq: rarer words have LOWER frequency (-> higher markedness degree)
    freq = {"good": 5e-3, "nice": 3e-3, "wonderful": 2e-4, "excellent": 8e-5, "great": 4e-3,
            "pleasant": 6e-4, "happy": 2e-3, "positive": 1e-3,
            "bad": 4e-3, "awful": 3e-4, "terrible": 9e-5, "poor": 2e-3, "sad": 2e-3,
            "unpleasant": 5e-4, "negative": 1e-3, "nasty": 3e-4}
    lanc = {}  # perceptual axis unused (we test the evaluative valence dim)
    chan = ScalarMagnitudeChannel(gv, freq, lanc, d_sub=2048, seed=20260827)

    # [1] oriented axis carries polarity
    ax = dim_axis("valence", gv)
    assert ax is not None and abs(ax[0]) > 0.9, "SemAxis must recover the valence direction (e_0)"
    pos_ok = sum(int(chan.pole(w, "valence") == 1) for w in POS)
    neg_ok = sum(int(chan.pole(w, "valence") == -1) for w in NEG)
    print(f"[1] oriented axis: positive words pole+1 {pos_ok}/{len(POS)}; negative pole-1 {neg_ok}/{len(NEG)}")
    assert pos_ok == len(POS) and neg_ok == len(NEG), "the oriented projection must carry polarity for both poles"

    # [2] markedness: rarer word -> larger degree
    d_rare, d_common = chan.degree("excellent"), chan.degree("good")
    print(f"[2] markedness degree: rare 'excellent' {d_rare:.3f} > common 'good' {d_common:.3f}")
    assert d_rare > d_common, "a rarer word must have a larger markedness degree (-log freq)"

    # [3] stored code + native ratio comparator on a SAME-POLE pair
    w1, w2 = "excellent", "good"                     # both positive pole
    assert chan.pole(w1, "valence") == chan.pole(w2, "valence") == 1
    dec = chan.compare(w1, w2, "valence")
    target = log_encode(chan._rates, chan.degree(w1) / chan.degree(w2))   # FPE_log(deg1/deg2)
    sim = float(_cos_complex(dec, target))
    print(f"[3] comparator: unbind(code(excellent), code(good)) ~= FPE_log(deg ratio) cos={sim:.3f}")
    assert sim > 0.99, f"the compare() unbind must decode the degree log-ratio ({sim:.3f})"

    # [4] info-free scrambled axis loses; glass-box
    rng = np.random.default_rng(1)
    scrambled = {w: rng.normal(0, 1, DIMV) for w in gv}    # random vectors -> no valence structure
    sc = ScalarMagnitudeChannel(scrambled, freq, lanc, d_sub=2048, seed=20260827)
    sc_pos = sum(int(sc.pole(w, "valence") == 1) for w in POS)
    print(f"[4] info-free scrambled axis: positive-word pole+1 only {sc_pos}/{len(POS)} (~chance, << {len(POS)})")
    assert sc_pos < len(POS), "a scrambled axis must NOT perfectly order the valence words"
    import inspect
    for m in (ScalarMagnitudeChannel.oriented_position, ScalarMagnitudeChannel.code):
        assert "gold" not in inspect.signature(m).parameters, m
    print("     glass-box PASS (no gold in the operation signatures)")

    print("\nALL WITNESS ASSERTIONS PASSED -- the scalar-magnitude channel's oriented axis carries polarity, markedness")
    print("gives log-degree, the stored code binds DIM x POLE x FPE_log(degree), and its comparator is a native unbind")
    print("that decodes the Weber degree-ratio; a scrambled axis loses.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
