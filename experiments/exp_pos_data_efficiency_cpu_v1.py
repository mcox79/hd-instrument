"""
exp_pos_data_efficiency_cpu_v1.py -- substrate POS tagger DATA-EFFICIENCY curve (low-data advantage) -- CPU.

ROUTING: deepen the substrate WINS per Research (aux-features-shrink discovery -> substrate features LOW-DATA optimal positioning).
  Quantify the substrate's data efficiency on its STRONGEST capability (POS structured prediction, full-data 0.95). Train the
  discriminative structured-perceptron POS tagger at increasing train sizes [25,50,100,250,500,1000,2500] sentences and report
  tag accuracy at each -- the data-efficiency curve. Commercial value: niche domains / few-shot / small-corpus where the substrate
  reaches high accuracy with few examples. UD-EWT 17 universal tags. Substrate-only, no LLM.
PRE-REGISTERED: HARD-PASS substrate POS >= 0.90 with <= 250 train sentences (strong low-data efficiency). MIDDLE >= 0.90 by 1000.
  HARD-FAIL needs > 1000 for 0.90. UNKNOWN if load fails. Reports the full curve.
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
from typing import Dict, Tuple, List
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from _ud_loader import load_conllu
ANCHOR_NAME = "pos_data_efficiency_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
SIZES = [25, 50, 100] if SMOKE else [25, 50, 100, 250, 500, 1000, 2500]


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


def _emit(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%s" % (k, wl[-k:], tag))
    fs.append("pw_%s~%s" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%s" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    return fs


def _train(train, TAGS, epochs):
    T = len(TAGS); rng = np.random.default_rng(7)
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "tt_%s~%s" % (p, t)

    def vit(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt("<S>", TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]

    for ep in range(epochs):
        for si in rng.permutation(len(train)):
            words, gold = train[si]; pred = vit(words, w)
            if pred != gold:
                pg = "<S>"; pp = "<S>"
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _emit(words, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in _emit(words, i, pred[i]): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    return {f: w[f] - cw[f] / c for f in w}, vit


def _selftest():
    assert _shape("Bob") == "Cap" and "w_bob~NOUN" in _emit(["Bob"], 0, "NOUN")
    print("[selftest] PASS: pos-data-efficiency", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    tr_all = [s for s in load_conllu("train") if 1 <= len(s) <= 40]
    te = [s for s in load_conllu("test") if 1 <= len(s) <= 40]
    if SMOKE: te = te[:150]
    train_all = [([t[1] for t in s], [t[2] for t in s]) for s in tr_all]
    test = [([t[1] for t in s], [t[2] for t in s]) for s in te]
    TAGS = sorted({t for _w, g in train_all for t in g})
    curve = []
    for n in SIZES:
        if n > len(train_all): break
        sub = train_all[:n]
        # more epochs for tiny sets (they converge fast but benefit from passes); cap compute
        epochs = 8 if n <= 250 else (6 if n <= 1000 else 5)
        if SMOKE: epochs = 4
        avg, vit = _train(sub, TAGS, epochs)
        hit = tot = 0
        for words, gold in test:
            pred = vit(words, avg)
            for p, g in zip(pred, gold): hit += int(p == g); tot += 1
        acc = hit / tot if tot else 0.0
        curve.append({"n_sents": n, "acc": round(acc, 4)})
        print("  POS @ %5d sents -> acc=%.4f" % (n, acc), flush=True)
    # find smallest n reaching 0.90
    n90 = next((c["n_sents"] for c in curve if c["acc"] >= 0.90), None)
    best = curve[-1]["acc"] if curve else 0.0
    print("  smallest-n for acc>=0.90 = %s | best=%.4f (n=%d) | test=%d sents" % (n90, best, curve[-1]["n_sents"] if curve else 0, len(test)), flush=True)
    return {"accuracy": best, "curve": curve, "n90": n90, "n_test": len(test), "n_tags": len(TAGS)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    n90 = r["n90"]; curve = r["curve"]
    cs = ", ".join("%d:%.3f" % (c["n_sents"], c["acc"]) for c in curve)
    s = "n90=%s, best=%.4f, curve=[%s], test=%d sents" % (n90, r["accuracy"], cs, r["n_test"])
    if n90 is not None and n90 <= 250:
        return ("HARD_PASS", "HARD_PASS: substrate POS reaches >=0.90 with <=250 training sentences (n90=%d) -- STRONG low-data efficiency; the structured-prediction win holds in the few-shot/niche-domain regime (substrate-product low-data advantage). " % n90 + s)
    if n90 is not None and n90 <= 1000:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate POS reaches >=0.90 by %d sentences -- good data efficiency, not extreme. " % n90 + s)
    return ("HARD_FAIL", "HARD_FAIL: substrate POS needs >1000 sentences for 0.90 -- weaker low-data efficiency than hypothesized. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
