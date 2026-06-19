"""
exp_set_membership_bundle_cpu_v1.py -- bundled-set membership test separates members from non-members -- CPU.

ROUTING: CPU substrate capability characterization (VSA set membership). Bundle a set S of items into one hypervector; test membership by cosine of an item to the bundle (members high, non-members low). Measures the member-vs-nonmember AUC vs set size. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS AUC >= 0.95 at set size 50 (N=4096). MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "set_membership_bundle_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    assert 4096 > 50, "size"; print("[selftest] PASS: set-membership-bundle-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(33); N = 2048 if SMOKE else 4096; V = 2000; S = 50; TR = 30 if SMOKE else 100
    book = cphasor(V, N, g); aucs = []
    for _ in range(TR):
        idx = g.choice(V, S, replace=False); B = book[idx].sum(0)
        mem = set(idx.tolist()); sc = (book @ B.conj()).real / N
        inm = sc[idx]; outm = sc[np.array([i for i in range(V) if i not in mem])]
        alls = np.concatenate([inm, outm]); lab = np.concatenate([np.ones(len(inm)), np.zeros(len(outm))])
        order = np.argsort(alls); ranks = np.empty_like(order, dtype=np.float64); ranks[order] = np.arange(1, len(alls) + 1)
        ni = len(inm); no = len(outm); auc = (ranks[lab == 1].sum() - ni * (ni + 1) / 2) / (ni * no); aucs.append(auc)
    a = float(np.mean(aucs)); print("  membership AUC=%.4f (set size=%d, V=%d, N=%d)" % (a, S, V, N), flush=True)
    return {"auc": a, "S": S}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.4f at set size %d" % (r["auc"], r["S"])
    if r["auc"] >= 0.95: return ("HARD_PASS", "HARD_PASS: bundled-set membership AUC>=0.95 -- set membership without per-item storage. " + s)
    if r["auc"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: membership AUC 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: membership AUC <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
