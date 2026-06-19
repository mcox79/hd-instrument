"""
exp_asdiv_cascade_v2_cpu_v1.py -- substrate ASDiv cascade v2 (1-op + 2-op multi-step + verifier) -- CPU.

ROUTING: Research ASDiv cascade (v1 got 0.300; target 0.40). v1 was single-op only; ASDiv has MULTI-STEP problems. v2 adds a
  2-op composition fallback: try 1-op (predicted op, all pairs, verifier); if no plausible answer, try 2-op (predicted op-pair,
  all triples, verifier). Single-op-first, multi-step-fallback, both plausibility-filtered. op + op-pair classifiers trained on
  answer-consistency weak labels. Bundled ASDiv. Substrate-only, no LLM.
PRE-REGISTERED: HARD-PASS >= 0.40. MIDDLE >= 0.33 (lifts v1 0.300). HARD-FAIL < 0.30. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, json, itertools
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "asdiv_cascade_v2_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
B = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b if b != 0 else None}
OP1 = {"ADD": ("+", 0), "MUL": ("*", 0), "SUB_ab": ("-", 0), "SUB_ba": ("-", 1), "DIV_ab": ("/", 0), "DIV_ba": ("/", 1)}
OP1N = list(OP1.keys()); PAIRS = [(o1, o2) for o1 in B for o2 in B]
def _ev1(name, a, b):
    op, sw = OP1[name]; x, y = (b, a) if sw else (a, b); return B[op](x, y)
def _ev2(a, b, c, o1, o2):
    t = B[o1](a, b); return None if t is None else B[o2](t, c)
def _nums(t):
    out = []
    for m in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.])", t.replace(",", "")):
        try: out.append(Fraction(m))
        except Exception: pass
    return out
def _ans(x):
    m = re.search(r"-?\d+(?:\.\d+)?", str(x).replace(",", ""))
    try: return Fraction(m.group(0)).limit_denominator(10**6) if m else None
    except Exception: return None
def _feats(txt):
    low = txt.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether", "times", "share", "divide", "per", "gave", "lost", "spent", "all", "combined", "together", "equally", "groups", "rest", "difference", "then", "after"):
        if cue in low: fs.add("c:" + cue)
    fs.add("BIAS"); return fs
def _count_q(txt): return bool(re.search(r"how many", txt.lower()))
def _plaus(r, cq): return r is not None and r >= 0 and r <= 100000 and (not cq or r.denominator == 1)
def _selftest():
    assert _ev2(Fraction(6), Fraction(2), Fraction(3), "-", "*") == 12
    print("[selftest] PASS: asdiv-cascade-v2", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _train(X, labels, rng, ep):
    w = {l: defaultdict(float) for l in labels}; cw = {l: defaultdict(float) for l in labels}; c = 1
    for _ in range(ep):
        for i in rng.permutation(len(X)):
            feats, g = X[i]; sc = {l: sum(w[l][f] for f in feats) for l in labels}
            pred = max(labels, key=lambda l: (sc[l], l))
            if pred != g:
                for f in feats: w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    return {l: {f: w[l][f] - cw[l][f] / c for f in w[l]} for l in labels}
def _pred(avg, labels, feats):
    return max(labels, key=lambda l: (sum(avg[l].get(f, 0.0) for f in feats), l))
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1022")))
    try:
        rows = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    data = []
    for e in rows:
        txt = (e.get("body", "") + " " + e.get("question", "")).strip(); a = _ans(e.get("answer"))
        if txt and a is not None and len(_nums(txt)) >= 2: data.append((txt, a))
    if SMOKE: data = data[:200]
    idx = np.arange(len(data)); rng.shuffle(idx); cut = len(idx) // 2
    train = [data[i] for i in idx[:cut]]; test = [data[i] for i in idx[cut:]]
    def gold1(txt, ans):
        nums = _nums(txt)
        for a, b in itertools.permutations(nums, 2):
            for o in OP1N:
                if _ev1(o, a, b) == ans: return o
        return None
    def gold2(txt, ans):
        nums = _nums(txt)
        for a, b, c in itertools.permutations(nums[:5], 3):
            for (o1, o2) in PAIRS:
                r = _ev2(a, b, c, o1, o2)
                if r is not None and r == ans: return (o1, o2)
        return None
    X1 = []; X2 = []
    for txt, ans in train:
        g1 = gold1(txt, ans)
        if g1: X1.append((_feats(txt), g1)); continue
        g2 = gold2(txt, ans)
        if g2: X2.append((_feats(txt), g2))
    if not X1: return {"error": "no_train_labels", "accuracy": 0.0}
    EP = 12 if not SMOKE else 4
    a1 = _train(X1, OP1N, rng, EP); a2 = _train(X2, PAIRS, rng, EP) if X2 else None
    cor = 0; nT = len(test)
    for txt, ans in test:
        nums = _nums(txt); feats = _feats(txt); cq = _count_q(txt); pred_ans = None
        # 1-op: predicted op, all pairs, verifier; prefer question-proximal (later) numbers
        o1 = _pred(a1, OP1N, feats); cands = []
        for k1, k2 in itertools.permutations(range(len(nums)), 2):
            r = _ev1(o1, nums[k1], nums[k2])
            if _plaus(r, cq): cands.append((k1 + k2, r))
        if cands: pred_ans = max(cands, key=lambda x: x[0])[1]
        # 2-op fallback if no plausible 1-op
        if pred_ans is None and a2 is not None and len(nums) >= 3:
            op2 = _pred(a2, PAIRS, feats); c2 = []
            for k1, k2, k3 in itertools.permutations(range(min(len(nums), 5)), 3):
                r = _ev2(nums[k1], nums[k2], nums[k3], op2[0], op2[1])
                if _plaus(r, cq): c2.append((k1 + k2 + k3, r))
            if c2: pred_ans = max(c2, key=lambda x: x[0])[1]
        if pred_ans is not None and pred_ans == ans: cor += 1
    acc = cor / nT
    print("  ASDIV-CASCADE-v2: accuracy=%.3f (vs v1 0.300, prior 0.224) | 1op-train=%d 2op-train=%d n_test=%d" % (acc, len(X1), len(X2), nT), flush=True)
    return {"accuracy": round(acc, 3), "n_1op": len(X1), "n_2op": len(X2), "n_test": nT}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; s = "accuracy=%.3f (1op-train=%d, 2op-train=%d, n_test=%d)" % (a, r["n_1op"], r["n_2op"], r["n_test"])
    if a >= 0.40:
        return ("HARD_PASS", "HARD_PASS: ASDiv cascade v2 (1-op + 2-op multi-step + verifier) >=0.40 -- multi-step fallback + distractor-robust selection reach the target band, substrate-only. " + s)
    if a >= 0.33:
        return ("MIDDLE_BAND", "MIDDLE_BAND: v2 0.33-0.40 -- multi-step fallback lifts v1 (0.300); below 0.40. " + s)
    return ("HARD_FAIL", "HARD_FAIL: <0.30 -- v2 does not lift v1. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
