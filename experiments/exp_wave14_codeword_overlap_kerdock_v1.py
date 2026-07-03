"""Empirical inner-product histogram between Kerdock codewords.

Motivation
----------
v164a/v165 established spectral/moment-based fingerprints of substrate
Kerdock non-MP-ness. A complementary, *structural* fingerprint is the
distribution of inner products <x_i, x_j>/N between distinct codewords.

For i.i.d. Rademacher columns: <x_i, x_j>/N is approximately N(0, 1/N) (CLT).
For Kerdock 4-coset codewords: theory predicts a few discrete inner-product
levels (related to the |C| values 0, +-1/sqrt(N), +-1 for nordstrom-robinson-
type 2nd-order Reed-Muller cosets), since codewords are constrained to lie on
specific algebraic surfaces.

If the empirical inner-product histogram has *discrete peaks* rather than a
smooth Gaussian, that is a structural-algebraic fingerprint independent of the
spectral fingerprint family. Substrate-novel observability.

Scientific question
-------------------
Does the histogram of <x_i, x_j>/N over n_pairs random distinct codeword
pairs (i!=j) show multi-modality (chi^2 goodness-of-fit reject vs Gaussian)?

Vertex:
  KERDOCK_OVERLAPS_NON_GAUSSIAN : KS-statistic vs Gaussian fit > 0.10
    (substrate-novel structural fingerprint)
  KERDOCK_OVERLAPS_GAUSSIAN : KS-statistic vs Gaussian < 0.05 (CLT-bulk-like)
  KERDOCK_OVERLAPS_INCONCLUSIVE : 0.05 < KS < 0.10

Pre-reg: preregs/2026-05-23_wave14_codeword_overlap_kerdock_v1.md

Pure CPU, <60s target (N=1024 or 4096, 5000-10000 pairs).
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

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

try:
    import torch
    _TORCH_OK = True
except ImportError:
    _TORCH_OK = False


def compute_overlaps(N: int, n_pairs: int, seed: int) -> np.ndarray:
    """Sample n_pairs random distinct codeword pairs and return <x_i,x_j>/N."""
    if not _TORCH_OK:
        raise RuntimeError("torch required")
    import torch
    cb, _info = make_kerdock_4coset_codebook(N, torch.device("cpu"))
    cb_np = cb.float().numpy()  # (4N, N) bipolar
    K = cb_np.shape[0]

    rng = np.random.default_rng(seed)
    idx_a = rng.integers(0, K, size=n_pairs)
    idx_b = rng.integers(0, K, size=n_pairs)
    # Resample collisions
    coll = idx_a == idx_b
    while coll.any():
        idx_b[coll] = rng.integers(0, K, size=int(coll.sum()))
        coll = idx_a == idx_b

    overlaps = np.einsum('ij,ij->i', cb_np[idx_a], cb_np[idx_b]) / float(N)
    return overlaps


def detect_multi_modality(overlaps: np.ndarray) -> dict:
    """Return histogram features + Gaussian-fit comparison."""
    mean = float(overlaps.mean())
    std = float(overlaps.std())

    # KS statistic vs Gaussian N(mean, std)
    sorted_v = np.sort(overlaps)
    n = len(sorted_v)
    # empirical CDF at each point i/n vs Gaussian CDF
    from math import erf
    def ncdf(x):
        return 0.5 * (1 + erf((x - mean) / (std * math.sqrt(2) + 1e-30)))
    emp_cdf = np.arange(1, n + 1) / n
    gauss_cdf = np.array([ncdf(v) for v in sorted_v])
    ks = float(np.max(np.abs(emp_cdf - gauss_cdf)))

    # Coarse peak detection on histogram (200 bins)
    counts, edges = np.histogram(overlaps, bins=200)
    centers = 0.5 * (edges[:-1] + edges[1:])
    # local maxima (count > both neighbours and > 5% of max)
    peak_idxs = []
    max_c = counts.max()
    for i in range(1, len(counts) - 1):
        if counts[i] > counts[i - 1] and counts[i] > counts[i + 1] and counts[i] > 0.05 * max_c:
            peak_idxs.append(i)
    peak_locs = [float(centers[i]) for i in peak_idxs]
    peak_heights = [int(counts[i]) for i in peak_idxs]

    # Are there >=2 distinct peaks whose extreme separation exceeds 3*std-of-tightest-cluster?
    # Use the range (max - min peak loc) > 3 * std as a coarse proxy.
    multi_peak = False
    if len(peak_locs) >= 2 and std > 0:
        peak_range = max(peak_locs) - min(peak_locs)
        if peak_range > 3 * std:
            multi_peak = True

    return {
        "mean": mean, "std": std, "ks_vs_gauss": ks,
        "n_peaks_detected": len(peak_locs),
        "peak_locs": peak_locs, "peak_heights": peak_heights,
        "multi_peak_3sigma": multi_peak,
        "n_pairs": n,
    }


def compute_verdict(summary: dict) -> tuple[str, str]:
    if not summary.get("cells"):
        return ("KERDOCK_OVERLAPS_INCONCLUSIVE", "No cells.")

    NON_GAUSS_THRESHOLD = 0.10
    GAUSS_THRESHOLD = 0.05

    non_gauss_cells = 0
    gauss_cells = 0
    n_cells = len(summary["cells"])

    max_ks = 0.0
    for cell in summary["cells"]:
        ks = cell["features"]["ks_vs_gauss"]
        if ks > max_ks:
            max_ks = ks
        if ks > NON_GAUSS_THRESHOLD:
            non_gauss_cells += 1
        elif ks < GAUSS_THRESHOLD:
            gauss_cells += 1

    if non_gauss_cells >= max(1, n_cells // 2):
        return (
            "KERDOCK_OVERLAPS_NON_GAUSSIAN",
            f"Kerdock codeword inner-product distribution departs from Gaussian "
            f"in {non_gauss_cells}/{n_cells} cells (KS > 0.10; max_ks={max_ks:.3f}). "
            f"Substrate-novel structural-algebraic fingerprint independent of "
            f"spectral moment family.",
        )

    if gauss_cells == n_cells:
        return (
            "KERDOCK_OVERLAPS_GAUSSIAN",
            f"All {n_cells} cells have inner-product histogram statistically "
            f"indistinguishable from Gaussian (max KS={max_ks:.3f} < 0.05). "
            f"Kerdock inner products are CLT-bulk-like; structural-algebraic "
            f"fingerprint absent at this resolution.",
        )

    return (
        "KERDOCK_OVERLAPS_INCONCLUSIVE",
        f"Mixed: {non_gauss_cells} non-gauss, {gauss_cells} gauss, out of {n_cells}. "
        f"Max_ks={max_ks:.3f}.",
    )


def self_test() -> None:
    # Test 1: Gaussian sample passes Gaussian-detection
    rng = np.random.default_rng(0)
    g = rng.normal(0, 0.03, size=5000)
    feat = detect_multi_modality(g)
    assert feat["ks_vs_gauss"] < 0.05, f"Gaussian KS too large: {feat['ks_vs_gauss']}"

    # Test 2: Bimodal mixture has high KS vs Gaussian fit
    rng = np.random.default_rng(1)
    a = rng.normal(-0.3, 0.02, size=2500)
    b = rng.normal(+0.3, 0.02, size=2500)
    mix = np.concatenate([a, b])
    feat = detect_multi_modality(mix)
    assert feat["ks_vs_gauss"] > 0.10, f"bimodal KS too low: {feat['ks_vs_gauss']}"

    # Test 3: verdict GAUSSIAN
    summary = {"cells": [{"features": {"ks_vs_gauss": 0.02}}]}
    v, _ = compute_verdict(summary)
    assert v == "KERDOCK_OVERLAPS_GAUSSIAN", f"expected GAUSSIAN got {v}"

    # Test 4: verdict NON_GAUSSIAN
    summary = {"cells": [
        {"features": {"ks_vs_gauss": 0.20}},
        {"features": {"ks_vs_gauss": 0.15}},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "KERDOCK_OVERLAPS_NON_GAUSSIAN", f"expected NON_GAUSSIAN got {v}"

    print("self_test passed (4/4)", flush=True)


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    if smoke:
        config = {"mode": "smoke", "N_list": [1024], "n_pairs": 1000, "n_seeds": 1}
    else:
        config = {"mode": "full", "N_list": [1024, 4096], "n_pairs": 5000, "n_seeds": 3}

    cells = []
    for N in config["N_list"]:
        for seed in range(config["n_seeds"]):
            sv = seed * 1000 + N
            overlaps = compute_overlaps(N, config["n_pairs"], seed=sv)
            feat = detect_multi_modality(overlaps)
            cells.append({"N": N, "seed": sv, "features": feat})
            print(f"[N={N} seed={sv}] mean={feat['mean']:+.4f} std={feat['std']:.4f} "
                  f"KS={feat['ks_vs_gauss']:.4f} n_peaks={feat['n_peaks_detected']} "
                  f"multi_peak_3sigma={feat['multi_peak_3sigma']}", flush=True)

    summary = {"cells": cells, "config": config}
    verdict, verdict_msg = compute_verdict(summary)
    summary["verdict"] = verdict
    summary["verdict_msg"] = verdict_msg
    elapsed = time.monotonic() - t0
    return summary, verdict, verdict_msg, elapsed, config


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "elapsed_s": elapsed, "summary": summary, "config": config,
    }
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    self_test()
    summary, verdict, verdict_msg, elapsed, config = run_experiment(smoke=args.smoke)
    print(f"\n=== VERDICT: {verdict} ===", flush=True)
    print(verdict_msg, flush=True)
    print(f"\nelapsed={elapsed:.1f}s", flush=True)

    default_name = "wave14_codeword_overlap_kerdock_v1_smoke" if args.smoke else "wave14_codeword_overlap_kerdock_v1"
    out_dir = get_output_dir(default_name)
    write_metrics(out_dir, summary, verdict, verdict_msg, elapsed, config)


if __name__ == "__main__":
    main()
