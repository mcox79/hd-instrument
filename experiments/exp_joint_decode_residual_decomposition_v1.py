"""exp_joint_decode_residual_decomposition_v1 -- WHERE the 19c dropped-verb signal lives: is the residual above the
CRF calibrated posterior (0.806) a STRUCTURE gap (closable by a better/register-robust parse -> the joint decode) or a
MEANING gap (needs the world-knowledge hub)? And does adding a parse-coherence cue flip any item?

This is the diagnostic that makes the joint-decode result (positive OR located-negative) rigorous. On the 19c genuine
verb-drop items (LitBank who-did-what pop, verb_idx tagged non-VERB by the live perceptron):

  1. ORACLE CEILING (spaCy = competent statistical reader, OFFLINE DIAGNOSTIC ONLY, never at inference -- the parent's
     admissible exception). Does a competent parser/tagger recover the drop? If YES for ~all, the drops are
     STRUCTURE/STATISTICS-recoverable (a parser-FIDELITY gap), NOT a meaning ceiling. This reconfirms the parent SS4b
     at item level and localizes our gap to OUR parser vs a competent one.
  2. PER-CUE SEPARATION on the drops vs the false candidates (non-verb gate-eligible tokens): CRF P(VERB) (the 0.806
     cue) vs force-VERB parse-coherence gain from (a) the LEXICAL modern parser, (b) the DELEXICALIZED register-robust
     parser. Does either coherence cue add separation the CRF posterior lacks? AUROC per cue + the incremental AUROC.
  3. IN-VOCAB vs OOV split of the drops (is register brittleness a vocabulary problem delex could fix, or word-order?).

Glass-box (perceptron + CRF + delex perceptron parser). spaCy = offline diagnostic oracle only. CPU. ASCII. own dir.
# KB_REFERENT: data/predict_revise_recall_v1/_population_litbank.json
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/exp_register_predicate_crf_tagger_v1/crf_tagger.pkl
# KB_REFERENT: data/frontend_assets_exp/arceager_dynamic_ud_ewt.npz
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_register_predicate_detector_v1 as D
import experiments.exp_register_predicate_crf_tagger_v1 as CRF
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_arceager_parser_operator_v1 as AEO
import experiments.exp_joint_decode_register_robust_tagger_parser_v1 as JD

OUT_DIR = os.path.join(_REPO, "data/exp_joint_decode_residual_decomposition_v1")


def _auroc(scores, labels):
    s = np.asarray(scores, float); y = np.asarray(labels, int)
    pos = s[y == 1]; neg = s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    # rank-based AUROC
    order = np.argsort(np.concatenate([pos, neg]))
    ranks = np.empty(len(order)); ranks[order] = np.arange(1, len(order) + 1)
    r_pos = ranks[:len(pos)].sum()
    return float((r_pos - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def ud_vocab(path):
    V = set()
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        c = line.split("\t")
        if "-" in c[0] or "." in c[0]:
            continue
        V.add(c[1].lower())
    return V


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--cap", type=int, default=2500)
    ap.add_argument("--no-spacy", action="store_true", dest="no_spacy")
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    cap = 300 if args.self_test else args.cap

    tg = D.tagger(); W = tg._perc.weights; tags = tg.tags
    crf = CRF.train_or_load_crf(400 if args.self_test else 4000); crfp = CRF.CRFPost(crf)
    W_lex = AEO.load_model(AEO.MODEL_PATH)
    Wp_delex = JD.train_or_load_delex(smoke=args.self_test)
    Vvocab = ud_vocab(os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu"))

    nlp = None
    if not args.no_spacy:
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print("[spacy] unavailable (%s) -- skipping oracle arm" % e, flush=True)

    pop = V1.load_pop(D.LB)[:cap]
    # collect per-candidate rows: (is_drop, crf_post, coh_lex, coh_delex), + per-DROP oracle recovery + oov
    crf_s = []; coh_lex = []; coh_delex = []; ylab = []
    drops = []  # dicts for the positive (dropped-verb) items
    for r in pop:
        toks = r["sent"].split(); vi = r["verb_idx"]
        if not toks or vi >= len(toks):
            continue
        pos = tg.tag(toks)
        gv = {vi} if (pos[vi] not in ("VERB", "AUX")) else set()
        vpost = crfp.vpost(toks)
        for i in range(len(toks)):
            if pos[i] in ("VERB", "AUX") or not CRF.VID.has_verb_reading(toks[i]):
                continue
            cs = CRF._logit(vpost[i])
            cl = D.parse_signals(toks, pos, i, W_lex, AEO.parse_with_conf)[0]      # local_gain (lexical)
            cd = D.parse_signals(toks, pos, i, Wp_delex, JD.parse_delex)[0]        # local_gain (delex)
            lab = 1 if i in gv else 0
            crf_s.append(cs); coh_lex.append(cl); coh_delex.append(cd); ylab.append(lab)
            if lab == 1:
                rec = {"word": toks[i], "oov": toks[i].lower() not in Vvocab, "crf_post": float(vpost[i])}
                if nlp is not None:
                    doc = nlp(" ".join(toks))
                    # align by token index (whitespace tokenization matches our split for these)
                    rec["spacy_verb"] = bool(i < len(doc) and doc[i].pos_ in ("VERB", "AUX"))
                drops.append(rec)

    y = np.array(ylab)
    res = {"n_candidates": len(y), "n_drops": int(y.sum()),
           "auroc_crf_post": round(_auroc(crf_s, y), 4),
           "auroc_coh_lex": round(_auroc(coh_lex, y), 4),
           "auroc_coh_delex": round(_auroc(coh_delex, y), 4),
           "auroc_crf_plus_cohlex": round(_auroc(np.array(crf_s) + np.array(coh_lex), y), 4),
           "auroc_crf_plus_cohdelex": round(_auroc(np.array(crf_s) + np.array(coh_delex), y), 4)}
    if drops:
        oov = sum(d["oov"] for d in drops)
        res["drops_oov_frac"] = round(oov / len(drops), 4)
        if nlp is not None:
            sv = sum(d.get("spacy_verb", False) for d in drops)
            res["oracle_spacy_recovers_frac"] = round(sv / len(drops), 4)
            iv = [d for d in drops if not d["oov"]]
            res["oracle_recovers_invocab_frac"] = round(sum(d.get("spacy_verb", False) for d in iv) / max(1, len(iv)), 4)
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "joint_decode_residual_decomposition_v1", "results": res}, f, indent=2)

    print("\n===== 19c dropped-verb residual decomposition (n_drops=%d, n_cand=%d) =====" % (res["n_drops"], res["n_candidates"]), flush=True)
    print("  AUROC (separating drops from false candidates):", flush=True)
    print("    CRF P(VERB) posterior (the 0.806 cue) : %.4f" % res["auroc_crf_post"], flush=True)
    print("    force-VERB coherence, LEXICAL parser  : %.4f  (CRF+cohLEX = %.4f)" % (res["auroc_coh_lex"], res["auroc_crf_plus_cohlex"]), flush=True)
    print("    force-VERB coherence, DELEX parser    : %.4f  (CRF+cohDELEX = %.4f)" % (res["auroc_coh_delex"], res["auroc_crf_plus_cohdelex"]), flush=True)
    if "drops_oov_frac" in res:
        print("  drops OOV-vs-UDtrain: %.3f" % res["drops_oov_frac"], flush=True)
    if "oracle_spacy_recovers_frac" in res:
        print("  ORACLE (spaCy competent reader) recovers %.3f of drops (%.3f of in-vocab drops) -> structure/statistics-recoverable"
              % (res["oracle_spacy_recovers_frac"], res["oracle_recovers_invocab_frac"]), flush=True)
    if args.self_test:
        assert res["n_drops"] > 0
        print("[self-test] PASS", flush=True)
    print("[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
