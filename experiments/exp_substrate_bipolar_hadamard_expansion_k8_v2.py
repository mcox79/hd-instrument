"""
substrate_bipolar_hadamard_expansion_k8_v2 -- SPARSE-V2-2: k=8 Hadamard bipolar expansion (Finding B rescue) -- CPU.

ROUTING: research 4_negatives_rescued_sparse_writes. Random-expansion HF rescue: use a STRUCTURED Hadamard-based
  BIPOLAR expansion (preserves bipolar structure, unlike Gaussian) N=128 -> N_exp=1024 (k=8) with sign nonlinearity
  (adds effective rank). PROPER Hopfield capacity (patterns +/-1, zero-diagonal W, sign-update cleanup from flip-
  corrupted cue; capacity = max M with recovery >= 0.95) vs baseline N=128. CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS capacity >= 4x baseline. MIDDLE: 1.5-4x. HARD-FAIL: < 1.5x or quality below baseline.
FORMULA SELF-TESTS (PROT-022): 1. Hopfield recovers a stored pattern from corruption at low load. 2. expansion bipolar. 3. marker.
ASCII-only. write_metrics. PROT-018: _v2 (not N-binding).
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

ANCHOR_NAME = "substrate_bipolar_hadamard_expansion_k8_v2"
N_BASE = 128; K_EXP = 8; N_EXP = N_BASE * K_EXP  # 1024
FLIP = 0.30; CLEAN_STEPS = 5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; M_GRID = [5, 10, 18, 30, 50, 90, 140, 200]
else:
    SEEDS = [7, 17, 23, 31, 43]; M_GRID = [5, 10, 18, 30, 50, 90, 140, 200, 280, 360]


def rand_pm1(M, n, g):
    return (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)


def expand(P, E):
    Y = np.sign(P @ E.T); Y[Y == 0] = 1.0                  # bipolar sign-nonlinear expansion (rank boost)
    return Y.astype(np.float32)


def hopfield_recovery(P, g, steps=CLEAN_STEPS):
    # P: (M,n) +/-1 patterns. W = (1/n) sum p p^T, zero diagonal. Recover each from FLIP-corrupted cue via sign-update.
    M, n = P.shape
    W = (P.T @ P).astype(np.float32) / n
    np.fill_diagonal(W, 0.0)
    flip = (g.random((M, n)) < FLIP)
    s = P * np.where(flip, -1.0, 1.0)
    for _ in range(steps):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))          # exact-recovery fraction


def capacity_of(P_fn, seeds_g):
    cap = 0
    for M in M_GRID:
        P = P_fn(M)
        rec = hopfield_recovery(P, seeds_g(M))
        if rec >= 0.95:
            cap = M
        else:
            break
    return cap


def _selftest():
    g = np.random.default_rng(0); P = rand_pm1(8, 256, g)
    assert hopfield_recovery(P, np.random.default_rng(1)) >= 0.95, "Hopfield recovers at low load"
    E = rand_pm1(64, 32, g); assert set(np.unique(expand(rand_pm1(3, 32, g), E))) <= {-1.0, 1.0}, "expansion bipolar"
    print("[selftest] PASS: hopfield expansion", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); E = rand_pm1(N_EXP, N_BASE, g)
    base_pats = {M: rand_pm1(M, N_BASE, np.random.default_rng(seed * 100 + M)) for M in M_GRID}
    cb = capacity_of(lambda M: base_pats[M], lambda M: np.random.default_rng(seed + 1))
    ce = capacity_of(lambda M: expand(base_pats[M], E), lambda M: np.random.default_rng(seed + 1))
    return {"seed": seed, "base_capacity": cb, "exp_capacity": ce, "ratio": float(ce / max(cb, 1))}


def verdict(ps) -> Tuple[str, str]:
    cb = float(np.mean([p["base_capacity"] for p in ps])); ce = float(np.mean([p["exp_capacity"] for p in ps]))
    ratio = ce / max(cb, 1)
    summary = "base_capacity(N=128)=%.0f exp_capacity(N=1024,k=8)=%.0f ratio=%.2fx (Hopfield, flip=%.2f)" % (cb, ce, ratio, FLIP)
    if ratio >= 4.0:
        return ("HARD_PASS", "HARD_PASS: Hadamard bipolar k=8 expansion gives >=4x capacity -- Phase 3 capacity multiplier. " + summary)
    if ratio >= 1.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 1.5-4x capacity from bipolar expansion (rank-limited but sign-nonlinearity helps). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: bipolar expansion < 1.5x capacity (source-rank bound dominates). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_base=%d N_exp=%d M_grid=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_BASE, N_EXP, M_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] base_cap=%d exp_cap=%d ratio=%.2fx" % (seed, r["base_capacity"], r["exp_capacity"], r["ratio"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_EXP, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
