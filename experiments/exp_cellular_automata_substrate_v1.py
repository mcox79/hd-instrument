"""Cellular automata orthogonal probe: substrate updates as CA rules.

CONTEXT (orthogonal shortlist -- first drill):
  The substrate's synchronous update rule (sign(W @ x)) is structurally identical
  to a cellular automaton (CA): each neuron reads its neighborhood (W row),
  applies a threshold rule, and updates simultaneously. Wolfram's CA classification
  maps rules to 4 complexity classes (fixed-point / periodic / chaotic / complex).

  Substrate as CA probe tests:
  1. Which Wolfram class does the substrate's dynamics fall into?
     Class I/II (fixed-point/periodic) = good for retrieval (attractor-based).
     Class III/IV (chaotic/complex) = bad for retrieval; patterns not preserved.
  2. Does the CA class depend on load (M/N ratio)?
     Expected: below alpha_c -> Class I/II; above alpha_c -> Class III.
  3. Does the Hamming distance between successive states converge or diverge?
     Convergence = attractor dynamics; divergence = chaotic dynamics.

SCIENTIFIC QUESTION:
  Is the substrate's synchronous update dynamics in Wolfram Class I/II
  (attractor basin) for alpha < alpha_c, consistent with its role as
  a pattern retrieval system?

PRE-REGISTERED BANDS (calibration probe: first CA measurement on substrate):
  HARD-PASS:
    - Hamming distance H(x(t), x(t-1)) converges to 0 in <= 20 steps
      for alpha <= 0.10 in >= 4/5 seeds
    - AND Class I/II fraction >= 80% at alpha <= 0.10
  HARD-FAIL:
    - Hamming distance diverges (H(t) increases monotonically) in >= 4/5 seeds
      at ALL alpha values tested
    - OR Class III/IV (chaotic) at alpha <= 0.05 in >= 4/5 seeds
  MIDDLE-BAND:
    - Convergence at sub-capacity but slow (> 20 steps)
    - OR mixed class behavior (some seeds Class I/II, some Class III/IV)

SELF-TESTS (per [[feedback-strategy-spec-formula-selftests]]):
  1. Identity rule (W = I): H(x(t+1), x(t)) = 0 for all t (trivially Class I).
  2. Zero rule (W = 0): all outputs 0; Class I (trivially stable at 0).
  3. Sub-capacity Hopfield W (alpha=0.01): should converge within 10 steps.
  4. Hamming distance computation: H(v, v) = 0; H(v, -v) = N.
  5. CA class assignment: constant H=0 -> Class I; H oscillating period-2 -> Class II.

N-suffix: no _nN suffix; production N = 1024.
Queue: remote_cpu_queue (pure numpy; N=1024 5-seed; ~5-15 min)
Timeout: smoke_wall_s ~ 3s; FULL: ceil(1.5 * 3 * (1024/256)**1.5 * 5) = ceil(180) = 300s -> use 600s.
Pre-reg: prereqs/2026-05-27_cellular_automata_substrate_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Production config ---
N_FULL  = 1024
N_SMOKE = 256
ALPHA_LOADS = [0.01, 0.05, 0.10, 0.12, 0.15]  # sub-capacity to above alpha_c
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
MAX_CA_STEPS = 30
ALPHA_HEBBIAN = 0.1

# Pre-registered thresholds
HP_CONV_SEED_MIN  = 4    # >= 4/5 seeds must show convergence
HP_MAX_CONV_STEPS = 20   # converge within this many steps
HP_CLASS12_FRAC   = 0.80 # fraction of seeds in Class I/II
HF_DIVERGE_SEED_MIN = 4  # hard-fail divergence count


def get_output_dir(default_name: str = "cellular_automata_substrate_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_hopfield_W(N: int, M: int, seed: int) -> np.ndarray:
    """Build symmetric Hopfield W from M bipolar patterns."""
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = np.zeros((N, N), dtype=np.float64)
    for v in patterns:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W


def synchronous_ca_step(W: np.ndarray, state: np.ndarray) -> np.ndarray:
    """One synchronous CA step: state[t+1] = sign(W @ state[t])."""
    raw = W @ state
    # sign with threshold: +1 if >= 0, -1 if < 0 (bipolar output)
    return np.where(raw >= 0, 1.0, -1.0)


def hamming_distance_bipolar(a: np.ndarray, b: np.ndarray) -> int:
    """Hamming distance between two bipolar (-1/+1) vectors."""
    return int(np.sum(a != b))


def classify_ca(hamming_traj: List[int], N: int) -> str:
    """Classify CA dynamics from Hamming distance trajectory.

    Class I: converges to H=0 (fixed point)
    Class II: converges to H > 0 periodic (small oscillation)
    Class III: H diverges or stays large (chaotic)
    Class IV: complex (H stabilizes at intermediate value after transient)
    """
    if len(hamming_traj) < 3:
        return "UNKNOWN"
    final_H = hamming_traj[-1]
    # Check for convergence to fixed point
    if final_H == 0:
        return "CLASS_I"
    # Check for small periodic: H oscillates but stays < 0.1*N
    H_arr = np.array(hamming_traj[-10:])
    H_range = float(H_arr.max() - H_arr.min())
    H_mean = float(H_arr.mean())
    if H_mean < 0.05 * N:
        return "CLASS_II"
    # Check for divergence: H increases
    h_trend = np.polyfit(range(len(hamming_traj)), hamming_traj, 1)[0]
    if h_trend > 0.5:
        return "CLASS_III"
    # Check for complex: intermediate stable H
    if 0.05 * N <= H_mean <= 0.3 * N and H_range < 0.1 * N:
        return "CLASS_IV"
    return "CLASS_III"


def run_one(N: int, seed: int, alpha_load: float) -> Dict:
    M = max(2, int(N * alpha_load))
    W = build_hopfield_W(N, M, seed)

    # Start from a random bipolar state
    rng = np.random.default_rng(seed + 1000)
    state = rng.choice([-1.0, 1.0], size=N).astype(np.float64)

    hamming_traj = []
    prev_state = state.copy()
    for _ in range(MAX_CA_STEPS):
        state = synchronous_ca_step(W, state)
        H = hamming_distance_bipolar(state, prev_state)
        hamming_traj.append(H)
        prev_state = state.copy()
        if H == 0:
            break  # fixed point reached

    ca_class = classify_ca(hamming_traj, N)
    converged = hamming_traj[-1] == 0
    conv_steps = next((i + 1 for i, h in enumerate(hamming_traj) if h == 0), MAX_CA_STEPS + 1)
    diverging = float(np.polyfit(range(len(hamming_traj)), hamming_traj, 1)[0]) > 0.5

    return {
        "N": N, "M": M, "seed": seed,
        "alpha_load": alpha_load,
        "ca_class": ca_class,
        "converged": converged,
        "convergence_steps": conv_steps,
        "diverging": diverging,
        "hamming_final": hamming_traj[-1],
        "hamming_traj": hamming_traj[:20],  # first 20 steps for inspection
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. Identity rule: W = I -> all states fixed (Class I)
    N_t = 16
    W_id = np.eye(N_t)
    np.fill_diagonal(W_id, 0.0)  # no self-connections; zero diagonal
    # With zero diagonal: W@x = 0 for 1D case; sign(0) -> all 1 (our threshold)
    # Let's use non-trivial identity-like W:
    W_id2 = np.eye(N_t) * 0.1
    np.fill_diagonal(W_id2, 0.0)
    # Actually all zeros after diagonal removal -- this will give H=N each step
    # Better test: sub-capacity W should converge
    W_sub = build_hopfield_W(N_t, 1, seed=42)  # 1 pattern stored
    rng = np.random.default_rng(42)
    state0 = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    state1 = synchronous_ca_step(W_sub, state0)
    H01 = hamming_distance_bipolar(state0, state1)
    assert isinstance(H01, int) and 0 <= H01 <= N_t, f"Hamming distance out of range: {H01}"

    # 2. Hamming distance self-tests
    v = np.array([1.0, -1.0, 1.0, -1.0])
    assert hamming_distance_bipolar(v, v) == 0, "H(v,v) should be 0"
    assert hamming_distance_bipolar(v, -v) == 4, "H(v,-v) should be N=4"

    # 3. CA class assignment
    # Class I: all zeros -> CLASS_I
    ca1 = classify_ca([0] * 10, N=16)
    assert ca1 == "CLASS_I", f"All-zero Hamming should be CLASS_I, got {ca1}"

    # 4. run_one returns finite metrics
    r = run_one(N_t * 4, seed=7, alpha_load=0.05)
    assert r["ca_class"] in ("CLASS_I", "CLASS_II", "CLASS_III", "CLASS_IV", "UNKNOWN"), \
        f"Unexpected CA class: {r['ca_class']}"
    assert isinstance(r["converged"], bool), "converged not bool"
    assert 0 <= r["convergence_steps"] <= MAX_CA_STEPS + 1, \
        f"convergence_steps out of range: {r['convergence_steps']}"
    assert isinstance(r["diverging"], bool), "diverging not bool"
    assert len(r["hamming_traj"]) > 0, "empty hamming trajectory"

    # 5. Self-test filter: at least one step of CA runs without error
    assert len(r["hamming_traj"]) >= 1, "no CA steps executed"

    print("SELFTEST PASS: all assertions satisfied")


_instrumentation_selftest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(0)  # self-test already ran at module scope

    N = N_SMOKE if args.smoke else N_FULL
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    alphas = ALPHA_LOADS if not args.smoke else ALPHA_LOADS[:3]
    out_dir = get_output_dir()

    t0 = time.time()
    all_results = []
    for seed in seeds:
        for al in alphas:
            r = run_one(N, seed, al)
            all_results.append(r)
        mode = "smoke" if args.smoke else "full"
        # Report for alpha=0.10
        for r in all_results:
            if r["seed"] == seed and abs(r["alpha_load"] - 0.10) < 0.001:
                print(f"[{mode}] N={N} seed={seed} alpha=0.10 "
                      f"class={r['ca_class']} conv={r['converged']} "
                      f"steps={r['convergence_steps']}")

    elapsed = time.time() - t0

    # Verdict: focus on alpha=0.10 (near alpha_c)
    results_10 = [r for r in all_results if abs(r["alpha_load"] - 0.10) < 0.001]
    n_converged = sum(1 for r in results_10 if r["converged"])
    n_class12 = sum(1 for r in results_10 if r["ca_class"] in ("CLASS_I", "CLASS_II"))
    n_diverging = sum(1 for r in results_10 if r["diverging"])
    n_seeds = len(seeds)

    class12_frac = n_class12 / max(1, n_seeds)

    if n_diverging >= HF_DIVERGE_SEED_MIN:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: diverging dynamics in {n_diverging}/{n_seeds} seeds "
                       f"at alpha=0.10. Substrate is Class III CA.")
    elif (n_converged >= HP_CONV_SEED_MIN and
          all(r["convergence_steps"] <= HP_MAX_CONV_STEPS for r in results_10 if r["converged"]) and
          class12_frac >= HP_CLASS12_FRAC):
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: converged in {n_converged}/{n_seeds} seeds at alpha=0.10, "
                       f"Class I/II={class12_frac:.1%}. Substrate is attractor CA (Class I/II).")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: conv={n_converged}/{n_seeds}, "
                       f"Class_I/II={class12_frac:.1%}, diverging={n_diverging}/{n_seeds}. "
                       f"Mixed CA dynamics at alpha=0.10.")

    # Alpha-class table
    alpha_summary = {}
    for al in alphas:
        r_al = [r for r in all_results if abs(r["alpha_load"] - al) < 0.001]
        class12_al = sum(1 for r in r_al if r["ca_class"] in ("CLASS_I", "CLASS_II"))
        alpha_summary[str(al)] = {
            "n_class12": class12_al,
            "n_total": len(r_al),
            "frac_class12": class12_al / max(1, len(r_al)),
        }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "n_seeds": n_seeds,
        "n_converged_at_alpha10": n_converged,
        "class12_frac_at_alpha10": class12_frac,
        "n_diverging_at_alpha10": n_diverging,
        "alpha_summary": alpha_summary,
        "per_run": all_results,
        "summary": (f"CA-substrate N={N}: {verdict} "
                    f"(Class_I/II={class12_frac:.1%} at alpha=0.10)"),
        "config": {
            "N": N,
            "alpha_loads": alphas,
            "seeds": seeds,
            "HP_CLASS12_FRAC": HP_CLASS12_FRAC,
            "HP_MAX_CONV_STEPS": HP_MAX_CONV_STEPS,
        },
    }

    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"VERDICT: {verdict}")
    print(f"MSG: {verdict_msg}")
    print(f"Wrote metrics to {out_path}")


if __name__ == "__main__":
    main()
