"""
spectral_zstat_v2 -- Spectral Z-statistic sensitivity for AI introspection auditing.
REDESIGN from v1: vectorized W build (matrix-multiply, not sequential outer-product loop).
v1 timed out at 300s because outer-product loop is O(k*N^2) sequential. v2 uses
batched matrix multiply: W = patterns.T @ patterns / N in O(M*N) ops.

Two test cells:
  (A) Z-statistic sensitivity: controlled rho=1 duplicate injection.
      Generate M activation vectors: (M-k) independent BSC +-1 vectors + k
      near-duplicate vectors with pairwise correlation rho=1 (exact copies).
      Write all M into W = patterns.T @ patterns / N (vectorized).
      Compute Z = (lambda_max - MP_bulk_edge) / sigma^2, lambda_max via power iteration.
      Prediction: Z > 3 first occurs at k >= k_crit where k_crit = 3 * N^(1/3).
      HARD-PASS A: fraction_crossing_seeds >= 0.80 (>= 4/5 seeds have a crossing).
      HARD-FAIL A: fraction_crossing_seeds < 0.20 (Z never crosses).

  (B) Advance-warning window: partial correlation ramp.
      For rho_dup in {0.2, 0.5, 0.8, 0.95}, inject k near-duplicates at varying k.
      Measure empirical k_detect (first Z > 3 crossing).
      Theoretical: k_detect(rho) = k_crit / rho = 3 * N^(1/3) / rho.
      HARD-PASS B: Spearman rho between empirical and theoretical k_detect across
                   4 rho_dup values >= 0.70.
      HARD-FAIL B: Spearman rho < 0.20 (no monotone relationship).

Marchenko-Pastur bulk edge: lambda_max_MP = sigma^2 * (1 + sqrt(M/N))^2
Z-scale: (lambda_max - lambda_max_MP) / sigma^2

Formula self-tests:
  k_crit(N=4096) = 3 * 4096^(1/3) = 3 * 16 = 48.
  MP edge at M=500, N=4096: (1 + sqrt(500/4096))^2 = (1+0.3493)^2 ~ 1.82.

No _nN suffix; production N=4096 per rule 3.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "spectral_zstat_v2"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M = 200
    K_SWEEP = [0, 3, 6, 10, 15, 20, 30, 40, 50, 60]
    RHO_DUP_LIST = [0.5, 0.95]
else:
    SEEDS = [7, 17, 23, 31, 41]
    M = 500
    K_SWEEP = list(range(0, 130, 5)) + [130, 150, 200]
    RHO_DUP_LIST = [0.2, 0.5, 0.8, 0.95]

# Pre-reg thresholds
K_CRIT = 3.0 * (N ** (1.0 / 3.0))   # ~48 at N=4096
HP_A_FRACTION_SEEDS_CROSSING = 0.80   # 4/5 seeds must cross Z=3 within K_SWEEP
HP_B_SPEARMAN = 0.70
HF_A_FRACTION = 0.20   # HARD-FAIL if fewer than 1/5 seeds ever cross
HF_B_SPEARMAN = 0.20

# Formula self-test assertions (run at import time)
assert abs(K_CRIT - 48.0) < 0.5, f"k_crit formula: expected ~48, got {K_CRIT:.2f}"


def mp_bulk_edge(M: int, N: int, sigma2: float = 1.0) -> float:
    """Marchenko-Pastur bulk edge: sigma^2 * (1 + sqrt(M/N))^2."""
    return sigma2 * (1.0 + math.sqrt(M / N)) ** 2


def power_iter_lmax(W: np.ndarray, n_iter: int = 60) -> float:
    """Estimate largest eigenvalue of symmetric W via power iteration."""
    rng = np.random.RandomState(123)
    v = rng.randn(W.shape[0])
    v /= np.linalg.norm(v)
    lam = 0.0
    for _ in range(n_iter):
        v_new = W @ v
        lam = float(np.dot(v, v_new))
        norm = float(np.linalg.norm(v_new))
        if norm < 1e-12:
            break
        v = v_new / norm
    return lam


def build_w_vectorized(M: int, N: int, k: int, rho_dup: float, seed: int) -> np.ndarray:
    """
    Build W = patterns.T @ patterns / N using batched matrix multiply.
    M-k independent BSC +-1, k near-duplicates with pairwise rho=rho_dup.
    Vectorized: no per-pattern outer product loop.
    """
    rng = np.random.RandomState(seed)
    n_indep = M - k

    if n_indep > 0:
        indep = rng.choice([-1.0, 1.0], size=(n_indep, N))
        W = indep.T @ indep / N
    else:
        W = np.zeros((N, N))

    if k > 0:
        base = rng.choice([-1.0, 1.0], size=(N,))
        if rho_dup >= 0.99:
            # exact copies
            dups = np.tile(base, (k, 1))
        else:
            flip_prob = (1.0 - rho_dup) / 2.0
            masks = rng.rand(k, N) < flip_prob
            dups = np.tile(base, (k, 1))
            dups[masks] *= -1.0
        W += dups.T @ dups / N

    return W


def compute_zstat(W: np.ndarray, M: int, N: int, sigma2: float = 1.0) -> float:
    """Z = (lambda_max - MP_edge) / sigma^2."""
    lam = power_iter_lmax(W)
    edge = mp_bulk_edge(M, N, sigma2)
    return (lam - edge) / sigma2


def find_first_z_crossing(M: int, N: int, k_sweep: List[int], rho_dup: float,
                           seed: int, z_thresh: float = 3.0) -> Optional[int]:
    """Find first k in k_sweep where Z > z_thresh."""
    for k in k_sweep:
        if k >= M:
            break
        W = build_w_vectorized(M, N, k, rho_dup, seed)
        z = compute_zstat(W, M, N)
        if z > z_thresh:
            return k
    return None


def run_cell_a(M: int, N: int, k_sweep: List[int], seed: int) -> Dict:
    """Cell A: Z-stat sensitivity with exact duplicates (rho=1)."""
    z_values = []
    for k in k_sweep:
        if k >= M:
            break
        W = build_w_vectorized(M, N, k, 1.0, seed)
        z = compute_zstat(W, M, N)
        z_values.append((k, z))
        print(f"  [cell_a] seed={seed} k={k} Z={z:.3f}", flush=True)

    first_cross = next((k for k, z in z_values if z > 3.0), None)
    return {
        "k_sweep": [k for k, _ in z_values],
        "z_values": [z for _, z in z_values],
        "first_k_z3": first_cross,
        "k_crit_theoretical": K_CRIT,
    }


def run_cell_b(M: int, N: int, k_sweep: List[int], rho_dup_list: List[float], seed: int) -> Dict:
    """Cell B: advance-warning window across rho values."""
    empirical_k_detect = []
    theoretical_k_detect = []
    for rho_dup in rho_dup_list:
        k_det = find_first_z_crossing(M, N, k_sweep, rho_dup, seed)
        k_theory = K_CRIT / rho_dup
        empirical_k_detect.append(k_det)
        theoretical_k_detect.append(k_theory)
        print(f"  [cell_b] seed={seed} rho={rho_dup:.2f} k_detect={k_det} k_theory={k_theory:.1f}", flush=True)

    valid_pairs = [(e, t) for e, t in zip(empirical_k_detect, theoretical_k_detect) if e is not None]
    if len(valid_pairs) >= 2:
        from scipy.stats import spearmanr
        emp_arr = np.array([p[0] for p in valid_pairs], dtype=float)
        th_arr = np.array([p[1] for p in valid_pairs], dtype=float)
        spear_rho, _ = spearmanr(emp_arr, th_arr)
    else:
        spear_rho = float("nan")

    return {
        "rho_dup_list": rho_dup_list,
        "empirical_k_detect": empirical_k_detect,
        "theoretical_k_detect": theoretical_k_detect,
        "spearman_rho": float(spear_rho) if not math.isnan(spear_rho) else None,
    }


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null at small scale."""
    N_test = 512
    M_test = 80
    k_sweep_test = [0, 3, 6, 10, 15, 20, 30, 40]
    seed = 42

    # Cell A: Z-values should vary, not all zero
    res_a = run_cell_a(M_test, N_test, k_sweep_test, seed)
    assert len(res_a["z_values"]) > 0, "no Z values computed"
    assert not all(z == 0.0 for z in res_a["z_values"]), "all Z values are exactly 0"
    # At least some k should give Z > 0 (even at small scale, duplicates should lift lambda_max)
    max_z = max(res_a["z_values"])
    assert max_z > 0.0, f"max Z is {max_z}, duplicates not lifting lambda_max"

    # Cell B with 2 rho values - check non-null
    res_b = run_cell_b(M_test, N_test, k_sweep_test, [0.5, 0.95], seed)
    assert "empirical_k_detect" in res_b, "empirical_k_detect missing"
    assert len(res_b["empirical_k_detect"]) == 2, "wrong n_rho"

    # Vectorized build check: W should be symmetric, N x N
    W = build_w_vectorized(M_test, N_test, 10, 0.8, seed)
    assert W.shape == (N_test, N_test), f"wrong W shape {W.shape}"
    assert np.allclose(W, W.T, atol=1e-10), "W not symmetric"

    print("[selftest] PASS: spectral_zstat_v2 metrics non-null at N=512 M=80", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Inline formula self-tests for pre-registered formulas."""
    # k_crit at N=4096 = 3 * 16 = 48
    assert abs(K_CRIT - 48.0) < 1.0, f"k_crit formula error: {K_CRIT}"
    # MP edge at M=500, N=4096
    edge = mp_bulk_edge(500, 4096, 1.0)
    assert 1.7 < edge < 2.0, f"MP edge formula error: {edge}"
    print("[formula_selftests] PASS: k_crit, MP_edge formulas verified", flush=True)


_verdict_formula_selftests()


def run_seed(seed: int) -> Dict:
    cell_a = run_cell_a(M, N, K_SWEEP, seed)
    cell_b = run_cell_b(M, N, K_SWEEP, RHO_DUP_LIST, seed)
    return {"cell_a": cell_a, "cell_b": cell_b, "seed": seed, "N": N, "M": M, "run_mode": RUN_MODE}


def aggregate_results(per_seed: Dict) -> Dict:
    k3_list = [v["cell_a"].get("first_k_z3") for v in per_seed.values()]
    crossing_seeds = sum(1 for k in k3_list if k is not None)
    never_cross = sum(1 for k in k3_list if k is None)
    valid_k3 = [k for k in k3_list if k is not None]
    median_k3 = float(np.median(valid_k3)) if valid_k3 else float("nan")

    spear_list = [v["cell_b"].get("spearman_rho") for v in per_seed.values()
                  if v["cell_b"].get("spearman_rho") is not None]
    mean_spear = float(np.mean(spear_list)) if spear_list else float("nan")

    return {
        "cell_a_crossing_seeds": crossing_seeds,
        "cell_a_never_cross_seeds": never_cross,
        "cell_a_median_k3": median_k3,
        "cell_a_k3_list": k3_list,
        "cell_b_mean_spearman": mean_spear,
        "k_crit_theoretical": K_CRIT,
        "n_seeds": len(per_seed),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    n = summary.get("n_seeds", 1)
    crossing_seeds = summary.get("cell_a_crossing_seeds", 0)
    never_cross = summary.get("cell_a_never_cross_seeds", 0)
    median_k3 = summary.get("cell_a_median_k3", float("nan"))
    spear = summary.get("cell_b_mean_spearman", float("nan"))

    fraction_cross = crossing_seeds / n if n > 0 else 0.0
    a_pass = fraction_cross >= HP_A_FRACTION_SEEDS_CROSSING
    a_fail = fraction_cross < HF_A_FRACTION

    b_spear_valid = not math.isnan(spear)
    b_pass = b_spear_valid and spear >= HP_B_SPEARMAN
    b_fail = b_spear_valid and spear < HF_B_SPEARMAN

    if a_pass and b_pass:
        return ("HARD_PASS",
                f"Z-stat sensitivity confirmed. "
                f"crossing_seeds={crossing_seeds}/{n} ({fraction_cross:.0%}), "
                f"median_k3={median_k3:.0f} (theory={K_CRIT:.1f}). "
                f"Spearman={spear:.3f}>={HP_B_SPEARMAN}.")
    if a_fail or b_fail:
        return ("HARD_FAIL",
                f"Z-stat sensitivity not confirmed. "
                f"crossing={crossing_seeds}/{n} ({fraction_cross:.0%}) "
                f"never_cross={never_cross}/{n} spearman={spear:.3f if b_spear_valid else float('nan')!s}.")
    return ("MIDDLE_BAND",
            f"Partial sensitivity. crossing={crossing_seeds}/{n} spearman={spear:.3f if b_spear_valid else float('nan')!s}. "
            f"k_crit_theory={K_CRIT:.1f} median_k3={median_k3:.0f}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} M={M} seeds={SEEDS} "
          f"k_sweep_len={len(K_SWEEP)} k_crit={K_CRIT:.1f}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} seeds done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        a_cross = result["cell_a"].get("first_k_z3")
        b_spear = result["cell_b"].get("spearman_rho")
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s | "
              f"first_k_Z3={a_cross} b_spearman={b_spear}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    summary = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(summary)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE,
        "N": N, "M": M,
        "seeds": SEEDS,
        "k_crit_theoretical": K_CRIT,
        "summary": summary,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"K_SWEEP": K_SWEEP, "RHO_DUP_LIST": RHO_DUP_LIST},
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete (selftests ran at module scope)", flush=True)
        sys.exit(0)
    main()
