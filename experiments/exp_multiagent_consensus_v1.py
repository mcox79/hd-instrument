"""
multiagent_consensus_v1 -- Multiagent coordination: consensus via substrate voting.

SCIENTIFIC QUESTION (from multiagent coordination handoff -- beyond write pressure):
  Can the substrate implement a multi-agent consensus protocol where multiple agents
  write partial beliefs into separate W matrices, and consensus is reached by
  superimposing (averaging) the W matrices?

  Mechanism: K agents each observe partial evidence and write their belief patterns
  into their own W_k matrix. Consensus: W_consensus = (1/K) * sum_k W_k.
  Query on W_consensus: does the majority pattern emerge with higher similarity
  than minority patterns?

  Prediction: if >50% of agents write pattern xi_majority, then W_consensus @ query
  retrieves xi_majority with higher dot product than xi_minority patterns written by
  <50% of agents.

  Two cells:
  (A) Majority consensus: K=5 agents, 3 write xi_majority, 2 write xi_minority.
      HP: majority pattern wins in >= 90% of seeds (sim_maj > sim_min).
  (B) Near-consensus: K=7 agents, 4 write xi_majority, 3 write xi_minority.
      HP: majority pattern wins in >= 85% of seeds.

PRE-REGISTERED BANDS:
  HARD-PASS: majority_win_rate >= 0.85 for both cells (A and B).
  MIDDLE: 0.65 <= majority_win_rate < 0.85 for at least one cell.
  HARD-FAIL: majority_win_rate < 0.65 for cell A (majority 3/5 does not win).

Calibration probe note: no prior substrate-consensus anchor. Theory: W_consensus
has coefficient (3/5) for majority and (2/5) for minority. Signal ratio = (3/5)/(2/5) = 1.5.
At N=4096, cross-terms average to ~0, so majority should dominate reliably.

FORMULA SELF-TESTS:
  1. W_consensus = (3*W_maj + 2*W_min) / 5. Retrieval sim for xi_maj:
     xi_maj^T W_consensus xi_maj = (3/5) * xi_maj^T W_maj xi_maj + (2/5) * xi_maj^T W_min xi_maj
     ~ (3/5) * M_maj/N + (2/5) * 0 (cross term) = (3/5) * 1 = 0.6 (one pattern each agent).
  2. For xi_min: sim = (3/5)*cross + (2/5)*1 = (3/5)*0 + 0.4 = 0.4.
  3. Ratio 0.6/0.4 = 1.5 -> majority always wins at infinite N.

TIMEOUT ESTIMATE:
  Smoke: N=4096, M_patterns=20 per agent, 2 seeds.
  Full: N=4096, M_patterns=50 per agent, 5 seeds.
  Each W build O(M*N). Smoke wall ~5s -> Full ~20s -> timeout=150s.
  No _nN suffix; production N=4096.
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
from typing import Dict, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "multiagent_consensus_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_PER_AGENT = 20
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_PER_AGENT = 50

# Cell A: K=5 agents, 3 majority, 2 minority
K_A = 5; MAJ_A = 3; MIN_A = 2
# Cell B: K=7 agents, 4 majority, 3 minority
K_B = 7; MAJ_B = 4; MIN_B = 3

# Pre-reg thresholds
HP_WIN_RATE = 0.85
MID_WIN_RATE = 0.65
HF_WIN_RATE = 0.65

# Formula self-test: majority ratio theory
_ratio_A = MAJ_A / K_A / (MIN_A / K_A)
assert abs(_ratio_A - 1.5) < 0.01, f"theory ratio A: {_ratio_A}"


def build_agent_w(M: int, N: int, seed: int) -> np.ndarray:
    """Agent W = Xi^T Xi / N (one agent's observed patterns)."""
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    return (Xi.T @ Xi) / N


def run_cell(K: int, n_maj: int, n_min: int, M: int, N: int, seed: int) -> Tuple[bool, float, float]:
    """
    Build W_consensus from K agents.
    First n_maj agents write xi_maj, remaining n_min agents write xi_min.
    Check if W_consensus @ xi_maj has higher dot product than W_consensus @ xi_min.
    Returns (majority_wins, sim_maj, sim_min).
    """
    rng = np.random.RandomState(seed)
    # The "contested" pattern pair
    xi_maj = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
    xi_min = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)

    W_total = np.zeros((N, N), dtype=np.float64)
    for k in range(K):
        agent_seed = seed * 1000 + k
        agent_rng = np.random.RandomState(agent_seed)
        # Each agent writes M-1 background patterns + the contested pattern
        background = agent_rng.choice([-1.0, 1.0], size=(M - 1, N)).astype(np.float64)
        if k < n_maj:
            contested = xi_maj.reshape(1, N)
        else:
            contested = xi_min.reshape(1, N)
        Xi = np.vstack([background, contested])
        W_k = (Xi.T @ Xi) / N
        W_total += W_k

    W_consensus = W_total / K

    sim_maj = float(np.dot(W_consensus @ xi_maj, xi_maj))
    sim_min = float(np.dot(W_consensus @ xi_min, xi_min))
    majority_wins = sim_maj > sim_min
    return majority_wins, sim_maj, sim_min


def run_seed(seed: int) -> Dict:
    # Cell A: K=5, 3 majority
    maj_a, wW_a, sW_a = run_cell(K_A, MAJ_A, MIN_A, M_PER_AGENT, N, seed)
    print(f"  [seed={seed} cell=A K={K_A} maj={MAJ_A}] "
          f"wins={maj_a} sim_maj={wW_a:.4f} sim_min={sW_a:.4f}", flush=True)

    # Cell B: K=7, 4 majority
    maj_b, wW_b, sW_b = run_cell(K_B, MAJ_B, MIN_B, M_PER_AGENT, N, seed + 100)
    print(f"  [seed={seed} cell=B K={K_B} maj={MAJ_B}] "
          f"wins={maj_b} sim_maj={wW_b:.4f} sim_min={sW_b:.4f}", flush=True)

    return {
        "cell_A_win": int(maj_a), "cell_A_sim_maj": wW_a, "cell_A_sim_min": sW_a,
        "cell_B_win": int(maj_b), "cell_B_sim_maj": wW_b, "cell_B_sim_min": sW_b,
        "seed": seed, "N": N, "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert consensus mechanism produces non-trivial majority signal."""
    N_t = 512
    seed = 42
    maj_win, sim_maj, sim_min = run_cell(5, 3, 2, 10, N_t, seed)
    assert not math.isnan(sim_maj), "sim_maj is NaN"
    assert not math.isnan(sim_min), "sim_min is NaN"
    # At N=512, M=10, majority 3/5 should typically win
    # Don't assert winner (finite N, random) -- just assert signals are non-null
    assert sim_maj > 0, f"sim_maj <= 0: {sim_maj}"
    assert sim_min > 0, f"sim_min <= 0: {sim_min}"
    print(f"[selftest] PASS: cell_A sim_maj={sim_maj:.4f} sim_min={sim_min:.4f} "
          f"majority_wins={maj_win}", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    ratio = MAJ_A / K_A / (MIN_A / K_A)
    assert abs(ratio - 1.5) < 0.01, f"consensus ratio formula: {ratio}"
    print("[formula_selftests] PASS: consensus voting formula verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    wins_A = []
    wins_B = []
    for sd in per_seed.values():
        wins_A.append(sd["cell_A_win"])
        wins_B.append(sd["cell_B_win"])
    return {
        "cell_A_win_rate": float(np.mean(wins_A)) if wins_A else float("nan"),
        "cell_B_win_rate": float(np.mean(wins_B)) if wins_B else float("nan"),
        "n_seeds": len(wins_A),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    wr_A = agg["cell_A_win_rate"]
    wr_B = agg["cell_B_win_rate"]
    if math.isnan(wr_A):
        return ("HARD_FAIL", "cell_A win_rate is NaN.")
    both_hp = wr_A >= HP_WIN_RATE and wr_B >= HP_WIN_RATE
    a_hf = wr_A < HF_WIN_RATE
    if both_hp:
        return ("HARD_PASS",
                f"Multiagent consensus confirmed. cell_A win_rate={wr_A:.3f} "
                f"cell_B win_rate={wr_B:.3f} (both HP>={HP_WIN_RATE}). "
                f"Substrate W-averaging implements majority vote protocol.")
    if a_hf:
        return ("HARD_FAIL",
                f"No majority consensus. cell_A win_rate={wr_A:.3f} < HF {HF_WIN_RATE}.")
    return ("MIDDLE_BAND",
            f"Partial consensus. cell_A={wr_A:.3f} cell_B={wr_B:.3f} "
            f"(HP>={HP_WIN_RATE}, HF<{HF_WIN_RATE}).")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"M_per_agent={M_PER_AGENT} seeds={SEEDS}", flush=True)

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
        "run_mode": RUN_MODE, "N": N, "M_per_agent": M_PER_AGENT, "seeds": SEEDS,
        "cells": {"A": {"K": K_A, "maj": MAJ_A, "min": MIN_A},
                  "B": {"K": K_B, "maj": MAJ_B, "min": MIN_B}},
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
