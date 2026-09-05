"""Landing witness for the register-robust event-detection turn-on (owner-DONE
register_robust_event_detection_turn_on_and_expand..., Q111 landing 2026-09-05). The who-did-what arm gains +
the copula readout are reverified by verification/test_event_detection_crossarm_organ.py (7/7); this asserts
the hdlab READER change is faithful: predicate_recall DEFAULT-ON + SCOPED causal. Glass-box, NO LLM. ASCII.

  W1 predicate_recall is DEFAULT-ON on the default reader (register-robust event recovery).
  W2 SCOPED causal: sm.causal_links (default recall-ON reader) is BYTE-IDENTICAL to the recall-OFF reader.
  W3 ADDITIVE detection: every base (recall-OFF) event survives in the recall-ON stream; ON >= OFF count.

Run: .venv/Scripts/python.exe verification/test_event_detection_scoped_recall_landing.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader
import experiments.exp_situation_model_qa_v1 as QA


def _links(sm):
    return {(l.sent_idx, l.cause, l.outcome, l.method) for l in sm.causal_links}


def _events(sm):
    return {(e.sent_idx, e.predicate, e.agent, e.patient, e.tense) for e in sm.events}


def main():
    gaz = QA.load_given_gazetteer()
    docs = [d for d in QA.load_docs(6) if os.path.exists(os.path.join(QA.CONLL_DIR, d + ".conll"))][:4]
    r_on = SituationReader(gaz=gaz)                              # default (predicate_recall ON)
    assert r_on.predicate_recall is True, "predicate_recall is not DEFAULT-ON"
    print("W1 predicate_recall DEFAULT-ON: PASS", flush=True)
    r_off = SituationReader(gaz=gaz, predicate_recall=False)

    total_extra = 0
    for doc in docs:
        path = os.path.join(QA.CONLL_DIR, doc + ".conll")
        sm_on = r_on.read(path)
        sm_off = r_off.read(path)
        lon, loff = _links(sm_on), _links(sm_off)
        assert lon == loff, "scoped causal differs on %s: on=%d off=%d (sym-diff %s)" % (
            doc, len(lon), len(loff), (lon ^ loff))
        eon, eoff = _events(sm_on), _events(sm_off)
        assert len(sm_on.events) >= len(sm_off.events), "recall-ON has FEWER events on %s" % doc
        total_extra += len(sm_on.events) - len(sm_off.events)
    print("W2 SCOPED causal byte-identical (recall ON == OFF) on %d docs: PASS" % len(docs), flush=True)
    print("W3 ADDITIVE detection (ON >= OFF; +%d recovered events over %d docs): PASS" % (total_extra, len(docs)), flush=True)
    print("\nALL WITNESSES PASS", flush=True)


if __name__ == "__main__":
    main()
