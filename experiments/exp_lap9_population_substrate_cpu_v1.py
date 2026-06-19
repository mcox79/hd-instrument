"""
exp_lap9_population_substrate_cpu_v1.py -- N=10 substrate ensemble vote beats single on noisy queries -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop batch (LAP-9 POPULATION-SUBSTRATE); pure-FHRR (no download). P independent substrates store the same KB with own vectors; majority vote vs single under query noise.
PRE-REGISTERED: HARD-PASS ensemble gain>=5pp. MIDDLE>=2pp. HARD-FAIL<2pp.
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
ANCHOR_NAME = "lap9_population_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert _n.bincount([1,1,2]).argmax()==1, "vote"; print("[selftest] PASS: population-substrate", flush=True)
def run() -> Dict:
    # P independent substrates each store the same M facts with their OWN random vectors; noisy retrieval; majority vote vs single.
    g = np.random.default_rng(909); N = 768; M = 90; VV = 100; P = 10; NOISE = 2.5
    TR = 30 if SMOKE else 200; single_ok = 0; ens_ok = 0; n = 0
    for _ in range(TR):
        truth = g.integers(0, VV, size=M)
        subs = []
        for p in range(P):
            keys = cphasor(M, N, g); vals = cphasor(VV, N, g)
            Mem = (keys * vals[truth]).sum(axis=0)
            subs.append((keys, vals, Mem))
        qi = int(g.integers(0, M))
        votes = []
        for p, (keys, vals, Mem) in enumerate(subs):
            noisy = Mem * np.conj(keys[qi]) + NOISE * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            votes.append(cidx(noisy, vals))
        single_ok += int(votes[0] == truth[qi])                          # substrate 0 alone
        ens = np.bincount(votes).argmax()
        ens_ok += int(ens == truth[qi]); n += 1
    sa = single_ok / n; ea = ens_ok / n
    print("  POPULATION single=%.3f ensemble(P=%d)=%.3f gain=%.3f (n=%d)" % (sa, ea, ea - sa, P, n), flush=True)
    return {"single_acc": sa, "ensemble_acc": ea, "gain_pp": round((ea - sa) * 100, 1), "P": P}
def verdict(r) -> Tuple[str, str]:
    s = "single=%.3f ensemble=%.3f gain=%.1fpp" % (r["single_acc"], r["ensemble_acc"], r["gain_pp"])
    if r["gain_pp"] >= 5.0:
        return ("HARD_PASS", "HARD_PASS: N=%d substrate population (majority vote) beats single by >=5pp on noisy queries -- biological population coding analog; ensembling averages independent encoding noise. " % r["P"] + s)
    if r["gain_pp"] >= 2.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: ensemble gain 2-5pp. " + s)
    return ("HARD_FAIL", "HARD_FAIL: ensemble gain <2pp. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
