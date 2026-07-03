"""Voiculescu free cumulants kappa_n on substrate's Kerdock spectrum (F4 drill).

Motivation
----------
The AMP_SE_DIVERGES verdict (2026-05-23) established that the substrate's
4-coset Kerdock codebook falls OUTSIDE the standard AMP universality class.
The Bayati-Montanari right-rotationally-invariant scalar SE recursion failed
to predict empirical AMP MSE on the Kerdock matrix.

In Zhong-Wang-Fan arXiv:2110.02318 (orthogonally-invariant AMP, OAMP), the
Onsager-correction coefficients in the EXACT state-evolution recursion are
the FREE CUMULANTS of the noise spectrum (Voiculescu kappa_n). The scalar
SE corresponds to truncating after kappa_1 (the mean). If the Kerdock matrix
has nontrivial higher free cumulants beyond MP (Marchenko-Pastur) baseline,
that is precisely the mechanism by which it departs from AMP universality.

F4 is the top-1 candidate from research_field_advisor.py (free-probability
tier-1, anchor_yield=100%, score=5.5). It directly probes the substrate-
novel regime that AMP_SE_DIVERGES confirmed.

Scientific question
-------------------
Are the higher free cumulants kappa_n (n>=2) of the Kerdock empirical
spectrum significantly different from the Marchenko-Pastur reference at the
same M/N ratio? Specifically:
  - kappa_2 (variance of free distribution): expected = c = M/N for MP
  - kappa_3 (free-skewness): expected = c for MP; non-MP if != c
  - kappa_4 (free-kurtosis / free-cumulant excess): expected = c for MP

If higher kappa_n diverge from MP reference: this is a substrate-novel
observability metric and the formal mechanism for AMP_SE_DIVERGES.

Vertex: FREE_CUMULANTS_MATCH_MP / FREE_CUMULANTS_DIVERGE / FREE_CUMULANTS_INCONCLUSIVE.

Computation
-----------
For a probability measure mu on R with finite moments m_n = integral lambda^n dmu,
the free cumulants kappa_n are defined by the moment-cumulant relation:

  m_n = sum over non-crossing partitions pi of {1..n} of product over
        blocks B in pi of kappa_|B|

Equivalently via the R-transform:
  R(z) = sum_{n>=1} kappa_n z^{n-1}
  R(G(z)) = z - 1/G(z),  where G(z) = integral 1/(z - lambda) dmu

We compute kappa_n for n in {1..4} via the moment-cumulant inversion using
Speicher's recursion (Nica-Speicher 2006, Lectures on Combinatorics of Free
Probability):

  kappa_1 = m_1
  kappa_2 = m_2 - m_1^2
  kappa_3 = m_3 - 3 m_1 m_2 + 2 m_1^3
  kappa_4 = m_4 - 4 m_1 m_3 - 2 m_2^2 + 10 m_1^2 m_2 - 5 m_1^4

For the Marchenko-Pastur(c) distribution with c = M/N:
  kappa_n^MP = c for all n >= 1

So the substrate-novel signature is "kappa_n / c - 1" for n >= 2 (deviation
from MP baseline).

Pre-reg: preregs/2026-05-23_wave14_free_cumulants_kerdock_v1.md
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
# Import Kerdock codebook builder from v3 (proven substrate codebook)
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
# Free cumulants from empirical moments
# ---------------------------------------------------------------------------

def moments_to_free_cumulants(moments: list[float]) -> list[float]:
    """Convert spectral moments m_1..m_n to free cumulants kappa_1..kappa_n.

    Uses the moment-free-cumulant inversion via the Mobius function on the
    non-crossing partition lattice (Nica-Speicher 2006, Eq 11.4).

    Equivalently, the closed forms for n=1..4 (most-used in practice):
      kappa_1 = m_1
      kappa_2 = m_2 - m_1^2
      kappa_3 = m_3 - 3*m_1*m_2 + 2*m_1^3
      kappa_4 = m_4 - 4*m_1*m_3 - 2*m_2^2 + 10*m_1^2*m_2 - 5*m_1^4

    Verification (MP reference): MP(c) has all kappa_n = c. Setting
    m_1 = c, m_2 = c + c^2, m_3 = c + 3 c^2 + c^3, m_4 = c + 6 c^2 + 6 c^3 + c^4
    (Marchenko-Pastur moments) gives kappa_1 = c, kappa_2 = c, kappa_3 = c,
    kappa_4 = c. We assert this in self-test.
    """
    n = len(moments)
    if n < 1:
        return []

    m1 = moments[0]
    out = [m1]

    if n >= 2:
        m2 = moments[1]
        k2 = m2 - m1 * m1
        out.append(k2)

    if n >= 3:
        m3 = moments[2]
        k3 = m3 - 3.0 * m1 * m2 + 2.0 * m1 ** 3
        out.append(k3)

    if n >= 4:
        m4 = moments[3]
        k4 = m4 - 4.0 * m1 * m3 - 2.0 * m2 ** 2 + 10.0 * m1 ** 2 * m2 - 5.0 * m1 ** 4
        out.append(k4)

    return out


def mp_reference_moments(c: float, n_max: int) -> list[float]:
    """Marchenko-Pastur moments m_n = sum_{k=0..n-1} C(n,k) C(n,k+1) c^{k+1} / n.

    Equivalently the Narayana-weighted polynomial. For c <= 1, the support of
    the MP density is [(1-sqrt(c))^2, (1+sqrt(c))^2] (with point mass at 0
    if c > 1 in the inverse direction; we use c = M/N <= 1 here).

    For verification, we use the explicit formula (Bai-Silverstein 2010,
    Section 3.1.1, "Marchenko-Pastur moments"):
      m_n(c) = (1/n) sum_{k=1..n} C(n,k) C(n,k-1) c^k
    """
    moments = []
    for n in range(1, n_max + 1):
        total = 0.0
        for k in range(1, n + 1):
            # C(n,k) * C(n,k-1) * c^k / n
            term = math.comb(n, k) * math.comb(n, k - 1) * (c ** k) / n
            total += term
        moments.append(total)
    return moments


def mp_reference_cumulants(c: float, n_max: int) -> list[float]:
    """For MP(c), all free cumulants are equal to c. Returns [c, c, ..., c]."""
    return [c] * n_max


# ---------------------------------------------------------------------------
# Spectrum extraction from Kerdock codebook
# ---------------------------------------------------------------------------

def get_kerdock_spectrum(N: int, M: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Build Kerdock 4-coset codebook, subsample M rows, return:
      - eigenvalues of (1/N) * A^T A (length min(M, N))
      - normalized matrix A_norm = A / sqrt(N)
    """
    if not _TORCH_OK:
        raise RuntimeError("torch required for Kerdock codebook builder")
    import torch

    device = torch.device("cpu")
    cb, _info = make_kerdock_4coset_codebook(N, device)  # (4N, N) bipolar in {-1, +1}

    rng = np.random.default_rng(seed)
    idx = rng.choice(cb.shape[0], size=M, replace=False)
    A_t = cb[idx].float()
    A = A_t.numpy()
    A_norm = A / math.sqrt(N)

    # SVD of A_norm gives singular values s; eigenvalues of A_norm^T A_norm = s^2
    # That is (1/N) A^T A
    _, s, _ = np.linalg.svd(A_norm, full_matrices=False)
    eigenvalues = s ** 2
    return eigenvalues, A_norm


def spectral_moments(eigenvalues: np.ndarray, n_max: int) -> list[float]:
    """Empirical spectral moments m_n = (1/K) sum lambda_i^n."""
    moments = []
    for n in range(1, n_max + 1):
        moments.append(float(np.mean(eigenvalues ** n)))
    return moments


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    """Determine verdict from per-alpha cumulant deviations.

    DIVERGE = at least one alpha cell has |kappa_n / c_ref - 1| > 0.20 for some n in {2,3,4}
              (significant departure from MP baseline)
    MATCH   = all alpha cells have all |kappa_n / c_ref - 1| < 0.10 (close to MP)
    INCONCLUSIVE = mixed
    """
    if not summary.get("cells"):
        return ("FREE_CUMULANTS_INCONCLUSIVE", "No cells computed.")

    DIVERGE_THRESHOLD = 0.20
    MATCH_THRESHOLD = 0.10

    diverge_cells = 0
    match_cells = 0
    max_dev = 0.0
    max_dev_loc = ""

    for cell in summary["cells"]:
        kappas = cell.get("kappa_mean", [])
        c_ref = cell.get("alpha")  # c = M/N
        if not kappas or c_ref is None or c_ref <= 0:
            continue

        worst_dev = 0.0
        worst_n = 0
        for n_idx in range(1, len(kappas)):  # n=2,3,4 -> idx 1,2,3
            n = n_idx + 1
            dev = abs(kappas[n_idx] / c_ref - 1.0)
            if dev > worst_dev:
                worst_dev = dev
                worst_n = n
        cell["worst_kappa_dev"] = worst_dev
        cell["worst_kappa_n"] = worst_n

        if worst_dev > max_dev:
            max_dev = worst_dev
            max_dev_loc = f"alpha={c_ref:.2f}, kappa_{worst_n}"

        if worst_dev > DIVERGE_THRESHOLD:
            diverge_cells += 1
        elif worst_dev < MATCH_THRESHOLD:
            match_cells += 1

    n_cells = len(summary["cells"])
    if n_cells == 0:
        return ("FREE_CUMULANTS_INCONCLUSIVE", "No valid cells.")

    if diverge_cells >= max(1, n_cells // 2):
        return (
            "FREE_CUMULANTS_DIVERGE",
            f"Kerdock spectrum has higher free cumulants kappa_n (n>=2) that deviate "
            f"significantly from MP baseline. {diverge_cells}/{n_cells} cells exceed "
            f"20% deviation; max_dev={max_dev:.3f} at {max_dev_loc}. This is the "
            f"formal mechanism for AMP_SE_DIVERGES: nontrivial higher free cumulants "
            f"in the Kerdock R-transform place it outside the AMP universality class. "
            f"Substrate-novel observability: kappa_n profile distinguishes Kerdock "
            f"from i.i.d. Gaussian baseline.",
        )

    if match_cells == n_cells:
        return (
            "FREE_CUMULANTS_MATCH_MP",
            f"All {n_cells} cells have kappa_n within 10% of MP baseline c=M/N. "
            f"Max deviation={max_dev:.3f}. Kerdock spectrum is FREE-PROBABILISTICALLY "
            f"INDISTINGUISHABLE from MP at higher cumulants up to n=4. AMP_SE_DIVERGES "
            f"cannot be attributed to higher free cumulants; the divergence must lie in "
            f"a non-free-probabilistic mechanism (e.g., eigenvector localization).",
        )

    return (
        "FREE_CUMULANTS_INCONCLUSIVE",
        f"Mixed verdict: {diverge_cells} cells diverge (>20%), {match_cells} cells "
        f"match (<10%), out of {n_cells}. Max_dev={max_dev:.3f} at {max_dev_loc}. "
        f"Free cumulants partially detect Kerdock departure from MP; need finer "
        f"resolution or higher n.",
    )


def self_test_verdict() -> None:
    """Verify both the moment-cumulant math AND verdict classifier."""
    # Test 1: MP(c=0.5) moments should give all kappa_n = 0.5
    c_test = 0.5
    moms = mp_reference_moments(c_test, 4)
    kappas = moments_to_free_cumulants(moms)
    for i, k in enumerate(kappas):
        assert abs(k - c_test) < 1e-9, (
            f"self_test FAIL: MP({c_test}) gave kappa_{i+1}={k}, expected {c_test}"
        )

    # Test 2: c=1 case
    c_test = 1.0
    moms = mp_reference_moments(c_test, 4)
    kappas = moments_to_free_cumulants(moms)
    for i, k in enumerate(kappas):
        assert abs(k - c_test) < 1e-9, (
            f"self_test FAIL: MP({c_test}) gave kappa_{i+1}={k}, expected {c_test}"
        )

    # Test 3: c=2 case (M > N, K = N eigenvalues)
    c_test = 2.0
    moms = mp_reference_moments(c_test, 4)
    kappas = moments_to_free_cumulants(moms)
    for i, k in enumerate(kappas):
        assert abs(k - c_test) < 1e-7, (
            f"self_test FAIL: MP({c_test}) gave kappa_{i+1}={k}, expected {c_test}"
        )

    # Test 4: verdict classifier — DIVERGE
    summary = {"cells": [
        {"alpha": 0.5, "kappa_mean": [0.5, 0.5, 0.5, 1.5]},  # kappa_4 / c - 1 = 2.0 > 0.2
        {"alpha": 1.0, "kappa_mean": [1.0, 1.0, 1.0, 1.0]},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "FREE_CUMULANTS_DIVERGE", f"expected DIVERGE got {v}"

    # Test 5: MATCH
    summary = {"cells": [
        {"alpha": 0.5, "kappa_mean": [0.5, 0.51, 0.49, 0.50]},
        {"alpha": 1.0, "kappa_mean": [1.0, 1.05, 0.95, 1.02]},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "FREE_CUMULANTS_MATCH_MP", f"expected MATCH got {v}"

    # Test 6: empty
    v, _ = compute_verdict({"cells": []})
    assert v == "FREE_CUMULANTS_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    print("verdict self-test passed (6/6 cases)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "M_over_N_list": [0.5, 1.0],
            "n_seeds": 2,
            "n_max_moment": 4,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "M_over_N_list": [0.25, 0.5, 1.0, 2.0, 4.0],
            "n_seeds": 5,
            "n_max_moment": 4,
        }

    N = config["N"]
    n_max = config["n_max_moment"]

    cells = []
    for alpha in config["M_over_N_list"]:
        M = max(1, int(alpha * N))
        if M > 4 * N:
            print(f"[skip] alpha={alpha:.2f}: M={M} > 4N={4*N}, skipping", flush=True)
            continue

        # When M > N, eigenvalues of (1/N) A^T A have N nonzero values.
        # When M <= N, M nonzero values.
        # The c-parameter for MP reference is min(M, N) / max(M, N) = c_eff
        # but the "natural" c = M/N (Marchenko-Pastur in row-aspect convention)
        # Following Bai-Silverstein: c = M/N (rows over cols), MP density for
        # (1/N) A^T A has support [(1-sqrt(c))^2, (1+sqrt(c))^2] (c<=1) or
        # bulk on [(1-sqrt(c))^2, (1+sqrt(c))^2] with N-M zero eigenvalues
        # for c > 1.
        # For free cumulants we use c = M/N directly (matches the spectral
        # moments definition m_n = (1/K) sum lam^n where K = rank).
        c_ref = float(alpha)

        print(f"\n[alpha={alpha:.2f}] N={N} M={M} c_ref={c_ref:.4f}", flush=True)

        kappa_per_seed = []
        moms_per_seed = []
        for seed in range(config["n_seeds"]):
            seed_val = seed * 1000 + int(alpha * 100)
            eigenvalues, _A_norm = get_kerdock_spectrum(N, M, seed=seed_val)

            # Empirical moments and free cumulants
            moms = spectral_moments(eigenvalues, n_max)
            kappas = moments_to_free_cumulants(moms)
            kappa_per_seed.append(kappas)
            moms_per_seed.append(moms)

            print(
                f"  seed={seed} moments={[f'{m:.4f}' for m in moms]} "
                f"kappas={[f'{k:.4f}' for k in kappas]}",
                flush=True,
            )

        # Aggregate kappas across seeds
        kappa_arr = np.array(kappa_per_seed)  # (n_seeds, n_max)
        kappa_mean = kappa_arr.mean(axis=0).tolist()
        kappa_std = kappa_arr.std(axis=0).tolist()
        moms_arr = np.array(moms_per_seed)
        moms_mean = moms_arr.mean(axis=0).tolist()

        # MP reference
        kappa_mp = mp_reference_cumulants(c_ref, n_max)
        moms_mp = mp_reference_moments(c_ref, n_max)

        # Per-n deviation
        dev_per_n = [
            (kappa_mean[i] / c_ref - 1.0) if c_ref > 0 else 0.0
            for i in range(n_max)
        ]

        cell = {
            "alpha": float(alpha),
            "N": N,
            "M": M,
            "c_ref": c_ref,
            "kappa_mean": kappa_mean,
            "kappa_std": kappa_std,
            "kappa_mp": kappa_mp,
            "moments_mean": moms_mean,
            "moments_mp": moms_mp,
            "kappa_dev_relative": dev_per_n,
        }
        cells.append(cell)

        print(
            f"  AGGREGATE alpha={alpha:.2f}: kappa_mean={[f'{k:.4f}' for k in kappa_mean]} "
            f"vs MP c={c_ref:.4f}; dev_rel={[f'{d:+.3f}' for d in dev_per_n]}",
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
    out_dir = get_output_dir("wave14_free_cumulants_kerdock_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test_verdict()
    out_dir = get_output_dir("wave14_free_cumulants_kerdock_v1")
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
