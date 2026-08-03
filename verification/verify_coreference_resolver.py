"""Scaffold-free witness: hdlab.coreference_resolver reproduces the banked earn-coref gains.

Proves the promoted module (atoms 29613/29614/29616/29618/29621, plus the 2026-08-02 speaker/
addressee deixis promotion) matches the VET-confirmed behavior of the source experiment cells on
small constructed fixtures (the same fixture shapes the source cells' own self-tests used, replayed
here against the hdlab port):
  (1) match-or-allocate chains name+pronoun mentions of one entity, keeps a second entity disjoint,
      and beats the recency-floor / random fair-test discriminators (atom 29613).
  (2) strict-Cb corrects an agent-vs-agent turn-taking mispick the salience pick makes (atom 29614).
  (3) Binding Principle B excludes a same-clause co-argument antecedent ("John saw him" -> him!=John)
      and abstains on the participial / multi-agent guard cases (atom 29618).
  (4) the confidence/flag signal (margin, n_compatible) is computed, is 0.0 on a genuine criterion
      tie, and >0 on an unambiguous pick (atom 29616); mention_link_wrong labels correctly.
  (5) NEW RECOMMENDED CANONICAL run_principle_b_deixis: an in-quote 3rd-person pronoun excludes the
      current speaker + addressee, forcing the absent third party that run_principle_b mispicks; and
      ABSTAINS (byte-identical decisions to run_principle_b) on an out-of-quote narration pronoun
      (source: experiments/exp_coref_loop_cross_clause_discourse_v1.py, commit 0c4285f52).

No corpus, no network, no torch, no tracing (module emits none).
Run: python verification/verify_coreference_resolver.py (exit 0 = PASS)
"""

import os
import random
import sys

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.coreference_resolver import (  # noqa: E402
    NO_COMPETITION_MARGIN,
    bcubed,
    build_mention_stream,
    enrich_dialogue,
    mention_link_wrong,
    run_match_or_allocate,
    run_principle_b,
    run_principle_b_deixis,
    run_random,
    run_recency_floor,
    run_strict_cb,
    run_strict_cb_instrumented,
)


def _stream_ids(stream, gold_entity):
    return [i for i, r in enumerate(stream) if r["gold_entity"] == gold_entity]


def test_match_or_allocate_chains_and_beats_floors():
    """Match-or-allocate must chain Alice/She/her into one entity, keep Bob disjoint, and clear
    the recency-floor + random fair-test discriminators on a tiny multi-passage eval."""
    passage = {
        "passage_id": "t1",
        "clauses": ["Alice went to the store.", "She bought bread.", "Bob saw her there."],
        "entities": {
            "Alice": [
                {"clause": 0, "mention": "Alice", "role": "agent"},
                {"clause": 1, "mention": "She", "role": "agent"},
                {"clause": 2, "mention": "her", "role": "patient"},
            ],
            "Bob": [{"clause": 2, "mention": "Bob", "role": "agent"}],
        },
    }
    stream = build_mention_stream(passage)
    assert len(stream) == 4, f"expected 4 surface mentions, got {len(stream)}"
    assert stream[0]["mention_text"] == "Alice" and not stream[0]["is_pronoun"]
    assert stream[1]["mention_text"] == "She" and stream[1]["is_pronoun"] and stream[1]["gender"] == "fem"

    pred = run_match_or_allocate(stream)
    alice_ids = {pred[i] for i in _stream_ids(stream, "Alice")}
    bob_ids = {pred[i] for i in _stream_ids(stream, "Bob")}
    assert len(alice_ids) == 1, f"failed to chain Alice/She/her: {alice_ids}"
    assert alice_ids.isdisjoint(bob_ids), "incorrectly merged Alice and Bob"

    b_learn = bcubed([(stream, pred)])
    assert b_learn["f1"] == 1.0, f"must score perfect B3 on this clean fixture: {b_learn}"

    rec_pred = run_recency_floor(stream)
    assert rec_pred == [0, 0, 0, 0]
    b_rec = bcubed([(stream, rec_pred)])
    assert b_rec["f1"] < b_learn["f1"], "recency-floor must not beat match-or-allocate"

    rng = random.Random(1234)
    rand_pred = run_random(stream, rng)
    assert len(rand_pred) == 4
    b_rand = bcubed([(stream, rand_pred)])
    assert b_rand["f1"] <= b_learn["f1"], "random must not beat match-or-allocate"
    return "match-or-allocate: perfect B3 on clean fixture, clears recency-floor + random"


def test_strict_cb_corrects_turn_taking_mispick():
    """Agent-vs-agent turn-taking: Robert mentioned twice (higher raw frequency) but Willie is the
    immediate-preceding-clause agent for 'He' -> the salience pick mispicks Robert, strict-Cb must
    correct it to Willie (the documented fix, atom 29614)."""
    fixture = {
        "passage_id": "flip_cb1",
        "clauses": ["Robert ran.", "Robert jumped again.", "Willie appeared.", "He laughed."],
        "entities": {
            "Robert": [
                {"clause": 0, "mention": "Robert", "role": "agent"},
                {"clause": 1, "mention": "Robert", "role": "agent"},
            ],
            "Willie": [
                {"clause": 2, "mention": "Willie", "role": "agent"},
                {"clause": 3, "mention": "He", "role": "agent"},
            ],
        },
    }
    stream = build_mention_stream(fixture)
    he_idx = [i for i, r in enumerate(stream) if r["mention_text"] == "He"][0]
    robert_idxs = _stream_ids(stream, "Robert")
    willie_idxs = _stream_ids(stream, "Willie")

    base_pred = run_match_or_allocate(stream)
    cb_pred = run_strict_cb(stream)

    assert base_pred[he_idx] in {base_pred[i] for i in robert_idxs}, (
        f"precondition: salience pick must mispick Robert here; base_pred={base_pred}")
    assert cb_pred[he_idx] in {cb_pred[i] for i in willie_idxs}, (
        f"strict-Cb must pick Willie (immediate-clause agent): cb_pred={cb_pred}")
    assert cb_pred[he_idx] not in {cb_pred[i] for i in robert_idxs}
    assert base_pred != cb_pred, "arms must differ on the flip fixture"

    b_base = bcubed([(stream, base_pred)])
    b_cb = bcubed([(stream, cb_pred)])
    assert b_cb["f1"] > b_base["f1"], f"strict-Cb must score strictly higher B3: base={b_base} cb={b_cb}"
    return f"strict_cb: corrects agent-vs-agent turn-taking mispick (B3 {b_base['f1']:.3f} -> {b_cb['f1']:.3f})"


def test_principle_b_excludes_same_clause_agent():
    """Binding Principle B: 'John saw him' -> him != John (same-clause co-argument exclusion);
    abstains on the participial guard (continued subject tagged at a prior clause) and the
    multi-agent guard (>=2 same-clause agents), never overriding the gold in those cases."""
    pos_fixture = {
        "passage_id": "pb_pos",
        "clauses": ["Bob spoke first.", "John ran outside.", "John saw him."],
        "entities": {
            "Bob": [{"clause": 0, "mention": "Bob", "role": "agent"},
                    {"clause": 2, "mention": "him", "role": "patient"}],
            "John": [{"clause": 1, "mention": "John", "role": "agent"},
                     {"clause": 2, "mention": "John", "role": "agent"}],
        },
    }
    s = build_mention_stream(pos_fixture)
    him_idx = [i for i, r in enumerate(s) if r["mention_text"] == "him"][0]
    bob_idxs = _stream_ids(s, "Bob")
    john_idxs = _stream_ids(s, "John")

    cb = run_strict_cb(s)
    pb, acts = run_principle_b(s)
    assert cb[him_idx] in {cb[i] for i in john_idxs}, (
        f"precondition: strict_cb must mispick John (same-clause agent): cb={cb}")
    assert pb[him_idx] in {pb[i] for i in bob_idxs} and pb[him_idx] not in {pb[i] for i in john_idxs}, (
        f"Principle B must exclude John and force Bob: pb={pb}")
    assert acts.get("fired", 0) >= 1, f"filter must fire on the positive case: {acts}"
    assert cb != pb, "arms must differ on the positive fixture"

    part_fixture = {
        "passage_id": "pb_participial",
        "clauses": ["A lad caught the pony.", "Catching Dick, jerked him forward."],
        "entities": {
            "lad": [{"clause": 0, "mention": "A lad", "role": "agent"}],
            "Dick": [{"clause": 1, "mention": "Dick", "role": "patient"},
                     {"clause": 1, "mention": "him", "role": "patient"}],
        },
    }
    sp = build_mention_stream(part_fixture)
    cbp = run_strict_cb(sp)
    pbp, actsp = run_principle_b(sp)
    assert pbp == cbp, f"participial guard must not change the pick: cb={cbp} pb={pbp}"
    assert actsp.get("fired", 0) == 0
    assert actsp.get("abstain_no_same_clause_agent", 0) >= 1, actsp

    multi_fixture = {
        "passage_id": "pb_multi",
        "clauses": ["Joab met Amasa.", "Joab asked Amasa who told him."],
        "entities": {
            "Joab": [{"clause": 0, "mention": "Joab", "role": "agent"},
                     {"clause": 1, "mention": "Joab", "role": "agent"},
                     {"clause": 1, "mention": "him", "role": "recipient"}],
            "Amasa": [{"clause": 0, "mention": "Amasa", "role": "patient"},
                      {"clause": 1, "mention": "Amasa", "role": "agent"}],
        },
    }
    sm = build_mention_stream(multi_fixture)
    _pbm, actsm = run_principle_b(sm)
    assert actsm.get("abstain_multi_same_clause_agent", 0) >= 1, actsm
    assert actsm.get("fired", 0) == 0
    return "principle_b: fires on positive case, abstains on participial + multi-agent guards"


def test_confidence_signal_and_link_label():
    """Confidence/flag margin: NO_COMPETITION_MARGIN on an unambiguous pick, 0.0 on a genuine
    criterion tie between two compatible candidates; mention_link_wrong labels a wrong link."""
    unambig = {
        "passage_id": "cb_margin_clear",
        "clauses": ["Robert ran.", "Willie appeared.", "He laughed."],
        "entities": {
            "Robert": [{"clause": 0, "mention": "Robert", "role": "agent"}],
            "Willie": [{"clause": 1, "mention": "Willie", "role": "agent"},
                       {"clause": 2, "mention": "He", "role": "agent"}],
        },
    }
    stream = build_mention_stream(unambig)
    inst, dec = run_strict_cb_instrumented(stream)
    assert inst == run_strict_cb(stream), "instrumented copy must reproduce the mechanism exactly"
    he_idx = [i for i, r in enumerate(stream) if r["mention_text"] == "He"][0]
    assert dec[he_idx]["is_pronoun"] and dec[he_idx]["margin"] == 1.0, dec[he_idx]
    assert not mention_link_wrong(he_idx, stream, inst), "He should correctly link to Willie"

    wrong_fixture = {
        "passage_id": "cb_margin_wrong",
        "clauses": ["Robert ran.", "Willie appeared.", "He laughed."],
        "entities": {
            "Robert": [{"clause": 0, "mention": "Robert", "role": "agent"}],
            "Willie": [{"clause": 1, "mention": "Willie", "role": "agent"}],
            "SomeoneElse": [{"clause": 2, "mention": "He", "role": "agent"}],
        },
    }
    s2 = build_mention_stream(wrong_fixture)
    inst2, _ = run_strict_cb_instrumented(s2)
    assert inst2 == run_strict_cb(s2)
    he2 = [i for i, r in enumerate(s2) if r["mention_text"] == "He"][0]
    assert mention_link_wrong(he2, s2, inst2), "He->present-candidate should be a wrong link"

    single_cand = {
        "passage_id": "cb_single_cand",
        "clauses": ["Robert ran.", "He laughed."],
        "entities": {"Robert": [{"clause": 0, "mention": "Robert", "role": "agent"},
                                {"clause": 1, "mention": "He", "role": "agent"}]},
    }
    s3 = build_mention_stream(single_cand)
    _inst3, dec3 = run_strict_cb_instrumented(s3)
    he3 = [i for i, r in enumerate(s3) if r["mention_text"] == "He"][0]
    assert dec3[he3]["margin"] == NO_COMPETITION_MARGIN, dec3[he3]
    return "confidence signal: margin=1.0 clear pick, NO_COMPETITION_MARGIN single-candidate, wrong-link label correct"


def test_speaker_deixis_excludes_speaker_and_addressee():
    """Scaffold-free witness for the 2026-08-02 speaker/addressee deixis promotion (source:
    experiments/exp_coref_loop_cross_clause_discourse_v1.py commit 0c4285f52, self_test() fixture
    (A)). Dialogue-turn: Stephen asks, Philip replies "He broke my cane" -- the in-quote 'He' must
    exclude the current speaker (Philip) and addressee (Stephen), forcing the absent third party
    (Robertson). run_principle_b's own Principle-B filter abstains here (the pronoun's own role is
    agent, the own-clause-agent guard), so run_principle_b alone still mispicks the addressee same as
    run_strict_cb -- deixis is the mechanism that fixes it. A second fixture proves the filter
    ABSTAINS on an out-of-quote narration pronoun (byte-identical decisions to run_principle_b)."""
    dlg = {
        "passage_id": "dlg1",
        "clauses": [
            "Farmer Robertson broke the cane.",
            '"Who did it," asked Stephen.',
            '"He broke my cane," replied Philip.',
        ],
        "entities": {
            "Robertson": [{"clause": 0, "mention": "Farmer Robertson", "role": "agent"},
                          {"clause": 2, "mention": "He", "role": "agent"}],
            "Stephen": [{"clause": 1, "mention": "Stephen", "role": "agent"}],
            "Philip": [{"clause": 2, "mention": "Philip", "role": "agent"}],
        },
    }
    s = enrich_dialogue(dlg, build_mention_stream(dlg))
    he_idx = [i for i, r in enumerate(s) if r["mention_text"] == "He"][0]
    assert s[he_idx]["in_quote"], f"'He' must be detected inside a quote: {s[he_idx]}"
    assert s[he_idx]["clause_speaker"] == "Philip", s[he_idx]
    assert s[he_idx]["clause_addressee"] == "Stephen", s[he_idx]  # alternating: prev diff speaker
    robertson_idxs = _stream_ids(s, "Robertson")
    stephen_idxs = _stream_ids(s, "Stephen")

    pb, _ = run_principle_b(s)
    pbd, acts = run_principle_b_deixis(s)
    assert pb[he_idx] in {pb[i] for i in stephen_idxs}, (
        f"precondition: run_principle_b must still mispick the addressee Stephen for in-quote 'He' "
        f"(its own-clause-agent guard abstains here): pb={pb}")
    assert pbd[he_idx] in {pbd[i] for i in robertson_idxs}, (
        f"speaker-deixis must exclude speaker+addressee and force Robertson: pbd={pbd}")
    assert acts.get("deixis_fired", 0) >= 1, f"deixis must have fired: {acts}"
    assert pb != pbd, "run_principle_b_deixis must differ from run_principle_b on the dialogue fixture"

    # deixis must NOT fire on an OUT-OF-QUOTE pronoun (narration frame): "said Joab, and he took the
    # darts" -- 'he' outside the quote refers to the speaker; excluding the speaker would break it.
    narr = {
        "passage_id": "narr1",
        "clauses": ["Amasa stood there.", "Then said Joab, and he took the darts."],
        "entities": {
            "Amasa": [{"clause": 0, "mention": "Amasa", "role": "agent"}],
            "Joab": [{"clause": 1, "mention": "Joab", "role": "agent"},
                     {"clause": 1, "mention": "he", "role": "agent"}],
        },
    }
    sn = enrich_dialogue(narr, build_mention_stream(narr))
    he2 = [i for i, r in enumerate(sn) if r["mention_text"] == "he"][0]
    assert not sn[he2]["in_quote"], "narration 'he' must NOT be flagged in-quote"
    pbn, _ = run_principle_b(sn)
    pbdn, actsn = run_principle_b_deixis(sn)
    assert pbdn == pbn, f"deixis must not change out-of-quote decisions: pb={pbn} pbd={pbdn}"
    assert actsn.get("deixis_fired", 0) == 0, actsn

    # un-enriched stream (no in_quote/clause_speaker fields) must degrade to abstain -> identical to
    # run_principle_b, proving the graceful-degradation contract documented on the function.
    s_raw = build_mention_stream(dlg)
    pbd_raw, acts_raw = run_principle_b_deixis(s_raw)
    assert pbd_raw == pb, "un-enriched stream must reduce exactly to run_principle_b"
    assert acts_raw.get("deixis_fired", 0) == 0, acts_raw
    return ("speaker_deixis: excludes speaker+addressee for in-quote 'He' (Philip/Stephen->Robertson), "
            "abstains on out-of-quote narration and on an un-enriched stream")


def main():
    tests = [
        test_match_or_allocate_chains_and_beats_floors,
        test_strict_cb_corrects_turn_taking_mispick,
        test_principle_b_excludes_same_clause_agent,
        test_confidence_signal_and_link_label,
        test_speaker_deixis_excludes_speaker_and_addressee,
    ]
    for t in tests:
        line = t()
        print("PASS %-42s %s" % (t.__name__, line))
    print("\nALL PASS: hdlab.coreference_resolver reproduces the banked earn-coref gains "
          "(atoms 29613/29614/29616/29618, plus the 2026-08-02 speaker/addressee deixis promotion, "
          "commit 0c4285f52) -- promoted module matches source-cell behavior.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
