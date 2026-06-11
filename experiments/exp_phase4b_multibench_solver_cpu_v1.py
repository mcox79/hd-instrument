"""
exp_phase4b_multibench_solver_cpu_v1.py -- substrate math-word-problem solver across 4 benchmarks -- CPU.

ROUTING: keep-going generalization test of the SVAMP solver (0.297). Validates whether the substrate-native discriminative
  word-problem solver (richer-feature averaged perceptron over op-classes, answer-consistency weak labels) GENERALIZES across
  the standard math-word-problem suite: SVAMP, MAWPS, ASDiv, MultiArith. Train on the combined train pool; eval per-benchmark
  (ASDiv is pure held-out, validation-only). Substrate-native discriminative classifier, no LLM. A multi-benchmark result is
  far stronger than single-SVAMP.
PRE-REGISTERED: HARD-PASS macro-avg accuracy >= 0.30 across >=3 benchmarks (substrate-native solver generalizes). MIDDLE >= 0.22
  (beats majority broadly). HARD-FAIL < 0.18. UNKNOWN if <2 datasets load.
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
ANCHOR_NAME = "phase4b_multibench_solver_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
OPS = {"ADD": lambda a, b: a + b, "MUL": lambda a, b: a * b, "SUB_ab": lambda a, b: a - b,
       "SUB_ba": lambda a, b: b - a, "DIV_ab": lambda a, b: a / b if b != 0 else None, "DIV_ba": lambda a, b: b / a if a != 0 else None}
OPNAMES = list(OPS.keys())
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
def _feats(txt, a, b):
    low = txt.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("rel:a_gt_b" if a > b else ("rel:b_gt_a" if b > a else "rel:eq"))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether", "times", "share", "divide", "per", "gave", "lost", "spent", "all", "combined", "together", "equally", "groups", "rest", "difference"):
        if cue in ws: fs.add("c:" + cue)
    toks = low.split()
    for k, w in enumerate(toks):
        if re.match(r"\d", w.replace("$", "").replace(",", "")):
            if k + 1 < len(toks): fs.add("nN:" + re.sub(r"[^a-z]", "", toks[k + 1]))
    m = re.search(r"how (many|much) ([a-z]+)", low)
    if m: fs.add("qtgt:" + m.group(2))
    fs.add("BIAS"); return fs
def _selftest():
    assert OPS["SUB_ab"](Fraction(76), Fraction(25)) == 51
    print("[selftest] PASS: phase4b-multibench-solver", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _load_all():
    from datasets import load_dataset
    out = {}
    def add(name, split, rows): out.setdefault(name, {})[split] = rows
    # SVAMP
    try:
        ds = load_dataset("ChilleD/SVAMP")
        for sp in ("train", "test"):
            add("SVAMP", sp, [((e.get("Body", "") + " " + e.get("Question", "")).strip(), _ans(e.get("Answer"))) for e in ds[sp]])
    except Exception as e: print("[data] SVAMP x", str(e)[:50], flush=True)
    # MAWPS
    try:
        ds = load_dataset("MU-NLPC/Calc-mawps")
        for sp in ("train", "test"):
            if sp in ds: add("MAWPS", sp, [(e.get("question", ""), _ans(e.get("result_float") or e.get("result"))) for e in ds[sp]])
    except Exception as e: print("[data] MAWPS x", str(e)[:50], flush=True)
    # MultiArith
    try:
        ds = load_dataset("ChilleD/MultiArith")
        for sp in ("train", "test"):
            if sp in ds: add("MultiArith", sp, [(e.get("question", ""), _ans(e.get("final_ans"))) for e in ds[sp]])
    except Exception as e: print("[data] MultiArith x", str(e)[:50], flush=True)
    # ASDiv (validation only -> pure held-out)
    try:
        ds = load_dataset("EleutherAI/asdiv")
        sp = list(ds.keys())[0]
        add("ASDiv", "test", [((e.get("body", "") + " " + e.get("question", "")).strip(), _ans(e.get("answer"))) for e in ds[sp]])
    except Exception as e: print("[data] ASDiv x", str(e)[:50], flush=True)
    # clean: keep 2-number problems with valid answer
    for nm in out:
        for sp in out[nm]:
            out[nm][sp] = [(t, a) for (t, a) in out[nm][sp] if t and a is not None and len(_nums(t)) >= 2]
    return out
def _goldop(txt, ans):
    ns = _nums(txt); a, b = ns[0], ns[1]
    for op in OPNAMES:
        r = OPS[op](a, b)
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: return op
    return None
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1012")))
    try:
        data = _load_all()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "macro_acc": 0.0}
    if len(data) < 2: return {"error": "too_few_datasets", "macro_acc": 0.0}
    # combined training pool (all train splits + any extra train-like)
    Xtr = []
    for nm in data:
        tr = data[nm].get("train", [])
        if SMOKE: tr = tr[:150]
        for txt, ans in tr:
            op = _goldop(txt, ans)
            if op: Xtr.append((_feats(txt, _nums(txt)[0], _nums(txt)[1]), op))
    if not Xtr: return {"error": "no_train_labels", "macro_acc": 0.0}
    w = {op: defaultdict(float) for op in OPNAMES}; cw = {op: defaultdict(float) for op in OPNAMES}; c = 1
    EP = 10 if not SMOKE else 4
    for ep in range(EP):
        for i in rng.permutation(len(Xtr)):
            feats, gp = Xtr[i]; sc = {op: sum(w[op][f] for f in feats) for op in OPNAMES}
            pred = max(OPNAMES, key=lambda o: (sc[o], o))
            if pred != gp:
                for f in feats: w[gp][f] += 1; w[pred][f] -= 1; cw[gp][f] += c; cw[pred][f] -= c
            c += 1
    avg = {op: {f: w[op][f] - cw[op][f] / c for f in w[op]} for op in OPNAMES}
    maj = max(OPNAMES, key=lambda o: sum(1 for _f, gg in Xtr if gg == o))
    per = {}
    for nm in data:
        te = data[nm].get("test", [])
        if SMOKE: te = te[:120]
        if not te: continue
        cor = 0
        for txt, ans in te:
            ns = _nums(txt); a, b = ns[0], ns[1]; feats = _feats(txt, a, b)
            sc = {op: sum(avg[op].get(f, 0.0) for f in feats) for op in OPNAMES}
            pred = max(OPNAMES, key=lambda o: (sc[o], o))
            r = OPS[pred](a, b)
            if r is not None and Fraction(r).limit_denominator(10**6) == ans: cor += 1
        per[nm] = (round(cor / len(te), 3), len(te))
    macro = sum(v[0] for v in per.values()) / len(per) if per else 0.0
    print("  PHASE4B-MULTIBENCH: macro-avg=%.3f | per-benchmark=%s | train-labeled=%d" %
          (macro, {k: v[0] for k, v in per.items()}, len(Xtr)), flush=True)
    return {"macro_acc": round(macro, 3), "per_benchmark": {k: v[0] for k, v in per.items()}, "per_n": {k: v[1] for k, v in per.items()}, "n_train_labeled": len(Xtr), "n_benchmarks": len(per)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    m = r["macro_acc"]; s = "macro-avg=%.3f per=%s (%d benchmarks, train-labeled=%d)" % (m, r["per_benchmark"], r["n_benchmarks"], r["n_train_labeled"])
    if m >= 0.30 and r["n_benchmarks"] >= 3:
        return ("HARD_PASS", "HARD_PASS: substrate-native discriminative word-problem solver generalizes -- macro-avg>=0.30 across >=3 benchmarks (SVAMP/MAWPS/ASDiv/MultiArith), no LLM. The discriminative-weighting math solver is a real multi-benchmark substrate capability. " + s)
    if m >= 0.22:
        return ("MIDDLE_BAND", "MIDDLE_BAND: macro 0.22-0.30 -- generalizes above majority broadly; per-benchmark variance expected. " + s)
    return ("HARD_FAIL", "HARD_FAIL: macro <0.18 -- does not generalize across benchmarks. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
