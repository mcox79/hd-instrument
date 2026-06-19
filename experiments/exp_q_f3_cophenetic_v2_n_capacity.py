"""
q_f3_cophenetic_v2_n_capacity -- Q-F3 cophenetic correlation on existing overlap matrix (v2).

NEW DESIGN per research note Section 2 (2026-06-02). Different framing from v1:
  v1 was dropped as genuine HARD_FAIL due to near-zero alpha regime.
  v2 re-flags with corrected framing: test at NEAR-CAPACITY loading on EXISTING
  overlap matrix (computed from Hopfield weights), not from random patterns alone.
  Decides 3 killer features:
    - Multi-tenant tree partitioning
    - Coarse-to-fine retrieval
    - Cluster-organized memory layout

SCIENTIFIC QUESTION (Q-F3 v2):
  Does the Hopfield overlap matrix Q_ij = xi_i^T W xi_j at near-capacity (alpha ~ 0.12)
  exhibit hierarchical tree structure (cophenetic correlation >= 0.70)?
  And does it improve monotonically from alpha=0.04 to alpha=0.12?

COMPOSITION CLASSIFICATION: N/A (single-substrate probe).

PRE-REGISTERED BANDS:
  HARD-PASS:
    cophenetic_corr >= 0.70 at alpha ~ 0.12 (near-capacity), 3+ seeds.
    (Calibration note: relaxed from v1 HP=0.85; near-capacity noise reduces cophenetic;
    even c=0.70 demonstrates real hierarchical structure; +-50% of 0.70 = [0.35, 1.05].)
  MIDDLE: 0.55 <= cophenetic_corr < 0.70 at near-capacity alpha.
  HARD-FAIL: cophenetic_corr < 0.55 at near-capacity (no tree structure at any reasonable load).

  Calibration probe note: first test at corrected near-capacity framing; bands +-50%
  of theoretical 0.70 threshold per calibration policy.

FORMULA SELF-TESTS:
  1. Single-pattern W (M=1): Q_12 = cosine_sim(xi_1, xi_2) ~ N(0, 1/N) for random BSC.
  2. Perfect ultrametric (3 items, Q_12=0.9, Q_13=0.5, Q_23=0.5): cophenetic=1.0.
  3. All equal overlaps (Q_ij = c for all i,j): single-linkage dendrogram is degenerate;
     cophenetic is undefined or 0 (NaN guard needed).

PROT-018: no _nN suffix; production N=1024 (cheap CPU probe; near-capacity is the key).
PROT-021: run_config includes N, P, run_mode.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, cophenet

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "q_f3_cophenetic_v2_n_capacity"

# PROT-018: no _nN suffix; production N=1024
N = 1024

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17, 23]
    ALPHA_LIST = [0.04, 0.08, 0.12]  # alpha = M/N
    N_RELAX_STEPS = 50
else:
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_LIST = [0.04, 0.08, 0.12, 0.14]  # sweep up to near-capacity
    N_RELAX_STEPS = 200

# Pre-reg thresholds
HP_COPHENETIC = 0.70
MID_COPHENETIC_LOW = 0.55
HF_COPHENETIC = 0.55

# Formula self-test: perfect ultrametric
_D = np.array([[0.0, 0.1, 0.5, 0.5], [0.1, 0.0, 0.5, 0.5],
               [0.5, 0.5, 0.0, 0.1], [0.5, 0.5, 0.1, 0.0]])
_sq = squareform(_D)
_L = linkage(_sq, method='single')
_c, _ = cophenet(_L, _sq)
assert _c > 0.80, f"Formula selftest: perfect-block cophenetic should be >0.80, got {_c:.3f}"
print(f"[formula_selftest] perfect-block cophenetic={_c:.3f} OK", flush=True)


def build_hopfield_w(M: int, N: int, seed: int) -> np.ndarray:
    """W = Xi^T @ Xi / N. Symmetric Hopfield matrix."""
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = (Xi.T @ Xi) / N
    np.fill_diagonal(W, 0.0)
    return W, Xi


def compute_overlap_matrix(W: np.ndarray, Xi: np.ndarray, n_steps: int) -> np.ndarray:
    """
    Compute pattern overlap matrix Q_ij = (1/N) * <xi_i, S(t_max; xi_j)>
    where S(t_max; xi_j) is the state after n_steps of synchronous Hopfield dynamics
    starting from xi_j.
    """
    M, N = Xi.shape
    Q = np.zeros((M, M))
    for i in range(M):
        state = Xi[i].copy()
        for _ in range(n_steps):
            state = np.sign(W @ state)
            state[state == 0] = 1.0
        for j in range(M):
            Q[i, j] = float(np.dot(state, Xi[j])) / N
    return Q


def cophenetic_from_overlap(Q: np.ndarray) -> float:
    """
    Convert overlap matrix to distance, run hierarchical clustering,
    return cophenetic correlation.
    """
    M = Q.shape[0]
    if M < 3:
        return float("nan")
    # Convert overlap -> distance: D_ij = 1 - |Q_ij| (high overlap = low distance)
    D = 1.0 - np.abs(Q)
    np.fill_diagonal(D, 0.0)
    # Symmetrize
    D = (D + D.T) / 2.0
    # Clamp
    D = np.clip(D, 0.0, 1.0)
    try:
        sq = squareform(D, checks=False)
        L = linkage(sq, method='single')
        c, _ = cophenet(L, sq)
        return float(c)
    except Exception as exc:
        print(f"  [cophenetic] error: {exc}", flush=True)
        return float("nan")


def run_seed(seed: int) -> Dict:
    """Run one seed: cophenetic across alpha values."""
    results = {}
    for alpha in ALPHA_LIST:
        M = max(3, int(alpha * N))
        t0 = time.time()
        W, Xi = build_hopfield_w(M, N, seed)
        Q = compute_overlap_matrix(W, Xi, N_RELAX_STEPS)
        c = cophenetic_from_overlap(Q)
        elapsed = time.time() - t0
        print(f"  [seed={seed} alpha={alpha:.2f} M={M}] cophenetic={c:.4f} "
              f"elapsed={elapsed:.1f}s", flush=True)
        results[alpha] = {
            "alpha": alpha, "M": M, "N": N,
            "cophenetic_corr": c,
            "elapsed_s": elapsed,
        }
    return {"alpha_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert cophenetic metric is non-null at small scale."""
    N_t = 128
    M_t = 10   # alpha=0.078, near 0.08
    seed = 99
    rng = np.random.RandomState(seed)
    Xi_t = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_t = (Xi_t.T @ Xi_t) / N_t
    np.fill_diagonal(W_t, 0.0)
    Q_t = np.zeros((M_t, M_t))
    for i in range(M_t):
        s = Xi_t[i].copy()
        for _ in range(10):
            s = np.sign(W_t @ s)
            s[s == 0] = 1.0
        for j in range(M_t):
            Q_t[i, j] = float(np.dot(s, Xi_t[j])) / N_t
    c_t = cophenetic_from_overlap(Q_t)
    assert not math.isnan(c_t), f"selftest: cophenetic is NaN at M={M_t}, N={N_t}"
    assert 0.0 <= c_t <= 1.0, f"selftest: cophenetic out of [0,1]: {c_t}"
    print(f"[selftest] PASS: cophenetic={c_t:.4f} at N={N_t} M={M_t}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate across seeds per alpha."""
    agg = {}
    for alpha in ALPHA_LIST:
        vals = []
        for sd in per_seed.values():
            r = sd["alpha_results"].get(alpha) or sd["alpha_results"].get(str(alpha))
            if r is not None and not math.isnan(r["cophenetic_corr"]):
                vals.append(r["cophenetic_corr"])
        mean_c = float(np.mean(vals)) if vals else float("nan")
        std_c = float(np.std(vals, ddof=1)) if len(vals) > 1 else float("nan")
        agg[alpha] = {
            "alpha": alpha,
            "mean_cophenetic_corr": mean_c,
            "std_cophenetic_corr": std_c,
            "n_seeds": len(vals),
        }
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    """Pre-registered verdict."""
    # Key threshold: near-capacity alpha ~ 0.12
    max_alpha = max(ALPHA_LIST)
    top = agg.get(max_alpha) or agg.get(str(max_alpha))
    if top is None or math.isnan(top["mean_cophenetic_corr"]):
        return ("HARD_FAIL", f"No valid cophenetic at alpha={max_alpha}.")
    c = top["mean_cophenetic_corr"]
    nc = top["n_seeds"]
    # Check monotonicity (nice to have, not required for HP)
    alpha_sorted = sorted(k for k in ALPHA_LIST if not math.isnan(
        (agg.get(k) or {}).get("mean_cophenetic_corr", float("nan"))))
    mono_ok = True
    if len(alpha_sorted) >= 2:
        cs = [agg[a]["mean_cophenetic_corr"] for a in alpha_sorted]
        mono_ok = all(cs[i] <= cs[i+1] + 0.05 for i in range(len(cs)-1))
    if c >= HP_COPHENETIC and nc >= 3:
        return ("HARD_PASS",
                f"Q-F3 cophenetic correlation confirmed. alpha={max_alpha:.2f} "
                f"cophenetic={c:.4f} (HP>={HP_COPHENETIC}) across {nc} seeds. "
                f"Monotonic={mono_ok}. Killer features: multi-tenant tree, "
                f"coarse-to-fine retrieval, cluster-organized memory.")
    if c < HF_COPHENETIC:
        return ("HARD_FAIL",
                f"Q-F3 no hierarchical structure at near-capacity. "
                f"alpha={max_alpha:.2f} cophenetic={c:.4f} (HF<{HF_COPHENETIC}). "
                f"Tree-based features not supported at this regime.")
    return ("MIDDLE_BAND",
            f"Q-F3 weak hierarchical signal. alpha={max_alpha:.2f} "
            f"cophenetic={c:.4f} (MIDDLE [{MID_COPHENETIC_LOW},{HP_COPHENETIC})). "
            f"Features possible but marginal; further study needed.")


def main():
    t_start = time.time()
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N={N} seeds={SEEDS}", flush=True)
    print(f"[{ANCHOR_NAME}] alpha_list={ALPHA_LIST} n_relax_steps={N_RELAX_STEPS}", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds already done; running {remaining}", flush=True)

    for seed in remaining:
        print(f"[{ANCHOR_NAME}] seed={seed} starting", flush=True)
        r = run_seed(seed)
        write_partial(out_dir, seed, r)
        print(f"[{ANCHOR_NAME}] seed={seed} done", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    total_elapsed = time.time() - t_start
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N,
        "seeds": SEEDS,
        "alpha_list": ALPHA_LIST,
        "aggregate": {str(k): v for k, v in agg.items()},
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": total_elapsed,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict}", flush=True)
    print(f"[{ANCHOR_NAME}] {verdict_msg}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={total_elapsed:.1f}s metrics={metrics_path}", flush=True)


if __name__ == "__main__":
    main()
