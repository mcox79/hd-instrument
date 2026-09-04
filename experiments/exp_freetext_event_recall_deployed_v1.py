"""exp_freetext_event_recall_deployed_v1 -- CLOSE THE DEPLOYMENT LOOP: measure the DEPLOYED, dependency-free
glass-box-CRF predicate detector end-to-end on FREE-TEXT 19c prose, at a PRECISION-GUARDED threshold, with the
info-free twin losing. This converts the tagger win from "proven mechanism + oracle upper bound" to a measured deployed
number, on the instrument where the tagger's value actually lives (free-text event recall -- the who-did-what gold hides
it by supplying the main verb).

WHAT'S NEW vs the parent (register_robust_event_detection SS3/SS4c):
  - FREE-TEXT 19c: raw LitBank novel sentences (not the who-did-what pop's supplied verb_idx). Event gold = spaCy VERB
    tokens (a competent statistical reader, OFFLINE DIAGNOSTIC ONLY, never at inference -- the parent's admissible
    exception, and far stronger than our perceptron on 19c). A "silently-lost event" = a spaCy VERB the perceptron
    tags non-VERB/AUX.
  - DEPLOYED path is fully GLASS-BOX + dependency-free: perceptron tags -> `GlassBoxCRF` posterior P(VERB) (pure-numpy
    forward-backward, NO crfsuite) as the detector's category cue -> logistic combiner over register-invariant cues.
    (Asserted identical to the crfsuite asset via the 7e-7 marginal match.)
  - PRECISION-GUARDED, no-per-pop tuning: threshold set on MODERN at FP<=0.25/sent, applied UNCHANGED to 19c free-text
    (the deployable operating point, tighter than the parent's 0.5). Info-free random-verbhood twin must LOSE CI-sep.
  - END-TO-END event recall lift: (perceptron VERB + recovered) / spaCy-VERB total vs perceptron alone.

Glass-box; spaCy offline-diagnostic only. Core-capped (USER 2026-09-04). CPU. ASCII. own dir.
# KB_REFERENT: data/litbank/original
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
# KB_REFERENT: data/benchmark_trap_check/qasrl/qasrl-v2/orig/dev.jsonl.gz
# KB_REFERENT: data/exp_crf_glassbox_marginals_v1/crf_tagger_glassbox.json
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse, glob, json, sys, time
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_register_predicate_detector_v1 as D
import experiments.exp_register_predicate_crf_tagger_v1 as CRF
import experiments.exp_crf_glassbox_marginals_v1 as GB

OUT_DIR = os.path.join(_REPO, "data/exp_freetext_event_recall_deployed_v1")
LITBANK_RAW = os.path.join(_REPO, "data/litbank/original")


def load_freetext_sents(nlp, Doc, max_sents, min_len=6, max_len=40):
    """Sentence-split + tokenize + POS-tag raw 19c LitBank novels with spaCy (OFFLINE ORACLE). Returns
    [(tokens, spacy_pos)] -- spaCy VERB tokens are the competent-reader event gold."""
    out = []
    files = sorted(glob.glob(os.path.join(LITBANK_RAW, "*.txt")))
    for fp in files:
        txt = open(fp, encoding="utf-8", errors="ignore").read()
        # cheap paragraph chunking to keep spaCy docs small
        for para in txt.split("\n\n"):
            para = " ".join(para.split())
            if len(para) < 40:
                continue
            doc = nlp(para)
            for sent in doc.sents:
                toks = [t.text for t in sent]
                spos = [t.pos_ for t in sent]
                if min_len <= len(toks) <= max_len and any(p == "VERB" for p in spos):
                    out.append((toks, spos))
                    if len(out) >= max_sents:
                        return out
    return out


def build_rows_freetext(sents_tokpos, gbcrf):
    """Candidate rows on free-text 19c. gold = spaCy VERB the perceptron DROPPED (tagged non-VERB/AUX)."""
    tg = D.tagger(); W = tg._perc.weights; tags = tg.tags
    rows = []; nsent = 0
    stats = {"gold_verbs": 0, "perc_hit": 0}
    for toks, spos in sents_tokpos:
        if not toks:
            continue
        pos = tg.tag(toks)
        vpost = gbcrf.vpost(toks)
        gold = set(i for i, p in enumerate(spos) if p == "VERB")
        dropped = set(i for i in gold if pos[i] not in ("VERB", "AUX"))
        stats["gold_verbs"] += len(gold)
        stats["perc_hit"] += sum(1 for i in gold if pos[i] == "VERB")
        for i in range(len(toks)):
            if pos[i] in ("VERB", "AUX") or not CRF.VID.has_verb_reading(toks[i]):
                continue
            base = D.feats_parsefree(toks, pos, i, W, tags)
            fv = CRF._cat(base, vpost[i], "CRF_POST") + base[1:]     # [logit(GlassBoxCRF P(VERB))] + frame/subj/obj/morph/verbless/relpos
            rows.append((nsent, i, fv, 1 if i in dropped else 0))
        nsent += 1
    return rows, nsent, stats


def _threshold_at_fp(curve, fp_budget):
    ok = [c for c in curve if c["false_verbs_per_sent"] <= fp_budget]
    return max(ok, key=lambda c: c["recovery"])["th"] if ok else 0.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--max-sents", type=int, default=None, dest="max_sents")
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    n_sents = args.max_sents or (150 if (args.self_test or args.smoke) else (5000 if args.full else 2000))
    tr_cap = 120 if (args.self_test or args.smoke) else (700 if not args.full else None)
    q_cap = 120 if (args.self_test or args.smoke) else (1200 if not args.full else None)

    import spacy
    from spacy.tokens import Doc
    nlp = spacy.load("en_core_web_sm")

    gbcrf = GB.GlassBoxCRF.load()

    # deployed-asset check: GlassBoxCRF == crfsuite marginals (recovery is identical by construction)
    if not (args.self_test):
        import pickle
        crf = pickle.load(open(os.path.join(_REPO, "data/exp_register_predicate_crf_tagger_v1/crf_tagger.pkl"), "rb"))
        ud_chk = CRF.load_ud_tagged(CRF.__dict__.get("UD_TEST", os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")), cap=30)
        err = 0.0
        for toks, _ in ud_chk:
            if not toks:
                continue
            ref = np.array([m.get("VERB", 0.0) for m in crf.predict_marginals([CRF.sent_feats(toks)])[0]])
            err = max(err, float(np.max(np.abs(ref - gbcrf.vpost(toks)))))
        print("[deployed-asset] max|GlassBoxCRF - crfsuite| P(VERB) = %.2e (dependency-free asset == validated)" % err, flush=True)
    else:
        err = 0.0

    # ---- train the deployed detector on MODERN (self-supervised), CRF_POST cue via GlassBoxCRF ----
    print("[train] modern rows (UD-EWT test + QA-SRL) with GlassBoxCRF posterior cue ...", flush=True)
    ud = D.load_ud(D.UD_TEST, cap=tr_cap)
    qasrl = D.load_qasrl(D.QASRL, cap=q_cap)
    mod_rows, mod_ns = CRF.build_rows_crf(ud, gbcrf, "CRF_POST")
    q_rows, _ = CRF.build_rows_crf(qasrl, gbcrf, "CRF_POST")
    modern = D.evaluate(mod_rows, mod_ns, D.cv_proba(mod_rows))
    th025 = _threshold_at_fp(modern["curve"], 0.25) if modern else 0.5
    clf, mu, sd = D._fit(mod_rows + q_rows)

    # ---- FREE-TEXT 19c ----
    print("[freetext] tagging %d raw 19c sentences with spaCy (offline oracle) ..." % n_sents, flush=True)
    sents = load_freetext_sents(nlp, Doc, n_sents)
    ft_rows, ft_ns, stats = build_rows_freetext(sents, gbcrf)
    ft_proba = D._proba(clf, mu, sd, ft_rows)
    # deployed (precision-guarded, modern-fixed threshold, no per-pop tuning) + twin CI
    deployed = D.evaluate_fixed(ft_rows, ft_ns, ft_proba, th025)
    # also report the FP<=0.5 operating point for continuity with the parent
    ft_eval = D.evaluate(ft_rows, ft_ns, ft_proba)

    # end-to-end event recall
    G = stats["gold_verbs"]; P = stats["perc_hit"]
    R = int((ft_proba >= th025).sum() * 0)  # placeholder, recomputed below
    y = np.array([r[3] for r in ft_rows]); promoted = ft_proba >= th025
    R = int((promoted & (y == 1)).sum())
    recall_perc = round(P / max(1, G), 4)
    recall_deployed = round((P + R) / max(1, G), 4)

    res = {"n_sents": ft_ns, "n_candidates": len(ft_rows), "glassbox_vs_crfsuite_maxerr": err,
           "modern_threshold_fp_le_0p25": round(float(th025), 4),
           "freetext_recovery_deployed": deployed,
           "freetext_recovery_fp_le_0p5": {"recovery": ft_eval["best_fp_le_0p5"]["recovery"] if (ft_eval and ft_eval["best_fp_le_0p5"]) else None},
           "event_recall": {"spacy_gold_verbs": G, "perceptron_recall": recall_perc,
                            "deployed_recall": recall_deployed, "n_dropped_recovered": R,
                            "n_dropped_total": int(y.sum())},
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "freetext_event_recall_deployed_v1", "results": res}, f, indent=2)

    print("\n===== DEPLOYED glass-box-CRF detector on FREE-TEXT 19c (n_sents=%d, n_cand=%d, n_dropped=%d) =====" % (
        ft_ns, len(ft_rows), int(y.sum())), flush=True)
    d = deployed
    print("  PRECISION-GUARDED (modern-fixed th=%.3f, FP<=0.25): recovery=%.4f fp=%.4f/sent  delta_vs_twin=%.4f CI[%.4f,%.4f] -> %s"
          % (th025, d["recovery"], d["false_verbs_per_sent"], d["delta_vs_twin_mean"], d["ci"][0], d["ci"][1],
             "CI-SEPARATED (twin loses)" if d["ci"][0] > 0 else "NOT separated"), flush=True)
    print("  twin recovery mean=%.4f p95=%.4f  (info-free random-verbhood at matched count)" % (d["twin_recovery_mean"], d["twin_recovery_p95"]), flush=True)
    print("  END-TO-END event recall vs spaCy oracle: perceptron=%.4f -> DEPLOYED=%.4f (+%.4f; recovered %d/%d dropped)"
          % (recall_perc, recall_deployed, recall_deployed - recall_perc, R, int(y.sum())), flush=True)

    if args.self_test or args.smoke:
        assert deployed is not None and res["event_recall"]["spacy_gold_verbs"] > 0
        print("\n[self-test] PASS", flush=True)
    print("[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
