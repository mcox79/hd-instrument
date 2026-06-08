"""
exp_federated_dp_aggregate_v1.py -- DP aggregate across M customers preserves the global routing distribution -- CPU.

ROUTING: federated_substrate PT1 aggregate-extension. Aggregate M per-customer DP-noised routing histograms (weighted mean) and compare to the true global aggregate. Validates federated global model utility. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS aggregate MAE < 0.02 at eps=1.0 across M=20 customers (averaging cancels per-customer DP noise). MIDDLE 0.02-0.05. HARD-FAIL > 0.05.
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
ANCHOR_NAME = "federated_dp_aggregate_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def gsig(eps, delta, sens=1.0):
    return float(np.sqrt(2*np.log(1.25/delta))*sens/eps)
def _selftest():
    assert gsig(1.0,1e-5) > 0, "sigma pos"; h = np.array([1.,1.]); assert abs((h/h.sum()).sum()-1)<1e-9, "norm"; assert gsig(0.5,1e-5)>gsig(2.0,1e-5), "noise order"
    print("[selftest] PASS: federated-dp-aggregate", flush=True)
def run() -> Dict:
    g = np.random.default_rng(3); BINS = 50; NPER = 500; EPS = 1.0; DELTA = 1e-5; M = 8 if SMOKE else 20; ALPHA = 0.5
    sigma = gsig(EPS, DELTA); true_agg = np.zeros(BINS); noisy_aggs = []
    for _ in range(M):
        p = g.dirichlet(np.full(BINS, ALPHA)); counts = g.multinomial(NPER, p).astype(float)
        true_agg += counts; noisy = np.clip(counts + g.normal(0, sigma, BINS), 0, None); noisy_aggs.append(noisy)
    true_n = true_agg / true_agg.sum(); agg = np.sum(noisy_aggs, axis=0); agg_n = agg / agg.sum()
    mae = float(np.abs(agg_n - true_n).mean())
    print("  federated aggregate MAE=%.4f across M=%d (eps=%.1f, per-customer sigma=%.2f)" % (mae, M, EPS, sigma), flush=True)
    return {"mae": mae, "M": M}
def verdict(r) -> Tuple[str, str]:
    s = "aggregate MAE=%.4f across M=%d (eps=1.0)" % (r["mae"], r["M"])
    if r["mae"] < 0.02: return ("HARD_PASS", "HARD_PASS: federated DP aggregate MAE<0.02 -- averaging across customers cancels per-customer DP noise; global model useful at strong privacy. " + s)
    if r["mae"] < 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: aggregate MAE 0.02-0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: aggregate MAE >0.05. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
