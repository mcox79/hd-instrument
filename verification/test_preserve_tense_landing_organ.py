"""Witness for the TENSE-PRESERVING landing into the canonical SituationReader (2026-08-31).

Wires the validated compositional Reichenbach tense parse (experiments/exp_tense_preserving_event_
detector_v1.assign_sentence, glass-box + in-substrate) into the live reader behind a DEFAULT-OFF
`preserve_tense` flag that REFINES `tense_agnostic_events`: the detector fires on the SAME UPOS==VERB
tokens (recall preserved EXACTLY) but assigns a COMPOSED tense/is_pp instead of the placeholder
TENSE_SIMPLE_PAST. Integrated from problem the_tense_agnostic_detector_drops_tense_needed_by_the_time
_dimension (owner-DONE, STRONG). Same default-off + equivalence-verified pattern as causation/time.

  (1) DEFAULT-OFF byte-identical: with preserve_tense OFF the tense-agnostic detector is unchanged --
      every event carries the PLACEHOLDER tense (constant SIMPLE_PAST), and the tense-preserving
      composition module is NOT imported (no new hard dependency on the default path).
  (2) RECALL PRESERVED EXACTLY: with preserve_tense ON the detected event SET (sent_idx, global_idx,
      predicate) is IDENTICAL to the placeholder path -- tense is a label on already-detected tokens.
  (3) TENSE NOW VARIED: preserve_tense ON yields >1 distinct tense (the placeholder path yields 1).
  (4) FAITHFUL WIRING: the landed preserve_tense=True output EQUALS the validated ref impl
      (exp_tense_preserving_live_reader_and_timeline_v1.tense_preserving_extract) byte-for-byte on
      predicate, tense AND is_pp -- the landing adds no new logic, it wires the validated composition.
ASCII-only, deterministic, CPU-only, small synthetic doc (fast).
"""
import os
import sys
import types

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader, _write_temp_conll

# A tense-varied passage so the composition produces multiple labels.
_SENTS = [
    "Mary opened the box .".split(),                       # simple past
    "She had hidden the letter there .".split(),           # past perfect (is_pp)
    "He walks to the market every day .".split(),          # simple present
    "The window was broken by the storm .".split(),        # passive
    "They have finished the work .".split(),               # present perfect
]


def _doc_path():
    rows = []
    for si, toks in enumerate(_SENTS):
        for wi, tok in enumerate(toks):
            rows.append((si, wi, tok, "-"))
    return _write_temp_conll(rows)


def _ev_tuples(sm):
    # EventRecord carries .tense (is_pp lives on the detector's T.Event -- checked at the detector level in [5]).
    return [(e.sent_idx, e.global_idx, str(e.predicate).lower(), str(e.tense)) for e in sm.events]


def test_preserve_tense_landing():
    doc = _doc_path()

    # (1) DEFAULT-OFF byte-identical: placeholder path unchanged, composition module not imported.
    assert "experiments.exp_tense_preserving_event_detector_v1" not in sys.modules, \
        "composition module must not be imported before any preserve_tense reader is built/run"
    sm_off = SituationReader(tense_agnostic_events=True, preserve_tense=False).read(doc)   # explicit-OFF (default-ON since 2026-09-03)
    sm_off2 = SituationReader(tense_agnostic_events=True, preserve_tense=False).read(doc)
    off_tuples = _ev_tuples(sm_off)
    assert off_tuples == _ev_tuples(sm_off2), "preserve_tense=False must be byte-identical to the default"
    off_tenses = sorted({t[3] for t in off_tuples})
    assert off_tenses == ["SIMPLE_PAST"], "placeholder path must carry the constant SIMPLE_PAST, got %r" % off_tenses
    assert "experiments.exp_tense_preserving_event_detector_v1" not in sys.modules, \
        "the tense-preserving composition must NOT be imported on the preserve_tense=OFF path"
    print("[1] DEFAULT-OFF byte-identical: %d events, all placeholder SIMPLE_PAST; composition not imported"
          % len(off_tuples))

    # (2)+(3) FLAG ON: recall preserved exactly + tense now varied.
    sm_on = SituationReader(tense_agnostic_events=True, preserve_tense=True).read(doc)
    on_tuples = _ev_tuples(sm_on)
    off_set = [(t[0], t[1], t[2]) for t in off_tuples]
    on_set = [(t[0], t[1], t[2]) for t in on_tuples]
    assert on_set == off_set, ("recall must be preserved EXACTLY (identical event set).\n  off: %r\n  on:  %r"
                               % (off_set, on_set))
    on_tenses = sorted({t[3] for t in on_tuples})
    assert len(on_tenses) > 1, "preserve_tense ON must yield varied tense, got %r" % on_tenses
    print("[2] RECALL PRESERVED EXACTLY: %d events, identical (sent,idx,pred) set" % len(on_tuples))
    print("[3] TENSE VARIED: %d distinct tenses %r (vs the placeholder's single SIMPLE_PAST)"
          % (len(on_tenses), on_tenses))

    # (4) FAITHFUL WIRING: landed output == the validated ref impl byte-for-byte.
    from experiments import exp_tense_preserving_live_reader_and_timeline_v1 as LT
    r_ref = SituationReader(tense_agnostic_events=True)
    r_ref._tense_agnostic_extract = types.MethodType(LT.tense_preserving_extract, r_ref)
    ref_tuples = _ev_tuples(r_ref.read(doc))
    assert on_tuples == ref_tuples, ("landed preserve_tense output must EQUAL the validated ref impl.\n"
                                     "  landed: %r\n  ref:    %r" % (on_tuples, ref_tuples))
    print("[4] FAITHFUL WIRING: landed preserve_tense=True == ref impl tense_preserving_extract (byte-for-byte)")

    # (5) DETECTOR-LEVEL is_pp faithfulness (the flashback signal the TIME dimension consumes lives on
    # T.Event.is_pp, not on EventRecord). Compare the raw _extract_events output including is_pp.
    r_land = SituationReader(tense_agnostic_events=True, preserve_tense=True)
    r_ref2 = SituationReader(tense_agnostic_events=True)
    r_ref2._tense_agnostic_extract = types.MethodType(LT.tense_preserving_extract, r_ref2)
    any_pp = False
    for toks in _SENTS:
        text = " ".join(toks)
        land_evs, _ = r_land._extract_events(text)
        ref_evs, _ = r_ref2._extract_events(text)
        land_raw = [(e.lemma, e.idx, str(e.tense), bool(e.is_pp)) for e in land_evs]
        ref_raw = [(e.lemma, e.idx, str(e.tense), bool(e.is_pp)) for e in ref_evs]
        assert land_raw == ref_raw, ("detector-level (incl is_pp) must match the ref impl on %r.\n"
                                     "  landed: %r\n  ref:    %r" % (text, land_raw, ref_raw))
        any_pp = any_pp or any(e.is_pp for e in land_evs)
    assert any_pp, "expected at least one is_pp (past-perfect) event on the flashback sentence"
    print("[5] DETECTOR-LEVEL is_pp faithful: raw T.Event (lemma,idx,tense,is_pp) == ref impl; is_pp fires on the flashback")

    print("ALL WITNESS CHECKS PASSED")


if __name__ == "__main__":
    test_preserve_tense_landing()
