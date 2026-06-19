"""
exp_chunking_discriminative_cpu_v1.py -- discriminative shallow-parsing (chunking) on UD-EWT -- CPU.

ROUTING: net-new capability probe (chunking / shallow parsing -- another structured-prediction task). BIO chunk tags derived
  from UD-EWT POS (NP = runs of DET/ADJ/NUM/NOUN/PROPN/PRON; VP = VERB/AUX; PP = ADP; else O), predicted from WORD features
  (structured perceptron + vectorized Viterbi). Span-level chunk F1. Bundled UD-EWT (RESCUE-1). Discriminative-weighting, no LLM.
PRE-REGISTERED: HARD-PASS chunk-F1 >= 0.85 (substrate-classical chunking production-grade). MIDDLE >= 0.75. HARD-FAIL < 0.65. UNKNOWN if load fails.
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
from typing import Dict, List, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics
from _ud_loader import load_conllu
ANCHOR_NAME = "chunking_discriminative_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
NPOS = {"DET", "ADJ", "NUM", "NOUN", "PROPN", "PRON"}; VPOS = {"VERB", "AUX"}
def _chunk_type(pos):
    if pos in NPOS: return "NP"
    if pos in VPOS: return "VP"
    if pos == "ADP": return "PP"
    return "O"
def _bio(sent):
    """derive BIO chunk tags from POS sequence."""
    tags = []; prev = "O"
    for (_i, _w, pos, _h, _d) in sent:
        ct = _chunk_type(pos)
        if ct == "O": tags.append("O"); prev = "O"
        elif ct == prev: tags.append("I-" + ct)
        else: tags.append("B-" + ct); prev = ct
    return tags
def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper(): return "Cap"
    if "-" in w: return "HYP"
    return "low"
def _emit(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_shape(w), tag)]
    for k in (2, 3):
        if len(wl) >= k: fs.append("suf%d_%s~%s" % (k, wl[-k:], tag))
    fs.append("pw_%s~%s" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%s" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    return fs
def _spans(tags):
    sp = set(); i = 0; n = len(tags)
    while i < n:
        t = tags[i]
        if t.startswith("B-"):
            ty = t[2:]; j = i + 1
            while j < n and tags[j] == "I-" + ty: j += 1
            sp.add((i, j, ty)); i = j
        else: i += 1
    return sp
def _selftest():
    assert _chunk_type("NOUN") == "NP" and _spans(["B-NP", "I-NP", "O"]) == {(0, 2, "NP")}
    print("[selftest] PASS: chunking-discriminative", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1032")))
    try:
        tr_s = load_conllu("train"); dv_s = load_conllu("dev")
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "f1": 0.0}
    tr_s = [s for s in tr_s if 1 <= len(s) <= 50]; dv_s = [s for s in dv_s if 1 <= len(s) <= 50]
    if not SMOKE: tr_s = tr_s[:3000]
    else: tr_s = tr_s[:300]; dv_s = dv_s[:150]
    train = [([t[1] for t in s], _bio(s)) for s in tr_s]; dev = [([t[1] for t in s], _bio(s)) for s in dv_s]
    TAGS = sorted({t for _w, g in train for t in g}); T = len(TAGS)
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
    for ep in range(6 if not SMOKE else 3):
        for si in rng.permutation(len(train)):
            words, gold = train[si]; pred = viterbi(words, w)
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
    avg = {f: w[f] - cw[f] / c for f in w}
    tp = fp = fn = 0
    for words, gold in dev:
        pred = viterbi(words, avg); gs = _spans(gold); ps = _spans(pred)
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); f1 = 2 * prec * rec / (prec + rec + 1e-9)
    print("  CHUNKING-DISCRIMINATIVE: chunk-F1=%.4f (P=%.3f R=%.3f) | train=%d sents" % (f1, prec, rec, len(train)), flush=True)
    return {"f1": round(f1, 4), "prec": round(prec, 3), "rec": round(rec, 3), "n_train": len(train)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    f1 = r["f1"]; s = "chunk-F1=%.4f (train=%d)" % (f1, r["n_train"])
    if f1 >= 0.85:
        return ("HARD_PASS", "HARD_PASS: discriminative chunker >=0.85 chunk-F1 -- substrate-classical shallow parsing production-grade; another structured-prediction capability, no LLM. " + s)
    if f1 >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: chunk-F1 0.75-0.85 -- strong. " + s)
    return ("HARD_FAIL", "HARD_FAIL: chunk-F1 <0.65. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
