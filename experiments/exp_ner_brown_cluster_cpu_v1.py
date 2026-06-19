"""
exp_ner_brown_cluster_cpu_v1.py -- NER Path 2: distributional word-cluster (Brown-style) features -- CPU.

ROUTING: Research Action 2 (research_to_exp_dev_NER_PATH1_REFUTED_FEATURES_NEXT). Diagnostics showed NER caps ~0.65 regardless of
  type granularity (18-type 0.582 / 4-type CoNLL 0.648 / single-type boundary 0.664) and the decoder is non-bottleneck (hard-BIO
  lift -0.012). So the lever is FEATURES. Path 2: add distributional word-cluster features (poor-man's Brown clusters, computed
  in-corpus, substrate-native, no external embeddings). Each word -> a feature-hashed context vector (prev/next word counts) ->
  numpy k-means into C clusters; cluster-id of word + prev + next become emission features. Cluster generalizes rare entity words
  ("Inc/Corp/Ltd", weekday names) to a shared class. Re-run the SAME structured-perceptron Viterbi on OntoNotes 18-type.
PRE-REGISTERED: report F1 with cluster features vs the 0.5817 baseline (same cell minus clusters). HARD-PASS F1 >= 0.62 AND
  lift >= 0.02 (clusters are a real feature lever; stack Path 5). MIDDLE lift in [0.005,0.02). HARD-FAIL lift < 0.005 (clusters
  add nothing; deeper feature work needed). UNKNOWN if load fails. NO pre-registered defeat (drill-defeatism).
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
from collections import defaultdict, Counter
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "ner_brown_cluster_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
F1_BASELINE = 0.5817
CDIM = 256   # context-vector hashing dim
NCLUST = 48  # number of word clusters


def _h(s, mod):
    return zlib.crc32(s.encode("utf-8")) % mod


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


def build_clusters(sents, seed):
    """In-corpus distributional clustering: word -> hashed context vec -> k-means -> cluster id. Returns dict word->cluster."""
    ctx = defaultdict(lambda: np.zeros(CDIM, dtype=np.float64)); freq = Counter()
    for toks, _g in sents:
        n = len(toks)
        for i, wtok in enumerate(toks):
            wl = wtok.lower(); freq[wl] += 1
            pv = toks[i - 1].lower() if i > 0 else "<S>"; nx = toks[i + 1].lower() if i + 1 < n else "<E>"
            ctx[wl][_h("L=" + pv, CDIM)] += 1.0; ctx[wl][_h("R=" + nx, CDIM)] += 1.0
    vocab = [w for w in ctx if freq[w] >= 2]
    if len(vocab) < NCLUST:
        return {}, 0
    M = np.stack([ctx[w] for w in vocab])
    M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    rng = np.random.default_rng(seed)
    cent = M[rng.choice(len(vocab), NCLUST, replace=False)].copy()
    for _it in range(8 if not SMOKE else 3):
        sims = M @ cent.T                      # cosine (rows are unit-norm; centroids ~unit)
        assign = np.argmax(sims, axis=1)
        for k in range(NCLUST):
            mask = assign == k
            if mask.any():
                v = M[mask].mean(axis=0); nv = v / (np.linalg.norm(v) + 1e-9); cent[k] = nv
    sims = M @ cent.T; assign = np.argmax(sims, axis=1)
    return {w: int(assign[i]) for i, w in enumerate(vocab)}, len(vocab)


CLUSTERS: Dict[str, int] = {}


def _clu(w):
    return CLUSTERS.get(w.lower(), -1)


def _emit_feats(words, i, tag, use_clusters):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%d" % (wl, tag), "sh_%s~%d" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%d" % (k, wl[-k:], tag))
    if len(wl) >= 3: fs.append("pre3_%s~%d" % (wl[:3], tag))
    fs.append("pw_%s~%d" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%d" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    fs.append("psh_%s~%d" % (_shape(words[i - 1]) if i > 0 else "<S>", tag))
    if use_clusters:
        fs.append("cl_%d~%d" % (_clu(w), tag))
        fs.append("pcl_%d~%d" % (_clu(words[i - 1]) if i > 0 else -2, tag))
        fs.append("ncl_%d~%d" % (_clu(words[i + 1]) if i + 1 < len(words) else -2, tag))
        fs.append("clsh_%d_%s~%d" % (_clu(w), _shape(w), tag))
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
    assert _spans([0, 1, 2, 0]) == {(1, 3, 0)} and _shape("Bob") == "Cap" and _h("x", 16) < 16
    print("[selftest] PASS: ner-brown-cluster", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _train_eval(train, test, TAGS, use_clusters, seed):
    global CLUSTERS
    T = len(TAGS); rng = np.random.default_rng(seed)
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(pt, t): return "tt_%d~%d" % (pt, t)

    def viterbi(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit_feats(words, i, TAGS[k], use_clusters)) for k in range(T)] for i in range(n)])
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
                        for f in _emit_feats(words, i, gold[i], use_clusters): w[f] += 1; cw[f] += c
                        for f in _emit_feats(words, i, pred[i], use_clusters): w[f] -= 1; cw[f] -= c
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
    return f1, prec, rec


def run() -> Dict:
    global CLUSTERS
    try:
        data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "f1": 0.0}
    train = [(t, g) for t, g in data["train"] if t and len(t) <= 60]
    test = [(t, g) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE: train = train[:300]; test = test[:150]
    TAGS = sorted({t for _w, g in train for t in g}); seed = int(os.environ.get("HDLAB_SEED", "1028"))
    CLUSTERS, nvocab = build_clusters(train, seed)
    print("  [clusters] %d words clustered into %d groups" % (nvocab, NCLUST), flush=True)
    fb, pb, rb = _train_eval(train, test, TAGS, use_clusters=False, seed=seed)
    print("  [no-cluster baseline] F1=%.4f (P=%.3f R=%.3f)" % (fb, pb, rb), flush=True)
    fc, pc, rc = _train_eval(train, test, TAGS, use_clusters=True, seed=seed)
    print("  [+cluster features]   F1=%.4f (P=%.3f R=%.3f)" % (fc, pc, rc), flush=True)
    lift = fc - fb
    print("  LIFT (cluster - baseline) = %+.4f | vs reference 0.5817 | train=%d test=%d" % (lift, len(train), len(test)), flush=True)
    return {"f1": round(fc, 4), "f1_cluster": round(fc, 4), "f1_baseline": round(fb, 4), "lift": round(lift, 4),
            "prec": round(pc, 3), "rec": round(rc, 3), "n_train": len(train), "n_clusters": NCLUST, "n_vocab": nvocab}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    fc = r["f1_cluster"]; fb = r["f1_baseline"]; lift = r["lift"]
    s = "+cluster F1=%.4f vs no-cluster %.4f (lift=%+.4f, P=%.3f R=%.3f, %d clusters/%d vocab, train=%d)" % (fc, fb, lift, r["prec"], r["rec"], r["n_clusters"], r["n_vocab"], r["n_train"])
    if fc >= 0.62 and lift >= 0.02:
        return ("HARD_PASS", "HARD_PASS: distributional word-cluster (Brown-style) features lift NER >=0.02 to F1>=0.62 -- features ARE the lever (confirms Path 2); substrate-native in-corpus clusters, no external embeddings. Stack Path 5 phrase-clusters. " + s)
    if lift >= 0.005:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cluster features give a small lift (>=0.005) -- partial; combine with richer/larger clusters or phrase features. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cluster features add nothing (lift<0.005) -- in-corpus distributional clusters insufficient; need external embeddings or larger corpus for the feature lever. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
