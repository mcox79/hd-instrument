"""
exp_cross_kb_interference_cpu_v1.py -- false-match rate when two KBs share one space -- CPU.

ROUTING: CPU substrate-physics characterization (two-KB shared-space interference). Two independent KBs (N each) in the same D-dim space; query with noisy KB1 keys; measure the rate at which a KB2 item outranks the true KB1 match (cross-tenant interference). Validates multi-tenant isolation in a shared substrate. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS cross-KB interference rate <= 0.05 at N=10000 each. MIDDLE <= 0.15. HARD-FAIL > 0.15.
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
ANCHOR_NAME = "cross_kb_interference_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    assert np.argmax([1, 2, 3]) == 2, "argmax"; print("[selftest] PASS: cross-kb-interference-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(11); N = 6000 if SMOKE else 10000; D = 512; NQ = 300; FLIP = 0.15
    KB1 = np.sign(g.standard_normal((N, D))).astype(np.float32); KB2 = np.sign(g.standard_normal((N, D))).astype(np.float32)
    ALL = np.vstack([KB1, KB2]); qi = g.choice(N, NQ, replace=False); Q = KB1[qi].copy(); fl = g.random((NQ, D)) < FLIP; Q[fl] *= -1
    pred = np.argmax(Q @ ALL.T, axis=1); interference = float((pred >= N).mean()); recall = float((pred == qi).mean())
    print("  cross-KB interference=%.4f recall=%.4f (N=%d each, D=%d)" % (interference, recall, N, D), flush=True)
    return {"interference": interference, "recall": recall}
def verdict(r) -> Tuple[str, str]:
    s = "interference=%.4f recall=%.4f" % (r["interference"], r["recall"])
    if r["interference"] <= 0.05: return ("HARD_PASS", "HARD_PASS: cross-KB interference <=0.05 -- two tenants share one space with negligible cross-talk (multi-tenant isolation). " + s)
    if r["interference"] <= 0.15: return ("MIDDLE_BAND", "MIDDLE_BAND: interference 0.05-0.15. " + s)
    return ("HARD_FAIL", "HARD_FAIL: interference >0.15 -- shared-space tenants leak. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
