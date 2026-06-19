"""
exp_math_wordproblem_extract_gate_cpu_v1.py -- keystone gate: NL word-problem -> computable structure extraction -- CPU.

ROUTING: keystone verify-before-invest (NL-extraction pipeline). MATH-LIGHT covered only clean-symbolic (~9%); word-problems
  are the gap. This GATE tests whether a substrate-style extraction front-end (number tokens + operation-keyword associative
  recall) can recover the COMPUTABLE STRUCTURE (quantities + operation) from level-1 word-problems and compute the answer.
  Pipeline per problem: extract numbers + percent markers; substrate-recall the operation from operation-keywords (difference/
  sum/product/of/more/less/total/times); compose a computation; compare to \boxed. Gates the multi-day dep-parser build:
  if simple extraction recovers structure at decent accuracy, the richer dep-parser is justified; if not, it quantifies difficulty.
PRE-REGISTERED: HARD-PASS extraction-accuracy >= 0.40 on attempted AND attempt-coverage >= 0.30 (extraction recovers structure
  -> dep-parser justified). MIDDLE accuracy >= 0.25. HARD-FAIL accuracy < 0.25 (even simple extraction fails -> harder than dep-parser).
  UNKNOWN if dataset load fails.
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
ANCHOR_NAME = "math_wordproblem_extract_gate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 4096
# substrate operation codebook: operation-keyword bundle -> operation (associative recall)
OP_KW = {
    "difference": ["difference", "minus", "less", "fewer", "decrease", "subtract"],
    "sum": ["sum", "total", "plus", "more", "altogether", "combined", "add"],
    "product": ["product", "times", "multiply", "each", "per", "every"],
    "quotient": ["quotient", "divide", "ratio", "split", "per"],
}
_BOOK = {}
_RNG = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "996")))
def _tok(w):
    if w not in _BOOK:
        ang = (_RNG.random(N) * 2 - 1) * math.pi; _BOOK[w] = np.exp(1j * ang).astype(np.complex64)
    return _BOOK[w]
def _bundle(words):
    v = np.zeros(N, dtype=np.complex64)
    for w in words: v = v + _tok(w)
    n = np.abs(v); n[n == 0] = 1; return (v / n).astype(np.complex64)
_OPVEC = None
def _opvecs():
    global _OPVEC
    if _OPVEC is None: _OPVEC = {op: _bundle(kws) for op, kws in OP_KW.items()}
    return _OPVEC
def _recall_op(text):
    qv = _bundle([w for w in re.findall(r"[a-z]+", text.lower())])
    ov = _opvecs(); sims = {op: float((v @ np.conj(qv)).real) for op, v in ov.items()}
    best = max(sims, key=sims.get)
    return best if sims[best] > 0.02 else None
def _boxed(sol):
    i = sol.find("oxed{")
    if i < 0: return None
    j = i + 5; depth = 1; out = []
    while j < len(sol) and depth > 0:
        c = sol[j]
        if c == "{": depth += 1
        elif c == "}": depth -= 1
        if depth > 0: out.append(c)
        j += 1
    return "".join(out)
def _to_frac(x):
    try:
        x = (x or "").replace("$", "").replace(",", "").replace("\\%", "").strip()
        if re.fullmatch(r"-?\d+(\.\d+)?", x): return Fraction(x).limit_denominator(10**6)
        if re.fullmatch(r"-?\d+/\d+", x): return Fraction(x)
        return None
    except Exception:
        return None
def _selftest():
    assert _recall_op("the positive difference between") == "difference"
    assert _boxed("$\\boxed{12}$") == "12"
    print("[selftest] PASS: math-wordproblem-extract-gate", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _extract_compute(q):
    """Extract quantities (incl 'N% of M') + operation; compose a value. Returns Fraction or None."""
    pcts = re.findall(r"(\d+(?:\.\d+)?)\s*\\?%\s*of\s*(\d+(?:\.\d+)?)", q)
    nums = [Fraction(n) for n in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.%])", q)]
    op = _recall_op(q)
    if pcts:
        vals = [Fraction(a) / 100 * Fraction(b) for a, b in pcts]
    else:
        vals = nums
    if len(vals) < 1: return None
    if op == "difference" and len(vals) >= 2: return abs(vals[0] - vals[1])
    if op == "sum" and len(vals) >= 2: return sum(vals)
    if op == "product" and len(vals) >= 2:
        r = Fraction(1)
        for v in vals: r *= v
        return r
    if op == "quotient" and len(vals) >= 2 and vals[1] != 0: return vals[0] / vals[1]
    if len(vals) == 1: return vals[0]
    return None
def run() -> Dict:
    try:
        from datasets import load_dataset
        probs = []
        for cfg in ["prealgebra", "algebra"]:
            ds = load_dataset("EleutherAI/hendrycks_math", cfg, split="test")
            probs += [x for x in ds if x.get("level") == "Level 1"]
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    if SMOKE: probs = probs[:40]
    attempted = 0; correct = 0
    for p in probs:
        gold = _to_frac(_boxed(p.get("solution", "")))
        if gold is None: continue
        val = _extract_compute(p["problem"])
        if val is None: continue
        attempted += 1
        correct += int(val == gold)
    nT = len(probs)
    cov = attempted / nT if nT else 0.0; acc = correct / attempted if attempted else 0.0
    print("  WORDPROBLEM-EXTRACT-GATE: attempt-coverage=%.3f (%d/%d) | accuracy-on-attempted=%.3f (%d/%d)" %
          (cov, attempted, nT, acc, correct, attempted), flush=True)
    return {"accuracy": round(acc, 3), "coverage": round(cov, 3), "n_attempted": attempted, "n_correct": correct, "n_total": nT}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    acc = r["accuracy"]; cov = r["coverage"]
    s = "accuracy=%.3f coverage=%.3f (%d/%d correct of attempted)" % (acc, cov, r["n_correct"], r["n_attempted"])
    if acc >= 0.40 and cov >= 0.30:
        return ("HARD_PASS", "HARD_PASS: substrate-style extraction recovers computable structure from word-problems (accuracy>=0.40 on coverage>=0.30) -- the NL-extraction front-end is viable; the richer dep-parser pipeline is JUSTIFIED to expand coverage. " + s)
    if acc >= 0.25:
        return ("MIDDLE_BAND", "MIDDLE_BAND: extraction accuracy 0.25-0.40 -- partial; dep-parser needed for robust quantity/operation extraction. " + s)
    return ("HARD_FAIL", "HARD_FAIL: extraction accuracy <0.25 -- even keyword+number extraction fails; word-problem understanding is harder than simple extraction (multi-step reasoning, not just quantity+op). " + s)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
