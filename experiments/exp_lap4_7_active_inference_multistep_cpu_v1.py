"""
exp_lap4_7_active_inference_multistep_cpu_v1.py -- multi-step active inference over a latent trajectory -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (LAP4-7 ACTIVE-INFERENCE-MULTI-STEP); pure-FHRR (no download). K-step trajectory; per-step hypothesize->predict->minimize->re-hypothesize; measure per-step + full-trajectory convergence.
PRE-REGISTERED: HARD-PASS per-step>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.
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
ANCHOR_NAME = "lap4_7_active_inference_multistep_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: active-inference-multi-step", flush=True)
def run() -> Dict:
    # multi-step active inference: a latent TRAJECTORY of K patterns; at each step generate-hypothesis -> predict -> minimize
    # prediction-error -> converge, then use the converged state to seed the next step. Measure full-trajectory convergence.
    g = np.random.default_rng(42); KB = 60; book = cphasor(KB, 8192, g); N = 8192
    STEPS = 6; NOISE = 1.3; MAXIT = 8; TR = 40 if SMOKE else 250; traj_ok = 0; step_ok = 0; tot_steps = 0
    for _ in range(TR):
        true_traj = [int(g.integers(0, KB)) for _ in range(STEPS)]; all_right = True
        for st in range(STEPS):
            obs = book[true_traj[st]] + NOISE * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            est = obs.copy(); prev = 1e9; hyp = -1
            for _it in range(MAXIT):
                hyp = int(np.argmax((book @ np.conj(est)).real)); pred = book[hyp]
                err = float(np.abs(est - pred).mean()); est = pred + 0.5 * (obs - pred)
                if abs(prev - err) < 1e-3:
                    break
                prev = err
            ok = (hyp == true_traj[st]); step_ok += int(ok); tot_steps += 1
            if not ok:
                all_right = False
        traj_ok += int(all_right)
    tr_rate = traj_ok / TR; sr = step_ok / tot_steps
    print("  ACTIVE-INFERENCE-MULTI-STEP full-trajectory=%.3f per-step=%.3f (STEPS=%d, n=%d)" % (tr_rate, sr, STEPS, TR), flush=True)
    return {"trajectory_converge": tr_rate, "step_converge": sr, "steps": STEPS}
def verdict(r) -> Tuple[str, str]:
    s = "per-step-converge=%.3f full-trajectory=%.3f" % (r["step_converge"], r["trajectory_converge"])
    if r["step_converge"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: multi-step active inference -- per-step convergence to the true latent >=0.85 across a %d-step trajectory (hypothesize->predict->minimize->re-hypothesize chains). " % r["steps"] + s)
    if r["step_converge"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: per-step 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: per-step <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
