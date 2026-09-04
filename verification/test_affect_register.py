"""Scaffold-free witnesses for the AFFECT/EMOTION situation-model dimension (the per-character affect
register + the upstream psych-verb experiencer-linking frame). Runs the REAL code paths, no mocks.

Reverify:  .venv/Scripts/python.exe verification/test_affect_register.py    # expect ALL PASS

W1  unit: extract binds the right emotion to the right experiencer (copular + object-exp psych verb)
W2  LitBank: "how does X feel" model CI-separated over the char-blind most-recent-emotion-word floor
W2b LitBank: the shuffled-character info-free twin LOSES
W3  UPSTREAM object-experiencer correction: the frame binds the OBJECT (experiencer); naive binds the
    SUBJECT (the inanimate stimulus) and is wrong on every object-experiencer sentence
W4  valence-sign accuracy on the reliable slice (the primary PINNED channel)
W5  copular adjective: 'was afraid' AND passive-participle 'was frightened' bind the SUBJECT
W6  positive control: multi-character passages where the char-blind floor returns the WRONG character
W7  'to her delight' + 'her fear' bind the possessor as experiencer
W8  overwrite dynamics: feels() returns the MOST RECENT emotion (de Vega), not an older one
W9  upstream frame: fear=subject / frighten=object / appeal=oblique; alternating resolved by frame shape
W10 ZERO REGRESSION: the psych-verb frame gates ONLY psych-verb experiencer position; every non-psych
    affect (copular/adverb/noun/to-poss) is byte-identical frame vs naive
W11 located negative: unstated action-implied emotion ('she slammed the door') yields NO explicit affect
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.affect_register as AR
from experiments.affect_lexicon import AffectLexicon
from experiments.psych_verb_frames import PsychVerbFrames
import experiments.exp_affect_register_qa_v1 as E
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer

LEX = AffectLexicon.load()
PVF = PsychVerbFrames.load()
_TAG = None


def tag(toks):
    global _TAG
    if _TAG is None:
        _TAG = E._tagger()
    return _TAG.tag(list(toks))


def _affects(sents):
    pos = [tag(t) for t in sents]
    return AR.extract_affect(sents, pos, LEX, pvf=PVF)


def w1_unit_binding():
    sents = [["Mary", "was", "afraid", "."], ["The", "dog", "frightened", "John", "."]]
    aff = _affects(sents)
    by = {(a.experiencer, a.emotion_word): a for a in aff}
    assert any(a.experiencer == "mary" and a.emotion_cat == "fear" and a.valence_sign == -1
               for a in aff), [(a.experiencer, a.emotion_word, a.emotion_cat) for a in aff]
    # object-experiencer: John (object) is the experiencer, not the dog (subject/stimulus)
    j = [a for a in aff if a.kind == "psych_verb"]
    assert j and j[0].experiencer == "john" and j[0].stimulus == "dog", [(a.experiencer, a.stimulus) for a in j]
    return "W1 unit binding (copular + object-exp psych)"


def _litbank_feel(n_docs=25, seed=20260904):
    gaz = load_given_gazetteer()
    docs = E.load_docs(n_docs)
    res = E.run(docs, seed=seed, n_boot=800, n_twin=60)
    return res


def w2_feel_ci_separated(res):
    fr = res["feel_reliable"]
    m = fr["acc"]["model"]; fl = fr["acc"]["floor_recent_emotion"]
    sep = fr["ci"].get("sep_over_floor_recent_emotion")
    assert m is not None and fl is not None and m > fl and sep, (m, fl, fr["ci"])
    return "W2 feel model %.3f CI-sep over recent-emotion floor %.3f (n=%d)" % (m, fl, fr["n"])


def w2b_twin_loses(res):
    fr = res["feel_reliable"]
    m = fr["acc"]["model"]; tw = fr["acc"]["twin_shuffled_char"]
    sep = fr["ci"].get("sep_over_twin_shuffled_char")
    p95 = (res["feel_all"].get("twin_null_p95") or {}).get("p95")
    assert m > tw and sep, (m, tw, fr["ci"])
    assert p95 is None or m > p95, (m, p95)
    return "W2b shuffled-char twin loses: model %.3f > twin %.3f (null p95=%s)" % (m, tw, p95)


def w3_object_experiencer_correction():
    ab = E.authored_experiencer_ab()
    assert ab["frame_acc"] == 1.0 and ab["naive_acc"] < ab["frame_acc"], ab
    assert ab["object_exp"]["frame_correct"] == ab["object_exp"]["n"] and ab["object_exp"]["n"] >= 4, ab
    return "W3 object-exp: frame %.3f vs naive %.3f (obj-exp %d/%d correct)" % (
        ab["frame_acc"], ab["naive_acc"], ab["object_exp"]["frame_correct"], ab["object_exp"]["n"])


def w4_valence_sign(res):
    vs = res["valence_sign"]
    m = vs["acc"]["model"]; fl = vs["acc"]["floor_recent_emotion"]
    sep = vs["ci"].get("sep_over_floor_recent_emotion")
    assert m is not None and fl is not None and m > fl and sep, (m, fl, vs["ci"])
    return "W4 valence-sign (primary PINNED channel) model %.3f CI-sep over floor %.3f (n=%d)" % (m, fl, vs["n"])


def w5_copular_adjective():
    # plain adjective + passive-participle adjective both bind the copula SUBJECT
    a1 = _affects([["She", "was", "afraid", "."]])
    a2 = _affects([["He", "was", "frightened", "."]])          # passive/participle -> subject experiencer
    a3 = _affects([["Anna", "felt", "happy", "."]])
    assert any(a.experiencer == "she" and a.valence_sign == -1 for a in a1), a1
    assert any(a.experiencer == "he" for a in a2), [(a.experiencer, a.kind) for a in a2]
    assert any(a.experiencer == "anna" and a.valence_sign == 1 for a in a3), a3
    return "W5 copular adj (plain + passive participle) bind the subject"


def w6_positive_control(n_docs=25):
    gaz = load_given_gazetteer()
    docs = E.load_docs(n_docs)
    pc = E.positive_control(docs, gaz)
    assert pc["model_right_charblind_wrong"] > pc["charblind_right_model_wrong"], pc
    return "W6 positive control: model-right/floor-wrong %d vs reverse %d" % (
        pc["model_right_charblind_wrong"], pc["charblind_right_model_wrong"])


def w7_possessor_binding():
    a1 = _affects([["To", "her", "delight", ",", "he", "came", "."]])
    a2 = _affects([["His", "fear", "was", "great", "."]])
    assert any(a.kind == "to_poss" and a.experiencer == "her" and a.valence_sign == 1 for a in a1), a1
    assert any(a.kind == "noun_poss" and a.experiencer == "his" for a in a2), a2
    return "W7 'to her delight' + 'his fear' bind the possessor"


def w8_overwrite_dynamics():
    # Mary: fear (early) then joy (late). feels() returns the CURRENT (most recent) emotion (overwrite).
    sents = [["Mary", "was", "afraid", "."], ["Later", "Mary", "was", "happy", "."]]
    pos = [tag(t) for t in sents]
    aff = AR.extract_affect(sents, pos, LEX, pvf=PVF)
    for a in aff:
        a.experiencer_canonical = "mary"
    reg = AR.AffectRegister(aff)
    cur = reg.feels("mary")
    assert cur is not None and cur.valence_sign == 1 and cur.sent_idx == 1, (cur.emotion_word, cur.sent_idx)
    assert len(reg.affects_of("mary")) == 2
    return "W8 overwrite: feels() returns the most recent emotion (joy), not the older (fear)"


def w9_upstream_frame():
    assert PVF.experiencer_position("fear") == "subject"
    assert PVF.experiencer_position("frighten") == "object"
    assert PVF.experiencer_position("appeal") == "oblique"
    # alternating resolved by frame shape
    assert PVF.experiencer_position("worry", has_object=True) == "object"
    assert PVF.experiencer_position("worry", has_object=False) == "subject"
    # inflected forms normalize
    assert PVF.experiencer_position("frightened") == "object"
    assert PVF.experiencer_position("loved") == "subject"
    assert PVF.experiencer_position("zzznovelverb") == "subject"     # unknown -> default subject
    return "W9 upstream frame: fear=subj / frighten=obj / appeal=obl / alternating by frame shape"


def w10_zero_regression(n_docs=15):
    """The psych-verb frame gates ONLY psych-verb experiencer position: every NON-psych affect
    (copular/felt/adverb/to_poss/noun_poss/metaphor) is byte-identical frame vs naive."""
    gaz = load_given_gazetteer()
    docs = E.load_docs(n_docs)
    total_non_psych = 0

    def sig(affects):
        return sorted((a.sent_idx, a.tok, a.kind, a.experiencer, a.emotion_word, a.valence_sign)
                      for a in affects if a.kind != "psych_verb")
    for doc in docs:
        df = E.read_doc(doc, gaz, pvf="default")
        dn = E.read_doc(doc, gaz, pvf=None)
        if df is None:
            continue
        sf, sn = sig(df["affects"]), sig(dn["affects"])
        total_non_psych += len(sf)
        assert sf == sn, ("non-psych affects changed frame vs naive in %s" % doc,
                          [x for x in sf if x not in sn], [x for x in sn if x not in sf])
    return "W10 zero regression: %d non-psych affects byte-identical frame vs naive (%d docs)" % (
        total_non_psych, n_docs)


def w11_located_negative():
    # unstated action-implied emotion is NOT extracted glass-box (needs the OCC meaning channel)
    aff = _affects([["She", "slammed", "the", "door", "."]])
    assert not aff, [(a.experiencer, a.emotion_word) for a in aff]
    return "W11 located negative: 'she slammed the door' yields NO explicit affect (needs meaning channel)"


def main():
    print("=" * 78)
    print("AFFECT REGISTER witnesses (real code paths, no scaffold)")
    print("=" * 78)
    results = []
    # fast unit/frame witnesses first
    for fn in (w1_unit_binding, w3_object_experiencer_correction, w5_copular_adjective,
               w7_possessor_binding, w8_overwrite_dynamics, w9_upstream_frame,
               w11_located_negative, w10_zero_regression):
        results.append(fn())
        print("PASS:", results[-1])
    # LitBank-based witnesses share one run
    res = _litbank_feel(n_docs=25)
    for fn in (w2_feel_ci_separated, w2b_twin_loses, w4_valence_sign):
        results.append(fn(res))
        print("PASS:", results[-1])
    print("PASS:", w6_positive_control(25))
    print("-" * 78)
    print("ALL %d WITNESSES PASS" % (len(results) + 1))


if __name__ == "__main__":
    main()
