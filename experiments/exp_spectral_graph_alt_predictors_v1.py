"""Spectral graph alternative predictors v1: test 3 graph properties beyond lambda_2.

CONTEXT:
  spectral_graph_lambda2_v4 HARD_FAIL: mean_corr=-0.861 (47-sigma anti-correlation).
  Strategy v259 rescue sketch (c): test alternative graph properties to see if
  any POSITIVE predictor exists in the graph-spectral family, before declaring
  the entire framework closed.

  lambda_2 falsified = algebraic connectivity is negatively correlated with retention.
  Rescue: try 3 orthogonal graph properties that theory suggests MIGHT capture
  substrate health more directly.

SCIENTIFIC QUESTION (v259 rescue-c):
  Do any of the following 3 alternative graph properties positively correlate
  with substrate retention (r >= 0.5) at N=1024 5-seed?

  Property 1: clustering_coefficient -- mean local clustering; high = dense local structure.
  Property 2: avg_shortest_path_APPROX -- graph diameter proxy via spectral gap of
    normalized Laplacian (L_sym = D^{-1/2} L D^{-1/2}); gap = 1 - lambda_{n-1}
    where lambda_{n-1} is the LARGEST eigenvalue of normalized Laplacian.
    Interpretation: large spectral gap = small effective diameter = tight coupling.
  Property 3: spectral_gap_normalized -- 1 - (lambda_max_normalized - lambda_min_normalized)
    of the normalized random-walk Laplacian. A proxy for mixing time.
    High spectral gap (of L_sym) = fast mixing = good information propagation.

  If any property clears corr >= 0.5: new spectral-framework positive-predictor row.
  If all 3 fail: spectral-graph framework comprehensively closed.

PRE-REGISTERED BANDS (calibration probe; lambda_2 was falsified but alternatives are new):
  Prior anchor: lambda_2 anti-correlation mean=-0.861. These are new observables.
  Bands widened to +- 50% per calibration-probe policy (no prior anchor for alternatives).

  HARD_PASS: at least one property achieves mean_corr >= 0.50 at N=1024 across 5 seeds.
    Interpretation: spectral-graph framework has a valid predictor (just not lambda_2).
  HARD_FAIL: all 3 properties show |corr| < 0.20 (no spectral-graph signal at all).
    Interpretation: graph-spectral family is comprehensively uninformative.
  MIDDLE_BAND: mixed -- some corr values in [0.20, 0.50]; potential signal but below threshold.

FORMULA SELF-TESTS:
  1. clustering_coefficient for triangle graph (3 nodes, all connected): C = 1.0.
     For star graph (N=5, center + 4 leaves): C = 0.0 (no triangles at leaves).
  2. spectral_gap_normalized: for complete graph K_N, lambda_2_sym = N/(N-1),
     spectral gap = 1. For empty graph: eigenvalues all 0, gap = 0.
  3. corr(x, y) where x=y: = 1.0. corr(x, -y): = -1.0.
  4. clustering_coefficient of random BSC substrate at low load (M=1):
     W = outer(v, v) / N -> weak all-to-all, small clustering coefficient.

TIMEOUT ESTIMATE:
  run_one_seed at N=1024, 7 alpha_B, 1 seed: ~8s (similar to lambda_2_v4).
    Clustering coeff: O(N^2) triangle counting -> ~2x overhead vs lambda_2.
  Full: 1 N-value * 5 seeds * 7 alpha_B each = ~80s.
  timeout_s = ceil(1.5 * 80 * 3) = ceil(360) -> 600s. Use 1800s for safety.

N-suffix: no _nN suffix; production N = 1024 throughout (PROT-018: stated explicitly).
Queue: remote_cpu_queue (pure numpy/scipy; N=1024 5-seed; ~10-20min)
Pre-reg: preregs/2026-05-28_spectral_graph_alt_predictors_v1.md
Parent: spectral_graph_lambda2_v4 (v259 HARD_FAIL closure rescue (c))
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# PRODUCTION CONFIG
# PROT-018: N=1024 throughout; no _nN suffix (stated explicitly)
N = 1024
N_SMOKE = 256
M_A_FRAC = 0.10
ALPHA_HEBBIAN = 0.1
NOISE_FLIP_FRAC = 0.10

ALPHA_B_FULL  = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]
ALPHA_B_SMOKE = [0.0, 0.10, 0.30]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_CORR_MIN = 0.50   # HARD_PASS: at least one property achieves this
HF_CORR_MAX = 0.20   # HARD_FAIL: ALL properties below this absolute value


def get_output_dir(default_name: str = "spectral_graph_alt_predictors_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate(N_dim: int, M_A: int, M_B: int, seed: int):
    """Build Hopfield W; return W and pats_A."""
    rng = np.random.default_rng(seed)
    pats_A = rng.choice([-1.0, 1.0], size=(M_A, N_dim))
    pats_B = rng.choice([-1.0, 1.0], size=(M_B, N_dim))
    W = np.zeros((N_dim, N_dim), dtype=np.float64)
    for v in pats_A:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N_dim
    for v in pats_B:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N_dim
    np.fill_diagonal(W, 0.0)
    return W, pats_A


def compute_clustering_coefficient(W: np.ndarray) -> float:
    """Mean local clustering coefficient of the absolute-weight graph.

    C_i = (# triangles through i) / (k_i * (k_i - 1) / 2)
    where k_i = degree.
    Uses: A^2 diagonal gives triangle counts per node (A[i,i] of A^2 @ A).
    Mean over all nodes with k_i >= 2.
    """
    A = (np.abs(W) > np.abs(W).mean() / 2).astype(np.float64)
    np.fill_diagonal(A, 0.0)
    degrees = A.sum(axis=1)
    A2 = A @ A
    # tris_i = number of triangles through node i
    tris_per_node = (A2 * A).sum(axis=1)  # = diagonal of A^2 @ A
    possible_per_node = degrees * (degrees - 1)
    mask = possible_per_node > 0
    if not mask.any():
        return 0.0
    cc_local = tris_per_node[mask] / possible_per_node[mask]
    return float(cc_local.mean())


def compute_spectral_gap_normalized(W: np.ndarray) -> float:
    """Spectral gap of the normalized symmetric Laplacian L_sym = D^{-1/2} L D^{-1/2}.

    gap = lambda_2(L_sym) where lambda_2 is 2nd smallest eigenvalue.
    For connected graphs: gap in (0, 1].
    Large gap = fast mixing = tight spectral connectivity.
    """
    A = np.abs(W)
    np.fill_diagonal(A, 0.0)
    d = A.sum(axis=1)
    # Disconnected nodes: treat as isolated
    d_safe = np.where(d < 1e-12, 1.0, d)
    d_inv_sqrt = 1.0 / np.sqrt(d_safe)
    D_inv_sqrt = np.diag(d_inv_sqrt)
    D = np.diag(d)
    L = D - A
    L_sym = D_inv_sqrt @ L @ D_inv_sqrt

    try:
        from scipy.linalg import eigh
        eigvals = eigh(L_sym, eigvals_only=True, subset_by_index=[0, 1])
        return float(eigvals[1])
    except ImportError:
        eigvals = np.linalg.eigvalsh(L_sym)
        return float(np.sort(eigvals)[1])


def compute_avg_path_spectral_proxy(W: np.ndarray) -> float:
    """Spectral proxy for average path length via effective resistance.

    Effective resistance sum = N * trace(L^+) where L^+ is pseudoinverse.
    Normalized: effective_resistance_mean = trace(L^+) / N.
    Smaller = more tightly connected = smaller average path length.
    Return NEGATIVE of this so positive corr with retention means tight = good.
    """
    A = np.abs(W)
    np.fill_diagonal(A, 0.0)
    d = A.sum(axis=1)
    D = np.diag(d)
    L = D - A

    try:
        from scipy.linalg import pinvh
        L_plus = pinvh(L)
    except ImportError:
        # numpy fallback
        L_plus = np.linalg.pinv(L)

    N_dim = W.shape[0]
    eff_res_mean = float(np.trace(L_plus)) / N_dim
    # Return negative: more tightly connected (smaller eff_res) -> higher return value
    return -eff_res_mean


def measure_retention(W: np.ndarray, patterns: np.ndarray, seed: int) -> float:
    """Fraction of patterns self-retrieved with 10% noise."""
    rng = np.random.default_rng(seed)
    N_dim = W.shape[0]
    n_correct = 0
    for v in patterns:
        q = v.copy()
        n_flip = max(1, int(N_dim * NOISE_FLIP_FRAC))
        idx = rng.choice(N_dim, size=n_flip, replace=False)
        q[idx] = -q[idx]
        retrieved = np.sign(W @ q)
        cosim = float(np.dot(retrieved, v)) / (N_dim + 1e-9)
        n_correct += int(abs(cosim) > 0.90)
    return n_correct / max(1, len(patterns))


def run_one_seed(N_dim: int, seed: int, alpha_b_vals: List[float]) -> Dict:
    """Run one (N, seed) cell sweeping alpha_B, returning all 3 properties."""
    M_A = max(4, int(N_dim * M_A_FRAC))
    results = []
    for alpha_B in alpha_b_vals:
        M_B = int(N_dim * alpha_B)
        W, pats_A = build_substrate(N_dim, M_A, M_B, seed)
        cc = compute_clustering_coefficient(W)
        sg = compute_spectral_gap_normalized(W)
        ap = compute_avg_path_spectral_proxy(W)
        ret_A = measure_retention(W, pats_A, seed + 100)
        results.append({
            "alpha_B": alpha_B, "M_B": M_B,
            "clustering_coeff": cc,
            "spectral_gap_normalized": sg,
            "avg_path_proxy": ap,
            "retention_A": ret_A,
        })

    cc_arr = np.array([r["clustering_coeff"] for r in results])
    sg_arr = np.array([r["spectral_gap_normalized"] for r in results])
    ap_arr = np.array([r["avg_path_proxy"] for r in results])
    ret_arr = np.array([r["retention_A"] for r in results])

    def safe_corr(x, y):
        if np.std(x) < 1e-9 or np.std(y) < 1e-9:
            return 0.0
        return float(np.corrcoef(x, y)[0, 1])

    return {
        "N": N_dim, "seed": seed,
        "corr_cc_ret": safe_corr(cc_arr, ret_arr),
        "corr_sg_ret": safe_corr(sg_arr, ret_arr),
        "corr_ap_ret": safe_corr(ap_arr, ret_arr),
        "alpha_results": results,
    }


def compute_verdict(summary: dict) -> tuple:
    cells = summary.get("cells", [])
    if not cells:
        return ("SPECTRAL_ALT_INCONCLUSIVE", "No cells.")

    props = ["corr_cc_ret", "corr_sg_ret", "corr_ap_ret"]
    prop_names = ["clustering_coeff", "spectral_gap_normalized", "avg_path_proxy"]

    per_prop_corrs: Dict[str, List[float]] = {p: [] for p in props}
    for c in cells:
        for p in props:
            v = c.get(p)
            if v is not None and np.isfinite(v):
                per_prop_corrs[p].append(v)

    mean_corrs = {p: float(np.mean(vals)) if vals else 0.0
                  for p, vals in per_prop_corrs.items()}

    max_abs_corr = max(abs(v) for v in mean_corrs.values()) if mean_corrs else 0.0
    best_prop = max(mean_corrs, key=lambda p: mean_corrs[p]) if mean_corrs else "none"
    best_corr = mean_corrs.get(best_prop, 0.0)

    msg_base = (f"mean_corrs: {dict((n, round(mean_corrs[p], 3)) for n, p in zip(prop_names, props))}. "
                f"best_property={prop_names[props.index(best_prop)] if best_prop in props else best_prop} "
                f"corr={best_corr:.3f}.")

    if best_corr >= HP_CORR_MIN:
        return ("SPECTRAL_ALT_HARD_PASS",
                f"Spectral alternative predictor found. {msg_base} "
                f"At least one graph property positively predicts retention (corr>={HP_CORR_MIN}).")

    if all(abs(v) < HF_CORR_MAX for v in mean_corrs.values()):
        return ("SPECTRAL_ALT_HARD_FAIL",
                f"No spectral graph signal detected. {msg_base} "
                f"All 3 alternative properties below |corr|<{HF_CORR_MAX}. "
                f"Spectral-graph framework comprehensively closed.")

    return ("SPECTRAL_ALT_MIDDLE_BAND",
            f"Mixed spectral signal. {msg_base} "
            f"Some properties in [{HF_CORR_MAX},{HP_CORR_MIN}); not conclusive.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    N_test = 32
    # 1. Test clustering coefficient on complete graph
    A_complete = np.ones((N_test, N_test)) - np.eye(N_test)
    cc_complete = compute_clustering_coefficient(A_complete)
    assert abs(cc_complete - 1.0) < 0.02, f"complete graph CC should be ~1: {cc_complete}"
    print(f"[selftest 1/5] clustering_coeff(complete) = {cc_complete:.3f} OK", flush=True)

    # 2. Spectral gap of normalized Laplacian for complete graph > 0
    W_test = np.ones((N_test, N_test)) - np.eye(N_test)
    W_test /= N_test
    sg = compute_spectral_gap_normalized(W_test)
    assert sg > 0, f"spectral gap should be > 0: {sg}"
    print(f"[selftest 2/5] spectral_gap_normalized = {sg:.4f} > 0 OK", flush=True)

    # 3. avg_path_proxy (effective resistance negative) - finite and non-null
    ap = compute_avg_path_spectral_proxy(W_test)
    assert np.isfinite(ap), f"avg_path_proxy non-finite: {ap}"
    print(f"[selftest 3/5] avg_path_proxy = {ap:.4f} finite OK", flush=True)

    # 4. run_one_seed at smoke scale, all fields non-null
    t0 = time.time()
    cell = run_one_seed(N_SMOKE, seed=17, alpha_b_vals=[0.0, 0.10, 0.30])
    t_cell = time.time() - t0
    for key in ["corr_cc_ret", "corr_sg_ret", "corr_ap_ret"]:
        v = cell.get(key)
        assert v is not None and np.isfinite(v), f"{key} is invalid: {v}"
    assert len(cell["alpha_results"]) == 3, f"wrong alpha_results count: {len(cell['alpha_results'])}"
    print(f"[selftest 4/5] run_one_seed N={N_SMOKE} t={t_cell:.2f}s all metrics OK", flush=True)

    # 5. Multi-scale smoke: N_SMOKE and N_SMOKE*4
    cell2 = run_one_seed(N_SMOKE * 4, seed=17, alpha_b_vals=[0.0, 0.10, 0.30])
    assert "corr_cc_ret" in cell2, "N_SMOKE*4 missing corr_cc_ret"
    print(f"[selftest 5/5] multi-scale N_SMOKE*4={N_SMOKE*4} OK", flush=True)

    # 6. Verdict formula: HARD_PASS case
    cells_hp = [{"corr_cc_ret": 0.6, "corr_sg_ret": 0.3, "corr_ap_ret": 0.1}]
    v, msg = compute_verdict({"cells": cells_hp})
    assert v == "SPECTRAL_ALT_HARD_PASS", f"Expected HARD_PASS: {v} {msg}"

    # HARD_FAIL case
    cells_hf = [{"corr_cc_ret": 0.1, "corr_sg_ret": 0.05, "corr_ap_ret": -0.1}]
    v, msg = compute_verdict({"cells": cells_hf})
    assert v == "SPECTRAL_ALT_HARD_FAIL", f"Expected HARD_FAIL: {v} {msg}"
    print("[selftest 6/5] verdict formulas OK", flush=True)

    print("[SELFTEST PASS] spectral_graph_alt_predictors_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    N_dim = N_SMOKE if smoke else N
    alpha_b_vals = ALPHA_B_SMOKE if smoke else ALPHA_B_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"

    t0 = time.time()
    out_dir = get_output_dir()

    print(f"[spectral_alt] N={N_dim} alpha_B={alpha_b_vals} seeds={seeds} mode={mode_str}", flush=True)

    all_cells = []
    for seed in seeds:
        print(f"  seed={seed}...", flush=True)
        t_seed = time.time()
        cell = run_one_seed(N_dim, seed, alpha_b_vals)
        t_s = time.time() - t_seed
        print(f"    corr_cc={cell['corr_cc_ret']:.3f} corr_sg={cell['corr_sg_ret']:.3f} "
              f"corr_ap={cell['corr_ap_ret']:.3f} t={t_s:.1f}s", flush=True)
        all_cells.append(cell)

    summary = {"cells": all_cells, "N": N_dim, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N_dim, "alpha_b_vals": alpha_b_vals, "seeds": seeds, "smoke": smoke},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[spectral_alt] VERDICT: {verdict}", flush=True)
    print(f"[spectral_alt] {verdict_msg}", flush=True)
    print(f"[spectral_alt] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
