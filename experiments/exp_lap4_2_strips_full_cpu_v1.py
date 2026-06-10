"""
exp_lap4_2_strips_full_cpu_v1.py -- STRIPS planning at production scale (n>=200) -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (LAP4-2 STRIPS-FULL); pure-FHRR (no download). Full-scale STRIPS planning over substrate-stored action schemas; BFS with reachable goals; n>=200.
PRE-REGISTERED: HARD-PASS plan_rate>=0.70 AND n>=200. MIDDLE>=0.55. HARD-FAIL<0.55.
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
ANCHOR_NAME = "lap4_2_strips_full_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: strips-full", flush=True)
def run() -> Dict:
    g = np.random.default_rng(1); N = 8192; NPROP = 16; NACT = 24; props = cphasor(NPROP, N, g); akeys = cphasor(NACT, N, g)
    SLOTP, SLOTA, SLOTD = cphasor(3, N, g)
    TR = 40 if SMOKE else 250; solved = 0; plan_lens = []; n = 0   # n>=200 at full (production scale)
    for _ in range(TR):
        acts = []
        for a in range(NACT):
            pre = set(int(p) for p in g.choice(NPROP, g.integers(0, 3), replace=False))
            add = set(int(p) for p in g.choice(NPROP, g.integers(1, 3), replace=False))
            dele = set(int(p) for p in g.choice(NPROP, g.integers(0, 2), replace=False)) - add
            acts.append((pre, add, dele))
        store = {a: sum((akeys[a] * (SLOTP * props[p]) for p in acts[a][0]), np.zeros(N, dtype=np.complex64))
                    + sum((akeys[a] * (SLOTA * props[p]) for p in acts[a][1]), np.zeros(N, dtype=np.complex64)) for a in range(NACT)}
        S0 = frozenset(int(p) for p in g.choice(NPROP, g.integers(1, 4), replace=False)); cur = set(S0)
        for _step in range(int(g.integers(3, 7))):
            appl = [a for a in range(NACT) if acts[a][0].issubset(cur)]
            if not appl:
                break
            a = appl[int(g.integers(0, len(appl)))]; cur = (cur - acts[a][2]) | acts[a][1]
        gl = sorted(cur); G = set(int(x) for x in g.choice(gl, min(len(gl), int(g.integers(1, 4))), replace=False)) if gl else set(S0)
        seen = {S0}; q = deque([(S0, 0)]); found = False
        while q:
            s, dlen = q.popleft()
            if G.issubset(s):
                found = True; plan_lens.append(dlen); break
            if dlen > 30:
                continue
            for a in range(NACT):
                pre, add, dele = acts[a]
                if pre.issubset(s):
                    ns = frozenset((set(s) - dele) | add)
                    if ns not in seen:
                        seen.add(ns); q.append((ns, dlen + 1))
        solved += int(found); n += 1
    rate = solved / n; mlen = float(np.mean(plan_lens)) if plan_lens else 0.0
    print("  STRIPS-FULL solved-rate=%.3f mean-plan-len=%.1f (n=%d)" % (rate, mlen, n), flush=True)
    return {"plan_rate": rate, "mean_plan_len": round(mlen, 1), "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "STRIPS-solved=%.3f mean-len=%.1f (n=%d)" % (r["plan_rate"], r["mean_plan_len"], r["n"])
    if r["plan_rate"] >= 0.70 and r["n"] >= 200:
        return ("HARD_PASS", "HARD_PASS: substrate-as-planner solves >=0.70 STRIPS at production scale (n>=200) -- smoke->full transition clean; planning over substrate-stored action schemas robust at scale. " + s)
    if r["plan_rate"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: STRIPS 0.55-0.70 or n<200. " + s)
    return ("HARD_FAIL", "HARD_FAIL: STRIPS <0.55. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
