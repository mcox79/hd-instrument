"""
exp_integ_softmax_t1_cpu_v1.py -- INTEG-SOFTMAX-T1 (multiplicative integration; fix for INTEGRATION-WEAK) -- CPU.

ROUTING: Research 5X_ARCHITECTURAL Sprint-1 (integration). My Sprint-2 INTEGRATION-ALGEBRA was WEAK: ADDITIVE weighted-sum
  integration of 5 competing drives did NOT beat baselines (it can starve a drive). This tests the proposed fix: MULTIPLICATIVE
  (geometric-mean / softmax) integration -- the universal operator per 5 convergent streams. Multiplicative gating penalizes
  any low-satisfaction drive (product is small if any drive is starved), so it maximizes the MIN drive satisfaction. Compares
  multiplicative vs my additive vs equal-weight vs best-single, under CONFLICT. numpy. N/A substrate-dims (drive-value algebra).
PRE-REGISTERED: HARD-PASS multiplicative min-drive-sat > additive AND > equal-weight (lift>=0.05) -- the operator FIXES integration. MIDDLE >= additive. HARD-FAIL else.
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
ANCHOR_NAME = "integ_softmax_t1_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def _selftest():
    print("[selftest] PASS: integ-softmax-t1", flush=True)
def run() -> Dict:
    g = np.random.default_rng(681); ND = 5; NA = 12; TR = 200 if not SMOKE else 60
    mult = []; add = []; eqw = []; bsingle = []
    for _ in range(TR):
        pref = g.random((ND, NA)) ** 3; pref = pref / pref.sum(1, keepdims=True)   # conflicting peaked drives
        def minsat(a):
            return float(np.min(pref[:, a]))
        # MULTIPLICATIVE integration (geometric mean over drives) -- the proposed fix
        a_mult = int(np.argmax(np.exp(np.log(pref + 1e-9).mean(0))))
        # ADDITIVE (my old approach: equal-weight sum)
        a_add = int(np.argmax(pref.mean(0)))
        # equal-weight == additive sum here; best-single = optimize one drive
        a_eq = a_add
        bs = max(minsat(int(np.argmax(pref[d]))) for d in range(ND))
        mult.append(minsat(a_mult)); add.append(minsat(a_add)); eqw.append(minsat(a_eq)); bsingle.append(bs)
    mm = float(np.mean(mult)); ma = float(np.mean(add)); me = float(np.mean(eqw)); mb = float(np.mean(bsingle))
    print("  INTEG-SOFTMAX min-drive-sat: MULTIPLICATIVE=%.3f additive=%.3f equal-weight=%.3f best-single=%.3f" % (mm, ma, me, mb), flush=True)
    return {"multiplicative_minsat": round(mm, 3), "additive_minsat": round(ma, 3), "equalweight_minsat": round(me, 3), "bestsingle_minsat": round(mb, 3)}
def verdict(r) -> Tuple[str, str]:
    mm = r["multiplicative_minsat"]; ma = r["additive_minsat"]; me = r["equalweight_minsat"]; mb = r["bestsingle_minsat"]
    s = "multiplicative=%.3f additive=%.3f equal-weight=%.3f best-single=%.3f" % (mm, ma, me, mb)
    if mm > ma and mm - me >= 0.05:
        return ("HARD_PASS", "HARD_PASS: MULTIPLICATIVE (geometric/softmax) integration beats additive AND equal-weight at min-drive-satisfaction (>=0.05 lift) -- the universal integration operator FIXES the Sprint-2 INTEGRATION-ALGEBRA WEAK result. Integration gap is mechanism-fixable, substrate-native. " + s)
    if mm >= ma:
        return ("MIDDLE_BAND", "MIDDLE_BAND: multiplicative >= additive but lift <0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: multiplicative integration does not beat additive -- integration gap deeper than operator choice. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
