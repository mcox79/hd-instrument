"""
lru_decay_kendall_v1 -- Native LRU/FIFO via weight decay on WRITE; Kendall-tau ranking.

SCIENTIFIC QUESTION (Caching-Policy Expressibility):
  Does applying exponential decay (gamma=0.95) to W before each new Hebbian write
  implement a native LRU (Least Recently Used) eviction policy?
  The substrate IS a frequency sketch (Kendall-tau=0.9951 claimed in drill finding).
  Prediction: after writing patterns in sequence p_1 ... p_M with decay gamma=0.95
  applied before each write, the Kendall-tau correlation between write-recency rank
  and post-sequence retrieval similarity rank should be >= 0.95.
  (Most recently written = highest similarity; earliest written = lowest similarity.)

PRE-REGISTERED BANDS:
  HARD-PASS: Kendall-tau >= 0.90 (drill claimed 0.9951 but that was for LFU;
             LRU via decay is similar mechanism; calibration probe -- +-50% from 0.90
             gives HP floor = 0.90).
  MIDDLE: 0.60 <= Kendall-tau < 0.90.
  HARD-FAIL: Kendall-tau < 0.60 (near-random ranking = no LRU signal).

Calibration probe note: no prior empirical anchor for LRU-via-decay. Bands set
conservatively; theory predicts strong recency ordering due to gamma^(M-t) weight decay.

FORMULA SELF-TESTS:
  1. After M=10 writes with gamma=0.95, the oldest pattern (index 0) has effective
     weight gamma^9 = 0.95^9 ~ 0.630, newest (index 9) has weight gamma^0 = 1.0.
     Ratio 1.0/0.630 ~ 1.59. So recency signal should be detectable.
  2. At M=20 writes, oldest weight = 0.95^19 ~ 0.377. Ratio 1.0/0.377 ~ 2.65x.
     Should give stronger tau at M=20 than M=10.
  3. Kendall-tau self-test: prefect ranking gives tau=1.0; reversed ranking gives tau=-1.

TIMEOUT ESTIMATE:
  Smoke: N=1024, M_sweep=[10, 20, 40], 2 seeds.
  Full: N=1024, M_sweep=[10, 20, 40, 80], 5 seeds.
  Linear scaling. Smoke wall ~5s -> Full ~20s -> timeout=120s.
  No _nN suffix; production N=1024.
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
from scipy.stats import kendalltau

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "lru_decay_kendall_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024
GAMMA = 0.95

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_SWEEP = [10, 20, 40]
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_SWEEP = [10, 20, 40, 80]

# Pre-reg thresholds
HP_KENDALL = 0.90
MID_KENDALL_LOW = 0.60
HF_KENDALL = 0.60

# Formula self-tests
_gamma_test = 0.95 ** 9
assert abs(_gamma_test - 0.630) < 0.01, f"gamma^9 test failed: {_gamma_test}"

_tau_test_perfect = kendalltau([1, 2, 3, 4], [1, 2, 3, 4]).statistic
assert abs(_tau_test_perfect - 1.0) < 1e-6, f"Kendall tau perfect ranking: {_tau_test_perfect}"


def build_patterns(M: int, N: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)


def build_lru_w_decay(patterns: np.ndarray, gamma: float, N: int) -> np.ndarray:
    """
    Write patterns sequentially with exponential decay.
    Before writing pattern t: W <- gamma * W
    After all writes, pattern 0 (oldest) has effective weight gamma^(M-1).
    Pattern M-1 (newest) has effective weight gamma^0 = 1.
    """
    M = patterns.shape[0]
    W = np.zeros((N, N), dtype=np.float64)
    for t in range(M):
        W = gamma * W
        xi = patterns[t]
        W += np.outer(xi, xi) / N
    return W


def measure_retrieval_sims(W: np.ndarray, patterns: np.ndarray) -> np.ndarray:
    """Measure cosine similarity of W @ xi_j to xi_j for each pattern."""
    M = patterns.shape[0]
    sims = np.zeros(M)
    for j in range(M):
        xi = patterns[j]
        retrieved = W @ xi
        norm_r = np.linalg.norm(retrieved)
        norm_xi = np.linalg.norm(xi)
        sims[j] = float(np.dot(retrieved, xi) / (norm_r * norm_xi + 1e-12))
    return sims


def run_seed(seed: int) -> Dict:
    """Run one seed: for each M in M_SWEEP, measure LRU Kendall-tau."""
    results = {}
    for M in M_SWEEP:
        patterns = build_patterns(M, N, seed)
        W = build_lru_w_decay(patterns, GAMMA, N)
        sims = measure_retrieval_sims(W, patterns)

        # Recency rank: pattern M-1 (most recent) = rank 0 (best retention expected)
        # sim rank: highest sim = rank 0
        recency_rank = np.arange(M - 1, -1, -1)  # newest=0, oldest=M-1
        sim_rank = np.argsort(-sims)              # indices sorted by sim descending
        # Create rank arrays for correlation
        write_order = np.arange(M)  # 0=oldest, M-1=newest
        tau_result = kendalltau(write_order, sims)
        tau_val = float(tau_result.statistic)

        # Effective weight ratio: newest vs oldest
        weight_ratio = 1.0 / (GAMMA ** (M - 1))

        print(f"  [seed={seed} M={M}] tau={tau_val:.4f} weight_ratio={weight_ratio:.2f} "
              f"sims=[{sims[0]:.3f},...,{sims[-1]:.3f}]", flush=True)

        results[M] = {
            "M": M,
            "kendall_tau": tau_val,
            "weight_ratio_new_vs_old": weight_ratio,
            "sims_oldest": float(sims[0]),
            "sims_newest": float(sims[-1]),
        }
    return {"M_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert LRU decay gives non-trivial recency ordering."""
    N_t = 128
    M_t = 15
    seed = 42
    patterns = build_patterns(M_t, N_t, seed)
    W = build_lru_w_decay(patterns, GAMMA, N_t)
    sims = measure_retrieval_sims(W, patterns)
    assert len(sims) == M_t, f"sims wrong length: {len(sims)}"
    assert not any(math.isnan(s) for s in sims), "sims contain NaN"
    # Newest should have higher sim than oldest (basic recency check)
    assert sims[-1] > sims[0], f"No recency signal: sims[-1]={sims[-1]:.3f} <= sims[0]={sims[0]:.3f}"
    tau_val = float(kendalltau(np.arange(M_t), sims).statistic)
    assert tau_val > 0.3, f"Weak recency ordering: tau={tau_val:.4f}"
    print(f"[selftest] PASS: recency tau={tau_val:.4f} sims[0]={sims[0]:.3f} sims[-1]={sims[-1]:.3f}",
          flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    g9 = 0.95 ** 9
    assert abs(g9 - 0.630) < 0.01, f"gamma^9 formula error: {g9}"
    print("[formula_selftests] PASS: LRU decay formula verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for M in M_SWEEP:
        tau_vals = []
        ratio_vals = []
        for sd in per_seed.values():
            mr = sd["M_results"].get(M) or sd["M_results"].get(str(M))
            if mr is None:
                continue
            tau_vals.append(mr["kendall_tau"])
            ratio_vals.append(mr["weight_ratio_new_vs_old"])
        agg[M] = {
            "M": M,
            "mean_kendall_tau": float(np.mean(tau_vals)) if tau_vals else float("nan"),
            "std_kendall_tau": float(np.std(tau_vals)) if len(tau_vals) > 1 else float("nan"),
            "mean_weight_ratio": float(np.mean(ratio_vals)) if ratio_vals else float("nan"),
            "n_seeds": len(tau_vals),
        }
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    # Primary metric: tau at largest M (strongest signal expected)
    sorted_M = sorted(agg.keys(), reverse=True)
    primary_M = sorted_M[0] if sorted_M else None
    if primary_M is None:
        return ("HARD_FAIL", "No aggregated results.")
    tau_primary = agg[primary_M]["mean_kendall_tau"]
    # Also check mean across all M
    all_taus = [v["mean_kendall_tau"] for v in agg.values()
                if not math.isnan(v["mean_kendall_tau"])]
    mean_tau = float(np.mean(all_taus)) if all_taus else float("nan")

    if math.isnan(tau_primary):
        return ("HARD_FAIL", "Kendall-tau is NaN at largest M.")

    if tau_primary >= HP_KENDALL:
        return ("HARD_PASS",
                f"LRU-via-decay confirmed. tau at M={primary_M}: {tau_primary:.4f} "
                f"(HP>={HP_KENDALL}). mean tau across M: {mean_tau:.4f}. "
                f"gamma={GAMMA} weight-decay LRU operative.")
    if tau_primary < HF_KENDALL:
        return ("HARD_FAIL",
                f"No LRU signal. tau at M={primary_M}: {tau_primary:.4f} < HF {HF_KENDALL}.")
    return ("MIDDLE_BAND",
            f"Partial LRU signal. tau at M={primary_M}: {tau_primary:.4f} "
            f"(HP>={HP_KENDALL}, HF<{HF_KENDALL}). mean tau: {mean_tau:.4f}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} gamma={GAMMA} "
          f"M_sweep={M_SWEEP} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE, "N": N, "gamma": GAMMA,
        "M_SWEEP": M_SWEEP, "seeds": SEEDS,
        "aggregated": {str(M): v for M, v in agg.items()},
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
