"""Landing witness for the affect-path NLTK-reroute + skip-valence (owner-DONE
route_the_redundant_nltk_perceptron_tagger_through_the_fast_hdlab_tagger, Q111 landing 2026-09-05). The full
mechanism was reverified by test_affect_reroute_hdlab_tagger.py (6/6 PRE-land; POST-land its C4 becomes a
stale NLTK-only tokenizer control that now measures the expected ~9% inert hdlab-vs-NLTK tagger divergence --
the SOLVED anticipated "5/5 post-land"). This asserts the LANDED reader is byte-identical + NLTK-free. ASCII.

  W1 NLTK-FREE: with nltk.pos_tag / nltk.word_tokenize disabled, a read's affect path completes (no NLTK call).
  W2 VALENCED BYTE-IDENTITY: the landed hdlab-rerouted _assign_affect vs the NLTK reference over the reader's
     actual affect calls -> 0 valenced (HARM/HELP) flips (the inert NA<->None provenance bit may differ).
  W3 SKIP-VALENCE byte-identity: score_item(need_valence=False) gives the same predicted_type/stage/ternary
     as need_valence=True (to_ternary is valence-independent).

Run: .venv/Scripts/python.exe verification/test_affect_reroute_landing.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.situation_reader as SR
from hdlab.situation_reader import SituationReader
from hdlab.context_grounded_valence import score_context_grounded_valence, score_item, to_ternary
import experiments.exp_situation_model_qa_v1 as SITQA


def _nltk_ref(patient, text):
    """The PRE-reroute affect behaviour: the NLTK entrypoint (kept for standalone use)."""
    if patient in (None, "?"):
        return None
    try:
        r = score_context_grounded_valence(patient, text)
    except ValueError:
        return None
    return to_ternary(r["predicted_type"]) if r["stage"] == "event" else None


def main():
    gaz = SITQA.load_given_gazetteer()
    docs = [d for d in SITQA.load_docs(None)[:4] if os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    paths = [os.path.join(SITQA.CONLL_DIR, d + ".conll") for d in docs]

    # W2 valenced byte-identity: landed (hdlab) vs the NLTK reference, over the reader's real affect calls
    landed = SR._assign_affect
    tally = {"calls": 0, "vflip": 0, "na_none": 0}

    def rec(patient, text):
        aH = landed(patient, text)          # landed hdlab reroute
        aN = _nltk_ref(patient, text)       # NLTK reference
        tally["calls"] += 1
        val = {"HARM", "HELP"}
        if aH != aN:
            tally["vflip" if ({aH, aN} & val) else "na_none"] += 1
        return aH

    SR._assign_affect = rec
    try:
        for p in paths:
            SituationReader(gaz=gaz).read(p)
    finally:
        SR._assign_affect = landed
    assert tally["calls"] > 0, "no affect calls scored"
    assert tally["vflip"] == 0, "VALENCED flip vs NLTK: %s" % tally
    print("W2 valenced byte-identity vs NLTK: 0 flips / %d calls (inert NA<->None divergences %d): PASS"
          % (tally["calls"], tally["na_none"]), flush=True)

    # W1 NLTK-free affect path
    import nltk
    op, wt = nltk.pos_tag, nltk.word_tokenize

    def _boom(*a, **k):
        raise RuntimeError("NLTK tagger called in the read path")
    nltk.pos_tag = _boom
    nltk.word_tokenize = _boom
    try:
        SituationReader(gaz=gaz).read(paths[0])          # completes without any NLTK call
    finally:
        nltk.pos_tag, nltk.word_tokenize = op, wt
    print("W1 NLTK-free affect path (nltk disabled, read completes): PASS", flush=True)

    # W3 skip-valence byte-identity of the ternary output
    toks = ["The", "thug", "battered", "the", "man", "."]
    tagger = SR._load_frontend()[0]
    pos = tagger.tag(toks)
    ti = 4
    rv = score_item(toks, pos, ti, "man", need_valence=True)
    rn = score_item(toks, pos, ti, "man", need_valence=False)
    assert rv["predicted_type"] == rn["predicted_type"] and rv["stage"] == rn["stage"], "skip-valence changed the type"
    assert to_ternary(rv["predicted_type"]) == to_ternary(rn["predicted_type"]), "skip-valence changed the ternary"
    assert rn["valence"] is None, "need_valence=False should not compute valence"
    print("W3 skip-valence byte-identical ternary (valence skipped): PASS", flush=True)
    print("\nALL WITNESSES PASS", flush=True)


if __name__ == "__main__":
    main()
