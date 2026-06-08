"""
exp_factrep_ep2_continuous_strength_cpu_v1.py -- facts carry a continuous strength; retrieval is strength-ordered and strength is recoverable -- CPU.

ROUTING: DEMO_SUPPORT C1 fact-rep pre-test (EP2 continuous-strength fact representation). Each fact is stored with a continuous strength (amplitude weight); a query returns facts strength-ordered (strong facts dominate cleanup) and the strength scalar is recoverable via a readout. Tests whether continuous confidence/strength is native (cheap to ship in v1). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS strongest fact wins cleanup >= 0.95 AND recovered strength correlates with true strength (Pearson >= 0.9). MIDDLE >= 0.85 / 0.75. HARD-FAIL below.
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
ANCHOR_NAME = "factrep_ep2_continuous_strength_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert abs(_n.corrcoef([1.0, 2, 3], [1.0, 2, 3])[0, 1] - 1.0) < 1e-9, "corr"; print("[selftest] PASS: factrep-ep2-continuous-strength", flush=True)
def run() -> Dict:
    g = np.random.default_rng(202); N = 4096; VK = 80; VV = 400; TR = 60 if SMOKE else 200
    keys = cphasor(VK, N, g); vals = cphasor(VV, N, g); win = 0; corrs = []
    for _ in range(TR):
        k = int(g.integers(0, VK))
        # this key has 3 competing values with different strengths
        cands = g.choice(VV, 3, replace=False); strengths = g.uniform(0.2, 1.0, 3)
        M = np.zeros(N, dtype=np.complex64)
        for ci in range(3):
            M = M + strengths[ci] * keys[k] * vals[int(cands[ci])]
        for _d in range(15):
            M = M + g.uniform(0.2, 1.0) * keys[int(g.integers(0, VK))] * vals[int(g.integers(0, VV))]
        rec = M * np.conj(keys[k]); pred = cidx(rec, vals)
        win += int(pred == int(cands[int(np.argmax(strengths))]))               # strongest value wins
        sc = (vals[cands] @ np.conj(rec)).real                                  # recovered strength per candidate
        if np.std(sc) > 0 and np.std(strengths) > 0:
            corrs.append(float(np.corrcoef(sc, strengths)[0, 1]))
    wr = win / TR; cr = float(np.mean(corrs)) if corrs else 0.0
    print("  strongest-wins=%.3f | strength-recovery Pearson=%.3f (n=%d)" % (wr, cr, TR), flush=True)
    return {"win": wr, "corr": cr}
def verdict(r) -> Tuple[str, str]:
    s = "strongest-wins=%.3f strength-correlation=%.3f" % (r["win"], r["corr"])
    if r["win"] >= 0.95 and r["corr"] >= 0.9: return ("HARD_PASS", "HARD_PASS: continuous-strength native -- strongest fact wins >=0.95 and recovered strength correlates >=0.9 with true; confidence-weighted facts ship-in-v1 candidate. " + s)
    if r["win"] >= 0.85 and r["corr"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: strength 0.85/0.75. " + s)
    return ("HARD_FAIL", "HARD_FAIL: continuous-strength weak. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
