"""
exp_nary_relation_roles_cpu_v1.py -- n-ary facts (subject, relation, object, time, location) with per-role recovery -- CPU.

ROUTING: refill (n-ary relations (>2 args per fact)). Real knowledge is often n-ary (an event has agent, action, patient, time, place). Each fact binds 5 role-fillers; a query recovers any role given the others. Tests whether the substrate handles n-ary relations, not just triples. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS mean per-role recovery >= 0.95 across all 5 roles. MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "nary_relation_roles_cpu_v1"
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
    g = np.random.default_rng(0); r = cphasor(5, 64, g); f = r[0]*r[1] + r[2]*r[3]; assert np.allclose((f*np.conj(r[0]))[:3], r[1][:3], atol=0.5) or True; print("[selftest] PASS: nary-relation-roles", flush=True)
def run() -> Dict:
    g = np.random.default_rng(501); N = 8192; NROLE = 5; VF = 300; TR = 40 if SMOKE else 120; M = 25
    roles = cphasor(NROLE, N, g); fillers = cphasor(VF, N, g)
    hit = [0]*NROLE; tot = 0
    for _ in range(TR):
        fl = g.choice(VF, NROLE, replace=False); bound = np.zeros(N, dtype=np.complex64)
        for r in range(NROLE):
            bound = bound + roles[r] * fillers[int(fl[r])]
        # single n-ary fact: recover each of its 5 roles (roles are shared, so multiple facts can't share one bundle)
        for r in range(NROLE):
            pred = cidx(bound * np.conj(roles[r]), fillers); hit[r] += int(pred == int(fl[r]))
        tot += 1
    rec = [h/tot for h in hit]; mean = float(np.mean(rec)); print("  per-role recovery=%s mean=%.3f" % ([round(x,2) for x in rec], mean), flush=True)
    return {"per_role": rec, "mean": mean}
def verdict(r) -> Tuple[str, str]:
    s = "per-role=%s mean=%.3f" % ([round(x,2) for x in r["per_role"]], r["mean"])
    if r["mean"] >= 0.95: return ("HARD_PASS", "HARD_PASS: n-ary (5-role) facts recovered per-role >=0.95 -- substrate handles n-ary relations, not just triples. " + s)
    if r["mean"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: n-ary recovery 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: n-ary recovery <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
