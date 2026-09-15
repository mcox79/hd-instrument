"""Landing witness for hdlab/predicate_detector.py + the SituationReader `predicate_recall` flag (the owner-DONE
register_robust_event_detection... P6 wire). Proves: (1) the organ's logistic score reproduces the reference
sklearn predict_proba on standardized features EXACTLY (byte-faithful to the validated asset); (2) the register-
invariant gate/rescue promotes a tagger-DROPPED real verb ("the lake PRESENTS...") and REJECTS the noun-flanked
distractors below threshold; (3) the wire is ADDITIVE -- flag-ON event detection is a strict SUPERSET of flag-OFF
(the existing UPOS==VERB detections + their fields are byte-identical, extras only for dropped predicates);
(4) a normal all-verbs-tagged sentence is byte-identical ON vs OFF; (5) the flag is a capability + factory-covered
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
    # 2026-09-14 (strategy): PosTagger.load() now routes to the frontend's category organ (no perceptron weights); this witness
    # checks the DETECTOR's faithfulness to its own asset, which was fitted against the perceptron's verb margin, so it loads the
    # raw perceptron explicitly. The LIVE reader uses the BF form (the category posterior's verb belief; situation_reader
    # _rescue branch) -- that form is measured by the reader witnesses, not here.
    tg = PosTagger.load(POS_ASSET, _raw=True)
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
    # 2026-09-14 (strategy): predicate_recall has been DEFAULT-ON since 2026-09-05, so SituationReader() == the ON reader and the
    # 'adds predicates' check could never pass (stale premise); OFF must be selected explicitly.
    r_off = SituationReader(predicate_recall=False)
    r_on = SituationReader(predicate_recall=True)
    # 2026-09-14 (pri-107): the first three are the historic set; the last three are MODERN UD-EWT test sentences
    # (gold UPOS) on which the LIVE category organ drops a real verb and the BF rescue recovers it with no false
    # promotion -- so "flag-ON adds recovered predicates" is a live-chain check, not a perceptron-era one.
    texts = [
        "the lake presents an unbroken sheet of ice",      # 'presents' dropped (19c-flavoured)
        "the man ate the apple and the dog chased the cat",  # all verbs tagged -> byte-identical
        "she quickly ran home",                             # clean
        "They own blogger , of course .",                   # gold VERB 'own' dropped -> rescued
        "Plus you land in a preferential terminal ...",     # gold VERB 'land' dropped -> rescued
        "how do you mold silicone or rubber into a mermaid tail ?",   # gold VERB 'mold' dropped -> rescued
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
    # 2026-09-14 (pri-107): predicate_recall has been DEFAULT-ON since 2026-09-05, so the stale "default OFF"
    # premise made this check unsatisfiable. What must hold is that it is a real capability flag and that
    # all_capabilities_off() turns it off.
    _ok(SituationReader().predicate_recall is True
        and SituationReader.all_capabilities_off().predicate_recall is False,
        "default ON + all_capabilities_off() turns it off")
    sm_off = SituationReader(predicate_recall=False).read(DOC)
    sm_on = SituationReader(predicate_recall=True).read(DOC)
    _ok(len(sm_off.events) > 0, "flag-off reader runs read() (byte-identical detection path)")
    _ok(len(sm_on.events) >= len(sm_off.events),
        "flag-on reader runs read() and never DROPS events (%d >= %d, additive through the full pipeline)"
        % (len(sm_on.events), len(sm_off.events)))

    # =================================================================================================
    # 7. THE LIVE CHAIN (2026-09-14, pri-107). Everything above checks the detector against the PERCEPTRON its
    #    asset was fitted to. The live path has been the brain-foundational category organ since 2026-09-12, and
    #    under it the rescue was DORMANT -- this section is what was silently failing.
    # =================================================================================================
    from hdlab import lexical_categories as LC
    from hdlab.predicate_detector import (BFPredicateDetector, bf_cue_block, category_emission,
                                          has_verb_reading_glassbox)
    lc = LC.get()
    bf = BFPredicateDetector.load()
    live = lc.tag(sent)
    _ok(live[2] != "VERB", "under the LIVE category organ 'presents' is still DROPPED (tagged %s)" % live[2])

    cues = bf_cue_block(lc, sent, live, lc.posterior(sent), category_emission(lc, sent))
    s_presents, s_sheet, s_ice = bf.score(cues[2]), bf.score(cues[5]), bf.score(cues[7])
    # THE CAPABILITY: the mis-tagged real verb is ranked far above its noun-flanked distractors. (The DEPLOYED
    # threshold is an FP-BUDGET knob; this sentence sits below the precision-preserving default and above the
    # recall-oriented threshold recorded in the same asset -- see SOLVED.md, which reports both.)
    _ok(s_presents > 10 * max(s_sheet, s_ice),
        "the BF rescue ranks the real verb 'presents' far above the distractors (%.4f vs sheet %.4f / ice %.4f)"
        % (s_presents, s_sheet, s_ice))
    recall_th = float(bf.thresholds_by_budget.get("0.25", {}).get("threshold") or bf.threshold)
    _ok(s_presents >= recall_th,
        "the BF rescue FIRES on 'presents' at the asset's recall-oriented operating point (%.4f >= %.4f)"
        % (s_presents, recall_th))

    # THE LIVE CHAIN FIRES ON MODERN PROSE at the DEPLOYED threshold, and only on the real verbs
    for text, want in (("They own blogger , of course .", 1),
                       ("Plus you land in a preferential terminal ...", 2),
                       ("how do you mold silicone or rubber into a mermaid tail ?", 3)):
        toks = text.split()
        tags = lc.tag(toks)
        r = dict(bf.rescue_indices(toks, tags, lc))
        _ok(set(r) == {want}, "BF rescue recovers exactly the dropped verb %r in %r (got %r)"
            % (toks[want], text, [toks[i] for i in sorted(r)]))
        _ok(all(tags[i] not in ("VERB", "AUX") for i in r),
            "the BF rescue never touches a VERB/AUX token in %r (additive by construction)" % text)

    # THE GATE IS GLASS-BOX: no nltk at inference, same decision as the WordNet gate
    from hdlab.predicate_detector import has_verb_reading as _wn_gate
    _ok(all(has_verb_reading_glassbox(w) == _wn_gate(w) for w in sent),
        "the glass-box morphology gate agrees with the WordNet gate on the witness (no nltk at inference)")

    # THE COMBINER IS PLASTIC: `observe` is a live online path, and the score moves with experience
    before = bf.score(cues[5])
    for _ in range(80):
        bf.observe(cues[5], 1)
    _ok(bf.score(cues[5]) > before,
        "observe() is a live plastic path (score %.4f -> %.4f after 80 positive outcomes)"
        % (before, bf.score(cues[5])))

    # AND THE READER ITSELF fires the recovered predicate on the live chain (this is the dormancy check)
    r_on2 = SituationReader(predicate_recall=True)
    r_off2 = SituationReader(predicate_recall=False)
    add = 0
    for text in ("They own blogger , of course .", "Plus you land in a preferential terminal ...",
                 "how do you mold silicone or rubber into a mermaid tail ?"):
        add += len(r_on2._extract_events(text)[0]) - len(r_off2._extract_events(text)[0])
    _ok(add == 3, "the LIVE reader fires one recovered predicate per modern witness sentence (%d extra events)" % add)

    print("%d/%d checks passed" % (_n, _n), flush=True)
    print("SELF-TEST PASSED", flush=True)


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
