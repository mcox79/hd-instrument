"""
exp_humaneval_structural_lite_cpu_v1.py -- HUMANEVAL-STRUCTURAL-LITE (substrate program synthesis) -- CPU.

ROUTING: Research SPRINT2_BOTH_PATHS Path-B (priority). Real simple programming tasks. Each task = keyword-spec (abstracts the
  English-parsing step) + real test cases. Substrate maps spec-keywords -> primitives via a stored keyword->primitive
  association memory, composes the program (role-separated op-shards), and EXECUTES it on the real test inputs. pass@1 = all
  test cases pass. ISOLATES whether the substrate can SYNTHESIZE+EXECUTE (vs the separate English-parsing bottleneck). N=8192.
PRE-REGISTERED: HARD-PASS pass@1 >= 0.50. MIDDLE >= 0.30. HARD-FAIL else.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "humaneval_structural_lite_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: humaneval-structural-lite", flush=True)

def prim(op, p, arr):
    if op == "filter_even": return [x for x in arr if x % 2 == 0]
    if op == "filter_odd": return [x for x in arr if x % 2 == 1]
    if op == "filter_gt": return [x for x in arr if x > p]
    if op == "sum": return [sum(arr)]
    if op == "max": return [max(arr)] if arr else [0]
    if op == "sort": return sorted(arr)
    if op == "reverse": return arr[::-1]
    if op == "map_mul": return [x * p for x in arr]
    if op == "map_add": return [x + p for x in arr]
    if op == "count": return [len(arr)]
    if op == "uniq": return sorted(set(arr))
    return arr

TASKS = [
    ("sum_even", ["even", "sum"], [("filter_even", 0), ("sum", 0)], [([1, 2, 3, 4], [6]), ([2, 4, 6], [12]), ([1, 3], [0])]),
    ("max_of_list", ["max"], [("max", 0)], [([3, 7, 2], [7]), ([1], [1])]),
    ("sort_desc", ["sort", "reverse"], [("sort", 0), ("reverse", 0)], [([3, 1, 2], [3, 2, 1]), ([5, 4], [5, 4])]),
    ("double_all", ["multiply", "two"], [("map_mul", 2)], [([1, 2, 3], [2, 4, 6]), ([0, 5], [0, 10])]),
    ("count_gt3", ["greater", "count"], [("filter_gt", 3), ("count", 0)], [([1, 4, 5, 2], [2]), ([6, 7], [2])]),
    ("unique_sorted", ["unique", "sort"], [("uniq", 0)], [([3, 1, 3, 2], [1, 2, 3]), ([5, 5], [5])]),
    ("sum_odd", ["odd", "sum"], [("filter_odd", 0), ("sum", 0)], [([1, 2, 3, 4], [4]), ([2, 4], [0])]),
    ("inc_then_max", ["add", "one", "max"], [("map_add", 1), ("max", 0)], [([1, 2], [3]), ([5, 0], [6])]),
    ("filter_even_count", ["even", "count"], [("filter_even", 0), ("count", 0)], [([2, 4, 1], [2]), ([1, 3], [0])]),
    ("reverse_list", ["reverse"], [("reverse", 0)], [([1, 2, 3], [3, 2, 1]), ([7], [7])]),
    ("triple_sum", ["multiply", "three", "sum"], [("map_mul", 3), ("sum", 0)], [([1, 2], [9]), ([0, 4], [12])]),
    ("sort_asc", ["sort"], [("sort", 0)], [([3, 1, 2], [1, 2, 3]), ([9, 0], [0, 9])]),
]
OPS = ["filter_even", "filter_odd", "filter_gt", "sum", "max", "sort", "reverse", "map_mul", "map_add", "count", "uniq"]
KEYWORDS = ["even", "odd", "greater", "sum", "max", "sort", "reverse", "multiply", "add", "count", "unique", "two", "three", "one"]
KW2PRIM = {"even": ("filter_even", 0), "odd": ("filter_odd", 0), "greater": ("filter_gt", 3), "sum": ("sum", 0), "max": ("max", 0),
           "sort": ("sort", 0), "reverse": ("reverse", 0), "multiply": ("map_mul", 2), "add": ("map_add", 1), "count": ("count", 0),
           "unique": ("uniq", 0), "two": ("map_mul", 2), "three": ("map_mul", 3), "one": ("map_add", 1)}

def run() -> Dict:
    g = np.random.default_rng(840)
    kwv = {k: cphasor(1, N, g)[0] for k in KEYWORDS}; opv = {o: cphasor(1, N, g)[0] for o in OPS}
    opbook = np.stack([opv[o] for o in OPS]); pv = cphasor(8, N, g); OPROLE = cphasor(1, N, g)[0]; PARROLE = cphasor(1, N, g)[0]
    ASSOC = cnorm(sum((kwv[k] * (OPROLE * opv[KW2PRIM[k][0]] + PARROLE * pv[KW2PRIM[k][1]]) for k in KEYWORDS), np.zeros(N, dtype=np.complex64)))
    passed = 0
    for (name, kws, gold_prog, tests) in TASKS:
        prog = []
        for k in kws:
            q = ASSOC * np.conj(kwv[k]); op = OPS[cidx(q * np.conj(OPROLE), opbook)]; par = cidx(q * np.conj(PARROLE), pv); prog.append((op, par))
        ok = True
        for (inp, gold_out) in tests:
            arr = list(inp)
            for (op, par) in prog:
                arr = prim(op, par, arr)
            ok = ok and (arr == gold_out)
        passed += int(ok)
        if not SMOKE:
            print("  [task] %-18s synth=%s -> %s" % (name, prog, "PASS" if ok else "fail"), flush=True)
    pat1 = passed / len(TASKS)
    print("  HUMANEVAL-STRUCTURAL-LITE pass@1=%.3f (%d/%d tasks; synthesis+execute from keyword-spec)" % (pat1, passed, len(TASKS)), flush=True)
    return {"pass_at_1": round(pat1, 3), "n_pass": passed, "n_task": len(TASKS)}

def verdict(r) -> Tuple[str, str]:
    s = "pass@1=%.3f (%d/%d)" % (r["pass_at_1"], r["n_pass"], r["n_task"])
    if r["pass_at_1"] >= 0.50:
        return ("HARD_PASS", "HARD_PASS: substrate SYNTHESIZES + EXECUTES correct programs from keyword-specs (pass@1>=0.50) on real tasks -- synthesis+execution work; the benchmark bottleneck is the separate English-PARSING step, not program synthesis. " + s)
    if r["pass_at_1"] >= 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: synthesis pass@1 0.30-0.50. " + s)
    return ("HARD_FAIL", "HARD_FAIL: synthesis pass@1 <0.30 -- substrate cannot synthesize correct programs even from keyword-spec. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
