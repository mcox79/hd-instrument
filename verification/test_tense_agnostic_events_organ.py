"""Witness for the TENSE-AGNOSTIC event-detection flag landed in hdlab/situation_reader.py (2026-08-31).

Integrated from `the_extraction_front_end_recovers_only_a_third_of_events_and_roles` (owner-DONE, EXCELLENT;
reverified 11/11 first-hand via verification/test_extraction_frontend_recall.py). The stock event detector
(experiments._temporal_ordering.extract_events) is TENSE-GATED and misses present-tense finite verbs (VBZ/VBP)
100%, capping event-detection recall at ~0.33. The fix -- detect at every UPOS==VERB via the in-substrate
UD-trained tagger (glass-box, no spaCy/LLM) -- is landed behind a DEFAULT-OFF `tense_agnostic_events` flag.

This witness proves the LANDING (the flag wiring), not the recall headline (that is the p1 witness, reverified):
  (1) DEFAULT-OFF is byte-identical: a reader built with the default == a reader built with
      tense_agnostic_events=False -> identical event set on a real LitBank doc (the landing invariant).
  (2) THE FLAG WIRES: tense_agnostic_events=True runs the UPOS==VERB detector through the canonical
      SituationReader.read() without error and LIFTS the detected event count (the recall direction of the
      end-to-end p1 result 0.381->0.966; here on a real doc the tense-gated detector's present-tense misses
      are recovered, so the flag-on event set is a strict superset-in-count).
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

from hdlab.situation_reader import SituationReader

DOC = os.path.join(_REPO, "data", "litbank", "coref_conll", "1023_bleak_house_brat.conll")


def _events(reader):
    sm = reader.read(DOC)
    return [(e.sent_idx, e.predicate) for e in sm.events]


def test_tense_agnostic_events_flag():
    assert os.path.exists(DOC), "missing witness doc %s" % DOC

    # (1) DEFAULT-OFF byte-identical: default reader == explicit tense_agnostic_events=False.
    ev_default = _events(SituationReader())
    ev_off = _events(SituationReader(tense_agnostic_events=False))
    assert ev_default == ev_off, "explicit flag=False must be byte-identical to the default reader"
    print("[1] default-off byte-identical: %d events, identical event set" % len(ev_default))

    # (2) THE FLAG WIRES + lifts the detected event count through the canonical read().
    ev_on = _events(SituationReader(tense_agnostic_events=True))
    assert len(ev_on) > len(ev_off), ("tense-agnostic detection must recover present-tense misses -> "
                                      "more events (off=%d on=%d)" % (len(ev_off), len(ev_on)))
    lift = len(ev_on) - len(ev_off)
    print("[2] flag ON wires through canonical read(): events %d -> %d (+%d, %.2fx) -- present-tense "
          "verbs recovered" % (len(ev_off), len(ev_on), lift, len(ev_on) / max(1, len(ev_off))))

    print("ALL WITNESS CHECKS PASSED")


if __name__ == "__main__":
    test_tense_agnostic_events_flag()
