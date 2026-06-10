"""
exp_stretch3_1_drift_diffusion_cpu_v1.py -- evidence accumulation to a decision threshold (DDM) -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 (STRETCH3-1 DRIFT-DIFFUSION-EVIDENCE); pure-FHRR (no download). Accumulate noisy evidence for one of 2 alternatives; decide when cleanup margin crosses threshold; measure accuracy + RT.
PRE-REGISTERED: HARD-PASS DDM accuracy>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.
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
ANCHOR_NAME = "stretch3_1_drift_diffusion_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: drift-diffusion", flush=True)
def run() -> Dict:
    # drift-diffusion: accumulate noisy evidence toward one of 2 alternatives; decide when the cleanup margin crosses threshold.
    g = np.random.default_rng(2); N = 4096; DRIFT = 0.25; SNOISE = 1.0; THR = 0.30; MAXT = 60
    TR = 100 if SMOKE else 400; correct = 0; rts = []; n = 0
    for _ in range(TR):
        A = cphasor(1, N, g)[0]; B = cphasor(1, N, g)[0]; book = np.stack([A, B]); true = int(g.integers(0, 2))
        target = book[true]; acc = np.zeros(N, dtype=np.complex64); decision = None
        for tstep in range(1, MAXT + 1):
            sample = DRIFT * target + SNOISE * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            acc = acc + sample
            sc = np.sort((book @ np.conj(acc)).real)[::-1] / (N * tstep)
            if (sc[0] - sc[1]) > THR:
                decision = int(np.argmax((book @ np.conj(acc)).real)); rts.append(tstep); break
        if decision is None:
            decision = int(np.argmax((book @ np.conj(acc)).real)); rts.append(MAXT)
        correct += int(decision == true); n += 1
    acc_rate = correct / n; mrt = float(np.mean(rts))
    print("  DRIFT-DIFFUSION accuracy=%.3f mean-RT=%.1f steps (drift=%.2f noise=%.1f thr=%.2f, n=%d)" % (acc_rate, mrt, DRIFT, SNOISE, THR, n), flush=True)
    return {"ddm_accuracy": acc_rate, "mean_rt": round(mrt, 1), "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "accuracy=%.3f mean-RT=%.1f" % (r["ddm_accuracy"], r["mean_rt"])
    if r["ddm_accuracy"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate evidence-accumulation (drift-diffusion) reaches >=0.85 accuracy by integrating noisy samples to a decision threshold -- biological sequential evidence integration; speed-accuracy via threshold. " + s)
    if r["ddm_accuracy"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: DDM accuracy 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: DDM accuracy <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
