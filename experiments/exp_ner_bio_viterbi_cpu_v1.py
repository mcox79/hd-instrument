"""
exp_ner_bio_viterbi_cpu_v1.py -- NER Path 1: HARD BIO-constrained Viterbi vs unconstrained -- CPU.

ROUTING: Research note research_to_exp_dev_NER_BIO_VITERBI_CHEAP_DECISIVE_2026-06-11. Hypothesis: the 0.58 NER F1 is an
  unstructured-decode FLOOR, not an architectural ceiling; adding a BIO-constrained structured decoder lifts it (target >=0.65).
  HONEST CORRECTION (verify-before-invest): the existing NER cell ALREADY uses a structured-perceptron Viterbi with LEARNED
  (Collins) transitions -- it is NOT per-token argmax. So the genuinely UNTESTED lever is HARD BIO CONSTRAINTS: masking ILLEGAL
  transitions to -inf (O->I-X, B-X->I-Y, I-X->I-Y for Y!=X, START->I-X). This cell trains TWO models from IDENTICAL features and
  isolates exactly that lever: (A) unconstrained Viterbi (= current baseline, expect ~0.58) vs (B) hard-BIO-constrained Viterbi.
  Bundled OntoNotes 18-type (35 tags; HARDER than the CoNLL-2003 4-type the note referenced -- state honestly). Substrate-only.
PRE-REGISTERED (decisive per decision matrix): report B's F1 and the lift B - A.
  HARD-PASS B >= 0.65 (BIO-constraint confirmed as the missing decoder lever). MIDDLE B in [0.58,0.65) OR lift>=0.03.
  HARD-FAIL B < 0.58 (constraint broke emissions) OR |lift|<0.01 (constraint adds nothing; bottleneck is features/benchmark).
  UNKNOWN if load fails. NO pre-registered defeat (drill-defeatism).
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
ANCHOR_NAME = "ner_bio_viterbi_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
NEG = -1e9


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
    sp = set(); i = 0; n = len(tags)
    while i < n:
        t = tags[i]
        if t > 0 and t % 2 == 1:
            j = i + 1
            while j < n and tags[j] == t + 1: j += 1
            sp.add((i, j, (t - 1) // 2)); i = j
        else: i += 1
    return sp


def _bio_masks(TAGS):
    """Return (trans_mask TxT, start_mask T): 0 if legal, NEG if illegal. Tags: 0=O, odd=B-type, even>0=I-type (I = its B + 1)."""
    T = len(TAGS); tm = np.zeros((T, T)); sm = np.zeros(T)
    for ci, c in enumerate(TAGS):
        is_I = (c > 0 and c % 2 == 0)
        if is_I:
            sm[ci] = NEG  # START -> I-X illegal
            for pi, p in enumerate(TAGS):
                if p == c - 1 or p == c:  # legal only after its own B (c-1) or continuation of itself (c)
                    pass
                else:
                    tm[pi, ci] = NEG
    return tm, sm


def _selftest():
    assert _spans([0, 1, 2, 0]) == {(1, 3, 0)} and _shape("Bob") == "Cap"
    tm, sm = _bio_masks([0, 1, 2, 3, 4])  # O, B0, I0, B1, I1
    # I0 (idx2) legal only after B0(idx1) or I0(idx2); illegal after O(0), B1(3), I1(4) and from START
    assert tm[0, 2] == NEG and tm[1, 2] == 0 and tm[2, 2] == 0 and tm[3, 2] == NEG and sm[2] == NEG and sm[1] == 0
    print("[selftest] PASS: ner-bio-viterbi", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _train_and_eval(train, test, TAGS, constrain, seed):
    T = len(TAGS); rng = np.random.default_rng(seed)
    tmask, smask = _bio_masks(TAGS)
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(pt, t): return "tt_%d~%d" % (pt, t)

    def viterbi(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit_feats(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt(-1, TAGS[k]), 0.0) for k in range(T)])
        if constrain: TM = TM + tmask; SV = SV + smask
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
    return f1, prec, rec


def run() -> Dict:
    try:
        data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "f1": 0.0}
    train = [(t, g) for t, g in data["train"] if t and len(t) <= 60]
    test = [(t, g) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE: train = train[:300]; test = test[:150]
    TAGS = sorted({t for _w, g in train for t in g}); T = len(TAGS)
    seed = int(os.environ.get("HDLAB_SEED", "1028"))
    fa, pa, ra = _train_and_eval(train, test, TAGS, constrain=False, seed=seed)
    print("  [A unconstrained] entity-F1=%.4f (P=%.3f R=%.3f)" % (fa, pa, ra), flush=True)
    fb, pb, rb = _train_and_eval(train, test, TAGS, constrain=True, seed=seed)
    print("  [B hard-BIO]      entity-F1=%.4f (P=%.3f R=%.3f)" % (fb, pb, rb), flush=True)
    lift = fb - fa
    print("  LIFT (B - A) = %.4f | train=%d test=%d tags=%d (OntoNotes 18-type, harder than CoNLL 4-type)" % (lift, len(train), len(test), T), flush=True)
    return {"f1": round(fb, 4), "f1_unconstrained": round(fa, 4), "f1_bio": round(fb, 4), "lift": round(lift, 4),
            "prec_bio": round(pb, 3), "rec_bio": round(rb, 3), "n_train": len(train), "n_tags": T}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    fb = r["f1_bio"]; fa = r["f1_unconstrained"]; lift = r["lift"]
    s = "hard-BIO F1=%.4f vs unconstrained %.4f (lift=%+.4f, P=%.3f R=%.3f, train=%d, OntoNotes 18-type)" % (fb, fa, lift, r["prec_bio"], r["rec_bio"], r["n_train"])
    if fb >= 0.65:
        return ("HARD_PASS", "HARD_PASS: hard-BIO-constrained Viterbi NER >=0.65 -- BIO-constraint confirmed as a real decoder lever; stack Path 2-5 toward 0.75. " + s)
    if fb >= 0.58 or lift >= 0.03:
        return ("MIDDLE_BAND", "MIDDLE_BAND: hard-BIO partial (F1 in [0.58,0.65) or lift>=0.03) -- constraint helps but features/benchmark (OntoNotes 18-type) cap it; need Path 2 richer features. " + s)
    if abs(lift) < 0.01:
        return ("HARD_FAIL", "HARD_FAIL: hard-BIO adds nothing (|lift|<0.01) -- the learned soft transitions already encode BIO; the 0.58 bottleneck is FEATURES/BENCHMARK-difficulty, not the decoder. Honest correction to the note's argmax premise. " + s)
    return ("HARD_FAIL", "HARD_FAIL: hard-BIO F1 <0.58 -- constraint degraded emissions; investigate. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
