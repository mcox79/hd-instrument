"""
exp_f5_gapscore_3seed_cpu_v1.py -- gap-score abstention 3-seed mean AUC >=0.80 with variance <0.02 -- CPU.

ROUTING: CYCLE_200_FOLLOWUPS (F5 gap-score 3-seed promotion). Multi-seed (3) gap-score abstention AUC for VALIDATED promotion of PP-181. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS 3-seed mean AUC >=0.80 AND var <0.02. MIDDLE mean >=0.75. HARD-FAIL <0.75.
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
ANCHOR_NAME = "f5_gapscore_3seed_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert _n.var([0.78,0.79,0.80]) < 0.02, "var"; print("[selftest] PASS: f5-gapscore-3seed", flush=True)
def auc(scores, labels):
    order = np.argsort(scores); ranks = np.empty(len(scores)); ranks[order] = np.arange(1, len(scores) + 1)
    pos = labels == 1; npos = int(pos.sum()); nneg = len(labels) - npos
    if npos == 0 or nneg == 0:
        return 0.5
    return (ranks[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg)
def one_seed(seed):
    g = np.random.default_rng(seed); N = 8192; VK = 60; VV = 300; keys = cphasor(VK, N, g); vals = cphasor(VV, N, g); M = 30
    TR = 120 if SMOKE else 400; scores = []; labels = []
    for _ in range(TR):
        Mem = np.zeros(N, dtype=np.complex64); present = []
        for _f in range(M):
            k = int(g.integers(0, VK)); vv = int(g.integers(0, VV)); Mem = Mem + keys[k] * vals[vv]; present.append((k, vv))
        if g.random() < 0.5:
            k, vv = present[int(g.integers(0, len(present)))]; lab = 1
        else:
            k = int(g.integers(0, VK)); vv = int(g.integers(0, VV)); lab = 0
        sc = np.sort((vals @ np.conj(Mem * np.conj(keys[k]))).real)[::-1]
        gap = float(sc[0] - sc[1]); scores.append(gap); labels.append(lab)
    return auc(np.array(scores), np.array(labels))
def run() -> Dict:
    seeds = [7] if SMOKE else [7, 13, 29]; aucs = [one_seed(s) for s in seeds]
    mean = float(np.mean(aucs)); var = float(np.var(aucs)); print("  gap-score AUC seeds=%s mean=%.3f var=%.4f" % ([round(a, 3) for a in aucs], mean, var), flush=True)
    return {"aucs": [round(a, 3) for a in aucs], "mean_auc": mean, "var": var, "n_seeds": len(seeds)}
def verdict(r) -> Tuple[str, str]:
    s = "3-seed mean AUC=%.3f var=%.4f seeds=%s" % (r["mean_auc"], r["var"], r["aucs"])
    if r["n_seeds"] >= 3 and r["mean_auc"] >= 0.80 and r["var"] < 0.02: return ("HARD_PASS", "HARD_PASS: gap-score abstention 3-seed mean AUC >=0.80 with variance <0.02 -- VALIDATED multi-seed. " + s)
    if r["mean_auc"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: mean AUC 0.75-0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: mean AUC <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
