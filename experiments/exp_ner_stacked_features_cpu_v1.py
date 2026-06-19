"""
exp_ner_stacked_features_cpu_v1.py -- NER: STACK Brown clusters + POS-cascade features -- CPU.

ROUTING: complete the NER feature program. Individually at full data: in-corpus Brown clusters (Path 2) +0.011; POS cascade
  (Path 3) +0.013. This stacks BOTH on the same structured-perceptron NER to get the best-achievable IN-CORPUS substrate NER (do
  the small gains add, or saturate?). Train TWO models from identical base features: baseline (word/affix/shape/context only) vs
  stacked (+ cluster-id + predicted-POS features). OntoNotes 18-type. Substrate-only, no external resources.
PRE-REGISTERED (NO defeat): report stacked F1 + lift vs 0.5817 baseline. HARD-PASS F1 >= 0.62 AND lift >= 0.025 (stacked features
  meaningfully add). MIDDLE lift in [0.01,0.025). HARD-FAIL lift < 0.01 (features saturate; external resources needed). UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, zlib
from pathlib import Path
from typing import Dict, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from _ud_loader import load_conllu
ANCHOR_NAME = "ner_stacked_features_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
F1_BASELINE = 0.5817
CDIM = 256; NCLUST = 48
CLUSTERS: Dict[str, int] = {}


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


def _clu(w): return CLUSTERS.get(w.lower(), -1)


def build_clusters(sents, seed):
    ctx = defaultdict(lambda: np.zeros(CDIM)); freq = defaultdict(int)
    for toks, _g in sents:
        n = len(toks)
        for i, wtok in enumerate(toks):
            wl = wtok.lower(); freq[wl] += 1
            pv = toks[i - 1].lower() if i > 0 else "<S>"; nx = toks[i + 1].lower() if i + 1 < n else "<E>"
            ctx[wl][zlib.crc32(("L=" + pv).encode()) % CDIM] += 1.0; ctx[wl][zlib.crc32(("R=" + nx).encode()) % CDIM] += 1.0
    vocab = [w for w in ctx if freq[w] >= 2]
    if len(vocab) < NCLUST: return {}, 0
    M = np.stack([ctx[w] for w in vocab]); M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    rng = np.random.default_rng(seed); cent = M[rng.choice(len(vocab), NCLUST, replace=False)].copy()
    for _it in range(8 if not SMOKE else 3):
        assign = np.argmax(M @ cent.T, axis=1)
        for k in range(NCLUST):
            mask = assign == k
            if mask.any(): v = M[mask].mean(axis=0); cent[k] = v / (np.linalg.norm(v) + 1e-9)
    assign = np.argmax(M @ cent.T, axis=1)
    return {w: int(assign[i]) for i, w in enumerate(vocab)}, len(vocab)


# POS tagger on UD
def _pos_emit(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%s" % (k, wl[-k:], tag))
    fs.append("pw_%s~%s" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%s" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    return fs


def train_pos_tagger():
    tr = [s for s in load_conllu("train") if 1 <= len(s) <= 40]
    tr = tr[:300] if SMOKE else tr[:2500]
    train = [([t[1] for t in s], [t[2] for t in s]) for s in tr]
    TAGS = sorted({t for _w, g in train for t in g}); T = len(TAGS); rng = np.random.default_rng(7)
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "ptt_%s~%s" % (p, t)

    def vit(words, weights):
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
            words, gold = train[si]; pred = vit(words, w)
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
    return lambda words: vit(words, avg)


def _ner_emit(words, i, tag, pos, stacked):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%d" % (wl, tag), "sh_%s~%d" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%d" % (k, wl[-k:], tag))
    if len(wl) >= 3: fs.append("pre3_%s~%d" % (wl[:3], tag))
    fs.append("pw_%s~%d" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%d" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    fs.append("psh_%s~%d" % (_shape(words[i - 1]) if i > 0 else "<S>", tag))
    if stacked:
        fs.append("cl_%d~%d" % (_clu(w), tag))
        fs.append("pcl_%d~%d" % (_clu(words[i - 1]) if i > 0 else -2, tag))
        fs.append("ncl_%d~%d" % (_clu(words[i + 1]) if i + 1 < len(words) else -2, tag))
        if pos is not None:
            fs.append("pos_%s~%d" % (pos[i], tag))
            fs.append("ppos_%s~%d" % (pos[i - 1] if i > 0 else "<S>", tag))
            fs.append("npos_%s~%d" % (pos[i + 1] if i + 1 < len(words) else "<E>", tag))
            fs.append("possh_%s_%s~%d" % (pos[i], _shape(w), tag))
            fs.append("poscl_%s_%d~%d" % (pos[i], _clu(w), tag))
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
    print("[selftest] PASS: ner-stacked-features", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _train_eval(train, test, TAGS, stacked, seed):
    T = len(TAGS); rng = np.random.default_rng(seed)
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "tt_%d~%d" % (p, t)

    def vit(words, pos, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _ner_emit(words, i, TAGS[k], pos, stacked)) for k in range(T)] for i in range(n)])
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
            words, gold, pos = train[si]; pred = vit(words, pos, w)
            if pred != gold:
                pg = -1; pp = -1
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _ner_emit(words, i, gold[i], pos, stacked): w[f] += 1; cw[f] += c
                        for f in _ner_emit(words, i, pred[i], pos, stacked): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    tp = fp = fn = 0
    for words, gold, pos in test:
        pred = vit(words, pos, avg); gs = _spans(gold); ps = _spans(pred)
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); f1 = 2 * prec * rec / (prec + rec + 1e-9)
    return f1, prec, rec


def run() -> Dict:
    global CLUSTERS
    try:
        data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "f1": 0.0}
    tagger = train_pos_tagger(); print("  [pos] UD tagger trained", flush=True)
    tr = [(t, g) for t, g in data["train"] if t and len(t) <= 60]
    te = [(t, g) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE: tr = tr[:300]; te = te[:150]
    seed = int(os.environ.get("HDLAB_SEED", "1028"))
    CLUSTERS, nvocab = build_clusters(tr, seed); print("  [clusters] %d words -> %d groups" % (nvocab, NCLUST), flush=True)
    train = [(t, g, tagger(t)) for t, g in tr]; test = [(t, g, tagger(t)) for t, g in te]
    TAGS = sorted({tg for _w, g, _p in train for tg in g})
    fb, pb, rb = _train_eval(train, test, TAGS, stacked=False, seed=seed)
    print("  [baseline]        F1=%.4f (P=%.3f R=%.3f)" % (fb, pb, rb), flush=True)
    fs, ps, rs = _train_eval(train, test, TAGS, stacked=True, seed=seed)
    print("  [+clusters+POS]   F1=%.4f (P=%.3f R=%.3f)" % (fs, ps, rs), flush=True)
    lift = fs - fb
    print("  STACKED LIFT = %+.4f | vs reference 0.5817 | train=%d test=%d" % (lift, len(train), len(test)), flush=True)
    return {"f1": round(fs, 4), "f1_stacked": round(fs, 4), "f1_baseline": round(fb, 4), "lift": round(lift, 4),
            "prec": round(ps, 3), "rec": round(rs, 3), "n_train": len(train), "n_vocab": nvocab}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    fs = r["f1_stacked"]; fb = r["f1_baseline"]; lift = r["lift"]
    s = "stacked(clusters+POS) F1=%.4f vs baseline %.4f (lift=%+.4f, P=%.3f R=%.3f, train=%d)" % (fs, fb, lift, r["prec"], r["rec"], r["n_train"])
    if fs >= 0.62 and lift >= 0.025:
        return ("HARD_PASS", "HARD_PASS: stacked in-corpus features (clusters+POS) lift NER >=0.025 to F1>=0.62 -- the small per-lever gains ADD; best in-corpus substrate NER. " + s)
    if lift >= 0.01:
        return ("MIDDLE_BAND", "MIDDLE_BAND: stacked lift 0.01-0.025 -- features partially add but largely SATURATE at full data (lexical features subsume most signal); best in-corpus substrate NER ~F1. External resources (embeddings/large-corpus clusters) needed to break ~0.66. " + s)
    return ("HARD_FAIL", "HARD_FAIL: stacked lift <0.01 -- in-corpus features fully saturate; the lexical features already capture the signal. External resources required. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
