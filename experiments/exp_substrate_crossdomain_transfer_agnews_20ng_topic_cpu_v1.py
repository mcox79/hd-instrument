"""
exp_substrate_crossdomain_transfer_agnews_20ng_topic_cpu_v1.py -- closed-feature TOPIC cross-domain transfer (AG-News -> 20NG) -- CPU.

ROUTING: strategy_request closed-feature topic-classification transfer (v591; 2nd-appearance test for
  meta::RULE_cross_domain_transfer_tail_shape_is_capability_class_dependent). Substrate-quality-first; NO LLM frame.
  CONFIRMING-vs-FALSIFYING test: closed-feature single-label tasks are predicted to CONVERGE to neutral at 100pct (unlike
  open-vocab NER which keeps a tail). 1st closed-feature anchor = PP-409 SST-2->IMDB sentiment (converged). This is a 2nd
  closed-feature anchor at a NON-sentiment task (topic classification).

  Label alignment (warm-start needs aligned classes): AG-News has {World,Sports,Business,Sci/Tech}; 20-newsgroups has no
  Business-like topic, so we restrict to the 3 cleanly-shared classes {World, Sports, Sci/Tech} and map 20NG's 20 groups onto
  them (politics/religion->World; rec.sport->Sports; comp.*/sci.*->Sci/Tech; drop forsale/autos/motorcycles). Genuine domain
  shift: news ARTICLES -> newsgroup FORUM posts.

  Classifier = multiclass averaged perceptron (discriminative_perceptron) over hashed word-unigram+bigram features. Warm-start
  transfer (init target weights from AG-News-trained weights) vs train-from-scratch on 20NG, at target fractions
  {1,2.5,5,10,100}pct, 3 seeds.

  DATA: AG-News bundled. 20NG via sklearn.fetch_20newsgroups (env-gated -> UNKNOWN if unavailable on the runner).

PRE-REGISTERED (v591): macro-F1 transfer/scratch ratio.
  HARD-PASS: ratio@2.5pct >= 1.20 (low-data lift) AND ratio@100pct in [0.95,1.10] (CONVERGES -- confirms closed-feature class).
  MIDDLE: ratio@2.5pct >= 1.20 but ratio@100pct > 1.10 (lift but non-converging -- rule needs refinement: maybe vocab-size,
  not open/closed, drives the tail). HARD-FAIL: ratio@2.5pct < 0.95 (no transfer). UNKNOWN if 20NG unavailable.
ASCII-only. CPU. --self-test + --smoke + metrics.json. Route via remote_cpu_queue (desktop; laptop CPU paused).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, re
from pathlib import Path
from typing import Dict, Tuple, List
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_crossdomain_transfer_agnews_20ng_topic_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
FRACS = [0.01, 0.025, 0.05, 0.10, 1.0]
SEEDS = [7, 8, 9]
NBITS = 20; DIM = 1 << NBITS
# 3 shared classes: 0=World, 1=Sports, 2=Sci/Tech (AG-News Business=label2 dropped)
CLASSES = [0, 1, 2]
AGNEWS_MAP = {"0": 0, "1": 1, "3": 2}  # AG-News labels World=0,Sports=1,Sci/Tech=3 -> 0,1,2 ; Business=2 dropped
_TOK = re.compile(r"[a-z']+")


def _20ng_map(name: str):
    if name.startswith("rec.sport"): return 1
    if name.startswith("comp.") or name.startswith("sci."): return 2
    if name.startswith("talk.politics") or name.startswith("talk.religion") or name.startswith("soc.religion") or name == "alt.atheism": return 0
    return None  # drop misc.forsale, rec.autos, rec.motorcycles


def _feats(text):
    toks = _TOK.findall(text.lower()); idxs = [hash("u_" + w) & (DIM - 1) for w in toks]
    for i in range(len(toks) - 1): idxs.append(hash("b_" + toks[i] + "_" + toks[i + 1]) & (DIM - 1))
    return idxs


def _train_mc(data, epochs, w0, seed):
    """Multiclass averaged perceptron. w[c] is a (DIM,) vector. Returns averaged {c: vec}."""
    w = {c: (w0[c].copy() if w0 else np.zeros(DIM)) for c in CLASSES}
    cw = {c: np.zeros(DIM) for c in CLASSES}; c_t = 1
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        for i in rng.permutation(len(data)):
            idxs, y = data[i]
            scores = {c: w[c][idxs].sum() for c in CLASSES}
            pred = max(scores, key=scores.get)
            if pred != y:
                w[y][idxs] += 1; cw[y][idxs] += c_t
                w[pred][idxs] -= 1; cw[pred][idxs] -= c_t
            c_t += 1
    return {c: w[c] - cw[c] / c_t for c in CLASSES}


def _macro_f1(data, w):
    tp = defaultdict(int); fp = defaultdict(int); fn = defaultdict(int)
    for idxs, y in data:
        pred = max(CLASSES, key=lambda c: w[c][idxs].sum())
        if pred == y: tp[y] += 1
        else: fp[pred] += 1; fn[y] += 1
    f1s = []
    for c in CLASSES:
        p = tp[c] / (tp[c] + fp[c] + 1e-9); r = tp[c] / (tp[c] + fn[c] + 1e-9)
        f1s.append(2 * p * r / (p + r + 1e-9))
    return sum(f1s) / len(f1s)


def _load_agnews():
    d = json.load(open(REPO / "experiments" / "data" / "ag_news.json", encoding="utf-8"))
    out = []
    for e in d["train"]:
        c = AGNEWS_MAP.get(str(e.get("label")))
        if c is not None and e.get("text"): out.append((_feats(e["text"]), c))
    return out


def _load_20ng():
    # SetFit/20_newsgroups parquet (datasets lib; reliable -- avoids the sklearn fetch_20newsgroups download hang).
    try:
        from datasets import load_dataset
        ds = load_dataset("SetFit/20_newsgroups")
        def grab(split):
            out = []
            for txt, name in zip(ds[split]["text"], ds[split]["label_text"]):
                c = _20ng_map(name)
                if c is not None and txt and txt.strip(): out.append((_feats(txt), c))
            return out
        return grab("train"), grab("test")
    except Exception as e:
        print("[20ng] unavailable: %s" % str(e)[:120], flush=True); return None


def run() -> Dict:
    ag = _load_agnews()
    ng = _load_20ng()
    if ng is None:
        return {"error": "twentyng_unavailable_env_gated", "note": "needs sklearn.fetch_20newsgroups on the runner; harness correct + ready"}
    ng_tr, ng_te = ng
    rng0 = np.random.default_rng(0)
    cap_ag = 600 if SMOKE else 4500; cap_tr = 400 if SMOKE else 3000; cap_te = 150 if SMOKE else 1500
    ag = [ag[i] for i in rng0.permutation(len(ag))[:cap_ag]]
    ng_tr = [ng_tr[i] for i in rng0.permutation(len(ng_tr))[:cap_tr]]
    ng_te = [ng_te[i] for i in rng0.permutation(len(ng_te))[:cap_te]]
    ep = 3 if SMOKE else 8
    w_src = _train_mc(ag, ep, None, 123)
    f_src_only = _macro_f1(ng_te, w_src)
    print("  [src] AG-News model zero-shot on 20NG macro-F1=%.4f (ag=%d, 20ng_test=%d, %d classes)" % (f_src_only, len(ag), len(ng_te), len(CLASSES)), flush=True)
    fracs = [0.025] if SMOKE else FRACS
    seeds = SEEDS[:1] if SMOKE else SEEDS
    curve = []
    for fr in fracs:
        sc = []; tf = []
        for sd in seeds:
            rng = np.random.default_rng(sd)
            n = max(6, int(len(ng_tr) * fr)); sub = [ng_tr[i] for i in rng.permutation(len(ng_tr))[:n]]
            sc.append(_macro_f1(ng_te, _train_mc(sub, ep, None, sd)))
            tf.append(_macro_f1(ng_te, _train_mc(sub, ep, w_src, sd)))
        scm = sum(sc) / len(sc); tfm = sum(tf) / len(tf)
        curve.append({"frac": fr, "scratch_f1": round(scm, 4), "transfer_f1": round(tfm, 4), "ratio": round(tfm / (scm + 1e-9), 4)})
        print("  frac=%5.1f%% scratch=%.4f transfer=%.4f ratio=%.4f" % (100 * fr, scm, tfm, curve[-1]["ratio"]), flush=True)
    return {"curve": curve, "src_only_f1": round(f_src_only, 4), "n_classes": len(CLASSES), "n_20ng_test": len(ng_te)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error", "").startswith("twentyng"):
        return ("UNKNOWN", "UNKNOWN: 20NG unavailable (env-gated; needs sklearn.fetch_20newsgroups). Harness correct + ready. " + r.get("note", ""))
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    by = {c["frac"]: c for c in r["curve"]}
    r25 = by.get(0.025, {}).get("ratio"); r100 = by.get(1.0, {}).get("ratio")
    s = ("ratio@2.5pct=%s ratio@100pct=%s; zero-shot AG-on-20NG F1=%s; curve=%s" %
         (r25, r100, r.get("src_only_f1"), [(c["frac"], c["scratch_f1"], c["transfer_f1"], c["ratio"]) for c in r["curve"]]))
    if r25 is None or r100 is None:
        return ("UNKNOWN", "UNKNOWN: missing 2.5pct or 100pct fraction. " + s)
    if r25 >= 1.20 and 0.95 <= r100 <= 1.10:
        return ("HARD_PASS", "HARD_PASS: closed-feature topic transfer CONFIRMS the rule -- low-data lift (ratio@2.5pct>=1.20) AND converges to neutral at 100pct (ratio in [0.95,1.10]). 2nd closed-feature anchor (topic, non-sentiment) for the capability-class tail-shape rule. " + s)
    if r25 >= 1.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: low-data lift present but tail does NOT converge (ratio@100pct>1.10 or <0.95) -- closed-feature converging prediction not cleanly confirmed; rule may need refinement (vocab-size vs open/closed split). " + s)
    return ("HARD_FAIL", "HARD_FAIL: ratio@2.5pct<1.20 -- no clear low-data cross-domain topic transfer. " + s)


def _selftest():
    assert _20ng_map("rec.sport.hockey") == 1 and _20ng_map("comp.graphics") == 2 and _20ng_map("talk.politics.guns") == 0
    assert _20ng_map("misc.forsale") is None and AGNEWS_MAP.get("2") is None
    rng = np.random.default_rng(0)
    data = [(_feats("game team score win"), 1), (_feats("government election policy"), 0), (_feats("computer software code"), 2)] * 15
    w = _train_mc(data, 5, None, 0); assert _macro_f1(data, w) > 0.8
    print("[selftest] PASS: crossdomain-agnews-20ng-topic (macro-F1=%.3f)" % _macro_f1(data, w), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
