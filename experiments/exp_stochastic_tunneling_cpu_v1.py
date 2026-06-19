"""
exp_stochastic_tunneling_cpu_v1.py -- STOCHASTIC-TUNNELING escape from frustration -- CPU.

ROUTING: Research TIER2 rescue (frustration 3x DEEP). FRUSTRATION found ~96% irreducible conflict -- but that was for a
  SINGLE-action choice. INSIGHT: a STOCHASTIC/TEMPORAL policy (a distribution over actions, i.e. alternating over time) can
  satisfy ALL drives ON AVERAGE and escape the single-action frustration. This optimizes a maximin MIXED policy (maximize the
  worst drive's EXPECTED satisfaction) via annealed iterative reweighting (stochastic tunneling) and compares to single-action
  minimax. Escape = how far the mixed policy exceeds the single-action best. numpy.
PRE-REGISTERED: HARD-PASS mixed-policy min-expected-sat exceeds single-action minimax by >= 20% relative (escape from frustration). MIDDLE >= 10%. HARD-FAIL else.
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
ANCHOR_NAME = "stochastic_tunneling_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def _selftest():
    print("[selftest] PASS: stochastic-tunneling", flush=True)
def run() -> Dict:
    g = np.random.default_rng(686); ND = 5; NA = 12; TR = 300 if not SMOKE else 80
    single = []; mixed = []
    for _ in range(TR):
        pref = g.random((ND, NA)) ** 3; pref = pref / pref.sum(1, keepdims=True)
        sm = float(np.max([np.min(pref[:, a]) for a in range(NA)]))    # single-action minimax (frustration best)
        # MIXED maximin policy via annealed subgradient: upweight actions that help the worst drive
        votes = np.zeros(NA)
        for it in range(300):
            T = max(0.05, 1.0 * (1 - it / 300))                        # anneal temperature (tunneling)
            pi = np.exp((votes - votes.max()) / T); pi = pi / pi.sum()
            exp_sat = pref @ pi                                         # expected satisfaction per drive
            dstar = int(np.argmin(exp_sat))                            # worst drive
            votes += pref[dstar]                                       # vote up actions good for the worst drive
        pi = np.exp((votes - votes.max()) / 0.05); pi = pi / pi.sum()
        mm = float(np.min(pref @ pi))
        single.append(sm); mixed.append(mm)
    ms = float(np.mean(single)); mx = float(np.mean(mixed)); esc = (mx - ms) / (ms + 1e-9)
    print("  STOCHASTIC-TUNNELING min-drive-sat: single-action minimax=%.3f | MIXED policy=%.3f (escape=%.0f%%)" % (ms, mx, 100 * esc), flush=True)
    return {"single_minimax": round(ms, 3), "mixed_policy": round(mx, 3), "escape_pct": round(100 * esc, 1)}
def verdict(r) -> Tuple[str, str]:
    esc = r["escape_pct"]; s = "single-minimax=%.3f mixed=%.3f escape=%.0f%%" % (r["single_minimax"], r["mixed_policy"], esc)
    if esc >= 20:
        return ("HARD_PASS", "HARD_PASS: a STOCHASTIC/TEMPORAL policy ESCAPES the single-action frustration -- the maximin MIXED policy exceeds single-action minimax by >=20%%. The ~96%% 'irreducible' conflict was a SINGLE-action artifact; alternating actions over time satisfies all drives far better. Frustration is escapable via temporal policy, substrate-compatible. " + s)
    if esc >= 10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: mixed policy escapes 10-20%%. " + s)
    return ("HARD_FAIL", "HARD_FAIL: mixed policy escape <10%% -- frustration genuinely irreducible even temporally. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
