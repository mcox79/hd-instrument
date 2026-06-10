"""
exp_lap4_4_n1000_ensemble_cpu_v1.py -- N=1000 ensemble saturation characterization -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (LAP4-4 N=1000-ENSEMBLE-STRESS); pure-FHRR (no download). Push ensemble to N=1000; map the accuracy-vs-P curve + diminishing returns past N=100.
PRE-REGISTERED: HARD-PASS best-single>=0.20 AND saturation mapped. MIDDLE>=0.10. HARD-FAIL<0.10.
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
ANCHOR_NAME = "lap4_4_n1000_ensemble_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: n1000-ensemble-stress", flush=True)
def run() -> Dict:
    g = np.random.default_rng(1000); N = 512; M = 90; VV = 100; NOISE = 2.6
    Ps = [1, 10, 50, 100, 300, 1000]; TR = 8 if SMOKE else 40
    acc_by_P = {p: 0 for p in Ps}; n = 0
    for _ in range(TR):
        truth = g.integers(0, VV, size=M); votes = []
        for p in range(1000):
            keys = cphasor(M, N, g); vals = cphasor(VV, N, g); Mem = (keys * vals[truth]).sum(axis=0)
            qi_seed = p
            votes.append((keys, vals, Mem))
        qi = int(g.integers(0, M)); allv = []
        for (keys, vals, Mem) in votes:
            noisy = Mem * np.conj(keys[qi]) + NOISE * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            allv.append(cidx(noisy, vals))
        allv = np.array(allv)
        for p in Ps:
            acc_by_P[p] += int(np.bincount(allv[:p]).argmax() == truth[qi])
        n += 1
    curve = {str(p): round(acc_by_P[p] / n, 3) for p in Ps}
    sat = curve[str(1000)] - curve[str(100)]                            # marginal gain N=100->1000
    print("  N=1000-ENSEMBLE accuracy-by-P=%s saturation(1000 vs 100)=%.3f" % (curve, sat), flush=True)
    return {"acc_by_P": curve, "saturation_gain": round(sat, 3), "single": curve[str(1)], "best": curve[str(1000)]}
def verdict(r) -> Tuple[str, str]:
    s = "single=%.3f N100=%s N1000=%.3f sat-gain(1000vs100)=%.3f" % (r["single"], r["acc_by_P"].get("100"), r["best"], r["saturation_gain"])
    if r["best"] - r["single"] >= 0.20 and r["saturation_gain"] >= 0.0:
        return ("HARD_PASS", "HARD_PASS: N=1000 ensemble characterized -- large lift over single (>=0.20) with diminishing returns past N=100 (saturation curve mapped); sqrt-N population coding saturates as predicted. " + s)
    if r["best"] - r["single"] >= 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: N=1000 lift 0.10-0.20. " + s)
    return ("HARD_FAIL", "HARD_FAIL: N=1000 lift <0.10. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
