"""
exp_substrate_capacity_sweep_n32768_asymptotic_alpha_v1 -- confirm alpha=0.040 asymptote at large N (Phase 3 gate) -- CPU.

ROUTING: research two_regime_alpha drill (Cell 2, Tier-1 gate). Capacity scaling showed two-regime alpha (0.060 small N
  -> 0.040 large N). This cell measures alpha = M*/N at N in {8192, 16384, 32768} to confirm the 0.040 asymptote
  (or detect further drift to 0.030-0.035) BEFORE committing the Phase 3 N=65536 blueprint. Uses W-FREE Hopfield
  (P-based matmuls; never materializes the N x N weight matrix) so N=32768 stays in RAM. CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS alpha at N=32768 in [0.038, 0.045] (0.040 asymptote confirmed; Phase 3 commit OK).
  MIDDLE: alpha in [0.030, 0.038) (further drift; revise blueprint down). HARD-FAIL: alpha < 0.030 or > 0.050 (model wrong).
FORMULA SELF-TESTS (PROT-022): 1. W-free update == explicit W (small N). 2. recovery at low load. 3. recall drops at overload.
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

ANCHOR_NAME = "substrate_capacity_sweep_n32768_asymptotic_alpha_v1"
FLIP = 0.15; STEPS = 4
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_GRID = [2048, 4096]; LOADS = [0.03, 0.04, 0.05, 0.06, 0.08]
else:
    SEEDS = [7, 17, 23]; N_GRID = [8192, 16384, 32768]; LOADS = [0.030, 0.035, 0.040, 0.045, 0.050, 0.055, 0.060]


def recall_wfree(n, M, g):
    # auto-associative Hopfield, W = sum p p^T zero-diagonal, but computed via P (M x n) matmuls (no N x N W).
    # W @ s = P^T (P s) - M s  (diag of P^T P is M for +/-1 patterns). Update s <- sign(W s).
    P = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    S = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)            # flip-corrupted cues (M x n)
    for _ in range(STEPS):
        A = P @ S.T                                                 # (M_pat, M_cue): p_k . cue_m
        WS = (P.T @ A).T - M * S                                    # (M_cue, n): sum_k p_k (p_k.cue_m) - M cue_m
        S = np.sign(WS).astype(np.float32); S[S == 0] = 1.0
    return float(np.mean(np.all(S == P, axis=1)))


def _selftest():
    g = np.random.default_rng(0); n = 256; M = 8
    P = (np.random.default_rng(1).integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)
    W = (P.T @ P).astype(np.float32); np.fill_diagonal(W, 0.0)
    s = P[3].copy(); wfree = (P.T @ (P @ s)) - M * s               # W-free for one pattern (zero-diag via -M)
    assert np.allclose(np.sign(wfree), np.sign(W @ s)), "W-free update == explicit W"
    assert recall_wfree(512, 8, np.random.default_rng(2)) >= 0.95, "recovery at low load"
    assert recall_wfree(256, 200, np.random.default_rng(3)) < 0.95, "recall drops at overload"
    print("[selftest] PASS: wfree lowload overload", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def capacity(n, seed):
    cap = 0
    for load in LOADS:
        M = max(2, int(load * n))
        if recall_wfree(n, M, np.random.default_rng(seed * 1000 + M)) >= 0.95:
            cap = M
        else:
            break
    return cap


def run_seed(seed) -> Dict:
    caps = {}; alphas = {}
    for n in N_GRID:
        c = capacity(n, seed); caps[str(n)] = c; alphas[str(n)] = c / n
    return {"seed": seed, "capacity_by_N": caps, "alpha_by_N": alphas, "alpha_largest": caps[str(N_GRID[-1])] / N_GRID[-1]}


def verdict(ps) -> Tuple[str, str]:
    nmax = str(N_GRID[-1]); a = float(np.mean([p["alpha_by_N"][nmax] for p in ps]))
    parts = " ".join("N%s:alpha=%.4f" % (n, np.mean([p["alpha_by_N"][str(n)] for p in ps])) for n in N_GRID)
    summary = "alpha@N=%s = %.4f | %s" % (nmax, a, parts)
    if 0.038 <= a <= 0.045:
        return ("HARD_PASS", "HARD_PASS: alpha=0.040 asymptote confirmed at N=%s (in [0.038,0.045]) -- Phase 3 N=65536 commit OK. " % nmax + summary)
    if 0.030 <= a < 0.038:
        return ("MIDDLE_BAND", "MIDDLE_BAND: alpha drifts further below 0.040 -- revise Phase 3 blueprint down. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: alpha@N=%s outside model (<0.030 or >0.050). " % nmax + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s loads=%d flip=%.2f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, len(LOADS), FLIP), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] alpha_by_N=%s" % (seed, {k: round(v, 4) for k, v in r["alpha_by_N"].items()}), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
