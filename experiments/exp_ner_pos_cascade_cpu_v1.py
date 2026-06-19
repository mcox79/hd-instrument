"""
exp_ner_pos_cascade_cpu_v1.py -- NER Path 3: POS-cascade features (substrate POS tagger -> NER feature) -- CPU.

ROUTING: Research Path 3 (cascade NER via the substrate POS tagger). NER feature levers so far: decoder (Path 1) -0.012; in-corpus
  Brown clusters (Path 2) +0.011. The current NER feature set has NO POS feature, yet POS is classically one of the strongest NER
  features and the substrate has a 0.95 POS tagger. Cascade: train a structured-perceptron POS tagger on UD-EWT (17 universal tags),
  predict POS for every OntoNotes token, and add predicted-POS features (pos, prev/next pos, pos+shape) to the NER emission. Train
  TWO NER models from identical base features: no-POS (= baseline 0.5817) vs +POS-cascade. Report lift. Substrate-only.
PRE-REGISTERED (NO defeat): HARD-PASS F1 >= 0.62 AND lift >= 0.02 (POS cascade is a real lever; stack with clusters). MIDDLE lift in
  [0.005,0.02). HARD-FAIL lift < 0.005. UNKNOWN if load fails.
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
from typing import Dict, Tuple, List
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from _ud_loader import load_conllu
ANCHOR_NAME = "ner_pos_cascade_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
F1_BASELINE = 0.5817


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


# ---------- POS tagger (structured perceptron on UD) ----------
def _pos_emit(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%s" % (k, wl[-k:], tag))
    fs.append("pw_%s~%s" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%s" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    return fs


def train_pos_tagger():
    tr = [s for s in load_conllu("train") if 1 <= len(s) <= 40]
    if not SMOKE: tr = tr[:2500]
    else: tr = tr[:300]
    train = [([t[1] for t in s], [t[2] for t in s]) for s in tr]
    TAGS = sorted({t for _w, g in train for t in g}); T = len(TAGS); rng = np.random.default_rng(7)
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "ptt_%s~%s" % (p, t)

    def viterbi(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _pos_emit(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt("<S>", TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]

    for ep in range(5 if not SMOKE else 2):
        for si in rng.permutation(len(train)):
            words, gold = train[si]; pred = viterbi(words, w)
            if pred != gold:
                pg = "<S>"; pp = "<S>"
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _pos_emit(words, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in _pos_emit(words, i, pred[i]): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    return lambda words: viterbi(words, avg)


# ---------- NER (structured perceptron with optional POS features) ----------
POSMAP: dict = {}  # sentence-tuple-id -> list of predicted POS (filled before training)


def _ner_emit(words, i, tag, pos, use_pos):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%d" % (wl, tag), "sh_%s~%d" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%d" % (k, wl[-k:], tag))
    if len(wl) >= 3: fs.append("pre3_%s~%d" % (wl[:3], tag))
    fs.append("pw_%s~%d" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%d" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    fs.append("psh_%s~%d" % (_shape(words[i - 1]) if i > 0 else "<S>", tag))
    if use_pos and pos is not None:
        fs.append("pos_%s~%d" % (pos[i], tag))
        fs.append("ppos_%s~%d" % (pos[i - 1] if i > 0 else "<S>", tag))
        fs.append("npos_%s~%d" % (pos[i + 1] if i + 1 < len(words) else "<E>", tag))
        fs.append("possh_%s_%s~%d" % (pos[i], _shape(w), tag))
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
    print("[selftest] PASS: ner-pos-cascade", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _train_eval_ner(train, test, TAGS, use_pos, seed):
    T = len(TAGS); rng = np.random.default_rng(seed)
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "tt_%d~%d" % (p, t)

    def viterbi(words, pos, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _ner_emit(words, i, TAGS[k], pos, use_pos)) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt(-1, TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]

    for ep in range(6 if not SMOKE else 3):
        for si in rng.permutation(len(train)):
            words, gold, pos = train[si]; pred = viterbi(words, pos, w)
            if pred != gold:
                pg = -1; pp = -1
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _ner_emit(words, i, gold[i], pos, use_pos): w[f] += 1; cw[f] += c
                        for f in _ner_emit(words, i, pred[i], pos, use_pos): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    tp = fp = fn = 0
    for words, gold, pos in test:
        pred = viterbi(words, pos, avg); gs = _spans(gold); ps = _spans(pred)
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); f1 = 2 * prec * rec / (prec + rec + 1e-9)
    return f1, prec, rec


def run() -> Dict:
    try:
        data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "f1": 0.0}
    tagger = train_pos_tagger()
    print("  [pos] UD POS tagger trained", flush=True)
    tr = [(t, g) for t, g in data["train"] if t and len(t) <= 60]
    te = [(t, g) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE: tr = tr[:300]; te = te[:150]
    train = [(t, g, tagger(t)) for t, g in tr]; test = [(t, g, tagger(t)) for t, g in te]
    print("  [pos] predicted POS for %d train + %d test sents" % (len(train), len(test)), flush=True)
    TAGS = sorted({tg for _w, g, _p in train for tg in g}); seed = int(os.environ.get("HDLAB_SEED", "1028"))
    fb, pb, rb = _train_eval_ner(train, test, TAGS, use_pos=False, seed=seed)
    print("  [no-POS baseline] F1=%.4f (P=%.3f R=%.3f)" % (fb, pb, rb), flush=True)
    fp_, pp_, rp_ = _train_eval_ner(train, test, TAGS, use_pos=True, seed=seed)
    print("  [+POS cascade]    F1=%.4f (P=%.3f R=%.3f)" % (fp_, pp_, rp_), flush=True)
    lift = fp_ - fb
    print("  LIFT (POS - baseline) = %+.4f | vs reference 0.5817 | train=%d test=%d" % (lift, len(train), len(test)), flush=True)
    return {"f1": round(fp_, 4), "f1_pos": round(fp_, 4), "f1_baseline": round(fb, 4), "lift": round(lift, 4),
            "prec": round(pp_, 3), "rec": round(rp_, 3), "n_train": len(train)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    fp_ = r["f1_pos"]; fb = r["f1_baseline"]; lift = r["lift"]
    s = "+POS F1=%.4f vs no-POS %.4f (lift=%+.4f, P=%.3f R=%.3f, train=%d)" % (fp_, fb, lift, r["prec"], r["rec"], r["n_train"])
    if fp_ >= 0.62 and lift >= 0.02:
        return ("HARD_PASS", "HARD_PASS: POS-cascade features lift NER >=0.02 to F1>=0.62 -- the substrate POS tagger is a real NER feature lever (Path 3); cascade substrate-strength into NER. " + s)
    if lift >= 0.005:
        return ("MIDDLE_BAND", "MIDDLE_BAND: POS cascade gives a small lift (>=0.005) -- partial; combine with clusters (Path 2 +0.011) for a stacked feature gain. " + s)
    return ("HARD_FAIL", "HARD_FAIL: POS cascade adds nothing (lift<0.005) -- cross-corpus POS (UD->OntoNotes) not informative for NER here. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
