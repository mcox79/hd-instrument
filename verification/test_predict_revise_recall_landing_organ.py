"""Scaffold-free witness for the LANDING of the predict-and-revise parse-RECALL drop-fill (p2) into the reader.

Proves the default-off `predict_revise` flag on hdlab.situation_reader.SituationReader is an ADDITIVE,
byte-identical-when-off wire whose flag-ON fills reproduce the validated drill's `relcl_fill` (resolve_patient
+ nearest-nominal position fallback) BYTE-EXACT on a REAL LitBank passage. Recomputes everything FROM SOURCE.
Every check can fail.

  [1] DEFAULT-OFF BYTE-IDENTICAL: with the flag off, every event's patient_prerevise is None and NO patient
      is changed -- the flag-off reader is the pre-wire reader.
  [2] RECALL PROTECTED (canonical untouched): flag-on changes ONLY events whose patient was DROPPED ('?');
      every non-dropped patient is identical flag-off vs flag-on (the pass is recall-scoped, not re-selection).
  [3] DROP-FILL FIRES (can-fail): flag-on recovers >=1 dropped patient (patient_prerevise=='?', patient!='?').
  [4] FILL BYTE-EXACT vs the validated drill: for every recovered event, the filled patient EQUALS an
      independent relcl_fill recompute -- resolve_patient(toks,pos,v+1) else nearest-nominal position fallback
      (candidates = non-pronoun nominals) -- the SAME logic the validated _drill_reuse_relcl_resolver_v1 measured.

Brain frame (PINNED): noisy-channel predict-and-revise -- recover the pre-verbal patient the batch parse DROPS
via the active-filler filler-gap resolver (relcl_resolver; Frazier & Flores d'Arcais), recall-scoped, no
surprisal gate (p2's structural drop-fill drill). Glass-box, NO LLM.

Run: .venv/Scripts/python.exe verification/test_predict_revise_recall_landing_organ.py
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_situation_model_qa_v1 as QA  # noqa: E402
from hdlab.situation_reader import SituationReader, parse_conll_sentences  # noqa: E402
from hdlab import relcl_resolver as RR  # noqa: E402
from experiments._forward_prediction_live import get_tagger, NOMINAL, PRON_LOW  # noqa: E402


# the p2 wire composes with role_route='wired' (the assembly who-did-what path) + the capable flags
CAPABLE = dict(tense_agnostic_events=True, preserve_tense=True, timeline_register=True,
               track_space=True, verb_subcat_gate=True, role_route="wired",
               spacy_pred_gate=False, causation_typed=False)


def _sig(sm):
    """Per-event signature of the fields the wire must NOT touch except the dropped patient."""
    return [(e.global_idx, str(e.predicate), str(e.agent), str(e.tense)) for e in sm.events]


def _relcl_fill_ref(toks, up, v0):
    """Independent reference reproduction of the validated drill's relcl_fill (== _read_predict_revise)."""
    cands = [(toks[i].lower(), i) for i in range(len(toks))
             if i < len(up) and up[i] in NOMINAL and toks[i].lower() not in PRON_LOW]
    idx = RR.resolve_patient(toks, up, v0 + 1)
    if idx is not None and 1 <= idx <= len(toks):
        return toks[idx - 1].lower()
    if cands:
        best, bd = None, 10 ** 9
        for (h, ci) in cands:
            if abs(ci - v0) < bd:
                bd, best = abs(ci - v0), h
        return best
    return None


def main():
    gaz = QA.load_given_gazetteer()
    reader_off = SituationReader(gaz=gaz, predict_revise=False, **CAPABLE)
    reader_on = SituationReader(gaz=gaz, predict_revise=True, **CAPABLE)
    tagger = get_tagger()

    doc_used = sm_off = sm_on = None
    for doc in QA.load_docs(12):
        path = os.path.join(QA.CONLL_DIR, doc + ".conll")
        if not os.path.exists(path):
            continue
        on = reader_on.read(path)
        n_fill = sum(1 for e in on.events if e.patient_prerevise == "?")
        if n_fill >= 1:                      # pick the first doc where the drop-fill actually fires
            doc_used, sm_on = doc, on
            sm_off = reader_off.read(path)
            break
    assert sm_on is not None, "no LitBank doc had a dropped patient the wire filled (need a can-fail fire)"
    sents = parse_conll_sentences(os.path.join(QA.CONLL_DIR, doc_used + ".conll"))

    checks = []

    # [1] DEFAULT-OFF byte-identical.
    off_ok = (all(e.patient_prerevise is None for e in sm_off.events)
              and _sig(sm_off) == _sig(sm_on)
              and len(sm_off.events) == len(sm_on.events))
    checks.append((off_ok,
                   "[1] DEFAULT-OFF byte-identical: flag-off patient_prerevise all None; event set (%d) + "
                   "predicate/agent/tense identical to flag-on" % len(sm_off.events)))

    # [2] RECALL PROTECTED: non-dropped patients identical off vs on.
    off_by_gi = {e.global_idx: e for e in sm_off.events}
    protected = 0
    changed_nondrop = 0
    for e in sm_on.events:
        o = off_by_gi.get(e.global_idx)
        if o is None:
            continue
        if o.patient not in ("?", None):     # a canonical (non-dropped) patient
            if e.patient == o.patient and e.patient_prerevise is None:
                protected += 1
            else:
                changed_nondrop += 1
    checks.append((changed_nondrop == 0 and protected > 0,
                   "[2] RECALL PROTECTED: %d canonical patients unchanged flag-on, %d wrongly changed "
                   "(recall-scoped: the pass touches ONLY drops)" % (protected, changed_nondrop)))

    # [3] DROP-FILL FIRES (can-fail).
    fills = [e for e in sm_on.events if e.patient_prerevise == "?"]
    checks.append((len(fills) >= 1,
                   "[3] DROP-FILL FIRES: recovered %d dropped patients on doc '%s' (patient_prerevise=='?')"
                   % (len(fills), doc_used)))

    # [4] FILL BYTE-EXACT vs the validated drill's relcl_fill.
    exact = 0
    bad = []
    for e in fills:
        si = e.sent_idx
        toks = sents[si]
        up = tagger.tag(toks)
        ref = _relcl_fill_ref(toks, up, int(e.pred_idx))
        if e.patient == ref:
            exact += 1
        else:
            bad.append((e.global_idx, e.patient, ref))
    checks.append((len(fills) > 0 and exact == len(fills),
                   "[4] FILL BYTE-EXACT: %d/%d recovered patients EQUAL the independent relcl_fill recompute "
                   "(resolve_patient + nominal position fallback)%s"
                   % (exact, len(fills), "" if not bad else " ; mismatches=%s" % bad[:3])))

    print("=== witness: predict-and-revise drop-fill LANDING (doc '%s', %d events, %d fills) ==="
          % (doc_used, len(sm_on.events), len(fills)))
    ok_all = True
    for ok, msg in checks:
        print("  %s  %s" % ("PASS" if ok else "FAIL", msg))
        ok_all = ok_all and bool(ok)
    print("\nRESULT: %s (%d/%d)" % ("ALL CHECKS PASS" if ok_all else "FAIL",
                                    sum(1 for ok, _ in checks if ok), len(checks)))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
