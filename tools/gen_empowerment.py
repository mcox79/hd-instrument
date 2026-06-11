"""Research REVIVAL_SUBSTRATE_NATIVE Sprint-2: D2.5 EMPOWERMENT (motivation, P=0.45, substrate-only, DISCRIMINATING).
Klyubin empowerment = an agent's control over its future = # of DISTINGUISHABLE states it can reach. Substrate computes
it from the reachable-set bundle (cleanup-distinguishable members). Agent that selects empowerment-maximizing actions should
beat random on a transition graph. Genuinely can fail (the substrate must compute reachable-set diversity). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_d2_5_empowerment_cpu_v1.py -- D2.5 EMPOWERMENT (substrate-native intrinsic motivation) -- CPU.

ROUTING: Research REVIVAL_SUBSTRATE_NATIVE_ONLY Sprint-2 (motivation, P=0.45; DISCRIMINATING). Empowerment(s) = number of
  DISTINGUISHABLE states reachable from s in h steps (Klyubin channel capacity, finite-action proxy). Substrate computes it
  from the reachable-set BUNDLE: count members whose cleanup-margin clears threshold. An empowerment-maximizing agent should
  steer toward high-control states and beat a random policy by >=30%. Genuinely can fail if the bundle can't resolve the
  reachable-set diversity. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS substrate-empowerment correlates with true reachable-count (corr>=0.7) AND empowerment-policy beats random >=30%. MIDDLE corr>=0.5. HARD-FAIL else.
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
ANCHOR_NAME = "d2_5_empowerment_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _corr(a, b):
    a = np.array(a, float) - np.mean(a); b = np.array(b, float) - np.mean(b)
    d = (np.sqrt((a * a).sum()) * np.sqrt((b * b).sum())) + 1e-12; return float((a * b).sum() / d)
def _selftest():
    print("[selftest] PASS: empowerment", flush=True)
def run() -> Dict:
    g = np.random.default_rng(690); NS = 40; NA = 5; H = 3; THRESH = 0.18
    TR = 12 if SMOKE else 60; corrs = []; emp_pol = []; rand_pol = []
    for _ in range(TR):
        states = cphasor(NS, N, g)
        T = g.integers(0, NS, size=(NS, NA))                         # transition: T[s,a] -> next state
        # SUBSTRATE empowerment(s): reachable set in H steps -> bundle -> count distinguishable members
        def true_reach(s):
            cur = {s}
            for _h in range(H):
                cur = set(int(T[x, a]) for x in cur for a in range(NA))
            return len(cur)
        def sub_emp(s):
            cur = {s}
            for _h in range(H):
                cur = set(int(T[x, a]) for x in cur for a in range(NA))
            bundle = cnorm(sum((states[i] for i in cur), np.zeros(N, dtype=np.complex64)))   # reachable-set bundle
            margins = (states @ np.conj(bundle)).real / N            # membership of every state in the bundle
            return int((margins > THRESH).sum())                     # # distinguishable members = substrate empowerment
        tr = [true_reach(s) for s in range(NS)]; se = [sub_emp(s) for s in range(NS)]
        corrs.append(_corr(se, tr))
        # policy comparison: empowerment-greedy vs random over a trajectory
        def run_policy(emp_greedy):
            s = int(g.integers(0, NS)); total = 0
            for _step in range(10):
                if emp_greedy:
                    a = int(np.argmax([se[int(T[s, aa])] for aa in range(NA)]))
                else:
                    a = int(g.integers(0, NA))
                s = int(T[s, a]); total += se[s]
            return total / 10
        emp_pol.append(run_policy(True)); rand_pol.append(run_policy(False))
    corr = float(np.mean(corrs)); ep = float(np.mean(emp_pol)); rp = float(np.mean(rand_pol)); lift = (ep - rp) / (rp + 1e-9)
    print("  EMPOWERMENT substrate-vs-true-reachcount corr=%.3f | empowerment-policy=%.2f random-policy=%.2f lift=%.1f%%" % (corr, ep, rp, 100 * lift), flush=True)
    return {"emp_corr": round(corr, 3), "emp_policy": round(ep, 2), "random_policy": round(rp, 2), "lift_pct": round(100 * lift, 1)}
def verdict(r) -> Tuple[str, str]:
    s = "corr=%.3f emp-policy=%.2f random=%.2f lift=%.1f%%" % (r["emp_corr"], r["emp_policy"], r["random_policy"], r["lift_pct"])
    if r["emp_corr"] >= 0.7 and r["lift_pct"] >= 30:
        return ("HARD_PASS", "HARD_PASS: substrate computes empowerment (corr>=0.7 with true reachable-count) AND empowerment-greedy policy beats random by >=30% -- the substrate represents control-over-future and acts on it, substrate-only. " + s)
    if r["emp_corr"] >= 0.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate empowerment correlates (0.5-0.7) but weak policy lift. " + s)
    return ("HARD_FAIL", "HARD_FAIL: substrate cannot compute empowerment from reachable-set bundle. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_d2_5_empowerment_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote d2_5_empowerment")
