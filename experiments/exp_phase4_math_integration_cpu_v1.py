"""
exp_phase4_math_integration_cpu_v1 -- Phase-4 end-to-end MATH integration (schema->slot->solve) -- CPU.

ROUTING: Research Phase-4 integration. Composes the validated pipeline pieces on REAL hendrycks MATH level-1: (1) substrate
  schema retrieval (RT-1 mechanism) identifies the problem schema; (2) slot-fill binds quantities to the schema's roles by
  keyword-proximity; (3) the schema's constraint computes the answer. Tests whether the SCHEMA-DRIVEN pipeline beats the
  shallow word-problem gate (0.023) -- the schema supplies the structure shallow "numbers+op" extraction lacked. Focused on
  5 solvable schema types (rate-motion, percent-of, work-together, interest, direct-arithmetic). Substrate-only.
PRE-REGISTERED: HARD-PASS end-to-end accuracy >= 0.20 on level-1 (substrate-only math word-problem solving viable). MIDDLE >= 0.10
  (beats the 0.023 shallow baseline substantially -> schema pipeline is the right direction). HARD-FAIL < 0.05. UNKNOWN if load fails.
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
ANCHOR_NAME = "phase4_math_integration_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
SCHEMA_KW = {
    "rate_motion": ["rate", "speed", "travels", "traveling", "mph", "miles", "per", "hour", "distance", "fast", "drives"],
    "percent_of": ["percent", "%", "of"],
    "work_together": ["together", "work", "job", "complete", "hours", "finish", "rate"],
    "interest": ["interest", "principal", "invested", "annual", "compound"],
    "direct_arith": ["sum", "difference", "product", "total", "add", "subtract", "multiply", "divide", "evaluate", "simplify", "compute"],
}
NAMES = list(SCHEMA_KW.keys())
def _tok(t): return re.findall(r"[a-z]+", t.lower())
def _boxed(sol):
    i = sol.find("oxed{")
    if i < 0: return None
    j = i + 5; d = 1; out = []
    while j < len(sol) and d > 0:
        c = sol[j]
        if c == "{": d += 1
        elif c == "}": d -= 1
        if d > 0: out.append(c)
        j += 1
    return "".join(out)
def _frac(x):
    try:
        x = (x or "").replace("$", "").replace(",", "").replace("\\%", "").strip()
        if re.fullmatch(r"-?\d+(\.\d+)?", x): return Fraction(x).limit_denominator(10**6)
        if re.fullmatch(r"-?\d+/\d+", x): return Fraction(x)
        return None
    except Exception: return None
def _nums(q): return [Fraction(n) for n in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.%])", q)]
def _selftest():
    assert _boxed("$\\boxed{7}$") == "7" and _nums("a 60 mph car for 2 hours")[0] == 60
    print("[selftest] PASS: phase4-math-integration", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1003")))
    try:
        from datasets import load_dataset
        probs = []
        for cfg in ["prealgebra", "algebra"]:
            ds = load_dataset("EleutherAI/hendrycks_math", cfg, split="test")
            probs += [x for x in ds if x.get("level") == "Level 1"]
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    if SMOKE: probs = probs[:60]
    book = {}
    def tok(w):
        if w not in book:
            ang = (g.random(N) * 2 - 1) * math.pi; book[w] = np.exp(1j * ang).astype(np.complex64)
        return book[w]
    def bundle(words):
        v = np.zeros(N, dtype=np.complex64)
        for w in words: v = v + tok(w)
        return np.exp(1j * np.angle(v)).astype(np.complex64)
    proto = np.stack([bundle(SCHEMA_KW[nm]) for nm in NAMES])
    def solve(schema, q):
        pcts = re.findall(r"(\d+(?:\.\d+)?)\s*\\?%\s*of\s*(\d+(?:\.\d+)?)", q)
        nums = _nums(q)
        if schema == "percent_of" and pcts:
            vals = [Fraction(a) / 100 * Fraction(b) for a, b in pcts]
            if "difference" in q.lower() and len(vals) >= 2: return abs(vals[0] - vals[1])
            return vals[0]
        if schema == "rate_motion" and len(nums) >= 2:
            return nums[0] * nums[1]                          # distance = rate * time (asked=distance)
        if schema == "work_together" and len(nums) >= 2 and nums[0] != 0 and nums[1] != 0:
            return 1 / (1 / nums[0] + 1 / nums[1])            # combined rate
        if schema == "interest" and len(nums) >= 2:
            return nums[0] * nums[1] / 100                    # simple interest
        if schema == "direct_arith":
            expr = q
            expr = re.sub(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", expr)
            expr = expr.replace("\\times", "*").replace("\\cdot", "*").replace("$", "").replace("^", "**")
            m = re.search(r"[-+]?[0-9][0-9\.\+\-\*\/\(\)\s]*[0-9\)]", expr)
            if m:
                try: return Fraction(eval(m.group(0), {"__builtins__": {}}, {})).limit_denominator(10**6)
                except Exception: return None
        return None
    matched = 0; correct = 0
    for p in probs:
        gold = _frac(_boxed(p.get("solution", "")))
        if gold is None: continue
        v = bundle(_tok(p["problem"])); schema = NAMES[int(np.argmax((proto @ np.conj(v)).real))]
        ans = solve(schema, p["problem"])
        if ans is None: continue
        matched += 1; correct += int(ans == gold)
    nT = len(probs); cov = matched / nT if nT else 0.0; acc = correct / nT if nT else 0.0; acc_cov = correct / matched if matched else 0.0
    print("  PHASE4-MATH: end-to-end accuracy=%.3f (%d/%d) | schema-coverage=%.3f | acc-on-covered=%.3f (vs shallow-gate 0.023)" %
          (acc, correct, nT, cov, acc_cov), flush=True)
    return {"accuracy": round(acc, 3), "coverage": round(cov, 3), "acc_on_covered": round(acc_cov, 3), "n_correct": correct, "n_total": nT}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; s = "accuracy=%.3f coverage=%.3f acc-on-covered=%.3f (vs shallow 0.023)" % (a, r["coverage"], r["acc_on_covered"])
    if a >= 0.20:
        return ("HARD_PASS", "HARD_PASS: schema-driven pipeline solves real MATH level-1 end-to-end at accuracy>=0.20 substrate-only -- schema retrieval + slot-fill + constraint-solve composes; the validated pieces work together on real text. " + s)
    if a >= 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: end-to-end 0.10-0.20 -- schema pipeline BEATS the shallow 0.023 gate substantially (schema structure helps); expand schema coverage + slot-binding for 0.20. " + s)
    return ("HARD_FAIL", "HARD_FAIL: end-to-end <0.05 -- pieces don't compose on real text (slot-binding/asked-quantity ID is the gap). " + s)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
