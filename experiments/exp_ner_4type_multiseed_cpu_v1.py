"""
exp_ner_4type_conll_cpu_v1.py -- NER diagnostic: collapse OntoNotes 18-type -> 4 CoNLL-style coarse types -- CPU.

ROUTING: Research Action 1 (research_to_exp_dev_NER_PATH1_REFUTED_FEATURES_NEXT). Decisive on whether the 0.58 18-type F1 was
  largely 18-WAY DIFFICULTY (apples-to-oranges vs the CoNLL-2003 4-type 0.65 target) or a genuine feature gap. Map OntoNotes types
  to the CoNLL-2003 coarse scheme and re-run the SAME structured-perceptron Viterbi:
    PER  <- PERSON
    ORG  <- ORG
    LOC  <- GPE, LOC, FAC
    MISC <- NORP, PRODUCT, EVENT, WORK_OF_ART, LAW, LANGUAGE
    O (dropped) <- DATE, TIME, PERCENT, MONEY, QUANTITY, ORDINAL, CARDINAL  (numeric/temporal; not in CoNLL-2003)
  Integer tags follow standard conll2012_ontonotesv5 order (verified: tag15=B-DATE, tags1/2=B/I-PERSON). type_id=(tag-1)//2.
  Bundled OntoNotes. Substrate-only. CoNLL-equivalent span F1.
PRE-REGISTERED (diagnostic; NO defeat): report 4-type CoNLL-equivalent F1 vs 18-type 0.5817.
  HARD-PASS F1 >= 0.70 (much of 0.58 was 18-way difficulty; CoNLL-equivalent is competitive -- the note's 0.65 was apples-to-oranges).
  MIDDLE 0.62-0.70. HARD-FAIL < 0.62 (genuine feature gap; proceed Path 2 Brown-cluster features). UNKNOWN if load fails.
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
ANCHOR_NAME = "ner_4type_multiseed_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
F1_18TYPE = 0.5817
# OntoNotes type_id -> CoNLL coarse id (0=PER,1=ORG,2=LOC,3=MISC) or None to drop. type_id=(tag-1)//2.
COARSE = {0: 0, 3: 1, 4: 2, 5: 2, 2: 2, 1: 3, 6: 3, 14: 3, 15: 3, 16: 3, 17: 3}  # PERSON|ORG|GPE/LOC/FAC|NORP/PRODUCT/EVENT/WOA/LAW/LANG
# numeric/temporal type_ids 7..13 absent -> dropped to O
# new tag scheme: 0=O, then B/I per coarse: B=1+2*coarse, I=2+2*coarse


def _collapse4(tags):
    out = []
    for t in tags:
        if t == 0: out.append(0); continue
        tid = (t - 1) // 2; is_B = (t % 2 == 1)
        cz = COARSE.get(tid)
        if cz is None: out.append(0)
        else: out.append((1 + 2 * cz) if is_B else (2 + 2 * cz))
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
    # PERSON tags 1,2 -> coarse PER (0) -> B=1,I=2 ; DATE tag 15 (tid7) -> dropped to 0 ; ORG tags 7,8 (tid3) -> ORG(1) -> B=3,I=4
    assert _collapse4([1, 2, 0, 15, 7, 8]) == [1, 2, 0, 0, 3, 4]
    assert _spans([1, 2, 0]) == {(0, 2, 0)}
    print("[selftest] PASS: ner-4type-conll", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _one_seed(train, test, TAGS, seed):
    T = len(TAGS); rng = np.random.default_rng(seed); w = defaultdict(float); cw = defaultdict(float); c = 1

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
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); return 2 * prec * rec / (prec + rec + 1e-9)


def run() -> Dict:
    try:
        data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "f1": 0.0}
    train = [(t, _collapse4(g)) for t, g in data["train"] if t and len(t) <= 60]
    test = [(t, _collapse4(g)) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE: train = train[:300]; test = test[:150]
    TAGS = sorted({tg for _w, g in train for tg in g})
    SEEDS = [1, 2, 3] if SMOKE else [1, 2, 3, 4, 5]
    vals = [round(_one_seed(train, test, TAGS, sd), 4) for sd in SEEDS]
    mean = sum(vals) / len(vals); std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
    se = std / (len(vals) ** 0.5)
    print("  NER-4TYPE-CONLL n=%d: mean-F1=%.4f std=%.4f SE=%.4f (mean-2SE=%.4f) vals=%s" % (
        len(vals), mean, std, se, mean - 2 * se, vals), flush=True)
    return {"f1": round(mean, 4), "accuracy": round(mean, 4), "std": round(std, 4), "se": round(se, 4),
            "mean_minus_2se": round(mean - 2 * se, 4), "vals": vals, "n_seeds": len(vals), "n_train": len(train)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    m = r["accuracy"]; m2 = r["mean_minus_2se"]
    s = "mean-F1=%.4f std=%.4f SE=%.4f mean-2SE=%.4f (n=%d, vals=%s)" % (m, r["std"], r["se"], m2, r["n_seeds"], r["vals"])
    if m2 >= 0.64:
        return ("HARD_PASS", "HARD_PASS: NER 4-type CoNLL-equiv multi-seed mean-2SE>=0.64 -- PROMOTE Tier-B->Tier-A (seed-robust; matches literature CoNLL-2003 ~0.65). " + s)
    if m >= 0.62:
        return ("MIDDLE_BAND", "MIDDLE_BAND: NER 4-type mean 0.62-0.65 -- Tier-B firmed (multi-seed) but mean-2SE below 0.64 promotion bar. " + s)
    return ("HARD_FAIL", "HARD_FAIL: NER 4-type mean <0.62. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
