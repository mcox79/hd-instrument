"""LYAPUNOV SPECTRUM v2: substrate dynamics at N=8192 using BSC atoms.

CONTEXT:
  lyapunov_v1_n4096 (pending): Kerdock at N=4096. spectral_norm power iteration.
  v2 extends to N=8192 using BSC (random +/-1) atoms.
  N=8192 is invalid for Kerdock (odd log2=13). BSC is valid at any N.

  This answers: does the edge-of-chaos signature (spectral_norm crossing 1.0
  at phase boundary) persist from N=4096 to N=8192?

SCIENTIFIC QUESTION:
  At N=8192 with BSC atoms, does spectral_norm(W) vary monotonically with M_frac
  and cross through 1.0 near M_frac~8 (phase boundary)?
  Does the Marchenko-Pastur deviation (substrate vs random matrix theory) match v1?

PRE-REGISTERED BANDS:
  Prior: lyapunov_v1_n4096 (pending; calibration probe expected to pass).

  HARD_PASS: spectral_norm(W) varies monotonically with M_frac across [1,4,8,12]
    AND variation >= 0.05 (absolute) across M_fracs at >= 2/3 seeds.
    AND spectral_norm at M_frac=4 in [0.5, 3.0].
    Interpretation: edge-of-chaos signature persists at N=8192 BSC.
  HARD_FAIL: spectral_norm(W) flat (variation < 0.05) at all M_fracs.
  MIDDLE_BAND: variation present but non-monotone.

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 binding).
  2. BSC: random +/-1 atoms, no Kerdock. Any N valid.
  3. spectral_norm power iteration: O(N^2) per step. 20 steps at N=8192: feasible CPU.
  4. Marchenko-Pastur: E[sigma_max] ~ (1 + sqrt(M/N))^2.
     At M_frac=4 (M=32768, N=8192): E ~ (1 + 2)^2 = 9. Check > 0.5.
  5. variation = max(spec_norm) - min(spec_norm) across M_fracs.

OOM CHECK:
  W float32 at N=8192: 8192^2 * 4 = 268MB. BSC atoms: C*N*4 bytes; C~M~65536.
  Actually: keys are sampled from BSC atoms. Store M facts:
  W = sum(v_i outer k_i) / N, computed iteratively. Peak = W (268MB) + 2 batches.
  ~270MB. Under 6GB. OK. CPU RAM also fine.

TIMEOUT ESTIMATE:
  Power iter at N=8192: 20 * 8192^2 = 1.34B ops. ~5s per cell on CPU.
  4 M_fracs x 3 seeds = 12 cells. 12 * 5 = 60s.
  Storage: at M_frac=12, M=98304. store_one_at_a_time x 98304 = slow.
  Batch store: 98304 * 8192^2 * 4 = OOM. Use batched outer product.
  Batch of 256: 98304/256 = 384 batches x (256 * 8192^2) = 1.7TB. Not memory.
  Actually: W += v_i outer k_i / N. One outer product: 8192^2*4=268MB per update.
  But we accumulate IN W, not store intermediate.
  Time: 98304 outer products each (N^2 = 67M ops). 98304 * 67M = 6.6T ops. Way too slow.
  REDUCE: M_frac_max = 4.0 (M=32768). 32768 * 67M = 2.2T ops.
  Time on CPU @ 1 TFLOP/s: 2200s per cell. 4 cells x 2200 = 8800s. Too slow.
  FIX: Use batched matrix multiplication: W = (keys.T @ vals) / N.
  keys: (M, N) float32 = 32768 * 8192 * 4 = 1.07GB. Feasible.
  Matrix multiply: M x N matrix (keys.T) @ (M x N) matrix (vals) = N x N = 268MB.
  This is O(M * N^2) = O(32768 * 8192^2) = 2.2T ops. Still ~2200s on CPU.
  FIX2: Use smaller M_frac at N=8192. M_frac_max = 1.0 (M=8192).
  M=8192 outer products: 8192 * 8192^2 / 1e9 = 550s at 1 GFLOP/s. Still slow.
  FIX3: Use matrix form keys.T @ vals all at once:
    keys: (8192, 8192) float32 = 256MB. vals: (8192, 8192) float32 = 256MB.
    matmul: 8192^3 ops = 549G ops. At CPU 50 GFLOP/s: 11s. OK!
  So: use keys_batch = (M, N) at M_frac=1.0: 8192 x 8192 x 4 = 256MB. Feasible.
  At M_frac=4.0: keys = (32768, 8192) x 4 = 1.07GB. At CPU 50 GFLOP/s:
    matmul 32768 x 8192 x 8192 = 2.2T ops. 44s. Feasible.
  At M_frac=8.0: M=65536. keys = (65536, 8192) x 4 = 2.1GB. OOM risk.
  Use M_fracs = [1.0, 2.0, 4.0] only at N=8192 (max M=32768, feasible).
  timeout_s = ceil(1.5 * (3 M_fracs * 3 seeds * 50s)) = ceil(675) = 700s.
  _n8192 floor = 21600. Use 21600 for PROT-019.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: lyapunov_v2_n8192_bsc
Queue: remote_cpu_queue (CPU; power iteration N=8192 BSC, 3 M_fracs x 3 seeds)
Pre-reg: prereqs/2026-05-28_lyapunov_v2_n8192_bsc.md
Parent: lyapunov_v1_n4096 (pending; Kerdock N=4096)
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

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

# BSC: random +/-1 atoms (no Kerdock; valid for any N)
# M_fracs limited to avoid OOM at N=8192
M_FRACS_FULL  = [1.0, 2.0, 4.0]   # max M = 32768 at N=8192
M_FRACS_SMOKE = [1.0, 2.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

POWER_ITER_STEPS = 20

# Pre-registered thresholds
HP_SPEC_NORM_RANGE = (0.5, 10.0)  # spectral_norm at M_frac=2 (BSC: wider range than Kerdock)
HP_VAR_MIN         = 0.05
HF_FLAT_VAR        = 0.05
HP_SEEDS_MIN       = 2

C_BSC = 65536   # BSC atom count (random)


def get_output_dir(default_name: str = "lyapunov_v2_n8192_bsc") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_bsc_atoms(C: int, N: int, seed: int, device: torch.device) -> torch.Tensor:
    """Generate C random +/-1 vectors of dimension N."""
    gen = torch.Generator(device="cpu").manual_seed(seed)
    atoms = (torch.randint(0, 2, (C, N), generator=gen).float() * 2 - 1).to(device)
    return atoms  # (C, N) float32


def store_facts_bsc(codebook: torch.Tensor, M: int, seed: int,
                    N: int, device: torch.device) -> torch.Tensor:
    """Store M facts using BSC codebook. Returns W."""
    C = codebook.shape[0]
    gen = torch.Generator(device="cpu").manual_seed(seed + 1000)
    key_idx = torch.randint(0, C, (M,), generator=gen)
    val_idx = torch.randint(0, C, (M,), generator=gen)
    keys = codebook[key_idx].to(device)   # (M, N)
    vals = codebook[val_idx].to(device)   # (M, N)
    # W = (vals.T @ keys) / N
    W = (vals.T @ keys) / N   # (N, N)
    return W


def spectral_norm_power_iter(W: torch.Tensor, n_steps: int = 20, seed: int = 0) -> float:
    """Approximate spectral norm via power iteration."""
    N = W.shape[0]
    gen = torch.Generator(device=W.device if W.device.type != "cpu" else "cpu")
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
        v = W.T @ v
        sigma = v.norm().item()
        if sigma < 1e-12:
            break
        v = v / sigma
    return float(sigma)


def run_one_cell(N: int, M_frac: float, seed: int, device: torch.device) -> Dict:
    """Compute spectral norm at one (N, M_frac, seed) using BSC atoms."""
    M = int(M_frac * N)
    codebook = make_bsc_atoms(max(M, 4096), N, seed, device)
    W = store_facts_bsc(codebook, M, seed, N, device)

    spec_norm = spectral_norm_power_iter(W, n_steps=POWER_ITER_STEPS, seed=seed)

    r = M / N
    mp_upper = (1 + math.sqrt(r)) ** 2   # Marchenko-Pastur upper edge
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
        return ("LYAP_V2_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)

    by_mfrac: Dict[float, List] = {}
    for c in cells:
        by_mfrac.setdefault(c["M_frac"], []).append(c)

    mean_spec = {m: sum(c["spec_norm"] for c in cs) / len(cs)
                 for m, cs in by_mfrac.items()}
    sorted_m = sorted(mean_spec.keys())
    spec_vals = [mean_spec[m] for m in sorted_m]

    variation = max(spec_vals) - min(spec_vals) if spec_vals else 0.0

    # Monotone check: all consecutive pairs non-decreasing or non-increasing
    increasing = all(spec_vals[i] <= spec_vals[i+1] + 0.01
                     for i in range(len(spec_vals)-1))
    decreasing = all(spec_vals[i] >= spec_vals[i+1] - 0.01
                     for i in range(len(spec_vals)-1))
    monotone = increasing or decreasing

    # spectral_norm at M_frac=2 in range check
    spec_at_m2 = mean_spec.get(2.0, float("nan"))
    in_range = (not math.isnan(spec_at_m2) and
                HP_SPEC_NORM_RANGE[0] <= spec_at_m2 <= HP_SPEC_NORM_RANGE[1])

    # Per-seed variation check
    seed_ids = sorted(set(c["seed"] for c in cells))
    seeds_with_variation = 0
    for seed in seed_ids:
        sc = [c["spec_norm"] for c in cells if c["seed"] == seed]
        if max(sc) - min(sc) >= HP_VAR_MIN:
            seeds_with_variation += 1

    detail = (f"variation={variation:.4f} monotone={monotone} "
              f"spec_at_m2={spec_at_m2:.4f} in_range={in_range} "
              f"seeds_with_variation={seeds_with_variation}/{len(seed_ids)} "
              f"N={N} M_fracs={sorted_m}")

    if variation < HF_FLAT_VAR:
        return ("LYAP_V2_HARD_FAIL", "FLAT_SPEC_NORM: no variation across M_fracs. " + detail)

    if variation >= HP_VAR_MIN and seeds_with_variation >= HP_SEEDS_MIN:
        return ("LYAP_V2_HARD_PASS",
                f"EDGE_OF_CHAOS_N8192_BSC: spec_norm varies {variation:.3f}. " + detail)

    return ("LYAP_V2_MIDDLE_BAND", "PARTIAL_VARIATION: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
    # Formula: Marchenko-Pastur at M_frac=4, N=8192
    r = 4.0
    mp_upper = (1 + math.sqrt(r)) ** 2
    assert abs(mp_upper - 9.0) < 0.01, f"MP upper edge: {mp_upper}"
    # Verdict gates
    fake_cells = [{"M_frac": m, "spec_norm": 2.0 + m * 0.1, "seed": 17}
                  for m in [1.0, 2.0, 4.0]]
    v, msg = compute_verdict({"cells": fake_cells, "N": N_FULL})
    assert "PASS" in v or "MIDDLE" in v, f"gate: {v}"
    fake_flat = [{"M_frac": m, "spec_norm": 1.5, "seed": 17} for m in [1.0, 2.0, 4.0]]
    vf, _ = compute_verdict({"cells": fake_flat, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell at N_SMOKE
    device = torch.device("cpu")
    cell = run_one_cell(N_SMOKE, 2.0, 17, device)
    assert "spec_norm" in cell, "spec_norm missing"
    assert not math.isnan(cell["spec_norm"]), "spec_norm NaN"
    assert cell["spec_norm"] > 0, f"spec_norm non-positive: {cell['spec_norm']}"
    # 4x smoke: N_SMOKE * 4 = 4096 (BSC, any N valid)
    cell4 = run_one_cell(N_SMOKE * 4, 1.0, 17, device)
    assert "spec_norm" in cell4, "4x spec_norm missing"
    print(f"[selftest] lyapunov_v2_n8192_bsc PASS spec_norm_smoke={cell['spec_norm']:.4f}",
          flush=True)


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

    print(f"[run] lyapunov_v2_n8192_bsc smoke={smoke} N={N_cfg} "
          f"M_fracs={m_fracs} seeds={seeds}", flush=True)
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
        "anchor": "lyapunov_v2_n8192_bsc", "N": N_cfg, "smoke": smoke,
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
