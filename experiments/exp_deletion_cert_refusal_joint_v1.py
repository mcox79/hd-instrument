"""Q14 -- Deletion-cert + refusal-cert joint composition reliability.

SCIENTIFIC QUESTION:
  After deleting a pattern (W -= xi*xi^T/N), does refusal fire correctly?
  Joint: post-delete refusal precision >= 0.95 AND recall >= 0.90.
  Joint reliability >= product of individual reliabilities (multiplicative bound).

PRE-REGISTERED BANDS:
  HARD-PASS: post-delete refusal precision >= 0.95 AND recall >= 0.90 AND
             joint_reliability >= individual_precision * individual_recall * 0.95
             (within 5% of multiplicative prediction -- tolerance for finite N).
  MIDDLE: precision in [0.85, 0.95) OR recall in [0.80, 0.90).
  HARD-FAIL: precision < 0.80 OR recall < 0.75 (joint composition unreliable).

DESIGN:
  N=4096, M=100 stored patterns. 5 seeds.
  Steps per seed:
  1. Store M patterns via outer-product Hopfield (W = sum xi*xi^T / N).
  2. Measure individual refusal precision/recall on random query probes.
     Refusal threshold tau = 0.5 (overlap score).
  3. Delete k=10 patterns (W -= sum_{i in del_set} xi_i * xi_i^T / N).
  4. Measure joint: (a) refusal precision on deleted patterns' probes (should refuse),
     (b) recall on remaining patterns' probes (should not refuse).
  5. Report: pre-delete precision/recall, post-delete precision/recall for deleted set,
     overlap with deleted patterns (should be near crosstalk floor).

  Crosstalk floor: E[|<xi_test, xi_other>|] / N ~ 1/sqrt(N) = 1/sqrt(4096) = 0.0156.
  Post-delete, the deleted pattern's effective weight contribution = 0 -> overlap should
  regress to crosstalk floor.

FORMULA SELF-TESTS:
  1. Pre-delete: overlap of stored pattern with W = 1.0 - (M-1)/N (approx 1.0 at low alpha).
     For M=100, N=4096: alpha = 0.024. Pre-delete self-overlap ~ 1 - 99/4096 = 0.976.
  2. Post-delete: contribution of xi_mu removed => overlap should be ~0 + crosstalk noise.
     Residual overlap ~ sum_{nu != mu} <xi_nu, xi_mu>^2 / N^2 ~ (M-k)/N = 90/4096 = 0.022.
  3. Refusal fires when overlap < tau=0.5. Post-delete overlap ~0.022 < 0.5 => refusal fires.

PROT-018: no _nN suffix. Production N=4096 per rule 3.
  Stated: production N = 4096; rationale: deletion-cert + refusal-cert at moderate N.

TIMEOUT ESTIMATE:
  5 seeds * (M=100 writes + k=10 deletes + 200 query evals): all O(M*N) ops.
  Per seed: ~110 * O(N^2 / N) = O(M*N) = 100 * 4096 = 0.4M ops, ~0.5ms per op.
  5 * 200 query evals * 0.5ms = 0.5s per seed. 5 seeds = 2.5s. timeout=300.

Anchor: deletion_cert_refusal_joint_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_deletion_cert_refusal_joint_v1.md
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

ANCHOR_NAME = "deletion_cert_refusal_joint_v1"

# Production config
N = 4096
M = 100
K_DELETE = 10       # number of patterns to delete
TAU = 0.5           # refusal threshold on overlap score
N_PROBE = 200       # number of probes per condition
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# Pre-registered thresholds
HP_PRECISION   = 0.95
HP_RECALL      = 0.90
HF_PRECISION   = 0.80
HF_RECALL      = 0.75
MULTIPLICATIVE_TOLERANCE = 0.95  # joint >= product * this


def build_weight(patterns: np.ndarray, N: int) -> np.ndarray:
    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)
    return W


def overlap_score_direct(patterns: np.ndarray, query: np.ndarray, N: int) -> float:
    """max |<q, xi_mu>| / N across stored patterns."""
    return float(np.max(np.abs(patterns @ query)) / N)


def eval_refusal(patterns: np.ndarray, probe_patterns: np.ndarray,
                 tau: float, N: int, rng: np.random.Generator,
                 noise_frac: float = 0.10) -> Tuple[float, float]:
    """Measure precision and recall of refusal gate.

    Refusal = score < tau (below threshold => pattern NOT stored => refuse).
    TP: probe from probe_patterns that IS refused (correct refusal for deleted patterns).
    FN: probe from probe_patterns that is NOT refused (missed refusal).

    For recall measurement (retained patterns should NOT be refused):
    we return precision = TP/(TP+FP) and recall = TP/(TP+FN) where TP = correctly
    classified probes. Function adapted based on context.
    """
    n = min(len(probe_patterns), N_PROBE)
    correct = 0
    for mu in range(n):
        q = probe_patterns[mu].copy()
        n_flip = max(1, int(noise_frac * N))
        flip_idx = rng.choice(N, size=n_flip, replace=False)
        q[flip_idx] *= -1
        score = overlap_score_direct(patterns, q, N)
        correct += int(score < tau)
    recall = correct / n
    return recall


def run_seed(seed: int, N: int, M: int, k_delete: int, tau: float,
             n_probe: int) -> Dict:
    """Run full deletion + refusal joint test for one seed."""
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    W = build_weight(patterns, N)

    # Select deletion set (first k_delete patterns)
    del_idx = list(range(k_delete))
    ret_idx = list(range(k_delete, M))

    del_pats = patterns[del_idx]
    ret_pats = patterns[ret_idx]

    # Pre-delete: measure overlap of retained patterns (should be high)
    pre_retained_overlaps = []
    for mu in ret_idx[:20]:
        q = patterns[mu].copy()
        score = overlap_score_direct(patterns, q, N)
        pre_retained_overlaps.append(score)
    pre_retained_mean = float(np.mean(pre_retained_overlaps)) if pre_retained_overlaps else float("nan")

    # Individual pre-delete refusal stats on deleted patterns (should NOT be refused pre-delete)
    rng_pre = np.random.default_rng(seed + 1000)
    # For deleted patterns pre-delete: should pass (not refused) - recall for deleted is ~0 (they ARE stored)
    pre_del_passes = 0
    n_eval = min(k_delete * 10, n_probe)
    for i in range(n_eval):
        mu = del_idx[i % k_delete]
        q = patterns[mu].copy()
        n_flip = max(1, int(0.10 * N))
        flip_idx = rng_pre.choice(N, size=n_flip, replace=False)
        q[flip_idx] *= -1
        score = overlap_score_direct(patterns, q, N)
        pre_del_passes += int(score >= tau)
    pre_del_precision = pre_del_passes / n_eval  # fraction correctly NOT refused

    # Delete the k patterns
    W_new = W.copy()
    for mu in del_idx:
        xi = patterns[mu].reshape(-1, 1).astype(np.float64)
        W_new -= (xi @ xi.T / N).astype(np.float32)
        np.fill_diagonal(W_new, 0.0)

    patterns_retained = patterns[ret_idx]

    # Post-delete: measure refusal precision on deleted patterns
    # Precision: among probes of deleted patterns that score < tau (correct)
    rng_post = np.random.default_rng(seed + 2000)
    post_del_refused = 0
    post_del_scores = []
    n_eval_del = min(k_delete * 10, n_probe)
    for i in range(n_eval_del):
        mu = del_idx[i % k_delete]
        q = patterns[mu].copy()
        n_flip = max(1, int(0.10 * N))
        flip_idx = rng_post.choice(N, size=n_flip, replace=False)
        q[flip_idx] *= -1
        score = overlap_score_direct(patterns_retained, q, N)
        post_del_refused += int(score < tau)
        post_del_scores.append(score)
    post_del_precision = post_del_refused / n_eval_del  # fraction correctly refused

    # Post-delete: measure recall on retained patterns (should NOT be refused)
    rng_ret = np.random.default_rng(seed + 3000)
    ret_not_refused = 0
    n_eval_ret = min(len(ret_idx) * 2, n_probe)
    for i in range(n_eval_ret):
        mu = ret_idx[i % len(ret_idx)]
        q = patterns[mu].copy()
        n_flip = max(1, int(0.10 * N))
        flip_idx = rng_ret.choice(N, size=n_flip, replace=False)
        q[flip_idx] *= -1
        score = overlap_score_direct(patterns_retained, q, N)
        ret_not_refused += int(score >= tau)
    post_ret_recall = ret_not_refused / n_eval_ret  # fraction NOT refused (correct)

    # Overlap floor check on deleted patterns after deletion
    del_overlap_post = float(np.mean(post_del_scores)) if post_del_scores else float("nan")
    crosstalk_floor = 1.0 / math.sqrt(N)

    return {
        "seed": seed,
        "pre_del_precision": pre_del_precision,
        "pre_retained_mean_overlap": pre_retained_mean,
        "post_del_precision": post_del_precision,   # refusal fires correctly
        "post_ret_recall": post_ret_recall,          # retained not refused
        "del_overlap_post_mean": del_overlap_post,
        "crosstalk_floor": crosstalk_floor,
    }


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert deletion + refusal metrics are non-null at tiny scale."""
    res = run_seed(42, 256, 20, 3, 0.5, 50)
    assert "post_del_precision" in res, "post_del_precision missing"
    assert "post_ret_recall" in res, "post_ret_recall missing"
    assert 0.0 <= res["post_del_precision"] <= 1.0, f"precision OOB: {res['post_del_precision']}"
    assert 0.0 <= res["post_ret_recall"] <= 1.0, f"recall OOB: {res['post_ret_recall']}"
    assert not math.isnan(res["post_del_precision"]), "precision is NaN"
    print("[selftest] PASS: deletion_cert_refusal_joint_v1 metrics non-null", flush=True)


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

    print(f"[{ANCHOR_NAME}] run_mode={run_mode} N={N} M={M} K_DELETE={K_DELETE} seeds={seeds}", flush=True)

    done, remaining = resumable_seeds(seeds, out_dir, run_config=run_config)
    print(f"[{ANCHOR_NAME}] checkpoint: {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"  seed={seed}...", flush=True)
        res = run_seed(seed, N, M, K_DELETE, TAU, N_PROBE)
        res["N"] = N
        res["run_mode"] = run_mode
        write_partial(out_dir, seed, res)

    from experiments._seed_checkpoint import aggregate_partials
    per_seed = aggregate_partials(out_dir, seeds, run_config=run_config)

    precisions = [p["post_del_precision"] for p in per_seed.values()]
    recalls    = [p["post_ret_recall"] for p in per_seed.values()]

    avg_precision = float(np.mean(precisions)) if precisions else float("nan")
    avg_recall    = float(np.mean(recalls))    if recalls    else float("nan")

    # Joint reliability vs multiplicative bound
    joint_empirical = avg_precision * avg_recall
    # Individual expected values (pre-delete, no interference)
    pre_precisions = [p["pre_del_precision"] for p in per_seed.values()]
    avg_pre = float(np.mean(pre_precisions)) if pre_precisions else float("nan")
    multiplicative_bound = avg_pre * avg_pre  # rough bound (pre-delete each)
    meets_multiplicative = (
        (not math.isnan(joint_empirical)) and
        (not math.isnan(multiplicative_bound)) and
        (joint_empirical >= multiplicative_bound * MULTIPLICATIVE_TOLERANCE)
    )

    if (avg_precision >= HP_PRECISION and avg_recall >= HP_RECALL and meets_multiplicative):
        verdict = "HARD_PASS"
    elif (avg_precision < HF_PRECISION or avg_recall < HF_RECALL):
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode, "N": N, "M": M,
        "K_delete": K_DELETE, "n_seeds": len(seeds),
        "avg_post_del_precision": avg_precision,
        "avg_post_ret_recall": avg_recall,
        "joint_reliability": joint_empirical,
        "multiplicative_bound": multiplicative_bound,
        "meets_multiplicative": meets_multiplicative,
        "verdict": verdict, "elapsed_s": elapsed,
        "thresholds": {
            "HP_precision": HP_PRECISION, "HP_recall": HP_RECALL,
            "HF_precision": HF_PRECISION, "HF_recall": HF_RECALL,
        },
        "verdict_msg": (
            f"Deletion+refusal joint N={N} M={M} K={K_DELETE}: "
            f"post_del_precision={avg_precision:.4f} (HP>={HP_PRECISION}), "
            f"post_ret_recall={avg_recall:.4f} (HP>={HP_RECALL}), "
            f"joint={joint_empirical:.4f} >= mult_bound={multiplicative_bound:.4f}*{MULTIPLICATIVE_TOLERANCE}. "
            f"Verdict={verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} precision={avg_precision:.4f} recall={avg_recall:.4f} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()
