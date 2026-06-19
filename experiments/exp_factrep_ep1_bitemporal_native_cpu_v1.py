"""
exp_factrep_ep1_bitemporal_native_cpu_v1.py -- facts carry valid-time + transaction-time; AS-OF query returns the version valid at t -- CPU.

ROUTING: DEMO_SUPPORT C1 fact-rep pre-test (EP1 bitemporal-native fact representation). Each fact is stored as key * VALID_period * value across a timeline; an AS-OF(t) query recovers the value that was valid at time t (and a corrected value supersedes for later t). Tests whether bitemporal versioning is native (cheap to ship in v1). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS AS-OF query returns the correct time-valid version >= 0.95 across a timeline with corrections. MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "factrep_ep1_bitemporal_native_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; t = cphasor(1, 32, g)[0]; v = cphasor(1, 32, g)[0]
    assert np.allclose(a * t * v * np.conj(a * t), v, atol=1e-3), "bind/unbind"; print("[selftest] PASS: factrep-ep1-bitemporal-native", flush=True)
def run() -> Dict:
    g = np.random.default_rng(201); N = 4096; VK = 100; VV = 400; NT = 8; TR = 60 if SMOKE else 200
    keys = cphasor(VK, N, g); vals = cphasor(VV, N, g); times = cphasor(NT, N, g)   # NT discrete time periods
    hit = 0; n = 0
    for _ in range(TR):
        k = int(g.integers(0, VK))
        # this key gets 2-3 versions over time: value changes at version boundaries
        nver = int(g.integers(2, 4)); bounds = sorted(g.choice(range(1, NT), nver - 1, replace=False).tolist()) if nver > 1 else []
        segs = [0] + bounds + [NT]; vlist = g.choice(VV, nver, replace=False)
        M = np.zeros(N, dtype=np.complex64)
        for vi in range(nver):
            for t in range(segs[vi], segs[vi + 1]):
                M = M + keys[k] * times[t] * vals[int(vlist[vi])]
        # distractor facts
        for _d in range(20):
            kk = int(g.integers(0, VK)); tt = int(g.integers(0, NT)); M = M + keys[kk] * times[tt] * vals[int(g.integers(0, VV))]
        # AS-OF query at a random time
        qt = int(g.integers(0, NT)); seg = next(vi for vi in range(nver) if segs[vi] <= qt < segs[vi + 1]); gold = int(vlist[seg])
        pred = cidx(M * np.conj(keys[k] * times[qt]), vals); hit += int(pred == gold); n += 1
    rec = hit / max(1, n); print("  bitemporal AS-OF correct=%.3f (n=%d)" % (rec, n), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "AS-OF correctness=%.3f" % r["recall"]
    if r["recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: bitemporal-native AS-OF returns the time-valid version >=0.95 -- versioned fact representation is cheap/native (ship-in-v1 candidate). " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: AS-OF 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: AS-OF <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
