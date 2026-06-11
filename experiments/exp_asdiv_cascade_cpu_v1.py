"""
exp_asdiv_cascade_cpu_v1.py -- substrate ASDiv cascade (op-gate + all-pairs + verifier) -- CPU.

ROUTING: Research ASDiv cascade AUTHORIZED (lift mixed-adversarial 0.224 -> 0.40+). ASDiv has DISTRACTOR numbers, so the
  first-2-numbers single-op solver picks wrong operands (0.224). Cascade: (1) op-classifier (discriminative perceptron, context
  -> op) = the type gate; (2) all-pairs enumeration over the problem numbers (extractive operand selection, not first-2 only);
  (3) VERIFIER (plausibility: positive, integer for count-questions, magnitude-reasonable) selects among candidate answers.
  Same shape as POS-tagger (route + per-route mechanism). Bundled ASDiv (RESCUE pattern). Substrate-only, no LLM.
PRE-REGISTERED: HARD-PASS accuracy >= 0.40. MIDDLE >= 0.30 (beats 0.224 baseline). HARD-FAIL < 0.25. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
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
ANCHOR_NAME = "asdiv_cascade_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
OPS = {"ADD": lambda a, b: a + b, "MUL": lambda a, b: a * b, "SUB_ab": lambda a, b: a - b,
       "SUB_ba": lambda a, b: b - a, "DIV_ab": lambda a, b: a / b if b != 0 else None, "DIV_ba": lambda a, b: b / a if a != 0 else None}
OPN = list(OPS.keys())
def _nums(t):
    out = []
    for m in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.])", t.replace(",", "")):
        try: out.append(Fraction(m))
        except Exception: pass
    return out
def _ans(x):
    m = re.search(r"-?\d+(?:\.\d+)?", str(x).replace(",", ""))
    if not m: return None
    try: return Fraction(m.group(0)).limit_denominator(10**6)
    except Exception: return None
def _feats(txt):
    low = txt.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether", "times", "share", "divide", "per", "gave", "lost", "spent", "all", "combined", "together", "equally", "groups", "rest", "difference"):
        if cue in low: fs.add("c:" + cue)
    fs.add("BIAS"); return fs
def _is_count_q(txt):
    return bool(re.search(r"how many", txt.lower()))
def _plausible(r, count_q):
    if r is None or r < 0 or r > 100000: return False
    if count_q and r.denominator != 1: return False
    return True
def _selftest():
    assert _plausible(Fraction(9), True) and not _plausible(Fraction(-1), True)
    print("[selftest] PASS: asdiv-cascade", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _load():
    rows = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8"))
    out = []
    for e in rows:
        txt = (e.get("body", "") + " " + e.get("question", "")).strip(); ans = _ans(e.get("answer"))
        if txt and ans is not None and len(_nums(txt)) >= 2: out.append((txt, ans))
    return out
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1021")))
    try:
        data = _load()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    if SMOKE: data = data[:200]
    idx = np.arange(len(data)); rng.shuffle(idx); cut = len(idx) // 2
    train = [data[i] for i in idx[:cut]]; test = [data[i] for i in idx[cut:]]
    def gold_op(txt, ans):
        nums = _nums(txt)
        for a, b in itertools.permutations(nums, 2):
            for op in OPN:
                r = OPS[op](a, b)
                if r is not None and r == ans: return op
        return None
    Xtr = []
    for txt, ans in train:
        op = gold_op(txt, ans)
        if op: Xtr.append((_feats(txt), op))
    if not Xtr: return {"error": "no_train_labels", "accuracy": 0.0}
    w = {o: defaultdict(float) for o in OPN}; cw = {o: defaultdict(float) for o in OPN}; c = 1
    EP = 12 if not SMOKE else 4
    for ep in range(EP):
        for i in rng.permutation(len(Xtr)):
            feats, g = Xtr[i]; sc = {o: sum(w[o][f] for f in feats) for o in OPN}
            pred = max(OPN, key=lambda o: (sc[o], o))
            if pred != g:
                for f in feats: w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    avg = {o: {f: w[o][f] - cw[o][f] / c for f in w[o]} for o in OPN}
    base_cor = 0; casc_cor = 0; nT = len(test)
    for txt, ans in test:
        nums = _nums(txt); feats = _feats(txt); cq = _is_count_q(txt)
        sc = {o: sum(avg[o].get(f, 0.0) for f in feats) for o in OPN}
        op = max(OPN, key=lambda o: (sc[o], o))
        rb = OPS[op](nums[0], nums[1]) if len(nums) >= 2 else None
        if rb is not None and rb == ans: base_cor += 1
        cands = []
        for k1, k2 in itertools.permutations(range(len(nums)), 2):
            r = OPS[op](nums[k1], nums[k2])
            if _plausible(r, cq): cands.append((k1 + k2, r))
        if not cands:
            for o2 in OPN:
                for k1, k2 in itertools.permutations(range(len(nums)), 2):
                    r = OPS[o2](nums[k1], nums[k2])
                    if _plausible(r, cq): cands.append((k1 + k2, r))
        pred_ans = max(cands, key=lambda x: x[0])[1] if cands else rb
        if pred_ans is not None and pred_ans == ans: casc_cor += 1
    base = base_cor / nT; casc = casc_cor / nT
    print("  ASDIV-CASCADE: cascade=%.3f vs baseline(first-2)=%.3f (vs prior 0.224) | train-labeled=%d n_test=%d" % (casc, base, len(Xtr), nT), flush=True)
    return {"accuracy": round(casc, 3), "baseline": round(base, 3), "n_train_labeled": len(Xtr), "n_test": nT}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; s = "cascade=%.3f baseline-first2=%.3f (n_test=%d, train-labeled=%d)" % (a, r["baseline"], r["n_test"], r["n_train_labeled"])
    if a >= 0.40:
        return ("HARD_PASS", "HARD_PASS: ASDiv cascade (op-gate + all-pairs extractive + verifier) >=0.40 -- distractor-robust operand selection lifts mixed-adversarial ASDiv, substrate-only. " + s)
    if a >= 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cascade 0.30-0.40 -- beats the 0.224 baseline; verifier/selection helps but below 0.40. " + s)
    return ("HARD_FAIL", "HARD_FAIL: <0.25 -- cascade does not lift ASDiv. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
