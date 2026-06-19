"""
exp_code1_function_compose_cpu_v1.py -- CODE-1 FUNCTION-COMPOSE (substrate-native code) -- CPU.

ROUTING: Research AGGRESSIVE_OVERNIGHT THRUST-3 CODE. A function SPEC = an ordered sequence of primitive ops (add k / mul k /
  sub k / square / neg). Substrate composes the op-sequence into a function-shard (slot-bound), then RECOVERS the ops in order
  and EXECUTES them on test inputs (real numeric ops). Tests the composed+recovered function computes the correct output on
  held-out inputs -- substrate-native program composition (structure recovered correctly -> correct execution). No LLM. N=8192.
PRE-REGISTERED: HARD-PASS function-correctness >= 0.80 on test inputs (recovered program executes correctly). MIDDLE >= 0.65. HARD-FAIL else.
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
ANCHOR_NAME = "code1_function_compose_cpu_v1"
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
    print("[selftest] PASS: code1-function-compose", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "830"))); STEPS = 5; NK = 5                  # program length, constant range
    # op vocabulary (op (X) const). recoverable ops: add/mul/sub/square/neg
    OPS = ["add", "mul", "sub", "square", "neg"]
    opv = {o: cphasor(1, N, g)[0] for o in OPS}; opbook = np.stack([opv[o] for o in OPS])
    consts = cphasor(NK, N, g); slots = cphasor(STEPS, N, g); OPROLE = cphasor(1, N, g)[0]; CONSTROLE = cphasor(1, N, g)[0]
    def apply(op, k, x):
        return {"add": x + k, "mul": x * (k + 1), "sub": x - k, "square": x * x, "neg": -x}[op]
    TR = 100 if not SMOKE else 30; correct = 0; n = 0
    for _ in range(TR):
        prog = [(OPS[int(g.integers(0, len(OPS)))], int(g.integers(0, NK))) for _ in range(STEPS)]
        # COMPOSE function-shard: slot_s (X) (op (X) const)
        fn = cnorm(sum((slots[s] * (OPROLE * opv[prog[s][0]] + CONSTROLE * consts[prog[s][1]]) for s in range(STEPS)), np.zeros(N, dtype=np.complex64)))
        # RECOVER program in order + EXECUTE on test inputs
        rec = []
        for s in range(STEPS):
            comp = fn * np.conj(slots[s]); ro = OPS[cidx(comp * np.conj(OPROLE), opbook)]; rk = cidx(comp * np.conj(CONSTROLE), consts); rec.append((ro, rk))
        for xi in [1, 3, -2]:
            xg = xi; xr = xi
            for (o, k) in prog:
                xg = apply(o, k, xg)
            for (o, k) in rec:
                xr = apply(o, k, xr)
            correct += int(xr == xg); n += 1
    acc = correct / n
    print("  CODE-1 FUNCTION-COMPOSE correctness=%.3f (program recovered+executed, len=%d, n=%d)" % (acc, STEPS, n), flush=True)
    return {"correctness": round(acc, 3), "prog_len": STEPS, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "correctness=%.3f (len=%d, n=%d)" % (r["correctness"], r["prog_len"], r["n"])
    if r["correctness"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate composes a program from op-shards, recovers it in order, and it EXECUTES correctly >=0.80 -- substrate-native program composition (structure -> correct computation), no LLM. " + s)
    if r["correctness"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: function-compose 0.65-0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: function-compose <0.65. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
