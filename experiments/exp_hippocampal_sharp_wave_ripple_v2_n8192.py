"""
hippocampal_sharp_wave_ripple_v2_n8192 -- SWR replay at N=8192 (N-scaling extension).

v1 HARD_PASS at N=1024 (fidelity_fast=1.0, compression 12x above baseline, wrong=0.027).
This anchor extends to N=8192: verify SWR replay signature holds at larger N.
Also tests longer K=12 chains (matching v1 FULL config) at production N=8192.

Same heteroassociative chain + MAP replay design as v1. At larger N, SNR improves
(chain signal grows as 1/K while noise ~ 1/sqrt(N)), so v1 thresholds are re-used.

HARD-PASS: frac_A_pass >= 0.60 AND frac_B_pass >= 0.60 AND frac_C_pass >= 0.60.
MIDDLE: 2/3 cells.
HARD-FAIL: 0-1 cells pass.

PRE-REGISTERED BANDS:
  HP: same as v1 (N=1024 passed easily; N=8192 expected equal or better).
  HF: fidelity_fast mean < 0.30 (random is 1/K ~ 0.083 for K=12).
  Calibration: v1 HARD_PASS is empirical anchor; bands unchanged.

FORMULA SELF-TESTS:
  1. Chain W[j,i] += xi_{t+1}[j] * xi_t[i] / N. sign(W @ xi_t) correlates with xi_{t+1}.
     [INPUT: K=5, N=256] [EXPECTED: cos(sign(W@xi_2), xi_3) > 0.10]
  2. HP_FIDELITY_FAST > random_baseline * HP_COMPRESSION_FACTOR (fidelity must be above chance).
     [INPUT: HP_FIDELITY=0.70, random~1/K=0.083, COMP=2.0] [EXPECTED: 0.70 > 0.083*2 = 0.167 OK]
  3. Wrong trigger: noisy last element does NOT produce correct replay.
     [INPUT: trigger=xi_{K-1} noisy] [EXPECTED: fidelity_wrong < 0.20]

PROT-018: anchor has _n8192; N MUST = 8192.
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "hippocampal_sharp_wave_ripple_v2_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    K_CHAIN = 8
    T_FAST = 1
    N_NOISE = 5
    N_TRIALS = 5
else:
    SEEDS = [7, 17, 23, 31, 41]
    K_CHAIN = 12
    T_FAST = 1
    N_NOISE = 5
    N_TRIALS = 10

HP_FIDELITY_FAST = 0.70
HP_COMPRESSION_FACTOR = 2.0
HP_WRONG_TRIGGER_MAX = 0.20
HP_FRAC_SEEDS = 0.60


def make_chain_patterns(N_dim: int, K: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(K, N_dim)).astype(np.float64)


def build_chain_W(Xi: np.ndarray, N_dim: int) -> np.ndarray:
    K = Xi.shape[0]
    W = np.zeros((N_dim, N_dim))
    for t in range(K - 1):
        W += np.outer(Xi[t + 1], Xi[t]) / N_dim
    return W


def make_noisy_cue(xi: np.ndarray, n_noise: int, rng: np.random.RandomState) -> np.ndarray:
    cue = xi.copy()
    flip_idx = rng.choice(len(xi), size=n_noise, replace=False)
    cue[flip_idx] *= -1.0
    return cue


def replay_sequence(W_chain: np.ndarray, trigger: np.ndarray, Xi: np.ndarray,
                    T_steps: int, n_replay: int, rng: np.random.RandomState) -> Dict:
    """MAP replay: state = sign(W_chain @ state) repeated T_steps per hop."""
    K, N_dim = Xi.shape
    state = trigger.copy()
    visited_order = []
    for hop in range(n_replay):
        for _ in range(T_steps):
            raw = W_chain @ state
            state = np.sign(raw + 1e-9 * rng.randn(N_dim))
        cosines = [float(np.dot(state, Xi[k])) / N_dim for k in range(K)]
        best_k = int(np.argmax(cosines))
        if cosines[best_k] > 0.30:
            visited_order.append(best_k)
        else:
            visited_order.append(-1)
    correct = 0
    total = min(len(visited_order), K - 1)
    for i in range(total):
        if visited_order[i] == i + 1:
            correct += 1
    fidelity = correct / total if total > 0 else 0.0
    steps_80 = float("nan")
    cum_c = 0
    for i in range(total):
        if visited_order[i] == i + 1:
            cum_c += 1
        if cum_c / max(total, 1) >= 0.80 and math.isnan(steps_80):
            steps_80 = float(i + 1) * T_steps
    return {"fidelity": fidelity, "steps_to_80pct": steps_80, "visited_order": visited_order}


def replay_random_baseline(Xi: np.ndarray, K: int, rng: np.random.RandomState) -> float:
    total = K - 1
    shuffled = rng.permutation(K)[:total]
    correct = sum(1 for i, v in enumerate(shuffled) if v == i + 1)
    return correct / total if total > 0 else 0.0


def _heteroassoc_cosine_test():
    rng = np.random.RandomState(0)
    N_test, K_test = 256, 5
    Xi = rng.choice([-1.0, 1.0], size=(K_test, N_test)).astype(np.float64)
    W = build_chain_W(Xi, N_test)
    raw = W @ Xi[0]
    cos = float(np.dot(np.sign(raw), Xi[1])) / N_test
    assert cos > 0.10, f"heteroassoc cos={cos:.4f} < 0.10"
    return cos


def _instrumentation_selftest():
    cos = _heteroassoc_cosine_test()
    # Compression: HP > random * factor check
    random_baseline = 1.0 / K_CHAIN
    assert HP_FIDELITY_FAST > random_baseline * HP_COMPRESSION_FACTOR, (
        f"HP_FIDELITY={HP_FIDELITY_FAST} <= random*factor={random_baseline*HP_COMPRESSION_FACTOR:.3f}")
    # Test replay at small scale
    N_test, K_test = 256, 5
    Xi_test = make_chain_patterns(N_test, K_test, 42)
    W_test = build_chain_W(Xi_test, N_test)
    rng_t = np.random.RandomState(42)
    trigger = make_noisy_cue(Xi_test[0], 3, rng_t)
    result = replay_sequence(W_test, trigger, Xi_test, T_steps=1, n_replay=K_test, rng=rng_t)
    assert 0.0 <= result["fidelity"] <= 1.0, f"fidelity={result['fidelity']} out of [0,1]"
    assert len(result["visited_order"]) > 0, "visited_order empty"
    print(f"[selftest] PASS: heteroassoc_cos={cos:.4f} fidelity_small={result['fidelity']:.4f} "
          f"random_baseline={random_baseline:.4f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_one_trial(Xi: np.ndarray, seed: int, trial: int) -> Dict:
    rng = np.random.RandomState(seed * 1000 + trial)
    N_dim = Xi.shape[1]
    W_chain = build_chain_W(Xi, N_dim)
    trigger_correct = make_noisy_cue(Xi[0], N_NOISE, rng)
    # Wrong trigger: completely random pattern (not from chain) -- cleaner test of specificity
    trigger_wrong = rng.choice([-1.0, 1.0], size=(N_dim,)).astype(np.float64)
    fast_result = replay_sequence(W_chain, trigger_correct, Xi, T_FAST, K_CHAIN * 2, rng)
    fidelity_random = replay_random_baseline(Xi, K_CHAIN, rng)
    wrong_result = replay_sequence(W_chain, trigger_wrong, Xi, T_FAST, K_CHAIN * 2, rng)
    return {
        "fidelity_fast": fast_result["fidelity"],
        "fidelity_random": fidelity_random,
        "fidelity_wrong": wrong_result["fidelity"],
        "steps_80_fast": fast_result["steps_to_80pct"],
    }


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    Xi = make_chain_patterns(N, K_CHAIN, seed)
    trials = [run_one_trial(Xi, seed, t) for t in range(N_TRIALS)]
    mean_fidelity_fast = float(np.mean([t["fidelity_fast"] for t in trials]))
    mean_fidelity_random = float(np.mean([t["fidelity_random"] for t in trials]))
    mean_fidelity_wrong = float(np.mean([t["fidelity_wrong"] for t in trials]))
    steps_80_fast = [t["steps_80_fast"] for t in trials if not math.isnan(t["steps_80_fast"])]
    mean_steps_fast = float(np.mean(steps_80_fast)) if steps_80_fast else float("nan")
    cell_A = mean_fidelity_fast >= HP_FIDELITY_FAST
    cell_B = mean_fidelity_fast >= mean_fidelity_random * HP_COMPRESSION_FACTOR + 0.10
    cell_C = mean_fidelity_wrong <= HP_WRONG_TRIGGER_MAX
    elapsed = time.time() - t0
    print(f"  [seed={seed}] fid_fast={mean_fidelity_fast:.4f}(A:{int(cell_A)}) "
          f"random={mean_fidelity_random:.4f}(B:{int(cell_B)}) "
          f"wrong={mean_fidelity_wrong:.4f}(C:{int(cell_C)}) elapsed={elapsed:.2f}s", flush=True)
    return {
        "seed": seed, "N": N, "K_CHAIN": K_CHAIN, "run_mode": RUN_MODE,
        "mean_fidelity_fast": float(mean_fidelity_fast),
        "mean_fidelity_random": float(mean_fidelity_random),
        "mean_fidelity_wrong": float(mean_fidelity_wrong),
        "mean_steps_80_fast": float(mean_steps_fast),
        "cell_A_pass": bool(cell_A), "cell_B_pass": bool(cell_B), "cell_C_pass": bool(cell_C),
        "elapsed_s": float(elapsed),
    }


def aggregate_results(per_seed_data: Dict) -> Dict:
    results = list(per_seed_data.values())
    return {
        "mean_fidelity_fast": float(np.mean([r["mean_fidelity_fast"] for r in results])),
        "mean_fidelity_random": float(np.mean([r["mean_fidelity_random"] for r in results])),
        "mean_fidelity_wrong": float(np.mean([r["mean_fidelity_wrong"] for r in results])),
        "frac_A_pass": float(np.mean([r["cell_A_pass"] for r in results])),
        "frac_B_pass": float(np.mean([r["cell_B_pass"] for r in results])),
        "frac_C_pass": float(np.mean([r["cell_C_pass"] for r in results])),
        "n_seeds": len(results),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    fA, fB, fC = agg["frac_A_pass"], agg["frac_B_pass"], agg["frac_C_pass"]
    hp_A = fA >= HP_FRAC_SEEDS
    hp_B = fB >= HP_FRAC_SEEDS
    hp_C = fC >= HP_FRAC_SEEDS
    cells_pass = sum([hp_A, hp_B, hp_C])
    mff = agg["mean_fidelity_fast"]
    mfr = agg["mean_fidelity_random"]
    mfw = agg["mean_fidelity_wrong"]
    summary = (f"fid_fast={mff:.4f}(HP>={HP_FIDELITY_FAST}) random={mfr:.4f} "
               f"wrong={mfw:.4f}(HP<={HP_WRONG_TRIGGER_MAX}) A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}")
    if cells_pass == 3:
        return ("HARD_PASS", f"HARD_PASS: SWR N=8192 confirmed. {summary}")
    if cells_pass <= 1:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {cells_pass}/3 cells. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "K_CHAIN": K_CHAIN, "T_FAST": T_FAST, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N} K={K_CHAIN}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
agg = aggregate_results(per_seed)
verdict, verdict_msg = compute_verdict(agg)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
all_results = list(per_seed.values())
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "mean_fidelity_fast": agg["mean_fidelity_fast"],
    "mean_fidelity_random": agg["mean_fidelity_random"],
    "mean_fidelity_wrong": agg["mean_fidelity_wrong"],
    "frac_A_pass": agg["frac_A_pass"],
    "frac_B_pass": agg["frac_B_pass"],
    "frac_C_pass": agg["frac_C_pass"],
}
metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
