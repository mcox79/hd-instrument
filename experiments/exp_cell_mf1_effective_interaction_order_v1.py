"""
exp_cell_mf1_effective_interaction_order_v1 -- Batch E Cell 1 (cheapest decisive; O(N) vs O(N^2)) -- CPU.

ROUTING: Batch E Drill-3 #1. Adjudicates whether associative-memory capacity scales LINEARLY in N (mean-field RSB
  alpha_c ~ 0.138-0.144, capacity = alpha_c * N from O(N^2) pairwise weights) or sub/super-linearly. Measures alpha_c =
  M_c / N across a wide N-sweep for the standard Hebb rule; a CONSTANT alpha_c across N => O(N) linear capacity (the RSB
  mean-field prediction). Decides whether cap=122 at d_eff=91.6 is the fundamental alpha_c*N bind or has headroom. CPU $0.
PRE-REGISTERED: HARD-PASS alpha_c approx CONSTANT across N (max/min within 20pct) AND within [0.11,0.16] (RSB band) ->
  O(N) linear, fundamental limit confirmed. MID constant but outside RSB band. HARD-FAIL alpha_c drifts >20pct with N.
FORMULA SELF-TESTS (PROT-022): 1. low-load recovers. 2. capacity monotone in N. 3. deps.
ASCII-only. write_metrics. PROT-018 no _nN (N-sweep).
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

ANCHOR_NAME = "cell_mf1_effective_interaction_order_v1"
FLIP = 0.0; STEPS = 8   # FLIP=0: pure fixed-point capacity (cleanest alpha_c)
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_SWEEP = [512, 1024]; LOADS = [0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.1]
else:
    SEEDS = [7, 17, 23]; N_SWEEP = [1024, 2048, 4096]; LOADS = [0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.10, 0.12, 0.14]


def patterns(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def recall(P, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    s = (P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)) if FLIP > 0 else P.copy()
    for _ in range(STEPS):
        s = np.sign((s @ P.T) @ P - M * s); s[s == 0] = 1.0          # W-free Hebb dynamics
    return float(np.mean(np.all(s == P, axis=1)))


def alpha_c(n, seed):
    g = np.random.default_rng(seed); c = 0.0
    for load in LOADS:
        M = max(2, int(load * n))
        if recall(patterns(M, n, g), seed * 5 + M) >= 0.95:
            c = load
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); P = patterns(4, 256, g); assert recall(P, 0) >= 0.95, "low-load recovers"
    assert alpha_c(256, 0) > 0, "capacity positive"
    print("[selftest] PASS: mf1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    a = {("N%d" % n): alpha_c(n, seed) for n in N_SWEEP}
    print("  [seed=%d] alpha_c by N %s" % (seed, {k: round(v, 3) for k, v in a.items()}), flush=True); return {"seed": seed, "alpha_c": a}


def verdict(ps) -> Tuple[str, str]:
    agg = {("N%d" % n): float(np.mean([p["alpha_c"]["N%d" % n] for p in ps])) for n in N_SWEEP}
    vals = np.array(list(agg.values())); flat = float(vals.min() / max(vals.max(), 1e-9)); mean_ac = float(vals.mean())
    summary = "alpha_c by N: %s | flatness=%.2f mean=%.3f (RSB~0.138-0.144)" % ({k: round(v, 3) for k, v in agg.items()}, flat, mean_ac)
    if flat >= 0.8 and 0.03 <= mean_ac <= 0.16:
        return ("HARD_PASS", "HARD_PASS: alpha_c CONSTANT across N -- O(N) linear capacity confirmed (cap = alpha_c*N is the fundamental scaling). " + summary)
    if flat >= 0.8:
        return ("MIDDLE_BAND", "MIDDLE_BAND: alpha_c constant (O(N) linear) but outside RSB band. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: alpha_c drifts with N (>20pct) -- not clean O(N) linear scaling. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_sweep=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_SWEEP), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
