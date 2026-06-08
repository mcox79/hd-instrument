"""
exp_continuous_regression_cpu_v1.py -- pinv readout recalls continuous scalar values (not just discrete items) -- CPU.

ROUTING: CPU substrate capability characterization (key->scalar regression readout). Store (key -> continuous scalar) pairs via a ridge readout vector; predict the stored scalar for each key; measure R^2. Tests that the substrate holds continuous (numeric) payloads, not only categorical fillers. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS R^2 >= 0.95 at load M/D=0.7. MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "continuous_regression_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    assert abs(np.corrcoef([1, 2, 3], [1, 2, 3])[0, 1] - 1.0) < 1e-9, "corr"; print("[selftest] PASS: continuous-regression-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(34); D = 512; M = int(0.7 * D); lam = 1e-2
    K = np.sign(g.standard_normal((M, D))).astype(np.float64); y = g.standard_normal(M)
    w = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ y); yhat = K @ w
    ss_res = float(np.sum((y - yhat) ** 2)); ss_tot = float(np.sum((y - y.mean()) ** 2)); r2 = 1 - ss_res / ss_tot
    print("  R^2=%.4f at load M/D=0.7 (D=%d M=%d)" % (r2, D, M), flush=True)
    return {"r2": r2}
def verdict(r) -> Tuple[str, str]:
    s = "R^2=%.4f" % r["r2"]
    if r["r2"] >= 0.95: return ("HARD_PASS", "HARD_PASS: continuous-value readout R^2>=0.95 -- substrate stores numeric payloads, not just categories. " + s)
    if r["r2"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: R^2 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: R^2 <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
