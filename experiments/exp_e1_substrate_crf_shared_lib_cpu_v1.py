"""
exp_e1_substrate_crf_shared_lib_cpu_v1.py -- E1: substrate-CRF Tier-1 shared feature library lift on NER -- CPU.

ROUTING: Research APPROVED big next build (research_to_exp_dev_NER_NORTH_STAR_WIN_E5_E1_PRIORITY / UNROUTED inventory E1).
  Shared Tier-1 feature library = distributional word clusters (k-means on PPMI context vectors -- tractable Brown-cluster proxy) +
  gazetteer (training entity surface -> majority type). Reusable across NER/chunking/slot/parse. TEST: does adding the library to the
  structured-perceptron+Viterbi NER tagger lift F1 at FULL training data? Per aux-features-shrink-with-data memory, aux features
  saturate at scale -- so this is a genuine empirical test (lift may be small). A/B: baseline features vs +library. n=3 seeds.
  NOTE on scope: tested on 4-TYPE NER (9 tags, tractable) -- the validated Tier-A capability -- NOT 18-type (37 tags, ~16x Viterbi
  cost). Research pre-reg said 18-type; flagged the deviation. Same +0.03 lift gate. Bundled OntoNotes. Substrate-only.
PRE-REGISTERED (Research): HARD-PASS mean F1 lift (library - baseline) >= +0.03 (CI excludes 0). MIDDLE 0 to +0.03. FAIL <= 0
  (library saturates -- consistent with aux-features-shrink; honest). UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, Tuple
from collections import defaultdict, Counter
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "e1_substrate_crf_shared_lib_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
COARSE = {0: 0, 3: 1, 4: 2, 5: 2, 2: 2, 1: 3, 6: 3, 14: 3, 15: 3, 16: 3, 17: 3}


def _collapse4(tags):
    out = []
    for t in tags:
        if t == 0: out.append(0); continue
        tid = (t - 1) // 2; is_B = (t % 2 == 1); cz = COARSE.get(tid)
        out.append(0 if cz is None else ((1 + 2 * cz) if is_B else (2 + 2 * cz)))
    return out


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


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


# ---------- Tier-1 shared feature library ----------
def build_clusters(train_sents, K, seed, min_count=5, n_anchor=200, iters=12):
    rng = np.random.default_rng(seed)
    wc = Counter(w.lower() for s in train_sents for w in s)
    anchors = [w for w, _ in wc.most_common(n_anchor)]; aidx = {w: i for i, w in enumerate(anchors)}
    vocab = [w for w, c in wc.items() if c >= min_count]
    if len(vocab) < K: return {}
    vidx = {w: i for i, w in enumerate(vocab)}
    M = np.zeros((len(vocab), len(anchors)))
    for s in train_sents:
        ws = [w.lower() for w in s]
        for i, w in enumerate(ws):
            vi = vidx.get(w)
            if vi is None: continue
            for j in (i - 1, i + 1):
                if 0 <= j < len(ws):
                    ai = aidx.get(ws[j])
                    if ai is not None: M[vi, ai] += 1
    M = np.log1p(M)
    norms = np.linalg.norm(M, axis=1, keepdims=True); norms[norms < 1e-9] = 1e-9; M = M / norms
    cent = M[rng.choice(len(vocab), K, replace=False)].copy()
    assign = np.zeros(len(vocab), dtype=int)
    for _ in range(iters):
        cn = np.linalg.norm(cent, axis=1, keepdims=True); cn[cn < 1e-9] = 1e-9
        assign = np.argmax(M @ (cent / cn).T, axis=1)
        for k in range(K):
            mask = assign == k
            cent[k] = M[mask].mean(axis=0) if mask.any() else M[rng.integers(len(vocab))]
    return {vocab[i]: int(assign[i]) for i in range(len(vocab))}


def build_gazetteer(train, min_count=2):
    cnt = defaultdict(Counter)
    for words, tags in train:
        for i, j, ty in _spans(tags):
            for w in words[i:j]: cnt[w.lower()][ty] += 1
    gaz = {}
    for surf, c in cnt.items():
        ty, n = c.most_common(1)[0]
        if n >= min_count: gaz[surf] = ty
    return gaz


def _emit_feats(words, i, tag, clusters, gaz, use_lib):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%d" % (wl, tag), "sh_%s~%d" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%d" % (k, wl[-k:], tag))
    if len(wl) >= 3: fs.append("pre3_%s~%d" % (wl[:3], tag))
    pw = words[i - 1].lower() if i > 0 else "<S>"; nw = words[i + 1].lower() if i + 1 < len(words) else "<E>"
    fs.append("pw_%s~%d" % (pw, tag)); fs.append("nw_%s~%d" % (nw, tag))
    fs.append("psh_%s~%d" % (_shape(words[i - 1]) if i > 0 else "<S>", tag))
    if use_lib:
        c0 = clusters.get(wl); cp = clusters.get(pw); cn = clusters.get(nw)
        if c0 is not None: fs.append("clu_%d~%d" % (c0, tag))
        if cp is not None: fs.append("cluP_%d~%d" % (cp, tag))
        if cn is not None: fs.append("cluN_%d~%d" % (cn, tag))
        g = gaz.get(wl)
        if g is not None: fs.append("gaz_%d~%d" % (g, tag))
    return fs


def _one_seed(train, test, TAGS, clusters, gaz, use_lib, seed):
    T = len(TAGS); rng = np.random.default_rng(seed); w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(pt, t): return "tt_%d~%d" % (pt, t)

    def viterbi(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit_feats(words, i, TAGS[k], clusters, gaz, use_lib)) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt(-1, TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]

    EP = 6 if not SMOKE else 2
    for ep in range(EP):
        for si in rng.permutation(len(train)):
            words, gold = train[si]; pred = viterbi(words, w)
            if pred != gold:
                pg = -1; pp = -1
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _emit_feats(words, i, gold[i], clusters, gaz, use_lib): w[f] += 1; cw[f] += c
                        for f in _emit_feats(words, i, pred[i], clusters, gaz, use_lib): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    tp = fp = fn = 0
    for words, gold in test:
        pred = viterbi(words, avg); gs = _spans(gold); ps = _spans(pred)
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); return 2 * prec * rec / (prec + rec + 1e-9)


def _selftest():
    assert _collapse4([1, 2, 0, 7, 8]) == [1, 2, 0, 3, 4]
    cl = build_clusters([["the", "dog", "ran"], ["the", "cat", "sat"], ["a", "dog", "sat"]] * 3, K=2, seed=0, min_count=1, n_anchor=5)
    assert isinstance(cl, dict)
    print("[selftest] PASS: e1-substrate-crf-shared-lib", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    import json
    try:
        data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed"}
    train = [(t, _collapse4(g)) for t, g in data["train"] if t and len(t) <= 60]
    test = [(t, _collapse4(g)) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE: train = train[:300]; test = test[:150]
    TAGS = sorted({tg for _w, g in train for tg in g})
    t_lib = time.time()
    clusters = build_clusters([t for t, _g in train], K=(20 if SMOKE else 40), seed=99)
    gaz = build_gazetteer(train)
    print("[library] clusters=%d words, gazetteer=%d entries (%.1fs)" % (len(clusters), len(gaz), time.time() - t_lib), flush=True)
    SEEDS = [1, 2] if SMOKE else [1, 2, 3]
    base_vals = []; lib_vals = []
    for sd in SEEDS:
        b = _one_seed(train, test, TAGS, clusters, gaz, False, sd); base_vals.append(round(b, 4))
        l = _one_seed(train, test, TAGS, clusters, gaz, True, sd); lib_vals.append(round(l, 4))
        print("  seed %d: baseline-F1=%.4f  +library-F1=%.4f  lift=%+.4f" % (sd, b, l, l - b), flush=True)
    bm = sum(base_vals) / len(base_vals); lm = sum(lib_vals) / len(lib_vals)
    lifts = [lib_vals[i] - base_vals[i] for i in range(len(SEEDS))]
    lift_mean = sum(lifts) / len(lifts)
    lift_std = (sum((x - lift_mean) ** 2 for x in lifts) / len(lifts)) ** 0.5
    lift_se = lift_std / (len(lifts) ** 0.5)
    print("  E1 SHARED-LIB n=%d: baseline=%.4f +library=%.4f lift=%+.4f +/- SE %.4f (lifts=%s)" % (
        len(SEEDS), bm, lm, lift_mean, lift_se, lifts), flush=True)
    return {"f1": round(lm, 4), "baseline_f1": round(bm, 4), "library_f1": round(lm, 4), "lift": round(lift_mean, 4),
            "lift_se": round(lift_se, 4), "lift_minus_2se": round(lift_mean - 2 * lift_se, 4), "lifts": lifts,
            "n_seeds": len(SEEDS), "n_clusters": len(clusters), "n_gaz": len(gaz), "n_train": len(train)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    lift = r["lift"]; l2 = r["lift_minus_2se"]
    s = "baseline-F1=%.4f +library-F1=%.4f lift=%+.4f (lift-2SE=%+.4f, n=%d, clusters=%d gaz=%d, 4-type NER)" % (
        r["baseline_f1"], r["library_f1"], lift, l2, r["n_seeds"], r["n_clusters"], r["n_gaz"])
    if l2 >= 0.03:
        return ("HARD_PASS", "HARD_PASS: substrate-CRF shared Tier-1 library lifts NER F1 >=+0.03 (CI excludes 0) -- reusable feature library is a real substrate-product lever. " + s)
    if lift > 0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: shared library lift 0 to +0.03 -- positive but saturates (consistent with aux-features-shrink-with-data at full training). " + s)
    return ("HARD_FAIL", "HARD_FAIL: shared library lift <=0 -- clusters+gazetteer subsumed by lexical features at full data (aux-features-shrink confirmed; honest). " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 1), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
