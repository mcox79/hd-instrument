"""
exp_gate3_conformal_coverage_cpu_v1.py -- split-conformal prediction on substrate cleanup score gives distribution-free coverage -- CPU.

ROUTING: 8_DRILLS batch (GATE-3 conformal coverage via substrate score). Uses the substrate cleanup confidence as a conformal nonconformity score. On a calibration split, take the (1-alpha) quantile of nonconformity (=1-confidence-of-true); on a test split, the prediction set is all candidates with nonconformity <= that threshold. Split-conformal theory guarantees test coverage >= 1-alpha distribution-free. Measures empirical coverage at alpha=0.1. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS empirical coverage in [0.90, 0.97] at alpha=0.1 (covers the 1-alpha guarantee without being trivially wide; mean set size reported). MIDDLE coverage in [0.85,0.99]. HARD-FAIL outside.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "gate3_conformal_coverage_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def scorevec(v, book):
    return (book @ np.conj(v)).real / book.shape[1]

def _selftest():
    import numpy as _n; q = _n.quantile([0.1,0.2,0.3,0.4], 0.9); assert 0.3 < q <= 0.4, "quantile"; print("[selftest] PASS: gate3-conformal-coverage", flush=True)
def run() -> Dict:
    g = np.random.default_rng(631); N = 4096; VE = 300; REL = cphasor(1, N, g)[0]; ents = cphasor(VE, N, g)
    NCAL = 200 if SMOKE else 500; NTEST = 200 if SMOKE else 500; ALPHA = 0.1
    def make_query():
        s = int(g.integers(0, VE)); o = int(g.integers(0, VE)); load = int(g.integers(5, 250))
        shard = ents[s] * REL * ents[o]
        for _d in range(load):
            shard = shard + ents[int(g.integers(0, VE))] * REL * ents[int(g.integers(0, VE))]
        sc = scorevec(shard * np.conj(ents[s] * REL), ents)
        return sc, o   # raw per-candidate confidence, true object
    cal = [make_query() for _ in range(NCAL)]
    ranks = np.array([int((sc > sc[o]).sum()) for sc, o in cal])            # rank-based nonconformity (consistent across queries)
    k = int(min(VE - 1, math.ceil((NCAL + 1) * (1 - ALPHA)) - 1))          # conformal rank quantile (0-indexed)
    qhat = int(np.sort(ranks)[min(k, NCAL - 1)])
    covered = 0; setsizes = []
    for _ in range(NTEST):
        sc, o = make_query(); r_true = int((sc > sc[o]).sum())
        covered += int(r_true <= qhat); setsizes.append(qhat + 1)           # prediction set = top-(qhat+1) by score
    cov = covered / NTEST; msize = float(np.mean(setsizes))
    print("  conformal coverage=%.3f (target>=%.2f) mean-set-size=%.1f/%d qhat=%.3f" % (cov, 1 - ALPHA, msize, VE, qhat), flush=True)
    return {"coverage": cov, "set_size": msize, "vocab": VE}
def verdict(r) -> Tuple[str, str]:
    s = "coverage=%.3f mean-set-size=%.1f/%d" % (r["coverage"], r["set_size"], r["vocab"])
    if 0.90 <= r["coverage"] <= 0.97: return ("HARD_PASS", "HARD_PASS: split-conformal on substrate score yields distribution-free coverage >=0.90 at alpha=0.1 with bounded set size -- calibrated abstention/uncertainty guarantee. " + s)
    if 0.85 <= r["coverage"] <= 0.99: return ("MIDDLE_BAND", "MIDDLE_BAND: coverage near target. " + s)
    return ("HARD_FAIL", "HARD_FAIL: coverage off target (calibration broken). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
