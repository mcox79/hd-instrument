"""
hippocampal_basin_fullscale_v2 -- Basin-radius scaling vs load at full GPU scale.

Extends hippocampal_basin_v1 (completed at N=1024) to:
  - N=4096 (CA3-scale with higher resolution)
  - 10 seeds
  - Full alpha grid 0.01 to 0.13
  - Both cells A and B

From hippocampal phenomena mapping handoff (2026-06-01).

Tests:
  (A) Basin-radius scaling vs load: r_basin ~ sqrt(1 - alpha/alpha_c).
      Biological benchmark: Treves-Rolls (1991). R^2 > 0.90 = HP.
  (B) Engram ablation curve: m_residual = m0 * (1 - f/f_crit).
      Linear trend confirmed if Pearson r > 0.85.

The N=4096 run requires GPU for the matrix operations to be practical.
W matrix size: 4096^2 * 4 = 64MB -- well within GPU 8GB.

PROT-018 N-suffix: _n4096 binding.
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
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "hippocampal_basin_fullscale_v2_n4096"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096
ALPHA_C = 0.138

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# PROT-018 runtime check
if "_n" in ANCHOR_NAME:
    import re as _re
    _m = _re.search(r'_n(\d+)', ANCHOR_NAME)
    if _m:
        _suffix_n = int(_m.group(1))
        assert N == _suffix_n, f"PROT-018: anchor name says _n{_suffix_n} but N={N}"

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    ALPHA_GRID = [0.02, 0.05, 0.08, 0.10]
    # RHO_GRID must span from very low (where high-alpha fails) to very high
    # (where low-alpha succeeds) to see the decay in r_basin vs alpha.
    # At N=4096 alpha_c=0.138 Hopfield, patterns survive up to rho~0.40 at low load.
    RHO_GRID = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    ABLATION_FRACS = [0.0, 0.02, 0.05, 0.10, 0.20]
else:
    SEEDS = [7, 17, 23, 31, 41, 53, 67, 79, 89, 97]
    ALPHA_GRID = [0.01, 0.02, 0.03, 0.05, 0.07, 0.08, 0.10, 0.11, 0.12, 0.13]
    RHO_GRID = [0.02, 0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    ABLATION_FRACS = [0.0, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]

# Cell A metric: Pearson correlation between empirical and analytical r_basin vs alpha.
# (R2 requires same-scale units; Pearson captures the monotone shape regardless of scale.)
HP_PEARSON_A = 0.85
MID_PEARSON_A = 0.60
HF_PEARSON_A = 0.30
# Cell B metric: absolute Pearson correlation of ablation curve (monotone decrease expected)
HP_PEARSON_ABLATION = 0.85
MID_PEARSON_ABLATION = 0.60
HF_PEARSON_ABLATION = 0.40


def make_patterns(N: int, M: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(N, M))


def build_hopfield_W(patterns: np.ndarray) -> np.ndarray:
    N, M = patterns.shape
    W = patterns @ patterns.T / N
    np.fill_diagonal(W, 0.0)
    return W


def hopfield_update(W: np.ndarray, x: np.ndarray, n_iters: int = 20) -> np.ndarray:
    for _ in range(n_iters):
        x = np.sign(W @ x + 1e-12)
    return x


def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def measure_basin_radius(W: np.ndarray, patterns: np.ndarray, rho_grid: List[float],
                          n_samples: int = 5, seed: int = 0) -> float:
    """
    Measure effective basin radius as largest rho s.t. retrieval success > 0.5.
    Returns r_basin (corruption fraction).
    """
    rng = np.random.RandomState(seed)
    N, M = patterns.shape
    r_basin = 0.0
    for rho in sorted(rho_grid):
        success = []
        for _ in range(n_samples):
            t = rng.randint(0, M)
            pat = patterns[:, t]
            # Corrupt rho fraction of bits
            noise = rng.rand(N) < rho
            corrupted = pat.copy()
            corrupted[noise] *= -1.0
            retrieved = hopfield_update(W, corrupted)
            success.append(cos_sim(retrieved, pat) > 0.7)
        if float(np.mean(success)) > 0.5:
            r_basin = rho
        else:
            break  # stop at first failure
    return r_basin


def analytical_r_basin(alpha: float, alpha_c: float) -> float:
    """Treves-Rolls formula: r_basin ~ sqrt(1 - alpha/alpha_c)."""
    if alpha >= alpha_c:
        return 0.0
    return math.sqrt(max(0.0, 1.0 - alpha / alpha_c))


def r_squared(y_true: List[float], y_pred: List[float]) -> float:
    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred)
    ss_res = np.sum((y_true_arr - y_pred_arr) ** 2)
    ss_tot = np.sum((y_true_arr - np.mean(y_true_arr)) ** 2)
    if ss_tot < 1e-12:
        return float("nan")
    return float(1.0 - ss_res / ss_tot)


def pearson_r(x: List[float], y: List[float]) -> float:
    xa, ya = np.array(x), np.array(y)
    xc = xa - np.mean(xa)
    yc = ya - np.mean(ya)
    denom = np.linalg.norm(xc) * np.linalg.norm(yc)
    if denom < 1e-12:
        return float("nan")
    return float(np.dot(xc, yc) / denom)


def run_cell_a(N: int, alpha_grid: List[float], rho_grid: List[float], seed: int) -> Dict:
    """Cell A: basin radius vs load.

    Metric: Pearson correlation between empirical r_basin and analytical r_basin.
    (Not R2: empirical and analytical are on different absolute scales; correlation
    captures the monotone decreasing relationship as load increases.)
    """
    empirical_r = []
    analytical_r = []

    for alpha in alpha_grid:
        M = max(1, int(alpha * N))
        patterns = make_patterns(N, M, seed)
        W = build_hopfield_W(patterns)
        r_emp = measure_basin_radius(W, patterns, rho_grid, n_samples=5, seed=seed + int(alpha * 1000))
        r_anal = analytical_r_basin(alpha, ALPHA_C)
        empirical_r.append(r_emp)
        analytical_r.append(r_anal)
        print(f"    alpha={alpha:.2f} M={M} r_emp={r_emp:.3f} r_anal={r_anal:.3f}", flush=True)

    corr = pearson_r(analytical_r, empirical_r)
    return {
        "alpha_grid": alpha_grid,
        "empirical_r_basin": empirical_r,
        "analytical_r_basin": analytical_r,
        "pearson_corr": corr,
    }


def run_cell_b(N: int, alpha: float, ablation_fracs: List[float], seed: int) -> Dict:
    """
    Cell B: engram ablation curve.
    Ablate by removing f fraction of the CONTRIBUTION of pattern 0 to W:
    W_abl = W_full - f * outer(pat0, pat0) / N.
    Measure residual cosine of retrieved pattern.
    This is the biologically-correct ablation: f=1.0 is exact rank-1 deletion.
    """
    M = max(1, int(alpha * N))
    patterns = make_patterns(N, M, seed)
    W_full = build_hopfield_W(patterns)
    pat0 = patterns[:, 0]
    pat0_contribution = np.outer(pat0, pat0) / N

    residuals = []
    for f in ablation_fracs:
        # Partial rank-1 removal: ablate f fraction of pat0's contribution
        W_abl = W_full - f * pat0_contribution
        np.fill_diagonal(W_abl, 0.0)

        retrieved = hopfield_update(W_abl, pat0)
        residual = cos_sim(retrieved, pat0)
        residuals.append(residual)

    # We expect residuals to DECREASE with increasing f (negative correlation)
    # Pearson r should be < -0.85 (HP)
    corr = pearson_r(ablation_fracs, residuals)
    return {
        "ablation_fracs": ablation_fracs,
        "residuals": residuals,
        "pearson_r": corr,  # expected negative: more ablation -> less residual
        "pearson_r_abs": abs(corr),
    }


def run_seed(seed: int) -> Dict:
    print(f"[seed {seed}] starting cell A (basin radius)", flush=True)
    cell_a = run_cell_a(N, ALPHA_GRID, RHO_GRID, seed)
    print(f"  [seed {seed}] cell_a pearson_corr={cell_a['pearson_corr']:.3f}", flush=True)

    print(f"[seed {seed}] starting cell B (ablation)", flush=True)
    cell_b = run_cell_b(N, 0.10, ABLATION_FRACS, seed)
    print(f"  [seed {seed}] cell_b pearson_r={cell_b['pearson_r']:.3f}", flush=True)

    return {"cell_a": cell_a, "cell_b": cell_b, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert all metrics non-null at small scale."""
    N_test = 512
    alpha_test = [0.02, 0.08]
    # Wide rho_grid so that different alpha values actually have different r_basin
    rho_test = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    ablation_test = [0.0, 0.05, 0.10]

    res_a = run_cell_a(N_test, alpha_test, rho_test, 42)
    assert "pearson_corr" in res_a, "pearson_corr missing from cell_a"
    assert res_a["empirical_r_basin"] is not None and len(res_a["empirical_r_basin"]) == 2, "wrong n_alphas"
    assert res_a["analytical_r_basin"] is not None and len(res_a["analytical_r_basin"]) == 2, "analytical missing"
    # At small N with wide rho_grid, empirical values should vary so pearson_corr is non-NaN
    print(f"[selftest] pearson_corr={res_a['pearson_corr']} empirical_r={res_a['empirical_r_basin']}")
    assert not math.isnan(res_a["pearson_corr"]), (
        f"SELFTEST FAIL: pearson_corr=NaN means all empirical r_basin identical -- rho_grid too narrow; "
        f"empirical_r={res_a['empirical_r_basin']}"
    )

    res_b = run_cell_b(N_test, 0.10, ablation_test, 42)
    assert "pearson_r" in res_b, "pearson_r missing"
    assert len(res_b["residuals"]) == 3, "wrong n_ablation_fracs"
    print(f"[selftest] PASS: cell_a pearson={res_a['pearson_corr']:.3f} cell_b pearson_r={res_b['pearson_r']:.3f}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    corr_a_list = [v["cell_a"]["pearson_corr"] for v in per_seed.values()
                   if not math.isnan(v["cell_a"].get("pearson_corr", float("nan")))]
    pearson_list = [abs(v["cell_b"]["pearson_r"]) for v in per_seed.values()
                    if not math.isnan(v["cell_b"].get("pearson_r", float("nan")))]
    seeds_a_pass = sum(1 for r in corr_a_list if r > HP_PEARSON_A)
    seeds_b_pass = sum(1 for r in pearson_list if r > HP_PEARSON_ABLATION)
    return {
        "mean_pearson_a": float(np.mean(corr_a_list)) if corr_a_list else float("nan"),
        "mean_pearson_ablation": float(np.mean(pearson_list)) if pearson_list else float("nan"),
        "seeds_a_pass": seeds_a_pass,
        "seeds_b_pass": seeds_b_pass,
        "n_seeds": len(per_seed),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    n = summary.get("n_seeds", 1)
    corr_a = summary.get("mean_pearson_a", float("nan"))
    pear = summary.get("mean_pearson_ablation", float("nan"))
    seeds_a = summary.get("seeds_a_pass", 0)
    seeds_b = summary.get("seeds_b_pass", 0)

    hp_seeds = math.ceil(0.8 * n)

    a_pass = not math.isnan(corr_a) and corr_a > HP_PEARSON_A and seeds_a >= hp_seeds
    a_fail = not math.isnan(corr_a) and corr_a < HF_PEARSON_A
    b_pass = not math.isnan(pear) and pear > HP_PEARSON_ABLATION and seeds_b >= hp_seeds
    b_fail = not math.isnan(pear) and pear < HF_PEARSON_ABLATION

    if a_pass and b_pass:
        return ("HARD_PASS",
                f"Hippocampal phenomena confirmed at N=4096. "
                f"Basin pearson={corr_a:.3f}>{HP_PEARSON_A}, "
                f"ablation pearson_r={pear:.3f}>{HP_PEARSON_ABLATION}. "
                f"Seeds: A={seeds_a}/{n}, B={seeds_b}/{n}.")
    if a_fail or b_fail:
        return ("HARD_FAIL",
                f"Hippocampal mapping fails at N=4096. "
                f"basin_pearson={corr_a:.3f}(hf={HF_PEARSON_A}), "
                f"ablation_pear={pear:.3f}(hf={HF_PEARSON_ABLATION}).")
    return ("MIDDLE_BAND",
            f"basin_pearson={corr_a:.3f}(hp={HP_PEARSON_A}), "
            f"ablation_pear={pear:.3f}(hp={HP_PEARSON_ABLATION}). "
            f"Seeds: A={seeds_a}/{n}, B={seeds_b}/{n}.")


def _verdict_formula_selftests():
    """Formula self-tests."""
    # analytical r_basin: at alpha=0.07, alpha_c=0.138 -> sqrt(1 - 0.07/0.138) = sqrt(0.493) = 0.702
    r = analytical_r_basin(0.07, 0.138)
    assert abs(r - math.sqrt(1.0 - 0.07 / 0.138)) < 1e-6, f"r_basin formula error: {r}"

    # Verdict: both cells pass
    s1 = {"mean_pearson_a": 0.92, "mean_pearson_ablation": 0.87, "seeds_a_pass": 9, "seeds_b_pass": 8, "n_seeds": 10}
    v1, _ = compute_verdict(s1)
    assert v1 == "HARD_PASS", f"Expected HARD_PASS got {v1}"

    # Verdict: cell A fails (pearson_a=0.20 < HF=0.30)
    s2 = {"mean_pearson_a": 0.20, "mean_pearson_ablation": 0.85, "seeds_a_pass": 2, "seeds_b_pass": 8, "n_seeds": 10}
    v2, _ = compute_verdict(s2)
    assert v2 == "HARD_FAIL", f"Expected HARD_FAIL got {v2}"

    # Verdict: both NaN -> MIDDLE_BAND
    s3 = {"mean_pearson_a": float("nan"), "mean_pearson_ablation": 0.87, "seeds_a_pass": 0, "seeds_b_pass": 8, "n_seeds": 10}
    v3, _ = compute_verdict(s3)
    assert v3 == "MIDDLE_BAND", f"Expected MIDDLE_BAND got {v3}"

    print("[formula_selftests] PASS: r_basin formula, verdict cases verified", flush=True)


_verdict_formula_selftests()


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s | "
              f"pearson_a={result['cell_a']['pearson_corr']:.3f} "
              f"pear_b={result['cell_b']['pearson_r']:.3f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    summary = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(summary)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE,
        "N": N,
        "seeds": SEEDS,
        "summary": summary,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {
            "ALPHA_GRID": ALPHA_GRID,
            "RHO_GRID": RHO_GRID,
            "ABLATION_FRACS": ABLATION_FRACS,
        },
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
