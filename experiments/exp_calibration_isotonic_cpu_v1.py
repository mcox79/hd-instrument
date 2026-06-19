"""
exp_calibration_isotonic_cpu_v1.py -- substrate classifier calibration (ECE) via isotonic/Venn-Abers -- CPU.

ROUTING: Research queue-closure experiment #4 (Venn-Abers calibration, ECE<0.05). The conformal #3 result showed the
  substrate-perceptron softmax is UNCALIBRATED (diffuse -> over-conservative conformal sets). This calibrates the top-class
  confidence with isotonic regression (the Venn-Abers core) fit on a held-out calibration split, and measures Expected
  Calibration Error (ECE) before vs after. Closes the calibration gap. Bundled-MBPP code-pattern classifier. No LLM.
PRE-REGISTERED: HARD-PASS post-calibration ECE < 0.05 AND ECE reduced vs raw. MIDDLE post-ECE < 0.10. HARD-FAIL >= 0.10. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "calibration_isotonic_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def _gold_type(code, prompt):
    c = code.lower(); pl = prompt.lower()
    fn = re.search(r"def\s+(\w+)", code); name = fn.group(1) if fn else ""
    if name and len(re.findall(r"\b" + re.escape(name) + r"\s*\(", code)) >= 2: return "RECURSION"
    if "sorted(" in c or ".sort(" in c or "heapq" in c: return "SORT"
    if any(s in pl for s in ("string", "char", "vowel", "palindrome", "letter", "word", "case", "substring", "reverse")) or any(s in c for s in (".join", ".split", ".replace", ".lower", ".upper", "ord(", "chr(")): return "STRING"
    if any(s in pl for s in ("prime", "factorial", "fibonacci", "gcd", "lcm", "divisor", "divisible", "power", "digit", "perfect number", "factor")): return "MATH"
    if any(s in pl for s in ("find", "search", "locate", "index of", "position")) or ".index(" in c or "bisect" in c: return "SEARCH"
    if any(s in pl for s in ("sum", "total", "count", "average", "product", "number of")) or "sum(" in c: return "ACCUMULATOR"
    if any(s in c for s in ("max(", "min(", "filter", "[x for", "[i for", "set(", "unique", "any(", "all(")) or any(s in pl for s in ("list", "array", "largest", "smallest", "maximum", "minimum")): return "LIST"
    return "MISC"
def _feats(prompt):
    low = prompt.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("BIAS"); return fs
def _ece(conf, correct, bins=10):
    conf = np.array(conf); correct = np.array(correct, dtype=float); n = len(conf); e = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        m = (conf > lo) & (conf <= hi)
        if m.sum() == 0: continue
        e += (m.sum() / n) * abs(correct[m].mean() - conf[m].mean())
    return e
def _isotonic(x, y):
    """pool-adjacent-violators isotonic regression; returns a step function f(x)."""
    order = np.argsort(x); xs = np.array(x)[order]; ys = np.array(y, dtype=float)[order]
    w = np.ones(len(ys)); vals = ys.copy()
    i = 0
    blocks = [[vals[k], w[k], xs[k], xs[k]] for k in range(len(vals))]   # value, weight, xmin, xmax
    merged = []
    for blk in blocks:
        merged.append(blk)
        while len(merged) >= 2 and merged[-2][0] > merged[-1][0]:
            v2, w2, a2, b2 = merged.pop(); v1, w1, a1, b1 = merged.pop()
            nw = w1 + w2; nv = (v1 * w1 + v2 * w2) / nw
            merged.append([nv, nw, a1, b2])
    def f(q):
        for v, _w, a, b in merged:
            if q <= b: return v
        return merged[-1][0]
    return f
def _selftest():
    assert abs(_ece([0.9, 0.9], [1, 1]) - 0.1) < 1e-9
    print("[selftest] PASS: calibration-isotonic", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1026")))
    try:
        ds = json.load(open(REPO / "experiments" / "data" / "mbpp" / "mbpp_full.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "ece_post": 1.0}
    def conv(sp): return [(e.get("text") or e.get("prompt") or "", e.get("code") or "") for e in ds[sp]]
    tr_raw = conv("train") + conv("validation") + (conv("prompt") if "prompt" in ds else [])
    train = [(t, _gold_type(c, t)) for t, c in tr_raw if t and c]
    pool = [(t, _gold_type(c, t)) for t, c in conv("test") if t and c]
    if SMOKE: train = train[:200]; pool = pool[:200]
    LAB = sorted(set(y for _t, y in train))
    Xtr = [(_feats(t), y) for t, y in train]
    w = {l: defaultdict(float) for l in LAB}; cw = {l: defaultdict(float) for l in LAB}; c = 1
    EP = 15 if not SMOKE else 4
    for ep in range(EP):
        for i in rng.permutation(len(Xtr)):
            feats, g = Xtr[i]; sc = {l: sum(w[l][f] for f in feats) for l in LAB}
            pred = max(LAB, key=lambda l: (sc[l], l))
            if pred != g:
                for f in feats: w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    avg = {l: {f: w[l][f] - cw[l][f] / c for f in w[l]} for l in LAB}
    def top(t):
        feats = _feats(t); sc = np.array([sum(avg[l].get(f, 0.0) for f in feats) for l in LAB])
        sc = sc - sc.max(); e = np.exp(sc); p = e / e.sum(); j = int(np.argmax(p)); return LAB[j], float(p[j])
    idx = rng.permutation(len(pool)); half = len(idx) // 2
    cal = [pool[i] for i in idx[:half]]; tst = [pool[i] for i in idx[half:]]
    # raw ECE on test (top-class confidence vs correctness)
    raw_conf = []; raw_corr = []
    for t, y in tst:
        pl, pc = top(t); raw_conf.append(pc); raw_corr.append(int(pl == y))
    ece_raw = _ece(raw_conf, raw_corr)
    # fit isotonic on calibration (confidence -> correctness), apply to test
    cc = []; cy = []
    for t, y in cal:
        pl, pc = top(t); cc.append(pc); cy.append(int(pl == y))
    f = _isotonic(cc, cy)
    cal_conf = [f(c0) for c0 in raw_conf]
    ece_post = _ece(cal_conf, raw_corr)
    print("  CALIBRATION-ISOTONIC: ECE raw=%.4f -> calibrated=%.4f | n_cal=%d n_test=%d" % (ece_raw, ece_post, len(cal), len(tst)), flush=True)
    return {"ece_raw": round(ece_raw, 4), "ece_post": round(ece_post, 4), "n_test": len(tst)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    pre = r["ece_raw"]; post = r["ece_post"]; s = "ECE raw=%.4f -> calibrated=%.4f (n_test=%d)" % (pre, post, r["n_test"])
    if post < 0.05 and post < pre:
        return ("HARD_PASS", "HARD_PASS: isotonic calibration reduces ECE to <0.05 -- substrate classifier confidences become calibrated probabilities (closes the conformal-#3 uncalibration finding). Substrate-classical calibrated uncertainty, no LLM. " + s)
    if post < 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: calibrated ECE <0.10 -- improves but above 0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: calibrated ECE >=0.10. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
