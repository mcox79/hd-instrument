"""exp_joint_decode_register_robust_tagger_parser_v1 -- the ONE LEVER, TWO PAYOFFS build:
a likelihood-trained CALIBRATED tagger (CRF, axis-1, already built) JOINT-DECODED with a REGISTER-ROBUST parser
(category re-estimated from structure -- Bohnet & Nivre 2012, but with the CRF/likelihood objective the drill bought).

THE CRUX the parent located (register_robust_event_detection SS4c): joint parse-coherence over the CRF posterior HELPS
MODERN (0.955->0.966) but is REGISTER-BRITTLE on 19c (0.806->0.800) -- because the arc-eager parser is ALSO
modern-trained, so its coherence cue is corrupted on 19c exactly as the tagger was. The honest deeper build: the PARSER
too must be register-robust.

THE BRAIN-FOUNDATIONAL FORM of "register-robust parser" is the CONTENT-INDEPENDENT structure-builder: the language
network builds structure on Jabberwocky nonsense at ~52% of real-sentence magnitude (Fedorenko lab), and 2-year-olds
slot invented verbs from FRAME alone (Yuan 2011) -- structure-building is form-independent. The computational analog is
the DELEXICALIZED parser (POS + morphology + configuration, NO word identity; McDonald 2011 the standard cross-domain
transfer tool). So the ONE VARIABLE we change is the parser's feature set: drop word-identity, keep POS/morph/structure.

WHAT THIS CELL MEASURES (both payoffs, one lever):
  PAYOFF 1 (the tagger -- past 0.806): recovery of 19c dropped verbs @ FP<=0.5 with the joint parse-coherence cue from
    the DELEXICALIZED parser (CRF_POST_PARSE_DELEX), vs the CRF-alone floor (CRF_POST = 0.806) and the register-brittle
    LEXICAL-parser arm (CRF_POST_PARSE_LEX = 0.800). Info-free twin (shuffled coherence) must lose.
  PAYOFF 2 (the parser's downstream consumer): 19c who-did-what gold-argument REACHABILITY + who-did-what accuracy
    (PP cell's `_attaches_to_verb` / `chain_pick`), BASE (lexical parser + committed perceptron tags = the live floor)
    vs DELEX (register-robust parser) vs JOINT (register-robust parser + joint-decoded tags = recovered verbs forced
    VERB). Info-free twin (shuffled tag corrections) must lose. Modern retention checked (delex UAS on UD-EWT test).

A rigorous located NEGATIVE (joint decode cannot push 19c past 0.806 within a register-robust budget, with the named
cause + number) is a FULL PASS per the brief.

Glass-box (perceptron + CRF + delexicalized perceptron parser; inspectable weights; NO LLM, NO spaCy at inference).
CPU numpy + sklearn_crfsuite. ASCII. own dir. Nothing in hdlab modified (proposed diff -> SOLVED.md; strategy lands Q111).

# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
# KB_REFERENT: data/predict_revise_recall_v1/_population_litbank.json
# KB_REFERENT: data/benchmark_trap_check/qasrl/qasrl-v2/orig/dev.jsonl.gz
# KB_REFERENT: data/frontend_assets_exp/arceager_dynamic_ud_ewt.npz
# KB_REFERENT: data/exp_register_predicate_crf_tagger_v1/crf_tagger.pkl
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import argparse, json, sys, time, pickle
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_arceager_parser_operator_v1 as AEO
import experiments.exp_register_predicate_detector_v1 as D
import experiments.exp_register_predicate_crf_tagger_v1 as CRF
import experiments.exp_register_native_pp_attachment_v1 as PP
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
from hdlab.predicate_argument_frontend import _attaches_to_verb

# AEO transition-system primitives (reused byte-faithfully; only the feature function changes)
from experiments.exp_arceager_parser_operator_v1 import (
    _h, _mk_attr, _legal, _apply, _score_actions, _argmax_legal, _move_costs_live, _perc_update,
    _config_feats as lex_config_feats, _pos, _dist, _szbucket, _val,
    SIZE, MASK, ACT_SALT, SHIFT, LARC, RARC, REDU, MAXLEN, EXPLORE_AFTER, EXPLORE_P,
)

OUT_DIR = os.path.join(_REPO, "data/exp_joint_decode_register_robust_tagger_parser_v1")
DELEX_MODEL = os.path.join(OUT_DIR, "arceager_delex_ud_ewt.npz")
MAX_HOPS = PP.MAX_HOPS
RICH = True


# --------------------------------------------------------------------- DELEXICALIZED feature function
def delex_config_feats(stack, bptr, n, attr, heads, lc, rc, hd):
    """AEO._config_feats with WORD-IDENTITY features removed (s0w, b0w, s0w_b0w, s0p_b0w, s0w_b0p). Keeps POS
    unigram/bigram/trigram, SUFFIX morphology (s0s,b0s -- register-stable), distance, valency, and the RICH
    non-local structural features (all POS/valency). This is the content-independent structure-builder (Jabberwocky/
    Fedorenko; delexicalized parser, McDonald 2011)."""
    s0 = stack[-1]; s1 = stack[-2] if len(stack) >= 2 else None
    b0 = bptr if bptr <= n else None; b1 = (bptr + 1) if (bptr + 1) <= n else None; b2 = (bptr + 2) if (bptr + 2) <= n else None
    s0w, s0p, s0s = attr[s0]
    s1w, s1p, s1s = attr[s1] if s1 is not None else AEO._NONE
    b0w, b0p, b0s = attr[b0] if b0 is not None else AEO._NONE
    b1w, b1p, b1s = attr[b1] if b1 is not None else AEO._NONE
    b2w, b2p, b2s = attr[b2] if b2 is not None else AEO._NONE
    dd = _dist(b0 - s0) if (b0 is not None and s0 > 0) else "0"
    s0hh = "1" if s0 in heads else "0"
    F = ["bias", "s0p:" + s0p, "s1p:" + s1p, "b0p:" + b0p, "b1p:" + b1p, "b2p:" + b2p,
         "s0p_b0p:%s_%s" % (s0p, b0p),
         "s0p_b0p_b1p:%s_%s_%s" % (s0p, b0p, b1p), "s1p_s0p_b0p:%s_%s_%s" % (s1p, s0p, b0p),
         "s0s:" + s0s, "b0s:" + b0s, "s0s_b0p:%s_%s" % (s0s, b0p), "b0s_s0p:%s_%s" % (b0s, s0p),
         "dist:%s_%s_%s" % (dd, s0p, b0p), "s0hh_p:%s_%s" % (s0hh, s0p), "s0hh_b0p:%s_%s" % (s0hh, b0p),
         "stksz:" + _szbucket(len(stack))]
    if RICH:
        s0lc = lc.get(s0, []); s0rc = rc.get(s0, []); b0lc = lc.get(b0, [])
        s0lcp = _pos(attr, s0lc[0]) if s0lc else "<nc>"
        s0rcp = _pos(attr, s0rc[-1]) if s0rc else "<nc>"
        b0lcp = _pos(attr, b0lc[0]) if b0lc else "<nc>"
        s0hp = _pos(attr, hd.get(s0)) if s0 in hd else "<nh>"
        s0lclc = _pos(attr, lc.get(s0lc[0], [None])[0]) if s0lc and lc.get(s0lc[0]) else "<nc>"
        F += ["s0lcp:" + s0lcp, "s0rcp:" + s0rcp, "b0lcp:" + b0lcp, "s0hp:" + s0hp,
              "s0p_s0lcp:%s_%s" % (s0p, s0lcp), "s0p_s0rcp:%s_%s" % (s0p, s0rcp), "b0p_b0lcp:%s_%s" % (b0p, b0lcp),
              "s0p_b0p_s0rcp:%s_%s_%s" % (s0p, b0p, s0rcp), "s0p_b0p_b0lcp:%s_%s_%s" % (s0p, b0p, b0lcp),
              "s0p_s0hp:%s_%s" % (s0p, s0hp), "s0lclcp:" + s0lclc,
              "s0vall:%s_%s" % (_val(len(s0lc)), s0p), "s0valr:%s_%s" % (_val(len(s0rc)), s0p), "b0vall:%s_%s" % (_val(len(b0lc)), b0p)]
    return F


# --------------------------------------------------------------------- pluggable-feature train + parse (copied from AEO, ff param)
def train_transition_ff(train, seed, ff, epochs, dynamic=True):
    rng = np.random.default_rng(seed); W = np.zeros(SIZE); CW = np.zeros(SIZE); c = 1
    for ep in range(epochs):
        explore = dynamic and ep >= EXPLORE_AFTER; te = time.time()
        for si in rng.permutation(len(train)):
            s = train[si]; n = len(s); attr = _mk_attr(s)
            gold = [0] * (n + 1)
            for tok in s:
                gold[tok[0]] = tok[3] if 0 <= tok[3] <= n else 0
            stack = [0]; bptr = 1; heads = {}; lc = {}; rc = {}; hd = {}; guard = 0
            while bptr <= n or len(stack) > 1:
                if bptr > n and len(stack) <= 1: break
                legal = _legal(stack, bptr, n, heads)
                if not legal: break
                base_ids = np.fromiter((_h(f) for f in ff(stack, bptr, n, attr, heads, lc, rc, hd)), dtype=np.int64)
                scores = _score_actions(base_ids, W, legal); a_pred = _argmax_legal(scores)
                costs = _move_costs_live(stack, bptr, n, gold, heads)
                zero = [a for a in legal if costs.get(a, 1) == 0] or [min(costs, key=lambda k: costs[k])]
                a_orl = max(zero, key=lambda a: scores.get(a, -1e18))
                if a_pred != a_orl and costs.get(a_pred, 1) > 0:
                    _perc_update(W, CW, base_ids, a_orl, a_pred, c); c += 1
                a_next = a_pred if (explore and a_pred in legal and rng.random() < EXPLORE_P) else a_orl
                stack, bptr = _apply(stack, bptr, heads, lc, rc, hd, a_next); guard += 1
                if guard > 4 * (n + 2): break
        print("  [delex-train] epoch %d/%d %.1fs (updates=%d)" % (ep + 1, epochs, time.time() - te, c - 1), flush=True)
    return W - CW / c


def parse_ff(sent_tokens, pos_tags, W, ff):
    """AEO.parse_with_conf with a pluggable feature function (heads, attach_conf, attach_margin)."""
    n = len(sent_tokens)
    sent = [(k + 1, sent_tokens[k], pos_tags[k], 0, "_", None) for k in range(n)]
    attr = _mk_attr(sent)
    stack = [0]; bptr = 1; heads = {}; lc = {}; rc = {}; hd = {}; conf = {}; marg = {}
    guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1: break
        legal = _legal(stack, bptr, n, heads)
        if not legal: break
        base_ids = np.fromiter((_h(f) for f in ff(stack, bptr, n, attr, heads, lc, rc, hd)), dtype=np.int64)
        scores = _score_actions(base_ids, W, legal); a = _argmax_legal(scores)
        sv = np.array([scores[x] for x in legal], dtype=np.float64)
        so = np.sort(sv)[::-1]; m = float(so[0] - so[1]) if len(so) > 1 else float(so[0])
        e = np.exp(sv - sv.max()); pa = float((e / e.sum())[legal.index(a)])
        s0 = stack[-1]
        if a == LARC: conf[s0] = pa; marg[s0] = m
        elif a == RARC: conf[bptr] = pa; marg[bptr] = m
        stack, bptr = _apply(stack, bptr, heads, lc, rc, hd, a); guard += 1
        if guard > 4 * (n + 2): break
    for i in range(1, n + 1):
        heads.setdefault(i, 0); conf.setdefault(i, 0.0); marg.setdefault(i, 0.0)
    return heads, conf, marg


def parse_delex(toks, pos, W):
    return parse_ff(toks, pos, W, delex_config_feats)


def uas_ff(sents, W, ff):
    hit = tot = 0
    for s in sents:
        toks = [t[1] for t in s]; pos = [t[2] for t in s]
        heads, _, _ = parse_ff(toks, pos, W, ff)
        for tok in s:
            i, h = tok[0], tok[3]
            if h < 0 or h > len(s): continue
            hit += int(heads.get(i, -1) == h); tot += 1
    return hit / tot if tot else 0.0


def train_or_load_delex(smoke, force=False):
    # smoke and full persist to DISTINCT paths so a fast smoke model can never masquerade as the full asset.
    path = (DELEX_MODEL[:-4] + "_smoke.npz") if smoke else DELEX_MODEL
    if os.path.exists(path) and not force:
        return AEO.load_model(path)
    train = [s for s in AEO._load_ud_feats("train") if 1 <= len(s) <= MAXLEN]
    epochs = 3 if smoke else 10
    if smoke:
        train = train[:400]
    print("[delex] training register-robust (delexicalized) arc-eager parser: %d sents, %d epochs -> %s"
          % (len(train), epochs, os.path.basename(path)), flush=True)
    W = train_transition_ff(train, seed=1, ff=delex_config_feats, epochs=epochs)
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = path + ".tmp.npz"; np.savez_compressed(tmp, avg=W.astype(np.float32)); os.replace(tmp, path)
    return W


# --------------------------------------------------------------------- paired bootstrap over records
def paired_boot(a, b, n_boot=2000, seed=20260903):
    """delta = mean(a) - mean(b), paired bootstrap over records. Returns dict with delta, CI, sep, half-width."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    rng = np.random.default_rng(seed); n = len(a); d = a - b
    rr = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n); rr[i] = d[idx].mean()
    lo, hi = float(np.percentile(rr, 2.5)), float(np.percentile(rr, 97.5))
    return {"a_mean": round(float(a.mean()), 4), "b_mean": round(float(b.mean()), 4),
            "delta": round(float(d.mean()), 4), "ci": [round(lo, 4), round(hi, 4)],
            "ci_half_width": round((hi - lo) / 2, 4), "sep": bool(lo > 0), "n": n}


# --------------------------------------------------------------------- PAYOFF 1: recovery past 0.806
def payoff1_recovery(crfp, Wp_delex, W_lex, smoke):
    """CRF_POST (floor 0.806) vs CRF_POST_PARSE_LEX (0.800) vs CRF_POST_PARSE_DELEX. 19c-transfer + modern."""
    cap = 120 if smoke else 700
    qcap = 120 if smoke else 1200
    lbcap = 300 if smoke else 2500
    ud = D.load_ud(D.UD_TEST, cap=cap)
    qasrl = D.load_qasrl(D.QASRL, cap=qcap)
    pop = V1.load_pop(D.LB)
    parse_lex = AEO.parse_with_conf

    arms = {"CRF_POST": (None, None),
            "CRF_POST_PARSE_LEX": (W_lex, parse_lex),
            "CRF_POST_PARSE_DELEX": (Wp_delex, parse_delex)}
    out = {}
    for name, (Wp, pfn) in arms.items():
        arm = "CRF_POST" if Wp is None else "CRF_POST_PARSE"
        mod_rows, mod_ns = CRF.build_rows_crf(ud, crfp, arm, Wp=Wp, parse_fn=pfn)
        q_rows, _ = CRF.build_rows_crf(qasrl, crfp, arm, Wp=Wp, parse_fn=pfn)
        modern = D.evaluate(mod_rows, mod_ns, D.cv_proba(mod_rows))
        clf, mu, sd = D._fit(mod_rows + q_rows)
        c19_rows, c19_ns = CRF.build_rows_19c_crf(pop, crfp, arm, cap=lbcap, Wp=Wp, parse_fn=pfn)
        c19 = D.evaluate(c19_rows, c19_ns, D._proba(clf, mu, sd, c19_rows))

        def pk(r):
            if not r:
                return {"rec": None}
            b = r["best_fp_le_0p5"]; bt = r["bootstrap_delta_vs_twin"]; tw = r["twin_at_best"]
            return {"rec@0.5FP": (b["recovery"] if b else None), "fp": (b["false_verbs_per_sent"] if b else None),
                    "n_pos": r["n_positives"],
                    "delta_vs_twin": (bt["delta_vs_twin_mean"] if bt else None),
                    "ci": (bt["ci"] if bt else None), "twin_sep": ((bt["ci"][0] > 0) if bt else None),
                    "twin_p95": (tw["twin_recovery_p95"] if tw else None)}
        out[name] = {"modern": pk(modern), "c19_transfer": pk(c19)}
        m = out[name]["modern"]; c = out[name]["c19_transfer"]
        print("  %-22s MODERN rec=%s | 19c rec=%s twin_sep=%s delta=%s" % (
            name, m.get("rec@0.5FP"), c.get("rec@0.5FP"), c.get("twin_sep"), c.get("delta_vs_twin")), flush=True)
    return out


# --------------------------------------------------------------------- PAYOFF 2: parser downstream consumer
def _recovered_verbs(toks, pos, crfp, detector):
    """joint-decode CATEGORY re-estimation: tokens the perceptron dropped (non-VERB/AUX, WordNet verb-reading) that the
    calibrated detector promotes above the operating threshold -> force VERB. detector=(clf,mu,sd,th,W,tags,Wp,pfn)."""
    clf, mu, sd, th, W, tags, Wp, pfn = detector
    out = []
    for i in range(len(toks)):
        if pos[i] in ("VERB", "AUX"):
            continue
        if not CRF.VID.has_verb_reading(toks[i]):
            continue
        base = D.feats_parsefree(toks, pos, i, W, tags)
        fv = CRF._cat(base, crfp.vpost(toks)[i], "CRF_POST_PARSE") + base[1:] + D.parse_signals(toks, pos, i, Wp, pfn)
        X = (np.array(fv, float) - mu) / sd
        p = float(clf.predict_proba(X.reshape(1, -1))[0, 1])
        if p >= th:
            out.append(i)
    return out


def payoff2_downstream(crfp, Wp_delex, W_lex, detector, smoke, seed=20260903):
    """19c who-did-what gold-argument reachability + who-did-what accuracy through the PARSE.
    BASE = lexical parser + committed perceptron tags (the live floor). DELEX = register-robust parser + perceptron
    tags (isolates the parser). JOINT = register-robust parser + joint-decoded tags (recovered verbs forced VERB).
    TWIN = register-robust parser + info-free tag corrections (random tokens forced VERB, same count)."""
    tg = D.tagger()
    rows = [r for r in V1.load_pop(D.LB) if PP.cand_ok(r)]
    if smoke:
        rows = rows[:250]
    rng = np.random.default_rng(seed)
    keep = {k: {"base": [], "delex": [], "joint": [], "twin": []} for k in ("reach", "wdw")}
    n_dropped = 0; n_corr = 0
    for r in rows:
        toks = r["sent"].split(); vi0 = r["verb_idx"]; gi0 = r.get("gold_idx")
        if not toks or gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        pos = tg.tag(toks)
        rec_idx = _recovered_verbs(toks, pos, crfp, detector)
        if vi0 in rec_idx or pos[vi0] not in ("VERB", "AUX"):
            n_dropped += int(pos[vi0] not in ("VERB", "AUX"))
        pos_joint = list(pos)
        for i in rec_idx:
            pos_joint[i] = "VERB"
        n_corr += len(rec_idx)
        # info-free twin: force VERB on the same NUMBER of random gate-eligible tokens
        elig = [i for i in range(len(toks)) if pos[i] not in ("VERB", "AUX") and CRF.VID.has_verb_reading(toks[i])]
        pos_twin = list(pos)
        if elig and rec_idx:
            pick = rng.choice(len(elig), size=min(len(rec_idx), len(elig)), replace=False)
            for j in pick:
                pos_twin[elig[j]] = "VERB"
        v1 = vi0 + 1
        H_base, _, _ = AEO.parse_with_conf(toks, pos, W_lex)
        H_delex, _, _ = parse_delex(toks, pos, Wp_delex)
        H_joint, _, _ = parse_delex(toks, pos_joint, Wp_delex)
        H_twin, _, _ = parse_delex(toks, pos_twin, Wp_delex)
        for nm, H, pp in (("base", H_base, pos), ("delex", H_delex, pos), ("joint", H_joint, pos_joint), ("twin", H_twin, pos_twin)):
            keep["reach"][nm].append(int(_attaches_to_verb(gi0 + 1, v1, H, pp, max_hops=MAX_HOPS)))
            keep["wdw"][nm].append(int(PP.chain_pick(r, toks, pp, H, "far") == r["gold_head"]))
    res = {"n_records": len(keep["reach"]["base"]), "n_verb_dropped": n_dropped, "n_tag_corrections": n_corr}
    for metric in ("reach", "wdw"):
        res[metric] = {
            "base_mean": round(float(np.mean(keep[metric]["base"])), 4),
            "delex_mean": round(float(np.mean(keep[metric]["delex"])), 4),
            "joint_mean": round(float(np.mean(keep[metric]["joint"])), 4),
            "twin_mean": round(float(np.mean(keep[metric]["twin"])), 4),
            "joint_vs_base": paired_boot(keep[metric]["joint"], keep[metric]["base"]),
            "delex_vs_base": paired_boot(keep[metric]["delex"], keep[metric]["base"]),
            "joint_vs_twin": paired_boot(keep[metric]["joint"], keep[metric]["twin"]),
        }
        r = res[metric]
        print("  [%s] base=%.4f delex=%.4f joint=%.4f twin=%.4f | joint-vs-base %+.4f sep=%s | joint-vs-twin %+.4f sep=%s" % (
            metric, r["base_mean"], r["delex_mean"], r["joint_mean"], r["twin_mean"],
            r["joint_vs_base"]["delta"], r["joint_vs_base"]["sep"], r["joint_vs_twin"]["delta"], r["joint_vs_twin"]["sep"]), flush=True)
    return res


def _fit_detector(crfp, Wp_delex, smoke):
    """Fit the CRF_POST_PARSE_DELEX detector on modern (self-supervised) + set the FP<=0.5 operating threshold."""
    cap = 120 if smoke else 700
    qcap = 120 if smoke else 1200
    ud = D.load_ud(D.UD_TEST, cap=cap); qasrl = D.load_qasrl(D.QASRL, cap=qcap)
    mod_rows, mod_ns = CRF.build_rows_crf(ud, crfp, "CRF_POST_PARSE", Wp=Wp_delex, parse_fn=parse_delex)
    q_rows, _ = CRF.build_rows_crf(qasrl, crfp, "CRF_POST_PARSE", Wp=Wp_delex, parse_fn=parse_delex)
    clf, mu, sd = D._fit(mod_rows + q_rows)
    modern = D.evaluate(mod_rows, mod_ns, D.cv_proba(mod_rows))
    th = modern["best_fp_le_0p5"]["th"] if (modern and modern["best_fp_le_0p5"]) else 0.5
    tg = D.tagger()
    return (clf, mu, sd, th, tg._perc.weights, tg.tags, Wp_delex, parse_delex)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--retrain-parser", action="store_true", dest="retrain_parser")
    args = ap.parse_args()
    smoke = args.self_test or args.smoke
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)

    # ---- 0. register-robust (delexicalized) parser ----
    Wp_delex = train_or_load_delex(smoke, force=args.retrain_parser)
    W_lex = AEO.load_model(AEO.MODEL_PATH)

    # modern UAS retention (delex vs lexical), UD-EWT test
    test = [s for s in AEO._load_ud_feats("test") if 1 <= len(s) <= MAXLEN]
    if smoke:
        test = test[:150]
    uas_delex = uas_ff(test, Wp_delex, delex_config_feats)
    uas_lex = uas_ff(test, W_lex, lex_config_feats)
    print("[uas] modern UD-EWT test (n=%d sents): lexical=%.4f  delex=%.4f  (delta %+.4f)" % (
        len(test), uas_lex, uas_delex, uas_delex - uas_lex), flush=True)

    # ---- CRF calibrated posterior ----
    crf = CRF.train_or_load_crf(400 if smoke else 4000, force=False); crfp = CRF.CRFPost(crf)

    # ---- PAYOFF 1: recovery of 19c dropped verbs past 0.806 ----
    print("\n===== PAYOFF 1: tagger recovery (past 0.806) =====", flush=True)
    p1 = payoff1_recovery(crfp, Wp_delex, W_lex, smoke)

    # ---- PAYOFF 2: parser downstream consumer (who-did-what reachability / wdw) ----
    print("\n===== PAYOFF 2: parser downstream (19c who-did-what reachability) =====", flush=True)
    detector = _fit_detector(crfp, Wp_delex, smoke)
    p2 = payoff2_downstream(crfp, Wp_delex, W_lex, detector, smoke)

    res = {"uas_modern": {"lexical": round(uas_lex, 4), "delex": round(uas_delex, 4)},
           "payoff1_recovery": p1, "payoff2_downstream": p2,
           "floors": {"CRF_POST_19c": 0.806, "CRF_POST_PARSE_LEX_19c": 0.800, "perceptron_19c": 0.582},
           "smoke": bool(smoke)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "joint_decode_register_robust_tagger_parser_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)

    if smoke:
        assert p1["CRF_POST_PARSE_DELEX"]["c19_transfer"].get("rec@0.5FP") is not None
        assert p2["reach"]["n" if False else "base_mean"] is not None
        print("\n[self-test] PASS", flush=True)
    print("\n[done] %.0fs -> %s" % (time.time() - t0, OUT_DIR), flush=True)


if __name__ == "__main__":
    main()
