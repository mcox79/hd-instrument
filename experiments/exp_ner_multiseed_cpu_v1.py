"""
exp_ner_multiseed_cpu_v1.py -- NER structured-perceptron multi-seed (Tier-B error bar) -- CPU.

ROUTING: Research NER Path 2 (multi-seed promotion). The NER baseline 0.5817 was single-seed. Run the structured-perceptron NER at
  n=5 seeds; report mean +/- std for the honest error-barred substrate-NER number (OntoNotes 18-type). Substrate-only.
PRE-REGISTERED: report mean/std. HARD-PASS mean >= 0.58 AND std <= 0.01 (stable Tier-B substrate NER). MIDDLE mean >= 0.55.
  HARD-FAIL mean < 0.55. UNKNOWN if load fails.
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
from typing import Dict, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "ner_multiseed_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
SEEDS = [1, 2, 3] if SMOKE else [1, 2, 3, 4, 5]


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


def _emit(words, i, tag):
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
    print("[selftest] PASS: ner-multiseed", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _train_eval(train, test, TAGS, seed):
    T = len(TAGS); rng = np.random.default_rng(seed)
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "tt_%d~%d" % (p, t)

    def vit(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
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
            words, gold = train[si]; pred = vit(words, w)
            if pred != gold:
                pg = -1; pp = -1
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _emit(words, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in _emit(words, i, pred[i]): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    tp = fp = fn = 0
    for words, gold in test:
        pred = vit(words, avg); gs = _spans(gold); ps = _spans(pred)
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); return 2 * prec * rec / (prec + rec + 1e-9)


def run() -> Dict:
    try:
        data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    train = [(t, g) for t, g in data["train"] if t and len(t) <= 60]
    test = [(t, g) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE: train = train[:300]; test = test[:150]
    TAGS = sorted({t for _w, g in train for t in g})
    vals = [round(_train_eval(train, test, TAGS, sd), 4) for sd in SEEDS]
    mean = sum(vals) / len(vals); std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
    print("  NER n=%d: mean-F1=%.4f std=%.4f vals=%s | OntoNotes 18-type, train=%d test=%d" % (len(vals), mean, std, vals, len(train), len(test)), flush=True)
    return {"accuracy": round(mean, 4), "std": round(std, 4), "vals": vals, "n_seeds": len(vals), "n_train": len(train)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    m = r["accuracy"]; sd = r["std"]; s = "mean-F1=%.4f std=%.4f (n=%d, vals=%s)" % (m, sd, r["n_seeds"], r["vals"])
    if m >= 0.58 and sd <= 0.01:
        return ("HARD_PASS", "HARD_PASS: substrate NER stable at mean-F1>=0.58 std<=0.01 -- honest Tier-B substrate NER on OntoNotes-18 (error-barred). CoNLL-equivalent remains the 0.648 primary. " + s)
    if m >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: NER mean-F1 0.55-0.58. " + s)
    return ("HARD_FAIL", "HARD_FAIL: NER mean-F1 <0.55. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 1), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
