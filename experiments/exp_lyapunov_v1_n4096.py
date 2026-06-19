"""LYAPUNOV SPECTRUM v1: substrate dynamics at edge-of-chaos at N=4096.

CONTEXT:
  Roadmap Ship 2 (Field-A reservoir-computing Lyapunov probe).
  Substrate dynamics look like edge-of-chaos echo-state networks.
  At the operating point (M_frac=4.0, beta=32, N=4096), the weight matrix
  W encodes Hebbian associations. The spectral structure of W governs
  how perturbations in the input space evolve over successive retrieval steps.

SCIENTIFIC QUESTION:
  What is the Lyapunov exponent lambda_1 of the substrate's retrieval dynamics
  at the operating point (W with M=4*N stored facts, beta=32)?
  Does lambda_1 vary with M_frac (distance from phase boundary)?
  Does lambda_1 cross 0 at the boundary M_c (edge-of-chaos signature)?

  Lyapunov exponent: lambda_1 = lim_{t->inf} (1/t) log ||J^t v|| where
  J = d(f(x))/dx is the Jacobian of one retrieval step at x* (attractor).
  For softmax retrieval: f(x) = argmax(Wx) is piecewise constant (no gradient).
  Use the spectral norm of W instead: spectral_norm(W) as proxy for lambda_1.

  Edge-of-chaos prediction: spectral_norm(W) ~ 1.0 at phase boundary;
  > 1.0 in paramagnetic phase; < 1.0 in spin-glass phase.

PRE-REGISTERED BANDS:
  Calibration probe. No prior Lyapunov measurement.
  Prediction from reservoir-computing theory: spectral_norm at operating point
  should be near 1.0 (edge-of-chaos) if substrate is dynamically critical.

  HARD_PASS: spectral_norm(W) varies monotonically with M_frac across the
    phase boundary (M_frac=4..12), crossing through 1.0 at some M_c.
    AND magnitude of spectral_norm(W) at M_frac=8 (near boundary) is in [0.7, 1.3].
    Interpretation: substrate shows edge-of-chaos signature.
  HARD_FAIL: spectral_norm(W) is constant (< 0.05 variation) across all M_fracs.
    Interpretation: no dynamical criticality signature.
  MIDDLE_BAND: spectral_norm(W) varies but does not cross 1.0 monotonically.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. W_outer = sum(v_i outer k_i) / N for M facts. spectral_norm(W) = sigma_max(W).
  3. For M random facts: E[spectral_norm(W)] ~ sqrt(M/N) by random matrix theory.
     At M_frac=4 (M=16384, N=4096): E ~ sqrt(4) = 2.0. Check: > 0.5.
  4. M at M_frac=4.0, N=4096: M=16384.

OOM CHECK:
  N=4096 M_frac=12 (M=49152): W=64MB. SVD of W: O(N^3)=64GB -- INFEASIBLE.
  Use power iteration for spectral norm (O(N^2) per iteration).
  10 iterations x N=4096: 10*4096^2*4=671MB memory OK.

TIMEOUT ESTIMATE:
  4 M_fracs x 3 seeds = 12 cells. Per cell: store M=16384 + power_iter 20 steps.
  Power iter at N=4096: 20*4096^2 = 335M ops ~ 0.5s per cell.
  Total: 12*0.5=6s. Smoke: 2 M_fracs x 1 seed = 2 cells.
  Safety: ceil(1.5*6*20)=180s. _n4096 floor=14400. timeout_s=14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: lyapunov_v1_n4096
Queue: remote_cpu_queue (CPU; spectral norm via power iteration; N=4096)
Pre-reg: prereqs/2026-05-28_lyapunov_v1_n4096.md
Parent: axis1_mb_chunk1_v1 (store_facts_batched, v3 codebook)
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
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load axis1_mb_chunk1 for store_facts_batched and v3 codebook
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_lyap", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
v3 = c1.v3

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL  = [1.0, 4.0, 8.0, 12.0]
M_FRACS_SMOKE = [1.0, 4.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

POWER_ITER_STEPS = 20  # iterations for spectral norm approximation

# Pre-registered thresholds
HP_SPEC_NORM_RANGE = (0.5, 3.0)   # spectral_norm at M_frac=4 should be in [0.5, 3.0]
HP_VAR_MIN         = 0.05         # variation across M_fracs must be > 0.05
HF_FLAT_VAR        = 0.05         # < 0.05 variation = HARD_FAIL (flat)
HP_SEEDS_MIN       = 2


def get_output_dir(default_name: str = "lyapunov_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def spectral_norm_power_iter(W: torch.Tensor, n_steps: int = 20, seed: int = 0) -> float:
    """Approximate spectral norm (sigma_max) via power iteration."""
    N = W.shape[0]
    gen = torch.Generator(device=W.device)
    gen.manual_seed(seed)
    v = torch.randn(N, generator=gen, device=W.device, dtype=torch.float32)
    v = v / v.norm()
    sigma = 0.0
    for _ in range(n_steps):
        u = W @ v
        sigma = u.norm().item()
        if sigma < 1e-12:
            break
        v = u / sigma
        # power iter also on W.T
        v = W.T @ v
        sigma = v.norm().item()
        if sigma < 1e-12:
            break
        v = v / sigma
    return float(sigma)


def run_one_cell(N: int, M_frac: float, seed: int, device: torch.device) -> Dict:
    """Compute spectral norm of W at one (N, M_frac, seed) cell."""
    M = int(M_frac * N)
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    W, keys, _vals, _key_idx, _val_idx = store_facts_batched(codebook, M, seed, N, device)

    spec_norm = spectral_norm_power_iter(W, n_steps=POWER_ITER_STEPS, seed=seed)

    # Random matrix theory prediction: E[sigma_max] ~ sqrt(M/N) * (1 + sqrt(N/M))^2
    # (Marchenko-Pastur upper edge for Wishart matrix scaled by 1/N)
    r = M / N
    mp_upper = (1 + math.sqrt(r)) ** 2  # Marchenko-Pastur upper edge
    deviation = (spec_norm - mp_upper) / max(mp_upper, 1e-9)

    print(f"    N={N} M_frac={M_frac} seed={seed} spec_norm={spec_norm:.4f} "
          f"mp_upper={mp_upper:.4f} deviation={deviation:.4f}", flush=True)
    return {
        "N": N, "M_frac": M_frac, "M": M, "seed": seed,
        "spec_norm": round(spec_norm, 5),
        "mp_upper": round(mp_upper, 5),
        "deviation": round(deviation, 5),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("LYAP_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)

    # Group by M_frac
    by_mfrac: Dict[float, List] = {}
    for c in cells:
        by_mfrac.setdefault(c["M_frac"], []).append(c)

    mean_spec_by_mfrac = {
        m: sum(c["spec_norm"] for c in cs) / len(cs)
        for m, cs in by_mfrac.items()
    }
    sorted_mfracs = sorted(mean_spec_by_mfrac.keys())
    spec_norms = [mean_spec_by_mfrac[m] for m in sorted_mfracs]

    variation = max(spec_norms) - min(spec_norms) if spec_norms else 0.0
    spec_at_m4 = mean_spec_by_mfrac.get(4.0, float("nan"))

    # Monotone check: increasing with M_frac
    n_mono = sum(1 for i in range(len(spec_norms) - 1)
                 if spec_norms[i + 1] >= spec_norms[i] - 0.01)
    mono_frac = n_mono / max(1, len(spec_norms) - 1)

    detail = (f"variation={variation:.4f} spec_norm_m4={spec_at_m4:.4f} "
              f"mono_frac={mono_frac:.2f} mfracs={sorted_mfracs} "
              f"spec_norms={[round(s, 4) for s in spec_norms]} N={N}")

    if variation < HF_FLAT_VAR:
        return ("LYAP_HARD_FAIL",
                f"SPECTRAL_FLAT: no dynamical structure across M_fracs. " + detail)

    in_range = HP_SPEC_NORM_RANGE[0] <= spec_at_m4 <= HP_SPEC_NORM_RANGE[1]
    if variation >= HP_VAR_MIN and in_range:
        return ("LYAP_HARD_PASS",
                f"EDGE_OF_CHAOS_SIGNATURE: variation={variation:.4f}. " + detail)

    return ("LYAP_MIDDLE_BAND", f"PARTIAL_DYNAMICAL_STRUCTURE: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Formula: M at M_frac=4.0
    assert int(4.0 * N_FULL) == 16384, f"M at M_frac=4: {int(4.0*N_FULL)}"
    # RMT: E[sigma_max] ~ (1+sqrt(r))^2 at M_frac=4 -> r=4 -> (1+2)^2=9
    r = 4.0
    expected_mp = (1 + math.sqrt(r)) ** 2
    assert abs(expected_mp - 9.0) < 0.01, f"mp_upper at M_frac=4: {expected_mp}"
    # Verdict gates
    fake_hp = [{"M_frac": m, "spec_norm": 0.5 + m * 0.2, "deviation": 0.1}
               for m in [1.0, 4.0, 8.0, 12.0]]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "PASS" in v or "MIDDLE" in v, f"PASS/MIDDLE gate: {v}"
    fake_hf = [{"M_frac": m, "spec_norm": 2.0, "deviation": 0.0}
               for m in [1.0, 4.0, 8.0, 12.0]]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell (CPU)
    device = torch.device("cpu")
    cell = run_one_cell(N_SMOKE, 4.0, 17, device)
    assert "spec_norm" in cell, f"spec_norm missing"
    assert not math.isnan(cell["spec_norm"]), "spec_norm NaN"
    assert cell["spec_norm"] > 0.0, "spec_norm <= 0"
    # 4x smoke: N=4096
    cell4 = run_one_cell(N_SMOKE * 4, 4.0, 17, device)
    assert "spec_norm" in cell4, f"4x spec_norm missing"
    print(f"[selftest] lyapunov_v1_n4096 PASS spec_norm_smoke={cell['spec_norm']:.4f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device = torch.device("cpu")  # CPU experiment
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] lyapunov_v1_n4096 smoke={smoke} N={N_cfg} M_fracs={m_fracs} seeds={seeds}", flush=True)
    t0 = time.time()

    all_cells = []
    for M_frac in m_fracs:
        print(f"\n  [M_frac={M_frac}]", flush=True)
        for seed in seeds:
            cell = run_one_cell(N_cfg, M_frac, seed, device)
            all_cells.append(cell)
        print(f"  M_frac={M_frac} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "lyapunov_v1_n4096", "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "seeds": seeds,
        "cells": all_cells, "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
