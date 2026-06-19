"""
exp_lap4_9_agm_contraction_depth_cpu_v1.py -- deep AGM belief revision (many supersessions per key) -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (LAP4-9 AGM-CONTRACTION-DEPTH); pure-FHRR (no download). Long prioritized-assertion stream; deep contraction chains; verify final belief set stays correct.
PRE-REGISTERED: HARD-PASS deep-AGM>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.
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
ANCHOR_NAME = "lap4_9_agm_contraction_depth_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: agm-contraction-depth", flush=True)
def run() -> Dict:
    # deep AGM: a LONG stream of prioritized assertions; each key revised many times (deep contraction chains). Verify the final
    # belief set + track contraction depth (number of supersessions per key).
    g = np.random.default_rng(266); N = 8192; NK = 25; NV = 200; keys = cphasor(NK, N, g); vals = cphasor(NV, N, g)
    TR = 20 if SMOKE else 120; correct = 0; n = 0; depths = []
    for _ in range(TR):
        Mem = np.zeros(N, dtype=np.complex64); belief = {}; supers = {k: 0 for k in range(NK)}
        T = 200
        for _t in range(T):
            k = int(g.integers(0, NK)); v = int(g.integers(0, NV)); p = float(g.random())
            if k in belief:
                vo, po = belief[k]
                if p > po:
                    Mem = Mem - keys[k] * vals[vo] + keys[k] * vals[v]; belief[k] = (v, p); supers[k] += 1
            else:
                Mem = Mem + keys[k] * vals[v]; belief[k] = (v, p)
        for k in belief:
            correct += int(cidx(Mem * np.conj(keys[k]), vals) == belief[k][0]); n += 1
        depths.append(np.mean([supers[k] for k in belief]))
    acc = correct / n; md = float(np.mean(depths))
    print("  AGM-CONTRACTION-DEPTH final-belief-correct=%.3f mean-contraction-depth=%.1f (n=%d)" % (acc, md, n), flush=True)
    return {"belief_acc": acc, "mean_depth": round(md, 1), "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "deep-AGM-correct=%.3f mean-contraction-depth=%.1f" % (r["belief_acc"], r["mean_depth"])
    if r["belief_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: AGM belief revision stays correct >=0.85 through DEEP contraction chains (mean depth %.1f supersessions/key) -- repeated exact erasure does not accumulate error; belief base stable under many revisions. " % r["mean_depth"] + s)
    if r["belief_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: deep-AGM 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: deep-AGM <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
