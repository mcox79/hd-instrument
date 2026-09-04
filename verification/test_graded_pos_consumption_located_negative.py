"""WITNESS: consuming the graded POS posterior in referent_per_np / role assignment is a LOCATED NEGATIVE,
and the brain-foundational animacy fix does NOT regress the live reader.

Problem: consume_the_graded_pos_posterior_uncertainty_aware_starting_with_referent_np_detection.
The graded posterior cannot beat the hard 1-best on the live who-did-what / coref consumer, with the cause named
and MEASURED. This witness asserts the four load-bearing claims, fast + scaffold-free:

  (1) INTRODUCTION-INVARIANCE: flipping every PROPN<->NOUN in the tagger output leaves referent_per_np's opened-
      head set IDENTICAL (NOUN and PROPN are both in NOMINAL) -> the brief's "opens the wrong referent / mis-
      clusters a name" mechanism is refuted for introduction.
  (2) FRAME-SATURATION: the graded CRF soft-nominal recovery (P(NOUN)+P(PROPN)>=tau) adds < 1% of gold content
      heads over the deployed frame detector -> no coverage lever for who-did-what.
  (3) GRADED ANIMACY IS A REAL BUT SUBORDINATE CUE: on the non-canonical role gold, the graded-animacy cue BEATS
      the shuffled-posterior twin (the mechanism is real), yet does NOT CI-separate over the hard-1-best floor
      (English word-order dominance caps it) -- reproduced from the landed metrics.
  (4) NO-REGRESS: patching animacy to the brain-foundational name->animate rule leaves the LIVE reader's
      who-did-what + coref outputs byte-identical on a real doc (animacy is not in the primary role path).

Run: .venv/Scripts/python.exe verification/test_graded_pos_consumption_located_negative.py
Glass-box, CPU, NO LLM. Writes nothing. ASCII.
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger
from hdlab.crf_tagger import GlassBoxCRF
from hdlab.scene_segment import parse_conll_sentences
from hdlab.referent_per_np import _content_head_positions, frame_heads, NOMINAL, STOP
import hdlab.animacy_lexicon as AL

POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
LB = os.path.join(_REPO, "data/litbank/coref_conll")
UD = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
NOMSET = frozenset(NOMINAL)


def _load_ud(n):
    out, toks, ups = [], [], []
    with open(UD, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if toks:
                    out.append((toks, ups)); toks, ups = [], []
                    if len(out) >= n:
                        return out
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if len(c) < 4 or "-" in c[0] or "." in c[0]:
                continue
            toks.append(c[1]); ups.append(c[3])
    return out


def main():
    import glob
    perc = PosTagger.load(POS_ASSET)
    crf = GlassBoxCRF.load()
    Li = crf.Li
    checks = []

    # (1) introduction-invariance on real LitBank docs
    docs = sorted(glob.glob(os.path.join(LB, "*.conll")))[:4]
    diffs = 0; nsent = 0
    for d in docs:
        for toks in parse_conll_sentences(d):
            if not toks or len(toks) > 120:
                continue
            nsent += 1
            up = perc.tag(list(toks))
            flip = ["NOUN" if u == "PROPN" else ("PROPN" if u == "NOUN" else u) for u in up]
            h0 = set(_content_head_positions(toks, up)) | frame_heads(toks, up, set(_content_head_positions(toks, up)))
            b1 = set(_content_head_positions(toks, flip))
            h1 = b1 | frame_heads(toks, flip, b1)
            if h0 != h1:
                diffs += 1
    checks.append(("(1) referent introduction PROPN<->NOUN-invariant (0 head-set diffs)", diffs == 0,
                   "%d/%d sents changed" % (diffs, nsent)))

    # (2) frame-saturation: soft-nominal recovers < 1% of gold heads over frame (UD gold)
    ud = _load_ud(1200)
    gold_heads = perc_hit = frame_rec = soft_extra = 0
    tau = 0.7
    for toks, gup in ud:
        up = perc.tag(list(toks))
        M = crf.marginals(toks)
        nm = M[:, Li["NOUN"]] + M[:, Li["PROPN"]]
        base = set(_content_head_positions(toks, up))
        frame = frame_heads(toks, up, base)
        for i, (tk, g) in enumerate(zip(toks, gup)):
            if g in NOMSET and tk.lower() not in STOP and len(tk) >= 3:
                gold_heads += 1
                if i in base:
                    perc_hit += 1
                elif i in frame:
                    frame_rec += 1
                elif nm[i] >= tau:
                    soft_extra += 1
    over_frame = soft_extra / max(1, gold_heads)
    checks.append(("(2) graded soft-nominal adds < 1%% of gold heads over frame (frame-saturated)", over_frame < 0.01,
                   "soft adds %.3f%% (%d/%d), frame recall %.4f" %
                   (100 * over_frame, soft_extra, gold_heads, (perc_hit + frame_rec) / max(1, gold_heads))))

    # (3) reproduced from landed metrics: graded animacy beats twin, does NOT beat floor CI-sep
    import json
    mp = os.path.join(_REPO, "data/exp_graded_animacy_litbank_v1/metrics.json")
    if os.path.exists(mp):
        r = json.load(open(mp))["results"]
        ncs = r["contrasts"]["nc"]
        beats_twin = ncs["graded_minus_twin"]["sep"] is True
        not_over_floor = ncs["graded_minus_floor"]["sep"] is False
        checks.append(("(3) graded animacy > twin (CI-sep) BUT not > floor (subordinate cue)",
                       beats_twin and not_over_floor,
                       "nc: graded-twin=%+.4f(%s), graded-floor=%+.4f(%s)" %
                       (ncs["graded_minus_twin"]["delta"], "SEP" if beats_twin else "n.s.",
                        ncs["graded_minus_floor"]["delta"], "n.s." if not_over_floor else "SEP")))
    else:
        checks.append(("(3) graded-animacy metrics present", False, "run exp_graded_animacy_litbank_v1.py first"))

    # (4) no-regress: name->animate animacy does not change the live reader who-did-what/coref on a real doc
    from hdlab.situation_reader import SituationReader
    from hdlab.coref import load_name_gender
    gaz = load_name_gender()
    _orig = AL.lookup_animacy

    def _bf_animacy(word, pos_tag=None):
        w = word.lower().strip(".,\"'();:")
        if pos_tag == "PROPN" and w in gaz:
            return {"animacy": "animate", "category": "person", "agent_capable": True}
        return _orig(word, pos_tag)

    doc = sorted(glob.glob(os.path.join(LB, "*.conll")))[0]

    def _fp(sm):
        evs = getattr(sm, "events", []) or []
        return (len(evs), tuple(sorted((str(getattr(e, "lemma", "")), str(getattr(e, "agent", "")),
                                        str(getattr(e, "patient", ""))) for e in evs)),
                round(float(getattr(sm, "coref_acc", 0.0) or 0.0), 6), len(getattr(sm, "entities", []) or []))
    r0 = SituationReader(gaz=gaz)
    fp0 = _fp(r0.read(doc))
    # patch EVERYWHERE lookup_animacy is imported (module attr + the consumers that did `from ... import`)
    import hdlab.graded_role_assigner as GRA
    import hdlab.predicate_argument_frontend as PAF
    import hdlab.thematic_role_labeler as TRL
    patched = [AL]
    for m in (GRA, PAF, TRL):
        if getattr(m, "lookup_animacy", None) is _orig:
            patched.append(m)
    for m in patched:
        m.lookup_animacy = _bf_animacy
    try:
        r1 = SituationReader(gaz=gaz)
        fp1 = _fp(r1.read(doc))
    finally:
        for m in patched:
            m.lookup_animacy = _orig
    checks.append(("(4) brain-foundational name->animate animacy: NO regression on live who-did-what/coref",
                   fp0 == fp1, "identical" if fp0 == fp1 else "DIFF %r != %r" % (fp0, fp1)))

    npass = 0
    print("=" * 78)
    for name, ok, detail in checks:
        print("  [%s] %s -- %s" % ("PASS" if ok else "FAIL", name, detail))
        npass += int(ok)
    print("%d/%d checks passed" % (npass, len(checks)))
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
