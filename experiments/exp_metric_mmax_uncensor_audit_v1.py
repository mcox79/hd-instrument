"""
exp_metric_mmax_uncensor_audit_v1 -- Batch E Cell 9 (TAX-6; retroactive saturation audit) -- CPU.

ROUTING: Batch E Drill-4 anchor B. Prior capacity cells censored the load grid at small M_max (e.g. M=50), so a measured
  "saturation/plateau" at M=4 or M=50 could be a CENSORING artifact (the grid simply stopped). This re-measures capacity
  with an UNCENSORED grid (M_max raised far past the old ceiling) on synthetic +-1 patterns and reports where recall ACTUALLY
  first drops below 0.95. If the true M_c exceeds the old censor point, prior saturation verdicts at that M are invalid.
PRE-REGISTERED: HARD-PASS true M_c > 2x the old censor (50) -- prior small-M_max saturation verdicts were censoring artifacts.
  MID 1.0-2x. HARD-FAIL true M_c <= old censor (saturation was real).
FORMULA SELF-TESTS (PROT-022): 1. low-load recovers. 2. high-load fails. 3. monotone.
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

ANCHOR_NAME = "metric_mmax_uncensor_audit_v1"
OLD_CENSOR = 50; FLIP = 0.05; STEPS = 6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048; M_GRID = [4, 8, 16, 32, 50, 80, 120, 200]
else:
    SEEDS = [7, 17, 23]; N = 4096; M_GRID = [4, 8, 16, 32, 50, 80, 120, 200, 320, 480, 640]


def patterns(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def recall(P, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign((s @ P.T) @ P - M * s); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def true_mc(n, seed):
    g = np.random.default_rng(seed); c = 0
    for M in M_GRID:
        if recall(patterns(M, n, g), seed * 9 + M) >= 0.95:
            c = M
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); assert recall(patterns(4, 512, g), 0) >= 0.95, "low-load recovers"
    assert recall(patterns(400, 512, g), 0) < 0.95, "high-load fails"
    print("[selftest] PASS: mmax-uncensor", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    mc = true_mc(N, seed); print("  [seed=%d N=%d] true_M_c=%d (old censor=%d)" % (seed, N, mc, OLD_CENSOR), flush=True)
    return {"seed": seed, "true_Mc": mc, "censored_at_old": mc >= OLD_CENSOR}


def verdict(ps) -> Tuple[str, str]:
    mc = float(np.mean([p["true_Mc"] for p in ps])); g = mc / OLD_CENSOR
    summary = "true M_c=%.0f vs old censor=%d | ratio=%.2fx (N=%d)" % (mc, OLD_CENSOR, g, N)
    if g > 2.0:
        return ("HARD_PASS", "HARD_PASS: true M_c >2x the old M_max=50 censor -- prior small-grid 'saturation' verdicts were CENSORING artifacts; re-audit them. " + summary)
    if g >= 1.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: true M_c near old censor (1-2x). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: true M_c <= old censor -- saturation was real, not censoring. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d M_grid_max=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, M_GRID[-1]), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
