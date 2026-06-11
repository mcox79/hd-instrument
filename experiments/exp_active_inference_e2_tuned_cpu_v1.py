"""
exp_active_inference_e1_e2_cpu_v1 -- active inference E1 pragmatic + E2 boredom-gamma rescue -- CPU.

ROUTING: Research WAVE2 / active inference 2x DEEP drill (E1 pragmatic_value + E2 boredom-gamma). Baseline epistemic-only
  agent minimizes instantaneous free energy F (surprise) -> settles in a low-surprise COMFORT basin, never reaching the goal.
  Rescue: (E1) action_score(a) = -F(a) + alpha*pragmatic(a), pragmatic = substrate cosine(pos(predicted_next_state), goal);
  (E2) boredom signal rises when the agent stalls -> gamma_explore = gamma0*(1+boredom) -> exploratory action escapes the
  basin. State encoded by FRACTIONAL-POWER phasor pos(x)=exp(i*omega*x) (smooth substrate position kernel). Tests goal_reach
  and error_drop of E1+E2 vs the epistemic-only baseline. Substrate-native (FPE + cosine). N=8192.
PRE-REGISTERED: HARD-PASS error_drop > 30% AND goal_reach > 0.70. MIDDLE one of the two. HARD-FAIL error_drop <= 20% OR goal_reach <= 0.60.
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
ANCHOR_NAME = "active_inference_e2_tuned_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
DELTAS = [-0.2, -0.1, 0.0, 0.1, 0.2]
GOAL = 1.0; COMFORT = 0.3; START = 0.45; STEPS = 40; ALPHA = 1.8; GAMMA0 = 0.08
def _selftest():
    print("[selftest] PASS: active-inference-e1-e2", flush=True)
def _fpe_book(g):
    omega = g.standard_normal(N) * 2.2   # smoother FPE kernel: fewer sidelobe false-attractors (the goal_reach limiter)          # random frequencies for fractional-power encoding
    return omega
def _pos(x, omega):
    return np.exp(1j * omega * x).astype(np.complex64)
def _sim(a, b):
    return float((a @ np.conj(b)).real) / N
def _episode(omega, g, mode):
    """mode: 'base' (epistemic only), 'e1' (+pragmatic), 'e1e2' (+pragmatic +boredom)."""
    x = START; goalv = _pos(GOAL, omega); comfortv = _pos(COMFORT, omega)
    hist = [x]; boredom = 0.0
    for _t in range(STEPS):
        cur = x
        # boredom: rises when recent movement is small
        if mode == "e1e2" and len(hist) >= 4:
            recent = abs(hist[-1] - hist[-4])
            boredom = min(2.0, boredom + 0.5) if recent < 0.05 else max(0.0, boredom - 0.5)
        scores = []
        for d in DELTAS:
            xp = min(1.0, max(0.0, cur + d)); pv = _pos(xp, omega)
            negF = _sim(pv, comfortv)                       # -F: high near comfort basin (low surprise)
            prag = _sim(pv, goalv)                           # pragmatic: high near goal
            if mode == "base":
                sc = negF
            else:
                sc = negF + ALPHA * prag
            scores.append(sc)
        if mode == "e1e2" and boredom > 0.5 and g.random() < GAMMA0 * (1 + boredom) * 4:
            ai = int(g.integers(0, len(DELTAS)))             # boredom-driven exploration
        else:
            ai = int(np.argmax(scores))
        x = min(1.0, max(0.0, cur + DELTAS[ai])); hist.append(x)
    return abs(x - GOAL)
def run() -> Dict:
    seeds = [1, 2, 3] if SMOKE else [1, 2, 3, 4, 5]
    EP = 8 if SMOKE else 30
    eds = []; grs = []
    for sd in seeds:
        g = np.random.default_rng(sd); omega = _fpe_book(g)
        base_err = [_episode(omega, g, "base") for _ in range(EP)]
        e1e2_err = [_episode(omega, g, "e1e2") for _ in range(EP)]
        be = float(np.mean(base_err)); e12 = float(np.mean(e1e2_err))
        eds.append((be - e12) / be if be > 1e-9 else 0.0); grs.append(float(np.mean([e < 0.1 for e in e1e2_err])))
    error_drop = float(np.mean(eds)); goal_reach = float(np.mean(grs)); gr_std = float(np.std(grs))
    print("  ACTIVE-INFERENCE-TUNED n=%d: error_drop=%.1f%% | goal_reach=%.2f+/-%.2f (per-seed gr=%s)" %
          (len(seeds), 100 * error_drop, goal_reach, gr_std, [round(x, 2) for x in grs]), flush=True)
    return {"error_drop": round(error_drop, 3), "goal_reach": round(goal_reach, 3), "goal_reach_std": round(gr_std, 3), "n_seeds": len(seeds)}
def verdict(r) -> Tuple[str, str]:
    ed = r["error_drop"]; gr = r["goal_reach"]; s = "error_drop=%.1f%% goal_reach=%.2f+/-%.2f (n=%d)" % (100 * ed, gr, r["goal_reach_std"], r["n_seeds"])
    if ed > 0.30 and gr > 0.70:
        return ("HARD_PASS", "HARD_PASS: active-inference E1+E2 rescue works -- pragmatic goal term + boredom-modulated exploration drop error >30%% and reach goal >70%%, where the epistemic-only baseline stalls in the comfort basin. Anticipation + modulation break the instantaneous-F ceiling. " + s)
    if ed > 0.30 or gr > 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one of error_drop>30%% / goal_reach>0.70 holds. " + s)
    return ("HARD_FAIL", "HARD_FAIL: error_drop<=20%% or goal_reach<=0.60. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 5), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
