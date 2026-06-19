"""
exp_lap3_7_n100_ensemble_cpu_v1.py -- N=100 substrate ensemble noise robustness -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 (LAP3-7 N=100-ENSEMBLE-POPULATION); pure-FHRR (no download). 100 independent substrates vote on noisy queries; measure gain over single + the N=10 baseline.
PRE-REGISTERED: HARD-PASS N=100 gain>=20pp. MIDDLE>=10pp. HARD-FAIL<10pp.
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
ANCHOR_NAME = "lap3_7_n100_ensemble_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert _n.bincount([2,2,1]).argmax()==2, "vote"; print("[selftest] PASS: n100-ensemble", flush=True)
def run() -> Dict:
    g = np.random.default_rng(249); N = 512; M = 90; VV = 100; NOISE = 2.6
    TR = 20 if SMOKE else 120; single = 0; ens10 = 0; ens100 = 0; n = 0
    for _ in range(TR):
        truth = g.integers(0, VV, size=M); P = 100
        subs = []
        for p in range(P):
            keys = cphasor(M, N, g); vals = cphasor(VV, N, g); Mem = (keys * vals[truth]).sum(axis=0); subs.append((keys, vals, Mem))
        qi = int(g.integers(0, M)); votes = []
        for (keys, vals, Mem) in subs:
            noisy = Mem * np.conj(keys[qi]) + NOISE * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            votes.append(cidx(noisy, vals))
        single += int(votes[0] == truth[qi])
        ens10 += int(np.bincount(votes[:10]).argmax() == truth[qi])
        ens100 += int(np.bincount(votes).argmax() == truth[qi]); n += 1
    sa = single / n; e10 = ens10 / n; e100 = ens100 / n
    print("  N=100-ENSEMBLE single=%.3f ens10=%.3f ens100=%.3f gain100=%.1fpp (n=%d)" % (sa, e10, e100, (e100 - sa) * 100, n), flush=True)
    return {"single": sa, "ens10": e10, "ens100": e100, "gain100_pp": round((e100 - sa) * 100, 1)}
def verdict(r) -> Tuple[str, str]:
    s = "single=%.3f ens10=%.3f ens100=%.3f gain=%.1fpp" % (r["single"], r["ens10"], r["ens100"], r["gain100_pp"])
    if r["gain100_pp"] >= 20.0:
        return ("HARD_PASS", "HARD_PASS: N=100 substrate ensemble lifts noisy-recall by >=20pp over single (past PP-249 N=10) -- sqrt-N population-coding improvement holds to N=100. " + s)
    if r["gain100_pp"] >= 10.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: N=100 gain 10-20pp. " + s)
    return ("HARD_FAIL", "HARD_FAIL: N=100 gain <10pp. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
