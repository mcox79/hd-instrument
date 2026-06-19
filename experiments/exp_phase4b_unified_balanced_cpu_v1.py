"""
exp_phase4b_unified_solver_cpu_v1.py -- unified arity-routed substrate math-word-problem solver -- CPU.

ROUTING: keep-going unification. Combines the single-op solver (MAWPS 0.81) + multi-step composition (MultiArith 0.75) into ONE
  substrate solver that auto-routes by problem arity: 2 numbers -> single-op discriminative classifier (6 op-classes); 3 numbers
  -> 2-op-sequence classifier (16 op-pair classes). Both trained on the combined 4-benchmark pool via answer-consistency weak
  labels. Eval per-benchmark with routing. This is the culmination substrate-native math-word-problem solver (no LLM); the
  unified macro should lift well above the single-op-only 0.336 (MultiArith joins at ~0.75).
PRE-REGISTERED: HARD-PASS unified macro-avg >= 0.45 across 4 benchmarks (arity-routing unifies single-op + multi-step). MIDDLE
  >= 0.36 (>= single-op-only Tier A). HARD-FAIL < 0.30. UNKNOWN if load fails.
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
ANCHOR_NAME = "phase4b_unified_balanced_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
BIN = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b if b != 0 else None}
OP1 = {"ADD": ("+", False), "MUL": ("*", False), "SUB_ab": ("-", False), "SUB_ba": ("-", True), "DIV_ab": ("/", False), "DIV_ba": ("/", True)}
OP1N = list(OP1.keys())
PAIRS = [(o1, o2) for o1 in BIN for o2 in BIN]
def _ev1(name, a, b):
    op, sw = OP1[name]; x, y = (b, a) if sw else (a, b); return BIN[op](x, y)
def _ev2(a, b, c, o1, o2):
    t = BIN[o1](a, b)
    return None if t is None else BIN[o2](t, c)
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
def _feats(txt):
    low = txt.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether", "times", "share", "divide", "per", "gave", "lost", "spent", "all", "combined", "together", "equally", "groups", "rest", "difference", "twice", "double", "then", "after", "remaining"):
        if cue in ws: fs.add("c:" + cue)
    toks = low.split()
    for k, w in enumerate(toks):
        if re.match(r"\d", w.replace("$", "").replace(",", "")):
            if k + 1 < len(toks): fs.add("nN:" + re.sub(r"[^a-z]", "", toks[k + 1]))
    m = re.search(r"how (many|much) ([a-z]+)", low)
    if m: fs.add("qtgt:" + m.group(2))
    fs.add("BIAS"); return fs
def _gold1(txt, ans):
    ns = _nums(txt); a, b = ns[0], ns[1]
    for nm in OP1N:
        r = _ev1(nm, a, b)
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: return nm
    return None
def _gold2(txt, ans):
    a, b, c = _nums(txt)[:3]
    for (o1, o2) in PAIRS:
        r = _ev2(a, b, c, o1, o2)
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: return (o1, o2)
    return None
def _train_perceptron(X, labels, rng, ep):
    w = {l: defaultdict(float) for l in labels}; cw = {l: defaultdict(float) for l in labels}; c = 1
    for _ in range(ep):
        for i in rng.permutation(len(X)):
            feats, g = X[i]; sc = {l: sum(w[l][f] for f in feats) for l in labels}
            pred = max(labels, key=lambda l: (sc[l], l))
            if pred != g:
                for f in feats: w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    return {l: {f: w[l][f] - cw[l][f] / c for f in w[l]} for l in labels}
def _predict(avg, labels, feats):
    sc = {l: sum(avg[l].get(f, 0.0) for f in feats) for l in labels}
    return max(labels, key=lambda l: (sc[l], l))
def _selftest():
    assert _ev2(Fraction(64), Fraction(36), Fraction(4), "-", "/") == 7 and _ev1("SUB_ab", Fraction(5), Fraction(3)) == 2
    print("[selftest] PASS: phase4b-unified-balanced", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _load_all():
    from datasets import load_dataset
    out = {}
    def clean(rows): return [(t, a) for t, a in rows if t and a is not None and len(_nums(t)) >= 2]
    try:
        ds = load_dataset("ChilleD/SVAMP")
        out["SVAMP"] = {sp: clean([((e.get("Body", "") + " " + e.get("Question", "")).strip(), _ans(e.get("Answer"))) for e in ds[sp]]) for sp in ("train", "test")}
    except Exception as e: print("[data] SVAMP x", str(e)[:40], flush=True)
    try:
        ds = load_dataset("MU-NLPC/Calc-mawps")
        out["MAWPS"] = {sp: clean([(e.get("question", ""), _ans(e.get("result_float") or e.get("result"))) for e in ds[sp]]) for sp in ("train", "test") if sp in ds}
    except Exception as e: print("[data] MAWPS x", str(e)[:40], flush=True)
    try:
        ds = load_dataset("ChilleD/MultiArith")
        out["MultiArith"] = {sp: clean([(e.get("question", ""), _ans(e.get("final_ans"))) for e in ds[sp]]) for sp in ("train", "test") if sp in ds}
    except Exception as e: print("[data] MultiArith x", str(e)[:40], flush=True)
    try:
        ds = load_dataset("EleutherAI/asdiv"); sp = list(ds.keys())[0]
        out["ASDiv"] = {"test": clean([((e.get("body", "") + " " + e.get("question", "")).strip(), _ans(e.get("answer"))) for e in ds[sp]])}
    except Exception as e: print("[data] ASDiv x", str(e)[:40], flush=True)
    return out
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1017")))
    try:
        data = _load_all()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "macro_acc": 0.0}
    if len(data) < 2: return {"error": "too_few_datasets", "macro_acc": 0.0}
    src1 = {}; src2 = {}
    for nm in data:
        tr = data[nm].get("train", [])
        if SMOKE: tr = tr[:150]
        s1 = []; s2 = []
        for txt, ans in tr:
            k = len(_nums(txt))
            if k == 2:
                g = _gold1(txt, ans)
                if g: s1.append((_feats(txt), g))
            elif k >= 3:
                g = _gold2(txt, ans)
                if g: s2.append((_feats(txt), g))
        if s1: src1[nm] = s1
        if s2: src2[nm] = s2
    # BALANCE: cap each source to the median per-source count (so MAWPS doesn't dominate the single-op classifier)
    def balance(src, brng):
        if not src: return []
        counts = sorted(len(v) for v in src.values()); cap = counts[len(counts) // 2]
        pool = []
        for nm, v in src.items():
            idx = brng.permutation(len(v))[:cap]; pool += [v[i] for i in idx]
        return pool
    brng = np.random.default_rng(20260611)
    X1 = balance(src1, brng); X2 = balance(src2, brng)
    if not X1: return {"error": "no_train_labels", "macro_acc": 0.0}
    bnames = [nm for nm in data if data[nm].get("test")]
    SEEDS = [1, 2, 3] if SMOKE else [1, 2, 3, 4, 5]; macros = []; perseed = defaultdict(list)
    for sd in SEEDS:
        srng = np.random.default_rng(sd); EP = 10 if not SMOKE else 4
        avg1 = _train_perceptron(X1, OP1N, srng, EP); avg2 = _train_perceptron(X2, PAIRS, srng, EP) if X2 else None
        per = {}
        for nm in bnames:
            te = data[nm].get("test", [])
            if SMOKE: te = te[:120]
            cor = 0
            for txt, ans in te:
                ns = _nums(txt); k = len(ns); feats = _feats(txt)
                if k == 2: pp = _predict(avg1, OP1N, feats); r = _ev1(pp, ns[0], ns[1])
                elif k >= 3 and avg2 is not None: pp = _predict(avg2, PAIRS, feats); r = _ev2(ns[0], ns[1], ns[2], pp[0], pp[1])
                else: r = None
                if r is not None and Fraction(r).limit_denominator(10**6) == ans: cor += 1
            per[nm] = cor / len(te); perseed[nm].append(round(cor / len(te), 3))
        macros.append(sum(per.values()) / len(per))
    mean = sum(macros) / len(macros); std = (sum((m - mean) ** 2 for m in macros) / len(macros)) ** 0.5
    per_mean = {nm: round(sum(v) / len(v), 3) for nm, v in perseed.items()}
    print("  PHASE4B-UNIFIED n=%d: macro-mean=%.3f std=%.4f | per=%s | train(1op=%d,2op=%d)" % (len(SEEDS), mean, std, per_mean, len(X1), len(X2)), flush=True)
    return {"macro_acc": round(mean, 3), "macro_std": round(std, 4), "per_benchmark": per_mean, "n_seeds": len(SEEDS), "n_benchmarks": len(bnames), "n_1op": len(X1), "n_2op": len(X2)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    m = r["macro_acc"]; s = "macro-mean=%.3f std=%.4f " % (m, r.get("macro_std", 0)) + "; per=%.3f per=%s (1-op-train=%d, 2-op-train=%d)" % (m, r["per_benchmark"], r["n_1op"], r["n_2op"])
    sd = r.get("macro_std", 1.0)
    if m >= 0.45 and sd <= 0.02:
        return ("HARD_PASS", "HARD_PASS: unified arity-routed solver SEED-ROBUST (macro-mean>=0.45, std<=0.02, n=%d) -- single-op + multi-step in ONE substrate solver, no LLM. TIER A primary substrate-math capability (per-benchmark-balanced training). " % r.get("n_seeds", 5) + s)
    if m >= 0.36:
        return ("MIDDLE_BAND", "MIDDLE_BAND: macro 0.36-0.45 -- unification helps (>= single-op-only Tier A 0.336) but below 0.45. " + s)
    return ("HARD_FAIL", "HARD_FAIL: macro <0.30. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
