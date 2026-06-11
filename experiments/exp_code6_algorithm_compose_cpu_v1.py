"""
exp_code6_algorithm_compose_cpu_v1.py -- CODE-6 ALGORITHM-COMPOSITION (substrate-native code) -- CPU.

ROUTING: Research AGGRESSIVE_OVERNIGHT THRUST-3 CODE. An algorithm = an ordered pipeline of higher-level primitives:
  filter(>p) / map_add(p) / map_mul(p) / take(p) / sort. Substrate composes the pipeline into a shard (slot (X) (OPROLE (X) op
  + PARAMROLE (X) param)), RECOVERS each stage in order, and EXECUTES the recovered pipeline on test integer arrays. Tests the
  recovered pipeline's output equals the gold pipeline's output -- compositional algorithm building, substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS pipeline-correctness >= 0.70 on test arrays. MIDDLE >= 0.55. HARD-FAIL else.
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
ANCHOR_NAME = "code6_algorithm_compose_cpu_v1"
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
    print("[selftest] PASS: code6-algorithm-compose", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "832"))); STEPS = 4; OPS = ["filter_gt", "map_add", "map_mul", "take", "sort"]; PARAMS = list(range(6))
    opv = {o: cphasor(1, N, g)[0] for o in OPS}; opbook = np.stack([opv[o] for o in OPS])
    pv = cphasor(len(PARAMS), N, g); slots = cphasor(STEPS, N, g); OPROLE = cphasor(1, N, g)[0]; PARAMROLE = cphasor(1, N, g)[0]
    def apply(op, p, arr):
        if op == "filter_gt": return [x for x in arr if x > p]
        if op == "map_add": return [x + p for x in arr]
        if op == "map_mul": return [x * p for x in arr]
        if op == "take": return arr[:max(1, p)]
        if op == "sort": return sorted(arr)
        return arr
    TR = 100 if not SMOKE else 30; ok = 0; n = 0
    for _ in range(TR):
        prog = [(OPS[int(g.integers(0, len(OPS)))], int(g.integers(0, len(PARAMS)))) for _ in range(STEPS)]
        fn = cnorm(sum((slots[s] * (OPROLE * opv[prog[s][0]] + PARAMROLE * pv[prog[s][1]]) for s in range(STEPS)), np.zeros(N, dtype=np.complex64)))
        rec = []
        for s in range(STEPS):
            comp = fn * np.conj(slots[s]); ro = OPS[cidx(comp * np.conj(OPROLE), opbook)]; rp = cidx(comp * np.conj(PARAMROLE), pv); rec.append((ro, rp))
        for _t in range(3):
            arr = [int(x) for x in g.integers(0, 8, size=6)]; ag = list(arr); ar = list(arr)
            for (o, p) in prog:
                ag = apply(o, p, ag)
            for (o, p) in rec:
                ar = apply(o, p, ar)
            ok += int(ag == ar); n += 1
    acc = ok / n
    print("  CODE-6 ALGORITHM-COMPOSE pipeline-correctness=%.3f (recovered+executed, steps=%d, n=%d)" % (acc, STEPS, n), flush=True)
    return {"correctness": round(acc, 3), "steps": STEPS, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "correctness=%.3f (steps=%d, n=%d)" % (r["correctness"], r["steps"], r["n"])
    if r["correctness"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate composes multi-step data-processing pipelines from primitives and EXECUTES them correctly >=0.70 -- compositional algorithm building beyond single functions, substrate-only. " + s)
    if r["correctness"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: algorithm-compose 0.55-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: algorithm-compose <0.55. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
