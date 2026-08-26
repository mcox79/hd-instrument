"""Witness: signed lexical-relation valence propagation LANDED in
hdlab/wordnet_polarity_propagation.py -- a DEFAULT-OFF replacement for the taxonomic Stage B.

Problem: propagate_along_the_relation_that_carries_valence (SOLVED + integrated EXCELLENT 2026-08-26).
Asserts:
  1. DEFAULT is BYTE-IDENTICAL -- signed_propagation defaults to False, so no live behaviour changes.
  2. The relation SIGN is load-bearing -- preserve keeps the pole, antonym flips it, sign-ambiguous
     does not vote, a nearer anchor outweighs a farther opposite one (short-range signed spread).
  3. The signed path REACHES MORE lemmas than the taxonomic Stage A+B (the coverage gain, 326->485
     at scale) -- because taxonomy carries no valence and selects a different, smaller neighbour set.
  4. It exposes a GRADED valence (vote_margin / confidence in [0,1]).
Scaffold-free; reads no artifact. The full-scale accuracy result (0.726 over floor, sign-scramble
twin at chance) is witnessed by verification/test_signed_lexical_valence_propagation.py.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.wordnet_polarity_propagation as W


def test_default_is_byte_identical():
    for lm in ("ruin", "heal", "worsen", "improve", "zzznotarealverb", "destroy"):
        assert W.dictionary_lookup(lm) == W.dictionary_lookup(lm, signed_propagation=False), lm
    print("PASS default_byte_identical")


def test_sign_is_load_bearing():
    poles = {"good": +1, "bad": -1}
    assert W._signed_predict({"good": (1, +1)}, poles)[0] == "POS"      # synonym of POS -> POS
    assert W._signed_predict({"good": (1, -1)}, poles)[0] == "NEG"      # antonym of POS -> NEG (FLIP)
    assert W._signed_predict({"bad": (1, -1)}, poles)[0] == "POS"       # antonym of NEG -> POS (FLIP)
    assert W._signed_predict({"good": (1, 0)}, poles)[0] is None        # sign-ambiguous: no vote
    assert W._signed_predict({}, poles)[0] is None                      # nothing reached
    # short-range: a nearer anchor outweighs a farther opposite one (gamma decay)
    p2 = {"a": +1, "b": +1}
    assert W._signed_predict({"a": (1, +1), "b": (2, -1)}, p2)[0] == "POS"
    print("PASS sign_load_bearing")


def test_signed_reaches_more_than_stage_ab():
    probes = ["worsen", "destroy", "heal", "improve", "ruin", "harm", "repair", "break", "fix",
              "build", "waste", "save", "help", "hurt", "kill", "grow", "shrink", "strengthen",
              "weaken", "melt"]
    sig = sum(1 for p in probes if W.dictionary_lookup(p, signed_propagation=True).stage == "signed")
    old = sum(1 for p in probes if W.dictionary_lookup(p).stage in ("antonym", "neighbor"))
    assert sig > old, "signed must reach more than taxonomic Stage A+B: %d vs %d" % (sig, old)
    print("PASS coverage_gain: signed %d > Stage A+B %d (of %d)" % (sig, old, len(probes)))


def test_exposes_graded_valence():
    lu = W.dictionary_lookup("ruin", signed_propagation=True)
    assert lu.polarity in ("POS", "NEG")
    assert 0.0 <= lu.vote_margin <= 1.0 and 0.0 <= lu.confidence <= 1.0
    print("PASS graded_valence: ruin -> %s margin=%.3f conf=%.2f" % (lu.polarity, lu.vote_margin, lu.confidence))


if __name__ == "__main__":
    test_default_is_byte_identical()
    test_sign_is_load_bearing()
    test_signed_reaches_more_than_stage_ab()
    test_exposes_graded_valence()
    print("WITNESS PASS")
