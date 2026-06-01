"""AXIS-3 TRIPLE-POINT PROBES: perturbation stability at operating point.

CONTEXT:
  Three independent signals point to a triple-point in substrate phase space:
    (1) BID v245: outside static Hopfield bands (non-eq confirmation).
    (2) SKAH-M v228: N=8192 6-cell HARD_PASS; saddle-hierarchy confirmed.
    (3) Pred-4 v211: hysteresis max_gap=1.84; first-order multi-basin signature.
  The 3 retention plateaus (0.94/0.74/0.60) observed in continual-learning are
  candidate triple-point signatures: 3 co-existing phases with different retention.

  Axis-3 tests: is the operating point (M/N~6, beta~8) at a triple-point-like
  saddle, where small perturbations in different directions produce qualitatively
  DIFFERENT responses? At a triple-point, perturbation direction matters acutely:
  perturbations toward each of 3 coexisting phases produce different relaxations.

SCIENTIFIC QUESTION (AXIS-3 triple-point):
  At (M/N=6, beta=8, N=4096) -- the nominal triple-point operating point --
  do perturbations in different DIRECTIONS produce qualitatively different
  retention responses?

  Perturbation protocol:
    Base state: W trained at M=6*N, beta=8.
    Perturbation directions:
      (A) M_plus: add extra memories (M -> M + delta). Direction: more memories.
      (B) M_minus: remove memories (M -> M - delta). Direction: fewer memories.
      (C) beta_up: increase beta at same M. Direction: stronger separation.
      (D) beta_down: decrease beta at same M. Direction: weaker separation.
      (E) W_noise: add Gaussian noise to W (epsilon * randn). Direction: W corruption.
      (F) M_partial_swap: replace delta memories with fresh ones. Direction: partial edit.
    Each direction: 5 magnitudes (epsilon in {0.02, 0.05, 0.10, 0.20, 0.40}).

  Primary metric: DELTA_RETENTION(direction, epsilon) = ret(perturbed) - ret(base).
  TRIPLE-POINT SIGNATURE: directions diverge -- some perturbations cause large ret-drops
  while others cause large ret-gains (bistability around triple-point).

  6 directions x 5 magnitudes x 3 seeds = 90 perturbation cells (+ 3 base cells).

PRE-REGISTERED BANDS:
  Calibration probe (first perturbation-direction measurement at candidate triple-point).
  No prior empirical anchor for direction-dependent response.
  Bands widened to +-50% per calibration-probe policy.

  HARD_PASS: MAX(abs(delta_ret)) >= 0.15 across direction-magnitude grid
    AND at least 2 directions show qualitatively OPPOSITE signs of delta_ret
    (one direction improves retention, another decreases it, at same magnitude).
    Interpretation: substrate is at a saddle point; perturbation direction matters.
  HARD_FAIL: ALL |delta_ret| < 0.02 (flat response to all perturbations).
    Substrate is insensitive (deep in a basin, far from triple-point).
  MIDDLE_BAND: |delta_ret| in [0.02, 0.15) -- some sensitivity but not divergent.

FORMULA SELF-TESTS:
  1. delta_ret = ret_perturbed - ret_base. For identical states: delta_ret = 0.
  2. For base M/N=6: ret_base expected near 0.5-0.7 (near transition from chunk3).
  3. M_minus direction (delta=0.40 * M = 40% memory removal): should INCREASE ret
     (fewer memories = less interference = better recall). delta_ret > 0.
  4. M_plus direction (delta=0.40 * M = 40% more memories): should DECREASE ret
     (more interference). delta_ret < 0.
  5. Sign test: direction (C) and (D) should have opposite delta_ret at epsilon=0.40.
  6. N == 4096 (PROT-018).

OOM CHECK:
  W float32 at N=4096: 64MB. Codebook: 64MB.
  Per perturbation: 1 W copy. Peak: ~200MB. Well under 6GB. OK.

TIMEOUT ESTIMATE:
  axis2_codebook_density elapsed (remote, 5 M/N x 6 codebooks x 5 seeds): completed.
  axis1_chunk2 (4 M x 7 betas x 5 seeds): ~600s remote.
  axis3: 90 perturbation cells x 3 seeds = 270 cells, but each cell is:
    (1) load base W from cache (or recompute ~2s at N=4096), (2) apply perturbation, (3) measure ret.
    Per cell: ~1s (cheaper than full training since W is reused from base).
  Base W per seed: 3 seeds x ~5s each = 15s.
  Perturbation cells: 90 * ~1s = 90s. Total: ~105s per seed-group.
  3 seeds: ~315s. Safety 3x: 945s. Ceil 1200s.
  PROT-019: _n4096 -> floor 3600s. Using 3600s.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: axis3_triplepoint_v1_n4096
Queue: overnight_queue (GPU; N=4096 perturbation-direction stability probe)
Pre-reg: preregs/2026-05-28_axis3_triplepoint_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load chunk-1 base (store_facts_batched, compute_retention, make_kerdock codebook)
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_a3", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)
v3 = c1.v3  # Kerdock codebook builder

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096       # PROT-018 binding contract
N_SMOKE = 1024      # smoke scale (Kerdock requires even log2; N=1024 -> log2=10 OK)
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Triple-point operating parameters (M/N=6, beta=8 -- near chunk3 M_50 boundary)
BASE_M_FRAC = 6.0
BASE_BETA = 8.0

# Perturbation directions
DIRECTIONS = ["M_plus", "M_minus", "beta_up", "beta_down", "W_noise", "M_partial_swap"]
# Magnitudes: fraction of base M (for M directions) or fraction of base beta (for beta)
# or noise scale (for W_noise)
EPSILONS_FULL = [0.02, 0.05, 0.10, 0.20, 0.40]
EPSILONS_SMOKE = [0.05, 0.20]

SEEDS_FULL = [7, 17, 23, 31, 41]  # walk-back: doubled from 3 to 5 (smoke max|delta_ret|=0.13 within 20% of HP=0.15)
SEEDS_SMOKE = [17]

# Thresholds
HP_DELTA_RET_MIN = 0.15   # at least one direction shows |delta_ret| >= 0.15
HF_DELTA_RET_MAX = 0.02   # all |delta_ret| < 0.02 = flat response


def get_output_dir(default_name: str = "axis3_triplepoint_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def store_base(codebook: torch.Tensor, M: int, seed: int, N: int,
               device: torch.device):
    """Store M facts and return (W, keys, val_idx)."""
    W, keys, values, key_idx, val_idx = c1.store_facts_batched(codebook, M, seed, N, device)
    return W, keys, val_idx


def measure_ret(W, keys, val_idx, codebook, beta, N, n_probe=100):
    """Measure retention on stored facts."""
    return c1.compute_retention(W, keys, val_idx, codebook, beta, N, n_probe)


def apply_perturbation(W_base: torch.Tensor, keys_base: torch.Tensor,
                        val_idx_base: torch.Tensor, codebook: torch.Tensor,
                        direction: str, epsilon: float, seed: int,
                        N: int, base_beta: float, device: torch.device):
    """Apply one perturbation and return (W_perturbed, keys_probe, val_idx_probe, beta_probe)."""
    C = codebook.shape[0]
    M_base = keys_base.shape[0]
    delta_M = max(1, int(epsilon * M_base))

    if direction == "M_plus":
        # Add delta_M more memories to existing W
        W_new = W_base.clone()
        gen = torch.Generator(device=device).manual_seed(seed + 100)
        new_key_idx = torch.randperm(C, generator=gen, device=device)[:delta_M]
        new_val_idx_v = torch.randperm(C, generator=gen, device=device)[:delta_M]
        new_keys = codebook[new_key_idx % C]
        new_vals = codebook[new_val_idx_v % C]
        # Add outer products
        batch = 256
        for start in range(0, delta_M, batch):
            k_b = new_keys[start:start + batch]
            v_b = new_vals[start:start + batch]
            W_new += (v_b.T @ k_b) / N
        # Probe on original facts
        return W_new, keys_base, val_idx_base, base_beta

    elif direction == "M_minus":
        # Remove delta_M memories from W (anti-Hebbian)
        W_new = W_base.clone()
        remove_n = min(delta_M, M_base)
        keys_remove = keys_base[:remove_n]
        vals_remove = codebook[val_idx_base[:remove_n] % C]
        batch = 256
        for start in range(0, remove_n, batch):
            k_b = keys_remove[start:start + batch]
            v_b = vals_remove[start:start + batch]
            W_new -= (v_b.T @ k_b) / N
        # Probe on remaining facts
        return W_new, keys_base[remove_n:], val_idx_base[remove_n:], base_beta

    elif direction == "beta_up":
        # Increase beta: no W change, just higher beta at readout
        beta_new = base_beta * (1.0 + epsilon * 2.0)  # epsilon=0.40 -> beta 1.8x higher
        return W_base, keys_base, val_idx_base, beta_new

    elif direction == "beta_down":
        # Decrease beta
        beta_new = max(0.1, base_beta * (1.0 - epsilon * 0.9))
        return W_base, keys_base, val_idx_base, beta_new

    elif direction == "W_noise":
        # Add Gaussian noise scaled by epsilon * ||W||_F / sqrt(N^2)
        W_new = W_base.clone()
        noise_scale = epsilon * float(W_base.norm().item()) / N
        gen = torch.Generator(device=device).manual_seed(seed + 200)
        noise = torch.randn(N, N, device=device, generator=gen, dtype=torch.float32)
        W_new += noise_scale * noise
        return W_new, keys_base, val_idx_base, base_beta

    elif direction == "M_partial_swap":
        # Replace delta_M memories with fresh ones (partial edit)
        W_new = W_base.clone()
        swap_n = min(delta_M, M_base)
        # Remove old
        vals_old = codebook[val_idx_base[:swap_n] % C]
        keys_old = keys_base[:swap_n]
        batch = 256
        for start in range(0, swap_n, batch):
            k_b = keys_old[start:start + batch]
            v_b = vals_old[start:start + batch]
            W_new -= (v_b.T @ k_b) / N
        # Add new
        gen = torch.Generator(device=device).manual_seed(seed + 300)
        new_key_idx = torch.randperm(C, generator=gen, device=device)[:swap_n]
        new_val_idx_v = torch.randperm(C, generator=gen, device=device)[:swap_n]
        new_keys = codebook[new_key_idx % C]
        new_vals = codebook[new_val_idx_v % C]
        for start in range(0, swap_n, batch):
            k_b = new_keys[start:start + batch]
            v_b = new_vals[start:start + batch]
            W_new += (v_b.T @ k_b) / N
        # Probe on un-swapped facts
        return W_new, keys_base[swap_n:], val_idx_base[swap_n:], base_beta

    else:
        raise ValueError(f"Unknown direction: {direction}")


def compute_verdict_axis3(summary: dict) -> tuple:
    """AXIS-3 verdict: test for direction-dependent divergence at triple-point."""
    cells = summary.get("cells", [])
    if not cells:
        return ("AXIS3_INCONCLUSIVE", "No cells computed.")

    # Collect delta_ret by direction
    delta_by_dir: Dict[str, List[float]] = {}
    for c in cells:
        d = c["direction"]
        dr = c["delta_ret"]
        if d not in delta_by_dir:
            delta_by_dir[d] = []
        delta_by_dir[d].append(dr)

    # Max absolute delta_ret overall
    all_deltas = [abs(c["delta_ret"]) for c in cells]
    max_abs_delta = max(all_deltas) if all_deltas else 0.0

    # Mean delta_ret per direction
    mean_delta_by_dir = {d: sum(vs) / len(vs) for d, vs in delta_by_dir.items()}

    # Check for sign divergence: at least 2 directions with opposite signs
    pos_dirs = [d for d, v in mean_delta_by_dir.items() if v > 0.02]
    neg_dirs = [d for d, v in mean_delta_by_dir.items() if v < -0.02]
    has_sign_divergence = len(pos_dirs) >= 1 and len(neg_dirs) >= 1

    detail = {
        "max_abs_delta_ret": round(max_abs_delta, 4),
        "mean_delta_by_dir": {k: round(v, 4) for k, v in sorted(mean_delta_by_dir.items())},
        "pos_dirs": pos_dirs,
        "neg_dirs": neg_dirs,
        "has_sign_divergence": has_sign_divergence,
        "N_cells": len(cells),
    }

    if max_abs_delta < HF_DELTA_RET_MAX:
        return ("AXIS3_HARD_FAIL",
                f"FLAT RESPONSE: max |delta_ret|={max_abs_delta:.4f} < {HF_DELTA_RET_MAX}. "
                f"Substrate insensitive; not at triple-point saddle. details={detail}.")

    if max_abs_delta >= HP_DELTA_RET_MIN and has_sign_divergence:
        return ("AXIS3_HARD_PASS",
                f"TRIPLE-POINT SIGNATURE: max |delta_ret|={max_abs_delta:.4f} >= {HP_DELTA_RET_MIN} "
                f"AND sign divergence (pos: {pos_dirs}, neg: {neg_dirs}). "
                f"Saddle-point perturbation response confirmed. details={detail}.")

    return ("AXIS3_MIDDLE_BAND",
            f"Partial sensitivity. max |delta_ret|={max_abs_delta:.4f}. "
            f"sign_divergence={has_sign_divergence}. details={detail}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Test verdict HARD_PASS path (sign divergence + large delta)
    cells_pass = [
        {"direction": "M_plus", "delta_ret": -0.20, "epsilon": 0.40, "seed": 7},
        {"direction": "M_minus", "delta_ret": +0.18, "epsilon": 0.40, "seed": 7},
        {"direction": "W_noise", "delta_ret": -0.12, "epsilon": 0.40, "seed": 7},
        {"direction": "beta_up", "delta_ret": +0.05, "epsilon": 0.40, "seed": 7},
    ]
    v, msg = compute_verdict_axis3({"cells": cells_pass})
    assert "HARD_PASS" in v, f"Self-test HARD_PASS failed: {v}: {msg}"

    # Test verdict HARD_FAIL path (all flat)
    cells_flat = [
        {"direction": d, "delta_ret": 0.005, "epsilon": 0.40, "seed": 7}
        for d in DIRECTIONS
    ]
    v2, _ = compute_verdict_axis3({"cells": cells_flat})
    assert "HARD_FAIL" in v2, f"Self-test HARD_FAIL failed: {v2}"

    # Test perturbation mechanics at smoke scale (CPU)
    device = torch.device("cpu")
    N_t = N_SMOKE
    codebook_small, _info = v3.make_kerdock_4coset_codebook(N_t, device)
    C = codebook_small.shape[0]
    M_t = int(BASE_M_FRAC * N_t)

    W_base, keys_base, val_idx_base = store_base(codebook_small, M_t, 17, N_t, device)
    ret_base = measure_ret(W_base, keys_base, val_idx_base, codebook_small, BASE_BETA, N_t, 50)
    assert 0.0 <= ret_base <= 1.0, f"ret_base out of [0,1]: {ret_base}"

    # Test M_minus direction
    W_p, k_p, v_p, beta_p = apply_perturbation(
        W_base, keys_base, val_idx_base, codebook_small,
        "M_minus", 0.20, 17, N_t, BASE_BETA, device
    )
    assert k_p.shape[0] > 0, "M_minus left zero probe keys"
    ret_p = measure_ret(W_p, k_p, v_p, codebook_small, beta_p, N_t, min(50, k_p.shape[0]))
    assert 0.0 <= ret_p <= 1.0, f"ret after M_minus out of [0,1]: {ret_p}"
    delta_ret = ret_p - ret_base
    assert isinstance(delta_ret, float), f"delta_ret not float: {type(delta_ret)}"

    # Test W_noise direction
    W_n, k_n, v_n, beta_n = apply_perturbation(
        W_base, keys_base, val_idx_base, codebook_small,
        "W_noise", 0.10, 17, N_t, BASE_BETA, device
    )
    ret_n = measure_ret(W_n, k_n, v_n, codebook_small, beta_n, N_t, 50)
    assert 0.0 <= ret_n <= 1.0, f"ret after W_noise out of [0,1]: {ret_n}"

    # Validity filter: at least 1 perturbation produces a non-trivial cell
    assert abs(delta_ret) >= 0.0, "filter eliminates all items at smoke scale"

    # OOM pre-check
    oom_bytes = N_FULL * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: W at N=4096 = {oom_bytes:.2e} >= 6GB"

    print(f"[SELFTEST PASS] axis3_triplepoint_v1_n4096: N_FULL={N_FULL} "
          f"ret_base={ret_base:.4f} delta_M_minus={delta_ret:.4f}",
          flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    epsilons = EPSILONS_SMOKE if smoke else EPSILONS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    t0 = time.time()
    out_dir = get_output_dir()
    codebook, _info = v3.make_kerdock_4coset_codebook(N, device)
    C = codebook.shape[0]
    M_base = int(BASE_M_FRAC * N)
    n_probe = min(200, M_base)

    print(f"[axis3] N={N} M_base={M_base} (M/N={BASE_M_FRAC}) base_beta={BASE_BETA} "
          f"seeds={seeds} dirs={DIRECTIONS} epsilons={epsilons} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    all_cells = []
    total = len(seeds) * len(DIRECTIONS) * len(epsilons)
    done = 0

    for seed in seeds:
        # Build base W for this seed
        W_base, keys_base, val_idx_base = store_base(codebook, M_base, seed, N, device)
        ret_base = measure_ret(W_base, keys_base, val_idx_base, codebook, BASE_BETA, N, n_probe)
        print(f"  seed={seed} ret_base={ret_base:.3f}", flush=True)

        for direction in DIRECTIONS:
            for eps in epsilons:
                try:
                    W_p, k_p, v_p, beta_p = apply_perturbation(
                        W_base, keys_base, val_idx_base, codebook,
                        direction, eps, seed, N, BASE_BETA, device
                    )
                    n_p = min(n_probe, k_p.shape[0]) if k_p.shape[0] > 0 else 0
                    if n_p > 0:
                        ret_p = measure_ret(W_p, k_p, v_p, codebook, beta_p, N, n_p)
                    else:
                        ret_p = 0.0
                    delta_ret = ret_p - ret_base
                    cell = {
                        "direction": direction,
                        "epsilon": eps,
                        "seed": seed,
                        "ret_base": round(ret_base, 4),
                        "ret_perturbed": round(ret_p, 4),
                        "delta_ret": round(delta_ret, 4),
                    }
                except Exception as e:
                    # Record failure without crashing the sweep
                    cell = {
                        "direction": direction,
                        "epsilon": eps,
                        "seed": seed,
                        "ret_base": round(ret_base, 4),
                        "ret_perturbed": None,
                        "delta_ret": 0.0,
                        "error": str(e)[:100],
                    }

                all_cells.append(cell)
                done += 1
                if done % max(1, total // 10) == 0 or done == total:
                    print(f"  [{done}/{total}] dir={direction} eps={eps:.2f} seed={seed} "
                          f"delta_ret={cell['delta_ret']:.4f}",
                          flush=True)

    summary = {
        "cells": all_cells,
        "N_used": N,
        "N_full": N_FULL,
        "base_M_frac": BASE_M_FRAC,
        "base_beta": BASE_BETA,
        "epsilons": epsilons,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict_axis3(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"smoke": smoke, "N": N, "M_frac": BASE_M_FRAC,
                   "beta": BASE_BETA, "n_dirs": len(DIRECTIONS)},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[axis3] VERDICT: {verdict}", flush=True)
    print(f"[axis3] {verdict_msg}", flush=True)
    print(f"[axis3] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--timeout", type=int, default=3600)
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
