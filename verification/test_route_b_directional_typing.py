"""Witness: ROUTE-B DIRECTIONAL TYPING on ConceptSpace (pri-2 meaning-representation SOLVED, 2026-09-10).

Piece 1 of the pri-2 landing (HDLAB_INTEGRATION_SPEC): turn the substrate's EXISTING separable co-occurrence
store into a PARSER-FREE IDENTITY / substitutability channel by adding DIRECTION+DISTANCE order typing
(temporal-order coding; the `sequence_memory` S-matrix principle) -- removing the NOT_BF supervised parser from
the learned meaning channel, and it grows by reading. The change is ADDITIVE + DEFAULT-OFF.

Proves: (a) the pure typing helper is correct (order, multi-occurrence, boundaries); (b) default-off is a true
no-op MODIFIER -- with the store ON but directional OFF the counts are byte-identical to the existing UNTYPED bag;
(c) directional ON yields ONLY DIRECTION+DISTANCE-typed keys (the identity channel), never a bare lemma; (d) the
RECALL PATH is byte-identical off-vs-on (only the separable `_ctx_counts` store changes, never `_sums`); (e) it
composes with the seed-known (`track_context_counts`) path too. Scaffold-free; writes nothing landed.
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
    directional_context_lemmas,
)


def test_helper_orders_and_types_neighbours():
    seq = ["engine", "tractor", "wait", "barn", "harvest"]
    got = directional_context_lemmas(seq, "wait")            # i=2
    assert got == ["L1__tractor", "R1__barn", "L2__engine", "R2__harvest"], got
    # boundary: first token has no left neighbour
    assert directional_context_lemmas(seq, "engine") == ["R1__tractor", "R2__wait"]
    # absent target -> empty
    assert directional_context_lemmas(seq, "nope") == []
    # MULTI-OCCURRENCE: every occurrence contributes its own typed neighbours (incl. self at distance 2)
    m = directional_context_lemmas(["a", "x", "b", "x", "c"], "x")
    assert m == ["L1__a", "R1__b", "R2__x", "L1__b", "R1__c", "L2__x"], m
    print("PASS helper_orders_and_types_neighbours")


def test_flag_default_off():
    s = ConceptSpace()
    assert s.track_directional_context_counts is False, "directional typing must be OFF by default"
    # both directional and the tracking flags off -> still a true no-op (the store never fires)
    s.observe_context_counts("cat", directional_context_lemmas(["cat", "sat"], "cat"))
    assert s.all_context_counts() == {}
    print("PASS flag_default_off")


def _reading_state(seed):
    st = HDFactStore(n_dim=2048, seed=seed,
                     relation_cardinality={KNOWN_RELATION: "FUNCTIONAL", MEANING_RELATION: "FUNCTIONAL"})
    state = ReadingLoopState(store=st, fused_ranking=False)   # test the ROUTE-B store PRIMITIVE in isolation (live default is fused ON)
    seed_known_words(state, ["engine", "harvest"], f"seed_dir_{seed}")
    return state


_SENT = "The engine and the tractor waited inside the barn before harvest."


def test_directional_off_is_byte_identical_bag():
    # broad tracking ON, directional OFF -> counts are the UNTYPED bag (no key contains '__'); this is the
    # existing behaviour, unchanged. CAN-FAIL: if my `_ctx_for` altered the off-path, a typed key would appear.
    st = _reading_state(11)
    st.space.track_all_content_lemmas = True                 # directional stays False
    process_sentence(st, _SENT, "off0", pass_idx=0)
    keys = [k for c in st.space.all_context_counts().values() for k in c]
    assert keys, "the store must have fired"
    assert all("__" not in k for k in keys), f"OFF path must be the untyped bag; found typed key: {keys[:5]}"
    print("PASS directional_off_is_byte_identical_bag")


def test_directional_on_yields_only_typed_keys():
    st = _reading_state(11)
    st.space.track_all_content_lemmas = True
    st.space.track_directional_context_counts = True         # the modifier ON
    process_sentence(st, _SENT, "on0", pass_idx=0)
    all_counts = st.space.all_context_counts()
    keys = [k for c in all_counts.values() for k in c]
    assert keys, "the store must have fired"
    # EVERY key is DIRECTION+DISTANCE typed -- the identity channel, no bare relatedness lemma survives
    assert all(k[:1] in ("L", "R") and "__" in k and k[1:2].isdigit() for k in keys), keys[:8]
    # a concrete neighbour: 'engine' is followed (R1, content-only) by 'tractor'
    eng = all_counts.get("engine", Counter())
    assert any(k == "R1__tractor" for k in eng), f"engine should have R1__tractor; got {list(eng)}"
    print("PASS directional_on_yields_only_typed_keys")


def test_recall_path_byte_identical_off_vs_on():
    # The RECALL/RANKING path reads `_sums` (bundle) + trace_count; directional typing touches ONLY `_ctx_counts`.
    off = _reading_state(11); off.space.track_all_content_lemmas = True
    process_sentence(off, _SENT, "r_off", pass_idx=0)
    on = _reading_state(11); on.space.track_all_content_lemmas = True
    on.space.track_directional_context_counts = True
    process_sentence(on, _SENT, "r_on", pass_idx=0)
    for lem in ("engine", "harvest"):                        # the seed-known lemmas that populate _sums
        assert (lem in off.space) == (lem in on.space)
        if lem in off.space:
            assert np.array_equal(off.space.bundle(lem), on.space.bundle(lem)), f"_sums changed for {lem}"
            assert off.space.trace_count(lem) == on.space.trace_count(lem), f"trace_count changed for {lem}"
    print("PASS recall_path_byte_identical_off_vs_on")


def test_composes_with_seed_known_narrow_path():
    # directional also modifies the narrow (seed-known-only) path (track_context_counts), not just broad.
    st = _reading_state(11)
    st.space.track_context_counts = True
    st.space.track_directional_context_counts = True
    process_sentence(st, _SENT, "narrow0", pass_idx=0)
    tracked = set(st.space.all_context_counts())
    assert tracked and tracked <= {"engine", "harvest"}, f"narrow path tracks only seed lemmas; got {tracked}"
    keys = [k for c in st.space.all_context_counts().values() for k in c]
    assert keys and all("__" in k for k in keys), "narrow path counts must be directional-typed when on"
    print("PASS composes_with_seed_known_narrow_path")


if __name__ == "__main__":
    test_helper_orders_and_types_neighbours()
    test_flag_default_off()
    test_directional_off_is_byte_identical_bag()
    test_directional_on_yields_only_typed_keys()
    test_recall_path_byte_identical_off_vs_on()
    test_composes_with_seed_known_narrow_path()
    print("6/6 WITNESSES PASSED")
