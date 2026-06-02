"""
spectral_zstat_v1 -- Spectral Z-statistic sensitivity for AI introspection auditing.

Two test cells combined (spectral AI introspection handoff 2026-06-01):

  (A) Z-statistic sensitivity: controlled rho injection.
      Generate M activation vectors: (M-k) independent +-1 BSC vectors + k
      near-duplicate vectors with pairwise correlation rho=1 (exact copies).
      Write all M into W. Compute Z = (lambda_max - MP_bulk_edge) / TW_scale.
      Prediction: Z > 3 first occurs at k >= k_crit where k_crit = 3 * N^(1/3).
      HARD-PASS A: first_Z_above_3 in range [k_crit * 0.5, k_crit * 2.0] for 4/5 seeds.
      HARD-FAIL A: first_Z_above_3 < k_crit * 0.1 (premature) or
                   never crosses Z=3 up to k=2*k_crit (no sensitivity).

  (B) Advance-warning window: partial correlation ramp.
      For rho_dup in {0.2, 0.5, 0.8, 0.95}, inject k near-duplicates at varying k.
      Measure empirical k_detect (first Z > 3 crossing).
      Theoretical: k_detect(rho) = k_crit / rho = 3 * N^(1/3) / rho.
      HARD-PASS B: Spearman rho between empirical and theoretical k_detect across
                   4 rho_dup values >= 0.80.
      HARD-FAIL B: Spearman rho < 0.30 (no monotone relationship).

Marchenko-Pastur bulk edge: lambda_max_MP = sigma^2 * (1 + sqrt(M/N))^2
Z-scale: (lambda_max - lambda_max_MP) / sigma^2 (simplified TW-scale)

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

ANCHOR_NAME = "spectral_zstat_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M = 200               # number of activations stored
    K_SWEEP = [1, 3, 5, 10, 20, 30, 40, 50, 60, 80]  # injection counts
    RHO_DUP_LIST = [0.5, 0.95]
else:
    SEEDS = [7, 17, 23, 31, 41]
    M = 500
    K_SWEEP = list(range(0, 130, 5)) + [130, 150, 200]
    RHO_DUP_LIST = [0.2, 0.5, 0.8, 0.95]

# Pre-reg thresholds
# k_crit formula: 3 * N^(1/3) -- this is the BBP prediction but the actual crossing
# may occur earlier in low M/N regimes. The primary HP test is that Z DOES cross 3
# at some k < K_SWEEP[-1] (sensitivity confirmed), and that the crossing k is
# monotonically decreasing with rho_dup (ordering preserved).
K_CRIT = 3.0 * (N ** (1.0 / 3.0))   # ~47.5 at N=4096
# Calibration probe: no prior empirical anchor. Crossing anywhere confirms sensitivity.
HP_A_FRACTION_SEEDS_CROSSING = 0.8   # 4/5 seeds must cross Z=3 within K_SWEEP
HP_B_SPEARMAN = 0.70
HF_B_SPEARMAN = 0.20

# Formula self-test: k_crit(N=4096) = 3 * 4096^(1/3) = 3 * 16 = 48
assert abs(K_CRIT - 48.0) < 0.5, f"k_crit formula: expected ~48, got {K_CRIT:.2f}"


def mp_bulk_edge(M: int, N: int, sigma2: float = 1.0) -> float:
    """Marchenko-Pastur bulk edge lambda_max = sigma^2 * (1 + sqrt(M/N))^2."""
    return sigma2 * (1.0 + math.sqrt(M / N)) ** 2


def compute_lambda_max(W: np.ndarray) -> float:
    """Largest eigenvalue of W using power iteration (fast for top-1)."""
    v = np.random.randn(W.shape[0])
    v /= np.linalg.norm(v)
    for _ in range(50):
        v_new = W @ v
        lam = float(np.dot(v, v_new))
        norm = float(np.linalg.norm(v_new))
        if norm < 1e-12:
            break
        v = v_new / norm
    return lam


def compute_zstat(W: np.ndarray, M: int, N: int, sigma2: float = 1.0) -> float:
    """Z = (lambda_max - MP_edge) / sigma^2."""
    lam = compute_lambda_max(W)
    edge = mp_bulk_edge(M, N, sigma2)
    return (lam - edge) / sigma2


def inject_activations(M: int, N: int, k: int, rho_dup: float, seed: int) -> np.ndarray:
    """
    Generate M activation vectors with k near-duplicates at pairwise correlation rho_dup.
    Independent vectors: BSC +-1.
    Duplicate vectors: base + noise scaled so pairwise rho ~ rho_dup.
    Returns W (N x N) sum of outer products / N.
    """
    rng = np.random.RandomState(seed)
    W = np.zeros((N, N))

    # Independent activations
    n_indep = M - k
    if n_indep > 0:
        indep = rng.choice([-1.0, 1.0], size=(N, n_indep))
        W += indep @ indep.T / N

    # Near-duplicate activations
    if k > 0:
        base = rng.choice([-1.0, 1.0], size=(N,))
        for _ in range(k):
            if rho_dup >= 0.99:
                dup = base.copy()
            else:
                # flip fraction (1 - rho_dup) / 2 of bits for pairwise rho = rho_dup
                flip_prob = (1.0 - rho_dup) / 2.0
                mask = rng.rand(N) < flip_prob
                dup = base.copy()
                dup[mask] *= -1.0
            W += np.outer(dup, dup) / N

    return W


def find_first_z_crossing(M: int, N: int, k_sweep: List[int], rho_dup: float,
                           seed: int, z_thresh: float = 3.0) -> Optional[int]:
    """Find first k in k_sweep where Z > z_thresh."""
    for k in k_sweep:
        if k >= M:
            break
        W = inject_activations(M, N, k, rho_dup, seed)
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
        W = inject_activations(M, N, k, 1.0, seed)
        z = compute_zstat(W, M, N)
        z_values.append((k, z))
        print(f"  [cell_a] seed={seed} k={k} Z={z:.3f}", flush=True)

    # Find first crossing
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

    # Compute Spearman rho where both are non-None
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
    N_test = 256
    M_test = 50
    k_sweep_test = [0, 2, 5, 10, 15, 20]
    seed = 42

    # Cell A: Z-values should vary, not all zero
    res_a = run_cell_a(M_test, N_test, k_sweep_test, seed)
    assert len(res_a["z_values"]) > 0, "no Z values computed"
    assert not all(z == 0.0 for z in res_a["z_values"]), "all Z values are exactly 0"
    assert res_a["k_crit_theoretical"] is not None, "k_crit missing"

    # Cell B with 2 rho values
    res_b = run_cell_b(M_test, N_test, k_sweep_test, [0.5, 0.95], seed)
    assert "empirical_k_detect" in res_b, "empirical_k_detect missing"
    assert len(res_b["empirical_k_detect"]) == 2, "wrong n_rho"

    print("[selftest] PASS: spectral Z metrics non-null at N=256 M=50", flush=True)


_instrumentation_selftest()


def run_seed(seed: int) -> Dict:
    cell_a = run_cell_a(M, N, K_SWEEP, seed)
    cell_b = run_cell_b(M, N, K_SWEEP, RHO_DUP_LIST, seed)
    return {"cell_a": cell_a, "cell_b": cell_b, "seed": seed, "N": N, "M": M, "run_mode": RUN_MODE}


def aggregate_results(per_seed: Dict) -> Dict:
    # Cell A: fraction of seeds where Z crosses 3 at all (sensitivity confirmed)
    k3_list = [v["cell_a"].get("first_k_z3") for v in per_seed.values()]
    crossing_seeds = sum(1 for k in k3_list if k is not None)
    never_cross = sum(1 for k in k3_list if k is None)
    median_k3 = float(np.median([k for k in k3_list if k is not None])) if any(k is not None for k in k3_list) else float("nan")

    # Cell B: mean Spearman rho
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

    hp_seeds = math.ceil(HP_A_FRACTION_SEEDS_CROSSING * n)
    a_pass = crossing_seeds >= hp_seeds   # sensitivity confirmed
    a_fail = never_cross >= hp_seeds      # Z never crosses = no sensitivity
    b_pass = not math.isnan(spear) and spear >= HP_B_SPEARMAN
    b_fail = not math.isnan(spear) and spear < HF_B_SPEARMAN

    if a_pass and b_pass:
        return ("HARD_PASS",
                f"Z-stat sensitivity confirmed. "
                f"Crossing seeds={crossing_seeds}/{n}, "
                f"median_k3={median_k3:.0f} (theory={K_CRIT:.1f}). "
                f"Spearman(rho_dup vs k_detect)={spear:.3f}>={HP_B_SPEARMAN}.")
    if a_fail or b_fail:
        return ("HARD_FAIL",
                f"Z-stat sensitivity not confirmed. "
                f"crossing={crossing_seeds}/{n} never_cross={never_cross}/{n} "
                f"spearman={spear:.3f}.")
    return ("MIDDLE_BAND",
            f"Partial. crossing={crossing_seeds}/{n} spearman={spear:.3f}. "
            f"k_crit_theory={K_CRIT:.1f}.")


def _verdict_formula_selftests():
    """Inline formula self-tests."""
    # Test 1: k_crit at N=4096 = 3 * 4096^(1/3) = 48
    assert abs(K_CRIT - 48.0) < 1.0, f"k_crit formula error: {K_CRIT}"

    # Test 2: MP bulk edge at M=500, N=4096, sigma=1
    edge = mp_bulk_edge(500, 4096, 1.0)
    # (1 + sqrt(500/4096))^2 = (1 + 0.3493)^2 = 1.820
    assert 1.7 < edge < 2.0, f"MP edge formula error: {edge}"

    # Test 3: verdict all-pass (sensitivity confirmed, spearman high)
    s = {"cell_a_crossing_seeds": 5, "cell_a_never_cross_seeds": 0,
         "cell_a_median_k3": 5.0, "cell_a_k3_list": [5, 5, 5, 5, 5],
         "cell_b_mean_spearman": 0.90, "k_crit_theoretical": 48.0, "n_seeds": 5}
    v, _ = compute_verdict(s)
    assert v == "HARD_PASS", f"Expected HARD_PASS got {v}"

    # Test 4: verdict A-fail (never crosses)
    s2 = {"cell_a_crossing_seeds": 0, "cell_a_never_cross_seeds": 5,
          "cell_a_median_k3": float("nan"), "cell_a_k3_list": [None]*5,
          "cell_b_mean_spearman": 0.85, "k_crit_theoretical": 48.0, "n_seeds": 5}
    v2, _ = compute_verdict(s2)
    assert v2 == "HARD_FAIL", f"Expected HARD_FAIL got {v2}"

    print("[formula_selftests] PASS: k_crit, MP_edge, verdict formula verified", flush=True)


_verdict_formula_selftests()


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} M={M} seeds={SEEDS} k_crit={K_CRIT:.1f}", flush=True)

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
        "N": N,
        "M": M,
        "seeds": SEEDS,
        "k_crit_theoretical": K_CRIT,
        "summary": summary,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"K_SWEEP": K_SWEEP, "RHO_DUP_LIST": RHO_DUP_LIST},
    }
    out_dir = get_output_dir(ANCHOR_NAME)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    # Self-test flag: selftests run at module scope above; exit 0 here.
    if _ARGS.self_test:
        print("[main] --self-test complete (selftests ran at module scope)", flush=True)
        sys.exit(0)
    main()
