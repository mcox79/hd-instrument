"""L=3 nested substrate composition at moderate N.

SCIENTIFIC QUESTION:
  Does the substrate support L=3 nested Hopfield composition via Hadamard binding
  at moderate N (4096)?
  Research predicts L=3 is borderline (0.50-0.61 accuracy) at very light load alpha <= 0.02 per level.
  HP: end-to-end accuracy > 0.55 at alpha_per_level <= 0.02 in >= 3/5 seeds.
  HF: accuracy < 0.52 in >= 3/5 seeds (below random chance for MIDDLE label).

  L=3 architecture:
    Inner level (Level 1): W_1 encodes entities {xi_mu}. N=4096.
    Middle level (Level 2): W_2 encodes bound composites {phi_mu = h_mu (*) xi_mu}.
    Outer level (Level 3): W_3 encodes doubly-bound {psi_mu = g_mu (*) phi_mu}.
    where h_mu, g_mu are Hadamard codewords, (*) is elementwise multiply.
    Query: noisy psi, retrieve psi -> unbind g -> get phi -> unbind h -> get xi.
    Accuracy = <xi_final, xi_mu> / N (end-to-end overlap).

PRE-REGISTERED BANDS:
  HARD-PASS: end-to-end accuracy > 0.55 at alpha_per_level <= 0.02 in >= 3/5 seeds.
  MIDDLE: 0.52 <= accuracy <= 0.55.
  HARD-FAIL: accuracy < 0.52 in >= 3/5 seeds.
  Note: calibration probe; research predicts 0.50-0.61 range.
  HP at 0.55; HF at 0.52 (within 60% of HP range from floor).

DESIGN:
  N = 4096 (PROT-018 _n4096 binding).
  n_entities = 80 (alpha_per_level = 80/4096 ~ 0.0195, just below 0.02 target).
  3 levels, each with 80 composites.
  Hadamard codewords: rows of Walsh-Hadamard matrix of size 4096.
  Query noise: 10% bit flip on the outer level query.
  5 seeds.

OOM CHECK:
  W at N=4096: float32 = 4096^2 * 4B = 64MB per matrix.
  3 matrices (W_1, W_2, W_3) = 192MB. Well within 8GB GPU.

PROT-018: _n4096 suffix binding. Production N MUST equal 4096.
  Pre-ship audit: grep for N = 4096 confirms this script.

TIMEOUT ESTIMATE:
  GPU matmul at N=4096: W @ q (4096x1) fast.
  5 seeds * 80 composites * 3 hops = 1200 retrievals. Trivial.
  W construction: 5 * 3 * 80 patterns * 4096^2 / 4096 = fast.
  Smoke (N=512): ~3s. Full (N=4096): scaling ~(4096/512)^1.5 = 45x.
  ceil(1.5 * 3 * 45 * (5/2)) = ceil(506) -> timeout_s=600.

Anchor: l3_composition_v1
Queue: overnight_queue
Pre-reg: preregs/2026-06-01_l3_composition_v1.md
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

ANCHOR_NAME = "l3_composition_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# PROT-018: _n4096 binding
N = 4096

if N != 4096:
    raise RuntimeError(f"PROT-018: N={N} != 4096 (anchor suffix)")

N_ENTITIES = 80  # alpha_per_level = 80/4096 ~ 0.0195
NOISE_FRAC = 0.10

if RUN_MODE == "smoke":
    N_SMOKE = 512
    SEEDS = [7, 17]
    N_ENT_SMOKE = 10  # alpha ~ 0.02 at N=512
    N_ITERS = 3  # hopfield iterations per level
else:
    N_SMOKE = 512
    SEEDS = [7, 17, 23, 31, 41]
    N_ENT_SMOKE = N_ENTITIES
    N_ITERS = 5


def hadamard_rows(N: int, n_rows: int, device: "torch.device") -> "torch.Tensor":
    """Return first n_rows rows of Walsh-Hadamard matrix (normalized to +/-1)."""
    # Build by iterating H_2^{log2(N)}
    k = int(math.log2(N))
    assert 2**k == N, f"N must be power of 2, got {N}"
    H = torch.tensor([[1.0, 1.0], [1.0, -1.0]], device=device)
    for _ in range(k - 1):
        H = torch.kron(H, torch.tensor([[1.0, 1.0], [1.0, -1.0]], device=device))
    # H is N x N, rows are Walsh-Hadamard vectors
    return H[:n_rows, :]  # (n_rows, N)


def hopfield_retrieve(W: "torch.Tensor", query: "torch.Tensor",
                      n_iters: int) -> "torch.Tensor":
    """Synchronous Hopfield retrieval. query: (N,)."""
    sigma = query.clone()
    for _ in range(n_iters):
        sigma = torch.sign(W @ sigma)
        sigma[sigma == 0] = 1.0
    return sigma


def run_one_seed(N: int, n_entities: int, seed: int, noise_frac: float,
                 n_iters: int, device: "torch.device") -> Dict:
    rng = np.random.RandomState(seed)
    alpha = n_entities / N

    # Generate entities
    Xi_np = rng.choice([-1.0, 1.0], size=(N, n_entities)).astype(np.float32)
    Xi = torch.tensor(Xi_np, dtype=torch.float32, device=device)

    # Hadamard codewords for levels 2 and 3
    H = hadamard_rows(N, n_entities * 2, device)  # (2*n_entities, N)
    h_codes = H[:n_entities, :]   # Level 2 binding codes (n_entities, N)
    g_codes = H[n_entities:, :]   # Level 3 binding codes (n_entities, N)

    # Level 1: W_1 = sum xi xi^T / N
    W1 = (Xi @ Xi.t()) / N  # (N, N)

    # Level 2 composites: phi_mu = h_mu (*) xi_mu
    Phi_np = np.zeros((N, n_entities), dtype=np.float32)
    for mu in range(n_entities):
        xi_mu = Xi_np[:, mu]
        h_mu = h_codes[mu].cpu().numpy()
        Phi_np[:, mu] = xi_mu * h_mu
    Phi = torch.tensor(Phi_np, dtype=torch.float32, device=device)
    W2 = (Phi @ Phi.t()) / N  # (N, N)

    # Level 3 composites: psi_mu = g_mu (*) phi_mu
    Psi_np = np.zeros((N, n_entities), dtype=np.float32)
    for mu in range(n_entities):
        phi_mu = Phi_np[:, mu]
        g_mu = g_codes[mu].cpu().numpy()
        Psi_np[:, mu] = phi_mu * g_mu
    Psi = torch.tensor(Psi_np, dtype=torch.float32, device=device)
    W3 = (Psi @ Psi.t()) / N  # (N, N)

    # Query each entity through L=3 chain
    accuracies = []
    for mu in range(n_entities):
        psi_mu = Psi[:, mu]  # (N,)
        # Add noise
        noise_mask = torch.rand(N, device=device) < noise_frac
        query = psi_mu.clone()
        query[noise_mask] = -query[noise_mask]

        # Retrieve from W3 (outer level)
        psi_retrieved = hopfield_retrieve(W3, query, n_iters)
        # Unbind g_mu to get phi estimate
        phi_est = psi_retrieved * g_codes[mu]  # element-wise
        # Retrieve from W2 (middle level)
        phi_retrieved = hopfield_retrieve(W2, phi_est, n_iters)
        # Unbind h_mu to get xi estimate
        xi_est = phi_retrieved * h_codes[mu]  # element-wise
        # Retrieve from W1 (inner level)
        xi_final = hopfield_retrieve(W1, xi_est, n_iters)

        # Accuracy = overlap with true xi_mu
        xi_true = Xi[:, mu]
        acc = float((xi_final * xi_true).sum() / N)
        accuracies.append(acc)

    mean_acc = float(np.mean(accuracies))
    hp = mean_acc > 0.55

    return {
        "seed": seed,
        "N": N,
        "n_entities": n_entities,
        "alpha": alpha,
        "mean_accuracy": mean_acc,
        "std_accuracy": float(np.std(accuracies)),
        "min_accuracy": float(np.min(accuracies)),
        "max_accuracy": float(np.max(accuracies)),
        "hp": hp,
    }


def _instrumentation_selftest():
    """Assert L=3 accuracy is non-null and in valid range."""
    if not HAS_TORCH:
        return
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Tiny test: N=64 requires n_entities <= 64/2 (Hadamard codes)
    r = run_one_seed(N=256, n_entities=5, seed=999, noise_frac=0.05,
                     n_iters=3, device=device)
    assert r["mean_accuracy"] is not None, "mean_accuracy is None"
    assert not math.isnan(r["mean_accuracy"]), "mean_accuracy is NaN"
    assert 0.0 <= r["mean_accuracy"] <= 1.01, \
        f"accuracy={r['mean_accuracy']} out of [0,1]"
    assert r["n_entities"] == 5, "n_entities mismatch"
    print(f"[selftest] PASS: L=3 acc={r['mean_accuracy']:.3f} N=256 n_ent=5",
          flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not HAS_TORCH:
        print(f"[{ANCHOR_NAME}] ERROR: torch required", flush=True)
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Determine actual N based on RUN_MODE
    N_run = N_SMOKE if RUN_MODE == "smoke" else N
    n_ent = N_ENT_SMOKE if RUN_MODE == "smoke" else N_ENTITIES

    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} N={N_run} n_entities={n_ent} "
          f"device={device} seeds={SEEDS}", flush=True)
    print(f"  alpha_per_level={n_ent/N_run:.4f} noise_frac={NOISE_FRAC}", flush=True)

    results = []
    for seed in SEEDS:
        print(f"[{ANCHOR_NAME}] seed={seed}...", flush=True)
        r = run_one_seed(N_run, n_ent, seed, NOISE_FRAC, N_ITERS, device)
        results.append(r)
        print(f"  mean_acc={r['mean_accuracy']:.3f} "
              f"std={r['std_accuracy']:.3f} hp={r['hp']}", flush=True)

    n_hp = sum(1 for r in results if r["hp"])
    n_seeds = len(results)
    accs = [r["mean_accuracy"] for r in results]
    mean_acc = float(np.mean(accs))

    if n_hp >= 3 and mean_acc > 0.55:
        verdict = "HARD_PASS"
    elif mean_acc >= 0.52:
        verdict = "MIDDLE_BAND"
    elif mean_acc < 0.52 and n_seeds - n_hp >= 3:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"L=3 composition: mean_acc={mean_acc:.3f} [HP: >0.55], "
            f"n_hp={n_hp}/{n_seeds}, "
            f"N={N_run}, n_entities={n_ent}, alpha={n_ent/N_run:.4f}"
        ),
        "mean_accuracy": mean_acc,
        "n_hp_seeds": n_hp,
        "n_seeds": n_seeds,
        "N_production": N,
        "N_run": N_run,
        "n_entities": n_ent,
        "alpha_per_level": n_ent / N_run,
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
        "per_seed": results,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  mean_acc={mean_acc:.3f} n_hp={n_hp}/{n_seeds}", flush=True)
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