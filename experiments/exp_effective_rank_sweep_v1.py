"""
effective_rank_sweep_v1 -- Effective rank monotone-in-M sweep.

SCIENTIFIC QUESTION (deep-drill: effective rank monotone-in-M):
  For the Hopfield weight matrix W = (1/N) * Xi^T Xi (M x N BSC patterns),
  is the effective rank r_eff(W) = exp(H(sigma)) monotone increasing in M?

  Where H(sigma) = -sum_i p_i log p_i is the entropy of the normalized
  singular value distribution: p_i = sigma_i^2 / sum_j sigma_j^2.

  This tests whether the substrate's representational dimensionality
  grows monotonically with the number of stored patterns (as intuitively
  expected), and whether the growth rate matches predictions from random
  matrix theory (r_eff ~ min(M, N) for M << N).

  Theory: W = Xi^T Xi / N; singular values of W = eigenvalues of W (symmetric).
  For M << N: W has M non-trivial eigenvalues ~ lambda_i ~ 1 + O(sqrt(M/N)).
  Effective rank ~ M (all eigenvalues approximately equal).
  Near capacity (M ~ alpha_c * N): rank ~ alpha_c * N but squashed by capacity effects.

PRE-REGISTERED BANDS:
  HARD-PASS: r_eff is monotone increasing in M for >= 4/5 seeds
             AND r_eff(M) >= 0.5 * M for M <= 0.10 * N (well below capacity).
  MIDDLE: monotone in >= 3/5 seeds OR r_eff(M) in [0.25*M, 0.5*M].
  HARD-FAIL: r_eff not monotone in >= 3/5 seeds (non-monotone is a structural anomaly).

FORMULA SELF-TESTS:
  1. r_eff of identity = N (all eigenvalues equal).
  2. r_eff of rank-1 matrix = 1 (one dominant eigenvalue).
  3. r_eff is in [1, min(M, N)] for any W.
  4. monotone_increasing test: r_eff(M1) < r_eff(M2) when M1 < M2.

No _nN suffix; production N=4096 per rule 3.
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "effective_rank_sweep_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_SWEEP = [10, 20, 50, 100, 200]
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_SWEEP = [5, 10, 20, 50, 100, 200, 300, 400, 500]

# Pre-reg thresholds
HP_FRAC_MONOTONE = 4/5
HF_FRAC_NONMONO = 3/5
HP_RATIO_THRESHOLD = 0.5   # r_eff >= 0.5*M for M <= 0.10*N (M <= 409)
CAPACITY_THRESHOLD_FRACTION = 0.10   # M <= 0.10 * N = 409.6

# Formula self-tests
def _effective_rank(eigs: np.ndarray) -> float:
    """r_eff = exp(-sum p_i log p_i), p_i = lambda_i^2 / sum_j lambda_j^2."""
    lam2 = eigs ** 2
    total = float(np.sum(lam2))
    if total < 1e-15:
        return 0.0
    p = lam2 / total
    p = p[p > 1e-15]
    return float(np.exp(-np.sum(p * np.log(p))))


# Test: identity matrix has r_eff = N
_N_test = 16
_W_id = np.eye(_N_test)
_eigs_id = np.abs(np.linalg.eigvalsh(_W_id))
_reff_id = _effective_rank(_eigs_id)
assert abs(_reff_id - _N_test) < 0.1, f"r_eff of identity should be N={_N_test}, got {_reff_id:.2f}"

# Test: rank-1 matrix
_v = np.ones(_N_test) / math.sqrt(_N_test)
_W_rank1 = np.outer(_v, _v)
_eigs_r1 = np.abs(np.linalg.eigvalsh(_W_rank1))
_reff_r1 = _effective_rank(_eigs_r1)
assert abs(_reff_r1 - 1.0) < 0.1, f"r_eff of rank-1 should be 1.0, got {_reff_r1:.2f}"


def compute_effective_rank(M: int, N: int, seed: int) -> Tuple[float, float]:
    """Build Hopfield W for M patterns, return effective rank and ratio r_eff/M."""
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N))
    W = Xi.T @ Xi / N
    # W is N x N symmetric; eigenvalues via eigvalsh
    # We only need the top M non-trivial eigenvalues
    # Use eigvalsh on Gram = Xi @ Xi^T / N (M x M) - same non-zero spectrum
    Gram = Xi @ Xi.T / N   # M x M
    eigs = np.linalg.eigvalsh(Gram)
    eigs = np.abs(eigs[eigs > 1e-10])  # positive eigenvalues only
    reff = _effective_rank(eigs)
    ratio = reff / M if M > 0 else float("nan")
    return reff, ratio


def run_seed(seed: int) -> Dict:
    """Run M sweep for one seed, return effective ranks."""
    reff_list = []
    for M in M_SWEEP:
        t0 = time.time()
        reff, ratio = compute_effective_rank(M, N, seed)
        elapsed = time.time() - t0
        print(f"  [seed={seed} M={M}] r_eff={reff:.2f} r_eff/M={ratio:.3f} ({elapsed:.1f}s)", flush=True)
        reff_list.append({"M": M, "r_eff": reff, "r_eff_over_M": ratio})

    # Check monotonicity
    reffs = [r["r_eff"] for r in reff_list]
    is_monotone = all(reffs[i] <= reffs[i+1] for i in range(len(reffs)-1))

    return {
        "M_sweep": M_SWEEP,
        "reff_list": reff_list,
        "is_monotone": is_monotone,
        "seed": seed, "N": N, "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert effective rank metrics are non-null and sensible at small scale."""
    N_test = 512
    M_test = 20

    reff, ratio = compute_effective_rank(M_test, N_test, seed=42)
    assert reff > 0, f"r_eff=0 is wrong"
    assert reff <= M_test + 1, f"r_eff={reff} > M={M_test} (impossible)"
    assert not math.isnan(ratio), "r_eff/M is NaN"
    # At M=20, N=512 (well below capacity), r_eff should be substantial fraction of M
    assert ratio > 0.3, f"r_eff/M too low at N=512: {ratio:.3f}"

    # Also verify monotonicity at small scale
    reffs = [compute_effective_rank(m, N_test, seed=42)[0] for m in [5, 10, 20]]
    is_mono = all(reffs[i] <= reffs[i+1] for i in range(len(reffs)-1))
    assert is_mono, f"r_eff not monotone at small scale: {reffs}"

    print(f"[selftest] PASS: r_eff={reff:.2f} ratio={ratio:.3f} monotone={is_mono}", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify formula properties."""
    # r_eff bounds
    eigs_test = np.array([1.0, 1.0, 1.0, 1.0])
    reff = _effective_rank(eigs_test)
    assert abs(reff - 4.0) < 0.01, f"equal eigenvalues: r_eff should be 4, got {reff}"

    # Degenerate: one dominant
    eigs_deg = np.array([10.0, 0.01, 0.01, 0.01])
    reff_deg = _effective_rank(eigs_deg)
    assert reff_deg < 2.0, f"dominated: r_eff should be ~1, got {reff_deg}"
    print("[formula_selftests] PASS: r_eff bounds verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate across seeds."""
    # Per M: mean r_eff and ratio
    M_to_reffs = {M: [] for M in M_SWEEP}
    M_to_ratios = {M: [] for M in M_SWEEP}
    n_monotone = 0
    n_seeds = 0

    for seed_data in per_seed.values():
        n_seeds += 1
        if seed_data.get("is_monotone"):
            n_monotone += 1
        for r in seed_data.get("reff_list", []):
            M = r["M"]
            if M in M_to_reffs:
                M_to_reffs[M].append(r["r_eff"])
                M_to_ratios[M].append(r["r_eff_over_M"])

    configs = []
    for M in M_SWEEP:
        reffs = M_to_reffs[M]
        ratios = M_to_ratios[M]
        configs.append({
            "M": M,
            "mean_r_eff": float(np.mean(reffs)) if reffs else float("nan"),
            "mean_ratio": float(np.mean(ratios)) if ratios else float("nan"),
            "n_seeds": len(reffs),
            "below_capacity": M <= CAPACITY_THRESHOLD_FRACTION * N,
        })

    frac_monotone = n_monotone / n_seeds if n_seeds > 0 else 0.0
    return {
        "configs": configs,
        "n_monotone_seeds": n_monotone,
        "n_seeds_total": n_seeds,
        "frac_monotone": frac_monotone,
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    frac_mono = agg.get("frac_monotone", 0.0)
    configs = agg.get("configs", [])

    below_cap = [c for c in configs if c.get("below_capacity") and not math.isnan(c.get("mean_ratio", float("nan")))]
    ratios_bc = [c["mean_ratio"] for c in below_cap]
    mean_ratio_bc = float(np.mean(ratios_bc)) if ratios_bc else float("nan")

    hp = (frac_mono >= HP_FRAC_MONOTONE and
          not math.isnan(mean_ratio_bc) and
          mean_ratio_bc >= HP_RATIO_THRESHOLD)
    hf = frac_mono < (1.0 - HF_FRAC_NONMONO + 0.01)

    if hp:
        return ("HARD_PASS",
                f"r_eff monotone in M confirmed. "
                f"frac_monotone={frac_mono:.2f} (HP>={HP_FRAC_MONOTONE:.2f}). "
                f"mean_r_eff/M (below cap)={mean_ratio_bc:.3f} (HP>={HP_RATIO_THRESHOLD}). "
                f"Substrate representational dim grows with pattern count.")
    if hf:
        return ("HARD_FAIL",
                f"r_eff NOT monotone. frac_monotone={frac_mono:.2f} "
                f"(HF threshold frac_nonmono>={HF_FRAC_NONMONO:.2f}). "
                f"Structural anomaly in effective rank.")
    return ("MIDDLE_BAND",
            f"Partial monotonicity. frac_monotone={frac_mono:.2f}. "
            f"mean_ratio_below_cap={mean_ratio_bc:.3f}. "
            f"Moderate capacity effects at tested M range.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"M_SWEEP={M_SWEEP} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        is_mono = result.get("is_monotone", False)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s monotone={is_mono}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE, "N": N,
        "M_SWEEP": M_SWEEP, "seeds": SEEDS,
        "aggregated": agg,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
