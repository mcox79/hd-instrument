"""Cell K: Symbolic primitive battery (S1+S2+S3+S5 combined at N=2048).

SCIENTIFIC QUESTION:
  Does the substrate function as a native inference engine at N=2048?
  Combined test of 4 symbolic primitives:
  S1: rule-fire (K=8 patterns, single-antecedent trigger)
  S2: disjunction (K=4, fires from single antecedent)
  S3: 4-step forward chain (T1->T2->T3->T4 in <=5 iterations)
  S5: backward 1-step (both hops, cos > 0.25)

PRE-REGISTERED BANDS (from research proposal):
  S1 rule-fire: HARD-PASS if K=8 all-correct gap > 0.3 (gap = cos_sim(retrieved, target) - max_other)
  S2 disjunction: HARD-PASS if K=4 single-antecedent fires at gap > 0.2
  S3 forward chain: HARD-PASS if T1->T4 in <=5 iterations cos > 0.25 at step 4
  S5 backward: HARD-PASS if 1-step backward for both hops gives cos > 0.25

  Overall HARD-PASS: >= 3/4 sub-tests pass HP criteria.
  MIDDLE: 2/4 sub-tests pass HP criteria.
  HARD-FAIL: <= 1/4 sub-tests pass HP criteria.

DESIGN:
  N=2048. Bipolar patterns (+/-1). 5 seeds.
  All sub-tests share the same pattern generation for efficiency.
  S1 (rule-fire): store 8 rule patterns {A_k -> B_k}. Present A_k + noise, retrieve B_k.
                  Rule encoding: W += (b_k outer a_k^T) / N.
  S2 (disjunction): store pattern B that can be triggered by A1 OR A2 (either single antecedent).
                    W += (b outer a1^T + b outer a2^T) / N. Trigger with a1 only.
  S3 (forward chain): store chain T1->T2->T3->T4. Run iterative retrieval 5 times.
  S5 (backward): store A->B. Given noisy B, recover A. Use W^T (asymmetric rule memory).

PROT-018: no _nN suffix. Production N=2048; stated per PROT-018 rule 3.
  Stated: production N = 2048; rationale: symbolic-primitive battery at standard size.

TIMEOUT ESTIMATE:
  5 seeds * (8 + 4 + 4 + 4) rules * ~20 steps each = 5 * 20 * 20 = 2000 steps.
  Each step: O(N^2) at N=2048 = ~1ms. Total: ~2s.
  timeout_s = 300 (floor).

Anchor: symbolic_prim_battery_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_symbolic_prim_battery_v1.md
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

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "symbolic_prim_battery_v1"

# Production config
N = 2048
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# HP thresholds per sub-test
HP_GAP_S1 = 0.30   # rule-fire K=8 gap
HP_GAP_S2 = 0.20   # disjunction K=4 gap
HP_COS_S3 = 0.25   # chain cos at step 4
HP_COS_S5 = 0.25   # backward hop cos

# Noise fraction for queries
NOISE_FRAC = 0.10
MAX_ITER = 5  # forward chain iterations


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two bipolar vectors."""
    return float(np.dot(a, b)) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12)


def retrieval_step(W: np.ndarray, state: np.ndarray) -> np.ndarray:
    """One synchronous update step."""
    return np.where(W @ state > 0, 1.0, -1.0)


def add_noise(pattern: np.ndarray, noise_frac: float, rng: np.random.Generator) -> np.ndarray:
    q = pattern.copy()
    n_flip = int(noise_frac * len(q))
    idx = rng.choice(len(q), size=n_flip, replace=False)
    q[idx] *= -1
    return q


# ---------------------------------------------------------------------------
# Sub-test S1: rule-fire
# ---------------------------------------------------------------------------

def run_s1_rule_fire(N: int, K: int, rng: np.random.Generator) -> Dict:
    """Store K rules A_k -> B_k. Present noisy A_k, expect B_k."""
    As = rng.choice([-1.0, 1.0], size=(K, N))
    Bs = rng.choice([-1.0, 1.0], size=(K, N))
    # Asymmetric rule memory W_rule = sum_k b_k a_k^T / N
    W = sum(np.outer(Bs[k], As[k]) for k in range(K)) / N
    gaps = []
    for k in range(K):
        q = add_noise(As[k], NOISE_FRAC, rng)
        retrieved = retrieval_step(W, q)
        sim_target = cosine_sim(retrieved, Bs[k])
        sim_others = [cosine_sim(retrieved, Bs[j]) for j in range(K) if j != k]
        max_other = max(sim_others) if sim_others else 0.0
        gap = sim_target - max_other
        gaps.append(gap)
    all_correct = all(g > HP_GAP_S1 for g in gaps)
    return {"gaps": [float(g) for g in gaps], "min_gap": float(min(gaps)),
            "all_correct": all_correct, "hp_pass": all_correct}


# ---------------------------------------------------------------------------
# Sub-test S2: disjunction
# ---------------------------------------------------------------------------

def run_s2_disjunction(N: int, K: int, rng: np.random.Generator) -> Dict:
    """Store K rules (A1_k OR A2_k) -> B_k. Fire with A1_k only."""
    A1s = rng.choice([-1.0, 1.0], size=(K, N))
    A2s = rng.choice([-1.0, 1.0], size=(K, N))
    Bs = rng.choice([-1.0, 1.0], size=(K, N))
    # W encodes both antecedents
    W = sum(np.outer(Bs[k], A1s[k]) + np.outer(Bs[k], A2s[k])
            for k in range(K)) / N
    gaps = []
    for k in range(K):
        # Fire from single antecedent A1_k
        q = add_noise(A1s[k], NOISE_FRAC, rng)
        retrieved = retrieval_step(W, q)
        sim_target = cosine_sim(retrieved, Bs[k])
        sim_others = [cosine_sim(retrieved, Bs[j]) for j in range(K) if j != k]
        max_other = max(sim_others) if sim_others else 0.0
        gap = sim_target - max_other
        gaps.append(gap)
    all_correct = all(g > HP_GAP_S2 for g in gaps)
    return {"gaps": [float(g) for g in gaps], "min_gap": float(min(gaps)),
            "all_correct": all_correct, "hp_pass": all_correct}


# ---------------------------------------------------------------------------
# Sub-test S3: 4-step forward chain
# ---------------------------------------------------------------------------

def run_s3_forward_chain(N: int, max_iter: int, rng: np.random.Generator) -> Dict:
    """Store T1->T2->T3->T4. Run from noisy T1, check T4 at step max_iter."""
    chain = rng.choice([-1.0, 1.0], size=(4, N))  # T1, T2, T3, T4
    # W = sum_{i=0}^{2} T_{i+1} outer T_i^T / N
    W = sum(np.outer(chain[i + 1], chain[i]) for i in range(3)) / N
    state = add_noise(chain[0], NOISE_FRAC, rng)
    cos_by_step = []
    for step in range(max_iter):
        state = retrieval_step(W, state)
        # Cosine with T4 (index 3)
        cos_t4 = cosine_sim(state, chain[3])
        cos_by_step.append(cos_t4)
    final_cos = cos_by_step[-1]
    hp_pass = final_cos > HP_COS_S3
    return {"cos_by_step": [float(c) for c in cos_by_step],
            "final_cos": float(final_cos), "hp_pass": hp_pass}


# ---------------------------------------------------------------------------
# Sub-test S5: backward 1-step
# ---------------------------------------------------------------------------

def run_s5_backward(N: int, rng: np.random.Generator) -> Dict:
    """Store 2 rules A->B and C->D. Given noisy B, recover A; given noisy D, recover C."""
    A = rng.choice([-1.0, 1.0], size=N)
    B = rng.choice([-1.0, 1.0], size=N)
    C = rng.choice([-1.0, 1.0], size=N)
    D = rng.choice([-1.0, 1.0], size=N)
    # Forward W: W_fwd = (B outer A^T + D outer C^T) / N
    # Backward W: W_bwd = W_fwd^T = (A outer B^T + C outer D^T) / N
    W_bwd = (np.outer(A, B) + np.outer(C, D)) / N
    # Hop 1: noisy B -> recover A
    q1 = add_noise(B, NOISE_FRAC, rng)
    rec_A = retrieval_step(W_bwd, q1)
    cos_A = cosine_sim(rec_A, A)
    # Hop 2: noisy D -> recover C
    q2 = add_noise(D, NOISE_FRAC, rng)
    rec_C = retrieval_step(W_bwd, q2)
    cos_C = cosine_sim(rec_C, C)
    hp_pass = (cos_A > HP_COS_S5 and cos_C > HP_COS_S5)
    return {"cos_A": float(cos_A), "cos_C": float(cos_C),
            "both_pass": hp_pass, "hp_pass": hp_pass}


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert all 4 sub-tests are non-null at N=64."""
    rng = np.random.default_rng(0)
    N_t = 128
    r1 = run_s1_rule_fire(N_t, 3, rng)
    assert r1["min_gap"] is not None and not math.isnan(r1["min_gap"]), "S1 gap NaN"
    r2 = run_s2_disjunction(N_t, 2, rng)
    assert r2["min_gap"] is not None and not math.isnan(r2["min_gap"]), "S2 gap NaN"
    r3 = run_s3_forward_chain(N_t, 3, rng)
    assert r3["final_cos"] is not None and not math.isnan(r3["final_cos"]), "S3 cos NaN"
    r5 = run_s5_backward(N_t, rng)
    assert r5["cos_A"] is not None and not math.isnan(r5["cos_A"]), "S5 cos NaN"
    print("[selftest] PASS: all 4 symbolic sub-tests non-null", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} N={N}", flush=True)

    s1_results, s2_results, s3_results, s5_results = [], [], [], []

    for seed in seeds:
        rng = np.random.default_rng(seed)
        r1 = run_s1_rule_fire(N, 8, rng)
        r2 = run_s2_disjunction(N, 4, rng)
        r3 = run_s3_forward_chain(N, MAX_ITER, rng)
        r5 = run_s5_backward(N, rng)
        s1_results.append(r1)
        s2_results.append(r2)
        s3_results.append(r3)
        s5_results.append(r5)
        print(f"  seed={seed}: S1_gap={r1['min_gap']:.3f} S2_gap={r2['min_gap']:.3f} "
              f"S3_cos={r3['final_cos']:.3f} S5_cosA={r5['cos_A']:.3f}", flush=True)

    # Per-sub-test verdict
    s1_hp = sum(1 for r in s1_results if r["hp_pass"]) >= math.ceil(len(seeds) * 0.8)
    s2_hp = sum(1 for r in s2_results if r["hp_pass"]) >= math.ceil(len(seeds) * 0.8)
    s3_hp = sum(1 for r in s3_results if r["hp_pass"]) >= math.ceil(len(seeds) * 0.8)
    s5_hp = sum(1 for r in s5_results if r["hp_pass"]) >= math.ceil(len(seeds) * 0.8)

    n_subtests_pass = sum([s1_hp, s2_hp, s3_hp, s5_hp])
    if n_subtests_pass >= 3:
        verdict = "HARD_PASS"
    elif n_subtests_pass == 2:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode,
        "N": N, "n_seeds": len(seeds),
        "S1_rule_fire": {
            "hp_pass": s1_hp,
            "min_gap_mean": float(np.mean([r["min_gap"] for r in s1_results])),
            "min_gap_std": float(np.std([r["min_gap"] for r in s1_results])),
            "HP_threshold": HP_GAP_S1,
        },
        "S2_disjunction": {
            "hp_pass": s2_hp,
            "min_gap_mean": float(np.mean([r["min_gap"] for r in s2_results])),
            "HP_threshold": HP_GAP_S2,
        },
        "S3_forward_chain": {
            "hp_pass": s3_hp,
            "final_cos_mean": float(np.mean([r["final_cos"] for r in s3_results])),
            "final_cos_std": float(np.std([r["final_cos"] for r in s3_results])),
            "HP_threshold": HP_COS_S3,
        },
        "S5_backward": {
            "hp_pass": s5_hp,
            "cos_A_mean": float(np.mean([r["cos_A"] for r in s5_results])),
            "cos_C_mean": float(np.mean([r["cos_C"] for r in s5_results])),
            "HP_threshold": HP_COS_S5,
        },
        "n_subtests_pass": n_subtests_pass,
        "verdict": verdict, "elapsed_s": elapsed,
        "verdict_msg": (
            f"Symbolic battery at N={N}: S1={'HP' if s1_hp else 'FAIL'} "
            f"S2={'HP' if s2_hp else 'FAIL'} S3={'HP' if s3_hp else 'FAIL'} "
            f"S5={'HP' if s5_hp else 'FAIL'} ({n_subtests_pass}/4 pass). "
            f"Verdict: {verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} subtests={n_subtests_pass}/4 "
          f"elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _p.add_argument("--smoke", action="store_true",
                    help="Run at smoke scope (SEEDS_SMOKE) for gate validation")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    if _args.smoke:
        os.environ["HDLAB_RUN_MODE"] = "smoke"
    main()
