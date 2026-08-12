"""Scaffold-free witness for the 2026-08-12 GROUNDING-QUALITY FIX -- tautology refusal, filler
(closed-class) refusal, and per-fact provenance in the reading-grounding loop.

Closes the defect measured in notes/foundation_grounding_sample_2026-08-12.md against the landed
foundation data/foundation/reading_grounding_v1: 2328/3544 (65.7%) of its GROUNDED_MEANING facts
were SELF-GROUNDED tautologies of the form (X, GROUNDED_MEANING, X), which assert nothing, and the
most frequent grounded "meanings" in the whole store were function/discourse words (`also` x31,
`say` x15, `like`/`more`/`most`).

Exercises the REAL objects (no mocks, no fakes, no monkeypatching): hdlab.hd_fact_store.HDFactStore,
hdlab.reading_grounding_loop.{ReadingLoopState, seed_known_words, process_sentence, checkpoint,
canonicalize}, hdlab.closed_class_lexicon, hdlab.foundation_persistence.{save,load}_foundation.
Every assertion below reads the store through its own record/query surface, never a stub.

Pre-reg: preregs/2026-08-12_grounding_quality_fix_v1.md
"""
from __future__ import annotations

import os
import sys
import tempfile

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

from hdlab.closed_class_lexicon import (
    UD_CLOSED_UPOS,
    _spacy_stop_words,
    _ud_majority_closed_forms,
    UD_TRAIN_CONLLU,
    is_closed_class,
    is_eligible_meaning,
)
from hdlab.hd_fact_store import HDFactStore
from hdlab import foundation_persistence
from hdlab.reading_grounding_loop import (
    KNOWN_RELATION,
    MEANING_RELATION,
    REFUSAL_TAUTOLOGY,
    SENSE_MATCH_THRESH,
    ReadingLoopState,
    canonicalize,
    checkpoint,
    is_gap,
    process_sentence,
    seed_known_words,
)

CARD = {KNOWN_RELATION: "FUNCTIONAL", MEANING_RELATION: "FUNCTIONAL"}


def _fresh_state(seed: int, seed_words) -> ReadingLoopState:
    store = HDFactStore(n_dim=2048, seed=seed, relation_cardinality=CARD, use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, seed_words, source=f"verif_seed_{seed}")
    return state


def _meaning_facts(state: ReadingLoopState):
    return [(f.subject, f.obj) for f in state.store.live_facts()
            if f.relation == MEANING_RELATION]


# ---------------------------------------------------------------- (1) TAUTOLOGY REFUSAL
def test_tautology_is_never_recorded_as_a_grounding():
    """A word with coherent, repeated exposure whose concept space holds NO eligible anchor above
    SENSE_MATCH_THRESH must NOT be written as (X, GROUNDED_MEANING, X). canonicalize's self-return
    is its NO-MATCH signal, not a meaning."""
    state = _fresh_state(2101, ["engine", "harvest", "tractor", "barn"])
    for i, s in enumerate(["The engine and the tractor waited inside the barn until harvest.",
                           "A tractor engine ran loudly in the barn before harvest."]):
        process_sentence(state, s, f"anchor{i}", pass_idx=0)
    target_sentences = [
        "The zibbo glimmered softly across the quiet violet meadow.",
        "A quiet zibbo glimmered above the violet meadow again.",
        "Every violet meadow held a softly glimmering zibbo.",
        "The glimmering zibbo drifted over that quiet violet meadow.",
    ]
    for i, s in enumerate(target_sentences):
        process_sentence(state, s, f"z{i}", pass_idx=1)
    for p in range(1, 7):
        checkpoint(state, pass_idx=p, source_tag="verif_taut")

    pairs = _meaning_facts(state)
    assert not any(s == o for s, o in pairs), f"a self-tautology was recorded: {pairs}"
    assert "zibbo" not in [s for s, _ in pairs], (
        f"a word with no eligible anchor must not be counted as grounded: {pairs}")


def test_refused_word_stays_visible_to_the_gap_machinery():
    """Refusal must not silently drop information the gap loop needs: the word stays a GAP (no
    KNOWN_WORD fact is written either) and the refusal is recorded with a reason."""
    state = _fresh_state(2102, ["engine", "harvest", "tractor", "barn"])
    for i, s in enumerate(["The engine and the tractor waited inside the barn until harvest.",
                           "A tractor engine ran loudly in the barn before harvest."]):
        process_sentence(state, s, f"anchor{i}", pass_idx=0)
    for i, s in enumerate([
            "The zibbo glimmered softly across the quiet violet meadow.",
            "A quiet zibbo glimmered above the violet meadow again.",
            "Every violet meadow held a softly glimmering zibbo.",
            "The glimmering zibbo drifted over that quiet violet meadow."]):
        process_sentence(state, s, f"z{i}", pass_idx=1)
    for p in range(1, 7):
        checkpoint(state, pass_idx=p, source_tag="verif_gapvisible")

    assert is_gap(state, "zibbo") is True, "a refused word must remain a gap"
    known = [f.subject for f in state.store.live_facts() if f.relation == KNOWN_RELATION]
    assert "zibbo" not in known, "refusal must withhold the KNOWN_WORD fact too, or the gate closes"
    reasons = [r["reason"] for r in state.refusals if r["lemma"] == "zibbo"]
    assert REFUSAL_TAUTOLOGY in reasons, f"refusal not recorded: {state.refusals}"
    row = [r for r in state.refusals if r["lemma"] == "zibbo"][0]
    for k in ("reason", "pass_idx", "segment", "n_exposures", "best_cos"):
        assert k in row, f"refusal ledger row missing {k}: {row}"


# ------------------------------------------------------------------ (2) FILLER REFUSAL
def test_closed_class_word_is_never_recorded_as_a_meaning():
    """CAN-FAIL BY CONSTRUCTION: the same fixture is first asserted to pick the function word as
    nearest anchor when the eligibility filter is NOT applied, so removing the filter breaks this
    test rather than silently passing it."""
    state = _fresh_state(2103, ["also", "engine", "harvest"])
    for i, s in enumerate([
            "The zibbo also appeared beside the humming engine before harvest.",
            "A zibbo also rested near the humming engine before harvest.",
            "That zibbo also stood beside the humming engine before harvest.",
            "Each zibbo also waited near the humming engine before harvest."]):
        process_sentence(state, s, f"f{i}", pass_idx=1)
    checkpoint(state, pass_idx=1, source_tag="verif_filler")

    item = state.library.items["zibbo"]
    raw_sum = np.sum([t.context_vec for t in item.traces], axis=0)
    unfiltered_obj, unfiltered_cos = canonicalize("zibbo", raw_sum, state.space,
                                                  thresh=SENSE_MATCH_THRESH)
    assert unfiltered_obj == "also" and unfiltered_cos >= SENSE_MATCH_THRESH, (
        f"fixture broken -- without the filter the nearest anchor must be the function word, got "
        f"{unfiltered_obj!r} at {unfiltered_cos:.3f}; the test could not fail otherwise")

    checkpoint(state, pass_idx=2, source_tag="verif_filler")
    pairs = _meaning_facts(state)
    assert "also" not in [o for _, o in pairs], f"function word recorded as a meaning: {pairs}"
    for _, o in pairs:
        assert is_eligible_meaning(o), f"closed-class object {o!r} recorded as a meaning"


def test_closed_class_criterion_is_principled_not_a_blacklist():
    """The exclusion comes from two published sources -- UD's own functional-class inventory
    (computed empirically from the in-repo UD English EWT treebank) and spaCy's English
    function-word list -- and not from the specific words the audit surfaced."""
    ud = _ud_majority_closed_forms(UD_TRAIN_CONLLU)
    spacy_list = _spacy_stop_words()
    assert "like" in ud, "UD majority-UPOS criterion must be what catches 'like' (majority ADP)"
    for w in ("also", "more", "most", "say"):
        assert w in spacy_list, f"the curated function-word list must be what catches {w!r}"
    assert {"ADP", "AUX", "DET", "PRON", "SCONJ", "CCONJ", "PART", "NUM"} <= UD_CLOSED_UPOS
    # content words -- including every MEANINGFUL object the prior audit found -- stay eligible
    for w in ("deductive", "decay", "phylogenetic", "cytoplasm", "polymerase", "haploid",
              "gene", "meaning", "nest", "soot", "alliance"):
        assert is_eligible_meaning(w), f"content word {w!r} must remain eligible as a meaning"
    # DISCLOSED LIMITATION, asserted so it cannot silently become a hand-patch later
    assert is_eligible_meaning("people"), (
        "'people' is open-class under the stated criterion and must stay eligible; excluding it "
        "would mean the lexicon had been tuned to the audit sample")
    assert is_closed_class("says"), "membership is tested on the lemma the loop actually stores"


# --------------------------------------------------------------------- (3) PROVENANCE
def test_every_grounding_carries_its_source_sentences_and_segment():
    sentences = [
        "Owen moored the flimzat boat before the storm reached the harbor.",
        "The crew moored a flimzat boat before every storm hit the harbor.",
        "Sailors always moor the flimzat boat before a storm nears the harbor.",
        "They moored the old flimzat boat before the storm entered the harbor.",
    ]
    state = _fresh_state(2104, ["boat", "storm", "harbor"])
    for i, s in enumerate(sentences):
        process_sentence(state, s, f"p{i}", pass_idx=1)
    checkpoint(state, pass_idx=1, source_tag="verif_segment")
    checkpoint(state, pass_idx=2, source_tag="verif_segment")

    grounded = [f for f in state.store.live_facts() if f.relation == MEANING_RELATION]
    assert grounded, "fixture must produce at least one grounding for provenance to be checked"
    by_fid = {r["fid"]: r for r in state.provenance}
    for f in grounded:
        assert f.fid in by_fid, f"no provenance for stored fact {f.fid} ({f.subject}->{f.obj})"
        row = by_fid[f.fid]
        assert row["segment"] == "verif_segment"
        assert row["evidence"], "provenance row carries no evidence"
        for e in row["evidence"]:
            assert e["sentence"] in sentences, f"unrecoverable source sentence: {e}"


def test_provenance_survives_save_reload_and_v1_stores_still_load():
    """The storage-format change is backward compatible: a snapshot WITHOUT the new sidecars (the
    shape of the landed v1 evidence store) still loads, with empty ledgers rather than an error."""
    state = _fresh_state(2105, ["boat", "storm", "harbor"])
    for i, s in enumerate([
            "Owen moored the flimzat boat before the storm reached the harbor.",
            "The crew moored a flimzat boat before every storm hit the harbor.",
            "Sailors always moor the flimzat boat before a storm nears the harbor.",
            "They moored the old flimzat boat before the storm entered the harbor."]):
        process_sentence(state, s, f"p{i}", pass_idx=1)
    checkpoint(state, pass_idx=1, source_tag="verif_persist")
    checkpoint(state, pass_idx=2, source_tag="verif_persist")

    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "v2")
        foundation_persistence.save_foundation(state, d, source_tag="verif_persist",
                                               next_pass_idx=3)
        back = foundation_persistence.load_foundation(d)
        assert [r["fid"] for r in back.provenance] == [r["fid"] for r in state.provenance]
        assert back.provenance and back.provenance[0]["evidence"][0]["sentence"]

        d1 = os.path.join(tmp, "v1_shape")
        foundation_persistence.save_foundation(state, d1, source_tag="v1_shape", next_pass_idx=3)
        for fn in (foundation_persistence.PROVENANCE_FILE,
                   foundation_persistence.REFUSALS_FILE,
                   foundation_persistence.EVIDENCE_PENDING_FILE):
            os.remove(os.path.join(d1, fn))
        legacy = foundation_persistence.load_foundation(d1)
        assert legacy.provenance == [] and legacy.refusals == []
        assert len(legacy.store._facts) == len(state.store._facts)


def test_landed_v1_evidence_store_still_loads_unchanged():
    """The real landed store is EVIDENCE. It must keep loading under the new code, unmutated."""
    d = os.path.join(_REPO, "data", "foundation", "reading_grounding_v1")
    if not foundation_persistence.foundation_exists(d):
        return  # store not present in this checkout; nothing to assert
    store = foundation_persistence.load_store(os.path.join(d, "store"))
    assert len(store._facts) == 7966, f"v1 evidence store mutated: {len(store._facts)} facts"
    gm = [f for f in store._facts if f.relation == MEANING_RELATION]
    assert len(gm) == 3544
    assert sum(1 for f in gm if f.subject == f.obj) == 2328, (
        "the v1 store's 2328 tautologies are the evidence this fix corrects; they must survive "
        "untouched in the v1 directory")
