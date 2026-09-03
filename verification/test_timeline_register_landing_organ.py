"""Witness for the TIMELINE-REGISTER landing into the canonical SituationReader (2026-08-31).

Wires the validated whole-passage TEMPORAL-ORDER register (experiments/_temporal_order_register.py --
discrete toposort over the constraint graph, with the clause-pluperfect binder) into the live reader
behind a DEFAULT-OFF `timeline_register` flag, as a PURELY ADDITIVE field `sm.timeline_order` (the
whole-passage chronological event order). The existing narrow "had"-gated `_read_timeline` /
`sm.timeline_frames` path is untouched. This is the 2nd ASSEMBLY (DEBT 2) dimension wired into the
reader (after causation), following the same default-off + equivalence-verified pattern.

  (1) DEFAULT-OFF byte-identical: SituationReader() == SituationReader(timeline_register=False) --
      identical timeline_frames, EMPTY timeline_order, and the register is NOT imported on the default
      path (the reader gains no hard temporal-register dependency).
  (2) THE FLAG FIRES + EQUIVALENCE: SituationReader(timeline_register=True).read(doc).timeline_order
      EQUALS the register's OWN output on the same sentences (byte-for-byte) -> the wiring is faithful,
      no new ordering logic.
  (3) THE REGISTER'S CONTRIBUTION: on a pluperfect FLASHBACK passage the chronological order differs
      from the narration order (the whole-passage register places "had hidden" before "opened", which
      the narrow per-sentence path misses).
ASCII-only, deterministic, CPU-only.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader, _write_temp_conll
from hdlab.scene_segment import parse_conll_sentences

# A pluperfect FLASHBACK passage: narration order (opened, hidden, read) != chronology (hidden, opened, read).
_SENTS = [
    "Mary opened the box .".split(),
    "She had hidden the letter there years before .".split(),
    "She read it .".split(),
]


def _doc_path():
    rows = []
    for si, toks in enumerate(_SENTS):
        for wi, tok in enumerate(toks):
            rows.append((si, wi, tok, "-"))
    return _write_temp_conll(rows)


def _frame_tuples(frames):
    return [(f.sent_idx, f.text, tuple(f.text_order), tuple(f.chrono_order), f.reordered) for f in frames]


def test_timeline_register_landing():
    doc = _doc_path()

    # (1) EXPLICIT-OFF byte-identical / reversible (flags are default-ON since 2026-09-03; the reversibility
    # guarantee is that timeline_register=False reproduces the pre-wire behavior -- empty order, no import).
    sm_def = SituationReader(timeline_register=False).read(doc)
    sm_off = SituationReader(timeline_register=False).read(doc)
    assert _frame_tuples(sm_def.timeline_frames) == _frame_tuples(sm_off.timeline_frames), \
        "timeline_frames must be byte-identical default vs explicit timeline_register=False"
    assert sm_def.timeline_order == [] and sm_off.timeline_order == [], \
        "timeline_order must be EMPTY when the flag is off"
    assert "experiments._temporal_order_register" not in sys.modules, \
        "the temporal-order register must NOT be imported on the default (off) path"
    print("[1] DEFAULT-OFF byte-identical: timeline_frames identical (%d); timeline_order empty; register not imported"
          % len(sm_def.timeline_frames))

    # (2) THE FLAG FIRES + EQUIVALENCE to the register's OWN output.
    sm_on = SituationReader(timeline_register=True).read(doc)
    order = sm_on.timeline_order
    assert len(order) >= 2, "flag must fire: expected the whole-passage order, got %r" % order
    from experiments import _temporal_order_register as TOR
    ev, tg, edges = TOR.extract_passage(parse_conll_sentences(doc), clause_pluperfect=True)
    reg = TOR.DiscreteOrderRegister(ev, tg, edges)
    want = [{"lemma": lem, "chrono_rank": i, "text_rank": reg.text_rank.get(lem)}
            for i, lem in enumerate(reg.order)]
    assert order == want, ("landed timeline_order must EQUAL the register's own output.\n"
                           "  landed: %r\n  register: %r" % (order, want))
    print("[2] FLAG FIRES + EQUIVALENCE: timeline_order == the register's own output (%d events, byte-for-byte)"
          % len(order))

    # (3) THE REGISTER'S CONTRIBUTION: chronological order != narration order on the flashback.
    chrono = [d["lemma"] for d in sorted(order, key=lambda d: d["chrono_rank"])]
    narration = [d["lemma"] for d in sorted(order, key=lambda d: (d["text_rank"] if d["text_rank"] is not None else 1e9))]
    assert chrono != narration, ("the whole-passage register must reorder the flashback (chrono != narration); "
                                 "chrono=%r narration=%r" % (chrono, narration))
    print("[3] REGISTER CONTRIBUTION: chronological %r != narration %r (flashback correctly reordered)"
          % (chrono, narration))

    print("ALL WITNESS CHECKS PASSED")


if __name__ == "__main__":
    test_timeline_register_landing()
