"""Q17 -- Set-algebra primitive composability (union, Jaccard, symdiff via trace).

SCIENTIFIC QUESTION:
  Rider on Q1 (tr_w1w2_set_intersect_v1, HARD_PASS r=0.9999990).
  Given K = tr(W1 W2) - (M1*M2 - K)/N (the corrected K estimate), do the
  derived set quantities:
    union:      M1 + M2 - K
    Jaccard:    K / (M1 + M2 - K)
    symdiff:    M1 + M2 - 2*K
  match empirically with MAE < 0.5 cardinality units AND Pearson r > 0.999
  across all 3 derived quantities?

THEORY:
  If tr(W1 W2) / N^2 recovers K (intersection) via the Round 6 formula, then
  inclusion-exclusion directly gives the 3 derived quantities. The question
  is whether the APPROXIMATION (using estimated K vs true K) keeps MAE < 0.5.
  Error budget: K_error = noise in tr estimate ~ sigma_K ~ 0.035 at N=2048, M=50.
  So MAE for union/symdiff ~ sigma_K ~ 0.035. Jaccard MAE depends on K/denominator.

DESIGN:
  N=2048, M1=M2=50 (identical to tr_w1w2_set_intersect_v1 for comparability).
  K grid: {0, 5, 10, 20, 30, 40, 50} -- 7 intersection sizes.
  For each (seed, K):
  1. Generate S1, S2 with |S1 intersect S2| = K.
  2. Compute K_est = tr(W1 W2) * N^2 / N^2 - (M1*M2 - K_guess)/N
     More precisely: K_est = tr(W1 W2) - (M1*M2)/N + K_guess/N
     => K_est ~ K + noise.
     Since K is unknown, we use: K_raw = tr(W1 W2) * N^0 (no bias correction)
     and see if derived quantities match TRUE K-based formula.
     Formula used: K_trace = tr(W1 W2) (raw, includes bias term M1*M2/N).
     Corrected K_est = K_trace - (M1*M2 - K_est)/N.
     Iterative: K_est = (K_trace - M1*M2/N) / (1 - 1/N) ~ K_trace - M1*M2/N.
     So K_est = tr(W1 W2) - M1*M2/N.
  3. Derived quantities from K_est.
  4. Compare to true values (K, M1+M2-K, K/(M1+M2-K), M1+M2-2K).
  5 seeds, 3 trials per (seed, K) for noise averaging.

FORMULA SELF-TESTS (from Q1 baseline):
  1. K=0: tr(W1 W2) ~ M1*M2/N = 2500/2048 = 1.22. K_est = 1.22 - 2500/2048 = 0.0.
  2. K=50: tr(W1 W2) ~ 50 + 2450/2048 = 51.20. K_est = 51.20 - 2500/2048 = 50.0.
  3. K=10: tr(W1 W2) ~ 10 + 2490/2048 = 11.22. K_est = 11.22 - 2500/2048 = 10.0.
     Union(K=10) = M1+M2-K = 90. Jaccard = 10/90 = 0.111. Symdiff = 80.
  4. MAE should be ~ sigma_K ~ 0.035 (well within 0.5 threshold).

PROT-018: no _nN suffix. Production N=2048 per rule 3.
  Stated: production N = 2048; rationale: algebraic rider on Q1 at same scale.

TIMEOUT ESTIMATE:
  Same scale as Q1 (tr_w1w2_set_intersect_v1 took <5s at N=2048 per recent verdict).
  5 seeds * 7 K * 3 trials: ~105 matmuls. timeout=300 (floor).

Anchor: set_algebra_composability_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_set_algebra_composability_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial  # noqa: E402

ANCHOR_NAME = "set_algebra_composability_v1"

# Production config (same as Q1 for comparability)
N = 2048
M1 = 50
M2 = 50
K_GRID = [0, 5, 10, 20, 30, 40, 50]
N_TRIALS = 3
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# Pre-registered thresholds
HP_MAE = 0.5
HP_R   = 0.999
HF_MAE = 2.0
HF_R   = 0.99


def make_pattern_sets(M1: int, M2: int, K: int, N: int,
                      rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """Generate two pattern sets with exactly K shared patterns."""
    # K shared patterns
    shared = rng.choice([-1.0, 1.0], size=(K, N)).astype(np.float64)
    # M1-K unique to S1
    unique1 = rng.choice([-1.0, 1.0], size=(M1 - K, N)).astype(np.float64)
    # M2-K unique to S2
    unique2 = rng.choice([-1.0, 1.0], size=(M2 - K, N)).astype(np.float64)

    if K > 0:
        S1 = np.concatenate([shared, unique1], axis=0)
        S2 = np.concatenate([shared, unique2], axis=0)
    else:
        S1 = unique1
        S2 = unique2

    return S1, S2


def compute_trace(S1: np.ndarray, S2: np.ndarray, N: int) -> float:
    """Compute tr(W1 W2) where W_i = S_i^T S_i / N."""
    # W1 = S1^T @ S1 / N; W2 = S2^T @ S2 / N
    # tr(W1 W2) = tr(S1^T S1 S2^T S2) / N^2
    # = ||S1 S2^T||_F^2 / N^2
    cross = (S1 @ S2.T) / N   # shape (M1, M2)
    return float(np.sum(cross ** 2))


def run_trial(M1: int, M2: int, K: int, N: int,
              rng: np.random.Generator) -> Dict:
    """Run one trial for a given K."""
    S1, S2 = make_pattern_sets(M1, M2, K, N, rng)
    trace_val = compute_trace(S1, S2, N)

    # Corrected K estimate (remove bias term M1*M2/N)
    K_est = trace_val - (M1 * M2) / N

    # True values
    union_true   = M1 + M2 - K
    jaccard_true = K / max(M1 + M2 - K, 1)
    symdiff_true = M1 + M2 - 2 * K

    # Derived from estimate
    union_est   = M1 + M2 - K_est
    denom_est   = max(M1 + M2 - K_est, 1e-6)
    jaccard_est = K_est / denom_est
    symdiff_est = M1 + M2 - 2 * K_est

    return {
        "K_true": K, "K_est": K_est, "trace_val": trace_val,
        "union_true": union_true, "union_est": union_est,
        "jaccard_true": jaccard_true, "jaccard_est": jaccard_est,
        "symdiff_true": symdiff_true, "symdiff_est": symdiff_est,
    }


def run_seed(seed: int, N: int, M1: int, M2: int, K_grid: List[int],
             n_trials: int) -> Dict:
    """Run all K values for one seed."""
    rng = np.random.default_rng(seed)
    results = []
    for K in K_grid:
        for _ in range(n_trials):
            res = run_trial(M1, M2, K, N, rng)
            results.append(res)
    return {"seed": seed, "trials": results}


def compute_metrics(all_trials: List[Dict]) -> Dict:
    """Compute MAE and Pearson r for union, Jaccard, symdiff."""
    union_true  = [t["union_true"]   for t in all_trials]
    union_est   = [t["union_est"]    for t in all_trials]
    jac_true    = [t["jaccard_true"] for t in all_trials]
    jac_est     = [t["jaccard_est"]  for t in all_trials]
    sym_true    = [t["symdiff_true"] for t in all_trials]
    sym_est     = [t["symdiff_est"]  for t in all_trials]

    def mae(a, b):
        return float(np.mean(np.abs(np.array(a) - np.array(b))))

    def pearson_r(a, b):
        a, b = np.array(a), np.array(b)
        if np.std(a) < 1e-10 or np.std(b) < 1e-10:
            return float("nan")
        return float(np.corrcoef(a, b)[0, 1])

    return {
        "union_mae": mae(union_true, union_est),
        "union_r":   pearson_r(union_true, union_est),
        "jaccard_mae": mae(jac_true, jac_est),
        "jaccard_r":   pearson_r(jac_true, jac_est),
        "symdiff_mae": mae(sym_true, sym_est),
        "symdiff_r":   pearson_r(sym_true, sym_est),
        "n_trials": len(all_trials),
    }


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert trace, K_est, derived quantities non-null at tiny scale."""
    rng = np.random.default_rng(99)
    N_t, M_t = 256, 10
    # Test make_pattern_sets
    S1, S2 = make_pattern_sets(M_t, M_t, 3, N_t, rng)
    assert S1.shape == (M_t, N_t), f"S1 shape wrong: {S1.shape}"

    # Test trace
    tr = compute_trace(S1, S2, N_t)
    assert tr > 0 and not math.isnan(tr), f"trace non-positive or NaN: {tr}"

    # Test trial
    res = run_trial(M_t, M_t, 3, N_t, rng)
    assert "K_est" in res, "K_est missing"
    assert not math.isnan(res["K_est"]), "K_est is NaN"
    assert not math.isnan(res["union_est"]), "union_est is NaN"
    assert not math.isnan(res["jaccard_est"]), "jaccard_est is NaN"

    # Test seed run and metric computation
    seed_res = run_seed(7, N_t, M_t, M_t, [0, 3, 5, 10], 2)
    assert "trials" in seed_res and len(seed_res["trials"]) > 0, "no trials"
    m = compute_metrics(seed_res["trials"])
    assert m["n_trials"] > 0, "0 trials in metrics"
    assert not math.isnan(m["union_mae"]), "union_mae is NaN"
    print("[selftest] PASS: set_algebra_composability_v1 metrics non-null", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = {"N": N, "run_mode": run_mode}

    print(f"[{ANCHOR_NAME}] run_mode={run_mode} N={N} M1={M1} M2={M2} K_grid={K_GRID} seeds={seeds}", flush=True)

    done, remaining = resumable_seeds(seeds, out_dir, run_config=run_config)
    print(f"[{ANCHOR_NAME}] checkpoint: {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"  seed={seed}...", flush=True)
        res = run_seed(seed, N, M1, M2, K_GRID, N_TRIALS)
        res["N"] = N
        res["run_mode"] = run_mode
        write_partial(out_dir, seed, res)

    from experiments._seed_checkpoint import aggregate_partials
    per_seed = aggregate_partials(out_dir, seeds, run_config=run_config)

    all_trials = []
    for payload in per_seed.values():
        all_trials.extend(payload.get("trials", []))

    m = compute_metrics(all_trials)
    union_mae    = m["union_mae"]
    union_r      = m["union_r"]
    jac_mae      = m["jaccard_mae"]
    jac_r        = m["jaccard_r"]
    sym_mae      = m["symdiff_mae"]
    sym_r        = m["symdiff_r"]

    all_mae_ok = (union_mae < HP_MAE and jac_mae < HP_MAE and sym_mae < HP_MAE)
    all_r_ok   = (union_r > HP_R and jac_r > HP_R and sym_r > HP_R)

    any_hf_mae = (union_mae > HF_MAE or jac_mae > HF_MAE or sym_mae > HF_MAE)
    any_hf_r   = (union_r < HF_R or jac_r < HF_R or sym_r < HF_R)

    if all_mae_ok and all_r_ok:
        verdict = "HARD_PASS"
    elif any_hf_mae or any_hf_r:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode, "N": N,
        "M1": M1, "M2": M2, "n_seeds": len(seeds),
        "union_mae": union_mae, "union_r": union_r,
        "jaccard_mae": jac_mae, "jaccard_r": jac_r,
        "symdiff_mae": sym_mae, "symdiff_r": sym_r,
        "n_trials_total": m["n_trials"],
        "verdict": verdict, "elapsed_s": elapsed,
        "thresholds": {"HP_MAE": HP_MAE, "HP_r": HP_R, "HF_MAE": HF_MAE, "HF_r": HF_R},
        "verdict_msg": (
            f"Set-algebra composability N={N} M={M1}: "
            f"union(MAE={union_mae:.4f},r={union_r:.6f}) "
            f"Jaccard(MAE={jac_mae:.4f},r={jac_r:.6f}) "
            f"symdiff(MAE={sym_mae:.4f},r={sym_r:.6f}). "
            f"HP: all MAE<{HP_MAE} AND all r>{HP_R}. Verdict={verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} union_r={union_r:.6f} union_mae={union_mae:.4f} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()
