"""
exp_pos_discriminative_perceptron_cpu_v1.py -- discriminative (structured-perceptron) POS tagger on PTB -- CPU.

ROUTING: Research 5-cheap experiment #1 (lift PP-364 HMM 0.906 -> 0.92+). The HMM is generative; a structured perceptron
  (Collins) discriminatively weights emission + transition features with Viterbi decode. Same discriminative-weighting lever
  validated on math/code/parsing. Bundled PTB treebank (RESCUE; no runtime NLTK download). Substrate-classical discriminative, no LLM.
PRE-REGISTERED: HARD-PASS tag-accuracy >= 0.92 (discriminative beats the HMM 0.906). MIDDLE >= 0.906. HARD-FAIL < 0.906. UNKNOWN if load fails.
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
ANCHOR_NAME = "pos_discriminative_perceptron_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def _shape(w):
    if any(c.isdigit() for c in w): return "DIG"
    if w[:1].isupper(): return "CAP"
    if "-" in w: return "HYP"
    return "low"
def _emit_feats(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%s" % (k, wl[-k:], tag))
    for k in (1, 2, 3):
        if len(wl) >= k: fs.append("pre%d_%s~%s" % (k, wl[:k], tag))
    fs.append("pw_%s~%s" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%s" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    return fs
def _selftest():
    assert _shape("dog") == "low" and _shape("Dog") == "CAP" and _shape("12") == "DIG"
    print("[selftest] PASS: pos-discriminative-perceptron", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1024")))
    try:
        sents = json.load(open(REPO / "experiments" / "data" / "ptb_treebank_tagged.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    sents = [[(w, t) for w, t in s if t != "-NONE-"] for s in sents]
    sents = [s for s in sents if s]
    if SMOKE: sents = sents[:300]
    cut = int(len(sents) * 0.8); train = sents[:cut]; test = sents[cut:]
    if not SMOKE: train = train[:1800]   # cap for tractable structured-perceptron training (vectorized Viterbi)
    TAGS = sorted({t for s in train for _w, t in s}); ti = {t: k for k, t in enumerate(TAGS)}; T = len(TAGS)
    w = defaultdict(float); cw = defaultdict(float); c = 1
    def tt(pt, t): return "tt_%s~%s" % (pt, t)
    def viterbi(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit_feats(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt("<S>", TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int)
        V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM
            bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]
    EP = 6 if not SMOKE else 3
    for ep in range(EP):
        for si in rng.permutation(len(train)):
            s = train[si]; words = [x[0] for x in s]; gold = [x[1] for x in s]
            pred = viterbi(words, w)
            if pred != gold:
                pg = "<S>"; pp = "<S>"
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _emit_feats(words, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in _emit_feats(words, i, pred[i]): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    hit = 0; tot = 0
    for s in test:
        words = [x[0] for x in s]; gold = [x[1] for x in s]; pred = viterbi(words, avg)
        for g, p in zip(gold, pred): hit += int(g == p); tot += 1
    acc = hit / tot if tot else 0.0
    print("  POS-DISCRIMINATIVE: tag-accuracy=%.4f (%d/%d, train=%d sents, %d tags) vs HMM 0.906" % (acc, hit, tot, len(train), T), flush=True)
    return {"accuracy": round(acc, 4), "n_tokens": tot, "n_train": len(train), "n_tags": T}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; s = "tag-accuracy=%.4f (%d tokens, train=%d sents)" % (a, r["n_tokens"], r["n_train"])
    if a >= 0.92:
        return ("HARD_PASS", "HARD_PASS: discriminative structured-perceptron POS tagger >=0.92 -- discriminative weighting beats the HMM 0.906; same lever (math/code/parsing) lifts POS. " + s)
    if a >= 0.906:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 0.906-0.92 -- matches/edges the HMM; richer features for 0.92. " + s)
    return ("HARD_FAIL", "HARD_FAIL: <0.906 -- below the HMM baseline. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
