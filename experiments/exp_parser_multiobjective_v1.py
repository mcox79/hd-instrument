"""exp_parser_multiobjective_v1 -- THE multi-objective bar for the improved parser. Given the disambiguation
(FINDINGS_disambiguation.md): the frontend arc_labeler is HARMFUL (-0.030 modern / -0.107 on 19c), and the
in-substrate UAS ceiling (~0.81 arc-eager) cannot reach spaCy via the sanctioned global-training infra
(HARD_FAIL on disk). So the improved parser = the arc-eager incremental heads (loadable operator, cell
exp_arceager_parser_operator_v1) + LABEL-FREE thematic role recovery (head-attachment + POS + voice + position;
drop the labeler) + an emitted attachment CONFIDENCE distribution (graded_competition / N7).

MEASURES (all vs the live baseline arc-factored richfeat + arc_labeler LABELED = 0.515):
  who-did-what patient (QA-SRL science FULL/HARD + 19c LitBank):
    FLOOR_POS      linear position
    BASE_CURRENT   richfeat heads + arc_labeler LABELED     (the live frontend = parent 0.515)
    FE_LABELFREE   richfeat heads + label-free              (drop labeler, same heads)
    AE_LABELFREE   arc-eager heads + label-free             (the IMPROVED parser; main arm)
    TWIN_AE_SHUF   arc-eager heads SHUFFLED + label-free    (info-free control -> must LOSE)
  2nd task (COMPOUNDS): subject->verb attachment on UD-EWT test (the who-DID/agent side), arc-eager vs richfeat,
    buried vs easy -> does the parse gain carry to a DIFFERENT role.
  N7 distribution: does the arc-eager attachment confidence / graded_competition entropy predict who-did-what
    errors (AUC)?  twin = shuffled confidence -> AUC ~0.5.
  no-regress: patient COVERAGE (did label-free drop args?), POS unchanged (same tagger).

Reuses exp_parser_gap_decomp_v1 (frontend parse + pick rules), exp_arceager_parser_operator_v1 (the operator),
hdlab.graded_competition (N7). spaCy NOT used here. ASCII. own dir. --self-test gates the arc-eager parse arm.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from collections import defaultdict
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_parser_gap_decomp_v1 as GD
import experiments.exp_arceager_parser_operator_v1 as AEO
from hdlab import graded_competition as GC

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_parser_multiobjective_v1")
NOUN_POS = ("NOUN", "PROPN", "PRON")


def _auc(scores, labels):
    """AUC of scores predicting positive label (1). Rank-based (Mann-Whitney). labels in {0,1}."""
    s = np.asarray(scores, float); y = np.asarray(labels, int)
    pos = s[y == 1]; neg = s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    order = np.argsort(s); ranks = np.empty(len(s), float); ranks[order] = np.arange(1, len(s) + 1)
    # average ties
    _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt); start = csum - cnt
    avg = (start + csum + 1) / 2.0
    ranks = avg[inv]
    rpos = ranks[y == 1].sum()
    return float((rpos - len(pos) * (len(pos) + 1) / 2.0) / (len(pos) * len(neg)))


def arceager_parses(sents, W, tg, shuffle=False, seed=0):
    """sent -> (({}, labelfree{vlem:set((form,tag,pas))}), confmap{vlem:{form:conf}}). Mirrors
    GD.frontend_parses but with arc-eager heads + attach confidence. shuffle=info-free head twin."""
    from hdlab.reading_grounding_loop import normalize_lemma
    rng = np.random.default_rng(seed)
    out = {}; confout = {}
    t0 = time.time()
    for k, sent in enumerate(sents):
        toks = GD.STRUCT.findall(sent)
        labelfree = defaultdict(set); confv = defaultdict(dict)
        if toks and len(toks) <= 80:
            pos = tg.tag(toks)
            heads, conf, marg = AEO.parse_with_conf(toks, pos, W)
            if shuffle:
                keys = list(range(1, len(toks) + 1)); vals = [heads.get(i, 0) for i in keys]
                rng.shuffle(vals); heads = {i: v for i, v in zip(keys, vals)}
            lem = [normalize_lemma(t) for t in toks]; low = [t.lower() for t in toks]; N = len(toks)
            for i in range(1, N + 1):
                h = heads.get(i, 0)
                if not (1 <= h <= N and pos[h - 1] == "VERB"):
                    continue
                vlem = V1._lem(lem[h - 1])
                if pos[i - 1] in GD.NOUN:
                    pas = GD._voice_is_passive(low, h - 1); tag = "PRE" if i < h else "POST"
                    labelfree[vlem].add((lem[i - 1], tag, pas)); labelfree[vlem].add((low[i - 1], tag, pas))
                    c = conf.get(i, 0.0)
                    confv[vlem][lem[i - 1]] = c; confv[vlem][low[i - 1]] = c
        out[sent] = ({}, dict(labelfree)); confout[sent] = {v: dict(d) for v, d in confv.items()}
        if (k + 1) % 1500 == 0:
            print("[arceager] %d/%d %.0fs" % (k + 1, len(sents), time.time() - t0), flush=True)
    return out, confout


def coverage(rows, fn):
    """fraction of items where the arm emitted a NON-position patient (did the parse contribute an arg?)."""
    n = c = 0
    for r in rows:
        if len(GD.cands(r)) < 2:
            continue
        n += 1
        if fn(r) != r.get("pos_pick"):
            c += 1
    return round(c / n, 4) if n else 0.0


def run_pop(pop_name, path, W, tg, nboot):
    rows = V1.load_pop(path)
    sents = sorted({r["sent"] for r in rows})
    print("[%s] %d items %d sents" % (pop_name, len(rows), len(sents)), flush=True)
    fe = GD.frontend_parses(sents)
    ae, aeconf = arceager_parses(sents, W, tg)
    ae_sh, _ = arceager_parses(sents, W, tg, shuffle=True, seed=7)

    def nonrev(r):
        return sum(1 for h, _ in GD.cands(r) if GD.anim(h)) < 2
    FULL = [r for r in rows if len(GD.cands(r)) >= 2 and nonrev(r)]
    HARD = [r for r in FULL if (r.get("voice") == "passive" or r.get("noncanonical"))]
    arms = {
        "FLOOR_POS": lambda r: r.get("pos_pick"),
        "BASE_CURRENT": lambda r: GD.pick_labeled(r, fe),
        "FE_LABELFREE": lambda r: GD.pick_labelfree(r, fe),
        "AE_LABELFREE": lambda r: GD.pick_labelfree(r, ae),
        "TWIN_AE_SHUF": lambda r: GD.pick_labelfree(r, ae_sh),
    }

    def acc(fn, S):
        return round(sum(1 for r in S if fn(r) == r["gold_head"]) / len(S), 4) if S else 0.0
    res = {"n_FULL": len(FULL), "n_HARD": len(HARD), "acc": {}, "deltas": {}, "coverage": {}}
    for tag, S in (("FULL", FULL), ("HARD", HARD)):
        res["acc"][tag] = {a: acc(f, S) for a, f in arms.items()}
        print("\n=== %s / %s (n=%d) ===" % (pop_name, tag, len(S)), flush=True)
        for a in arms:
            print("  %-14s acc=%.4f" % (a, res["acc"][tag][a]), flush=True)
    D = lambda a, b, S: {k: V1.paired_delta(S, arms[a], arms[b], nboot)[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")}
    res["deltas"]["AE_vs_BASE_FULL"] = D("AE_LABELFREE", "BASE_CURRENT", FULL)
    res["deltas"]["AE_vs_BASE_HARD"] = D("AE_LABELFREE", "BASE_CURRENT", HARD)
    res["deltas"]["AE_vs_FE_FULL"] = D("AE_LABELFREE", "FE_LABELFREE", FULL)      # head-attach effect
    res["deltas"]["FE_vs_BASE_FULL"] = D("FE_LABELFREE", "BASE_CURRENT", FULL)    # labeler-drop effect
    res["deltas"]["AE_vs_TWIN_FULL"] = D("AE_LABELFREE", "TWIN_AE_SHUF", FULL)    # info-free control
    print("  --- key deltas (FULL unless noted) ---", flush=True)
    for lbl, d in res["deltas"].items():
        print("    %-18s d=%+.4f CI[%+.4f,%+.4f] frac<=0=%.3f" % (lbl, d["delta"], d["ci_lo"], d["ci_hi"], d["frac_le_0"]), flush=True)
    res["coverage"] = {"BASE_CURRENT": coverage(FULL, arms["BASE_CURRENT"]),
                       "FE_LABELFREE": coverage(FULL, arms["FE_LABELFREE"]),
                       "AE_LABELFREE": coverage(FULL, arms["AE_LABELFREE"])}
    print("  coverage (emit non-position patient): %s" % res["coverage"], flush=True)

    # N7: does arc-eager attach confidence / graded entropy predict AE_LABELFREE errors?
    diff_conf = []; diff_ent = []; diff_shuf = []; err = []
    rng = np.random.default_rng(11)
    for r in FULL:
        pick = GD.pick_labelfree(r, ae)
        e = int(pick != r["gold_head"]); err.append(e)
        cmap = aeconf.get(r["sent"], {}).get(V1._lem(r["verb"]), {})
        conf_pick = cmap.get(V1._lem(pick), cmap.get(pick, 0.0)) if pick else 0.0
        diff_conf.append(1.0 - conf_pick)
        # graded_competition over candidates: cues = position(post-verbal) + attach-conf
        C = GD.cands(r); vi = r["verb_idx"]
        supp_pos = [1.0 if idx > vi else 0.0 for h, idx in C]
        supp_att = [cmap.get(V1._lem(h), cmap.get(h, 0.0)) for h, idx in C]
        gp = GC.graded_pick({"pos": supp_pos, "att": supp_att}, {"pos": 1.0, "att": 2.0})
        diff_ent.append(gp["entropy"])
        diff_shuf.append(float(rng.random()))
    res["N7"] = {"auc_conf_vs_error": round(_auc(diff_conf, err), 4),
                 "auc_entropy_vs_error": round(_auc(diff_ent, err), 4),
                 "auc_shuffled_twin": round(_auc(diff_shuf, err), 4),
                 "err_rate": round(float(np.mean(err)), 4)}
    print("  N7 difficulty->error AUC: conf=%.4f entropy=%.4f shuffled-twin=%.4f (err_rate=%.3f)" % (
        res["N7"]["auc_conf_vs_error"], res["N7"]["auc_entropy_vs_error"], res["N7"]["auc_shuffled_twin"], res["N7"]["err_rate"]), flush=True)
    return res


# ---------- 2nd task: subject->verb attachment on UD-EWT (compounding) ----------
def _classify_buried(sent, s_idx, v_idx, s_num):
    fn = None
    for (i, w, p, h, dl, num) in sent:
        if p in NOUN_POS:
            fn = i; break
    subj_is_first = (fn == s_idx)
    lo, hi = min(s_idx, v_idx), max(s_idx, v_idx)
    diff = False
    if s_num is not None:
        for (i, w, p, h, dl, num) in sent:
            if lo < i < hi and p in NOUN_POS and num is not None and num != s_num:
                diff = True; break
    return (not subj_is_first) and diff, subj_is_first


def subject_task(W, tg):
    from hdlab.arc_parser import ArcParser
    test = [s for s in AEO._load_ud_feats("test") if 1 <= len(s) <= AEO.MAXLEN]
    rich = ArcParser.load(os.path.join(_REPO, "data", "frontend_assets", "arc_parser_richfeat_ud_ewt.npz"))

    def ae_heads(s):
        toks = [w for (_i, w, _p, _h, _d, _n) in s]; pos = [p for (_i, _w, p, _h, _d, _n) in s]
        h, _, _ = AEO.parse_with_conf(toks, pos, W); return h

    def rich_heads(s):
        toks = [w for (_i, w, _p, _h, _d, _n) in s]; pos = [p for (_i, _w, p, _h, _d, _n) in s]
        return rich.parse(toks, pos).heads

    out = {}
    for nm, fn in (("arc_eager", ae_heads), ("richfeat", rich_heads)):
        hb = tb = he = te = 0
        for s in test:
            heads = fn(s); n = len(s)
            for (i, w, p, h, dl, num) in s:
                if not dl.startswith("nsubj"):
                    continue
                v = h
                if v < 1 or v > n or s[v - 1][2] not in ("VERB", "AUX"):
                    continue
                buried, easy = _classify_buried(s, i, v, num)
                corr = int(heads.get(i, -1) == v)
                if buried: hb += corr; tb += 1
                if easy: he += corr; te += 1
        out[nm] = {"buried": round(hb / tb, 4) if tb else 0.0, "easy": round(he / te, 4) if te else 0.0,
                   "n_buried": tb, "n_easy": te}
        print("  [subj-task] %-10s buried=%.4f easy=%.4f (n_buried=%d)" % (nm, out[nm]["buried"], out[nm]["easy"], tb), flush=True)
    out["buried_gain"] = round(out["arc_eager"]["buried"] - out["richfeat"]["buried"], 4)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nboot", type=int, default=2000)
    ap.add_argument("--pops", type=str, default="qa,litbank")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        # tiny arc-eager weights: parse runs, returns heads/conf of right length
        W = np.zeros(AEO.SIZE)
        h, c, m = AEO.parse_with_conf(["The", "cat", "sat"], ["DET", "NOUN", "VERB"], W)
        assert len(h) == 3 and len(c) == 3, "parse_with_conf shape"
        assert abs(_auc([0.9, 0.1, 0.8, 0.2], [1, 0, 1, 0]) - 1.0) < 1e-9, "auc"
        print("[selftest] PASS", flush=True); return
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    W = AEO.load_model(AEO.MODEL_PATH)
    out = {"pops": {}}
    for p in args.pops.split(","):
        out["pops"][p] = run_pop(p, {"qa": V1.QA, "litbank": V1.LB}[p], W, tg, args.nboot)
    print("\n=== 2nd TASK: subject->verb attachment on UD-EWT (compounding) ===", flush=True)
    out["subject_task"] = subject_task(W, tg)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "parser_multiobjective_v1", "results": out,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
