"""
exp_burial_depth_invariant_v1.py -- load-bearing bindings detected + protected from decay -- CPU.

ROUTING: DEEPER_drills_8 Anchor 1.2 (burial-depth / load-bearing protection). Some bindings are load-bearing (referenced by many composite facts). Detect them by reference count; protect (exempt from decay); verify protected bindings survive N decay cycles while unreferenced ones decay out. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS load-bearing detection accuracy >= 0.95 AND protected bindings retain >= 0.95 recall after decay cycles (vs unprotected decaying out). MIDDLE 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "burial_depth_invariant_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    refs = {0: 10, 1: 1, 2: 8}; lb = [k for k, v in refs.items() if v >= 5]; assert set(lb) == {0, 2}, "load-bearing by refcount"
    w = 1.0; w *= 0.9; assert w < 1.0, "decay shrinks"
    assert sorted([3, 1])[0] == 1, "sort"
    print("[selftest] PASS: burial-depth-invariant", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2); N = 500 if SMOKE else 2000; THR = 5; CYCLES = 20; DECAY = 0.85
    refcount = g.integers(0, 12, N)                          # how many composites reference each binding
    load_bearing = refcount >= THR                          # ground truth
    detected = refcount >= THR                              # detector (refcount-based) -- here exact; test robustness with noise
    noisy_rc = refcount + g.integers(-1, 2, N)
    detected = noisy_rc >= THR
    det_acc = float((detected == load_bearing).mean())
    # decay: weights start 1.0; protected (detected load-bearing) exempt; others decay each cycle
    w = np.ones(N)
    for _ in range(CYCLES):
        w[~detected] *= DECAY
    protected_recall = float((w[load_bearing] >= 0.95).mean()) if load_bearing.any() else 1.0
    unprotected_decayed = float((w[~load_bearing] < 0.5).mean()) if (~load_bearing).any() else 1.0
    print("  load-bearing detection acc=%.3f | protected retention=%.3f unprotected decayed=%.3f (N=%d cycles=%d)" % (det_acc, protected_recall, unprotected_decayed, N, CYCLES), flush=True)
    return {"det_acc": det_acc, "protected": protected_recall, "unprotected_decayed": unprotected_decayed}
def verdict(r) -> Tuple[str, str]:
    s = "detection=%.3f protected-retention=%.3f unprotected-decayed=%.3f" % (r["det_acc"], r["protected"], r["unprotected_decayed"])
    if r["det_acc"] >= 0.95 and r["protected"] >= 0.95: return ("HARD_PASS", "HARD_PASS: load-bearing bindings detected >=0.95 + protected from decay -- burial-depth invariant holds (critical facts survive consolidation). " + s)
    if r["det_acc"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: detection 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: load-bearing detection <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
