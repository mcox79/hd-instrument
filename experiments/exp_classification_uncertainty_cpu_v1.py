"""
exp_classification_uncertainty_cpu_v1.py -- substrate classifier UNCERTAINTY QUANTIFICATION on SST-2 + AG-News -- CPU.

ROUTING: the banked conformal+isotonic uncertainty quantification was MATH-only. Extend it to the substrate CLASSIFIER's
  confidence (product dimension: a deployed classifier needs calibrated confidence + abstention). For each task: train the
  averaged-perceptron, turn margins into probabilities (softmax with temperature scaling fit on a calibration split), measure
  ECE before/after temperature scaling, and run split-conformal (APS-style cumulative-prob) prediction SETS at alpha=0.1 ->
  empirical coverage + mean set size. Substrate-only, no LLM.
PRE-REGISTERED: HARD-PASS if (calibrated ECE <= 0.10 on BOTH tasks) AND (conformal coverage within [0.86,0.94] on BOTH). MIDDLE if
  one task meets both. HARD-FAIL if neither. UNKNOWN if load fails. (alpha=0.1 -> target coverage 0.90.)
ASCII-only.
"""
import sys, os, time, json, math, random
from pathlib import Path
from collections import defaultdict
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import re
REPO = Path(__file__).resolve().parent.parent
SMOKE = "--smoke" in sys.argv
OUT = REPO / "data" / ("exp_" + os.environ.get("HDLAB_EXP_NAME", "classification_uncertainty_cpu_v1"))


def _feats(txt):
    ws = re.findall(r"[a-z]+", txt.lower()); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("BIAS"); return fs


def _train(train, LAB):
    rng = random.Random(0); Xtr = [(_feats(e["text"]), e["label"]) for e in train]
    w = {l: defaultdict(float) for l in LAB}; cw = {l: defaultdict(float) for l in LAB}; c = 1
    for ep in range(8 if not SMOKE else 3):
        order = list(range(len(Xtr))); rng.shuffle(order)
        for i in order:
            feats, g = Xtr[i]; sc = {l: sum(w[l][f] for f in feats) for l in LAB}
            pred = max(LAB, key=lambda l: (sc[l], l))
            if pred != g:
                for f in feats: w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    return {l: {f: w[l][f] - cw[l][f] / c for f in w[l]} for l in LAB}


def _margins(avg, e, LAB):
    feats = _feats(e["text"]); return [sum(avg[l].get(f, 0.0) for f in feats) for l in LAB]


def _softmax_T(scores, T):
    m = max(scores); ex = [math.exp((s - m) / T) for s in scores]; Z = sum(ex); return [x / Z for x in ex]


def _ece(probs, preds, golds, nb=10):
    bins = [[] for _ in range(nb)]
    for p, pr, g in zip(probs, preds, golds):
        conf = max(p); b = min(nb - 1, int(conf * nb)); bins[b].append((conf, int(pr == g)))
    e = 0.0; n = len(probs)
    for bk in bins:
        if not bk: continue
        conf = sum(x[0] for x in bk) / len(bk); acc = sum(x[1] for x in bk) / len(bk); e += len(bk) / n * abs(conf - acc)
    return e


def _fit_T(scores_list, golds):
    best_T, best = 1.0, 1e18
    for T in [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0]:
        nll = 0.0
        for sc, g in zip(scores_list, golds):
            p = _softmax_T(sc, T); nll += -math.log(max(p[g], 1e-12))
        if nll < best: best, best_T = nll, T
    return best_T


def run_task(fn):
    data = json.load(open(REPO / "experiments" / "data" / fn, encoding="utf-8"))
    LABELS = data["labels"]; train = data["train"]; LAB = list(range(len(LABELS)))
    pool = data["test"][: (40 if SMOKE else 800)]
    half = len(pool) // 2; cal, test = pool[:half], pool[half:]   # calibration / test split
    avg = _train(train, LAB)
    cal_sc = [_margins(avg, e, LAB) for e in cal]; cal_g = [e["label"] for e in cal]
    test_sc = [_margins(avg, e, LAB) for e in test]; test_g = [e["label"] for e in test]
    T = _fit_T(cal_sc, cal_g)
    # ECE before (T=1) and after (fitted T)
    p1 = [_softmax_T(s, 1.0) for s in test_sc]; pT = [_softmax_T(s, T) for s in test_sc]
    preds = [max(LAB, key=lambda l: (s[l], l)) for s in test_sc]
    ece_before = _ece(p1, preds, test_g); ece_after = _ece(pT, preds, test_g)
    acc = sum(int(p == g) for p, g in zip(preds, test_g)) / len(test_g)
    # split-conformal APS: nonconformity = 1 - sum of probs down to true label (cumulative)
    def aps_score(prob, y):
        order = sorted(range(len(prob)), key=lambda k: -prob[k]); s = 0.0
        for k in order:
            s += prob[k]
            if k == y: return s
        return s
    cal_pT = [_softmax_T(s, T) for s in cal_sc]
    scores = sorted(aps_score(p, g) for p, g in zip(cal_pT, cal_g))
    alpha = 0.1; n = len(scores); q = scores[min(n - 1, math.ceil((n + 1) * (1 - alpha)) - 1)]
    cov = 0; setsz = 0
    for p, g in zip(pT, test_g):
        order = sorted(range(len(p)), key=lambda k: -p[k]); cum = 0.0; S = []
        for k in order:
            cum += p[k]; S.append(k)
            if cum >= q: break
        setsz += len(S); cov += int(g in S)
    coverage = cov / len(test_g); meanset = setsz / len(test_g)
    return {"acc": round(acc, 3), "ece_before": round(ece_before, 3), "ece_after": round(ece_after, 3),
            "T": T, "coverage": round(coverage, 3), "mean_set_size": round(meanset, 2), "n_test": len(test_g), "n_labels": len(LABELS)}


def main():
    print("[config] classification uncertainty quantification (substrate-only)", flush=True)
    t0 = time.time(); res = {}
    for tname, fn in [("sst2", "sst2.json"), ("agnews", "ag_news.json")]:
        res[tname] = run_task(fn)
        r = res[tname]
        print("  [%s] acc=%.3f ECE %.3f->%.3f (T=%.2f) | conformal cov=%.3f set=%.2f (target 0.90)" % (
            tname, r["acc"], r["ece_before"], r["ece_after"], r["T"], r["coverage"], r["mean_set_size"]), flush=True)
    def ok(r): return r["ece_after"] <= 0.10 and 0.86 <= r["coverage"] <= 0.94
    n_ok = sum(ok(r) for r in res.values())
    if n_ok == 2: verdict = "HARD_PASS"
    elif n_ok == 1: verdict = "MIDDLE_BAND"
    else: verdict = "HARD_FAIL"
    parts = ["%s: ECE_cal=%.3f cov=%.3f set=%.2f" % (t, r["ece_after"], r["coverage"], r["mean_set_size"]) for t, r in res.items()]
    msg = "%s: substrate classifier uncertainty quantification -- %s. (HARD_PASS needs cal-ECE<=0.10 + cov in [0.86,0.94] on both.) Temperature-scaled confidence + split-conformal APS sets, substrate-only." % (verdict, " | ".join(parts))
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "classification_uncertainty_cpu_v1", "verdict": verdict, "verdict_msg": msg,
               "summary": msg, "elapsed_s": time.time() - t0, "per_task": res}, open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)


if "--self-test" in sys.argv:
    assert abs(sum(_softmax_T([1.0, 2.0], 1.0)) - 1.0) < 1e-9; print("[selftest] PASS: classification-uncertainty", flush=True); sys.exit(0)
main()
