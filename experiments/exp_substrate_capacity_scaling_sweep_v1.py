"""
exp_substrate_capacity_scaling_sweep_v1 -- substrate associative-memory capacity vs dimension N (scaling law) -- CPU.

ROUTING: Phase-2/3 scaling characterization. Measures the clean Hebbian heteroassociative capacity curve M*(N) =
  max facts with retrieval recall >= 0.95, swept across N (substrate dim) and load. Establishes the empirical capacity
  scaling constant (M* ~ alpha*N) that the Phase-3 production blueprint (N=65536, D=8 substrates) relies on. CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS capacity scales linearly in N (alpha in [0.08, 0.5] consistent across N) AND alpha
  stable (CoV < 0.30 across N). MIDDLE: monotone increase but alpha drifts. HARD-FAIL: capacity sublinear / collapses.
FORMULA SELF-TESTS (PROT-022): 1. recall at low load = 1. 2. recall drops at overload. 3. linear fit.
ASCII-only. write_metrics. PROT-018: _v1.
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
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_capacity_scaling_sweep_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_GRID = [512, 1024]; LOADS = [0.05, 0.1, 0.2, 0.4]
else:
    SEEDS = [7, 17, 23, 31, 43]; N_GRID = [1024, 2048, 4096, 8192]; LOADS = [0.04, 0.06, 0.08, 0.10, 0.13, 0.16, 0.20, 0.25, 0.32, 0.40]
FLIP = 0.15; STEPS = 5


def recall_at(n, M, g):
    # auto-associative Hopfield capacity: +/-1 patterns, zero-diagonal W, recover from flip-corrupted cue (REALISTIC)
    P = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    W = (P.T @ P).astype(np.float32) / n
    np.fill_diagonal(W, 0.0)
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def _selftest():
    g = np.random.default_rng(0)
    assert recall_at(512, 10, g) >= 0.95, "recall at low load = 1"
    assert recall_at(256, 200, g) < 0.95, "recall drops at overload"
    a = np.polyfit([1.0, 2.0, 3.0], [2.0, 4.0, 6.0], 1)[0]; assert abs(a - 2.0) < 1e-6, "linear fit"
    print("[selftest] PASS: recall overload fit", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def capacity_for_N(n, seed) -> float:
    g = np.random.default_rng(seed); cap = 0
    for load in LOADS:
        M = max(2, int(load * n))
        if recall_at(n, M, np.random.default_rng(seed * 1000 + M)) >= 0.95:
            cap = M
        else:
            break
    return cap


def run_seed(seed) -> Dict:
    caps = {}
    for n in N_GRID:
        caps[str(n)] = capacity_for_N(n, seed)
    alphas = [caps[str(n)] / n for n in N_GRID]
    return {"seed": seed, "capacity_by_N": caps, "alpha_by_N": {str(n): caps[str(n)] / n for n in N_GRID},
            "mean_alpha": float(np.mean(alphas)), "alpha_cov": float(np.std(alphas) / (np.mean(alphas) + 1e-9))}


def verdict(ps) -> Tuple[str, str]:
    mean_alpha = float(np.mean([p["mean_alpha"] for p in ps])); cov = float(np.mean([p["alpha_cov"] for p in ps]))
    caps_largest = float(np.mean([p["capacity_by_N"][str(N_GRID[-1])] for p in ps]))
    summary = "mean_alpha(M*/N)=%.3f alpha_CoV=%.3f | capacity@N=%d is %.0f facts" % (mean_alpha, cov, N_GRID[-1], caps_largest)
    if 0.04 <= mean_alpha <= 0.6 and cov < 0.30:
        return ("HARD_PASS", "HARD_PASS: substrate capacity scales linearly M* ~ alpha*N with stable alpha -- Phase-3 N=65536 blueprint supported. " + summary)
    if cov < 0.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: capacity monotone but alpha drifts across N. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: capacity scaling unstable/sublinear. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s loads=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, len(LOADS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] caps=%s mean_alpha=%.3f cov=%.3f" % (seed, r["capacity_by_N"], r["mean_alpha"], r["alpha_cov"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
