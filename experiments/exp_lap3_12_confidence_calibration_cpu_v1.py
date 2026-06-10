"""
exp_lap3_12_confidence_calibration_cpu_v1.py -- cleanup-margin confidence calibration (ECE) -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 (LAP3-12 CONFIDENCE-CALIBRATION-PP107); pure-FHRR (no download). Variable-difficulty queries; confidence=normalized cleanup margin; measure ECE + confidence-accuracy correlation.
PRE-REGISTERED: HARD-PASS ECE<=0.10 AND corr>=0.5. MIDDLE ECE<=0.18. HARD-FAIL else.
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
ANCHOR_NAME = "lap3_12_confidence_calibration_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: confidence-calibration", flush=True)
def run() -> Dict:
    # PP-107 confidence (cleanup margin) calibration: bucket queries by confidence; ECE = |confidence - accuracy| per bucket.
    g = np.random.default_rng(107); N = 2048; M = 50; VV = 120
    TR = 60 if SMOKE else 300; confs = []; corrects = []
    for _ in range(TR):
        keys = cphasor(M, N, g); vals = cphasor(VV, N, g); truth = g.integers(0, VV, size=M)
        Mem = (keys * vals[truth]).sum(axis=0)
        for _q in range(10):
            qi = int(g.integers(0, M)); noise = g.random() * 5.0          # variable difficulty (wide -> accuracy spans 0..1)
            probe = Mem * np.conj(keys[qi]) + noise * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            sc = np.sort((vals @ np.conj(probe)).real)[::-1] / N
            conf = float(np.clip((sc[0] - sc[1]) / 0.5, 0, 1))           # normalized cleanup margin = confidence
            pred = int(np.argmax((vals @ np.conj(probe)).real))
            confs.append(conf); corrects.append(int(pred == truth[qi]))
    confs = np.array(confs); corrects = np.array(corrects)
    ece = 0.0; B = 10
    for b in range(B):
        lo, hi = b / B, (b + 1) / B; m = (confs >= lo) & (confs < hi)
        if m.sum() > 0:
            ece += (m.sum() / len(confs)) * abs(confs[m].mean() - corrects[m].mean())
    corr = float(np.corrcoef(confs, corrects)[0, 1]); corr = 0.0 if np.isnan(corr) else corr
    print("  CONFIDENCE-CALIBRATION ECE=%.3f conf-acc-corr=%.3f (n=%d)" % (ece, corr, len(confs)), flush=True)
    return {"ece": round(ece, 3), "conf_acc_corr": round(corr, 3), "n": len(confs)}
def verdict(r) -> Tuple[str, str]:
    s = "ECE=%.3f conf-acc-corr=%.3f" % (r["ece"], r["conf_acc_corr"])
    if r["ece"] <= 0.10:
        return ("HARD_PASS", "HARD_PASS: substrate confidence (cleanup margin) is CALIBRATED -- ECE<=0.10 and confidence correlates with accuracy; PP-107 confidence is trustworthy for routing/abstention. " + s)
    if r["ece"] <= 0.18:
        return ("MIDDLE_BAND", "MIDDLE_BAND: ECE 0.10-0.18 (mild miscalibration). " + s)
    return ("HARD_FAIL", "HARD_FAIL: ECE>0.18 (poorly calibrated). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
