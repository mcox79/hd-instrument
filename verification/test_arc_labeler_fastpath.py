"""Scaffold-free witness: byte-identical fast path for hdlab.arc_labeler.ArcLabeler._predict_label.
(additional inefficiency from route_the_redundant_nltk_perceptron_tagger_through_the_fast_hdlab_tagger)

C1  per-arc predicted label byte-identical (stock vs fast plan) over real conll arcs.
C2  a full read with the fast labeler installed yields byte-identical sm.entity_states.
C3  the fast plan is genuinely doing the work: an info-free (weights-shuffled) plan does NOT reproduce
    the labels (guards against a vacuous 'identical because trivial').

Run: .venv/Scripts/python.exe verification/test_arc_labeler_fastpath.py
"""
from __future__ import annotations
import os, sys, random
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.situation_reader import SituationReader
import hdlab.arc_labeler as AL
from experiments.exp_arc_labeler_fastpath_v1 import FastLabelPlan


def c1_arc_byte_identity(ndocs=2):
    lab = AL.ArcLabeler.load(os.path.join(_REPO, "data/frontend_assets/arc_labeler_hashed_ud_ewt.json"))
    plan = FastLabelPlan(lab.weights, lab.labels)
    gaz = SITQA.load_given_gazetteer()
    reader = SituationReader(gaz=gaz)
    tagger = reader._frontend_tagger(); parser = reader._frontend_parser()
    n = mism = 0
    for doc in SITQA.load_docs(None)[:ndocs]:
        p = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        if not os.path.exists(p):
            continue
        for toks in SITQA._conll_sents(p):
            if not toks or len(toks) > 60:
                continue
            up = tagger.tag(list(toks)); heads = parser.parse(list(toks), up).heads
            for i in range(1, len(toks) + 1):
                h = heads.get(i, 0)
                if h is None or h < 0 or h > len(toks):
                    h = 0
                feats = AL.arc_features(toks, up, i, h)
                n += 1
                if lab._predict_label(feats) != plan.predict(feats):
                    mism += 1
    assert mism == 0, "arc label mismatch: %d/%d" % (mism, n)
    print("  C1 PASS: fast plan byte-identical over %d real arcs (%d docs)" % (n, ndocs))
    return lab


def c2_entity_states_identical(ndocs=2):
    gaz = SITQA.load_given_gazetteer()
    for doc in SITQA.load_docs(None)[:ndocs]:
        p = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        if not os.path.exists(p):
            continue
        r = SituationReader(gaz=gaz)
        sm0 = r.read(p)
        es0 = [(e.sent_idx, e.holder, e.property, e.htype) for e in sm0.entity_states]
        if getattr(r, "_es_lab", None) is None:
            continue
        plan = FastLabelPlan(r._es_lab.weights, r._es_lab.labels)
        r._es_lab._predict_label = plan.predict
        sm1 = r.read(p)
        es1 = [(e.sent_idx, e.holder, e.property, e.htype) for e in sm1.entity_states]
        assert es0 == es1, "entity_states diverged on %s: %d vs %d" % (doc, len(es0), len(es1))
    print("  C2 PASS: full-read sm.entity_states byte-identical with the fast labeler (%d docs)" % ndocs)


def c3_infofree_plan_differs(lab):
    """A weights-shuffled plan must NOT reproduce the labels -- proves the identity is non-vacuous."""
    keys = list(lab.weights.keys()); vals = [lab.weights[k] for k in keys]
    rng = random.Random(20260905); rng.shuffle(vals)
    shuffled = {k: v for k, v in zip(keys, vals)}
    good = FastLabelPlan(lab.weights, lab.labels)
    bad = FastLabelPlan(shuffled, lab.labels)
    toks = ["the", "wolf", "bit", "the", "sheep"]; pos = ["DET", "NOUN", "VERB", "DET", "NOUN"]
    diff = 0
    for i in range(1, len(toks) + 1):
        for h in (0, 3):
            feats = AL.arc_features(toks, pos, i, h)
            if good.predict(feats) != bad.predict(feats):
                diff += 1
    assert diff > 0, "info-free shuffled-weights plan matched the real plan (vacuous identity)"
    print("  C3 PASS: info-free shuffled-weights plan diverges (identity is non-vacuous)")


if __name__ == "__main__":
    print("witness: byte-identical arc-labeler fast path")
    lab = c1_arc_byte_identity()
    c2_entity_states_identical()
    c3_infofree_plan_differs(lab)
    print("ALL CHECKS PASS (3/3)")


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_file_as_test as _pri128_run


@_pri128_pytest.mark.slow
def test_witness():
    _code, _out = _pri128_run(__file__)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
