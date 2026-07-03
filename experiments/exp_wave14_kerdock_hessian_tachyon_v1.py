"""Tachyon-mode probe: negative eigenvalues / zero modes of Kerdock Hessian.

Motivation
----------
The Kerdock-Hebbian weight matrix W = (1/N) sum_mu xi_mu xi_mu^T (PSD by
construction; xi_mu in {-1,+1}^N from Kerdock codebook). For analysing the
substrate's *stored-pattern Hessian* H = -d^2 E/dx^2 of the energy landscape
E(x) = -(1/2) x^T W x, the relevant operator is - W (negative Hessian = -W).

A *tachyon* (negative eigenvalue of H = -W, equivalently *positive* eigenvalue
of W with magnitude > some reference) reflects an unstable mode. Conversely,
*zero modes* of W (eigenvalues at lambda = 0) correspond to flat directions
in the energy landscape — degenerate retrieval directions / null directions
that any input is mapped to zero by W.

For an MP(c) ensemble with c = M/N < 1, the spectrum lives on
[(1-sqrt(c))^2, (1+sqrt(c))^2] strictly inside (0, 4]; there should be NO
zero modes in expectation (smallest eigenvalue lower-bounded away from 0).

For c >= 1, there are M-N zero eigenvalues by rank deficiency. The question
becomes: how MANY zero modes does the Kerdock Hessian have, and does it
exceed the rank-deficiency baseline (M - N for c >= 1, or 0 for c < 1)?

EXCESS zero modes = substrate-novel degeneracy = additional algebraic
constraints from Kerdock structure beyond generic rank.

Scientific question
-------------------
For each alpha = M/N in {0.5, 1.0, 2.0}, what fraction of empirical
eigenvalues of W = (1/N) A^T A fall below epsilon = 1e-6 vs the MP-baseline
expectation?

Vertex:
  KERDOCK_HAS_EXCESS_ZERO_MODES : (n_near_zero / N) - max(0, 1 - 1/alpha) > 0.05
    (excess >5% of N beyond rank-deficiency floor; substrate-novel kernel structure)
  KERDOCK_NO_EXCESS_ZERO_MODES : excess < 0.01 across all cells
  KERDOCK_TACHYON_INCONCLUSIVE : mixed

Pre-reg: preregs/2026-05-23_wave14_kerdock_hessian_tachyon_v1.md

Pure CPU, <60s target (N=1024, 3 alphas, 3 seeds).
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


def get_kerdock_W_spectrum(N: int, M: int, seed: int) -> np.ndarray:
    """Return N eigenvalues of W = (1/N) A^T A (N x N PSD)."""
    if not _TORCH_OK:
        raise RuntimeError("torch required")
    import torch
    cb, _info = make_kerdock_4coset_codebook(N, torch.device("cpu"))
    rng = np.random.default_rng(seed)
    idx = rng.choice(cb.shape[0], size=M, replace=False)
    A = cb[idx].float().numpy()
    W = (A.T @ A) / float(N)  # (N, N)
    eigs = np.linalg.eigvalsh(W)
    return eigs  # ascending


def rank_deficiency_floor(alpha: float) -> float:
    """Expected fraction of zero eigenvalues from rank deficiency: max(0, 1 - 1/alpha) for alpha>=1, else 0."""
    if alpha >= 1.0:
        return max(0.0, 1.0 - 1.0 / alpha)
    return 0.0


def compute_verdict(summary: dict) -> tuple[str, str]:
    if not summary.get("cells"):
        return ("KERDOCK_TACHYON_INCONCLUSIVE", "No cells.")

    EXCESS_THRESHOLD = 0.05
    NO_EXCESS_THRESHOLD = 0.01

    excess_cells = 0
    no_excess_cells = 0
    n_cells = len(summary["cells"])
    max_excess = 0.0
    max_excess_loc = ""

    for cell in summary["cells"]:
        alpha = cell["alpha"]
        emp_zero_frac = cell["zero_frac_mean"]
        rd_floor = rank_deficiency_floor(alpha)
        excess = emp_zero_frac - rd_floor
        cell["excess_zero_frac"] = excess
        cell["rank_def_floor"] = rd_floor

        if excess > max_excess:
            max_excess = excess
            max_excess_loc = f"alpha={alpha:.2f}"

        if excess > EXCESS_THRESHOLD:
            excess_cells += 1
        elif excess < NO_EXCESS_THRESHOLD:
            no_excess_cells += 1

    if excess_cells >= max(1, n_cells // 2):
        return (
            "KERDOCK_HAS_EXCESS_ZERO_MODES",
            f"Kerdock Hessian has EXCESS zero modes (beyond rank-deficiency floor) "
            f"in {excess_cells}/{n_cells} cells; max_excess={max_excess:.3f} at "
            f"{max_excess_loc}. This is a degenerate flat-direction signature from "
            f"the algebraic structure of the Kerdock 4-coset codebook — substrate-"
            f"novel kernel dimension beyond generic random-matrix rank-deficiency.",
        )

    if no_excess_cells == n_cells:
        return (
            "KERDOCK_NO_EXCESS_ZERO_MODES",
            f"All {n_cells} cells have empirical zero-eigenvalue fraction matching "
            f"the rank-deficiency floor to within 1%. Max_excess={max_excess:.3f}. "
            f"The Kerdock Hessian has no extra algebraic-degeneracy modes beyond "
            f"the generic rank-deficiency expected of a random M x N matrix.",
        )

    return (
        "KERDOCK_TACHYON_INCONCLUSIVE",
        f"Mixed: {excess_cells} excess, {no_excess_cells} no-excess, out of {n_cells}. "
        f"Max_excess={max_excess:.3f}.",
    )


def self_test() -> None:
    # Test 1: rank_deficiency_floor
    assert rank_deficiency_floor(0.5) == 0.0
    assert rank_deficiency_floor(1.0) == 0.0
    assert abs(rank_deficiency_floor(2.0) - 0.5) < 1e-9
    assert abs(rank_deficiency_floor(4.0) - 0.75) < 1e-9

    # Test 2: verdict NO_EXCESS
    summary = {"cells": [
        {"alpha": 0.5, "zero_frac_mean": 0.0},
        {"alpha": 2.0, "zero_frac_mean": 0.5},  # exactly rank-deficiency floor
    ]}
    v, _ = compute_verdict(summary)
    assert v == "KERDOCK_NO_EXCESS_ZERO_MODES", f"expected NO_EXCESS got {v}"

    # Test 3: verdict EXCESS
    summary = {"cells": [
        {"alpha": 0.5, "zero_frac_mean": 0.10},  # 10% excess
        {"alpha": 1.0, "zero_frac_mean": 0.15},  # 15% excess (floor=0)
    ]}
    v, _ = compute_verdict(summary)
    assert v == "KERDOCK_HAS_EXCESS_ZERO_MODES", f"expected EXCESS got {v}"

    # Test 4: empty
    v, _ = compute_verdict({"cells": []})
    assert v == "KERDOCK_TACHYON_INCONCLUSIVE"

    print("self_test passed (4/4)", flush=True)


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    if smoke:
        config = {"mode": "smoke", "N": 1024, "alphas": [1.0], "n_seeds": 1, "eps": 1e-6}
    else:
        config = {"mode": "full", "N": 1024, "alphas": [0.5, 1.0, 2.0], "n_seeds": 3, "eps": 1e-6}

    N = config["N"]
    eps = config["eps"]
    cells = []
    for alpha in config["alphas"]:
        M = max(1, int(alpha * N))
        if M > 4 * N:
            continue
        per_seed_zero_frac = []
        per_seed_min_eig = []
        per_seed_max_eig = []
        for seed in range(config["n_seeds"]):
            sv = seed * 1000 + int(alpha * 100)
            eigs = get_kerdock_W_spectrum(N, M, sv)
            zero_count = int(np.sum(eigs < eps))
            zero_frac = zero_count / float(N)
            per_seed_zero_frac.append(zero_frac)
            per_seed_min_eig.append(float(eigs.min()))
            per_seed_max_eig.append(float(eigs.max()))
            print(f"[alpha={alpha:.2f} seed={sv}] zero_frac={zero_frac:.4f} "
                  f"({zero_count}/{N}) min_eig={eigs.min():.2e} "
                  f"max_eig={eigs.max():.4f}", flush=True)

        cells.append({
            "alpha": alpha, "N": N, "M": M,
            "zero_frac_mean": float(np.mean(per_seed_zero_frac)),
            "zero_frac_std": float(np.std(per_seed_zero_frac)),
            "min_eig_mean": float(np.mean(per_seed_min_eig)),
            "max_eig_mean": float(np.mean(per_seed_max_eig)),
            "per_seed_zero_frac": per_seed_zero_frac,
        })

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

    default_name = "wave14_kerdock_hessian_tachyon_v1_smoke" if args.smoke else "wave14_kerdock_hessian_tachyon_v1"
    out_dir = get_output_dir(default_name)
    write_metrics(out_dir, summary, verdict, verdict_msg, elapsed, config)


if __name__ == "__main__":
    main()
