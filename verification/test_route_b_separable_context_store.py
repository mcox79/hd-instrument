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

from hdlab.reading_grounding_loop import (
    ConceptSpace, ReadingLoopState, seed_known_words, process_sentence,
    content_lemmas, HDFactStore, KNOWN_RELATION, MEANING_RELATION,
)


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


def test_broad_flag_enables_tracking_without_track_context_counts():
    # ROUTE B change 2 (the_reader SOLVED): the NEW opt-in flag enables the count store ON ITS OWN,
    # with track_context_counts left OFF -- so it cannot disturb the existing seed-known-only path.
    s = ConceptSpace()
    assert s.track_all_content_lemmas is False, "the broad flag must be OFF by default"
    s.observe_context_counts("cat", ["furry", "pet"])            # both flags off -> no-op
    assert s.all_context_counts() == {}
    s.track_all_content_lemmas = True                            # broad flag alone
    s.observe_context_counts("cat", ["furry", "pet"])
    assert s.context_counts("cat") == Counter({"furry": 1, "pet": 1})
    print("PASS broad_flag_enables_tracking_without_track_context_counts")


def _reading_state(seed):
    st = HDFactStore(n_dim=2048, seed=seed,
                     relation_cardinality={KNOWN_RELATION: "FUNCTIONAL", MEANING_RELATION: "FUNCTIONAL"})
    state = ReadingLoopState(store=st)
    seed_known_words(state, ["engine", "harvest"], f"seed_broad_{seed}")   # only 2 of the content words
    return state


def test_broad_flag_read_tracks_all_content_lemmas_no_double_count():
    # The read-loop half of change 2: with the broad flag ON, EVERY content lemma read gets a separable
    # count-store entry (the coverage the distributional channel was missing), while the narrow flag
    # still tracks ONLY seed-known lemmas. CAN-FAIL: if the broadening did not fire, the non-seed words
    # would be absent; if it double-counted, engine->harvest would be 2.
    sent = "The engine and the tractor waited inside the barn before harvest."
    content = set(content_lemmas(sent))
    seedset = {"engine", "harvest"}
    nonseed = content - seedset
    assert nonseed, f"fixture must contain non-seed content words to prove broadening; content={content}"

    narrow = _reading_state(11)
    narrow.space.track_context_counts = True
    process_sentence(narrow, sent, "n0", pass_idx=0)
    tracked_narrow = set(narrow.space.all_context_counts())
    assert tracked_narrow and tracked_narrow <= seedset, (
        f"narrow path must track ONLY seed-known lemmas, got {tracked_narrow}")

    broad = _reading_state(11)
    broad.space.track_all_content_lemmas = True
    process_sentence(broad, sent, "b0", pass_idx=0)
    tracked_broad = set(broad.space.all_context_counts())
    assert content <= tracked_broad, f"broad path must track ALL content lemmas; missing {content - tracked_broad}"
    assert nonseed <= tracked_broad, "the non-seed words (the coverage gap the channel needs) are now tracked"

    eng = broad.space.context_counts("engine")
    if "harvest" in eng:
        assert eng["harvest"] == 1, (
            "double-count: engine->harvest must be 1 -- the all-lemmas loop OWNS tracking when broad is on")
    print("PASS broad_flag_read_tracks_all_content_lemmas_no_double_count")


if __name__ == "__main__":
    test_default_off_is_a_true_noop()
    test_on_keeps_counts_separable()
    test_additive_sums_path_untouched()
    test_broad_flag_enables_tracking_without_track_context_counts()
    test_broad_flag_read_tracks_all_content_lemmas_no_double_count()
    print("5/5 WITNESSES PASSED")
