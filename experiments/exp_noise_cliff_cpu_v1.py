"""
exp_noise_cliff_cpu_v1.py -- sign-key recall@1 across bit-flip rates (graceful-degradation cliff) -- CPU.

ROUTING: CPU substrate-physics characterization (recall vs bit-flip sweep). Sweep query corruption (bit-flip rate 0.1..0.4) at N=20000 D=512; find where recall@1 falls off. Characterizes robustness to query corruption. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS recall@1 >= 0.95 at 0.30 bit-flip. MIDDLE 0.80-0.95. HARD-FAIL < 0.80.
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
ANCHOR_NAME = "noise_cliff_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    assert np.sign(0.3) == 1, "sign"; assert np.sign(-0.2) == -1, "sign-"; print("[selftest] PASS: noise-cliff-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(1); N = 5000 if SMOKE else 20000; D = 512; NQ = 300; by = {}
    X = np.sign(g.standard_normal((N, D))).astype(np.float32); X[X == 0] = 1; qi = g.choice(N, NQ, replace=False)
    for flip in [0.1, 0.2, 0.3, 0.4]:
        Q = X[qi].copy(); fl = g.random((NQ, D)) < flip; Q[fl] *= -1
        pred = np.argmax(Q @ X.T, axis=1); by["f%.1f" % flip] = float((pred == qi).mean())
    print("  recall by flip: %s (N=%d D=%d)" % ({k: round(v, 3) for k, v in by.items()}, N, D), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    f3 = r["by"].get("f0.3", 0.0); s = "recall by flip: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if f3 >= 0.95: return ("HARD_PASS", "HARD_PASS: recall>=0.95 even at 0.30 bit-flip -- robust to heavy query corruption. " + s)
    if f3 >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.80-0.95 at 0.30 flip. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.80 at 0.30 flip. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
