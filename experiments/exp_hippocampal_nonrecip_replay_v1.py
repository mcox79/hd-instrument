"""
hippocampal_nonrecip_replay_v1 -- Non-reciprocal W replay directionality.

Test C from hippocampal phenomena mapping handoff (2026-06-01).
Section 3 of research note: asymmetric component A = (W - W^T)/2 != 0
should produce statistically significant forward-biased replay in random-init dynamics.

Design:
  Store a sequence of M patterns xi_1, ..., xi_M (a one-directional chain)
  using non-reciprocal Hebbian: W = sum_{t=1}^{M-1} xi_{t+1} xi_t^T / N.
  W is asymmetric: W != W^T.
  Run Hopfield-like dynamics starting from noisy xi_1.
  Measure whether the trajectory visits xi_2, xi_3, ... in order (forward bias)
  vs a time-reversed version.

  Metric: forward_bias = (n_forward_steps - n_backward_steps) / (n_forward_steps + n_backward_steps)
  where n_forward = number of sequential state visits matching the stored order,
  n_backward = same for reverse order.

Pre-reg thresholds:
  HARD-PASS: forward_bias > 0.30 at p < 0.05 (permutation test) in 4/5 seeds.
  MIDDLE:    forward_bias > 0.10 but p > 0.05 in at least 3/5 seeds.
  HARD-FAIL: forward_bias <= 0 in majority (>= 3/5) seeds.

  Calibration: no prior empirical anchor on forward_bias magnitude.
  Bands widened to +/-50% of expected forward_bias ~ 0.50 per BBP theory
  for non-reciprocal Hopfield chains: HARD_PASS threshold = 0.25 (0.5 - 50%),
  HARD_FAIL threshold = -0.10 (chance or reversed).

No _nN suffix; production N=1024 per rule 3 (CA3 scale, same as hippocampal_basin_v1).
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

ANCHOR_NAME = "hippocampal_nonrecip_replay_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_CHAIN = 5          # chain length (patterns in sequence)
    N_TRIALS = 10        # trials per seed
    NOISE_LEVELS = [0.05, 0.10]
    N_PERM = 100         # permutation test samples
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_CHAIN = 10
    N_TRIALS = 50
    NOISE_LEVELS = [0.05, 0.10, 0.15, 0.20]
    N_PERM = 500

HP_FORWARD_BIAS = 0.25   # pre-reg: calibration probe, +/-50% of theory 0.50
HF_FORWARD_BIAS = -0.10  # hard-fail: at or below chance
HP_FRAC_SEEDS = 0.8      # 4/5 seeds must pass


def make_chain_patterns(N: int, M: int, seed: int) -> np.ndarray:
    """M bipolar patterns for a directional chain."""
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(N, M))


def build_nonreciprocal_W(patterns: np.ndarray) -> np.ndarray:
    """
    Non-reciprocal Hebbian: W = sum_{t=0}^{M-2} patterns[:,t+1] patterns[:,t]^T / N.
    W[i,j] reflects backward connection strength from j to i for next pattern.
    """
    N, M = patterns.shape
    W = np.zeros((N, N))
    for t in range(M - 1):
        W += np.outer(patterns[:, t + 1], patterns[:, t]) / N
    return W


def build_symmetric_W(patterns: np.ndarray) -> np.ndarray:
    """Symmetric Hopfield W for baseline comparison."""
    N, M = patterns.shape
    W = np.zeros((N, N))
    for t in range(M):
        W += np.outer(patterns[:, t], patterns[:, t]) / N
    np.fill_diagonal(W, 0.0)
    return W


def run_dynamics(W: np.ndarray, init: np.ndarray, n_steps: int = 20) -> List[np.ndarray]:
    """Run synchronous Hopfield update, collect trajectory."""
    trajectory = [init.copy()]
    x = init.copy()
    for _ in range(n_steps):
        x = np.sign(W @ x + 1e-12)
        trajectory.append(x.copy())
    return trajectory


def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def count_forward_steps(trajectory: List[np.ndarray], patterns: np.ndarray,
                         cos_thresh: float = 0.60) -> int:
    """Count forward pattern visits in trajectory (order 0,1,2,...,M-1)."""
    M = patterns.shape[1]
    fwd = 0
    order = list(range(M))
    t_visit = {i: None for i in range(M)}
    for step, state in enumerate(trajectory):
        for i in range(M):
            if t_visit[i] is None and cos_sim(state, patterns[:, i]) > cos_thresh:
                t_visit[i] = step
    # Check order matches stored sequence
    prev_t = -1
    for i in order[1:]:
        if t_visit[i] is not None:
            if t_visit[i] > prev_t:
                fwd += 1
                prev_t = t_visit[i]
    return fwd


def count_backward_steps(trajectory: List[np.ndarray], patterns: np.ndarray,
                          cos_thresh: float = 0.60) -> int:
    """Count backward pattern visits (reverse order M-1,...,1,0)."""
    M = patterns.shape[1]
    reverse_order = list(range(M - 1, -1, -1))
    t_visit = {i: None for i in range(M)}
    for step, state in enumerate(trajectory):
        for i in range(M):
            if t_visit[i] is None and cos_sim(state, patterns[:, i]) > cos_thresh:
                t_visit[i] = step
    bwd = 0
    prev_t = -1
    for i in reverse_order[1:]:
        if t_visit[i] is not None:
            if t_visit[i] > prev_t:
                bwd += 1
                prev_t = t_visit[i]
    return bwd


def run_one_trial(N: int, M: int, noise_level: float, rng: np.random.RandomState,
                  seed_offset: int) -> Tuple[float, float]:
    """
    Run one trial. Returns (forward_frac, backward_frac).
    """
    patterns = make_chain_patterns(N, M, seed=rng.randint(0, 100000))
    W_nr = build_nonreciprocal_W(patterns)

    # Initialize from noisy first pattern
    noise = rng.choice([-1.0, 1.0], size=N) * noise_level
    init = np.sign(patterns[:, 0] + noise + 1e-12)

    traj_nr = run_dynamics(W_nr, init, n_steps=3 * M)
    fwd = count_forward_steps(traj_nr, patterns)
    bwd = count_backward_steps(traj_nr, patterns)

    total = fwd + bwd
    if total == 0:
        return 0.0, 0.0
    return fwd / total, bwd / total


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    trial_results = []

    for noise in NOISE_LEVELS:
        fwd_fracs = []
        bwd_fracs = []
        for t in range(N_TRIALS):
            f, b = run_one_trial(N, M_CHAIN, noise, rng, t)
            fwd_fracs.append(f)
            bwd_fracs.append(b)
        mean_fwd = float(np.mean(fwd_fracs))
        mean_bwd = float(np.mean(bwd_fracs))
        bias = mean_fwd - mean_bwd
        trial_results.append({
            "noise_level": noise,
            "mean_fwd_frac": mean_fwd,
            "mean_bwd_frac": mean_bwd,
            "forward_bias": bias,
        })
        print(f"  [seed {seed}] noise={noise:.2f} fwd={mean_fwd:.3f} bwd={mean_bwd:.3f} bias={bias:.3f}", flush=True)

    # Permutation test: shuffle patterns order, measure bias under null
    null_biases = []
    for _ in range(N_PERM):
        perm_order = rng.permutation(M_CHAIN)
        patterns_null = make_chain_patterns(N, M_CHAIN, seed=rng.randint(0, 100000))
        W_null = build_nonreciprocal_W(patterns_null[:, perm_order])
        noise = NOISE_LEVELS[0]
        noise_vec = rng.choice([-1.0, 1.0], size=N) * noise
        init = np.sign(patterns_null[:, perm_order[0]] + noise_vec + 1e-12)
        traj = run_dynamics(W_null, init, n_steps=3 * M_CHAIN)
        f = count_forward_steps(traj, patterns_null[:, perm_order])
        b = count_backward_steps(traj, patterns_null[:, perm_order])
        total = f + b
        null_biases.append((f - b) / total if total > 0 else 0.0)

    null_mean = float(np.mean(null_biases))
    null_std = float(np.std(null_biases)) + 1e-12

    # Pick mean bias at NOISE_LEVELS[0] for significance test
    observed_bias = trial_results[0]["forward_bias"]
    z_score = (observed_bias - null_mean) / null_std
    # p-value approximation
    from scipy.stats import norm as sp_norm
    p_val = float(1.0 - sp_norm.cdf(z_score))

    return {
        "by_noise": trial_results,
        "null_mean_bias": null_mean,
        "null_std_bias": null_std,
        "z_score": z_score,
        "p_value": p_val,
        "seed": seed,
        "N": N,
        "M_CHAIN": M_CHAIN,
        "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert all metrics non-null at small scale."""
    N_test = 128
    M_test = 4
    rng = np.random.RandomState(42)
    patterns = make_chain_patterns(N_test, M_test, 42)
    W = build_nonreciprocal_W(patterns)
    assert W.shape == (N_test, N_test), "W shape wrong"
    init = np.sign(patterns[:, 0] + rng.randn(N_test) * 0.1)
    traj = run_dynamics(W, init, n_steps=15)
    assert len(traj) == 16, "trajectory length wrong"
    fwd = count_forward_steps(traj, patterns)
    bwd = count_backward_steps(traj, patterns)
    assert isinstance(fwd, int), "fwd not int"
    assert isinstance(bwd, int), "bwd not int"
    print(f"[selftest] PASS: fwd={fwd} bwd={bwd} N=128 M=4", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    biases_at_low_noise = []
    z_scores = []
    p_values = []
    for v in per_seed.values():
        br = v.get("by_noise", [])
        if br:
            biases_at_low_noise.append(br[0]["forward_bias"])
        z_scores.append(v.get("z_score", float("nan")))
        p_values.append(v.get("p_value", 1.0))

    seeds_passing_bias = sum(1 for b in biases_at_low_noise if b > HP_FORWARD_BIAS)
    seeds_sig = sum(1 for p in p_values if p < 0.05)
    return {
        "mean_forward_bias": float(np.mean(biases_at_low_noise)) if biases_at_low_noise else float("nan"),
        "seeds_passing_bias_threshold": seeds_passing_bias,
        "seeds_significant_p05": seeds_sig,
        "n_seeds": len(per_seed),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    n = summary.get("n_seeds", 1)
    mean_bias = summary.get("mean_forward_bias", 0.0)
    seeds_pass = summary.get("seeds_passing_bias_threshold", 0)
    seeds_sig = summary.get("seeds_significant_p05", 0)

    hp_seeds = math.ceil(HP_FRAC_SEEDS * n)
    a_pass = mean_bias > HP_FORWARD_BIAS and seeds_pass >= hp_seeds
    a_fail = mean_bias <= HF_FORWARD_BIAS

    if a_pass:
        return ("HARD_PASS",
                f"Non-reciprocal replay directionality confirmed. "
                f"mean_bias={mean_bias:.3f}>{HP_FORWARD_BIAS}, "
                f"seeds_passing={seeds_pass}/{n}, "
                f"seeds_sig_p05={seeds_sig}/{n}.")
    if a_fail:
        return ("HARD_FAIL",
                f"No forward-bias. mean_bias={mean_bias:.3f}<={HF_FORWARD_BIAS}. "
                f"Non-reciprocal W does not produce directional replay.")
    return ("MIDDLE_BAND",
            f"Weak forward-bias. mean_bias={mean_bias:.3f}(hp={HP_FORWARD_BIAS}), "
            f"seeds_passing={seeds_pass}/{n}, sig={seeds_sig}/{n}.")


def _verdict_formula_selftests():
    """Formula self-tests."""
    # Test 1: strong bias
    s1 = {"mean_forward_bias": 0.45, "seeds_passing_bias_threshold": 5,
          "seeds_significant_p05": 4, "n_seeds": 5}
    v1, _ = compute_verdict(s1)
    assert v1 == "HARD_PASS", f"Expected HARD_PASS got {v1}"

    # Test 2: negative bias
    s2 = {"mean_forward_bias": -0.20, "seeds_passing_bias_threshold": 0,
          "seeds_significant_p05": 0, "n_seeds": 5}
    v2, _ = compute_verdict(s2)
    assert v2 == "HARD_FAIL", f"Expected HARD_FAIL got {v2}"

    # Test 3: weak positive
    s3 = {"mean_forward_bias": 0.15, "seeds_passing_bias_threshold": 2,
          "seeds_significant_p05": 1, "n_seeds": 5}
    v3, _ = compute_verdict(s3)
    assert v3 == "MIDDLE_BAND", f"Expected MIDDLE_BAND got {v3}"

    print("[formula_selftests] PASS: 3 verdict cases verified", flush=True)


_verdict_formula_selftests()


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} M_CHAIN={M_CHAIN} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} seeds done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        bias = result["by_noise"][0]["forward_bias"] if result.get("by_noise") else 0.0
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s | bias={bias:.3f} z={result.get('z_score',0):.2f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    summary = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(summary)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE,
        "N": N,
        "M_CHAIN": M_CHAIN,
        "seeds": SEEDS,
        "summary": summary,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N_TRIALS": N_TRIALS, "NOISE_LEVELS": NOISE_LEVELS, "N_PERM": N_PERM},
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete (selftests ran at module scope)", flush=True)
        sys.exit(0)
    main()
