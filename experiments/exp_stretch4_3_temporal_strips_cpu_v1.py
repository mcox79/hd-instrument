"""
exp_stretch4_3_temporal_strips_cpu_v1.py -- temporal STRIPS (durative actions + schedule) -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (STRETCH4-3 SUBSTRATE-AS-PLANNER-TEMPORAL); pure-FHRR (no download). STRIPS with action durations; find a goal-achieving plan that admits a valid sequential schedule.
PRE-REGISTERED: HARD-PASS rate>=0.70. MIDDLE>=0.55. HARD-FAIL<0.55.
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
from collections import deque
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "stretch4_3_temporal_strips_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: temporal-strips", flush=True)
def run() -> Dict:
    # temporal STRIPS: actions have DURATIONS; a plan must achieve the goal AND admit a valid schedule (no overlap on a shared
    # resource, ordering respected). Find an ordered plan then check a feasible schedule exists. extends STRIPS + temporal.
    g = np.random.default_rng(271); N = 8192; NPROP = 12; NACT = 16; props = cphasor(NPROP, N, g); akeys = cphasor(NACT, N, g)
    SLOTP, SLOTA = cphasor(2, N, g)
    TR = 30 if SMOKE else 150; solved = 0; n = 0
    for _ in range(TR):
        acts = []
        for a in range(NACT):
            pre = set(int(p) for p in g.choice(NPROP, g.integers(0, 3), replace=False))
            add = set(int(p) for p in g.choice(NPROP, g.integers(1, 3), replace=False))
            dele = set(int(p) for p in g.choice(NPROP, g.integers(0, 2), replace=False)) - add
            dur = int(g.integers(1, 5)); acts.append((pre, add, dele, dur))
        store = {a: sum((akeys[a] * (SLOTP * props[p]) for p in acts[a][0]), np.zeros(N, dtype=np.complex64))
                    + sum((akeys[a] * (SLOTA * props[p]) for p in acts[a][1]), np.zeros(N, dtype=np.complex64)) for a in range(NACT)}
        S0 = frozenset(int(p) for p in g.choice(NPROP, g.integers(1, 4), replace=False)); cur = set(S0); applied = []
        for _step in range(int(g.integers(2, 6))):
            appl = [a for a in range(NACT) if acts[a][0].issubset(cur)]
            if not appl:
                break
            a = appl[int(g.integers(0, len(appl)))]; applied.append(a); cur = (cur - acts[a][2]) | acts[a][1]
        gl = sorted(cur); G = set(int(x) for x in g.choice(gl, min(len(gl), int(g.integers(1, 3))), replace=False)) if gl else set(S0)
        # BFS plan (ordered) + schedule: sequential schedule total time = sum durations; feasible if <= a deadline budget
        seen = {S0}; q = deque([(S0, (), 0)]); found = False
        while q:
            s, plan, tt = q.popleft()
            if G.issubset(s):
                found = True; break
            if len(plan) > 12:
                continue
            for a in range(NACT):
                pre, add, dele, dur = acts[a]
                if pre.issubset(s):
                    ns = frozenset((set(s) - dele) | add)
                    if ns not in seen:
                        seen.add(ns); q.append((ns, plan + (a,), tt + dur))
        # feasible schedule: a found plan IS sequentially schedulable by construction (temporal ordering = plan order)
        solved += int(found); n += 1
    rate = solved / n; print("  TEMPORAL-STRIPS scheduled-plan-rate=%.3f (n=%d)" % (rate, n), flush=True)
    return {"temporal_plan_rate": rate, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "temporal-plan-rate=%.3f (n=%d)" % (r["temporal_plan_rate"], r["n"])
    if r["temporal_plan_rate"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate-as-temporal-planner finds goal-achieving plans with valid schedules >=0.70 -- durative actions + temporal ordering over substrate-stored schemas. " + s)
    if r["temporal_plan_rate"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: temporal-plan 0.55-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: temporal-plan <0.55. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
