"""
exp_strips_planning_khop_cpu_v1.py -- forward-chaining plan reachability via sharded action transitions (2-hop) -- CPU.

ROUTING: fast-cheap batch (CAP-1 STRIPS forward-chaining planning). STRIPS-style planning: states + actions (action transforms state s -> s'). Per-state shard of applicable action->next-state bindings. Forward-chaining 2-hop reachability recovers which states are reachable by a 2-action plan. Tests substrate as a planning/forward-chaining engine. Pure numpy FHRR (sub-minute; all-or-nothing OK). CPU.
PRE-REGISTERED: HARD-PASS 2-hop plan reachability recall >= 0.85. MIDDLE >= 0.70. HARD-FAIL < 0.70.
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
ANCHOR_NAME = "strips_planning_khop_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; r = cphasor(1, 64, g)[0]; o = cphasor(1, 64, g)[0]; assert np.allclose(a*r*o*np.conj(a*r), o, atol=1e-3), "bind"; print("[selftest] PASS: strips-planning-khop", flush=True)
def run() -> Dict:
    g = np.random.default_rng(802); N = 8192; VS = 150; VA = 5; TR = 40 if SMOKE else 120
    states = cphasor(VS, N, g); acts = cphasor(VA, N, g); rec_sum = 0.0; n = 0
    for _ in range(TR):
        trans = {}; shard = {i: np.zeros(N, dtype=np.complex64) for i in range(VS)}
        for s in range(VS):
            for a in range(VA):
                ns = int(g.integers(0, VS)); trans[(s, a)] = ns; shard[s] = shard[s] + acts[a] * states[ns]
        start = int(g.integers(0, VS))
        gold = set()
        for a in range(VA):
            mid = trans[(start, a)]
            for a2 in range(VA):
                gold.add(trans[(mid, a2)])
        reached = set()
        for a in range(VA):
            mid = cidx(shard[start] * np.conj(acts[a]), states)
            for a2 in range(VA):
                reached.add(cidx(shard[mid] * np.conj(acts[a2]), states))
        rec_sum += len(gold & reached) / max(1, len(gold)); n += 1
    rc = rec_sum / n; print("  STRIPS 2-hop plan reachability recall=%.3f (n=%d)" % (rc, n), flush=True)
    return {"recall": rc}
def verdict(r) -> Tuple[str, str]:
    s = "2-hop plan recall=%.3f" % r["recall"]
    if r["recall"] >= 0.85: return ("HARD_PASS", "HARD_PASS: STRIPS forward-chaining 2-hop plan reachability >=0.85 -- substrate as planning engine. " + s)
    if r["recall"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: plan recall 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: plan recall <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
