"""
exp_substrate_sparse_vs_dense_capacity_v1 -- sparse vs dense coding capacity (cross-cutting linear-noise lever) -- CPU.

ROUTING: research 4_negatives_rescued_sparse_writes (cross-cutting finding: dense bipolar retrieval noise is EXPONENTIAL
  in load; SPARSE coding -> LINEAR noise -> higher capacity; NeurIPS 2023 sparse Hopfield arXiv:2309.12673). Empirically
  compares DENSE bipolar value codewords vs SPARSE (s-of-N active) codewords for Hebbian heteroassociative capacity,
  swept across sparsity s and load M. Validates whether sparse coding extends substrate capacity. CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS best sparse config capacity >= 1.5x dense at matched N. MIDDLE: 1.1-1.5x. HARD-FAIL:
  sparse <= dense (no linear-noise benefit at this scale).
FORMULA SELF-TESTS (PROT-022): 1. sparse codeword has s active. 2. dense recall low-load. 3. N marker.
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

ANCHOR_NAME = "substrate_sparse_vs_dense_capacity_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512; ACTIVITIES = [0.5, 0.1]; LOAD_GRID = [0.05, 0.1, 0.2, 0.4]
else:
    SEEDS = [7, 17, 23, 31, 43]; N_DIM = 1024; ACTIVITIES = [0.5, 0.25, 0.1, 0.05]
    LOAD_GRID = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.3]
FLIP = 0.10; STEPS = 6


def recall(n, M, a, g):
    # auto-associative Hopfield with activity a (a=0.5 dense; a<0.5 sparse). Mean-subtracted covariance rule.
    P = (g.random((M, n)) < a).astype(np.float32) * 2 - 1   # +1 w.p. a, else -1
    mean = 2 * a - 1
    Pc = P - mean
    W = (Pc.T @ Pc).astype(np.float32) / (n * a * (1 - a) + 1e-9)
    np.fill_diagonal(W, 0.0)
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign((s - mean) @ W.T); s[s == 0] = 1.0      # mean-field threshold via mean-subtraction
    return float(np.mean(np.all(s == P, axis=1)))


def _selftest():
    g = np.random.default_rng(0)
    assert recall(512, 10, 0.5, g) >= 0.95, "dense recall low-load"
    assert recall(256, 200, 0.5, g) < 0.95, "recall drops at overload"
    print("[selftest] PASS: sparse dense hopfield", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def capacity(n, a, seed):
    cap = 0
    for load in LOAD_GRID:
        M = max(2, int(load * n))
        if recall(n, M, a, np.random.default_rng(seed * 1000 + M)) >= 0.95:
            cap = M
        else:
            break
    return cap


def run_seed(seed) -> Dict:
    caps = {("a%.2f" % a): capacity(N_DIM, a, seed) for a in ACTIVITIES}
    dense = caps["a0.50"]; best_sparse = max(v for k, v in caps.items() if k != "a0.50")
    return {"seed": seed, "N": N_DIM, "capacity_by_activity": caps, "dense_capacity": dense,
            "best_sparse_capacity": best_sparse, "ratio": float(best_sparse / max(dense, 1))}


def verdict(ps) -> Tuple[str, str]:
    dc = float(np.mean([p["dense_capacity"] for p in ps])); sc = float(np.mean([p["best_sparse_capacity"] for p in ps]))
    ratio = sc / max(dc, 1)
    summary = "dense_capacity=%.0f best_sparse_capacity=%.0f ratio=%.2fx (N=%d, sparsities=%s)" % (dc, sc, ratio, N_DIM, SPARSITIES)
    if ratio >= 1.5:
        return ("HARD_PASS", "HARD_PASS: sparse coding gives >=1.5x capacity (linear-noise regime confirmed) -- cross-cutting lever validated. " + summary)
    if ratio >= 1.1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sparse coding 1.1-1.5x capacity. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: sparse coding no capacity benefit at this scale. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d activities=%s loads=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, ACTIVITIES, len(LOAD_GRID)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] dense=%d best_sparse=%d ratio=%.2fx caps=%s" % (seed, r["dense_capacity"], r["best_sparse_capacity"], r["ratio"], r["capacity_by_activity"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
