"""exp_register_predicate_detector_v1 -- a REGISTER-ROBUST, glass-box, self-supervised PREDICATE detector.

PROBLEM: register_robust_event_detection_the_reader_drops_events_when_the_tagger_misses_the_verb.
On raw prose the reader fires an event at every UPOS==VERB token (landed tense_agnostic detector). When the tagger
mis-tags a real verb (archaic / noun-with-a-verb-reading / noun-flanked), NO event fires and the whole clause is lost.
A heuristic override over-generates (3.72 false-verbs/sentence). The parent's post-hoc noisy-channel override recovers
0.50 @ 0.92 FP on 19c but does NOT generalize to modern (0.16 @ 0.46 FP) -- because it is a SINGLE-CUE, hard-AND/OR,
structure-ONLY rule that discards load-bearing signal (the brain-mechanism drill: predicate-hood = a LEARNED
noisy-channel combination of a lexical LIKELIHOOD (tagger verb-margin) x a structural/frame PRIOR, Gibson 2013; the
precision comes from COMBINING cues + one-predicate-per-clause competition, never one threshold).

THIS CELL: a small glass-box LOGISTIC combiner over REGISTER-INVARIANT cues, trained SELF-SUPERVISED on modern
auto-labels (natural tagger errors on gold held-out from the tagger's own training), then applied to recover dropped
verbs. The headline is TRANSFER: train on MODERN, recover 19c mis-tags with ZERO 19c labels (register-invariance is the
brain's signature -- Jabberwocky/novel-verb structure-building). An info-free twin (random verbhood promotion at the
matched rate) must LOSE. Precision guard: report recovery at a controlled false-verbs/sentence budget (no flooding).

Features (register-invariant; the drill's spec):
  verb_margin      tagger emission score(VERB) - best non-VERB non-AUX     (noisy-channel LIKELIHOOD; Gibson 2013)
  frame_anchor     Mintz N-[tok]-N, no other VERB in the clause slot        (frequent-frame; Mintz 2003) -- sparse/precise
  subj_before      a nominal within k tokens BEFORE                         (argument scaffolding)
  obj_after        a nominal within k tokens AFTER                          (argument scaffolding)
  morph_finite     finite-verb suffix (-s/-ed/-ing/-eth/-est/-'d/-th)       (morphology carries what frames miss; Monaghan05)
  clause_verbless  the tagger left NO VERB in the sentence                  (one-predicate-per-clause competition; Spivey-K93)
  rel_position     token index / len                                        (predicates are rarely sentence-initial/-final)
  [optional +parse] local_gain, global_delta (force-VERB re-parse; the parent's structural signal) -- --with-parse

Glass-box, CPU, NO LLM, NO spaCy, NO nltk except WordNet (a fixed lexicon, the candidate gate). ASCII. own dir. Nothing
in hdlab modified. Remote-safe (in-substrate tagger+parser; parses live, no cached parse needed).

# KB_REFERENT: data/frontend_assets/pos_tagger_ud_ewt_upos.json
# KB_REFERENT: data/frontend_assets_exp/arceager_dynamic_ud_ewt.npz
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/predict_revise_recall_v1/_population_litbank.json
# KB_REFERENT: data/benchmark_trap_check/qasrl/qasrl-v2/orig/dev.jsonl.gz
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import argparse, gzip, json, sys, time
from collections import Counter
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

from hdlab.pos_tagger import PosTagger, pos_features
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_whodidwhat_verb_id_recoverable_v1 as VID  # has_verb_reading, frame_verb_cue

OUT_DIR = os.path.join(_REPO, "data/exp_register_predicate_detector_v1")
TAGGER_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
UD_TRAIN = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu")
LB = os.path.join(_REPO, "data/predict_revise_recall_v1/_population_litbank.json")
QASRL = os.path.join(_REPO, "data/benchmark_trap_check/qasrl/qasrl-v2/orig/dev.jsonl.gz")

NOMINAL = ("NOUN", "PROPN", "PRON")
FEAT_NAMES = ["verb_margin", "frame_anchor", "subj_before", "obj_after", "morph_finite", "clause_verbless", "rel_position"]
PARSE_FEAT_NAMES = ["local_gain", "global_delta"]

_TG = None
def tagger():
    global _TG
    if _TG is None:
        _TG = PosTagger.load(TAGGER_ASSET)
    return _TG


def verb_margin(obs, i, W, tags):
    """emission(VERB) - best emission over non-VERB non-AUX tags (the noisy-channel lexical LIKELIHOOD)."""
    s = {t: sum(W.get(f, 0.0) for f in pos_features(obs, i, t)) for t in tags}
    v = s.get("VERB", -1e9)
    best_non = max(val for t, val in s.items() if t not in ("VERB", "AUX"))
    return v - best_non


def morph_finite(w):
    """Finite/participial verb morphology (register-inclusive incl. archaic -eth/-est/'d/-th)."""
    wl = w.lower()
    for suf in ("ing", "eth", "est", "ed", "th", "'d", "es", "s", "d", "n"):
        if wl.endswith(suf) and len(wl) > len(suf) + 1:
            return 1.0
    return 0.0


def feats_parsefree(toks, pos, i, W, tags):
    subj = 1.0 if any(pos[j] in NOMINAL for j in range(max(0, i - 4), i)) else 0.0
    obj = 1.0 if any(pos[j] in NOMINAL for j in range(i + 1, min(len(toks), i + 5))) else 0.0
    frame = 1.0 if VID.frame_verb_cue(toks, pos, i) else 0.0
    verbless = 0.0 if any(p == "VERB" for p in pos) else 1.0
    relpos = i / max(1, len(toks) - 1)
    return [verb_margin(toks, i, W, tags), frame, subj, obj, morph_finite(toks[i]), verbless, relpos]


def parse_signals(toks, pos, i, Wp, parse_fn):
    """(local_gain, global_delta) for forcing token i to VERB -- the parent's noisy-channel structural signal."""
    def measure(p):
        heads, conf, _ = parse_fn(toks, p, Wp)
        deps = [(c - 1) for c, h in heads.items() if h == i + 1]
        nom_pre = [c for c in deps if c < i and pos[c] in NOMINAL]
        nom_post = [c for c in deps if c > i and pos[c] in NOMINAL]
        local = (conf.get(nom_pre[-1] + 1, 0.0) if nom_pre else 0.0) \
            + (conf.get(nom_post[0] + 1, 0.0) if nom_post else 0.0) \
            + 0.25 * (bool(nom_pre) + bool(nom_post))
        glob = float(np.mean([c for c in conf.values()])) if conf else 0.0
        return local, glob
    l0, g0 = measure(pos)
    alt = list(pos); alt[i] = "VERB"
    l1, g1 = measure(alt)
    return [l1 - l0, g1 - g0]


# ------------------------------------------------------------------ population -> per-sentence candidate rows
def _cands(toks, pos, gold_verb_set, W, tags, Wp, parse_fn, use_parse):
    """Rescue candidates in one sentence: non-VERB non-AUX tokens with a WordNet verb-reading (register-invariant gate).
    Returns list of (i, feature_vec, label) where label=1 iff the token is a real verb the tagger dropped."""
    out = []
    for i in range(len(toks)):
        if pos[i] in ("VERB", "AUX"):
            continue
        if not VID.has_verb_reading(toks[i]):
            continue
        fv = feats_parsefree(toks, pos, i, W, tags)
        if use_parse:
            fv = fv + parse_signals(toks, pos, i, Wp, parse_fn)
        out.append((i, fv, 1 if i in gold_verb_set else 0))
    return out


def load_ud(path, cap=None):
    sents = []; cur = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("#"):
            continue
        if not line.strip():
            if cur:
                sents.append(cur); cur = []
            continue
        c = line.split("\t")
        if "-" in c[0] or "." in c[0]:
            continue
        cur.append(c)
    if cur:
        sents.append(cur)
    out = []
    for s in sents:
        toks = [c[1] for c in s]
        gold_verb = set(i for i, c in enumerate(s) if c[3] == "VERB")  # non-AUX real verbs
        out.append((toks, gold_verb))
    return out[:cap] if cap else out


def load_qasrl(path, cap=None):
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            out.append((d["sentenceTokens"], set(int(k) for k in d["verbEntries"].keys())))
            if cap and len(out) >= cap:
                break
    return out


def build_rows(sents, W, tags, Wp, parse_fn, use_parse):
    """[(sent_idx, i, feats, label)] over all rescue candidates; plus per-sentence token counts."""
    tg = tagger()
    rows = []; nsent = 0
    for toks, gold_verb in sents:
        if not toks:
            continue
        pos = tg.tag(toks)
        # a DROPPED real verb = gold VERB the tagger tagged non-VERB (the recoverable target)
        dropped = set(i for i in gold_verb if pos[i] not in ("VERB", "AUX"))
        for (i, fv, _lab) in _cands(toks, pos, gold_verb, W, tags, Wp, parse_fn, use_parse):
            rows.append((nsent, i, fv, 1 if i in dropped else 0))
        nsent += 1
    return rows, nsent


def build_rows_19c(pop, W, tags, Wp, parse_fn, use_parse, cap=None):
    """19c LitBank who-did-what population. The gold verb is r['verb_idx']. A DROPPED genuine verb = verb_idx tagged
    NOUN/ADJ/ADV/ADP (NOT AUX -- copula-as-AUX is correct UPOS, out of scope). Candidates over the whole sentence give
    the false-verb population (other non-verb tokens)."""
    tg = tagger()
    rows = []; nsent = 0
    if cap:
        pop = pop[:cap]
    for r in pop:
        toks = r["sent"].split(); vi = r["verb_idx"]
        if not toks or vi >= len(toks):
            continue
        pos = tg.tag(toks)
        genuine_drop = (pos[vi] not in ("VERB", "AUX"))  # exclude copula-as-AUX
        gv = {vi} if genuine_drop else set()
        for (i, fv, _lab) in _cands(toks, pos, gv, W, tags, Wp, parse_fn, use_parse):
            rows.append((nsent, i, fv, 1 if i in gv else 0))
        nsent += 1
    return rows, nsent


# ------------------------------------------------------------------ eval: recovery vs FP, twin, bootstrap CI
def _standardize(X, mu, sd):
    return (X - mu) / sd


def evaluate(rows, nsent, proba, seed=20260903, n_boot=2000):
    """For each threshold: recovery (promoted positives / total positives), false_verbs/sent (promoted negatives/nsent).
    Info-free twin: promote the SAME NUMBER of candidates at random, measure recovery. Bootstrap CI over sentences on
    the recovery at the operating point (FP<=1.0/sent). `proba` = P(predicate) per candidate row (held-out for modern)."""
    if not rows:
        return None
    y = np.array([r[3] for r in rows], dtype=np.int64)
    sidx = np.array([r[0] for r in rows], dtype=np.int64)
    thresholds = list(np.linspace(0.05, 0.99, 40))
    n_pos = int(y.sum())
    curve = []
    for th in thresholds:
        promote = proba >= th
        rec = float((promote & (y == 1)).sum()) / max(1, n_pos)
        fp = float((promote & (y == 0)).sum()) / max(1, nsent)
        curve.append({"th": round(float(th), 4), "recovery": round(rec, 4),
                      "false_verbs_per_sent": round(fp, 4), "n_promoted": int(promote.sum())})
    ok = [c for c in curve if c["false_verbs_per_sent"] <= 1.0]
    best = max(ok, key=lambda c: c["recovery"]) if ok else None
    # tighter budget too
    ok_tight = [c for c in curve if c["false_verbs_per_sent"] <= 0.5]
    best_tight = max(ok_tight, key=lambda c: c["recovery"]) if ok_tight else None

    twin = None; boot = None
    if best is not None and best["n_promoted"] > 0:
        rng = np.random.default_rng(seed)
        k = best["n_promoted"]
        n = len(y)
        twrec = []
        for _ in range(400):
            pick = rng.choice(n, size=min(k, n), replace=False)
            m = np.zeros(n, dtype=bool); m[pick] = True
            twrec.append(float((m & (y == 1)).sum()) / max(1, n_pos))
        twin = {"n_promoted": k, "twin_recovery_mean": round(float(np.mean(twrec)), 4),
                "twin_recovery_p95": round(float(np.percentile(twrec, 95)), 4)}
        # bootstrap CI over SENTENCES on (combiner recovery - twin mean recovery) at the operating threshold
        th = best["th"]
        promote = proba >= th
        uniq = np.unique(sidx)
        rr = np.empty(n_boot)
        for b in range(n_boot):
            samp = rng.choice(uniq, size=len(uniq), replace=True)
            mask = np.isin(sidx, samp)
            # recompute per-resample: recovery of combiner vs twin at matched promoted-count
            yb = y[mask]; pb = promote[mask]
            npos_b = max(1, int(yb.sum()))
            rec_b = float((pb & (yb == 1)).sum()) / npos_b
            kb = int(pb.sum())
            # twin draw within the resample
            nb = len(yb)
            if nb > 0 and kb > 0:
                pk = rng.choice(nb, size=min(kb, nb), replace=False)
                tm = np.zeros(nb, dtype=bool); tm[pk] = True
                tw_b = float((tm & (yb == 1)).sum()) / npos_b
            else:
                tw_b = 0.0
            rr[b] = rec_b - tw_b
        boot = {"delta_vs_twin_mean": round(float(rr.mean()), 4),
                "ci": [round(float(np.percentile(rr, 2.5)), 4), round(float(np.percentile(rr, 97.5)), 4)],
                "ci_half_width": round(float((np.percentile(rr, 97.5) - np.percentile(rr, 2.5)) / 2), 4)}
    return {"n_candidates": len(rows), "n_sent": nsent, "n_positives": n_pos,
            "best_fp_le_1": best, "best_fp_le_0p5": best_tight, "twin_at_best": twin, "bootstrap_delta_vs_twin": boot,
            "curve": curve}


def _fit(rows):
    from sklearn.linear_model import LogisticRegression
    X = np.array([r[2] for r in rows], dtype=np.float64)
    y = np.array([r[3] for r in rows], dtype=np.int64)
    mu = X.mean(axis=0); sd = X.std(axis=0); sd[sd == 0] = 1.0
    clf = LogisticRegression(max_iter=2000, class_weight="balanced")
    clf.fit(_standardize(X, mu, sd), y)
    return clf, mu, sd


def _proba(clf, mu, sd, rows):
    X = np.array([r[2] for r in rows], dtype=np.float64)
    return clf.predict_proba(_standardize(X, mu, sd))[:, 1]


def evaluate_fixed(rows, nsent, proba, th, seed=20260903, n_boot=2000):
    """Recovery/FP/twin/CI at a SINGLE FIXED threshold (the deployed operating point set on modern) -- the honest
    cross-register number (no per-population threshold tuning)."""
    if not rows:
        return None
    y = np.array([r[3] for r in rows], dtype=np.int64)
    sidx = np.array([r[0] for r in rows], dtype=np.int64)
    n_pos = int(y.sum())
    promote = proba >= th
    rec = float((promote & (y == 1)).sum()) / max(1, n_pos)
    fp = float((promote & (y == 0)).sum()) / max(1, nsent)
    k = int(promote.sum())
    rng = np.random.default_rng(seed)
    n = len(y)
    tw = [float((lambda m: (m & (y == 1)).sum())(np.isin(np.arange(n), rng.choice(n, size=min(k, n), replace=False))) / max(1, n_pos)) for _ in range(400)]
    uniq = np.unique(sidx); rr = np.empty(n_boot)
    for b in range(n_boot):
        samp = rng.choice(uniq, size=len(uniq), replace=True); mask = np.isin(sidx, samp)
        yb = y[mask]; pb = promote[mask]; npb = max(1, int(yb.sum())); kb = int(pb.sum()); nb = len(yb)
        rec_b = float((pb & (yb == 1)).sum()) / npb
        if nb > 0 and kb > 0:
            pk = rng.choice(nb, size=min(kb, nb), replace=False); tm = np.zeros(nb, dtype=bool); tm[pk] = True
            tw_b = float((tm & (yb == 1)).sum()) / npb
        else:
            tw_b = 0.0
        rr[b] = rec_b - tw_b
    return {"threshold": round(float(th), 4), "recovery": round(rec, 4), "false_verbs_per_sent": round(fp, 4),
            "n_promoted": k, "twin_recovery_mean": round(float(np.mean(tw)), 4), "twin_recovery_p95": round(float(np.percentile(tw, 95)), 4),
            "delta_vs_twin_mean": round(float(rr.mean()), 4),
            "ci": [round(float(np.percentile(rr, 2.5)), 4), round(float(np.percentile(rr, 97.5)), 4)],
            "ci_half_width": round(float((np.percentile(rr, 97.5) - np.percentile(rr, 2.5)) / 2), 4)}


def cv_proba(rows, k=5, seed=20260903):
    """5-fold CV over SENTENCES -> held-out P(predicate) per candidate (honest within-modern generalization)."""
    sids = sorted(set(r[0] for r in rows))
    rng = np.random.default_rng(seed); rng.shuffle(sids)
    fold_of = {s: (idx % k) for idx, s in enumerate(sids)}
    proba = np.zeros(len(rows))
    for f in range(k):
        tr = [r for r in rows if fold_of[r[0]] != f]
        te_idx = [j for j, r in enumerate(rows) if fold_of[r[0]] == f]
        if not tr or not te_idx or sum(r[3] for r in tr) == 0:
            continue
        clf, mu, sd = _fit(tr)
        te = [rows[j] for j in te_idx]
        pr = _proba(clf, mu, sd, te)
        for j, p in zip(te_idx, pr):
            proba[j] = p
    return proba


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--with-parse", action="store_true", dest="with_parse")
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)

    tg = tagger(); W = tg._perc.weights; tags = tg.tags
    Wp = None; parse_fn = None
    if args.with_parse:
        from hdlab.arceager_parser import load_model, parse_with_conf, MODEL_PATH
        Wp = load_model(MODEL_PATH); parse_fn = parse_with_conf

    cap = 60 if args.self_test else (150 if args.smoke else (None if args.full else 800))
    qcap = 60 if args.self_test else (150 if args.smoke else (None if args.full else 1500))
    lbcap = 400 if (args.self_test or args.smoke) else (None if args.full else 2500)

    # --- MODERN set: UD-EWT test (gold POS, HELD-OUT from the tagger's train/test split -> natural verb-drops). ---
    print("building MODERN rows (UD-EWT test, gold) ...", flush=True)
    ud_test = load_ud(UD_TEST, cap=cap)
    mod_rows, mod_ns = build_rows(ud_test, W, tags, Wp, parse_fn, args.with_parse)
    # MODERN generalization = 5-fold CV over UD-EWT test (held-out folds; clean gold labels/negatives).
    mod_proba = cv_proba(mod_rows)
    modern = evaluate(mod_rows, mod_ns, mod_proba)

    # --- TRANSFER combiner: train on ALL modern (UD-test + QA-SRL positives to enrich) -> apply to 19c, 0 19c labels ---
    print("building QA-SRL (modern OOD) training-enrichment rows ...", flush=True)
    qasrl = load_qasrl(QASRL, cap=qcap)
    q_rows, q_ns = build_rows(qasrl, W, tags, Wp, parse_fn, args.with_parse)
    train_all = mod_rows + q_rows
    clf, mu, sd = _fit(train_all)
    fnames = FEAT_NAMES + (PARSE_FEAT_NAMES if args.with_parse else [])
    coefs = dict(zip(fnames, [round(float(c), 3) for c in clf.coef_[0]]))
    ntr_pos = int(sum(r[3] for r in train_all))

    print("building 19c TRANSFER rows (LitBank who-did-what pop) ...", flush=True)
    pop = V1.load_pop(LB)
    c19_rows, c19_ns = build_rows_19c(pop, W, tags, Wp, parse_fn, args.with_parse, cap=lbcap)
    c19_proba = _proba(clf, mu, sd, c19_rows)
    c19 = evaluate(c19_rows, c19_ns, c19_proba)

    # QA-SRL modern-OOD recovery (recovery-only; QA-SRL under-annotates verbs so its negatives/FP are a NOISY upper bound)
    qeval = evaluate(q_rows, q_ns, cv_proba(q_rows)) if q_rows else None

    # --- SINGLE DEPLOYED THRESHOLD set on MODERN (FP<=0.5), applied UNCHANGED to 19c (honest, no per-pop tuning) ---
    th_star = modern["best_fp_le_0p5"]["th"] if (modern and modern["best_fp_le_0p5"]) else 0.5
    c19_fixed = evaluate_fixed(c19_rows, c19_ns, c19_proba, th_star)

    # --- PERSIST the detector as a deployable static asset (glass-box json: weights + standardizer + threshold) ---
    asset = {"model": "logistic_noisy_channel_predicate_detector", "feat_names": fnames,
             "coef": [float(c) for c in clf.coef_[0]], "intercept": float(clf.intercept_[0]),
             "mu": [float(x) for x in mu], "sd": [float(x) for x in sd],
             "operating_threshold_fp_le_0p5_modern": round(float(th_star), 4), "with_parse": bool(args.with_parse),
             "gate": "wordnet_verb_reading_and_non_aux", "trained_on": "UD-EWT-test + QA-SRL-dev (modern, self-supervised auto-labels)"}
    with open(os.path.join(OUT_DIR, "predicate_detector_asset.json"), "w", encoding="ascii") as fh:
        json.dump(asset, fh, indent=2)

    res = {
        "with_parse": bool(args.with_parse),
        "n_train_candidates": len(train_all), "n_train_positives": ntr_pos,
        "combiner_coefs_standardized": coefs, "combiner_intercept": round(float(clf.intercept_[0]), 3),
        "MODERN_udtest_cv_generalization": modern,
        "C19_litbank_transfer": c19,
        "C19_transfer_at_MODERN_fixed_threshold": c19_fixed,
        "QASRL_modern_ood_cv_recoveryonly": qeval,
        "parent_baselines": {"heuristic_combined_fp_per_sent": 3.72, "noisy_channel_19c": "0.50rec@0.92FP",
                             "noisy_channel_modern": "0.16rec@0.46FP"},
    }
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "register_predicate_detector_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()},
                  fh, indent=2)

    print("\n===== REGISTER-ROBUST PREDICATE DETECTOR (learned noisy-channel combiner) with_parse=%s =====" % args.with_parse, flush=True)
    print("  transfer-combiner train: %d candidates, %d positives (dropped real verbs)" % (len(train_all), ntr_pos), flush=True)
    print("  combiner weights (standardized):", coefs, flush=True)
    for name, r in (("MODERN(UD-test CV)", modern), ("19c-TRANSFER(LitBank)", c19), ("QASRL-OOD(CV,noisy-FP)", qeval)):
        if r and r["best_fp_le_1"]:
            b = r["best_fp_le_1"]; tw = r["twin_at_best"]; bt = r["bootstrap_delta_vs_twin"]
            print("\n  %s  n_pos=%d n_sent=%d n_cand=%d" % (name, r["n_positives"], r["n_sent"], r["n_candidates"]), flush=True)
            print("    BEST @ FP<=1.0/sent: recovery=%.4f fp=%.4f  (twin recovery=%.4f p95=%.4f)" % (
                b["recovery"], b["false_verbs_per_sent"], tw["twin_recovery_mean"] if tw else -1, tw["twin_recovery_p95"] if tw else -1), flush=True)
            if r["best_fp_le_0p5"]:
                print("    BEST @ FP<=0.5/sent: recovery=%.4f fp=%.4f" % (r["best_fp_le_0p5"]["recovery"], r["best_fp_le_0p5"]["false_verbs_per_sent"]), flush=True)
            if bt:
                print("    delta(combiner-twin)=%.4f CI[%.4f,%.4f] half=%.4f null_twin_p95=%.4f -> %s" % (
                    bt["delta_vs_twin_mean"], bt["ci"][0], bt["ci"][1], bt["ci_half_width"],
                    tw["twin_recovery_p95"] if tw else -1,
                    "CI-SEPARATED (twin loses)" if bt["ci"][0] > 0 else "NOT separated"), flush=True)
        else:
            print("\n  %s: NO operating point at FP<=1.0" % name, flush=True)
    if c19_fixed:
        print("\n  19c at MODERN-FIXED threshold %.3f (no per-pop tuning): recovery=%.4f fp=%.4f delta_vs_twin=%.4f CI[%.4f,%.4f] -> %s" % (
            c19_fixed["threshold"], c19_fixed["recovery"], c19_fixed["false_verbs_per_sent"], c19_fixed["delta_vs_twin_mean"],
            c19_fixed["ci"][0], c19_fixed["ci"][1], "CI-SEPARATED" if c19_fixed["ci"][0] > 0 else "ns"), flush=True)
    print("\n  asset saved -> %s/predicate_detector_asset.json" % OUT_DIR, flush=True)

    if args.self_test or args.smoke:
        assert len(train_all) > 20 and ntr_pos >= 3, "need some rescue positives"
        assert c19 is not None
        print("\n[self-test] PASS", flush=True)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
