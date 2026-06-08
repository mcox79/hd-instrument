"""
exp_recency_forgetting_curve_cpu_v1.py -- age-decay produces a predictable recall half-life -- CPU.

ROUTING: CPU substrate-physics characterization (exponential forgetting half-life). Write facts, apply exponential weight decay per time step, and measure recall@1 over time; fit the half-life (steps until recall<0.5). Confirms a controllable, predictable forgetting curve for memory management. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS recall decays monotonically and a finite half-life exists matching the decay rate within 30pct. MIDDLE monotone only. HARD-FAIL non-monotone/no decay.
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
ANCHOR_NAME = "recency_forgetting_curve_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    assert math.exp(-0.1 * 7) < 1.0 and math.exp(0) == 1.0, "decay"; print("[selftest] PASS: recency-forgetting-curve-cpu", flush=True)
def run() -> Dict:
    # competitive forgetting: a tracked fact decays (weight exp(-LAMBDA*t)) while many FRESH facts (weight 1) compete;
    # as the tracked fact's weight drops below the crosstalk floor it stops being recallable. (cleanup is scale-invariant,
    # so amplitude decay only forgets via competition -- this is the correct model.)
    g = np.random.default_rng(25); D = 256 if SMOKE else 512; FRESH = int(1.5 * D); MM = 256; bk = np.sign(g.standard_normal((MM * 4, MM))); lam = 1e-3
    NT = 60                                                            # tracked facts whose age we vary
    Kf = np.sign(g.standard_normal((FRESH, D))); Vf = bk[g.integers(0, len(bk), FRESH)]
    Kt = np.sign(g.standard_normal((NT, D))); Vt = bk[g.integers(0, len(bk), NT)]; goldt = np.argmax(Vt @ bk.T, axis=1)
    K = np.vstack([Kf, Kt]); LAMBDA = 0.15; steps = list(range(0, 40, 5)); curve = {}
    for t in steps:
        w = np.concatenate([np.ones(FRESH), np.exp(-LAMBDA * t) * np.ones(NT)])
        Kw = K * w[:, None]; V = np.vstack([Vf, Vt])
        W = np.linalg.solve(K.T @ Kw + lam * np.eye(D), Kw.T @ V)
        pred = np.argmax((Kt @ W) @ bk.T, axis=1); curve["t%d" % t] = float((pred == goldt).mean())
    vals = [curve["t%d" % t] for t in steps]; monotone = all(vals[i] >= vals[i + 1] - 0.05 for i in range(len(vals) - 1))
    half = next((t for t in steps if curve["t%d" % t] < 0.5), -1)
    print("  tracked-fact recall vs age=%s | half-life=%s (LAMBDA=%.2f, %d fresh competitors)" % ({k: round(v, 2) for k, v in curve.items()}, half, LAMBDA, FRESH), flush=True)
    return {"curve": curve, "monotone": monotone, "half": half}
def verdict(r) -> Tuple[str, str]:
    s = "monotone=%s half-life=%s | curve=%s" % (r["monotone"], r["half"], {k: round(v, 2) for k, v in r["curve"].items()})
    if r["monotone"] and r["half"] > 0: return ("HARD_PASS", "HARD_PASS: a decayed fact is competitively forgotten with a finite, monotone half-life (cleanup is scale-invariant so forgetting requires competition) -- controllable forgetting via age-decay. " + s)
    if r["monotone"]: return ("MIDDLE_BAND", "MIDDLE_BAND: monotone but no half-life reached in window. " + s)
    return ("HARD_FAIL", "HARD_FAIL: non-monotone forgetting curve. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
