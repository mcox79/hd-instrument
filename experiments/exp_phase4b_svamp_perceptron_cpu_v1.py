"""
exp_phase4b_svamp_perceptron_cpu_v1.py -- Phase-4B-FULL option (c): discriminative-weighting op-classifier on SVAMP -- CPU.

ROUTING: Research PHASE4B_WALL ask, option (c). The bag-of-words substrate prototype got 0.110 on SVAMP (below majority) because
  cleanup/count scoring can't DISCRIMINATIVELY WEIGHT features. This tests whether discriminative weight-learning (an averaged
  perceptron over unigram + bigram + number-order features -> op-class) breaks that plateau. If it does, discriminative weighting
  is the missing mechanism (Research decides if the weighted-bundle framing counts as substrate-native). Gold op-class via
  answer-consistency on the two numbers. No LLM.
PRE-REGISTERED: HARD-PASS test accuracy >= 0.30 (discriminative weighting breaks the plateau; substrate-discriminative path viable).
  MIDDLE >= 0.20 (beats bag-of-words 0.110 + majority ~0.26). HARD-FAIL < 0.18 (no real lift). UNKNOWN if load fails.
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
ANCHOR_NAME = "phase4b_svamp_perceptron_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
OPS = {
    "ADD": lambda a, b: a + b, "MUL": lambda a, b: a * b,
    "SUB_ab": lambda a, b: a - b, "SUB_ba": lambda a, b: b - a,
    "DIV_ab": lambda a, b: a / b if b != 0 else None, "DIV_ba": lambda a, b: b / a if a != 0 else None,
}
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
    """discriminative features: unigrams + bigrams + number-order + cue words."""
    ws = re.findall(r"[a-z]+", txt.lower()); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("rel:a_gt_b" if a > b else ("rel:b_gt_a" if b > a else "rel:eq"))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether", "times", "share", "divide", "per", "gave", "lost", "spent"):
        if cue in ws: fs.add("c:" + cue)
    fs.add("BIAS")
    return fs
def _selftest():
    assert OPS["DIV_ba"](Fraction(2), Fraction(290)) == 145
    print("[selftest] PASS: phase4b-svamp-perceptron", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _load():
    from datasets import load_dataset
    ds = load_dataset("ChilleD/SVAMP")
    def conv(sp):
        out = []
        for ex in ds[sp]:
            txt = (ex.get("Body", "") + " " + ex.get("Question", "")).strip(); ans = _ans(ex.get("Answer"))
            if txt and ans is not None: out.append((txt, ans))
        return out
    return conv("train"), conv("test")
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1008")))
    try:
        train, test = _load()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    if SMOKE: train = train[:200]; test = test[:80]
    def gold(txt, ans):
        ns = _nums(txt)
        if len(ns) < 2: return None, None
        a, b = ns[0], ns[1]
        for op in OPNAMES:
            r = OPS[op](a, b)
            if r is not None and Fraction(r).limit_denominator(10**6) == ans: return op, (a, b)
        return None, (a, b)
    # build labeled training set
    Xtr = []
    for txt, ans in train:
        op, ab = gold(txt, ans)
        if op is None: continue
        Xtr.append((_feats(txt, ab[0], ab[1]), op))
    if not Xtr: return {"error": "no_train_labels", "accuracy": 0.0}
    # averaged perceptron (discriminative weight learning)
    w = {op: defaultdict(float) for op in OPNAMES}; cw = {op: defaultdict(float) for op in OPNAMES}; c = 1
    EPOCHS = 10 if not SMOKE else 4
    for ep in range(EPOCHS):
        order = rng.permutation(len(Xtr))
        for i in order:
            feats, g = Xtr[i]
            scores = {op: sum(w[op][f] for f in feats) for op in OPNAMES}
            pred = max(OPNAMES, key=lambda o: (scores[o], o))
            if pred != g:
                for f in feats: w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    avg = {op: {f: w[op][f] - cw[op][f] / c for f in w[op]} for op in OPNAMES}   # averaged weights
    maj = max(OPNAMES, key=lambda o: sum(1 for _f, gg in Xtr if gg == o))
    correct = 0; nT = 0
    for txt, ans in test:
        nT += 1; ns = _nums(txt)
        if len(ns) < 2:
            a = ns[0] if ns else Fraction(0); b = Fraction(0); pred = maj
        else:
            a, b = ns[0], ns[1]; feats = _feats(txt, a, b)
            scores = {op: sum(avg[op].get(f, 0.0) for f in feats) for op in OPNAMES}
            pred = max(OPNAMES, key=lambda o: (scores[o], o))
        r = OPS[pred](a, b)
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: correct += 1
    acc = correct / nT if nT else 0.0
    print("  PHASE4B-SVAMP-PERCEPTRON: test-accuracy=%.3f (%d/%d) | train-labeled=%d epochs=%d (vs bag-of-words 0.110, majority ~0.26)" %
          (acc, correct, nT, len(Xtr), EPOCHS), flush=True)
    return {"accuracy": round(acc, 3), "n_correct": correct, "n_test": nT, "n_train_labeled": len(Xtr)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; s = "accuracy=%.3f (%d/%d) train-labeled=%d" % (a, r["n_correct"], r["n_test"], r["n_train_labeled"])
    if a >= 0.30:
        return ("HARD_PASS", "HARD_PASS: discriminative weight-learning reaches >=0.30 on SVAMP -- discriminative weighting (option c) BREAKS the bag-of-words 0.110 plateau; the missing mechanism is feature weighting, not the substrate paradigm. " + s)
    if a >= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 0.20-0.30 -- discriminative weighting beats bag-of-words (0.110) + majority (0.26); partial, richer features/structure for 0.30. " + s)
    return ("HARD_FAIL", "HARD_FAIL: <0.18 -- even discriminative weighting can't solve SVAMP from these features; genuine syntactic structure (parse tree) needed. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
