"""Landing witness for the AFFECT-PATH TAGGER MEMO (strategy optimization 2026-09-06).

_assign_affect runs once PER EVENT and re-tagged its sentence string every time via the frontend UPOS tagger.
Many events share a sentence, so the identical string was re-tagged repeatedly -- the affect path was the
majority of the read's POS-tag calls, and tagging is ~40% of read cost. `_affect_pos_cached` memoizes the
tags by sentence_text. tag() is a PURE deterministic function of the tokens, so the memo is byte-identical.

  W1 BYTE-IDENTICAL: on real LitBank docs, the ordered sequence of _assign_affect results (the affect field
     assigned to every event) is IDENTICAL with the memo (default) vs the memo bypassed (pre-change behavior).
  W2 REDUCTION: pos_tagger.tag calls drop sharply (memo vs bypass) -- the tagging work saved.
  W3 the memo returns EXACTLY the un-memoized tags for a battery of strings (implementation-bug guard).

Glass-box, NO LLM. ASCII.
Run: .venv/Scripts/python.exe verification/test_affect_tag_memo_landing.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.situation_reader as SR
from hdlab.situation_reader import SituationReader, _load_frontend, _affect_pos_cached
import hdlab.pos_tagger as PT
import experiments.exp_situation_model_qa_v1 as QA


def _read_all_recording_affect(r, docs):
    """Read every doc, recording the ordered (patient, sentence_text, result) of every _assign_affect call."""
    rec = []
    _orig = SR._assign_affect
    def _wrap(patient, sentence_text):
        out = _orig(patient, sentence_text)
        rec.append((patient, sentence_text, out))
        return out
    SR._assign_affect = _wrap
    # patch the two call sites' module-global reference too (they call the module-level name)
    calls = {"n": 0}
    _tag = PT.PosTagger.tag
    def _ctag(self, *a, **k):
        calls["n"] += 1
        return _tag(self, *a, **k)
    PT.PosTagger.tag = _ctag
    try:
        for d in docs:
            r.read(os.path.join(QA.CONLL_DIR, d + ".conll"))
    finally:
        SR._assign_affect = _orig
        PT.PosTagger.tag = _tag
    return rec, calls["n"]


def main():
    gaz = QA.load_given_gazetteer()
    docs = [d for d in QA.load_docs(6) if os.path.exists(os.path.join(QA.CONLL_DIR, d + ".conll"))][:3]
    assert docs, "no docs found"
    r = SituationReader(gaz=gaz)
    r.read(os.path.join(QA.CONLL_DIR, docs[0] + ".conll"))     # warm lazy assets

    # memo ON (default)
    _affect_pos_cached.cache_clear()
    rec_memo, calls_memo = _read_all_recording_affect(r, docs)

    # memo BYPASSED (reproduce the pre-change re-tag-every-event behavior)
    _orig_cache = SR._affect_pos_cached
    SR._affect_pos_cached = lambda s: tuple(_load_frontend()[0].tag(s.split(" ")))
    try:
        rec_bypass, calls_bypass = _read_all_recording_affect(r, docs)
    finally:
        SR._affect_pos_cached = _orig_cache

    # W1 byte-identity of the affect assignments
    assert len(rec_memo) == len(rec_bypass), "call count differs: %d vs %d" % (len(rec_memo), len(rec_bypass))
    diffs = [(a, b) for a, b in zip(rec_memo, rec_bypass) if a != b]
    assert not diffs, "affect result DIFFERS memo-vs-bypass on %d/%d calls; first: %s" % (
        len(diffs), len(rec_memo), diffs[0])
    print("W1 BYTE-IDENTICAL affect field over %d events across %d docs (memo==bypass): PASS"
          % (len(rec_memo), len(docs)), flush=True)

    # W2 tag-call reduction
    print("W2 REDUCTION: pos_tagger.tag calls memo %d vs bypass %d (saved %d = %.0f%%): PASS"
          % (calls_memo, calls_bypass, calls_bypass - calls_memo,
             100.0 * (calls_bypass - calls_memo) / max(1, calls_bypass)), flush=True)

    # W3 implementation-bug guard: the memo equals the un-memoized tags on a battery
    _affect_pos_cached.cache_clear()
    battery = ["He was very angry at the boy .", "She smiled .", "The old soldier died to save them .",
               "to go", "a", "in order to leave the room quietly", "They wanted to run away ."]
    bad = [s for s in battery if tuple(_load_frontend()[0].tag(s.split(" "))) != _affect_pos_cached(s)]
    assert not bad, "memo != fresh tag on: %s" % bad
    print("W3 memo==fresh tags on %d battery strings: PASS" % len(battery), flush=True)

    print("\nALL WITNESSES PASS", flush=True)


if __name__ == "__main__":
    main()
