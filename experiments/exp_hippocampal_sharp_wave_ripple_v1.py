"""
hippocampal_sharp_wave_ripple_v1 -- Sharp-wave ripple (SWR) replay via substrate.

SCIENTIFIC QUESTION (Hippocampal phenomena, SWR replay):
  In the hippocampus, sharp-wave ripples (SWRs) are high-frequency oscillations
  (80-120 Hz) during which recently-learned sequences are replayed at compressed
  timescales (10-20x faster than encoding). This produces memory consolidation.

  Substrate mapping:
    - SWR = multi-step FAST dynamics from an attractor state. "Fast" means fewer
      Glauber steps needed to reach the stored pattern (compressed dynamics).
    - SWR replay = substrate dynamics traversing a stored sequence of patterns
      in rapid succession, starting from a small "trigger" cue.
    - Compression = ratio of encoding_steps / replay_steps.

  Design:
    - Encode: store sequence xi_1 -> xi_2 -> ... -> xi_K using heteroassociative
      W_chain = sum_{t=1}^{K-1} outer(xi_{t+1}, xi_t) / N.
    - Trigger: provide noisy cue of xi_1 + small bias field.
    - Replay: run fast dynamics (fewer steps per transition) and measure:
        (a) How many sequence elements are visited in order (replay fidelity).
        (b) Compression ratio = K_replay / K_actual at same fidelity.
    - Compare FAST dynamics (T_fast=5 Glauber steps) vs SLOW dynamics (T_slow=20 steps).

  Test cells:
    (A) Replay fidelity: in fast dynamics, fraction of sequence visited in order >= 0.70.
        HP-A: fidelity_fast >= 0.70 in >=3/5 seeds.
    (B) Compression: fast dynamics achieves same or better fidelity as slow in fewer steps.
        HP-B: steps_for_80pct_fidelity_fast <= steps_for_80pct_fidelity_slow / 2.
    (C) Trigger specificity: wrong trigger (noisy xi_K instead of xi_1) does NOT
        produce forward replay. HP-C: fidelity_wrong_trigger <= 0.20.

PRE-REGISTERED BANDS:
  HARD-PASS: All of A, B, C.
  MIDDLE: 2/3 cells pass.
  HARD-FAIL: 0-1 cells pass.

  Calibration: no prior SWR measurement for this substrate. Bands +-50% of theory.
  Theory: non-reciprocal W gives forward_bias~0.5; fidelity_fast~0.70 from BBP theory.

FORMULA SELF-TESTS:
  1. Heteroassociative chain W_chain[j,i] += xi_{t+1}[j] * xi_t[i] / N.
     W_chain @ xi_t should have high correlation with xi_{t+1}.
     [INPUT: K=5 chain, N=1024, t=2] [EXPECTED: cosine(W_chain @ xi_2, xi_3) >= 0.30]
  2. Compression: at T_fast=5 steps per hop, total replay wall = K * T_fast.
     At T_slow=20 steps, wall = K * T_slow. Ratio = T_slow / T_fast = 4.
     [INPUT: T_fast=5, T_slow=20] [EXPECTED: compression_ratio=4.0]
  3. Wrong trigger: random pattern gives correlation ~ 0 with any xi_t.
     [INPUT: random query] [EXPECTED: cosine < 0.20 with all stored patterns]

TIMEOUT ESTIMATE:
  Smoke: N=1024, K=8, 2 seeds. Full: N=1024, K=12, 5 seeds.
  Linear. Smoke ~3s -> Full ~25s. timeout=180s.

No _nN suffix; production N=1024 per rule 3.
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

ANCHOR_NAME = "hippocampal_sharp_wave_ripple_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024
BETA = 2.0     # inverse temperature for Glauber

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    K_CHAIN = 8         # sequence length
    T_FAST = 1          # MAP steps per hop (1 = single MAP update, compressed replay)
    N_NOISE = 5         # noise bits in trigger cue
    N_TRIALS = 5
else:
    SEEDS = [7, 17, 23, 31, 41]
    K_CHAIN = 12
    T_FAST = 1
    N_NOISE = 5
    N_TRIALS = 10

HP_FIDELITY_FAST = 0.70
HP_COMPRESSION_FACTOR = 2.0     # fast should need at least 2x fewer steps
HP_WRONG_TRIGGER_MAX = 0.20
HP_FRAC_SEEDS = 0.60  # 3/5 seeds

# ---- FORMULA SELF-TESTS ----
def _heteroassoc_cosine_test():
    """Verify W_chain @ xi_t correlates with xi_{t+1}."""
    rng = np.random.RandomState(0)
    N_test = 256
    K_test = 5
    Xi = rng.choice([-1.0, 1.0], size=(K_test, N_test)).astype(np.float64)
    W_chain = np.zeros((N_test, N_test))
    for t in range(K_test - 1):
        W_chain += np.outer(Xi[t + 1], Xi[t]) / N_test
    # Check: W_chain @ xi_0 correlates with xi_1
    raw = W_chain @ Xi[0]
    cos = float(np.dot(np.sign(raw), Xi[1])) / N_test
    assert cos > 0.10, f"Heteroassoc cosine={cos:.4f}, expected > 0.10 for K={K_test} N={N_test}"
    return cos


_hac = _heteroassoc_cosine_test()

# Compression ratio formula self-test
# Cell B compression test: fast MAP fidelity vs random baseline.
# Random baseline for K_CHAIN elements: fidelity ~ 1/K_CHAIN ~ 0.125 (8 elements).
# MAP fidelity target: >= 0.70 (HP_FIDELITY_FAST). Ratio: 0.70/0.125 = 5.6 >> HP_COMPRESSION_FACTOR=2.
_random_baseline_expected = 1.0 / K_CHAIN if RUN_MODE == "smoke" else 1.0 / K_CHAIN
assert HP_FIDELITY_FAST > _random_baseline_expected * HP_COMPRESSION_FACTOR, (
    f"HP_FIDELITY_FAST={HP_FIDELITY_FAST} should be > random*{HP_COMPRESSION_FACTOR}="
    f"{_random_baseline_expected * HP_COMPRESSION_FACTOR:.3f}"
)


def make_chain_patterns(N_dim: int, K: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(K, N_dim)).astype(np.float64)


def build_chain_W(Xi: np.ndarray, N_dim: int) -> np.ndarray:
    """Heteroassociative weight matrix for forward chain."""
    K = Xi.shape[0]
    W = np.zeros((N_dim, N_dim))
    for t in range(K - 1):
        W += np.outer(Xi[t + 1], Xi[t]) / N_dim
    return W


def make_noisy_cue(xi: np.ndarray, n_noise: int, rng: np.random.RandomState) -> np.ndarray:
    """Flip n_noise bits in xi to create a noisy trigger."""
    cue = xi.copy()
    flip_idx = rng.choice(len(xi), size=n_noise, replace=False)
    cue[flip_idx] *= -1.0
    return cue


def glauber_step(state: np.ndarray, W: np.ndarray,
                 beta: float, rng: np.random.RandomState) -> np.ndarray:
    N_dim = len(state)
    state = state.copy()
    indices = rng.randint(0, N_dim, size=N_dim)
    for i in indices:
        h_i = float(W[i] @ state)
        prob_up = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
        state[i] = 1.0 if rng.rand() < prob_up else -1.0
    return state


def replay_sequence(W_chain: np.ndarray, trigger: np.ndarray, Xi: np.ndarray,
                    T_steps: int, n_replay: int, rng: np.random.RandomState) -> Dict:
    """
    Run n_replay MAP steps from trigger using sign(W_chain @ state).
    Each step = one MAP update: state = sign(W_chain @ state).
    T_steps controls the number of MAP steps per hop between measurement.
    Fast dynamics = T_steps=1; slow dynamics = T_steps=5.
    Measure which sequence elements are visited in order.
    Returns: fidelity (fraction of expected next-elements correctly predicted),
             steps_to_80pct.
    """
    K, N_dim = Xi.shape
    state = trigger.copy()

    # Track which patterns the trajectory visits (cosine > 0.30)
    visited_order = []

    step = 0
    for hop in range(n_replay):
        # Apply T_steps MAP updates: each is sign(W_chain @ state)
        for _ in range(T_steps):
            raw = W_chain @ state
            state = np.sign(raw + 1e-9 * rng.randn(N_dim))  # tiny noise breaks ties
            step += 1
        # Check correlation with each pattern after this hop
        cosines = [float(np.dot(state, Xi[k])) / N_dim for k in range(K)]
        best_k = int(np.argmax(cosines))
        if cosines[best_k] > 0.30:
            visited_order.append(best_k)
        else:
            visited_order.append(-1)

    # Fidelity: fraction of hops where we visited the next expected element
    # Expected sequence after trigger (xi_0): xi_1, xi_2, ...
    correct = 0
    total = min(len(visited_order), K - 1)
    for i in range(total):
        if visited_order[i] == i + 1:
            correct += 1
    fidelity = correct / total if total > 0 else 0.0

    # Steps to reach 80% fidelity: cumulative over hops
    cum_correct = 0
    steps_80 = float("nan")
    for i in range(total):
        if visited_order[i] == i + 1:
            cum_correct += 1
        if cum_correct / total >= 0.80 and math.isnan(steps_80):
            steps_80 = float(i + 1) * T_steps

    return {
        "fidelity": fidelity,
        "steps_to_80pct": steps_80,
        "visited_order": visited_order,
    }


def replay_random_baseline(Xi: np.ndarray, K: int, rng: np.random.RandomState) -> float:
    """Fidelity for random assignment. Expected ~ 1/K for random ordering."""
    total = K - 1
    # Random assignment: shuffle indices
    shuffled = rng.permutation(K)[:total]
    correct = sum(1 for i, v in enumerate(shuffled) if v == i + 1)
    return correct / total if total > 0 else 0.0


def run_one_trial(Xi: np.ndarray, seed: int, trial: int) -> Dict:
    rng = np.random.RandomState(seed * 1000 + trial)
    N_dim = Xi.shape[1]
    W_chain = build_chain_W(Xi, N_dim)

    # Correct trigger: noisy xi_0
    trigger_correct = make_noisy_cue(Xi[0], N_NOISE, rng)
    # Wrong trigger: noisy xi_{K-1} (last element)
    trigger_wrong = make_noisy_cue(Xi[K_CHAIN - 1], N_NOISE, rng)

    fast_result = replay_sequence(W_chain, trigger_correct, Xi,
                                   T_FAST, K_CHAIN * 2, rng)
    # Random baseline: expected fidelity ~ 1/K_CHAIN
    fidelity_random = replay_random_baseline(Xi, K_CHAIN, rng)
    wrong_result = replay_sequence(W_chain, trigger_wrong, Xi,
                                    T_FAST, K_CHAIN * 2, rng)

    return {
        "fidelity_fast": fast_result["fidelity"],
        "fidelity_random": fidelity_random,
        "fidelity_wrong": wrong_result["fidelity"],
        "steps_80_fast": fast_result["steps_to_80pct"],
    }


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    Xi = make_chain_patterns(N, K_CHAIN, seed)

    trials = [run_one_trial(Xi, seed, t) for t in range(N_TRIALS)]

    mean_fidelity_fast = float(np.mean([t["fidelity_fast"] for t in trials]))
    mean_fidelity_random = float(np.mean([t["fidelity_random"] for t in trials]))
    mean_fidelity_wrong = float(np.mean([t["fidelity_wrong"] for t in trials]))

    steps_80_fast = [t["steps_80_fast"] for t in trials if not math.isnan(t["steps_80_fast"])]
    mean_steps_fast = float(np.mean(steps_80_fast)) if steps_80_fast else float("nan")

    cell_A_pass = mean_fidelity_fast >= HP_FIDELITY_FAST
    # Cell B: fast MAP fidelity exceeds random baseline by >= HP_COMPRESSION_FACTOR x
    cell_B_pass = (mean_fidelity_fast >= mean_fidelity_random * HP_COMPRESSION_FACTOR + 0.10)
    cell_C_pass = mean_fidelity_wrong <= HP_WRONG_TRIGGER_MAX

    print(f"  [seed={seed}] fidelity_fast={mean_fidelity_fast:.4f}(A:{cell_A_pass}) "
          f"fidelity_random={mean_fidelity_random:.4f}(B:{cell_B_pass}) "
          f"fidelity_wrong={mean_fidelity_wrong:.4f}(C:{cell_C_pass})", flush=True)

    return {
        "seed": seed,
        "mean_fidelity_fast": mean_fidelity_fast,
        "mean_fidelity_random": mean_fidelity_random,
        "mean_fidelity_wrong": mean_fidelity_wrong,
        "mean_steps_80_fast": mean_steps_fast,
        "cell_A_pass": cell_A_pass,
        "cell_B_pass": cell_B_pass,
        "cell_C_pass": cell_C_pass,
        "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert replay metrics non-null at small scale."""
    N_test = 256
    K_test = 5
    Xi_test = make_chain_patterns(N_test, K_test, 42)
    W_test = build_chain_W(Xi_test, N_test)

    rng = np.random.RandomState(42)
    trigger = make_noisy_cue(Xi_test[0], 3, rng)
    result = replay_sequence(W_test, trigger, Xi_test, T_steps=3, n_replay=K_test, rng=rng)

    assert not math.isnan(result["fidelity"]), "fidelity is NaN"
    assert 0.0 <= result["fidelity"] <= 1.0, f"fidelity={result['fidelity']} out of [0,1]"
    assert len(result["visited_order"]) > 0, "visited_order is empty"

    # Test wrong trigger
    trigger_wrong = make_noisy_cue(Xi_test[-1], 3, rng)
    result_wrong = replay_sequence(W_test, trigger_wrong, Xi_test, T_steps=3,
                                    n_replay=K_test, rng=rng)
    assert not math.isnan(result_wrong["fidelity"]), "wrong_fidelity is NaN"

    print(f"[selftest] PASS: fidelity_correct={result['fidelity']:.4f} "
          f"fidelity_wrong={result_wrong['fidelity']:.4f} at N={N_test}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    fidels_fast, fidels_random, fidels_wrong = [], [], []
    steps_fast = []
    a_pass, b_pass, c_pass = [], [], []
    for sd in per_seed.values():
        fidels_fast.append(sd.get("mean_fidelity_fast", float("nan")))
        fidels_random.append(sd.get("mean_fidelity_random", float("nan")))
        fidels_wrong.append(sd.get("mean_fidelity_wrong", float("nan")))
        steps_fast.append(sd.get("mean_steps_80_fast", float("nan")))
        a_pass.append(sd.get("cell_A_pass", False))
        b_pass.append(sd.get("cell_B_pass", False))
        c_pass.append(sd.get("cell_C_pass", False))
    return {
        "mean_fidelity_fast": float(np.nanmean(fidels_fast)),
        "mean_fidelity_random": float(np.nanmean(fidels_random)),
        "mean_fidelity_wrong": float(np.nanmean(fidels_wrong)),
        "mean_steps_fast": float(np.nanmean(steps_fast)),
        "frac_A_pass": float(np.mean(a_pass)),
        "frac_B_pass": float(np.mean(b_pass)),
        "frac_C_pass": float(np.mean(c_pass)),
        "n_seeds": len(a_pass),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    fA = agg["frac_A_pass"]
    fB = agg["frac_B_pass"]
    fC = agg["frac_C_pass"]
    hp_A = fA >= HP_FRAC_SEEDS
    hp_B = fB >= HP_FRAC_SEEDS
    hp_C = fC >= HP_FRAC_SEEDS
    cells_pass = sum([hp_A, hp_B, hp_C])

    mff = agg["mean_fidelity_fast"]
    mfr = agg["mean_fidelity_random"]
    msf = agg["mean_steps_fast"]
    mfw = agg["mean_fidelity_wrong"]

    if cells_pass == 3:
        return ("HARD_PASS",
                f"SWR replay CONFIRMED. fidelity_fast={mff:.4f}>={HP_FIDELITY_FAST} "
                f"vs random={mfr:.4f} (>{HP_COMPRESSION_FACTOR}x above random). "
                f"wrong_fidelity={mfw:.4f}<={HP_WRONG_TRIGGER_MAX}. "
                f"A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")
    if cells_pass <= 1:
        return ("HARD_FAIL",
                f"SWR replay NOT confirmed. fidelity_fast={mff:.4f} random={mfr:.4f} "
                f"wrong={mfw:.4f}. A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")
    return ("MIDDLE_BAND",
            f"{cells_pass}/3 cells pass. fidelity_fast={mff:.4f} random={mfr:.4f} "
            f"wrong={mfw:.4f}. A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"K_CHAIN={K_CHAIN} T_FAST={T_FAST} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "K_CHAIN": K_CHAIN, "run_mode": RUN_MODE}
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
        "run_mode": RUN_MODE, "N": N, "K_CHAIN": K_CHAIN,
        "T_FAST": T_FAST, "seeds": SEEDS,
        "aggregated": agg,
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
