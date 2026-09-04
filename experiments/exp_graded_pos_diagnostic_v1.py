"""exp_graded_pos_diagnostic_v1 -- WHERE is the leverage for consuming the graded POS posterior?

The brief (consume_the_graded_pos_posterior_...) claims the PROPN<->NOUN confusion (28% of tagger errors)
propagates through referent_per_np's NP/entity/name detection and corrupts coref. An organ-map (Explore, this
session) says the OPPOSITE on disk: `_content_head_positions` puts NOUN and PROPN in the SAME `NOMINAL` set, so a
PROPN<->NOUN swap NEVER changes referent introduction; and `parse_litbank_conll` never reads UPOS, so coref/gender
are tag-independent. This cell REPRODUCES that first-hand and locates where the graded posterior COULD help:

  (A) NOMINAL-vs-non-nominal margin: gold content heads (NOUN/PROPN) the PERCEPTRON argmax tags NON-nominal are
      MISSED by _content_head_positions. How many? How many does the heuristic frame detector (capitalization/
      determiner-edge) already recover? How many would the calibrated CRF nominal-mass P(NOUN)+P(PROPN)>=tau
      recover ON TOP of frame? -> the coverage headroom for a graded-posterior consumer.
  (B) PROPN<->NOUN confusion -> ANIMACY: the ONE place NOUN/PROPN actually differ (animacy_lexicon: PROPN->empty
      overrides->"unk"; NOUN->WordNet). Count perceptron PROPN-vs-NOUN errors and whether lookup_animacy flips.
  (C) INTRODUCTION-INVARIANCE: flip every PROPN<->NOUN in the perceptron output on real LitBank docs, re-run the
      landed referent_per_np head set (base + frame), assert the opened-referent set is IDENTICAL -> confirms (or
      refutes) the brief's "opens the wrong referent / mis-clusters a name" mechanism.

Glass-box, CPU, NO LLM. Own dir. hdlab READ-only. ASCII.
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import argparse, glob, json, time
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger
from hdlab.crf_tagger import GlassBoxCRF
from hdlab.scene_segment import parse_conll_sentences
from hdlab.referent_per_np import (_content_head_positions, frame_heads, NOMINAL, STOP)
from hdlab.animacy_lexicon import lookup_animacy

OUT_DIR = os.path.join(_REPO, "data/exp_graded_pos_diagnostic_v1")
POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
LB_CORPUS = os.path.join(_REPO, "data/litbank/coref_conll")
NOMSET = frozenset(NOMINAL)  # {"NOUN","PROPN"}


def load_conllu(path, max_sents=None):
    """Yield (toks, gold_upos) from a CoNLL-U file (skip MWT/empty-node rows)."""
    out = []
    toks, ups = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if toks:
                    out.append((toks, ups)); toks, ups = [], []
                    if max_sents and len(out) >= max_sents:
                        return out
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if len(c) < 4 or "-" in c[0] or "." in c[0]:
                continue
            toks.append(c[1]); ups.append(c[3])
    if toks:
        out.append((toks, ups))
    return out


def is_head_candidate(tok):
    return tok.lower() not in STOP and len(tok) >= 3


def run(n_ud=1500, n_lb_docs=6, taus=(0.5, 0.7, 0.9), seed=20260904):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    perc = PosTagger.load(POS_ASSET)
    crf = GlassBoxCRF.load()
    res = {}

    # ---------- (A)+(B) on UD-EWT gold UPOS ----------
    ud = load_conllu(UD_TEST, max_sents=n_ud)
    # gold content head = gold nominal, non-stop, len>=3 (the organ's coverage rule, measured against gold tag)
    gold_heads = 0
    perc_hit = 0            # perceptron argmax nominal at a gold head
    perc_miss_frame = 0     # gold head perceptron missed, frame recovers
    perc_miss_softcrf = {tau: 0 for tau in taus}   # gold head perc missed AND frame missed, CRF-soft recovers
    perc_miss_unrec = {tau: 0 for tau in taus}     # gold head perc missed, frame missed, CRF-soft missed
    # PROPN<->NOUN confusion + animacy flips
    propn_as_noun = noun_as_propn = 0
    anim_flip = 0
    n_tok = 0
    # soft-nominal PRECISION: of tokens CRF-soft opens that argmax did NOT, how many are gold nominal?
    soft_new_total = {tau: 0 for tau in taus}
    soft_new_goldnom = {tau: 0 for tau in taus}

    for toks, gup in ud:
        n_tok += len(toks)
        pup = perc.tag(list(toks))
        M = crf.marginals(toks)   # (n,K)
        Li = crf.Li
        nom_mass = M[:, Li["NOUN"]] + M[:, Li["PROPN"]] if ("NOUN" in Li and "PROPN" in Li) else np.zeros(len(toks))
        base = set(_content_head_positions(toks, pup))
        frame = frame_heads(toks, pup, base)
        recov = base | frame
        for i, (tk, g, p) in enumerate(zip(toks, gup, pup)):
            # (B) confusion + animacy
            if p != g and {p, g} <= {"NOUN", "PROPN"}:
                if g == "PROPN":
                    propn_as_noun += 1
                else:
                    noun_as_propn += 1
                a_gold = lookup_animacy(tk, g); a_perc = lookup_animacy(tk, p)
                if (a_gold or {}).get("animacy") != (a_perc or {}).get("animacy"):
                    anim_flip += 1
            # (A) coverage at gold content heads
            if g in NOMSET and is_head_candidate(tk):
                gold_heads += 1
                if i in base:
                    perc_hit += 1
                elif i in frame:
                    perc_miss_frame += 1
                else:
                    for tau in taus:
                        if nom_mass[i] >= tau:
                            perc_miss_softcrf[tau] += 1
                        else:
                            perc_miss_unrec[tau] += 1
            # soft-nominal precision: a NEW head CRF-soft opens (not in perc recov set base|frame)
            if is_head_candidate(tk) and i not in recov:
                for tau in taus:
                    if nom_mass[i] >= tau:
                        soft_new_total[tau] += 1
                        if g in NOMSET:
                            soft_new_goldnom[tau] += 1

    res["A_coverage_gold_ud"] = {
        "n_sents": len(ud), "n_tok": n_tok, "gold_content_heads": gold_heads,
        "perc_argmax_hit": perc_hit,
        "perc_miss_recovered_by_frame": perc_miss_frame,
        "recall_perc_only": round(perc_hit / max(1, gold_heads), 4),
        "recall_perc_plus_frame": round((perc_hit + perc_miss_frame) / max(1, gold_heads), 4),
        "residual_missed_after_frame": gold_heads - perc_hit - perc_miss_frame,
        "crf_soft_recovers_on_top_of_frame": {str(t): perc_miss_softcrf[t] for t in taus},
        "still_unrecovered": {str(t): perc_miss_unrec[t] for t in taus},
        "recall_perc_frame_plus_softcrf": {
            str(t): round((perc_hit + perc_miss_frame + perc_miss_softcrf[t]) / max(1, gold_heads), 4) for t in taus},
        "soft_new_heads_total": {str(t): soft_new_total[t] for t in taus},
        "soft_new_heads_gold_nominal": {str(t): soft_new_goldnom[t] for t in taus},
        "soft_new_precision": {str(t): round(soft_new_goldnom[t] / max(1, soft_new_total[t]), 4) for t in taus},
    }
    res["B_propn_noun_confusion_ud"] = {
        "propn_tagged_noun": propn_as_noun, "noun_tagged_propn": noun_as_propn,
        "total_propn_noun_swaps": propn_as_noun + noun_as_propn,
        "of_which_flip_lookup_animacy": anim_flip,
        "note": "animacy flips are the ONLY channel PROPN<->NOUN changes a reader output (per organ-map)",
    }

    # ---------- (C) introduction-invariance on real LitBank docs ----------
    docs = sorted(glob.glob(os.path.join(LB_CORPUS, "*.conll")))[:n_lb_docs]
    tot_sents = 0; changed_sents = 0; tot_heads = 0; head_set_diffs = 0
    for d in docs:
        for toks in parse_conll_sentences(d):
            if not toks or len(toks) > 120:
                continue
            tot_sents += 1
            pup = perc.tag(list(toks))
            # flip every PROPN<->NOUN
            flip = ["NOUN" if u == "PROPN" else ("PROPN" if u == "NOUN" else u) for u in pup]
            b0 = set(_content_head_positions(toks, pup)); f0 = frame_heads(toks, pup, b0); h0 = b0 | f0
            b1 = set(_content_head_positions(toks, flip)); f1 = frame_heads(toks, flip, b1); h1 = b1 | f1
            tot_heads += len(h0)
            if h0 != h1:
                changed_sents += 1
                head_set_diffs += len(h0 ^ h1)
    res["C_introduction_invariance_litbank"] = {
        "n_docs": len(docs), "n_sents": tot_sents, "total_opened_heads": tot_heads,
        "sents_whose_head_set_CHANGED_under_propn_noun_flip": changed_sents,
        "total_head_membership_diffs": head_set_diffs,
        "verdict": ("INVARIANT (brief mechanism refuted for introduction)" if changed_sents == 0
                    else "NOT invariant -- %d sents change" % changed_sents),
    }

    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "graded_pos_diagnostic_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--ud", type=int, default=1500)
    ap.add_argument("--docs", type=int, default=6)
    a = ap.parse_args()
    if a.self_test or a.smoke:
        res = run(n_ud=120, n_lb_docs=2)
    else:
        res = run(n_ud=a.ud, n_lb_docs=a.docs)
    print(json.dumps(res, indent=2), flush=True)
    A = res["A_coverage_gold_ud"]; C = res["C_introduction_invariance_litbank"]
    print("\n=== SUMMARY ===", flush=True)
    print("A) gold content heads=%d | perc recall=%.4f | +frame=%.4f | residual missed=%d"
          % (A["gold_content_heads"], A["recall_perc_only"], A["recall_perc_plus_frame"],
             A["residual_missed_after_frame"]), flush=True)
    print("   CRF-soft recovers on top of frame: %s" % A["crf_soft_recovers_on_top_of_frame"], flush=True)
    print("   soft-new precision (gold-nominal / opened): %s" % A["soft_new_precision"], flush=True)
    print("B) PROPN<->NOUN swaps=%d | flip animacy=%d"
          % (res["B_propn_noun_confusion_ud"]["total_propn_noun_swaps"],
             res["B_propn_noun_confusion_ud"]["of_which_flip_lookup_animacy"]), flush=True)
    print("C) introduction under PROPN<->NOUN flip: %s" % C["verdict"], flush=True)
    if a.self_test or a.smoke:
        assert C["n_sents"] > 0 and A["gold_content_heads"] > 0
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
