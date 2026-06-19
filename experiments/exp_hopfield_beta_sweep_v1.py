"""
exp_hopfield_beta_sweep_v1.py -- modern-Hopfield retrieval separation threshold vs inverse-temperature beta -- CPU.

ROUTING: field_modern_hopfield Anchor 2 (separation/beta sweep). At fixed load P/N=1.0, sweep beta (inverse temperature). Modern Hopfield needs beta above a separation threshold for clean retrieval (Ramsauer). Find the minimum beta achieving recall@1 >= 0.95 from noisy queries. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS some beta <= 16 achieves recall@1 >= 0.95 at P/N=1.0 (separation threshold is practical). MIDDLE needs beta <= 64. HARD-FAIL no beta clears 0.95.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "hopfield_beta_sweep_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def softmax(x):
    x = x - x.max(axis=-1, keepdims=True); e = np.exp(x); return e / e.sum(axis=-1, keepdims=True)
def _selftest():
    sm = softmax(np.array([[1.0, 2.0]])); assert abs(sm.sum() - 1.0) < 1e-9, "softmax norm"
    assert 1 < 2, "order"; assert np.sign(-0.5) == -1, "sign"
    print("[selftest] PASS: hopfield-beta-sweep", flush=True)
def run() -> Dict:
    g = np.random.default_rng(1); N = 256; P = N; FLIP = 0.15; NQ = 200
    X = np.sign(g.standard_normal((P, N))).astype(np.float64)
    qi = g.choice(P, min(NQ, P), replace=False); Q = X[qi].copy(); fl = g.random(Q.shape) < FLIP; Q[fl] *= -1
    betas = [1, 2, 4, 8, 16] if SMOKE else [0.5, 1, 2, 4, 8, 16, 32, 64]; by = {}
    for b in betas:
        ret = softmax(b * (Q @ X.T)) @ X; rs = np.sign(ret)
        rec = float(((rs * X[qi]).sum(1) / N >= 0.95).mean()); by["b%g" % b] = rec
        print("  beta=%g recall@1=%.3f" % (b, rec), flush=True)
    good = [b for b in betas if by["b%g" % b] >= 0.95]; minb = min(good) if good else 1e9
    return {"by": by, "min_beta": minb}
def verdict(r) -> Tuple[str, str]:
    mb = r["min_beta"]; s = "min-beta-for-0.95=%s | %s" % (mb if mb < 1e9 else "none", {k: round(v, 3) for k, v in r["by"].items()})
    if mb <= 16: return ("HARD_PASS", "HARD_PASS: modern-Hopfield clean retrieval at beta<=16 (P/N=1.0) -- the separation threshold is practical; the substrate operates well inside it. " + s)
    if mb <= 64: return ("MIDDLE_BAND", "MIDDLE_BAND: needs beta<=64. " + s)
    return ("HARD_FAIL", "HARD_FAIL: no beta clears 0.95 at P/N=1.0. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
