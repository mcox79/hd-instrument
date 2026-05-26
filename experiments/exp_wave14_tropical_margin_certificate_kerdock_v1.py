"""Tropical-polytope adversarial-margin certificate for Kerdock readout (Cap 13 candidate).

Tests whether substrate's Kerdock readout `argmax_i <w_i, y>` admits a CLOSED-FORM
L_inf adversarial margin certificate from tropical-polynomial decision boundaries
(Tropical Decision Boundaries arXiv 2402.00576; Tropical Attention NeurIPS 2025).

Closed-form claim: for y inside cell of codeword w_i,
    margin_closed(y, w_i) = min_{j != i} (<w_i - w_j, y>) / ||w_i - w_j||_1

This is the L_inf-norm tropical adversarial margin (sharp constant per arXiv 2402.00576).

Empirical claim: substrate's actual BSC adversarial threshold (minimum bit-flip
count to flip argmax) matches the closed-form margin within 5% across the
operational N grid {4, 16, 64, 256, 1024}.

Pre-reg: preregs/2026-05-24_wave14_tropical_margin_certificate_kerdock_v1.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    _TORCH_OK = True
except ImportError:
    _TORCH_OK = False

# Import 2-coset Kerdock codebook builder (works at any N=2^k, k>=2 — substrate-native
# at small N where 4-coset MM requires t>=5 i.e. N>=1024)
_v2_path = REPO / "experiments" / "exp_wave14v_erase_kerdock_v2.py"
_spec = importlib.util.spec_from_file_location("kerdock_v2", _v2_path)
_v2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v2)
make_kerdock_2coset_codebook = _v2.make_kerdock_2coset_codebook


# ---------------------------------------------------------------------------
# Core: tropical polynomial + closed-form margin
# ---------------------------------------------------------------------------

def evaluate_tropical_poly(codebook: np.ndarray, y: np.ndarray) -> tuple[float, int]:
    """Evaluate tropical polynomial p(y) = max_i <w_i, y>.

    Returns (max_value, argmax_index).
    """
    inner_products = codebook @ y  # shape (M,)
    argmax = int(np.argmax(inner_products))
    return float(inner_products[argmax]), argmax


def margin_closed_form(codebook: np.ndarray, y: np.ndarray, i: int) -> tuple[float, Optional[int]]:
    """Closed-form L_inf tropical adversarial margin at point y in cell of codeword i.

    margin = min_{j != i} (<w_i - w_j, y>) / ||w_i - w_j||_1

    Returns (margin_value, j_closest_competitor) or (margin, None) if codebook is trivial.
    """
    M, _ = codebook.shape
    if M < 2:
        return (float("inf"), None)
    w_i = codebook[i]
    diffs = w_i[None, :] - codebook  # shape (M, N), w_i - w_j
    # numerator: <w_i - w_j, y>
    numers = diffs @ y  # shape (M,)
    # denominator: ||w_i - w_j||_1
    denoms = np.sum(np.abs(diffs), axis=1)  # shape (M,)
    # Avoid self (i==i) where denom=0
    margin_vals = np.full(M, np.inf)
    mask = (np.arange(M) != i) & (denoms > 0)
    margin_vals[mask] = numers[mask] / denoms[mask]
    j_argmin = int(np.argmin(margin_vals))
    return float(margin_vals[j_argmin]), j_argmin


def empirical_bsc_margin(codebook: np.ndarray, y: np.ndarray, i: int, max_competitors: int = 64) -> tuple[float, Optional[int], int]:
    """Empirical BSC adversarial margin: min # of bit-flips in y to flip argmax from i.

    Each bit-flip in y_k toggles y_k → -y_k (assuming y in {-1, +1}-vicinity).
    L_inf perturbation per flip = 2 * |y_k|.

    Strategy: for each competitor j != i (truncated to top-max_competitors by
    margin_closed bound), compute minimum number of bit-flips to make <w_j, y'> > <w_i, y'>.

    For coordinates where w_i_k != w_j_k: flipping y_k changes <w_i - w_j, y> by:
       2 * (w_i_k - w_j_k) * (y'_k - y_k) / 2 ... actually let's just compute it.

    The gain from flipping coordinate k toward closing the gap is:
       gain_k = - 2 * y_k * (w_i_k - w_j_k)
    (positive gain reduces the gap; flip greedily by max positive gain).

    Returns (margin_emp = 2 * min_k, j_closest, n_competitors_checked).
    """
    M, N = codebook.shape
    w_i = codebook[i]
    cur_gap = float(np.dot(w_i, y) - 0)  # placeholder, will set per j below

    # Pre-rank competitors by closed-form margin to prune to top-max_competitors
    diffs = w_i[None, :] - codebook
    numers = diffs @ y
    denoms = np.sum(np.abs(diffs), axis=1)
    closed_margins = np.full(M, np.inf)
    mask = (np.arange(M) != i) & (denoms > 0)
    closed_margins[mask] = numers[mask] / denoms[mask]
    # Take top max_competitors smallest closed-form margins (most threatening j)
    sorted_idx = np.argsort(closed_margins)
    candidates = sorted_idx[:max_competitors]
    n_competitors_checked = int(np.sum(closed_margins[candidates] < np.inf))

    best_k = N + 1
    best_j: Optional[int] = None
    for j in candidates:
        if j == i:
            continue
        w_j = codebook[j]
        gap = float(np.dot(w_i, y) - np.dot(w_j, y))  # >=0 by assumption y in cell of i
        if gap < 0:
            # y was not actually in cell of i (numerical edge); skip
            continue
        # gain per coord from flipping y_k: changes <w_i - w_j, y> by:
        #    delta = (w_i_k - w_j_k) * (y'_k - y_k) = (w_i_k - w_j_k) * (-2 * y_k)
        # We want to maximize total reduction in gap, so flip coords with max
        # (-1) * delta = 2 * y_k * (w_i_k - w_j_k).  Choose those with largest
        # positive value.
        gains = 2.0 * y * (w_i - w_j)  # gain per flip (reduces gap by gains[k])
        # We can only flip a coord once; greedy = sort descending and accumulate.
        gains_sorted = np.sort(gains)[::-1]
        # We need to reduce gap to <= 0 strictly (argmax shifts to j once <w_j, y'> > <w_i, y'>).
        # That is, sum of top-k gains > gap.
        cumsum = np.cumsum(gains_sorted)
        flips_idx = np.searchsorted(cumsum, gap + 1e-12, side='right')
        # flips_idx = first index where cumsum > gap; min k = flips_idx + 1 (1-indexed) but
        # since cumsum is 0-indexed, k_min = flips_idx + 1 only if all entries <= gap before;
        # adjust: smallest k with cumsum[k-1] > gap is k = flips_idx + 1.
        k_min = int(flips_idx) + 1
        if cumsum.size == 0 or cumsum[-1] <= gap:
            # Even flipping all coords can't close gap; infinite margin to this j
            continue
        if k_min < best_k:
            best_k = k_min
            best_j = int(j)

    if best_j is None:
        # No competitor reachable; margin "infinite" (substrate is locally stable)
        return (float(N) * 2.0, None, n_competitors_checked)
    return (2.0 * float(best_k), best_j, n_competitors_checked)


def pairwise_l1_equivalence_classes(codebook: np.ndarray) -> int:
    """Count number of unique pairwise L_1 distances among all codeword pairs.

    For Kerdock-orbit (Hadamard + bent-coset structure), this collapses to a
    small set by code distance regularity (Solov'eva-Tokareva).
    """
    M = codebook.shape[0]
    # diffs[i,j] = ||w_i - w_j||_1
    # Compute via broadcasting (memory M^2 * N; for M=2048 this is 16 GB — instead loop)
    if M > 1024:
        # Sample-based estimation: sample 2000 random pairs and count unique
        rng = np.random.default_rng(0)
        n_samples = min(2000, M * (M - 1) // 2)
        unique_dists = set()
        for _ in range(n_samples):
            i, j = rng.integers(M, size=2)
            if i == j:
                continue
            d = float(np.sum(np.abs(codebook[i] - codebook[j])))
            unique_dists.add(round(d, 6))
        return len(unique_dists)
    # Full enumeration for M <= 1024
    diffs_l1 = np.zeros((M, M))
    for i in range(M):
        diffs_l1[i] = np.sum(np.abs(codebook[i:i+1] - codebook), axis=1)
    triu = diffs_l1[np.triu_indices(M, k=1)]
    return int(len(np.unique(np.round(triu, decimals=6))))


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("TROPICAL_MARGIN_INCONCLUSIVE", "No cells computed.")

    rel_errs_by_n: dict[int, list[float]] = {}
    eq_classes_by_n: dict[int, int] = {}
    for cell in cells:
        N = cell["N"]
        rel_errs_by_n.setdefault(N, [])
        for trial in cell.get("trials", []):
            cm = trial.get("margin_closed")
            em = trial.get("margin_emp")
            if cm is None or em is None or cm == float("inf") or em == float("inf"):
                continue
            denom = max(abs(cm), abs(em), 1e-12)
            rel_errs_by_n[N].append(abs(cm - em) / denom)
        eq_classes_by_n[N] = cell.get("n_equiv_classes", -1)

    # Mean rel_err per N
    mean_rel_err_by_n: dict[int, float] = {}
    for N, errs in rel_errs_by_n.items():
        if errs:
            mean_rel_err_by_n[N] = float(np.mean(errs))

    # Symmetry collapse check: ALL N should have < 300 unique classes
    any_class_overflow = any(c >= 300 for c in eq_classes_by_n.values())

    # Per-N hard fail check: any N with rel_err > 0.25
    any_hard_fail = any(e > 0.25 for e in mean_rel_err_by_n.values())

    # Count of N values with rel_err <= 0.05 (HARD PASS criterion: >=4 of 5)
    pass_count = sum(1 for e in mean_rel_err_by_n.values() if e <= 0.05)
    n_total = len(mean_rel_err_by_n)

    if any_hard_fail or any_class_overflow:
        reason = (
            f"rel_err per N: {mean_rel_err_by_n}; classes: {eq_classes_by_n}; "
            f"any_class_overflow={any_class_overflow}; any_hard_fail={any_hard_fail}."
        )
        return (
            "TROPICAL_MARGIN_KILLED",
            f"Cap 13 closed-form margin claim refuted. {reason}",
        )

    if pass_count >= 4 and n_total >= 5:
        return (
            "TROPICAL_MARGIN_CERTIFIED",
            f"Cap 13 closed-form margin certificate licensed. rel_err per N: "
            f"{mean_rel_err_by_n}; classes: {eq_classes_by_n}; "
            f"{pass_count}/{n_total} N values pass 5% threshold.",
        )

    # In-between: middle band (partial validation)
    return (
        "TROPICAL_MARGIN_PARTIAL",
        f"Closed-form margin approximately valid but not tight (5% on {pass_count}/{n_total} N). "
        f"rel_err per N: {mean_rel_err_by_n}; classes: {eq_classes_by_n}.",
    )


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def self_test() -> None:
    # 1. Tropical poly evaluation on N=2 trivial case
    cb = np.array([[1, 1], [1, -1]], dtype=float)
    y = np.array([2.0, 0.5])
    val, am = evaluate_tropical_poly(cb, y)
    assert abs(val - 2.5) < 1e-9, f"tropical val {val} != 2.5"
    assert am == 0, f"argmax {am} != 0"

    # 2. Closed-form margin on N=2 trivial case: w_i = (1,1), competitor (1,-1), y = (2, 0.5)
    # numerator <w_i - w_j, y> = <(0, 2), (2, 0.5)> = 1.0; ||w_i - w_j||_1 = 2; margin = 0.5
    margin, j = margin_closed_form(cb, y, 0)
    assert abs(margin - 0.5) < 1e-9, f"closed margin {margin} != 0.5"
    assert j == 1, f"competitor {j} != 1"

    # 3. Hadamard orthogonality at N=4
    if _TORCH_OK:
        import torch
        cb4 = make_kerdock_2coset_codebook(4, torch.device('cpu')).numpy()
        # First N=4 rows are Sylvester Hadamard; pairwise IPs should be 0 off-diagonal
        H4 = cb4[:4]
        ip4 = H4 @ H4.T / 4.0
        assert abs(ip4[0, 1]) < 1e-9, f"Hadamard rows not orthogonal: ip={ip4[0,1]}"
        assert abs(ip4[2, 3]) < 1e-9

    # 4. 2-coset codebook shape at N=4
    if _TORCH_OK:
        import torch
        cb4 = make_kerdock_2coset_codebook(4, torch.device('cpu')).numpy()
        assert cb4.shape == (8, 4), f"codebook shape {cb4.shape} != (8,4)"

    # 5. L_1 distance computation
    a = np.array([1, 1, -1, -1])
    b = np.array([1, -1, 1, -1])
    d = float(np.sum(np.abs(a - b)))
    assert abs(d - 4.0) < 1e-9, f"L_1 distance {d} != 4"

    # 6. Margin non-negativity for y in cell of w_i
    if _TORCH_OK:
        import torch
        cb16 = make_kerdock_2coset_codebook(16, torch.device('cpu')).numpy()
        rng = np.random.default_rng(42)
        for _ in range(10):
            i = int(rng.integers(cb16.shape[0]))
            y = cb16[i] + 0.1 * rng.standard_normal(16)
            # Confirm i is argmax
            ips = cb16 @ y
            actual_i = int(np.argmax(ips))
            if actual_i != i:
                continue
            margin, _ = margin_closed_form(cb16, y, i)
            assert margin >= -1e-9, f"margin {margin} negative for y in cell"

    # 7. Pairwise-distance equivalence classes at N=4 2-coset: small count
    if _TORCH_OK:
        import torch
        cb4 = make_kerdock_2coset_codebook(4, torch.device('cpu')).numpy()
        nc = pairwise_l1_equivalence_classes(cb4)
        assert nc <= 10, f"# equiv classes at N=4 = {nc} > 10"

    # 8. Verdict logic
    pass_data = {
        "cells": [
            {"N": n, "n_equiv_classes": 50,
             "trials": [{"margin_closed": 1.0, "margin_emp": 1.02}] * 5}
            for n in [4, 16, 64, 256, 1024]
        ]
    }
    v, _ = compute_verdict(pass_data)
    assert v == "TROPICAL_MARGIN_CERTIFIED", f"PASS data → {v}"

    fail_data = {
        "cells": [
            {"N": n, "n_equiv_classes": 50,
             "trials": [{"margin_closed": 1.0, "margin_emp": 1.5}] * 5}  # 33% rel err
            for n in [4, 16, 64, 256, 1024]
        ]
    }
    v, _ = compute_verdict(fail_data)
    assert v == "TROPICAL_MARGIN_KILLED", f"FAIL data → {v}"

    middle_data = {
        "cells": [
            {"N": n, "n_equiv_classes": 50,
             "trials": [{"margin_closed": 1.0, "margin_emp": 1.08}] * 5}  # 7.4% rel err
            for n in [4, 16, 64, 256, 1024]
        ]
    }
    v, _ = compute_verdict(middle_data)
    assert v == "TROPICAL_MARGIN_PARTIAL", f"MIDDLE data → {v}"

    overflow_data = {
        "cells": [
            {"N": n, "n_equiv_classes": 500 if n == 1024 else 50,
             "trials": [{"margin_closed": 1.0, "margin_emp": 1.02}] * 5}
            for n in [4, 16, 64, 256, 1024]
        ]
    }
    v, _ = compute_verdict(overflow_data)
    assert v == "TROPICAL_MARGIN_KILLED", f"overflow data → {v}"

    print(f"self-tests passed (8 cells)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    if not _TORCH_OK:
        raise RuntimeError("torch required for Kerdock codebook builder")
    import torch

    if smoke:
        config = {
            "mode": "smoke",
            "N_list": [4],
            "n_seeds": 1,
            "n_codewords_per_cell": 3,
            "eps": 0.1,
            "max_competitors": 64,
        }
    else:
        config = {
            "mode": "full",
            "N_list": [4, 16, 64, 256, 1024],
            "n_seeds": 5,
            "n_codewords_per_cell": 10,
            "eps": 0.1,
            "max_competitors": 64,
        }

    cells = []
    device = torch.device("cpu")

    for N in config["N_list"]:
        print(f"\n[N={N}] building 2-coset codebook...", flush=True)
        codebook_t = make_kerdock_2coset_codebook(N, device)
        codebook = codebook_t.numpy()  # shape (2N, N), entries in {-1, +1}
        M, _ = codebook.shape

        print(f"[N={N}] codebook shape={codebook.shape}; computing equiv classes...", flush=True)
        n_classes = pairwise_l1_equivalence_classes(codebook)
        print(f"[N={N}] # unique pairwise L_1 distances: {n_classes}", flush=True)

        trials = []
        rng = np.random.default_rng(N * 31)
        for seed in range(config["n_seeds"]):
            seed_rng = np.random.default_rng(seed * 1000 + N)
            # Sample n_codewords distinct codewords
            n_cw = min(config["n_codewords_per_cell"], M)
            cw_indices = seed_rng.choice(M, size=n_cw, replace=False)
            for i in cw_indices:
                w_i = codebook[i]
                direction = seed_rng.standard_normal(N)
                direction /= max(np.linalg.norm(direction), 1e-12)
                y = w_i + config["eps"] * direction

                # Confirm i is still argmax (numerical safety)
                ips = codebook @ y
                actual_i = int(np.argmax(ips))
                if actual_i != int(i):
                    # eps too large; skip
                    continue

                margin_c, j_c = margin_closed_form(codebook, y, int(i))
                margin_e, j_e, n_checked = empirical_bsc_margin(
                    codebook, y, int(i), max_competitors=config["max_competitors"]
                )
                trials.append({
                    "seed": int(seed),
                    "i": int(i),
                    "margin_closed": float(margin_c),
                    "margin_emp": float(margin_e),
                    "j_closed": int(j_c) if j_c is not None else -1,
                    "j_emp": int(j_e) if j_e is not None else -1,
                    "n_competitors_checked": int(n_checked),
                })

        # Aggregate
        valid_pairs = [(t["margin_closed"], t["margin_emp"]) for t in trials
                       if t["margin_closed"] != float("inf") and t["margin_emp"] != float("inf")]
        rel_errs = [abs(c - e) / max(abs(c), abs(e), 1e-12) for c, e in valid_pairs]
        cell = {
            "N": int(N),
            "n_equiv_classes": int(n_classes),
            "n_trials": len(trials),
            "n_valid_trials": len(valid_pairs),
            "mean_margin_closed": float(np.mean([c for c, _ in valid_pairs])) if valid_pairs else None,
            "mean_margin_emp": float(np.mean([e for _, e in valid_pairs])) if valid_pairs else None,
            "mean_rel_err": float(np.mean(rel_errs)) if rel_errs else None,
            "max_rel_err": float(np.max(rel_errs)) if rel_errs else None,
            "trials": trials,
        }
        cells.append(cell)
        print(f"[N={N}] mean rel_err = {cell['mean_rel_err']}, "
              f"mean margin_closed = {cell['mean_margin_closed']}, "
              f"mean margin_emp = {cell['mean_margin_emp']}", flush=True)

    summary = {"cells": cells, "config": config}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    env_name = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{env_name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not d.get("verdict"):
        raise ValueError("empty verdict")


def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_tropical_margin_certificate_kerdock_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_tropical_margin_certificate_kerdock_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
