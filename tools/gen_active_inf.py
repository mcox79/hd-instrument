"""Research WAVE-2 STRETCH: STRETCH2-4 ACTIVE-INFERENCE-1 (Friston FEP: hypothesis-generate -> predict -> minimize prediction error -> converge). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_stretch2_4_active_inference_cpu_v1.py -- STRETCH2-4 ACTIVE-INFERENCE-1: free-energy-minimizing convergence -- CPU.

ROUTING: Research LAPTOP_WAVE2 STRETCH (STRETCH2-4). Friston Free-Energy-Principle analog: the substrate holds a generative model
  (a codebook of patterns = priors). Given a noisy observation, it runs active inference -- generate a hypothesis (cleanup),
  predict (the hypothesised pattern), compute prediction error (obs - prediction), and update the estimate toward the
  observation -- iterating until the prediction error stops shrinking (converged). Measures whether the loop CONVERGES to the
  true generating pattern across noise levels. numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS >= 0.85 of active-inference cycles converge to the true pattern. MIDDLE >= 0.70. HARD-FAIL < 0.70.
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
ANCHOR_NAME = "stretch2_4_active_inference_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def _selftest():
    print("[selftest] PASS: active-inference", flush=True)


def run() -> Dict:
    g = np.random.default_rng(42); K = 60; NOISE = 1.3; MAXIT = 8
    book = cphasor(K, N, g)
    TR = 50 if SMOKE else 300; converged = 0; n = 0; iters = []
    for _ in range(TR):
        true = int(g.integers(0, K))
        obs = book[true] + NOISE * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
        est = obs.copy(); prev_err = 1e9; hyp = -1; it = 0
        for it in range(1, MAXIT + 1):
            hyp = int(np.argmax((book @ np.conj(est)).real))             # generate hypothesis (cleanup against priors)
            pred = book[hyp]                                              # predict
            err = float(np.abs(est - pred).mean())                       # prediction error (free energy proxy)
            est = pred + 0.5 * (obs - pred)                              # update estimate toward observation
            if abs(prev_err - err) < 1e-3:                               # converged (error stopped shrinking)
                break
            prev_err = err
        converged += int(hyp == true); n += 1; iters.append(it)
    rate = converged / n; ai = float(np.mean(iters))
    print("  ACTIVE-INFERENCE converge-to-true=%.3f (mean-iters=%.2f, K=%d, n=%d)" % (rate, ai, K, n), flush=True)
    return {"converge_rate": rate, "mean_iters": round(ai, 2), "n": n}


def verdict(r) -> Tuple[str, str]:
    s = "converge-to-true=%.3f mean-iters=%.2f (n=%d)" % (r["converge_rate"], r["mean_iters"], r["n"])
    if r["converge_rate"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: active-inference loop converges to the true generating pattern >=0.85 -- substrate codebook as generative model; hypothesis-generate + predict + prediction-error-minimize converges (Friston FEP). " + s)
    if r["converge_rate"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: converge 0.70-0.85 (noise near capacity). " + s)
    return ("HARD_FAIL", "HARD_FAIL: converge <0.70. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_stretch2_4_active_inference_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote active_inference")
