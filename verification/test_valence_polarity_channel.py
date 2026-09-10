"""Witness: the VALENCE-POLARITY meaning channel (pri-2 meaning-representation, piece 2).

Proves (a) the organ mechanism -- antonyms are OPPOSITE poles on the signed evaluative axis, synonyms share the
pole, an OOV word abstains; and (b) the MEASURED basis re-derives first-hand: fusing the signed valence polarity
with the relation-blind distributional channel un-blinds meaning to ANTONYMY, CI-separated over the distributional
floor, WITHOUT WordNet, with a low complementarity correlation and an info-free (shuffled-valence) twin that loses.

HONEST NOTE: valence-ALONE beats the floor strongly (AUC ~0.84) but at the tiny SimVerb affective-pair n (~43) its
CI vs the floor is seed-sensitive; the robust, landable claim is the FUSED channel (distributional + valence
polarity), which IS CI-separated. That is exactly how it lands -- as a COMPLEMENTARY polarity axis fused alongside
the relatedness channels, not a standalone ranker.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401

from hdlab.valence_polarity_channel import valence_polarity, va_polarity, same_pole


def test_mechanism_antonyms_are_opposite_poles():
    lp = valence_polarity("love", "hate")
    ln = valence_polarity("love", "adore")
    assert lp is not None and ln is not None
    assert lp < ln, ("antonym must be MORE negative than the synonym", lp, ln)
    assert same_pole("love", "adore") is True and same_pole("love", "hate") is False
    # va_polarity (adds arousal) still orders the antonym below the synonym
    assert va_polarity("love", "hate") < va_polarity("love", "adore")
    # honest OOV: abstain rather than fabricate
    assert valence_polarity("love", "zzzznotaword") is None and same_pole("x", "zzzznotaword") is None
    print("PASS mechanism_antonyms_are_opposite_poles")


def test_measured_fused_beats_floor_ci_sep_without_wordnet():
    import experiments.exp_valence_polarity_meaning_channel_v1 as E
    r = E.run("seq", seed=13, n_boot=1500)
    auc = r["syn_vs_antonym_AUC"]
    fused_ci = r["FUSED_vs_DISTRIBUTIONAL_AUC_diff"]["ci"]
    v = r["verdict"]
    # FUSED beats the relation-blind distributional floor, CI-separated (lower CI bound > 0)
    assert v["fused_beats_distributional_floor_ci_sep"] and fused_ci[0] > 0.0, (fused_ci, auc)
    # it does so WITHOUT WordNet in the channel
    assert v["beats_floor_WITHOUT_wordnet"]
    # the valence axis is COMPLEMENTARY to the distributional channel (low correlation)
    assert v["valence_is_complementary_low_corr"] and r["complementarity_corr_valence_vs_distributional"] < 0.3
    # info-free twin (shuffled valence) LOSES to the real valence signal (does not hold up as a ranker)
    assert r["info_free_twin_AUC"] < auc["VALENCE"], (r["info_free_twin_AUC"], auc["VALENCE"])
    # most antonyms are affectively opposed (the honest coverage of this axis)
    assert r["frac_antonyms_affectively_opposed"] > 0.6
    print("PASS measured_fused_beats_floor_ci_sep_without_wordnet "
          "(FUSED %.3f vs DIST %.3f, ci %s; twin %.3f)"
          % (auc["FUSED_dist_plus_valence"], auc["DISTRIBUTIONAL"], fused_ci, r["info_free_twin_AUC"]))


if __name__ == "__main__":
    test_mechanism_antonyms_are_opposite_poles()
    test_measured_fused_beats_floor_ci_sep_without_wordnet()
    print("2/2 WITNESSES PASSED")
