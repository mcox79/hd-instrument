"""Cell D: L=2 nested composition at production N (Hadamard-binding).

SCIENTIFIC QUESTION:
  Does the substrate support L=2 nested Hopfield composition using Hadamard-binding
  at N_outer = N_inner = 8192? End-to-end accuracy > 0.88 at conservative inner load.

  L=2 architecture: inner memory W_inner encodes entities {xi_mu} at N=8192.
  Outer memory W_outer encodes composite patterns {phi_mu = h_k (*) xi_mu} where
  h_k are Hadamard codewords (exact orthogonality) and (*) is elementwise multiply.
  Query: present noisy composite, retrieve composite, unbind with h_k, verify entity.

PRE-REGISTERED BANDS:
  HARD-PASS: end-to-end accuracy > 0.88 at inner load alpha_inner <= 0.05
             in >= 4/5 seeds.
  MIDDLE: 0.75 <= accuracy <= 0.88 (composition is noisy but functional).
  HARD-FAIL: accuracy < 0.75 in >= 3/5 seeds (composition fails at N=8192).

DESIGN:
  N = 8192 (PROT-018 _n8192 binding).
  n_entities = 20 (alpha_inner = 20/8192 ~ 0.0024 -- well below capacity).
  n_composite = 20 (each entity bound to one Hadamard codeword).
  Hadamard codewords: first 20 rows of H_{8192} (Walsh-Hadamard, {-1,+1} entries).
  W_inner = sum_mu xi_mu xi_mu^T / N.
  W_outer = sum_mu phi_mu phi_mu^T / N where phi_mu = h_mu (*) xi_mu.
  Query: phi_noisy = add_noise(phi_mu, noise_frac=0.10).
  Retrieve from W_outer: phi_retrieved = hop(W_outer, phi_noisy).
  Unbind: xi_retrieved = phi_retrieved (*) h_mu (Hadamard self-inverse).
  Verify with W_inner: xi_final = hop(W_inner, xi_retrieved).
  Measure accuracy = <xi_final, xi_mu> / N (end-to-end overlap).

PROT-018: _n8192 suffix binding. Production N MUST equal 8192. Smoke uses N=1024.
  Pre-ship audit: grep for N = 8192 confirms this script.

MEMORY CHECK (OOM):
  W at N=8192: float32 = 8192^2 * 4 bytes = 256 MB per matrix.
  Two matrices (W_inner + W_outer) = 512 MB. Well within 8 GB GPU.

TIMEOUT ESTIMATE:
  GPU matmul at N=8192: W_outer @ phi = 8192^2 ops ~ fast (<1ms on GPU).
  5 seeds * 20 composites * 2 hops = 200 retrieval ops. Negligible.
  W construction: 5 seeds * 20 patterns * N^2 / N = 5 * 20 * N = trivial.
  Smoke (N=1024): ~5s. Full (N=8192): scaling by (8192/1024)^1.5 ~ 90s.
  ceil(1.5 * 5 * (8192/1024)^1.5 * (5/2)) = ceil(1.5 * 5 * 22.6 * 2.5) = ceil(424) = 450s.
  timeout_s = 900 (2x safety for GPU overhead).

Anchor: l2_hadamard_comp_n8192_v1
Queue: overnight_queue
Pre-reg: preregs/2026-06-01_l2_hadamard_comp_n8192_v1.md
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "l2_hadamard_comp_n8192_v1"

# PROT-018: _n8192 binding
N = 8192
N_SMOKE = 1024
N_ENTITIES = 20
N_COMPOSITE = 20
NOISE_FRAC = 0.10
MAX_STEPS = 10

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# Pre-registered thresholds
HP_ACC = 0.88
MID_ACC_LOW = 0.75
HF_MIN_SEEDS = 3
HP_MIN_SEEDS = 4

assert N == 8192, "PROT-018: _n8192 binds N=8192"


def make_hadamard_row(i: int, N_dim: int) -> np.ndarray:
    """Build row i of the Walsh-Hadamard matrix H_N using H[i,j] = (-1)^popcount(i & j)."""
    j_arr = np.arange(N_dim)
    bitwise = i & j_arr
    popcount = np.array([bin(int(x)).count('1') for x in bitwise])
    return (-1.0) ** popcount


def make_hadamard_codebook(D: int, N_dim: int) -> np.ndarray:
    """Build D x N Hadamard codebook (first D rows of H_N)."""
    codebook = np.stack([make_hadamard_row(i, N_dim) for i in range(D)], axis=0)
    assert codebook.shape == (D, N_dim)
    # Verify orthogonality (spot-check first 5 rows)
    for i in range(min(D, 5)):
        for j in range(i + 1, min(D, 5)):
            dot = float(np.dot(codebook[i], codebook[j]))
            assert abs(dot) < 1e-6, f"Hadamard rows {i},{j} not orthogonal: dot={dot}"
    return codebook


def build_w(patterns: np.ndarray, N_dim: int) -> np.ndarray:
    """Hopfield W = (1/N) * patterns^T @ patterns."""
    W = (patterns.T @ patterns) / N_dim
    np.fill_diagonal(W, 0.0)
    return W


def hopfield_retrieve(W: np.ndarray, query: np.ndarray,
                      max_steps: int = MAX_STEPS) -> np.ndarray:
    """Synchronous Hopfield retrieval."""
    s = query.copy()
    for _ in range(max_steps):
        s_new = np.where(W @ s > 0, 1.0, -1.0)
        if np.all(s_new == s):
            break
        s = s_new
    return s


def add_noise(pattern: np.ndarray, frac: float, rng: np.random.Generator) -> np.ndarray:
    q = pattern.copy()
    n_flip = int(frac * len(q))
    idx = rng.choice(len(q), size=n_flip, replace=False)
    q[idx] *= -1
    return q


def run_one_seed(seed: int, N_dim: int) -> Dict:
    """Run L=2 composition test for one seed."""
    rng = np.random.default_rng(seed)

    # Generate entities and Hadamard codebook
    entities = rng.choice([-1.0, 1.0], size=(N_ENTITIES, N_dim))
    hadamard = make_hadamard_codebook(N_COMPOSITE, N_dim)

    # Build inner memory
    W_inner = build_w(entities, N_dim)

    # Build composite patterns: phi_mu = h_mu (*) xi_mu (elementwise)
    composites = hadamard[:N_COMPOSITE] * entities[:N_COMPOSITE]
    W_outer = build_w(composites, N_dim)

    # End-to-end accuracy
    accuracies = []
    for mu in range(N_COMPOSITE):
        # Noisy composite query
        q = add_noise(composites[mu], NOISE_FRAC, rng)
        # Retrieve from outer memory
        phi_retrieved = hopfield_retrieve(W_outer, q)
        # Unbind with Hadamard codeword (self-inverse: h * h = 1)
        xi_unbound = phi_retrieved * hadamard[mu]
        # Retrieve from inner memory
        xi_final = hopfield_retrieve(W_inner, xi_unbound)
        # Overlap with target entity
        ov = float(np.dot(xi_final, entities[mu])) / N_dim
        accuracies.append(ov)

    mean_acc = float(np.mean(accuracies))
    return {
        "mean_acc": mean_acc,
        "min_acc": float(np.min(accuracies)),
        "hp_pass": mean_acc > HP_ACC,
        "accuracies": [float(a) for a in accuracies],
    }


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert Hadamard binding and L=2 composition non-null at N=128."""
    N_t = 128
    D_t = 5
    rng = np.random.default_rng(0)
    had = make_hadamard_codebook(D_t, N_t)
    assert had.shape == (D_t, N_t), f"Hadamard shape {had.shape}"
    # Verify self-inverse: h * h = +1 everywhere
    for i in range(D_t):
        assert np.all(had[i] * had[i] == 1.0), f"row {i} not self-inverse"
    # Run one seed at N=128
    res = run_one_seed.__wrapped__(42, N_t) if hasattr(run_one_seed, '__wrapped__') \
        else _run_small_test(N_t, rng)
    assert res["mean_acc"] is not None and not math.isnan(res["mean_acc"]), \
        "mean_acc is NaN"
    print(f"[selftest] PASS: Hadamard orthog OK, mean_acc={res['mean_acc']:.3f}",
          flush=True)


def _run_small_test(N_t: int, rng: np.random.Generator) -> Dict:
    """Minimal composition test at small N for self-test."""
    n = min(5, N_t)
    entities = rng.choice([-1.0, 1.0], size=(n, N_t))
    hadamard = make_hadamard_codebook(n, N_t)
    W_inner = build_w(entities, N_t)
    composites = hadamard * entities
    W_outer = build_w(composites, N_t)
    accs = []
    for mu in range(n):
        q = add_noise(composites[mu], NOISE_FRAC, rng)
        phi_r = hopfield_retrieve(W_outer, q)
        xi_u = phi_r * hadamard[mu]
        xi_f = hopfield_retrieve(W_inner, xi_u)
        accs.append(float(np.dot(xi_f, entities[mu])) / N_t)
    return {"mean_acc": float(np.mean(accs))}


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
    n_dim = N if run_mode == "full" else N_SMOKE
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} N={n_dim}", flush=True)
    if run_mode == "full":
        assert n_dim == N, f"PROT-018: full run must use N={N}"

    all_results = {}
    for seed in seeds:
        print(f"  seed={seed}...", flush=True)
        res = run_one_seed(seed, n_dim)
        all_results[str(seed)] = res
        print(f"    mean_acc={res['mean_acc']:.4f} min_acc={res['min_acc']:.4f}",
              flush=True)

    accs = [r["mean_acc"] for r in all_results.values()]
    n_seeds = len(seeds)
    seeds_hp = sum(1 for r in all_results.values() if r["hp_pass"])
    seeds_hf = sum(1 for r in all_results.values() if r["mean_acc"] < MID_ACC_LOW)

    hp_thresh = HP_MIN_SEEDS if n_seeds >= 5 else math.ceil(n_seeds * 0.8)
    hf_thresh = HF_MIN_SEEDS if n_seeds >= 5 else math.ceil(n_seeds * 0.6)

    if seeds_hf >= hf_thresh:
        verdict = "HARD_FAIL"
    elif seeds_hp >= hp_thresh:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode,
        "N": n_dim, "n_entities": N_ENTITIES, "n_composite": N_COMPOSITE,
        "n_seeds": n_seeds,
        "mean_acc_across_seeds": float(np.mean(accs)),
        "std_acc_across_seeds": float(np.std(accs)),
        "seeds_hp": seeds_hp, "seeds_hf": seeds_hf,
        "per_seed": {k: {"mean_acc": v["mean_acc"], "min_acc": v["min_acc"]}
                     for k, v in all_results.items()},
        "verdict": verdict, "elapsed_s": elapsed,
        "thresholds": {"HP_acc": HP_ACC, "MID_acc_low": MID_ACC_LOW},
        "verdict_msg": (
            f"L=2 Hadamard composition at N={n_dim}: "
            f"mean_acc={np.mean(accs):.4f}+/-{np.std(accs):.4f} "
            f"(HP>{HP_ACC}), {seeds_hp}/{n_seeds} seeds pass HP. "
            f"Verdict: {verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} mean_acc={np.mean(accs):.4f} "
          f"elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _p.add_argument("--smoke", action="store_true",
                    help="Run at smoke scope for gate validation")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    if _args.smoke:
        os.environ["HDLAB_RUN_MODE"] = "smoke"
    main()
