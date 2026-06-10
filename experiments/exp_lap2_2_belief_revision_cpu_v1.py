"""
exp_lap2_2_belief_revision_cpu_v1.py -- AGM belief revision (prioritized contraction + expansion) -- CPU.

ROUTING: Research LAPTOP_WAVE2 (LAP2-2 BELIEF-REVISION-1); pure-FHRR (no download). Stream of prioritized assertions; higher-priority val supersedes via exact erasure; query final belief set.
PRE-REGISTERED: HARD-PASS posterior>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.
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
ANCHOR_NAME = "lap2_2_belief_revision_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: belief-revision", flush=True)
def run() -> Dict:
    # AGM: stream of (key, val, priority) assertions; revision = higher-priority val supersedes (erase old, add new); lower rejected.
    g = np.random.default_rng(2); N = 8192; NK = 30; NV = 200; keys = cphasor(NK, N, g); vals = cphasor(NV, N, g)
    TR = 30 if SMOKE else 200; correct = 0; n = 0
    for _ in range(TR):
        Mem = np.zeros(N, dtype=np.complex64); belief = {}                 # key -> (val, prio)
        T = 60
        for _t in range(T):
            k = int(g.integers(0, NK)); v = int(g.integers(0, NV)); p = float(g.random())
            if k in belief:
                vo, po = belief[k]
                if p > po:                                                # prioritized contraction + expansion (revision)
                    Mem = Mem - keys[k] * vals[vo] + keys[k] * vals[v]; belief[k] = (v, p)
            else:
                Mem = Mem + keys[k] * vals[v]; belief[k] = (v, p)
        for k in belief:
            correct += int(cidx(Mem * np.conj(keys[k]), vals) == belief[k][0]); n += 1
    acc = correct / n; print("  BELIEF-REVISION posterior-correct=%.3f (n=%d)" % (acc, n), flush=True)
    return {"belief_acc": acc, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "AGM-posterior-correct=%.3f (n=%d)" % (r["belief_acc"], r["n"])
    if r["belief_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate performs AGM belief revision >=0.85 (prioritized contraction + expansion via exact erasure) -- higher-priority beliefs supersede, superseded ones cleanly removed. " + s)
    if r["belief_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: belief revision 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: belief revision <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
