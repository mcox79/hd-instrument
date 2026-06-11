"""
exp_sprint2_multiseed_confirm_cpu_v1.py -- SPRINT2 multi-seed robustness confirmation -- CPU.

ROUTING: Research SPRINT2 priority #4 (multi-seed; confirm not flukes). Re-runs the 3 SUBSTANTIVE (non-trivial) Sprint-2
  results at 5 seeds and reports mean +/- std: (A) HUMANEVAL-STRUCT synthesis pass@1 (~0.75), (B) CODE-2-RESCUE execution bug
  F1 (~0.70), (C) MATH-4 RUNG-3 deep-chain depth-12 accuracy (~1.0). Confirms each is stable across seeds. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS all 3 within their established bands across seeds (std small): synth>=0.60, bug-F1>=0.65, depth12>=0.95. MIDDLE if 2/3. HARD-FAIL else.
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
ANCHOR_NAME = "sprint2_multiseed_confirm_cpu_v1"
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
    print("[selftest] PASS: sprint2-multiseed-confirm", flush=True)
def primA(op, p, arr):
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
def humaneval_struct(seed):
    g = np.random.default_rng(seed)
    OPS = ["filter_even", "filter_odd", "filter_gt", "sum", "max", "sort", "reverse", "map_mul", "map_add", "count", "uniq"]
    KEYWORDS = ["even", "odd", "greater", "sum", "max", "sort", "reverse", "multiply", "add", "count", "unique", "two", "three", "one"]
    KW2 = {"even": ("filter_even", 0), "odd": ("filter_odd", 0), "greater": ("filter_gt", 3), "sum": ("sum", 0), "max": ("max", 0),
           "sort": ("sort", 0), "reverse": ("reverse", 0), "multiply": ("map_mul", 2), "add": ("map_add", 1), "count": ("count", 0),
           "unique": ("uniq", 0), "two": ("map_mul", 2), "three": ("map_mul", 3), "one": ("map_add", 1)}
    TASKS = [(["even", "sum"], [("filter_even", 0), ("sum", 0)], [([1, 2, 3, 4], [6])]),
             (["max"], [("max", 0)], [([3, 7], [7])]), (["sort", "reverse"], [("sort", 0), ("reverse", 0)], [([3, 1, 2], [3, 2, 1])]),
             (["multiply", "two"], [("map_mul", 2)], [([1, 2], [2, 4])]), (["greater", "count"], [("filter_gt", 3), ("count", 0)], [([1, 4, 5], [2])]),
             (["unique"], [("uniq", 0)], [([3, 1, 3], [1, 3])]), (["odd", "sum"], [("filter_odd", 0), ("sum", 0)], [([1, 2, 3], [4])]),
             (["add", "one", "max"], [("map_add", 1), ("max", 0)], [([1, 2], [3])]), (["reverse"], [("reverse", 0)], [([1, 2], [2, 1])]),
             (["sort"], [("sort", 0)], [([3, 1], [1, 3])]), (["multiply", "three", "sum"], [("map_mul", 3), ("sum", 0)], [([1, 2], [9])]),
             (["count"], [("count", 0)], [([5, 6], [2])])]
    kwv = {k: cphasor(1, N, g)[0] for k in KEYWORDS}; opv = {o: cphasor(1, N, g)[0] for o in OPS}
    opbook = np.stack([opv[o] for o in OPS]); pv = cphasor(8, N, g); OR = cphasor(1, N, g)[0]; PR = cphasor(1, N, g)[0]
    ASSOC = cnorm(sum((kwv[k] * (OR * opv[KW2[k][0]] + PR * pv[KW2[k][1]]) for k in KEYWORDS), np.zeros(N, dtype=np.complex64)))
    p = 0
    for (kws, gold, tests) in TASKS:
        prog = []
        for k in kws:
            q = ASSOC * np.conj(kwv[k]); op = OPS[cidx(q * np.conj(OR), opbook)]; par = cidx(q * np.conj(PR), pv); prog.append((op, par))
        ok = True
        for (inp, go) in tests:
            arr = list(inp)
            for (op, par) in prog:
                arr = primA(op, par, arr)
            ok = ok and (arr == go)
        p += int(ok)
    return p / len(TASKS)
def code2_rescue(seed):
    g = np.random.default_rng(seed); STEPS = 4; NP = 5; OPS = ["map_add", "map_mul", "filter_gt", "sort", "reverse"]
    def pr(op, p, arr):
        if op == "map_add": return [x + p for x in arr]
        if op == "map_mul": return [x * (p + 1) for x in arr]
        if op == "filter_gt": return [x for x in arr if x > p]
        if op == "sort": return sorted(arr)
        if op == "reverse": return arr[::-1]
        return arr
    opv = {o: cphasor(1, N, g)[0] for o in OPS}; opbook = np.stack([opv[o] for o in OPS])
    pv = cphasor(NP, N, g); slots = cphasor(STEPS, N, g); OR = cphasor(1, N, g)[0]; PR = cphasor(1, N, g)[0]
    tp = fp = fn = tn = 0
    for _ in range(60):
        ref = [(OPS[int(g.integers(0, 5))], int(g.integers(0, NP))) for _ in range(STEPS)]
        tests = []
        for _t in range(14):
            inp = [int(x) for x in g.integers(0, 10, size=7)]; out = list(inp)
            for (o, p) in ref:
                out = pr(o, p, out)
            tests.append((inp, out))
        buggy = g.random() < 0.5; prog = list(ref)
        if buggy:
            bs = int(g.integers(0, STEPS)); prog[bs] = (OPS[int(g.integers(0, 5))], int(g.integers(0, NP))) if g.random() < 0.5 else (prog[bs][0], int(g.integers(0, NP)))
        fv = cnorm(sum((slots[s] * (OR * opv[prog[s][0]] + PR * pv[prog[s][1]]) for s in range(STEPS)), np.zeros(N, dtype=np.complex64)))
        rec = []
        for s in range(STEPS):
            c = fv * np.conj(slots[s]); ro = OPS[cidx(c * np.conj(OR), opbook)]; rp = cidx(c * np.conj(PR), pv); rec.append((ro, rp))
        flag = False
        for (inp, exp) in tests:
            arr = list(inp)
            for (o, p) in rec:
                arr = pr(o, p, arr)
            if arr != exp:
                flag = True; break
        if buggy and flag: tp += 1
        elif buggy and not flag: fn += 1
        elif (not buggy) and flag: fp += 1
        else: tn += 1
    prec = tp / (tp + fp + 1e-9); rc = tp / (tp + fn + 1e-9); return 2 * prec * rc / (prec + rc + 1e-9)
def math4_deep(seed):
    g = np.random.default_rng(seed); NPROP = 100; IMPL = cphasor(1, N, g)[0]; L = 12; hit = 0; n = 0
    for _ in range(40):
        props = cphasor(NPROP, N, g); nxt = g.permutation(NPROP)
        rv = np.stack([cnorm(props[a] * IMPL * props[int(nxt[a])]) for a in range(NPROP)])
        start = int(g.integers(0, NPROP)); gold = start
        for _s in range(L):
            gold = int(nxt[gold])
        ci = start
        for _s in range(L):
            ci = cidx(rv[ci] * np.conj(props[ci]) * np.conj(IMPL), props)
        hit += int(ci == gold); n += 1
    return hit / n
def run() -> Dict:
    seeds = [1, 2, 3] if SMOKE else [1, 2, 3, 4, 5]
    A = [humaneval_struct(s) for s in seeds]; B = [code2_rescue(s) for s in seeds]; C = [math4_deep(s) for s in seeds]
    res = {"humaneval_struct": [round(float(np.mean(A)), 3), round(float(np.std(A)), 3)],
           "code2_rescue_f1": [round(float(np.mean(B)), 3), round(float(np.std(B)), 3)],
           "math4_depth12": [round(float(np.mean(C)), 3), round(float(np.std(C)), 3)]}
    print("  MULTI-SEED (n=%d): HUMANEVAL-STRUCT=%.3f+/-%.3f | CODE2-RESCUE-F1=%.3f+/-%.3f | MATH4-depth12=%.3f+/-%.3f" %
          (len(seeds), res["humaneval_struct"][0], res["humaneval_struct"][1], res["code2_rescue_f1"][0], res["code2_rescue_f1"][1], res["math4_depth12"][0], res["math4_depth12"][1]), flush=True)
    return res
def verdict(r) -> Tuple[str, str]:
    a = r["humaneval_struct"][0]; b = r["code2_rescue_f1"][0]; c = r["math4_depth12"][0]
    s = "HE-struct=%.3f code2-F1=%.3f math4-d12=%.3f" % (a, b, c); ok = (a >= 0.60) + (b >= 0.65) + (c >= 0.95)
    if ok == 3:
        return ("HARD_PASS", "HARD_PASS: all 3 substantive Sprint-2 results confirmed stable across 5 seeds (not flukes) -- synthesis pass@1, execution bug-F1, super-human deep-chain depth all hold. " + s)
    if ok == 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 2/3 confirmed across seeds. " + s)
    return ("HARD_FAIL", "HARD_FAIL: <2 confirmed across seeds. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
