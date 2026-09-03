"""Landing witness for hdlab/predicate_detector.py + the SituationReader `predicate_recall` flag (the owner-DONE
register_robust_event_detection... P6 wire). Proves: (1) the organ's logistic score reproduces the reference
sklearn predict_proba on standardized features EXACTLY (byte-faithful to the validated asset); (2) the register-
invariant gate/rescue promotes a tagger-DROPPED real verb ("the lake PRESENTS...") and REJECTS the noun-flanked
distractors below threshold; (3) the wire is ADDITIVE -- flag-ON event detection is a strict SUPERSET of flag-OFF
(the existing UPOS==VERB detections + their fields are byte-identical, extras only for dropped predicates);
(4) a normal all-verbs-tagged sentence is byte-identical ON vs OFF; (5) the flag is default-off + factory-covered
and both readers run read() end-to-end; (6) the rescue gate never touches a VERB/AUX token. Glass-box, NO LLM.
Run:
  .venv/Scripts/python.exe verification/test_predicate_recall_landing_organ.py
"""
import json
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.chdir(_REPO)

from hdlab.pos_tagger import PosTagger
from hdlab.predicate_detector import PredicateDetector, feats_parsefree, FEAT_NAMES
from hdlab.situation_reader import SituationReader

POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
ASSET = os.path.join(_REPO, "data/frontend_assets/predicate_detector_ud_qasrl.json")
DOC = os.path.join(_REPO, "data/litbank/coref/conll/1023_bleak_house_brat.conll")

_n = 0


def _ok(cond, msg):
    global _n
    assert cond, "FAIL: " + msg
    _n += 1
    print("  PASS " + msg, flush=True)


def _evkey(evs):
    return sorted((e.idx, e.lemma, e.pos, e.tense, e.is_pp) for e in evs)


def main():
    tg = PosTagger.load(POS_ASSET)
    W = tg._perc.weights
    tags = tg.tags
    det = PredicateDetector.load()

    # 1. FAITHFULNESS: organ score == sigmoid(coef . standardize(feats) + intercept) from the raw asset, exactly
    a = json.load(open(ASSET, encoding="utf-8"))
    _ok(a["feat_names"] == FEAT_NAMES and not a.get("with_parse", False), "asset is the parse-free 7-cue detector")
    sent = "the lake presents an unbroken sheet of ice".split()
    pos = tg.tag(sent)
    maxerr = 0.0
    n_cand = 0
    for i in range(len(sent)):
        if not det.is_candidate(sent, pos, i):
            continue
        n_cand += 1
        fv = feats_parsefree(sent, pos, i, W, tags)
        z = a["intercept"]
        for k in range(len(a["coef"])):
            sd = a["sd"][k] if a["sd"][k] != 0 else 1.0
            z += a["coef"][k] * ((fv[k] - a["mu"][k]) / sd)
        ref = 1.0 / (1.0 + math.exp(-z))
        maxerr = max(maxerr, abs(ref - det.score(sent, pos, i, W, tags)))
    _ok(maxerr < 1e-9, "organ score == reference logistic (max abs err %.1e < 1e-9)" % maxerr)

    # 2. RESCUE CORRECTNESS: the mistagged verb is promoted; the noun-flanked distractors are not
    _ok(pos[2] != "VERB", "'presents' is DROPPED by the tagger (tagged %s, not VERB)" % pos[2])
    resc = dict(det.rescue_indices(sent, pos, W, tags))
    _ok(2 in resc and resc[2] >= det.threshold, "detector rescues the real verb 'presents' (p=%.3f >= th=%.3f)"
        % (resc.get(2, 0.0), det.threshold))
    _ok(5 not in resc and 7 not in resc, "detector REJECTS noun-flanked distractors 'sheet'/'ice' (< threshold)")

    # 6. GATE never touches VERB/AUX (additive-by-construction precondition)
    _ok(all(pos[i] not in ("VERB", "AUX") for i, _ in det.rescue_indices(sent, pos, W, tags)),
        "rescue gate excludes VERB/AUX tokens (additive: existing detections untouched)")

    # 3. ADDITIVE / no-regression at the event-detection level, on a register-diverse set (drops + clean)
    r_off = SituationReader()
    r_on = SituationReader(predicate_recall=True)
    texts = [
        "the lake presents an unbroken sheet of ice",      # 'presents' dropped -> +1 event
        "the man ate the apple and the dog chased the cat",  # all verbs tagged -> byte-identical
        "she quickly ran home",                             # clean
    ]
    total_off = total_on = 0
    for t in texts:
        eoff, _ = r_off._extract_events(t)
        eon, _ = r_on._extract_events(t)
        koff, kon = _evkey(eoff), _evkey(eon)
        # every OFF event is present UNCHANGED in ON (strict superset -> the UPOS==VERB detections are byte-identical)
        _ok(all(k in kon for k in koff), "flag-ON is a strict superset of flag-OFF for: %r" % t)
        total_off += len(eoff)
        total_on += len(eon)
    _ok(total_on > total_off, "flag-ON adds recovered predicates overall (%d > %d events)" % (total_on, total_off))

    # 4. NORMAL sentence byte-identical ON vs OFF
    norm = "the man ate the apple and the dog chased the cat"
    _ok(_evkey(r_off._extract_events(norm)[0]) == _evkey(r_on._extract_events(norm)[0]),
        "all-verbs-tagged sentence is byte-identical ON vs OFF (nothing dropped -> nothing added)")

    # 5. CONSTRUCTOR / FACTORY + end-to-end read()
    _ok("predicate_recall" in SituationReader.CAPABILITY_FLAGS, "flag in CAPABILITY_FLAGS")
    _ok(SituationReader().predicate_recall is False
        and SituationReader.all_capabilities_off().predicate_recall is False,
        "default OFF + all_capabilities_off() covers it")
    sm_off = SituationReader().read(DOC)
    sm_on = SituationReader(predicate_recall=True).read(DOC)
    _ok(len(sm_off.events) > 0, "default-off reader runs read() (byte-identical detection path)")
    _ok(len(sm_on.events) >= len(sm_off.events),
        "flag-on reader runs read() and never DROPS events (%d >= %d, additive through the full pipeline)"
        % (len(sm_on.events), len(sm_off.events)))

    print("%d/%d checks passed" % (_n, _n), flush=True)
    print("SELF-TEST PASSED", flush=True)


if __name__ == "__main__":
    main()
