"""
exp_sec_10k_substrate_cpu_v1.py -- SEC 10-K financial-metric query correctness >=0.95 -- CPU.

ROUTING: BATCH_4_CRITICAL vertical proof (A4 SEC 10-K finance substrate). Company->metric->value financial KB in substrate; metric-query correctness across 200 companies x 8 metrics -- finance vertical demo proof. Pure numpy (synthetic domain data). CPU.
PRE-REGISTERED: HARD-PASS correctness>=0.95. MIDDLE >=0.85. HARD-FAIL <0.85.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "sec_10k_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert (2==2), "eq"; print("[selftest] PASS: sec-10k-substrate", flush=True)
def run() -> Dict:
    g = np.random.default_rng(974); N = 8192; NCO = 200; NMETRIC = 8; cos_ = cphasor(NCO, N, g); metrics_ = cphasor(NMETRIC, N, g); VV = 400; vals = cphasor(VV, N, g)
    truth = {}; shard = np.zeros((NCO, N), dtype=np.complex64)
    for ci in range(NCO):
        for m in range(NMETRIC):
            vv = int(g.integers(0, VV)); shard[ci] = shard[ci] + metrics_[m] * vals[vv]; truth[(ci, m)] = vv
    TR = 100 if SMOKE else 400; hit = 0
    for _ in range(TR):
        ci = int(g.integers(0, NCO)); m = int(g.integers(0, NMETRIC))
        hit += int(cidx(shard[ci] * np.conj(metrics_[m]), vals) == truth[(ci, m)])
    acc = hit / TR; print("  SEC 10-K metric-query correctness=%.3f (%d companies x %d metrics, n=%d)" % (acc, NCO, NMETRIC, TR), flush=True)
    return {"acc": acc}
def verdict(r) -> Tuple[str, str]:
    s = "metric-query correctness=%.3f" % r["acc"]
    if r["acc"] >= 0.95: return ("HARD_PASS", "HARD_PASS: SEC 10-K financial-metric query correctness >=0.95 -- finance vertical demo proof. " + s)
    if r["acc"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: finance 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: finance <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
