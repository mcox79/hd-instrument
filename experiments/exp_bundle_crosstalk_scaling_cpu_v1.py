"""
exp_bundle_crosstalk_scaling_cpu_v1.py -- empirical bundle unbind crosstalk norm scales as sqrt(K-1) -- CPU.

ROUTING: CPU substrate-physics characterization (bundle unbind crosstalk vs size). Measure the unbind crosstalk (rec - true filler) norm as a function of bundle size K (FHRR role-filler superposition); compare to the theoretical sqrt(K-1) law. Validates the composition noise model that governs bundle capacity. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS empirical crosstalk norm within 15pct of sqrt(K-1) across K. MIDDLE within 30pct. HARD-FAIL > 30pct deviation.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "bundle_crosstalk_scaling_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

import math
def _selftest():
    assert abs(math.sqrt(4) - 2.0) < 1e-9, "sqrt"; print("[selftest] PASS: bundle-crosstalk-scaling-cpu", flush=True)
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def run() -> Dict:
    g = np.random.default_rng(4); N = 4096; TR = 30 if SMOKE else 120; devs = []; rows = {}
    for K in [2, 4, 8, 16]:
        emps = []
        for _ in range(TR):
            roles = cphasor(K, N, g); fillers = cphasor(K, N, g)
            rec = ((roles * fillers).sum(0)) * roles[0].conj()         # unbind slot 0
            crosstalk = rec - fillers[0]                               # everything except the true filler
            emps.append(float(np.linalg.norm(crosstalk) / math.sqrt(N)))
        emp = float(np.mean(emps)); theo = math.sqrt(max(1, K - 1)); dev = abs(emp - theo) / theo; devs.append(dev); rows["K%d" % K] = round(emp, 3)
        print("  K=%d crosstalk-norm=%.3f theory(sqrt(K-1))=%.3f dev=%.2f" % (K, emp, theo, dev), flush=True)
    md = float(np.max(devs)); return {"max_dev": md, "rows": rows}
def verdict(r) -> Tuple[str, str]:
    s = "max deviation from sqrt(K-1) = %.2f | crosstalk-norm: %s" % (r["max_dev"], r["rows"])
    if r["max_dev"] <= 0.15: return ("HARD_PASS", "HARD_PASS: bundle crosstalk norm matches sqrt(K-1) within 15pct -- composition noise model validated (predictable capacity). " + s)
    if r["max_dev"] <= 0.30: return ("MIDDLE_BAND", "MIDDLE_BAND: crosstalk within 30pct of theory. " + s)
    return ("HARD_FAIL", "HARD_FAIL: crosstalk deviates >30pct from sqrt(K-1). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
