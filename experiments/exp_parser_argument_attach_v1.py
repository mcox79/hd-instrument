"""exp_parser_argument_attach_v1 -- PARSE-ATTACH PRECISION ON ARGUMENTS (the bar's explicitly-requested metric,
"reported as parse-attach PRECISION on ARGUMENTS, not just overall UAS") + the compounding 2nd task. On UD-EWT
test, per gold argument relation {obj, nsubj, nsubj:pass, obl, iobj, ccomp, xcomp}, does the head attach to the
correct governor? arc-eager (improved) vs richfeat (live) vs hashed. Object-attach compounds to who-did-what
PATIENT; subject-attach to who-did-what AGENT (a DIFFERENT role = the 2nd downstream task). Buried subjects
broken out (the error-propagation-prone long arc). Bootstrap CIs over sentences. CPU numpy, NO torch/spaCy/LLM.
ASCII. own dir.
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
import experiments.exp_arceager_parser_operator_v1 as AEO

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_parser_argument_attach_v1")
ARG_RELS = ("obj", "nsubj", "nsubj:pass", "obl", "iobj", "ccomp", "xcomp")
NOUN_POS = ("NOUN", "PROPN", "PRON")


def _base_rel(dl):
    return dl.split(":", 1)[0] if dl.split(":", 1)[0] in ("obj", "nsubj", "obl", "iobj", "ccomp", "xcomp") else dl


def _is_buried_subj(sent, s_idx, v_idx, s_num):
    fn = None
    for (i, w, p, h, dl, num) in sent:
        if p in NOUN_POS:
            fn = i; break
    lo, hi = min(s_idx, v_idx), max(s_idx, v_idx)
    diff = False
    if s_num is not None:
        for (i, w, p, h, dl, num) in sent:
            if lo < i < hi and p in NOUN_POS and num is not None and num != s_num:
                diff = True; break
    return (fn != s_idx) and diff


def eval_heads(test, head_fn):
    """per-relation attach accuracy + per-sentence correct/total for bootstrap. Returns dict."""
    per = defaultdict(lambda: [0, 0])          # rel -> [correct, total]
    buried = [0, 0]; easy = [0, 0]
    # per-sentence obj / nsubj correctness lists for bootstrap
    sent_obj = []; sent_subj = []
    for s in test:
        heads = head_fn(s); n = len(s)
        oc = ot = sc = st = 0
        for (i, w, p, h, dl, num) in s:
            rb = dl if dl in ("nsubj:pass",) else _base_rel(dl)
            if rb not in ARG_RELS:
                continue
            if h < 1 or h > n:
                continue
            ok = int(heads.get(i, -1) == h)
            per[rb][0] += ok; per[rb][1] += 1
            if rb == "obj":
                oc += ok; ot += 1
            if rb in ("nsubj", "nsubj:pass"):
                sc += ok; st += 1
                if s[h - 1][2] in ("VERB", "AUX"):
                    if _is_buried_subj(s, i, h, num):
                        buried[0] += ok; buried[1] += 1
                    else:
                        easy[0] += ok; easy[1] += 1
        if ot:
            sent_obj.append((oc, ot))
        if st:
            sent_subj.append((sc, st))
    out = {rel: {"acc": round(per[rel][0] / per[rel][1], 4) if per[rel][1] else 0.0, "n": per[rel][1]} for rel in ARG_RELS}
    out["_buried_subj"] = {"acc": round(buried[0] / buried[1], 4) if buried[1] else 0.0, "n": buried[1]}
    out["_easy_subj"] = {"acc": round(easy[0] / easy[1], 4) if easy[1] else 0.0, "n": easy[1]}
    return out, sent_obj, sent_subj


def _boot_delta(a_pairs, b_pairs, nboot=2000, seed=13):
    """paired bootstrap over sentences of (acc_a - acc_b) where each sentence contributes (correct,total)."""
    rng = np.random.default_rng(seed)
    a = np.array(a_pairs, float); b = np.array(b_pairs, float)  # aligned by sentence index
    m = min(len(a), len(b)); a = a[:m]; b = b[:m]
    def acc(x, idx):
        c = x[idx, 0].sum(); t = x[idx, 1].sum(); return c / t if t else 0.0
    base = acc(a, np.arange(m)) - acc(b, np.arange(m))
    ds = []
    for _ in range(nboot):
        idx = rng.integers(0, m, m)
        ds.append(acc(a, idx) - acc(b, idx))
    ds = np.array(ds)
    return {"delta": round(float(base), 4), "ci_lo": round(float(np.percentile(ds, 2.5)), 4),
            "ci_hi": round(float(np.percentile(ds, 97.5)), 4), "frac_le_0": round(float((ds <= 0).mean()), 3)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--nboot", type=int, default=2000); args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.arc_parser import ArcParser
    W = AEO.load_model(AEO.MODEL_PATH)
    test = [s for s in AEO._load_ud_feats("test") if 1 <= len(s) <= AEO.MAXLEN]
    print("[data] UD-EWT test sents=%d" % len(test), flush=True)

    def ae_heads(s):
        toks = [w for (_i, w, _p, _h, _d, _n) in s]; pos = [p for (_i, _w, p, _h, _d, _n) in s]
        h, _, _ = AEO.parse_with_conf(toks, pos, W); return h
    parsers = {}
    for nm, fn in (("richfeat", "arc_parser_richfeat_ud_ewt.npz"), ("hashed", "arc_parser_hashed_ud_ewt.npz")):
        pr = ArcParser.load(os.path.join(_REPO, "data", "frontend_assets", fn))
        parsers[nm] = (lambda pr: (lambda s: pr.parse([w for (_i, w, _p, _h, _d, _n) in s],
                                                       [p for (_i, _w, p, _h, _d, _n) in s]).heads))(pr)

    res = {}; sents = {}
    for nm, fn in [("arc_eager", ae_heads)] + list(parsers.items()):
        r, so, ss = eval_heads(test, fn); res[nm] = r; sents[nm] = (so, ss)
        print("\n[%s] per-argument attach precision:" % nm, flush=True)
        for rel in ARG_RELS:
            print("    %-12s acc=%.4f (n=%d)" % (rel, r[rel]["acc"], r[rel]["n"]), flush=True)
        print("    buried-subj=%.4f (n=%d)  easy-subj=%.4f (n=%d)" % (
            r["_buried_subj"]["acc"], r["_buried_subj"]["n"], r["_easy_subj"]["acc"], r["_easy_subj"]["n"]), flush=True)

    # compounding deltas: arc-eager vs richfeat (live) on obj (->patient) and subj (->agent)
    d_obj = _boot_delta(sents["arc_eager"][0], sents["richfeat"][0], args.nboot)
    d_subj = _boot_delta(sents["arc_eager"][1], sents["richfeat"][1], args.nboot)
    res["_deltas_vs_richfeat"] = {"obj_attach": d_obj, "subj_attach": d_subj}
    print("\n=== arc-eager vs richfeat (live) argument-attach deltas ===", flush=True)
    print("  OBJ  ->patient : d=%+.4f CI[%+.4f,%+.4f] frac<=0=%.3f" % (d_obj["delta"], d_obj["ci_lo"], d_obj["ci_hi"], d_obj["frac_le_0"]), flush=True)
    print("  SUBJ ->agent   : d=%+.4f CI[%+.4f,%+.4f] frac<=0=%.3f" % (d_subj["delta"], d_subj["ci_lo"], d_subj["ci_hi"], d_subj["frac_le_0"]), flush=True)

    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "parser_argument_attach_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
