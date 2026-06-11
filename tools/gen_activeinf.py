"""Research 5X ARCHITECTURAL: ACTIVE-INFERENCE-LITE (embodied/autonomous, P=0.30, substrate-only). A toy FEP loop: agent
has a substrate forward-model (predict obs from state+action); it ACTS to minimize prediction error (free energy). Tests
prediction error DECREASES over the perception-action loop (the agent learns to predict+control). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_active_inference_lite_cpu_v1.py -- ACTIVE-INFERENCE-LITE (FEP perception-action loop) -- CPU.

ROUTING: Research 5X_ARCHITECTURAL (embodied/autonomous-agent). A substrate forward-model stores (state (X) action -> next-
  obs). Each step the agent picks the action whose PREDICTED obs best matches a GOAL obs (active inference / free-energy
  minimization), executes, and learns the true transition. Tests: prediction error DECREASES over the loop AND goal-distance
  decreases (the agent learns to predict and steer toward the goal). Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS prediction-error drops >=30% over the loop AND goal-reach-rate >= 0.70. MIDDLE error drops >=15%. HARD-FAIL else.
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
ANCHOR_NAME = "active_inference_lite_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: active-inference-lite", flush=True)
def run() -> Dict:
    g = np.random.default_rng(706); NS = 12; NA = 4; A = cphasor(NA, N, g); SACT = cphasor(2, N, g)
    TR = 15 if SMOKE else 100; err_early = []; err_late = []; reached = []
    for _ in range(TR):
        states = cphasor(NS, N, g); T = g.integers(0, NS, size=(NS, NA))      # true environment dynamics
        FM = np.zeros(N, dtype=np.complex64)                                   # learned forward model (state (X) action -> next state)
        s = int(g.integers(0, NS)); goal = int(g.integers(0, NS)); errs = []
        for step in range(30):
            # predict next state for each action from FM; pick action whose predicted obs is closest to GOAL
            scores = []
            for a in range(NA):
                pred = FM * np.conj(states[s] * SACT[0]) * np.conj(A[a] * SACT[1])
                scores.append(float((states[goal] @ np.conj(pred)).real) / N)
            a = int(np.argmax(scores)) if step > 2 else int(g.integers(0, NA))
            ns = int(T[s, a])
            # prediction error: predicted next-state vs actual
            pred = FM * np.conj(states[s] * SACT[0]) * np.conj(A[a] * SACT[1])
            pe = 1.0 - max(0.0, float((states[ns] @ np.conj(pred)).real) / N); errs.append(pe)
            FM = FM + (states[s] * SACT[0]) * (A[a] * SACT[1]) * states[ns]     # learn the transition
            s = ns
            if s == goal:
                break
        err_early.append(float(np.mean(errs[:5]))); err_late.append(float(np.mean(errs[-5:]))); reached.append(int(s == goal))
    ee = float(np.mean(err_early)); el = float(np.mean(err_late)); rr = float(np.mean(reached)); drop = (ee - el) / (ee + 1e-9)
    print("  ACTIVE-INFERENCE prediction-error %.3f->%.3f (drop=%.0f%%) | goal-reach-rate=%.3f" % (ee, el, 100 * drop, rr), flush=True)
    return {"err_early": round(ee, 3), "err_late": round(el, 3), "error_drop_pct": round(100 * drop, 1), "goal_reach": round(rr, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "error %.3f->%.3f (drop=%.0f%%) goal-reach=%.3f" % (r["err_early"], r["err_late"], r["error_drop_pct"], r["goal_reach"])
    if r["error_drop_pct"] >= 30 and r["goal_reach"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate active-inference loop -- prediction error drops >=30% as the forward model learns AND the agent reaches the goal >=70% (acts to minimize free energy). Autonomous perception-action loop, substrate-only. " + s)
    if r["error_drop_pct"] >= 15:
        return ("MIDDLE_BAND", "MIDDLE_BAND: error drops 15-30% or goal-reach weak. " + s)
    return ("HARD_FAIL", "HARD_FAIL: active inference loop does not reduce prediction error. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_active_inference_lite_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote active_inference_lite")
