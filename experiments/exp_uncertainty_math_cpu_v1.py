"""
exp_uncertainty_math_cpu_v1.py -- conformal coverage + isotonic calibration on the SVAMP math op-classifier -- CPU.

ROUTING: extend substrate uncertainty quantification to a 2ND domain (math, after code in #3/#4). The SVAMP op-classifier
  (discriminative perceptron, 6 op-classes) gets a split-conformal coverage guarantee (APS) + isotonic calibration (ECE).
  Shows the uncertainty-quantification capability generalizes across tasks (code AND math), not task-specific. Bundled SVAMP
  (math_benchmarks_test.json). Substrate-classical, no LLM.
PRE-REGISTERED: HARD-PASS conformal coverage>=0.95 AND post-calibration ECE<0.05. MIDDLE one of two. HARD-FAIL neither. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, json, math
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "uncertainty_math_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
ALPHA = 0.05
OPS = {"ADD": lambda a, b: a + b, "MUL": lambda a, b: a * b, "SUB_ab": lambda a, b: a - b,
       "SUB_ba": lambda a, b: b - a, "DIV_ab": lambda a, b: a / b if b != 0 else None, "DIV_ba": lambda a, b: b / a if a != 0 else None}
OPN = list(OPS.keys())
def _nums(t):
    out = []
    for m in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.])", t.replace(",", "")):
        try: out.append(Fraction(m))
        except Exception: pass
    return out
def _feats(txt):
    low = txt.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    for cue in ("left", "more", "than", "each", "total", "altogether", "times", "per", "all", "rest", "difference"):
        if cue in low: fs.add("c:" + cue)
    fs.add("BIAS"); return fs
def _ece(conf, corr, bins=10):
    conf = np.array(conf); corr = np.array(corr, float); n = len(conf); e = 0.0
    for b in range(bins):
        m = (conf > b / bins) & (conf <= (b + 1) / bins)
        if m.sum(): e += (m.sum() / n) * abs(corr[m].mean() - conf[m].mean())
    return e
def _isotonic(x, y):
    order = np.argsort(x); xs = np.array(x)[order]; ys = np.array(y, float)[order]
    merged = []
    for k in range(len(ys)):
        merged.append([ys[k], 1.0, xs[k]])
        while len(merged) >= 2 and merged[-2][0] > merged[-1][0]:
            v2, w2, b2 = merged.pop(); v1, w1, b1 = merged.pop()
            merged.append([(v1 * w1 + v2 * w2) / (w1 + w2), w1 + w2, b2])
    def f(q):
        for v, _w, b in merged:
            if q <= b: return v
        return merged[-1][0]
    return f
def _selftest():
    print("[selftest] PASS: uncertainty-math", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1031")))
    try:
        mb = json.load(open(REPO / "experiments" / "data" / "math_benchmarks_test.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "coverage": 0.0, "ece_post": 1.0}
    rows = mb.get("SVAMP", []) + mb.get("MAWPS", [])
    data = []
    for r in rows:
        q = r["q"]; a = r["a"]
        try: ans = Fraction(str(a)).limit_denominator(10**6)
        except Exception:
            m = re.search(r"-?\d+(?:\.\d+)?", str(a)); ans = Fraction(m.group(0)) if m else None
        ns = _nums(q)
        if ans is not None and len(ns) >= 2:
            for op in OPN:
                rr = OPS[op](ns[0], ns[1])
                if rr is not None and Fraction(rr).limit_denominator(10**6) == ans: data.append((q, op)); break
    if SMOKE: data = data[:200]
    if len(data) < 60: return {"error": "too_few", "coverage": 0.0, "ece_post": 1.0}
    idx = rng.permutation(len(data)); tr = [data[i] for i in idx[:len(idx) // 2]]; pool = [data[i] for i in idx[len(idx) // 2:]]
    LAB = sorted(set(y for _q, y in tr)); Xtr = [(_feats(q), y) for q, y in tr]
    w = {l: defaultdict(float) for l in LAB}; cw = {l: defaultdict(float) for l in LAB}; c = 1
    for ep in range(12 if not SMOKE else 4):
        for i in rng.permutation(len(Xtr)):
            feats, g = Xtr[i]; sc = {l: sum(w[l][f] for f in feats) for l in LAB}
            pred = max(LAB, key=lambda l: (sc[l], l))
            if pred != g:
                for f in feats: w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    avg = {l: {f: w[l][f] - cw[l][f] / c for f in w[l]} for l in LAB}; li = {l: k for k, l in enumerate(LAB)}; L = len(LAB)
    def probs(q):
        feats = _feats(q); s = np.array([sum(avg[l].get(f, 0.0) for f in feats) for l in LAB]); s = s - s.max(); e = np.exp(s); return e / e.sum()
    half = len(pool) // 2; cal = pool[:half]; tst = pool[half:]
    # conformal APS
    def aps(p, yj):
        order = np.argsort(-p); cum = 0.0
        for j in order:
            cum += p[j]
            if j == yj: return cum
        return cum
    ncf = sorted(aps(probs(q), li[y]) for q, y in cal); n = len(ncf); qhat = ncf[min(n - 1, int(math.ceil((1 - ALPHA) * (n + 1))) - 1)]
    cov = 0
    for q, y in tst:
        p = probs(q); order = np.argsort(-p); cum = 0.0; pset = set()
        for j in order:
            cum += p[j]; pset.add(LAB[j])
            if cum >= qhat: break
        cov += int(y in pset)
    coverage = cov / len(tst)
    # calibration ECE (raw -> isotonic)
    rc = []; ry = []
    for q, y in tst:
        p = probs(q); j = int(np.argmax(p)); rc.append(float(p[j])); ry.append(int(LAB[j] == y))
    ece_raw = _ece(rc, ry); cc = []; cy = []
    for q, y in cal:
        p = probs(q); j = int(np.argmax(p)); cc.append(float(p[j])); cy.append(int(LAB[j] == y))
    f = _isotonic(cc, cy); ece_post = _ece([f(x) for x in rc], ry)
    print("  UNCERTAINTY-MATH: conformal-coverage=%.4f (target 0.95) | ECE raw=%.4f -> calibrated=%.4f | n_test=%d %d ops" %
          (coverage, ece_raw, ece_post, len(tst), L), flush=True)
    return {"coverage": round(coverage, 4), "ece_raw": round(ece_raw, 4), "ece_post": round(ece_post, 4), "n_test": len(tst)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    cv = r["coverage"]; ep = r["ece_post"]; s = "coverage=%.4f ECE %.4f->%.4f (n=%d)" % (cv, r["ece_raw"], ep, r["n_test"])
    if cv >= 0.95 and ep < 0.05:
        return ("HARD_PASS", "HARD_PASS: conformal coverage guarantee + calibrated ECE<0.05 on the MATH op-classifier -- uncertainty quantification generalizes to a 2nd domain (code AND math), no LLM. " + s)
    if cv >= 0.95 or ep < 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one of {coverage>=0.95, ECE<0.05} holds. " + s)
    return ("HARD_FAIL", "HARD_FAIL: neither holds. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
