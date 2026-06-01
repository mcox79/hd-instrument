"""Q13 -- Query-DP audit accuracy at small epsilon.

SCIENTIFIC QUESTION:
  Does Query-DP noise variance contribution M*c^2/eps^2 / N stay negligible
  vs crosstalk for eps > 0.06, leaving audit accuracy unchanged within 1pp?
  Verify that degradation only appears at eps <= 0.06.

PRE-REGISTERED BANDS:
  HARD-PASS: audit accuracy drop at eps=0.1 < 1.0pp AND at eps=0.3 < 0.5pp AND
             eps=1.0 < 0.2pp; accuracy drop at eps=0.06 is visible (>1pp drop vs eps=inf).
  MIDDLE: drop at eps=0.1 in [1, 3]pp OR degradation is not monotone in eps.
  HARD-FAIL: drop at eps=0.3 > 3pp (query-DP imposes non-negligible cost at moderate eps).

DESIGN:
  N=4096, M=200 stored patterns. 5 seeds.
  Eps grid: [inf (no noise), 1.0, 0.3, 0.1, 0.06].
  DP noise variance per query dimension: sigma^2 = M * c^2 / (eps^2 * N).
  c = 1.0 (pattern-space clip norm, all patterns +/-1).
  Gaussian noise added to overlap probe before threshold comparison.
  Audit metric: precision of overlap-threshold refusal (overlap < tau means
  "not stored"); tau chosen at 0.5 for clean signal/noise separation.
  200 audit queries per (seed, eps): 100 planted (should pass, overlap > tau)
  and 100 random (should be refused, overlap < tau).
  Accuracy = fraction correct at the threshold.
  5 seeds, sweep eps grid.

FORMULA SELF-TESTS:
  1. At eps=inf (no noise): sigma=0, audit accuracy = baseline retrieval accuracy.
  2. At eps=0.06, N=4096, M=200, c=1: sigma^2 = 200*1/(0.0036*4096) = 13.56.
     sigma = 3.68. This is large relative to the overlap signal (max ~1.0).
     Expected: significant accuracy drop.
  3. At eps=0.1: sigma^2 = 200*1/(0.01*4096) = 4.88. sigma=2.21. Should be
     smaller than eps=0.06 but still potentially visible.
  4. At eps=0.3: sigma^2 = 200*1/(0.09*4096) = 0.54. sigma=0.74. Should be
     smaller. Theory says negligible vs crosstalk at moderate M/N.
  5. At eps=1.0: sigma^2 = 200*1/(1.0*4096) = 0.049. sigma=0.22. Negligible.

NOTE on noise scale: the DP noise is added to the overlap score (scalar), not
the full N-dimensional probe vector. The overlap is <q, W*q>/N or similar;
we add Gaussian(0, sigma_scalar^2) where sigma_scalar^2 = c^2/(eps^2 * N)
(post-projection formula per Round 6 drill 2 -- noise on the projected scalar).
This is more faithful: sigma_scalar^2 = M * c^2 / (eps^2 * N) becomes the
variance on the retrieved overlap value. For M=200, N=4096, c=1, eps=0.1:
sigma_scalar = sqrt(200/(0.01*4096)) = sqrt(4.88) = 2.21. This is large
-- test validates whether the AUDIT SIGNAL is above this noise floor.

PROT-018: no _nN suffix. Production N=4096 per rule 3.
  Stated: production N = 4096; rationale: algebraic confirmation at moderate N.

TIMEOUT ESTIMATE:
  5 seeds * 5 eps * 200 queries each: mostly numpy ops at N=4096.
  Per (seed, eps): store M=200 patterns (O(M*N) = 0.8M ops, ~1ms) +
  200 queries (O(M*N) = 0.8M ops per query = 160M ops, ~200ms).
  5 * 5 * 0.2s = 5s. timeout=300 (floor, 60x safety).

Anchor: query_dp_audit_eps_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_query_dp_audit_eps_v1.md
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
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial  # noqa: E402

ANCHOR_NAME = "query_dp_audit_eps_v1"

# Production config
N = 4096
M = 200
TAU = 0.5          # overlap threshold for audit decision
N_QUERIES = 200    # 100 planted + 100 random per eps
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# Eps grid: inf = no noise baseline
EPS_GRID = [float("inf"), 1.0, 0.3, 0.1, 0.06]
C_CLIP = 1.0  # pattern clip norm

# Pre-registered thresholds
HP_DROP_EPS01 = 1.0    # pp
HP_DROP_EPS03 = 0.5    # pp
HP_DROP_EPS10 = 0.2    # pp
HP_VISIBLE_EPS006 = 1.0  # pp (must see at least this drop at eps=0.06)
HF_DROP_EPS03 = 3.0    # pp


def build_weight_matrix(patterns: np.ndarray, N: int) -> np.ndarray:
    """Outer-product Hopfield weight matrix."""
    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)
    return W


def overlap_score(W: np.ndarray, query: np.ndarray, N: int) -> float:
    """Overlap score: max_mu |<q, W*e_mu>|/N via direct pattern comparison."""
    # We use the direct pattern overlap for audit (not Hopfield retrieval)
    # because audit measures whether the probe matches a stored pattern
    # before threshold gating.
    # score = max |<q, xi_mu>| / N
    # For a planted query with noise, this should be near 1.0 (without DP noise).
    return float(np.max(np.abs(W @ query)) / N)


def add_dp_noise(score: float, eps: float, M: int, N: int, c: float,
                 rng: np.random.Generator) -> float:
    """Add DP Gaussian noise to overlap score."""
    if math.isinf(eps):
        return score
    sigma_sq = (M * c * c) / (eps * eps * N)
    sigma = math.sqrt(sigma_sq)
    return score + float(rng.normal(0.0, sigma))


def run_seed(seed: int, N: int, M: int, tau: float, eps_grid: List[float],
             n_queries: int, c_clip: float) -> Dict:
    """Run one seed across all eps values."""
    rng = np.random.default_rng(seed)
    # Store M patterns
    patterns = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    W = build_weight_matrix(patterns, N)

    n_planted = n_queries // 2
    n_random = n_queries - n_planted

    # Generate queries
    planted_qs = []
    random_qs  = []
    for mu in range(n_planted):
        # noisy copy of pattern mu (10% flip)
        q = patterns[mu % M].copy()
        n_flip = max(1, int(0.10 * N))
        flip_idx = rng.choice(N, size=n_flip, replace=False)
        q[flip_idx] *= -1
        planted_qs.append(q)
    for _ in range(n_random):
        q = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
        random_qs.append(q)

    # Pre-compute clean overlap scores (no DP noise)
    planted_scores = np.array([overlap_score(W, q, N) for q in planted_qs])
    random_scores  = np.array([overlap_score(W, q, N) for q in random_qs])

    eps_results = {}
    for eps in eps_grid:
        eps_key = "inf" if math.isinf(eps) else str(eps)
        eps_seed_offset = 0 if math.isinf(eps) else int(eps * 1000 + 999)
        rng_eps = np.random.default_rng(seed + eps_seed_offset)

        # Add DP noise to scores
        noisy_planted = np.array([
            add_dp_noise(s, eps, M, N, c_clip, rng_eps) for s in planted_scores
        ])
        noisy_random = np.array([
            add_dp_noise(s, eps, M, N, c_clip, rng_eps) for s in random_scores
        ])

        # Audit decision: planted should have score >= tau; random should have score < tau
        tp = int((noisy_planted >= tau).sum())   # correct: planted passes
        tn = int((noisy_random  <  tau).sum())   # correct: random refused
        accuracy = (tp + tn) / n_queries

        eps_results[eps_key] = {
            "accuracy": accuracy,
            "tp": tp, "tn": tn,
            "n_planted": n_planted, "n_random": n_random,
        }

    return {"seed": seed, "eps_results": eps_results}


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert DP noise and accuracy metrics are non-null at tiny scale."""
    rng = np.random.default_rng(42)
    N_t, M_t = 256, 20
    pats = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    W_t = build_weight_matrix(pats, N_t)

    # Test overlap_score non-null
    q = pats[0].copy()
    s = overlap_score(W_t, q, N_t)
    assert s is not None and not math.isnan(s) and s > 0.0, f"overlap_score non-positive: {s}"

    # Test DP noise addition
    s_noisy = add_dp_noise(s, 0.1, M_t, N_t, 1.0, rng)
    assert s_noisy is not None, "DP noisy score is None"

    # Test full seed run at tiny scale passes
    res = run_seed(7, N_t, M_t, 0.5, [float("inf"), 0.1], 20, 1.0)
    assert "eps_results" in res, "eps_results missing"
    assert "inf" in res["eps_results"], "eps=inf missing"
    acc_inf = res["eps_results"]["inf"]["accuracy"]
    assert 0.0 <= acc_inf <= 1.0, f"accuracy out of [0,1]: {acc_inf}"
    print("[selftest] PASS: query_dp_audit_eps_v1 metrics non-null", flush=True)


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

    print(f"[{ANCHOR_NAME}] run_mode={run_mode} N={N} M={M} seeds={seeds} eps_grid={EPS_GRID}", flush=True)

    done, remaining = resumable_seeds(seeds, out_dir, run_config=run_config)
    print(f"[{ANCHOR_NAME}] checkpoint: {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"  seed={seed}...", flush=True)
        res = run_seed(seed, N, M, TAU, EPS_GRID, N_QUERIES, C_CLIP)
        res["N"] = N
        res["run_mode"] = run_mode
        write_partial(out_dir, seed, res)

    # Aggregate
    from experiments._seed_checkpoint import aggregate_partials
    per_seed = aggregate_partials(out_dir, seeds, run_config=run_config)

    # Per eps accuracy
    eps_accuracies: Dict[str, List[float]] = {}
    for seed_key, payload in per_seed.items():
        for eps_key, er in payload["eps_results"].items():
            eps_accuracies.setdefault(eps_key, []).append(er["accuracy"])

    baseline_acc_vals = eps_accuracies.get("inf", [])
    baseline_acc = float(np.mean(baseline_acc_vals)) if baseline_acc_vals else float("nan")

    def mean_acc(eps_key: str) -> float:
        vals = eps_accuracies.get(eps_key, [])
        return float(np.mean(vals)) if vals else float("nan")

    drop_10  = (baseline_acc - mean_acc("0.1"))  * 100.0
    drop_03  = (baseline_acc - mean_acc("0.3"))  * 100.0
    drop_10v = (baseline_acc - mean_acc("1.0"))  * 100.0
    drop_006 = (baseline_acc - mean_acc("0.06")) * 100.0

    # Verdict
    if (drop_10 < HP_DROP_EPS01 and drop_03 < HP_DROP_EPS03
            and drop_10v < HP_DROP_EPS10 and drop_006 >= HP_VISIBLE_EPS006):
        verdict = "HARD_PASS"
    elif (drop_03 > HF_DROP_EPS03):
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode, "N": N, "M": M,
        "n_seeds": len(seeds),
        "baseline_acc": baseline_acc,
        "acc_eps_10":  mean_acc("1.0"),
        "acc_eps_03":  mean_acc("0.3"),
        "acc_eps_01":  mean_acc("0.1"),
        "acc_eps_006": mean_acc("0.06"),
        "drop_pp_eps10":  drop_10v,
        "drop_pp_eps03":  drop_03,
        "drop_pp_eps01":  drop_10,
        "drop_pp_eps006": drop_006,
        "verdict": verdict, "elapsed_s": elapsed,
        "thresholds": {
            "HP_drop_eps01_pp": HP_DROP_EPS01,
            "HP_drop_eps03_pp": HP_DROP_EPS03,
            "HP_drop_eps10_pp": HP_DROP_EPS10,
            "HP_visible_eps006_pp": HP_VISIBLE_EPS006,
            "HF_drop_eps03_pp": HF_DROP_EPS03,
        },
        "verdict_msg": (
            f"Query-DP eps sweep N={N} M={M}: baseline_acc={baseline_acc:.4f}. "
            f"Drops: eps=1.0:{drop_10v:.2f}pp eps=0.3:{drop_03:.2f}pp "
            f"eps=0.1:{drop_10:.2f}pp eps=0.06:{drop_006:.2f}pp. "
            f"HP: eps>=0.1 drop<1pp AND eps=0.06 visible(>1pp). Verdict={verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()
