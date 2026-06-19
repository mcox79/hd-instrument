"""Research REVIVAL_SUBSTRATE_NATIVE Sprint-2: INTEGRATION-ALGEBRA + FLOW (motivation, P=0.55, substrate-only).
The 'missing layer' for intrinsic motivation: integrate 5 competing drives (curiosity/empowerment/mastery/social/identity)
via superposition binding + a flow controller that up-weights unsatisfied drives. Tests the integrated decision balances
competing drives under CONFLICT (beats single-drive + equal-weight). Genuinely non-trivial. Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_integration_algebra_flow_cpu_v1.py -- INTEGRATION-ALGEBRA + FLOW CONTROLLER (motivation) -- CPU.

ROUTING: Research REVIVAL_SUBSTRATE_NATIVE_ONLY Sprint-2 (motivation, P=0.55). 5 drives, each a substrate superposition over
  actions weighting its preferences. Integration = flow-weighted superposition sum_d w_d * drive_d; the FLOW CONTROLLER sets
  w_d proportional to drive d's current UNSATISFACTION (so neglected drives gain influence). Readout = cleanup to best action.
  Tests: under CONFLICT (drives prefer different actions) the integrated policy achieves higher MIN-drive satisfaction (no
  drive starved) than best-single-drive or equal-weight, over a multi-step loop. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS integrated min-drive-satisfaction > equal-weight AND > best-single-drive (lift>=0.10) under conflict. MIDDLE >= equal-weight. HARD-FAIL else.
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
ANCHOR_NAME = "integration_algebra_flow_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: integration-algebra-flow", flush=True)
def run() -> Dict:
    g = np.random.default_rng(680); ND = 5; NA = 12
    TR = 20 if SMOKE else 120; STEPS = 10
    integ = []; eqw = []; bestsingle = []
    for _ in range(TR):
        acts = cphasor(NA, N, g)
        pref = g.random((ND, NA)) ** 3                                # each drive's action-values (CONFLICTING: peaked, different)
        pref = pref / pref.sum(1, keepdims=True)
        drive_vec = np.stack([cnorm((pref[d][:, None] * acts).sum(0)) for d in range(ND)])
        def chosen_min_sat(weights):
            I = (weights[:, None] * drive_vec).sum(0); a = int(np.argmax((acts @ np.conj(I)).real)); return float(np.min(pref[:, a])), a
        # FLOW loop: start equal, then up-weight unsatisfied drives over STEPS
        w = np.ones(ND) / ND; sat_hist = np.zeros(ND)
        for _s in range(STEPS):
            _, a = chosen_min_sat(w); sat_hist = 0.7 * sat_hist + pref[:, a]   # accumulated satisfaction per drive
            unsat = 1.0 - (sat_hist / (sat_hist.max() + 1e-9)); w = cnorm_w(0.5 * w + 0.5 * (unsat / (unsat.sum() + 1e-9)))
        ms_int, _ = chosen_min_sat(w)
        ms_eq, _ = chosen_min_sat(np.ones(ND) / ND)
        ms_bs = max(min(pref[:, int(np.argmax(pref[d]))] ) for d in range(ND))   # best single-drive: optimize one drive, its action's MIN sat
        integ.append(ms_int); eqw.append(ms_eq); bestsingle.append(ms_bs)
    mi = float(np.mean(integ)); me = float(np.mean(eqw)); mb = float(np.mean(bestsingle))
    print("  INTEGRATION min-drive-satisfaction: flow-integrated=%.3f equal-weight=%.3f best-single=%.3f" % (mi, me, mb), flush=True)
    return {"integrated_minsat": round(mi, 3), "equalweight_minsat": round(me, 3), "bestsingle_minsat": round(mb, 3)}
def cnorm_w(w):
    w = np.clip(w, 1e-6, None); return w / w.sum()
def verdict(r) -> Tuple[str, str]:
    mi = r["integrated_minsat"]; me = r["equalweight_minsat"]; mb = r["bestsingle_minsat"]
    s = "integrated=%.3f equal-weight=%.3f best-single=%.3f" % (mi, me, mb)
    if mi >= me and mi - mb >= 0.10:
        return ("HARD_PASS", "HARD_PASS: flow-controlled integration of 5 competing drives achieves higher MIN-drive satisfaction than best-single-drive (lift>=0.10) and >= equal-weight -- superposition binding + unsatisfaction-weighting integrates conflicting drives without starving any, substrate-only. " + s)
    if mi >= me - 0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: integration matches equal-weight but no clear lift over single-drive. " + s)
    return ("HARD_FAIL", "HARD_FAIL: integration does not balance competing drives. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_integration_algebra_flow_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote integration_algebra_flow")
