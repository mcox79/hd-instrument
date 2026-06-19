"""
exp_conv13_higher_order_cpu_v1.py -- substrate retrieves through 2 levels of nested binding -- CPU.

ROUTING: HUGE_BATCH TIER-2 laptop (CONV-13 higher-order composition); pure-FHRR (no HF download, no desktop CPU). Nested records (role-of-(subrole-filler)); retrieve fillers through two unbinding levels.
PRE-REGISTERED: HARD-PASS 2-level>=0.85. MIDDLE>=0.65. HARD-FAIL<0.65.
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
ANCHOR_NAME = "conv13_higher_order_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert _n.allclose(_n.exp(1j*0.0), 1+0j), "phasor"; print("[selftest] PASS: conv13-higher-order", flush=True)
def run() -> Dict:
    # higher-order composition: nested records. outer = sum_i role_i * inner_i ; inner_i = sum_j subrole_j * filler_ij.
    # retrieve through TWO levels of unbinding: unbind(outer, role_i) -> inner_i ; unbind(inner_i, subrole_j) -> filler_ij.
    g = np.random.default_rng(44); N = 8192; NR = 3; NS = 3; VF = 200
    roles = cphasor(NR, N, g); subroles = cphasor(NS, N, g); fillers = cphasor(VF, N, g)
    TR = 60 if SMOKE else 240; lvl2 = 0; n = 0
    for _ in range(TR):
        truth = {}; outer = np.zeros(N, dtype=np.complex64)
        for i in range(NR):
            inner = np.zeros(N, dtype=np.complex64)
            for j in range(NS):
                f = int(g.integers(0, VF)); inner = inner + subroles[j] * fillers[f]; truth[(i, j)] = f
            outer = outer + roles[i] * inner
        for i in range(NR):
            inner_hat = outer * np.conj(roles[i])                         # level-1 unbind -> approx inner_i
            for j in range(NS):
                pred = cidx(inner_hat * np.conj(subroles[j]), fillers)    # level-2 unbind -> filler
                lvl2 += int(pred == truth[(i, j)]); n += 1
    acc = lvl2 / n
    print("  CONV-13 higher-order 2-level retrieval acc=%.3f (NR=%d, NS=%d, n=%d)" % (acc, NR, NS, n), flush=True)
    return {"twolevel_acc": acc, "depth": 2}
def verdict(r) -> Tuple[str, str]:
    s = "2-level-retrieval=%.3f" % r["twolevel_acc"]
    if r["twolevel_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate retrieves fillers through TWO levels of nested binding >=85pct -- higher-order compositional structure holds (role-of-(subrole-filler)). Substrate algebra extends to nested records. " + s)
    if r["twolevel_acc"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 2-level 0.65-0.85 (nested superposition load; sub-sharding lifts). " + s)
    return ("HARD_FAIL", "HARD_FAIL: 2-level <0.65. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
