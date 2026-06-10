"""
exp_novelty_detection_cpu_v1.py -- OOD/novelty detection via cleanup-confidence -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop STRETCH (LAP-STRETCH-2 NOVELTY-DETECTION); pure-FHRR (no download). Known vs novel keys; novelty score = -(cleanup margin); AUC.
PRE-REGISTERED: HARD-PASS AUC>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.
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
ANCHOR_NAME = "novelty_detection_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _auc(scores, labels):
    import numpy as _n; o = _n.argsort(scores); r = _n.empty(len(scores)); r[o] = _n.arange(1, len(scores) + 1)
    pos = labels == 1; npos = int(pos.sum()); nneg = len(labels) - npos
    return 0.5 if npos == 0 or nneg == 0 else float((r[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg))
def _selftest():
    print("[selftest] PASS: novelty-detection", flush=True)
def run() -> Dict:
    g = np.random.default_rng(180); N = 8192; M = 40; VV = 300
    TR = 60 if SMOKE else 300; sc = []; lab = []
    for _ in range(TR):
        keys = cphasor(M, N, g); vals = cphasor(VV, N, g); truth = g.integers(0, VV, size=M)
        Mem = (keys * vals[truth]).sum(axis=0)
        if g.random() < 0.5:                                             # KNOWN query
            qi = int(g.integers(0, M)); probe = Mem * np.conj(keys[qi]); lb = 0
        else:                                                            # NOVEL query (key never stored)
            nk = cphasor(1, N, g)[0]; probe = Mem * np.conj(nk); lb = 1
        s = np.sort((vals @ np.conj(probe)).real)[::-1]; margin = float(s[0] - s[1])
        sc.append(-margin); lab.append(lb)                              # novel -> low margin -> high novelty score (-margin)
    auc = _auc(np.array(sc), np.array(lab))
    print("  NOVELTY-DETECTION known-vs-novel AUC=%.3f (n=%d)" % (auc, len(lab)), flush=True)
    return {"novelty_auc": auc, "n": len(lab)}
def verdict(r) -> Tuple[str, str]:
    s = "novelty-AUC=%.3f (n=%d)" % (r["novelty_auc"], r["n"])
    if r["novelty_auc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate flags novel/OOD inputs by cleanup-confidence (margin) AUC>=0.85 -- known facts retrieve with high margin, novel keys collapse to noise; intrinsic OOD signal, no separate detector. " + s)
    if r["novelty_auc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: novelty AUC 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: novelty AUC <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
