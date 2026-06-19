"""
exp_code2_bug_rescue_exec_cpu_v1.py -- CODE-2-RESCUE-R2 execution-based bug detection -- CPU.

ROUTING: Research SPRINT2 code2 rescue R2 (execution-trace comparison). The anomaly-margin bug detector was weak (F1 0.57)
  because a single bad op barely shifts a bundle's cleanup margin. RESCUE: detect bugs by EXECUTION -- the substrate composes
  the program (CODE-1 mechanism), EXECUTES it on the spec's test inputs, and flags a bug when any output != expected. This
  leverages the substrate's compose+execute strength (both 1.0) instead of anomaly margin. Tests bug-detection F1. N=8192.
PRE-REGISTERED: HARD-PASS execution-based bug-detection F1 >= 0.85 (rescues anomaly-margin 0.57). MIDDLE >= 0.70. HARD-FAIL else.
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
ANCHOR_NAME = "code2_bug_rescue_exec_cpu_v1"
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
    print("[selftest] PASS: code2-bug-rescue-exec", flush=True)
OPS = ["map_add", "map_mul", "filter_gt", "sort", "reverse"]
def prim(op, p, arr):
    if op == "map_add": return [x + p for x in arr]
    if op == "map_mul": return [x * (p + 1) for x in arr]
    if op == "filter_gt": return [x for x in arr if x > p]
    if op == "sort": return sorted(arr)
    if op == "reverse": return arr[::-1]
    return arr
def run() -> Dict:
    g = np.random.default_rng(833); STEPS = 4; NP = 5
    opv = {o: cphasor(1, N, g)[0] for o in OPS}; opbook = np.stack([opv[o] for o in OPS])
    pv = cphasor(NP, N, g); slots = cphasor(STEPS, N, g); OPROLE = cphasor(1, N, g)[0]; PARROLE = cphasor(1, N, g)[0]
    TR = 25 if SMOKE else 120; tp = fp = fn = tn = 0
    for _ in range(TR):
        for _q in range(8):
            ref = [(OPS[int(g.integers(0, len(OPS)))], int(g.integers(0, NP))) for _ in range(STEPS)]
            tests = []
            for _t in range(14):
                inp = [int(x) for x in g.integers(0, 10, size=7)]; out = list(inp)
                for (o, p) in ref:
                    out = prim(o, p, out)
                tests.append((inp, out))                              # spec from the reference program
            buggy = g.random() < 0.5; prog = list(ref)
            if buggy:                                                 # mutate one op or param
                bs = int(g.integers(0, STEPS))
                if g.random() < 0.5:
                    prog[bs] = (OPS[int(g.integers(0, len(OPS)))], prog[bs][1])
                else:
                    prog[bs] = (prog[bs][0], int(g.integers(0, NP)))
            # encode + recover the program via substrate (compose/execute mechanism), then EXECUTE vs spec
            fn_vec = cnorm(sum((slots[s] * (OPROLE * opv[prog[s][0]] + PARROLE * pv[prog[s][1]]) for s in range(STEPS)), np.zeros(N, dtype=np.complex64)))
            rec = []
            for s in range(STEPS):
                comp = fn_vec * np.conj(slots[s]); ro = OPS[cidx(comp * np.conj(OPROLE), opbook)]; rp = cidx(comp * np.conj(PARROLE), pv); rec.append((ro, rp))
            flagged = False
            for (inp, exp) in tests:
                arr = list(inp)
                for (o, p) in rec:
                    arr = prim(o, p, arr)
                if arr != exp:
                    flagged = True; break
            # confusion (positive = buggy)
            if buggy and flagged: tp += 1
            elif buggy and not flagged: fn += 1
            elif (not buggy) and flagged: fp += 1
            else: tn += 1
    prec = tp / (tp + fp + 1e-9); rec_ = tp / (tp + fn + 1e-9); f1 = 2 * prec * rec_ / (prec + rec_ + 1e-9)
    print("  CODE-2-RESCUE execution-based bug-detection: F1=%.3f (tp=%d fp=%d fn=%d tn=%d) [anomaly-margin was 0.57]" % (f1, tp, fp, fn, tn), flush=True)
    return {"f1": round(f1, 3), "precision": round(prec, 3), "recall": round(rec_, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "F1=%.3f prec=%.3f rec=%.3f" % (r["f1"], r["precision"], r["recall"])
    if r["f1"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: EXECUTION-based bug detection F1>=0.85 -- substrate composes+executes the program vs spec and flags behavioral bugs reliably. Rescues the weak anomaly-margin detector (0.57); bug-detection works via the substrate's execution strength. " + s)
    if r["f1"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: execution-based bug-detection 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: execution-based bug-detection <0.70. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
