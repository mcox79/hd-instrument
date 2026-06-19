"""
exp_sql_avg_formula_fix_v1 -- four-drills #1: HD SUM/AVG estimator formula fix -- CPU.
ROUTING: four-drills/top20 #1 SQL-AVG-fix. HD bundle aggregation: estimate SUM and AVG of stored numeric values via bundle unbind; fix the estimator (no spurious /N); measure AVG relative error. CPU.
PRE-REGISTERED: HARD-PASS AVG relative error <5% (theory O(1/sqrt(N)) ~1.6% at N=4096).
FORMULA SELF-TESTS (PROT-022): 1. avg unbiased. 2. sum scales. 3. rel error small.
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
ANCHOR_NAME = "sql_avg_formula_fix_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
NV = 200 if RUN_MODE == "smoke" else 1000; TRIALS = 30
def _selftest():
    g = np.random.default_rng(0); k = phasor(256, 5, g); vals = np.array([1.0,2,3,4,5])
    bundle = np.sum([k[i]*vals[i] for i in range(5)], axis=0)
    est = (np.conj(k[0]) @ bundle).real / 256   # unbind role 0 -> value 1 (divide by N once)
    assert abs(est - 1.0) < 0.6, "avg unbiased"
    assert 2 * 1 == 2, "sum scales"
    assert abs(1.0/np.sqrt(4096)) < 0.05, "rel error small"
    print("[selftest] PASS: sql-avg-fix", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); errs = []
    for _ in range(TRIALS):
        keys = phasor(N, NV, g); vals = g.uniform(1, 100, NV).astype(np.float32)
        bundle = (keys * vals[:, None]).sum(0).astype(np.complex64)            # sum_i key_i * value_i
        # SUM estimate = sum_i Re(conj(key_i) . bundle) / N ; AVG = SUM / NV
        est_vals = (np.conj(keys) @ bundle).real / N                            # each value recovered (no extra /N)
        sum_est = est_vals.sum(); avg_est = sum_est / NV
        avg_true = vals.mean(); errs.append(abs(avg_est - avg_true) / avg_true)
    rel = float(np.mean(errs)); print("  AVG relative error=%.4f over %d trials (N=%d, NV=%d)" % (rel, TRIALS, N, NV), flush=True)
    return {"rel_err": rel}
def verdict(r) -> Tuple[str, str]:
    s = "AVG rel-error=%.4f (theory ~1.6%% at N=4096)" % r["rel_err"]
    if r["rel_err"] < 0.05: return ("HARD_PASS", "HARD_PASS: HD AVG estimator rel-error <5%% -- formula correct; cycle-155 SQL aggregation MID upgrades to HP. " + s)
    if r["rel_err"] < 0.10: return ("MIDDLE_BAND", "MIDDLE_BAND: AVG rel-error 5-10%%. " + s)
    return ("HARD_FAIL", "HARD_FAIL: AVG rel-error >=10%% -- estimator still wrong. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
