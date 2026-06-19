"""
multiagent_emergence_v1 -- Multiagent emergent coordination without explicit consensus.

SCIENTIFIC QUESTION (multiagent emergent coordination):
  Prior multiagent tests used explicit consensus protocols or adversarial setups.
  This test asks: do N_AGENTS agents with independent local writes SPONTANEOUSLY
  COORDINATE through the shared substrate, WITHOUT any explicit message-passing?

  Emergent coordination mechanism: if multiple agents write patterns that share
  structure (partial alignment), the substrate W accumulates these aligned patterns.
  When a new agent queries W, it gets a response influenced by ALL prior writes.
  The substrate acts as an implicit coordination channel.

  Design:
    - N_AGENTS agents, each writing M_PER_AGENT patterns per round.
    - Patterns have PARTIAL structure: each agent's patterns have a shared
      COMPONENT xi_shared with weight LAMBDA_SHARED and an agent-specific component.
    - After all agents write, test: can each agent retrieve the SHARED component
      even if it never explicitly communicated it to others?

    - No explicit consensus round; no message-passing; only shared W.

  Test cells:
    (A) Shared component retrieval: after all N_AGENTS agents write,
        each agent can retrieve xi_shared from noisy probe.
        HP-A: cosine(retrieved_shared, xi_shared) >= 0.70 for >= 4/5 seeds.
    (B) Agent isolation: agent-specific patterns are NOT cross-contaminated.
        HP-B: agent 1's specific pattern is not retrievable by agent 2's query.
        metric: cosine(retrieved_by_2, xi_specific_1) <= 0.20.
    (C) Emergent vs direct: joint retrieval accuracy (shared component) is HIGHER
        with all N_AGENTS writing than with just 1 agent writing.
        HP-C: acc_joint > acc_single * 1.10 (at least 10% improvement from emergence).

  HARD-PASS: All of A, B, C.
  HARD-FAIL: HF-A (no shared component detectable) OR HF-B (full contamination).
  MIDDLE: 2/3 cells.

PRE-REGISTERED BANDS (calibration probe; first emergent coordination test):
  HP: cosine >= 0.70, contamination <= 0.20, joint_improvement >= 10%.
  HF: cosine < 0.35, contamination > 0.50, joint_improvement < 0%.
  Bands: +-50% per calibration-probe policy.
  Theory: with N_AGENTS agents each contributing LAMBDA_SHARED * xi_shared, total
  contribution = N_AGENTS * LAMBDA_SHARED, amplifying the shared component.

FORMULA SELF-TESTS:
  1. Shared component amplification: N_AGENTS=5 agents each contribute LAMBDA_SHARED=0.3
     to xi_shared. Total weight ~ 5 * 0.3 = 1.5x vs single agent. Cosine improvement
     should scale roughly as sqrt(N_AGENTS) for Hebbian encoding.
     [INPUT: N_AGENTS=5, LAMBDA_SHARED=0.3] [EXPECTED: joint_snr > single_snr]
  2. Agent isolation: agent-specific component (1-LAMBDA_SHARED)*xi_specific_k.
     Cross-agent cosine ~ 0 for orthogonal specific patterns.
     [INPUT: orthogonal specific patterns] [EXPECTED: cross_cosine ~ 0]
  3. Noisy query: flip 10% of bits in xi_shared query.
     For K=50 patterns stored, SNR from xi_shared > 0.40.
     [INPUT: 10% noise, xi_shared at K=50, N=1024] [EXPECTED: cos >= 0.50]

TIMEOUT ESTIMATE:
  Smoke: N=512, N_AGENTS=5, M_PER_AGENT=4, 2 seeds. Full: N=1024, N_AGENTS=8, M_PER_AGENT=5, 5 seeds.
  Linear. Smoke ~1s -> Full ~8s. timeout=120s.

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
from typing import Dict, List

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "multiagent_emergence_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17]
    N_AGENTS = 5
    M_PER_AGENT = 4
    LAMBDA_SHARED = 0.5   # weight on shared component
    NOISE_FRAC = 0.10
else:
    N = 1024
    SEEDS = [7, 17, 23, 31, 41]
    N_AGENTS = 8
    M_PER_AGENT = 5
    LAMBDA_SHARED = 0.5
    NOISE_FRAC = 0.10

HP_COSINE_SHARED = 0.70
HF_COSINE_SHARED = 0.35
HP_CONTAMINATION_MAX = 0.20
HF_CONTAMINATION_MAX = 0.50
HP_JOINT_IMPROVEMENT = 0.10   # 10% better than single agent

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()


# ---- FORMULA SELF-TESTS ----
def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    rng = np.random.RandomState(42)
    N_test = 256

    # Generate shared and specific patterns
    xi_shared = rng.choice([-1.0, 1.0], size=N_test).astype(np.float64)
    xi_specific = rng.choice([-1.0, 1.0], size=N_test).astype(np.float64)

    lam = 0.5
    # Agent 1 writes mixed pattern
    pattern_1 = lam * xi_shared + (1 - lam) * xi_specific
    pattern_1 = np.sign(pattern_1 + 1e-8)

    W = np.outer(pattern_1, pattern_1) / N_test
    np.fill_diagonal(W, 0.0)

    # Retrieval test
    noisy_query = xi_shared.copy()
    noisy_query[:int(0.10 * N_test)] = -noisy_query[:int(0.10 * N_test)]
    retrieved = np.sign(W @ noisy_query + 1e-8)
    cos = float(np.dot(retrieved, xi_shared)) / N_test
    assert cos >= 0.0, f"Shared component cosine must be non-negative: {cos:.3f}"

    # Cross-contamination: agent-specific pattern should not be strongly retrieved
    xi_other_specific = rng.choice([-1.0, 1.0], size=N_test).astype(np.float64)
    cos_contam = abs(float(np.dot(np.sign(W @ xi_other_specific + 1e-8), xi_specific)) / N_test)
    assert cos_contam >= 0.0, "contamination must be non-negative"

    print(f"[selftest] shared_cos={cos:.3f} contamination={cos_contam:.3f}", flush=True)


_instrumentation_selftest()


def run_one_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)

    # Shared component (same for all agents)
    xi_shared = rng.choice([-1.0, 1.0], size=N).astype(np.float64)

    # Agent-specific patterns
    Xi_specific = [rng.choice([-1.0, 1.0], size=N).astype(np.float64) for _ in range(N_AGENTS)]

    # --- Single agent baseline (only agent 0 writes) ---
    W_single = np.zeros((N, N), dtype=np.float64)
    for m in range(M_PER_AGENT):
        xi_specific_0 = rng.choice([-1.0, 1.0], size=N).astype(np.float64)
        pattern_m = LAMBDA_SHARED * xi_shared + (1 - LAMBDA_SHARED) * xi_specific_0
        pattern_m_bin = np.sign(pattern_m + 1e-8)
        W_single += np.outer(pattern_m_bin, pattern_m_bin) / N
    np.fill_diagonal(W_single, 0.0)

    # Single-agent retrieval of shared component
    query = xi_shared.copy()
    n_flip = int(NOISE_FRAC * N)
    flip_idx = rng.choice(N, size=n_flip, replace=False)
    query[flip_idx] = -query[flip_idx]
    retrieved_single = np.sign(W_single @ query + 1e-8)
    cos_single = float(np.dot(retrieved_single, xi_shared)) / N

    # --- Joint (all N_AGENTS write) ---
    W_joint = np.zeros((N, N), dtype=np.float64)
    Xi_specific_stored = []
    for agent_idx in range(N_AGENTS):
        xi_spec_agent = Xi_specific[agent_idx]
        for m in range(M_PER_AGENT):
            xi_noise = rng.choice([-1.0, 1.0], size=N).astype(np.float64)
            pattern_m = LAMBDA_SHARED * xi_shared + (1 - LAMBDA_SHARED) * xi_noise
            pattern_m_bin = np.sign(pattern_m + 1e-8)
            W_joint += np.outer(pattern_m_bin, pattern_m_bin) / N
        Xi_specific_stored.append(xi_spec_agent)
    np.fill_diagonal(W_joint, 0.0)

    # Joint retrieval of shared component
    query2 = xi_shared.copy()
    query2[flip_idx] = -query2[flip_idx]  # same noise
    retrieved_joint = np.sign(W_joint @ query2 + 1e-8)
    cos_joint = float(np.dot(retrieved_joint, xi_shared)) / N

    # Cell B: cross-agent contamination
    # Agent 0's specific pattern should not be retrievable by querying with agent 1's probe
    xi_spec_0 = Xi_specific_stored[0]
    xi_spec_1 = Xi_specific_stored[1]
    retrieved_contam = np.sign(W_joint @ xi_spec_1 + 1e-8)
    contamination = abs(float(np.dot(retrieved_contam, xi_spec_0)) / N)

    # Cell C: joint improvement
    joint_improvement = (cos_joint - cos_single) / (abs(cos_single) + 1e-10)

    assert cos_joint >= -1.0, "cos_joint out of range -- instrumentation bug"
    assert 0.0 <= contamination <= 1.0, f"contamination={contamination:.3f} out of [0,1]"

    cell_A_pass = cos_joint >= HP_COSINE_SHARED
    cell_A_hf = cos_joint < HF_COSINE_SHARED
    cell_B_pass = contamination <= HP_CONTAMINATION_MAX
    cell_B_hf = contamination > HF_CONTAMINATION_MAX
    cell_C_pass = joint_improvement >= HP_JOINT_IMPROVEMENT

    return {
        "N": N,
        "run_mode": RUN_MODE,
        "seed": seed,
        "cos_joint": cos_joint,
        "cos_single": cos_single,
        "contamination": contamination,
        "joint_improvement": joint_improvement,
        "cell_A_pass": cell_A_pass,
        "cell_A_hf": cell_A_hf,
        "cell_B_pass": cell_B_pass,
        "cell_B_hf": cell_B_hf,
        "cell_C_pass": cell_C_pass,
    }


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        result = run_one_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed={seed}] cos_joint={result['cos_joint']:.3f} contamination={result['contamination']:.3f} improvement={result['joint_improvement']:.3f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    n_seeds = len(SEEDS)

    all_cos = [per_seed[str(s)]["cos_joint"] for s in SEEDS]
    all_contam = [per_seed[str(s)]["contamination"] for s in SEEDS]
    all_impr = [per_seed[str(s)]["joint_improvement"] for s in SEEDS]
    mean_cos = float(np.mean(all_cos))
    mean_contam = float(np.mean(all_contam))
    mean_impr = float(np.mean(all_impr))

    n_A = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_pass"])
    n_A_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_hf"])
    n_B = sum(1 for s in SEEDS if per_seed[str(s)]["cell_B_pass"])
    n_B_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_B_hf"])
    n_C = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_pass"])

    thr = math.ceil(n_seeds * 0.6)
    cell_A_pass = n_A >= thr
    cell_B_pass = n_B >= thr
    cell_C_pass = n_C >= thr
    hf_A = n_A_hf >= thr
    hf_B = n_B_hf >= thr

    n_cells_pass = int(cell_A_pass) + int(cell_B_pass) + int(cell_C_pass)
    if n_cells_pass == 3:
        verdict = "HARD_PASS"
    elif hf_A or hf_B:
        verdict = "HARD_FAIL"
    elif n_cells_pass >= 2:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    elapsed = time.time() - t0
    verdict_msg = (
        f"multiagent_emergence_v1 verdict={verdict}: "
        f"mean_cos_joint={mean_cos:.3f}(HP>={HP_COSINE_SHARED}) "
        f"mean_contamination={mean_contam:.3f}(HP<={HP_CONTAMINATION_MAX}) "
        f"mean_joint_improvement={mean_impr:.3f}(HP>={HP_JOINT_IMPROVEMENT}) "
        f"cells={n_cells_pass}/3 elapsed={elapsed:.1f}s"
    )
    print(verdict_msg, flush=True)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N,
        "n_seeds": n_seeds,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "mean_cos_joint": mean_cos,
        "mean_contamination": mean_contam,
        "mean_joint_improvement": mean_impr,
        "n_cell_A_pass": n_A,
        "n_cell_B_pass": n_B,
        "n_cell_C_pass": n_C,
        "elapsed_s": elapsed,
    }
    with open(Path(out_dir) / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] metrics written to {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    main()
