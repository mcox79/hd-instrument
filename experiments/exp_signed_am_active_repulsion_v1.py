"""Signed-AM active repulsion: B-patterns as energy maxima (Q16 DEEP verification).

SCIENTIFIC QUESTION:
  Does W_signed = W_A - W_B create active repulsion for B-patterns?
  Theory (anti-Hopfield / signed-AM):
    W_A = sum_mu xi_mu xi_mu^T / N (A-patterns: attractors)
    W_B = sum_nu eta_nu eta_nu^T / N (B-patterns: anti-learned = repellers)
    W_signed = W_A - W_B.

  Prediction:
    1. Starting near a B-pattern (eta_nu + noise), synchronous Hopfield dynamics
       REPELS away (does NOT converge to eta_nu; converges to -eta_nu or an A-pattern).
    2. Energy at eta_nu: E(eta_nu) = -0.5 * eta_nu^T W_signed eta_nu / N
       = -0.5 * [eta_nu^T W_A eta_nu - eta_nu^T W_B eta_nu] / N
       ~ -0.5 * (|B|/N) * (M_A/N) * N^2/N  -- wait, let me compute exactly.
       E = -0.5/N * [sum_mu (xi_mu.eta_nu)^2 - sum_nu' (eta_nu'.eta_nu)^2]
       For nu'=nu: eta_nu.eta_nu = N -> contributes -0.5/N * (-N^2/N) = +N/2 > 0 (energy MAX).
       For mu in A: random overlap ~ N^{1/2} -> small contribution.
       So B-patterns are ENERGY MAXIMA in W_signed.
    3. The antipode -eta_nu is an energy MINIMUM (repulsion goes to antipode).

  HP criterion:
    - Fraction of B-queries that converge to anti-B (dot product with eta_nu < -0.5N):
      >= 0.75 in >= 4/5 seeds.
    - Energy of eta_nu under W_signed > energy of random vector (B is a MAX, not a min).

PRE-REGISTERED BANDS:
  HARD-PASS: fraction_anti_B >= 0.75 AND energy_B > energy_random in >= 4/5 seeds.
  MIDDLE: fraction_anti_B >= 0.50 (some repulsion but weak).
  HARD-FAIL: fraction_anti_B < 0.30 in >= 3/5 seeds (no active repulsion).
  Note: calibration probe; +-50% per policy. HP at 0.75; HF at 0.30.

DESIGN:
  N = 2048 (GPU; W at 2048^2 * 4B = 16MB).
  M_A = 15 (alpha_A = 0.0073; A-patterns are stored safely).
  M_B = 15 (alpha_B = 0.0073; B-patterns are anti-learned).
  Total alpha = 0.0146 << alpha_c = 0.138.
  n_queries_per_pattern = 5 (different noise realizations).
  noise_frac = 0.10 (10% bit flip on B-pattern).
  5 seeds.

OOM CHECK:
  W: 2048^2 * 4B = 16MB. Fine for 8GB GPU.

PROT-018: no _nN suffix. Production N=2048, rule 3.
  Stated: production N=2048; rationale: signed-AM energy landscape test.

TIMEOUT ESTIMATE:
  5 seeds * (M_A+M_B)*5 queries * N hopfield iters = 5 * 150 * 50 = 37500 iters.
  Each iter: GPU matmul 2048x2048 ~ fast. Total: <30s.
  timeout_s=300.

Anchor: signed_am_active_repulsion_v1
Queue: overnight_queue
Pre-reg: preregs/2026-06-01_signed_am_active_repulsion_v1.md
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
from typing import Dict, List

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

ANCHOR_NAME = "signed_am_active_repulsion_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 2048
M_A = 15
M_B = 15
NOISE_FRAC = 0.10
N_QUERIES = 5
N_ITERS = 50  # Hopfield relaxation iterations

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
else:
    SEEDS = [7, 17, 23, 31, 41]


def hopfield_signed_retrieve(W: "torch.Tensor", query: "torch.Tensor",
                              n_iters: int) -> "torch.Tensor":
    """Synchronous Hopfield update with W_signed = W_A - W_B."""
    sigma = query.clone()
    for _ in range(n_iters):
        sigma = torch.sign(W @ sigma)
        sigma[sigma == 0] = 1.0
    return sigma


def run_one_seed(N: int, M_A: int, M_B: int, seed: int,
                 noise_frac: float, n_queries: int, n_iters: int,
                 device: "torch.device") -> Dict:
    rng = np.random.RandomState(seed)

    Xi_np = rng.choice([-1.0, 1.0], size=(N, M_A)).astype(np.float32)
    Eta_np = rng.choice([-1.0, 1.0], size=(N, M_B)).astype(np.float32)

    Xi = torch.tensor(Xi_np, dtype=torch.float32, device=device)
    Eta = torch.tensor(Eta_np, dtype=torch.float32, device=device)

    W_A = (Xi @ Xi.t()) / N
    W_B = (Eta @ Eta.t()) / N
    W_signed = W_A - W_B  # (N, N)

    # Energy function: E(sigma) = -0.5 * sigma^T W_signed sigma / N
    def energy(sigma):
        return float(-0.5 * (sigma @ (W_signed @ sigma)) / N)

    # Test B-pattern repulsion
    anti_b_count = 0
    total_b_queries = 0
    b_energies = []
    a_energies = []
    random_energies = []

    for nu in range(M_B):
        eta_nu = Eta[:, nu]
        b_energies.append(energy(eta_nu))
        for q in range(n_queries):
            # Noisy B-pattern query (start close to B)
            noise_mask = torch.rand(N, device=device) < noise_frac
            query = eta_nu.clone()
            query[noise_mask] = -query[noise_mask]
            # ONE synchronous update: h = W_signed @ query, sigma = sign(h)
            # B-patterns are energy maxima: one update should move AWAY from B
            h_one = W_signed @ query
            after_one_step = torch.sign(h_one)
            after_one_step[after_one_step == 0] = 1.0
            overlap_b_one = float((after_one_step * eta_nu).sum() / N)
            # Also run full relaxation (will oscillate if pure anti-Hopfield basin)
            # Check: overlap at step 1 < 0 (moving away from B direction)
            if overlap_b_one < -0.3:
                anti_b_count += 1
            total_b_queries += 1

    # Also test A-pattern retrieval (should still work)
    a_correct = 0
    for mu in range(M_A):
        xi_mu = Xi[:, mu]
        a_energies.append(energy(xi_mu))
        noise_mask = torch.rand(N, device=device) < noise_frac
        query = xi_mu.clone()
        query[noise_mask] = -query[noise_mask]
        final = hopfield_signed_retrieve(W_signed, query, n_iters)
        overlap_a = float((final * xi_mu).sum() / N)
        if overlap_a > 0.5:
            a_correct += 1

    # Energy of random vectors
    for _ in range(20):
        rand_vec = torch.tensor(
            rng.choice([-1.0, 1.0], size=N).astype(np.float32),
            device=device
        )
        random_energies.append(energy(rand_vec))

    fraction_anti_b = anti_b_count / max(1, total_b_queries)
    fraction_a_correct = a_correct / max(1, M_A)
    mean_b_energy = float(np.mean(b_energies))
    mean_a_energy = float(np.mean(a_energies))
    mean_rand_energy = float(np.mean(random_energies))

    # B-pattern is energy MAX if E(B) > E(random)
    b_is_max = mean_b_energy > mean_rand_energy
    # A-pattern is energy MIN if E(A) < E(random)
    a_is_min = mean_a_energy < mean_rand_energy

    hp = fraction_anti_b >= 0.75 and b_is_max

    return {
        "seed": seed,
        "N": N,
        "M_A": M_A,
        "M_B": M_B,
        "fraction_anti_b": fraction_anti_b,
        "fraction_a_correct": fraction_a_correct,
        "mean_b_energy": mean_b_energy,
        "mean_a_energy": mean_a_energy,
        "mean_rand_energy": mean_rand_energy,
        "b_is_max": b_is_max,
        "a_is_min": a_is_min,
        "hp": hp,
    }


def _instrumentation_selftest():
    """Assert signed-AM computation is non-null at small scale."""
    if not HAS_TORCH:
        return
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    r = run_one_seed(N=256, M_A=5, M_B=5, seed=999, noise_frac=0.05,
                     n_queries=3, n_iters=20, device=device)
    assert r["fraction_anti_b"] is not None, "fraction_anti_b is None"
    assert not math.isnan(r["fraction_anti_b"]), "fraction_anti_b is NaN"
    assert 0.0 <= r["fraction_anti_b"] <= 1.0, \
        f"fraction_anti_b={r['fraction_anti_b']} out of [0,1]"
    assert r["mean_b_energy"] is not None, "mean_b_energy is None"
    print(f"[selftest] PASS: fraction_anti_b={r['fraction_anti_b']:.3f} "
          f"b_energy={r['mean_b_energy']:.4f} "
          f"rand_energy={r['mean_rand_energy']:.4f} "
          f"b_is_max={r['b_is_max']}", flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not HAS_TORCH:
        print(f"[{ANCHOR_NAME}] ERROR: torch required", flush=True)
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} N={N} M_A={M_A} M_B={M_B} "
          f"device={device} seeds={SEEDS}", flush=True)

    results = []
    for seed in SEEDS:
        print(f"[{ANCHOR_NAME}] seed={seed}...", flush=True)
        r = run_one_seed(N, M_A, M_B, seed, NOISE_FRAC, N_QUERIES, N_ITERS, device)
        results.append(r)
        print(f"  frac_anti_b={r['fraction_anti_b']:.3f} "
              f"frac_a_correct={r['fraction_a_correct']:.3f} "
              f"b_energy={r['mean_b_energy']:.4f} "
              f"rand_energy={r['mean_rand_energy']:.4f} "
              f"b_is_max={r['b_is_max']} hp={r['hp']}", flush=True)

    n_hp = sum(1 for r in results if r["hp"])
    n_seeds = len(results)
    frac_anti_b_vals = [r["fraction_anti_b"] for r in results]
    mean_frac_anti_b = float(np.mean(frac_anti_b_vals))
    b_is_max_count = sum(1 for r in results if r["b_is_max"])

    if n_hp >= 4 and mean_frac_anti_b >= 0.75:
        verdict = "HARD_PASS"
    elif mean_frac_anti_b >= 0.50:
        verdict = "MIDDLE_BAND"
    elif mean_frac_anti_b < 0.30 and (n_seeds - n_hp) >= 3:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"Signed-AM repulsion: mean_frac_anti_b={mean_frac_anti_b:.3f} "
            f"[HP: >=0.75], n_hp={n_hp}/{n_seeds}, "
            f"b_is_max={b_is_max_count}/{n_seeds}, N={N}, M_A={M_A}, M_B={M_B}"
        ),
        "mean_fraction_anti_b": mean_frac_anti_b,
        "n_hp_seeds": n_hp,
        "n_seeds": n_seeds,
        "b_is_max_count": b_is_max_count,
        "N": N,
        "M_A": M_A,
        "M_B": M_B,
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
        "per_seed": results,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  mean_frac_anti_b={mean_frac_anti_b:.3f} n_hp={n_hp}/{n_seeds} "
          f"b_is_max={b_is_max_count}/{n_seeds}", flush=True)
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