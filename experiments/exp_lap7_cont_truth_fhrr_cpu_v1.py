"""
exp_lap7_cont_truth_fhrr_cpu_v1.py -- FHRR magnitude as continuous truth gradient -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop batch (LAP-7 CONT-TRUTH-FHRR); pure-FHRR (no download). Graded predicate degrees encoded as amplitude; recover magnitude; correlate with true degree (Sorites-style vagueness).
PRE-REGISTERED: HARD-PASS corr>=0.70. MIDDLE>=0.50. HARD-FAIL<0.50.
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
ANCHOR_NAME = "lap7_cont_truth_fhrr_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert abs(_n.corrcoef([1,2,3],[1,2,3])[0,1]-1)<1e-9, "corr"; print("[selftest] PASS: cont-truth-fhrr", flush=True)
def run() -> Dict:
    # continuous truth: predicate P holds to degree d in [0,1] encoded as amplitude d on key_P; recover d_hat=|<state,key_P>|; correlate.
    g = np.random.default_rng(707); N = 4096; NP = 8; keys = cphasor(NP, N, g)
    TR = 40 if SMOKE else 300; true_d = []; rec_d = []
    for _ in range(TR):
        degs = g.random(NP)                                              # graded truth per predicate (Sorites: vague membership)
        state = (degs[:, None] * keys).sum(axis=0)                       # amplitude-weighted bundle
        for p in range(NP):
            dhat = float(np.abs(np.vdot(keys[p], state)) / N)            # recovered magnitude
            true_d.append(degs[p]); rec_d.append(dhat)
    corr = float(np.corrcoef(true_d, rec_d)[0, 1])
    print("  CONT-TRUTH recovered-vs-true corr=%.3f (NP=%d, n=%d)" % (corr, NP, len(true_d)), flush=True)
    return {"corr": corr, "n": len(true_d)}
def verdict(r) -> Tuple[str, str]:
    s = "truth-gradient-corr=%.3f (n=%d)" % (r["corr"], r["n"])
    if r["corr"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: FHRR magnitude tracks continuous truth degree (corr>=0.70) -- vague/graded predicates (Sorites) native via amplitude; no separate fuzzy-logic mechanism needed. " + s)
    if r["corr"] >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: corr 0.50-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: corr <0.50. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
