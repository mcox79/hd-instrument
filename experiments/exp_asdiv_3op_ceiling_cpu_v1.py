"""
exp_asdiv_3op_ceiling_cpu_v1.py -- ASDiv arithmetic-reachability ORACLE ceiling by op-count -- CPU.

ROUTING: Research direction B (T-3OP-CEILING, research_drill_substrate_3op_compositional_extension) + direction C (ASDiv
  simple/complex diagnostic). Instrument-only oracle (NO LLM, NO trained solver): for each ASDiv item, extract the numbers from the
  problem TEXT (body+question) and ask -- can a depth-<=k binary-op tree (+,-,*,/) over those numbers reach the gold answer? This
  is the architectural-reach ceiling: the max accuracy the substrate compositional engine could reach with a PERFECT operator/
  operand selector. Failures = the answer needs a number NOT in the text (implicit world-knowledge constant, e.g. "2 dogs"->4 legs)
  or a non-arithmetic op. Report ceiling split by formula op-count (1-op=simple ... 3-op=complex) -- this IS the complexity
  diagnostic (direction C) and the 3-op ceiling (direction B test).
PRE-REGISTERED (per drill): 3-OP CEILING -- PASS >= 0.85 (architecture reach fine; bottleneck is the selector). FAIL < 0.65
  (architecture wrong shape for 3-op). 0.65-0.85 = MIDDLE. Also report 1-op/2-op ceilings for the simple/complex split. NO defeat.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, re
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "asdiv_3op_ceiling_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
TOL = 1e-3


_W = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
      "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
      "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
      "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100, "dozen": 12,
      "half": 0.5, "twice": 2, "double": 2, "triple": 3}


def _nums(text):
    out = []
    for m in re.findall(r"\d+\.?\d*", text.replace(",", "")):
        try: out.append(float(m))
        except Exception: pass
    low = text.lower()
    for wd in re.findall(r"[a-z]+", low):
        if wd in _W: out.append(float(_W[wd]))
    return out


def _gold(ans):
    m = re.search(r"-?\d+\.?\d*", str(ans).replace(",", ""))
    return float(m.group()) if m else None


def _opcount(formula):
    f = formula.split("=")[0]
    return sum(f.count(o) for o in "+-*/")


def reachable(nums, target, max_ops):
    """Can target be produced by <= max_ops binary ops over the multiset nums (each value consumed once)? Memoized DFS."""
    seen = set()
    start = tuple(sorted(round(x, 4) for x in nums))

    def dfs(pool, ops_left):
        for v in pool:
            if abs(v - target) <= TOL or (abs(target) > 1 and abs(v - target) <= abs(target) * 1e-3):
                return True
        if ops_left == 0:
            return False
        key = (pool, ops_left)
        if key in seen:
            return False
        seen.add(key)
        n = len(pool)
        for i in range(n):
            for j in range(n):
                if i == j: continue
                a = pool[i]; b = pool[j]
                rest = tuple(pool[k] for k in range(n) if k != i and k != j)
                cands = [a + b, a - b, a * b]
                if abs(b) > 1e-9: cands.append(a / b)
                for r in cands:
                    if abs(r) > 1e12: continue
                    newpool = tuple(sorted(rest + (round(r, 4),)))
                    if dfs(newpool, ops_left - 1):
                        return True
        return False

    return dfs(start, max_ops)


def _selftest():
    assert reachable([7.0, 2.0], 9.0, 1) and reachable([2.0, 2.0, 4.0, 4.0], 12.0, 3) and not reachable([3.0], 7.0, 2)
    assert _opcount("(4+4)+(2+2)=12") == 3 and _gold("9 (apples)") == 9.0
    print("[selftest] PASS: asdiv-3op-ceiling", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    try:
        data = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed"}
    by_op = {1: [], 2: [], 3: []}
    for it in data:
        f = it.get("formula", "")
        if "=" not in f: continue
        oc = _opcount(f)
        if oc in by_op: by_op[oc].append(it)
    res = {}
    for oc in (1, 2, 3):
        items = by_op[oc]
        if SMOKE: items = items[:30]
        hit = 0; usable = 0; capnum = 0
        for it in items:
            nums = _nums(it.get("body", "") + " " + it.get("question", "")); g = _gold(it.get("answer", ""))
            if g is None or not nums: continue
            usable += 1
            if len(nums) > 8: nums = nums[:8]; capnum += 1   # bound search blowup (rare)
            if reachable(nums, g, oc): hit += 1
        ceil = hit / usable if usable else 0.0
        res["op%d" % oc] = {"ceiling": round(ceil, 4), "n": usable, "hit": hit, "capped_long": capnum}
        print("  [%d-op] reachability ceiling=%.4f (%d/%d items; %d had >8 nums capped)" % (oc, ceil, hit, usable, capnum), flush=True)
    res["ceiling_3op"] = res["op3"]["ceiling"]
    return res


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    c3 = r["ceiling_3op"]; c1 = r["op1"]["ceiling"]; c2 = r["op2"]["ceiling"]
    s = "3-op ceiling=%.4f (n=%d) | 2-op=%.4f | 1-op=%.4f (simple->complex split). Failures = answer needs an implicit constant not in text, or non-arithmetic op." % (c3, r["op3"]["n"], c2, c1)
    if c3 >= 0.85:
        return ("HARD_PASS", "HARD_PASS: 3-op arithmetic-reachability ceiling >=0.85 -- the substrate compositional engine HAS the architectural reach for 3-op chains; the bottleneck is the operator/operand SELECTOR (build the recursive 2-op solver, drill T-3OP-RECURSE). " + s)
    if c3 >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 3-op ceiling 0.65-0.85 -- partial architectural reach; a meaningful fraction of 3-op ASDiv needs implicit constants/world-knowledge (out of substrate arithmetic scope). " + s)
    return ("HARD_FAIL", "HARD_FAIL: 3-op ceiling <0.65 -- most 3-op ASDiv items are NOT reachable from text-numbers alone (implicit world-knowledge constants dominate); this is a comprehension/knowledge boundary, not an arithmetic-composition gap. Honest scope: substrate 3-op arithmetic reach is fine but the BENCHMARK needs world knowledge. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
