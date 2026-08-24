"""Witness: ROUTE B separable context-count store on ConceptSpace (2026-08-24).

Increment 1 of wiring the meaning-channel win (notes/problems/
the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by/SOLVED.md): the store is ADDITIVE
and DEFAULT-OFF, and when on it keeps per-lemma context-word counts SEPARABLE -- the thing the d=256
`_sums` bundle blurs. This witness proves (a) default-off is a true no-op, (b) on, counts are kept
separable per lemma, and (c) the existing `_sums`/`observe` path is untouched by it. Scaffold-free;
writes nothing to any landed directory.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from collections import Counter

import numpy as np

from hdlab.reading_grounding_loop import ConceptSpace


def test_default_off_is_a_true_noop():
    s = ConceptSpace()
    assert s.track_context_counts is False, "the separable store must be OFF by default"
    s.observe_context_counts("cat", ["furry", "pet", "furry"])   # off -> must do nothing
    assert s.all_context_counts() == {}
    assert s.context_counts("cat") == Counter()
    print("PASS default_off_is_a_true_noop")


def test_on_keeps_counts_separable():
    s = ConceptSpace()
    s.track_context_counts = True
    s.observe_context_counts("cat", ["furry", "pet", "furry"])
    s.observe_context_counts("cat", ["pet", "sofa"])
    # multiset preserved: two 'furry', two 'pet', one 'sofa' -- NOT deduped, NOT blurred
    assert s.context_counts("cat") == Counter({"furry": 2, "pet": 2, "sofa": 1})
    # a second lemma is stored SEPARATELY (pattern-separated), never superposed onto the first
    s.observe_context_counts("dog", ["furry", "loyal"])
    assert s.context_counts("dog") == Counter({"furry": 1, "loyal": 1})
    assert set(s.all_context_counts()) == {"cat", "dog"}
    print("PASS on_keeps_counts_separable")


def test_additive_sums_path_untouched():
    # observe() (the d=256 sum path) is unchanged and independent of the new count store: calling it
    # populates _sums/_counts but NOT _ctx_counts, and vice versa.
    s = ConceptSpace(d=8)
    s.track_context_counts = True
    v = np.ones(8, dtype=np.float64)
    s.observe("cat", v)
    assert "cat" in s and s.trace_count("cat") == 1
    assert np.array_equal(s.bundle("cat"), np.sign(v)) or np.array_equal(s.bundle("cat"), v)
    assert s.context_counts("cat") == Counter(), "observe() alone must not populate the count store"
    print("PASS additive_sums_path_untouched")


if __name__ == "__main__":
    test_default_off_is_a_true_noop()
    test_on_keeps_counts_separable()
    test_additive_sums_path_untouched()
    print("3/3 WITNESSES PASSED")
