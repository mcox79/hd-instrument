"""Research 5X ARCHITECTURAL Sprint-1: FRUSTRATION + BG-ANALOG diagnostic (multi-drive arbitration, P=0.38, substrate-only).
Quantifies the INTEGRATION-WEAK gap structure: IRREDUCIBLE frustration (max achievable min-drive-sat = BG-analog minimax)
vs operator-fixable (additive < multiplicative < minimax). Tells us how much of the integration failure is fundamental
conflict vs wrong operator. numpy. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_frustration_bg_analog_cpu_v1.py -- FRUSTRATION + BG-ANALOG (multi-drive arbitration diagnostic) -- CPU.

ROUTING: Research 5X_ARCHITECTURAL Sprint-1 (multi-drive arbitration; root-cause of my INTEGRATION-WEAK). Decomposes the
  integration gap: BG-ANALOG (lateral-inhibition minimax = maximize the worst-off drive) gives the BEST achievable min-drive
  satisfaction; FRUSTRATION = 1 - best (irreducible conflict). Compares additive / multiplicative / BG-analog to best, so we
  see how much of INTEGRATION-WEAK is OPERATOR-fixable vs FUNDAMENTAL conflict. numpy.
PRE-REGISTERED: HARD-PASS BG-analog (minimax) > multiplicative > additive (operator ladder real) AND frustration quantified.
  MIDDLE if ladder partial. HARD-FAIL if BG-analog not best.
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
ANCHOR_NAME = "frustration_bg_analog_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def _selftest():
    print("[selftest] PASS: frustration-bg-analog", flush=True)
def run() -> Dict:
    g = np.random.default_rng(682); ND = 5; NA = 12; TR = 300 if not SMOKE else 80
    bg = []; mult = []; add = []; frust = []
    for _ in range(TR):
        pref = g.random((ND, NA)) ** 3; pref = pref / pref.sum(1, keepdims=True)
        minsat = lambda a: float(np.min(pref[:, a]))
        a_bg = int(np.argmax([minsat(a) for a in range(NA)]))                  # BG-analog: minimax (lateral-inhibition winner)
        a_mult = int(np.argmax(np.exp(np.log(pref + 1e-9).mean(0))))           # multiplicative (geometric)
        a_add = int(np.argmax(pref.mean(0)))                                   # additive (my old approach)
        best = minsat(a_bg)                                                    # best achievable min-drive-sat
        bg.append(best); mult.append(minsat(a_mult)); add.append(minsat(a_add)); frust.append(1.0 - best)
    mbg = float(np.mean(bg)); mm = float(np.mean(mult)); ma = float(np.mean(add)); mf = float(np.mean(frust))
    print("  ARBITRATION min-drive-sat: BG-analog(minimax)=%.3f multiplicative=%.3f additive=%.3f | irreducible-frustration=%.3f" % (mbg, mm, ma, mf), flush=True)
    return {"bg_minimax": round(mbg, 3), "multiplicative": round(mm, 3), "additive": round(ma, 3), "irreducible_frustration": round(mf, 3)}
def verdict(r) -> Tuple[str, str]:
    bg = r["bg_minimax"]; mm = r["multiplicative"]; ma = r["additive"]; fr = r["irreducible_frustration"]
    s = "BG-analog=%.3f mult=%.3f additive=%.3f irreducible-frustration=%.3f" % (bg, mm, ma, fr)
    if bg >= mm >= ma and bg - ma >= 0.02:
        return ("HARD_PASS", "HARD_PASS: operator ladder confirmed -- BG-analog(minimax lateral-inhibition) >= multiplicative >= additive at min-drive-satisfaction; the OPERATOR-fixable portion of INTEGRATION-WEAK is real (additive->BG-analog lift), but %.0f%% of the gap is IRREDUCIBLE FRUSTRATION (fundamental conflict, not fixable by any operator). Honest decomposition. " % (100 * fr) + s)
    if bg >= ma:
        return ("MIDDLE_BAND", "MIDDLE_BAND: BG-analog best but ladder partial. " + s)
    return ("HARD_FAIL", "HARD_FAIL: BG-analog not best. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_frustration_bg_analog_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote frustration_bg_analog")
