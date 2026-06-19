"""
exp_ner_singletype_boundary_cpu_v1.py -- NER diagnostic: collapse 18 types -> 1 "ENTITY" (boundary-only) -- CPU.

ROUTING: follow-up to NER Path 1 refutation (exp_ner_bio_viterbi: hard-BIO lift=-0.0125; decoder NOT the bottleneck). Decisive
  cheap diagnostic separating TYPE-CONFUSION from BOUNDARY/FEATURE limits. Collapse every entity type to ONE ("ENTITY"): every
  B-* -> B-ENT, I-* -> I-ENT, O stays O. Re-run the SAME structured-perceptron Viterbi. Span F1 here = pure boundary detection,
  no 18-way type confusion. Compare to the 18-type F1=0.5817.
  - If single-type F1 >> 0.58 (e.g. >=0.72): much of "0.58" is 18-WAY TYPE CONFUSION; boundary detection is fine; the lever is
    better TYPE discrimination (features), and OntoNotes-18 is harder than CoNLL-4 (apples-to-oranges vs the 0.65 CoNLL target).
  - If single-type F1 ~= 0.58: the problem is BOUNDARY DETECTION itself (features for where entities start/end), not type confusion.
  Substrate-only. Bundled OntoNotes.
PRE-REGISTERED (diagnostic, NO defeat): report single-type boundary-F1 and the gap vs 18-type 0.5817.
  HARD-PASS boundary-F1 >= 0.72 (type-confusion is the dominant cost; boundary detection is strong). MIDDLE 0.62-0.72.
  HARD-FAIL < 0.62 (boundary/feature limited, not type confusion). UNKNOWN if load fails.
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
ANCHOR_NAME = "ner_singletype_boundary_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
F1_18TYPE = 0.5817  # reference from exp_ner_bio_viterbi unconstrained baseline


def _collapse(tags):
    """18-type integer tags (0=O, odd=B-*, even>0=I-*) -> single-type (0=O, 1=B-ENT, 2=I-ENT)."""
    out = []
    for t in tags:
        if t == 0: out.append(0)
        elif t % 2 == 1: out.append(1)   # any B-* -> B-ENT
        else: out.append(2)              # any I-* -> I-ENT
    return out


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
    """single-type: 1=B-ENT, 2=I-ENT. Returns (start,end) spans (type always ENT)."""
    sp = set(); i = 0; n = len(tags)
    while i < n:
        if tags[i] == 1:
            j = i + 1
            while j < n and tags[j] == 2: j += 1
            sp.add((i, j)); i = j
        else: i += 1
    return sp


def _selftest():
    assert _collapse([0, 3, 4, 0, 1, 0]) == [0, 1, 2, 0, 1, 0] and _spans([0, 1, 2, 0]) == {(1, 3)}
    print("[selftest] PASS: ner-singletype-boundary", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1028")))
    try:
        data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "f1": 0.0}
    train = [(t, _collapse(g)) for t, g in data["train"] if t and len(t) <= 60]
    test = [(t, _collapse(g)) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE: train = train[:300]; test = test[:150]
    TAGS = [0, 1, 2]; T = 3
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
    gap = f1 - F1_18TYPE
    print("  NER-SINGLETYPE-BOUNDARY: F1=%.4f (P=%.3f R=%.3f) | vs 18-type 0.5817 -> gap=%+.4f | train=%d test=%d" %
          (f1, prec, rec, gap, len(train), len(test)), flush=True)
    return {"f1": round(f1, 4), "boundary_f1": round(f1, 4), "f1_18type": F1_18TYPE, "type_confusion_cost": round(gap, 4),
            "prec": round(prec, 3), "rec": round(rec, 3), "n_train": len(train)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    f1 = r["boundary_f1"]; gap = r["type_confusion_cost"]
    s = "boundary-F1=%.4f vs 18-type 0.5817 (type-confusion cost=%+.4f, P=%.3f R=%.3f, train=%d)" % (f1, gap, r["prec"], r["rec"], r["n_train"])
    if f1 >= 0.72:
        return ("HARD_PASS", "HARD_PASS: single-type boundary-F1>=0.72 -- boundary detection is STRONG; most of the 0.58 18-type cost is 18-WAY TYPE CONFUSION. Lever = better type discrimination (features); OntoNotes-18 is harder than CoNLL-4 (the note's 0.65 target was apples-to-oranges). " + s)
    if f1 >= 0.62:
        return ("MIDDLE_BAND", "MIDDLE_BAND: boundary-F1 0.62-0.72 -- type confusion is a moderate cost; both boundary features and type discrimination matter. " + s)
    return ("HARD_FAIL", "HARD_FAIL: boundary-F1 <0.62 -- even single-type boundary detection is limited; the bottleneck is BOUNDARY/FEATURE detection, not type confusion. Richer span features needed (Path 2/5). " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
