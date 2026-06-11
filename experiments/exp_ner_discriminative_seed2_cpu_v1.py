"""
exp_ner_discriminative_cpu_v1.py -- discriminative (structured-perceptron) NER on OntoNotes -- CPU.

ROUTING: 5th discriminative-weighting task (after POS/parse/math/code). Structured-perceptron BIO sequence labeling with
  vectorized Viterbi + Collins updates over rich features (word/suffix/shape/context) on OntoNotes English NER (18 entity
  types). Entity-level span F1. Bundled OntoNotes (RESCUE pattern; tags: 0=O, odd=B-, even=I-). Same universal discriminative-
  weighting lever; a genuine NLP capability, no LLM.
PRE-REGISTERED: HARD-PASS entity-F1 >= 0.75 (substrate-classical NER production-grade). MIDDLE >= 0.65. HARD-FAIL < 0.55. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "ner_discriminative_seed2_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"
def _emit_feats(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%d" % (wl, tag), "sh_%s~%d" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%d" % (k, wl[-k:], tag))
    if len(wl) >= 3: fs.append("pre3_%s~%d" % (wl[:3], tag))
    fs.append("pw_%s~%d" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%d" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    fs.append("psh_%s~%d" % (_shape(words[i - 1]) if i > 0 else "<S>", tag))
    return fs
def _spans(tags):
    sp = set(); i = 0; n = len(tags)
    while i < n:
        t = tags[i]
        if t > 0 and t % 2 == 1:
            j = i + 1
            while j < n and tags[j] == t + 1: j += 1
            sp.add((i, j, (t - 1) // 2)); i = j
        else: i += 1
    return sp
def _selftest():
    assert _spans([0, 1, 2, 0]) == {(1, 3, 0)} and _shape("Bob") == "Cap"
    print("[selftest] PASS: ner-discriminative", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "2028")))
    try:
        data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "f1": 0.0}
    train = [(toks, tags) for toks, tags in data["train"] if toks]
    test = [(toks, tags) for toks, tags in data["test"] if toks]
    if SMOKE: train = train[:300]; test = test[:150]
    train = [(t, g) for t, g in train if len(t) <= 60]; test = [(t, g) for t, g in test if len(t) <= 60]
    TAGS = sorted({t for _w, g in train for t in g}); ti = {t: k for k, t in enumerate(TAGS)}; T = len(TAGS)
    w = defaultdict(float); cw = defaultdict(float); c = 1
    def tt(pt, t): return "tt_%d~%d" % (pt, t)
    def viterbi(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit_feats(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt(-1, TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]
    EP = 6 if not SMOKE else 3
    for ep in range(EP):
        for si in rng.permutation(len(train)):
            words, gold = train[si]; pred = viterbi(words, w)
            if pred != gold:
                pg = -1; pp = -1
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _emit_feats(words, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in _emit_feats(words, i, pred[i]): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    tp = fp = fn = 0
    for words, gold in test:
        pred = viterbi(words, avg); gs = _spans(gold); ps = _spans(pred)
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); f1 = 2 * prec * rec / (prec + rec + 1e-9)
    print("  NER-DISCRIMINATIVE: entity-F1=%.4f (P=%.3f R=%.3f) | train=%d sents, %d tags, %d entity-types" %
          (f1, prec, rec, len(train), T, T // 2), flush=True)
    return {"f1": round(f1, 4), "prec": round(prec, 3), "rec": round(rec, 3), "n_train": len(train), "n_tags": T}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    f1 = r["f1"]; s = "entity-F1=%.4f (P=%.3f R=%.3f, train=%d)" % (f1, r["prec"], r["rec"], r["n_train"])
    if f1 >= 0.75:
        return ("HARD_PASS", "HARD_PASS: discriminative structured-perceptron NER >=0.75 entity-F1 on OntoNotes -- 5th task confirming the universal discriminative-weighting lever; substrate-classical NER, no LLM. " + s)
    if f1 >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: NER F1 0.65-0.75 -- strong; richer features/gazetteers/more data for 0.80+. " + s)
    return ("HARD_FAIL", "HARD_FAIL: NER F1 <0.55. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
