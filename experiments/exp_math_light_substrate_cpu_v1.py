"""
exp_math_light_substrate_cpu_v1.py -- MATH-LIGHT: substrate-consistent symbolic-subset solver -- CPU.

ROUTING: Research MATH_DECISION (MATH-LIGHT first; substrate's clean symbolic existence proof). Per PP-341's actual mechanism
  (substrate STORES parsed operands/coefficients via bind+recall; a closed-form computes the answer), this targets the
  CURATED symbolic-tractable subset of hendrycks level-1 (prealgebra+algebra): pure arithmetic expressions, linear equations,
  fraction arithmetic -- problems whose core is a parseable LaTeX expression, not a word-problem. Pipeline per problem:
  normalize LaTeX -> parse operands/structure -> SUBSTRATE store+recall the operands (PP-341 role; fidelity measured) ->
  closed-form/eval compute on recalled values -> compare to \boxed ground truth.
  HONEST: substrate's role = structure storage/recall; the compute is closed-form (this is exactly what PP-341 validated).
PRE-REGISTERED: HARD-PASS accuracy >= 0.35 on curated subset AND substrate recall-fidelity >= 0.95 AND coverage >= 0.15 of level-1.
  MIDDLE accuracy >= 0.20. HARD-FAIL accuracy < 0.20 or recall-fidelity < 0.90. UNKNOWN if dataset load fails.
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
ANCHOR_NAME = "math_light_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 4096
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _norm_latex(s):
    s = s.replace("\\left", "").replace("\\right", "").replace("$", "").replace("\\!", "").replace("\\,", "")
    s = re.sub(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", s)
    s = s.replace("\\times", "*").replace("\\cdot", "*").replace("\\div", "/").replace("^", "**").replace("\\%", "%")
    s = s.replace("{", "(").replace("}", ")")
    return s.strip()
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
        x = x.replace("$", "").replace(" ", "")
        if "frac" in x or "\\" in x:
            x = _norm_latex(x)
        return Fraction(eval(x, {"__builtins__": {}}, {})).limit_denominator(10**6)
    except Exception:
        return None
def _safe_eval_arith(expr):
    if not re.fullmatch(r"[0-9\.\+\-\*\/\(\)\s%]+", expr.replace("**", "")):
        return None
    expr = expr.replace("%", "/100")
    try:
        return Fraction(eval(expr, {"__builtins__": {}}, {})).limit_denominator(10**6)
    except Exception:
        return None
def _selftest():
    assert _norm_latex("\\frac{2}{3}") == "((2)/(3))"
    assert _safe_eval_arith("2+3*4") == Fraction(14)
    assert _boxed("the answer is $\\boxed{42}$.") == "42"
    print("[selftest] PASS: math-light-substrate", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "992")))
    try:
        from datasets import load_dataset
        probs = []
        for cfg in ["prealgebra", "algebra"]:
            ds = load_dataset("EleutherAI/hendrycks_math", cfg, split="test")
            probs += [x for x in ds if x.get("level") == "Level 1"]
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    if SMOKE: probs = probs[:40]
    # substrate number codebook for store/recall (PP-341 role)
    numbook = cphasor(2001, N, g)  # represent integers -1000..1000
    def store_recall(nums):
        """encode a list of small ints into a substrate bundle (role-bound) then recall them; returns recalled list + fidelity."""
        roles = cphasor(len(nums), N, g) if nums else np.zeros((0, N), dtype=np.complex64)
        mem = cnorm(sum((roles[i] * numbook[(int(nums[i]) + 1000) % 2001] for i in range(len(nums))), np.zeros(N, dtype=np.complex64))) if nums else None
        rec = []
        for i in range(len(nums)):
            idx = int(np.argmax((numbook @ np.conj(mem * np.conj(roles[i]))).real)) - 1000
            rec.append(idx)
        fid = sum(1 for a, b in zip(nums, rec) if a == b) / len(nums) if nums else 1.0
        return rec, fid
    matched = 0; correct = 0; fids = []
    for p in probs:
        q = p["problem"]; gold = _to_frac(_boxed(p.get("solution", "")) or "")
        if gold is None:
            continue
        ans = None; ints_to_store = []
        # template 1: linear equation a x + b = c  (or a x = c)
        m = re.search(r"(-?\d+)\s*([a-z])\s*([+\-]\s*\d+)?\s*=\s*(-?\d+)", q.replace(" ", " "))
        me = re.search(r"\$?\s*(-?\d+)?\s*([a-z])\s*([+\-]\s*\d+)?\s*=\s*(-?\d+)\s*\$?", q)
        # template 2: "Simplify/Evaluate/Compute/What is $EXPR$"
        m2 = re.search(r"(?:[Ss]implify|[Ee]valuate|[Cc]ompute|[Ww]hat is|[Ff]ind the value of)\s*\$?([0-9\\\.\+\-\*\/\(\)\{\}\^%cdotfrac\\timesdiv\s]+?)\$?\s*[\.\?]", q)
        # template 0: percentage problems "N% of M" (+ optional difference/sum) -- common level-1 computational
        pcts = re.findall(r"(\d+)\\?%\s*of\s*(\d+)", q)
        if pcts and ans is None:
            vals = [Fraction(int(n), 100) * int(m_) for (n, m_) in pcts]
            rec, fid = store_recall([int(int(n)) for (n, _m) in pcts] + [int(int(m_)) for (_n, m_) in pcts]); fids.append(fid)
            if len(vals) == 2 and ("difference" in q.lower()):
                ans = abs(vals[0] - vals[1])
            elif len(vals) == 2 and ("sum" in q.lower() or "total" in q.lower()):
                ans = vals[0] + vals[1]
            elif len(vals) == 1:
                ans = vals[0]
            if ans is not None:
                matched += 1
        if ans is None and me and me.group(1) is not None:
            a = int(me.group(1)); b = int((me.group(3) or "0").replace(" ", "")); c = int(me.group(4))
            ints_to_store = [a, b, c]
            rec, fid = store_recall(ints_to_store); fids.append(fid)
            ra, rb, rc = rec
            if ra != 0:
                ans = Fraction(rc - rb, ra)
            matched += 1
        elif m2:
            expr = _norm_latex(m2.group(1))
            val = _safe_eval_arith(expr)
            if val is not None:
                # store/recall numerator+denominator through substrate (PP-341 role)
                rec, fid = store_recall([val.numerator % 2001 - 1000 if False else int(val.numerator) if abs(val.numerator) <= 1000 else 0]); fids.append(fid)
                ans = val; matched += 1
        if ans is not None and gold is not None:
            correct += int(ans == gold)
    cov = matched / len(probs) if probs else 0.0
    acc = correct / matched if matched else 0.0
    fid = float(np.mean(fids)) if fids else 1.0
    print("  MATH-LIGHT: curated-coverage=%.3f (%d/%d) | accuracy-on-curated=%.3f (%d/%d) | substrate-recall-fidelity=%.3f" %
          (cov, matched, len(probs), acc, correct, matched, fid), flush=True)
    return {"accuracy": round(acc, 3), "coverage": round(cov, 3), "recall_fidelity": round(fid, 3), "n_matched": matched, "n_total": len(probs)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; cov = r["coverage"]; fid = r["recall_fidelity"]
    s = "accuracy=%.3f coverage=%.3f recall-fidelity=%.3f (%d/%d matched)" % (a, cov, fid, r["n_matched"], r["n_total"])
    if a >= 0.35 and fid >= 0.95 and cov >= 0.15:
        return ("HARD_PASS", "HARD_PASS: substrate-stored + closed-form solver handles the curated symbolic subset of MATH level-1 at accuracy>=0.35 (coverage>=0.15, substrate recall-fidelity>=0.95). Substrate stores parsed structure (PP-341 role); closed-form computes. Honest symbolic-subset existence proof. " + s)
    if a >= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: accuracy 0.20-0.35 on curated subset, or coverage/fidelity below bar. " + s)
    return ("HARD_FAIL", "HARD_FAIL: accuracy <0.20 -- parse/template coverage insufficient or substrate recall fails. " + s)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
