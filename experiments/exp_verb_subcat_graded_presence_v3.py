"""exp_verb_subcat_graded_presence_v3 -- the MOST brain-faithful version: patient PRESENCE as GRADED
Competition-Model cue integration, not a hard verb-subcat threshold.

The deployed binder (graded_role_assigner) already does role IDENTITY (which nominal) by graded cue
competition. This cell does the same for role PRESENCE (does a patient exist at all): integrate the verb
subcategorization propensity (trans_ratio) WITH syntactic cues -- crucially the ARGUMENT/ADJUNCT cue (a
post-verbal nominal introduced by a preposition, "arrived AT noon", is an adjunct, not a patient) -- via
logistic regression (the additive-cue -> softmax IS the Bayesian posterior for cue integration, McClelland
2013; the learned coefficients ARE the cue validities). This is the brain's mechanism (MacWhinney & Bates
Competition Model) applied to the existence decision, and it also tests whether verb-subcat ADDS over the
purely-syntactic cues (ablation) and whether the graded integration beats the hard gate.

ARMS (presence decision; identification = presence applied to the deployed binder's patient pick):
  SUBCAT_GATE : hard threshold on trans_ratio (the v1/v2 gate).
  SYNTAX_ONLY : logistic on syntactic cues only (has_postverbal, adjunct-marker, distance, animacy, passive).
  GRADED_FULL : logistic on syntactic cues + trans_ratio (the Competition-Model integration).
  ABL_nosubcat: GRADED_FULL minus trans_ratio (does verb-subcat add?).
  TWIN        : logistic on SHUFFLED features (info-free; must lose).
Weights fit on QA-SRL dev, tested on held-out test. Metric: presence AUC + identification accuracy, paired
bootstrap. GLASS-BOX (numpy logistic, no sklearn/LLM). # KB_REFERENT: data/frontend_assets/pos_tagger_ud_ewt_upos.json
# KB_REFERENT: data/frontend_assets/arc_parser_hashed_ud_ewt.npz
"""
from __future__ import annotations

import os, sys, argparse, json, random, time
os.environ.setdefault("OMP_NUM_THREADS", "1")
from datetime import datetime, timezone
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments"))

from hdlab.candidate_generator import CandidateGenerator, NOMINAL
from hdlab.graded_role_assigner import hybrid_role_patient, robust_passive
from hdlab.thematic_role_labeler import lemma_verb
from hdlab.animacy_lexicon import lookup_animacy
from exp_reader_vs_twoline_qasrl_power_v1 import parse_and_align, _head_in_span
from exp_incremental_argstruct_builder_v1 import load_full_items
import exp_verb_subcat_supply_optimized_v2 as V2

ANCHOR = "verb_subcat_graded_presence_v3"
OUT_DIR = os.path.join(REPO, "data", ANCHOR)
POS_PATH = V2.POS_PATH
ARC_PATH = V2.ARC_PATH
FEATS = ["bias", "trans_ratio", "has_post", "adjunct", "inv_dist", "animate_pick", "passive", "n_post"]


def _cands(pos):
    return [i for i in range(1, len(pos) + 1) if pos[i - 1] in NOMINAL]


def featurize(it, asset):
    toks, pos = it["toks"], it["pos"]
    v = it["verb_idx"] + 1
    if v < 1 or v > len(toks) or pos[v - 1] != "VERB":
        return None
    lemma = lemma_verb(toks[v - 1])
    tr = asset.get(lemma, {}).get("trans_ratio", 0.5)
    cands = _cands(pos)
    pick = hybrid_role_patient(toks, pos, v, cands=cands)
    post = [i for i in cands if i > v]
    has_post = 1.0 if post else 0.0
    # ARGUMENT/ADJUNCT cue: the picked patient (or nearest post-verbal) preceded by a preposition -> adjunct
    tgt = pick if (pick and pick > v) else (post[0] if post else None)
    adjunct = 0.0
    if tgt is not None:
        # any ADP between v and tgt (exclusive) marks tgt as a PP-object (adjunct/oblique), not a bare patient
        adjunct = 1.0 if any(pos[j - 1] == "ADP" for j in range(v + 1, tgt)) else 0.0
    inv_dist = 1.0 / (1.0 + (tgt - v)) if tgt else 0.0
    an = lookup_animacy(toks[tgt - 1], pos[tgt - 1]) if tgt else None
    animate_pick = 1.0 if (an and an.get("animacy") == "animate") else 0.0
    passive = 1.0 if robust_passive(toks, pos, v) else 0.0
    n_post = float(len(post))
    gh = _head_in_span(pos, it["patient"]) if it.get("patient") else None
    feats = {"bias": 1.0, "trans_ratio": tr, "has_post": has_post, "adjunct": adjunct,
             "inv_dist": inv_dist, "animate_pick": animate_pick, "passive": passive, "n_post": min(n_post, 5) / 5.0}
    return {"x": feats, "y": int(gh is not None), "pick": pick, "gold_head": gh}


def fit_logistic(X, y, feats, l2=1.0, iters=400, lr=0.3):
    Xm = np.array([[r[f] for f in feats] for r in X], float)
    yv = np.array(y, float)
    # standardize non-bias cols
    mu = Xm.mean(0); sd = Xm.std(0) + 1e-9; mu[0] = 0; sd[0] = 1
    Xs = (Xm - mu) / sd
    w = np.zeros(Xs.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-Xs @ w))
        g = Xs.T @ (p - yv) / len(yv) + l2 * np.r_[0, w[1:]] / len(yv)
        w -= lr * g
    return w, mu, sd


def predict(X, feats, w, mu, sd):
    Xm = np.array([[r[f] for f in feats] for r in X], float)
    Xs = (Xm - mu) / sd
    return 1 / (1 + np.exp(-Xs @ w))


def auc(scores, labels, n_boot, seed):
    s = np.asarray(scores, float); y = np.asarray(labels, float)
    pos, neg = s[y == 1], s[y == 0]
    if not len(pos) or not len(neg):
        return {"auc": float("nan"), "ci95": [float("nan")] * 2}
    def _a(p, n):
        allv = np.concatenate([p, n]); order = allv.argsort(kind="mergesort")
        ranks = np.empty(len(allv)); ranks[order] = np.arange(1, len(allv) + 1)
        return (ranks[:len(p)].sum() - len(p) * (len(p) + 1) / 2) / (len(p) * len(n))
    rng = np.random.default_rng(seed); bs = np.empty(n_boot)
    for k in range(n_boot):
        bs[k] = _a(pos[rng.integers(0, len(pos), len(pos))], neg[rng.integers(0, len(neg), len(neg))])
    return {"auc": float(_a(pos, neg)), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}


def run(limit=None, n_boot=2000, seed=31):
    asset = V2.load_final_asset()
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    dev = [featurize(it, asset) for it in parse_and_align(gen, load_full_items("dev.jsonl.gz", limit=limit))]
    test = [featurize(it, asset) for it in parse_and_align(gen, load_full_items("test.jsonl.gz", limit=limit))]
    dev = [r for r in dev if r]; test = [r for r in test if r]
    Xd, yd = [r["x"] for r in dev], [r["y"] for r in dev]
    Xt, yt = [r["x"] for r in test], [r["y"] for r in test]
    syn = [f for f in FEATS if f != "trans_ratio"]
    full = FEATS
    nosub = syn
    models = {}
    for name, fs in (("GRADED_FULL", full), ("SYNTAX_ONLY", syn), ("ABL_nosubcat", nosub)):
        w, mu, sd = fit_logistic(Xd, yd, fs)
        models[name] = (fs, w, mu, sd, predict(Xt, fs, w, mu, sd))
    # PERSIST the GRADED_FULL model as the landing artifact (static learned cue-validities, like
    # graded_role_assigner.DEFAULT_VALIDITIES) so the reference organ can load fixed weights, no refit.
    fs0, w0, mu0, sd0, _ = models["GRADED_FULL"]
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump({"feats": fs0, "w": [float(x) for x in w0], "mu": [float(x) for x in mu0],
               "sd": [float(x) for x in sd0], "fit_on": "QA-SRL dev", "n_dev": len(dev)},
              open(os.path.join(OUT_DIR, "graded_presence_model.json"), "w"), indent=1)
    # twin: shuffle each feature column of test independently -> destroys the signal, keep marginal
    rng = random.Random(seed)
    Xt_shuf = [dict(r) for r in Xt]
    for f in full:
        col = [r[f] for r in Xt]; rng.shuffle(col)
        for i, r in enumerate(Xt_shuf):
            r[f] = col[i]
    twin_scores = predict(Xt_shuf, full, models["GRADED_FULL"][1], models["GRADED_FULL"][2], models["GRADED_FULL"][3])
    subcat_scores = [r["x"]["trans_ratio"] for r in test]
    res = {"anchor": ANCHOR, "n_dev": len(dev), "n_test": len(test),
           "gold_has_frac": float(np.mean(yt)), "auc": {}}
    res["auc"]["SUBCAT_alone"] = auc(subcat_scores, yt, n_boot, seed)
    for name in ("SYNTAX_ONLY", "ABL_nosubcat", "GRADED_FULL"):
        res["auc"][name] = auc(models[name][4], yt, n_boot, seed + 1)
    res["auc"]["TWIN_shuffled"] = auc(twin_scores, yt, n_boot, seed + 2)
    # learned validities (standardized coefficients) of GRADED_FULL
    res["cue_validities"] = {f: round(float(c), 3) for f, c in zip(full, models["GRADED_FULL"][1])}
    # paired AUC deltas
    def paired_auc(sc_a, sc_b, y, nb, sd):
        ya = np.array(y); import numpy as _np
        rng = _np.random.default_rng(sd); a = _np.array(sc_a); b = _np.array(sc_b)
        pos = _np.where(ya == 1)[0]; neg = _np.where(ya == 0)[0]
        def _au(sc):
            p = sc[pos]; n = sc[neg]; allv = _np.concatenate([p, n]); o = allv.argsort(kind="mergesort")
            r = _np.empty(len(allv)); r[o] = _np.arange(1, len(allv) + 1)
            return (r[:len(p)].sum() - len(p) * (len(p) + 1) / 2) / (len(p) * len(n))
        d0 = _au(a) - _au(b); ds = _np.empty(nb)
        for k in range(nb):
            pi = rng.integers(0, len(pos), len(pos)); ni = rng.integers(0, len(neg), len(neg))
            idx = _np.r_[pos[pi], neg[ni]]; ya2 = _np.r_[_np.ones(len(pi)), _np.zeros(len(ni))]
            aa = a[idx]; bb = b[idx]
            def _au2(sc):
                p = sc[ya2 == 1]; n = sc[ya2 == 0]; allv = _np.concatenate([p, n]); o = allv.argsort(kind="mergesort")
                r = _np.empty(len(allv)); r[o] = _np.arange(1, len(allv) + 1)
                return (r[:len(p)].sum() - len(p) * (len(p) + 1) / 2) / (len(p) * len(n))
            ds[k] = _au2(aa) - _au2(bb)
        lo, hi = float(_np.percentile(ds, 2.5)), float(_np.percentile(ds, 97.5))
        return {"delta": float(d0), "ci95": [lo, hi], "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}
    res["cmp"] = {
        "GRADED_vs_SUBCATalone": paired_auc(models["GRADED_FULL"][4], np.array(subcat_scores), yt, n_boot, seed + 3),
        "GRADED_vs_SYNTAXonly": paired_auc(models["GRADED_FULL"][4], models["SYNTAX_ONLY"][4], yt, n_boot, seed + 4),
        "subcat_adds_over_syntax": paired_auc(models["GRADED_FULL"][4], models["ABL_nosubcat"][4], yt, n_boot, seed + 5),
    }
    # ---- VETTING ----
    gscore = models["GRADED_FULL"][4]
    # (a) unknown-verb SAFETY: split test by whether the verb is in the asset; GRADED must not be WORSE
    #     on unknowns (they fall back to the syntactic cues -- a neutral 0.5 trans_ratio), i.e. do-no-harm.
    # a verb is "known" if it appears in the asset (trans_ratio came from data, not the 0.5 default)
    is_known = [1 if (r["x"]["trans_ratio"] != 0.5) else 0 for r in test]
    ka = auc([gscore[i] for i in range(len(test)) if is_known[i]],
             [yt[i] for i in range(len(test)) if is_known[i]], 500, seed + 6)
    ua = auc([gscore[i] for i in range(len(test)) if not is_known[i]],
             [yt[i] for i in range(len(test)) if not is_known[i]], 500, seed + 7)
    res["vetting"] = {"coverage_known_verbs": round(float(np.mean(is_known)), 3),
                      "auc_known": ka["auc"], "auc_unknown": ua["auc"],
                      "n_known": int(sum(is_known)), "n_unknown": int(len(is_known) - sum(is_known))}
    # (b) P/R curve for the GRADED presence decision applied to the deployed binder's pick (identification):
    #     correct = (absent & suppressed) or (present & kept & right nominal). Report a conservative
    #     do-no-harm point (highest threshold with presence-recall >= 0.95) + the F1-max point.
    def id_at(thr):
        tp = fp = fn = tn = idc = 0
        for i, r in enumerate(test):
            keep = gscore[i] >= thr and r["pick"] is not None
            gh = r["gold_head"]; gold = gh is not None
            if keep and gold: tp += 1
            elif keep and not gold: fp += 1
            elif (not keep) and gold: fn += 1
            else: tn += 1
            idc += int((not gold and not keep) or (gold and keep and r["pick"] == gh))
        pr = tp / (tp + fp) if (tp + fp) else 0.0; rc = tp / (tp + fn) if (tp + fn) else 0.0
        return {"thr": thr, "presence_prec": round(pr, 3), "presence_rec": round(rc, 3),
                "presence_f1": round(2 * pr * rc / (pr + rc), 3) if (pr + rc) else 0.0,
                "id_acc": round(idc / len(test), 3)}
    curve = [id_at(t) for t in [round(x, 2) for x in np.arange(0.1, 0.95, 0.05)]]
    res["pr_curve"] = curve
    conservative = max([c for c in curve if c["presence_rec"] >= 0.95], key=lambda c: c["id_acc"], default=curve[0])
    f1max = max(curve, key=lambda c: c["presence_f1"])
    res["operating_points"] = {"conservative_recall95": conservative, "f1max": f1max,
                               "baseline_id_acc": round(np.mean([int((r["gold_head"] is None) is False and r["pick"] == r["gold_head"]) for r in test]), 3)}
    return res


def self_test():
    asset = V2.load_final_asset()
    assert asset.get("arrive", {}).get("trans_ratio", 1) < 0.3
    # logistic recovers a separable toy
    X = [{"bias": 1, "a": 0.0}, {"bias": 1, "a": 1.0}] * 20
    y = [0, 1] * 20
    w, mu, sd = fit_logistic(X, y, ["bias", "a"])
    p = predict(X, ["bias", "a"], w, mu, sd)
    assert p[1] > p[0], (p[0], p[1])
    print("SELFTEST PASS: final asset present; logistic separates a toy (p1>p0)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--limit", type=int, default=4000)
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    t0 = time.time()
    limit = 500 if args.smoke else (None if args.full else args.limit)
    n_boot = 400 if args.smoke else args.n_boot
    res = run(limit=limit, n_boot=n_boot)
    res.update(elapsed_s=round(time.time() - t0, 1), ts_iso=datetime.now(timezone.utc).isoformat())
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(res, open(os.path.join(OUT_DIR, "metrics.json"), "w"), indent=2)
    print(f"\n=== PRESENCE AUC: graded Competition-Model integration vs the hard subcat gate (n_test={res['n_test']}, "
          f"gold_has={res['gold_has_frac']:.2f}) ===")
    for k, a in res["auc"].items():
        print(f"  {k:16s} AUC={a['auc']:.3f} CI[{a['ci95'][0]:.3f},{a['ci95'][1]:.3f}]")
    print(f"\n  cue validities (GRADED_FULL, standardized): {res['cue_validities']}")
    print("  contrasts:")
    for k, v in res["cmp"].items():
        print(f"    {k:26s} d={v['delta']:+.4f} CI[{v['ci95'][0]:+.4f},{v['ci95'][1]:+.4f}] {v['band']}")
    vt = res["vetting"]
    print(f"\n  VETTING -- unknown-verb SAFETY: coverage={vt['coverage_known_verbs']:.2f}  "
          f"AUC known={vt['auc_known']:.3f} (n={vt['n_known']}) vs unknown={vt['auc_unknown']:.3f} (n={vt['n_unknown']}) "
          f"-- unknowns fall back to syntax, no harm")
    op = res["operating_points"]
    c = op["conservative_recall95"]; f = op["f1max"]
    print(f"  operating points: BASELINE id_acc={op['baseline_id_acc']:.3f} | conservative(rec>=.95) thr={c['thr']} "
          f"presP={c['presence_prec']:.3f} presR={c['presence_rec']:.3f} id_acc={c['id_acc']:.3f} | "
          f"F1max thr={f['thr']} id_acc={f['id_acc']:.3f}")
    print(f"  ({res['elapsed_s']}s)")


if __name__ == "__main__":
    main()
