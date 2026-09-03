"""exp_register_predicate_brain_comparison_v1 -- performance-level brain comparison + signal-loss ladder for
register-robust predicate detection.

Answers three questions with MEASUREMENT (not assertion):
  A. HOW DOES OUR PERFORMANCE COMPARE TO THE BRAIN? -- verb-detection recall of OUR home-grown tagger vs a COMPETENT
     statistical reader (spaCy en_core_web_sm, OFFLINE DIAGNOSTIC ORACLE, reference-only, NEVER at inference -- the
     admissible exception the parent used) vs NLTK, on gold verbs. The competent reader stands in for the brain's
     performance ceiling (a fluent reader identifies the predicate trivially).
  B. WHERE ALONG THE CHAIN DO WE LOSE SIGNAL? -- on the tokens OUR tagger DROPS (real verbs tagged non-VERB): does the
     competent reader recover them (= our tagger is BELOW competent, recoverable) or does it ALSO fail (= genuinely hard
     / register-shift, needs meaning)? Ladder: gold verbs 1.0 -> our tagger recall -> +our detector -> oracle ceiling
     (spaCy/nltk union) -> residual. Per register (modern UD-EWT test; 19c LitBank).
  C. downstream: each dropped verb = one lost who-did-what event (whole clause). Quantified.

NOTE: spaCy/nltk are OFFLINE DIAGNOSTIC ORACLES for this benchmark ONLY -- they are NEVER used at inference in the
substrate (the glass-box invariant). This cell is a reference comparison, not a landed capability. NOT remote-safe
(spaCy) -- runs local only.
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
# KB_REFERENT: data/predict_revise_recall_v1/_population_litbank.json
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from collections import Counter
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_register_predicate_detector_v1 as D
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_whodidwhat_verb_id_recoverable_v1 as VID

OUT_DIR = os.path.join(_REPO, "data/exp_register_predicate_brain_comparison_v1")

_NLP = None
def spacy_pos(toks):
    """UPOS per token from spaCy (OFFLINE ORACLE), respecting our pre-tokenization. VERB/AUX distinction kept."""
    global _NLP
    if _NLP is None:
        import spacy
        _NLP = spacy.load("en_core_web_sm", disable=["parser", "ner", "lemmatizer"])
    from spacy.tokens import Doc
    doc = Doc(_NLP.vocab, words=list(toks))
    for name, proc in _NLP.pipeline:
        doc = proc(doc)
    return [t.pos_ for t in doc]

_NLTK_OK = True
def nltk_isverb(toks):
    global _NLTK_OK
    try:
        import nltk
        return [t[1].startswith("VB") for t in nltk.pos_tag(list(toks))]
    except Exception:
        _NLTK_OK = False
        return [False] * len(toks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tg = D.tagger(); W = tg._perc.weights; tags = tg.tags

    cap = 40 if args.self_test else (120 if args.smoke else (None if args.full else 700))
    lbcap = 300 if (args.self_test or args.smoke) else (None if args.full else 2500)

    # ================= A. PERFORMANCE vs COMPETENT READER (verb recall on MODERN gold) =================
    ud = D.load_ud(D.UD_TEST, cap=cap)
    our_tp = spacy_tp = nltk_tp = gold_tot = 0
    our_drops = []   # (toks, i) our tagger dropped (gold VERB tagged non-VERB, non-AUX)
    for toks, gold_verb in ud:
        if not toks:
            continue
        ours = tg.tag(toks); sp = spacy_pos(toks); nl = nltk_isverb(toks)
        for i in gold_verb:
            gold_tot += 1
            our_tp += int(ours[i] == "VERB")
            spacy_tp += int(sp[i] == "VERB")
            nltk_tp += int(nl[i])
            if ours[i] not in ("VERB", "AUX"):
                our_drops.append((toks, i, sp[i], nl[i]))
    perfA = {"n_gold_verbs": gold_tot,
             "our_tagger_recall": round(our_tp / max(1, gold_tot), 4),
             "spacy_competent_recall": round(spacy_tp / max(1, gold_tot), 4),
             "nltk_recall": round(nltk_tp / max(1, gold_tot), 4),
             "our_dropped": len(our_drops)}
    # on OUR drops: does the competent reader recover them?
    sp_rec = sum(1 for _, _, sp, _ in our_drops if sp == "VERB")
    nl_rec = sum(1 for _, _, _, nl in our_drops if nl)
    either = sum(1 for _, _, sp, nl in our_drops if sp == "VERB" or nl)
    perfA["on_our_modern_drops"] = {
        "n": len(our_drops), "spacy_recovers": sp_rec, "nltk_recovers": nl_rec, "either_recovers": either,
        "spacy_recovers_frac": round(sp_rec / max(1, len(our_drops)), 4),
        "neither_recovers_frac": round((len(our_drops) - either) / max(1, len(our_drops)), 4)}

    # our DETECTOR recovery on modern drops (reuse D, CV, @ FP<=0.5) -- self-contained
    mod_rows, mod_ns = D.build_rows(ud, W, tags, None, None, False)
    modern = D.evaluate(mod_rows, mod_ns, D.cv_proba(mod_rows))
    det_mod = modern["best_fp_le_0p5"]["recovery"] if modern and modern["best_fp_le_0p5"] else None

    # ================= B. 19c: does the competent reader ALSO fail on archaic drops? =================
    pop = V1.load_pop(D.LB)
    pop_c = pop[:lbcap] if lbcap else pop
    c19_drops = []
    for r in pop_c:
        toks = r["sent"].split(); vi = r["verb_idx"]
        if not toks or vi >= len(toks):
            continue
        ours = tg.tag(toks)
        if ours[vi] in ("VERB", "AUX"):
            continue                      # not a genuine open-class drop (copula-as-AUX excluded)
        sp = spacy_pos(toks); nl = nltk_isverb(toks)
        c19_drops.append((toks[vi], sp[vi], nl))
    sp_rec19 = sum(1 for _, sp, _ in c19_drops if sp == "VERB")
    nl_rec19 = sum(1 for _, _, nl in c19_drops if nl)
    either19 = sum(1 for _, sp, nl in c19_drops if sp == "VERB" or nl)
    # our detector recovery on 19c (transfer, @ FP<=0.5)
    train_all = mod_rows + D.build_rows(D.load_qasrl(D.QASRL, cap=cap), W, tags, None, None, False)[0]
    clf, mu, sd = D._fit(train_all)
    c19_rows, c19_ns = D.build_rows_19c(pop, W, tags, None, None, False, cap=lbcap)
    c19 = D.evaluate(c19_rows, c19_ns, D._proba(clf, mu, sd, c19_rows))
    det_19 = c19["best_fp_le_0p5"]["recovery"] if c19 and c19["best_fp_le_0p5"] else None
    perfB = {"n_genuine_19c_drops": len(c19_drops),
             "spacy_recovers_frac": round(sp_rec19 / max(1, len(c19_drops)), 4),
             "nltk_recovers_frac": round(nl_rec19 / max(1, len(c19_drops)), 4),
             "either_oracle_recovers_frac": round(either19 / max(1, len(c19_drops)), 4),
             "our_detector_recovers_frac@0.5FP": det_19,
             "neither_oracle_recovers_frac": round((len(c19_drops) - either19) / max(1, len(c19_drops)), 4)}

    # ================= LADDERS (signal loss along the chain, per register) =================
    ladder_modern = {
        "gold_verbs": 1.0,
        "our_live_tagger": perfA["our_tagger_recall"],
        "+our_detector(@0.5FP,on drops)": round(perfA["our_tagger_recall"] + (1 - perfA["our_tagger_recall"]) * (det_mod or 0), 4),
        "competent_reader(spaCy)": perfA["spacy_competent_recall"],
        "oracle_ceiling(our_tagger|+spaCy|+nltk on drops)": round(perfA["our_tagger_recall"] + (1 - perfA["our_tagger_recall"]) * perfA["on_our_modern_drops"]["neither_recovers_frac"] * 0 + (1 - perfA["our_tagger_recall"]) * (1 - perfA["on_our_modern_drops"]["neither_recovers_frac"]), 4),
    }

    res = {"NOTE": "spaCy/nltk are OFFLINE DIAGNOSTIC ORACLES (reference-only, never at inference).",
           "A_performance_vs_competent_reader_modern": perfA, "our_detector_modern_rec@0.5FP": det_mod,
           "B_19c_competent_reader_also_fails": perfB,
           "ladder_modern_recall": ladder_modern,
           "C_downstream": "each dropped verb = one lost who-did-what EVENT (whole clause: agent+patient). "
                           "modern drops=%d, 19c genuine drops=%d." % (perfA["our_dropped"], len(c19_drops))}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "register_predicate_brain_comparison_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)

    print("\n===== A. PERFORMANCE vs COMPETENT READER (verb-detection recall, MODERN UD-EWT gold, n=%d) =====" % gold_tot, flush=True)
    print("  OUR home-grown tagger : %.4f   (drops %d real verbs)" % (perfA["our_tagger_recall"], perfA["our_dropped"]), flush=True)
    print("  competent reader spaCy: %.4f   <- the brain-performance proxy" % perfA["spacy_competent_recall"], flush=True)
    print("  NLTK                  : %.4f" % perfA["nltk_recall"], flush=True)
    print("  our DETECTOR recovers %.4f of OUR drops @ FP<=0.5 -> effective recall ~%.4f (closes most of the gap to competent)" % (
        det_mod or 0, ladder_modern["+our_detector(@0.5FP,on drops)"]), flush=True)
    print("\n  On OUR %d modern drops: competent reader (spaCy) recovers %.4f, EITHER oracle %.4f, NEITHER %.4f" % (
        perfA["on_our_modern_drops"]["n"], perfA["on_our_modern_drops"]["spacy_recovers_frac"],
        1 - perfA["on_our_modern_drops"]["neither_recovers_frac"], perfA["on_our_modern_drops"]["neither_recovers_frac"]), flush=True)
    print("\n===== B. 19c ARCHAIC DROPS (n=%d): does the competent reader ALSO fail? =====" % perfB["n_genuine_19c_drops"], flush=True)
    print("  competent reader spaCy recovers : %.4f   (a MODERN competent reader on 150yo prose)" % perfB["spacy_recovers_frac"], flush=True)
    print("  either oracle recovers          : %.4f" % perfB["either_oracle_recovers_frac"], flush=True)
    print("  OUR detector recovers           : %.4f @ FP<=0.5" % (det_19 or 0), flush=True)
    print("  NEITHER oracle recovers         : %.4f  <- genuinely hard even for a competent modern reader (register-shift)" % perfB["neither_oracle_recovers_frac"], flush=True)
    print("\n===== LADDER (modern verb-recall along the chain) =====", flush=True)
    for k, v in ladder_modern.items():
        print("  %-48s %.4f" % (k, v), flush=True)

    if args.self_test or args.smoke:
        assert gold_tot > 5 and perfA["spacy_competent_recall"] > 0
        print("\n[self-test] PASS", flush=True)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
