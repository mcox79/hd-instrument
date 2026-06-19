"""Spectral support test: does Kerdock spectrum extend beyond MP bulk edges?

Motivation
----------
v164a/v165 established the substrate Kerdock spectrum has nontrivial higher
free cumulants kappa_n / S-transform deviating from MP. This is a moment-based
fingerprint. An independent, *geometric* fingerprint is the SUPPORT of the
spectrum: where does it live on the real line?

For Marchenko-Pastur(c) at c=M/N <= 1, the MP support is:
  [lambda_min, lambda_max] = [(1 - sqrt(c))^2, (1 + sqrt(c))^2]
i.e. the spectrum is bulk-bounded — no eigenvalue escapes the soft edges.

If the Kerdock spectrum has *outlier* eigenvalues outside the MP bulk, that is
a substrate-novel geometric signature complementing the moment-based ones.

Scientific question
-------------------
Does the empirical spectrum of (1/N) A^T A for the Kerdock 4-coset codebook
have eigenvalues OUTSIDE [(1-sqrt(c))^2, (1+sqrt(c))^2] by more than O(1/sqrt(N))?

Vertex:
  KERDOCK_SPECTRUM_BULK_BOUNDED : max excursion beyond MP edge < 0.05 * (edge width)
  KERDOCK_SPECTRUM_HAS_OUTLIERS : any eigenvalue exceeds (1+sqrt(c))^2 * 1.05
                                   or below (1-sqrt(c))^2 - 0.05 * edge_width
  KERDOCK_SPECTRUM_INCONCLUSIVE : mixed across seeds/alphas

Pre-reg: preregs/2026-05-23_wave14_spectral_support_kerdock_v1.md

Pure CPU, <60s wallclock target (single (N=1024, alpha=1.0) cell, 5 seeds).
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

# Reuse v3 Kerdock codebook builder (proven)
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


def get_kerdock_eigenvalues(N: int, M: int, seed: int) -> np.ndarray:
    """Return eigenvalues of (1/N) A^T A where A is M subsampled Kerdock codewords."""
    if not _TORCH_OK:
        raise RuntimeError("torch required for Kerdock codebook builder")
    import torch
    device = torch.device("cpu")
    cb, _info = make_kerdock_4coset_codebook(N, device)
    rng = np.random.default_rng(seed)
    idx = rng.choice(cb.shape[0], size=M, replace=False)
    A = cb[idx].float().numpy() / math.sqrt(N)
    _, s, _ = np.linalg.svd(A, full_matrices=False)
    return s ** 2


def mp_edges(c: float) -> tuple[float, float]:
    """MP support [lambda_min, lambda_max] for c = M/N."""
    sqrt_c = math.sqrt(c)
    return ((1.0 - sqrt_c) ** 2, (1.0 + sqrt_c) ** 2)


def compute_verdict(summary: dict) -> tuple[str, str]:
    if not summary.get("cells"):
        return ("KERDOCK_SPECTRUM_INCONCLUSIVE", "No cells computed.")

    OUTLIER_REL = 0.05  # fractional excursion beyond MP edge counts as outlier

    n_cells = len(summary["cells"])
    outlier_cells = 0
    bounded_cells = 0
    max_excursion = 0.0
    max_excursion_loc = ""

    for cell in summary["cells"]:
        c = cell["alpha"]
        lam_min_mp, lam_max_mp = mp_edges(c)
        edge_width = lam_max_mp - lam_min_mp
        upper_thresh = lam_max_mp + OUTLIER_REL * edge_width
        lower_thresh = lam_min_mp - OUTLIER_REL * edge_width

        # excursion = max(lam_max_emp - lam_max_mp, lam_min_mp - lam_min_emp) / edge_width
        excursion_upper = (cell["lam_max_mean"] - lam_max_mp) / max(edge_width, 1e-9)
        excursion_lower = (lam_min_mp - cell["lam_min_mean"]) / max(edge_width, 1e-9)
        worst_excursion = max(excursion_upper, excursion_lower)
        cell["mp_lam_min"] = lam_min_mp
        cell["mp_lam_max"] = lam_max_mp
        cell["worst_excursion_rel"] = worst_excursion

        if worst_excursion > max_excursion:
            max_excursion = worst_excursion
            max_excursion_loc = f"alpha={c:.2f}"

        if cell["lam_max_mean"] > upper_thresh or cell["lam_min_mean"] < lower_thresh:
            outlier_cells += 1
        else:
            bounded_cells += 1

    if outlier_cells >= max(1, n_cells // 2):
        return (
            "KERDOCK_SPECTRUM_HAS_OUTLIERS",
            f"Kerdock spectrum has eigenvalues OUTSIDE the MP bulk in "
            f"{outlier_cells}/{n_cells} cells. Max relative excursion="
            f"{max_excursion:.3f} at {max_excursion_loc}. This is a "
            f"geometric (support-level) fingerprint of the substrate-novel "
            f"regime, complementing the moment-based (free-cumulant / "
            f"S-transform) fingerprints. Substrate-novel observability: "
            f"spectral-support excursion distinguishes Kerdock from MP.",
        )

    if bounded_cells == n_cells:
        return (
            "KERDOCK_SPECTRUM_BULK_BOUNDED",
            f"All {n_cells} cells have spectrum CONFINED within 5% of the MP "
            f"bulk edges. Max excursion={max_excursion:.3f}. The substrate-"
            f"novel signature is therefore MOMENT-BASED ONLY: free cumulants "
            f"deviate from MP, but the support does not. The mechanism is "
            f"shape-of-bulk, not outliers.",
        )

    return (
        "KERDOCK_SPECTRUM_INCONCLUSIVE",
        f"Mixed: {outlier_cells} outlier-bearing cells, {bounded_cells} bounded "
        f"out of {n_cells}. Max excursion={max_excursion:.3f}.",
    )


def self_test() -> None:
    # Test 1: MP edge formulas
    for c, expected_max in [(0.5, (1 + math.sqrt(0.5)) ** 2),
                            (1.0, 4.0),
                            (0.25, (1.5) ** 2)]:
        _, lam_max = mp_edges(c)
        assert abs(lam_max - expected_max) < 1e-9, f"MP edge wrong for c={c}"

    # Test 2: verdict BULK_BOUNDED
    summary = {"cells": [
        {"alpha": 1.0, "lam_max_mean": 4.0, "lam_min_mean": 0.0},  # exact MP
        {"alpha": 0.5, "lam_max_mean": (1 + math.sqrt(0.5)) ** 2, "lam_min_mean": (1 - math.sqrt(0.5)) ** 2},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "KERDOCK_SPECTRUM_BULK_BOUNDED", f"expected BULK_BOUNDED got {v}"

    # Test 3: verdict HAS_OUTLIERS
    summary = {"cells": [
        {"alpha": 1.0, "lam_max_mean": 5.0, "lam_min_mean": 0.0},  # 25% above MP edge
        {"alpha": 0.5, "lam_max_mean": 4.0, "lam_min_mean": 0.0},  # above MP edge
    ]}
    v, _ = compute_verdict(summary)
    assert v == "KERDOCK_SPECTRUM_HAS_OUTLIERS", f"expected HAS_OUTLIERS got {v}"

    # Test 4: empty
    v, _ = compute_verdict({"cells": []})
    assert v == "KERDOCK_SPECTRUM_INCONCLUSIVE"

    print("self_test passed (4/4)", flush=True)


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    if smoke:
        config = {"mode": "smoke", "N": 1024, "alphas": [1.0], "n_seeds": 2}
    else:
        config = {"mode": "full", "N": 1024, "alphas": [0.5, 1.0, 2.0], "n_seeds": 5}

    N = config["N"]
    cells = []
    for alpha in config["alphas"]:
        M = max(1, int(alpha * N))
        if M > 4 * N:
            continue
        c_ref = float(alpha)
        lam_min_mp, lam_max_mp = mp_edges(c_ref)
        print(f"[alpha={alpha:.2f}] N={N} M={M} MP_edges=[{lam_min_mp:.4f},{lam_max_mp:.4f}]", flush=True)

        per_seed = []
        for seed in range(config["n_seeds"]):
            sv = seed * 1000 + int(alpha * 100)
            eigs = get_kerdock_eigenvalues(N, M, sv)
            # If c>1, there are M-N zero eigenvalues; for MP comparison use the nonzero bulk.
            if alpha > 1.0:
                eigs = eigs[eigs > 1e-9]
            lam_max_emp = float(eigs.max())
            lam_min_emp = float(eigs.min())
            per_seed.append({"seed": sv, "lam_max": lam_max_emp, "lam_min": lam_min_emp})
            print(f"  seed={sv} lam_max={lam_max_emp:.4f} lam_min={lam_min_emp:.4f}", flush=True)

        lam_max_arr = np.array([s["lam_max"] for s in per_seed])
        lam_min_arr = np.array([s["lam_min"] for s in per_seed])
        cells.append({
            "alpha": alpha, "N": N, "M": M,
            "lam_max_mean": float(lam_max_arr.mean()),
            "lam_max_std": float(lam_max_arr.std()),
            "lam_min_mean": float(lam_min_arr.mean()),
            "lam_min_std": float(lam_min_arr.std()),
            "per_seed": per_seed,
        })

    summary = {"cells": cells, "config": config}
    verdict, verdict_msg = compute_verdict(summary)
    summary["verdict"] = verdict
    summary["verdict_msg"] = verdict_msg
    elapsed = time.monotonic() - t0
    return summary, verdict, verdict_msg, elapsed, config


def get_output_dir(default_name: str) -> Path:
    env_name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{env_name}"
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

    default_name = "wave14_spectral_support_kerdock_v1_smoke" if args.smoke else "wave14_spectral_support_kerdock_v1"
    out_dir = get_output_dir(default_name)
    write_metrics(out_dir, summary, verdict, verdict_msg, elapsed, config)


if __name__ == "__main__":
    main()
