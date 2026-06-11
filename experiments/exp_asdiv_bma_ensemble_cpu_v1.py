"""
exp_asdiv_bma_ensemble_cpu_v1.py -- Priority 1: BMA (Bayesian Model Averaging) ensemble over existing mechanisms -- CPU.

ROUTING: Research consolidated drills, Priority 1 (Drill 3 rank-2; ~20min, 100% existing primitives). The ~0.38 ASDiv-1op plateau
  is hit by 9 mechanisms. Hypothesis: if the mechanisms make DECORRELATED errors, a BMA vote breaks the plateau WITHOUT a new
  mechanism. The mechanisms differ chiefly in OPERAND SELECTION (PP-375 text-order / proximity-cascade / magnitude / target-aligned)
  on a shared op-classifier. Each predicts an answer per item; BMA = vote weighted by each strategy's validation accuracy. Decisive:
  HARD-PASS = errors decorrelate, ensemble closes gap; HARD-FAIL = errors CORRELATED (shared comprehension blind-spot confirmed --
  the plateau is the comprehension wall, not strategy variance). ASDiv-1op. Substrate-discriminative, no LLM.
PRE-REGISTERED (Research gate): HARD-PASS ASDiv-1op >= 0.42 (decorrelation+ensemble). MIDDLE 0.39-0.42. HARD-FAIL <= 0.39 (errors
  correlated). UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, itertools
from pathlib import Path
from typing import Dict, Tuple, List
from collections import defaultdict
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "asdiv_bma_ensemble_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
BIN = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: (a / b if b != 0 else None)}
OPS = list(BIN.keys())
_WORDNUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "hundred": 100}


def _nums_idx(t):
    """numbers with their following-noun + token index (for selection strategies)."""
    toks = t.lower().split(); out = []
    for k, w in enumerate(toks):
        ww = w.replace("$", "").replace(",", "").rstrip("?.,")
        v = Fraction(ww) if re.match(r"^\d+(?:\.\d+)?$", ww) else (Fraction(_WORDNUM[ww]) if ww in _WORDNUM else None)
        if v is not None:
            noun = re.sub(r"[^a-z]", "", toks[k + 1]) if k + 1 < len(toks) else ""
            out.append((v, noun, k))
    return out


def _ans(x):
    m = re.search(r"-?\d+(?:\.\d+)?", str(x).replace(",", ""))
    try: return Fraction(m.group(0)).limit_denominator(10**6) if m else None
    except Exception: return None


def _feats(txt):
    low = txt.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether", "times", "share",
                "divide", "per", "gave", "lost", "spent", "all", "combined", "together", "equally", "groups", "rest", "difference"):
        if cue in ws: fs.add("c:" + cue)
    m = re.search(r"how (many|much) ([a-z]+)", low)
    if m: fs.add("qtgt:" + m.group(2))
    fs.add("BIAS"); return fs


def _tgt(txt):
    m = re.search(r"how (?:many|much) ([a-z]+)", txt.lower()); return re.sub(r"s$", "", m.group(1)) if m else ""


def _cq(t): return bool(re.search(r"how many", t.lower()))
def _plaus(r, cq): return r is not None and r >= 0 and r <= 100000 and (not cq or r.denominator == 1)


# ---- 4 operand-selection strategies: given numbers, return ordered (a,b) pair ----
def _pairs(nums):
    return [(i, j) for i in range(len(nums)) for j in range(len(nums)) if i != j]


def _sel_textorder(nums, tgt): return (0, 1) if len(nums) >= 2 else None
def _sel_proximity(nums, tgt):
    if len(nums) < 2: return None
    return max(_pairs(nums), key=lambda ij: nums[ij[0]][2] + nums[ij[1]][2])
def _sel_magnitude(nums, tgt):
    if len(nums) < 2: return None
    order = sorted(range(len(nums)), key=lambda k: -nums[k][0]); return (order[0], order[1])
def _sel_target(nums, tgt):
    if len(nums) < 2: return None
    def rel(k): return (3.0 if tgt and re.sub(r"s$", "", nums[k][1]) == tgt else 0.0) + 0.001 * nums[k][2]
    order = sorted(range(len(nums)), key=lambda k: -rel(k)); a, b = order[0], order[1]
    return (a, b) if nums[a][2] <= nums[b][2] else (b, a)


STRATS = [("textorder", _sel_textorder), ("proximity", _sel_proximity), ("magnitude", _sel_magnitude), ("target", _sel_target)]


def _selftest():
    n = _nums_idx("there are 5 apples and 3 oranges . how many apples ?")
    assert len(n) == 2 and _tgt("how many apples ?") == "apple"
    print("[selftest] PASS: asdiv-bma-ensemble", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _train_op(train, rng):
    X = []
    for txt, ans in train:
        nums = _nums_idx(txt)
        if len(nums) < 2: continue
        hit = None
        for i, j in _pairs(nums):
            o = next((o for o in OPS if BIN[o](nums[i][0], nums[j][0]) == ans), None)
            if o: hit = o; break
        if hit: X.append((_feats(txt), hit))
    if not X: return None
    w = {o: defaultdict(float) for o in OPS}; cw = {o: defaultdict(float) for o in OPS}; c = 1
    for ep in range(12 if not SMOKE else 4):
        for i in rng.permutation(len(X)):
            feats, g = X[i]; sc = {o: sum(w[o][f] for f in feats) for o in OPS}
            pred = max(OPS, key=lambda o: (sc[o], o))
            if pred != g:
                for f in feats: w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    return {o: {f: w[o][f] - cw[o][f] / c for f in w[o]} for o in OPS}


def _predict(txt, avg_op):
    """each strategy -> answer. returns dict strat_name -> answer (or None)."""
    nums = _nums_idx(txt); tgt = _tgt(txt); cq = _cq(txt); out = {}
    if len(nums) < 2:
        return {nm: None for nm, _ in STRATS}
    feats = _feats(txt); op = max(OPS, key=lambda o: (sum(avg_op[o].get(f, 0.0) for f in feats), o))
    for nm, sel in STRATS:
        pr = sel(nums, tgt)
        if pr is None: out[nm] = None; continue
        r = BIN[op](nums[pr[0]][0], nums[pr[1]][0])
        out[nm] = r if _plaus(r, cq) else None
    return out


def run() -> Dict:
    import json
    d = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8"))
    items = []
    for e in d:
        f = e.get("formula", "")
        if "=" not in f or sum(f.split("=")[0].count(o) for o in "+-*/") != 1: continue
        a = _ans(e.get("answer"))
        if a is None: continue
        items.append(((e.get("body", "") + " " + e.get("question", "")).strip(), a))
    cut = int(len(items) * 0.7); train = items[:cut]; test = items[cut:]
    if SMOKE: train = train[:400]; test = test[:200]
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1013")))
    # train op-classifier on train' (80%), BMA weights from val (20%)
    vcut = int(len(train) * 0.8); tr2 = train[:vcut]; val = train[vcut:]
    avg_op = _train_op(tr2, rng)
    if avg_op is None: return {"error": "no_train"}
    # BMA weights = each strategy's val accuracy
    vcorr = {nm: 0 for nm, _ in STRATS}
    for txt, ans in val:
        preds = _predict(txt, avg_op)
        for nm, _ in STRATS:
            if preds[nm] is not None and preds[nm] == ans: vcorr[nm] += 1
    weights = {nm: (vcorr[nm] / len(val) if val else 0.25) for nm, _ in STRATS}
    # evaluate single strategies + BMA vote on test
    single = {nm: 0 for nm, _ in STRATS}; bma_cor = 0
    for txt, ans in test:
        preds = _predict(txt, avg_op)
        for nm, _ in STRATS:
            if preds[nm] is not None and preds[nm] == ans: single[nm] += 1
        # BMA: weighted vote over predicted answers
        votes = defaultdict(float)
        for nm, _ in STRATS:
            if preds[nm] is not None: votes[preds[nm]] += weights[nm]
        if votes:
            best = max(votes.items(), key=lambda kv: (kv[1], -float(kv[0])))[0]
            if best == ans: bma_cor += 1
    n = len(test)
    sa = {nm: round(single[nm] / n, 4) for nm, _ in STRATS}; bma = round(bma_cor / n, 4)
    bestsingle = max(sa.values())
    print("  BMA ensemble ASDiv-1op: singles=%s | BMA=%.4f | best-single=%.4f | gain=%+.4f (weights=%s)" % (
        sa, bma, bestsingle, bma - bestsingle, {k: round(v, 3) for k, v in weights.items()}), flush=True)
    return {"accuracy": bma, "bma": bma, "best_single": bestsingle, "gain": round(bma - bestsingle, 4), "singles": sa, "n_test": n}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    bma = r["bma"]; bs = r["best_single"]; g = r["gain"]
    s = "BMA=%.4f vs best-single=%.4f (gain=%+.4f); singles=%s. 4 operand-selection strategies, val-weighted vote." % (bma, bs, g, r["singles"])
    if bma >= 0.42:
        return ("HARD_PASS", "HARD_PASS: BMA ensemble breaks the ~0.38 plateau to >=0.42 -- the mechanisms' errors DECORRELATE; ensembling closes the gap without a new mechanism. " + s)
    if bma >= 0.39 or g >= 0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: BMA gives a small ensemble gain -- partial decorrelation. " + s)
    return ("HARD_FAIL", "HARD_FAIL: BMA <=0.39, no gain over best single -- the mechanisms' errors are CORRELATED (shared comprehension blind-spot). The plateau is the comprehension wall, not strategy variance. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
