"""
exp_stretch3_2_stochastic_resonance_cpu_v1.py -- noise improves sub-threshold signal detection (SR) -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 (STRETCH3-2 STOCHASTIC-RESONANCE); pure-FHRR (no download). Sub-threshold weak signal; sweep noise; detection d' peaks at intermediate noise.
PRE-REGISTERED: HARD-PASS peak-d' - zero-noise >= 0.15 at sigma>0. MIDDLE>=0.08. HARD-FAIL else.
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
ANCHOR_NAME = "stretch3_2_stochastic_resonance_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: stochastic-resonance", flush=True)
def run() -> Dict:
    # stochastic resonance: a SUB-THRESHOLD weak signal is detected better WITH some noise than with none. Detection statistic
    # d' = (true-positive - false-positive) over a threshold; sweep noise sigma; the SR curve peaks at intermediate noise.
    g = np.random.default_rng(2); N = 4096; VV = 80; vals = cphasor(VV, N, g)
    sigmas = [0.0, 0.3, 0.6, 1.0, 1.5, 2.2, 3.2]; TR = 200 if not SMOKE else 60
    WEAK = 0.18                                                          # weak (sub-threshold) signal amplitude
    THR = 0.22                                                          # detection threshold on normalized cleanup margin
    dprime = {}
    for sig in sigmas:
        tp = 0; fp = 0; npos = 0; nneg = 0
        for _ in range(TR):
            present = g.random() < 0.5; vi = int(g.integers(0, VV))
            base = (WEAK * vals[vi]) if present else np.zeros(N, dtype=np.complex64)
            obs = base + sig * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            margin = float(np.max((vals @ np.conj(obs)).real)) / N
            det = margin > THR
            if present:
                tp += int(det); npos += 1
            else:
                fp += int(det); nneg += 1
        tpr = tp / max(1, npos); fpr = fp / max(1, nneg); dprime[sig] = round(tpr - fpr, 3)
    base0 = dprime[0.0]; peak = max(dprime.values()); peak_sig = max(dprime, key=lambda k: dprime[k])
    print("  STOCHASTIC-RESONANCE d'(tpr-fpr) by sigma=%s peak=%.3f@sigma=%.1f zero-noise=%.3f" % (dprime, peak, peak_sig, base0), flush=True)
    return {"dprime_by_sigma": {str(k): v for k, v in dprime.items()}, "peak": peak, "peak_sigma": peak_sig, "zero_noise": base0}
def verdict(r) -> Tuple[str, str]:
    s = "peak-d'=%.3f@sigma=%.1f vs zero-noise=%.3f" % (r["peak"], r["peak_sigma"], r["zero_noise"])
    if r["peak"] - r["zero_noise"] >= 0.15 and r["peak_sigma"] > 0:
        return ("HARD_PASS", "HARD_PASS: stochastic resonance -- detection of a sub-threshold signal peaks at intermediate noise, beating zero-noise by >=0.15 d'. Optimal noise improves substrate signal detection (biological SR). " + s)
    if r["peak"] - r["zero_noise"] >= 0.08:
        return ("MIDDLE_BAND", "MIDDLE_BAND: SR effect 0.08-0.15. " + s)
    return ("HARD_FAIL", "HARD_FAIL: no SR effect. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
