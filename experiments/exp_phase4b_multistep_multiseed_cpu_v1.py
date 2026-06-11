"""
exp_phase4b_multistep_cpu_v1.py -- substrate MULTI-STEP word-problem solver (2-op composition) -- CPU.

ROUTING: keep-going extension of the multi-benchmark solver. MultiArith scored 0.022 because the single-op solver can't compose
  multiple operations. This builds a 2-step solver: ((a op1 b) op2 c) over the text-order numbers; answer-consistency finds the
  gold (op1,op2) pair (16 classes); a discriminative perceptron predicts the op-sequence from problem context. Reports the
  answer-consistency CEILING (fraction solvable by SOME 2-op sequence) AND the classifier accuracy. Substrate-native discriminative,
  no LLM. Tests whether multi-step composition is tractable + how much of the gap is reachability vs comprehension.
PRE-REGISTERED: HARD-PASS MultiArith classifier accuracy >= 0.20 (multi-step composition works substrate-only, >10x the 0.022
  single-op baseline). MIDDLE >= 0.10. HARD-FAIL < 0.06. Reports ceiling separately. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "phase4b_multistep_multiseed_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
BIN = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b if b != 0 else None}
OPS = list(BIN.keys())
PAIRS = [(o1, o2) for o1 in OPS for o2 in OPS]   # 16 two-step op sequences
def _nums(t):
    out = []
    for m in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.])", t.replace(",", "")):
        try: out.append(Fraction(m))
        except Exception: pass
    return out
def _ans(x):
    try: return Fraction(str(x).strip()).limit_denominator(10**6)
    except Exception:
        m = re.search(r"-?\d+(?:\.\d+)?", str(x)); return Fraction(m.group(0)).limit_denominator(10**6) if m else None
def _eval2(a, b, c, o1, o2):
    t = BIN[o1](a, b)
    if t is None: return None
    return BIN[o2](t, c)
def _feats(txt):
    low = txt.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether", "times", "share", "divide", "per", "gave", "lost", "spent", "all", "combined", "together", "equally", "groups", "rest", "difference", "twice", "double", "then", "after", "remaining"):
        if cue in ws: fs.add("c:" + cue)
    m = re.search(r"how (many|much) ([a-z]+)", low)
    if m: fs.add("qtgt:" + m.group(2))
    fs.add("BIAS"); return fs
def _selftest():
    assert _eval2(Fraction(64), Fraction(36), Fraction(4), "-", "/") == 7
    print("[selftest] PASS: phase4b-multistep-multiseed", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _load():
    from datasets import load_dataset
    ds = load_dataset("ChilleD/MultiArith")
    def conv(sp): return [(e.get("question", ""), _ans(e.get("final_ans"))) for e in ds[sp]]
    tr = [(t, a) for t, a in conv("train") if t and a is not None and len(_nums(t)) >= 3]
    te = [(t, a) for t, a in conv("test") if t and a is not None and len(_nums(t)) >= 3]
    return tr, te
def _goldpair(txt, ans):
    ns = _nums(txt)[:3]
    if len(ns) < 3: return None
    a, b, c = ns
    for (o1, o2) in PAIRS:
        r = _eval2(a, b, c, o1, o2)
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: return (o1, o2)
    return None
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1013")))
    try:
        train, test = _load()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    if SMOKE: train = train[:150]; test = test[:80]
    # answer-consistency ceiling + gold labels
    Xtr = []; tr_solvable = 0
    for txt, ans in train:
        gp = _goldpair(txt, ans)
        if gp is not None: Xtr.append((_feats(txt), gp)); tr_solvable += 1
    te_solvable = sum(1 for txt, ans in test if _goldpair(txt, ans) is not None)
    ceiling = te_solvable / len(test) if test else 0.0
    if not Xtr: return {"error": "no_train_labels", "accuracy": 0.0}
    LAB = PAIRS; SEEDS = [1, 2, 3] if SMOKE else [1, 2, 3, 4, 5]; vals = []
    for sd in SEEDS:
        srng = np.random.default_rng(sd)
        w = {p: defaultdict(float) for p in LAB}; cw = {p: defaultdict(float) for p in LAB}; c = 1
        EP = 12 if not SMOKE else 4
        for ep in range(EP):
            for i in srng.permutation(len(Xtr)):
                feats, gp = Xtr[i]; sc = {p: sum(w[p][f] for f in feats) for p in LAB}
                pred = max(LAB, key=lambda p: (sc[p], p))
                if pred != gp:
                    for f in feats: w[gp][f] += 1; w[pred][f] -= 1; cw[gp][f] += c; cw[pred][f] -= c
                c += 1
        avg = {p: {f: w[p][f] - cw[p][f] / c for f in w[p]} for p in LAB}
        cor = 0
        for txt, ans in test:
            ns = _nums(txt)[:3]; a, b, c3 = ns; feats = _feats(txt)
            pr = max(LAB, key=lambda p: (sum(avg[p].get(f, 0.0) for f in feats), p))
            r = _eval2(a, b, c3, pr[0], pr[1])
            if r is not None and Fraction(r).limit_denominator(10**6) == ans: cor += 1
        vals.append(round(cor / len(test), 4))
    mean = sum(vals) / len(vals); std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
    print("  PHASE4B-MULTISTEP n=%d (MultiArith): mean=%.4f std=%.4f vals=%s | ceiling=%.3f | train=%d" %
          (len(vals), mean, std, vals, ceiling, len(Xtr)), flush=True)
    return {"accuracy": round(mean, 3), "std": round(std, 4), "vals": vals, "ceiling": round(ceiling, 3), "n_seeds": len(vals), "n_test": len(test), "n_train_labeled": len(Xtr)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; s = "mean=%.4f std=%.4f " % (a, r.get("std", 0)) + "; detail-classifier-acc=%.3f ceiling=%.3f (n_test=%d, train-labeled=%d)" % (a, r["ceiling"], r["n_test"], r["n_train_labeled"])
    sd = r.get("std", 1.0)
    if a >= 0.20 and sd <= 0.03:
        return ("HARD_PASS", "HARD_PASS: substrate multi-step composition SEED-ROBUST on MultiArith (mean>=0.20, std<=0.03, n=%d) -- discriminative 2-op SEQUENCE prediction, no LLM. TIER A multi-step math capability. " % r.get("n_seeds", 5) + s)
    if a >= 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: multi-step 0.10-0.20 -- composition works above single-op baseline but op-sequence prediction is hard; ceiling shows headroom. " + s)
    return ("HARD_FAIL", "HARD_FAIL: multi-step <0.06 -- op-sequence not predictable from context (comprehension gap); ceiling=%.3f shows reachability vs predictability split. " % r["ceiling"] + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
