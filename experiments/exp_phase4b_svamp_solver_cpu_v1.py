"""
exp_phase4b_svamp_solver_cpu_v1.py -- Phase-4B-FULL: substrate math-word-problem solver on SVAMP -- CPU.

ROUTING: Research PHASE_4B_FULL_WEAK_SUPERVISION_CONFIRMED (use MAWPS/ASDiv/SVAMP word-problem datasets). hendrycks level-1 is
  mostly SYMBOLIC (role-parser found only 2 answer-consistent labels there). SVAMP (ChilleD/SVAMP) is a real word-problem
  benchmark with gold Equation+Answer -- the right data for role-binding. Task: predict the arithmetic OPERATION + operand
  ORDER from problem context. Substrate-as-classifier (bag-of-words prototype per op-class, the validated intent mechanism);
  gold op-class via ANSWER-CONSISTENCY on the problem's two numbers (the op-class whose result == gold Answer). Substrate-only,
  no LLM. This is the genuine ceiling-breaker test on the RIGHT dataset.
PRE-REGISTERED: HARD-PASS test accuracy >= 0.30 (substrate-only SVAMP word-problem solving; small-LLM-competitive). MIDDLE >= 0.20.
  HARD-FAIL < 0.12 (~ majority-class). UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, re
from pathlib import Path
from typing import Dict, List, Tuple
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "phase4b_svamp_solver_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
# op-classes over the two text numbers (a, b) in text order
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
        m = re.search(r"-?\d+(?:\.\d+)?", str(x))
        return Fraction(m.group(0)).limit_denominator(10**6) if m else None
def _selftest():
    assert OPS["SUB_ab"](Fraction(76), Fraction(25)) == 51 and _nums("87 oranges and 290 bananas")[1] == 290
    print("[selftest] PASS: phase4b-svamp-solver", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _load():
    from datasets import load_dataset
    ds = load_dataset("ChilleD/SVAMP")
    def conv(sp):
        out = []
        for ex in ds[sp]:
            txt = (ex.get("Body", "") + " " + ex.get("Question", "")).strip()
            ans = _ans(ex.get("Answer"))
            if txt and ans is not None: out.append((txt, ans))
        return out
    return conv("train"), conv("test")
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1007")))
    try:
        train, test = _load()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    if SMOKE: train = train[:200]; test = test[:80]
    book = {}
    def tok(w):
        if w not in book:
            ang = (g.random(N) * 2 - 1) * math.pi; book[w] = np.exp(1j * ang).astype(np.complex64)
        return book[w]
    def bundle(words):
        v = np.zeros(N, dtype=np.complex64)
        for w in words: v = v + tok(w)
        return np.exp(1j * np.angle(v)).astype(np.complex64) if np.any(v) else v
    def gold_op(txt, ans):
        ns = _nums(txt)
        if len(ns) < 2: return None, ns
        a, b = ns[0], ns[1]
        for op in OPNAMES:
            r = OPS[op](a, b)
            if r is not None and Fraction(r).limit_denominator(10**6) == ans: return op, ns
        return None, ns
    # TRAIN: answer-consistency gold op-class -> substrate bag-of-words prototype per op
    proto_acc = {op: np.zeros(N, dtype=np.complex64) for op in OPNAMES}; counts = {op: 0 for op in OPNAMES}; n_lab = 0
    for txt, ans in train:
        op, ns = gold_op(txt, ans)
        if op is None: continue
        proto_acc[op] = proto_acc[op] + bundle(re.findall(r"[a-z]+", txt.lower())); counts[op] += 1; n_lab += 1
    proto = {op: (np.exp(1j * np.angle(proto_acc[op])).astype(np.complex64) if counts[op] else None) for op in OPNAMES}
    live = [op for op in OPNAMES if proto[op] is not None]
    P = np.stack([proto[op] for op in live]) if live else None
    if P is None: return {"error": "no_train_labels", "accuracy": 0.0}
    # majority op (prior fallback for <2-number or ambiguous)
    maj = max(OPNAMES, key=lambda o: counts[o])
    # EVAL on test
    correct = 0; nT = 0; covered = 0
    for txt, ans in test:
        nT += 1; ns = _nums(txt)
        if len(ns) < 2:
            pred_op = maj; a = ns[0] if ns else Fraction(0); b = Fraction(0)
        else:
            a, b = ns[0], ns[1]; v = bundle(re.findall(r"[a-z]+", txt.lower()))
            pred_op = live[int(np.argmax((P @ np.conj(v)).real))] if np.any(v) else maj; covered += 1
        r = OPS[pred_op](a, b)
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: correct += 1
    acc = correct / nT if nT else 0.0
    # op-class distribution (for context)
    dist = sorted(((op, counts[op]) for op in OPNAMES), key=lambda x: -x[1])
    print("  PHASE4B-SVAMP: test-accuracy=%.3f (%d/%d) | train-labeled=%d | op-dist=%s" %
          (acc, correct, nT, n_lab, dist[:4]), flush=True)
    return {"accuracy": round(acc, 3), "n_correct": correct, "n_test": nT, "n_train_labeled": n_lab, "maj_op": maj}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; s = "accuracy=%.3f (%d/%d) train-labeled=%d" % (a, r["n_correct"], r["n_test"], r["n_train_labeled"])
    if a >= 0.30:
        return ("HARD_PASS", "HARD_PASS: substrate-only SVAMP word-problem solver >=0.30 -- substrate-as-classifier predicts the arithmetic operation+order from problem context (answer-consistency weak supervision), no LLM. Phase-4B role-binding works on the right dataset; small-LLM-competitive. " + s)
    if a >= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: SVAMP 0.20-0.30 -- substrate op-classification works above majority but needs richer context/structure for 0.30. " + s)
    return ("HARD_FAIL", "HARD_FAIL: SVAMP <0.12 -- substrate context bag-of-words can't disambiguate the operation; needs syntactic structure (full dep-parser). " + s)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
