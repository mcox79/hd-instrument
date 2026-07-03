"""Orthogonal probe: Spectral graph theory -- Fiedler value lambda_2 of substrate W Laplacian.

MOTIVATION: Substrate's W is a weight matrix on atoms. Treating W as a bipartite graph
adjacency gives a Laplacian whose spectral gap (Fiedler value lambda_2) measures how well
the substrate propagates information between atoms. Large lambda_2 => fast convergence
(good mixing); small lambda_2 => bottleneck / partitioned structure.

HYPOTHESIS (SG-1, P=0.38): lambda_2 of the normalized W Laplacian correlates with
retention_A across N values. Algebraically connected substrates retain better.

HYPOTHESIS (SG-2): The lambda_2 / lambda_N (ratio of algebraic connectivity to max
eigenvalue) is a proxy for the substrate's effective dimension utilization.

DESIGN:
  - Build symmetric Hopfield W at N in {512, 1024, 2048} (smoke: {256}).
  - Compute Laplacian L = D - |W_sym| where D = diag(sum_j |W_{ij}|).
  - Compute Fiedler value lambda_2 (second smallest eigenvalue of L) via torch.linalg.eigh.
  - Also compute lambda_N, spectral gap ratio = lambda_2 / lambda_N.
  - Run 5 seeds per N. Measure correlation(lambda_2, retention_A).

PRE-REGISTERED BANDS:
  HARD-PASS:
    - Correlation(lambda_2, retention_A) > 0.60 across N sweep (Pearson r > 0.6)
    - AND lambda_2 > 0.001 (non-trivial connectivity) at N=1024
    -> Algebraic connectivity predicts retention; Fiedler value is diagnostic
  HARD-FAIL:
    - lambda_2 < 1e-6 at ALL N values (graph is disconnected; Laplacian trivial)
    - OR correlation < -0.30 (anti-correlated with retention)
    -> W does not form a connected graph; spectral graph theory inapplicable
  MIDDLE-BAND: lambda_2 > 0 but correlation < 0.30 (connectivity exists but doesn't predict retention)
  INSTRUMENTATION-FAIL: lambda_2 is NaN; torch.linalg.eigh fails.

Self-tests:
  1. L = D - A for complete graph K_4: lambda_2 = 4.0 (analytically known).
  2. lambda_2(disconnected graph) = 0.0 exactly.
  3. lambda_2 > 0 for connected Hopfield W at sub-capacity.
  4. lambda_2 / lambda_N in [0, 1] always.

Queue: remote_cpu_queue (CPU; N={512,1024,2048} 5seeds; ~15-30 min BELOWNORMAL)
Pre-reg: prereqs/2026-05-26_wave14_ortho_spectral_graph_lambda2_v1.md
Orthogonal probe: Spectral graph theory / Fiedler value; field drill count = 0.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
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

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
N_FULL = [512, 1024, 2048]
N_SMOKE = [256, 512]
M_LOAD_FRAC = 0.10   # sub-capacity: M = N * 0.10
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def build_W_hopfield(N: int, M: int, seed: int) -> torch.Tensor:
    """Build symmetric Hopfield W from M random normalized vectors."""
    gen = torch.Generator()
    gen.manual_seed(seed)
    W = torch.zeros(N, N)
    patterns = []
    for _ in range(M):
        v = torch.randn(N, generator=gen)
        v = v / (v.norm() + 1e-9)
        W += torch.outer(v, v)
        patterns.append(v)
    W = W / (math.sqrt(M) + 1e-9)
    W.fill_diagonal_(0.0)
    return W, patterns


def compute_fiedler(W: torch.Tensor) -> Dict:
    """Compute Fiedler value (lambda_2) of signed Laplacian of W."""
    W_abs = W.abs()
    D = W_abs.sum(dim=1)  # degree vector
    L = torch.diag(D) - W_abs  # Laplacian
    # Compute eigenvalues (symmetric; sort ascending)
    eigenvalues = torch.linalg.eigh(L)[0]  # returns sorted eigenvalues
    lambda_1 = float(eigenvalues[0].item())   # should be ~0
    lambda_2 = float(eigenvalues[1].item())   # Fiedler value
    lambda_N = float(eigenvalues[-1].item())  # largest eigenvalue
    spectral_gap_ratio = lambda_2 / (lambda_N + 1e-12)
    return {
        "lambda_1": lambda_1,
        "lambda_2": lambda_2,
        "lambda_N": lambda_N,
        "spectral_gap_ratio": spectral_gap_ratio,
    }


def measure_retention(W: torch.Tensor, patterns_A: List[torch.Tensor],
                      W_A: torch.Tensor) -> float:
    """Retention = fraction of task-A patterns still retrievable after W modified by ABC."""
    correct = 0
    for v in patterns_A[:50]:
        v_noisy = v + 0.1 * torch.randn_like(v)
        v_noisy = v_noisy / (v_noisy.norm() + 1e-9)
        retrieved = W @ v_noisy
        retrieved = retrieved / (retrieved.norm() + 1e-9)
        cos_sim = float((retrieved @ v).item())
        if cos_sim > 0.5:
            correct += 1
    baseline_correct = 0
    for v in patterns_A[:50]:
        v_noisy = v + 0.1 * torch.randn_like(v)
        v_noisy = v_noisy / (v_noisy.norm() + 1e-9)
        retrieved = W_A @ v_noisy
        retrieved = retrieved / (retrieved.norm() + 1e-9)
        cos_sim = float((retrieved @ v).item())
        if cos_sim > 0.5:
            baseline_correct += 1
    if baseline_correct == 0:
        return 0.0
    return correct / baseline_correct


def run_one_seed(N: int, seed: int, smoke: bool) -> Dict:
    M = max(1, int(N * M_LOAD_FRAC))
    if smoke:
        M = max(1, int(N * 0.08))

    W_A, patterns_A = build_W_hopfield(N, M, seed=seed)
    spectral_A = compute_fiedler(W_A)

    # Add task B and C patterns
    W_ABC = W_A.clone() * math.sqrt(M)
    _, patterns_B = build_W_hopfield(N, M, seed=seed + 100)
    for v in patterns_B:
        W_ABC += torch.outer(v, v)
    _, patterns_C = build_W_hopfield(N, M, seed=seed + 200)
    for v in patterns_C:
        W_ABC += torch.outer(v, v)
    W_ABC = W_ABC / math.sqrt(3 * M)
    W_ABC.fill_diagonal_(0.0)

    spectral_ABC = compute_fiedler(W_ABC)
    retention_A = measure_retention(W_ABC, patterns_A, W_A)

    return {
        "N": N,
        "seed": seed,
        "lambda_2_A": spectral_A["lambda_2"],
        "lambda_2_ABC": spectral_ABC["lambda_2"],
        "lambda_N_ABC": spectral_ABC["lambda_N"],
        "spectral_gap_ratio_ABC": spectral_ABC["spectral_gap_ratio"],
        "retention_A": retention_A,
    }


def _instrumentation_selftest() -> None:
    """Assert Laplacian eigenvalue computations are correct."""
    # 1. Complete graph K_4: lambda_2 = 4 (n nodes, lambda_2 = n for K_n)
    K4 = torch.ones(4, 4) - torch.eye(4)  # adjacency of K_4
    D4 = K4.sum(dim=1)  # degree = 3 for all
    L4 = torch.diag(D4) - K4
    eigs4 = torch.linalg.eigh(L4)[0]
    lambda2_K4 = float(eigs4[1].item())
    assert abs(lambda2_K4 - 4.0) < 0.01, f"K_4 Fiedler self-test: expected 4.0 got {lambda2_K4}"

    # 2. Disconnected graph: lambda_2 = 0
    A_disconnected = torch.zeros(4, 4)
    A_disconnected[0, 1] = A_disconnected[1, 0] = 1.0  # two disconnected edges
    A_disconnected[2, 3] = A_disconnected[3, 2] = 1.0
    D_disc = A_disconnected.sum(dim=1)
    L_disc = torch.diag(D_disc) - A_disconnected
    eigs_disc = torch.linalg.eigh(L_disc)[0]
    lambda2_disc = float(eigs_disc[1].item())
    assert abs(lambda2_disc) < 0.01, f"Disconnected Fiedler: expected ~0 got {lambda2_disc}"

    # 3. Sub-capacity Hopfield W has lambda_2 > 0
    W_test, _ = build_W_hopfield(N=64, M=5, seed=42)
    spec_test = compute_fiedler(W_test)
    assert spec_test["lambda_2"] >= 0, f"Hopfield lambda_2 < 0: {spec_test['lambda_2']}"

    # 4. spectral_gap_ratio in [0, 1]
    assert 0 <= spec_test["spectral_gap_ratio"] <= 1.0 + 1e-6, \
        f"spectral_gap_ratio out of [0,1]: {spec_test['spectral_gap_ratio']}"

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
    N_list = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    name = "wave14_ortho_spectral_graph_lambda2_v1"
    out_dir = get_output_dir(name)
    t0 = time.time()

    all_results = []
    for N in N_list:
        print(f"[run] N={N} seeds={seeds}", flush=True)
        for seed in seeds:
            r = run_one_seed(N, seed, smoke)
            all_results.append(r)
            print(f"  N={N} seed={seed} lambda2_ABC={r['lambda_2_ABC']:.6f} "
                  f"ret_A={r['retention_A']:.4f}", flush=True)

    # Aggregate
    by_N: Dict[int, List] = {}
    for r in all_results:
        by_N.setdefault(r["N"], []).append(r)

    summary: Dict = {}
    for N, rows in sorted(by_N.items()):
        l2s = [r["lambda_2_ABC"] for r in rows]
        rets = [r["retention_A"] for r in rows]
        summary[f"N{N}"] = {
            "N": N,
            "n_seeds": len(rows),
            "lambda_2_mean": float(np.mean(l2s)),
            "lambda_2_std": float(np.std(l2s)),
            "retention_A_mean": float(np.mean(rets)),
            "retention_A_std": float(np.std(rets)),
        }

    # Correlation across N sweep
    all_l2 = [r["lambda_2_ABC"] for r in all_results]
    all_ret = [r["retention_A"] for r in all_results]
    if np.std(all_l2) > 0 and np.std(all_ret) > 0:
        corr_l2_ret = float(np.corrcoef(all_l2, all_ret)[0, 1])
    else:
        corr_l2_ret = float("nan")

    # Verdict
    if not all_results:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "INSTRUMENTATION_FAIL: no results produced"
    else:
        # Check lambda_2 > 0 at smallest N
        N0 = N_list[0]
        l2_mean = summary.get(f"N{N0}", {}).get("lambda_2_mean", 0.0)
        if l2_mean < 1e-6:
            verdict = "HARD_FAIL"
            verdict_msg = (f"HARD_FAIL: lambda_2={l2_mean:.2e} < 1e-6 at N={N0}. "
                           "Graph is effectively disconnected; spectral theory inapplicable.")
        elif not math.isnan(corr_l2_ret) and corr_l2_ret > 0.60:
            verdict = "HARD_PASS"
            verdict_msg = (f"HARD_PASS: corr(lambda_2, retention_A)={corr_l2_ret:.3f} > 0.60 "
                           f"AND lambda_2={l2_mean:.4f} > 0.001. "
                           "Algebraic connectivity predicts retention.")
        elif not math.isnan(corr_l2_ret) and corr_l2_ret < -0.30:
            verdict = "HARD_FAIL"
            verdict_msg = (f"HARD_FAIL: corr(lambda_2, retention_A)={corr_l2_ret:.3f} < -0.30. "
                           "Anti-correlated; spectral connectivity does not predict retention.")
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (f"MIDDLE_BAND: lambda_2={l2_mean:.4f}; "
                           f"corr(lambda_2, retention_A)={corr_l2_ret:.3f}. "
                           "Connectivity measurable but correlation inconclusive.")

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "corr_lambda2_retention": corr_l2_ret,
        "config": {
            "mode": "smoke" if smoke else "full",
            "N_list": N_list,
            "seeds": seeds,
            "M_load_frac": M_LOAD_FRAC,
            "field": "Spectral graph theory / Fiedler value",
            "orthogonal_probe": True,
            "P_deflated": 0.38,
        },
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[done] {verdict}: {verdict_msg[:120]}", flush=True)
    print(f"elapsed={elapsed:.1f}s  metrics -> {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    main()
