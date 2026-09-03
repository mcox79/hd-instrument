"""Organ witness for the predict_surprisal landing (2026-08-31, Q111) -- the forward-prediction N400
surprisal wired into the live SituationReader behind a DEFAULT-OFF flag, from the owner-DONE problem
the_forward_prediction_organ_is_inert_wire_its_surprisal_into_a_live_decision (EXCELLENT).

Proves, on a real LitBank doc through the LIVE read():
  1. DEFAULT-OFF is BYTE-IDENTICAL: a SituationReader() and a predict_surprisal=True reader produce the
     SAME core events (global_idx/predicate/agent/patient/tense); the OFF reader leaves patient_surprisal /
     pred_precision / low_confidence all None (the additive metadata is inert when off).
  2. FLAG-ON POPULATES: events with a grounded verb-PATIENT get a float patient_surprisal + pred_precision.
  3. FAITHFUL WIRING (the load-bearing check): for EVERY scored event, the reader's patient_surprisal EQUALS
     an INDEPENDENT recompute -- PredictiveReader.load(asset).surprisal(lemma_word(predicate), "PATIENT",
     patient, nominal_heads(sentence)) -- i.e. read() runs exactly the validated driver computation.
  4. ABSTAIN: with surprisal_abstain_tau set, low_confidence == (patient_surprisal > tau); None when unset.
  5. ASSET INTEGRITY: the committed foundation asset loads and reproduces surprisal deterministically.

Reverify: .venv/Scripts/python.exe verification/test_predict_surprisal_landing_organ.py
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import sys
import glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.situation_reader import (SituationReader, _PREDICT_SURPRISAL_ASSET,
                                    _SURPRISAL_NOMINAL_POS, _SURPRISAL_PRON_LOW, _FRONTEND_POS_ASSET)
from hdlab.predictive_reader import PredictiveReader
from hdlab.pos_tagger import PosTagger
from hdlab.thematic_role_labeler import lemma_word
from hdlab.scene_segment import parse_conll_sentences
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer

_DOC = sorted(glob.glob(os.path.join(REPO, "data/litbank/coref/conll", "*.conll")))[0]


def _nominal_heads(toks, up):
    out = []
    for i, tk in enumerate(toks):
        if i < len(up) and up[i] in _SURPRISAL_NOMINAL_POS:
            low = tk.lower()
            if low in _SURPRISAL_PRON_LOW:
                continue
            out.append(low)
    return sorted(set(out))


def test_default_off_byte_identical():
    gaz = load_given_gazetteer()
    off = SituationReader(gaz=gaz, predict_surprisal=False).read(_DOC)   # explicit-OFF (flags default-ON since 2026-09-03)
    on = SituationReader(gaz=gaz, predict_surprisal=True, surprisal_abstain_tau=6.0).read(_DOC)
    core_off = [(e.global_idx, e.predicate, e.agent, e.patient, str(e.tense)) for e in off.events]
    core_on = [(e.global_idx, e.predicate, e.agent, e.patient, str(e.tense)) for e in on.events]
    assert core_off == core_on, "predict_surprisal is NOT additive -- core events differ off vs on"
    assert all(e.patient_surprisal is None and e.pred_precision is None and e.low_confidence is None
               for e in off.events), "OFF reader leaked surprisal metadata"
    print(f"PASS default-off: {len(off.events)} events byte-identical off/on; OFF metadata all None")


def test_flag_on_populates_and_is_faithful():
    """The load-bearing check: read()'s surprisal EQUALS an independent recompute with the same asset."""
    gaz = load_given_gazetteer()
    sm = SituationReader(gaz=gaz, predict_surprisal=True).read(_DOC)
    sents = parse_conll_sentences(_DOC)
    pr = PredictiveReader.load(_PREDICT_SURPRISAL_ASSET)
    tagger = PosTagger.load(_FRONTEND_POS_ASSET)
    cand_cache = {}
    n_scored = 0
    for e in sm.events:
        if e.patient in ("?", None):
            continue
        si = e.sent_idx
        if si not in cand_cache:
            toks = sents[si] if 0 <= si < len(sents) else []
            cand_cache[si] = _nominal_heads(toks, tagger.tag(toks)) if toks else []
        exp = pr.surprisal(lemma_word(str(e.predicate).lower()), "PATIENT",
                           str(e.patient).lower(), cand_cache[si])
        exp = None if exp is None else round(float(exp), 6)
        assert e.patient_surprisal == exp, (e.predicate, e.patient, e.patient_surprisal, exp)
        if e.patient_surprisal is not None:
            n_scored += 1
            assert e.pred_precision == pr.precision(lemma_word(str(e.predicate).lower()), "PATIENT")
    assert n_scored >= 1, "no event got a surprisal -- the flag-on pass did not populate"
    print(f"PASS faithful: {n_scored} scored events, each patient_surprisal == independent recompute (byte-exact)")


def test_abstain_flag():
    gaz = load_given_gazetteer()
    tau = 5.0
    sm = SituationReader(gaz=gaz, predict_surprisal=True, surprisal_abstain_tau=tau).read(_DOC)
    sm_notau = SituationReader(gaz=gaz, predict_surprisal=True).read(_DOC)
    n = 0
    for e in sm.events:
        if e.patient_surprisal is not None:
            assert e.low_confidence == (e.patient_surprisal > tau), (e.patient_surprisal, tau, e.low_confidence)
            n += 1
    assert all(e.low_confidence is None for e in sm_notau.events), "low_confidence set without a tau"
    print(f"PASS abstain: low_confidence == (surprisal>{tau}) on {n} scored events; None when no tau")


def test_asset_integrity():
    pr = PredictiveReader.load(_PREDICT_SURPRISAL_ASSET)
    assert len(pr._vr_centroid) > 100, "asset has too few verb-role centroids -- fit failed?"
    s1 = pr.surprisal("study", "PATIENT", "man", ["man", "dog", "house"])
    s2 = pr.surprisal("study", "PATIENT", "man", ["man", "dog", "house"])
    assert s1 == s2, "surprisal not deterministic"
    print(f"PASS asset: {len(pr._vr_centroid)} verb-role centroids; surprisal deterministic ({s1})")


if __name__ == "__main__":
    tests = [test_default_off_byte_identical, test_flag_on_populates_and_is_faithful,
             test_abstain_flag, test_asset_integrity]
    for t in tests:
        t()
    print(f"\nALL {len(tests)} WITNESS TESTS PASSED")
