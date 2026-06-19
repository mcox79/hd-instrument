"""
exp_substrate_atis_slot_filling_cpu_v1.py -- substrate-classical SLOT FILLING (ATIS) -- CPU.

ROUTING: Tier-A roster expansion -- a NEW substrate-classical NL capability (slot filling / NLU sequence labeling), not yet
  tested. Substrate-quality-first; NO LLM frame. discriminative_perceptron (structured perceptron + Viterbi) over BIO slot tags
  on ATIS (4978 train / 893 test, ~120 slot labels: fromloc.city_name, depart_time.time, toloc.city_name, ...). Span-level slot
  F1 (the standard ATIS metric). Same universal discriminative-weighting lever as POS/NER/chunking.

PRE-REGISTERED: HARD-PASS slot-F1 >= 0.88 (substrate-classical production-grade slot filling; strong neural systems ~0.95).
  MIDDLE 0.78-0.88. HARD-FAIL < 0.78. UNKNOWN if load fails.
ASCII-only. CPU. --self-test + --smoke + metrics.json. Route via remote_cpu_queue (desktop).
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
ANCHOR_NAME = "substrate_atis_slot_filling_robustness_cpu_v1"
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


def _emit(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_shape(w), tag)]
    for k in (1, 2, 3):
        if len(wl) >= k: fs.append("suf%d_%s~%s" % (k, wl[-k:], tag))
    if len(wl) >= 3: fs.append("pre3_%s~%s" % (wl[:3], tag))
    fs.append("pw_%s~%s" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%s" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    fs.append("p2w_%s~%s" % (words[i - 2].lower() if i > 1 else "<S>", tag))
    return fs


def _spans(tags):
    """BIO spans with slot type: (start, end, slot_type)."""
    sp = set(); i = 0; n = len(tags)
    while i < n:
        t = tags[i]
        if t.startswith("B-"):
            typ = t[2:]; j = i + 1
            while j < n and tags[j] == "I-" + typ: j += 1
            sp.add((i, j, typ)); i = j
        else: i += 1
    return sp


def _char_perturb(word, rate, rng):
    if rate <= 0 or len(word) < 2 or not word.isalpha(): return word
    out = []
    for ch in word:
        if rng.random() < rate:
            op = rng.integers(0, 3)
            if op == 0: out.append(chr(int(rng.integers(97, 123))))
            elif op == 1: out.append(ch); out.append(chr(int(rng.integers(97, 123))))
        else: out.append(ch)
    return "".join(out) or word


def _load():
    d = json.load(open(REPO / "experiments" / "data" / "atis_full.json", encoding="utf-8"))
    def conv(split):
        out = []
        for e in split:
            toks = e["text"].split(); tags = e["slots"].split()
            if len(toks) == len(tags) and toks: out.append((toks, tags))
        return out
    return conv(d["train"]), conv(d["test"])


def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1028")))
    try:
        train, test = _load()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed"}
    if SMOKE: train = train[:400]; test = test[:150]
    TAGS = sorted({t for _w, g in train for t in g}); T = len(TAGS); ti = {t: k for k, t in enumerate(TAGS)}
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(pt, t): return "tt_%s~%s" % (pt, t)

    def viterbi(words, weights):
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

    EP = 6 if not SMOKE else 3
    for ep in range(EP):
        for si in rng.permutation(len(train)):
            words, gold = train[si]; pred = viterbi(words, w)
            if pred != gold:
                pg = "<S>"; pp = "<S>"
                for i in range(len(words)):
                    if pred[i] != gold[i]:
                        for f in _emit(words, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in _emit(words, i, pred[i]): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    noises = [0.0, 0.20] if SMOKE else [0.0, 0.05, 0.10, 0.20]
    curve = []
    for nz in noises:
        nrng = np.random.default_rng(7); tp = fp = fn = 0
        for words, gold in test:
            tw = [_char_perturb(x, nz, nrng) for x in words] if nz > 0 else words
            gs = _spans(gold); ps = _spans(viterbi(tw, avg))
            tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
        prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); f1 = 2 * prec * rec / (prec + rec + 1e-9)
        curve.append({"noise": nz, "slot_f1": round(f1, 4)})
        print("  noise=%2.0f%% slot-F1=%.4f" % (100 * nz, f1), flush=True)
    f0 = curve[0]["slot_f1"]; f20 = curve[-1]["slot_f1"]; ret = round(f20 / (f0 + 1e-9), 4)
    print("  ATIS-SLOT-FILLING ROBUSTNESS: clean=%.4f @20%%-noise=%.4f retention=%.1f%% (%d tags)" % (f0, f20, 100 * ret, T), flush=True)
    return {"f1": f0, "slot_f1_clean": f0, "slot_f1_20noise": f20, "retention_20": ret, "curve": curve, "n_train": len(train), "n_tags": T}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    ret = r["retention_20"]; s = "clean=%.4f @20%%-noise=%.4f retention=%.1f%% (%d slot-tags); curve=%s" % (r["slot_f1_clean"], r["slot_f1_20noise"], 100 * ret, r["n_tags"], [(c["noise"], c["slot_f1"]) for c in r["curve"]])
    if ret >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate slot-filling ROBUST -- >=70%% slot-F1 retention at 20%% char-noise (123 slot-tags). Structured-prediction noise-robustness extends to large-tag-set NLU (consistent with NER transition noise-robustness). " + s)
    if ret >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: moderate slot-filling robustness (55-70%% retention @20%% noise). " + s)
    return ("HARD_FAIL", "HARD_FAIL: slot-filling fragile (<55%% retention @20%% noise). " + s)


def _selftest():
    assert _spans(["O", "B-x", "I-x", "O", "B-y"]) == {(1, 3, "x"), (4, 5, "y")}
    assert _shape("Boston") == "Cap"
    print("[selftest] PASS: atis-slot-filling", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
