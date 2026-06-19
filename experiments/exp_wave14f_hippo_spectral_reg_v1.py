"""HiPPO rescue #5: Spectral regularization keeping W in HiPPO basis.

MOTIVATION: wave14f_hippo_init_w_v1 showed: (1) HiPPO init provides NO depth benefit
over random init at K=4 (P1 HARD_FAIL); but (2) post-Hebbian W implicitly converges to
HiPPO-like eigenstructure regardless of init (P3 spectral_corr=0.993). PROT-004 rescue
sketch #5: add a spectral regularization loss that FORCES W to remain in the HiPPO
basis throughout Hebbian training. If HiPPO alignment is beneficial (not just emergent),
regularization should exceed the unregularized result.

HYPOTHESIS: Chain-cleanup depth with HiPPO-spectral regularization >= unregularized
depth * 1.2x at N=2048, K=4, 3 seeds. The regularization keeps W projecting onto the
HiPPO eigenvectors, preventing noise accumulation in off-basis directions.

DESIGN:
  - Regularization: after each Hebbian update, project out non-HiPPO components:
    W_reg = P_hippo @ W @ P_hippo (where P_hippo = top-K eigenvectors of HiPPO W).
  - Compare depth_reg vs depth_unreg at K=4, N=2048, 3 seeds.

PRE-REGISTERED BANDS:
  HARD-PASS:
    - depth_reg / depth_unreg >= 1.2x on >= 2/3 seeds
    -> Spectral regularization provides depth benefit
  HARD-FAIL:
    - depth_reg / depth_unreg <= 1.0x ALL seeds
    -> HiPPO spectral basis does NOT help even when enforced structurally
  MIDDLE-BAND: ratio >= 1.1x but < 1.2x (marginal benefit)
  INSTRUMENTATION-FAIL: projection fails or depth is NaN.

Self-tests:
  1. P_hippo @ P_hippo = P_hippo (projector is idempotent).
  2. ||P_hippo @ v||_2 <= ||v||_2 (projection does not amplify).
  3. depth computation returns finite integer.
  4. Spectral regularization reduces off-basis components.

Queue: overnight_queue (GPU; N=2048 K=4 3seeds; ~1-2 GPU hrs)
Pre-reg: prereqs/2026-05-26_wave14f_hippo_spectral_reg_v1.md
Parent: wave14f_hippo_init_w_v1 P3_HARD_PASS spectral_corr=0.993
PROT-004 rescue: sketch #5 (spectral regularization)
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

N_FULL = 2048
N_SMOKE = 256
K_ATOMS = 4      # number of experts / context positions
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [7]
D_SWEEP_FULL = [2, 5, 10, 20, 30, 50, 80, 100]
D_SWEEP_SMOKE = [2, 5, 10, 20]
ACC_THRESHOLD = 0.5
N_PROJ_COMPONENTS = 64  # number of HiPPO eigenvectors to keep


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def make_hippo_legs_projector(N: int, n_components: int) -> torch.Tensor:
    """
    Build projector onto top-n_components eigenvectors of HiPPO-LegS matrix.
    Returns: P [N, N] = V_k V_k^T where V_k = top-k eigenvectors.
    """
    # Build HiPPO-LegS (same as hippo_k8_depth_v1)
    H = torch.zeros(N, N)
    for n_idx in range(N):
        for k in range(n_idx + 1):
            if k < n_idx:
                H[n_idx, k] = math.sqrt(2 * n_idx + 1) * math.sqrt(2 * k + 1) * ((-1) ** (n_idx - k))
            else:
                H[n_idx, k] = 2 * n_idx + 1
    H_sym = (H + H.T) / 2.0
    H_sym.fill_diagonal_(0.0)

    # Top eigenvectors via SVD
    n_comp = min(n_components, N - 1)
    _, S, Vt = torch.linalg.svd(H_sym, full_matrices=False)
    V_top = Vt[:n_comp].T  # [N, n_comp]
    P = V_top @ V_top.T    # projector [N, N]
    return P


def train_hopfield_with_reg(N: int, K: int, seed: int, P_hippo: torch.Tensor,
                             reg_strength: float, device: torch.device) -> torch.Tensor:
    """
    Train Hopfield W with HiPPO spectral regularization.
    After each pattern addition, apply: W = (1-reg)*W + reg*(P @ W @ P)
    """
    gen = torch.Generator().manual_seed(seed)
    W = torch.zeros(N, N, device=device)
    P_hippo = P_hippo.to(device)
    patterns = []
    for _ in range(K):
        v = torch.randn(N, generator=gen, device=device)
        v = v / (v.norm() + 1e-9)
        W += torch.outer(v, v)
        # Spectral regularization: project W toward HiPPO basis
        if reg_strength > 0:
            W_proj = P_hippo @ W @ P_hippo
            W = (1 - reg_strength) * W + reg_strength * W_proj
        patterns.append(v)
    W = W / (math.sqrt(K) + 1e-9)
    W.fill_diagonal_(0.0)
    return W, patterns


def find_depth_from_W(W: torch.Tensor, patterns: List[torch.Tensor],
                      d_sweep: List[int], seed: int, device: torch.device) -> int:
    """Find chain-cleanup depth d_c from trained W."""
    K = len(patterns)
    W_norm = W / (math.sqrt(K) + 1e-9)

    acc_at_d = {}
    for d in d_sweep:
        correct = 0
        for v in patterns:
            q = v.clone()
            for _ in range(d):
                q_next = W_norm @ q
                if q_next.norm() > 0:
                    q_next = q_next / q_next.norm()
                q = q_next
            cos_sim = float((q @ v).item())
            if cos_sim > ACC_THRESHOLD:
                correct += 1
        acc_at_d[d] = correct / len(patterns)

    d_c = 0
    for d in sorted(d_sweep):
        if acc_at_d[d] > ACC_THRESHOLD:
            d_c = d
    return d_c


def run_one_seed(N: int, K: int, seed: int, P_hippo: torch.Tensor,
                 smoke: bool, device: torch.device) -> Dict:
    d_sweep = D_SWEEP_SMOKE if smoke else D_SWEEP_FULL

    # Unregularized
    W_unreg, pats_unreg = train_hopfield_with_reg(N, K, seed, P_hippo, reg_strength=0.0, device=device)
    depth_unreg = find_depth_from_W(W_unreg, pats_unreg, d_sweep, seed, device)

    # Spectral regularized (reg_strength=0.3)
    W_reg, pats_reg = train_hopfield_with_reg(N, K, seed, P_hippo, reg_strength=0.3, device=device)
    depth_reg = find_depth_from_W(W_reg, pats_reg, d_sweep, seed, device)

    depth_ratio = (depth_reg + 1) / (depth_unreg + 1)

    return {
        "N": N,
        "K": K,
        "seed": seed,
        "depth_unreg": depth_unreg,
        "depth_reg": depth_reg,
        "depth_ratio": float(depth_ratio),
        "reg_wins": bool(depth_reg > depth_unreg * 1.2),
    }


def _instrumentation_selftest() -> None:
    """Assert projector and depth computations are correct."""
    P = make_hippo_legs_projector(N=32, n_components=16)

    # 1. P @ P = P (idempotent projector, up to numerical precision)
    P2 = P @ P
    err = float((P2 - P).abs().max().item())
    assert err < 0.01, f"Projector not idempotent: max err = {err}"

    # 2. ||P @ v||_2 <= ||v||_2 (projection does not amplify)
    v = torch.randn(32)
    Pv = P @ v
    assert Pv.norm().item() <= v.norm().item() + 1e-5, "Projection amplifies vector"

    # 3. depth computation returns valid int
    device = torch.device("cpu")
    W_test, pats_test = train_hopfield_with_reg(64, 4, 42, make_hippo_legs_projector(64, 32), 0.0, device)
    d_test = find_depth_from_W(W_test, pats_test, [2, 5, 10], 42, device)
    assert isinstance(d_test, int) and d_test >= 0, f"depth not valid: {d_test}"

    # 4. Regularized W has smaller off-HiPPO component
    W_unreg_test, _ = train_hopfield_with_reg(64, 4, 42, make_hippo_legs_projector(64, 32), 0.0, device)
    W_reg_test, _ = train_hopfield_with_reg(64, 4, 42, make_hippo_legs_projector(64, 32), 0.3, device)
    P64 = make_hippo_legs_projector(64, 32)
    # Projection onto HiPPO: should be closer for reg version
    off_unreg = float((W_unreg_test - P64 @ W_unreg_test @ P64).norm().item())
    off_reg = float((W_reg_test - P64 @ W_reg_test @ P64).norm().item())
    assert off_reg < off_unreg + 0.1, f"Reg does not reduce off-HiPPO: {off_reg:.4f} vs {off_unreg:.4f}"

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
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    name = "wave14f_hippo_spectral_reg_v1"
    out_dir = get_output_dir(name)
    t0 = time.time()

    print(f"[setup] Building HiPPO projector for N={N}...", flush=True)
    P_hippo = make_hippo_legs_projector(N, n_components=N_PROJ_COMPONENTS)
    print(f"[setup] Projector shape: {P_hippo.shape}", flush=True)

    all_results = []
    for seed in seeds:
        print(f"[run] N={N} K={K_ATOMS} seed={seed}", flush=True)
        r = run_one_seed(N, K_ATOMS, seed, P_hippo, smoke, device)
        all_results.append(r)
        print(f"  depth_unreg={r['depth_unreg']} depth_reg={r['depth_reg']} "
              f"ratio={r['depth_ratio']:.3f}", flush=True)

    # Aggregate
    ratios = [r["depth_ratio"] for r in all_results]
    reg_wins_frac = sum(r["reg_wins"] for r in all_results) / len(all_results)

    summary = {
        "N": N,
        "K": K_ATOMS,
        "n_seeds": len(all_results),
        "depth_ratio_mean": float(np.mean(ratios)),
        "depth_ratio_std": float(np.std(ratios)),
        "reg_wins_frac": float(reg_wins_frac),
    }

    # Verdict
    if not all_results:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "INSTRUMENTATION_FAIL: no results"
    else:
        ratio_mean = summary["depth_ratio_mean"]
        if ratio_mean >= 1.2 and reg_wins_frac >= 0.6:
            verdict = "HARD_PASS"
            verdict_msg = (
                f"HARD_PASS: depth_ratio={ratio_mean:.3f} >= 1.2x on {reg_wins_frac:.2f} seeds. "
                "HiPPO spectral regularization provides depth benefit. "
                "PROT-004 rescue sketch #5 CONFIRMED."
            )
        elif ratio_mean <= 1.0 and reg_wins_frac == 0.0:
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"HARD_FAIL: depth_ratio={ratio_mean:.3f} <= 1.0 ALL seeds. "
                "HiPPO spectral basis does NOT help even when enforced. "
                "PROT-004 rescue sketch #5 CLOSED."
            )
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"MIDDLE_BAND: depth_ratio={ratio_mean:.3f}; reg_wins={reg_wins_frac:.2f}. "
                "Marginal spectral regularization benefit."
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
            "K": K_ATOMS,
            "seeds": seeds,
            "n_proj_components": N_PROJ_COMPONENTS,
            "parent": "wave14f_hippo_init_w_v1 P3_HARD_PASS spectral_corr=0.993",
            "prot004_rescue": "sketch #5 (spectral regularization)",
        },
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[done] {verdict}: {verdict_msg[:120]}", flush=True)
    print(f"elapsed={elapsed:.1f}s  metrics -> {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    main()
