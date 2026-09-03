"""exp_register_predicate_crf_tagger_v1 -- the EXACT axis-1 architecture fix: a LIKELIHOOD-trained linear-chain CRF
tagger, whose forward-backward marginals are CALIBRATED probabilities BY CONSTRUCTION (Lafferty, McCallum & Pereira
2001) -- vs our max-margin averaged perceptron whose exponentiated potentials SATURATE (measured: 96% of tokens
P(VERB)<0.01, the textbook CRF-vs-margin signature).

Same feature templates as hdlab/pos_tagger.pos_features (word + affix + shape + prev/next-word context) and the same
UD-EWT training data -- the ONLY difference is the training OBJECTIVE (conditional log-likelihood vs max-margin). This
isolates whether the divergence the brain-mechanism drill named (graded-probabilistic vs max-margin-discriminative) is
the cause of the frozen/saturated category signal, and whether fixing it upstream recovers dropped verbs better.

Measures:
  1. UPSTREAM TAGGER FIX: CRF argmax verb-recall vs the perceptron's (does the likelihood objective drop FEWER verbs?).
  2. CALIBRATION: CRF posterior P(VERB) saturation vs the perceptron's forward-backward posterior.
  3. RECOVERY: CRF calibrated posterior (log-odds) as the detector's category cue -> recovery of dropped verbs
     (modern-CV + 19c-transfer) vs R0 (perceptron max-margin margin) and R3 (perceptron saturated posterior, log-odds).

Glass-box (crfsuite = a linear-chain CRF, inspectable weights; NOT an LLM). CPU. ASCII. own dir.
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
# KB_REFERENT: data/predict_revise_recall_v1/_population_litbank.json
# KB_REFERENT: data/benchmark_trap_check/qasrl/qasrl-v2/orig/dev.jsonl.gz
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, pickle, sys, time
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_register_predicate_detector_v1 as D
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_whodidwhat_verb_id_recoverable_v1 as VID

OUT_DIR = os.path.join(_REPO, "data/exp_register_predicate_crf_tagger_v1")
MODEL_PKL = os.path.join(OUT_DIR, "crf_tagger.pkl")


def crf_token_feats(toks, i):
    """Per-token feature dict for crfsuite -- mirrors hdlab.pos_tagger.pos_features content (crfsuite learns the
    transition features itself). Same information as the perceptron; different training objective."""
    w = toks[i]; wl = w.lower(); L = len(wl)
    f = {"bias": 1.0, "w": wl}
    for k in (1, 2, 3, 4):
        if L >= k:
            f["suf%d" % k] = wl[-k:]; f["pre%d" % k] = wl[:k]
    if w[:1].isupper(): f["cap"] = True
    if any(c.isdigit() for c in w): f["hasdig"] = True
    if "-" in w: f["hyph"] = True
    f["pw"] = toks[i - 1].lower() if i > 0 else "<BOS>"
    f["nw"] = toks[i + 1].lower() if i + 1 < len(toks) else "<EOS>"
    return f


def sent_feats(toks):
    return [crf_token_feats(toks, i) for i in range(len(toks))]


def load_ud_tagged(path, cap=None):
    """[(tokens, upos_list)] for CRF training (gold UPOS)."""
    sents = []; cur = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("#"):
            continue
        if not line.strip():
            if cur:
                sents.append(([c[1] for c in cur], [c[3] for c in cur])); cur = []
            continue
        c = line.split("\t")
        if "-" in c[0] or "." in c[0]:
            continue
        cur.append(c)
    if cur:
        sents.append(([c[1] for c in cur], [c[3] for c in cur]))
    return sents[:cap] if cap else sents


def train_or_load_crf(train_cap, force=False):
    import sklearn_crfsuite
    if os.path.exists(MODEL_PKL) and not force:
        with open(MODEL_PKL, "rb") as f:
            return pickle.load(f)
    train = load_ud_tagged(os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu"), cap=train_cap)
    X = [sent_feats(t) for t, _ in train]; y = [u for _, u in train]
    crf = sklearn_crfsuite.CRF(algorithm="lbfgs", c1=0.1, c2=0.1, max_iterations=80,
                               all_possible_transitions=True)
    crf.fit(X, y)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(MODEL_PKL, "wb") as f:
        pickle.dump(crf, f)
    return crf


class CRFPost:
    """Cache CRF argmax tags + P(VERB) marginals per sentence (crfsuite predict / predict_marginals)."""
    def __init__(self, crf):
        self.crf = crf; self._cache = {}
    def _run(self, toks):
        key = tuple(toks)
        if key not in self._cache:
            X = [sent_feats(list(toks))]
            tags = self.crf.predict(X)[0]
            marg = self.crf.predict_marginals(X)[0]
            self._cache[key] = (tags, [m.get("VERB", 0.0) for m in marg])
        return self._cache[key]
    def tag(self, toks):
        return self._run(toks)[0]
    def vpost(self, toks):
        return self._run(toks)[1]


def _logit(p):
    p = min(max(float(p), 1e-6), 1 - 1e-6)
    return float(np.log(p / (1 - p)))


def _cat(base, vpost_i, arm):
    if arm == "CRF_POST":
        return [_logit(vpost_i)]
    return [base[0], _logit(vpost_i)]              # CRF_BOTH / CRF_POST_PARSE: perceptron margin + CRF posterior


def build_rows_crf(sents, crfp, arm, Wp=None, parse_fn=None):
    """arm: CRF_POST=logit(CRF P(VERB)); CRF_BOTH=+perceptron margin; CRF_POST_PARSE=+joint parse-coherence (a)x(c)."""
    tg = D.tagger(); W = tg._perc.weights; tags = tg.tags
    rows = []; nsent = 0
    for toks, gold_verb in sents:
        if not toks:
            continue
        pos = tg.tag(toks)                       # the LIVE (perceptron) tagger defines the DROPS (deployed floor)
        vpost = crfp.vpost(toks)
        dropped = set(i for i in gold_verb if pos[i] not in ("VERB", "AUX"))
        for i in range(len(toks)):
            if pos[i] in ("VERB", "AUX") or not VID.has_verb_reading(toks[i]):
                continue
            base = D.feats_parsefree(toks, pos, i, W, tags)  # [margin, frame, subj, obj, morph, verbless, relpos]
            fv = _cat(base, vpost[i], arm) + base[1:]
            if arm == "CRF_POST_PARSE":
                fv = fv + D.parse_signals(toks, pos, i, Wp, parse_fn)
            rows.append((nsent, i, fv, 1 if i in dropped else 0))
        nsent += 1
    return rows, nsent


def build_rows_19c_crf(pop, crfp, arm, cap=None, Wp=None, parse_fn=None):
    tg = D.tagger(); W = tg._perc.weights; tags = tg.tags
    rows = []; nsent = 0
    pop = pop[:cap] if cap else pop
    for r in pop:
        toks = r["sent"].split(); vi = r["verb_idx"]
        if not toks or vi >= len(toks):
            continue
        pos = tg.tag(toks); vpost = crfp.vpost(toks)
        gv = {vi} if (pos[vi] not in ("VERB", "AUX")) else set()
        for i in range(len(toks)):
            if pos[i] in ("VERB", "AUX") or not VID.has_verb_reading(toks[i]):
                continue
            base = D.feats_parsefree(toks, pos, i, W, tags)
            fv = _cat(base, vpost[i], arm) + base[1:]
            if arm == "CRF_POST_PARSE":
                fv = fv + D.parse_signals(toks, pos, i, Wp, parse_fn)
            rows.append((nsent, i, fv, 1 if i in gv else 0))
        nsent += 1
    return rows, nsent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--retrain", action="store_true")
    ap.add_argument("--with-parse", action="store_true", dest="with_parse")
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    Wp = None; parse_fn = None
    if args.with_parse:
        from hdlab.arceager_parser import load_model, parse_with_conf, MODEL_PATH
        Wp = load_model(MODEL_PATH); parse_fn = parse_with_conf

    train_cap = 400 if (args.self_test or args.smoke) else (None if args.full else 4000)
    cap = 60 if args.self_test else (120 if args.smoke else (None if args.full else 700))
    qcap = 60 if args.self_test else (120 if args.smoke else (1500 if args.full else 1200))
    lbcap = 300 if (args.self_test or args.smoke) else (None if args.full else 2500)

    print("training/loading CRF (train_cap=%s) ..." % train_cap, flush=True)
    crf = train_or_load_crf(train_cap, force=args.retrain); crfp = CRFPost(crf)
    tg = D.tagger()

    # ---- 1+2. UPSTREAM verb-recall + calibration on UD-EWT test ----
    ud_tagged = load_ud_tagged(os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu"), cap=cap)
    perc_tp = crf_tp = gold_tot = 0
    crf_post_pos = []; crf_post_neg = []
    for toks, upos in ud_tagged:
        pp = tg.tag(toks); ct = crfp.tag(toks); vpost = crfp.vpost(toks)
        for i, g in enumerate(upos):
            if g == "VERB":
                gold_tot += 1
                perc_tp += int(pp[i] == "VERB"); crf_tp += int(ct[i] == "VERB")
                crf_post_pos.append(vpost[i])
            else:
                crf_post_neg.append(vpost[i])
    upstream = {"n_gold_verbs": gold_tot,
                "perceptron_verb_recall": round(perc_tp / max(1, gold_tot), 4),
                "crf_verb_recall": round(crf_tp / max(1, gold_tot), 4),
                "crf_post_mean_on_true_verbs": round(float(np.mean(crf_post_pos)), 4),
                "crf_post_mean_on_nonverbs": round(float(np.mean(crf_post_neg)), 4),
                "crf_post_saturation_frac_lt_0.01": round(float(np.mean(np.array(crf_post_pos + crf_post_neg) < 0.01)), 4)}

    # ---- 3. RECOVERY: CRF calibrated posterior as the category cue ----
    ud = D.load_ud(D.UD_TEST, cap=cap)
    qasrl = D.load_qasrl(D.QASRL, cap=qcap)
    pop = V1.load_pop(D.LB)
    out_arms = {}
    arms = ["CRF_POST", "CRF_BOTH"] + (["CRF_POST_PARSE"] if args.with_parse else [])
    for arm in arms:
        mod_rows, mod_ns = build_rows_crf(ud, crfp, arm, Wp=Wp, parse_fn=parse_fn)
        q_rows, _ = build_rows_crf(qasrl, crfp, arm, Wp=Wp, parse_fn=parse_fn)
        modern = D.evaluate(mod_rows, mod_ns, D.cv_proba(mod_rows))
        clf, mu, sd = D._fit(mod_rows + q_rows)
        c19_rows, c19_ns = build_rows_19c_crf(pop, crfp, arm, cap=lbcap, Wp=Wp, parse_fn=parse_fn)
        c19 = D.evaluate(c19_rows, c19_ns, D._proba(clf, mu, sd, c19_rows))
        def pk(r):
            b = r["best_fp_le_0p5"]; bt = r["bootstrap_delta_vs_twin"]
            return {"rec@0.5FP": b["recovery"] if b else None, "fp": b["false_verbs_per_sent"] if b else None,
                    "sep": (bt["ci"][0] > 0) if bt else None, "n_pos": r["n_positives"]}
        out_arms[arm] = {"modern": pk(modern), "c19_transfer": pk(c19)}

    res = {"upstream_tagger_fix": upstream, "recovery_arms": out_arms,
           "baselines_perceptron": {"R0_frozen_margin_c19": 0.5818, "R3_perceptron_posterior_logit_c19": 0.8182,
                                    "R3_both_c19": 0.80, "R0_modern": 0.9655}}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "register_predicate_crf_tagger_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)

    print("\n===== CRF TAGGER (likelihood-trained) -- the EXACT axis-1 architecture fix =====", flush=True)
    print("  1. UPSTREAM verb-recall (UD-EWT test, n=%d):  perceptron %.4f  vs  CRF %.4f" % (
        gold_tot, upstream["perceptron_verb_recall"], upstream["crf_verb_recall"]), flush=True)
    print("  2. CALIBRATION: CRF P(VERB) mean on true-verbs=%.4f on non-verbs=%.4f  saturation(frac<0.01)=%.4f"
          "  (perceptron posterior was 96%% saturated)" % (
        upstream["crf_post_mean_on_true_verbs"], upstream["crf_post_mean_on_nonverbs"], upstream["crf_post_saturation_frac_lt_0.01"]), flush=True)
    print("  3. RECOVERY of dropped verbs @ FP<=0.5 (CRF calibrated posterior as category cue):", flush=True)
    for arm, r in out_arms.items():
        print("     %-9s MODERN rec=%.4f sep=%-5s | 19c-TRANSFER rec=%.4f sep=%-5s" % (
            arm, r["modern"]["rec@0.5FP"] or 0, r["modern"]["sep"], r["c19_transfer"]["rec@0.5FP"] or 0, r["c19_transfer"]["sep"]), flush=True)
    print("  vs perceptron baselines: R0-frozen 19c=0.582, R3-posterior 19c=0.818, modern R0=0.966", flush=True)

    if args.self_test or args.smoke:
        assert out_arms["CRF_POST"]["c19_transfer"]["rec@0.5FP"] is not None
        print("\n[self-test] PASS", flush=True)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
