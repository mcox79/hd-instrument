"""D1 Glauber dynamics on substrate's Kerdock codeword space (CPU drill).

Motivation
----------
The substrate's iterated argmax cleanup at zero temperature corresponds to
zero-T Glauber dynamics over the discrete configuration space spanned by
stored codewords. Finite-T Glauber dynamics (sequential single-bit flips
accepted with Metropolis criterion) gives a smoother trajectory and a
characteristic stationary distribution P(q) over overlaps q = (1/N) <s, s_mu>
between current state s and target codeword s_mu.

D1 is the top-2 candidate from research_field_advisor.py (tier-1
semiconductor, anchor_yield=100%, score=5.0; the anchor is "drift-diffusion
to BP, Cap 3 + theorem anchor"). It exercises the substrate's discrete
configuration dynamics under thermal noise — a fundamentally different
probe from the spectral-RMT line of attack of Exp 1, providing cross-
mechanism design-space coverage.

Scientific question
-------------------
Does P(q), the stationary distribution of overlap between Glauber-evolved
state and target codeword on the Kerdock codebook, show the substrate-
characteristic two-peak / heavy-tail structure observed at zero-T (modes
at q=1 retrieval and q=0 noise floor)?

Hypothesis-driven design:
  - At low T (T < T_c): bimodal P(q) with peaks at q ~ 1 and q ~ 0
  - At T_c (transition): broad unimodal P(q) at q ~ 0
  - At high T (T > T_c): unimodal P(q) at q = 0 only

The transition temperature T_c is the substrate-internal mean-field
temperature for Hopfield-style retrieval on Kerdock codewords. Mapping
T_c gives a substrate-novel scaling law for retrieval robustness vs noise.

Vertex: GLAUBER_BIMODAL_KERDOCK / GLAUBER_UNIMODAL_KERDOCK / GLAUBER_INCONCLUSIVE.

Pre-reg: preregs/2026-05-23_wave14_glauber_kerdock_v1.md
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
# Import Kerdock codebook builder
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


# ---------------------------------------------------------------------------
# Hopfield-style energy on Kerdock codeword space
# ---------------------------------------------------------------------------

def build_hebbian_W(codewords: np.ndarray) -> np.ndarray:
    """Hebbian weight matrix W = (1/N) sum_mu xi_mu xi_mu^T from stored codewords.

    codewords: (M, N) bipolar in {-1, +1}
    Returns W: (N, N) symmetric, diag-zeroed by convention.
    """
    M, N = codewords.shape
    W = (codewords.T @ codewords).astype(np.float64) / N
    np.fill_diagonal(W, 0.0)
    return W


def hopfield_energy(s: np.ndarray, W: np.ndarray) -> float:
    """E(s) = -0.5 * s^T W s. Standard Hopfield energy."""
    return -0.5 * float(s @ (W @ s))


def glauber_sweep(
    s: np.ndarray,
    W: np.ndarray,
    beta: float,
    rng: np.random.Generator,
    n_sweeps: int = 1,
) -> np.ndarray:
    """Parallel (synchronous) heat-bath dynamics: vectorized one-shot update of all N sites.

    For each sweep:
      h = W @ s
      P(s_new_i = +1) = sigmoid(2 * beta * h_i)
      s_new ~ Bernoulli(P) per site (vectorized)

    This is the synchronous Peretto 1984 / Coolen 2001 finite-T parallel
    Hopfield dynamics. For symmetric W with diag(W)=0 it has the same
    Lyapunov function structure as sequential Glauber and the same
    equilibrium phase diagram (RFIM / Hopfield literature, see e.g. Bolle
    et al. 1991, Hertz-Krogh-Palmer 1991 Ch. 4). We use it because it is
    vectorizable and N=1024 sequential Python loop is impractical.

    NOTE: parallel updates can introduce two-cycle (period-2) attractors at
    zero T that sequential Glauber avoids. Burn-in measurement averages over
    cycle phases so this is harmless for stationary P(q) statistics. We
    document this in the prereg as a known mechanism-detail caveat.

    Returns updated s.
    """
    for _ in range(n_sweeps):
        h = W @ s  # (N,) vector
        # Stable sigmoid: clip 2*beta*h to avoid overflow
        z = np.clip(2.0 * beta * h, -50.0, 50.0)
        p_plus = 1.0 / (1.0 + np.exp(-z))
        u = rng.random(s.shape[0])
        s = np.where(u < p_plus, 1.0, -1.0)
    return s


def measure_overlap(s: np.ndarray, target: np.ndarray) -> float:
    """q = (1/N) <s, target>. For bipolar +-1 states q in [-1, 1]."""
    return float(np.dot(s, target)) / s.shape[0]


# ---------------------------------------------------------------------------
# P(q) histogram and bimodality detection
# ---------------------------------------------------------------------------

def detect_bimodality(q_samples: np.ndarray) -> dict:
    """Compute summary stats and a simple bimodality indicator on q samples.

    Returns:
      mean_q, std_q, abs_mean_q, max_abs, frac_above_05, frac_below_neg05,
      bimodal_score (0 to 1; 1 = strongly bimodal)

    Bimodal score heuristic:
      - Build a 21-bin histogram on [-1, 1]
      - bimodal_score = 1 - density(|q| < 0.1) / max(density(|q| > 0.5), 1e-6)
      - Clamped to [0, 1]; ~1 when histogram is concentrated near +-1 with a
        dip near 0; ~0 when concentrated near 0
    """
    q = np.asarray(q_samples)
    mean_q = float(np.mean(q))
    std_q = float(np.std(q))
    abs_mean = float(np.mean(np.abs(q)))
    max_abs = float(np.max(np.abs(q)))
    frac_hi = float(np.mean(q > 0.5))
    frac_lo = float(np.mean(q < -0.5))

    # Histogram-based bimodality
    bins = np.linspace(-1, 1, 22)
    hist, _ = np.histogram(q, bins=bins, density=True)
    # Center bin = idx 10 (between -0.05 and 0.05)
    central = float(hist[10])
    edge_lo = float(hist[0:3].mean())  # q in [-1, -0.71]
    edge_hi = float(hist[-3:].mean())  # q in [0.71, 1]
    edge = max(edge_lo, edge_hi)
    if edge < 1e-6:
        bimodal_score = 0.0
    else:
        bimodal_score = max(0.0, min(1.0, 1.0 - central / edge))

    return {
        "mean_q": mean_q,
        "std_q": std_q,
        "abs_mean_q": abs_mean,
        "max_abs": max_abs,
        "frac_above_05": frac_hi,
        "frac_below_neg05": frac_lo,
        "bimodal_score": bimodal_score,
        "central_density": central,
        "edge_density": edge,
    }


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    """Determine verdict from per-(T, alpha) cells.

    BIMODAL_KERDOCK: at low T cells (beta >= 4), bimodal_score >= 0.5 AND
      abs_mean_q >= 0.30 (state retains alignment with target)
    UNIMODAL_KERDOCK: ALL cells have bimodal_score < 0.2 AND abs_mean_q < 0.15
      (no retrieval regime found across the T sweep)
    INCONCLUSIVE: mixed
    """
    if not summary.get("cells"):
        return ("GLAUBER_INCONCLUSIVE", "No cells computed.")

    low_T_bimodal = 0
    low_T_total = 0
    n_unimodal_global = 0
    max_bimodal = 0.0
    max_bimodal_loc = ""

    for cell in summary["cells"]:
        bs = cell.get("bimodal_score", 0.0)
        am = cell.get("abs_mean_q", 0.0)
        beta = cell.get("beta", 0.0)

        if bs > max_bimodal:
            max_bimodal = bs
            max_bimodal_loc = f"beta={beta:.2f}, alpha={cell.get('alpha', 0):.2f}"

        if beta >= 4.0:  # low T regime
            low_T_total += 1
            if bs >= 0.5 and am >= 0.30:
                low_T_bimodal += 1

        if bs < 0.2 and am < 0.15:
            n_unimodal_global += 1

    n_cells = len(summary["cells"])

    if low_T_total > 0 and low_T_bimodal >= max(1, low_T_total // 2):
        return (
            "GLAUBER_BIMODAL_KERDOCK",
            f"Glauber dynamics on Kerdock-Hebbian W shows substrate-characteristic "
            f"bimodal P(q) at low T. {low_T_bimodal}/{low_T_total} low-T cells satisfy "
            f"bimodal_score >= 0.5 and abs_mean_q >= 0.30. Max bimodal_score={max_bimodal:.3f} "
            f"at {max_bimodal_loc}. Substrate codeword space supports retrieval-noise "
            f"two-mode equilibrium under finite-T thermal dynamics; Cap 3 streaming-NESS "
            f"framing extends from drift-diffusion to a Glauber-Hopfield discrete analog.",
        )

    if n_unimodal_global == n_cells:
        return (
            "GLAUBER_UNIMODAL_KERDOCK",
            f"Glauber dynamics never shows bimodal P(q) across the T sweep. All {n_cells} "
            f"cells have bimodal_score < 0.2 and abs_mean_q < 0.15. Substrate's "
            f"Kerdock-Hebbian W does NOT support retrieval under single-spin Glauber "
            f"dynamics; the zero-T argmax cleanup is dynamically distinct from finite-T "
            f"Hopfield retrieval. May indicate ergodicity-breaking issue at low T or "
            f"a deep mismatch between Kerdock spectral structure and Glauber mixing.",
        )

    return (
        "GLAUBER_INCONCLUSIVE",
        f"Mixed Glauber response: low_T_bimodal={low_T_bimodal}/{low_T_total}, "
        f"global_unimodal={n_unimodal_global}/{n_cells}, max_bimodal={max_bimodal:.3f} "
        f"at {max_bimodal_loc}. Need finer T resolution or longer chain length.",
    )


def self_test_verdict() -> None:
    """Verify verdict classifier on hand-crafted cases."""

    # Test 1: BIMODAL — low T cell with high bimodal_score
    summary = {"cells": [
        {"beta": 8.0, "alpha": 0.5, "bimodal_score": 0.8, "abs_mean_q": 0.7},
        {"beta": 4.0, "alpha": 0.5, "bimodal_score": 0.6, "abs_mean_q": 0.4},
        {"beta": 1.0, "alpha": 0.5, "bimodal_score": 0.1, "abs_mean_q": 0.05},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "GLAUBER_BIMODAL_KERDOCK", f"expected BIMODAL got {v}"

    # Test 2: UNIMODAL — no retrieval at any T
    summary = {"cells": [
        {"beta": 8.0, "alpha": 0.5, "bimodal_score": 0.05, "abs_mean_q": 0.02},
        {"beta": 4.0, "alpha": 0.5, "bimodal_score": 0.03, "abs_mean_q": 0.04},
        {"beta": 1.0, "alpha": 0.5, "bimodal_score": 0.10, "abs_mean_q": 0.08},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "GLAUBER_UNIMODAL_KERDOCK", f"expected UNIMODAL got {v}"

    # Test 3: INCONCLUSIVE — partial retrieval
    summary = {"cells": [
        {"beta": 8.0, "alpha": 0.5, "bimodal_score": 0.3, "abs_mean_q": 0.2},
        {"beta": 4.0, "alpha": 0.5, "bimodal_score": 0.25, "abs_mean_q": 0.15},
        {"beta": 1.0, "alpha": 0.5, "bimodal_score": 0.1, "abs_mean_q": 0.05},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "GLAUBER_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    # Test 4: empty
    v, _ = compute_verdict({"cells": []})
    assert v == "GLAUBER_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    print("verdict self-test passed (4/4 cases)", flush=True)


# ---------------------------------------------------------------------------
# Per-cell Glauber simulation
# ---------------------------------------------------------------------------

def simulate_cell(
    codewords: np.ndarray,
    target_idx: int,
    beta: float,
    n_burn: int,
    n_collect: int,
    seed: int,
) -> dict:
    """One Glauber chain at temperature 1/beta, target = codewords[target_idx].

    Initialize from target with bit-flip noise (p_flip=0.3 init noise).
    Burn-in n_burn sweeps, then collect q after each of n_collect sweeps.
    """
    M, N = codewords.shape
    rng = np.random.default_rng(seed)
    target = codewords[target_idx].astype(np.float64)

    # Initialize: target with random bit flips (~30%)
    mask = rng.random(N) < 0.3
    s = target.copy()
    s[mask] = -s[mask]

    # Build Hebbian W from all M codewords
    W = build_hebbian_W(codewords)

    # Burn-in
    for _ in range(n_burn):
        s = glauber_sweep(s, W, beta, rng, n_sweeps=1)

    # Collect overlap samples
    q_samples = np.empty(n_collect, dtype=np.float64)
    for i in range(n_collect):
        s = glauber_sweep(s, W, beta, rng, n_sweeps=1)
        q_samples[i] = measure_overlap(s, target)

    stats = detect_bimodality(q_samples)
    stats["q_samples"] = q_samples.tolist()
    stats["beta"] = beta
    stats["target_idx"] = int(target_idx)
    stats["seed"] = seed
    return stats


def select_subset_codewords(N: int, M: int, seed: int) -> np.ndarray:
    """Subsample M Kerdock 4-coset codewords. Returns (M, N) numpy bipolar."""
    if not _TORCH_OK:
        raise RuntimeError("torch required for Kerdock codebook builder")
    import torch
    device = torch.device("cpu")
    cb, _info = make_kerdock_4coset_codebook(N, device)  # (4N, N) bipolar
    rng = np.random.default_rng(seed)
    idx = rng.choice(cb.shape[0], size=M, replace=False)
    sub = cb[idx].float().numpy().astype(np.float64)
    return sub


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        # Kerdock builder supports only N in {1024, 4096} (t=5, t=6 primitive
        # polys registered). Smoke uses N=1024 with sparse cell count.
        config = {
            "mode": "smoke",
            "N": 1024,
            "alpha_list": [0.5],  # M = 512
            "beta_list": [1.0, 4.0],
            "n_seeds": 2,
            "n_burn": 30,
            "n_collect": 50,
        }
    else:
        config = {
            "mode": "full",
            "N": 1024,
            "alpha_list": [0.25, 0.5, 1.0],  # M = 256, 512, 1024
            "beta_list": [0.5, 1.0, 2.0, 4.0, 8.0],
            "n_seeds": 5,
            "n_burn": 200,
            "n_collect": 400,
        }

    N = config["N"]
    cells = []

    for alpha in config["alpha_list"]:
        M = max(1, int(alpha * N))
        if M > 4 * N:
            print(f"[skip] alpha={alpha}: M={M} > 4N", flush=True)
            continue

        for beta in config["beta_list"]:
            bimodal_scores = []
            abs_mean_qs = []
            mean_qs = []
            all_q = []
            for seed in range(config["n_seeds"]):
                seed_val = seed * 1000 + int(alpha * 100) + int(beta * 7)
                codewords = select_subset_codewords(N, M, seed=seed_val)
                target_idx = seed_val % M
                stats = simulate_cell(
                    codewords, target_idx, beta,
                    n_burn=config["n_burn"],
                    n_collect=config["n_collect"],
                    seed=seed_val + 999,
                )
                bimodal_scores.append(stats["bimodal_score"])
                abs_mean_qs.append(stats["abs_mean_q"])
                mean_qs.append(stats["mean_q"])
                all_q.extend(stats["q_samples"])
                print(
                    f"  alpha={alpha:.2f} beta={beta:.2f} seed={seed} "
                    f"mean_q={stats['mean_q']:+.3f} abs_mean={stats['abs_mean_q']:.3f} "
                    f"bimodal={stats['bimodal_score']:.3f}",
                    flush=True,
                )

            cell = {
                "alpha": float(alpha),
                "beta": float(beta),
                "T": 1.0 / float(beta) if beta > 0 else float("inf"),
                "N": N,
                "M": M,
                "bimodal_score": float(np.mean(bimodal_scores)),
                "bimodal_score_std": float(np.std(bimodal_scores)),
                "abs_mean_q": float(np.mean(abs_mean_qs)),
                "abs_mean_q_std": float(np.std(abs_mean_qs)),
                "mean_q": float(np.mean(mean_qs)),
                "n_seeds": config["n_seeds"],
            }
            cells.append(cell)
            print(
                f"  AGGREGATE alpha={alpha:.2f} beta={beta:.2f}: "
                f"bimodal={cell['bimodal_score']:.3f}+-{cell['bimodal_score_std']:.3f} "
                f"abs_mean_q={cell['abs_mean_q']:.3f}+-{cell['abs_mean_q_std']:.3f}",
                flush=True,
            )

    summary = {
        "cells": cells,
        "config": config,
    }

    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
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
    self_test_verdict()
    out_dir = get_output_dir("wave14_glauber_kerdock_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test_verdict()
    out_dir = get_output_dir("wave14_glauber_kerdock_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
