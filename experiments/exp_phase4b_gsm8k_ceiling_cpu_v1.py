"""
exp_phase4b_gsm8k_ceiling_cpu_v1.py -- GSM8K reachability ceiling for the substrate 1-2-op solver family -- CPU.

ROUTING: keep-going honest boundary. GSM8K is the standard hard math benchmark (2-8 step reasoning). The substrate solver family
  handles 1-op (2 numbers) + 2-op (3 numbers). This measures the ANSWER-CONSISTENCY CEILING on GSM8K: what fraction of problems
  is even REACHABLE by <=2 operations over the problem's numbers (upper bound for the solver family, before any classifier).
  A low ceiling honestly bounds the substrate math claim (handles simple word problems, not GSM8K multi-step). No LLM.
PRE-REGISTERED: this is a CEILING/diagnostic (not a pass/fail capability). Report 1-op + 2-op reachability. Interpretation:
  ceiling < 0.20 -> GSM8K needs deeper reasoning than the substrate 1-2-op family (honest boundary); ceiling > 0.40 -> deeper
  classifier worth building. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, itertools
from pathlib import Path
from typing import Dict, List, Tuple
from fractions import Fraction
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "phase4b_gsm8k_ceiling_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
BIN = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b if b != 0 else None}
def _nums(t):
    out = []
    for m in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.])", t.replace(",", "")):
        try: out.append(Fraction(m))
        except Exception: pass
    return out
def _final(ans):
    m = re.search(r"####\s*(-?[\d,]+(?:\.\d+)?)", ans)
    if m:
        try: return Fraction(m.group(1).replace(",", ""))
        except Exception: return None
    return None
def _one_op(nums, gold):
    for a, b in itertools.permutations(nums, 2):
        for op in BIN:
            r = BIN[op](a, b)
            if r is not None and r == gold: return True
    return False
def _two_op(nums, gold):
    for a, b, c in itertools.permutations(nums, 3):
        for o1 in BIN:
            t = BIN[o1](a, b)
            if t is None: continue
            for o2 in BIN:
                r = BIN[o2](t, c)
                if r is not None and r == gold: return True
    return False
def _selftest():
    assert _final("foo #### 9") == 9 and _two_op([Fraction(16), Fraction(3), Fraction(4)], Fraction(9))
    print("[selftest] PASS: phase4b-gsm8k-ceiling", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    try:
        from datasets import load_dataset
        ds = load_dataset("gsm8k", "main", split="test")
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "ceiling_2op": 0.0}
    probs = list(ds)
    if SMOKE: probs = probs[:120]
    CAP = 6   # cap to first 6 numbers (permutations bounded)
    n = 0; r1 = 0; r2 = 0
    for ex in probs:
        gold = _final(ex["answer"])
        if gold is None: continue
        nums = _nums(ex["question"])[:CAP]
        if len(nums) < 2: continue
        n += 1
        one = _one_op(nums, gold); two = one or (len(nums) >= 3 and _two_op(nums, gold))
        r1 += int(one); r2 += int(two)
    c1 = r1 / n if n else 0.0; c2 = r2 / n if n else 0.0
    print("  GSM8K-CEILING: 1-op-reachable=%.3f | <=2-op-reachable=%.3f (n=%d; first-%d-numbers)" % (c1, c2, n, CAP), flush=True)
    return {"ceiling_1op": round(c1, 3), "ceiling_2op": round(c2, 3), "n": n, "cap": CAP}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    c2 = r["ceiling_2op"]; s = "1-op=%.3f <=2-op=%.3f (n=%d)" % (r["ceiling_1op"], c2, r["n"])
    if c2 < 0.20:
        return ("HARD_FAIL", "HARD_FAIL (honest boundary): GSM8K <=2-op reachability <0.20 -- GSM8K needs DEEPER reasoning (2-8 steps) than the substrate 1-2-op solver family. Bounds the substrate math claim: strong on simple word problems (MAWPS 0.81/MultiArith 0.75), NOT GSM8K-level multi-step. " + s)
    if c2 < 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: GSM8K <=2-op reachability 0.20-0.40 -- partial; deeper-op classifier could capture this fraction. " + s)
    return ("HARD_PASS", "HARD_PASS: GSM8K <=2-op reachability >=0.40 -- a substantial fraction reachable; deeper classifier worth building. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
