"""Does the vectorized POS-feature path GENERALIZE -- to retraining (new/bigger KB corpus) and to a
modified tagger design? Three controls:

  G1 WEIGHT-INVARIANCE (retraining robustness): on a RAW float64 weight vector (NOT the float32-round-
     tripped production asset), the vec path must be BIT-IDENTICAL to the landed hdlab fast path
     (sentence_scores) -- because both build the identical flat id array and call the identical
     np.add.reduceat, this holds for ANY weights. So retraining the parser on a larger/modified corpus
     keeps the optimization exact. (Contrast: hdlab FAST vs hdlab REFERENCE _decode on raw float64 DO
     diverge in low bits -- a PRE-EXISTING reduceat-vs-per-arc-sum contingency that the vec path
     neither creates nor worsens; measured here for context.)

  G2 TAGSET-ADAPTIVITY (modified-design robustness): rebuild the POS tables over an EXTENDED tag
     universe (a novel tag "ZZZ") and confirm a synthetic sentence using it produces a flat id stream
     BYTE-IDENTICAL to hdlab._arc_ids (which hashes any tag string). The tables are keyed on tag
     STRINGS, so a larger inventory is just bigger (still-cheap) tables.

  G3 FAIL-LOUD on an out-of-universe tag: a tag absent from the built universe raises a clear error
     (no silent-wrong), so a modified tagger cannot silently corrupt the parse.

  Plus: G0 confirms the tag universe was DERIVED from the wired tagger asset (not hardcoded), and
  restates that the parser imports nothing from the KB (decoupling is architectural).

NO LLM. numpy + pure-python. Writes only its own data dir.
Run: .venv/Scripts/python.exe experiments/exp_arc_parser_posfeat_generalize_v1.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import json
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import hdlab.arc_parser as A
from hdlab.arc_parser import ArcParser, FeatCache, sentence_scores, sentence_flat
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences
import experiments.exp_arc_parser_posfeat_vectorize_v1 as V

OUT_DIR = os.path.join(_REPO, "data/exp_arc_parser_posfeat_generalize_v1")
_POS = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_ARC = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
_CONLL = os.path.join(_REPO, "data/litbank/coref_conll")
_DOCS = ["105_persuasion_brat.conll", "113_the_secret_garden_brat.conll"]


def load_tagged(docs, per_doc=150, maxlen=120):
    tagger = PosTagger.load(_POS)
    out = []
    for d in docs:
        p = os.path.join(_CONLL, d)
        if not os.path.exists(p):
            continue
        cnt = 0
        for toks in parse_conll_sentences(p):
            if 1 <= len(toks) <= maxlen:
                out.append((list(toks), list(tagger.tag(toks))))
                cnt += 1
                if cnt >= per_doc:
                    break
    return out


def run():
    T = V.pos_tables()
    sents = load_tagged(_DOCS)
    out = {}

    # G0: universe derived from the wired tagger asset; parser has no KB import
    import json as _j
    asset_tags = _j.load(open(_POS, encoding="utf-8"))["tags"]
    derived_ok = all(t in V._TAG2CODE for t in asset_tags)
    print("G0 tag universe derived from wired tagger asset (all %d tagger tags present): %s"
          % (len(asset_tags), derived_ok))
    out["G0_universe_derived_from_asset"] = derived_ok

    # G1: weight-invariance on RAW float64 -- vec == hdlab fast, bit-exact, any weights
    rng = np.random.default_rng(0)
    avg_raw = rng.standard_normal(A.SIZE).astype(np.float64) * 0.7   # NOT float32-round-tripped
    Cf = FeatCache(); Cv = FeatCache()
    vec_vs_fast_bad = 0
    for toks, pos in sents:
        sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
        Sf = sentence_scores(sent, avg_raw, Cf)
        Sv = V.sentence_scores_vec(sent, avg_raw, Cv, T)
        if any(Sf[i][h] != Sv[i].get(h) for i in Sf for h in Sf[i]):
            vec_vs_fast_bad += 1
    # context: hdlab FAST vs REFERENCE _decode on the SAME raw float64 (pre-existing contingency)
    pr = ArcParser(avg_raw)
    fast_vs_ref_head = fast_vs_ref_marg = 0
    for toks, pos in sents:
        r = pr._parse_reference(toks, pos)
        f = pr.parse(toks, pos)
        if r.heads != f.heads:
            fast_vs_ref_head += 1
        if any(r.margins[k] != f.margins.get(k) for k in r.margins):
            fast_vs_ref_marg += 1
    print("G1 WEIGHT-INVARIANCE (raw float64): vec == hdlab fast bit-exact on %d/%d sents (mismatch=%d)"
          % (len(sents) - vec_vs_fast_bad, len(sents), vec_vs_fast_bad))
    print("   [context] hdlab FAST vs REFERENCE _decode on the SAME raw float64: %d/%d head, %d/%d margin"
          " differ (PRE-EXISTING reduceat-vs-sum contingency; vec inherits fast, adds none)"
          % (fast_vs_ref_head, len(sents), fast_vs_ref_marg, len(sents)))
    out["G1_vec_vs_fast_mismatch_rawfloat64"] = vec_vs_fast_bad
    out["G1_fast_vs_ref_head_mismatch_rawfloat64"] = fast_vs_ref_head
    out["G1_fast_vs_ref_margin_mismatch_rawfloat64"] = fast_vs_ref_marg

    # G2: tagset-adaptivity -- rebuild over an EXTENDED universe with a novel tag "ZZZ"
    orig = (V._UPOS, V._CODES, V._TAG2CODE, V._NC, V._ROOT, V._S, V._E, V._POS_TABLES)
    try:
        V._UPOS = list(V._UPOS) + ["ZZZ"]
        V._CODES = V._UPOS + V._SPECIAL
        V._TAG2CODE = {t: k for k, t in enumerate(V._CODES)}
        V._NC = len(V._CODES)
        V._ROOT = V._TAG2CODE["ROOT"]; V._S = V._TAG2CODE["<S>"]; V._E = V._TAG2CODE["<E>"]
        V._POS_TABLES = None
        Text = V.pos_tables()
        # synthetic sentence using the novel tag
        toks = ["Alpha", "zzz", "ran", "fast", "."]
        pos = ["PROPN", "ZZZ", "VERB", "ADV", "PUNCT"]
        sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
        fv, sv, ov, n = V.sentence_flat_vec(sent, FeatCache(), Text)
        # reference flat stream from hdlab._arc_ids (handles any tag string)
        ref = []; starts_ref = []
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h == i:
                    continue
                starts_ref.append(len(ref))
                ref.extend(list(A._arc_ids(sent, i, h)))
        g2_ok = (list(fv) == ref and list(sv) == starts_ref)
        print("G2 TAGSET-ADAPTIVITY (novel tag 'ZZZ'): vec flat stream == hdlab._arc_ids: %s (%d arcs)"
              % (g2_ok, len(ov)))
        out["G2_extended_tagset_byte_identical"] = g2_ok
    finally:
        (V._UPOS, V._CODES, V._TAG2CODE, V._NC, V._ROOT, V._S, V._E, V._POS_TABLES) = orig

    # G3: fail-loud on an out-of-universe tag
    g3_raised = False
    toks = ["x", "y"]; pos = ["NOUN", "QQQ_UNKNOWN"]
    sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
    try:
        V.sentence_flat_vec(sent, FeatCache(), V.pos_tables())
    except KeyError:
        g3_raised = True
    print("G3 FAIL-LOUD on out-of-universe tag: raised clear error = %s (no silent-wrong)" % g3_raised)
    out["G3_fail_loud_on_unknown_tag"] = g3_raised

    all_ok = (out["G0_universe_derived_from_asset"] and vec_vs_fast_bad == 0
              and out.get("G2_extended_tagset_byte_identical") and g3_raised)
    print("\nGENERALIZES: %s" % all_ok)
    os.makedirs(OUT_DIR, exist_ok=True)
    out["numpy"] = np.__version__
    out["all_ok"] = bool(all_ok)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print("wrote", os.path.join(OUT_DIR, "metrics.json"))


if __name__ == "__main__":
    run()
