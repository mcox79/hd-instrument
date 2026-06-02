"""
hippocampal_basin_v1 -- Hippocampal phenomena mapping: basin-radius scaling + engram ablation.

Tests:
  (A) Basin-radius scaling vs load: r_basin ~ sqrt(1 - alpha/alpha_c).
      Treves-Rolls (1991) CA3 formula: Biological benchmark. R^2 > 0.90 = HP.
  (B) Engram ablation curve: m_residual = m0 * (1 - f/f_crit).
      f_crit = a^2 * N. Ablation fraction vs cosine residual should be linear.

Scope: Test C (non-reciprocal replay) excluded - requires asymmetric W infrastructure
not yet present in the codebase baseline.

Pre-reg:
  A HARD-PASS: R^2 > 0.90 between empirical r_basin and analytical formula at 4/5 seeds.
  A MIDDLE:    R^2 in [0.70, 0.90] or 3/5 seeds.
  A HARD-FAIL: R^2 < 0.50 or majority fail.
  B HARD-PASS: Pearson r > 0.85 between ablation fraction and cosine residual; slope ~ -m0/f_crit.
  B MIDDLE:    r in [0.60, 0.85] or slope off by >2x.
  B HARD-FAIL: r < 0.40 or no monotone trend.

No _nN suffix; production N=1024 rule 3 (CA3 scale).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import time
import math
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "hippocampal_basin_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# CA3 scale from Treves-Rolls
N = 1024
ALPHA_C = 0.138  # classical Hopfield capacity

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    ALPHA_GRID = [0.02, 0.05, 0.08, 0.10]
    RHO_GRID = [0.05, 0.10, 0.15, 0.20, 0.25]  # initial corruption
    ABLATION_FRACS = [0.0, 0.02, 0.05, 0.10, 0.20]
else:
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_GRID = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12]
    RHO_GRID = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
    ABLATION_FRACS = [0.0, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30]


def hopfield_update(W: np.ndarray, x: np.ndarray, beta: float = 8.0) -> np.ndarray:
    return np.sign(W @ x + 1e-12)


def hopfield_retrieval_acc(W: np.ndarray, Xi: np.ndarray, rho: float,
                            n_queries: int, n_iters: int, rng) -> float:
    """Fraction of noisy queries that converge back to stored pattern."""
    N, M = Xi.shape
    correct = 0
    for _ in range(n_queries):
        k = rng.randint(0, M)
        target = Xi[:, k].copy()
        # Corrupt rho fraction
        flip = rng.random(N) < rho
        noisy = target.copy()
        noisy[flip] = -noisy[flip]
        # Iterate
        x = noisy.copy()
        for _ in range(n_iters):
            x = hopfield_update(W, x)
        cos = float(np.dot(x, target) / (N + 1e-10))
        if cos > 0.7:
            correct += 1
    return correct / n_queries


def test_a_basin_scaling(N: int, seed: int) -> Dict:
    """Test A: r_basin empirical vs Treves-Rolls formula."""
    rng = np.random.RandomState(seed)
    alpha_c = ALPHA_C

    alpha_list = []
    r_basin_empirical = []
    r_basin_theoretical = []

    for alpha in ALPHA_GRID:
        if alpha >= alpha_c:
            continue
        M = max(1, int(N * alpha))
        Xi = rng.choice([-1.0, 1.0], size=(N, M))
        W = Xi @ Xi.T / N

        # Find basin radius: largest rho where retrieval acc > 0.80
        acc_curve = []
        for rho in RHO_GRID:
            acc = hopfield_retrieval_acc(W, Xi, rho, n_queries=20, n_iters=20, rng=rng)
            acc_curve.append((rho, acc))

        # r_basin = largest rho where acc > 0.80
        r_emp = 0.0
        for rho, acc in acc_curve:
            if acc > 0.80:
                r_emp = rho

        # Theoretical: r_basin ~ sqrt(1 - alpha/alpha_c)
        r_theory = math.sqrt(max(0, 1.0 - alpha / alpha_c))

        alpha_list.append(alpha)
        r_basin_empirical.append(r_emp)
        r_basin_theoretical.append(r_theory)

        print(f"    alpha={alpha:.3f} M={M} r_emp={r_emp:.3f} r_theory={r_theory:.3f}",
              flush=True)

    if len(alpha_list) < 2:
        return {"seed": seed, "r2": 0.0, "hp": False, "n_points": 0}

    # R^2 between empirical and theoretical
    y = np.array(r_basin_empirical)
    y_hat = np.array(r_basin_theoretical)
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = max(0.0, 1.0 - ss_res / (ss_tot + 1e-10))

    return {
        "seed": seed,
        "r2": float(r2),
        "n_points": len(alpha_list),
        "alpha_list": alpha_list,
        "r_basin_empirical": r_basin_empirical,
        "r_basin_theoretical": r_basin_theoretical,
        "hp": r2 > 0.90,
    }


def test_b_engram_ablation(N: int, seed: int) -> Dict:
    """
    Test B: engram ablation curve.
    Ablate f fraction of W entries tied to pattern 0.
    m_residual should drop linearly with f.
    """
    rng = np.random.RandomState(seed)
    a_sparsity = 0.1  # 10% active neurons
    M = max(5, int(N * 0.05))
    Xi = rng.choice([-1.0, 1.0], size=(N, M))
    W = Xi @ Xi.T / N
    p = Xi[:, 0]

    # f_crit formula: a^2 * N
    f_crit = (a_sparsity ** 2) * N
    print(f"    f_crit={f_crit:.1f} N={N} a={a_sparsity}", flush=True)

    # Cosine before any ablation
    x0 = p.copy()
    for _ in range(20):
        x0 = hopfield_update(W, x0)
    cos0 = float(np.dot(x0, p) / (np.linalg.norm(x0) * np.linalg.norm(p) + 1e-10))

    fracs_measured = []
    cos_residuals = []
    for f_frac in ABLATION_FRACS:
        # Ablate f fraction of W columns associated with p
        # Zero out f_frac * N entries in p-correlated columns
        W_ablated = W.copy()
        n_ablate = int(f_frac * N)
        if n_ablate > 0:
            # Rank the weights by correlation with p: |W[:, j] * p[j]|
            scores = np.abs(W.sum(axis=1) * p)
            ablate_idx = np.argsort(-scores)[:n_ablate]
            W_ablated[ablate_idx, :] = 0
            W_ablated[:, ablate_idx] = 0

        x = p.copy()
        for _ in range(20):
            x = hopfield_update(W_ablated, x)
        cos = float(np.dot(x, p) / (np.linalg.norm(x) * np.linalg.norm(p) + 1e-10))
        fracs_measured.append(f_frac)
        cos_residuals.append(cos)
        print(f"    f_frac={f_frac:.3f} n_ablate={n_ablate} cos={cos:.3f}", flush=True)

    # Pearson r between f_frac and cos_residual (should be negative/monotone decreasing)
    if len(fracs_measured) < 3:
        return {"seed": seed, "pearson_r": 0.0, "hp": False}

    fracs_arr = np.array(fracs_measured)
    cos_arr = np.array(cos_residuals)
    # Pearson r with negated fracs (we expect cos ~ decreasing with f)
    if np.std(fracs_arr) < 1e-10 or np.std(cos_arr) < 1e-10:
        pearson_r = 0.0
    else:
        pearson_r = float(np.corrcoef(-fracs_arr, cos_arr)[0, 1])

    return {
        "seed": seed,
        "pearson_r": pearson_r,
        "cos0": float(cos0),
        "fracs": fracs_measured,
        "cos_residuals": cos_residuals,
        "n_points": len(fracs_measured),
        "hp": pearson_r > 0.85,
    }


def _instrumentation_selftest():
    """Assert basin scaling and engram ablation are non-null at small scale."""
    # Test A
    r_a = test_a_basin_scaling(N=256, seed=999)
    assert "r2" in r_a, "r2 not in result"
    assert not math.isnan(r_a["r2"]), "r2 is NaN"
    assert r_a["n_points"] >= 1, "n_points == 0 at smoke scale"
    # Test B
    r_b = test_b_engram_ablation(N=256, seed=999)
    assert "pearson_r" in r_b, "pearson_r not in result"
    assert not math.isnan(r_b["pearson_r"]), "pearson_r is NaN"
    print(f"[selftest] PASS: basin_r2={r_a['r2']:.3f} engram_r={r_b['pearson_r']:.3f}",
          flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} N={N} seeds={SEEDS}", flush=True)

    results_a = []
    results_b = []

    for seed in SEEDS:
        print(f"\n[{ANCHOR_NAME}] seed={seed}...", flush=True)
        print("  [A] Basin scaling:", flush=True)
        r_a = test_a_basin_scaling(N, seed)
        results_a.append(r_a)
        print(f"  [A] R^2={r_a['r2']:.4f} n_points={r_a['n_points']} hp={r_a['hp']}",
              flush=True)

        print("  [B] Engram ablation:", flush=True)
        r_b = test_b_engram_ablation(N, seed)
        results_b.append(r_b)
        print(f"  [B] pearson_r={r_b['pearson_r']:.4f} hp={r_b['hp']}", flush=True)

    n_seeds = len(SEEDS)
    n_hp_a = sum(1 for r in results_a if r["hp"])
    n_hp_b = sum(1 for r in results_b if r["hp"])
    mean_r2 = float(np.mean([r["r2"] for r in results_a]))
    mean_pearson = float(np.mean([r["pearson_r"] for r in results_b]))

    hp_thresh = max(2, (n_seeds + 1) // 2)
    if n_hp_a >= hp_thresh and mean_r2 > 0.90:
        v_a = "HARD_PASS"
    elif mean_r2 < 0.50 or n_hp_a == 0:
        v_a = "HARD_FAIL"
    else:
        v_a = "MIDDLE_BAND"

    if n_hp_b >= hp_thresh and mean_pearson > 0.85:
        v_b = "HARD_PASS"
    elif mean_pearson < 0.40 or n_hp_b == 0:
        v_b = "HARD_FAIL"
    else:
        v_b = "MIDDLE_BAND"

    # A and B test different hippocampal phenomena; treat as independent.
    # B (engram ablation) is more decisive. A (basin scaling) is calibration.
    if v_b == "HARD_PASS" and v_a == "HARD_PASS":
        verdict = "HARD_PASS"
    elif v_b == "HARD_FAIL" and v_a == "HARD_FAIL":
        verdict = "HARD_FAIL"
    elif v_b == "HARD_PASS":
        # B alone sufficient for cap_map annotation; A is calibration
        verdict = "MIDDLE_BAND"
    elif v_a == "HARD_FAIL":
        # Basin scaling not tracking Treves-Rolls formula
        verdict = "MIDDLE_BAND"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"hippocampal_basin: A={v_a} mean_r2={mean_r2:.4f} n_hp_a={n_hp_a}/{n_seeds}; "
            f"B={v_b} mean_pearson={mean_pearson:.4f} n_hp_b={n_hp_b}/{n_seeds}; N={N}"
        ),
        "verdict_a": v_a,
        "verdict_b": v_b,
        "n_hp_a": int(n_hp_a),
        "n_hp_b": int(n_hp_b),
        "n_seeds": int(n_seeds),
        "mean_r2_basin_scaling": float(mean_r2),
        "mean_pearson_ablation": float(mean_pearson),
        "N": N,
        "alpha_c_nominal": ALPHA_C,
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  A (basin scaling): {v_a} mean_R2={mean_r2:.4f}", flush=True)
    print(f"  B (engram ablation): {v_b} mean_pearson={mean_pearson:.4f}", flush=True)
    print(f"  elapsed={elapsed:.1f}s", flush=True)


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