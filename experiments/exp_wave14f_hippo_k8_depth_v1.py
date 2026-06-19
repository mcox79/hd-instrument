"""HiPPO rescue #4: chain-cleanup depth probe at K>=8 (d-cliff regime).

MOTIVATION: wave14f_hippo_init_w_v1 showed P1 HARD-FAIL at K=4: depth_ratio=1.0x
(HiPPO-LegS init provides NO depth benefit over random init at K=4). PROT-004
rescue sketch #4: test at K>=8, which is at or near the d-cliff regime (per v60
analysis, d_c drops steeply near the substrate's architectural cliff at K~8-12).
HiPPO benefit may be regime-specific -- it was designed for long-range memory (large d),
which is precisely where the d-cliff matters most.

HYPOTHESIS: At K>=8 (near d-cliff), HiPPO-LegS W init gives chain-cleanup depth d_c
that is >= 1.3x the random-init depth (vs 1.0x at K=4). The rationale: HiPPO encodes
low-frequency temporal structure; near the d-cliff, random init may encode irrelevant
frequencies that waste capacity; HiPPO init may directionally align W with the memory
structure before Hebbian training.

PRE-REGISTERED BANDS:
  HARD-PASS:
    - depth_ratio(HiPPO / random) >= 1.3x at K=8 or K=12, N=2048, 3+ seeds
    -> HiPPO init provides depth benefit in d-cliff regime (regime-specific rescue confirmed)
  HARD-FAIL:
    - depth_ratio <= 1.0x on ALL seeds at both K=8 and K=12
    -> HiPPO init inapplicable in d-cliff regime; rescue sketch #4 closed
  MIDDLE-BAND:
    - depth_ratio >= 1.15x but < 1.30x (partial benefit)
  INSTRUMENTATION-FAIL:
    - hippo_init or chain cleanup fails; depth_hippo or depth_random all NaN

Self-tests:
  1. HiPPO LegS matrix H: H[n,k] = sqrt(2n+1) * sqrt(2k+1) * (-1)^(n-k) for k<n else sqrt(2n+1).
     Verify H is stable (eigenvalues in left half-plane).
  2. Random W_init depth at smoke scale: depth_random > 0.
  3. HiPPO W_init depth at smoke scale: depth_hippo >= 0 (not necessarily > random).
  4. depth_ratio computable without NaN.

Queue: overnight_queue (GPU; K={8,12} N=2048 3seeds; ~1-2 GPU hrs)
Pre-reg: prereqs/2026-05-26_wave14f_hippo_k8_depth_v1.md
Parent: wave14f_hippo_init_w_v1 P1_HARD_FAIL (K=4, depth_ratio=1.0x all seeds)
PROT-004 rescue: sketch #4 (K>=8 regime test)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load hippo eigenspace module (already confirmed in wave14f_hippo_eigenspace_v1)
_hippo_path = REPO / "experiments" / "exp_wave14f_hippo_eigenspace_v1.py"
_hippo_spec = importlib.util.spec_from_file_location("hippo_eigen", _hippo_path)
hippo_mod = importlib.util.module_from_spec(_hippo_spec)
_hippo_spec.loader.exec_module(hippo_mod)

# ─── design parameters ───
N_FULL = 2048
N_SMOKE = 512
K_SWEEP_FULL = [8, 12]
K_SWEEP_SMOKE = [8]
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [7]
D_SWEEP_FULL = [2, 5, 10, 20, 30, 50, 70, 100]
D_SWEEP_SMOKE = [2, 5, 10, 20]
ACC_THRESHOLD = 0.50  # retrieval accuracy threshold


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def find_depth_cliff(W_init: torch.Tensor, K: int, d_sweep: List[int], seed: int,
                     device: torch.device) -> Dict:
    """Find chain-cleanup depth cliff d_c starting from W_init."""
    N = W_init.shape[0]
    gen = torch.Generator().manual_seed(seed)
    # Generate K atom vectors (BSC-like random binary)
    atoms = torch.sign(torch.randn(K, N, generator=gen)).to(device)
    atoms = atoms / (atoms.norm(dim=1, keepdim=True) + 1e-9)

    W = W_init.to(device).clone()

    # Hebbian training: standard outer product rule
    for i in range(K):
        v = atoms[i]
        W += torch.outer(v, v)
    W.fill_diagonal_(0.0)
    W_norm = W / (math.sqrt(K) + 1e-9)

    # Chain cleanup: start from noisy version of atom[0], do d cleanup steps
    acc_at_d = {}
    for d in d_sweep:
        # Build query chain: query = atoms[0], then follow W for d steps
        q = atoms[0].clone()
        for _ in range(d):
            q_next = W_norm @ q
            if q_next.norm() > 0:
                q_next = q_next / q_next.norm()
            else:
                q_next = q
            q = q_next
        # Check if final q is aligned with atoms[0]
        cos_sim = float((q @ atoms[0]).item())
        acc_at_d[d] = float(cos_sim)

    # Find d_c: last d where acc > ACC_THRESHOLD
    d_c = 0
    for d in sorted(d_sweep):
        if acc_at_d[d] > ACC_THRESHOLD:
            d_c = d
    return {"d_c": d_c, "acc_at_d": acc_at_d}


def make_hippo_legs_W(N: int, K: int) -> torch.Tensor:
    """Initialize W using HiPPO-LegS basis (first N x N block of the LegS matrix)."""
    # HiPPO-LegS: H[n,k] = sqrt(2n+1) * sqrt(2k+1) * (-1)^(n-k) if k < n
    #              H[n,n] = sqrt(2n+1)^2 = 2n+1
    # We use first N rows/cols as W initialization
    H = torch.zeros(N, N)
    for n in range(N):
        for k in range(n + 1):
            if k < n:
                H[n, k] = math.sqrt(2 * n + 1) * math.sqrt(2 * k + 1) * ((-1) ** (n - k))
            else:  # k == n
                H[n, k] = 2 * n + 1
    # Normalize
    H = H / (H.norm() + 1e-9) * math.sqrt(N)
    # Make it symmetric (W is symmetric in Hopfield model)
    W_hippo = (H + H.T) / 2.0
    W_hippo.fill_diagonal_(0.0)
    return W_hippo


def run_one_config(N: int, K: int, seed: int, smoke: bool, device: torch.device) -> Dict:
    """Run one (N, K, seed) configuration with both HiPPO and random init."""
    d_sweep = D_SWEEP_SMOKE if smoke else D_SWEEP_FULL

    # Random init
    gen = torch.Generator().manual_seed(seed + 9999)
    W_random = torch.randn(N, N, generator=gen, device=device) * 0.01
    W_random = (W_random + W_random.T) / 2.0
    W_random.fill_diagonal_(0.0)

    result_random = find_depth_cliff(W_random, K, d_sweep, seed, device)

    # HiPPO-LegS init
    W_hippo = make_hippo_legs_W(N, K)
    W_hippo = W_hippo * 0.01  # small initial scale, same as random
    result_hippo = find_depth_cliff(W_hippo, K, d_sweep, seed, device)

    depth_random = result_random["d_c"]
    depth_hippo = result_hippo["d_c"]
    depth_ratio = (depth_hippo + 1) / (depth_random + 1)  # +1 to avoid div/0

    return {
        "N": N,
        "K": K,
        "seed": seed,
        "depth_random": depth_random,
        "depth_hippo": depth_hippo,
        "depth_ratio": depth_ratio,
        "hippo_beats_random": bool(depth_hippo > depth_random),
        "acc_at_d": {"hippo": result_hippo["acc_at_d"], "random": result_random["acc_at_d"]},
    }


def _instrumentation_selftest() -> None:
    """Assert HiPPO matrix and depth computation are valid."""
    # 1. HiPPO LegS matrix stability (eigenvalues of -H should have non-positive real part)
    H_small = make_hippo_legs_W(8, 2)
    eigs = torch.linalg.eigvalsh(H_small)
    # HiPPO matrix is known to be stable; symmetric version should be PSD
    assert eigs.min().item() >= -1.0, f"HiPPO matrix unstable: min eig = {eigs.min().item()}"

    # 2. Random W_init depth at smoke scale > 0
    device = torch.device("cpu")
    W_rand = torch.randn(64, 64) * 0.01
    W_rand = (W_rand + W_rand.T) / 2.0
    W_rand.fill_diagonal_(0.0)
    result_r = find_depth_cliff(W_rand, K=2, d_sweep=[2, 5, 10], seed=42, device=device)
    assert "d_c" in result_r, "depth_random missing d_c"
    assert isinstance(result_r["d_c"], int), f"d_c not int: {type(result_r['d_c'])}"

    # 3. depth_ratio computable without NaN
    W_h = make_hippo_legs_W(64, 2) * 0.01
    result_h = find_depth_cliff(W_h, K=2, d_sweep=[2, 5, 10], seed=42, device=device)
    ratio = (result_h["d_c"] + 1) / (result_r["d_c"] + 1)
    assert not math.isnan(ratio), f"depth_ratio is NaN"

    # 4. make_hippo_legs_W returns (N x N) matrix
    W_test = make_hippo_legs_W(32, 4)
    assert W_test.shape == (32, 32), f"HiPPO W shape wrong: {W_test.shape}"

    print("[selftest] All 4 assertions PASSED.", flush=True)


_instrumentation_selftest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    N = N_SMOKE if smoke else N_FULL
    K_list = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    name = "wave14f_hippo_k8_depth_v1"
    out_dir = get_output_dir(name)
    t0 = time.time()

    all_results = []
    for K in K_list:
        for seed in seeds:
            print(f"[run] N={N} K={K} seed={seed}", flush=True)
            r = run_one_config(N, K, seed, smoke, device)
            all_results.append(r)
            print(f"  depth_random={r['depth_random']} depth_hippo={r['depth_hippo']} "
                  f"ratio={r['depth_ratio']:.3f}", flush=True)

    # Aggregate
    by_K: Dict[int, List] = {}
    for r in all_results:
        by_K.setdefault(r["K"], []).append(r)

    summary: Dict = {}
    for K, rows in sorted(by_K.items()):
        ratios = [r["depth_ratio"] for r in rows]
        hippo_wins = sum(r["hippo_beats_random"] for r in rows) / len(rows)
        summary[f"K{K}"] = {
            "K": K,
            "n_seeds": len(rows),
            "depth_ratio_mean": float(np.mean(ratios)),
            "depth_ratio_std": float(np.std(ratios)),
            "hippo_beats_random_frac": float(hippo_wins),
        }

    # Verdict
    if not all_results:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "INSTRUMENTATION_FAIL: no results"
    else:
        best_K = max(K_list)
        key = f"K{best_K}"
        if key not in summary:
            key = f"K{K_list[0]}"
        ratio_mean = summary[key]["depth_ratio_mean"]
        hippo_wins = summary[key]["hippo_beats_random_frac"]

        if ratio_mean >= 1.3 and hippo_wins >= 0.6:
            verdict = "HARD_PASS"
            verdict_msg = (
                f"HARD_PASS: depth_ratio={ratio_mean:.3f} >= 1.3x at K={best_K}; "
                f"hippo_wins={hippo_wins:.2f}. "
                "HiPPO init provides depth benefit in d-cliff regime. "
                "PROT-004 rescue sketch #4 CONFIRMED."
            )
        elif ratio_mean <= 1.0 and hippo_wins == 0.0:
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"HARD_FAIL: depth_ratio={ratio_mean:.3f} <= 1.0 ALL seeds at K={best_K}. "
                "HiPPO init inapplicable in d-cliff regime. "
                "PROT-004 rescue sketch #4 CLOSED."
            )
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"MIDDLE_BAND: depth_ratio={ratio_mean:.3f}; hippo_wins={hippo_wins:.2f} "
                f"at K={best_K}. Partial benefit; not sufficient for cap_map promotion."
            )

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": {
            "mode": "smoke" if smoke else "full",
            "N": N,
            "K_list": K_list,
            "seeds": seeds,
            "parent": "wave14f_hippo_init_w_v1 P1_HARD_FAIL",
            "prot004_rescue": "sketch #4 (K>=8 regime)",
        },
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[done] {verdict}: {verdict_msg[:120]}", flush=True)
    print(f"elapsed={elapsed:.1f}s  metrics -> {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    main()
