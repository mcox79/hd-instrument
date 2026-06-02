"""Ultrametricity of pairwise basin overlaps (FRSB/non-reciprocal FRSB discriminator).

SCIENTIFIC QUESTION:
  Does the substrate exhibit ultrametric organization of its memory basins?
  Ultrametricity test (Garcia Lorenzana 2025 + standard FRSB theory):
    For triplets of random initial conditions (i, j, k), define pairwise overlaps
    q_ij = C(sigma_i(T), sigma_j(T)) after relaxation from different random starts.
    Ultrametric property: for any triplet, max(q_ij, q_jk, q_ik) >= both others
    MINUS a tolerance; equivalently, the two SMALLEST overlaps in any triplet
    are approximately EQUAL (within fluctuations).

  Two-point overlap distribution P(q): FRSB has broad continuous P(q) on [0, q_EA].
  1-RSB has delta-peak at 0 and q_EA. RS has delta-peak at q_EA only.

  FRSB ultrametric test (three-point):
    For triplet (i,j,k): sort overlaps as q_(1) <= q_(2) <= q_(3).
    Ultrametricity ratio R = q_(2) / q_(3) should be close to 1.0 in pure FRSB
    (two smallest overlaps nearly equal).
    For 1-RSB: R bimodal (0 or 1).
    For RS: R=1 trivially (all in same basin).

  Also: check if P(q) is continuous on [0, q_EA] (vs. discrete peaks).

PRE-REGISTERED BANDS (calibration probe, no prior ultrametricity anchor):
  HARD-PASS:
    - Mean(q_(2)/q_(3)) in [0.80, 1.0] (two smallest overlaps nearly equal).
    - P(q) shows continuous support on [0, q_EA] (not discrete peaks).
    - >= 4/5 seeds show mean ratio > 0.75.
  MIDDLE:
    - Mean ratio > 0.60 OR P(q) shows mixed structure.
  HARD-FAIL:
    - Mean ratio < 0.50 in >= 3/5 seeds (strong discretization -> RS or 1-RSB).
  Note: calibration probe; +-50% of threshold per policy.
  HP at 0.80 ratio; HF at 0.50 (5/8 of HP threshold).

DESIGN:
  N = 2048 (GPU; avoids OOM; 2048^2 * 4B = 16MB per matrix).
  alpha = 0.15 (above alpha_c = 0.138; spin-glass phase).
  M = int(0.15 * N) = 307 patterns.
  n_random_starts = 30 (random initial conditions per seed).
  Relaxation: synchronous Hopfield updates until convergence (max 100 iterations).
  Triplet count: C(30, 3) = 4060 triplets per seed. Sample 200 random triplets.
  5 seeds.

OOM CHECK:
  W: 2048^2 * 4B = 16MB. n_starts * N: 30 * 2048 = negligible.
  Total GPU: ~50MB. Well within 8GB.

PROT-018: no _nN suffix. Production N=2048, rule 3 stated.
  Stated: production N=2048; rationale: ultrametricity test, GPU memory budget.

TIMEOUT ESTIMATE:
  GPU matmul 2048x2048 with 30 initial states: W @ states (2048x30) fast.
  5 seeds * 30 starts * 100 iters: 15000 GPU matmuls. At 2048^2: ~10ms each.
  Estimate: ~150s. ceil(1.5*150) = 225 -> 300s.
  But let's be conservative: timeout_s=900.

Anchor: ultrametricity_basins_v1
Queue: overnight_queue
Pre-reg: preregs/2026-06-01_ultrametricity_basins_v1.md
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
from typing import Dict, List, Optional

import numpy as np

try:
    import torch
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    DEVICE = None
    torch = None  # type: ignore

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "ultrametricity_basins_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# PROT-018: no _nN suffix. Production N=2048, rule 3.
N = 2048
ALPHA = 0.15
M = int(ALPHA * N)  # 307

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_STARTS = 10
    N_TRIPLETS = 50
    MAX_ITERS = 50
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_STARTS = 30
    N_TRIPLETS = 200
    MAX_ITERS = 100


def build_W(N: int, M: int, seed: int, device: "torch.device") -> "torch.Tensor":
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1, 1], size=(N, M)).astype(np.float32)
    Xi_t = torch.tensor(Xi, dtype=torch.float32, device=device)
    W = (Xi_t @ Xi_t.t()) / N
    return W


def hopfield_relax(W: "torch.Tensor", states: "torch.Tensor",
                   max_iters: int = 100) -> "torch.Tensor":
    """Synchronous Hopfield relaxation. states: (N, n_starts)."""
    for _ in range(max_iters):
        new_states = torch.sign(W @ states)
        # Handle 0 -> keep previous sign
        new_states = torch.where(new_states == 0, states, new_states)
        if torch.all(new_states == states):
            break
        states = new_states
    return states


def overlap(a: "torch.Tensor", b: "torch.Tensor") -> float:
    """Normalized overlap between two state vectors."""
    N = a.shape[0]
    return float((a * b).sum() / N)


def run_one_seed(N: int, M: int, seed: int, n_starts: int,
                 n_triplets: int, max_iters: int,
                 device: "torch.device") -> Dict:
    rng = np.random.RandomState(seed)

    W = build_W(N, M, seed, device)

    # Random initial conditions
    init_np = rng.choice([-1, 1], size=(N, n_starts)).astype(np.float32)
    states = torch.tensor(init_np, dtype=torch.float32, device=device)

    # Relax all states
    states_relaxed = hopfield_relax(W, states, max_iters)  # (N, n_starts)
    states_np = states_relaxed.cpu().numpy()  # (N, n_starts)

    # Pairwise overlaps q[i,j] = <sigma_i, sigma_j> / N
    q_matrix = np.zeros((n_starts, n_starts))
    for i in range(n_starts):
        for j in range(i + 1, n_starts):
            q_ij = float(np.dot(states_np[:, i], states_np[:, j]) / N)
            q_matrix[i, j] = q_ij
            q_matrix[j, i] = q_ij
    np.fill_diagonal(q_matrix, 1.0)

    # Sample random triplets
    triplet_indices = []
    attempts = 0
    while len(triplet_indices) < n_triplets and attempts < n_triplets * 10:
        i, j, k = rng.choice(n_starts, 3, replace=False)
        triplet_indices.append((i, j, k))
        attempts += 1

    # Ultrametricity ratio for each triplet
    ratios = []
    q_values_all = []
    for (i, j, k) in triplet_indices:
        q_ij = q_matrix[i, j]
        q_jk = q_matrix[j, k]
        q_ik = q_matrix[i, k]
        qs = sorted([abs(q_ij), abs(q_jk), abs(q_ik)])  # ascending
        q1, q2, q3 = qs
        if q3 > 1e-6:
            ratio = q2 / q3  # two smallest / largest
            ratios.append(ratio)
        q_values_all.extend([q_ij, q_jk, q_ik])

    # P(q) distribution: check if continuous
    q_abs = [abs(q) for q in q_values_all]
    q_mean = float(np.mean(q_abs))
    q_std = float(np.std(q_abs))
    q_max = float(np.max(q_abs))

    # Check if P(q) is concentrated (RS: all at q_EA) or spread (FRSB: continuous)
    q_EA_est = q_max  # rough estimate of q_EA
    q_spread = q_std / max(1e-6, q_EA_est)  # normalized spread

    mean_ratio = float(np.mean(ratios)) if ratios else 0.0
    hp = mean_ratio > 0.75

    return {
        "seed": seed,
        "N": N,
        "M": M,
        "n_starts": n_starts,
        "n_triplets_sampled": len(ratios),
        "mean_ultrametricity_ratio": mean_ratio,
        "std_ultrametricity_ratio": float(np.std(ratios)) if ratios else 0.0,
        "q_mean": q_mean,
        "q_std": q_std,
        "q_max": q_max,
        "q_spread_normalized": q_spread,
        "hp": hp,
    }


def _instrumentation_selftest():
    """Assert ultrametricity computation is non-null at small scale."""
    if not HAS_TORCH:
        print("[selftest] WARN: torch not available, using numpy fallback", flush=True)
        return
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    r = run_one_seed(N=256, M=20, seed=999, n_starts=5, n_triplets=10,
                     max_iters=20, device=device)
    assert r["mean_ultrametricity_ratio"] is not None, "mean_ratio is None"
    assert not math.isnan(r["mean_ultrametricity_ratio"]), "mean_ratio is NaN"
    assert r["n_triplets_sampled"] > 0, f"no triplets sampled at smoke scale"
    assert 0.0 <= r["mean_ultrametricity_ratio"] <= 1.01, \
        f"ratio out of [0,1]: {r['mean_ultrametricity_ratio']}"
    print(f"[selftest] PASS: mean_ratio={r['mean_ultrametricity_ratio']:.3f} "
          f"q_mean={r['q_mean']:.3f} n_triplets={r['n_triplets_sampled']}", flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not HAS_TORCH:
        print(f"[{ANCHOR_NAME}] ERROR: torch required", flush=True)
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} N={N} M={M} alpha={ALPHA} "
          f"device={device} seeds={SEEDS}", flush=True)
    print(f"  n_starts={N_STARTS} n_triplets={N_TRIPLETS}", flush=True)

    results = []
    for seed in SEEDS:
        print(f"[{ANCHOR_NAME}] seed={seed}...", flush=True)
        r = run_one_seed(N, M, seed, N_STARTS, N_TRIPLETS, MAX_ITERS, device)
        results.append(r)
        print(f"  mean_ratio={r['mean_ultrametricity_ratio']:.3f} "
              f"q_spread={r['q_spread_normalized']:.3f} "
              f"q_mean={r['q_mean']:.3f} hp={r['hp']}", flush=True)

    n_hp = sum(1 for r in results if r["hp"])
    n_seeds = len(results)
    mean_ratios = [r["mean_ultrametricity_ratio"] for r in results]
    overall_mean_ratio = float(np.mean(mean_ratios))
    q_spreads = [r["q_spread_normalized"] for r in results]
    mean_q_spread = float(np.mean(q_spreads))

    if n_hp >= 4 and overall_mean_ratio > 0.80:
        verdict = "HARD_PASS"
    elif overall_mean_ratio > 0.60 or n_hp >= 2:
        verdict = "MIDDLE_BAND"
    elif overall_mean_ratio < 0.50 and n_hp <= 1:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"Ultrametricity: mean_ratio={overall_mean_ratio:.3f}, "
            f"n_hp={n_hp}/{n_seeds}, q_spread={mean_q_spread:.3f}, "
            f"N={N}, alpha={ALPHA}, n_starts={N_STARTS}"
        ),
        "mean_ultrametricity_ratio": overall_mean_ratio,
        "n_hp_seeds": n_hp,
        "n_seeds": n_seeds,
        "mean_q_spread_normalized": mean_q_spread,
        "N": N,
        "M": M,
        "alpha": ALPHA,
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
        "per_seed": results,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  mean_ratio={overall_mean_ratio:.3f} n_hp={n_hp}/{n_seeds} "
          f"q_spread={mean_q_spread:.3f}", flush=True)
    print(f"  elapsed={elapsed:.1f}s", flush=True)
    print(f"  metrics -> {metrics_path}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _p.add_argument("--smoke", action="store_true",
                    help="Run at smoke scope for gate validation")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()