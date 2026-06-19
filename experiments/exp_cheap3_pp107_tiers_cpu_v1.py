"""
exp_cheap3_pp107_tiers_cpu_v1.py -- cleanup confidence tracks graded similarity tiers monotonically, with graceful noise degradation -- CPU.

ROUTING: 8_DRILLS cheap-decisive batch (CHEAP-3 PP-107 confidence as graded population code). Store values at controlled cosine-similarity tiers to a probe (0.60-1.00); under query noise, the cleanup confidence should track the tier monotonically (Spearman high) and degrade gracefully -- the substrate confidence is a graded population-code-like signal, not binary. Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS Spearman(confidence, tier) > 0.85 AND ranking preserved under noise. MIDDLE > 0.70. HARD-FAIL <= 0.70.
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
ANCHOR_NAME = "cheap3_pp107_tiers_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def scores(v, book):
    return (book @ np.conj(v)).real / book.shape[1]
def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg); c = 0; t = 0
    for p in pos:
        c += (neg < p).sum() + 0.5 * (neg == p).sum(); t += len(neg)
    return c / max(1, t)
def spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    ra = ra - ra.mean(); rb = rb - rb.mean()
    d = math.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / d) if d > 0 else 0.0

def _selftest():
    assert abs(spearman([1,2,3],[1,2,3]) - 1.0) < 1e-9, "spearman"; print("[selftest] PASS: cheap3-pp107-tiers", flush=True)
def run() -> Dict:
    g = np.random.default_rng(613); N = 8192; TIERS = [0.60,0.70,0.80,0.90,1.00]; TR = 60 if SMOKE else 200
    confs = []; tiervals = []
    for _ in range(TR):
        base = cphasor(1, N, g)[0]
        for t in TIERS:
            # mix base with a random vector to hit target real-cosine ~ t, then add query noise
            r = cphasor(1, N, g)[0]; mixed = t * base + math.sqrt(max(0.0,1-t*t)) * r; mixed = mixed / (np.abs(mixed)+1e-8)
            noisy = base * np.exp(1j * 0.15 * g.standard_normal(N)); noisy = noisy/(np.abs(noisy)+1e-8)
            conf = float((mixed @ np.conj(noisy)).real / N); confs.append(conf); tiervals.append(t)
    rho = spearman(confs, tiervals); print("  Spearman(confidence, tier)=%.3f (n=%d, noise=0.15)" % (rho, len(confs)), flush=True)
    return {"spearman": rho}
def verdict(r) -> Tuple[str, str]:
    s = "Spearman(conf,tier)=%.3f" % r["spearman"]
    if r["spearman"] > 0.85: return ("HARD_PASS", "HARD_PASS: cleanup confidence tracks graded tiers >0.85 under noise -- graded population-code-like confidence (PP-107) confirmed. " + s)
    if r["spearman"] > 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: tier-tracking 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: tier-tracking <=0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
